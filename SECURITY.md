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
- **Hosted auth fail-closed**: empty `STELE_API_KEYS` (and no `STELE_TENANT_KEY_SECRET`)
  rejects non-health HTTP requests unless `STELE_AUTH_DISABLED=true` (local only). Never commit live keys/DSNs/PEMs.
- **Redact-at-export** for packs leaving a store (secret patterns + subject allowlist).
- **Subject-indexed erasure**: true `DELETE` (distinct from `SUPERSEDE`) with index rebuild.
- **Private-source path rejection** on ADD / adapters (C8) — selected redacted projection only.
- **Quarantine never served** until external-oracle promotion (C7).

### Derived tenant keys (multi-tenant hosts)

When `STELE_TENANT_KEY_SECRET` is set, the hosted server also accepts keys a
host app derives for its own tenants (TECH_SPEC §12,
[`docs/integrations/HOST_APP.md`](docs/integrations/HOST_APP.md)):

- **Key shape**: `stl_<tenant>_<base64url_nopad(HMAC-SHA256(secret, "stl:<version>:<tenant>"))>`.
  Tenant names match `^[a-z0-9][a-z0-9-]{0,55}$`. The MAC is compared in constant time;
  the tenant is read as the text between the prefix and the last 44 characters.
  Neither side stores the key. `STELE_TENANT_KEY_VERSIONS` (default `v1`) lists accepted
  versions, so the secret can be rotated by adding a version; `STELE_REVOKED_TENANTS`
  refuses named tenants at once.
- **Fail-closed** only when both `STELE_API_KEYS` and `STELE_TENANT_KEY_SECRET` are empty.
- **Core only**: a tenant key is refused on `/sse`, `/messages` and `/mcp`; it is served
  only under `/core/*`.
- **A store per tenant**: a tenant key opens store `t-<tenant>` with its own scratch root.
  Tenant keys are refused on the file store (MySQL `STELE_STORE_DSN` only). A store opened
  with an explicit id never adopts another store's row.
- **Allowlist**: a tenant key may list and call only `stele_search`, `stele_add`,
  `stele_promote`, `stele_delete` and `stele_list`. Tools that take server paths
  (`stele_export`, `stele_snapshot`, `stele_hydrate`, `stele_diff_stores`) and every other
  tool are refused.
- **Identity per message**: each MCP message runs as the key on its own HTTP request, and an
  MCP session is bound to the identity of its first message; a later message signed by
  another tenant or an operator key is refused.
- **Not the server's job**: the host fills entry provenance and builds promotion evidence
  from someone other than the writer; the server cannot tell a host's own spaces apart.

Out of scope for this policy: vulnerabilities only in caller-supplied embedders,
oracles, or MCP hosts.

## Supported versions

| Version | Supported |
|---|---|
| 18.x | Yes (current) |
| < 18 | No |
