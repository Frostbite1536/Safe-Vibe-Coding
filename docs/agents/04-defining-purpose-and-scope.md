---
layout: default
title: 4. Defining Purpose & Scope
nav_order: 4
parent: Agents Guide
description: "How to write the one-page scope brief that becomes your agent's constitution. What the agent will do, what it will never do, who it interacts with, and why 'I can't describe what it won't do' is a red flag to stop building."
permalink: /agents/purpose-and-scope
---

# 4. Defining Purpose & Scope

Every agent that has ever failed in production had a clear reason to fail, and it was almost never "the model was not smart enough." It was "nobody wrote down what the agent was for."

Before you design tools, before you pick a model, before you draft a system prompt — you write the scope. It is one page. It takes an afternoon. It is the cheapest and most important artifact in the entire project.

---

## The One-Page Scope Brief

The scope brief is a single document, stored in version control, that answers seven questions. When the document is complete, the rest of the guide gives you the mechanics to enforce it. When it is not complete, every later decision is a guess.

### 1. Purpose — *What problem does this agent solve?*

One sentence. If you cannot compress it to one sentence, you are describing a product, not an agent.

> *"Respond to customer emails about order status by looking up the order and drafting a reply for human review."*

Not:

> *"Handle customer service end-to-end using AI to improve response times across multiple channels while maintaining brand voice and escalating when appropriate."*

The first sentence tells you what to build. The second tells you someone has not made a decision yet.

### 2. Inclusions — *What is the agent allowed to do?*

A bulleted list of actions. Each bullet is narrow and verbable. Future-you will be tempted to add to this list when a user asks for "just one more thing." Resist.

> - Read incoming customer emails from the `support@` inbox.
> - Look up orders by email address or order number.
> - Draft a reply summarizing order status.
> - Post the draft into the review queue.

That's it. Four bullets. If the list needs ten, the agent is probably two agents.

### 3. Exclusions — *What is the agent forbidden from doing?*

This is the half of the brief most teams skip, and it is the half that matters.

Exclusions are not hypothetical. Each one should correspond to an action the agent *could plausibly take* and the reason it *must not*.

> - **Never send an email directly.** All drafts go to the review queue.
> - **Never refund, cancel, or modify an order.** Escalate to a human.
> - **Never share order details with anyone whose email does not match the order's customer email.** This is a data-protection rule.
> - **Never access orders older than 90 days.** Older data is archived and subject to different retention rules.
> - **Never answer questions that are not about order status.** Escalate them.

Good exclusions read like a list of near-misses. If you cannot write five of them, you have not thought hard enough about how the agent could go wrong.

> **Red flag**: If you cannot describe what the agent *won't* do, you don't know enough to build it yet. Stop and go talk to whoever owns the business process.

### 4. Stakeholders — *Who or what does it interact with?*

List every actor the agent touches. For each, note whether the interaction is read, write, or both.

> - **Customers** (read — incoming email; no direct write)
> - **Order database** (read only)
> - **Review queue** (write only — drafts)
> - **Support agents** (write only — they own the human checkpoint)
> - **Audit log** (write only)

This list is where most authorization bugs are born. If a stakeholder is missing from the brief, the tool contract will probably forget to check their permissions.

### 5. Success criteria — *How do you know the agent worked?*

A run is successful when you can answer *yes* to all of these. Be concrete; "the user was happy" is not concrete.

> - A draft was posted to the review queue within 60 seconds of the inbound email.
> - The draft contains the correct order number, status, and estimated delivery date.
> - The draft does not include any customer data from a different order.
> - The audit log records the tools called and their inputs and outputs.

These criteria become your eval set in [Chapter 17](./17-evaluation-frameworks.md). Write them now so you do not have to reverse-engineer them later.

### 6. Failure criteria — *How do you know it didn't?*

Explicit failure modes. The agent should *know* it has failed when one of these occurs and should escalate instead of guessing.

> - The order lookup returned nothing.
> - The customer email does not match any order's customer email.
> - The draft would contain information outside the scope of the question.
> - Any tool call returned an unexpected error or malformed response.
> - The agent took more than 5 tool calls (the task should never need more).

Failure criteria are also escalation criteria — see [Chapter 11](./11-escalation-and-hitl.md).

### 7. Out-of-scope but tempting — *What might people ask for next?*

This is the "future features" section, and its purpose is the opposite of what you might think. It exists so you can say *"that was explicitly out of scope in the original brief"* when the scope creep pressure arrives. Name the things you already considered and chose not to do.

> - Processing refund requests. *(Out of scope — legal and financial exposure.)*
> - Handling non-English email. *(Out of scope — translation quality not yet validated.)*
> - Auto-sending replies without human review. *(Out of scope — reputational risk too high.)*
> - Answering product questions. *(Out of scope — different agent if we ever build it.)*

