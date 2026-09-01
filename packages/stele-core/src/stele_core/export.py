"""Pack export with redact-at-export (C3, FF-7, FF-9, FF-10). Storage ≠ pack."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from stele_core.distill import extract_equipment_lines
from stele_core.schema import SchemaError, canonical_dumps, canonical_loads
from stele_core.store import SteleStore

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*\S+"),
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9\-._~+/]+=*"),
    re.compile(r"(?i)postgres(?:ql)?://\S+"),
    re.compile(r"(?i)mongodb(?:\+srv)?://\S+"),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"/Users/[^\s\"']+"),
    re.compile(r"ledger/tenants|tenants/private|workspace/ledger"),
]

AUDIENCE_TIERS = frozenset({"expert", "practitioner", "novice"})

_LAYER_BY_TIER = {
    "expert": frozenset({"goal", "decision", "failure_lesson", "skill_artifact"}),
    "practitioner": frozenset(
        {"goal", "decision", "failure_lesson", "skill_artifact", "workflow", "issue"}
    ),
    "novice": frozenset(
        {"goal", "issue", "decision", "failure_lesson", "workflow", "skill_artifact"}
    ),
}


def scan_secrets(text: str) -> list[str]:
    hits: list[str] = []
    for pat in SECRET_PATTERNS:
        if pat.search(text):
            hits.append(pat.pattern)
    return hits


def redact_text(text: str) -> str:
    out = text
    for pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out


def build_adaptation(entries: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """FF-7 adaptation operators: substitute / env assumptions / re-derive."""
    env: set[str] = set()
    substitutions: list[dict[str, str]] = []
    re_derive: list[str] = []
    for e in entries:
        for a in e.get("env_assumptions") or []:
            env.add(str(a))
        for opt in e.get("rejected_options") or []:
            substitutions.append(
                {
                    "from_rejected": str(opt)[:200],
                    "guidance": "do not replay this rejected option; re-check against current env",
                }
            )
        for line in e.get("_equipment_for_adapt") or extract_equipment_lines(
            str(e.get("body") or "")
        ):
            re_derive.append(str(line))
        if e.get("layer") in {"workflow", "skill_artifact"}:
            re_derive.append(
                f"Re-derive {e['layer']} steps for entry {e['id']} in the buyer environment"
            )
    # de-dupe re_derive preserving order
    seen: set[str] = set()
    rd: list[str] = []
    for x in re_derive:
        if x not in seen:
            seen.add(x)
            rd.append(x)
    return {
        "substitutions": substitutions,
        "env_assumptions": sorted(env),
        "re_derive": rd,
    }


def export_pack(
    store: SteleStore,
    dest: Path,
    *,
    scope: str | Sequence[str],
    audience: str,
    purpose: str,
    created_at: str,
    expiry: str,
    entry_ids: Iterable[str] | None = None,
    subject_allowlist: Sequence[str] | None = None,
) -> dict[str, Any]:
    if audience not in AUDIENCE_TIERS:
        raise SchemaError(f"audience must be one of {sorted(AUDIENCE_TIERS)}")

    scopes = {scope} if isinstance(scope, str) else set(scope)
    allowed_layers = _LAYER_BY_TIER[audience]
    allow = set(subject_allowlist) if subject_allowlist is not None else None
    dest = Path(dest)
    entries_dir = dest / "entries"
    prov_dir = dest / "provenance"
    entries_dir.mkdir(parents=True, exist_ok=True)
    prov_dir.mkdir(parents=True, exist_ok=True)

    exported: list[dict[str, Any]] = []

    candidates = list(store.iter_entries(states={"promoted"}))
    if entry_ids is not None:
        want = set(entry_ids)
        candidates = [e for e in candidates if e["id"] in want]

    for entry in candidates:
        if entry["scope"] not in scopes and entry["scope"] != "universal":
            if "universal" not in scopes:
                continue
        if entry["layer"] not in allowed_layers:
            continue
        subject = entry["provenance"].get("subject_id")
        if allow is not None and subject not in allow:
            continue

        body = redact_text(entry["body"])
        title = redact_text(entry["title"])
        equipment = extract_equipment_lines(body)
        # Recipe layer: drop equipment lines from exported body (FF-13); they land in re_derive
        for line in equipment:
            body = body.replace(line, "").strip()
        # Also strip inline equipment fragments (not full-line)
        inline_eq = re.findall(
            r"(?:\$\s+\S+(?:\s+\S+)*|npm\s+install\s+\S+|pip\s+install\s+\S+)",
            body,
            flags=re.IGNORECASE,
        )
        for frag in inline_eq:
            equipment.append(frag)
            body = body.replace(frag, "").strip()
        body = re.sub(r"\n{3,}", "\n\n", body).strip()

        pack_entry = {
            "id": entry["id"],
            "layer": entry["layer"],
            "title": title,
            "body": body,
            "scope": entry["scope"],
            "temporal": entry["temporal"],
            "env_assumptions": entry.get("env_assumptions") or [],
            "rejected_options": entry.get("rejected_options") or [],
            "links": entry.get("links") or [],
            "_equipment_for_adapt": equipment,  # stripped before write
            "provenance": {
                "agent": entry["provenance"]["agent"],
                "task": entry["provenance"]["task"],
                "environment": entry["provenance"]["environment"],
                "subject_id": entry["provenance"]["subject_id"],
                "source": entry["provenance"]["source"],
            },
        }
        blob = canonical_dumps(pack_entry)
        hits2 = scan_secrets(blob)
        if hits2:
            src = str(pack_entry["provenance"].get("source", ""))
            if scan_secrets(src):
                pack_entry["provenance"]["source"] = "source:redacted"
            blob = canonical_dumps(pack_entry)
            hits2 = scan_secrets(blob)
            if hits2:
                raise SchemaError(f"export blocked by secret/private patterns: {hits2}")

        (entries_dir / f"{entry['id']}.json").write_text(
            canonical_dumps({k: v for k, v in pack_entry.items() if not k.startswith("_")}),
            encoding="utf-8",
        )
        (prov_dir / f"{entry['id']}.json").write_text(
            canonical_dumps(
                {"entry_id": entry["id"], "source": pack_entry["provenance"]["source"]}
            ),
            encoding="utf-8",
        )
        exported.append(pack_entry)

    adaptation = build_adaptation(exported)
    (dest / "adaptation.json").write_text(canonical_dumps(adaptation), encoding="utf-8")

    if (dest / "trajectory.json").exists() or (dest / "trajectories").exists():
        raise SchemaError("pack must not contain top-level trajectories")

    report = {"entries": [e["id"] for e in exported], "subjects": sorted({e["provenance"]["subject_id"] for e in exported})}
    report_text = canonical_dumps(report)
    policy = {
        "audience_tier": audience,
        "scope": sorted(scopes),
        "purpose": purpose,
        "allowed_layers": sorted(allowed_layers),
        "subject_allowlist": sorted(allow) if allow is not None else None,
    }
    policy_digest = hashlib.sha256(canonical_dumps(policy).encode("utf-8")).hexdigest()
    manifest = {
        "pack_version": 1,
        "purpose": purpose,
        "audience_tier": audience,
        "scope": sorted(scopes),
        "created_at": created_at,
        "expiry": expiry,
        "source_store_id": store.store_id,
        "entry_count": len(exported),
        "subject_allowlist": sorted(allow) if allow is not None else None,
        "policy": policy,
        "policy_digest": policy_digest,
        "redaction_report_digest": hashlib.sha256(report_text.encode()).hexdigest(),
        "may_be_outdated": True,  # FF-8 / liability hedge
    }
    (dest / "manifest.json").write_text(canonical_dumps(manifest), encoding="utf-8")
    (dest / "redaction_report.json").write_text(report_text, encoding="utf-8")
    (dest / "policy_manifest.json").write_text(canonical_dumps(policy), encoding="utf-8")
    return manifest


def verify_pack(pack_dir: Path) -> dict[str, Any]:
    """
    Offline pack integrity (C3): stamps present, secrets clean, no top-level trajectory.
    Does not mutate the pack.
    """
    pack_dir = Path(pack_dir)
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        return {"ok": False, "errors": ["missing manifest.json"], "warnings": [], "entry_count": 0}
    try:
        manifest = canonical_loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "errors": [f"manifest unreadable: {exc}"], "warnings": [], "entry_count": 0}

    for key in ("pack_version", "purpose", "audience_tier", "created_at", "expiry", "may_be_outdated"):
        if key not in manifest:
            errors.append(f"manifest missing {key}")
    if manifest.get("audience_tier") not in AUDIENCE_TIERS:
        errors.append("invalid audience_tier")

    entries_dir = pack_dir / "entries"
    count = 0
    if not entries_dir.is_dir():
        errors.append("missing entries/")
    else:
        for path in sorted(entries_dir.glob("*.json")):
            count += 1
            try:
                raw = canonical_loads(path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{path.name}: {exc}")
                continue
            blob = f"{raw.get('title', '')}\n{raw.get('body', '')}"
            hits = scan_secrets(blob)
            if hits:
                errors.append(f"{path.name}: secret patterns remain")
            if "trajectory" in raw or "messages" in raw:
                errors.append(f"{path.name}: raw trajectory fields at pack surface")

    if (pack_dir / "provenance").is_dir():
        # Appendix is allowed; flag only if it looks like a chat dump at top level.
        for path in (pack_dir / "provenance").glob("*.json"):
            try:
                raw = canonical_loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if isinstance(raw, dict) and ("messages" in raw or "tool_calls" in raw):
                warnings.append(f"provenance/{path.name}: looks trajectory-heavy")

    return {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "entry_count": count,
        "manifest": {
            "purpose": manifest.get("purpose"),
            "audience_tier": manifest.get("audience_tier"),
            "expiry": manifest.get("expiry"),
        },
    }


def pack_seal(pack_dir: Path) -> dict[str, Any]:
    """
    Tamper-evident seal over a redacted pack (manifest + entry content digests).

    Complements store_seal — seals the *export* surface, not the live SoT.
    """
    pack_dir = Path(pack_dir)
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise SchemaError("pack_seal requires manifest.json")
    manifest_text = manifest_path.read_text(encoding="utf-8")
    manifest_digest = hashlib.sha256(manifest_text.encode("utf-8")).hexdigest()
    pairs: list[tuple[str, str]] = []
    entries_dir = pack_dir / "entries"
    if entries_dir.is_dir():
        for path in sorted(entries_dir.glob("*.json")):
            raw = canonical_loads(path.read_text(encoding="utf-8"))
            eid = str(raw.get("id") or path.stem)
            dig = hashlib.sha256(
                canonical_dumps(raw).encode("utf-8")
            ).hexdigest()
            pairs.append((eid, dig))
    pairs.sort(key=lambda x: x[0])
    material = canonical_dumps(
        {"manifest_digest": manifest_digest, "entries": pairs}
    ).encode("utf-8")
    root = hashlib.sha256(material).hexdigest()
    return {
        "algorithm": "sha256",
        "root": root,
        "manifest_digest": manifest_digest,
        "entry_count": len(pairs),
        "entries": [{"id": i, "content_digest": d} for i, d in pairs],
        "note": "pack content seal — not TRACE behavioral watermark",
    }


def verify_pack_seal(pack_dir: Path, seal: dict[str, Any]) -> dict[str, Any]:
    """Compare a prior pack seal to the on-disk pack."""
    live = pack_seal(pack_dir)
    expected = str(seal.get("root") or "")
    ok = bool(expected) and expected == live["root"]
    return {
        "ok": ok,
        "expected_root": expected or None,
        "live_root": live["root"],
        "entry_count_live": live["entry_count"],
        "entry_count_seal": seal.get("entry_count"),
        "manifest_digest_live": live["manifest_digest"],
        "manifest_digest_seal": seal.get("manifest_digest"),
    }


def verify_import(
    pack_dir: Path,
    *,
    expected_seal: dict[str, Any] | None = None,
    expected_policy_digest: str | None = None,
) -> dict[str, Any]:
    """
    Portable-Agent-Memory-shaped import gate — halt on first failure.

    Steps: structure (verify_pack) → injection markers → entry_count →
    optional pack seal → optional policy_digest. Does not write the store.
    """
    from stele_core.risk import scan_text

    pack_dir = Path(pack_dir)
    steps: list[dict[str, Any]] = []

    base = verify_pack(pack_dir)
    steps.append({"step": "structure", "ok": bool(base.get("ok")), "errors": base.get("errors")})
    if not base.get("ok"):
        return {
            "ok": False,
            "halted_at": "structure",
            "steps": steps,
            "entry_count": base.get("entry_count", 0),
            "note": "fail-closed import verify — PAM-shaped",
        }

    manifest = canonical_loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    entries_dir = pack_dir / "entries"
    inj_errors: list[str] = []
    count = 0
    for path in sorted(entries_dir.glob("*.json")):
        count += 1
        raw = canonical_loads(path.read_text(encoding="utf-8"))
        markers = scan_text(f"{raw.get('title') or ''}\n{raw.get('body') or ''}")
        if markers:
            inj_errors.append(f"{path.name}: {markers}")
    steps.append({"step": "injection_scan", "ok": not inj_errors, "errors": inj_errors})
    if inj_errors:
        return {
            "ok": False,
            "halted_at": "injection_scan",
            "steps": steps,
            "entry_count": count,
            "note": "fail-closed import verify — PAM-shaped",
        }

    expected_count = manifest.get("entry_count")
    count_ok = expected_count is None or int(expected_count) == count
    steps.append(
        {
            "step": "entry_count",
            "ok": count_ok,
            "errors": [] if count_ok else [f"manifest entry_count={expected_count} live={count}"],
        }
    )
    if not count_ok:
        return {
            "ok": False,
            "halted_at": "entry_count",
            "steps": steps,
            "entry_count": count,
            "note": "fail-closed import verify — PAM-shaped",
        }

    policy_digest = manifest.get("policy_digest")
    if expected_policy_digest is not None:
        pol_ok = str(policy_digest or "") == str(expected_policy_digest)
        steps.append(
            {
                "step": "policy_digest",
                "ok": pol_ok,
                "errors": [] if pol_ok else ["policy_digest mismatch"],
            }
        )
        if not pol_ok:
            return {
                "ok": False,
                "halted_at": "policy_digest",
                "steps": steps,
                "entry_count": count,
                "note": "fail-closed import verify — PAM-shaped",
            }
    elif policy_digest and (pack_dir / "policy_manifest.json").is_file():
        live_pol = canonical_loads(
            (pack_dir / "policy_manifest.json").read_text(encoding="utf-8")
        )
        live_dig = hashlib.sha256(canonical_dumps(live_pol).encode("utf-8")).hexdigest()
        pol_ok = live_dig == str(policy_digest)
        steps.append(
            {
                "step": "policy_manifest",
                "ok": pol_ok,
                "errors": [] if pol_ok else ["policy_manifest.json diverges from digest"],
            }
        )
        if not pol_ok:
            return {
                "ok": False,
                "halted_at": "policy_manifest",
                "steps": steps,
                "entry_count": count,
                "note": "fail-closed import verify — PAM-shaped",
            }

    if expected_seal is not None:
        seal_rep = verify_pack_seal(pack_dir, expected_seal)
        steps.append(
            {
                "step": "pack_seal",
                "ok": bool(seal_rep.get("ok")),
                "errors": [] if seal_rep.get("ok") else ["pack seal root mismatch"],
            }
        )
        if not seal_rep.get("ok"):
            return {
                "ok": False,
                "halted_at": "pack_seal",
                "steps": steps,
                "entry_count": count,
                "note": "fail-closed import verify — PAM-shaped",
            }

    return {
        "ok": True,
        "halted_at": None,
        "steps": steps,
        "entry_count": count,
        "policy_digest": policy_digest,
        "note": "fail-closed import verify — PAM-shaped",
    }


def hydrate_pack(
    pack_dir: Path,
    *,
    written_at: str,
    default_scope: str | None = None,
) -> list[dict[str, Any]]:
    """
    Load a redacted pack into ADD-ready payloads (OP-12 scoped import).

    Does not write the store — caller ADDs (and promotes with external evidence).
    Pack bodies are treated as distilled Insights; provenance.agent becomes
    ``pack-hydrate`` so the receiving writer cannot self-promote.
    """
    pack_dir = Path(pack_dir)
    manifest_path = pack_dir / "manifest.json"
    if not manifest_path.exists():
        raise SchemaError("pack missing manifest.json")
    entries_dir = pack_dir / "entries"
    if not entries_dir.is_dir():
        raise SchemaError("pack missing entries/")

    from stele_core.schema import validate_entry

    out: list[dict[str, Any]] = []
    for path in sorted(entries_dir.glob("*.json")):
        raw = canonical_loads(path.read_text(encoding="utf-8"))
        scope = raw.get("scope") or default_scope or "project:imported"
        payload = {
            "layer": raw["layer"],
            "title": raw["title"],
            "body": raw["body"],
            "scope": scope,
            "temporal": {
                "valid_from": written_at,
                "last_verified": written_at,
                "expiry": raw.get("temporal", {}).get("expiry"),
            },
            "env_assumptions": raw.get("env_assumptions") or [],
            "rejected_options": raw.get("rejected_options") or [],
            "links": raw.get("links") or [],
            "provenance": {
                "agent": "pack-hydrate",
                "task": "foreign-pack-import",
                "environment": "hydrate",
                "subject_id": raw.get("provenance", {}).get("subject_id") or "imported",
                "source": f"pack:{raw.get('id', path.stem)}",
                "written_at": written_at,
            },
        }
        # Drop empty expiry
        if not payload["temporal"].get("expiry"):
            payload["temporal"].pop("expiry", None)
        if payload["layer"] not in {"workflow", "skill_artifact"}:
            payload.pop("env_assumptions", None)
        out.append(validate_entry(payload))
    return out
