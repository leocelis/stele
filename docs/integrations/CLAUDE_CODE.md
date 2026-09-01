# Stele in Claude Code (via MCP)

Same MCP tools as Cursor. Prefer the hosted endpoint + Bearer key.

**Full vs. core.** The full server exposes 2003 tools: the 35-tool governed
ledger plus ~1970 PEFT/agent-pattern research-reproduction tools (see
`../../ROADMAP.md`). If you only want the ledger — `stele_add` / `stele_promote`
/ `stele_search` / `stele_doctor` / etc. — use the `/core/sse` URL or the
`stele-mcp-core` command below instead of `/sse` / `stele-mcp`. Every option
below has a core-only variant.

---

## 1. Register in Claude Code

### Option A — Hosted (recommended)

```bash
claude mcp add --transport http stele https://stele.leocelis.com/sse \
  --header "Authorization: Bearer YOUR_KEY_HERE" \
  --scope user
```

Core-only (governed ledger, 35 tools — no PEFT/pattern research tools):

```bash
claude mcp add --transport http stele https://stele.leocelis.com/core/sse \
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

Core-only: use `"url": "https://stele.leocelis.com/core/sse"` instead.

### Option C — local stdio

```bash
claude mcp add stele -- stele-mcp --scope user
```

Core-only (governed ledger, 35 tools):

```bash
claude mcp add stele -- stele-mcp-core --scope user
```

(Requires `STELE_STORE` in the environment.)

---

## 2. Global instructions (`~/.claude/CLAUDE.md`)

Append the block from [`../cursor-rules/stele-hosted-mcp.mdc`](../cursor-rules/stele-hosted-mcp.mdc)
(plain-text section) so Claude Code uses Stele for governed memory without soft
“should I?” prompts. Hosted access **requires** the Bearer-configured MCP entry.
