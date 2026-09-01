"""Governed Memory-shaped dual project + routing + session delta + entity isolation.

Stdlib only. No LLM on write path. Proxies for arXiv:2603.17787 mechanisms —
not Personize production scores.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

SESSION_DELTA_NAME = "session_delta.json"
DEFAULT_ENTITY_SATURATION = 7

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def dual_project(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    Dual memory projection: open-set atomic facts + schema-typed properties.

    Facts = distilled body sentences (no LLM). Properties = structured fields.
    """
    body = str(entry.get("body") or "").strip()
    title = str(entry.get("title") or "").strip()
    raw_sents = [s.strip() for s in _SENT_SPLIT.split(body) if s.strip()]
    if not raw_sents and body:
        raw_sents = [body]
    facts = []
    for i, s in enumerate(raw_sents[:12]):
        facts.append(
            {
                "text": s,
                "kind": "atomic_fact",
                "source_field": "body",
                "ordinal": i,
            }
        )
    if title and not any(title.lower() in f["text"].lower() for f in facts):
        facts.insert(
            0,
            {
                "text": title,
                "kind": "atomic_fact",
                "source_field": "title",
                "ordinal": -1,
            },
        )
    usage = entry.get("usage") or {}
    temporal = entry.get("temporal") or {}
    provenance = entry.get("provenance") or {}
    properties = {
        "layer": entry.get("layer"),
        "scope": entry.get("scope"),
        "state": entry.get("state"),
        "subject_id": provenance.get("subject_id"),
        "source": provenance.get("source"),
        "conflict_key": entry.get("conflict_key"),
        "pinned": bool(usage.get("pinned")),
        "helpful": int(usage.get("helpful") or 0),
        "harmful": int(usage.get("harmful") or 0),
        "valid_from": temporal.get("valid_from"),
        "last_verified": temporal.get("last_verified"),
        "env_assumptions": list(entry.get("env_assumptions") or []),
        "assessment_domain_depth": (entry.get("assessment") or {}).get(
            "domain_depth"
        ),
    }
    return {
        "id": entry.get("id"),
        "atomic_facts": facts,
        "typed_properties": properties,
        "fact_count": len(facts),
        "ok": True,
        "note": "Governed Memory dual project — deterministic; not LLM dual extract",
    }


def governance_route(
    task: str,
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 7,
    critical_threshold: float = 0.35,
) -> dict[str, Any]:
    """
    Fast governance-aware hybrid path (no LLM): rank policy-like entries for a task.
    """
    q = str(task or "").strip()
    if not q:
        raise SchemaError("task is required")
    if not (0 <= critical_threshold <= 1):
        raise SchemaError("critical_threshold must be in [0, 1]")
    qtok = set(tokenize(q))
    policy_layers = {"decision", "workflow", "skill_artifact", "goal"}
    scored: list[tuple[float, dict[str, Any]]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        if e.get("layer") not in policy_layers:
            continue
        blob = f"{e.get('title')}\n{e.get('body')}"
        etok = set(tokenize(blob))
        overlap = len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0
        pin_boost = 0.1 if (e.get("usage") or {}).get("pinned") else 0.0
        helpful = int((e.get("usage") or {}).get("helpful") or 0)
        harm = int((e.get("usage") or {}).get("harmful") or 0)
        polarity = (helpful - harm) / max(helpful + harm, 1)
        score = round(overlap + pin_boost + 0.05 * max(0.0, polarity), 6)
        if score <= 0:
            continue
        tier = "critical" if score >= critical_threshold else "supplementary"
        scored.append(
            (
                score,
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "layer": e.get("layer"),
                    "score": score,
                    "tier": tier,
                },
            )
        )
    scored.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    selected = [row for _, row in scored[: max(1, int(limit))]]
    return {
        "task": q,
        "selected": selected,
        "count": len(selected),
        "path": "fast_hybrid",
        "ok": True,
        "note": "Governed Memory governance_route — fast hybrid only; no LLM full path",
    }


def _delta_path(root: Path) -> Path:
    return Path(root) / SESSION_DELTA_NAME


def load_session_delta(root: Path) -> dict[str, Any]:
    path = _delta_path(root)
    if not path.is_file():
        return {"sessions": {}}
    data = canonical_loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SchemaError("session_delta.json must be an object")
    sessions = data.get("sessions")
    if sessions is None:
        sessions = {}
    if not isinstance(sessions, dict):
        raise SchemaError("sessions must be an object")
    return {"sessions": sessions}


def save_session_delta(root: Path, data: Mapping[str, Any]) -> None:
    _delta_path(root).write_text(canonical_dumps(dict(data)), encoding="utf-8")


def session_delta_open(
    root: Path,
    session_id: str,
    *,
    ttl_hours: float = 24.0,
) -> dict[str, Any]:
    sid = str(session_id or "").strip()
    if not sid:
        raise SchemaError("session_id is required")
    store = load_session_delta(root)
    sessions = store["sessions"]
    sessions[sid] = {
        "delivered_critical": [],
        "ttl_hours": float(ttl_hours),
    }
    save_session_delta(root, store)
    return {
        "session_id": sid,
        "delivered_critical": [],
        "ttl_hours": float(ttl_hours),
        "ok": True,
        "note": "Governed Memory session delta opened",
    }


