"""MemEngine-shaped modular memory framework (stdlib; no LLM).

Shaped by MemEngine (arXiv:2505.02099 / WWW 2025): three-level stack
(functions → operations → models), config, reflection/optimize ops,
pluggable model registry. Proxies only — not MemEngine paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

LEVELS = frozenset({"function", "operation", "model"})
OPS = frozenset({"recall", "write", "reflect", "optimize"})


def memengine_register_function(*, name: str) -> dict[str, Any]:
    """Register a level-0 memory function (e.g. retrieve)."""
    body = name.strip()
    if not body:
        raise SchemaError("name required")
    fid = hashlib.sha256(
        canonical_dumps({"l": "function", "n": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "function_id": fid,
        "name": body[:80],
        "level": "function",
        "ok": True,
        "note": "memengine memengine_register_function",
    }


def memengine_compose_operation(
    *,
    op: str,
    function_ids: list[str],
) -> dict[str, Any]:
    """Compose level-1 operation from functions."""
    if op not in OPS:
        raise SchemaError(f"op must be one of {sorted(OPS)}")
    ids = [f.strip() for f in function_ids if f.strip()]
    if not ids:
        raise SchemaError("at least one function_id required")
    oid = hashlib.sha256(
        canonical_dumps({"o": op, "f": sorted(ids)}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "operation_id": oid,
        "op": op,
        "function_count": len(ids),
        "ok": True,
        "note": "memengine memengine_compose_operation",
    }


def memengine_bind_model(
    *,
    model_name: str,
    operation_ids: list[str],
) -> dict[str, Any]:
    """Bind a level-2 research model from operations."""
    body = model_name.strip()
    if not body:
        raise SchemaError("model_name required")
    ops = [o.strip() for o in operation_ids if o.strip()]
    if not ops:
        raise SchemaError("at least one operation_id required")
    mid = hashlib.sha256(
        canonical_dumps({"m": body, "o": sorted(ops)}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "model_id": mid,
        "model_name": body[:80],
        "operation_count": len(ops),
        "ok": True,
        "note": "memengine memengine_bind_model",
    }


def memengine_config_set(
    *,
    key: str,
    value: str,
) -> dict[str, Any]:
    """Configuration module hyper-parameter proxy."""
    k = key.strip()
    v = value.strip()
    if not k or not v:
        raise SchemaError("key and value required")
    return {
        "key": k[:64],
        "value": v[:80],
        "ok": True,
        "note": "memengine memengine_config_set",
    }


def memengine_reflect_plan(
    *,
    entries: int,
    min_entries: int = 2,
) -> dict[str, Any]:
    """Reflection/optimization support gate."""
    if entries < 0 or min_entries < 1:
        raise SchemaError("entries >= 0 and min_entries >= 1")
    reflect = entries >= min_entries
    return {
        "reflect": reflect,
        "apply": False,
        "ok": True,
        "note": "memengine memengine_reflect_plan",
    }


def memengine_pluggable(
    *,
    agent_compatible: bool,
) -> dict[str, Any]:
    """Plug-and-play integration gate."""
    return {
        "pluggable": agent_compatible,
        "ok": True,
        "note": "memengine memengine_pluggable",
    }


def memengine_loop_plan(*, phase: str) -> dict[str, Any]:
    """Function → operation → model → reflect."""
    order = ("function", "operation", "model", "reflect")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "function"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memengine memengine_loop_plan",
    }
