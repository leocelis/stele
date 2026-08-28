# Stele Architecture

**Version:** 1.0.0 · **Date:** 2026-08-20

Stele is a **governed experiential-memory protocol**: agents write distilled lessons, an external oracle promotes them, and any consumer retrieves a budgeted, still-valid slice — with zero LLM/network on the core write path.

```
┌─────────────────────────────────────────────────────────────┐
│  Agents / MCP hosts / CLI / library callers                 │
└───────────────┬─────────────────────────────┬───────────────┘
                │ stele-mcp (26 named tools)  │ stele CLI
                ▼                             ▼
┌─────────────────────────────────────────────────────────────┐
│  stele-core (zero runtime deps)                             │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ schema   │ │ governance │ │ retrieval│ │ export/pack  │ │
│  │ + JSON   │ │ quarantine │ │ BM25+opt │ │ hydrate      │ │
│  │ Schema   │ │ → promote  │ │ temporal │ │ verify_pack  │ │
│  └──────────┘ │ contested  │ └──────────┘ └──────────────┘ │
│               └────────────┘                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ store: files SoT + journal + attachments + lock      │   │
│  │ indexes under index/ are DERIVED (rebuildable)       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
        │ adapters (projection only — never import foreign frameworks or DB drivers)
        ▼
  project_receipt · judgment_entry · migration_entry
  to_memorywire_remember / from_memorywire_recall_hits
```

## Planes

| Plane | Role |
|---|---|
| **K Contract** | Entry schema, bi-temporal fields, scope rungs, JSON Schema export |
| **T Tools** | Six ops + promote/link + living ledger + ops + MCP/CLI |
| **G Governance** | Quarantine → external-oracle promote; contested surface; REFLECT |
| **R Retrieval** | Hybrid search, filters, budget, compress, link follow |
| **X Export** | Redacted packs, hydrate, verify_pack, snapshot |
| **L Living** | Outcomes, pin, stale_report, reverify |
| **O Ops** | verify, stats, timeline, attach, doctor |

## Hard boundaries

- **C5:** no LLM / no network on core write path.
- **C1:** stele-core is stdlib-only (no third-party product or DB imports).
- **C7:** writer cannot self-promote; self-issued evidence rejected.
- **C8:** private operator inventories never bulk-imported — selected redacted projection only.

## Docs map

| Doc | Purpose |
|---|---|
| `docs/PRD.md` | Product requirements + use cases |
| `docs/TECH_SPEC.md` | Schema, APIs, MCP, tests |
| `docs/schemas/entry.schema.json` | Machine contract |
| `docs/research/*` | Source-audited research |
| `stele_system_intent.yaml` | Constraints C1–C8 |

Full detail: [`TECH_SPEC.md`](TECH_SPEC.md).
