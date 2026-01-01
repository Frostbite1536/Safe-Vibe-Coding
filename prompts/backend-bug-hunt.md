# Backend Bug Hunt Prompt

Use this prompt after implementing backend changes to proactively find server-side bugs.

---

## Prompt

You are a backend engineer performing a defensive bug hunt on server-side code. Your goal is to find bugs before they reach production.

**Code to review**: [specify files, commits, or describe changes]

---

## Backend-Specific Bug Categories

### 1. Data Integrity Issues

**Check for**:
- Missing database transactions where needed
- Race conditions in concurrent data access
- Partial updates that could leave data inconsistent
- Missing validation before database writes
- Improper handling of database constraints
- Data type mismatches (int vs string, nullable vs required)

**Questions**:
- Can this operation leave the database in an inconsistent state?
- What happens if two requests modify the same data simultaneously?
- Are foreign key constraints properly maintained?
- Can this create orphaned records?

### 2. API Contract Violations

**Check for**:
- Response format doesn't match documented schema
- Missing required fields in responses
- Incorrect HTTP status codes
- Breaking changes to existing endpoints
- Missing pagination on list endpoints
- Inconsistent error response formats

**Questions**:
- Does the API response match what clients expect?
- Are all documented fields present?
- Is versioning respected?
- Could this break existing clients?

### 3. Authentication & Authorization

**Check for**:
- Missing authentication checks
- Authorization bypasses (accessing resources you shouldn't)
- Insecure session handling
- Missing CSRF protection
- Inadequate permission checks
- Privilege escalation vulnerabilities

**Questions**:
- Can unauthenticated users access this endpoint?
- Can users access other users' data?
- Are role/permission checks complete?
- Can users modify data they shouldn't?

### 4. Input Validation & Injection

**Check for**:
- SQL injection vulnerabilities (non-parameterized queries)
- NoSQL injection
- Command injection
- Path traversal
- XML/XXE attacks
- Insufficient input sanitization

**Questions**:
- Are all inputs validated and sanitized?
- Are database queries parameterized?
- Can user input reach system commands?
- Are file paths validated?

### 5. State Management & Concurrency

**Check for**:
- Race conditions in shared state
- Missing locks on critical sections
- Deadlock potential
- Non-atomic operations that should be atomic
- Stale cache data
- Session state inconsistencies

**Questions**:
- Can concurrent requests interfere with each other?
- Is shared state properly synchronized?
- Are database transactions used correctly?
- Could this cause a deadlock?

### 6. Error Handling & Logging

**Check for**:
- Unhandled exceptions that crash the server
- Sensitive data in logs or error messages
- Missing error logging
- Exposing stack traces to clients
- Silent failures (errors caught but not logged)
- Generic error messages that hide real issues

**Questions**:
- What happens if this operation fails?
- Are errors properly logged?
- Do error messages leak sensitive info?
- Can failures be debugged from logs?

### 7. Resource Management

**Check for**:
- Connection leaks (database, network)
- File handle leaks
- Memory leaks
- Missing cleanup in error paths
- Unbounded resource consumption
- Missing timeouts on external calls

**Questions**:
- Are connections properly closed?
- What happens on error—are resources cleaned up?
- Can this exhaust server resources?
- Are there timeouts on slow operations?

### 8. Business Logic Errors

**Check for**:
- Incorrect calculations
- Wrong state transitions
- Missing boundary checks
- Improper handling of edge cases
- Violated business rules
- Incorrect assumptions about data

**Questions**:
- Does the logic match the requirements?
- Are all edge cases handled?
- Can business rules be violated?
- What happens with invalid state?

### 9. External Service Integration

**Check for**:
- Missing timeout/retry logic
- No circuit breaker for failing services
- Uncaught errors from external APIs
- Missing fallback behavior
- Assuming external service is always available
- Not validating external responses

**Questions**:
- What if the external service is down?
- What if it returns unexpected data?
- Are timeouts set?
- Is there retry logic?

### 10. Performance & Scalability

**Check for**:
- N+1 query problems
- Missing database indices
- Unbounded loops or queries
- Synchronous blocking on slow operations
- Missing pagination
- Inefficient algorithms on large datasets

**Questions**:
- How does this scale with data size?
- Are there N+1 queries?
- Could this block the event loop/thread pool?
- Is there a query that scans large tables?

---

## Output Format

For each bug found:

**Location**: [file:line or endpoint]

**Category**: [from categories above]

**Issue**: [description of the bug]

**Impact**: Critical / High / Medium / Low
- **Critical**: Data loss, security breach, system crash
- **High**: Data corruption, auth bypass, major malfunction
- **Medium**: Incorrect behavior, degraded performance
- **Low**: Edge case, unlikely scenario

**Scenario**: [how this bug manifests]

**Suggested fix**: [how to fix it]

---

## Example Bug Report

**Location**: `api/orders.py:47`

**Category**: Data Integrity

**Issue**: Order creation doesn't use database transaction

**Impact**: High

**Scenario**:
```python
# Current code
create_order(user_id, items)  # Inserts order
create_order_items(order_id, items)  # Inserts items
update_inventory(items)  # Updates stock

# If update_inventory fails, we have an order with no items
# and inventory wasn't decremented
```

**Suggested fix**: Wrap all three operations in a database transaction:
```python
with db.transaction():
    create_order(user_id, items)
    create_order_items(order_id, items)
    update_inventory(items)
```

---

## Red Flags

Watch for these patterns:

🚩 **No database transactions** in multi-step operations

🚩 **String concatenation** in SQL queries (not parameterized)

🚩 **Missing auth checks** on sensitive endpoints

🚩 **try/except pass** (silently swallowing errors)

🚩 **Time-of-check-time-of-use** bugs (checking then using stale data)

🚩 **Shared mutable state** without synchronization

🚩 **No timeouts** on external service calls

🚩 **User input** flowing into system commands, file paths, or queries

🚩 **Missing pagination** on list endpoints

🚩 **Secrets in code** or logs

---

## Invariant Check

Before completing the review:

- [ ] Review `INVARIANTS.md` for backend-specific rules
- [ ] Confirm all data integrity invariants are maintained
- [ ] Verify authorization invariants hold
- [ ] Check that API contracts are respected

**If any invariants are violated**: Flag as Critical bugs.

---

## Remember

Backend bugs often have severe consequences:
- Data corruption can be permanent
- Security bugs expose user data
- Race conditions are hard to reproduce
- Performance issues compound under load

**Be thorough. Production databases don't have undo.**
