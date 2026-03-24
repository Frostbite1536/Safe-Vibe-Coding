# Building Agents: A Practical Guide Outline

*Inspired by the Safe Vibe Coding guide. Mirrors its structure but focused on building reliable, safe autonomous agents.*

---

## Core Philosophy

Agents fail not because AI is weak, but because **the boundaries around what the agent can do are unclear**.

> **Treat your agent as a contractor with a power tool**: capable and fast, but destructive without guardrails.

Your job is to provide:
- **Scope** — What the agent is allowed to do and, critically, what it is not
- **Tool contracts** — Precise definitions of every capability exposed to the agent
- **Escalation paths** — When the agent must stop and ask a human
- **Observability** — Logs and traces so you can audit every decision

---

## The Workflow

### 1. Define Purpose and Scope Before Anything Else

Before writing a single line of code, answer:
- What problem does this agent solve?
- What actions can it take in the world?
- What is **strictly out of scope** — actions it must never perform?
- Who or what does it interact with (users, APIs, databases, other agents)?

Write this as a one-page brief. The scope document becomes your agent's constitution.

**Red flag**: If you cannot describe what the agent *won't* do, you don't know enough to build it yet.

---

### 2. Design the Tool Interface Before Implementation

Tools are the agent's only interface to the world. Design them like a public API.

For each tool, define:
- **Name** — Clear, unambiguous verb-noun (`search_web`, `send_email`, `read_file`)
- **Description** — Written for an LLM consumer, not a human; be explicit about side effects
- **Input schema** — Typed, validated, with constraints
- **Output schema** — What success and failure look like
- **Side effects** — Is this destructive? Reversible? Rate-limited?
- **Authorization** — Who or what can invoke this tool?

**Principle**: Fewer tools with precise contracts beat many tools with vague descriptions.

---

### 3. Write the System Prompt as a Contract

The system prompt is the agent's operating manual. It should define:

- **Role and identity** — What kind of agent is this?
- **Invariants** — Rules that must always hold (e.g., "Never delete data without confirmation")
- **Decision boundaries** — Criteria for when to act vs. when to ask
- **Output format** — How results should be structured
- **Prohibited behaviors** — Explicit list of what the agent must never do

Treat the system prompt like `INVARIANTS.md` in vibe coding. If a behavior violates it, that's a bug — not a prompt tuning opportunity.

---

### 4. Build a Minimal Tool Set First (No Tool Sprawl)

Start with the fewest tools that make the agent useful. Add tools only when a real use case demands them.

Each tool added:
- Expands the attack surface
- Increases the chance of unintended chained actions
- Grows the complexity of testing

**Anti-pattern**: Building 20 tools at once because they "might be useful."

**Pattern**: Build 3 tools, ship, observe, then add what's actually needed.

---

### 5. Implement Observability from Day One

Before the agent runs in production, you need:

- **Full trace logging** — Every tool call, its inputs, outputs, and the reasoning that triggered it
- **Decision audit trail** — What did the agent consider before acting?
- **Latency and cost tracking** — Token usage and wall time per run
- **Error categorization** — Did the agent fail, refuse, or produce wrong output?

You cannot debug an agent you cannot observe. Logs are not optional.

---

### 6. Define Escalation Paths Explicitly

An agent that never asks for help is dangerous. Define when it must stop and hand control back:

- Ambiguous input that could be interpreted multiple ways
- Actions above a certain risk threshold (e.g., sending to >10 recipients, deleting >1 record)
- Confidence below a threshold
- Unexpected tool output (error, empty result, schema mismatch)
- Any action that is irreversible

Escalation is not failure — it is a safety feature.

---

### 7. Add Tests Before Running Against Real Systems

Test the agent against a mock/sandbox environment first. Cover:

- **Happy path** — Does it solve the core task correctly?
- **Edge cases** — Empty input, malformed data, missing fields
- **Boundary conditions** — What happens at the edge of its scope?
- **Adversarial inputs** — Prompt injection, jailbreak attempts, unexpected tool responses
- **Tool failure** — What happens when a tool errors, times out, or returns garbage?

Tests are gates. Do not connect to production APIs until they pass.

---

### 8. Harden Against Prompt Injection

Agents that process external content (emails, web pages, documents, user messages) are vulnerable to prompt injection — where malicious input tries to hijack the agent's behavior.

Mitigations:
- Treat all external content as untrusted data, not instructions
- Separate system instructions from user/external content structurally
- Validate tool outputs before acting on them
- Log and alert on anomalous instruction patterns in external content

---

### 9. Run Chaos and Adversarial Testing

Beyond standard tests, deliberately break the agent:

- Feed it contradictory instructions
- Simulate tool failures mid-task
- Inject unexpected data formats
- Test what happens when it runs out of context
- Try to make it exceed its authorized scope

The goal is not to make the agent work in ideal conditions — it's to find how it fails, then make those failures safe.

---

### 10. Maintain a Prompt Library

Keep reusable prompts for common agent development tasks:

