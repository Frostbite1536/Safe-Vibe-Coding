---
layout: default
title: 24. Documenting Agent Behavior
nav_order: 24
parent: Agents Guide
description: "Behavior specs, tool registries, decision logs, and honest known-limitations sections — the documents that keep an agent's real behavior and its stated behavior in sync as the system evolves."
permalink: /agents/documenting-agent-behavior
---

# 24. Documenting Agent Behavior

Documentation for a conventional software system describes code that is, at least in principle, self-describing. If the README drifts, you can read the source to find the truth. Documentation for an agent does not have that luxury. The "source" of an agent's behavior is spread across a system prompt, a set of tool implementations, a model version, a memory strategy, an escalation policy, and whatever the model happened to decide at runtime given all of the above. No single artifact on disk fully describes what the agent will do.

That is why documentation for agents is not optional. It is the only place where the *intended* behavior is written down in one piece, and therefore the only thing anyone can reliably check the *actual* behavior against. Without it, every question about what the agent is supposed to do becomes an archeological dig through git history, prompt diffs, and tool-code comments — and every team that has been through that dig has learned, usually through an incident, that the system they thought they had and the system they actually had were different.

This chapter is about the documents that keep those two things in sync. It complements [Chapter 21](./21-checkpoint-summaries.md), which describes the *rhythm* of updating documentation; this chapter describes the *artifacts* you keep updated.

---

## Four Documents Every Agent Needs

A serious agent project has at least four documents, all version-controlled in the same repository as the agent's code. They are different artifacts because they answer different questions and have different audiences. Merging them into one document is a tempting shortcut that produces something nobody on the team actually reads.

- **Behavior Spec** — *what the agent does and what it will not do.* Audience: anyone who wants to know, in one sitting, what this system is.
- **Tool Registry** — *every tool the agent can call, canonically.* Audience: engineers changing tools, reviewers of tool changes, and the LLM itself via the tool catalog.
- **Decision Log** — *the meaningful design and policy decisions and the reasons behind them.* Audience: the team's future self.
- **Known Limitations List** — *what the agent cannot do and will not reliably do.* Audience: users, support teams, incident responders, and the eval set.

Some teams add two more: a runbook (for the on-call rotation) and a prompt change log (for teams with rapid prompt iteration). Those are worth adding when the team is ready for them, but the four above are the floor, not the ceiling.

Each is described below with enough structure that you can write the first draft in an afternoon. Resist the urge to make them longer. A short document that everyone reads beats a long one that nobody does.

---

## 1. The Behavior Spec

The behavior spec is the first document someone should read when they encounter the agent. It is not a design document — those go in the decision log. It is not a user manual — that lives elsewhere. It is a short, declarative statement of *what the agent is* and *what it does*, written in the present tense, in the voice of the team that runs it.

A behavior spec has six sections. None should be more than a page; the full document should fit in ten minutes of reading.

```text
# BEHAVIOR SPEC — {AGENT_NAME}
Version: {SEMVER}
Last reviewed: {DATE}
Owner: {TEAM_OR_INDIVIDUAL}

## 1. Purpose
One paragraph. What problem does the agent solve, for whom,
and why was an agent chosen over a simpler alternative?

## 2. Scope — In and Out
- IN SCOPE: {bullet list of tasks the agent handles}
- OUT OF SCOPE: {bullet list of tasks the agent explicitly
  refuses or escalates}
(If the OUT OF SCOPE list is shorter than IN SCOPE, you have
not thought about it enough yet.)

## 3. Inputs and Outputs
- Inputs the agent accepts: {structure and examples}
- Outputs the agent returns: {structure and examples}
- Downstream systems that consume the outputs: {list}

## 4. Invariants
The named invariants the agent must never violate, and where
each is enforced (tool layer, prompt, runtime policy, etc.).

## 5. Escalation
When the agent stops and hands control back to a human,
what the escalation envelope looks like, and who receives it.

## 6. Current Model and Prompt
- Model: {model_id_and_version}
- System prompt hash: {sha256}
- Tool set hash: {sha256}
- Eval score on the current golden set: {score}
```

