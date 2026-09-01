"""TGMS-shaped bi-temporal operator planning + claim verify (stdlib; no LLM).

Typed, deterministic, bounded, cost-guarded operator plans. Claims cite
content-addressed result digests. Summaries overlapping corrected intervals
quarantine. Not the TGMS product — Stele proxies only.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

# Closed operator algebra subset (TGMS-shaped)
TGMS_OPERATORS = frozenset(
    {
        "as_of_belief",
        "lineage",
        "conflict_surface",
        "bridge_discover",
        "density_fuse",
        "evidence_plan",
        "compute_count",
        "resolve_entities",
    }
)

_COST_UNITS = {
    "as_of_belief": 5,
    "lineage": 3,
    "conflict_surface": 4,
    "bridge_discover": 8,
    "density_fuse": 4,
    "evidence_plan": 6,
    "compute_count": 1,
    "resolve_entities": 2,
}


def result_digest(payload: Any) -> dict[str, Any]:
    """Content-addressed SHA-256 digest of canonical JSON."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return {
        "digest": digest,
        "bytes": len(blob.encode("utf-8")),
        "ok": True,
        "note": "TGMS result_digest — content-addressed; excludes live tip metadata by caller choice",
    }


def operator_cost_estimate(
    steps: Sequence[Mapping[str, Any]],
    *,
    max_cost: int = 40,
) -> dict[str, Any]:
    """
    Pre-execution cost estimate for a plan DAG.

    Each step: {op, limit?} — cost = base * ceil(limit/10) for limited ops.
    """
    if not steps:
        raise SchemaError("steps is required")
    total = 0
    detail: list[dict[str, Any]] = []
    for i, step in enumerate(steps):
        op = str(step.get("op") or "").strip()
        if op not in TGMS_OPERATORS:
            raise SchemaError(f"unknown operator: {op}")
        base = _COST_UNITS[op]
        limit = int(step.get("limit") or 10)
        if limit < 1:
            raise SchemaError("limit must be >= 1")
        units = base * max(1, (limit + 9) // 10)
        total += units
        detail.append({"i": i, "op": op, "units": units, "limit": limit})
    admitted = total <= max_cost
    return {
        "total": total,
        "max_cost": max_cost,
        "admitted": admitted,
        "steps": detail,
        "ok": admitted,
        "narrow_hints": []
        if admitted
        else [
            "lower --limit on bridge_discover / evidence_plan",
            "split plan into smaller DAGs",
            f"raise max_cost above {total}",
        ],
        "note": "TGMS cost_guard — reject oversized plans before execute",
    }


def plan_static_verify(
    plan: Mapping[str, Any],
    *,
    task_ids: Sequence[str] | None = None,
    max_cost: int = 40,
) -> dict[str, Any]:
    """
    Static verifier for a small JSON DAG plan.

    plan: {steps: [{id, op, args?, refs?, limit?}], answer?: {step, field}}
    Grounding: literal ids must appear in task_ids or come from prior $ref.
    """
    if not isinstance(plan, Mapping):
        raise SchemaError("plan must be a mapping")
    steps = plan.get("steps")
    if not isinstance(steps, list) or not steps:
        raise SchemaError("plan.steps required")
    task = {str(x) for x in (task_ids or []) if x}
    violations: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    produced: set[str] = set()

    for i, step in enumerate(steps):
        if not isinstance(step, Mapping):
            violations.append({"code": "step_not_object", "i": i})
            continue
        sid = str(step.get("id") or f"s{i}")
        if sid in seen_ids:
            violations.append({"code": "duplicate_step_id", "id": sid})
        seen_ids.add(sid)
        op = str(step.get("op") or "").strip()
        if op not in TGMS_OPERATORS:
            violations.append({"code": "unknown_op", "id": sid, "op": op})
        # Acyclic refs: only prior steps
        for ref in step.get("refs") or []:
            r = str(ref)
            if r not in produced:
                violations.append(
                    {"code": "forward_or_missing_ref", "id": sid, "ref": r}
                )
        # Grounding literals
        for lit in step.get("literal_ids") or []:
            lid = str(lit)
            if lid not in task and lid not in produced:
                violations.append(
                    {
                        "code": "ungrounded_literal",
                        "id": sid,
                        "literal": lid,
                        "hint": "use resolve_entities or task input",
                    }
                )
        # Declared output field check for answer later
        outs = step.get("outputs") or ["rows", "count", "digest"]
        if not isinstance(outs, list):
            violations.append({"code": "outputs_not_list", "id": sid})
        produced.add(sid)

    # Answer spec
    answer = plan.get("answer")
    if answer is not None:
        if not isinstance(answer, Mapping):
            violations.append({"code": "answer_not_object"})
        else:
            astep = str(answer.get("step") or "")
            field = str(answer.get("field") or "")
            if astep not in produced:
                violations.append({"code": "answer_missing_step", "step": astep})
            # Find step outputs
            for step in steps:
                if str(step.get("id") or "") == astep:
                    outs = step.get("outputs") or ["rows", "count", "digest"]
                    if field and field not in outs:
                        violations.append(
                            {
                                "code": "unknown_output_field",
                                "step": astep,
                                "field": field,
                                "allowed": outs,
                            }
                        )
                    break

    cost = operator_cost_estimate(steps, max_cost=max_cost)
    if not cost.get("admitted"):
        violations.append(
            {
                "code": "cost_exceeded",
                "total": cost.get("total"),
                "max_cost": max_cost,
                "hints": cost.get("narrow_hints"),
            }
        )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
        "cost": cost,
        "step_count": len(steps),
        "ok": len(violations) == 0,
        "note": "TGMS plan_static_verify — schema/acyclicity/grounding/cost before execute",
    }


