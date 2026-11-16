"""Derived tenant keys (TECH_SPEC §12.1, ST1) — auth middleware unit coverage."""

from __future__ import annotations

import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from stele_mcp import auth as auth_module

SECRET = "test-secret-do-not-use"
VECTOR_KEY = "stl_acme_0p59V8dV554TE_3lmyXhrfNERv2GlWUS1dYdLIYS9fg"


async def _whoami(request):
    ident = auth_module.identity_from_scope(request.scope)
    return JSONResponse(
        {
            "kind": ident.kind if ident else None,
            "tenant": ident.tenant if ident else None,
        }
    )


def _client() -> TestClient:
    app = Starlette(
        routes=[
            Route("/core/mcp", _whoami, methods=["GET", "POST"]),
            Route("/core/sse", _whoami),
            Route("/mcp", _whoami, methods=["GET", "POST"]),
            Route("/sse", _whoami),
        ]
    )
    return TestClient(auth_module.SteleAuthMiddleware(app))


@pytest.fixture(autouse=True)
def _tenant_auth(monkeypatch):
    monkeypatch.setattr(auth_module, "VALID_API_KEYS", {"stl_operator_key_1"})
    monkeypatch.setattr(auth_module, "AUTH_DISABLED", False)
    monkeypatch.setattr(auth_module, "TENANT_KEY_SECRET", SECRET)
    monkeypatch.setattr(auth_module, "TENANT_KEY_VERSIONS", ("v1",))
    monkeypatch.setattr(auth_module, "REVOKED_TENANTS", set())
    monkeypatch.setattr(
        auth_module, "_rate_limiter", auth_module.RateLimiter(rate_per_minute=6000, burst=1000)
    )
    monkeypatch.setenv("STELE_STORE_DSN", "mysql://u:p@db.invalid:3306/x")


def _bearer(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"}


def test_test_vector_derives_and_verifies() -> None:
    assert auth_module.derive_tenant_key(SECRET, "acme", "v1") == VECTOR_KEY
    # The vector's MAC contains "_": the tenant must still come out as "acme".
    assert "_" in VECTOR_KEY[len("stl_acme_") :]
    assert auth_module.tenant_from_key(VECTOR_KEY) == "acme"


def test_valid_tenant_key_served_on_core() -> None:
    resp = _client().get("/core/mcp", headers=_bearer(VECTOR_KEY))
    assert resp.status_code == 200
    assert resp.json() == {"kind": "tenant", "tenant": "acme"}


def test_tampered_mac_refused() -> None:
    last = VECTOR_KEY[-1]
    tampered = VECTOR_KEY[:-1] + ("A" if last != "A" else "B")
    assert auth_module.tenant_from_key(tampered) is None
    assert _client().get("/core/mcp", headers=_bearer(tampered)).status_code == 401


def test_other_tenant_name_with_same_mac_refused() -> None:
    forged = "stl_acmf_" + VECTOR_KEY[len("stl_acme_") :]
    assert auth_module.tenant_from_key(forged) is None


def test_unknown_version_refused(monkeypatch) -> None:
    v2_key = auth_module.derive_tenant_key(SECRET, "acme", "v2")
    assert auth_module.tenant_from_key(v2_key) is None
    monkeypatch.setattr(auth_module, "TENANT_KEY_VERSIONS", ("v1", "v2"))
    assert auth_module.tenant_from_key(v2_key) == "acme"


def test_revoked_tenant_refused(monkeypatch) -> None:
    monkeypatch.setattr(auth_module, "REVOKED_TENANTS", {"acme"})
    assert auth_module.tenant_from_key(VECTOR_KEY) is None
    assert _client().get("/core/mcp", headers=_bearer(VECTOR_KEY)).status_code == 401


@pytest.mark.parametrize(
    "tenant",
    ["Acme", "-acme", "ac_me", "acme!", "", "a" * 57],
)
def test_tenant_breaking_the_rule_refused(tenant: str) -> None:
    with pytest.raises(ValueError):
        auth_module.derive_tenant_key(SECRET, tenant)
    import base64
    import hashlib
    import hmac

    mac = hmac.new(SECRET.encode(), f"stl:v1:{tenant}".encode(), hashlib.sha256).digest()
    key = f"stl_{tenant}_" + base64.urlsafe_b64encode(mac).rstrip(b"=").decode()
    assert auth_module.tenant_from_key(key) is None


def test_longest_tenant_name_allowed() -> None:
    tenant = "a" * 56
    key = auth_module.derive_tenant_key(SECRET, tenant)
    assert auth_module.tenant_from_key(key) == tenant
    assert len(f"stele:t-{tenant}") <= 64


def test_tenant_key_refused_off_core() -> None:
    client = _client()
    assert client.get("/mcp", headers=_bearer(VECTOR_KEY)).status_code == 401
    assert client.get("/sse", headers=_bearer(VECTOR_KEY)).status_code == 401
    assert "only under /core" in client.get("/mcp", headers=_bearer(VECTOR_KEY)).json()["error"]


def test_tenant_key_refused_on_file_store(monkeypatch) -> None:
    monkeypatch.delenv("STELE_STORE_DSN", raising=False)
    resp = _client().get("/core/mcp", headers=_bearer(VECTOR_KEY))
    assert resp.status_code == 401
    assert "MySQL" in resp.json()["error"]


def test_tenant_secret_set_and_no_api_keys_serves_tenant(monkeypatch) -> None:
    monkeypatch.setattr(auth_module, "VALID_API_KEYS", set())
    client = _client()
    assert client.get("/core/mcp", headers=_bearer(VECTOR_KEY)).status_code == 200
    # Operator-style keys still have nothing to match.
    assert client.get("/core/mcp", headers=_bearer("stl_operator_key_1")).status_code == 401


def test_fail_closed_only_when_both_missing(monkeypatch) -> None:
    monkeypatch.setattr(auth_module, "VALID_API_KEYS", set())
    monkeypatch.setattr(auth_module, "TENANT_KEY_SECRET", "")
    resp = _client().get("/core/mcp", headers=_bearer(VECTOR_KEY))
    assert resp.status_code == 401
    assert "STELE_API_KEYS" in resp.json()["error"]


def test_tenant_keys_off_without_secret(monkeypatch) -> None:
    monkeypatch.setattr(auth_module, "TENANT_KEY_SECRET", "")
    resp = _client().get("/core/mcp", headers=_bearer(VECTOR_KEY))
    assert resp.status_code == 401
    assert "Invalid API key" in resp.json()["error"]


def test_operator_key_behaves_as_before() -> None:
    client = _client()
    for path in ("/core/mcp", "/mcp", "/sse"):
        resp = client.get(path, headers=_bearer("stl_operator_key_1"))
        assert resp.status_code == 200
        assert resp.json() == {"kind": "operator", "tenant": None}
    assert client.get("/mcp", headers=_bearer("stl_wrong")).status_code == 401
