# Documentation

This directory contains documentation templates and essential guides for safe vibe coding projects.

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

### [Version Control Best Practices](./VERSION_CONTROL.md)
Git workflow for AI-assisted development. Covers:
- Atomic commits with AI code
- Reviewing diffs before committing
- Branching strategies for experiments
- Commit message templates
- Handling failed AI attempts

**Read this to**: Use git effectively as a safety net for AI development.

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
