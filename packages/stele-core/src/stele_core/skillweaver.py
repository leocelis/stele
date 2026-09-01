"""SkillWeaver-shaped API skill discovery (stdlib; no LLM / no browser).

Shaped by SkillWeaver (arXiv:2504.07079): propose → practice → distill API
→ hone/test → library register / transfer. Proxies only.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

SKILL_KINDS = frozenset({"procedural", "navigational", "info_seeking"})


def propose_skill(
    *,
    description: str,
    kind: str = "procedural",
    existing: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Stage I: propose a short-horizon reusable skill description."""
    if not description.strip():
        raise SchemaError("description required")
    if kind not in SKILL_KINDS:
        raise SchemaError(f"kind must be one of {sorted(SKILL_KINDS)}")
    desc = description.strip()[:160]
    existing_l = [str(e).strip().lower() for e in (existing or [])]
    novel = desc.lower() not in existing_l
    sid = hashlib.sha256(
        canonical_dumps({"d": desc, "k": kind}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "skill_id": sid,
        "description": desc,
        "kind": kind,
        "novel": novel,
        "ok": True,
        "note": "skillweaver propose_skill",
    }


def practice_skill_run(
    *,
    skill_id: str,
    success: bool,
    steps: int = 1,
) -> dict[str, Any]:
    """Stage II practice attempt result (report-only)."""
    if not skill_id.strip():
        raise SchemaError("skill_id required")
    if steps < 1:
        raise SchemaError("steps must be >= 1")
    return {
        "skill_id": skill_id.strip()[:64],
        "success": success,
        "steps": steps,
        "ready_to_distill": success and steps <= 8,
        "ok": True,
        "note": "skillweaver practice_skill_run",
    }


def distill_skill_api(
    *,
    skill_id: str,
    description: str,
    params: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Synthesize a lightweight API signature from a practiced skill."""
    if not skill_id.strip() or not description.strip():
        raise SchemaError("skill_id and description required")
    pname = "".join(
        c if c.isalnum() else "_" for c in description.strip().lower()
    )[:40].strip("_") or "skill_fn"
    args = ["page"] + [str(p).strip() for p in (params or []) if str(p).strip()]
    sig = f"async def {pname}({', '.join(args)}): ..."
    return {
        "skill_id": skill_id.strip()[:64],
        "api_name": pname,
        "signature": sig[:120],
        "params": args,
        "apply": False,
        "ok": True,
        "note": "skillweaver distill_skill_api",
    }


def hone_skill_api(
    *,
    unit_test_pass: bool,
    static_ok: bool = True,
) -> dict[str, Any]:
    """Stage III honing: admit API only if unit test + static checks pass."""
    admit = unit_test_pass and static_ok
    return {
        "admit": admit,
        "unit_test_pass": unit_test_pass,
        "static_ok": static_ok,
        "apply": False,
        "ok": True,
        "note": "skillweaver hone_skill_api",
    }


def skill_library_register(
    *,
    api_name: str,
    library_size: int,
) -> dict[str, Any]:
    """Register API into expanding skill library (report-only)."""
    if not api_name.strip():
        raise SchemaError("api_name required")
    if library_size < 0:
        raise SchemaError("library_size must be >= 0")
    return {
        "api_name": api_name.strip()[:64],
        "new_size": library_size + 1,
        "apply": False,
        "ok": True,
        "note": "skillweaver skill_library_register",
    }


def transfer_skill_gate(
    *,
    donor_success_rate: float,
    recipient_baseline: float,
) -> dict[str, Any]:
    """Strong→weak transfer: APIs help when donor is stronger."""
    if not (0.0 <= donor_success_rate <= 1.0 and 0.0 <= recipient_baseline <= 1.0):
        raise SchemaError("rates must be in [0, 1]")
    transfer_worth = donor_success_rate > recipient_baseline + 0.05
    return {
        "transfer_worth": transfer_worth,
        "expected_lift": round(
            max(0.0, donor_success_rate - recipient_baseline), 4
        ),
        "ok": True,
        "note": "skillweaver transfer_skill_gate",
    }
