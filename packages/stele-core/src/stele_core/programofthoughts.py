"""Program-of-Thoughts-shaped code+interpreter (stdlib; no LLM / no exec).

Shaped by Program of Thoughts (arXiv:2211.12588): emit program, sandbox
proxy run, read result, optional self-consistency. Proxies only — never
executes untrusted code on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def pot_emit_program(*, problem: str, lang: str = "python") -> dict[str, Any]:
    """Emit a reasoning program (proxy id only)."""
    p = problem.strip()
    l = lang.strip()
    if not p:
        raise SchemaError("problem required")
    if not l:
        raise SchemaError("lang required")
    pid = hashlib.sha256(
        canonical_dumps({"p": p, "l": l}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "program_id": pid,
        "lang": l[:32],
        "ok": True,
        "note": "pot pot_emit_program",
    }


def pot_sandbox_run(*, program_id: str) -> dict[str, Any]:
    """Sandbox-run proxy — report-only, never real exec."""
    pid = program_id.strip()
    if not pid:
        raise SchemaError("program_id required")
    rid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "result_id": rid,
        "program_id": pid[:64],
        "apply": False,
        "ok": True,
        "note": "pot pot_sandbox_run",
    }


def pot_read_result(*, result_id: str) -> dict[str, Any]:
    """Read interpreter result from proxy."""
    rid = result_id.strip()
    if not rid:
        raise SchemaError("result_id required")
    return {
        "result_id": rid[:64],
        "read": True,
        "ok": True,
        "note": "pot pot_read_result",
    }


def pot_self_consistency(*, samples: int) -> dict[str, Any]:
    """Count PoT+self-consistency samples."""
    if samples < 0:
        raise SchemaError("samples must be >= 0")
    return {
        "samples": samples,
        "ok": True,
        "note": "pot pot_self_consistency",
    }


def pot_disentangle(*, compute_offloaded: bool) -> dict[str, Any]:
    """Flag that computation is offloaded from reasoning."""
    return {
        "compute_offloaded": compute_offloaded,
        "ok": True,
        "note": "pot pot_disentangle",
    }


def pot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Emit → run → read → vote."""
    order = ("emit", "run", "read", "vote")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "emit"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "pot pot_loop_plan",
    }
