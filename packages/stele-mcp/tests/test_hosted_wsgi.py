"""HTTP shell smoke: health + auth on deploy/wsgi.py (file store, no DSN)."""

from __future__ import annotations

import importlib.util
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

    ok_health = client.get("/health")
    assert ok_health.status_code == 200
