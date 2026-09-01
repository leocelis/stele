"""PlanRAG-shaped plan-then-retrieval for Decision QA (stdlib; no LLM).

Shaped by PlanRAG (arXiv:2406.12430): make decision plan, emit analysis
queries, retrieve data, replan, decide. Proxies only — not live SQL/Cypher.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def planrag_make_plan(*, question: str) -> dict[str, Any]:
    """Generate an initial decision-making plan."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    plan_id = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": plan_id,
        "ok": True,
        "note": "planrag planrag_make_plan",
    }


def planrag_analysis_query(*, plan_id: str, query: str) -> dict[str, Any]:
    """Emit a data-analysis query from the plan."""
    pid = plan_id.strip()
    q = query.strip()
    if not pid or not q:
        raise SchemaError("plan_id and query required")
    qid = hashlib.sha256(
        canonical_dumps({"p": pid, "q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "query_id": qid,
        "ok": True,
        "note": "planrag planrag_analysis_query",
    }


def planrag_retrieve_data(*, query_id: str, rows: int) -> dict[str, Any]:
    """Retrieve analysis results for a query (proxy row count)."""
    qid = query_id.strip()
    if not qid:
        raise SchemaError("query_id required")
    if rows < 0:
        raise SchemaError("rows must be >= 0")
    return {
        "rows": rows,
        "query_id": qid[:64],
        "ok": True,
        "note": "planrag planrag_retrieve_data",
    }


def planrag_replan(*, need_replan: bool) -> dict[str, Any]:
    """Decide whether to replan (report-only)."""
    return {
        "replan": need_replan,
        "apply": False,
        "ok": True,
        "note": "planrag planrag_replan",
    }


def planrag_decide(*, ready: bool) -> dict[str, Any]:
    """Emit best decision when analysis is sufficient."""
    return {
        "decided": ready,
        "apply": False,
        "ok": True,
        "note": "planrag planrag_decide",
    }


def planrag_loop_plan(*, phase: str) -> dict[str, Any]:
    """Plan → query → retrieve → decide."""
    order = ("plan", "query", "retrieve", "decide")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "plan"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "planrag planrag_loop_plan",
    }
