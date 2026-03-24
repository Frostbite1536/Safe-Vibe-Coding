---
layout: default
title: Refactoring with AI
nav_order: 12
parent: Guides
description: "How to refactor safely with AI assistance — incremental strategies, verification discipline, and the failure modes that turn a cleanup into a rewrite."
permalink: /refactoring-with-ai
---

# Refactoring with AI: Changing Code Without Breaking It

Refactoring is one of the most common things you'll ask an AI to do. It's also one of the most dangerous. The AI will happily restructure your entire codebase in minutes — and introduce subtle behavioral changes that no test catches because the tests were written for the old structure.

This guide covers how to refactor safely with AI, when refactoring is low-risk vs. high-risk, what goes wrong when the AI refactors without discipline, and the verification habits that keep a cleanup from becoming a rewrite.

---

## Table of Contents

1. [Why AI Refactoring Is Different](#why-ai-refactoring-is-different)
2. [The Risk Spectrum](#the-risk-spectrum)
3. [The Incremental Method](#the-incremental-method)
4. [Verification Between Steps](#verification-between-steps)
5. [What the AI Gets Wrong During Refactoring](#what-the-ai-gets-wrong-during-refactoring)
6. [Refactoring Patterns That Work](#refactoring-patterns-that-work)
7. [Refactoring Patterns That Don't](#refactoring-patterns-that-dont)
8. [The Scope Problem](#the-scope-problem)
9. [When Not to Refactor with AI](#when-not-to-refactor-with-ai)
10. [Prompting for Safe Refactoring](#prompting-for-safe-refactoring)
11. [Checklist](#checklist)

---

## Why AI Refactoring Is Different

When a human refactors, they hold the *intent* of the code in their head. They understand why a condition exists, what edge case a branch handles, why two seemingly identical blocks have a subtle difference. They refactor around these details.

An AI refactors *structurally*. It sees patterns, identifies what looks like duplication, recognizes extract-method opportunities, and applies transformations. It does this quickly and confidently. But it doesn't understand intent the way the person who wrote (or lived with) the code does.

This creates a specific failure mode: **the refactored code looks cleaner, passes the same tests, and has a different behavior at the edges.** The edges are exactly where bugs live, and exactly what refactoring is most likely to disturb.

The core tension:
- AI is excellent at mechanical refactoring (renaming, extracting, reorganizing)
- AI is poor at judgment-heavy refactoring (simplifying logic, changing abstractions, merging behaviors)
- Most real refactoring involves both

---

## The Risk Spectrum

Not all refactoring carries the same risk. Before starting, identify where your refactor falls.

### Low Risk

These are mechanical transformations that don't change logic:

| Refactoring | Why it's safe |
|------------|---------------|
| Renaming variables/functions | No logic change |
| Extracting a function (pure logic, no side effects) | Behavior preserved by definition |
| Moving a file/module | Import changes only |
| Removing dead code | No callers means no behavior change |
| Reformatting / style changes | Cosmetic only |
| Adding types to untyped code | No runtime behavior change |

**For low-risk refactoring, the AI is excellent.** Let it work with minimal supervision.

### Medium Risk

These change structure in ways that could affect behavior:

| Refactoring | What can go wrong |
|------------|------------------|
| Extracting a class from a large function | State management changes, execution order shifts |
| Splitting a file into modules | Circular dependencies, initialization order, lost shared state |
| Replacing conditionals with polymorphism | Edge cases in the switch/if-else that don't map cleanly to classes |
| Changing data structures | Callers that depend on the old structure's properties |
| Consolidating duplicate code | The "duplicates" had subtle differences for a reason |

**For medium-risk refactoring, use the incremental method (below). Verify after each step.**

### High Risk

These change abstractions, contracts, or assumptions:

| Refactoring | What can go wrong |
|------------|------------------|
| Changing a public API's signature | Every caller needs updating; missed callers break silently |
| Replacing a library with another | API surface differences, edge case handling differences |
| Rewriting a core algorithm | Correctness at boundaries, performance characteristics |
| Merging two systems into one | Each had different assumptions that conflict |
| Changing error handling strategy | Callers that catch specific errors stop working |

**For high-risk refactoring, plan first.** Use the [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md) workflow. Don't let the AI start coding until the plan is audited.

---

## The Incremental Method

The single most important practice for safe AI refactoring: **never refactor more than one thing at a time.**

### The Process

```
1. Pick ONE refactoring operation
2. Tell the AI to make ONLY that change
3. Run tests
4. Review the diff
5. Commit
6. Repeat
```

### Why This Works

When a refactoring introduces a bug and it was the only change in the commit, you know exactly where the bug came from. When five refactoring steps are combined into one commit, finding the source of a regression becomes archaeology.

### Why This Feels Slow

It isn't. The AI is fast — each individual step takes seconds. What takes time is debugging a large refactoring that broke something three steps ago and you can't tell which step caused it. The incremental method trades a small amount of overhead per step for a massive reduction in debugging time.

### Example: Splitting a God File

Instead of asking the AI to split a 2,000-line file into modules all at once:

```
Step 1: Extract type definitions into types.ts
  → Run tests → Review diff → Commit

Step 2: Extract pure utility functions into utils.ts
  → Run tests → Review diff → Commit

Step 3: Extract data access functions into data.ts
  → Run tests → Review diff → Commit

Step 4: Extract validation logic into validation.ts
  → Run tests → Review diff → Commit

Step 5: What remains is the core module — review and clean up
  → Run tests → Review diff → Commit
```

Each step is safe, reversible, and independently verifiable. If step 3 breaks something, you revert one commit — not the entire refactoring.

---

## Verification Between Steps

Running tests after each step is necessary but not sufficient. Tests only verify what they cover, and AI-generated code often has coverage gaps at exactly the boundaries that refactoring disturbs.

### The Three Verification Layers

**Layer 1: Automated tests.** Run the full test suite. This catches outright breakage.

**Layer 2: Diff review.** Read every line of the diff. This catches behavioral changes the tests don't cover. Specifically look for:
- Conditions that were reordered (short-circuit evaluation changes)
- Default values that changed or disappeared
- Error messages that changed (callers may parse them)
- Return types that shifted (e.g., returning `undefined` where it used to return `null`)
- Side effects that moved (logging, analytics, cache writes)

**Layer 3: Manual spot-check.** For medium and high-risk refactoring, manually test the specific behavior the refactoring touches. Automated tests tell you what still works. Manual testing tells you whether the thing you changed still *feels* right.

### When to Skip Layers

- **Low-risk refactoring (rename, move):** Layer 1 is sufficient.
- **Medium-risk refactoring (extract, split):** Layers 1 + 2.
- **High-risk refactoring (rewrite, merge, API change):** All three layers.

---

## What the AI Gets Wrong During Refactoring

These are the specific failure modes that show up when AI refactors code. They're not theoretical — they're the bugs you'll actually encounter.

### 1. Collapsing intentional duplication

Two blocks of code look identical. The AI extracts them into a shared function. But one block is for user-facing errors and the other is for internal logging — they just happen to look the same right now. When requirements change (and they will), you need to modify them independently. Now they're coupled.

**How to catch it:** When the AI extracts "duplicate" code, ask yourself: *do these things change for the same reason?* If not, the duplication is intentional. Leave it.

### 2. Changing execution order

The AI reorders operations during refactoring — moving a variable assignment, reordering function calls, restructuring a pipeline. If any of those operations have side effects, the order matters.

**How to catch it:** In your diff review, pay special attention to any code that moved *position* within a function, not just code that changed content. Side effects (database writes, API calls, cache invalidation, event emission) are order-dependent.

### 3. Losing error context

The original code catches errors at each step and adds context: "failed while processing user X." The AI refactors the steps into a loop or a pipeline and wraps the whole thing in a single try/catch. The error still gets caught, but the context — which step, which item — is gone.

**How to catch it:** Search the diff for removed `catch` blocks and error handling. If error handling shrank during a refactoring, that's a red flag. Ask the AI: "Did we lose any error context in this refactoring?"

### 4. Widening scope when extracting

You ask the AI to extract a function. It extracts the function and then "helpfully" converts three other call sites to use the new function. Those other call sites may have had slightly different behavior — an extra null check, a different default, a logging call. The AI normalizes them all to the extracted version.

**How to catch it:** Compare the diff size to what you expected. If you asked for one extraction and the diff touches six files, the AI widened the scope. Revert and be more specific.

### 5. Changing public contracts silently

The AI renames a function parameter, changes a return type from `string | null` to `string | undefined`, or restructures a response object during refactoring. The code compiles. Tests pass (because the tests were updated too). But every external consumer is now broken.

**How to catch it:** Before any refactoring, identify what the public API is. Tell the AI explicitly: "These interfaces must not change." Review the diff for any changes to exported types, function signatures, or response shapes.

### 6. Creating circular dependencies during file splits

The AI splits a file into modules and creates a situation where module A imports from module B and module B imports from module A. In some languages and bundlers, this works. In others, it causes initialization order bugs that manifest as `undefined` at runtime with no clear error.

**How to catch it:** After a file split, check the import graph. If any two new modules import from each other, restructure so dependencies flow one direction.

---

## Refactoring Patterns That Work

These refactoring patterns are well-suited to AI assistance because they're mechanical, bounded, and easy to verify.

### Rename and update references
The AI is excellent at finding every usage of a symbol and renaming it consistently. Better than find-and-replace because it understands scope.

**Prompt:** "Rename `processData` to `transformUserRecords` in this file and update all references across the codebase."

### Extract pure function
Pulling a block of side-effect-free code into its own function. The AI identifies inputs and outputs correctly for pure logic.

**Prompt:** "Extract the calculation on lines 45-62 into a separate function. This logic has no side effects."

### Add types to untyped code
The AI can infer types from usage patterns and add type annotations. This is one of the highest-value AI refactoring tasks — tedious for humans, fast and accurate for AI.

**Prompt:** "Add TypeScript types to this file. Infer types from usage. Don't change any runtime behavior."

### Replace magic numbers/strings with constants
Mechanical extraction that the AI handles well.

**Prompt:** "Extract all magic numbers and string literals in this file into named constants at the top of the file."

### Flatten nested callbacks/promises
Converting callback hell or deeply nested `.then()` chains to async/await. The AI does this well because the transformation is mechanical.

**Prompt:** "Convert the promise chains in this file to async/await. Preserve all error handling behavior."

---

## Refactoring Patterns That Don't

These patterns are poorly suited to unsupervised AI refactoring because they require judgment about intent, not just structure.

### "Clean up this file"
The vaguest and most dangerous prompt. The AI will rename things, extract things, reorder things, remove things, and add things. You'll get a diff with 200 changes and no way to verify that none of them changed behavior.

**Instead:** "Identify the three biggest clarity issues in this file. Don't change anything yet — just list them."

### Merging two implementations
"We have two similar functions — combine them." The AI will find the common parts and parameterize the differences. But the differences exist for reasons the AI may not understand, and parameterization often makes the code *harder* to understand, not easier.

**Instead:** Evaluate whether merging is actually worth it. If the functions change for different reasons, duplication is better than the wrong abstraction.

### Rewriting a function "more elegantly"
"This works but it's ugly — rewrite it." The AI produces something that looks cleaner but handles fewer edge cases. The "ugly" code was ugly because it was handling real complexity.

**Instead:** "What edge cases does this function handle? List them. Then show me a clearer version that handles all of them."

### Large-scale pattern migration
"Convert all our class components to functional components." Or "migrate from callbacks to async/await across the codebase." These are high-volume changes where each individual transformation is simple, but the sheer volume makes reviewing every change impractical.

**Instead:** Do it module by module, not codebase-wide. One module per PR. This keeps each change reviewable.

---

## The Scope Problem

The most common failure in AI-assisted refactoring is scope expansion. You ask for one change. The AI makes that change, then "while it's in there" fixes three other things, improves two function names, and reorganizes an import block.

Each of those additional changes may be individually fine. Together, they make the diff unreviewable. And one of them might introduce a subtle bug that you can't find because it's buried in 50 other changes.

### How to Control Scope

**Be explicit about boundaries:**
> "Refactor ONLY the `processOrder` function. Do not modify any other function in this file. Do not rename anything outside `processOrder`. Do not change imports."

**Set a diff size expectation:**
> "This refactoring should touch approximately 20-30 lines. If your change is significantly larger, stop and explain why."

**Use a constraint checklist:**
> "Constraints for this refactoring:
> - Do not change any function signatures
> - Do not change any file names
> - Do not add or remove dependencies
> - Do not modify tests
> - All existing tests must still pass without modification"

The constraint that tests must pass *without modification* is particularly powerful. If the AI has to change tests to make the refactoring work, it's changing behavior — not just structure.

---

## When Not to Refactor with AI

Sometimes the right answer is to refactor by hand, or not to refactor at all.

### Don't refactor when you don't understand the code

If you can't explain what the code does, you can't verify whether the refactored version does the same thing. Read first. Understand the behavior, the edge cases, the invariants. Then decide whether to refactor.

Asking the AI to "clean up this code I don't understand" is how you get code that's clean, elegant, and wrong.

### Don't refactor code that's about to be replaced

If the feature is being rewritten next sprint, refactoring the current implementation is pure waste. The investment won't pay off.

### Don't refactor without tests

If the code has no tests, you have no way to verify that the refactoring preserved behavior. Write tests first, *then* refactor. This is true with or without AI, but it's especially important with AI because the AI refactors aggressively — it makes more changes in less time, which means more opportunities for unverified behavioral changes.

**The sequence:** Tests → Refactor → Verify. Never: Refactor → Hope.

### Don't refactor under time pressure

Refactoring is investment. It costs time now to save time later. If you're shipping a fix today, ship the fix. Refactor when you have time to do it properly — incrementally, with verification at each step.

---

## Prompting for Safe Refactoring

### The safe refactoring prompt template

```
Refactor [specific target] in [specific file].

Goal: [what should improve — clarity, modularity, performance]

Constraints:
- Do not change behavior. All existing tests must pass WITHOUT modification.
- Do not change public interfaces (exported functions, API responses, types).
- Do not change any code outside [specific target].
- Do not add or remove dependencies.

Process:
1. Before making changes, list the current behavior and edge cases you observe.
2. Make the refactoring changes.
3. Confirm: "All existing tests should pass without modification."
```

The key element is step 1: **making the AI articulate the current behavior before changing it.** This forces it to reason about what it needs to preserve, not just what it wants to improve.

### For file splitting

```
Split [filename] into smaller modules.

Step 1 (this prompt): Extract ONLY [specific concern] into a new file.
Do not extract anything else. Do not refactor the remaining code.

After extraction:
- All imports in other files should still work
- No circular dependencies between the new and old file
- All tests pass without modification
```

### For large refactoring projects

Use the [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md) workflow. Write a plan that lists every refactoring step, the expected diff size for each step, and the verification method. Audit the plan before executing it.

---

## Checklist

### Before starting any refactoring

- [ ] Identified the risk level (low / medium / high)
- [ ] Confirmed test coverage exists for the code being refactored
- [ ] Identified the public interface that must not change
- [ ] Defined the scope explicitly (what changes, what doesn't)
- [ ] Committed the current working state (clean starting point to revert to)

### During refactoring

- [ ] Making one change at a time (incremental method)
- [ ] Running tests after each step
- [ ] Reviewing diffs after each step — checking for behavioral changes
- [ ] Committing after each verified step
- [ ] Monitoring diff size against expectations
- [ ] Reverting and re-scoping if the AI expanded beyond the request

### After refactoring

- [ ] Full test suite passes
- [ ] No tests were modified (unless test-only refactoring was the goal)
- [ ] Public interfaces are unchanged
- [ ] No circular dependencies introduced
- [ ] No new dependencies added
- [ ] Manual spot-check of critical paths (for medium/high-risk refactoring)
- [ ] Import graph verified (for file splits)

---

## Related Guides

- **[Anti-Patterns & Warning Signs](./ANTI_PATTERNS.md)** — The "Endless Refactor" anti-pattern is the extreme case of what happens when refactoring scope isn't controlled. The "Copy-Paste Coding" and "God File" anti-patterns are what create the need for refactoring in the first place.
- **[Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md)** — Use the full planning workflow for high-risk refactoring that spans multiple files or changes abstractions.
- **[Version Control Best Practices](./VERSION_CONTROL.md)** — Includes a commit message template for AI-assisted refactoring and guidance on atomic commits. Incremental refactoring produces clean, revertible commit histories.
- **[Code Review for AI](./CODE_REVIEW_AI.md)** — The AI code smells section (particularly "Over-Generic Solutions" and cross-boundary review) applies directly to reviewing refactored code.

### Related Prompts

- **[Refactor for Clarity](/prompts/refactor-for-clarity)** — A focused prompt for clarity-only refactoring. Use it for low-risk, single-file improvements.
- **[Modularity Review](/prompts/modularity-review)** — Use this before splitting large files. It identifies what to extract and in what order.
