"""Optional semantic vector index — embedder is caller-supplied (C1, C5)."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from typing import Any


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class SemanticIndex:
    def __init__(self) -> None:
        self.vectors: dict[str, list[float]] = {}

    def rebuild(self, entries: Iterable[dict[str, Any]], embedder: Any) -> None:
        items = list(entries)
        self.vectors.clear()
        if not items:
            return
        texts = [f"{e.get('title', '')} {e.get('body', '')}" for e in items]
        vectors = embedder.embed(texts)
        for e, vec in zip(items, vectors):
            self.vectors[e["id"]] = list(vec)

    def search(
        self, query_vec: Sequence[float], *, limit: int = 50
    ) -> list[tuple[str, float]]:
        scored = [(eid, cosine(query_vec, vec)) for eid, vec in self.vectors.items()]
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored[:limit]
