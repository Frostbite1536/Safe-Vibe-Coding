---
layout: default
title: Code Review for AI
nav_order: 3
parent: Guides
description: "How to review AI-generated code effectively, including AI-specific code smells and security checks."
---

# Code Review Practices for AI-Generated Code

AI-generated code requires different review practices than human-written code. LLMs can produce syntactically correct code that is nonetheless wrong, insecure, or inefficient. This document outlines how to review AI outputs effectively.

---

## Core Principle

**Never merge AI-generated code without human review.**

Even with excellent prompts and strong guardrails, LLMs make mistakes. Your job as the human is to be the final quality gate.

---

## Classify Findings by Severity

Not all issues are equal. Use a consistent severity system so reviewers and developers can prioritize:

| Level | Meaning | Action |
|-------|---------|--------|
| **Critical** | A bug that should be fixed before merging — logic errors, security vulnerabilities, data corruption | Block merge |
| **Nit** | A minor issue worth fixing but not blocking — style violations, missing edge case tests, slight inefficiency | Fix if easy, track if not |
| **Pre-existing** | A bug in the codebase not introduced by this change | File separately, don't block this PR |

This classification prevents two common failure modes: blocking PRs over trivial issues (reviewer fatigue) and letting real bugs through because they're buried in a wall of style nits.

---

## Use a REVIEW.md File for Review-Specific Rules

Create a `REVIEW.md` file at your repository root to encode review rules that don't belong in your general project docs. This file is specifically for what reviewers (human or AI) should flag or skip.

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

## Skip
- Generated files under src/gen/
- Formatting-only changes in *.lock files
```

**Why separate from CLAUDE.md?** Your `CLAUDE.md` contains general development instructions that apply during coding. `REVIEW.md` contains rules that only matter during review — what to flag, what to skip, what severity to assign. Keeping them separate prevents review noise from cluttering development context and vice versa.

For a structured code review prompt that uses both files, see the [Code Review prompt](../prompts/code-review.md).

---

## The AI Code Review Checklist

### 1. Does It Actually Work?

**Don't assume it works because it looks right.**

- [ ] Run the code locally
- [ ] Execute all affected tests
- [ ] Manually test the feature/fix
- [ ] Try edge cases the LLM might have missed
- [ ] Verify error handling actually works

**Common AI mistakes**:
- Code that compiles but crashes at runtime
- Logic that works for happy path but fails for edge cases
- Off-by-one errors
- Incorrect assumptions about data types

### 2. Does It Match Requirements?

**LLMs sometimes solve a different problem than requested.**

- [ ] Compare output to original request
- [ ] Verify it solves the actual problem
- [ ] Check that nothing extra was added
- [ ] Confirm scope hasn't creeped

**Common AI mistakes**:
- Solving a more general problem than needed
- Adding unrequested features
- Misunderstanding the requirement
- Optimizing for the wrong thing

### 3. Correctness Deep Dive

**AI can produce subtly incorrect code.**

#### Logic Errors
- [ ] Verify conditional logic (especially complex boolean expressions)
- [ ] Check loop termination conditions
- [ ] Verify sorting/comparison functions
- [ ] Confirm mathematical operations

#### State Management
- [ ] Check for race conditions
- [ ] Verify state updates happen correctly
- [ ] Confirm state isn't mutated when it shouldn't be
- [ ] Check for stale state bugs

#### Error Handling
- [ ] Verify all error paths are handled
- [ ] Check that errors don't silently fail
- [ ] Confirm error messages are helpful
- [ ] Verify cleanup happens in error cases

### 4. Security Review (Critical)

**AI often generates insecure code.**

- [ ] **SQL Injection**: Are queries parameterized?
- [ ] **XSS**: Is user input properly escaped in output?
- [ ] **Command Injection**: Is user input used in system commands?
- [ ] **Path Traversal**: Are file paths validated?
- [ ] **Authentication**: Are auth checks present and correct?
- [ ] **Authorization**: Can users access things they shouldn't?
- [ ] **Data Leakage**: Is sensitive data in logs or error messages?
- [ ] **Input Validation**: Is all external input validated?

**AI tendency**: LLMs often skip input validation or use unsafe string interpolation.

### 5. Performance Review

**AI frequently generates inefficient code.**

- [ ] Check for N+1 query problems
- [ ] Verify database queries are indexed
- [ ] Look for unnecessary loops or operations
- [ ] Check algorithmic complexity (O(n²) when O(n) possible)
- [ ] Verify large datasets aren't loaded entirely into memory
- [ ] Check for unnecessary re-renders (frontend)

**AI tendency**: LLMs optimize for readability over performance, often using inefficient patterns.

### 6. Invariant Compliance

**AI doesn't inherently respect your system contracts.**

- [ ] Review against `INVARIANTS.md`
- [ ] Confirm data integrity rules maintained
- [ ] Verify authorization invariants hold
- [ ] Check API contracts unchanged (or properly versioned)
- [ ] Confirm consistency requirements met

**AI tendency**: LLMs don't know your invariants unless explicitly told, and may violate them.

### 7. Architecture Alignment

**AI can introduce architectural drift.**

- [ ] Follows established patterns?
- [ ] Respects component boundaries?
- [ ] Uses existing abstractions (doesn't reinvent)?
- [ ] Fits the data flow model?
- [ ] Doesn't introduce inappropriate dependencies?

**AI tendency**: LLMs sometimes create new patterns instead of using existing ones, causing inconsistency.

### 8. Code Quality

**AI code often has subtle quality issues.**

#### Readability
- [ ] Variable/function names are clear
- [ ] Code is self-explanatory
- [ ] Complex logic is broken into functions
- [ ] No overly clever code

#### Maintainability
- [ ] Will make sense in 6 months
- [ ] Easy to modify
- [ ] Clear where to make changes
- [ ] No hidden coupling

#### Duplication
- [ ] No copy-paste code
- [ ] Doesn't reimplement existing utilities
- [ ] Appropriately DRY (not over-abstracted)

### 9. Testing Coverage

**AI-generated tests can be incomplete.**

- [ ] Tests cover happy path
- [ ] Tests cover edge cases
- [ ] Tests cover error cases
- [ ] Tests are actually testing the right thing
- [ ] No tests that always pass
- [ ] Assertions are meaningful

**AI tendency**: LLMs write tests that look right but don't actually test edge cases or might have weak assertions.

### 10. Dependencies

**AI may suggest problematic dependencies.**

- [ ] Is this dependency necessary?
- [ ] Is it well-maintained?
- [ ] Does it have known vulnerabilities?
- [ ] Is the license compatible?
- [ ] Is the version pinned?

**AI tendency**: LLMs may suggest popular but heavy dependencies when simpler solutions exist.

---

## Specific AI Code Smells

These patterns appear more in AI code than human code:

### 1. Over-Generic Solutions

```python
# AI might generate
def process_data(data, config, options, handlers):
    # Overly flexible for a single use case
