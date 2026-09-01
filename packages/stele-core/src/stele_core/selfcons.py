"""Self-Consistency-shaped sample-and-vote (stdlib; no LLM).

Shaped by Self-Consistency (arXiv:2203.11171): sample paths, collect
answers, majority vote, marginalize. Proxies only — not Wang et al. decoder.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sc_sample_path(*, path_idx: int, answer: str) -> dict[str, Any]:
    """Sample one reasoning path with an answer."""
    if path_idx < 0:
        raise SchemaError("path_idx must be >= 0")
    a = answer.strip()
    if not a:
        raise SchemaError("answer required")
    pid = hashlib.sha256(
        canonical_dumps({"i": path_idx, "a": a}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "path_id": pid,
        "path_idx": path_idx,
        "answer": a[:128],
        "ok": True,
        "note": "selfcons sc_sample_path",
    }


def sc_collect_answers(*, n: int) -> dict[str, Any]:
    """Count collected sampled answers."""
    if n < 0:
        raise SchemaError("n must be >= 0")
    return {
        "n": n,
        "ok": True,
        "note": "selfcons sc_collect_answers",
    }


def sc_majority_vote(*, votes: dict[str, int]) -> dict[str, Any]:
    """Pick majority answer (ties → lexicographically first)."""
    if not votes:
        raise SchemaError("votes required")
    for k, v in votes.items():
        if not str(k).strip():
            raise SchemaError("vote keys must be non-empty")
        if v < 0:
            raise SchemaError("vote counts must be >= 0")
    winner = max(sorted(votes.keys()), key=lambda k: votes[k])
    return {
        "winner": winner,
        "count": votes[winner],
        "ok": True,
        "note": "selfcons sc_majority_vote",
    }


def sc_marginalize(*, paths: int, unique_answers: int) -> dict[str, Any]:
    """Marginalize paths into unique answer set size."""
    if paths < 0 or unique_answers < 0:
        raise SchemaError("paths and unique_answers must be >= 0")
    if unique_answers > paths:
        raise SchemaError("unique_answers must be <= paths")
    return {
        "paths": paths,
        "unique_answers": unique_answers,
        "ok": True,
        "note": "selfcons sc_marginalize",
    }


def sc_temperature(*, temp: float) -> dict[str, Any]:
    """Record sampling temperature proxy (0..2)."""
    if temp < 0.0 or temp > 2.0:
        raise SchemaError("temp must be in [0, 2]")
    return {
        "temp": temp,
        "ok": True,
        "note": "selfcons sc_temperature",
    }


def sc_loop_plan(*, phase: str) -> dict[str, Any]:
    """Sample → collect → vote → marginalize."""
    order = ("sample", "collect", "vote", "marginalize")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "sample"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "selfcons sc_loop_plan",
    }
