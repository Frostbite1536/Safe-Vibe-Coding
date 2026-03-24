---
layout: default
title: Team Workflows
parent: Guides
nav_order: 15
description: "Patterns for teams using AI-assisted development together."
---

# Team Workflows: AI-Assisted Development at Scale

Individual vibe coding is straightforward — one developer, one AI, one session. Teams add dimensions that single-developer guides don't address: shared context, divergent AI sessions, conflicting conventions, ownership ambiguity, and the compounding risk of multiple people generating code that no single person fully understands.

This guide covers the patterns that make AI-assisted development work when more than one person is involved.

---

## The Core Team Problem

When one developer uses AI, the risk is local — they might introduce a bug, but they'll likely notice because they were there when it was written.

When a team uses AI, risks compound:

1. **Divergent conventions.** Two developers prompt the AI differently. One gets Express-style error handling, another gets Koa-style. Both work in isolation. Both ship. The codebase becomes inconsistent.

2. **Invisible assumptions.** Developer A's AI session decided that user IDs are UUIDs. Developer B's session assumed integers. Neither documented the decision. The bug appears three weeks later at the integration boundary.

3. **Ownership gaps.** When no one wrote the code, no one feels responsible for understanding it. Bugs in AI-generated code get punted between developers because "I didn't write that module."

4. **Context fragmentation.** Each developer has a different mental model of the system based on their conversations with the AI. No shared context document means no shared understanding.

Every pattern in this guide exists to address one of these four problems.

---

## Shared CLAUDE.md as Team Constitution

The `CLAUDE.md` file is the single most important team coordination tool for AI-assisted development. It's not just a preferences file — it's the team's shared understanding of how the codebase works, encoded in a format the AI can use.

### What Belongs in a Team CLAUDE.md

For team use, CLAUDE.md needs more than build commands and lint rules. It needs to encode the decisions that prevent divergence:

```markdown
# CLAUDE.md

## Architecture Decisions (Do Not Override)
- REST API, not GraphQL — decided 2025-01-15, not revisiting
- PostgreSQL with Prisma ORM — no raw SQL queries
- All IDs are UUIDs (string type), never integers
- Error responses use RFC 7807 format
- Pagination is cursor-based, never offset-based

## Naming Conventions
- Files: kebab-case (user-service.ts, not userService.ts)
- Classes: PascalCase
- Functions/variables: camelCase
- Database tables: snake_case plural (user_accounts, not UserAccount)
- Environment variables: SCREAMING_SNAKE_CASE

## Patterns to Use
- Repository pattern for data access
- Result type for operations that can fail (never return null as error)
- Dependency injection via constructor, not service locator
- Zod for runtime validation at API boundaries

## Patterns to Reject
- ❌ No default exports (use named exports only)
- ❌ No barrel files (index.ts re-exporting everything)
- ❌ No ORM models in API responses (always map to DTOs)
- ❌ No catch-all exception handlers without re-raising
```

### The CLAUDE.md Update Protocol

CLAUDE.md is only useful if it's maintained. Establish a team protocol:

