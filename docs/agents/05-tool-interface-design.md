---
layout: default
title: 5. Designing the Tool Interface
nav_order: 5
parent: Agents Guide
grand_parent: Guides
description: "Treat tools as a public API. How to write names, descriptions, schemas, and side-effect declarations that an LLM can actually use correctly — and why fewer precise tools beat many vague ones."
permalink: /agents/tool-interface-design
---

# 5. Designing the Tool Interface

Tools are the only way your agent affects the world. That makes the tool layer the only place where safety can be enforced in code rather than begged for in prose. Everything else in this guide — the system prompt, the eval suite, the observability stack — exists to support the tool layer or to compensate for its gaps.

Design tools like a public API that will be used by an unfamiliar developer who will not read the docs twice. Because that is exactly what your LLM is.

---

## Tools Are an API for an LLM Consumer

The audience for a tool definition is not a human. It is a language model that will read the tool's name, description, and schema, and then — without being able to ask clarifying questions — decide when and how to call it.

That audience has three properties you have to design around:

1. **It takes names and descriptions literally.** If the tool is called `get_user`, the model will call it to "get a user," whatever the model interprets that to mean in context.
2. **It pattern-matches aggressively.** If two tools have overlapping descriptions, the model will call the one that matches the surface form of the request, not the one you meant.
3. **It cannot see your implementation.** The tool's name, description, input schema, output schema, and error messages are *all it knows*. If a constraint is enforced but not documented, the model will violate it repeatedly and you will not understand why.

Everything that follows is a consequence of those three properties.

---

## The Six Things Every Tool Definition Needs

For every tool, write down all six. If any are missing, the tool is not finished.

### 1. Name — unambiguous verb-noun

Tool names should be short, active, and specific. A good name tells the model *exactly one thing* it can do.

| Bad                  | Why                                         | Better                        |
|:---------------------|:--------------------------------------------|:------------------------------|
| `do_order`           | Verb missing; what is "doing" an order?     | `lookup_order_by_id`          |
| `handle_email`       | "Handle" is infinite                        | `classify_email_topic`        |
| `process`            | Nothing                                     | `generate_reply_draft`        |
| `get_data`           | Which data?                                 | `fetch_order_status`          |
| `user_tool`          | Noun-only, no verb                          | `create_user_account`         |

Naming rules of thumb:

- Start with a verb. Read, look up, create, update, delete, send, classify, search, summarize, validate.
- End with the specific noun. Not "the thing" — the actual entity.
- If two tools would have the same name with different "modes," split them into two tools. `send_email_internal` and `send_email_external` are clearer than `send_email(recipient_type=…)`.

### 2. Description — written for an LLM consumer

The description is the model's only instruction manual. It should answer four questions in 3–6 sentences:

- **What does this tool do?** One sentence.
- **When should the model call it?** The triggering condition.
- **What are its side effects?** *Explicitly* — "writes to the database," "sends an email," "costs money."
- **When should the model *not* call it?** Cases where the model should pick a different tool or escalate.

Good description:

> `fetch_order_status` — Looks up the current status of an order by its order number. Call this when the user provides an order number and asks about status, shipping, or delivery. Read-only; no side effects. Returns `null` if no order is found — do not retry; escalate instead. Do not use this tool to look up orders by customer email; use `find_orders_by_customer` for that.

Bad description:

> `fetch_order_status` — Gets order information from the database.

The bad version tells the model *what* the function does and nothing about *when* to call it, *when not to*, or *what its side effects are*. Expect it to be called in situations you never anticipated.

### 3. Input schema — typed, validated, constrained

Every parameter needs a type, a description, and — wherever possible — a constraint. JSON Schema is the common vocabulary:

```json
{
  "name": "fetch_order_status",
  "input_schema": {
    "type": "object",
    "properties": {
      "order_id": {
        "type": "string",
        "pattern": "^ORD-[0-9]{8}$",
        "description": "The order number in the format ORD-12345678."
      }
    },
    "required": ["order_id"],
    "additionalProperties": false
  }
}
```

