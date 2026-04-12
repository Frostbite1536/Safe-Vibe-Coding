---
layout: default
title: 7. Model Selection for Agents
nav_order: 7
parent: Agents Guide
description: "Picking the right model for the job. Reasoning-heavy orchestrators versus cheap fast workers, cost-per-run math, latency budgets, and when to mix models inside a single agent."
permalink: /agents/model-selection
---

# 7. Model Selection for Agents

"Which model should I use?" is the question most teams ask first, and it is almost never the question they should answer first. Model selection is a *consequence* of the scope brief, the tool set, and the trajectory length — not a starting point.

But once the earlier chapters have given you a real design, model selection matters. The wrong pick can turn a working agent into a slow one, an unaffordable one, or a subtly unreliable one. This chapter gives you the framework to choose deliberately.

---

## Four Axes That Actually Matter

Forget the leaderboards. For agent work, only four axes matter.

### 1. Reasoning quality under tool use

The hardest thing an agent model does is *decide which tool to call next, given a partially completed trajectory*. That is a different skill from scoring well on a benchmark; it is the ability to:

- Read a dense tool-call transcript without losing track.
- Recover gracefully from a tool error and pick a different path.
- Refuse to hallucinate a tool that does not exist in the schema.
- Stop when the task is done, rather than calling one more tool "just in case."

Some models do this well and some do not — and the ordering does not always match "smartest model on MMLU." Test this yourself on a small eval set. Do not trust marketing.

### 2. Latency per decision

An agent that takes 30 seconds per tool-call decision and runs 8 steps is a 4-minute interaction. That might be fine for a background job and intolerable for a user-facing chatbot. Measure latency under your realistic prompt length and tool count, not under a toy benchmark.

Two latency numbers to track:

- **Time-to-first-token**: how long before the model starts responding. Dominates interactive feel.
- **Time-to-decision**: total wall-clock time from request to completed tool-call decision. Dominates throughput for autonomous agents.

### 3. Cost per run (not per token)

Per-token prices are a lie that sounds like an answer. What you actually pay is:

> `cost_per_run ≈ (input_tokens_per_step × input_price + output_tokens_per_step × output_price) × avg_steps_per_run`

And `input_tokens_per_step` grows as the trajectory grows, because every new tool result gets added to the context for the next step. A 10-step trajectory can easily use 5–10× more tokens than a 1-step call on the same base prompt.

Always compute cost *per completed task*, on your real workload, before committing. Not per million tokens.

### 4. Instruction-following fidelity

Some models will follow the contract prompt from [Chapter 6](./06-system-prompts-as-contracts.md) closely; others will drift when the user message pushes against it. Drift shows up as:

- Calling a tool the prompt told the agent to avoid.
- Answering a question outside the scope when the user asks nicely.
- Producing output in a format other than the one the prompt specified.

Instruction-following is not the same as raw intelligence. A smaller model with strict instruction-following is often a better agent than a bigger model that creatively reinterprets its role.

---

## The Orchestrator / Worker Split

The single most useful design idea in model selection is *you do not have to pick one model*. Agents can — and often should — use different models for different roles in the same run.

### Orchestrator

The orchestrator holds the overall goal, chooses which tool to call next, and decides when the task is done. It reads the full trajectory on every step. It is the seat of the reasoning load.

- **Wants**: strong reasoning under tool use, strong instruction-following, ability to track a long context.
- **Tolerates**: higher per-token cost, because it is invoked relatively few times per run.
- **Good fit**: the best reasoning model you can afford, constrained to the minimum context window you actually need.

### Worker

Workers are called by the orchestrator (or by tools) to do narrow, well-defined subtasks — summarizing a document, extracting structured data, classifying a message, generating a draft reply.

- **Wants**: speed, low cost, strong single-call instruction-following, structured output fidelity.
- **Tolerates**: smaller context windows, weaker multi-step reasoning (because there is no multi-step work).
- **Good fit**: a fast, cheap model that excels at one-shot structured tasks.

### The pattern in practice

> *An email triage agent uses a frontier model as the orchestrator. When the orchestrator needs to classify an email or generate a draft, it calls a tool that invokes a cheaper fast model behind the scenes. The orchestrator sees the tool, not the model underneath.*

The worker shows up to the orchestrator as just another tool. The orchestrator never knows — and should not know — whether the tool is backed by a model, a SQL query, or a hand-written function. That separation is what makes the split safe to refactor later.

---

## Doing the Cost Math

Before you commit to a model, do the cost math for a realistic run on a whiteboard. Here is a worked example for the Support Triage Drafter from earlier chapters:

Assume:

- System prompt: ~400 tokens
- Scope brief excerpts in context: ~200 tokens
- Tool schemas: ~600 tokens
- Average user email: ~300 tokens
- Average tool output (order lookup): ~200 tokens
- Average draft reply: ~250 tokens
- Average trajectory: 3 tool calls + 1 final draft = 4 model turns

Context grows with each step:

