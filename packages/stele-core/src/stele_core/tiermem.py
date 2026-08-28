"""TierMem-shaped provenance-linked summary/raw evidence allocation (stdlib).

Summary-first retrieval → sufficiency gate → escalate to linked raw logs →
verified write-back. Deterministic router — not LoCoMo scores / learned miss detector.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

RAW_DIR = "raw_pages"
TIER_TAG_SUMMARY = "tiermem:summary"
TIER_TAG_RAW = "tiermem:raw"

# Query tokens that suggest raw detail is required (deterministic miss cues).
_DETAIL_CUES = frozenset(
    {
        "exact",
        "quote",
        "verbatim",
        "timestamp",
        "when",
        "date",
        "id",
        "uuid",
        "checksum",
        "hash",
        "log",
        "trace",
        "stack",
        "error",
        "code",
    }
)


def _raw_dir(root: Path) -> Path:
    return Path(root) / RAW_DIR


def put_raw_page(
    root: Path,
    text: str,
    *,
    actor: str,
    ts: str,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Immutable Tier-2 raw page (content-addressed). Independent of entry SoT.
    """
    actor = str(actor or "").strip()
    blob = str(text or "")
    if not actor:
        raise SchemaError("actor is required")
    if not blob.strip():
        raise SchemaError("raw page text must be non-empty")
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    d = _raw_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"{digest}.txt"
    if not path.is_file():
        path.write_text(blob, encoding="utf-8")
    meta_path = d / f"{digest}.json"
    row = {
        "digest": digest,
        "bytes": len(blob.encode("utf-8")),
        "actor": actor,
        "ts": ts,
        "meta": dict(meta or {}),
        "note": "TierMem Tier-2 immutable raw page",
    }
    meta_path.write_text(canonical_dumps(row), encoding="utf-8")
    return row


def get_raw_page(root: Path, digest: str) -> dict[str, Any] | None:
    d = _raw_dir(root)
    path = d / f"{digest}.txt"
    meta_path = d / f"{digest}.json"
    if not path.is_file():
        return None
    meta = {}
    if meta_path.is_file():
        meta = canonical_loads(meta_path.read_text(encoding="utf-8"))
    return {
        "digest": digest,
        "text": path.read_text(encoding="utf-8"),
        "meta": meta,
    }


def raw_digests_from_entry(entry: Mapping[str, Any]) -> list[str]:
    """Collect Tier-2 digests from attachment:/raw: link refs."""
    out: list[str] = []
    for lnk in entry.get("links") or []:
        ref = str(lnk.get("ref") or "")
        kind = str(lnk.get("kind") or "")
        dig = str(lnk.get("digest") or "")
        if dig and dig not in out:
            out.append(dig)
        for prefix in ("attachment:", "raw:"):
            if ref.startswith(prefix):
                d = ref[len(prefix) :]
                if d and d not in out:
                    out.append(d)
        if kind in {"artifact", "raw"} and dig and dig not in out:
            out.append(dig)
    return out


def is_summary_entry(entry: Mapping[str, Any]) -> bool:
    tags = {str(t).lower() for t in (entry.get("cue_tags") or [])}
    if TIER_TAG_SUMMARY in tags:
        return True
    if TIER_TAG_RAW in tags:
        return False
    # Heuristic: short body + has raw links → summary
    body = str(entry.get("body") or "")
    return bool(raw_digests_from_entry(entry)) and len(body) < 800


