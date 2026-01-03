---
layout: default
title: Automation & Testing
nav_order: 6
parent: Guides
description: "CI/CD, hooks, static analysis, security scanning, and verification loops for AI-assisted development."
---

# Automation & Testing for AI-Assisted Development

AI-generated code requires robust automated quality gates. Manual review is essential but insufficient—automated checks catch issues humans miss and provide consistent enforcement. This document covers setting up comprehensive automation pipelines for safe vibe coding.

---

## Why Automation Matters for AI Code

When working with LLMs, code appears quickly. This speed creates risk:
- More code means more potential bugs
- Fast iteration makes manual review harder
- AI can introduce subtle issues that look correct at first glance

**Automation provides**:
- Consistent quality enforcement (no "I forgot to run tests")
- Fast feedback on every change
- Security scanning at scale
- Documentation that code meets standards

**Rule: If a human should check it, automate the check.**

---

## The Automation Stack

A comprehensive automation setup includes:

1. **Pre-commit hooks** - Catch issues before they enter version control
2. **Claude Code hooks** - Auto-format code, run verification after edits
3. **CI/CD pipelines** - Automated testing and deployment
4. **Static analysis** - Find bugs without running code
5. **Security scanning** - Identify vulnerabilities automatically
6. **Dependency auditing** - Keep dependencies secure and updated
7. **Code coverage** - Ensure tests actually test the code
8. **Verification loops** - Give Claude ways to verify its own work

---

## Pre-Commit Hooks

Pre-commit hooks run automatically before each commit, preventing broken or non-compliant code from entering your repository.

### Using the Pre-commit Framework

The [pre-commit](https://pre-commit.com/) framework provides a more robust solution than raw git hooks:

```bash
# Install pre-commit
pip install pre-commit
# or
brew install pre-commit
```

Create `.pre-commit-config.yaml` in your repository root:

```yaml
# .pre-commit-config.yaml
repos:
  # General hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key  # Catches committed secrets

  # Python
  - repo: https://github.com/psf/black
    rev: 24.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  # JavaScript/TypeScript
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: \.[jt]sx?$
        types: [file]
        additional_dependencies:
          - eslint
          - eslint-config-prettier
          - '@typescript-eslint/parser'
          - '@typescript-eslint/eslint-plugin'

  # Markdown
  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.39.0
    hooks:
      - id: markdownlint
        args: ['--fix']

  # Security - detect secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

Install hooks in your repository:

```bash
pre-commit install

# Run against all files (first time)
pre-commit run --all-files
```

### Language-Specific Pre-commit Configurations

**For Python projects**, add type checking:

```yaml
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
```

**For JavaScript/TypeScript projects**, add Prettier:

```yaml
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, json, yaml, markdown]
```

**For Go projects**:

```yaml
  - repo: https://github.com/dnephin/pre-commit-golang
    rev: v0.5.1
    hooks:
      - id: go-fmt
      - id: go-vet
      - id: go-lint
```

**For Rust projects**:

```yaml
  - repo: local
    hooks:
      - id: cargo-fmt
        name: cargo fmt
        entry: cargo fmt --
        language: system
        types: [rust]
      - id: cargo-clippy
        name: cargo clippy
        entry: cargo clippy --all-targets -- -D warnings
        language: system
        types: [rust]
        pass_filenames: false
```

---

## Claude Code Hooks

If you're using Claude Code for AI-assisted development, **hooks** provide powerful automation that runs during your coding session—not just at commit time.

### PostToolUse Hooks for Auto-Formatting

Claude usually generates well-formatted code, but a PostToolUse hook handles the last 10% to avoid formatting errors in CI. This runs automatically after every file edit:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npm run format || true"
          }
        ]
      }
    ]
  }
}
```

**Language-specific examples**:

```json
// JavaScript/TypeScript - Prettier
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "prettier --write . || true"
          }
        ]
      }
    ]
  }
}
```

```json
// Python - Black + isort
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "black . && isort . || true"
          }
        ]
      }
    ]
  }
}
```

