"""Temporal validity helpers (C2, C6)."""

from __future__ import annotations

from typing import Any


def parse_ts(ts: str) -> str:
    return ts.replace("+00:00", "Z")


def is_valid_at(entry: dict[str, Any], as_of: str) -> bool:
    """Belief in force at as_of (superseded_at ends validity; state alone does not)."""
    t = entry["temporal"]
    if parse_ts(t["valid_from"]) > parse_ts(as_of):
        return False
    expiry = t.get("expiry")
    if expiry and parse_ts(expiry) <= parse_ts(as_of):
        return False
    superseded_at = t.get("superseded_at")
    if superseded_at and parse_ts(superseded_at) <= parse_ts(as_of):
        return False
    revoked_at = t.get("revoked_at")
    if revoked_at and parse_ts(revoked_at) <= parse_ts(as_of):
        return False
    if entry.get("state") == "quarantined":
        return False
    return True


def is_stale(entry: dict[str, Any], as_of: str, horizon: str | None) -> bool:
    if horizon is None:
        return False
    return parse_ts(entry["temporal"]["last_verified"]) < parse_ts(horizon)
