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
5. [Design Your Internal APIs for MCP from Day One](#design-your-internal-apis-for-mcp-from-day-one)
6. [Common Bug Categories](#common-bug-categories)
7. [MCP Server Checklist](#mcp-server-checklist)

---

## What Is an MCP Server?

An MCP server exposes **tools** — functions with typed input schemas and structured output — over a transport layer (typically stdio or HTTP). An LLM client connects to the server, reads the list of available tools and their descriptions, and calls them by sending JSON parameters. The server executes the tool and returns a structured response.

```
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

- **Database queries**: Let the LLM explore and modify data without writing raw SQL
- **API integrations**: Connect to Slack, GitHub, Jira, or internal services
- **Domain-specific operations**: Animation engines, analytics pipelines, CRM systems
- **File and infrastructure management**: Controlled access to filesystems, deployments, cloud resources

The alternative — having the LLM generate scripts you run manually — is slower, less safe, and harder to constrain. MCP servers give you a boundary where you control exactly what the LLM can and cannot do.

---

## The Core Mental Model

> **Your consumer is an LLM, not a human.**

This single idea explains most of the bugs in first-time MCP server implementations. A human developer can read source code, try different parameter names, inspect stack traces, and intuit what went wrong. An LLM cannot. It will:

- Use exactly the parameter names from your description (and hallucinate plausible alternatives if the description is unclear)
- Trust default values silently rather than questioning them
- Retry with the same wrong approach if the error message doesn't contain enough information to correct course
- Never discover undocumented parameters or features

**Treat every tool description as the complete, authoritative API documentation. If it isn't in the description, it doesn't exist to the LLM.**

---

## Guidelines for AI Coding Agents

The following guidelines are written for the LLM coding agent that is building the MCP server. These are the patterns and pitfalls that surfaced across multiple real-world MCP server implementations.

### 1. Tool Descriptions Are Your API Contract

Tool descriptions are not comments or nice-to-haves. They are the **only documentation** the consuming LLM will ever read. Every tool description must include:

- **What the tool does** in one clear sentence
- **Every parameter** with its type, purpose, and valid values
- **Return type semantics**: Does this tool create something, return a reference, return data, or produce a side effect?
- **Naming conventions**: If outputs follow a pattern (e.g., `{name}_{outputKey}`), document it explicitly
- **Examples** for non-obvious parameter combinations

**Common failures:**
- Parameters that exist in code but aren't listed in the description — the LLM will never use them
- Inconsistent naming across similar tools (`freq` on one tool, `frequency` on another)
- Descriptions that say "see docs" — the LLM cannot see external docs mid-conversation
- Missing return type information — the LLM won't know whether it got back a reference, an ID, a URL, or a data object

### 2. Parameter Names Must Match Natural Expectations

If your description says `base` and `exponent`, your schema must accept `base` and `exponent` — not `a` and `b`. An LLM will pass what the description suggests. If the actual parameter names differ, you get silent wrong behavior (e.g., the wrong value falls through to a default) with no error.

**Rule:** Parameter names in the schema must match what the description leads the consumer to expect. If the underlying API uses terse names, accept both the terse and descriptive forms.

### 3. Validate at the Boundary — MCP Handlers Are the System Edge

MCP tool handlers sit at the trust boundary between an LLM (which generates unpredictable inputs) and your internal systems (which expect precise types). Every handler should be as defensive as a public API endpoint:

- **Validate enum values** before passing to internal code. LLMs may send display-friendly strings ("Meeting Scheduled") instead of database values ("Meeting_Scheduled"). Accept both forms where practical.
- **Guard against non-finite numbers.** `NaN` and `Infinity` won't crash your handler but will produce wrong results downstream (SVG elements off-canvas, silent calculation errors).
- **Validate references/IDs exist** before using them. Return the list of valid values in the error response if they don't.
- **Check types at runtime.** TypeScript's `as` casts and Python's dynamic typing both let wrong types through silently. If a parameter must be a string array, verify it's actually a string array.
- **Don't trust `as` casts.** The pattern `r('param') as string` bypasses the type system. When your schema uses `z.any()` or `z.record(z.any())` for flexibility, every `as` cast is an assumption that the LLM sent the right type. Validate first, then cast.

### 4. Error Messages Must Enable Self-Recovery

An LLM cannot re-read documentation or inspect source code when something goes wrong. Error responses must contain everything needed to retry correctly:

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

Include in error responses:
- What was wrong
- What the valid options are
- What the expected format looks like
- Available references/IDs when a lookup fails

Every error that says "see the docs" or "check the description" wastes a round-trip and burns context window.

### 5. Wrap Every Handler in a Safe Error Boundary

A single unhandled exception in an MCP server can crash the entire process or corrupt the transport stream. Wrap every tool handler with a decorator or try/catch that:

- Catches all exceptions
- Returns a structured error response instead of crashing
- Logs the full error for debugging
- Never leaks stack traces to the LLM (they waste context and expose internals)

This pattern (e.g., a `@safe_tool` decorator or `tryCatch` wrapper) was consistently the **single highest-value addition** across multiple MCP server implementations. It turns fatal crashes into recoverable error responses.

### 6. Never Print to stdout in stdio Transport

In stdio MCP transport, **stdout IS the JSON-RPC channel**. Any `print()`, `console.log()`, or debug output that writes to stdout will corrupt the message framing and break the connection.

This is unique to MCP servers and extremely easy to miss, especially when wrapping existing code that was originally designed for CLI use.

**Before wiring up existing code to an MCP handler:**
- Audit every `print`/`console.log`/`puts` call in the execution path
- Redirect all output to stderr or a log file
- Use a logging framework that can be configured to write to stderr

### 7. Verify Every Attribute Name Against the Actual Source

The most common category of MCP server bugs is **hallucinated attribute names** — plausible-sounding field names that are slightly wrong:

| What the code says | What actually exists |
|---------------------|---------------------|
| `report.amplifier_profiles` | `report.top_amplifiers` |
| `report.term_pairs` | `report.top_pairs` |
| `stats.total` | `stats.count` |
| `result.data` | `result` (the object itself) |

This happens because LLMs confidently invent field names that "sound right." Every attribute access on a return type from an internal API must be verified against the actual definition — dataclass fields, TypeScript interfaces, database column names.

**This applies to the agent building the server, not just the LLM consuming it.** When you are generating MCP handler code, cross-reference every field access against the real type definition.

### 8. Cross-Reference Every Function Signature

MCP tool wrappers are thin glue — they call internal functions with parameters received from the LLM. Every parameter name and keyword argument must exactly match the target function's signature:

| What the wrapper passes | What the function expects |
|------------------------|--------------------------|
| `csv_file=` | `csv_path=` |
| `client=` | `api_key=` |
| `max_workers=` | `workers=` |
| `date=` | `timestamp=` |

Python won't catch keyword argument mismatches until runtime. TypeScript may catch some at compile time but `as any` casts and `Record<string, unknown>` types hide them.

**Rule:** For every internal function call in an MCP handler, verify the parameter names against the function definition. Do not guess.

### 9. Handle Return Types Correctly

Two patterns that consistently cause bugs:

- **Dict vs. object confusion:** A function returns a dataclass/class instance, but the handler code treats it as a dictionary (checking for `.data` attribute, using `isinstance(dict)`). Or vice versa.
- **Dict iteration:** `for item in some_dict` iterates **keys** (strings), not values. This is a classic Python gotcha that produces empty or wrong results with no error.

**Rule:** Check the actual return type of every internal function you call. Don't assume dict when it's an object, or vice versa.

### 10. Check Imports and Exports

A class or function may exist in a module but not be re-exported from the package's `__init__.py`. The import `from mypackage.submodule import MyClass` may work, but `from mypackage import MyClass` may not.

**Rule:** Verify that every import in your MCP server code resolves correctly. Don't assume re-exports exist.

### 11. Serialize Carefully

MCP responses are JSON. Your internal data types are not. Common serialization failures:

- `datetime` objects — need explicit formatting
- `Tuple` dict keys — legal in Python, illegal in JSON (`json.dumps` only applies `default=str` to values, not keys)
- `Decimal`, `set`, `bytes`, custom objects — all need explicit conversion
- ORM/dataclass objects — need a `to_dict()` method or manual field extraction
- Prisma enum types vs. runtime strings — database ORMs expect their own enum types, not raw strings

**Rule:** Build a serialization layer that handles every type that can appear in your response objects. Test it with real data, not just happy-path examples.

### 12. Use Transactions for Multi-Step Operations

If a tool handler performs multiple database operations (e.g., update a record and create an audit log entry), wrap them in a transaction. MCP servers are long-lived processes where a broken pipe, timeout, or crash between operations is a real scenario — not a theoretical one.

### 13. Rate Limit Before Expensive Work

Check rate limits, permissions, and preconditions **before** performing database queries, API calls, or other expensive operations — not after. In an MCP context where an LLM might call tools in rapid succession, this prevents resource exhaustion.

### 14. Document Deduplication and Name-Mangling Behavior

If your server modifies input values (e.g., appending `_1`, `_2` to avoid name collisions), document this in the tool description and make the response clearly highlight when a name was changed. The LLM will reference the name it sent, not the name your server actually used.

### 15. Python Version Compatibility

If your project supports Python 3.9+, don't use `list[str] | None` syntax (requires 3.10+). Use `from __future__ import annotations` or `Optional[List[str]]` from `typing`.

---

## Design Your Internal APIs for MCP from Day One

Many MCP bugs don't originate in the MCP handler code — they originate in internal APIs that were never designed to be called by generated glue code. If you know you'll eventually expose functionality through MCP, design your internal APIs to be MCP-friendly from the start:

- **Use descriptive parameter names.** `csv_path` not `p`, `max_results` not `n`. The MCP handler is glue code that maps parameter names — the more obvious the names, the less room for error.
- **Return simple, serializable types.** Prefer dicts or dataclasses with primitive fields over complex nested objects with tuple keys or custom types.
- **Keep function signatures stable.** Every renamed parameter is a potential MCP handler bug.
- **Export public APIs explicitly.** If a class should be importable from the package, add it to `__init__.py`.
- **Avoid stdout for status output.** Use logging frameworks or stderr. This makes your code safe to use in stdio transport contexts.
- **Use consistent naming conventions** across similar functions. If one function uses `frequency`, don't use `freq` on a related function.

---

## Common Bug Categories

Ranked by how insidious they are (hardest to catch first):

### Silent Wrong Results (Most Dangerous)

These produce output with no error — but the output is wrong:

- `NaN` or `Infinity` in numeric fields (renders with missing/broken attributes)
- Wrong default values used when a parameter name doesn't match
- Iterating dict keys instead of values
- Type coercion that silently converts to wrong type
- Missing parameters that fall back to defaults the LLM didn't intend

### Hallucinated Names (Most Common)

Plausible attribute or parameter names that don't exist on the actual object or function. The code looks correct at a glance. It crashes at runtime.

### Transport Corruption

`print()` or `console.log()` calls that corrupt the stdio JSON-RPC channel. The server appears to work in tests (which don't use stdio transport) and breaks in production.

### Serialization Failures

Types that exist in your language but have no JSON representation. These crash `json.dumps()` / `JSON.stringify()` at runtime with unhelpful error messages.

### Type Boundary Mismatches

Prisma expects enum types, your handler receives strings. A function returns a dataclass, your handler treats it as a dict. TypeScript `as` casts hide the mismatch until runtime.

---

## MCP Server Checklist

Use this checklist when building or reviewing an MCP server.

### Tool Descriptions
- [ ] Every parameter is listed with type, purpose, and valid values
- [ ] Return type semantics are documented (creates, returns ref, returns data, side effect)
- [ ] Naming conventions for composite outputs are documented
- [ ] No description says "see docs" or "see description" — all info is inline
- [ ] Parameter names in schema match what the description leads the consumer to expect
- [ ] Consistent naming across similar tools (don't mix `freq` and `frequency`)

### Input Validation
- [ ] Enum values are validated before use
- [ ] Both display-friendly and internal forms are accepted where practical
- [ ] Numeric inputs are checked for `NaN`/`Infinity`
- [ ] References and IDs are verified to exist
- [ ] Required parameters are validated as present and non-null
- [ ] Types are validated at runtime, not just through type casts

### Error Handling
- [ ] Every handler is wrapped in a safe error boundary (decorator/try-catch)
- [ ] Error responses include valid options, expected format, and available references
- [ ] No error message says "see the docs" — all recovery info is inline
- [ ] Unhandled exceptions never crash the server process
- [ ] Stack traces are logged but not returned to the LLM

### Serialization
- [ ] All response types are JSON-serializable
- [ ] `datetime`, `Decimal`, `set`, `bytes`, tuple-keyed dicts are handled
- [ ] ORM/dataclass objects are converted to plain dicts
- [ ] Serialization is tested with real data, including edge cases

### Transport Safety
- [ ] No `print()`/`console.log()` calls write to stdout in the execution path
- [ ] All debug output goes to stderr or a log file
- [ ] Existing library code is audited for stdout output before wrapping

### Code Correctness
- [ ] Every attribute access is verified against the actual type definition
- [ ] Every function call uses the correct parameter names from the real signature
- [ ] Every import resolves correctly (not assuming re-exports)
- [ ] Return types are handled correctly (dict vs. object, iteration patterns)
- [ ] Multi-step database operations use transactions
- [ ] Rate limits and preconditions are checked before expensive work
- [ ] Python version syntax is compatible with the project's minimum version

### Integration Testing
- [ ] Each tool is tested with realistic LLM-style inputs (not just ideal inputs)
- [ ] Tools are tested with wrong parameter names to verify error messages
- [ ] Tools are tested with edge-case values (`null`, empty strings, boundary numbers)
- [ ] The full stdio transport path is tested end-to-end (not just handler functions)
- [ ] An LLM-specific input test suite exists (see below)

---

## Write an LLM-Specific Input Test Suite

LLMs don't send the same inputs humans do. They send lowercase enums (`"buy"` instead of `"Buy"`), `NaN` from hallucinated JSON, and arbitrary strings for sort orders. This is a distinct concern from normal unit tests and deserves its own test file.

Create a `test_llm_inputs.py` (or equivalent) that specifically tests the weird things LLMs actually send:

```python
# test_llm_inputs.py — tests for real LLM input patterns

def test_lowercase_enum_values():
    """LLMs often send lowercase versions of enum values."""
    # Should accept "buy", "Buy", "BUY" — normalize, don't reject
    result = handle_trade(action="buy")
    assert result.action == "Buy"

def test_nan_numeric_inputs():
    """LLMs sometimes produce NaN from malformed JSON."""
    # Should reject NaN, not silently produce wrong results
    with pytest.raises(ValueError):
        filter_by_pnl(min_pnl=float('nan'))

def test_infinity_numeric_inputs():
    """LLMs sometimes produce Infinity from edge-case calculations."""
    with pytest.raises(ValueError):
        set_threshold(value=float('inf'))

def test_arbitrary_sort_strings():
    """LLMs may send plausible but invalid sort orders."""
    result = list_trades(sort_by="most_recent")  # Not a valid sort key
    # Should return helpful error, not crash or silently ignore
    assert "valid sort options" in result.error.lower()

def test_extra_whitespace_in_strings():
    """LLMs sometimes add leading/trailing whitespace."""
    result = find_market(slug="  polymarket-election-2024  ")
    assert result is not None  # Should trim, not fail
```

**Why this matters**: `filter_by_pnl(min_pnl=float('nan'))` silently returns *all trades* because NaN comparisons always return `False` in Python. No error, no warning — just wrong results. Financial tools that silently give wrong numbers are worse than tools that crash.

**The advice from the MCP Development Guide to "accept both display-friendly and internal forms" is correct** — normalize inputs instead of rejecting them. Rejecting `"buy"` when you accept `"Buy"` just wastes an LLM round-trip.

---

## The Meta-Lesson

MCP servers look like simple glue code — thin wrappers connecting a protocol to internal APIs. But glue code at a trust boundary (LLM on one side, database/API on the other) has a different error profile than typical application code. The bugs aren't in business logic. They're in the seams: wrong names, wrong types, wrong keys, wrong iteration patterns, wrong serialization, wrong transport assumptions.

Real-world audits consistently show **25-30% defect rates** in first-pass MCP implementations. The defects are not complex — they are small, obvious-in-hindsight mismatches that compound because there are so many integration points and no type system spans the full boundary.

The fix is not cleverness. It is discipline:
- Validate at the boundary
- Document everything in tool descriptions
- Make errors self-correcting
- Wrap every handler in a safe error boundary
- Verify every name against the source
- Test with realistic, imperfect inputs

Build these habits into the implementation process from the start — not as an audit step after the fact.
