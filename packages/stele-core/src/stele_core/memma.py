"""MemMA-shaped memory-cycle coordination (stdlib; no LLM).

Shaped by MemMA (arXiv:2603.18718): Meta-Thinker guidance, answerability,
probe QA, in-situ verify/repair (SKIP/MERGE/INSERT). Proxies only —
not MemMA paper scores.
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


def meta_thinker_guidance(
    *,
    chunk: str,
    mode: str = "construction",
    evidence_hint: str = "",
) -> dict[str, Any]:
    """
    Meta-Thinker proxy: construction focus points or retrieval critique.
    mode: construction | retrieval
    """
    if not isinstance(chunk, str) or not chunk.strip():
        raise SchemaError("chunk required")
    if mode not in {"construction", "retrieval"}:
        raise SchemaError("mode must be construction|retrieval")
    low = chunk.lower()
    focus: list[str] = []
    if mode == "construction":
        if any(w in low for w in ("instead", "now", "changed", "correct")):
            focus.append("resolve_conflict")
        if any(w in low for w in ("also", "and", "plus")):
            focus.append("consolidate_redundancy")
        if any(w in low for w in ("prefer", "always", "never", "fact")):
            focus.append("retain_important")
        if not focus:
            focus.append("retain_important")
        return {
            "mode": mode,
            "guidance": {"focus_points": focus},
            "ok": True,
            "note": "memma meta_thinker_guidance — construction",
        }
    # retrieval critique
    eh = evidence_hint.lower()
    missing: list[str] = []
    if "when" in low and "202" not in eh:
        missing.append("temporal_scope")
    if any(w in low for w in ("who", "which")) and not eh:
        missing.append("entity_attribute")
    if not eh.strip():
        missing.append("any_evidence")
    answerable = len(missing) == 0
    return {
        "mode": mode,
        "guidance": {
            "verdict": "ANSWERABLE" if answerable else "NOT-ANSWERABLE",
            "missing": missing,
            "next_probe": missing[0] if missing else None,
        },
        "ok": True,
        "note": "memma meta_thinker_guidance — retrieval",
    }


def answerability_check(
    *,
    query: str,
    evidence_blobs: Sequence[str],
) -> dict[str, Any]:
    """ANSWERABLE if evidence tokens cover query content words."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = {t for t in _tokens(query) if len(t) > 3}
    etok: set[str] = set()
    for b in evidence_blobs:
        if isinstance(b, str):
            etok |= _tokens(b)
    covered = qtok & etok
    missing = sorted(qtok - etok)
    answerable = len(qtok) == 0 or len(covered) >= max(1, len(qtok) // 2)
    return {
        "query": query.strip(),
        "verdict": "ANSWERABLE" if answerable else "NOT-ANSWERABLE",
        "covered_count": len(covered),
        "missing": missing[:12],
        "ok": True,
        "note": "memma answerability_check",
    }


def synthesize_probe_qa(session_text: str, *, max_probes: int = 3) -> dict[str, Any]:
    """Synthesize probe QA pairs from a session chunk (heuristic)."""
    if not isinstance(session_text, str) or not session_text.strip():
        raise SchemaError("session_text required")
    if max_probes < 1:
        raise SchemaError("max_probes must be >= 1")
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", session_text.strip()) if s.strip()]
    probes: list[dict[str, Any]] = []
    for i, sent in enumerate(sentences[:max_probes]):
        # Fact probe: "What was stated about X?"
        words = [w for w in _TOKEN.findall(sent) if len(w) > 3][:4]
        topic = " ".join(words) if words else f"fact-{i}"
        q = f"What was stated about {topic}?"
        pid = hashlib.sha256(
            canonical_dumps({"q": q, "a": sent}).encode("utf-8")
        ).hexdigest()[:10]
        probes.append(
            {
                "probe_id": pid,
                "question": q[:160],
                "answer": sent[:200],
                "kind": "factual",
            }
        )
    return {
        "probe_count": len(probes),
        "probes": probes,
        "ok": True,
        "note": "memma synthesize_probe_qa",
    }


def verify_probes(
    probes: Sequence[Mapping[str, Any]],
    *,
    evidence_blobs: Sequence[str],
) -> dict[str, Any]:
    """Verify probes against evidence (lexical containment proxy)."""
    if not isinstance(probes, Sequence) or isinstance(probes, (str, bytes)):
        raise SchemaError("probes sequence required")
    joined = " ".join(b for b in evidence_blobs if isinstance(b, str)).lower()
    results: list[dict[str, Any]] = []
    fails = 0
    for p in probes:
        if not isinstance(p, Mapping):
            continue
        ans = str(p.get("answer") or "")
        atok = [t for t in _tokens(ans) if len(t) > 3][:6]
        hit = sum(1 for t in atok if t in joined)
        passed = hit >= max(1, len(atok) // 2) if atok else bool(joined)
        if not passed:
            fails += 1
        results.append(
            {
                "probe_id": p.get("probe_id"),
                "pass": passed,
                "hit_tokens": hit,
            }
        )
    return {
        "result_count": len(results),
        "fail_count": fails,
        "results": results,
        "ok": True,
        "note": "memma verify_probes",
    }


def repair_from_probes(
    probes: Sequence[Mapping[str, Any]],
    verify_results: Sequence[Mapping[str, Any]],
    *,
    existing_bodies: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Convert failed probes into SKIP/MERGE/INSERT repair actions (report-only).
    """
    if not isinstance(probes, Sequence) or isinstance(probes, (str, bytes)):
        raise SchemaError("probes sequence required")
    by_id = {
        str(p.get("probe_id")): p
        for p in probes
        if isinstance(p, Mapping) and p.get("probe_id")
    }
    existing = list(existing_bodies or [])
    repairs: list[dict[str, Any]] = []
    for r in verify_results:
        if not isinstance(r, Mapping) or r.get("pass"):
            continue
        pid = str(r.get("probe_id") or "")
        p = by_id.get(pid)
        if not p:
            continue
        fact = str(p.get("answer") or "").strip()
        ftok = _tokens(fact)
        best = 0.0
        for body in existing:
            btok = _tokens(body)
            if not ftok or not btok:
                continue
            ov = len(ftok & btok) / max(1, len(ftok | btok))
            best = max(best, ov)
        if best >= 0.7:
            action = "SKIP"
        elif best >= 0.3:
            action = "MERGE"
        else:
            action = "INSERT"
        repairs.append(
            {
                "probe_id": pid,
                "action": action,
                "fact_preview": fact[:120],
                "overlap": round(best, 4),
            }
        )
    return {
        "repair_count": len(repairs),
        "repairs": repairs,
        "apply": False,
        "ok": True,
        "note": "memma repair_from_probes — no auto-write",
    }
