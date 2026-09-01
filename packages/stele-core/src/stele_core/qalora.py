"""QA-LoRA proxies (stdlib; no LLM).

Shaped by QA-LoRA (arXiv:2309.14717): group-wise quantization + shared
LoRA per group so INT4 weights merge without a PTQ step. Proxies only.

Prefix ``qal_*`` — not QLoRA (``qlo_*``) / LoftQ (``lfq_*``) / Tied-LoRA
(``tld_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def qal_group(*, task: str, groups: int) -> dict[str, Any]:
    """Partition columns into groups (groups >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if groups < 1:
        raise SchemaError("groups must be >= 1")
    gid = hashlib.sha256(
        canonical_dumps({"t": t, "g": groups}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "group_id": gid,
        "groups": groups,
        "ok": True,
        "note": "qal qal_group",
    }


def qal_quant(*, group_id: str, bits: int) -> dict[str, Any]:
    """Quantize each group (bits >= 2)."""
    gid = group_id.strip()
    if not gid:
        raise SchemaError("group_id required")
    if bits < 2:
        raise SchemaError("bits must be >= 2")
    qid = hashlib.sha256(
        canonical_dumps({"g": gid, "b": bits}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "quant_id": qid,
        "bits": bits,
        "ok": True,
        "note": "qal qal_quant",
    }


def qal_adapt(*, quant_id: str) -> dict[str, Any]:
    """Share LoRA adapters within each group."""
    qid = quant_id.strip()
    if not qid:
        raise SchemaError("quant_id required")
    aid = hashlib.sha256(
        canonical_dumps({"q": qid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapt_id": aid,
        "ok": True,
        "note": "qal qal_adapt",
    }


def qal_score(*, adapt_id: str, score: int) -> dict[str, Any]:
    """Score QA-LoRA run (0–100)."""
    aid = adapt_id.strip()
    if not aid:
        raise SchemaError("adapt_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "qal qal_score",
    }


def qal_merge(*, merge_int4: bool) -> dict[str, Any]:
    """Flag INT4 merge without PTQ (report-only)."""
    return {
        "merge_int4": merge_int4,
        "apply": False,
        "ok": True,
        "note": "qal qal_merge",
    }


def qal_loop_plan(*, phase: str) -> dict[str, Any]:
    """Group → quant → adapt → score."""
    order = ("group", "quant", "adapt", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "group"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "qal qal_loop_plan",
    }
