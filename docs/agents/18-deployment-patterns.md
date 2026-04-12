---
layout: default
title: 18. Deployment Patterns
nav_order: 18
parent: Agents Guide
description: "Staged rollouts, shadow mode, canary agents, and feature-flagging new tools. How to graduate an agent from sandbox to production without a cliff."
permalink: /agents/deployment-patterns
---

# 18. Deployment Patterns

The gap between "the agent passes every test" and "the agent is safe to run against real users" is wider than it is for most software. Traditional services change behavior only when you ship new code. Agents change behavior when you ship new code, when you change the prompt, when you adjust a tool description, when you swap the model, when upstream systems shift — and sometimes for reasons the audit log cannot fully explain.

You need a deployment strategy that assumes the first exposure to production is where you learn what you got wrong. This chapter is about graduating an agent from the sandbox to real users in steps small enough to catch problems while they are still recoverable.

---

## Why "Ship It" Is Not Enough

A typical web service either works or does not, and when it does not, the failure is usually loud — 500s, exceptions, broken pages. Agents fail differently:

- **Silent correctness regressions.** The agent still produces plausible-looking output, but it is subtly wrong. No errors fire. Users may not notice for days.
- **Long-tail behaviors.** The eval score is 98%, and the 2% that fails is invisible until you run against real traffic volumes.
- **Emergent behaviors under load.** Rate limits, latency pressure, and retry patterns surface bugs that never showed up at single-digit QPS in the sandbox.
- **Distribution shift.** Real users write messages the golden dataset never anticipated. The agent has to handle them on day one.

None of these are solved by "run the tests, merge, deploy." They are solved by *running the agent in places where its mistakes cannot hurt anyone* long enough to notice the mistakes.

---

## The Ladder of Exposure

Think of every new agent — and every meaningful change to an existing agent — as climbing a ladder, one rung at a time. You only climb to the next rung when you have evidence the current rung is fine.

### Rung 0 — Sandbox only

The agent runs only in the test harness from Chapter 14. Mocked tools, fake data, no real users, no real side effects. This is where the full test suite and the golden eval run.

**Exit criterion**: the full eval suite passes at or above the baseline, all chaos and adversarial tests pass, and the test-plan from Chapter 14 has no gaps for the change you are shipping.

### Rung 1 — Shadow mode

The agent runs against *real* production traffic but its outputs are not exposed to users. The real upstream request is handled by the previous method (a human, a different service, a simpler agent). The new agent sees the same input and produces what it *would have done*. The output is logged and compared against the real resolution after the fact.

Shadow mode is the single most valuable pre-launch tool you have. It answers the question *"how would this have handled yesterday's traffic?"* without any user being harmed.

What you learn in shadow mode:

- The real distribution of inputs — the ones your eval set should have had.
- The real cost per run under real trajectory lengths.
- The real latency under real load.
- The cases where the agent's answer differs from the existing system's — which is either "we found a bug in the agent" or "we found a bug in the existing system," and both are useful discoveries.

**Exit criterion**: the agent's shadow outputs agree with ground truth (existing system or human rater) at a rate you are comfortable with, typically within a couple of percentage points of the eval-set score. Any disagreements are reviewed and either fixed or explicitly acknowledged as known limitations.

### Rung 2 — Dark launch with internal users only

The agent is now exposed to real users — but only to employees, specifically the team owning the agent and a small ring of tolerant internal testers. The feature is gated by a user-level flag. External users still see nothing.

Dark launch catches the usability problems shadow mode cannot: the reply is technically correct but reads oddly, the draft is grammatically wrong in ways the grader missed, the escalation queue format is hard for the support rep to act on. These are "real user" bugs, and real users have to find them — but the blast radius is small and internal.

**Exit criterion**: internal users report that the agent's outputs are usable in production. Not "perfect"; *usable*. Any issues are either fixed or documented as known rough edges the next rung will surface more of.

### Rung 3 — Canary: a tiny slice of real users

The agent is enabled for a small percentage of real users or real traffic — 1%, 5%, 10%. The percentage depends on how much traffic you have and how confident you are. The goal is to expose the agent to *enough real volume to catch long-tail bugs, not enough to cause a proportional incident*.

Things you only catch at a canary:

- The long tail of adversarial or unusual inputs.
- Real cost and latency percentiles under real load.
- Silent correctness regressions the eval set did not represent.
- How the rest of your operational systems — support queue, alerting, dashboards — behave when the agent is in the loop.

**Exit criterion**: at least a week of canary traffic with no unexplained incidents, eval metrics on canary traffic within the confidence band of the sandbox eval, and support / operations teams reporting no escalations traced to the canary group.

### Rung 4 — Staged rollout to full production

The agent is now expanded beyond the canary in clear, reversible steps. 10% → 25% → 50% → 100%, with at least a day at each tier for observability to stabilize. Never jump from 10% to 100% — the goal is to have at least one intermediate stage where a problem would be visible but not catastrophic.