- System prompt scaffolds for different agent types (research, coding, data, customer support)
- Evaluation prompts to assess agent output quality
- Red-teaming prompts for adversarial testing
- Debugging prompts to diagnose unexpected behavior
- Handoff prompts for multi-agent coordination

---

### 11. Document Agent Behavior, Not Just Code

Agent behavior is not always readable from code alone. Maintain:

- **Behavior spec** — What the agent does, step by step, in plain language
- **Tool registry** — All tools, their contracts, and their side effects
- **Decision log** — A record of edge cases encountered and how they were resolved
- **Known limitations** — What the agent cannot do reliably (be honest here)

Update these documents every time behavior changes. Undocumented agents become black boxes quickly.

---

### 12. Plan for Multi-Agent Coordination Early

If your agent will eventually work alongside other agents:

- Define who is the orchestrator and who are the workers
- Establish explicit handoff contracts between agents
- Avoid shared mutable state between agents unless unavoidable
- Log inter-agent communication with the same rigor as tool calls
- Test the full pipeline end-to-end, not just each agent in isolation

**Warning**: Bugs in multi-agent systems compound. A 90%-reliable agent orchestrating a 90%-reliable sub-agent gives you ~81% reliability at best.

---

### 13. Generate Checkpoint Summaries After Each Milestone

After completing major capabilities, document:

- What the agent can now do
- New tools added and their contracts
- Any invariants added or changed
- Known failure modes discovered
- What was intentionally left out

This creates an audit trail and prevents long-term capability drift.

---

## Essential Reading (Suggested Sections)

| Guide | What You'll Learn |
|:------|:------------------|
| Tool Design Principles | How to write tool schemas LLMs can use reliably |
| System Prompt Engineering | Structuring prompts as contracts, not instructions |
| Observability & Debugging | Tracing agent decisions and diagnosing failures |
| Safety & Guardrails | Escalation paths, scope limits, and kill switches |
| Prompt Injection Defense | Hardening agents against malicious external content |
| Testing Strategies | Unit, integration, and adversarial testing for agents |
| Multi-Agent Coordination | Orchestration patterns and inter-agent contracts |
| Anti-Patterns & Failure Modes | Common mistakes and how to avoid them |

---

## Anti-Patterns

### Tool Sprawl
**Symptom**: Dozens of tools with overlapping or vague purposes.
**Fix**: Audit the tool set. Merge overlapping tools. Delete tools not used in the last 10 runs.

### The God Prompt
**Symptom**: A 5,000-word system prompt trying to handle every edge case.
**Fix**: Move edge case handling into tool logic and structured escalation. Keep the system prompt focused on role, invariants, and boundaries.

### Over-Autonomy
**Symptom**: The agent takes irreversible actions without any human checkpoint.
**Fix**: Add confirmation gates for high-impact or irreversible actions. Trust is earned incrementally.

### Silent Failure
**Symptom**: The agent returns a plausible-sounding response even when it couldn't complete the task.
**Fix**: Require explicit success/failure signals. Treat vague or hedged outputs as failures until proven otherwise.

### Testing in Production
**Symptom**: The agent is first run against real systems with real consequences.
**Fix**: Build a sandbox environment. Mock all external tools. Graduate to production only after passing adversarial tests.

### Undocumented Scope Creep
**Symptom**: The agent starts doing things it was never explicitly designed to do.
**Fix**: Reassert scope in the system prompt. Audit recent tool call logs. Add explicit prohibitions.

---

## Quick Reference Checklist

### Before Building
- [ ] One-page purpose and scope brief written
- [ ] Out-of-scope actions explicitly listed
- [ ] Tool interface designed (not yet implemented)
- [ ] System prompt drafted as a contract
- [ ] Escalation criteria defined

### During Development
- [ ] Tools have typed input/output schemas
- [ ] Tool descriptions written for an LLM consumer
- [ ] Observability (trace logging) wired up
- [ ] Sandbox/mock environment ready for testing
- [ ] Tests written before connecting to real systems

### Before Production
- [ ] Happy path, edge case, and adversarial tests passing
- [ ] Prompt injection scenarios tested
- [ ] Behavior spec and tool registry documented
- [ ] Known limitations documented honestly
- [ ] Escalation paths manually verified

### Ongoing
- [ ] Audit logs reviewed regularly
- [ ] Tool call patterns analyzed for drift
- [ ] Capability checkpoints recorded after milestones
- [ ] Documentation updated when behavior changes

---

## Why This Structure Works

Agents feel magical but fail for mundane reasons: vague scope, untested tool contracts, no way to observe what happened, no path to ask for help.

The workflow above forces those decisions to be made **before** the agent runs — not discovered painfully in production.

The result: **autonomous agents that stay within their lane.**

---

*This outline mirrors the Safe Vibe Coding guide's approach: replace trust in the model with systems that enforce correctness. For agents, correctness means staying in scope, using tools safely, and failing loudly when uncertain.*
