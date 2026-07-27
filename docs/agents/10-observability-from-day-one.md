---
layout: default
title: 10. Observability from Day One
nav_order: 10
parent: Agents Guide
grand_parent: Guides
description: "Trace logging, decision audit trails, cost and latency tracking, and error categorization. Why logs are not optional, what to record for every tool call, and how to reconstruct any past agent decision."
permalink: /agents/observability-from-day-one
---

# 10. Observability from Day One

You cannot debug an agent you cannot observe. That sentence is the entire chapter compressed into nine words.

Every other chapter in this guide assumes observability is in place. The scope brief tells you what to watch for; the tool contracts tell you what to log; the evals tell you how to score; the incident playbook tells you how to respond. None of it works if the underlying traces are missing, incomplete, or unsearchable.

Observability is not a nice-to-have you add after the first bad incident. It is the thing that lets you see the first bad incident *coming*. Wire it up before the agent's first real run.

---

## Why Agents Need More Observability Than Regular Services

A traditional service is relatively easy to observe. You log the request, you log the response, you log a handful of key internal states, and 95% of the time that is enough to explain what happened.

Agents are not like that. Three properties make them observationally harder:

1. **The control flow is chosen at runtime.** You do not know which tools will be called in which order until the model decides. Pre-instrumented hot paths do not cover enough of the actual behavior.
2. **The "why" matters as much as the "what".** Knowing the agent called `fetch_order_status` is not enough. You need to know *why it chose to*, especially when the choice was wrong.
3. **Failures are often silent.** An agent that politely hallucinates a success looks fine in normal logs. The only way to catch it is to log enough of the reasoning that you can tell hallucination from fact after the run.

These properties turn observability from a fringe concern into a first-order design constraint.

---

## What to Log for Every Run

For every agent run, your audit trail should contain enough information to answer, without a follow-up conversation with anyone, the question *"why did the agent do that?"*

At minimum:

### Run metadata

- **Run ID** — a unique identifier that you can search on.
- **Timestamp** — when the run started and when it ended.
- **Agent version** — the git SHA or tag of the code that served the run.
- **Prompt version** — a hash of the system prompt used, so you can tell which prompt revision was live.
- **Model ID** — the exact model name and version.
- **User / caller context** — who triggered the run, from what surface.

Without all six of these, you will one day try to investigate a bad run and discover you cannot reproduce it.

### The inputs

- The full system prompt.
- The full user message (redacted if necessary — see "Privacy" below).
- Any conversation history or retrieved memory that was injected.
- The exact tool schemas the model saw.

These are the things that, together, fully define the agent's starting conditions. Miss any of them and your post-mortem has a hole.

### The full trajectory

For every step:

- The model's reasoning output, if the model produced any (some models return an explicit chain-of-thought; log it when it exists).
- The tool call, with the tool name, the exact input JSON, and a timestamp.
- The tool response, with the full output JSON, the execution time, and any internal error codes.
- Whether the runtime modified the response (compaction, redaction, truncation).

"Full trajectory" is a load-bearing phrase. Logging the first and last steps is not enough. Agents fail between steps.

### The outcome

- The final response or the final action taken.
- A structured success/failure classification (see "Error categorization" below).
- Token counts per step and totals.
- Dollar cost per step and totals.
- Whether the run escalated, and if so, with what reason.
- Whether the run hit a runtime guardrail (token ceiling, tool-call ceiling, time ceiling).

### The decision audit trail

This is the agent-specific observability that teams most often skip.

For each tool call, record *why the model selected that tool*. Some models return an explicit "rationale" field; others do not. When they do not, you have two options:

1. **Ask the model to include a short rationale in the tool input.** Add a `reason` parameter to each tool's schema that is required and not used for business logic — purely observability. Most models are happy to fill it in, and it gives you a short sentence per call.
2. **Log the context delta.** Record what was *new* in the context since the previous step, so you can see what information the model had when it made the decision.

Either way, you should be able to open any run in the log and answer *"why did it call this tool?"* without guessing.

---

## Error Categorization

