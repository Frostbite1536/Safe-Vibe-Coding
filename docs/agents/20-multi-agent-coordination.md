---
layout: default
title: 20. Multi-Agent Coordination
nav_order: 20
parent: Agents Guide
description: "Orchestrator versus worker patterns, handoff contracts between agents, avoiding shared mutable state, and why 90% × 90% = 81% reliability compounds badly in pipelines."
permalink: /agents/multi-agent-coordination
---

# 20. Multi-Agent Coordination

At some point, someone on your team will propose "just spinning up another agent" to solve a new subproblem. This often seems like the right idea — agents are modular, bounded, and easier to reason about than monoliths. And sometimes it really is the right idea. But multi-agent systems bring in a new class of failures that single-agent systems do not have, and the failures compound much faster than the benefits.

This chapter is about when multiple agents are the right design, how to coordinate them safely, and — most importantly — how to avoid the trap that multi-agent systems set for otherwise careful teams.

---

## The Reliability Math, Again

Recall the reliability table from [Chapter 3](./03-when-to-build-an-agent.md): at ~95% reliability per step, a 10-step trajectory ends up around 60% reliable end-to-end. That math was for a single agent. For a pipeline of agents, it gets *worse*, because you multiply not just across steps but across agent boundaries.

Two 90%-reliable agents chained together give you ~81% reliability end-to-end.

Three give you ~73%.

Five give you ~59%.

That is the entire argument against the casual multi-agent architecture. Every time you split work across an agent boundary, you introduce a new failure surface — the handoff — and you multiply the per-agent error rates. If each agent is not *very* reliable on its own piece, and the handoffs are not *very* reliable between them, the pipeline is not worth building.

Two consequences follow:

1. **Multi-agent systems should be rare, not the default.** The question is never *"could we use another agent here?"* but *"is this problem big enough that the reliability hit is worth paying?"*.
2. **When you do use them, each individual agent has to be much better than you think.** 90% is not enough. 95% is barely enough. Treat every agent in a multi-agent system as if the combined system's reliability is its responsibility, because in practice it is.

---

## When Multi-Agent Actually Helps

There are three situations where splitting work across multiple agents pays for its reliability cost. Outside these situations, prefer a single agent with more tools, or a deterministic pipeline with one agent embedded in it.

### 1. Scope separation for safety

The clearest case: a task requires two capabilities whose *combination* is dangerous, and splitting them across agents lets you enforce least privilege per agent.

- An "inbound triage" agent has read access to customer emails and can classify them, but cannot touch the database.
- An "order lookup" agent has database read access but never sees raw email content.
- Between them, an orchestrator that routes based on the triage output.

Neither agent alone has the data or permissions to cause a serious incident. An attacker who compromises one of them runs into the boundary before reaching the other. This is the multi-agent pattern as an *architectural* safety measure, not a convenience.

### 2. Parallelism for throughput or latency

When a task decomposes into independent subtasks that can run at the same time, multiple agents running in parallel can be dramatically faster than one agent sequencing the work itself. A research agent that can dispatch five concurrent retrievers and then summarize the results is a canonical example.

The reliability math is gentler here: parallel subtasks fail independently, and a single subtask failure does not necessarily break the overall task. But the handoff discipline still matters — the orchestrator has to know what to do when two of the five workers disagree, or one fails entirely.

### 3. Orchestrator/worker specialization (Chapter 7's pattern generalized)

The pattern introduced in [Chapter 7](./07-model-selection.md) — a reasoning-heavy orchestrator delegating narrow subtasks to cheaper fast workers — generalizes from "different models" to "different agents." If a subtask is well-defined enough to have its own scope brief, its own tool set, its own evals, and its own escalation rules, it can be its own agent.

This is the most legitimate multi-agent pattern. Used well, it keeps each agent small, boring, and reliable. Used poorly, it becomes tool sprawl at the agent level — which is much worse than tool sprawl at the tool level, because every agent has its own scope, its own prompt, its own state, and its own bugs.

---

## Orchestrator and Worker Roles