def session_delta_deliver(
    root: Path,
    session_id: str,
    route: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Progressive delivery: skip already-delivered critical ids; never lock supplementary.
    """
    sid = str(session_id or "").strip()
    if not sid:
        raise SchemaError("session_id is required")
    store = load_session_delta(root)
    sessions = store["sessions"]
    sess = sessions.get(sid)
    if sess is None:
        raise SchemaError(f"unknown session_id: {sid}")
    delivered = set(str(x) for x in (sess.get("delivered_critical") or []))
    inject: list[dict[str, Any]] = []
    skipped: list[str] = []
    newly: list[str] = []
    for row in route.get("selected") or []:
        eid = str(row.get("id") or "")
        if not eid:
            continue
        tier = str(row.get("tier") or "supplementary")
        if tier == "critical" and eid in delivered:
            skipped.append(eid)
            continue
        inject.append(dict(row))
        if tier == "critical":
            newly.append(eid)
            delivered.add(eid)
    sess["delivered_critical"] = sorted(delivered)
    sessions[sid] = sess
    save_session_delta(root, store)
    return {
        "session_id": sid,
        "inject": inject,
        "skipped_critical": skipped,
        "newly_delivered": newly,
        "inject_count": len(inject),
        "skipped_count": len(skipped),
        "ok": True,
        "note": "Governed Memory progressive delivery — supplementary never locked",
    }


def session_delta_status(root: Path, session_id: str) -> dict[str, Any]:
    sid = str(session_id or "").strip()
    if not sid:
        raise SchemaError("session_id is required")
    store = load_session_delta(root)
    sess = store["sessions"].get(sid)
    if sess is None:
        return {"session_id": sid, "exists": False, "ok": False}
    return {
        "session_id": sid,
        "exists": True,
        "delivered_critical": list(sess.get("delivered_critical") or []),
        "ttl_hours": sess.get("ttl_hours"),
        "ok": True,
    }


def entity_context(
    entries: Iterable[Mapping[str, Any]],
    *,
    subject_id: str,
    budget: int = 400,
    saturation: int = DEFAULT_ENTITY_SATURATION,
) -> dict[str, Any]:
    """
    Compile Properties + Observations for one subject_id under a token budget.
    Properties prioritized over open-set facts (Governed Memory saturation ~7).
    """
    sid = str(subject_id or "").strip()
    if not sid:
        raise SchemaError("subject_id is required")
    pool = [
        e
        for e in entries
        if e.get("state") in {"promoted", "contested"}
        and str((e.get("provenance") or {}).get("subject_id") or "") == sid
    ]
    pool.sort(
        key=lambda e: (
            -int(bool((e.get("usage") or {}).get("pinned"))),
            -int((e.get("usage") or {}).get("helpful") or 0),
            str(e.get("id")),
        )
    )
    pool = pool[: max(1, int(saturation))]
    properties: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    used = 0
    for e in pool:
        dual = dual_project(e)
        props = dual["typed_properties"]
        prop_cost = max(1, len(str(props).split()))
        if used + prop_cost <= budget:
            properties.append({"id": e.get("id"), "properties": props})
            used += prop_cost
        for fact in dual["atomic_facts"]:
            cost = max(1, len(str(fact.get("text") or "").split()))
            if used + cost > budget:
                break
            observations.append(
                {"id": e.get("id"), "text": fact.get("text"), "kind": "observation"}
            )
            used += cost
    return {
        "subject_id": sid,
        "properties": properties,
        "observations": observations,
        "entry_count": len(pool),
        "used": used,
        "budget": budget,
        "saturation": saturation,
        "ok": True,
        "note": "Governed Memory entity_context — properties first; saturation cap",
    }


def entity_leak_probe(
    hits: Sequence[Mapping[str, Any]],
    *,
    subject_id: str,
    entries: Sequence[Mapping[str, Any]] | None = None,
    prefilter: bool = True,
) -> dict[str, Any]:
    """
    Assert retrieval hits are entity-scoped (subject_id). Cross-entity = leak.

    When prefilter=True (Governed Memory key filter), foreign subjects are
    dropped before the leak assert and reported as filtered_out.
    """
    sid = str(subject_id or "").strip()
    if not sid:
        raise SchemaError("subject_id is required")
    by_id = {str(e.get("id")): e for e in (entries or [])}
    working = list(hits)
    filtered_out: list[dict[str, Any]] = []
    if prefilter:
        kept: list[Mapping[str, Any]] = []
        for h in working:
            eid = str(h.get("id") or "")
            e = by_id.get(eid) or h
            other = str((e.get("provenance") or {}).get("subject_id") or "")
            if other and other != sid:
                filtered_out.append(
                    {
                        "id": eid,
                        "subject_id": other,
                        "title": e.get("title"),
                    }
                )
            else:
                kept.append(h)
        working = kept
    leaks: list[dict[str, Any]] = []
    ok_ids: list[str] = []
    for h in working:
        eid = str(h.get("id") or "")
        e = by_id.get(eid) or h
        other = str((e.get("provenance") or {}).get("subject_id") or "")
        if other and other != sid:
            leaks.append(
                {
                    "id": eid,
                    "subject_id": other,
                    "title": e.get("title"),
                }
            )
        else:
            ok_ids.append(eid)
    return {
        "subject_id": sid,
        "hit_count": len(hits),
        "ok_count": len(ok_ids),
        "leak_count": len(leaks),
        "leaks": leaks,
        "filtered_out": filtered_out,
        "filtered_count": len(filtered_out),
        "prefilter": prefilter,
        "ok": len(leaks) == 0,
        "note": "Governed Memory entity_leak_probe — key filter, not embedding distance",
    }