```

**Red flag**: More parameters and flexibility than current use case needs.

### 2. Inconsistent Error Handling

```python
# Mix of different error handling styles
try:
    foo()
except:
    pass  # Silent failure

def bar():
    if error:
        raise Exception("Error")  # Generic exception

def baz():
    return None  # Error signaled by return value
```

**Red flag**: AI picks different error handling patterns in the same codebase.

### 3. Placeholder Implementations

```python
# AI might generate
def complex_algorithm(data):
    # TODO: Optimize this
    result = []
    for item in data:
        # This could be improved
        result.append(process(item))
    return result
```

**Red flag**: Comments suggesting improvement + basic implementation = AI might not know the optimal approach.

### 4. Pattern Misapplication

```python
# Using a pattern inappropriately
class SimpleConfig:
    """Singleton pattern for config"""
    _instance = None

    def __new__(cls):
        # Singleton for a simple config is overkill
```

**Red flag**: Design patterns applied where simple code would work better.

### 5. Incomplete Null Handling

```typescript
// AI might generate
function getUser(id: string) {
    const user = database.findUser(id);
    return user.name;  // No null check!
}
```

**Red flag**: Assumes data exists without checking.

### 6. Copy-Paste Variation

```python
# AI generates similar code multiple times
def handle_create(data):
    validate(data)
    save(data)
    return success()

def handle_update(data):
    validate(data)
    save(data)
    return success()
```

**Red flag**: AI doesn't refactor common patterns it creates.

### 7. Sentinel Value Abuse

```python
# AI might generate
if trade.pnl == 0.0:
    # "Not yet calculated"
    calculate_pnl(trade)
