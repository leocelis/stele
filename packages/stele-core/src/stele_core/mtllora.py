"""MTL-LoRA proxies (stdlib; no LLM).

Shaped by MTL-LoRA (arXiv:2410.09437): task-specific low-rank
transforms plus dynamic sharing so multi-task LoRA keeps both
task-specific and task-agnostic knowledge. Proxies only.

Prefix ``mtl_*`` — not MultiLoRA (``mlr_*``) / MALoRA (``mal_*``) /
MoELoRA (``mel_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mtl_task(*, task: str, tasks: int) -> dict[str, Any]:
    """Declare multi-task set (tasks >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if tasks < 2:
        raise SchemaError("tasks must be >= 2")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "n": tasks}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "task_id": tid,
        "tasks": tasks,
        "ok": True,
        "note": "mtl mtl_task",
    }


def mtl_spec(*, task_id: str) -> dict[str, Any]:
    """Allocate task-specific low-rank transforms."""
    tid = task_id.strip()
    if not tid:
        raise SchemaError("task_id required")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "spec_id": sid,
        "ok": True,
        "note": "mtl mtl_spec",
    }


def mtl_share(*, spec_id: str) -> dict[str, Any]:
    """Dynamic share of task-agnostic information."""
    sid = spec_id.strip()
    if not sid:
        raise SchemaError("spec_id required")
    hid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "share_id": hid,
        "ok": True,
        "note": "mtl mtl_share",
    }


def mtl_score(*, share_id: str, score: int) -> dict[str, Any]:
    """Score MTL-LoRA adaptation (0–100)."""
    hid = share_id.strip()
    if not hid:
        raise SchemaError("share_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"h": hid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mtl mtl_score",
    }


def mtl_interfere(*, less_interference: bool) -> dict[str, Any]:
    """Flag reduced task interference (report-only)."""
    return {
        "less_interference": less_interference,
        "apply": False,
        "ok": True,
        "note": "mtl mtl_interfere",
    }


def mtl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Task → spec → share → score."""
    order = ("task", "spec", "share", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "task"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mtl mtl_loop_plan",
    }
