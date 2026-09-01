# Security Policy

## Reporting a vulnerability

Please report security issues privately via GitHub Security Advisories
("Report a vulnerability" on the repository's Security tab). Do not open
public issues for security reports.

You can expect an acknowledgment within 72 hours.

## Scope

Stele ships executable code: `stele-core` (library + CLI; optional MySQL SoT)
and `stele-mcp` (stdio MCP server + hosted HTTP via `deploy/wsgi.py`). Security
surface includes the store on disk or MySQL, pack export/hydrate, MCP tool
inputs, CLI argument handling, and hosted Bearer auth.

Commitments enforced by tests and the system intent:

- **Zero network / zero LLM calls on the core write path** (purity + static import scan).
  MySQL storage I/O for hosted SoT is allowed; it is not an LLM call.
- **Hosted auth fail-closed**: empty `STELE_API_KEYS` rejects non-health HTTP requests
  unless `STELE_AUTH_DISABLED=true` (local only). Never commit live keys/DSNs/PEMs.
- **Redact-at-export** for packs leaving a store (secret patterns + subject allowlist).
- **Subject-indexed erasure**: true `DELETE` (distinct from `SUPERSEDE`) with index rebuild.
- **Private-source path rejection** on ADD / adapters (C8) — selected redacted projection only.
- **Quarantine never served** until external-oracle promotion (C7).

Out of scope for this policy: vulnerabilities only in caller-supplied embedders,
oracles, or MCP hosts.

## Supported versions

| Version | Supported |
|---|---|
| 18.x | Yes (current) |
| < 18 | No |
