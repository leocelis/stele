"""Distillation / anti-pattern gates (OP-2, FF-2, FF-3) — keep junk out of ADD."""

from __future__ import annotations

import re
from collections.abc import Mapping

from stele_core.schema import SchemaError

_SPEAKER = re.compile(
    r"^(?:user|assistant|human|ai|agent|system)\s*[:\-—]",
    re.IGNORECASE | re.MULTILINE,
)
_TOOL_TRAJECTORY = re.compile(
    r"(?:tool_call|function_call|<\|tool\||Action:\s|Observation:\s)",
    re.IGNORECASE,
)
_EQUIPMENT_LINE = re.compile(
    r"^\s*(?:\$\s+|sudo\s+|npm\s+install|pip\s+install|yarn\s+add|docker\s+run|curl\s+|wget\s+)",
    re.IGNORECASE | re.MULTILINE,
)

# Insight-level bodies should stay short; raw dumps are long and turn-structured.
MAX_BODY_CHARS = 4000
MAX_SPEAKER_TURNS = 6
MAX_TOOL_MARKERS = 3


def assert_distilled_entry(entry: Mapping[str, object]) -> None:
    """
    Reject raw-transcript / trajectory-shaped content at ADD (OP-2, FF-2, FF-3).

    Writers must submit Insight/workflow distillates — never session dumps.
    """
    body = str(entry.get("body") or "")
    title = str(entry.get("title") or "")
    layer = str(entry.get("layer") or "")

    if len(body) > MAX_BODY_CHARS:
        raise SchemaError(
            f"body exceeds {MAX_BODY_CHARS} chars — distill before ADD (FF-2); "
            "raw transcripts are not durable ledger content"
        )

    speaker_hits = _SPEAKER.findall(body)
    if len(speaker_hits) >= MAX_SPEAKER_TURNS:
        raise SchemaError(
            "body looks like a multi-turn transcript (speaker labels) — "
            "distill to Insight/failure_lesson before ADD (OP-2)"
        )

    tool_hits = _TOOL_TRAJECTORY.findall(body)
    if len(tool_hits) >= MAX_TOOL_MARKERS:
        raise SchemaError(
            "body looks like a tool trajectory dump — store Insight/workflow only; "
            "keep raw trajectory as provenance.source pointer (FF-3)"
        )

    # Equipment-layer command recipes are not Insight (FF-13); workflow may list
    # assumptions, but a body that is mostly shell lines is rejected.
    if layer in {"failure_lesson", "decision", "goal", "issue"}:
        eq = _EQUIPMENT_LINE.findall(body)
        if len(eq) >= 3:
            raise SchemaError(
                f"{layer} body looks like equipment-layer shell commands (FF-13); "
                "record the principle, put commands in workflow with env_assumptions"
            )

    if title and body and title.strip() == body.strip():
        raise SchemaError("title and body identical — expand the distilled lesson")


def extract_equipment_lines(body: str) -> list[str]:
    """Lines that look like environment-specific commands (candidates for re_derive)."""
    return [ln.strip() for ln in body.splitlines() if _EQUIPMENT_LINE.match(ln)]
