---
layout: default
title: Quick Reference Checklist
nav_order: 2
description: "Print-friendly checklist for safe AI-assisted development."
---

# Vibe Coding Checklist: Production-Safe AI Development

Use this as a lightweight guardrail when building with LLMs. Print it, pin it, reference it before each session.

---

## Product & Scope

- [ ] Clearly describe the product, users, and problem
- [ ] Specify the type of system (web app, API, CLI, service, etc.)
- [ ] State non-goals and out-of-scope features

## Role & Prompt Alignment

- [ ] Assign the LLM a precise expert role
- [ ] Explicitly optimize for boring, conventional code
- [ ] Ask the LLM to refine the prompt before coding

## Planning Artifacts

- [ ] Roadmap with phased implementation ([template](./docs/templates/ROADMAP.md))
- [ ] Architecture document - components, data flow ([template](./docs/templates/ARCHITECTURE.md))
- [ ] README explaining purpose and structure ([template](./docs/templates/PROJECT_README.md))
- [ ] System Invariants & Contracts document ([template](./docs/templates/INVARIANTS.md))

## System Invariants & Contracts

- [ ] Define non-negotiable rules
- [ ] Confirm invariants before behavior changes
- [ ] Treat invariant violations as bugs or product decisions

## Secrets & API Key Security

- [ ] No API keys or secrets in frontend code ([guide](./docs/API_KEY_SECURITY.md))
- [ ] External APIs called through server-side proxy routes
- [ ] No secrets in `NEXT_PUBLIC_`, `VITE_`, or `REACT_APP_` env vars
- [ ] `.env` files in `.gitignore`
- [ ] Network tab checked for exposed credentials
- [ ] Proxy routes require authentication
- [ ] No "warn-only" security defaults (insecure configs must fail-fast outside dev)
- [ ] Auth endpoints have rate limiting

## Implementation Discipline

- [ ] Write tests alongside features
- [ ] Add static checks (lint, format, type)
- [ ] Run tests before accepting new code
- [ ] Prefer clarity over cleverness
- [ ] Keep files modular and focused (< ~1,500 lines)

## Cross-Boundary Integrity

- [ ] Adding a field? Grep for every site that creates, stores, restores, or serializes the data model
- [ ] Data round-trips (save/restore, serialize/deserialize) preserve all fields and types
- [ ] Multi-step operations build new state in temp variables, swap atomically on success
- [ ] No type leakage across boundaries (Decimal into JSON, datetime into dicts)
- [ ] Multi-source data has compatible units/semantics before aggregation
- [ ] After fixing a bug, search entire codebase for the same pattern class

## Auditing at Scale (Large Codebases)

- [ ] SAST scanner running in CI/CD on every PR (Snyk, Semgrep, CodeQL, or similar)
- [ ] Code quality gate in CI (SonarQube/SonarCloud or similar)
- [ ] Dependency vulnerability scanning enabled
- [ ] Security findings triaged for reachability (real vs. false positive)
- [ ] Repository-wide architecture review run before major releases
- [ ] External tool findings fed back to agents as focused investigation tasks
- [ ] Full guide: [Auditing at Scale](./docs/EXTERNAL_AUDIT_TOOLS.md)

## Validation & Stability

- [ ] Run bug hunts frequently ([prompt](./prompts/bug-hunt.md))
- [ ] Check for regressions against invariants
- [ ] Update docs when behavior changes
- [ ] Generate checkpoint summaries after major changes

## Prompt Hygiene

- [ ] Keep reusable prompts in `/prompts` ([examples](./prompts))
- [ ] Use role-specific prompts for consistency
- [ ] Avoid "creative" prompts unless explicitly needed

---

## Quick Prompt Reference

| Prompt | Use Case | Link |
|--------|----------|------|
| Engineering | Default production coding mode | [prompts/engineering-prompt.md](./prompts/engineering-prompt.md) |
| Architecture-Aware Feature | Adding features safely | [prompts/architecture-aware-feature.md](./prompts/architecture-aware-feature.md) |
| Bug Hunt | General bug detection | [prompts/bug-hunt.md](./prompts/bug-hunt.md) |
| Backend Bug Hunt | Backend-specific issues | [prompts/backend-bug-hunt.md](./prompts/backend-bug-hunt.md) |
| Frontend Bug Hunt | Frontend-specific issues | [prompts/frontend-bug-hunt.md](./prompts/frontend-bug-hunt.md) |
| Bug Fixing | Surgical fixes only | [prompts/bug-fixing.md](./prompts/bug-fixing.md) |
| Modularity Review | File size and structure | [prompts/modularity-review.md](./prompts/modularity-review.md) |
| Refactor for Clarity | Improve readability | [prompts/refactor-for-clarity.md](./prompts/refactor-for-clarity.md) |
| Invariant Check | Verify against contracts | [prompts/invariant-check.md](./prompts/invariant-check.md) |
| User Feedback Simulation | Usability testing | [prompts/user-feedback-simulation.md](./prompts/user-feedback-simulation.md) |
| Performance Review | Optimization | [prompts/performance-review.md](./prompts/performance-review.md) |
| Code Review | Multi-pass PR review | [prompts/code-review.md](./prompts/code-review.md) |
| Setup Review Pipeline | Automated PR reviews | [prompts/setup-code-review-pipeline.md](./prompts/setup-code-review-pipeline.md) |
| Smart Contract Audit | Solidity security audit | [prompts/smart-contract-audit.md](./prompts/smart-contract-audit.md) |

