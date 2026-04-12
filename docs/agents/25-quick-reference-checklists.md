---
layout: default
title: 25. Quick-Reference Checklists
nav_order: 25
parent: Agents Guide
description: "Consolidated checklists for every phase of an agent's life — before building, during development, before production, and ongoing operations — each item tied to the chapter that explains it."
permalink: /agents/quick-reference-checklists
---

# 25. Quick-Reference Checklists

Every chapter of this guide has ended with a checklist. This chapter pulls those checklists into a single place, reorganized by the phase of the agent's life where each item actually gets used, and links each item back to the chapter where the full reasoning lives.

The checklists are designed to be **used**, not admired. If you print one, it should fit on a page. If you paste one into a pull-request template, it should be short enough that reviewers actually read it. If you hand one to a new engineer on day one, they should be able to tell, within a week, which items their current project has and which it doesn't.

The point of a checklist is not to prove that the system is safe. It is to prevent the specific class of mistakes that teams under pressure consistently make — the forgetting, the skipping, the "we'll add that later" — which compound into the anti-patterns in [Chapter 22](./22-anti-patterns.md). A checklist turns a habit that requires discipline into one that requires only honesty.

---

## How to Use These Checklists

Four rules get the most value out of them:

1. **Use the right checklist for the phase.** The "before production" checklist is not the same as the "during development" one. Running the wrong checklist at the wrong time produces false confidence in one direction and false anxiety in the other.
2. **Read each item honestly.** An unchecked box is information. A box checked because it was *almost* true, or because someone had a meeting about it once, is not.
3. **If an item is checked, you should be able to name the evidence.** Not the aspiration, not the plan, not the ticket — the artifact in the repository or the run in the log that proves the item is done. "Where is the test?" "Where is the kill-switch code?" "Where is the scope brief?"
4. **If an item does not apply, write that down.** A deliberate N/A with a one-line reason is fine and common. A silent skip looks identical to a forgotten item and should be treated as one.

The four lists below are cumulative. Items from earlier phases do not stop applying just because the phase has moved on — they become ongoing obligations. The "ongoing operations" list is the smallest because it assumes the first three have been done and are still true.

---

## Before Building

You are still in design. No code has been written. The worst mistakes you can make right now are mistakes of *shape* — choosing the wrong architecture, skipping the scope brief, signing up to build a system that should not exist. These items are cheap to do now and expensive to fix later.

