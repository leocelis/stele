"""MySQL-backed Stele store — optional extra for hosted durable SoT.

Requires ``pip install stele-core[mysql]`` (PyMySQL). Configuration:

    STELE_STORE_DSN            mysql://user:pass@host:port/dbname
    STELE_MYSQL_SSL_CA         path to server CA PEM, or
    STELE_MYSQL_SSL_CA_B64     same PEM base64-encoded (ephemeral filesystems)

TLS verification is mandatory. Entries, journal, and attachments live in
MySQL. ``root`` is a local scratch directory for rebuildable indexes and
sidecar features that still expect a Path layout.

Never log DSN passwords. Never commit live DSN values.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import tempfile
import time
import urllib.parse
import uuid
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any

from stele_core.schema import canonical_dumps, canonical_loads, validate_entry
from stele_core.store import StoreError, _GENESIS_HASH, _row_content_digest

_log = logging.getLogger("stele_core.mysql_store")

_SCHEMA_VERSION = 1

DDL = """
CREATE TABLE IF NOT EXISTS stele_meta (
    store_id        VARCHAR(64)  NOT NULL,
    schema_version  INT          NOT NULL,
    created_at      VARCHAR(32)  NOT NULL,
    PRIMARY KEY (store_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS stele_entry (
    store_id        VARCHAR(64)  NOT NULL,
    entry_id        VARCHAR(64)  NOT NULL,
    state           VARCHAR(32)  NOT NULL,
    body_json       LONGTEXT     NOT NULL,
    PRIMARY KEY (store_id, entry_id),
    KEY idx_stele_entry_state (store_id, state)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS stele_journal (
    seq             BIGINT       NOT NULL AUTO_INCREMENT,
    store_id        VARCHAR(64)  NOT NULL,
    entry_id        VARCHAR(64)      NULL,
    row_json        LONGTEXT     NOT NULL,
    PRIMARY KEY (seq),
    KEY idx_stele_journal_store (store_id, seq),
    KEY idx_stele_journal_entry (store_id, entry_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE IF NOT EXISTS stele_attachment (
    store_id        VARCHAR(64)  NOT NULL,
    digest          CHAR(64)     NOT NULL,
    data            LONGBLOB     NOT NULL,
    PRIMARY KEY (store_id, digest)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC
  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
"""

_RETRIES = int(os.environ.get("MYSQL_CONN_RETRIES", "7"))
_DELAY = float(os.environ.get("MYSQL_CONN_DELAY", "2"))
_STARTUP_BUDGET_S = float(os.environ.get("STELE_MYSQL_STARTUP_BUDGET_S", "45"))
_STARTUP_CONNECT_TIMEOUT_S = int(os.environ.get("STELE_MYSQL_STARTUP_CONNECT_TIMEOUT_S", "10"))
_PERMANENT_ERRNOS = frozenset({1044, 1045, 1049, 1698, 2059})
_PERMANENT_TLS_MARKER = "CERTIFICATE_VERIFY_FAILED"


def _is_permanent(exc: BaseException) -> bool:
    errno = exc.args[0] if getattr(exc, "args", None) else None
    if isinstance(errno, int) and errno in _PERMANENT_ERRNOS:
        return True
    return _PERMANENT_TLS_MARKER in str(exc)


def _resolve_ca_path() -> str:
    path = os.environ.get("STELE_MYSQL_SSL_CA")
    if path:
        return path
    b64 = os.environ.get("STELE_MYSQL_SSL_CA_B64")
    if b64:
        tmp = tempfile.NamedTemporaryFile(
            mode="wb", suffix=".pem", delete=False, prefix="stele_ca_"
        )
        tmp.write(base64.b64decode(b64))
        tmp.close()
        return tmp.name
    raise RuntimeError(
        "MySQL backend requires TLS verification: set STELE_MYSQL_SSL_CA "
        "(path to the server CA PEM) or STELE_MYSQL_SSL_CA_B64 (base64 PEM). "
        "Refusing to connect unverified."
    )


def _caller_or_placeholder_ts() -> str:
    return "1970-01-01T00:00:00Z"


class MySQLSteleStore:
    """Duck-typed SteleStore using MySQL for entries/journal/attachments."""

    backend = "mysql"

    def __init__(
        self,
        dsn: str,
        *,
        scratch_root: Path,
        store_id: str | None = None,
        create: bool = True,
    ) -> None:
        try:
            import pymysql  # noqa: F401
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "MySQL backend requires PyMySQL: pip install stele-core[mysql]"
            ) from exc

        self.root = Path(scratch_root)
        self.index_dir = self.root / "index"
        self.attachments = self.root / "attachments"
        self._params = self._parse(dsn)
        self._conn = self._connect_with_retry(
            budget_seconds=_STARTUP_BUDGET_S,
            connect_timeout=_STARTUP_CONNECT_TIMEOUT_S,
        )
        self._store_id = store_id or f"store_{uuid.uuid4().hex[:12]}"
        self._ensure_scratch()
        if create:
            self._init_schema()
        else:
            self._load_meta_or_fail()

    @staticmethod
    def _parse(dsn: str) -> dict:
        u = urllib.parse.urlparse(dsn)
        if u.scheme != "mysql":
            raise ValueError(f"unsupported DSN scheme {u.scheme!r}; expected mysql://")
        if not (u.hostname and u.username and u.path.lstrip("/")):
            raise ValueError("DSN must be mysql://user:pass@host:port/dbname")
        import pymysql.cursors

        return {
            "host": u.hostname,
            "port": u.port or 3306,
            "user": urllib.parse.unquote(u.username),
            "password": urllib.parse.unquote(u.password or ""),
            "database": u.path.lstrip("/"),
            "charset": "utf8mb4",
            "init_command": "SET NAMES utf8mb4 COLLATE utf8mb4_bin",
            "cursorclass": pymysql.cursors.DictCursor,
            "ssl": {"ca": _resolve_ca_path()},
            "connect_timeout": 30,
            "read_timeout": 60,
            "write_timeout": 60,
            "autocommit": False,
        }

    def _ensure_scratch(self) -> None:
        for d in (
            self.attachments,
            self.index_dir / "lexical",
            self.index_dir / "semantic",
            self.index_dir / "temporal",
        ):
            d.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _apply_session_settings(conn) -> None:
        with conn.cursor() as cur:
            cur.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        conn.commit()

    def _connect_with_retry(
        self,
        *,
        budget_seconds: float | None = None,
        connect_timeout: int | None = None,
    ):
        import pymysql

        params = dict(self._params)
        if connect_timeout is not None:
            params["connect_timeout"] = connect_timeout
        deadline = (time.monotonic() + budget_seconds) if budget_seconds else None
        last: Exception | None = None
        for attempt in range(_RETRIES):
            if deadline is not None and time.monotonic() >= deadline:
                raise RuntimeError(
                    f"mysql connection not established within the "
                    f"{budget_seconds:.0f}s startup budget"
                ) from last
            try:
                conn = pymysql.connect(**params)
                self._apply_session_settings(conn)
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    cur.fetchone()
                conn.commit()
                return conn
            except Exception as exc:  # noqa: BLE001
                last = exc
                if _is_permanent(exc):
                    raise RuntimeError(
                        f"mysql connection refused for a permanent reason (not retried): {exc}"
                    ) from exc
                if attempt < _RETRIES - 1:
                    wait = _DELAY * (2**attempt)
                    if deadline is not None and time.monotonic() + wait >= deadline:
                        raise RuntimeError(
                            f"mysql connection not established within the "
                            f"{budget_seconds:.0f}s startup budget"
                        ) from exc
                    _log.warning("mysql connect failed; retry in %.1fs", wait)
                    time.sleep(wait)
        raise RuntimeError(f"mysql connection failed after {_RETRIES} attempts") from last

    def ensure_live(self) -> None:
        try:
            self._conn.ping(reconnect=False)
        except Exception:  # noqa: BLE001
            _log.warning("mysql connection lost; reconnecting")
            self._conn = self._connect_with_retry()

    def _init_schema(self) -> None:
        self.ensure_live()
        try:
            for stmt in DDL.split(";"):
                if stmt.strip():
                    self._conn.cursor().execute(stmt)
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT store_id FROM stele_meta WHERE store_id = %s",
                    (self._store_id,),
                )
                if cur.fetchone() is None:
                    # Prefer an existing meta row if this DB already has one store.
                    cur.execute("SELECT store_id FROM stele_meta LIMIT 1")
                    existing = cur.fetchone()
                    if existing:
                        self._store_id = existing["store_id"]
                    else:
                        cur.execute(
                            "INSERT INTO stele_meta (store_id, schema_version, created_at) "
                            "VALUES (%s, %s, %s)",
                            (self._store_id, _SCHEMA_VERSION, _caller_or_placeholder_ts()),
                        )
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def _load_meta_or_fail(self) -> None:
        self.ensure_live()
        with self._conn.cursor() as cur:
            cur.execute("SELECT store_id FROM stele_meta LIMIT 1")
            row = cur.fetchone()
        if row is None:
            raise StoreError("no stele store in MySQL (stele_meta empty)")
        self._store_id = row["store_id"]

    @property
    def store_id(self) -> str:
        return self._store_id

    # ----- locking (MySQL named lock) -------------------------------------

    def acquire(self, *, timeout_s: float = 10.0) -> None:
        self.ensure_live()
        name = f"stele:{self._store_id}"
        with self._conn.cursor() as cur:
            cur.execute("SELECT GET_LOCK(%s, %s) AS got", (name, int(timeout_s)))
            row = cur.fetchone()
        self._conn.commit()
        if not row or int(row["got"] or 0) != 1:
            raise StoreError(f"could not acquire MySQL lock {name}")

    def release(self) -> None:
        self.ensure_live()
        name = f"stele:{self._store_id}"
        with self._conn.cursor() as cur:
            cur.execute("SELECT RELEASE_LOCK(%s) AS rel", (name,))
        self._conn.commit()

    def __enter__(self) -> MySQLSteleStore:
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()

    # ----- journal ---------------------------------------------------------

    def _journal_unlocked(
        self,
        op: str,
        *,
        entry_id: str | None = None,
        actor: str,
        payload: dict[str, Any] | None = None,
        ts: str,
    ) -> None:
        """Append a journal row without committing (caller owns the txn)."""
        prev_hash = _GENESIS_HASH
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT row_json FROM stele_journal WHERE store_id = %s "
                "ORDER BY seq DESC LIMIT 1",
                (self._store_id,),
            )
            last = cur.fetchone()
        if last and last.get("row_json"):
            try:
                prev_row = canonical_loads(last["row_json"])
                prev_hash = str(prev_row.get("row_hash") or _row_content_digest(prev_row))
            except Exception:  # noqa: BLE001
                prev_hash = _GENESIS_HASH
        line: dict[str, Any] = {
            "op": op,
            "entry_id": entry_id,
            "actor": actor,
            "ts": ts,
            "payload_digest": None,
            "prev_hash": prev_hash,
        }
        if payload is not None:
            line["payload_digest"] = hashlib.sha256(
                canonical_dumps(payload).encode("utf-8")
            ).hexdigest()
            if op == "PURGE" and isinstance(payload.get("removed"), list):
                line["removed"] = [str(x) for x in payload["removed"]]
        line["row_hash"] = _row_content_digest(line)
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO stele_journal (store_id, entry_id, row_json) VALUES (%s, %s, %s)",
                (self._store_id, entry_id, canonical_dumps(line)),
            )

    def journal(
        self,
        op: str,
        *,
        entry_id: str | None = None,
        actor: str,
        payload: dict[str, Any] | None = None,
        ts: str,
    ) -> None:
        self.ensure_live()
        try:
            self._journal_unlocked(op, entry_id=entry_id, actor=actor, payload=payload, ts=ts)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def iter_journal(self, *, entry_id: str | None = None) -> Iterator[dict[str, Any]]:
        self.ensure_live()
        with self._conn.cursor() as cur:
            if entry_id is None:
                cur.execute(
                    "SELECT row_json FROM stele_journal WHERE store_id = %s ORDER BY seq ASC",
                    (self._store_id,),
                )
            else:
                cur.execute(
                    "SELECT row_json FROM stele_journal WHERE store_id = %s AND entry_id = %s "
                    "ORDER BY seq ASC",
                    (self._store_id, entry_id),
                )
            rows = cur.fetchall()
        for row in rows:
            yield canonical_loads(row["row_json"])

    # ----- CRUD ------------------------------------------------------------

    def write_entry(self, entry: dict[str, Any], *, actor: str, ts: str, op: str) -> dict[str, Any]:
        validated = validate_entry(entry, allow_state=entry.get("state"))
        state = validated["state"]
        eid = validated["id"]
        self.ensure_live()
        body = canonical_dumps(validated)
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO stele_entry (store_id, entry_id, state, body_json) "
                    "VALUES (%s, %s, %s, %s) AS new "
                    "ON DUPLICATE KEY UPDATE state = new.state, body_json = new.body_json",
                    (self._store_id, eid, state, body),
                )
            self._journal_unlocked(op, entry_id=eid, actor=actor, payload=validated, ts=ts)
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        return validated

    def read_entry(self, entry_id: str) -> dict[str, Any] | None:
        self.ensure_live()
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT body_json FROM stele_entry WHERE store_id = %s AND entry_id = %s",
                (self._store_id, entry_id),
            )
            row = cur.fetchone()
        if row is None:
            return None
        return canonical_loads(row["body_json"])

    def delete_entry_file(self, entry_id: str, *, actor: str, ts: str, reason: str) -> bool:
        self.ensure_live()
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM stele_entry WHERE store_id = %s AND entry_id = %s",
                    (self._store_id, entry_id),
                )
                deleted = cur.rowcount > 0
            if not deleted:
                self._conn.rollback()
                return False
            self._journal_unlocked(
                "DELETE",
                entry_id=entry_id,
                actor=actor,
                payload={"reason": reason},
                ts=ts,
            )
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        return True

    def iter_entries(self, *, states: Iterable[str] | None = None) -> Iterator[dict[str, Any]]:
        self.ensure_live()
        want = set(states) if states is not None else None
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT body_json FROM stele_entry WHERE store_id = %s ORDER BY entry_id ASC",
                (self._store_id,),
            )
            rows = cur.fetchall()
        for row in rows:
            entry = canonical_loads(row["body_json"])
            if want is None or entry.get("state") in want:
                yield entry

    def drop_indexes(self) -> None:
        for sub in ("lexical", "semantic", "temporal"):
            d = self.index_dir / sub
            if d.exists():
                for child in d.iterdir():
                    if child.is_file():
                        child.unlink()

    def put_attachment(self, data: bytes) -> str:
        digest = hashlib.sha256(data).hexdigest()
        self.ensure_live()
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT IGNORE INTO stele_attachment (store_id, digest, data) VALUES (%s, %s, %s)",
                (self._store_id, digest, data),
            )
        self._conn.commit()
        path = self.attachments / digest
        if not path.exists():
            path.write_bytes(data)
        return digest

    def verify_attachment_digest(self, digest: str) -> bool:
        path = self.attachments / digest
        if path.exists():
            return hashlib.sha256(path.read_bytes()).hexdigest() == digest
        self.ensure_live()
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT data FROM stele_attachment WHERE store_id = %s AND digest = %s",
                (self._store_id, digest),
            )
            row = cur.fetchone()
        if row is None:
            return False
        data = bytes(row["data"])
        ok = hashlib.sha256(data).hexdigest() == digest
        if ok:
            path.write_bytes(data)
        return ok

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:  # noqa: BLE001
            pass
