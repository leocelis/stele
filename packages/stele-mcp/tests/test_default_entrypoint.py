"""Default stele-mcp console script must expose core-only surface."""

from __future__ import annotations

from stele_mcp.server import _CORE_TOOL_NAMES, create_core_app


def test_default_surface_matches_core_allowlist() -> None:
    core = create_core_app()
    names = {t.name for t in core._tool_manager.list_tools()}
    assert names == set(_CORE_TOOL_NAMES)
    assert len(names) == 35
