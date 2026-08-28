"""HuggingGPT-shaped LLM controller over models (stdlib; no LLM).

Shaped by HuggingGPT (arXiv:2303.17580): plan tasks, select models,
execute subtasks, summarize. Proxies only — no Hugging Face network.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hgpt_plan(*, request: str, tasks: int) -> dict[str, Any]:
    """Controller plans subtasks from a user request."""
    r = request.strip()
    if not r:
        raise SchemaError("request required")
    if tasks < 1:
        raise SchemaError("tasks must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"r": r, "t": tasks}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": pid,
        "tasks": tasks,
        "ok": True,
        "note": "hugginggpt hgpt_plan",
    }


def hgpt_select(*, plan_id: str, model: str) -> dict[str, Any]:
    """Select a model by function description (proxy)."""
    pid = plan_id.strip()
    m = model.strip()
    if not pid or not m:
        raise SchemaError("plan_id and model required")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid, "m": m}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "selection_id": sid,
        "ok": True,
        "note": "hugginggpt hgpt_select",
    }


def hgpt_execute(*, selection_id: str) -> dict[str, Any]:
    """Execute a selected model on a subtask (proxy; report-only)."""
    sid = selection_id.strip()
    if not sid:
        raise SchemaError("selection_id required")
    eid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "result_id": eid,
        "apply": False,
        "ok": True,
        "note": "hugginggpt hgpt_execute",
    }


def hgpt_summarize(*, results: int) -> dict[str, Any]:
    """Summarize execution results into a final response."""
    if results < 0:
        raise SchemaError("results must be >= 0")
    return {
        "results": results,
        "ok": True,
        "note": "hugginggpt hgpt_summarize",
    }


def hgpt_modality(*, modalities: int) -> dict[str, Any]:
    """Count modalities spanned (language/vision/speech…)."""
    if modalities < 0:
        raise SchemaError("modalities must be >= 0")
    return {
        "modalities": modalities,
        "ok": True,
        "note": "hugginggpt hgpt_modality",
    }


def hgpt_loop_plan(*, phase: str) -> dict[str, Any]:
    """Plan → select → execute → summarize."""
    order = ("plan", "select", "execute", "summarize")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "plan"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hugginggpt hgpt_loop_plan",
    }