Three design points:

- **Every field has a description.** The model reads the field description before deciding what value to put there. Write them like a brief comment to a junior developer.
- **Constraints are enforced, not requested.** The `pattern` regex is the contract. If the model passes a malformed ID, the tool layer rejects the call before it reaches your code. The model then sees the error and can correct itself.
- **`additionalProperties: false` is mandatory.** Models will invent fields. Reject them at the boundary.

### 4. Output schema — success *and* failure shapes

Models adapt to whatever you return. If you return unstructured strings, you will get unstructured behavior. Return structured data and declare its shape.

```json
{
  "success_shape": {
    "order_id": "string",
    "status": "string (one of: pending | shipped | delivered | cancelled)",
    "estimated_delivery": "string (ISO 8601 date) | null",
    "tracking_url": "string | null"
  },
  "not_found_shape": {
    "error": "order_not_found",
    "order_id": "string",
    "message": "string"
  },
  "error_shape": {
    "error": "string",
    "retryable": "boolean",
    "message": "string"
  }
}
```

Two rules here:

- **Name your failure shapes.** Never return a bare error string. `order_not_found` is a semantic signal the model can reason about; `"Error: not found"` is a natural-language string the model will sometimes misread.
- **Tell the model if an error is retryable.** Agents loop. Without a `retryable` flag you will get infinite retry loops on permanent failures, or immediate give-up on transient ones. Either is bad.

### 5. Side effects — declared in English, enforced in code

Every tool must declare its side effects explicitly — and the declaration must appear in the description, not buried in a wiki page. Common categories:

- **Read-only.** No state changes. Safe to retry.
- **Write (reversible).** Creates a draft, a queue entry, a reversible record. Retryable with care.
- **Write (irreversible).** Sends an email, moves money, deletes data, publishes content. Must require explicit confirmation from the escalation path.
- **Costly.** Uses a paid API, rate-limited resource, or long-running compute. Must be rate-limited by the tool layer.
- **Cross-user.** Touches data belonging to other users. Must enforce authorization inside the tool.

A good tool description names its category out loud: *"Read-only."* *"Irreversible — sends a live email."* *"Write (reversible) — creates a draft that a human must approve before it is sent."*

### 6. Authorization — who can invoke it and under what conditions

Authorization is enforced inside the tool, not in the prompt. The tool layer answers two questions on every call:

- **Is the caller permitted to use this tool at all?** (Agent-level permissions.)
- **Is the caller permitted to operate on the specific data this call touches?** (Row-level permissions.)

If the prompt says *"only look up orders belonging to the requesting customer"* but the tool itself does not check the ownership, the model will eventually violate the rule. Enforce it in code and document it in the description: *"Returns 403 if the order's customer email does not match the current session's customer email."*

This is covered in depth in [Chapter 12 — Authorization, Sandboxing & Isolation](./12-authorization-and-sandboxing.md).

---

## Fewer, Precise Tools Beat Many, Vague Tools

Every tool you add expands three things: the action space the agent can explore, the test surface you are responsible for, and the odds that two tools will overlap in a way the model will exploit.

The default should be *three tools and a reason*. You can always add a fourth when a real use case demands it. You cannot easily remove a tool once the agent has learned to lean on it.

A useful exercise: for each tool you are considering, ask *"what would the agent do without this?"* If the honest answer is *"use one of the other tools a little less efficiently,"* the new tool is not pulling its weight. Delete it.

---

## A Concrete Example: Good vs. Bad Tool Sets

Imagine an agent that answers customer questions about orders. Here is a bad tool set:

```text
- query_database(query: string) → string
- send_reply(text: string) → boolean
- lookup(entity: string, id: string) → object
```

It has three tools, so it looks minimal. But:

- `query_database` lets the model write arbitrary SQL. Injection, data exfiltration, and irreversible writes are all one call away.
- `send_reply` has no approval step, no rate limit, no recipient constraint, and no side-effect declaration.
- `lookup` is a catch-all whose behavior depends on a free-form `entity` string. The model will invent entities you never coded for.

Here is the same capability set, redesigned:

```text
- fetch_order_status(order_id: str matching ^ORD-[0-9]{8}$)
    → {status, eta, tracking_url} | {error: "order_not_found"}
    Read-only.

- find_orders_by_customer(customer_email: str, limit: int ≤ 5)
    → [{order_id, status, placed_at}, …]
    Read-only. Returns at most 5 orders, most recent first.
    Only visible orders from the last 90 days.

- post_reply_to_review_queue(order_id: str, draft_text: str, reason: str)
    → {queue_id}
    Write (reversible). Adds a draft to the review queue.
    Does NOT send to the customer. A human rep sends.
```

Each tool is narrow, has explicit input constraints, has named success and failure shapes, and states its side-effect category. The action space is a tiny fraction of what the first set allowed, and every unsafe action the bad set permitted is now impossible.

---

## Tools Should Refuse, Not Ask

When a tool is called incorrectly, the tool should refuse the call with a structured error and an actionable message — not do the wrong thing, and not return a vague failure that the model will interpret creatively.

Good refusal:

```json
{
  "error": "order_not_owned_by_customer",
  "retryable": false,
  "message": "The requested order belongs to a different customer than the current session. Escalate to a human rep."
}
```

Bad refusal:

```json
{
  "error": "failed"
}
```

The good refusal tells the model *why* it failed, *whether to retry*, and *what to do instead*. The bad one will produce a retry loop and then a silent failure.

The principle: **tool errors are a communication channel**. Use them to teach the model, run after run, what the tool will and will not do.

---

## Anti-Pattern: The `do_stuff` Tool

**Symptom**: A single tool — often called something like `run_action`, `execute`, or `handle_request` — takes a free-form string and dispatches to an unbounded set of behaviors inside the tool layer.

**Why it hurts**: You have collapsed the entire tool interface into one call with one parameter. The model now has zero structural guidance and every action looks the same to your observability stack. You cannot test it, you cannot authorize it, and you cannot write a useful description for it.

**Fix**: Enumerate the real actions. Replace the catch-all with 3–6 specific tools that each have a name, a schema, and a declared side-effect category. If that produces more than ~10 tools, your agent is trying to do too much — split it into multiple agents with narrower scopes.

---

## Checklist

- [ ] Every tool has a verb-noun name that describes exactly one action.
- [ ] Every tool description answers: *what*, *when to call*, *side effects*, *when not to call*.
- [ ] Every input schema has typed fields, descriptions on every field, constraints where possible, and `additionalProperties: false`.
- [ ] Every tool returns structured success *and* structured failure shapes, with named error codes and a `retryable` signal where applicable.
- [ ] Every tool declares its side-effect category (read-only, reversible write, irreversible write, costly, cross-user).
- [ ] Authorization is enforced inside the tool, not in the prompt.
- [ ] The tool set is as small as it can be while still covering the scope brief. Each tool justifies its own existence.
- [ ] Error messages are structured and actionable — written to teach the model.

---

## What to Read Next

- [Chapter 4 — Defining Purpose & Scope](./04-defining-purpose-and-scope.md): tools should implement the inclusions and enforce the exclusions from the brief.
- [Chapter 6 — System Prompts as Contracts](./06-system-prompts-as-contracts.md): the prompt should *describe* the tools, not duplicate their rules.
- [Chapter 9 — Building a Minimal Tool Set First](./09-minimal-tool-set.md): the discipline of shipping with three tools instead of twenty.
- [Chapter 12 — Authorization, Sandboxing & Isolation](./12-authorization-and-sandboxing.md): the infrastructure layer under your tool contracts.
