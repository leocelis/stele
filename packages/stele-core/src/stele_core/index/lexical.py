"""Pure-Python BM25 lexical index (C2, C5 — zero deps)."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from typing import Any

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class LexicalIndex:
    """Pure-Python BM25 over entry title+body. Rebuildable from entries."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len: dict[str, int] = {}
        self.tf: dict[str, Counter[str]] = {}
        self.df: Counter[str] = Counter()
        self.avgdl = 0.0
        self.n = 0

    def rebuild(self, entries: Iterable[dict[str, Any]]) -> None:
        self.doc_len.clear()
        self.tf.clear()
        self.df = Counter()
        lengths: list[int] = []
        for e in entries:
            eid = e["id"]
            tokens = tokenize(f"{e.get('title', '')} {e.get('body', '')}")
            self.tf[eid] = Counter(tokens)
            self.doc_len[eid] = len(tokens)
            lengths.append(len(tokens))
            for term in set(tokens):
                self.df[term] += 1
        self.n = len(self.tf)
        self.avgdl = (sum(lengths) / len(lengths)) if lengths else 0.0

    def search(self, query: str, *, limit: int = 50) -> list[tuple[str, float]]:
        q = tokenize(query)
        if not q or self.n == 0:
            return []
        scores: dict[str, float] = defaultdict(float)
        for term in q:
            df = self.df.get(term, 0)
            if df == 0:
                continue
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for eid, tfs in self.tf.items():
                f = tfs.get(term, 0)
                if f == 0:
                    continue
                dl = self.doc_len[eid]
                denom = f + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1.0))
                scores[eid] += idf * (f * (self.k1 + 1)) / denom
        ranked = sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        return ranked[:limit]