Each tier is a decision point, not a schedule. You graduate to the next tier only if the current tier is clean. The decision to pause, roll back, or continue is made by a human (or by a policy, but a reviewed policy) — never automated on pure metric threshold, because metric noise will eventually spook an automated system into pausing unnecessarily.

**Exit criterion**: 100% of traffic served by the agent, with metrics stable and within sandbox-eval tolerances.

### Rung 5 — General availability

The agent is on for everyone and stays on. This is not the end of the deployment work; it is the beginning of the operational chapters (Chapter 19 — Monitoring and Incident Response; Chapter 21 — Capability Drift). But the launch specifically is complete.

---

## Feature Flags for Agents

The mechanism that makes the ladder work is feature flags, and agent feature flags are a little different from the ones most teams are used to.

### Flag scopes

Agent feature flags should be flexible about *who* the flag applies to:

- **User-level**: enable/disable the agent per user.
- **Tenant-level**: enable/disable per customer or organization.
- **Region-level**: enable/disable per geography, for compliance or staged rollout.
- **Channel-level**: enable/disable per input channel (email vs. chat vs. API).
- **Percentage-level**: enable for N% of traffic across a scope, chosen deterministically so the same user gets the same experience on retries.

You want all of these because different rollouts call for different slicings. Launching by region is an easier rollback than launching by percentage; launching to one tenant catches tenant-specific bugs that percentage-based rollouts miss.

### Flag granularity

You also want flags to control more than just "is the agent on?":

- **The whole agent** — kill-switch scope (Chapter 13).
- **Individual tools** — the agent is on, but a risky new tool is off for most users.
- **Model selection** — route some traffic to a new model to compare against the baseline.
- **Prompt version** — A/B test a prompt change without rebuilding infrastructure.
- **Budget tiers** — allow a larger tool-call budget for internal users while keeping the production ceiling tight.

The more granular the flag surface, the smaller the blast radius when something is wrong. The tradeoff is complexity — too many flags and the deployed behavior becomes hard to reason about. A good rule: every flag has an owner, a default, a removal date, and a description of what "on" means.

### Deterministic bucketing

A user who sees the new agent on one request should see it on all their requests. Bucketing by `hash(user_id) % 100` gives you stable, deterministic groups where the same user lives in the same bucket every time. This matters because an agent that behaves differently across turns in a multi-turn session produces weird, hard-to-debug bugs.

For interactions without a user ID (batch jobs, background tasks), bucket by the work item's own stable identifier — not by wall-clock time.

---

## Comparing Shadow and Canary Results

Shadow mode and canary stages both produce real traffic you can compare against a baseline. The comparisons look different.

### Shadow comparisons

In shadow mode you have *paired* data: for each real request, you have both the production answer and the agent's would-be answer. You can compute agreement directly:

- Exact-match rate between the agent and the existing system.
- Distribution of disagreements by category (did the agent escalate more than the baseline? act more? use different tools?).
- Cost and latency deltas on the same inputs.

Paired comparisons are statistically powerful — you need far fewer samples to detect a regression than in unpaired comparisons. That is the main reason shadow is so valuable.

### Canary comparisons

In canary mode the traffic is split, and each user only sees one version. You cannot compare pairs; you have to compare *populations*. That means:

- Larger sample sizes before you can claim a difference is real.
- Bucketing discipline so the populations are actually comparable (hash-bucket by user, not by random split per request).
- Primary metrics that are *per-user* or *per-task*, not per-step — otherwise the users who spawn more tool calls dominate the numbers.

Both kinds of comparison need confidence intervals and repeat-to-confidence discipline from [Chapter 17](./17-evaluation-frameworks.md). A single day's numbers are rarely enough to decide.

---

## Prompt and Tool Changes Are Deployments

Here is the trap: changing a prompt feels like editing a string, not shipping code. So teams skip the deployment ladder for prompt edits and push them straight to production. Two weeks later an incident blames "the new prompt."

**Every prompt change is a deployment.** Every tool schema change is a deployment. Every model swap is a deployment. All of them go through the ladder, all of them run the full eval suite, and all of them get at least a canary.

The same is true, though less obviously, for *data* changes — an updated knowledge base, a new retrieval index, a refreshed set of examples. Agents are functions of their inputs, and the inputs include more than the user message. Treat every meaningful change to what the agent reads as a deployment with its own rollout.

---

## Rollback Discipline

A deployment ladder without rollbacks is a one-way street. Before you climb any rung, make sure you can climb back down.

### What rollback means for agents

Traditional rollback means "revert to the previous binary." Agents have more moving parts:

- **Code rollback**: revert the git SHA and redeploy.
- **Prompt rollback**: revert to the previous prompt version in the prompt store.
- **Model rollback**: route requests back to the previous model via the flag surface.
- **Tool rollback**: re-enable the old tool set, disable new tools.
- **Config rollback**: revert budgets, thresholds, and rate limits.

