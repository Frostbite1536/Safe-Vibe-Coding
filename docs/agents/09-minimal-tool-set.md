---
layout: default
title: 9. Building a Minimal Tool Set First
nav_order: 9
parent: Agents Guide
description: "The discipline of shipping with three tools instead of twenty. How every added tool expands the attack surface, testing burden, and chained-action risk — and how to decide which tools earn their place."
permalink: /agents/minimal-tool-set
---

# 9. Building a Minimal Tool Set First

Chapter 5 taught you how to design a good tool. This chapter is about having the discipline to design as few of them as possible.

"Minimal tool set first" is not just a style preference. It is the single biggest lever you have on reliability, testability, and safety in the early life of an agent. Teams that ship with three tools and add a fourth only when pain demands it end up with agents that work. Teams that ship with twenty tools "because the agent might need them" end up with agents that cannot be debugged.

---

## Why More Tools Make Agents Worse, Not Better

Every tool you add expands three things at once. The expansion is not linear — it is multiplicative — and all three directions push toward fragility.

### 1. The action space expands multiplicatively

With 3 tools, an agent's first-step action space is roughly 3 × (number of reasonable inputs). At 10 tools it is roughly 10 ×. At 20 tools it is 20 ×. Over a 5-step trajectory, those numbers become ~243 vs. ~100,000 vs. ~3,200,000 possible paths. You cannot test the third one — you can only hope.

The point is not that the model will pick randomly; it is that the *wrong* paths the model can pick grow much faster than the right paths you actually wanted it to take.

### 2. Tool overlap creates pattern-matching bugs

When two tools have overlapping descriptions, the model does not pick "the right one." It picks "the one that pattern-matches the surface form of the current request." That choice is often wrong in ways that only show up under adversarial inputs.

Consider two tools:

```text
- search_orders(query: str)
  "Searches orders by free-form query. Returns matching orders."

- find_orders_by_customer(customer_email: str)
  "Looks up all orders placed by a specific customer."
```

Both can be used to answer *"what did customer X buy?"*. The model will sometimes pick one and sometimes the other, depending on how the question is phrased. The behavior is unstable, the tests are flaky, and the bug is in *having two tools at all* — not in the prompt.

### 3. The test surface explodes

For each tool you need:

- Happy-path tests.
- Edge-case tests (empty inputs, malformed inputs, authorization failures).
- Tool-failure tests (the tool errors, times out, returns malformed data).
- Interaction tests (does the agent pick this tool correctly when the alternatives are also present?).

Three tools are ~12 test cases. Twenty tools are ~200 test cases *and* the combinatorial interaction tests between them. The second number is not what you thought you were signing up for.

---

## The Rule of Three (to Start)

Start with three tools. No more.

This is a forcing function, not a religion. The goal is to make you justify every addition against a real use case, not to write "three" on a sticker. When you start with three, you have to answer hard questions early:

- Which three capabilities are load-bearing for the core task?
- What is the agent supposed to do when it needs a capability the three tools do not provide?
- Which capabilities are nice-to-have and can be deferred?

If you cannot answer those questions, you do not yet have a design — and adding a fourth tool will not give you one.

For the Support Triage Drafter from earlier chapters, the three tools are:

```text
- fetch_order_status(order_id)          # read-only
- post_reply_to_review_queue(...)       # write, reversible
- escalate_to_human(reason, summary)    # always available
```

That is the entire agent. Notice what is *not* there:

- No `find_orders_by_customer` — if the user does not provide an order number, the agent escalates.
- No `send_email` — the human rep sends from the queue.
- No `search_knowledge_base` — the scope is order status only.
- No `classify_email` — that is a one-shot upstream filter, not a tool the agent chooses.

Every "missing" tool is a deliberate choice. The agent handles the long tail by escalating, not by growing a wider toolbox.

---

## How to Decide If a New Tool Earns Its Place

When pressure comes to add a fourth tool — and it will — walk through this checklist. A new tool should pass every point.

### 1. Is it covered by an existing tool with a small change?

Before adding, ask: *can we extend an existing tool to cover this?* Often the answer is yes, and a new parameter is cheaper and safer than a new tool. But be careful: this is how tools become overloaded `do_stuff` calls. If extending would widen a tool's side-effect category (from read-only to write, say), make a new tool instead.

### 2. Could escalation cover it instead?

If the new tool would be called rarely, and the cost of escalating to a human is small, *escalate*. A tool the agent uses once a week is not worth the ongoing maintenance cost of being on the tool list. Humans are an acceptable fallback for the long tail.

### 3. Can you describe it in 3–6 sentences?

If the description needs more than six sentences, the tool is doing too much. Split it or reject it. The LLM reads the description every call; a long description is a drag on every decision, not just the ones that use this tool.

### 4. Does it have a non-overlapping name?

If you cannot pick a name that does not pattern-match against an existing tool, you have an overlap bug before you start. Either rename one of the existing tools to be narrower, or reconsider whether both should exist.

### 5. Is it independently testable?

If the only way to test the new tool is through an end-to-end agent run, the test will be slow, flaky, and hard to interpret. Good tools are unit-testable: you can call them with inputs and assert on outputs without any agent involved.

### 6. Does it fit the side-effect budget?

Count the side-effect categories on your tool list:

- Read-only tools are cheap. Add them when needed.
- Reversible write tools are moderate cost. Justify them.
- Irreversible write tools are expensive. Every one is an incident waiting to happen; each needs its own approval flow and its own eval cases.
- Costly tools (paid APIs, long compute) need rate-limiting and cost tracking.

If adding the new tool pushes the agent's total side-effect exposure higher, the question is not just *"is this tool useful?"* but *"is the extra risk worth it?"*

### 7. Will you commit to removing it if it goes unused?

Set a review date — 30 days, 90 days — and commit up front: if the tool is called on fewer than N runs in that window, it gets deleted. A tool that is not earning its place is not a feature, it is a liability.

---

## The Escalation Tool Counts

One tool belongs on every agent's list from day one, and it is the one most teams forget:

```text
escalate_to_human(reason: str, summary: str) → {escalation_id}
```

Escalation is a first-class success state (see [Chapter 11](./11-escalation-and-hitl.md)), and that makes it a tool. Giving the agent a named way to stop and hand off is strictly better than hoping it will refuse inside the prompt.

Why it matters:

- **It replaces the long tail.** Instead of adding a 21st tool for a rare case, the agent escalates. One tool covers all rare cases cheaply.
- **It is observable.** Escalations show up as a distinct tool call in the audit log, so you can count them, categorize them, and use them to prioritize future tool additions.
- **It is a psychological unlock.** The model is more willing to decline in-scope-but-uncertain actions when "escalate" is an available action rather than an implicit refusal.

Count it as tool #3 if you want. Just do not skip it.

---

## Growing the Tool Set Safely

You will eventually need to add tools. That is fine. The discipline is about *how*.

1. **Wait for real demand.** A good signal is: the agent keeps escalating on cases that would be cheaply automated by a specific tool. The escalation log is telling you exactly what to build next.
2. **Add one tool at a time.** Do not ship a batch of five new tools in one release; you will never know which one broke what.
3. **Ship behind a feature flag.** The new tool is off for most users until you have confidence. See [Chapter 18](./18-deployment-patterns.md).
4. **Re-run the golden eval set.** Every tool addition is a behavior change, even when you did not mean it to be. See [Chapter 17](./17-evaluation-frameworks.md).
5. **Update the system prompt and scope brief *explicitly*.** A tool the scope brief does not mention is a scope violation waiting to happen.
6. **Set a removal trigger.** If the new tool does not earn its keep in the defined window, remove it.

That process sounds heavy. It is. Adding tools is supposed to be harder than deleting them.

---

## A Useful Exercise: The Tool Autopsy

Once a quarter, look at your agent's audit log and ask: *"If I started over today, would I ship every tool that is currently on this list?"*

For each tool, pull:

- Number of calls in the last 30 days.
- Number of successful calls (tool returned success-shape output).
- Number of resulting escalations (agent escalated after calling this tool).
- Number of tool-interaction bugs where this tool was one of the actors.

Any tool that does not justify its slot gets flagged for removal. Deprecate it, remove it from the schema, re-run the evals, and confirm nothing regressed. Most of the tools you remove will not be missed.

The tool autopsy is how you resist Tool Sprawl without it becoming a one-time cleanup project.

---

## Anti-Pattern: Tool Sprawl

**Symptom**: The tool list has grown to 15–30 entries. Multiple tools have overlapping purposes. Some have not been called in weeks. Several have vague descriptions that could plausibly match any request. New team members cannot tell which tool to use for a given task — and neither can the model.

**Why it hurts**: The action space is too large to test. Behavior is unstable across runs because the model picks different tools for semantically identical requests. Every regression investigation starts with *"which tool did it call this time?"*. Eval scores have a wide variance and teams stop trusting them.

**Fix**: Conduct a tool autopsy. Remove tools that have not been called in 30 days. Merge tools with overlapping descriptions into a single, narrower tool. Replace tools for rare cases with escalation. Rewrite every remaining description to be unambiguously narrower. The agent will probably get *more* reliable after the diet, not less.

---

## Checklist

- [ ] You started with no more than three core tools plus `escalate_to_human`.
- [ ] Every tool on the list was justified against a real use case, not a hypothetical one.
- [ ] No two tools have descriptions that could plausibly match the same request.
- [ ] The tool with the widest side-effect category (irreversible write) has an explicit approval flow and is independently tested.
- [ ] Every new tool addition goes through the 7-point checklist in this chapter.
- [ ] A tool autopsy is scheduled (quarterly) and has run at least once.
- [ ] Tools that have not been called in 30 days are flagged for removal.
- [ ] `escalate_to_human` is one of the tools, and its usage is logged and reviewed.

---

## What to Read Next

- [Chapter 5 — Designing the Tool Interface](./05-tool-interface-design.md): the mechanics of writing a single tool well.
- [Chapter 10 — Observability from Day One](./10-observability-from-day-one.md): the audit log is where the tool autopsy gets its data.
- [Chapter 11 — Escalation Paths & Human-in-the-Loop](./11-escalation-and-hitl.md): escalation is the alternative to adding more tools.
- [Chapter 22 — Anti-Patterns & Failure Modes](./22-anti-patterns.md): the full catalog of agent failure modes, including Tool Sprawl.
