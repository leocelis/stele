# Stele in Claude Code (via MCP)

Same MCP tools as Cursor. Prefer the hosted endpoint + Bearer key.

---

## 1. Register in Claude Code

### Option A — Hosted (recommended)

```bash
claude mcp add --transport http stele https://stele.leocelis.com/sse \
  --header "Authorization: Bearer YOUR_KEY_HERE" \
  --scope user
```

DNS fallback:

```bash
claude mcp add --transport http stele https://stele-mcp-2vlrd.ondigitalocean.app/sse \
  --header "Authorization: Bearer YOUR_KEY_HERE" \
  --scope user
```

Verify:

```bash
claude mcp get stele
```

### Option B — Project `.mcp.json`

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

### Option C — local stdio

```bash
claude mcp add stele -- stele-mcp --scope user
```

(Requires `STELE_STORE` in the environment.)

---

## 2. Global instructions (`~/.claude/CLAUDE.md`)

Append the block from [`../cursor-rules/stele-hosted-mcp.mdc`](../cursor-rules/stele-hosted-mcp.mdc)
(plain-text section) so Claude Code uses Stele for governed memory without soft
“should I?” prompts. Hosted access **requires** the Bearer-configured MCP entry.
