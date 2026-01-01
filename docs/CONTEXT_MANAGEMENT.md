# Context Management: Working with LLMs Across Sessions

One of the biggest challenges in AI-assisted development is maintaining coherent context across long projects and multiple sessions. LLMs have no memory between conversations, and even within a conversation, context can become polluted or confused.

This document provides strategies for effective context management.

---

## The Context Problem

**Challenge**: LLMs need context to produce correct code, but:
- Context windows have limits (~100k-200k tokens)
- Context can become polluted with outdated information
- Long conversations drift from original goals
- New sessions start with zero knowledge

**Solution**: Treat context as a precious resource. Provide it intentionally and maintain it carefully.

---

## Starting a New Session

### Warm-Up Template

When starting a new LLM session on an existing project, provide this context upfront:

```
I'm working on [PROJECT_NAME], a [TYPE] that [PURPOSE].

Key context:
- Architecture: [Brief summary or link to ARCHITECTURE.md]
- Current phase: [Which roadmap phase you're in]
- Recent work: [What was done in last session]
- Today's goal: [What you're trying to accomplish]

Critical constraints:
- [Key invariants from INVARIANTS.md]
- [Technology stack]
- [Any recent architectural decisions]

Please confirm you understand the context before we begin.
```

### Essential Files to Share

**Always provide**:
- `ARCHITECTURE.md` (or relevant sections)
- `INVARIANTS.md`
- README (for setup/context)

**Provide as needed**:
- Recent checkpoint summaries
- Specific files you'll be working with
- Related test files
- Recent commit messages for context

**Don't dump everything**: Selective context is better than overwhelming the LLM.

---

## During a Session: Maintaining Context

### Context Hygiene Practices

**Do**:
- ✅ Reference back to invariants and architecture docs
- ✅ Remind the LLM of decisions made earlier in the session
- ✅ Correct misconceptions immediately
- ✅ Summarize progress periodically
- ✅ Keep conversations focused on one feature/task

**Don't**:
- ❌ Let the conversation drift to unrelated topics
- ❌ Assume the LLM remembers earlier context perfectly
- ❌ Work on multiple unrelated features in one session
- ❌ Continue when the LLM seems confused

### When to Start a Fresh Conversation

**Start fresh when**:
- The LLM is consistently misunderstanding requirements
- You've been working for 2+ hours on complex changes
- Switching to a completely different part of the codebase
- Previous suggestions were mostly wrong (context is polluted)
- You've hit the context window limit
- The conversation has >50 back-and-forth exchanges

**Before starting fresh**:
- Generate a checkpoint summary of what you accomplished
- Document any decisions made
- Commit working code
- Note any issues or blockers

### Context Checkpoints

Every 30-60 minutes, or after completing a subtask:

```
Let's pause and summarize:
- What have we accomplished so far?
- What assumptions have we made?
- What's still left to do?
- Are we still aligned with the architecture and invariants?
```

This prevents context drift and catches misalignments early.

---

## Managing Context Window Limits

### Signs You're Hitting Limits

- LLM responses become generic or vague
- It "forgets" earlier decisions
- Responses take longer to generate
- Quality degrades over time

### Strategies to Extend Effective Context

**1. Be Selective**
- Don't paste entire files if you only need a function
- Provide relevant snippets, not everything
- Link to full files instead of including them

**2. Use Summaries**
- Summarize previous work instead of re-sharing all code
- Reference "as discussed earlier" instead of repeating

**3. Progressive Disclosure**
- Start with high-level context
- Drill down into specifics only as needed
- Don't front-load everything

**4. Anchor Points**
- Keep architecture docs and invariants as "north star" references
- These should be re-readable without consuming too much context

**5. Session Splitting**
- Break large tasks into smaller sessions
- Each session focuses on one module or feature
- Use checkpoint summaries to bridge sessions

---

## Context Pollution: Prevention & Recovery

### How Context Gets Polluted

- Exploring dead-end approaches
- LLM misunderstanding a requirement and building on that
- Mixing multiple unrelated tasks
- Outdated information from early in conversation
- Conflicting instructions

### Preventing Pollution

**At the start**:
- Clear, focused goal for the session
- Explicit constraints upfront
- Reference to authoritative docs (architecture, invariants)

