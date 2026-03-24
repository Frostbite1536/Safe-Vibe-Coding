---
layout: default
title: Legacy Codebases
parent: Guides
nav_order: 16
description: "Introducing AI-assisted development into existing, mature codebases."
---

# Legacy Codebases: AI-Assisted Development on Existing Code

Most vibe coding guides assume you're starting from scratch. Most real work happens in codebases that already exist — with established patterns, missing tests, inconsistent conventions, and years of accumulated decisions that no one fully remembers.

AI is extraordinarily useful in legacy codebases. It can read code faster than any human, explain unfamiliar patterns, generate tests for untested modules, and perform tedious migrations. But it's also more dangerous here than in greenfield projects, because legacy code has implicit rules that aren't written down anywhere. The AI doesn't know them. It will confidently break them.

This guide covers how to introduce AI-assisted development into existing codebases without making things worse.

---

## Before You Start: Assess What You Have

Before using AI on a legacy codebase, understand the terrain. The AI can help with this assessment, but you need to direct it.

### The Codebase Survey

Ask the AI to analyze the codebase and answer these questions. Provide it with the directory structure and key files — don't dump the whole thing.

```
Review this codebase and report:

1. Architecture: What patterns are used? (MVC, microservices, monolith, etc.)
2. Conventions: What naming conventions, file organization, and coding styles are present? Are they consistent?
3. Test coverage: Where do tests exist? Where are the gaps?
4. Dependencies: How many? How old? Are any deprecated or unmaintained?
5. Configuration: How is config managed? Are there environment-specific settings?
6. Build system: What tools? Any custom scripts or unusual steps?
7. Inconsistencies: Where do different parts of the codebase disagree with each other?

Be specific. Cite file paths and line numbers.
```

This survey becomes the foundation for your CLAUDE.md. Without it, every AI session starts from zero understanding.

### Building CLAUDE.md From an Existing Codebase

