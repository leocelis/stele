"""MemArchitect-shaped context triage & bid (stdlib; no LLM).

Entries compete for limited reader budget slots. Report-only — never deletes.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from stele_core.execution import authority_score
from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError
from stele_core.worth import memory_worth


def context_bid(
    entries: Iterable[Mapping[str, Any]],
    query: str,
    *,
    slots: int = 5,
    now: str | None = None,
) -> dict[str, Any]:
    """
    Triage & bid: score candidates for context window admission.

    bid = 0.4*relevance + 0.3*authority + 0.3*worth  (deterministic proxies)
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    n = max(1, int(slots))
    q_tokens = set(tokenize(q))
    bids: list[dict[str, Any]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        title = str(e.get("title") or "")
        body = str(e.get("body") or "")
        toks = set(tokenize(f"{title}\n{body}"))
        if q_tokens and toks:
            relevance = len(q_tokens & toks) / max(len(q_tokens), 1)
        else:
            relevance = 0.0
        if relevance <= 0 and q.lower() not in f"{title}\n{body}".lower():
            continue
        if q.lower() in f"{title}\n{body}".lower() and relevance < 0.2:
            relevance = max(relevance, 0.35)
        auth = authority_score(e)["authority"]
        worth = float(memory_worth(e).get("worth") or 0.0)
        bid = round(0.4 * relevance + 0.3 * auth + 0.3 * worth, 4)
        bids.append(
            {
                "id": e.get("id"),
                "title": title,
                "state": e.get("state"),
                "bid": bid,
                "relevance": round(relevance, 4),
                "authority": auth,
                "worth": worth,
            }
        )
    bids.sort(key=lambda r: (-float(r["bid"]), str(r["id"])))
    admitted = bids[:n]
    rejected = bids[n:]
    return {
        "query": q,
        "slots": n,
        "admitted": admitted,
        "rejected": rejected,
        "admitted_count": len(admitted),
        "rejected_count": len(rejected),
        "now": now,
        "note": "MemArchitect triage & bid proxy — report only, no auto-delete",
    }
