"""LoRA-Composer proxies (stdlib; no LLM).

Shaped by LoRA-Composer (arXiv:2403.11627): training-free multi-concept
LoRA composition — concept injection (anti-vanishing), concept isolation
(anti-confusion), and latent re-initialization. Proxies only.

Prefix ``lco_*`` — not COLA/Chain-of-LoRA (``col_*``) / Compress-then-Serve
(``cts_*``) / CARE-LoRA (``car_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lco_concepts(*, task: str, n_loras: int) -> dict[str, Any]:
    """Register multi-concept LoRA set (n_loras >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_loras < 2:
        raise SchemaError("n_loras must be >= 2")
    cid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_loras}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "concepts_id": cid,
        "n_loras": n_loras,
        "ok": True,
        "note": "lco lco_concepts",
    }


def lco_inject(*, concepts_id: str) -> dict[str, Any]:
    """Apply concept injection constraints (anti-vanishing)."""
    cid = concepts_id.strip()
    if not cid:
        raise SchemaError("concepts_id required")
    iid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "inject_id": iid,
        "ok": True,
        "note": "lco lco_inject",
    }


def lco_isolate(*, inject_id: str) -> dict[str, Any]:
    """Apply concept isolation constraints (anti-confusion)."""
    iid = inject_id.strip()
    if not iid:
        raise SchemaError("inject_id required")
    oid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "isolate_id": oid,
        "ok": True,
        "note": "lco lco_isolate",
    }


def lco_score(*, isolate_id: str, score: int) -> dict[str, Any]:
    """Score multi-concept composition (0–100)."""
    oid = isolate_id.strip()
    if not oid:
        raise SchemaError("isolate_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"o": oid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lco lco_score",
    }


def lco_free(*, training_free: bool) -> dict[str, Any]:
    """Flag training-free composition (report-only)."""
    return {
        "training_free": training_free,
        "apply": False,
        "ok": True,
        "note": "lco lco_free",
    }


def lco_loop_plan(*, phase: str) -> dict[str, Any]:
    """Concepts → inject → isolate → score."""
    order = ("concepts", "inject", "isolate", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "concepts"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lco lco_loop_plan",
    }
