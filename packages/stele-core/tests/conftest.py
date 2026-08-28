"""Shared fixtures for stele-core constraint tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from helpers import TS
from stele_core import Stele


@pytest.fixture
def stele(tmp_path: Path) -> Stele:
    return Stele.open(tmp_path / "store", store_id="test", now=TS)
