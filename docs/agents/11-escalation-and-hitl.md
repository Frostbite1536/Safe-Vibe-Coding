---
layout: default
title: 11. Escalation Paths & Human-in-the-Loop
nav_order: 11
parent: Agents Guide
description: "When the agent must stop and hand control back to a human. Ambiguous input, low confidence, irreversible actions, and unexpected tool output — treated as a first-class success state, not a fallback."
permalink: /agents/escalation-and-hitl
---

# 11. Escalation Paths & Human-in-the-Loop

An agent that never asks for help is not confident. It is dangerous.

Every mature agent project eventually rediscovers the same lesson: the runs where the agent escalated are the ones that would have caused incidents if it had not. Escalation is not a sign that the agent is weak. It is the single most valuable behavior in the whole system — the thing that converts an unsafe autonomous loop into a safe collaborative one.

This chapter is about designing escalation as a first-class feature, not as the thing that happens when everything else has failed.

---

## Escalation Is a Success State

The biggest conceptual mistake teams make is to classify escalation as a failure. It is not. A run that escalates with good reason is a *successful run that happened to end in "hand off"*. It should be celebrated, not penalized, in your eval scores.

The consequences of treating escalation as success are large:

- **The model becomes willing to do it.** If your prompts, your evals, and your incentives all treat escalation as failure, the model will try very hard not to — and the tries will look like overconfident guesses.
- **The logs become tractable.** Escalations sit in their own category in observability (see [Chapter 10](./10-observability-from-day-one.md)) and become a design signal: *"these are the cases the agent knew it should not handle alone."*
- **The escalation queue becomes the product backlog.** The cases the agent escalates most often are the next tools, the next eval cases, and the next scope clarifications. Escalation is where the agent tells you what to build next.

In your metrics dashboard, reserve a separate slot for escalation rate. Track it over time. An escalation rate that is too low is not a win — it is a signal that the agent is guessing when it should be asking.

---

## The Five Situations That Must Escalate

Every agent should escalate in at least these five situations. Bake them into the prompt, enforce them in the tool layer, and test for them in the eval suite.

### 1. Ambiguous input

The user's request can be read in more than one way, and the different readings have meaningfully different answers. Examples:

- *"Cancel my order"* — which order? The most recent? All of them?
- *"Send it to the new address"* — which new address? The one you just added or the one on file?
- *"Refund the broken one"* — which broken one, if there are two?

Rule: *when the next action depends on a disambiguation the user did not provide, escalate.* Do not guess. Do not pick "the most likely" interpretation. Ambiguity is always cheaper to resolve with a question than with a wrong action.

### 2. Low confidence

The model is about to act, but its confidence in the action is below a threshold you set. Two practical ways to capture this:

- **Self-reported confidence**: require the agent to emit a confidence token (high / medium / low) as part of its decision. Route "low" straight to escalation.
- **Tool-driven confidence**: if a retrieval or classification tool returns a score, escalate when it falls below a calibrated cutoff.

Self-reported confidence is imperfect — models are notoriously miscalibrated. Combine it with hard triggers from the next three situations so you do not rely on self-report alone.

### 3. Actions above a risk threshold

Some actions are high-impact by their nature. They always escalate, regardless of confidence. Typical thresholds:

- Spending more than $X.
- Sending messages to more than N recipients.
- Modifying or deleting more than R records.
- Touching any data classified as "sensitive."
- Any action flagged as irreversible.

The threshold is a business decision, not a model decision. Pick numbers that match your organization's tolerance and enforce them in the tool layer — the prompt alone is not enough.

### 4. Unexpected tool output

The tool returned something the runtime was not expecting: an error, an empty result, a malformed payload, a value outside the declared schema. Any of these is a signal that the world does not match the agent's model of it, and the right response is almost never *"keep going and hope."*

Categorize tool outputs at the tool layer:

- `success` → proceed.
- `empty` → escalate unless the prompt explicitly handles empty as a valid case.
- `error_retryable` → retry once, then escalate.
- `error_permanent` → escalate immediately.
- `schema_mismatch` → escalate immediately, log loudly. This is usually a bug.

### 5. Any action explicitly flagged as requiring approval

The scope brief or the business process names a specific action type as "always requires human approval": a contract signing, a publication, a refund above $X, a deletion from production. These are not based on confidence or context — they are always escalated.

The simplest and safest implementation: the agent does not *have* a tool for those actions at all. The closest it can get is posting a draft or a recommendation into a queue that a human owns. See "Approval Gates" below.

---

## Approval Gates vs. Advisory Escalation

Not all escalation is the same. Distinguish two patterns in the design:

### Approval gates (hard stop)

The agent cannot proceed without a human's explicit yes. Examples:

- Posting a draft reply to a review queue where a support rep owns the send button.
- Recommending a refund that a finance manager must approve.
- Generating a code change that a reviewer must merge.

Implementation: the agent has *no tool that can perform the action*. The only available tool posts a proposal into a queue. A separate human-owned system actually executes. This is the safest pattern, and the pattern you should default to for anything irreversible.

### Advisory escalation (soft stop)

The agent hands off with context but does not strictly block the action. Examples:

- A chat assistant that says *"I'm not sure I understood — do you mean X or Y?"* and waits for the user to answer.
- A classification agent that flags a borderline case for human review but continues processing the rest of the batch.

Implementation: the agent emits an `escalate` tool call with a reason and a summary, and the upstream caller decides what to do next. Good for interactive cases where a user is already in the loop.

When in doubt, prefer approval gates. They fail safe.

---

## What an Escalation Must Contain

A bad escalation is as dangerous as a bad action. If the agent says "I need help" and does not say *why*, you will end up with a queue of escalations that humans cannot triage efficiently, and humans will start ignoring them.

Every escalation must carry:

- **Reason** — a short, enumerated code: `out_of_scope`, `ambiguous`, `data_mismatch`, `low_confidence`, `above_threshold`, `tool_error`, `invariant_risk`. Free-form reasons are bad; enumerated codes let you count, sort, and alert.
- **Summary** — one or two sentences in plain language explaining what the agent was trying to do and why it stopped.
- **Context snapshot** — the minimum set of facts the human needs to act: the user's request, the tool results so far, the relevant state. *Not the full trajectory — that is in the audit log.*
- **Recommendation** (optional) — if the agent has a guess at the right answer, it can include it, clearly labeled as a suggestion. The human still decides.
- **Link to full trace** — a one-click jump to the full run in the observability system.

Design the escalation payload like an API response. The consumer is a human, and humans deserve structured, scannable information, not a paragraph of apology.

Example:

```json
{
  "reason": "ambiguous",
  "summary": "Customer asked about 'the cancelled order' but has two cancelled orders from the last 7 days.",
  "context": {
    "user_message": "What happened with my cancelled order refund?",
    "matching_orders": [
      { "order_id": "ORD-18293746", "cancelled_at": "2026-04-08" },
      { "order_id": "ORD-18311902", "cancelled_at": "2026-04-10" }
    ],
    "customer_email": "customer@example.com"
  },
  "suggested_action": "Ask customer which order they mean before taking action.",
  "run_id": "run_01JKM8Z..."
}
```

A human can triage this in ten seconds. A free-form paragraph would take a minute and risk a wrong read.

---

## Routing Escalations

Escalation is only as good as the path from the escalation event to the human who acts on it. Design the routing explicitly:

- **Who is the owner?** Every escalation reason should route to a specific team or queue. No "miscellaneous" bucket.
- **What is the SLA?** Different reasons have different urgency. `tool_error` on a production run is "now." `out_of_scope` on a support ticket is "within 2 hours." Write the SLAs down.
- **How does the human respond?** The escalation should be *actionable* — the human can click a button, paste a reply, or trigger a retry. If the only response is "file a ticket in another system," the escalation path is incomplete.
- **What happens to the user in the meantime?** If a user is waiting, someone should tell them what is happening. A silent escalation is a bad user experience even when the handling is correct.
- **Does the loop close?** When the human resolves the escalation, the resolution should be recorded, linked to the original run, and fed back into the eval corpus. Uncounted escalations become invisible, and invisible things cannot be improved.

