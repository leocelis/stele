"""Core vs full MCP surface — governed-ledger allowlist must stay coherent."""

from __future__ import annotations

import pytest

from stele_mcp.server import _CORE_TOOL_NAMES, create_app, create_core_app


def test_core_app_exposes_only_allowlisted_tools() -> None:
    full = create_app()
    core = create_core_app()
    full_names = {t.name for t in full._tool_manager.list_tools()}
    core_names = {t.name for t in core._tool_manager.list_tools()}

    assert core_names == set(_CORE_TOOL_NAMES)
    assert core_names.issubset(full_names)
    assert len(full_names) > len(core_names)
    assert "stele_doctor" in core_names
    assert "stele_add" in core_names
    # PEFT research tools stay on full only
    assert "stele_mef_loop_plan" in full_names
    assert "stele_mef_loop_plan" not in core_names


def test_core_allowlist_names_are_registered_on_full() -> None:
    full_names = {t.name for t in create_app()._tool_manager.list_tools()}
    missing = sorted(set(_CORE_TOOL_NAMES) - full_names)
    assert missing == [], f"core allowlist references missing tools: {missing}"


def test_create_core_app_raises_on_stale_allowlist(monkeypatch) -> None:
    """A `_CORE_TOOL_NAMES` entry that doesn't exist on `mcp` must fail loudly,
    not silently shrink the exposed core surface."""
    import stele_mcp.server as server_mod

    monkeypatch.setattr(
        server_mod,
        "_CORE_TOOL_NAMES",
        frozenset(server_mod._CORE_TOOL_NAMES | {"stele_this_tool_does_not_exist"}),
    )
    with pytest.raises(RuntimeError, match="stele_this_tool_does_not_exist"):
        server_mod.create_core_app()
