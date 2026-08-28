"""Active-Prompt-shaped uncertainty annotation selection (stdlib; no LLM).

Shaped by Active-Prompt (arXiv:2302.12246): sample answers, score
uncertainty, select questions to annotate, build CoT exemplars.
Proxies only — ≠ Auto-CoT.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ap_sample(*, question: str, k: int) -> dict[str, Any]:
    """Sample k answers for uncertainty estimation."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"q": q, "k": k}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sample_id": sid,
        "k": k,
        "ok": True,
        "note": "activeprompt ap_sample",
    }


def ap_uncertainty(*, sample_id: str, score: float) -> dict[str, Any]:
    """Score uncertainty (disagreement/entropy proxy in [0,1])."""
    sid = sample_id.strip()
    if not sid:
        raise SchemaError("sample_id required")
    if score < 0.0 or score > 1.0:
        raise SchemaError("score must be in [0, 1]")
    uid = hashlib.sha256(
        canonical_dumps({"s": sid, "u": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "uncertainty_id": uid,
        "score": score,
        "ok": True,
        "note": "activeprompt ap_uncertainty",
    }


def ap_select(*, top_n: int) -> dict[str, Any]:
    """Select top-n most uncertain questions for annotation."""
    if top_n < 1:
        raise SchemaError("top_n must be >= 1")
    return {
        "top_n": top_n,
        "ok": True,
        "note": "activeprompt ap_select",
    }


def ap_annotate(*, question_id: str, cot: str) -> dict[str, Any]:
    """Human-shaped CoT annotation for a selected question."""
    qid = question_id.strip()
    c = cot.strip()
    if not qid or not c:
        raise SchemaError("question_id and cot required")
    aid = hashlib.sha256(
        canonical_dumps({"q": qid, "c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "exemplar_id": aid,
        "ok": True,
        "note": "activeprompt ap_annotate",
    }


def ap_pool(*, size: int) -> dict[str, Any]:
    """Size of the unlabeled question pool."""
    if size < 0:
        raise SchemaError("size must be >= 0")
    return {
        "size": size,
        "ok": True,
        "note": "activeprompt ap_pool",
    }


def ap_loop_plan(*, phase: str) -> dict[str, Any]:
    """Sample → uncertainty → select → annotate."""
    order = ("sample", "uncertainty", "select", "annotate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "sample"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "activeprompt ap_loop_plan",
    }
