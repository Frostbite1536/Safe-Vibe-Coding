---
layout: default
title: Project Bootstrap for Agents
parent: Prompts Library
nav_order: 14
description: "Bootstrap a new project with Safe Vibe Coding infrastructure."
---

# Project Bootstrap for Agents

A structured prompt for LLM coding agents to set up a new project with Safe Vibe Coding infrastructure. Point an agent at this guide and a new repository to establish the foundation for safe AI-assisted development.

---

## When to Use This Prompt

- Starting a new project from scratch
- Converting an existing project to use Safe Vibe Coding practices
- Onboarding an LLM agent to a repository that needs structure
- Setting up the skeleton infrastructure before implementation begins

---

## The Bootstrap Prompt

Give this prompt to your LLM agent along with the project requirements:

```markdown
## Project Bootstrap: Safe Vibe Coding Infrastructure

You are setting up a new project with Safe Vibe Coding infrastructure.
You are methodical, thorough, and establish foundations before building.
Every file you create will guide future development—make them count.

### Reference Repository

Read and internalize the patterns from:
https://github.com/[org]/Safe-Vibe-Coding

Key documents to study:
- README.md (core principles)
- docs/templates/*.md (file templates)
- prompts/*.md (reusable prompts)

### Project Context

[FILL IN: Describe your project]
- **Name**: [Project name]
- **Type**: [Web app / API / CLI / Library / Service]
- **Tech Stack**: [Languages, frameworks, databases]
- **Purpose**: [What problem it solves]
- **Target Users**: [Who uses it]

### Phase 1: Documentation Foundation

Create these files in order:

#### 1.1 README.md
```
# [Project Name]

[One-paragraph description]

## Quick Start

[How to run locally]

## Architecture

[Brief overview, link to ARCHITECTURE.md]

## Development

[How to contribute, link to other docs]
```

#### 1.2 docs/ARCHITECTURE.md

Use the template structure:
- Overview (purpose, type, users, environment)
- High-level architecture diagram
- Component breakdown with responsibilities
- Data models with constraints
- External dependencies with failure modes
- Key design decisions with rationale
- Security considerations
- Performance considerations

Fill in based on project requirements. Mark unknowns with [TBD].

#### 1.3 docs/INVARIANTS.md

Define the non-negotiable rules:
- Data integrity invariants (what must always be true)
- Security invariants (authentication, authorization boundaries)
- Consistency invariants (what must stay in sync)
- API contract invariants (what the API guarantees)

Use the INV-[CATEGORY]-### naming convention.
Each invariant needs: Rule, Rationale, Examples (valid/invalid), Enforcement.

#### 1.4 docs/THREAT_MODEL.md

For systems handling user data or external input, create a threat model:
- Identify assets to protect (credentials, PII, business data)
- Map trust boundaries (where data crosses security domains)
- Apply STRIDE analysis (Spoofing, Tampering, Repudiation, Information Disclosure, DoS, Elevation of Privilege)
- Document attack surface (entry points, data flows)
- Define security controls (preventive, detective, corrective)

Use threat IDs (S-1, T-1, etc.) and track mitigation status.

#### 1.5 docs/ROADMAP.md

Structure the implementation plan:
- Phase 1: [Foundation - core infrastructure]
- Phase 2: [MVP - minimum viable features]
- Phase 3: [Enhancement - additional features]
- Phase 4: [Polish - optimization, edge cases]

Each phase should list:
- Goals (what success looks like)
- Features included (specific deliverables)
- Explicit exclusions (what's NOT in this phase)

### Phase 2: Project Structure

Create the directory skeleton:

```
[project-root]/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── INVARIANTS.md
│   ├── ROADMAP.md
│   └── DECISIONS.md          # For checkpoint summaries
├── prompts/
│   ├── README.md             # How to use project prompts
│   └── engineering.md        # Default coding prompt
├── src/                      # Or appropriate source directory
│   └── [structure based on tech stack]
├── tests/                    # Or __tests__/ based on convention
│   └── [mirror src structure]
└── [config files]            # package.json, pyproject.toml, etc.
```

### Phase 3: Prompt Library Setup

#### 3.1 prompts/README.md

```markdown
# Project Prompts

Reusable prompts for working with this codebase.

## Available Prompts

- **engineering.md** - Default prompt for feature development
- [Add more as needed]

## Usage

Copy the prompt, fill in context, paste into your LLM conversation.
```

#### 3.2 prompts/engineering.md

Customize the Safe Engineering prompt for this project:

```markdown
## [Project Name] Engineering Prompt

### Role & Context

You are a senior engineer working on [Project Name].
[Brief project description]

### Tech Stack
- [Language/Framework]
- [Database]
- [Key dependencies]

### Architecture Principles
[Summarize from ARCHITECTURE.md]

### Critical Invariants
[List top 3-5 from INVARIANTS.md]

### Coding Standards
- [Project-specific conventions]
- [Naming patterns]
- [File organization rules]

