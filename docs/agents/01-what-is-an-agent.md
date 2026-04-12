---
layout: default
title: 1. What Is an Agent?
nav_order: 1
parent: Agents Guide
description: "Defines the term precisely. Draws the line between a chatbot, a scripted LLM workflow, and a true autonomous agent, and explains why the distinction matters for design and safety."
permalink: /agents/what-is-an-agent
---

# 1. What Is an Agent?

"Agent" is the most overloaded word in applied AI. A vendor calls their chatbot an agent. A startup calls their retrieval pipeline an agent. A researcher calls a multi-step LLM loop an agent. They are not the same system, and they do not have the same failure modes.

Before you can build one safely, you need a definition sharp enough to design against.

---

## A Working Definition

> **An agent is a system in which an LLM decides, on its own, which tool to call next — and keeps doing so until it believes the task is complete.**

Three things have to be true:

1. **The LLM is in the control loop.** It is not just generating text; it is choosing the next action from a set of options.
2. **The actions affect the world.** Tools read from or write to real systems — databases, APIs, filesystems, other services.
3. **The loop continues until the model stops it.** There is no pre-scripted sequence of steps. The model decides when it is done.

If any of those three is missing, you have something simpler — which is usually good news, because simpler systems fail in simpler ways.

---

## The Spectrum

It helps to place agents on a spectrum of autonomy, from *least* to *most*:

| Level | Name                    | LLM's Job                                   | Example                                           |
|:------|:------------------------|:--------------------------------------------|:--------------------------------------------------|
| 0     | **Prompt**              | Produce text                                 | "Summarize this article."                         |
| 1     | **Retrieval-Augmented** | Produce text over fetched context            | A RAG chatbot that cites docs                     |
| 2     | **Scripted Workflow**   | Fill slots in a fixed pipeline               | Extract → classify → route an email               |
| 3     | **Tool-Calling LLM**    | Choose one tool per turn, human drives loop  | A chat assistant that can run a `search_web` tool |
| 4     | **Agent**               | Choose tools in a loop, model drives loop    | "Book me a flight under $400 with a morning leg." |
| 5     | **Multi-Agent System**  | Orchestrate other agents                     | A planner agent that delegates to worker agents   |

Levels 0–3 are **not agents** in the sense this guide uses the word. They are important and widely deployed — and most of them should stay that way. An agent is what you build when the other four levels cannot solve your problem.

---

## What Makes Agents Different (And Dangerous)

A scripted workflow fails in predictable places — the places you put the `try/except`. An agent fails in places nobody drew on a whiteboard, because the sequence of actions was chosen by the model at runtime.

Three properties follow from that:

### 1. The action space is the product of the tool set

If an agent has 5 tools, each taking 3 parameters with ~10 reasonable values, the space of possible single actions is ~150. Over a 10-step trajectory that is ~10¹⁰ possible paths. You cannot test them all. You can only constrain them.

### 2. Failures chain

A 95%-reliable single step is fine. A trajectory of 10 such steps is ~60% reliable. Agents amplify small flaws into visible ones. This is covered in depth in [Chapter 20 — Multi-Agent Coordination](./20-multi-agent-coordination.md).

### 3. There is no "completed" signal from outside

A scripted workflow ends when the script runs out of steps. An agent ends when the *model* decides it is done — which may be early (silent failure) or late (runaway loop). Both are bugs, and both need infrastructure to catch. See [Chapter 13 — Cost, Rate-Limiting & Latency Budgets](./13-cost-and-kill-switches.md).

---

## A Concrete Example

Consider the task: *"Find the three most cited papers on retrieval-augmented generation published in 2024 and email me a summary."*

Here is how each level handles it:

- **Level 1 (RAG chatbot)**: Cannot do it. It has no way to fetch new papers or send email.
- **Level 2 (scripted workflow)**: Works if you wrote a pipeline `search_papers → rank_by_citations → summarize → send_email`. Fails if the user asks for "published in 2024 *or* early 2025" — the script has no step for that.
- **Level 3 (tool-calling LLM)**: A human asks follow-ups in chat and approves each step. The LLM calls `search_papers`, shows results, user says "summarize these three", LLM calls `summarize`, user says "email it", LLM calls `send_email`.
- **Level 4 (agent)**: The user gives the prompt once. The agent calls `search_papers`, inspects the results, decides it needs to call `get_citation_count`, ranks, calls `summarize`, calls `send_email`, and returns. No human in the loop.

Notice what changed between Level 3 and Level 4: **the human stopped being the loop controller**. That single change is what separates "LLM with tools" from "agent." It is also what turns every bug into a production incident instead of a conversation.

---

## Anti-Pattern: Calling Everything an Agent

**Symptom**: The team describes a simple RAG chatbot, a fixed workflow, and a true autonomous loop all as "our agent." Design conversations conflate their requirements.

**Why it hurts**: The three systems have different testing needs, different observability needs, and different failure modes. Treating them as one category means you either over-engineer the simple ones or under-engineer the complex one.

**Fix**: Pin every project to one row in the spectrum table above. If someone says "our agent," the next question is *"which level?"* — and the answer gets written into the scope document from [Chapter 4](./04-defining-purpose-and-scope.md).

---

## Checklist

- [ ] You can state, in one sentence, which row of the autonomy spectrum your system lives on.
- [ ] If the answer is Level 4 or 5, you have accepted that the design work in Parts II–V of this guide is non-optional.
- [ ] If the answer is Level 0–3, you have asked whether your problem actually requires going higher.
- [ ] Everyone on the team uses the same definition of "agent" in design discussions.

---

## What to Read Next

- [Chapter 2 — Core Philosophy & Mental Model](./02-core-philosophy.md): the four pillars that make agents safe to build.
- [Chapter 3 — When to Build an Agent](./03-when-to-build-an-agent.md): a decision framework for staying at a lower level when you can.
