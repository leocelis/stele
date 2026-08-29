# Stele integrations

| Client | Doc |
|---|---|
| Cursor | [CURSOR.md](./CURSOR.md) |
| Claude Code | [CLAUDE_CODE.md](./CLAUDE_CODE.md) |
| Claude Desktop | [CLAUDE_DESKTOP.md](./CLAUDE_DESKTOP.md) |

**Hosted MCP (recommended):** `https://stele.leocelis.com/sse`  
Requires `Authorization: Bearer <key>` (`STELE_API_KEYS` on the server).  
Fallback while DNS propagates: `https://stele-mcp-2vlrd.ondigitalocean.app/sse`

**Local stdio:** `stele-mcp` with `STELE_STORE` — no Bearer key (process isolation).

Never commit live API keys. Placeholders in these docs only.
