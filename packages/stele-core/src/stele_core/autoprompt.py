"""AutoPrompt proxies (stdlib; no LLM).

Shaped by AutoPrompt (arXiv:2010.15980): gradient-guided search for
discrete trigger tokens that maximize label likelihood. Proxies only.

Prefix ``aup_*`` — not Active-Prompt (``ap_*``) / Prefix-Tuning (``pfx_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def aup_template(*, template: str) -> dict[str, Any]:
    """Register a cloze / fill-in-the-blank prompt template with [T] slots."""
    t = template.strip()
    if not t:
        raise SchemaError("template required")
    tid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tmpl_id": tid,
        "ok": True,
        "note": "aup aup_template",
    }


def aup_trigger(*, tmpl_id: str) -> dict[str, Any]:
    """Initialize shared trigger tokens (often [MASK] seeds)."""
    tid = tmpl_id.strip()
    if not tid:
        raise SchemaError("tmpl_id required")
    xid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "trig_id": xid,
        "ok": True,
        "note": "aup aup_trigger",
    }


def aup_search(*, trig_id: str) -> dict[str, Any]:
    """Gradient-guided discrete token swap search over triggers."""
    tid = trig_id.strip()
    if not tid:
        raise SchemaError("trig_id required")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "search_id": sid,
        "ok": True,
        "note": "aup aup_search",
    }


def aup_score(*, search_id: str, score: int) -> dict[str, Any]:
    """Label-likelihood score for the current trigger set (0–100)."""
    sid = search_id.strip()
    if not sid:
        raise SchemaError("search_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    xid = hashlib.sha256(
        canonical_dumps({"s": sid, "v": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": xid,
        "score": score,
        "ok": True,
        "note": "aup aup_score",
    }


def aup_probe(*, parameter_free: bool) -> dict[str, Any]:
    """Flag parameter-free probing alternative to finetuning (report-only)."""
    return {
        "parameter_free": parameter_free,
        "apply": False,
        "ok": True,
        "note": "aup aup_probe",
    }


def aup_loop_plan(*, phase: str) -> dict[str, Any]:
    """Template → trigger → search → score."""
    order = ("template", "trigger", "search", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "template"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "aup aup_loop_plan",
    }
