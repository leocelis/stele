"""mLoRA proxies (stdlib; no LLM).

Shaped by mLoRA (arXiv:2312.02515): LoRA-aware pipeline parallelism
across GPUs for simultaneous fine-tuning of multiple adapters, plus
BatchLoRA for shared-backbone batches. Proxies only.

Prefix ``mla_*`` — not MiLoRA (``mil_*``) / MultiLoRA (``mlr_*``) /
Punica (``pun_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mla_pipe(*, tasks: int, gpus: int) -> dict[str, Any]:
    """Declare LoRA-aware pipeline (tasks >= 1, gpus >= 1)."""
    if tasks < 1 or gpus < 1:
        raise SchemaError("tasks and gpus must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": tasks, "g": gpus}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pipe_id": pid,
        "tasks": tasks,
        "gpus": gpus,
        "ok": True,
        "note": "mla mla_pipe",
    }


def mla_batch(*, pipe_id: str) -> dict[str, Any]:
    """BatchLoRA: multiple adapters share base forward."""
    pid = pipe_id.strip()
    if not pid:
        raise SchemaError("pipe_id required")
    bid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "batch_id": bid,
        "ok": True,
        "note": "mla mla_batch",
    }


def mla_train(*, batch_id: str) -> dict[str, Any]:
    """Pipeline-train multiple LoRA tasks."""
    bid = batch_id.strip()
    if not bid:
        raise SchemaError("batch_id required")
    tid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "mla mla_train",
    }


def mla_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score mLoRA fine-tuning efficiency (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mla mla_score",
    }


def mla_eff(*, lower_completion_time: bool) -> dict[str, Any]:
    """Flag reduced task completion time vs FSDP (report-only)."""
    return {
        "lower_completion_time": lower_completion_time,
        "apply": False,
        "ok": True,
        "note": "mla mla_eff",
    }


def mla_loop_plan(*, phase: str) -> dict[str, Any]:
    """Pipe → batch → train → score."""
    order = ("pipe", "batch", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "pipe"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mla mla_loop_plan",
    }
