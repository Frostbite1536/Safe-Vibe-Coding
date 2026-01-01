# Performance Review Prompt

Use this prompt to identify performance issues in code or architecture.

---

## Prompt

You are conducting a performance review of the system. Your goal is to identify bottlenecks, inefficiencies, and opportunities for optimization.

**Scope**: [describe what to review - specific file/function/feature or entire system]

**Context**:
- Expected load: [requests/sec, data volume, user count, etc.]
- Current performance: [if known - latency, throughput, etc.]
- Performance requirements: [SLA, response time targets, etc.]

---

**Review areas**:

### 1. Database Performance

**Check for**:
- N+1 queries (loop with query inside)
- Missing indices on frequently queried/joined columns
- Full table scans on large tables
- Inefficient joins or subqueries
- Fetching unnecessary columns (SELECT *)
- No query result limits

**Questions**:
- How many database round-trips per request?
- Are queries indexed appropriately?
- Is pagination implemented for large result sets?

### 2. API & Network Efficiency

**Check for**:
- Multiple API calls that could be batched
- Large payloads when smaller would work
- Missing caching of external API results
- No timeout/retry logic (causing hung requests)
- Synchronous calls to slow external services

**Questions**:
- Can multiple calls be combined?
- Are responses cacheable?
- Should this be async?

### 3. Algorithmic Efficiency

**Check for**:
- O(n²) or worse algorithms on large datasets
- Unnecessary repeated computation
- Inefficient data structure choices (list when set/map appropriate)
- Sorting when unnecessary
- String concatenation in loops (should use builder/join)

**Questions**:
- What's the time complexity?
- Is there a more efficient algorithm?
- Are we doing work we don't need to?

### 4. Memory Usage

**Check for**:
- Loading entire large datasets into memory
- Memory leaks (unreleased resources, event listeners, etc.)
- Excessive object creation in hot paths
- Large allocations that could be streamed
- No pagination for large collections

**Questions**:
- Can we stream instead of load all?
- Are we holding references longer than needed?
- Is memory growth unbounded?

### 5. Caching Opportunities

**Check for**:
- Repeated computation of same results
- Frequently accessed data not cached
- Missing HTTP caching headers
- No memoization of expensive functions

**Questions**:
- What's computed repeatedly?
- What's slow but stable (good cache candidate)?
- What's the cache invalidation strategy?

### 6. Frontend Performance

**Check for**:
- Large bundle sizes
- No code splitting
- Synchronous scripts blocking rendering
- Large unoptimized images
- Unnecessary re-renders in React/Vue/etc.
- No lazy loading of offscreen content

**Questions**:
- What's the bundle size?
- Are we code-splitting routes?
- Are images optimized and lazy-loaded?

### 7. Concurrency & Parallelization

**Check for**:
- Sequential operations that could be parallel
- No connection pooling
- Single-threaded when multi-threaded appropriate
- Blocking operations on main thread

**Questions**:
- Can these run in parallel?
- Are we using connection pools?
- Is there a worker/queue for slow operations?

---

**Output format**:

For each issue:
- **Location**: [file:line or component]
- **Issue**: [description of performance problem]
- **Impact**: [estimated performance impact - High/Medium/Low]
- **Current complexity/cost**: [e.g., O(n²), 10 DB queries per request]
- **Optimization**: [how to fix it]
- **Expected improvement**: [rough estimate of improvement]
- **Effort**: [Low/Medium/High]

Prioritize by: **Impact / Effort ratio** (high impact, low effort = do first)

---

**Remember**:
- Don't optimize prematurely - focus on actual/likely bottlenecks
- Measure before and after if possible
- Sometimes "good enough" is better than "optimal but complex"
