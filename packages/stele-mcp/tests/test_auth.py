"""Unit coverage for stele_mcp.auth (hosted Bearer + rate limit)."""

from __future__ import annotations

import hashlib

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from stele_mcp import auth as auth_module


async def _protected(request):
    return JSONResponse({"ok": True, "key_id": auth_module.current_key_id.get()})


async def _health(request):
    return JSONResponse({"status": "healthy"})


def _make_client() -> TestClient:
    app = Starlette(routes=[Route("/protected", _protected), Route("/health", _health)])
    wrapped = auth_module.SteleAuthMiddleware(app)
    return TestClient(wrapped)


@pytest.fixture(autouse=True)
def _restore_auth_globals():
    orig_keys = set(auth_module.VALID_API_KEYS)
    orig_disabled = auth_module.AUTH_DISABLED
    yield
    auth_module.VALID_API_KEYS = orig_keys
    auth_module.AUTH_DISABLED = orig_disabled


def test_request_with_valid_configured_key_is_allowed() -> None:
    auth_module.VALID_API_KEYS = {"stl_test_validkey123"}
    auth_module.AUTH_DISABLED = False
    client = _make_client()

    resp = client.get("/protected", headers={"Authorization": "Bearer stl_test_validkey123"})

    assert resp.status_code == 200
    expected_key_id = hashlib.sha256(b"stl_test_validkey123").hexdigest()[:8]
    assert resp.json()["key_id"] == expected_key_id


def test_request_with_invalid_key_is_rejected() -> None:
    auth_module.VALID_API_KEYS = {"stl_test_validkey123"}
    auth_module.AUTH_DISABLED = False
    client = _make_client()

    resp = client.get("/protected", headers={"Authorization": "Bearer wrong-key"})

    assert resp.status_code == 401
    assert "Invalid API key" in resp.json()["error"]


def test_request_with_missing_authorization_header_is_rejected() -> None:
    auth_module.VALID_API_KEYS = {"stl_test_validkey123"}
    auth_module.AUTH_DISABLED = False
    client = _make_client()

    resp = client.get("/protected")

    assert resp.status_code == 401
    assert "Missing Authorization header" in resp.json()["error"]


def test_no_keys_configured_and_auth_not_disabled_is_fail_closed() -> None:
    auth_module.VALID_API_KEYS = set()
    auth_module.AUTH_DISABLED = False
    client = _make_client()

    resp = client.get("/protected", headers={"Authorization": "Bearer anything"})

    assert resp.status_code == 401
    assert "STELE_API_KEYS" in resp.json()["error"]


def test_health_path_is_exempt_from_auth_even_with_keys_configured() -> None:
    auth_module.VALID_API_KEYS = {"stl_test_validkey123"}
    auth_module.AUTH_DISABLED = False
    client = _make_client()

    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_auth_disabled_flag_bypasses_all_checks() -> None:
    auth_module.VALID_API_KEYS = {"stl_test_validkey123"}
    auth_module.AUTH_DISABLED = True
    client = _make_client()

    resp = client.get("/protected")

    assert resp.status_code == 200


def test_generate_api_key_prefix() -> None:
    key = auth_module.generate_api_key("deploy")
    assert key.startswith("stl_deploy_")


def test_rate_limiter_burst() -> None:
    limiter = auth_module.RateLimiter(rate_per_minute=60, burst=2)
    assert limiter.allow("k")[0] is True
    assert limiter.allow("k")[0] is True
    allowed, retry = limiter.allow("k")
    assert allowed is False
    assert retry > 0