| Turn | Input tokens                       | Output tokens |
|:-----|:-----------------------------------|:--------------|
| 1    | 1500 (sys + tools + email)          | 80 (tool call) |
| 2    | 1780 (prev + tool result)           | 80 (tool call) |
| 3    | 2060 (prev + tool result)           | 80 (tool call) |
| 4    | 2340 (prev + tool result)           | 250 (draft)    |

Totals: ~7680 input tokens, ~490 output tokens per run.

Plug that into two price points:

| Model class | Input $/Mtok | Output $/Mtok | Cost per run |
|:------------|-------------:|--------------:|-------------:|
| Frontier    | $3.00        | $15.00        | $0.030       |
| Mid-tier    | $1.00        | $5.00         | $0.010       |
| Fast/cheap  | $0.25        | $1.25         | $0.0025      |

Scaled to 10,000 runs per day:

| Model class | Daily cost | Monthly cost |
|:------------|-----------:|-------------:|
| Frontier    | $300       | $9,000       |
| Mid-tier    | $100       | $3,000       |
| Fast/cheap  | $25        | $750         |

Two observations:

1. **The gap between tiers is not small.** Picking the frontier model "to be safe" can be a 12× cost premium. Do not pay that premium unless you have evidence — from a real eval, not a hunch — that the cheaper model fails on your task.
2. **Trajectory length dominates.** If the average run grows from 3 tool calls to 8, your cost roughly doubles. Shrinking trajectories is one of the highest-leverage optimizations available. Do that before shopping for cheaper models.

---

## When to Mix Models

Mix models when the orchestrator / worker split gives you a clean cost or latency win *without* compromising the critical-path reasoning.

Good candidates for worker-tier models:

- Summarizing a long document into a 5-sentence abstract.
- Classifying an email into one of a fixed set of categories.
- Extracting structured fields from free-form text.
- Rewriting a draft into a specific tone or format.
- Generating a short response given a fully specified template.

Keep the orchestrator on the better model when:

- The decision *about which tool to call* is non-trivial and depends on the entire trajectory.
- The agent must recover from tool errors by trying a different approach.
- Escalation decisions depend on nuanced reading of the user's intent.

A useful heuristic: **the orchestrator reads the whole trajectory; workers read one thing**. If a subtask can be framed as "read this one thing and produce one structured output," it is a worker task.

---

## Latency Budgets

Model choice is also about wall-clock behavior. Before selecting, set a latency budget per interaction type:

| Interaction       | Budget for end-to-end response |
|:------------------|:-------------------------------|
| User-facing chat  | < 2 seconds to first token, < 8 seconds to completion |
| Synchronous API   | < 5 seconds                    |
| Background job    | < 60 seconds                   |
| Scheduled batch   | Minutes are fine               |

Now measure the candidate model against that budget *with your real prompt length and trajectory*. The model that wins a leaderboard with 200-token prompts may not win with 2,000-token prompts and 8-step trajectories. Test this once and you will save yourself a painful post-launch migration.

When the budget is tight, two knobs are more effective than switching models:

1. **Shrink the trajectory.** Fewer tool calls is the biggest latency lever you have.
2. **Parallelize independent tool calls.** If two tools can run at the same time, do it — the model may support parallel tool use, and the runtime certainly does.

---

## Anti-Pattern: Model Mismatch

**Symptom**: Either (a) a cheap model is used as the orchestrator for a reasoning-heavy task, producing flaky decisions and long retry loops; or (b) a frontier model is used for trivial classification work, burning budget on overkill.

**Why it hurts**: (a) costs reliability; (b) costs money. Both look "fine" in small-scale testing and fall apart under load.

**Fix**: Split the work. Put the orchestrator on the best model you can justify with an eval score. Put the workers on the cheapest model that passes their one-shot benchmarks. Measure cost-per-completed-task on a realistic workload and adjust. Do not pay a frontier premium for summary-writing; do not pay reliability costs on strategic decisions.

---

## Checklist

- [ ] You have picked a model based on an eval score on *your* task, not a leaderboard.
- [ ] You have measured latency under realistic prompt length and trajectory depth.
- [ ] You have computed cost-per-completed-task on a realistic workload, not cost-per-million-tokens.
- [ ] You have identified which subtasks (if any) can be delegated to cheaper worker models.
- [ ] The orchestrator's model was chosen for tool-use reasoning, not for chat benchmark scores.
- [ ] Worker models were chosen for single-shot structured output quality.
- [ ] Latency budgets for each interaction type are documented.
- [ ] You have a plan to re-evaluate the choice as cheaper models improve — model selection is not a one-time decision.

---

## What to Read Next

- [Chapter 8 — Memory & State Management](./08-memory-and-state.md): shorter context = cheaper runs, so context bounds are also a cost decision.
- [Chapter 13 — Cost, Rate-Limiting & Latency Budgets](./13-cost-and-kill-switches.md): enforcing the budgets from this chapter at runtime.
- [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md): how to build the eval that lets you compare models without guessing.
- [Chapter 20 — Multi-Agent Coordination](./20-multi-agent-coordination.md): the orchestrator/worker split generalizes into multi-agent territory.
