---
layout: default
title: Plan-Driven Development
nav_order: 10
parent: Guides
description: "How to use detailed implementation plans to get reliable, auditable results from coding agents — from ideation through execution and bug audit."
permalink: /plan-driven-development
---

# Plan-Driven Development with Coding Agents

The fastest way to build something wrong is to skip the plan. The fastest way to build something right is to write the plan, audit the plan, then follow the plan.

This guide covers a workflow for human-agent paired development where the agent writes detailed implementation plans, the plans are audited for accuracy before a line of code is written, and the agent then follows its own plans to build. The result is faster, more reliable, and produces fewer bugs than "just start coding."

---

## Table of Contents

1. [Why Plans Work](#why-plans-work)
2. [The Full Workflow](#the-full-workflow)
3. [Phase 1: Ideation and Research](#phase-1-ideation-and-research)
4. [Phase 2: Plan Creation](#phase-2-plan-creation)
5. [Phase 3: Plan Audit](#phase-3-plan-audit)
6. [Phase 4: Prompt Sequencing (Large Projects)](#phase-4-prompt-sequencing-large-projects)
7. [Phase 5: Execution](#phase-5-execution)
8. [Phase 6: Code Audit](#phase-6-code-audit)
9. [Advanced Practices](#advanced-practices)
    - [When to Scrap and Replan](#when-to-scrap-and-replan)
    - [CLAUDE.md as Plan Accelerator](#claudemd-as-plan-accelerator)
    - [Parallel Research Agents](#parallel-research-agents)
    - [Plan Versioning](#plan-versioning)
10. [What Goes Wrong Without This](#what-goes-wrong-without-this)
11. [Templates](#templates)

---

## Why Plans Work

Coding agents are fast and tireless. They can produce hundreds of lines in minutes. But speed without direction produces code that needs to be rewritten — and rewriting costs more than planning.

Plans work because they:

- **Separate thinking from doing.** Design decisions made mid-implementation are worse than decisions made during planning. The agent is juggling syntax, types, imports, and edge cases while coding. During planning, it has full attention on architecture.
- **Create an auditable artifact.** You can review a plan in minutes. Reviewing 500 lines of code for design errors takes much longer and catches fewer issues.
- **Catch errors before they're embedded.** A wrong tool count in a plan is a one-line fix. A wrong tool count embedded in code, descriptions, tests, and documentation is a multi-file fix with regression risk.
- **Provide continuity across sessions.** If a session runs out of context or you need to start fresh, the plan document carries the full design forward. Without it, the next session has to re-derive everything.

---

## The Full Workflow

```text
Phase 1: Ideation
  Talk about what you want to build
  Research open source repos with similar ideas
  Brainstorm adaptations for your codebase

Phase 2: Plan Creation
  Agent writes detailed, multi-document implementation plan
  Plan includes file changes, data structures, code samples, constraints

Phase 3: Plan Audit
  Agent audits its own plan for accuracy
  Fix the 1-3+ bugs that are always there
  Human reviews the corrected plan

Phase 4: Prompt Sequencing (if project is large)
  Break plan into sequential prompts
  Each prompt is self-contained with enough context to execute

Phase 5: Execution
  Agent follows its own plan
  Build step by step, committing at natural milestones

Phase 6: Code Audit
  At least one thorough bug audit of the built code
  Agent reviews its own implementation as if someone else wrote it
```

---

## Phase 1: Ideation and Research

Start with a conversation, not a task. Describe what you want to build, why it matters, and what constraints exist. Let the agent ask questions.

### Using Open Source as a Starting Point

If an open source repo already implements something similar to what you need, share it with the agent early. This is one of the highest-value moves you can make during ideation.

**What to do:**
- Send the agent a link to the repo
- Ask it to evaluate the approach: what works, what doesn't, what's overengineered
- Brainstorm how the ideas apply to your codebase and constraints
- Identify what to adopt, what to adapt, and what to ignore

**Why this works:** The agent gets a concrete reference implementation instead of working from abstract requirements. It can see actual data structures, API shapes, and edge cases that the original authors discovered. This eliminates an entire class of "didn't think of that" bugs.

**What to watch for:** The agent may try to import the approach wholesale. Your codebase has different constraints, conventions, and scale. Push back when the borrowed design doesn't fit. The goal is inspiration and structural insight, not copy-paste.

### What Good Ideation Produces

By the end of this phase, you should have:
- A clear description of what you're building
- Key design decisions made (or explicitly deferred)
- An understanding of how this fits into the existing codebase
- Reference implementations identified (if any exist)

---

## Phase 2: Plan Creation

Ask the agent to produce a detailed, multi-document implementation plan. Be explicit about the audience: **this plan will be followed by a coding agent.** This changes the level of detail.

### What to Ask For

> "Create a detailed implementation plan for [feature]. The plan will be followed by a coding agent, so it needs to be precise enough that another agent can execute it without ambiguity. Include file paths, data structures, code samples for non-obvious parts, constraints, and the order of operations."

### What a Good Plan Contains

**1. Problem statement.** What's being solved and why. One paragraph.

**2. Design.** Data structures, API shapes, state management. Include actual type definitions, not prose descriptions. An agent implementing the plan needs to know the exact field names and types.

**3. Implementation steps.** Ordered list of changes with specific file paths. Each step should be independently committable. Include code samples for anything non-obvious — but don't write the full implementation in the plan. The plan shows structure and interfaces; the implementation fills in the logic.

**4. Constraints and invariants.** Rules that must not be violated. These are the most important part of the plan for preventing bugs during execution.

**5. Computed values.** If the plan references counts, sums, or derived numbers, show the computation. "The analyst preset contains 35 tools" is only useful if you can verify: core(3) + prediction(5) + feed(9) + ensemble(2) + memory(2) + provenance(4) + study(5) + reputation(5) = 35.

**6. Edge cases.** What happens at boundaries? What's the failure mode? What should error messages say?

**7. Testing strategy.** What tests need to be written and what they verify.

**8. Files changed.** A summary table of every file created or modified.

### Plan Anti-Patterns

- **Plans that describe what to build but not how.** "Add group support to the MCP server" is a goal, not a plan.
- **Plans without code samples.** If the data structures aren't specified, the implementing agent will invent them, and they'll be different from what you intended.
- **Plans with hardcoded computed values.** "This preset has 30 tools" without showing the arithmetic. These are always wrong.
- **Plans that skip constraints.** Without explicit invariants, the implementing agent will make reasonable-sounding decisions that violate your design intent.

---

## Phase 3: Plan Audit

This is the phase most people skip, and it's the one that saves the most time.

### The Rule: Plans Always Have Bugs

In practice, every implementation plan produced by a coding agent contains at least 1-3 errors. Common categories:

| Error Type | Example | How Often |
|-----------|---------|-----------|
| Wrong arithmetic | Preset count says 30, actual is 32 | Very common |
| Stale references | References a function/file that was renamed | Common |
| Missing interactions | Two subsystems that conflict when combined | Common |
| Wrong API assumptions | Assumes a library method exists or works differently | Occasional |
| Impossible sequences | Step 3 depends on step 5's output | Occasional |

### How to Audit

Ask the agent to audit its own plan:

> "Audit this implementation plan for accuracy. Verify all computed values against the source. Check that every referenced file, function, and API exists. Trace the full execution path from startup through normal operation. Fix all errors you find."

**Key instruction: "Fix all errors."** If you just ask the agent to "review" the plan, it may list issues without fixing them. Be explicit that it should both find and fix.

### What to Verify Yourself

The agent's self-audit catches most errors, but as the human you should verify:
- **Design direction.** Does this solve the right problem the right way?
- **Scope.** Is this building what you asked for, or has it grown?
- **Constraints.** Are the invariants correct and complete?
- **Integration points.** How does this interact with existing code?

You don't need to verify arithmetic or API spellings — that's what the audit step is for. Focus on judgment calls the agent can't make alone.

---

## Phase 4: Prompt Sequencing (Large Projects)

For projects that span multiple files and sessions, break the audited plan into sequential prompts. Each prompt is a self-contained task that a coding agent can execute in one session.

### When You Need This

- The plan has more than 5-6 implementation steps
- The work will span multiple sessions (context window limits)
- Different parts of the plan have different risk profiles
- You want to review intermediate results before continuing

### How to Create Prompts

Ask the agent:

> "Break this plan into sequential prompts that I can feed one at a time to a coding agent. Each prompt should include enough context that the agent can execute it without having seen the previous prompts. Include the relevant constraints, file paths, and design decisions in each prompt."

### Prompt Design Principles

**Each prompt is self-contained.** Include the relevant context from the plan directly in the prompt. Don't rely on "see the plan" — the executing agent may not have the plan in context.

**Each prompt produces a committable result.** At the end of each prompt, the code should compile and tests should pass. Don't split work mid-feature where the code is in a broken state.

**Earlier prompts create foundations.** Types, schemas, and data structures first. Business logic second. Integration and wiring last. This matches the natural dependency order.

**Include verification.** Each prompt should end with "verify by running X" — a test command, a type check, or a specific behavior to confirm.

---

## Phase 5: Execution

The agent follows its own plan (or the sequenced prompts). This is the implementation phase.

### How to Manage It

**Let the agent work.** If the plan is solid and audited, the agent should be able to execute without much intervention. Resist the urge to micro-manage implementation details that the plan already covers.

**Intervene on judgment calls.** When the agent encounters something the plan didn't anticipate, it needs your input. Watch for moments where it's making design decisions on the fly — those should have been in the plan.

**Commit at natural milestones.** Each implementation step from the plan is a good commit point. Don't let work accumulate without committing.

**Track progress.** On multi-step plans, keep track of which steps are complete. The agent's todo list helps, but your own awareness matters more.

### When to Deviate from the Plan

Plans aren't sacred. Deviate when:
- You discover a constraint the plan didn't anticipate
- A simpler approach becomes obvious during implementation
- A dependency doesn't work as the plan assumed

But deviate consciously. Update the plan document to reflect the change so it remains an accurate record.

---

## Phase 6: Code Audit

After implementation is complete, do at least one thorough bug audit. This is different from code review — it's specifically looking for the kinds of bugs that agents introduce.

### How to Run It

> "Thoroughly audit the recent changes. Trace the full execution path. Check for interactions between the new subsystems. Verify that all computed values match reality. Look for edge cases, dead code, and missing error handling."

### What Agent Audits Catch

Agent self-audits consistently find:
- **Subsystem interactions that break.** Each function works alone; together they fail. This is the most common class of bug in agent-written code.
- **Dead code and unused variables.** The agent's drafting process leaves artifacts.
- **Missing edge cases.** Happy path works; boundary conditions don't.
- **Hardcoded values that should be derived.** Constants that duplicate information from a source of truth.

### What Agent Audits Miss

- **Whether the design is right.** The agent can verify the code matches the plan. It can't tell you the plan was wrong.
- **Performance at scale.** Logic correctness doesn't imply runtime efficiency.
- **Security implications.** Unless explicitly asked, agents don't reason about attack surfaces.

For these, you need human review or specialized audit prompts (see the [Audit Findings guide](./AUDIT_FINDINGS.md)).

### The Human's Role in Audit

The most productive interventions during audit are short diagnostic questions:

- **"Should this be called?"** — Not "remove the unused variable" but "is there missing logic that should use this?"
- **"Should these be used?"** — Not "clean up the imports" but "did you forget to wire these in?"
- **"Should this be fixed?"** — Not accepting "pre-existing, not my problem" as a dismissal.

These questions force the agent to reason about intent rather than mechanically cleaning up symptoms. The difference between "remove unused variable" and "is the code incomplete?" is the difference between cosmetic cleanup and catching real bugs.

---

## Advanced Practices

### When to Scrap and Replan

Plans accumulate drift. Each deviation from the plan makes the remaining steps less reliable, because they were designed for a codebase state that no longer exists. At some point, patching the plan costs more than writing a new one.

**The rule of three:** If you've deviated from the plan on three or more steps, stop and evaluate the remaining steps. They were written assuming the first steps went as planned. With three deviations, the assumptions behind the remaining steps are probably wrong.

**Signs you need to replan:**
- You're making design decisions the plan doesn't cover, more than once
- The agent is working around constraints the plan didn't anticipate
- New steps are appearing that weren't in the plan
- You've discovered a fundamental assumption was wrong (e.g., an API doesn't work the way the plan expected)

**How to replan efficiently:** You don't start from scratch. Take the original plan, mark what was completed and what deviated, describe the current actual state of the codebase, and ask the agent to write a new plan for the remaining work starting from where you actually are — not where the old plan expected you to be.

> "The original plan has diverged from reality. Here's what was completed [list], here's what changed [list deviations], and here's the current state [describe]. Write a new plan for the remaining work that starts from this actual state."

**When to push through instead:** If the deviations are minor (renamed a variable, reordered two steps, used a slightly different API) and the remaining steps don't depend on the specific details that changed, keep going. The rule of three is about structural deviations, not cosmetic ones.

### CLAUDE.md as Plan Accelerator

The quality of an implementation plan is directly proportional to the quality of context the agent has about the codebase. A `CLAUDE.md` file (or equivalent project context document) is the single highest-leverage input to the planning phase.

**With a good CLAUDE.md, plans contain:**
- Real file paths, not guesses (`packages/server/src/services/botService.ts`, not `src/services/bot.ts`)
- Real conventions ("`AppError(code, message, statusCode)` for domain errors", not invented error patterns)
- Real constraints ("Prisma Decimal fields need `Number()` conversion", not discovered mid-implementation)
- Real testing patterns (`useTestPrisma()` helper, `createBot()` factory, not improvised test setup)

**Without a CLAUDE.md, the agent:**
- Guesses at file structure and gets it partially wrong
- Invents conventions that conflict with existing patterns
- Misses constraints that only become apparent during implementation
- Produces plans that require more audit corrections

**What to put in CLAUDE.md for better plans:**
- Architecture overview with actual package/directory structure
- Key commands (build, test, lint, migrate)
- Database and ORM patterns with gotchas
- Auth and middleware patterns
- Testing patterns and helpers
- Known invariants and constraints
- Error handling conventions

You don't need to document everything. Focus on the things an agent would get wrong without being told — the conventions that aren't obvious from reading one file.

**The compound effect:** Better context produces better plans. Better plans produce fewer audit corrections. Fewer corrections mean the implementing agent follows a more accurate plan. More accurate plans produce code with fewer bugs. The CLAUDE.md investment pays dividends at every phase of the workflow.

### Parallel Research Agents

During ideation, you often need to evaluate multiple approaches, repos, or libraries before committing to a direction. Doing this sequentially is slow. If your tooling supports it, send multiple research agents out in parallel.

**When to parallelize:**
- Evaluating 2-3 open source repos that solve similar problems
- Comparing library options (e.g., "evaluate BullMQ vs. Agenda vs. pg-boss for our job queue needs")
- Researching different architectural approaches simultaneously
- Gathering context from multiple parts of a large codebase

**How to structure parallel research:**

Give each agent a focused, independent question:

> **Agent 1:** "Evaluate [repo A]. Focus on: data model design, API surface, how they handle [specific concern]. Report what we should adopt, adapt, and ignore for our use case."
>
> **Agent 2:** "Evaluate [repo B]. Same questions as above."
>
> **Agent 3:** "Research how [specific pattern] is typically implemented in [our tech stack]. Find 2-3 approaches with trade-offs."

Then synthesize the results yourself or with a single agent:

> "Here are three research reports on [topic]. Synthesize these into a recommendation for our implementation. Our constraints are [list constraints]."

**Why this works better than sequential research:** Each agent gets the full context window for its research task. When you research sequentially in one session, earlier research fills the context window, leaving less room for later research. Parallel agents each start fresh with full capacity.

**What to watch for:** Parallel agents can't coordinate. If Agent 1's findings would change what you'd ask Agent 2, you need sequential research instead. Use parallel for independent questions, sequential for dependent ones.

### Plan Versioning

Save the plan before and after each audit. The diff between versions is a valuable artifact.

**What plan diffs tell you:**

- **Error frequency by category.** If arithmetic errors dominate, you know to double-check computed values in future plans before auditing. If stale references dominate, the codebase is changing faster than the agent's context reflects.
- **Model calibration.** Some models produce plans that need 1-2 fixes. Others need 5-6. Knowing the typical error rate for your model and project type helps you gauge how much trust to place in an unaudited plan.
- **Project complexity signal.** Plans for well-documented codebases (with good CLAUDE.md files) have fewer audit corrections. Plans for unfamiliar codebases have more. The correction count is a proxy for how well the agent understands the project.
- **Recurring blind spots.** If the same type of error appears across multiple plans, it's a systematic blind spot. You can address it by adding the relevant information to your CLAUDE.md or including specific audit instructions.

**How to version:**

The simplest approach: before running the audit, copy the plan to a versioned filename.

```text
feature-plan-v1-pre-audit.md    # Original plan
feature-plan-v2-post-audit.md   # After agent self-audit
feature-plan-v3-post-review.md  # After human review (if changes were made)
```

Or use git commits if the plan lives in your repo:

```bash
git add docs/plans/feature-plan.md
git commit -m "docs: feature plan v1 (pre-audit)"
# ... run audit ...
git add docs/plans/feature-plan.md
git commit -m "docs: feature plan v2 (post-audit, fixed 3 errors)"
```

**Over time, this builds institutional knowledge.** You'll know which types of features produce clean plans and which types always need heavy auditing. You'll know which parts of your codebase the agent understands well and which parts confuse it. This knowledge directly improves your planning prompts and CLAUDE.md documentation.

---

## What Goes Wrong Without This

### Without plans: "stream of consciousness" coding

The agent starts writing code immediately. Design decisions are made mid-implementation, embedded in code rather than documented. When problems emerge, the agent patches rather than redesigns. The result is code that works but is structurally unsound — and nobody can explain why it's structured the way it is, because the reasoning was never recorded.

### Without plan audits: embedded errors

The plan says "this preset has 30 tools." The agent implements it as 30. The actual count is 32. Now the wrong number is in the code, the description strings, the documentation, and the test assertions. A one-line plan fix became a multi-file bug that's hard to find because the code is internally consistent — it's just wrong.

### Without code audits: interaction bugs

The agent builds two subsystems that each work correctly. The first populates a registry with all items. The second disables items not on a whitelist. Neither system knows about items that should be exempt from both. The result: critical items are disabled. Each function passes its unit tests. The system is broken.

### Without prompt sequencing: context collapse

On large projects, the agent runs out of context window mid-implementation. It starts forgetting earlier design decisions. It re-derives solutions that contradict what it built 2,000 lines ago. The code becomes internally inconsistent because the agent literally cannot see all of it at once.

---

## Templates

### Plan Request Prompt

```
Create a detailed implementation plan for [feature description].

This plan will be followed by a coding agent, so it needs to be precise
enough to execute without ambiguity. Include:
- Problem statement (1 paragraph)
- Design: data structures, types, API shapes (show actual definitions)
- Implementation steps in order, with specific file paths
- Code samples for non-obvious parts
- Constraints and invariants that must not be violated
- Computed values with arithmetic shown
- Edge cases and error handling
- Testing strategy
- Summary table of files changed
```

### Plan Audit Prompt

```
Audit this implementation plan for accuracy. Fix all errors discovered.

Specifically:
- Verify all computed values (counts, sums) against the actual source
- Check that every referenced file, function, and API actually exists
- Trace the full execution path from startup through normal operation
- Identify interactions between subsystems that could conflict
- Verify the implementation order (no step depends on a later step's output)
- Check library/SDK API assumptions against actual type definitions
```

### Prompt Sequencing Request

```
Break this audited plan into sequential prompts that I can feed one at a
time to a coding agent. Requirements:
- Each prompt is self-contained (includes relevant context, constraints,
  file paths, and design decisions — don't rely on "see the plan")
- Each prompt produces a committable result (code compiles, tests pass)
- Earlier prompts create foundations (types, schemas) before logic
- Each prompt ends with a verification step
- Include the constraint/invariant section in every prompt where relevant
```

### Code Audit Prompt

```
Thoroughly audit the recent changes. This is a bug hunt, not a code review.

- Trace the full execution path from startup through normal operation
- Check interactions between new subsystems (each may work alone but
  fail together)
- Verify all computed values match reality
- Look for: dead code, unused variables, missing edge cases, hardcoded
  values that should be derived, subsystems that can disable or conflict
  with each other
- For every issue found: fix it, don't just report it
```

### Open Source Research Prompt

```
I'm planning to implement [feature description]. This repo has a similar
approach: [link to repo]

Please evaluate:
- What does this implementation do well?
- What's overengineered or unnecessary for our use case?
- What data structures, API shapes, or patterns should we adopt?
- What should we adapt (and how) vs. ignore?
- What edge cases did the original authors handle that we should consider?

Our constraints: [list your codebase constraints, scale, tech stack]
```
