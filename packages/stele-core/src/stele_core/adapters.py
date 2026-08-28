"""Caller-supplied protocols and operator receipt projection (C1, C8)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

from stele_core.schema import SchemaError, private_source_fields_present, validate_entry


@runtime_checkable
class Embedder(Protocol):
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Return one vector per text. Caller-supplied; core never imports vendors."""


@runtime_checkable
class OracleAdapter(Protocol):
    def emit_evidence(self, entry_id: str) -> Sequence[Mapping[str, Any]]:
        """Produce evidence records outside Stele; core only validates structure."""


@runtime_checkable
class SearchBackend(Protocol):
    def search(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int,
        as_of: str | None = None,
        include_contested: bool = False,
        scope_override: Sequence[str] | None = None,
        consumer_domain: str | None = None,
        consumer_env: Sequence[str] | None = None,
        stale_policy: str = "flag",
        consumer_model_id: str | None = None,
        model_policy: str = "flag",
        follow_links: bool = False,
    ) -> list[dict[str, Any]]:
        ...


def project_receipt(receipt: Mapping[str, Any], *, written_at: str) -> dict[str, Any]:
    """
    Map one selected, redacted operator receipt into an ADD payload.

    Preserves expected / detection / diagnosis / change / outcome / resolution / trace
    as distinct concerns. Never accepts private tenant paths.
    """
    hits = private_source_fields_present(receipt)
    if hits:
        raise SchemaError(
            f"private-source fields forbidden in receipt projection: {hits}"
        )

    # Prefer diagnosis layer when present; else detection as issue.
    if receipt.get("diagnosis"):
        layer = "failure_lesson"
        title = str(receipt.get("diagnosis_title") or receipt["diagnosis"])[:120]
        body = str(receipt["diagnosis"])
    elif receipt.get("detection"):
        layer = "issue"
        title = str(receipt.get("detection_title") or receipt["detection"])[:120]
        body = str(receipt["detection"])
    elif receipt.get("expected"):
        layer = "goal"
        title = str(receipt.get("expected_title") or receipt["expected"])[:120]
        body = str(receipt["expected"])
    else:
        raise SchemaError("receipt needs expected, detection, or diagnosis content")

    change = receipt.get("change_tried")
    if change and layer == "failure_lesson":
        # Keep diagnosis distinct; attach change as rejected/accepted context in body.
        body = f"{body}\n\nChange tried: {change}"

    agent = str(receipt.get("agent") or "receipt-adapter")
    entry: dict[str, Any] = {
        "layer": layer,
        "title": title,
        "body": body,
        "scope": str(receipt.get("scope") or "project:receipt"),
        "temporal": {
            "valid_from": written_at,
            "last_verified": written_at,
        },
        "provenance": {
            "agent": agent,
            "task": str(receipt.get("task") or "receipt-import"),
            "environment": str(receipt.get("environment") or "adapter"),
            "subject_id": str(receipt.get("subject_id") or "unknown"),
            "source": str(receipt.get("source") or "receipt:redacted"),
            "written_at": written_at,
        },
        "links": list(receipt.get("links") or []),
        "receipt_projection": {
            "expected": receipt.get("expected"),
            "detection": receipt.get("detection"),
            "diagnosis": receipt.get("diagnosis"),
            "change_tried": receipt.get("change_tried"),
            "outcome": receipt.get("outcome"),
            "code_regression": bool(receipt.get("code_regression", False)),
        },
    }
    if receipt.get("model_id"):
        entry["provenance"]["model_id"] = str(receipt["model_id"])
    if receipt.get("domain_depth"):
        entry["assessment"] = {"domain_depth": receipt["domain_depth"]}

    # Structural validate before return so ADD never sees a partial projection.
    return validate_entry(entry)


def migration_entry(
    raw: Mapping[str, Any],
    *,
    written_at: str,
    project: str,
    source_pointer: str,
) -> dict[str, Any]:
    """
    TECH_SPEC §8.3 migration producer: selected/redacted source → quarantined payload.

    Sets provenance.agent='migration'. Caller must still pass oracle evidence to promote.
    """
    hits = private_source_fields_present(raw)
    if hits:
        raise SchemaError(f"private-source fields forbidden in migration: {hits}")
    if private_source_fields_present({"source": source_pointer}):
        raise SchemaError("migration source_pointer must be redacted (no private paths)")

    entry = dict(raw)
    entry.setdefault("scope", f"project:{project}")
    entry["temporal"] = entry.get("temporal") or {
        "valid_from": written_at,
        "last_verified": written_at,
    }
    prov = dict(entry.get("provenance") or {})
    prov.update(
        {
            "agent": "migration",
            "task": prov.get("task") or "seed-migration",
            "environment": prov.get("environment") or "migration",
            "subject_id": prov.get("subject_id") or f"mig-{project}",
            "source": source_pointer,
            "written_at": written_at,
        }
    )
    entry["provenance"] = prov
    return validate_entry(entry)


