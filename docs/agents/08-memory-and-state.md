---
layout: default
title: 8. Memory & State Management
nav_order: 8
parent: Agents Guide
description: "Conversation history, scratchpads, vector stores, and long-running state. How state becomes the single biggest source of agent bugs and how to bound, compact, and forget it deliberately."
permalink: /agents/memory-and-state
---

# 8. Memory & State Management

Agents are stateful. That single sentence is the source of most mysterious agent bugs.

A pure function of inputs is easy to reason about — given the same input, you get the same output. An agent sits between a user, a conversation history, a scratchpad of prior reasoning, a set of tools that each carry their own state, and sometimes a long-term store that persists between sessions. Any of those can change between runs. Any of them can silently poison a later decision. Any of them can leak data that was supposed to stay in a prior conversation.

State is not optional for agents — some problems genuinely require it — but it must be *explicit*, *bounded*, and *deliberately forgotten*.

---

## The Four Kinds of Agent State

Before deciding how to manage state, name which kind you are talking about. These four categories behave differently and deserve different strategies.

### 1. Trajectory state (this run)

Everything the model sees during a single run: the system prompt, the user message, each tool call and its result, and any intermediate reasoning the model produced.

- **Lifetime**: one task, start to finish.
- **Typical size**: grows linearly with each step.
- **Risk**: runaway growth → context rot, higher cost, slower decisions.
- **Rule**: bounded at the *runtime level*, not just trusted to stay small.

### 2. Conversation state (this session)

The back-and-forth history of a multi-turn conversation with a user: prior user messages, prior agent responses, prior tool outputs from earlier turns.

- **Lifetime**: one user session — could be minutes or hours.
- **Typical size**: grows with turn count, unbounded by default.
- **Risk**: old turns carry stale context into new decisions; sensitive data from early turns keeps reappearing.
- **Rule**: compacted aggressively and summarized rather than kept verbatim.

### 3. Long-term memory (across sessions)

State the agent carries between sessions: the user's preferences, facts it has been told, documents it has stored for retrieval, learned patterns.

- **Lifetime**: indefinite unless deleted.
- **Typical size**: grows forever unless capped.
- **Risk**: the biggest source of "why did the agent say that?" bugs; also the biggest source of privacy incidents.
- **Rule**: write-gated, read-gated, and *expirable*.

### 4. Tool-side state (outside the agent)

State that lives in the systems the tools touch: the database, the review queue, the vector index, the file the agent wrote last time.

- **Lifetime**: controlled by the external system.
- **Typical size**: whatever the system permits.
- **Risk**: the agent forms beliefs about the world that are out of date by the time the next step runs.
- **Rule**: tools are read at the moment of use; never cached in the model's context.

A memory strategy names all four categories and decides, per category, how big they get, how they are compacted, when they are forgotten, and who can read or write them.

---

## The Context-Window Budget

Trajectory state has a hard ceiling — the model's context window — and a soft ceiling you should set much lower than the hard one. As trajectory length grows, three bad things happen at once: cost grows (Chapter 7), latency grows, and decision quality degrades.

Set a budget and enforce it at the runtime layer. A starting point:

| Budget item               | Starting allocation |
|:--------------------------|:--------------------|
| System prompt             | ≤ 1,000 tokens      |
| Tool schemas              | ≤ 1,500 tokens      |
| Conversation history      | ≤ 2,000 tokens      |
| Trajectory (this run)     | ≤ 4,000 tokens      |
| Headroom for final output | ≥ 1,000 tokens      |

This example totals 9,500 tokens in a 10K effective budget. Your numbers will differ, but the discipline is the same: **budget first, fit into it, refuse to exceed it**. If a run is bumping against the ceiling, that is a signal to compact, not to raise the ceiling.

When the budget fills up mid-run, you have three good responses and one bad one. The bad one is "just keep appending and hope." The good ones are:

1. **Compact**: summarize earlier tool results into a shorter form and replace the original output.
2. **Forget**: drop entries that are no longer decision-relevant.
3. **Escalate**: stop the run, hand off to a human, and start fresh.

Which response you pick should depend on the kind of state, not on convenience.

