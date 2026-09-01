"""ERSkill-shaped retrieval skills (stdlib; no LLM / no learned router).

Retrieval behaviors = ordered primitives. Router matches query cues to a skill.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

PRIMITIVES = frozenset(
    {
        "lexical_search",
        "follow_links",
        "freshness_assemble",
        "multi_hop",
        "residual_augment",
        "skill_rank",
    }
)

# Built-in retrieval skills (name → primitive sequence)
BUILTIN_SKILLS: dict[str, list[str]] = {
    "lexical_only": ["lexical_search"],
    "linked_context": ["lexical_search", "follow_links"],
    "current_facts": ["lexical_search", "freshness_assemble"],
    "multi_hop_graph": ["lexical_search", "multi_hop"],
    "skill_first": ["skill_rank", "lexical_search"],
    "full_evidence": [
        "lexical_search",
        "follow_links",
        "multi_hop",
        "freshness_assemble",
        "residual_augment",
    ],
}

_SKILL_CUES: dict[str, frozenset[str]] = {
    "multi_hop_graph": frozenset({"why", "how", "related", "hop", "chain", "because"}),
    "current_facts": frozenset(
        {"current", "latest", "now", "version", "update", "today"}
    ),
    "skill_first": frozenset({"skill", "workflow", "procedure", "playbook", "how-to"}),
    "linked_context": frozenset({"related", "also", "see", "linked", "depends"}),
    "full_evidence": frozenset(
        {"evidence", "complete", "all", "audit", "prove", "thorough"}
    ),
    "lexical_only": frozenset(),
}


def list_primitives() -> dict[str, Any]:
    return {
        "primitives": sorted(PRIMITIVES),
        "count": len(PRIMITIVES),
        "ok": True,
        "note": "ERSkill primitives — executable retrieval steps",
    }


def list_retrieval_skills() -> dict[str, Any]:
    skills = [
        {"name": name, "primitives": list(prims)}
        for name, prims in sorted(BUILTIN_SKILLS.items())
    ]
    return {
        "skills": skills,
        "count": len(skills),
        "ok": True,
        "note": "ERSkill built-in retrieval skills — not evolving trie",
    }


def compose_retrieval_skill(
    name: str, primitives: Sequence[str]
) -> dict[str, Any]:
    """Validate and return a custom skill composition (in-memory report)."""
    n = str(name or "").strip()
    if not n:
        raise SchemaError("name is required")
    seq = [str(p).strip() for p in primitives if p and str(p).strip()]
    if not seq:
        raise SchemaError("primitives is required")
    bad = [p for p in seq if p not in PRIMITIVES]
    if bad:
        raise SchemaError(f"unknown primitives: {bad}")
    return {
        "name": n,
        "primitives": seq,
        "ok": True,
        "note": "compose_retrieval_skill — validated schema; caller holds the skill",
    }


def route_retrieval_skill(query: str) -> dict[str, Any]:
    """Cue-based skill router (deterministic; not trained ERSkill router)."""
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    toks = set(tokenize(q))
    scored: list[tuple[int, str]] = []
    for name, cues in _SKILL_CUES.items():
        if name == "lexical_only":
            continue
        hit = len(toks & cues)
        if hit:
            scored.append((hit, name))
    if scored:
        scored.sort(key=lambda x: (-x[0], x[1]))
        chosen = scored[0][1]
    else:
        chosen = "lexical_only"
    return {
        "query": q,
        "skill": chosen,
        "primitives": list(BUILTIN_SKILLS[chosen]),
        "cue_hits": {n: h for h, n in scored},
        "ok": True,
        "note": "route_retrieval_skill — cue heuristic; not co-evolving router",
    }
