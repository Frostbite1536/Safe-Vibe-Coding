---
layout: default
title: 3. When to Build an Agent (and When Not To)
nav_order: 3
parent: Agents Guide
grand_parent: Guides
description: "A decision framework for choosing an agent over a deterministic pipeline, a simple LLM call, or a human-in-the-loop tool. Covers the cost, reliability, and risk trade-offs that should decide for you."
permalink: /agents/when-to-build
---

# 3. When to Build an Agent (and When Not To)

The best agent is the one you did not build.

That sounds flippant, but it is the single piece of advice most teams wish they had taken earlier. Agents are the most expensive, least reliable, and hardest-to-test way to solve most problems. They justify that cost in exactly one situation: when nothing simpler will work. This chapter gives you a framework to find out whether you are in that situation — *before* you commit to the design work in the rest of the guide.

---

## The Ladder of Alternatives

Before building an agent, walk up this ladder. Stop at the first rung that solves your problem.

1. **A script.** Deterministic code. Zero LLM calls. If the task can be expressed as a flowchart, it should be a flowchart.
2. **A script with one LLM call.** The LLM classifies, extracts, or rewrites one thing. The rest is code. This handles more cases than people expect.
3. **A script with a chain of LLM calls.** A fixed pipeline: extract → validate → summarize → route. Each step is an LLM call, but the sequence is hard-coded. No model decides what to do next.
4. **A retrieval-augmented chatbot (human in the loop).** The user drives each turn. The LLM answers over fetched context. The human decides when they are done.
5. **A tool-calling assistant (human in the loop).** Same as above, but the LLM can call tools. The human still decides whether to call each one, or approves before the tool runs.
6. **An agent.** The LLM drives the loop. You stopped being able to stay on rung 5 because the user's task requires more than ~3 tool calls and the user is not willing to approve each one.

Rungs 1–5 are cheaper, more reliable, and radically easier to test than rung 6. Most of the projects that get labeled "agent" belong on rungs 3–5 and are suffering because their builders skipped the ladder.

---

## The "Should I Build an Agent?" Test

Answer every question honestly. If you cannot answer *yes* to all of them, do not build an agent yet.

### 1. Is the task beyond a fixed pipeline?

The task must involve **branching decisions the designer cannot enumerate**. If you can draw the decision tree on a whiteboard, it is a pipeline, not an agent. Pipelines are better at pipelined work.

Good sign: *"The next action depends on what the previous tool returned, and the space of returns is open-ended."*
Bad sign: *"There are three possible paths and I can describe all of them."*

### 2. Is the cost of a wrong action bounded?

Agents make wrong actions. Before you build one, you must know the worst thing a wrong action can do. If the answer is *"irreversibly delete production data"* or *"send money to the wrong account with no clawback,"* the agent needs to be wrapped in so much approval machinery that you might as well use rung 5.

A bounded failure surface is not optional. It is what makes safe iteration possible.

### 3. Can you observe the agent cheaply?

Agents are only debuggable with full trace logs. If your infrastructure cannot store and search those logs — per-run reasoning, per-tool-call inputs and outputs, per-decision metadata — you are not ready for rung 6. [Chapter 10](./10-observability-from-day-one.md) covers the minimum bar.

### 4. Is there a human in the loop somewhere?

"Somewhere" can mean before (approval), during (escalation), or after (review). Fully unattended agents are a small minority of real deployments. If you cannot name the human and the checkpoint, you do not yet have a design.

### 5. Is the payoff big enough to justify the overhead?

Building a safe agent is expensive: scope docs, tool contracts, observability, a sandbox, an eval harness, incident response. If the task is run ten times a week and a human could do it in five minutes, a pipeline is almost certainly cheaper all-in.

A good rule of thumb:

> *An agent is justified when the cost of the design work is less than the cost of humans solving the long tail of the problem by hand.*

---

## Reliability Math

It helps to put rough numbers on why agents are hard before you commit. Assume each tool-calling decision is ~95% reliable — a generous assumption for a well-tuned agent on a well-scoped task. Then:

| Trajectory length | End-to-end reliability |
|:------------------|:-----------------------|
| 1 step            | 95%                    |
| 3 steps           | 86%                    |
| 5 steps           | 77%                    |
| 10 steps          | 60%                    |
| 20 steps          | 36%                    |

Every additional step compounds. Two consequences:

1. **Short trajectories are much safer than long ones.** Design agents that take 3–5 steps, not 15–20. If a task needs 15 steps, break it into three tasks of 5 steps with explicit handoffs.
2. **Evaluation is harder than you think.** At 77% trajectory reliability, you need hundreds of runs to tell a real regression from noise. Plan for that in [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md).

If your task requires 30-step trajectories with ≥99% end-to-end reliability, an agent is probably the wrong tool entirely.

---

## A Worked Example

Task: *"When a customer emails us asking about order status, look it up and reply."*

**Option A — Pipeline (rung 3):**
```
classify(email) → if order_status_question:
    extract(order_id) → lookup(order_id) → draft_reply(order, email) → human_approve → send
```
This is four LLM calls and one tool call in a fixed order. It is deterministic, testable, cheap, and catches ~90% of the real traffic. Build this first.

**Option B — Agent (rung 6):**
An agent that can call `classify`, `extract_order_id`, `lookup_order`, `search_docs`, `draft_reply`, `send_email`, and chooses its own sequence. It handles edge cases Option A misses — multi-order emails, typos, customers asking about returns and status in the same message.

When is Option B worth it? When the long tail of edge cases Option A punts to humans is expensive *and* the cost of a wrong automated reply is small (customers can write back; nothing irreversible happens). When the reply could move money or close accounts, stay on Option A and route the edge cases to humans.

The question is never *"can we build it as an agent?"* It is *"does the edge-case coverage justify the reliability hit and the operational cost?"*

---

## Anti-Pattern: Agent as a Résumé Line

**Symptom**: The team decided to build an agent because "agents are the new thing" and the project exists as a showcase. The business requirement is never actually stated.

**Why it hurts**: You will end up with rung-6 machinery solving a rung-3 problem, with all of the cost and none of the edge-case coverage that would have justified it.

**Fix**: Write the business problem in one sentence *before* writing anything else. Then walk the ladder. If a lower rung would have worked, use it — you can always graduate later.

---

## When to Definitely *Not* Build an Agent

There are a few situations where the answer is simply no:

- **The task is safety-critical and failure is irreversible.** Medical dosing, legal filings, money movement without human approval. Use humans, use rung 5 at most.
- **The task is already solved by a deterministic system.** Do not replace working `cron` jobs with agents.
- **The task has a hard reliability SLO above ~95% end-to-end.** The math above shows you cannot get there with a meaningful trajectory length.
- **You have no observability infrastructure.** You will be flying blind, and agents fail silently when you are flying blind.
- **You cannot describe what the agent must *not* do.** If you cannot name the exclusions, you do not yet have a scope, and without a scope you cannot design the tool contracts.

---

## Checklist

- [ ] You walked the ladder of alternatives and explicitly rejected each lower rung with a reason.
- [ ] You can state, in one sentence, the business problem the agent solves.
- [ ] You can state, in one sentence, the worst thing the agent could do if it went wrong.
- [ ] The worst thing is bounded — you can recover from it without a crisis.
- [ ] You have a reliability target that is compatible with the trajectory length you need.
- [ ] You have (or are about to build) observability infrastructure sufficient to debug a misbehaving agent.
- [ ] You have identified the human in the loop and the checkpoints they own.

---

## What to Read Next

If you answered yes to every question above, proceed to Part II:

- [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md): write the one-page brief that becomes your agent's constitution.

If you answered no to any of them, go back a rung. The rest of this guide will still be useful — scope, tool design, and observability apply to pipelines and tool-calling assistants too — but you will save yourself weeks by not treating a pipeline problem as an agent problem.
