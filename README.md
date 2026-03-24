# Vibe Coding with LLMs: A Practical Guide to Building Real Software

This guide describes a collaborative, structured way to build software with LLMs while maintaining correctness, stability, and long-term maintainability. The goal is not novelty—it's shipping reliable systems without losing momentum. 

---

## Core Principles

Vibe coding works because it replaces "trusting the model" with **systems that enforce correctness**. You move fast without breaking things—not because the LLM is perfect, but because your process is.

**Treat the LLM as a junior engineer with infinite stamina**: fast, tireless, and helpful—but lacking long-term judgment unless you supply it.

Your job is to provide:
- Constraints
- Invariants
- Tests
- Clear expectations

---

## The Workflow

### 1. Start with a Product Conversation, Not Code

Begin by talking to the LLM about **what** you want to build, not **how** to build it yet. Describe:
- The problem
- The type of program (web app, service, CLI, library, embedded system, etc.)
- The users
- The environment it will run in

Treat this as a design discussion. Bounce ideas back and forth. Let the model question assumptions, suggest alternatives, and surface risks early.

**Explicitly prompt the model to act as an expert** in the relevant domain (for example: "You are a senior backend engineer building production APIs"). This anchors responses in proven patterns instead of generic or experimental approaches.

### 2. Co-Design the Prompt Before Writing Code

Before implementation, ask the LLM to help refine the prompt it should follow. Have it identify:
- Missing constraints
- Ambiguous requirements
- Trade-offs that should be decided explicitly

This step dramatically improves output quality. You are aligning on expectations before any code exists.

### 3. Produce a Roadmap with Clear Phases

Once the idea is clear, have the LLM generate a roadmap broken into phases. Each phase should include:
- Goals
- Features included
- Explicit exclusions

Phases reduce scope creep and give you natural checkpoints to reassess direction.

### 4. Create Architecture and README Documents Early

