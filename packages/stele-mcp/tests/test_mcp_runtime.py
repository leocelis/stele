"""Runtime smoke for stele-mcp — catches mcp 2.x FastMCP breakage.

AST tool-name checks alone cannot see ModuleNotFoundError on
``mcp.server.fastmcp``. This test imports the live server module.
"""

from __future__ import annotations

import importlib.metadata
from importlib.metadata import PackageNotFoundError

import pytest


def test_mcp_sdk_below_v2() -> None:
    """stele-mcp requires FastMCP from mcp 1.x (``mcp>=1.0,<2``)."""
    try:
        ver = importlib.metadata.version("mcp")
    except PackageNotFoundError:  # pragma: no cover
        pytest.fail("mcp package not installed")
    major = int(ver.split(".", 1)[0])
    assert major < 2, (
        f"mcp {ver} breaks stele-mcp (FastMCP moved); pin mcp>=1.0,<2"
    )


def test_stele_mcp_imports_fastmcp() -> None:
    """Boot path used by the ``stele-mcp`` console script."""
    from mcp.server.fastmcp import FastMCP

    assert FastMCP is not None


def test_stele_mcp_server_registers_tools() -> None:
    """Import server and confirm FastMCP tool registry is populated."""
    from stele_mcp.server import mcp

    tools = getattr(mcp, "_tool_manager", None)
    assert tools is not None, "FastMCP tool manager missing"
    registered = getattr(tools, "_tools", {}) or {}
    assert len(registered) >= 26, (
        f"expected core MCP tools registered, got {len(registered)}"
    )
    assert "stele_add" in registered
    assert "stele_search" in registered
    assert "stele_promote" in registered
