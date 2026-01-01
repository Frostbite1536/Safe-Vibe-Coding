# Invariant Check Prompt

Use this prompt to verify that code changes respect system invariants and contracts.

---

## Prompt

You are performing an invariant check. Your job is to compare proposed code changes against the System Invariants & Contracts document and identify violations, ambiguities, or required updates.

**Changes to review**: [describe changes, paste diff, or specify files]

**Invariants document**: `INVARIANTS.md`

---

## Review Process

### 1. Read the Invariants

Read the complete `INVARIANTS.md` document. Understand:
- What rules must always hold
- Why each invariant exists
- How they're enforced
- What violations would mean

### 2. Analyze Each Change

For each code change, ask:
- Does this maintain all existing invariants?
- Does this introduce new behavior that needs invariants?
- Could this create edge cases where invariants break?
- Are enforcement mechanisms still in place?

### 3. Check Systematically

Go through each invariant category:

**Data Integrity Invariants**:
- [ ] All data rules still hold
- [ ] Database constraints still enforced
- [ ] Validation still in place

**Security Invariants**:
- [ ] Security boundaries maintained
- [ ] Authentication/authorization still required
- [ ] No new attack vectors

**Authorization Invariants**:
- [ ] Permission checks still present
- [ ] Access controls unchanged (or properly updated)
- [ ] No privilege escalation possible

**Consistency Invariants**:
- [ ] State remains consistent
- [ ] No new race conditions
- [ ] Transactions still wrap multi-step operations

**Ordering & Timing Invariants**:
- [ ] Sequence requirements met
- [ ] Timing constraints preserved
- [ ] No out-of-order operations

**Idempotency Invariants**:
- [ ] Idempotent operations remain so
- [ ] Retry safety maintained
- [ ] Duplicate request handling unchanged

**Performance & Availability Invariants**:
- [ ] Performance guarantees met
- [ ] No unbounded operations introduced
- [ ] Timeouts still in place

**API Contract Invariants**:
- [ ] API contracts unchanged (or versioned properly)
- [ ] Response formats consistent
- [ ] Backwards compatibility maintained

---

## Output Format

### Invariant Compliance Report

#### ✅ Invariants Maintained

List each invariant that is properly maintained:

**[INV-ID]**: [Invariant Name]
- **Status**: ✅ Maintained
- **How**: [brief explanation of how this change maintains the invariant]

#### ⚠️ Invariants Requiring Attention

List invariants that need discussion or clarification:

**[INV-ID]**: [Invariant Name]
- **Status**: ⚠️ Needs Review
- **Issue**: [what's unclear or potentially problematic]
- **Recommendation**: [suggest next steps]

#### ❌ Invariant Violations

List any clear violations:

**[INV-ID]**: [Invariant Name]
- **Status**: ❌ **VIOLATED**
- **Violation**: [how this change breaks the invariant]
- **Impact**: [what could go wrong]
- **Required Action**: [must fix or must update invariant with approval]

#### 🆕 New Invariants Needed

List new invariants that should be added:

**New Invariant**: [Proposed Name]
- **Rule**: [what should always be true]
- **Rationale**: [why this is needed]
- **Enforcement**: [how it will be guaranteed]
- **Category**: [which invariant category this belongs to]

---

## Decision Framework

For each finding, recommend one of:

### ✅ Proceed
- All invariants maintained
- No violations found
- Code can be merged as-is

### ⚠️ Discuss
- Ambiguous whether invariant holds
- Edge cases need clarification
- May require minor adjustments

### ❌ Block
- Clear invariant violation
- Must either:
  1. Fix the code to maintain the invariant, OR
  2. Get explicit approval to update the invariant (with documentation)

### 🆕 Extend
- Change is fine but needs new invariants documented
- Add to INVARIANTS.md before merging

---

## Example Report

### Changes Reviewed
Modified user authentication to support OAuth in addition to password auth.

### ✅ Invariants Maintained

**INV-SEC-001**: All API endpoints require authentication
- **Status**: ✅ Maintained
- **How**: OAuth tokens validated with same middleware as password auth

**INV-AUTH-002**: Users can only access their own data
- **Status**: ✅ Maintained
- **How**: OAuth tokens include user_id, same permission checks apply

### ⚠️ Invariants Requiring Attention

**INV-DATA-003**: Email must be unique per user
- **Status**: ⚠️ Needs Review
- **Issue**: OAuth providers might not guarantee unique emails
- **Recommendation**: Add check to prevent duplicate OAuth emails, or update invariant to clarify scope

### ❌ Invariant Violations

**INV-SEC-004**: Passwords must be hashed with bcrypt
- **Status**: ❌ **VIOLATED**
- **Violation**: OAuth users have no password, code assumes password field exists
- **Impact**: Crashes when trying to hash null password
- **Required Action**: Update code to allow null password for OAuth users

### 🆕 New Invariants Needed

**New Invariant**: OAuth tokens must be validated on every request
- **Rule**: OAuth tokens cannot be trusted without server-side validation
- **Rationale**: Client could send expired or forged tokens
- **Enforcement**: Middleware validates with OAuth provider
- **Category**: Security Invariants

---

## Red Flags

Watch for changes that:

🚩 **Remove validation** without replacement

🚩 **Skip authentication checks** in new code paths

🚩 **Bypass existing enforcement mechanisms**

🚩 **Introduce new state** without consistency rules

🚩 **Change API contracts** without versioning

🚩 **Assume data exists** when invariants don't guarantee it

🚩 **Make operations non-idempotent** that were previously safe to retry

---

## Severity Levels

**Critical Violations**:
- Security invariants broken
- Data integrity compromised
- Production reliability at risk

**High Violations**:
- Authorization bypassed
- Data consistency not guaranteed
- API contracts broken

**Medium Violations**:
- Performance guarantees missed
- Edge cases not handled
- Documentation out of sync

**Low Violations**:
- Minor inconsistencies
- Unclear whether invariant applies
- Opportunities to strengthen invariants

---

## Remember

**Invariants exist for a reason**. If a change requires violating an invariant, one of three things is true:

1. **The code is wrong** - Fix the implementation
2. **The requirement is wrong** - Push back on the feature
3. **The invariant is wrong** - Update it with explicit approval and documentation

Invariants should rarely change. If you find yourself updating invariants frequently, the system may lack clarity about its core contracts.

**When in doubt, maintain the invariant.**