Every multi-agent system has one of two shapes. Pick one deliberately. Mixing the shapes inside a single system is a design smell.

### Orchestrator / worker (hub-and-spoke)

One orchestrator agent holds the overall goal. It decomposes the task, dispatches subtasks to workers, collects their results, and decides what to do next. Workers do not talk to each other; they talk to the orchestrator.

Pros:

- Clear accountability. If the task fails, the orchestrator is responsible.
- Easier to observe. One trace per task, with sub-traces branching out from it.
- Easier to bound. The orchestrator's tool-call budget includes the worker invocations, so there is a single number that caps the cost of the whole task.

Cons:

- The orchestrator is a bottleneck. If it crashes, the whole task fails.
- The orchestrator has to understand every worker's capabilities — its tool list grows as you add workers.

This is the default pattern. When in doubt, use it.

### Peer-to-peer (mesh)

Multiple agents talk to each other directly, without a central orchestrator. Each agent may hand off to any other agent based on its own judgment.

Pros:

- Flexible — agents can route work based on local conditions.
- Resilient — no single bottleneck.

Cons:

- Much harder to reason about. Any agent can trigger any other, so the action space is the product of all agents' tool lists *and* every permutation of handoffs.
- Much harder to observe. A single user task can fan out through an arbitrary set of agents, and the "trace" is actually a graph.
- Much harder to bound. Without a central coordinator, who owns the budget? Who decides when the task is done?

Peer-to-peer multi-agent systems exist and can be valuable, but they are research-grade complexity. Do not build one unless the problem genuinely requires it and you have the observability infrastructure to handle a graph of runs rather than a linear trace.

---

## Handoff Contracts

The single most important artifact in a multi-agent system is the *handoff contract* — the precise definition of what one agent passes to another. Treat it exactly like the tool contracts from Chapter 5.

A handoff contract defines:

- **The input schema**. What fields the receiving agent expects, typed and constrained. `additionalProperties: false`.
- **The output schema**. What the receiving agent will return, including its success, error, and escalation shapes.
- **The side-effect declaration**. What the receiving agent may do in the world during the handoff.
- **The authorization boundary**. Who is the "caller" when Agent A invokes Agent B? The original user, or Agent A itself? The receiving agent's permission checks need to know.
- **The failure modes**. What can go wrong, how is it reported, and who handles retries.
- **The budget**. How many tokens, how many tool calls, how much wall-clock the receiving agent is allowed to spend.

Handoffs are the place where the compound reliability story either works or collapses. A handoff with a vague contract is a handoff that fails ambiguously — and ambiguous failures are the ones that eat investigation time.

### Handoffs as typed calls, not free-form messages

The biggest trap is letting agents communicate through free-form natural language. It looks natural — *"Agent A asks Agent B to look something up"* — and it is a terrible idea. Every free-form handoff is a mini-prompt-injection vector and a place where misunderstandings compound.

Structure the handoff as a typed function call:

```json
{
  "from": "triage_orchestrator",
  "to": "order_lookup_agent",
  "task": "fetch_order_status",
  "input": {
    "order_id": "ORD-18293746",
    "customer_email_hash": "abc123..."
  },
  "caller_context": {
    "user_id": "user_42",
    "tenant_id": "tenant_7"
  },
  "budget": {
    "max_tokens": 2000,
    "max_tool_calls": 3,
    "max_wall_clock_ms": 5000
  }
}
```

The receiving agent parses this, authorizes against `caller_context`, runs inside the handed-down budget, and returns a typed response. If the orchestrator wants to "tell the worker something in natural language," it goes into a `context` field labeled as data, not instructions.

---

## Authorization Across Agents

When Agent A calls Agent B, whose permissions apply?

This question has wrecked more multi-agent systems than any other, and it has exactly one correct answer: **the permissions of the original caller propagate along the call chain, never accumulate.**

Concretely:

- If the user is allowed to read their own orders but not others', Agent B (the worker) must refuse to read a different user's orders *even when Agent A is the one asking*.
- Agent A cannot "vouch" for actions the user is not allowed to take. Agent A's own tool list does not grant it the right to ask Agent B to do something the user would be refused.
- Every handoff includes the original caller context. Every receiving agent's tools enforce against that context, not against "whoever is calling the tool right now."

This is the same principle as impersonation in a normal service-to-service call: the downstream service acts on behalf of the original user, not on behalf of the upstream service. Agents are no different.

The alternative — "well, the orchestrator is a trusted agent, so its calls get full permissions" — creates a privilege-escalation attack waiting to happen. Prompt injections into the orchestrator now let the attacker do anything the orchestrator's "trusted" role can do, which in practice is everything.

---

## Shared State Is a Liability

If the agents in a multi-agent system share a mutable state — a scratchpad, a shared memory store, a "conversation context" object they all read and write — you have turned a coordination problem into a concurrency problem, and agents are very bad at concurrency.

Two things go wrong:

1. **Ordering bugs.** Agent A reads X, Agent B writes X, Agent A acts on stale data. The bug is invisible in the logs because both agents did what they were asked.
2. **Injection across agents.** Content that made it into the shared state from Agent A's context becomes an instruction to Agent B. Worse, this can cross tenant or trust boundaries if the shared state is not scoped carefully.

Rules:

- **Prefer message-passing over shared memory.** Each agent's state is its own; data moves through explicit handoffs.
- **If you must share state**, make it read-only for all agents except one designated writer, and treat reads as potentially stale.
- **Never share state across trust boundaries**. If Agent A's content is untrusted (handles external input) and Agent B's actions are sensitive, they do not share anything except a typed handoff.
- **Tag every state entry with its origin** so downstream agents know where a fact came from and whether to trust it.

Shared state is the single biggest reason multi-agent systems drift in ways that are hard to debug. The cost of avoiding it is almost always smaller than the cost of debugging it.

---

## Observability Across Agents

Every tool from [Chapter 10](./10-observability-from-day-one.md) applies — but with a twist: a single user task now produces a *tree* (or graph) of runs, not a single trace.

What to add:

- **Parent-child run IDs**. Every sub-agent run has a `parent_run_id` that links to the run that invoked it. You can reconstruct the whole tree from any leaf.
- **End-to-end task ID**. A top-level identifier that ties together all runs produced by a single user request, across every agent.
- **Cross-agent timeline view**. A dashboard or tool that shows the whole tree as a timeline — orchestrator on top, workers as children, each with its own mini-trajectory. The ability to see the whole task at once is essential for debugging multi-agent bugs.
- **Aggregated budgets**. The task-level total of tokens, tool calls, and wall-clock across every agent involved. Because a single user request that fans out to four workers might show normal per-agent cost but be three times more expensive than intended.
- **Cross-agent error correlation**. When Agent A escalates because Agent B returned a malformed response, the log should let you hop from one to the other in one click.

Build this before you ship the second agent. Retrofit is painful and always partial.

---

## A Worked Multi-Agent System

Suppose we extend the Support Triage Drafter into a three-agent system:

- **Triage Orchestrator**: reads the inbound email, classifies the topic, decides which specialist to hand off to, and assembles the final draft.
- **Order Lookup Worker**: given an order number or customer email, returns structured order data. No text generation; no side effects beyond reads. Has the database tools; has *no* email tools.
- **Draft Writer Worker**: given a topic, structured order data, and tone requirements, returns a draft reply. Has no database access; has no customer-facing tools.

The scope of each agent is narrower than the original triage drafter; the per-agent reliability of each is higher precisely because their tool sets are tiny.

A flow:

1. Email arrives. Orchestrator classifies it as "order status question" and extracts an order number.
2. Orchestrator invokes Order Lookup Worker with `{order_id, caller_context}`. Budget: 2K tokens, 2 tool calls, 5s.
3. Worker calls `fetch_order_status`, gets the result, returns a structured payload. The structured payload includes `fetched_at` so the orchestrator can see how fresh it is.
4. Orchestrator invokes Draft Writer Worker with `{topic="status", order_data, tone="support_team"}`. Budget: 2K tokens, 0 tool calls (pure generation), 5s.
5. Worker returns a draft.
6. Orchestrator posts the draft via `post_reply_to_review_queue`, which is the *only* side-effect tool on the entire system.
7. Orchestrator returns.

