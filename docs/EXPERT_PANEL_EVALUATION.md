---
layout: default
title: Expert Panel Evaluation
parent: Guides
nav_order: 17
description: "Using simulated expert committees to find architectural, economic, and systemic problems before they calcify."
---

# Expert Panel Evaluation: Finding What Bug Hunts Miss

Most vibe coders have one relationship with their LLM: builder. You describe what you want, it builds it. This is powerful — but it leaves a large class of problems undiscovered.

The technique described here adds a second relationship: **expert critic**. You ask the LLM to evaluate what you've built, not build more of it. The difference in output quality can be striking.

---

## The Core Idea

LLMs can roleplay domain expertise with surprising depth. A model asked to evaluate code as a senior security engineer will surface different findings than one asked to evaluate it as a distributed systems architect — even over the exact same codebase.

This is not a trick. It reflects something real: the framing you give an LLM changes which patterns it matches against, which failure modes it prioritizes, and how it weights trade-offs. The [Emotional Prompt Engineering guide](./EMOTIONAL_PROMPT_ENGINEERING.md) explains the mechanism — persona framing activates higher-quality token paths in the model's output.

**The technique**: before you build more, assemble a virtual committee of experts and ask them to evaluate what you've already built. Then use their findings to generate a concrete improvement plan before you write another line of code.

**The payoff**: you discover architectural, economic, and systemic problems in analysis — not after they've calcified across a large codebase.

---

## When to Use This

This technique is most valuable when:

- You've completed a significant phase of development and want a quality checkpoint
- Your system has domain-specific correctness requirements (economics, security, distributed systems, real-time systems, etc.) that go beyond "does it run"
- You suspect the design has structural weaknesses but can't articulate them
- You're about to start a major new phase and want to catch problems before they compound
- You've been the only reviewer and want a different lens

It's overkill for a simple CRUD feature. It's essential for anything with game mechanics, economic incentives, security invariants, consensus requirements, or complex multi-party interactions.

---

## The Workflow

### Step 1: Identify the Right Expert Domains

Start by thinking carefully about what *kinds* of correctness matter for your system. This takes 10 minutes and determines the quality of everything that follows.

For a token economy with staking and slashing, the right committee might be:

- A computer scientist (protocol correctness, state machine completeness, edge cases)
- An economist (incentive alignment, equilibrium analysis, market manipulation vectors)
- A game theorist (Nash equilibria, dominant strategies, collusion scenarios)
- A security engineer (exploit paths, economic attacks, griefing)

For a real-time multiplayer game, the committee might be:

- A distributed systems engineer (consistency, latency, partition tolerance)
- A security engineer (cheating vectors, replay attacks)
- A game designer (balance, progression loops, feel)
- A player (confusion points, frustrating edge cases)

For a financial application:

- A fintech compliance expert (regulatory exposure, audit trails)
- A security engineer (fraud vectors, access control)
- An accountant (ledger correctness, rounding behavior)

**Write the list down before you start.** Vague expert identities produce vague feedback.

### Step 2: Prime the Model with Context

Before invoking any expert persona, give the model a complete picture of what it's evaluating. Feed it:

- Your architecture document
- Your system invariants
- Relevant source files (all of them for the component under review)
- A plain-English description of what the system is supposed to do

If the codebase is large, start with the highest-level files and the invariants. You can drill down per-expert in later passes. See [Context Management](./CONTEXT_MANAGEMENT.md) for how to budget context effectively — you want the AI's full attention on the evaluation, not wasted on irrelevant code.

**Example context-setting prompt**:

```
I'm going to ask you to evaluate this codebase from several expert perspectives.
Before we begin, here is the full context:

[Architecture document]
[System invariants]
[Core source files]

The system is a decentralized job market where autonomous agents post work,
bid on tasks, stake tokens to signal commitment, and can be slashed for
non-performance. There is also a governance token that accrues fees.

Please confirm you understand the system before I ask the first evaluation.
```

This confirmation step is worth doing. It catches misunderstandings before you've generated a lengthy report built on a wrong assumption.

### Step 3: Run Each Expert Evaluation Separately

Invoke each expert persona in its own prompt. Mixing them into one prompt produces averaged, diluted feedback. Separate personas produce sharper, more specific findings.

**Example expert prompt**:

