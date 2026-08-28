"""Optional derived SQLite index — SoT stays files (C4). Stdlib only."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any


INDEX_NAME = "derived.sqlite"


def index_path(store_root: Path) -> Path:
    return Path(store_root) / "index" / INDEX_NAME


def rebuild_sqlite_index(store_root: Path, entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """
    Rebuild a derived FTS5 (+ metadata) index from live entry files.

    Never becomes SoT — delete anytime; rebuild from files.
    """
    path = index_path(store_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path))
    try:
        conn.execute(
            """
            CREATE TABLE entries (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                scope TEXT NOT NULL,
                state TEXT NOT NULL,
                layer TEXT NOT NULL,
                last_verified TEXT,
                conflict_key TEXT,
                cues TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE entries_fts USING fts5(
                id UNINDEXED,
                title,
                body,
                cues,
                content='entries',
                content_rowid='rowid'
            )
            """
        )
        # Triggers keep FTS in sync on insert (rebuild is insert-only).
        conn.execute(
            """
            CREATE TRIGGER entries_ai AFTER INSERT ON entries BEGIN
              INSERT INTO entries_fts(rowid, id, title, body, cues)
              VALUES (new.rowid, new.id, new.title, new.body, new.cues);
            END
            """
        )
        n = 0
        for e in entries:
            cues = e.get("cue_tags") or []
            cue_text = " ".join(str(c) for c in cues) if isinstance(cues, list) else ""
            conn.execute(
                """
                INSERT INTO entries(id, title, body, scope, state, layer, last_verified, conflict_key, cues)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    e["id"],
                    e.get("title") or "",
                    e.get("body") or "",
                    e.get("scope") or "",
                    e.get("state") or "",
                    e.get("layer") or "",
                    (e.get("temporal") or {}).get("last_verified"),
                    e.get("conflict_key"),
                    cue_text,
                ),
            )
            n += 1
        conn.commit()
    finally:
        conn.close()
    return {
        "path": str(path),
        "entry_count": n,
        "note": "derived index — files remain SoT (C4)",
    }


def search_sqlite_index(
    store_root: Path,
    query: str,
    *,
    states: Sequence[str] | None = None,
    scopes: Sequence[str] | None = None,
    cue: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Query the derived FTS index. Empty/missing index → []."""
    path = index_path(store_root)
    if not path.exists() or not query.strip():
        return []
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        # Escape FTS5 special chars lightly — quote the query as a phrase bag of tokens
        tokens = [t for t in query.replace('"', " ").split() if t]
        if not tokens:
            return []
        fts_q = " ".join(f'"{t}"' for t in tokens[:12])
        sql = """
            SELECT e.id, e.title, e.scope, e.state, e.layer, e.cues,
                   bm25(entries_fts) AS rank
            FROM entries_fts
            JOIN entries e ON e.rowid = entries_fts.rowid
            WHERE entries_fts MATCH ?
        """
        params: list[Any] = [fts_q]
        if states:
            placeholders = ",".join("?" for _ in states)
            sql += f" AND e.state IN ({placeholders})"
            params.extend(states)
        if scopes:
            placeholders = ",".join("?" for _ in scopes)
            sql += f" AND e.scope IN ({placeholders})"
            params.extend(scopes)
        if cue:
            sql += " AND e.cues LIKE ?"
            params.append(f"%{cue}%")
        sql += " ORDER BY rank LIMIT ?"
        params.append(int(limit))
        rows = conn.execute(sql, params).fetchall()
        return [
            {
                "id": r["id"],
                "title": r["title"],
                "scope": r["scope"],
                "state": r["state"],
                "layer": r["layer"],
                "cues": r["cues"],
                "rank": r["rank"],
                "via": "sqlite_fts",
            }
            for r in rows
        ]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()
