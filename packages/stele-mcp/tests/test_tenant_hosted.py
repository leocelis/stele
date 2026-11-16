"""Multi-tenant hosts end to end through deploy/wsgi.py (TECH_SPEC §12, ST1-ST4).

The MySQL store is the in-process fake from ``fake_mysql.py``; nothing here
reaches a hosted database or the network.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import pytest
from fake_mysql import FAKE_DSN, FakeMySQLServer
from starlette.testclient import TestClient
from stele_mcp import auth as auth_module
from stele_mcp import server as server_mod

REPO = Path(__file__).resolve().parents[3]
SECRET = "test-secret-do-not-use"
TS = "2026-11-16T12:00:00Z"
OPERATOR_KEY = "stl_operator_key_1"
HDR = {"Accept": "application/json, text/event-stream"}
EVIDENCE = [
    {
        "type": "test_result",
        "issuer": "ci",
        "ref": "tests/test_tenant_hosted.py",
        "observed_at": TS,
        "verdict": "supports",
        "command": "pytest -q",
        "exit_status": 0,
    }
]


def _load_wsgi():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location(
        "stele_deploy_wsgi_tenants", REPO / "deploy" / "wsgi.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _key(tenant: str) -> str:
    return auth_module.derive_tenant_key(SECRET, tenant)


def _entry(title: str, body: str, scope: str) -> dict[str, Any]:
    return {
        "layer": "failure_lesson",
        "title": title,
        "body": body,
        "scope": scope,
        "temporal": {"valid_from": TS, "last_verified": TS},
        "provenance": {
            "agent": "writer-agent",
            "task": "tenant-hosted",
            "environment": "local",
            "subject_id": "subj-1",
            "source": "session:tenant-hosted",
            "written_at": TS,
        },
    }


@pytest.fixture
def env(tmp_path, monkeypatch):
    db = FakeMySQLServer()
    db.install(monkeypatch)
    db.add_store_row("store_operator01")
    monkeypatch.setenv("STELE_STORE", str(tmp_path / "scratch"))
    monkeypatch.setenv("STELE_STORE_DSN", FAKE_DSN)
    monkeypatch.setenv("STELE_STORE_ID", "store_operator01")
    monkeypatch.setenv("STELE_NOW", TS)
    monkeypatch.delenv("STELE_AUTH_DISABLED", raising=False)
    monkeypatch.setattr(auth_module, "VALID_API_KEYS", {OPERATOR_KEY})
    monkeypatch.setattr(auth_module, "AUTH_DISABLED", False)
    monkeypatch.setattr(auth_module, "TENANT_KEY_SECRET", SECRET)
    monkeypatch.setattr(auth_module, "TENANT_KEY_VERSIONS", ("v1",))
    monkeypatch.setattr(auth_module, "REVOKED_TENANTS", set())
    monkeypatch.setattr(
        auth_module, "_rate_limiter", auth_module.RateLimiter(rate_per_minute=6000, burst=1000)
    )
    monkeypatch.setattr(server_mod, "_STORE", None)
    server_mod._TENANT_STORES.clear()
    # The full-surface FastMCP is a module singleton; its session manager can
    # run once, so give each test app a fresh one.
    monkeypatch.setattr(server_mod.mcp, "_session_manager", None)
    wsgi = _load_wsgi()
    with TestClient(wsgi.build_app()) as client:
        yield client, db
    server_mod._TENANT_STORES.clear()


class Session:
    """A Streamable HTTP MCP session on /core/mcp."""

    def __init__(self, client: TestClient, key: str, path: str = "/core/mcp") -> None:
        self.client = client
        self.key = key
        self.path = path
        self.sid: str | None = None
        self._id = 0
        r = self._post(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        )
        self.init_status = r.status_code
        self.sid = r.headers.get("mcp-session-id")

    def _post(self, method: str, params: dict[str, Any], key: str | None = None):
        self._id += 1
        headers = dict(HDR)
        headers["Authorization"] = f"Bearer {key or self.key}"
        if self.sid:
            headers["mcp-session-id"] = self.sid
        body = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params}
        return self.client.post(self.path, json=body, headers=headers)

    def rpc(self, method: str, params: dict[str, Any], key: str | None = None) -> dict[str, Any]:
        r = self._post(method, params, key=key)
        assert r.status_code == 200, r.text[:300]
        match = re.search(r"data: (\{.*\})", r.text)
        assert match, r.text[:300]
        return json.loads(match.group(1))

    def tools(self) -> set[str]:
        return {t["name"] for t in self.rpc("tools/list", {})["result"]["tools"]}

    def call(self, name: str, key: str | None = None, **arguments: Any) -> tuple[bool, Any]:
        payload = self.rpc("tools/call", {"name": name, "arguments": arguments}, key=key)
        if "error" in payload:
            return False, payload["error"]["message"]
        result = payload["result"]
        text = result["content"][0]["text"] if result.get("content") else ""
        if result.get("isError"):
            return False, text
        return True, json.loads(text)


def _add_and_promote(s: Session, title: str, body: str, scope: str) -> str:
    ok, added = s.call("stele_add", entry_json=json.dumps(_entry(title, body, scope)), ts=TS)
    assert ok, added
    ok, promoted = s.call(
        "stele_promote", entry_id=added["id"], evidence_json=json.dumps(EVIDENCE), actor="ci",
        ts=TS,
    )
    assert ok, promoted
    return str(added["id"])


def test_tenant_tools_list_shows_only_five(env) -> None:
    client, _db = env
    s = Session(client, _key("acme"))
    assert s.init_status == 200
    assert s.tools() == server_mod.TENANT_TOOL_NAMES
    assert len(server_mod.TENANT_TOOL_NAMES) == 5
    # The operator key on the same surface still sees the whole core set.
    op = Session(client, OPERATOR_KEY)
    assert op.tools() == set(server_mod._CORE_TOOL_NAMES)
    assert len(server_mod._CORE_TOOL_NAMES) == 36


def test_tenant_calling_export_is_refused(env, tmp_path) -> None:
    client, _db = env
    s = Session(client, _key("acme"))
    for name, args in (
        ("stele_export", {"dest": str(tmp_path / "out")}),
        ("stele_snapshot", {}),
        ("stele_doctor", {}),
    ):
        ok, msg = s.call(name, **args)
        assert not ok
        assert "not available to tenant keys" in str(msg)
    assert not (tmp_path / "out").exists()


def test_tenant_key_on_full_surface_is_refused(env) -> None:
    client, _db = env
    headers = dict(HDR)
    headers["Authorization"] = f"Bearer {_key('acme')}"
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    assert client.post("/mcp", json=body, headers=headers).status_code == 401
    assert client.get("/sse", headers=headers).status_code == 401
    assert client.post("/messages/?session_id=x", json=body, headers=headers).status_code == 401


def test_two_tenants_never_see_each_other(env) -> None:
    client, db = env
    acme = Session(client, _key("acme"))
    globex = Session(client, _key("globex"))
    scope = "project:shared-scope"
    a_id = _add_and_promote(acme, "acme lesson", "zebra crossing calibration acme", scope)
    g_id = _add_and_promote(globex, "globex lesson", "zebra crossing calibration globex", scope)

    ok, a_list = acme.call("stele_list")
    assert ok
    assert [e["id"] for e in a_list["entries"]] == [a_id]
    ok, g_list = globex.call("stele_list")
    assert [e["id"] for e in g_list["entries"]] == [g_id]

    ok, a_hits = acme.call("stele_search", query="zebra crossing calibration", consumer_scope=scope)
    assert ok
    assert {h["id"] for h in a_hits} == {a_id}
    ok, g_hits = globex.call(
        "stele_search", query="zebra crossing calibration", consumer_scope=scope
    )
    assert {h["id"] for h in g_hits} == {g_id}

    # Deleting the other tenant's id from acme's key erases nothing.
    acme.call("stele_delete", actor="host", entry_id=g_id, ts=TS)
    assert ("t-globex", g_id) in db.entries
    ok, _ = globex.call("stele_delete", actor="host", entry_id=g_id, ts=TS)
    assert ok
    assert ("t-globex", g_id) not in db.entries
    assert ("t-acme", a_id) in db.entries

    # Stores land on their own rows, never the operator's.
    assert {"t-acme", "t-globex", "store_operator01"} <= set(db.meta)
    assert not any(k[0] == "store_operator01" for k in db.entries)


def test_session_continued_with_another_key_is_refused(env) -> None:
    client, db = env
    s = Session(client, _key("acme"))
    assert s.tools() == server_mod.TENANT_TOOL_NAMES
    other = s.rpc("tools/list", {}, key=_key("globex"))
    assert "error" in other
    assert "different key" in other["error"]["message"]
    op = s.rpc("tools/list", {}, key=OPERATOR_KEY)
    assert "error" in op
    ok, msg = s.call(
        "stele_add", key=_key("globex"),
        entry_json=json.dumps(_entry("x", "should never land", "project:x")), ts=TS,
    )
    assert not ok
    assert not any(k[0] == "t-globex" for k in db.entries)
    # The owner can keep using its session.
    assert s.tools() == server_mod.TENANT_TOOL_NAMES


def test_version_pin_in_one_store_does_not_steer_another(env) -> None:
    client, _db = env
    acme = Session(client, _key("acme"))
    globex = Session(client, _key("globex"))
    scope = "project:pin-scope"
    a_id = _add_and_promote(acme, "acme pin", "harbor tide tables acme", scope)
    g_id = _add_and_promote(globex, "globex pin", "harbor tide tables globex", scope)

    from stele_mcp.auth import Identity

    acme_store = server_mod.get_store(Identity(kind="tenant", key_id="k", tenant="acme"))
    globex_store = server_mod.get_store(Identity(kind="tenant", key_id="k", tenant="globex"))
    assert acme_store.store.root != globex_store.store.root
    commit = acme_store.commit_view("acme view", entry_ids=[a_id], actor="host", ts=TS)
    commit_hash = commit.get("commit_hash") or commit["commit"]["commit_hash"]
    acme_store.activate_version(commit_hash)
    assert acme_store.active_version()["live"] is False
    assert globex_store.active_version()["live"] is True

    ok, hits = globex.call("stele_search", query="harbor tide tables", consumer_scope=scope)
    assert ok
    assert {h["id"] for h in hits} == {g_id}
    ok, a_hits = acme.call("stele_search", query="harbor tide tables", consumer_scope=scope)
    assert ok
    assert {h["id"] for h in a_hits} <= {a_id}


def test_stele_list_pages_only_the_callers_entries(env) -> None:
    client, _db = env
    acme = Session(client, _key("acme"))
    globex = Session(client, _key("globex"))
    ids = []
    for i in range(3):
        ok, added = acme.call(
            "stele_add", entry_json=json.dumps(_entry(f"a{i}", f"acme body {i}", "project:l")),
            ts=TS,
        )
        assert ok
        ids.append(added["id"])
    globex.call(
        "stele_add", entry_json=json.dumps(_entry("g", "globex body", "project:l")), ts=TS
    )

    ok, p1 = acme.call("stele_list", limit=2)
    assert ok and len(p1["entries"]) == 2 and p1["next_cursor"]
    ok, p2 = acme.call("stele_list", limit=2, cursor=p1["next_cursor"])
    assert ok and len(p2["entries"]) == 1 and p2["next_cursor"] is None
    got = [e["id"] for e in p1["entries"] + p2["entries"]]
    assert got == sorted(ids)
    assert all(e["state"] == "quarantined" for e in p1["entries"] + p2["entries"])
    ok, q = acme.call("stele_list", state="quarantine")
    assert len(q["entries"]) == 3
    ok, p = acme.call("stele_list", state="promoted")
    assert p["entries"] == []


def test_operator_key_keeps_operator_store(env) -> None:
    client, db = env
    op = Session(client, OPERATOR_KEY)
    ok, added = op.call(
        "stele_add", entry_json=json.dumps(_entry("op", "operator body", "project:op")), ts=TS
    )
    assert ok
    assert ("store_operator01", added["id"]) in db.entries
    ok, stats = op.call("stele_stats")
    assert ok


def test_evicting_a_tenant_store_never_closes_it_under_a_caller(monkeypatch) -> None:
    """Build review 2026-11-16: eviction closed the evicted store's connection,
    cutting any request on another thread that still held it. Eviction now only
    drops the cache's reference."""

    class _Conn:
        closed = 0

        def close(self) -> None:
            _Conn.closed += 1

    class _FakeStele:
        def __init__(self) -> None:
            self.store = type("S", (), {"close": lambda self: _Conn().close()})()

    monkeypatch.setattr(server_mod, "_open_tenant_store", lambda tenant: _FakeStele())
    monkeypatch.setattr(server_mod, "TENANT_STORE_CACHE_SIZE", 1)
    server_mod._TENANT_STORES.clear()
    held = server_mod._tenant_store("acme")  # a request is using acme's store
    server_mod._tenant_store("beta")  # beta's arrival evicts acme
    assert "acme" not in server_mod._TENANT_STORES
    assert _Conn.closed == 0 and held.store is not None
    server_mod._TENANT_STORES.clear()
