"""Entry schema, canonical serialization, and validation (intent C6)."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

SCHEMA_VERSION = 1

LAYERS = frozenset(
    {"goal", "issue", "decision", "failure_lesson", "workflow", "skill_artifact"}
)
STATES = frozenset(
    {
        "quarantined",
        "promoted",
        "superseded",
        "expired",
        "contested",
        "revoked",
        "archived",
    }
)
MEMORY_ROLES = frozenset({"evidence", "claim", "decision"})
EVIDENCE_TYPES = frozenset(
    {"test_result", "env_feedback", "independent_judge", "human_signoff"}
)
VERDICTS = frozenset({"supports", "refutes", "mixed"})
DOMAIN_DEPTHS = frozenset({"expert", "practitioner", "adjacent", "novice"})
LINK_KINDS = frozenset({"artifact", "test", "entry", "source"})
OUTCOME_KINDS = frozenset({"helpful", "harmful", "ignored"})

_SCOPE_RE = re.compile(r"^(universal|domain:[A-Za-z0-9_.-]+|project:[A-Za-z0-9_.-]+)$")
_ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)


def normalize_usage(raw: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Usage / outcome counters (reinforce on use; FF-8 freshness)."""
    raw = raw or {}
    out: dict[str, Any] = {
        "helpful": int(raw.get("helpful") or 0),
        "harmful": int(raw.get("harmful") or 0),
        "ignored": int(raw.get("ignored") or 0),
        "pinned": bool(raw.get("pinned") or False),
    }
    if out["helpful"] < 0 or out["harmful"] < 0 or out["ignored"] < 0:
        raise SchemaError("usage counters must be >= 0")
    if raw.get("last_outcome"):
        lo = str(raw["last_outcome"])
        if lo not in OUTCOME_KINDS:
            raise SchemaError(f"usage.last_outcome must be one of {sorted(OUTCOME_KINDS)}")
        out["last_outcome"] = lo
    if raw.get("last_outcome_at"):
        out["last_outcome_at"] = _require_iso(
            str(raw["last_outcome_at"]), "usage.last_outcome_at"
        )
    return out


class SchemaError(ValueError):
    """Raised when an entry or evidence record fails structural validation."""


def canonical_dumps(obj: Any) -> str:
    """Byte-stable JSON: UTF-8, sorted keys, LF endings, no float money/scores."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def canonical_loads(text: str) -> Any:
    return json.loads(text)


def entry_content_for_id(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Fields that participate in content-derived identity (exclude id/state)."""
    skip = {"id", "state", "evidence"}
    return {k: entry[k] for k in sorted(entry.keys()) if k not in skip}


def derive_entry_id(entry: Mapping[str, Any]) -> str:
    payload = canonical_dumps(entry_content_for_id(entry)).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()[:16]
    return f"se_{digest}"


def _require_str(obj: Mapping[str, Any], key: str) -> str:
    if key not in obj or not isinstance(obj[key], str) or not obj[key].strip():
        raise SchemaError(f"missing or empty string field: {key}")
    return obj[key]


def _require_iso(value: str, field: str) -> str:
    if not _ISO_RE.match(value):
        raise SchemaError(f"{field} must be ISO-8601 UTC-ish timestamp, got {value!r}")
    return value


def validate_scope(scope: str) -> str:
    if not _SCOPE_RE.match(scope):
        raise SchemaError(
            f"scope must be universal | domain:<name> | project:<name>, got {scope!r}"
        )
    return scope


