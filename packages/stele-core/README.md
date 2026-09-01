# stele-core

Governed experiential-memory ledger for AI agents.

Agents `ADD` distilled lessons into **quarantine**. Promotion requires
**external-oracle evidence**. Retrieval serves **promoted** entries only
(hybrid keyword + optional semantic + temporal), budgeted as slices.
Exports are redacted **packs** — the live store is never the sharing surface.

**Zero runtime dependencies.** Callers supply an optional embedder callable
for semantic search; the default path never networks and never calls an LLM.

## Install

```bash
pip install -e packages/stele-core
```

## Quick start

```python
from pathlib import Path
from stele_core import Stele

store = Stele.open(Path("./.stele-store"), store_id="demo")
result = store.add({
    "layer": "failure_lesson",
    "title": "Pin cache keys to calendar buckets",
    "body": "Day-scoped keys prevent stale cross-day reads.",
    "scope": "project:demo",
    "temporal": {"valid_from": "2026-08-20T00:00:00Z", "last_verified": "2026-08-20T00:00:00Z"},
    "provenance": {
        "agent": "agent-a",
        "task": "cache-fix",
        "environment": "local",
        "subject_id": "subj-demo",
        "source": "session:abc",
        "written_at": "2026-08-20T12:00:00Z",
    },
})
# result == {"id": "se_...", "state": "quarantined"}
```

See the repo [`docs/TECH_SPEC.md`](../../docs/TECH_SPEC.md) for the full contract.
