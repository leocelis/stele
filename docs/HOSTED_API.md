# Hosted Stele HTTP API

## GET /health

Unauthenticated.

```json
{
  "status": "healthy",
  "server": "stele",
  "version": "18.16.1",
  "store_mode": "mysql",
  "tool_counts": { "full": 2003, "core": 35 },
  "recommended_surface": "core",
  "docs_url": "https://github.com/leocelis/stele/blob/main/docs/QUICKSTART.md"
}
```

## MCP transports

- **Recommended:** `/core/sse` + `Authorization: Bearer <key>`
- Streamable HTTP: `/core/mcp`
- Full research library: `/sse`, `/mcp`

## Errors

| HTTP | Meaning |
|------|---------|
| 401 | Missing/invalid Bearer |
| 404 | Wrong path (use `/core/sse` for ledger-only) |

## Rate limits

When enabled, responses may include `Retry-After`. Document operator limits in your deployment runbook.
