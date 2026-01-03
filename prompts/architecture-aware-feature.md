---
layout: default
title: Architecture-Aware Feature
parent: Prompts Library
nav_order: 7
---

# Architecture-Aware Feature Prompt

Use this prompt when adding new functionality to an existing system. It ensures the feature aligns with architecture and respects invariants.

---

## Prompt

You are extending an existing system with a new feature. Your implementation must respect the established architecture and system contracts.

**Feature to implement**: [describe the feature]

**Context**: [relevant background or user requirements]

---

## Before You Write Any Code

Complete these steps in order:

### 1. Architecture Review

**Read the following documents**:
- `ARCHITECTURE.md` - Understand the system structure
- `INVARIANTS.md` - Know the non-negotiable rules
- `README.md` - Understand setup and conventions

**Then answer**:
- Where does this feature belong in the current architecture?
- Which existing components will it interact with?
- Does this require new components, or does it extend existing ones?
- What's the data flow for this feature?

### 2. Invariant Check

**Review each invariant** in `INVARIANTS.md` and confirm:
- Does this feature violate any existing invariants?
- Does this feature require new invariants to be added?
- Are there edge cases where invariants might be broken?

**If any conflicts exist**: Flag them immediately and propose how to resolve (either change the approach or update the invariant with explicit approval).

### 3. Testing Strategy

**Identify what tests are needed**:
- What's the happy path?
- What edge cases exist?
- How do we test failure modes?
- Which existing tests might be affected?
- What integration points need testing?

**Plan to write tests alongside the implementation, not after.**

### 4. Integration Plan

**Determine how this integrates**:
- What's the public API/interface for this feature?
- What configuration or setup is required?
- How does this affect existing functionality?
- Are there backwards compatibility concerns?
- What documentation needs updating?

---

## Implementation Guidelines

Once planning is complete:

**Minimal Surface Area**:
- Implement only what's requested
- Don't refactor unrelated code
- Don't add "nice to have" features
- Keep changes localized

**Follow Existing Patterns**:
- Match the coding style of the codebase
- Use the same libraries/frameworks already in use
- Follow established naming conventions
- Respect the module structure

**Maintain Modularity**:
- Keep new files focused and < 1,500 lines
- If extending existing files, consider extracting new modules instead
- Maintain clear boundaries between components

**Explicit Over Implicit**:
- Make dependencies clear
- Avoid hidden state or side effects
- Document any new assumptions
- Make error cases explicit

---

## Implementation Checklist

Before submitting your implementation:

- [ ] Feature works as specified (tested manually)
- [ ] Tests added and passing
- [ ] No system invariants violated
- [ ] Follows existing architecture patterns
- [ ] Documentation updated (README, ARCHITECTURE.md if needed)
- [ ] No new security vulnerabilities introduced
- [ ] Error handling in place
- [ ] Edge cases handled
- [ ] Code is modular and clear
- [ ] No unrelated changes included

---

## Output Format

Provide your implementation in this format:

### 1. Architecture Summary

**Where this fits**: [brief explanation]

**Components affected**:
- [Component 1]: [what changes]
- [Component 2]: [what changes]

**Data flow**: [describe the flow through the system]

### 2. Invariant Confirmation

**Checked invariants**:
- [INV-001]: ✅ Not affected
- [INV-002]: ✅ Maintained through [how]
- [INV-003]: ⚠️ Requires discussion: [explain conflict]

**New invariants needed**: [if any]

### 3. Test Plan

**Tests to add**:
- Test 1: [description]
- Test 2: [description]

**Existing tests affected**: [if any]

### 4. Implementation

[Your code here, organized by file]

### 5. Documentation Updates

**README.md**: [changes needed]

**ARCHITECTURE.md**: [changes needed, if any]

**Other docs**: [changes needed, if any]

---

## Red Flags to Avoid

❌ **Don't** start coding before understanding the architecture

❌ **Don't** skip the invariant check

❌ **Don't** add the feature "creatively" if it doesn't fit the architecture—flag the issue instead

❌ **Don't** write code first and tests later

❌ **Don't** introduce new dependencies without justification

❌ **Don't** refactor unrelated code as part of this feature

---

## Remember

The goal is **safe feature addition**. If you're unsure how the feature fits, or if it conflicts with invariants, **ask before implementing**. It's better to clarify the approach than to build the wrong thing correctly.

**You're not just adding a feature—you're maintaining the integrity of a system.**