### Before Any Change
1. Check INVARIANTS.md for constraints
2. Review ARCHITECTURE.md for patterns
3. Run existing tests
4. Verify change is minimal and focused
```

### Phase 4: Configuration Files

Create appropriate config files for the tech stack:

#### For Node.js/TypeScript:
- package.json with scripts (test, lint, build)
- tsconfig.json with strict mode
- .eslintrc or eslint.config.js
- .prettierrc

#### For Python:
- pyproject.toml with dependencies and tools
- pytest.ini or pyproject.toml [tool.pytest]
- .flake8 or ruff.toml

#### For any project:
- .gitignore (language-appropriate)
- .editorconfig (consistent formatting)

### Phase 5: Initial Test Setup

Create the test infrastructure:

1. **Test directory structure** matching src/
2. **Example test file** demonstrating patterns
3. **Test configuration** with coverage settings
4. **CI workflow** (.github/workflows/ci.yml)

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup [runtime]
        uses: [appropriate-action]
      - name: Install dependencies
        run: [install command]
      - name: Run tests
        run: [test command]
      - name: Run linter
        run: [lint command]
      - name: Build
        run: [build command]
```

### Phase 6: Verification

After setup, verify:

- [ ] README.md exists and is accurate
- [ ] ARCHITECTURE.md describes the system
- [ ] INVARIANTS.md has at least 3 real invariants
- [ ] ROADMAP.md has phased implementation plan
- [ ] prompts/engineering.md is project-specific
- [ ] Directory structure matches architecture
- [ ] Test framework runs (even with 0 tests)
- [ ] Linter runs without config errors
- [ ] Build command succeeds
- [ ] CI workflow is valid YAML

### Output

When complete, provide:

1. **Summary table** of files created
2. **Next steps** for starting Phase 1 implementation
3. **Any decisions** that need user input
```

---

## Customization Guide

### For Web Applications

Add to prompts/engineering.md:
- Frontend/backend separation
- API contract requirements
- State management approach
- Authentication patterns

Create additional prompts:
- `prompts/frontend-bug-hunt.md`
- `prompts/api-review.md`

### For APIs/Services

Add to INVARIANTS.md:
- Rate limiting guarantees
- Response time SLAs
- Backward compatibility rules
- Versioning strategy

Create additional prompts:
- `prompts/api-design.md`
- `prompts/performance-review.md`

### For Libraries

Add to ARCHITECTURE.md:
- Public API surface
- Backward compatibility policy
- Supported environments/versions

Create additional prompts:
- `prompts/api-compatibility.md`
- `prompts/documentation-review.md`

### For CLI Tools

Add to INVARIANTS.md:
- Exit code conventions
- Output format guarantees
- Configuration precedence

Create additional prompts:
- `prompts/ux-review.md`
- `prompts/help-text-review.md`

---

## Minimal Bootstrap (Quick Start)

For a faster setup, create only these essential files:

1. **README.md** - Project overview and quick start
2. **docs/ARCHITECTURE.md** - System design
3. **docs/INVARIANTS.md** - Non-negotiable rules (at least 3)
4. **prompts/engineering.md** - Customized coding prompt
5. **.github/workflows/ci.yml** - Basic CI pipeline

This gives you the core Safe Vibe Coding infrastructure in 5 files.

**Add if handling user data or external input**:
6. **docs/THREAT_MODEL.md** - Attack surface and mitigations (use STRIDE)

---

## Example: Bootstrapping a Node.js API

```
User: Bootstrap a new project for a REST API that manages user subscriptions.
      Tech stack: Node.js, TypeScript, PostgreSQL, Express.

Agent: I'll set up the Safe Vibe Coding infrastructure for your subscription API.

[Creates files...]

**Files Created:**
| File | Purpose |
|------|---------|
| README.md | Project overview, quick start |
| docs/ARCHITECTURE.md | Component design, data models |
| docs/INVARIANTS.md | Subscription rules, billing constraints |
| docs/ROADMAP.md | 4-phase implementation plan |
| prompts/engineering.md | API-specific coding prompt |
| src/index.ts | Entry point placeholder |
| tests/setup.ts | Test configuration |
| package.json | Dependencies and scripts |
| tsconfig.json | TypeScript configuration |
| .github/workflows/ci.yml | CI pipeline |

**Key Invariants Defined:**
- INV-DATA-001: Subscription dates must be valid ranges
- INV-AUTH-001: Users can only access their own subscriptions
- INV-CONS-001: Billing status must match subscription status

**Next Steps:**
1. Review ARCHITECTURE.md and confirm design
2. Review INVARIANTS.md and add domain-specific rules
3. Begin Phase 1: Database schema and core models

Ready to proceed with implementation?
```

---

## Integration with Other Prompts

After bootstrap, use these prompts for development:

- **[Feature Implementation](./feature-implementation.md)** - Build from ROADMAP.md
- **[Bug Discovery](./bug-hunt.md)** - Audit new code
- **[Invariant Check](./invariant-check.md)** - Verify against INVARIANTS.md
- **[Confidence Sweep](./llm-coding-templates.md)** - Validate stability

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Instead |
|--------------|---------|---------|
| Empty templates | No guidance for future work | Fill in real content, mark unknowns as [TBD] |
| Generic invariants | Don't catch real bugs | Write domain-specific rules |
| Monolithic roadmap | No clear milestones | Break into phases with explicit scope |
| Missing CI | No verification loop | Always set up automated checks |
| Copy-paste prompts | Wrong context | Customize for your specific project |

---

## Remember

> **The goal is to give your future self (and future LLM sessions) the context they need to work safely and effectively.**

Time spent on infrastructure now saves exponentially more time later. A well-bootstrapped project makes every future coding session faster and safer.
