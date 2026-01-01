# Anti-Patterns & Warning Signs: When AI Development Goes Wrong

Not all AI-assisted development is productive. Sometimes the LLM leads you astray, wastes time, or introduces problems faster than it solves them. This document helps you recognize when things are going wrong and how to course-correct.

---

## Core Warning Signs

### 1. You're Explaining the Same Thing Repeatedly

**Symptom**: The LLM keeps forgetting or misunderstanding the same concept.

**What's happening**: Context pollution or fundamental misunderstanding.

**Fix**:
- Start a fresh conversation with better initial context
- Explicitly document the concept in architecture or invariants docs
- Reference the documentation instead of re-explaining

**Prevention**: Include critical concepts in warm-up context for every session.

---

### 2. Code Quality Is Degrading

**Symptom**: Early code was good, but recent outputs are messy, inconsistent, or buggy.

**What's happening**: Context drift, accumulated errors, or conversation fatigue.

**Fix**:
- Stop and review what you have
- Commit working code
- Start fresh session with checkpoint summary
- Refactor problematic code before continuing

**Prevention**: Regular checkpoints every 30-60 minutes.

---

### 3. Scope Is Expanding Uncontrollably

**Symptom**: Simple task balloons into extensive refactoring or feature additions.

**What's happening**: Lack of clear boundaries, LLM over-engineering, or unclear requirements.

**Fix**:
- Stop immediately
- Review original goal
- Explicitly state: "We are ONLY doing [specific task]"
- Roll back scope creep

**Prevention**: Be extremely specific about what's in-scope and out-of-scope.

---

### 4. You're Accepting Code You Don't Understand

**Symptom**: Merging AI outputs without fully grasping what they do.

**What's happening**: Moving too fast, trusting the LLM too much.

**Fix**:
- **STOP IMMEDIATELY**
- Review code line-by-line
- Ask LLM to explain anything unclear
- Refactor for clarity if needed
- Never merge code you don't understand

**Prevention**: Insist on clarity. Ask "Explain this line-by-line" if needed.

---

### 5. Tests Are Passing But Features Don't Work

**Symptom**: Green tests, broken functionality.

**What's happening**: Weak tests, tests testing the wrong thing, or tests written to match broken code.

**Fix**:
- Manually test the feature
- Review test assertions carefully
- Strengthen tests
- Delete meaningless tests

**Prevention**: Review tests as critically as production code.

---

### 6. You're Constantly Debugging AI Output

**Symptom**: More time fixing AI code than it would take to write it yourself.

**What's happening**: Wrong tool for the job, unclear prompts, or complex task poorly suited for AI.

**Fix**:
- Consider writing this code yourself
- Simplify the problem
- Break into smaller pieces
- Improve your prompts

**Prevention**: Know when AI helps and when it hinders.

---

### 7. Architecture Is Becoming Incoherent

**Symptom**: New code doesn't fit existing patterns, inconsistent approaches.

**What's happening**: LLM doesn't understand your architecture or isn't following it.

**Fix**:
- **Stop adding features**
- Review architecture doc
- Refactor recent changes to align
- Strengthen architecture-aware prompts

**Prevention**: Always reference architecture docs in prompts.

---

### 8. The LLM Keeps Suggesting the Same Failed Approach

**Symptom**: After you reject a solution, it suggests a trivial variation.

**What's happening**: LLM locked into a pattern, not exploring alternatives.

**Fix**:
```
Stop suggesting variations of [failed approach].
Please try a completely different approach.
Consider: [alternative direction]
```

**Prevention**: Explicitly rule out dead-ends: "Do not use [X] approach."

---

### 9. Security Is an Afterthought

**Symptom**: Code has obvious security flaws after implementation.

**What's happening**: LLM prioritizing functionality over security.

**Fix**:
- Review all code for security issues
- Add security requirements to prompts
- Use security-focused bug hunt

**Prevention**: Explicitly require secure coding upfront: "Include input validation and prevent SQL injection."

