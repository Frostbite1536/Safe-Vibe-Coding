---
layout: default
title: Bug Fixing
parent: Prompts Library
nav_order: 5
---

# Bug Fixing Prompt

Use this prompt when fixing bugs to ensure surgical, focused fixes without scope creep.

---

## Prompt

You are fixing bugs only. This is not a refactoring session. This is not a feature addition. This is surgical bug fixing.

**Bug to fix**: [description of the bug]

**Steps to reproduce**: [if known]

**Expected behavior**: [what should happen]

**Actual behavior**: [what actually happens]

---

## Bug Fixing Constraints

**You MUST**:
- ✅ Fix only the root cause of this specific bug
- ✅ Add or update tests to prevent regression
- ✅ Preserve all existing behavior except the bug
- ✅ Keep changes minimal and focused

**You MUST NOT**:
- ❌ Refactor unrelated code
- ❌ "Clean up" surrounding code
- ❌ Add new features, even small ones
- ❌ Change coding style of existing code
- ❌ Fix other bugs you notice (file them separately instead)
- ❌ Make "while we're here" improvements

---

## Bug Fixing Process

### 1. Understand the Root Cause

**Before changing any code**:
- Reproduce the bug (if possible)
- Identify the root cause, not just symptoms
- Trace the bug to the specific code location
- Understand why the current code is wrong

**Ask yourself**:
- Why does this bug exist?
- Is this a logic error, edge case, race condition, etc.?
- What assumptions were incorrect?
- Could this bug exist elsewhere with the same pattern?

### 2. Design the Minimal Fix

**Plan the smallest possible change**:
- What's the minimal code change to fix the root cause?
- Can this be fixed with a 1-line change? 5 lines? 10 lines?
- Are there alternative fixes that are simpler?

**Avoid**:
- Rewriting entire functions when changing one condition would work
- Introducing new abstractions to fix a simple bug
- Changing method signatures unless absolutely necessary

### 3. Write or Update Tests

**Test requirements**:
- Add a test that fails without the fix and passes with it
- Ensure existing tests still pass
- If there's an edge case, add a test for it
- Make tests specific to this bug (not generic)

**Test format**:
```
test_bug_[issue_number]_[brief_description]:
    # This test reproduces the bug from issue #123
    # Expected: [correct behavior]
    # Before fix: [buggy behavior]
    [test code]
```

### 4. Implement the Fix

**Implementation guidelines**:
- Change only what's necessary
- Match the existing code style (even if not ideal)
- Add comments only if the fix is non-obvious
- Preserve existing error handling

**If the fix requires larger changes**: Stop and discuss whether this is really just a bug fix, or if it's a design issue that needs architectural changes.

### 5. Verify the Fix

**Check that**:
- [ ] Bug is fixed (verify manually)
- [ ] New/updated tests pass
- [ ] All existing tests still pass
- [ ] No new bugs introduced (especially edge cases)
- [ ] No invariants violated
- [ ] No regressions in related functionality

---

## Output Format

Provide your fix in this format:

### Root Cause Analysis

**Location**: [file:line]

**Root cause**: [clear explanation of why the bug exists]

**Why it happened**: [incorrect assumption, missing edge case, etc.]

### The Fix

**Changed files**:
- [file1]: [one-line description of change]
- [file2]: [one-line description of change]

**Diff**:
```
[show the minimal diff]
```

### Tests Added/Updated

**New tests**:
- [test name]: [what it tests]

**Updated tests**:
- [test name]: [why it was updated]

### Verification

- [x] Bug no longer reproduces
- [x] All tests pass
- [x] No regressions observed
- [x] Edge cases handled

---

## Examples

### ✅ Good Bug Fix

**Bug**: User login fails when email has uppercase letters

**Root cause**: Email comparison is case-sensitive

**Fix**: One line change to lowercase email before comparison
```python
- if user.email == provided_email:
+ if user.email.lower() == provided_email.lower():
```

**Test**: Added test for uppercase email login

**Scope**: 1 line of production code, 5 lines of test code

---

### ❌ Bad Bug Fix (Scope Creep)

**Bug**: User login fails when email has uppercase letters

**Fix**: Rewrote entire authentication system to use a new library, refactored user model, changed database schema, added password strength validation, updated UI components

**Why this is bad**: The bug was a simple comparison issue. All these changes introduce risk and are unrelated to the actual bug.

---

## When to Stop and Ask

Stop and ask for guidance if:
- The minimal fix would require changing > 50 lines of code
- The fix requires changing public APIs
- The fix reveals a deeper architectural issue
- Multiple approaches exist with significant trade-offs
- The fix might break backwards compatibility

In these cases, the "bug" might actually be a design issue that needs broader discussion.

---

## Remember

**Surgical precision beats comprehensive improvement.**

A focused bug fix that changes 3 lines is better than a "clean" refactor that changes 300 lines—even if the refactor is objectively better code. Bug fixes should be:
- **Minimal**: Smallest possible change
- **Obvious**: Easy to review and verify
- **Safe**: Low risk of introducing new bugs
- **Testable**: Covered by regression tests

**The best bug fix is the one you can confidently deploy without fear.**
