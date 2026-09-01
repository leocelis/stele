"""PAL-shaped program-aided language model (stdlib; no LLM / no exec).

Shaped by PAL (arXiv:2211.10435): emit reasoning program, offload solve
to interpreter proxy, read answer. Distinct from Program of Thoughts
(`programofthoughts` / pot_*). Proxies only — never real exec on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def pal_emit_program(*, problem: str, lang: str = "python") -> dict[str, Any]:
    """LLM-shaped emit of an intermediate reasoning program."""
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
        "note": "pal pal_emit_program",
    }


def pal_offload_solve(*, program_id: str) -> dict[str, Any]:
    """Offload solve to interpreter runtime (proxy; report-only)."""
    pid = program_id.strip()
    if not pid:
        raise SchemaError("program_id required")
    rid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "result_id": rid,
        "apply": False,
        "ok": True,
        "note": "pal pal_offload_solve",
    }


def pal_read_answer(*, result_id: str) -> dict[str, Any]:
    """Read final answer from interpreter proxy."""
    rid = result_id.strip()
    if not rid:
        raise SchemaError("result_id required")
    return {
        "result_id": rid[:64],
        "read": True,
        "ok": True,
        "note": "pal pal_read_answer",
    }


def pal_decompose_only(*, llm_solves: bool) -> dict[str, Any]:
    """Flag that LLM only decomposes; solve is offloaded."""
    return {
        "llm_solves": llm_solves,
        "ok": True,
        "note": "pal pal_decompose_only",
    }


def pal_vs_cot(*, program_beats_text: bool) -> dict[str, Any]:
    """Flag program intermediate vs text CoT."""
    return {
        "program_beats_text": program_beats_text,
        "ok": True,
        "note": "pal pal_vs_cot",
    }


def pal_loop_plan(*, phase: str) -> dict[str, Any]:
    """Emit → offload → read → flag."""
    order = ("emit", "offload", "read", "flag")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "emit"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "pal pal_loop_plan",
    }
