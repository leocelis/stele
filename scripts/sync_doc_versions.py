"""Patch version lines in top-level docs from stele-core pyproject.toml."""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "packages/stele-core/pyproject.toml"
VERSION = re.search(r'^version = "([^"]+)"', PYPROJECT.read_text(), re.MULTILINE).group(1)

REPLACEMENTS: list[tuple[pathlib.Path, list[tuple[str, str]]]] = [
    (
        ROOT / "README.md",
        [
            (r"^(\*\*Status: )v[\d.]+(\.\*\*)", f"**Status: v{VERSION}.**"),
        ],
    ),
    (
        ROOT / "docs/PRD.md",
        [
            (r"^\*\*Version:\*\* [\d.]+", f"**Version:** {VERSION}"),
        ],
    ),
    (
        ROOT / "docs/ARCHITECTURE.md",
        [
            (r"^\*\*Version:\*\* [\d.]+", f"**Version:** {VERSION}"),
            (
                r"stele-mcp \(26 named tools\)",
                "stele-mcp-core (35 governed-ledger tools)",
            ),
        ],
    ),
]

for path, subs in REPLACEMENTS:
    text = path.read_text(encoding="utf-8")
    for pattern, repl in subs:
        text = re.sub(pattern, repl, text, count=1, flags=re.MULTILINE)
    path.write_text(text, encoding="utf-8")
    print(f"synced {path.relative_to(ROOT)} → {VERSION}")
