"""C1 / C5 — core purity: stdlib-only imports, no network/LLM on write path."""

from __future__ import annotations

import ast
import socket
import sys
from pathlib import Path

from stele_core import Stele
from helpers import TS, base_entry, oracle_evidence

CORE_SRC = Path(__file__).resolve().parents[1] / "src" / "stele_core"

# Third-party / vendor roots that must never appear in stele-core.
# (DB drivers, LLM SDKs, HTTP clients — not an allowlist of other products.)
FORBIDDEN_MODULES = {
    "openai",
    "anthropic",
    "httpx",
    "requests",
    "urllib3",
    "aiohttp",
    "psycopg2",
    "pymongo",
    "pymysql",
    "sqlalchemy",
    "redis",
}


def test_core_static_import_scan() -> None:
    """Every import in stele-core is stdlib or stele_core itself.

    Exception: ``mysql_store.py`` is the optional ``[mysql]`` extra (hosted SoT).
    It must stay out of the default install path; purity of the file SoT is unchanged.
    """
    stdlib = set(sys.stdlib_module_names)
    hits: list[str] = []
    for path in CORE_SRC.rglob("*.py"):
        if path.name == "mysql_store.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module.split(".")[0]]
            for root in names:
                if root in ("stele_core",) or root.startswith("stele_core"):
                    continue
                if root in FORBIDDEN_MODULES:
                    hits.append(f"{path.name}: forbidden {root}")
                elif root not in stdlib and root not in {"__future__"}:
                    # relative imports have module None / leading dots — skip empty
                    if root:
                        hits.append(f"{path.name}: non-stdlib import {root}")
    assert hits == [], hits


def test_mysql_store_is_optional_extra_not_imported_by_default() -> None:
    """File SoT path must not pull PyMySQL; only explicit mysql_store import may."""
    import stele_core.store as store_mod

    src = (CORE_SRC / "store.py").read_text(encoding="utf-8")
    assert "pymysql" not in src
    assert "mysql_store" not in src
    assert hasattr(store_mod, "SteleStore")



class CountingEmbedder:
    def __init__(self) -> None:
        self.calls = 0

    def embed(self, texts):  # type: ignore[no-untyped-def]
        self.calls += 1
        return [[0.0, 1.0] for _ in texts]


def test_write_path_zero_llm_zero_network(tmp_path: Path) -> None:
    embedder = CountingEmbedder()
    stele = Stele.open(tmp_path / "store", store_id="pure", embedder=embedder, now=TS)

    real_socket = socket.socket

    def blocked(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("network socket opened on write path")

    socket.socket = blocked  # type: ignore[assignment]
    try:
        stele.add(base_entry(), ts=TS)
        eid = stele.add(base_entry(title="Second lesson about buckets"), ts=TS)["id"]
        stele.promote(eid, oracle_evidence(), actor="oracle", ts=TS)
    finally:
        socket.socket = real_socket  # type: ignore[assignment]

    assert embedder.calls == 0
