---
layout: default
title: Guides
nav_order: 3
has_children: true
description: "Essential guides and documentation for safe vibe coding."
permalink: /docs/
---

# Guides

This section contains essential guides and documentation templates for safe vibe coding projects.

---

## Essential Guides

These documents cover critical practices for successful AI-assisted development:

### [Claude Code Setup Guide](./BEGINNER_SETUP.md) (Start Here!)
Comprehensive beginner-friendly guide to setting up Claude Code. Covers:
- Terminal configuration (notifications, line breaks)
- Running multiple Claude instances in parallel
- Plan mode for complex tasks
- CLAUDE.md: teaching Claude your codebase
- Slash commands, subagents, and skills
- Hooks for auto-formatting and verification
- MCP servers for external tools
- Model selection and verification loops

**Read this to**: Get the most out of Claude Code from day one.

### [Context Management](./CONTEXT_MANAGEMENT.md)
How to maintain coherent context across LLM sessions. Covers:
- Starting new sessions with proper warm-up
- Preventing context pollution
- Managing context window limits
- Session continuity patterns
- When to start fresh vs. continue

**Read this to**: Avoid confusion and maintain productive AI collaboration across sessions.

### [Code Review for AI-Generated Code](./CODE_REVIEW_AI.md)
How to review AI outputs effectively. Covers:
- AI-specific code review checklist
- Security review requirements
- Human review checkpoints (non-negotiable)
- AI code smells and red flags
- Iterative refinement techniques

**Read this to**: Catch AI mistakes before they reach production.

### [Anti-Patterns & Warning Signs](./ANTI_PATTERNS.md)
When AI development goes wrong and how to recover. Covers:
- Recognizing when LLM is leading you astray
- Common anti-patterns (Framework Fever, Testing Theater, etc.)
- Course correction strategies
- When AI is the wrong tool
- Emergency procedures

**Read this to**: Avoid common failure modes and know when to course-correct.

### [API Key & Secrets Security](./API_KEY_SECURITY.md)
How to keep API keys out of your frontend code. Covers:
- Why 9/10 vibe-coded apps leak credentials
- Server-side proxy patterns for all major frameworks
- Environment variable best practices
- Framework-specific guidance (Next.js, Vite, Express, FastAPI)
- How to check for leaks (Network tab, source search)
- Pre-commit hooks for secret detection

**Read this to**: Stop your app from leaking API keys in the browser Network tab.

### [Version Control Best Practices](./VERSION_CONTROL.md)
Git workflow for AI-assisted development. Covers:
- Atomic commits with AI code
- Reviewing diffs before committing
- Branching strategies for experiments
- Commit message templates
- Handling failed AI attempts

**Read this to**: Use git effectively as a safety net for AI development.

### [Setting Up AI Code Review](./CODE_REVIEW_SETUP.md)
Step-by-step tutorial for automated code review with Claude Code. Covers:
- Level 1: Zero-setup one-off reviews in your terminal
- Level 2: Reusable `/review-pr` slash command (2 min setup)
- Level 3: Fully automated GitHub Actions pipeline with inline PR comments
- REVIEW.md convention for project-specific review rules
- Cost expectations and security considerations

**Read this to**: Get automated code review working in your project, from simple to fully automated.

### [Audit Findings & Lessons](./AUDIT_FINDINGS.md)
Real findings from a security audit of an AI-generated app. Covers:
- 11 real vulnerabilities (XSS, domain bypass, unpinned deps, cleartext traffic)
- 3 LLM root causes: "local fix, global miss", shortcut matching, "make it work" mindset
- Audit checklist for vibe-coded projects
- Prompt templates for catching these patterns

**Read this to**: Learn the predictable security mistakes LLMs make and how to catch them.

### [Automation & Testing](./AUTOMATION_TESTING.md)
Comprehensive automation and CI/CD for AI-assisted projects. Covers:
- GitHub Actions workflows for automated testing
- Claude Code hooks (PostToolUse for auto-formatting)
- Pre-commit hooks with the pre-commit framework
- Static analysis tools (ESLint, Pylint, SonarCloud)
- Security scanning (CodeQL, Semgrep, Gitleaks)
- Dependency vulnerability auditing
- Code coverage enforcement
- Verification loops (the key to quality AI code)
- Claude Code GitHub Action for PR reviews

**Read this to**: Set up automated quality gates that catch issues humans miss.

### [MCP Tool Grouping](./MCP_TOOL_GROUPING.md)
How to scale MCP servers beyond 20 tools without burning tokens. Covers:
- Why tool schemas cost thousands of tokens per turn at scale
- Enable/disable meta-tools with per-session group state
- The critical deadlock bug every implementation hits (and the fix)
- HTTP mode global state traps
- Design principles: groups map to domains, not access levels
- Complete checklist for group definitions, meta-tools, startup, runtime, and testing

**Read this to**: Keep token costs manageable as your MCP server grows, without breaking agent functionality.

