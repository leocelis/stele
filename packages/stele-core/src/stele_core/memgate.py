"""MemGate-shaped query-conditioned retrieval admission (stdlib; no neural gate).

Between Select hits and reader context: admit only task-conditioned memories.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def retrieval_admit(
    query: str,
    hits: Sequence[Mapping[str, Any]],
    *,
    min_overlap: float = 0.15,
    withhold_injection: bool = True,
    consumer_domain: str | None = None,
) -> dict[str, Any]:
    """
    Query-conditioned admission over candidate hits.

    Drops low-overlap, injection-suspect, and domain-mismatched rows.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    if not (0 <= min_overlap <= 1):
        raise SchemaError("min_overlap must be in [0, 1]")
    qtok = set(tokenize(q))
    admitted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for h in hits:
        eid = str(h.get("id") or "")
        blob = f"{h.get('title') or ''}\n{h.get('body') or ''}"
        etok = set(tokenize(blob))
        overlap = len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0
        reason = None
        if withhold_injection:
            low = blob.lower()
            if "ignore prior" in low or "jailbreak" in low:
                reason = "injection_suspect"
        if reason is None and overlap < min_overlap:
            reason = "low_query_overlap"
        if reason is None and consumer_domain:
            # Optional domain from assessment or title cue
            domain = str(
                (h.get("assessment") or {}).get("domain_depth")
                or h.get("domain")
                or ""
            )
            # Soft: only reject if entry declares a different domain token
            if domain and consumer_domain not in domain and domain not in consumer_domain:
                # Don't hard-reject on domain alone when overlap is strong
                if overlap < min_overlap + 0.2:
                    reason = "domain_mismatch"
        if reason:
            rejected.append(
                {
                    "id": eid,
                    "title": h.get("title"),
                    "reason": reason,
                    "overlap": round(overlap, 4),
                }
            )
            continue
        admitted.append(
            {
                "id": eid,
                "title": h.get("title"),
                "overlap": round(overlap, 4),
                "state": h.get("state"),
            }
        )

    return {
        "query": q,
        "admitted": admitted,
        "rejected": rejected,
        "admit_count": len(admitted),
        "reject_count": len(rejected),
        "min_overlap": min_overlap,
        "ok": True,
        "note": "MemGate retrieval_admit — query-conditioned; not 9M neural gate",
    }


def task_conditioned_pack(
    query: str,
    hits: Sequence[Mapping[str, Any]],
    *,
    budget: int = 400,
    min_overlap: float = 0.15,
) -> dict[str, Any]:
    """Admit then pack until token budget."""
    gate = retrieval_admit(query, hits, min_overlap=min_overlap)
    used = 0
    pack: list[dict[str, Any]] = []
    by_id = {str(h.get("id")): h for h in hits}
    for row in gate.get("admitted") or []:
        e = by_id.get(str(row.get("id"))) or row
        text = f"{e.get('title') or ''}\n{e.get('body') or ''}"
        cost = max(1, len(text.split()))
        if used + cost > budget:
            break
        pack.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "overlap": row.get("overlap"),
                "chars": len(text),
            }
        )
        used += cost
    return {
        "query": query,
        "pack": pack,
        "used": used,
        "budget": budget,
        "gate": {
            "admit_count": gate.get("admit_count"),
            "reject_count": gate.get("reject_count"),
        },
        "ok": True,
        "note": "MemGate task_conditioned_pack — admitted hits under budget",
    }
