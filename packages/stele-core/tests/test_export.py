"""C3 — pack export is redacted, versioned, scoped; no top-level trajectories."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stele_core import SchemaError, Stele
from stele_core.export import scan_secrets
from helpers import TS, base_entry, oracle_evidence


def test_pack_is_redacted_versioned_scoped(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "store", store_id="export", now=TS)
    eid = stele.add(
        base_entry(
            title="Exportable insight",
            body="Prefer day-scoped keys. Never put api_key=SECRET123 in lessons.",
        ),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    dest = tmp_path / "pack"
    manifest = stele.export(
        dest,
        scope="project:demo",
        audience="practitioner",
        purpose="demo-pack",
        created_at=TS,
        expiry="2027-01-01T00:00:00Z",
    )

    assert manifest["pack_version"] == 1
    assert manifest["audience_tier"] == "practitioner"
    assert manifest["expiry"] == "2027-01-01T00:00:00Z"
    assert (dest / "manifest.json").exists()
    assert not (dest / "trajectory.json").exists()

    entry_files = list((dest / "entries").glob("*.json"))
    assert len(entry_files) == 1
    body = json.loads(entry_files[0].read_text())["body"]
    assert "SECRET123" not in body or "[REDACTED]" in body
    assert scan_secrets(body) == [] or "[REDACTED]" in body


def test_export_blocks_private_ledger_paths(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "store2", store_id="export2", now=TS)
    with pytest.raises(SchemaError, match="private-source"):
        stele.add(
            base_entry(provenance={
                "agent": "a",
                "task": "t",
                "environment": "e",
                "subject_id": "s",
                "source": "ledger/tenants/private/feedback/x.yaml",
                "written_at": TS,
            }),
            ts=TS,
        )
