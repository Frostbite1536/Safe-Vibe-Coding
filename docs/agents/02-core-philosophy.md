---
layout: default
title: 2. Core Philosophy & Mental Model
nav_order: 2
parent: Agents Guide
grand_parent: Guides
description: "The contractor-with-a-power-tool analogy, the four pillars of safe agent design (Scope, Tool Contracts, Escalation, Observability), and why boundaries beat cleverness."
permalink: /agents/core-philosophy
---

# 2. Core Philosophy & Mental Model

If you take one idea from this guide, let it be this:

> **Agents fail not because the model is weak, but because the boundaries around what the model can do are unclear.**

You cannot fix boundary problems by picking a smarter model. You fix them the same way you fix boundary problems in any other engineering discipline: by writing the boundaries down and enforcing them with systems.

---

## The Contractor Analogy

Imagine you hire a contractor to renovate a room in your house. They are fast, skilled, and confident. They also arrive with a sledgehammer.

You would never say: *"Just figure it out, you're the expert."* You would say:

- **Scope**: "Renovate the kitchen. Do not touch the bathroom. Do not touch load-bearing walls."
- **Tool contracts**: "You can use the electrical panel, but only after calling the inspector. You can remove cabinets, but not the gas line."
- **Escalation**: "If you find asbestos, stop and call me. Do not decide on your own."
- **Observability**: "Photograph the demo each day and text me the pictures. I will check in at 5pm."

Those four sentences are not distrust. They are what makes the contractor *usable*. The same four sentences are what make an agent usable.

---

## The Four Pillars

Every design decision in the rest of this guide maps to one of these four pillars. When a chapter feels like a digression, ask which pillar it is reinforcing — there will always be one.

### Pillar 1: Scope

> *What the agent is allowed to do, and what it is never allowed to do.*

Scope is the contract between you and the agent before a single token is generated. It is written down in a one-page brief (covered in [Chapter 4](./04-defining-purpose-and-scope.md)) and referenced from the system prompt.

Scope has two halves, and most teams write only the first:

1. **Inclusions** — "Book flights on behalf of the user."
2. **Exclusions** — "Never book more than one ticket per request. Never book business class. Never book without explicit price approval."

A scope with only inclusions is an invitation for creative reinterpretation. A scope with explicit exclusions gives the agent — and the reviewer — something to push back against.

### Pillar 2: Tool Contracts

> *Precise definitions of every capability exposed to the agent.*

Tools are the only way an agent affects the world. That makes them the only place you can enforce safety in code rather than in prose. A tool contract specifies:

- The exact input schema (with types and constraints)
- The exact output schema
- Every side effect, written in English
- Who is authorized to invoke it
- What "failure" looks like

Anything you write in the system prompt as *"please do not…"* can be bypassed by a clever trajectory. Anything you write in a tool's code as `if not authorized: raise` cannot. This is covered in [Chapter 5](./05-tool-interface-design.md).

### Pillar 3: Escalation

> *The conditions under which the agent must stop and hand control back to a human.*

Silence is not safety. An agent that never asks for help is not well-behaved; it is about to do something you did not authorize.

Escalation is a **first-class success state**, not a fallback. Design it in from the beginning:

- Low confidence on the next action → escalate.
- Ambiguous input that has multiple valid interpretations → escalate.
- An action above a risk threshold (spend > $X, emails > N recipients, any `DELETE`) → escalate.
- Unexpected tool output (error, empty result, schema mismatch) → escalate.
- Any action the user explicitly marked as requiring approval → escalate.

See [Chapter 11](./11-escalation-and-hitl.md) for the full pattern.

### Pillar 4: Observability

> *Logs and traces detailed enough to reconstruct every decision the agent made.*

If you cannot explain *why* the agent took an action, you cannot debug it, audit it, or improve it. Observability is not something you add after a bad incident; it is something you wire up on day one so you can see the bad incident coming. This is Chapter 10's entire subject.

At a minimum, every run should record:

- The prompt (system + user)
- Every tool call with inputs, outputs, and latency
- The model's reasoning or rationale when available
- The final outcome, including whether the agent escalated, succeeded, or failed
- Token and dollar cost

---

## Why Boundaries Beat Cleverness

New teams often try to fix agent bugs by making the prompt cleverer. *"Just add another sentence telling it not to do that."* This works for a day, then stops working, then stops working louder.

The reason is simple: prompts are requests, not contracts. A request can be reinterpreted under adversarial inputs, long trajectories, or distribution shift. A contract enforced in code cannot.

The rule of thumb:

> **Anything that would be a bug if the agent did it should be impossible, not discouraged.**

Concretely:

| Don't say this in a prompt | Do this instead |
|:---------------------------|:----------------|
| "Never spend more than $500" | Tool rejects the call if `amount > 500` |
| "Only email internal addresses" | Tool validates `@yourcompany.com` before sending |
| "Ask before deleting" | `delete` tool requires a `confirmation_token` that only the human approval step can mint |
| "Don't read files outside the project" | Sandbox the process so it cannot |

Prose is a hint. Code is the boundary.

---

## The Failure Mode This Prevents

The most common agent incident looks like this:

1. The agent is doing its job correctly.
2. A novel input arrives — an email with an unusual attachment, a database row with a null column, a user phrasing the request oddly.
3. The model reinterprets the scope to accommodate the new input.
4. The reinterpretation calls a tool that was not supposed to be reachable from that state.
5. Something irreversible happens.
6. The post-mortem finds that the system prompt "asked" the model not to do that.

Every step of that chain is preventable by the four pillars. Scope would have named the out-of-bounds action. The tool contract would have refused the call. Escalation would have forced a human checkpoint. Observability would have surfaced the weird input before it produced the bad action.

---

## Anti-Pattern: Prompt-Only Safety

**Symptom**: The team's answer to every safety concern is *"we'll add it to the system prompt."* The prompt grows into a wall of negations.

**Why it hurts**: Prompts are persuasion, not enforcement. Long prompts also crowd out the reasoning tokens the model needs to do its actual job, and they make behavior regressions hard to isolate.

**Fix**: For every line in the prompt that starts with "never" or "always," ask: *"Could I enforce this in the tool layer or the infrastructure layer instead?"* If yes, move it. The prompt should describe the role; the code should enforce the rules.

---

## Checklist

- [ ] You can name all four pillars without looking them up.
- [ ] Every "never" in your system prompt has been audited — can it move into code?
- [ ] Your scope document lists exclusions, not just inclusions.
- [ ] Escalation is listed as a success state in your spec, not as an error.
- [ ] Observability is wired up before the first real run, not after the first real incident.

---

## What to Read Next

- [Chapter 1 — What Is an Agent?](./01-what-is-an-agent.md): if you skipped the definition, go back.
- [Chapter 3 — When to Build an Agent](./03-when-to-build-an-agent.md): sometimes the right answer is not to build one.
- [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md): the first pillar, in practice.
