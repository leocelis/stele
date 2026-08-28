"""MemGen-shaped generative latent memory (stdlib; no LLM / no LoRA).

Shaped by MemGen (arXiv:2509.24704): memory trigger + weaver, interwoven
reason↔memory, emergent faculties (planning/procedural/working).
Proxies only — not MemGen paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

FACULTIES = frozenset({"planning", "procedural", "working"})


def memory_trigger_decide(
    *,
    at_boundary: bool,
    uncertainty: float,
    threshold: float = 0.4,
) -> dict[str, Any]:
    """Metacognitive trigger: INVOKE only at boundaries when uncertainty high."""
    if not (0.0 <= uncertainty <= 1.0):
        raise SchemaError("uncertainty must be in [0, 1]")
    if not (0.0 <= threshold <= 1.0):
        raise SchemaError("threshold must be in [0, 1]")
    invoke = at_boundary and uncertainty >= threshold
    return {
        "decision": "INVOKE" if invoke else "SKIP",
        "invoke": invoke,
        "ok": True,
        "note": "memgen memory_trigger_decide",
    }


def weave_latent_memory(
    *,
    stimulus: str,
    token_budget: int = 4,
) -> dict[str, Any]:
    """Weaver synthesizes a fixed-length latent memory proxy from stimulus."""
    body = stimulus.strip()
    if not body:
        raise SchemaError("stimulus required")
    if token_budget < 1:
        raise SchemaError("token_budget must be >= 1")
    digest = hashlib.sha256(
        canonical_dumps({"s": body}).encode("utf-8")
    ).hexdigest()
    tokens = [digest[i : i + 4] for i in range(0, token_budget * 4, 4)][
        :token_budget
    ]
    return {
        "latent_tokens": tokens,
        "token_count": len(tokens),
        "ok": True,
        "note": "memgen weave_latent_memory",
    }


def interweave_cycle_plan(
    *,
    step: str,
) -> dict[str, Any]:
    """Reason ↔ memory cycle: generate → monitor → invoke → weave → resume."""
    order = ("generate", "monitor", "invoke", "weave", "resume")
    if step not in order:
        raise SchemaError(f"step must be one of {list(order)}")
    idx = order.index(step)
    nxt = order[idx + 1] if idx + 1 < len(order) else "generate"
    return {
        "step": step,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memgen interweave_cycle_plan",
    }


def faculty_classify(
    *,
    faculty: str,
) -> dict[str, Any]:
    """Emergent faculty label: planning | procedural | working."""
    if faculty not in FACULTIES:
        raise SchemaError(f"faculty must be one of {sorted(FACULTIES)}")
    return {
        "faculty": faculty,
        "ok": True,
        "note": "memgen faculty_classify",
    }


def weaver_only_update_gate(
    *,
    reasoner_frozen: bool,
    weaver_updated: bool,
) -> dict[str, Any]:
    """Knowledge writes go to weaver only; reasoner stays frozen."""
    ok_policy = reasoner_frozen and weaver_updated
    return {
        "allow": ok_policy,
        "reasoner_frozen": reasoner_frozen,
        "weaver_updated": weaver_updated,
        "apply": False,
        "ok": True,
        "note": "memgen weaver_only_update_gate",
    }


def sparse_invoke_penalty(
    *,
    invoke_count: int,
    expected_rate: float = 0.2,
    lambda_penalty: float = 0.1,
) -> dict[str, Any]:
    """Penalty when invoke rate exceeds expected (sparse trigger)."""
    if invoke_count < 0:
        raise SchemaError("invoke_count must be >= 0")
    if not (0.0 <= expected_rate <= 1.0) or lambda_penalty < 0:
        raise SchemaError("expected_rate in [0,1] and lambda_penalty >= 0")
    # Proxy: treat invoke_count as excess over a unit-length horizon
    excess = max(0.0, float(invoke_count) - expected_rate)
    penalty = round(lambda_penalty * excess, 4)
    return {
        "penalty": penalty,
        "ok": True,
        "note": "memgen sparse_invoke_penalty",
    }
