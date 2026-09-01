"""NEMORI-shaped prediction-error distillation (stdlib; no LLM).

Shaped by NEMORI / What Deserves Memory (ACL 2026): episodic narrative
integration + semantic distillation via prediction error (unexpected
info deserves memory). Management-agnostic; report-only consolidate.
Proxies only — not NEMORI paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def integrate_episodic_narrative(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Episodic Memory Integration: raw → narrative episode + cue."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    title = str(entry.get("title") or "").strip()
    body = str(entry.get("body") or "").strip()
    temporal = entry.get("temporal") if isinstance(entry.get("temporal"), Mapping) else {}
    t = temporal.get("valid_from") or entry.get("created_at")
    narrative = title
    if body:
        first = body.split(".")[0].strip()
        if first and first.lower() not in title.lower():
            narrative = f"{title}: {first}" if title else first
    narrative = narrative[:240]
    cue = str(entry.get("conflict_key") or title or "episode").strip()[:80]
    return {
        "id": entry.get("id"),
        "narrative": narrative,
        "cue": cue,
        "reference_time": t,
        "ok": True,
        "note": "nemori integrate_episodic_narrative — representation prior proxy",
    }


def anticipatory_schema(
    entries: Sequence[Mapping[str, Any]],
    *,
    cue: str,
) -> dict[str, Any]:
    """
    Anticipatory schema from existing store: what we 'expect' given cue
    (lexical centroid of matching entries — no LLM predict).
    """
    if not isinstance(cue, str) or not cue.strip():
        raise SchemaError("cue string required")
    qtok = _tokens(cue)
    expected_parts: list[str] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        blob = f"{e.get('title') or ''}\n{e.get('body') or ''}"
        if qtok & _tokens(blob):
            expected_parts.append(str(e.get("title") or blob.split(".")[0])[:80])
        if len(expected_parts) >= 5:
            break
    schema = " | ".join(expected_parts) if expected_parts else "(no prior)"
    return {
        "cue": cue.strip(),
        "anticipated": schema,
        "prior_count": len(expected_parts),
        "ok": True,
        "note": "nemori anticipatory_schema — prediction proxy",
    }


def prediction_error_distill(
    *,
    actual: str,
    anticipated: str,
) -> dict[str, Any]:
    """
    Distill insights = tokens/phrases in actual not covered by anticipated.
    Prediction error → what deserves memory.
    """
    if not isinstance(actual, str) or not isinstance(anticipated, str):
        raise SchemaError("actual and anticipated strings required")
    a_tok = _tokens(actual)
    e_tok = _tokens(anticipated)
    novel = sorted(a_tok - e_tok)
    # Drop ultra-common stop-ish short tokens
    novel = [t for t in novel if len(t) > 3][:24]
    error_ratio = len(novel) / max(1, len(a_tok))
    return {
        "novel_tokens": novel,
        "novel_count": len(novel),
        "error_ratio": round(error_ratio, 4),
        "deserves_memory": error_ratio >= 0.25 or len(novel) >= 3,
        "ok": True,
        "note": "nemori prediction_error_distill — predictability prior proxy",
    }


def deserves_memory_gate(
    *,
    actual: str,
    anticipated: str,
    min_error_ratio: float = 0.25,
    min_novel: int = 3,
) -> dict[str, Any]:
    """Gate: admit to memory only if prediction error is material."""
    distill = prediction_error_distill(actual=actual, anticipated=anticipated)
    admit = distill["error_ratio"] >= min_error_ratio or distill["novel_count"] >= min_novel
    return {
        "admit": admit,
        "error_ratio": distill["error_ratio"],
        "novel_count": distill["novel_count"],
        "novel_tokens": distill["novel_tokens"][:12],
        "min_error_ratio": min_error_ratio,
        "min_novel": min_novel,
        "ok": True,
        "note": "nemori deserves_memory_gate",
    }


def distill_batch_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    prior_entries: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Batch NEMORI pipeline: narrative → anticipate from prior → distill.
    Report-only; does not write.
    """
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence required")
    prior = list(prior_entries) if prior_entries is not None else []
    results: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        narr = integrate_episodic_narrative(e)
        # Anticipate from prior only (not including current)
        ant = anticipatory_schema(prior, cue=narr["cue"])
        gate = deserves_memory_gate(
            actual=narr["narrative"], anticipated=ant["anticipated"]
        )
        insight_id = hashlib.sha256(
            canonical_dumps(
                {"id": e.get("id"), "novel": gate["novel_tokens"][:8]}
            ).encode("utf-8")
        ).hexdigest()[:10]
        results.append(
            {
                "entry_id": e.get("id"),
                "narrative": narr["narrative"],
                "admit": gate["admit"],
                "novel_tokens": gate["novel_tokens"],
                "insight_id": insight_id if gate["admit"] else None,
            }
        )
        # Growing prior for sequential distillation
        prior.append(e)
    admit_n = sum(1 for r in results if r["admit"])
    return {
        "result_count": len(results),
        "admit_count": admit_n,
        "skip_count": len(results) - admit_n,
        "results": results,
        "apply": False,
        "ok": True,
        "note": "nemori distill_batch_plan — management-agnostic; no auto-write",
    }
