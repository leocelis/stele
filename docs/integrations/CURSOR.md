# Stele in Cursor (via MCP)

Stele exposes the governed experiential-memory ledger as MCP tools (`stele_add`,
`stele_promote`, `stele_search`, `stele_doctor`, …). Same tools on hosted HTTPS
and local stdio.

---

## 1. Register in Cursor

### Option A — Hosted endpoint (recommended)

Zero local Python. You need a Bearer key from the operator (`STELE_API_KEYS`).

Add to **`~/.cursor/mcp.json`** (merge into existing `mcpServers` — never wipe other servers):

```json
{
  "mcpServers": {
    "stele": {
      "url": "https://stele.leocelis.com/sse",
      "headers": { "Authorization": "Bearer YOUR_KEY_HERE" }
    }
  }
}
```

<<<<<<< HEAD
=======
If `stele.leocelis.com` does not resolve yet, use the App Platform ingress temporarily:

```json
"url": "https://stele-mcp-2vlrd.ondigitalocean.app/sse"
```

>>>>>>> origin/main
Reload MCP (Cursor Settings → Features → Model Context Protocol → toggle off/on).

> Hosted Stele uses durable MySQL SoT. Bearer auth is fail-closed. Never put live keys in the Stele git tree.

### Option B — local stdio

```bash
cd /path/to/stele
pip install -e packages/stele-core -e 'packages/stele-mcp'
export STELE_STORE=./.stele-store
```

```json
{
  "mcpServers": {
    "stele": {
      "command": "/path/to/stele/.venv/bin/stele-mcp",
      "env": { "STELE_STORE": "/path/to/stele/.stele-store" }
    }
  }
}
```

---

## 2. Agent instructions (Cursor rules)

Copy [`../cursor-rules/stele-hosted-mcp.mdc`](../cursor-rules/stele-hosted-mcp.mdc) into the
workspace `.cursor/rules/` (or enable the shipped copy) so the agent uses Stele
when experiential memory is needed — not as invisible monitoring.

---

## 3. Smoke check

After reload, the agent tool list should include `stele_*` tools. Quick probe:

1. Call `stele_doctor` with a fixed `now` ISO timestamp.
2. Expect JSON with `"ok": true` (empty store is fine).

Unauthorized calls against the hosted URL return HTTP 401.
