"""PageIndex-shaped vectorless TOC navigation (stdlib; no LLM).

Shaped by PageIndex (VectifyAI, 2025): hierarchical TOC/tree index,
reasoning-based section navigation, traceable paths — no vector DB /
chunking on core. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def pageindex_build_toc(*, title: str, sections: int) -> dict[str, Any]:
    """Build a document table-of-contents tree root."""
    t = title.strip()
    if not t:
        raise SchemaError("title required")
    if sections < 0:
        raise SchemaError("sections must be >= 0")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "n": sections}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "toc_id": tid,
        "sections": sections,
        "ok": True,
        "note": "pageindex pageindex_build_toc",
    }


def pageindex_add_section(
    *,
    parent_id: str,
    heading: str,
    page_start: int,
) -> dict[str, Any]:
    """Add a natural section node (no artificial chunking)."""
    pid = parent_id.strip()
    h = heading.strip()
    if not pid or not h:
        raise SchemaError("parent_id and heading required")
    if page_start < 0:
        raise SchemaError("page_start must be >= 0")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid, "h": h, "s": page_start}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "section_id": sid,
        "heading": h[:120],
        "page_start": page_start,
        "ok": True,
        "note": "pageindex pageindex_add_section",
    }


def pageindex_reason_nav(*, query: str, candidates: int) -> dict[str, Any]:
    """Reasoning-based navigation over section titles/summaries."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if candidates < 0:
        raise SchemaError("candidates must be >= 0")
    return {
        "query": q[:120],
        "candidates": candidates,
        "ok": True,
        "note": "pageindex pageindex_reason_nav",
    }


def pageindex_select_section(*, section_id: str, relevant: bool) -> dict[str, Any]:
    """Select or prune a section during tree search."""
    sid = section_id.strip()
    if not sid:
        raise SchemaError("section_id required")
    return {
        "section_id": sid[:64],
        "kept": relevant,
        "ok": True,
        "note": "pageindex pageindex_select_section",
    }


def pageindex_trace_path(*, hops: int) -> dict[str, Any]:
    """Traceable retrieval path length (explainable nav)."""
    if hops < 0:
        raise SchemaError("hops must be >= 0")
    return {
        "hops": hops,
        "traceable": hops >= 1,
        "ok": True,
        "note": "pageindex pageindex_trace_path",
    }


def pageindex_loop_plan(*, phase: str) -> dict[str, Any]:
    """TOC → section → navigate → select."""
    order = ("toc", "section", "navigate", "select")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "toc"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "pageindex pageindex_loop_plan",
    }
