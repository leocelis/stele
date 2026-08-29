"""HTTP shell smoke: health + auth on deploy/wsgi.py (file store, no DSN)."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest
from starlette.testclient import TestClient

REPO = Path(__file__).resolve().parents[3]


def _load_wsgi():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("stele_deploy_wsgi", REPO / "deploy" / "wsgi.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_health_unauthenticated(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STELE_STORE", str(tmp_path / "scratch"))
    monkeypatch.delenv("STELE_STORE_DSN", raising=False)
    monkeypatch.setenv("STELE_AUTH_DISABLED", "true")
    monkeypatch.setenv("STELE_API_KEYS", "")

    import stele_mcp.auth as auth

    auth.AUTH_DISABLED = True
    auth.VALID_API_KEYS = set()

    wsgi = _load_wsgi()
    client = TestClient(wsgi.build_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["server"] == "stele"
    assert body["store_mode"] == "file"
    assert "sse" in body["transports"]
    assert "core-sse" in body["transports"]
    assert body["tool_counts"]["full"] > body["tool_counts"]["core"]
    assert body["tool_counts"]["core"] >= 30


def test_protected_path_requires_auth_when_enabled(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("STELE_STORE", str(tmp_path / "scratch"))
    monkeypatch.delenv("STELE_STORE_DSN", raising=False)
    monkeypatch.delenv("STELE_AUTH_DISABLED", raising=False)

    import stele_mcp.auth as auth

    auth.AUTH_DISABLED = False
    auth.VALID_API_KEYS = {"stl_unit_test_key"}

    wsgi = _load_wsgi()
    client = TestClient(wsgi.build_app())

    denied = client.get("/sse")
    assert denied.status_code == 401

    denied_core = client.get("/core/sse")
    assert denied_core.status_code == 401

    ok_health = client.get("/health")
    assert ok_health.status_code == 200


def test_core_mcp_route_serves_only_governed_ledger_tools(tmp_path, monkeypatch) -> None:
    """`/core/mcp` must expose exactly `_CORE_TOOL_NAMES` — none of the ~2000
    PEFT/agent-pattern research tools riding on the full `/mcp` surface."""
    monkeypatch.setenv("STELE_STORE", str(tmp_path / "scratch"))
    monkeypatch.delenv("STELE_STORE_DSN", raising=False)
    monkeypatch.setenv("STELE_AUTH_DISABLED", "true")
    monkeypatch.setenv("STELE_API_KEYS", "")

    import stele_mcp.auth as auth

    auth.AUTH_DISABLED = True
    auth.VALID_API_KEYS = set()

    from stele_mcp.server import _CORE_TOOL_NAMES

    wsgi = _load_wsgi()
    hdr = {"Accept": "application/json, text/event-stream"}
    init = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1"},
        },
    }
    list_tools = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}

    with TestClient(wsgi.build_app()) as client:
        r1 = client.post("/core/mcp", json=init, headers=hdr)
        assert r1.status_code == 200
        session_id = r1.headers.get("mcp-session-id")
        h2 = dict(hdr)
        if session_id:
            h2["mcp-session-id"] = session_id

        r2 = client.post("/core/mcp", json=list_tools, headers=h2)
        assert r2.status_code == 200
        match = re.search(r"data: (\{.*\})", r2.text)
        assert match, f"no SSE data payload in response: {r2.text[:200]}"
        payload = json.loads(match.group(1))
        returned = {t["name"] for t in payload["result"]["tools"]}

    assert returned == _CORE_TOOL_NAMES
    # None of the PEFT research-reproduction tools ride along on /core/mcp.
    assert "stele_sdt_dim" not in returned
    assert "stele_mef_adapt" not in returned
