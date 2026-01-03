---
layout: default
title: Version Control
nav_order: 5
parent: Guides
description: "Git workflow and best practices for AI-assisted development."
---

# Version Control Best Practices for AI-Assisted Development

AI-generated code requires careful version control practices. Because code appears quickly, it's tempting to commit large batches without proper review. This document outlines how to use git effectively when working with LLMs.

---

## Core Principles

1. **Commit only code you've reviewed**
2. **Make atomic commits** (one logical change per commit)
3. **Write meaningful commit messages**
4. **Review diffs before committing**
5. **Test before committing**

---

## The Commit Workflow

```mermaid
graph TD
    A([AI Generates Code]) --> B{Tests Pass?}
    B -- No --> C[Fix Code]
    C --> B
    B -- Yes --> D{Linter Clean?}
    D -- No --> E[Run Linter Fix]
    E --> D
    D -- Yes --> F[Review Diff]
    F --> G{Understand All Changes?}
    G -- No --> H[Investigate Code]
    H --> G
    G -- Yes --> I{Secure & Correct?}
    I -- No --> J[Make Corrections]
    J --> B
    I -- Yes --> K([Commit])

    style A fill:#e1f5fe,stroke:#01579b
    style B fill:#fff9c4,stroke:#fbc02d
    style D fill:#fff9c4,stroke:#fbc02d
    style G fill:#fff9c4,stroke:#fbc02d
    style I fill:#fff9c4,stroke:#fbc02d
    style K fill:#c8e6c9,stroke:#2e7d32
    style C fill:#ffcdd2,stroke:#c62828
    style J fill:#ffcdd2,stroke:#c62828
```

### Before Committing

#### 1. Run Tests

```bash
# All tests must pass
npm test
# or
pytest
# or
cargo test
```

**Never commit broken code.** Even if "it works locally," tests must pass.

#### 2. Run Linters

```bash
# Fix style issues automatically
npm run lint --fix
# or
black .
pylint src/
# or
cargo fmt
cargo clippy
```

**Fix all linter errors before committing.**

#### 3. Review the Diff

```bash
# See what's changed
git diff

# Or use a visual diff tool
git difftool
```

**Read every line.** Ask yourself:
- Do I understand what this does?
- Is this necessary?
- Are there any obvious bugs?
- Is it secure?

### The Commit

#### Atomic Commits

**Good**: One logical change per commit

```bash
✅ git add src/auth/oauth.ts tests/auth/oauth.test.ts
   git commit -m "Add OAuth authentication support"

✅ git add src/middleware/logging.ts
   git commit -m "Fix logging middleware error handling"
```

**Bad**: Multiple unrelated changes

```bash
❌ git add .
   git commit -m "Various fixes and features"
   # This commit has: OAuth, logging fix, UI changes, refactoring
```

#### When to Commit

**Commit after**:
- ✅ Feature works (manually tested)
- ✅ Tests pass
- ✅ Code reviewed
- ✅ No linter errors
- ✅ Diff reviewed

**Don't commit**:
- ❌ "Just to save progress" (use `git stash` instead)
- ❌ Broken code (even temporarily)
- ❌ Unreviewed AI output
- ❌ Failed tests
- ❌ Work in progress (use feature branches)

### Commit Messages

**Format**: Follow Conventional Commits or your team's standard

```bash
# Good commit messages
✅ "Add user authentication with OAuth 2.0"
✅ "Fix null pointer exception in payment processing"
✅ "Refactor user repository for better testability"
✅ "Update API docs for /users endpoint"

# Bad commit messages
❌ "fix"
❌ "changes"
❌ "WIP"
❌ "asdf"
❌ "AI generated code"
```

**Template for AI-assisted work**:

```bash
<type>: <brief description>

<what changed and why>

AI-assisted: <prompt or approach used>
Reviewed: <what you verified>
```

**Example**:

```bash
feat: Add OAuth authentication

Implemented OAuth 2.0 support for Google and GitHub login.
Users can now authenticate using social accounts in addition
to email/password.

AI-assisted: Used architecture-aware-feature prompt
Reviewed: Security, error handling, test coverage
Tests: Added integration tests for OAuth flow
```

---

## Branching Strategy

### Branch Types

**Feature branches**: For new features or changes

```bash
# Create feature branch
git checkout -b feature/oauth-auth

# Work on feature (AI-assisted)
# Commit incrementally
# When done, merge to main
```

