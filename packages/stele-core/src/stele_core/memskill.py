"""MemSkill-shaped evolvable memory skills (stdlib; no LLM).

Shaped by MemSkill (arXiv:2602.02474): skill bank (INSERT/UPDATE/DELETE/SKIP),
controller Top-K select, span-level execute plan, designer evolve from hard
cases. Proxies only — not MemSkill paper scores. No RL / LLM executor.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

PRIMITIVES = ("INSERT", "UPDATE", "DELETE", "SKIP")
_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)

_DEFAULT_SKILLS: list[dict[str, str]] = [
    {
        "skill_id": "sk:insert",
        "name": "INSERT",
        "description": "Add a new factual memory when nothing similar exists.",
        "content": "Extract novel facts; do not overwrite existing entries.",
    },
    {
        "skill_id": "sk:update",
        "name": "UPDATE",
        "description": "Revise an existing memory when new evidence corrects it.",
        "content": "Prefer supersede over silent overwrite; keep provenance.",
    },
    {
        "skill_id": "sk:delete",
        "name": "DELETE",
        "description": "Remove or revoke memory that is false or harmful.",
        "content": "Mark for revoke/purge; never silent erase without audit.",
    },
    {
        "skill_id": "sk:skip",
        "name": "SKIP",
        "description": "Skip when the span adds no durable memory value.",
        "content": "No-op when redundant, noise, or already covered.",
    },
]


def init_skill_bank(
    extra: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Initialize skill bank with four primitives (+ optional extras)."""
    skills = [dict(s) for s in _DEFAULT_SKILLS]
    for e in extra or []:
        if not isinstance(e, Mapping) or not e.get("name"):
            continue
        sid = str(e.get("skill_id") or f"sk:{e['name']}").lower()
        skills.append(
            {
                "skill_id": sid,
                "name": str(e["name"]).upper()[:32],
                "description": str(e.get("description") or "")[:160],
                "content": str(e.get("content") or "")[:400],
            }
        )
    return {
        "skill_count": len(skills),
        "skills": skills,
        "ok": True,
        "note": "memskill init_skill_bank",
    }


def span_partition(text: str, *, max_chars: int = 120) -> dict[str, Any]:
    """Partition interaction text into contiguous spans (char windows)."""
    if not isinstance(text, str):
        raise SchemaError("text string required")
    if max_chars < 20:
        raise SchemaError("max_chars must be >= 20")
    raw = text.strip()
    if not raw:
        return {"spans": [], "span_count": 0, "ok": True, "note": "memskill span_partition"}
    spans: list[dict[str, Any]] = []
    i = 0
    idx = 0
    while i < len(raw):
        chunk = raw[i : i + max_chars]
        # Prefer break on sentence
        cut = chunk.rfind(".")
        if cut > max_chars // 3:
            chunk = chunk[: cut + 1]
        spans.append({"span_id": f"span:{idx}", "text": chunk.strip(), "offset": i})
        i += max(len(chunk), 1)
        idx += 1
    return {
        "spans": spans,
        "span_count": len(spans),
        "ok": True,
        "note": "memskill span_partition",
    }


def select_skills(
    skills: Sequence[Mapping[str, Any]],
    *,
    span_text: str,
    retrieved_hint: str = "",
    top_k: int = 2,
) -> dict[str, Any]:
    """Controller proxy: Top-K skills by lexical overlap with span (+ hint)."""
    if not isinstance(span_text, str) or not span_text.strip():
        raise SchemaError("span_text required")
    if top_k < 1:
        raise SchemaError("top_k must be >= 1")
    qtok = {t.lower() for t in _TOKEN.findall(f"{span_text} {retrieved_hint}")}
    scored: list[tuple[int, dict[str, Any]]] = []
    for s in skills:
        if not isinstance(s, Mapping):
            continue
        blob = f"{s.get('name') or ''} {s.get('description') or ''} {s.get('content') or ''}"
        score = len(qtok & {t.lower() for t in _TOKEN.findall(blob)})
        # Soft priors on verbs in span
        low = span_text.lower()
        name = str(s.get("name") or "").upper()
        if name == "UPDATE" and any(w in low for w in ("correct", "instead", "now", "changed")):
            score += 3
        if name == "DELETE" and any(w in low for w in ("wrong", "false", "revoke", "harmful")):
            score += 3
        if name == "SKIP" and any(w in low for w in ("ok", "thanks", "hmm", "lol")):
            score += 2
        if name == "INSERT" and score == 0:
            score = 1  # default fallback weight
        scored.append((score, dict(s)))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("skill_id") or "")))
    chosen = [s for sc, s in scored[:top_k] if sc >= 0]
    return {
        "top_k": top_k,
        "selected": chosen,
        "selected_names": [str(s.get("name")) for s in chosen],
        "ok": True,
        "note": "memskill select_skills — controller proxy",
    }


