"""NLoRA proxies (stdlib; no LLM).

Shaped by NLoRA (arXiv:2502.14482): Nyström landmarks initialize
LoRA cheaper than full SVD (PiSSA-style). Proxies only.

Prefix ``nlr_*`` — not S-LoRA (``slr_*``) / LISA (``lis_*``) /
PiSSA (``pis_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def nlr_landmark(*, task: str, k: int) -> dict[str, Any]:
    """Pick k Nyström landmarks (k >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    lid = hashlib.sha256(
        canonical_dumps({"t": t, "k": k}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "landmark_id": lid,
        "k": k,
        "ok": True,
        "note": "nlr nlr_landmark",
    }


def nlr_nystrom(*, landmark_id: str) -> dict[str, Any]:
    """Form Nyström sketch of W."""
    lid = landmark_id.strip()
    if not lid:
        raise SchemaError("landmark_id required")
    nid = hashlib.sha256(
        canonical_dumps({"l": lid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "nystrom_id": nid,
        "ok": True,
        "note": "nlr nlr_nystrom",
    }


def nlr_init(*, nystrom_id: str, rank: int) -> dict[str, Any]:
    """Init LoRA from the Nyström sketch (rank >= 1)."""
    nid = nystrom_id.strip()
    if not nid:
        raise SchemaError("nystrom_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    iid = hashlib.sha256(
        canonical_dumps({"n": nid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "rank": rank,
        "ok": True,
        "note": "nlr nlr_init",
    }


def nlr_score(*, init_id: str, score: int) -> dict[str, Any]:
    """Score NLoRA run (0–100)."""
    iid = init_id.strip()
    if not iid:
        raise SchemaError("init_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"i": iid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "nlr nlr_score",
    }


def nlr_cheap(*, cheaper_svd: bool) -> dict[str, Any]:
    """Flag cheaper init vs full SVD (report-only)."""
    return {
        "cheaper_svd": cheaper_svd,
        "apply": False,
        "ok": True,
        "note": "nlr nlr_cheap",
    }


def nlr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Landmark → nystrom → init → score."""
    order = ("landmark", "nystrom", "init", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "landmark"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "nlr nlr_loop_plan",
    }
