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

## Implementation Discipline

- [ ] Write tests alongside features
- [ ] Add static checks (lint, format, type)
- [ ] Run tests before accepting new code
- [ ] Prefer clarity over cleverness
- [ ] Keep files modular and focused (< ~1,500 lines)

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

---

## After Each Major Change

Generate a checkpoint summary:
- [ ] 5-bullet summary of what changed
- [ ] Any new assumptions introduced
- [ ] Any risks added

This creates a rolling audit trail and reduces long-term confusion.

---

**Remember**: The goal is velocity without chaos. These checks aren't bureaucracy—they're the guardrails that let you move fast safely.
