# Threat Model

## Overview

**System Name**: [Your system name]

**Version**: [Document version]

**Last Updated**: [Date]

**Threat Model Owner**: [Name/Team]

---

## Purpose

This document identifies potential security threats to the system, assesses their risk, and documents mitigations. It should be reviewed:

- Before major feature implementations
- When adding new external integrations
- When changing authentication/authorization
- After security incidents
- Quarterly (at minimum)

**For AI-assisted development**: Review this document before prompting an LLM to implement security-sensitive features. Include relevant sections in your prompt context.

---

## System Description

### What Are We Protecting?

**Primary Assets**:
| Asset | Description | Sensitivity |
|-------|-------------|-------------|
| [User credentials] | [Passwords, API keys, tokens] | Critical |
| [User PII] | [Names, emails, addresses] | High |
| [Business data] | [Transactions, analytics] | High |
| [System secrets] | [Database credentials, signing keys] | Critical |

**Secondary Assets**:
| Asset | Description | Sensitivity |
|-------|-------------|-------------|
| [Logs] | [Application and access logs] | Medium |
| [Configuration] | [Non-secret settings] | Low |

### System Architecture Overview

```
[ASCII diagram or reference to ARCHITECTURE.md]

Example:
┌──────────────┐     HTTPS      ┌──────────────┐     Internal    ┌──────────────┐
│   Browser    │◄──────────────►│  API Server  │◄───────────────►│   Database   │
└──────────────┘                └──────────────┘                 └──────────────┘
                                       │
                                       ▼
                                ┌──────────────┐
                                │ Third-party  │
                                │    APIs      │
                                └──────────────┘
```

### Trust Boundaries

Trust boundaries separate components with different trust levels. Data crossing these boundaries requires validation.

| Boundary | From | To | Data Crossing |
|----------|------|-----|---------------|
| TB-1 | Internet | API Server | User requests, auth tokens |
| TB-2 | API Server | Database | Queries, user data |
| TB-3 | API Server | Third-party APIs | API calls, credentials |
| TB-4 | Admin Network | Internal Systems | Admin commands |

---

## Threat Actors

### Who Might Attack?

| Actor | Motivation | Capability | Likelihood |
|-------|------------|------------|------------|
| **External Attacker** | Financial gain, data theft | Medium-High | High |
| **Script Kiddie** | Curiosity, reputation | Low | High |
| **Malicious Insider** | Revenge, financial gain | High (has access) | Low |
| **Competitor** | Business advantage | Medium | Low-Medium |
| **Nation State** | Espionage, disruption | Very High | [Depends on domain] |

### What Do They Want?

- [ ] User credentials
- [ ] Personal data (PII)
- [ ] Financial data
- [ ] System access/control
- [ ] Service disruption
- [ ] Reputation damage
- [ ] [Other: specify]

---

## STRIDE Threat Analysis

STRIDE is a threat classification model:
- **S**poofing - Pretending to be someone else
- **T**ampering - Modifying data or code
- **R**epudiation - Denying actions taken
- **I**nformation Disclosure - Exposing data to unauthorized parties
- **D**enial of Service - Making system unavailable
- **E**levation of Privilege - Gaining unauthorized access levels

### Spoofing Threats

| ID | Threat | Target | Mitigation | Status |
|----|--------|--------|------------|--------|
| S-1 | [Credential stuffing] | [Login endpoint] | [Rate limiting, MFA] | [Implemented] |
| S-2 | [Session hijacking] | [Session tokens] | [Secure cookies, short expiry] | [Implemented] |
| S-3 | [API key theft] | [API authentication] | [Key rotation, scoping] | [Partial] |

### Tampering Threats

| ID | Threat | Target | Mitigation | Status |
|----|--------|--------|------------|--------|
| T-1 | [SQL injection] | [Database queries] | [Parameterized queries] | [Implemented] |
| T-2 | [Request tampering] | [API parameters] | [Input validation, signing] | [Implemented] |
| T-3 | [File upload exploits] | [Upload endpoints] | [Type validation, sandboxing] | [Needs review] |

### Repudiation Threats

| ID | Threat | Target | Mitigation | Status |
|----|--------|--------|------------|--------|
| R-1 | [Denying transactions] | [Financial operations] | [Audit logging, signing] | [Implemented] |
| R-2 | [Log tampering] | [Audit logs] | [Append-only logs, checksums] | [Partial] |

### Information Disclosure Threats

| ID | Threat | Target | Mitigation | Status |
|----|--------|--------|------------|--------|
| I-1 | [Data breach via injection] | [User database] | [Parameterized queries, encryption at rest] | [Implemented] |
| I-2 | [Verbose error messages] | [API responses] | [Generic errors in production] | [Implemented] |
| I-3 | [Log data exposure] | [Application logs] | [PII scrubbing, access controls] | [Needs review] |
| I-4 | [Man-in-the-middle] | [Network traffic] | [TLS everywhere, cert pinning] | [Implemented] |

### Denial of Service Threats

| ID | Threat | Target | Mitigation | Status |
|----|--------|--------|------------|--------|
| D-1 | [API flooding] | [All endpoints] | [Rate limiting, WAF] | [Implemented] |
| D-2 | [Resource exhaustion] | [Server resources] | [Request size limits, timeouts] | [Partial] |
| D-3 | [Database DoS] | [Expensive queries] | [Query timeouts, pagination] | [Implemented] |

### Elevation of Privilege Threats

