"""AWM-shaped Agent Workflow Memory (stdlib; no LLM).

Shaped by Agent Workflow Memory (arXiv:2409.07429): induce reusable
workflows from successful trajectories; retrieve to guide future tasks;
online induce only on success. Proxies only — not AWM paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def induce_workflow(
    *,
    task: str,
    steps: Sequence[str],
    success: bool = True,
) -> dict[str, Any]:
    """Induce a workflow routine from a task + action steps."""
    if not isinstance(task, str) or not task.strip():
        raise SchemaError("task string required")
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
        raise SchemaError("steps sequence required")
    clean = [str(s).strip() for s in steps if str(s).strip()]
    if not clean:
        raise SchemaError("steps must be non-empty")
    if not success:
        return {
            "induced": False,
            "reason": "AWM induces only from successful trajectories",
            "ok": True,
            "note": "awm induce_workflow — skipped failure",
        }
    wid = hashlib.sha256(
        canonical_dumps({"task": task, "steps": clean[:12]}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "induced": True,
        "workflow_id": wid,
        "task": task.strip()[:120],
        "steps": clean[:12],
        "step_count": len(clean[:12]),
        "description": f"Workflow for: {task.strip()[:80]}",
        "ok": True,
        "note": "awm induce_workflow",
    }


def online_induce_gate(*, success_label: bool) -> dict[str, Any]:
    """Online AWM: only induce when evaluator marks success."""
    return {
        "allow_induce": bool(success_label),
        "success_label": bool(success_label),
        "ok": True,
        "note": "awm online_induce_gate",
    }


def workflow_memory_add_plan(
    workflows: Sequence[Mapping[str, Any]],
    new_workflow: Mapping[str, Any],
) -> dict[str, Any]:
    """Plan to add workflow if not duplicate (report-only)."""
    if not isinstance(new_workflow, Mapping):
        raise SchemaError("new_workflow mapping required")
    if not new_workflow.get("induced", True):
        return {
            "action": "SKIP",
            "reason": "not induced",
            "apply": False,
            "ok": True,
            "note": "awm workflow_memory_add_plan",
        }
    title = str(new_workflow.get("task") or "").strip().lower()
    for w in workflows:
        if not isinstance(w, Mapping):
            continue
        if str(w.get("task") or "").strip().lower() == title:
            return {
                "action": "SKIP",
                "reason": "duplicate_task",
                "existing_id": w.get("workflow_id"),
                "apply": False,
                "ok": True,
                "note": "awm workflow_memory_add_plan",
            }
    return {
        "action": "ADD",
        "workflow": dict(new_workflow),
        "apply": False,
        "ok": True,
        "note": "awm workflow_memory_add_plan",
    }


def retrieve_workflows(
    workflows: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Retrieve workflows by lexical overlap with query."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    scored: list[tuple[int, dict[str, Any]]] = []
    for w in workflows:
        if not isinstance(w, Mapping):
            continue
        blob = f"{w.get('task') or ''} {w.get('description') or ''} {' '.join(w.get('steps') or [])}"
        score = len(qtok & _tokens(blob))
        scored.append((score, dict(w)))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("workflow_id") or "")))
    hits = [w for sc, w in scored[:top_k] if sc >= 0]
    return {
        "query": query.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "awm retrieve_workflows",
    }


def workflow_step_budget(
    *,
    baseline_steps: int,
    workflow_step_count: int,
) -> dict[str, Any]:
    """Estimate step budget when guided by a workflow (AWM efficiency proxy)."""
    if baseline_steps < 1 or workflow_step_count < 1:
        raise SchemaError("steps must be >= 1")
    guided = min(baseline_steps, max(1, workflow_step_count + 1))
    saved = max(0, baseline_steps - guided)
    return {
        "baseline_steps": baseline_steps,
        "guided_steps": guided,
        "steps_saved": saved,
        "ok": True,
        "note": "awm workflow_step_budget",
    }
