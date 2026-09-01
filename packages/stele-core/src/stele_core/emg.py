"""EMG-shaped experience correction paths (stdlib; no LLM).

Match a failed lesson to a successful workflow/skill and emit an edit path
(add/delete/relabel token ops) — one-shot correction plan, not reflect-replay.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def _tokset(entry: Mapping[str, Any]) -> set[str]:
    return set(tokenize(f"{entry.get('title') or ''}\n{entry.get('body') or ''}"))


def correction_path(
    failed: Mapping[str, Any],
    success: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Graph-edit proxy between a failure lesson and a successful workflow/skill.
    """
    ftok = _tokset(failed)
    stok = _tokset(success)
    add = sorted(stok - ftok)
    delete = sorted(ftok - stok)
    keep = sorted(ftok & stok)
    return {
        "failed_id": failed.get("id"),
        "success_id": success.get("id"),
        "add": add[:40],
        "delete": delete[:40],
        "keep": keep[:40],
        "add_count": len(add),
        "delete_count": len(delete),
        "keep_count": len(keep),
        "overlap": round(len(keep) / max(len(ftok | stok), 1), 4),
        "note": "EMG correction path — token edit proxy, not ALFWorld scores",
    }


def match_correction(
    entries: Iterable[Mapping[str, Any]],
    *,
    failure_id: str | None = None,
    min_overlap: float = 0.15,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Pair failure_lesson entries with best workflow/skill_artifact successes.
    """
    if not (0 <= min_overlap <= 1):
        raise SchemaError("min_overlap must be in [0, 1]")
    pool = list(entries)
    failures = [
        e
        for e in pool
        if e.get("state") in {"promoted", "contested"}
        and e.get("layer") == "failure_lesson"
        and (failure_id is None or str(e.get("id")) == failure_id)
    ]
    successes = [
        e
        for e in pool
        if e.get("state") == "promoted"
        and e.get("layer") in {"workflow", "skill_artifact", "decision"}
        and int((e.get("usage") or {}).get("helpful") or 0)
        >= int((e.get("usage") or {}).get("harmful") or 0)
    ]
    pairs: list[dict[str, Any]] = []
    for f in failures:
        best = None
        best_score = -1.0
        for s in successes:
            if f.get("scope") and s.get("scope") and f.get("scope") != s.get("scope"):
                continue
            path = correction_path(f, s)
            score = float(path.get("overlap") or 0)
            if score > best_score:
                best_score = score
                best = path
        if best is None or best_score < min_overlap:
            pairs.append(
                {
                    "failed_id": f.get("id"),
                    "success_id": None,
                    "overlap": round(max(0.0, best_score), 4),
                    "action": "no_match",
                    "title": f.get("title"),
                }
            )
            continue
        best["action"] = "apply_edit_path"
        best["title_failed"] = f.get("title")
        pairs.append(best)
    pairs.sort(key=lambda r: (-float(r.get("overlap") or 0), str(r.get("failed_id"))))
    pairs = pairs[: max(1, int(limit))]
    return {
        "pairs": pairs,
        "count": len(pairs),
        "ok": True,
        "note": "EMG match_correction — one-shot edit plans; never auto-rewrites SoT",
    }


def insight_inject(
    correction: Mapping[str, Any],
    *,
    max_add: int = 8,
) -> dict[str, Any]:
    """Format a loop-free retrieval insight from a correction path."""
    add = list(correction.get("add") or [])[: max(1, int(max_add))]
    delete = list(correction.get("delete") or [])[: max(1, int(max_add))]
    lines = []
    if correction.get("success_id"):
        lines.append(f"Prefer pattern from {correction.get('success_id')}.")
    if add:
        lines.append("Do: " + ", ".join(add))
    if delete:
        lines.append("Avoid: " + ", ".join(delete))
    text = " ".join(lines) if lines else "No correction insight."
    return {
        "insight": text,
        "failed_id": correction.get("failed_id"),
        "success_id": correction.get("success_id"),
        "ok": bool(correction.get("success_id")),
        "note": "EMG insight inject — single-pass guidance, no reflect-replay loop",
    }
