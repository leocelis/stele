"""Decomposed-Prompting-shaped modular handlers (stdlib; no LLM).

Shaped by Decomposed Prompting (arXiv:2210.02406): decompose to library
handlers, recurse, swap symbolic modules. Proxies only — ≠ Least-to-Most.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dep_decompose(*, task: str, subs: int) -> dict[str, Any]:
    """Decompose a complex task into sub-tasks."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if subs < 1:
        raise SchemaError("subs must be >= 1")
    did = hashlib.sha256(
        canonical_dumps({"t": t, "n": subs}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "decomp_id": did,
        "subs": subs,
        "ok": True,
        "note": "decomposed dep_decompose",
    }


def dep_delegate(*, handler: str, sub_idx: int) -> dict[str, Any]:
    """Delegate a sub-task to a shared handler library entry."""
    h = handler.strip()
    if not h:
        raise SchemaError("handler required")
    if sub_idx < 0:
        raise SchemaError("sub_idx must be >= 0")
    hid = hashlib.sha256(
        canonical_dumps({"h": h, "i": sub_idx}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "delegate_id": hid,
        "handler": h[:64],
        "sub_idx": sub_idx,
        "ok": True,
        "note": "decomposed dep_delegate",
    }


def dep_recurse(*, depth: int) -> dict[str, Any]:
    """Recursive further decomposition depth."""
    if depth < 0:
        raise SchemaError("depth must be >= 0")
    return {
        "depth": depth,
        "ok": True,
        "note": "decomposed dep_recurse",
    }


def dep_swap_symbolic(*, module: str) -> dict[str, Any]:
    """Swap a prompt handler for a symbolic module (report-only)."""
    m = module.strip()
    if not m:
        raise SchemaError("module required")
    return {
        "module": m[:64],
        "apply": False,
        "ok": True,
        "note": "decomposed dep_swap_symbolic",
    }


def dep_library_size(*, handlers: int) -> dict[str, Any]:
    """Count shared prompting-handler library size."""
    if handlers < 0:
        raise SchemaError("handlers must be >= 0")
    return {
        "handlers": handlers,
        "ok": True,
        "note": "decomposed dep_library_size",
    }


def dep_loop_plan(*, phase: str) -> dict[str, Any]:
    """Decompose → delegate → recurse → swap."""
    order = ("decompose", "delegate", "recurse", "swap")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "decompose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "decomposed dep_loop_plan",
    }
