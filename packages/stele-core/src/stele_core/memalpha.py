"""Mem-α-shaped memory construction ops (stdlib; no LLM / no RL train).

Shaped by Mem-α (arXiv:2509.25911): core / episodic / semantic slots,
insert|update|delete writes, chunk processing, correctness+compression
rewards, length generalization. Proxies only — not Mem-α paper scores.
"""

from __future__ import annotations

from typing import Any

from stele_core.schema import SchemaError

SLOTS = frozenset({"core", "episodic", "semantic"})
WRITE_OPS = frozenset({"insert", "update", "delete"})


def classify_memory_slot(*, text: str, has_timestamp: bool = False) -> dict[str, Any]:
    """Route content to core / episodic / semantic (heuristic proxy)."""
    if not isinstance(text, str) or not text.strip():
        raise SchemaError("text required")
    body = text.strip().lower()
    if has_timestamp or any(
        k in body for k in ("yesterday", "today", "at ", "on monday", "last week")
    ):
        slot = "episodic"
    elif any(k in body for k in ("prefers", "is a", "works at", "lives in", "fact:")):
        slot = "semantic"
    elif len(body.split()) <= 40:
        slot = "core"
    else:
        slot = "semantic"
    return {
        "slot": slot,
        "text_preview": text.strip()[:120],
        "ok": True,
        "note": "memalpha classify_memory_slot",
    }


def memory_write_op(
    *,
    slot: str,
    op: str,
    content: str = "",
    record_id: str | None = None,
) -> dict[str, Any]:
    """
    Validate a memory write tool call.
    Core supports update only; episodic/semantic support insert/update/delete.
    """
    if slot not in SLOTS:
        raise SchemaError(f"slot must be one of {sorted(SLOTS)}")
    if op not in WRITE_OPS:
        raise SchemaError(f"op must be one of {sorted(WRITE_OPS)}")
    barriers: list[str] = []
    if slot == "core" and op != "update":
        barriers.append("core_update_only")
    if op in {"insert", "update"} and not content.strip():
        barriers.append("content_required")
    if op in {"update", "delete"} and slot != "core" and not record_id:
        barriers.append("record_id_required")
    if op == "delete" and slot == "core":
        barriers.append("core_no_delete")
    return {
        "allowed": len(barriers) == 0,
        "slot": slot,
        "op": op,
        "record_id": record_id,
        "content_preview": content.strip()[:80] if content else "",
        "barriers": barriers,
        "format_ok": len(barriers) == 0,
        "ok": True,
        "note": "memalpha memory_write_op",
    }


def process_chunk_plan(
    *,
    chunk: str,
    existing_core_chars: int = 0,
    core_max: int = 512,
) -> dict[str, Any]:
    """Plan write ops for one sequential chunk (report-only)."""
    if not isinstance(chunk, str) or not chunk.strip():
        raise SchemaError("chunk required")
    slot = classify_memory_slot(text=chunk)["slot"]
    ops: list[dict[str, Any]] = []
    if slot == "core":
        if existing_core_chars + len(chunk) > core_max:
            ops.append(
                {
                    "slot": "core",
                    "op": "update",
                    "reason": "rewrite_core_under_budget",
                }
            )
        else:
            ops.append({"slot": "core", "op": "update", "reason": "absorb_chunk"})
    else:
        ops.append({"slot": slot, "op": "insert", "reason": "new_entry"})
    return {
        "chunk_preview": chunk.strip()[:80],
        "ops": ops,
        "apply": False,
        "ok": True,
        "note": "memalpha process_chunk_plan",
    }


def compression_ratio(*, memory_chars: int, chunk_chars: int) -> dict[str, Any]:
    """r3 = 1 - lm/lc compression reward proxy."""
    if memory_chars < 0 or chunk_chars < 1:
        raise SchemaError("invalid lengths")
    ratio = max(0.0, 1.0 - (memory_chars / chunk_chars))
    return {
        "r3": round(ratio, 4),
        "memory_chars": memory_chars,
        "chunk_chars": chunk_chars,
        "ok": True,
        "note": "memalpha compression_ratio",
    }


def memalpha_reward_bundle(
    *,
    qa_correct: int,
    qa_total: int,
    tool_success: int,
    tool_total: int,
    memory_chars: int,
    chunk_chars: int,
    content_valid: int,
    content_total: int,
    beta: float = 0.5,
    gamma: float = 0.5,
) -> dict[str, Any]:
    """Combine r1–r4 shaped rewards (no GRPO)."""
    if qa_total < 1 or tool_total < 1 or content_total < 1 or chunk_chars < 1:
        raise SchemaError("totals must be >= 1")
    r1 = qa_correct / qa_total
    r2 = tool_success / tool_total
    r3 = compression_ratio(memory_chars=memory_chars, chunk_chars=chunk_chars)["r3"]
    r4 = content_valid / content_total
    # Mem-α: r2 weight fixed at 1; beta/gamma on r3/r4
    total = r1 + r2 + beta * float(r3) + gamma * r4
    return {
        "r1": round(r1, 4),
        "r2": round(r2, 4),
        "r3": r3,
        "r4": round(r4, 4),
        "total": round(total, 4),
        "ok": True,
        "note": "memalpha memalpha_reward_bundle",
    }


def length_generalization_gate(
    *,
    train_max_tokens: int,
    eval_tokens: int,
) -> dict[str, Any]:
    """Flag eval length vs training max (Mem-α: 30k train → 400k eval)."""
    if train_max_tokens < 1 or eval_tokens < 1:
        raise SchemaError("token counts must be >= 1")
    factor = eval_tokens / train_max_tokens
    return {
        "factor": round(factor, 4),
        "beyond_train": factor > 1.0,
        "extreme_ood": factor >= 10.0,
        "ok": True,
        "note": "memalpha length_generalization_gate",
    }