---

## Compacting Trajectory State

Compacting means summarizing earlier parts of the run into a shorter form the model can still reason over, then discarding the originals.

A simple pattern that works in practice:

1. At the end of each tool call, store the full tool result to your audit log (that is what observability is for — see [Chapter 10](./10-observability-from-day-one.md)).
2. In the model's visible context, keep only the **last N** full tool results (N = 2 or 3 is a reasonable default).
3. Everything before that becomes a short summary the runtime prepends: *"Earlier steps: looked up order ORD-1234 (status: shipped, ETA 2026-04-15)."*
4. The summary is generated either by a cheap worker model or by a deterministic formatter against the tool's structured output.

Three rules keep this safe:

- **Summaries are not decisions.** Do not drop a fact just because it seems unimportant right now. If you are not sure whether to keep a fact, keep it in the summary.
- **Summaries are verifiable.** The runtime should be able to reconstruct them from the audit log. Never hand-write a summary that lives only in the model's context.
- **The model never compacts its own history.** Compacting is a runtime operation, not a model operation. Letting the model rewrite its own context is a quiet way to lose information or to have it subtly fabricated.

---

## Conversation State: Summarize, Don't Hoard

Multi-turn conversations tempt you to keep everything. Don't. By turn 20, the full history is a liability: it is expensive to carry, it drowns the important parts of the current question, and it may contain data you should not still be handling.

A working strategy:

1. Keep the last 2–4 user/agent turns verbatim.
2. Replace older turns with a running summary that preserves:
   - User preferences that affect current answers (*"prefers metric units"*).
   - Facts the user has asserted that the agent has acted on (*"shipping to address on file"*).
   - Unresolved questions that are still open (*"waiting for customer to confirm order number"*).
3. Drop chat pleasantries, retracted statements, and duplicated tool outputs.
4. On every compaction, write the full replaced turns to the audit log.

You want the conversation summary to answer a very specific question: *if the next user message were the first one, what would the agent need to know?* Everything that does not help answer that question can be forgotten.

---

## Long-Term Memory: The Hardest Category

Long-term memory is where privacy incidents, scope drift, and "the agent made something up" bugs come from. Treat it with the same caution you would treat a production database — because that is what it is.

Four principles:

### Write-gated

Not every fact the agent encounters should end up in long-term memory. Ask two questions before a write:

- **Is this fact the user explicitly asked me to remember?** If yes, write it with clear provenance.
- **Is this fact a conclusion the agent inferred?** If yes, it should probably not be stored — inferences age badly and get remembered as facts.

A good rule: **the agent writes to long-term memory only through a tool, and the tool requires a `provenance` field.**

### Read-gated

When long-term memory is retrieved into the context, the model treats it as ground truth. That is dangerous if the source was weaker than ground truth.

- Retrieve memory in a separate, labeled section of the context (*"Memory (may be stale):"*) so the model can weight it appropriately.
- Stamp every fact with the time it was written and the source that wrote it.
- Prefer *structured* memory (typed fields) over free-form notes — the latter are a hallucination vector.

### Expirable

Long-term memory should have a TTL. A fact written today is more trustworthy than the same fact written a year ago; a preference from six months ago may not apply now. Set per-category TTLs and let the garbage collector do its job.

### User-controlled

If the memory contains user-specific information, the user must be able to view it, edit it, and delete it. This is not just a privacy requirement — it is a debugging tool. Many bugs turn out to be stale memory, and the fastest fix is often "delete that memory and try again."

---

## Tool-Side State: Read Fresh, Don't Cache

The agent's beliefs about the world should come from the most recent tool call, not from a step earlier in the same trajectory. A common bug:

> *The agent looks up an order in step 2. In step 5, it references the order status again, using the value from step 2. By that point the order has been updated, and the agent confidently reports stale information.*

Three mitigations:

- **Tools always read fresh.** Do not cache read results inside the agent; if a later step needs the same data, call the tool again.
- **Structured tool outputs carry a timestamp.** If the model sees *"fetched at 14:02"* it can notice when it is working from old data — especially across retries.
- **Writes return the new canonical state.** If the agent writes to a store, the tool's response includes the resulting state, so the model does not need to guess.