def sufficiency_gate(
    query: str,
    hits: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Deterministic TierMem miss detector (proxy for learned router).

    MISS when: no hits, contested flags, detail cues without raw links,
    query digits absent from summary bodies, or very low token overlap.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    q_tokens = set(tokenize(q))
    detail = bool(q_tokens & _DETAIL_CUES) or bool(re.search(r"\d", q))
    reasons: list[str] = []
    if not hits:
        return {
            "decision": "miss",
            "reasons": ["no_hits"],
            "escalate_ids": [],
            "note": "TierMem sufficiency — escalate or abstain",
        }
    escalate_ids: list[str] = []
    for h in hits:
        eid = str(h.get("id") or "")
        body = str(h.get("body") or "")
        state = str(h.get("state") or "")
        if state == "contested":
            reasons.append(f"contested:{eid}")
            escalate_ids.append(eid)
            continue
        raws = raw_digests_from_entry(h)
        b_tokens = set(tokenize(body))
        overlap = (
            len(q_tokens & b_tokens) / max(len(q_tokens), 1) if q_tokens else 0.0
        )
        digits = set(re.findall(r"\d+", q))
        body_digits = set(re.findall(r"\d+", body))
        if digits and not digits.issubset(body_digits):
            reasons.append(f"digit_gap:{eid}")
            escalate_ids.append(eid)
        elif detail and not raws:
            reasons.append(f"detail_without_raw:{eid}")
            escalate_ids.append(eid)
        elif overlap < 0.15:
            reasons.append(f"low_overlap:{eid}")
            escalate_ids.append(eid)
        elif detail and raws:
            # detail query with linked raw available → prefer escalate for fidelity
            reasons.append(f"detail_prefer_raw:{eid}")
            escalate_ids.append(eid)
    # unique preserve order
    seen: set[str] = set()
    esc: list[str] = []
    for i in escalate_ids:
        if i and i not in seen:
            seen.add(i)
            esc.append(i)
    decision = "miss" if reasons else "hit"
    # If only detail_prefer_raw reasons and we have raws — still miss (escalate)
    return {
        "decision": decision,
        "reasons": reasons,
        "escalate_ids": esc,
        "hit_count": len(hits),
        "note": "TierMem sufficiency proxy — not a trained miss detector",
    }


def escalate(
    root: Path,
    entries: Iterable[Mapping[str, Any]],
    summary_ids: Sequence[str],
    *,
    max_pages: int = 8,
) -> dict[str, Any]:
    """Load linked Tier-2 raw pages for summary entry ids."""
    by_id = {str(e.get("id")): e for e in entries}
    pages: list[dict[str, Any]] = []
    missing: list[str] = []
    for sid in summary_ids:
        e = by_id.get(str(sid))
        if e is None:
            missing.append(str(sid))
            continue
        for dig in raw_digests_from_entry(e):
            page = get_raw_page(root, dig)
            if page is None:
                # Fallback: attachments dir
                att = Path(root) / "attachments" / dig
                if att.is_file():
                    pages.append(
                        {
                            "digest": dig,
                            "text": att.read_text(encoding="utf-8", errors="replace"),
                            "via_entry": sid,
                            "source": "attachments",
                        }
                    )
                else:
                    missing.append(dig)
                continue
            pages.append(
                {
                    "digest": dig,
                    "text": page["text"],
                    "via_entry": sid,
                    "source": "raw_pages",
                }
            )
            if len(pages) >= max(1, int(max_pages)):
                break
        if len(pages) >= max(1, int(max_pages)):
            break
    return {
        "pages": pages,
        "page_count": len(pages),
        "missing": missing,
        "ok": len(pages) > 0,
        "note": "TierMem escalate — linked raw only (bounded)",
    }


def summary_entry_template(
    *,
    title: str,
    body: str,
    scope: str,
    raw_digests: Sequence[str],
    provenance: Mapping[str, Any],
    temporal: Mapping[str, Any],
    conflict_key: str | None = None,
) -> dict[str, Any]:
    """Build a Tier-1 summary entry dict with raw provenance links (caller ADDs)."""
    links = [
        {"kind": "artifact", "ref": f"raw:{d}", "digest": d} for d in raw_digests
    ]
    entry: dict[str, Any] = {
        "layer": "failure_lesson",
        "title": title,
        "body": body,
        "scope": scope,
        "temporal": dict(temporal),
        "provenance": dict(provenance),
        "links": links,
        "cue_tags": [TIER_TAG_SUMMARY],
        "memory_role": "claim",
    }
    if conflict_key:
        entry["conflict_key"] = conflict_key
    return entry