def validate_evidence(record: Mapping[str, Any], *, writer_agent: str | None = None) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        raise SchemaError("evidence record must be an object")
    etype = record.get("type")
    if etype not in EVIDENCE_TYPES:
        raise SchemaError(f"evidence.type must be one of {sorted(EVIDENCE_TYPES)}")
    issuer = _require_str(record, "issuer")
    if writer_agent is not None and etype != "human_signoff" and issuer == writer_agent:
        raise SchemaError("self-issued evidence cannot promote (issuer == provenance.agent)")
    verdict = record.get("verdict")
    if verdict not in VERDICTS:
        raise SchemaError(f"evidence.verdict must be one of {sorted(VERDICTS)}")
    out: dict[str, Any] = {
        "type": etype,
        "issuer": issuer,
        "ref": _require_str(record, "ref"),
        "observed_at": _require_iso(_require_str(record, "observed_at"), "observed_at"),
        "verdict": verdict,
    }
    if "digest" in record and record["digest"] is not None:
        if not isinstance(record["digest"], str) or len(record["digest"]) < 8:
            raise SchemaError("evidence.digest must be a hex digest string")
        out["digest"] = record["digest"]
    if etype == "test_result":
        out["command"] = _require_str(record, "command")
        if "exit_status" not in record or not isinstance(record["exit_status"], int):
            raise SchemaError("test_result evidence requires integer exit_status")
        out["exit_status"] = record["exit_status"]
    return out


def validate_link(link: Mapping[str, Any]) -> dict[str, Any]:
    kind = link.get("kind")
    if kind not in LINK_KINDS:
        raise SchemaError(f"link.kind must be one of {sorted(LINK_KINDS)}")
    out: dict[str, Any] = {"kind": kind, "ref": _require_str(link, "ref")}
    if "digest" in link and link["digest"] is not None:
        out["digest"] = str(link["digest"])
    return out


