---
layout: default
title: Audit Findings & Lessons
nav_order: 5
parent: Guides
description: "Real-world security audit findings from an AI-generated mobile app — patterns to watch for in your own vibe-coded projects."
---

# Audit Findings & Lessons Learned

What happens when you actually security-audit a vibe-coded app? This guide walks through **real findings from a security audit of an AI-generated Android app** that uses the Archive.org API. Every issue here was introduced by an LLM and missed during development.

Use this as a checklist for your own projects and as evidence for why the practices in this guide matter.

---

## Audit Summary

**11 issues found and fixed** across three severity levels:

| Severity | Count | Examples |
|:---------|:------|:--------|
| **CRITICAL** | 3 | XSS via innerHTML, domain validation bypass |
| **HIGH** | 5 | Unpinned CDN, cleartext traffic, WebView open navigation |
| **MEDIUM** | 3 | Error message XSS, CSS selector injection, type confusion |

Every single issue traces back to a recognizable LLM code generation pattern.

---

## Critical Findings

### 1. XSS in Video Card Templates

**What happened**: The LLM injected `title`, `creator`, `year`, and `identifier` from the Archive.org API directly into `innerHTML` — unescaped.

**The code looked like**:
```javascript
// ❌ LLM-generated: injects API data directly into HTML
card.innerHTML = `<h3>${item.title}</h3><p>${item.creator}</p>`;
```

**The fix**:
```javascript
// ✅ Escape all dynamic content before inserting into HTML
card.innerHTML = `<h3>${escapeHtml(item.title)}</h3>
  <p>${escapeHtml(item.creator)}</p>`;
```

**The pattern**: The LLM *did* create an `escapeHtml()` utility and used it in the description field — but failed to apply it in the video card template, the favorites template, or the error display. This is the **"local fix, global miss"** pattern: the LLM solves the problem once and doesn't propagate the fix.

---

### 2. XSS in Favorites Card Templates

**What happened**: Identical to finding #1, but in the favorites rendering path. Same API data, same `innerHTML` injection, same missing `escapeHtml()`.

**Why it matters**: This confirms the "local fix, global miss" pattern. The LLM generated both templates — probably in different turns or sessions — and only applied escaping in one place.

**The fix**: Applied `escapeHtml()` and `encodeURIComponent()` consistently across all templates.

---

### 3. Domain Validation Bypass

**What happened**: The Kotlin code validated URLs with `host.contains("archive.org")`, which matches `evil-archive.org`.

**The code looked like**:
```kotlin
// ❌ LLM-generated: contains() matches substrings
if (url.host.contains("archive.org")) { /* allow */ }
```

**The fix**:
```kotlin
// ✅ Exact match + subdomain check
if (url.host == "archive.org" || url.host.endsWith(".archive.org")) { /* allow */ }
```

**The pattern**: The LLM used `contains()` as a shortcut for domain matching — a common LLM behavior that creates security bypasses. Additionally, this was originally a warn-only check; it was changed to a hard block.

---

## High Severity Findings

### 4. Unpinned CDN Dependency

**The issue**: `lucide@latest` auto-loads whatever version is current — including potentially compromised ones.

```html
<!-- ❌ @latest can silently change to any version -->
<script src="https://cdn.jsdelivr.net/npm/lucide@latest"></script>

<!-- ✅ Pin to a specific version -->
<script src="https://cdn.jsdelivr.net/npm/lucide@0.460.0"></script>
```

**The pattern**: The LLM optimized for "make it work" — `@latest` is the fastest way to get a dependency loading. Pinning versions is a production concern the LLM didn't consider.

---

### 5. Cleartext Traffic Enabled

**The issue**: `usesCleartextTraffic="true"` in the Android manifest allowed HTTP traffic, enabling man-in-the-middle attacks.

```xml
<!-- ❌ Allows unencrypted HTTP connections -->
<application android:usesCleartextTraffic="true">

<!-- ✅ Enforce HTTPS only -->
<application android:usesCleartextTraffic="false">
```

**The pattern**: Another "make it work" shortcut. During development, cleartext traffic avoids certificate issues. The LLM left it enabled for production.

---

### 6. No WebView Navigation Restriction

**The issue**: JavaScript running in the WebView could navigate to any URL — no domain allowlist.

**The fix**: Added `shouldOverrideUrlLoading` with a domain allowlist so the WebView can only navigate to approved domains.

---

### 7. Release Minification Disabled

**The issue**: `isMinifyEnabled = false` in the release build left code unobfuscated and larger than necessary.

**The fix**: Enabled minification for release builds.

---

### 8. WebView Domain Allowlist Bypass

**The issue**: Same pattern as finding #3 — `endsWith("archive.org")` matched `evilarchive.org`.

```kotlin
// ❌ endsWith matches without dot boundary
if (url.host.endsWith("archive.org")) { /* allow */ }

// ✅ Exact match + dot-prefix for subdomains
if (url.host == "archive.org" || url.host.endsWith(".archive.org")) { /* allow */ }
```

**The pattern**: The same domain validation mistake appeared in two different locations — the LLM repeated the error because it follows the same shortcuts consistently.

---

## Medium Severity Findings

### 9. Error Message XSS

**The issue**: `error.message` injected into `innerHTML` unescaped. An attacker controlling the error message gets script execution.

**The fix**: Applied `escapeHtml()` to error messages before rendering.

---

### 10. CSS Selector Injection