```
You are a senior economist with 20 years of experience analyzing token economies,
mechanism design, and decentralized market structures. You have advised protocol
teams on incentive alignment and have published research on staking dynamics
and slashing economics.

Review the system described above from your perspective. Focus on:
- Whether incentive structures produce the intended behaviors
- Whether any rational actor can extract value at the expense of system health
- Whether the staking and slashing parameters create stable or unstable equilibria
- Whether fee structures are well-designed or extractable
- Whether there are missing incentive mechanisms

Be critical. Identify real problems, not theoretical ones. Prioritize findings
by severity. Do not pad the report—if something is fine, say it's fine and move on.
```

Repeat this for each domain. Ask each expert to produce a structured report with:

- Findings ranked by severity (Critical / Moderate / Minor)
- Specific locations in the code or design where each problem exists
- Concrete recommendations, not vague suggestions
- Areas that are actually well-designed (so you don't fix things that aren't broken)

### Step 4: Consolidate Into a Research Document

Once you have feedback from each expert, ask the model to synthesize them into a consolidated findings document. This is not a summary — it is a working document you will hand to a coding agent.

**Example synthesis prompt**:

```
Here are evaluation reports from four domain experts reviewing this system.
Please produce a consolidated findings document that:

1. Deduplicates overlapping findings (noting when multiple experts flagged the same issue)
2. Flags conflicts between expert recommendations (where experts disagree)
3. Groups findings by area of the system (staking module, job market, governance, etc.)
4. Preserves the severity ratings
5. Retains the specific recommendations, not just the problem statements

The output will be used as input to a coding agent. It should be precise and
actionable, not narrative.
```

Save this document. It becomes your implementation specification for the next phase and part of the project's institutional memory. Store it in `/docs` alongside your architecture and invariant documents.

### Step 5: Generate an Implementation Plan

Now switch back to builder mode. Give the coding agent the consolidated findings document and ask it to produce a phased implementation plan. This maps directly to the [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md) workflow — the findings document becomes the input to the planning phase.

**Example prompt**:

```
Here is a technical findings report produced by a panel of domain experts
reviewing this codebase. Please read it carefully and produce an implementation
plan that:

1. Addresses all Critical findings before any Moderate findings
2. Groups related changes that should be implemented together
3. Identifies changes that are risky or require special care
4. Flags any recommendations that conflict with existing system invariants
   (do not resolve them—flag them for human review)
5. Breaks the work into phases with clear completion criteria

Do not begin implementation. Produce only the plan.
```

Review the plan before executing it. This is a human checkpoint. If the plan involves changes to system invariants — stop. That is a product decision, not an implementation detail.

### Step 6: Execute Through Your Normal Build Process

Once the plan is reviewed, execute it using your standard vibe coding workflow: roadmap → phased implementation → tests → bug hunts → checkpoint summaries.

The expert evaluation feeds into the process — it does not replace it.

---

## What Good Expert Feedback Looks Like

Good expert feedback is **specific, falsifiable, and tied to code or design decisions**. Weak feedback is abstract and unactionable.

**Weak finding**:
> "The staking mechanism could be improved."

**Strong finding**:
> "The slashing penalty is calculated as a flat percentage of staked tokens regardless of the severity or recurrence of the violation. This means a single small infraction carries the same cost as repeated gross non-performance. Rational actors will model the expected cost of slashing versus the expected profit of defection. At current parameters, defection is profitable for high-value jobs. Recommendation: implement a graduated slashing schedule with recidivism multipliers."

If you're getting weak findings, try these adjustments:

- Make the expert persona more specific (not "economist" but "mechanism design researcher specializing in staking protocols")
- Explicitly ask for concrete code or design locations
- Ask the expert to be adversarial: "You are trying to exploit this system. What do you do first?"
- Ask for findings in the format of a formal review, not a conversation

---

## Adversarial Personas Are Especially Useful

One of the highest-value variants of this technique is the adversarial persona: asking the model to act as someone trying to break, exploit, or game your system.

**Examples**:

- "You are an MEV bot operator. How do you extract value from this protocol?"
- "You are a malicious actor with 15% of the staked tokens. What attack surfaces exist?"
- "You are a user who wants to earn rewards without performing real work. What strategies do you try?"
- "You are a competing service trying to drain liquidity from this market. What are your options?"

Adversarial personas surface problems that benevolent expert reviewers miss, because they're optimizing for a different objective.

