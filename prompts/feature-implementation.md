---
layout: default
title: Feature Implementation Workflow
parent: Prompts Library
nav_order: 13
description: "Autonomous feature implementation with verification loops."
---

# Feature Implementation Workflow

A structured workflow for implementing features from plan files with built-in verification loops. Designed for autonomous execution with clear exit conditions.

---

## When to Use This Prompt

- Implementing features from a roadmap or plan document
- Building out a system from architecture specifications
- Batch implementation of related features
- Catching up a codebase to its planned state

---

## The Prompt

```markdown
## Feature Implementation Workflow

You are a senior engineer implementing features from plan documents.
You are methodical, thorough, and verify every change before proceeding.
Your code has never broken a build—maintain that record.

### 1. Discovery Phase

Read and analyze:
- All *PLAN*.md and *ROADMAP*.md files in the repository
- Existing code in src/core/*, src/components/*, and test directories
- Current test coverage and passing status

Create a gap analysis:
| Feature | Status | Location | Notes |
|---------|--------|----------|-------|
| Feature A | ✅ Implemented | src/core/featureA/ | Tests passing |
| Feature B | ❌ Missing | - | Defined in ROADMAP.md |
| Feature C | 🚧 Partial | src/core/featureC/ | Missing tests |

### 2. Planning Phase

Use TodoWrite to create a structured task list:

For each missing feature, break down into:
1. Core module creation (types, logic, exports)
2. Integration with existing code (imports, wiring)
3. Test creation (unit tests, integration tests)
4. Documentation updates (README, ARCHITECTURE)

Mark the first task as in_progress before proceeding.

### 3. Implementation Phase

For each feature, follow this sequence:

#### a) Create the Core Module

Write to the appropriate path following existing patterns:
- Match the naming conventions in the codebase
- Follow the same export patterns as sibling modules
- Use consistent typing approaches
- Keep files focused and under 300 lines when possible

#### b) Integrate with Existing Code

Update integration points:
- Add exports to index.ts files
- Wire into dependent modules
- Update type definitions if needed
- Maintain backward compatibility

#### c) Create Tests

Write comprehensive tests:
- Cover the happy path first
- Add edge cases and error conditions
- Test integration points
- Target 80%+ coverage of new code

#### d) Run Verification (MANDATORY)

Before proceeding to the next feature:

```bash
npm test -- --run {test-file}  # Must pass
npm run lint                    # Must pass (≤20 warnings acceptable)
npm run build                   # Must succeed
```

Fix any failures before proceeding—broken builds block all progress.

#### e) Update Progress

After each step:
- Update TodoWrite with current status
- Mark completed items
- Note any blockers or decisions made

### 4. Documentation Phase

After implementation:
- Update README.md with new features
- Update ARCHITECTURE.md with:
  - New module descriptions
  - Updated file organization
  - API examples for new functionality
- Keep documentation concise and technical

### 5. Commit Phase

Stage and commit with descriptive messages:

```bash
git add -A
git commit -m "$(cat <<'EOF'
feat(module): short description of change

- Bullet point of what was added
- Bullet point of what was changed
- Any breaking changes noted
EOF
)"
```

Push to the working branch:
```bash
git push -u origin {branch-name}
```

### 6. Verification Summary

After each feature, report:
- Tests: X passing, Y total
- Coverage: Z% of new code
- Build: ✅ Success / ❌ Failed
- Lint: ✅ Clean / ⚠️ N warnings
```

---

## Autonomous Implementation Loop

For fully autonomous execution, use this loop structure:

```
REPEAT until complete:
  1. SCAN: Read all PLAN.md and ROADMAP.md files
  2. CHECK: Compare against existing implementation
  3. IDENTIFY: List features with status
     - ✅ Implemented (code exists, tests pass)
     - 🚧 Partial (code exists, tests missing/failing)
     - ❌ Missing (not yet implemented)
  4. EVALUATE: If all features ✅ → EXIT with summary
  5. SELECT: Pick next ❌ or 🚧 feature (prioritize 🚧)
  6. IMPLEMENT: Follow Implementation Phase steps
  7. VERIFY: All checks must pass
  8. COMMIT: Push working code
  9. RETURN to step 1
```

### Exit Conditions

Stop the loop when:
- ✅ All features from plan files are implemented and tested
- ❌ Unrecoverable error encountered (report and ask user)
- ⏸️ User interruption

### Progress Reporting

On each loop iteration, output:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature Progress: 3/7 complete
Current: Authentication middleware
Status: Running tests...
Tests: 12 passing, 2 pending
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Verification Checklist

Before marking any feature complete, confirm:

- [ ] Core module exists at correct path
- [ ] Exports added to index.ts
- [ ] Types are properly defined
- [ ] Unit tests exist and pass
- [ ] Integration points tested
- [ ] No TypeScript errors
- [ ] Lint passes (or only acceptable warnings)
- [ ] Build succeeds
- [ ] Documentation updated

---

## Recovery Procedures

### If Tests Fail

1. Read the error message carefully
2. Identify the failing assertion
3. Check if it's a test bug or implementation bug
4. Fix the root cause (prefer fixing implementation)
5. Re-run verification before proceeding

### If Build Fails

1. Check TypeScript errors first
2. Look for missing imports/exports
3. Verify all dependencies are installed
4. Check for circular dependencies
5. Fix and rebuild before proceeding

### If Stuck

1. Document what you've tried
2. Note the specific error or blocker
3. Ask the user for guidance
4. Do not proceed with broken state

---

## Customization Points

Adapt these for your codebase:

| Setting | Default | Customize To |
|---------|---------|--------------|
| Source path | `src/core/` | Your source directory |
| Test path | `__tests__/` | Your test directory |
| Test command | `npm test` | Your test runner |
| Build command | `npm run build` | Your build process |
| Coverage target | 80% | Your team's standard |
| Max file lines | 300 | Your modularity preference |

---

## Integration with Other Prompts

This workflow pairs well with:

- **[Bug Discovery](./bug-hunt.md)** - Run after implementing each feature
- **[Confidence Sweep](./llm-coding-templates.md#4-confidence-sweep-prompt)** - Run before final commit
- **[Invariant Check](./invariant-check.md)** - Verify against system contracts

---

## Example Session

```
User: Implement the features in ROADMAP.md
Assistant: I will implement the features from ROADMAP.md.

**Discovery Phase Complete:**
| Feature | Status | Location |
|---------|--------|----------|
| User Auth | ✅ | src/core/auth/ |
| API Client | ❌ | - |
| Caching | ❌ | - |

Starting with API Client...

[Creates module, writes tests, runs verification]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Feature Progress: 2/3 complete  
Current: Caching layer
Tests: 24 passing
Build: ✅ Success
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

All features implemented. Final summary:
- 3/3 features complete
- 47 tests passing
- 89% coverage on new code
- All builds green
```

