"""Tab-CoT proxies (stdlib; no LLM).

Shaped by Tab-CoT (arXiv:2305.17812): tabular 2D CoT with
step/subquestion/process/result columns. Proxies only.

Prefix ``tabcot_*`` — not plain CoT / Contrastive CoT (``ccot_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tabcot_header(*, columns: str) -> dict[str, Any]:
    """Emit tabular CoT header (e.g. step|subquestion|process|result)."""
    c = columns.strip()
    if not c:
        raise SchemaError("columns required")
    hid = hashlib.sha256(
        canonical_dumps({"c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "header_id": hid,
        "ok": True,
        "note": "tabcot tabcot_header",
    }


def tabcot_row(*, header_id: str, step: int) -> dict[str, Any]:
    """Fill one reasoning row in the table."""
    hid = header_id.strip()
    if not hid:
        raise SchemaError("header_id required")
    if step < 1:
        raise SchemaError("step must be >= 1")
    rid = hashlib.sha256(
        canonical_dumps({"h": hid, "s": step}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "row_id": rid,
        "step": step,
        "ok": True,
        "note": "tabcot tabcot_row",
    }


def tabcot_infer2d(*, rows: int) -> dict[str, Any]:
    """Flag 2D inference across rows and columns."""
    if rows < 1:
        raise SchemaError("rows must be >= 1")
    return {
        "rows": rows,
        "ok": True,
        "note": "tabcot tabcot_infer2d",
    }


def tabcot_extract(*, row_id: str) -> dict[str, Any]:
    """Extract final answer from the generated table."""
    rid = row_id.strip()
    if not rid:
        raise SchemaError("row_id required")
    eid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": eid,
        "ok": True,
        "note": "tabcot tabcot_extract",
    }


def tabcot_zeroshot(*, zero_shot: bool) -> dict[str, Any]:
    """Flag zero-shot Tab-CoT mode (report-only)."""
    return {
        "zero_shot": zero_shot,
        "apply": False,
        "ok": True,
        "note": "tabcot tabcot_zeroshot",
    }


def tabcot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Header → row → infer2d → extract."""
    order = ("header", "row", "infer2d", "extract")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "header"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tabcot tabcot_loop_plan",
    }