```

**Red flag**: Using a legitimate business value (zero = breakeven) as a sentinel for "uninitialized." This silently corrupts real data. The fix is an explicit flag (`pnl_is_set = True`) or `Optional[float]` — boring but correct. **If you see `if x == 0.0` or `if x is None` to detect "uninitialized," ask whether that value could naturally occur.**

### 8. Timezone Stripping Instead of Converting

```python
# AI might generate
naive_dt = aware_dt.replace(tzinfo=None)  # ❌ Strips label, doesn't convert

# Correct
naive_utc = aware_dt.astimezone(timezone.utc).replace(tzinfo=None)  # ✅
```

**Red flag**: `replace(tzinfo=None)` just removes the timezone label without converting the time. `2024-01-15T10:00:00-05:00` should become `2024-01-15T15:00:00` (UTC), not `2024-01-15T10:00:00`. This bug gets copy-pasted across files. **When you see timezone handling, mentally trace a non-UTC input through it.**

### 9. Dead `hasattr` Checks on Structured Types

```python
# AI might generate
if hasattr(trade, 'outcome'):
    # This field doesn't exist on the dataclass — always False
    process_outcome(trade.outcome)
```

**Red flag**: `hasattr` on a `@dataclass` or typed class for a field that isn't declared. Since these types have fixed fields, the check always returns `False` and the guarded code never runs. This often happens when code was copied from a dict-based predecessor. **Verify the attribute actually exists on at least one code path.**

### 10. Wrong Formulas from Memory

```python
# AI might generate — looks right but isn't
downside_deviation = np.std(negative_returns)  # ❌ Wrong Sortino denominator
# Correct: sqrt(mean(min(r, 0)^2))
```

**Red flag**: Named financial or statistical metrics implemented from memory rather than the actual formula. `std(negative_returns)` and `sqrt(mean(min(r, 0)^2))` look similar but produce different results. **For any named metric (Sortino ratio, Sharpe ratio, drawdowns), look up the actual formula. Don't approximate from memory.**

### 11. Inconsistent Grouping Keys Across Files

```python
# File A groups by display name
groups = group_by(trades, key=lambda t: t.market)

