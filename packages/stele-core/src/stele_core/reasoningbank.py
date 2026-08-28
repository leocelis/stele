"""ReasoningBank-shaped strategy memory (stdlib; no LLM).

Shaped by ReasoningBank (arXiv:2509.25140): distill transferable strategies
from successful *and* failed experiences; MaTTS contrastive scaling plans.
Proxies only — not ReasoningBank / WebArena paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def distill_strategy_item(
    entry: Mapping[str, Any],
    *,
    outcome: str = "success",
) -> dict[str, Any]:
    """
    Distill title / description / content strategy item.
    outcome: success | failure (both are first-class).
    """
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    if outcome not in {"success", "failure"}:
        raise SchemaError("outcome must be success|failure")
    title = str(entry.get("title") or "strategy").strip()[:80]
    body = str(entry.get("body") or "").strip()
    first = body.split(".")[0].strip() if body else title
    prefix = "Avoid:" if outcome == "failure" else "Do:"
    description = f"{prefix} {first}"[:160]
    steps = [s.strip() for s in re.split(r"[;\n]", body) if s.strip()][:5]
    if not steps:
        steps = [first]
    content = "; ".join(f"{i+1}. {s}" for i, s in enumerate(steps))[:400]
    sid = hashlib.sha256(
        canonical_dumps(
            {"title": title, "outcome": outcome, "id": entry.get("id")}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "strategy_id": sid,
        "entry_id": entry.get("id"),
        "outcome": outcome,
        "title": title,
        "description": description,
        "content": content,
        "ok": True,
        "note": "reasoningbank distill_strategy_item",
    }


def failure_lesson_gate(
    *,
    success_count: int,
    failure_count: int,
    min_failure_share: float = 0.2,
) -> dict[str, Any]:
    """Gate: strategy bank must include failure lessons (not success-only)."""
    if success_count < 0 or failure_count < 0:
        raise SchemaError("counts must be >= 0")
    total = success_count + failure_count
    share = (failure_count / total) if total else 0.0
    pass_ = total == 0 or share >= min_failure_share or failure_count >= 1
    return {
        "success_count": success_count,
        "failure_count": failure_count,
        "failure_share": round(share, 4),
        "min_failure_share": min_failure_share,
        "pass": pass_,
        "ok": True,
        "note": "reasoningbank failure_lesson_gate",
    }


def retrieve_strategies(
    strategies: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Retrieve strategy items by lexical overlap with query."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string required")
    qtok = {t.lower() for t in _TOKEN.findall(query)}
    scored: list[tuple[int, Mapping[str, Any]]] = []
    for s in strategies:
        if not isinstance(s, Mapping):
            continue
        blob = f"{s.get('title') or ''} {s.get('description') or ''} {s.get('content') or ''}"
        score = len(qtok & {t.lower() for t in _TOKEN.findall(blob)})
        scored.append((score, s))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("strategy_id") or "")))
    hits = [dict(s) for sc, s in scored[:top_k] if sc >= 0]
    return {
        "query": query.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "reasoningbank retrieve_strategies",
    }


def consolidate_strategy_plan(
    items: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Consolidate strategy items into bank plan (report-only; dedupe by title)."""
    if not isinstance(items, Sequence) or isinstance(items, (str, bytes)):
        raise SchemaError("items sequence required")
    seen: set[str] = set()
    keep: list[dict[str, Any]] = []
    skip: list[str] = []
    for it in items:
        if not isinstance(it, Mapping):
            continue
        key = str(it.get("title") or "").strip().lower()
        sid = str(it.get("strategy_id") or key)
        if key in seen:
            skip.append(sid)
            continue
        seen.add(key)
        keep.append(dict(it))
    succ = sum(1 for k in keep if k.get("outcome") == "success")
    fail = sum(1 for k in keep if k.get("outcome") == "failure")
    gate = failure_lesson_gate(success_count=succ, failure_count=fail)
    return {
        "keep_count": len(keep),
        "skip_count": len(skip),
        "keep": keep,
        "skipped_ids": skip,
        "failure_gate": gate,
        "apply": False,
        "ok": True,
        "note": "reasoningbank consolidate_strategy_plan",
    }


def matts_contrastive_plan(
    *,
    mode: str = "parallel",
    n_trajectories: int = 3,
    task_hint: str = "",
) -> dict[str, Any]:
    """
    MaTTS memory-aware test-time scaling plan (report-only).
    parallel = contrast across trajectories; sequential = self-refine chain.
    """
    if mode not in {"parallel", "sequential"}:
        raise SchemaError("mode must be parallel|sequential")
    if n_trajectories < 2:
        raise SchemaError("n_trajectories must be >= 2")
    steps: list[dict[str, Any]]
    if mode == "parallel":
        steps = [
            {
                "step": i + 1,
                "action": "explore_trajectory",
                "role": "contrast_branch",
            }
            for i in range(n_trajectories)
        ]
        steps.append({"step": n_trajectories + 1, "action": "contrast_distill", "role": "aggregate"})
    else:
        steps = [
            {"step": 1, "action": "attempt", "role": "seed"},
            {"step": 2, "action": "self_refine", "role": "intermediate"},
            {"step": 3, "action": "final_distill", "role": "aggregate"},
        ]
    return {
        "mode": mode,
        "n_trajectories": n_trajectories,
        "task_hint": task_hint[:120],
        "steps": steps,
        "apply": False,
        "ok": True,
        "note": "reasoningbank matts_contrastive_plan — MaTTS proxy",
    }
