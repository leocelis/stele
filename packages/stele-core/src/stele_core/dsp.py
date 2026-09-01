"""DSP-shaped Demonstrate–Search–Predict (stdlib; no LLM).

Shaped by DSP (arXiv:2212.14024): bootstrap demonstrations, search,
predict, compose programs, multi-hop. Proxies only — not Stanford DSP/DSPy runtime.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dsp_bootstrap_demo(*, task: str, n: int = 3) -> dict[str, Any]:
    """Bootstrap pipeline-aware demonstrations."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n < 1:
        raise SchemaError("n must be >= 1")
    demo_id = hashlib.sha256(
        canonical_dumps({"t": t, "n": n}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "demo_id": demo_id,
        "n": n,
        "ok": True,
        "note": "dsp dsp_bootstrap_demo",
    }


def dsp_search(*, query: str, k: int = 5) -> dict[str, Any]:
    """Search stage: retrieve relevant passages."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "ok": True,
        "note": "dsp dsp_search",
    }


def dsp_predict(*, grounded: bool) -> dict[str, Any]:
    """Predict stage: grounded generation over demos+passages."""
    return {
        "grounded": grounded,
        "ok": True,
        "note": "dsp dsp_predict",
    }


def dsp_compose_program(*, stages: int) -> dict[str, Any]:
    """Compose a high-level DSP program of N stages."""
    if stages < 1:
        raise SchemaError("stages must be >= 1")
    return {
        "stages": stages,
        "ok": True,
        "note": "dsp dsp_compose_program",
    }


def dsp_multihop_hop(*, hop: int) -> dict[str, Any]:
    """One multi-hop search transformation."""
    if hop < 0:
        raise SchemaError("hop must be >= 0")
    return {
        "hop": hop,
        "ok": True,
        "note": "dsp dsp_multihop_hop",
    }


def dsp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Demonstrate → search → predict → compose."""
    order = ("demonstrate", "search", "predict", "compose")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "demonstrate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "dsp dsp_loop_plan",
    }
