---
layout: default
title: Setup Code Review Pipeline
parent: Prompts Library
nav_order: 14
---

# Setup Code Review Pipeline

Give this prompt to an LLM (Claude Code, Cursor, etc.) to set up a fully automated PR review pipeline in your repository. The pipeline posts inline comments on exact lines where issues are found, supports automatic and manual triggers, and reads your CLAUDE.md and REVIEW.md for custom rules.

---

## Prompt

Set up an automated code review pipeline in this repository that reviews pull requests and posts inline comments on the exact lines where issues are found. Follow these steps exactly:

### Step 1: Create the review script

Create `run_review.py` in the repository root. This Python script:
- Fetches the PR diff via GitHub API
- Reads `CLAUDE.md` and `REVIEW.md` from the repo root for custom rules
- Sends the diff to Claude with a structured review prompt
- Parses the response as a JSON array of findings
- Posts inline comments on the exact changed lines via GitHub's Pull Request Review Comments API
- Posts a top-level summary comment with finding counts by severity

The system prompt for the reviewer must instruct Claude to:
- Output findings as a strict JSON array (no markdown wrapping, no preamble)
- Each finding has: `file` (string), `line` (integer — must be a line in the diff), `severity` (one of "🔴 Normal", "🟡 Nit", "🟣 Pre-existing"), `issue` (string), `reasoning` (string)
- Return `[]` if no issues found
- Focus on correctness bugs, security vulnerabilities, cross-boundary contract violations, and regressions — not formatting
- Respect REVIEW.md rules (review-specific) and CLAUDE.md rules (violations are nit-level)

Required environment variables (all set automatically by GitHub Actions):
- `GITHUB_TOKEN` — automatic
- `ANTHROPIC_API_KEY` — from repo secrets
- `GITHUB_REPOSITORY` — "owner/repo", automatic
- `PR_NUMBER` — from workflow
- `COMMIT_SHA` — from workflow

Dependencies: `requests`, `anthropic`

Use `claude-sonnet-4-20250514` as the model. Set `temperature=0.0` and `max_tokens=4096`.

Handle the JSON parsing defensively: strip markdown code fences if Claude wraps the output. If parsing fails, print the raw output and exit non-zero.

Post inline comments using `POST /repos/{owner}/{repo}/pulls/{pr_number}/comments` with `commit_id`, `path`, `line`, `side: "RIGHT"`. GitHub rejects comments on lines not in the diff — catch 422 errors gracefully and log them instead of crashing.

Post a summary comment using `POST /repos/{owner}/{repo}/issues/{pr_number}/comments` with counts of findings by severity.

### Step 2: Create the GitHub Actions workflow

Create `.github/workflows/claude_review.yml`. The workflow must:

**Trigger on:**
- `pull_request` events: `opened`, `synchronize`
- `issue_comment` events: `created` (for manual `@claude review` trigger)

**Job condition:**
```yaml
if: >
  github.event_name == 'pull_request' ||
  (github.event_name == 'issue_comment' &&
   github.event.issue.pull_request &&
   startsWith(github.event.comment.body, '@claude review'))
```

**Permissions:** `pull-requests: write`, `contents: read`

**Event normalization step (critical):**
The `pull_request` event provides `PR_NUMBER` and `COMMIT_SHA` directly. The `issue_comment` event does NOT — it only has the issue number. Add a step that:
- For `pull_request`: reads from `github.event.pull_request.number` and `github.event.pull_request.head.sha`
- For `issue_comment`: reads `PR_NUMBER` from `github.event.issue.number` and fetches `COMMIT_SHA` via `gh api repos/${{ github.repository }}/pulls/$PR_NUMBER --jq .head.sha`
- Writes both to `$GITHUB_ENV` so `run_review.py` reads them as environment variables

**Steps:** checkout, setup Python 3.11, pip install requests anthropic, run `python run_review.py`

**Pass these env vars to the run step:**
- `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`
- `ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}`

Add a comment in the YAML noting that for public repos, users should add a user allowlist to the `if` condition to prevent unauthorized API spend.

### Step 3: Create REVIEW.md (if it doesn't exist)

If there is no `REVIEW.md` in the repository root, create one with this structure:

```markdown
# Code Review Guidelines

## Always check
- New API endpoints have corresponding tests
- Database migrations are backward-compatible
- Error messages don't leak internal details to users
- New fields added to data models are reflected in persistence and serialization

## Style
- Prefer early returns over nested conditionals
- Use structured logging, not f-string interpolation in log calls

## Skip
- Generated files under src/gen/
- Formatting-only changes in *.lock files
```

Ask the user what project-specific rules to add before creating the file.

### Step 4: Set up the Claude Code slash command

Create `.claude/commands/review-pr.md` with a prompt that performs the same multi-pass review interactively in Claude Code:
1. Gather context: fetch the diff with `gh pr diff`, read changed files in full, read CLAUDE.md/REVIEW.md/INVARIANTS.md
2. Run 5 passes: correctness, security, cross-boundary contracts, invariant compliance, regression patterns
3. Report findings with severity tags (Critical/Nit/Pre-existing) and file:line locations

Use `$ARGUMENTS` to accept a PR number as input, with fallback to reviewing current branch changes against main.

### Step 5: Verify and report

After creating all files:
1. Run `python -c "import requests; import anthropic; print('Dependencies available')"` to check if dependencies are importable (informational only — they'll be installed by GitHub Actions)
2. List all created files
3. Tell the user: "The pipeline is ready. You need to do ONE manual step: add your `ANTHROPIC_API_KEY` to your repository secrets at Settings > Secrets and variables > Actions > New repository secret. After that, open a PR and the review will run automatically. You can also comment `@claude review` on any open PR to trigger a review manually."

---

## What you get

After setup, your repository will have:

| File | Purpose |
|------|---------|
| `run_review.py` | Review script — fetches diff, calls Claude, posts inline comments |
| `.github/workflows/claude_review.yml` | Triggers reviews on PR open/push and `@claude review` comments |
| `REVIEW.md` | Review-specific rules (what to flag, what to skip) |
| `.claude/commands/review-pr.md` | Interactive review via `/review-pr 42` in Claude Code |

**Trigger modes:**
- **Automatic**: Every PR open and push
- **Manual**: Comment `@claude review` on any open PR

**Severity system:**
- 🔴 **Normal**: Bug that should be fixed before merging
- 🟡 **Nit**: Minor issue, worth fixing but not blocking
- 🟣 **Pre-existing**: Bug not introduced by this PR

**One manual step required**: Add `ANTHROPIC_API_KEY` to repository secrets.