# File B groups by slug
groups = group_by(trades, key=lambda t: t.market_slug)
```

**Red flag**: Two files operating on "the same grouping" use different keys. Display names can change or collide; slugs are stable. **When multiple functions group by the same concept, grep for all grouping sites and verify they use the same key.**

### 12. Cumulative Metrics Without a Baseline

```python
# AI might generate
cumulative_pnl = np.cumsum(pnls)
peak = np.maximum.accumulate(cumulative_pnl)
drawdown = (cumulative_pnl - peak) / peak  # ❌ First peak could be negative
```

**Red flag**: Starting `cumsum` without a zero origin means the first "peak" could be negative, making drawdown percentages meaningless. **Prepend a zero: `np.concatenate([[0], np.cumsum(pnls)])`.** Any cumulative metric needs an explicit starting point.

---

## Cross-Boundary Review: Where AI Code Actually Breaks

The most dangerous bugs in AI-generated code aren't inside modules — they're **between** them. LLMs generate each file in relative isolation. Each module may work correctly on its own, but the contracts between modules are implicit and sometimes contradictory. This is LLM code's characteristic failure mode.

### Think in Arrows, Not Boxes

Visualize your system as a data pipeline:

```
Input Source → Data Objects → State → Filters → Calculations → Serialization → Output
```

The bugs live on the **arrows** (boundaries between components), not in the **boxes** (individual modules). Review code at every boundary crossing.

### Cross-Boundary Review Checklist

**Data shape preservation across layers:**
- When Component A produces data and Component B consumes it, do they agree on the exact fields, types, and semantics?
- If you added a field to a data model, does every layer that touches that model (persistence, serialization, API, tests) know about it?
- Does a round-trip (serialize → deserialize, save → restore, API request → response) preserve all fields and types? Check for: boolean flags lost in persistence, `Decimal` leaking into JSON serialization, `datetime` objects not handled by serializers, `Optional` fields silently defaulting

**State corruption on partial failure:**
- If an operation fails midway (step 3 of 5), what state is the system in? Is it rolled back to the previous clean state, or left partially modified?
- If a multi-page API fetch fails on page 3 of 5, are pages 1-2 kept (potentially confusing) or discarded (clean but lossy)?
- If input validation fails after state has already been modified, is the state rolled back?

**Type consistency across boundaries:**
- If one module accumulates values using `Decimal` for precision, does it convert back to `float` before passing to the next module? Can a `Decimal` leak into a JSON response and crash serialization?
- Do all producers of a given type string (e.g., trade type: "Buy"/"Sell") agree on exact values, casing, and semantics? A filter expecting `"Buy"` won't match `"BUY"` or `"Market Buy"`
- When multiple modules group data by the same concept (e.g., "market"), do they all use the same key (slug vs. display name)?

**Mixed-source calculations:**
- When combining data from multiple sources, are units compatible? Summing USD and USDC amounts as if identical may be approximately correct but is not semantically sound
- Does a "global summary" function actually separate incompatible categories, or does it silently merge them?
- If sources use different PnL semantics (realized vs. unrealized, FIFO vs. settlement-based), does the aggregation acknowledge this?

**Filtering side effects on downstream calculations:**
- If a user filters to "only sells" and then requests a PnL summary, the sells have no corresponding buys — are the numbers meaningful or misleading?
- After filtering, do all downstream functions operate on the filtered set, or do some accidentally read from the unfiltered source?
- When filters are cleared, is the state reset to "all data" or to "empty"?

### How to Review Cross-Boundary Code

1. **Pick a data object** (e.g., a Trade, a User, an Order) and trace it through every layer: creation, storage, retrieval, filtering, calculation, serialization, output
2. **At each boundary**, verify: Does the receiving module handle every field, type, and edge case the producing module can generate?
3. **Specifically check**: What happens when the data is empty? One item? Contains special values (zero, None, NaN, Infinity, unicode)?
4. **Check round-trips**: Save and restore. Serialize and deserialize. Does everything survive?

---

## Lessons from LLM Audit Cycles

Real-world audits of AI-generated codebases consistently reveal patterns that single-file reviews miss. These lessons come from structured audit-and-fix cycles on production code.

### Audit in Layers, Not All at Once

Don't try to find everything in one pass. Use structured layers with different lenses:

1. **Automated scan** — patterns like hardcoded secrets, missing validations, unused imports
2. **Checklist-driven review** — cross-reference against your invariants and architecture docs
3. **Documentation sync** — verify docs match actual code (tool names, field lists, API surfaces)
4. **Production-readiness gap analysis** — rate limiting, error handling, security boundaries

Each pass catches things the previous one missed. A single exhaustive review is less thorough than multiple focused passes.

### Audit Reports Overcount — Group by Root Cause

A report listing 19 "bugs" often collapses to ~14 distinct code changes because many findings share a root cause (e.g., the same timezone pattern repeated in 3 files, or the same sentinel value problem in 5 functions). **Group findings by root cause before coding fixes, and fix in dependency order** — model changes first, then business logic, then consumers, then tests.

### Unused Imports Tell a Story

Finding the same unused import (`MarketNotFoundError`, `error_result`) across multiple files suggests copy-paste patterns during initial development. These aren't just style issues — they obscure what a module actually depends on and make it harder to reason about error handling paths. **After completing a feature, run a quick unused-import check.** It takes seconds and reveals architectural shortcuts.

### Don't Trust Documentation During Audits

Documentation drifts faster than you think. In one audit, 8 out of 18 tool names in an architecture doc were stale. Wrong tool names, wrong field lists, wrong tool counts. **Cross-reference everything against actual code.** When you fix code, grep for old names in every markdown file.

### Test What You Can, Note What You Can't

If some tests can't run (missing dependencies, uninstalled modules), don't skip testing entirely. Run the subset that can execute. 335 passing tests is infinitely better than zero tests because the other 50 couldn't run. **Document the gap so someone can close it later.**

---

## Human Review Checkpoints (Non-Negotiable)

These areas **require** human review before merging:

### Critical: Always Human Review

- **Security-critical code** (auth, permissions, data access)
- **Database migrations** (irreversible changes)
- **API contract changes** (breaking changes for clients)
- **Payment/financial logic** (money is involved)
- **Data deletion logic** (permanent data loss)
- **Encryption/crypto code** (easy to get wrong)
- **Production config changes** (can take down systems)

### High: Strong Human Review

- **Complex algorithms** (easy for AI to get subtle bugs)
- **State machines** (state transitions must be correct)
- **Concurrency code** (race conditions, deadlocks)
- **Performance-critical paths** (AI often inefficient)
- **Public APIs** (external contract)
- **Error handling** (must handle all cases)

### Medium: Careful Review

- **Business logic** (domain rules must be correct)
- **Data transformations** (edge cases)
- **Frontend state** (complex state management)
- **Test code** (tests must actually test)

### Low: Light Review

- **Boilerplate code** (simple CRUD)
- **Simple utilities** (pure functions)
- **Documentation** (verify accuracy)
- **Configuration** (if validated)

---

## Review Process

### Before Review

1. **Run all tests**
   ```bash
   # Tests must pass before review starts
   npm test
   # or
   pytest
   ```

2. **Run linters**
   ```bash
   # Catch style issues automatically
   npm run lint
   # or
   pylint src/
   ```

3. **Review the diff**
   ```bash
   git diff
   # Or use a visual diff tool
   ```

### During Review

**Read top-to-bottom**:
- Understand overall structure first
- Then dive into specifics
- Check each function/method individually

**Ask questions**:
- "Why this approach?"
- "What happens if [edge case]?"
- "Is this secure?"
- "Can this fail? How is failure handled?"

**Test mentally**:
- Walk through the logic
- Consider edge cases
- Think about failure modes

**Check references**:
- Does it match architecture?
- Does it follow invariants?
- Is it consistent with existing code?

### After Review

**If approved**:
- [ ] Tests pass
- [ ] Manually verified
- [ ] Security checked
- [ ] Invariants maintained
- [ ] Ready to commit

**If rejected**:
- Document specific issues
- Ask LLM to fix specific problems
- Don't merge partial fixes

**If needs iteration**:
- Request specific changes
- Review again after changes
- Don't assume fixes are correct

---

## Iterative Refinement

**Don't accept first output blindly.**

### Request Alternatives

```
This works, but I'm concerned about [issue].
Can you show me 2-3 alternative approaches with trade-offs?
```

### Ask for Explanation

```
Explain why you chose this approach over [alternative].
What are the trade-offs?
```

### Push Back

```
This violates our invariant [INV-001].
Please revise to maintain [specific requirement].
```

### Request Simplification

```
This seems overly complex for our use case.
Can you simplify this while maintaining correctness?
```

---

## Red Flags During Review

🚩 **"Looks too good"** - Suspiciously perfect code might have hidden issues

🚩 **Unfamiliar patterns** - AI using patterns you don't recognize

🚩 **Many edge cases unhandled** - AI focused on happy path only

🚩 **Commented-out code** - AI unsure about correctness

🚩 **Generic variable names** - `data`, `config`, `options` everywhere

🚩 **Missing error handling** - No try/catch or error checking

🚩 **Hardcoded values** - Magic numbers or strings

🚩 **Different style** - Doesn't match codebase conventions

🚩 **New dependencies** - Introduced without justification

🚩 **Overly complex** - More complicated than necessary

---

## Self-Review Prompt for LLM

Ask the LLM to review its own code:

```
Review the code you just wrote. Check for:
1. Security vulnerabilities
2. Edge cases not handled
3. Performance issues
4. Violations of our invariants (from INVARIANTS.md)
5. Inconsistencies with our architecture (from ARCHITECTURE.md)

