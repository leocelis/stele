"""JSON Schema 2020-12 export for Stele entries (OP-6 / memorywire interop)."""

from __future__ import annotations

from typing import Any

from stele_core.schema import (
    DOMAIN_DEPTHS,
    EVIDENCE_TYPES,
    LAYERS,
    LINK_KINDS,
    OUTCOME_KINDS,
    SCHEMA_VERSION,
    STATES,
    VERDICTS,
)


def entry_json_schema() -> dict[str, Any]:
    """Machine-readable entry contract — no runtime deps; JSON Schema Draft 2020-12."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "urn:stele:schema:entry:v1",
        "title": "SteleEntry",
        "description": "Governed experiential-memory ledger entry (Stele schema_version "
        f"{SCHEMA_VERSION}).",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "layer",
            "title",
            "body",
            "scope",
            "temporal",
            "provenance",
            "state",
        ],
        "properties": {
            "id": {
                "type": "string",
                "pattern": "^se_[0-9a-f]{16}$",
                "description": "Content-derived id (se_ + first 16 hex of sha256).",
            },
            "schema_version": {"type": "integer", "const": SCHEMA_VERSION},
            "layer": {"type": "string", "enum": sorted(LAYERS)},
            "title": {"type": "string", "minLength": 1},
            "body": {
                "type": "string",
                "minLength": 1,
                "description": "Distilled Insight — not a raw transcript (FF-2).",
            },
            "rejected_options": {
                "type": "array",
                "items": {"type": "string"},
                "description": "IBIS rejected alternatives (FF-7).",
            },
            "scope": {
                "type": "string",
                "pattern": "^(universal|domain:[A-Za-z0-9_.-]+|project:[A-Za-z0-9_.-]+)$",
            },
            "env_assumptions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Required non-empty for workflow/skill_artifact (FF-4).",
            },
            "temporal": {
                "type": "object",
                "required": ["valid_from", "last_verified"],
                "additionalProperties": False,
                "properties": {
                    "valid_from": {"type": "string", "format": "date-time"},
                    "last_verified": {"type": "string", "format": "date-time"},
                    "expiry": {"type": ["string", "null"], "format": "date-time"},
                    "superseded_by": {"type": ["string", "null"]},
                    "superseded_at": {"type": ["string", "null"], "format": "date-time"},
                    "revoked_at": {"type": ["string", "null"], "format": "date-time"},
                    "revoked_key": {"type": ["string", "null"]},
                },
            },
            "conflict_key": {
                "type": "string",
                "maxLength": 200,
                "description": "TEPA-shaped precedent key for keyed revoke (optional).",
            },
            "cue_tags": {
                "type": "array",
                "maxItems": 32,
                "items": {"type": "string", "minLength": 1, "maxLength": 64},
                "description": "Associative cue tags for retrieval (optional).",
            },
            "memory_role": {
                "type": "string",
                "enum": ["evidence", "claim", "decision"],
                "description": "MemIR-shaped typed role (optional; layer default if omitted).",
            },
            "provenance": {
                "type": "object",
                "required": [
                    "agent",
                    "task",
                    "environment",
                    "subject_id",
                    "source",
                    "written_at",
                ],
                "additionalProperties": False,
                "properties": {
                    "agent": {"type": "string", "minLength": 1},
                    "task": {"type": "string", "minLength": 1},
                    "environment": {"type": "string", "minLength": 1},
                    "subject_id": {"type": "string", "minLength": 1},
                    "source": {"type": "string", "minLength": 1},
                    "written_at": {"type": "string", "format": "date-time"},
                    "model_id": {"type": "string"},
                },
            },
            "assessment": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "domain_depth": {"type": "string", "enum": sorted(DOMAIN_DEPTHS)},
                },
            },
            "receipt_projection": {"type": "object"},
            "evidence": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["type", "issuer", "ref", "observed_at", "verdict"],
                    "properties": {
                        "type": {"type": "string", "enum": sorted(EVIDENCE_TYPES)},
                        "issuer": {"type": "string"},
                        "ref": {"type": "string"},
                        "observed_at": {"type": "string", "format": "date-time"},
                        "verdict": {"type": "string", "enum": sorted(VERDICTS)},
                        "digest": {"type": "string"},
                        "command": {"type": "string"},
                        "exit_status": {"type": "integer"},
                    },
                },
            },
            "links": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["kind", "ref"],
                    "properties": {
                        "kind": {"type": "string", "enum": sorted(LINK_KINDS)},
                        "ref": {"type": "string"},
                        "digest": {"type": "string"},
                    },
                },
            },
            "contested_with": {"type": "array", "items": {"type": "string"}},
            "usage": {
                "type": "object",
                "properties": {
                    "helpful": {"type": "integer", "minimum": 0},
                    "harmful": {"type": "integer", "minimum": 0},
                    "ignored": {"type": "integer", "minimum": 0},
                    "pinned": {"type": "boolean"},
                    "last_outcome": {"type": "string", "enum": sorted(OUTCOME_KINDS)},
                    "last_outcome_at": {"type": "string", "format": "date-time"},
                },
            },
            "state": {"type": "string", "enum": sorted(STATES)},
        },
    }