| ID | Threat | Target | Mitigation | Status |
|----|--------|--------|------------|--------|
| E-1 | [IDOR vulnerabilities] | [Resource access] | [Authorization checks on every request] | [Implemented] |
| E-2 | [JWT manipulation] | [Auth tokens] | [Signature verification, short expiry] | [Implemented] |
| E-3 | [Admin function exposure] | [Admin endpoints] | [Role-based access, network segregation] | [Needs review] |

---

## Attack Surface

### External Attack Surface

| Entry Point | Protocol | Authentication | Exposed To |
|-------------|----------|----------------|------------|
| [Web application] | HTTPS | [Session cookie] | Internet |
| [REST API] | HTTPS | [JWT/API key] | Internet |
| [WebSocket] | WSS | [Session token] | Internet |
| [Admin panel] | HTTPS | [MFA required] | VPN only |

### Internal Attack Surface

| Entry Point | Protocol | Authentication | Exposed To |
|-------------|----------|----------------|------------|
| [Database] | [PostgreSQL] | [Password + TLS] | App servers only |
| [Cache] | [Redis] | [Password] | App servers only |
| [Message queue] | [AMQP] | [Credentials] | Internal services |

### Data Flow Attack Surface

```
User Input → [Validation] → Processing → [Sanitization] → Output
                 ↓                              ↓
            Reject invalid              Encode for context
```

**Critical data flows to protect**:
1. [Authentication flow - credentials must never be logged]
2. [Payment flow - PCI compliance required]
3. [PII handling - GDPR/privacy compliance]

---

## Risk Assessment

### Risk Matrix

| Likelihood ↓ / Impact → | Low | Medium | High | Critical |
|-------------------------|-----|--------|------|----------|
| **High** | Medium | High | Critical | Critical |
| **Medium** | Low | Medium | High | Critical |
| **Low** | Low | Low | Medium | High |

### Prioritized Risks

| Rank | Threat ID | Risk Level | Mitigation Status | Owner |
|------|-----------|------------|-------------------|-------|
| 1 | [I-1] | Critical | Implemented | [Team] |
| 2 | [E-1] | High | Implemented | [Team] |
| 3 | [T-3] | High | Needs review | [Team] |
| 4 | [S-1] | Medium | Implemented | [Team] |

---

## Security Controls

### Preventive Controls

| Control | Protects Against | Implementation |
|---------|------------------|----------------|
| Input validation | Injection attacks | All user input validated server-side |
| Parameterized queries | SQL injection | ORM with parameterization |
| Output encoding | XSS | Context-aware encoding |
| Authentication | Unauthorized access | [OAuth2/JWT/Session] |
| Authorization | Privilege escalation | RBAC on every endpoint |
| Rate limiting | DoS, brute force | [X] requests per [time] per [scope] |
| TLS | Man-in-the-middle | TLS 1.2+ required |

### Detective Controls

| Control | Detects | Implementation |
|---------|---------|----------------|
| Audit logging | Unauthorized actions | All auth events logged |
| Anomaly detection | Unusual patterns | [Tool/approach] |
| Security scanning | Vulnerabilities | CI/CD integrated (Semgrep, etc.) |
| Dependency scanning | Known CVEs | Dependabot/Snyk |

### Corrective Controls

| Control | Responds To | Implementation |
|---------|-------------|----------------|
| Incident response | Security breaches | [Runbook location] |
| Secret rotation | Credential compromise | [Rotation procedure] |
| Account lockout | Brute force | Lock after [N] failures |
| Session invalidation | Token theft | Invalidate all sessions on password change |

---

## AI-Assisted Development Considerations

When using LLMs to implement security-sensitive code:

### High-Risk Areas (Require Extra Review)

- [ ] Authentication/authorization logic
- [ ] Cryptographic operations
- [ ] Input validation and sanitization
- [ ] Database queries with user input
- [ ] File operations with user-controlled paths
- [ ] Deserialization of untrusted data
- [ ] API endpoint access controls

### Prompt Guidance

When prompting for security-sensitive features, include:

```
Security requirements:
- All user input must be validated against [specific rules]
- Use parameterized queries for all database operations
- Implement rate limiting of [X] requests per [time period]
- Log security events to audit log
- Follow principle of least privilege

Refer to THREAT_MODEL.md section [X] for specific threats to mitigate.
```

### Common AI Security Mistakes

Watch for these in AI-generated code:
- String interpolation in SQL queries
- Missing authorization checks
- Verbose error messages with stack traces
- Hardcoded secrets
- Missing input validation
- Insecure cryptographic choices
- CORS misconfigurations
- Missing rate limiting

---

## Compliance Requirements

| Requirement | Applies To | Status | Evidence |
|-------------|------------|--------|----------|
| [GDPR] | [EU user data] | [Compliant] | [Documentation link] |
| [PCI-DSS] | [Payment data] | [N/A or Compliant] | [Documentation link] |
| [SOC 2] | [Customer data] | [In progress] | [Documentation link] |
| [HIPAA] | [Health data] | [N/A or Compliant] | [Documentation link] |

---

## Open Issues & Action Items

| Issue | Severity | Owner | Due Date | Status |
|-------|----------|-------|----------|--------|
| [T-3: File upload validation] | High | [Name] | [Date] | Open |
| [I-3: Log PII scrubbing] | Medium | [Name] | [Date] | In Progress |
| [E-3: Admin endpoint audit] | Medium | [Name] | [Date] | Open |

---

## Review History

| Date | Reviewer | Changes | Next Review |
|------|----------|---------|-------------|
| [YYYY-MM-DD] | [Name] | Initial creation | [Date] |
| [YYYY-MM-DD] | [Name] | Added [X] threats | [Date] |

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [STRIDE Threat Model](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- Project ARCHITECTURE.md
- Project INVARIANTS.md (Security Invariants section)