1. **Every PR that introduces a new pattern** must update CLAUDE.md. If the pattern isn't documented, it will be contradicted by the next developer's AI session.
2. **Every PR review that catches a convention violation** should result in a CLAUDE.md update — not just a code fix. Fix the root cause (the AI doesn't know the rule) not just the symptom (the wrong code).
3. **Tag `@claude` in PR comments** to suggest CLAUDE.md updates. This keeps the update in the review flow rather than requiring a separate task.
4. **Review CLAUDE.md monthly.** Remove rules that no longer apply. Add rules for patterns that keep recurring. A stale CLAUDE.md is worse than none — it creates false confidence.

### Personal Overrides with .claude.local.md

Team members have individual preferences that shouldn't be in the shared CLAUDE.md:

```markdown
# .claude.local.md (gitignored)

## Current Work
I'm refactoring the payment module — don't suggest changes to
src/payments/ that conflict with the branch feature/payment-v2.

## Personal Preferences
- I prefer verbose variable names over abbreviations
- Show me the test first, then the implementation
- Use TypeScript strict mode explanations when I ask about types
```

This file stays local. It prevents one developer's style preferences from being imposed on the team.

---

## Code Ownership with AI

AI-generated code creates an ownership vacuum. When no one typed the code, no one feels accountable for understanding it. This leads to modules that everyone can use but nobody can debug.

### The Ownership Rule

**Whoever prompts the AI owns the output.** This means:

- You review it as if you wrote it by hand
- You can explain what it does and why
- You're the first person called when it breaks
- You update the tests when requirements change

This isn't about blame. It's about ensuring someone on the team has the context to debug each module when things go wrong.

### Practical Ownership Patterns

**CODEOWNERS for AI-generated modules.** Use GitHub's CODEOWNERS file to require review from the person who generated the module:

```
# CODEOWNERS
/src/auth/          @alice
/src/payments/      @bob
/src/notifications/ @carol
```

When the AI generates a change to `/src/auth/`, Alice reviews it — even if Dave prompted the AI. Alice has the context to know whether the change is safe.

**PR descriptions must include human verification.** The template from the [Version Control guide](./VERSION_CONTROL.md) already includes an "AI Assistance" section. For teams, enforce it:

```markdown
## AI Assistance
- What was AI-generated: [specific files/functions]
- What I verified manually: [specific checks performed]
- What I understand well: [parts I can explain]
- What I'm less confident about: [parts that need extra review]
```

The last line is the most important. It tells reviewers where to focus.

---

## Review Workflow for AI-Generated Code

Code review is already covered in [Code Review for AI](./CODE_REVIEW_AI.md) and [Setting Up AI Code Review](./CODE_REVIEW_SETUP.md). This section covers the team-specific dynamics.

### The Double-AI Problem

Developer A uses AI to write code. Developer B uses AI to review it. Neither human reads the code carefully. This is the most dangerous team anti-pattern with AI — the illusion of review without actual comprehension.

**Mitigation:**
- At least one human must read every changed function. Not skim — *read*.
- AI review supplements human review, never replaces it. The [Code Review guide](./CODE_REVIEW_AI.md#human-review-checkpoints-non-negotiable) is explicit: human review checkpoints are non-negotiable.
- Rotate reviewers. If the same two people always review each other's AI code, blind spots become shared blind spots.

### What Team Reviewers Should Focus On

Individual code review catches bugs. Team code review also catches *divergence*:

| Check | Why it matters for teams |
|-------|------------------------|
| Does this follow CLAUDE.md conventions? | Prevents style drift across developers |
| Does this duplicate existing functionality? | AI doesn't know what your teammate built last week |
| Does this match the architecture doc? | Different sessions may place code in different layers |
| Are the interfaces consistent with adjacent modules? | Cross-boundary contracts are where team-AI bugs live |
| Is the error handling style consistent? | AI produces different error patterns for different developers |

### REVIEW.md for Team-Specific Rules

The [Code Review guide](./CODE_REVIEW_AI.md#use-a-reviewmd-file-for-review-specific-rules) introduces the `REVIEW.md` convention. For teams, add team-specific rules:

```markdown
# REVIEW.md

## Team Review Rules

### Always Flag
- New dependencies added without justification in PR description
- New patterns that aren't documented in CLAUDE.md
- Changes to shared types without updating all consumers
- Database migrations that aren't backward-compatible

### Cross-Team Impact
- Changes to /src/shared/ require review from at least 2 team members
- API contract changes require consumer team notification
- Changes to CI/CD pipeline require team lead approval

### Skip in Review
- Formatting-only changes (handled by prettier/eslint)
- Test file organization (move tests, rename test files)
- Comment updates in AI-generated boilerplate
```

---

## Branching and Parallel Work

AI-assisted development is fast enough that merge conflicts become more frequent. Two developers can generate overlapping code in less time than it takes to communicate about it.

### Branch Discipline

- **One feature per branch, one developer per branch.** Don't share AI session branches. The developer who prompted the AI should be the only one pushing to that branch.
- **Short-lived branches.** AI generates code fast, so branches should merge fast. A branch open for a week accumulates drift. Target 1-2 days maximum.
- **Rebase before review.** AI-generated code on a stale branch is doubly risky — the AI didn't know about recent changes, and the developer may not notice conflicts during manual merge.

### Handling Merge Conflicts in AI Code

When AI-generated code conflicts with another developer's AI-generated code:

1. **Don't ask the AI to resolve it blindly.** The AI doesn't have context about either developer's intent.
2. **Read both versions.** Understand what each branch was trying to do.
3. **Pick the canonical convention.** If the conflict is stylistic (two valid approaches), pick one and update CLAUDE.md so it doesn't recur.
4. **Test the merge thoroughly.** Cross-boundary bugs are most likely in code that was merged from conflicting AI sessions.

### Parallel AI Sessions

Multiple developers working simultaneously can run into the problem described in [Context Management — Multi-LLM](./CONTEXT_MANAGEMENT.md#multi-llm-context-management): conversations making conflicting assumptions.

**Coordination patterns:**
- **Feature boundaries.** Divide work at module boundaries, not within modules. "You take auth, I take payments" is safe. "You take the auth controller, I take the auth middleware" is not — the AI sessions will make incompatible assumptions about the interface between them.
- **Interface-first development.** Before parallel implementation, agree on the interfaces (function signatures, API contracts, data types). Commit these as type definitions or interface files. Both developers' AI sessions can then reference these as constraints.
- **Sync points.** If two developers are working on adjacent modules, sync at the end of each day. Compare CLAUDE.md-level decisions: "Did your AI choose any conventions or patterns that mine should know about?"

---

## Onboarding New Team Members

A new developer joining an AI-assisted team needs a different onboarding than a traditional team. They need to understand not just the code, but the *AI workflow* that produced it.

### Onboarding Checklist

1. **Read CLAUDE.md completely.** Not skim — read. This is the team's shared mental model.
2. **Read ARCHITECTURE.md and INVARIANTS.md.** These are the constraints the AI should follow.
3. **Review 3-5 recent PRs.** Focus on the "AI Assistance" sections. Understand the team's prompting style and verification habits.
4. **Pair with an existing team member on an AI session.** Watch how they prompt, what they verify, and how they handle AI mistakes. This transfers tacit knowledge that no document captures.
5. **Make a small change with AI, get it reviewed.** Before doing anything significant, go through the full cycle: prompt, review, test, PR, team review. Get feedback on your process, not just your code.
6. **Set up personal `.claude.local.md`.** Note anything you learn during onboarding that isn't in the shared CLAUDE.md — then decide whether it should be added.

### What New Members Get Wrong

- **Trusting AI output without reading it.** Veterans have calibrated their skepticism. New members haven't. Pair programming is the fastest cure.
- **Ignoring CLAUDE.md.** New members often start prompting the AI their own way, producing code that doesn't match team conventions. CLAUDE.md exists to prevent this, but only if people use it.
- **Not understanding existing patterns.** The AI happily generates a second way to do something the team already does a specific way. New members should explore the codebase before generating new code, so the AI can build on what exists.

---

## Knowledge Sharing and Institutional Learning

AI-assisted teams have a unique opportunity: every mistake can be permanently fixed by updating CLAUDE.md. But this only works if the team has a culture of sharing learnings.

### The Mistake → Rule Pipeline

```
Developer hits a bug caused by AI
        ↓
Root cause: AI didn't know about [convention/constraint]
        ↓
Fix the bug
        ↓
Add rule to CLAUDE.md (or REVIEW.md)
        ↓
The bug class is eliminated for the entire team, forever
```

This is the compound learning loop described in the [Beginner Setup guide](./BEGINNER_SETUP.md#team-claudemd). Make it explicit. Celebrate CLAUDE.md updates in the same way you'd celebrate catching a production bug.

### Prompt Sharing

Keep the team's `/prompts` folder current:

- When a developer creates a prompt that works well, add it to `/prompts` (see the main guide's [Prompt Library section](../README.md#10-maintain-a-prompt-library-inside-the-codebase))
- When a prompt leads to a recurring mistake, retire it and document why
- Review the prompt library quarterly — remove prompts that are obsolete, update prompts that have drifted from current architecture

### Retrospectives for AI Workflow

Add an AI-specific section to your team retrospectives:

- **What AI patterns worked well this sprint?** (Share across the team)
- **What AI patterns caused problems?** (Update CLAUDE.md or REVIEW.md)
- **Did we duplicate effort because AI sessions diverged?** (Improve coordination)
- **Did any AI-generated code require significant rework after review?** (Adjust verification discipline)
- **Should any new CLAUDE.md rules be added?** (Continuous improvement)

---

## Scaling Considerations

### Small Teams (2-5 Developers)

- Shared CLAUDE.md is sufficient for coordination
- Informal sync ("hey, my AI chose X for that pattern") works
- Everyone reviews everyone's code
- One person maintains CLAUDE.md as a side responsibility

### Medium Teams (6-15 Developers)

- CLAUDE.md per module or per team area (use directory-level CLAUDE.md files)
- Designated reviewers per area (CODEOWNERS becomes important)
- Weekly sync on conventions and patterns
- REVIEW.md rules become more formal
- Someone explicitly owns CLAUDE.md maintenance

### Large Teams (15+)

- Architecture team governs shared conventions
- CLAUDE.md becomes a living document with change review (PR for CLAUDE.md changes)
- Automated checks for convention compliance (linters that enforce CLAUDE.md rules)
- Inner-source model: teams own modules, publish interfaces
- AI-generated code requires the same review rigor as hand-written code — no shortcuts for velocity
- Investment in shared tooling: custom prompts, custom slash commands, team-specific MCP servers

---

## Anti-Patterns in Team AI Development

### "The AI Wrote It, Not Me"

Refusing to own AI-generated code. This leads to orphan modules no one understands or maintains.

**Fix**: Whoever prompts owns the output. This is non-negotiable.

### "We All Use AI, So Reviews Are Optional"

The assumption that AI code is high-quality because the AI is "smart." AI makes systematic errors that only human review catches (see [Anti-Patterns](./ANTI_PATTERNS.md)).

**Fix**: AI-generated code requires *more* review discipline, not less. The developer may not have read every line the AI produced. The reviewer is the safety net.

### "Let's Each Set Up Our Own CLAUDE.md"

Multiple developers maintaining personal CLAUDE.md files with different conventions. The codebase reflects every developer's personal preferences.

**Fix**: One committed CLAUDE.md per project. Personal preferences go in `.claude.local.md` (gitignored). Team conventions go in the shared file.

### "AI Will Figure Out Our Conventions"

Not documenting conventions because "the AI can infer them from the codebase." The AI infers from whatever context it sees — which may be inconsistent, outdated, or too large to fit in context.

**Fix**: Explicit rules beat implicit conventions. If it matters, write it down in CLAUDE.md.

### "Move Fast, Review Later"

Multiple developers shipping AI-generated code without review because velocity is the priority. The codebase accumulates inconsistencies that are increasingly expensive to unify.

**Fix**: Short review cycles, not no review cycles. A 15-minute review prevents a 3-day cleanup.

---

## The Team Workflow Checklist

### Setup (Once)

- [ ] CLAUDE.md committed to repo root with architecture decisions, naming conventions, patterns, and anti-patterns
- [ ] REVIEW.md with team-specific review rules
- [ ] CODEOWNERS file mapping modules to responsible developers
- [ ] PR template with AI Assistance section
- [ ] `/prompts` folder with team-approved prompts
- [ ] `.claude.local.md` in `.gitignore`

### Every Sprint

- [ ] Review and update CLAUDE.md based on learnings
- [ ] Retire or update outdated prompts
- [ ] AI workflow section in retrospective
- [ ] Check for convention drift across modules

### Every PR

- [ ] AI Assistance section filled out honestly
- [ ] At least one human has read every changed function
- [ ] Changes follow CLAUDE.md conventions
- [ ] No duplication of existing functionality
- [ ] Cross-boundary interfaces are consistent
- [ ] New patterns are documented in CLAUDE.md

---

## Related Guides

- [Claude Code Setup — Team CLAUDE.md](./BEGINNER_SETUP.md#team-claudemd) — Setting up shared project context
- [Context Management — Multi-LLM](./CONTEXT_MANAGEMENT.md#multi-llm-context-management) — Coordinating parallel AI sessions
- [Code Review for AI](./CODE_REVIEW_AI.md) — Review discipline for AI-generated code
- [Setting Up AI Code Review](./CODE_REVIEW_SETUP.md) — Automated review pipelines
- [Version Control](./VERSION_CONTROL.md#collaboration-workflow) — PR templates and collaboration workflow
- [Anti-Patterns](./ANTI_PATTERNS.md) — Individual anti-patterns that compound at team scale
- [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md) — Structured planning for complex team projects
