---
layout: default
title: After the Merge
parent: Guides
nav_order: 14
description: "Deployment, monitoring, and production readiness for AI-generated code."
---

# After the Merge: Deployment & Production for AI-Generated Code

Every other guide in this series focuses on getting code right *before* it ships. This guide covers what happens next — deploying, observing, and operating AI-generated code in production. The patterns here aren't unique to AI code, but AI code fails in specific, predictable ways that demand specific attention.

---

## Why AI Code Needs Extra Production Discipline

AI-generated code has three properties that make production failures more likely:

1. **Optimized for "works on my machine."** LLMs produce code that passes the test you asked for, not code that survives real traffic. Default-insecure configurations, missing timeouts, and absent rate limiting are the norm, not the exception (see [Audit Findings](./AUDIT_FINDINGS.md)).

2. **Implicit contracts between modules.** Code generated across multiple sessions often agrees on interfaces only superficially. The bugs live in edge cases: missing fields, mismatched types, or assumptions that hold in test data but not production data (see [Refactoring with AI — Silent Contract Changes](./REFACTORING_WITH_AI.md#failure-mode-5-silent-contract-changes)).

3. **Confidence without comprehension.** The developer who wrote zero lines of a module may not recognize when it's failing subtly. Monitoring and alerting fill this gap.

---

## The Pre-Deployment Checklist

Run this *after* tests pass and *before* the first real deployment. Most items are one-time setup; some recur with each deploy.

### Environment & Configuration

- [ ] No hardcoded secrets, URLs, or environment-specific values in source (see [API Key Security](./API_KEY_SECURITY.md))
- [ ] Environment variables documented and present in the target environment
- [ ] Fail-fast on missing required config — no silent defaults in production (see [API Key Security — Fail-Fast](./API_KEY_SECURITY.md#6-fail-fast-on-missing-config))
- [ ] Debug flags, verbose logging, and development middleware are disabled
- [ ] `usesCleartextTraffic`, `DEBUG=True`, and equivalent dev-only settings are off

### Dependencies

- [ ] All dependencies are pinned to exact versions (`==`, not `>=`) (see [Dependency Safety](./DEPENDENCY_SAFETY.md))
- [ ] No `@latest` CDN tags — pin to a specific version with SRI hashes
- [ ] `npm audit` / `pip audit` / equivalent shows no critical vulnerabilities
- [ ] Lockfile (`package-lock.json`, `poetry.lock`, etc.) is committed and matches what CI tested

### Build & Artifact

- [ ] Production build succeeds with no warnings treated as errors
- [ ] Minification / tree-shaking enabled (LLMs sometimes disable these for debugging)
- [ ] Source maps are generated but *not* served publicly
- [ ] Build artifact is the exact artifact that was tested in CI — no rebuild on deploy

### Database & State

- [ ] Migrations run cleanly on a copy of production data (not just an empty database)
- [ ] Migration is backward-compatible if you need to roll back the code without rolling back the schema
- [ ] No destructive schema changes (`DROP COLUMN`, `DROP TABLE`) without a deprecation period
- [ ] Connection pool sizes, timeouts, and retry policies are explicitly configured

---

## Deployment Strategies

Choose a strategy based on your risk tolerance. AI-generated code — especially the first deploy of a feature — benefits from conservative strategies.

### Rolling Deploys (Default for Most Teams)

Replace instances gradually. If the new version fails health checks, the old version stays up.

**When to use**: Standard deploys where you have health checks and can tolerate a brief period of mixed versions.

**Watch for with AI code**: Implicit contract mismatches between old and new versions. If the AI changed an API response shape, the old frontend and new backend may disagree during the rollout window.

### Blue-Green / Canary

Route a small percentage of traffic to the new version. Promote if metrics look good; roll back instantly if not.

**When to use**: First deployment of a significant AI-generated feature. High-traffic systems where a full rollout is risky.

**Watch for with AI code**: The canary might look fine on 5% traffic but break at scale. AI code rarely accounts for contention, rate limits, or cache pressure.

### Feature Flags

Deploy the code but gate the feature behind a flag. Enable incrementally.

**When to use**: When you want to decouple deployment from release. Especially useful when the AI generated a large feature across multiple modules and you want to test pieces independently.

**Watch for with AI code**: Dead code left behind when flags are removed. LLMs are good at adding flags; they're bad at cleaning them up. Track every flag with an owner and a removal date.

---

## What to Monitor

Monitoring AI code requires the same tools as any production system, but the *priorities* shift. AI-generated code fails differently than hand-written code.

### The Four Signals (Start Here)

| Signal | What to watch | AI-specific concern |
|--------|--------------|---------------------|
| **Error rate** | 5xx responses, unhandled exceptions | AI code often catches exceptions too broadly — errors get swallowed instead of surfaced. Check logs, not just HTTP status codes. (See [Anti-Patterns — Silent Swallowing](./ANTI_PATTERNS.md)) |
| **Latency** | p50, p95, p99 response times | AI code rarely includes timeouts on external calls. One slow dependency can cascade. |
| **Throughput** | Requests per second | Unexpected drops may indicate silent failures or broken retry loops. |
| **Saturation** | CPU, memory, connections, queue depth | AI code can leak connections, spawn unbounded goroutines/promises, or cache without eviction. |

### AI-Specific Monitoring Priorities

**1. Cross-boundary data integrity**

AI modules generated in different sessions may agree on field names but disagree on types or semantics. Monitor for:
- Unexpected `null` / `undefined` values in required fields
- Type coercion warnings (string where number expected)
- Serialization failures (datetime to JSON, Decimal to float)

**2. Silent failures**

AI-generated error handling often catches everything and logs at debug level. Production bugs become invisible. Monitor for:
- Log lines with level `debug` or `info` that contain error-like content ("failed", "error", "exception")
- Catch-all exception handlers that don't re-raise
- Empty response bodies (API returned 200 but no data)

**3. External dependency health**

AI code tends to call external APIs without circuit breakers, retries, or fallbacks. Monitor:
- Response times per external dependency
- Error rates per external dependency
- Connection pool exhaustion

**4. Resource leaks**

AI code frequently forgets to close connections, file handles, or cancel timers. Monitor:
- Open file descriptor count over time (should be stable, not growing)
- Database connection count over time
- Memory usage over time (gradual climb = leak)

---

## Structured Logging for AI-Generated Code

AI code's most dangerous failure mode is *silent* failure — the code runs, returns 200, but the response is wrong. Structured logging makes these visible.

### Minimum Logging Requirements

Add these to your CLAUDE.md or project rules so the AI includes them from the start:

```markdown
## Logging Rules
- Every external API call: log request start, response status, and duration
- Every database query over 100ms: log the query and duration
- Every error: log at ERROR level with full context (don't catch and log at DEBUG)
- Every authentication decision: log the outcome (allow/deny) and the reason
- Every background job: log start, completion, and failure with job ID
```

### What Structured Logs Look Like

```json
{
  "timestamp": "2025-03-15T14:22:01Z",
  "level": "error",
  "service": "payment-api",
  "event": "external_call_failed",
  "dependency": "stripe",
  "method": "POST",
  "path": "/v1/charges",
  "status": 429,
  "duration_ms": 1203,
  "retry_count": 3,
  "correlation_id": "abc-123",
  "message": "Stripe rate limit exceeded after 3 retries"
}
```

This is grep-able, dashboard-able, and alert-able. Compare to what AI typically generates:

```python
except Exception as e:
    logger.debug(f"Error: {e}")
    return None
```

The first version lets you build dashboards. The second hides production failures.

---

## Rollback Planning

Every deployment needs a rollback plan. AI-generated deployments need it more, because the developer may not fully understand what changed.

### Before You Deploy

1. **Know your rollback command.** Write it down. Don't figure it out during an incident.
2. **Test the rollback.** Deploy, then roll back, then verify. The first time you roll back should not be during a production incident.
3. **Check for irreversible steps.** Database migrations, external API calls with side effects, sent emails — these can't be undone by redeploying old code.

### Rollback Decision Framework

| Symptom | Action |
|---------|--------|
| Error rate > 2x baseline within 5 minutes of deploy | Roll back immediately |
| Latency p99 > 3x baseline | Roll back immediately |
| Functional regression (feature worked before, broken now) | Roll back immediately |
| Slow leak (memory, connections growing over hours) | Schedule rollback within the hour |
| Edge case bug affecting < 1% of requests | Fix forward with a hotfix, don't roll back |

### Database Rollback Compatibility

The most common rollback failure with AI code: the migration added a new required column, so rolling back the code breaks because the old code doesn't set the new column.

**Rule**: Migrations should be backward-compatible for at least one deploy cycle. Add columns as nullable or with defaults. Remove columns in a *subsequent* deploy after the code no longer references them.

---

## Incident Response for AI-Generated Systems

When production breaks, the unique challenge with AI-generated systems is that no one may fully understand the code. Here's how to handle it.

### The First 5 Minutes

1. **Identify the blast radius.** What's broken? What still works? Check dashboards, not code.
2. **Decide: rollback or fix forward.** Use the decision framework above. When in doubt, roll back.
3. **If rolling back**: execute your pre-written rollback command. Verify. Communicate.
4. **If fixing forward**: isolate the failing component. Read the code before changing it.

### Using AI to Debug Production Issues

AI is useful during incidents, but only with discipline:

- **Do**: Paste the error log and ask the AI to explain what's happening
- **Do**: Ask the AI to identify what recently changed that could cause this failure
- **Do**: Ask the AI to write a targeted fix for the specific error
- **Don't**: Ask the AI to "fix everything" — this leads to broad changes during a crisis
- **Don't**: Deploy AI-generated fixes without reading them. You're under pressure, but shipping a second bug is worse than being slow.
- **Don't**: Let the AI refactor during an incident. Fix the bug, ship, then clean up later.

### Post-Incident Review

After the incident is resolved:

1. **Trace the root cause to its origin.** Was it a silent contract mismatch? A missing timeout? An exception swallowed by a catch-all? These are the characteristic AI failure modes.
2. **Add monitoring for the specific failure.** If it happened once, the same pattern likely exists elsewhere.
3. **Search the codebase for the same pattern.** AI often generates the same bug in multiple places across different sessions (see [Code Review — Bug Class Search](./CODE_REVIEW_AI.md)).
4. **Update your CLAUDE.md or project rules** to prevent the AI from reintroducing the pattern.
5. **Write a regression test.** This is non-negotiable.

---

## Production Hardening Checklist

These items are commonly missing from AI-generated code. Review before the first production deployment and periodically thereafter.

### Timeouts & Resilience

- [ ] Every HTTP client call has an explicit timeout (connect + read)
- [ ] Database queries have a statement timeout configured
- [ ] Background jobs have a maximum execution time
- [ ] Retry logic uses exponential backoff with jitter, not fixed delays
- [ ] Retry logic has a maximum attempt count (AI code sometimes retries forever)
- [ ] Circuit breakers exist for critical external dependencies

### Rate Limiting & Abuse Prevention

- [ ] Authentication endpoints have rate limiting (see [API Key Security](./API_KEY_SECURITY.md))
- [ ] Public API endpoints have rate limiting per client
- [ ] File upload endpoints validate size and type
- [ ] Pagination has a maximum page size (AI code often allows `?limit=999999`)

### Error Handling

- [ ] No catch-all exception handlers that swallow errors silently
- [ ] Errors are logged at ERROR level, not DEBUG or INFO
- [ ] API error responses don't leak stack traces, file paths, or internal state
- [ ] Failed operations don't leave state half-modified (use transactions or atomic swaps)

### Security (Production-Specific)

- [ ] HTTPS only — no cleartext fallback
- [ ] CORS is configured for specific origins, not `*`
- [ ] Security headers set (CSP, HSTS, X-Frame-Options, etc.)
- [ ] Session/token expiry is configured (AI code often creates tokens that never expire)
- [ ] Admin/debug endpoints are not accessible in production

---

## The CLAUDE.md Production Rules

Add these rules to your CLAUDE.md to prevent common production issues at generation time:

```markdown
## Production Code Rules

### Error Handling
- Never catch broad exceptions (Exception, Error) without re-raising or logging at ERROR level
- Never return None/null as an error sentinel — raise an exception or return a Result type
- Every external call must have an explicit timeout

### Configuration
- No hardcoded URLs, ports, or secrets — use environment variables
- Fail fast on missing required configuration — no silent defaults
- Debug/development settings must not be reachable in production

### API Design
- All list endpoints must have pagination with a maximum page size
- All endpoints must have rate limiting configured
- Error responses must not include stack traces or internal paths

### Database
- All migrations must be backward-compatible (add nullable columns, never drop in the same deploy)
- All queries must use parameterized inputs (no string interpolation)
- Connection pools must have explicit size limits and timeouts
```

---

## Continuous Production Validation

Deployment isn't the end of the process — it's where a new feedback loop begins.

### Smoke Tests After Deploy

Run a small set of critical-path tests against production immediately after every deploy:

- Can a user log in?
- Can the core workflow complete end-to-end?
- Are external integrations responding?

Automate these. If they fail, roll back.

### Periodic Health Checks

Beyond uptime pings, periodically validate data integrity:

- Are counts in the database consistent with what the UI shows?
- Are background jobs completing, or silently piling up?
- Are log volumes normal, or has something gone silent?

AI code can "work" for weeks while silently corrupting data or dropping events. Periodic validation catches drift before users do.

### Dependency Monitoring

AI-suggested dependencies need ongoing attention (see [Dependency Safety](./DEPENDENCY_SAFETY.md)):

- Enable automated vulnerability scanning (Dependabot, Snyk, or equivalent)
- Review dependency update PRs — don't auto-merge
- Monitor for newly discovered vulnerabilities in your locked versions

---

## Summary

| Phase | Key action | AI-specific risk |
|-------|-----------|-----------------|
| Pre-deploy | Run the checklist | Dev-only settings left enabled |
| Deploy | Use canary or rolling deploys | Contract mismatches between old and new code |
| Monitor | Watch error rates, latency, resource usage | Silent failures hidden by catch-all handlers |
| Respond | Roll back fast, debug with discipline | No one fully understands the code under pressure |
| Harden | Add timeouts, rate limits, proper error handling | These are almost always missing from AI output |
| Maintain | Smoke tests, dependency scanning, data validation | AI code silently degrades over time |

The code that passes your tests is the *beginning* of production readiness, not the end. Everything in this guide exists to close that gap.

---

## Related Guides

- [Automation & Testing](./AUTOMATION_TESTING.md) — CI/CD pipelines and quality gates (what runs *before* this guide kicks in)
- [API Key Security](./API_KEY_SECURITY.md) — Keeping secrets out of code and configuring environments safely
- [Dependency Safety](./DEPENDENCY_SAFETY.md) — Evaluating, pinning, and monitoring AI-suggested packages
- [Audit Findings](./AUDIT_FINDINGS.md) — Real production bugs found in AI-generated code
- [Anti-Patterns](./ANTI_PATTERNS.md) — Silent swallowing, catch-all handlers, and other production killers
- [Code Review for AI](./CODE_REVIEW_AI.md) — Catching production issues during review
- [Refactoring with AI](./REFACTORING_WITH_AI.md) — Safe changes that don't break production contracts
