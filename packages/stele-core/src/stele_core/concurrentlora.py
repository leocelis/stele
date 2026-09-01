"""PLoRA concurrent-training proxies (stdlib; no LLM).

Shaped by PLoRA (arXiv:2508.02932): fuse many LoRA adapters into one
packed forward so concurrent fine-tunes share GPU work instead of
serializing per adapter. Proxies only.

Prefix ``cnl_*`` — not PeriodicLoRA (``plr_*``) / Punica (``pun_*``)
/ MixLoRA (``mxl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cnl_pack(*, task: str, adapters: int) -> dict[str, Any]:
    """Pack N concurrent LoRA adapters (adapters >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if adapters < 1:
        raise SchemaError("adapters must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "n": adapters}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pack_id": pid,
        "adapters": adapters,
        "ok": True,
        "note": "cnl cnl_pack",
    }


def cnl_fuse(*, pack_id: str) -> dict[str, Any]:
    """Fuse packed adapters into one batched forward."""
    pid = pack_id.strip()
    if not pid:
        raise SchemaError("pack_id required")
    fid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fuse_id": fid,
        "ok": True,
        "note": "cnl cnl_fuse",
    }


def cnl_train(*, fuse_id: str) -> dict[str, Any]:
    """Run the concurrent packed train step."""
    fid = fuse_id.strip()
    if not fid:
        raise SchemaError("fuse_id required")
    tid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "cnl cnl_train",
    }


def cnl_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score concurrent PLoRA run (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "cnl cnl_score",
    }


def cnl_hw(*, better_util: bool) -> dict[str, Any]:
    """Flag better GPU util vs serial LoRAs (report-only)."""
    return {
        "better_util": better_util,
        "apply": False,
        "ok": True,
        "note": "cnl cnl_hw",
    }


def cnl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Pack → fuse → train → score."""
    order = ("pack", "fuse", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "pack"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cnl cnl_loop_plan",
    }
