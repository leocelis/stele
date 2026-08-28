"""C4 — indexes are derived; rebuild is lossless for retrieval results."""

from __future__ import annotations

import json
from pathlib import Path

from stele_core import Stele
from helpers import TS, base_entry, oracle_evidence


def test_index_rebuild_is_lossless(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "store", store_id="rebuild", now=TS)
    eid = stele.add(
        base_entry(title="Rebuild lesson on cache keys", body="Calendar buckets again."),
        ts=TS,
    )["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)

    before = stele.search("calendar buckets", consumer_scope="project:demo")
    assert len(before) == 1

    stele.store.drop_indexes()
    stele.rebuild_indexes()
    after = stele.search("calendar buckets", consumer_scope="project:demo")

    assert json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)
