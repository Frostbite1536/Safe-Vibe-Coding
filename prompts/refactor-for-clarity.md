---
layout: default
title: Refactor for Clarity
parent: Prompts Library
nav_order: 9
---

# Refactor for Clarity Prompt

Use this prompt when code is working but hard to understand or maintain.

---

## Prompt

You are refactoring code to improve clarity and maintainability **without changing behavior**.

**Target code**: [paste code or specify file/function]

**Constraints**:
- **Do not change behavior**: All tests must still pass
- **Do not change APIs**: External interfaces remain the same
- **Do not add features**: This is purely a clarity refactor

**Refactoring goals**:

1. **Improve Naming**:
   - Use descriptive variable/function names
   - Avoid abbreviations unless universally understood
   - Name things after what they represent, not their type

2. **Simplify Control Flow**:
   - Reduce nesting (early returns, guard clauses)
   - Eliminate unnecessary conditionals
   - Extract complex conditions into well-named variables or functions

3. **Reduce Complexity**:
   - Break large functions into smaller, focused ones
   - Limit function length (aim for < 50 lines)
   - Reduce cyclomatic complexity

4. **Eliminate Redundancy**:
   - Remove duplicate code
   - Extract common patterns
   - But avoid premature abstraction (3 uses before extracting)

5. **Improve Data Structures**:
   - Use appropriate data structures (map vs array, set vs array)
   - Make implicit state explicit
   - Group related data into objects/structs

6. **Clarify Intent**:
   - Use language features that express intent (map/filter/reduce vs loops)
   - Make assumptions explicit
   - Document why, not what (if needed)

7. **Remove Dead Code**:
   - Unused variables, functions, imports
   - Commented-out code
   - Unreachable code

**Anti-patterns to avoid**:
- Don't abstract for a single use case
- Don't add type annotations to everything (only where they add clarity)
- Don't over-engineer simple logic
- Don't change working error handling unless it's truly unclear

**Process**:
1. Understand current behavior (read tests if available)
2. Identify primary clarity issues
3. Propose refactoring
4. Verify behavior is preserved

**Output**:
- List the specific clarity problems found
- Show the refactored code
- Explain what changed and why it's clearer
- Confirm: "Behavior is unchanged. All tests should still pass."

**Remember**: The goal is **clarity**, not cleverness.
