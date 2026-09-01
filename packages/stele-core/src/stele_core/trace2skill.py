"""Trace2Skill-shaped parallel skill consolidation (stdlib; no LLM).

Shaped by Trace2Skill (arXiv:2603.25158): parallel trajectory patches
(error/success analysts), hierarchical conflict-free merge into one
portable skill; deepen vs create modes. Proxies only — not paper scores.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def collect_trajectory_label(
    *,
    task: str,
    outcome: str,
    lesson: str = "",
) -> dict[str, Any]:
    """Labeled success/failure trajectory stub for the evolving set."""
    if outcome not in {"success", "failure"}:
        raise SchemaError("outcome must be success|failure")
    if not isinstance(task, str) or not task.strip():
        raise SchemaError("task required")
    tid = hashlib.sha256(
        canonical_dumps({"t": task, "o": outcome, "l": lesson[:120]}).encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return {
        "trajectory_id": tid,
        "task": task.strip()[:120],
        "outcome": outcome,
        "lesson": (lesson or "").strip()[:240],
        "ok": True,
        "note": "trace2skill collect_trajectory_label",
    }


def propose_trajectory_patch(
    *,
    trajectory: Mapping[str, Any],
    base_skill: str = "",
    analyst: str = "auto",
) -> dict[str, Any]:
    """
    Propose a skill patch from one trajectory.
    analyst: error | success | auto (from outcome)
    Failures without a lesson are excluded (ungrounded).
    """
    if not isinstance(trajectory, Mapping):
        raise SchemaError("trajectory mapping required")
    outcome = str(trajectory.get("outcome") or "")
    if analyst == "auto":
        analyst = "error" if outcome == "failure" else "success"
    if analyst not in {"error", "success"}:
        raise SchemaError("analyst must be error|success|auto")
    lesson = str(trajectory.get("lesson") or "").strip()
    if analyst == "error" and not lesson:
        return {
            "proposed": False,
            "reason": "ungrounded_failure",
            "ok": True,
            "note": "trace2skill propose_trajectory_patch — excluded",
        }
    if analyst == "success" and not lesson:
        lesson = f"reuse successful pattern for: {trajectory.get('task') or 'task'}"
    kind = "avoid" if analyst == "error" else "prefer"
    text = f"{kind}: {lesson}"[:240]
    if base_skill.strip():
        text = f"[vs {base_skill.strip()[:40]}] {text}"[:240]
    pid = hashlib.sha256(
        canonical_dumps(
            {
                "tid": trajectory.get("trajectory_id"),
                "a": analyst,
                "p": text,
            }
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "proposed": True,
        "patch_id": pid,
        "analyst": analyst,
        "text": text,
        "source_trajectory": trajectory.get("trajectory_id"),
        "ok": True,
        "note": "trace2skill propose_trajectory_patch",
    }


def parallel_patch_pool(
    trajectories: Sequence[Mapping[str, Any]],
    *,
    base_skill: str = "",
) -> dict[str, Any]:
    """Propose patches in parallel over a trajectory pool (report aggregation)."""
    patches: list[dict[str, Any]] = []
    skipped = 0
    for t in trajectories:
        if not isinstance(t, Mapping):
            continue
        p = propose_trajectory_patch(trajectory=t, base_skill=base_skill)
        if p.get("proposed"):
            patches.append(p)
        else:
            skipped += 1
    return {
        "patches": patches,
        "patch_count": len(patches),
        "skipped": skipped,
        "ok": True,
        "note": "trace2skill parallel_patch_pool",
    }


def hierarchical_merge_patches(
    patches: Sequence[Mapping[str, Any]],
    *,
    merge_branch: int = 4,
) -> dict[str, Any]:
    """
    Hierarchical merge: prefer prevalent token patterns; drop idiosyncratic.
    Conflict = overlapping near-duplicate texts → keep higher recurrence.
    """
    if merge_branch < 2:
        raise SchemaError("merge_branch must be >= 2")
    texts = [
        str(p.get("text") or "").strip()
        for p in patches
        if isinstance(p, Mapping) and p.get("text")
    ]
    if not texts:
        return {
            "merged": False,
            "skill_body": "",
            "levels": 0,
            "apply": False,
            "ok": True,
            "note": "trace2skill hierarchical_merge_patches — empty",
        }
    # recurrence by normalized text
    counts = Counter(t.lower() for t in texts)
    # token prevalence across patches
    token_counts: Counter[str] = Counter()
    for t in texts:
        token_counts.update(_tokens(t))
    # keep unique texts sorted by count then length
    unique = sorted(
        {t.lower(): t for t in texts}.values(),
        key=lambda t: (-counts[t.lower()], -len(t), t),
    )
    # drop lowest half if many idiosyncratic (count==1 and large pool)
    if len(unique) > merge_branch:
        keep = [t for t in unique if counts[t.lower()] > 1] or unique[:merge_branch]
    else:
        keep = unique
    levels = max(1, math.ceil(math.log(max(1, len(patches)), merge_branch)))
    body_lines = [f"- {t}" for t in keep[:12]]
    skill_body = "# Consolidated skill\n" + "\n".join(body_lines)
    return {
        "merged": True,
        "skill_body": skill_body,
        "kept_patches": keep,
        "kept_count": len(keep),
        "levels": levels,
        "prevalent_tokens": [w for w, _ in token_counts.most_common(8)],
        "apply": False,
        "ok": True,
        "note": "trace2skill hierarchical_merge_patches",
    }


def skill_mode_gate(*, mode: str, has_human_skill: bool) -> dict[str, Any]:
    """deepen requires human skill; create starts from parametric draft."""
    if mode not in {"deepen", "create"}:
        raise SchemaError("mode must be deepen|create")
    if mode == "deepen" and not has_human_skill:
        return {
            "allowed": False,
            "mode": mode,
            "reason": "deepen_requires_human_skill",
            "ok": True,
            "note": "trace2skill skill_mode_gate",
        }
    return {
        "allowed": True,
        "mode": mode,
        "reason": None,
        "ok": True,
        "note": "trace2skill skill_mode_gate",
    }


def prefer_parallel_over_sequential(
    *,
    parallel_quality: float,
    sequential_quality: float,
    parallel_minutes: float,
    sequential_minutes: float,
) -> dict[str, Any]:
    """Proxy: prefer parallel when quality >= sequential and faster."""
    prefer = (
        parallel_quality >= sequential_quality - 1e-9
        and parallel_minutes <= sequential_minutes
    )
    return {
        "prefer_parallel": prefer,
        "parallel_quality": parallel_quality,
        "sequential_quality": sequential_quality,
        "parallel_minutes": parallel_minutes,
        "sequential_minutes": sequential_minutes,
        "ok": True,
        "note": "trace2skill prefer_parallel_over_sequential",
    }
