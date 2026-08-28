"""HiMem-shaped episode/note hierarchy (stdlib; no LLM).

Shaped by HiMem (arXiv:2601.06377): Episode Memory + Note Memory,
event–surprise dual-channel segmentation, hybrid vs best-effort retrieve,
conflict-aware reconsolidation.
Proxies only — not HiMem paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def himem_segment_episode(
    *,
    topic: str,
    surprise: float,
    surprise_threshold: float = 0.5,
) -> dict[str, Any]:
    """Dual-channel: topic event + surprise gate for episode boundary."""
    top = topic.strip()
    if not top:
        raise SchemaError("topic required")
    if not (0.0 <= surprise <= 1.0):
        raise SchemaError("surprise must be in [0, 1]")
    if not (0.0 <= surprise_threshold <= 1.0):
        raise SchemaError("surprise_threshold must be in [0, 1]")
    boundary = surprise >= surprise_threshold
    eid = hashlib.sha256(
        canonical_dumps({"t": top, "s": surprise}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "episode_id": eid,
        "topic": top[:80],
        "boundary": boundary,
        "ok": True,
        "note": "himem himem_segment_episode",
    }


def himem_extract_note(
    *,
    knowledge: str,
) -> dict[str, Any]:
    """Note Memory: stable knowledge from multi-stage extraction proxy."""
    body = knowledge.strip()
    if not body:
        raise SchemaError("knowledge required")
    nid = hashlib.sha256(
        canonical_dumps({"k": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "note_id": nid,
        "knowledge": body[:200],
        "ok": True,
        "note": "himem himem_extract_note",
    }


def himem_link_episode_note(
    *,
    episode_id: str,
    note_id: str,
) -> dict[str, Any]:
    """Semantically link an episode to abstract note knowledge."""
    e = episode_id.strip()
    n = note_id.strip()
    if not e or not n:
        raise SchemaError("episode_id and note_id required")
    lid = hashlib.sha256(
        canonical_dumps({"e": e, "n": n}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "link_id": lid,
        "episode_id": e[:64],
        "note_id": n[:64],
        "ok": True,
        "note": "himem himem_link_episode_note",
    }


def himem_retrieve_strategy(
    *,
    mode: str,
    note_hit: bool,
) -> dict[str, Any]:
    """hybrid: notes+episodes; best_effort: descend to episodes only if needed."""
    if mode not in ("hybrid", "best_effort"):
        raise SchemaError("mode must be hybrid or best_effort")
    if mode == "hybrid":
        use_episodes = True
    else:
        use_episodes = not note_hit
    return {
        "mode": mode,
        "use_episodes": use_episodes,
        "ok": True,
        "note": "himem himem_retrieve_strategy",
    }


def himem_reconsolidate(
    *,
    conflict: bool,
    missing_knowledge: bool,
) -> dict[str, Any]:
    """Conflict-aware reconsolidation: revise/supplement on retrieval feedback."""
    revise = conflict or missing_knowledge
    return {
        "revise": revise,
        "conflict": conflict,
        "missing_knowledge": missing_knowledge,
        "apply": False,
        "ok": True,
        "note": "himem himem_reconsolidate",
    }


def himem_loop_plan(*, phase: str) -> dict[str, Any]:
    """Construct → retrieve → reconsolidate."""
    order = ("construct", "retrieve", "reconsolidate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "construct"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "himem himem_loop_plan",
    }
