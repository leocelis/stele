"""Portable Agent Memory deepen (stdlib; no LLM / no keyed crypto).

Shaped by Portable Agent Memory (arXiv:2605.11032): five-component memory
model, Merkle-DAG provenance (SHA-256 content digests), capability-scoped
tokens for selective disclosure, injection-resistant rehydrate plan.
Ed25519 / BLAKE3 remain caller-side — core stays unkeyed stdlib digests (C5).
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

COMPONENTS = frozenset(
    {"episodic", "semantic", "procedural", "working", "identity"}
)
CAP_OPS = frozenset(
    {"read", "write", "derive", "redact", "export", "rehydrate"}
)

_LAYER_TO_COMPONENT: dict[str, str] = {
    "goal": "working",
    "issue": "episodic",
    "decision": "semantic",
    "failure_lesson": "episodic",
    "workflow": "procedural",
    "skill_artifact": "procedural",
}


def classify_memory_component(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Map Stele content layer → PAM (E,S,P,W,I) component."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    layer = str(entry.get("layer") or "").strip()
    component = _LAYER_TO_COMPONENT.get(layer, "episodic")
    body = f"{entry.get('title') or ''}\n{entry.get('body') or ''}".lower()
    if "i am" in body or "my preference" in body or "identity:" in body:
        component = "identity"
    elif "working memory" in body or "current goal" in body:
        component = "working"
    return {
        "id": entry.get("id"),
        "component": component,
        "content_layer": layer or None,
        "ok": True,
        "note": "pam classify_memory_component — E/S/P/W/I proxy",
    }


def entry_content_digest(entry: Mapping[str, Any]) -> str:
    """Stable SHA-256 over canonical entry body fields (not journal)."""
    material = {
        "id": entry.get("id"),
        "layer": entry.get("layer"),
        "title": entry.get("title"),
        "body": entry.get("body"),
        "scope": entry.get("scope"),
        "conflict_key": entry.get("conflict_key"),
        "state": entry.get("state"),
        "links": entry.get("links") or [],
    }
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


def build_merkle_dag(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Content-addressed DAG: node = entry digest; edges = LINK kind=entry parents.
    Root = SHA-256 over sorted (id, digest, parents) rows.
    """
    by_id = {str(e.get("id")): e for e in entries if isinstance(e, Mapping)}
    nodes: list[dict[str, Any]] = []
    for eid, e in sorted(by_id.items()):
        parents: list[str] = []
        for lnk in e.get("links") or []:
            if not isinstance(lnk, Mapping):
                continue
            if str(lnk.get("kind") or "") != "entry":
                continue
            ref = str(lnk.get("ref") or "")
            if ref in by_id:
                parents.append(ref)
        digest = entry_content_digest(e)
        nodes.append(
            {
                "id": eid,
                "digest": digest,
                "parents": sorted(set(parents)),
                "component": classify_memory_component(e)["component"],
            }
        )
    root_material = [
        {"id": n["id"], "digest": n["digest"], "parents": n["parents"]}
        for n in nodes
    ]
    root = hashlib.sha256(
        canonical_dumps(root_material).encode("utf-8")
    ).hexdigest()
    return {
        "nodes": nodes,
        "node_count": len(nodes),
        "root": root,
        "ok": True,
        "note": "pam build_merkle_dag — SHA-256 Merkle-DAG proxy (not BLAKE3/Ed25519)",
    }


def verify_merkle_root(
    entries: Sequence[Mapping[str, Any]],
    *,
    expected_root: str,
) -> dict[str, Any]:
    """Recompute Merkle root and compare to expected."""
    expected = str(expected_root or "").strip().lower()
    if not expected or len(expected) != 64:
        raise SchemaError("expected_root must be a 64-char hex digest")
    dag = build_merkle_dag(entries)
    match = dag["root"] == expected
    return {
        "ok": match,
        "match": match,
        "root": dag["root"],
        "expected_root": expected,
        "node_count": dag["node_count"],
        "note": "pam verify_merkle_root — tamper-evident check",
    }


