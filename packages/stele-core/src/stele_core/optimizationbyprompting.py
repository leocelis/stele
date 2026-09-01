"""Optimization by PROmpting (OPRO) proxies (stdlib; no LLM).

Shaped by OPRO (arXiv:2309.03409): LLM-as-optimizer over a scored
trajectory of candidate instructions. Proxies only.

Prefix ``opro_*`` — not APE (``ape_*``) / Promptbreeder (``pbr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def opro_meta(*, task: str) -> dict[str, Any]:
    """Build meta-prompt context for the optimization task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    mid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "meta_id": mid,
        "ok": True,
        "note": "opro opro_meta",
    }


def opro_propose(*, meta_id: str) -> dict[str, Any]:
    """Propose new instruction candidates from the trajectory."""
    mid = meta_id.strip()
    if not mid:
        raise SchemaError("meta_id required")
    cid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cand_id": cid,
        "ok": True,
        "note": "opro opro_propose",
    }


def opro_score(*, cand_id: str, score: int) -> dict[str, Any]:
    """Score a candidate on the development / train set (0–100)."""
    cid = cand_id.strip()
    if not cid:
        raise SchemaError("cand_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"c": cid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "opro opro_score",
    }


def opro_append(*, score_id: str) -> dict[str, Any]:
    """Append scored candidate into the optimization trajectory."""
    sid = score_id.strip()
    if not sid:
        raise SchemaError("score_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "traj_id": tid,
        "ok": True,
        "note": "opro opro_append",
    }


def opro_best(*, beat_human: bool) -> dict[str, Any]:
    """Flag whether best OPRO prompt beats human baseline (report-only)."""
    return {
        "beat_human": beat_human,
        "apply": False,
        "ok": True,
        "note": "opro opro_best",
    }


def opro_loop_plan(*, phase: str) -> dict[str, Any]:
    """Meta → propose → score → append."""
    order = ("meta", "propose", "score", "append")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "meta"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "opro opro_loop_plan",
    }