---

## A Worked Flow

The Support Triage Drafter receives an email: *"Hi, can you cancel my last order and refund it? Thanks!"*

Step-by-step:

1. The agent reads the scope brief's exclusions and sees that refunds and cancellations are out of scope.
2. It calls `escalate_to_human` with:
   - `reason: "out_of_scope"`
   - `summary: "Customer is requesting an order cancellation and refund, which are not in scope for this agent."`
   - `context.user_message: "<original email>"`
   - `suggested_action: "Route to cancellations team."`
3. Observability records the escalation in the `escalation / out_of_scope` bucket.
4. The routing layer sends the escalation to the cancellations queue, not to the general support queue.
5. A human rep picks it up within the SLA for that queue, handles it, and clicks "resolved."
6. The eval harness notes the run as a successful escalation. The weekly review notices that `out_of_scope / cancellations` is the most common escalation category — informing a future conversation about whether a separate cancellation agent is worth building, or whether an upstream router should send cancellation emails somewhere else entirely.

Every part of that flow is designed. None of it is accidental. That is what it means to treat escalation as a first-class feature.

---

## Anti-Pattern: Silent Failure

**Symptom**: When the agent is uncertain, or a tool returns an empty or unexpected result, the agent produces a plausible-sounding response and marks the run as successful. Users encounter wrong answers but no errors are raised. The audit log shows nominal runs; the escalation rate is suspiciously close to zero; the eval scores look great. The bugs only surface weeks later when a user complains.

**Why it hurts**: Silent failure is the worst failure mode because you cannot even count it. There is no dashboard signal, no error log, no alert — just a slow erosion of user trust. And because the run "looked successful," it gets used as positive eval data, which reinforces the behavior.

**Fix**: Wire uncertainty and unexpected tool output *into* the escalation path. Require the agent to emit a structured outcome — `success`, `escalation`, or `failure` — and treat a missing outcome as a bug. Alert on runs where the agent answered the user despite a tool error or an empty result. Treat a zero escalation rate as a smell, not a goal. In your evals, include adversarial cases where the correct answer is "I don't know" — and fail the run if the agent guesses.

---

## Checklist

- [ ] Escalation is counted as a success state in your metrics, not a failure.
- [ ] `escalate_to_human` (or equivalent) is one of the agent's tools from day one.
- [ ] The scope brief maps every failure criterion to an escalation reason.
- [ ] The five escalation situations (ambiguous, low confidence, above threshold, unexpected tool output, approval-required) are enforced in code, not just the prompt.
- [ ] Every escalation carries an enumerated reason, a summary, a context snapshot, and a link to the run.
- [ ] Approval gates exist for every irreversible action — the agent has no tool that can perform the action directly.
- [ ] Routing rules exist for every escalation reason. No "miscellaneous" bucket.
- [ ] SLAs are defined per reason and tracked in the dashboard.
- [ ] Resolution data flows back into evals and into capability drift reviews.
- [ ] Your eval set contains adversarial cases where the correct answer is "escalate," and the agent fails if it guesses instead.

---

## What to Read Next

- [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md): failure criteria in the scope brief become escalation triggers here.
- [Chapter 9 — Building a Minimal Tool Set First](./09-minimal-tool-set.md): escalation replaces the long tail of rarely-used tools.
- [Chapter 10 — Observability from Day One](./10-observability-from-day-one.md): escalations need first-class logging and dashboards.
- [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md): adversarial "should escalate" test cases.
- [Chapter 22 — Anti-Patterns & Failure Modes](./22-anti-patterns.md): Silent Failure and Over-Autonomy in the full catalog.
