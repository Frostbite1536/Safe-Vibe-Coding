---
layout: default
title: 13. Cost, Rate-Limiting & Latency Budgets
nav_order: 13
parent: Agents Guide
grand_parent: Guides
description: "Per-run token budgets, runaway-loop detection, circuit breakers, and kill switches. How to stop an agent that has lost the plot before it burns through your API quota or your user's patience."
permalink: /agents/cost-and-kill-switches
---

# 13. Cost, Rate-Limiting & Latency Budgets

Agents are the first kind of software where "ran for too long" and "spent too much money" are not just performance concerns — they are safety concerns. A traditional service that hangs costs you a thread. An agent that hangs costs you the thread, a four-figure cloud bill, a runaway tool-call loop against a production system, and a very uncomfortable conversation with your finance team.

This chapter is about the runtime layer that catches those failures. The goal is simple: **no single agent run should ever consume more resources than you authorized — and the enforcement should happen in the scaffold, not in the prompt.**

---

## Three Budgets, Not One

Teams often think about "cost" as a single budget. In practice, agents need three budgets, and each needs its own limits, its own dashboards, and its own kill switches.

### 1. Token budget (and therefore dollar budget)

The sum of input and output tokens consumed by the model during a run. This is the one most teams track — and it is the one that surprises them most often when trajectories lengthen.

| Budget | What to enforce |
|:-------|:----------------|
| Per step | Max input tokens and max output tokens per model call. Above the cap, truncate or fail. |
| Per run | Max total tokens across all steps in a single run. Above the cap, halt and escalate. |
| Per user / per session | Max tokens consumed by a single caller in a defined window. Above the cap, rate-limit or refuse. |
| Per tenant / per day | Max aggregate tokens spent by a tenant per day. Above the cap, page the on-call. |

Every budget needs an owner and an alert policy. A budget with no alert is not a budget; it is a hope.

### 2. Tool-call budget

The number of tool calls the agent makes during a run. This is the second-most-important budget and the most-often-forgotten one.

- **Per run cap**: the absolute maximum number of tool calls allowed. Beyond this number, the runtime halts the agent and escalates. For the Support Triage Drafter, the cap was 5. For more complex agents, 20 is a reasonable starting ceiling. 50 is a smell. 100 is a bug.
- **Per tool cap**: the maximum number of times a single tool can be called in one run. Catches the common failure mode where the agent calls the same lookup over and over because it did not understand the result.
- **Per window cap**: the maximum number of invocations of an expensive tool across all runs in a given window — particularly important for paid APIs and irreversible actions.