def judgment_entry(
    judgment: Mapping[str, Any],
    *,
    written_at: str,
) -> dict[str, Any]:
    """
    Wire-shape codified judgment → ADD payload (TECH_SPEC §8.3).

    Accepts a redacted, already-codified judgment dict. Stele never imports foreign frameworks;
    the caller (or glue) supplies this shape over the protocol.
    """
    hits = private_source_fields_present(judgment)
    if hits:
        raise SchemaError(f"private-source fields forbidden in judgment: {hits}")

    title = str(judgment.get("title") or "").strip()
    body = str(judgment.get("body") or judgment.get("correction") or "").strip()
    if not title or not body:
        raise SchemaError("judgment requires title and body|correction")

    layer = str(judgment.get("layer") or "decision")
    if layer not in {"decision", "failure_lesson", "issue"}:
        raise SchemaError("judgment layer must be decision, failure_lesson, or issue")

    entry: dict[str, Any] = {
        "layer": layer,
        "title": title[:120],
        "body": body,
        "scope": str(judgment.get("scope") or "project:judgment"),
        "temporal": {
            "valid_from": written_at,
            "last_verified": written_at,
        },
        "provenance": {
            "agent": str(judgment.get("agent") or "judgment-adapter"),
            "task": str(judgment.get("task") or "intent-correction"),
            "environment": str(judgment.get("environment") or "adapter"),
            "subject_id": str(judgment.get("subject_id") or "judgment"),
            "source": str(judgment.get("source") or "judgment:redacted"),
            "written_at": written_at,
        },
        "links": list(judgment.get("links") or []),
    }
    if judgment.get("rejected_options") is not None:
        entry["rejected_options"] = list(judgment["rejected_options"])
    if judgment.get("model_id"):
        entry["provenance"]["model_id"] = str(judgment["model_id"])
    if judgment.get("domain_depth"):
        entry["assessment"] = {"domain_depth": judgment["domain_depth"]}
    return validate_entry(entry)


_LAYER_TO_MEMORYWIRE_TYPE = {
    "goal": "semantic",
    "issue": "episodic",
    "decision": "semantic",
    "failure_lesson": "episodic",
    "workflow": "procedural",
    "skill_artifact": "procedural",
}


def to_memorywire_remember(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    Project a Stele entry to a memorywire-shaped `remember` payload (arXiv:2606.01138).

    Stele remains the governed SoT. This is a redacted projection helper — zero
    dependency on the memorywire package (C1). Callers that speak memorywire use
    this dict as the wire body; they do not import Stele internals into memorywire.
    """
    hits = private_source_fields_present(entry)
    if hits:
        raise SchemaError(f"private-source fields forbidden in memorywire projection: {hits}")
    layer = str(entry.get("layer") or "")
    mem_type = _LAYER_TO_MEMORYWIRE_TYPE.get(layer, "episodic")
    temporal = entry.get("temporal") or {}
    provenance = entry.get("provenance") or {}
    return {
        "op": "remember",
        "type": mem_type,
        "content": str(entry.get("body") or ""),
        "metadata": {
            "stele_id": entry.get("id"),
            "title": entry.get("title"),
            "layer": layer,
            "scope": entry.get("scope"),
            "state": entry.get("state"),
            "subject_id": provenance.get("subject_id"),
            "valid_from": temporal.get("valid_from"),
            "last_verified": temporal.get("last_verified"),
            "source": "stele",
            "schema_version": entry.get("schema_version"),
        },
    }


def from_memorywire_recall_hits(
    hits: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """
    Normalize memorywire-shaped recall hits into Stele-friendly slice stubs.

    Does not invent Stele ids. If `metadata.stele_id` is present, it is preserved;
    otherwise the stub is marked `foreign: true` for caller routing.
    """
    out: list[dict[str, Any]] = []
    for hit in hits:
        meta = dict(hit.get("metadata") or {})
        stele_id = meta.get("stele_id")
        stub: dict[str, Any] = {
            "title": meta.get("title") or "",
            "body": str(hit.get("content") or hit.get("text") or ""),
            "scope": meta.get("scope"),
            "layer": meta.get("layer"),
            "score": hit.get("score"),
            "source": "memorywire",
        }
        if stele_id:
            stub["id"] = stele_id
            stub["foreign"] = False
        else:
            stub["foreign"] = True
        out.append(stub)
    return out
