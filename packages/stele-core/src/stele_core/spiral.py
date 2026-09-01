"""SPIRAL-shaped self-play RAE (stdlib; no LLM / no games).

Shaped by SPIRAL (arXiv:2506.24119): zero-sum self-play curriculum,
role-conditioned advantage estimation (RAE), multi-game transfer patterns.
Proxies only — not SPIRAL paper scores.
"""

from __future__ import annotations

from typing import Any

from stele_core.schema import SchemaError

GAMES = frozenset({"tictactoe", "kuhn_poker", "negotiation"})
PATTERNS = frozenset(
    {"case_by_case", "expected_value", "pattern_recognition"}
)


def spiral_self_play_match(
    *,
    game: str,
    role: str,
    won: bool,
) -> dict[str, Any]:
    """Record a self-play match outcome for a role in a zero-sum game."""
    if game not in GAMES:
        raise SchemaError(f"game must be one of {sorted(GAMES)}")
    r = role.strip()
    if not r:
        raise SchemaError("role required")
    return {
        "game": game,
        "role": r[:40],
        "won": won,
        "ok": True,
        "note": "spiral spiral_self_play_match",
    }


def spiral_rae_advantage(
    *,
    reward: float,
    role_baseline: float,
) -> dict[str, Any]:
    """Role-conditioned advantage: reward − role baseline (RAE)."""
    adv = reward - role_baseline
    return {
        "advantage": round(adv, 4),
        "reward": reward,
        "role_baseline": role_baseline,
        "ok": True,
        "note": "spiral spiral_rae_advantage",
    }


def spiral_baseline_ema(
    *,
    baseline: float,
    reward: float,
    decay: float = 0.95,
) -> dict[str, Any]:
    """EMA update of role baseline: decay·baseline + (1−decay)·reward."""
    if not (0.0 <= decay <= 1.0):
        raise SchemaError("decay must be in [0, 1]")
    new_b = decay * baseline + (1.0 - decay) * reward
    return {
        "baseline": round(new_b, 4),
        "ok": True,
        "note": "spiral spiral_baseline_ema",
    }


def spiral_transfer_pattern(
    *,
    pattern: str,
) -> dict[str, Any]:
    """Cognitive pattern that transfers from games to reasoning."""
    if pattern not in PATTERNS:
        raise SchemaError(f"pattern must be one of {sorted(PATTERNS)}")
    return {
        "pattern": pattern,
        "ok": True,
        "note": "spiral spiral_transfer_pattern",
    }


def spiral_opponent_strength(
    *,
    self_elo: float,
    opponent_elo: float,
) -> dict[str, Any]:
    """Adaptive curriculum: opponent should be near or above self."""
    gap = opponent_elo - self_elo
    challenging = gap >= -50.0
    return {
        "gap": round(gap, 2),
        "challenging": challenging,
        "ok": True,
        "note": "spiral spiral_opponent_strength",
    }


def spiral_multi_game_plan(
    *,
    phase: str,
) -> dict[str, Any]:
    """Multi-game round: match → RAE → baseline → transfer."""
    order = ("match", "rae", "baseline", "transfer")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "match"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "spiral spiral_multi_game_plan",
    }
