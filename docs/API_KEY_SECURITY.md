---
layout: default
title: API Key & Secrets Security
nav_order: 5
parent: Guides
description: "How to keep API keys and secrets out of your frontend code. Essential reading for vibe coders."
---

# API Key & Secrets Security: Don't Be the App Leaking Keys

This guide exists because **9 out of 10 vibe-coded apps leak credentials**. If you open the browser Network tab on most AI-generated web apps, you'll find API keys, tokens, and secrets flying around in plain text.

This is not hypothetical. People actively scan for these keys and will use them to rack up charges on your accounts.

---

## The Core Rule

**Never put secrets in code that runs in the browser.**

This includes:
- API keys (OpenAI, Stripe, Twilio, etc.)
- Database connection strings
- JWT signing secrets
- OAuth client secrets
- Any token that grants access to paid services or private data

If it's in your frontend code, **anyone can see it** by:
- Opening browser DevTools → Network tab
- Viewing the JavaScript source
- Inspecting the bundled code

---

## Why This Happens in Vibe Coding

When you ask an AI to "add OpenAI integration," it often generates the simplest working code:

```javascript
// ❌ DANGEROUS: API key in frontend code
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  headers: {
    'Authorization': `Bearer sk-proj-abc123...`,  // YOUR KEY IS NOW PUBLIC
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ model: 'gpt-4', messages: [...] })
});
```

This works! Tests pass! The feature is complete!

But you've just published your API key to everyone who visits your site.

---

## The Fix: Server-Side Proxy Routes

The solution is simple: **API calls with secrets go through your backend**.

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Browser   │ ──────► │ Your Server │ ──────► │ External API│
│  (public)   │         │  (private)  │         │  (OpenAI)   │
└─────────────┘         └─────────────┘         └─────────────┘
     │                        │                       │
     │  No secrets here       │  Secrets live here    │
     │                        │  (env variables)      │
```

### Before (Dangerous)

```javascript
// Frontend code - ANYONE CAN SEE THIS
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  headers: { 'Authorization': `Bearer ${process.env.OPENAI_API_KEY}` }
  // ❌ process.env gets bundled into your JS - the key is exposed!
});
```

### After (Safe)

**Frontend** (no secrets):
```javascript
// Frontend calls YOUR server, not OpenAI directly
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: userMessage })
  // ✅ No API key here - your server adds it
});
```

**Backend** (secrets stay here):
```javascript
// Server-side route (Next.js API route example)
// File: app/api/chat/route.ts