### [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT.md)
A structured workflow for human-agent paired development. Covers:
- Six-phase process: ideation, plan creation, plan audit, prompt sequencing, execution, code audit
- Why implementation plans always have 1-3+ bugs and how to catch them before coding
- Prompt sequencing for large projects that span multiple sessions
- CLAUDE.md as a plan accelerator
- When to scrap and replan (the rule of three)
- Templates for plan requests, audits, prompt sequencing, and code reviews

**Read this to**: Get reliable, auditable results from coding agents on projects of any size.

### [Dependency Safety](./DEPENDENCY_SAFETY.md)
How to evaluate, vet, and manage dependencies when an LLM is picking your packages. Covers:
- The three ways AI gets dependencies wrong (hallucinated, abandoned, unnecessary)
- The 60-second package evaluation check
- Hallucinated packages as a supply chain attack vector
- Pinning, lockfiles, and CDN version discipline
- CLAUDE.md rules to prevent bad dependency suggestions
- Decision framework: when to add a package vs. write it yourself

**Read this to**: Stop blindly installing whatever the AI suggests and keep your dependency tree secure.

### [Refactoring with AI](./REFACTORING_WITH_AI.md)
How to refactor safely with AI assistance. Covers:
- The risk spectrum: low, medium, and high-risk refactoring operations
- The incremental method: one change, one test run, one commit
- Six specific failure modes (collapsed duplication, execution order, lost error context, scope creep, silent contract changes, circular dependencies)
- Refactoring patterns that work well with AI vs. patterns that don't
- Scope control techniques to prevent the AI from expanding beyond your request
- When NOT to refactor with AI (no tests, don't understand the code, under time pressure)

**Read this to**: Keep refactoring from turning into a rewrite that introduces subtle bugs.

### [After the Merge](./AFTER_THE_MERGE.md)
Deployment, monitoring, and production readiness for AI-generated code. Covers:
- Pre-deployment checklist (environment, dependencies, build, database)
- Deployment strategies (rolling, blue-green, canary, feature flags)
- The four monitoring signals and AI-specific monitoring priorities
- Structured logging rules to surface silent failures
- Rollback planning and decision framework
- Incident response for systems you didn't fully write
- Production hardening checklist (timeouts, rate limits, error handling, security)
- CLAUDE.md rules to prevent common production issues at generation time

**Read this to**: Ship AI-generated code to production without waking up at 3 AM.

### [Team Workflows](./TEAM_WORKFLOWS.md)
Patterns for teams using AI-assisted development together. Covers:
- Shared CLAUDE.md as the team's constitution for conventions and decisions
- Code ownership rules: whoever prompts the AI owns the output
- The double-AI problem: when AI writes code and AI reviews it
- Branching discipline, parallel AI sessions, and merge conflict handling
- Onboarding new team members to AI-assisted workflows
- Knowledge sharing: the mistake-to-rule pipeline
- Scaling patterns for small (2-5), medium (6-15), and large (15+) teams
- Team-specific anti-patterns and how to avoid them

**Read this to**: Coordinate AI-assisted development across your team without diverging into chaos.

### [Legacy Codebases](./LEGACY_CODEBASES.md)
Introducing AI-assisted development into existing, mature codebases. Covers:
- Codebase survey: assessing architecture, conventions, test coverage, and debt
- Building CLAUDE.md from existing code (document reality, not aspirations)
- Adding tests to untested code: characterization tests and the test-first-then-change rule
- Safe modification patterns: expansion, strangler fig, and seam patterns
- Migration strategies: incremental batch migration, database migrations, dependency upgrades
- Working with large files: structural overview, targeted analysis, safe splitting
- Legacy-specific anti-patterns ("let the AI rewrite it", "quick modernization")

**Read this to**: Get AI working safely on code that's been in production for years.

### [When AI Audits Go Wrong](./AI_AUDIT_FAILURES.md)
A three-act debugging story where an AI auditor, an AI fixer, and a git baseline error sent everyone chasing a phantom problem. Covers:
- Three distinct failure layers: trusting AI reports, wrong diff baselines, AI agents debugging each other in circles
- Why `git diff main..branch` vs `git diff main...branch` matters for AI reviews
- The meta-lesson: blindly trusting AI reviews is the same mistake as blindly trusting AI code
- Prevention playbook for AI-assisted audits and code reviews
- Investigation questions for both the fixing and auditing agents

**Read this to**: Stop trusting AI-generated audit reports the same way you stopped trusting AI-generated code.

### [Expert Panel Evaluation](./EXPERT_PANEL_EVALUATION.md)
Using simulated expert committees to find architectural, economic, and systemic problems before they calcify. Covers:
- The core idea: assembling virtual expert panels to critique what you've built
- Six-step workflow: identify domains, prime context, run evaluations, consolidate, plan, build
- Adversarial personas for finding exploits, attack surfaces, and gaming strategies
- Anti-sycophancy techniques: demand asymmetry, minimum finding counts, failure scenarios
- Expert panel templates for different system types (games, payments, auth, ML, APIs)
- Integration points with the vibe coding workflow and plan-driven development

**Read this to**: Discover the problems in your system that code review and bug hunts don't catch.

### [Smart Contract Auditing](./SMART_CONTRACT_AUDIT.md)
Lessons from a real multi-agent audit of 4 UUPS-upgradeable Solidity contracts. Covers:
- Five vulnerability categories: pause-weaponized time, mutable config on committed funds, external calls in critical paths, privileged role abuse, state lifecycle gaps
- What AI auditors get right and wrong — including bugs in their own fix suggestions
- The two-pass audit workflow: external audit → self-audit of the fixes
- Human-agent collaboration lessons for security-critical code
- Comprehensive smart contract deployment checklist
- Prompt templates for audits, fix implementation, and cross-contract consistency checks

**Read this to**: Audit AI-generated smart contracts and run effective multi-agent security reviews.

### [Auditing at Scale](./EXTERNAL_AUDIT_TOOLS.md)
When your AI-generated codebase outgrows a single agent's context window. Covers:
- Why agent self-review breaks down at scale (contextual drift, context window limits)
- Four tool categories: repository-wide reasoning, security scanning (SAST), noise reduction/triage, code quality
- Decision framework for choosing tools based on your primary concern
- Building a layered audit stack (continuous, periodic, milestone)
- Integration patterns: feeding tool output back into AI agent workflows
- Step-by-step first audit setup (security scan, quality baseline, architecture review)

**Read this to**: Choose and set up external auditing tools when your codebase is too large for AI agents to review alone.

---

## Templates

The [`templates/`](./templates) directory contains starter templates for project documentation:

- **[ARCHITECTURE.md](./templates/ARCHITECTURE.md)** - System architecture and design decisions
  - Use this to document components, data flow, and key technical decisions
  - Update when you add new components or change system structure

- **[INVARIANTS.md](./templates/INVARIANTS.md)** - System invariants and contracts
  - Define non-negotiable rules that must always hold
  - Reference this before implementing features
  - Update only when product decisions change core rules

- **[ROADMAP.md](./templates/ROADMAP.md)** - Development roadmap and phases
  - Break your project into clear phases with goals and exclusions
  - Update at the end of each phase
  - Use for planning and stakeholder communication

- **[PROJECT_README.md](./templates/PROJECT_README.md)** - Starter README for your project
  - Copy this to your project root and customize
  - Keep it updated as the project evolves

---

## How to Use Templates

1. **Copy the template** to your project's documentation folder
2. **Fill in the placeholders** (marked with [brackets])
3. **Remove sections** that don't apply to your project
4. **Keep them updated** as your project evolves

---

## Documentation Principles

### Write for Your Future Self

Document as if you're explaining to yourself 6 months from now, after you've forgotten all context.

### Keep Docs Close to Code

Store documentation in the repository, versioned alongside the code. This ensures docs and code stay in sync.

### Update Before You Forget

Update documentation immediately after making changes. If you wait, you'll forget the details.

### Document Decisions, Not Just Facts

Explain **why** decisions were made, not just **what** was decided. Future maintainers need context.

### Less is More

Don't document the obvious. Focus on:
- Non-obvious design decisions
- Invariants that must be maintained
- Integration points and contracts
- Known limitations and trade-offs

---

## Documentation Workflow with LLMs

1. **Start with templates**: Have the LLM fill in initial versions based on your description
2. **Review and refine**: The LLM's first pass is a starting point, not the final version
3. **Keep docs updated**: Ask the LLM to update relevant docs when making changes
4. **Reference in prompts**: Tell the LLM to check docs before making changes

Example prompt:
```
Before implementing this feature, review ARCHITECTURE.md and INVARIANTS.md
to ensure the implementation aligns with our system design and doesn't
violate any invariants.
```

---

## When to Create New Documents

Create documentation when:
- **A decision needs to persist**: If you'll need to remember this in 6 months
- **Multiple people need to understand**: If this will be maintained by others
- **Integration points exist**: APIs, contracts, external dependencies
- **Complexity is unavoidable**: When the code alone isn't self-explanatory

Don't create documentation for:
- Obvious code patterns
- Things that change frequently
- Information already in code comments
- Process that's better handled by tools (e.g., setup scripts)

---

## Keeping Documentation in Sync

**The Problem**: Code evolves, docs drift, trust erodes.

**The Solution**:
1. Make doc updates part of the definition of "done"
2. Ask the LLM to identify doc updates needed when reviewing changes
3. Include doc checks in code review
4. Keep docs minimal so updates are lightweight

**Warning signs of drift**:
- Developers don't reference docs
- Docs describe features that don't exist
- New team members find docs misleading

---

## Project-Specific Documentation

Beyond these templates, consider adding:
- **API documentation** (if you have APIs)
- **Deployment guide** (if deployment is non-trivial)
- **Troubleshooting guide** (common issues and solutions)
- **Contributing guide** (for open source or team projects)

But remember: **Only create docs that provide value**. Don't document for the sake of documenting.
