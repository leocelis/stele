"""STaR-shaped self-taught rationale bootstrap (stdlib; no LLM / no train).

Shaped by STaR (arXiv:2203.14465): generate rationale, filter correct,
rationalize failures, fine-tune proxy. Proxies only — ≠ Quiet-STaR.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def star_generate(*, question: str) -> dict[str, Any]:
    """Generate a rationale+answer attempt."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    gid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "gen_id": gid,
        "ok": True,
        "note": "star star_generate",
    }


def star_filter_correct(*, gen_id: str, correct: bool) -> dict[str, Any]:
    """Keep only rationales that yielded correct answers."""
    gid = gen_id.strip()
    if not gid:
        raise SchemaError("gen_id required")
    return {
        "gen_id": gid[:64],
        "keep": correct,
        "apply": False,
        "ok": True,
        "note": "star star_filter_correct",
    }


def star_rationalize(*, question: str, answer: str) -> dict[str, Any]:
    """Rationalize: generate rationale given the correct answer."""
    q = question.strip()
    a = answer.strip()
    if not q or not a:
        raise SchemaError("question and answer required")
    rid = hashlib.sha256(
        canonical_dumps({"q": q, "a": a}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "rationale_id": rid,
        "ok": True,
        "note": "star star_rationalize",
    }


def star_finetune_proxy(*, examples: int) -> dict[str, Any]:
    """Fine-tune proxy on retained rationales (report-only)."""
    if examples < 0:
        raise SchemaError("examples must be >= 0")
    return {
        "examples": examples,
        "apply": False,
        "ok": True,
        "note": "star star_finetune_proxy",
    }


def star_bootstrap_round(*, round_n: int) -> dict[str, Any]:
    """Count bootstrap loop round."""
    if round_n < 0:
        raise SchemaError("round_n must be >= 0")
    return {
        "round": round_n,
        "ok": True,
        "note": "star star_bootstrap_round",
    }


def star_loop_plan(*, phase: str) -> dict[str, Any]:
    """Generate → filter → rationalize → finetune."""
    order = ("generate", "filter", "rationalize", "finetune")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "generate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "star star_loop_plan",
    }
