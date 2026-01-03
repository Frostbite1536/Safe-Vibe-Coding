---
layout: default
title: Modularity Review
parent: Prompts Library
nav_order: 8
---

# Modularity Review Prompt

Use this prompt to review code for modularity issues and get recommendations for breaking down large or complex files.

---

## Prompt

You are conducting a modularity review of the codebase. Your goal is to identify files and components that violate modularity principles and recommend how to restructure them for better AI collaboration and long-term maintainability.

**Code to review**: [paste code, specify files, or describe scope]

**Context**:
- File size guideline: **~1,500 lines maximum** (soft limit)
- LLMs reason best over code they can fully "see"
- Modularity improves correctness, review quality, and iteration speed

---

## Review Methodology

### 1. File Size Analysis

**Check for**:
- Files exceeding ~1,500 lines
- Files that require extensive scrolling to understand
- Files that mix multiple concerns

**Questions**:
- What's the line count of each file?
- Are there natural split points?
- What's preventing this from being smaller?

### 2. Single Responsibility Principle

**Check for**:
- Files doing more than one thing
- Mixed concerns (business logic + UI + data access)
- Unclear file purpose from the name
- Multiple unrelated exports from a single module

**Questions**:
- What is this file's primary responsibility?
- What secondary responsibilities could be extracted?
- Does the filename accurately reflect what it does?

### 3. Interface Clarity

**Check for**:
- Unclear or sprawling public APIs
- Too many exports (sign of multiple responsibilities)
- Missing boundaries between internal/external APIs
- Tight coupling between modules

**Questions**:
- What's the public interface of this module?
- Is it obvious what should be used externally vs internally?
- Can this module be understood without reading its implementation?

### 4. Comprehension Test

**Check for**:
- Code that requires holding many concepts in your head
- Deep nesting (> 3-4 levels)
- Long functions (> 50 lines)
- Complex state management spread across the file

**Questions**:
- Can I understand this module without reading the entire codebase?
- How many concepts do I need to track simultaneously?
- Is there hidden/implicit state?

### 5. Testing Implications

**Check for**:
- Difficulty isolating code for testing
- Tests that require extensive setup/mocking
- Untestable code due to tight coupling
- Inability to test components independently

**Questions**:
- Can individual functions/classes be tested in isolation?
- Does testing require loading the entire module?
- Are dependencies injected or hardcoded?

### 6. AI Collaboration Readiness

**Check for**:
- Files too large for LLM context window
- Code that can't be reasoned about in isolation
- Missing clear boundaries for targeted changes
- Difficulty giving precise instructions like "modify only X"

**Questions**:
- Can an LLM understand this entire file at once?
- Are there clear boundaries where changes can be isolated?
- Would changing one thing require understanding everything?

---

## Output Format

For each file or component reviewed:

### File: [filename] ([line count] lines)

**Primary Issue**: [Main modularity problem]

**Severity**: Critical / High / Medium / Low
- **Critical**: > 2,000 lines or fundamentally unmaintainable
- **High**: 1,500-2,000 lines or severe responsibility mixing
- **Medium**: 1,000-1,500 lines or moderate coupling
- **Low**: < 1,000 lines but could be improved

**Current Responsibilities**:
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]

**Recommended Split**:

```
Original: large_file.py (1,800 lines)

Refactor to:
├── core.py (400 lines)
│   └── Core business logic and primary responsibility
├── data_access.py (300 lines)
│   └── Database/API interactions
├── validation.py (200 lines)
│   └── Input validation and sanitization
├── transforms.py (250 lines)
│   └── Data transformation utilities
└── types.py (100 lines)
    └── Type definitions and constants
```

**Interface Design**:
- **core.py exports**: `process()`, `calculate()`, `main_workflow()`
- **data_access.py exports**: `fetch()`, `save()`, `query()`
- Dependencies flow: UI → core → data_access

**Migration Strategy**:
1. Extract type definitions first (safest, most referenced)
2. Extract pure functions (validation, transforms) next
3. Extract data access layer
4. Refactor core to use new modules
5. Update tests incrementally

**Benefits**:
- Each file becomes < 500 lines (fully comprehensible)
- Clear separation of concerns
- Easier to test each layer independently
- LLM can reason about each module in isolation
- Targeted changes become safer

**Effort**: [Low / Medium / High]

---

## Prioritization

Prioritize files based on:
1. **Size**: Larger files first (> 1,500 lines)
2. **Change frequency**: Files that change often benefit most from modularity
3. **Bug density**: Files with frequent bugs need better boundaries
4. **Team pain**: Files developers complain about

---

## Red Flags

Watch for these warning signs:
- "God objects" or "Manager classes" that do everything
- Files named "utils," "helpers," or "common" that keep growing
- Files with hundreds of imports
- Circular dependencies
- Comments like "TODO: refactor this" that never get addressed

---

## Principles for Good Modularity

When recommending splits, ensure each new module:
- ✅ Has a single, clear responsibility
- ✅ Exposes a minimal, obvious interface
- ✅ Hides implementation details
- ✅ Can be understood without reading other modules
- ✅ Is independently testable
- ✅ Fits comfortably in LLM context (< 1,500 lines)

---

## Anti-Patterns to Avoid

Don't recommend:
- ❌ Premature abstraction (extracting code used only once)
- ❌ Over-engineering (creating frameworks for simple cases)
- ❌ Splitting purely by line count without considering responsibility
- ❌ Creating "utils" dumping grounds
- ❌ Breaking apart code that genuinely belongs together

---

## Remember

The goal is **comprehension**, not just smaller files. A well-modular codebase should:
- Be easier to understand, not harder
- Have clear boundaries that match mental models
- Make changes safer and more predictable
- Enable both humans and LLMs to reason effectively

**Modularity is not an end in itself—it's a means to maintainability and correctness.**
