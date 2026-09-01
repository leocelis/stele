# Stele in Claude Code (via MCP)

Same MCP tools as Cursor. Prefer the hosted **core** endpoint + Bearer key.

**Default vs full.** `stele-mcp` (stdio) and `/core/sse` (hosted) expose the 35-tool
governed ledger. `stele-mcp-full` and `/sse` add ~2000 PEFT/agent-pattern research tools.

---

## 1. Register in Claude Code

### Option A — Hosted (recommended)

```bash
claude mcp add --transport http stele https://stele.leocelis.com/core/sse \
  --header "Authorization: Bearer YOUR_KEY_HERE" \
  --scope user
```

Full research library:

```bash
claude mcp add --transport http stele-full https://stele.leocelis.com/sse \
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
      "url": "https://stele.leocelis.com/core/sse",
      "headers": { "Authorization": "Bearer YOUR_KEY_HERE" }
    }
  }
}
```

### Option C — local stdio

```bash
pip install stele-core stele-mcp
claude mcp add stele -- stele-mcp --scope user
```

(Requires `STELE_STORE` in the environment.)

Full library: `stele-mcp-full` instead of `stele-mcp`.

---

## 2. Global instructions (`~/.claude/CLAUDE.md`)

Append the block from [`../cursor-rules/stele-hosted-mcp.mdc`](../cursor-rules/stele-hosted-mcp.mdc)
(plain-text section) so Claude Code uses Stele for governed memory without soft
“should I?” prompts. Hosted access **requires** the Bearer-configured MCP entry.
