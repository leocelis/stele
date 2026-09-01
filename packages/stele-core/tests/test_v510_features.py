"""v5.1: PAM Merkle/capability/disclose + CapSeal action handles."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, pam_capseal_shaped_report

TS = "2026-08-22T23:00:00Z"


def test_pam_capseal(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v51", now=TS)
    report = pam_capseal_shaped_report(
        stele, consumer_scope="project:v51", now=TS
    )
    assert report["suite"] == "pam_capseal_shaped"
    assert report["ok"] is True

    cap = stele.issue_action_capability(
        intent="list invoices",
        method="http_get",
        host="billing.example.com",
        session_id="s1",
        expires_at="2099-01-01T00:00:00Z",
    )
    assert (
        stele.capability_export_probe(cap["handle"], cap["payload"])[
            "export_allowed"
        ]
        is False
    )
