"""MemEvolve / EvolveLab-shaped architecture meta-evolution (stdlib; no LLM).

Shaped by MemEvolve (arXiv:2512.18746 / ICML 2026): modular design space
Ω = (Encode, Store, Retrieve, Manage); dual-loop experience + architecture
evolution with diagnose-and-design. Proxies only — not EvolveLab code
search or LLM redesign.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

ENCODE_OPTIONS = frozenset(
    {"raw_trajectory", "lesson_distill", "skill_granular", "schema_ept"}
)
STORE_OPTIONS = frozenset(
    {"flat_vector", "knowledge_graph", "layered_strata", "file_ledger"}
)
RETRIEVE_OPTIONS = frozenset(
    {"lexical_topk", "graph_ppr", "dual_channel", "meta_guarded"}
)
MANAGE_OPTIONS = frozenset(
    {"append_only", "dream_consolidate", "forget_gate", "pin_reinforce"}
)

_DEFAULT_PROFILE = {
    "encode": "lesson_distill",
    "store": "file_ledger",
    "retrieve": "lexical_topk",
    "manage": "append_only",
}


def list_design_space() -> dict[str, Any]:
    """EvolveLab four-component design space catalog."""
    return {
        "encode": sorted(ENCODE_OPTIONS),
        "store": sorted(STORE_OPTIONS),
        "retrieve": sorted(RETRIEVE_OPTIONS),
        "manage": sorted(MANAGE_OPTIONS),
        "ok": True,
        "note": "memevolve list_design_space — EvolveLab Ω proxy",
    }


def architecture_profile(
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Concrete Ω = (E, U, R, G) profile within the design space."""
    profile = dict(_DEFAULT_PROFILE)
    if overrides:
        for key in ("encode", "store", "retrieve", "manage"):
            if key in overrides and overrides[key]:
                profile[key] = str(overrides[key]).strip()
    invalid = []
    if profile["encode"] not in ENCODE_OPTIONS:
        invalid.append("encode")
    if profile["store"] not in STORE_OPTIONS:
        invalid.append("store")
    if profile["retrieve"] not in RETRIEVE_OPTIONS:
        invalid.append("retrieve")
    if profile["manage"] not in MANAGE_OPTIONS:
        invalid.append("manage")
    return {
        "omega": profile,
        "valid": not invalid,
        "invalid_components": invalid,
        "ok": not invalid,
        "note": "memevolve architecture_profile",
    }


