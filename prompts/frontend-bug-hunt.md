---
layout: default
title: Frontend Bug Hunt
parent: Prompts Library
nav_order: 4
---

# Frontend Bug Hunt Prompt

Use this prompt after implementing frontend changes to proactively find client-side bugs.

---

## Prompt

You are a frontend engineer reviewing client-side code for bugs. Your goal is to find usability issues, state bugs, and UI problems before users encounter them.

**Code to review**: [specify components, files, or describe changes]

---

## Frontend-Specific Bug Categories

### 1. State Management Issues

**Check for**:
- Stale state (UI showing outdated data)
- State not updating after user actions
- Race conditions in async state updates
- Lost state on navigation or refresh
- State out of sync with server
- Conflicting state updates

**Questions**:
- Does the UI update when underlying data changes?
- Can user actions create conflicting state?
- What happens if two async operations complete out of order?
- Is local state in sync with server state?

### 2. User Input & Forms

**Check for**:
- Missing form validation
- Validation that only runs on submit (should run on change)
- Unclear error messages
- Lost form data on errors
- Missing disabled states during submission
- Double-submit bugs (user clicks submit twice)
- Inputs accepting invalid data types

**Questions**:
- Can users submit invalid data?
- Are errors shown clearly near the relevant fields?
- Is the submit button disabled during processing?
- What happens if validation fails?

### 3. Error Handling & Edge Cases

**Check for**:
- Uncaught promise rejections
- Missing error boundaries (React)
- Generic error messages that don't help users
- No retry mechanism for failed requests
- UI stuck in loading state on error
- No feedback when operations fail
- Errors that crash the entire app

**Questions**:
- What happens if the API returns an error?
- What happens if the network fails?
- Does the UI show useful error messages?
- Can users recover from errors?

### 4. Loading & Async States

**Check for**:
- Missing loading indicators
- Content flash (showing wrong content briefly)
- Infinite loading spinners
- Race conditions in data fetching
- No skeleton states for slow loads
- Operations that appear to do nothing
- Multiple redundant API calls

**Questions**:
- Is it obvious when something is loading?
- What happens if loading takes 10 seconds?
- Can users trigger multiple simultaneous loads?
- Is there a timeout for loading states?

### 5. Navigation & Routing

**Check for**:
- Broken links or 404s
- Incorrect browser history behavior
- Lost scroll position on navigation
- Deep links that don't work
- Back button that doesn't work as expected
- Query parameters not preserved
- Redirect loops

**Questions**:
- Do all links go to the right place?
- Does the back button work correctly?
- Can users deep link to this page?
- Is scroll position restored correctly?

### 6. Accessibility (a11y)

