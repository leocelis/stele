"""MALoRA proxies (stdlib; no LLM).

Shaped by MALoRA (arXiv:2410.22782 · NAACL Findings 2025): mixture of
asymmetric LoRA experts — shared down-proj subspace, higher-rank
up-proj, fewer params / faster train than MoLoRA. Proxies only.

Prefix ``mal_*`` — not MTL-LoRA (``mtl_*``) / MoELoRA (``mel_*``) /
AsymmetryLoRA (``asy_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mal_mix(*, task: str, experts: int) -> dict[str, Any]:
    """Declare asymmetric LoRA expert mixture (experts >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if experts < 2:
        raise SchemaError("experts must be >= 2")
    mid = hashlib.sha256(
        canonical_dumps({"t": t, "e": experts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mix_id": mid,
        "experts": experts,
        "ok": True,
        "note": "mal mal_mix",
    }


def mal_down(*, mix_id: str) -> dict[str, Any]:
    """Shared tunable down-projection subspace."""
    mid = mix_id.strip()
    if not mid:
        raise SchemaError("mix_id required")
    did = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "down_id": did,
        "ok": True,
        "note": "mal mal_down",
    }


def mal_up(*, down_id: str) -> dict[str, Any]:
    """Higher-rank asymmetric up-projection per expert."""
    did = down_id.strip()
    if not did:
        raise SchemaError("down_id required")
    uid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "up_id": uid,
        "ok": True,
        "note": "mal mal_up",
    }


def mal_score(*, up_id: str, score: int) -> dict[str, Any]:
    """Score MALoRA adaptation (0–100)."""
    uid = up_id.strip()
    if not uid:
        raise SchemaError("up_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"u": uid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mal mal_score",
    }


def mal_eff(*, fewer_params: bool) -> dict[str, Any]:
    """Flag fewer params / faster train vs MoLoRA (report-only)."""
    return {
        "fewer_params": fewer_params,
        "apply": False,
        "ok": True,
        "note": "mal mal_eff",
    }


def mal_loop_plan(*, phase: str) -> dict[str, Any]:
    """Mix → down → up → score."""
    order = ("mix", "down", "up", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "mix"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mal mal_loop_plan",
    }
