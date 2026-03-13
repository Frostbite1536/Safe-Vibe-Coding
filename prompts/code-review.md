---
layout: default
title: Code Review
parent: Prompts Library
nav_order: 13
---

# Code Review Prompt

Use this prompt to perform a structured, multi-pass code review on pull requests or local diffs. Designed to replicate the multi-agent analysis approach of managed code review services using tools you already have.

---

## Using as a Claude Code Slash Command

Copy this file to `.claude/commands/review-pr.md` in your project to use it as `/review-pr`:

```bash
mkdir -p .claude/commands
cp prompts/code-review.md .claude/commands/review-pr.md
```

Then invoke with: `/review-pr 42` (where 42 is the PR number)

---

## Prompt

You are performing a structured code review. Your goal is to find correctness bugs, security vulnerabilities, broken edge cases, and subtle regressions — not formatting preferences or style nits (unless they violate explicit rules in REVIEW.md).

**What to review**: $ARGUMENTS

If a PR number was provided, fetch the diff and changed files. If no argument was given, review the current branch's changes against the base branch.

---

## Step 1: Gather Context

Before reviewing, collect these inputs:

1. **The diff**: Use `gh pr diff <number>` for PRs, or `git diff main...HEAD` for local branches
2. **Changed files in full**: Read each changed file completely — reviewing only the diff misses bugs that depend on surrounding code
3. **CLAUDE.md**: Read the project's CLAUDE.md for general rules (if it exists)
4. **REVIEW.md**: Read the project's REVIEW.md for review-specific rules (if it exists)
5. **INVARIANTS.md**: Read the project's invariants doc (if it exists)
6. **Recent commit messages**: `git log --oneline -20` to understand the intent of changes

---

## Step 2: Multi-Pass Analysis

Run these passes sequentially. Each pass looks for a different class of issue.

### Pass 1 — Correctness

- Logic errors: wrong conditionals, off-by-one, incorrect operators
- Unhandled edge cases: empty inputs, null values, boundary conditions, single-element collections
- Division by zero in aggregations (empty lists, all-identical values, single-element with `ddof=1`)
- State management: race conditions, stale state, mutations where immutability is expected
- Error handling: silent failures, errors caught but not handled, cleanup in error paths

### Pass 2 — Security

- SQL injection, XSS, command injection, path traversal
- Missing authentication or authorization checks on new endpoints
- Secrets or credentials in code, logs, or error messages
- Input validation gaps at system boundaries

### Pass 3 — Cross-Boundary Contracts

This is the highest-value pass — most bugs in AI-generated code live at the seams between components.

- Does the changed code agree with its consumers and producers on data shape, types, and semantics?
- If a field was added to a data model, does every layer (persistence, serialization, API, tests) know about it?
- Are round-trips preserved? (save/restore, serialize/deserialize)
- Type leakage: `Decimal` into JSON, `datetime` into dicts, `Optional` fields silently defaulting
- If an operation fails midway, is state rolled back or left half-modified?

### Pass 4 — Invariant & Architecture Compliance

- Check changes against INVARIANTS.md (if it exists)
- Check changes against CLAUDE.md rules (violations are nit-level)
- Check changes against REVIEW.md rules (if it exists)
- Does the change follow existing patterns or introduce a new one?
- Does it respect component boundaries from the architecture doc?

### Pass 5 — Regression Pattern Search

- For each bug found, search the codebase for the same pattern elsewhere
- Check if the PR introduces a pattern that already exists as a known anti-pattern
- Verify test fixtures are updated to reflect any new fields or changed semantics

---

## Step 3: Report Findings

### Severity Levels

Tag each finding with exactly one severity:

| Marker | Level | Meaning |
|--------|-------|---------|
| **[CRITICAL]** | Normal | A bug that should be fixed before merging |
| **[NIT]** | Nit | A minor issue, worth fixing but not blocking |
| **[PRE-EXISTING]** | Pre-existing | A bug in the codebase not introduced by this PR |

### Output Format

For each finding:

```
**[SEVERITY] File: `path/to/file.py` | Line: N**

**Issue**: One-sentence description of the problem.

**Why**: Explanation of why this is a bug, including the specific failure scenario.

**Suggested fix**: How to fix it (code snippet if helpful).
```

### Summary

After all findings, provide:

```
## Review Summary

**Findings**: N total (X critical, Y nits, Z pre-existing)

**Overall assessment**: [Approve / Request Changes / Needs Discussion]

**Key concerns**: [1-3 bullet points of the most important issues]
```

If no issues are found, state: "Code review complete. No issues found." and list what was checked.

---

## REVIEW.md File Convention

Teams can create a `REVIEW.md` file at the repository root to encode review-specific rules that don't belong in CLAUDE.md. This file is only relevant during code reviews, not during general development.

Example `REVIEW.md`:

```markdown
# Code Review Guidelines

## Always check
- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible
- Error messages don't leak internal details to users
- New fields added to data models are reflected in persistence and serialization

## Style
- Prefer early returns over nested conditionals
- Use structured logging, not f-string interpolation in log calls
- Group imports: stdlib, third-party, local

## Skip
- Generated files under `src/gen/`
- Formatting-only changes in `*.lock` files
- Test fixtures (unless data model changed)
```

---

## Tips for Effective Reviews

- **Read changed files in full**, not just the diff. Bugs often depend on context the diff doesn't show
- **Focus on correctness over style**. A review that finds one real bug is worth more than one that flags twenty formatting issues
- **Check the tests**: Are they testing the right thing? Would they catch the bug if it regressed?
- **Trace data through boundaries**: The most important bugs live between components, not inside them
- **Search for patterns**: If you find a bug, grep for the same pattern codebase-wide — AI code replicates mistakes
