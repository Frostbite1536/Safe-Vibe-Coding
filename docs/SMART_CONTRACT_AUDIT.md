---
layout: default
title: Smart Contract Auditing
nav_order: 16
parent: Guides
description: "Lessons from a real multi-agent smart contract audit — vulnerability patterns, human-agent collaboration, and a deployment checklist for Solidity projects."
---

# Smart Contract Auditing with AI Agents

What happens when one AI agent writes smart contracts, another audits them, and then the first agent audits its own fixes? This guide walks through **real findings from a multi-agent audit of 4 UUPS-upgradeable Solidity contracts** and extracts the patterns every human-agent team should know.

Use this as a reference for smart contract security, a checklist before deployment, and a process guide for running multi-agent audits.

---

## Why Smart Contracts Need Special Treatment

Smart contracts are **immutable once deployed** (upgradeable patterns add complexity, not simplicity), **adversarial by default** (anyone can call any public function), and **economically motivated** (every bug is a potential exploit worth real money). The normal "ship and patch" cycle doesn't work — you need to get it right before deployment.

AI agents are good at generating Solidity code quickly. They are bad at reasoning about adversarial environments, cross-contract consistency, and the interaction between time, pause states, and economic commitments. This guide covers exactly those gaps.

---

## The Vulnerability Taxonomy

These patterns emerged from a real audit of 4 contracts. They represent the categories of bugs that AI agents most commonly introduce or miss.

### Category A: "The Environment Is Not Your Friend"

**Pattern:** Code that works in steady-state but breaks under adversarial conditions — pausing, mempool observation, time manipulation.

**Example — Pause weaponizes time against users:**
```solidity
// ❌ Challenge window expires while contract is paused
function challengeSlash(uint256 signalId) external whenNotPaused {
    require(block.timestamp <= signal.slashedAt + 48 hours, "Window expired");
    // User can't call this during pause, but the 48h clock keeps ticking
}

// ✅ Defensive actions bypass pause
function challengeSlash(uint256 signalId) external {
    // whenNotPaused removed — users must always be able to defend themselves
    require(block.timestamp <= signal.slashedAt + 48 hours, "Window expired");
}
```

**Example — Mempool visibility enables front-running:**
```solidity
// ❌ Resolver's outcome is visible before execution
function resolve(uint256 predictionId, bool outcome) external onlyResolver {
    // 'outcome' is visible in the mempool — traders can front-run
}

// ✅ Use commit-reveal or commitment deadlines
function commitResolution(uint256 predictionId, bytes32 commitHash) external onlyResolver { }
function revealResolution(uint256 predictionId, bool outcome, bytes32 salt) external onlyResolver {
    require(keccak256(abi.encodePacked(outcome, salt)) == commitHash);
}
```

**The rule:** `whenNotPaused` is not always "safety." Classify every function:
- **Offensive actions** (stake, register, slash) — pause is appropriate
- **Defensive actions** (challenge slash, renew bond, withdraw) — pause must NOT block these
- **Settlement actions** (claim, release) — context-dependent

**Audit question:** *"For every `whenNotPaused` function, does time advancing during pause harm the caller?"*

---

### Category B: "Mutable Config, Immutable Commitments"

**Pattern:** Admin-settable parameters that retroactively change the economic terms under which users already committed funds.

**Example — Slash config changes affect inflight stakes:**
```solidity
// ❌ Slash distribution uses current globals, not values at stake time
function _computeSlash(uint256 signalId) internal {
    uint256 challengerShare = slashConfig.challengerPct; // This can change!
    // User staked when challengerPct was 30%, now it's 5%
}

// ✅ Snapshot config at commitment time
struct Signal {
    // ... existing fields ...
    uint256 snapshotChallengerPct;
    uint256 snapshotTreasuryPct;
}

function stake(uint256 amount) external {
    signal.snapshotChallengerPct = slashConfig.challengerPct;
    signal.snapshotTreasuryPct = slashConfig.treasuryPct;
}
```

**The rule:** There are two kinds of state:
- **System parameters** — can change anytime, affect future actions
- **Commitment parameters** — locked when a user stakes/deposits/bonds

If a value affects a user's payout or risk, snapshot it when they commit.

**Snapshot pitfall:** Using `value > 0` to detect "was this snapshotted?" fails when `0` is a legitimate value. Safer alternatives:
- Use a boolean flag (`bool configSnapshotted`)
- Use compound detection (`fieldA > 0 || fieldB > 0` when at least one must be non-zero)
- Use 1-indexed storage (`store value + 1`, read `value - 1`, where 0 means unset)

