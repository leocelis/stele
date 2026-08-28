"""Dynamic Cheatsheet-shaped test-time memory (stdlib; no LLM).

Shaped by Dynamic Cheatsheet (arXiv:2504.07952): Gen/Cur memory,
DC-Cu cumulative vs DC-RS retrieve→curate→generate, concise snippets
not full-history. Proxies only — not DC paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)
SNIPPET_KINDS = frozenset({"strategy", "code", "insight", "formula"})
CURATOR_ACTIONS = frozenset({"ADD", "REFINE", "PRUNE", "KEEP"})


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def extract_cheatsheet_snippet(
    *,
    kind: str,
    title: str,
    body: str,
    max_chars: int = 240,
) -> dict[str, Any]:
    """Curate a concise transferable snippet (not a transcript dump)."""
    if kind not in SNIPPET_KINDS:
        raise SchemaError(f"kind must be one of {sorted(SNIPPET_KINDS)}")
    if not isinstance(title, str) or not title.strip():
        raise SchemaError("title required")
    if not isinstance(body, str) or not body.strip():
        raise SchemaError("body required")
    if max_chars < 40:
        raise SchemaError("max_chars must be >= 40")
    compact = " ".join(body.strip().split())
    if len(compact) > max_chars:
        compact = compact[: max_chars - 1].rstrip() + "…"
    sid = hashlib.sha256(
        canonical_dumps({"k": kind, "t": title, "b": compact}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "snippet_id": sid,
        "kind": kind,
        "title": title.strip()[:80],
        "body": compact,
        "char_count": len(compact),
        "ok": True,
        "note": "dc extract_cheatsheet_snippet",
    }


def retrieve_cheatsheet(
    memory: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Retrieve relevant cheatsheet snippets for a query."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    scored: list[tuple[int, dict[str, Any]]] = []
    for s in memory:
        if not isinstance(s, Mapping):
            continue
        blob = f"{s.get('title') or ''} {s.get('body') or ''} {s.get('kind') or ''}"
        score = len(qtok & _tokens(blob))
        scored.append((score, dict(s)))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("snippet_id") or "")))
    hits = [s for sc, s in scored[:top_k] if sc >= 0]
    return {
        "query": query.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "dc retrieve_cheatsheet",
    }


def curator_decide(
    *,
    proposed_useful: bool,
    existing_faulty: bool = False,
    superseded: bool = False,
) -> dict[str, Any]:
    """Curator decision without ground-truth labels (proxy heuristics)."""
    if existing_faulty or superseded:
        action = "PRUNE" if existing_faulty else "REFINE"
    elif proposed_useful:
        action = "ADD"
    else:
        action = "KEEP"
    return {
        "action": action,
        "proposed_useful": proposed_useful,
        "existing_faulty": existing_faulty,
        "superseded": superseded,
        "apply": False,
        "ok": True,
        "note": "dc curator_decide",
    }


def compact_memory_gate(
    *,
    entry_chars: int,
    max_entry_chars: int = 240,
    memory_chars: int = 0,
    max_memory_chars: int = 4000,
) -> dict[str, Any]:
    """Reject full-history ballooning; keep cheatsheet compact."""
    if max_entry_chars < 1 or max_memory_chars < 1:
        raise SchemaError("limits must be >= 1")
    entry_ok = entry_chars <= max_entry_chars
    mem_ok = memory_chars + entry_chars <= max_memory_chars
    return {
        "allowed": entry_ok and mem_ok,
        "entry_ok": entry_ok,
        "memory_ok": mem_ok,
        "entry_chars": entry_chars,
        "memory_chars": memory_chars,
        "reason": (
            None
            if entry_ok and mem_ok
            else ("entry_too_long" if not entry_ok else "memory_budget")
        ),
        "ok": True,
        "note": "dc compact_memory_gate — forbids FH append",
    }


def dc_rs_order_check(
    steps: Sequence[str],
) -> dict[str, Any]:
    """
    DC-RS order: retrieve → curate → generate.
    DC-Cu: generate → curate (no retrieve).
    """
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
        raise SchemaError("steps sequence required")
    norm = [str(s).strip().lower() for s in steps if str(s).strip()]
    rs = ["retrieve", "curate", "generate"]
    cu = ["generate", "curate"]
    mode = None
    valid = False
    if norm == rs:
        mode = "DC-RS"
        valid = True
    elif norm == cu:
        mode = "DC-Cu"
        valid = True
    elif "retrieve" in norm and norm != rs:
        mode = "invalid_rs"
    else:
        mode = "unknown"
    return {
        "mode": mode,
        "valid": valid,
        "steps": norm,
        "ok": True,
        "note": "dc dc_rs_order_check",
    }
