"""Credential / secret reject gate for memory writes (stdlib; no LLM).

Shaped by MAPLE-Guard write Reject (credentials never persist) and PRISM-style
secret pattern detection — report-only gate; actor applies reject.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("aws_secret_assign", re.compile(r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*\S+")),
    ("generic_api_key", re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+")),
    ("bearer_jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("pem_private", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("github_pat", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai_sk", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
)


def credential_scan(text: str) -> dict[str, Any]:
    """Scan free text for credential/secret patterns."""
    blob = str(text or "")
    hits: list[dict[str, str]] = []
    for name, pat in _PATTERNS:
        for m in pat.finditer(blob):
            hits.append({"kind": name, "span": m.group(0)[:24] + ("…" if len(m.group(0)) > 24 else "")})
    return {
        "hits": hits,
        "count": len(hits),
        "ok": True,
        "note": "credguard credential_scan — pattern proxy, not entropy ML",
    }


def credential_scan_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Scan title+body (+ optional provenance.source) for credentials."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    parts = [
        str(entry.get("title") or ""),
        str(entry.get("body") or ""),
    ]
    prov = entry.get("provenance") or {}
    if isinstance(prov, Mapping):
        parts.append(str(prov.get("source") or ""))
    scan = credential_scan("\n".join(parts))
    return {
        "id": entry.get("id"),
        "hits": scan["hits"],
        "count": scan["count"],
        "ok": True,
        "note": "credguard credential_scan_entry",
    }


def credential_reject_gate(
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    """
    MAPLE-shaped write Reject: credentials must never become persistent memory.
    """
    scan = credential_scan_entry(candidate)
    if scan["count"] > 0:
        decision = "reject"
        reason = "credential_patterns"
    else:
        decision = "admit"
        reason = "no_credential_patterns"
    return {
        "decision": decision,
        "reason": reason,
        "hits": scan["hits"],
        "count": scan["count"],
        "ok": True,
        "note": "credguard credential_reject_gate — never memorize secrets",
    }


def credential_store_scan(
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """Inventory store entries that still contain credential patterns."""
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    rows: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        s = credential_scan_entry(e)
        if s["count"] <= 0:
            continue
        rows.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "state": e.get("state"),
                "count": s["count"],
                "kinds": sorted({h["kind"] for h in s["hits"]}),
            }
        )
        if len(rows) >= limit:
            break
    return {
        "suspects": rows,
        "count": len(rows),
        "ok": True,
        "note": "credguard credential_store_scan — hygiene inventory",
    }