All five need to be independently reversible, and reversible *fast*. A rollback that takes 20 minutes is too slow for an agent incident.

### Rollback-friendly patterns

- **Prompts and tool schemas live in a versioned store**, not hardcoded into the binary. Rolling back the prompt does not require a redeploy.
- **Feature flags default to the old behavior**. Flipping a flag off should always return to a known-good state.
- **Do not delete the old path when you ship the new one**. Keep both live, flag-gated, for at least one full rollout cycle. The option to revert is worth more than the cost of carrying the old code.
- **Rollback is tested**. Practice it once before the first real incident. A rollback mechanism that has never been used does not exist.

---

## A Worked Rollout

Here is how a change — say, adding a new tool to the Support Triage Drafter — would walk the ladder.

1. **Sandbox (Rung 0)**: the new tool is implemented, unit-tested, and contract-tested. The golden eval runs with the new tool enabled. Scores are within tolerance. Chaos and adversarial tests catch one unexpected interaction, which is fixed.
2. **Shadow mode (Rung 1)**: the tool is flipped on in a shadow branch of the production agent. For a week, every real email produces two trajectories — one from the current agent (served to the rep) and one from the shadow agent with the new tool (logged). Agreements and disagreements are categorized. The team finds one case where the new tool produces worse escalation reasons; they tighten the tool's description and re-run shadow for another few days.
3. **Dark launch (Rung 2)**: the tool is enabled for the support engineering team's own ticket alias. Five internal users hit it for three days. Two of them flag a minor phrasing issue in the draft; one flags a real bug where the new tool masks a legitimate error. The bug is fixed; shadow is re-run to confirm.
4. **Canary (Rung 3)**: the tool is enabled for 5% of real customers, bucketed by customer ID. Over a week, the metrics dashboard shows eval-equivalent correctness and a slight increase in average tool calls per run. The team judges this acceptable — the new tool is doing real work — and prepares to graduate.
5. **Staged rollout (Rung 4)**: 5% → 25% (one day) → 50% (one day) → 100% (one day). Each tier holds until the dashboard is stable. No incidents.
6. **General availability (Rung 5)**: the flag is removed from the rollout plan but kept in the config in case of a future rollback. The golden eval set grows by a handful of new cases that exercise the new tool. Done.

Notice how long that was. That is correct. A simple tool addition took weeks. Anything faster is a cut corner, and cut corners are the reason incidents happen in the first week of a rollout.

---

## Anti-Pattern: Launch by Courage

**Symptom**: The team ships the agent by merging to main, flipping a flag to 100%, and watching the dashboards. There is no shadow mode, no canary, no staged rollout. The justification is *"we have good tests"* or *"we need to move fast"*. When a problem appears, the blast radius is everyone — there is no smaller slice to fall back to, no paired comparison to diagnose with, and no rollback path that does not itself require a deploy.

**Why it hurts**: The first few days of a new agent are when unknown-unknowns surface — the distribution-shift bugs, the rate-limit interactions, the real cost curve, the weird inputs nobody wrote a test for. Finding them at 100% of traffic means the first impression is the buggy one. Trust, once broken with users (or with stakeholders), is expensive to rebuild, and the postmortem reads "nobody disagreed that we should launch this way." That is not reassuring.

**Fix**: Climb the ladder. Shadow mode first, dark launch to internal users second, canary third, staged rollout fourth. Do this even when the change is "small." Especially when the change is small — small changes are the ones teams skip the ladder for, and they are the ones that catch you off guard.

---

## Checklist

- [ ] Every change to the agent — code, prompt, tool, model, data — follows the deployment ladder.
- [ ] A shadow-mode capability exists that can run the new agent against real traffic without exposing outputs to users.
- [ ] Shadow mode produces paired comparisons with ground truth and is reviewed before moving to the next rung.
- [ ] Dark launch exposes the agent to internal users before external ones, gated by user-level flags.
- [ ] Canary rollouts use deterministic bucketing by user (or work item), not time-random splits.
- [ ] Staged rollouts have explicit tiers with human review at each step.
- [ ] Feature flags cover the whole agent, individual tools, model selection, prompt version, and budget tiers.
- [ ] Rollback is independently reversible for code, prompt, model, tools, and config — and has been tested.
- [ ] Prompt and tool schema changes are treated as deployments, with the same ladder and the same eval gates.
- [ ] Old paths are kept live behind a flag for at least one full rollout cycle after a new path ships.
- [ ] A change you would be tempted to "just flip on" is recognized as exactly the kind of change the ladder was designed for.

---

## What to Read Next

- [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md): the eval gate that sits at the bottom of the ladder.
- [Chapter 19 — Monitoring & Incident Response](./19-monitoring-and-incident-response.md): the operational layer that takes over the moment real traffic lands.
- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): how to keep the agent accountable long after the rollout is done.
- [Chapter 13 — Cost, Rate-Limiting & Latency Budgets](./13-cost-and-kill-switches.md): the kill switches your rollout plan leans on for fast mitigation.
