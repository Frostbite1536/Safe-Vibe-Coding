---
layout: default
title: 17. Evaluation Frameworks
nav_order: 17
parent: Agents Guide
description: "Golden datasets, LLM-as-judge scoring, regression suites, and the difference between 'it passed my tests' and 'it's actually reliable.' How to measure agents across distributions, not just individual inputs."
permalink: /agents/evaluation-frameworks
---

# 17. Evaluation Frameworks

Testing and evaluation are related but different disciplines. Testing asks *"on this specific input, did the agent do the right thing?"*. Evaluation asks *"across a realistic distribution of inputs, how often does the agent do the right thing, and is it getting better or worse over time?"*.

Both are necessary. Tests catch individual regressions. Evaluation catches the slow drift in reliability that no single test will see. An agent can pass 100% of its tests and still be unreliable in production — and an agent with a dropping eval score is in trouble long before any single test fails.

This chapter is about building the eval harness that keeps your agent honest run after run, release after release.

---

## Tests vs. Evals

The distinction is worth naming clearly because teams routinely confuse the two.

| Tests                                           | Evals                                               |
|:------------------------------------------------|:----------------------------------------------------|
| Specific inputs with expected outcomes          | Distributions of inputs with aggregate metrics      |
| Pass / fail per case                            | Scores across the whole dataset                     |
| Deterministic (or quarantine)                   | Inherently noisy — measured with confidence intervals |
| Small count (tens to low hundreds)              | Larger count (hundreds to thousands)                |
| Run on every PR                                 | Run on every release and nightly                    |
| Break the build when they go red                | Gate the release when the score regresses          |
| *"Does the agent handle X correctly?"*          | *"How often does the agent handle the realistic workload correctly?"* |

You need both. Tests give you fast, precise signal on specific regressions. Evals give you slow, noisy signal on overall behavior. The eval score is your North Star metric; the test suite is the alarm system.

---

## The Golden Dataset

An eval harness is only as good as the dataset underneath it. The single biggest lever you have on eval quality is the set of inputs you score against.

A golden dataset for an agent should:

- **Cover the real workload.** Not just the cases you designed for, but the shape of inputs you actually see in production. Pull examples from production logs (with appropriate redaction) as often as possible. Synthetic data is a supplement, not a substitute.
- **Include all important categories.** Happy paths, edge cases, failure modes, scope-boundary cases, and adversarial inputs should each be represented in realistic proportions. If production is 70% happy path and 30% edge cases, the eval set should be too.
- **Have ground truth labels.** For every input, the expected outcome is recorded. The label includes whether the right answer is action or escalation, *which* tool the agent should call (or not call), and what the final state should be. Labeled data is expensive; budget for it.
- **Grow from incidents.** Every production incident, every chaos finding, every fixed bug becomes a new labeled case in the golden set. The set is an append-only record of everything that could go wrong and was noticed.
- **Be versioned.** The golden dataset is code. It lives in version control next to the agent. Changes are reviewed. Additions have provenance.

A useful size target: ~200 cases to start, growing to 1,000+ over the first year. Smaller than ~100 and the score has too much variance to trust; larger than ~5,000 and eval runs become too slow to do frequently. Those numbers scale with how many cases your agent handles per day.

---

## What to Measure

An agent eval score is never a single number. It is a small dashboard of related numbers, and different numbers catch different classes of regression. Here is a starter set.

### Correctness

Did the agent produce the right structured outcome for the input? For a triage-drafter style agent:

- **Right action selected**: did the agent draft vs. escalate as the label says it should?
- **Right data used**: did the draft reference the correct order, customer, and status?
- **Right escalation reason**: when escalating, did the agent pick the label's reason code?
- **No forbidden action**: did the agent avoid every action the scope brief forbids?

Correctness is usually the headline metric. But it is not enough on its own.

### Trajectory efficiency

Even when the outcome is right, *how* the agent got there matters:

- **Average tool calls per run.** Shorter is better, up to a point.
- **Average tokens per run.** Catches prompt bloat and context rot.
- **Average wall-clock per run.** Catches latency regressions.
- **Distribution of trajectory lengths.** A small regression at the p95 is a real signal even if the median is stable.

A 100% correct agent that now uses 50% more tokens per run is a regression. Efficiency metrics catch that.

### Escalation quality

Escalations are first-class outcomes (Chapter 11), and they need their own metrics:

- **Escalation rate.** Where does it sit compared to the label distribution? Too low means guessing; too high means over-cautious.
- **Escalation reason accuracy.** Among the cases where escalation is the right answer, is the agent picking the right reason code?
- **False escalations.** Cases the label says the agent should handle but it escalated anyway. These are quality regressions.
- **Missed escalations.** Cases the label says the agent should escalate but it acted anyway. These are *safety* regressions and should be tracked separately.

