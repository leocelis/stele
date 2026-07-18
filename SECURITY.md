# Security Policy

## Reporting a vulnerability

Please report security issues privately via GitHub Security Advisories
("Report a vulnerability" on the repository's Security tab). Do not open
public issues for security reports.

You can expect an acknowledgment within 72 hours.

## Scope

Stele is currently a **design-phase repository** (research, patterns, and a
system intent — no executable code). Until implementation lands, the security
surface is documentation only.

Security-relevant design commitments already locked in the intent, which
implementation will be held to:

- **Zero network / zero LLM calls on the core write path** (test-enforced
  purity, static import scan).
- **Redact-at-export** as a first-class step for any pack leaving a store —
  leakage is treated as a trajectory-level property, not a per-message one.
- **Subject-indexed erasure**: true `DELETE` (distinct from `SUPERSEDE`)
  with erasure propagation through all derived indexes.
- **No secrets in entries**: the schema review at promotion time is the
  enforcement point; quarantined entries are never served.

If you spot a way the *design* itself enables a leak or an unsafe default,
that is in scope — report it the same way.

## Supported versions

No releases yet. This policy activates for code with the first tagged release.