**Experimental branches**: For AI exploration

```bash
# Try new approach
git checkout -b experiment/alternative-auth

# Let AI explore
# If it works, clean up and merge
# If it fails, delete branch
```

**Bug fix branches**: For fixes

```bash
git checkout -b fix/login-validation
```

### Working with Feature Branches

**Creating a branch**:

```bash
# Always branch from updated main
git checkout main
git pull
git checkout -b feature/new-feature
```

**During development**:

```bash
# Commit frequently (but only working code)
git add <files>
git commit -m "Implement first part of feature"

# Push to remote periodically
git push -u origin feature/new-feature
```

**Before merging**:

```bash
# Update from main
git checkout main
git pull
git checkout feature/new-feature
git rebase main  # or merge main

# Resolve conflicts
# Run all tests
# Review all changes

# Merge to main
git checkout main
git merge feature/new-feature
git push
```

---

## Reviewing AI-Generated Diffs

### Use Visual Diff Tools

```bash
# Better than command-line diff for large changes
git difftool

# Or use your editor's git integration
code .  # VS Code
```

### What to Look For

**Added lines**:
- Is this code necessary?
- Is it correct?
- Is it secure?

**Deleted lines**:
- Why was this removed?
- Is it safe to delete?
- Are there dependencies on this code?

**Modified lines**:
- What changed and why?
- Is the new version better?
- Are there side effects?

### Red Flags in Diffs

🚩 **Large blocks of commented code** - Delete it or uncomment it

🚩 **TODO/FIXME comments** - Address before committing

🚩 **Hardcoded secrets** - Never commit secrets

🚩 **Massive files** - Should this be split?

🚩 **Unrelated changes** - Should be separate commits

🚩 **Generated files** - Should be in .gitignore

---

## Handling AI Experimentation

### Stashing Experiments

```bash
# AI generated something you want to save but not commit
git stash push -m "OAuth alternative approach"

# Work on something else

# Later, restore
git stash list
git stash apply stash@{0}
```

### Branching for Experiments

```bash
# Try AI approach 1
git checkout -b experiment/approach-1
# ... AI generates code ...
# Commit the experiment
git commit -am "Experiment: Using JWT for auth"

# Try AI approach 2
git checkout main
git checkout -b experiment/approach-2
# ... AI generates different code ...
git commit -am "Experiment: Using sessions for auth"

# Compare approaches
git diff experiment/approach-1 experiment/approach-2

# Choose winner
git checkout main
git merge experiment/approach-1  # Keep this approach
git branch -D experiment/approach-2  # Delete failed experiment
```

---

## Commit Frequency

### Commit After Each Working Unit

**Too infrequent** (bad):
```bash
❌ Work for 6 hours
   Generate 50 files with AI
   Commit everything at once
   # Impossible to review, hard to revert
```

**Good frequency**:
```bash
✅ Implement OAuth controller (30 min) → commit
✅ Add OAuth middleware (20 min) → commit
✅ Update user model (15 min) → commit
✅ Add tests (30 min) → commit
```

**Too frequent** (also bad):
```bash
❌ Fix typo → commit
   Add semicolon → commit
   Rename variable → commit
   # Cluttered history
```

### The Test: Can You Revert This Commit?

**Good commit**: Reverting it removes one feature cleanly

**Bad commit**: Reverting it breaks multiple things or only partially removes a feature

---

## Handling Failed AI Attempts

### Option 1: Discard and Start Over

```bash
# AI generated broken code
git status  # See what changed
git restore .  # Discard all changes
# Start fresh with better prompt
```

### Option 2: Stash and Retry

```bash
# Some of this might be useful
git stash push -m "Failed OAuth attempt"
# Try again
# If new attempt works, commit it
# Old stash can be deleted later
git stash drop
```

### Option 3: Cherry-Pick Good Parts

```bash
# AI mixed good and bad code
git add src/auth/oauth.ts  # Good file
git commit -m "Add OAuth controller"

git restore src/middleware/  # Bad files
# Ask AI to regenerate just the middleware
```

---

## .gitignore for AI Projects

**Essential ignores**:

```gitignore
# Dependencies
node_modules/
venv/
.venv/

# Build outputs
dist/
build/
*.pyc
__pycache__/

# Environment files (NEVER commit secrets)
.env
.env.local
.env.*.local

# Editor files
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Test coverage
coverage/
.coverage

# AI-specific
.ai_session_logs/  # If you keep logs
scratch/  # Experimental AI work
```

