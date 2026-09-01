"""IRCoT-shaped interleaved retrieval + CoT (stdlib; no LLM).

Shaped by IRCoT (arXiv:2212.10509): CoT step guides retrieval; retrieved
docs improve next CoT step until answer-ready.
Proxies only — not GPT-3 IRCoT loops.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ircot_cot_step(*, step: int, claim: str) -> dict[str, Any]:
    """Record one chain-of-thought reasoning sentence."""
    if step < 0:
        raise SchemaError("step must be >= 0")
    c = claim.strip()
    if not c:
        raise SchemaError("claim required")
    sid = hashlib.sha256(
        canonical_dumps({"s": step, "c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "step_id": sid,
        "step": step,
        "ok": True,
        "note": "ircot ircot_cot_step",
    }


def ircot_retrieve_guided(*, step_id: str, k: int = 3) -> dict[str, Any]:
    """Retrieve paragraphs guided by the latest CoT step."""
    sid = step_id.strip()
    if not sid:
        raise SchemaError("step_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "step_id": sid[:64],
        "ok": True,
        "note": "ircot ircot_retrieve_guided",
    }


def ircot_interleave(*, cot_steps: int, retrieves: int) -> dict[str, Any]:
    """Count interleaved CoT ↔ retrieve pairs."""
    if cot_steps < 0 or retrieves < 0:
        raise SchemaError("cot_steps and retrieves must be >= 0")
    return {
        "pairs": min(cot_steps, retrieves),
        "ok": True,
        "note": "ircot ircot_interleave",
    }


def ircot_answer_ready(*, enough: bool) -> dict[str, Any]:
    """Decide whether to stop and answer (report-only)."""
    return {
        "ready": enough,
        "apply": False,
        "ok": True,
        "note": "ircot ircot_answer_ready",
    }


def ircot_hallucination_check(*, grounded: float) -> dict[str, Any]:
    """Proxy factuality: fraction of CoT grounded in retrieved docs."""
    if not (0.0 <= grounded <= 1.0):
        raise SchemaError("grounded must be in [0, 1]")
    return {
        "grounded": round(grounded, 4),
        "ok": True,
        "note": "ircot ircot_hallucination_check",
    }


def ircot_loop_plan(*, phase: str) -> dict[str, Any]:
    """CoT → retrieve → interleave → answer."""
    order = ("cot", "retrieve", "interleave", "answer")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "cot"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ircot ircot_loop_plan",
    }
