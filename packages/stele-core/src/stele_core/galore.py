"""GaLore proxies (stdlib; no LLM).

Shaped by GaLore (arXiv:2403.03507): project gradients onto low-rank
subspaces during full-parameter training — memory-efficient optimizer
path, not an adapter. Proxies only.

Prefix ``gal_*`` — not LoRA-GA (``lga_*``) / DropLoRA (``drl_*``) / AdaLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def gal_grad(*, task: str) -> dict[str, Any]:
    """Capture full-parameter gradients for projection."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    gid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "grad_id": gid,
        "ok": True,
        "note": "gal gal_grad",
    }


def gal_project(*, grad_id: str, rank: int) -> dict[str, Any]:
    """Project gradients onto a low-rank subspace (rank >= 1)."""
    gid = grad_id.strip()
    if not gid:
        raise SchemaError("grad_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"g": gid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "project_id": pid,
        "rank": rank,
        "ok": True,
        "note": "gal gal_project",
    }


def gal_step(*, project_id: str) -> dict[str, Any]:
    """Optimizer step in the projected subspace."""
    pid = project_id.strip()
    if not pid:
        raise SchemaError("project_id required")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "step_id": sid,
        "ok": True,
        "note": "gal gal_step",
    }


def gal_score(*, step_id: str, score: int) -> dict[str, Any]:
    """Score GaLore training run (0–100)."""
    sid = step_id.strip()
    if not sid:
        raise SchemaError("step_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    scid = hashlib.sha256(
        canonical_dumps({"s": sid, "c": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": scid,
        "score": score,
        "ok": True,
        "note": "gal gal_score",
    }


def gal_full(*, updates_all_weights: bool) -> dict[str, Any]:
    """Flag full-parameter updates (not adapter-only) (report-only)."""
    return {
        "updates_all_weights": updates_all_weights,
        "apply": False,
        "ok": True,
        "note": "gal gal_full",
    }


def gal_loop_plan(*, phase: str) -> dict[str, Any]:
    """Grad → project → step → score."""
    order = ("grad", "project", "step", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "grad"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "gal gal_loop_plan",
    }