The most important section is Section 2, "Scope — In and Out." If you cannot write it with specific bullets, stop and go back to [Chapter 4](./04-defining-purpose-and-scope.md); the agent is not ready to be documented because it is not ready to exist.

The second most important section is Section 4, "Invariants." Every line in this section must name the *enforcement layer* for that invariant, not just the rule. *"Never share order details with customers whose email does not match the order — enforced in the `fetch_order` tool via the `customer_email` argument; prompt-level echo only as a secondary defense."* A line that says *"never share order details"* without naming the enforcement is an open question disguised as a rule.

---

## 2. The Tool Registry

The tool registry is the canonical catalog of every tool the agent has access to. It exists for two reasons: so that engineers can reason about the tool surface without reading the implementation code, and so that the LLM itself can be given an accurate, consistent tool catalog at runtime.

The registry must be structured. Prose here is the wrong choice — prose descriptions drift from the code and lie to both humans and models. A tool registry looks closer to a schema document than to a wiki page.

```text
# TOOL REGISTRY — {AGENT_NAME}
Version: {SEMVER}

## Tool: fetch_order

Purpose:
  Return the current status of a single order, keyed by the
  order's unique ID. Use this tool when the user provides an
  order ID in the format ORD-[0-9]{8} and you need the order's
  status, shipping address, or line items.

Do NOT use this tool when:
  - The user provides a name, email, or partial ID instead of
    a full order ID.
  - The order is older than 90 days (use escalate instead).
  - You only need to know whether the order exists (use
    order_exists instead).

Input schema:
  {
    "order_id": "string (pattern: ORD-[0-9]{8})",
    "requesting_customer_email": "string (email)"
  }

Output schema:
  {
    "status": "pending" | "shipped" | "delivered" | "returned",
    "shipping_address": { ... },
    "line_items": [ ... ],
    "last_updated": "ISO8601 datetime"
  }

Side effects:
  - Read-only. No database writes.
  - Logs the lookup to audit_log with requesting_customer_email.

Authorization:
  - The tool rejects the call with error code AUTH_MISMATCH
    if requesting_customer_email does not match the order's
    customer_email on file. Enforcement is in the tool
    implementation, NOT the prompt.

Error modes:
  - NOT_FOUND: the order_id does not exist.
  - AUTH_MISMATCH: the email does not match the order.
  - TOO_OLD: the order is older than 90 days.
  - TRANSIENT: database unreachable; retry once.

Last reviewed: {DATE}
Usage last 30 days: {count} calls, {percent}% of traffic
```

Four properties make this registry useful:

1. **"Do NOT use" is explicit.** Every tool entry spells out at least one case where the tool looks applicable but is wrong. This is the single most effective thing a tool description can do to reduce misrouting.
2. **Schemas are typed.** `string (pattern: ORD-[0-9]{8})` is better than `string`. `string (email)` is better than `string`. The LLM uses the type hints at runtime; humans use them at review time.
3. **Enforcement is explicit.** Each authorization or invariant is labeled with *where* it is enforced. If it is prompt-only, say so and treat it as a known weakness.
4. **Usage is tracked.** The "usage last 30 days" line is the input to your next tool audit. A tool at 0.0% usage for thirty days is a deletion candidate the next time you review ([Chapter 9](./09-minimal-tool-set.md)).

The tool registry is not the code. It is a document *derived* from the code, updated as part of every tool change. Some teams generate it mechanically from the tool implementation; others update it by hand on each PR. Either works, as long as "the registry and the code disagreed" is treated as a bug.

---

## 3. The Decision Log

The decision log answers a question that no other document can: *why is this system shaped the way it is?*

