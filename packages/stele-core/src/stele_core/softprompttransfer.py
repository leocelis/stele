"""SPoT proxies (stdlib; no LLM).

Shaped by SPoT (arXiv:2110.07904): Soft Prompt Transfer — train on source
tasks, initialize target soft prompts, retrieve via task embeddings.
Proxies only.

Prefix ``spot_*`` — not Soft Prompt Mixtures (``msp_*``) / Prompt Tuning.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def spot_source(*, source_task: str) -> dict[str, Any]:
    """Train / register a soft prompt on a source task."""
    t = source_task.strip()
    if not t:
        raise SchemaError("source_task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "src_id": sid,
        "ok": True,
        "note": "spot spot_source",
    }


def spot_init(*, src_id: str, target_task: str) -> dict[str, Any]:
    """Initialize target soft prompt from a transferred source prompt."""
    sid = src_id.strip()
    tgt = target_task.strip()
    if not sid or not tgt:
        raise SchemaError("src_id and target_task required")
    iid = hashlib.sha256(
        canonical_dumps({"s": sid, "t": tgt}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "ok": True,
        "note": "spot spot_init",
    }


def spot_embed(*, src_id: str) -> dict[str, Any]:
    """Interpret a learned prompt as a task embedding for retrieval."""
    sid = src_id.strip()
    if not sid:
        raise SchemaError("src_id required")
    eid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "emb_id": eid,
        "ok": True,
        "note": "spot spot_embed",
    }


def spot_retrieve(*, emb_id: str, score: int) -> dict[str, Any]:
    """Retrieve likely-positive source tasks by embedding similarity (0–100)."""
    eid = emb_id.strip()
    if not eid:
        raise SchemaError("emb_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    rid = hashlib.sha256(
        canonical_dumps({"e": eid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ret_id": rid,
        "score": score,
        "ok": True,
        "note": "spot spot_retrieve",
    }


def spot_vs_tune(*, beat_model_tuning: bool) -> dict[str, Any]:
    """Flag competitiveness vs full model tuning (report-only)."""
    return {
        "beat_model_tuning": beat_model_tuning,
        "apply": False,
        "ok": True,
        "note": "spot spot_vs_tune",
    }


def spot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Source → init → embed → retrieve."""
    order = ("source", "init", "embed", "retrieve")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "source"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "spot spot_loop_plan",
    }
