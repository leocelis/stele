"""GitOfThoughts-shaped commit log for memory views (stdlib; no git binary)."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

_GENESIS = "0" * 64
COMMITS_NAME = "commits.ndjson"
REFS_DIR = "refs"
TAGS_DIR = "tags"
READ_HEAD = "read_head"


def _commits_path(root: Path) -> Path:
    return Path(root) / COMMITS_NAME


def _refs_dir(root: Path) -> Path:
    return Path(root) / REFS_DIR


def _tags_dir(root: Path) -> Path:
    return Path(root) / TAGS_DIR


def get_read_head(root: Path) -> str | None:
    """ChronoMem-shaped active read version (scopes Select to a prior view)."""
    return read_ref(root, READ_HEAD)


def set_read_head(root: Path, commit_hash: str | None) -> dict[str, Any]:
    """
    Activate or clear global read HEAD for counterfactual Select.

    Does not mutate SoT entry files — only the read overlay ref.
    """
    if commit_hash is None:
        path = _refs_dir(root) / READ_HEAD
        if path.is_file():
            path.unlink()
        return {
            "ok": True,
            "read_head": None,
            "note": "live SoT reads restored (ChronoMem-shaped)",
        }
    if get_commit(root, commit_hash) is None:
        raise SchemaError(f"unknown commit for read_head: {commit_hash}")
    write_ref(root, READ_HEAD, commit_hash)
    return {
        "ok": True,
        "read_head": commit_hash,
        "view": checkout_view(root, commit_hash),
        "note": "Select scoped to version — SoT unchanged (ChronoMem-shaped)",
    }


def _row_digest(row: dict[str, Any]) -> str:
    material = {k: v for k, v in row.items() if k != "commit_hash"}
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


def _iter_commits(root: Path) -> list[dict[str, Any]]:
    path = _commits_path(root)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(canonical_loads(line))
    return rows


def verify_commit_chain(root: Path) -> dict[str, Any]:
    rows = _iter_commits(root)
    known: set[str] = {_GENESIS}
    head = _GENESIS
    for i, row in enumerate(rows):
        parent = str(row.get("parent") or _GENESIS)
        if parent not in known:
            return {
                "ok": False,
                "error": f"unknown parent at row {i}",
                "row_count": len(rows),
                "head": None,
            }
        expected = _row_digest(row)
        if str(row.get("commit_hash") or "") != expected:
            return {
                "ok": False,
                "error": f"commit_hash mismatch at row {i}",
                "row_count": len(rows),
                "head": None,
            }
        known.add(expected)
        head = expected
    return {
        "ok": True,
        "row_count": len(rows),
        "head": head,
        "note": "commit chain — GitOfThoughts-shaped without git binary",
    }


def commit_view(
    root: Path,
    *,
    message: str,
    actor: str,
    ts: str,
    entry_ids: Sequence[str],
    journal_head: str | None,
    parent: str | None = None,
    branch: str = "main",
    score: float | None = None,
    outcome: str | None = None,
) -> dict[str, Any]:
    """
    Append a commit binding a memory view (entry id set) to journal head.

    Parent defaults to current branch tip (or genesis).
    """
    message = str(message or "").strip()
    actor = str(actor or "").strip()
    if not message or not actor:
        raise SchemaError("message and actor are required")
    if not entry_ids:
        raise SchemaError("entry_ids must be non-empty")
    chain = verify_commit_chain(root)
    if not chain.get("ok"):
        raise SchemaError(f"commit chain broken: {chain.get('error')}")
    tip = read_ref(root, branch)
    parent_hash = parent or tip or _GENESIS
    ids = sorted({str(i) for i in entry_ids})
    view_digest = hashlib.sha256(canonical_dumps(ids).encode("utf-8")).hexdigest()
    row: dict[str, Any] = {
        "parent": parent_hash,
        "message": message,
        "actor": actor,
        "ts": ts,
        "entry_ids": ids,
        "view_digest": view_digest,
        "journal_head": journal_head,
        "branch": branch,
        "score": score,
        "outcome": outcome,
    }
    row["commit_hash"] = _row_digest(row)
    path = _commits_path(root)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(canonical_dumps(row) + "\n")
    write_ref(root, branch, row["commit_hash"])
    if outcome in {"success", "failed"}:
        tag_commit(root, outcome, row["commit_hash"], actor=actor, ts=ts)
    return {
        "ok": True,
        "commit": row,
        "note": "memory view commit — not a git object; replay via checkout_view",
    }


def read_ref(root: Path, name: str) -> str | None:
    path = _refs_dir(root) / name
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8").strip() or None


def write_ref(root: Path, name: str, commit_hash: str) -> None:
    d = _refs_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(commit_hash + "\n", encoding="utf-8")


def tag_commit(
    root: Path,
    tag: str,
    commit_hash: str,
    *,
    actor: str,
    ts: str,
) -> dict[str, Any]:
    tag = str(tag or "").strip()
    if not tag:
        raise SchemaError("tag is required")
    d = _tags_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    body = {
        "tag": tag,
        "commit_hash": commit_hash,
        "actor": actor,
        "ts": ts,
    }
    (d / f"{tag}.json").write_text(canonical_dumps(body), encoding="utf-8")
    return body


def get_commit(root: Path, commit_hash: str) -> dict[str, Any] | None:
    for row in _iter_commits(root):
        if row.get("commit_hash") == commit_hash:
            return row
    return None


def checkout_view(root: Path, commit_hash: str) -> dict[str, Any]:
    """Reconstruct the entry-id set bound to a commit (replay)."""
    row = get_commit(root, commit_hash)
    if row is None:
        raise SchemaError(f"unknown commit: {commit_hash}")
    return {
        "commit_hash": commit_hash,
        "entry_ids": list(row.get("entry_ids") or []),
        "journal_head": row.get("journal_head"),
        "message": row.get("message"),
        "view_digest": row.get("view_digest"),
        "ts": row.get("ts"),
        "note": "checkout reconstructs id set — load entries from SoT by id",
    }


def diff_commits(root: Path, a: str, b: str) -> dict[str, Any]:
    """Entry-set diff between two commits (GitOfThoughts-shaped audit)."""
    ca = checkout_view(root, a)
    cb = checkout_view(root, b)
    sa, sb = set(ca["entry_ids"]), set(cb["entry_ids"])
    return {
        "a": a,
        "b": b,
        "only_in_a": sorted(sa - sb),
        "only_in_b": sorted(sb - sa),
        "shared": sorted(sa & sb),
        "message_a": ca.get("message"),
        "message_b": cb.get("message"),
        "note": "entry-set diff — line-level body diffs are caller-side",
    }


def merge_refs(
    root: Path,
    ours: str,
    theirs: str,
    *,
    into_branch: str = "main",
    actor: str,
    ts: str,
) -> dict[str, Any]:
    """
    Merge two branch tips: union entry ids; conflict when shared slots disagree
    is reported via commit messages only — entry-level conflict uses same ids.

    Surfaces empty intersection as clean fast-forward style union commit.
    """
    ha, hb = read_ref(root, ours), read_ref(root, theirs)
    if not ha or not hb:
        raise SchemaError("both branch refs must exist")
    ca, cb = checkout_view(root, ha), checkout_view(root, hb)
    sa, sb = set(ca["entry_ids"]), set(cb["entry_ids"])
    conflicts = sorted(sa & sb)  # same ids = no content conflict at id layer
    # GitOfThoughts lesson: content-hash ids can silently coexist; flag overlap
    # as needs_adjudication when messages differ
    needs = []
    if ca.get("message") != cb.get("message") and (sa & sb):
        needs.append("overlapping_ids_divergent_messages")
    merged_ids = sorted(sa | sb)
    result = commit_view(
        root,
        message=f"merge {ours}+{theirs}",
        actor=actor,
        ts=ts,
        entry_ids=merged_ids,
        journal_head=None,
        parent=ha,
        branch=into_branch,
        outcome=None,
    )
    return {
        "ok": True,
        "merged_commit": result["commit"],
        "only_ours": sorted(sa - sb),
        "only_theirs": sorted(sb - sa),
        "overlap": conflicts,
        "needs_adjudication": needs,
        "note": "union merge of view sets — contested content still needs MELD classify",
    }


def copyability_score(query: str, entry: Mapping[str, Any]) -> float:
    """
    Jaccard token overlap vs title+body — GitOfThoughts copyability proxy.

    Paper τ≈0.8 for near-duplicate payoff; below → memory unlikely to help accuracy.
    """
    q = set(tokenize(query or ""))
    text = f"{entry.get('title') or ''} {entry.get('body') or ''}"
    t = set(tokenize(text))
    if not q or not t:
        return 0.0
    return round(len(q & t) / len(q | t), 6)


def copyability_gate(
    query: str,
    entries: Iterable[Mapping[str, Any]],
    *,
    threshold: float = 0.8,
) -> dict[str, Any]:
    """Flag whether any hit clears the copyability threshold."""
    if threshold < 0 or threshold > 1:
        raise SchemaError("threshold must be in [0, 1]")
    scored = []
    for e in entries:
        s = copyability_score(query, e)
        scored.append({"id": e.get("id"), "score": s, "title": e.get("title")})
    scored.sort(key=lambda x: (-x["score"], x["id"] or ""))
    best = scored[0]["score"] if scored else 0.0
    return {
        "threshold": threshold,
        "best_score": best,
        "above_threshold": best >= threshold,
        "memory_likely_helps": best >= threshold,
        "ranked": scored[:20],
        "note": "GitOfThoughts copyability proxy — not method-transfer claim",
    }


def list_commits(root: Path, *, limit: int = 50, branch: str | None = None) -> list[dict[str, Any]]:
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    rows = _iter_commits(root)
    if branch:
        rows = [r for r in rows if r.get("branch") == branch]
    return list(reversed(rows[-limit:]))
