---
layout: default
title: Incorporate into Your Repo
nav_order: 5
description: "Agent-facing checklist for auditing a repository and incorporating Safe Vibe Coding practices."
---

# Incorporate Safe Vibe Coding into Your Repo

A step-by-step checklist for an LLM coding agent to audit any repository — new or existing — and incorporate the essential Safe Vibe Coding artifacts. Hand this document to your agent alongside your repo and let it work through each section.

---

## How to Use This Document

**If you are the developer**: Copy the prompt below into a conversation with your LLM coding agent (Claude Code, Cursor, etc.), or tell your agent to read this file directly.

**If you are the LLM agent**: Work through this document top-to-bottom. For each section, audit whether the target repo already has the artifact. If it does, check it against the quality bar described here. If it doesn't, create it using the linked template and the repo's existing code as source material.

---

## The Prompt

Give this to your LLM agent along with access to both repos:

```markdown
## Task: Incorporate Safe Vibe Coding Practices

You have access to two repositories:
1. **Safe-Vibe-Coding** (reference) — https://github.com/Frostbite1536/Safe-Vibe-Coding
2. **[TARGET REPO]** (the project to improve)

Work through the incorporation checklist below. For each item:
1. Check if the target repo already has it
2. If yes — audit it against the quality bar and suggest improvements
3. If no — create it using the template and the target repo's actual code/context
4. Report what you created, what you improved, and what was already good

Prioritize Tier 1 items. Only move to Tier 2 and 3 if Tier 1 is complete
or the developer asks for them.
```

---

## Phase 0: Orientation

Before creating anything, understand the target repo.

- [ ] **Read the existing README** (or note its absence)
- [ ] **Identify the tech stack** — languages, frameworks, databases, infrastructure
- [ ] **Map the directory structure** — where does source code live? tests? config?
- [ ] **Check for existing docs** — is there an `ARCHITECTURE.md`, `INVARIANTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, or similar?
- [ ] **Check for existing CI/CD** — `.github/workflows/`, `Makefile`, `justfile`, etc.
- [ ] **Identify the project type** — web app, API, CLI, library, service, smart contract, monorepo
- [ ] **Note the project maturity** — greenfield, MVP, established, legacy

Record your findings. Everything you create below should be grounded in what actually exists, not generic boilerplate.

---

## Tier 1: Non-Negotiable Foundations

These are the artifacts every repo needs. Without them, LLM-assisted development is flying blind.

### 1.1 CLAUDE.md (or equivalent agent instructions)

**What**: A file at the repo root that teaches the LLM agent about the project — conventions, architecture summary, commands to run, things to avoid.

**Why**: This is included in every turn of a Claude Code conversation. It's the single highest-leverage file for AI-assisted development.

**Where to put it**: `CLAUDE.md` at repo root (Claude Code reads this automatically). For other tools, use their equivalent (`.cursorrules`, `.github/copilot-instructions.md`, etc.)

**Quality bar**:
- [ ] States the project's purpose in 1-2 sentences
- [ ] Lists the tech stack and key dependencies
- [ ] Describes the directory structure
- [ ] Documents how to build, test, and lint (`npm test`, `pytest`, etc.)
- [ ] Lists coding conventions (naming, file size limits, import style)
- [ ] References INVARIANTS.md and ARCHITECTURE.md if they exist
- [ ] Includes "never do" rules (e.g., "never commit .env files", "never use `any` type")
- [ ] Kept concise — it's loaded on every turn, so avoid bloat
- [ ] Includes multi-agent git safety rules if parallel agents are used

**Reference**: [Beginner Setup Guide — CLAUDE.md section](./docs/BEGINNER_SETUP)

---

### 1.2 System Invariants

**What**: A document defining the non-negotiable truths of the system — rules that must always hold regardless of code path.

**Why**: Invariants are the single best defense against LLM-generated bugs. They give every future session (and every reviewer) an objective correctness standard.

**Where to put it**: `docs/INVARIANTS.md` or `INVARIANTS.md` at repo root

**How to derive from an existing codebase**:
1. Look at database schema constraints (NOT NULL, UNIQUE, FOREIGN KEY, CHECK)
2. Read validation logic in API handlers and form submissions
3. Check auth middleware — what must always be true about access control?
4. Look at tests — what are they actually asserting? Those are implicit invariants
5. Search for comments like "must always", "never", "invariant", "assert"
6. Ask: "If this rule broke silently, what would the consequences be?"

**Quality bar**:
- [ ] Uses the `INV-[CATEGORY]-###` naming convention
- [ ] Each invariant has: Rule, Rationale, Examples (valid/invalid), Enforcement
- [ ] Covers at minimum: data integrity, security boundaries, authorization
- [ ] Cross-component contract invariants are documented (where data crosses boundaries)
- [ ] Includes an invariant change log (changes require explicit justification)

