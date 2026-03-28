---
layout: default
title: "When AI Audits Go Wrong"
nav_order: 6
parent: Guides
description: "A real incident where an AI auditor, an AI fixer, and a git baseline disagreement sent everyone chasing a phantom problem — and the layered lessons it revealed."
---

# When AI Audits Go Wrong: A Four-Act Debugging Story
### *Trust the Diff*

What happens when you use one AI to fix code and another AI to review those fixes? This guide documents a real incident that unfolded in four acts, each revealing a different failure mode. Every person and every AI involved was acting in good faith. Everyone was wrong about something.

---

## Act 1: The Accusation

A developer used a security audit prompt from this guide to scan a Discord bot codebase they hadn't worked on before. The fixing agent found 13 real bugs, fixed them, and generated professional documentation — an IMPLEMENTATION_PLAN.md and CHANGELOG.md.

A second AI agent was then used to review the fix branch. It produced a confident, well-formatted report claiming the fix branch had made **undocumented destructive changes**:

> But buried in the same branch, alongside those fixes, there are **undocumented changes that silently downgrade the bot:**
>
> - **Deleted 7 of your developer KB entries** (signing, SDKs, orders, claiming, market-types, smart-wallet-signer, claim-winnings) — hours of your work, gone without mention
> - **Removed ~120 phrase hints** that help the resolver match real user questions
> - **Removed the retry logic** for Claude API calls
> - **Removed the hallucinated URL filter**
> - **Removed prompt instructions** that told Claude to ask one question at a time
> - **Removed your PID guard** that prevents two bot instances from running
>
> None of these removals appear in the CHANGELOG or IMPLEMENTATION_PLAN.

The report was specific, authoritative, and alarming. The developer and the bot maintainer both believed it. The developer apologized to the maintainer. Everyone agreed: don't merge that branch.

**Lesson 1: A confident, well-formatted AI report is not evidence.** The auditing agent produced something that *looked* like a thorough code review. It had bold text, bullet points, specific file names, and a clear recommendation. It was convincing enough that two humans accepted it without verification.

---

## Act 2: The Defense

When confronted, the fixing agent ran actual `git diff` commands against the branch's merge-base and showed:

| Auditor's Claim | Actual Diff |
|:----------------|:------------|
| "Deleted 7 developer KB entries" | `knowledge.py` was not modified — zero diff |
| "Removed ~120 phrase hints" | `resolver.py` had 1 line changed (a duplicate typo fix) |
| "Removed retry logic" | No retry logic was touched anywhere |
| "Removed hallucinated URL filter" | No URL filter was touched |
| "Removed prompt instructions" | `SYSTEM_PROMPT` was untouched |
| "Removed PID guard" | No PID guard was touched |

The fixing agent then searched the entire codebase for the "deleted" features and found that **several of them had never existed at all** — no retry logic, no URL filter, no PID guard anywhere in the codebase. Some KB entry names the auditor listed (signing, smart-wallet-signer, claim-winnings, market-types) returned zero matches.

The fixing agent's conclusion: the auditing agent hallucinated. It invented features a Discord bot *should* have, noticed they were absent, and blamed the fix branch.

**Lesson 2: An AI defending itself with `git diff` output is more credible than an AI making narrative claims — but "more credible" doesn't mean "right."** The fixing agent showed real command output instead of just asserting innocence. That's better evidence. But as Act 3 reveals, even correct evidence can support the wrong conclusion.

---

## Act 3: The Truth

When someone finally ran `git log` on the current `main` branch, the full picture emerged:

```
88b3ad2  2026-03-27  Add 15 new KB topics for prediction market user questions
a8bcab9  2026-03-27  Merge fix/clean-security-fixes: 12 security and correctness fixes
726bf74  2026-03-27  Fix security, correctness, and cleanup issues from code review
6b9e22c  2026-03-26  Add retry logic, PID guard, developer KB entries, and resolver improvements
39f9ca5  (branch point)
```

After the fix branch was created from commit `39f9ca5`, the maintainer pushed new commits to `main` that **added** the retry logic, PID guard, KB entries, and phrase hints. These features didn't exist when the fix branch was created.

**Both agents were "correct" from their own perspective:**

- The **auditing agent** compared the fix branch against **current `main`** and correctly noted that features present on `main` were absent from the branch. But it reported this as "the branch deleted these features" when actually "the branch predates these features."

- The **fixing agent** compared against the **merge-base** (the point where it branched) and correctly showed it hadn't deleted anything. But it went further and claimed the auditor "hallucinated" features that actually did exist — just on a different commit.

