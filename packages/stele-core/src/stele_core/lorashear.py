"""LoRAShear proxies (stdlib; no LLM).

Shaped by LoRAShear (arXiv:2310.18356): structured prune via LoRA
dependency graphs + LHSPG knowledge transfer, then dynamic recovery
fine-tuning. Proxies only.

Prefix ``lsh_*`` — not LoRA-SP (``lsp_*``) / DropLoRA (``drl_*``) /
alternating OPLoRA (``aop_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lsh_graph(*, task: str) -> dict[str, Any]:
    """Build LoRA dependency graph for minimally removable structures."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    gid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "graph_id": gid,
        "ok": True,
        "note": "lsh lsh_graph",
    }


def lsh_prune(*, graph_id: str, ratio_pct: int) -> dict[str, Any]:
    """Progressive structured prune via LHSPG (1–50% footprint cut)."""
    gid = graph_id.strip()
    if not gid:
        raise SchemaError("graph_id required")
    if ratio_pct < 1 or ratio_pct > 50:
        raise SchemaError("ratio_pct must be 1..50")
    pid = hashlib.sha256(
        canonical_dumps({"g": gid, "r": ratio_pct}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prune_id": pid,
        "ratio_pct": ratio_pct,
        "ok": True,
        "note": "lsh lsh_prune",
    }


def lsh_recover(*, prune_id: str) -> dict[str, Any]:
    """Dynamic knowledge-recovery fine-tuning after prune."""
    pid = prune_id.strip()
    if not pid:
        raise SchemaError("prune_id required")
    rid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "recover_id": rid,
        "ok": True,
        "note": "lsh lsh_recover",
    }


def lsh_score(*, recover_id: str, score: int) -> dict[str, Any]:
    """Score LoRAShear prune+recover (0–100)."""
    rid = recover_id.strip()
    if not rid:
        raise SchemaError("recover_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"r": rid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lsh lsh_score",
    }


def lsh_footprint(*, reduced: bool) -> dict[str, Any]:
    """Flag footprint reduction with small quality drop (report-only)."""
    return {
        "reduced": reduced,
        "apply": False,
        "ok": True,
        "note": "lsh lsh_footprint",
    }


def lsh_loop_plan(*, phase: str) -> dict[str, Any]:
    """Graph → prune → recover → score."""
    order = ("graph", "prune", "recover", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "graph"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lsh lsh_loop_plan",
    }
