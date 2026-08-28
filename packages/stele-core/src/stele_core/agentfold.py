"""AgentFold-shaped proactive context folding (stdlib; no LLM).

Shaped by AgentFold (arXiv:2510.24699): context as cognitive workspace,
granular condensation vs deep consolidation fold commands, working vs
long-term split. Proxies only — not AgentFold paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def agentfold_workspace_split(
    *,
    working_tokens: int,
    long_term_blocks: int,
) -> dict[str, Any]:
    """Split context into immediate working memory vs long-term blocks."""
    if working_tokens < 0 or long_term_blocks < 0:
        raise SchemaError("counts must be >= 0")
    return {
        "working_tokens": working_tokens,
        "long_term_blocks": long_term_blocks,
        "ok": True,
        "note": "agentfold agentfold_workspace_split",
    }


def agentfold_fold_command(
    *,
    mode: str,
    range_start: int,
    step_t: int,
) -> dict[str, Any]:
    """Fold command: granular (k=t-1) or deep (k<t-1)."""
    if mode not in ("granular", "deep"):
        raise SchemaError("mode must be granular or deep")
    if step_t < 1:
        raise SchemaError("step_t must be >= 1")
    if range_start < 0 or range_start >= step_t:
        raise SchemaError("range_start must be in [0, step_t)")
    if mode == "granular" and range_start != step_t - 1:
        raise SchemaError("granular requires range_start == step_t - 1")
    if mode == "deep" and range_start >= step_t - 1:
        raise SchemaError("deep requires range_start < step_t - 1")
    fid = hashlib.sha256(
        canonical_dumps({"m": mode, "k": range_start, "t": step_t}).encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return {
        "fold_id": fid,
        "mode": mode,
        "range_start": range_start,
        "step_t": step_t,
        "ok": True,
        "note": "agentfold agentfold_fold_command",
    }


def agentfold_granular_condense(
    *,
    last_step_tokens: int,
    target_tokens: int,
) -> dict[str, Any]:
    """Granular condensation: compress only the latest step."""
    if last_step_tokens < 0 or target_tokens < 1:
        raise SchemaError("last_step_tokens >= 0 and target_tokens >= 1")
    compressed = min(last_step_tokens, target_tokens)
    return {
        "compressed_tokens": compressed,
        "ok": True,
        "note": "agentfold agentfold_granular_condense",
    }


def agentfold_deep_consolidate(
    *,
    blocks_merged: int,
) -> dict[str, Any]:
    """Deep consolidation: merge multiple summary blocks into one."""
    if blocks_merged < 2:
        raise SchemaError("blocks_merged must be >= 2")
    return {
        "blocks_merged": blocks_merged,
        "result_blocks": 1,
        "ok": True,
        "note": "agentfold agentfold_deep_consolidate",
    }


def agentfold_context_budget(
    *,
    turns: int,
    tokens: int,
    soft_cap: int = 7000,
) -> dict[str, Any]:
    """Budget gate: stay under soft cap after many turns."""
    if turns < 0 or tokens < 0 or soft_cap < 1:
        raise SchemaError("turns/tokens >= 0 and soft_cap >= 1")
    under_cap = tokens <= soft_cap
    return {
        "under_cap": under_cap,
        "turns": turns,
        "tokens": tokens,
        "ok": True,
        "note": "agentfold agentfold_context_budget",
    }


def agentfold_loop_plan(*, phase: str) -> dict[str, Any]:
    """Act → fold → split → budget."""
    order = ("act", "fold", "split", "budget")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "act"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "agentfold agentfold_loop_plan",
    }
