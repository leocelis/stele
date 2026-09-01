"""REPLUG-shaped black-box retrieve-and-plug (stdlib; no LLM).

Shaped by REPLUG (arXiv:2301.12652): retrieve docs, prepend to frozen
LM input, ensemble parallel forwards, LM-supervise retriever.
Proxies only — not live GPT-3 / tuned Contriever.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def replug_retrieve_docs(*, query: str, k: int = 5) -> dict[str, Any]:
    """Retrieve k docs for black-box LM augmentation."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "ok": True,
        "note": "replug replug_retrieve_docs",
    }


def replug_prepend_doc(*, doc_id: str, context: str) -> dict[str, Any]:
    """Prepend one retrieved doc to the frozen LM input."""
    d = doc_id.strip()
    c = context.strip()
    if not d or not c:
        raise SchemaError("doc_id and context required")
    pack_id = hashlib.sha256(
        canonical_dumps({"d": d, "c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pack_id": pack_id,
        "ok": True,
        "note": "replug replug_prepend_doc",
    }


def replug_ensemble_probs(*, packs: int) -> dict[str, Any]:
    """Ensemble probabilities across parallel doc+context packs."""
    if packs < 1:
        raise SchemaError("packs must be >= 1")
    return {
        "packs": packs,
        "ensembled": True,
        "ok": True,
        "note": "replug replug_ensemble_probs",
    }


def replug_supervise_retriever(*, lm_gain: float) -> dict[str, Any]:
    """Use LM likelihood gain to supervise retriever (report-only)."""
    if not (0.0 <= lm_gain <= 1.0):
        raise SchemaError("lm_gain must be in [0, 1]")
    return {
        "lm_gain": round(lm_gain, 4),
        "apply": False,
        "ok": True,
        "note": "replug replug_supervise_retriever",
    }


def replug_blackbox_forward(*, pack_id: str) -> dict[str, Any]:
    """Forward one pack through frozen black-box LM (proxy)."""
    pid = pack_id.strip()
    if not pid:
        raise SchemaError("pack_id required")
    return {
        "pack_id": pid[:64],
        "forwarded": True,
        "ok": True,
        "note": "replug replug_blackbox_forward",
    }


def replug_loop_plan(*, phase: str) -> dict[str, Any]:
    """Retrieve → prepend → forward → ensemble."""
    order = ("retrieve", "prepend", "forward", "ensemble")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "retrieve"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "replug replug_loop_plan",
    }
