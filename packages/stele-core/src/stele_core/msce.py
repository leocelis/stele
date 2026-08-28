"""MSCE-shaped memory→skill co-evolution proxies (stdlib; no LLM).

Evidence-backed policies crystallize into callable skill_artifact drafts with
eligibility gates and reflection-weighted value backfill. Proxies only.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError


def skill_eligibility(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    Whether an entry may crystallize into a skill (MSCE-shaped).

    Requires: promoted, layer in {failure_lesson, workflow, skill_artifact},
    positive net usage or pin, and evidence or entry links.
    """
    state = str(entry.get("state") or "")
    layer = str(entry.get("layer") or "")
    usage = entry.get("usage") or {}
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    net = helpful - harmful
    pinned = bool(usage.get("pinned"))
    has_ev = bool(entry.get("evidence"))
    has_links = bool(entry.get("links"))
    barriers: list[str] = []
    if state != "promoted":
        barriers.append(f"state={state}")
    if layer not in {"failure_lesson", "workflow", "skill_artifact"}:
        barriers.append(f"layer={layer}")
    if net <= 0 and not pinned:
        barriers.append("nonpositive_gain")
    if not has_ev and not has_links:
        barriers.append("missing_evidence_links")
    ok = len(barriers) == 0
    return {
        "ok": ok,
        "eligible": ok,
        "barriers": barriers,
        "net_gain": net,
        "entry_id": entry.get("id"),
        "note": "MSCE skill eligibility — evidence-backed positive gain",
    }


def crystallize_skill(
    entries: Iterable[Mapping[str, Any]],
    source_ids: Sequence[str],
    *,
    title: str | None = None,
    scope: str | None = None,
    env_assumptions: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Build a skill_artifact draft from eligible source entries (does not write).

    Retains evidence links + applicability boundary stubs.
    """
    by_id = {str(e.get("id")): e for e in entries}
    sources: list[dict[str, Any]] = []
    barriers: list[str] = []
    for sid in source_ids:
        e = by_id.get(str(sid))
        if e is None:
            barriers.append(f"missing:{sid}")
            continue
        elig = skill_eligibility(e)
        if not elig.get("eligible"):
            barriers.append(f"ineligible:{sid}:{','.join(elig.get('barriers') or [])}")
            continue
        sources.append(e)
    if not sources:
        return {
            "ok": False,
            "draft": None,
            "barriers": barriers or ["no_eligible_sources"],
            "note": "MSCE crystallize refused",
        }
    primary = sources[0]
    skill_title = title or f"Skill: {primary.get('title')}"
    skill_scope = scope or str(primary.get("scope") or "project:local")
    bodies = [str(s.get("body") or "") for s in sources]
    procedure = "\n---\n".join(bodies)
    env = list(env_assumptions) if env_assumptions else list(
        primary.get("env_assumptions") or ["runtime:local"]
    )
    if not env:
        env = ["runtime:local"]
    links = [
        {"kind": "entry", "ref": str(s.get("id"))} for s in sources if s.get("id")
    ]
    draft = {
        "layer": "skill_artifact",
        "title": skill_title,
        "body": (
            f"PROCEDURE\n{procedure}\n\n"
            "VERIFICATION: re-run linked evidence commands before promote.\n"
            "APPLICABILITY: only under env_assumptions; abstain on mismatch."
        ),
        "scope": skill_scope,
        "env_assumptions": env,
        "temporal": dict(primary.get("temporal") or {}),
        "provenance": {
            **dict(primary.get("provenance") or {}),
            "task": "msce_crystallize",
            "source": "msce:crystallize",
        },
        "links": links,
        "cue_tags": ["msce:skill"],
        "memory_role": "claim",
        "usage": {"helpful": 0, "harmful": 0, "pinned": False},
    }
    # Ensure temporal keys exist for ADD
    if "valid_from" not in draft["temporal"]:
        written = str((primary.get("provenance") or {}).get("written_at") or "")
        draft["temporal"] = {
            "valid_from": written,
            "last_verified": written,
        }
    return {
        "ok": True,
        "draft": draft,
        "source_ids": [str(s.get("id")) for s in sources],
        "barriers": barriers,
        "note": "MSCE skill draft — caller ADD + promote with evidence",
    }


def value_backfill(
    entry: Mapping[str, Any],
    *,
    terminal_success: bool,
    reflection_weight: float = 1.0,
) -> dict[str, Any]:
    """
    Reflection-weighted usage update plan (MSCE backfill).

    Returns proposed usage delta — does not write unless caller applies.
    """
    if reflection_weight < 0:
        raise SchemaError("reflection_weight must be >= 0")
    usage = dict(entry.get("usage") or {})
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    delta = max(1, int(round(reflection_weight)))
    if terminal_success:
        helpful += delta
    else:
        harmful += delta
    proposed = {
        "helpful": helpful,
        "harmful": harmful,
        "pinned": bool(usage.get("pinned")),
    }
    return {
        "entry_id": entry.get("id"),
        "terminal_success": terminal_success,
        "reflection_weight": reflection_weight,
        "usage_before": dict(usage),
        "usage_after": proposed,
        "note": "MSCE value backfill plan — apply via record_outcome / usage write",
    }


def skill_catalog(
    entries: Iterable[Mapping[str, Any]],
    *,
    states: Sequence[str] | None = None,
) -> dict[str, Any]:
    """List skill_artifact entries (callable skill surface)."""
    allow = set(states or ["promoted", "quarantined"])
    skills: list[dict[str, Any]] = []
    for e in entries:
        if e.get("layer") != "skill_artifact":
            continue
        if e.get("state") not in allow:
            continue
        elig = skill_eligibility(e) if e.get("state") == "promoted" else {
            "eligible": False,
            "barriers": ["not_promoted"],
        }
        skills.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "state": e.get("state"),
                "scope": e.get("scope"),
                "env_assumptions": list(e.get("env_assumptions") or []),
                "eligible": elig.get("eligible"),
                "links": len(e.get("links") or []),
            }
        )
    skills.sort(key=lambda r: str(r.get("id")))
    return {
        "skills": skills,
        "count": len(skills),
        "note": "MSCE skill catalog — callable surface over skill_artifact entries",
    }
