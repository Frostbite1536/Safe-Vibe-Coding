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

---

## Code Review Setup

- [ ] Create `REVIEW.md` at repo root with review-specific rules ([guide](./docs/CODE_REVIEW_AI.md))
- [ ] Use consistent severity levels: Critical (block merge), Nit (fix if easy), Pre-existing (file separately)
- [ ] Review changed files in full, not just the diff
- [ ] Run the [code review prompt](./prompts/code-review.md) on PRs (copy to `.claude/commands/review-pr.md` for slash command access)

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

## After Each Major Change

Generate a checkpoint summary:
- [ ] 5-bullet summary of what changed
- [ ] Any new assumptions introduced
- [ ] Any risks added

This creates a rolling audit trail and reduces long-term confusion.

---

**Remember**: The goal is velocity without chaos. These checks aren't bureaucracy—they're the guardrails that let you move fast safely.