Naming these in advance protects the scope from well-meaning *"can't we just…"* conversations.

---

## Where the Scope Brief Lives

Commit the brief to the repository alongside the agent's code. Treat changes to it the way you treat changes to a database schema: reviewed, deliberate, with a changelog.

Two rules keep it honest:

1. **The system prompt must quote from the brief, not paraphrase it.** When you change the brief, the prompt changes with it. See [Chapter 6](./06-system-prompts-as-contracts.md).
2. **The eval set must reference the brief.** Every success criterion becomes at least one eval case. Every failure criterion becomes an escalation case.

---

## A Warning About Scope Drift

Scope drift is the second-most-common cause of agent incidents (after prompt injection). It almost never happens in a single step — it happens across a dozen small concessions, each of which seemed reasonable at the time:

> *"The user asked for order status and also asked about a refund, so I wrote a paragraph about refunds."*
> *"The customer emailed from a different address, so I matched on name instead."*
> *"There wasn't an order, so I drafted a general apology."*

Each of those is a scope violation dressed up as helpfulness. The defense is a scope brief the agent is literally unable to violate — exclusions enforced in code (Chapter 5), escalation triggered on failure criteria (Chapter 11), and audit logs that make drift visible (Chapter 10).

See also the [Undocumented Scope Creep anti-pattern](./22-anti-patterns.md#undocumented-scope-creep) in Chapter 22.

---

## Example: A Complete Scope Brief

Here is what a real brief looks like, compressed to one page. Copy the shape, not the details.

```text
AGENT: Support Triage Drafter
OWNER: Support Engineering
VERSION: 1.2 — 2026-03-15

PURPOSE
Respond to customer emails about order status by looking up the order
and drafting a reply for human review.

INCLUDES
- Read incoming email from support@
- Classify as order-status question (or not)
- Look up order by email or order number
- Draft a reply with status, tracking, and ETA
- Post to the review queue

EXCLUDES
- Direct email send (drafts only; humans send)
- Any refund, cancellation, or order modification
- Sharing data across customers
- Orders older than 90 days
- Any topic other than order status (escalate)

STAKEHOLDERS
- Customers (read: email; no direct write)
- Orders DB (read-only)
- Review queue (write: drafts)
- Support reps (write: they send)
- Audit log (write: append-only)

SUCCESS CRITERIA
- Draft posted within 60s of inbound email
- Correct order, status, ETA
- No cross-customer data
- Audit trail complete

FAILURE CRITERIA (→ escalate)
- Order lookup empty or ambiguous
- Customer email does not match order
- Question is not about order status
- Any tool error or malformed response
- More than 5 tool calls needed

OUT-OF-SCOPE BUT TEMPTING
- Refund processing (legal/financial exposure)
- Non-English email (translation not validated)
- Auto-send (reputational risk)
- Product questions (separate agent if ever)
```

That is the entire brief. Everything in Parts II–V of this guide is about implementing it faithfully.

---

## Anti-Pattern: The Vague Mission Statement

**Symptom**: The scope document reads like a product brochure. Phrases include *"delight customers,"* *"optimize workflows,"* *"leverage AI to…"*. There are no explicit exclusions.

**Why it hurts**: Vague language gives the model permission to interpret the role however the next input suggests. Every novel user message becomes a small scope negotiation, and the agent loses every one of them on the side of "try to be helpful."

**Fix**: Replace every abstract noun with a concrete action. *"Delight customers"* becomes *"post a draft reply to the review queue within 60 seconds."* *"Optimize workflows"* becomes *"reduce the number of tickets a human reads end-to-end by classifying and drafting."* If a phrase cannot be made concrete, delete it — it was never a scope item.

---

## Checklist

- [ ] The scope brief fits on one page.
- [ ] Purpose is one sentence.
- [ ] Inclusions and exclusions are both present, and exclusions are at least as long as inclusions.
- [ ] You can name the worst thing the agent could do and the brief forbids it explicitly.
- [ ] Success criteria are objective enough to evaluate automatically.
- [ ] Failure criteria are mapped to escalation paths.
- [ ] The brief is in version control, with an owner and a version number.
- [ ] The system prompt will quote from the brief verbatim — not paraphrase it.

---

## What to Read Next

- [Chapter 5 — Designing the Tool Interface](./05-tool-interface-design.md): turn the inclusions and exclusions into tool contracts the model cannot violate.
- [Chapter 6 — System Prompts as Contracts](./06-system-prompts-as-contracts.md): embed the brief into the agent's operating manual.
- [Chapter 11 — Escalation Paths](./11-escalation-and-hitl.md): wire the failure criteria into real escalation behavior.