---

## Commit Message Templates

### For AI-Generated Features

```bash
feat: <feature name>

<description of what it does>

Implementation details:
- <key technical decision 1>
- <key technical decision 2>

AI-assisted: <which prompt used>
Human review:
- [x] Functionality tested
- [x] Security reviewed
- [x] Tests passing
- [x] Architecture aligned
```

### For AI-Assisted Refactoring

```bash
refactor: <what was refactored>

Refactored to <improvement achieved>

Changes:
- <specific change 1>
- <specific change 2>

AI-assisted: Used refactor-for-clarity prompt
Verified: All tests pass, behavior unchanged
```

### For AI-Assisted Bug Fixes

```bash
fix: <brief description of bug>

Fixed <detailed description>

Root cause: <why the bug existed>
Solution: <what was changed>

AI-assisted: Used bug-fixing prompt
Reviewed: <what you verified>
Tests: <new/updated tests>
```

---

## Pre-Commit Hooks

**Automate checks before commits**:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run tests
npm test || exit 1

# Run linter
npm run lint || exit 1

# Check for secrets
if git diff --cached | grep -i "api_key\|secret\|password\s*="; then
    echo "⚠️  Possible secret detected! Review before committing."
    exit 1
fi

echo "✅ Pre-commit checks passed"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Reviewing Your Own Commits

### Before Pushing

```bash
# Review commits before pushing
git log -p origin/main..HEAD

# Check the summary
git log --oneline origin/main..HEAD
```

**Ask yourself**:
- Would I understand these changes in 6 months?
- Is anything missing tests?
- Did I commit something that shouldn't be there?
- Are commit messages clear?

### After Pushing (PR Review)

**Review your own PR first**:
- Read the diff on GitHub/GitLab
- Check for issues you missed locally
- Update PR description
- Add comments on complex parts

---

## Collaboration Workflow

### Working with Others on AI-Assisted Code

**Pull Request Description Template**:

```markdown
## Summary
<What this PR does>

## AI Assistance
- Prompts used: <which prompts>
- Human review: <what you verified>
- Testing: <what was tested>

## Changes
- <file 1>: <what changed>
- <file 2>: <what changed>

## Security Review
- [ ] Input validation present
- [ ] No SQL injection risks
- [ ] No XSS vulnerabilities
- [ ] Auth/authz correct

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manually tested

## Checklist
- [ ] Code reviewed line-by-line
- [ ] Tests passing
- [ ] Linter passing
- [ ] Invariants maintained
- [ ] Architecture aligned
```

---

## Emergency Procedures

### Accidentally Committed Secrets

```bash
# DO NOT just delete in next commit - it's in history!

# Option 1: Rewrite history (if not pushed)
git reset HEAD~1  # Undo commit
# Remove secrets
git add .
git commit -m "..."

# Option 2: If already pushed - rotate the secrets immediately
# Then: git filter-branch or BFG Repo-Cleaner to remove from history
```

**Prevention**: Use pre-commit hooks to detect secrets.

### Accidentally Committed Broken Code

```bash
# If not pushed
git reset HEAD~1  # Undo commit
# Fix the code
git add .
git commit -m "..."

# If already pushed but no one pulled
git push --force  # Use with caution!

# If others have pulled - do NOT rewrite history
# Fix in a new commit instead
```

---

## Best Practices Summary

1. **Test before committing** - All tests must pass
2. **Review before committing** - Read every line
3. **Atomic commits** - One logical change per commit
4. **Meaningful messages** - Future you will thank you
5. **Branch for experiments** - Keep main stable
6. **Never commit secrets** - Use .env files
7. **Use pre-commit hooks** - Automate quality checks
8. **Review your own PRs** - Catch issues before others
9. **Small, frequent commits** - Easier to review and revert
10. **Discard bad attempts** - Don't commit everything AI generates

---

## Remember

**Git is your safety net.**

With AI generating code quickly, version control becomes even more critical:
- You can experiment freely (branches are cheap)
- You can revert mistakes (commits are checkpoints)
- You can track what changed (diffs show AI additions)
- You can review incrementally (small commits are reviewable)

**Use git as a tool to work confidently with AI.**

**When in doubt, commit working code frequently. You can always squash commits later.**