**When using sentinel values for "unset" detection, always verify the sentinel can never be a valid real value.**

---

### Category C: "External Calls in Critical Paths"

**Pattern:** `safeTransfer` to an external address (like treasury) inside a function that gates other users' ability to claim funds.

```solidity
// ❌ If treasury reverts, all claims are blocked
function _ensureSlashComputed(uint256 signalId) internal {
    // ... compute slash amounts ...
    token.safeTransfer(treasury, treasuryAmount); // Treasury could be a reverting contract
    // If this reverts, no one can claim their share
}

// ✅ Pull-over-push: accrue balance, let treasury withdraw later
function _ensureSlashComputed(uint256 signalId) internal {
    // ... compute slash amounts ...
    pendingTreasuryBalance += treasuryAmount; // No external call
}

function claimTreasuryFunds() external {
    uint256 amount = pendingTreasuryBalance;
    pendingTreasuryBalance = 0;
    token.safeTransfer(treasury, amount);
}
```

**The rule:** The treasury *feels* safe because it's admin-controlled, but it's still an external address that can become a contract, get blacklisted by the token, or be misconfigured. **Every `safeTransfer` to a non-`msg.sender` address in a function that other users depend on is a latent DoS vector.**

---

### Category D: "Privileged Role Abuse"

**Pattern:** Access-controlled functions without rate limiting, allowing a compromised key to cause outsized damage in a single block.

```solidity
// ❌ Compromised evaluator can drain all bonds in one block
function slash(address maker, uint256 pct) external onlyRole(QUALITY_EVALUATOR_ROLE) {
    // 20 calls × 5% = 100% of maker's bond, all in one transaction
}

// ✅ Rate-limit destructive privileged actions
mapping(address => uint256) public lastSlashAt;
uint256 public constant SLASH_COOLDOWN = 1 hours;

function slash(address maker, uint256 pct) external onlyRole(QUALITY_EVALUATOR_ROLE) {
    uint256 amount = computeSlash(maker, pct);
    require(amount > 0, "Zero slash"); // Don't consume cooldown on no-ops
    require(block.timestamp >= lastSlashAt[maker] + SLASH_COOLDOWN, "Cooldown");
    lastSlashAt[maker] = block.timestamp;
    // ... execute slash ...
}
```

**Rate-limiting pitfall:** Verify the action is substantive *before* consuming the rate-limit budget. Zero-amount slashes that consume the cooldown without actually slashing are a subtle DoS vector.

**The rule:** Access control answers "who can do this?" but not "how much damage can they do per unit time?" For every privileged destructive action, define the maximum acceptable damage rate and enforce it on-chain.

---

### Category E: "State Lifecycle Gaps"

**Pattern:** State that grows forever or reaches terminal states with no recovery path.

```solidity
// ❌ Array grows forever — getActiveDeposits becomes unbounded
function createProposal() external {
    depositorProposals[msg.sender].push(proposalId);
    // No cleanup on settlement
}

// ✅ Swap-and-pop deletion when order doesn't matter
function _removeProposal(address depositor, uint256 index) internal {
    uint256[] storage proposals = depositorProposals[depositor];
    proposals[index] = proposals[proposals.length - 1];
    proposals.pop();
}
```

```solidity
// ❌ nodeId can never be reused — lockedAt is never zeroed
function deregister(bytes32 nodeId) external {
    // lockedAt stays non-zero forever
}

function register(bytes32 nodeId) external {
    require(nodes[nodeId].lockedAt == 0, "Already registered"); // Blocks reuse
}

// ✅ Use status enum, not timestamp presence
enum NodeStatus { Unregistered, Active, Deregistered }
function register(bytes32 nodeId) external {
    require(nodes[nodeId].status == NodeStatus.Unregistered, "Not available");
}
```

**The rule:** Every piece of state needs a defined lifecycle — creation, active use, cleanup. If state is only ever added and never removed, ask: *"What happens after 10,000 operations?"*

**Upgrade pitfall:** When upgradeable contracts change data structures, old data doesn't magically appear in the new structure. Every upgrade that changes how data is tracked needs a migration plan.

---

## The Audit-of-the-Audit: What AI Auditors Get Wrong