def execute_skill_plan(
    *,
    span_text: str,
    selected_skills: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Executor proxy: emit structured memory-op intents from selected skills.
    Report-only — does not write the store.
    """
    if not isinstance(span_text, str):
        raise SchemaError("span_text required")
    ops: list[dict[str, Any]] = []
    for s in selected_skills:
        if not isinstance(s, Mapping):
            continue
        name = str(s.get("name") or "SKIP").upper()
        ops.append(
            {
                "op": name if name in PRIMITIVES else "SKIP",
                "skill_id": s.get("skill_id"),
                "rationale": str(s.get("description") or "")[:120],
                "span_preview": span_text.strip()[:80],
            }
        )
    if not ops:
        ops.append(
            {
                "op": "SKIP",
                "skill_id": "sk:skip",
                "rationale": "no skills selected",
                "span_preview": span_text.strip()[:80],
            }
        )
    return {
        "ops": ops,
        "op_count": len(ops),
        "apply": False,
        "ok": True,
        "note": "memskill execute_skill_plan — no auto-write",
    }


def record_hard_case(
    *,
    query: str,
    predicted: str = "",
    expected: str = "",
    performance: float = 0.0,
    fail: bool = True,
) -> dict[str, Any]:
    """Record a query-centric hard case for the designer buffer."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    cid = hashlib.sha256(
        canonical_dumps({"q": query, "p": predicted, "e": expected}).encode("utf-8")
    ).hexdigest()[:10]
    return {
        "case_id": cid,
        "query": query.strip()[:200],
        "predicted": predicted[:200],
        "expected": expected[:200],
        "performance": float(performance),
        "fail": bool(fail),
        "ok": True,
        "note": "memskill record_hard_case",
    }


def designer_evolve_plan(
    hard_cases: Sequence[Mapping[str, Any]],
    *,
    current_skills: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Designer proxy: from hard cases, propose refine + optional new skills.
    Report-only — does not mutate the bank.
    """
    if not isinstance(hard_cases, Sequence) or isinstance(hard_cases, (str, bytes)):
        raise SchemaError("hard_cases sequence required")
    fails = [c for c in hard_cases if isinstance(c, Mapping) and c.get("fail")]
    refine: list[dict[str, Any]] = []
    propose: list[dict[str, Any]] = []
    bank = list(current_skills) if current_skills else init_skill_bank()["skills"]
    names = {str(s.get("name") or "").upper() for s in bank if isinstance(s, Mapping)}
    if fails:
        refine.append(
            {
                "skill_id": "sk:update",
                "action": "refine",
                "change": "Strengthen UPDATE guidance for correction phrases.",
            }
        )
        if "TEMPORAL" not in names and any(
            "when" in str(c.get("query") or "").lower() for c in fails
        ):
            propose.append(
                {
                    "skill_id": "sk:temporal",
                    "name": "TEMPORAL",
                    "description": "Preserve time-anchored facts from hard temporal queries.",
                    "content": "Extract valid_from/valid_to; prefer temporal UPDATE over INSERT.",
                    "action": "add",
                }
            )
    return {
        "hard_case_count": len(fails),
        "refine": refine,
        "propose": propose,
        "apply": False,
        "ok": True,
        "note": "memskill designer_evolve_plan — no auto-write",
    }