**The issue**: `querySelector` called with a user-controlled `data-id` value without escaping.

```javascript
// ❌ User-controlled value in CSS selector
document.querySelector(`[data-id="${item.identifier}"]`);

// ✅ Escape the value for use in CSS selectors
document.querySelector(`[data-id="${CSS.escape(item.identifier)}"]`);
```

---

### 11. localStorage Type Confusion

**The issue**: `JSON.parse` result from `localStorage` was assumed to be an array without validation.

```javascript
// ❌ Assumes parsed result is always an array
const favorites = JSON.parse(localStorage.getItem('favorites'));
favorites.forEach(/* ... */);

// ✅ Validate the parsed type
const parsed = JSON.parse(localStorage.getItem('favorites'));
const favorites = Array.isArray(parsed) ? parsed : [];
```

---

## LLM Code Pattern Root Causes

These 11 findings share three root causes that are characteristic of LLM-generated code:

### Root Cause 1: "Local Fix, Global Miss"

The LLM created `escapeHtml()` and used it in one place — but failed to apply it consistently across all templates. When an LLM "learns" a fix during generation, it applies it locally but doesn't propagate it to all affected code paths.

**What to do about it**:
- After finding any security issue, **grep the entire codebase** for the same pattern
- Don't fix the instance — fix the class of bugs
- See [Anti-Pattern: Fix One, Miss Ten](./ANTI_PATTERNS.md#anti-pattern-fix-one-miss-ten)

### Root Cause 2: Shortcut Matching

The LLM used `contains()` and `endsWith()` instead of proper domain matching with dot boundaries. These are common LLM shortcuts that look correct but create bypasses:

| LLM Shortcut | What It Matches | Correct Approach |
|:-------------|:----------------|:-----------------|
| `host.contains("archive.org")` | `evil-archive.org` | Exact match + `.archive.org` |
| `host.endsWith("archive.org")` | `evilarchive.org` | Exact match + `.archive.org` |
| `url.includes("api.example.com")` | `api.example.com.evil.com` | Parse URL, check host |

**What to do about it**:
- Review all string-based security checks (domain validation, path checks, origin checks)
- Use exact matching with explicit subdomain handling
- Never use substring matching for security-critical comparisons

### Root Cause 3: "Make It Work" Over "Make It Secure"

The `@latest` CDN tag, `usesCleartextTraffic="true"`, and disabled minification all share a pattern: the LLM optimized for getting the code running, not for production readiness.

**What to do about it**:
- Include security requirements in your initial prompt: *"This code must be production-ready with no cleartext traffic, pinned dependencies, and minification enabled"*
- Run a security-focused review before any release
- Use the [Security Bug Hunt prompt]({{ site.baseurl }}/prompts/bug-hunt) regularly

---

## Audit Checklist for Vibe-Coded Projects

Use this checklist before shipping any AI-generated project:

### Output Handling
- [ ] All dynamic content escaped before insertion into HTML (`escapeHtml()`)
- [ ] All user/API-controlled values escaped in CSS selectors (`CSS.escape()`)
- [ ] No raw `innerHTML` with unescaped external data
- [ ] Error messages escaped before display

### Domain & URL Validation
- [ ] Domain checks use exact match + dot-prefix (not `contains()` or `endsWith()`)
- [ ] WebView navigation restricted to allowlisted domains
- [ ] URL parsing uses proper URL/URI classes, not string matching

### Dependencies & Transport
- [ ] All CDN dependencies pinned to specific versions (no `@latest`)
- [ ] Cleartext traffic disabled (`usesCleartextTraffic="false"`)
- [ ] HTTPS enforced for all external requests

### Build & Release
- [ ] Minification enabled for release builds
- [ ] Debug flags disabled in production
- [ ] No development-only permissions left in production manifests

### Data Handling
- [ ] `JSON.parse` results validated before use (`Array.isArray()`, type checks)
- [ ] localStorage/sessionStorage data treated as untrusted
- [ ] API responses validated against expected schema

---

## How to Apply These Lessons

### During Development

Include these requirements in your prompts:
```
Security requirements:
- Escape all dynamic content before innerHTML insertion
- Use exact domain matching (no contains/endsWith for hosts)
- Pin all CDN dependencies to specific versions
- Validate all parsed data types before use
- No cleartext traffic in production
```

### During Code Review

After each AI-generated feature, run:
```
Review this code for the following LLM security patterns:
1. Unescaped dynamic content in innerHTML
2. String-based domain validation (contains, endsWith, includes)
3. Unpinned dependencies (@latest, unversioned CDN links)
4. Missing type validation after JSON.parse
5. Development-only settings left enabled (cleartext, debug flags)
```

### Before Release

Run a full audit using the checklist above. The patterns are predictable — if the LLM made one of these mistakes, it probably made several.

---

## Key Takeaway

> **LLMs make security mistakes in predictable patterns.** Once you know the patterns, you can catch them systematically. The audit found 11 issues, but they reduced to just 3 root causes. Learn the root causes, and you'll catch the issues before they ship.

---

## Related Guides

- [Anti-Patterns & Warning Signs](./ANTI_PATTERNS.md) — Broader patterns of AI development going wrong
- [Code Review for AI-Generated Code](./CODE_REVIEW_AI.md) — How to review AI outputs effectively
- [Automation & Testing](./AUTOMATION_TESTING.md) — Automated quality gates
- [API Key & Secrets Security](./API_KEY_SECURITY.md) — Keeping secrets out of frontend code
