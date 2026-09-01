# Stele integrations

| Client | Doc |
|---|---|
| Cursor | [CURSOR.md](./CURSOR.md) |
| Claude Code | [CLAUDE_CODE.md](./CLAUDE_CODE.md) |
| Claude Desktop | [CLAUDE_DESKTOP.md](./CLAUDE_DESKTOP.md) |

**Hosted MCP (recommended):** `https://stele.leocelis.com/sse`  
Requires `Authorization: Bearer <key>` (`STELE_API_KEYS` on the server).  
<<<<<<< HEAD
=======
Fallback while DNS propagates: `https://stele-mcp-2vlrd.ondigitalocean.app/sse`
>>>>>>> origin/main

**Core-only surface (governed ledger tools, ~34):** `https://stele.leocelis.com/core/sse`  
Same Bearer auth. Use this when you do not want the full ~2000-tool research surface.

**Local stdio:** `stele-mcp` with `STELE_STORE` — no Bearer key (process isolation).  
Core-only stdio: `stele-mcp-core` or `STELE_TOOL_SET=core stele-mcp`.

Never commit live API keys. Placeholders in these docs only.