Tool-call budgets are the ceiling under which [Chapter 6's](./06-system-prompts-as-contracts.md) stop conditions live. The prompt says "stop after 5"; the runtime *enforces* stop after 5, regardless of what the prompt says.

### 3. Wall-clock budget

The total elapsed time a run can take. This is about users, not money.

- **Per interaction type**: chat-facing agents have seconds; background jobs have minutes; batch jobs have longer but still bounded windows.
- **Per step**: a single tool call that hangs should not hold up the whole run. Wrap every tool call in a timeout and treat a timeout as a `tool_error` outcome that the agent should escalate on.
- **Per model call**: similarly, model calls get their own timeout. If a single model decision takes longer than X seconds, the scaffold aborts the call and treats it as a transient failure.

A common mistake is to set only an end-to-end wall-clock budget and trust the individual steps to respect it. That does not work — a single stuck step can absorb the whole budget before the scaffold knows what to do with the time left.

---

## Soft Limits, Hard Limits, and Kill Switches

Each budget gets three enforcement tiers. Mixing them up is how teams end up with alerts that fire during normal operation (useless) or kill switches that fire too late to matter.

### Soft limit (warning)

A threshold below the hard limit that triggers observability events but does not halt the run. Its purpose is to catch drift early.

- *"This run has now used 75% of its token budget."* → record a warning in the trace, increment a dashboard metric, move on.
- Soft limits are tuned to fire on the p95 of normal runs — above that is "unusual," not "broken."

### Hard limit (halt)

A threshold that stops the run. Past this limit, the agent does not get another step.

- *"This run has used 100% of its token budget."* → halt the run, emit a structured failure outcome (`budget_exceeded` from Chapter 10), escalate if an escalation path exists, notify the caller.
- Hard limits are enforced by the scaffold, not by the prompt. The prompt's stop conditions are the polite version of the same rule; the scaffold is the last line of defense if the prompt fails.

### Kill switch (global halt)

A control the on-call engineer can flip that immediately stops all agent activity — or all activity of a specific agent, or all activity on a specific tenant. The goal is to be able to make a bad thing stop happening in seconds, not in the 20 minutes it takes to merge a code change.

A usable kill switch has four properties:

1. **Reachable in one command or one click.** Not *"submit a PR to the config repo."* A button, a CLI flag, a feature-flag toggle.
2. **Scoped.** You can kill one agent, one tool, one tenant, or everything — not just "all or nothing." You want the smallest blast radius that stops the problem.
3. **Graceful and hard modes.** Graceful drains existing runs and refuses new ones. Hard aborts everything in flight. Both are useful; they serve different incidents.
4. **Tested.** A kill switch that has never been fired does not exist. Fire it on purpose in a drill at least once a quarter.

Kill switches are a dependency of the incident response playbook in [Chapter 19](./19-monitoring-and-incident-response.md). Build them first, build the playbook second.

---

## Detecting Runaway Loops

A classic agent failure mode: the model keeps calling tools without making progress, each step looking locally reasonable, the budgets nominally respected, but the run as a whole going nowhere. Tool-call budgets eventually catch it, but by then you may have made 20 calls to a paid upstream. Better to catch it earlier.

Three cheap heuristics:

### Repetition detection

If the agent calls the same tool with semantically equivalent inputs more than N times in a single run, halt the run and escalate. "Semantically equivalent" means after normalizing — whitespace, order of fields, trivial paraphrasing — so a retry pattern like `fetch_order_status(ORD-1)` → `fetch_order_status(ORD-1)` → `fetch_order_status(ORD-1)` fires the alarm on the second or third repeat.

### Progress checks

Every few steps, ask the runtime: *is the agent closer to completion than it was N steps ago?* One simple signal: has the tool set being used changed, or has the agent been hammering the same two tools for a while? If nothing new is happening, escalate.

More sophisticated progress checks use a lightweight "supervisor" model (or a deterministic rubric) to score the trajectory against its stated goal. When progress stalls, the runtime halts the run. This is overkill for small agents and essential for big ones.

### Budget velocity

Track the rate at which the run is consuming its budgets. If tokens or tool calls are being consumed faster than expected for the current step, that is a leading indicator that the run is going to overshoot. Halt early and escalate, rather than waiting until the hard limit is reached.

Any of these is better than none. All three, layered, will catch the vast majority of runaway loops before they become incidents.

---

## Rate Limiting the Agent's Side Effects

Budgets protect *you* from the agent's cost overruns. Rate limits protect *the world* from the agent's side effects.

For every tool that touches an external system, enforce:

- **Per-run rate limits**: no more than N calls to this tool in a single run.
- **Global rate limits**: no more than M calls to this tool per minute across the entire fleet, regardless of how many agents are running.
- **Backpressure**: if a downstream API is rate-limiting you, the tool returns a structured retryable error rather than swallowing it — so the agent learns from the failure and the scaffold can decide whether to retry.
- **Circuit breakers**: if a tool has been failing at a high rate for the last few minutes, stop routing calls to it entirely. Return a `circuit_open` error for a cool-down period. Fail fast rather than pile up retries against a broken dependency.

Rate limits especially matter for:

- **Paid APIs** (LLM calls, search APIs, payment APIs).
- **Email / SMS / notification tools** — a loop here becomes spam very quickly.
- **Write-heavy tools** that touch shared resources (queues, databases, filesystems).

Treat the rate-limit configuration as part of the tool's contract from [Chapter 5](./05-tool-interface-design.md). It is not an operational afterthought.

---

## Making Budgets Visible to the Model

The model can cooperate with your budgets, but only if it knows about them. A lightweight pattern: surface the remaining budget in each step's context, so the model can decide when to wrap up.

Something like:

```text
[runtime] Tool calls used: 3 of 5. Tokens used: 4,200 of 6,000. Time used: 8s of 20s.
```

Two effects:

- The model becomes more likely to finish or escalate before the limit rather than pushing up against it.
- The trace now records, at every step, exactly how much room was left — useful in the post-mortem.

This is *assistance*, not *enforcement*. The scaffold still enforces the caps regardless of what the model does. But models that know the room they have tend to use it well, and the cost of telling them is trivial.

---

## A Worked Configuration

For the Support Triage Drafter, the budgets look like this:

```text
PER RUN
- max_tokens: 6,000 total (input + output)
- max_output_tokens: 1,500
- max_tool_calls: 5
- max_wall_clock: 20 seconds
- max_calls_to_single_tool: 3

SOFT LIMITS (warn, do not halt)
- 75% of token budget
- 4 tool calls
- 15 seconds wall clock

HARD LIMITS (halt and escalate)
- 100% of token budget
- 5 tool calls
- 20 seconds wall clock
- Any tool call repeated with identical input twice in a row

RATE LIMITS
- fetch_order_status: 100 req/min/tenant, circuit-break at 20% error rate
- post_reply_to_review_queue: 30 req/min/agent
- escalate_to_human: unlimited (but counted)

KILL SWITCH
- Feature flag triage_drafter.enabled — graceful drain.
- Feature flag triage_drafter.hard_stop — immediate abort.
- Tested in drill 2026-03-01; recovery time 45s.
```

Notice how specific every number is. Vague budgets ("a few thousand tokens," "a couple of tool calls") do not enforce; they hope. Real enforcement needs real numbers.

---

## Anti-Pattern: Kill-Switch Absent

**Symptom**: The agent is in production. Something goes wrong — a bad prompt change, a runaway loop, an upstream API glitch making every run fail spectacularly, a prompt-injection campaign hitting an inbound channel. The on-call engineer's only option to stop it is *"push a config change, wait for deploy, hope."* Meanwhile the agent is burning money, flooding a downstream queue, or writing the same bad draft to the review queue over and over.

**Why it hurts**: The response time for an agent incident is measured in minutes. If the mitigation is measured in tens of minutes, the mitigation is slower than the damage. By the time the deploy is live, the dashboard is red, the budget is toast, and the post-mortem is already writing itself.

**Fix**: Build the kill switch before the agent ships. One command, one click, one flag. Scoped so you can stop one agent without stopping everything. Tested at least once in a drill. Documented in the incident playbook with the exact command to run. If you cannot stop your agent in under a minute, you are not ready to run it in production.

---

## Checklist

- [ ] Token, tool-call, and wall-clock budgets are all defined with explicit numbers — not "a reasonable amount."
- [ ] Every budget has a per-step, per-run, and per-window limit.
- [ ] Each budget has both a soft limit (warning) and a hard limit (halt).
- [ ] Hard limits are enforced in the scaffold, not just the prompt.
- [ ] A runaway-loop detector is in place: repetition detection, progress checks, or budget velocity tracking (ideally all three).
- [ ] Every expensive or side-effectful tool has per-run and global rate limits.
- [ ] A circuit breaker closes off failing tools so the agent fails fast instead of looping.
- [ ] A kill switch exists, is scoped, is reachable in seconds, and has been tested in a drill.
- [ ] Remaining budgets are visible to the model during each step.
- [ ] The budget configuration is version-controlled alongside the agent's code.

---

## What to Read Next

- [Chapter 7 — Model Selection for Agents](./07-model-selection.md): the cost math that tells you what the right budget even is.
- [Chapter 10 — Observability from Day One](./10-observability-from-day-one.md): the telemetry that makes soft limits and dashboards possible.
- [Chapter 11 — Escalation Paths & Human-in-the-Loop](./11-escalation-and-hitl.md): what happens when a budget or kill switch triggers.
- [Chapter 19 — Monitoring & Incident Response](./19-monitoring-and-incident-response.md): the production playbook that consumes the kill switches this chapter defines.
