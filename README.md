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

### 9. Run Frequent Bug Hunts

In addition to automated tests, regularly ask the LLM to:
- Review recent changes for bugs
- Check edge cases
- Look for regressions against earlier assumptions

This can be done incrementally—after each feature or group of changes. Treat bug hunts as routine hygiene, not emergency response.

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

---

## Getting Started

1. **Use the templates** in [`/docs/templates`](./docs/templates) to set up your project documentation
2. **Browse example prompts** in [`/prompts`](./prompts) to see how to communicate effectively with LLMs
3. **Start with the product conversation** before writing any code
4. **Establish your invariants early** and refer to them often

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
