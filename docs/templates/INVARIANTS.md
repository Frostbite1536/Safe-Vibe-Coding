# System Invariants & Contracts

## Purpose

This document defines the **non-negotiable truths** of the system: rules that must always hold, regardless of UI, API path, ingest source, or future feature additions. These invariants are the foundation for correctness, trust, and long-term maintainability.

**If a change violates an invariant, it is a bug or a product decision—never an implementation detail.**

---

## How to Use This Document

1. **Before implementing any feature**: Review this document to ensure compliance
2. **During code review**: Check that changes respect all invariants
3. **When debugging**: Verify that invariants still hold
4. **When changing an invariant**: Document why, get explicit approval, update tests

---

## Data Integrity Invariants

### INV-DATA-001: [Invariant Name]

**Rule**: [Clear statement of what must always be true]

**Rationale**: [Why this matters]

**Examples**:
- ✅ Valid: [Example of correct behavior]
- ❌ Invalid: [Example of violation]

**Enforcement**: [How this is guaranteed - database constraints, validation, tests]

---

## Security Invariants

### INV-SEC-001: [Invariant Name]

**Rule**:

**Rationale**:

**Examples**:
- ✅ Valid:
- ❌ Invalid:

**Enforcement**:

---

## Authorization Invariants

### INV-AUTH-001: [Invariant Name]

**Rule**:

**Rationale**:

**Examples**:
- ✅ Valid:
- ❌ Invalid:

**Enforcement**:

---

## Consistency Invariants

### INV-CONS-001: [Invariant Name]

**Rule**:

**Rationale**:

**Examples**:
- ✅ Valid:
- ❌ Invalid:

**Enforcement**:

---

## Ordering & Timing Invariants

### INV-ORD-001: [Invariant Name]

**Rule**:

**Rationale**:

**Examples**:
- ✅ Valid:
- ❌ Invalid:

**Enforcement**:

---

## Idempotency Invariants

### INV-IDEMP-001: [Invariant Name]

**Rule**:

**Rationale**:

**Examples**:
- ✅ Valid:
- ❌ Invalid:

**Enforcement**:

---

## Performance & Availability Invariants

### INV-PERF-001: [Invariant Name]

**Rule**:

**Rationale**:

**Examples**:
- ✅ Valid:
- ❌ Invalid:

**Enforcement**:

---

## Cross-Component Contract Invariants

These invariants govern data as it crosses boundaries between components. LLM-generated code characteristically fails at these seams — each module works in isolation, but the contracts between modules are implicit and sometimes contradictory.

### INV-XCOMP-001: [Data Round-Trip Integrity]

**Rule**: [e.g., "Serializing and deserializing a Trade object must preserve all 14 fields with identical values and types"]

**Rationale**: Fields silently lost in persistence, serialization, or API round-trips cause data corruption that may not be detected until much later.

**Boundaries to verify**:
- Database save → restore
- JSON serialize → deserialize
- API request → response → client parse
- File export → import

**Enforcement**: [e.g., "Round-trip test for each data type that crosses a boundary"]

### INV-XCOMP-002: [Type Consistency Across Layers]

**Rule**: [e.g., "All monetary calculations use Decimal internally but convert to float before serialization"]

**Rationale**: Type leakage across boundaries (e.g., `Decimal` into JSON, `datetime` into a dict) causes serialization crashes or silent data loss.

**Enforcement**: [e.g., "Serializer tests with Decimal, datetime, None, and NaN inputs"]

### INV-XCOMP-003: [State Atomicity on Failure]

**Rule**: [e.g., "If any multi-step operation fails partway, the system state must be rolled back to its pre-operation state"]

**Rationale**: Partial state after a failure leaves the system in a state no code path was designed to handle.

**Enforcement**: [e.g., "Build new state in temporary variables; swap atomically on success"]

---

## API Contract Invariants

### INV-API-001: [Invariant Name]

**Rule**:

**Rationale**:

**Examples**:
- ✅ Valid:
- ❌ Invalid:

**Enforcement**:

---

## Testing Requirements

All invariants must be covered by:
- [ ] Unit tests
- [ ] Integration tests
- [ ] Property-based tests (where applicable)
- [ ] Runtime assertions (where appropriate)

---

## Invariant Change Log

| Date | Invariant ID | Change | Reason | Approved By |
|------|--------------|---------|--------|-------------|
| [YYYY-MM-DD] | [ID] | [Added/Modified/Removed] | [Explanation] | [Name] |

---

**Last Updated**: [Date]
**Reviewed By**: [Team/Person]
