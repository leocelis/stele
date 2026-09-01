"""MemGPT-shaped virtual context paging (stdlib; no LLM).

Shaped by MemGPT (arXiv:2310.08560) / Letta: main context as RAM, recall +
archival as disk, page-in/out via tools, capacity flush warning. Proxies
only — not MemGPT paper scores. Distinct from MemoryOS segmented paging.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def memgpt_main_capacity(
    *,
    used_tokens: int,
    max_tokens: int,
    warn_ratio: float = 0.7,
) -> dict[str, Any]:
    """Capacity gate: warn at warn_ratio, flush at full."""
    if used_tokens < 0 or max_tokens < 1:
        raise SchemaError("used_tokens >= 0 and max_tokens >= 1")
    if not (0.0 < warn_ratio < 1.0):
        raise SchemaError("warn_ratio must be in (0, 1)")
    ratio = used_tokens / max_tokens
    warn = ratio >= warn_ratio
    flush = used_tokens >= max_tokens
    return {
        "ratio": round(ratio, 4),
        "warn": warn,
        "flush": flush,
        "ok": True,
        "note": "memgpt memgpt_main_capacity",
    }


def memgpt_page_out(*, content: str, tier: str) -> dict[str, Any]:
    """Evict content from main context into recall or archival."""
    if tier not in ("recall", "archival"):
        raise SchemaError("tier must be recall or archival")
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    pid = hashlib.sha256(
        canonical_dumps({"t": tier, "c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "page_id": pid,
        "tier": tier,
        "ok": True,
        "note": "memgpt memgpt_page_out",
    }


def memgpt_page_in(*, page_id: str, fits: bool) -> dict[str, Any]:
    """Page fault: load external page into main when it fits."""
    pid = page_id.strip()
    if not pid:
        raise SchemaError("page_id required")
    return {
        "page_id": pid[:64],
        "loaded": fits,
        "ok": True,
        "note": "memgpt memgpt_page_in",
    }


def memgpt_recall_search(*, query: str, hits: int) -> dict[str, Any]:
    """Search recall (autobiographical message log)."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "query": q[:120],
        "hits": hits,
        "ok": True,
        "note": "memgpt memgpt_recall_search",
    }


def memgpt_archival_search(*, query: str, page: int = 0) -> dict[str, Any]:
    """Paginated archival search."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if page < 0:
        raise SchemaError("page must be >= 0")
    return {
        "query": q[:120],
        "page": page,
        "ok": True,
        "note": "memgpt memgpt_archival_search",
    }


def memgpt_loop_plan(*, phase: str) -> dict[str, Any]:
    """Capacity → page_out → page_in → search."""
    order = ("capacity", "page_out", "page_in", "search")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "capacity"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memgpt memgpt_loop_plan",
    }
