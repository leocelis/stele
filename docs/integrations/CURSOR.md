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
      "url": "https://stele.leocelis.com/core/sse",
      "headers": { "Authorization": "Bearer YOUR_KEY_HERE" }
    }
  }
}
```

Full research library (~2000 tools): use `https://stele.leocelis.com/sse` instead.

Reload MCP (Cursor Settings → Features → Model Context Protocol → toggle off/on).

> Hosted Stele uses durable MySQL SoT. Bearer auth is fail-closed. Never put live keys in the Stele git tree.

### Option B — local stdio

```bash
pip install stele-core stele-mcp
export STELE_STORE=./.stele-store
```

```json
{
  "mcpServers": {
    "stele": {
      "command": "stele-mcp",
      "env": { "STELE_STORE": "/path/to/.stele-store" }
    }
  }
}
```

Full research library: use `stele-mcp-full` as the command.

---

## 2. Agent instructions (Cursor rules)

Copy [`../cursor-rules/stele-hosted-mcp.mdc`](../cursor-rules/stele-hosted-mcp.mdc) into the
workspace `.cursor/rules/` (or enable the shipped copy) so the agent uses Stele
when experiential memory is needed — not as invisible monitoring.

---

## 3. Smoke check

After reload, the agent tool list should include `stele_*` tools (35 for default `stele-mcp`). Quick probe:

1. Call `stele_doctor` with a fixed `now` ISO timestamp.
2. Expect JSON with `"ok": true` (empty store is fine).

Unauthorized calls against the hosted URL return HTTP 401.