**Template**: [docs/templates/INVARIANTS.md](./docs/templates/INVARIANTS.md)

---

### 1.3 Architecture Document

**What**: A document describing the system's components, their responsibilities, data flow, and key design decisions.

**Why**: LLMs lose architectural context across sessions. This document is the anchor that prevents architectural drift.

**Where to put it**: `docs/ARCHITECTURE.md` or `ARCHITECTURE.md` at repo root

**How to derive from an existing codebase**:
1. Map the top-level directories to components
2. Trace a request from entry point (HTTP handler, CLI command, event listener) through the layers
3. Identify the data models and where they're defined
4. List external dependencies (databases, APIs, message queues) and their failure modes
5. Document key design decisions that aren't obvious from the code ("we use eventual consistency because...")

**Quality bar**:
- [ ] Has a high-level diagram (ASCII art or Mermaid)
- [ ] Each component has: responsibility, dependencies, interfaces, data flow
- [ ] Data models documented with constraints
- [ ] External dependencies listed with failure modes
- [ ] Key design decisions recorded with rationale
- [ ] Security and performance considerations noted

**Template**: [docs/templates/ARCHITECTURE.md](./docs/templates/ARCHITECTURE.md)

---

### 1.4 README

**What**: The project's front door — what it is, how to run it, how it's organized.

**Why**: Every LLM session starts by reading the README. A bad or missing README means every session starts confused.

**Where to put it**: `README.md` at repo root

**Quality bar**:
- [ ] One-paragraph description of what the project does and who it's for
- [ ] Quick start instructions (clone, install, run)
- [ ] Project structure overview
- [ ] How to run tests
- [ ] Links to ARCHITECTURE.md, INVARIANTS.md, ROADMAP.md

**Template**: [docs/templates/PROJECT_README.md](./docs/templates/PROJECT_README.md)

---

### 1.5 Tests That Actually Run

**What**: A test suite that passes and that the LLM agent can execute.

**Why**: Tests are the verification loop. Without them, the LLM has no way to check its own work. This is the single most important quality multiplier.

**Quality bar**:
- [ ] Test command is documented in README and CLAUDE.md
- [ ] Tests pass on a clean checkout
- [ ] At least one test exists per core module/component
- [ ] Test directory structure mirrors source directory structure
- [ ] CI runs tests on every push/PR (if CI exists)

**Reference**: [Automation & Testing Guide](./docs/AUTOMATION_TESTING)

---

## Tier 2: Strongly Recommended

These artifacts significantly improve the quality and safety of LLM-assisted development. Incorporate them once Tier 1 is solid.

### 2.1 Roadmap

**What**: A phased implementation plan with explicit goals, deliverables, and exclusions per phase.

**Why**: Phases prevent scope creep — the most common failure mode in LLM-assisted development. Explicit exclusions ("Phase 1 does NOT include...") are more important than inclusions.

**Where to put it**: `docs/ROADMAP.md`

**Quality bar**:
- [ ] 3-4 phases with clear goals
- [ ] Each phase lists features included AND explicitly excluded
- [ ] Success criteria for each phase
- [ ] Dependencies between phases identified

**Template**: [docs/templates/ROADMAP.md](./docs/templates/ROADMAP.md)

---

### 2.2 Prompt Library

**What**: A directory of reusable, role-specific prompts for common tasks (engineering, bug hunting, code review, etc.).

**Why**: Consistent prompts produce consistent results. A prompt library means you don't reinvent the wheel every session.

**Where to put it**: `prompts/` directory with a `README.md` index

