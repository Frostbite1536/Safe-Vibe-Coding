---
layout: default
title: Setting Up AI Code Review
nav_order: 7
parent: Guides
description: "Step-by-step tutorial for setting up automated code review with Claude Code — from zero-setup terminal reviews to fully automated GitHub Actions pipelines."
---

# Setting Up AI Code Review: A Step-by-Step Tutorial

This tutorial walks you through three levels of AI-assisted code review, from a zero-setup one-liner to a fully automated GitHub Actions pipeline that posts inline comments on your PRs.

Pick the level that matches your needs:

| Level | What you get | Setup time | Cost |
|-------|-------------|-----------|------|
| [Level 1: One-off review](#level-1-one-off-review-in-claude-code) | Review in your terminal | None | Included in Claude Code subscription |
| [Level 2: Slash command](#level-2-reusable-slash-command) | `/review-pr 42` in your terminal | 2 minutes | Included in Claude Code subscription |
| [Level 3: GitHub Actions](#level-3-automated-github-actions-pipeline) | Inline comments on every PR | 10 minutes | Anthropic API usage (~$0.05-0.50 per review) |

---

## Prerequisites

- [Claude Code](BEGINNER_SETUP.md) installed and working
- A GitHub repository with the `gh` CLI authenticated (`gh auth login`)
- For Level 3: An [Anthropic API key](https://console.anthropic.com/)

---

## Level 1: One-Off Review in Claude Code

No setup. Open Claude Code in your repository and type:

```
Review PR #42. Fetch the diff with gh pr diff 42, read each changed
file in full, read CLAUDE.md and REVIEW.md if they exist, and check
for: correctness bugs, security issues, cross-boundary contract
violations, and invariant compliance. Tag findings as Critical, Nit,
or Pre-existing.
```

Replace `42` with your PR number. If you're reviewing local changes instead of a PR:

```
Review my current branch changes against main. Run git diff main...HEAD,
read each changed file in full, and check for correctness bugs, security
issues, and cross-boundary contract violations. Tag findings as Critical,
Nit, or Pre-existing.
```

**What happens**: Claude fetches the diff, reads the full files for context, and reports findings in your terminal with severity tags and file:line locations.

**When to use**: Quick reviews, one-off checks, or trying out the concept before committing to a setup.

---

## Level 2: Reusable Slash Command

Turn the review into a repeatable command you can invoke with `/review-pr 42`.

### Step 1: Create the command directory

```bash
mkdir -p .claude/commands
```

### Step 2: Create the review command

Create `.claude/commands/review-pr.md` with this content:

```markdown
You are performing a structured code review. Find correctness bugs,
security vulnerabilities, broken edge cases, and subtle regressions —
not formatting preferences or style nits (unless they violate explicit
rules in REVIEW.md).

**What to review**: $ARGUMENTS

If a PR number was provided, fetch the diff and changed files.
If no argument was given, review changes on the current branch against main.

## Step 1: Gather Context

1. **The diff**: Use `gh pr diff <number>` for PRs, or `git diff main...HEAD` for local branches
2. **Changed files in full**: Read each changed file completely — not just the diff
3. **CLAUDE.md**: Read for general project rules (if it exists)
4. **REVIEW.md**: Read for review-specific rules (if it exists)
5. **INVARIANTS.md**: Read for system invariants (if it exists)

## Step 2: Multi-Pass Analysis

### Pass 1 — Correctness
- Logic errors, off-by-one, wrong conditionals
- Unhandled edge cases: empty inputs, null, boundary conditions
- Division by zero in aggregations (empty lists, single-element with ddof=1)
- Error handling: silent failures, errors caught but not handled
- Optimization layer bugs (React): useMemo/useCallback with stale closures, React.memo with unstable references, useEffect dependency arrays missing or over-specified

### Pass 2 — Security
- SQL injection, XSS, command injection, path traversal
- Missing auth checks on new endpoints
- Secrets in code, logs, or error messages

### Pass 3 — Cross-Boundary Contracts
- Trace upstream, not downstream: when data looks wrong, find where it was produced before checking consumers
- Data shape mismatches between producer and consumer components
- Fields added to a model but missing from persistence/serialization/tests
- Type leakage: Decimal into JSON, datetime into dicts
- Partial failure leaving state half-modified

### Pass 4 — Invariant & Architecture Compliance
- Check against INVARIANTS.md, CLAUDE.md, REVIEW.md (if they exist)
- Does the change follow existing patterns or introduce a new one?

### Pass 5 — Regression Pattern Search
- For each bug found, search codebase for the same pattern elsewhere
- Check if test fixtures reflect any new fields or changed semantics

## Step 3: Report

Tag each finding:
- **[CRITICAL]**: Bug that should be fixed before merging
- **[NIT]**: Minor issue, worth fixing but not blocking
- **[PRE-EXISTING]**: Bug not introduced by this PR

Format:
**[SEVERITY] File: `path/to/file` | Line: N**
**Issue**: Description.
**Why**: Failure scenario.
**Fix**: Suggested fix.

End with a summary: total findings, key concerns, overall assessment.
If no issues found: "Code review complete. No issues found."
```

### Step 3: Use it

In Claude Code, type:

```
/review-pr 42
```

Or for local changes:

```
/review-pr
```

### Step 4 (optional): Add a REVIEW.md

Create `REVIEW.md` at your repository root to customize what the review checks. This file only applies during reviews — it doesn't affect normal Claude Code sessions.

```markdown
# Code Review Guidelines

## Always check
- New API endpoints have corresponding tests
- Database migrations are backward-compatible
- Error messages don't leak internal details
- New data model fields are reflected in persistence and serialization

## Style
- Prefer early returns over nested conditionals
- Use structured logging, not f-string interpolation in log calls

## Skip
- Generated files under src/gen/
- Formatting-only changes in *.lock files
```

**When to use**: Daily development. This is the sweet spot — zero API cost beyond your Claude Code subscription, full multi-pass review, and it takes 2 minutes to set up.

---

## Level 3: Automated GitHub Actions Pipeline

This posts inline comments directly on your PRs in GitHub — on the exact lines where issues are found. Reviews trigger automatically on every PR, or manually when someone comments `@claude review`.

### What you'll build

```
Developer opens PR
       ↓
GitHub Actions triggers
       ↓
Script fetches PR diff + CLAUDE.md + REVIEW.md
       ↓
Claude analyzes diff, returns JSON findings
       ↓
Script posts inline comments on exact lines
       ↓
Summary comment appears on the PR
```

### Step 1: Get an Anthropic API key

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Create an API key
3. Keep it handy — you'll add it to GitHub in Step 4

### Step 2: Create the review script

Ask Claude Code to create it for you:

```
Create run_review.py in the repository root. This script should:

1. Read environment variables: GITHUB_TOKEN, ANTHROPIC_API_KEY,
   GITHUB_REPOSITORY ("owner/repo"), PR_NUMBER, COMMIT_SHA

2. Fetch the PR diff using GitHub API with Accept: application/vnd.github.v3.diff

3. Read CLAUDE.md and REVIEW.md from the repo root if they exist

4. Send the diff + rules to Claude (claude-sonnet-4-20250514, temperature=0,
   max_tokens=4096) with a system prompt that requires strict JSON array output.
   Each finding: {"file": str, "line": int, "severity": "🔴 Normal" | "🟡 Nit" | "🟣 Pre-existing", "issue": str, "reasoning": str}
   Return [] if no issues.

5. Parse the JSON (strip markdown code fences if present)

6. Post inline comments using POST /repos/{owner}/{repo}/pulls/{pr_number}/comments
   with commit_id, path, line, side="RIGHT". Handle 422 errors gracefully (GitHub
   rejects comments on lines not in the diff).

7. Post a summary comment using POST /repos/{owner}/{repo}/issues/{pr_number}/comments
   with finding counts by severity.

Dependencies: requests, anthropic
```

Or copy the template from this guide's repository: [`docs/templates/run_review.py`](templates/run_review.py)

### Step 3: Create the GitHub Actions workflow

Ask Claude Code:

```
Create .github/workflows/claude_review.yml that:

1. Triggers on pull_request (opened, synchronize) AND issue_comment (created)

2. Job condition: runs on PR events OR when someone comments "@claude review"
   on an open PR (check github.event.issue.pull_request exists and comment
   startsWith '@claude review')

3. Has a "Get PR Context" step that normalizes PR_NUMBER and COMMIT_SHA:
   - For pull_request events: read from github.event.pull_request
   - For issue_comment events: read PR_NUMBER from github.event.issue.number,
     fetch COMMIT_SHA via: gh api repos/${{ github.repository }}/pulls/$PR_NUMBER --jq .head.sha
   Write both to $GITHUB_ENV

4. Checkout, setup Python 3.11, pip install requests anthropic

5. Run python run_review.py with GITHUB_TOKEN and ANTHROPIC_API_KEY env vars

Permissions: pull-requests write, contents read
```

Or copy the template: [`docs/templates/claude_review.yml`](templates/claude_review.yml)

### Step 4: Add your API key to GitHub

1. Go to your repository on GitHub
2. Click **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: paste your Anthropic API key
6. Click **Add secret**

`GITHUB_TOKEN` is automatically provided by GitHub Actions — you don't need to add it.

### Step 5: Commit and push

```bash
git add run_review.py .github/workflows/claude_review.yml
git commit -m "Add automated code review pipeline"
git push
```

### Step 6: Test it

Open a PR (or push to an existing one). Within a few minutes:
- A check run named **Claude Code Review** appears
- Inline comments appear on the exact lines where issues are found
- A summary comment shows finding counts

To trigger manually, comment on any open PR:

```
@claude review
```

### Troubleshooting

**No check run appears:**
- Verify `ANTHROPIC_API_KEY` is set in repository secrets
- Check the Actions tab for workflow run errors
- Ensure the workflow file is on the default branch (or the PR branch)

**Comments fail to post (422 errors):**
- This is expected for some findings — GitHub only allows inline comments on lines that appear in the diff. The script logs these and continues.

**Review is too expensive:**
- Change the model in `run_review.py` from `claude-sonnet-4-20250514` to `claude-haiku-4-5-20251001` for cheaper reviews
- Switch the trigger to manual-only: remove `pull_request` from the `on:` section and only use `issue_comment`

**Review misses things / too many false positives:**
- Add more specific rules to your `REVIEW.md`
- Add project context to your `CLAUDE.md`

### Security considerations

**For public repositories**: Anyone who can comment on your repo can trigger a review and spend your API credits. Add a user allowlist to the workflow:

```yaml
# In the job's 'if' condition, add:
&& contains(fromJson('["your_username", "trusted_collaborator"]'), github.event.comment.user.login)
```

**For private repositories**: Only collaborators can comment, so this is less of a concern.

### Cost expectations

Reviews use the Anthropic API and are billed per token:
- Small PR (< 100 lines changed): ~$0.05
- Medium PR (100-500 lines): ~$0.10-0.30
- Large PR (500+ lines): ~$0.30-0.50

These are rough estimates. Actual cost depends on the diff size, number of changed files, and the size of your CLAUDE.md/REVIEW.md files.

---

## Quick Reference: All Three Levels

### Level 1 — One-off (zero setup)
```
Review PR #42. Fetch the diff with gh pr diff 42, read each changed
file in full, and check for correctness bugs and security issues.
Tag findings as Critical, Nit, or Pre-existing.
```

### Level 2 — Slash command (2 min setup)
```bash
# One-time setup
mkdir -p .claude/commands
# Create .claude/commands/review-pr.md (see above)

# Daily use
/review-pr 42
```

### Level 3 — GitHub Actions (10 min setup)
```bash
# One-time setup (ask Claude Code to create these)
# 1. run_review.py in repo root
# 2. .github/workflows/claude_review.yml
# 3. Add ANTHROPIC_API_KEY to repo secrets

# Then it's automatic — or trigger manually:
# Comment "@claude review" on any PR
```

---

## What's Next

- **Customize your reviews**: Create a [`REVIEW.md`](CODE_REVIEW_AI.md#use-a-reviewmd-file-for-review-specific-rules) with project-specific rules
- **Understand severity levels**: Read about the [severity classification system](CODE_REVIEW_AI.md#classify-findings-by-severity)
- **Learn what to look for**: Study the [Cross-Boundary Review checklist](CODE_REVIEW_AI.md#cross-boundary-review-where-ai-code-actually-breaks) — the highest-value review pass
- **Review AI code effectively**: Read the full [Code Review for AI guide](CODE_REVIEW_AI.md)
