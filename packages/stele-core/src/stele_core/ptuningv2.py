"""P-Tuning v2 proxies (stdlib; no LLM).

Shaped by P-Tuning v2 (arXiv:2110.07602): deep continuous prompts at
every transformer layer for NLU, matching finetuning with 0.1%–3%
params. Proxies only.

Prefix ``ptv_*`` — not Prefix-Tuning (``pfx_*``) / Prompt Tuning (``ptl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ptv_deep(*, task: str) -> dict[str, Any]:
    """Allocate deep continuous prompts across transformer layers."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    did = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "deep_id": did,
        "ok": True,
        "note": "ptv ptv_deep",
    }


def ptv_inject(*, deep_id: str) -> dict[str, Any]:
    """Inject layer-wise prefix embeddings (LM frozen)."""
    did = deep_id.strip()
    if not did:
        raise SchemaError("deep_id required")
    iid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "inj_id": iid,
        "ok": True,
        "note": "ptv ptv_inject",
    }


def ptv_tune(*, inj_id: str) -> dict[str, Any]:
    """Optimize deep prompts only (no verbalizer required)."""
    iid = inj_id.strip()
    if not iid:
        raise SchemaError("inj_id required")
    tid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tune_id": tid,
        "ok": True,
        "note": "ptv ptv_tune",
    }


def ptv_seqtag(*, tune_id: str, score: int) -> dict[str, Any]:
    """Evaluate on hard sequence tagging / NLU (score 0–100)."""
    tid = tune_id.strip()
    if not tid:
        raise SchemaError("tune_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tag_id": sid,
        "score": score,
        "ok": True,
        "note": "ptv ptv_seqtag",
    }


def ptv_universal(*, match_finetune: bool) -> dict[str, Any]:
    """Flag universality vs finetuning across scales (report-only)."""
    return {
        "match_finetune": match_finetune,
        "apply": False,
        "ok": True,
        "note": "ptv ptv_universal",
    }


def ptv_loop_plan(*, phase: str) -> dict[str, Any]:
    """Deep → inject → tune → seqtag."""
    order = ("deep", "inject", "tune", "seqtag")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "deep"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ptv ptv_loop_plan",
    }
