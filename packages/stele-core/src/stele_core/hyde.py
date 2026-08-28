"""HyDE-shaped hypothetical document retrieval (stdlib; no LLM).

Shaped by HyDE (arXiv:2212.10496): generate hypothetical doc from query,
encode proxy, retrieve by hyp embedding neighborhood, filter
hallucinations via dense bottleneck, ground to corpus.
Proxies only — not InstructGPT / Contriever.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hyde_hypothetical_doc(*, query: str) -> dict[str, Any]:
    """Register a hypothetical document derived from the query."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    hyp_id = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hyp_id": hyp_id,
        "ok": True,
        "note": "hyde hyde_hypothetical_doc",
    }


def hyde_encode_proxy(*, hyp_id: str) -> dict[str, Any]:
    """Proxy encode hyp doc into a dense vector id (hash)."""
    hid = hyp_id.strip()
    if not hid:
        raise SchemaError("hyp_id required")
    vec_id = hashlib.sha256(
        canonical_dumps({"h": hid}).encode("utf-8")
    ).hexdigest()[:16]
    return {
        "vec_id": vec_id,
        "ok": True,
        "note": "hyde hyde_encode_proxy",
    }


def hyde_retrieve_by_hyp(*, vec_id: str, k: int = 5) -> dict[str, Any]:
    """Retrieve k neighbors by hypothetical embedding."""
    vid = vec_id.strip()
    if not vid:
        raise SchemaError("vec_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "vec_id": vid[:16],
        "ok": True,
        "note": "hyde hyde_retrieve_by_hyp",
    }


def hyde_filter_hallucination(*, retained: float) -> dict[str, Any]:
    """Dense-bottleneck filter: fraction of hyp details retained as grounded."""
    if not (0.0 <= retained <= 1.0):
        raise SchemaError("retained must be in [0, 1]")
    return {
        "retained": round(retained, 4),
        "filtered": retained < 1.0,
        "ok": True,
        "note": "hyde hyde_filter_hallucination",
    }


def hyde_ground_corpus(*, hits: int, grounded: int) -> dict[str, Any]:
    """Ground hyp neighborhood to real corpus hits."""
    if hits < 0 or grounded < 0:
        raise SchemaError("hits and grounded must be >= 0")
    if grounded > hits:
        raise SchemaError("grounded must be <= hits")
    return {
        "grounded": grounded,
        "hits": hits,
        "ok": True,
        "note": "hyde hyde_ground_corpus",
    }


def hyde_loop_plan(*, phase: str) -> dict[str, Any]:
    """Hyp → encode → retrieve → ground."""
    order = ("hyp", "encode", "retrieve", "ground")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "hyp"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hyde hyde_loop_plan",
    }
