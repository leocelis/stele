"""MindMemOS + MemGuard-shaped memory OS proxies (stdlib; no LLM).

Shaped by:
- MindMemOS (arXiv:2608.12428) — entity–property–time, dreaming consolidate,
  feedback revise, MindSkillEvolve from trajectories.
- MEMGUARD (arXiv:2605.28009) — functional roles + contamination boundaries
  + query-adaptive type routing.

Proxies only — not MindMemOS/MemGuard paper scores or LLM schema search.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

FUNCTIONAL_ROLES = frozenset({"semantic", "episodic", "procedural", "unknown"})

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)

_LAYER_ROLE: dict[str, str] = {
    "decision": "semantic",
    "goal": "semantic",
    "issue": "episodic",
    "failure_lesson": "episodic",
    "workflow": "procedural",
    "skill_artifact": "procedural",
}


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def ept_classify(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Entity–property–time triple view of a Stele entry (MindMemOS EPT)."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    title = str(entry.get("title") or "").strip()
    body = str(entry.get("body") or "").strip()
    scope = str(entry.get("scope") or "").strip()
    entity = scope.split(":")[-1] if scope else (title.split()[0] if title else "unknown")
    # Property = content layer / conflict key stem
    ck = str(entry.get("conflict_key") or "").strip()
    prop = ck.split(":")[-1] if ck else str(entry.get("layer") or "fact")
    temporal = entry.get("temporal") if isinstance(entry.get("temporal"), Mapping) else {}
    t = temporal.get("valid_from") or entry.get("created_at")
    return {
        "id": entry.get("id"),
        "entity": entity,
        "property": prop,
        "time": t,
        "title": title or None,
        "body_digest": hashlib.sha256(body.encode("utf-8")).hexdigest()[:12]
        if body
        else None,
        "ok": True,
        "note": "mindmemos ept_classify — EPT proxy",
    }


def functional_role_assign(entry: Mapping[str, Any]) -> dict[str, Any]:
    """MEMGUARD write-time functional role (semantic/episodic/procedural)."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    layer = str(entry.get("layer") or "").strip()
    role = _LAYER_ROLE.get(layer, "unknown")
    body = f"{entry.get('title') or ''}\n{entry.get('body') or ''}".lower()
    if "procedure" in body or "workflow" in body or "step 1" in body:
        role = "procedural"
    elif "on " in body and any(m in body for m in ("monday", "yesterday", "at ")):
        if role == "unknown":
            role = "episodic"
    return {
        "id": entry.get("id"),
        "functional_role": role,
        "content_layer": layer or None,
        "ok": role in FUNCTIONAL_ROLES,
        "note": "memguard functional_role_assign — type boundary proxy",
    }