Every non-trivial agent has a history of decisions that were made early, that seem strange or restrictive later, and whose reasons are lost. *"Why are we capping tool calls at 5 instead of 10?"* *"Why does the agent escalate orders older than 90 days?"* *"Why did we drop the `find_orders_by_customer` tool in February?"* These are the questions that eat the most engineering time on mature agents, because every time someone asks one and nobody can answer, the team is tempted to reverse the decision, discover why it was made in the first place, and re-make it.

A decision log prevents that loop. It is a running list of architectural, scope, policy, and tooling decisions, each captured in a short entry at the time the decision was made.

```text
# DECISION LOG — {AGENT_NAME}

## DEC-0047 — Cap tool calls at 5 per task
Date: 2026-03-12
Owner: {NAME}
Status: Active
Supersedes: DEC-0031

Context:
  Before this decision, the agent had no cap and runs were
  occasionally exhibiting 20+ tool calls as the agent looped
  through alternative strategies. Average latency was 18s;
  p95 was 58s. One incident involved 142 tool calls on a
  malformed input.

Decision:
  Cap tool calls at 5 per task. Enforced at the runtime layer.
  Runs that exceed the cap are treated as status="failed" with
  reason="tool_call_cap_exceeded".

Alternatives considered:
  - Cap at 10: rejected, didn't prevent the incident above.
  - Cap at 3: too aggressive, broke legitimate multi-step cases.
  - No cap, just alert: rejected after the 142-call incident.

Consequences:
  - p95 latency dropped to 11s.
  - 1.3% of tasks now hit the cap and escalate where they
    would previously have answered. Reviewed via the golden
    eval; escalations are appropriate.
  - Deliberate: humans now handle the 1.3% edge cases.
```

The format is the lightweight Architectural Decision Record (ADR) pattern, adapted to the things that actually matter for agents. The essential fields are:

- **Context** — what was true before the decision. Without this, the decision reads as arbitrary.
- **Decision** — the chosen path, in the present tense.
- **Alternatives considered** — the paths not taken, and a sentence on why. This is the single field teams most commonly skip, and the one that pays off most when the decision is revisited later.
- **Consequences** — what changed, including the costs, not just the benefits.

Decision logs are append-only. A decision that is later reversed gets a *new* entry (`DEC-0068 — Reverse DEC-0047, raise tool-call cap to 8`), not an edit to the original. The old entry's `Status` field is updated from `Active` to `Superseded`. This leaves the full history visible and lets anyone trace the evolution of the system's shape without spelunking through git blame.

---

## 4. The Known Limitations List

The known limitations list is the document teams are most tempted to downplay and the one that pays off hardest when written honestly. [Chapter 21](./21-checkpoint-summaries.md) covers why honesty matters; this section covers the shape of the document.

A limitation entry has five fields:

```text
## LIM-{id} — {one-line title}
Discovered: {DATE}
Status: {active | mitigated | resolved}

What it is:
  One paragraph, concrete. The reader should be able to predict
  how the agent behaves on an adversarial input after reading
  this paragraph.

Why it exists:
  The underlying reason. Is it a model limitation, a scope
  choice, a deliberate cost trade-off, a known gap in the tool
  set, a compliance constraint?

How it surfaces:
  What the user sees when this limitation is hit. Error message,
  silent miss, escalation, wrong answer? Be specific.

Workaround:
  What the on-call engineer or support rep should do when a user
  hits this. If there is no workaround, say so.

Tracking:
  Link to the eval case(s) that verify the limitation still
  holds, or to the ticket for fixing it if it is on the roadmap.
```

Three tests for whether the limitation list is honest enough:

1. **The stranger test.** A new team member reading the list alone should be able to predict behavior on inputs that hit each limitation. If they cannot, rewrite.
2. **The support test.** A customer-facing support rep should be able to read the list and know what to tell a user who has hit a limitation. If they cannot, rewrite.
3. **The eval test.** Every limitation should correspond to at least one eval case that verifies the limitation is still the limitation it claims to be. Limitations drift like capabilities drift; without a test, there is no way to know when the limitation has silently widened or narrowed.