Greenfield projects write CLAUDE.md before the code. Legacy projects extract CLAUDE.md *from* the code. The structure is the same (see [Beginner Setup — Advanced CLAUDE.md](./BEGINNER_SETUP.md#advanced-claudemd-structure)), but the process is different:

1. **Run the codebase survey** above. Use the AI's findings as a starting point.
2. **Document the conventions you find**, not the conventions you wish existed. If the codebase uses both camelCase and snake_case, document that — don't pretend it's consistent.
3. **Document the target conventions.** Separately note which patterns new code should follow, so the AI doesn't perpetuate inconsistencies.
4. **List the danger zones.** Modules that are fragile, poorly tested, or poorly understood. Tell the AI explicitly: "Do not modify files in `/src/billing/` without explicit instruction — this module is untested and business-critical."

```markdown
# CLAUDE.md

## Current State (What Exists)
- Mix of Express 4 and Koa routes — Express for API, Koa for webhooks
- Database access: raw SQL in older modules, Prisma in newer modules
- Tests exist for /src/api/ and /src/auth/ only
- No tests for /src/billing/, /src/notifications/, /src/legacy/

## Target State (What New Code Should Follow)
- All new routes: Express 4 with validation middleware
- All new database access: Prisma ORM, no raw SQL
- All new code must have tests

## Danger Zones (Do Not Modify Without Explicit Instruction)
- /src/billing/ — untested, processes real payments
- /src/legacy/import-engine.js — 3,000-line file, works but nobody understands it
- /config/production.json — deploy config, wrong change = outage
```

### Understanding Before Changing

The single most important rule for AI + legacy code:

**Never ask the AI to change code you haven't first asked it to explain.**

This serves two purposes:
1. You learn what the code does before deciding whether to change it
2. The AI's explanation reveals its understanding — if the explanation is wrong, its changes will be wrong too

```
Explain what this function does, including:
- Its inputs and outputs
- Side effects (database writes, external calls, file operations)
- Edge cases it handles (and any it doesn't)
- Assumptions it makes about the state of the system
- Why it might have been written this way

Do not suggest changes. Just explain.
```

If the AI's explanation doesn't match your understanding of the system, don't proceed with changes until you've resolved the discrepancy.

---

## Adding Tests to Untested Code

Legacy codebases often lack tests. AI is excellent at generating tests for existing code — but only if you direct it carefully.

### The Test-First-Then-Change Rule

The [Refactoring guide](./REFACTORING_WITH_AI.md#dont-refactor-without-tests) states it plainly: don't refactor without tests. For legacy code, this means every change starts with tests for the *existing* behavior, not the desired behavior.

**The sequence:**
1. Ask AI to explain the current code (see above)
2. Ask AI to write tests that capture current behavior
3. Run the tests — they must pass against the existing code
4. *Then* make changes
5. Run the tests again — they must still pass

### Generating Tests for Legacy Code

```
Write tests for [function/module] that capture its CURRENT behavior.

Requirements:
- Test the happy path with realistic inputs
- Test edge cases: null/undefined inputs, empty collections, boundary values
- Test error handling: what happens when [dependency] fails?
- Test side effects: verify database writes, external calls, events emitted
- Do NOT test idealized behavior — test what the code actually does,
  including any quirks or bugs you notice

If you notice behavior that seems like a bug, still write a test for it
and add a comment: "// NOTE: Possible bug — [description]. Preserving
current behavior."

Use [test framework] and follow the patterns in [existing test file].
```

The key instruction is: **test what the code does, not what you think it should do.** AI has a strong tendency to "fix" behavior while writing tests, which means the tests pass but don't actually capture the code's real behavior. When you later change the code, you've lost your safety net.

### Characterization Tests

For particularly complex or opaque legacy code, use characterization tests — tests that simply record the output for given inputs, without asserting that the output is "correct":

```
Write characterization tests for [function]. For each test:
1. Call the function with specific inputs
2. Record the actual output
3. Assert the output matches

These tests document current behavior, not correct behavior.
The goal is to detect any change in behavior, intentional or not.

Inputs to test:
- [typical input 1]
- [typical input 2]
- [edge case 1]
- [empty/null/missing input]
```

Characterization tests aren't pretty, but they're the fastest way to get a safety net around untested code.

---

## Safe Modification Patterns

### The Expansion Pattern: Add, Don't Change

The safest way to modify legacy code with AI is to avoid modifying it at all. Instead, add new code alongside it:

1. **New endpoint alongside old endpoint.** Build the v2 endpoint next to v1. Route new clients to v2. Leave v1 untouched.
2. **New function alongside old function.** Write `processOrderV2()` that handles the new requirements. Callers migrate one at a time. Delete the old function when no callers remain.
3. **Wrapper around legacy code.** Build a clean interface that delegates to the legacy code internally. New consumers use the wrapper. The legacy code is isolated.

This pattern avoids the biggest AI-legacy risk: changing code you don't fully understand.

### The Strangler Fig Pattern

For larger migrations, use the strangler fig approach:

```
Phase 1: Build new implementation alongside legacy code
Phase 2: Route new traffic/callers to new implementation
Phase 3: Migrate existing callers one at a time
Phase 4: Remove legacy code when no callers remain
```

AI is well-suited to phases 1 and 2 — building new code with clear requirements. Phase 3 requires human judgment about migration order and risk. Phase 4 is straightforward but needs careful verification that no callers remain.

**What to tell the AI:**

```
We are using the strangler fig pattern to replace [legacy module].

The new implementation is in [path]. The legacy implementation is in [path].

Rules:
- Do NOT modify the legacy implementation
- The new implementation must produce identical outputs for identical inputs
- Add a compatibility test that runs the same inputs through both
  implementations and asserts identical results
- New callers should use the new implementation
- Existing callers stay on legacy until explicitly migrated
```

### The Seam Pattern: Find Natural Boundaries

Legacy code often has natural "seams" — places where you can insert new behavior without modifying existing code. Common seams:

- **Function parameters.** Add an optional parameter with a default that preserves current behavior.
- **Configuration.** Add a config flag that enables new behavior while defaulting to old.
- **Interface implementations.** If the code uses interfaces (or duck typing), implement a new version.
- **Event hooks.** If the code emits events, add a new listener rather than modifying the emitter.

Ask the AI to identify seams:

```
I need to add [new behavior] to [module]. Identify the natural seams
where I can introduce this change with minimal modification to existing
code. For each seam, explain:
- Where it is (file and line)
- What I'd add
- What existing code stays unchanged
- What could go wrong
```

---

## Migration Strategies

### Incremental Migration with AI

AI excels at repetitive, mechanical migrations: converting class components to functional components, callbacks to async/await, one ORM to another, one test framework to another. But the [Refactoring guide](./REFACTORING_WITH_AI.md#failure-mode-3-lost-error-context) warns that volume makes review impractical.

**The safe migration approach:**

1. **Migrate one file manually** (or with AI, carefully reviewed). This establishes the pattern.
2. **Document the migration pattern** in CLAUDE.md: "When converting from X to Y, follow this exact structure."
3. **Migrate files in small batches** (3-5 at a time). Review each batch. Run tests.
4. **Don't mix migration with feature work.** A commit should either migrate or add features, never both. This makes rollback possible.

### Database Migrations in Legacy Systems

AI-generated database migrations are high-risk in legacy systems because:

- The AI doesn't know what data exists in production
- Legacy schemas often have implicit constraints (not enforced by the database but assumed by the code)
- Migration rollback is harder when production data has been transformed

**Rules for AI-generated migrations:**

- [ ] Always generate both `up` and `down` migrations
- [ ] Test on a copy of production data, not an empty database
- [ ] New columns must be nullable or have defaults (see [After the Merge — Database Rollback](./AFTER_THE_MERGE.md#database-rollback-compatibility))
- [ ] Never `DROP` anything in the same deploy that stops using it
- [ ] Have the AI list every code path that reads or writes the affected tables before generating the migration

```
Before writing the migration, list every file that reads from or writes
to the [table_name] table. For each file, explain what columns it
accesses and what assumptions it makes about the data.
```

### Dependency Upgrades

AI is useful for dependency upgrades in legacy codebases — it can read changelogs, identify breaking changes, and update call sites. But review the [Dependency Safety guide](./DEPENDENCY_SAFETY.md) first.

**The upgrade process:**

1. **One dependency at a time.** Never upgrade multiple dependencies in the same commit.
2. **Ask the AI what changed:** "What are the breaking changes between [package] v2.3 and v4.1?"
3. **Have the AI identify all usage sites:** "Find every file that imports from [package] and list what APIs they use."
4. **Make the upgrade.** Let the AI update the call sites.
5. **Run all tests.** If tests are sparse, add characterization tests first (see above).
6. **Test manually for the specific breaking changes** the AI identified in step 2.

---

## Working with Large Files

Legacy codebases often contain large files that exceed the AI's ability to reason about effectively. The [main guide](../README.md#8-favor-modularity-as-a-first-class-constraint) recommends keeping files under ~1,500 lines. Legacy code regularly exceeds this.

### Reading Large Files with AI

Don't paste a 5,000-line file and ask the AI to "review it." Instead:

1. **Ask for a structural overview first:**
   ```
   Read [file] and describe its structure:
   - What classes/functions does it contain?
   - What are the main responsibilities?
   - What are the dependencies (imports)?
   - Where are the natural boundaries between responsibilities?

   Don't explain every function. Give me the high-level map.
   ```

2. **Then zoom in on specific sections:**
   ```
   Explain lines 200-350 of [file] in detail. What does this section do?
   ```

3. **Ask about specific behaviors:**
   ```
   In [file], trace what happens when [specific input/event] occurs.
   Which functions are involved and in what order?
   ```

### Splitting Large Files

If you need to split a large legacy file, this is a high-risk refactoring operation (see [Refactoring with AI — Risk Spectrum](./REFACTORING_WITH_AI.md#the-risk-spectrum)). The approach:

1. **Write characterization tests** for the file's public interface
2. **Have the AI propose a split plan** — which functions move to which new files
3. **Review the plan for dependency issues** — circular imports, shared state, initialization order
4. **Execute one extraction at a time** — move one group of functions, run tests, commit
5. **Don't change behavior during the split** — extract only, refactor later

---

## The Legacy Code CLAUDE.md Template

```markdown
# CLAUDE.md

## Project Overview
[What this project does, who uses it, how long it's been in development]

## Current State
### Architecture
[Actual architecture, not aspirational]

### Conventions (Existing)
[What conventions exist in the code NOW, even if inconsistent]
- [Area A uses pattern X]
- [Area B uses pattern Y]
- [Newer code uses Z — this is the preferred pattern going forward]

### Test Coverage
[Where tests exist and where they don't]
- Tested: [list modules/areas]
- Untested: [list modules/areas]
- Partially tested: [list modules/areas with notes on what's covered]

### Known Technical Debt
[Major issues the team knows about but hasn't fixed]

## Target Conventions (New Code)
[What new code should look like — this is what the AI should follow]

## Danger Zones
[Areas the AI must not modify without explicit instruction]
- [path] — [reason: untested, business-critical, fragile, etc.]

## Migration In Progress
[Any ongoing migrations the AI should be aware of]
- [migration description] — [current state, what's done, what remains]

## Common Tasks
### Adding a Feature
[Step-by-step for the most common type of change]

### Bug Fixes
[How to approach bug fixes in this codebase]

### Adding Tests to Untested Code
1. Read and explain the code first
2. Write characterization tests that pass against current behavior
3. Get tests reviewed before making any changes

## Commands
[Build, test, lint, migrate — whatever developers need to run]
```

---

## Anti-Patterns for AI + Legacy Code

### "Let the AI Rewrite It"

Asking the AI to rewrite a legacy module from scratch. The rewrite looks cleaner but misses edge cases the legacy code handled — edge cases that exist because of production bugs discovered over years.

**Fix**: Incremental modification with tests. The legacy code's ugliness often encodes important behavior.

### "The AI Understands the Whole System"

Assuming the AI can reason about the entire codebase at once. It can't — it sees what you put in context. In a legacy codebase with implicit contracts and undocumented dependencies, the AI's understanding is always partial.

**Fix**: Always ask the AI to identify what it *doesn't* know. "What assumptions are you making about code you haven't seen?"

### "Tests Will Catch Everything"

Over-relying on existing tests when making AI-generated changes. Legacy test suites often have gaps — they test the happy path but miss edge cases. The AI's changes may pass all tests while still breaking production behavior.

**Fix**: Add characterization tests before making changes. Don't trust existing tests alone — they were written for a different version of the code.

### "Quick Modernization"

Using AI to modernize the codebase in one pass: updating syntax, replacing patterns, upgrading dependencies all at once. Each individual change might be fine, but the combination is unreviable.

**Fix**: One type of change at a time. Separate commits for separate concerns. Migrate in batches.

### "The AI Can Figure Out the Implicit Contracts"

Not documenting the implicit contracts between legacy modules because "the AI can infer them from the code." The AI infers based on code it can see — it can't see the conversation from 2019 where two developers agreed that a field would always be populated.

**Fix**: Document contracts as you discover them. Add them to CLAUDE.md. Every implicit contract you make explicit prevents a future AI-generated bug.

---

## Summary

| Activity | Key rule | Why |
|----------|---------|-----|
| Assessment | Survey before changing | You can't direct AI without understanding the terrain |
| CLAUDE.md | Document reality, not aspirations | AI that follows wrong conventions is worse than AI with no guidance |
| Testing | Test current behavior first | Tests are your safety net — build it before you walk the wire |
| Modification | Add alongside, don't rewrite | Expansion is safer than replacement |
| Migration | One change type, small batches | Volume defeats review discipline |
| Large files | Structural overview, then zoom in | AI can't reason about 5,000 lines at once |
| Contracts | Document what you discover | Every implicit contract made explicit prevents a future bug |

Legacy codebases are where AI assistance provides the highest leverage — and where undisciplined AI usage causes the most damage. The difference is preparation: understand the code, write tests, document the rules, change incrementally. There are no shortcuts.

---

## Related Guides

- [Refactoring with AI](./REFACTORING_WITH_AI.md) — The incremental method, failure modes, and when not to refactor
- [Context Management](./CONTEXT_MANAGEMENT.md) — Managing AI context across sessions with existing codebases
- [Code Review for AI](./CODE_REVIEW_AI.md) — Reviewing AI-generated changes, including cross-boundary checks
- [Anti-Patterns](./ANTI_PATTERNS.md) — Warning signs that apply doubly to legacy code
- [After the Merge](./AFTER_THE_MERGE.md) — Production readiness, especially database migration safety
- [Dependency Safety](./DEPENDENCY_SAFETY.md) — Evaluating and upgrading dependencies safely
- [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md) — Structured planning for complex changes to existing systems
