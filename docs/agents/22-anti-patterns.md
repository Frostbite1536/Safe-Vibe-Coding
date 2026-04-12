---
layout: default
title: 22. Anti-Patterns & Failure Modes
nav_order: 22
parent: Agents Guide
description: "The full catalog of agent failure modes — Tool Sprawl, The God Prompt, Over-Autonomy, Silent Failure, Testing in Production, Undocumented Scope Creep, and more — with symptoms, causes, and fixes."
permalink: /agents/anti-patterns
---

# 22. Anti-Patterns & Failure Modes

Every chapter before this one ended with an anti-pattern, because every good practice has a specific bad practice it is trying to prevent. This chapter pulls those anti-patterns into a single catalog so you can use them the way they are actually used in practice: as a lookup table when something is wrong.

An anti-pattern is not the same as a bug. A bug is a specific failure in a specific line of code. An anti-pattern is a *shape* of mistake — a pattern of design, process, or culture that reliably produces bugs. The payoff of naming them is that once you can see the shape, you can stop treating each new failure as a surprise and start treating it as the same problem you have already seen, now arriving in a different costume.

This chapter is written to be read in two directions:

- **Forwards**, as a quick review of the failure modes the rest of the guide has been warning you about. If you have read Parts I–V, the names will be familiar; this chapter is where they live together.
- **Backwards**, as a debugging tool. When an agent is misbehaving in production and you are trying to figure out *what class of problem* this is, scan the catalog, find the entry whose symptoms match, and follow the "Fix" section and the linked chapter for the full treatment.

The catalog is not exhaustive. It is the set of failure modes common enough, damaging enough, and distinctive enough to have earned a name.

---

## How to Use This Catalog

Each entry follows the same structure:

- **Symptom** — what the failure looks like from the outside. The thing that made you suspect something was wrong.
- **Why it hurts** — the underlying damage the anti-pattern causes, including the second-order effects that are not obvious until you have seen it a few times.
- **Root cause** — the design or process mistake that lets the anti-pattern take root.
- **Fix** — the practical steps that get you out of it. Not "do the right thing" but *what* to do and in *what order*.
- **See also** — the chapter where the anti-pattern is developed in full, plus any related entries in this catalog.

A single real-world failure often sits at the intersection of two or three entries in this catalog. That is normal. Start with the one that matches the loudest symptom, fix that one, and re-read the others once you can see clearly again.

---

## The Six Core Anti-Patterns

