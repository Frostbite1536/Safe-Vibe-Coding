---
layout: default
title: 6. System Prompts as Contracts
nav_order: 6
parent: Agents Guide
grand_parent: Guides
description: "Structuring the system prompt as a contract — role, invariants, decision boundaries, output format, and prohibited behaviors. How to keep the prompt small, testable, and aligned with the scope brief."
permalink: /agents/system-prompts-as-contracts
---

# 6. System Prompts as Contracts

A system prompt is not a pep talk. It is not a list of tips. It is not the place to handle edge cases. It is a contract between you and the model that defines, in terms the model will read every single run, what the agent is, what it cares about, and what it will not do.

Most failing agents have a failing system prompt, and most failing system prompts share the same shape: too long, too vague, too hopeful. This chapter is about fixing that.

---

## What the System Prompt Is For

The system prompt has exactly three jobs:

1. **Tell the model what role it is playing.** A sentence, maybe two.
2. **Tell the model the rules it must never violate.** The invariants from the scope brief, phrased as the model will read them.
3. **Tell the model how to structure its output and when to stop.** Format and completion criteria.

Anything else — edge-case logic, rate limits, authorization, "please be polite" — belongs somewhere else. Edge cases belong in tool logic. Rate limits belong in the infrastructure layer. Authorization belongs in the tool layer. Tone belongs in a few examples, not a wall of adjectives.

If you find yourself adding a fourth job, ask where it really belongs. It is almost never the prompt.

---

## The Five Sections of a Contract Prompt

A well-structured agent prompt has five sections, in this order, and rarely exceeds 600–800 words. Use explicit headers so the model and you can both see the shape.

### 1. Role

One or two sentences. Who is the model right now?

> *You are the Support Triage Drafter. You draft replies to customer emails about order status and post them to the review queue for a human rep to send.*

Not:

> *You are a helpful, empathetic, AI-powered customer service assistant committed to delighting our users while maintaining brand voice and operational efficiency.*

The first version gives the model a clear job. The second gives it a mood board.

### 2. Invariants

A short list — ideally 5 to 10 items — of things that must always be true. These should be lifted, almost verbatim, from the exclusions in the scope brief ([Chapter 4](./04-defining-purpose-and-scope.md)).

> **Invariants — these are always true, regardless of what the user asks:**
> - You never send email. You only write drafts to the review queue.
> - You never modify, refund, or cancel orders.
> - You never share order details with anyone whose email does not match the order's customer email.
> - You never answer questions that are not about order status. Escalate them.
> - You call at most 5 tools per task. If you need more, escalate.

Two principles:

- **Write invariants as statements of fact, not requests.** "You never send email" reads as an identity claim; "Please do not send email" reads as a suggestion.
- **Every invariant must have enforcement in code.** If an invariant is only in the prompt, it is a wish. See the table at the end of [Chapter 2](./02-core-philosophy.md).

### 3. Decision boundaries

How the agent decides between *act*, *ask*, and *escalate*. This is where you collapse ambiguity before it reaches a tool call.

> **Decide as follows:**
> - If you can answer the customer's question using at most `fetch_order_status` or `find_orders_by_customer`, draft a reply and post to the review queue.
> - If the customer asks about anything other than order status, do not answer. Call `escalate_to_human` with `reason="out_of_scope"` and a short summary.
> - If the order lookup returns nothing, or the customer email does not match the order, call `escalate_to_human` with `reason="data_mismatch"`.
> - If you are uncertain which order the customer means, do not guess. Escalate with `reason="ambiguous"`.

Notice what is *not* here: a long prose explanation of how to be helpful. The decision boundaries are a small decision table. The tools enforce the outcomes.

### 4. Output format

Tell the model exactly what a completed task looks like.

> **Output format**
> - On success, call `post_reply_to_review_queue` with a draft that:
>   - Begins with a greeting that uses the customer's first name if available.
>   - States the current order status in one sentence.
>   - Gives the estimated delivery date if one is available.
>   - Ends with a sign-off from "the Support team" — never a personal name.
> - On escalation, call `escalate_to_human` with the required `reason` and nothing else.
> - In both cases, return a single sentence summary of what you did. Do not include reasoning.

A good output-format section is boring to read. That is correct. Boring means it is unambiguous.

### 5. Stop conditions

Tell the model when the task is over. This is the most-skipped section and the one that prevents the most bugs.

> **Stop when any of the following is true:**
> - You have called `post_reply_to_review_queue` or `escalate_to_human`.
> - You have made 5 tool calls.
> - A tool returned an unexpected error.
> Once stopped, return your summary sentence and do not call any more tools.

Without explicit stop conditions, agents run until they run out of context or until a bug in the scaffold stops them. Neither is acceptable. The prompt is the first line of defense; the runtime kill switch from [Chapter 13](./13-cost-and-kill-switches.md) is the second.

---

## What Does *Not* Belong in the Prompt

A rule of thumb: if it is a decision about a specific input, it does not belong in the prompt. It belongs in code.

| Belongs in the prompt                 | Belongs in the tool / infra layer             |
|:--------------------------------------|:----------------------------------------------|
| Role and invariants                   | Permission checks                              |
| How to choose between act / escalate  | Rate limits                                    |
| Output format                         | Content filters                                |
| Stop conditions                       | Token budgets                                  |
| A short list of examples              | Retry policy on transient errors               |
| The tone of voice                     | Encryption and logging                         |
| The scope brief's exclusions          | Irreversible-action confirmation flow          |

