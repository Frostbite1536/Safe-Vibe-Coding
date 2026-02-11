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

### 2. Debug Logging Strategy

**CRITICAL: Be VERY generous with debug logging when investigating bugs.**

Don't be cautious or conservative with logging. The more information, the better.

#### What to Log

**Log comprehensively at every step**:
```typescript
// ✅ EXCELLENT - Comprehensive context
function processImport(data: ImportData) {
  console.log('[IMPORT] Starting import:', {
    recordCount: data.records.length,
    source: data.source,
    timestamp: Date.now()
  });

  for (const record of data.records) {
    console.log('[IMPORT] Processing record:', {
      id: record.id,
      type: record.type,
      hasRequiredFields: !!(record.name && record.email)
    });

    const result = validateRecord(record);
    console.log('[IMPORT] Validation result:', { id: record.id, result });

    if (!result.valid) {
      console.log('[IMPORT] SKIPPING invalid record:', {
        id: record.id,
        errors: result.errors,
        record
      });
      continue;
    }

    // ... more logging at each step
  }
}

// ❌ INSUFFICIENT - Too cautious
function processImport(data: ImportData) {
  console.log('Processing import');
  for (const record of data.records) {
    const result = validateRecord(record);
    if (!result.valid) continue;
  }
}
```

**Log at these critical points**:
1. **Function entry/exit** - With full input/output context
2. **Before/after API calls** - Request + response + timing
3. **Conditional branches** - Log BOTH branches with relevant data
4. **Data transformations** - Log before and after state
5. **Cache/state updates** - Log what's being updated and the new value
6. **Error cases** - Log the full context that led to the error

#### Use Descriptive Prefixes

Make logs easy to grep:
```typescript
console.log('[IMPORT-DEBUG] ...');
console.log('[CONTACT-UPDATE] ...');
console.log('[CACHE-MUTATION] ...');
console.log('[API-RESPONSE] ...');
```

#### Philosophy

**It's better to have 50 lines of debug output and quickly identify the issue than to add one log statement at a time and iterate slowly.**

You can always remove logging later. You can't retroactively see what was happening without it.

#### ⚠️ Debug Code Can Introduce Bugs

**CRITICAL:** Debug code itself can cause issues, especially with React Query, Redux, and other systems that rely on immutability.

**Dangerous patterns:**
```typescript
// ❌ DANGEROUS - Mutates cached object
console.log('Contact:', contact);
contact.debugFlag = true;  // Modifies React Query cache!
contact.roles.push('DEBUG');  // Breaks immutability!

// ❌ DANGEROUS - .sort() mutates arrays
console.log('Sorted:', contacts.sort(...));  // Mutates cached array!

// ❌ DANGEROUS - Modifying during iteration
const processed = contacts.map(c => {
  c.processed = true;  // Mutates original!
  return c;
});
```

**Safe patterns:**
```typescript
// ✅ SAFE - Read-only access
console.log('Contact:', { ...contact });

// ✅ SAFE - Clone before mutating
console.log('Sorted:', [...contacts].sort(...));

// ✅ SAFE - Create new objects
const processed = contacts.map(c => ({
  ...c,
  processed: true  // New object
}));
```

**Why this matters:**
- React Query caches by reference - mutations affect ALL components
- Mutating arrays (.sort(), .push(), .splice()) is especially dangerous
- Creates "phantom bugs" that vanish when debug code is removed

**Rule: Never mutate objects you're debugging - only read, never write.**

### 3. Root Cause vs Symptoms

**CRITICAL LESSON: Trace data flow UPSTREAM to the entry point. Don't chase symptoms downstream.**

#### ❌ Inefficient: Whack-a-Mole with Symptoms

```typescript
// Round 1: Add defensive check
{contact.name?.slice(0, 1) || '?'}

// Round 2: Error appears elsewhere, add another check
{typeof contact.email === 'string' ? contact.email : ''}

// Round 3: More defensive checks...
{Array.isArray(contact.roles) ? contact.roles.join(', ') : ''}

// Result: 20+ defensive checks scattered everywhere, error still persists
```

