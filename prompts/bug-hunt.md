# Bug Hunt Prompt

Use this prompt after implementing features or making significant changes to proactively find bugs.

---

## Prompt

You are conducting a thorough bug hunt on recent code changes. Your goal is to find bugs **before** they reach production.

**Review the following changes**: [paste git diff or describe changes]

**Review methodology**:

1. **Logic Errors**:
   - Check conditional logic (off-by-one, incorrect operators, wrong branch taken)
   - Verify loop termination conditions
   - Check for unhandled edge cases
   - Look for incorrect default values

2. **Data Flow Issues**:
   - Trace data through the system
   - Check for data type mismatches or coercion issues
   - Verify nullability assumptions
   - Check for mutations where immutability is expected

3. **Error Handling**:
   - Are all error paths handled?
   - Do error handlers actually handle the error (or just log and continue)?
   - Can exceptions escape unhandled?
   - Are errors surfaced to users appropriately?

4. **Race Conditions & Concurrency**:
   - Check for shared mutable state
   - Verify thread-safety assumptions
   - Look for time-of-check-time-of-use bugs
   - Check for missing locks or synchronization

5. **Resource Management**:
   - Are files/connections/handles properly closed?
   - Check for memory leaks
   - Verify cleanup in error paths (not just happy path)

6. **Security Vulnerabilities**:
   - SQL injection, XSS, command injection
   - Missing authentication/authorization checks
   - Insecure defaults
   - Sensitive data leakage (logs, error messages, responses)

7. **Boundary Conditions**:
   - Empty collections
   - Null/undefined values
   - Maximum values (integer overflow, buffer overflow)
   - Minimum values (underflow, negative indices)

8. **Integration Issues**:
   - API contract violations
   - Incorrect assumptions about external services
   - Missing timeout/retry logic
   - Deserialization errors

9. **Performance Problems**:
   - N+1 queries
   - Unnecessary loops or operations
   - Missing database indices
   - Large object allocations in hot paths

10. **Invariant Violations**:
    - Check against INVARIANTS.md
    - Does this code maintain all system invariants?
    - Are there new code paths that bypass existing checks?

**Output format**:

For each potential bug found:
- **Location**: [file:line or function name]
- **Type**: [category from above]
- **Issue**: [description of the problem]
- **Impact**: [High/Medium/Low]
- **Suggested fix**: [how to fix it]

If no bugs found, explicitly state: "No bugs detected in this review" and list what was checked.

**Remember**: It's better to flag a false positive than miss a real bug.