**What to include**:
- [ ] An engineering prompt customized for this project's stack and conventions
- [ ] A bug hunt prompt that references the project's invariants and architecture
- [ ] A code review prompt with project-specific severity levels

**Reference prompts to adapt**:
- [Engineering Prompt](./prompts/engineering-prompt.md)
- [Bug Hunt](./prompts/bug-hunt.md)
- [Code Review](./prompts/code-review.md)
- [Invariant Check](./prompts/invariant-check.md)
- [Full Prompt Library](./prompts/)

---

### 2.3 Code Review Configuration

**What**: A `REVIEW.md` at repo root with review-specific rules, plus optionally an automated review pipeline.

**Why**: AI-generated code needs different review focus areas than human-written code — especially at data boundaries and in cross-component contracts.

**Where to put it**: `REVIEW.md` at repo root; `.github/workflows/claude_review.yml` for automation

**Quality bar**:
- [ ] Severity levels defined (Critical / Nit / Pre-existing)
- [ ] Review checklist includes invariant verification
- [ ] Cross-boundary data integrity is an explicit review focus
- [ ] Changed files reviewed in full context, not just the diff

**Reference**: [Code Review for AI Guide](./docs/CODE_REVIEW_AI) | [Review Setup Tutorial](./docs/CODE_REVIEW_SETUP)
**Template**: [claude_review.yml](./docs/templates/claude_review.yml)

---

### 2.4 CI/CD Pipeline

**What**: GitHub Actions (or equivalent) that run tests, linting, and type checking on every push and PR.

**Why**: CI is the automated verification loop. It catches the errors that the LLM won't notice in-session.

**Quality bar**:
- [ ] Runs on push and pull_request
- [ ] Executes: install, lint, type-check, test, build
- [ ] Fails the build on any error (no "warn-only" security defaults)
- [ ] SAST/dependency scanning enabled for production projects

**Reference**: [Automation & Testing Guide](./docs/AUTOMATION_TESTING) | [Auditing at Scale](./docs/EXTERNAL_AUDIT_TOOLS)

---

### 2.5 .gitignore and Secrets Hygiene

**What**: Proper .gitignore and separation of secrets from code.

**Why**: LLMs routinely generate code that hardcodes secrets or exposes them in frontend bundles. This is a safety net.

**Quality bar**:
- [ ] `.env` files in `.gitignore`
- [ ] `.env.example` exists with placeholder values (never real secrets)
- [ ] No API keys in frontend-visible env vars (`NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`)
- [ ] External APIs called through server-side proxy routes
- [ ] No secrets in committed code (search for hardcoded keys, tokens, passwords)

**Reference**: [API Key Security Guide](./docs/API_KEY_SECURITY)

---

## Tier 3: Scale and Hardening

For established projects, teams, or anything handling sensitive data.

### 3.1 Threat Model

**What**: A document identifying assets to protect, trust boundaries, attack surface, and mitigations using STRIDE analysis.

**When needed**: Any project handling user data, authentication, financial transactions, or external input.

**Template**: [docs/templates/THREAT_MODEL.md](./docs/templates/THREAT_MODEL.md)

---

### 3.2 Decision Log

**What**: A running log of architectural and product decisions with context and rationale.

**Where to put it**: `docs/DECISIONS.md` or individual ADRs in `docs/decisions/`

**Why**: LLM sessions are ephemeral. Without a decision log, the next session (or the next developer) will re-litigate settled questions.

**Quality bar**:
- [ ] Each entry has: date, decision, context, alternatives considered, rationale
- [ ] Referenced from ARCHITECTURE.md where relevant

---

### 3.3 Checkpoint Summaries

**What**: After each major change, a 5-bullet summary of what changed, new assumptions introduced, and risks added.

**Why**: Creates a rolling audit trail. Reduces confusion in long-running projects.

**Quality bar**:
- [ ] Generated after every major feature or refactor
- [ ] Stored in PR descriptions, DECISIONS.md, or a dedicated CHANGELOG

---

### 3.4 Multi-Agent Git Safety Rules

**What**: Rules for when multiple LLM agents work on the same repo concurrently.

**When needed**: If you run parallel Claude Code sessions, use worktrees, or have multiple developers with agents.

