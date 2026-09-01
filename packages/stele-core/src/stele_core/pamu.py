"""PAMU preference-aware memory update (stdlib; no LLM).

Shaped by Preference-Aware Memory Update (PAMU), arXiv:2510.09720 /
ACL 2026 Findings: SW + EMA fusion, divergence change detection,
preference prompt formatting. Proxies only — not LoCoMo paper scores.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

PREFERENCE_DIMS = (
    "tone",
    "length",
    "emotion",
    "density",
    "formality",
)

_DEFAULT_BETA = 0.8
_DEFAULT_LAMBDA = 0.5
_DEFAULT_WINDOW = 3
_DEFAULT_DELTA = 0.35


def extract_preference_signal(text: str) -> dict[str, Any]:
    """Heuristic 5-D preference observation from user text (0–1 scalars)."""
    if not isinstance(text, str):
        raise SchemaError("text string is required")
    t = text.lower()
    # tone: casual/humorous → low formal; professional → high
    tone = 0.5
    if any(w in t for w in ("joke", "funny", "lol", "humor", "casual")):
        tone = 0.2
    if any(w in t for w in ("formal", "professional", "please ensure")):
        tone = 0.85
    length = 0.5
    if any(w in t for w in ("brief", "short", "concise", "tl;dr", "one sentence")):
        length = 0.2
    if any(w in t for w in ("detailed", "long", "thorough", "in depth", "comprehensive")):
        length = 0.85
    emotion = 0.5
    if any(w in t for w in ("angry", "frustrated", "upset")):
        emotion = 0.2
    if any(w in t for w in ("happy", "excited", "grateful", "thanks")):
        emotion = 0.8
    density = 0.5
    if any(w in t for w in ("high-level", "overview", "summary only")):
        density = 0.25
    if any(w in t for w in ("dense", "citations", "numbers", "specifics", "data")):
        density = 0.85
    formality = tone  # correlated default; adjust
    if "hey" in t or "yo " in t:
        formality = min(formality, 0.25)
    if "dear" in t or "sincerely" in t:
        formality = max(formality, 0.8)
    vec = {
        "tone": tone,
        "length": length,
        "emotion": emotion,
        "density": density,
        "formality": formality,
    }
    return {
        "vector": vec,
        "ok": True,
        "note": "pamu extract_preference_signal — lexical proxy",
    }


def _mean(vals: Sequence[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _var(vals: Sequence[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return sum((x - m) ** 2 for x in vals) / len(vals)


def sliding_window_average(
    observations: Sequence[Mapping[str, float]],
    *,
    window: int = _DEFAULT_WINDOW,
) -> dict[str, Any]:
    """SW_t over recent preference vectors."""
    if window < 1:
        raise SchemaError("window must be >= 1")
    if not observations:
        raise SchemaError("observations required")
    recent = list(observations)[-window:]
    sw: dict[str, float] = {}
    for d in PREFERENCE_DIMS:
        sw[d] = round(_mean([float(o.get(d, 0.5)) for o in recent]), 6)
    return {
        "sw": sw,
        "window": window,
        "n": len(recent),
        "ok": True,
        "note": "pamu sliding_window_average",
    }


def ema_update(
    previous: Mapping[str, float] | None,
    observation: Mapping[str, float],
    *,
    beta: float = _DEFAULT_BETA,
) -> dict[str, Any]:
    """EMA_t = β·EMA_{t-1} + (1-β)·p_t."""
    if not 0.0 < beta < 1.0:
        raise SchemaError("beta must be in (0,1)")
    prev = previous or {}
    ema: dict[str, float] = {}
    for d in PREFERENCE_DIMS:
        p = float(observation.get(d, 0.5))
        e0 = float(prev.get(d, p))
        ema[d] = round(beta * e0 + (1.0 - beta) * p, 6)
    return {
        "ema": ema,
        "beta": beta,
        "ok": True,
        "note": "pamu ema_update",
    }


def fuse_preference(
    sw: Mapping[str, float],
    ema: Mapping[str, float],
    *,
    lam: float = _DEFAULT_LAMBDA,
) -> dict[str, Any]:
    """ŵ = λ·SW + (1-λ)·EMA."""
    if not 0.0 <= lam <= 1.0:
        raise SchemaError("lam must be in [0,1]")
    fused: dict[str, float] = {}
    for d in PREFERENCE_DIMS:
        fused[d] = round(
            lam * float(sw.get(d, 0.5)) + (1.0 - lam) * float(ema.get(d, 0.5)),
            6,
        )
    return {
        "fused": fused,
        "lambda": lam,
        "ok": True,
        "note": "pamu fuse_preference",
    }


def preference_change_detect(
    sw: Mapping[str, float],
    ema: Mapping[str, float],
    *,
    sw_history: Sequence[Mapping[str, float]] | None = None,
    ema_history: Sequence[Mapping[str, float]] | None = None,
    delta: float = _DEFAULT_DELTA,
) -> dict[str, Any]:
    """
    C_t^(d) = |SW-EMA| / (ε + sqrt(Var(SW)+Var(EMA))); trigger when C > δ.
    """
    eps = 1e-6
    dims: dict[str, Any] = {}
    triggered: list[str] = []
    for d in PREFERENCE_DIMS:
        delta_d = abs(float(sw.get(d, 0.5)) - float(ema.get(d, 0.5)))
        sw_vals = [float(h.get(d, 0.5)) for h in (sw_history or [sw])]
        ema_vals = [float(h.get(d, 0.5)) for h in (ema_history or [ema])]
        denom = eps + math.sqrt(_var(sw_vals) + _var(ema_vals))
        c = delta_d / denom if denom else delta_d
        # When history is thin, fall back to absolute divergence.
        if len(sw_vals) < 2 and len(ema_vals) < 2:
            c = delta_d
        fire = c >= delta
        if fire:
            triggered.append(d)
        dims[d] = {
            "delta": round(delta_d, 6),
            "score": round(c, 6),
            "triggered": fire,
        }
    return {
        "dimensions": dims,
        "triggered": triggered,
        "should_update": bool(triggered),
        "delta_threshold": delta,
        "ok": True,
        "note": "pamu preference_change_detect — C_t proxy",
    }


def format_preference_prompt(fused: Mapping[str, float]) -> dict[str, Any]:
    """Map fused vector to interpretable NL preference descriptors."""

    def band(v: float, low: str, mid: str, high: str) -> str:
        if v < 0.34:
            return low
        if v < 0.67:
            return mid
        return high

    lines = [
        f"tone: {band(float(fused.get('tone', 0.5)), 'casual/humorous', 'neutral', 'formal')}",
        f"length: {band(float(fused.get('length', 0.5)), 'concise', 'balanced', 'detailed')}",
        f"emotion: {band(float(fused.get('emotion', 0.5)), 'subdued', 'neutral', 'warm')}",
        f"density: {band(float(fused.get('density', 0.5)), 'high-level', 'moderate', 'information-dense')}",
        f"formality: {band(float(fused.get('formality', 0.5)), 'informal', 'semi-formal', 'formal')}",
    ]
    return {
        "prompt": "User preference profile:\n- " + "\n- ".join(lines),
        "descriptors": lines,
        "ok": True,
        "note": "pamu format_preference_prompt",
    }


def preference_update_plan(
    observations: Sequence[Mapping[str, Any] | str],
    *,
    window: int = _DEFAULT_WINDOW,
    beta: float = _DEFAULT_BETA,
    lam: float = _DEFAULT_LAMBDA,
    delta: float = _DEFAULT_DELTA,
) -> dict[str, Any]:
    """Full PAMU pipeline over a sequence of turn observations (report-only)."""
    if not isinstance(observations, Sequence) or isinstance(observations, (str, bytes)):
        raise SchemaError("observations sequence is required")
    if not observations:
        raise SchemaError("at least one observation required")

    vectors: list[dict[str, float]] = []
    for obs in observations:
        if isinstance(obs, str):
            vectors.append(extract_preference_signal(obs)["vector"])
        elif isinstance(obs, Mapping):
            if "vector" in obs and isinstance(obs["vector"], Mapping):
                vectors.append({d: float(obs["vector"].get(d, 0.5)) for d in PREFERENCE_DIMS})
            else:
                vectors.append({d: float(obs.get(d, 0.5)) for d in PREFERENCE_DIMS})
        else:
            raise SchemaError("observation must be str or mapping")

    ema_state: dict[str, float] | None = None
    ema_hist: list[dict[str, float]] = []
    sw_hist: list[dict[str, float]] = []
    steps: list[dict[str, Any]] = []
    for i, vec in enumerate(vectors):
        sw_rep = sliding_window_average(vectors[: i + 1], window=window)
        ema_rep = ema_update(ema_state, vec, beta=beta)
        ema_state = ema_rep["ema"]
        fuse = fuse_preference(sw_rep["sw"], ema_state, lam=lam)
        sw_hist.append(sw_rep["sw"])
        ema_hist.append(dict(ema_state))
        change = preference_change_detect(
            sw_rep["sw"],
            ema_state,
            sw_history=sw_hist,
            ema_history=ema_hist,
            delta=delta,
        )
        prompt = format_preference_prompt(fuse["fused"])
        steps.append(
            {
                "t": i + 1,
                "sw": sw_rep["sw"],
                "ema": dict(ema_state),
                "fused": fuse["fused"],
                "change": {
                    "should_update": change["should_update"],
                    "triggered": change["triggered"],
                },
                "prompt": prompt["prompt"] if change["should_update"] else None,
            }
        )

    last = steps[-1]
    return {
        "steps": steps,
        "final_fused": last["fused"],
        "updates_triggered": sum(1 for s in steps if s["change"]["should_update"]),
        "final_prompt": format_preference_prompt(last["fused"])["prompt"],
        "apply": False,
        "ok": True,
        "note": "pamu preference_update_plan — modular update proxy; no auto-write",
    }