def diagnose_architecture(
    profile: Mapping[str, Any],
    *,
    feedback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Defect profile D(Ω) from fitness feedback + static heuristics.
    feedback keys: success_rate, token_cost, latency (0–1 normalized ok).
    """
    if not isinstance(profile, Mapping):
        raise SchemaError("profile mapping is required")
    omega = profile.get("omega") if "omega" in profile else profile
    if not isinstance(omega, Mapping):
        raise SchemaError("omega components required")
    fb = feedback or {}
    defects: list[dict[str, Any]] = []
    success = float(fb.get("success_rate") or 0.5)
    tokens = float(fb.get("token_cost") or 0.5)
    latency = float(fb.get("latency") or 0.5)

    if omega.get("encode") == "raw_trajectory":
        defects.append(
            {
                "component": "encode",
                "issue": "no_abstraction",
                "hint": "lesson_distill_or_skill_granular",
            }
        )
    if omega.get("store") == "flat_vector" and success < 0.6:
        defects.append(
            {
                "component": "store",
                "issue": "weak_relational_recall",
                "hint": "knowledge_graph_or_file_ledger",
            }
        )
    if omega.get("retrieve") == "lexical_topk" and success < 0.55:
        defects.append(
            {
                "component": "retrieve",
                "issue": "retrieval_miss",
                "hint": "dual_channel_or_meta_guarded",
            }
        )
    if omega.get("manage") == "append_only" and tokens > 0.7:
        defects.append(
            {
                "component": "manage",
                "issue": "unbounded_growth",
                "hint": "dream_consolidate_or_forget_gate",
            }
        )
    if latency > 0.8:
        defects.append(
            {
                "component": "retrieve",
                "issue": "high_latency",
                "hint": "narrower_budget_or_meta_guarded",
            }
        )
    return {
        "omega": dict(omega),
        "defect_count": len(defects),
        "defects": defects,
        "feedback": {
            "success_rate": success,
            "token_cost": tokens,
            "latency": latency,
        },
        "ok": True,
        "note": "memevolve diagnose_architecture — D(Ω) proxy",
    }


def propose_architecture_variants(
    profile: Mapping[str, Any],
    diagnosis: Mapping[str, Any],
    *,
    s: int = 3,
) -> dict[str, Any]:
    """Design step: S descendants by mutating defective components (report-only)."""
    if s < 1:
        raise SchemaError("s must be >= 1")
    omega = profile.get("omega") if "omega" in profile else profile
    if not isinstance(omega, Mapping):
        raise SchemaError("omega components required")
    base = {
        "encode": str(omega.get("encode") or _DEFAULT_PROFILE["encode"]),
        "store": str(omega.get("store") or _DEFAULT_PROFILE["store"]),
        "retrieve": str(omega.get("retrieve") or _DEFAULT_PROFILE["retrieve"]),
        "manage": str(omega.get("manage") or _DEFAULT_PROFILE["manage"]),
    }
    hint_map = {
        "encode": {
            "lesson_distill_or_skill_granular": ["lesson_distill", "skill_granular"],
        },
        "store": {
            "knowledge_graph_or_file_ledger": ["knowledge_graph", "file_ledger"],
        },
        "retrieve": {
            "dual_channel_or_meta_guarded": ["dual_channel", "meta_guarded"],
            "narrower_budget_or_meta_guarded": ["meta_guarded", "dual_channel"],
        },
        "manage": {
            "dream_consolidate_or_forget_gate": ["dream_consolidate", "forget_gate"],
        },
    }
    variants: list[dict[str, Any]] = []
    defects = list(diagnosis.get("defects") or [])
    for i in range(s):
        candidate = dict(base)
        mutated: list[str] = []
        if defects:
            d = defects[i % len(defects)]
            comp = str(d.get("component") or "")
            hint = str(d.get("hint") or "")
            options = (hint_map.get(comp) or {}).get(hint) or []
            if options:
                pick = options[i % len(options)]
                if pick != candidate.get(comp):
                    candidate[comp] = pick
                    mutated.append(comp)
        else:
            # exploratory: cycle manage
            alts = sorted(MANAGE_OPTIONS - {candidate["manage"]})
            if alts:
                candidate["manage"] = alts[i % len(alts)]
                mutated.append("manage")
        variants.append(
            {
                "index": i,
                "omega": candidate,
                "mutated": mutated,
                "apply": False,
            }
        )
    return {
        "parent": base,
        "variant_count": len(variants),
        "variants": variants,
        "ok": True,
        "note": "memevolve propose_architecture_variants — Design proxy; no auto-apply",
    }


def rank_architecture_fitness(
    candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Rank Ω candidates by fitness vector F = (success, -tokens, -latency).
    Each candidate: {id?, omega?, success_rate, token_cost, latency}.
    """
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        raise SchemaError("candidates sequence is required")
    scored: list[dict[str, Any]] = []
    for i, c in enumerate(candidates):
        if not isinstance(c, Mapping):
            continue
        success = float(c.get("success_rate") or 0.0)
        tokens = float(c.get("token_cost") or 1.0)
        latency = float(c.get("latency") or 1.0)
        # Higher success better; lower cost/latency better.
        score = success - 0.25 * tokens - 0.25 * latency
        scored.append(
            {
                "id": c.get("id") or f"omega:{i}",
                "omega": c.get("omega"),
                "success_rate": success,
                "token_cost": tokens,
                "latency": latency,
                "fitness": round(score, 6),
            }
        )
    scored.sort(key=lambda x: (-x["fitness"], x["id"]))
    return {
        "ranked": scored,
        "best_id": scored[0]["id"] if scored else None,
        "ok": True,
        "note": "memevolve rank_architecture_fitness — F aggregation proxy",
    }


def select_architecture_parents(
    ranked: Mapping[str, Any] | Sequence[Mapping[str, Any]],
    *,
    k: int = 1,
) -> dict[str, Any]:
    """Survivor budget K — keep top-ranked parents for next outer loop."""
    if k < 1:
        raise SchemaError("k must be >= 1")
    if isinstance(ranked, Mapping):
        rows = list(ranked.get("ranked") or [])
    elif isinstance(ranked, Sequence) and not isinstance(ranked, (str, bytes)):
        rows = list(ranked)
    else:
        raise SchemaError("ranked mapping or sequence required")
    parents = [r for r in rows if isinstance(r, Mapping)][:k]
    return {
        "k": k,
        "parent_count": len(parents),
        "parents": parents,
        "ok": True,
        "note": "memevolve select_architecture_parents — outer-loop proxy",
    }