Be critical. What could go wrong?
```

**Caution**: LLM self-review is useful but not sufficient. Human review still required.

---

## Quick Review Template

For each AI-generated change:

```markdown
## AI Code Review: [Feature/Fix Name]

### ✅ Verified Working
- [ ] Tests pass
- [ ] Manually tested
- [ ] Edge cases work

### 🔒 Security Check
- [ ] No injection vulnerabilities
- [ ] Input validation present
- [ ] Auth/authz correct
- [ ] No data leakage

### 📋 Requirements
- [ ] Solves the right problem
- [ ] Scope is correct
- [ ] No extra features added

### 🏗️ Architecture
- [ ] Follows existing patterns
- [ ] Respects invariants
- [ ] Appropriate complexity

### ⚡ Performance
- [ ] No obvious inefficiencies
- [ ] Scales appropriately
- [ ] Database queries indexed

### 🧪 Testing
- [ ] Good test coverage
- [ ] Tests are meaningful
- [ ] Edge cases tested

### Decision: [Approve / Request Changes / Reject]

**Notes**: [Any concerns or observations]
```

---

## Remember

**AI is a tool, not a teammate with judgment.**

It will:
- Make mistakes confidently
- Miss edge cases
- Generate insecure code
- Violate your architecture
- Produce inefficient solutions

**Your job is to catch these issues before they reach production.**

**Good AI-assisted development is 30% prompting and 70% reviewing.**