```json
// Go - gofmt
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "gofmt -w . || true"
          }
        ]
      }
    ]
  }
}
```

**Why use `|| true`?** This prevents the hook from blocking Claude if formatting fails on a partial file. The CI pipeline will catch any remaining issues.

### Stop Hooks for Verification

For long-running tasks, use a Stop hook to automatically verify Claude's work when it finishes:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "npm test"
      }
    ]
  }
}
```

This ensures every coding session ends with a test run, catching issues before you review.

### Pre-allowing Safe Commands

Instead of using `--dangerously-skip-permissions`, pre-allow common safe commands in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm test:*)",
      "Bash(npm run lint:*)",
      "Bash(npm run build:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)"
    ]
  }
}
```

This avoids permission prompts for routine operations while maintaining security for destructive commands.

---

## GitHub Actions for CI/CD

GitHub Actions automates testing, building, and deployment. Every push and pull request should trigger automated checks.

### Basic CI Workflow

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]  # Test multiple versions

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linter
        run: npm run lint

      - name: Run type check
        run: npm run type-check

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: true

  build:
    runs-on: ubuntu-latest
    needs: test  # Only build if tests pass

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build
        run: npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/
```

### Python CI Workflow

```yaml
name: Python CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          flake8 src/ tests/
          black --check src/ tests/
          isort --check-only src/ tests/

      - name: Run type checking
        run: mypy src/

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-fail-under=80

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

### Required Status Checks

Configure branch protection to require CI passes:

1. Go to **Settings > Branches > Branch protection rules**
2. Add rule for `main`
3. Enable:
   - **Require status checks to pass before merging**
   - Select your CI jobs (test, lint, build)
   - **Require branches to be up to date before merging**
   - **Require pull request reviews before merging**

This prevents merging code that fails automated checks.

### Claude Code GitHub Action

Use the Claude Code GitHub Action to automate AI-assisted code review and documentation updates on pull requests:

```yaml
# .github/workflows/claude-review.yml
name: Claude Code Review

on:
  pull_request:
    types: [opened, synchronize]
  issue_comment:
    types: [created]

jobs:
  claude-review:
    if: |
      github.event_name == 'pull_request' ||
      (github.event_name == 'issue_comment' &&
       contains(github.event.comment.body, '@claude'))
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Claude Code Review
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Use cases**:
- **Automated review**: Claude reviews every PR for code quality, security, and best practices
- **Documentation updates**: Tag `@claude` in PR comments to update CLAUDE.md or other docs
- **CLAUDE.md maintenance**: When Claude makes a mistake, add it to CLAUDE.md as part of the PR

**Pro tip**: During code review, tag `@claude` on coworkers' PRs to add learnings to the team's CLAUDE.md. This creates a compounding knowledge base—mistakes made once are never repeated.

---

## Static Analysis

Static analysis finds bugs, security issues, and code quality problems without running code.

### ESLint (JavaScript/TypeScript)

**Installation**:

```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

**Configuration** (`eslint.config.js` for flat config):

```javascript
import eslint from '@eslint/js';
import tseslint from '@typescript-eslint/eslint-plugin';
import tsparser from '@typescript-eslint/parser';

export default [
  eslint.configs.recommended,
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: tsparser,
      parserOptions: {
        project: './tsconfig.json',
      },
    },
    plugins: {
      '@typescript-eslint': tseslint,
    },
    rules: {
      // Catch common AI mistakes
      'no-unused-vars': 'error',
      'no-undef': 'error',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'warn',

      // Security rules
      'no-eval': 'error',
      'no-implied-eval': 'error',
      'no-new-func': 'error',

      // Code quality
      'no-console': 'warn',  // AI often leaves console.logs
      'no-debugger': 'error',
      'prefer-const': 'error',
      'no-var': 'error',
    },
  },
];
```

### Pylint/Flake8 (Python)

**Installation**:

```bash
pip install flake8 pylint mypy black isort
```

**Flake8 configuration** (`.flake8`):

