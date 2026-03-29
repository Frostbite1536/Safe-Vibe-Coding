---
layout: default
title: Smart Contract Audit
parent: Prompts Library
nav_order: 14
---

# Smart Contract Audit Prompt

Use this prompt to audit Solidity smart contracts for security vulnerabilities. Designed for adversarial environments where every public function can be called by anyone, admin keys can be compromised, and the mempool is observable.

---

## Prompt

You are conducting a security audit of Solidity smart contracts. Assume a **hostile environment**: compromised admin keys, paused contracts with advancing timestamps, mempool-visible transactions, and reverting external addresses.

**Review the following contracts**: [paste contract code or describe the contract set]

**Audit methodology — check every category systematically:**

### 1. Time & Pause Analysis

For every function with `whenNotPaused`:
- Classify it: offensive (stake, register, slash), defensive (challenge, renew, withdraw), or settlement (claim, release)
- **Defensive actions must NOT be blocked by pause** — if they are, the pause mechanism weaponizes time against users
- For every deadline/window: can the user's response action be paused while the clock ticks?
- For every `block.timestamp` comparison: what happens if the contract is paused for days?

### 2. External Call Analysis

For every `safeTransfer`, `.call`, or external function call:
- Is the recipient `msg.sender` (safe) or a stored address like treasury (risky)?
- If the external call reverts, does it block other users' state transitions?
- Is pull-over-push used for all non-sender transfers in critical paths?
- Check for reentrancy: are state changes made before external calls?

### 3. Mutable Config Analysis

For every admin-settable parameter (`set*` functions):
- Is this parameter used in calculations for already-committed funds?
- If yes: is the value snapshotted at commitment time, or does it retroactively change payouts?
- What happens at value = 0? At `type(uint256).max`?
- Does the setter have minimum and maximum validation?
- If one config value exists *because of* another, does changing one update the other?

### 4. Privileged Role Analysis

For every function gated by access control (`onlyRole`, `onlyOwner`, etc.):
- What is the maximum damage a compromised key can do in **one block**?
- Can the function be called repeatedly in the same transaction? (loop attack)
- Are destructive actions rate-limited?
- Do rate limits verify the action is substantive before consuming the cooldown budget?
- Can a zero-amount action consume rate-limit budget without effect?

### 5. State Lifecycle Analysis

For every array or mapping:
- Is there a deletion strategy, or does it grow unboundedly?
- For arrays used in loops: what is the gas cost after 10,000 entries?

For every terminal state:
- Can the identifier (nodeId, bondId, etc.) be reused after deregistration?
- Does the "existence check" (`lockedAt != 0`, `amount > 0`) distinguish active from historical?

### 6. Front-Running & MEV

For every function whose parameters or timing determine economic outcomes:
- Can the outcome be observed in the mempool before execution?
- Can a watcher copy the transaction, change the sender, and profit?
- Is commit-reveal or a commitment deadline needed?

### 7. Upgradeable Contract Safety

If using UUPS, transparent proxy, or similar patterns:
- Are new struct fields appended to the END of the struct?
- Is the storage gap decremented correctly for each new state variable?
- Do sentinel values (`0 = unset`) conflict with valid values?
- For new data structures: what happens to data created before the upgrade?
- Is the `_authorizeUpgrade` function properly protected?

### 8. Cross-Contract Consistency

For every vulnerability found:
- Does the same pattern exist in sibling contracts?
- Do all contracts handling the same external address use the same pattern?
- If contracts share roles, can role interactions create unexpected states?

### 9. Economic Invariant Analysis

For every staking/bonding/deposit mechanism:
- Can a user extract more value than they deposited through any sequence of actions?
- Are correlated invariants maintained? (e.g., if bond amount decreases via slash, does max inventory adjust?)
- Can rounding errors be exploited across many small operations?

### 10. Event Completeness

- Does every state-changing function emit an event?
- Are events consistent across similar functions? (e.g., `withdrawRewardPool` emits but `claimTreasuryFunds` doesn't)

---

**Output format:**

For each finding:
- **ID**: [Severity-Number, e.g., H-01, M-02, L-03]
- **Severity**: Critical / High / Medium / Low / Informational
- **Contract**: [Contract name]
- **Function**: [Function name]
- **Issue**: [Clear description of the vulnerability]
- **Attack scenario**: [Step-by-step exploit path]
- **Attacker cost vs. victim loss**: [Economic analysis]
- **Suggested fix**: [Concrete code or pattern change]
- **Cross-contract check**: [Does this pattern appear in other contracts?]

After all findings, provide:
- **Summary table** of findings by severity
- **Cross-contract pattern matrix** showing which vulnerabilities appear in which contracts

---

## Post-Fix Re-Audit Prompt

Use this after implementing audit fixes to catch bugs introduced by the fixes themselves.

```
You are re-auditing smart contracts after implementing fixes from a prior audit.
Your job is to audit the FIXES THEMSELVES as new code. The original auditor is
not infallible — their suggested fixes may introduce new bugs.

Specifically check:
1. NEW PARAMETERS: Does every new setter have min/max validation? What happens at 0?
2. SENTINEL VALUES: If using `value > 0` to mean "was set", can 0 ever be a valid value?
3. CROSS-CONTRACT: Was the fix applied to ALL contracts with the same pattern, or just one?
4. RATE LIMITS: If rate limiting was added, can a no-op action consume the cooldown?
5. PULL-OVER-PUSH: If treasury transfers were converted, were ALL treasury transfers converted?
6. EVENTS: Are events emitted for new state changes? Are they consistent with existing events?
7. SNAPSHOT LOGIC: If values are snapshotted at commitment time, is the "unset" detection correct?

For each issue found, note whether it was:
- (A) A bug in the auditor's suggested fix code
- (B) A pre-existing issue the original audit missed
- (C) A new issue introduced during implementation
```

---

## Quick Pre-Deployment Checklist Prompt

```
Run through this checklist for each contract. Answer YES, NO, or N/A for each item.
If NO, explain the risk and suggest a fix.

TIME & PAUSE
[ ] Every whenNotPaused function justified (defensive actions exempt)
[ ] No deadline that ticks during pause without user recourse

EXTERNAL CALLS
[ ] No safeTransfer to non-msg.sender in functions other users depend on
[ ] Checks-effects-interactions pattern followed everywhere

MUTABLE CONFIG
[ ] Every setter has min/max validation
[ ] Config affecting committed funds is snapshotted at commitment time

PRIVILEGED ROLES
[ ] Maximum single-block damage documented for every role
[ ] Destructive actions rate-limited with substantive-action check

STATE LIFECYCLE
[ ] Every array has a bounded growth or deletion strategy
[ ] Terminal states distinguishable from active states

UPGRADEABLE
[ ] New struct fields at end only, storage gap adjusted
[ ] Sentinel values don't collide with valid values
[ ] Migration plan for existing data on structure changes

CROSS-CONTRACT
[ ] Same patterns use same fixes across all sibling contracts
```