---

### 10. You're In Analysis Paralysis

**Symptom**: LLM generates extensive plans but little working code.

**What's happening**: Over-planning, under-doing.

**Fix**:
- Skip to implementation
- Build smallest working version
- Iterate from there

**Prevention**: "Show me a minimal working implementation first, we can improve it after."

---

## Anti-Pattern Catalog

### Anti-Pattern: The Endless Refactor

**What it looks like**: Every change triggers a refactoring cascade.

**Why it's bad**: Never actually ships features, increases risk.

**Fix**: Limit refactoring. "Make this change with minimal impact to existing code."

---

### Anti-Pattern: Framework Fever

**What it looks like**: LLM suggests complex frameworks or libraries for simple problems.

**Why it's bad**: Unnecessary dependencies, over-engineering.

**Example**:
```
❌ "Use Redux for state management"
✅ "Use React useState for this simple case"
```

**Fix**: "Solve this with standard library / existing dependencies only."

---

### Anti-Pattern: Pattern Misapplication

**What it looks like**: Design patterns used where simple code would work.

**Why it's bad**: Unnecessary complexity, harder to maintain.

**Example**:
```
❌ Singleton pattern for configuration
❌ Factory pattern for simple object creation
❌ Observer pattern for one-time events
```

**Fix**: "Use the simplest approach that works."

---

### Anti-Pattern: Abstraction Explosion

**What it looks like**: Layers of abstractions for minimal code.

**Why it's bad**: Hard to understand, hard to debug.

**Example**:
```
❌ BaseManager → AbstractDataManager → UserDataManager → UserRepository
✅ UserRepository (just one class)
```

**Fix**: "Don't create abstractions unless we need them in at least 3 places."

---

### Anti-Pattern: Testing Theater

**What it looks like**: Many tests, low actual coverage of important cases.

**Why it's bad**: False sense of security, tests don't catch real bugs.

**Example**:
```typescript
❌ test('function exists', () => {
    expect(myFunction).toBeDefined();
});

✅ test('handles null user correctly', () => {
    expect(() => myFunction(null)).toThrow('User required');
});
```

**Fix**: "Write tests that verify behavior, not existence."

---

### Anti-Pattern: The God File

**What it looks like**: Single file growing to thousands of lines.

**Why it's bad**: LLM can't fully reason about it, hard to maintain.

**Example**: `utils.js` with 50 unrelated functions.

**Fix**: Split by responsibility. Use modularity review prompt.

---

### Anti-Pattern: Comment-Driven Development

**What it looks like**: Heavy comments explaining confusing code.

**Why it's bad**: Code should be self-explanatory.

**Example**:
```python
❌ # Loop through users and check if they match
   for u in users:
       # Compare user id with target
       if u.id == target_id:
           return u

✅ def find_user_by_id(users, target_id):
       return next((u for u in users if u.id == target_id), None)
```

**Fix**: "Refactor for clarity instead of adding comments."

---

### Anti-Pattern: Copy-Paste Coding

**What it looks like**: LLM generates similar code multiple times instead of refactoring.

**Why it's bad**: Violates DRY, harder to maintain.

**Fix**: "Extract common logic into a shared function."

---

### Anti-Pattern: The Over-Engineered API

**What it looks like**: APIs with many options, parameters, overloads.

**Why it's bad**: Confusing, hard to use correctly.

**Example**:
```python
❌ def process(data, mode='sync', async_=False, callback=None,
              error_handler=None, retry=True, timeout=None, ...)
```

**Fix**: "Create a simple API with sensible defaults."

---

### Anti-Pattern: Silent Failure Cascade

**What it looks like**: Errors caught and swallowed throughout the code.

**Why it's bad**: Bugs hide, debugging is impossible.

**Example**:
```python
❌ try:
       critical_operation()
   except:
       pass  # Silently fails
```

**Fix**: "Handle errors explicitly or let them propagate."

---

