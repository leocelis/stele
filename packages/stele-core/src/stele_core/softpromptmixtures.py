"""Soft Prompt Mixtures proxies (stdlib; no LLM).

Shaped by Qin & Eisner (arXiv:2104.06599): learn soft-word prompts by
gradient descent and ensemble mixtures for cloze knowledge queries.
Proxies only.

Prefix ``msp_*`` — not Prompt Tuning (``ptl_*``) / SPoT (``spot_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def msp_soft(*, query: str) -> dict[str, Any]:
    """Allocate soft-word continuous vectors for a cloze query."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    sid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "soft_id": sid,
        "ok": True,
        "note": "msp msp_soft",
    }


def msp_mix(*, soft_id: str) -> dict[str, Any]:
    """Form a mixture of soft prompts for the same task."""
    sid = soft_id.strip()
    if not sid:
        raise SchemaError("soft_id required")
    mid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mix_id": mid,
        "ok": True,
        "note": "msp msp_mix",
    }


def msp_ensemble(*, mix_id: str) -> dict[str, Any]:
    """Ensemble mixture members into a query distribution."""
    mid = mix_id.strip()
    if not mid:
        raise SchemaError("mix_id required")
    eid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ens_id": eid,
        "ok": True,
        "note": "msp msp_ensemble",
    }


def msp_probe(*, ens_id: str, score: int) -> dict[str, Any]:
    """Score cloze factual probe quality (0–100)."""
    eid = ens_id.strip()
    if not eid:
        raise SchemaError("ens_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    pid = hashlib.sha256(
        canonical_dumps({"e": eid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "probe_id": pid,
        "score": score,
        "ok": True,
        "note": "msp msp_probe",
    }


def msp_underest(*, prior_underestimate: bool) -> dict[str, Any]:
    """Flag that prior probes underestimated LM knowledge (report-only)."""
    return {
        "prior_underestimate": prior_underestimate,
        "apply": False,
        "ok": True,
        "note": "msp msp_underest",
    }


def msp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Soft → mix → ensemble → probe."""
    order = ("soft", "mix", "ensemble", "probe")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "soft"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "msp msp_loop_plan",
    }