**Quality bar**:
- [ ] Each agent commits from its own branch or worktree
- [ ] `git status` run before every commit to catch cross-agent changes
- [ ] No `git pull` or `git checkout` with uncommitted work from other agents
- [ ] Rules documented in CLAUDE.md

**Reference**: [Version Control Guide — Multi-Agent Safety](./docs/VERSION_CONTROL)

---

### 3.5 Smart Contract Audit Checklist

**What**: Solidity-specific invariants and audit procedures.

**When needed**: Any project involving smart contracts or on-chain logic.

**Reference**: [Smart Contract Auditing Guide](./docs/SMART_CONTRACT_AUDIT)

---

## Completion Report

After working through the checklist, provide a summary:

```markdown
## Incorporation Report

### Created
| File | Purpose |
|------|---------|
| [list files created] | [what each does] |

### Improved
| File | Changes |
|------|---------|
| [list files improved] | [what was improved] |

### Already Adequate
| File | Notes |
|------|-------|
| [list files that needed no changes] | [why they're fine] |

### Recommended Next Steps
1. [Most important follow-up action]
2. [Second priority]
3. [Third priority]

### Skipped (with rationale)
| Item | Why Skipped |
|------|-------------|
| [any skipped items] | [reason — e.g., "no smart contracts in this project"] |
```

---

## Quick Reference: File Placement

```
your-repo/
├── CLAUDE.md                  # Tier 1 — Agent instructions (auto-loaded by Claude Code)
├── README.md                  # Tier 1 — Project front door
├── REVIEW.md                  # Tier 2 — Code review rules
├── .env.example               # Tier 2 — Secret placeholders
├── docs/
│   ├── ARCHITECTURE.md        # Tier 1 — System design
│   ├── INVARIANTS.md          # Tier 1 — Non-negotiable rules
│   ├── ROADMAP.md             # Tier 2 — Phased plan
│   ├── DECISIONS.md           # Tier 3 — Decision log
│   └── THREAT_MODEL.md        # Tier 3 — Security analysis
├── prompts/
│   ├── README.md              # Tier 2 — Prompt index
│   ├── engineering.md         # Tier 2 — Default coding prompt
│   ├── bug-hunt.md            # Tier 2 — Bug detection prompt
│   └── code-review.md         # Tier 2 — Review prompt
├── tests/                     # Tier 1 — Must exist and pass
└── .github/
    └── workflows/
        ├── ci.yml             # Tier 2 — Automated verification
        └── claude_review.yml  # Tier 2 — Automated PR review
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Instead |
|---|---|---|
| **Empty templates** | Generic placeholders provide no guidance | Fill in real content from the actual codebase; mark unknowns as `[TBD]` |
| **Generic invariants** | "Data must be valid" catches nothing | Write domain-specific rules: "User balance must never go negative" |
| **Copy-paste CLAUDE.md** | Wrong conventions confuse the agent | Derive conventions from the actual code, not a template |
| **Docs without enforcement** | Invariants nobody checks are just wishes | Every invariant should map to a test, constraint, or review check |
| **Everything at once** | Creating 15 docs in one session overwhelms | Finish Tier 1 first, iterate on Tier 2 and 3 over time |

---

## Further Reading

| Topic | Guide |
|---|---|
| Full framework overview | [README.md](./README.md) |
| Daily checklist | [CHECKLIST.md](./CHECKLIST.md) |
| Claude Code setup | [Beginner Setup Guide](./docs/BEGINNER_SETUP) |
| Common mistakes | [Anti-Patterns Guide](./docs/ANTI_PATTERNS) |
| Context management | [Context Management Guide](./docs/CONTEXT_MANAGEMENT) |
| Building agents | [Agent Guide Outline](./AGENT_GUIDE_OUTLINE.md) |
| All templates | [docs/templates/](./docs/templates/) |
| All prompts | [prompts/](./prompts/) |
| Bootstrap from scratch | [Project Bootstrap Prompt](./prompts/project-bootstrap.md) |

---

**Remember**: The goal is not to create a pile of documents. It's to give every future LLM session the context it needs to work safely and effectively. A thin, accurate CLAUDE.md and a real INVARIANTS.md are worth more than a dozen empty templates.
