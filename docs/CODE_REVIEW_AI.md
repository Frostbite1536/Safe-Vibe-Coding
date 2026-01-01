# Code Review Practices for AI-Generated Code

AI-generated code requires different review practices than human-written code. LLMs can produce syntactically correct code that is nonetheless wrong, insecure, or inefficient. This document outlines how to review AI outputs effectively.

---

## Core Principle

**Never merge AI-generated code without human review.**

Even with excellent prompts and strong guardrails, LLMs make mistakes. Your job as the human is to be the final quality gate.

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