```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,build,dist,venv
ignore = E203,W503  # Conflicts with Black
per-file-ignores =
    __init__.py:F401
```

**Pylint configuration** (`.pylintrc` or `pyproject.toml`):

```toml
[tool.pylint.messages_control]
disable = [
    "missing-docstring",  # Can be noisy for small functions
    "too-few-public-methods",
]

[tool.pylint.format]
max-line-length = 100

[tool.pylint.design]
max-args = 7
max-locals = 15
```

### SonarQube/SonarCloud

For comprehensive static analysis, use SonarCloud (free for open source):

```yaml
# .github/workflows/sonar.yml
name: SonarCloud Analysis

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  sonarcloud:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: SonarCloud Scan
        uses: SonarSource/sonarcloud-github-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

Create `sonar-project.properties`:

```properties
sonar.projectKey=your-org_your-project
sonar.organization=your-org
sonar.sources=src
sonar.tests=tests
sonar.javascript.lcov.reportPaths=coverage/lcov.info
sonar.python.coverage.reportPaths=coverage.xml
```

---

## Security Scanning

### Dependency Vulnerability Scanning

**GitHub Dependabot** (enable in repository settings):

Create `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    reviewers:
      - "your-username"
    labels:
      - "dependencies"
      - "security"

  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

**npm audit** (for JavaScript):

```yaml
# In CI workflow
- name: Security audit
  run: npm audit --audit-level=high
```

**pip-audit** (for Python):

```bash
pip install pip-audit
pip-audit
```

### Static Application Security Testing (SAST)

