# Prompt Library

This directory contains reusable prompts for working with LLMs on software projects. Each prompt is designed to invoke a specific mode or perspective from the LLM.

---

## Available Prompts

### Engineering & Development

- **[engineering-prompt.md](./engineering-prompt.md)** - Production-grade code with conservative, proven patterns
  - Use when: Building new features, writing production code
  - Focus: Maintainability, modularity, security, respecting architecture

- **[modularity-review.md](./modularity-review.md)** - Review code for modularity issues and recommend restructuring
  - Use when: Files are growing large (> 1,500 lines) or becoming hard to understand
  - Focus: File size, single responsibility, interface clarity, AI-compatibility

- **[refactor-for-clarity.md](./refactor-for-clarity.md)** - Improve code readability without changing behavior
  - Use when: Code works but is hard to understand
  - Focus: Clarity, simplicity, maintainability

### Quality & Testing

- **[bug-hunt.md](./bug-hunt.md)** - Proactive bug detection after changes
  - Use when: After implementing features or significant changes
  - Focus: Logic errors, edge cases, security, invariant violations

- **[performance-review.md](./performance-review.md)** - Identify performance bottlenecks and optimization opportunities
  - Use when: Performance issues suspected or pre-launch optimization
  - Focus: Database, algorithms, caching, memory usage

### User Experience

- **[user-feedback-simulation.md](./user-feedback-simulation.md)** - Simulate user testing to find UX issues
  - Use when: Testing new features or flows
  - Focus: Usability, confusion, friction, accessibility

---

## How to Use These Prompts

1. **Copy the entire prompt** (including context and instructions)
2. **Fill in the placeholders** (marked with [brackets])
3. **Paste into your LLM conversation**
4. **Provide the code/context** the LLM needs to review

---

## Creating Your Own Prompts

When creating project-specific prompts:

1. **Be explicit about the role**: "You are a [role] doing [task]"
2. **Provide constraints**: What should/shouldn't be changed
3. **List specific checks**: Concrete things to look for
4. **Define output format**: How results should be structured
5. **Include examples**: Show what good output looks like

---

## Prompt Naming Convention

Use descriptive, action-oriented names:
- `[action]-[target].md` (e.g., `review-api-contracts.md`)
- `[role]-prompt.md` (e.g., `frontend-engineer-prompt.md`)
- `[mode]-mode.md` (e.g., `debug-mode.md`)

---

## Contributing New Prompts

Found a prompt pattern that works well? Add it here:

1. Create a new `.md` file with a clear name
2. Follow the structure of existing prompts
3. Update this README with a brief description
4. Test it on your project first

---

## Best Practices

- **Be specific**: Vague prompts get vague results
- **Iterate on prompts**: Refine based on what works
- **Version your prompts**: Track what changes you make
- **Share what works**: If a prompt is effective, document why

---

## Language-Specific Prompts

As your project grows, consider creating:
- `python-engineering.md` (Python-specific patterns)
- `react-bug-hunt.md` (React-specific issues)
- `sql-performance.md` (Database-specific optimization)

Keep them in subdirectories if you have many:
```
prompts/
├── general/
├── python/
├── javascript/
└── sql/
```
