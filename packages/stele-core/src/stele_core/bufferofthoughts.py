"""Buffer-of-Thoughts-shaped meta-buffer (stdlib; no LLM).

Shaped by Buffer of Thoughts (arXiv:2406.04271): distill templates,
retrieve, instantiate, buffer-manager update. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def bot_distill_template(*, task: str) -> dict[str, Any]:
    """Distill a thought-template into the meta-buffer."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    tid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "template_id": tid,
        "ok": True,
        "note": "bot bot_distill_template",
    }


def bot_retrieve_template(*, query: str) -> dict[str, Any]:
    """Retrieve a relevant thought-template for a problem."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    rid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "retrieval_id": rid,
        "ok": True,
        "note": "bot bot_retrieve_template",
    }


def bot_instantiate(*, template_id: str) -> dict[str, Any]:
    """Instantiate a template with a concrete reasoning structure."""
    tid = template_id.strip()
    if not tid:
        raise SchemaError("template_id required")
    iid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "instance_id": iid,
        "template_id": tid[:64],
        "ok": True,
        "note": "bot bot_instantiate",
    }


def bot_buffer_update(*, templates: int) -> dict[str, Any]:
    """Buffer-manager update of meta-buffer size (report-only)."""
    if templates < 0:
        raise SchemaError("templates must be >= 0")
    return {
        "templates": templates,
        "apply": False,
        "ok": True,
        "note": "bot bot_buffer_update",
    }


def bot_cost_ratio(*, multi_query: int, bot: int) -> dict[str, Any]:
    """Compare BoT cost vs multi-query prompting."""
    if multi_query < 0 or bot < 0:
        raise SchemaError("multi_query and bot must be >= 0")
    return {
        "multi_query": multi_query,
        "bot": bot,
        "cheaper": bot < multi_query,
        "ok": True,
        "note": "bot bot_cost_ratio",
    }


def bot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Distill → retrieve → instantiate → update."""
    order = ("distill", "retrieve", "instantiate", "update")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "distill"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "bot bot_loop_plan",
    }