### Anti-Pattern: Database Query Explosion

**What it looks like**: N+1 queries, missing eager loading.

**Why it's bad**: Terrible performance.

**Example**:
```python
❌ for user in users:
       user.posts  # Separate query for each user!
```

**Fix**: Run performance review prompt after database code.

---

## Recognizing Context Pollution

**Signs context is polluted**:

1. LLM contradicts itself
2. Suggests code violating earlier constraints
3. "Forgets" decisions from same conversation
4. Responses become generic/vague
5. Solutions ignore project-specific context

**Recovery**:
- Generate checkpoint summary
- Commit working code
- Start fresh conversation
- Provide corrected context upfront

---

## When AI Is The Wrong Tool

**AI struggles with**:
- Highly complex algorithms requiring deep reasoning
- Code requiring deep domain expertise
- Performance-critical low-level code
- Novel approaches (AI prefers common patterns)
- Debugging race conditions or subtle timing issues

**When to code yourself**:
- You could write it faster than explaining it
- Security is critical and complexity is high
- Performance requirements are stringent
- You're learning a new technology (don't let AI rob you of understanding)

**AI excels at**:
- Boilerplate generation
- Standard CRUD operations
- Test case generation
- Refactoring for clarity
- Documentation
- Common patterns implementation

---

## Course Correction Strategies

### Hard Reset

When things are seriously off track:

1. **Stop coding**
2. **Commit or stash work**
3. **Review roadmap and architecture**
4. **Identify what went wrong**
5. **Start fresh with corrected approach**
6. **Cherry-pick good code from failed attempt**

### Gentle Correction

For minor drift:

1. **Checkpoint current state**
2. **Explicitly state the issue**
3. **Reference docs (architecture, invariants)**
4. **Request specific correction**
5. **Verify fix before continuing**

### Scope Reset

When scope has creeped:

```
Let's reset scope. We are ONLY doing:
- [Specific task 1]
- [Specific task 2]

We are NOT doing:
- [Out of scope item 1]
- [Out of scope item 2]

Please focus exclusively on the in-scope items.
```

---

## Velocity Red Flags

**You should be moving faster with AI, not slower.**

If you're experiencing:
- More debugging than writing
- More explaining than coding
- More refactoring than progressing
- More testing than implementing

**Something is wrong.** Time to reassess.

---

## Quality Red Flags

**Code quality should remain high.**

If you're seeing:
- Declining test coverage
- More bugs in new code
- Harder-to-read code
- Architecture drift

**Stop and course-correct.**

---

## Trust Red Flags

**You should trust the code you're merging.**

If you're:
- Merging code you don't understand
- Skipping review "just this once"
- Accepting solutions that feel wrong
- Ignoring security concerns

**You've lost control.** Reset immediately.

---

## Emergency Checklist

When things feel wrong:

- [ ] **Stop adding features**
- [ ] Run all tests
- [ ] Review recent commits
- [ ] Check architecture alignment
- [ ] Verify invariants hold
- [ ] Review security
- [ ] Generate checkpoint summary
- [ ] Identify specific problems
- [ ] Start fresh or roll back

**Don't dig deeper when you're in a hole.**

---

## Prevention Is Better Than Cure

**Best practices to avoid anti-patterns**:

1. ✅ Clear, specific prompts
2. ✅ Reference architecture and invariants
3. ✅ Regular checkpoints
4. ✅ Strict code review
5. ✅ Human review for critical code
6. ✅ Test everything
7. ✅ Start fresh when confused
8. ✅ Push back on bad suggestions
9. ✅ Maintain focus
10. ✅ Know when to code yourself

---

## Remember

**AI amplifies both good and bad practices.**

- Good process + AI = Velocity
- Bad process + AI = Faster accumulation of technical debt

**Your job is to maintain discipline.**

The LLM will happily lead you off a cliff if you let it. Stay vigilant, trust your judgment, and course-correct early.

**When in doubt, slow down and review.**
