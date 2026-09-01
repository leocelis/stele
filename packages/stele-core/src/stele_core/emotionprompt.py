"""EmotionPrompt proxies (stdlib; no LLM).

Shaped by EmotionPrompt (arXiv:2307.11760): append emotional stimuli
to prompts to lift task performance. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def emo_stimulus(*, text: str) -> dict[str, Any]:
    """Register an emotional stimulus phrase."""
    t = text.strip()
    if not t:
        raise SchemaError("text required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "stimulus_id": sid,
        "ok": True,
        "note": "emo emo_stimulus",
    }


def emo_append(*, prompt: str, stimulus_id: str) -> dict[str, Any]:
    """Append stimulus to the original prompt."""
    p = prompt.strip()
    sid = stimulus_id.strip()
    if not p or not sid:
        raise SchemaError("prompt and stimulus_id required")
    aid = hashlib.sha256(
        canonical_dumps({"p": p, "s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prompt_id": aid,
        "ok": True,
        "note": "emo emo_append",
    }


def emo_run(*, prompt_id: str) -> dict[str, Any]:
    """Run the emotion-augmented prompt (proxy)."""
    pid = prompt_id.strip()
    if not pid:
        raise SchemaError("prompt_id required")
    rid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "run_id": rid,
        "ok": True,
        "note": "emo emo_run",
    }


def emo_truth(*, improved: bool) -> dict[str, Any]:
    """Flag improved truthfulness under EmotionPrompt."""
    return {
        "improved": improved,
        "ok": True,
        "note": "emo emo_truth",
    }


def emo_psych(*, psychology: bool) -> dict[str, Any]:
    """Flag psychology-inspired stimulus design (report-only)."""
    return {
        "psychology": psychology,
        "apply": False,
        "ok": True,
        "note": "emo emo_psych",
    }


def emo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Stimulus → append → run → truth."""
    order = ("stimulus", "append", "run", "truth")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "stimulus"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "emo emo_loop_plan",
    }
