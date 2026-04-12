---
layout: default
title: 19. Monitoring & Incident Response
nav_order: 19
parent: Agents Guide
description: "What to alert on in production, how to triage a misbehaving agent, and the kill-switch playbook. Turning Chapter 10's observability into operational safety."
permalink: /agents/monitoring-and-incident-response
---

# 19. Monitoring & Incident Response

Observability (Chapter 10) is the raw data. Monitoring is the part where a human — or a pager — finds out something is wrong before users do. Incident response is the part where someone stops the bleeding. This chapter is about the operational layer that sits between *"we have logs"* and *"we have a safely running agent"*.

The core idea is simple: the moment an agent runs against real users, the question is no longer *"will something go wrong?"*. It is *"how fast will we notice, and how fast can we stop it?"*.

---

## What to Monitor

The monitoring surface for an agent has four layers, and each one catches a different class of problem. Every one of them should be wired up before the agent graduates past shadow mode in Chapter 18's ladder.

### 1. Health — is the agent running at all?

These are the things traditional services monitor: process up, requests flowing, no obvious infrastructure failure. For agents, slightly specialized:

- **Model API availability**: success rate of calls to the model provider. A dip here is visible before anything else.
- **Tool API availability**: per-tool success rates. A spike in `tool_error` for a single tool usually points upstream.
- **Queue depth**: if the agent runs async, how deep is the backlog? Growing queue = agent cannot keep up.
- **Deploy health**: the usual web-service signals — 5xx rates, restart counts, memory pressure.

Health monitoring catches catastrophic failures. It is necessary but not sufficient. An agent can be perfectly healthy by these metrics and still be doing the wrong thing on every single run.

### 2. Behavior — is the agent doing the right kind of work?

These metrics describe what the agent is actually *doing*, not just whether it is running. They catch regressions in behavior that health checks do not see.

- **Outcome distribution**: the percentages of runs ending in `success`, `escalation`, `tool_error`, `budget_exceeded`, `invariant_violation`, etc. (the error categories from Chapter 10). Watch for shifts in this distribution, not just absolute values.
- **Escalation rate**: the canonical agent metric. Too low means the agent is guessing; too high means the agent is broken, the inputs are shifted, or the scope is wrong.
- **Escalation reason distribution**: a spike in `ambiguous` or `data_mismatch` often points to a change in the upstream data; a spike in `out_of_scope` often points to prompt injection or adversarial traffic.
- **Tool call mix**: how often each tool is called relative to baseline. A new, unexpected pattern — a rarely-used tool suddenly getting called often, or a core tool dropping out — is a strong signal that *something* shifted.
- **Trajectory length distribution**: p50, p95, p99 of tool calls per run. The p99 creeping up is the classic runaway-loop precursor.

Behavioral monitoring is the most agent-specific layer. Set up the dashboards before you launch.

### 3. Quality — is the work correct?

Quality metrics require ground truth or a proxy for it. They are slower to compute and more expensive, but they are the layer that catches silent correctness regressions.

- **Online eval score**: run the golden eval set (or a subset of it) against the production agent on a schedule — nightly, or every few hours. Track the same metrics as Chapter 17, with confidence intervals.
- **Sampled LLM-as-judge grading of live runs**: a random N% of production runs is fed to a grader model against a rubric, in the background. Grades are aggregated into a rolling quality score. Feed disagreements back into the golden set.
- **Human review backlog**: a small sample of runs routed to human raters weekly. Use it as the ground-truth calibration for the LLM judge.
- **User feedback signals**: when users can rate the agent's output (thumbs up/down, "this was wrong," re-open tickets after resolution), those signals go into the quality dashboard.

Quality monitoring catches the bugs where health and behavior look normal but the agent is wrong — the hardest bugs to find and the most damaging ones.

### 4. Cost and budget — is the agent affordable?

Finally, the metrics from Chapter 13, but now in production:

- **Spend per hour / per day**: token cost totals, broken down by agent, tool, and tenant.
- **Budget-exceeded rate**: how often runs hit the hard ceilings. A spike is either a new bug, a shift in input distribution, or both.
- **Per-user spend**: catches "one user is hammering the agent in a loop" and "one user is farming the agent for free compute."
- **Circuit-breaker state**: which tools are currently tripped, how long have they been out.

Cost is the metric most likely to surface through your finance team rather than your monitoring stack, which is exactly the wrong way to find out. Dashboard it properly and you will hear about problems from the alerts, not from accounts payable.

---

## Alerts: Noise Is the Enemy

A metric without an alert is a dashboard no one reads. A metric with a noisy alert is a pager no one trusts. The goal is a small set of loud alerts and a larger set of quiet ones that only page when something really is wrong.

A usable alert policy has three tiers.

### Tier 1 — Page immediately (humans wake up)

These are the alerts that warrant interrupting a human at any hour. Keep the list short. For an agent, at most:

- **Invariant violation** detected in a production run. Any single one. This is a stop-the-line event.
- **Silent failure detected** by the quality monitor above a small threshold.
- **Budget runaway**: spend exceeding a ceiling over a short window (e.g., $X in 10 minutes). Classic runaway-loop symptom.
- **Kill-switch failure**: an attempt to stop the agent via the kill switch did not take effect.
- **Mass escalation spike**: escalation rate multiple standard deviations above baseline, suggesting either an attack or a broken upstream.
- **Data leak detected**: any log line matching the tenant-isolation tripwires from Chapter 12.

Each of these needs a clear runbook entry. "Pager goes off → open runbook → follow steps." If the on-call does not know what to do in the first minute, the alert is not ready.

### Tier 2 — Notify a channel (humans glance during work hours)

These alerts go to a team channel, not to a pager. They need a human to look at them within hours, not minutes.

- Outcome distribution shifting beyond a confidence band.
- Tool call mix shifting beyond a confidence band.
- Online eval score regressing beyond the noise floor.
- Per-tool error rates rising above baseline.
- Trajectory-length p99 creeping up.
- Unusual new patterns in escalation reasons.

These are signals to investigate, not reasons to stop the agent. Most of them turn out to be upstream changes, not agent bugs — but "most" is not "all," and reviewing them is how you catch the drift before it becomes a Tier 1.

### Tier 3 — Dashboard only

Everything else. Long-term trends, slow-moving metrics, cost efficiency, eval drift over weeks. Nobody wakes up for these; nobody even looks at them daily. But the weekly review catches the bugs that never cross a sharp threshold.

### Tuning the alerts

Two rules keep the alert set honest:

1. **Every page is reviewed.** If a page fired and the response was "this was a false alarm, ignore it," the alert is miscalibrated. Either the threshold is wrong, the metric is wrong, or the runbook is missing something. Fix it that week.
2. **If the on-call has paged for the same non-issue twice, change the alert.** No exceptions. Alert fatigue is the slow poison of incident response; protect the pager's signal-to-noise ratio ruthlessly.

---

## The Incident Playbook

When something goes wrong, the team needs a small number of steps to follow. Not a wiki — a runbook, kept short enough to execute under pressure.

### Step 0 — Acknowledge

Someone owns the incident. They announce that they own it. No more people pile in; they report to the owner.

### Step 1 — Stop the bleeding

Before investigating, stop ongoing harm. Options from smallest to largest:

- **Flip the kill switch for the affected agent** (Chapter 13). This is the default first move for any incident that is actively causing harm. Users can wait a few minutes; damaged data cannot be un-damaged.
- **Revert to the previous prompt or model** via the flag surface. Fast, reversible, usually enough for prompt-induced regressions.
- **Disable a specific tool** via its feature flag. Useful when the incident is isolated to one tool's behavior.
- **Scope the stop**: kill the agent for one tenant, one region, one channel — don't stop everything if you can stop the part that matters.
- **Full rollback** of the most recent deploy if none of the above is sufficient.

Stopping the bleed is not the same as fixing the bug. You are buying time to investigate safely.

### Step 2 — Triage

With harm stopped, figure out what happened enough to classify the incident.

- Pull the affected runs from the audit log. Use the structured trace format from Chapter 10 to walk each one.
- Categorize by error category and escalation reason. A pattern is usually visible in the first three runs.
- Check for an obvious external cause: did an upstream API just change? Did a dependency deploy recently? Did the input distribution shift? Is there an adversarial pattern in the user messages?
- Check for an obvious internal cause: did the prompt change recently? The tool schema? The model? A config? Chapter 18's deployment ladder should tell you which of these are candidates.

### Step 3 — Communicate

Once you have a shape of the problem, tell people:

- **Internal**: a short, structured status update to the team and to stakeholders. What is happening, what we have done so far, what we know, what we do not know, and when the next update will land.
- **External**: if users are affected, a statement to them. Honest, specific, no mystery verbs ("an issue occurred"). Users forgive real incidents; they do not forgive feeling lied to.
- **Track the timeline**: every action, every decision, every discovery goes into a single timeline doc. This is the post-mortem's raw material.

### Step 4 — Fix

Now fix the actual bug. Not "revert and call it done" — that only works for regressions that came in with the deploy. Many agent incidents involve a change in the environment, not a change in the code, and those need a real fix to the agent's resilience to that change.

When a fix exists:

- Run the full eval suite against it, including the new case representing this incident.
- Walk the deployment ladder from Chapter 18 — shadow, dark launch, canary — before going to full production. The temptation to fast-track a fix mid-incident is real; resist it unless the ongoing harm is large enough to justify the risk of a second incident from a rushed fix.

### Step 5 — Re-enable

Flip the kill switch back off. Watch the dashboards closely. Be ready to flip it on again.

### Step 6 — Post-mortem

