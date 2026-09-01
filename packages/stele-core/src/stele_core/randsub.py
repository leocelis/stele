"""ROSA random-subspace proxies (stdlib; no LLM).

Shaped by ROSA (arXiv:2407.07802): adapt a random subspace of
arbitrary dimension so expressiveness beats LoRA at the same
memory, zero extra infer. Proxies only.

Prefix ``rsa_*`` — not RoSA robust (``ros_*``) / rsLoRA (``rsl_*``)
/ NLoRA (``nlr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rsa_subspace(*, task: str, dim: int) -> dict[str, Any]:
    """Draw a random subspace (dim >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if dim < 1:
        raise SchemaError("dim must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "d": dim}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "subspace_id": sid,
        "dim": dim,
        "ok": True,
        "note": "rsa rsa_subspace",
    }


def rsa_project(*, subspace_id: str) -> dict[str, Any]:
    """Project W into the random subspace."""
    sid = subspace_id.strip()
    if not sid:
        raise SchemaError("subspace_id required")
    pid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "project_id": pid,
        "ok": True,
        "note": "rsa rsa_project",
    }


def rsa_train(*, project_id: str) -> dict[str, Any]:
    """Train inside the projected subspace."""
    pid = project_id.strip()
    if not pid:
        raise SchemaError("project_id required")
    tid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "rsa rsa_train",
    }


def rsa_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score ROSA run (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "rsa rsa_score",
    }


def rsa_express(*, more_expressive: bool) -> dict[str, Any]:
    """Flag higher expressiveness vs LoRA at same memory (report-only)."""
    return {
        "more_expressive": more_expressive,
        "apply": False,
        "ok": True,
        "note": "rsa rsa_express",
    }


def rsa_loop_plan(*, phase: str) -> dict[str, Any]:
    """Subspace → project → train → score."""
    order = ("subspace", "project", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "subspace"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rsa rsa_loop_plan",
    }
