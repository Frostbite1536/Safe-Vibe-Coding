---
layout: default
title: 21. Checkpoint Summaries & Capability Drift
nav_order: 21
parent: Agents Guide
description: "Documenting what the agent can and cannot do after each milestone. How to detect and correct capability drift before it becomes scope creep or silent regression."
permalink: /agents/checkpoint-summaries
---

# 21. Checkpoint Summaries & Capability Drift

An agent that has been in production for six months is not the same agent you launched. The prompt has been edited, tools have been added or changed, the model has been upgraded, the scope brief has been tweaked to accommodate a business pivot, and the eval set has grown to cover new cases. Each change seemed small at the time. Together, they have produced an agent whose real behavior is subtly different from the one your original design documents describe.

That divergence is *capability drift*, and it is the slow poison of long-running agent systems. The fix is a discipline of explicit checkpoints — regular moments where you write down what the agent actually does now, compare it to what it used to do, and decide whether the changes are the ones you meant.

This chapter is about building that discipline into the normal lifecycle of the agent so drift is caught early, deliberately, and as a planned part of operations — not as an accidental discovery during an incident.

---

## What Drift Looks Like

Drift does not announce itself. It shows up as a collection of small, plausible changes whose combined effect nobody tracked:

- A tool description was tightened to fix a specific confusion. Six months later, the agent is handling a wider range of inputs than that description still covers.
- A new tool was added to solve one class of case. Eighteen months later, it is being called for a dozen classes of case the team never discussed.
- A prompt was edited to improve tone. It also, quietly, changed the escalation rate on ambiguous inputs.
- The model was upgraded to a newer version. The eval score held steady on average, but the *distribution* of tool calls shifted — the agent now takes a different route through the same tools to reach the same answer, with different failure modes in the long tail.
- The scope brief has a new exclusion added last quarter to handle a compliance concern. Nobody checked whether the running system actually enforces it in code.

Any one of these is fine. The problem is the *cumulative* effect: the agent's real capability envelope has moved, and no one on the current team can describe it accurately without digging through six months of commits and incident reports.

The symptoms of unchecked drift include:

- New team members cannot tell, by reading the scope brief, what the agent really does.
- Old test cases pass, but the team is not sure whether the tests still represent real behavior.
- Support reps notice the agent "doing something new" and are not sure whether it is a bug or intended.
- Incidents surface invariants that nobody on the team remembers adopting.
- The original authors of the agent are the only people who can answer "can it do X?" — and even they have stopped being confident.

Drift is not a technical problem. It is a *knowledge* problem, and the defense is documentation that is written regularly enough to stay true.

---

## The Checkpoint Discipline

A checkpoint is a short written artifact — one to three pages — that captures what the agent can and cannot do at a specific point in time. It is produced after every meaningful change to the agent, whether the change is code, prompt, tools, model, scope, or eval set.

Checkpoints are cheap to write and catastrophic to skip. Write them on a rhythm.

### When to write a checkpoint

- **After every release** that changes behavior. If the deployment ladder from [Chapter 18](./18-deployment-patterns.md) has moved something to production, there is a checkpoint.
- **After every incident** that produced a post-mortem action item. The action items often imply new invariants, new tools, or new scope exclusions — the checkpoint captures them.
- **On a regular cadence** regardless of release activity — monthly or quarterly, whichever matches the agent's change rate. Even when nothing shipped, the world around the agent may have shifted (upstream APIs, user patterns, compliance rules).
- **Before any major refactor or redesign**. You cannot know what you are changing if you do not know what you have.
- **When a new team member inherits the agent**. The checkpoint is their onboarding document. If it is not good enough for that, it is not good enough for its real purpose.

### What a checkpoint contains

A checkpoint is a snapshot of the agent's current state across seven axes. Short descriptions, concrete statements, no marketing language.

```text
CHECKPOINT — Support Triage Drafter
Date: 2026-04-12
Agent version: e7c3a91
Prompt version: sha256:…
Model: claude-sonnet-4-6

1. WHAT THE AGENT CAN DO NOW
   - Draft replies to order-status questions from customer email.
   - Look up orders by order number (ORD-xxxxxxxx format).
   - Post drafts to the review queue for a rep to send.
   - Escalate out-of-scope, ambiguous, and data-mismatch cases.

2. WHAT THE AGENT CANNOT DO
   - Cannot look up orders by customer email. Removed 2026-02;
     replaced by escalation.
   - Cannot handle non-English emails. Escalates them.
   - Cannot process refund or cancellation requests. Escalates.
   - Cannot access orders older than 90 days. Escalates.

3. CHANGES SINCE LAST CHECKPOINT (2026-03-15)
   - Tool description for fetch_order_status tightened to specify
     when not to call it (overlap with find_orders_by_customer).
   - find_orders_by_customer removed after audit showed it was used
     on <0.1% of runs and escalation handled those cases.
   - New exclusion added: "no orders older than 90 days."
   - Golden eval grew from 584 to 612 cases.
   - Model upgraded from claude-sonnet-4-5 to claude-sonnet-4-6.

4. CURRENT INVARIANTS
   (Lifted verbatim from system prompt and tool code.)
   - Never sends email directly.
   - Never modifies, refunds, or cancels orders.
   - Never shares order details with a non-matching email.
   - Never answers off-topic questions.
   - Calls at most 5 tools per task.
   - Access limited to orders <90 days old.

5. KNOWN LIMITATIONS
   - Escalation rate has risen slightly (20.6% → 20.3% baseline)
     due to the new 90-day rule. This is intentional.
   - Multi-turn context is not supported; each email is independent.
   - Customers who don't provide order numbers always escalate,
     even when a lookup by name would succeed.

6. HEALTH METRICS
   - Correct outcome (golden eval): 94.2% ± 0.8%
   - Escalation rate:              20.6%
   - Invariant violations:         0
   - Silent failures:              1 (LLM judge)
   - Avg cost per run:             $0.011

7. OPEN QUESTIONS / NOTES
   - Should we reconsider find_orders_by_customer now that
     escalation rate has stabilized? Decision deferred to Q3.
   - Q2 red team scheduled for 2026-05-20.
```

