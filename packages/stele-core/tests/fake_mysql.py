"""In-process stand-in for PyMySQL, enough for ``MySQLSteleStore``.

Tests that exercise the MySQL store must never reach a hosted database; this
module answers exactly the statements ``stele_core.mysql_store`` sends, over
plain Python dicts shared by every connection to one ``FakeMySQLServer``.

Usage::

    server = FakeMySQLServer()
    server.install(monkeypatch)          # patches pymysql.connect
    Stele.open(tmp, store_id="x", dsn=FAKE_DSN)
"""

from __future__ import annotations

import re
from typing import Any

FAKE_DSN = "mysql://fake:fake@fake-mysql.invalid:3306/stele_test"


def _norm(sql: str) -> str:
    return re.sub(r"\s+", " ", sql).strip()


class FakeMySQLServer:
    def __init__(self) -> None:
        self.meta: dict[str, dict[str, Any]] = {}
        self.entries: dict[tuple[str, str], dict[str, Any]] = {}
        self.journal: list[dict[str, Any]] = []
        self.attachments: dict[tuple[str, str], bytes] = {}
        self.statements: list[str] = []
        self.connections = 0

    def install(self, monkeypatch: Any) -> None:
        import pymysql

        def _connect(**_params: Any) -> FakeConnection:
            self.connections += 1
            return FakeConnection(self)

        monkeypatch.setattr(pymysql, "connect", _connect)
        monkeypatch.setenv("STELE_MYSQL_SSL_DISABLED", "1")

    def add_store_row(self, store_id: str, created_at: str = "1970-01-01T00:00:00Z") -> None:
        self.meta[store_id] = {
            "store_id": store_id,
            "schema_version": 1,
            "created_at": created_at,
        }


class FakeConnection:
    def __init__(self, server: FakeMySQLServer) -> None:
        self.server = server

    def cursor(self) -> FakeCursor:
        return FakeCursor(self.server)

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None

    def ping(self, reconnect: bool = False) -> None:
        return None

    def close(self) -> None:
        return None


class FakeCursor:
    def __init__(self, server: FakeMySQLServer) -> None:
        self.s = server
        self._rows: list[dict[str, Any]] = []
        self.rowcount = 0

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def fetchone(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None

    def fetchall(self) -> list[dict[str, Any]]:
        return list(self._rows)

    def execute(self, sql: str, args: tuple[Any, ...] | None = None) -> int:  # noqa: C901
        q = _norm(sql)
        a = tuple(args or ())
        s = self.s
        s.statements.append(q)
        self._rows = []
        self.rowcount = 0
        up = q.upper()

        if up.startswith("CREATE TABLE") or up.startswith("SET "):
            return 0
        if q == "SELECT 1":
            self._rows = [{"1": 1}]
        elif q.startswith("SELECT GET_LOCK"):
            self._rows = [{"got": 1}]
        elif q.startswith("SELECT RELEASE_LOCK"):
            self._rows = [{"rel": 1}]
        elif q == "SELECT store_id FROM stele_meta WHERE store_id = %s":
            row = s.meta.get(a[0])
            self._rows = [{"store_id": row["store_id"]}] if row else []
        elif q.startswith("SELECT store_id FROM stele_meta WHERE store_id NOT LIKE 't-%'"):
            ids = sorted(k for k in s.meta if not k.startswith("t-"))
            self._rows = [{"store_id": ids[0]}] if ids else []
        elif q == "SELECT store_id FROM stele_meta LIMIT 1":
            ids = sorted(s.meta)
            self._rows = [{"store_id": ids[0]}] if ids else []
        elif q.startswith("INSERT INTO stele_meta"):
            s.add_store_row(a[0], a[2])
            self.rowcount = 1
        elif q.startswith("SELECT row_json FROM stele_journal WHERE store_id = %s ORDER BY seq DESC"):
            rows = [r for r in s.journal if r["store_id"] == a[0]]
            self._rows = [{"row_json": rows[-1]["row_json"]}] if rows else []
        elif q.startswith("SELECT row_json FROM stele_journal WHERE store_id = %s AND entry_id"):
            self._rows = [
                {"row_json": r["row_json"]}
                for r in s.journal
                if r["store_id"] == a[0] and r["entry_id"] == a[1]
            ]
        elif q.startswith("SELECT row_json FROM stele_journal WHERE store_id = %s"):
            self._rows = [{"row_json": r["row_json"]} for r in s.journal if r["store_id"] == a[0]]
        elif q.startswith("INSERT INTO stele_journal"):
            s.journal.append({"store_id": a[0], "entry_id": a[1], "row_json": a[2]})
            self.rowcount = 1
        elif q.startswith("INSERT INTO stele_entry"):
            s.entries[(a[0], a[1])] = {"state": a[2], "body_json": a[3]}
            self.rowcount = 1
        elif q == "SELECT body_json FROM stele_entry WHERE store_id = %s AND entry_id = %s":
            row = s.entries.get((a[0], a[1]))
            self._rows = [{"body_json": row["body_json"]}] if row else []
        elif q.startswith("SELECT body_json FROM stele_entry WHERE store_id = %s ORDER BY"):
            keys = sorted(k for k in s.entries if k[0] == a[0])
            self._rows = [{"body_json": s.entries[k]["body_json"]} for k in keys]
        elif q.startswith("DELETE FROM stele_entry"):
            self.rowcount = 1 if s.entries.pop((a[0], a[1]), None) is not None else 0
        elif q.startswith("INSERT IGNORE INTO stele_attachment"):
            s.attachments.setdefault((a[0], a[1]), bytes(a[2]))
            self.rowcount = 1
        elif q.startswith("SELECT data FROM stele_attachment"):
            blob = s.attachments.get((a[0], a[1]))
            self._rows = [{"data": blob}] if blob is not None else []
        else:
            raise AssertionError(f"fake MySQL got an unexpected statement: {q}")
        return self.rowcount
