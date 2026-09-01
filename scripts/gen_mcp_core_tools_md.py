"""Generate docs/MCP_CORE_TOOLS.md from _CORE_TOOL_NAMES."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages/stele-mcp/src"))

from stele_mcp.server import _CORE_TOOL_NAMES

OUT = ROOT / "docs" / "MCP_CORE_TOOLS.md"
lines = ["# MCP core tools (35)\n", "Auto-generated — do not edit by hand.\n\n"]
for name in sorted(_CORE_TOOL_NAMES):
    lines.append(f"- `{name}`\n")
OUT.write_text("".join(lines), encoding="utf-8")
print(f"wrote {OUT}")