That is the entire artifact. It takes 30–60 minutes to write when you are in the habit and hours to write when drift has accumulated — which is exactly why you write it regularly.

---

## Comparing Checkpoints

A single checkpoint is a snapshot. A sequence of checkpoints is the thing that actually detects drift.

Every new checkpoint is compared against the previous one along three axes:

### 1. Intended changes vs. actual changes

Every change in the "changes since last checkpoint" section should correspond to a planned change: a release, a post-mortem action, a scheduled refactor. If there is a change in the checkpoint that nobody planned, that is drift — investigate it before moving on.

Common culprits:

- A tool description got edited to fix a bug and nobody updated the scope brief.
- A prompt change was intended to improve tone but also moved a decision boundary.
- A model upgrade changed the distribution of tool calls without changing the eval score.

Unplanned changes are not automatically bad. But they should be *acknowledged* rather than discovered.

### 2. Invariant stability

The list of invariants should be derivable from the system prompt and the tool code at the time of the checkpoint. If an invariant from the previous checkpoint has quietly disappeared — because the prompt was edited, or the tool enforcement was refactored, or a new tool was added that bypasses it — that is a *red alert*, not a footnote.

Every invariant that appears on the list should either:

- Be enforced in code (tool layer or runtime layer), or
- Be explicitly marked as "prompt-only, known limitation, accepted risk."

Invariants that are neither are decoration. They are not load-bearing and should not be listed as if they were.

### 3. Capability boundary

The "what the agent cannot do" list should be the same, or *more restrictive*, than the previous checkpoint unless there was an explicit decision to expand scope. Quiet expansions — where the agent is now handling something it used to escalate — are how scope creep becomes an incident.

When the capability boundary grew, ask three questions:

- Was the expansion a planned change, reviewed against the scope brief?
- Does the eval set cover the new capability?
- Are the new failure modes documented?

If any answer is no, the expansion has not been properly adopted yet, and the next step is to finish adopting it — not to ship the next change on top.

---

## Capability Regression Drills

In addition to checkpoints, run a *capability regression drill* on a regular cadence — quarterly is a good starting point. The drill answers one question: **is the agent still doing what the checkpoint says it does?**

The drill has three parts:

### 1. Capability inventory

Walk the "what the agent can do" section of the current checkpoint and test each entry. Pick a small set of inputs for each listed capability, run them against production (or staging, if the inputs would cause real changes), and confirm the agent handles them as claimed.

You are not looking for correctness — that is the eval set's job. You are looking for whether the *capability exists at all*. A capability listed in the checkpoint but missing from the running agent is drift in the opposite direction: the documentation has outrun the code.

### 2. Boundary probe

Walk the "what the agent cannot do" section. For each entry, craft a realistic input that tries to push against the boundary. Confirm the agent still refuses or escalates.

This is the part teams find most valuable, and the part most likely to surface surprises. A tool description change three months ago is now letting the agent handle a case it used to refuse. A model upgrade has made the agent more willing to engage with out-of-scope questions. A prompt edit has weakened an invariant that used to hold under pressure.

### 3. Invariant test sweep

Run the invariant test sweep from the eval set (Chapter 17 — the small set of tests that each map to one invariant from the system prompt). Every one of them should still pass. If any fails, treat it as a Tier 1 incident even if no user has complained yet — the invariant is broken and the next real-world trigger for it is a countdown clock.

---

## Documenting Known Limitations Honestly

The "known limitations" section of the checkpoint deserves its own treatment because it is the section teams are tempted to downplay. Honesty here is not a nice-to-have; it is a safety feature.

A limitation that is written down is one that:

- The on-call engineer can find during an incident investigation.
- A new team member can read before making changes.
- A user-facing team can quote when explaining what the agent does and does not do.
- The eval set can test that it still holds.

A limitation that is *not* written down is one that:

- Everyone "knows" until the one person who knows it leaves.
- Gets discovered as a bug instead of a feature.
- Ends up in an incident post-mortem as *"we did not realize the agent could not…"*.

When writing limitations, be specific about cause and scope:

- Not: *"Works best in English."*
  But: *"Only handles English. Non-English emails are escalated with reason='out_of_scope'."*
- Not: *"Sometimes misses subtle context."*
  But: *"Treats each email as independent. Does not read prior emails from the same customer, even when the current email is a reply to a previous thread."*
- Not: *"Requires good order numbers."*
  But: *"Looks up orders only when the user provides an order ID matching `ORD-[0-9]{8}`. Escalates when the user provides a name, email, or partial ID."*

The test: can a reader, who has never seen the agent before, predict how it will behave on an adversarial input based on the limitation list alone? If yes, the list is honest enough. If no, rewrite.

---

## A Worked Drift Detection

Here is how capability drift gets caught in practice.

A quarterly checkpoint is written for the Support Triage Drafter. In the "changes since last checkpoint" section, the author lists:

- Prompt revision to tighten the tone section.
- New tool description for `post_reply_to_review_queue`.
- Model upgraded from v4.5 to v4.6.

In the invariant list, the author copy-pastes the previous list. But as part of the discipline, they also run the invariant test sweep — and one test fails. The test is *"customer emails from a non-matching address → escalation."* The agent escalated 9 out of 10 times; the 10th time, it produced a draft.

Investigation:

- The sandbox-level test always passed with the old prompt.
- The new prompt is 50 words shorter. The author shortened the invariant section when they tightened the tone section, and one invariant now reads *"You should not share order details with different customers"* instead of *"You never share order details with a customer whose email does not match the order."*
- The tool layer's authorization check is still in place. So the invariant holds on the *tool* level.
- But the agent, under the slightly softer language, now sometimes believes it is allowed to post a draft that *mentions* cross-customer details in prose.

Resolution:

- The prompt is reverted to the firmer language.
- A regression eval case is added that covers "soft" cross-customer violations, not just tool-layer ones.
- The checkpoint discipline is credited as the thing that caught this, not the eval.
- The post-mortem includes an action item: every prompt edit that touches the invariant section must be reviewed specifically for invariant stability, in addition to the normal eval run.

Notice what happened: a small prompt edit, passed all the old tests, would have shipped silently without the checkpoint. The checkpoint discipline was the *one* layer that caught it — because the person writing the checkpoint went through the "invariant stability" comparison step, ran the invariant sweep, and found the regression. Every other layer (tests, evals, deployment ladder) would have passed this change.

This is the whole value proposition of checkpoints: they catch the class of drift where nothing is broken *yet*.

---

## Anti-Pattern: "The Agent Has Always Worked This Way"

**Symptom**: A team member explains a behavior by saying *"the agent has always done that"*. Nobody is sure when the behavior started or why. The original design documents describe something different. When asked where to read the current definition of scope, the answer is *"you kind of have to just know it"*. Onboarding a new engineer takes weeks because the system's real behavior is passed down orally.

**Why it hurts**: Oral tradition is the slowest, least reliable, and most turnover-fragile form of documentation. When the people who "just know it" leave, the team inherits a system they cannot confidently describe. Every decision after that is made with partial information; every change risks breaking something nobody remembered to mention. Drift accelerates because there is no record to check against.

**Fix**: Write the first checkpoint today, even retroactively. It will be painful; the gap between what is written and what the agent does will be embarrassing. That is the *point*. Every subsequent checkpoint is easier than the last one, because the drift has a starting line. Make the checkpoint a required output of every release. Make the oldest checkpoint in the repo a reference — when someone claims the agent "has always" done something, check.

---

## Checklist

- [ ] A checkpoint format exists and is documented — short enough to write in under an hour.
- [ ] Checkpoints are produced after every release, after every incident post-mortem, on a monthly or quarterly cadence, and before any major refactor.
- [ ] Each checkpoint covers: current capabilities, current exclusions, changes since the last checkpoint, invariants, known limitations, health metrics, and open questions.
- [ ] Every change in the "changes since last checkpoint" section corresponds to a planned action with an owner.
- [ ] Invariants are cross-checked against code at checkpoint time — every listed invariant is either enforced in code or explicitly labeled as a known-weak rule.
- [ ] The "cannot do" list is the same or more restrictive than the previous checkpoint unless a scope expansion was reviewed and adopted.
- [ ] A quarterly capability regression drill tests the capability inventory, probes the boundary, and runs the invariant sweep.
- [ ] Known limitations are written specifically enough that a new reader can predict behavior from them.
- [ ] Checkpoints are version-controlled in the same repository as the agent's code.
- [ ] New team members are onboarded using the current checkpoint as a primary reference.
- [ ] Oral-tradition knowledge — "the agent has always…" — is actively hunted down and written into the checkpoint.

---

## What to Read Next

- [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md): the scope brief the checkpoints are tracking against.
- [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md): the eval set whose cases the invariant sweep exercises.
- [Chapter 18 — Deployment Patterns](./18-deployment-patterns.md): checkpoints are produced at the top of every deployment ladder.
- [Chapter 19 — Monitoring & Incident Response](./19-monitoring-and-incident-response.md): incidents feed directly into the next checkpoint's "changes since last checkpoint" section.