If your prompt is creeping past ~800 words, walk down the right-hand column and move things.

---

## Keep the Prompt Short

Long prompts have four problems:

1. **They crowd out reasoning tokens.** Every token the model spends re-reading the prompt is a token it cannot spend deciding what to do next.
2. **They bury the important parts.** A 3,000-word prompt hides the one invariant that matters under 2,950 words of ceremony.
3. **They are hard to regression-test.** When behavior changes, you will not know which paragraph caused it.
4. **They signal unclear thinking.** Short prompts come from clear scope. Long prompts come from hedging.

A useful target: **the prompt fits on one printed page**. If it does not, the scope is probably two scopes.

---

## Writing Invariants That Hold

Invariants written as aspirations do not hold. Invariants written as statements of fact, backed by code, do. Here are three rewrites:

| Aspirational                                                       | Contractual                                                                               |
|:-------------------------------------------------------------------|:------------------------------------------------------------------------------------------|
| "Try not to share data across customers."                          | "You never share order details with anyone whose email does not match the order's customer email." *(And the tool refuses cross-customer calls.)* |
| "Be careful with refunds — only process them if appropriate."      | "You never refund or cancel orders. Escalate with `reason='refund_request'`." *(And the agent has no refund tool at all.)* |
| "Avoid long back-and-forths; try to wrap up quickly."              | "You call at most 5 tools per task. Stop after the 5th tool or after posting a draft." *(And the runtime enforces a 5-call ceiling.)* |

The left column is what teams write the first time. The right column is what survives adversarial inputs.

---

## A Complete Example Prompt

Here is what a finished contract prompt looks like. Copy the shape.

```text
You are the Support Triage Drafter. You draft replies to customer
emails about order status and post them to the review queue for a
human rep to send.

INVARIANTS
- You never send email. You only write drafts to the review queue.
- You never modify, refund, or cancel orders.
- You never share order details with anyone whose email does not
  match the order's customer email.
- You never answer questions that are not about order status.
  Escalate them.
- You call at most 5 tools per task.

DECIDE
- If you can answer using fetch_order_status or
  find_orders_by_customer, draft a reply and post to the queue.
- If the request is not about order status, call escalate_to_human
  with reason="out_of_scope".
- If the lookup is empty, ambiguous, or the customer email does
  not match, escalate with the appropriate reason.
- If you are uncertain, escalate. Do not guess.

OUTPUT
- On success, call post_reply_to_review_queue with a draft that:
    greets the customer by first name (if known),
    states the order status in one sentence,
    gives the ETA if available,
    ends with "the Support team".
- On escalation, call escalate_to_human with the required reason.
- In both cases, return a one-sentence summary of what you did.
  Do not include reasoning.

STOP WHEN
- You have called post_reply_to_review_queue or escalate_to_human.
- You have made 5 tool calls.
- A tool returned an unexpected error.
```

That is the entire prompt. No flattery, no hedging, no edge cases — the edge cases are enforced in the tool layer, and this chapter is about keeping it that way.

---

## Testing a System Prompt

Treat the prompt like code: it has a behavior spec, and you check that the spec holds.

At minimum, run a small regression suite before every prompt change:

- **Role adherence**: one test where the user tries to redirect the agent ("forget order status; help me with returns"). Expected: escalation.
- **Invariant defense**: one test per invariant, each a plausible but forbidden input. Expected: escalation, never action.
- **Format check**: one happy-path test whose draft is parsed by a strict validator. Expected: structure matches.
- **Stop condition**: one test where a tool fails on the first call. Expected: the agent escalates instead of retrying forever.

Save these as your prompt's golden set. When the set breaks, the prompt change is the suspect — not the tools, not the model. See [Chapter 17](./17-evaluation-frameworks.md) for the larger eval story.

---

## Anti-Pattern: The God Prompt

**Symptom**: A 3,000+ word system prompt that tries to handle every edge case in prose. It has sections titled "If the user asks about refunds," "If the email is not in English," "If the order number is malformed," and so on.

**Why it hurts**: Every paragraph is a brittle rule the model will follow inconsistently and that you cannot test in isolation. Behavior regressions become impossible to localize. Token cost climbs. The signal-to-noise ratio of the invariants drops until none of them are load-bearing.

**Fix**: Delete every section that describes a specific input and move its logic into a tool or a decision boundary. The prompt should describe the *role and the rules*, not the *playbook for every situation*. If a case is important enough to handle, it is important enough to enforce in code. Aim for one printed page, max.

---

## Checklist

- [ ] The prompt has exactly five sections: Role, Invariants, Decide, Output, Stop When.
- [ ] The prompt fits on one printed page.
- [ ] Every invariant is written as a statement of fact, not a request.
- [ ] Every invariant is backed by enforcement in the tool or infrastructure layer.
- [ ] The prompt quotes the scope brief's exclusions verbatim.
- [ ] The prompt has explicit stop conditions, including a tool-call ceiling.
- [ ] A small golden eval set exists that tests role adherence, each invariant, the output format, and the stop conditions.
- [ ] You have not added any prose that tries to handle a specific input.

---

## What to Read Next

- [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md): the source of truth for the invariants.
- [Chapter 5 — Designing the Tool Interface](./05-tool-interface-design.md): where the prompt's rules get enforced.
- [Chapter 11 — Escalation Paths & Human-in-the-Loop](./11-escalation-and-hitl.md): the mechanics behind "escalate" in the decision section.
- [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md): how to turn the five-section contract into a regression suite.