**Run at least one adversarial persona pass on any system with economic incentives, access control, or multi-party interactions.**

---

## Keeping the Findings Honest

LLMs are prone to sycophancy — the [Emotional Prompt Engineering guide](./EMOTIONAL_PROMPT_ENGINEERING.md#the-sycophancy-trap-agreement--quality) covers this in depth. An expert asked to review your system may produce an unrealistically balanced report. A few techniques counter this:

**Demand asymmetry**: Tell the expert their job is to find problems, not to assess the system holistically. "Assume I know the system works. Your job is to find the five most serious problems with it."

**Ask for a failure scenario**: "Describe in detail a realistic scenario where this system fails in a way that causes significant user harm or economic damage."

**Set a minimum finding count**: "Identify at least seven distinct issues. If you can't find seven real issues, the last few can be minor. But you must find seven."

**Ask for a severity distribution**: "I expect a mix of critical, moderate, and minor findings. If you return only minor findings, explain why nothing is critical or moderate."

These prompts counteract the tendency to produce glowing reviews with token criticisms appended.

---

## Applying This Beyond Economics

The expert panel technique is not specific to token economies. It maps to any domain where correctness has multiple dimensions.

| System Type | Useful Expert Personas |
|---|---|
| Real-time multiplayer | Network engineer, game designer, cheater |
| Authentication system | Security engineer, penetration tester, compliance auditor |
| Payment processing | Fraud analyst, accountant, regulator |
| ML pipeline | Statistician, data engineer, user impacted by model errors |
| Distributed database | Database internals engineer, network partition simulator |
| Healthcare application | Clinician, privacy officer, patient |
| Recommendation system | Economist (attention markets), ethicist, adversarial user |
| CLI tool | Power user, first-time user, accessibility expert |
| API platform | Consumer developer, security auditor, rate-limit exploiter |

The pattern is always the same: identify the dimensions of correctness, find experts who own those dimensions, run them separately, consolidate, plan, build.

---

## Integration with the Vibe Coding Workflow

This technique fits naturally at the end of major phases, before starting new ones:

- **After architecture is established** (before significant implementation): run a structural review panel to catch design problems early
- **After a major feature is complete** (before the next phase begins): run a domain expert panel on the completed module
- **Before production deployment**: run an adversarial panel focused on security and failure modes (complements the [After the Merge](./AFTER_THE_MERGE.md) pre-deployment checklist)
- **After significant growth** (the codebase has doubled in size): run a systems-level review

If a finding results in a change to your system invariants, document the change in `INVARIANTS.md` with the reason. Expert review is one of the few legitimate reasons to update invariants.

If findings surface bugs, run the [bug hunt prompts](../prompts/bug-hunt.md) on the affected areas. The expert panel identifies *categories* of problems; bug hunts find *specific instances* in the code.

---

## Summary

The expert panel technique adds a structured critique step to the vibe coding workflow. Instead of asking "what should I build next?", you periodically ask "what is wrong with what I've built so far?" — through the eyes of people who specialize in finding those specific problems.

The key steps:

1. Identify the expert domains relevant to your system
2. Feed each persona the full context
3. Run each expert in a separate prompt with specific evaluation criteria
4. Consolidate findings into a structured report
5. Generate a phased implementation plan from the findings
6. Execute through your normal build process

**The technique works because LLMs don't just generate code — they simulate reasoning.** A well-primed expert persona applies real domain knowledge to your specific system. The output is not generic advice; it is a targeted critique you can act on immediately.

**Treat every major phase of development as having two stages: build, then evaluate.** The evaluation stage is where you find the problems that would otherwise surface in production.

---

## Related Guides

- [Emotional Prompt Engineering](./EMOTIONAL_PROMPT_ENGINEERING.md) — Why persona framing works and how to avoid the sycophancy trap
- [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md) — The expert findings document feeds directly into the planning workflow
- [Code Review for AI](./CODE_REVIEW_AI.md) — Expert panel complements but does not replace code review
- [Anti-Patterns](./ANTI_PATTERNS.md) — Warning signs that the panel technique helps catch early
- [After the Merge](./AFTER_THE_MERGE.md) — Production readiness checks that pair with pre-deployment adversarial panels
- [Context Management](./CONTEXT_MANAGEMENT.md) — How to feed the right context to each expert persona