**CodeQL** (GitHub's built-in security scanner):

> **Note**: CodeQL is **free for public repositories** but requires **GitHub Advanced Security** (paid enterprise feature) for private repositories. See [free alternatives below](#free-sast-alternatives-for-private-repos) if you're on a private repo.

```yaml
# .github/workflows/codeql.yml
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      matrix:
        language: ['javascript', 'python']  # Add your languages

    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-extended  # More thorough scanning

      - name: Autobuild
        uses: github/codeql-action/autobuild@v3

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

**Semgrep** (fast, customizable SAST - **free for all repos**):

```yaml
# .github/workflows/semgrep.yml
name: Semgrep

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten
```

### Free SAST Alternatives for Private Repos

If you're using a **private repository** and don't have GitHub Advanced Security, use these free alternatives instead of CodeQL:

| Tool | Best For | Setup Complexity |
|------|----------|------------------|
| **Semgrep** | All languages, highly customizable | Easy |
| **Bandit** | Python security | Easy |
| **Brakeman** | Ruby on Rails | Easy |
| **ESLint security plugins** | JavaScript/TypeScript | Easy |
| **Trivy** | Container & dependency scanning | Medium |

**Recommended: Semgrep** (shown above) - It's free, fast, supports most languages, and has excellent security rules out of the box.

**ESLint Security Plugin** (JavaScript/TypeScript):

```bash
npm install --save-dev eslint-plugin-security
```

Add to your ESLint config:
```javascript
// eslint.config.js
import security from 'eslint-plugin-security';

export default [
  // ... your config
  {
    plugins: { security },
    rules: {
      'security/detect-object-injection': 'warn',
      'security/detect-non-literal-regexp': 'warn',
      'security/detect-unsafe-regex': 'error',
      'security/detect-buffer-noassert': 'error',
      'security/detect-eval-with-expression': 'error',
      'security/detect-no-csrf-before-method-override': 'error',
      'security/detect-possible-timing-attacks': 'warn',
    },
  },
];
```

**Bandit** (Python):

```yaml
# Add to your CI workflow
- name: Run Bandit Security Scan
  run: |
    pip install bandit
    bandit -r src/ -ll -ii
```

**Trivy** (containers, filesystems, git repos):

```yaml
# .github/workflows/trivy.yml
name: Trivy Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'HIGH,CRITICAL'
```

### Secret Detection

**Gitleaks** (find secrets in git history):

```yaml
# .github/workflows/gitleaks.yml
name: Gitleaks

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Code Coverage

Code coverage measures how much of your code is tested. For AI-generated code, coverage is especially important—it ensures the generated code has corresponding tests.

### Coverage Requirements

**Minimum coverage thresholds**:
- **New code**: 80%+ coverage (enforce in CI)
- **Critical paths**: 90%+ coverage (auth, payments, data processing)
- **Overall project**: 70%+ (allow some legacy code)

### Jest Coverage (JavaScript/TypeScript)

**Configuration** (`jest.config.js`):

```javascript
module.exports = {
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  collectCoverageFrom: [
    'src/**/*.{js,ts,jsx,tsx}',
    '!src/**/*.d.ts',
    '!src/**/index.{js,ts}',  // Re-exports
    '!src/**/*.stories.{js,ts,jsx,tsx}',  // Storybook
  ],
};
```

### Pytest Coverage (Python)

**Configuration** (`pyproject.toml`):

```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

### Coverage in CI

```yaml
- name: Run tests with coverage
  run: npm test -- --coverage --coverageReporters=lcov

- name: Check coverage threshold
  run: |
    COVERAGE=$(cat coverage/lcov.info | grep -E "^LF:" | awk -F: '{sum+=$2} END {print sum}')
    COVERED=$(cat coverage/lcov.info | grep -E "^LH:" | awk -F: '{sum+=$2} END {print sum}')
    PERCENT=$((COVERED * 100 / COVERAGE))
    echo "Coverage: $PERCENT%"
    if [ $PERCENT -lt 80 ]; then
      echo "Coverage below 80%!"
      exit 1
    fi

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v4
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    fail_ci_if_error: true
```

---

## Testing Strategies for AI Code

AI-generated code needs specific testing approaches:

### 1. Test Immediately After Generation

**Prompt for the AI**:
```
After implementing this feature, write comprehensive tests including:
- Happy path tests
- Edge cases (empty inputs, null values, boundary conditions)
- Error cases (invalid inputs, network failures)
- Integration tests if applicable
```

### 2. Property-Based Testing

Property-based testing generates many test cases automatically—perfect for catching edge cases AI might miss:

**JavaScript** (fast-check):

```javascript
import fc from 'fast-check';

test('parseAmount handles any valid currency string', () => {
  fc.assert(
    fc.property(
      fc.float({ min: 0, max: 1000000 }),
      (amount) => {
        const formatted = formatCurrency(amount);
        const parsed = parseAmount(formatted);
        return Math.abs(parsed - amount) < 0.01;
      }
    )
  );
});
```

**Python** (hypothesis):

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_is_idempotent(xs):
    sorted_once = sorted(xs)
    sorted_twice = sorted(sorted_once)
    assert sorted_once == sorted_twice
```

### 3. Mutation Testing

Mutation testing modifies your code slightly and checks if tests catch the change. If tests pass with mutated code, they're not thorough enough:

**JavaScript** (Stryker):

```bash
npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner
npx stryker run
```

**Python** (mutmut):

```bash
pip install mutmut
mutmut run
```

### 4. Contract Testing

Ensure AI-generated APIs match expected contracts:

```javascript
// Using Pact for contract testing
const { Pact } = require('@pact-foundation/pact');

describe('User API Contract', () => {
  const provider = new Pact({
    consumer: 'Frontend',
    provider: 'UserService',
  });

  it('returns user by ID', async () => {
    await provider.addInteraction({
      state: 'user exists',
      uponReceiving: 'a request for user 1',
      withRequest: {
        method: 'GET',
        path: '/users/1',
      },
      willRespondWith: {
        status: 200,
        body: {
          id: 1,
          name: Matchers.string('John Doe'),
          email: Matchers.email(),
        },
      },
    });
  });
});
```

---

## Complete CI/CD Pipeline Example

Here's a comprehensive pipeline combining all checks:

```yaml
# .github/workflows/complete-ci.yml
name: Complete CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  NODE_VERSION: '20.x'

jobs:
  # Stage 1: Quick checks (fail fast)
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  # Stage 2: Tests (parallel with lint)
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

  # Stage 3: Security (parallel)
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run npm audit
        run: npm audit --audit-level=high
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: p/security-audit

  # Stage 4: Build (after lint + test pass)
  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: build
          path: dist/

  # Stage 5: Integration tests (after build)
  integration:
    needs: build
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run test:integration
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test

  # Stage 6: Deploy preview (PRs only)
  deploy-preview:
    if: github.event_name == 'pull_request'
    needs: [build, security]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: build
          path: dist/
      - name: Deploy to preview
        run: echo "Deploy preview here"

  # Stage 7: Deploy production (main only)
  deploy-production:
    if: github.ref == 'refs/heads/main'
    needs: [build, security, integration]
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: build
          path: dist/
      - name: Deploy to production
        run: echo "Deploy to production here"
```

---

## Quality Gate Checklist

Before code can be merged, ensure all gates pass:

### Automated Gates (CI Must Pass)

- [ ] All tests pass
- [ ] Code coverage >= 80%
- [ ] No linter errors
- [ ] No type errors
- [ ] No high/critical security vulnerabilities
- [ ] No secrets detected
- [ ] Build succeeds

### Human Review Gates

- [ ] Code reviewed line-by-line
- [ ] AI-generated code verified for correctness
- [ ] Security implications considered
- [ ] Architecture alignment checked
- [ ] Invariants not violated

---

## Troubleshooting Common Issues

### "Tests pass locally but fail in CI"

**Causes**:
- Environment differences (Node version, OS)
- Missing environment variables
- Race conditions in tests
- Timezone differences

**Solutions**:
- Use matrix testing for multiple Node/Python versions
- Add environment variables to CI secrets
- Use proper async/await and test isolation
- Mock time-dependent functions

### "Coverage dropped after AI-generated code"

**Causes**:
- AI generated code without tests
- Dead code was added
- Tests weren't updated for changes

**Solutions**:
- Always prompt AI to include tests
- Review coverage reports for uncovered lines
- Add missing tests before merging

### "Pre-commit hooks are slow"

**Solutions**:
- Use `stages` to run heavy hooks only on push
- Configure hooks to only run on changed files
- Skip hooks temporarily: `git commit --no-verify` (use sparingly!)

```yaml
# Run type-check only on push
- repo: local
  hooks:
    - id: mypy
      stages: [push]  # Only on push, not commit
```

---

## Verification Loops: The Most Important Pattern

**The single most important thing for getting great results from AI coding: give Claude a way to verify its work.**

If Claude has a feedback loop to check its own work, it will 2-3x the quality of the final result. Without verification, Claude is coding blind.

### Why Verification Matters

AI can generate code that:
- Looks correct but has subtle bugs
- Works in isolation but breaks integration
- Passes type checks but fails at runtime
- Handles happy paths but crashes on edge cases

**Verification catches these issues before you review the code.**

### Types of Verification Loops

**1. Test Suite Verification** (Most Common)

Prompt Claude to run tests after every change:

```
After making changes, always run `npm test` and fix any failures before reporting completion.
```

Or use a Stop hook to enforce it:

```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "npm test"
      }
    ]
  }
}
```

**2. Build Verification**

Ensure the code compiles/builds:

```
After implementing this feature:
1. Run `npm run build` to verify compilation
2. Fix any type errors or build failures
3. Only report completion when build succeeds
```

**3. Browser/UI Verification**

For frontend work, Claude can test in a real browser using the Claude Chrome extension:

```
After implementing this UI change:
1. Open the app in Chrome
2. Navigate to the affected page
3. Verify the feature works visually
4. Test user interactions
5. Iterate until the UX feels right
```

**4. Linter Verification**

Ensure code style compliance:

```
After every file edit, run `npm run lint` and fix any issues.
```

**5. Integration Verification**

For API or database changes:

```
After implementing this endpoint:
1. Start the dev server
2. Make test requests with curl
3. Verify responses match expected format
4. Test error cases
```

### Verification Subagents

For complex verification, create dedicated subagents:

```markdown
# .claude/agents/verify-app.md
---
name: verify-app
description: Comprehensive app verification. Use after completing features.
tools: Bash, Read
---

Run comprehensive verification:

1. Run the test suite: `npm test`
2. Run the linter: `npm run lint`
3. Build the project: `npm run build`
4. Start the dev server and verify it loads
5. Check for console errors
6. Report any failures with specific details
```

Then prompt Claude:

```
After implementing the feature, use the verify-app subagent to check everything works.
```

### Verification for Long-Running Tasks

For tasks that run autonomously for extended periods:

**Option A: Prompt-based verification**
```
When you finish, use a background subagent to verify your work before reporting completion.
```

**Option B: Stop hook verification**
```json
{
  "hooks": {
    "Stop": [
      {
        "type": "command",
        "command": "./scripts/full-verification.sh"
      }
    ]
  }
}
```

**Option C: Continuous verification plugin**
Use plugins like [ralph-wiggum](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-wiggum) for automated verification during long sessions.

### Domain-Specific Verification

Verification looks different for each domain:

| Domain | Verification Method |
|--------|-------------------|
| Backend API | Run test suite + curl requests |
| Frontend UI | Browser testing with Chrome extension |
| CLI tools | Run commands and check output |
| Libraries | Run unit tests + example usage |
| Data pipelines | Validate output data format |
| Infrastructure | Terraform plan + apply dry-run |

### Making Verification Rock-Solid

Invest time in making verification reliable:

1. **Fast feedback**: Verification should take seconds, not minutes
2. **Clear output**: Success/failure should be obvious
3. **Comprehensive**: Cover the common failure modes
4. **Automated**: No manual steps required

**If verification is slow or flaky, Claude won't use it effectively.**

### Verification Prompt Template

```
After completing this task:

1. Run tests: `npm test`
2. Run linter: `npm run lint`
3. Build: `npm run build`

If any step fails:
- Fix the issue
- Re-run verification
- Only report completion when ALL checks pass

Do not skip verification. Do not report success with failing tests.
```

---

## Summary

**Automation is not optional for AI-assisted development.** The speed of AI-generated code makes manual-only review insufficient. Implement:

1. **Pre-commit hooks** - Stop problems at the source
2. **Claude Code hooks** - Auto-format and verify during sessions
3. **CI/CD pipelines** - Consistent automated testing
4. **Static analysis** - Catch bugs before runtime
5. **Security scanning** - Find vulnerabilities automatically
6. **Coverage enforcement** - Ensure tests exist for AI code
7. **Quality gates** - Block merging until standards are met
8. **Verification loops** - Give Claude feedback to improve output quality 2-3x

**The investment in automation pays off immediately**: fewer bugs in production, faster code reviews, and confidence that AI-generated code meets your standards.

---

## Quick Start Checklist

Getting started with automation:

### Essential (Do First)
1. [ ] Install pre-commit: `pip install pre-commit && pre-commit install`
2. [ ] Create `.pre-commit-config.yaml` with basic hooks
3. [ ] Create `.github/workflows/ci.yml` for CI
4. [ ] Set up verification loop (make Claude run tests after changes)

### Recommended (Do Soon)
5. [ ] Add PostToolUse hook for auto-formatting
6. [ ] Enable Dependabot for dependency updates
7. [ ] Add security scanning (Semgrep for all repos, or CodeQL for public repos)
8. [ ] Configure coverage thresholds
9. [ ] Set up branch protection rules
10. [ ] Pre-allow safe commands in `.claude/settings.json`

### Advanced (As Needed)
11. [ ] Install Claude Code GitHub Action for PR reviews
12. [ ] Create verification subagents for complex workflows
13. [ ] Set up Stop hooks for automatic verification
14. [ ] Configure MCP servers for external tool access

**Start small and iterate.** Add more checks as you identify pain points. The verification loop is the highest-impact change you can make.