def claim_verify(
    claims: Sequence[Mapping[str, Any]],
    trace: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Verify typed claims against a content-addressed execution trace.

    claim: {kind: count|value|entity|ordering, cite: step_id, expect, field?}
    trace: {steps: {id: {digest, fields: {...}, truncated?: bool}}}
    """
    if not claims:
        raise SchemaError("claims is required")
    if not isinstance(trace, Mapping):
        raise SchemaError("trace is required")
    steps = trace.get("steps") or {}
    results: list[dict[str, Any]] = []
    for c in claims:
        kind = str(c.get("kind") or "").lower()
        cite = str(c.get("cite") or "")
        step = steps.get(cite) if isinstance(steps, Mapping) else None
        if step is None:
            results.append(
                {
                    "cite": cite,
                    "kind": kind,
                    "support": "unsupported",
                    "reason": "missing_trace_step",
                }
            )
            continue
        truncated = bool(step.get("truncated"))
        fields = step.get("fields") or {}
        field = str(c.get("field") or "count")
        expect = c.get("expect")
        observed = fields.get(field)
        support = "supported"
        reason = "match"
        if kind == "count":
            try:
                if int(observed) != int(expect):  # type: ignore[arg-type]
                    support = "contradicted"
                    reason = f"count {observed} != {expect}"
            except (TypeError, ValueError):
                support = "unsupported"
                reason = "non_numeric_count"
        elif kind == "value":
            if observed != expect:
                support = "contradicted"
                reason = f"value {observed!r} != {expect!r}"
        elif kind == "entity":
            entities = fields.get("entities") or fields.get("ids") or []
            if expect not in entities and str(expect) not in {
                str(x) for x in entities
            }:
                support = "contradicted"
                reason = f"entity {expect!r} not in cited set"
        elif kind == "ordering":
            # expect: [earlier_id, later_id]; fields.order list
            order = list(fields.get("order") or [])
            if not isinstance(expect, (list, tuple)) or len(expect) != 2:
                support = "unsupported"
                reason = "ordering expect needs [earlier, later]"
            else:
                a, b = str(expect[0]), str(expect[1])
                if a not in order or b not in order:
                    support = "unsupported"
                    reason = "ids missing from order"
                elif order.index(a) >= order.index(b):
                    support = "contradicted"
                    reason = "order inverted"
        else:
            support = "unsupported"
            reason = f"unknown kind {kind}"
        if truncated and support == "supported":
            support = "weakly_supported"
            reason = "truncated_evidence"
        results.append(
            {
                "cite": cite,
                "kind": kind,
                "support": support,
                "reason": reason,
                "observed": observed,
                "expect": expect,
            }
        )
    blocked = any(
        r["support"] in {"contradicted", "unsupported"}
        and r["kind"] in {"count", "value", "entity", "ordering"}
        for r in results
    )
    return {
        "results": results,
        "count": len(results),
        "all_supported": all(
            r["support"] in {"supported", "weakly_supported"} for r in results
        ),
        "blocked": blocked,
        "ok": not blocked,
        "note": "TGMS claim_verify — counts/values/entities/ordering vs trace; truncated ≤ weak",
    }


def summary_quarantine_scan(
    summaries: Sequence[Mapping[str, Any]],
    corrections: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Quarantine summaries whose valid-time window overlaps a correction interval.

    summary: {id, valid_from, valid_to?}
    correction: {id, valid_from, valid_to?, conflict_key?}
    """
    hits: list[dict[str, Any]] = []
    for s in summaries:
        sf = str(s.get("valid_from") or "")
        st = str(s.get("valid_to") or "9999-12-31T23:59:59Z")
        if not sf:
            continue
        for c in corrections:
            cf = str(c.get("valid_from") or "")
            ct = str(c.get("valid_to") or "9999-12-31T23:59:59Z")
            if not cf:
                continue
            # Interval overlap: [sf,st) overlaps [cf,ct)
            if sf < ct and cf < st:
                hits.append(
                    {
                        "summary_id": s.get("id"),
                        "correction_id": c.get("id"),
                        "action": "quarantine",
                        "reason": "valid_time_overlap",
                    }
                )
                break
    return {
        "quarantine": hits,
        "count": len(hits),
        "ok": True,
        "note": "TGMS summary_quarantine_scan — correction overlaps invalidate derived notes",
    }
