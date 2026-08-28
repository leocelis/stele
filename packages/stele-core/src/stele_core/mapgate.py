"""Quipu write-gate + MAP-Graph action risk gate (stdlib; no LLM).

Write gate evaluates pending post-state predicates before ADD lands.
Action risk gate: Allow / Block / Reverify / AskUser / Redact.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.graph import path_trust
from stele_core.schema import SchemaError

RISK_LEVELS = frozenset({"low", "medium", "high"})
GATE_VERDICTS = frozenset(
    {"Allow", "Block", "Reverify", "AskUser", "Redact"}
)

# MAP-Graph-shaped trust thresholds by risk
_TRUST_THETA = {"low": 0.30, "medium": 0.60, "high": 0.85}


def write_gate(
    pending: Mapping[str, Any],
    existing: Iterable[Mapping[str, Any]],
    *,
    require_scope: bool = True,
    block_universal_without_pin: bool = True,
) -> dict[str, Any]:
    """
    Quipu-shaped gate: no fact enters except through predicates on pending post-state.

    Does not write — caller decides. Fail-closed on missing scope / poison markers.
    """
    failures: list[str] = []
    title = str(pending.get("title") or "").strip()
    body = str(pending.get("body") or "").strip()
    scope = str(pending.get("scope") or "").strip()
    if not title or not body:
        failures.append("incomplete_content")
    if require_scope and not scope:
        failures.append("missing_scope")
    if block_universal_without_pin and scope == "universal":
        usage = pending.get("usage") or {}
        if not usage.get("pinned"):
            failures.append("universal_requires_pin")
    # Conflict: same conflict_key already contested
    ck = str(pending.get("conflict_key") or "").strip()
    if ck:
        for e in existing:
            if str(e.get("conflict_key") or "") != ck:
                continue
            if e.get("state") == "contested":
                failures.append(f"conflict_key_contested:{ck}")
                break
            if e.get("state") == "promoted" and str(e.get("title") or "") == title:
                failures.append(f"duplicate_title_under_key:{ck}")
                break
    # Injection markers (lightweight)
    blob = f"{title}\n{body}".lower()
    for marker in ("ignore prior instructions", "system prompt", "jailbreak"):
        if marker in blob:
            failures.append(f"injection_marker:{marker}")
            break
    ok = len(failures) == 0
    return {
        "ok": ok,
        "allowed": ok,
        "failures": failures,
        "pending_title": title or None,
        "note": "Quipu write-gate proxy — predicates on pending post-state; does not write",
    }


def action_risk_gate(
    entries: Iterable[Mapping[str, Any]],
    supporting_ids: Sequence[str],
    *,
    risk: str = "medium",
    trusted_sources: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    MAP-Graph risk-sensitive gate before irreversible action.

    Ordered rules (simplified):
    1. high risk + any revoked/archived/affected support → Block
    2. medium/high + no surviving support → Reverify (AskUser if high)
    3. untrusted lineage path → Block/Redact/Reverify by risk
    4. max path_trust < θ(risk) → Redact/Reverify/AskUser else Allow
    """
    level = str(risk or "medium").strip().lower()
    if level not in RISK_LEVELS:
        raise SchemaError(f"risk must be one of {sorted(RISK_LEVELS)}")
    theta = _TRUST_THETA[level]
    pool = {str(e.get("id")): e for e in entries}
    trusts: list[float] = []
    reasons: list[str] = []
    surviving = 0
    for eid in supporting_ids:
        e = pool.get(str(eid))
        if e is None:
            reasons.append(f"missing:{eid}")
            continue
        state = str(e.get("state") or "")
        if state in {"revoked", "archived", "expired", "superseded"}:
            reasons.append(f"affected:{eid}:{state}")
            if level == "high":
                return {
                    "verdict": "Block",
                    "risk": level,
                    "theta": theta,
                    "reasons": reasons,
                    "trusts": trusts,
                    "ok": False,
                    "note": "MAP-Graph action risk gate — high+affected → Block",
                }
            continue
        if state not in {"promoted", "contested"}:
            reasons.append(f"ineligible:{eid}:{state}")
            continue
        surviving += 1
        try:
            pt = path_trust(
                list(pool.values()),
                str(eid),
                trusted_sources=trusted_sources,
            )
            trusts.append(float(pt.get("path_trust") or 0))
        except Exception:  # noqa: BLE001
            trusts.append(0.0)
            reasons.append(f"trust_unavailable:{eid}")

    if surviving == 0 and level in {"medium", "high"}:
        verdict = "AskUser" if level == "high" else "Reverify"
        return {
            "verdict": verdict,
            "risk": level,
            "theta": theta,
            "reasons": reasons or ["no_surviving_support"],
            "trusts": trusts,
            "ok": False,
            "note": "MAP-Graph action risk gate",
        }

    max_trust = max(trusts) if trusts else 0.0
    if max_trust < theta:
        if level == "high":
            verdict = "AskUser"
        elif level == "medium":
            verdict = "Reverify"
        else:
            verdict = "Redact"
        return {
            "verdict": verdict,
            "risk": level,
            "theta": theta,
            "max_trust": round(max_trust, 6),
            "reasons": reasons,
            "trusts": [round(t, 6) for t in trusts],
            "ok": False,
            "note": "MAP-Graph action risk gate — below θ",
        }

    return {
        "verdict": "Allow",
        "risk": level,
        "theta": theta,
        "max_trust": round(max_trust, 6),
        "reasons": reasons,
        "trusts": [round(t, 6) for t in trusts],
        "ok": True,
        "note": "MAP-Graph action risk gate — Allow",
    }