---

## Forgetting Is a Feature, Not a Bug

Most teams build agents that never forget and then wonder why behavior drifts. A healthy agent has explicit *forgetting events*:

- **Task completion**: the trajectory is cleared. The next task starts fresh.
- **Session end**: the conversation summary is written to long-term memory (if applicable) and the verbatim history is dropped.
- **Milestone completion**: see Chapter 21 — a long-running session checkpoint compacts state and confirms with the human.
- **Escalation**: when a task is handed off, the agent clears its working state. The human starts with clean context.
- **TTL expiration**: long-term memory entries expire on their written schedule without any explicit action.

Design the forgetting events before the agent ships. Adding them later requires rewriting the state code and — worse — re-building a user's trust after an incident.

---

## A Worked Example

Back to the Support Triage Drafter. Here is its full state strategy in one page:

```text
STATE STRATEGY: Support Triage Drafter

TRAJECTORY STATE
- Budget: 4K tokens for run, hard-capped at 5K.
- Keep last 2 full tool results verbatim.
- Older tool results replaced with deterministic summaries
  generated from structured output.
- Clear on task completion.

CONVERSATION STATE
- N/A: each incoming email is its own task. No multi-turn.

LONG-TERM MEMORY
- None. The agent has no persistent memory between runs.
- All long-term state lives in the Orders DB and the review queue.

TOOL-SIDE STATE
- fetch_order_status always reads fresh from Orders DB.
- No in-context caching of order data across steps.
- Tool responses include a fetched_at timestamp.

FORGETTING EVENTS
- Task completion: full trajectory cleared.
- Tool-call ceiling hit (5): trajectory cleared, escalation logged.
- Runtime error: trajectory cleared, incident logged.
```

Notice how short this is. Most agents do not need long-term memory, and most multi-turn agents do not need raw history retention. Ruthless minimalism here is worth more than clever storage.

---

## Anti-Pattern: Context Rot

**Symptom**: The agent behaves well at the start of a run but degrades as the trajectory lengthens. It starts contradicting earlier tool results, re-calling tools it already called, or missing details that were clearly in the context. Costs climb and decision quality drops.

**Why it hurts**: The context window is filling up with stale tool output, prior reasoning, and duplicate information. The signal-to-noise ratio gets worse with every step, and the model's attention disperses across irrelevant tokens. The bug is not "the model is bad"; the bug is "the runtime is letting the context rot."

**Fix**: Put a token budget on the trajectory and enforce it at the runtime layer. Compact earlier steps into deterministic summaries the moment the budget fills. Keep at most N full tool results and summarize the rest. If the agent still degrades, that is a signal the trajectory is too long — shorten it by splitting the work or tightening the scope.

---

## Checklist

- [ ] You have named which of the four state categories your agent uses. The ones you do not use are explicitly "none."
- [ ] Trajectory state has a token budget enforced at the runtime layer, not just hoped for in the prompt.
- [ ] Compaction is deterministic or performed by a worker model — the orchestrator never compacts its own history.
- [ ] Conversation history, if present, is summarized past a small window of recent turns.
- [ ] Long-term memory is write-gated, read-gated (with provenance), expirable, and user-editable.
- [ ] Tools always read fresh from their systems. No in-context caching of tool outputs across steps.
- [ ] Tool outputs include timestamps so the model can detect staleness.
- [ ] Forgetting events are defined and happen automatically: task completion, session end, milestone, escalation, TTL.
- [ ] A full state strategy fits on one page and is checked in with the code.

---

## What to Read Next

- [Chapter 7 — Model Selection for Agents](./07-model-selection.md): context size is a cost input; state and model selection are tightly coupled.
- [Chapter 10 — Observability from Day One](./10-observability-from-day-one.md): the audit log is where compacted state goes so you can always reconstruct what happened.
- [Chapter 13 — Cost, Rate-Limiting & Latency Budgets](./13-cost-and-kill-switches.md): the runtime enforcement layer for the trajectory budget.
- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): milestone-level forgetting for long-running agents.
