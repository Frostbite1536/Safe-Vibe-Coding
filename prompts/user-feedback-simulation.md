---
layout: default
title: User Feedback Simulation
parent: Prompts Library
nav_order: 11
---

# User Feedback Simulation Prompt

Use this prompt to have the LLM simulate user behavior and identify UX issues.

---

## Prompt

You are now a user testing this application. Your goal is to identify usability issues, confusing flows, and potential frustrations.

**Application**: [describe the app or feature]

**User persona**: [describe who this user is - their goals, experience level, context]

**Testing scenario**: [what the user is trying to accomplish]

---

**Your task**:

1. **Walk through the user journey** step by step as if you were actually using the application.

2. **Think aloud** as you go:
   - What are you trying to do?
   - What do you expect to happen?
   - What questions do you have?
   - What's confusing or unclear?
   - What's frustrating?

3. **Flag issues** in these categories:

   **Confusion**:
   - Unclear labels or instructions
   - Ambiguous button/link text
   - Missing guidance on what to do next
   - Jargon or technical terms

   **Friction**:
   - Too many steps for a simple task
   - Redundant information requests
   - Slow loading with no feedback
   - Forced sequencing that doesn't match mental model

   **Errors**:
   - Unclear error messages
   - Error messages that don't suggest fixes
   - Validation that's too strict or unclear
   - Confusing form validation

   **Discoverability**:
   - Important features that are hidden
   - Unclear navigation
   - Missing affordances (things that don't look clickable/interactive)
   - No indication of what's possible

   **Trust & Safety**:
   - Unclear privacy implications
   - Surprising behavior
   - Irreversible actions without warning
   - Missing confirmations for destructive actions

   **Accessibility**:
   - Can't be operated by keyboard alone
   - Missing alt text or labels
   - Poor contrast or readability
   - Issues for screen reader users

4. **Prioritize findings**:
   - **Critical**: Prevents task completion
   - **High**: Causes significant frustration or confusion
   - **Medium**: Causes minor friction
   - **Low**: Polish issues

**Output format**:

For each issue:
- **Step**: [Which step in the journey]
- **Issue**: [What the problem is]
- **User thought**: [What the user is thinking/feeling]
- **Impact**: Critical/High/Medium/Low
- **Suggested fix**: [How to address it]

**Example**:

**Step**: User tries to submit form

**Issue**: Error message says "Invalid input" without specifying which field

**User thought**: "What did I do wrong? Which field is invalid? This is frustrating."

**Impact**: High

**Suggested fix**: Highlight the invalid field and show "Email must include an @ symbol" next to the email field

---

**Remember**: You're not looking for bugs in the code. You're looking for **usability issues** from a user's perspective.
