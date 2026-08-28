"""StateFuse-shaped projection authority + correction handles (stdlib; no LLM).

Resolvers may select among surfaced candidates or abstain. They MUST NOT
rewrite SoT entry bodies — pins live in a projection overlay only.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from stele_core.execution import authority_score
from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

PROJ_DIR = "projections"
PROJ_INDEX = "projections.ndjson"

# Authority margin below which contested/symmetric sides force abstain.
_MARGIN = 0.15


def _proj_dir(root: Path) -> Path:
    return Path(root) / PROJ_DIR


def _safe_key(conflict_key: str) -> str:
    dig = hashlib.sha256(conflict_key.encode("utf-8")).hexdigest()[:16]
    return f"ck_{dig}"


def _candidates_for_key(
    entries: Iterable[Mapping[str, Any]], conflict_key: str
) -> list[dict[str, Any]]:
    key = str(conflict_key).strip()
    if not key:
        raise SchemaError("conflict_key is required")
    out: list[dict[str, Any]] = []
    for e in entries:
        if str(e.get("conflict_key") or "") != key:
            continue
        state = str(e.get("state") or "")
        if state not in {"promoted", "contested", "quarantined"}:
            continue
        score = authority_score(e)
        out.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "state": state,
                "authority": score["authority"],
                "reasons": score["reasons"],
            }
        )
    return sorted(out, key=lambda r: (-float(r["authority"]), str(r["id"])))


def project_resolve(
    entries: Iterable[Mapping[str, Any]],
    conflict_key: str,
    *,
    pinned_id: str | None = None,
) -> dict[str, Any]:
    """
    Conservative projection-time resolver (StateFuse-shaped).

    - Pin present + still a candidate → select pin
    - Single clear authority leader (margin) and no contested → select
    - Contested / close / symmetric → abstain
    Never mutates SoT.
    """
    cands = _candidates_for_key(entries, conflict_key)
    if not cands:
        return {
            "decision": "abstain",
            "reason": "no_candidates",
            "conflict_key": conflict_key,
            "winner_id": None,
            "candidates": [],
            "note": "projection resolve — SoT unchanged (StateFuse-shaped)",
        }
    by_id = {str(c["id"]): c for c in cands}
    if pinned_id and pinned_id in by_id:
        return {
            "decision": "select",
            "reason": "projection_pin",
            "conflict_key": conflict_key,
            "winner_id": pinned_id,
            "candidates": cands,
            "note": "projection pin — SoT unchanged (StateFuse-shaped)",
        }
    contested = [c for c in cands if c["state"] == "contested"]
    if contested:
        return {
            "decision": "abstain",
            "reason": "contested_open",
            "conflict_key": conflict_key,
            "winner_id": None,
            "candidates": cands,
            "note": "projection resolve — SoT unchanged (StateFuse-shaped)",
        }
    promoted = [c for c in cands if c["state"] == "promoted"]
    if not promoted:
        return {
            "decision": "abstain",
            "reason": "no_promoted",
            "conflict_key": conflict_key,
            "winner_id": None,
            "candidates": cands,
            "note": "projection resolve — SoT unchanged (StateFuse-shaped)",
        }
    if len(promoted) == 1:
        return {
            "decision": "select",
            "reason": "single_promoted",
            "conflict_key": conflict_key,
            "winner_id": promoted[0]["id"],
            "candidates": cands,
            "note": "projection resolve — SoT unchanged (StateFuse-shaped)",
        }
    top = float(promoted[0]["authority"])
    second = float(promoted[1]["authority"])
    if top - second < _MARGIN:
        return {
            "decision": "abstain",
            "reason": "symmetric_authority",
            "conflict_key": conflict_key,
            "winner_id": None,
            "candidates": cands,
            "note": "projection resolve — SoT unchanged (StateFuse-shaped)",
        }
    return {
        "decision": "select",
        "reason": "authority_margin",
        "conflict_key": conflict_key,
        "winner_id": promoted[0]["id"],
        "candidates": cands,
        "note": "projection resolve — SoT unchanged (StateFuse-shaped)",
    }


def correction_handle(
    entries: Iterable[Mapping[str, Any]],
    *,
    claim_id: str | None = None,
    claim_ref: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Dual correction handles: exact claim_id + semantic claim_ref.

    claim_ref matches conflict_key, title, or token overlap on title+body.
    """
    entries_list = list(entries)
    if claim_id:
        eid = str(claim_id).strip()
        hit = next((e for e in entries_list if e.get("id") == eid), None)
        if hit is None:
            return {
                "handle": "claim_id",
                "ok": False,
                "matches": [],
                "note": "exact id miss — try claim_ref (StateFuse-shaped)",
            }
        return {
            "handle": "claim_id",
            "ok": True,
            "matches": [
                {
                    "id": hit.get("id"),
                    "title": hit.get("title"),
                    "state": hit.get("state"),
                    "conflict_key": hit.get("conflict_key"),
                    "score": 1.0,
                }
            ],
            "note": "exact claim_id handle (StateFuse-shaped)",
        }
    ref = str(claim_ref or "").strip()
    if not ref:
        raise SchemaError("correction_handle requires claim_id or claim_ref")
    ref_l = ref.lower()
    ref_tokens = set(tokenize(ref))
    scored: list[dict[str, Any]] = []
    for e in entries_list:
        ck = str(e.get("conflict_key") or "")
        title = str(e.get("title") or "")
        body = str(e.get("body") or "")
        score = 0.0
        if ck and (ck == ref or ck.lower() == ref_l):
            score = 1.0
        elif title.lower() == ref_l:
            score = 0.95
        elif ref_l in title.lower() or ref_l in ck.lower():
            score = 0.7
        else:
            toks = set(tokenize(f"{title}\n{body}\n{ck}"))
            if ref_tokens and toks:
                overlap = len(ref_tokens & toks) / max(len(ref_tokens), 1)
                if overlap >= 0.4:
                    score = round(0.4 + 0.5 * overlap, 4)
        if score > 0:
            scored.append(
                {
                    "id": e.get("id"),
                    "title": title,
                    "state": e.get("state"),
                    "conflict_key": ck or None,
                    "score": score,
                }
            )
    scored.sort(key=lambda r: (-float(r["score"]), str(r["id"])))
    matches = scored[: max(1, int(limit))]
    return {
        "handle": "claim_ref",
        "ok": bool(matches),
        "matches": matches,
        "query": ref,
        "note": "semantic claim_ref handle — not NLI (StateFuse-shaped)",
    }


