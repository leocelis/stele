"""ConsistencyGate-shaped write-time admission (stdlib; no LLM).

Paper uses K LLM soft-support scores. Stele proxy: lexical support against
existing promoted store + pending context blob — admit only above τ.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

DEFAULT_TAU = 0.35


def support_score(
    candidate: Mapping[str, Any],
    *,
    context: str = "",
    store_entries: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Soft 0–1 support for candidate fact from context + store overlap.

    Not LLM self-consistency — deterministic Jaccard against evidence text.
    """
    cand = f"{candidate.get('title') or ''}\n{candidate.get('body') or ''}".strip()
    if not cand:
        raise SchemaError("candidate title/body required")
    ctok = set(tokenize(cand))
    if not ctok:
        raise SchemaError("candidate must tokenize")

    ctx = str(context or "").strip()
    ctx_tok = set(tokenize(ctx)) if ctx else set()
    ctx_overlap = len(ctok & ctx_tok) / max(len(ctok), 1) if ctx_tok else 0.0

    store_best = 0.0
    store_id = None
    for e in store_entries or []:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        etok = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
        if not etok:
            continue
        # Support from store = how much of candidate is already evidenced
        ov = len(ctok & etok) / max(len(ctok), 1)
        if ov > store_best:
            store_best = ov
            store_id = e.get("id")

    # Prefer context support when present; blend with store corroboration
    if ctx_tok:
        score = round(0.7 * ctx_overlap + 0.3 * store_best, 4)
    else:
        score = round(store_best, 4)

    return {
        "score": score,
        "context_overlap": round(ctx_overlap, 4),
        "store_overlap": round(store_best, 4),
        "store_id": store_id,
        "token_count": len(ctok),
        "ok": True,
        "note": "ConsistencyGate support_score — lexical proxy, not K LLM votes",
    }


def consistency_admit(
    candidate: Mapping[str, Any],
    *,
    context: str = "",
    store_entries: Sequence[Mapping[str, Any]] | None = None,
    tau: float = DEFAULT_TAU,
    check_contradiction: bool = True,
) -> dict[str, Any]:
    """
    Write-time admission: admit | quarantine | reject.

    Reject on injection markers / empty. Quarantine when below τ or
    strong contradiction with promoted tip under same conflict_key.
    """
    if not (0 <= tau <= 1):
        raise SchemaError("tau must be in [0, 1]")
    body = f"{candidate.get('title') or ''}\n{candidate.get('body') or ''}".lower()
    poison = (
        "ignore prior instructions" in body
        or "dump secrets" in body
        or "jailbreak" in body
    )
    if poison:
        return {
            "decision": "reject",
            "reason": "lexical_injection",
            "score": 0.0,
            "tau": tau,
            "ok": False,
            "note": "ConsistencyGate reject — injection markers",
        }

    support = support_score(
        candidate, context=context, store_entries=store_entries
    )
    score = float(support["score"])

    contradiction = None
    if check_contradiction and candidate.get("conflict_key"):
        ck = str(candidate.get("conflict_key"))
        ctok = set(tokenize(f"{candidate.get('title')}\n{candidate.get('body')}"))
        for e in store_entries or []:
            if e.get("state") != "promoted":
                continue
            if str(e.get("conflict_key") or "") != ck:
                continue
            etok = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
            # High token divergence under same key ⇒ contradiction risk
            jacc = len(ctok & etok) / max(len(ctok | etok), 1)
            if jacc < 0.25 and len(ctok) >= 3:
                contradiction = {
                    "against_id": e.get("id"),
                    "jaccard": round(jacc, 4),
                }
                break

    if contradiction is not None and score < tau + 0.15:
        return {
            "decision": "quarantine",
            "reason": "contradiction_low_support",
            "score": score,
            "tau": tau,
            "support": support,
            "contradiction": contradiction,
            "ok": False,
            "note": "ConsistencyGate quarantine — conflict_key clash + weak support",
        }

    if score >= tau:
        return {
            "decision": "admit",
            "reason": "support_above_tau",
            "score": score,
            "tau": tau,
            "support": support,
            "contradiction": contradiction,
            "ok": True,
            "note": "ConsistencyGate admit — lexical support ≥ τ",
        }

    return {
        "decision": "quarantine",
        "reason": "support_below_tau",
        "score": score,
        "tau": tau,
        "support": support,
        "ok": False,
        "note": "ConsistencyGate quarantine — below τ (Stele ADD still lands quarantined)",
    }
