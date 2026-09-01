"""SAMULE-shaped multi-level reflection (stdlib; no LLM).

Shaped by SAMULE (arXiv:2509.20562): micro/meso/macro reflection synthesis,
foresight reflection, failure-centric learning.
Proxies only — not SAMULE paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

LEVELS = frozenset({"micro", "meso", "macro"})


def single_trajectory_reflect(
    *,
    trajectory_id: str,
    error_note: str,
) -> dict[str, Any]:
    """Micro-level: detailed error correction on one trajectory."""
    tid = trajectory_id.strip()
    note = error_note.strip()
    if not tid or not note:
        raise SchemaError("trajectory_id and error_note required")
    rid = hashlib.sha256(
        canonical_dumps({"t": tid, "n": note}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reflection_id": rid,
        "level": "micro",
        "trajectory_id": tid[:64],
        "note_text": note[:160],
        "ok": True,
        "note": "samule single_trajectory_reflect",
    }


def intra_task_taxonomy(
    *,
    error_labels: Sequence[str],
) -> dict[str, Any]:
    """Meso-level: build error taxonomy across trials of the same task."""
    if not isinstance(error_labels, Sequence) or isinstance(
        error_labels, (str, bytes)
    ):
        raise SchemaError("error_labels sequence required")
    cleaned = sorted({str(e).strip() for e in error_labels if str(e).strip()})
    if not cleaned:
        raise SchemaError("error_labels required")
    return {
        "level": "meso",
        "taxonomy": cleaned[:20],
        "error_count": len(cleaned),
        "ok": True,
        "note": "samule intra_task_taxonomy",
    }


def inter_task_transfer(
    *,
    error_type: str,
    strategy: str,
) -> dict[str, Any]:
    """Macro-level: transferable insight for a typed error across tasks."""
    et = error_type.strip()
    strat = strategy.strip()
    if not et or not strat:
        raise SchemaError("error_type and strategy required")
    tid = hashlib.sha256(
        canonical_dumps({"e": et, "s": strat}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "insight_id": tid,
        "level": "macro",
        "error_type": et[:80],
        "strategy": strat[:160],
        "ok": True,
        "note": "samule inter_task_transfer",
    }


def foresight_reflect(
    *,
    predicted: str,
    actual: str,
) -> dict[str, Any]:
    """Compare predicted vs actual response; mismatch triggers foresight reflect."""
    pred = predicted.strip()
    act = actual.strip()
    if not pred or not act:
        raise SchemaError("predicted and actual required")
    mismatch = pred != act
    return {
        "mismatch": mismatch,
        "reflect": mismatch,
        "ok": True,
        "note": "samule foresight_reflect",
    }


def failure_centric_gate(
    *,
    success_count: int,
    failure_count: int,
) -> dict[str, Any]:
    """Prefer failure-centric learning over rare success-only reflections."""
    if success_count < 0 or failure_count < 0:
        raise SchemaError("counts must be >= 0")
    prefer_failures = failure_count > 0 or success_count == 0
    return {
        "prefer_failures": prefer_failures,
        "failure_count": failure_count,
        "success_count": success_count,
        "apply": False,
        "ok": True,
        "note": "samule failure_centric_gate",
    }


def merge_reflections(
    *,
    levels_present: Sequence[str],
) -> dict[str, Any]:
    """Merge micro/meso/macro reflections into one final reflection proxy."""
    if not isinstance(levels_present, Sequence) or isinstance(
        levels_present, (str, bytes)
    ):
        raise SchemaError("levels_present sequence required")
    cleaned = [str(l).strip() for l in levels_present if str(l).strip()]
    for lv in cleaned:
        if lv not in LEVELS:
            raise SchemaError(f"level must be one of {sorted(LEVELS)}")
    complete = LEVELS.issubset(set(cleaned))
    return {
        "merged": True,
        "levels": cleaned,
        "complete": complete,
        "ok": True,
        "note": "samule merge_reflections",
    }
