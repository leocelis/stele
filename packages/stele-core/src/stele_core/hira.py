"""HiRA proxies (stdlib; no LLM).

Shaped by HiRA — Hadamard High-Rank Adaptation (ICLR 2025 Oral,
OpenReview:TwJrTz9cRS). No arXiv ID after live fetch. Update is
W' = W0 + W0 ⊙ (BA): a low-rank factor pair modulates frozen W0
elementwise so the *effective* update rank is high, then merges
like LoRA (zero extra infer). Proxies only.

Prefix ``hir_*`` — not SHiRA (``shr_*``) / LoHA (``lha_*``) /
MoRA (``mor_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hir_base(*, task: str) -> dict[str, Any]:
    """Freeze W0 for a Hadamard-modulated update."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    bid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "base_id": bid,
        "ok": True,
        "note": "hir hir_base",
    }


def hir_factors(*, base_id: str, rank: int) -> dict[str, Any]:
    """Allocate low-rank A, B (rank >= 1)."""
    bid = base_id.strip()
    if not bid:
        raise SchemaError("base_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    fid = hashlib.sha256(
        canonical_dumps({"b": bid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "factors_id": fid,
        "rank": rank,
        "ok": True,
        "note": "hir hir_factors",
    }


def hir_hadamard(*, factors_id: str) -> dict[str, Any]:
    """Form W0 ⊙ (BA) high-rank update."""
    fid = factors_id.strip()
    if not fid:
        raise SchemaError("factors_id required")
    hid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hadamard_id": hid,
        "ok": True,
        "note": "hir hir_hadamard",
    }


def hir_score(*, hadamard_id: str, score: int) -> dict[str, Any]:
    """Score HiRA run (0–100)."""
    hid = hadamard_id.strip()
    if not hid:
        raise SchemaError("hadamard_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"h": hid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "hir hir_score",
    }


def hir_merge(*, zero_infer: bool) -> dict[str, Any]:
    """Flag merge-into-W0 (zero extra infer; report-only)."""
    return {
        "zero_infer": zero_infer,
        "apply": False,
        "ok": True,
        "note": "hir hir_merge",
    }


def hir_loop_plan(*, phase: str) -> dict[str, Any]:
    """Base → factors → hadamard → score."""
    order = ("base", "factors", "hadamard", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "base"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hir hir_loop_plan",
    }