def pin_projection(
    root: Path,
    *,
    conflict_key: str,
    chosen_id: str,
    actor: str,
    ts: str,
) -> dict[str, Any]:
    """
    Record a projection-scoped choice. Does NOT rewrite entry files.
    """
    key = str(conflict_key).strip()
    eid = str(chosen_id).strip()
    actor = str(actor or "").strip()
    if not key or not eid or not actor:
        raise SchemaError("conflict_key, chosen_id, and actor are required")
    d = _proj_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    row = {
        "conflict_key": key,
        "chosen_id": eid,
        "actor": actor,
        "ts": ts,
        "note": "projection pin — SoT unchanged (StateFuse bounded authority)",
    }
    path = d / f"{_safe_key(key)}.json"
    path.write_text(canonical_dumps(row), encoding="utf-8")
    with (Path(root) / PROJ_INDEX).open("a", encoding="utf-8") as fh:
        fh.write(
            canonical_dumps(
                {"conflict_key": key, "chosen_id": eid, "actor": actor, "ts": ts}
            )
            + "\n"
        )
    return dict(row)


def get_projection_pin(root: Path, conflict_key: str) -> dict[str, Any] | None:
    path = _proj_dir(root) / f"{_safe_key(str(conflict_key).strip())}.json"
    if not path.is_file():
        return None
    return canonical_loads(path.read_text(encoding="utf-8"))


def clear_projection_pin(root: Path, conflict_key: str) -> dict[str, Any]:
    path = _proj_dir(root) / f"{_safe_key(str(conflict_key).strip())}.json"
    existed = path.is_file()
    if existed:
        path.unlink()
    return {
        "ok": True,
        "cleared": existed,
        "conflict_key": conflict_key,
        "note": "projection pin cleared — SoT unchanged",
    }


def list_projection_pins(root: Path, *, limit: int = 50) -> dict[str, Any]:
    d = _proj_dir(root)
    pins: list[dict[str, Any]] = []
    if d.is_dir():
        for path in sorted(d.glob("ck_*.json")):
            pins.append(canonical_loads(path.read_text(encoding="utf-8")))
            if len(pins) >= max(1, int(limit)):
                break
    return {
        "pins": pins,
        "count": len(pins),
        "note": "projection overlay — not SoT (StateFuse-shaped)",
    }


def normalize_claim_ref(text: str) -> str:
    """Deterministic claim_ref derivation (predicate contract proxy)."""
    t = str(text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t