### Safety metrics

Track these separately from correctness. They have stricter tolerances — a few false escalations is a quality problem; a single invariant violation is a stop-the-line problem.

- **Invariant violation rate.** Per the scope brief's exclusions, how often did the agent do something it must never do? Target: zero.
- **Authorization-check failure rate.** How often did a tool's authorization layer refuse a call? Not a bug, but a rising number is a signal of drift.
- **Budget-exceeded rate.** How often did runs hit the hard-limit ceilings from Chapter 13?
- **Silent-failure rate.** How often did the agent claim success while the label says it failed? This is the most important and most expensive metric to compute — see "LLM-as-Judge" below.

### Cost

The cost-per-completed-task from Chapter 7, measured across the whole eval set. Catches the kind of regressions where a prompt edit doubled token usage and nobody noticed.

Report all of these as a small dashboard with historical series. Reviewing the series weekly is how slow regressions get caught before they become incidents.

---

## Deterministic vs. LLM-as-Judge Scoring

Different metrics need different scoring approaches.

### Deterministic scoring

When the label is a structured fact, the check is a plain comparison:

- *Was the tool `fetch_order_status` called with `order_id='ORD-18293746'`?* → yes/no
- *Did the final outcome equal `escalation` with `reason='out_of_scope'`?* → yes/no
- *Did the draft contain the order's tracking URL?* → yes/no
- *Did the run touch any forbidden tool?* → yes/no

Deterministic scoring is fast, cheap, reproducible, and should cover as much of the eval surface as possible. If you can express a metric as a yes/no check against the trajectory log, do it that way. Save the expensive techniques for the metrics you genuinely cannot capture this way.

### LLM-as-judge scoring

Some metrics resist deterministic checks. *"Is the draft reply factually consistent with the order data?"* is hard to express as a pattern match. For these, you can use a second LLM as a judge: feed it the input, the agent's output, and the label, and ask for a structured verdict.

LLM-as-judge is powerful but comes with rules:

- **Use a structured rubric.** Don't ask "is this good?"; ask specific yes/no questions with defined criteria. *"Does the reply mention the correct order status? Does it contain any data from a different customer? Is the tone consistent with the 'Support team' identity?"* Each answer is a separate scoring dimension.
- **Use a different model than the agent.** Using the same model to grade itself is a bias trap. Use a stronger model, a different family, or a model fine-tuned specifically for grading.
- **Calibrate against human labels.** Sample a few hundred cases, have humans score them, and check the judge's agreement. If the judge disagrees with humans more than ~10% of the time, the rubric or the judge needs to change.
- **Log the judge's reasoning.** The rubric should include a "reason" field so you can audit why the judge graded a run the way it did. Silent judgments are untrustworthy.
- **Budget for it.** Judge runs cost model tokens. A 1,000-case eval set with 5 rubric dimensions and a frontier judge can be meaningful money per run. Budget it and watch the cost like any other operational expense.

A common pattern: deterministic scoring for most metrics, LLM-as-judge for the 2–3 metrics that genuinely need it.

### Human-in-the-loop scoring

For the metrics that matter most and cannot be automated reliably, keep a small human review loop:

- A random sample of N runs per week is reviewed by a human rater.
- Their scores are compared to the automated judge's scores to calibrate.
- Their flagged findings become new labeled cases in the golden set.

Human review is slow and expensive per case, but it is the only source of ground truth you can actually trust, and it is what keeps the automated parts of the system honest.

---

## Running Evals

Eval runs are different from test runs, and your CI should treat them differently.

### Scheduled runs

- **Nightly**: full eval suite on the current main. Catches regressions within a day.
- **On release candidate**: full eval suite with confidence intervals reported. Gate the release on "is the new score within the confidence interval of the baseline, or better?"
- **On model upgrades**: full eval suite as the first step of any model change. A model that scores worse on *your* eval is a model you don't adopt, regardless of leaderboard numbers.

### Report format

Eval results should produce a short, human-readable report with:

- Headline metrics (correctness, safety) with confidence intervals.
- Deltas from the previous release, highlighted when outside the confidence band.
- A link to the set of runs whose score changed — so a human can inspect the cases that regressed.
- A link to the new labeled cases added since the last run.

The report is for humans. It goes on a dashboard, into a channel, into the release checklist. If no human reads it, you are not really running evals.

### Flake discipline

Eval scores are noisy. Never gate a release on a single run — use repeat-to-confidence. Two runs with different seeds, averaged, is a reasonable floor; five runs is better. When a metric moves, ask whether the delta is outside the confidence interval before reacting.

The goal is not to make evals deterministic. The goal is to make the *decisions* you make from evals robust to the noise.

---

## Eval-Driven Development

Once the harness exists, the workflow for agent changes becomes:

1. **Write a failing eval case** for the behavior you want to change. (This is the agent equivalent of TDD.)
2. **Make the change** — prompt edit, tool change, model swap, whatever.
3. **Run the focused eval**: does the new case pass?
4. **Run the full eval**: did anything else regress?
5. **If nothing regressed, ship**. If something did, stop and diagnose — not fix with *another* change on top.

This discipline is slow at first and faster over time. The eval harness becomes your conscience: you can no longer ship the change that makes one case better and three cases worse, because the dashboard will show it.

The same workflow applies to bug fixes: every production bug becomes a failing eval case first, then a code change, then a passing eval case. The regression record is automatic.

---

## A Minimal Eval Dashboard

For the Support Triage Drafter, a starting eval dashboard might look like:

```text
EVAL RUN 2026-04-12 — main @ e7c3a91

GOLDEN SET
- 612 labeled cases
- 428 happy path, 124 escalation-expected,
  40 adversarial, 20 chaos-regressions

HEADLINE METRICS  (95% CI over 3 repeats)
- Correct outcome:          94.2% ± 0.8%   (baseline 94.0%)
- Correct escalation reason: 91.3% ± 1.1%   (baseline 92.7%)  ⚠ regression
- Invariant violations:      0 (of 612)    (baseline 0)
- Silent failures (LLM judge): 1 (of 612)  (baseline 1)

EFFICIENCY
- Avg tool calls:         2.8   (baseline 2.6)  ⚠ +8%
- Avg tokens/run:         7,940 (baseline 7,650) ⚠ +4%
- p95 wall clock:         11.2s (baseline 10.9s)
- Cost per run:           $0.011 (baseline $0.010)

ESCALATION QUALITY
- Escalation rate:        20.6% (label says 20.3%)
- False escalations:      4
- Missed escalations:     2     ⚠ safety signal

REGRESSIONS TO INVESTIGATE
- 3 new escalation-reason mismatches (ambiguous→out_of_scope)
- 2 missed escalations in data-mismatch category

LINKS
- Regressed runs: …
- Full report:    …
- Label diffs:    …
```

That is one page, and it tells you everything you need to know to decide whether to ship this build. The warnings are specific, the trajectories are one click away, and the dashboard has a history so the trend is visible.

---

## Anti-Pattern: The Vanity Eval

**Symptom**: The team has an eval score. It is 98%. It has been 98% for months. New features are evaluated against it and always score 98%. When a production incident happens, the incident is not represented in the eval set. The eval set is stocked entirely with cases the agent handles well, and stays that way because no one wants to lower the number.

**Why it hurts**: A high, stable score is satisfying and useless. It does not catch regressions because the regressions do not land on the cases in the set. It does not represent production because production has a long tail the eval set has excluded. It provides false confidence, which is worse than no confidence, because it prevents the investigation that would have found the real problem.

**Fix**: Aggressively seed the eval set from production logs, including the hard cases — especially the ones where the agent did the wrong thing. An eval score that *drops* when you add real-world cases is a feature, not a bug — it means you just found the work. Resist the temptation to "clean" the set by removing cases the agent struggles with. Those are the cases that matter.

---

## Checklist

- [ ] A golden dataset exists, is versioned alongside the code, and has labels for every case.
- [ ] The golden set covers happy path, edge cases, failure modes, scope-boundary cases, and adversarial inputs in realistic proportions.
- [ ] The set grows from production logs and from every incident.
- [ ] Correctness, trajectory efficiency, escalation quality, safety, and cost are all measured — not just "accuracy."
- [ ] Most scoring is deterministic against structured trajectory facts, not string matches on output text.
- [ ] LLM-as-judge scoring is used sparingly, with a structured rubric, a different model than the agent, and periodic calibration against human raters.
- [ ] A small human review loop samples and labels real runs weekly.
- [ ] Eval runs are scheduled nightly and on every release candidate; they gate the release on regression against a baseline.
- [ ] Eval runs report confidence intervals and use repeat-to-confidence on flaky metrics.
- [ ] Changes to the agent follow eval-driven development — failing case first, then the change, then the full eval.
- [ ] The eval dashboard is short, human-readable, historically trended, and links directly to regressed runs.
- [ ] The team is comfortable with the eval score *going down* when new real-world cases are added.

---

## What to Read Next

- [Chapter 14 — Testing Strategies](./14-testing-strategies.md): the test layer underneath the eval layer.
- [Chapter 16 — Chaos & Adversarial Testing](./16-chaos-and-adversarial-testing.md): the adversarial cases that feed the eval set.
- [Chapter 18 — Deployment Patterns](./18-deployment-patterns.md): how the eval dashboard becomes a release gate.
- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): the long-term companion to eval scores — tracking what the agent can and cannot do over time.