In the real audit, a 3rd-party LLM found 10 issues. The implementing agent then independently found 7 more — including 3 bugs in the auditor's own suggested fixes. Here's what to watch for.

### What AI Auditors Do Well

1. **Systemic thinking** — cross-contract analysis, not just per-function review
2. **Adversarial role modeling** — thinking about compromised privileged keys
3. **Concrete remediation code** — copy-pasteable fixes that accelerate implementation
4. **Severity calibration** — High/Medium/Low ratings generally well-calibrated

### What AI Auditors Get Wrong

**1. False positives from ignoring attacker cost:**
An auditor flagged "front-running `lockDeposit`" as medium severity. But the attacker would lose 50 LMTS (locked and slashable) to block someone from depositing — the cost-benefit ratio makes this impractical. **Always evaluate the attacker's cost, not just the victim's loss.**

**2. Over-engineered fixes that add attack surface:**
Suggesting a shared `ProtocolRegistry` contract for treasury management across 4 contracts adds a dependency and a new single point of failure. Sometimes 4 separate `setTreasury` calls is the right answer. **Not every observation needs a code fix. Some are operational procedures.**

**3. Fix code that introduces new bugs:**
- Snapshot fallback using `value > 0 ? snapshot : global` breaks for legitimate zero values
- New setter functions without minimum/maximum validation
- Fixes applied to one contract but not sibling contracts with the same pattern

### The Stats

| Metric | Count |
|--------|-------|
| 3rd-party findings | 10 |
| Accepted and implemented | 8 |
| Rejected (false positive / over-engineered) | 2 |
| Independent findings from re-audit | 7 |
| Bugs in the 3rd-party's own fix code | 3 |
| Pre-existing issues the 3rd-party missed | 4 |
| **Total fixes implemented** | **13** |

The 3rd-party caught ~62% of total issues. The re-audit caught the remaining ~38%, including bugs introduced by the fixes themselves. **No single audit pass is sufficient for security-critical code.**

---

## The Two-Pass Audit Workflow

Based on this experience, smart contract audits should always be two passes.

### Pass 1: External Audit

A separate agent (or human auditor) reviews the contracts and proposes fixes.

**Human responsibilities:**
- Review each finding for validity — reject false positives and over-engineered suggestions
- Evaluate whether the attacker's cost justifies the severity rating
- Decide which fixes to accept before the implementing agent touches anything

### Pass 2: Self-Audit of the Fixes

The implementing agent re-audits its own changes as if it were a different auditor.

**What to check:**
1. Do any new parameters lack validation? (min/max bounds, zero-value behavior)
2. Do any new sentinel values conflict with valid values?
3. Does the same vulnerability pattern exist in sibling contracts?
4. Do the fixes introduce new edge cases?
5. Are events emitted consistently for all state-changing operations?

This two-pass approach caught 5 additional issues in the real audit, including 3 bugs in the audit's own fix code.

---

## Lessons for Human-Agent Collaboration

### For Humans Directing Agents

**1. Never apply audit fixes without a second review pass.**
Auditors provide correct *diagnoses* but subtly flawed *prescriptions*. After an agent implements fixes, always instruct it to re-audit its own changes.

**2. Require cross-contract consistency checks.**
When an agent fixes a pattern in one contract, explicitly instruct it to search for the same pattern in all related contracts. Agents fix only where told unless you say otherwise.

**3. Demand adversarial edge case analysis for every new parameter.**
Every new configurable parameter is a new attack surface. For every setter: what happens at 0? At max value? Who benefits from extreme values?

**4. Treat audit fixes as new code that needs its own tests.**
The fix's boundary conditions need test coverage, not just the happy path.

### For Agents Implementing Fixes

**1. Sentinel value detection is a footgun.**
When adding fields to structs in upgradeable contracts, the default value (0) must be distinguishable from valid values. Use boolean flags or compound detection.

**2. Rate-limiting must guard against no-ops.**
Verify the action is substantive *before* consuming the rate-limit budget.

**3. Pull-over-push is system-wide, not per-function.**
When converting one function from push to pull, find every other function in every contract that pushes to the same external address.

**4. Every `whenNotPaused` needs a justification.**
The default should be "no pause" with explicit justification for adding it.

---

## Smart Contract Audit Checklist

Use this before deployment. Every item should be explicitly verified.

