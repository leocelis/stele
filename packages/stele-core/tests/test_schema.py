"""C6 — schema validation and byte-stable round-trip."""

from __future__ import annotations

import pytest

from stele_core.schema import SchemaError, canonical_dumps, validate_entry
from helpers import base_entry


def test_incomplete_entries_rejected() -> None:
    with pytest.raises(SchemaError, match="scope"):
        validate_entry({**base_entry(), "scope": ""})

    bad = base_entry()
    del bad["provenance"]["subject_id"]
    with pytest.raises(SchemaError, match="subject_id"):
        validate_entry(bad)

    bad2 = base_entry()
    del bad2["temporal"]
    with pytest.raises(SchemaError, match="temporal"):
        validate_entry(bad2)

    workflow = base_entry(layer="workflow", title="Deploy steps", body="Run the checklist.")
    with pytest.raises(SchemaError, match="env_assumptions"):
        validate_entry(workflow)

    complete = validate_entry(
        base_entry(
            layer="workflow",
            title="Deploy steps",
            body="Run the checklist.",
            env_assumptions=["linux", "bash"],
        )
    )
    again = validate_entry(complete)
    assert canonical_dumps(complete) == canonical_dumps(again)
    assert complete["id"].startswith("se_")