---

## Code Review Setup

- [ ] Create `REVIEW.md` at repo root with review-specific rules ([guide](./docs/CODE_REVIEW_AI.md))
- [ ] Use consistent severity levels: Critical (block merge), Nit (fix if easy), Pre-existing (file separately)
- [ ] Review changed files in full, not just the diff
- [ ] Run the [code review prompt](./prompts/code-review.md) on PRs (copy to `.claude/commands/review-pr.md` for slash command access)
- [ ] For automated reviews: set up the [GitHub Actions pipeline](./docs/templates/claude_review.yml) with inline comments

---

## MCP Server Development

- [ ] Tool descriptions list every parameter with type, purpose, and valid values
- [ ] Return type semantics documented (creates, returns ref, returns data, side effect)
- [ ] Parameter names in schema match what descriptions lead the LLM to expect
- [ ] Every handler wrapped in a safe error boundary (decorator/try-catch)
- [ ] Error responses include valid options and expected format (never "see the docs")
- [ ] No `print()`/`console.log()` writing to stdout (corrupts stdio transport)
- [ ] Every attribute access verified against actual type definitions
- [ ] Every function call uses correct parameter names from real signatures
- [ ] All response types are JSON-serializable (handle datetime, tuples, custom types)
- [ ] Inputs validated at the boundary: enums, non-finite numbers, required refs, types
- [ ] LLM-specific input test suite exists (lowercase enums, NaN, extra whitespace)
- [ ] Full checklist: [Building MCP Servers guide](./docs/MCP_DEVELOPMENT.md#mcp-server-checklist)

---

## Multi-Agent Git Safety

- [ ] Each agent's work committed from its own tab before switching tasks
- [ ] `git status` run before every commit to find ALL untracked/modified files (not just the agent's own)
- [ ] Parallel agents use separate branches or git worktrees, not tabs-on-main
- [ ] No `git pull` or `git checkout` with uncommitted work from other agents — stash first
- [ ] `git status` run after every push to verify nothing was left behind
- [ ] CLAUDE.md includes multi-agent git safety rules ([guide](./docs/VERSION_CONTROL.md#multi-agent-git-safety))

---

## Smart Contracts (Solidity)

- [ ] Every `whenNotPaused` function justified — defensive actions (challenge, renew, withdraw) exempt from pause
- [ ] No deadline/window that ticks during pause without user recourse
- [ ] No `safeTransfer` to non-`msg.sender` in functions other users depend on (use pull-over-push)
- [ ] Every admin setter has min/max validation; zero-value behavior analyzed
- [ ] Config affecting already-committed funds is snapshotted at commitment time
- [ ] Sentinel values for "unset" (`0`) don't collide with valid values
- [ ] Maximum single-block damage documented for every privileged role
- [ ] Destructive privileged actions rate-limited; no-ops don't consume cooldown
- [ ] Every array has bounded growth or a deletion strategy
- [ ] Terminal states distinguishable from active states (use enum, not timestamps)
- [ ] Upgradeable: new struct fields at END only, storage gap adjusted
- [ ] Upgradeable: migration plan for existing data when structures change
- [ ] Cross-contract: same vulnerability pattern checked across all sibling contracts
- [ ] Two-pass audit completed: external audit → self-audit of fixes
- [ ] Full checklist: [Smart Contract Auditing guide](./docs/SMART_CONTRACT_AUDIT.md#smart-contract-audit-checklist)

---

## Claude Code Session Management

- [ ] `/compact` used proactively when sessions exceed 30+ exchanges
- [ ] `/cost` checked periodically to monitor token usage
- [ ] `/memory` reviewed to verify persistent memories are accurate
- [ ] CLAUDE.md kept focused — it's included in every turn's context budget
- [ ] Subagents used for deep exploration to protect main context window
- [ ] Worktree isolation used for risky or parallel agent operations
- [ ] Stop hooks configured for automated verification on task completion
- [ ] PostToolUse hooks configured for auto-formatting on Write/Edit
- [ ] Permission allow-lists configured for safe commands (test, lint, build)
- [ ] Full guide: [Claude Code Architecture Deep Dive](./docs/CLAUDE_CODE_ADVANCED.md)

---

## After Each Major Change

Generate a checkpoint summary:
- [ ] 5-bullet summary of what changed
- [ ] Any new assumptions introduced
- [ ] Any risks added

This creates a rolling audit trail and reduces long-term confusion.

---

**Remember**: The goal is velocity without chaos. These checks aren't bureaucracy—they're the guardrails that let you move fast safely.
