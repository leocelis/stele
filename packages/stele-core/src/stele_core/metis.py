"""Metis-shaped dual text/code memory (stdlib; no LLM / no compiler).

Shaped by Metis (arXiv:2606.24151): hierarchical text (plans/facts/pitfalls)
+ selective crystallization of recurring plans into code tools.
Proxies only — not Metis paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

TEXT_KINDS = frozenset({"plan", "fact", "pitfall"})


def text_experience_store(
    *,
    kind: str,
    content: str,
) -> dict[str, Any]:
    """Store differentiated text experience: plan | fact | pitfall."""
    if kind not in TEXT_KINDS:
        raise SchemaError(f"kind must be one of {sorted(TEXT_KINDS)}")
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    eid = hashlib.sha256(
        canonical_dumps({"k": kind, "c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "entry_id": eid,
        "kind": kind,
        "content": body[:200],
        "ok": True,
        "note": "metis text_experience_store",
    }


def crystallize_plan_to_tool(
    *,
    plan_id: str,
    reuse_count: int,
    min_reuse: int = 3,
) -> dict[str, Any]:
    """Promote recurring plans into callable tools when reuse ≥ threshold."""
    pid = plan_id.strip()
    if not pid:
        raise SchemaError("plan_id required")
    if reuse_count < 0 or min_reuse < 1:
        raise SchemaError("reuse_count >= 0 and min_reuse >= 1")
    promote = reuse_count >= min_reuse
    tool_id = None
    if promote:
        tool_id = hashlib.sha256(
            canonical_dumps({"p": pid}).encode("utf-8")
        ).hexdigest()[:12]
    return {
        "promote": promote,
        "tool_id": tool_id,
        "reuse_count": reuse_count,
        "apply": False,
        "ok": True,
        "note": "metis crystallize_plan_to_tool",
    }


def dual_retrieve(
    *,
    text_hits: Sequence[str],
    code_tool_ids: Sequence[str],
) -> dict[str, Any]:
    """Retrieve from both text store and code tool library."""
    if not isinstance(text_hits, Sequence) or isinstance(text_hits, (str, bytes)):
        raise SchemaError("text_hits sequence required")
    if not isinstance(code_tool_ids, Sequence) or isinstance(
        code_tool_ids, (str, bytes)
    ):
        raise SchemaError("code_tool_ids sequence required")
    texts = [str(t).strip() for t in text_hits if str(t).strip()][:10]
    codes = [str(c).strip() for c in code_tool_ids if str(c).strip()][:10]
    return {
        "text": texts,
        "code": codes,
        "dual": bool(texts) and bool(codes),
        "ok": True,
        "note": "metis dual_retrieve",
    }


def representation_tradeoff(
    *,
    construction_cost: float,
    execution_efficiency: float,
    transferability: float,
) -> dict[str, Any]:
    """Score text vs code trade-offs (higher better for each axis 0–1)."""
    for name, val in (
        ("construction_cost", construction_cost),
        ("execution_efficiency", execution_efficiency),
        ("transferability", transferability),
    ):
        if not (0.0 <= val <= 1.0):
            raise SchemaError(f"{name} must be in [0, 1]")
    # Prefer low construction cost (invert), high efficiency, high transfer
    score = round(
        (1.0 - construction_cost) * 0.3
        + execution_efficiency * 0.4
        + transferability * 0.3,
        4,
    )
    return {
        "score": score,
        "ok": True,
        "note": "metis representation_tradeoff",
    }


def promote_kind_gate(
    *,
    kind: str,
) -> dict[str, Any]:
    """Only plans crystallize to code; facts/pitfalls stay text."""
    if kind not in TEXT_KINDS:
        raise SchemaError(f"kind must be one of {sorted(TEXT_KINDS)}")
    return {
        "allow_crystallize": kind == "plan",
        "kind": kind,
        "apply": False,
        "ok": True,
        "note": "metis promote_kind_gate",
    }


def metis_loop_plan(
    *,
    phase: str,
) -> dict[str, Any]:
    """Self-evolve loop: reflect → crystallize → retrieve → act."""
    order = ("reflect", "crystallize", "retrieve", "act")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "reflect"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "metis metis_loop_plan",
    }
