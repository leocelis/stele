"""Hindsight-shaped four-network memory (stdlib; no LLM).

Shaped by Hindsight (arXiv:2512.12818): world / experience / opinion /
observation networks + retain / recall / reflect ops. Proxies only —
not Hindsight paper scores.
"""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

NETWORKS = frozenset({"world", "experience", "opinion", "observation"})
_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)

_OPINION_MARKERS = (
    "i think",
    "i believe",
    "should",
    "prefer",
    "opinion",
    "seems",
    "probably",
)
_EXPERIENCE_MARKERS = (
    "i did",
    "i tried",
    "we shipped",
    "i ran",
    "my action",
    "i recommended",
)
_WORLD_MARKERS = (
    "is located",
    "was born",
    "fact:",
    "happened on",
    "api returns",
    "timeout is",
)


def _blob(entry: Mapping[str, Any]) -> str:
    return f"{entry.get('title') or ''}\n{entry.get('body') or ''}".lower()


def classify_network(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Map one entry onto Hindsight network (heuristic; no LLM)."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    text = _blob(entry)
    layer = str(entry.get("layer") or "")
    if any(m in text for m in _OPINION_MARKERS) or layer == "goal":
        net = "opinion"
    elif any(m in text for m in _EXPERIENCE_MARKERS) or layer in {
        "failure_lesson",
        "workflow",
        "skill_artifact",
    }:
        net = "experience"
    elif any(m in text for m in _WORLD_MARKERS) or layer in {"issue", "decision"}:
        # decision defaults world unless opinion markers already caught
        if any(m in text for m in ("prefer", "i think", "i believe")):
            net = "opinion"
        else:
            net = "world"
    else:
        net = "observation"
    return {
        "id": entry.get("id"),
        "network": net,
        "ok": net in NETWORKS,
        "note": "hindsight classify_network",
    }


def retain_plan(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Retain: classify entries into four networks (report-only)."""
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence required")
    by_net: dict[str, list[str]] = defaultdict(list)
    classified: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        c = classify_network(e)
        by_net[c["network"]].append(str(e.get("id")))
        classified.append(c)
    return {
        "counts": {n: len(by_net.get(n, [])) for n in sorted(NETWORKS)},
        "by_network": {k: v for k, v in sorted(by_net.items())},
        "classified": classified,
        "apply": False,
        "ok": True,
        "note": "hindsight retain_plan — no auto-write",
    }


def network_inventory(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Inventory counts per Hindsight network."""
    plan = retain_plan(entries)
    return {
        "counts": plan["counts"],
        "total": sum(plan["counts"].values()),
        "ok": True,
        "note": "hindsight network_inventory",
    }


def recall_multi_strategy(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    token_budget: int = 400,
    top_k: int = 5,
) -> dict[str, Any]:
    """
    Recall via parallel lexical strategies (semantic proxy + temporal + entity),
    fused with simple RRF ranks. No embeddings / cross-encoder.
    """
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string required")
    qtok = {t.lower() for t in _TOKEN.findall(query)}
    scored: dict[str, dict[str, Any]] = {}

    def _touch(eid: str, channel: str, score: float, entry: Mapping[str, Any]) -> None:
        row = scored.setdefault(
            eid,
            {
                "id": eid,
                "channels": {},
                "network": classify_network(entry)["network"],
                "title": entry.get("title"),
            },
        )
        row["channels"][channel] = max(float(row["channels"].get(channel, 0)), score)

    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        eid = str(e.get("id"))
        blob = _blob(e)
        etok = set(_TOKEN.findall(blob))
        overlap = len(qtok & etok)
        if overlap:
            _touch(eid, "lexical", float(overlap), e)
        temporal = e.get("temporal") if isinstance(e.get("temporal"), Mapping) else {}
        vf = str(temporal.get("valid_from") or "")
        if any(t in vf for t in qtok if t.isdigit() and len(t) == 4):
            _touch(eid, "temporal", 1.0, e)
        # entity proxy: conflict_key / title tokens
        ck = str(e.get("conflict_key") or "").lower()
        if any(t in ck for t in qtok if len(t) > 3):
            _touch(eid, "entity", 1.5, e)

    # RRF fuse
    ranked: list[tuple[float, dict[str, Any]]] = []
    for row in scored.values():
        rrf = 0.0
        for ch, sc in row["channels"].items():
            rrf += sc / (60.0)  # simplified
            _ = ch
        ranked.append((rrf, row))
    ranked.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    hits = [r for _, r in ranked[:top_k]]
    # Token budget trim by title length proxy
    kept: list[dict[str, Any]] = []
    used = 0
    for h in hits:
        cost = len(str(h.get("title") or "")) + 20
        if used + cost > token_budget and kept:
            break
        kept.append(h)
        used += cost
    return {
        "query": query.strip(),
        "hits": kept,
        "hit_count": len(kept),
        "token_budget": token_budget,
        "tokens_used": used,
        "ok": True,
        "note": "hindsight recall_multi_strategy — RRF lexical proxy",
    }


def opinion_reinforce(
    *,
    opinion_text: str,
    supporting: bool = True,
    prior_confidence: float = 0.5,
    step: float = 0.1,
) -> dict[str, Any]:
    """Reinforce or weaken opinion confidence (bounded [0,1])."""
    if not isinstance(opinion_text, str) or not opinion_text.strip():
        raise SchemaError("opinion_text required")
    c0 = max(0.0, min(1.0, float(prior_confidence)))
    delta = float(step) if supporting else -float(step)
    c1 = max(0.0, min(1.0, c0 + delta))
    return {
        "opinion": opinion_text.strip()[:200],
        "prior_confidence": round(c0, 4),
        "confidence": round(c1, 4),
        "supporting": supporting,
        "apply": False,
        "ok": True,
        "note": "hindsight opinion_reinforce",
    }


def reflect_plan(
    *,
    query: str,
    recalled: Sequence[Mapping[str, Any]],
    skepticism: int = 3,
    literalism: int = 3,
    empathy: int = 3,
    bias_strength: float = 0.5,
) -> dict[str, Any]:
    """
    Reflect: disposition-shaped response plan + optional opinion updates.
    Report-only — no LLM generation.
    """
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string required")
    for name, val in (
        ("skepticism", skepticism),
        ("literalism", literalism),
        ("empathy", empathy),
    ):
        if not 1 <= int(val) <= 5:
            raise SchemaError(f"{name} must be 1..5")
    bias = max(0.0, min(1.0, float(bias_strength)))
    facts = [r for r in recalled if isinstance(r, Mapping)]
    world_n = sum(1 for r in facts if r.get("network") == "world")
    opinion_n = sum(1 for r in facts if r.get("network") == "opinion")
    tone = []
    if skepticism >= 4:
        tone.append("require_evidence")
    if literalism >= 4:
        tone.append("quote_verbatim")
    if empathy >= 4:
        tone.append("acknowledge_user")
    if bias >= 0.7 and opinion_n:
        tone.append("lean_prior_opinion")
    return {
        "query": query.strip(),
        "disposition": {
            "skepticism": skepticism,
            "literalism": literalism,
            "empathy": empathy,
            "bias_strength": bias,
        },
        "evidence_world": world_n,
        "evidence_opinion": opinion_n,
        "tone_directives": tone,
        "cite_ids": [str(r.get("id")) for r in facts if r.get("id")][:8],
        "apply": False,
        "ok": True,
        "note": "hindsight reflect_plan — Cara proxy; no LLM",
    }
