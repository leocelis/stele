# stele-mcp

MCP stdio server for [`stele-core`](../stele-core).

## Tools

| Tool | Role |
|---|---|
| `stele_add` | Quarantine a distilled entry |
| `stele_update` | Patch non-state fields |
| `stele_promote` | Oracle-gated promotion |
| `stele_supersede` | Invalidate old belief; new entry quarantined |
| `stele_delete` | True erase by entry or subject |
| `stele_search` | Budgeted hybrid retrieval |
| `stele_reflect` | Dedupe / expire / surface conflicts |
| `stele_list_contested` | Open conflict queue |
| `stele_resolve_contested` | Evidenced supersede of a contested pair |
| `stele_link` | Link entry → artifact/test/entry/source |

## Run

```bash
export STELE_STORE=./.stele-store
stele-mcp
```
