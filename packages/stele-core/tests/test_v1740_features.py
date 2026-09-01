"""v17.4: LoRA-Composer + CARE-LoRA."""

from __future__ import annotations

from pathlib import Path

from stele_core import Stele, lco_car_shaped_report

TS = "2026-08-24T12:00:00Z"


def test_lco_car(tmp_path: Path) -> None:
    stele = Stele.open(tmp_path / "s", store_id="v174", now=TS)
    report = lco_car_shaped_report(
        stele, consumer_scope="project:v174", now=TS
    )
    assert report["suite"] == "lco_car_shaped"
    assert report["ok"] is True

    free = stele.lco_free(training_free=False)
    assert free["apply"] is False

    mem = stele.car_mem(activation_saved=False)
    assert mem["apply"] is False