def contamination_scan(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Detect heterogeneous memory contamination signals:
    episodic-looking bodies under semantic roles, or mixed conflict_keys.
    """
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence is required")
    issues: list[dict[str, Any]] = []
    by_ck: dict[str, set[str]] = defaultdict(set)
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        role_rep = functional_role_assign(e)
        role = role_rep["functional_role"]
        body = f"{e.get('title') or ''}\n{e.get('body') or ''}".lower()
        eid = str(e.get("id") or "")
        ck = str(e.get("conflict_key") or "").strip()
        if ck:
            by_ck[ck].add(role)
        # Write-time: episodic cues stored as semantic
        episodic_cues = any(
            p in body for p in ("yesterday", "last week", "on monday", "happened")
        )
        if role == "semantic" and episodic_cues:
            issues.append(
                {
                    "id": eid,
                    "kind": "write_time",
                    "issue": "episodic_as_semantic",
                    "functional_role": role,
                }
            )
        # Procedural guidance mixed into episodic issue layer
        if role == "episodic" and (
            "always do" in body or "must never" in body or "policy:" in body
        ):
            issues.append(
                {
                    "id": eid,
                    "kind": "write_time",
                    "issue": "procedural_as_episodic",
                    "functional_role": role,
                }
            )
    for ck, roles in sorted(by_ck.items()):
        if len(roles - {"unknown"}) >= 2:
            issues.append(
                {
                    "conflict_key": ck,
                    "kind": "boundary",
                    "issue": "mixed_roles_same_key",
                    "roles": sorted(roles),
                }
            )
    return {
        "issue_count": len(issues),
        "issues": issues,
        "ok": True,
        "note": "memguard contamination_scan — heterogeneous boundary proxy",
    }


def type_route_retrieve(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    allowed_roles: Sequence[str] | None = None,
    budget: int = 8,
) -> dict[str, Any]:
    """Query-adaptive type routing: only compose evidence from allowed roles."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string is required")
    q = query.lower()
    # Infer roles from query if not provided
    if allowed_roles is None:
        roles: list[str] = []
        if any(w in q for w in ("how", "workflow", "procedure", "steps")):
            roles.append("procedural")
        if any(w in q for w in ("when", "what happened", "session", "yesterday")):
            roles.append("episodic")
        if any(w in q for w in ("policy", "fact", "prefer", "always", "rule")):
            roles.append("semantic")
        if not roles:
            roles = ["semantic", "episodic", "procedural"]
        allowed = roles
    else:
        allowed = [str(r) for r in allowed_roles]

    qtok = _tokens(query)
    scored: list[tuple[int, dict[str, Any]]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        role = functional_role_assign(e)["functional_role"]
        if role not in allowed and role != "unknown":
            continue
        blob = f"{e.get('title') or ''}\n{e.get('body') or ''}"
        score = len(qtok & _tokens(blob))
        if score:
            scored.append(
                (
                    score,
                    {
                        "id": e.get("id"),
                        "functional_role": role,
                        "score": score,
                        "title": e.get("title"),
                    },
                )
            )
    scored.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    hits = [h for _, h in scored[: max(0, budget)]]
    return {
        "query": query.strip(),
        "allowed_roles": allowed,
        "hit_count": len(hits),
        "hits": hits,
        "ok": True,
        "note": "memguard type_route_retrieve — dynamic routing proxy",
    }


def dreaming_consolidate_plan(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Offline dreaming: merge redundant + flag conflicts (report-only)."""
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence is required")
    by_ck: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        ck = str(e.get("conflict_key") or "").strip() or f"id:{e.get('id')}"
        by_ck[ck].append(e)

    merges: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for ck, group in sorted(by_ck.items()):
        if len(group) < 2:
            continue
        bodies = {str(g.get("body") or "").strip() for g in group}
        ids = [str(g.get("id")) for g in group]
        if len(bodies) == 1:
            merges.append(
                {
                    "conflict_key": ck,
                    "entry_ids": ids,
                    "action": "merge_redundant",
                    "keep": ids[0],
                    "drop": ids[1:],
                }
            )
        else:
            conflicts.append(
                {
                    "conflict_key": ck,
                    "entry_ids": ids,
                    "action": "resolve_conflict",
                    "body_variants": len(bodies),
                }
            )
    plan_id = hashlib.sha256(
        canonical_dumps({"m": len(merges), "c": len(conflicts)}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": plan_id,
        "merge_count": len(merges),
        "conflict_count": len(conflicts),
        "merges": merges,
        "conflicts": conflicts,
        "apply": False,
        "ok": True,
        "note": "mindmemos dreaming_consolidate_plan — offline; no auto-delete",
    }


def feedback_revise_plan(
    *,
    signal: str,
    entry_ids: Sequence[str] | None = None,
    mode: str = "explicit",
) -> dict[str, Any]:
    """Convert corrective feedback into structured revise actions (report-only)."""
    if not isinstance(signal, str) or not signal.strip():
        raise SchemaError("signal string is required")
    mode_l = str(mode or "explicit").strip().lower()
    if mode_l not in {"explicit", "implicit"}:
        raise SchemaError("mode must be explicit or implicit")
    text = signal.lower()
    actions: list[dict[str, Any]] = []
    targets = [str(i) for i in (entry_ids or []) if i]
    if any(w in text for w in ("wrong", "incorrect", "not true", "fix")):
        actions.append({"action": "mark_inaccurate", "entry_ids": targets})
    if any(w in text for w in ("outdated", "expired", "no longer", "stale")):
        actions.append({"action": "expire", "entry_ids": targets})
    if any(w in text for w in ("prefer", "instead", "should be", "update to")):
        actions.append({"action": "revise_body", "entry_ids": targets})
    if not actions:
        actions.append({"action": "review", "entry_ids": targets})
    return {
        "mode": mode_l,
        "signal": signal.strip(),
        "action_count": len(actions),
        "actions": actions,
        "apply": False,
        "ok": True,
        "note": "mindmemos feedback_revise_plan — HITL revise proxy",
    }


def skill_evolve_plan(
    trajectories: Sequence[Mapping[str, Any]],
    *,
    supervised: bool = False,
    min_batch: int = 2,
) -> dict[str, Any]:
    """
    MindSkillEvolve-shaped plan: aggregate trajectories under a skill version
    into reinforce / suppress guidance (report-only).
    """
    if not isinstance(trajectories, Sequence) or isinstance(trajectories, (str, bytes)):
        raise SchemaError("trajectories sequence is required")
    by_skill: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for tr in trajectories:
        if not isinstance(tr, Mapping):
            continue
        skill = str(tr.get("skill_id") or tr.get("skill") or "skill:default")
        by_skill[skill].append(tr)

    updates: list[dict[str, Any]] = []
    for skill, batch in sorted(by_skill.items()):
        if len(batch) < min_batch:
            continue
        successes = [
            t
            for t in batch
            if str(t.get("outcome") or "").lower() in {"success", "ok", "pass"}
            or (supervised and float(t.get("score") or 0) >= 0.7)
        ]
        failures = [
            t
            for t in batch
            if str(t.get("outcome") or "").lower() in {"fail", "error", "failure"}
            or (supervised and float(t.get("score") or 1) < 0.4)
        ]
        reinforce = []
        suppress = []
        for t in successes:
            note = str(t.get("strategy") or t.get("note") or "").strip()
            if note:
                reinforce.append(note)
        for t in failures:
            note = str(t.get("error") or t.get("note") or "").strip()
            if note:
                suppress.append(note)
        updates.append(
            {
                "skill_id": skill,
                "batch_size": len(batch),
                "reinforce": sorted(set(reinforce))[:8],
                "suppress": sorted(set(suppress))[:8],
                "supervised": supervised,
                "apply": False,
            }
        )
    return {
        "update_count": len(updates),
        "updates": updates,
        "min_batch": min_batch,
        "supervised": supervised,
        "apply": False,
        "ok": True,
        "note": "mindmemos skill_evolve_plan — Unsup/Sup proxy; no auto-write",
    }
