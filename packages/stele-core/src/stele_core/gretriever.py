"""G-Retriever-shaped textual-graph RAG (stdlib; no GNN/LLM).

Shaped by G-Retriever (arXiv:2402.07630): node prizes, PCST-style
subgraph select, soft-prompt plan, highlight relevant parts.
Proxies only — not Prize-Collecting Steiner Tree solver or GNN.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def gretriever_node_prize(*, node_id: str, prize: float) -> dict[str, Any]:
    """Assign a retrieval prize to a textual graph node."""
    nid = node_id.strip()
    if not nid:
        raise SchemaError("node_id required")
    if prize < 0.0:
        raise SchemaError("prize must be >= 0")
    return {
        "node_id": nid[:64],
        "prize": round(prize, 4),
        "ok": True,
        "note": "gretriever gretriever_node_prize",
    }


def gretriever_pcst_select(*, nodes: int, budget: int) -> dict[str, Any]:
    """Proxy PCST subgraph selection under a node budget."""
    if nodes < 0 or budget < 1:
        raise SchemaError("nodes >= 0 and budget >= 1")
    selected = min(nodes, budget)
    return {
        "selected": selected,
        "budget": budget,
        "ok": True,
        "note": "gretriever gretriever_pcst_select",
    }


def gretriever_subgraph(*, selected: int) -> dict[str, Any]:
    """Materialize selected subgraph id."""
    if selected < 0:
        raise SchemaError("selected must be >= 0")
    sid = hashlib.sha256(
        canonical_dumps({"n": selected}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "subgraph_id": sid,
        "nodes": selected,
        "ok": True,
        "note": "gretriever gretriever_subgraph",
    }


def gretriever_soft_prompt_plan(*, subgraph_id: str) -> dict[str, Any]:
    """Soft-prompt plan over retrieved subgraph (report-only)."""
    sid = subgraph_id.strip()
    if not sid:
        raise SchemaError("subgraph_id required")
    return {
        "subgraph_id": sid[:64],
        "apply": False,
        "ok": True,
        "note": "gretriever gretriever_soft_prompt_plan",
    }


def gretriever_highlight(*, nodes: int) -> dict[str, Any]:
    """Highlight relevant graph parts for the answer."""
    if nodes < 0:
        raise SchemaError("nodes must be >= 0")
    return {
        "highlighted": nodes,
        "ok": True,
        "note": "gretriever gretriever_highlight",
    }


def gretriever_loop_plan(*, phase: str) -> dict[str, Any]:
    """Prize → PCST → subgraph → prompt."""
    order = ("prize", "pcst", "subgraph", "prompt")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "prize"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "gretriever gretriever_loop_plan",
    }