Before significant coding, generate:
- An **architecture document** (components, responsibilities, data flow)
- A **README** (what the project is, how it's structured, how to run it)

These documents act as anchors. They help both you and the LLM maintain consistency across long sessions and incremental changes.

**Update them as the system evolves.**

See [`/docs/templates`](./docs/templates) for starting templates.

### 5. Define System Invariants & Contracts (Non-Negotiables)

Create a document that defines the **non-negotiable truths** of your system: rules that must always hold, regardless of UI, API path, ingest source, or future feature additions. These invariants are the foundation for correctness, trust, and long-term maintainability.

**If a change violates an invariant, it is a bug or a product decision—never an implementation detail.**

Examples of invariants might include:
- Data integrity rules
- Security boundaries
- Authorization guarantees
- Ordering, idempotency, or consistency requirements
- Performance or availability assumptions

This document should be consulted before changing behavior. If new code conflicts with it, either the code is wrong or the invariant must be consciously revised.

See [`/docs/templates/INVARIANTS.md`](./docs/templates/INVARIANTS.md) for a template.

### 6. Add Tests Immediately—and Keep Adding Them

Introduce tests as soon as real code appears.

Start with:
- Static pattern tests (linting, formatting, type checks)
- Basic functional tests for core flows

**Run tests before accepting or merging any new feature or refactor** produced by the LLM.

As features are added, add tests alongside them. Over-testing early may feel annoying, but it is far cheaper than debugging later—especially with fast-moving AI-assisted development.

**Tests are not optional feedback; they are gates.**

### 7. Optimize for Boring, Conventional Code

Tell the LLM explicitly:
- You want boring, predictable, production-grade solutions
- Prefer established patterns and idioms
- Avoid clever abstractions unless asked

**Boring code is successful code. Creativity is opt-in. Reliability is the default.**

This single instruction prevents a large class of long-term maintenance problems.

### 8. Favor Modularity as a First-Class Constraint

Favor modularity aggressively. Keep files small, focused, and single-purpose. As a practical guideline, **avoid scripts or files longer than ~1,500 lines**. This is not an arbitrary style preference—it is a reliability constraint when collaborating with LLMs.

**LLMs reason best over code they can fully and clearly "see."** Large, monolithic files reduce the model's ability to understand context, increase hallucinations, and make subtle bugs more likely. Smaller modules improve correctness, review quality, and iteration speed.

#### Design for Comprehension, Not Just Execution

A program that runs is not necessarily a program that can be safely modified. Code should be structured so that both humans and LLMs can understand it in isolation.

Each module should:
- Have a single responsibility
- Expose a clear interface
- Hide internal implementation details
- Be understandable without reading the entire codebase

**If a file requires scrolling constantly or holding many concepts in your head at once, it is doing too much.**

#### Prefer Composition Over Growth

When adding features, resist the temptation to extend existing large files. Instead:
- Extract new behavior into new modules
- Introduce clear boundaries between concerns
- Keep changes localized

Growth should increase the number of small, understandable pieces—not inflate a few central ones.

#### Modular Boundaries Improve AI Collaboration

Modularity creates natural checkpoints for AI-assisted work:
- The LLM can reason about a single module at a time
- Bug hunts can target specific components
- Refactors become safer and more predictable
- Tests can map cleanly to modules

This also makes it easier to give the LLM precise instructions: "Modify this module only" or "Add a new module that implements X."

#### File Size as a Soft Safety Limit

Treat ~1,500 lines as a soft upper bound, not a strict rule. Hitting that limit is a signal to pause and ask:
- Can this be split?
- Are responsibilities mixed?
- Is there a missing abstraction?

Smaller files are easier to test, easier to document, and easier to reason about—especially across long sessions or future revisits.

#### Modularity Reinforces Other Guardrails

Good modularity directly supports:
- Strong System Invariants (enforced at boundaries)
- Cleaner architecture documents
- More targeted tests
- Reduced regression risk
- Faster and safer LLM iteration

**In short: modular code is not just cleaner—it is more AI-compatible.**

### 9. Run Frequent Bug Hunts — Especially at Component Boundaries

In addition to automated tests, regularly ask the LLM to:
- Review recent changes for bugs
- Check edge cases
- Look for regressions against earlier assumptions
- **Audit data as it crosses component boundaries** (the most important and most overlooked)

LLM-generated code has a characteristic failure mode: **each module works correctly in isolation, but the contracts between modules are implicit and sometimes contradictory.** This happens because different modules are often generated in separate sessions with no shared memory of the exact agreements between them.

The highest-value bug hunts focus on the **arrows** between components, not the components themselves:
- Does every layer that touches a data model agree on its fields, types, and semantics?
- Does a round-trip (save → restore, serialize → deserialize) preserve all fields?
- If an operation fails midway, is state rolled back or left half-modified?
- When combining data from multiple sources, are units and semantics compatible?
- After fixing a bug, does the same bug class exist in other files generated during different sessions?

Treat bug hunts as routine hygiene, not emergency response. Run them incrementally after each feature or group of changes.

### 10. Maintain a Prompt Library Inside the Codebase

Keep a `/prompts` folder in the repository containing reusable, role-specific prompts. These act as tools you can invoke consistently.

Examples:
- Engineering prompt (architecture-aware, conservative)
- Frontend bug hunt
- Backend bug hunt
- Bug fixing mode
- User feedback testing (model simulates user behavior and confusion)
- Refactor for clarity
- Performance review

These prompts reduce variance and help you re-enter the correct mindset instantly.

See [`/prompts`](./prompts) for examples.

### 11. Keep Documentation in Sync with Reality

As the system changes:
- Update the README
- Update the architecture doc
- Update the System Invariants & Contracts **if (and only if) product decisions change**

**Drift between code and documentation is one of the fastest ways to lose control of an AI-assisted project.**

### 12. Treat the LLM as a Junior Engineer with Infinite Stamina

The LLM is fast, tireless, and helpful—but it lacks long-term judgment unless you supply it.

Your job is to provide:
- Constraints
- Invariants
- Tests
- Clear expectations

Do that, and vibe coding becomes not just productive, but **safe**.

### 13. Generate Checkpoint Summaries After Major Changes

After completing significant features or changes, create a checkpoint summary. This builds a rolling audit trail that prevents long-term context loss.

**Ask the LLM to produce**:
- A 5-bullet summary of what changed
- Any new assumptions introduced
- Any risks or trade-offs added

**Why this matters**:
- Creates a searchable history of decisions
- Helps you (or future developers) understand why things are the way they are
- Catches drift before it compounds
- Makes it easier to resume work after breaks

**Example checkpoint**:

```
## Checkpoint: Added OAuth Authentication (2024-01-15)

### What Changed
- Added OAuth 2.0 support for Google and GitHub
- Created new OAuthController and token validation middleware
- Updated User model to support optional password field
- Added OAuth configuration to environment variables
- Migrated database to add oauth_provider and oauth_id columns

### New Assumptions
- OAuth providers return verified email addresses
- OAuth tokens are validated on every request (no local caching)
- Users can have either password OR OAuth, not both
- Google/GitHub APIs remain stable and available

### Risks & Trade-offs
- OAuth provider outages prevent login (mitigation: support multiple providers)
- Token validation adds latency to every request (acceptable for our scale)
- Email uniqueness now depends on OAuth provider behavior (documented in INVARIANTS.md)
```

Store checkpoints in:
- A `CHANGELOG.md` or `DECISIONS.md` file in `/docs`
- Commit messages (for smaller changes)
- PR descriptions
- Architecture document updates

**Treat checkpoints as future documentation**. When you return to the project in 6 months, these summaries are invaluable.

---

## Essential Reading

Before you start vibe coding, read these critical documents. They address common failure modes and essential practices:

### 🚀 New to Claude Code? Start Here!

- **[Claude Code Setup Guide](./docs/BEGINNER_SETUP.md)** - Comprehensive beginner guide
  - Terminal configuration and notifications
  - Running multiple Claude instances in parallel
  - Plan mode, CLAUDE.md, slash commands
  - Subagents, skills, and hooks
  - MCP servers and verification loops

### 📖 Core Guides

- **[Context Management](./docs/CONTEXT_MANAGEMENT.md)** - How to maintain coherent context across sessions
  - When to start fresh conversations
  - Preventing context pollution
  - Managing context window limits
  - Session continuity patterns

- **[Code Review for AI](./docs/CODE_REVIEW_AI.md)** - How to review AI-generated code
  - AI-specific code smells and cross-boundary review
  - Severity classification (Critical / Nit / Pre-existing)
  - REVIEW.md convention for review-specific rules
  - Human review checkpoints (non-negotiable)

- **[Setting Up AI Code Review](./docs/CODE_REVIEW_SETUP.md)** - Tutorial: from zero to automated PR reviews
  - Level 1: One-off reviews in your terminal (zero setup)
  - Level 2: `/review-pr` slash command (2 min setup)
  - Level 3: GitHub Actions pipeline with inline PR comments (10 min setup)

- **[Anti-Patterns & Warning Signs](./docs/ANTI_PATTERNS.md)** - When AI development goes wrong
  - Recognizing when LLM is leading you astray
  - Common anti-patterns (Framework Fever, The God File, etc.)
  - Course correction strategies
  - When AI is the wrong tool

- **[Version Control Best Practices](./docs/VERSION_CONTROL.md)** - Git workflow for AI-assisted development
  - Atomic commits with AI code
  - Reviewing diffs before committing
  - Branching for experiments
  - Commit message templates

- **[Automation & Testing](./docs/AUTOMATION_TESTING.md)** - Automated quality gates for AI code
  - GitHub Actions CI/CD pipelines
  - Claude Code hooks (PostToolUse for auto-formatting)
  - Pre-commit hooks and static analysis
  - Security scanning (CodeQL, Semgrep, Gitleaks)
  - Verification loops (key to quality AI code)
  - Claude Code GitHub Action for PR reviews

- **[Emotional Prompt Engineering](./docs/EMOTIONAL_PROMPT_ENGINEERING.md)** - Using psychology to improve LLM output
  - Why telling LLMs they're "the best" actually works
  - EmotionPrompt research and findings
  - Effective vs. ineffective "hype" strategies
  - The sycophancy trap and how to avoid it
  - High-competence prompt formulas

- **[Building MCP Servers](./docs/MCP_DEVELOPMENT.md)** - Hard-won lessons from real MCP server implementations
  - What MCP servers are and why you'd build one
  - Why your consumer is an LLM, not a human
  - Input validation, error handling, and serialization
  - The 15 most common bug patterns (with fixes)
  - Design-time practices that prevent MCP bugs later
  - Complete build/review checklist

- **[MCP Tool Grouping](./docs/MCP_TOOL_GROUPING.md)** - Scaling MCP servers beyond 20 tools
  - Reducing token cost by 50-95% with tool grouping
  - Enable/disable meta-tools and per-session state
  - The critical deadlock bug every implementation hits
  - HTTP mode global state traps and fixes
  - Design principles and complete checklist

- **[Plan-Driven Development](./docs/PLAN_DRIVEN_DEVELOPMENT.md)** - Reliable results from coding agents through structured planning
  - Six-phase workflow: ideation, plan, audit, sequencing, execution, code audit
  - Why plans always have bugs and how to catch them
  - Prompt sequencing for large projects
  - CLAUDE.md as a plan accelerator
  - Templates for plan requests, audits, and code reviews

- **[Dependency Safety](./docs/DEPENDENCY_SAFETY.md)** - Evaluating and managing AI-suggested packages
  - Hallucinated packages and supply chain attacks
  - The 60-second package evaluation check
  - When you don't need a dependency at all
  - Pinning, lockfiles, and version discipline
  - CLAUDE.md rules to prevent bad suggestions

**Start here**: If you only read one, read [Anti-Patterns & Warning Signs](./docs/ANTI_PATTERNS.md). It will save you from the most common mistakes.

---

## Getting Started

1. **Review the [quick-reference checklist](./CHECKLIST.md)** - Print it and keep it handy
2. **Read [Essential Reading](#essential-reading)** - Understand critical practices and failure modes
3. **Use the templates** in [`/docs/templates`](./docs/templates) to set up your project documentation
4. **Browse example prompts** in [`/prompts`](./prompts) to see how to communicate effectively with LLMs
5. **Start with the product conversation** before writing any code
6. **Establish your invariants early** and refer to them often

---

## Why This Works

Traditional software development emphasizes careful upfront planning because writing code is expensive. With LLMs, code generation is cheap—but **maintaining correctness is still hard**.

This workflow inverts the traditional approach:
- Spend time on constraints, tests, and documentation
- Let the LLM handle the tedious implementation
- Use automated checks to catch drift

The result: **velocity without chaos.**

---

## Contributing

This guide is a living document. If you've found patterns that work (or anti-patterns that don't), please contribute:

1. Share your templates in `/docs/templates`
2. Add useful prompts to `/prompts`
3. Document lessons learned

---

## License

This guide is released into the public domain. Use it however helps you build better software.
