"""Chameleon-shaped plug-and-play compositional reasoning (stdlib; no LLM).

Shaped by Chameleon (arXiv:2304.09842): inventory tools, plan sequence,
compose modules, execute. Proxies only — ≠ HuggingGPT.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cham_inventory(*, tools: int) -> dict[str, Any]:
    """Count tools in the plug-and-play inventory."""
    if tools < 1:
        raise SchemaError("tools must be >= 1")
    return {
        "tools": tools,
        "ok": True,
        "note": "chameleon cham_inventory",
    }


def cham_plan(*, task: str, modules: int) -> dict[str, Any]:
    """LLM-shaped planner assembles a tool sequence."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if modules < 1:
        raise SchemaError("modules must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "m": modules}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": pid,
        "modules": modules,
        "ok": True,
        "note": "chameleon cham_plan",
    }


def cham_compose(*, plan_id: str, module: str) -> dict[str, Any]:
    """Append a module into the compositional program."""
    pid = plan_id.strip()
    m = module.strip()
    if not pid or not m:
        raise SchemaError("plan_id and module required")
    cid = hashlib.sha256(
        canonical_dumps({"p": pid, "m": m}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "compose_id": cid,
        "ok": True,
        "note": "chameleon cham_compose",
    }


def cham_execute(*, plan_id: str) -> dict[str, Any]:
    """Execute the composed tool sequence (proxy; report-only)."""
    pid = plan_id.strip()
    if not pid:
        raise SchemaError("plan_id required")
    eid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "result_id": eid,
        "apply": False,
        "ok": True,
        "note": "chameleon cham_execute",
    }


def cham_constraint(*, inferred: bool) -> dict[str, Any]:
    """Flag planner inferring constraints from instructions."""
    return {
        "inferred": inferred,
        "ok": True,
        "note": "chameleon cham_constraint",
    }


def cham_loop_plan(*, phase: str) -> dict[str, Any]:
    """Inventory → plan → compose → execute."""
    order = ("inventory", "plan", "compose", "execute")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "inventory"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "chameleon cham_loop_plan",
    }
