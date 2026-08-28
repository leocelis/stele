"""HyMem-shaped typed context isolation (stdlib; no LLM).

Slots: plan · execute · reason · memory. Only schema-constrained crossover
messages may leave execute/reason into the planner pack.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

SLOTS = frozenset({"plan", "execute", "reason", "memory"})

_EXECUTE_CUES = frozenset(
    {
        "run",
        "exec",
        "execute",
        "shell",
        "tool",
        "stdout",
        "stderr",
        "traceback",
        "http",
        "status",
        "payload",
    }
)
_REASON_CUES = frozenset(
    {
        "because",
        "therefore",
        "however",
        "consider",
        "analyze",
        "hypothesis",
        "deliberat",
        "think",
        "maybe",
    }
)
_PLAN_CUES = frozenset(
    {
        "goal",
        "plan",
        "next",
        "step",
        "todo",
        "should",
        "must",
        "objective",
        "priority",
    }
)
_MEMORY_CUES = frozenset(
    {
        "remember",
        "lesson",
        "workflow",
        "skill",
        "previously",
        "history",
        "memory",
        "recall",
    }
)


def classify_slot(text: str) -> dict[str, Any]:
    """Assign a typed context slot from lexical cues (deterministic)."""
    raw = str(text or "").strip()
    if not raw:
        raise SchemaError("text is required")
    toks = set(tokenize(raw))
    scores = {
        "execute": len(toks & _EXECUTE_CUES),
        "reason": len(toks & _REASON_CUES),
        "plan": len(toks & _PLAN_CUES),
        "memory": len(toks & _MEMORY_CUES),
    }
    # layer-ish titles often memory
    best = max(scores.items(), key=lambda x: (x[1], x[0] != "execute"))
    slot = best[0] if best[1] > 0 else "plan"
    return {
        "text_preview": raw[:120],
        "slot": slot,
        "scores": scores,
        "ok": True,
        "note": "HyMem classify_slot — cue proxy, not paper isolator",
    }


def isolate_pack(
    items: Sequence[Mapping[str, Any]],
    *,
    planner_budget: int = 200,
) -> dict[str, Any]:
    """
    Partition items into typed slots; planner only receives constrained returns.

    Item shape: {id?, text|title|body, slot?} — slot auto-classified if missing.
    Execute/reason raw traces never enter planner; only summary returns do.
    """
    buckets: dict[str, list[dict[str, Any]]] = {
        "plan": [],
        "execute": [],
        "reason": [],
        "memory": [],
    }
    for it in items:
        text = str(
            it.get("text")
            or it.get("title")
            or it.get("body")
            or ""
        ).strip()
        if not text:
            continue
        slot = str(it.get("slot") or "").strip()
        if slot not in SLOTS:
            slot = classify_slot(text)["slot"]
        row = {
            "id": it.get("id"),
            "text": text,
            "slot": slot,
            "layer": it.get("layer"),
        }
        buckets[slot].append(row)

    # Constrained crossover: short returns from execute/reason only
    returns: list[dict[str, Any]] = []
    for slot in ("execute", "reason"):
        for row in buckets[slot]:
            words = str(row["text"]).split()
            summary = " ".join(words[:12])
            returns.append(
                {
                    "from_slot": slot,
                    "id": row.get("id"),
                    "return": summary,
                    "kind": "typed_return",
                }
            )

    planner: list[dict[str, Any]] = []
    used = 0
    for row in buckets["plan"] + buckets["memory"]:
        cost = max(1, len(str(row["text"]).split()))
        if used + cost > planner_budget:
            continue
        planner.append(
            {
                "id": row.get("id"),
                "text": row["text"],
                "slot": row["slot"],
                "kind": "direct",
            }
        )
        used += cost
    for ret in returns:
        cost = max(1, len(str(ret["return"]).split()))
        if used + cost > planner_budget:
            continue
        planner.append(ret)
        used += cost

    diluted = any(
        r.get("kind") == "direct" and r.get("slot") in {"execute", "reason"}
        for r in planner
    )
    return {
        "buckets": {k: len(v) for k, v in buckets.items()},
        "typed_returns": returns,
        "planner_pack": planner,
        "used": used,
        "budget": planner_budget,
        "dilution_ok": not diluted,
        "ok": True,
        "note": "HyMem isolate_pack — typed isolation; raw execute/reason blocked from planner",
    }