- [ ] **A one-page purpose and scope brief exists.** Written down, not just discussed. See [Chapter 4](./04-defining-purpose-and-scope.md).
- [ ] **The scope brief has an "out of scope" section at least as long as the "in scope" section.** If you cannot describe what the agent will not do, you are not ready to build it. See [Chapter 4](./04-defining-purpose-and-scope.md).
- [ ] **The decision to build an *agent* (as opposed to a workflow, a single LLM call, or a retrieval system) has been justified on problem-fit grounds.** Not résumé grounds. See [Chapter 3](./03-when-to-build-an-agent.md).
- [ ] **The four-pillar model (Scope, Tool Contracts, Escalation, Observability) has been applied to the design.** Each pillar has a concrete answer before implementation begins. See [Chapter 2](./02-core-philosophy.md).
- [ ] **The tool interface is designed on paper.** Names, descriptions, typed input/output schemas, side effects, and authorization rules exist in a document before any tool is coded. See [Chapter 5](./05-tool-interface-design.md).
- [ ] **The system prompt is drafted as a contract, not a pep talk.** It has role, invariants, decision boundaries, output format, and an escape hatch. See [Chapter 6](./06-system-prompts-as-contracts.md).
- [ ] **Escalation criteria are defined.** The specific conditions under which the agent stops and hands control to a human are written down. See [Chapter 11](./11-escalation-and-hitl.md).
- [ ] **A model has been selected with a cost-per-run estimate.** The estimate is in the scope brief. The tradeoff between model capability and cost has been explicit. See [Chapter 7](./07-model-selection.md).
- [ ] **A memory and state strategy has been chosen.** "We'll figure out state later" is not a strategy; it is the first step toward [Context Rot](./22-anti-patterns.md#context-rot). See [Chapter 8](./08-memory-and-state.md).
- [ ] **The blast radius of the worst-case run has been estimated.** What is the most damage the agent could cause if it went completely wrong on its first real input? If the answer is "we don't know," stop and figure it out. See [Chapter 11](./11-escalation-and-hitl.md) and [Chapter 12](./12-authorization-and-sandboxing.md).
- [ ] **The alternative to building the agent has been costed.** A deterministic pipeline, a human-in-the-loop tool, or a simple LLM call — each as a specific proposal, not a shrug. This is the document you will be glad you wrote when the agent costs twice what you expected. See [Chapter 3](./03-when-to-build-an-agent.md).

If more than two of these items are not done, you are not in the "before building" phase — you are in the "design" phase that comes before it. Go back.

---

## During Development

You are writing code. Tools are being implemented. The system prompt is evolving. The first tests are being written. The worst mistakes you can make now are mistakes of *foundation* — skipping observability, deferring safety controls, letting the test environment drift from the real one.

- [ ] **Tools have typed input and output schemas, not free-form strings.** Untyped tools are a shortcut to [The `do_stuff` Tool](./22-anti-patterns.md#the-do_stuff-tool). See [Chapter 5](./05-tool-interface-design.md).
- [ ] **Tool descriptions are written for an LLM consumer.** Each description says when to call the tool, when *not* to call it, and what the side effects are. See [Chapter 5](./05-tool-interface-design.md) and [Chapter 24](./24-documenting-agent-behavior.md).
- [ ] **Observability is wired up from the first tool call, not added later.** Every tool call, decision, escalation, and error is captured in a trace that can be queried. See [Chapter 10](./10-observability-from-day-one.md).
- [ ] **A sandbox or mock environment exists and mirrors production.** No connection to production APIs before the sandbox passes the test suite. See [Chapter 14](./14-testing-strategies.md).
- [ ] **Happy-path tests exist and pass before any real-system connection.** Failing to do this is the first step toward [Testing in Production](./22-anti-patterns.md#5-testing-in-production). See [Chapter 14](./14-testing-strategies.md).
- [ ] **Authorization is enforced at the infrastructure and tool layer, not in the prompt.** Prompt-only authorization is not authorization. See [Chapter 12](./12-authorization-and-sandboxing.md).
- [ ] **Sandboxing is configured at the infrastructure layer.** Filesystem scoping, network egress rules, container isolation, or equivalent. See [Chapter 12](./12-authorization-and-sandboxing.md).
- [ ] **Per-run cost and latency budgets are enforced in code.** Not just documented in prose or hoped for in the prompt. See [Chapter 13](./13-cost-and-kill-switches.md).
- [ ] **Runaway-loop detection is in place.** Tool-call caps, repeat-call detection, circuit breakers. See [Chapter 13](./13-cost-and-kill-switches.md).
- [ ] **A graceful-stop and a hard-stop mechanism both exist and are tested.** Before the agent sees production. See [Chapter 13](./13-cost-and-kill-switches.md).
- [ ] **The first version of the tool registry is being maintained in the same PRs as the tool code.** Not written as an afterthought. See [Chapter 24](./24-documenting-agent-behavior.md).
- [ ] **The memory/state strategy from the design phase is the one that is actually implemented.** If it has quietly changed, update the design document before the code. See [Chapter 8](./08-memory-and-state.md).

A good rule: if observability is not already in place when the first tool is wired up, pause and add it. Every hour of development against a blind agent is an hour of work you will repeat later when you cannot figure out what went wrong.

---

## Before Production

The agent works in the sandbox. Tests pass. Someone is about to propose shipping. This is the most dangerous moment in the agent's life, because the gap between "works in the sandbox" and "works in production" is exactly the gap that produces the worst incidents. These items are the graduation gate — if any of them is unchecked, the agent is not ready.

- [ ] **Happy-path, edge-case, and adversarial test suites all pass.** Each one is a separate suite, not a subset of the others. See [Chapter 14](./14-testing-strategies.md) and [Chapter 16](./16-chaos-and-adversarial-testing.md).
- [ ] **Prompt-injection scenarios have been tested.** Direct injection, indirect injection via tool output, chained-action probes, contradictory-instruction probes. See [Chapter 15](./15-prompt-injection-defense.md) and the red-team library in [Chapter 23](./23-prompt-library.md).
- [ ] **A golden eval set has been established and the baseline score is recorded.** The eval set draws from real traffic, not just from cases the team knew how to write. See [Chapter 17](./17-evaluation-frameworks.md).
- [ ] **A silent-failure detector is wired into the eval suite.** Not just a correctness judge. The detector is [Chapter 23](./23-prompt-library.md#silent-failure-detector). See also [Chapter 17](./17-evaluation-frameworks.md).
- [ ] **Each named invariant has a dedicated invariant-checker test.** An invariant without a test is a suggestion. See [Chapter 17](./17-evaluation-frameworks.md) and [Chapter 21](./21-checkpoint-summaries.md).
- [ ] **The behavior spec, tool registry, decision log, and known-limitations list all exist and have named owners.** See [Chapter 24](./24-documenting-agent-behavior.md).
- [ ] **The known-limitations list passes the stranger test, the support test, and the eval test.** See [Chapter 24](./24-documenting-agent-behavior.md).
- [ ] **Escalation paths have been manually exercised.** Someone on the team has triggered each escalation reason end-to-end and confirmed that the right human receives the right envelope. See [Chapter 11](./11-escalation-and-hitl.md).
- [ ] **The kill switch has been tested under realistic load.** Not just in a unit test. Someone has triggered the hard stop during a stress run and verified it worked. See [Chapter 13](./13-cost-and-kill-switches.md).
- [ ] **The deployment ladder is planned.** Sandbox → shadow mode → canary → partial rollout → full. Each rung has its own success criteria and rollback procedure. See [Chapter 18](./18-deployment-patterns.md).
- [ ] **Monitoring and alerting are in place and aimed at the right signals.** Not a dashboard nobody watches; a small set of alerts that would page someone. See [Chapter 19](./19-monitoring-and-incident-response.md).
- [ ] **The on-call runbook exists and names who owns what.** See [Chapter 19](./19-monitoring-and-incident-response.md) and [Chapter 24](./24-documenting-agent-behavior.md).
- [ ] **The first checkpoint has been written.** Even if nothing has shipped yet. See [Chapter 21](./21-checkpoint-summaries.md).
- [ ] **An incident-response plan exists.** The first incident is not a surprise; it is a scheduled event whose exact timing is unknown. See [Chapter 19](./19-monitoring-and-incident-response.md).
- [ ] **The team has rehearsed a rollback.** Not just read the procedure. Actually run it, in staging, in the last week. See [Chapter 18](./18-deployment-patterns.md).

The rule for this list is stricter than the others: **no exceptions without a named decision-log entry.** An unchecked item at this gate is a decision. Write it down. If it is unwritten, it is not a decision, it is an oversight, and the graduation is not yet earned.

---

## Ongoing Operations

The agent is in production. People are using it. New versions are shipping. The worst mistakes you can make now are mistakes of *drift* — losing track of what the agent does, ignoring the monitoring, letting the documents rot, skipping the regression work. These are the cheapest items on this page and the ones most often forgotten.

- [ ] **Audit logs are reviewed on a regular cadence.** Weekly for new agents, monthly for mature ones. Not only when there is an incident. See [Chapter 10](./10-observability-from-day-one.md) and [Chapter 19](./19-monitoring-and-incident-response.md).
- [ ] **Tool-call patterns are analyzed for drift.** The distribution of which tools the agent calls is tracked over time, and unusual shifts are investigated. See [Chapter 21](./21-checkpoint-summaries.md).
- [ ] **Checkpoints are produced on schedule.** After every release, after every incident post-mortem, and on a regular cadence (monthly or quarterly). See [Chapter 21](./21-checkpoint-summaries.md).
- [ ] **The four core documents are updated when the system changes.** Behavior spec, tool registry, decision log, known-limitations list. PRs that should update a document and do not are rejected. See [Chapter 24](./24-documenting-agent-behavior.md).
- [ ] **The eval regression suite runs on every material change.** Material means anything that could plausibly affect behavior: prompt edits, tool changes, model upgrades, memory-strategy changes, escalation-logic changes. See [Chapter 17](./17-evaluation-frameworks.md).
- [ ] **Incident post-mortems are fed back into the scope brief, the eval set, and the limitations list.** An incident whose lessons are not captured in these three places is an incident whose cost has not been recovered. See [Chapter 19](./19-monitoring-and-incident-response.md) and [Chapter 21](./21-checkpoint-summaries.md).
- [ ] **A quarterly capability regression drill is run.** The invariant sweep, the boundary probe, the capability inventory. This is the step that catches drift the tests do not. See [Chapter 21](./21-checkpoint-summaries.md).
- [ ] **A red-team pass runs on a scheduled cadence, not only on new features.** Attackers iterate; so should the team. See [Chapter 16](./16-chaos-and-adversarial-testing.md).
- [ ] **The cost and latency budgets are still the right numbers.** Budgets set in the design phase drift as traffic changes. Review at each checkpoint. See [Chapter 13](./13-cost-and-kill-switches.md).
- [ ] **Tools that have not been called in the last 30 days are audit candidates.** Delete or justify. See [Chapter 9](./09-minimal-tool-set.md) and [Tool Sprawl](./22-anti-patterns.md#1-tool-sprawl).
- [ ] **The on-call knows the kill switch and has practiced using it in the last quarter.** Kill switches that nobody has practiced are kill switches that nobody can find at 2am. See [Chapter 13](./13-cost-and-kill-switches.md).
- [ ] **New team members are onboarded through the four core documents and asked what they couldn't find.** Their feedback is the cheapest, most honest signal you will get that the documents have drifted. See [Chapter 24](./24-documenting-agent-behavior.md).

The ongoing list is the one that decays fastest. Teams usually start it with enthusiasm and slowly lose items to the friction of production work. The defense is to treat ongoing items as scheduled rituals — on the team calendar, assigned to owners, with a visible history — rather than as a cultural aspiration. A checklist that lives in someone's head has no way to catch its own decay.

---

## The Single-Page Summary

When all four checklists above are too much, print this. It is not a substitute for the full lists; it is the minimum floor. A team whose answer to any of these eight questions is "no" should not be running an agent in production.

```text
THE AGENT GRADUATION TEST — SINGLE-PAGE VERSION

1. Can you describe, in one paragraph, what the agent will never do?
   → Scope brief with an out-of-scope list. (Ch 4)

2. Is every critical invariant enforced in code, not just in the prompt?
   → Tool-layer and infrastructure-layer enforcement. (Ch 2, 12)

3. Can you replay any single run from the trace logs?
   → Observability from day one. (Ch 10)

4. Does the agent escalate instead of guessing when uncertain?
   → Explicit escalation paths with typed reasons. (Ch 11)

5. Is there a kill switch, and has someone used it in the last quarter?
   → Hard-stop and graceful-stop mechanisms. (Ch 13)

6. Have adversarial and prompt-injection tests run against it recently?
   → Red-team and chaos test suites. (Ch 15, 16)

7. Does an honest known-limitations list exist, and is it tied to evals?
   → Limitations that pass the stranger, support, and eval tests. (Ch 24)

8. Was a checkpoint written in the last month?
   → The discipline that catches drift. (Ch 21)

If any answer is "no," the agent is not ready.
```

Eight questions. The full lists above are how you earn each "yes"; this is the question form you carry in your head.

---

## Anti-Pattern: Check-Box Compliance

**Symptom**: The team runs through the checklist the day before launch and marks items complete based on a loose interpretation — the eval suite "kind of exists" (a dozen test cases in a notebook), the kill switch "is in the plan" (ticket filed), the behavior spec "is in the README" (two paragraphs). Every box is checked. The agent ships. Two weeks later, an incident reveals that none of the boxes were honestly checked.

**Why it hurts**: A dishonest checklist is a dishonest artifact, and dishonest artifacts are worse than no artifact at all because they create the appearance of readiness without the substance. The team feels more confident than they should, the reviewers rely on the checklist as evidence of due diligence, and the incident that follows produces the most painful class of post-mortem: one that ends with *"we knew we were supposed to do this and we said we had."*

**Fix**: For every checked item, name the evidence. A specific file path, a specific test name, a specific commit hash, a specific document URL. "Where is it?" is a reviewer's question, and the answer should be one click, not three sentences of explanation. If an item cannot produce its evidence in under thirty seconds, it is not checked. Build the habit early — during the "during development" phase — so that "before production" is not the first time anyone is asked to produce receipts. The goal is not to fail teams at the gate; it is to make honest passes cheap enough that dishonest ones stop being tempting.

---

## What to Read Next

- [Chapter 22 — Anti-Patterns & Failure Modes](./22-anti-patterns.md): the failure modes each checklist item is trying to prevent.
- [Chapter 24 — Documenting Agent Behavior](./24-documenting-agent-behavior.md): the documents many of the checklist items point at.
- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): the rhythm that keeps the "ongoing" checklist from decaying.
- [Chapter 26 — Further Reading & Tooling](./26-further-reading-and-tooling.md): external resources for the practices these checklists depend on.
