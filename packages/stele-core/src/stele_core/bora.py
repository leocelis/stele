"""BoRA proxies (stdlib; no LLM).

Shaped by BoRA (arXiv:2412.06441): bi-dimensional DoRA-style
magnitude on rows and columns. Proxies only.

Prefix ``bor_*`` — not DoRA (``dora_*``) / Uni-LoRA (``ulo_*``) / LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def bor_row(*, task: str) -> dict[str, Any]:
    """Allocate row-wise magnitude factors."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    rid = hashlib.sha256(
        canonical_dumps({"t": t, "a": "row"}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "row_id": rid,
        "ok": True,
        "note": "bor bor_row",
    }


def bor_col(*, row_id: str) -> dict[str, Any]:
    """Allocate column-wise magnitude factors."""
    rid = row_id.strip()
    if not rid:
        raise SchemaError("row_id required")
    cid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "col_id": cid,
        "ok": True,
        "note": "bor bor_col",
    }


def bor_train(*, col_id: str) -> dict[str, Any]:
    """Train LoRA direction plus both magnitude axes."""
    cid = col_id.strip()
    if not cid:
        raise SchemaError("col_id required")
    tid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "bor bor_train",
    }


def bor_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score BoRA run (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "bor bor_score",
    }


def bor_sym(*, symmetric: bool) -> dict[str, Any]:
    """Flag row/column magnitude symmetry (report-only)."""
    return {
        "symmetric": symmetric,
        "apply": False,
        "ok": True,
        "note": "bor bor_sym",
    }


def bor_loop_plan(*, phase: str) -> dict[str, Any]:
    """Row → col → train → score."""
    order = ("row", "col", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "row"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "bor bor_loop_plan",
    }
