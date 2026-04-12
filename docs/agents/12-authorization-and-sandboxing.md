---
layout: default
title: 12. Authorization, Sandboxing & Isolation
nav_order: 12
parent: Agents Guide
description: "User-level vs. agent-level permissions, network egress controls, filesystem scoping, container isolation, and the principle of least privilege applied to autonomous agents."
permalink: /agents/authorization-and-sandboxing
---

# 12. Authorization, Sandboxing & Isolation

If an attacker compromises your agent — by prompt injection, by a poisoned document, by a malicious tool output, or by sheer bad luck — the only thing standing between the attacker and your production systems is the infrastructure boundary you put around the agent.

Not the prompt. Not the model's good intentions. The boundary.

This chapter is about that boundary. It is the most security-forward chapter in the guide, and it is the one teams most often push to "later." Do not push it. The infrastructure layer is where you cash in the safety promises you made in Chapters 4–6.

---

## Two Kinds of Permissions

Agents have to answer two different authorization questions on every tool call, and teams routinely conflate them:

### Agent-level permissions

> *"Is this agent allowed to use this tool at all?"*

Agent-level permissions are set by you, the builder, at design time. They say things like:

- The Support Triage Drafter can use `fetch_order_status` and `post_reply_to_review_queue`, but not `issue_refund`.
- The research assistant can use `search_web` and `summarize`, but not `send_email`.
- The internal code assistant can call `read_file` inside the repository, but not `write_file` outside the `/tmp/` scratch directory.

These permissions are a property of the agent. They do not depend on who the user is. If the agent does not have the tool, the tool is not on the list the model sees — full stop.

### User-level (or session-level) permissions

> *"Is **this caller**, on **this request**, allowed to perform this specific action on this specific data?"*

User-level permissions depend on who triggered the run, what their role is, what they own, and what the action would touch. They say things like:

- This support rep can look up orders for any customer.
- This end user can only look up their own orders.
- This admin can approve refunds up to $500 without a second signoff.
- This service account can read from the audit log but not write to it.

Both layers must exist, and both layers must be enforced. Agent-level permissions without user-level permissions lead to over-broad agents that act on the wrong user's data. User-level permissions without agent-level permissions lead to agents that "technically could not" take a destructive action but "technically did" because the tool was still callable.

The simplest rule: **the user-level check belongs inside the tool, and the agent-level list belongs outside it**. One is enforced at the point of the call; the other determines what calls exist in the first place.

---

## The Principle of Least Privilege, For Agents

The classical principle of least privilege — *a component should have only the permissions it needs to do its job* — applies to agents with one important adjustment: you are not granting privileges to a process, you are granting them to a *model that chooses its own actions*. That changes the math in two ways:

1. **Defaults matter more.** A human operator who has excess permissions usually does not use them. A model under adversarial input will use every permission you gave it. Grant on a strict allowlist basis.
2. **Revocation is harder.** Once a capability is in production, removing it tends to break real flows. The first grant is where you should spend the paranoia budget, not the tenth.

Apply least privilege on all five axes that matter for agents:

| Axis            | Question to answer                                                         |
|:----------------|:---------------------------------------------------------------------------|
| Tools           | Exactly which tools does this agent need?                                  |
| Data            | Exactly which rows, records, files, or documents can each tool touch?      |
| Users           | Exactly which callers can invoke this agent, and from where?               |
| Network         | Which domains or IPs can the agent's process reach out to?                 |
| Filesystem      | Which paths can the agent read, write, or execute?                         |

Answer all five before the agent goes live. Every "we will figure this out later" is a future incident.

---

## Enforcing User-Level Permissions Inside Tools

The most common authorization bug in early agents is this: the scope brief says *"only look up orders belonging to the requesting customer"*, the prompt dutifully repeats it, and the tool itself does not check. The agent then violates the rule when a user phrases their request oddly, and the post-mortem discovers the rule was never enforced at all.

Fix it in the tool. Every tool that touches user-specific data should take an explicit caller context and check it:

```python
def fetch_order_status(order_id: str, *, caller: CallerContext) -> OrderStatus:
    order = orders_db.get(order_id)
    if order is None:
        return {"error": "order_not_found", "order_id": order_id}

    if not caller.can_read_order(order):
        return {
            "error": "not_authorized",
            "retryable": False,
            "message": "This order is not accessible to the current session."
        }

    return order.status_payload()
```

