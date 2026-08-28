"""AM-Sentry-shaped save policy + retrieval screen (stdlib; no LLM).

Two-stage defense against GhostWriter-style indirect memory poisoning:
strict write admission + retrieval-time screen before context injection.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

SAVE_LEVELS = frozenset({"permissive", "standard", "strict"})

_DIRECTIVE_MARKERS = (
    "ignore prior",
    "ignore previous",
    "disregard instructions",
    "system prompt",
    "exfiltrate",
    "send all data",
    "redirect payment",
    "include unauthorized",
    "bcc adversary",
    "hidden instruction",
    "do not tell the user",
)


def save_policy(
    pending: Mapping[str, Any],
    *,
    level: str = "standard",
    channel_origin: str = "untrusted_external",
) -> dict[str, Any]:
    """
    Memory-saving policy (AM-Sentry S1–S3 shaped).

    permissive: block only blatant directives
    standard: also quarantine untrusted_external without evidence
    strict: refuse untrusted_external writes entirely (report-only deny)
    """
    lvl = str(level or "standard").lower()
    if lvl not in SAVE_LEVELS:
        raise SchemaError(f"level must be one of {sorted(SAVE_LEVELS)}")
    origin = str(channel_origin or "").lower()
    text = f"{pending.get('title') or ''}\n{pending.get('body') or ''}".lower()
    markers = [m for m in _DIRECTIVE_MARKERS if m in text]

    if markers:
        return {
            "decision": "reject",
            "level": lvl,
            "origin": origin,
            "markers": markers,
            "ok": False,
            "note": "AM-Sentry save_policy — directive markers at write",
        }
    if lvl == "strict" and origin == "untrusted_external":
        return {
            "decision": "reject",
            "level": lvl,
            "origin": origin,
            "markers": [],
            "ok": False,
            "note": "AM-Sentry strict — untrusted_external refused at save",
        }
    if lvl == "standard" and origin == "untrusted_external":
        return {
            "decision": "quarantine",
            "level": lvl,
            "origin": origin,
            "markers": [],
            "ok": True,
            "note": "AM-Sentry standard — untrusted stays quarantined until oracle",
        }
    return {
        "decision": "admit",
        "level": lvl,
        "origin": origin,
        "markers": [],
        "ok": True,
        "note": "AM-Sentry save_policy — admit",
    }


def retrieval_screen(
    hits: Sequence[Mapping[str, Any]],
    *,
    context: str = "",
    block_untrusted_act: bool = True,
) -> dict[str, Any]:
    """
    Retrieval screen: drop directive / untrusted-actionable hits before inject.

    Uses metadata (authority.origin / act_class) when present; else markers.
    """
    admitted: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    ctx = str(context or "").lower()
    for h in hits:
        auth = h.get("authority") if isinstance(h.get("authority"), Mapping) else {}
        origin = str(auth.get("origin") or "").lower()
        act = str(auth.get("act_class") or "").lower()
        text = f"{h.get('title') or ''}\n{h.get('body') or ''}".lower()
        markers = [m for m in _DIRECTIVE_MARKERS if m in text]
        reason = None
        if markers:
            reason = "directive_markers"
        elif block_untrusted_act and (
            origin == "untrusted_external" or act == "none"
        ):
            # Still allow inform-only surface if act_class inform and no markers
            if act == "none" or origin == "untrusted_external":
                # If body pushes consequential patterns relative to context
                if markers or any(
                    x in text
                    for x in (
                        "pay ",
                        "wire ",
                        "send to ",
                        "exfil",
                        "bcc ",
                        "password",
                    )
                ):
                    reason = "untrusted_actionable"
        if reason:
            blocked.append(
                {
                    "id": h.get("id"),
                    "title": h.get("title"),
                    "reason": reason,
                    "markers": markers,
                }
            )
        else:
            admitted.append(
                {
                    "id": h.get("id"),
                    "title": h.get("title"),
                    "origin": origin or None,
                    "act_class": act or None,
                }
            )
    return {
        "admitted": admitted,
        "blocked": blocked,
        "admit_count": len(admitted),
        "block_count": len(blocked),
        "context_len": len(ctx),
        "ok": True,
        "note": "AM-Sentry retrieval_screen — second stage before context inject",
    }