These are the six failure modes this guide treats as foundational — the ones you are most likely to encounter, the ones most commonly named in post-mortems, and the ones every team building agents should be able to recognize without looking them up. The [Extended Catalog](#extended-catalog) that follows covers additional named failure modes that each have their own full treatment elsewhere in the guide.

### 1. Tool Sprawl
{: #1-tool-sprawl}

**Symptom**: The agent has dozens of tools. Several have overlapping or near-identical purposes. New team members cannot explain which tool to use when. The tool-call logs show the agent picking the "wrong" tool often enough that you have started writing prompt text to nudge it toward the right one. A recent incident involved the agent calling a tool nobody on the current team remembered was there.

**Why it hurts**: Every tool expands three things at once — the attack surface the agent presents, the testing burden required to ship a change, and the combinatorial space of tool-call sequences the agent might attempt. Tool sprawl compounds: as you add tools to fix edge cases, the agent gets more ways to take the wrong path through the problem, which produces more edge cases, which pressure you to add more tools. The end state is an agent whose real capability envelope nobody can describe.

**Root cause**: Adding tools is the lowest-friction way to "fix" an agent that failed on a new input. Deleting tools requires more courage than adding them, because any deletion risks removing a capability someone depended on. The incentive gradient slopes toward sprawl unless a deliberate countervailing discipline exists.

**Fix**: Run a tool audit. List every tool, count how often each has been called in the last 30 days of real traffic, and flag any tool under 1% usage as a deletion candidate. Merge tools whose purposes overlap — one tool with a richer input schema is almost always better than two tools that overlap in 80% of their behavior. For every tool you keep, the description should make it clear *when not to call it*, not just when to call it. Commit to a rule like "the next tool we add requires us to either delete or merge an existing one." Review the audit quarterly.

**See also**: [Chapter 9 — Building a Minimal Tool Set First](./09-minimal-tool-set.md); [The `do_stuff` Tool](#the-do_stuff-tool) later in this catalog.

### 2. The God Prompt
{: #2-the-god-prompt}

**Symptom**: The system prompt is five thousand words long. It has grown by accretion — a new paragraph for every edge case that ever surprised the team. It tries to handle every situation with English-language instructions, including ones that should be enforced in code. Edits to the prompt are nerve-wracking because nobody is sure which paragraph is still load-bearing and which is vestigial. New team members avoid touching it.

**Why it hurts**: A prompt at this size is no longer a contract; it is a swamp. The model cannot reliably attend to five thousand words of equally-weighted instructions, so edits in one section quietly change behavior in another. Edge cases that should have been addressed in tool schemas, escalation logic, or deterministic pre-checks are instead carried by paragraphs of increasingly desperate English. When something breaks, there is no single owner for any specific behavior, because every behavior is "in the prompt somewhere."

**Root cause**: Prompts are easier to edit than code, and English is easier to write than schemas and branching logic. Every time an edge case appears, the cheapest fix is to "just add a line to the prompt." The cost of that choice is invisible at the moment and compounding over time.

**Fix**: Move edge case handling out of the prompt and into the layer where it belongs. Deterministic rules go into tool schemas and pre-tool-call validation. Escalation conditions go into explicit escalation tool calls with typed reasons. Output format requirements go into structured output schemas. What remains in the prompt is the minimum: role, non-negotiable invariants, decision boundaries, and a pointer to the tools. Every paragraph in the surviving prompt should answer the question *"why can't this be enforced in code?"*. If it cannot, delete it.

**See also**: [Chapter 6 — System Prompts as Contracts](./06-system-prompts-as-contracts.md); [Prompt-Only Safety](#prompt-only-safety); [Prompt-Only Authorization](#prompt-only-authorization).

### 3. Over-Autonomy
{: #3-over-autonomy}

**Symptom**: The agent takes irreversible actions — sending messages, making payments, merging pull requests, deleting files, calling APIs with real-world side effects — without a human checkpoint. It is framed as a feature: "the agent handles the whole loop end-to-end." It is discovered as a problem the first time the agent takes one of those actions on bad input and there is no way to undo it.

**Why it hurts**: The damage from an irreversible action scales with the action, not with the cost of the run that caused it. A one-dollar LLM call can ship a thousand-dollar email to the wrong customer list. Autonomy without checkpoints means the blast radius of any single failure is unbounded. And the more capable the agent, the larger the blast radius, because more capable agents take larger actions more confidently.

**Root cause**: Irreversible actions are framed as the *point* of the agent — "we built this so it can actually do the thing, end-to-end." A human checkpoint feels like a retreat from that vision. The team postpones thinking about confirmation gates until the first incident forces them to, at which point the gates are bolted on retroactively and the trust has already been burned.

**Fix**: Classify every tool and action on a reversibility axis. Fully reversible (read-only, sandboxed writes) can run autonomously. Partially reversible (draft a reply, create a pull request) can run autonomously but must be visible and recallable. Irreversible (send, publish, pay, delete) requires an explicit human confirmation gate by default. The confirmation gate is a feature, not a bug. As the agent earns trust on a specific class of input, you can narrow the scope of the gate — but you start with it on, not off. See [Chapter 11](./11-escalation-and-hitl.md) for the gate design.

**See also**: [Chapter 11 — Escalation Paths & Human-in-the-Loop](./11-escalation-and-hitl.md); [Chapter 12 — Authorization, Sandboxing & Isolation](./12-authorization-and-sandboxing.md); [Silent Failure](#4-silent-failure).

### 4. Silent Failure
{: #4-silent-failure}

**Symptom**: The agent returns a plausible-looking response every time, even when it could not complete the task. The response is well-formatted and confident. Only later — during a manual audit, or because a user complained, or because downstream systems got garbage input — does someone realize that the agent has been returning hallucinated "successes" for a class of failing cases.

**Why it hurts**: A loud failure is a gift: it interrupts the pipeline, triggers alerts, and forces someone to look. A silent failure is a landmine: it passes through the system unnoticed, often for days or weeks, and the damage is measured by the number of downstream actions built on the wrong answer before anyone notices. By the time the failure is visible, the remediation is not a bug fix — it is an incident.

**Root cause**: Models are trained to produce fluent, helpful-looking outputs even under high uncertainty. The default behavior, absent very specific instructions and a structured output format, is to answer *something* rather than admit failure. Add to that the human tendency to trust confident prose, and the silent failure becomes the default outcome unless you deliberately engineer against it.

**Fix**: Require explicit success/failure signals. Every task the agent completes must return a typed outcome — one of `success`, `escalated`, or `failed_with_reason` — and downstream systems must check that field before acting. Treat vague, hedged, or "maybe-success" outputs as failures until proven otherwise; an eval that measures this directly is one of the most valuable evals you can build. Log every case where the agent produced an answer it was not confident in, and sample them for review. Make escalation the default response to uncertainty, not a last resort. See [Chapter 11](./11-escalation-and-hitl.md) for escalation design and [Chapter 17](./17-evaluation-frameworks.md) for silent-failure evaluation.

**See also**: [Chapter 11 — Escalation Paths & Human-in-the-Loop](./11-escalation-and-hitl.md); [Chapter 17 — Evaluation Frameworks](./17-evaluation-frameworks.md); [Over-Autonomy](#3-over-autonomy).

### 5. Testing in Production
{: #5-testing-in-production}

**Symptom**: The agent's first exposure to real inputs, real tools, and real systems is the day it goes live. There is no sandbox environment, or the sandbox exists but has drifted so far from production that nobody trusts it. The test suite — if it exists — exercises the happy path against mocked tools. Real correctness evidence comes from "we ran it on Alice's mailbox for a day and it seemed fine."

**Why it hurts**: Agents fail in ways that are invisible from unit tests: in the shape of their tool-call sequences, in their handling of surprising tool outputs, in the way long contexts accumulate, in adversarial inputs the team never imagined. Production is where those failures show up. If production is also where the *testing* happens, every failure is a user-facing incident, every fix is emergency work, and every lesson learned is paid for in real damage.

**Root cause**: Building a sandbox or mock environment is upfront work with no immediate visible payoff. Running against real systems is the fastest way to demo something working. Teams under demo pressure consistently make the trade that saves time today and costs much more time next month.

**Fix**: Build the sandbox before the agent runs against anything real. Mock every external tool. Write the test suite before connecting to production systems. Treat the first real-system connection as a deliberate graduation, not a default. The deployment ladder in [Chapter 18](./18-deployment-patterns.md) is how that graduation is staged. The chaos and adversarial tests in [Chapter 16](./16-chaos-and-adversarial-testing.md) are the evidence that the sandbox work has been done seriously. Make "testing in production" a phrase that gets pushed back on in design reviews, not a workflow.

**See also**: [Chapter 14 — Testing Strategies](./14-testing-strategies.md); [Chapter 16 — Chaos & Adversarial Testing](./16-chaos-and-adversarial-testing.md); [Chapter 18 — Deployment Patterns](./18-deployment-patterns.md); [Launch by Courage](#launch-by-courage).

### 6. Undocumented Scope Creep
{: #undocumented-scope-creep}

**Symptom**: The agent is now doing things that were never in its original design. When asked, nobody on the team can point to the decision that added the new capability. It "sort of started working" after a prompt tweak, or after a tool was repurposed, or after a model upgrade. The scope brief still describes the original design. The running system has quietly outgrown it.

**Why it hurts**: Undocumented scope is unmanaged scope. Every new behavior the team did not explicitly adopt is a behavior nobody tests, nobody monitors, nobody has committed to maintaining, and nobody has thought about from a safety or compliance standpoint. The failure mode is not that the new behavior is wrong — it is that when the new behavior *does* go wrong, the team has no framework for even recognizing that it was supposed to be out of scope.

**Root cause**: Agents generalize. A prompt written to handle order-status questions will, under the right phrasing, handle shipping questions, return questions, product questions, even complaints. Each generalization looks like a win in the moment. The team celebrates the agent "learning a new skill" without stopping to decide whether that skill was sanctioned. The scope brief stays frozen while the behavior migrates.

**Fix**: Treat the scope brief as executable. Every capability the agent exercises must appear in the "what it does" list of the current checkpoint ([Chapter 21](./21-checkpoint-summaries.md)) and be backed by test cases. Every capability not on the list must trigger an escalation, not a graceful handle. Run the boundary probe from the quarterly capability regression drill to catch quiet expansions. When a new capability is genuinely wanted, adopt it *deliberately* — update the scope brief, add test cases, document the invariants, ship it through the deployment ladder. Creep is what happens to teams that cannot say no; the fix is a process that makes saying yes require the same work as saying yes used to.

**See also**: [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md); [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md); ["The Agent Has Always Worked This Way"](#the-agent-has-always-worked-this-way).

---

## Extended Catalog

These entries come from the chapters that make them up. They are shorter because each one has its own chapter treatment — the goal of this section is to give you a recognizable name and a fast pointer, not to re-derive the argument.

### Calling Everything an Agent

**Symptom**: The team describes every LLM-powered feature as an "agent." A chatbot is an agent. A classifier is an agent. A retrieval-augmented QA system is an agent. The word has no discriminating power on the team; every design conversation starts with a five-minute disambiguation.

**Why it hurts**: You cannot design the right safety envelope for something whose category you have not pinned down. A stateless classifier needs different guardrails than a tool-using autonomous loop, and if you call both "agents" you will over-build the first and under-build the second.

**Fix**: Use the definition from [Chapter 1](./01-what-is-an-agent.md) — an autonomous system that perceives, decides, and acts using tools in a loop until a goal is reached or it gives up. Things that do not fit that definition are chatbots, pipelines, classifiers, or assistants; call them what they are.

### Agent as a Résumé Line

**Symptom**: The decision to build an agent was made before anyone wrote the problem statement. The project is described to leadership in terms of *what it is* ("it's an AI agent") rather than *what it does* ("it drafts replies to order-status emails"). When you ask whether a deterministic pipeline would have worked, the answer is defensive.

**Why it hurts**: An agent is the highest-complexity, highest-risk architecture you can pick. Picking it for résumé reasons instead of problem-fit reasons means every downstream trade-off — reliability, cost, oversight — is being made in service of a label instead of the user.

**Fix**: Apply the [Chapter 3](./03-when-to-build-an-agent.md) decision framework honestly. If a workflow, a single LLM call, or a retrieval system would do the job, build that instead. Come back to the agent architecture when the problem actually justifies the complexity.

### The Vague Mission Statement

**Symptom**: The scope brief reads *"Help users with customer support"* or *"Act as a coding assistant."* Nobody can recite from memory what the agent will refuse to do. The out-of-scope list is empty or aspirational.

**Why it hurts**: Vagueness at the top cascades into vagueness at every level below it. Tool designs become over-general, tests become unfocused, escalation criteria become unenforceable, and the agent inherits the team's inability to draw a line.

**Fix**: [Chapter 4](./04-defining-purpose-and-scope.md) — write the one-page brief. Include the exclusion list. Refuse to proceed with design work until both are concrete enough to review.

### The `do_stuff` Tool
{: #the-do_stuff-tool}

**Symptom**: A tool is named something like `execute_action` or `do_stuff` or `call_api`. Its input schema is `{ "command": "string" }` and its output schema is `{ "result": "string" }`. It is described as "a flexible tool that lets the agent do anything."

**Why it hurts**: A single tool that can do anything is indistinguishable from a shell. It gives the agent maximum expressive power and minimum type safety, turns every tool call into an opportunity for prompt injection and scope escape, and makes the tool layer impossible to audit. It is the tool-interface equivalent of `eval()`.

**Fix**: [Chapter 5](./05-tool-interface-design.md) — every tool does one named thing with typed inputs and typed outputs. If the agent needs to do five things, expose five tools. The constraint is the safety feature.

### Prompt-Only Safety

**Symptom**: The invariant "never share order details with customers whose email does not match the order" lives only in a paragraph of the system prompt. There is no code in any tool that enforces it. Asked where the enforcement lives, the team points at the prompt.

**Why it hurts**: Prompt text is a suggestion to the model, not a guarantee about the system. A sufficiently persuasive user input, a prompt injection, a model upgrade, or a well-intentioned prompt edit can all quietly defeat the rule. The team *believes* the rule holds because they can read it in the prompt; the system does not actually enforce it.

**Fix**: [Chapter 2](./02-core-philosophy.md) — every invariant that matters must be enforced in the layer below the model. That means tool-layer checks, deterministic pre- or post-filters, authorization inside the tool implementation, or runtime policy checks. Prompt text can *echo* the rule for consistency, but it cannot be the only enforcement.

### Context Rot

**Symptom**: The agent's behavior degrades as the task gets longer. Early in a run it is precise and on-topic. After ten or fifteen tool calls, it starts repeating itself, mis-routing decisions, or losing track of invariants. The logs show a context window filling with stale tool output and prior reasoning the agent is still being asked to attend to.

**Why it hurts**: Every token of irrelevant context is a token the model has to work around. Long contexts are not free; they reduce effective attention to the things that still matter, and they make the model more likely to be distracted by something it saw earlier in the run.

**Fix**: [Chapter 8](./08-memory-and-state.md) — bound memory explicitly. Summarize and compact on a schedule. Reset on milestone completion. Do not treat the context window as a scratchpad you never clean.

### Model Mismatch

**Symptom**: A cheap fast model is being used to orchestrate a reasoning-heavy task and making bad decisions, or a frontier model is being used to classify trivial inputs and costing ten times what it should. The choice of model was made once, early, and has not been revisited.

**Why it hurts**: The wrong model at the reasoning layer produces wrong answers at volume. The wrong model at the routing layer produces a cost blowout. Both mistakes are invisible until someone looks at the eval score or the monthly bill.

**Fix**: [Chapter 7](./07-model-selection.md) — match model capability to the work each step actually does. Mixed-model pipelines are not an advanced technique; they are the default for any agent with more than one kind of step.

### Observability Theater

**Symptom**: There are logs. There is a dashboard. Nobody can answer the question "what did the agent decide at step 7 of the run that failed yesterday?" without grepping through a JSON blob by hand. The observability exists for compliance reasons, not debugging reasons.

**Why it hurts**: Logs you cannot query at incident time are not logs; they are an archaeological deposit. When something breaks, the team cannot diagnose it, which means every incident takes longer than it should and some incidents are never truly explained.

**Fix**: [Chapter 10](./10-observability-from-day-one.md) — every tool call, every decision point, every escalation, every error must be captured in a trace that can be filtered, replayed, and joined to the run that produced it. Build the query paths into the tooling, not into incident-time improvisation.

### Prompt-Only Authorization

**Symptom**: Access control is implemented in the system prompt: "You may only access orders for the requesting customer." The tool layer accepts any customer ID the agent passes in. Asked what prevents the agent from passing a different customer ID, the team points at the prompt.

**Why it hurts**: Authorization that lives in prose cannot survive prompt injection, jailbreaks, or even an innocent misunderstanding by the model. It is not authorization; it is a polite request.

**Fix**: [Chapter 12](./12-authorization-and-sandboxing.md) — the tool layer enforces identity, scopes, and per-call permissions. The model proposes; the tool disposes. Sandboxing and network egress rules live in infrastructure, not in prose.

### Kill-Switch Absent

**Symptom**: There is no way to halt a running agent short of killing the process and hoping. A runaway loop can burn through the API budget for the month before anyone notices. The "stop" button, if any, is "wait for the task to finish on its own."

**Why it hurts**: Agents go off the rails in ways humans do not predict. Without a kill switch, the first time it happens in production you are paying for every token it takes to discover that fact, and any irreversible actions it takes along the way are yours to live with.

**Fix**: [Chapter 13](./13-cost-and-kill-switches.md) — design graceful-stop and hard-stop mechanisms before the agent sees production. Per-run token and latency budgets, runaway-loop detection, circuit breakers on tool calls, and a single operator-facing kill switch that every team member knows how to use.

### Trusting the Model to Notice

**Symptom**: The defense against prompt injection is "the model will recognize the injection attempt and refuse." There is no structural separation between user content and instructions, no validation of tool outputs, no alerting on anomalous instruction patterns.

**Why it hurts**: Models catch *some* injections and miss others. The failures are not random; attackers iterate until they find the phrasing that gets through. A strategy that relies on the model's pattern-matching is a strategy that will lose the first time someone puts real effort into breaking it.

**Fix**: [Chapter 15](./15-prompt-injection-defense.md) — five-layer defense in depth. Structural separation, content validation, tool-output sanity checks, authorization at the tool layer, and alerting on anomalies. No single layer is the plan.

### Happy-Path-Only Testing

**Symptom**: The test suite exercises the cases the agent is designed to handle. It does not exercise contradictory instructions, simulated tool failures, malformed tool outputs, adversarial inputs, or context-exhaustion scenarios. The team describes the suite as "complete."

**Why it hurts**: Agents do not fail on the happy path — that is why it is called the happy path. They fail on the edges and under pressure. A suite that only exercises the middle of the distribution will miss every failure mode that matters.

**Fix**: [Chapter 16](./16-chaos-and-adversarial-testing.md) — chaos tests, adversarial tests, simulated tool failures, context-exhaustion runs, and deliberate scope-escape attempts. Budget as much test work for the pressure cases as for the happy path.

### The Vanity Eval

**Symptom**: The eval score is 94%, the team celebrates, and the agent ships. A month later, an incident reveals that the eval set is made up of the cases the team knew how to write, not the cases the agent sees in the wild. The 94% was a statement about the eval set, not about reality.

**Why it hurts**: A vanity eval gives the team a feeling of readiness without the underlying readiness. It produces false confidence that extends into deployment decisions, risk assessments, and incident response, and the cost of the false confidence is paid in every incident that the eval would have caught if it had been honest.

**Fix**: [Chapter 17](./17-evaluation-frameworks.md) — golden sets drawn from real traffic, regression suites that grow on every incident, LLM-as-judge scoring with human spot-checks, and an explicit comparison between the eval's distribution and the production distribution. Treat a 94% eval score as a hypothesis to test, not an answer.

### Launch by Courage

**Symptom**: The agent goes from "almost ready" to "in production" in a single decision. There is no shadow mode, no canary, no staged rollout. The launch plan is "enable the feature flag and watch the graphs."

**Why it hurts**: You have no evidence that the agent behaves well on real traffic until it is already behaving well or badly on real traffic, at the scale of the launch. The cost of a bad launch is proportional to the blast radius, and without staging you have no way to make that blast radius small.

**Fix**: [Chapter 18](./18-deployment-patterns.md) — the deployment ladder. Sandbox, shadow mode, canary, partial rollout, full rollout. Each rung has its own success criteria and its own rollback procedure. Courage is a fine personal trait and a bad deployment strategy.

### The Dashboard Nobody Watches

**Symptom**: There is a monitoring dashboard with dozens of charts. Nobody has it open right now. The most recent alert was dismissed two weeks ago. When the last incident happened, the team learned about it from a user complaint, not from the dashboard.

**Why it hurts**: A dashboard that is not part of someone's regular attention is not monitoring; it is decoration. The alerts that do not wake anyone up cannot shorten an incident. The charts that are not reviewed on a cadence cannot catch drift.

**Fix**: [Chapter 19](./19-monitoring-and-incident-response.md) — define the small set of alerts that should actually page someone, make the dashboard part of an operational rhythm (a brief daily or weekly review), and measure the dashboard by whether it caught the last incident before the users did.

### Multi-Agent Theater

**Symptom**: A problem that could have been solved by one agent with three tools has instead been solved by three agents passing messages to each other. The architecture diagram looks impressive. The reliability is worse than the single-agent version. Nobody can fully explain what happens when agent B receives a malformed handoff from agent A.

**Why it hurts**: Multi-agent systems multiply reliability costs across agent boundaries — 90% × 90% = 81% — and they introduce a whole new class of failure modes around handoffs, shared state, and coordination. Used unnecessarily, they trade away reliability for the aesthetic of distributed cleverness.

**Fix**: [Chapter 20](./20-multi-agent-coordination.md) — use multi-agent only when the situation actually calls for it: scope separation for safety, parallelism for throughput, or genuine orchestrator/worker specialization. When in doubt, collapse the system into one agent with more tools and revisit later.

### "The Agent Has Always Worked This Way"
{: #the-agent-has-always-worked-this-way}

**Symptom**: A team member explains a behavior by saying it has always been there. Nobody is sure when it started or why. The design documents describe something different. Onboarding a new engineer takes weeks because the system's real behavior is passed down orally.

**Why it hurts**: Oral tradition is the slowest, least reliable, and most turnover-fragile form of documentation. When the people who "just know" leave, the team inherits a system they cannot confidently describe — and every change after that carries an extra layer of risk.

**Fix**: [Chapter 21](./21-checkpoint-summaries.md) — write the first checkpoint today, even retroactively. Make checkpoints a required output of every release. Hunt oral-tradition knowledge and write it down.

---

## Diagnosing a Failure Back to Its Anti-Pattern

When an agent misbehaves in production, the temptation is to treat the incident as a novel event — a specific bug that needs a specific fix. Most incidents are not novel. They are one of the anti-patterns in this catalog, wearing different clothes.

A quick diagnostic flow:

1. **What was the surface symptom?** A wrong answer, a wrong action, a runaway cost, a missed escalation, a security boundary crossed. Write this down in one sentence.
2. **Which layer failed?** Scope, tool design, prompt, escalation, authorization, observability, testing, or deployment. There is almost always exactly one layer that is most responsible for the incident even though others may have contributed.
3. **Which anti-pattern matches?** Scan this catalog for the entry whose symptoms and root cause line up with your diagnosis in steps 1 and 2. Often you will recognize it immediately. Sometimes you will have to pick between two candidates; in that case the one that comes earlier in the agent lifecycle (e.g., scope before tool design) is usually the right answer, because the later problems are consequences of the earlier ones.
4. **Read the linked chapter.** The catalog entry is a summary. The chapter is the actual treatment.
5. **Fix the anti-pattern, not just the incident.** Fixing the specific bug without fixing the anti-pattern is a guarantee you will see the same class of incident again, from a different direction, within weeks.

The purpose of the catalog is not to assign blame after the fact. It is to make the first forty-five minutes of an incident retrospective shorter and more structured, so that the fix the team commits to is actually aimed at the root cause.

---

## Anti-Pattern: Reading This Chapter Instead of Fixing Your Agent

**Symptom**: The team has read the anti-pattern catalog, nodded at every entry, and identified the three that most obviously apply to their current agent. They have added those three to a backlog. The backlog has not moved in a month.

**Why it hurts**: A catalog is not a cure. Recognizing the shape of the problem is the first ten percent of the work; the remaining ninety percent is the unglamorous, expensive, politically difficult business of actually rewriting the scope brief, deleting the tools, rebuilding the sandbox, adding the kill switch, writing the checkpoint. Teams that stop after recognition get to feel they have addressed the risk without having changed the system that produces it.

**Fix**: Pick the single anti-pattern in this chapter that is most dangerous for your current agent right now. Commit to fixing it before reading any further. When it is fixed — actually fixed, not "in progress," not "planned for next quarter" — come back and pick the next one. The value of the catalog comes out when the list gets shorter, not when the team has memorized it.

---

## Checklist

- [ ] Every team member who builds or operates the agent has read this catalog at least once.
- [ ] The team uses the anti-pattern names as common vocabulary — an incident retrospective can reference "the God Prompt" or "Silent Failure" and everyone knows what is meant.
- [ ] Each incident retrospective explicitly identifies which anti-pattern(s) the failure sits under.
- [ ] Fixes address the anti-pattern, not just the specific bug — the remediation language in post-mortems names the layer that failed.
- [ ] The "core six" anti-patterns have been actively checked for in the current agent within the last quarter.
- [ ] The extended catalog has been scanned at least once per major release.
- [ ] Recurring appearances of the same anti-pattern in multiple retrospectives escalate to a process change, not just another individual fix.
- [ ] New anti-patterns discovered by the team (not in this catalog) are written up in the same format and added to the team's own version of the catalog.

---

## What to Read Next

- [Chapter 23 — Prompt Library for Agent Development](./23-prompt-library.md): reusable prompt scaffolds that implement the fixes named in this catalog.
- [Chapter 24 — Documenting Agent Behavior](./24-documenting-agent-behavior.md): how to keep the scope brief, tool registry, and limitation list honest enough to catch these anti-patterns early.
- [Chapter 25 — Quick-Reference Checklists](./25-quick-reference-checklists.md): the consolidated checklists drawn from every chapter, useful as a final pass before production.
- [Chapter 21 — Checkpoint Summaries & Capability Drift](./21-checkpoint-summaries.md): the discipline that catches anti-patterns as they reappear.
