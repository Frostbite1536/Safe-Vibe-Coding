---
layout: default
title: Root Cause Isolation
parent: Prompts Library
nav_order: 6
---

# Root Cause Isolation Prompt

Use this prompt when a bug evades normal debugging—when defensive fixes keep failing and the error appears in new locations.

---

## When to Use This Prompt

**Use this when:**
- The same error appears in multiple locations after each "fix"
- Adding defensive checks (null guards, type coercion) doesn't resolve the issue
- The error message points to one location but fixing it doesn't help
- You've made 3+ attempts to fix the same underlying bug

**This is NOT for:**
- Simple, localized bugs with obvious causes
- Performance issues (use performance-review.md)
- Proactive bug hunting (use bug-hunt.md)

---

## Prompt

You are debugging an elusive bug that has resisted multiple fix attempts. Your goal is to find the **root cause**, not treat symptoms.

**The bug**: [describe the error/behavior]

**What's been tried**: [list previous fix attempts]

**Error location**: [file:line where error appears]

---

## The Core Principle

> **The error location is not the problem location.**

When a bug appears at render time, the data was corrupted earlier. When a cache throws an error, something wrote bad data to it. When a component crashes, its props were invalid before it received them.

**Trace upstream, not downstream.**

---

## Root Cause Isolation Methodology

### Step 1: Read the Stack Trace

Before touching any code:

1. **Find the actual operation** - What function is failing? (`setData`, `render`, `map`, etc.)
2. **Identify the data flow** - Where does the failing data come from?
3. **Look for cache/state operations** - `setData`, `setState`, `dispatch`, `mutate` indicate the data was written somewhere

**Questions to answer:**
- What is the actual failing operation? (not just where it throws)
- What data is involved?
- Where could that data have been corrupted?

### Step 2: Map the Data Flow

Trace the data from error site back to its origin:

```
Error site (component render)
    ↑
State/cache read
    ↑
State/cache write (mutation, setter)
    ↑
Data transformation (mapper, normalizer)
    ↑
API response / user input
```

**For each layer, ask:**
- Could invalid data enter here?
- Is there validation at this boundary?
- What assumptions does this layer make?

### Step 3: Disable Complexity Layers

Modern apps have optimization layers that can create edge cases:

| Layer | What it does | How to disable |
|-------|--------------|----------------|
| **Virtualization** | Only renders visible items | Set threshold very high (e.g., 10000) |
| **Memoization** | Caches computed values | Remove `useMemo`/`useCallback`/`React.memo` |
| **Optimistic updates** | Updates UI before server confirms | Disable in mutation options |
| **Caching** | Stores fetched data | Clear cache, disable `staleTime` |
| **Batching** | Groups state updates | Force synchronous updates |
| **Suspense** | Defers rendering during loads | Use fallback loading states |

**Process:**
1. Disable one layer at a time
2. Test if bug persists
3. If bug disappears → that layer is involved in the root cause
4. If bug persists → re-enable and try next layer

### Step 4: Reproduce at the Boundary

Once you've identified the layer, find the exact boundary condition:

- **Virtualization**: What happens during scroll? During window resize? During data updates while scrolling?
- **Caching**: What happens during cache invalidation? Race between read and write?
- **Optimistic updates**: What happens on rollback? On rapid successive updates?

### Step 5: Fix at the Source

The fix should be:
- **At the boundary where invalid data enters** (not where it's consumed)
- **One change** (not defensive checks in 10 places)
- **Addressing the root cause** (not masking symptoms)

---

## Red Flags: You're Treating Symptoms

🚩 **Adding the same defensive check in multiple files**

If you're adding `typeof x === 'string' ? x : String(x)` in 5 different components, the data should have been validated once at the source.

🚩 **The error moves after each fix**

First it was in ComponentA, then ComponentB, then ComponentC. The root cause is upstream of all of them.

🚩 **Increasing commit count with no resolution**

v1, v2, v3... v10... each adding more guards. Stop and trace upstream.

🚩 **Grepping for patterns instead of tracing data**

Searching for `contact.name` usages treats symptoms. Following the data from API → cache → component finds root cause.

🚩 **The fix requires changing more than 50 lines across multiple files**

Root cause fixes are usually small. Symptom fixes spread across the codebase.

---

## Isolation Techniques

### Binary Search Isolation

When you can't identify the layer:

1. Comment out half the complexity (half the middleware, half the optimizations)
2. Test
3. If bug persists → problem is in remaining half
4. If bug disappears → problem is in commented half
5. Repeat on the problematic half

### Minimal Reproduction

1. Create the simplest version of the component/flow
2. Add complexity back one piece at a time
3. When bug appears → you found the trigger

### Logging at Boundaries

```typescript
// Log data at each transformation boundary
console.log('[API Response]', rawData);
console.log('[After Transform]', transformedData);
console.log('[Cache Write]', cacheData);
console.log('[Component Props]', props);
```

Look for where valid data becomes invalid.

---

## Output Format

### Root Cause Analysis

**Error symptom**: [what the error says]

**Error location**: [where it appears]

**Actual root cause**: [where the problem originates]

**Why it happens**: [the specific condition/timing/edge case]

**Data flow**:
```
[origin] → [transform] → [cache] → [read] → [error]
                ↑
          Problem here: [explanation]
```

### The Fix

**Location**: [single file:line]

**Change**: [minimal diff]

**Why this works**: [addresses root cause, not symptom]

### Verification

- [ ] Error no longer reproducible
- [ ] Removed temporary defensive checks (if added during debugging)
- [ ] Tested edge cases that triggered the original bug
- [ ] No regression in related functionality

---

## Example: The Virtualization Bug

**Symptom**: "Objects are not valid as React child" appearing in various components

**Previous attempts**: Added type checks in 10+ components, error kept moving

**Stack trace analysis**: Error occurred during `setData` in React Query cache

**Insight**: The error location (render) wasn't the problem. The stack trace showed cache mutation (`setData → batch → setTimeout`).

**Layer isolation**: Disabled virtualization → error disappeared

**Root cause**: Virtualization library created edge cases during cache transitions. Rows could briefly render with stale/incomplete data objects during window calculations.

**Fix**: One constant: `VIRTUALIZATION_THRESHOLD = 10000` (effectively disabled)

**Lesson**: 20 commits treating symptoms vs. 1 line fixing root cause.

---

## Remember

**When debugging feels like whack-a-mole, you're treating symptoms.**

Stop adding defensive code. Stop grepping for patterns. Instead:

1. Read the stack trace
2. Trace data upstream
3. Disable complexity layers
4. Find the single point where invalid data enters
5. Fix there

The best debugging sessions end with a small fix and the realization: "That's where it was the whole time."
