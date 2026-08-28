"""Evo-Memory-shaped streaming self-evolving memory (stdlib; no LLM).

Shaped by Evo-Memory (arXiv:2511.20857): search–predict–evolve protocol,
ExpRAG task-level experience retrieve, ReMem think/act/refine loop.
Proxies only — not Evo-Memory paper scores. Distinct from REMem (`remem.py`).
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)
SPE_STEPS = ("search", "predict", "evolve")
REFINE_ACTIONS = frozenset({"retrieve", "prune", "organize", "noop"})


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def streaming_task_append(
    memory: Sequence[Mapping[str, Any]],
    *,
    task: str,
    prediction: str = "",
    outcome: str = "unknown",
) -> dict[str, Any]:
    """Append a task-level experience to the streaming memory bank."""
    if not isinstance(task, str) or not task.strip():
        raise SchemaError("task required")
    if outcome not in {"success", "failure", "unknown"}:
        raise SchemaError("outcome must be success|failure|unknown")
    eid = hashlib.sha256(
        canonical_dumps(
            {"t": task, "p": prediction[:80], "o": outcome}
        ).encode("utf-8")
    ).hexdigest()[:12]
    entry = {
        "experience_id": eid,
        "task": task.strip()[:120],
        "prediction": (prediction or "").strip()[:240],
        "outcome": outcome,
    }
    next_mem = [dict(m) for m in memory if isinstance(m, Mapping)] + [entry]
    return {
        "entry": entry,
        "next_memory": next_mem,
        "memory_size": len(next_mem),
        "apply": False,
        "ok": True,
        "note": "evomemory streaming_task_append",
    }


def exprag_retrieve(
    memory: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """ExpRAG: retrieve similar prior task experiences."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    scored: list[tuple[int, dict[str, Any]]] = []
    for m in memory:
        if not isinstance(m, Mapping):
            continue
        blob = f"{m.get('task') or ''} {m.get('prediction') or ''}"
        score = len(qtok & _tokens(blob))
        scored.append((score, dict(m)))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("experience_id") or "")))
    hits = [e for sc, e in scored[:top_k]]
    return {
        "query": query.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "evomemory exprag_retrieve",
    }


def search_predict_evolve_check(steps: Sequence[str]) -> dict[str, Any]:
    """Validate search → predict → evolve order (Evo-Memory protocol)."""
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
        raise SchemaError("steps sequence required")
    norm = [str(s).strip().lower() for s in steps if str(s).strip()]
    valid = norm == list(SPE_STEPS)
    return {
        "valid": valid,
        "steps": norm,
        "expected": list(SPE_STEPS),
        "ok": True,
        "note": "evomemory search_predict_evolve_check",
    }


def evomem_refine_plan(
    *,
    memory_size: int,
    max_memory: int = 50,
    retrieval_hit: bool = True,
    noisy: bool = False,
) -> dict[str, Any]:
    """
    ReMem-shaped refine actions: retrieve / prune / organize / noop.
    Report-only (no LLM Think/Act).
    """
    if memory_size < 0 or max_memory < 1:
        raise SchemaError("invalid memory bounds")
    actions: list[str] = []
    if not retrieval_hit:
        actions.append("retrieve")
    if memory_size > max_memory or noisy:
        actions.append("prune")
    if memory_size >= 3:
        actions.append("organize")
    if not actions:
        actions.append("noop")
    # filter to allowed
    actions = [a for a in actions if a in REFINE_ACTIONS]
    return {
        "actions": actions,
        "memory_size": memory_size,
        "max_memory": max_memory,
        "apply": False,
        "ok": True,
        "note": "evomemory evomem_refine_plan — ReMem refine proxy",
    }


def evolution_similarity_hint(
    *,
    query_tokens: Sequence[str],
    cluster_tokens: Sequence[str],
) -> dict[str, Any]:
    """
    Proxy for within-dataset similarity: Jaccard overlap.
    Higher → stronger expected memory reuse (Evo-Memory RQ2).
    """
    q = {str(t).lower() for t in query_tokens if t}
    c = {str(t).lower() for t in cluster_tokens if t}
    if not q or not c:
        jaccard = 0.0
    else:
        jaccard = len(q & c) / len(q | c)
    expect_gain = jaccard >= 0.25
    return {
        "jaccard": round(jaccard, 4),
        "expect_reuse_gain": expect_gain,
        "ok": True,
        "note": "evomemory evolution_similarity_hint",
    }
