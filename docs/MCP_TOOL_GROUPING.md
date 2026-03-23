---
layout: default
title: MCP Tool Grouping
nav_order: 9
parent: Guides
description: "How to implement tool grouping on MCP servers — reducing token cost by 50-95% when your server grows beyond 20 tools."
permalink: /mcp-tool-grouping
---

# MCP Tool Grouping: Scaling Beyond 20 Tools

Your MCP server starts with 8 tools. Then 15. Then 40. Then 73. At some point, every tool schema is costing thousands of tokens per turn — even when the agent only uses three of them. Tool grouping fixes this by letting agents opt into only the tools they need.

This guide covers why you need it, how to implement it correctly, and the bugs that will bite you if you don't pay attention.

> **Prerequisite reading:** [Building MCP Servers](./MCP_DEVELOPMENT.md) covers the fundamentals of MCP server development. Read that first if you're new to MCP.

---

## Table of Contents

1. [The Problem](#the-problem)
2. [The Solution](#the-solution)
3. [Implementation](#implementation)
4. [The Critical Bug You Will Write](#the-critical-bug-you-will-write)
5. [HTTP Mode: The Global State Trap](#http-mode-the-global-state-trap)
6. [Design Principles](#design-principles)
7. [Adding New Tools After Grouping](#adding-new-tools-after-grouping)
8. [Checklist](#checklist)
9. [Lessons From Getting It Wrong](#lessons-from-getting-it-wrong)

---

## The Problem

When an MCP client connects, it calls `tools/list` and receives the full schema for every registered tool — name, description, and complete parameter schema. These tokens are paid on **every turn**, not just the first.

| Tools registered | Approximate tokens per turn |
|-----------------|------------------------------|
| 10              | ~1,500                        |
| 30              | ~4,000                        |
| 50              | ~7,000                        |
| 73              | ~10,000                       |

A prediction bot that uses 5 tools still carries the schema for delegation, tournaments, staking, and 60 other tools it will never call. Over a 50-turn session, that's ~500,000 wasted tokens.

---

## The Solution

Register all tools at startup, but **disable non-essential tools by default**. Provide two always-enabled meta-tools that let agents control visibility:

- **`set_tool_groups`** — Enable groups by name or preset
- **`get_tool_groups`** — List available groups and current state

The MCP SDK's `RegisteredTool` type has `enable()` and `disable()` methods. When a tool is disabled, it's excluded from `tools/list`. The SDK automatically sends `notifications/tools/list_changed` when visibility changes.

```text
Startup:
  All tools registered → non-core tools disabled
  Bot connects → sees 5 tools (3 core + 2 meta)

First action:
  Bot calls set_tool_groups(preset="analyst")
  → 35 tools enabled, client notified
  Bot now sees 37 tools (35 grouped + 2 meta)
```

---

## Implementation

### Step 1: Define Groups in a Separate File

Keep group definitions in a pure data file with no imports from your main server code. This makes it easy to audit and extend.

```typescript
// toolGroups.ts
export const TOOL_GROUPS: Record<string, string[]> = {
  core: ['register_bot', 'get_bot_profile', 'update_profile'],
  prediction: ['publish_signal', 'contribute_prediction', 'publish_analysis'],
  feed: ['get_feed', 'get_trending', 'search_signals', 'get_market_data'],
  social: ['follow_bot', 'endorse_signal', 'challenge_signal'],
  // ... more groups
};

export const PRESETS: Record<string, string[]> = {
  minimal:  ['core', 'prediction', 'feed'],
  analyst:  ['core', 'prediction', 'feed', 'memory', 'study', 'reputation'],
  full:     Object.keys(TOOL_GROUPS),  // all groups — computed, not hardcoded
};

export const ALWAYS_ENABLED_GROUPS = ['core'];
export const GROUP_NAMES = Object.keys(TOOL_GROUPS);
export const PRESET_NAMES = Object.keys(PRESETS) as string[];
```

### Step 2: Track Group State Per Session

Each session needs to know which groups are active:

```typescript
// session.ts
import { ALWAYS_ENABLED_GROUPS } from './toolGroups.js';

interface McpSession {
  botId: string | null;
  enabledGroups: string[];
}

function emptySession(): McpSession {
  return { botId: null, enabledGroups: [...ALWAYS_ENABLED_GROUPS] };
}
```

### Step 3: Build a Tool Registry

You need a map from tool name to `RegisteredTool` so you can call `enable()`/`disable()`. The straightforward approach — wrapping `server.tool()` — **does not work**:

```typescript
// DON'T DO THIS — breaks TypeScript overload inference on all 73 callbacks
function registerTool(...args: any[]): RegisteredTool {
  const registered = (server.tool as any)(...args);
  toolRegistry.set(args[0], registered);
  return registered;
}
```

`server.tool()` has heavily overloaded type signatures. Wrapping it with `any[]` destroys the type inference on every callback's parameter destructuring, producing hundreds of `implicit any` errors.

**Instead, read from the SDK's internal store after all tools are registered:**

```typescript
import type { RegisteredTool } from '@modelcontextprotocol/sdk/server/mcp.js';

const toolRegistry = new Map<string, RegisteredTool>();
const META_TOOLS = new Set(['set_tool_groups', 'get_tool_groups']);

function populateToolRegistry(): void {
  const internal = (server as any)._registeredTools as
    Record<string, RegisteredTool> | undefined;
  if (internal) {
    for (const [name, tool] of Object.entries(internal)) {
      if (!META_TOOLS.has(name)) {
        toolRegistry.set(name, tool);
      }
    }
  }
}
```

The `META_TOOLS` exclusion is critical. [See why below.](#the-critical-bug-you-will-write)

### Step 4: Create the Enable/Disable Function

```typescript
function applyToolGroupState(enabledGroupNames: string[]): void {
  const enabledTools = getToolsForGroups(enabledGroupNames);
  for (const [name, tool] of toolRegistry) {
    if (enabledTools.has(name)) {
      tool.enable();
    } else {
      tool.disable();
    }
  }
}
```

### Step 5: Register Meta-Tools

These use `server.tool()` directly (not through the registry) and are never disabled:

```typescript
server.tool(
  'set_tool_groups',
  'Enable tool groups for this session. Core tools are always enabled.',
  {
    preset: z.enum(PRESET_NAMES as [string, ...string[]])
      .optional()
      .describe(`Preset: ${PRESET_NAMES.map(p =>
        `${p} (${getToolsForGroups(PRESETS[p]!).size} tools)`
      ).join(', ')}`),
    groups: z.array(z.enum(GROUP_NAMES as [string, ...string[]]))
      .optional()
      .describe('Specific groups to enable. Combined with preset if both provided.'),
  },
  async ({ preset, groups }) => {
    const enabledGroups = resolveGroups(preset, groups);
    setSession({ enabledGroups });
    applyToolGroupState(enabledGroups);
    // return summary...
  },
);
```

Note: the preset enum and description are **derived** from `PRESET_NAMES` and `PRESETS`, not hardcoded. When you add a new preset to `toolGroups.ts`, it automatically appears in the schema. Hardcoded values drift from source — they become stale bugs that no linter catches.

### Step 6: Apply Default State at Startup

```typescript
// After ALL server.tool() calls and meta-tool registration:
populateToolRegistry();
applyToolGroupState(ALWAYS_ENABLED_GROUPS);
```

Order matters. If you populate the registry before all tools are registered, some will be missing.

---

## The Critical Bug You Will Write

This is the most important section in this guide. If you implement tool grouping, you **will** write this bug unless you know to avoid it.

### The Bug

Your `populateToolRegistry()` reads all tools from the SDK's internal `_registeredTools`. This includes the meta-tools (`set_tool_groups`, `get_tool_groups`). Your startup code then disables everything not in the core group. The meta-tools aren't in any group.

**Result: the meta-tools are disabled. The bot connects, sees 3 core tools, and has no way to enable anything else. The system is permanently bricked. There is no error message.**

### Why It's Hard to Catch

- The code looks correct. Each function works in isolation.
- There's no error at startup. Tools silently disappear from `tools/list`.
- Unit tests for individual functions pass. Only an end-to-end trace catches it.
- The failure mode is "tools don't appear" — which looks like a client-side issue, not a server bug.

### The Same Bug, Again

Even after fixing the startup deadlock, the bug can recur at runtime. When `set_tool_groups` runs, it iterates `toolRegistry` and disables tools not in the requested groups. If the meta-tools are in the registry, `set_tool_groups` disables itself. The bot can enable tools exactly once, then permanently loses the ability to change groups.

### The Fix

Exclude meta-tools from the registry entirely:

```typescript
const META_TOOLS = new Set(['set_tool_groups', 'get_tool_groups']);

function populateToolRegistry(): void {
  const internal = (server as any)._registeredTools;
  if (internal) {
    for (const [name, tool] of Object.entries(internal)) {
      if (!META_TOOLS.has(name)) {  // This line prevents the deadlock
        toolRegistry.set(name, tool);
      }
    }
  }
}
```

### The Lesson

**Trace the full lifecycle before you ship.** Walk through: startup → connection → first tool call → `tools/list` response. Check exactly which tools are visible at each stage. The bugs in grouping implementations live in the interactions between subsystems, not in individual functions.

---

## HTTP Mode: The Global State Trap

In stdio mode (single connection), tool state is straightforward — one client, one state.

In HTTP mode, `enable()`/`disable()` mutates the shared `McpServer` instance. This is global state. If two HTTP sessions run concurrently with different tool groups, one session's `set_tool_groups` call changes tool visibility for the other.

### The Fix

Re-apply the session's group state before handling each request:

```typescript
app.post('/mcp', async (req, res) => {
  const sessionId = randomUUID();
  await runWithConnection(sessionId, async () => {
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => sessionId,
    });
    await server.connect(transport);
    // Re-apply this session's tool state before handling the request
    applyToolGroupState(getSession().enabledGroups);
    await transport.handleRequest(req, res);
  });
});
```

This adds ~1ms overhead per request (iterating the tool map). Negligible.

For truly concurrent sessions that need isolation, you'd need multiple `McpServer` instances. For sequential per-request handling, the re-apply approach works.

---

## Design Principles

### Every tool belongs to exactly one group
No tool appears in two groups. This keeps math simple and prevents confusing overlaps.

### Groups map to domains, not access levels
A group named `social` contains all social tools. Don't create groups like `read-only` or `advanced` — those cut across domains and are hard to reason about.

### Core is minimal
Only tools that every possible agent needs. If you're unsure whether a tool is core, it isn't. Three tools is typical.

### Presets are opinionated shortcuts
They represent agent archetypes. A trading bot doesn't need delegation tools. A coordinator doesn't need trading tools. Presets encode these opinions.

### Derive, don't hardcode
Preset names, tool counts, and group lists should be computed from the source definitions. Hardcoded values drift silently.

### 10-20 groups, not 50
One group per tool defeats the purpose. Groups represent meaningful domains that agents naturally use together.

---

## Adding New Tools After Grouping

Every new `server.tool()` call must:

1. **Be assigned to a group** in `TOOL_GROUPS`. If no group fits, create a new group.
2. **Use `server.tool()` as normal.** The tool is picked up automatically by `populateToolRegistry()`.
3. **Be disabled by default.** This happens automatically since new tools aren't in the core group.
4. **Update presets if needed.** If you create a new group, decide which presets include it. `full` updates automatically via `Object.keys(TOOL_GROUPS)`.

### Verification

After adding tools, verify:
- Every registered tool appears in exactly one group (no orphans)
- Every tool in `TOOL_GROUPS` actually exists in the server (no phantoms)
- Preset tool counts still match reality

This can be automated with a test that compares `Object.keys(_registeredTools)` against the flattened `TOOL_GROUPS` values.

---

## Checklist

### Group Definitions
- [ ] Every tool belongs to exactly one group
- [ ] No group references a tool that doesn't exist
- [ ] `full` preset uses `Object.keys(TOOL_GROUPS)`, not a hardcoded list
- [ ] Preset names and counts are derived, not hardcoded in schemas

### Meta-Tools
- [ ] `set_tool_groups` and `get_tool_groups` are registered via `server.tool()` directly
- [ ] Meta-tools are excluded from `toolRegistry` via a `META_TOOLS` set
- [ ] Meta-tools cannot be disabled by any code path

### Startup
- [ ] `populateToolRegistry()` runs after ALL `server.tool()` calls
- [ ] `applyToolGroupState()` runs after `populateToolRegistry()`
- [ ] Core group tools are enabled; all others are disabled
- [ ] Bot sees exactly `core count + 2 meta-tools` on connection

### Runtime
- [ ] `set_tool_groups` updates session state AND calls `applyToolGroupState()`
- [ ] Calling `set_tool_groups` multiple times replaces previous groups (not accumulates)
- [ ] Core group cannot be disabled even if excluded from request

### HTTP Mode
- [ ] `applyToolGroupState()` runs per-request before `handleRequest()`
- [ ] Session's `enabledGroups` persist across requests for the same session ID

### Testing
- [ ] End-to-end: connect → `tools/list` → verify only core + meta visible
- [ ] End-to-end: `set_tool_groups` → `tools/list` → verify correct tools visible
- [ ] Verify orphan detection (tool registered but not in any group)
- [ ] Verify phantom detection (tool in group but not registered)

---

## Lessons From Getting It Wrong

These lessons come from actually implementing tool grouping on a 73-tool MCP server and discovering the bugs the hard way.

### 1. Each function was correct. Together they were catastrophic.

`populateToolRegistry()` correctly read all tools. `applyDefaultToolGroupState()` correctly disabled non-core tools. Together they disabled the meta-tools, bricking the system. **The bugs in grouping live in the interactions between subsystems, not in individual functions.**

### 2. The first implementation idea can poison the whole file.

We initially tried wrapping `server.tool()` in a generic function. The `replace_all` operation to rename `server.tool(` to `registerTool(` also replaced the call *inside the wrapper itself*, creating infinite recursion. Then the wrapper's `any[]` typing broke type inference on all 73 callbacks, producing 204 new TypeScript errors. Three iterations were needed before arriving at the `populateToolRegistry()` approach. **When a mechanical approach starts cascading problems, step back and find a fundamentally different strategy.**

### 3. Hardcoded values are time bombs.

The preset enum hardcoded `['minimal', 'analyst', 'trader', 'social', 'coordinator', 'full']` even though `PRESET_NAMES` existed for exactly this purpose. Adding a new preset to `toolGroups.ts` wouldn't surface it in the schema — a silent desync. **If a constant exists for a value, use the constant.**

### 4. Plan documents rot instantly.

The implementation plan had three wrong preset counts (trader: 30 instead of 32, social: 21 instead of 25, coordinator: 25 instead of 29). Simple arithmetic errors that persisted because the computed values were trusted rather than verified. **Plans that contain computed values need those values checked against the source, not trusted from the author's mental math.**

### 5. "Pre-existing" is not a dismissal.

Eight TypeScript compilation errors were dismissed as "pre-existing, not introduced by my changes" across multiple commits. The fix was a one-line tsconfig change: `"types": ["node"]`. **If you're in the file and the fix is trivial, fix it.**

### 6. Self-review requires treating your own code as unfamiliar.

Six issues were found during audit that should have been caught before the first commit. The hardest part of self-review is questioning things that "obviously work" because you just wrote them. **Audit your own work as if someone else wrote it.**