def validate_entry(
    raw: Mapping[str, Any],
    *,
    require_complete: bool = True,
    allow_state: str | None = None,
) -> dict[str, Any]:
    """Validate and normalize an entry. Incomplete entries raise SchemaError."""
    if not isinstance(raw, Mapping):
        raise SchemaError("entry must be an object")

    layer = raw.get("layer")
    if layer not in LAYERS:
        raise SchemaError(f"layer must be one of {sorted(LAYERS)}")

    title = _require_str(raw, "title")
    body = _require_str(raw, "body")
    scope = validate_scope(_require_str(raw, "scope"))

    temporal = raw.get("temporal")
    if not isinstance(temporal, Mapping):
        raise SchemaError("temporal object is required")
    valid_from = _require_iso(_require_str(temporal, "valid_from"), "temporal.valid_from")
    last_verified = _require_iso(
        _require_str(temporal, "last_verified"), "temporal.last_verified"
    )
    temporal_out: dict[str, Any] = {
        "valid_from": valid_from,
        "last_verified": last_verified,
    }
    if temporal.get("expiry"):
        temporal_out["expiry"] = _require_iso(str(temporal["expiry"]), "temporal.expiry")
    if temporal.get("superseded_by"):
        temporal_out["superseded_by"] = str(temporal["superseded_by"])
    if temporal.get("superseded_at"):
        temporal_out["superseded_at"] = _require_iso(
            str(temporal["superseded_at"]), "temporal.superseded_at"
        )
    if temporal.get("revoked_at"):
        temporal_out["revoked_at"] = _require_iso(
            str(temporal["revoked_at"]), "temporal.revoked_at"
        )
    if temporal.get("revoked_key"):
        temporal_out["revoked_key"] = str(temporal["revoked_key"])

    provenance = raw.get("provenance")
    if not isinstance(provenance, Mapping):
        raise SchemaError("provenance object is required")
    for key in ("agent", "task", "environment", "subject_id", "source", "written_at"):
        if key not in provenance or not isinstance(provenance[key], str) or not provenance[key]:
            if require_complete:
                raise SchemaError(f"provenance.{key} is required")
    provenance_out: dict[str, Any] = {
        "agent": str(provenance["agent"]),
        "task": str(provenance["task"]),
        "environment": str(provenance["environment"]),
        "subject_id": str(provenance["subject_id"]),
        "source": str(provenance["source"]),
        "written_at": _require_iso(str(provenance["written_at"]), "provenance.written_at"),
    }
    if provenance.get("model_id"):
        provenance_out["model_id"] = str(provenance["model_id"])

    entry: dict[str, Any] = {
        "schema_version": int(raw.get("schema_version", SCHEMA_VERSION)),
        "layer": layer,
        "title": title,
        "body": body,
        "scope": scope,
        "temporal": temporal_out,
        "provenance": provenance_out,
        "links": [],
        "evidence": [],
    }

    if layer in {"workflow", "skill_artifact"}:
        env = raw.get("env_assumptions")
        if not isinstance(env, list) or not env:
            raise SchemaError(f"{layer} entries require non-empty env_assumptions")
        entry["env_assumptions"] = [str(x) for x in env]

    if layer in {"issue", "decision"} and raw.get("rejected_options") is not None:
        opts = raw["rejected_options"]
        if not isinstance(opts, list):
            raise SchemaError("rejected_options must be a list")
        entry["rejected_options"] = opts

    if raw.get("assessment") and isinstance(raw["assessment"], Mapping):
        depth = raw["assessment"].get("domain_depth")
        if depth is not None and depth not in DOMAIN_DEPTHS:
            raise SchemaError(f"assessment.domain_depth must be one of {sorted(DOMAIN_DEPTHS)}")
        entry["assessment"] = {"domain_depth": depth} if depth else {}

    if raw.get("receipt_projection") is not None:
        if not isinstance(raw["receipt_projection"], Mapping):
            raise SchemaError("receipt_projection must be an object")
        entry["receipt_projection"] = dict(raw["receipt_projection"])

    if raw.get("contested_with") is not None:
        peers = raw["contested_with"]
        if not isinstance(peers, list) or not all(isinstance(x, str) for x in peers):
            raise SchemaError("contested_with must be a list of entry id strings")
        entry["contested_with"] = sorted(set(peers))

    if raw.get("usage") is not None:
        entry["usage"] = normalize_usage(raw["usage"])

    if raw.get("conflict_key") is not None:
        from stele_core.lifecycle import parse_conflict_key

        entry["conflict_key"] = parse_conflict_key(str(raw["conflict_key"]))

    if raw.get("cue_tags") is not None:
        cues = raw["cue_tags"]
        if not isinstance(cues, list) or not all(isinstance(x, str) and x.strip() for x in cues):
            raise SchemaError("cue_tags must be a list of non-empty strings")
        if len(cues) > 32:
            raise SchemaError("cue_tags max 32 tags")
        cleaned = []
        for c in cues:
            tag = str(c).strip().lower()
            if len(tag) > 64:
                raise SchemaError("cue_tags entries must be ≤64 chars")
            if tag not in cleaned:
                cleaned.append(tag)
        entry["cue_tags"] = cleaned

    if raw.get("memory_role") is not None:
        role = str(raw["memory_role"]).strip().lower()
        if role not in MEMORY_ROLES:
            raise SchemaError(f"memory_role must be one of {sorted(MEMORY_ROLES)}")
        entry["memory_role"] = role

    links = raw.get("links") or []
    if not isinstance(links, list):
        raise SchemaError("links must be a list")
    entry["links"] = [validate_link(x) for x in links]

    evidence = raw.get("evidence") or []
    if not isinstance(evidence, list):
        raise SchemaError("evidence must be a list")
    entry["evidence"] = [
        validate_evidence(x, writer_agent=None) for x in evidence
    ]

    state = allow_state or raw.get("state") or "quarantined"
    if state not in STATES:
        raise SchemaError(f"state must be one of {sorted(STATES)}")
    entry["state"] = state

    eid = raw.get("id") or derive_entry_id(entry)
    if not isinstance(eid, str) or not eid.startswith("se_"):
        raise SchemaError("id must be a se_<hex16> content-derived identifier")
    entry["id"] = eid
    return entry


def private_source_fields_present(obj: Mapping[str, Any]) -> list[str]:
    """Detect private operator paths that must never enter public Stele payloads."""
    banned_substrings = (
        "ledger/tenants",
        "tenants/private",
        "workspace/ledger",
        "inventory_index",
        "/private/feedback/",
        "private-receipt-root",
    )
    blob = canonical_dumps(dict(obj))
    hits = [s for s in banned_substrings if s in blob]
    return hits
