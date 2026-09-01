# Stele integrations

| Client | Doc |
|---|---|
| Cursor | [CURSOR.md](./CURSOR.md) |
| Claude Code | [CLAUDE_CODE.md](./CLAUDE_CODE.md) |
| Claude Desktop | [CLAUDE_DESKTOP.md](./CLAUDE_DESKTOP.md) |

**Hosted MCP (recommended):** `https://stele.leocelis.com/core/sse`  
Requires `Authorization: Bearer <key>` (`STELE_API_KEYS` on the server).

**Full research surface (~2000 tools):** `https://stele.leocelis.com/sse`  
Same Bearer auth. Use only when you need the PEFT/pattern research library.

**Local stdio:** `stele-mcp` with `STELE_STORE` — 35 ledger tools (default).  
Full library: `stele-mcp-full`.

Never commit live API keys. Placeholders in these docs only.