**Problem:** You're treating symptoms (unsafe rendering) not the root cause (malformed data).

#### ✅ Efficient: Trace Data Flow Upstream

**Key Question:** "Where could invalid data GET INTO the system?" (not "where are we using it unsafely?")

**Trace the flow backward:**
```
JSX Render → Component Props → React Hook → React Query Cache → API Response
    ↑                                              ↑
  ERROR HERE                              FIX IT HERE!

Also fed by:
    ↑
Inline edits, form submissions, optimistic updates
```

**Real-world example:**

```typescript
// Stack trace showed: setData → batch → setTimeout
// This pointed to React Query cache mutations, not rendering

// ❌ I first looked at: JSX rendering code (wrong!)
<div>{contact.name.slice(0, 1)}</div>

// ✅ Should have looked at: What's calling setData?

// Found in use-inline-edit.ts:
updateContactCache({
  ...contact,
  [field]: value  // ← value: unknown (TypeScript warning!)
})
```

#### Red Flags Pointing to Entry Point Issues

1. **TypeScript `unknown` or `any` types** - Data that could be "anything"
2. **Stack trace shows cache/state updates** - Not rendering code
3. **Defensive fixes don't stop the error** - You're not at the source
4. **Error appears in multiple components** - Shared upstream data is bad

#### The Right Debugging Flow

**For data-related errors:**

1. **Read the stack trace carefully**
   - `setData`/`setState`/`dispatch` → Cache/state mutation issue
   - Component render → Check data source, not just render code

2. **Trace data backward to its origin**
   - Component crashed → What data is it using?
   - Where does that data come from? (props, hook, query)
   - Where does THAT come from? (API, cache, state)
   - **Keep going until you find the entry point**

3. **Validate at entry point, not at every usage**
   ```typescript
   // ❌ BAD: Defensive checks everywhere
   function ContactCard({ contact }: { contact: Contact }) {
     const name = typeof contact.name === 'string' ? contact.name : 'Unknown';
     const email = typeof contact.email === 'string' ? contact.email : '';
     // ... 20 components with similar checks
   }

   // ✅ GOOD: Sanitize once at the entry point
   function useContacts() {
     return useQuery({
       queryFn: async () => {
         const response = await api.contacts.getAll();
         return response.data.map(sanitizeContact); // ← Fix here
       }
     });
   }

   // Now all components can trust the data
   function ContactCard({ contact }: { contact: Contact }) {
     return <div>{contact.name}</div>; // Safe!
   }
   ```

4. **Look for TypeScript warnings**
   ```typescript
   value: unknown  // ← RED FLAG!
   data: any       // ← RED FLAG!
   ```

#### Ask the Right Questions

- ❌ "Where do we render `contact.name` unsafely?"
- ✅ "Where could `contact.name` become a non-string?"

- ❌ "Let's add `contact.field?.toString() ?? ''` everywhere"
- ✅ "Let's ensure only valid Contact objects enter our cache"

**One sanitization layer at entry points >> Dozens of defensive checks at usage points**

### 4. Design the Minimal Fix

**Plan the smallest possible change**:
- What's the minimal code change to fix the root cause?
- Can this be fixed with a 1-line change? 5 lines? 10 lines?
- Are there alternative fixes that are simpler?

**Avoid**:
- Rewriting entire functions when changing one condition would work
- Introducing new abstractions to fix a simple bug
- Changing method signatures unless absolutely necessary

### 5. Write or Update Tests

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

### 6. Implement the Fix

**Implementation guidelines**:
- Change only what's necessary
- Match the existing code style (even if not ideal)
- Add comments only if the fix is non-obvious
- Preserve existing error handling

**If the fix requires larger changes**: Stop and discuss whether this is really just a bug fix, or if it's a design issue that needs architectural changes.

### 7. Verify the Fix

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
