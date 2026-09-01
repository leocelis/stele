<p align="center">
  <strong>Stele</strong><br>
  <em>The governed experiential-memory ledger for AI agents — log what worked and what failed, promote only oracle-verified lessons, and let any agent build solid context from real experience.</em>
</p>

---

## What is Stele?

A **stele** is a stone raised to record what happened — deeds, laws, warnings — for those who come after. Stele is the same idea for AI agents: a **centralized ledger of task experience**. Agents automatically log what worked and what failed on each task; a governance gate promotes only lessons backed by external evidence; and any agent — today's or a future one — retrieves the distilled experience through one protocol before its next task.

**Status: v18.16.1.** Design locked in [`stele_system_intent.yaml`](stele_system_intent.yaml). Packages: `stele-core` (zero runtime deps; optional `[mysql]`) + `stele-mcp` (stdio + hosted HTTP) + `stele` CLI.

## Why Stele (research-backed)

| Problem | Evidence | Stele answer |
|---|---|---|
| Recall wins ≠ better actions | MemoryArena (arXiv:2602.16313) | Task-outcome harnesses, not recall@k marketing |
| Self-reflection poisons stores | Survey (arXiv:2603.07670) | Quarantine + external oracle only |
| Every framework is a silo | memorywire (arXiv:2606.01138) | JSON Schema + projection helpers |
| Stale lessons mislead | LongMemEval (arXiv:2410.10813) | Bi-temporal supersede + stale_policy |

Full research: [`docs/research/`](docs/research/) · patterns: [`docs/patterns/`](docs/patterns/).

## Install

```bash
pip install stele-core stele-mcp
```

From git (contributors):

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e packages/stele-core -e packages/stele-mcp
make check   # ruff + mypy + pytest
make proof   # end-to-end PASS/FAIL proof
```

Quick path: [`docs/QUICKSTART.md`](docs/QUICKSTART.md) · comparison: [`docs/COMPARISON.md`](docs/COMPARISON.md).

## Quick start (library)

```python
from pathlib import Path
from stele_core import Stele

s = Stele.open(Path(".stele-store"), store_id="demo", now="2026-08-20T12:00:00Z")
added = s.add({
    "layer": "failure_lesson",
    "title": "Pin cache keys to calendar buckets",
    "body": "Day-scoped keys prevent stale cross-day reads.",
    "scope": "project:demo",
    "temporal": {"valid_from": "2026-08-20T12:00:00Z", "last_verified": "2026-08-20T12:00:00Z"},
    "provenance": {
        "agent": "agent-a", "task": "cache-fix", "environment": "local",
        "subject_id": "subj-1", "source": "session:abc",
        "written_at": "2026-08-20T12:00:00Z",
    },
})
# → {"id": "se_…", "state": "quarantined"}  — not searchable yet

s.promote(added["id"], [{
    "type": "test_result", "issuer": "ci", "ref": "tests/test_cache.py",
    "observed_at": "2026-08-20T12:00:00Z", "verdict": "supports",
    "command": "pytest -q", "exit_status": 0,
}], actor="ci", ts="2026-08-20T12:00:00Z")

print(s.search("cache buckets", consumer_scope="project:demo"))
print(s.doctor(now="2026-08-20T12:00:00Z")["ok"])
```

## CLI

```bash
stele init ./.stele-store --store-id demo
stele doctor ./.stele-store --now 2026-08-20T12:00:00Z
stele hygiene ./.stele-store --now 2026-08-20T12:00:00Z
stele entangled ./.stele-store --source web_page --now 2026-08-20T12:00:00Z
stele forget-check ./.stele-store --scope project:demo --subject-id subj-x --probe-query secret --now 2026-08-20T12:00:00Z
stele schema --out docs/schemas/entry.schema.json
stele snapshot ./.stele-store /tmp/stele-backup --now 2026-08-20T12:00:00Z --actor ops
```

## MCP (stdio)

Requires the Model Context Protocol Python SDK **1.x** (`mcp>=1.0,<2`).
mcp 2.x removed `mcp.server.fastmcp` and will not boot this server.

**Default (`stele-mcp`):** 35 governed-ledger tools — add, promote, search, doctor, export, …

```bash
export STELE_STORE=./.stele-store
stele-mcp
```

Full research library (~2000 PEFT/agent-pattern tools): `stele-mcp-full`.

## MCP (hosted HTTP)

Same tools over HTTPS (SSE + streamable HTTP). Two independent tool surfaces,
same process, same auth, same store:

| Surface | SSE | Streamable HTTP | Tools |
|---|---|---|---|
| Full | `/sse` | `/mcp` | 2003 (ledger + PEFT/pattern research library) |
| Core (governed ledger only) | `/core/sse` | `/core/mcp` | 35 — see list below |

Production:

- **URL:** `https://stele.leocelis.com/sse` · core: `https://stele.leocelis.com/core/sse` (Bearer required)
- Client setup: [`docs/integrations/CURSOR.md`](docs/integrations/CURSOR.md) · [`CLAUDE_CODE.md`](docs/integrations/CLAUDE_CODE.md) · [`CLAUDE_DESKTOP.md`](docs/integrations/CLAUDE_DESKTOP.md)
- Agent rule: [`docs/cursor-rules/stele-hosted-mcp.mdc`](docs/cursor-rules/stele-hosted-mcp.mdc)

Local run (dev):

```bash
bash deploy/build.sh
STELE_API_KEYS=stl_local_dev STELE_AUTH_DISABLED=false \
  STELE_STORE=./.stele-store \
  python deploy/wsgi.py --port 8080
```

- `GET /health` — unauthenticated; reports `tool_counts: {full, core}`
- `/sse` + `/mcp` (full) and `/core/sse` + `/core/mcp` (ledger-only) — both Bearer via `STELE_API_KEYS`
- Hosted durable SoT: `STELE_STORE_DSN` + TLS CA (DSN wins over file path)
- Never commit API keys, DSNs, or PEMs

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

**35 governed-ledger tools** (TECH_SPEC §7.1-7.9 — everything `create_core_app()` exposes):
add · update · promote · supersede · delete · search · reflect · link ·
list_contested · resolve_contested · verify · reviewer_corrections · hydrate · export ·
record_outcome · pin · stale_report · reverify · related · stats · timeline · verify_pack ·
attach · snapshot · doctor · entry_schema · purge_by_provenance · diff_stores · add_batch ·
entangled_suspects · hygiene_candidates · forget_compliance · lineage · belief_at · conflict_surface

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Planes: Contract · Tools · Governance · Retrieval · Export · Living ledger · Ops.

| Doc | Link |
|---|---|
| OSS guide (start here) | [`docs/OSS_GUIDE.md`](docs/OSS_GUIDE.md) |
| Quickstart | [`docs/QUICKSTART.md`](docs/QUICKSTART.md) |
| PRD | [`docs/PRD.md`](docs/PRD.md) |
| TECH_SPEC v1.1 | [`docs/TECH_SPEC.md`](docs/TECH_SPEC.md) |
| Entry JSON Schema | [`docs/schemas/entry.schema.json`](docs/schemas/entry.schema.json) |
| Intent (C1–C8) | [`stele_system_intent.yaml`](stele_system_intent.yaml) |

## License

MIT · Copyright (c) 2026 Stele contributors