After the incident is fully resolved, run a blameless post-mortem. The deliverable is not *"whose fault was it"*; it is a list of concrete changes to the system that would have either prevented the incident or detected it faster. Typical changes:

- A new alert in Tier 1 or 2.
- A new case in the golden eval set.
- A new chaos or adversarial test from Chapter 16.
- An update to the incident playbook.
- A design change — scope, tool, prompt, infra.

Every post-mortem action item has an owner and a due date. No action items without owners; no owners without deadlines.

---

## Who Is On Call?

Agents need an on-call rotation. The alerts are useless without someone authorized to respond to them.

- **Primary**: the engineer who can flip kill switches, roll back deploys, and run the playbook. Reachable within minutes.
- **Secondary**: the backup, reachable within the hour, brought in when the primary needs help or when the incident is large.
- **Domain expert**: whoever understands the business context — *"is this pattern normal for order status traffic?"* — reachable asynchronously. Not paged for everything; paged when the call involves judgment the primary cannot make alone.

The first on-call rotation for a new agent should include at least one of its original authors, because they understand the design tradeoffs nobody wrote down. Over time, the rotation broadens as the team learns the system. The authors should not be on call forever — that is a recipe for burnout and bus-factor risk.

---

## Tabletop Drills

An incident playbook that has never been exercised is not a playbook, it is a wiki page. Run drills.

At least twice a year, stage a fake incident. The on-call engineer is paged, follows the runbook, and the team scores how fast they got from "page fired" to "harm stopped." The drill is not evaluated on cleverness; it is evaluated on *did the published process work*.

Drill ideas:

- **Runaway loop**: a fake spike in tool-call rate. Does the kill switch flip in time? Does the observability dashboard show what is happening?
- **Silent failure**: a seeded run where the agent is wrong but the normal monitoring is green. Does the quality monitor catch it? Does the sampled human review catch it?
- **Data leak**: simulate a near-miss on tenant isolation. Do the tripwires fire? Is the response correct?
- **Kill-switch failure**: the kill switch is flipped but the agent continues. How does the on-call escalate? What is the fallback?

A drill that reveals a gap is a successful drill. Every gap found in a drill is fixed before the next drill is scheduled.

---

## Anti-Pattern: The Dashboard Nobody Watches

**Symptom**: The team built a full metrics dashboard for the agent during the rollout. It covers everything — health, behavior, quality, cost. It is linked in the README. In practice, nobody has opened it since launch. When an incident happens, the team discovers it through a user complaint. The dashboard showed the problem starting three days earlier, but no alert fired and no one was watching.

**Why it hurts**: Passive monitoring is a form of performance theater. The data exists; the detection does not. The team feels covered and is not. Every minute between "the problem started" and "a human noticed" is a minute of user harm that was avoidable — and the dashboard's existence made the gap harder to spot, because it felt like someone was already looking.

**Fix**: Every important metric has an alert, not just a dashboard. Every alert has a tier (page, channel, review). Every page has a runbook entry. A metric without an alert is either promoted to one or demoted to "not important enough to track." And every week, a human glances at the Tier 2 channel and the Tier 3 dashboard — put it on a recurring calendar if you have to. The cost of looking is small; the cost of not looking is the incident that caught you.

---

## Checklist

- [ ] Health, behavior, quality, and cost metrics are all dashboarded.
- [ ] Every Tier 1 alert has a runbook entry that an on-call engineer can execute in one minute.
- [ ] The Tier 1 list is short (ideally under 10 items) and every entry represents real harm, not noise.
- [ ] Tier 2 alerts route to a team channel, not a pager, and are reviewed within business hours.
- [ ] Tier 3 metrics are reviewed on a recurring schedule, even when "nothing is wrong."
- [ ] The incident playbook is written, versioned, and linked from every alert.
- [ ] "Stop the bleeding" options are listed in order of increasing blast radius, and the smallest one is tried first.
- [ ] Kill switches are reachable in seconds and have been tested in a drill.
- [ ] Rollback is independently reversible for code, prompt, model, tools, and config.
- [ ] An on-call rotation exists with primary, secondary, and domain expert roles.
- [ ] Tabletop drills happen at least twice a year and produce concrete fixes.
- [ ] Every incident produces a blameless post-mortem with owned, deadlined action items.
- [ ] Alert fatigue is actively managed — repeat false alarms trigger alert changes, not just eye-rolls.

---

## What to Read Next

- [Chapter 10 — Observability from Day One](./10-observability-from-day-one.md): the raw telemetry this chapter depends on.
- [Chapter 13 — Cost, Rate-Limiting & Latency Budgets](./13-cost-and-kill-switches.md): the kill switches and budget enforcement that the playbook uses.
- [Chapter 18 — Deployment Patterns](./18-deployment-patterns.md): how to get into production safely in the first place.
- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): the long-term companion to incident response — detecting slow drift before it becomes a loud incident.