Not all failures are the same. A well-observed agent distinguishes at least these categories — and the category is stamped into the log at the moment the failure occurs, not inferred later:

| Category                 | What it means                                                | Example                                         |
|:-------------------------|:-------------------------------------------------------------|:------------------------------------------------|
| `tool_error`             | A tool raised an exception or returned an error shape.       | Database timeout, 500 from upstream API.        |
| `tool_refused`           | A tool rejected the call because of authorization or input validation. | Cross-customer lookup attempted.          |
| `model_parse_error`      | The model produced output the runtime could not parse as a valid tool call. | Malformed JSON, hallucinated tool name.   |
| `budget_exceeded`        | The run hit a token, tool-call, or wall-clock ceiling.       | 5th tool call triggered the ceiling.            |
| `escalation`             | The agent voluntarily escalated via `escalate_to_human`.     | Ambiguous input, out-of-scope question.         |
| `invariant_violation`    | A post-hoc check caught the agent doing something the scope brief forbids. | Draft mentioned a different customer.    |
| `user_cancel`            | The user or upstream caller cancelled the run.               | Chat window closed.                             |
| `success`                | The run completed its goal.                                  | Draft posted to the review queue.               |

With these categories in place, you can produce a one-glance dashboard that tells you whether the agent is mostly succeeding, mostly escalating, mostly hitting budget ceilings, or mostly crashing on tool errors. Each of those requires different interventions.

---

## Cost and Latency Tracking

Cost and latency are the observability signals that catch reliability problems before the users do.

### Per-run

- Total input tokens, total output tokens, total dollar cost.
- Wall-clock duration from first model call to final response.
- Number of tool calls.
- Model ID (costs differ per model).

### Per-step

- Time-to-first-token.
- Time-to-decision.
- Tool execution time.
- Tokens consumed this step.

### Aggregates

- p50, p95, p99 latency per interaction type.
- p50, p95, p99 cost per interaction type.
- Trajectory length distribution — are most runs 3 steps, or is there a long tail at 15?

The aggregates matter because agents have long tails. A p50 run is fine; a p99 run is the one that costs $5 and takes 90 seconds. If you only watch averages, you will miss the runs that are eating your budget and making your users wait.

See [Chapter 13](./13-cost-and-kill-switches.md) for how to enforce limits once you can see them.

---

## Sampling vs. Logging Everything

A common question: *"Our agent runs 100K times a day — do we really log every run in full?"*

The default answer is **yes**. Agent runs are small compared to classic web request logs, and the information density is much higher per event. You will rarely regret having too much.

When you really cannot afford to keep everything, use a *risk-weighted* sampling strategy, not a simple percentage:

- **Always keep 100%**: escalations, invariant violations, budget-exceeded runs, tool errors, and any run flagged by the eval harness.
- **Always keep 100%**: runs involving new users, new tools, or a prompt/model version released in the last N days.
- **Sample 10–100%**: nominal successful runs on established code.
- **Never drop**: the decision audit trail for any run you keep at all. Truncating the trajectory is how you get "we kept the logs but we still cannot explain the failure."

The cheap storage class is your friend. Move old full logs to cold storage rather than deleting them — you will want them the first time a regression needs a six-week-old baseline.

---

## Privacy and Redaction

Agent logs are high-value forensic data. They are also a compliance surface: they likely contain personal data, business secrets, and tool credentials that must not leak.

Two rules:

1. **Redact at ingest, not at query time.** Strip tokens, API keys, and obvious PII before the log lands in storage. Retroactive redaction is too late.
2. **Log *that* something was redacted.** Do not silently drop fields. A log entry should say "input contained an email address (redacted)" so the downstream reader knows the field existed.

Category-based redaction works well:

- Bearer tokens, OAuth codes, API keys → always stripped.
- Email addresses, phone numbers → stripped outside of the logs that need them.
- Full message bodies → kept in a restricted-access log tier; summaries in the general tier.

Design this before the first real run, because retroactively fixing "the logs contain everyone's credit card numbers" is a bad week.

---

## Making Logs Usable

A log no one reads is not observability; it is compliance theater. To be usable, the log must be:

1. **Searchable by run ID, user, agent version, prompt version, outcome, and error category.** If you cannot narrow down to "all runs where the agent escalated with `reason='ambiguous'` last Tuesday," you will not be able to investigate.
2. **Linkable from every user-facing artifact.** Every draft, every escalation, every error surfaced to the user should carry the run ID so a support rep can jump directly to the trace.
3. **Diffable between versions.** When you change the prompt or a tool, you want to compare trajectories on the same inputs before and after. Tooling that supports side-by-side trace diffs pays for itself the first time you use it.
4. **Exportable as eval cases.** A bad run should become a new eval case in one click. The feedback loop from "we found a bug" to "we added a regression test" should be minutes, not hours.

Build this tooling alongside the agent. Do not wait for the first crisis.

---

## A Minimal Log Entry

Here is what a single step's log entry might look like, stripped to the essentials:

```json
{
  "run_id": "run_01JKM8Z...",
  "step": 2,
  "timestamp": "2026-04-12T14:02:17.334Z",
  "agent_version": "triage-drafter@e7c3a91",
  "prompt_version": "sha256:…",
  "model": "claude-sonnet-4-6",
  "reasoning": "The user provided an order number; I'll look it up directly.",
  "tool_call": {
    "name": "fetch_order_status",
    "input": { "order_id": "ORD-18293746" }
  },
  "tool_result": {
    "status": "shipped",
    "estimated_delivery": "2026-04-15",
    "tracking_url": "https://…",
    "fetched_at": "2026-04-12T14:02:17.502Z"
  },
  "tool_latency_ms": 168,
  "tokens": { "input": 1780, "output": 64 },
  "cost_usd": 0.0062,
  "outcome": "ok"
}
```

Nothing fancy — but every field is there for a reason. Remove one and a specific class of post-mortem becomes impossible.

---

## Anti-Pattern: Observability Theater

**Symptom**: The team has a logging system. Dashboards exist. Someone put "observability" on the roadmap and ticked it off. But when a real incident happens, no one can find the failing run, the logs do not contain the reasoning, tool inputs were truncated to save space, and the only way to understand what went wrong is to try to reproduce the failure by hand.

**Why it hurts**: This is the worst of both worlds — you paid for a logging system, you trusted it enough to skip defensive testing, and it does not answer the questions you actually need answered. Incidents last longer because the first hour is spent realizing the logs are not going to help.

**Fix**: Pick the three questions you most often want to answer after an agent does something wrong — *"why did it pick that tool?"*, *"what did the user actually say?"*, *"what was in the context when it decided?"* — and check that your current logging can answer all three from any run at random. If not, fix that before writing any more features. A log that cannot answer your real questions is not observability.

---

## Checklist

- [ ] Every run has a unique, searchable run ID.
- [ ] Every run records agent version, prompt version, and model ID.
- [ ] The full system prompt, user input, and tool schemas are logged at run start.
- [ ] Every tool call logs its name, input, output, latency, and tokens.
- [ ] A decision audit trail exists — either a model-native rationale or a mandatory `reason` field on each tool.
- [ ] Errors are classified into a fixed set of categories at the moment they occur.
- [ ] Cost and latency are tracked per step and per run.
- [ ] Aggregates (p50, p95, p99) for cost and latency are dashboarded.
- [ ] PII and secrets are redacted at ingest, and redaction events are themselves logged.
- [ ] Logs are searchable by run ID, user, version, outcome, and category.
- [ ] Any bad run can be exported to the eval set in one click.
- [ ] You have tested the "can we explain a past run?" question against real, random runs — not hypothetical ones.

---

## What to Read Next

- [Chapter 11 — Escalation Paths & Human-in-the-Loop](./11-escalation-and-hitl.md): escalations are one of the most important categories of run to log and review.
- [Chapter 13 — Cost, Rate-Limiting & Latency Budgets](./13-cost-and-kill-switches.md): enforcement of the limits you measure here.
- [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md): turning bad runs in the audit log into regression cases.
- [Chapter 19 — Monitoring & Incident Response](./19-monitoring-and-incident-response.md): the production layer on top of everything in this chapter.