**During the session**:
- Correct misconceptions immediately (don't let them compound)
- Explicitly mark dead-ends: "Let's discard that approach"
- Stay focused on one task/feature

**If pollution occurs**:
- **Option 1**: Explicitly reset
  ```
  Let's reset. Ignore previous approaches we discussed.
  Here's the correct approach: [...]
  ```

- **Option 2**: Start fresh conversation
  - Summarize what worked
  - Note what didn't work (so new session avoids it)
  - Begin new session with clean context

---

## Working Across Multiple Sessions

### Session Continuity Pattern

**End of Session**:
1. Generate checkpoint summary
2. Commit working code
3. Document any blockers or open questions
4. Note what's next

**Start of Next Session**:
1. Review checkpoint summary
2. Provide warm-up context (see template above)
3. Explicitly state: "We're continuing from where we left off"
4. Share only relevant new context

### The Handoff Document

For complex work spanning many sessions, maintain a `WORKING_NOTES.md`:

```markdown
## Current Work: User Authentication Feature

### Status
- ✅ OAuth integration complete
- ✅ Token validation working
- 🚧 In progress: Session management
- ⏳ Not started: Logout flow

### Context for Next Session
- Using JWT for sessions
- Tokens expire in 1 hour
- Refresh tokens stored in Redis
- Need to implement token refresh logic next

### Decisions Made
- Chose JWT over sessions (stateless)
- Redis for refresh token storage (fast, expire support)
- 1-hour token lifetime (balance security/UX)

### Blockers
- None currently

### Files Changed
- src/auth/oauth.ts
- src/auth/token.ts
- src/middleware/auth.ts
```

This makes resuming work trivial, even days later.

---

## Multi-LLM Context Management

If using multiple LLM conversations in parallel (e.g., one for backend, one for frontend):

**Synchronization points**:
- Shared architecture document
- Shared invariants
- API contracts document
- Regular manual sync of decisions

**Dangers**:
- Conversations making conflicting assumptions
- Duplicated effort
- Integration issues at boundaries

**Best practice**: Use single LLM conversation per feature. Only parallelize for truly independent work.

---

## Emergency Context Recovery

**If you've lost the thread completely**:

1. **Stop coding**
2. Review what's been committed
3. Run tests to see what works
4. Read recent checkpoint summaries
5. Review architecture and invariants
6. Start fresh conversation with corrected understanding

Don't try to salvage a confused conversation—it usually wastes more time than restarting.

---

## Context Budgeting

Think of context as a limited resource:

**High value context** (spend freely):
- Architecture docs
- System invariants
- The specific code being modified
- Test files for that code

**Medium value context**:
- Related files
- Recent changes
- Checkpoint summaries

**Low value context** (avoid):
- Entire codebase dumps
- Unrelated code
- Verbose logs
- Exploratory dead-ends

**Budget example**:
```
~10% - Architecture & invariants
~30% - Code being modified
~20% - Tests and related code
~20% - Conversation and instructions
~20% - Buffer for LLM responses
```

---

## Red Flags: Context Is Failing

🚩 LLM suggests code that violates stated invariants

🚩 LLM "forgets" decisions from earlier in conversation

🚩 Responses become generic (not project-specific)

🚩 LLM contradicts itself

🚩 Solutions ignore existing architecture

🚩 You're constantly correcting the same misconception

**When you see these**: Consider starting fresh with better context.

---

## Best Practices Summary

1. **Start with focus**: Clear goal, essential context only
2. **Stay focused**: One feature per session when possible
3. **Checkpoint regularly**: Every 30-60 minutes
4. **Correct early**: Don't let misconceptions compound
5. **Know when to restart**: Better to start fresh than fight confusion
6. **Document for continuity**: Checkpoint summaries bridge sessions
7. **Budget context**: Provide high-value context, avoid noise
8. **Warm up new sessions**: Don't assume the LLM knows anything

---

## Remember

**Context is not just information—it's shared understanding.**

Your goal isn't to give the LLM all the information, it's to give it the *right* information to maintain coherent understanding across time.

**Good context management is the difference between productive AI collaboration and frustrating confusion.**
