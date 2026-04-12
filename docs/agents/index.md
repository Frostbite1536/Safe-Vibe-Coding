---
layout: default
title: Agents Guide
nav_order: 9
parent: Guides
has_children: true
description: "A practitioner's guide to building safe, reliable, and observable autonomous agents — written in stages, one topic at a time."
permalink: /agents
---

# Building Agents: A Practitioner's Guide

Agents feel magical but fail for mundane reasons: vague scope, untested tool contracts, no way to observe what happened, and no path to ask for help. This guide mirrors the Safe Vibe Coding philosophy — *replace trust in the model with systems that enforce correctness* — and applies it to autonomous agents.

> **Treat your agent as a contractor with a power tool**: capable and fast, but destructive without guardrails.

All twenty-six chapters are now complete. The table of contents below links to each in order, and the source of truth for the overall structure is [`AGENT_GUIDE_OUTLINE.md`](../../AGENT_GUIDE_OUTLINE.md) at the repository root, which contains the condensed workflow, anti-patterns, and checklists the full guide expands on.

---

## How to Read This Guide

- **If you are starting a new agent project**, read Part I → Part II → Part III in order.
- **If you already have an agent running**, jump to Part IV (Testing & Hardening) and Part V (Ship & Operate).
- **If you're debugging bad agent behavior**, start with Anti-Patterns and then walk back to the relevant design chapter.

---

## Table of Contents (Writing Stages)

Each item below is a planned chapter. We'll write them in order, but they can be read independently once complete.

### Part I — Foundations

1. **What Is an Agent?** — Defines the term precisely. Draws the line between a chatbot, a scripted workflow, and a true autonomous agent. Explains why the distinction matters for design and safety.

2. **Core Philosophy & Mental Model** — The "contractor with a power tool" analogy, the four pillars (Scope, Tool Contracts, Escalation, Observability), and why boundaries beat cleverness.

3. **When to Build an Agent (and When Not To)** — Decision framework for choosing an agent over a deterministic pipeline, a simple LLM call, or a human-in-the-loop tool. Includes cost, reliability, and risk trade-offs.

### Part II — Design Before You Build

4. **Defining Purpose & Scope** — How to write the one-page scope brief. What the agent *will* do, what it *will never* do, who it interacts with, and why "I can't describe what it won't do" is a red flag to stop building.

5. **Designing the Tool Interface** — Treating tools as a public API. Naming, descriptions written for LLM consumers, typed input/output schemas, declared side effects, and authorization. Why fewer precise tools beat many vague ones.

6. **System Prompts as Contracts** — Structuring the system prompt as a contract: role, invariants, decision boundaries, output format, and prohibited behaviors. How to avoid the "God Prompt" anti-pattern.

7. **Model Selection for Agents** — Picking the right model for the job: reasoning-heavy orchestrators vs. cheap fast workers, cost-per-run math, and when to mix models in a single agent.

8. **Memory & State Management** — Conversation history, scratchpads, vector stores, and long-running state. How state becomes a source of bugs and how to bound it.

### Part III — Build It Safely

9. **Building a Minimal Tool Set First** — The discipline of shipping with three tools instead of twenty. How every added tool expands attack surface, testing burden, and chained-action risk.

10. **Observability from Day One** — Trace logging, decision audit trails, cost and latency tracking, and error categorization. Why logs are not optional and what to record for every tool call.

11. **Escalation Paths & Human-in-the-Loop** — When the agent must stop and hand control back: ambiguous input, low confidence, irreversible actions, unexpected tool output. Escalation as a safety feature, not a failure.

12. **Authorization, Sandboxing & Isolation** — User-level vs. agent-level permissions, network egress controls, filesystem scoping, container isolation, and the principle of least privilege applied to agents.

13. **Cost, Rate-Limiting & Latency Budgets** — Per-run token budgets, runaway-loop detection, circuit breakers, and kill switches. How to stop an agent that has lost the plot before it burns through your API quota.

### Part IV — Test & Harden

14. **Testing Strategies** — Happy path, edge cases, boundary conditions, tool-failure tests. Building a sandbox/mock environment. Why you must not connect to production APIs until the test suite passes.

15. **Hardening Against Prompt Injection** — Treating all external content as untrusted data, separating system instructions from user content structurally, validating tool outputs before acting, and alerting on anomalous instruction patterns.

16. **Chaos & Adversarial Testing** — Deliberately breaking the agent: contradictory instructions, simulated tool failures, context exhaustion, and scope-escape attempts. Finding failure modes before production does.

17. **Evaluation Frameworks** — Golden datasets, LLM-as-judge scoring, regression suites, and the difference between "it passed my tests" and "it's actually reliable."

### Part V — Ship & Operate

18. **Deployment Patterns** — Staged rollouts, shadow mode, canary agents, and feature-flagging new tools. How to graduate an agent from sandbox to production without a cliff.

19. **Monitoring & Incident Response** — What to alert on in production, how to triage a misbehaving agent, and the kill-switch playbook. Lessons from real-world agent incidents.

20. **Multi-Agent Coordination** — Orchestrator vs. worker patterns, handoff contracts, avoiding shared mutable state, and why 90% × 90% = 81% reliability compounds badly in pipelines.

21. **Checkpoint Summaries & Capability Drift** — Documenting what the agent can (and cannot) do after each milestone. How to detect and correct drift before it becomes scope creep.

### Part VI — Reference Material

22. **Anti-Patterns & Failure Modes** — The full catalog: Tool Sprawl, The God Prompt, Over-Autonomy, Silent Failure, Testing in Production, Undocumented Scope Creep — with symptoms and fixes for each.

23. **Prompt Library for Agent Development** — Reusable prompts: system-prompt scaffolds per agent type, evaluation prompts, red-teaming prompts, debugging prompts, and inter-agent handoff templates.

24. **Documenting Agent Behavior** — Behavior specs, tool registries, decision logs, and honest "known limitations" sections. Keeping docs in sync as behavior evolves.

25. **Quick-Reference Checklists** — Before building, during development, before production, and ongoing. A one-page printable for every project.

26. **Further Reading & Tooling** — Curated external resources: papers, frameworks, eval harnesses, and community write-ups.

---

## Chapter Conventions

Every chapter in the guide follows the same shape so readers can drop in at any point:

1. Stands alone — a reader landing from a search engine should get value without reading the rest.
2. Links forward and back — references adjacent chapters where the topic connects.
3. Includes at least one concrete example, one anti-pattern, and one checklist item.
4. Ends with a "What to read next" pointer.

---

## Source Outline

The condensed version of this guide — already written — lives at [`AGENT_GUIDE_OUTLINE.md`](../../AGENT_GUIDE_OUTLINE.md) in the repository root. It contains:

- The core philosophy and four-pillar model
- A 13-step workflow covering scope, tools, prompts, observability, escalation, testing, injection defense, chaos testing, prompt libraries, documentation, multi-agent coordination, and checkpointing
- Six named anti-patterns with symptoms and fixes
- A four-phase checklist (before building, during development, before production, ongoing)

Use it as the skeleton. The chapters in this directory are the flesh.