export async function POST(request: Request) {
  const { message } = await request.json();

  // ✅ API key only exists on server, never sent to browser
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [{ role: 'user', content: message }]
    })
  });

  const data = await response.json();
  return Response.json(data);
}
```

---

## Framework-Specific Patterns

### Next.js (App Router)

```typescript
// app/api/external-service/route.ts
export async function POST(request: Request) {
  const body = await request.json();

  const response = await fetch('https://api.example.com/endpoint', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.EXTERNAL_API_KEY}`, // Server-only
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });

  return Response.json(await response.json());
}
```

### Express.js

```javascript
// routes/api.js
const express = require('express');
const router = express.Router();

router.post('/chat', async (req, res) => {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(req.body)
  });

  res.json(await response.json());
});

module.exports = router;
```

### Python (FastAPI)

```python
# routes/chat.py
import os
import httpx
from fastapi import APIRouter

router = APIRouter()

@router.post("/api/chat")
async def chat(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json"
            },
            json={"model": "gpt-4", "messages": [{"role": "user", "content": message}]}
        )
    return response.json()
```

### Python (Flask)

```python
# app.py
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {os.environ["OPENAI_API_KEY"]}',
            'Content-Type': 'application/json'
        },
        json=data
    )
    return jsonify(response.json())
```

---

## Environment Variables Done Right

### .env Files

Create a `.env` file for local development:

```bash
# .env (NEVER commit this file)
OPENAI_API_KEY=sk-proj-abc123...
DATABASE_URL=postgresql://user:pass@localhost/db
STRIPE_SECRET_KEY=sk_live_...
```

### .env.example

Commit a template so others know what's needed:

```bash
# .env.example (safe to commit)
OPENAI_API_KEY=your-key-here
DATABASE_URL=your-database-url
STRIPE_SECRET_KEY=your-stripe-key
```

### .gitignore

**Always** include:

```gitignore
# Environment files - NEVER commit secrets
.env
.env.local
.env.*.local
.env.production

# But DO commit the example
!.env.example
```

### Framework-Specific Environment Variables

| Framework | Server-only prefix | Client-safe prefix |
|-----------|-------------------|-------------------|
| Next.js | (no prefix) | `NEXT_PUBLIC_` |
| Vite | (no prefix) | `VITE_` |
| Create React App | (no prefix) | `REACT_APP_` |
| Nuxt | (no prefix) | `NUXT_PUBLIC_` |

**Rule**: If a variable has the "public" prefix, it WILL be bundled into client code. Never put secrets in public env vars.

```bash
# ✅ Safe - server only
OPENAI_API_KEY=sk-proj-...

# ❌ DANGEROUS - will be in browser bundle!
NEXT_PUBLIC_OPENAI_API_KEY=sk-proj-...
VITE_OPENAI_API_KEY=sk-proj-...
REACT_APP_OPENAI_API_KEY=sk-proj-...
```

---

## Common Mistakes

### 1. "It's in .env so it's safe"

**Wrong.** If your frontend code references `process.env.API_KEY`, bundlers like Webpack/Vite will inline the value into your JavaScript.

```javascript
// Your code
const key = process.env.API_KEY;

// After bundling (visible to everyone)
const key = "sk-proj-abc123...";
```

### 2. Using NEXT_PUBLIC_ for secrets

```bash
# ❌ This WILL be exposed to browsers
NEXT_PUBLIC_STRIPE_SECRET=sk_live_...

# ✅ This stays on the server
STRIPE_SECRET_KEY=sk_live_...
```

### 3. Hardcoding "just for testing"

```javascript
// "I'll fix it later" - famous last words
const API_KEY = "sk-proj-abc123..."; // ❌ Committed to git forever
```

### 4. Logging secrets

```javascript
console.log('Using API key:', process.env.API_KEY); // ❌ Now in browser console
console.log('Config loaded'); // ✅ Safe
```

### 5. Including secrets in error messages

```javascript
// ❌ Dangerous
throw new Error(`API call failed with key ${apiKey}`);

// ✅ Safe
throw new Error('API call failed - check server logs');
```

### 6. Warn-Only Security Defaults

```python
# ❌ AI generates this constantly
SECRET_KEY = os.environ.get("SECRET_KEY", "default-insecure-key-change-me")
if SECRET_KEY == "default-insecure-key-change-me":
    logger.warning("Using default SECRET_KEY — not safe for production!")
    # But keeps running with the insecure key...

# ✅ Fail-fast in non-development environments
SECRET_KEY = os.environ.get("SECRET_KEY", "default-insecure-key-change-me")
if SECRET_KEY == "default-insecure-key-change-me":
    env = os.environ.get("ENVIRONMENT", "production")
    if env != "development":
        raise RuntimeError("SECRET_KEY must be set in production/staging")
    logger.warning("Using default SECRET_KEY — development only")
```

Nobody reads warning logs during development, and the default key ships to production. **Default-insecure with a warning is effectively the same as no security.** Make insecure configurations fail loudly in any non-development environment.

### 7. Missing Rate Limiting on Auth Endpoints

```python
# ❌ Unauthenticated endpoint with no rate limiting
@app.route('/auth/login', methods=['POST'])
def login():
    # Brute-force invitation, especially with JWT (no account lockout)
    ...

# ✅ Rate limit before processing
@app.route('/auth/login', methods=['POST'])
@limiter.limit("5/minute")
def login():
    ...
```

Rate limiting is table stakes, not a nice-to-have. An unauthenticated login endpoint without rate limiting is a brute-force invitation — especially with JWT-based auth where there's no account lockout mechanism. **Add rate limiting before your first deployment, not after your first incident.** Five requests per minute on auth endpoints is a reasonable starting point.

### 8. Exposing internal services

```javascript
// ❌ Frontend directly calls internal service
fetch('http://internal-api.local:3001/admin/users')

// ✅ Frontend calls your public API, which calls internal services
fetch('/api/users')  // Your server handles internal routing
```

---

## How to Check for Leaks

### 1. Browser Network Tab

1. Open your app in Chrome/Firefox
2. Open DevTools (F12) → Network tab
3. Use your app normally
4. Look at each request's headers and payload
5. **If you see API keys in any request, you have a problem**

### 2. View Source

1. Open DevTools → Sources tab
2. Search (Ctrl+Shift+F) for:
   - `sk-` (OpenAI)
   - `sk_live` (Stripe)
   - `api_key`
   - `secret`
   - `token`
3. **If you find real values, you have a problem**

### 3. Git History Check

```bash
# Search git history for potential secrets
git log -p | grep -i "api_key\|secret\|password\|token" | head -50
```

### 4. Automated Scanning

Use tools like:
- [git-secrets](https://github.com/awslabs/git-secrets)
- [truffleHog](https://github.com/trufflesecurity/trufflehog)
- [detect-secrets](https://github.com/Yelp/detect-secrets)

---

## Pre-commit Hook for Secrets

Add to `.claude/settings.json` or your git hooks:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for potential secrets
if git diff --cached | grep -iE "(sk-[a-zA-Z0-9]{20,}|api_key\s*=\s*['\"][^'\"]+|secret\s*=\s*['\"][^'\"]+)" > /dev/null; then
    echo "⚠️  Potential secret detected in commit!"
    echo "Please review your changes and remove any API keys or secrets."
    exit 1
fi
```

---

## Prompts for Safe API Integration

When asking an AI to add API integrations, be explicit:

### Good Prompt

```
Add OpenAI chat integration.

Requirements:
- Create a server-side API route at /api/chat
- The OPENAI_API_KEY must only be used server-side
- Frontend should call /api/chat, NOT the OpenAI API directly
- Add OPENAI_API_KEY to .env.example (without real value)
- Ensure .env is in .gitignore
```

### Bad Prompt

```
Add OpenAI chat to my app
```

The bad prompt gives the AI freedom to take shortcuts that expose your keys.

---

## Authentication for Your Proxy Routes

Your proxy routes need protection too! Otherwise anyone can use your API through your server:

```typescript
// app/api/chat/route.ts
import { getServerSession } from 'next-auth';

export async function POST(request: Request) {
  // ✅ Verify user is authenticated
  const session = await getServerSession();
  if (!session) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // ✅ Optional: Rate limiting
  const rateLimitOk = await checkRateLimit(session.user.id);
  if (!rateLimitOk) {
    return Response.json({ error: 'Rate limited' }, { status: 429 });
  }

  // Now safe to make the external API call
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    // ...
  });

  return Response.json(await response.json());
}
```

---

## Quick Reference Checklist

Before deploying any app:

- [ ] **No API keys in frontend code** - Search your codebase
- [ ] **No secrets in public env vars** - Check for `NEXT_PUBLIC_`, `VITE_`, etc.
- [ ] **.env in .gitignore** - Verify it's not being committed
- [ ] **Server-side proxy routes** - External APIs called from backend only
- [ ] **Network tab clean** - No secrets visible in browser DevTools
- [ ] **Proxy routes authenticated** - Can't be abused by anonymous users
- [ ] **Rate limiting** - Prevent runaway API costs
- [ ] **Error messages clean** - No secrets in error responses

---

## What To Do If You Leaked a Key

1. **Revoke the key immediately** - Go to the service dashboard and rotate/delete the key
2. **Check usage** - Look for unauthorized usage in the billing dashboard
3. **Remove from git history** - Use `git filter-branch` or BFG Repo-Cleaner
4. **Generate new key** - Create a fresh key and update your server config
5. **Add prevention** - Set up pre-commit hooks and CI checks

```bash
# Remove secrets from git history (use BFG Repo-Cleaner)
bfg --replace-text secrets.txt  # File containing patterns to remove
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

**Note**: If the repo was ever public, assume the key is compromised even after removal.

---

## Remember

**The browser is hostile territory.** Everything sent to the browser is public:
- All JavaScript code
- All network requests
- All localStorage data
- All cookies (readable by JS unless httpOnly)

Your server is the security boundary. Keep secrets on your server, and treat every browser request as potentially malicious.

**If you can see it in DevTools, so can attackers.**