**The real bug was a baseline comparison error.** The auditing agent used the wrong reference point. In git terms, it did `git diff main..branch` (which includes changes to main since branching) instead of `git diff main...branch` (which shows only the branch's changes). This is a mistake even experienced human developers make.

**Lesson 3: When two AIs disagree, the answer is usually in the data, not in either AI's narrative.** Neither agent lied. Neither hallucinated in the traditional sense. They were looking at different baselines and both reporting accurately on what they saw. The human needed to check `git log` to understand why.

---

## Act 4: The Resolution

With the root cause identified, the fix was straightforward: rebase the fix branch onto current `main` so it included the maintainer's new features.

```
$ git rebase origin/main
CONFLICT (content): Merge conflict in chat_engine.py
CONFLICT (content): Merge conflict in rag.py
```

Two merge conflicts appeared — exactly where the fix branch and the maintainer's commits had touched the same code:

1. **rag.py**: The maintainer had changed the resolution order (`user_text` first, then `expanded`). The fix branch had added a `match=` parameter to the same function calls. The correct resolution: keep the maintainer's ordering AND the fix branch's `match=` parameter.

2. **chat_engine.py**: A trivial trailing whitespace conflict at the end of the file.

After resolving and pushing, the diff told the real story:

```
# Before rebase (against current main): ~900 lines changed, "massive deletions"
# After rebase (against current main): 29 lines changed across 2 files
```

The fix branch went from looking destructive to looking like what it actually was: a small, focused set of remaining fixes. Most of the original 13 findings had already been independently applied by the maintainer in commit `726bf74` — which meant the audit findings were genuinely valid. The fix branch's work had real value; the maintainer had simply gotten there first for most of them.

**Lesson 4: The rebase proved the diagnosis.** When the diff shrinks from 900 lines to 29 after rebasing onto current main, it confirms the "deletions" were just branch divergence. This is the fastest way to verify a baseline comparison error — rebase and see if the alarming diff disappears.

### A Note on Merge Conflicts as Evidence

The merge conflicts themselves were informative. They appeared in `rag.py` and `chat_engine.py` — exactly the files where both the fix branch and the maintainer's commits had made changes. The conflicts showed that the maintainer and the fixing agent had independently identified and fixed some of the same issues, which is strong evidence that the 13 audit findings were legitimate.

When a human resolves merge conflicts, they're doing something no AI in this story did: looking at both versions simultaneously and making a judgment call about how to combine them. The `rag.py` resolution — keeping the maintainer's resolution order while adding the fix branch's `match=` parameter — required understanding the intent of both changes. This is the kind of nuanced decision that justified having a human in the loop.

---

## The Three Layers of Failure

This incident stacks three distinct failure modes, each worth understanding independently:

### Layer 1: Trusting AI-Generated Reports Without Verification

The auditing agent's report was accepted because it was:
- **Specific** — it named exact files and features
- **Well-formatted** — bold text, bullet points, clear recommendations
- **Alarming** — it triggered urgency ("don't merge this!")
- **Plausible** — the claims sounded like things an AI fixer *could* do

None of these qualities correlate with accuracy. A hallucinated report can have all four.

**Mitigation**: Treat AI audit reports the same way you treat AI-generated code — as a starting point that requires human verification. Run the diffs yourself.

### Layer 2: Wrong Baseline in Code Comparison

The auditing agent compared the fix branch against the current tip of `main`, not the merge-base. This made features added to `main` after branching look like deletions by the branch.

**Mitigation**: Always use three-dot diff for branch reviews:

```bash
# WRONG: includes changes made to main since branching
git diff main..feature-branch

# RIGHT: shows only the branch's changes relative to where it diverged
git diff main...feature-branch

# Or explicitly find the merge-base
git diff $(git merge-base main feature-branch)..feature-branch
```

When instructing an AI to review a branch, be explicit:

```markdown
Compare this branch against its merge-base with main, not against the
current tip of main. Use `git merge-base main <branch>` to find the
correct comparison point.
```

### Layer 3: AI Agents Debugging Each Other in Circles

The incident spawned a recursive debugging loop:
1. Agent A reviews Agent B's work and claims it's destructive
2. Agent B defends itself and claims Agent A hallucinated
3. A third agent (reviewing the conversation) initially sides with Agent A
4. Agent B presents evidence and the third agent switches sides
5. Eventually a human checks `git log` and finds the real answer

At no point did any AI say "I'm not sure — let me check the commit history to understand the timeline." Each agent was confident in its own framing.

**Mitigation**: When AIs disagree about facts, don't ask another AI to arbitrate. Check the primary source yourself. In this case, `git log --oneline main` would have resolved the disagreement in seconds.

---

## Prevention Playbook

### For AI-Assisted Security Audits

1. **Two-phase approach**: Have the agent report findings first (no changes), then fix them in a separate step
2. **Specify the baseline**: Tell the auditing agent to compare against the merge-base, not current main
3. **Scope narrowly**: "Fix only the issues in this audit report" prevents scope creep
4. **Atomic commits**: One commit per fix makes review trivial

### For AI-Generated Code Reviews

1. **Verify claims against diffs**: If the reviewer says something was deleted, check the diff yourself
2. **Check the timeline**: Were features added to main after the branch was created?
3. **Be skeptical of alarm**: Urgent-sounding findings get accepted without scrutiny — slow down
4. **Specify comparison method**: Include `git diff main...<branch>` (three-dot) in your review prompt

### For Codebases Without Guardrails

Before pointing any AI agent at a codebase — for fixing OR reviewing — add:

**CLAUDE.md**:
```markdown
## Rules
- Never delete existing features without explicit approval
- Document ALL changes in commit messages — additions AND deletions
- Only modify code directly related to identified issues
- Flag anything questionable for human review instead of changing it
```

**INVARIANTS.md**:
```markdown
## Protected Components
[List the features, data, and configurations that must not be modified
without explicit approval]
```

These files won't prevent comparison errors, but they give both fixing and auditing agents better context about what's intentional.

---

## Checklist: Reviewing AI-Generated Audit Reports

- [ ] Did the auditor specify what baseline it compared against?
- [ ] Run `git diff --stat main...<branch>` yourself — does it match the audit's claims?
- [ ] For each claimed deletion: is the feature present on main at the **merge-base**, or was it added later?
- [ ] Run `git log main` to check for commits made after the branch was created
- [ ] If two AIs disagree, check primary sources (`git log`, `git diff`) instead of asking a third AI
- [ ] Treat the audit report as a hypothesis to verify, not a conclusion to act on

---

## Checklist: Reviewing AI-Generated Fix Branches

- [ ] Read the AI's documentation (CHANGELOG, IMPLEMENTATION_PLAN, PR description)
- [ ] Run `git diff --stat` against the **merge-base** — do modified files match the documented changes?
- [ ] Run full `git diff` — are there deletions not explained by documented fixes?
- [ ] Count lines removed vs added — is the ratio reasonable for "bug fixes"?
- [ ] Check for deleted files or large removed blocks
- [ ] Verify no knowledge base entries, training data, or configuration was removed
- [ ] Confirm protective mechanisms (retry logic, rate limits, guards) still exist
- [ ] Test the application after applying changes — does existing functionality still work?

---

## The Meta-Lesson

People are learning not to blindly trust AI-generated code. That's good. But **blindly trusting AI-generated reviews of code is the same mistake one layer up.**

The auditing agent did exactly what this guide warns about: it produced a confident, well-formatted, professional-looking document that was convincing enough to skip verification. The only difference was that it was an audit report instead of a changelog.

Every practice in this guide — verify claims, check diffs, don't trust summaries — applies equally to AI-generated code AND AI-generated reviews of code. The format of the output (code vs. prose) doesn't change the need for human verification.

**Trust the diff. Question the narrative. Verify the baseline.**

---

## Questions for Investigation

<!--
INSTRUCTIONS FOR THE DEVELOPER:
These questions are designed to be asked to the AI agents involved in the
incident (both the fixer and the auditor). Have each agent answer its
relevant questions directly in this document, then review what they say.
-->

### For the Auditing Agent

1. **What baseline did you compare the fix branch against?** Did you use `git diff main..branch` (two-dot) or `git diff main...branch` (three-dot)? Were you aware of the difference?

2. **Did you check `git log` to understand the commit timeline?** Specifically, did you verify that the features you flagged as "deleted" existed at the point the branch was created?

3. **How confident were you in the claim that features were "deleted"?** Did you consider the possibility that the branch simply predated those features?

4. **What would have changed your report?** If the branch had included a note saying "branched from commit 39f9ca5," would you have compared against that commit instead?

### For the Fixing Agent

5. **When you defended yourself, did you consider that new commits might have been pushed to main?** Or did you assume main was static from the point you branched?

6. **You claimed several features "never existed" — but they existed on current main.** Did you search only your branch, or also search main? What led you to conclude the auditor was hallucinating rather than comparing against a different baseline?

7. **If you had fetched current main before responding, would you have understood the discrepancy sooner?**

### For Both Agents

8. **At any point, did you feel uncertain about your conclusions?** If so, did you communicate that uncertainty, or did you present your conclusions as definitive?

9. **What would have prevented this entire incident?** From your perspective, what single change to the process would have caught the baseline error before it spiraled?

---

## Related Guides

- [Audit Findings & Lessons](AUDIT_FINDINGS.html) — Real findings from a security audit of an AI-generated app
- [Code Review for AI](CODE_REVIEW_AI.html) — Review practices specific to AI-generated code
- [Anti-Patterns & Warning Signs](ANTI_PATTERNS.html) — Recognize when AI development goes wrong
- [Plan-Driven Development](PLAN_DRIVEN_DEVELOPMENT.html) — Why planning before coding prevents scope creep
- [Version Control Best Practices](VERSION_CONTROL.html) — Git workflow for AI-assisted development

---

*This guide is based on a real incident involving three AI agents and two humans. Nobody acted in bad faith. Everyone was wrong about something. The commit history was right the whole time.*