The worst mistake in limitations documentation is the marketing reflex — softening hard limits into encouraging language. *"Works best with English inputs"* is a lie wearing a smile when the truth is *"non-English inputs are escalated without being processed."* The first sentence comforts users; the second helps them. Only the second belongs in the document.

---

## Optional: Runbook and Prompt Change Log

For agents past the early-prototype phase, two additional documents become worth the overhead.

### The Runbook

The runbook is the on-call-facing document. It lives next to whatever other runbooks your team keeps, and it is written for someone who has been paged at 2am and has ten minutes to understand the situation.

It answers five questions:

1. **What does this agent do?** (Two sentences, not the behavior spec.)
2. **What are the alerts and what do they mean?** (Each alert → what it signals → first response.)
3. **What are the kill switches and where are they?** (Hard-stop and graceful-stop procedures from [Chapter 13](./13-cost-and-kill-switches.md).)
4. **Who owns this in business hours?** (Escalation chain.)
5. **What has broken before?** (Pointers to the last five incident post-mortems.)

A runbook is not the place for design rationale or long explanations. It is a one-page rescue card. If it grows past two pages, you have started writing a different document.

### The Prompt Change Log

For teams that iterate on the system prompt frequently, the prompt change log is a short append-only record of every prompt change with three fields: what changed, why, and the eval delta. It is not the decision log — prompt edits are rarely decision-log-worthy individually — but it is the only practical way to answer the question *"what did we change in the prompt between last week and this week?"* without diffing hashes in version control.

```text
## PROMPT-CL-0312
Date: 2026-04-08
Hash before: sha256:a3f1…
Hash after:  sha256:b8c4…

What changed:
  Tightened the "invariants" section. Rephrased
  "do not share order details with different customers" to
  "never share any order details with a customer whose email
  does not match the order, even in summary or prose form."

Why:
  Post-mortem for incident INC-2026-04-07. Previous phrasing
  let the agent produce prose summaries that mentioned cross-
  customer details.

Eval delta:
  Invariant sweep: 49/50 → 50/50.
  Correctness (golden): 94.1% → 94.2% (not statistically
  significant).
  No regression on latency or cost.
```

---

## Keeping Documents in Sync

Documentation drift is the default. A team that writes these four documents once and then moves on will, six months later, have four documents that are subtly wrong in ways that nobody has noticed. The defense against drift is not heroism; it is *friction*. Make it slightly painful to merge a change without updating the relevant documents, and drift stays bounded.

Three practices do most of the work:

### Link each document to a change trigger

Every document should have a one-line declaration at the top: *"This document is updated whenever X happens."* Examples:

- Behavior spec: *"Updated whenever the scope brief changes, the invariant set changes, or the model is upgraded."*
- Tool registry: *"Updated in the same PR as any tool implementation change."*
- Decision log: *"Updated when any decision of scope, policy, tooling, or architecture is made."*
- Limitations list: *"Updated whenever a limitation is discovered, mitigated, or resolved."*

This declaration is enforceable. A PR template can ask *"Did this change affect the tool registry? If yes, link the updated entry."* A reviewer can reject a PR that should have updated the registry but did not.

### Tie documentation to the checkpoint rhythm

Every checkpoint ([Chapter 21](./21-checkpoint-summaries.md)) is also a documentation audit. The author of the checkpoint should spot-check each of the four documents against the current state of the system, flag any section that has drifted, and fix the drift before the checkpoint is filed. If a checkpoint is published and the documents are still wrong, the checkpoint did not do its job.

### Assign each document an owner

