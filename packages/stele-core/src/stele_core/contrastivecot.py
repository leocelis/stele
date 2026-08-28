"""Contrastive Chain-of-Thought proxies (stdlib; no LLM).

Shaped by Contrastive CoT (arXiv:2311.09277): valid + invalid
demonstrations guide step-by-step reasoning. Proxies only.

Prefix ``ccot_*`` — not plain CoT / Auto-CoT / Faithful-CoT.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ccot_valid(*, demo: str) -> dict[str, Any]:
    """Register a valid reasoning demonstration."""
    d = demo.strip()
    if not d:
        raise SchemaError("demo required")
    vid = hashlib.sha256(
        canonical_dumps({"d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "valid_id": vid,
        "ok": True,
        "note": "ccot ccot_valid",
    }


def ccot_invalid(*, demo: str) -> dict[str, Any]:
    """Register an invalid reasoning demonstration (mistakes to avoid)."""
    d = demo.strip()
    if not d:
        raise SchemaError("demo required")
    iid = hashlib.sha256(
        canonical_dumps({"d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "invalid_id": iid,
        "ok": True,
        "note": "ccot ccot_invalid",
    }


def ccot_contrast(*, valid_id: str, invalid_id: str) -> dict[str, Any]:
    """Contrast valid vs invalid demonstrations."""
    vid = valid_id.strip()
    iid = invalid_id.strip()
    if not vid or not iid:
        raise SchemaError("valid_id and invalid_id required")
    cid = hashlib.sha256(
        canonical_dumps({"v": vid, "i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "contrast_id": cid,
        "ok": True,
        "note": "ccot ccot_contrast",
    }


def ccot_reason(*, contrast_id: str) -> dict[str, Any]:
    """Step-by-step reason guided by the contrast pair."""
    cid = contrast_id.strip()
    if not cid:
        raise SchemaError("contrast_id required")
    rid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reason_id": rid,
        "ok": True,
        "note": "ccot ccot_reason",
    }


def ccot_auto(*, construct: bool) -> dict[str, Any]:
    """Flag automatic contrastive demo construction (report-only)."""
    return {
        "construct": construct,
        "apply": False,
        "ok": True,
        "note": "ccot ccot_auto",
    }


def ccot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Valid → invalid → contrast → reason."""
    order = ("valid", "invalid", "contrast", "reason")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "valid"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ccot ccot_loop_plan",
    }
