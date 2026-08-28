"""MPBench-shaped write-channel taxonomy + source isolation (stdlib; no LLM).

Shaped by arXiv:2606.04329 — four write channels and source isolation so
untrusted external content is not treated as authenticated user input.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

WRITE_CHANNELS = frozenset(
    {"user", "oracle", "tool", "web", "agent", "unknown"}
)


def classify_write_channel(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    Map provenance.source prefix → write channel.

    Channels: user | oracle | tool | web | agent | unknown.
    """
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    prov = entry.get("provenance") or {}
    source = ""
    if isinstance(prov, Mapping):
        source = str(prov.get("source") or "").strip()
    low = source.lower()
    channel = "unknown"
    if low.startswith("user:") or low.startswith("human:"):
        channel = "user"
    elif low.startswith("oracle:") or low.startswith("ci:"):
        channel = "oracle"
    elif low.startswith("tool:") or low.startswith("mcp:"):
        channel = "tool"
    elif (
        low.startswith("web:")
        or low.startswith("http://")
        or low.startswith("https://")
        or low.startswith("url:")
    ):
        channel = "web"
    elif low.startswith("agent:") or low.startswith("llm:"):
        channel = "agent"
    return {
        "id": entry.get("id"),
        "source": source,
        "channel": channel,
        "ok": True,
        "note": "MPBench classify_write_channel — prefix taxonomy proxy",
    }


def source_isolation_gate(
    entry: Mapping[str, Any],
    *,
    deny_channels: Sequence[str] | None = None,
    quarantine_channels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Admit / quarantine / reject by write channel.

    Default: deny web; quarantine tool+agent; admit user/oracle.
    """
    deny = {str(c).lower() for c in (deny_channels if deny_channels is not None else ("web",))}
    quar = {
        str(c).lower()
        for c in (
            quarantine_channels
            if quarantine_channels is not None
            else ("tool", "agent")
        )
    }
    bad = (deny | quar) - WRITE_CHANNELS
    if bad:
        raise SchemaError(f"unknown channels: {sorted(bad)}")
    classified = classify_write_channel(entry)
    ch = str(classified["channel"])
    if ch in deny:
        decision = "reject"
    elif ch in quar:
        decision = "quarantine"
    else:
        decision = "admit"
    return {
        "id": entry.get("id"),
        "channel": ch,
        "source": classified.get("source"),
        "decision": decision,
        "ok": True,
        "note": "MPBench source_isolation_gate — untrusted ≠ user write",
    }


def write_channel_inventory(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Count entries by write channel."""
    counts: dict[str, int] = {c: 0 for c in sorted(WRITE_CHANNELS)}
    rows: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        c = classify_write_channel(e)
        ch = str(c["channel"])
        counts[ch] = counts.get(ch, 0) + 1
        rows.append({"id": e.get("id"), "channel": ch, "state": e.get("state")})
    return {
        "counts": counts,
        "entries": rows,
        "total": len(rows),
        "ok": True,
        "note": "MPBench write_channel_inventory",
    }


def channel_admit_batch(
    candidates: Sequence[Mapping[str, Any]],
    *,
    deny_channels: Sequence[str] | None = None,
    quarantine_channels: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Batch source_isolation_gate over candidate entry dicts."""
    if not candidates:
        raise SchemaError("candidates is required")
    admitted: list[dict[str, Any]] = []
    quarantined: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for c in candidates:
        g = source_isolation_gate(
            c,
            deny_channels=deny_channels,
            quarantine_channels=quarantine_channels,
        )
        row = {
            "id": g.get("id"),
            "channel": g.get("channel"),
            "decision": g.get("decision"),
        }
        if g["decision"] == "admit":
            admitted.append(row)
        elif g["decision"] == "quarantine":
            quarantined.append(row)
        else:
            rejected.append(row)
    return {
        "admitted": admitted,
        "quarantined": quarantined,
        "rejected": rejected,
        "admit_count": len(admitted),
        "quarantine_count": len(quarantined),
        "reject_count": len(rejected),
        "ok": True,
        "note": "MPBench channel_admit_batch",
    }