Notice the properties:

- Each worker has a tiny tool list and is easy to evaluate in isolation.
- No worker can send a message. The only outbound channel is owned by the orchestrator, and even that channel goes to a human-reviewed queue.
- Shared state: none. All data moves through typed handoffs.
- Authorization: the orchestrator passes the caller context down; both workers check it against their own tools before acting.
- Observability: one top-level run ID, three child run IDs, one tree view that shows the whole path.

And notice what you bought for this:

- Cost: three agent invocations per email instead of one. Budget math says this is roughly 1.5–2× more expensive than the single-agent version.
- Latency: slightly worse, because of the handoff overhead.
- Complexity: three scope briefs, three prompts, three eval sets instead of one.

This is a multi-agent system that would be justified if — and only if — the *safety* benefit of splitting database access from email context is large enough to pay for those costs. If the safety benefit is modest, the single-agent version is still better.

---

## Anti-Pattern: Multi-Agent Theater

**Symptom**: The team has built a system with three, five, or ten agents. The architecture diagram is complicated. The scope briefs for each agent are thin. The handoff contracts are natural language. Agents share a "conversation state" object they all read and write. When something goes wrong, the trace is a tangle of overlapping runs and nobody can tell which agent was responsible. Reliability is worse than the single-agent version it replaced.

**Why it hurts**: Multi-agent systems are impressive-looking and demo well. They are also where reliability goes to die when they are built for the wrong reasons. Every one of the safety principles in Parts I–IV still applies to each individual agent, *and* to every handoff, *and* to the system as a whole. Skimping on any of them turns the multi-agent architecture into exactly the failure mode it was supposed to prevent — sprawling, unbounded, and impossible to observe.

**Fix**: Start with one agent and more tools. Only split into multiple agents when you have a *named, specific* reason — scope separation for safety, parallelism for throughput, or orchestrator/worker specialization from Chapter 7. For every new agent, write a full scope brief, a contract prompt, a tool list, an eval set, and a set of handoff contracts. If you cannot produce all of those, you do not yet have a design — merge the agents back together until you do.

---

## Checklist

- [ ] Every multi-agent system has a named reason to exist that corresponds to one of the three justified patterns (safety scope separation, parallelism, orchestrator/worker specialization).
- [ ] Each individual agent has its own full set of Part II / III artifacts: scope brief, tool set, system prompt, state strategy, budgets, escalation paths, and eval set.
- [ ] The system shape is deliberately chosen — orchestrator/worker as default, peer-to-peer only when justified.
- [ ] Every handoff has a typed contract with inputs, outputs, side effects, caller context, failure modes, and budget.
- [ ] Handoffs never carry free-form natural language instructions across agent boundaries.
- [ ] The original caller's permissions propagate through every handoff. No agent can exceed its caller's privileges, regardless of what the upstream agent asks.
- [ ] Shared mutable state across agents is avoided. Where it exists, it is scoped, origin-tagged, and read-mostly.
- [ ] Never share state across a trust boundary (between agents that touch untrusted content and agents that take sensitive actions).
- [ ] Observability includes parent-child run IDs, an end-to-end task ID, aggregated budgets, and a cross-agent timeline view.
- [ ] Evals score each agent in isolation *and* the whole system end-to-end.
- [ ] The reliability math has been computed — end-to-end reliability is projected based on per-agent reliability and acknowledged as the hard constraint.

---

## What to Read Next

- [Chapter 7 — Model Selection for Agents](./07-model-selection.md): the single-agent orchestrator/worker pattern that generalizes to multi-agent here.
- [Chapter 12 — Authorization, Sandboxing & Isolation](./12-authorization-and-sandboxing.md): the permission model that must survive across handoffs.
- [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md): how to score a multi-agent system end-to-end.
- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): tracking drift in each agent and across the system.
