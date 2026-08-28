"""v0.1.7: stats, timeline, attach, verify_pack, multi-hop links."""

from __future__ import annotations

from pathlib import Path

from helpers import TS, base_entry, oracle_evidence
from stele_core import Stele


def test_stats_timeline_attach(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="dash", now=TS)
    eid = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    digest = stele.attach(b"fixture-bytes", entry_id=eid, actor="ops", ts=TS)["digest"]
    assert len(digest) == 64
    assert stele.store.verify_attachment_digest(digest)

    st = stele.stats(now=TS)
    assert st["total"] == 1
    assert st["by_state"].get("promoted") == 1
    assert st["attachments"] >= 1

    tl = stele.timeline(eid)
    ops = [r["op"] for r in tl]
    assert "ADD" in ops and "PROMOTE" in ops and "LINK" in ops


def test_verify_pack_clean(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="vp", now=TS)
    eid = stele.add(base_entry(), ts=TS)["id"]
    stele.promote(eid, oracle_evidence(), actor="ci", ts=TS)
    pack = tmp_path / "pack"
    stele.export(
        pack,
        scope="project:demo",
        audience="expert",
        purpose="verify",
        created_at=TS,
        expiry="2027-01-01T00:00:00Z",
    )
    report = stele.verify_pack(pack)
    assert report["ok"] is True
    assert report["entry_count"] >= 1


def test_follow_link_depth_two(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="hop", now=TS)
    root = stele.add(
        base_entry(
            title="Root cache calendar buckets lesson",
            body="Root day-scoped cache keys insight.",
        ),
        ts=TS,
    )["id"]
    mid = stele.add(
        base_entry(
            layer="goal",
            title="Mid hop midnight safety",
            body="Preserve midnight rollover safety goal.",
        ),
        ts=TS,
    )["id"]
    leaf = stele.add(
        base_entry(
            layer="decision",
            title="Leaf hop reject shared keys",
            body="Decision: never share keys across days.",
            rejected_options=["share keys overnight"],
        ),
        ts=TS,
    )["id"]
    for eid, issuer in ((root, "r"), (mid, "m"), (leaf, "l")):
        stele.promote(eid, oracle_evidence(issuer=issuer), actor=issuer, ts=TS)
    stele.link(root, kind="entry", ref=mid, actor="ops", ts=TS)
    stele.link(mid, kind="entry", ref=leaf, actor="ops", ts=TS)

    one = stele.search(
        "calendar buckets",
        consumer_scope="project:demo",
        follow_links=True,
        follow_link_depth=1,
    )
    ids1 = {s["id"] for s in one}
    assert root in ids1 and mid in ids1
    assert leaf not in ids1

    two = stele.search(
        "calendar buckets",
        consumer_scope="project:demo",
        follow_links=True,
        follow_link_depth=2,
    )
    ids2 = {s["id"] for s in two}
    assert leaf in ids2
