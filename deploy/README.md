# Deploy Stele MCP (BYO hosting)

Production entry: `deploy/wsgi.py`.

## Required env

| Variable | Purpose |
|----------|---------|
| `STELE_API_KEYS` | Bearer keys (comma-separated). Empty = fail-closed except `/health`. |
| `STELE_STORE` | File store path (dev/single-node) |
| `STELE_STORE_DSN` | MySQL DSN (production — wins over `STELE_STORE`) |
| `STELE_MYSQL_SSL_CA` | TLS CA PEM path for managed MySQL |
| `STELE_MYSQL_SSL_CA_B64` | Same PEM, base64-encoded |
| `STELE_AUTH_DISABLED` | `true` local only — never production |

## Routes

| Path | Auth | Tools |
|------|------|-------|
| `/health` | No | Status + `tool_counts` |
| `/core/sse` | Bearer | 35 ledger tools (**recommended**) |
| `/core/mcp` | Bearer | 35 ledger tools |
| `/sse` | Bearer | Full (~2000) |
| `/mcp` | Bearer | Full |

## DigitalOcean App Platform

1. Connect repo, branch `main`.
2. Build: `bash deploy/build.sh`
3. Run: `python deploy/wsgi.py --port 8080`
4. Attach managed MySQL OR set `STELE_STORE` on a persistent volume.
5. Set `STELE_API_KEYS` in the platform console (never commit).

## Smoke

```bash
curl -s https://YOUR_HOST/health | jq .
curl -s -o /dev/null -w "%{http_code}\n" https://YOUR_HOST/core/sse
# expect 401 without Bearer
```

See `docs/HOSTED_API.md`.
