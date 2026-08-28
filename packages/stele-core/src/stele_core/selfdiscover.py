"""Self-Discover-shaped structure composition (stdlib; no LLM).

Shaped by Self-Discover (arXiv:2402.03620): select modules, adapt,
implement JSON structure, apply per instance. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sd_select_modules(*, task: str, modules: int) -> dict[str, Any]:
    """Select atomic reasoning modules for a task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if modules < 1:
        raise SchemaError("modules must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "m": modules}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "select_id": sid,
        "modules": modules,
        "ok": True,
        "note": "selfdiscover sd_select_modules",
    }


def sd_adapt(*, select_id: str) -> dict[str, Any]:
    """Adapt selected modules to the task."""
    sid = select_id.strip()
    if not sid:
        raise SchemaError("select_id required")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapt_id": aid,
        "select_id": sid[:64],
        "ok": True,
        "note": "selfdiscover sd_adapt",
    }


def sd_implement(*, adapt_id: str, keys: int) -> dict[str, Any]:
    """Implement actionable JSON reasoning structure."""
    aid = adapt_id.strip()
    if not aid:
        raise SchemaError("adapt_id required")
    if keys < 1:
        raise SchemaError("keys must be >= 1")
    iid = hashlib.sha256(
        canonical_dumps({"a": aid, "k": keys}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "structure_id": iid,
        "keys": keys,
        "ok": True,
        "note": "selfdiscover sd_implement",
    }


def sd_apply_instance(*, structure_id: str) -> dict[str, Any]:
    """Apply discovered structure to one instance (report-only)."""
    sid = structure_id.strip()
    if not sid:
        raise SchemaError("structure_id required")
    return {
        "structure_id": sid[:64],
        "apply": False,
        "ok": True,
        "note": "selfdiscover sd_apply_instance",
    }


def sd_compute_ratio(*, sc_calls: int, self_discover: int) -> dict[str, Any]:
    """Compare Self-Discover compute vs self-consistency calls."""
    if sc_calls < 0 or self_discover < 0:
        raise SchemaError("sc_calls and self_discover must be >= 0")
    return {
        "sc_calls": sc_calls,
        "self_discover": self_discover,
        "cheaper": self_discover < sc_calls,
        "ok": True,
        "note": "selfdiscover sd_compute_ratio",
    }


def sd_loop_plan(*, phase: str) -> dict[str, Any]:
    """Select → adapt → implement → apply."""
    order = ("select", "adapt", "implement", "apply")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "select"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "selfdiscover sd_loop_plan",
    }