Three design choices to notice:

- **`caller` is a required parameter, not an implicit thread-local.** Implicit caller context is how authorization bugs hide; explicit caller context is how they get caught in code review.
- **The unauthorized case returns a structured error, not an exception.** The model reads the error, recognizes `not_authorized`, and escalates. An exception would become "tool error" and the trace would be harder to read.
- **The permission check lives in the tool, not in the prompt.** No amount of prompt tuning can bypass this.

The agent-level permission layer — *"does this agent have this tool at all?"* — happens when the tool schema is assembled at run start. If the agent is not allowed to use `issue_refund`, that tool is simply not on the schema list the model ever sees. It cannot be called because it does not exist from the model's perspective.

---

## Sandboxing the Process

Authorization prevents the *tools* from doing the wrong thing. Sandboxing prevents *the agent's process* from doing the wrong thing — reaching a server it should not, writing to a file it should not, executing a binary it should not.

Sandboxing is especially important when the agent:

- Runs arbitrary code the model generated.
- Executes shell commands.
- Processes untrusted content (emails, web pages, documents) that could contain prompt injection payloads.
- Has any tool that itself makes outbound network calls.

### Network egress control

By default, the agent's process should not be able to reach the open internet. It should only be able to reach the specific domains or IPs the tools need.

- Run the agent in a container with a restrictive egress policy: an allowlist of destinations, deny-by-default.
- Block metadata endpoints (e.g., cloud instance metadata services) explicitly — these are the first thing exploit payloads try.
- Require outbound requests to go through a proxy that enforces the allowlist and logs every call.
- Treat the allowlist as a code artifact: reviewed, versioned, changed only through a PR.

### Filesystem scoping

The agent should see only the files it needs to do its job.

- Mount only the required directories into the sandbox. Make them read-only when possible.
- Scratch space goes to a bounded, ephemeral directory (`/tmp/agent-scratch-<runid>/`) that gets wiped at the end of the run.
- Never expose credentials files, SSH keys, or host environment variables into the sandbox unless a specific tool needs them — and then only that tool.

### Process isolation

A compromised agent process should not be able to harm its neighbors.

- Run each agent instance in its own container or lightweight sandbox (user namespace, seccomp filters, or equivalent).
- Do not share long-lived credentials between agent instances.
- Limit resource use: CPU, memory, disk, file descriptors. This is also an anti-DOS measure — see [Chapter 13](./13-cost-and-kill-switches.md).

### Code execution

If the agent can execute code — for example, by generating Python and running it — treat the code execution layer as the most hostile component in your stack.

- The code runs in a separate sandbox from the agent's own process, with *more* restrictions, not fewer.
- The sandbox has no network access, or strictly limited network access.
- The sandbox has a wall-clock timeout and a memory limit.
- Outputs are size-capped before being returned to the model (so a malicious script cannot return a 10 MB payload that blows out the context window).

---

## Secrets Management

Agents routinely need secrets — API keys, database credentials, signing keys. These are the single most valuable thing an attacker can exfiltrate from a compromised agent, and they must never be visible to the model.

Three rules:

1. **Secrets are injected into the tool, not into the prompt.** The model should never see an API key. If the tool's description says *"provide the auth token in the `api_key` field,"* that is a bug.
2. **Secrets are held by the infrastructure layer.** A secret manager holds them; the tool process reads them at startup or per-call; the model never touches them.
3. **Secrets are scoped.** The key the agent uses should have the minimum privileges needed — a read-only key, a customer-scoped key, a per-environment key. No "admin key because it is simpler."

Audit regularly: grep every agent process for environment variables that look like credentials, and make sure they are the minimally-privileged versions. This is worth doing at least once before launch and once after any major refactor.

---

## Isolating Per-Tenant Data

For any agent that operates on behalf of multiple users or organizations, tenant isolation is the single most important data boundary. A prompt injection that smuggles data across tenants is an incident. A bug that returns Tenant A's orders to Tenant B is a bigger one.

Defense in depth:

- **Filter at the database layer.** Queries must include the tenant ID in the WHERE clause, enforced by a shared helper, not left to each call site.
- **Filter at the tool layer.** The tool rejects calls that reference IDs the caller does not own.
- **Filter at the response layer.** Before returning data to the model, verify that every record in the response belongs to the caller's tenant. Anything that does not is dropped and logged as a violation — *and* alerts fire immediately.
- **Never cache across tenants.** Retrieval caches, summary caches, anything that mixes data across tenants is a leak vector.

Yes, this is redundant. That is the point. A bug that gets past one layer is caught by the next, and a correlated bug that gets past two layers still gets alerted on the third.

---

## Auditing the Boundary

Once you think you have the boundary in place, *test it*. The infrastructure layer is code too; it has bugs; and the only way to find them is to try to break it.

Before launch, run a set of adversarial drills:

- **Egress test**: put a tool in the agent that tries to reach `http://example.net/exfil`. The network policy should block it. If it does not, you have a gap.
- **Tenant-cross test**: feed the agent a request whose referenced data belongs to a different tenant. Every layer should refuse it, the last layer should alert.
- **Secret-leak test**: try to get the agent to print its own environment variables, read `/proc/self/environ`, or return a file containing secrets. The result should be *"access denied,"* not *"here you go."*
- **Escape test**: try to make a code-execution tool write outside its sandbox, touch the host filesystem, or spawn a shell that survives the run.
- **Privilege-escalation test**: invoke the agent as a low-privilege user and try to reach an action reserved for admins. The agent-level permission layer should refuse.

These drills become part of the adversarial test suite in [Chapter 16](./16-chaos-and-adversarial-testing.md). Run them on every infrastructure change.

---

## Anti-Pattern: Prompt-Only Authorization

**Symptom**: The team relies on instructions in the system prompt to enforce access rules. The prompt says things like *"only look up orders belonging to the current user"*, *"never access data from other tenants"*, *"do not print secrets"*. The tools themselves have no permission checks. There is no sandbox. The "security layer" is the model's good judgment.

**Why it hurts**: Every one of those prompt-level rules is one prompt-injection payload away from being bypassed. The model does not "know" the rules the way a code path knows its guards — it follows them statistically, under adversarial pressure, without any enforcement. A small fraction of runs will violate them, and those runs will be the incidents.

**Fix**: Move every authorization rule into the tool layer and every sandbox rule into the infrastructure layer. The prompt's role is to describe the agent; the code's role is to make violations impossible. If you cannot enforce a rule in code, assume it is unenforced in practice.

---

## Checklist

- [ ] Agent-level permissions are explicit — the tool schema the model sees is exactly the set of tools this agent is allowed to use, nothing more.
- [ ] User-level permissions are enforced inside every tool that touches user-specific data, via an explicit `caller` context parameter.
- [ ] The agent runs in a sandbox with a deny-by-default egress policy and an explicit allowlist of destinations.
- [ ] Metadata endpoints and internal networks are blocked.
- [ ] The filesystem is read-only where possible; scratch space is bounded and ephemeral.
- [ ] Secrets are never visible to the model, are held by the infrastructure, and are scoped to the minimum privileges needed.
- [ ] Code-execution tools (if any) run in a secondary sandbox with no network, a wall-clock timeout, memory limits, and output size caps.
- [ ] Tenant isolation is enforced in the DB, the tool, and the response — defense in depth.
- [ ] Adversarial drills (egress, tenant-cross, secret-leak, escape, privilege escalation) are part of the pre-launch test suite.
- [ ] You have never, at any point, relied on the system prompt to enforce a rule that matters.

---

## What to Read Next

- [Chapter 5 — Designing the Tool Interface](./05-tool-interface-design.md): tool-level authorization is part of the tool contract, not an add-on.
- [Chapter 13 — Cost, Rate-Limiting & Latency Budgets](./13-cost-and-kill-switches.md): resource isolation is the runtime twin of this chapter.
- [Chapter 15 — Hardening Against Prompt Injection](./15-prompt-injection-defense.md): the attack model this chapter is defending against.
- [Chapter 16 — Chaos & Adversarial Testing](./16-chaos-and-adversarial-testing.md): where the authorization drills live.
