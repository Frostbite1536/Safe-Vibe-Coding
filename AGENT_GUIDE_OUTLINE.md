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

## The Full Guide: 26 Topics in 6 Parts

The long-form version of this outline lives in [`docs/agents/`](docs/agents/). Each numbered item below is a chapter in that directory. The sections after the table of contents (Anti-Patterns, Quick Reference Checklist) are the condensed distillation that belongs at the end of the guide.

### Part I — Foundations

1. **What Is an Agent?** — Draws the line between a chatbot, a scripted workflow, and a true autonomous agent. Explains why the distinction matters for design and safety.

2. **Core Philosophy & Mental Model** — The "contractor with a power tool" analogy, the four pillars (Scope, Tool Contracts, Escalation, Observability), and why boundaries beat cleverness.

3. **When to Build an Agent (and When Not To)** — Decision framework for choosing an agent over a deterministic pipeline, a simple LLM call, or a human-in-the-loop tool. Cost, reliability, and risk trade-offs.

### Part II — Design Before You Build

4. **Defining Purpose & Scope** — How to write the one-page scope brief. What the agent will do, what it will never do, who it interacts with, and why "I can't describe what it won't do" is a red flag to stop building.

5. **Designing the Tool Interface** — Treating tools as a public API. Naming, descriptions written for LLM consumers, typed input/output schemas, declared side effects, and authorization. Why fewer precise tools beat many vague ones.

6. **System Prompts as Contracts** — Structuring the system prompt as a contract: role, invariants, decision boundaries, output format, and prohibited behaviors. How to avoid the "God Prompt" anti-pattern.

7. **Model Selection for Agents** — Picking the right model for the job: reasoning-heavy orchestrators vs. cheap fast workers, cost-per-run math, and when to mix models within a single agent.

8. **Memory & State Management** — Conversation history, scratchpads, vector stores, and long-running state. How state becomes a source of bugs and how to bound it.

### Part III — Build It Safely

9. **Building a Minimal Tool Set First** — The discipline of shipping with three tools instead of twenty. How every added tool expands attack surface, testing burden, and chained-action risk.

10. **Observability from Day One** — Trace logging, decision audit trails, cost and latency tracking, and error categorization. Why logs are not optional and what to record for every tool call.

11. **Escalation Paths & Human-in-the-Loop** — When the agent must stop and hand control back: ambiguous input, low confidence, irreversible actions, unexpected tool output. Escalation as a safety feature, not a failure.

12. **Authorization, Sandboxing & Isolation** — User-level vs. agent-level permissions, network egress controls, filesystem scoping, container isolation, and the principle of least privilege applied to agents.

13. **Cost, Rate-Limiting & Latency Budgets** — Per-run token budgets, runaway-loop detection, circuit breakers, and kill switches. How to stop an agent that has lost the plot before it burns through your API quota.

### Part IV — Test & Harden

14. **Testing Strategies** — Happy path, edge cases, boundary conditions, tool-failure tests. Building a sandbox/mock environment. Why you must not connect to production APIs until the test suite passes.

15. **Hardening Against Prompt Injection** — Treating all external content as untrusted data, separating system instructions from user content structurally, validating tool outputs before acting, and alerting on anomalous instruction patterns.

16. **Chaos & Adversarial Testing** — Deliberately breaking the agent: contradictory instructions, simulated tool failures, context exhaustion, and scope-escape attempts. Finding failure modes before production does.

17. **Evaluation Frameworks** — Golden datasets, LLM-as-judge scoring, regression suites, and the difference between "it passed my tests" and "it's actually reliable."

### Part V — Ship & Operate

18. **Deployment Patterns** — Staged rollouts, shadow mode, canary agents, and feature-flagging new tools. How to graduate an agent from sandbox to production without a cliff.

19. **Monitoring & Incident Response** — What to alert on in production, how to triage a misbehaving agent, and the kill-switch playbook. Lessons from real-world agent incidents.

20. **Multi-Agent Coordination** — Orchestrator vs. worker patterns, handoff contracts, avoiding shared mutable state, and why 90% × 90% = 81% reliability compounds badly in pipelines.

21. **Checkpoint Summaries & Capability Drift** — Documenting what the agent can (and cannot) do after each milestone. How to detect and correct drift before it becomes scope creep.

### Part VI — Reference Material

22. **Anti-Patterns & Failure Modes** — The full catalog: Tool Sprawl, The God Prompt, Over-Autonomy, Silent Failure, Testing in Production, Undocumented Scope Creep — with symptoms and fixes.

23. **Prompt Library for Agent Development** — Reusable prompts: system-prompt scaffolds per agent type, evaluation prompts, red-teaming prompts, debugging prompts, and inter-agent handoff templates.

24. **Documenting Agent Behavior** — Behavior specs, tool registries, decision logs, and honest "known limitations" sections. Keeping docs in sync as behavior evolves.

25. **Quick-Reference Checklists** — Before building, during development, before production, and ongoing.

26. **Further Reading & Tooling** — Curated external resources: papers, frameworks, eval harnesses, and community write-ups.

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

### Context Rot
**Symptom**: The agent's behavior degrades mid-run as its context window fills with irrelevant tool output and prior reasoning.
**Fix**: Bound memory explicitly. Summarize and compact. Reset on milestone completion.

### Model Mismatch
**Symptom**: A cheap model is used for reasoning-heavy orchestration (bad decisions) or a frontier model is used for trivial routing (cost blowout).
**Fix**: Match model capability to the task. Consider a mixed-model pipeline.

### Kill-Switch Absent
**Symptom**: No way to halt a running agent short of killing the process and hoping.
**Fix**: Design graceful-stop and hard-stop mechanisms before the agent sees production.

---

## Quick Reference Checklist

### Before Building
- [ ] One-page purpose and scope brief written
- [ ] Out-of-scope actions explicitly listed
- [ ] Tool interface designed (not yet implemented)
- [ ] System prompt drafted as a contract
- [ ] Escalation criteria defined
- [ ] Model selected with cost-per-run estimate
- [ ] Memory/state strategy chosen

### During Development
- [ ] Tools have typed input/output schemas
- [ ] Tool descriptions written for an LLM consumer
- [ ] Observability (trace logging) wired up
- [ ] Sandbox/mock environment ready for testing
- [ ] Tests written before connecting to real systems
- [ ] Authorization and sandboxing enforced at the infrastructure layer
- [ ] Cost and latency budgets enforced in code (not just in prompts)

### Before Production
- [ ] Happy path, edge case, and adversarial tests passing
- [ ] Prompt injection scenarios tested
- [ ] Behavior spec and tool registry documented
- [ ] Known limitations documented honestly
- [ ] Escalation paths manually verified
- [ ] Kill switch tested under load
- [ ] Golden eval set established with baseline scores

### Ongoing
- [ ] Audit logs reviewed regularly
- [ ] Tool call patterns analyzed for drift
- [ ] Capability checkpoints recorded after milestones
- [ ] Documentation updated when behavior changes
- [ ] Eval regression suite run on every material change
- [ ] Incident post-mortems fed back into the scope brief

---

## Why This Structure Works

Agents feel magical but fail for mundane reasons: vague scope, untested tool contracts, no way to observe what happened, no path to ask for help.

The workflow above forces those decisions to be made **before** the agent runs — not discovered painfully in production.

The result: **autonomous agents that stay within their lane.**

---

*This outline mirrors the Safe Vibe Coding guide's approach: replace trust in the model with systems that enforce correctness. For agents, correctness means staying in scope, using tools safely, and failing loudly when uncertain.*
