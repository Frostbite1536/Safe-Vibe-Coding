"""
DIY Claude Code Review — GitHub Actions Pipeline

Posts inline review comments on pull requests using the Anthropic API.
Reads CLAUDE.md and REVIEW.md from the repository root for custom rules.

Setup:
  1. Copy this file to the root of your repository
  2. Copy the workflow template to .github/workflows/claude_review.yml
  3. Add ANTHROPIC_API_KEY to your repository secrets
  4. Open a PR and watch the review appear

Environment variables (set by GitHub Actions):
  GITHUB_TOKEN       — Automatically provided by GitHub Actions
  ANTHROPIC_API_KEY  — Your Anthropic API key (add to repo secrets)
  GITHUB_REPOSITORY  — "owner/repo" (automatic)
  PR_NUMBER          — PR number (from workflow)
  COMMIT_SHA         — Latest commit SHA (from workflow)
"""

import json
import os
import sys

import requests
from anthropic import Anthropic

SYSTEM_PROMPT = """You are an expert Code Review System. Analyze code diffs for logic errors,
security vulnerabilities, broken edge cases, cross-boundary contract violations, and subtle
regressions. You prioritize correctness over formatting preferences.

Context & Rules:
* Adhere to the custom rules provided in REVIEW.md and CLAUDE.md (if provided).
* Treat newly introduced violations of CLAUDE.md as nit-level findings.
* Ignore formatting issues unless they directly violate a rule in REVIEW.md.
* Pay special attention to cross-boundary bugs: data shape mismatches between components,
  type leakage (Decimal into JSON, datetime into dicts), partial failure state corruption,
  and round-trip integrity (save/restore, serialize/deserialize losing fields).

Output Format:
You MUST output your findings as a strict JSON array of objects. Do not include any
conversational text, markdown formatting, or preamble outside the JSON array.
If no issues are found, return an empty array: []

Each object in the array must have these keys:
- "file": The file path as shown in the diff (string)
- "line": The exact line number in the NEW code where the issue occurs (integer).
  IMPORTANT: This must be a line that appears in the diff, or the comment will fail to post.
- "severity": Exactly one of: "🔴 Normal", "🟡 Nit", "🟣 Pre-existing"
- "issue": A brief description of the problem (string)
- "reasoning": Detailed explanation of why this was flagged and how to fix it (string)
"""


def get_pr_diff(owner: str, repo: str, pr_number: str, token: str) -> str | None:
    """Fetch the raw diff of a GitHub Pull Request."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",
    }
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 200:
        return response.text
    print(f"Error fetching PR diff: {response.status_code} - {response.text}")
    return None


def read_local_file(filepath: str) -> str | None:
    """Read a local file if it exists."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return None


def format_payload(
    diff: str, claude_md: str | None, review_md: str | None
) -> str:
    """Combine the diff and rule files into a single prompt."""
    payload = f"Here is the code diff to review:\n\n```diff\n{diff}\n```\n\n"
    if review_md or claude_md:
        payload += "---\n### Custom Repository Rules\n"
        if review_md:
            payload += (
                f"**REVIEW.md:**\n```markdown\n{review_md}\n```\n\n"
            )
        if claude_md:
            payload += (
                f"**CLAUDE.md:**\n```markdown\n{claude_md}\n```\n"
            )
    return payload


def run_review(payload: str, api_key: str) -> str:
    """Send the payload to the Anthropic API and return the response."""
    client = Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        temperature=0.0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": payload}],
    )
    return message.content[0].text


def post_inline_comment(
    owner: str,
    repo: str,
    pr_number: str,
    commit_sha: str,
    token: str,
    finding: dict,
) -> None:
    """Post a single inline comment on a specific file and line in the PR."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    severity = finding.get("severity", "")
    issue = finding.get("issue", "")
    reasoning = finding.get("reasoning", "")

    body = (
        f"**{severity}** {issue}\n\n"
        f"<details><summary>Extended Reasoning</summary>\n\n"
        f"{reasoning}\n</details>"
    )

    data = {
        "body": body,
        "commit_id": commit_sha,
        "path": finding.get("file"),
        "line": int(finding.get("line", 0)),
        "side": "RIGHT",
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    file_line = f"{finding.get('file')}:{finding.get('line')}"
    if response.status_code == 201:
        print(f"  Posted comment on {file_line}")
    else:
        # GitHub rejects comments on lines not in the diff — this is expected
        print(f"  Failed to post on {file_line}: {response.status_code}")


def post_summary_comment(
    owner: str, repo: str, pr_number: str, token: str, findings: list
) -> None:
    """Post a top-level summary comment on the PR."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    if not findings:
        body = "## Claude Code Review\n\nCode review complete. No issues found."
    else:
        normal = sum(1 for f in findings if "Normal" in f.get("severity", ""))
        nit = sum(1 for f in findings if "Nit" in f.get("severity", ""))
        preexisting = sum(
            1 for f in findings if "Pre-existing" in f.get("severity", "")
        )
        body = (
            f"## Claude Code Review\n\n"
            f"**{len(findings)} findings**: "
            f"{normal} critical, {nit} nits, {preexisting} pre-existing\n\n"
            f"See inline comments for details."
        )

    requests.post(url, headers=headers, json={"body": body}, timeout=30)


def main() -> None:
    github_token = os.getenv("GITHUB_TOKEN")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    github_repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    commit_sha = os.getenv("COMMIT_SHA")

    required = {
        "GITHUB_TOKEN": github_token,
        "ANTHROPIC_API_KEY": anthropic_key,
        "GITHUB_REPOSITORY": github_repo,
        "PR_NUMBER": pr_number,
        "COMMIT_SHA": commit_sha,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    owner, repo = github_repo.split("/")

    # 1. Fetch the PR diff
    print(f"Fetching diff for PR #{pr_number}...")
    pr_diff = get_pr_diff(owner, repo, pr_number, github_token)
    if not pr_diff:
        print("Could not fetch PR diff. Exiting.")
        sys.exit(1)

    # 2. Read rule files from the repository
    claude_rules = read_local_file("CLAUDE.md")
    review_rules = read_local_file("REVIEW.md")

    # 3. Run the review
    print("Sending to Claude for review...")
    payload = format_payload(pr_diff, claude_rules, review_rules)
    raw_output = run_review(payload, anthropic_key)

    # 4. Parse and post findings
    clean_json = raw_output.replace("```json", "").replace("```", "").strip()
    try:
        findings = json.loads(clean_json)
    except json.JSONDecodeError:
        print("Failed to parse Claude output as JSON. Raw output:")
        print(raw_output)
        sys.exit(1)

    if not findings:
        print("Code review complete. No issues found.")
    else:
        print(f"Found {len(findings)} issues. Posting inline comments...")
        for finding in findings:
            post_inline_comment(
                owner, repo, pr_number, commit_sha, github_token, finding
            )

    # 5. Post a summary comment
    post_summary_comment(owner, repo, pr_number, github_token, findings)
    print("Review complete.")


if __name__ == "__main__":
    main()
