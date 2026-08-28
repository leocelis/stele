"""AgentHER-shaped hindsight failure relabeling (stdlib; no LLM).

Shaped by AgentHER (arXiv:2603.21357): failure classify → outcome extract
→ hindsight relabel with confidence gate → SFT/DPO packaging.
Proxies only — not AgentHER paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

FAILURE_TYPES = frozenset(
    {
        "Incomplete",
        "Constraint_Violation",
        "Wrong_Result",
        "Tool_Error",
        "Hallucination",
        "Off_Topic",
    }
)
PACK_FORMATS = frozenset({"SFT", "DPO", "ShareGPT"})


def classify_failure(
    *,
    failure_type: str,
    observation_chars: int = 0,
    severity: float | None = None,
) -> dict[str, Any]:
    """Stage 1: failure type, recoverability, severity weight."""
    if failure_type not in FAILURE_TYPES:
        raise SchemaError(f"failure_type must be one of {sorted(FAILURE_TYPES)}")
    if severity is None:
        # rule-based proxy: Tool_Error / Hallucination → major
        if failure_type in {"Tool_Error", "Hallucination"}:
            severity = 0.2
        elif failure_type == "Off_Topic":
            severity = 0.25
        else:
            severity = 0.6
    severity = float(severity)
    recoverable = (
        observation_chars >= 20 and failure_type != "Tool_Error" and severity >= 0.3
    )
    return {
        "failure_type": failure_type,
        "severity": round(severity, 4),
        "recoverable": recoverable,
        "discard": not recoverable,
        "ok": True,
        "note": "agenther classify_failure",
    }


def extract_replay_outcome(
    *,
    observations: Sequence[str],
    max_items: int = 5,
) -> dict[str, Any]:
    """Stage 2: ReplayOutcome — achieved facts from observations."""
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        raise SchemaError("observations sequence required")
    items = [str(o).strip() for o in observations if str(o).strip()][:max_items]
    return {
        "achievements": items,
        "achievement_count": len(items),
        "ok": True,
        "note": "agenther extract_replay_outcome",
    }


def hindsight_relabel_plan(
    *,
    original_goal: str,
    achievements: Sequence[str],
    confidence: float = 0.85,
    theta: float = 0.7,
) -> dict[str, Any]:
    """Stage 3: synthesise hindsight goal from achievements (proxy text)."""
    if not isinstance(original_goal, str) or not original_goal.strip():
        raise SchemaError("original_goal required")
    ach = [str(a).strip() for a in achievements if str(a).strip()]
    if not ach:
        return {
            "accepted": False,
            "reason": "no_achievements",
            "hindsight_goal": None,
            "confidence": confidence,
            "apply": False,
            "ok": True,
            "note": "agenther hindsight_relabel_plan",
        }
    # Hindsight goal = describe what was actually achieved
    hindsight = f"Demonstrate: {'; '.join(ach[:3])}"[:200]
    accepted = confidence >= theta
    return {
        "accepted": accepted,
        "hindsight_goal": hindsight if accepted else None,
        "original_goal": original_goal.strip()[:120],
        "confidence": confidence,
        "theta": theta,
        "apply": False,
        "ok": True,
        "note": "agenther hindsight_relabel_plan",
    }


def multi_judge_accept(
    *,
    confidence_j1: float,
    confidence_j2: float,
    theta: float = 0.7,
) -> dict[str, Any]:
    """Cross-model multi-judge: both must pass theta."""
    ok1 = confidence_j1 >= theta
    ok2 = confidence_j2 >= theta
    return {
        "accepted": ok1 and ok2,
        "j1_ok": ok1,
        "j2_ok": ok2,
        "theta": theta,
        "ok": True,
        "note": "agenther multi_judge_accept",
    }


def package_training_pair(
    *,
    format: str,
    hindsight_goal: str,
    original_goal: str,
    trajectory_summary: str = "",
    severity_weight: float = 1.0,
) -> dict[str, Any]:
    """Stage 4: package SFT / DPO / ShareGPT training pair."""
    if format not in PACK_FORMATS:
        raise SchemaError(f"format must be one of {sorted(PACK_FORMATS)}")
    if not hindsight_goal.strip():
        raise SchemaError("hindsight_goal required")
    pid = hashlib.sha256(
        canonical_dumps(
            {"f": format, "h": hindsight_goal, "o": original_goal}
        ).encode("utf-8")
    ).hexdigest()[:12]
    if format == "SFT":
        payload = {
            "messages": [
                {"role": "user", "content": hindsight_goal.strip()[:200]},
                {
                    "role": "assistant",
                    "content": (trajectory_summary or "execute trajectory").strip()[
                        :240
                    ],
                },
            ],
            "weight": severity_weight,
        }
    elif format == "DPO":
        payload = {
            "chosen": {"goal": hindsight_goal.strip()[:200]},
            "rejected": {"goal": original_goal.strip()[:200]},
            "weight": severity_weight,
        }
    else:  # ShareGPT
        payload = {
            "conversations": [
                {"from": "human", "value": hindsight_goal.strip()[:200]},
                {
                    "from": "gpt",
                    "value": (trajectory_summary or "ok").strip()[:240],
                },
            ]
        }
    return {
        "pair_id": pid,
        "format": format,
        "payload": payload,
        "ok": True,
        "note": "agenther package_training_pair",
    }
