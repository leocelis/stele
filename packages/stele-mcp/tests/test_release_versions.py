"""stele-mcp ships with the stele-core it was tested against."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def _version(package: str) -> str:
    text = (ROOT / "packages" / package / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', text, re.MULTILINE)
    assert match
    return match.group(1)


def test_mcp_pins_core_to_its_own_version() -> None:
    text = (ROOT / "packages/stele-mcp/pyproject.toml").read_text(encoding="utf-8")
    pins = re.findall(r'"stele-core(?:\[[a-z]+\])?([^"]*)"', text)
    assert pins
    assert _version("stele-core") == _version("stele-mcp")
    assert set(pins) == {f"=={_version('stele-core')}"}
