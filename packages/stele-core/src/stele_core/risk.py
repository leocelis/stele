"""Deterministic memory-injection risk heuristics (MIND / MAPLE-inspired).

Zero network / zero LLM. Markers are structural defense signals — not a
semantic classifier. Callers decide quarantine / withhold / promote policy.
"""

from __future__ import annotations

from typing import Any

# Lowercased substrings — keep short; expand only with research-backed phrases.
INJECTION_MARKERS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard previous instructions",
    "forget your previous instructions",
    "override your instructions",
    "ignore your system prompt",
    "jailbreak",
    "do not follow your policies",
    "you are now unrestricted",
)


def scan_text(text: str) -> list[str]:
    """Return matched injection markers (lowercase) found in text."""
    blob = str(text or "").lower()
    if not blob.strip():
        return []
    return [m for m in INJECTION_MARKERS if m in blob]


def scan_entry(entry: dict[str, Any]) -> dict[str, Any]:
    """Scan title+body of one entry."""
    title = str(entry.get("title") or "")
    body = str(entry.get("body") or "")
    hits = scan_text(f"{title}\n{body}")
    return {
        "id": entry.get("id"),
        "title": title,
        "state": entry.get("state"),
        "source": str((entry.get("provenance") or {}).get("source") or ""),
        "markers": hits,
        "suspect": bool(hits),
    }
