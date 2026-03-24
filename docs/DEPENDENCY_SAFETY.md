---
layout: default
title: Dependency Safety
nav_order: 11
parent: Guides
description: "How to evaluate, vet, and manage dependencies when an LLM is suggesting your packages — covering hallucinated packages, supply chain risks, and the discipline of saying no."
permalink: /dependency-safety
---

# Dependency Safety: When the AI Picks Your Packages

Every time you ask an LLM to build something, it will suggest packages. Sometimes three. Sometimes twelve. It does this confidently, quickly, and without checking whether the package exists, is maintained, or is safe. Your `package.json` or `requirements.txt` is the attack surface it grows fastest.

This guide covers how to evaluate what the AI suggests, what can go wrong when you don't, and the habits that keep your dependency tree from becoming a liability.

---

## Table of Contents

1. [Why This Matters More with AI](#why-this-matters-more-with-ai)
2. [The Three Ways AI Gets Dependencies Wrong](#the-three-ways-ai-gets-dependencies-wrong)
3. [Evaluating a Suggested Package](#evaluating-a-suggested-package)
4. [The "Do You Even Need This?" Check](#the-do-you-even-need-this-check)
5. [Hallucinated Packages and Supply Chain Attacks](#hallucinated-packages-and-supply-chain-attacks)
6. [Pinning, Lockfiles, and Version Discipline](#pinning-lockfiles-and-version-discipline)
7. [CDN Dependencies](#cdn-dependencies)
8. [Automated Scanning Is Not Enough](#automated-scanning-is-not-enough)
9. [What to Put in Your CLAUDE.md](#what-to-put-in-your-claudemd)
10. [Checklist](#checklist)

---

## Why This Matters More with AI

A human developer adding a dependency typically:
- Searches for options, reads comparisons, checks GitHub stars and issues
- Evaluates whether the dependency is necessary or if the standard library suffices
- Reads at least part of the README before installing
- Notices if a package name looks wrong or unfamiliar

An LLM adding a dependency does none of this. It generates the `npm install` or `pip install` command from training data patterns. It doesn't verify the package exists on the registry at the time of suggestion. It doesn't check download counts, maintenance status, or known vulnerabilities. It recommends what *sounds right* based on what it's seen in training data.

This creates three categories of risk that don't exist (or are much rarer) when humans choose dependencies.

---

## The Three Ways AI Gets Dependencies Wrong

### 1. Suggesting packages that don't exist

LLMs hallucinate package names. They combine real library names into plausible-sounding but nonexistent packages: `react-auth-helper`, `flask-security-utils`, `express-jwt-validator`. These names feel right. They follow naming conventions. They don't exist.

The danger isn't just a failed install. Attackers monitor LLM outputs and register packages with commonly hallucinated names. This is a documented attack vector — researchers have demonstrated it by publishing typosquat packages that received thousands of downloads from developers (and CI systems) following AI suggestions.

### 2. Suggesting abandoned or deprecated packages

LLMs recommend packages that were popular in their training data but are now unmaintained. A package last updated in 2021 may have known CVEs, incompatible peer dependencies, or simply not work with current language versions. The AI doesn't know the package is dead — it only knows it was widely used.

### 3. Suggesting heavy packages for simple tasks

LLMs default to packages they've seen most often in training data, not the simplest solution. This leads to pulling in `moment.js` (295KB) for a single date format, `lodash` for one array operation, or a full ORM when a query builder (or raw SQL) would suffice. Each unnecessary dependency adds to your bundle size, attack surface, and maintenance burden.

---

## Evaluating a Suggested Package

When the AI suggests a package, run through this evaluation before installing. It takes 60 seconds and prevents problems that take hours to fix.

### The 60-Second Check

| Check | Where to look | Red flag |
|-------|--------------|----------|
| **Does it exist?** | Search the registry (npmjs.com, pypi.org) | No results, or the result doesn't match what the AI described |
| **Weekly downloads** | Registry page | Under 1,000/week for a general-purpose package |
| **Last published** | Registry page | More than 12 months ago |
| **Open issues / PRs** | GitHub repo | Hundreds of open issues with no maintainer response |
| **Maintainer count** | Registry page or GitHub | Single maintainer with no activity |
| **License** | `package.json`, `setup.py`, or LICENSE file | No license, or license incompatible with your project |
| **Dependencies** | Registry page | More transitive dependencies than the package seems to warrant |
| **Bundle size** | bundlephobia.com (JS) | Disproportionate to what you're using it for |

### When to dig deeper

The 60-second check catches obvious problems. Dig deeper when:
- The package has `install` or `postinstall` scripts (check `package.json`)
- The package requests permissions beyond its stated purpose
- The package has a suspiciously recent publish date with a name that's close to a popular package
- The package is a transitive dependency you didn't explicitly choose — review your lockfile after installation

### Framework-specific guidance

**JavaScript/TypeScript:**
- Prefer packages in the `@types/*` namespace for type definitions over unscoped alternatives
- Check if the functionality exists in Node.js built-ins before adding a package (`fs/promises`, `crypto`, `url`, `path` cover more than most developers realize)
- For utility functions, check if your existing framework already provides them (Next.js, Nuxt, and Remix bundle many common utilities)

**Python:**
- The standard library is large — `pathlib`, `dataclasses`, `itertools`, `collections`, `json`, `csv`, `urllib`, `http.server` handle many common tasks
- Prefer packages with type stubs available (`types-*` on PyPI or inline types)
- Check if the package is on the [PSF's list of known malicious packages](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/) periodically

---

## The "Do You Even Need This?" Check

This is the most important section in this guide. The best dependency is the one you don't add.

### Ask the AI to solve it without the package first

Before accepting a package suggestion, try this:

> "Implement this using only the standard library and our existing dependencies. No new packages."

You'll find that the AI can often produce a clean, working implementation in 10-30 lines that does exactly what the suggested package does — for your specific use case. The package handles 500 edge cases you'll never encounter. Your 20-line implementation handles the 3 cases you actually need.

### The decision framework

| Situation | Add the dependency | Write it yourself |
|-----------|:-:|:-:|
| Complex, well-defined domain (crypto, image processing, PDF generation) | Yes | No |
| Simple utility (slugify, debounce, deep clone) | No | Yes |
| Standard protocol implementation (OAuth, JWT, WebSocket) | Yes | No |
| Data formatting (date display, number formatting) | Maybe | Usually |
| Thin wrapper around a built-in | No | Yes |
| Active ecosystem with security implications (auth, encryption) | Yes | No |

### The rule

**If you can write it in under 50 lines, understand every line, and it doesn't involve cryptography or security protocols — write it yourself.**

Every dependency you avoid is one fewer supply chain risk, one fewer version conflict, one fewer abandoned package to replace in two years.

---

## Hallucinated Packages and Supply Chain Attacks

### How the attack works

1. Researchers (and attackers) prompt popular LLMs with coding questions
2. They collect the package names the LLMs suggest that *don't actually exist*
3. They register those names on npm, PyPI, or other registries
4. They publish packages with those names containing malicious code (data exfiltration, credential theft, cryptominers)
5. Developers or CI systems following AI suggestions install the package
6. The malicious code executes during installation or import

This isn't theoretical. In 2024-2025, multiple research papers documented this attack vector, and real malicious packages were found on registries with names matching common LLM hallucinations.

### How to protect yourself

**Always verify the package exists before installing.** Open the registry page. Read the description. Check it matches what the AI described. This single step defeats the entire attack.

**Never run AI-generated install commands blindly.** When the AI outputs `npm install super-auth-validator`, don't paste it into your terminal. Search for `super-auth-validator` on npmjs.com first. If it doesn't exist, or it exists but has 12 downloads and was published yesterday, don't install it.

**Use lockfiles and review lockfile changes.** Your `package-lock.json` or `poetry.lock` records exactly what was installed, including transitive dependencies. Review lockfile diffs in PRs — a new package appearing that nobody explicitly added is a signal worth investigating.

**Set up a pre-install verification step.** For teams, consider a policy where new dependencies require a brief justification in the PR description: what it does, why it's needed, and confirmation that it was verified on the registry.

---

## Pinning, Lockfiles, and Version Discipline

### Why AI-generated code uses loose versions

LLMs generate version ranges (`^`, `~`, `>=`) or no version at all because that's what they've seen most often in training data. Tutorials use `npm install express` without a version. Blog posts use `pip install flask`. The AI follows the same pattern.

Loose versions are fine for tutorials. They're dangerous in production code.

### What to pin

| File | What to do |
|------|-----------|
| `package.json` / `requirements.txt` | Use exact versions for direct dependencies (`"express": "4.18.2"`, `flask==3.0.0`) |
| `package-lock.json` / `poetry.lock` / `yarn.lock` | Commit to version control — always |
| CI/CD workflows | Pin action versions to full SHA, not tags (`actions/checkout@a5ac7e51...` not `actions/checkout@v4`) |
| Dockerfiles | Pin base images to digest (`node@sha256:abc123...` not `node:20`) |

### Why lockfiles matter more than you think

A lockfile records the exact version of every dependency (including transitive ones) that was installed. Without it, `npm install` or `pip install` resolves to whatever the latest compatible version is *at that moment*. Two developers running the same install command on different days get different dependency trees.

**Commit your lockfiles. Always.** When the AI generates a project scaffold, it often includes a `.gitignore` that excludes lockfiles. Remove that exclusion.

### Reviewing lockfile changes

When a PR modifies a lockfile, look for:
- **New packages you didn't ask for** — transitive dependencies pulled in by the new package. How many? Are any of them suspicious?
- **Version changes in unrelated packages** — a resolution change that updated something you didn't intend to update
- **Removed packages** — make sure nothing was accidentally dropped

---

## CDN Dependencies

When building frontend projects, LLMs frequently suggest loading libraries from CDNs. This has specific risks beyond what npm/pip dependencies face.

### The @latest problem

LLMs consistently generate CDN links with `@latest`:

```html
<!-- ❌ This can change to ANY version at ANY time -->
<script src="https://cdn.jsdelivr.net/npm/library@latest/dist/lib.min.js"></script>

<!-- ✅ Pin to specific version -->
<script src="https://cdn.jsdelivr.net/npm/library@1.2.3/dist/lib.min.js"></script>
```

Using `@latest` means your production site will automatically load a new version the moment it's published — including versions with breaking changes or compromised code. You will not be notified. Your tests will not catch it (they run against installed, not CDN-fetched code). Your site will simply break or be compromised silently.

### Subresource Integrity (SRI)

For any CDN-loaded resource, add SRI hashes:

```html
<script
  src="https://cdn.jsdelivr.net/npm/library@1.2.3/dist/lib.min.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8w"
  crossorigin="anonymous">
</script>
```

SRI ensures the browser will refuse to execute the script if its content changes. If the CDN is compromised or the file is modified, the script simply won't load instead of executing malicious code.

**LLMs never add SRI hashes.** This is one check you'll always need to add manually.

### When to self-host instead

If a library is critical to your application, consider bundling it into your build rather than loading from a CDN. This eliminates CDN availability as a dependency and gives you full control over what code runs. The performance benefit of CDNs is real but smaller than it once was, and the security tradeoff is worth evaluating.

---

## Automated Scanning Is Not Enough

The [Automation & Testing guide](./AUTOMATION_TESTING.md) covers setting up Dependabot, `npm audit`, `pip-audit`, and other scanning tools. These tools are necessary — use them. But they only catch *known vulnerabilities in existing packages*.

Automated scanning does **not** catch:
- Packages that don't exist (hallucinated names)
- Packages that exist but are malicious and haven't been reported yet
- Packages that are simply unnecessary bloat
- Packages that are abandoned but not yet vulnerable
- License incompatibilities (unless you add a separate license scanner)

**Scanning is the safety net. Human evaluation is the tightrope walk.** Both are needed, but don't let the existence of scanning tools make you complacent about what gets installed in the first place.

---

## What to Put in Your CLAUDE.md

Adding dependency guidance to your project's `CLAUDE.md` (or equivalent context file) prevents the AI from making bad suggestions in the first place.

```markdown
## Dependencies

### Rules
- Do NOT add new dependencies without explicit approval
- Always check if the standard library or existing dependencies can solve the problem first
- When suggesting a new dependency, include: name, purpose, weekly downloads, last publish date
- Pin all versions exactly (no ^ or ~ prefixes)
- Never use @latest for CDN links

### Existing dependencies (use these before adding new ones)
- date-fns: date formatting and manipulation (do NOT suggest moment.js or dayjs)
- zod: schema validation (do NOT suggest joi or yup)
- [list your actual dependencies and their purposes]

### Banned packages
- moment.js (deprecated, use date-fns)
- request (deprecated, use native fetch)
- [any packages you've decided against and why]
```

This approach works because it gives the AI specific alternatives instead of just prohibitions. Saying "use date-fns for dates" is more effective than "don't use moment.js" — the AI needs a path forward, not just a wall.

---

## Checklist

### Before installing any AI-suggested package

- [ ] Verified the package exists on the registry (npmjs.com, pypi.org)
- [ ] Checked weekly downloads (>1,000 for general-purpose packages)
- [ ] Confirmed the package was published within the last 12 months
- [ ] Reviewed the GitHub repo for maintenance activity
- [ ] Confirmed the license is compatible with your project
- [ ] Checked that you actually need the package (can you write it in <50 lines?)
- [ ] Asked the AI to implement it without the package first

### Version discipline

- [ ] All direct dependencies use exact versions
- [ ] Lockfile is committed to version control
- [ ] CDN links use pinned versions (no `@latest`)
- [ ] CDN links include SRI hashes
- [ ] CI/CD action versions are pinned to full SHA

### Project setup

- [ ] CLAUDE.md includes dependency rules and preferred packages
- [ ] Dependabot or Renovate is configured for automated vulnerability alerts
- [ ] `npm audit` or `pip-audit` runs in CI
- [ ] New dependency additions require justification in PR description
- [ ] `.gitignore` does NOT exclude lockfiles

### Ongoing maintenance

- [ ] Review lockfile diffs in PRs for unexpected additions
- [ ] Audit transitive dependencies periodically (quarterly minimum)
- [ ] Remove unused dependencies when features are removed
- [ ] Update pinned versions deliberately, not automatically
- [ ] Check for hallucinated package names before every install

---

## Related Guides

- **[Automation & Testing](./AUTOMATION_TESTING.md)** — Covers the tooling side: Dependabot configuration, `npm audit` in CI, and security scanning pipelines. This guide covers the decision-making that happens *before* those tools run.
- **[Audit Findings & Lessons](./AUDIT_FINDINGS.md)** — Documents real findings including unpinned CDN dependencies. The `@latest` pattern described there is one specific instance of the broader dependency safety problem covered here.
- **[Anti-Patterns & Warning Signs](./ANTI_PATTERNS.md)** — The "Framework Fever" anti-pattern is the dependency equivalent of over-engineering. When the AI suggests a framework for a simple problem, the dependency evaluation in this guide helps you decide whether to accept or push back.
- **[Code Review for AI](./CODE_REVIEW_AI.md)** — Includes a dependency checklist (section 10) for code review. This guide provides the background knowledge that makes those checklist items actionable.
