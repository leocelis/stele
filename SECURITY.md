# Security Policy

## Reporting a vulnerability

Please report security issues privately via GitHub Security Advisories
("Report a vulnerability" on the repository's Security tab). Do not open
public issues for security reports.

You can expect an acknowledgment within 72 hours.

## Scope

Stele **v1.0** ships executable code: `stele-core` (library + CLI) and
`stele-mcp` (stdio MCP server). Security surface includes the store on disk,
pack export/hydrate, MCP tool inputs, and CLI argument handling.

Commitments enforced by tests and the system intent:

- **Zero network / zero LLM calls on the core write path** (purity + static import scan).
- **Redact-at-export** for packs leaving a store (secret patterns + subject allowlist).
- **Subject-indexed erasure**: true `DELETE` (distinct from `SUPERSEDE`) with index rebuild.
- **Private-source path rejection** on ADD / adapters (C8) — selected redacted projection only.
- **Quarantine never served** until external-oracle promotion (C7).

Out of scope for this policy: vulnerabilities only in caller-supplied embedders,
oracles, or MCP hosts.

## Supported versions

| Version | Supported |
|---|---|
| 1.0.x | Yes |
| < 1.0 | No (pre-release) |
