"""SuperLoRA proxies (stdlib; no LLM).

Shaped by SuperLoRA (arXiv:2403.11887): unified LoRA family — grouping,
folding, shuffling, projection, tensor factoring (covers LoHA/LoKr).
Proxies only.

Prefix ``spr_*`` — not S-LoRA (``slr_*``) / MixLoRA (``mxl_*``) / LoHA
(``lha_*``) / LoKr (``lkr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def spr_group(*, task: str, groups: int) -> dict[str, Any]:
    """Split ΔW into groups (groups >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if groups < 1:
        raise SchemaError("groups must be >= 1")
    gid = hashlib.sha256(
        canonical_dumps({"t": t, "g": groups}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "group_id": gid,
        "groups": groups,
        "ok": True,
        "note": "spr spr_group",
    }


def spr_fold(*, group_id: str) -> dict[str, Any]:
    """Apply folding / reshape of grouped ΔW."""
    gid = group_id.strip()
    if not gid:
        raise SchemaError("group_id required")
    fid = hashlib.sha256(
        canonical_dumps({"g": gid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fold_id": fid,
        "ok": True,
        "note": "spr spr_fold",
    }


def spr_factor(*, fold_id: str) -> dict[str, Any]:
    """Tensor / Kronecker factor the folded update."""
    fid = fold_id.strip()
    if not fid:
        raise SchemaError("fold_id required")
    kid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "factor_id": kid,
        "ok": True,
        "note": "spr spr_factor",
    }


def spr_score(*, factor_id: str, score: int) -> dict[str, Any]:
    """Score SuperLoRA run (0–100)."""
    fid = factor_id.strip()
    if not fid:
        raise SchemaError("factor_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"f": fid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "spr spr_score",
    }


def spr_unify(*, unifies_loha_lokr: bool) -> dict[str, Any]:
    """Flag LoHA/LoKr unification (report-only)."""
    return {
        "unifies_loha_lokr": unifies_loha_lokr,
        "apply": False,
        "ok": True,
        "note": "spr spr_unify",
    }


def spr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Group → fold → factor → score."""
    order = ("group", "fold", "factor", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "group"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "spr spr_loop_plan",
    }