An unowned document is a document that nobody is accountable for. Assign a single named owner (a person, not a team) to each document. Ownership can rotate, but at any given moment there is exactly one person responsible for the document being accurate. When the owner leaves the team, the rotation happens as part of the handover, not as a discovery six months later.

---

## Who Reads What

Writing documents that nobody reads is a common failure. Match the document to the audience; if you cannot name the audience for a document, delete it.

| Document | Primary readers | When they read |
|---|---|---|
| Behavior spec | New team members, stakeholders, security reviewers | Onboarding, reviews, audits |
| Tool registry | Engineers making tool changes, PR reviewers, the LLM itself | Every PR that touches tools |
| Decision log | Future team members, people revisiting old decisions | When asking "why is it this way?" |
| Limitations list | Support, users, incident responders, eval authors | When an unexpected case arrives |
| Runbook | On-call engineers | During incidents |
| Prompt change log | Authors of prompt edits, incident investigators | During prompt edits and post-mortems |

The most common audience mistake is writing the behavior spec as if it were the decision log (full of rationale) or writing the tool registry as if it were the behavior spec (full of prose). Each document has a voice. Keep them separate.

---

## Anti-Pattern: The Wiki That Nobody Reads

**Symptom**: There is a wiki, a folder of design documents, a Notion workspace, or a Confluence page tree. It is large. It has not been updated in three months. When something is needed, the team asks in Slack because they know the wiki is wrong more often than it is right. New team members are told *"don't bother reading the docs, just ask."*

**Why it hurts**: An ignored wiki is worse than no wiki. It costs maintenance time, provides false confidence during audits, creates plausible deniability for documenting new decisions ("we have docs, go read them"), and makes the real knowledge more tribal, not less. The first incident that involves someone acting on a stale wiki page is the moment the team discovers they have been carrying a liability, not an asset.

**Fix**: Aggressively shrink the documentation surface. Delete documents that nobody reads. Merge overlapping documents down to the four named in this chapter plus any that are genuinely load-bearing. For every surviving document, assign an owner, tie it to a change trigger, and include the "last reviewed" date at the top — a date older than six months is a red flag that escalates until it is addressed. Make the documents short enough to read. Make reading them a normal part of the workflow (PR template questions, onboarding steps, checkpoint audits) so they are exercised regularly. The test is simple: can any team member reliably answer "what does this agent do?" by pointing at a document? If not, the documentation has not earned its keep yet, and the work to fix it is higher-leverage than any feature.

---

## Checklist

- [ ] A behavior spec exists, fits in ten minutes of reading, and has an owner.
- [ ] The behavior spec's "out of scope" list is at least as long as its "in scope" list.
- [ ] A tool registry exists, is structured (not prose), and is updated in the same PR as any tool code change.
- [ ] Every tool in the registry declares at least one "Do NOT use" case.
- [ ] Every tool's authorization and invariants are labeled with the *enforcement layer*, not just the rule.
- [ ] A decision log exists in append-only form (ADR-style), with Context / Decision / Alternatives / Consequences fields.
- [ ] Superseded decisions are marked as superseded, not deleted.
- [ ] A known-limitations list exists and passes the stranger test, the support test, and the eval test.
- [ ] Every limitation has at least one eval case pinned to it.
- [ ] Each document has a named owner and a change trigger.
- [ ] Each checkpoint ([Chapter 21](./21-checkpoint-summaries.md)) includes a documentation audit step.
- [ ] "Last reviewed" dates are visible and no document is silently allowed to age past six months without a review.
- [ ] New team members are onboarded through the four documents and asked, at the end, what they couldn't find.

---

## What to Read Next

- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): the rhythm that keeps these documents honest.
- [Chapter 25 — Quick-Reference Checklists](./25-quick-reference-checklists.md): the consolidated checklists that reference the documents in this chapter.
- [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md): the source material for the behavior spec's scope section.
- [Chapter 5 — Designing the Tool Interface](./05-tool-interface-design.md): the source material for the tool registry.