def issue_capability_token(
    *,
    entry_ids: Sequence[str],
    ops: Sequence[str],
    audience: str,
    expires_at: str,
    components: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Issue an unkeyed capability token (digest attestation).

    Caller may wrap with Ed25519 offline — core never holds private keys (C5).
    """
    ids = sorted({str(i) for i in entry_ids if i})
    if not ids:
        raise SchemaError("entry_ids is required")
    op_set = sorted({str(o).strip().lower() for o in ops if o})
    bad = set(op_set) - CAP_OPS
    if bad:
        raise SchemaError(f"unknown ops: {sorted(bad)}")
    if not op_set:
        raise SchemaError("ops is required")
    aud = str(audience or "").strip()
    exp = str(expires_at or "").strip()
    if not aud or not exp:
        raise SchemaError("audience and expires_at are required")
    comps = sorted(
        {str(c).strip().lower() for c in (components or []) if c}
    )
    bad_c = set(comps) - COMPONENTS
    if bad_c:
        raise SchemaError(f"unknown components: {sorted(bad_c)}")
    payload = {
        "entry_ids": ids,
        "ops": op_set,
        "audience": aud,
        "expires_at": exp,
        "components": comps,
    }
    token = hashlib.sha256(canonical_dumps(payload).encode("utf-8")).hexdigest()
    return {
        "token": token,
        "payload": payload,
        "ok": True,
        "note": "pam issue_capability_token — unkeyed digest; sign caller-side",
    }


def check_capability(
    token: str,
    payload: Mapping[str, Any],
    *,
    op: str,
    entry_id: str | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Verify token digests payload and authorizes op (and optional entry)."""
    token = str(token or "").strip().lower()
    op = str(op or "").strip().lower()
    if op not in CAP_OPS:
        raise SchemaError(f"op must be one of {sorted(CAP_OPS)}")
    expected = hashlib.sha256(
        canonical_dumps(dict(payload)).encode("utf-8")
    ).hexdigest()
    if token != expected:
        return {
            "allowed": False,
            "reason": "token_mismatch",
            "ok": True,
            "note": "pam check_capability",
        }
    ops = {str(o) for o in (payload.get("ops") or [])}
    if op not in ops:
        return {
            "allowed": False,
            "reason": "op_not_granted",
            "ok": True,
            "note": "pam check_capability",
        }
    if entry_id:
        allowed_ids = {str(i) for i in (payload.get("entry_ids") or [])}
        if str(entry_id) not in allowed_ids:
            return {
                "allowed": False,
                "reason": "entry_not_in_scope",
                "ok": True,
                "note": "pam check_capability",
            }
    exp = str(payload.get("expires_at") or "")
    if now and exp and now > exp:
        return {
            "allowed": False,
            "reason": "expired",
            "ok": True,
            "note": "pam check_capability",
        }
    return {
        "allowed": True,
        "reason": "ok",
        "ok": True,
        "note": "pam check_capability",
    }


def selective_disclose(
    entries: Sequence[Mapping[str, Any]],
    *,
    entry_ids: Sequence[str],
    include_ancestors: bool = True,
) -> dict[str, Any]:
    """
    Export a subset of entries; optionally close under LINK parents (ancestors).
    """
    want = {str(i) for i in entry_ids if i}
    if not want:
        raise SchemaError("entry_ids is required")
    by_id = {str(e.get("id")): e for e in entries if isinstance(e, Mapping)}
    missing = sorted(want - set(by_id))
    selected: set[str] = set(want & set(by_id))
    if include_ancestors:
        frontier = set(selected)
        while frontier:
            nxt: set[str] = set()
            for eid in frontier:
                e = by_id.get(eid)
                if e is None:
                    continue
                for lnk in e.get("links") or []:
                    if not isinstance(lnk, Mapping):
                        continue
                    if str(lnk.get("kind") or "") != "entry":
                        continue
                    ref = str(lnk.get("ref") or "")
                    if ref in by_id and ref not in selected:
                        selected.add(ref)
                        nxt.add(ref)
            frontier = nxt
    disclosed = []
    for eid in sorted(selected):
        e = by_id[eid]
        disclosed.append(
            {
                "id": eid,
                "title": e.get("title"),
                "component": classify_memory_component(e)["component"],
                "digest": entry_content_digest(e),
                "seed": eid in want,
            }
        )
    dag = build_merkle_dag([by_id[i] for i in selected])
    return {
        "disclosed": disclosed,
        "count": len(disclosed),
        "missing": missing,
        "root": dag["root"],
        "ok": True,
        "note": "pam selective_disclose — subset + ancestor closure",
    }


def rehydrate_safe_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    injection_markers: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Plan injection-resistant rehydration: flag / strip directive markers.
    Report-only — does not mutate SoT.
    """
    markers = tuple(
        injection_markers
        or (
            "ignore prior",
            "ignore previous",
            "exfiltrate",
            "developer mode",
            "system note:",
        )
    )
    rows: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        text = f"{e.get('title') or ''}\n{e.get('body') or ''}".lower()
        hits = [m for m in markers if m in text]
        action = "strip_markers" if hits else "admit"
        rows.append(
            {
                "id": e.get("id"),
                "action": action,
                "markers": hits,
            }
        )
    strip = [r for r in rows if r["action"] == "strip_markers"]
    return {
        "plan": rows,
        "strip_count": len(strip),
        "admit_count": len(rows) - len(strip),
        "ok": True,
        "note": "pam rehydrate_safe_plan — injection-resistant rehydrate proxy",
    }