### Time & Pause
- [ ] For every `whenNotPaused` function: does time advancing during pause harm the caller?
- [ ] For every deadline/window: can the user's response action be paused while the clock ticks?
- [ ] For every `block.timestamp` comparison: what happens if the contract is paused for days?

### External Calls
- [ ] For every `safeTransfer` to a non-`msg.sender`: what if the recipient reverts?
- [ ] Does any external call failure block other users' state transitions?
- [ ] Are all treasury/fee transfers using pull-over-push?

### Mutable Config
- [ ] For every admin-settable parameter: is it used in calculations for already-committed funds?
- [ ] If yes: is the value snapshotted at commitment time?
- [ ] For every setter: what happens at value = 0? At max value?
- [ ] Does the setter have minimum/maximum validation?

### Privileged Roles
- [ ] For every role: what's the maximum damage a compromised key can do in one block?
- [ ] Are destructive privileged actions rate-limited?
- [ ] Do rate limits verify the action is substantive before consuming budget?

### State Lifecycle
- [ ] For every array: is there a deletion strategy, or does it grow forever?
- [ ] For every terminal state: can the identifier be reused after reaching terminal?
- [ ] For every "existence check" (`lockedAt != 0`): does it distinguish active from historical?

### Upgradeable Contracts
- [ ] Are new struct fields appended to the END only?
- [ ] Is the storage gap decremented correctly for each new state variable?
- [ ] Do sentinel values (0 = unset) conflict with valid values?
- [ ] For new data structures: what happens to data created before the upgrade?

### Front-Running & MEV
- [ ] For every function whose parameters determine economic outcomes: can the outcome be observed in the mempool?
- [ ] Are commitment deadlines or commit-reveal schemes used where needed?
- [ ] Can transaction ordering be exploited for profit?

### Cross-Contract Consistency
- [ ] Is the same vulnerability pattern present in sibling contracts?
- [ ] If a fix is applied to one contract, has the same pattern been checked in all others?
- [ ] Do all contracts handling the same external address (treasury) use the same pattern?

### Reentrancy & Call Ordering
- [ ] Are state changes made before external calls (checks-effects-interactions)?
- [ ] Are reentrancy guards used on functions that make external calls?
- [ ] Can callback functions (ERC-721 `onERC721Received`, etc.) manipulate state unexpectedly?

---

## Prompt Templates for Smart Contract Audits

### For Implementing Audit Fixes

```
Implement the following audit fixes. After implementation, conduct your own
independent audit of the changes you made. Specifically check:
1. Do any new parameters lack validation? (min value, max value, zero behavior)
2. Do any new sentinel values conflict with valid values?
3. Does the same vulnerability pattern exist in sibling contracts?
4. Do the fixes introduce any new edge cases?
5. Are events emitted consistently for all new state-changing operations?
```

### For Reviewing 3rd-Party Audits

```
Evaluate this audit report against the actual code. For each finding:
1. Is the diagnosis correct?
2. Is the severity rating accurate?
3. Is the suggested fix correct, or does it introduce new issues?
4. What is the attacker's cost vs. the victim's loss?
5. Are there related instances of the same pattern that the auditor missed?
```

### For Pre-Deployment Audit

```
Audit these contracts assuming a hostile environment: compromised admin keys,
paused contracts, mempool-visible transactions, reverting external addresses.
For every privileged function, state the maximum damage rate.
For every user-facing function, state what can block it.
For every time-bounded action, state what happens if the contract is paused.
```

### For Cross-Contract Consistency Check

```
I just fixed [describe vulnerability] in [ContractA]. Grep for the same
pattern across all contracts in the codebase. List every instance and
confirm each is either fixed or not applicable. Specifically check:
- Same external call pattern (push-to-treasury, safeTransfer in critical paths)
- Same config mutation pattern (global state used for committed funds)
- Same pause pattern (whenNotPaused on defensive actions)
```

---

## Related Guides

- [Audit Findings & Lessons](./AUDIT_FINDINGS) — Security audit of AI-generated web/mobile apps
- [Code Review for AI-Generated Code](./CODE_REVIEW_AI) — General AI code review practices
- [Expert Panel Evaluation](../EXPERT_PANEL_EVALUATION) — Using simulated expert committees for architectural review
- [Plan-Driven Development](./PLAN_DRIVEN_DEVELOPMENT) — Structured planning workflow that reduces bugs before coding
- [Anti-Patterns & Warning Signs](./ANTI_PATTERNS) — When AI development goes wrong