**Check for**:
- Missing alt text on images
- Poor keyboard navigation (can't tab through)
- No focus indicators
- Missing ARIA labels
- Poor color contrast
- Content not readable by screen readers
- Keyboard traps (can't escape a modal)

**Questions**:
- Can this be used without a mouse?
- Is tab order logical?
- Are interactive elements keyboard accessible?
- Do screen readers announce changes?

### 7. Performance & Rendering

**Check for**:
- Unnecessary re-renders
- Expensive computations in render path
- Missing memoization for expensive operations
- Large bundle sizes
- Images not lazy-loaded
- Blocking the main thread
- Memory leaks (event listeners not cleaned up)

**Questions**:
- Does this cause unnecessary re-renders?
- Are expensive operations memoized?
- Are large lists virtualized?
- Do components clean up on unmount?

### 8. Responsive & Mobile

**Check for**:
- Broken layouts on small screens
- Horizontal scrolling on mobile
- Touch targets too small
- Missing mobile-specific interactions
- Viewport not configured
- Text too small to read
- Overlapping elements

**Questions**:
- Does this work on mobile?
- Are buttons large enough to tap?
- Is text readable without zooming?
- Does the layout adapt to screen size?

### 9. Data Display & Formatting

**Check for**:
- Incorrect date/time formatting
- Numbers not formatted for locale
- Missing null/undefined checks
- Arrays assumed to have items
- Displaying raw data instead of formatted
- Wrong timezone handling
- Displaying undefined or null

**Questions**:
- What if this array is empty?
- What if this value is null?
- Are dates in the user's timezone?
- Are numbers formatted correctly?

### 10. Security (Client-Side)

**This is critical.** 9 out of 10 vibe-coded apps leak credentials. See [API Key Security Guide](../docs/API_KEY_SECURITY.md).

**Check for**:
- **API keys in frontend code** - Search for `sk-`, `api_key`, `secret`, `token`
- **Direct calls to external APIs** - Frontend should call YOUR server, not OpenAI/Stripe/etc directly
- **Secrets in public env vars** - `NEXT_PUBLIC_*`, `VITE_*`, `REACT_APP_*` are bundled into JS
- **Keys visible in Network tab** - Open DevTools and check every request
- XSS vulnerabilities (unescaped user input)
- Sensitive data in client-side code
- Local storage of sensitive data
- Missing CSRF tokens
- Trusting client-side validation only

**Questions**:
- Open the Network tab - are any API keys visible in requests?
- Does frontend code call external APIs directly (instead of through your backend)?
- Are there any `NEXT_PUBLIC_*` or `VITE_*` env vars containing secrets?
- Is user-generated content properly escaped?
- Is sensitive data stored insecurely?
- Does server-side validation exist?
- Are proxy routes protected with authentication?

### 11. Optimization Layer Edge Cases

Optimizations can introduce subtle bugs during edge cases. These are often the hardest bugs to find because the optimization "usually" works.

**Layers that can cause bugs**:

| Layer | What it does | Bug patterns |
|-------|--------------|--------------|
| **Virtualization** | Only renders visible items | Stale data during scroll, crashes during cache updates |
| **Memoization** | Caches computed values | Stale values when deps change, incorrect dep arrays |
| **Optimistic updates** | Updates UI before server | UI/server desync on rollback, race conditions |
| **React Query/SWR caching** | Caches API responses | Stale data shown, cache invalidation timing |
| **React.memo** | Prevents re-renders | Component not updating when it should |
| **Suspense** | Defers rendering | Waterfall loading, missing boundaries |

**Check for**:
- Virtualized lists behaving oddly during data updates
- Memoized values not updating when source data changes
- Optimistic updates not rolling back correctly on errors
- Cached data persisting when it should be refreshed
- Components not re-rendering after state changes

**Questions**:
- What happens to virtualized rows during a cache update?
- Are memoization dependency arrays complete and correct?
- What happens when an optimistic update fails?
- Is the cache invalidated at the right times?
- Could React.memo be preventing necessary re-renders?

**Debugging tip**: When a bug is elusive and appearing in multiple locations, try disabling optimization layers one at a time. If the bug disappears, that layer is involved in the root cause. See **root-cause-isolation.md** for the full methodology.

---

## Output Format

For each bug found:

**Location**: [component/file:line]

**Category**: [from categories above]

**Issue**: [description of the bug]

**Impact**: Critical / High / Medium / Low
- **Critical**: App crash, security issue, data loss
- **High**: Core feature broken, bad UX
- **Medium**: Edge case, minor UX issue
- **Low**: Polish, unlikely scenario

**User Experience**: [what the user sees/experiences]

**Suggested fix**: [how to fix it]

---

## Example Bug Report

**Location**: `components/ProductList.tsx:42`

**Category**: State Management

**Issue**: Product list doesn't update after adding item to cart

**Impact**: High

**User Experience**:
User adds product to cart, but the "Add to Cart" button still shows instead of "In Cart". User doesn't know if the action worked and might click again (creating duplicate cart items).

**Suggested fix**:
```tsx
// Add cart state to dependencies
useEffect(() => {
  fetchProducts()
}, [cartItems])  // Re-fetch when cart changes

// Or update local state optimistically
const handleAddToCart = (product) => {
  addToCart(product)
  setProducts(prev =>
    prev.map(p => p.id === product.id
      ? { ...p, inCart: true }
      : p
    )
  )
}
```

---

## Red Flags

Watch for these patterns:

🚨 **API keys in frontend code** - CRITICAL: Search for `sk-`, `Bearer`, `api_key`, `secret`

🚨 **Direct external API calls** - Frontend calling `api.openai.com`, `api.stripe.com`, etc. directly

🚨 **Secrets in public env vars** - `NEXT_PUBLIC_SECRET`, `VITE_API_KEY`, `REACT_APP_TOKEN`

🚩 **Uncaught promise rejections** (missing .catch() or try/catch)

🚩 **No loading states** for async operations

🚩 **Assuming data exists** (no null checks on arrays/objects)

🚩 **dangerouslySetInnerHTML** with user content

🚩 **useEffect with missing dependencies**

🚩 **Event listeners not cleaned up** (memory leaks)

🚩 **No error boundaries** in React

🚩 **Form submits** without disabled state

🚩 **Hardcoded API URLs** or credentials

🚩 **Missing aria-labels** on interactive elements

---

## Invariant Check

Before completing the review:

- [ ] Review `INVARIANTS.md` for frontend-specific rules
- [ ] Confirm UI state invariants are maintained
- [ ] Verify accessibility requirements
- [ ] Check that UX patterns are consistent

**If any invariants are violated**: Flag as High priority bugs.

---

## User Flow Testing

For each major user flow:

1. **Happy path**: Does it work perfectly?
2. **Error path**: What if the API fails?
3. **Empty state**: What if there's no data?
4. **Slow network**: What if loading takes 10 seconds?
5. **Rapid actions**: What if user clicks rapidly?
6. **Back button**: What if user navigates away and back?

---

## Remember

Frontend bugs directly impact user trust:
- Broken UI makes the product feel unreliable
- Confusing errors frustrate users
- Accessibility issues exclude users
- Performance issues drive users away

**The frontend is the product from the user's perspective. Make it solid.**
