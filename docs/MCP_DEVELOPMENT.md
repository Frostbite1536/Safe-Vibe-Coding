---
layout: default
title: Building MCP Servers
nav_order: 8
parent: Guides
description: "Comprehensive guide to building MCP servers — what they are, why they matter, and hard-won lessons for avoiding the bugs that plague every first implementation."
permalink: /mcp-development
---

# Building MCP Servers: A Practitioner's Guide

MCP (Model Context Protocol) servers let LLMs interact with external systems — databases, APIs, file systems, third-party services — through a standardized tool-calling interface. Instead of the LLM generating code that *you* run, the LLM calls tools that *your server* executes. This turns an LLM from a text generator into an agent that can take real actions.

If you are building software that an LLM will operate through tool calls, you are building an MCP server. This guide covers what you need to know — and what will go wrong if you don't.

---

## Table of Contents

1. [What Is an MCP Server?](#what-is-an-mcp-server)
2. [Why Build One?](#why-build-one)
3. [The Core Mental Model](#the-core-mental-model)
4. [Guidelines for AI Coding Agents](#guidelines-for-ai-coding-agents)
5. [Common Bug Categories](#common-bug-categories)
6. [MCP Server Checklist](#mcp-server-checklist)
7. [Write an LLM-Specific Input Test Suite](#write-an-llm-specific-input-test-suite)

---

## What Is an MCP Server?

An MCP server exposes **tools** — functions with typed input schemas and structured output — over a transport layer (typically stdio or HTTP). An LLM client connects to the server, reads the list of available tools and their descriptions, and calls them by sending JSON parameters. The server executes the tool and returns a structured response.

```text
┌──────────────┐       JSON-RPC        ┌──────────────┐
│   LLM Client │ ◄──────────────────► │  MCP Server   │
│  (e.g. Claude│    stdio / HTTP       │  (your code)  │
│   Code)      │                       │               │
└──────────────┘                       └───────┬───────┘
                                               │
                                       ┌───────▼───────┐
                                       │  Your APIs,   │
                                       │  Database,    │
                                       │  Services     │
                                       └───────────────┘
```

The LLM never sees your source code. It sees **only**:
- Tool names and descriptions
- Parameter schemas
- Response payloads
- Error messages

Everything the LLM knows about how to use your server comes from these four things.

---

## Why Build One?

MCP servers let you give an LLM **controlled access** to real systems. Common use cases:

- **Database queries**: Let the LLM explore and modify data without writing raw SQL.
- **API integrations**: Connect to Slack, GitHub, Jira, or internal services.
- **Domain-specific operations**: Animation engines, analytics pipelines, CRM systems.
- **File and infrastructure management**: Controlled access to filesystems, deployments, cloud resources.

The alternative — having the LLM generate scripts you run manually — is slower, less safe, and harder to constrain. MCP servers give you a boundary where you control exactly what the LLM can and cannot do.

---

## The Core Mental Model

> **Your consumer is an LLM, not a human.**

This single idea explains most of the bugs in first-time MCP server implementations. A human developer can read source code, try different parameter names, inspect stack traces, and intuit what went wrong. An LLM cannot. It will:

- Use exactly the parameter names from your description (and hallucinate plausible alternatives if the description is unclear).
- Trust default values silently rather than questioning them.
- Retry with the same wrong approach if the error message doesn't contain enough information to correct course.
- Never discover undocumented parameters or features.

**Treat every tool description as the complete, authoritative API documentation. If it isn't in the description, it doesn't exist to the LLM.**

---

## Guidelines for AI Coding Agents

The following guidelines are written for the LLM coding agent that is building the MCP server. These are the patterns and pitfalls that surfaced across multiple real-world MCP server implementations.

### 1. Design Internal APIs for MCP From Day One

Many MCP bugs originate in internal APIs that were never designed to be called by generated glue code. Design internal functions to be MCP-friendly from the start:

- **Use descriptive parameter names:** `csv_path` not `p`, `max_results` not `n`. The more obvious the names, the less room for the LLM to guess wrong.
- **Keep function signatures stable:** Every renamed parameter is a potential MCP handler bug.
- **Return simple, serializable types:** Prefer basic dictionaries or plain objects over complex nested structures with custom types.
- **Use consistent naming conventions** across similar functions. If one function uses `frequency`, don't use `freq` on a related function.
- **Avoid stdout for status output.** Use logging frameworks or stderr. This makes your code safe to use in stdio transport contexts from the start.

### 2. Tool Descriptions Are Your API Contract

Tool descriptions are not comments or nice-to-haves. They are the **only documentation** the consuming LLM will ever read. Every tool description must include:

- **What the tool does** in one clear sentence.
- **Every parameter** with its type, purpose, and valid values.
- **Return type semantics**: Does this tool create something, return a reference, return data, or produce a side effect?
- **Naming conventions**: If outputs follow a pattern (e.g., `{name}_{outputKey}`), document it explicitly.
- **Examples** for non-obvious parameter combinations.

*Common failures:*
- Parameters that exist in code but aren't listed in the description — the LLM will never use them.
- Inconsistent naming across similar tools (`freq` on one tool, `frequency` on another).
- Descriptions that say "see docs" — the LLM cannot see external docs mid-conversation.
- Missing return type information — the LLM won't know whether it got back a reference, an ID, a URL, or a data object.

### 3. Parameter Names Must Match Natural Expectations

If your description says `base` and `exponent`, your schema must accept `base` and `exponent` — not `a` and `b`. An LLM will pass what the description suggests. If the underlying API uses terse names, build your MCP schema to accept the descriptive forms and map them internally.

### 4. Validate at the Boundary (MCP Handlers Are the System Edge)

MCP tool handlers sit at the trust boundary between an LLM (which generates unpredictable JSON) and your internal systems (which expect precise types). Every handler should be as defensive as a public API endpoint:

- **Validate enum values:** LLMs may send display-friendly strings (`"Meeting Scheduled"`) instead of database values (`"Meeting_Scheduled"`). Accept both forms where practical, and normalize them before passing them downstream.
- **Guard against non-finite numbers:** `NaN` and `Infinity` won't crash your handler but will produce wrong results downstream (elements positioned off-canvas, silent calculation errors, comparisons that always return false).
- **Validate references/IDs exist:** Return the list of valid values in the error response if they don't.
- **Don't trust dynamic type casting:** In TypeScript, `as string` bypasses the type system. In Python, assuming `kwargs` are the correct type is dangerous. Validate the data *before* you cast it or pass it.

### 5. Error Messages Must Enable Self-Recovery

An LLM cannot re-read documentation when something goes wrong. Error responses must contain everything needed to retry correctly:

**Bad:**
```json
{ "error": "Unknown node type: \"foo\". See tool description for available types." }
```

**Good:**
```json
{
  "error": "Unknown node type: \"foo\".",
  "validTypes": ["sine", "add", "multiply", "compare"],
  "hint": "Use one of the validTypes values as the 'type' parameter."
}
```

Every error that says "see the docs" wastes a round-trip and burns the context window.

### 6. Wrap Every Handler in a Safe Error Boundary

A single unhandled exception in an MCP server can crash the entire process or corrupt the transport stream. Wrap every tool handler with a decorator or try/catch block that:

- Catches all exceptions.
- Returns a structured error response instead of crashing.
- Logs the full error internally for debugging.
- Never leaks raw stack traces to the LLM (they waste context and expose internals).

This pattern (e.g., a `@safe_tool` decorator or `tryCatch` wrapper) was consistently the **single highest-value addition** across multiple MCP server implementations. It turns fatal crashes into recoverable error responses.

### 7. Never Print to stdout in stdio Transport

In stdio MCP transport, **stdout IS the JSON-RPC channel**. Any `print()`, `console.log()`, or debug output that writes to stdout will corrupt the message framing and instantly break the connection.

- Audit every print/log call in the execution path.
- Redirect all debug output to stderr or a dedicated log file.

### 8. Verify Every Attribute Name Against the Actual Source

The most common category of MCP server bugs is **hallucinated attribute names**. LLMs confidently invent field names that "sound right."

| What the code says | What actually exists |
|---------------------|---------------------|
| `report.amplifier_profiles` | `report.top_amplifiers` |
| `stats.total` | `stats.count` |
| `result.data` | `result` (the object itself) |

When generating MCP handler code, cross-reference every field access against the real type definition (database column, interface, or dataclass). Do not guess. **This applies to the agent building the server, not just the LLM consuming it.**

### 9. Handle Return Types Correctly

Don't mix up dictionaries and objects. If an internal function returns a class instance, don't write handler code that checks for it like a dictionary (e.g., `result['data']`). Always check the actual return type of the internal function you are calling.

### 10. Serialize Carefully

MCP responses are JSON. Your internal data types are not.

- Date/Time objects need explicit string formatting.
- Database ORM objects often need a `.to_dict()` or `.toJSON()` method called on them.
- Language-specific types (sets, tuples, decimals, bytes) need explicit conversion.
- Build a serialization layer that handles every type that can appear in your response objects. Test it with real data.

### 11. Document Deduplication and Name-Mangling Behavior

If your server modifies input values (e.g., appending `_1`, `_2` to avoid name collisions), document this in the tool description and make the response clearly highlight when a name was changed. The LLM will reference the name it sent, not the name your server actually used.

### 12. Use Transactions for Multi-Step Operations

If a tool handler performs multiple database operations (e.g., update a record and create an audit log entry), wrap them in a transaction. MCP servers are long-lived processes where a broken pipe or timeout between operations will leave data in a corrupted state.

### 13. Rate Limit Before Expensive Work

Check rate limits, permissions, and preconditions **before** performing database queries or API calls. In an MCP context, an LLM might loop and call tools in rapid succession, which can quickly exhaust resources.

---

## Common Bug Categories

Ranked by how insidious they are (hardest to catch first):

1. **Silent Wrong Results (Most Dangerous):** Iterating dict keys instead of values, missing parameters falling back to unintended defaults, `NaN` or `Infinity` in numeric fields, or type coercion that silently converts to the wrong type. Produces output with no error, but the output is wrong.

2. **Hallucinated Names (Most Common):** Plausible attribute or parameter names that don't exist on the actual object or function. The code looks correct at a glance but crashes at runtime.

3. **Transport Corruption:** `print()` or `console.log()` calls that corrupt the stdio JSON-RPC channel. Works in unit tests; breaks instantly in production.

4. **Serialization Failures:** Internal language types (Sets, Dates, Tuples) that crash `JSON.stringify()` or `json.dumps()` at runtime.

5. **Type Boundary Mismatches:** Database ORMs expect their own enum types, not raw strings. A function returns a class instance, the handler treats it as a dictionary. Type casts hide the mismatch until runtime.

---

## MCP Server Checklist

Use this checklist when building or reviewing an MCP server.

### Tool Descriptions & Schema
- [ ] Every parameter is listed with type, purpose, and valid values.
- [ ] Return type semantics are documented (creates, returns ref, returns data, side effect).
- [ ] Parameter names in schema exactly match what the description leads the consumer to expect.
- [ ] Naming conventions for composite outputs are documented.
- [ ] Consistent naming across similar tools (don't mix `freq` and `frequency`).
- [ ] No description says "see docs" — all info is inline.

### Input Validation & Error Handling
- [ ] Enum values are validated and normalized before use.
- [ ] Both display-friendly and internal forms are accepted where practical.
- [ ] Numeric inputs are checked for `NaN`/`Infinity`.
- [ ] Missing/required parameters are validated before execution.
- [ ] References and IDs are verified to exist.
- [ ] Types are validated at runtime, not just through type casts.
- [ ] Every handler is wrapped in a safe error boundary (decorator/try-catch).
- [ ] Error responses include valid options and hints for self-recovery.
- [ ] Stack traces are logged internally, not returned to the LLM.

### Execution & Transport Safety
- [ ] No `print()`/`console.log()` calls write to stdout in the execution path. All debug output goes to stderr.
- [ ] All response types are safely JSON-serializable (Dates, ORM models handled).
- [ ] Every attribute access in the handler is verified against the actual target type definition.
- [ ] Multi-step database operations use transactions.
- [ ] Rate limits and preconditions are checked before expensive work.

### Integration Testing
- [ ] Each tool is tested with realistic LLM-style inputs (not just ideal inputs).
- [ ] Tools are tested with wrong parameter names to verify error messages.
- [ ] Tools are tested with edge-case values (`null`, empty strings, boundary numbers).
- [ ] The full stdio transport path is tested end-to-end (not just handler functions).
- [ ] An LLM-specific input test suite exists (see below).

---

## Write an LLM-Specific Input Test Suite

LLMs don't send the same inputs humans do. They send lowercase enums (`"buy"` instead of `"Buy"`), arbitrary strings for sort orders, and often pad strings with extra whitespace. This is a distinct concern from normal unit tests and deserves its own test file.

Create a test suite that specifically tests the weird things LLMs actually send:

```text
// Example LLM Input Test Cases

Test: Lowercase or improperly cased enum values
Input: action="buy"
Expected: Should accept and normalize to "Buy", not reject.

Test: Non-finite numeric inputs
Input: threshold=NaN or threshold=Infinity
Expected: Should reject with clear error, not silently produce wrong results.
Why: NaN comparisons always return false — a filter with NaN silently returns
     all results (or no results). No error, no warning, just wrong data.

Test: Arbitrary/hallucinated sort strings
Input: sort_by="most_recent" (when only "date_asc" or "date_desc" are valid)
Expected: Should return a helpful JSON error listing valid sort options, not crash.

Test: Extra whitespace in strings
Input: slug="  my-project-name  "
Expected: Should trim and process, not fail validation.

Test: Stringified bad data types
Input: threshold="NaN" or threshold="null" (as strings, bypassing JSON schema checks)
Expected: Should catch during boundary validation and return a clear formatting error.
```

---

## The Meta-Lesson

MCP servers look like simple glue code — thin wrappers connecting a protocol to internal APIs. But glue code at a trust boundary (LLM on one side, database/API on the other) has a different error profile than typical application code. The bugs aren't usually in your business logic. They're in the seams: wrong names, wrong types, wrong serialization, and transport assumptions.

Real-world audits consistently show **25-30% defect rates** in first-pass MCP implementations. The defects are not complex — they are small, obvious-in-hindsight mismatches that compound because there are so many integration points and no type system spans the full boundary.

The fix is not cleverness. It is discipline:
- Validate at the boundary
- Document everything in tool descriptions
- Make errors self-correcting
- Wrap every handler in a safe error boundary
- Verify every name against the source
- Test with realistic, imperfect inputs

Build these habits into the implementation process from the start — not as an audit step after the fact.

---

## Next Steps

Once your MCP server grows beyond 20 tools, see **[MCP Tool Grouping](./MCP_TOOL_GROUPING.md)** for how to reduce token costs by 50-95% through dynamic tool visibility.
