"""Operator CLI for Stele stores (v1 surface)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stele_core import Stele, __version__
from stele_core.schema_json import entry_json_schema


def _print(obj: object) -> None:
    print(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False))


def _open(path: str, *, store_id: str | None, now: str | None, create: bool = True) -> Stele:
    return Stele.open(Path(path), store_id=store_id, now=now, create=create)


def cmd_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=args.store_id, now=args.now)
    _print({"ok": True, "store": str(Path(args.store).resolve()), "store_id": stele.store.store_id})
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    schema = entry_json_schema()
    if args.out:
        Path(args.out).write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        print(args.out)
    else:
        _print(schema)
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.verify()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_doctor(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.doctor(now=args.now)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_stats(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.stats(now=args.now))
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.snapshot(args.dest, actor=args.actor, ts=args.now))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    slices = stele.search(
        args.query,
        consumer_scope=args.scope,
        budget=args.budget,
        stale_policy=args.stale_policy,
    )
    _print(slices)
    return 0


def cmd_attach(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    data = Path(args.file).read_bytes()
    _print(
        stele.attach(
            data,
            entry_id=args.entry_id,
            actor=args.actor,
            ts=args.now,
            kind=args.kind,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stele",
        description=f"Stele v{__version__} — governed experiential-memory ledger CLI",
    )
    p.add_argument("--version", action="version", version=f"stele {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_store(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("store", help="Path to store root")
        sp.add_argument("--now", default=None, help="Caller clock ISO-8601 (required for writes)")
        sp.add_argument("--store-id", default=None)

    s = sub.add_parser("init", help="Create an empty store")
    add_store(s)
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("schema", help="Emit entry JSON Schema 2020-12")
    s.add_argument("--out", default=None, help="Write to file instead of stdout")
    s.set_defaults(func=cmd_schema)

    s = sub.add_parser("verify", help="Store integrity check")
    add_store(s)
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("doctor", help="verify + stats + contested + stale")
    add_store(s)
    s.set_defaults(func=cmd_doctor)

    s = sub.add_parser("stats", help="Store health counts")
    add_store(s)
    s.set_defaults(func=cmd_stats)

    s = sub.add_parser("snapshot", help="Cold-copy SoT to dest directory")
    add_store(s)
    s.add_argument("dest", help="Empty or new destination directory")
    s.add_argument("--actor", default="cli")
    s.set_defaults(func=cmd_snapshot)

    s = sub.add_parser("search", help="Search promoted lessons")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", required=True)
    s.add_argument("--budget", type=int, default=400)
    s.add_argument("--stale-policy", default="flag", choices=("flag", "withhold"))
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("attach", help="Content-address an artifact; optional LINK")
    add_store(s)
    s.add_argument("file", help="Path to bytes to attach")
    s.add_argument("--entry-id", default=None)
    s.add_argument("--actor", default="cli")
    s.add_argument("--kind", default="artifact")
    s.set_defaults(func=cmd_attach)

    s = sub.add_parser("purge", help="Provenance recovery (default dry-run)")
    add_store(s)
    s.add_argument("--source", action="append", default=[], help="Untrusted source token")
    s.add_argument("--agent", action="append", default=[], help="Untrusted agent id")
    s.add_argument("--execute", action="store_true", help="Actually delete (default dry-run)")
    s.add_argument("--actor", default="cli")
    s.set_defaults(func=cmd_purge)

    s = sub.add_parser("diff", help="Diff store vs another root / snapshot")
    add_store(s)
    s.add_argument("other", help="Other store root")
    s.set_defaults(func=cmd_diff)

    s = sub.add_parser("hygiene", help="Zombie / net-harm hygiene report (no deletes)")
    add_store(s)
    s.add_argument("--unused-before", default=None, help="Flag unused if last_verified before ISO")
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_hygiene)

    s = sub.add_parser("entangled", help="LINK-entangled suspects for human review")
    add_store(s)
    s.add_argument("--source", action="append", default=[], help="Untrusted source token")
    s.add_argument("--agent", action="append", default=[], help="Untrusted agent id")
    s.add_argument("--seed", action="append", default=[], help="Seed entry id")
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_entangled)

    s = sub.add_parser("forget-check", help="Post-erasure forgetting compliance probe")
    add_store(s)
    s.add_argument("--scope", required=True, help="consumer_scope for SEARCH probe")
    s.add_argument("--subject-id", default=None)
    s.add_argument("--entry-id", action="append", default=[], dest="entry_ids")
    s.add_argument("--probe-query", default=None)
    s.add_argument("--forbid", action="append", default=[], dest="forbid")
    s.set_defaults(func=cmd_forget_check)

    s = sub.add_parser("lineage", help="Supersede chain + journal audit lineage")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_lineage)

    s = sub.add_parser("belief-at", help="Point-in-time belief inventory or search")
    add_store(s)
    s.add_argument("as_of", help="ISO timestamp")
    s.add_argument("--scope", required=True)
    s.add_argument("--query", default=None)
    s.set_defaults(func=cmd_belief_at)

    s = sub.add_parser("conflicts", help="Conflict-preserving contested pairs")
    add_store(s)
    s.add_argument("--body-max", type=int, default=240)
    s.set_defaults(func=cmd_conflicts)

    s = sub.add_parser("injection-scan", help="Deterministic injection-marker scan")
    add_store(s)
    s.add_argument("--entry-id", action="append", default=[], dest="entry_ids")
    s.add_argument("--limit", type=int, default=100)
    s.set_defaults(func=cmd_injection_scan)

    s = sub.add_parser("budget-plan", help="Select compress plan under token budget")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", required=True)
    s.add_argument("--budget", type=int, default=400)
    s.add_argument("--withhold-injection", action="store_true")
    s.set_defaults(func=cmd_budget_plan)

    s = sub.add_parser("seal", help="Emit tamper-evident store seal")
    add_store(s)
    s.set_defaults(func=cmd_seal)

    s = sub.add_parser("verify-seal", help="Verify a prior seal JSON file against store")
    add_store(s)
    s.add_argument("seal_file", help="Path to seal JSON")
    s.set_defaults(func=cmd_verify_seal)

    s = sub.add_parser("receipt", help="Attribution receipt for one entry")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_receipt)

    s = sub.add_parser("replay-check", help="Journal↔SoT replay consistency")
    add_store(s)
    s.set_defaults(func=cmd_replay_check)

    s = sub.add_parser("lifecycle", help="AMV-L-shaped lifecycle tier inventory")
    add_store(s)
    s.add_argument("--hot-days", type=float, default=7.0)
    s.add_argument("--warm-days", type=float, default=30.0)
    s.set_defaults(func=cmd_lifecycle)

    s = sub.add_parser("revoke-key", help="TEPA-shaped revoke by conflict_key")
    add_store(s)
    s.add_argument("conflict_key")
    s.add_argument("--evidence", required=True, help="Path to evidence JSON list")
    s.add_argument("--actor", required=True)
    s.add_argument("--keep-id", default=None)
    s.set_defaults(func=cmd_revoke_key)

    s = sub.add_parser("pack-seal", help="Tamper-evident seal over an exported pack")
    add_store(s)
    s.add_argument("pack_dir")
    s.set_defaults(func=cmd_pack_seal)

    s = sub.add_parser("verify-pack-seal", help="Verify a prior pack seal")
    add_store(s)
    s.add_argument("pack_dir")
    s.add_argument("seal_file")
    s.set_defaults(func=cmd_verify_pack_seal)

    s = sub.add_parser("explain", help="SEARCH with channel rank detail")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", required=True)
    s.add_argument("--budget", type=int, default=400)
    s.add_argument("--tier", action="append", default=[], help="lifecycle tier allowlist")
    s.set_defaults(func=cmd_explain)

    s = sub.add_parser("blast", help="LINK neighborhood blast radius")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--depth", type=int, default=3)
    s.set_defaults(func=cmd_blast)

    s = sub.add_parser("merge-classify", help="MELD-shaped five-outcome merge classifier")
    add_store(s)
    s.add_argument("entry_a")
    s.add_argument("entry_b")
    s.add_argument("--merge-threshold", type=float, default=0.85)
    s.add_argument("--relate-threshold", type=float, default=0.45)
    s.set_defaults(func=cmd_merge_classify)

    s = sub.add_parser("path-trust", help="MAP-Graph-shaped path trust")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--source", action="append", default=[], help="Trusted source prefix")
    s.add_argument("--depth", type=int, default=3)
    s.set_defaults(func=cmd_path_trust)

    s = sub.add_parser("journal-chain", help="GPM-shaped journal hash-chain verify")
    add_store(s)
    s.set_defaults(func=cmd_journal_chain)

    s = sub.add_parser("spread", help="SYNAPSE-shaped spreading activation")
    add_store(s)
    s.add_argument("--seed", action="append", required=True, help="Seed entry id")
    s.add_argument("--hops", type=int, default=2)
    s.add_argument("--decay", type=float, default=0.5)
    s.add_argument("--inhibit", type=float, default=0.15)
    s.set_defaults(func=cmd_spread)

    s = sub.add_parser("density", help="SodaMem-shaped connection density")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_density)

    s = sub.add_parser("retention", help="Oblivion-shaped retention score")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--half-life", type=float, default=30.0)
    s.set_defaults(func=cmd_retention)

    s = sub.add_parser("health", help="Unified operator health report")
    add_store(s)
    s.set_defaults(func=cmd_health)

    s = sub.add_parser("release-gate", help="GPM-shaped fail-closed release gate")
    add_store(s)
    s.add_argument("--expected-head", default=None)
    s.add_argument("--allow-contested", action="store_true")
    s.add_argument("--allow-injection", action="store_true")
    s.add_argument("--block-stale", action="store_true")
    s.add_argument("--issue-receipt", action="store_true")
    s.add_argument("--record-abstain", action="store_true")
    s.add_argument("--actor", default=None)
    s.set_defaults(func=cmd_release_gate)

    s = sub.add_parser("rebuild-index", help="Rebuild derived SQLite FTS index")
    add_store(s)
    s.set_defaults(func=cmd_rebuild_index)

    s = sub.add_parser("search-sqlite", help="Query derived SQLite FTS index")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--state", action="append", default=[])
    s.add_argument("--scope-filter", action="append", default=[])
    s.add_argument("--cue", default=None)
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(func=cmd_search_sqlite)

    s = sub.add_parser("verify-import", help="PAM-shaped fail-closed import verify")
    add_store(s)
    s.add_argument("pack")
    s.set_defaults(func=cmd_verify_import)

    s = sub.add_parser("decisions", help="List local decision receipts")
    add_store(s)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_decisions)

    s = sub.add_parser("lineage-trust", help="MemLineage-shaped trust label")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--max-depth", type=int, default=3)
    s.set_defaults(func=cmd_lineage_trust)

    s = sub.add_parser("record-exec", help="PoEM-shaped proof-of-execution append")
    add_store(s)
    s.add_argument("step")
    s.add_argument("--subject-id", required=True)
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_record_exec)

    s = sub.add_parser("verify-exec", help="Verify safety step against execution ledger")
    add_store(s)
    s.add_argument("step")
    s.add_argument("--subject-id", required=True)
    s.set_defaults(func=cmd_verify_exec)

    s = sub.add_parser("authority-gate", help="PPMF-shaped action risk vs provenance")
    add_store(s)
    s.add_argument("action_risk", choices=["low", "medium", "high", "critical"])
    s.add_argument("--entry-id", action="append", dest="entry_ids", required=True)
    s.set_defaults(func=cmd_authority_gate)

    s = sub.add_parser("claim-closure", help="GPM-shaped exact claim closure")
    add_store(s)
    s.add_argument("--claim-id", action="append", dest="claim_ids", required=True)
    s.add_argument("--expected-head", default=None)
    s.set_defaults(func=cmd_claim_closure)

    s = sub.add_parser("cascade", help="MemoRepair-shaped cascade impact")
    add_store(s)
    s.add_argument("fault_id")
    s.add_argument("--max-depth", type=int, default=5)
    s.set_defaults(func=cmd_cascade)

    s = sub.add_parser("withdraw-cascade", help="Barrier-first cascade withdraw")
    add_store(s)
    s.add_argument("fault_id")
    s.add_argument("--actor", required=True)
    s.add_argument("--evidence-json", required=True)
    s.add_argument("--max-depth", type=int, default=5)
    s.set_defaults(func=cmd_withdraw_cascade)

    s = sub.add_parser("repair-plan", help="Predecessor-closed repair plan")
    add_store(s)
    s.add_argument("fault_id")
    s.add_argument("--lambda-cost", type=float, default=0.5)
    s.add_argument("--budget", type=int, default=None)
    s.add_argument("--max-depth", type=int, default=5)
    s.set_defaults(func=cmd_repair_plan)

    s = sub.add_parser("fact-interface", help="MemIR-shaped fact interface")
    add_store(s)
    s.add_argument("--entry-id", action="append", dest="entry_ids", default=None)
    s.set_defaults(func=cmd_fact_interface)

    s = sub.add_parser("role-scan", help="Provenance-role collapse scan")
    add_store(s)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_role_scan)

    s = sub.add_parser("dual-search", help="D-Mem dual-channel Select")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", required=True)
    s.add_argument("--budget", type=int, default=400)
    s.set_defaults(func=cmd_dual_search)

    s = sub.add_parser("commit", help="GitOfThoughts-shaped memory view commit")
    add_store(s)
    s.add_argument("message")
    s.add_argument("--entry-id", action="append", dest="entry_ids", required=True)
    s.add_argument("--actor", required=True)
    s.add_argument("--branch", default="main")
    s.add_argument("--outcome", default=None, choices=["success", "failed", None])
    s.set_defaults(func=cmd_commit)

    s = sub.add_parser("checkout", help="Replay commit entry-id set")
    add_store(s)
    s.add_argument("commit_hash")
    s.set_defaults(func=cmd_checkout)

    s = sub.add_parser("diff-commits", help="Diff two memory view commits")
    add_store(s)
    s.add_argument("a")
    s.add_argument("b")
    s.set_defaults(func=cmd_diff_commits)

    s = sub.add_parser("copyability", help="Copyability threshold gate")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", required=True)
    s.add_argument("--threshold", type=float, default=0.8)
    s.set_defaults(func=cmd_copyability)

    s = sub.add_parser("pin-version", help="ChronoMem pin promoted memory version")
    add_store(s)
    s.add_argument("label")
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_pin_version)

    s = sub.add_parser("activate-version", help="Activate/clear ChronoMem read HEAD")
    add_store(s)
    s.add_argument("commit_hash", nargs="?", default=None)
    s.add_argument("--clear", action="store_true")
    s.set_defaults(func=cmd_activate_version)

    s = sub.add_parser("stale-facts", help="MemStrata stale-fact scan")
    add_store(s)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_stale_facts)

    s = sub.add_parser("propose-update", help="TARL classify incoming entry JSON")
    add_store(s)
    s.add_argument("entry_json")
    s.set_defaults(func=cmd_propose_update)

    s = sub.add_parser("apply-update", help="TARL apply incoming entry JSON")
    add_store(s)
    s.add_argument("entry_json")
    s.add_argument("--actor", required=True)
    s.add_argument("--action", default=None)
    s.set_defaults(func=cmd_apply_update)

    s = sub.add_parser("ledger-view", help="TARL accepted/pending/rejected view")
    add_store(s)
    s.set_defaults(func=cmd_ledger_view)

    s = sub.add_parser("memory-worth", help="Memory Worth for one entry")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_memory_worth)

    s = sub.add_parser("low-worth", help="Low Memory Worth scan")
    add_store(s)
    s.add_argument("--threshold", type=float, default=0.4)
    s.add_argument("--min-samples", type=int, default=2)
    s.set_defaults(func=cmd_low_worth)

    s = sub.add_parser("begin-tx", help="MemTX begin transaction")
    add_store(s)
    s.add_argument("--actor", required=True)
    s.add_argument("--risk-tier", default="write")
    s.set_defaults(func=cmd_begin_tx)

    s = sub.add_parser("commit-tx", help="MemTX commit transaction")
    add_store(s)
    s.add_argument("txid")
    s.add_argument("--actor", required=True)
    s.add_argument("--evidence", required=True, help="Path to evidence JSON list")
    s.set_defaults(func=cmd_commit_tx)

    s = sub.add_parser("abort-tx", help="MemTX abort transaction")
    add_store(s)
    s.add_argument("txid")
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_abort_tx)

    s = sub.add_parser("action-safe", help="MemTX action-safety gate")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.set_defaults(func=cmd_action_safe)

    s = sub.add_parser("in-flight", help="MemTX in-flight report")
    add_store(s)
    s.set_defaults(func=cmd_in_flight)

    s = sub.add_parser("symbolic-conflicts", help="LatticeMind symbolic conflict scan")
    add_store(s)
    s.set_defaults(func=cmd_symbolic_conflicts)

    s = sub.add_parser("classify-conflict", help="Credibility vs coordination")
    add_store(s)
    s.add_argument("entry_a")
    s.add_argument("entry_b")
    s.set_defaults(func=cmd_classify_conflict)

    s = sub.add_parser("compact-render", help="LatticeMind budgeted compact render")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", required=True)
    s.add_argument("--reader-budget", type=int, default=1400)
    s.set_defaults(func=cmd_compact_render)

    s = sub.add_parser("stage-effect", help="Cordon stage effect outbox")
    add_store(s)
    s.add_argument("--sink", required=True)
    s.add_argument("--payload", required=True, help="JSON object or path")
    s.add_argument("--actor", required=True)
    s.add_argument("--txid", default=None)
    s.set_defaults(func=cmd_stage_effect)

    s = sub.add_parser("list-effects", help="Cordon list effect outbox")
    add_store(s)
    s.add_argument("--state", default=None)
    s.set_defaults(func=cmd_list_effects)

    s = sub.add_parser("state-resolution", help="STALE state resolution")
    add_store(s)
    s.add_argument("--key", default=None)
    s.set_defaults(func=cmd_state_resolution)

    s = sub.add_parser("premise-resistance", help="STALE premise resistance")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", default=None)
    s.set_defaults(func=cmd_premise_resistance)

    s = sub.add_parser("verify-transition", help="VTA verify supersede pair")
    add_store(s)
    s.add_argument("old_id")
    s.add_argument("new_id")
    s.set_defaults(func=cmd_verify_transition)

    s = sub.add_parser("related-slots", help="Same-domain slot scan")
    add_store(s)
    s.add_argument("conflict_key")
    s.set_defaults(func=cmd_related_slots)

    s = sub.add_parser("gem-report", help="GEM correctness checklist")
    add_store(s)
    s.set_defaults(func=cmd_gem_report)

    s = sub.add_parser("project-resolve", help="StateFuse projection resolve")
    add_store(s)
    s.add_argument("conflict_key")
    s.set_defaults(func=cmd_project_resolve)

    s = sub.add_parser("correction-handle", help="StateFuse correction handle")
    add_store(s)
    s.add_argument("--claim-id")
    s.add_argument("--claim-ref")
    s.set_defaults(func=cmd_correction_handle)

    s = sub.add_parser("pin-projection", help="Pin projection without SoT rewrite")
    add_store(s)
    s.add_argument("conflict_key")
    s.add_argument("chosen_id")
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_pin_projection)

    s = sub.add_parser("toki-classify", help="TOKI classify write operator")
    add_store(s)
    s.add_argument("candidate_json")
    s.add_argument("--tip-id")
    s.set_defaults(func=cmd_toki_classify)

    s = sub.add_parser("toki-anomalies", help="TOKI anomaly scan")
    add_store(s)
    s.set_defaults(func=cmd_toki_anomalies)

    s = sub.add_parser("context-bid", help="MemArchitect triage & bid")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--slots", type=int, default=5)
    s.set_defaults(func=cmd_context_bid)

    s = sub.add_parser("repair-mincut", help="Exact MemoRepair s-t min-cut select")
    add_store(s)
    s.add_argument("fault_id")
    s.add_argument("--lambda-cost", type=float, default=0.5)
    s.set_defaults(func=cmd_repair_mincut)

    s = sub.add_parser("adjudicate", help="CUPMem write-side adjudicate")
    add_store(s)
    s.add_argument("candidate_json")
    s.set_defaults(func=cmd_adjudicate)

    s = sub.add_parser("unknown-slots", help="CUPMem unknown-current slots")
    add_store(s)
    s.set_defaults(func=cmd_unknown_slots)

    s = sub.add_parser("authorize-retrieval", help="CUPMem authorize retrieval")
    add_store(s)
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.add_argument("--query", default="")
    s.set_defaults(func=cmd_authorize_retrieval)

    s = sub.add_parser("admit-gate", help="CMGL-shaped admit gate")
    add_store(s)
    s.add_argument("action")
    s.add_argument("--actor", required=True)
    s.add_argument("--bundle-json", required=True)
    s.set_defaults(func=cmd_admit_gate)

    s = sub.add_parser("put-raw", help="TierMem put raw page")
    add_store(s)
    s.add_argument("text")
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_put_raw)

    s = sub.add_parser("sufficiency", help="TierMem sufficiency gate")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_sufficiency)

    s = sub.add_parser("escalate-raw", help="TierMem escalate to raw")
    add_store(s)
    s.add_argument("summary_ids", nargs="+")
    s.set_defaults(func=cmd_escalate_raw)

    s = sub.add_parser("writeback", help="TierMem verified write-back")
    add_store(s)
    s.add_argument("--title", required=True)
    s.add_argument("--body", required=True)
    s.add_argument("--scope", required=True)
    s.add_argument("--raw-digest", action="append", default=[])
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_writeback)

    s = sub.add_parser("crystallize-skill", help="MSCE crystallize skill")
    add_store(s)
    s.add_argument("source_ids", nargs="+")
    s.add_argument("--write", action="store_true")
    s.add_argument("--actor")
    s.set_defaults(func=cmd_crystallize)

    s = sub.add_parser("skill-catalog", help="MSCE skill catalog")
    add_store(s)
    s.set_defaults(func=cmd_skill_catalog)

    s = sub.add_parser("fade-scan", help="FadeMem fade candidates")
    add_store(s)
    s.add_argument("--threshold", type=float, default=0.15)
    s.set_defaults(func=cmd_fade_scan)

    s = sub.add_parser("fusion-candidates", help="FadeMem fusion pairs")
    add_store(s)
    s.set_defaults(func=cmd_fusion_candidates)

    s = sub.add_parser("weibull", help="SSGM Weibull relevance")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_weibull)

    s = sub.add_parser("evidence-gap", help="MemR3 evidence gap")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_evidence_gap)

    s = sub.add_parser("reflective-retrieve", help="MemR3 reflective plan")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_reflective)

    s = sub.add_parser("archive-plan", help="Utility-weighted archive plan")
    add_store(s)
    s.add_argument("--min-age-days", type=float, default=14.0)
    s.set_defaults(func=cmd_archive_plan)

    s = sub.add_parser("archive-apply", help="Archive entry ids")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.add_argument("--actor", required=True)
    s.add_argument("--force", action="store_true", help="Skip eligibility gate")
    s.set_defaults(func=cmd_archive_apply)

    s = sub.add_parser("unarchive", help="Restore archived → promoted")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_unarchive)

    s = sub.add_parser("cis", help="SF-AMS composite importance")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_cis)

    s = sub.add_parser("cis-scan", help="SF-AMS CIS scan")
    add_store(s)
    s.set_defaults(func=cmd_cis_scan)

    s = sub.add_parser("control-suggest", help="MemCon control suggest")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_control_suggest)

    s = sub.add_parser("value-tag", help="SCM value tag")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--task-query", default="")
    s.set_defaults(func=cmd_value_tag)

    s = sub.add_parser("wm-push", help="SCM working-memory push")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_wm_push)

    s = sub.add_parser("wm-list", help="SCM working-memory list")
    add_store(s)
    s.set_defaults(func=cmd_wm_list)

    s = sub.add_parser("sleep-plan", help="SCM sleep cycle plan")
    add_store(s)
    s.set_defaults(func=cmd_sleep_plan)

    s = sub.add_parser("sleep-nrem", help="SCM NREM reinforce apply")
    add_store(s)
    s.add_argument("--actor", required=True)
    s.set_defaults(func=cmd_sleep_nrem)

    s = sub.add_parser("episodic-buffer", help="GAM episodic buffer")
    add_store(s)
    s.set_defaults(func=cmd_episodic_buffer)

    s = sub.add_parser("semantic-boundary", help="GAM topic shift")
    add_store(s)
    s.add_argument("previous")
    s.add_argument("current")
    s.set_defaults(func=cmd_semantic_boundary)

    s = sub.add_parser("consolidate-plan", help="GAM consolidate plan")
    add_store(s)
    s.set_defaults(func=cmd_consolidate_plan)

    s = sub.add_parser("anticipate", help="ACM anticipate prefetch")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_anticipate)

    s = sub.add_parser("verify-compaction", help="ACM compaction verify")
    add_store(s)
    s.add_argument("query")
    s.add_argument("compacted_text")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_verify_compaction)

    s = sub.add_parser("sensory-filter", help="LightMem sensory filter")
    add_store(s)
    s.add_argument("text")
    s.set_defaults(func=cmd_sensory_filter)

    s = sub.add_parser("stage-inventory", help="LightMem stage inventory")
    add_store(s)
    s.set_defaults(func=cmd_stage_inventory)

    s = sub.add_parser("stage-budget", help="LightMem stage budget plan")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_stage_budget)

    s = sub.add_parser("multi-hop", help="HippoRAG multi-hop retrieve")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_multi_hop)

    s = sub.add_parser("write-gate", help="Quipu write gate (JSON pending)")
    add_store(s)
    s.add_argument("pending_json")
    s.set_defaults(func=cmd_write_gate)

    s = sub.add_parser("action-risk-gate", help="MAP-Graph action risk gate")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.add_argument("--risk", default="medium")
    s.set_defaults(func=cmd_action_risk_gate)

    s = sub.add_parser("residuals", help="ProGraph compression residuals")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_residuals)

    s = sub.add_parser("entities", help="ProGraph entity registry")
    add_store(s)
    s.set_defaults(func=cmd_entities)

    s = sub.add_parser("profile-expand", help="ProGraph profile expansion")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_profile_expand)

    s = sub.add_parser("residual-augment", help="ProGraph residual augment")
    add_store(s)
    s.add_argument("query")
    s.add_argument("entry_ids", nargs="+")
    s.set_defaults(func=cmd_residual_augment)

    s = sub.add_parser("match-correction", help="EMG match correction paths")
    add_store(s)
    s.add_argument("--failure-id", default=None)
    s.set_defaults(func=cmd_match_correction)

    s = sub.add_parser("insight-inject", help="EMG insight inject (JSON path)")
    add_store(s)
    s.add_argument("correction_json")
    s.set_defaults(func=cmd_insight_inject)

    s = sub.add_parser("cascade-route", help="AgentIR cascade route")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_cascade_route)

    s = sub.add_parser("multi-channel", help="AgentIR multi-channel RRF")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.add_argument("--force-full", action="store_true")
    s.set_defaults(func=cmd_multi_channel)

    s = sub.add_parser("dual-project", help="Governed Memory dual project")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_dual_project)

    s = sub.add_parser("governance-route", help="Governed Memory route")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_governance_route)

    s = sub.add_parser("session-delta-open", help="Open session delta")
    add_store(s)
    s.add_argument("session_id")
    s.set_defaults(func=cmd_session_delta_open)

    s = sub.add_parser("session-delta-deliver", help="Deliver session delta")
    add_store(s)
    s.add_argument("session_id")
    s.add_argument("route_json")
    s.set_defaults(func=cmd_session_delta_deliver)

    s = sub.add_parser("entity-context", help="Entity Properties+Observations")
    add_store(s)
    s.add_argument("subject_id")
    s.set_defaults(func=cmd_entity_context)

    s = sub.add_parser("entity-leak-probe", help="Entity leakage probe")
    add_store(s)
    s.add_argument("subject_id")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.add_argument("--query", default="")
    s.add_argument("--no-prefilter", action="store_true")
    s.set_defaults(func=cmd_entity_leak_probe)

    s = sub.add_parser("hymem-slot", help="HyMem classify slot")
    add_store(s)
    s.add_argument("text")
    s.set_defaults(func=cmd_hymem_slot)

    s = sub.add_parser("hymem-isolate", help="HyMem isolate pack (JSON items)")
    add_store(s)
    s.add_argument("items_json")
    s.set_defaults(func=cmd_hymem_isolate)

    s = sub.add_parser("version-markers", help="Extract version markers")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_version_markers)

    s = sub.add_parser("freshness-resolve", help="Deterministic freshness resolve")
    add_store(s)
    s.add_argument("--conflict-key", default=None)
    s.set_defaults(func=cmd_freshness_resolve)

    s = sub.add_parser("assemble-current", help="Assemble current tips")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_assemble_current)

    s = sub.add_parser("hop-freshness", help="Per-hop freshness (JSON hops)")
    add_store(s)
    s.add_argument("hops_json")
    s.set_defaults(func=cmd_hop_freshness)

    s = sub.add_parser("patch-test", help="MemTxn patch test")
    add_store(s)
    s.add_argument("pending_json")
    s.add_argument("source_id")
    s.add_argument("--span", dest="cited_span", default=None)
    s.set_defaults(func=cmd_patch_test)

    s = sub.add_parser("temporal-resolve", help="MemTxn temporal resolve")
    add_store(s)
    s.add_argument("conflict_key")
    s.set_defaults(func=cmd_temporal_resolve)

    s = sub.add_parser("recover-active-map", help="Recover active tip map")
    add_store(s)
    s.add_argument("--keys-json", default=None)
    s.set_defaults(func=cmd_recover_active_map)

    s = sub.add_parser("fleet-scope-gate", help="Fleet scope gate")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("scopes", nargs="+")
    s.set_defaults(func=cmd_fleet_scope_gate)

    s = sub.add_parser("propagate-plan", help="Fleet propagate plan")
    add_store(s)
    s.add_argument("--from-scope", dest="source_scope", required=True)
    s.add_argument("--to-scope", dest="target_scopes", nargs="+", required=True)
    s.add_argument("--query", default="")
    s.set_defaults(func=cmd_propagate_plan)

    s = sub.add_parser("stale-propagation", help="Stale propagation scan")
    add_store(s)
    s.set_defaults(func=cmd_stale_propagation)

    s = sub.add_parser("query-complexity", help="BudgetMem query complexity")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_query_complexity)

    s = sub.add_parser("budget-tier-route", help="BudgetMem tier route")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_budget_tier_route)

    s = sub.add_parser("budget-module-plan", help="BudgetMem module plan")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--budget", type=int, default=10)
    s.set_defaults(func=cmd_budget_module_plan)

    s = sub.add_parser("skill-rank", help="Rank skill/workflow library")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_skill_rank)

    s = sub.add_parser("skill-prereq", help="Expand skill LINKs")
    add_store(s)
    s.add_argument("skill_id")
    s.set_defaults(func=cmd_skill_prereq)

    s = sub.add_parser("retrieval-skills", help="List ERSkill skills")
    add_store(s)
    s.set_defaults(func=cmd_retrieval_skills)

    s = sub.add_parser("route-retrieval-skill", help="Route retrieval skill")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_route_retrieval_skill)

    s = sub.add_parser("run-retrieval-skill", help="Run retrieval skill")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.add_argument("--skill", default=None)
    s.set_defaults(func=cmd_run_retrieval_skill)

    s = sub.add_parser("support-score", help="ConsistencyGate support score")
    add_store(s)
    s.add_argument("pending_json")
    s.add_argument("--context", default="")
    s.set_defaults(func=cmd_support_score)

    s = sub.add_parser("consistency-admit", help="ConsistencyGate admit")
    add_store(s)
    s.add_argument("pending_json")
    s.add_argument("--context", default="")
    s.add_argument("--tau", type=float, default=0.35)
    s.set_defaults(func=cmd_consistency_admit)

    s = sub.add_parser("retrieval-admit", help="MemGate retrieval admit")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_retrieval_admit)

    s = sub.add_parser("task-pack", help="MemGate task-conditioned pack")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_task_pack)

    s = sub.add_parser("sovereignty-checklist", help="Mnemonic sovereignty checklist")
    add_store(s)
    s.set_defaults(func=cmd_sovereignty_checklist)

    s = sub.add_parser("post-delete-verify", help="Post-deletion verify")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.add_argument("--scope", dest="consumer_scope", default=None)
    s.set_defaults(func=cmd_post_delete_verify)

    s = sub.add_parser("rollback-plan", help="Rollback plan (report-only)")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.set_defaults(func=cmd_rollback_plan)

    s = sub.add_parser("density-fuse", help="SodaMem density fuse")
    add_store(s)
    s.add_argument("tunnels_json")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(func=cmd_density_fuse)

    s = sub.add_parser("evidence-plan", help="SodaMem evidence plan")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=8)
    s.set_defaults(func=cmd_evidence_plan)

    s = sub.add_parser("cited-pack", help="SodaMem cited reader pack")
    add_store(s)
    s.add_argument("query")
    s.add_argument("evidence_ids", nargs="+")
    s.add_argument("--budget", type=int, default=400)
    s.set_defaults(func=cmd_cited_pack)

    s = sub.add_parser("compress-candidates", help="MemRefine pair candidates")
    add_store(s)
    s.add_argument("--min-sim", type=float, default=0.45)
    s.set_defaults(func=cmd_compress_candidates)

    s = sub.add_parser("refine-plan", help="MemRefine compression plan")
    add_store(s)
    s.add_argument("--target", type=int, required=True)
    s.add_argument("--min-sim", type=float, default=0.45)
    s.set_defaults(func=cmd_refine_plan)

    s = sub.add_parser("merge-link-add", help="AriadneMem merge|link|add")
    add_store(s)
    s.add_argument("entry_json")
    s.set_defaults(func=cmd_merge_link_add)

    s = sub.add_parser("bridge-discover", help="AriadneMem bridge discovery")
    add_store(s)
    s.add_argument("seed_ids", nargs="+")
    s.add_argument("--max-depth", type=int, default=3)
    s.set_defaults(func=cmd_bridge_discover)

    s = sub.add_parser("fuse-cluster", help="MemFuse cluster summary")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.add_argument("--label", default=None)
    s.set_defaults(func=cmd_fuse_cluster)

    s = sub.add_parser("result-digest", help="TGMS content-addressed digest")
    add_store(s)
    s.add_argument("payload_json")
    s.set_defaults(func=cmd_result_digest)

    s = sub.add_parser("operator-cost", help="TGMS operator cost estimate")
    add_store(s)
    s.add_argument("steps_json")
    s.add_argument("--max-cost", type=int, default=40)
    s.set_defaults(func=cmd_operator_cost)

    s = sub.add_parser("plan-verify", help="TGMS static plan verify")
    add_store(s)
    s.add_argument("plan_json")
    s.add_argument("--task-ids", nargs="*", default=[])
    s.add_argument("--max-cost", type=int, default=40)
    s.set_defaults(func=cmd_plan_verify)

    s = sub.add_parser("claim-verify", help="TGMS claim verify vs trace")
    add_store(s)
    s.add_argument("claims_json")
    s.add_argument("trace_json")
    s.set_defaults(func=cmd_claim_verify)

    s = sub.add_parser("summary-quarantine", help="TGMS summary quarantine scan")
    add_store(s)
    s.add_argument("summaries_json")
    s.add_argument("corrections_json")
    s.set_defaults(func=cmd_summary_quarantine)

    s = sub.add_parser("local-maint", help="MemoryData localized maintenance")
    add_store(s)
    s.add_argument("seed_ids", nargs="+")
    s.add_argument("--radius", type=int, default=1)
    s.add_argument("--max-touch", type=int, default=20)
    s.set_defaults(func=cmd_local_maint)

    s = sub.add_parser("maint-cost", help="Local vs global maint cost")
    add_store(s)
    s.add_argument("local_touch", type=int)
    s.add_argument("--store-size", type=int, default=None)
    s.set_defaults(func=cmd_maint_cost)

    s = sub.add_parser("origin-bind", help="TMA-NM origin bind")
    add_store(s)
    s.add_argument("pending_json")
    s.add_argument("--origin", dest="channel_origin", required=True)
    s.set_defaults(func=cmd_origin_bind)

    s = sub.add_parser("propagate-origin", help="TMA-NM propagate origin")
    add_store(s)
    s.add_argument("derived_json")
    s.add_argument("source_ids", nargs="+")
    s.set_defaults(func=cmd_propagate_origin)

    s = sub.add_parser("launder-scan", help="TMA-NM launder scan")
    add_store(s)
    s.set_defaults(func=cmd_launder_scan)

    s = sub.add_parser("act-authority", help="TMA-NM act authority gate")
    add_store(s)
    s.add_argument("value")
    s.add_argument("driver_ids", nargs="+")
    s.add_argument("--principal", action="append", default=[])
    s.add_argument("--user-auth", action="store_true")
    s.set_defaults(func=cmd_act_authority)

    s = sub.add_parser("save-policy", help="AM-Sentry save policy")
    add_store(s)
    s.add_argument("pending_json")
    s.add_argument("--level", default="standard")
    s.add_argument("--origin", dest="channel_origin", default="untrusted_external")
    s.set_defaults(func=cmd_save_policy)

    s = sub.add_parser("retrieval-screen", help="AM-Sentry retrieval screen")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_retrieval_screen)

    s = sub.add_parser("build-memtree", help="MemForest MemTree index")
    add_store(s)
    s.add_argument("--scope", default=None)
    s.set_defaults(func=cmd_build_memtree)

    s = sub.add_parser("dirty-path", help="MemForest dirty-path plan")
    add_store(s)
    s.add_argument("entry_json")
    s.add_argument("--scope", default=None)
    s.set_defaults(func=cmd_dirty_path)

    s = sub.add_parser("coarse-to-fine", help="MemForest coarse-to-fine")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", default=None)
    s.set_defaults(func=cmd_coarse_to_fine)

    s = sub.add_parser("build-themes", help="xMemory theme bootstrap")
    add_store(s)
    s.add_argument("--scope", default=None)
    s.set_defaults(func=cmd_build_themes)

    s = sub.add_parser("theme-attach", help="xMemory theme attach")
    add_store(s)
    s.add_argument("entry_json")
    s.add_argument("--scope", default=None)
    s.set_defaults(func=cmd_theme_attach)

    s = sub.add_parser("split-merge", help="xMemory split/merge plan")
    add_store(s)
    s.add_argument("--scope", default=None)
    s.add_argument("--max-size", type=int, default=6)
    s.set_defaults(func=cmd_split_merge)

    s = sub.add_parser("top-down-pack", help="xMemory top-down pack")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", default=None)
    s.add_argument("--budget", type=int, default=200)
    s.set_defaults(func=cmd_top_down_pack)

    s = sub.add_parser("persistence-probe", help="MemSecBench persistence")
    add_store(s)
    s.add_argument("poison_ids", nargs="+")
    s.set_defaults(func=cmd_persistence_probe)

    s = sub.add_parser("execute-chain-probe", help="MemSecBench execute chain")
    add_store(s)
    s.add_argument("poison_ids", nargs="+")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.add_argument("--query", default="")
    s.add_argument("--action-value", default="")
    s.set_defaults(func=cmd_execute_chain_probe)

    s = sub.add_parser("lifecycle-report", help="MemSecBench WEF lifecycle")
    add_store(s)
    s.add_argument("poison_ids", nargs="+")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.add_argument("--preserve", nargs="*", default=[])
    s.set_defaults(func=cmd_lifecycle_report)

    s = sub.add_parser("selective-repair", help="MemSecBench selective repair")
    add_store(s)
    s.add_argument("poison_ids", nargs="+")
    s.add_argument("--preserve", nargs="*", default=[])
    s.set_defaults(func=cmd_selective_repair)

    s = sub.add_parser("conflict-tag", help="SleepGate conflict tags")
    add_store(s)
    s.add_argument("--conflict-key", default=None)
    s.set_defaults(func=cmd_conflict_tag)

    s = sub.add_parser("forget-gate", help="SleepGate forget gate plan")
    add_store(s)
    s.add_argument("--conflict-key", default=None)
    s.set_defaults(func=cmd_forget_gate)

    s = sub.add_parser("consolidate-survivors", help="SleepGate consolidate")
    add_store(s)
    s.add_argument("conflict_key")
    s.set_defaults(func=cmd_consolidate_survivors)

    s = sub.add_parser("pi-depth", help="SleepGate PI depth")
    add_store(s)
    s.add_argument("conflict_key")
    s.set_defaults(func=cmd_pi_depth)

    s = sub.add_parser("consensus-admit", help="A-MemGuard consensus admit")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_consensus_admit)

    s = sub.add_parser("mem-action-graph", help="DepRepair memory↔action graph")
    add_store(s)
    s.add_argument("--actions-json", default=None)
    s.set_defaults(func=cmd_mem_action_graph)

    s = sub.add_parser("dependency-trace", help="DepRepair dependency trace")
    add_store(s)
    s.add_argument("fault_ids", nargs="+")
    s.set_defaults(func=cmd_dependency_trace)

    s = sub.add_parser("preserve-independent", help="DepRepair preserve independent")
    add_store(s)
    s.add_argument("fault_ids", nargs="+")
    s.add_argument("--trusted-source", action="append", default=[])
    s.set_defaults(func=cmd_preserve_independent)

    s = sub.add_parser("selective-replay", help="DepRepair selective replay plan")
    add_store(s)
    s.add_argument("fault_ids", nargs="+")
    s.add_argument("--trusted-source", action="append", default=[])
    s.add_argument("--actions-json", default=None)
    s.set_defaults(func=cmd_selective_replay)

    s = sub.add_parser("classify-write-channel", help="MPBench write channel")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_classify_write_channel)

    s = sub.add_parser("source-isolation", help="MPBench source isolation gate")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_source_isolation)

    s = sub.add_parser("write-channel-inventory", help="MPBench channel inventory")
    add_store(s)
    s.set_defaults(func=cmd_write_channel_inventory)

    s = sub.add_parser("channel-admit-batch", help="MPBench batch channel admit")
    add_store(s)
    s.add_argument("candidates_json")
    s.set_defaults(func=cmd_channel_admit_batch)

    s = sub.add_parser("slot-coverage", help="MemPoison slot coverage")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_slot_coverage)

    s = sub.add_parser("threat-tier", help="MemPoison L1/L2/L3 tier")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_threat_tier)

    s = sub.add_parser("dormant-scan", help="MemPoison L3 dormant scan")
    add_store(s)
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(func=cmd_dormant_scan)

    s = sub.add_parser("coalition-scan", help="Salami coalition scan")
    add_store(s)
    s.add_argument("--min-slots", type=int, default=3)
    s.set_defaults(func=cmd_coalition_scan)

    s = sub.add_parser("collusion-gate", help="Salami collusion risk gate")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_collusion_gate)

    s = sub.add_parser("mempoison-ladder", help="MemPoison L1–L3 inventory")
    add_store(s)
    s.set_defaults(func=cmd_mempoison_ladder)

    s = sub.add_parser("salami-pair", help="Salami two-fragment probe")
    add_store(s)
    s.add_argument("entry_id_a")
    s.add_argument("entry_id_b")
    s.set_defaults(func=cmd_salami_pair)

    s = sub.add_parser("persistence-layer", help="Classify persistence layer")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--override", default=None)
    s.set_defaults(func=cmd_persistence_layer)

    s = sub.add_parser("persistence-policy", help="Persistence layer policy card")
    add_store(s)
    s.add_argument("layer")
    s.set_defaults(func=cmd_persistence_policy)

    s = sub.add_parser("layer-inventory", help="Persistence layer inventory")
    add_store(s)
    s.set_defaults(func=cmd_layer_inventory)

    s = sub.add_parser("knowledge-protect", help="Knowledge protect scan")
    add_store(s)
    s.add_argument("--faded", nargs="*", default=[])
    s.set_defaults(func=cmd_knowledge_protect)

    s = sub.add_parser("intelligence-reject", help="Reject ephemeral intelligence")
    add_store(s)
    s.add_argument("--entry-id", default=None)
    s.add_argument("--candidate-json", default=None)
    s.set_defaults(func=cmd_intelligence_reject)

    s = sub.add_parser("credential-scan", help="Scan entry for credentials")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_credential_scan)

    s = sub.add_parser("credential-reject", help="Credential write reject gate")
    add_store(s)
    s.add_argument("--entry-id", default=None)
    s.add_argument("--candidate-json", default=None)
    s.set_defaults(func=cmd_credential_reject)

    s = sub.add_parser("credential-store-scan", help="Store credential inventory")
    add_store(s)
    s.set_defaults(func=cmd_credential_store_scan)

    s = sub.add_parser("uncertainty-score", help="Oblivion uncertainty score")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_uncertainty_score)

    s = sub.add_parser("uncertainty-gate", help="Uncertainty retrieve gate")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--scope", dest="consumer_scope", required=True)
    s.set_defaults(func=cmd_uncertainty_gate)

    s = sub.add_parser("reasoning-reserve", help="Adaptive budget split")
    add_store(s)
    s.add_argument("budget", type=int)
    s.add_argument("--confidence", type=float, required=True)
    s.set_defaults(func=cmd_reasoning_reserve)

    s = sub.add_parser("memory-component", help="PAM E/S/P/W/I component")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_memory_component)

    s = sub.add_parser("merkle-dag", help="PAM Merkle-DAG")
    add_store(s)
    s.set_defaults(func=cmd_merkle_dag)

    s = sub.add_parser("verify-merkle", help="Verify Merkle root")
    add_store(s)
    s.add_argument("expected_root")
    s.set_defaults(func=cmd_verify_merkle)

    s = sub.add_parser("issue-cap-token", help="Issue PAM capability token")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.add_argument("--ops", nargs="+", required=True)
    s.add_argument("--audience", required=True)
    s.add_argument("--expires-at", required=True)
    s.set_defaults(func=cmd_issue_cap_token)

    s = sub.add_parser("check-cap-token", help="Check PAM capability token")
    add_store(s)
    s.add_argument("token")
    s.add_argument("payload_json")
    s.add_argument("--op", required=True)
    s.add_argument("--entry-id", default=None)
    s.set_defaults(func=cmd_check_cap_token)

    s = sub.add_parser("selective-disclose", help="PAM selective disclose")
    add_store(s)
    s.add_argument("entry_ids", nargs="+")
    s.add_argument("--no-ancestors", action="store_true")
    s.set_defaults(func=cmd_selective_disclose)

    s = sub.add_parser("rehydrate-safe", help="PAM rehydrate safe plan")
    add_store(s)
    s.add_argument("entry_ids", nargs="*")
    s.set_defaults(func=cmd_rehydrate_safe)

    s = sub.add_parser("issue-action-cap", help="CapSeal action capability")
    add_store(s)
    s.add_argument("--intent", required=True)
    s.add_argument("--method", required=True)
    s.add_argument("--host", required=True)
    s.add_argument("--session-id", required=True)
    s.add_argument("--expires-at", required=True)
    s.add_argument("--max-calls", type=int, default=1)
    s.set_defaults(func=cmd_issue_action_cap)

    s = sub.add_parser("cap-export-probe", help="CapSeal export probe")
    add_store(s)
    s.add_argument("handle")
    s.add_argument("payload_json")
    s.set_defaults(func=cmd_cap_export_probe)

    s = sub.add_parser("check-action-cap", help="Check CapSeal action capability")
    add_store(s)
    s.add_argument("handle")
    s.add_argument("payload_json")
    s.add_argument("--method", required=True)
    s.add_argument("--host", required=True)
    s.add_argument("--session-id", required=True)
    s.add_argument("--call-count", type=int, default=0)
    s.set_defaults(func=cmd_check_action_cap)

    s = sub.add_parser("risk-source", help="AgentDoG risk source")
    add_store(s)
    s.add_argument("step_json")
    s.set_defaults(func=cmd_risk_source)

    s = sub.add_parser("failure-mode", help="AgentDoG failure mode")
    add_store(s)
    s.add_argument("step_json")
    s.set_defaults(func=cmd_failure_mode)

    s = sub.add_parser("real-world-harm", help="AgentDoG real-world harm")
    add_store(s)
    s.add_argument("step_json")
    s.set_defaults(func=cmd_real_world_harm)

    s = sub.add_parser("diagnose-step", help="AgentDoG diagnose one step")
    add_store(s)
    s.add_argument("step_json")
    s.set_defaults(func=cmd_diagnose_step)

    s = sub.add_parser("diagnose-trajectory", help="AgentDoG diagnose trajectory")
    add_store(s)
    s.add_argument("steps_json")
    s.set_defaults(func=cmd_diagnose_trajectory)

    s = sub.add_parser("unreasonable-scan", help="Safe-but-unreasonable scan")
    add_store(s)
    s.add_argument("steps_json")
    s.set_defaults(func=cmd_unreasonable_scan)

    s = sub.add_parser("taxonomy-inventory", help="AgentDoG taxonomy inventory")
    add_store(s)
    s.set_defaults(func=cmd_taxonomy_inventory)

    s = sub.add_parser("weave-layer", help="MemWeaver weave layer")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_weave_layer)

    s = sub.add_parser("hybrid-weave", help="MemWeaver hybrid weave")
    add_store(s)
    s.set_defaults(func=cmd_hybrid_weave)

    s = sub.add_parser("dual-channel", help="MemWeaver dual-channel retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--k-r", type=int, default=6)
    s.add_argument("--k-p", type=int, default=6)
    s.add_argument("--k-e", type=int, default=6)
    s.set_defaults(func=cmd_dual_channel)

    s = sub.add_parser("experience-abstract", help="MemWeaver experience plan")
    add_store(s)
    s.add_argument("--min-support", type=int, default=2)
    s.set_defaults(func=cmd_experience_abstract)

    s = sub.add_parser("temporal-conflict", help="MemWeaver temporal conflict scan")
    add_store(s)
    s.set_defaults(func=cmd_temporal_conflict)

    s = sub.add_parser("hop-depth", help="MemHop-shaped hop depth")
    add_store(s)
    s.add_argument("path_ids", nargs="+")
    s.set_defaults(func=cmd_hop_depth)

    s = sub.add_parser("design-space", help="MemEvolve design space")
    add_store(s)
    s.set_defaults(func=cmd_design_space)

    s = sub.add_parser("arch-profile", help="MemEvolve architecture profile")
    add_store(s)
    s.add_argument("--encode", default=None)
    s.add_argument("--store-mode", default=None, dest="store_mode")
    s.add_argument("--retrieve", default=None)
    s.add_argument("--manage", default=None)
    s.set_defaults(func=cmd_arch_profile)

    s = sub.add_parser("arch-diagnose", help="MemEvolve diagnose architecture")
    add_store(s)
    s.add_argument("profile_json")
    s.add_argument("--feedback-json", default=None)
    s.set_defaults(func=cmd_arch_diagnose)

    s = sub.add_parser("arch-variants", help="MemEvolve propose variants")
    add_store(s)
    s.add_argument("profile_json")
    s.add_argument("diagnosis_json")
    s.add_argument("-s", type=int, default=3)
    s.set_defaults(func=cmd_arch_variants)

    s = sub.add_parser("arch-rank", help="MemEvolve rank fitness")
    add_store(s)
    s.add_argument("candidates_json")
    s.set_defaults(func=cmd_arch_rank)

    s = sub.add_parser("arch-parents", help="MemEvolve select parents")
    add_store(s)
    s.add_argument("ranked_json")
    s.add_argument("-k", type=int, default=1)
    s.set_defaults(func=cmd_arch_parents)

    s = sub.add_parser("ept", help="MindMemOS EPT classify")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_ept)

    s = sub.add_parser("functional-role", help="MemGuard functional role")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_functional_role)

    s = sub.add_parser("contamination-scan", help="MemGuard contamination scan")
    add_store(s)
    s.set_defaults(func=cmd_contamination_scan)

    s = sub.add_parser("type-route", help="MemGuard type-route retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--roles", nargs="*", default=None)
    s.add_argument("--budget", type=int, default=8)
    s.set_defaults(func=cmd_type_route)

    s = sub.add_parser("dreaming-plan", help="MindMemOS dreaming plan")
    add_store(s)
    s.set_defaults(func=cmd_dreaming_plan)

    s = sub.add_parser("feedback-revise", help="MindMemOS feedback revise plan")
    add_store(s)
    s.add_argument("signal")
    s.add_argument("--entry-ids", nargs="*", default=None)
    s.add_argument("--mode", default="explicit")
    s.set_defaults(func=cmd_feedback_revise)

    s = sub.add_parser("skill-evolve", help="MindSkillEvolve plan")
    add_store(s)
    s.add_argument("trajectories_json")
    s.add_argument("--supervised", action="store_true")
    s.add_argument("--min-batch", type=int, default=2)
    s.set_defaults(func=cmd_skill_evolve)

    s = sub.add_parser("pref-signal", help="PAMU preference signal")
    add_store(s)
    s.add_argument("text")
    s.set_defaults(func=cmd_pref_signal)

    s = sub.add_parser("pref-update", help="PAMU preference update plan")
    add_store(s)
    s.add_argument("observations_json")
    s.add_argument("--window", type=int, default=3)
    s.add_argument("--beta", type=float, default=0.8)
    s.add_argument("--lambda", type=float, default=0.5, dest="lam")
    s.add_argument("--delta", type=float, default=0.35)
    s.set_defaults(func=cmd_pref_update)

    s = sub.add_parser("pref-fuse", help="PAMU fuse SW+EMA")
    add_store(s)
    s.add_argument("sw_json")
    s.add_argument("ema_json")
    s.add_argument("--lambda", type=float, default=0.5, dest="lam")
    s.set_defaults(func=cmd_pref_fuse)

    s = sub.add_parser("pref-change", help="PAMU change detect")
    add_store(s)
    s.add_argument("sw_json")
    s.add_argument("ema_json")
    s.add_argument("--delta", type=float, default=0.35)
    s.set_defaults(func=cmd_pref_change)

    s = sub.add_parser("pref-prompt", help="PAMU preference prompt")
    add_store(s)
    s.add_argument("fused_json")
    s.set_defaults(func=cmd_pref_prompt)

    s = sub.add_parser("beam-categories", help="BEAM category inventory")
    add_store(s)
    s.set_defaults(func=cmd_beam_categories)

    s = sub.add_parser("beam-classify", help="Classify BEAM query")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_beam_classify)

    s = sub.add_parser("knowledge-update", help="BEAM knowledge update check")
    add_store(s)
    s.add_argument("--prior", required=True)
    s.add_argument("--current", required=True)
    s.set_defaults(func=cmd_knowledge_update)

    s = sub.add_parser("abstention-gate", help="BEAM abstention gate")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--evidence-count", type=int, required=True)
    s.add_argument("--min-evidence", type=int, default=1)
    s.set_defaults(func=cmd_abstention_gate)

    s = sub.add_parser("contradiction-plan", help="BEAM contradiction plan")
    add_store(s)
    s.add_argument("statements_json")
    s.set_defaults(func=cmd_contradiction_plan)

    s = sub.add_parser("event-order", help="BEAM event order check")
    add_store(s)
    s.add_argument("events_json")
    s.set_defaults(func=cmd_event_order)

    s = sub.add_parser("halu-stage", help="HaluMem stage localize")
    add_store(s)
    s.add_argument("symptom")
    s.set_defaults(func=cmd_halu_stage)

    s = sub.add_parser("episodic-gist", help="REMem episodic gist")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_episodic_gist)

    s = sub.add_parser("temporal-facts", help="REMem temporal facts")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_temporal_facts)

    s = sub.add_parser("situational-bind", help="REMem situational bind")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_situational_bind)

    s = sub.add_parser("episodic-graph", help="REMem hybrid episodic graph")
    add_store(s)
    s.set_defaults(func=cmd_episodic_graph)

    s = sub.add_parser("agentic-retrieve", help="REMem agentic retrieve plan")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--max-steps", type=int, default=3)
    s.set_defaults(func=cmd_agentic_retrieve)

    s = sub.add_parser("ordinal-event", help="REMem ordinal event query")
    add_store(s)
    s.add_argument("--order", default="first", choices=["first", "last"])
    s.set_defaults(func=cmd_ordinal_event)

    s = sub.add_parser("memcell", help="EverMemOS form MemCell")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_memcell)

    s = sub.add_parser("memscenes", help="EverMemOS consolidate MemScenes")
    add_store(s)
    s.set_defaults(func=cmd_memscenes)

    s = sub.add_parser("foresight-filter", help="EverMemOS foresight filter")
    add_store(s)
    s.set_defaults(func=cmd_foresight_filter)

    s = sub.add_parser("recollect", help="EverMemOS reconstructive recollect")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--n-scenes", type=int, default=3)
    s.add_argument("--k-episodes", type=int, default=5)
    s.set_defaults(func=cmd_recollect)

    s = sub.add_parser("profile-evolve", help="EverMemOS profile evolve plan")
    add_store(s)
    s.set_defaults(func=cmd_profile_evolve)

    s = sub.add_parser("necessity-check", help="EverMemOS necessity/sufficiency")
    add_store(s)
    s.add_argument("--retrieved-count", type=int, required=True)
    s.add_argument("--min-needed", type=int, default=1)
    s.add_argument("--max-sufficient", type=int, default=10)
    s.set_defaults(func=cmd_necessity_check)

    s = sub.add_parser("memory-tier", help="MemoryOS classify STM/MTM/LPM")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_memory_tier)

    s = sub.add_parser("heat-score", help="MemoryOS segment heat")
    add_store(s)
    s.add_argument("--n-visit", type=int, default=0)
    s.add_argument("--l-interaction", type=int, default=1)
    s.add_argument("--delta-t", type=float, default=0.0)
    s.set_defaults(func=cmd_heat_score)

    s = sub.add_parser("segment-pages", help="MemoryOS segmented paging")
    add_store(s)
    s.set_defaults(func=cmd_segment_pages)

    s = sub.add_parser("stm-to-mtm", help="MemoryOS STM→MTM FIFO plan")
    add_store(s)
    s.add_argument("page_ids", nargs="+")
    s.add_argument("--capacity", type=int, default=5)
    s.set_defaults(func=cmd_stm_to_mtm)

    s = sub.add_parser("mtm-evict", help="MemoryOS MTM heat eviction plan")
    add_store(s)
    s.add_argument("--max-segments", type=int, default=3)
    s.set_defaults(func=cmd_mtm_evict)

    s = sub.add_parser("promote-lpm", help="MemoryOS promote-to-LPM plan")
    add_store(s)
    s.add_argument("--tau", type=float, default=5.0)
    s.set_defaults(func=cmd_promote_lpm)

    s = sub.add_parser("hier-retrieve", help="MemoryOS hierarchical retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--top-m", type=int, default=2)
    s.add_argument("--top-k", type=int, default=3)
    s.set_defaults(func=cmd_hier_retrieve)

    s = sub.add_parser("episodic-narrative", help="NEMORI episodic narrative")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_episodic_narrative)

    s = sub.add_parser("anticipatory-schema", help="NEMORI anticipatory schema")
    add_store(s)
    s.add_argument("cue")
    s.set_defaults(func=cmd_anticipatory_schema)

    s = sub.add_parser("prediction-error", help="NEMORI prediction-error distill")
    add_store(s)
    s.add_argument("--actual", required=True)
    s.add_argument("--anticipated", required=True)
    s.set_defaults(func=cmd_prediction_error)

    s = sub.add_parser("deserves-memory", help="NEMORI deserves-memory gate")
    add_store(s)
    s.add_argument("--actual", required=True)
    s.add_argument("--anticipated", required=True)
    s.set_defaults(func=cmd_deserves_memory)

    s = sub.add_parser("distill-batch", help="NEMORI batch distill plan")
    add_store(s)
    s.add_argument("--entry-id", action="append", dest="entry_ids")
    s.set_defaults(func=cmd_distill_batch)

    s = sub.add_parser("classify-network", help="Hindsight network classify")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_classify_network)

    s = sub.add_parser("retain-plan", help="Hindsight retain plan")
    add_store(s)
    s.set_defaults(func=cmd_retain_plan)

    s = sub.add_parser("network-inventory", help="Hindsight network inventory")
    add_store(s)
    s.set_defaults(func=cmd_network_inventory)

    s = sub.add_parser("recall-multi", help="Hindsight multi-strategy recall")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--token-budget", type=int, default=400)
    s.add_argument("--top-k", type=int, default=5)
    s.set_defaults(func=cmd_recall_multi)

    s = sub.add_parser("opinion-reinforce", help="Hindsight opinion reinforce")
    add_store(s)
    s.add_argument("opinion_text")
    s.add_argument("--supporting", action="store_true", default=True)
    s.add_argument("--weaken", action="store_true")
    s.add_argument("--prior", type=float, default=0.5)
    s.set_defaults(func=cmd_opinion_reinforce)

    s = sub.add_parser("reflect-plan", help="Hindsight reflect plan")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--skepticism", type=int, default=3)
    s.add_argument("--literalism", type=int, default=3)
    s.add_argument("--empathy", type=int, default=3)
    s.add_argument("--bias", type=float, default=0.5)
    s.set_defaults(func=cmd_reflect_plan)

    s = sub.add_parser("distill-strategy", help="ReasoningBank distill strategy")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("--outcome", choices=["success", "failure"], default="success")
    s.set_defaults(func=cmd_distill_strategy)

    s = sub.add_parser("failure-lesson-gate", help="ReasoningBank failure gate")
    add_store(s)
    s.add_argument("--success-count", type=int, required=True)
    s.add_argument("--failure-count", type=int, required=True)
    s.set_defaults(func=cmd_failure_lesson_gate)

    s = sub.add_parser("matts-plan", help="ReasoningBank MaTTS plan")
    add_store(s)
    s.add_argument("--mode", choices=["parallel", "sequential"], default="parallel")
    s.add_argument("--n", type=int, default=3)
    s.add_argument("--hint", default="")
    s.set_defaults(func=cmd_matts_plan)

    s = sub.add_parser("skill-bank", help="MemSkill init skill bank")
    add_store(s)
    s.set_defaults(func=cmd_skill_bank)

    s = sub.add_parser("span-partition", help="MemSkill span partition")
    add_store(s)
    s.add_argument("text")
    s.add_argument("--max-chars", type=int, default=120)
    s.set_defaults(func=cmd_span_partition)

    s = sub.add_parser("select-skills", help="MemSkill select skills")
    add_store(s)
    s.add_argument("span_text")
    s.add_argument("--top-k", type=int, default=2)
    s.set_defaults(func=cmd_select_skills)

    s = sub.add_parser("execute-skills", help="MemSkill execute skill plan")
    add_store(s)
    s.add_argument("span_text")
    s.set_defaults(func=cmd_execute_skills)

    s = sub.add_parser("hard-case", help="MemSkill record hard case")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--predicted", default="")
    s.add_argument("--expected", default="")
    s.set_defaults(func=cmd_hard_case)

    s = sub.add_parser("designer-evolve", help="MemSkill designer evolve plan")
    add_store(s)
    s.add_argument("--query", action="append", dest="queries")
    s.set_defaults(func=cmd_designer_evolve)

    s = sub.add_parser("memory-op", help="Memory-R1 classify memory op")
    add_store(s)
    s.add_argument("candidate")
    s.set_defaults(func=cmd_memory_op)

    s = sub.add_parser("noop-gate", help="Memory-R1 NOOP gate")
    add_store(s)
    s.add_argument("candidate")
    s.set_defaults(func=cmd_noop_gate)

    s = sub.add_parser("memory-op-plan", help="Memory-R1 memory op plan")
    add_store(s)
    s.add_argument("candidate")
    s.set_defaults(func=cmd_memory_op_plan)

    s = sub.add_parser("conflict-update", help="Memory-R1 conflict UPDATE plan")
    add_store(s)
    s.add_argument("--old", required=True)
    s.add_argument("--new", required=True)
    s.set_defaults(func=cmd_conflict_update)

    s = sub.add_parser("delete-stale", help="Memory-R1 DELETE stale plan")
    add_store(s)
    s.set_defaults(func=cmd_delete_stale)

    s = sub.add_parser("graph-tier", help="G-Memory classify graph tier")
    add_store(s)
    s.add_argument("entry_id")
    s.set_defaults(func=cmd_graph_tier)

    s = sub.add_parser("query-graph", help="G-Memory build query graph")
    add_store(s)
    s.set_defaults(func=cmd_query_graph)

    s = sub.add_parser("insight-up", help="G-Memory upward insight traverse")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_insight_up)

    s = sub.add_parser("interaction-down", help="G-Memory downward traverse")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_interaction_down)

    s = sub.add_parser("bidir-retrieve", help="G-Memory bi-directional retrieve")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_bidir_retrieve)

    s = sub.add_parser("hierarchy-update", help="G-Memory hierarchy update plan")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--status", choices=["Failed", "Resolved"], default="Resolved")
    s.set_defaults(func=cmd_hierarchy_update)

    s = sub.add_parser("meta-thinker", help="MemMA Meta-Thinker guidance")
    add_store(s)
    s.add_argument("chunk")
    s.add_argument("--mode", choices=["construction", "retrieval"], default="construction")
    s.set_defaults(func=cmd_meta_thinker)

    s = sub.add_parser("answerability", help="MemMA answerability check")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_answerability)

    s = sub.add_parser("probe-qa", help="MemMA synthesize probe QA")
    add_store(s)
    s.add_argument("session_text")
    s.set_defaults(func=cmd_probe_qa)

    s = sub.add_parser("verify-probes", help="MemMA verify probes (JSON)")
    add_store(s)
    s.add_argument("probes_json")
    s.set_defaults(func=cmd_verify_probes)

    s = sub.add_parser("repair-probes", help="MemMA repair from probes JSON")
    add_store(s)
    s.add_argument("probes_json")
    s.add_argument("results_json")
    s.set_defaults(func=cmd_repair_probes)

    s = sub.add_parser("induce-workflow", help="AWM induce workflow")
    add_store(s)
    s.add_argument("task")
    s.add_argument("steps_json")
    s.add_argument("--fail", action="store_true")
    s.set_defaults(func=cmd_induce_workflow)

    s = sub.add_parser("online-induce-gate", help="AWM online induce gate")
    add_store(s)
    s.add_argument("--success", action="store_true")
    s.set_defaults(func=cmd_online_induce_gate)

    s = sub.add_parser("workflow-add-plan", help="AWM workflow add plan JSON")
    add_store(s)
    s.add_argument("workflow_json")
    s.add_argument("--existing-json", default="[]")
    s.set_defaults(func=cmd_workflow_add_plan)

    s = sub.add_parser("retrieve-workflows", help="AWM retrieve workflows")
    add_store(s)
    s.add_argument("workflows_json")
    s.add_argument("query")
    s.add_argument("--top-k", type=int, default=3)
    s.set_defaults(func=cmd_retrieve_workflows)

    s = sub.add_parser("workflow-step-budget", help="AWM step budget")
    add_store(s)
    s.add_argument("baseline_steps", type=int)
    s.add_argument("workflow_step_count", type=int)
    s.set_defaults(func=cmd_workflow_step_budget)

    s = sub.add_parser("distill-retrieval-exp", help="RRM distill retrieval experience")
    add_store(s)
    s.add_argument("query")
    s.add_argument("outcome", choices=["success", "failure"])
    s.add_argument("--anomaly", default="none")
    s.add_argument("--hint", default="")
    s.set_defaults(func=cmd_distill_retrieval_exp)

    s = sub.add_parser("anomaly-trigger", help="RRM anomaly trigger")
    add_store(s)
    s.add_argument("--hits", type=int, default=0)
    s.add_argument("--query", default="")
    s.add_argument("--priors-json", default="[]")
    s.add_argument("--rounds", type=int, default=0)
    s.add_argument("--max-rounds", type=int, default=5)
    s.set_defaults(func=cmd_anomaly_trigger)

    s = sub.add_parser("query-level-guidance", help="RRM query-level guidance")
    add_store(s)
    s.add_argument("experiences_json")
    s.add_argument("query")
    s.add_argument("--anomaly", default="none")
    s.set_defaults(func=cmd_query_level_guidance)

    s = sub.add_parser("experience-lifecycle", help="RRM experience lifecycle score")
    add_store(s)
    s.add_argument("--usage", type=int, default=0)
    s.add_argument("--reuse-success", type=int, default=0)
    s.add_argument("--age-days", type=float, default=0.0)
    s.set_defaults(func=cmd_experience_lifecycle)

    s = sub.add_parser("prune-experience", help="RRM prune experience plan")
    add_store(s)
    s.add_argument("experiences_json")
    s.add_argument("--capacity", type=int, default=10)
    s.set_defaults(func=cmd_prune_experience)

    s = sub.add_parser("isolate-factual", help="RRM isolate factual vs procedural")
    add_store(s)
    s.add_argument("answer_ids_json")
    s.add_argument("experience_ids_json")
    s.set_defaults(func=cmd_isolate_factual)

    s = sub.add_parser("multi-faceted-distill", help="ReMe multi-faceted distill")
    add_store(s)
    s.add_argument("scenario")
    s.add_argument("outcome", choices=["success", "failure"])
    s.add_argument("--steps-json", default="[]")
    s.add_argument("--failure-reason", default="")
    s.add_argument("--peer-success", default="")
    s.set_defaults(func=cmd_multi_faceted_distill)

    s = sub.add_parser("scenario-retrieve", help="ReMe scenario retrieve")
    add_store(s)
    s.add_argument("pool_json")
    s.add_argument("scenario")
    s.add_argument("--top-k", type=int, default=3)
    s.set_defaults(func=cmd_scenario_retrieve)

    s = sub.add_parser("adaptive-rewrite", help="ReMe adaptive rewrite plan")
    add_store(s)
    s.add_argument("experiences_json")
    s.add_argument("new_scenario")
    s.set_defaults(func=cmd_adaptive_rewrite)

    s = sub.add_parser("utility-after-reuse", help="ReMe utility after reuse")
    add_store(s)
    s.add_argument("freq", type=int)
    s.add_argument("utility", type=int)
    s.add_argument("--helped", action="store_true")
    s.set_defaults(func=cmd_utility_after_reuse)

    s = sub.add_parser("selective-add", help="ReMe selective add plan")
    add_store(s)
    s.add_argument("candidate_json")
    s.add_argument("--pool-json", default="[]")
    s.add_argument("--unvalidated", action="store_true")
    s.set_defaults(func=cmd_selective_add)

    s = sub.add_parser("utility-prune", help="ReMe utility prune plan")
    add_store(s)
    s.add_argument("pool_json")
    s.add_argument("--alpha", type=int, default=3)
    s.add_argument("--beta", type=float, default=0.3)
    s.set_defaults(func=cmd_utility_prune)

    s = sub.add_parser("cheatsheet-snippet", help="DC extract cheatsheet snippet")
    add_store(s)
    s.add_argument("kind", choices=["strategy", "code", "insight", "formula"])
    s.add_argument("title")
    s.add_argument("body")
    s.set_defaults(func=cmd_cheatsheet_snippet)

    s = sub.add_parser("retrieve-cheatsheet", help="DC retrieve cheatsheet")
    add_store(s)
    s.add_argument("memory_json")
    s.add_argument("query")
    s.add_argument("--top-k", type=int, default=3)
    s.set_defaults(func=cmd_retrieve_cheatsheet)

    s = sub.add_parser("curator-decide", help="DC curator decide")
    add_store(s)
    s.add_argument("--useful", action="store_true")
    s.add_argument("--faulty", action="store_true")
    s.add_argument("--superseded", action="store_true")
    s.set_defaults(func=cmd_curator_decide)

    s = sub.add_parser("compact-memory-gate", help="DC compact memory gate")
    add_store(s)
    s.add_argument("entry_chars", type=int)
    s.add_argument("--memory-chars", type=int, default=0)
    s.set_defaults(func=cmd_compact_memory_gate)

    s = sub.add_parser("dc-rs-order", help="DC-RS/Cu order check")
    add_store(s)
    s.add_argument("steps_json")
    s.set_defaults(func=cmd_dc_rs_order)

    s = sub.add_parser("experience-pool-add", help="ExpeL experience pool add")
    add_store(s)
    s.add_argument("task")
    s.add_argument("outcome", choices=["success", "failure"])
    s.add_argument("--summary", default="")
    s.set_defaults(func=cmd_experience_pool_add)

    s = sub.add_parser("insight-op", help="ExpeL insight op JSON")
    add_store(s)
    s.add_argument("insights_json")
    s.add_argument("op", choices=["ADD", "EDIT", "UPVOTE", "DOWNVOTE"])
    s.add_argument("--text", default="")
    s.add_argument("--insight-id", default=None)
    s.set_defaults(func=cmd_insight_op)

    s = sub.add_parser("insight-importance-gate", help="ExpeL importance gate")
    add_store(s)
    s.add_argument("insights_json")
    s.set_defaults(func=cmd_insight_importance_gate)

    s = sub.add_parser("retrieve-insights", help="ExpeL retrieve insights")
    add_store(s)
    s.add_argument("insights_json")
    s.add_argument("query")
    s.add_argument("--top-k", type=int, default=5)
    s.set_defaults(func=cmd_retrieve_insights)

    s = sub.add_parser("retrieve-similar-successes", help="ExpeL similar successes")
    add_store(s)
    s.add_argument("pool_json")
    s.add_argument("task")
    s.add_argument("--top-k", type=int, default=3)
    s.set_defaults(func=cmd_retrieve_similar_successes)

    s = sub.add_parser("prospective-reflect", help="RMM prospective reflect")
    add_store(s)
    s.add_argument("topic")
    s.add_argument("segment")
    s.add_argument("--granularity", default="turn", choices=["utterance", "turn", "session"])
    s.set_defaults(func=cmd_prospective_reflect)

    s = sub.add_parser("topic-memory-bank", help="RMM topic memory bank")
    add_store(s)
    s.add_argument("memories_json")
    s.set_defaults(func=cmd_topic_memory_bank)

    s = sub.add_parser("retrieve-topic-memories", help="RMM retrieve topic memories")
    add_store(s)
    s.add_argument("memories_json")
    s.add_argument("query")
    s.add_argument("--top-k", type=int, default=5)
    s.set_defaults(func=cmd_retrieve_topic_memories)

    s = sub.add_parser("retrospective-cite", help="RMM retrospective cite feedback")
    add_store(s)
    s.add_argument("cited_json")
    s.add_argument("retrieved_json")
    s.set_defaults(func=cmd_retrospective_cite)

    s = sub.add_parser("rerank-memories", help="RMM rerank memories")
    add_store(s)
    s.add_argument("candidates_json")
    s.add_argument("query")
    s.add_argument("--boosts-json", default="{}")
    s.set_defaults(func=cmd_rerank_memories)

    s = sub.add_parser("retrieval-refine", help="RMM retrieval refine plan")
    add_store(s)
    s.add_argument("memories_json")
    s.add_argument("cited_json")
    s.add_argument("unused_json")
    s.set_defaults(func=cmd_retrieval_refine)

    s = sub.add_parser("collect-trajectory", help="Trace2Skill collect trajectory")
    add_store(s)
    s.add_argument("task")
    s.add_argument("outcome", choices=["success", "failure"])
    s.add_argument("--lesson", default="")
    s.set_defaults(func=cmd_collect_trajectory)

    s = sub.add_parser("propose-patch", help="Trace2Skill propose patch JSON")
    add_store(s)
    s.add_argument("trajectory_json")
    s.add_argument("--base-skill", default="")
    s.add_argument("--analyst", default="auto")
    s.set_defaults(func=cmd_propose_patch)

    s = sub.add_parser("parallel-patch-pool", help="Trace2Skill parallel patch pool")
    add_store(s)
    s.add_argument("trajectories_json")
    s.add_argument("--base-skill", default="")
    s.set_defaults(func=cmd_parallel_patch_pool)

    s = sub.add_parser("merge-patches", help="Trace2Skill hierarchical merge")
    add_store(s)
    s.add_argument("patches_json")
    s.add_argument("--branch", type=int, default=4)
    s.set_defaults(func=cmd_merge_patches)

    s = sub.add_parser("skill-mode-gate", help="Trace2Skill deepen/create gate")
    add_store(s)
    s.add_argument("mode", choices=["deepen", "create"])
    s.add_argument("--human-skill", action="store_true")
    s.set_defaults(func=cmd_skill_mode_gate)

    s = sub.add_parser("prefer-parallel", help="Trace2Skill parallel preference")
    add_store(s)
    s.add_argument("parallel_quality", type=float)
    s.add_argument("sequential_quality", type=float)
    s.add_argument("parallel_minutes", type=float)
    s.add_argument("sequential_minutes", type=float)
    s.set_defaults(func=cmd_prefer_parallel)

    s = sub.add_parser("streaming-task-append", help="Evo-Memory stream append")
    add_store(s)
    s.add_argument("memory_json")
    s.add_argument("task")
    s.add_argument("--prediction", default="")
    s.add_argument("--outcome", default="unknown")
    s.set_defaults(func=cmd_streaming_task_append)

    s = sub.add_parser("exprag-retrieve", help="Evo-Memory ExpRAG retrieve")
    add_store(s)
    s.add_argument("memory_json")
    s.add_argument("query")
    s.add_argument("--top-k", type=int, default=3)
    s.set_defaults(func=cmd_exprag_retrieve)

    s = sub.add_parser("spe-check", help="Evo-Memory SPE order check")
    add_store(s)
    s.add_argument("steps_json")
    s.set_defaults(func=cmd_spe_check)

    s = sub.add_parser("evomem-refine", help="Evo-Memory refine plan")
    add_store(s)
    s.add_argument("memory_size", type=int)
    s.add_argument("--max-memory", type=int, default=50)
    s.add_argument("--miss", action="store_true")
    s.add_argument("--noisy", action="store_true")
    s.set_defaults(func=cmd_evomem_refine)

    s = sub.add_parser("evolution-similarity", help="Evo-Memory similarity hint")
    add_store(s)
    s.add_argument("query_tokens_json")
    s.add_argument("cluster_tokens_json")
    s.set_defaults(func=cmd_evolution_similarity)

    s = sub.add_parser("classify-memory-slot", help="Mem-α classify memory slot")
    add_store(s)
    s.add_argument("text")
    s.add_argument("--timestamp", action="store_true")
    s.set_defaults(func=cmd_classify_memory_slot)

    s = sub.add_parser("memory-write-op", help="Mem-α memory write op")
    add_store(s)
    s.add_argument("slot", choices=["core", "episodic", "semantic"])
    s.add_argument("op", choices=["insert", "update", "delete"])
    s.add_argument("--content", default="")
    s.add_argument("--record-id", default=None)
    s.set_defaults(func=cmd_memory_write_op)

    s = sub.add_parser("process-chunk", help="Mem-α process chunk plan")
    add_store(s)
    s.add_argument("chunk")
    s.add_argument("--core-chars", type=int, default=0)
    s.set_defaults(func=cmd_process_chunk)

    s = sub.add_parser("compression-ratio", help="Mem-α compression ratio")
    add_store(s)
    s.add_argument("memory_chars", type=int)
    s.add_argument("chunk_chars", type=int)
    s.set_defaults(func=cmd_compression_ratio)

    s = sub.add_parser("memalpha-reward", help="Mem-α reward bundle JSON")
    add_store(s)
    s.add_argument("params_json")
    s.set_defaults(func=cmd_memalpha_reward)

    s = sub.add_parser("length-gen-gate", help="Mem-α length generalization gate")
    add_store(s)
    s.add_argument("train_max_tokens", type=int)
    s.add_argument("eval_tokens", type=int)
    s.set_defaults(func=cmd_length_gen_gate)

    s = sub.add_parser("classify-failure", help="AgentHER classify failure")
    add_store(s)
    s.add_argument("failure_type")
    s.add_argument("--obs-chars", type=int, default=0)
    s.add_argument("--severity", type=float, default=None)
    s.set_defaults(func=cmd_classify_failure)

    s = sub.add_parser("replay-outcome", help="AgentHER extract replay outcome")
    add_store(s)
    s.add_argument("observations_json")
    s.set_defaults(func=cmd_replay_outcome)

    s = sub.add_parser("hindsight-relabel", help="AgentHER hindsight relabel")
    add_store(s)
    s.add_argument("original_goal")
    s.add_argument("achievements_json")
    s.add_argument("--confidence", type=float, default=0.85)
    s.set_defaults(func=cmd_hindsight_relabel)

    s = sub.add_parser("multi-judge", help="AgentHER multi-judge accept")
    add_store(s)
    s.add_argument("confidence_j1", type=float)
    s.add_argument("confidence_j2", type=float)
    s.add_argument("--theta", type=float, default=0.7)
    s.set_defaults(func=cmd_multi_judge)

    s = sub.add_parser("package-training-pair", help="AgentHER package training pair")
    add_store(s)
    s.add_argument("format", choices=["SFT", "DPO", "ShareGPT"])
    s.add_argument("hindsight_goal")
    s.add_argument("original_goal")
    s.add_argument("--summary", default="")
    s.set_defaults(func=cmd_package_training_pair)

    s = sub.add_parser("distill-planning-error", help="PreFlect distill planning error")
    add_store(s)
    s.add_argument("error_id")
    s.add_argument("pattern")
    s.add_argument("--success-hint", default="")
    s.add_argument("--failure-hint", default="")
    s.set_defaults(func=cmd_distill_planning_error)

    s = sub.add_parser("prospective-critique", help="PreFlect prospective critique")
    add_store(s)
    s.add_argument("plan_steps_json")
    s.add_argument("planning_errors_json")
    s.set_defaults(func=cmd_prospective_critique)

    s = sub.add_parser("revise-plan", help="PreFlect revise plan proposal")
    add_store(s)
    s.add_argument("original_steps_json")
    s.add_argument("avoid_patterns_json")
    s.add_argument("--guard", default="verify precondition")
    s.set_defaults(func=cmd_revise_plan)

    s = sub.add_parser("replan-deviation", help="PreFlect replan on deviation")
    add_store(s)
    s.add_argument("expected")
    s.add_argument("actual")
    s.add_argument("remaining_steps", type=int)
    s.set_defaults(func=cmd_replan_deviation)

    s = sub.add_parser("preflect-gate", help="PreFlect before-execute gate")
    add_store(s)
    s.add_argument("--needs-revise", action="store_true")
    s.add_argument("--revised-ready", action="store_true")
    s.set_defaults(func=cmd_preflect_gate)

    s = sub.add_parser("orch-action", help="SkillFlow orchestration action")
    add_store(s)
    s.add_argument("action_type", choices=["skill", "act", "accept"])
    s.add_argument("--skill-id", default=None)
    s.add_argument("--step", type=int, default=0)
    s.set_defaults(func=cmd_orch_action)

    s = sub.add_parser("ttb-residual", help="SkillFlow TTB residual")
    add_store(s)
    s.add_argument("log_forward", type=float)
    s.add_argument("log_backward", type=float)
    s.add_argument("log_reward", type=float)
    s.set_defaults(func=cmd_ttb_residual)

    s = sub.add_parser("step-importance", help="SkillFlow step importance")
    add_store(s)
    s.add_argument("log_forward", type=float)
    s.add_argument("log_backward", type=float)
    s.set_defaults(func=cmd_step_importance)

    s = sub.add_parser("skill-marginal-flow", help="SkillFlow skill marginal flow")
    add_store(s)
    s.add_argument("skill_id")
    s.add_argument("flows_json")
    s.add_argument("--index", type=int, default=0)
    s.set_defaults(func=cmd_skill_marginal_flow)

    s = sub.add_parser("skill-curation", help="SkillFlow skill curation")
    add_store(s)
    s.add_argument("mean_log_flow", type=float)
    s.add_argument("centered_log_share", type=float)
    s.add_argument("--jensen-gap", type=float, default=0.0)
    s.add_argument("--high-imp", action="store_true")
    s.set_defaults(func=cmd_skill_curation)

    s = sub.add_parser("phase-evolve", help="SkillFlow phase evolve gate")
    add_store(s)
    s.add_argument("residual_mean", type=float)
    s.add_argument("residual_floor", type=float)
    s.set_defaults(func=cmd_phase_evolve)

    s = sub.add_parser("define-skill", help="ProcMEM define skill triplet")
    add_store(s)
    s.add_argument("skill_id")
    s.add_argument("activation")
    s.add_argument("execution")
    s.add_argument("termination")
    s.set_defaults(func=cmd_define_skill)

    s = sub.add_parser("skill-select", help="ProcMEM skill select gate")
    add_store(s)
    s.add_argument("state_text")
    s.add_argument("activation")
    s.set_defaults(func=cmd_skill_select)

    s = sub.add_parser("skill-terminate", help="ProcMEM skill terminate check")
    add_store(s)
    s.add_argument("observation")
    s.add_argument("termination")
    s.set_defaults(func=cmd_skill_terminate)

    s = sub.add_parser("semantic-gradient", help="ProcMEM semantic gradient")
    add_store(s)
    s.add_argument("success_trace")
    s.add_argument("failure_trace")
    s.add_argument("base_skill_id")
    s.set_defaults(func=cmd_semantic_gradient)

    s = sub.add_parser("ppo-gate", help="ProcMEM PPO gate verify")
    add_store(s)
    s.add_argument("candidate_score", type=float)
    s.add_argument("incumbent_score", type=float)
    s.set_defaults(func=cmd_ppo_gate)

    s = sub.add_parser("skill-maintain", help="ProcMEM skill score maintain")
    add_store(s)
    s.add_argument("frequency", type=int)
    s.add_argument("avg_gain", type=float)
    s.set_defaults(func=cmd_skill_maintain)

    s = sub.add_parser("ieu-record", help="MemRL IEU record")
    add_store(s)
    s.add_argument("intent")
    s.add_argument("experience")
    s.add_argument("--utility", type=float, default=0.0)
    s.set_defaults(func=cmd_ieu_record)

    s = sub.add_parser("two-phase-retrieve", help="MemRL two-phase retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("memories_json")
    s.set_defaults(func=cmd_two_phase_retrieve)

    s = sub.add_parser("utility-q-update", help="MemRL utility Q update")
    add_store(s)
    s.add_argument("current_q", type=float)
    s.add_argument("reward", type=float)
    s.add_argument("--next-max-q", type=float, default=0.0)
    s.set_defaults(func=cmd_utility_q_update)

    s = sub.add_parser("value-aware-select", help="MemRL value-aware select")
    add_store(s)
    s.add_argument("candidates_json")
    s.add_argument("--min-utility", type=float, default=0.0)
    s.set_defaults(func=cmd_value_aware_select)

    s = sub.add_parser("sim-util-warn", help="MemRL semantic vs utility warn")
    add_store(s)
    s.add_argument("similarity", type=float)
    s.add_argument("utility", type=float)
    s.set_defaults(func=cmd_sim_util_warn)

    s = sub.add_parser("distill-principle", help="EvolveR distill principle")
    add_store(s)
    s.add_argument("kind", choices=["success", "failure"])
    s.add_argument("description")
    s.set_defaults(func=cmd_distill_principle)

    s = sub.add_parser("principle-dedupe", help="EvolveR principle dedupe")
    add_store(s)
    s.add_argument("candidate_desc")
    s.add_argument("existing_descs_json")
    s.set_defaults(func=cmd_principle_dedupe)

    s = sub.add_parser("principle-score", help="EvolveR principle metric score")
    add_store(s)
    s.add_argument("succ_count", type=int)
    s.add_argument("use_count", type=int)
    s.set_defaults(func=cmd_principle_score)

    s = sub.add_parser("search-exp-action", help="EvolveR search experience action")
    add_store(s)
    s.add_argument(
        "action", choices=["search_experience", "search_knowledge", "answer"]
    )
    s.add_argument("--query", default="")
    s.set_defaults(func=cmd_search_exp_action)

    s = sub.add_parser("lifecycle-phase", help="EvolveR lifecycle phase gate")
    add_store(s)
    s.add_argument("phase", choices=["online", "offline"])
    s.add_argument("--mutate-policy", action="store_true")
    s.add_argument("--distill", action="store_true")
    s.set_defaults(func=cmd_lifecycle_phase)

    s = sub.add_parser("prune-principles", help="EvolveR prune low-score principles")
    add_store(s)
    s.add_argument("scores_json")
    s.set_defaults(func=cmd_prune_principles)

    s = sub.add_parser("self-question", help="AgentEvolver self-question task")
    add_store(s)
    s.add_argument("exploration_summary")
    s.add_argument("--preference", default="")
    s.set_defaults(func=cmd_self_question)

    s = sub.add_parser("exp-when-content", help="AgentEvolver experience when/content")
    add_store(s)
    s.add_argument("when_to_use")
    s.add_argument("content")
    s.set_defaults(func=cmd_exp_when_content)

    s = sub.add_parser("mixed-rollout", help="AgentEvolver mixed rollout split")
    add_store(s)
    s.add_argument("total_rollouts", type=int)
    s.add_argument("--eta", type=float, default=0.5)
    s.set_defaults(func=cmd_mixed_rollout)

    s = sub.add_parser("attribute-credit", help="AgentEvolver attribute step credit")
    add_store(s)
    s.add_argument("step_scores_json")
    s.add_argument("outcome_reward", type=float)
    s.set_defaults(func=cmd_attribute_credit)

    s = sub.add_parser("curiosity-explore", help="AgentEvolver curiosity explore")
    add_store(s)
    s.add_argument("visited_states", type=int)
    s.add_argument("novel_states", type=int)
    s.add_argument("budget", type=int)
    s.set_defaults(func=cmd_curiosity_explore)

    s = sub.add_parser("propose-skill", help="SkillWeaver propose skill")
    add_store(s)
    s.add_argument("description")
    s.add_argument(
        "--kind",
        default="procedural",
        choices=["procedural", "navigational", "info_seeking"],
    )
    s.set_defaults(func=cmd_propose_skill)

    s = sub.add_parser("practice-skill", help="SkillWeaver practice skill")
    add_store(s)
    s.add_argument("skill_id")
    s.add_argument("--success", action="store_true")
    s.add_argument("--steps", type=int, default=1)
    s.set_defaults(func=cmd_practice_skill)

    s = sub.add_parser("distill-skill-api", help="SkillWeaver distill skill API")
    add_store(s)
    s.add_argument("skill_id")
    s.add_argument("description")
    s.set_defaults(func=cmd_distill_skill_api)

    s = sub.add_parser("hone-skill-api", help="SkillWeaver hone skill API")
    add_store(s)
    s.add_argument("--unit-pass", action="store_true")
    s.add_argument("--static-fail", action="store_true")
    s.set_defaults(func=cmd_hone_skill_api)

    s = sub.add_parser("skill-library-reg", help="SkillWeaver library register")
    add_store(s)
    s.add_argument("api_name")
    s.add_argument("library_size", type=int)
    s.set_defaults(func=cmd_skill_library_reg)

    s = sub.add_parser("transfer-skill", help="SkillWeaver transfer gate")
    add_store(s)
    s.add_argument("donor_success_rate", type=float)
    s.add_argument("recipient_baseline", type=float)
    s.set_defaults(func=cmd_transfer_skill)

    s = sub.add_parser("decompose-task", help="SkillRoute decompose task")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_decompose_task)

    s = sub.add_parser("retrieve-step-skills", help="SkillRoute retrieve skills")
    add_store(s)
    s.add_argument("steps_json")
    s.add_argument("catalog_json")
    s.set_defaults(func=cmd_retrieve_step_skills)

    s = sub.add_parser("compose-skill-dag", help="SkillRoute compose DAG")
    add_store(s)
    s.add_argument("step_skills_json")
    s.set_defaults(func=cmd_compose_skill_dag)

    s = sub.add_parser("sad-loop", help="SkillRoute SAD feedback loop")
    add_store(s)
    s.add_argument("prior_steps_json")
    s.add_argument("hints_json")
    s.set_defaults(func=cmd_sad_loop)

    s = sub.add_parser("granularity-match", help="SkillRoute granularity match")
    add_store(s)
    s.add_argument("step_count", type=int)
    s.add_argument("expected_skills", type=int)
    s.set_defaults(func=cmd_granularity_match)

    s = sub.add_parser("propose-reason-task", help="Absolute Zero propose task")
    add_store(s)
    s.add_argument("mode", choices=["induction", "abduction", "deduction"])
    s.add_argument("--hint", default="")
    s.set_defaults(func=cmd_propose_reason_task)

    s = sub.add_parser("validate-task-struct", help="Absolute Zero validate structure")
    add_store(s)
    s.add_argument("mode", choices=["induction", "abduction", "deduction"])
    s.add_argument("--program", action="store_true")
    s.add_argument("--input", action="store_true", dest="has_input")
    s.add_argument("--output", action="store_true", dest="has_output")
    s.set_defaults(func=cmd_validate_task_struct)

    s = sub.add_parser("learnability-reward", help="Absolute Zero learnability")
    add_store(s)
    s.add_argument("mean_solve_rate", type=float)
    s.set_defaults(func=cmd_learnability_reward)

    s = sub.add_parser("solve-reward", help="Absolute Zero solve reward")
    add_store(s)
    s.add_argument("--match", action="store_true")
    s.set_defaults(func=cmd_solve_reward)

    s = sub.add_parser("abszero-objective", help="Absolute Zero joint objective")
    add_store(s)
    s.add_argument("r_propose", type=float)
    s.add_argument("r_solve", type=float)
    s.set_defaults(func=cmd_abszero_objective)

    s = sub.add_parser("executor-verify", help="Absolute Zero executor gate")
    add_store(s)
    s.add_argument("--task-valid", action="store_true")
    s.add_argument("--answer-match", action="store_true")
    s.set_defaults(func=cmd_executor_verify)

    s = sub.add_parser("challenger-propose", help="R-Zero challenger propose")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_challenger_propose)

    s = sub.add_parser("uncertainty-reward", help="R-Zero uncertainty reward")
    add_store(s)
    s.add_argument("empirical_accuracy", type=float)
    s.set_defaults(func=cmd_uncertainty_reward)

    s = sub.add_parser("majority-vote", help="R-Zero majority vote")
    add_store(s)
    s.add_argument("answers_json")
    s.set_defaults(func=cmd_majority_vote)

    s = sub.add_parser("curriculum-band", help="R-Zero curriculum band filter")
    add_store(s)
    s.add_argument("empirical_accuracy", type=float)
    s.add_argument("--delta", type=float, default=0.2)
    s.set_defaults(func=cmd_curriculum_band)

    s = sub.add_parser("solver-reward", help="R-Zero solver binary reward")
    add_store(s)
    s.add_argument("answer")
    s.add_argument("pseudo_label")
    s.set_defaults(func=cmd_solver_reward)

    s = sub.add_parser("coevolve-round", help="R-Zero coevolve round plan")
    add_store(s)
    s.add_argument("round_index", type=int)
    s.add_argument("--challenger-updated", action="store_true")
    s.add_argument("--solver-updated", action="store_true")
    s.set_defaults(func=cmd_coevolve_round)

    s = sub.add_parser("write-turn-mem", help="ECHO write turn memory")
    add_store(s)
    s.add_argument("source_turn_id")
    s.add_argument("finding")
    s.set_defaults(func=cmd_write_turn_mem)

    s = sub.add_parser("select-turn-mem", help="ECHO select turn memories")
    add_store(s)
    s.add_argument("memory_ids_json")
    s.add_argument("budget", type=int)
    s.set_defaults(func=cmd_select_turn_mem)

    s = sub.add_parser("reconstruct-ctx", help="ECHO reconstruct context")
    add_store(s)
    s.add_argument("findings_json")
    s.add_argument("recent_json")
    s.set_defaults(func=cmd_reconstruct_ctx)

    s = sub.add_parser("credit-mask", help="ECHO provenance credit mask")
    add_store(s)
    s.add_argument("sources_json")
    s.add_argument("selected_json")
    s.add_argument("--positive", action="store_true")
    s.set_defaults(func=cmd_credit_mask)

    s = sub.add_parser("collapse-gate", help="ECHO history collapse gate")
    add_store(s)
    s.add_argument("--summary-only", action="store_true")
    s.set_defaults(func=cmd_collapse_gate)

    s = sub.add_parser("budget-binding", help="ECHO budget binding check")
    add_store(s)
    s.add_argument("history_chars", type=int)
    s.add_argument("budget_chars", type=int)
    s.set_defaults(func=cmd_budget_binding)

    s = sub.add_parser("curriculum-task", help="Agent0 curriculum propose")
    add_store(s)
    s.add_argument("task")
    s.add_argument("--requires-tool", action="store_true")
    s.set_defaults(func=cmd_curriculum_task)

    s = sub.add_parser("tool-use-reward", help="Agent0 tool use reward")
    add_store(s)
    s.add_argument("tool_call_count", type=int)
    s.set_defaults(func=cmd_tool_use_reward)

    s = sub.add_parser("curriculum-reward", help="Agent0 curriculum reward")
    add_store(s)
    s.add_argument("r_uncertainty", type=float)
    s.add_argument("r_tool", type=float)
    s.set_defaults(func=cmd_curriculum_reward)

    s = sub.add_parser("executor-frontier", help="Agent0 frontier filter")
    add_store(s)
    s.add_argument("self_consistency", type=float)
    s.set_defaults(func=cmd_executor_frontier)

    s = sub.add_parser("tool-pressure", help="Agent0 tool-aware pressure")
    add_store(s)
    s.add_argument("executor_tool_success_rate", type=float)
    s.add_argument("prior_task_complexity", type=float)
    s.set_defaults(func=cmd_tool_pressure)

    s = sub.add_parser("symbiotic-round", help="Agent0 symbiotic round")
    add_store(s)
    s.add_argument("round_index", type=int)
    s.add_argument("--curriculum-updated", action="store_true")
    s.add_argument("--executor-updated", action="store_true")
    s.set_defaults(func=cmd_symbiotic_round)

    s = sub.add_parser("mae-propose", help="MAE propose question")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_mae_propose)

    s = sub.add_parser("mae-solve", help="MAE solve attempt")
    add_store(s)
    s.add_argument("answer")
    s.set_defaults(func=cmd_mae_solve)

    s = sub.add_parser("mae-judge", help="MAE judge score")
    add_store(s)
    s.add_argument("quality_score", type=float)
    s.add_argument("correctness_score", type=float)
    s.set_defaults(func=cmd_mae_judge)

    s = sub.add_parser("mae-proposer-reward", help="MAE proposer reward")
    add_store(s)
    s.add_argument("quality_score", type=float)
    s.add_argument("--solver-failed", action="store_true")
    s.set_defaults(func=cmd_mae_proposer_reward)

    s = sub.add_parser("mae-quality-filter", help="MAE quality filter")
    add_store(s)
    s.add_argument("quality_score", type=float)
    s.set_defaults(func=cmd_mae_quality_filter)

    s = sub.add_parser("mae-triad", help="MAE triad round plan")
    add_store(s)
    s.add_argument("round_index", type=int)
    s.add_argument("phase", choices=["propose", "solve", "judge"])
    s.set_defaults(func=cmd_mae_triad)

    s = sub.add_parser("sage-challenge", help="SAGE challenge task")
    add_store(s)
    s.add_argument("task")
    s.add_argument("--difficulty", type=float, default=0.5)
    s.set_defaults(func=cmd_sage_challenge)

    s = sub.add_parser("sage-plan", help="SAGE plan steps")
    add_store(s)
    s.add_argument("steps_json")
    s.set_defaults(func=cmd_sage_plan)

    s = sub.add_parser("sage-solve", help="SAGE solve with plan")
    add_store(s)
    s.add_argument("plan_step_count", type=int)
    s.add_argument("followed_steps", type=int)
    s.add_argument("answer")
    s.set_defaults(func=cmd_sage_solve)

    s = sub.add_parser("sage-critic", help="SAGE critic filter")
    add_store(s)
    s.add_argument("question_score", type=float)
    s.add_argument("plan_score", type=float)
    s.set_defaults(func=cmd_sage_critic)

    s = sub.add_parser("sage-drift", help="SAGE drift gate")
    add_store(s)
    s.add_argument("difficulty_delta", type=float)
    s.set_defaults(func=cmd_sage_drift)

    s = sub.add_parser("sage-loop", help="SAGE closed loop round")
    add_store(s)
    s.add_argument("round_index", type=int)
    s.add_argument(
        "phase", choices=["challenge", "plan", "solve", "criticize"]
    )
    s.set_defaults(func=cmd_sage_loop)

    s = sub.add_parser("mem-trigger", help="MemGen memory trigger")
    add_store(s)
    s.add_argument("--boundary", action="store_true")
    s.add_argument("uncertainty", type=float)
    s.set_defaults(func=cmd_mem_trigger)

    s = sub.add_parser("weave-latent", help="MemGen weave latent memory")
    add_store(s)
    s.add_argument("stimulus")
    s.add_argument("--tokens", type=int, default=4)
    s.set_defaults(func=cmd_weave_latent)

    s = sub.add_parser("interweave", help="MemGen interweave cycle")
    add_store(s)
    s.add_argument(
        "step",
        choices=["generate", "monitor", "invoke", "weave", "resume"],
    )
    s.set_defaults(func=cmd_interweave)

    s = sub.add_parser("faculty", help="MemGen faculty classify")
    add_store(s)
    s.add_argument("faculty", choices=["planning", "procedural", "working"])
    s.set_defaults(func=cmd_faculty)

    s = sub.add_parser("weaver-gate", help="MemGen weaver-only update gate")
    add_store(s)
    s.add_argument("--reasoner-frozen", action="store_true")
    s.add_argument("--weaver-updated", action="store_true")
    s.set_defaults(func=cmd_weaver_gate)

    s = sub.add_parser("sparse-invoke", help="MemGen sparse invoke penalty")
    add_store(s)
    s.add_argument("invoke_count", type=int)
    s.set_defaults(func=cmd_sparse_invoke)

    s = sub.add_parser("text-experience", help="Metis text experience store")
    add_store(s)
    s.add_argument("kind", choices=["plan", "fact", "pitfall"])
    s.add_argument("content")
    s.set_defaults(func=cmd_text_experience)

    s = sub.add_parser("crystallize", help="Metis crystallize plan to tool")
    add_store(s)
    s.add_argument("plan_id")
    s.add_argument("reuse_count", type=int)
    s.set_defaults(func=cmd_crystallize)

    s = sub.add_parser("dual-retrieve", help="Metis dual retrieve")
    add_store(s)
    s.add_argument("text_json")
    s.add_argument("code_json")
    s.set_defaults(func=cmd_dual_retrieve)

    s = sub.add_parser("rep-tradeoff", help="Metis representation tradeoff")
    add_store(s)
    s.add_argument("construction_cost", type=float)
    s.add_argument("execution_efficiency", type=float)
    s.add_argument("transferability", type=float)
    s.set_defaults(func=cmd_rep_tradeoff)

    s = sub.add_parser("promote-kind", help="Metis promote kind gate")
    add_store(s)
    s.add_argument("kind", choices=["plan", "fact", "pitfall"])
    s.set_defaults(func=cmd_promote_kind)

    s = sub.add_parser("metis-loop", help="Metis loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["reflect", "crystallize", "retrieve", "act"]
    )
    s.set_defaults(func=cmd_metis_loop)

    s = sub.add_parser("samule-micro", help="SAMULE single trajectory reflect")
    add_store(s)
    s.add_argument("trajectory_id")
    s.add_argument("error_note")
    s.set_defaults(func=cmd_samule_micro)

    s = sub.add_parser("samule-meso", help="SAMULE intra-task taxonomy")
    add_store(s)
    s.add_argument("labels_json")
    s.set_defaults(func=cmd_samule_meso)

    s = sub.add_parser("samule-macro", help="SAMULE inter-task transfer")
    add_store(s)
    s.add_argument("error_type")
    s.add_argument("strategy")
    s.set_defaults(func=cmd_samule_macro)

    s = sub.add_parser("samule-foresight", help="SAMULE foresight reflect")
    add_store(s)
    s.add_argument("predicted")
    s.add_argument("actual")
    s.set_defaults(func=cmd_samule_foresight)

    s = sub.add_parser("samule-fail-gate", help="SAMULE failure-centric gate")
    add_store(s)
    s.add_argument("success_count", type=int)
    s.add_argument("failure_count", type=int)
    s.set_defaults(func=cmd_samule_fail_gate)

    s = sub.add_parser("samule-merge", help="SAMULE merge reflections")
    add_store(s)
    s.add_argument("levels_json")
    s.set_defaults(func=cmd_samule_merge)

    s = sub.add_parser("liveevo-exp", help="LIVE-EVO experience bank")
    add_store(s)
    s.add_argument("experience")
    s.add_argument("--weight", type=float, default=1.0)
    s.set_defaults(func=cmd_liveevo_exp)

    s = sub.add_parser("liveevo-meta", help="LIVE-EVO meta guideline")
    add_store(s)
    s.add_argument("guideline")
    s.set_defaults(func=cmd_liveevo_meta)

    s = sub.add_parser("liveevo-compile", help="LIVE-EVO compile guideline")
    add_store(s)
    s.add_argument("task")
    s.add_argument("experience_count", type=int)
    s.add_argument("--has-meta", action="store_true")
    s.set_defaults(func=cmd_liveevo_compile)

    s = sub.add_parser("liveevo-weight", help="LIVE-EVO update weight")
    add_store(s)
    s.add_argument("weight", type=float)
    s.add_argument("delta", type=float)
    s.set_defaults(func=cmd_liveevo_weight)

    s = sub.add_parser("liveevo-forget", help="LIVE-EVO forget stale")
    add_store(s)
    s.add_argument("weight", type=float)
    s.set_defaults(func=cmd_liveevo_forget)

    s = sub.add_parser("liveevo-round", help="LIVE-EVO online round")
    add_store(s)
    s.add_argument(
        "phase", choices=["retrieve", "compile", "act", "update"]
    )
    s.set_defaults(func=cmd_liveevo_round)

    s = sub.add_parser("socratic-teach", help="Socratic-Zero teacher craft")
    add_store(s)
    s.add_argument("weakness")
    s.add_argument("question")
    s.set_defaults(func=cmd_socratic_teach)

    s = sub.add_parser("socratic-prefer", help="Socratic-Zero solver preference")
    add_store(s)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--success", action="store_true")
    g.add_argument("--failed", action="store_true")
    s.set_defaults(func=cmd_socratic_prefer)

    s = sub.add_parser("socratic-distill", help="Socratic-Zero generator distill")
    add_store(s)
    s.add_argument("teacher_strategy")
    s.set_defaults(func=cmd_socratic_distill)

    s = sub.add_parser("socratic-seed", help="Socratic-Zero seed bootstrap")
    add_store(s)
    s.add_argument("seed_count", type=int)
    s.set_defaults(func=cmd_socratic_seed)

    s = sub.add_parser("socratic-weakness", help="Socratic-Zero weakness target")
    add_store(s)
    s.add_argument("fail_rate", type=float)
    s.set_defaults(func=cmd_socratic_weakness)

    s = sub.add_parser("socratic-loop", help="Socratic-Zero closed loop")
    add_store(s)
    s.add_argument(
        "phase", choices=["teach", "solve", "prefer", "distill"]
    )
    s.set_defaults(func=cmd_socratic_loop)

    s = sub.add_parser("spiral-match", help="SPIRAL self-play match")
    add_store(s)
    s.add_argument("game", choices=["tictactoe", "kuhn_poker", "negotiation"])
    s.add_argument("role")
    s.add_argument("--won", action="store_true")
    s.set_defaults(func=cmd_spiral_match)

    s = sub.add_parser("spiral-rae", help="SPIRAL RAE advantage")
    add_store(s)
    s.add_argument("reward", type=float)
    s.add_argument("role_baseline", type=float)
    s.set_defaults(func=cmd_spiral_rae)

    s = sub.add_parser("spiral-ema", help="SPIRAL baseline EMA")
    add_store(s)
    s.add_argument("baseline", type=float)
    s.add_argument("reward", type=float)
    s.set_defaults(func=cmd_spiral_ema)

    s = sub.add_parser("spiral-pattern", help="SPIRAL transfer pattern")
    add_store(s)
    s.add_argument(
        "pattern",
        choices=["case_by_case", "expected_value", "pattern_recognition"],
    )
    s.set_defaults(func=cmd_spiral_pattern)

    s = sub.add_parser("spiral-opponent", help="SPIRAL opponent strength")
    add_store(s)
    s.add_argument("self_elo", type=float)
    s.add_argument("opponent_elo", type=float)
    s.set_defaults(func=cmd_spiral_opponent)

    s = sub.add_parser("spiral-plan", help="SPIRAL multi-game plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["match", "rae", "baseline", "transfer"]
    )
    s.set_defaults(func=cmd_spiral_plan)

    s = sub.add_parser("smith-store", help="SMITH store memory")
    add_store(s)
    s.add_argument("tier", choices=["procedural", "semantic", "episodic"])
    s.add_argument("content")
    s.set_defaults(func=cmd_smith_store)

    s = sub.add_parser("smith-tool", help="SMITH create tool")
    add_store(s)
    s.add_argument("tool_name")
    s.add_argument("--sandbox-pass", action="store_true")
    s.set_defaults(func=cmd_smith_tool)

    s = sub.add_parser("smith-episode", help="SMITH retrieve episode")
    add_store(s)
    s.add_argument("similarity", type=float)
    s.set_defaults(func=cmd_smith_episode)

    s = sub.add_parser("smith-curriculum", help="SMITH curriculum difficulty")
    add_store(s)
    s.add_argument("ensemble_fail_rate", type=float)
    s.set_defaults(func=cmd_smith_curriculum)

    s = sub.add_parser("smith-reuse", help="SMITH tool reuse gate")
    add_store(s)
    s.add_argument("--tool-exists", action="store_true")
    s.add_argument("--task-similar", action="store_true")
    s.set_defaults(func=cmd_smith_reuse)

    s = sub.add_parser("smith-loop", help="SMITH loop plan")
    add_store(s)
    s.add_argument("phase", choices=["store", "tool", "retrieve", "act"])
    s.set_defaults(func=cmd_smith_loop)

    s = sub.add_parser("hmem-leaf", help="H-Mem leaf event")
    add_store(s)
    s.add_argument("topic")
    s.add_argument("timestamp")
    s.set_defaults(func=cmd_hmem_leaf)

    s = sub.add_parser("hmem-consolidate", help="H-Mem consolidate nodes")
    add_store(s)
    s.add_argument("time_gap", type=float)
    s.add_argument("--same-topic", action="store_true")
    s.set_defaults(func=cmd_hmem_consolidate)

    s = sub.add_parser("hmem-link", help="H-Mem link entities")
    add_store(s)
    s.add_argument("entity_a")
    s.add_argument("entity_b")
    s.add_argument("relation")
    s.set_defaults(func=cmd_hmem_link)

    s = sub.add_parser("hmem-decompose", help="H-Mem decompose query")
    add_store(s)
    s.add_argument("sub_queries_json")
    s.set_defaults(func=cmd_hmem_decompose)

    s = sub.add_parser("hmem-hybrid", help="H-Mem hybrid retrieve")
    add_store(s)
    s.add_argument("tree_hits", type=int)
    s.add_argument("graph_hops", type=int)
    s.set_defaults(func=cmd_hmem_hybrid)

    s = sub.add_parser("hmem-evolution", help="H-Mem evolution gate")
    add_store(s)
    s.add_argument("short_term_count", type=int)
    s.add_argument("consolidated_count", type=int)
    s.set_defaults(func=cmd_hmem_evolution)

    s = sub.add_parser("himem-segment", help="HiMem segment episode")
    add_store(s)
    s.add_argument("topic")
    s.add_argument("surprise", type=float)
    s.add_argument("--surprise-threshold", type=float, default=0.5)
    s.set_defaults(func=cmd_himem_segment)

    s = sub.add_parser("himem-note", help="HiMem extract note")
    add_store(s)
    s.add_argument("knowledge")
    s.set_defaults(func=cmd_himem_note)

    s = sub.add_parser("himem-link", help="HiMem link episode note")
    add_store(s)
    s.add_argument("episode_id")
    s.add_argument("note_id")
    s.set_defaults(func=cmd_himem_link)

    s = sub.add_parser("himem-retrieve", help="HiMem retrieve strategy")
    add_store(s)
    s.add_argument("mode", choices=["hybrid", "best_effort"])
    s.add_argument("--note-hit", action="store_true")
    s.set_defaults(func=cmd_himem_retrieve)

    s = sub.add_parser("himem-reconsolidate", help="HiMem reconsolidate")
    add_store(s)
    s.add_argument("--conflict", action="store_true")
    s.add_argument("--missing-knowledge", action="store_true")
    s.set_defaults(func=cmd_himem_reconsolidate)

    s = sub.add_parser("himem-loop", help="HiMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["construct", "retrieve", "reconsolidate"]
    )
    s.set_defaults(func=cmd_himem_loop)

    s = sub.add_parser("hmeml-store", help="H-MEM store level")
    add_store(s)
    s.add_argument(
        "level",
        choices=["section", "subsection", "subsubsection", "content"],
    )
    s.add_argument("content")
    s.set_defaults(func=cmd_hmeml_store)

    s = sub.add_parser("hmeml-route", help="H-MEM route query")
    add_store(s)
    s.add_argument(
        "start_level",
        choices=["section", "subsection", "subsubsection", "content"],
    )
    s.set_defaults(func=cmd_hmeml_route)

    s = sub.add_parser("hmeml-descend", help="H-MEM descend")
    add_store(s)
    s.add_argument(
        "current_level",
        choices=["section", "subsection", "subsubsection", "content"],
    )
    s.add_argument("--hit", action="store_true")
    s.set_defaults(func=cmd_hmeml_descend)

    s = sub.add_parser("hmeml-parent", help="H-MEM parent link")
    add_store(s)
    s.add_argument(
        "parent_level",
        choices=["section", "subsection", "subsubsection", "content"],
    )
    s.add_argument(
        "child_level",
        choices=["section", "subsection", "subsubsection", "content"],
    )
    s.set_defaults(func=cmd_hmeml_parent)

    s = sub.add_parser("hmeml-efficiency", help="H-MEM efficiency score")
    add_store(s)
    s.add_argument("levels_scanned", type=int)
    s.add_argument("--max-levels", type=int, default=4)
    s.set_defaults(func=cmd_hmeml_efficiency)

    s = sub.add_parser("hmeml-loop", help="H-MEM loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["store", "route", "descend", "score"]
    )
    s.set_defaults(func=cmd_hmeml_loop)

    s = sub.add_parser("hyperskill-subtask", help="HyperSkill add subtask")
    add_store(s)
    s.add_argument("label")
    s.set_defaults(func=cmd_hyperskill_subtask)

    s = sub.add_parser("hyperskill-skill", help="HyperSkill add skill")
    add_store(s)
    s.add_argument("label")
    s.set_defaults(func=cmd_hyperskill_skill)

    s = sub.add_parser("hyperskill-hyperedge", help="HyperSkill add hyperedge")
    add_store(s)
    s.add_argument("subtask_ids_json")
    s.add_argument("skill_ids_json")
    s.add_argument("utility", type=float)
    s.set_defaults(func=cmd_hyperskill_hyperedge)

    s = sub.add_parser("hyperskill-dual", help="HyperSkill dual-path retrieve")
    add_store(s)
    s.add_argument("subtask_hits", type=int)
    s.add_argument("trajectory_hits", type=int)
    s.set_defaults(func=cmd_hyperskill_dual)

    s = sub.add_parser("hyperskill-rank", help="HyperSkill rank skills")
    add_store(s)
    s.add_argument("cooccurrence", type=int)
    s.add_argument("utility", type=float)
    s.set_defaults(func=cmd_hyperskill_rank)

    s = sub.add_parser("hyperskill-maintain", help="HyperSkill maintain plan")
    add_store(s)
    s.add_argument("utility", type=float)
    s.add_argument("--prune-below", type=float, default=0.2)
    s.add_argument("--redundant", action="store_true")
    s.set_defaults(func=cmd_hyperskill_maintain)

    s = sub.add_parser("hyperskill-loop", help="HyperSkill loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["store", "retrieve", "rank", "maintain"]
    )
    s.set_defaults(func=cmd_hyperskill_loop)

    s = sub.add_parser("dcpm-day", help="DCPM day write")
    add_store(s)
    s.add_argument("belief")
    s.add_argument("--superseded-id", default=None)
    s.set_defaults(func=cmd_dcpm_day)

    s = sub.add_parser("dcpm-chain", help="DCPM supersedes chain")
    add_store(s)
    s.add_argument("chain_len", type=int)
    s.set_defaults(func=cmd_dcpm_chain)

    s = sub.add_parser("dcpm-night", help="DCPM night induce")
    add_store(s)
    s.add_argument("fact_cluster_size", type=int)
    s.add_argument("--min-cluster", type=int, default=3)
    s.set_defaults(func=cmd_dcpm_night)

    s = sub.add_parser("dcpm-collision", help="DCPM cross-domain collision")
    add_store(s)
    s.add_argument("behavioral_similarity", type=float)
    s.add_argument("semantic_similarity", type=float)
    s.set_defaults(func=cmd_dcpm_collision)

    s = sub.add_parser("dcpm-level", help="DCPM hierarchy level")
    add_store(s)
    s.add_argument(
        "level",
        choices=[
            "raw",
            "fact",
            "belief",
            "identity",
            "schema",
            "intention",
            "core_schema",
        ],
    )
    s.set_defaults(func=cmd_dcpm_level)

    s = sub.add_parser("dcpm-loop", help="DCPM loop plan")
    add_store(s)
    s.add_argument("phase", choices=["day", "night", "collision"])
    s.set_defaults(func=cmd_dcpm_loop)

    s = sub.add_parser("memos-cube", help="MemOS create cube")
    add_store(s)
    s.add_argument(
        "kind", choices=["plaintext", "activation", "parametric"]
    )
    s.add_argument("content")
    s.set_defaults(func=cmd_memos_cube)

    s = sub.add_parser("memos-schedule", help="MemOS schedule")
    add_store(s)
    s.add_argument("strategy", choices=["lru", "semantic", "label"])
    s.add_argument("candidate_count", type=int)
    s.set_defaults(func=cmd_memos_schedule)

    s = sub.add_parser("memos-lifecycle", help="MemOS lifecycle")
    add_store(s)
    s.add_argument(
        "state", choices=["active", "frozen", "migrating", "fused"]
    )
    s.add_argument(
        "action", choices=["freeze", "thaw", "migrate", "fuse"]
    )
    s.set_defaults(func=cmd_memos_lifecycle)

    s = sub.add_parser("memos-compose", help="MemOS compose")
    add_store(s)
    s.add_argument("cube_ids_json")
    s.set_defaults(func=cmd_memos_compose)

    s = sub.add_parser("memos-migrate", help="MemOS migrate")
    add_store(s)
    s.add_argument(
        "from_kind", choices=["plaintext", "activation", "parametric"]
    )
    s.add_argument(
        "to_kind", choices=["plaintext", "activation", "parametric"]
    )
    s.set_defaults(func=cmd_memos_migrate)

    s = sub.add_parser("memos-fuse", help="MemOS fuse gate")
    add_store(s)
    s.add_argument("--compatible", action="store_true")
    s.add_argument("--conflict", action="store_true")
    s.set_defaults(func=cmd_memos_fuse)

    s = sub.add_parser("memos-loop", help="MemOS loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["create", "schedule", "lifecycle", "compose"]
    )
    s.set_defaults(func=cmd_memos_loop)

    s = sub.add_parser("skillcraft-save", help="SkillCraft save skill")
    add_store(s)
    s.add_argument("name")
    s.add_argument("steps", type=int)
    s.add_argument("--verified", action="store_true")
    s.set_defaults(func=cmd_skillcraft_save)

    s = sub.add_parser("skillcraft-get", help="SkillCraft get skill")
    add_store(s)
    s.add_argument("skill_id")
    s.set_defaults(func=cmd_skillcraft_get)

    s = sub.add_parser("skillcraft-list", help="SkillCraft list skills")
    add_store(s)
    s.add_argument("library_size", type=int)
    s.set_defaults(func=cmd_skillcraft_list)

    s = sub.add_parser("skillcraft-execute", help="SkillCraft execute skill")
    add_store(s)
    s.add_argument("--skill-exists", action="store_true")
    s.add_argument("--params-ok", action="store_true")
    s.set_defaults(func=cmd_skillcraft_execute)

    s = sub.add_parser("skillcraft-verify", help="SkillCraft verify skill")
    add_store(s)
    s.add_argument("--syntax-ok", action="store_true")
    s.add_argument("--runtime-ok", action="store_true")
    s.add_argument("--nonempty-output", action="store_true")
    s.set_defaults(func=cmd_skillcraft_verify)

    s = sub.add_parser(
        "skillcraft-efficiency", help="SkillCraft token efficiency"
    )
    add_store(s)
    s.add_argument("tokens_baseline", type=int)
    s.add_argument("tokens_skill_mode", type=int)
    s.set_defaults(func=cmd_skillcraft_efficiency)

    s = sub.add_parser("skillcraft-loop", help="SkillCraft loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["explore", "verify", "save", "execute"]
    )
    s.set_defaults(func=cmd_skillcraft_loop)

    s = sub.add_parser("cma-persist", help="CMA persist")
    add_store(s)
    s.add_argument("content")
    s.set_defaults(func=cmd_cma_persist)

    s = sub.add_parser("cma-retain", help="CMA selective retain")
    add_store(s)
    s.add_argument("utility", type=float)
    s.add_argument("--retain-threshold", type=float, default=0.4)
    s.set_defaults(func=cmd_cma_retain)

    s = sub.add_parser("cma-route", help="CMA associative route")
    add_store(s)
    s.add_argument("cue")
    s.add_argument("--hop-budget", type=int, default=2)
    s.set_defaults(func=cmd_cma_route)

    s = sub.add_parser("cma-chain", help="CMA temporal chain")
    add_store(s)
    s.add_argument("event_a")
    s.add_argument("event_b")
    s.add_argument("--order-ok", action="store_true")
    s.set_defaults(func=cmd_cma_chain)

    s = sub.add_parser("cma-consolidate", help="CMA consolidate")
    add_store(s)
    s.add_argument("episode_count", type=int)
    s.add_argument("--min-episodes", type=int, default=2)
    s.set_defaults(func=cmd_cma_consolidate)

    s = sub.add_parser("cma-probe", help="CMA probe gate")
    add_store(s)
    s.add_argument(
        "probe",
        choices=[
            "knowledge_update",
            "temporal_association",
            "associative_recall",
            "contextual_disambiguation",
        ],
    )
    s.add_argument("--supports-mutation", action="store_true")
    s.set_defaults(func=cmd_cma_probe)

    s = sub.add_parser("cma-loop", help="CMA loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["persist", "retain", "route", "chain", "consolidate"],
    )
    s.set_defaults(func=cmd_cma_loop)

    s = sub.add_parser("agentfold-split", help="AgentFold workspace split")
    add_store(s)
    s.add_argument("working_tokens", type=int)
    s.add_argument("long_term_blocks", type=int)
    s.set_defaults(func=cmd_agentfold_split)

    s = sub.add_parser("agentfold-fold", help="AgentFold fold command")
    add_store(s)
    s.add_argument("mode", choices=["granular", "deep"])
    s.add_argument("range_start", type=int)
    s.add_argument("step_t", type=int)
    s.set_defaults(func=cmd_agentfold_fold)

    s = sub.add_parser(
        "agentfold-granular", help="AgentFold granular condense"
    )
    add_store(s)
    s.add_argument("last_step_tokens", type=int)
    s.add_argument("target_tokens", type=int)
    s.set_defaults(func=cmd_agentfold_granular)

    s = sub.add_parser("agentfold-deep", help="AgentFold deep consolidate")
    add_store(s)
    s.add_argument("blocks_merged", type=int)
    s.set_defaults(func=cmd_agentfold_deep)

    s = sub.add_parser("agentfold-budget", help="AgentFold context budget")
    add_store(s)
    s.add_argument("turns", type=int)
    s.add_argument("tokens", type=int)
    s.add_argument("--soft-cap", type=int, default=7000)
    s.set_defaults(func=cmd_agentfold_budget)

    s = sub.add_parser("agentfold-loop", help="AgentFold loop plan")
    add_store(s)
    s.add_argument("phase", choices=["act", "fold", "split", "budget"])
    s.set_defaults(func=cmd_agentfold_loop)

    s = sub.add_parser("memengine-fn", help="MemEngine register function")
    add_store(s)
    s.add_argument("name")
    s.set_defaults(func=cmd_memengine_fn)

    s = sub.add_parser("memengine-op", help="MemEngine compose operation")
    add_store(s)
    s.add_argument("op", choices=["recall", "write", "reflect", "optimize"])
    s.add_argument("function_ids_json")
    s.set_defaults(func=cmd_memengine_op)

    s = sub.add_parser("memengine-model", help="MemEngine bind model")
    add_store(s)
    s.add_argument("model_name")
    s.add_argument("operation_ids_json")
    s.set_defaults(func=cmd_memengine_model)

    s = sub.add_parser("memengine-config", help="MemEngine config set")
    add_store(s)
    s.add_argument("key")
    s.add_argument("value")
    s.set_defaults(func=cmd_memengine_config)

    s = sub.add_parser("memengine-reflect", help="MemEngine reflect plan")
    add_store(s)
    s.add_argument("entries", type=int)
    s.add_argument("--min-entries", type=int, default=2)
    s.set_defaults(func=cmd_memengine_reflect)

    s = sub.add_parser("memengine-pluggable", help="MemEngine pluggable")
    add_store(s)
    s.add_argument("--agent-compatible", action="store_true")
    s.set_defaults(func=cmd_memengine_pluggable)

    s = sub.add_parser("memengine-loop", help="MemEngine loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["function", "operation", "model", "reflect"]
    )
    s.set_defaults(func=cmd_memengine_loop)

    s = sub.add_parser("simplemem-compress", help="SimpleMem compress")
    add_store(s)
    s.add_argument("raw_turns", type=int)
    s.add_argument("--window", type=int, default=20)
    s.set_defaults(func=cmd_simplemem_compress)

    s = sub.add_parser("simplemem-synthesize", help="SimpleMem synthesize")
    add_store(s)
    s.add_argument("related_facts", type=int)
    s.add_argument("--min-related", type=int, default=2)
    s.set_defaults(func=cmd_simplemem_synthesize)

    s = sub.add_parser("simplemem-intent", help="SimpleMem intent scope")
    add_store(s)
    s.add_argument("complexity", choices=["simple", "medium", "complex"])
    s.set_defaults(func=cmd_simplemem_intent)

    s = sub.add_parser("simplemem-index", help="SimpleMem multiview index")
    add_store(s)
    s.add_argument("--dense", action="store_true")
    s.add_argument("--sparse", action="store_true")
    s.add_argument("--metadata", action="store_true")
    s.set_defaults(func=cmd_simplemem_index)

    s = sub.add_parser("simplemem-ratio", help="SimpleMem token ratio")
    add_store(s)
    s.add_argument("tokens_baseline", type=int)
    s.add_argument("tokens_simplemem", type=int)
    s.set_defaults(func=cmd_simplemem_ratio)

    s = sub.add_parser("simplemem-loop", help="SimpleMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["compress", "synthesize", "retrieve"]
    )
    s.set_defaults(func=cmd_simplemem_loop)

    s = sub.add_parser("omem-persona", help="O-Mem extract persona")
    add_store(s)
    s.add_argument("trait")
    s.add_argument("confidence", type=float)
    s.set_defaults(func=cmd_omem_persona)

    s = sub.add_parser("omem-event", help="O-Mem update event")
    add_store(s)
    s.add_argument("event")
    s.add_argument("timestamp")
    s.set_defaults(func=cmd_omem_event)

    s = sub.add_parser("omem-retrieve", help="O-Mem hierarchy retrieve")
    add_store(s)
    s.add_argument("channel", choices=["persona", "topic"])
    s.add_argument("hits", type=int)
    s.set_defaults(func=cmd_omem_retrieve)

    s = sub.add_parser("omem-gate", help="O-Mem profile gate")
    add_store(s)
    s.add_argument("confidence", type=float)
    s.add_argument("--min-confidence", type=float, default=0.5)
    s.set_defaults(func=cmd_omem_gate)

    s = sub.add_parser("omem-scale", help="O-Mem scale memory time")
    add_store(s)
    s.add_argument("interactions", type=int)
    s.add_argument("memory_units", type=int)
    s.set_defaults(func=cmd_omem_scale)

    s = sub.add_parser("omem-loop", help="O-Mem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["extract", "event", "retrieve", "gate"]
    )
    s.set_defaults(func=cmd_omem_loop)

    s = sub.add_parser("mandol-basic", help="Mandol basic unit")
    add_store(s)
    s.add_argument("content")
    s.set_defaults(func=cmd_mandol_basic)

    s = sub.add_parser("mandol-agglomerate", help="Mandol agglomerate")
    add_store(s)
    s.add_argument("basic_ids_json")
    s.set_defaults(func=cmd_mandol_agglomerate)

    s = sub.add_parser("mandol-map", help="Mandol semantic map put")
    add_store(s)
    s.add_argument("key")
    s.add_argument("--vector-ok", action="store_true")
    s.set_defaults(func=cmd_mandol_map)

    s = sub.add_parser("mandol-hybrid", help="Mandol hybrid retrieve")
    add_store(s)
    s.add_argument("vector_hits", type=int)
    s.add_argument("graph_hops", type=int)
    s.set_defaults(func=cmd_mandol_hybrid)

    s = sub.add_parser("mandol-route", help="Mandol query route")
    add_store(s)
    s.add_argument(
        "query_type", choices=["factual", "relational", "temporal"]
    )
    s.set_defaults(func=cmd_mandol_route)

    s = sub.add_parser("mandol-budget", help="Mandol token budget")
    add_store(s)
    s.add_argument("selected_tokens", type=int)
    s.add_argument("max_tokens", type=int)
    s.set_defaults(func=cmd_mandol_budget)

    s = sub.add_parser("mandol-loop", help="Mandol loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["basic", "agglomerate", "retrieve", "budget"]
    )
    s.set_defaults(func=cmd_mandol_loop)

    s = sub.add_parser("memanto-store", help="Memanto store typed")
    add_store(s)
    s.add_argument(
        "category",
        choices=[
            "preference",
            "fact",
            "event",
            "entity",
            "relation",
            "goal",
            "constraint",
            "skill",
            "decision",
            "feedback",
            "context",
            "meta",
            "other",
        ],
    )
    s.add_argument("content")
    s.set_defaults(func=cmd_memanto_store)

    s = sub.add_parser("memanto-conflict", help="Memanto conflict resolve")
    add_store(s)
    s.add_argument("--conflict", action="store_true")
    s.add_argument("--newer-wins", action="store_true")
    s.set_defaults(func=cmd_memanto_conflict)

    s = sub.add_parser("memanto-version", help="Memanto version")
    add_store(s)
    s.add_argument("entry_id")
    s.add_argument("version", type=int)
    s.set_defaults(func=cmd_memanto_version)

    s = sub.add_parser("memanto-retrieve", help="Memanto retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--multi-query", action="store_true")
    s.set_defaults(func=cmd_memanto_retrieve)

    s = sub.add_parser("memanto-latency", help="Memanto latency gate")
    add_store(s)
    s.add_argument("latency_ms", type=float)
    s.add_argument("--soft-cap-ms", type=float, default=90.0)
    s.set_defaults(func=cmd_memanto_latency)

    s = sub.add_parser("memanto-loop", help="Memanto loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["store", "version", "retrieve", "conflict"]
    )
    s.set_defaults(func=cmd_memanto_loop)

    s = sub.add_parser("zep-episode", help="Zep add episode")
    add_store(s)
    s.add_argument("content")
    s.add_argument("valid_at")
    s.set_defaults(func=cmd_zep_episode)

    s = sub.add_parser("zep-link", help="Zep link entities")
    add_store(s)
    s.add_argument("entity_a")
    s.add_argument("entity_b")
    s.add_argument("relation")
    s.set_defaults(func=cmd_zep_link)

    s = sub.add_parser("zep-bitemporal", help="Zep bitemporal")
    add_store(s)
    s.add_argument("valid_at")
    s.add_argument("transaction_at")
    s.set_defaults(func=cmd_zep_bitemporal)

    s = sub.add_parser("zep-synthesize", help="Zep synthesize")
    add_store(s)
    s.add_argument("conversation_facts", type=int)
    s.add_argument("business_facts", type=int)
    s.set_defaults(func=cmd_zep_synthesize)

    s = sub.add_parser("zep-cross-session", help="Zep cross session")
    add_store(s)
    s.add_argument("sessions", type=int)
    s.add_argument("--min-sessions", type=int, default=2)
    s.set_defaults(func=cmd_zep_cross)

    s = sub.add_parser("zep-loop", help="Zep loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["episode", "link", "bitemporal", "retrieve"]
    )
    s.set_defaults(func=cmd_zep_loop)

    s = sub.add_parser("memgpt-capacity", help="MemGPT main capacity")
    add_store(s)
    s.add_argument("used_tokens", type=int)
    s.add_argument("max_tokens", type=int)
    s.add_argument("--warn-ratio", type=float, default=0.7)
    s.set_defaults(func=cmd_memgpt_capacity)

    s = sub.add_parser("memgpt-page-out", help="MemGPT page out")
    add_store(s)
    s.add_argument("content")
    s.add_argument("tier", choices=["recall", "archival"])
    s.set_defaults(func=cmd_memgpt_page_out)

    s = sub.add_parser("memgpt-page-in", help="MemGPT page in")
    add_store(s)
    s.add_argument("page_id")
    s.add_argument("--fits", action="store_true")
    s.set_defaults(func=cmd_memgpt_page_in)

    s = sub.add_parser("memgpt-recall", help="MemGPT recall search")
    add_store(s)
    s.add_argument("query")
    s.add_argument("hits", type=int)
    s.set_defaults(func=cmd_memgpt_recall)

    s = sub.add_parser("memgpt-archival", help="MemGPT archival search")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--page", type=int, default=0)
    s.set_defaults(func=cmd_memgpt_archival)

    s = sub.add_parser("memgpt-loop", help="MemGPT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["capacity", "page_out", "page_in", "search"]
    )
    s.set_defaults(func=cmd_memgpt_loop)

    s = sub.add_parser("ripple-store", help="RippleMem store episode")
    add_store(s)
    s.add_argument("content")
    s.set_defaults(func=cmd_ripple_store)

    s = sub.add_parser("ripple-link", help="RippleMem link entity")
    add_store(s)
    s.add_argument("episode_id")
    s.add_argument("entity")
    s.set_defaults(func=cmd_ripple_link)

    s = sub.add_parser("ripple-seed", help="RippleMem seed retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("seed_hits", type=int)
    s.set_defaults(func=cmd_ripple_seed)

    s = sub.add_parser("ripple-expand", help="RippleMem expand")
    add_store(s)
    s.add_argument("seeds", type=int)
    s.add_argument("hop", type=int)
    s.add_argument("--max-hops", type=int, default=2)
    s.set_defaults(func=cmd_ripple_expand)

    s = sub.add_parser("ripple-recollect", help="RippleMem recollect gate")
    add_store(s)
    s.add_argument("seed_hits", type=int)
    s.add_argument("associated", type=int)
    s.set_defaults(func=cmd_ripple_recollect)

    s = sub.add_parser("ripple-loop", help="RippleMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["store", "seed", "expand", "recollect"]
    )
    s.set_defaults(func=cmd_ripple_loop)

    s = sub.add_parser("flux-connect", help="FluxMem connect form")
    add_store(s)
    s.add_argument("src")
    s.add_argument("dst")
    s.add_argument("relation")
    s.set_defaults(func=cmd_flux_connect)

    s = sub.add_parser("flux-refine", help="FluxMem feedback refine")
    add_store(s)
    s.add_argument("edge_id")
    s.add_argument("feedback")
    s.add_argument("--keep", action="store_true")
    s.set_defaults(func=cmd_flux_refine)

    s = sub.add_parser("flux-consolidate", help="FluxMem consolidate")
    add_store(s)
    s.add_argument("circuits", type=int)
    s.add_argument("--min-success", type=int, default=2)
    s.set_defaults(func=cmd_flux_consolidate)

    s = sub.add_parser("flux-repair", help="FluxMem repair link")
    add_store(s)
    s.add_argument("--missing", action="store_true")
    s.add_argument("--repaired", action="store_true")
    s.set_defaults(func=cmd_flux_repair)

    s = sub.add_parser("flux-prune", help="FluxMem prune interference")
    add_store(s)
    s.add_argument("noise_score", type=float)
    s.add_argument("--threshold", type=float, default=0.5)
    s.set_defaults(func=cmd_flux_prune)

    s = sub.add_parser("flux-maturity", help="FluxMem maturity gate")
    add_store(s)
    s.add_argument("generalizability", type=float)
    s.add_argument("--min-score", type=float, default=0.5)
    s.set_defaults(func=cmd_flux_maturity)

    s = sub.add_parser("flux-loop", help="FluxMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["connect", "refine", "consolidate", "mature"]
    )
    s.set_defaults(func=cmd_flux_loop)

    s = sub.add_parser("qumem-segment", help="QUMem segment episode")
    add_store(s)
    s.add_argument("content")
    s.add_argument("continuity", type=float)
    s.set_defaults(func=cmd_qumem_segment)

    s = sub.add_parser("qumem-decompose", help="QUMem decompose")
    add_store(s)
    s.add_argument("episode_id")
    s.add_argument(
        "mem_type", choices=["factual", "preference", "insight"]
    )
    s.set_defaults(func=cmd_qumem_decompose)

    s = sub.add_parser("qumem-plan", help="QUMem plan queries")
    add_store(s)
    s.add_argument("task")
    s.add_argument("needs", type=int)
    s.set_defaults(func=cmd_qumem_plan)

    s = sub.add_parser("qumem-infer", help="QUMem infer user state")
    add_store(s)
    s.add_argument("factual", type=int)
    s.add_argument("preference", type=int)
    s.add_argument("insight", type=int)
    s.set_defaults(func=cmd_qumem_infer)

    s = sub.add_parser("qumem-temporal", help="QUMem temporal valid")
    add_store(s)
    s.add_argument("event_ts")
    s.add_argument("query_ts")
    s.add_argument("--stale", action="store_true")
    s.set_defaults(func=cmd_qumem_temporal)

    s = sub.add_parser("qumem-loop", help="QUMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["segment", "decompose", "plan", "infer"]
    )
    s.set_defaults(func=cmd_qumem_loop)

    s = sub.add_parser("viking-extract", help="VikingMem extract event")
    add_store(s)
    s.add_argument("content")
    s.add_argument("--high-value", action="store_true")
    s.set_defaults(func=cmd_viking_extract)

    s = sub.add_parser("viking-update", help="VikingMem update entity")
    add_store(s)
    s.add_argument("entity")
    s.add_argument("event_id")
    s.set_defaults(func=cmd_viking_update)

    s = sub.add_parser("viking-compress", help="VikingMem timeline compress")
    add_store(s)
    s.add_argument("topic")
    s.add_argument("items", type=int)
    s.set_defaults(func=cmd_viking_compress)

    s = sub.add_parser("viking-recall", help="VikingMem time-weighted recall")
    add_store(s)
    s.add_argument("query")
    s.add_argument("recency_weight", type=float)
    s.set_defaults(func=cmd_viking_recall)

    s = sub.add_parser("viking-rerank", help="VikingMem rerank")
    add_store(s)
    s.add_argument("candidates", type=int)
    s.add_argument("top_k", type=int)
    s.set_defaults(func=cmd_viking_rerank)

    s = sub.add_parser("viking-loop", help="VikingMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["extract", "update", "compress", "recall"]
    )
    s.set_defaults(func=cmd_viking_loop)

    s = sub.add_parser("recmem-buffer", help="RecMem buffer subconscious")
    add_store(s)
    s.add_argument("content")
    s.set_defaults(func=cmd_recmem_buffer)

    s = sub.add_parser("recmem-gate", help="RecMem recurrence gate")
    add_store(s)
    s.add_argument("similar_count", type=int)
    s.add_argument("--threshold", type=int, default=5)
    s.set_defaults(func=cmd_recmem_gate)

    s = sub.add_parser("recmem-consolidate", help="RecMem consolidate episodic")
    add_store(s)
    s.add_argument("cluster_size", type=int)
    s.set_defaults(func=cmd_recmem_consolidate)

    s = sub.add_parser("recmem-refine", help="RecMem semantic refine")
    add_store(s)
    s.add_argument("omitted_facts", type=int)
    s.set_defaults(func=cmd_recmem_refine)

    s = sub.add_parser("recmem-merge", help="RecMem merge retrieve")
    add_store(s)
    s.add_argument("subconscious", type=int)
    s.add_argument("episodic", type=int)
    s.add_argument("semantic", type=int)
    s.set_defaults(func=cmd_recmem_merge)

    s = sub.add_parser("recmem-loop", help="RecMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["buffer", "gate", "consolidate", "refine"]
    )
    s.set_defaults(func=cmd_recmem_loop)

    s = sub.add_parser("mbank-store", help="MemoryBank store memory")
    add_store(s)
    s.add_argument("content")
    s.add_argument("significance", type=float)
    s.set_defaults(func=cmd_mbank_store)

    s = sub.add_parser("mbank-summon", help="MemoryBank summon")
    add_store(s)
    s.add_argument("query")
    s.add_argument("hits", type=int)
    s.set_defaults(func=cmd_mbank_summon)

    s = sub.add_parser("mbank-personality", help="MemoryBank personality synth")
    add_store(s)
    s.add_argument("traits", type=int)
    s.set_defaults(func=cmd_mbank_personality)

    s = sub.add_parser("mbank-forget", help="MemoryBank forget curve")
    add_store(s)
    s.add_argument("days_elapsed", type=float)
    s.add_argument("--strength", type=float, default=1.0)
    s.set_defaults(func=cmd_mbank_forget)

    s = sub.add_parser("mbank-reinforce", help="MemoryBank reinforce")
    add_store(s)
    s.add_argument("memory_id")
    s.add_argument("boost", type=float)
    s.set_defaults(func=cmd_mbank_reinforce)

    s = sub.add_parser("mbank-loop", help="MemoryBank loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["store", "summon", "personality", "forget"]
    )
    s.set_defaults(func=cmd_mbank_loop)

    s = sub.add_parser("rfmem-score", help="RF-Mem familiarity score")
    add_store(s)
    s.add_argument("mean_score", type=float)
    s.add_argument("entropy", type=float)
    s.set_defaults(func=cmd_rfmem_score)

    s = sub.add_parser("rfmem-route", help="RF-Mem path route")
    add_store(s)
    s.add_argument("mean_score", type=float)
    s.add_argument("entropy", type=float)
    s.add_argument("--high-mean", type=float, default=0.7)
    s.add_argument("--low-entropy", type=float, default=1.0)
    s.set_defaults(func=cmd_rfmem_route)

    s = sub.add_parser("rfmem-topk", help="RF-Mem top-k familiar")
    add_store(s)
    s.add_argument("candidates", type=int)
    s.add_argument("top_k", type=int)
    s.set_defaults(func=cmd_rfmem_topk)

    s = sub.add_parser("rfmem-expand", help="RF-Mem recollect expand")
    add_store(s)
    s.add_argument("clusters", type=int)
    s.add_argument("hops", type=int)
    s.add_argument("--max-hops", type=int, default=3)
    s.set_defaults(func=cmd_rfmem_expand)

    s = sub.add_parser("rfmem-mix", help="RF-Mem alpha mix")
    add_store(s)
    s.add_argument("alpha", type=float)
    s.add_argument("query_weight", type=float)
    s.set_defaults(func=cmd_rfmem_mix)

    s = sub.add_parser("rfmem-loop", help="RF-Mem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["score", "route", "retrieve", "mix"]
    )
    s.set_defaults(func=cmd_rfmem_loop)

    s = sub.add_parser("agemem-store", help="AgeMem LTM/STM store")
    add_store(s)
    s.add_argument("content")
    s.add_argument("--tier", choices=["ltm", "stm"], default="ltm")
    s.set_defaults(func=cmd_agemem_store)

    s = sub.add_parser("agemem-stm", help="AgeMem STM manage")
    add_store(s)
    s.add_argument("capacity", type=int)
    s.add_argument("used", type=int)
    s.set_defaults(func=cmd_agemem_stm)

    s = sub.add_parser("agemem-retrieve", help="AgeMem retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("hits", type=int)
    s.set_defaults(func=cmd_agemem_retrieve)

    s = sub.add_parser("agemem-summarize", help="AgeMem summarize")
    add_store(s)
    s.add_argument("entries", type=int)
    s.set_defaults(func=cmd_agemem_summarize)

    s = sub.add_parser("agemem-discard", help="AgeMem discard plan")
    add_store(s)
    s.add_argument("memory_id")
    s.add_argument("reason")
    s.set_defaults(func=cmd_agemem_discard)

    s = sub.add_parser("agemem-loop", help="AgeMem loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["store", "stm", "retrieve", "summarize"]
    )
    s.set_defaults(func=cmd_agemem_loop)

    s = sub.add_parser("memgas-unit", help="MemGAS unit")
    add_store(s)
    s.add_argument("content")
    s.add_argument(
        "granularity", choices=["turn", "session", "topic", "summary"]
    )
    s.set_defaults(func=cmd_memgas_unit)

    s = sub.add_parser("memgas-associate", help="MemGAS associate")
    add_store(s)
    s.add_argument("new_id")
    s.add_argument("cluster_size", type=int)
    s.set_defaults(func=cmd_memgas_associate)

    s = sub.add_parser("memgas-route", help="MemGAS entropy route")
    add_store(s)
    s.add_argument("entropy", type=float)
    s.add_argument("--low", type=float, default=1.0)
    s.set_defaults(func=cmd_memgas_route)

    s = sub.add_parser("memgas-select", help="MemGAS select granularity")
    add_store(s)
    s.add_argument(
        "preferred", choices=["turn", "session", "topic", "summary"]
    )
    s.add_argument("entropy", type=float)
    s.set_defaults(func=cmd_memgas_select)

    s = sub.add_parser("memgas-filter", help="MemGAS filter plan")
    add_store(s)
    s.add_argument("candidates", type=int)
    s.add_argument("keep", type=int)
    s.set_defaults(func=cmd_memgas_filter)

    s = sub.add_parser("memgas-loop", help="MemGAS loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["unit", "associate", "route", "select"]
    )
    s.set_defaults(func=cmd_memgas_loop)

    s = sub.add_parser("memwalker-segment", help="MemWalker segment")
    add_store(s)
    s.add_argument("content")
    s.add_argument("chunk_size", type=int)
    s.set_defaults(func=cmd_memwalker_segment)

    s = sub.add_parser("memwalker-build", help="MemWalker build node")
    add_store(s)
    s.add_argument("summary")
    s.add_argument("level", type=int)
    s.set_defaults(func=cmd_memwalker_build)

    s = sub.add_parser("memwalker-nav", help="MemWalker navigate")
    add_store(s)
    s.add_argument("node_id")
    s.add_argument(
        "action", choices=["child", "revert", "stay", "answer"]
    )
    s.set_defaults(func=cmd_memwalker_nav)

    s = sub.add_parser("memwalker-gather", help="MemWalker gather")
    add_store(s)
    s.add_argument("leaves", type=int)
    s.add_argument("budget", type=int)
    s.set_defaults(func=cmd_memwalker_gather)

    s = sub.add_parser("memwalker-gate", help="MemWalker path gate")
    add_store(s)
    s.add_argument("depth", type=int)
    s.add_argument("max_depth", type=int)
    s.set_defaults(func=cmd_memwalker_gate)

    s = sub.add_parser("memwalker-loop", help="MemWalker loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["segment", "build", "navigate", "gather"]
    )
    s.set_defaults(func=cmd_memwalker_loop)

    s = sub.add_parser("mgr-store", help="MemGraphRAG store layer")
    add_store(s)
    s.add_argument("content")
    s.add_argument(
        "layer", choices=["ontology", "fact", "passage"]
    )
    s.set_defaults(func=cmd_mgr_store)

    s = sub.add_parser("mgr-detect", help="MemGraphRAG detect conflict")
    add_store(s)
    s.add_argument("facts", type=int)
    s.add_argument("anomalies", type=int)
    s.set_defaults(func=cmd_mgr_detect)

    s = sub.add_parser("mgr-resolve", help="MemGraphRAG resolve plan")
    add_store(s)
    s.add_argument("conflict_id")
    s.set_defaults(func=cmd_mgr_resolve)

    s = sub.add_parser("mgr-retrieve", help="MemGraphRAG multilayer retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("layers_hit", type=int)
    s.set_defaults(func=cmd_mgr_retrieve)

    s = sub.add_parser("mgr-propagate", help="MemGraphRAG propagate")
    add_store(s)
    s.add_argument("seeds", type=int)
    s.add_argument("--damping", type=float, default=0.85)
    s.set_defaults(func=cmd_mgr_propagate)

    s = sub.add_parser("mgr-loop", help="MemGraphRAG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["store", "detect", "retrieve", "propagate"]
    )
    s.set_defaults(func=cmd_mgr_loop)

    s = sub.add_parser("raptor-embed", help="RAPTOR embed chunk")
    add_store(s)
    s.add_argument("content")
    s.set_defaults(func=cmd_raptor_embed)

    s = sub.add_parser("raptor-cluster", help="RAPTOR cluster")
    add_store(s)
    s.add_argument("chunks", type=int)
    s.add_argument("clusters", type=int)
    s.set_defaults(func=cmd_raptor_cluster)

    s = sub.add_parser("raptor-summarize", help="RAPTOR summarize node")
    add_store(s)
    s.add_argument("level", type=int)
    s.add_argument("children", type=int)
    s.set_defaults(func=cmd_raptor_summarize)

    s = sub.add_parser("raptor-traverse", help="RAPTOR tree traverse")
    add_store(s)
    s.add_argument("depth", type=int)
    s.add_argument("keep_per_level", type=int)
    s.set_defaults(func=cmd_raptor_traverse)

    s = sub.add_parser("raptor-collapsed", help="RAPTOR collapsed retrieve")
    add_store(s)
    s.add_argument("candidates", type=int)
    s.add_argument("top_k", type=int)
    s.set_defaults(func=cmd_raptor_collapsed)

    s = sub.add_parser("raptor-loop", help="RAPTOR loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["embed", "cluster", "summarize", "retrieve"]
    )
    s.set_defaults(func=cmd_raptor_loop)

    s = sub.add_parser("lightrag-entity", help="LightRAG index entity")
    add_store(s)
    s.add_argument("name")
    s.set_defaults(func=cmd_lightrag_entity)

    s = sub.add_parser("lightrag-relation", help="LightRAG index relation")
    add_store(s)
    s.add_argument("src")
    s.add_argument("dst")
    s.add_argument("rel")
    s.set_defaults(func=cmd_lightrag_relation)

    s = sub.add_parser("lightrag-dual", help="LightRAG dual retrieve")
    add_store(s)
    s.add_argument("query")
    s.add_argument("level", choices=["low", "high", "both"])
    s.set_defaults(func=cmd_lightrag_dual)

    s = sub.add_parser("lightrag-update", help="LightRAG incremental update")
    add_store(s)
    s.add_argument("new_docs", type=int)
    s.set_defaults(func=cmd_lightrag_update)

    s = sub.add_parser("lightrag-fuse", help="LightRAG graph-vector fuse")
    add_store(s)
    s.add_argument("graph_hits", type=int)
    s.add_argument("vector_hits", type=int)
    s.set_defaults(func=cmd_lightrag_fuse)

    s = sub.add_parser("lightrag-loop", help="LightRAG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["index", "dual", "fuse", "update"]
    )
    s.set_defaults(func=cmd_lightrag_loop)

    s = sub.add_parser("memorag-memorize", help="MemoRAG memorize")
    add_store(s)
    s.add_argument("corpus_chars", type=int)
    s.set_defaults(func=cmd_memorag_memorize)

    s = sub.add_parser("memorag-clue", help="MemoRAG clue")
    add_store(s)
    s.add_argument("query")
    s.add_argument("draft")
    s.set_defaults(func=cmd_memorag_clue)

    s = sub.add_parser("memorag-retrieve", help="MemoRAG retrieve by clue")
    add_store(s)
    s.add_argument("clue_id")
    s.add_argument("hits", type=int)
    s.set_defaults(func=cmd_memorag_retrieve)

    s = sub.add_parser("memorag-dual", help="MemoRAG dual system")
    add_store(s)
    s.add_argument("role", choices=["memory", "generator"])
    s.set_defaults(func=cmd_memorag_dual)

    s = sub.add_parser("memorag-generate", help="MemoRAG generate plan")
    add_store(s)
    s.add_argument("evidence", type=int)
    s.set_defaults(func=cmd_memorag_generate)

    s = sub.add_parser("memorag-loop", help="MemoRAG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["memorize", "clue", "retrieve", "generate"]
    )
    s.set_defaults(func=cmd_memorag_loop)

    s = sub.add_parser("pageindex-toc", help="PageIndex build TOC")
    add_store(s)
    s.add_argument("title")
    s.add_argument("sections", type=int)
    s.set_defaults(func=cmd_pageindex_toc)

    s = sub.add_parser("pageindex-section", help="PageIndex add section")
    add_store(s)
    s.add_argument("parent_id")
    s.add_argument("heading")
    s.add_argument("page_start", type=int)
    s.set_defaults(func=cmd_pageindex_section)

    s = sub.add_parser("pageindex-nav", help="PageIndex reason nav")
    add_store(s)
    s.add_argument("query")
    s.add_argument("candidates", type=int)
    s.set_defaults(func=cmd_pageindex_nav)

    s = sub.add_parser("pageindex-select", help="PageIndex select section")
    add_store(s)
    s.add_argument("section_id")
    s.add_argument("--relevant", action="store_true")
    s.set_defaults(func=cmd_pageindex_select)

    s = sub.add_parser("pageindex-trace", help="PageIndex trace path")
    add_store(s)
    s.add_argument("hops", type=int)
    s.set_defaults(func=cmd_pageindex_trace)

    s = sub.add_parser("pageindex-loop", help="PageIndex loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["toc", "section", "navigate", "select"]
    )
    s.set_defaults(func=cmd_pageindex_loop)

    s = sub.add_parser("selfrag-need", help="Self-RAG need retrieve")
    add_store(s)
    s.add_argument("confidence", type=float)
    s.add_argument("--threshold", type=float, default=0.5)
    s.set_defaults(func=cmd_selfrag_need)

    s = sub.add_parser("selfrag-relevance", help="Self-RAG relevance critique")
    add_store(s)
    s.add_argument("--relevant", action="store_true")
    s.set_defaults(func=cmd_selfrag_relevance)

    s = sub.add_parser("selfrag-support", help="Self-RAG support critique")
    add_store(s)
    s.add_argument("--supported", action="store_true")
    s.set_defaults(func=cmd_selfrag_support)

    s = sub.add_parser("selfrag-utility", help="Self-RAG utility critique")
    add_store(s)
    s.add_argument("utility", type=float)
    s.set_defaults(func=cmd_selfrag_utility)

    s = sub.add_parser("selfrag-select", help="Self-RAG select best")
    add_store(s)
    s.add_argument("scores", type=int)
    s.add_argument("pick", type=int)
    s.set_defaults(func=cmd_selfrag_select)

    s = sub.add_parser("selfrag-loop", help="Self-RAG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["decide", "critique", "select", "generate"]
    )
    s.set_defaults(func=cmd_selfrag_loop)

    s = sub.add_parser("memobrain-dep", help="MemoBrain dep edge")
    add_store(s)
    s.add_argument("src_step")
    s.add_argument("dst_step")
    s.set_defaults(func=cmd_memobrain_dep)

    s = sub.add_parser("memobrain-prune", help="MemoBrain prune invalid")
    add_store(s)
    s.add_argument("step_id")
    s.add_argument("--invalid", action="store_true")
    s.set_defaults(func=cmd_memobrain_prune)

    s = sub.add_parser("memobrain-fold", help="MemoBrain fold subtraj")
    add_store(s)
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_memobrain_fold)

    s = sub.add_parser("memobrain-flush", help="MemoBrain flush budget")
    add_store(s)
    s.add_argument("used", type=int)
    s.add_argument("budget", type=int)
    s.set_defaults(func=cmd_memobrain_flush)

    s = sub.add_parser("memobrain-salience", help="MemoBrain salience keep")
    add_store(s)
    s.add_argument("salience", type=float)
    s.add_argument("--min-keep", type=float, default=0.5)
    s.set_defaults(func=cmd_memobrain_salience)

    s = sub.add_parser("memobrain-loop", help="MemoBrain loop plan")
    add_store(s)
    s.add_argument("phase", choices=["dep", "prune", "fold", "flush"])
    s.set_defaults(func=cmd_memobrain_loop)

    s = sub.add_parser("crag-evaluate", help="CRAG evaluate retrieval")
    add_store(s)
    s.add_argument("confidence", type=float)
    s.set_defaults(func=cmd_crag_evaluate)

    s = sub.add_parser("crag-refine", help="CRAG correct refine")
    add_store(s)
    s.add_argument("chunks", type=int)
    s.set_defaults(func=cmd_crag_refine)

    s = sub.add_parser("crag-web", help="CRAG web fallback plan")
    add_store(s)
    s.add_argument("--trigger", action="store_true")
    s.set_defaults(func=cmd_crag_web)

    s = sub.add_parser("crag-blend", help="CRAG ambiguous blend")
    add_store(s)
    s.add_argument("local_hits", type=int)
    s.add_argument("web_hits", type=int)
    s.set_defaults(func=cmd_crag_blend)

    s = sub.add_parser("crag-action", help="CRAG action select")
    add_store(s)
    s.add_argument("action", choices=["Correct", "Incorrect", "Ambiguous"])
    s.set_defaults(func=cmd_crag_action)

    s = sub.add_parser("crag-loop", help="CRAG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["evaluate", "refine", "fallback", "blend"]
    )
    s.set_defaults(func=cmd_crag_loop)

    s = sub.add_parser("hyde-hyp", help="HyDE hypothetical doc")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_hyde_hyp)

    s = sub.add_parser("hyde-encode", help="HyDE encode proxy")
    add_store(s)
    s.add_argument("hyp_id")
    s.set_defaults(func=cmd_hyde_encode)

    s = sub.add_parser("hyde-retrieve", help="HyDE retrieve by hyp")
    add_store(s)
    s.add_argument("vec_id")
    s.add_argument("--k", type=int, default=5)
    s.set_defaults(func=cmd_hyde_retrieve)

    s = sub.add_parser("hyde-filter", help="HyDE filter hallucination")
    add_store(s)
    s.add_argument("retained", type=float)
    s.set_defaults(func=cmd_hyde_filter)

    s = sub.add_parser("hyde-ground", help="HyDE ground corpus")
    add_store(s)
    s.add_argument("hits", type=int)
    s.add_argument("grounded", type=int)
    s.set_defaults(func=cmd_hyde_ground)

    s = sub.add_parser("hyde-loop", help="HyDE loop plan")
    add_store(s)
    s.add_argument("phase", choices=["hyp", "encode", "retrieve", "ground"])
    s.set_defaults(func=cmd_hyde_loop)

    s = sub.add_parser("adaptiverag-classify", help="Adaptive-RAG classify")
    add_store(s)
    s.add_argument("hops", type=int)
    s.set_defaults(func=cmd_adaptiverag_classify)

    s = sub.add_parser("adaptiverag-select", help="Adaptive-RAG select strategy")
    add_store(s)
    s.add_argument("level", type=int, choices=[0, 1, 2])
    s.set_defaults(func=cmd_adaptiverag_select)

    s = sub.add_parser("adaptiverag-none", help="Adaptive-RAG no retrieve")
    add_store(s)
    s.add_argument("--parametric-ok", action="store_true")
    s.set_defaults(func=cmd_adaptiverag_none)

    s = sub.add_parser("adaptiverag-single", help="Adaptive-RAG single step")
    add_store(s)
    s.add_argument("hits", type=int)
    s.set_defaults(func=cmd_adaptiverag_single)

    s = sub.add_parser("adaptiverag-multi", help="Adaptive-RAG multi step")
    add_store(s)
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_adaptiverag_multi)

    s = sub.add_parser("adaptiverag-loop", help="Adaptive-RAG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["classify", "select", "execute", "adapt"]
    )
    s.set_defaults(func=cmd_adaptiverag_loop)

    s = sub.add_parser("flare-anticipate", help="FLARE anticipate sentence")
    add_store(s)
    s.add_argument("context")
    s.set_defaults(func=cmd_flare_anticipate)

    s = sub.add_parser("flare-confidence", help="FLARE low confidence")
    add_store(s)
    s.add_argument("confidence", type=float)
    s.add_argument("--threshold", type=float, default=0.4)
    s.set_defaults(func=cmd_flare_confidence)

    s = sub.add_parser("flare-retrieve", help="FLARE retrieve for regen")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--k", type=int, default=3)
    s.set_defaults(func=cmd_flare_retrieve)

    s = sub.add_parser("flare-regen", help="FLARE regenerate sentence")
    add_store(s)
    s.add_argument("sent_id")
    s.add_argument("--with-docs", action="store_true")
    s.set_defaults(func=cmd_flare_regen)

    s = sub.add_parser("flare-step", help="FLARE active step")
    add_store(s)
    s.add_argument("step", type=int)
    s.add_argument("--retrieved", action="store_true")
    s.set_defaults(func=cmd_flare_step)

    s = sub.add_parser("flare-loop", help="FLARE loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["anticipate", "confidence", "retrieve", "regenerate"],
    )
    s.set_defaults(func=cmd_flare_loop)

    s = sub.add_parser("graphreader-build", help="GraphReader build node")
    add_store(s)
    s.add_argument("chunk")
    s.set_defaults(func=cmd_graphreader_build)

    s = sub.add_parser("graphreader-read", help="GraphReader read node")
    add_store(s)
    s.add_argument("node_id")
    s.set_defaults(func=cmd_graphreader_read)

    s = sub.add_parser("graphreader-neighbors", help="GraphReader neighbors")
    add_store(s)
    s.add_argument("node_id")
    s.add_argument("--hops", type=int, default=1)
    s.set_defaults(func=cmd_graphreader_neighbors)

    s = sub.add_parser("graphreader-note", help="GraphReader note insight")
    add_store(s)
    s.add_argument("text")
    s.set_defaults(func=cmd_graphreader_note)

    s = sub.add_parser("graphreader-reflect", help="GraphReader reflect plan")
    add_store(s)
    s.add_argument("--enough", action="store_true")
    s.set_defaults(func=cmd_graphreader_reflect)

    s = sub.add_parser("graphreader-loop", help="GraphReader loop plan")
    add_store(s)
    s.add_argument("phase", choices=["plan", "read", "note", "reflect"])
    s.set_defaults(func=cmd_graphreader_loop)

    s = sub.add_parser("gretriever-prize", help="G-Retriever node prize")
    add_store(s)
    s.add_argument("node_id")
    s.add_argument("prize", type=float)
    s.set_defaults(func=cmd_gretriever_prize)

    s = sub.add_parser("gretriever-pcst", help="G-Retriever PCST select")
    add_store(s)
    s.add_argument("nodes", type=int)
    s.add_argument("budget", type=int)
    s.set_defaults(func=cmd_gretriever_pcst)

    s = sub.add_parser("gretriever-subgraph", help="G-Retriever subgraph")
    add_store(s)
    s.add_argument("selected", type=int)
    s.set_defaults(func=cmd_gretriever_subgraph)

    s = sub.add_parser("gretriever-prompt", help="G-Retriever soft prompt plan")
    add_store(s)
    s.add_argument("subgraph_id")
    s.set_defaults(func=cmd_gretriever_prompt)

    s = sub.add_parser("gretriever-highlight", help="G-Retriever highlight")
    add_store(s)
    s.add_argument("nodes", type=int)
    s.set_defaults(func=cmd_gretriever_highlight)

    s = sub.add_parser("gretriever-loop", help="G-Retriever loop plan")
    add_store(s)
    s.add_argument("phase", choices=["prize", "pcst", "subgraph", "prompt"])
    s.set_defaults(func=cmd_gretriever_loop)

    s = sub.add_parser("rqrag-rewrite", help="RQ-RAG rewrite")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_rqrag_rewrite)

    s = sub.add_parser("rqrag-decompose", help="RQ-RAG decompose")
    add_store(s)
    s.add_argument("query")
    s.add_argument("parts", type=int)
    s.set_defaults(func=cmd_rqrag_decompose)

    s = sub.add_parser("rqrag-disambiguate", help="RQ-RAG disambiguate")
    add_store(s)
    s.add_argument("query")
    s.add_argument("intents", type=int)
    s.set_defaults(func=cmd_rqrag_disambiguate)

    s = sub.add_parser("rqrag-mode", help="RQ-RAG refine mode")
    add_store(s)
    s.add_argument("mode", choices=["rewrite", "decompose", "disambiguate"])
    s.set_defaults(func=cmd_rqrag_mode)

    s = sub.add_parser("rqrag-retrieve", help="RQ-RAG retrieve refined")
    add_store(s)
    s.add_argument("refined_id")
    s.add_argument("--k", type=int, default=5)
    s.set_defaults(func=cmd_rqrag_retrieve)

    s = sub.add_parser("rqrag-loop", help="RQ-RAG loop plan")
    add_store(s)
    s.add_argument("phase", choices=["mode", "refine", "retrieve", "answer"])
    s.set_defaults(func=cmd_rqrag_loop)

    s = sub.add_parser("ircot-cot", help="IRCoT CoT step")
    add_store(s)
    s.add_argument("step", type=int)
    s.add_argument("claim")
    s.set_defaults(func=cmd_ircot_cot)

    s = sub.add_parser("ircot-retrieve", help="IRCoT retrieve guided")
    add_store(s)
    s.add_argument("step_id")
    s.add_argument("--k", type=int, default=3)
    s.set_defaults(func=cmd_ircot_retrieve)

    s = sub.add_parser("ircot-interleave", help="IRCoT interleave")
    add_store(s)
    s.add_argument("cot_steps", type=int)
    s.add_argument("retrieves", type=int)
    s.set_defaults(func=cmd_ircot_interleave)

    s = sub.add_parser("ircot-ready", help="IRCoT answer ready")
    add_store(s)
    s.add_argument("--enough", action="store_true")
    s.set_defaults(func=cmd_ircot_ready)

    s = sub.add_parser("ircot-grounded", help="IRCoT hallucination check")
    add_store(s)
    s.add_argument("grounded", type=float)
    s.set_defaults(func=cmd_ircot_grounded)

    s = sub.add_parser("ircot-loop", help="IRCoT loop plan")
    add_store(s)
    s.add_argument("phase", choices=["cot", "retrieve", "interleave", "answer"])
    s.set_defaults(func=cmd_ircot_loop)

    s = sub.add_parser("replug-retrieve", help="REPLUG retrieve docs")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--k", type=int, default=5)
    s.set_defaults(func=cmd_replug_retrieve)

    s = sub.add_parser("replug-prepend", help="REPLUG prepend doc")
    add_store(s)
    s.add_argument("doc_id")
    s.add_argument("context")
    s.set_defaults(func=cmd_replug_prepend)

    s = sub.add_parser("replug-ensemble", help="REPLUG ensemble probs")
    add_store(s)
    s.add_argument("packs", type=int)
    s.set_defaults(func=cmd_replug_ensemble)

    s = sub.add_parser("replug-supervise", help="REPLUG supervise retriever")
    add_store(s)
    s.add_argument("lm_gain", type=float)
    s.set_defaults(func=cmd_replug_supervise)

    s = sub.add_parser("replug-forward", help="REPLUG blackbox forward")
    add_store(s)
    s.add_argument("pack_id")
    s.set_defaults(func=cmd_replug_forward)

    s = sub.add_parser("replug-loop", help="REPLUG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["retrieve", "prepend", "forward", "ensemble"]
    )
    s.set_defaults(func=cmd_replug_loop)

    s = sub.add_parser("iterretgen-generate", help="Iter-RetGen generate")
    add_store(s)
    s.add_argument("iteration", type=int)
    s.add_argument("draft")
    s.set_defaults(func=cmd_iterretgen_generate)

    s = sub.add_parser("iterretgen-query", help="Iter-RetGen use as query")
    add_store(s)
    s.add_argument("gen_id")
    s.set_defaults(func=cmd_iterretgen_query)

    s = sub.add_parser("iterretgen-retrieve", help="Iter-RetGen retrieve next")
    add_store(s)
    s.add_argument("query_from")
    s.add_argument("--k", type=int, default=5)
    s.set_defaults(func=cmd_iterretgen_retrieve)

    s = sub.add_parser("iterretgen-iterate", help="Iter-RetGen iterate")
    add_store(s)
    s.add_argument("round_n", type=int)
    s.add_argument("--max-rounds", type=int, default=3)
    s.set_defaults(func=cmd_iterretgen_iterate)

    s = sub.add_parser("iterretgen-adapt", help="Iter-RetGen adapt retriever")
    add_store(s)
    s.add_argument("--improve", action="store_true")
    s.set_defaults(func=cmd_iterretgen_adapt)

    s = sub.add_parser("iterretgen-loop", help="Iter-RetGen loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["generate", "query", "retrieve", "iterate"]
    )
    s.set_defaults(func=cmd_iterretgen_loop)

    s = sub.add_parser("planrag-plan", help="PlanRAG make plan")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_planrag_plan)

    s = sub.add_parser("planrag-query", help="PlanRAG analysis query")
    add_store(s)
    s.add_argument("plan_id")
    s.add_argument("query")
    s.set_defaults(func=cmd_planrag_query)

    s = sub.add_parser("planrag-retrieve", help="PlanRAG retrieve data")
    add_store(s)
    s.add_argument("query_id")
    s.add_argument("rows", type=int)
    s.set_defaults(func=cmd_planrag_retrieve)

    s = sub.add_parser("planrag-replan", help="PlanRAG replan")
    add_store(s)
    s.add_argument("--need-replan", action="store_true")
    s.set_defaults(func=cmd_planrag_replan)

    s = sub.add_parser("planrag-decide", help="PlanRAG decide")
    add_store(s)
    s.add_argument("--ready", action="store_true")
    s.set_defaults(func=cmd_planrag_decide)

    s = sub.add_parser("planrag-loop", help="PlanRAG loop plan")
    add_store(s)
    s.add_argument("phase", choices=["plan", "query", "retrieve", "decide"])
    s.set_defaults(func=cmd_planrag_loop)

    s = sub.add_parser("rrr-rewrite", help="RRR rewrite query")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_rrr_rewrite)

    s = sub.add_parser("rrr-retrieve", help="RRR retrieve")
    add_store(s)
    s.add_argument("rewrite_id")
    s.add_argument("--k", type=int, default=5)
    s.set_defaults(func=cmd_rrr_retrieve)

    s = sub.add_parser("rrr-read", help="RRR read")
    add_store(s)
    s.add_argument("hits", type=int)
    s.set_defaults(func=cmd_rrr_read)

    s = sub.add_parser("rrr-feedback", help="RRR reader feedback")
    add_store(s)
    s.add_argument("reward", type=float)
    s.set_defaults(func=cmd_rrr_feedback)

    s = sub.add_parser("rrr-train", help="RRR train rewriter plan")
    add_store(s)
    s.add_argument("--improve", action="store_true")
    s.set_defaults(func=cmd_rrr_train)

    s = sub.add_parser("rrr-loop", help="RRR loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["rewrite", "retrieve", "read", "feedback"]
    )
    s.set_defaults(func=cmd_rrr_loop)

    s = sub.add_parser("dsp-demo", help="DSP bootstrap demo")
    add_store(s)
    s.add_argument("task")
    s.add_argument("--n", type=int, default=3)
    s.set_defaults(func=cmd_dsp_demo)

    s = sub.add_parser("dsp-search", help="DSP search")
    add_store(s)
    s.add_argument("query")
    s.add_argument("--k", type=int, default=5)
    s.set_defaults(func=cmd_dsp_search)

    s = sub.add_parser("dsp-predict", help="DSP predict")
    add_store(s)
    s.add_argument("--grounded", action="store_true")
    s.set_defaults(func=cmd_dsp_predict)

    s = sub.add_parser("dsp-compose", help="DSP compose program")
    add_store(s)
    s.add_argument("stages", type=int)
    s.set_defaults(func=cmd_dsp_compose)

    s = sub.add_parser("dsp-hop", help="DSP multihop hop")
    add_store(s)
    s.add_argument("hop", type=int)
    s.set_defaults(func=cmd_dsp_hop)

    s = sub.add_parser("dsp-loop", help="DSP loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["demonstrate", "search", "predict", "compose"]
    )
    s.set_defaults(func=cmd_dsp_loop)

    s = sub.add_parser("genread-context", help="GenRead generate context")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_genread_context)

    s = sub.add_parser("genread-ground", help="GenRead ground optional")
    add_store(s)
    s.add_argument("ctx_id")
    s.add_argument("--use-retriever", action="store_true")
    s.set_defaults(func=cmd_genread_ground)

    s = sub.add_parser("genread-answer", help="GenRead answer")
    add_store(s)
    s.add_argument("ctx_id")
    s.set_defaults(func=cmd_genread_answer)

    s = sub.add_parser("genread-compare", help="GenRead compare retrieve")
    add_store(s)
    s.add_argument("gen_hits", type=int)
    s.add_argument("retrieve_hits", type=int)
    s.set_defaults(func=cmd_genread_compare)

    s = sub.add_parser("genread-hybrid", help="GenRead hybrid")
    add_store(s)
    s.add_argument("--generate", action="store_true")
    s.add_argument("--retrieve", action="store_true")
    s.set_defaults(func=cmd_genread_hybrid)

    s = sub.add_parser("genread-loop", help="GenRead loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["generate", "ground", "answer", "compare"]
    )
    s.set_defaults(func=cmd_genread_loop)

    s = sub.add_parser("selfask-followup", help="Self-Ask followup")
    add_store(s)
    s.add_argument("question")
    s.add_argument("--hop", type=int, default=0)
    s.set_defaults(func=cmd_selfask_followup)

    s = sub.add_parser("selfask-search", help="Self-Ask search intercept")
    add_store(s)
    s.add_argument("followup_id")
    s.add_argument("--k", type=int, default=3)
    s.set_defaults(func=cmd_selfask_search)

    s = sub.add_parser("selfask-compose", help="Self-Ask compose answer")
    add_store(s)
    s.add_argument("followups", type=int)
    s.set_defaults(func=cmd_selfask_compose)

    s = sub.add_parser("selfask-stop", help="Self-Ask stop")
    add_store(s)
    s.add_argument("--enough", action="store_true")
    s.set_defaults(func=cmd_selfask_stop)

    s = sub.add_parser("selfask-demos", help="Self-Ask demo prompt")
    add_store(s)
    s.add_argument("demos", type=int)
    s.set_defaults(func=cmd_selfask_demos)

    s = sub.add_parser("selfask-loop", help="Self-Ask loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["followup", "search", "compose", "stop"]
    )
    s.set_defaults(func=cmd_selfask_loop)

    s = sub.add_parser("react-thought", help="ReAct thought")
    add_store(s)
    s.add_argument("step", type=int)
    s.add_argument("text")
    s.set_defaults(func=cmd_react_thought)

    s = sub.add_parser("react-action", help="ReAct action")
    add_store(s)
    s.add_argument("action")
    s.add_argument("arg")
    s.set_defaults(func=cmd_react_action)

    s = sub.add_parser("react-observe", help="ReAct observe")
    add_store(s)
    s.add_argument("observation")
    s.set_defaults(func=cmd_react_observe)

    s = sub.add_parser("react-finish", help="ReAct finish")
    add_store(s)
    s.add_argument("answer")
    s.set_defaults(func=cmd_react_finish)

    s = sub.add_parser("react-trajectory", help="ReAct trajectory")
    add_store(s)
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_react_trajectory)

    s = sub.add_parser("react-loop", help="ReAct loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["thought", "action", "observe", "finish"]
    )
    s.set_defaults(func=cmd_react_loop)

    s = sub.add_parser("tog-init", help="ToG init entity")
    add_store(s)
    s.add_argument("entity")
    s.set_defaults(func=cmd_tog_init)

    s = sub.add_parser("tog-explore", help="ToG explore neighbors")
    add_store(s)
    s.add_argument("entity_id")
    s.add_argument("--width", type=int, default=3)
    s.set_defaults(func=cmd_tog_explore)

    s = sub.add_parser("tog-prune", help="ToG beam prune")
    add_store(s)
    s.add_argument("paths", type=int)
    s.add_argument("keep", type=int)
    s.set_defaults(func=cmd_tog_prune)

    s = sub.add_parser("tog-score", help="ToG path score")
    add_store(s)
    s.add_argument("path_id")
    s.add_argument("score", type=float)
    s.set_defaults(func=cmd_tog_score)

    s = sub.add_parser("tog-answer", help="ToG answer from paths")
    add_store(s)
    s.add_argument("path_count", type=int)
    s.set_defaults(func=cmd_tog_answer)

    s = sub.add_parser("tog-loop", help="ToG loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["init", "explore", "prune", "answer"]
    )
    s.set_defaults(func=cmd_tog_loop)

    s = sub.add_parser("tf-candidate", help="Toolformer API candidate")
    add_store(s)
    s.add_argument("api")
    s.add_argument("args")
    s.set_defaults(func=cmd_tf_candidate)

    s = sub.add_parser("tf-filter", help="Toolformer filter call")
    add_store(s)
    s.add_argument("candidate_id")
    s.add_argument("--useful", action="store_true")
    s.set_defaults(func=cmd_tf_filter)

    s = sub.add_parser("tf-execute", help="Toolformer execute proxy")
    add_store(s)
    s.add_argument("api")
    s.set_defaults(func=cmd_tf_execute)

    s = sub.add_parser("tf-incorporate", help="Toolformer incorporate result")
    add_store(s)
    s.add_argument("result_id")
    s.set_defaults(func=cmd_tf_incorporate)

    s = sub.add_parser("tf-demos", help="Toolformer demo APIs")
    add_store(s)
    s.add_argument("count", type=int)
    s.set_defaults(func=cmd_tf_demos)

    s = sub.add_parser("tf-loop", help="Toolformer loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["candidate", "filter", "execute", "incorporate"],
    )
    s.set_defaults(func=cmd_tf_loop)

    s = sub.add_parser("rx-trial", help="Reflexion trial run")
    add_store(s)
    s.add_argument("task")
    s.add_argument("--trial", type=int, default=0)
    s.set_defaults(func=cmd_rx_trial)

    s = sub.add_parser("rx-evaluate", help="Reflexion evaluate")
    add_store(s)
    s.add_argument("trial_id")
    s.add_argument("--success", action="store_true")
    s.set_defaults(func=cmd_rx_evaluate)

    s = sub.add_parser("rx-reflect", help="Reflexion verbal reflect")
    add_store(s)
    s.add_argument("trial_id")
    s.add_argument("feedback")
    s.set_defaults(func=cmd_rx_reflect)

    s = sub.add_parser("rx-store", help="Reflexion memory store")
    add_store(s)
    s.add_argument("reflection_id")
    s.set_defaults(func=cmd_rx_store)

    s = sub.add_parser("rx-next", help="Reflexion next trial")
    add_store(s)
    s.add_argument("reflections", type=int)
    s.set_defaults(func=cmd_rx_next)

    s = sub.add_parser("rx-loop", help="Reflexion loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["trial", "evaluate", "reflect", "store"]
    )
    s.set_defaults(func=cmd_rx_loop)

    s = sub.add_parser("sc-sample", help="Self-Consistency sample path")
    add_store(s)
    s.add_argument("path_idx", type=int)
    s.add_argument("answer")
    s.set_defaults(func=cmd_sc_sample)

    s = sub.add_parser("sc-collect", help="Self-Consistency collect answers")
    add_store(s)
    s.add_argument("n", type=int)
    s.set_defaults(func=cmd_sc_collect)

    s = sub.add_parser("sc-vote", help="Self-Consistency majority vote")
    add_store(s)
    s.add_argument("votes_json")
    s.set_defaults(func=cmd_sc_vote)

    s = sub.add_parser("sc-marginalize", help="Self-Consistency marginalize")
    add_store(s)
    s.add_argument("paths", type=int)
    s.add_argument("unique_answers", type=int)
    s.set_defaults(func=cmd_sc_marginalize)

    s = sub.add_parser("sc-temp", help="Self-Consistency temperature")
    add_store(s)
    s.add_argument("temp", type=float)
    s.set_defaults(func=cmd_sc_temp)

    s = sub.add_parser("sc-loop", help="Self-Consistency loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["sample", "collect", "vote", "marginalize"]
    )
    s.set_defaults(func=cmd_sc_loop)

    s = sub.add_parser("tot-propose", help="ToT propose")
    add_store(s)
    s.add_argument("parent_id")
    s.add_argument("text")
    s.set_defaults(func=cmd_tot_propose)

    s = sub.add_parser("tot-evaluate", help="ToT evaluate")
    add_store(s)
    s.add_argument("node_id")
    s.add_argument("score", type=float)
    s.set_defaults(func=cmd_tot_evaluate)

    s = sub.add_parser("tot-expand", help="ToT expand")
    add_store(s)
    s.add_argument("breadth", type=int)
    s.add_argument("depth", type=int)
    s.set_defaults(func=cmd_tot_expand)

    s = sub.add_parser("tot-backtrack", help="ToT backtrack")
    add_store(s)
    s.add_argument("from_node")
    s.set_defaults(func=cmd_tot_backtrack)

    s = sub.add_parser("tot-select", help="ToT select best")
    add_store(s)
    s.add_argument("candidates", type=int)
    s.set_defaults(func=cmd_tot_select)

    s = sub.add_parser("tot-loop", help="ToT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["propose", "evaluate", "expand", "select"]
    )
    s.set_defaults(func=cmd_tot_loop)

    s = sub.add_parser("ltm-decompose", help="LtM decompose")
    add_store(s)
    s.add_argument("problem")
    s.add_argument("n_subs", type=int)
    s.set_defaults(func=cmd_ltm_decompose)

    s = sub.add_parser("ltm-solve", help="LtM solve sub")
    add_store(s)
    s.add_argument("decomp_id")
    s.add_argument("sub_idx", type=int)
    s.set_defaults(func=cmd_ltm_solve)

    s = sub.add_parser("ltm-carry", help="LtM carry forward")
    add_store(s)
    s.add_argument("answered", type=int)
    s.set_defaults(func=cmd_ltm_carry)

    s = sub.add_parser("ltm-compose", help="LtM compose final")
    add_store(s)
    s.add_argument("subs_done", type=int)
    s.set_defaults(func=cmd_ltm_compose)

    s = sub.add_parser("ltm-easy", help="LtM easy to hard")
    add_store(s)
    s.add_argument("exemplars", type=int)
    s.set_defaults(func=cmd_ltm_easy)

    s = sub.add_parser("ltm-loop", help="LtM loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["decompose", "solve", "carry", "compose"]
    )
    s.set_defaults(func=cmd_ltm_loop)

    s = sub.add_parser("got-add", help="GoT add thought")
    add_store(s)
    s.add_argument("text")
    s.set_defaults(func=cmd_got_add)

    s = sub.add_parser("got-link", help="GoT link")
    add_store(s)
    s.add_argument("src")
    s.add_argument("dst")
    s.set_defaults(func=cmd_got_link)

    s = sub.add_parser("got-aggregate", help="GoT aggregate")
    add_store(s)
    s.add_argument("inputs", type=int)
    s.set_defaults(func=cmd_got_aggregate)

    s = sub.add_parser("got-feedback", help="GoT feedback")
    add_store(s)
    s.add_argument("vertex_id")
    s.set_defaults(func=cmd_got_feedback)

    s = sub.add_parser("got-score", help="GoT score graph")
    add_store(s)
    s.add_argument("vertices", type=int)
    s.add_argument("edges", type=int)
    s.set_defaults(func=cmd_got_score)

    s = sub.add_parser("got-loop", help="GoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["add", "link", "aggregate", "score"]
    )
    s.set_defaults(func=cmd_got_loop)

    s = sub.add_parser("pot-emit", help="PoT emit program")
    add_store(s)
    s.add_argument("problem")
    s.add_argument("--lang", default="python")
    s.set_defaults(func=cmd_pot_emit)

    s = sub.add_parser("pot-run", help="PoT sandbox run")
    add_store(s)
    s.add_argument("program_id")
    s.set_defaults(func=cmd_pot_run)

    s = sub.add_parser("pot-read", help="PoT read result")
    add_store(s)
    s.add_argument("result_id")
    s.set_defaults(func=cmd_pot_read)

    s = sub.add_parser("pot-sc", help="PoT self-consistency")
    add_store(s)
    s.add_argument("samples", type=int)
    s.set_defaults(func=cmd_pot_sc)

    s = sub.add_parser("pot-disentangle", help="PoT disentangle")
    add_store(s)
    s.add_argument("--offload", action="store_true")
    s.set_defaults(func=cmd_pot_disentangle)

    s = sub.add_parser("pot-loop", help="PoT loop plan")
    add_store(s)
    s.add_argument("phase", choices=["emit", "run", "read", "vote"])
    s.set_defaults(func=cmd_pot_loop)

    s = sub.add_parser("aot-load", help="AoT load algorithm")
    add_store(s)
    s.add_argument("name")
    s.set_defaults(func=cmd_aot_load)

    s = sub.add_parser("aot-explore", help="AoT explore subtree")
    add_store(s)
    s.add_argument("depth", type=int)
    s.add_argument("branch", type=int)
    s.set_defaults(func=cmd_aot_explore)

    s = sub.add_parser("aot-tunnel", help="AoT tunnel vision")
    add_store(s)
    s.add_argument("--activate", action="store_true")
    s.set_defaults(func=cmd_aot_tunnel)

    s = sub.add_parser("aot-budget", help="AoT query budget")
    add_store(s)
    s.add_argument("queries", type=int)
    s.set_defaults(func=cmd_aot_budget)

    s = sub.add_parser("aot-surpass", help="AoT surpass algo")
    add_store(s)
    s.add_argument("--intuition", action="store_true")
    s.set_defaults(func=cmd_aot_surpass)

    s = sub.add_parser("aot-loop", help="AoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["load", "explore", "tunnel", "budget"]
    )
    s.set_defaults(func=cmd_aot_loop)

    s = sub.add_parser("rap-state", help="RAP world state")
    add_store(s)
    s.add_argument("state")
    s.set_defaults(func=cmd_rap_state)

    s = sub.add_parser("rap-expand", help="RAP expand")
    add_store(s)
    s.add_argument("state_id")
    s.add_argument("actions", type=int)
    s.set_defaults(func=cmd_rap_expand)

    s = sub.add_parser("rap-reward", help="RAP reward")
    add_store(s)
    s.add_argument("state_id")
    s.add_argument("reward", type=float)
    s.set_defaults(func=cmd_rap_reward)

    s = sub.add_parser("rap-select", help="RAP select path")
    add_store(s)
    s.add_argument("visits", type=int)
    s.set_defaults(func=cmd_rap_select)

    s = sub.add_parser("rap-balance", help="RAP balance")
    add_store(s)
    s.add_argument("explore", type=float)
    s.set_defaults(func=cmd_rap_balance)

    s = sub.add_parser("rap-loop", help="RAP loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["state", "expand", "reward", "select"]
    )
    s.set_defaults(func=cmd_rap_loop)

    s = sub.add_parser("sot-skeleton", help="SoT emit skeleton")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_sot_skeleton)

    s = sub.add_parser("sot-extract", help="SoT extract points")
    add_store(s)
    s.add_argument("skeleton_id")
    s.add_argument("points", type=int)
    s.set_defaults(func=cmd_sot_extract)

    s = sub.add_parser("sot-expand", help="SoT parallel expand")
    add_store(s)
    s.add_argument("points", type=int)
    s.set_defaults(func=cmd_sot_expand)

    s = sub.add_parser("sot-router", help="SoT router")
    add_store(s)
    s.add_argument("--suitable", action="store_true")
    s.set_defaults(func=cmd_sot_router)

    s = sub.add_parser("sot-latency", help="SoT latency gain")
    add_store(s)
    s.add_argument("sequential", type=int)
    s.add_argument("parallel", type=int)
    s.set_defaults(func=cmd_sot_latency)

    s = sub.add_parser("sot-loop", help="SoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["skeleton", "extract", "expand", "route"]
    )
    s.set_defaults(func=cmd_sot_loop)

    s = sub.add_parser("bot-distill", help="BoT distill template")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_bot_distill)

    s = sub.add_parser("bot-retrieve", help="BoT retrieve template")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_bot_retrieve)

    s = sub.add_parser("bot-instantiate", help="BoT instantiate")
    add_store(s)
    s.add_argument("template_id")
    s.set_defaults(func=cmd_bot_instantiate)

    s = sub.add_parser("bot-update", help="BoT buffer update")
    add_store(s)
    s.add_argument("templates", type=int)
    s.set_defaults(func=cmd_bot_update)

    s = sub.add_parser("bot-cost", help="BoT cost ratio")
    add_store(s)
    s.add_argument("multi_query", type=int)
    s.add_argument("bot", type=int)
    s.set_defaults(func=cmd_bot_cost)

    s = sub.add_parser("bot-loop", help="BoT loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["distill", "retrieve", "instantiate", "update"],
    )
    s.set_defaults(func=cmd_bot_loop)

    s = sub.add_parser("sd-select", help="Self-Discover select modules")
    add_store(s)
    s.add_argument("task")
    s.add_argument("modules", type=int)
    s.set_defaults(func=cmd_sd_select)

    s = sub.add_parser("sd-adapt", help="Self-Discover adapt")
    add_store(s)
    s.add_argument("select_id")
    s.set_defaults(func=cmd_sd_adapt)

    s = sub.add_parser("sd-implement", help="Self-Discover implement")
    add_store(s)
    s.add_argument("adapt_id")
    s.add_argument("keys", type=int)
    s.set_defaults(func=cmd_sd_implement)

    s = sub.add_parser("sd-apply", help="Self-Discover apply instance")
    add_store(s)
    s.add_argument("structure_id")
    s.set_defaults(func=cmd_sd_apply)

    s = sub.add_parser("sd-ratio", help="Self-Discover compute ratio")
    add_store(s)
    s.add_argument("sc_calls", type=int)
    s.add_argument("self_discover", type=int)
    s.set_defaults(func=cmd_sd_ratio)

    s = sub.add_parser("sd-loop", help="Self-Discover loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["select", "adapt", "implement", "apply"]
    )
    s.set_defaults(func=cmd_sd_loop)

    s = sub.add_parser("mp-break", help="Meta-Prompting break task")
    add_store(s)
    s.add_argument("query")
    s.add_argument("pieces", type=int)
    s.set_defaults(func=cmd_mp_break)

    s = sub.add_parser("mp-assign", help="Meta-Prompting assign expert")
    add_store(s)
    s.add_argument("piece_idx", type=int)
    s.add_argument("expert")
    s.set_defaults(func=cmd_mp_assign)

    s = sub.add_parser("mp-oversee", help="Meta-Prompting oversee")
    add_store(s)
    s.add_argument("messages", type=int)
    s.set_defaults(func=cmd_mp_oversee)

    s = sub.add_parser("mp-verify", help="Meta-Prompting verify")
    add_store(s)
    s.add_argument("claim")
    s.set_defaults(func=cmd_mp_verify)

    s = sub.add_parser("mp-agnostic", help="Meta-Prompting task-agnostic")
    add_store(s)
    s.add_argument("--scaffold", action="store_true")
    s.set_defaults(func=cmd_mp_agnostic)

    s = sub.add_parser("mp-loop", help="Meta-Prompting loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["break", "assign", "oversee", "verify"]
    )
    s.set_defaults(func=cmd_mp_loop)

    s = sub.add_parser("qs-bounds", help="Quiet-STaR thought bounds")
    add_store(s)
    s.add_argument("start")
    s.add_argument("end")
    s.set_defaults(func=cmd_qs_bounds)

    s = sub.add_parser("qs-sample", help="Quiet-STaR parallel sample")
    add_store(s)
    s.add_argument("positions", type=int)
    s.add_argument("thoughts", type=int)
    s.set_defaults(func=cmd_qs_sample)

    s = sub.add_parser("qs-mix", help="Quiet-STaR mix head")
    add_store(s)
    s.add_argument("weight", type=float)
    s.set_defaults(func=cmd_qs_mix)

    s = sub.add_parser("qs-aid", help="Quiet-STaR hard token aid")
    add_store(s)
    s.add_argument("hard_tokens", type=int)
    s.add_argument("helped", type=int)
    s.set_defaults(func=cmd_qs_aid)

    s = sub.add_parser("qs-zeroshot", help="Quiet-STaR zero-shot flag")
    add_store(s)
    s.add_argument("--improved", action="store_true")
    s.set_defaults(func=cmd_qs_zeroshot)

    s = sub.add_parser("qs-loop", help="Quiet-STaR loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["bounds", "sample", "mix", "aid"]
    )
    s.set_defaults(func=cmd_qs_loop)

    s = sub.add_parser("dep-decompose", help="Decomposed Prompting decompose")
    add_store(s)
    s.add_argument("task")
    s.add_argument("subs", type=int)
    s.set_defaults(func=cmd_dep_decompose)

    s = sub.add_parser("dep-delegate", help="Decomposed Prompting delegate")
    add_store(s)
    s.add_argument("handler")
    s.add_argument("sub_idx", type=int)
    s.set_defaults(func=cmd_dep_delegate)

    s = sub.add_parser("dep-recurse", help="Decomposed Prompting recurse")
    add_store(s)
    s.add_argument("depth", type=int)
    s.set_defaults(func=cmd_dep_recurse)

    s = sub.add_parser("dep-swap", help="Decomposed Prompting swap symbolic")
    add_store(s)
    s.add_argument("module")
    s.set_defaults(func=cmd_dep_swap)

    s = sub.add_parser("dep-library", help="Decomposed Prompting library size")
    add_store(s)
    s.add_argument("handlers", type=int)
    s.set_defaults(func=cmd_dep_library)

    s = sub.add_parser("dep-loop", help="Decomposed Prompting loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["decompose", "delegate", "recurse", "swap"]
    )
    s.set_defaults(func=cmd_dep_loop)

    s = sub.add_parser("star-generate", help="STaR generate")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_star_generate)

    s = sub.add_parser("star-filter", help="STaR filter correct")
    add_store(s)
    s.add_argument("gen_id")
    s.add_argument("--correct", action="store_true")
    s.set_defaults(func=cmd_star_filter)

    s = sub.add_parser("star-rationalize", help="STaR rationalize")
    add_store(s)
    s.add_argument("question")
    s.add_argument("answer")
    s.set_defaults(func=cmd_star_rationalize)

    s = sub.add_parser("star-finetune", help="STaR finetune proxy")
    add_store(s)
    s.add_argument("examples", type=int)
    s.set_defaults(func=cmd_star_finetune)

    s = sub.add_parser("star-round", help="STaR bootstrap round")
    add_store(s)
    s.add_argument("round_n", type=int)
    s.set_defaults(func=cmd_star_round)

    s = sub.add_parser("star-loop", help="STaR loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["generate", "filter", "rationalize", "finetune"],
    )
    s.set_defaults(func=cmd_star_loop)

    s = sub.add_parser("cr-propose", help="Cumulative Reasoning propose")
    add_store(s)
    s.add_argument("step")
    s.set_defaults(func=cmd_cr_propose)

    s = sub.add_parser("cr-verify", help="Cumulative Reasoning verify")
    add_store(s)
    s.add_argument("proposal_id")
    s.add_argument("--valid", action="store_true")
    s.set_defaults(func=cmd_cr_verify)

    s = sub.add_parser("cr-accumulate", help="Cumulative Reasoning accumulate")
    add_store(s)
    s.add_argument("accepted", type=int)
    s.set_defaults(func=cmd_cr_accumulate)

    s = sub.add_parser("cr-report", help="Cumulative Reasoning report")
    add_store(s)
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_cr_report)

    s = sub.add_parser("cr-roles", help="Cumulative Reasoning roles")
    add_store(s)
    s.add_argument("roles", type=int, nargs="?", default=3)
    s.set_defaults(func=cmd_cr_roles)

    s = sub.add_parser("cr-loop", help="Cumulative Reasoning loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["propose", "verify", "accumulate", "report"],
    )
    s.set_defaults(func=cmd_cr_loop)

    s = sub.add_parser("ps-plan", help="Plan-and-Solve devise plan")
    add_store(s)
    s.add_argument("problem")
    s.add_argument("subtasks", type=int)
    s.set_defaults(func=cmd_ps_plan)

    s = sub.add_parser("ps-execute", help="Plan-and-Solve execute")
    add_store(s)
    s.add_argument("plan_id")
    s.add_argument("step", type=int)
    s.set_defaults(func=cmd_ps_execute)

    s = sub.add_parser("ps-extract", help="Plan-and-Solve PS+ extract")
    add_store(s)
    s.add_argument("variables", type=int)
    s.set_defaults(func=cmd_ps_extract)

    s = sub.add_parser("ps-guard", help="Plan-and-Solve calc guard")
    add_store(s)
    s.add_argument("--careful", action="store_true")
    s.set_defaults(func=cmd_ps_guard)

    s = sub.add_parser("ps-missing", help="Plan-and-Solve missing-step fix")
    add_store(s)
    s.add_argument("--fixed", action="store_true")
    s.set_defaults(func=cmd_ps_missing)

    s = sub.add_parser("ps-loop", help="Plan-and-Solve loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["plan", "execute", "extract", "guard"]
    )
    s.set_defaults(func=cmd_ps_loop)

    s = sub.add_parser("php-base", help="PHP base answer")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_php_base)

    s = sub.add_parser("php-hint", help="PHP emit hint")
    add_store(s)
    s.add_argument("answer_id")
    s.add_argument("hint")
    s.set_defaults(func=cmd_php_hint)

    s = sub.add_parser("php-reask", help="PHP reask")
    add_store(s)
    s.add_argument("hints", type=int)
    s.set_defaults(func=cmd_php_reask)

    s = sub.add_parser("php-stop", help="PHP stable stop")
    add_store(s)
    s.add_argument("--same-twice", action="store_true")
    s.set_defaults(func=cmd_php_stop)

    s = sub.add_parser("php-sc", help="PHP combine self-consistency")
    add_store(s)
    s.add_argument("--reduced", action="store_true")
    s.set_defaults(func=cmd_php_sc)

    s = sub.add_parser("php-loop", help="PHP loop plan")
    add_store(s)
    s.add_argument("phase", choices=["base", "hint", "reask", "stop"])
    s.set_defaults(func=cmd_php_loop)

    s = sub.add_parser("ac-program", help="AgentCoder programmer")
    add_store(s)
    s.add_argument("requirement")
    s.set_defaults(func=cmd_ac_program)

    s = sub.add_parser("ac-design", help="AgentCoder test designer")
    add_store(s)
    s.add_argument("requirement")
    s.add_argument("cases", type=int)
    s.set_defaults(func=cmd_ac_design)

    s = sub.add_parser("ac-execute", help="AgentCoder test executor")
    add_store(s)
    s.add_argument("code_id")
    s.add_argument("suite_id")
    s.set_defaults(func=cmd_ac_execute)

    s = sub.add_parser("ac-refine", help="AgentCoder refine")
    add_store(s)
    s.add_argument("code_id")
    s.add_argument("feedback_id")
    s.set_defaults(func=cmd_ac_refine)

    s = sub.add_parser("ac-pass", help="AgentCoder pass gate")
    add_store(s)
    s.add_argument("--all-pass", action="store_true")
    s.set_defaults(func=cmd_ac_pass)

    s = sub.add_parser("ac-loop", help="AgentCoder loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["program", "design", "execute", "refine"]
    )
    s.set_defaults(func=cmd_ac_loop)

    s = sub.add_parser("pal-emit", help="PAL emit program")
    add_store(s)
    s.add_argument("problem")
    s.add_argument("--lang", default="python")
    s.set_defaults(func=cmd_pal_emit)

    s = sub.add_parser("pal-offload", help="PAL offload solve")
    add_store(s)
    s.add_argument("program_id")
    s.set_defaults(func=cmd_pal_offload)

    s = sub.add_parser("pal-read", help="PAL read answer")
    add_store(s)
    s.add_argument("result_id")
    s.set_defaults(func=cmd_pal_read)

    s = sub.add_parser("pal-decompose", help="PAL decompose-only flag")
    add_store(s)
    s.add_argument("--llm-solves", action="store_true")
    s.set_defaults(func=cmd_pal_decompose)

    s = sub.add_parser("pal-vs-cot", help="PAL vs CoT flag")
    add_store(s)
    s.add_argument("--beats", action="store_true")
    s.set_defaults(func=cmd_pal_vs_cot)

    s = sub.add_parser("pal-loop", help="PAL loop plan")
    add_store(s)
    s.add_argument("phase", choices=["emit", "offload", "read", "flag"])
    s.set_defaults(func=cmd_pal_loop)

    s = sub.add_parser("fcot-translate", help="Faithful CoT translate")
    add_store(s)
    s.add_argument("query")
    s.add_argument("symbolic")
    s.set_defaults(func=cmd_fcot_translate)

    s = sub.add_parser("fcot-solve", help="Faithful CoT solve")
    add_store(s)
    s.add_argument("chain_id")
    s.set_defaults(func=cmd_fcot_solve)

    s = sub.add_parser("fcot-faith", help="Faithful CoT faithfulness")
    add_store(s)
    s.add_argument("--explains", action="store_true")
    s.set_defaults(func=cmd_fcot_faith)

    s = sub.add_parser("fcot-interleave", help="Faithful CoT interleave")
    add_store(s)
    s.add_argument("--nl-sl", action="store_true")
    s.set_defaults(func=cmd_fcot_interleave)

    s = sub.add_parser("fcot-vs-cot", help="Faithful CoT vs CoT")
    add_store(s)
    s.add_argument("--beats", action="store_true")
    s.set_defaults(func=cmd_fcot_vs_cot)

    s = sub.add_parser("fcot-loop", help="Faithful CoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["translate", "solve", "faithfulness", "flag"]
    )
    s.set_defaults(func=cmd_fcot_loop)

    s = sub.add_parser("lats-expand", help="LATS expand")
    add_store(s)
    s.add_argument("state")
    s.add_argument("actions", type=int)
    s.set_defaults(func=cmd_lats_expand)

    s = sub.add_parser("lats-value", help="LATS value")
    add_store(s)
    s.add_argument("node_id")
    s.add_argument("score", type=float)
    s.set_defaults(func=cmd_lats_value)

    s = sub.add_parser("lats-reflect", help="LATS reflect")
    add_store(s)
    s.add_argument("node_id")
    s.add_argument("feedback")
    s.set_defaults(func=cmd_lats_reflect)

    s = sub.add_parser("lats-select", help="LATS select")
    add_store(s)
    s.add_argument("node_id")
    s.set_defaults(func=cmd_lats_select)

    s = sub.add_parser("lats-env", help="LATS env feedback")
    add_store(s)
    s.add_argument("--useful", action="store_true")
    s.set_defaults(func=cmd_lats_env)

    s = sub.add_parser("lats-loop", help="LATS loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["expand", "value", "reflect", "select"]
    )
    s.set_defaults(func=cmd_lats_loop)

    s = sub.add_parser("voy-curriculum", help="Voyager curriculum")
    add_store(s)
    s.add_argument("level", type=int)
    s.add_argument("task")
    s.set_defaults(func=cmd_voy_curriculum)

    s = sub.add_parser("voy-store", help="Voyager skill store")
    add_store(s)
    s.add_argument("name")
    s.add_argument("code_ref")
    s.set_defaults(func=cmd_voy_store)

    s = sub.add_parser("voy-retrieve", help="Voyager skill retrieve")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_voy_retrieve)

    s = sub.add_parser("voy-verify", help="Voyager self-verify")
    add_store(s)
    s.add_argument("skill_id")
    s.add_argument("--passed", action="store_true")
    s.set_defaults(func=cmd_voy_verify)

    s = sub.add_parser("voy-compose", help="Voyager compose")
    add_store(s)
    s.add_argument("skills", type=int)
    s.set_defaults(func=cmd_voy_compose)

    s = sub.add_parser("voy-loop", help="Voyager loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["curriculum", "store", "retrieve", "verify"]
    )
    s.set_defaults(func=cmd_voy_loop)

    s = sub.add_parser("rewoo-plan", help="ReWOO plan")
    add_store(s)
    s.add_argument("task")
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_rewoo_plan)

    s = sub.add_parser("rewoo-worker", help="ReWOO worker")
    add_store(s)
    s.add_argument("plan_id")
    s.add_argument("step", type=int)
    s.set_defaults(func=cmd_rewoo_worker)

    s = sub.add_parser("rewoo-solver", help="ReWOO solver")
    add_store(s)
    s.add_argument("plan_id")
    s.add_argument("evidence", type=int)
    s.set_defaults(func=cmd_rewoo_solver)

    s = sub.add_parser("rewoo-decouple", help="ReWOO decouple")
    add_store(s)
    s.add_argument("--from-obs", action="store_true")
    s.set_defaults(func=cmd_rewoo_decouple)

    s = sub.add_parser("rewoo-token", help="ReWOO token save")
    add_store(s)
    s.add_argument("--reduced", action="store_true")
    s.set_defaults(func=cmd_rewoo_token)

    s = sub.add_parser("rewoo-loop", help="ReWOO loop plan")
    add_store(s)
    s.add_argument("phase", choices=["plan", "worker", "solve", "flag"])
    s.set_defaults(func=cmd_rewoo_loop)

    s = sub.add_parser("critic-draft", help="CRITIC draft")
    add_store(s)
    s.add_argument("question")
    s.set_defaults(func=cmd_critic_draft)

    s = sub.add_parser("critic-check", help="CRITIC tool check")
    add_store(s)
    s.add_argument("draft_id")
    s.add_argument("tool")
    s.set_defaults(func=cmd_critic_check)

    s = sub.add_parser("critic-revise", help="CRITIC revise")
    add_store(s)
    s.add_argument("draft_id")
    s.add_argument("critique_id")
    s.set_defaults(func=cmd_critic_revise)

    s = sub.add_parser("critic-iterate", help="CRITIC iterate")
    add_store(s)
    s.add_argument("rounds", type=int)
    s.set_defaults(func=cmd_critic_iterate)

    s = sub.add_parser("critic-stop", help="CRITIC stop")
    add_store(s)
    s.add_argument("--satisfied", action="store_true")
    s.set_defaults(func=cmd_critic_stop)

    s = sub.add_parser("critic-loop", help="CRITIC loop plan")
    add_store(s)
    s.add_argument("phase", choices=["draft", "check", "revise", "stop"])
    s.set_defaults(func=cmd_critic_loop)

    s = sub.add_parser("dv-program", help="Deductive Natural Program")
    add_store(s)
    s.add_argument("claim")
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_dv_program)

    s = sub.add_parser("dv-verify", help="Deductive step verify")
    add_store(s)
    s.add_argument("program_id")
    s.add_argument("step", type=int)
    s.set_defaults(func=cmd_dv_verify)

    s = sub.add_parser("dv-premises", help="Deductive premise scope")
    add_store(s)
    s.add_argument("premises", type=int)
    s.set_defaults(func=cmd_dv_premises)

    s = sub.add_parser("dv-unanimity", help="Deductive unanimity")
    add_store(s)
    s.add_argument("--all-pass", action="store_true")
    s.set_defaults(func=cmd_dv_unanimity)

    s = sub.add_parser("dv-ground", help="Deductive ground")
    add_store(s)
    s.add_argument("--grounded", action="store_true")
    s.set_defaults(func=cmd_dv_ground)

    s = sub.add_parser("dv-loop", help="Deductive loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["program", "verify", "unanimity", "ground"]
    )
    s.set_defaults(func=cmd_dv_loop)

    s = sub.add_parser("hgpt-plan", help="HuggingGPT plan")
    add_store(s)
    s.add_argument("request")
    s.add_argument("tasks", type=int)
    s.set_defaults(func=cmd_hgpt_plan)

    s = sub.add_parser("hgpt-select", help="HuggingGPT select")
    add_store(s)
    s.add_argument("plan_id")
    s.add_argument("model")
    s.set_defaults(func=cmd_hgpt_select)

    s = sub.add_parser("hgpt-execute", help="HuggingGPT execute")
    add_store(s)
    s.add_argument("selection_id")
    s.set_defaults(func=cmd_hgpt_execute)

    s = sub.add_parser("hgpt-summarize", help="HuggingGPT summarize")
    add_store(s)
    s.add_argument("results", type=int)
    s.set_defaults(func=cmd_hgpt_summarize)

    s = sub.add_parser("hgpt-modality", help="HuggingGPT modality")
    add_store(s)
    s.add_argument("modalities", type=int)
    s.set_defaults(func=cmd_hgpt_modality)

    s = sub.add_parser("hgpt-loop", help="HuggingGPT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["plan", "select", "execute", "summarize"]
    )
    s.set_defaults(func=cmd_hgpt_loop)

    s = sub.add_parser("mad-propose", help="Multiagent Debate propose")
    add_store(s)
    s.add_argument("agent")
    s.add_argument("answer")
    s.set_defaults(func=cmd_mad_propose)

    s = sub.add_parser("mad-debate", help="Multiagent Debate round")
    add_store(s)
    s.add_argument("round_n", type=int)
    s.add_argument("agents", type=int)
    s.set_defaults(func=cmd_mad_debate)

    s = sub.add_parser("mad-critique", help="Multiagent Debate critique")
    add_store(s)
    s.add_argument("proposal_id")
    s.add_argument("critique")
    s.set_defaults(func=cmd_mad_critique)

    s = sub.add_parser("mad-converge", help="Multiagent Debate converge")
    add_store(s)
    s.add_argument("--common", action="store_true")
    s.set_defaults(func=cmd_mad_converge)

    s = sub.add_parser("mad-factuality", help="Multiagent Debate factuality")
    add_store(s)
    s.add_argument("--improved", action="store_true")
    s.set_defaults(func=cmd_mad_factuality)

    s = sub.add_parser("mad-loop", help="Multiagent Debate loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["propose", "debate", "critique", "converge"]
    )
    s.set_defaults(func=cmd_mad_loop)

    s = sub.add_parser("autocot-cluster", help="Auto-CoT cluster")
    add_store(s)
    s.add_argument("questions", type=int)
    s.add_argument("clusters", type=int)
    s.set_defaults(func=cmd_autocot_cluster)

    s = sub.add_parser("autocot-sample", help="Auto-CoT sample")
    add_store(s)
    s.add_argument("cluster_id")
    s.set_defaults(func=cmd_autocot_sample)

    s = sub.add_parser("autocot-generate", help="Auto-CoT generate")
    add_store(s)
    s.add_argument("demo_id")
    s.set_defaults(func=cmd_autocot_generate)

    s = sub.add_parser("autocot-heuristic", help="Auto-CoT heuristic")
    add_store(s)
    s.add_argument("max_steps", type=int)
    s.set_defaults(func=cmd_autocot_heuristic)

    s = sub.add_parser("autocot-diversity", help="Auto-CoT diversity")
    add_store(s)
    s.add_argument("--diverse", action="store_true")
    s.set_defaults(func=cmd_autocot_diversity)

    s = sub.add_parser("autocot-loop", help="Auto-CoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["cluster", "sample", "generate", "heuristic"]
    )
    s.set_defaults(func=cmd_autocot_loop)

    s = sub.add_parser("camel-roles", help="CAMEL roles")
    add_store(s)
    s.add_argument("user_role")
    s.add_argument("assistant_role")
    s.set_defaults(func=cmd_camel_roles)

    s = sub.add_parser("camel-inception", help="CAMEL inception")
    add_store(s)
    s.add_argument("role_id")
    s.add_argument("task")
    s.set_defaults(func=cmd_camel_inception)

    s = sub.add_parser("camel-turn", help="CAMEL turn")
    add_store(s)
    s.add_argument("inception_id")
    s.add_argument("speaker")
    s.set_defaults(func=cmd_camel_turn)

    s = sub.add_parser("camel-complete", help="CAMEL complete")
    add_store(s)
    s.add_argument("--done", action="store_true")
    s.set_defaults(func=cmd_camel_complete)

    s = sub.add_parser("camel-society", help="CAMEL society")
    add_store(s)
    s.add_argument("agents", type=int)
    s.set_defaults(func=cmd_camel_society)

    s = sub.add_parser("camel-loop", help="CAMEL loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["roles", "inception", "turn", "complete"]
    )
    s.set_defaults(func=cmd_camel_loop)

    s = sub.add_parser("cham-inventory", help="Chameleon inventory")
    add_store(s)
    s.add_argument("tools", type=int)
    s.set_defaults(func=cmd_cham_inventory)

    s = sub.add_parser("cham-plan", help="Chameleon plan")
    add_store(s)
    s.add_argument("task")
    s.add_argument("modules", type=int)
    s.set_defaults(func=cmd_cham_plan)

    s = sub.add_parser("cham-compose", help="Chameleon compose")
    add_store(s)
    s.add_argument("plan_id")
    s.add_argument("module")
    s.set_defaults(func=cmd_cham_compose)

    s = sub.add_parser("cham-execute", help="Chameleon execute")
    add_store(s)
    s.add_argument("plan_id")
    s.set_defaults(func=cmd_cham_execute)

    s = sub.add_parser("cham-constraint", help="Chameleon constraint")
    add_store(s)
    s.add_argument("--inferred", action="store_true")
    s.set_defaults(func=cmd_cham_constraint)

    s = sub.add_parser("cham-loop", help="Chameleon loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["inventory", "plan", "compose", "execute"]
    )
    s.set_defaults(func=cmd_cham_loop)

    s = sub.add_parser("rot-trigger", help="RoT trigger")
    add_store(s)
    s.add_argument("token")
    s.set_defaults(func=cmd_rot_trigger)

    s = sub.add_parser("rot-divide", help="RoT divide")
    add_store(s)
    s.add_argument("problem")
    s.add_argument("parts", type=int)
    s.set_defaults(func=cmd_rot_divide)

    s = sub.add_parser("rot-conquer", help="RoT conquer")
    add_store(s)
    s.add_argument("divide_id")
    s.add_argument("part", type=int)
    s.set_defaults(func=cmd_rot_conquer)

    s = sub.add_parser("rot-merge", help="RoT merge")
    add_store(s)
    s.add_argument("parts", type=int)
    s.set_defaults(func=cmd_rot_merge)

    s = sub.add_parser("rot-limit", help="RoT context limit")
    add_store(s)
    s.add_argument("--within", action="store_true")
    s.set_defaults(func=cmd_rot_limit)

    s = sub.add_parser("rot-loop", help="RoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["trigger", "divide", "conquer", "merge"]
    )
    s.set_defaults(func=cmd_rot_loop)

    s = sub.add_parser("ap-sample", help="Active-Prompt sample")
    add_store(s)
    s.add_argument("question")
    s.add_argument("k", type=int)
    s.set_defaults(func=cmd_ap_sample)

    s = sub.add_parser("ap-uncertainty", help="Active-Prompt uncertainty")
    add_store(s)
    s.add_argument("sample_id")
    s.add_argument("score", type=float)
    s.set_defaults(func=cmd_ap_uncertainty)

    s = sub.add_parser("ap-select", help="Active-Prompt select")
    add_store(s)
    s.add_argument("top_n", type=int)
    s.set_defaults(func=cmd_ap_select)

    s = sub.add_parser("ap-annotate", help="Active-Prompt annotate")
    add_store(s)
    s.add_argument("question_id")
    s.add_argument("cot")
    s.set_defaults(func=cmd_ap_annotate)

    s = sub.add_parser("ap-pool", help="Active-Prompt pool")
    add_store(s)
    s.add_argument("size", type=int)
    s.set_defaults(func=cmd_ap_pool)

    s = sub.add_parser("ap-loop", help="Active-Prompt loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["sample", "uncertainty", "select", "annotate"]
    )
    s.set_defaults(func=cmd_ap_loop)

    s = sub.add_parser("ana-recall", help="Analogical recall")
    add_store(s)
    s.add_argument("problem")
    s.set_defaults(func=cmd_ana_recall)

    s = sub.add_parser("ana-knowledge", help="Analogical knowledge")
    add_store(s)
    s.add_argument("problem")
    s.add_argument("facts", type=int)
    s.set_defaults(func=cmd_ana_knowledge)

    s = sub.add_parser("ana-solve", help="Analogical solve")
    add_store(s)
    s.add_argument("exemplar_id")
    s.set_defaults(func=cmd_ana_solve)

    s = sub.add_parser("ana-adapt", help="Analogical adapt")
    add_store(s)
    s.add_argument("--tailored", action="store_true")
    s.set_defaults(func=cmd_ana_adapt)

    s = sub.add_parser("ana-no-label", help="Analogical no-label")
    add_store(s)
    s.add_argument("--needs-labels", action="store_true")
    s.set_defaults(func=cmd_ana_no_label)

    s = sub.add_parser("ana-loop", help="Analogical loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["recall", "knowledge", "solve", "adapt"]
    )
    s.set_defaults(func=cmd_ana_loop)

    s = sub.add_parser("cbp-score", help="Complexity-Based score")
    add_store(s)
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_cbp_score)

    s = sub.add_parser("cbp-select", help="Complexity-Based select")
    add_store(s)
    s.add_argument("min_steps", type=int)
    s.add_argument("exemplars", type=int)
    s.set_defaults(func=cmd_cbp_select)

    s = sub.add_parser("cbp-sample", help="Complexity-Based sample chains")
    add_store(s)
    s.add_argument("n", type=int)
    s.set_defaults(func=cmd_cbp_sample)

    s = sub.add_parser("cbp-vote", help="Complexity-Based vote")
    add_store(s)
    s.add_argument("--prefer-complex", action="store_true")
    s.set_defaults(func=cmd_cbp_vote)

    s = sub.add_parser("cbp-robust", help="Complexity-Based robust")
    add_store(s)
    s.add_argument("--under-shift", action="store_true")
    s.set_defaults(func=cmd_cbp_robust)

    s = sub.add_parser("cbp-loop", help="Complexity-Based loop plan")
    add_store(s)
    s.add_argument("phase", choices=["score", "select", "sample", "vote"])
    s.set_defaults(func=cmd_cbp_loop)

    s = sub.add_parser("sb-abstract", help="Step-Back abstract")
    add_store(s)
    s.add_argument("instance")
    s.set_defaults(func=cmd_sb_abstract)

    s = sub.add_parser("sb-principle", help="Step-Back principle")
    add_store(s)
    s.add_argument("concept_id")
    s.add_argument("principle")
    s.set_defaults(func=cmd_sb_principle)

    s = sub.add_parser("sb-reason", help="Step-Back reason")
    add_store(s)
    s.add_argument("principle_id")
    s.set_defaults(func=cmd_sb_reason)

    s = sub.add_parser("sb-path", help="Step-Back path")
    add_store(s)
    s.add_argument("--correct", action="store_true")
    s.set_defaults(func=cmd_sb_path)

    s = sub.add_parser("sb-trap", help="Step-Back detail trap")
    add_store(s)
    s.add_argument("--escaped", action="store_true")
    s.set_defaults(func=cmd_sb_trap)

    s = sub.add_parser("sb-loop", help="Step-Back loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["abstract", "principle", "reason", "path"]
    )
    s.set_defaults(func=cmd_sb_loop)

    s = sub.add_parser("mmcot-fuse", help="Multimodal-CoT fuse")
    add_store(s)
    s.add_argument("text")
    s.add_argument("vision_ref")
    s.set_defaults(func=cmd_mmcot_fuse)

    s = sub.add_parser("mmcot-rationale", help="Multimodal-CoT rationale")
    add_store(s)
    s.add_argument("fuse_id")
    s.set_defaults(func=cmd_mmcot_rationale)

    s = sub.add_parser("mmcot-infer", help="Multimodal-CoT infer")
    add_store(s)
    s.add_argument("rationale_id")
    s.set_defaults(func=cmd_mmcot_infer)

    s = sub.add_parser("mmcot-hallucination", help="Multimodal-CoT hallucination")
    add_store(s)
    s.add_argument("--mitigated", action="store_true")
    s.set_defaults(func=cmd_mmcot_hallucination)

    s = sub.add_parser("mmcot-separate", help="Multimodal-CoT separate")
    add_store(s)
    s.add_argument("--two-stage", action="store_true")
    s.set_defaults(func=cmd_mmcot_separate)

    s = sub.add_parser("mmcot-loop", help="Multimodal-CoT loop plan")
    add_store(s)
    s.add_argument("phase", choices=["fuse", "rationale", "infer", "flag"])
    s.set_defaults(func=cmd_mmcot_loop)

    s = sub.add_parser("mai-abduce", help="Maieutic abduce")
    add_store(s)
    s.add_argument("claim")
    s.add_argument("because")
    s.set_defaults(func=cmd_mai_abduce)

    s = sub.add_parser("mai-recurse", help="Maieutic recurse")
    add_store(s)
    s.add_argument("node_id")
    s.add_argument("depth", type=int)
    s.set_defaults(func=cmd_mai_recurse)

    s = sub.add_parser("mai-sat", help="Maieutic SAT")
    add_store(s)
    s.add_argument("relations", type=int)
    s.set_defaults(func=cmd_mai_sat)

    s = sub.add_parser("mai-consistent", help="Maieutic consistent")
    add_store(s)
    s.add_argument("--consistent", action="store_true")
    s.set_defaults(func=cmd_mai_consistent)

    s = sub.add_parser("mai-unreliable", help="Maieutic unreliable")
    add_store(s)
    s.add_argument("--tolerate", action="store_true")
    s.set_defaults(func=cmd_mai_unreliable)

    s = sub.add_parser("mai-loop", help="Maieutic loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["abduce", "recurse", "sat", "consistent"]
    )
    s.set_defaults(func=cmd_mai_loop)

    s = sub.add_parser("sr-generate", help="Self-Refine generate")
    add_store(s)
    s.add_argument("draft")
    s.set_defaults(func=cmd_sr_generate)

    s = sub.add_parser("sr-feedback", help="Self-Refine feedback")
    add_store(s)
    s.add_argument("gen_id")
    s.set_defaults(func=cmd_sr_feedback)

    s = sub.add_parser("sr-refine", help="Self-Refine refine")
    add_store(s)
    s.add_argument("gen_id")
    s.add_argument("feedback_id")
    s.set_defaults(func=cmd_sr_refine)

    s = sub.add_parser("sr-iterate", help="Self-Refine iterate")
    add_store(s)
    s.add_argument("rounds", type=int)
    s.set_defaults(func=cmd_sr_iterate)

    s = sub.add_parser("sr-no-train", help="Self-Refine no-train")
    add_store(s)
    s.add_argument("--no-rl", action="store_true")
    s.set_defaults(func=cmd_sr_no_train)

    s = sub.add_parser("sr-loop", help="Self-Refine loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["generate", "feedback", "refine", "iterate"]
    )
    s.set_defaults(func=cmd_sr_loop)

    s = sub.add_parser("mcp-recognize", help="Metacognitive recognize")
    add_store(s)
    s.add_argument("knowledge")
    s.set_defaults(func=cmd_mcp_recognize)

    s = sub.add_parser("mcp-interpret", help="Metacognitive interpret")
    add_store(s)
    s.add_argument("recognize_id")
    s.set_defaults(func=cmd_mcp_interpret)

    s = sub.add_parser("mcp-reevaluate", help="Metacognitive reevaluate")
    add_store(s)
    s.add_argument("interpret_id")
    s.set_defaults(func=cmd_mcp_reevaluate)

    s = sub.add_parser("mcp-confidence", help="Metacognitive confidence")
    add_store(s)
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mcp_confidence)

    s = sub.add_parser("mcp-justify", help="Metacognitive justify")
    add_store(s)
    s.add_argument("--justified", action="store_true")
    s.set_defaults(func=cmd_mcp_justify)

    s = sub.add_parser("mcp-loop", help="Metacognitive loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["recognize", "interpret", "reevaluate", "confidence"],
    )
    s.set_defaults(func=cmd_mcp_loop)

    s = sub.add_parser("thot-segment", help="Thread of Thought segment")
    add_store(s)
    s.add_argument("context")
    s.add_argument("pieces", type=int)
    s.set_defaults(func=cmd_thot_segment)

    s = sub.add_parser("thot-analyze", help="Thread of Thought analyze")
    add_store(s)
    s.add_argument("segment_id")
    s.set_defaults(func=cmd_thot_analyze)

    s = sub.add_parser("thot-select", help="Thread of Thought select")
    add_store(s)
    s.add_argument("analyze_id")
    s.set_defaults(func=cmd_thot_select)

    s = sub.add_parser("thot-synthesize", help="Thread of Thought synthesize")
    add_store(s)
    s.add_argument("select_id")
    s.set_defaults(func=cmd_thot_synthesize)

    s = sub.add_parser("thot-plug", help="Thread of Thought plug")
    add_store(s)
    s.add_argument("--plug-and-play", action="store_true")
    s.set_defaults(func=cmd_thot_plug)

    s = sub.add_parser("thot-loop", help="Thread of Thought loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["segment", "analyze", "select", "synthesize"]
    )
    s.set_defaults(func=cmd_thot_loop)

    s = sub.add_parser("tprop-propose", help="Thought Propagation propose")
    add_store(s)
    s.add_argument("problem")
    s.set_defaults(func=cmd_tprop_propose)

    s = sub.add_parser("tprop-solve", help="Thought Propagation solve")
    add_store(s)
    s.add_argument("propose_id")
    s.set_defaults(func=cmd_tprop_solve)

    s = sub.add_parser("tprop-reuse", help="Thought Propagation reuse")
    add_store(s)
    s.add_argument("analog_id")
    s.set_defaults(func=cmd_tprop_reuse)

    s = sub.add_parser("tprop-amend", help="Thought Propagation amend")
    add_store(s)
    s.add_argument("reuse_id")
    s.set_defaults(func=cmd_tprop_amend)

    s = sub.add_parser("tprop-compat", help="Thought Propagation compat")
    add_store(s)
    s.add_argument("--plug-and-play", action="store_true")
    s.set_defaults(func=cmd_tprop_compat)

    s = sub.add_parser("tprop-loop", help="Thought Propagation loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["propose", "solve", "reuse", "amend"]
    )
    s.set_defaults(func=cmd_tprop_loop)

    s = sub.add_parser("s2a-regenerate", help="System 2 Attention regenerate")
    add_store(s)
    s.add_argument("context")
    s.set_defaults(func=cmd_s2a_regenerate)

    s = sub.add_parser("s2a-attend", help="System 2 Attention attend")
    add_store(s)
    s.add_argument("regen_id")
    s.set_defaults(func=cmd_s2a_attend)

    s = sub.add_parser("s2a-respond", help="System 2 Attention respond")
    add_store(s)
    s.add_argument("attend_id")
    s.set_defaults(func=cmd_s2a_respond)

    s = sub.add_parser("s2a-factuality", help="System 2 Attention factuality")
    add_store(s)
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_s2a_factuality)

    s = sub.add_parser("s2a-sycophancy", help="System 2 Attention sycophancy")
    add_store(s)
    s.add_argument("--reduced", action="store_true")
    s.set_defaults(func=cmd_s2a_sycophancy)

    s = sub.add_parser("s2a-loop", help="System 2 Attention loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["regenerate", "attend", "respond", "factuality"],
    )
    s.set_defaults(func=cmd_s2a_loop)

    s = sub.add_parser("ccot-valid", help="Contrastive CoT valid")
    add_store(s)
    s.add_argument("demo")
    s.set_defaults(func=cmd_ccot_valid)

    s = sub.add_parser("ccot-invalid", help="Contrastive CoT invalid")
    add_store(s)
    s.add_argument("demo")
    s.set_defaults(func=cmd_ccot_invalid)

    s = sub.add_parser("ccot-contrast", help="Contrastive CoT contrast")
    add_store(s)
    s.add_argument("valid_id")
    s.add_argument("invalid_id")
    s.set_defaults(func=cmd_ccot_contrast)

    s = sub.add_parser("ccot-reason", help="Contrastive CoT reason")
    add_store(s)
    s.add_argument("contrast_id")
    s.set_defaults(func=cmd_ccot_reason)

    s = sub.add_parser("ccot-auto", help="Contrastive CoT auto")
    add_store(s)
    s.add_argument("--construct", action="store_true")
    s.set_defaults(func=cmd_ccot_auto)

    s = sub.add_parser("ccot-loop", help="Contrastive CoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["valid", "invalid", "contrast", "reason"]
    )
    s.set_defaults(func=cmd_ccot_loop)

    s = sub.add_parser("tabcot-header", help="Tab-CoT header")
    add_store(s)
    s.add_argument("columns")
    s.set_defaults(func=cmd_tabcot_header)

    s = sub.add_parser("tabcot-row", help="Tab-CoT row")
    add_store(s)
    s.add_argument("header_id")
    s.add_argument("step", type=int)
    s.set_defaults(func=cmd_tabcot_row)

    s = sub.add_parser("tabcot-infer2d", help="Tab-CoT 2D infer")
    add_store(s)
    s.add_argument("rows", type=int)
    s.set_defaults(func=cmd_tabcot_infer2d)

    s = sub.add_parser("tabcot-extract", help="Tab-CoT extract")
    add_store(s)
    s.add_argument("row_id")
    s.set_defaults(func=cmd_tabcot_extract)

    s = sub.add_parser("tabcot-zeroshot", help="Tab-CoT zeroshot")
    add_store(s)
    s.add_argument("--zero-shot", action="store_true")
    s.set_defaults(func=cmd_tabcot_zeroshot)

    s = sub.add_parser("tabcot-loop", help="Tab-CoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["header", "row", "infer2d", "extract"]
    )
    s.set_defaults(func=cmd_tabcot_loop)

    s = sub.add_parser("xot-mcts", help="XoT MCTS")
    add_store(s)
    s.add_argument("problem")
    s.set_defaults(func=cmd_xot_mcts)

    s = sub.add_parser("xot-revise", help="XoT revise")
    add_store(s)
    s.add_argument("mcts_id")
    s.set_defaults(func=cmd_xot_revise)

    s = sub.add_parser("xot-map", help="XoT map")
    add_store(s)
    s.add_argument("revise_id")
    s.set_defaults(func=cmd_xot_map)

    s = sub.add_parser("xot-penrose", help="XoT penrose")
    add_store(s)
    s.add_argument("--defy", action="store_true")
    s.set_defaults(func=cmd_xot_penrose)

    s = sub.add_parser("xot-flexible", help="XoT flexible")
    add_store(s)
    s.add_argument("--multi-solution", action="store_true")
    s.set_defaults(func=cmd_xot_flexible)

    s = sub.add_parser("xot-loop", help="XoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["mcts", "revise", "map", "penrose"]
    )
    s.set_defaults(func=cmd_xot_loop)

    s = sub.add_parser("cove-draft", help="CoVe draft")
    add_store(s)
    s.add_argument("claim")
    s.set_defaults(func=cmd_cove_draft)

    s = sub.add_parser("cove-plan", help="CoVe plan")
    add_store(s)
    s.add_argument("draft_id")
    s.set_defaults(func=cmd_cove_plan)

    s = sub.add_parser("cove-answer", help="CoVe answer")
    add_store(s)
    s.add_argument("plan_id")
    s.set_defaults(func=cmd_cove_answer)

    s = sub.add_parser("cove-final", help="CoVe final")
    add_store(s)
    s.add_argument("verify_id")
    s.set_defaults(func=cmd_cove_final)

    s = sub.add_parser("cove-hallucination", help="CoVe hallucination")
    add_store(s)
    s.add_argument("--reduced", action="store_true")
    s.set_defaults(func=cmd_cove_hallucination)

    s = sub.add_parser("cove-loop", help="CoVe loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["draft", "plan", "answer", "final"]
    )
    s.set_defaults(func=cmd_cove_loop)

    s = sub.add_parser("ved-uncertain", help="Verify-and-Edit uncertain")
    add_store(s)
    s.add_argument("consistency", type=int)
    s.set_defaults(func=cmd_ved_uncertain)

    s = sub.add_parser("ved-search", help="Verify-and-Edit search")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_ved_search)

    s = sub.add_parser("ved-edit", help="Verify-and-Edit edit")
    add_store(s)
    s.add_argument("fact_id")
    s.add_argument("rationale")
    s.set_defaults(func=cmd_ved_edit)

    s = sub.add_parser("ved-predict", help="Verify-and-Edit predict")
    add_store(s)
    s.add_argument("edit_id")
    s.set_defaults(func=cmd_ved_predict)

    s = sub.add_parser("ved-knowledge", help="Verify-and-Edit knowledge")
    add_store(s)
    s.add_argument("--enhanced", action="store_true")
    s.set_defaults(func=cmd_ved_knowledge)

    s = sub.add_parser("ved-loop", help="Verify-and-Edit loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["uncertain", "search", "edit", "predict"]
    )
    s.set_defaults(func=cmd_ved_loop)

    s = sub.add_parser("sve-forward", help="Self-Verification forward")
    add_store(s)
    s.add_argument("problem")
    s.set_defaults(func=cmd_sve_forward)

    s = sub.add_parser("sve-mask", help="Self-Verification mask")
    add_store(s)
    s.add_argument("candidate_id")
    s.set_defaults(func=cmd_sve_mask)

    s = sub.add_parser("sve-repredict", help="Self-Verification repredict")
    add_store(s)
    s.add_argument("mask_id")
    s.set_defaults(func=cmd_sve_repredict)

    s = sub.add_parser("sve-score", help="Self-Verification score")
    add_store(s)
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_sve_score)

    s = sub.add_parser("sve-select", help="Self-Verification select")
    add_store(s)
    s.add_argument("--pick-best", action="store_true")
    s.set_defaults(func=cmd_sve_select)

    s = sub.add_parser("sve-loop", help="Self-Verification loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["forward", "mask", "repredict", "score"]
    )
    s.set_defaults(func=cmd_sve_loop)

    s = sub.add_parser("cod-sparse", help="Chain of Density sparse")
    add_store(s)
    s.add_argument("source")
    s.set_defaults(func=cmd_cod_sparse)

    s = sub.add_parser("cod-entities", help="Chain of Density entities")
    add_store(s)
    s.add_argument("sparse_id")
    s.add_argument("count", type=int)
    s.set_defaults(func=cmd_cod_entities)

    s = sub.add_parser("cod-fuse", help="Chain of Density fuse")
    add_store(s)
    s.add_argument("entity_id")
    s.set_defaults(func=cmd_cod_fuse)

    s = sub.add_parser("cod-length", help="Chain of Density length")
    add_store(s)
    s.add_argument("--fixed", action="store_true")
    s.set_defaults(func=cmd_cod_length)

    s = sub.add_parser("cod-tradeoff", help="Chain of Density tradeoff")
    add_store(s)
    s.add_argument("--prefer-dense", action="store_true")
    s.set_defaults(func=cmd_cod_tradeoff)

    s = sub.add_parser("cod-loop", help="Chain of Density loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["sparse", "entities", "fuse", "length"]
    )
    s.set_defaults(func=cmd_cod_loop)

    s = sub.add_parser("hsp-hint", help="HSP hint")
    add_store(s)
    s.add_argument("problem")
    s.set_defaults(func=cmd_hsp_hint)

    s = sub.add_parser("hsp-solve", help="HSP solve")
    add_store(s)
    s.add_argument("hint_id")
    s.set_defaults(func=cmd_hsp_solve)

    s = sub.add_parser("hsp-answer", help="HSP answer")
    add_store(s)
    s.add_argument("solve_id")
    s.set_defaults(func=cmd_hsp_answer)

    s = sub.add_parser("hsp-compose", help="HSP compose")
    add_store(s)
    s.add_argument("base", choices=["cot", "ltm", "ps", "standard"])
    s.set_defaults(func=cmd_hsp_compose)

    s = sub.add_parser("hsp-quality", help="HSP quality")
    add_store(s)
    s.add_argument("--high-quality", action="store_true")
    s.set_defaults(func=cmd_hsp_quality)

    s = sub.add_parser("hsp-loop", help="HSP loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["hint", "solve", "answer", "compose"]
    )
    s.set_defaults(func=cmd_hsp_loop)

    s = sub.add_parser("emo-stimulus", help="EmotionPrompt stimulus")
    add_store(s)
    s.add_argument("text")
    s.set_defaults(func=cmd_emo_stimulus)

    s = sub.add_parser("emo-append", help="EmotionPrompt append")
    add_store(s)
    s.add_argument("prompt")
    s.add_argument("stimulus_id")
    s.set_defaults(func=cmd_emo_append)

    s = sub.add_parser("emo-run", help="EmotionPrompt run")
    add_store(s)
    s.add_argument("prompt_id")
    s.set_defaults(func=cmd_emo_run)

    s = sub.add_parser("emo-truth", help="EmotionPrompt truth")
    add_store(s)
    s.add_argument("--improved", action="store_true")
    s.set_defaults(func=cmd_emo_truth)

    s = sub.add_parser("emo-psych", help="EmotionPrompt psych")
    add_store(s)
    s.add_argument("--psychology", action="store_true")
    s.set_defaults(func=cmd_emo_psych)

    s = sub.add_parser("emo-loop", help="EmotionPrompt loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["stimulus", "append", "run", "truth"]
    )
    s.set_defaults(func=cmd_emo_loop)

    s = sub.add_parser("ape-propose", help="APE propose")
    add_store(s)
    s.add_argument("demos")
    s.set_defaults(func=cmd_ape_propose)

    s = sub.add_parser("ape-score", help="APE score")
    add_store(s)
    s.add_argument("pool_id")
    s.set_defaults(func=cmd_ape_score)

    s = sub.add_parser("ape-select", help="APE select")
    add_store(s)
    s.add_argument("score_id")
    s.set_defaults(func=cmd_ape_select)

    s = sub.add_parser("ape-steer", help="APE steer")
    add_store(s)
    s.add_argument("instr_id")
    s.set_defaults(func=cmd_ape_steer)

    s = sub.add_parser("ape-human", help="APE human parity")
    add_store(s)
    s.add_argument("--match-human", action="store_true")
    s.set_defaults(func=cmd_ape_human)

    s = sub.add_parser("ape-loop", help="APE loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["propose", "score", "select", "steer"]
    )
    s.set_defaults(func=cmd_ape_loop)

    s = sub.add_parser("pbr-init", help="Promptbreeder init")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_pbr_init)

    s = sub.add_parser("pbr-mutate", help="Promptbreeder mutate")
    add_store(s)
    s.add_argument("pop_id")
    s.set_defaults(func=cmd_pbr_mutate)

    s = sub.add_parser("pbr-fitness", help="Promptbreeder fitness")
    add_store(s)
    s.add_argument("mut_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_pbr_fitness)

    s = sub.add_parser("pbr-diversity", help="Promptbreeder diversity")
    add_store(s)
    s.add_argument("--maintain", action="store_true")
    s.set_defaults(func=cmd_pbr_diversity)

    s = sub.add_parser("pbr-selfref", help="Promptbreeder selfref")
    add_store(s)
    s.add_argument("--self-improve", action="store_true")
    s.set_defaults(func=cmd_pbr_selfref)

    s = sub.add_parser("pbr-loop", help="Promptbreeder loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["init", "mutate", "fitness", "diversity"]
    )
    s.set_defaults(func=cmd_pbr_loop)

    s = sub.add_parser("opro-meta", help="OPRO meta")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_opro_meta)

    s = sub.add_parser("opro-propose", help="OPRO propose")
    add_store(s)
    s.add_argument("meta_id")
    s.set_defaults(func=cmd_opro_propose)

    s = sub.add_parser("opro-score", help="OPRO score")
    add_store(s)
    s.add_argument("cand_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_opro_score)

    s = sub.add_parser("opro-append", help="OPRO append")
    add_store(s)
    s.add_argument("score_id")
    s.set_defaults(func=cmd_opro_append)

    s = sub.add_parser("opro-best", help="OPRO best vs human")
    add_store(s)
    s.add_argument("--beat-human", action="store_true")
    s.set_defaults(func=cmd_opro_best)

    s = sub.add_parser("opro-loop", help="OPRO loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["meta", "propose", "score", "append"]
    )
    s.set_defaults(func=cmd_opro_loop)

    s = sub.add_parser("evp-init", help="EvoPrompt init")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_evp_init)

    s = sub.add_parser("evp-cross", help="EvoPrompt crossover")
    add_store(s)
    s.add_argument("pop_id")
    s.set_defaults(func=cmd_evp_cross)

    s = sub.add_parser("evp-mutate", help="EvoPrompt mutate")
    add_store(s)
    s.add_argument("cross_id")
    s.set_defaults(func=cmd_evp_mutate)

    s = sub.add_parser("evp-select", help="EvoPrompt select")
    add_store(s)
    s.add_argument("mut_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_evp_select)

    s = sub.add_parser("evp-ea", help="EvoPrompt EA connect")
    add_store(s)
    s.add_argument("--connect-ea", action="store_true")
    s.set_defaults(func=cmd_evp_ea)

    s = sub.add_parser("evp-loop", help="EvoPrompt loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["init", "cross", "mutate", "select"]
    )
    s.set_defaults(func=cmd_evp_loop)

    s = sub.add_parser("ptg-gradient", help="ProTeGi gradient")
    add_store(s)
    s.add_argument("prompt")
    s.set_defaults(func=cmd_ptg_gradient)

    s = sub.add_parser("ptg-edit", help="ProTeGi edit")
    add_store(s)
    s.add_argument("grad_id")
    s.set_defaults(func=cmd_ptg_edit)

    s = sub.add_parser("ptg-beam", help="ProTeGi beam")
    add_store(s)
    s.add_argument("edit_id")
    s.set_defaults(func=cmd_ptg_beam)

    s = sub.add_parser("ptg-bandit", help="ProTeGi bandit")
    add_store(s)
    s.add_argument("beam_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ptg_bandit)

    s = sub.add_parser("ptg-jailbreak", help="ProTeGi jailbreak flag")
    add_store(s)
    s.add_argument("--detect", action="store_true")
    s.set_defaults(func=cmd_ptg_jailbreak)

    s = sub.add_parser("ptg-loop", help="ProTeGi loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["gradient", "edit", "beam", "bandit"]
    )
    s.set_defaults(func=cmd_ptg_loop)

    s = sub.add_parser("pag-state", help="PromptAgent state")
    add_store(s)
    s.add_argument("prompt")
    s.set_defaults(func=cmd_pag_state)

    s = sub.add_parser("pag-reflect", help="PromptAgent reflect")
    add_store(s)
    s.add_argument("state_id")
    s.set_defaults(func=cmd_pag_reflect)

    s = sub.add_parser("pag-expand", help="PromptAgent expand")
    add_store(s)
    s.add_argument("reflect_id")
    s.set_defaults(func=cmd_pag_expand)

    s = sub.add_parser("pag-backprop", help="PromptAgent backprop")
    add_store(s)
    s.add_argument("expand_id")
    s.add_argument("reward", type=int)
    s.set_defaults(func=cmd_pag_backprop)

    s = sub.add_parser("pag-expert", help="PromptAgent expert flag")
    add_store(s)
    s.add_argument("--expert-level", action="store_true")
    s.set_defaults(func=cmd_pag_expert)

    s = sub.add_parser("pag-loop", help="PromptAgent loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["state", "reflect", "expand", "backprop"]
    )
    s.set_defaults(func=cmd_pag_loop)

    s = sub.add_parser("mapo-posgrad", help="MAPO positive gradient")
    add_store(s)
    s.add_argument("prompt")
    s.set_defaults(func=cmd_mapo_posgrad)

    s = sub.add_parser("mapo-momentum", help="MAPO momentum")
    add_store(s)
    s.add_argument("pos_id")
    s.set_defaults(func=cmd_mapo_momentum)

    s = sub.add_parser("mapo-beam", help="MAPO beam")
    add_store(s)
    s.add_argument("mom_id")
    s.set_defaults(func=cmd_mapo_beam)

    s = sub.add_parser("mapo-ucb", help="MAPO UCB")
    add_store(s)
    s.add_argument("beam_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mapo_ucb)

    s = sub.add_parser("mapo-faster", help="MAPO vs ProTeGi flag")
    add_store(s)
    s.add_argument("--beat-protegi", action="store_true")
    s.set_defaults(func=cmd_mapo_faster)

    s = sub.add_parser("mapo-loop", help="MAPO loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["posgrad", "momentum", "beam", "ucb"]
    )
    s.set_defaults(func=cmd_mapo_loop)

    s = sub.add_parser("grips-seed", help="GrIPS seed")
    add_store(s)
    s.add_argument("instruction")
    s.set_defaults(func=cmd_grips_seed)

    s = sub.add_parser("grips-edit", help="GrIPS edit")
    add_store(s)
    s.add_argument("seed_id")
    s.add_argument(
        "op", choices=["add", "paraphrase", "swap", "delete"]
    )
    s.set_defaults(func=cmd_grips_edit)

    s = sub.add_parser("grips-score", help="GrIPS score")
    add_store(s)
    s.add_argument("edit_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_grips_score)

    s = sub.add_parser("grips-accept", help="GrIPS accept")
    add_store(s)
    s.add_argument("score_id")
    s.set_defaults(func=cmd_grips_accept)

    s = sub.add_parser("grips-api", help="GrIPS API-tunable flag")
    add_store(s)
    s.add_argument("--api-tunable", action="store_true")
    s.set_defaults(func=cmd_grips_api)

    s = sub.add_parser("grips-loop", help="GrIPS loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["seed", "edit", "score", "accept"]
    )
    s.set_defaults(func=cmd_grips_loop)

    s = sub.add_parser("tmpa-state", help="TEMPERA state")
    add_store(s)
    s.add_argument("prompt")
    s.add_argument("query")
    s.set_defaults(func=cmd_tmpa_state)

    s = sub.add_parser("tmpa-act", help="TEMPERA act")
    add_store(s)
    s.add_argument("state_id")
    s.add_argument(
        "component",
        choices=["instruction", "exemplar", "verbalizer"],
    )
    s.set_defaults(func=cmd_tmpa_act)

    s = sub.add_parser("tmpa-reward", help="TEMPERA reward")
    add_store(s)
    s.add_argument("act_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_tmpa_reward)

    s = sub.add_parser("tmpa-adapt", help="TEMPERA adapt")
    add_store(s)
    s.add_argument("reward_id")
    s.set_defaults(func=cmd_tmpa_adapt)

    s = sub.add_parser("tmpa-efficiency", help="TEMPERA efficiency")
    add_store(s)
    s.add_argument("--sample-efficient", action="store_true")
    s.set_defaults(func=cmd_tmpa_efficiency)

    s = sub.add_parser("tmpa-loop", help="TEMPERA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["state", "act", "reward", "adapt"]
    )
    s.set_defaults(func=cmd_tmpa_loop)

    s = sub.add_parser("rlp-init", help="RLPrompt init")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_rlp_init)

    s = sub.add_parser("rlp-sample", help="RLPrompt sample")
    add_store(s)
    s.add_argument("policy_id")
    s.set_defaults(func=cmd_rlp_sample)

    s = sub.add_parser("rlp-reward", help="RLPrompt reward")
    add_store(s)
    s.add_argument("sample_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_rlp_reward)

    s = sub.add_parser("rlp-update", help="RLPrompt update")
    add_store(s)
    s.add_argument("reward_id")
    s.set_defaults(func=cmd_rlp_update)

    s = sub.add_parser("rlp-discrete", help="RLPrompt discrete flag")
    add_store(s)
    s.add_argument("--discrete", action="store_true")
    s.set_defaults(func=cmd_rlp_discrete)

    s = sub.add_parser("rlp-loop", help="RLPrompt loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["init", "sample", "reward", "update"]
    )
    s.set_defaults(func=cmd_rlp_loop)

    s = sub.add_parser("aup-template", help="AutoPrompt template")
    add_store(s)
    s.add_argument("template")
    s.set_defaults(func=cmd_aup_template)

    s = sub.add_parser("aup-trigger", help="AutoPrompt trigger")
    add_store(s)
    s.add_argument("tmpl_id")
    s.set_defaults(func=cmd_aup_trigger)

    s = sub.add_parser("aup-search", help="AutoPrompt search")
    add_store(s)
    s.add_argument("trig_id")
    s.set_defaults(func=cmd_aup_search)

    s = sub.add_parser("aup-score", help="AutoPrompt score")
    add_store(s)
    s.add_argument("search_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_aup_score)

    s = sub.add_parser("aup-probe", help="AutoPrompt probe flag")
    add_store(s)
    s.add_argument("--parameter-free", action="store_true")
    s.set_defaults(func=cmd_aup_probe)

    s = sub.add_parser("aup-loop", help="AutoPrompt loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["template", "trigger", "search", "score"]
    )
    s.set_defaults(func=cmd_aup_loop)

    s = sub.add_parser("pfx-task", help="Prefix-Tuning task")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_pfx_task)

    s = sub.add_parser("pfx-prefix", help="Prefix-Tuning prefix")
    add_store(s)
    s.add_argument("task_id")
    s.set_defaults(func=cmd_pfx_prefix)

    s = sub.add_parser("pfx-optimize", help="Prefix-Tuning optimize")
    add_store(s)
    s.add_argument("prefix_id")
    s.set_defaults(func=cmd_pfx_optimize)

    s = sub.add_parser("pfx-generate", help="Prefix-Tuning generate")
    add_store(s)
    s.add_argument("opt_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_pfx_generate)

    s = sub.add_parser("pfx-freeze", help="Prefix-Tuning freeze flag")
    add_store(s)
    s.add_argument("--freeze-lm", action="store_true")
    s.set_defaults(func=cmd_pfx_freeze)

    s = sub.add_parser("pfx-loop", help="Prefix-Tuning loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["task", "prefix", "optimize", "generate"]
    )
    s.set_defaults(func=cmd_pfx_loop)

    s = sub.add_parser("ptv-deep", help="P-Tuning v2 deep")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_ptv_deep)

    s = sub.add_parser("ptv-inject", help="P-Tuning v2 inject")
    add_store(s)
    s.add_argument("deep_id")
    s.set_defaults(func=cmd_ptv_inject)

    s = sub.add_parser("ptv-tune", help="P-Tuning v2 tune")
    add_store(s)
    s.add_argument("inj_id")
    s.set_defaults(func=cmd_ptv_tune)

    s = sub.add_parser("ptv-seqtag", help="P-Tuning v2 seqtag")
    add_store(s)
    s.add_argument("tune_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ptv_seqtag)

    s = sub.add_parser("ptv-universal", help="P-Tuning v2 universal")
    add_store(s)
    s.add_argument("--match-finetune", action="store_true")
    s.set_defaults(func=cmd_ptv_universal)

    s = sub.add_parser("ptv-loop", help="P-Tuning v2 loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["deep", "inject", "tune", "seqtag"]
    )
    s.set_defaults(func=cmd_ptv_loop)

    s = sub.add_parser("ptl-soft", help="Prompt Tuning soft")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_ptl_soft)

    s = sub.add_parser("ptl-prepend", help="Prompt Tuning prepend")
    add_store(s)
    s.add_argument("soft_id")
    s.set_defaults(func=cmd_ptl_prepend)

    s = sub.add_parser("ptl-optimize", help="Prompt Tuning optimize")
    add_store(s)
    s.add_argument("prep_id")
    s.set_defaults(func=cmd_ptl_optimize)

    s = sub.add_parser("ptl-scale", help="Prompt Tuning scale")
    add_store(s)
    s.add_argument("opt_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ptl_scale)

    s = sub.add_parser("ptl-input-only", help="Prompt Tuning input-only")
    add_store(s)
    s.add_argument("--input-layer-only", action="store_true")
    s.set_defaults(func=cmd_ptl_input_only)

    s = sub.add_parser("ptl-loop", help="Prompt Tuning loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["soft", "prepend", "optimize", "scale"]
    )
    s.set_defaults(func=cmd_ptl_loop)

    s = sub.add_parser("msp-soft", help="Soft Prompt Mixtures soft")
    add_store(s)
    s.add_argument("query")
    s.set_defaults(func=cmd_msp_soft)

    s = sub.add_parser("msp-mix", help="Soft Prompt Mixtures mix")
    add_store(s)
    s.add_argument("soft_id")
    s.set_defaults(func=cmd_msp_mix)

    s = sub.add_parser("msp-ensemble", help="Soft Prompt Mixtures ensemble")
    add_store(s)
    s.add_argument("mix_id")
    s.set_defaults(func=cmd_msp_ensemble)

    s = sub.add_parser("msp-probe", help="Soft Prompt Mixtures probe")
    add_store(s)
    s.add_argument("ens_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_msp_probe)

    s = sub.add_parser("msp-underest", help="Soft Prompt Mixtures underest")
    add_store(s)
    s.add_argument("--prior-underestimate", action="store_true")
    s.set_defaults(func=cmd_msp_underest)

    s = sub.add_parser("msp-loop", help="Soft Prompt Mixtures loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["soft", "mix", "ensemble", "probe"]
    )
    s.set_defaults(func=cmd_msp_loop)

    s = sub.add_parser("spot-source", help="SPoT source")
    add_store(s)
    s.add_argument("source_task")
    s.set_defaults(func=cmd_spot_source)

    s = sub.add_parser("spot-init", help="SPoT init")
    add_store(s)
    s.add_argument("src_id")
    s.add_argument("target_task")
    s.set_defaults(func=cmd_spot_init)

    s = sub.add_parser("spot-embed", help="SPoT embed")
    add_store(s)
    s.add_argument("src_id")
    s.set_defaults(func=cmd_spot_embed)

    s = sub.add_parser("spot-retrieve", help="SPoT retrieve")
    add_store(s)
    s.add_argument("emb_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_spot_retrieve)

    s = sub.add_parser("spot-vs-tune", help="SPoT vs model-tuning")
    add_store(s)
    s.add_argument("--beat-model-tuning", action="store_true")
    s.set_defaults(func=cmd_spot_vs_tune)

    s = sub.add_parser("spot-loop", help="SPoT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["source", "init", "embed", "retrieve"]
    )
    s.set_defaults(func=cmd_spot_loop)

    s = sub.add_parser("atm-source", help="ATTEMPT source")
    add_store(s)
    s.add_argument("source_task")
    s.set_defaults(func=cmd_atm_source)

    s = sub.add_parser("atm-target", help="ATTEMPT target")
    add_store(s)
    s.add_argument("target_task")
    s.set_defaults(func=cmd_atm_target)

    s = sub.add_parser("atm-attend", help="ATTEMPT attend")
    add_store(s)
    s.add_argument("src_id")
    s.add_argument("tgt_id")
    s.set_defaults(func=cmd_atm_attend)

    s = sub.add_parser("atm-mix", help="ATTEMPT mix")
    add_store(s)
    s.add_argument("attn_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_atm_mix)

    s = sub.add_parser("atm-modular", help="ATTEMPT modular flag")
    add_store(s)
    s.add_argument("--modular", action="store_true")
    s.set_defaults(func=cmd_atm_modular)

    s = sub.add_parser("atm-loop", help="ATTEMPT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["source", "target", "attend", "mix"]
    )
    s.set_defaults(func=cmd_atm_loop)

    s = sub.add_parser("mptp-shared", help="MPT shared")
    add_store(s)
    s.add_argument("corpus")
    s.set_defaults(func=cmd_mptp_shared)

    s = sub.add_parser("mptp-factor", help="MPT factor")
    add_store(s)
    s.add_argument("shared_id")
    s.add_argument("task")
    s.set_defaults(func=cmd_mptp_factor)

    s = sub.add_parser("mptp-transfer", help="MPT transfer")
    add_store(s)
    s.add_argument("factor_id")
    s.set_defaults(func=cmd_mptp_transfer)

    s = sub.add_parser("mptp-score", help="MPT score")
    add_store(s)
    s.add_argument("xfer_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mptp_score)

    s = sub.add_parser("mptp-efficient", help="MPT efficiency flag")
    add_store(s)
    s.add_argument("--param-efficient", action="store_true")
    s.set_defaults(func=cmd_mptp_efficient)

    s = sub.add_parser("mptp-loop", help="MPT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["shared", "factor", "transfer", "score"]
    )
    s.set_defaults(func=cmd_mptp_loop)

    s = sub.add_parser("lora-freeze", help="LoRA freeze flag")
    add_store(s)
    s.add_argument("--base-frozen", action="store_true")
    s.set_defaults(func=cmd_lora_freeze)

    s = sub.add_parser("lora-rank", help="LoRA rank")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lora_rank)

    s = sub.add_parser("lora-train", help="LoRA train")
    add_store(s)
    s.add_argument("rank_id")
    s.set_defaults(func=cmd_lora_train)

    s = sub.add_parser("lora-merge", help="LoRA merge")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lora_merge)

    s = sub.add_parser("lora-latency", help="LoRA latency flag")
    add_store(s)
    s.add_argument("--zero-extra", action="store_true")
    s.set_defaults(func=cmd_lora_latency)

    s = sub.add_parser("lora-loop", help="LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["freeze", "rank", "train", "merge"]
    )
    s.set_defaults(func=cmd_lora_loop)

    s = sub.add_parser("adf-extract", help="AdapterFusion extract")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_adf_extract)

    s = sub.add_parser("adf-compose", help="AdapterFusion compose")
    add_store(s)
    s.add_argument("adapter_id")
    s.set_defaults(func=cmd_adf_compose)

    s = sub.add_parser("adf-attend", help="AdapterFusion attend")
    add_store(s)
    s.add_argument("compose_id")
    s.set_defaults(func=cmd_adf_attend)

    s = sub.add_parser("adf-score", help="AdapterFusion score")
    add_store(s)
    s.add_argument("fusion_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_adf_score)

    s = sub.add_parser("adf-nondestruct", help="AdapterFusion nondestructive")
    add_store(s)
    s.add_argument("--nondestructive", action="store_true")
    s.set_defaults(func=cmd_adf_nondestruct)

    s = sub.add_parser("adf-loop", help="AdapterFusion loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["extract", "compose", "attend", "score"]
    )
    s.set_defaults(func=cmd_adf_loop)

    s = sub.add_parser("cmp-insert", help="Compacter insert")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_cmp_insert)

    s = sub.add_parser("cmp-kronecker", help="Compacter kronecker")
    add_store(s)
    s.add_argument("adapter_id")
    s.add_argument("n", type=int)
    s.set_defaults(func=cmd_cmp_kronecker)

    s = sub.add_parser("cmp-train", help="Compacter train")
    add_store(s)
    s.add_argument("kron_id")
    s.set_defaults(func=cmd_cmp_train)

    s = sub.add_parser("cmp-score", help="Compacter score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_cmp_score)

    s = sub.add_parser("cmp-compact", help="Compacter efficiency flag")
    add_store(s)
    s.add_argument("--param-efficient", action="store_true")
    s.set_defaults(func=cmd_cmp_compact)

    s = sub.add_parser("cmp-loop", help="Compacter loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["insert", "kronecker", "train", "score"]
    )
    s.set_defaults(func=cmd_cmp_loop)

    s = sub.add_parser("ia3-vector", help="(IA)^3 vector")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_ia3_vector)

    s = sub.add_parser("ia3-scale", help="(IA)^3 scale")
    add_store(s)
    s.add_argument("vector_id")
    s.set_defaults(func=cmd_ia3_scale)

    s = sub.add_parser("ia3-train", help="(IA)^3 train")
    add_store(s)
    s.add_argument("scale_id")
    s.set_defaults(func=cmd_ia3_train)

    s = sub.add_parser("ia3-score", help="(IA)^3 score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ia3_score)

    s = sub.add_parser("ia3-mixed", help="(IA)^3 mixed-batch flag")
    add_store(s)
    s.add_argument("--mixed-batch", action="store_true")
    s.set_defaults(func=cmd_ia3_mixed)

    s = sub.add_parser("ia3-loop", help="(IA)^3 loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["vector", "scale", "train", "score"]
    )
    s.set_defaults(func=cmd_ia3_loop)

    s = sub.add_parser("bft-freeze", help="BitFit freeze flag")
    add_store(s)
    s.add_argument("--weights-frozen", action="store_true")
    s.set_defaults(func=cmd_bft_freeze)

    s = sub.add_parser("bft-bias", help="BitFit bias")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_bft_bias)

    s = sub.add_parser("bft-train", help="BitFit train")
    add_store(s)
    s.add_argument("bias_id")
    s.set_defaults(func=cmd_bft_train)

    s = sub.add_parser("bft-score", help="BitFit score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_bft_score)

    s = sub.add_parser("bft-tiny", help="BitFit tiny-fraction flag")
    add_store(s)
    s.add_argument("fraction_pct", type=int)
    s.set_defaults(func=cmd_bft_tiny)

    s = sub.add_parser("bft-loop", help="BitFit loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["freeze", "bias", "train", "score"]
    )
    s.set_defaults(func=cmd_bft_loop)

    s = sub.add_parser("dora-decompose", help="DoRA decompose")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_dora_decompose)

    s = sub.add_parser("dora-magnitude", help="DoRA magnitude")
    add_store(s)
    s.add_argument("decomp_id")
    s.set_defaults(func=cmd_dora_magnitude)

    s = sub.add_parser("dora-direction", help="DoRA direction")
    add_store(s)
    s.add_argument("mag_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_dora_direction)

    s = sub.add_parser("dora-score", help="DoRA score")
    add_store(s)
    s.add_argument("dir_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_dora_score)

    s = sub.add_parser("dora-vs-lora", help="DoRA vs LoRA flag")
    add_store(s)
    s.add_argument("--closes-gap", action="store_true")
    s.set_defaults(func=cmd_dora_vs_lora)

    s = sub.add_parser("dora-loop", help="DoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase",
        choices=["decompose", "magnitude", "direction", "score"],
    )
    s.set_defaults(func=cmd_dora_loop)

    s = sub.add_parser("qlo-quantize", help="QLoRA quantize")
    add_store(s)
    s.add_argument("bits", type=int)
    s.set_defaults(func=cmd_qlo_quantize)

    s = sub.add_parser("qlo-nf4", help="QLoRA NF4")
    add_store(s)
    s.add_argument("quant_id")
    s.set_defaults(func=cmd_qlo_nf4)

    s = sub.add_parser("qlo-adapter", help="QLoRA adapter")
    add_store(s)
    s.add_argument("nf4_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_qlo_adapter)

    s = sub.add_parser("qlo-score", help="QLoRA score")
    add_store(s)
    s.add_argument("adapter_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_qlo_score)

    s = sub.add_parser("qlo-memory", help="QLoRA memory flag")
    add_store(s)
    s.add_argument("--double-quant", action="store_true")
    s.set_defaults(func=cmd_qlo_memory)

    s = sub.add_parser("qlo-loop", help="QLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["quantize", "nf4", "adapter", "score"]
    )
    s.set_defaults(func=cmd_qlo_loop)

    s = sub.add_parser("adl-init", help="AdaLoRA init")
    add_store(s)
    s.add_argument("task")
    s.add_argument("budget", type=int)
    s.set_defaults(func=cmd_adl_init)

    s = sub.add_parser("adl-svd", help="AdaLoRA SVD")
    add_store(s)
    s.add_argument("init_id")
    s.set_defaults(func=cmd_adl_svd)

    s = sub.add_parser("adl-prune", help="AdaLoRA prune")
    add_store(s)
    s.add_argument("svd_id")
    s.add_argument("keep", type=int)
    s.set_defaults(func=cmd_adl_prune)

    s = sub.add_parser("adl-score", help="AdaLoRA score")
    add_store(s)
    s.add_argument("prune_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_adl_score)

    s = sub.add_parser("adl-adaptive", help="AdaLoRA adaptive-rank flag")
    add_store(s)
    s.add_argument("--adaptive-rank", action="store_true")
    s.set_defaults(func=cmd_adl_adaptive)

    s = sub.add_parser("adl-loop", help="AdaLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["init", "svd", "prune", "score"]
    )
    s.set_defaults(func=cmd_adl_loop)

    s = sub.add_parser("vra-share", help="VeRA share")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_vra_share)

    s = sub.add_parser("vra-scale", help="VeRA scale")
    add_store(s)
    s.add_argument("share_id")
    s.set_defaults(func=cmd_vra_scale)

    s = sub.add_parser("vra-train", help="VeRA train")
    add_store(s)
    s.add_argument("scale_id")
    s.set_defaults(func=cmd_vra_train)

    s = sub.add_parser("vra-score", help="VeRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_vra_score)

    s = sub.add_parser("vra-tiny", help="VeRA tiny flag")
    add_store(s)
    s.add_argument("--vector-only", action="store_true")
    s.set_defaults(func=cmd_vra_tiny)

    s = sub.add_parser("vra-loop", help="VeRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["share", "scale", "train", "score"]
    )
    s.set_defaults(func=cmd_vra_loop)

    s = sub.add_parser("adp-insert", help="AdapterDrop insert")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_adp_insert)

    s = sub.add_parser("adp-drop", help="AdapterDrop drop")
    add_store(s)
    s.add_argument("adapter_id")
    s.add_argument("lower_layers", type=int)
    s.set_defaults(func=cmd_adp_drop)

    s = sub.add_parser("adp-infer", help="AdapterDrop infer")
    add_store(s)
    s.add_argument("drop_id")
    s.set_defaults(func=cmd_adp_infer)

    s = sub.add_parser("adp-score", help="AdapterDrop score")
    add_store(s)
    s.add_argument("infer_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_adp_score)

    s = sub.add_parser("adp-efficient", help="AdapterDrop efficiency flag")
    add_store(s)
    s.add_argument("--multi-task", action="store_true")
    s.set_defaults(func=cmd_adp_efficient)

    s = sub.add_parser("adp-loop", help="AdapterDrop loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["insert", "drop", "infer", "score"]
    )
    s.set_defaults(func=cmd_adp_loop)

    s = sub.add_parser("psa-svd", help="PiSSA SVD")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_psa_svd)

    s = sub.add_parser("psa-principal", help="PiSSA principal")
    add_store(s)
    s.add_argument("svd_id")
    s.set_defaults(func=cmd_psa_principal)

    s = sub.add_parser("psa-residual", help="PiSSA residual")
    add_store(s)
    s.add_argument("principal_id")
    s.set_defaults(func=cmd_psa_residual)

    s = sub.add_parser("psa-score", help="PiSSA score")
    add_store(s)
    s.add_argument("residual_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_psa_score)

    s = sub.add_parser("psa-fast", help="PiSSA fast-convergence flag")
    add_store(s)
    s.add_argument("--faster-than-lora", action="store_true")
    s.set_defaults(func=cmd_psa_fast)

    s = sub.add_parser("psa-loop", help="PiSSA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["svd", "principal", "residual", "score"]
    )
    s.set_defaults(func=cmd_psa_loop)

    s = sub.add_parser("dpr-diff", help="Diff Pruning diff")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_dpr_diff)

    s = sub.add_parser("dpr-mask", help="Diff Pruning mask")
    add_store(s)
    s.add_argument("diff_id")
    s.set_defaults(func=cmd_dpr_mask)

    s = sub.add_parser("dpr-prune", help="Diff Pruning prune")
    add_store(s)
    s.add_argument("mask_id")
    s.add_argument("sparsity_pct", type=int)
    s.set_defaults(func=cmd_dpr_prune)

    s = sub.add_parser("dpr-score", help="Diff Pruning score")
    add_store(s)
    s.add_argument("prune_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_dpr_score)

    s = sub.add_parser("dpr-sparse", help="Diff Pruning sparse flag")
    add_store(s)
    s.add_argument("--no-new-params", action="store_true")
    s.set_defaults(func=cmd_dpr_sparse)

    s = sub.add_parser("dpr-loop", help="Diff Pruning loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["diff", "mask", "prune", "score"]
    )
    s.set_defaults(func=cmd_dpr_loop)

    s = sub.add_parser("tlo-base", help="Tied-LoRA base")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_tlo_base)

    s = sub.add_parser("tlo-tie", help="Tied-LoRA tie")
    add_store(s)
    s.add_argument("base_id")
    s.add_argument("layers", type=int)
    s.set_defaults(func=cmd_tlo_tie)

    s = sub.add_parser("tlo-train", help="Tied-LoRA train")
    add_store(s)
    s.add_argument("tie_id")
    s.set_defaults(func=cmd_tlo_train)

    s = sub.add_parser("tlo-score", help="Tied-LoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_tlo_score)

    s = sub.add_parser("tlo-efficient", help="Tied-LoRA efficiency flag")
    add_store(s)
    s.add_argument("--weight-tied", action="store_true")
    s.set_defaults(func=cmd_tlo_efficient)

    s = sub.add_parser("tlo-loop", help="Tied-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["base", "tie", "train", "score"]
    )
    s.set_defaults(func=cmd_tlo_loop)

    s = sub.add_parser("lrp-split", help="LoRA+ split")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_lrp_split)

    s = sub.add_parser("lrp-ratio", help="LoRA+ ratio")
    add_store(s)
    s.add_argument("split_id")
    s.add_argument("lambda_ratio", type=int)
    s.set_defaults(func=cmd_lrp_ratio)

    s = sub.add_parser("lrp-train", help="LoRA+ train")
    add_store(s)
    s.add_argument("ratio_id")
    s.set_defaults(func=cmd_lrp_train)

    s = sub.add_parser("lrp-score", help="LoRA+ score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lrp_score)

    s = sub.add_parser("lrp-speed", help="LoRA+ speed flag")
    add_store(s)
    s.add_argument("--faster-than-lora", action="store_true")
    s.set_defaults(func=cmd_lrp_speed)

    s = sub.add_parser("lrp-loop", help="LoRA+ loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["split", "ratio", "train", "score"]
    )
    s.set_defaults(func=cmd_lrp_loop)

    s = sub.add_parser("lfa-freeze-a", help="LoRA-FA freeze A")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lfa_freeze_a)

    s = sub.add_parser("lfa-train-b", help="LoRA-FA train B")
    add_store(s)
    s.add_argument("a_id")
    s.set_defaults(func=cmd_lfa_train_b)

    s = sub.add_parser("lfa-merge", help="LoRA-FA merge")
    add_store(s)
    s.add_argument("train_id")
    s.set_defaults(func=cmd_lfa_merge)

    s = sub.add_parser("lfa-score", help="LoRA-FA score")
    add_store(s)
    s.add_argument("merge_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lfa_score)

    s = sub.add_parser("lfa-memory", help="LoRA-FA memory flag")
    add_store(s)
    s.add_argument("--activation-saved", action="store_true")
    s.set_defaults(func=cmd_lfa_memory)

    s = sub.add_parser("lfa-loop", help="LoRA-FA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["freeze_a", "train_b", "merge", "score"]
    )
    s.set_defaults(func=cmd_lfa_loop)

    s = sub.add_parser("dyl-range", help="DyLoRA range")
    add_store(s)
    s.add_argument("task")
    s.add_argument("r_min", type=int)
    s.add_argument("r_max", type=int)
    s.set_defaults(func=cmd_dyl_range)

    s = sub.add_parser("dyl-sample", help="DyLoRA sample")
    add_store(s)
    s.add_argument("range_id")
    s.set_defaults(func=cmd_dyl_sample)

    s = sub.add_parser("dyl-select", help="DyLoRA select")
    add_store(s)
    s.add_argument("sample_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_dyl_select)

    s = sub.add_parser("dyl-score", help="DyLoRA score")
    add_store(s)
    s.add_argument("select_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_dyl_score)

    s = sub.add_parser("dyl-searchfree", help="DyLoRA search-free flag")
    add_store(s)
    s.add_argument("--search-free", action="store_true")
    s.set_defaults(func=cmd_dyl_searchfree)

    s = sub.add_parser("dyl-loop", help="DyLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["range", "sample", "select", "score"]
    )
    s.set_defaults(func=cmd_dyl_loop)

    s = sub.add_parser("lxs-svd", help="LoRA-XS SVD")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lxs_svd)

    s = sub.add_parser("lxs-r", help="LoRA-XS R")
    add_store(s)
    s.add_argument("svd_id")
    s.set_defaults(func=cmd_lxs_r)

    s = sub.add_parser("lxs-train", help="LoRA-XS train")
    add_store(s)
    s.add_argument("r_id")
    s.set_defaults(func=cmd_lxs_train)

    s = sub.add_parser("lxs-score", help="LoRA-XS score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lxs_score)

    s = sub.add_parser("lxs-tiny", help="LoRA-XS tiny flag")
    add_store(s)
    s.add_argument("--r-squared-only", action="store_true")
    s.set_defaults(func=cmd_lxs_tiny)

    s = sub.add_parser("lxs-loop", help="LoRA-XS loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["svd", "r", "train", "score"]
    )
    s.set_defaults(func=cmd_lxs_loop)

    s = sub.add_parser("asy-role", help="AsymmetryLoRA role")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_asy_role)

    s = sub.add_parser("asy-freeze-a", help="AsymmetryLoRA freeze A")
    add_store(s)
    s.add_argument("role_id")
    s.set_defaults(func=cmd_asy_freeze_a)

    s = sub.add_parser("asy-train-b", help="AsymmetryLoRA train B")
    add_store(s)
    s.add_argument("a_id")
    s.set_defaults(func=cmd_asy_train_b)

    s = sub.add_parser("asy-score", help="AsymmetryLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_asy_score)

    s = sub.add_parser("asy-bound", help="AsymmetryLoRA bound flag")
    add_store(s)
    s.add_argument("--tighter-bound", action="store_true")
    s.set_defaults(func=cmd_asy_bound)

    s = sub.add_parser("asy-loop", help="AsymmetryLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["role", "freeze_a", "train_b", "score"]
    )
    s.set_defaults(func=cmd_asy_loop)

    s = sub.add_parser("lga-grad", help="LoRA-GA grad")
    add_store(s)
    s.add_argument("task")
    s.add_argument("samples", type=int)
    s.set_defaults(func=cmd_lga_grad)

    s = sub.add_parser("lga-svd", help="LoRA-GA svd")
    add_store(s)
    s.add_argument("grad_id")
    s.set_defaults(func=cmd_lga_svd)

    s = sub.add_parser("lga-scale", help="LoRA-GA scale")
    add_store(s)
    s.add_argument("svd_id")
    s.set_defaults(func=cmd_lga_scale)

    s = sub.add_parser("lga-score", help="LoRA-GA score")
    add_store(s)
    s.add_argument("scale_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lga_score)

    s = sub.add_parser("lga-fast", help="LoRA-GA fast flag")
    add_store(s)
    s.add_argument("--faster-convergence", action="store_true")
    s.set_defaults(func=cmd_lga_fast)

    s = sub.add_parser("lga-loop", help="LoRA-GA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["grad", "svd", "scale", "score"]
    )
    s.set_defaults(func=cmd_lga_loop)

    s = sub.add_parser("mor-square", help="MoRA square")
    add_store(s)
    s.add_argument("task")
    s.add_argument("side", type=int)
    s.set_defaults(func=cmd_mor_square)

    s = sub.add_parser("mor-compress", help="MoRA compress")
    add_store(s)
    s.add_argument("square_id")
    s.set_defaults(func=cmd_mor_compress)

    s = sub.add_parser("mor-expand", help="MoRA expand")
    add_store(s)
    s.add_argument("compress_id")
    s.set_defaults(func=cmd_mor_expand)

    s = sub.add_parser("mor-score", help="MoRA score")
    add_store(s)
    s.add_argument("expand_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mor_score)

    s = sub.add_parser("mor-merge", help="MoRA merge flag")
    add_store(s)
    s.add_argument("--mergeable", action="store_true")
    s.set_defaults(func=cmd_mor_merge)

    s = sub.add_parser("mor-loop", help="MoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["square", "compress", "expand", "score"]
    )
    s.set_defaults(func=cmd_mor_loop)

    s = sub.add_parser("rsl-rank", help="rsLoRA rank")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_rsl_rank)

    s = sub.add_parser("rsl-scale", help="rsLoRA scale")
    add_store(s)
    s.add_argument("rank_id")
    s.set_defaults(func=cmd_rsl_scale)

    s = sub.add_parser("rsl-train", help="rsLoRA train")
    add_store(s)
    s.add_argument("scale_id")
    s.set_defaults(func=cmd_rsl_train)

    s = sub.add_parser("rsl-score", help="rsLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_rsl_score)

    s = sub.add_parser("rsl-stable", help="rsLoRA stable flag")
    add_store(s)
    s.add_argument("--no-collapse", action="store_true")
    s.set_defaults(func=cmd_rsl_stable)

    s = sub.add_parser("rsl-loop", help="rsLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["rank", "scale", "train", "score"]
    )
    s.set_defaults(func=cmd_rsl_loop)

    s = sub.add_parser("lkr-factors", help="LoKr factors")
    add_store(s)
    s.add_argument("task")
    s.add_argument("factor_a", type=int)
    s.add_argument("factor_b", type=int)
    s.set_defaults(func=cmd_lkr_factors)

    s = sub.add_parser("lkr-kron", help="LoKr kron")
    add_store(s)
    s.add_argument("factors_id")
    s.set_defaults(func=cmd_lkr_kron)

    s = sub.add_parser("lkr-vectorize", help="LoKr vectorize")
    add_store(s)
    s.add_argument("kron_id")
    s.set_defaults(func=cmd_lkr_vectorize)

    s = sub.add_parser("lkr-score", help="LoKr score")
    add_store(s)
    s.add_argument("vector_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lkr_score)

    s = sub.add_parser("lkr-preserve", help="LoKr preserve flag")
    add_store(s)
    s.add_argument("--rank-preserved", action="store_true")
    s.set_defaults(func=cmd_lkr_preserve)

    s = sub.add_parser("lkr-loop", help="LoKr loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["factors", "kron", "vectorize", "score"]
    )
    s.set_defaults(func=cmd_lkr_loop)

    s = sub.add_parser("lha-pair", help="LoHa pair")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lha_pair)

    s = sub.add_parser("lha-hadamard", help="LoHa hadamard")
    add_store(s)
    s.add_argument("pair_id")
    s.set_defaults(func=cmd_lha_hadamard)

    s = sub.add_parser("lha-train", help="LoHa train")
    add_store(s)
    s.add_argument("hadamard_id")
    s.set_defaults(func=cmd_lha_train)

    s = sub.add_parser("lha-score", help="LoHa score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lha_score)

    s = sub.add_parser("lha-express", help="LoHa express flag")
    add_store(s)
    s.add_argument("--more-expressivity", action="store_true")
    s.set_defaults(func=cmd_lha_express)

    s = sub.add_parser("lha-loop", help="LoHa loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["pair", "hadamard", "train", "score"]
    )
    s.set_defaults(func=cmd_lha_loop)

    s = sub.add_parser("fft-basis", help="FourierFT basis")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_coeff", type=int)
    s.set_defaults(func=cmd_fft_basis)

    s = sub.add_parser("fft-coeff", help="FourierFT coeff")
    add_store(s)
    s.add_argument("basis_id")
    s.set_defaults(func=cmd_fft_coeff)

    s = sub.add_parser("fft-idft", help="FourierFT idft")
    add_store(s)
    s.add_argument("coeff_id")
    s.set_defaults(func=cmd_fft_idft)

    s = sub.add_parser("fft-score", help="FourierFT score")
    add_store(s)
    s.add_argument("idft_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_fft_score)

    s = sub.add_parser("fft-sparse", help="FourierFT sparse flag")
    add_store(s)
    s.add_argument("--spectral-sparse", action="store_true")
    s.set_defaults(func=cmd_fft_sparse)

    s = sub.add_parser("fft-loop", help="FourierFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["basis", "coeff", "idft", "score"]
    )
    s.set_defaults(func=cmd_fft_loop)

    s = sub.add_parser("had-insert", help="Houlsby insert")
    add_store(s)
    s.add_argument("task")
    s.add_argument("bottleneck", type=int)
    s.set_defaults(func=cmd_had_insert)

    s = sub.add_parser("had-freeze", help="Houlsby freeze")
    add_store(s)
    s.add_argument("insert_id")
    s.set_defaults(func=cmd_had_freeze)

    s = sub.add_parser("had-train", help="Houlsby train")
    add_store(s)
    s.add_argument("freeze_id")
    s.set_defaults(func=cmd_had_train)

    s = sub.add_parser("had-score", help="Houlsby score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_had_score)

    s = sub.add_parser("had-latency", help="Houlsby latency flag")
    add_store(s)
    s.add_argument("--adds-latency", action="store_true")
    s.set_defaults(func=cmd_had_latency)

    s = sub.add_parser("had-loop", help="Houlsby loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["insert", "freeze", "train", "score"]
    )
    s.set_defaults(func=cmd_had_loop)

    s = sub.add_parser("rft-repr", help="ReFT repr")
    add_store(s)
    s.add_argument("task")
    s.add_argument("layers", type=int)
    s.set_defaults(func=cmd_rft_repr)

    s = sub.add_parser("rft-edit", help="ReFT edit")
    add_store(s)
    s.add_argument("repr_id")
    s.set_defaults(func=cmd_rft_edit)

    s = sub.add_parser("rft-train", help="ReFT train")
    add_store(s)
    s.add_argument("edit_id")
    s.set_defaults(func=cmd_rft_train)

    s = sub.add_parser("rft-score", help="ReFT score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_rft_score)

    s = sub.add_parser("rft-weightless", help="ReFT weightless flag")
    add_store(s)
    s.add_argument("--no-weight-update", action="store_true")
    s.set_defaults(func=cmd_rft_weightless)

    s = sub.add_parser("rft-loop", help="ReFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["repr", "edit", "train", "score"]
    )
    s.set_defaults(func=cmd_rft_loop)

    s = sub.add_parser("oft-ortho", help="OFT ortho")
    add_store(s)
    s.add_argument("task")
    s.add_argument("block", type=int)
    s.set_defaults(func=cmd_oft_ortho)

    s = sub.add_parser("oft-butterfly", help="OFT butterfly")
    add_store(s)
    s.add_argument("ortho_id")
    s.add_argument("factors", type=int)
    s.set_defaults(func=cmd_oft_butterfly)

    s = sub.add_parser("oft-train", help="OFT train")
    add_store(s)
    s.add_argument("butterfly_id")
    s.set_defaults(func=cmd_oft_train)

    s = sub.add_parser("oft-score", help="OFT score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_oft_score)

    s = sub.add_parser("oft-energy", help="OFT energy flag")
    add_store(s)
    s.add_argument("--hypersphere-preserved", action="store_true")
    s.set_defaults(func=cmd_oft_energy)

    s = sub.add_parser("oft-loop", help="OFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["ortho", "butterfly", "train", "score"]
    )
    s.set_defaults(func=cmd_oft_loop)

    s = sub.add_parser("mss-shard", help="MiSS shard")
    add_store(s)
    s.add_argument("task")
    s.add_argument("shards", type=int)
    s.set_defaults(func=cmd_mss_shard)

    s = sub.add_parser("mss-share", help="MiSS share")
    add_store(s)
    s.add_argument("shard_id")
    s.set_defaults(func=cmd_mss_share)

    s = sub.add_parser("mss-train", help="MiSS train")
    add_store(s)
    s.add_argument("share_id")
    s.set_defaults(func=cmd_mss_train)

    s = sub.add_parser("mss-score", help="MiSS score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mss_score)

    s = sub.add_parser("mss-pareto", help="MiSS pareto flag")
    add_store(s)
    s.add_argument("--better-tradeoff", action="store_true")
    s.set_defaults(func=cmd_mss_pareto)

    s = sub.add_parser("mss-loop", help="MiSS loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["shard", "share", "train", "score"]
    )
    s.set_defaults(func=cmd_mss_loop)

    s = sub.add_parser("drl-rank", help="DropLoRA rank")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_drl_rank)

    s = sub.add_parser("drl-mask", help="DropLoRA mask")
    add_store(s)
    s.add_argument("rank_id")
    s.add_argument("keep_prob", type=int)
    s.set_defaults(func=cmd_drl_mask)

    s = sub.add_parser("drl-train", help="DropLoRA train")
    add_store(s)
    s.add_argument("mask_id")
    s.set_defaults(func=cmd_drl_train)

    s = sub.add_parser("drl-score", help="DropLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_drl_score)

    s = sub.add_parser("drl-infer", help="DropLoRA infer flag")
    add_store(s)
    s.add_argument("--no-extra-cost", action="store_true")
    s.set_defaults(func=cmd_drl_infer)

    s = sub.add_parser("drl-loop", help="DropLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["rank", "mask", "train", "score"]
    )
    s.set_defaults(func=cmd_drl_loop)

    s = sub.add_parser("gal-grad", help="GaLore grad")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_gal_grad)

    s = sub.add_parser("gal-project", help="GaLore project")
    add_store(s)
    s.add_argument("grad_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_gal_project)

    s = sub.add_parser("gal-step", help="GaLore step")
    add_store(s)
    s.add_argument("project_id")
    s.set_defaults(func=cmd_gal_step)

    s = sub.add_parser("gal-score", help="GaLore score")
    add_store(s)
    s.add_argument("step_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_gal_score)

    s = sub.add_parser("gal-full", help="GaLore full flag")
    add_store(s)
    s.add_argument("--updates-all-weights", action="store_true")
    s.set_defaults(func=cmd_gal_full)

    s = sub.add_parser("gal-loop", help="GaLore loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["grad", "project", "step", "score"]
    )
    s.set_defaults(func=cmd_gal_loop)

    s = sub.add_parser("shr-mask", help="SHiRA mask")
    add_store(s)
    s.add_argument("task")
    s.add_argument("pct", type=int)
    s.set_defaults(func=cmd_shr_mask)

    s = sub.add_parser("shr-tune", help="SHiRA tune")
    add_store(s)
    s.add_argument("mask_id")
    s.set_defaults(func=cmd_shr_tune)

    s = sub.add_parser("shr-switch", help="SHiRA switch")
    add_store(s)
    s.add_argument("tune_id")
    s.set_defaults(func=cmd_shr_switch)

    s = sub.add_parser("shr-score", help="SHiRA score")
    add_store(s)
    s.add_argument("switch_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_shr_score)

    s = sub.add_parser("shr-fusion", help="SHiRA fusion flag")
    add_store(s)
    s.add_argument("--less-concept-loss", action="store_true")
    s.set_defaults(func=cmd_shr_fusion)

    s = sub.add_parser("shr-loop", help="SHiRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["mask", "tune", "switch", "score"]
    )
    s.set_defaults(func=cmd_shr_loop)

    s = sub.add_parser("wft-wave", help="WaveFT wave")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_coeff", type=int)
    s.set_defaults(func=cmd_wft_wave)

    s = sub.add_parser("wft-sparse", help="WaveFT sparse")
    add_store(s)
    s.add_argument("wave_id")
    s.set_defaults(func=cmd_wft_sparse)

    s = sub.add_parser("wft-idwt", help="WaveFT idwt")
    add_store(s)
    s.add_argument("sparse_id")
    s.set_defaults(func=cmd_wft_idwt)

    s = sub.add_parser("wft-score", help="WaveFT score")
    add_store(s)
    s.add_argument("idwt_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_wft_score)

    s = sub.add_parser("wft-granular", help="WaveFT granular flag")
    add_store(s)
    s.add_argument("--below-lora-min", action="store_true")
    s.set_defaults(func=cmd_wft_granular)

    s = sub.add_parser("wft-loop", help="WaveFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["wave", "sparse", "idwt", "score"]
    )
    s.set_defaults(func=cmd_wft_loop)

    s = sub.add_parser("lpr-equiv", help="LoRA-Pro equiv")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_lpr_equiv)

    s = sub.add_parser("lpr-adjust", help="LoRA-Pro adjust")
    add_store(s)
    s.add_argument("equiv_id")
    s.set_defaults(func=cmd_lpr_adjust)

    s = sub.add_parser("lpr-train", help="LoRA-Pro train")
    add_store(s)
    s.add_argument("adjust_id")
    s.set_defaults(func=cmd_lpr_train)

    s = sub.add_parser("lpr-score", help="LoRA-Pro score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lpr_score)

    s = sub.add_parser("lpr-bridge", help="LoRA-Pro bridge flag")
    add_store(s)
    s.add_argument("--closer-to-fft", action="store_true")
    s.set_defaults(func=cmd_lpr_bridge)

    s = sub.add_parser("lpr-loop", help="LoRA-Pro loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["equiv", "adjust", "train", "score"]
    )
    s.set_defaults(func=cmd_lpr_loop)

    s = sub.add_parser("krl-kron", help="Kron-LoRA kron")
    add_store(s)
    s.add_argument("task")
    s.add_argument("factor", type=int)
    s.set_defaults(func=cmd_krl_kron)

    s = sub.add_parser("krl-lora", help="Kron-LoRA lora")
    add_store(s)
    s.add_argument("kron_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_krl_lora)

    s = sub.add_parser("krl-train", help="Kron-LoRA train")
    add_store(s)
    s.add_argument("lora_id")
    s.set_defaults(func=cmd_krl_train)

    s = sub.add_parser("krl-score", help="Kron-LoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_krl_score)

    s = sub.add_parser("krl-compress", help="Kron-LoRA compress flag")
    add_store(s)
    s.add_argument("--more-compression", action="store_true")
    s.set_defaults(func=cmd_krl_compress)

    s = sub.add_parser("krl-loop", help="Kron-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["kron", "lora", "train", "score"]
    )
    s.set_defaults(func=cmd_krl_loop)

    s = sub.add_parser("mil-svd", help="MiLoRA svd")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_mil_svd)

    s = sub.add_parser("mil-minor", help="MiLoRA minor")
    add_store(s)
    s.add_argument("svd_id")
    s.set_defaults(func=cmd_mil_minor)

    s = sub.add_parser("mil-freeze", help="MiLoRA freeze")
    add_store(s)
    s.add_argument("minor_id")
    s.set_defaults(func=cmd_mil_freeze)

    s = sub.add_parser("mil-score", help="MiLoRA score")
    add_store(s)
    s.add_argument("freeze_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mil_score)

    s = sub.add_parser("mil-preserve", help="MiLoRA preserve flag")
    add_store(s)
    s.add_argument("--preserves-principal", action="store_true")
    s.set_defaults(func=cmd_mil_preserve)

    s = sub.add_parser("mil-loop", help="MiLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["svd", "minor", "freeze", "score"]
    )
    s.set_defaults(func=cmd_mil_loop)

    s = sub.add_parser("cda-cov", help="CorDA cov")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_cda_cov)

    s = sub.add_parser("cda-mode", help="CorDA mode")
    add_store(s)
    s.add_argument("cov_id")
    s.add_argument("mode", choices=["KPM", "IPM", "kpm", "ipm"])
    s.set_defaults(func=cmd_cda_mode)

    s = sub.add_parser("cda-adapt", help="CorDA adapt")
    add_store(s)
    s.add_argument("mode_id")
    s.set_defaults(func=cmd_cda_adapt)

    s = sub.add_parser("cda-score", help="CorDA score")
    add_store(s)
    s.add_argument("adapt_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_cda_score)

    s = sub.add_parser("cda-forget", help="CorDA forget flag")
    add_store(s)
    s.add_argument("--less-forgetting", action="store_true")
    s.set_defaults(func=cmd_cda_forget)

    s = sub.add_parser("cda-loop", help="CorDA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["cov", "mode", "adapt", "score"]
    )
    s.set_defaults(func=cmd_cda_loop)

    s = sub.add_parser("lfq-quant", help="LoftQ quant")
    add_store(s)
    s.add_argument("task")
    s.add_argument("bits", type=int)
    s.set_defaults(func=cmd_lfq_quant)

    s = sub.add_parser("lfq-init", help="LoftQ init")
    add_store(s)
    s.add_argument("quant_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lfq_init)

    s = sub.add_parser("lfq-train", help="LoftQ train")
    add_store(s)
    s.add_argument("init_id")
    s.set_defaults(func=cmd_lfq_train)

    s = sub.add_parser("lfq-score", help="LoftQ score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lfq_score)

    s = sub.add_parser("lfq-gap", help="LoftQ gap flag")
    add_store(s)
    s.add_argument("--closes-qlora-gap", action="store_true")
    s.set_defaults(func=cmd_lfq_gap)

    s = sub.add_parser("lfq-loop", help="LoftQ loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["quant", "init", "train", "score"]
    )
    s.set_defaults(func=cmd_lfq_loop)

    s = sub.add_parser("lds-prelaunch", help="LoRA-Dash prelaunch")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_lds_prelaunch)

    s = sub.add_parser("lds-tsd", help="LoRA-Dash tsd")
    add_store(s)
    s.add_argument("prelaunch_id")
    s.add_argument("count", type=int)
    s.set_defaults(func=cmd_lds_tsd)

    s = sub.add_parser("lds-dash", help="LoRA-Dash dash")
    add_store(s)
    s.add_argument("tsd_id")
    s.set_defaults(func=cmd_lds_dash)

    s = sub.add_parser("lds-score", help="LoRA-Dash score")
    add_store(s)
    s.add_argument("dash_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lds_score)

    s = sub.add_parser("lds-impact", help="LoRA-Dash impact flag")
    add_store(s)
    s.add_argument("--maximizes-tsd", action="store_true")
    s.set_defaults(func=cmd_lds_impact)

    s = sub.add_parser("lds-loop", help="LoRA-Dash loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["prelaunch", "tsd", "dash", "score"]
    )
    s.set_defaults(func=cmd_lds_loop)

    s = sub.add_parser("dlo-adapters", help="Delta-LoRA adapters")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_dlo_adapters)

    s = sub.add_parser("dlo-delta", help="Delta-LoRA delta")
    add_store(s)
    s.add_argument("adapters_id")
    s.set_defaults(func=cmd_dlo_delta)

    s = sub.add_parser("dlo-propagate", help="Delta-LoRA propagate")
    add_store(s)
    s.add_argument("delta_id")
    s.set_defaults(func=cmd_dlo_propagate)

    s = sub.add_parser("dlo-score", help="Delta-LoRA score")
    add_store(s)
    s.add_argument("propagate_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_dlo_score)

    s = sub.add_parser("dlo-highrank", help="Delta-LoRA highrank flag")
    add_store(s)
    s.add_argument("--high-rank-capacity", action="store_true")
    s.set_defaults(func=cmd_dlo_highrank)

    s = sub.add_parser("dlo-loop", help="Delta-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["adapters", "delta", "propagate", "score"]
    )
    s.set_defaults(func=cmd_dlo_loop)

    s = sub.add_parser("lon-grad", help="LoRA-One grad")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_lon_grad)

    s = sub.add_parser("lon-align", help="LoRA-One align")
    add_store(s)
    s.add_argument("grad_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lon_align)

    s = sub.add_parser("lon-train", help="LoRA-One train")
    add_store(s)
    s.add_argument("align_id")
    s.set_defaults(func=cmd_lon_train)

    s = sub.add_parser("lon-score", help="LoRA-One score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lon_score)

    s = sub.add_parser("lon-immediate", help="LoRA-One immediate flag")
    add_store(s)
    s.add_argument("--immediate-align", action="store_true")
    s.set_defaults(func=cmd_lon_immediate)

    s = sub.add_parser("lon-loop", help="LoRA-One loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["grad", "align", "train", "score"]
    )
    s.set_defaults(func=cmd_lon_loop)

    s = sub.add_parser("olr-qr", help="OLoRA qr")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_olr_qr)

    s = sub.add_parser("olr-ortho", help="OLoRA ortho")
    add_store(s)
    s.add_argument("qr_id")
    s.set_defaults(func=cmd_olr_ortho)

    s = sub.add_parser("olr-train", help="OLoRA train")
    add_store(s)
    s.add_argument("ortho_id")
    s.set_defaults(func=cmd_olr_train)

    s = sub.add_parser("olr-score", help="OLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_olr_score)

    s = sub.add_parser("olr-stable", help="OLoRA stable flag")
    add_store(s)
    s.add_argument("--stable-landscape", action="store_true")
    s.set_defaults(func=cmd_olr_stable)

    s = sub.add_parser("olr-loop", help="OLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["qr", "ortho", "train", "score"]
    )
    s.set_defaults(func=cmd_olr_loop)

    s = sub.add_parser("lsp-select", help="LoRA-SP select")
    add_store(s)
    s.add_argument("task")
    s.add_argument("fraction", type=int)
    s.set_defaults(func=cmd_lsp_select)

    s = sub.add_parser("lsp-freeze", help="LoRA-SP freeze")
    add_store(s)
    s.add_argument("select_id")
    s.set_defaults(func=cmd_lsp_freeze)

    s = sub.add_parser("lsp-train", help="LoRA-SP train")
    add_store(s)
    s.add_argument("freeze_id")
    s.set_defaults(func=cmd_lsp_train)

    s = sub.add_parser("lsp-score", help="LoRA-SP score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lsp_score)

    s = sub.add_parser("lsp-memory", help="LoRA-SP memory flag")
    add_store(s)
    s.add_argument("--lower-memory", action="store_true")
    s.set_defaults(func=cmd_lsp_memory)

    s = sub.add_parser("lsp-loop", help="LoRA-SP loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["select", "freeze", "train", "score"]
    )
    s.set_defaults(func=cmd_lsp_loop)

    s = sub.add_parser("qps-quant", help="QPiSSA quant")
    add_store(s)
    s.add_argument("task")
    s.add_argument("bits", type=int)
    s.set_defaults(func=cmd_qps_quant)

    s = sub.add_parser("qps-principal", help="QPiSSA principal")
    add_store(s)
    s.add_argument("quant_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_qps_principal)

    s = sub.add_parser("qps-train", help="QPiSSA train")
    add_store(s)
    s.add_argument("principal_id")
    s.set_defaults(func=cmd_qps_train)

    s = sub.add_parser("qps-score", help="QPiSSA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_qps_score)

    s = sub.add_parser("qps-error", help="QPiSSA error flag")
    add_store(s)
    s.add_argument("--smaller-than-qlora", action="store_true")
    s.set_defaults(func=cmd_qps_error)

    s = sub.add_parser("qps-loop", help="QPiSSA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["quant", "principal", "train", "score"]
    )
    s.set_defaults(func=cmd_qps_loop)

    s = sub.add_parser("msl-split", help="MoSLoRA split")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_msl_split)

    s = sub.add_parser("msl-mixer", help="MoSLoRA mixer")
    add_store(s)
    s.add_argument("split_id")
    s.set_defaults(func=cmd_msl_mixer)

    s = sub.add_parser("msl-train", help="MoSLoRA train")
    add_store(s)
    s.add_argument("mixer_id")
    s.set_defaults(func=cmd_msl_train)

    s = sub.add_parser("msl-score", help="MoSLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_msl_score)

    s = sub.add_parser("msl-fuse", help="MoSLoRA fuse flag")
    add_store(s)
    s.add_argument("--flexible-fuse", action="store_true")
    s.set_defaults(func=cmd_msl_fuse)

    s = sub.add_parser("msl-loop", help="MoSLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["split", "mixer", "train", "score"]
    )
    s.set_defaults(func=cmd_msl_loop)

    s = sub.add_parser("ldr-eval", help="LoRA-drop eval")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_ldr_eval)

    s = sub.add_parser("ldr-keep", help="LoRA-drop keep")
    add_store(s)
    s.add_argument("eval_id")
    s.add_argument("keep_pct", type=int)
    s.set_defaults(func=cmd_ldr_keep)

    s = sub.add_parser("ldr-share", help="LoRA-drop share")
    add_store(s)
    s.add_argument("keep_id")
    s.set_defaults(func=cmd_ldr_share)

    s = sub.add_parser("ldr-score", help="LoRA-drop score")
    add_store(s)
    s.add_argument("share_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ldr_score)

    s = sub.add_parser("ldr-prune", help="LoRA-drop prune flag")
    add_store(s)
    s.add_argument("--half-params", action="store_true")
    s.set_defaults(func=cmd_ldr_prune)

    s = sub.add_parser("ldr-loop", help="LoRA-drop loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["eval", "keep", "share", "score"]
    )
    s.set_defaults(func=cmd_ldr_loop)

    s = sub.add_parser("vbl-bank", help="VB-LoRA bank")
    add_store(s)
    s.add_argument("task")
    s.add_argument("size", type=int)
    s.set_defaults(func=cmd_vbl_bank)

    s = sub.add_parser("vbl-topk", help="VB-LoRA topk")
    add_store(s)
    s.add_argument("bank_id")
    s.add_argument("k", type=int)
    s.set_defaults(func=cmd_vbl_topk)

    s = sub.add_parser("vbl-compose", help="VB-LoRA compose")
    add_store(s)
    s.add_argument("topk_id")
    s.set_defaults(func=cmd_vbl_compose)

    s = sub.add_parser("vbl-score", help="VB-LoRA score")
    add_store(s)
    s.add_argument("compose_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_vbl_score)

    s = sub.add_parser("vbl-extreme", help="VB-LoRA extreme flag")
    add_store(s)
    s.add_argument("--extreme-compression", action="store_true")
    s.set_defaults(func=cmd_vbl_extreme)

    s = sub.add_parser("vbl-loop", help="VB-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["bank", "topk", "compose", "score"]
    )
    s.set_defaults(func=cmd_vbl_loop)

    s = sub.add_parser("opl-proj", help="OPLoRA proj")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_opl_proj)

    s = sub.add_parser("opl-constrain", help="OPLoRA constrain")
    add_store(s)
    s.add_argument("proj_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_opl_constrain)

    s = sub.add_parser("opl-train", help="OPLoRA train")
    add_store(s)
    s.add_argument("constrain_id")
    s.set_defaults(func=cmd_opl_train)

    s = sub.add_parser("opl-score", help="OPLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_opl_score)

    s = sub.add_parser("opl-forget", help="OPLoRA forget flag")
    add_store(s)
    s.add_argument("--less-forgetting", action="store_true")
    s.set_defaults(func=cmd_opl_forget)

    s = sub.add_parser("opl-loop", help="OPLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["proj", "constrain", "train", "score"]
    )
    s.set_defaults(func=cmd_opl_loop)

    s = sub.add_parser("gel-idim", help="GeLoRA idim")
    add_store(s)
    s.add_argument("task")
    s.add_argument("layer", type=int)
    s.set_defaults(func=cmd_gel_idim)

    s = sub.add_parser("gel-rank", help="GeLoRA rank")
    add_store(s)
    s.add_argument("idim_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_gel_rank)

    s = sub.add_parser("gel-train", help="GeLoRA train")
    add_store(s)
    s.add_argument("rank_id")
    s.set_defaults(func=cmd_gel_train)

    s = sub.add_parser("gel-score", help="GeLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_gel_score)

    s = sub.add_parser("gel-budget", help="GeLoRA budget flag")
    add_store(s)
    s.add_argument("--within-budget", action="store_true")
    s.set_defaults(func=cmd_gel_budget)

    s = sub.add_parser("gel-loop", help="GeLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["idim", "rank", "train", "score"]
    )
    s.set_defaults(func=cmd_gel_loop)

    s = sub.add_parser("geo-dyn", help="GeoLoRA dyn")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_geo_dyn)

    s = sub.add_parser("geo-budget", help="GeoLoRA budget")
    add_store(s)
    s.add_argument("dyn_id")
    s.add_argument("layers", type=int)
    s.set_defaults(func=cmd_geo_budget)

    s = sub.add_parser("geo-train", help="GeoLoRA train")
    add_store(s)
    s.add_argument("budget_id")
    s.set_defaults(func=cmd_geo_train)

    s = sub.add_parser("geo-score", help="GeoLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_geo_score)

    s = sub.add_parser("geo-ortho", help="GeoLoRA ortho flag")
    add_store(s)
    s.add_argument("--exact-ortho", action="store_true")
    s.set_defaults(func=cmd_geo_ortho)

    s = sub.add_parser("geo-loop", help="GeoLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["dyn", "budget", "train", "score"]
    )
    s.set_defaults(func=cmd_geo_loop)

    s = sub.add_parser("rlo-bases", help="RandLoRA bases")
    add_store(s)
    s.add_argument("task")
    s.add_argument("count", type=int)
    s.set_defaults(func=cmd_rlo_bases)

    s = sub.add_parser("rlo-scale", help="RandLoRA scale")
    add_store(s)
    s.add_argument("bases_id")
    s.set_defaults(func=cmd_rlo_scale)

    s = sub.add_parser("rlo-train", help="RandLoRA train")
    add_store(s)
    s.add_argument("scale_id")
    s.set_defaults(func=cmd_rlo_train)

    s = sub.add_parser("rlo-score", help="RandLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_rlo_score)

    s = sub.add_parser("rlo-fullrank", help="RandLoRA fullrank flag")
    add_store(s)
    s.add_argument("--full-rank-update", action="store_true")
    s.set_defaults(func=cmd_rlo_fullrank)

    s = sub.add_parser("rlo-loop", help="RandLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["bases", "scale", "train", "score"]
    )
    s.set_defaults(func=cmd_rlo_loop)

    s = sub.add_parser("lsh-graph", help="LoRAShear graph")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_lsh_graph)

    s = sub.add_parser("lsh-prune", help="LoRAShear prune")
    add_store(s)
    s.add_argument("graph_id")
    s.add_argument("ratio_pct", type=int)
    s.set_defaults(func=cmd_lsh_prune)

    s = sub.add_parser("lsh-recover", help="LoRAShear recover")
    add_store(s)
    s.add_argument("prune_id")
    s.set_defaults(func=cmd_lsh_recover)

    s = sub.add_parser("lsh-score", help="LoRAShear score")
    add_store(s)
    s.add_argument("recover_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lsh_score)

    s = sub.add_parser("lsh-footprint", help="LoRAShear footprint flag")
    add_store(s)
    s.add_argument("--reduced", action="store_true")
    s.set_defaults(func=cmd_lsh_footprint)

    s = sub.add_parser("lsh-loop", help="LoRAShear loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["graph", "prune", "recover", "score"]
    )
    s.set_defaults(func=cmd_lsh_loop)

    s = sub.add_parser("aop-sub", help="Alternating OPLoRA subproblem")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_aop_sub)

    s = sub.add_parser("aop-alt", help="Alternating OPLoRA ALS steps")
    add_store(s)
    s.add_argument("sub_id")
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_aop_alt)

    s = sub.add_parser("aop-train", help="Alternating OPLoRA train")
    add_store(s)
    s.add_argument("alt_id")
    s.set_defaults(func=cmd_aop_train)

    s = sub.add_parser("aop-score", help="Alternating OPLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_aop_score)

    s = sub.add_parser("aop-svd", help="Alternating OPLoRA near-SVD flag")
    add_store(s)
    s.add_argument("--near-svd", action="store_true")
    s.set_defaults(func=cmd_aop_svd)

    s = sub.add_parser("aop-loop", help="Alternating OPLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["sub", "alt", "train", "score"]
    )
    s.set_defaults(func=cmd_aop_loop)

    s = sub.add_parser("lin-tsd", help="LoRA-Init TSD")
    add_store(s)
    s.add_argument("task")
    s.add_argument("count", type=int)
    s.set_defaults(func=cmd_lin_tsd)

    s = sub.add_parser("lin-init", help="LoRA-Init init")
    add_store(s)
    s.add_argument("tsd_id")
    s.set_defaults(func=cmd_lin_init)

    s = sub.add_parser("lin-train", help="LoRA-Init train")
    add_store(s)
    s.add_argument("init_id")
    s.set_defaults(func=cmd_lin_train)

    s = sub.add_parser("lin-score", help="LoRA-Init score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lin_score)

    s = sub.add_parser("lin-fast", help="LoRA-Init fast flag")
    add_store(s)
    s.add_argument("--faster-convergence", action="store_true")
    s.set_defaults(func=cmd_lin_fast)

    s = sub.add_parser("lin-loop", help="LoRA-Init loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tsd", "init", "train", "score"]
    )
    s.set_defaults(func=cmd_lin_loop)

    s = sub.add_parser("lnu-act", help="LoRA-Null activations")
    add_store(s)
    s.add_argument("task")
    s.add_argument("samples", type=int)
    s.set_defaults(func=cmd_lnu_act)

    s = sub.add_parser("lnu-null", help="LoRA-Null null space")
    add_store(s)
    s.add_argument("act_id")
    s.set_defaults(func=cmd_lnu_null)

    s = sub.add_parser("lnu-train", help="LoRA-Null train")
    add_store(s)
    s.add_argument("null_id")
    s.set_defaults(func=cmd_lnu_train)

    s = sub.add_parser("lnu-score", help="LoRA-Null score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lnu_score)

    s = sub.add_parser("lnu-forget", help="LoRA-Null forget flag")
    add_store(s)
    s.add_argument("--preserves-knowledge", action="store_true")
    s.set_defaults(func=cmd_lnu_forget)

    s = sub.add_parser("lnu-loop", help="LoRA-Null loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["act", "null", "train", "score"]
    )
    s.set_defaults(func=cmd_lnu_loop)

    s = sub.add_parser("hyd-share", help="HydraLoRA shared A")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_hyd_share)

    s = sub.add_parser("hyd-heads", help="HydraLoRA multi-B heads")
    add_store(s)
    s.add_argument("share_id")
    s.add_argument("heads", type=int)
    s.set_defaults(func=cmd_hyd_heads)

    s = sub.add_parser("hyd-route", help="HydraLoRA MoE route")
    add_store(s)
    s.add_argument("heads_id")
    s.set_defaults(func=cmd_hyd_route)

    s = sub.add_parser("hyd-score", help="HydraLoRA score")
    add_store(s)
    s.add_argument("route_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_hyd_score)

    s = sub.add_parser("hyd-nodomain", help="HydraLoRA no-domain flag")
    add_store(s)
    s.add_argument("--no-domain-labels", action="store_true")
    s.set_defaults(func=cmd_hyd_nodomain)

    s = sub.add_parser("hyd-loop", help="HydraLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["share", "heads", "route", "score"]
    )
    s.set_defaults(func=cmd_hyd_loop)

    s = sub.add_parser("llg-msu", help="LoRA-LEGO MSUs")
    add_store(s)
    s.add_argument("task")
    s.add_argument("adapters", type=int)
    s.set_defaults(func=cmd_llg_msu)

    s = sub.add_parser("llg-cluster", help="LoRA-LEGO cluster")
    add_store(s)
    s.add_argument("msu_id")
    s.add_argument("k", type=int)
    s.set_defaults(func=cmd_llg_cluster)

    s = sub.add_parser("llg-merge", help="LoRA-LEGO merge")
    add_store(s)
    s.add_argument("cluster_id")
    s.set_defaults(func=cmd_llg_merge)

    s = sub.add_parser("llg-score", help="LoRA-LEGO score")
    add_store(s)
    s.add_argument("merge_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_llg_score)

    s = sub.add_parser("llg-modular", help="LoRA-LEGO modular flag")
    add_store(s)
    s.add_argument("--modular-merge", action="store_true")
    s.set_defaults(func=cmd_llg_modular)

    s = sub.add_parser("llg-loop", help="LoRA-LEGO loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["msu", "cluster", "merge", "score"]
    )
    s.set_defaults(func=cmd_llg_loop)

    s = sub.add_parser("lme-plugin", help="LoRAMoE plugin")
    add_store(s)
    s.add_argument("task")
    s.add_argument("experts", type=int)
    s.set_defaults(func=cmd_lme_plugin)

    s = sub.add_parser("lme-balance", help="LoRAMoE balance")
    add_store(s)
    s.add_argument("plugin_id")
    s.set_defaults(func=cmd_lme_balance)

    s = sub.add_parser("lme-route", help="LoRAMoE route")
    add_store(s)
    s.add_argument("balance_id")
    s.set_defaults(func=cmd_lme_route)

    s = sub.add_parser("lme-score", help="LoRAMoE score")
    add_store(s)
    s.add_argument("route_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lme_score)

    s = sub.add_parser("lme-forget", help="LoRAMoE forget flag")
    add_store(s)
    s.add_argument("--preserves-world", action="store_true")
    s.set_defaults(func=cmd_lme_forget)

    s = sub.add_parser("lme-loop", help="LoRAMoE loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["plugin", "balance", "route", "score"]
    )
    s.set_defaults(func=cmd_lme_loop)

    s = sub.add_parser("mel-experts", help="MoELoRA experts")
    add_store(s)
    s.add_argument("task")
    s.add_argument("count", type=int)
    s.set_defaults(func=cmd_mel_experts)

    s = sub.add_parser("mel-contrast", help="MoELoRA contrast")
    add_store(s)
    s.add_argument("experts_id")
    s.set_defaults(func=cmd_mel_contrast)

    s = sub.add_parser("mel-gate", help="MoELoRA gate")
    add_store(s)
    s.add_argument("contrast_id")
    s.set_defaults(func=cmd_mel_gate)

    s = sub.add_parser("mel-score", help="MoELoRA score")
    add_store(s)
    s.add_argument("gate_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mel_score)

    s = sub.add_parser("mel-sparse", help="MoELoRA sparse flag")
    add_store(s)
    s.add_argument("--sparse-activate", action="store_true")
    s.set_defaults(func=cmd_mel_sparse)

    s = sub.add_parser("mel-loop", help="MoELoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["experts", "contrast", "gate", "score"]
    )
    s.set_defaults(func=cmd_mel_loop)

    s = sub.add_parser("lhb-pool", help="LoraHub pool")
    add_store(s)
    s.add_argument("task")
    s.add_argument("modules", type=int)
    s.set_defaults(func=cmd_lhb_pool)

    s = sub.add_parser("lhb-compose", help="LoraHub compose")
    add_store(s)
    s.add_argument("pool_id")
    s.set_defaults(func=cmd_lhb_compose)

    s = sub.add_parser("lhb-adapt", help="LoraHub adapt")
    add_store(s)
    s.add_argument("compose_id")
    s.add_argument("shots", type=int)
    s.set_defaults(func=cmd_lhb_adapt)

    s = sub.add_parser("lhb-score", help="LoraHub score")
    add_store(s)
    s.add_argument("adapt_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lhb_score)

    s = sub.add_parser("lhb-nograd", help="LoraHub nograd flag")
    add_store(s)
    s.add_argument("--gradient-free", action="store_true")
    s.set_defaults(func=cmd_lhb_nograd)

    s = sub.add_parser("lhb-loop", help="LoraHub loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["pool", "compose", "adapt", "score"]
    )
    s.set_defaults(func=cmd_lhb_loop)

    s = sub.add_parser("mlr-scale", help="MultiLoRA scale")
    add_store(s)
    s.add_argument("task")
    s.add_argument("shards", type=int)
    s.set_defaults(func=cmd_mlr_scale)

    s = sub.add_parser("mlr-init", help="MultiLoRA init")
    add_store(s)
    s.add_argument("scale_id")
    s.set_defaults(func=cmd_mlr_init)

    s = sub.add_parser("mlr-train", help="MultiLoRA train")
    add_store(s)
    s.add_argument("init_id")
    s.set_defaults(func=cmd_mlr_train)

    s = sub.add_parser("mlr-score", help="MultiLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mlr_score)

    s = sub.add_parser("mlr-demo", help="MultiLoRA democratic flag")
    add_store(s)
    s.add_argument("--more-democratic", action="store_true")
    s.set_defaults(func=cmd_mlr_demo)

    s = sub.add_parser("mlr-loop", help="MultiLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["scale", "init", "train", "score"]
    )
    s.set_defaults(func=cmd_mlr_loop)

    s = sub.add_parser("mtl-task", help="MTL-LoRA task set")
    add_store(s)
    s.add_argument("task")
    s.add_argument("tasks", type=int)
    s.set_defaults(func=cmd_mtl_task)

    s = sub.add_parser("mtl-spec", help="MTL-LoRA task-specific")
    add_store(s)
    s.add_argument("task_id")
    s.set_defaults(func=cmd_mtl_spec)

    s = sub.add_parser("mtl-share", help="MTL-LoRA dynamic share")
    add_store(s)
    s.add_argument("spec_id")
    s.set_defaults(func=cmd_mtl_share)

    s = sub.add_parser("mtl-score", help="MTL-LoRA score")
    add_store(s)
    s.add_argument("share_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mtl_score)

    s = sub.add_parser("mtl-interfere", help="MTL-LoRA interference flag")
    add_store(s)
    s.add_argument("--less-interference", action="store_true")
    s.set_defaults(func=cmd_mtl_interfere)

    s = sub.add_parser("mtl-loop", help="MTL-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["task", "spec", "share", "score"]
    )
    s.set_defaults(func=cmd_mtl_loop)

    s = sub.add_parser("mal-mix", help="MALoRA expert mix")
    add_store(s)
    s.add_argument("task")
    s.add_argument("experts", type=int)
    s.set_defaults(func=cmd_mal_mix)

    s = sub.add_parser("mal-down", help="MALoRA shared down-proj")
    add_store(s)
    s.add_argument("mix_id")
    s.set_defaults(func=cmd_mal_down)

    s = sub.add_parser("mal-up", help="MALoRA asymmetric up-proj")
    add_store(s)
    s.add_argument("down_id")
    s.set_defaults(func=cmd_mal_up)

    s = sub.add_parser("mal-score", help="MALoRA score")
    add_store(s)
    s.add_argument("up_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mal_score)

    s = sub.add_parser("mal-eff", help="MALoRA efficiency flag")
    add_store(s)
    s.add_argument("--fewer-params", action="store_true")
    s.set_defaults(func=cmd_mal_eff)

    s = sub.add_parser("mal-loop", help="MALoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["mix", "down", "up", "score"]
    )
    s.set_defaults(func=cmd_mal_loop)

    s = sub.add_parser("lmi-split", help="LoRA-Mini split")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lmi_split)

    s = sub.add_parser("lmi-inner", help="LoRA-Mini inner trainable")
    add_store(s)
    s.add_argument("split_id")
    s.set_defaults(func=cmd_lmi_inner)

    s = sub.add_parser("lmi-train", help="LoRA-Mini train")
    add_store(s)
    s.add_argument("inner_id")
    s.set_defaults(func=cmd_lmi_train)

    s = sub.add_parser("lmi-score", help="LoRA-Mini score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lmi_score)

    s = sub.add_parser("lmi-tiny", help="LoRA-Mini compress flag")
    add_store(s)
    s.add_argument("--extreme-compress", action="store_true")
    s.set_defaults(func=cmd_lmi_tiny)

    s = sub.add_parser("lmi-loop", help="LoRA-Mini loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["split", "inner", "train", "score"]
    )
    s.set_defaults(func=cmd_lmi_loop)

    s = sub.add_parser("qdy-range", help="QDyLoRA rank range")
    add_store(s)
    s.add_argument("task")
    s.add_argument("r_min", type=int)
    s.add_argument("r_max", type=int)
    s.set_defaults(func=cmd_qdy_range)

    s = sub.add_parser("qdy-quant", help="QDyLoRA quantize")
    add_store(s)
    s.add_argument("range_id")
    s.add_argument("bits", type=int)
    s.set_defaults(func=cmd_qdy_quant)

    s = sub.add_parser("qdy-train", help="QDyLoRA train")
    add_store(s)
    s.add_argument("quant_id")
    s.set_defaults(func=cmd_qdy_train)

    s = sub.add_parser("qdy-score", help="QDyLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_qdy_score)

    s = sub.add_parser("qdy-pick", help="QDyLoRA pick-rank flag")
    add_store(s)
    s.add_argument("--pick-rank-at-infer", action="store_true")
    s.set_defaults(func=cmd_qdy_pick)

    s = sub.add_parser("qdy-loop", help="QDyLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["range", "quant", "train", "score"]
    )
    s.set_defaults(func=cmd_qdy_loop)

    s = sub.add_parser("lts-tsd", help="LoRA-TSD identify directions")
    add_store(s)
    s.add_argument("task")
    s.add_argument("count", type=int)
    s.set_defaults(func=cmd_lts_tsd)

    s = sub.add_parser("lts-init", help="LoRA-TSD init from TSDs")
    add_store(s)
    s.add_argument("tsd_id")
    s.set_defaults(func=cmd_lts_init)

    s = sub.add_parser("lts-dash", help="LoRA-TSD dash amplify")
    add_store(s)
    s.add_argument("init_id")
    s.set_defaults(func=cmd_lts_dash)

    s = sub.add_parser("lts-score", help="LoRA-TSD score")
    add_store(s)
    s.add_argument("dash_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lts_score)

    s = sub.add_parser("lts-combo", help="LoRA-TSD Init+Dash combo flag")
    add_store(s)
    s.add_argument("--uses-both", action="store_true")
    s.set_defaults(func=cmd_lts_combo)

    s = sub.add_parser("lts-loop", help="LoRA-TSD loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tsd", "init", "dash", "score"]
    )
    s.set_defaults(func=cmd_lts_loop)

    s = sub.add_parser("slr-pool", help="S-LoRA adapter pool")
    add_store(s)
    s.add_argument("adapters", type=int)
    s.set_defaults(func=cmd_slr_pool)

    s = sub.add_parser("slr-page", help="S-LoRA Unified Paging")
    add_store(s)
    s.add_argument("pool_id")
    s.add_argument("--unified", action="store_true")
    s.set_defaults(func=cmd_slr_page)

    s = sub.add_parser("slr-batch", help="S-LoRA heterogeneous batch")
    add_store(s)
    s.add_argument("page_id")
    s.add_argument("concurrent", type=int)
    s.set_defaults(func=cmd_slr_batch)

    s = sub.add_parser("slr-score", help="S-LoRA score")
    add_store(s)
    s.add_argument("batch_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_slr_score)

    s = sub.add_parser("slr-scale", help="S-LoRA scale flag")
    add_store(s)
    s.add_argument("--thousands", action="store_true")
    s.set_defaults(func=cmd_slr_scale)

    s = sub.add_parser("slr-loop", help="S-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["pool", "page", "batch", "score"]
    )
    s.set_defaults(func=cmd_slr_loop)

    s = sub.add_parser("cts-collect", help="Compress-then-Serve collect")
    add_store(s)
    s.add_argument("adapters", type=int)
    s.set_defaults(func=cmd_cts_collect)

    s = sub.add_parser("cts-basis", help="Compress-then-Serve shared basis")
    add_store(s)
    s.add_argument("collect_id")
    s.set_defaults(func=cmd_cts_basis)

    s = sub.add_parser("cts-scale", help="Compress-then-Serve per-adapter scales")
    add_store(s)
    s.add_argument("basis_id")
    s.add_argument("adapters", type=int)
    s.set_defaults(func=cmd_cts_scale)

    s = sub.add_parser("cts-score", help="Compress-then-Serve score")
    add_store(s)
    s.add_argument("scale_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_cts_score)

    s = sub.add_parser("cts-cluster", help="Compress-then-Serve cluster flag")
    add_store(s)
    s.add_argument("--cluster-for-large", action="store_true")
    s.set_defaults(func=cmd_cts_cluster)

    s = sub.add_parser("cts-loop", help="Compress-then-Serve loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["collect", "basis", "scale", "score"]
    )
    s.set_defaults(func=cmd_cts_loop)

    s = sub.add_parser("flo-clients", help="FLoRA client set")
    add_store(s)
    s.add_argument("clients", type=int)
    s.set_defaults(func=cmd_flo_clients)

    s = sub.add_parser("flo-stack", help="FLoRA stack adapters")
    add_store(s)
    s.add_argument("clients_id")
    s.add_argument("--hetero-ranks", action="store_true")
    s.set_defaults(func=cmd_flo_stack)

    s = sub.add_parser("flo-agg", help="FLoRA stacking aggregation")
    add_store(s)
    s.add_argument("stack_id")
    s.set_defaults(func=cmd_flo_agg)

    s = sub.add_parser("flo-score", help="FLoRA score")
    add_store(s)
    s.add_argument("agg_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_flo_score)

    s = sub.add_parser("flo-hetero", help="FLoRA hetero flag")
    add_store(s)
    s.add_argument("--supports-hetero", action="store_true")
    s.set_defaults(func=cmd_flo_hetero)

    s = sub.add_parser("flo-loop", help="FLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["clients", "stack", "agg", "score"]
    )
    s.set_defaults(func=cmd_flo_loop)

    s = sub.add_parser("pun-backbone", help="Punica shared backbone")
    add_store(s)
    s.add_argument("model")
    s.set_defaults(func=cmd_pun_backbone)

    s = sub.add_parser("pun-sgmv", help="Punica SGMV batch")
    add_store(s)
    s.add_argument("backbone_id")
    s.add_argument("adapters", type=int)
    s.set_defaults(func=cmd_pun_sgmv)

    s = sub.add_parser("pun-sched", help="Punica scheduler")
    add_store(s)
    s.add_argument("sgmv_id")
    s.set_defaults(func=cmd_pun_sched)

    s = sub.add_parser("pun-score", help="Punica score")
    add_store(s)
    s.add_argument("sched_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_pun_score)

    s = sub.add_parser("pun-multi", help="Punica multi-tenant flag")
    add_store(s)
    s.add_argument("--multi-tenant", action="store_true")
    s.set_defaults(func=cmd_pun_multi)

    s = sub.add_parser("pun-loop", help="Punica loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["backbone", "sgmv", "sched", "score"]
    )
    s.set_defaults(func=cmd_pun_loop)

    s = sub.add_parser("mla-pipe", help="mLoRA pipeline")
    add_store(s)
    s.add_argument("tasks", type=int)
    s.add_argument("gpus", type=int)
    s.set_defaults(func=cmd_mla_pipe)

    s = sub.add_parser("mla-batch", help="mLoRA BatchLoRA")
    add_store(s)
    s.add_argument("pipe_id")
    s.set_defaults(func=cmd_mla_batch)

    s = sub.add_parser("mla-train", help="mLoRA train")
    add_store(s)
    s.add_argument("batch_id")
    s.set_defaults(func=cmd_mla_train)

    s = sub.add_parser("mla-score", help="mLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mla_score)

    s = sub.add_parser("mla-eff", help="mLoRA efficiency flag")
    add_store(s)
    s.add_argument("--lower-completion-time", action="store_true")
    s.set_defaults(func=cmd_mla_eff)

    s = sub.add_parser("mla-loop", help="mLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["pipe", "batch", "train", "score"]
    )
    s.set_defaults(func=cmd_mla_loop)

    s = sub.add_parser("swl-alloc", help="SwitchLoRA allocate")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_swl_alloc)

    s = sub.add_parser("swl-switch", help="SwitchLoRA switch dims")
    add_store(s)
    s.add_argument("alloc_id")
    s.add_argument("dims", type=int)
    s.set_defaults(func=cmd_swl_switch)

    s = sub.add_parser("swl-train", help="SwitchLoRA train")
    add_store(s)
    s.add_argument("switch_id")
    s.set_defaults(func=cmd_swl_train)

    s = sub.add_parser("swl-score", help="SwitchLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_swl_score)

    s = sub.add_parser("swl-full", help="SwitchLoRA full-rank mimic flag")
    add_store(s)
    s.add_argument("--mimics-fullrank", action="store_true")
    s.set_defaults(func=cmd_swl_full)

    s = sub.add_parser("swl-loop", help="SwitchLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["alloc", "switch", "train", "score"]
    )
    s.set_defaults(func=cmd_swl_loop)

    s = sub.add_parser("col-tune", help="COLA tune LoRA link")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_col_tune)

    s = sub.add_parser("col-knot", help="COLA tie knot")
    add_store(s)
    s.add_argument("tune_id")
    s.set_defaults(func=cmd_col_knot)

    s = sub.add_parser("col-extend", help="COLA extend chain")
    add_store(s)
    s.add_argument("knot_id")
    s.set_defaults(func=cmd_col_extend)

    s = sub.add_parser("col-score", help="COLA score")
    add_store(s)
    s.add_argument("extend_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_col_score)

    s = sub.add_parser("col-gap", help="COLA FT-gap flag")
    add_store(s)
    s.add_argument("--closes-ft-gap", action="store_true")
    s.set_defaults(func=cmd_col_gap)

    s = sub.add_parser("col-loop", help="COLA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tune", "knot", "extend", "score"]
    )
    s.set_defaults(func=cmd_col_loop)

    s = sub.add_parser("dlr-norm", help="DeLoRA normalize")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_dlr_norm)

    s = sub.add_parser("dlr-bound", help="DeLoRA Frobenius bound")
    add_store(s)
    s.add_argument("norm_id")
    s.add_argument("lambda_bound", type=int)
    s.set_defaults(func=cmd_dlr_bound)

    s = sub.add_parser("dlr-train", help="DeLoRA train")
    add_store(s)
    s.add_argument("bound_id")
    s.set_defaults(func=cmd_dlr_train)

    s = sub.add_parser("dlr-score", help="DeLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_dlr_score)

    s = sub.add_parser("dlr-robust", help="DeLoRA robustness flag")
    add_store(s)
    s.add_argument("--hyperparam-robust", action="store_true")
    s.set_defaults(func=cmd_dlr_robust)

    s = sub.add_parser("dlr-loop", help="DeLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["norm", "bound", "train", "score"]
    )
    s.set_defaults(func=cmd_dlr_loop)

    s = sub.add_parser("meo-mini", help="MELoRA mini ensemble")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_minis", type=int)
    s.add_argument("mini_rank", type=int)
    s.set_defaults(func=cmd_meo_mini)

    s = sub.add_parser("meo-diag", help="MELoRA block-diagonal")
    add_store(s)
    s.add_argument("mini_id")
    s.set_defaults(func=cmd_meo_diag)

    s = sub.add_parser("meo-train", help="MELoRA train")
    add_store(s)
    s.add_argument("diag_id")
    s.set_defaults(func=cmd_meo_train)

    s = sub.add_parser("meo-score", help="MELoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_meo_score)

    s = sub.add_parser("meo-rank", help="MELoRA effective-rank flag")
    add_store(s)
    s.add_argument("--higher-effective-rank", action="store_true")
    s.set_defaults(func=cmd_meo_rank)

    s = sub.add_parser("meo-loop", help="MELoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["mini", "diag", "train", "score"]
    )
    s.set_defaults(func=cmd_meo_loop)

    s = sub.add_parser("rlr-warm", help="ReLoRA warm-start")
    add_store(s)
    s.add_argument("task")
    s.add_argument("steps", type=int)
    s.set_defaults(func=cmd_rlr_warm)

    s = sub.add_parser("rlr-merge", help="ReLoRA merge restart")
    add_store(s)
    s.add_argument("warm_id")
    s.set_defaults(func=cmd_rlr_merge)

    s = sub.add_parser("rlr-jagged", help="ReLoRA jagged LR")
    add_store(s)
    s.add_argument("merge_id")
    s.set_defaults(func=cmd_rlr_jagged)

    s = sub.add_parser("rlr-score", help="ReLoRA score")
    add_store(s)
    s.add_argument("jagged_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_rlr_score)

    s = sub.add_parser("rlr-high", help="ReLoRA high-rank flag")
    add_store(s)
    s.add_argument("--high-rank-update", action="store_true")
    s.set_defaults(func=cmd_rlr_high)

    s = sub.add_parser("rlr-loop", help="ReLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["warm", "merge", "jagged", "score"]
    )
    s.set_defaults(func=cmd_rlr_loop)

    s = sub.add_parser("eth-plane", help="ETHER hyperplane alloc")
    add_store(s)
    s.add_argument("task")
    s.add_argument("reflections", type=int)
    s.set_defaults(func=cmd_eth_plane)

    s = sub.add_parser("eth-reflect", help="ETHER reflect")
    add_store(s)
    s.add_argument("plane_id")
    s.set_defaults(func=cmd_eth_reflect)

    s = sub.add_parser("eth-train", help="ETHER train")
    add_store(s)
    s.add_argument("reflect_id")
    s.set_defaults(func=cmd_eth_train)

    s = sub.add_parser("eth-score", help="ETHER score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_eth_score)

    s = sub.add_parser("eth-plus", help="ETHER+ flag")
    add_store(s)
    s.add_argument("--ether-plus", action="store_true")
    s.set_defaults(func=cmd_eth_plus)

    s = sub.add_parser("eth-loop", help="ETHER loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["plane", "reflect", "train", "score"]
    )
    s.set_defaults(func=cmd_eth_loop)

    s = sub.add_parser("lco-concepts", help="LoRA-Composer multi-concept set")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_loras", type=int)
    s.set_defaults(func=cmd_lco_concepts)

    s = sub.add_parser("lco-inject", help="LoRA-Composer inject")
    add_store(s)
    s.add_argument("concepts_id")
    s.set_defaults(func=cmd_lco_inject)

    s = sub.add_parser("lco-isolate", help="LoRA-Composer isolate")
    add_store(s)
    s.add_argument("inject_id")
    s.set_defaults(func=cmd_lco_isolate)

    s = sub.add_parser("lco-score", help="LoRA-Composer score")
    add_store(s)
    s.add_argument("isolate_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lco_score)

    s = sub.add_parser("lco-free", help="LoRA-Composer training-free flag")
    add_store(s)
    s.add_argument("--training-free", action="store_true")
    s.set_defaults(func=cmd_lco_free)

    s = sub.add_parser("lco-loop", help="LoRA-Composer loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["concepts", "inject", "isolate", "score"]
    )
    s.set_defaults(func=cmd_lco_loop)

    s = sub.add_parser("car-compress", help="CARE-LoRA compress activations")
    add_store(s)
    s.add_argument("task")
    s.add_argument("keep_rank", type=int)
    s.set_defaults(func=cmd_car_compress)

    s = sub.add_parser("car-recon", help="CARE-LoRA reconstruct")
    add_store(s)
    s.add_argument("compress_id")
    s.set_defaults(func=cmd_car_recon)

    s = sub.add_parser("car-train", help="CARE-LoRA train")
    add_store(s)
    s.add_argument("recon_id")
    s.set_defaults(func=cmd_car_train)

    s = sub.add_parser("car-score", help="CARE-LoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_car_score)

    s = sub.add_parser("car-mem", help="CARE-LoRA memory flag")
    add_store(s)
    s.add_argument("--activation-saved", action="store_true")
    s.set_defaults(func=cmd_car_mem)

    s = sub.add_parser("car-loop", help="CARE-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["compress", "recon", "train", "score"]
    )
    s.set_defaults(func=cmd_car_loop)

    s = sub.add_parser("lrr-pair", help="LoRA.rar subject-style pairs")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_pairs", type=int)
    s.set_defaults(func=cmd_lrr_pair)

    s = sub.add_parser("lrr-hyper", help="LoRA.rar hypernetwork")
    add_store(s)
    s.add_argument("pair_id")
    s.set_defaults(func=cmd_lrr_hyper)

    s = sub.add_parser("lrr-merge", help="LoRA.rar merge")
    add_store(s)
    s.add_argument("hyper_id")
    s.set_defaults(func=cmd_lrr_merge)

    s = sub.add_parser("lrr-score", help="LoRA.rar score")
    add_store(s)
    s.add_argument("merge_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lrr_score)

    s = sub.add_parser("lrr-fast", help="LoRA.rar realtime flag")
    add_store(s)
    s.add_argument("--realtime-merge", action="store_true")
    s.set_defaults(func=cmd_lrr_fast)

    s = sub.add_parser("lrr-loop", help="LoRA.rar loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["pair", "hyper", "merge", "score"]
    )
    s.set_defaults(func=cmd_lrr_loop)

    s = sub.add_parser("svf-svd", help="SVFT singular-vector factor")
    add_store(s)
    s.add_argument("task")
    s.add_argument("keep", type=int)
    s.set_defaults(func=cmd_svf_svd)

    s = sub.add_parser("svf-sparse", help="SVFT sparse pattern")
    add_store(s)
    s.add_argument("svd_id")
    s.set_defaults(func=cmd_svf_sparse)

    s = sub.add_parser("svf-train", help="SVFT train")
    add_store(s)
    s.add_argument("sparse_id")
    s.set_defaults(func=cmd_svf_train)

    s = sub.add_parser("svf-score", help="SVFT score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_svf_score)

    s = sub.add_parser("svf-geom", help="SVFT geometry flag")
    add_store(s)
    s.add_argument("--weight-dependent", action="store_true")
    s.set_defaults(func=cmd_svf_geom)

    s = sub.add_parser("svf-loop", help="SVFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["svd", "sparse", "train", "score"]
    )
    s.set_defaults(func=cmd_svf_loop)

    s = sub.add_parser("fly-proj", help="FlyLoRA frozen projection")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_fly_proj)

    s = sub.add_parser("fly-topk", help="FlyLoRA top-k experts")
    add_store(s)
    s.add_argument("proj_id")
    s.add_argument("k", type=int)
    s.set_defaults(func=cmd_fly_topk)

    s = sub.add_parser("fly-train", help="FlyLoRA train")
    add_store(s)
    s.add_argument("topk_id")
    s.set_defaults(func=cmd_fly_train)

    s = sub.add_parser("fly-score", help="FlyLoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_fly_score)

    s = sub.add_parser("fly-implicit", help="FlyLoRA implicit-router flag")
    add_store(s)
    s.add_argument("--implicit-router", action="store_true")
    s.set_defaults(func=cmd_fly_implicit)

    s = sub.add_parser("fly-loop", help="FlyLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["proj", "topk", "train", "score"]
    )
    s.set_defaults(func=cmd_fly_loop)

    s = sub.add_parser("nla-basis", help="NOLA random bases")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_basis", type=int)
    s.set_defaults(func=cmd_nla_basis)

    s = sub.add_parser("nla-coeff", help="NOLA coefficients")
    add_store(s)
    s.add_argument("basis_id")
    s.set_defaults(func=cmd_nla_coeff)

    s = sub.add_parser("nla-train", help="NOLA train")
    add_store(s)
    s.add_argument("coeff_id")
    s.set_defaults(func=cmd_nla_train)

    s = sub.add_parser("nla-score", help="NOLA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_nla_score)

    s = sub.add_parser("nla-compact", help="NOLA compact flag")
    add_store(s)
    s.add_argument("--beyond-rank1", action="store_true")
    s.set_defaults(func=cmd_nla_compact)

    s = sub.add_parser("nla-loop", help="NOLA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["basis", "coeff", "train", "score"]
    )
    s.set_defaults(func=cmd_nla_loop)

    s = sub.add_parser("mxl-experts", help="MixLoRA FFN experts")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_experts", type=int)
    s.set_defaults(func=cmd_mxl_experts)

    s = sub.add_parser("mxl-route", help="MixLoRA top-k router")
    add_store(s)
    s.add_argument("experts_id")
    s.add_argument("k", type=int)
    s.set_defaults(func=cmd_mxl_route)

    s = sub.add_parser("mxl-attn", help="MixLoRA attention LoRAs")
    add_store(s)
    s.add_argument("route_id")
    s.set_defaults(func=cmd_mxl_attn)

    s = sub.add_parser("mxl-score", help="MixLoRA score")
    add_store(s)
    s.add_argument("attn_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mxl_score)

    s = sub.add_parser("mxl-balance", help="MixLoRA load-balance flag")
    add_store(s)
    s.add_argument("--load-balance", action="store_true")
    s.set_defaults(func=cmd_mxl_balance)

    s = sub.add_parser("mxl-loop", help="MixLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["experts", "route", "attn", "score"]
    )
    s.set_defaults(func=cmd_mxl_loop)

    s = sub.add_parser("spr-group", help="SuperLoRA grouping")
    add_store(s)
    s.add_argument("task")
    s.add_argument("groups", type=int)
    s.set_defaults(func=cmd_spr_group)

    s = sub.add_parser("spr-fold", help="SuperLoRA fold")
    add_store(s)
    s.add_argument("group_id")
    s.set_defaults(func=cmd_spr_fold)

    s = sub.add_parser("spr-factor", help="SuperLoRA factor")
    add_store(s)
    s.add_argument("fold_id")
    s.set_defaults(func=cmd_spr_factor)

    s = sub.add_parser("spr-score", help="SuperLoRA score")
    add_store(s)
    s.add_argument("factor_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_spr_score)

    s = sub.add_parser("spr-unify", help="SuperLoRA unify flag")
    add_store(s)
    s.add_argument("--unifies-loha-lokr", action="store_true")
    s.set_defaults(func=cmd_spr_unify)

    s = sub.add_parser("spr-loop", help="SuperLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["group", "fold", "factor", "score"]
    )
    s.set_defaults(func=cmd_spr_loop)

    s = sub.add_parser("tld-tie", help="Tied-LoRA weight tying")
    add_store(s)
    s.add_argument("task")
    s.add_argument("layers", type=int)
    s.set_defaults(func=cmd_tld_tie)

    s = sub.add_parser("tld-select", help="Tied-LoRA selective train")
    add_store(s)
    s.add_argument("tie_id")
    s.set_defaults(func=cmd_tld_select)

    s = sub.add_parser("tld-scale", help="Tied-LoRA scale vectors")
    add_store(s)
    s.add_argument("select_id")
    s.set_defaults(func=cmd_tld_scale)

    s = sub.add_parser("tld-score", help="Tied-LoRA score")
    add_store(s)
    s.add_argument("scale_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_tld_score)

    s = sub.add_parser("tld-frac", help="Tied-LoRA fraction flag")
    add_store(s)
    s.add_argument("--fraction-of-lora", action="store_true")
    s.set_defaults(func=cmd_tld_frac)

    s = sub.add_parser("tld-loop", help="Tied-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tie", "select", "scale", "score"]
    )
    s.set_defaults(func=cmd_tld_loop)

    s = sub.add_parser("qal-group", help="QA-LoRA grouping")
    add_store(s)
    s.add_argument("task")
    s.add_argument("groups", type=int)
    s.set_defaults(func=cmd_qal_group)

    s = sub.add_parser("qal-quant", help="QA-LoRA quantize")
    add_store(s)
    s.add_argument("group_id")
    s.add_argument("bits", type=int)
    s.set_defaults(func=cmd_qal_quant)

    s = sub.add_parser("qal-adapt", help="QA-LoRA grouped adapters")
    add_store(s)
    s.add_argument("quant_id")
    s.set_defaults(func=cmd_qal_adapt)

    s = sub.add_parser("qal-score", help="QA-LoRA score")
    add_store(s)
    s.add_argument("adapt_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_qal_score)

    s = sub.add_parser("qal-merge", help="QA-LoRA INT4 merge flag")
    add_store(s)
    s.add_argument("--merge-int4", action="store_true")
    s.set_defaults(func=cmd_qal_merge)

    s = sub.add_parser("qal-loop", help="QA-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["group", "quant", "adapt", "score"]
    )
    s.set_defaults(func=cmd_qal_loop)

    s = sub.add_parser("ulo-space", help="Uni-LoRA subspace")
    add_store(s)
    s.add_argument("task")
    s.add_argument("dim", type=int)
    s.set_defaults(func=cmd_ulo_space)

    s = sub.add_parser("ulo-iso", help="Uni-LoRA isometric projection")
    add_store(s)
    s.add_argument("space_id")
    s.set_defaults(func=cmd_ulo_iso)

    s = sub.add_parser("ulo-vec", help="Uni-LoRA shared vector")
    add_store(s)
    s.add_argument("iso_id")
    s.set_defaults(func=cmd_ulo_vec)

    s = sub.add_parser("ulo-score", help="Uni-LoRA score")
    add_store(s)
    s.add_argument("vec_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ulo_score)

    s = sub.add_parser("ulo-one", help="Uni-LoRA one-vector flag")
    add_store(s)
    s.add_argument("--one-vector", action="store_true")
    s.set_defaults(func=cmd_ulo_one)

    s = sub.add_parser("ulo-loop", help="Uni-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["space", "iso", "vec", "score"]
    )
    s.set_defaults(func=cmd_ulo_loop)

    s = sub.add_parser("bor-row", help="BoRA row magnitudes")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_bor_row)

    s = sub.add_parser("bor-col", help="BoRA column magnitudes")
    add_store(s)
    s.add_argument("row_id")
    s.set_defaults(func=cmd_bor_col)

    s = sub.add_parser("bor-train", help="BoRA train")
    add_store(s)
    s.add_argument("col_id")
    s.set_defaults(func=cmd_bor_train)

    s = sub.add_parser("bor-score", help="BoRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_bor_score)

    s = sub.add_parser("bor-sym", help="BoRA symmetry flag")
    add_store(s)
    s.add_argument("--symmetric", action="store_true")
    s.set_defaults(func=cmd_bor_sym)

    s = sub.add_parser("bor-loop", help="BoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["row", "col", "train", "score"]
    )
    s.set_defaults(func=cmd_bor_loop)

    s = sub.add_parser("qga-weight", help="Q-GaLore INT8 weights")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_qga_weight)

    s = sub.add_parser("qga-proj", help="Q-GaLore INT4 projection")
    add_store(s)
    s.add_argument("weight_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_qga_proj)

    s = sub.add_parser("qga-lazy", help="Q-GaLore lazy SVD")
    add_store(s)
    s.add_argument("proj_id")
    s.set_defaults(func=cmd_qga_lazy)

    s = sub.add_parser("qga-score", help="Q-GaLore score")
    add_store(s)
    s.add_argument("lazy_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_qga_score)

    s = sub.add_parser("qga-mem", help="Q-GaLore memory flag")
    add_store(s)
    s.add_argument("--consumer-gpu", action="store_true")
    s.set_defaults(func=cmd_qga_mem)

    s = sub.add_parser("qga-loop", help="Q-GaLore loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["weight", "proj", "lazy", "score"]
    )
    s.set_defaults(func=cmd_qga_loop)

    s = sub.add_parser("lfw-pool", help="LoRA-Flow skill pool")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n_loras", type=int)
    s.set_defaults(func=cmd_lfw_pool)

    s = sub.add_parser("lfw-gate", help="LoRA-Flow fusion gate")
    add_store(s)
    s.add_argument("pool_id")
    s.set_defaults(func=cmd_lfw_gate)

    s = sub.add_parser("lfw-token", help="LoRA-Flow token weights")
    add_store(s)
    s.add_argument("gate_id")
    s.set_defaults(func=cmd_lfw_token)

    s = sub.add_parser("lfw-score", help="LoRA-Flow score")
    add_store(s)
    s.add_argument("token_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lfw_score)

    s = sub.add_parser("lfw-few", help="LoRA-Flow few-shot flag")
    add_store(s)
    s.add_argument("--few-shot", action="store_true")
    s.set_defaults(func=cmd_lfw_few)

    s = sub.add_parser("lfw-loop", help="LoRA-Flow loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["pool", "gate", "token", "score"]
    )
    s.set_defaults(func=cmd_lfw_loop)

    s = sub.add_parser("ros-rank", help="RoSA low-rank branch")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_ros_rank)

    s = sub.add_parser("ros-sparse", help="RoSA sparse residual")
    add_store(s)
    s.add_argument("rank_id")
    s.set_defaults(func=cmd_ros_sparse)

    s = sub.add_parser("ros-train", help="RoSA train")
    add_store(s)
    s.add_argument("sparse_id")
    s.set_defaults(func=cmd_ros_train)

    s = sub.add_parser("ros-score", help="RoSA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ros_score)

    s = sub.add_parser("ros-fft", help="RoSA FFT-recovery flag")
    add_store(s)
    s.add_argument("--matches-fft", action="store_true")
    s.set_defaults(func=cmd_ros_fft)

    s = sub.add_parser("ros-loop", help="RoSA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["rank", "sparse", "train", "score"]
    )
    s.set_defaults(func=cmd_ros_loop)

    s = sub.add_parser("abb-left", help="ABBA left factor")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_abb_left)

    s = sub.add_parser("abb-right", help="ABBA right factor")
    add_store(s)
    s.add_argument("left_id")
    s.set_defaults(func=cmd_abb_right)

    s = sub.add_parser("abb-hadamard", help="ABBA Hadamard")
    add_store(s)
    s.add_argument("right_id")
    s.set_defaults(func=cmd_abb_hadamard)

    s = sub.add_parser("abb-score", help="ABBA score")
    add_store(s)
    s.add_argument("hadamard_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_abb_score)

    s = sub.add_parser("abb-expr", help="ABBA expressivity flag")
    add_store(s)
    s.add_argument("--expressive", action="store_true")
    s.set_defaults(func=cmd_abb_expr)

    s = sub.add_parser("abb-loop", help="ABBA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["left", "right", "hadamard", "score"]
    )
    s.set_defaults(func=cmd_abb_loop)

    s = sub.add_parser("bha-split", help="BoHA block split")
    add_store(s)
    s.add_argument("task")
    s.add_argument("blocks", type=int)
    s.set_defaults(func=cmd_bha_split)

    s = sub.add_parser("bha-hadamard", help="BoHA per-block Hadamard")
    add_store(s)
    s.add_argument("split_id")
    s.set_defaults(func=cmd_bha_hadamard)

    s = sub.add_parser("bha-train", help="BoHA train")
    add_store(s)
    s.add_argument("hadamard_id")
    s.set_defaults(func=cmd_bha_train)

    s = sub.add_parser("bha-score", help="BoHA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_bha_score)

    s = sub.add_parser("bha-local", help="BoHA localized-rank flag")
    add_store(s)
    s.add_argument("--localized", action="store_true")
    s.set_defaults(func=cmd_bha_local)

    s = sub.add_parser("bha-loop", help="BoHA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["split", "hadamard", "train", "score"]
    )
    s.set_defaults(func=cmd_bha_loop)

    s = sub.add_parser("smo-struct", help="SMoA subspaces")
    add_store(s)
    s.add_argument("task")
    s.add_argument("subspaces", type=int)
    s.set_defaults(func=cmd_smo_struct)

    s = sub.add_parser("smo-mod", help="SMoA modulation")
    add_store(s)
    s.add_argument("struct_id")
    s.set_defaults(func=cmd_smo_mod)

    s = sub.add_parser("smo-train", help="SMoA train")
    add_store(s)
    s.add_argument("mod_id")
    s.set_defaults(func=cmd_smo_train)

    s = sub.add_parser("smo-score", help="SMoA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_smo_score)

    s = sub.add_parser("smo-rank", help="SMoA high-rank flag")
    add_store(s)
    s.add_argument("--high-rank", action="store_true")
    s.set_defaults(func=cmd_smo_rank)

    s = sub.add_parser("smo-loop", help="SMoA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["struct", "mod", "train", "score"]
    )
    s.set_defaults(func=cmd_smo_loop)

    s = sub.add_parser("glo-prompt", help="GLoRA prompt module")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_glo_prompt)

    s = sub.add_parser("glo-scale", help="GLoRA scale")
    add_store(s)
    s.add_argument("prompt_id")
    s.set_defaults(func=cmd_glo_scale)

    s = sub.add_parser("glo-search", help="GLoRA layer search")
    add_store(s)
    s.add_argument("scale_id")
    s.set_defaults(func=cmd_glo_search)

    s = sub.add_parser("glo-score", help="GLoRA score")
    add_store(s)
    s.add_argument("search_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_glo_score)

    s = sub.add_parser("glo-zero", help="GLoRA zero-infer flag")
    add_store(s)
    s.add_argument("--zero-infer", action="store_true")
    s.set_defaults(func=cmd_glo_zero)

    s = sub.add_parser("glo-loop", help="GLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["prompt", "scale", "search", "score"]
    )
    s.set_defaults(func=cmd_glo_loop)

    s = sub.add_parser("plr-stage", help="PeriodicLoRA stage")
    add_store(s)
    s.add_argument("task")
    s.add_argument("stages", type=int)
    s.set_defaults(func=cmd_plr_stage)

    s = sub.add_parser("plr-merge", help="PeriodicLoRA merge into W")
    add_store(s)
    s.add_argument("stage_id")
    s.set_defaults(func=cmd_plr_merge)

    s = sub.add_parser("plr-reset", help="PeriodicLoRA reinit")
    add_store(s)
    s.add_argument("merge_id")
    s.set_defaults(func=cmd_plr_reset)

    s = sub.add_parser("plr-score", help="PeriodicLoRA score")
    add_store(s)
    s.add_argument("reset_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_plr_score)

    s = sub.add_parser("plr-rank", help="PeriodicLoRA accumulated-rank flag")
    add_store(s)
    s.add_argument("--accum-rank", action="store_true")
    s.set_defaults(func=cmd_plr_rank)

    s = sub.add_parser("plr-loop", help="PeriodicLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["stage", "merge", "reset", "score"]
    )
    s.set_defaults(func=cmd_plr_loop)

    s = sub.add_parser("hir-base", help="HiRA freeze W0")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_hir_base)

    s = sub.add_parser("hir-factors", help="HiRA A, B factors")
    add_store(s)
    s.add_argument("base_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_hir_factors)

    s = sub.add_parser("hir-hadamard", help="HiRA W0 ⊙ (BA)")
    add_store(s)
    s.add_argument("factors_id")
    s.set_defaults(func=cmd_hir_hadamard)

    s = sub.add_parser("hir-score", help="HiRA score")
    add_store(s)
    s.add_argument("hadamard_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_hir_score)

    s = sub.add_parser("hir-merge", help="HiRA merge-into-W0 flag")
    add_store(s)
    s.add_argument("--zero-infer", action="store_true")
    s.set_defaults(func=cmd_hir_merge)

    s = sub.add_parser("hir-loop", help="HiRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["base", "factors", "hadamard", "score"]
    )
    s.set_defaults(func=cmd_hir_loop)

    s = sub.add_parser("cnl-pack", help="PLoRA concurrent pack")
    add_store(s)
    s.add_argument("task")
    s.add_argument("adapters", type=int)
    s.set_defaults(func=cmd_cnl_pack)

    s = sub.add_parser("cnl-fuse", help="PLoRA concurrent fuse")
    add_store(s)
    s.add_argument("pack_id")
    s.set_defaults(func=cmd_cnl_fuse)

    s = sub.add_parser("cnl-train", help="PLoRA concurrent train")
    add_store(s)
    s.add_argument("fuse_id")
    s.set_defaults(func=cmd_cnl_train)

    s = sub.add_parser("cnl-score", help="PLoRA concurrent score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_cnl_score)

    s = sub.add_parser("cnl-hw", help="PLoRA concurrent util flag")
    add_store(s)
    s.add_argument("--better-util", action="store_true")
    s.set_defaults(func=cmd_cnl_hw)

    s = sub.add_parser("cnl-loop", help="PLoRA concurrent loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["pack", "fuse", "train", "score"]
    )
    s.set_defaults(func=cmd_cnl_loop)

    s = sub.add_parser("llr-window", help="LongLoRA long-context window")
    add_store(s)
    s.add_argument("task")
    s.add_argument("ctx_len", type=int)
    s.set_defaults(func=cmd_llr_window)

    s = sub.add_parser("llr-shift", help="LongLoRA S2-Attn shift")
    add_store(s)
    s.add_argument("window_id")
    s.set_defaults(func=cmd_llr_shift)

    s = sub.add_parser("llr-lora", help="LongLoRA adapter")
    add_store(s)
    s.add_argument("shift_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_llr_lora)

    s = sub.add_parser("llr-score", help="LongLoRA score")
    add_store(s)
    s.add_argument("lora_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_llr_score)

    s = sub.add_parser("llr-sparse", help="LongLoRA sparse-train flag")
    add_store(s)
    s.add_argument("--sparse-train", action="store_true")
    s.set_defaults(func=cmd_llr_sparse)

    s = sub.add_parser("llr-loop", help="LongLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["window", "shift", "lora", "score"]
    )
    s.set_defaults(func=cmd_llr_loop)

    s = sub.add_parser("lis-layers", help="LISA layer set")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n", type=int)
    s.set_defaults(func=cmd_lis_layers)

    s = sub.add_parser("lis-sample", help="LISA importance sample")
    add_store(s)
    s.add_argument("layers_id")
    s.set_defaults(func=cmd_lis_sample)

    s = sub.add_parser("lis-unfreeze", help="LISA unfreeze sampled layers")
    add_store(s)
    s.add_argument("sample_id")
    s.set_defaults(func=cmd_lis_unfreeze)

    s = sub.add_parser("lis-score", help="LISA score")
    add_store(s)
    s.add_argument("unfreeze_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lis_score)

    s = sub.add_parser("lis-memory", help="LISA optimizer-memory flag")
    add_store(s)
    s.add_argument("--less-opt", action="store_true")
    s.set_defaults(func=cmd_lis_memory)

    s = sub.add_parser("lis-loop", help="LISA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["layers", "sample", "unfreeze", "score"]
    )
    s.set_defaults(func=cmd_lis_loop)

    s = sub.add_parser("nlr-landmark", help="NLoRA Nyström landmarks")
    add_store(s)
    s.add_argument("task")
    s.add_argument("k", type=int)
    s.set_defaults(func=cmd_nlr_landmark)

    s = sub.add_parser("nlr-nystrom", help="NLoRA Nyström sketch")
    add_store(s)
    s.add_argument("landmark_id")
    s.set_defaults(func=cmd_nlr_nystrom)

    s = sub.add_parser("nlr-init", help="NLoRA init from sketch")
    add_store(s)
    s.add_argument("nystrom_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_nlr_init)

    s = sub.add_parser("nlr-score", help="NLoRA score")
    add_store(s)
    s.add_argument("init_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_nlr_score)

    s = sub.add_parser("nlr-cheap", help="NLoRA cheaper-than-SVD flag")
    add_store(s)
    s.add_argument("--cheaper-svd", action="store_true")
    s.set_defaults(func=cmd_nlr_cheap)

    s = sub.add_parser("nlr-loop", help="NLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["landmark", "nystrom", "init", "score"]
    )
    s.set_defaults(func=cmd_nlr_loop)

    s = sub.add_parser("rsa-subspace", help="ROSA random subspace")
    add_store(s)
    s.add_argument("task")
    s.add_argument("dim", type=int)
    s.set_defaults(func=cmd_rsa_subspace)

    s = sub.add_parser("rsa-project", help="ROSA project into subspace")
    add_store(s)
    s.add_argument("subspace_id")
    s.set_defaults(func=cmd_rsa_project)

    s = sub.add_parser("rsa-train", help="ROSA train in subspace")
    add_store(s)
    s.add_argument("project_id")
    s.set_defaults(func=cmd_rsa_train)

    s = sub.add_parser("rsa-score", help="ROSA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_rsa_score)

    s = sub.add_parser("rsa-express", help="ROSA expressiveness flag")
    add_store(s)
    s.add_argument("--more-expressive", action="store_true")
    s.set_defaults(func=cmd_rsa_express)

    s = sub.add_parser("rsa-loop", help="ROSA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["subspace", "project", "train", "score"]
    )
    s.set_defaults(func=cmd_rsa_loop)

    s = sub.add_parser("hra-house", help="HRA Householder vectors")
    add_store(s)
    s.add_argument("task")
    s.add_argument("n", type=int)
    s.set_defaults(func=cmd_hra_house)

    s = sub.add_parser("hra-reflect", help="HRA compose reflections")
    add_store(s)
    s.add_argument("house_id")
    s.set_defaults(func=cmd_hra_reflect)

    s = sub.add_parser("hra-train", help="HRA train adapter")
    add_store(s)
    s.add_argument("reflect_id")
    s.set_defaults(func=cmd_hra_train)

    s = sub.add_parser("hra-score", help="HRA score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_hra_score)

    s = sub.add_parser("hra-ortho", help="HRA orthogonal-stable flag")
    add_store(s)
    s.add_argument("--ortho-stable", action="store_true")
    s.set_defaults(func=cmd_hra_ortho)

    s = sub.add_parser("hra-loop", help="HRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["house", "reflect", "train", "score"]
    )
    s.set_defaults(func=cmd_hra_loop)

    s = sub.add_parser("hyb-lora", help="Hybrid PEFT LoRA-GA branch")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_hyb_lora)

    s = sub.add_parser("hyb-boft", help="Hybrid PEFT BOFT branch")
    add_store(s)
    s.add_argument("lora_id")
    s.set_defaults(func=cmd_hyb_boft)

    s = sub.add_parser("hyb-fuse", help="Hybrid PEFT fuse branches")
    add_store(s)
    s.add_argument("boft_id")
    s.set_defaults(func=cmd_hyb_fuse)

    s = sub.add_parser("hyb-score", help="Hybrid PEFT score")
    add_store(s)
    s.add_argument("fuse_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_hyb_score)

    s = sub.add_parser("hyb-stable", help="Hybrid PEFT stability flag")
    add_store(s)
    s.add_argument("--more-stable", action="store_true")
    s.set_defaults(func=cmd_hyb_stable)

    s = sub.add_parser("hyb-loop", help="Hybrid PEFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["lora", "boft", "fuse", "score"]
    )
    s.set_defaults(func=cmd_hyb_loop)

    s = sub.add_parser("lrt-tensor", help="LoRTA unified tensor")
    add_store(s)
    s.add_argument("task")
    s.add_argument("order", type=int)
    s.set_defaults(func=cmd_lrt_tensor)

    s = sub.add_parser("lrt-cp", help="LoRTA CP decompose")
    add_store(s)
    s.add_argument("tensor_id")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_lrt_cp)

    s = sub.add_parser("lrt-share", help="LoRTA share factors")
    add_store(s)
    s.add_argument("cp_id")
    s.set_defaults(func=cmd_lrt_share)

    s = sub.add_parser("lrt-score", help="LoRTA score")
    add_store(s)
    s.add_argument("share_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lrt_score)

    s = sub.add_parser("lrt-compact", help="LoRTA fewer-params flag")
    add_store(s)
    s.add_argument("--fewer-params", action="store_true")
    s.set_defaults(func=cmd_lrt_compact)

    s = sub.add_parser("lrt-loop", help="LoRTA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tensor", "cp", "share", "score"]
    )
    s.set_defaults(func=cmd_lrt_loop)

    s = sub.add_parser("clo-route", help="C-LoRA shared route")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_clo_route)

    s = sub.add_parser("clo-task", help="C-LoRA bind task")
    add_store(s)
    s.add_argument("route_id")
    s.set_defaults(func=cmd_clo_task)

    s = sub.add_parser("clo-ortho", help="C-LoRA orthogonality")
    add_store(s)
    s.add_argument("task_id")
    s.set_defaults(func=cmd_clo_ortho)

    s = sub.add_parser("clo-score", help="C-LoRA score")
    add_store(s)
    s.add_argument("ortho_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_clo_score)

    s = sub.add_parser("clo-forget", help="C-LoRA less-forgetting flag")
    add_store(s)
    s.add_argument("--less-forget", action="store_true")
    s.set_defaults(func=cmd_clo_forget)

    s = sub.add_parser("clo-loop", help="C-LoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["route", "task", "ortho", "score"]
    )
    s.set_defaults(func=cmd_clo_loop)

    s = sub.add_parser("alo-init", help="ALoRA equal-rank init")
    add_store(s)
    s.add_argument("task")
    s.add_argument("rank", type=int)
    s.set_defaults(func=cmd_alo_init)

    s = sub.add_parser("alo-ablate", help="ALoRA AB-LoRA importance")
    add_store(s)
    s.add_argument("init_id")
    s.set_defaults(func=cmd_alo_ablate)

    s = sub.add_parser("alo-prune", help="ALoRA prune and reallocate")
    add_store(s)
    s.add_argument("ablate_id")
    s.set_defaults(func=cmd_alo_prune)

    s = sub.add_parser("alo-score", help="ALoRA score")
    add_store(s)
    s.add_argument("prune_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_alo_score)

    s = sub.add_parser("alo-realloc", help="ALoRA dynamic-realloc flag")
    add_store(s)
    s.add_argument("--dynamic", action="store_true")
    s.set_defaults(func=cmd_alo_realloc)

    s = sub.add_parser("alo-loop", help="ALoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["init", "ablate", "prune", "score"]
    )
    s.set_defaults(func=cmd_alo_loop)

    s = sub.add_parser("lnt-attn", help="LN Tuning attention LN select")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_lnt_attn)

    s = sub.add_parser("lnt-scale", help="LN Tuning scale (gamma)")
    add_store(s)
    s.add_argument("attn_id")
    s.set_defaults(func=cmd_lnt_scale)

    s = sub.add_parser("lnt-train", help="LN Tuning train")
    add_store(s)
    s.add_argument("scale_id")
    s.set_defaults(func=cmd_lnt_train)

    s = sub.add_parser("lnt-score", help="LN Tuning score")
    add_store(s)
    s.add_argument("train_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lnt_score)

    s = sub.add_parser("lnt-cheap", help="LN Tuning cheaper-than-LoRA flag")
    add_store(s)
    s.add_argument("--cheaper-than-lora", action="store_true")
    s.set_defaults(func=cmd_lnt_cheap)

    s = sub.add_parser("lnt-loop", help="LN Tuning loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["attn", "scale", "train", "score"]
    )
    s.set_defaults(func=cmd_lnt_loop)

    s = sub.add_parser("lfu-split", help="LoRAFusion graph split")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_lfu_split)

    s = sub.add_parser("lfu-fuse", help="LoRAFusion kernel fuse")
    add_store(s)
    s.add_argument("split_id")
    s.set_defaults(func=cmd_lfu_fuse)

    s = sub.add_parser("lfu-batch", help="LoRAFusion multi-job batch")
    add_store(s)
    s.add_argument("fuse_id")
    s.add_argument("jobs", type=int)
    s.set_defaults(func=cmd_lfu_batch)

    s = sub.add_parser("lfu-score", help="LoRAFusion score")
    add_store(s)
    s.add_argument("batch_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_lfu_score)

    s = sub.add_parser("lfu-speed", help="LoRAFusion faster-than-mLoRA flag")
    add_store(s)
    s.add_argument("--faster-than-mlora", action="store_true")
    s.set_defaults(func=cmd_lfu_speed)

    s = sub.add_parser("lfu-loop", help="LoRAFusion loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["split", "fuse", "batch", "score"]
    )
    s.set_defaults(func=cmd_lfu_loop)

    s = sub.add_parser("ter-tucker", help="TeRA tensorize ΔW")
    add_store(s)
    s.add_argument("task")
    s.add_argument("order", type=int)
    s.set_defaults(func=cmd_ter_tucker)

    s = sub.add_parser("ter-freeze", help="TeRA freeze random factors")
    add_store(s)
    s.add_argument("tucker_id")
    s.set_defaults(func=cmd_ter_freeze)

    s = sub.add_parser("ter-scale", help="TeRA per-layer scale vectors")
    add_store(s)
    s.add_argument("freeze_id")
    s.set_defaults(func=cmd_ter_scale)

    s = sub.add_parser("ter-score", help="TeRA score")
    add_store(s)
    s.add_argument("scale_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ter_score)

    s = sub.add_parser("ter-highrank", help="TeRA high-rank-cheap flag")
    add_store(s)
    s.add_argument("--high-rank-cheap", action="store_true")
    s.set_defaults(func=cmd_ter_highrank)

    s = sub.add_parser("ter-loop", help="TeRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tucker", "freeze", "scale", "score"]
    )
    s.set_defaults(func=cmd_ter_loop)

    s = sub.add_parser("tnl-stack", help="TensLoRA stack LoRA updates")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_tnl_stack)

    s = sub.add_parser("tnl-tucker", help="TensLoRA Tucker factor")
    add_store(s)
    s.add_argument("stack_id")
    s.add_argument("ranks", type=int)
    s.set_defaults(func=cmd_tnl_tucker)

    s = sub.add_parser("tnl-mode", help="TensLoRA per-mode ranks")
    add_store(s)
    s.add_argument("tucker_id")
    s.set_defaults(func=cmd_tnl_mode)

    s = sub.add_parser("tnl-score", help="TensLoRA score")
    add_store(s)
    s.add_argument("mode_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_tnl_score)

    s = sub.add_parser("tnl-budget", help="TensLoRA mode-specific budget flag")
    add_store(s)
    s.add_argument("--mode-specific", action="store_true")
    s.set_defaults(func=cmd_tnl_budget)

    s = sub.add_parser("tnl-loop", help="TensLoRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["stack", "tucker", "mode", "score"]
    )
    s.set_defaults(func=cmd_tnl_loop)

    s = sub.add_parser("azt-tt", help="AdaZeta tensor-train adapter")
    add_store(s)
    s.add_argument("task")
    s.add_argument("cores", type=int)
    s.set_defaults(func=cmd_azt_tt)

    s = sub.add_parser("azt-ff", help="AdaZeta fast-forward contraction")
    add_store(s)
    s.add_argument("tt_id")
    s.set_defaults(func=cmd_azt_ff)

    s = sub.add_parser("azt-query", help="AdaZeta adaptive ZO queries")
    add_store(s)
    s.add_argument("ff_id")
    s.set_defaults(func=cmd_azt_query)

    s = sub.add_parser("azt-score", help="AdaZeta score")
    add_store(s)
    s.add_argument("query_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_azt_score)

    s = sub.add_parser("azt-mem", help="AdaZeta ZO-memory flag")
    add_store(s)
    s.add_argument("--zo-memory", action="store_true")
    s.set_defaults(func=cmd_azt_mem)

    s = sub.add_parser("azt-loop", help="AdaZeta loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tt", "ff", "query", "score"]
    )
    s.set_defaults(func=cmd_azt_loop)

    s = sub.add_parser("fct-tensor", help="FacT 3D increment tensor")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_fct_tensor)

    s = sub.add_parser("fct-tt", help="FacT Tensor-Train factors")
    add_store(s)
    s.add_argument("tensor_id")
    s.set_defaults(func=cmd_fct_tt)

    s = sub.add_parser("fct-tucker", help="FacT Tucker factors")
    add_store(s)
    s.add_argument("tt_id")
    s.set_defaults(func=cmd_fct_tucker)

    s = sub.add_parser("fct-score", help="FacT score")
    add_store(s)
    s.add_argument("tucker_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_fct_score)

    s = sub.add_parser("fct-tiny", help="FacT tiny-params flag")
    add_store(s)
    s.add_argument("--tiny-params", action="store_true")
    s.set_defaults(func=cmd_fct_tiny)

    s = sub.add_parser("fct-loop", help="FacT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["tensor", "tt", "tucker", "score"]
    )
    s.set_defaults(func=cmd_fct_loop)

    s = sub.add_parser("ltr-stack", help="LoTR stack Q/V across depth")
    add_store(s)
    s.add_argument("task")
    s.add_argument("layers", type=int)
    s.set_defaults(func=cmd_ltr_stack)

    s = sub.add_parser("ltr-core", help="LoTR shared core tensor")
    add_store(s)
    s.add_argument("stack_id")
    s.set_defaults(func=cmd_ltr_core)

    s = sub.add_parser("ltr-share", help="LoTR share left/right factors")
    add_store(s)
    s.add_argument("core_id")
    s.set_defaults(func=cmd_ltr_share)

    s = sub.add_parser("ltr-score", help="LoTR score")
    add_store(s)
    s.add_argument("share_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ltr_score)

    s = sub.add_parser("ltr-deep", help="LoTR better-for-deep flag")
    add_store(s)
    s.add_argument("--better-for-deep", action="store_true")
    s.set_defaults(func=cmd_ltr_deep)

    s = sub.add_parser("ltr-loop", help="LoTR loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["stack", "core", "share", "score"]
    )
    s.set_defaults(func=cmd_ltr_loop)

    s = sub.add_parser("cra-mha", help="CaRA MHA tensor")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_cra_mha)

    s = sub.add_parser("cra-ffn", help="CaRA FFN tensor")
    add_store(s)
    s.add_argument("mha_id")
    s.set_defaults(func=cmd_cra_ffn)

    s = sub.add_parser("cra-cpd", help="CaRA CP decompose")
    add_store(s)
    s.add_argument("ffn_id")
    s.set_defaults(func=cmd_cra_cpd)

    s = sub.add_parser("cra-score", help="CaRA score")
    add_store(s)
    s.add_argument("cpd_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_cra_score)

    s = sub.add_parser("cra-heads", help="CaRA head-mode flag")
    add_store(s)
    s.add_argument("--head-mode", action="store_true")
    s.set_defaults(func=cmd_cra_heads)

    s = sub.add_parser("cra-loop", help="CaRA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["mha", "ffn", "cpd", "score"]
    )
    s.set_defaults(func=cmd_cra_loop)

    s = sub.add_parser("ltt-adp", help="LoRETTA adapter branch")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_ltt_adp)

    s = sub.add_parser("ltt-rep", help="LoRETTA reparam branch")
    add_store(s)
    s.add_argument("adp_id")
    s.set_defaults(func=cmd_ltt_rep)

    s = sub.add_parser("ltt-tt", help="LoRETTA tensor-train cores")
    add_store(s)
    s.add_argument("rep_id")
    s.set_defaults(func=cmd_ltt_tt)

    s = sub.add_parser("ltt-score", help="LoRETTA score")
    add_store(s)
    s.add_argument("tt_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_ltt_score)

    s = sub.add_parser("ltt-tiny", help="LoRETTA sub-MB flag")
    add_store(s)
    s.add_argument("--sub-mb", action="store_true")
    s.set_defaults(func=cmd_ltt_tiny)

    s = sub.add_parser("ltt-loop", help="LoRETTA loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["adp", "rep", "tt", "score"]
    )
    s.set_defaults(func=cmd_ltt_loop)

    s = sub.add_parser("c3a-kernel", help="C3A convolution kernel")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_c3a_kernel)

    s = sub.add_parser("c3a-circ", help="C3A circulant lift")
    add_store(s)
    s.add_argument("kernel_id")
    s.set_defaults(func=cmd_c3a_circ)

    s = sub.add_parser("c3a-fft", help="C3A FFT multiply")
    add_store(s)
    s.add_argument("circ_id")
    s.set_defaults(func=cmd_c3a_fft)

    s = sub.add_parser("c3a-score", help="C3A score")
    add_store(s)
    s.add_argument("fft_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_c3a_score)

    s = sub.add_parser("c3a-rank", help="C3A high-rank flag")
    add_store(s)
    s.add_argument("--high-rank", action="store_true")
    s.set_defaults(func=cmd_c3a_rank)

    s = sub.add_parser("c3a-loop", help="C3A loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["kernel", "circ", "fft", "score"]
    )
    s.set_defaults(func=cmd_c3a_loop)

    s = sub.add_parser("bof-block", help="BOFT butterfly block")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_bof_block)

    s = sub.add_parser("bof-orth", help="BOFT orthogonal factor")
    add_store(s)
    s.add_argument("block_id")
    s.set_defaults(func=cmd_bof_orth)

    s = sub.add_parser("bof-butter", help="BOFT butterfly factorize")
    add_store(s)
    s.add_argument("orth_id")
    s.set_defaults(func=cmd_bof_butter)

    s = sub.add_parser("bof-score", help="BOFT score")
    add_store(s)
    s.add_argument("butter_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_bof_score)

    s = sub.add_parser("bof-full", help="BOFT full-orthogonal flag")
    add_store(s)
    s.add_argument("--full-rank", action="store_true")
    s.set_defaults(func=cmd_bof_full)

    s = sub.add_parser("bof-loop", help="BOFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["block", "orth", "butter", "score"]
    )
    s.set_defaults(func=cmd_bof_loop)

    s = sub.add_parser("sdt-dim", help="SDT sparse SSM dimension")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_sdt_dim)

    s = sub.add_parser("sdt-mask", help="SDT sparse mask")
    add_store(s)
    s.add_argument("dim_id")
    s.set_defaults(func=cmd_sdt_mask)

    s = sub.add_parser("sdt-tune", help="SDT sparse dimension tune")
    add_store(s)
    s.add_argument("mask_id")
    s.set_defaults(func=cmd_sdt_tune)

    s = sub.add_parser("sdt-score", help="SDT score")
    add_store(s)
    s.add_argument("tune_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_sdt_score)

    s = sub.add_parser("sdt-ssm", help="SDT SSM-targeted flag")
    add_store(s)
    s.add_argument("--ssm-only", action="store_true")
    s.set_defaults(func=cmd_sdt_ssm)

    s = sub.add_parser("sdt-loop", help="SDT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["dim", "mask", "tune", "score"]
    )
    s.set_defaults(func=cmd_sdt_loop)

    s = sub.add_parser("mef-adapt", help="MEFT sparse adapter")
    add_store(s)
    s.add_argument("task")
    s.set_defaults(func=cmd_mef_adapt)

    s = sub.add_parser("mef-route", help="MEFT MoE router")
    add_store(s)
    s.add_argument("adapt_id")
    s.set_defaults(func=cmd_mef_route)

    s = sub.add_parser("mef-fetch", help="MEFT sparse neuron fetch")
    add_store(s)
    s.add_argument("route_id")
    s.set_defaults(func=cmd_mef_fetch)

    s = sub.add_parser("mef-score", help="MEFT score")
    add_store(s)
    s.add_argument("fetch_id")
    s.add_argument("score", type=int)
    s.set_defaults(func=cmd_mef_score)

    s = sub.add_parser("mef-cpu", help="MEFT CPU-offload flag")
    add_store(s)
    s.add_argument("--cpu-offload", action="store_true")
    s.set_defaults(func=cmd_mef_cpu)

    s = sub.add_parser("mef-loop", help="MEFT loop plan")
    add_store(s)
    s.add_argument(
        "phase", choices=["adapt", "route", "fetch", "score"]
    )
    s.set_defaults(func=cmd_mef_loop)

    return p


def cmd_purge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.purge_by_provenance(
            untrusted_sources=args.source,
            untrusted_agents=args.agent,
            actor=args.actor,
            ts=args.now,
            dry_run=not args.execute,
        )
    )
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.diff_stores(args.other))
    return 0


def cmd_hygiene(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hygiene_candidates(
            now=args.now, unused_before=args.unused_before, limit=args.limit
        )
    )
    return 0


def cmd_entangled(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.entangled_suspects(
            seed_ids=args.seed or None,
            untrusted_sources=args.source or None,
            untrusted_agents=args.agent or None,
            limit=args.limit,
        )
    )
    return 0


def cmd_forget_check(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.forget_compliance(
        consumer_scope=args.scope,
        subject_id=args.subject_id,
        entry_ids=args.entry_ids or None,
        probe_query=args.probe_query,
        forbidden_substrings=args.forbid or None,
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_lineage(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lineage(args.entry_id))
    return 0


def cmd_belief_at(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.belief_at(args.as_of, consumer_scope=args.scope, query=args.query)
    )
    return 0


def cmd_conflicts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.conflict_surface(body_max_chars=args.body_max))
    return 0


def cmd_injection_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.injection_scan(
            entry_ids=args.entry_ids or None, limit=args.limit
        )
    )
    return 0


def cmd_budget_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.select_budget_plan(
            args.query,
            consumer_scope=args.scope,
            budget=args.budget,
            withhold_injection_suspects=args.withhold_injection,
        )
    )
    return 0


def cmd_seal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.store_seal())
    return 0


def cmd_verify_seal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    seal = json.loads(Path(args.seal_file).read_text(encoding="utf-8"))
    report = stele.verify_seal(seal)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_receipt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.attribution_receipt(args.entry_id))
    return 0


def cmd_replay_check(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.replay_consistency()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_lifecycle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lifecycle_inventory(
            now=args.now, hot_days=args.hot_days, warm_days=args.warm_days
        )
    )
    return 0


def cmd_revoke_key(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    _print(
        stele.revoke_by_key(
            args.conflict_key,
            evidence=evidence,
            actor=args.actor,
            ts=args.now,
            keep_id=args.keep_id,
        )
    )
    return 0


def cmd_pack_seal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pack_seal(args.pack_dir))
    return 0


def cmd_verify_pack_seal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    seal = json.loads(Path(args.seal_file).read_text(encoding="utf-8"))
    report = stele.verify_pack_seal(args.pack_dir, seal)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_explain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.search_explain(
            args.query,
            consumer_scope=args.scope,
            budget=args.budget,
            lifecycle_tiers=args.tier or None,
        )
    )
    return 0


def cmd_blast(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.blast_radius(args.entry_id, max_depth=args.depth))
    return 0


def cmd_merge_classify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.merge_classify(
            args.entry_a,
            args.entry_b,
            merge_threshold=args.merge_threshold,
            relate_threshold=args.relate_threshold,
        )
    )
    return 0


def cmd_path_trust(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.path_trust(
            args.entry_id,
            trusted_sources=args.source or None,
            max_depth=args.depth,
        )
    )
    return 0


def cmd_journal_chain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.verify_journal_chain()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_spread(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spread_activate(
            args.seed,
            max_hops=args.hops,
            decay=args.decay,
            lateral_inhibit=args.inhibit,
        )
    )
    return 0


def cmd_density(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.connection_density(args.entry_id))
    return 0


def cmd_retention(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.retention_score(
            args.entry_id, now=args.now, half_life_days=args.half_life
        )
    )
    return 0


def cmd_health(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.health_report(now=args.now)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_release_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.release_gate(
        expected_head=args.expected_head,
        allow_contested=args.allow_contested,
        allow_injection_suspects=args.allow_injection,
        allow_stale=not args.block_stale,
        now=args.now,
        issue_receipt=args.issue_receipt,
        record_abstain=args.record_abstain,
        actor=args.actor,
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_rebuild_index(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rebuild_sqlite_index())
    return 0


def cmd_search_sqlite(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.search_sqlite(
            args.query,
            states=args.state or None,
            scopes=args.scope_filter or None,
            cue=args.cue,
            limit=args.limit,
        )
    )
    return 0


def cmd_verify_import(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.verify_import(args.pack)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_decisions(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.list_decision_receipts(limit=args.limit))
    return 0


def cmd_lineage_trust(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lineage_trust(args.entry_id, max_depth=args.max_depth))
    return 0


def cmd_record_exec(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.record_execution(
            args.step,
            subject_id=args.subject_id,
            actor=args.actor,
            ts=args.now,
        )
    )
    return 0


def cmd_verify_exec(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.verify_execution(args.step, subject_id=args.subject_id)
    _print(report)
    return 0 if report.get("allowed") else 1


def cmd_authority_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.authority_gate(args.entry_ids, action_risk=args.action_risk)
    _print(report)
    return 0 if report.get("allowed") else 1


def cmd_claim_closure(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.claim_closure(
        args.claim_ids, expected_head=args.expected_head
    )
    _print(report)
    return 0 if report.get("closed") else 1


def cmd_cascade(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cascade_impact(args.fault_id, max_depth=args.max_depth))
    return 0


def cmd_withdraw_cascade(args: argparse.Namespace) -> int:
    import json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    evidence = json.loads(args.evidence_json)
    report = stele.withdraw_cascade(
        args.fault_id,
        evidence=evidence,
        actor=args.actor,
        ts=args.now,
        max_depth=args.max_depth,
    )
    _print(report)
    return 0


def cmd_repair_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.repair_plan(
            args.fault_id,
            lambda_cost=args.lambda_cost,
            max_depth=args.max_depth,
            budget=args.budget,
        )
    )
    return 0


def cmd_fact_interface(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fact_interface(args.entry_ids))
    return 0


def cmd_role_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.role_collapse_scan(limit=args.limit))
    return 0


def cmd_dual_search(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dual_channel_search(
            args.query, consumer_scope=args.scope, budget=args.budget
        )
    )
    return 0


def cmd_commit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.commit_view(
            args.message,
            entry_ids=args.entry_ids,
            actor=args.actor,
            ts=args.now,
            branch=args.branch,
            outcome=args.outcome,
        )
    )
    return 0


def cmd_checkout(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.checkout_view(args.commit_hash))
    return 0


def cmd_diff_commits(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.diff_commits(args.a, args.b))
    return 0


def cmd_copyability(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.copyability_gate(
        args.query, consumer_scope=args.scope, threshold=args.threshold
    )
    _print(report)
    return 0 if report.get("memory_likely_helps") else 1


def cmd_pin_version(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pin_memory_version(args.label, actor=args.actor, ts=args.now)
    )
    return 0


def cmd_activate_version(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    commit = None if args.clear else args.commit_hash
    _print(stele.activate_version(commit))
    return 0


def cmd_stale_facts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.stale_fact_scan(limit=args.limit)
    _print(report)
    return 0 if report.get("count", 0) == 0 else 1


def cmd_propose_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    entry = json.loads(Path(args.entry_json).read_text(encoding="utf-8")) if Path(args.entry_json).is_file() else json.loads(args.entry_json)
    _print(stele.propose_update(entry))
    return 0


def cmd_apply_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    entry = json.loads(Path(args.entry_json).read_text(encoding="utf-8")) if Path(args.entry_json).is_file() else json.loads(args.entry_json)
    _print(
        stele.apply_update(
            entry, actor=args.actor, action=args.action, ts=args.now
        )
    )
    return 0


def cmd_ledger_view(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ledger_view())
    return 0


def cmd_memory_worth(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memory_worth(args.entry_id))
    return 0


def cmd_low_worth(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.low_worth_scan(
        threshold=args.threshold, min_samples=args.min_samples
    )
    _print(report)
    return 0 if report.get("count", 0) == 0 else 1


def cmd_begin_tx(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.begin_transaction(
            actor=args.actor, risk_tier=args.risk_tier, ts=args.now
        )
    )
    return 0


def cmd_commit_tx(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
    _print(
        stele.commit_transaction(
            args.txid, evidence, actor=args.actor, ts=args.now
        )
    )
    return 0


def cmd_abort_tx(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.abort_transaction(args.txid, actor=args.actor, ts=args.now)
    )
    return 0


def cmd_action_safe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.action_safe_gate(args.entry_ids)
    _print(report)
    return 0 if report.get("allowed") else 1


def cmd_in_flight(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.in_flight_report())
    return 0


def cmd_symbolic_conflicts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.symbolic_conflict_scan()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_classify_conflict(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_conflict(args.entry_a, args.entry_b))
    return 0


def cmd_compact_render(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.compact_render(
            args.query,
            consumer_scope=args.scope,
            reader_budget=args.reader_budget,
        )
    )
    return 0


def cmd_stage_effect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    raw = args.payload
    payload = (
        json.loads(Path(raw).read_text(encoding="utf-8"))
        if Path(raw).is_file()
        else json.loads(raw)
    )
    _print(
        stele.stage_effect(
            sink=args.sink,
            payload=payload,
            actor=args.actor,
            txid=args.txid,
            ts=args.now,
        )
    )
    return 0


def cmd_list_effects(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.list_effects(state=args.state))
    return 0


def cmd_state_resolution(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.state_resolution(conflict_key=args.key)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_premise_resistance(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.premise_resistance(args.query, consumer_scope=args.scope)
    _print(report)
    return 1 if report.get("refuse_premise") else 0


def cmd_verify_transition(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.verify_transition(args.old_id, args.new_id)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_related_slots(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.related_slot_scan(args.conflict_key))
    return 0


def cmd_gem_report(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.gem_report()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_project_resolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.project_resolve(args.conflict_key)
    _print(report)
    return 0 if report.get("decision") == "select" else 1


def cmd_correction_handle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.correction_handle(
        claim_id=args.claim_id, claim_ref=args.claim_ref
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_pin_projection(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pin_projection(
            args.conflict_key,
            args.chosen_id,
            actor=args.actor,
            ts=args.now,
        )
    )
    return 0


def cmd_toki_classify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    raw = args.candidate_json
    if raw.strip().startswith("{"):
        candidate = json.loads(raw)
    else:
        candidate = json.loads(Path(raw).read_text(encoding="utf-8"))
    _print(stele.toki_classify_operator(candidate, tip_id=args.tip_id))
    return 0


def cmd_toki_anomalies(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.toki_anomaly_scan()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_context_bid(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.context_bid(args.query, slots=args.slots, now=args.now))
    return 0


def cmd_repair_mincut(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.repair_select_mincut(
            args.fault_id, lambda_cost=args.lambda_cost
        )
    )
    return 0


def cmd_adjudicate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    raw = args.candidate_json
    if raw.strip().startswith("{"):
        candidate = json.loads(raw)
    else:
        candidate = json.loads(Path(raw).read_text(encoding="utf-8"))
    _print(stele.adjudicate_update(candidate))
    return 0


def cmd_unknown_slots(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.unknown_current_slots()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_authorize_retrieval(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.authorize_retrieval(
            query=args.query, consumer_scope=args.consumer_scope
        )
    )
    return 0


def cmd_admit_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    bundle = json.loads(args.bundle_json)
    report = stele.admit_gate(
        action=args.action, actor=args.actor, authority_bundle=bundle, ts=args.now
    )
    _print(report)
    return 0 if report.get("admitted") else 1


def cmd_put_raw(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=True)
    _print(stele.put_raw_page(args.text, actor=args.actor, ts=args.now))
    return 0


def cmd_sufficiency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.sufficiency_gate(
        args.query, consumer_scope=args.consumer_scope
    )
    _print(report)
    return 0 if report.get("decision") == "hit" else 1


def cmd_escalate_raw(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.escalate_raw(args.summary_ids)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_writeback(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=True)
    _print(
        stele.verified_writeback(
            title=args.title,
            body=args.body,
            scope=args.scope,
            raw_digests=args.raw_digest,
            actor=args.actor,
            ts=args.now,
        )
    )
    return 0


def cmd_crystallize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.crystallize_skill(
        args.source_ids, actor=args.actor, ts=args.now, write=args.write
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_skill_catalog(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.skill_catalog())
    return 0


def cmd_fade_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fade_scan(now=args.now, threshold=args.threshold))
    return 0


def cmd_fusion_candidates(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fusion_candidates())
    return 0


def cmd_weibull(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.weibull_relevance(args.entry_id, now=args.now))
    return 0


def cmd_evidence_gap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.evidence_gap(
        args.query, consumer_scope=args.consumer_scope
    )
    _print(report)
    return 0 if report.get("closed") else 1


def cmd_reflective(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.reflective_retrieve(
            args.query, consumer_scope=args.consumer_scope
        )
    )
    return 0


def cmd_archive_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.archive_plan(now=args.now, min_age_days=args.min_age_days))
    return 0


def cmd_archive_apply(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.archive_apply(
            args.entry_ids,
            actor=args.actor,
            ts=args.now,
            require_eligible=not args.force,
        )
    )
    return 0


def cmd_unarchive(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.unarchive(args.entry_id, actor=args.actor, ts=args.now))
    return 0


def cmd_cis(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.composite_importance(args.entry_id, now=args.now))
    return 0


def cmd_cis_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cis_scan(now=args.now))
    return 0


def cmd_control_suggest(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.control_suggest(
            args.query, consumer_scope=args.consumer_scope, now=args.now
        )
    )
    return 0


def cmd_value_tag(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.value_tag(
            args.entry_id, now=args.now, task_query=args.task_query
        )
    )
    return 0


def cmd_wm_push(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wm_push(args.entry_id))
    return 0


def cmd_wm_list(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wm_list())
    return 0


def cmd_sleep_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sleep_plan(now=args.now))
    return 0


def cmd_sleep_nrem(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sleep_apply_nrem(actor=args.actor, now=args.now))
    return 0


def cmd_episodic_buffer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.episodic_buffer())
    return 0


def cmd_semantic_boundary(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.semantic_boundary(args.previous, args.current))
    return 0


def cmd_consolidate_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.consolidate_plan())
    return 0


def cmd_anticipate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.anticipate(args.query, consumer_scope=args.consumer_scope)
    )
    return 0


def cmd_verify_compaction(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.verify_compaction(
        args.query,
        args.compacted_text,
        consumer_scope=args.consumer_scope,
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_sensory_filter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sensory_filter(args.text))
    return 0


def cmd_stage_inventory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.stage_inventory(now=args.now))
    return 0


def cmd_stage_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.stage_budget_plan(
            args.query, consumer_scope=args.consumer_scope, now=args.now
        )
    )
    return 0


def cmd_multi_hop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.multi_hop_retrieve(args.query))
    return 0


def cmd_write_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pending = json.loads(args.pending_json)
    report = stele.write_gate(pending)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_action_risk_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.action_risk_gate(args.entry_ids, risk=args.risk)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_residuals(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.extract_residuals(args.entry_id))
    return 0


def cmd_entities(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.register_entities())
    return 0


def cmd_profile_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.profile_expand(args.query))
    return 0


def cmd_residual_augment(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.residual_augment(args.query, args.entry_ids))
    return 0


def cmd_match_correction(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.match_correction(failure_id=args.failure_id))
    return 0


def cmd_insight_inject(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    correction = json.loads(args.correction_json)
    report = stele.insight_inject(correction)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_cascade_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cascade_route(
            args.query, consumer_scope=args.consumer_scope
        )
    )
    return 0


def cmd_multi_channel(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.multi_channel_fuse(
            args.query,
            consumer_scope=args.consumer_scope,
            force_full=bool(args.force_full),
        )
    )
    return 0


def cmd_dual_project(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dual_project(args.entry_id))
    return 0


def cmd_governance_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.governance_route(args.task))
    return 0


def cmd_session_delta_open(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.session_delta_open(args.session_id))
    return 0


def cmd_session_delta_deliver(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    route = json.loads(args.route_json)
    _print(stele.session_delta_deliver(args.session_id, route))
    return 0


def cmd_entity_context(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.entity_context(args.subject_id))
    return 0


def cmd_entity_leak_probe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.entity_leak_probe(
        args.subject_id,
        query=args.query,
        consumer_scope=args.consumer_scope,
        prefilter=not bool(args.no_prefilter),
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_hymem_slot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hymem_classify_slot(args.text))
    return 0


def cmd_hymem_isolate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    items = json.loads(args.items_json)
    report = stele.hymem_isolate_pack(items)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_version_markers(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.extract_version_markers(args.entry_id))
    return 0


def cmd_freshness_resolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.freshness_resolve(conflict_key=args.conflict_key)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_assemble_current(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.assemble_current(args.query))
    return 0


def cmd_hop_freshness(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    hops = json.loads(args.hops_json)
    _print(stele.hop_freshness(hops))
    return 0


def cmd_patch_test(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pending = json.loads(args.pending_json)
    report = stele.patch_test(
        pending, args.source_id, cited_span=args.cited_span
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_temporal_resolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.temporal_resolve(args.conflict_key)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_recover_active_map(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    keys = json.loads(args.keys_json) if args.keys_json else None
    _print(stele.recover_active_map(keys))
    return 0


def cmd_fleet_scope_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.fleet_scope_gate(
        args.entry_id, allowed_scopes=args.scopes
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_propagate_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.propagate_plan(
            source_scope=args.source_scope,
            target_scopes=args.target_scopes,
            query=args.query,
        )
    )
    return 0


def cmd_stale_propagation(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.stale_propagation_scan())
    return 0


def cmd_query_complexity(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.query_complexity(args.query))
    return 0


def cmd_budget_tier_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.budget_tier_route(args.query))
    return 0


def cmd_budget_module_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.budget_module_plan(args.query, global_budget=args.budget))
    return 0


def cmd_skill_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.skill_rank(args.query))
    return 0


def cmd_skill_prereq(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.skill_prereq_expand(args.skill_id))
    return 0


def cmd_retrieval_skills(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.list_retrieval_skills())
    return 0


def cmd_route_retrieval_skill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.route_retrieval_skill(args.query))
    return 0


def cmd_run_retrieval_skill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.run_retrieval_skill(
        args.query,
        consumer_scope=args.consumer_scope,
        skill=args.skill,
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_support_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pending = json.loads(args.pending_json)
    _print(stele.support_score(pending, context=args.context))
    return 0


def cmd_consistency_admit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pending = json.loads(args.pending_json)
    report = stele.consistency_admit(
        pending, context=args.context, tau=args.tau
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_retrieval_admit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.retrieval_admit(
            args.query, consumer_scope=args.consumer_scope
        )
    )
    return 0


def cmd_task_pack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.task_conditioned_pack(
            args.query, consumer_scope=args.consumer_scope
        )
    )
    return 0


def cmd_sovereignty_checklist(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.sovereignty_checklist()
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_post_delete_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.post_delete_verify(
        args.entry_ids, consumer_scope=args.consumer_scope
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_rollback_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.rollback_plan(args.entry_ids)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_density_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    tunnels = json.loads(args.tunnels_json)
    report = stele.density_fuse(tunnels, limit=args.limit)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_evidence_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.evidence_plan(args.query, limit=args.limit)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_cited_pack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.cited_pack(
        args.query, args.evidence_ids, budget=args.budget
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_compress_candidates(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.compress_candidates(min_similarity=args.min_sim)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_refine_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.refine_plan(
        target_count=args.target, min_similarity=args.min_sim
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_merge_link_add(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    entry = json.loads(args.entry_json)
    report = stele.merge_link_add(entry)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_bridge_discover(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.bridge_discover(args.seed_ids, max_depth=args.max_depth)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_fuse_cluster(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.fuse_cluster(args.entry_ids, label=args.label)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_result_digest(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    payload = json.loads(args.payload_json)
    _print(stele.result_digest(payload))
    return 0


def cmd_operator_cost(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = json.loads(args.steps_json)
    report = stele.operator_cost_estimate(steps, max_cost=args.max_cost)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_plan_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    plan = json.loads(args.plan_json)
    report = stele.plan_static_verify(
        plan, task_ids=args.task_ids, max_cost=args.max_cost
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_claim_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    claims = json.loads(args.claims_json)
    trace = json.loads(args.trace_json)
    report = stele.claim_verify(claims, trace)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_summary_quarantine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    summaries = json.loads(args.summaries_json)
    corrections = json.loads(args.corrections_json)
    report = stele.summary_quarantine_scan(summaries, corrections)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_local_maint(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.localized_maintenance_plan(
        args.seed_ids, radius=args.radius, max_touch=args.max_touch
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_maint_cost(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.maintenance_cost_compare(
        args.local_touch, store_size=args.store_size
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_origin_bind(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pending = json.loads(args.pending_json)
    report = stele.origin_bind(pending, channel_origin=args.channel_origin)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_propagate_origin(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    derived = json.loads(args.derived_json)
    report = stele.propagate_origin(derived, args.source_ids)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_launder_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.launder_scan())
    return 0


def cmd_act_authority(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.act_authority_gate(
        args.value,
        args.driver_ids,
        trusted_principals=args.principal,
        user_auth=args.user_auth,
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_save_policy(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pending = json.loads(args.pending_json)
    report = stele.save_policy(
        pending, level=args.level, channel_origin=args.channel_origin
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_retrieval_screen(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.retrieval_screen(
        args.query, consumer_scope=args.consumer_scope
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_build_memtree(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.build_memtree(scope=args.scope)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_dirty_path(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    entry = json.loads(args.entry_json)
    report = stele.dirty_path_plan(entry, scope=args.scope)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_coarse_to_fine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.coarse_to_fine(args.query, scope=args.scope)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_build_themes(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.build_themes(scope=args.scope)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_theme_attach(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    entry = json.loads(args.entry_json)
    report = stele.theme_attach(entry, scope=args.scope)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_split_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.split_merge_plan(
        scope=args.scope, max_size=args.max_size
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_top_down_pack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.top_down_pack(
        args.query, scope=args.scope, budget=args.budget
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_persistence_probe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.persistence_probe(args.poison_ids))
    return 0


def cmd_execute_chain_probe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.execute_chain_probe(
            args.poison_ids,
            consumer_scope=args.consumer_scope,
            probe_query=args.query,
            action_value=args.action_value,
        )
    )
    return 0


def cmd_lifecycle_report(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.lifecycle_report(
        args.poison_ids,
        consumer_scope=args.consumer_scope,
        preserve_ids=args.preserve or None,
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_selective_repair(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.selective_repair_plan(
        args.poison_ids, preserve_ids=args.preserve or None
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_conflict_tag(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.conflict_tag(conflict_key=args.conflict_key))
    return 0


def cmd_forget_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.forget_gate_plan(conflict_key=args.conflict_key))
    return 0


def cmd_consolidate_survivors(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.consolidate_survivors(args.conflict_key)
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_pi_depth(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pi_depth_scan(args.conflict_key))
    return 0


def cmd_consensus_admit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.consensus_admit(
        args.query, consumer_scope=args.consumer_scope
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_mem_action_graph(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    actions = json.loads(args.actions_json) if args.actions_json else None
    _print(stele.build_mem_action_graph(actions=actions))
    return 0


def cmd_dependency_trace(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dependency_trace(args.fault_ids))
    return 0


def cmd_preserve_independent(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.preserve_independent(
            args.fault_ids,
            trusted_sources=args.trusted_source or None,
        )
    )
    return 0


def cmd_selective_replay(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    actions = json.loads(args.actions_json) if args.actions_json else None
    report = stele.selective_replay_plan(
        args.fault_ids,
        trusted_sources=args.trusted_source or None,
        actions=actions,
    )
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_classify_write_channel(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_write_channel(args.entry_id))
    return 0


def cmd_source_isolation(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.source_isolation_gate(args.entry_id))
    return 0


def cmd_write_channel_inventory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.write_channel_inventory())
    return 0


def cmd_channel_admit_batch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.channel_admit_batch(json.loads(args.candidates_json))
    _print(report)
    return 0 if report.get("ok") else 1


def cmd_slot_coverage(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.slot_coverage(args.entry_id))
    return 0


def cmd_threat_tier(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.threat_tier_classify(args.entry_id))
    return 0


def cmd_dormant_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dormant_trigger_scan(limit=args.limit))
    return 0


def cmd_coalition_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.compositional_coalition_scan(min_slots=args.min_slots))
    return 0


def cmd_collusion_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.collusion_risk_gate(
        args.query, consumer_scope=args.consumer_scope
    )
    _print(report)
    return 0 if report.get("decision") == "admit" else 1


def cmd_mempoison_ladder(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mempoison_ladder_report())
    return 0


def cmd_salami_pair(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.salami_pair_probe(args.entry_id_a, args.entry_id_b))
    return 0


def cmd_persistence_layer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.classify_persistence_layer(
            args.entry_id, override=args.override
        )
    )
    return 0


def cmd_persistence_policy(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.persistence_policy(args.layer))
    return 0


def cmd_layer_inventory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.layer_inventory())
    return 0


def cmd_knowledge_protect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.knowledge_protect_scan(
            faded_ids=args.faded or None,
        )
    )
    return 0


def cmd_intelligence_reject(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    candidate = (
        json.loads(args.candidate_json) if args.candidate_json else None
    )
    report = stele.intelligence_reject_gate(
        entry_id=args.entry_id, candidate=candidate
    )
    _print(report)
    return 0 if report.get("decision") == "admit" else 1


def cmd_credential_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.credential_scan(args.entry_id))
    return 0


def cmd_credential_reject(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    candidate = (
        json.loads(args.candidate_json) if args.candidate_json else None
    )
    report = stele.credential_reject_gate(
        entry_id=args.entry_id, candidate=candidate
    )
    _print(report)
    return 0 if report.get("decision") == "admit" else 1


def cmd_credential_store_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.credential_store_scan())
    return 0


def cmd_uncertainty_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.uncertainty_score(
            args.query, consumer_scope=args.consumer_scope
        )
    )
    return 0


def cmd_uncertainty_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.uncertainty_retrieve_gate(
        args.query, consumer_scope=args.consumer_scope
    )
    _print(report)
    return 0


def cmd_reasoning_reserve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.reasoning_reserve_plan(
            args.budget, confidence=args.confidence
        )
    )
    return 0


def cmd_memory_component(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_memory_component(args.entry_id))
    return 0


def cmd_merkle_dag(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.build_merkle_dag())
    return 0


def cmd_verify_merkle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.verify_merkle_root(args.expected_root)
    _print(report)
    return 0 if report.get("match") else 1


def cmd_issue_cap_token(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.issue_capability_token(
            entry_ids=args.entry_ids,
            ops=args.ops,
            audience=args.audience,
            expires_at=args.expires_at,
        )
    )
    return 0


def cmd_check_cap_token(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.check_capability(
        args.token,
        json.loads(args.payload_json),
        op=args.op,
        entry_id=args.entry_id,
    )
    _print(report)
    return 0 if report.get("allowed") else 1


def cmd_selective_disclose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.selective_disclose(
            args.entry_ids,
            include_ancestors=not args.no_ancestors,
        )
    )
    return 0


def cmd_rehydrate_safe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ids = args.entry_ids or None
    _print(stele.rehydrate_safe_plan(ids))
    return 0


def cmd_issue_action_cap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.issue_action_capability(
            intent=args.intent,
            method=args.method,
            host=args.host,
            session_id=args.session_id,
            max_calls=args.max_calls,
            expires_at=args.expires_at,
        )
    )
    return 0


def cmd_cap_export_probe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.capability_export_probe(
        args.handle, json.loads(args.payload_json)
    )
    _print(report)
    return 0 if report.get("export_allowed") is False else 1


def cmd_check_action_cap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.check_action_capability(
        args.handle,
        json.loads(args.payload_json),
        method=args.method,
        host=args.host,
        session_id=args.session_id,
        call_count=args.call_count,
    )
    _print(report)
    return 0 if report.get("allowed") else 1


def cmd_risk_source(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_risk_source(json.loads(args.step_json)))
    return 0


def cmd_failure_mode(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_failure_mode(json.loads(args.step_json)))
    return 0


def cmd_real_world_harm(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_real_world_harm(json.loads(args.step_json)))
    return 0


def cmd_diagnose_step(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.diagnose_trajectory_step(json.loads(args.step_json)))
    return 0


def cmd_diagnose_trajectory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.diagnose_trajectory(json.loads(args.steps_json)))
    return 0


def cmd_unreasonable_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.safe_but_unreasonable_scan(json.loads(args.steps_json)))
    return 0


def cmd_taxonomy_inventory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.taxonomy_inventory())
    return 0


def cmd_weave_layer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.weave_layer_assign(args.entry_id))
    return 0


def cmd_hybrid_weave(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.build_hybrid_weave())
    return 0


def cmd_dual_channel(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dual_channel_retrieve(
            args.query, k_r=args.k_r, k_p=args.k_p, k_e=args.k_e
        )
    )
    return 0


def cmd_experience_abstract(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.experience_abstract_plan(min_support=args.min_support))
    return 0


def cmd_temporal_conflict(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.temporal_session_conflict_scan())
    return 0


def cmd_hop_depth(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.multi_hop_depth_score(args.path_ids))
    return 0


def cmd_design_space(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.list_design_space())
    return 0


def cmd_arch_profile(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    overrides = {
        k: v
        for k, v in {
            "encode": args.encode,
            "store": args.store_mode,
            "retrieve": args.retrieve,
            "manage": args.manage,
        }.items()
        if v
    }
    _print(stele.architecture_profile(overrides or None))
    return 0


def cmd_arch_diagnose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    fb = json.loads(args.feedback_json) if args.feedback_json else None
    _print(
        stele.diagnose_architecture(json.loads(args.profile_json), feedback=fb)
    )
    return 0


def cmd_arch_variants(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.propose_architecture_variants(
            json.loads(args.profile_json),
            json.loads(args.diagnosis_json),
            s=args.s,
        )
    )
    return 0


def cmd_arch_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rank_architecture_fitness(json.loads(args.candidates_json)))
    return 0


def cmd_arch_parents(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.select_architecture_parents(json.loads(args.ranked_json), k=args.k)
    )
    return 0


def cmd_ept(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ept_classify(args.entry_id))
    return 0


def cmd_functional_role(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.functional_role_assign(args.entry_id))
    return 0


def cmd_contamination_scan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.contamination_scan())
    return 0


def cmd_type_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.type_route_retrieve(
            args.query, allowed_roles=args.roles, budget=args.budget
        )
    )
    return 0


def cmd_dreaming_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dreaming_consolidate_plan())
    return 0


def cmd_feedback_revise(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.feedback_revise_plan(
            signal=args.signal,
            entry_ids=args.entry_ids,
            mode=args.mode,
        )
    )
    return 0


def cmd_skill_evolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skill_evolve_plan(
            json.loads(args.trajectories_json),
            supervised=args.supervised,
            min_batch=args.min_batch,
        )
    )
    return 0


def cmd_pref_signal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.extract_preference_signal(args.text))
    return 0


def cmd_pref_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.preference_update_plan(
            json.loads(args.observations_json),
            window=args.window,
            beta=args.beta,
            lam=args.lam,
            delta=args.delta,
        )
    )
    return 0


def cmd_pref_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.fuse_preference(
            json.loads(args.sw_json), json.loads(args.ema_json), lam=args.lam
        )
    )
    return 0


def cmd_pref_change(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.preference_change_detect(
            json.loads(args.sw_json),
            json.loads(args.ema_json),
            delta=args.delta,
        )
    )
    return 0


def cmd_pref_prompt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.format_preference_prompt(json.loads(args.fused_json)))
    return 0


def cmd_beam_categories(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.beam_category_inventory())
    return 0


def cmd_beam_classify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_beam_query(args.query))
    return 0


def cmd_knowledge_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.knowledge_update_check(prior=args.prior, current=args.current)
    )
    return 0


def cmd_abstention_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.abstention_gate(
            query=args.query,
            evidence_count=args.evidence_count,
            min_evidence=args.min_evidence,
        )
    )
    return 0


def cmd_contradiction_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.contradiction_resolve_plan(json.loads(args.statements_json)))
    return 0


def cmd_event_order(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.event_order_check(json.loads(args.events_json)))
    return 0


def cmd_halu_stage(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.localize_hallucination_stage(symptom=args.symptom))
    return 0


def cmd_episodic_gist(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.extract_episodic_gist(args.entry_id))
    return 0


def cmd_temporal_facts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.extract_temporal_facts(args.entry_id))
    return 0


def cmd_situational_bind(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.situational_bind(args.entry_id))
    return 0


def cmd_episodic_graph(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.build_hybrid_episodic_graph())
    return 0


def cmd_agentic_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agentic_retrieve_plan(args.query, max_steps=args.max_steps)
    )
    return 0


def cmd_ordinal_event(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ordinal_event_query(order=args.order))
    return 0


def cmd_memcell(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.form_memcell(args.entry_id))
    return 0


def cmd_memscenes(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.consolidate_memscenes())
    return 0


def cmd_foresight_filter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.foresight_filter(now=args.now))
    return 0


def cmd_recollect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.reconstructive_recollect(
            args.query, n_scenes=args.n_scenes, k_episodes=args.k_episodes
        )
    )
    return 0


def cmd_profile_evolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.profile_evolve_plan())
    return 0


def cmd_necessity_check(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.necessity_sufficiency_check(
        retrieved_count=args.retrieved_count,
        min_needed=args.min_needed,
        max_sufficient=args.max_sufficient,
    )
    _print(report)
    return 0 if report.get("pass") else 1


def cmd_memory_tier(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_memory_tier(args.entry_id))
    return 0


def cmd_heat_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.heat_score(
            n_visit=args.n_visit,
            l_interaction=args.l_interaction,
            delta_t_seconds=args.delta_t,
        )
    )
    return 0


def cmd_segment_pages(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.segment_pages())
    return 0


def cmd_stm_to_mtm(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.stm_to_mtm_plan(args.page_ids, capacity=args.capacity))
    return 0


def cmd_mtm_evict(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mtm_evict_plan(max_segments=args.max_segments))
    return 0


def cmd_promote_lpm(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.promote_to_lpm_plan(tau=args.tau))
    return 0


def cmd_hier_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hierarchical_retrieve(
            args.query, top_m_segments=args.top_m, top_k_pages=args.top_k
        )
    )
    return 0


def cmd_episodic_narrative(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.integrate_episodic_narrative(args.entry_id))
    return 0


def cmd_anticipatory_schema(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.anticipatory_schema(args.cue))
    return 0


def cmd_prediction_error(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.prediction_error_distill(
            actual=args.actual, anticipated=args.anticipated
        )
    )
    return 0


def cmd_deserves_memory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.deserves_memory_gate(
        actual=args.actual, anticipated=args.anticipated
    )
    _print(report)
    return 0 if report.get("admit") else 1


def cmd_distill_batch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.distill_batch_plan(args.entry_ids))
    return 0


def cmd_classify_network(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_network(args.entry_id))
    return 0


def cmd_retain_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.retain_plan())
    return 0


def cmd_network_inventory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.network_inventory())
    return 0


def cmd_recall_multi(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.recall_multi_strategy(
            args.query, token_budget=args.token_budget, top_k=args.top_k
        )
    )
    return 0


def cmd_opinion_reinforce(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    supporting = not args.weaken
    _print(
        stele.opinion_reinforce(
            args.opinion_text, supporting=supporting, prior_confidence=args.prior
        )
    )
    return 0


def cmd_reflect_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.reflect_plan(
            args.query,
            skepticism=args.skepticism,
            literalism=args.literalism,
            empathy=args.empathy,
            bias_strength=args.bias,
        )
    )
    return 0


def cmd_distill_strategy(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.distill_strategy_item(args.entry_id, outcome=args.outcome))
    return 0


def cmd_failure_lesson_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.failure_lesson_gate(
        success_count=args.success_count, failure_count=args.failure_count
    )
    _print(report)
    return 0 if report.get("pass") else 1


def cmd_matts_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.matts_contrastive_plan(
            mode=args.mode, n_trajectories=args.n, task_hint=args.hint
        )
    )
    return 0


def cmd_skill_bank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.init_skill_bank())
    return 0


def cmd_span_partition(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.span_partition(args.text, max_chars=args.max_chars))
    return 0


def cmd_select_skills(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.select_skills(span_text=args.span_text, top_k=args.top_k))
    return 0


def cmd_execute_skills(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.execute_skill_plan(span_text=args.span_text))
    return 0


def cmd_hard_case(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.record_hard_case(
            query=args.query, predicted=args.predicted, expected=args.expected
        )
    )
    return 0


def cmd_designer_evolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    cases = [
        stele.record_hard_case(query=q, fail=True) for q in (args.queries or ["when?"])
    ]
    _print(stele.designer_evolve_plan(cases))
    return 0


def cmd_memory_op(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_memory_op(args.candidate))
    return 0


def cmd_noop_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    report = stele.noop_gate(args.candidate)
    _print(report)
    return 0 if report.get("noop") else 1


def cmd_memory_op_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memory_op_plan(args.candidate))
    return 0


def cmd_conflict_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.conflict_update_plan(old_text=args.old, new_text=args.new))
    return 0


def cmd_delete_stale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.delete_stale_plan())
    return 0


def cmd_graph_tier(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.classify_graph_tier(args.entry_id))
    return 0


def cmd_query_graph(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.build_query_graph())
    return 0


def cmd_insight_up(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.upward_insight_traverse(args.query))
    return 0


def cmd_interaction_down(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.downward_interaction_traverse(args.query))
    return 0


def cmd_bidir_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bidirectional_retrieve(args.query))
    return 0


def cmd_hierarchy_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hierarchy_update_plan(query=args.query, status=args.status))
    return 0


def cmd_meta_thinker(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.meta_thinker_guidance(args.chunk, mode=args.mode))
    return 0


def cmd_answerability(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.answerability_check(args.query))
    return 0


def cmd_probe_qa(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.synthesize_probe_qa(args.session_text))
    return 0


def cmd_verify_probes(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    probes = _json.loads(args.probes_json)
    _print(stele.verify_probes(probes))
    return 0


def cmd_repair_probes(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    probes = _json.loads(args.probes_json)
    results = _json.loads(args.results_json)
    _print(stele.repair_from_probes(probes, results))
    return 0


def cmd_induce_workflow(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.steps_json)
    _print(
        stele.induce_workflow(
            task=args.task, steps=steps, success=not args.fail
        )
    )
    return 0


def cmd_online_induce_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.online_induce_gate(success_label=bool(args.success)))
    return 0


def cmd_workflow_add_plan(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    wf = _json.loads(args.workflow_json)
    existing = _json.loads(args.existing_json)
    _print(stele.workflow_memory_add_plan(wf, existing=existing))
    return 0


def cmd_retrieve_workflows(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    workflows = _json.loads(args.workflows_json)
    _print(
        stele.retrieve_workflows(
            workflows, query=args.query, top_k=args.top_k
        )
    )
    return 0


def cmd_workflow_step_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.workflow_step_budget(
            baseline_steps=args.baseline_steps,
            workflow_step_count=args.workflow_step_count,
        )
    )
    return 0


def cmd_distill_retrieval_exp(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.distill_retrieval_experience(
            query=args.query,
            outcome=args.outcome,
            anomaly=args.anomaly,
            strategy_hint=args.hint,
        )
    )
    return 0


def cmd_anomaly_trigger(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    priors = _json.loads(args.priors_json)
    _print(
        stele.anomaly_trigger(
            hit_count=args.hits,
            prior_queries=priors,
            current_query=args.query,
            rounds_used=args.rounds,
            max_rounds=args.max_rounds,
        )
    )
    return 0


def cmd_query_level_guidance(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    exps = _json.loads(args.experiences_json)
    _print(
        stele.query_level_guidance(
            exps, query=args.query, anomaly=args.anomaly
        )
    )
    return 0


def cmd_experience_lifecycle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.experience_lifecycle_score(
            usage=args.usage,
            reuse_success=args.reuse_success,
            age_days=args.age_days,
        )
    )
    return 0


def cmd_prune_experience(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    exps = _json.loads(args.experiences_json)
    _print(stele.prune_experience_plan(exps, capacity=args.capacity))
    return 0


def cmd_isolate_factual(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ans = _json.loads(args.answer_ids_json)
    exp = _json.loads(args.experience_ids_json)
    _print(
        stele.isolate_factual_from_procedural(
            answer_pack_ids=ans, experience_ids=exp
        )
    )
    return 0


def cmd_multi_faceted_distill(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.steps_json)
    _print(
        stele.multi_faceted_distill(
            scenario=args.scenario,
            outcome=args.outcome,
            steps=steps,
            failure_reason=args.failure_reason,
            peer_success=args.peer_success,
        )
    )
    return 0


def cmd_scenario_retrieve(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pool = _json.loads(args.pool_json)
    _print(
        stele.scenario_retrieve(pool, scenario=args.scenario, top_k=args.top_k)
    )
    return 0


def cmd_adaptive_rewrite(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    exps = _json.loads(args.experiences_json)
    _print(
        stele.adaptive_rewrite_plan(exps, new_scenario=args.new_scenario)
    )
    return 0


def cmd_utility_after_reuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.utility_after_reuse(
            freq=args.freq, utility=args.utility, reuse_helped=bool(args.helped)
        )
    )
    return 0


def cmd_selective_add(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    cand = _json.loads(args.candidate_json)
    pool = _json.loads(args.pool_json)
    _print(
        stele.selective_add_plan(
            cand, pool=pool, validated=not args.unvalidated
        )
    )
    return 0


def cmd_utility_prune(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pool = _json.loads(args.pool_json)
    _print(stele.utility_prune_plan(pool, alpha=args.alpha, beta=args.beta))
    return 0


def cmd_cheatsheet_snippet(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.extract_cheatsheet_snippet(
            kind=args.kind, title=args.title, body=args.body
        )
    )
    return 0


def cmd_retrieve_cheatsheet(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    memory = _json.loads(args.memory_json)
    _print(
        stele.retrieve_cheatsheet(memory, query=args.query, top_k=args.top_k)
    )
    return 0


def cmd_curator_decide(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.curator_decide(
            proposed_useful=bool(args.useful),
            existing_faulty=bool(args.faulty),
            superseded=bool(args.superseded),
        )
    )
    return 0


def cmd_compact_memory_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.compact_memory_gate(
            entry_chars=args.entry_chars, memory_chars=args.memory_chars
        )
    )
    return 0


def cmd_dc_rs_order(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.steps_json)
    _print(stele.dc_rs_order_check(steps))
    return 0


def cmd_experience_pool_add(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.experience_pool_add(
            task=args.task,
            outcome=args.outcome,
            trajectory_summary=args.summary,
        )
    )
    return 0


def cmd_insight_op(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    insights = _json.loads(args.insights_json)
    _print(
        stele.insight_op(
            insights,
            op=args.op,
            text=args.text,
            insight_id=args.insight_id,
        )
    )
    return 0


def cmd_insight_importance_gate(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    insights = _json.loads(args.insights_json)
    _print(stele.insight_importance_gate(insights))
    return 0


def cmd_retrieve_insights(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    insights = _json.loads(args.insights_json)
    _print(
        stele.retrieve_insights(
            insights, query=args.query, top_k=args.top_k
        )
    )
    return 0


def cmd_retrieve_similar_successes(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    pool = _json.loads(args.pool_json)
    _print(
        stele.retrieve_similar_successes(
            pool, task=args.task, top_k=args.top_k
        )
    )
    return 0


def cmd_prospective_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.prospective_reflect(
            topic=args.topic,
            segment=args.segment,
            granularity=args.granularity,
        )
    )
    return 0


def cmd_topic_memory_bank(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    memories = _json.loads(args.memories_json)
    _print(stele.topic_memory_bank(memories))
    return 0


def cmd_retrieve_topic_memories(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    memories = _json.loads(args.memories_json)
    _print(
        stele.retrieve_topic_memories(
            memories, query=args.query, top_k=args.top_k
        )
    )
    return 0


def cmd_retrospective_cite(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    cited = _json.loads(args.cited_json)
    retrieved = _json.loads(args.retrieved_json)
    _print(
        stele.retrospective_cite_feedback(
            cited_ids=cited, all_retrieved_ids=retrieved
        )
    )
    return 0


def cmd_rerank_memories(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    candidates = _json.loads(args.candidates_json)
    boosts = _json.loads(args.boosts_json)
    _print(
        stele.rerank_memories(
            candidates, query=args.query, cite_boosts=boosts
        )
    )
    return 0


def cmd_retrieval_refine(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    memories = _json.loads(args.memories_json)
    cited = _json.loads(args.cited_json)
    unused = _json.loads(args.unused_json)
    _print(
        stele.retrieval_refine_plan(
            memories, cited_ids=cited, unused_ids=unused
        )
    )
    return 0


def cmd_collect_trajectory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.collect_trajectory_label(
            task=args.task, outcome=args.outcome, lesson=args.lesson
        )
    )
    return 0


def cmd_propose_patch(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    traj = _json.loads(args.trajectory_json)
    _print(
        stele.propose_trajectory_patch(
            traj, base_skill=args.base_skill, analyst=args.analyst
        )
    )
    return 0


def cmd_parallel_patch_pool(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    trajs = _json.loads(args.trajectories_json)
    _print(stele.parallel_patch_pool(trajs, base_skill=args.base_skill))
    return 0


def cmd_merge_patches(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    patches = _json.loads(args.patches_json)
    _print(stele.hierarchical_merge_patches(patches, merge_branch=args.branch))
    return 0


def cmd_skill_mode_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skill_mode_gate(
            mode=args.mode, has_human_skill=bool(args.human_skill)
        )
    )
    return 0


def cmd_prefer_parallel(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.prefer_parallel_over_sequential(
            parallel_quality=args.parallel_quality,
            sequential_quality=args.sequential_quality,
            parallel_minutes=args.parallel_minutes,
            sequential_minutes=args.sequential_minutes,
        )
    )
    return 0


def cmd_streaming_task_append(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    memory = _json.loads(args.memory_json)
    _print(
        stele.streaming_task_append(
            memory,
            task=args.task,
            prediction=args.prediction,
            outcome=args.outcome,
        )
    )
    return 0


def cmd_exprag_retrieve(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    memory = _json.loads(args.memory_json)
    _print(
        stele.exprag_retrieve(memory, query=args.query, top_k=args.top_k)
    )
    return 0


def cmd_spe_check(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.steps_json)
    _print(stele.search_predict_evolve_check(steps))
    return 0


def cmd_evomem_refine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.evomem_refine_plan(
            memory_size=args.memory_size,
            max_memory=args.max_memory,
            retrieval_hit=not args.miss,
            noisy=bool(args.noisy),
        )
    )
    return 0


def cmd_evolution_similarity(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    q = _json.loads(args.query_tokens_json)
    c = _json.loads(args.cluster_tokens_json)
    _print(
        stele.evolution_similarity_hint(query_tokens=q, cluster_tokens=c)
    )
    return 0


def cmd_classify_memory_slot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.classify_memory_slot(
            text=args.text, has_timestamp=bool(args.timestamp)
        )
    )
    return 0


def cmd_memory_write_op(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memory_write_op(
            slot=args.slot,
            op=args.op,
            content=args.content,
            record_id=args.record_id,
        )
    )
    return 0


def cmd_process_chunk(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.process_chunk_plan(
            chunk=args.chunk, existing_core_chars=args.core_chars
        )
    )
    return 0


def cmd_compression_ratio(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.compression_ratio(
            memory_chars=args.memory_chars, chunk_chars=args.chunk_chars
        )
    )
    return 0


def cmd_memalpha_reward(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    params = _json.loads(args.params_json)
    _print(stele.memalpha_reward_bundle(**params))
    return 0


def cmd_length_gen_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.length_generalization_gate(
            train_max_tokens=args.train_max_tokens,
            eval_tokens=args.eval_tokens,
        )
    )
    return 0


def cmd_classify_failure(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.classify_failure(
            failure_type=args.failure_type,
            observation_chars=args.obs_chars,
            severity=args.severity,
        )
    )
    return 0


def cmd_replay_outcome(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    obs = _json.loads(args.observations_json)
    _print(stele.extract_replay_outcome(observations=obs))
    return 0


def cmd_hindsight_relabel(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ach = _json.loads(args.achievements_json)
    _print(
        stele.hindsight_relabel_plan(
            original_goal=args.original_goal,
            achievements=ach,
            confidence=args.confidence,
        )
    )
    return 0


def cmd_multi_judge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.multi_judge_accept(
            confidence_j1=args.confidence_j1,
            confidence_j2=args.confidence_j2,
            theta=args.theta,
        )
    )
    return 0


def cmd_package_training_pair(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.package_training_pair(
            format=args.format,
            hindsight_goal=args.hindsight_goal,
            original_goal=args.original_goal,
            trajectory_summary=args.summary,
        )
    )
    return 0


def cmd_distill_planning_error(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.distill_planning_error(
            error_id=args.error_id,
            pattern=args.pattern,
            success_hint=args.success_hint,
            failure_hint=args.failure_hint,
        )
    )
    return 0


def cmd_prospective_critique(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.plan_steps_json)
    errs = _json.loads(args.planning_errors_json)
    _print(
        stele.prospective_critique_plan(
            plan_steps=steps, planning_errors=errs
        )
    )
    return 0


def cmd_revise_plan(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.original_steps_json)
    avoid = _json.loads(args.avoid_patterns_json)
    _print(
        stele.revise_plan_proposal(
            original_steps=steps,
            avoid_patterns=avoid,
            insert_guard=args.guard,
        )
    )
    return 0


def cmd_replan_deviation(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.replan_on_deviation(
            expected_observation=args.expected,
            actual_observation=args.actual,
            remaining_steps=args.remaining_steps,
        )
    )
    return 0


def cmd_preflect_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.preflect_before_execute_gate(
            critique_needs_revise=bool(args.needs_revise),
            revised_ready=bool(args.revised_ready),
        )
    )
    return 0


def cmd_orch_action(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.orchestration_action_select(
            action_type=args.action_type,
            skill_id=args.skill_id,
            step=args.step,
        )
    )
    return 0


def cmd_ttb_residual(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ttb_residual(
            log_forward=args.log_forward,
            log_backward=args.log_backward,
            log_reward=args.log_reward,
        )
    )
    return 0


def cmd_step_importance(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.step_importance(
            log_forward=args.log_forward, log_backward=args.log_backward
        )
    )
    return 0


def cmd_skill_marginal_flow(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    flows = _json.loads(args.flows_json)
    _print(
        stele.skill_marginal_flow(
            skill_flows=flows,
            skill_id=args.skill_id,
            target_index=args.index,
        )
    )
    return 0


def cmd_skill_curation(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skill_curation_decide(
            mean_log_flow=args.mean_log_flow,
            centered_log_share=args.centered_log_share,
            jensen_gap=args.jensen_gap,
            high_importance_step=bool(args.high_imp),
        )
    )
    return 0


def cmd_phase_evolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.phase_evolve_gate(
            residual_mean=args.residual_mean,
            residual_floor=args.residual_floor,
        )
    )
    return 0


def cmd_define_skill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.define_skill_triplet(
            skill_id=args.skill_id,
            activation=args.activation,
            execution=args.execution,
            termination=args.termination,
        )
    )
    return 0


def cmd_skill_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skill_select_gate(
            state_text=args.state_text, activation=args.activation
        )
    )
    return 0


def cmd_skill_terminate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skill_terminate_check(
            observation=args.observation, termination=args.termination
        )
    )
    return 0


def cmd_semantic_gradient(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.semantic_gradient_candidate(
            success_trace=args.success_trace,
            failure_trace=args.failure_trace,
            base_skill_id=args.base_skill_id,
        )
    )
    return 0


def cmd_ppo_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ppo_gate_verify(
            candidate_score=args.candidate_score,
            incumbent_score=args.incumbent_score,
        )
    )
    return 0


def cmd_skill_maintain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skill_score_maintain(
            frequency=args.frequency, avg_gain=args.avg_gain
        )
    )
    return 0


def cmd_ieu_record(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ieu_record(
            intent=args.intent,
            experience=args.experience,
            utility=args.utility,
        )
    )
    return 0


def cmd_two_phase_retrieve(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    memories = _json.loads(args.memories_json)
    _print(
        stele.two_phase_retrieve(query=args.query, memories=memories)
    )
    return 0


def cmd_utility_q_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.utility_q_update(
            current_q=args.current_q,
            reward=args.reward,
            next_max_q=args.next_max_q,
        )
    )
    return 0


def cmd_value_aware_select(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    candidates = _json.loads(args.candidates_json)
    _print(
        stele.value_aware_select(
            candidates=candidates, min_utility=args.min_utility
        )
    )
    return 0


def cmd_sim_util_warn(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.semantic_vs_utility_warn(
            similarity=args.similarity, utility=args.utility
        )
    )
    return 0


def cmd_distill_principle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.distill_principle(
            kind=args.kind, description=args.description
        )
    )
    return 0


def cmd_principle_dedupe(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    existing = _json.loads(args.existing_descs_json)
    _print(
        stele.principle_dedupe_plan(
            candidate_desc=args.candidate_desc, existing_descs=existing
        )
    )
    return 0


def cmd_principle_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.principle_metric_score(
            succ_count=args.succ_count, use_count=args.use_count
        )
    )
    return 0


def cmd_search_exp_action(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.search_experience_action(
            action=args.action, query=args.query
        )
    )
    return 0


def cmd_lifecycle_phase(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lifecycle_phase_gate(
            phase=args.phase,
            mutate_policy=bool(args.mutate_policy),
            distill=bool(args.distill),
        )
    )
    return 0


def cmd_prune_principles(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    scores = _json.loads(args.scores_json)
    _print(stele.prune_low_score_principles(scores=scores))
    return 0


def cmd_self_question(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.self_question_task(
            exploration_summary=args.exploration_summary,
            user_preference=args.preference,
        )
    )
    return 0


def cmd_exp_when_content(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.experience_when_content(
            when_to_use=args.when_to_use, content=args.content
        )
    )
    return 0


def cmd_mixed_rollout(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mixed_rollout_split(
            total_rollouts=args.total_rollouts, eta=args.eta
        )
    )
    return 0


def cmd_attribute_credit(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    scores = _json.loads(args.step_scores_json)
    _print(
        stele.attribute_step_credit(
            step_scores=scores, outcome_reward=args.outcome_reward
        )
    )
    return 0


def cmd_curiosity_explore(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.curiosity_explore_plan(
            visited_states=args.visited_states,
            novel_states=args.novel_states,
            budget=args.budget,
        )
    )
    return 0


def cmd_propose_skill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.propose_skill(description=args.description, kind=args.kind)
    )
    return 0


def cmd_practice_skill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.practice_skill_run(
            skill_id=args.skill_id,
            success=bool(args.success),
            steps=args.steps,
        )
    )
    return 0


def cmd_distill_skill_api(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.distill_skill_api(
            skill_id=args.skill_id, description=args.description
        )
    )
    return 0


def cmd_hone_skill_api(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hone_skill_api(
            unit_test_pass=bool(args.unit_pass),
            static_ok=not bool(args.static_fail),
        )
    )
    return 0


def cmd_skill_library_reg(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skill_library_register(
            api_name=args.api_name, library_size=args.library_size
        )
    )
    return 0


def cmd_transfer_skill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.transfer_skill_gate(
            donor_success_rate=args.donor_success_rate,
            recipient_baseline=args.recipient_baseline,
        )
    )
    return 0


def cmd_decompose_task(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.decompose_task_steps(query=args.query))
    return 0


def cmd_retrieve_step_skills(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.steps_json)
    catalog = _json.loads(args.catalog_json)
    _print(
        stele.retrieve_skills_for_steps(steps=steps, skill_catalog=catalog)
    )
    return 0


def cmd_compose_skill_dag(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    skills = _json.loads(args.step_skills_json)
    _print(stele.compose_skill_dag(step_skills=skills))
    return 0


def cmd_sad_loop(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    prior = _json.loads(args.prior_steps_json)
    hints = _json.loads(args.hints_json)
    _print(
        stele.sad_feedback_loop(
            prior_steps=prior, hint_skill_names=hints
        )
    )
    return 0


def cmd_granularity_match(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.granularity_match_check(
            step_count=args.step_count,
            expected_skills=args.expected_skills,
        )
    )
    return 0


def cmd_propose_reason_task(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.propose_reasoning_task(mode=args.mode, seed_hint=args.hint)
    )
    return 0


def cmd_validate_task_struct(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.validate_task_structure(
            has_program=bool(args.program),
            has_input=bool(args.has_input),
            has_output=bool(args.has_output),
            mode=args.mode,
        )
    )
    return 0


def cmd_learnability_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.learnability_reward(mean_solve_rate=args.mean_solve_rate)
    )
    return 0


def cmd_solve_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.solve_reward(answer_match=bool(args.match)))
    return 0


def cmd_abszero_objective(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.abszero_joint_objective(
            r_propose=args.r_propose, r_solve=args.r_solve
        )
    )
    return 0


def cmd_executor_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.executor_verify_gate(
            task_valid=bool(args.task_valid),
            answer_match=bool(args.answer_match),
        )
    )
    return 0


def cmd_challenger_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.challenger_propose(question=args.question))
    return 0


def cmd_uncertainty_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.uncertainty_reward(
            empirical_accuracy=args.empirical_accuracy
        )
    )
    return 0


def cmd_majority_vote(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    answers = _json.loads(args.answers_json)
    _print(stele.majority_vote_label(answers=answers))
    return 0


def cmd_curriculum_band(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.curriculum_band_filter(
            empirical_accuracy=args.empirical_accuracy, delta=args.delta
        )
    )
    return 0


def cmd_solver_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.solver_binary_reward(
            answer=args.answer, pseudo_label=args.pseudo_label
        )
    )
    return 0


def cmd_coevolve_round(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.coevolve_round_plan(
            round_index=args.round_index,
            challenger_updated=bool(args.challenger_updated),
            solver_updated=bool(args.solver_updated),
        )
    )
    return 0


def cmd_write_turn_mem(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.write_turn_memory(
            source_turn_id=args.source_turn_id, finding=args.finding
        )
    )
    return 0


def cmd_select_turn_mem(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ids = _json.loads(args.memory_ids_json)
    _print(stele.select_turn_memories(memory_ids=ids, budget=args.budget))
    return 0


def cmd_reconstruct_ctx(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    findings = _json.loads(args.findings_json)
    recent = _json.loads(args.recent_json)
    _print(
        stele.reconstruct_policy_context(
            selected_findings=findings, recent_turns=recent
        )
    )
    return 0


def cmd_credit_mask(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    sources = _json.loads(args.sources_json)
    selected = _json.loads(args.selected_json)
    _print(
        stele.provenance_credit_mask(
            source_turn_ids=sources,
            selected_source_ids=selected,
            outcome_positive=bool(args.positive),
        )
    )
    return 0


def cmd_collapse_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.history_collapse_gate(
            collapsed_summary_only=bool(args.summary_only)
        )
    )
    return 0


def cmd_budget_binding(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.budget_binding_check(
            history_chars=args.history_chars,
            budget_chars=args.budget_chars,
        )
    )
    return 0


def cmd_curriculum_task(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.curriculum_propose_task(
            task=args.task, requires_tool=bool(args.requires_tool)
        )
    )
    return 0


def cmd_tool_use_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tool_use_reward(tool_call_count=args.tool_call_count))
    return 0


def cmd_curriculum_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.curriculum_reward(
            r_uncertainty=args.r_uncertainty, r_tool=args.r_tool
        )
    )
    return 0


def cmd_executor_frontier(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.executor_frontier_filter(
            self_consistency=args.self_consistency
        )
    )
    return 0


def cmd_tool_pressure(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.tool_aware_pressure(
            executor_tool_success_rate=args.executor_tool_success_rate,
            prior_task_complexity=args.prior_task_complexity,
        )
    )
    return 0


def cmd_symbiotic_round(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.symbiotic_round_plan(
            round_index=args.round_index,
            curriculum_updated=bool(args.curriculum_updated),
            executor_updated=bool(args.executor_updated),
        )
    )
    return 0


def cmd_mae_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mae_propose_question(question=args.question))
    return 0


def cmd_mae_solve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mae_solve_attempt(answer=args.answer))
    return 0


def cmd_mae_judge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mae_judge_score(
            quality_score=args.quality_score,
            correctness_score=args.correctness_score,
        )
    )
    return 0


def cmd_mae_proposer_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mae_proposer_reward(
            quality_score=args.quality_score,
            solver_failed=bool(args.solver_failed),
        )
    )
    return 0


def cmd_mae_quality_filter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mae_quality_filter(quality_score=args.quality_score))
    return 0


def cmd_mae_triad(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mae_triad_round_plan(
            round_index=args.round_index, phase=args.phase
        )
    )
    return 0


def cmd_sage_challenge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sage_challenge_task(
            task=args.task, difficulty=args.difficulty
        )
    )
    return 0


def cmd_sage_plan(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    steps = _json.loads(args.steps_json)
    _print(stele.sage_plan_steps(steps=steps))
    return 0


def cmd_sage_solve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sage_solve_with_plan(
            plan_step_count=args.plan_step_count,
            followed_steps=args.followed_steps,
            answer=args.answer,
        )
    )
    return 0


def cmd_sage_critic(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sage_critic_filter(
            question_score=args.question_score,
            plan_score=args.plan_score,
        )
    )
    return 0


def cmd_sage_drift(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sage_drift_gate(difficulty_delta=args.difficulty_delta))
    return 0


def cmd_sage_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sage_closed_loop_round(
            round_index=args.round_index, phase=args.phase
        )
    )
    return 0


def cmd_mem_trigger(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memory_trigger_decide(
            at_boundary=bool(args.boundary),
            uncertainty=args.uncertainty,
        )
    )
    return 0


def cmd_weave_latent(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.weave_latent_memory(
            stimulus=args.stimulus, token_budget=args.tokens
        )
    )
    return 0


def cmd_interweave(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.interweave_cycle_plan(step=args.step))
    return 0


def cmd_faculty(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.faculty_classify(faculty=args.faculty))
    return 0


def cmd_weaver_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.weaver_only_update_gate(
            reasoner_frozen=bool(args.reasoner_frozen),
            weaver_updated=bool(args.weaver_updated),
        )
    )
    return 0


def cmd_sparse_invoke(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sparse_invoke_penalty(invoke_count=args.invoke_count))
    return 0


def cmd_text_experience(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.text_experience_store(kind=args.kind, content=args.content)
    )
    return 0


def cmd_crystallize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.crystallize_plan_to_tool(
            plan_id=args.plan_id, reuse_count=args.reuse_count
        )
    )
    return 0


def cmd_dual_retrieve(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    texts = _json.loads(args.text_json)
    codes = _json.loads(args.code_json)
    _print(stele.dual_retrieve(text_hits=texts, code_tool_ids=codes))
    return 0


def cmd_rep_tradeoff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.representation_tradeoff(
            construction_cost=args.construction_cost,
            execution_efficiency=args.execution_efficiency,
            transferability=args.transferability,
        )
    )
    return 0


def cmd_promote_kind(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.promote_kind_gate(kind=args.kind))
    return 0


def cmd_metis_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.metis_loop_plan(phase=args.phase))
    return 0


def cmd_samule_micro(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.single_trajectory_reflect(
            trajectory_id=args.trajectory_id, error_note=args.error_note
        )
    )
    return 0


def cmd_samule_meso(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    labels = _json.loads(args.labels_json)
    _print(stele.intra_task_taxonomy(error_labels=labels))
    return 0


def cmd_samule_macro(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.inter_task_transfer(
            error_type=args.error_type, strategy=args.strategy
        )
    )
    return 0


def cmd_samule_foresight(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.foresight_reflect(
            predicted=args.predicted, actual=args.actual
        )
    )
    return 0


def cmd_samule_fail_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.failure_centric_gate(
            success_count=args.success_count,
            failure_count=args.failure_count,
        )
    )
    return 0


def cmd_samule_merge(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    levels = _json.loads(args.levels_json)
    _print(stele.merge_reflections(levels_present=levels))
    return 0


def cmd_liveevo_exp(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.experience_bank_record(
            experience=args.experience, weight=args.weight
        )
    )
    return 0


def cmd_liveevo_meta(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.meta_guideline_record(guideline=args.guideline))
    return 0


def cmd_liveevo_compile(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.compile_task_guideline(
            task=args.task,
            experience_count=args.experience_count,
            has_meta=bool(args.has_meta),
        )
    )
    return 0


def cmd_liveevo_weight(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.update_experience_weight(
            weight=args.weight, delta_on_minus_off=args.delta
        )
    )
    return 0


def cmd_liveevo_forget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.forget_stale_experience(weight=args.weight))
    return 0


def cmd_liveevo_round(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.liveevo_online_round(phase=args.phase))
    return 0


def cmd_socratic_teach(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.socratic_teacher_craft(
            weakness=args.weakness, question=args.question
        )
    )
    return 0


def cmd_socratic_prefer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.socratic_solver_preference(
            success=bool(args.success), failed=bool(args.failed)
        )
    )
    return 0


def cmd_socratic_distill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.socratic_generator_distill(
            teacher_strategy=args.teacher_strategy
        )
    )
    return 0


def cmd_socratic_seed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.socratic_seed_bootstrap(seed_count=args.seed_count))
    return 0


def cmd_socratic_weakness(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.socratic_weakness_target(fail_rate=args.fail_rate))
    return 0


def cmd_socratic_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.socratic_closed_loop(phase=args.phase))
    return 0


def cmd_spiral_match(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spiral_self_play_match(
            game=args.game, role=args.role, won=bool(args.won)
        )
    )
    return 0


def cmd_spiral_rae(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spiral_rae_advantage(
            reward=args.reward, role_baseline=args.role_baseline
        )
    )
    return 0


def cmd_spiral_ema(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spiral_baseline_ema(
            baseline=args.baseline, reward=args.reward
        )
    )
    return 0


def cmd_spiral_pattern(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spiral_transfer_pattern(pattern=args.pattern))
    return 0


def cmd_spiral_opponent(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spiral_opponent_strength(
            self_elo=args.self_elo, opponent_elo=args.opponent_elo
        )
    )
    return 0


def cmd_spiral_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spiral_multi_game_plan(phase=args.phase))
    return 0


def cmd_smith_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smith_store_memory(tier=args.tier, content=args.content))
    return 0


def cmd_smith_tool(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.smith_create_tool(
            tool_name=args.tool_name, sandbox_pass=bool(args.sandbox_pass)
        )
    )
    return 0


def cmd_smith_episode(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smith_retrieve_episode(similarity=args.similarity))
    return 0


def cmd_smith_curriculum(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.smith_curriculum_difficulty(
            ensemble_fail_rate=args.ensemble_fail_rate
        )
    )
    return 0


def cmd_smith_reuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.smith_tool_reuse_gate(
            tool_exists=bool(args.tool_exists),
            task_similar=bool(args.task_similar),
        )
    )
    return 0


def cmd_smith_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smith_loop_plan(phase=args.phase))
    return 0


def cmd_hmem_leaf(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmem_leaf_event(topic=args.topic, timestamp=args.timestamp)
    )
    return 0


def cmd_hmem_consolidate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmem_consolidate_nodes(
            time_gap=args.time_gap, same_topic=bool(args.same_topic)
        )
    )
    return 0


def cmd_hmem_link(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmem_link_entities(
            entity_a=args.entity_a,
            entity_b=args.entity_b,
            relation=args.relation,
        )
    )
    return 0


def cmd_hmem_decompose(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    subs = _json.loads(args.sub_queries_json)
    _print(stele.hmem_decompose_query(sub_queries=subs))
    return 0


def cmd_hmem_hybrid(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmem_hybrid_retrieve(
            tree_hits=args.tree_hits, graph_hops=args.graph_hops
        )
    )
    return 0


def cmd_hmem_evolution(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmem_evolution_gate(
            short_term_count=args.short_term_count,
            consolidated_count=args.consolidated_count,
        )
    )
    return 0


def cmd_himem_segment(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.himem_segment_episode(
            topic=args.topic,
            surprise=args.surprise,
            surprise_threshold=args.surprise_threshold,
        )
    )
    return 0


def cmd_himem_note(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.himem_extract_note(knowledge=args.knowledge))
    return 0


def cmd_himem_link(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.himem_link_episode_note(
            episode_id=args.episode_id, note_id=args.note_id
        )
    )
    return 0


def cmd_himem_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.himem_retrieve_strategy(
            mode=args.mode, note_hit=args.note_hit
        )
    )
    return 0


def cmd_himem_reconsolidate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.himem_reconsolidate(
            conflict=args.conflict,
            missing_knowledge=args.missing_knowledge,
        )
    )
    return 0


def cmd_himem_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.himem_loop_plan(phase=args.phase))
    return 0


def cmd_hmeml_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmeml_store_level(level=args.level, content=args.content)
    )
    return 0


def cmd_hmeml_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hmeml_route_query(start_level=args.start_level))
    return 0


def cmd_hmeml_descend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmeml_descend(
            current_level=args.current_level, hit=args.hit
        )
    )
    return 0


def cmd_hmeml_parent(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmeml_parent_link(
            parent_level=args.parent_level, child_level=args.child_level
        )
    )
    return 0


def cmd_hmeml_efficiency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hmeml_efficiency_score(
            levels_scanned=args.levels_scanned,
            max_levels=args.max_levels,
        )
    )
    return 0


def cmd_hmeml_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hmeml_loop_plan(phase=args.phase))
    return 0


def cmd_hyperskill_subtask(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyperskill_add_subtask(label=args.label))
    return 0


def cmd_hyperskill_skill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyperskill_add_skill(label=args.label))
    return 0


def cmd_hyperskill_hyperedge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    subs = json.loads(args.subtask_ids_json)
    skills = json.loads(args.skill_ids_json)
    _print(
        stele.hyperskill_add_hyperedge(
            subtask_ids=list(subs),
            skill_ids=list(skills),
            utility=args.utility,
        )
    )
    return 0


def cmd_hyperskill_dual(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hyperskill_dual_path_retrieve(
            subtask_hits=args.subtask_hits,
            trajectory_hits=args.trajectory_hits,
        )
    )
    return 0


def cmd_hyperskill_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hyperskill_rank_skills(
            cooccurrence=args.cooccurrence, utility=args.utility
        )
    )
    return 0


def cmd_hyperskill_maintain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hyperskill_maintain_plan(
            utility=args.utility,
            prune_below=args.prune_below,
            redundant=bool(args.redundant),
        )
    )
    return 0


def cmd_hyperskill_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyperskill_loop_plan(phase=args.phase))
    return 0


def cmd_dcpm_day(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dcpm_day_write(
            belief=args.belief, superseded_id=args.superseded_id
        )
    )
    return 0


def cmd_dcpm_chain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dcpm_supersedes_chain(chain_len=args.chain_len))
    return 0


def cmd_dcpm_night(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dcpm_night_induce(
            fact_cluster_size=args.fact_cluster_size,
            min_cluster=args.min_cluster,
        )
    )
    return 0


def cmd_dcpm_collision(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dcpm_cross_domain_collision(
            behavioral_similarity=args.behavioral_similarity,
            semantic_similarity=args.semantic_similarity,
        )
    )
    return 0


def cmd_dcpm_level(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dcpm_hierarchy_level(level=args.level))
    return 0


def cmd_dcpm_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dcpm_loop_plan(phase=args.phase))
    return 0


def cmd_memos_cube(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memos_create_cube(kind=args.kind, content=args.content)
    )
    return 0


def cmd_memos_schedule(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memos_schedule(
            strategy=args.strategy, candidate_count=args.candidate_count
        )
    )
    return 0


def cmd_memos_lifecycle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memos_lifecycle(state=args.state, action=args.action)
    )
    return 0


def cmd_memos_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ids = json.loads(args.cube_ids_json)
    _print(stele.memos_compose(cube_ids=list(ids)))
    return 0


def cmd_memos_migrate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memos_migrate(
            from_kind=args.from_kind, to_kind=args.to_kind
        )
    )
    return 0


def cmd_memos_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memos_fuse_gate(
            compatible=bool(args.compatible),
            conflict=bool(args.conflict),
        )
    )
    return 0


def cmd_memos_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memos_loop_plan(phase=args.phase))
    return 0


def cmd_skillcraft_save(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skillcraft_save_skill(
            name=args.name,
            steps=args.steps,
            verified=bool(args.verified),
        )
    )
    return 0


def cmd_skillcraft_get(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.skillcraft_get_skill(skill_id=args.skill_id))
    return 0


def cmd_skillcraft_list(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skillcraft_list_skills(library_size=args.library_size)
    )
    return 0


def cmd_skillcraft_execute(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skillcraft_execute_skill(
            skill_exists=bool(args.skill_exists),
            params_ok=bool(args.params_ok),
        )
    )
    return 0


def cmd_skillcraft_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skillcraft_verify_skill(
            syntax_ok=bool(args.syntax_ok),
            runtime_ok=bool(args.runtime_ok),
            nonempty_output=bool(args.nonempty_output),
        )
    )
    return 0


def cmd_skillcraft_efficiency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.skillcraft_token_efficiency(
            tokens_baseline=args.tokens_baseline,
            tokens_skill_mode=args.tokens_skill_mode,
        )
    )
    return 0


def cmd_skillcraft_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.skillcraft_loop_plan(phase=args.phase))
    return 0


def cmd_cma_persist(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cma_persist(content=args.content))
    return 0


def cmd_cma_retain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cma_selective_retain(
            utility=args.utility,
            retain_threshold=args.retain_threshold,
        )
    )
    return 0


def cmd_cma_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cma_associative_route(
            cue=args.cue, hop_budget=args.hop_budget
        )
    )
    return 0


def cmd_cma_chain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cma_temporal_chain(
            event_a=args.event_a,
            event_b=args.event_b,
            order_ok=bool(args.order_ok),
        )
    )
    return 0


def cmd_cma_consolidate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cma_consolidate(
            episode_count=args.episode_count,
            min_episodes=args.min_episodes,
        )
    )
    return 0


def cmd_cma_probe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cma_probe_gate(
            probe=args.probe,
            supports_mutation=bool(args.supports_mutation),
        )
    )
    return 0


def cmd_cma_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cma_loop_plan(phase=args.phase))
    return 0


def cmd_agentfold_split(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agentfold_workspace_split(
            working_tokens=args.working_tokens,
            long_term_blocks=args.long_term_blocks,
        )
    )
    return 0


def cmd_agentfold_fold(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agentfold_fold_command(
            mode=args.mode,
            range_start=args.range_start,
            step_t=args.step_t,
        )
    )
    return 0


def cmd_agentfold_granular(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agentfold_granular_condense(
            last_step_tokens=args.last_step_tokens,
            target_tokens=args.target_tokens,
        )
    )
    return 0


def cmd_agentfold_deep(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agentfold_deep_consolidate(blocks_merged=args.blocks_merged)
    )
    return 0


def cmd_agentfold_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agentfold_context_budget(
            turns=args.turns,
            tokens=args.tokens,
            soft_cap=args.soft_cap,
        )
    )
    return 0


def cmd_agentfold_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.agentfold_loop_plan(phase=args.phase))
    return 0


def cmd_memengine_fn(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memengine_register_function(name=args.name))
    return 0


def cmd_memengine_op(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ids = json.loads(args.function_ids_json)
    _print(
        stele.memengine_compose_operation(
            op=args.op, function_ids=list(ids)
        )
    )
    return 0


def cmd_memengine_model(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ids = json.loads(args.operation_ids_json)
    _print(
        stele.memengine_bind_model(
            model_name=args.model_name, operation_ids=list(ids)
        )
    )
    return 0


def cmd_memengine_config(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memengine_config_set(key=args.key, value=args.value))
    return 0


def cmd_memengine_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memengine_reflect_plan(
            entries=args.entries, min_entries=args.min_entries
        )
    )
    return 0


def cmd_memengine_pluggable(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memengine_pluggable(
            agent_compatible=bool(args.agent_compatible)
        )
    )
    return 0


def cmd_memengine_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memengine_loop_plan(phase=args.phase))
    return 0


def cmd_simplemem_compress(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.simplemem_compress(
            raw_turns=args.raw_turns, window=args.window
        )
    )
    return 0


def cmd_simplemem_synthesize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.simplemem_synthesize(
            related_facts=args.related_facts,
            min_related=args.min_related,
        )
    )
    return 0


def cmd_simplemem_intent(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.simplemem_intent_scope(complexity=args.complexity))
    return 0


def cmd_simplemem_index(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.simplemem_multiview_index(
            dense=bool(args.dense),
            sparse=bool(args.sparse),
            metadata=bool(args.metadata),
        )
    )
    return 0


def cmd_simplemem_ratio(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.simplemem_token_ratio(
            tokens_baseline=args.tokens_baseline,
            tokens_simplemem=args.tokens_simplemem,
        )
    )
    return 0


def cmd_simplemem_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.simplemem_loop_plan(phase=args.phase))
    return 0


def cmd_omem_persona(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.omem_extract_persona(
            trait=args.trait, confidence=args.confidence
        )
    )
    return 0


def cmd_omem_event(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.omem_update_event(
            event=args.event, timestamp=args.timestamp
        )
    )
    return 0


def cmd_omem_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.omem_hierarchy_retrieve(
            channel=args.channel, hits=args.hits
        )
    )
    return 0


def cmd_omem_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.omem_profile_gate(
            confidence=args.confidence,
            min_confidence=args.min_confidence,
        )
    )
    return 0


def cmd_omem_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.omem_scale_memory_time(
            interactions=args.interactions,
            memory_units=args.memory_units,
        )
    )
    return 0


def cmd_omem_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.omem_loop_plan(phase=args.phase))
    return 0


def cmd_mandol_basic(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mandol_basic_unit(content=args.content))
    return 0


def cmd_mandol_agglomerate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    ids = json.loads(args.basic_ids_json)
    _print(stele.mandol_agglomerate(basic_ids=list(ids)))
    return 0


def cmd_mandol_map(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mandol_semantic_map_put(
            key=args.key, vector_ok=bool(args.vector_ok)
        )
    )
    return 0


def cmd_mandol_hybrid(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mandol_hybrid_retrieve(
            vector_hits=args.vector_hits, graph_hops=args.graph_hops
        )
    )
    return 0


def cmd_mandol_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mandol_query_route(query_type=args.query_type))
    return 0


def cmd_mandol_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mandol_token_budget(
            selected_tokens=args.selected_tokens,
            max_tokens=args.max_tokens,
        )
    )
    return 0


def cmd_mandol_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mandol_loop_plan(phase=args.phase))
    return 0


def cmd_memanto_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memanto_store_typed(
            category=args.category, content=args.content
        )
    )
    return 0


def cmd_memanto_conflict(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memanto_conflict_resolve(
            conflict=bool(args.conflict),
            newer_wins=bool(args.newer_wins),
        )
    )
    return 0


def cmd_memanto_version(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memanto_version(
            entry_id=args.entry_id, version=args.version
        )
    )
    return 0


def cmd_memanto_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memanto_retrieve(
            query=args.query, single_query=not bool(args.multi_query)
        )
    )
    return 0


def cmd_memanto_latency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memanto_latency_gate(
            latency_ms=args.latency_ms, soft_cap_ms=args.soft_cap_ms
        )
    )
    return 0


def cmd_memanto_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memanto_loop_plan(phase=args.phase))
    return 0


def cmd_zep_episode(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.zep_add_episode(
            content=args.content, valid_at=args.valid_at
        )
    )
    return 0


def cmd_zep_link(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.zep_link_entities(
            entity_a=args.entity_a,
            entity_b=args.entity_b,
            relation=args.relation,
        )
    )
    return 0


def cmd_zep_bitemporal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.zep_bitemporal(
            valid_at=args.valid_at, transaction_at=args.transaction_at
        )
    )
    return 0


def cmd_zep_synthesize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.zep_synthesize(
            conversation_facts=args.conversation_facts,
            business_facts=args.business_facts,
        )
    )
    return 0


def cmd_zep_cross(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.zep_cross_session(
            sessions=args.sessions, min_sessions=args.min_sessions
        )
    )
    return 0


def cmd_zep_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.zep_loop_plan(phase=args.phase))
    return 0


def cmd_memgpt_capacity(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgpt_main_capacity(
            used_tokens=args.used_tokens,
            max_tokens=args.max_tokens,
            warn_ratio=args.warn_ratio,
        )
    )
    return 0


def cmd_memgpt_page_out(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memgpt_page_out(content=args.content, tier=args.tier))
    return 0


def cmd_memgpt_page_in(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgpt_page_in(page_id=args.page_id, fits=bool(args.fits))
    )
    return 0


def cmd_memgpt_recall(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgpt_recall_search(query=args.query, hits=args.hits)
    )
    return 0


def cmd_memgpt_archival(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgpt_archival_search(query=args.query, page=args.page)
    )
    return 0


def cmd_memgpt_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memgpt_loop_plan(phase=args.phase))
    return 0


def cmd_ripple_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ripple_store_episode(content=args.content))
    return 0


def cmd_ripple_link(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ripple_link_entity(
            episode_id=args.episode_id, entity=args.entity
        )
    )
    return 0


def cmd_ripple_seed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ripple_seed_retrieve(
            query=args.query, seed_hits=args.seed_hits
        )
    )
    return 0


def cmd_ripple_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ripple_expand(
            seeds=args.seeds, hop=args.hop, max_hops=args.max_hops
        )
    )
    return 0


def cmd_ripple_recollect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ripple_recollect_gate(
            seed_hits=args.seed_hits, associated=args.associated
        )
    )
    return 0


def cmd_ripple_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ripple_loop_plan(phase=args.phase))
    return 0


def cmd_flux_connect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flux_connect_form(
            src=args.src, dst=args.dst, relation=args.relation
        )
    )
    return 0


def cmd_flux_refine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flux_feedback_refine(
            edge_id=args.edge_id,
            feedback=args.feedback,
            keep=bool(args.keep),
        )
    )
    return 0


def cmd_flux_consolidate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flux_consolidate(
            circuits=args.circuits, min_success=args.min_success
        )
    )
    return 0


def cmd_flux_repair(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flux_repair_link(
            missing=bool(args.missing), repaired=bool(args.repaired)
        )
    )
    return 0


def cmd_flux_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flux_prune_interference(
            noise_score=args.noise_score, threshold=args.threshold
        )
    )
    return 0


def cmd_flux_maturity(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flux_maturity_gate(
            generalizability=args.generalizability,
            min_score=args.min_score,
        )
    )
    return 0


def cmd_flux_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flux_loop_plan(phase=args.phase))
    return 0


def cmd_qumem_segment(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qumem_segment_episode(
            content=args.content, continuity=args.continuity
        )
    )
    return 0


def cmd_qumem_decompose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qumem_decompose(
            episode_id=args.episode_id, mem_type=args.mem_type
        )
    )
    return 0


def cmd_qumem_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qumem_plan_queries(task=args.task, needs=args.needs))
    return 0


def cmd_qumem_infer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qumem_infer_user_state(
            factual=args.factual,
            preference=args.preference,
            insight=args.insight,
        )
    )
    return 0


def cmd_qumem_temporal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qumem_temporal_valid(
            event_ts=args.event_ts,
            query_ts=args.query_ts,
            stale=bool(args.stale),
        )
    )
    return 0


def cmd_qumem_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qumem_loop_plan(phase=args.phase))
    return 0


def cmd_viking_extract(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.viking_extract_event(
            content=args.content, high_value=bool(args.high_value)
        )
    )
    return 0


def cmd_viking_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.viking_update_entity(
            entity=args.entity, event_id=args.event_id
        )
    )
    return 0


def cmd_viking_compress(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.viking_timeline_compress(topic=args.topic, items=args.items)
    )
    return 0


def cmd_viking_recall(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.viking_time_weighted_recall(
            query=args.query, recency_weight=args.recency_weight
        )
    )
    return 0


def cmd_viking_rerank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.viking_rerank(candidates=args.candidates, top_k=args.top_k)
    )
    return 0


def cmd_viking_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.viking_loop_plan(phase=args.phase))
    return 0


def cmd_recmem_buffer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.recmem_buffer_subconscious(content=args.content))
    return 0


def cmd_recmem_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.recmem_recurrence_gate(
            similar_count=args.similar_count, threshold=args.threshold
        )
    )
    return 0


def cmd_recmem_consolidate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.recmem_consolidate_episodic(cluster_size=args.cluster_size)
    )
    return 0


def cmd_recmem_refine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.recmem_semantic_refine(omitted_facts=args.omitted_facts)
    )
    return 0


def cmd_recmem_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.recmem_merge_retrieve(
            subconscious=args.subconscious,
            episodic=args.episodic,
            semantic=args.semantic,
        )
    )
    return 0


def cmd_recmem_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.recmem_loop_plan(phase=args.phase))
    return 0


def cmd_mbank_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mbank_store_memory(
            content=args.content, significance=args.significance
        )
    )
    return 0


def cmd_mbank_summon(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mbank_summon(query=args.query, hits=args.hits))
    return 0


def cmd_mbank_personality(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mbank_personality_synth(traits=args.traits))
    return 0


def cmd_mbank_forget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mbank_forget_curve(
            days_elapsed=args.days_elapsed, strength=args.strength
        )
    )
    return 0


def cmd_mbank_reinforce(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mbank_reinforce(memory_id=args.memory_id, boost=args.boost)
    )
    return 0


def cmd_mbank_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mbank_loop_plan(phase=args.phase))
    return 0


def cmd_rfmem_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rfmem_familiarity_score(
            mean_score=args.mean_score, entropy=args.entropy
        )
    )
    return 0


def cmd_rfmem_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rfmem_path_route(
            mean_score=args.mean_score,
            entropy=args.entropy,
            high_mean=args.high_mean,
            low_entropy=args.low_entropy,
        )
    )
    return 0


def cmd_rfmem_topk(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rfmem_top_k_familiar(
            candidates=args.candidates, top_k=args.top_k
        )
    )
    return 0


def cmd_rfmem_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rfmem_recollect_expand(
            clusters=args.clusters, hops=args.hops, max_hops=args.max_hops
        )
    )
    return 0


def cmd_rfmem_mix(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rfmem_alpha_mix(
            alpha=args.alpha, query_weight=args.query_weight
        )
    )
    return 0


def cmd_rfmem_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rfmem_loop_plan(phase=args.phase))
    return 0


def cmd_agemem_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.agemem_ltm_store(content=args.content, tier=args.tier))
    return 0


def cmd_agemem_stm(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agemem_stm_manage(capacity=args.capacity, used=args.used)
    )
    return 0


def cmd_agemem_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.agemem_retrieve(query=args.query, hits=args.hits))
    return 0


def cmd_agemem_summarize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.agemem_summarize(entries=args.entries))
    return 0


def cmd_agemem_discard(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.agemem_discard_plan(
            memory_id=args.memory_id, reason=args.reason
        )
    )
    return 0


def cmd_agemem_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.agemem_loop_plan(phase=args.phase))
    return 0


def cmd_memgas_unit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgas_unit(
            content=args.content, granularity=args.granularity
        )
    )
    return 0


def cmd_memgas_associate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgas_associate(
            new_id=args.new_id, cluster_size=args.cluster_size
        )
    )
    return 0


def cmd_memgas_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memgas_entropy_route(entropy=args.entropy, low=args.low))
    return 0


def cmd_memgas_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgas_select_granularity(
            preferred=args.preferred, entropy=args.entropy
        )
    )
    return 0


def cmd_memgas_filter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memgas_filter_plan(
            candidates=args.candidates, keep=args.keep
        )
    )
    return 0


def cmd_memgas_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memgas_loop_plan(phase=args.phase))
    return 0


def cmd_memwalker_segment(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memwalker_segment(
            content=args.content, chunk_size=args.chunk_size
        )
    )
    return 0


def cmd_memwalker_build(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memwalker_build_node(summary=args.summary, level=args.level)
    )
    return 0


def cmd_memwalker_nav(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memwalker_navigate(node_id=args.node_id, action=args.action)
    )
    return 0


def cmd_memwalker_gather(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memwalker_gather(leaves=args.leaves, budget=args.budget)
    )
    return 0


def cmd_memwalker_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memwalker_path_gate(
            depth=args.depth, max_depth=args.max_depth
        )
    )
    return 0


def cmd_memwalker_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memwalker_loop_plan(phase=args.phase))
    return 0


def cmd_mgr_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mgr_store_layer(content=args.content, layer=args.layer))
    return 0


def cmd_mgr_detect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mgr_detect_conflict(
            facts=args.facts, anomalies=args.anomalies
        )
    )
    return 0


def cmd_mgr_resolve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mgr_resolve_plan(conflict_id=args.conflict_id))
    return 0


def cmd_mgr_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mgr_multilayer_retrieve(
            query=args.query, layers_hit=args.layers_hit
        )
    )
    return 0


def cmd_mgr_propagate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mgr_propagate(seeds=args.seeds, damping=args.damping)
    )
    return 0


def cmd_mgr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mgr_loop_plan(phase=args.phase))
    return 0


def cmd_raptor_embed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.raptor_embed_chunk(content=args.content))
    return 0


def cmd_raptor_cluster(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.raptor_cluster(chunks=args.chunks, clusters=args.clusters)
    )
    return 0


def cmd_raptor_summarize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.raptor_summarize_node(
            level=args.level, children=args.children
        )
    )
    return 0


def cmd_raptor_traverse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.raptor_tree_traverse(
            depth=args.depth, keep_per_level=args.keep_per_level
        )
    )
    return 0


def cmd_raptor_collapsed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.raptor_collapsed_retrieve(
            candidates=args.candidates, top_k=args.top_k
        )
    )
    return 0


def cmd_raptor_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.raptor_loop_plan(phase=args.phase))
    return 0


def cmd_lightrag_entity(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lightrag_index_entity(name=args.name))
    return 0


def cmd_lightrag_relation(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lightrag_index_relation(
            src=args.src, dst=args.dst, rel=args.rel
        )
    )
    return 0


def cmd_lightrag_dual(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lightrag_dual_retrieve(query=args.query, level=args.level)
    )
    return 0


def cmd_lightrag_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lightrag_incremental_update(new_docs=args.new_docs))
    return 0


def cmd_lightrag_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lightrag_graph_vector_fuse(
            graph_hits=args.graph_hits, vector_hits=args.vector_hits
        )
    )
    return 0


def cmd_lightrag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lightrag_loop_plan(phase=args.phase))
    return 0


def cmd_memorag_memorize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memorag_memorize(corpus_chars=args.corpus_chars))
    return 0


def cmd_memorag_clue(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memorag_clue(query=args.query, draft=args.draft))
    return 0


def cmd_memorag_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memorag_retrieve_by_clue(
            clue_id=args.clue_id, hits=args.hits
        )
    )
    return 0


def cmd_memorag_dual(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memorag_dual_system(role=args.role))
    return 0


def cmd_memorag_generate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memorag_generate_plan(evidence=args.evidence))
    return 0


def cmd_memorag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memorag_loop_plan(phase=args.phase))
    return 0


def cmd_pageindex_toc(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pageindex_build_toc(title=args.title, sections=args.sections)
    )
    return 0


def cmd_pageindex_section(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pageindex_add_section(
            parent_id=args.parent_id,
            heading=args.heading,
            page_start=args.page_start,
        )
    )
    return 0


def cmd_pageindex_nav(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pageindex_reason_nav(
            query=args.query, candidates=args.candidates
        )
    )
    return 0


def cmd_pageindex_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pageindex_select_section(
            section_id=args.section_id, relevant=bool(args.relevant)
        )
    )
    return 0


def cmd_pageindex_trace(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pageindex_trace_path(hops=args.hops))
    return 0


def cmd_pageindex_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pageindex_loop_plan(phase=args.phase))
    return 0


def cmd_selfrag_need(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.selfrag_need_retrieve(
            confidence=args.confidence, threshold=args.threshold
        )
    )
    return 0


def cmd_selfrag_relevance(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfrag_relevance_critique(relevant=bool(args.relevant)))
    return 0


def cmd_selfrag_support(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfrag_support_critique(supported=bool(args.supported)))
    return 0


def cmd_selfrag_utility(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfrag_utility_critique(utility=args.utility))
    return 0


def cmd_selfrag_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfrag_select_best(scores=args.scores, pick=args.pick))
    return 0


def cmd_selfrag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfrag_loop_plan(phase=args.phase))
    return 0


def cmd_memobrain_dep(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memobrain_dep_edge(
            src_step=args.src_step, dst_step=args.dst_step
        )
    )
    return 0


def cmd_memobrain_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memobrain_prune_invalid(
            step_id=args.step_id, invalid=bool(args.invalid)
        )
    )
    return 0


def cmd_memobrain_fold(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memobrain_fold_subtraj(steps=args.steps))
    return 0


def cmd_memobrain_flush(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memobrain_flush_budget(used=args.used, budget=args.budget)
    )
    return 0


def cmd_memobrain_salience(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.memobrain_salience_keep(
            salience=args.salience, min_keep=args.min_keep
        )
    )
    return 0


def cmd_memobrain_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.memobrain_loop_plan(phase=args.phase))
    return 0


def cmd_crag_evaluate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.crag_evaluate_retrieval(confidence=args.confidence))
    return 0


def cmd_crag_refine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.crag_correct_refine(chunks=args.chunks))
    return 0


def cmd_crag_web(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.crag_web_fallback_plan(trigger=bool(args.trigger)))
    return 0


def cmd_crag_blend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.crag_ambiguous_blend(
            local_hits=args.local_hits, web_hits=args.web_hits
        )
    )
    return 0


def cmd_crag_action(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.crag_action_select(action=args.action))
    return 0


def cmd_crag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.crag_loop_plan(phase=args.phase))
    return 0


def cmd_hyde_hyp(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyde_hypothetical_doc(query=args.query))
    return 0


def cmd_hyde_encode(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyde_encode_proxy(hyp_id=args.hyp_id))
    return 0


def cmd_hyde_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyde_retrieve_by_hyp(vec_id=args.vec_id, k=args.k))
    return 0


def cmd_hyde_filter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyde_filter_hallucination(retained=args.retained))
    return 0


def cmd_hyde_ground(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.hyde_ground_corpus(hits=args.hits, grounded=args.grounded)
    )
    return 0


def cmd_hyde_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyde_loop_plan(phase=args.phase))
    return 0


def cmd_adaptiverag_classify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adaptiverag_classify_complexity(hops=args.hops))
    return 0


def cmd_adaptiverag_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adaptiverag_select_strategy(level=args.level))
    return 0


def cmd_adaptiverag_none(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.adaptiverag_no_retrieve(
            parametric_ok=bool(args.parametric_ok)
        )
    )
    return 0


def cmd_adaptiverag_single(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adaptiverag_single_step(hits=args.hits))
    return 0


def cmd_adaptiverag_multi(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adaptiverag_multi_step(steps=args.steps))
    return 0


def cmd_adaptiverag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adaptiverag_loop_plan(phase=args.phase))
    return 0


def cmd_flare_anticipate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flare_anticipate_sentence(context=args.context))
    return 0


def cmd_flare_confidence(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flare_low_confidence(
            confidence=args.confidence, threshold=args.threshold
        )
    )
    return 0


def cmd_flare_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flare_retrieve_for_regen(query=args.query, k=args.k))
    return 0


def cmd_flare_regen(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flare_regenerate_sentence(
            sent_id=args.sent_id, with_docs=bool(args.with_docs)
        )
    )
    return 0


def cmd_flare_step(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flare_active_step(
            step=args.step, retrieved=bool(args.retrieved)
        )
    )
    return 0


def cmd_flare_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flare_loop_plan(phase=args.phase))
    return 0


def cmd_graphreader_build(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.graphreader_build_node(chunk=args.chunk))
    return 0


def cmd_graphreader_read(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.graphreader_read_node(node_id=args.node_id))
    return 0


def cmd_graphreader_neighbors(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.graphreader_read_neighbors(
            node_id=args.node_id, hops=args.hops
        )
    )
    return 0


def cmd_graphreader_note(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.graphreader_note_insight(text=args.text))
    return 0


def cmd_graphreader_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.graphreader_reflect_plan(enough=bool(args.enough)))
    return 0


def cmd_graphreader_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.graphreader_loop_plan(phase=args.phase))
    return 0


def cmd_gretriever_prize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.gretriever_node_prize(node_id=args.node_id, prize=args.prize)
    )
    return 0


def cmd_gretriever_pcst(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.gretriever_pcst_select(nodes=args.nodes, budget=args.budget)
    )
    return 0


def cmd_gretriever_subgraph(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gretriever_subgraph(selected=args.selected))
    return 0


def cmd_gretriever_prompt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gretriever_soft_prompt_plan(subgraph_id=args.subgraph_id))
    return 0


def cmd_gretriever_highlight(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gretriever_highlight(nodes=args.nodes))
    return 0


def cmd_gretriever_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gretriever_loop_plan(phase=args.phase))
    return 0


def cmd_rqrag_rewrite(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rqrag_rewrite(query=args.query))
    return 0


def cmd_rqrag_decompose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rqrag_decompose(query=args.query, parts=args.parts))
    return 0


def cmd_rqrag_disambiguate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rqrag_disambiguate(query=args.query, intents=args.intents)
    )
    return 0


def cmd_rqrag_mode(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rqrag_refine_mode(mode=args.mode))
    return 0


def cmd_rqrag_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rqrag_retrieve_refined(refined_id=args.refined_id, k=args.k)
    )
    return 0


def cmd_rqrag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rqrag_loop_plan(phase=args.phase))
    return 0


def cmd_ircot_cot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ircot_cot_step(step=args.step, claim=args.claim))
    return 0


def cmd_ircot_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ircot_retrieve_guided(step_id=args.step_id, k=args.k))
    return 0


def cmd_ircot_interleave(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ircot_interleave(
            cot_steps=args.cot_steps, retrieves=args.retrieves
        )
    )
    return 0


def cmd_ircot_ready(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ircot_answer_ready(enough=bool(args.enough)))
    return 0


def cmd_ircot_grounded(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ircot_hallucination_check(grounded=args.grounded))
    return 0


def cmd_ircot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ircot_loop_plan(phase=args.phase))
    return 0


def cmd_replug_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.replug_retrieve_docs(query=args.query, k=args.k))
    return 0


def cmd_replug_prepend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.replug_prepend_doc(doc_id=args.doc_id, context=args.context)
    )
    return 0


def cmd_replug_ensemble(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.replug_ensemble_probs(packs=args.packs))
    return 0


def cmd_replug_supervise(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.replug_supervise_retriever(lm_gain=args.lm_gain))
    return 0


def cmd_replug_forward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.replug_blackbox_forward(pack_id=args.pack_id))
    return 0


def cmd_replug_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.replug_loop_plan(phase=args.phase))
    return 0


def cmd_iterretgen_generate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.iterretgen_generate(
            iteration=args.iteration, draft=args.draft
        )
    )
    return 0


def cmd_iterretgen_query(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.iterretgen_use_as_query(gen_id=args.gen_id))
    return 0


def cmd_iterretgen_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.iterretgen_retrieve_next(
            query_from=args.query_from, k=args.k
        )
    )
    return 0


def cmd_iterretgen_iterate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.iterretgen_iterate(
            round_n=args.round_n, max_rounds=args.max_rounds
        )
    )
    return 0


def cmd_iterretgen_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.iterretgen_adapt_retriever(improve=bool(args.improve)))
    return 0


def cmd_iterretgen_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.iterretgen_loop_plan(phase=args.phase))
    return 0


def cmd_planrag_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.planrag_make_plan(question=args.question))
    return 0


def cmd_planrag_query(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.planrag_analysis_query(
            plan_id=args.plan_id, query=args.query
        )
    )
    return 0


def cmd_planrag_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.planrag_retrieve_data(query_id=args.query_id, rows=args.rows)
    )
    return 0


def cmd_planrag_replan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.planrag_replan(need_replan=bool(args.need_replan)))
    return 0


def cmd_planrag_decide(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.planrag_decide(ready=bool(args.ready)))
    return 0


def cmd_planrag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.planrag_loop_plan(phase=args.phase))
    return 0


def cmd_rrr_rewrite(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rrr_rewrite_query(query=args.query))
    return 0


def cmd_rrr_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rrr_retrieve(rewrite_id=args.rewrite_id, k=args.k))
    return 0


def cmd_rrr_read(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rrr_read(hits=args.hits))
    return 0


def cmd_rrr_feedback(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rrr_reader_feedback(reward=args.reward))
    return 0


def cmd_rrr_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rrr_train_rewriter_plan(improve=bool(args.improve)))
    return 0


def cmd_rrr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rrr_loop_plan(phase=args.phase))
    return 0


def cmd_dsp_demo(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dsp_bootstrap_demo(task=args.task, n=args.n))
    return 0


def cmd_dsp_search(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dsp_search(query=args.query, k=args.k))
    return 0


def cmd_dsp_predict(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dsp_predict(grounded=bool(args.grounded)))
    return 0


def cmd_dsp_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dsp_compose_program(stages=args.stages))
    return 0


def cmd_dsp_hop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dsp_multihop_hop(hop=args.hop))
    return 0


def cmd_dsp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dsp_loop_plan(phase=args.phase))
    return 0


def cmd_genread_context(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.genread_generate_context(question=args.question))
    return 0


def cmd_genread_ground(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.genread_ground_optional(
            ctx_id=args.ctx_id, use_retriever=bool(args.use_retriever)
        )
    )
    return 0


def cmd_genread_answer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.genread_answer(ctx_id=args.ctx_id))
    return 0


def cmd_genread_compare(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.genread_compare_retrieve(
            gen_hits=args.gen_hits, retrieve_hits=args.retrieve_hits
        )
    )
    return 0


def cmd_genread_hybrid(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.genread_hybrid(
            generate=bool(args.generate), retrieve=bool(args.retrieve)
        )
    )
    return 0


def cmd_genread_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.genread_loop_plan(phase=args.phase))
    return 0


def cmd_selfask_followup(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfask_followup(question=args.question, hop=args.hop))
    return 0


def cmd_selfask_search(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.selfask_search_intercept(
            followup_id=args.followup_id, k=args.k
        )
    )
    return 0


def cmd_selfask_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfask_compose_answer(followups=args.followups))
    return 0


def cmd_selfask_stop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfask_stop(enough=bool(args.enough)))
    return 0


def cmd_selfask_demos(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfask_demo_prompt(demos=args.demos))
    return 0


def cmd_selfask_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.selfask_loop_plan(phase=args.phase))
    return 0


def cmd_react_thought(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.react_thought(step=args.step, text=args.text))
    return 0


def cmd_react_action(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.react_action(action=args.action, arg=args.arg))
    return 0


def cmd_react_observe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.react_observe(observation=args.observation))
    return 0


def cmd_react_finish(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.react_finish(answer=args.answer))
    return 0


def cmd_react_trajectory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.react_trajectory(steps=args.steps))
    return 0


def cmd_react_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.react_loop_plan(phase=args.phase))
    return 0


def cmd_tog_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tog_init_entity(entity=args.entity))
    return 0


def cmd_tog_explore(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.tog_explore_neighbors(
            entity_id=args.entity_id, width=args.width
        )
    )
    return 0


def cmd_tog_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tog_beam_prune(paths=args.paths, keep=args.keep))
    return 0


def cmd_tog_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tog_path_score(path_id=args.path_id, score=args.score))
    return 0


def cmd_tog_answer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tog_answer_from_paths(path_count=args.path_count))
    return 0


def cmd_tog_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tog_loop_plan(phase=args.phase))
    return 0


def cmd_tf_candidate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tf_api_candidate(api=args.api, args=args.args))
    return 0


def cmd_tf_filter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.tf_filter_call(
            candidate_id=args.candidate_id, useful=bool(args.useful)
        )
    )
    return 0


def cmd_tf_execute(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tf_execute_proxy(api=args.api))
    return 0


def cmd_tf_incorporate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tf_incorporate_result(result_id=args.result_id))
    return 0


def cmd_tf_demos(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tf_demo_apis(count=args.count))
    return 0


def cmd_tf_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tf_loop_plan(phase=args.phase))
    return 0


def cmd_rx_trial(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rx_trial_run(task=args.task, trial=args.trial))
    return 0


def cmd_rx_evaluate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rx_evaluate(
            trial_id=args.trial_id, success=bool(args.success)
        )
    )
    return 0


def cmd_rx_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rx_verbal_reflect(
            trial_id=args.trial_id, feedback=args.feedback
        )
    )
    return 0


def cmd_rx_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rx_memory_store(reflection_id=args.reflection_id))
    return 0


def cmd_rx_next(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rx_next_trial(reflections=args.reflections))
    return 0


def cmd_rx_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rx_loop_plan(phase=args.phase))
    return 0


def cmd_sc_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sc_sample_path(path_idx=args.path_idx, answer=args.answer)
    )
    return 0


def cmd_sc_collect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sc_collect_answers(n=args.n))
    return 0


def cmd_sc_vote(args: argparse.Namespace) -> int:
    import json as _json

    stele = _open(args.store, store_id=None, now=args.now, create=False)
    votes = _json.loads(args.votes_json)
    _print(stele.sc_majority_vote(votes=votes))
    return 0


def cmd_sc_marginalize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sc_marginalize(
            paths=args.paths, unique_answers=args.unique_answers
        )
    )
    return 0


def cmd_sc_temp(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sc_temperature(temp=args.temp))
    return 0


def cmd_sc_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sc_loop_plan(phase=args.phase))
    return 0


def cmd_tot_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tot_propose(parent_id=args.parent_id, text=args.text))
    return 0


def cmd_tot_evaluate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tot_evaluate(node_id=args.node_id, score=args.score))
    return 0


def cmd_tot_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tot_expand(breadth=args.breadth, depth=args.depth))
    return 0


def cmd_tot_backtrack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tot_backtrack(from_node=args.from_node))
    return 0


def cmd_tot_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tot_select_best(candidates=args.candidates))
    return 0


def cmd_tot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tot_loop_plan(phase=args.phase))
    return 0


def cmd_ltm_decompose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltm_decompose(problem=args.problem, n_subs=args.n_subs))
    return 0


def cmd_ltm_solve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ltm_solve_sub(decomp_id=args.decomp_id, sub_idx=args.sub_idx)
    )
    return 0


def cmd_ltm_carry(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltm_carry_forward(answered=args.answered))
    return 0


def cmd_ltm_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltm_compose_final(subs_done=args.subs_done))
    return 0


def cmd_ltm_easy(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltm_easy_to_hard(exemplars=args.exemplars))
    return 0


def cmd_ltm_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltm_loop_plan(phase=args.phase))
    return 0


def cmd_got_add(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.got_add_thought(text=args.text))
    return 0


def cmd_got_link(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.got_link(src=args.src, dst=args.dst))
    return 0


def cmd_got_aggregate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.got_aggregate(inputs=args.inputs))
    return 0


def cmd_got_feedback(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.got_feedback(vertex_id=args.vertex_id))
    return 0


def cmd_got_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.got_score_graph(vertices=args.vertices, edges=args.edges)
    )
    return 0


def cmd_got_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.got_loop_plan(phase=args.phase))
    return 0


def cmd_pot_emit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pot_emit_program(problem=args.problem, lang=args.lang))
    return 0


def cmd_pot_run(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pot_sandbox_run(program_id=args.program_id))
    return 0


def cmd_pot_read(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pot_read_result(result_id=args.result_id))
    return 0


def cmd_pot_sc(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pot_self_consistency(samples=args.samples))
    return 0


def cmd_pot_disentangle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pot_disentangle(compute_offloaded=bool(args.offload))
    )
    return 0


def cmd_pot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pot_loop_plan(phase=args.phase))
    return 0


def cmd_aot_load(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aot_load_algorithm(name=args.name))
    return 0


def cmd_aot_explore(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.aot_explore_subtree(depth=args.depth, branch=args.branch)
    )
    return 0


def cmd_aot_tunnel(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aot_tunnel_vision(activate=bool(args.activate)))
    return 0


def cmd_aot_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aot_query_budget(queries=args.queries))
    return 0


def cmd_aot_surpass(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aot_surpass_algo(intuition=bool(args.intuition)))
    return 0


def cmd_aot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aot_loop_plan(phase=args.phase))
    return 0


def cmd_rap_state(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rap_world_state(state=args.state))
    return 0


def cmd_rap_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rap_expand(state_id=args.state_id, actions=args.actions)
    )
    return 0


def cmd_rap_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rap_reward(state_id=args.state_id, reward=args.reward)
    )
    return 0


def cmd_rap_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rap_select_path(visits=args.visits))
    return 0


def cmd_rap_balance(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rap_balance(explore=args.explore))
    return 0


def cmd_rap_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rap_loop_plan(phase=args.phase))
    return 0


def cmd_sot_skeleton(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sot_emit_skeleton(question=args.question))
    return 0


def cmd_sot_extract(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sot_extract_points(
            skeleton_id=args.skeleton_id, points=args.points
        )
    )
    return 0


def cmd_sot_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sot_parallel_expand(points=args.points))
    return 0


def cmd_sot_router(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sot_router(suitable=bool(args.suitable)))
    return 0


def cmd_sot_latency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sot_latency_gain(
            sequential=args.sequential, parallel=args.parallel
        )
    )
    return 0


def cmd_sot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sot_loop_plan(phase=args.phase))
    return 0


def cmd_bot_distill(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bot_distill_template(task=args.task))
    return 0


def cmd_bot_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bot_retrieve_template(query=args.query))
    return 0


def cmd_bot_instantiate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bot_instantiate(template_id=args.template_id))
    return 0


def cmd_bot_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bot_buffer_update(templates=args.templates))
    return 0


def cmd_bot_cost(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.bot_cost_ratio(multi_query=args.multi_query, bot=args.bot)
    )
    return 0


def cmd_bot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bot_loop_plan(phase=args.phase))
    return 0


def cmd_sd_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sd_select_modules(task=args.task, modules=args.modules)
    )
    return 0


def cmd_sd_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sd_adapt(select_id=args.select_id))
    return 0


def cmd_sd_implement(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sd_implement(adapt_id=args.adapt_id, keys=args.keys))
    return 0


def cmd_sd_apply(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sd_apply_instance(structure_id=args.structure_id))
    return 0


def cmd_sd_ratio(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sd_compute_ratio(
            sc_calls=args.sc_calls, self_discover=args.self_discover
        )
    )
    return 0


def cmd_sd_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sd_loop_plan(phase=args.phase))
    return 0


def cmd_mp_break(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mp_break_task(query=args.query, pieces=args.pieces))
    return 0


def cmd_mp_assign(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mp_assign_expert(
            piece_idx=args.piece_idx, expert=args.expert
        )
    )
    return 0


def cmd_mp_oversee(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mp_oversee(messages=args.messages))
    return 0


def cmd_mp_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mp_verify(claim=args.claim))
    return 0


def cmd_mp_agnostic(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mp_task_agnostic(scaffold=bool(args.scaffold)))
    return 0


def cmd_mp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mp_loop_plan(phase=args.phase))
    return 0


def cmd_qs_bounds(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qs_thought_bounds(start=args.start, end=args.end))
    return 0


def cmd_qs_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qs_parallel_sample(
            positions=args.positions, thoughts=args.thoughts
        )
    )
    return 0


def cmd_qs_mix(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qs_mix_head(weight=args.weight))
    return 0


def cmd_qs_aid(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qs_hard_token_aid(
            hard_tokens=args.hard_tokens, helped=args.helped
        )
    )
    return 0


def cmd_qs_zeroshot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qs_zero_shot_flag(improved=bool(args.improved)))
    return 0


def cmd_qs_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qs_loop_plan(phase=args.phase))
    return 0


def cmd_dep_decompose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dep_decompose(task=args.task, subs=args.subs))
    return 0


def cmd_dep_delegate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dep_delegate(handler=args.handler, sub_idx=args.sub_idx)
    )
    return 0


def cmd_dep_recurse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dep_recurse(depth=args.depth))
    return 0


def cmd_dep_swap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dep_swap_symbolic(module=args.module))
    return 0


def cmd_dep_library(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dep_library_size(handlers=args.handlers))
    return 0


def cmd_dep_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dep_loop_plan(phase=args.phase))
    return 0


def cmd_star_generate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.star_generate(question=args.question))
    return 0


def cmd_star_filter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.star_filter_correct(
            gen_id=args.gen_id, correct=bool(args.correct)
        )
    )
    return 0


def cmd_star_rationalize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.star_rationalize(question=args.question, answer=args.answer)
    )
    return 0


def cmd_star_finetune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.star_finetune_proxy(examples=args.examples))
    return 0


def cmd_star_round(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.star_bootstrap_round(round_n=args.round_n))
    return 0


def cmd_star_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.star_loop_plan(phase=args.phase))
    return 0


def cmd_cr_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cr_propose(step=args.step))
    return 0


def cmd_cr_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cr_verify(
            proposal_id=args.proposal_id, valid=bool(args.valid)
        )
    )
    return 0


def cmd_cr_accumulate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cr_accumulate(accepted=args.accepted))
    return 0


def cmd_cr_report(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cr_report(steps=args.steps))
    return 0


def cmd_cr_roles(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cr_roles(roles=args.roles))
    return 0


def cmd_cr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cr_loop_plan(phase=args.phase))
    return 0


def cmd_ps_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ps_devise_plan(problem=args.problem, subtasks=args.subtasks)
    )
    return 0


def cmd_ps_execute(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ps_execute(plan_id=args.plan_id, step=args.step))
    return 0


def cmd_ps_extract(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ps_plus_extract(variables=args.variables))
    return 0


def cmd_ps_guard(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ps_calc_guard(careful=bool(args.careful)))
    return 0


def cmd_ps_missing(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ps_missing_step_fix(fixed=bool(args.fixed)))
    return 0


def cmd_ps_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ps_loop_plan(phase=args.phase))
    return 0


def cmd_php_base(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.php_base_answer(question=args.question))
    return 0


def cmd_php_hint(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.php_emit_hint(answer_id=args.answer_id, hint=args.hint)
    )
    return 0


def cmd_php_reask(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.php_reask(hints=args.hints))
    return 0


def cmd_php_stop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.php_stable_stop(same_twice=bool(args.same_twice)))
    return 0


def cmd_php_sc(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.php_combine_sc(reduced_paths=bool(args.reduced)))
    return 0


def cmd_php_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.php_loop_plan(phase=args.phase))
    return 0


def cmd_ac_program(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ac_programmer(requirement=args.requirement))
    return 0


def cmd_ac_design(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ac_test_designer(
            requirement=args.requirement, cases=args.cases
        )
    )
    return 0


def cmd_ac_execute(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ac_test_executor(
            code_id=args.code_id, suite_id=args.suite_id
        )
    )
    return 0


def cmd_ac_refine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ac_refine(
            code_id=args.code_id, feedback_id=args.feedback_id
        )
    )
    return 0


def cmd_ac_pass(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ac_pass_gate(all_pass=bool(args.all_pass)))
    return 0


def cmd_ac_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ac_loop_plan(phase=args.phase))
    return 0


def cmd_pal_emit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pal_emit_program(problem=args.problem, lang=args.lang))
    return 0


def cmd_pal_offload(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pal_offload_solve(program_id=args.program_id))
    return 0


def cmd_pal_read(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pal_read_answer(result_id=args.result_id))
    return 0


def cmd_pal_decompose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pal_decompose_only(llm_solves=bool(args.llm_solves)))
    return 0


def cmd_pal_vs_cot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pal_vs_cot(program_beats_text=bool(args.beats)))
    return 0


def cmd_pal_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pal_loop_plan(phase=args.phase))
    return 0


def cmd_fcot_translate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.fcot_translate(query=args.query, symbolic=args.symbolic)
    )
    return 0


def cmd_fcot_solve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fcot_solve(chain_id=args.chain_id))
    return 0


def cmd_fcot_faith(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fcot_faithfulness(chain_explains=bool(args.explains)))
    return 0


def cmd_fcot_interleave(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fcot_interleave(nl_sl=bool(args.nl_sl)))
    return 0


def cmd_fcot_vs_cot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fcot_vs_cot(faithful_beats=bool(args.beats)))
    return 0


def cmd_fcot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fcot_loop_plan(phase=args.phase))
    return 0


def cmd_lats_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lats_expand(state=args.state, actions=args.actions))
    return 0


def cmd_lats_value(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lats_value(node_id=args.node_id, score=args.score))
    return 0


def cmd_lats_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lats_reflect(node_id=args.node_id, feedback=args.feedback)
    )
    return 0


def cmd_lats_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lats_select(node_id=args.node_id))
    return 0


def cmd_lats_env(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lats_env_feedback(useful=bool(args.useful)))
    return 0


def cmd_lats_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lats_loop_plan(phase=args.phase))
    return 0


def cmd_voy_curriculum(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.voy_curriculum(level=args.level, task=args.task))
    return 0


def cmd_voy_store(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.voy_skill_store(name=args.name, code_ref=args.code_ref))
    return 0


def cmd_voy_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.voy_skill_retrieve(query=args.query))
    return 0


def cmd_voy_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.voy_self_verify(
            skill_id=args.skill_id, passed=bool(args.passed)
        )
    )
    return 0


def cmd_voy_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.voy_compose(skills=args.skills))
    return 0


def cmd_voy_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.voy_loop_plan(phase=args.phase))
    return 0


def cmd_rewoo_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rewoo_plan(task=args.task, steps=args.steps))
    return 0


def cmd_rewoo_worker(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rewoo_worker(plan_id=args.plan_id, step=args.step))
    return 0


def cmd_rewoo_solver(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rewoo_solver(plan_id=args.plan_id, evidence=args.evidence)
    )
    return 0


def cmd_rewoo_decouple(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.rewoo_decouple(from_observation=bool(args.from_obs))
    )
    return 0


def cmd_rewoo_token(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rewoo_token_save(reduced=bool(args.reduced)))
    return 0


def cmd_rewoo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rewoo_loop_plan(phase=args.phase))
    return 0


def cmd_critic_draft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.critic_draft(question=args.question))
    return 0


def cmd_critic_check(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.critic_tool_check(draft_id=args.draft_id, tool=args.tool)
    )
    return 0


def cmd_critic_revise(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.critic_revise(
            draft_id=args.draft_id, critique_id=args.critique_id
        )
    )
    return 0


def cmd_critic_iterate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.critic_iterate(rounds=args.rounds))
    return 0


def cmd_critic_stop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.critic_stop(satisfied=bool(args.satisfied)))
    return 0


def cmd_critic_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.critic_loop_plan(phase=args.phase))
    return 0


def cmd_dv_program(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dv_natural_program(claim=args.claim, steps=args.steps))
    return 0


def cmd_dv_verify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dv_step_verify(program_id=args.program_id, step=args.step)
    )
    return 0


def cmd_dv_premises(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dv_premise_scope(premises=args.premises))
    return 0


def cmd_dv_unanimity(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dv_unanimity(all_pass=bool(args.all_pass)))
    return 0


def cmd_dv_ground(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dv_ground(grounded=bool(args.grounded)))
    return 0


def cmd_dv_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dv_loop_plan(phase=args.phase))
    return 0


def cmd_hgpt_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hgpt_plan(request=args.request, tasks=args.tasks))
    return 0


def cmd_hgpt_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hgpt_select(plan_id=args.plan_id, model=args.model))
    return 0


def cmd_hgpt_execute(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hgpt_execute(selection_id=args.selection_id))
    return 0


def cmd_hgpt_summarize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hgpt_summarize(results=args.results))
    return 0


def cmd_hgpt_modality(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hgpt_modality(modalities=args.modalities))
    return 0


def cmd_hgpt_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hgpt_loop_plan(phase=args.phase))
    return 0


def cmd_mad_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mad_propose(agent=args.agent, answer=args.answer))
    return 0


def cmd_mad_debate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mad_debate(round_n=args.round_n, agents=args.agents))
    return 0


def cmd_mad_critique(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mad_critique(
            proposal_id=args.proposal_id, critique=args.critique
        )
    )
    return 0


def cmd_mad_converge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mad_converge(common=bool(args.common)))
    return 0


def cmd_mad_factuality(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mad_factuality(improved=bool(args.improved)))
    return 0


def cmd_mad_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mad_loop_plan(phase=args.phase))
    return 0


def cmd_autocot_cluster(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.autocot_cluster(
            questions=args.questions, clusters=args.clusters
        )
    )
    return 0


def cmd_autocot_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.autocot_sample(cluster_id=args.cluster_id))
    return 0


def cmd_autocot_generate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.autocot_generate(demo_id=args.demo_id))
    return 0


def cmd_autocot_heuristic(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.autocot_heuristic(max_steps=args.max_steps))
    return 0


def cmd_autocot_diversity(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.autocot_diversity(diverse=bool(args.diverse)))
    return 0


def cmd_autocot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.autocot_loop_plan(phase=args.phase))
    return 0


def cmd_camel_roles(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.camel_roles(
            user_role=args.user_role, assistant_role=args.assistant_role
        )
    )
    return 0


def cmd_camel_inception(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.camel_inception(role_id=args.role_id, task=args.task))
    return 0


def cmd_camel_turn(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.camel_turn(
            inception_id=args.inception_id, speaker=args.speaker
        )
    )
    return 0


def cmd_camel_complete(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.camel_complete(done=bool(args.done)))
    return 0


def cmd_camel_society(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.camel_society(agents=args.agents))
    return 0


def cmd_camel_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.camel_loop_plan(phase=args.phase))
    return 0


def cmd_cham_inventory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cham_inventory(tools=args.tools))
    return 0


def cmd_cham_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cham_plan(task=args.task, modules=args.modules))
    return 0


def cmd_cham_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cham_compose(plan_id=args.plan_id, module=args.module))
    return 0


def cmd_cham_execute(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cham_execute(plan_id=args.plan_id))
    return 0


def cmd_cham_constraint(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cham_constraint(inferred=bool(args.inferred)))
    return 0


def cmd_cham_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cham_loop_plan(phase=args.phase))
    return 0


def cmd_rot_trigger(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rot_trigger(token=args.token))
    return 0


def cmd_rot_divide(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rot_divide(problem=args.problem, parts=args.parts))
    return 0


def cmd_rot_conquer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rot_conquer(divide_id=args.divide_id, part=args.part))
    return 0


def cmd_rot_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rot_merge(parts=args.parts))
    return 0


def cmd_rot_limit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rot_context_limit(within_limit=bool(args.within)))
    return 0


def cmd_rot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rot_loop_plan(phase=args.phase))
    return 0


def cmd_ap_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ap_sample(question=args.question, k=args.k))
    return 0


def cmd_ap_uncertainty(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ap_uncertainty(sample_id=args.sample_id, score=args.score)
    )
    return 0


def cmd_ap_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ap_select(top_n=args.top_n))
    return 0


def cmd_ap_annotate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ap_annotate(question_id=args.question_id, cot=args.cot))
    return 0


def cmd_ap_pool(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ap_pool(size=args.size))
    return 0


def cmd_ap_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ap_loop_plan(phase=args.phase))
    return 0


def cmd_ana_recall(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ana_recall(problem=args.problem))
    return 0


def cmd_ana_knowledge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ana_knowledge(problem=args.problem, facts=args.facts))
    return 0


def cmd_ana_solve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ana_solve(exemplar_id=args.exemplar_id))
    return 0


def cmd_ana_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ana_adapt(tailored=bool(args.tailored)))
    return 0


def cmd_ana_no_label(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ana_no_label(needs_labels=bool(args.needs_labels)))
    return 0


def cmd_ana_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ana_loop_plan(phase=args.phase))
    return 0


def cmd_cbp_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cbp_score(steps=args.steps))
    return 0


def cmd_cbp_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cbp_select(
            min_steps=args.min_steps, exemplars=args.exemplars
        )
    )
    return 0


def cmd_cbp_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cbp_sample_chains(n=args.n))
    return 0


def cmd_cbp_vote(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cbp_vote_complex(prefer_complex=bool(args.prefer_complex))
    )
    return 0


def cmd_cbp_robust(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cbp_robust(under_shift=bool(args.under_shift)))
    return 0


def cmd_cbp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cbp_loop_plan(phase=args.phase))
    return 0


def cmd_sb_abstract(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sb_abstract(instance=args.instance))
    return 0


def cmd_sb_principle(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sb_principle(
            concept_id=args.concept_id, principle=args.principle
        )
    )
    return 0


def cmd_sb_reason(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sb_reason(principle_id=args.principle_id))
    return 0


def cmd_sb_path(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sb_path(correct_path=bool(args.correct)))
    return 0


def cmd_sb_trap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sb_detail_trap(escaped=bool(args.escaped)))
    return 0


def cmd_sb_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sb_loop_plan(phase=args.phase))
    return 0


def cmd_mmcot_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mmcot_fuse(text=args.text, vision_ref=args.vision_ref)
    )
    return 0


def cmd_mmcot_rationale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mmcot_rationale(fuse_id=args.fuse_id))
    return 0


def cmd_mmcot_infer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mmcot_infer(rationale_id=args.rationale_id))
    return 0


def cmd_mmcot_hallucination(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mmcot_hallucination(mitigated=bool(args.mitigated)))
    return 0


def cmd_mmcot_separate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mmcot_separate(two_stage=bool(args.two_stage)))
    return 0


def cmd_mmcot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mmcot_loop_plan(phase=args.phase))
    return 0


def cmd_mai_abduce(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mai_abduce(claim=args.claim, because=args.because))
    return 0


def cmd_mai_recurse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mai_recurse(node_id=args.node_id, depth=args.depth))
    return 0


def cmd_mai_sat(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mai_sat(relations=args.relations))
    return 0


def cmd_mai_consistent(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mai_consistent(consistent=bool(args.consistent)))
    return 0


def cmd_mai_unreliable(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mai_unreliable(tolerate=bool(args.tolerate)))
    return 0


def cmd_mai_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mai_loop_plan(phase=args.phase))
    return 0


def cmd_sr_generate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sr_generate(draft=args.draft))
    return 0


def cmd_sr_feedback(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sr_feedback(gen_id=args.gen_id))
    return 0


def cmd_sr_refine(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.sr_refine(gen_id=args.gen_id, feedback_id=args.feedback_id)
    )
    return 0


def cmd_sr_iterate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sr_iterate(rounds=args.rounds))
    return 0


def cmd_sr_no_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sr_no_train(no_rl=bool(args.no_rl)))
    return 0


def cmd_sr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sr_loop_plan(phase=args.phase))
    return 0


def cmd_mcp_recognize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mcp_recognize(knowledge=args.knowledge))
    return 0


def cmd_mcp_interpret(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mcp_interpret(recognize_id=args.recognize_id))
    return 0


def cmd_mcp_reevaluate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mcp_reevaluate(interpret_id=args.interpret_id))
    return 0


def cmd_mcp_confidence(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mcp_confidence(score=args.score))
    return 0


def cmd_mcp_justify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mcp_justify(justified=bool(args.justified)))
    return 0


def cmd_mcp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mcp_loop_plan(phase=args.phase))
    return 0


def cmd_thot_segment(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.thot_segment(context=args.context, pieces=args.pieces)
    )
    return 0


def cmd_thot_analyze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.thot_analyze(segment_id=args.segment_id))
    return 0


def cmd_thot_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.thot_select(analyze_id=args.analyze_id))
    return 0


def cmd_thot_synthesize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.thot_synthesize(select_id=args.select_id))
    return 0


def cmd_thot_plug(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.thot_plug(plug_and_play=bool(args.plug_and_play)))
    return 0


def cmd_thot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.thot_loop_plan(phase=args.phase))
    return 0


def cmd_tprop_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tprop_propose(problem=args.problem))
    return 0


def cmd_tprop_solve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tprop_solve(propose_id=args.propose_id))
    return 0


def cmd_tprop_reuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tprop_reuse(analog_id=args.analog_id))
    return 0


def cmd_tprop_amend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tprop_amend(reuse_id=args.reuse_id))
    return 0


def cmd_tprop_compat(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tprop_compat(plug_and_play=bool(args.plug_and_play)))
    return 0


def cmd_tprop_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tprop_loop_plan(phase=args.phase))
    return 0


def cmd_s2a_regenerate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.s2a_regenerate(context=args.context))
    return 0


def cmd_s2a_attend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.s2a_attend(regen_id=args.regen_id))
    return 0


def cmd_s2a_respond(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.s2a_respond(attend_id=args.attend_id))
    return 0


def cmd_s2a_factuality(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.s2a_factuality(score=args.score))
    return 0


def cmd_s2a_sycophancy(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.s2a_sycophancy(reduced=bool(args.reduced)))
    return 0


def cmd_s2a_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.s2a_loop_plan(phase=args.phase))
    return 0


def cmd_ccot_valid(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ccot_valid(demo=args.demo))
    return 0


def cmd_ccot_invalid(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ccot_invalid(demo=args.demo))
    return 0


def cmd_ccot_contrast(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ccot_contrast(
            valid_id=args.valid_id, invalid_id=args.invalid_id
        )
    )
    return 0


def cmd_ccot_reason(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ccot_reason(contrast_id=args.contrast_id))
    return 0


def cmd_ccot_auto(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ccot_auto(construct=bool(args.construct)))
    return 0


def cmd_ccot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ccot_loop_plan(phase=args.phase))
    return 0


def cmd_tabcot_header(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tabcot_header(columns=args.columns))
    return 0


def cmd_tabcot_row(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tabcot_row(header_id=args.header_id, step=args.step))
    return 0


def cmd_tabcot_infer2d(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tabcot_infer2d(rows=args.rows))
    return 0


def cmd_tabcot_extract(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tabcot_extract(row_id=args.row_id))
    return 0


def cmd_tabcot_zeroshot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tabcot_zeroshot(zero_shot=bool(args.zero_shot)))
    return 0


def cmd_tabcot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tabcot_loop_plan(phase=args.phase))
    return 0


def cmd_xot_mcts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.xot_mcts(problem=args.problem))
    return 0


def cmd_xot_revise(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.xot_revise(mcts_id=args.mcts_id))
    return 0


def cmd_xot_map(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.xot_map(revise_id=args.revise_id))
    return 0


def cmd_xot_penrose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.xot_penrose(defy=bool(args.defy)))
    return 0


def cmd_xot_flexible(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.xot_flexible(multi_solution=bool(args.multi_solution))
    )
    return 0


def cmd_xot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.xot_loop_plan(phase=args.phase))
    return 0


def cmd_cove_draft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cove_draft(claim=args.claim))
    return 0


def cmd_cove_plan(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cove_plan(draft_id=args.draft_id))
    return 0


def cmd_cove_answer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cove_answer(plan_id=args.plan_id))
    return 0


def cmd_cove_final(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cove_final(verify_id=args.verify_id))
    return 0


def cmd_cove_hallucination(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cove_hallucination(reduced=bool(args.reduced)))
    return 0


def cmd_cove_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cove_loop_plan(phase=args.phase))
    return 0


def cmd_ved_uncertain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ved_uncertain(consistency=args.consistency))
    return 0


def cmd_ved_search(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ved_search(query=args.query))
    return 0


def cmd_ved_edit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ved_edit(fact_id=args.fact_id, rationale=args.rationale)
    )
    return 0


def cmd_ved_predict(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ved_predict(edit_id=args.edit_id))
    return 0


def cmd_ved_knowledge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ved_knowledge(enhanced=bool(args.enhanced)))
    return 0


def cmd_ved_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ved_loop_plan(phase=args.phase))
    return 0


def cmd_sve_forward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sve_forward(problem=args.problem))
    return 0


def cmd_sve_mask(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sve_mask(candidate_id=args.candidate_id))
    return 0


def cmd_sve_repredict(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sve_repredict(mask_id=args.mask_id))
    return 0


def cmd_sve_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sve_score(score=args.score))
    return 0


def cmd_sve_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sve_select(pick_best=bool(args.pick_best)))
    return 0


def cmd_sve_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sve_loop_plan(phase=args.phase))
    return 0


def cmd_cod_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cod_sparse(source=args.source))
    return 0


def cmd_cod_entities(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cod_entities(sparse_id=args.sparse_id, count=args.count)
    )
    return 0


def cmd_cod_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cod_fuse(entity_id=args.entity_id))
    return 0


def cmd_cod_length(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cod_length(fixed=bool(args.fixed)))
    return 0


def cmd_cod_tradeoff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cod_tradeoff(prefer_dense=bool(args.prefer_dense)))
    return 0


def cmd_cod_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cod_loop_plan(phase=args.phase))
    return 0


def cmd_hsp_hint(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hsp_hint(problem=args.problem))
    return 0


def cmd_hsp_solve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hsp_solve(hint_id=args.hint_id))
    return 0


def cmd_hsp_answer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hsp_answer(solve_id=args.solve_id))
    return 0


def cmd_hsp_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hsp_compose(base=args.base))
    return 0


def cmd_hsp_quality(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hsp_quality(high_quality=bool(args.high_quality)))
    return 0


def cmd_hsp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hsp_loop_plan(phase=args.phase))
    return 0


def cmd_emo_stimulus(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.emo_stimulus(text=args.text))
    return 0


def cmd_emo_append(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.emo_append(prompt=args.prompt, stimulus_id=args.stimulus_id)
    )
    return 0


def cmd_emo_run(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.emo_run(prompt_id=args.prompt_id))
    return 0


def cmd_emo_truth(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.emo_truth(improved=bool(args.improved)))
    return 0


def cmd_emo_psych(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.emo_psych(psychology=bool(args.psychology)))
    return 0


def cmd_emo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.emo_loop_plan(phase=args.phase))
    return 0


def cmd_ape_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ape_propose(demos=args.demos))
    return 0


def cmd_ape_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ape_score(pool_id=args.pool_id))
    return 0


def cmd_ape_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ape_select(score_id=args.score_id))
    return 0


def cmd_ape_steer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ape_steer(instr_id=args.instr_id))
    return 0


def cmd_ape_human(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ape_human(match_human=bool(args.match_human)))
    return 0


def cmd_ape_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ape_loop_plan(phase=args.phase))
    return 0


def cmd_pbr_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pbr_init(task=args.task))
    return 0


def cmd_pbr_mutate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pbr_mutate(pop_id=args.pop_id))
    return 0


def cmd_pbr_fitness(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pbr_fitness(mut_id=args.mut_id, score=args.score))
    return 0


def cmd_pbr_diversity(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pbr_diversity(maintain=bool(args.maintain)))
    return 0


def cmd_pbr_selfref(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pbr_selfref(self_improve=bool(args.self_improve)))
    return 0


def cmd_pbr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pbr_loop_plan(phase=args.phase))
    return 0


def cmd_opro_meta(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opro_meta(task=args.task))
    return 0


def cmd_opro_propose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opro_propose(meta_id=args.meta_id))
    return 0


def cmd_opro_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opro_score(cand_id=args.cand_id, score=args.score))
    return 0


def cmd_opro_append(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opro_append(score_id=args.score_id))
    return 0


def cmd_opro_best(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opro_best(beat_human=bool(args.beat_human)))
    return 0


def cmd_opro_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opro_loop_plan(phase=args.phase))
    return 0


def cmd_evp_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.evp_init(task=args.task))
    return 0


def cmd_evp_cross(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.evp_cross(pop_id=args.pop_id))
    return 0


def cmd_evp_mutate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.evp_mutate(cross_id=args.cross_id))
    return 0


def cmd_evp_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.evp_select(mut_id=args.mut_id, score=args.score))
    return 0


def cmd_evp_ea(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.evp_ea(connect_ea=bool(args.connect_ea)))
    return 0


def cmd_evp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.evp_loop_plan(phase=args.phase))
    return 0


def cmd_ptg_gradient(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptg_gradient(prompt=args.prompt))
    return 0


def cmd_ptg_edit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptg_edit(grad_id=args.grad_id))
    return 0


def cmd_ptg_beam(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptg_beam(edit_id=args.edit_id))
    return 0


def cmd_ptg_bandit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptg_bandit(beam_id=args.beam_id, score=args.score))
    return 0


def cmd_ptg_jailbreak(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptg_jailbreak(detect=bool(args.detect)))
    return 0


def cmd_ptg_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptg_loop_plan(phase=args.phase))
    return 0


def cmd_pag_state(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pag_state(prompt=args.prompt))
    return 0


def cmd_pag_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pag_reflect(state_id=args.state_id))
    return 0


def cmd_pag_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pag_expand(reflect_id=args.reflect_id))
    return 0


def cmd_pag_backprop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pag_backprop(expand_id=args.expand_id, reward=args.reward)
    )
    return 0


def cmd_pag_expert(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pag_expert(expert_level=bool(args.expert_level)))
    return 0


def cmd_pag_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pag_loop_plan(phase=args.phase))
    return 0


def cmd_mapo_posgrad(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mapo_posgrad(prompt=args.prompt))
    return 0


def cmd_mapo_momentum(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mapo_momentum(pos_id=args.pos_id))
    return 0


def cmd_mapo_beam(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mapo_beam(mom_id=args.mom_id))
    return 0


def cmd_mapo_ucb(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mapo_ucb(beam_id=args.beam_id, score=args.score))
    return 0


def cmd_mapo_faster(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mapo_faster(beat_protegi=bool(args.beat_protegi)))
    return 0


def cmd_mapo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mapo_loop_plan(phase=args.phase))
    return 0


def cmd_grips_seed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.grips_seed(instruction=args.instruction))
    return 0


def cmd_grips_edit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.grips_edit(seed_id=args.seed_id, op=args.op))
    return 0


def cmd_grips_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.grips_score(edit_id=args.edit_id, score=args.score))
    return 0


def cmd_grips_accept(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.grips_accept(score_id=args.score_id))
    return 0


def cmd_grips_api(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.grips_api(api_tunable=bool(args.api_tunable)))
    return 0


def cmd_grips_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.grips_loop_plan(phase=args.phase))
    return 0


def cmd_tmpa_state(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tmpa_state(prompt=args.prompt, query=args.query))
    return 0


def cmd_tmpa_act(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.tmpa_act(state_id=args.state_id, component=args.component)
    )
    return 0


def cmd_tmpa_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tmpa_reward(act_id=args.act_id, score=args.score))
    return 0


def cmd_tmpa_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tmpa_adapt(reward_id=args.reward_id))
    return 0


def cmd_tmpa_efficiency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.tmpa_efficiency(
            sample_efficient=bool(args.sample_efficient)
        )
    )
    return 0


def cmd_tmpa_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tmpa_loop_plan(phase=args.phase))
    return 0


def cmd_rlp_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlp_init(task=args.task))
    return 0


def cmd_rlp_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlp_sample(policy_id=args.policy_id))
    return 0


def cmd_rlp_reward(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlp_reward(sample_id=args.sample_id, score=args.score))
    return 0


def cmd_rlp_update(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlp_update(reward_id=args.reward_id))
    return 0


def cmd_rlp_discrete(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlp_discrete(discrete=bool(args.discrete)))
    return 0


def cmd_rlp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlp_loop_plan(phase=args.phase))
    return 0


def cmd_aup_template(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aup_template(template=args.template))
    return 0


def cmd_aup_trigger(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aup_trigger(tmpl_id=args.tmpl_id))
    return 0


def cmd_aup_search(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aup_search(trig_id=args.trig_id))
    return 0


def cmd_aup_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aup_score(search_id=args.search_id, score=args.score))
    return 0


def cmd_aup_probe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aup_probe(parameter_free=bool(args.parameter_free)))
    return 0


def cmd_aup_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aup_loop_plan(phase=args.phase))
    return 0


def cmd_pfx_task(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pfx_task(task=args.task))
    return 0


def cmd_pfx_prefix(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pfx_prefix(task_id=args.task_id))
    return 0


def cmd_pfx_optimize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pfx_optimize(prefix_id=args.prefix_id))
    return 0


def cmd_pfx_generate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pfx_generate(opt_id=args.opt_id, score=args.score))
    return 0


def cmd_pfx_freeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pfx_freeze(freeze_lm=bool(args.freeze_lm)))
    return 0


def cmd_pfx_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pfx_loop_plan(phase=args.phase))
    return 0


def cmd_ptv_deep(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptv_deep(task=args.task))
    return 0


def cmd_ptv_inject(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptv_inject(deep_id=args.deep_id))
    return 0


def cmd_ptv_tune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptv_tune(inj_id=args.inj_id))
    return 0


def cmd_ptv_seqtag(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptv_seqtag(tune_id=args.tune_id, score=args.score))
    return 0


def cmd_ptv_universal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptv_universal(match_finetune=bool(args.match_finetune)))
    return 0


def cmd_ptv_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptv_loop_plan(phase=args.phase))
    return 0


def cmd_ptl_soft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptl_soft(task=args.task))
    return 0


def cmd_ptl_prepend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptl_prepend(soft_id=args.soft_id))
    return 0


def cmd_ptl_optimize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptl_optimize(prep_id=args.prep_id))
    return 0


def cmd_ptl_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptl_scale(opt_id=args.opt_id, score=args.score))
    return 0


def cmd_ptl_input_only(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.ptl_input_only(
            input_layer_only=bool(args.input_layer_only)
        )
    )
    return 0


def cmd_ptl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ptl_loop_plan(phase=args.phase))
    return 0


def cmd_msp_soft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msp_soft(query=args.query))
    return 0


def cmd_msp_mix(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msp_mix(soft_id=args.soft_id))
    return 0


def cmd_msp_ensemble(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msp_ensemble(mix_id=args.mix_id))
    return 0


def cmd_msp_probe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msp_probe(ens_id=args.ens_id, score=args.score))
    return 0


def cmd_msp_underest(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.msp_underest(
            prior_underestimate=bool(args.prior_underestimate)
        )
    )
    return 0


def cmd_msp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msp_loop_plan(phase=args.phase))
    return 0


def cmd_spot_source(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spot_source(source_task=args.source_task))
    return 0


def cmd_spot_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spot_init(src_id=args.src_id, target_task=args.target_task)
    )
    return 0


def cmd_spot_embed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spot_embed(src_id=args.src_id))
    return 0


def cmd_spot_retrieve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spot_retrieve(emb_id=args.emb_id, score=args.score))
    return 0


def cmd_spot_vs_tune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spot_vs_tune(beat_model_tuning=bool(args.beat_model_tuning))
    )
    return 0


def cmd_spot_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spot_loop_plan(phase=args.phase))
    return 0


def cmd_atm_source(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.atm_source(source_task=args.source_task))
    return 0


def cmd_atm_target(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.atm_target(target_task=args.target_task))
    return 0


def cmd_atm_attend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.atm_attend(src_id=args.src_id, tgt_id=args.tgt_id))
    return 0


def cmd_atm_mix(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.atm_mix(attn_id=args.attn_id, score=args.score))
    return 0


def cmd_atm_modular(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.atm_modular(modular=bool(args.modular)))
    return 0


def cmd_atm_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.atm_loop_plan(phase=args.phase))
    return 0


def cmd_mptp_shared(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mptp_shared(corpus=args.corpus))
    return 0


def cmd_mptp_factor(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mptp_factor(shared_id=args.shared_id, task=args.task))
    return 0


def cmd_mptp_transfer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mptp_transfer(factor_id=args.factor_id))
    return 0


def cmd_mptp_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mptp_score(xfer_id=args.xfer_id, score=args.score))
    return 0


def cmd_mptp_efficient(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mptp_efficient(param_efficient=bool(args.param_efficient))
    )
    return 0


def cmd_mptp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mptp_loop_plan(phase=args.phase))
    return 0


def cmd_lora_freeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lora_freeze(base_frozen=bool(args.base_frozen)))
    return 0


def cmd_lora_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lora_rank(task=args.task, rank=args.rank))
    return 0


def cmd_lora_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lora_train(rank_id=args.rank_id))
    return 0


def cmd_lora_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lora_merge(train_id=args.train_id, score=args.score))
    return 0


def cmd_lora_latency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lora_latency(zero_extra=bool(args.zero_extra)))
    return 0


def cmd_lora_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lora_loop_plan(phase=args.phase))
    return 0


def cmd_adf_extract(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adf_extract(task=args.task))
    return 0


def cmd_adf_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adf_compose(adapter_id=args.adapter_id))
    return 0


def cmd_adf_attend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adf_attend(compose_id=args.compose_id))
    return 0


def cmd_adf_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adf_score(fusion_id=args.fusion_id, score=args.score))
    return 0


def cmd_adf_nondestruct(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.adf_nondestruct(nondestructive=bool(args.nondestructive))
    )
    return 0


def cmd_adf_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adf_loop_plan(phase=args.phase))
    return 0


def cmd_cmp_insert(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cmp_insert(task=args.task))
    return 0


def cmd_cmp_kronecker(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cmp_kronecker(adapter_id=args.adapter_id, n=args.n))
    return 0


def cmd_cmp_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cmp_train(kron_id=args.kron_id))
    return 0


def cmd_cmp_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cmp_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_cmp_compact(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.cmp_compact(param_efficient=bool(args.param_efficient))
    )
    return 0


def cmd_cmp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cmp_loop_plan(phase=args.phase))
    return 0


def cmd_ia3_vector(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ia3_vector(task=args.task))
    return 0


def cmd_ia3_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ia3_scale(vector_id=args.vector_id))
    return 0


def cmd_ia3_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ia3_train(scale_id=args.scale_id))
    return 0


def cmd_ia3_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ia3_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_ia3_mixed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ia3_mixed(mixed_batch=bool(args.mixed_batch)))
    return 0


def cmd_ia3_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ia3_loop_plan(phase=args.phase))
    return 0


def cmd_bft_freeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bft_freeze(weights_frozen=bool(args.weights_frozen)))
    return 0


def cmd_bft_bias(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bft_bias(task=args.task))
    return 0


def cmd_bft_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bft_train(bias_id=args.bias_id))
    return 0


def cmd_bft_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bft_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_bft_tiny(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bft_tiny(fraction_pct=args.fraction_pct))
    return 0


def cmd_bft_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bft_loop_plan(phase=args.phase))
    return 0


def cmd_dora_decompose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dora_decompose(task=args.task))
    return 0


def cmd_dora_magnitude(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dora_magnitude(decomp_id=args.decomp_id))
    return 0


def cmd_dora_direction(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dora_direction(mag_id=args.mag_id, rank=args.rank))
    return 0


def cmd_dora_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dora_score(dir_id=args.dir_id, score=args.score))
    return 0


def cmd_dora_vs_lora(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dora_vs_lora(closes_gap=bool(args.closes_gap)))
    return 0


def cmd_dora_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dora_loop_plan(phase=args.phase))
    return 0


def cmd_qlo_quantize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qlo_quantize(bits=args.bits))
    return 0


def cmd_qlo_nf4(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qlo_nf4(quant_id=args.quant_id))
    return 0


def cmd_qlo_adapter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qlo_adapter(nf4_id=args.nf4_id, rank=args.rank))
    return 0


def cmd_qlo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qlo_score(adapter_id=args.adapter_id, score=args.score))
    return 0


def cmd_qlo_memory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qlo_memory(double_quant=bool(args.double_quant)))
    return 0


def cmd_qlo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qlo_loop_plan(phase=args.phase))
    return 0


def cmd_adl_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adl_init(task=args.task, budget=args.budget))
    return 0


def cmd_adl_svd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adl_svd(init_id=args.init_id))
    return 0


def cmd_adl_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adl_prune(svd_id=args.svd_id, keep=args.keep))
    return 0


def cmd_adl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adl_score(prune_id=args.prune_id, score=args.score))
    return 0


def cmd_adl_adaptive(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adl_adaptive(adaptive_rank=bool(args.adaptive_rank)))
    return 0


def cmd_adl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adl_loop_plan(phase=args.phase))
    return 0


def cmd_vra_share(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vra_share(task=args.task, rank=args.rank))
    return 0


def cmd_vra_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vra_scale(share_id=args.share_id))
    return 0


def cmd_vra_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vra_train(scale_id=args.scale_id))
    return 0


def cmd_vra_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vra_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_vra_tiny(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vra_tiny(vector_only=bool(args.vector_only)))
    return 0


def cmd_vra_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vra_loop_plan(phase=args.phase))
    return 0


def cmd_adp_insert(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adp_insert(task=args.task))
    return 0


def cmd_adp_drop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.adp_drop(
            adapter_id=args.adapter_id, lower_layers=args.lower_layers
        )
    )
    return 0


def cmd_adp_infer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adp_infer(drop_id=args.drop_id))
    return 0


def cmd_adp_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adp_score(infer_id=args.infer_id, score=args.score))
    return 0


def cmd_adp_efficient(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adp_efficient(multi_task=bool(args.multi_task)))
    return 0


def cmd_adp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.adp_loop_plan(phase=args.phase))
    return 0


def cmd_psa_svd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.psa_svd(task=args.task, rank=args.rank))
    return 0


def cmd_psa_principal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.psa_principal(svd_id=args.svd_id))
    return 0


def cmd_psa_residual(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.psa_residual(principal_id=args.principal_id))
    return 0


def cmd_psa_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.psa_score(residual_id=args.residual_id, score=args.score)
    )
    return 0


def cmd_psa_fast(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.psa_fast(faster_than_lora=bool(args.faster_than_lora))
    )
    return 0


def cmd_psa_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.psa_loop_plan(phase=args.phase))
    return 0


def cmd_dpr_diff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dpr_diff(task=args.task))
    return 0


def cmd_dpr_mask(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dpr_mask(diff_id=args.diff_id))
    return 0


def cmd_dpr_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dpr_prune(
            mask_id=args.mask_id, sparsity_pct=args.sparsity_pct
        )
    )
    return 0


def cmd_dpr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dpr_score(prune_id=args.prune_id, score=args.score))
    return 0


def cmd_dpr_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dpr_sparse(no_new_params=bool(args.no_new_params)))
    return 0


def cmd_dpr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dpr_loop_plan(phase=args.phase))
    return 0


def cmd_tlo_base(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tlo_base(task=args.task, rank=args.rank))
    return 0


def cmd_tlo_tie(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tlo_tie(base_id=args.base_id, layers=args.layers))
    return 0


def cmd_tlo_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tlo_train(tie_id=args.tie_id))
    return 0


def cmd_tlo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tlo_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_tlo_efficient(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tlo_efficient(weight_tied=bool(args.weight_tied)))
    return 0


def cmd_tlo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tlo_loop_plan(phase=args.phase))
    return 0


def cmd_lrp_split(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrp_split(task=args.task))
    return 0


def cmd_lrp_ratio(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lrp_ratio(
            split_id=args.split_id, lambda_ratio=args.lambda_ratio
        )
    )
    return 0


def cmd_lrp_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrp_train(ratio_id=args.ratio_id))
    return 0


def cmd_lrp_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrp_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lrp_speed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lrp_speed(faster_than_lora=bool(args.faster_than_lora))
    )
    return 0


def cmd_lrp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrp_loop_plan(phase=args.phase))
    return 0


def cmd_lfa_freeze_a(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfa_freeze_a(task=args.task, rank=args.rank))
    return 0


def cmd_lfa_train_b(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfa_train_b(a_id=args.a_id))
    return 0


def cmd_lfa_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfa_merge(train_id=args.train_id))
    return 0


def cmd_lfa_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfa_score(merge_id=args.merge_id, score=args.score))
    return 0


def cmd_lfa_memory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lfa_memory(activation_saved=bool(args.activation_saved))
    )
    return 0


def cmd_lfa_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfa_loop_plan(phase=args.phase))
    return 0


def cmd_dyl_range(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dyl_range(
            task=args.task, r_min=args.r_min, r_max=args.r_max
        )
    )
    return 0


def cmd_dyl_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dyl_sample(range_id=args.range_id))
    return 0


def cmd_dyl_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dyl_select(sample_id=args.sample_id, rank=args.rank))
    return 0


def cmd_dyl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dyl_score(select_id=args.select_id, score=args.score))
    return 0


def cmd_dyl_searchfree(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dyl_searchfree(search_free=bool(args.search_free)))
    return 0


def cmd_dyl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dyl_loop_plan(phase=args.phase))
    return 0


def cmd_lxs_svd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lxs_svd(task=args.task, rank=args.rank))
    return 0


def cmd_lxs_r(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lxs_r(svd_id=args.svd_id))
    return 0


def cmd_lxs_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lxs_train(r_id=args.r_id))
    return 0


def cmd_lxs_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lxs_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lxs_tiny(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lxs_tiny(r_squared_only=bool(args.r_squared_only)))
    return 0


def cmd_lxs_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lxs_loop_plan(phase=args.phase))
    return 0


def cmd_asy_role(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.asy_role(task=args.task))
    return 0


def cmd_asy_freeze_a(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.asy_freeze_a(role_id=args.role_id))
    return 0


def cmd_asy_train_b(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.asy_train_b(a_id=args.a_id))
    return 0


def cmd_asy_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.asy_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_asy_bound(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.asy_bound(tighter_bound=bool(args.tighter_bound)))
    return 0


def cmd_asy_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.asy_loop_plan(phase=args.phase))
    return 0


def cmd_lga_grad(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lga_grad(task=args.task, samples=args.samples))
    return 0


def cmd_lga_svd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lga_svd(grad_id=args.grad_id))
    return 0


def cmd_lga_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lga_scale(svd_id=args.svd_id))
    return 0


def cmd_lga_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lga_score(scale_id=args.scale_id, score=args.score))
    return 0


def cmd_lga_fast(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lga_fast(faster_convergence=bool(args.faster_convergence)))
    return 0


def cmd_lga_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lga_loop_plan(phase=args.phase))
    return 0


def cmd_mor_square(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mor_square(task=args.task, side=args.side))
    return 0


def cmd_mor_compress(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mor_compress(square_id=args.square_id))
    return 0


def cmd_mor_expand(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mor_expand(compress_id=args.compress_id))
    return 0


def cmd_mor_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mor_score(expand_id=args.expand_id, score=args.score))
    return 0


def cmd_mor_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mor_merge(mergeable=bool(args.mergeable)))
    return 0


def cmd_mor_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mor_loop_plan(phase=args.phase))
    return 0


def cmd_rsl_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsl_rank(task=args.task, rank=args.rank))
    return 0


def cmd_rsl_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsl_scale(rank_id=args.rank_id))
    return 0


def cmd_rsl_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsl_train(scale_id=args.scale_id))
    return 0


def cmd_rsl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsl_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_rsl_stable(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsl_stable(no_collapse=bool(args.no_collapse)))
    return 0


def cmd_rsl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsl_loop_plan(phase=args.phase))
    return 0


def cmd_lkr_factors(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lkr_factors(
            task=args.task, factor_a=args.factor_a, factor_b=args.factor_b
        )
    )
    return 0


def cmd_lkr_kron(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lkr_kron(factors_id=args.factors_id))
    return 0


def cmd_lkr_vectorize(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lkr_vectorize(kron_id=args.kron_id))
    return 0


def cmd_lkr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lkr_score(vector_id=args.vector_id, score=args.score))
    return 0


def cmd_lkr_preserve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lkr_preserve(rank_preserved=bool(args.rank_preserved)))
    return 0


def cmd_lkr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lkr_loop_plan(phase=args.phase))
    return 0


def cmd_lha_pair(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lha_pair(task=args.task, rank=args.rank))
    return 0


def cmd_lha_hadamard(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lha_hadamard(pair_id=args.pair_id))
    return 0


def cmd_lha_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lha_train(hadamard_id=args.hadamard_id))
    return 0


def cmd_lha_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lha_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lha_express(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lha_express(more_expressivity=bool(args.more_expressivity)))
    return 0


def cmd_lha_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lha_loop_plan(phase=args.phase))
    return 0


def cmd_fft_basis(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fft_basis(task=args.task, n_coeff=args.n_coeff))
    return 0


def cmd_fft_coeff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fft_coeff(basis_id=args.basis_id))
    return 0


def cmd_fft_idft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fft_idft(coeff_id=args.coeff_id))
    return 0


def cmd_fft_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fft_score(idft_id=args.idft_id, score=args.score))
    return 0


def cmd_fft_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fft_sparse(spectral_sparse=bool(args.spectral_sparse)))
    return 0


def cmd_fft_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fft_loop_plan(phase=args.phase))
    return 0


def cmd_had_insert(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.had_insert(task=args.task, bottleneck=args.bottleneck))
    return 0


def cmd_had_freeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.had_freeze(insert_id=args.insert_id))
    return 0


def cmd_had_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.had_train(freeze_id=args.freeze_id))
    return 0


def cmd_had_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.had_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_had_latency(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.had_latency(adds_latency=bool(args.adds_latency)))
    return 0


def cmd_had_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.had_loop_plan(phase=args.phase))
    return 0


def cmd_rft_repr(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rft_repr(task=args.task, layers=args.layers))
    return 0


def cmd_rft_edit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rft_edit(repr_id=args.repr_id))
    return 0


def cmd_rft_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rft_train(edit_id=args.edit_id))
    return 0


def cmd_rft_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rft_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_rft_weightless(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rft_weightless(no_weight_update=bool(args.no_weight_update)))
    return 0


def cmd_rft_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rft_loop_plan(phase=args.phase))
    return 0


def cmd_oft_ortho(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.oft_ortho(task=args.task, block=args.block))
    return 0


def cmd_oft_butterfly(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.oft_butterfly(ortho_id=args.ortho_id, factors=args.factors)
    )
    return 0


def cmd_oft_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.oft_train(butterfly_id=args.butterfly_id))
    return 0


def cmd_oft_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.oft_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_oft_energy(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.oft_energy(
            hypersphere_preserved=bool(args.hypersphere_preserved)
        )
    )
    return 0


def cmd_oft_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.oft_loop_plan(phase=args.phase))
    return 0


def cmd_mss_shard(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mss_shard(task=args.task, shards=args.shards))
    return 0


def cmd_mss_share(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mss_share(shard_id=args.shard_id))
    return 0


def cmd_mss_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mss_train(share_id=args.share_id))
    return 0


def cmd_mss_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mss_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_mss_pareto(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mss_pareto(better_tradeoff=bool(args.better_tradeoff)))
    return 0


def cmd_mss_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mss_loop_plan(phase=args.phase))
    return 0


def cmd_drl_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.drl_rank(task=args.task, rank=args.rank))
    return 0


def cmd_drl_mask(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.drl_mask(rank_id=args.rank_id, keep_prob=args.keep_prob))
    return 0


def cmd_drl_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.drl_train(mask_id=args.mask_id))
    return 0


def cmd_drl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.drl_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_drl_infer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.drl_infer(no_extra_cost=bool(args.no_extra_cost)))
    return 0


def cmd_drl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.drl_loop_plan(phase=args.phase))
    return 0


def cmd_gal_grad(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gal_grad(task=args.task))
    return 0


def cmd_gal_project(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gal_project(grad_id=args.grad_id, rank=args.rank))
    return 0


def cmd_gal_step(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gal_step(project_id=args.project_id))
    return 0


def cmd_gal_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gal_score(step_id=args.step_id, score=args.score))
    return 0


def cmd_gal_full(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.gal_full(updates_all_weights=bool(args.updates_all_weights))
    )
    return 0


def cmd_gal_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gal_loop_plan(phase=args.phase))
    return 0


def cmd_shr_mask(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.shr_mask(task=args.task, pct=args.pct))
    return 0


def cmd_shr_tune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.shr_tune(mask_id=args.mask_id))
    return 0


def cmd_shr_switch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.shr_switch(tune_id=args.tune_id))
    return 0


def cmd_shr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.shr_score(switch_id=args.switch_id, score=args.score))
    return 0


def cmd_shr_fusion(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.shr_fusion(less_concept_loss=bool(args.less_concept_loss)))
    return 0


def cmd_shr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.shr_loop_plan(phase=args.phase))
    return 0


def cmd_wft_wave(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wft_wave(task=args.task, n_coeff=args.n_coeff))
    return 0


def cmd_wft_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wft_sparse(wave_id=args.wave_id))
    return 0


def cmd_wft_idwt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wft_idwt(sparse_id=args.sparse_id))
    return 0


def cmd_wft_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wft_score(idwt_id=args.idwt_id, score=args.score))
    return 0


def cmd_wft_granular(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wft_granular(below_lora_min=bool(args.below_lora_min)))
    return 0


def cmd_wft_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.wft_loop_plan(phase=args.phase))
    return 0


def cmd_lpr_equiv(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lpr_equiv(task=args.task))
    return 0


def cmd_lpr_adjust(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lpr_adjust(equiv_id=args.equiv_id))
    return 0


def cmd_lpr_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lpr_train(adjust_id=args.adjust_id))
    return 0


def cmd_lpr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lpr_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lpr_bridge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lpr_bridge(closer_to_fft=bool(args.closer_to_fft)))
    return 0


def cmd_lpr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lpr_loop_plan(phase=args.phase))
    return 0


def cmd_krl_kron(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.krl_kron(task=args.task, factor=args.factor))
    return 0


def cmd_krl_lora(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.krl_lora(kron_id=args.kron_id, rank=args.rank))
    return 0


def cmd_krl_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.krl_train(lora_id=args.lora_id))
    return 0


def cmd_krl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.krl_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_krl_compress(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.krl_compress(more_compression=bool(args.more_compression)))
    return 0


def cmd_krl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.krl_loop_plan(phase=args.phase))
    return 0


def cmd_mil_svd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mil_svd(task=args.task, rank=args.rank))
    return 0


def cmd_mil_minor(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mil_minor(svd_id=args.svd_id))
    return 0


def cmd_mil_freeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mil_freeze(minor_id=args.minor_id))
    return 0


def cmd_mil_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mil_score(freeze_id=args.freeze_id, score=args.score))
    return 0


def cmd_mil_preserve(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mil_preserve(preserves_principal=bool(args.preserves_principal))
    )
    return 0


def cmd_mil_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mil_loop_plan(phase=args.phase))
    return 0


def cmd_cda_cov(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cda_cov(task=args.task))
    return 0


def cmd_cda_mode(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cda_mode(cov_id=args.cov_id, mode=args.mode))
    return 0


def cmd_cda_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cda_adapt(mode_id=args.mode_id))
    return 0


def cmd_cda_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cda_score(adapt_id=args.adapt_id, score=args.score))
    return 0


def cmd_cda_forget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cda_forget(less_forgetting=bool(args.less_forgetting)))
    return 0


def cmd_cda_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cda_loop_plan(phase=args.phase))
    return 0


def cmd_lfq_quant(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfq_quant(task=args.task, bits=args.bits))
    return 0


def cmd_lfq_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfq_init(quant_id=args.quant_id, rank=args.rank))
    return 0


def cmd_lfq_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfq_train(init_id=args.init_id))
    return 0


def cmd_lfq_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfq_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lfq_gap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfq_gap(closes_qlora_gap=bool(args.closes_qlora_gap)))
    return 0


def cmd_lfq_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfq_loop_plan(phase=args.phase))
    return 0


def cmd_lds_prelaunch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lds_prelaunch(task=args.task))
    return 0


def cmd_lds_tsd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lds_tsd(prelaunch_id=args.prelaunch_id, count=args.count))
    return 0


def cmd_lds_dash(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lds_dash(tsd_id=args.tsd_id))
    return 0


def cmd_lds_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lds_score(dash_id=args.dash_id, score=args.score))
    return 0


def cmd_lds_impact(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lds_impact(maximizes_tsd=bool(args.maximizes_tsd)))
    return 0


def cmd_lds_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lds_loop_plan(phase=args.phase))
    return 0


def cmd_dlo_adapters(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlo_adapters(task=args.task, rank=args.rank))
    return 0


def cmd_dlo_delta(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlo_delta(adapters_id=args.adapters_id))
    return 0


def cmd_dlo_propagate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlo_propagate(delta_id=args.delta_id))
    return 0


def cmd_dlo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dlo_score(propagate_id=args.propagate_id, score=args.score)
    )
    return 0


def cmd_dlo_highrank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dlo_highrank(high_rank_capacity=bool(args.high_rank_capacity))
    )
    return 0


def cmd_dlo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlo_loop_plan(phase=args.phase))
    return 0


def cmd_lon_grad(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lon_grad(task=args.task))
    return 0


def cmd_lon_align(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lon_align(grad_id=args.grad_id, rank=args.rank))
    return 0


def cmd_lon_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lon_train(align_id=args.align_id))
    return 0


def cmd_lon_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lon_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lon_immediate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lon_immediate(immediate_align=bool(args.immediate_align)))
    return 0


def cmd_lon_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lon_loop_plan(phase=args.phase))
    return 0


def cmd_olr_qr(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.olr_qr(task=args.task, rank=args.rank))
    return 0


def cmd_olr_ortho(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.olr_ortho(qr_id=args.qr_id))
    return 0


def cmd_olr_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.olr_train(ortho_id=args.ortho_id))
    return 0


def cmd_olr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.olr_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_olr_stable(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.olr_stable(stable_landscape=bool(args.stable_landscape)))
    return 0


def cmd_olr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.olr_loop_plan(phase=args.phase))
    return 0


def cmd_lsp_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsp_select(task=args.task, fraction=args.fraction))
    return 0


def cmd_lsp_freeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsp_freeze(select_id=args.select_id))
    return 0


def cmd_lsp_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsp_train(freeze_id=args.freeze_id))
    return 0


def cmd_lsp_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsp_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lsp_memory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsp_memory(lower_memory=bool(args.lower_memory)))
    return 0


def cmd_lsp_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsp_loop_plan(phase=args.phase))
    return 0


def cmd_qps_quant(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qps_quant(task=args.task, bits=args.bits))
    return 0


def cmd_qps_principal(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qps_principal(quant_id=args.quant_id, rank=args.rank))
    return 0


def cmd_qps_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qps_train(principal_id=args.principal_id))
    return 0


def cmd_qps_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qps_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_qps_error(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qps_error(smaller_than_qlora=bool(args.smaller_than_qlora))
    )
    return 0


def cmd_qps_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qps_loop_plan(phase=args.phase))
    return 0


def cmd_msl_split(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msl_split(task=args.task, rank=args.rank))
    return 0


def cmd_msl_mixer(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msl_mixer(split_id=args.split_id))
    return 0


def cmd_msl_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msl_train(mixer_id=args.mixer_id))
    return 0


def cmd_msl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msl_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_msl_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msl_fuse(flexible_fuse=bool(args.flexible_fuse)))
    return 0


def cmd_msl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.msl_loop_plan(phase=args.phase))
    return 0


def cmd_ldr_eval(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ldr_eval(task=args.task))
    return 0


def cmd_ldr_keep(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ldr_keep(eval_id=args.eval_id, keep_pct=args.keep_pct))
    return 0


def cmd_ldr_share(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ldr_share(keep_id=args.keep_id))
    return 0


def cmd_ldr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ldr_score(share_id=args.share_id, score=args.score))
    return 0


def cmd_ldr_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ldr_prune(half_params=bool(args.half_params)))
    return 0


def cmd_ldr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ldr_loop_plan(phase=args.phase))
    return 0


def cmd_vbl_bank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vbl_bank(task=args.task, size=args.size))
    return 0


def cmd_vbl_topk(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vbl_topk(bank_id=args.bank_id, k=args.k))
    return 0


def cmd_vbl_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vbl_compose(topk_id=args.topk_id))
    return 0


def cmd_vbl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vbl_score(compose_id=args.compose_id, score=args.score))
    return 0


def cmd_vbl_extreme(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.vbl_extreme(extreme_compression=bool(args.extreme_compression))
    )
    return 0


def cmd_vbl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.vbl_loop_plan(phase=args.phase))
    return 0


def cmd_opl_proj(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opl_proj(task=args.task))
    return 0


def cmd_opl_constrain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opl_constrain(proj_id=args.proj_id, rank=args.rank))
    return 0


def cmd_opl_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opl_train(constrain_id=args.constrain_id))
    return 0


def cmd_opl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opl_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_opl_forget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opl_forget(less_forgetting=bool(args.less_forgetting)))
    return 0


def cmd_opl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.opl_loop_plan(phase=args.phase))
    return 0


def cmd_gel_idim(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gel_idim(task=args.task, layer=args.layer))
    return 0


def cmd_gel_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gel_rank(idim_id=args.idim_id, rank=args.rank))
    return 0


def cmd_gel_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gel_train(rank_id=args.rank_id))
    return 0


def cmd_gel_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gel_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_gel_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gel_budget(within_budget=bool(args.within_budget)))
    return 0


def cmd_gel_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.gel_loop_plan(phase=args.phase))
    return 0


def cmd_geo_dyn(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.geo_dyn(task=args.task))
    return 0


def cmd_geo_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.geo_budget(dyn_id=args.dyn_id, layers=args.layers))
    return 0


def cmd_geo_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.geo_train(budget_id=args.budget_id))
    return 0


def cmd_geo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.geo_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_geo_ortho(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.geo_ortho(exact_ortho=bool(args.exact_ortho)))
    return 0


def cmd_geo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.geo_loop_plan(phase=args.phase))
    return 0


def cmd_rlo_bases(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlo_bases(task=args.task, count=args.count))
    return 0


def cmd_rlo_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlo_scale(bases_id=args.bases_id))
    return 0


def cmd_rlo_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlo_train(scale_id=args.scale_id))
    return 0


def cmd_rlo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlo_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_rlo_fullrank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlo_fullrank(full_rank_update=bool(args.full_rank_update)))
    return 0


def cmd_rlo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlo_loop_plan(phase=args.phase))
    return 0


def cmd_lsh_graph(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsh_graph(task=args.task))
    return 0


def cmd_lsh_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsh_prune(graph_id=args.graph_id, ratio_pct=args.ratio_pct))
    return 0


def cmd_lsh_recover(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsh_recover(prune_id=args.prune_id))
    return 0


def cmd_lsh_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsh_score(recover_id=args.recover_id, score=args.score))
    return 0


def cmd_lsh_footprint(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsh_footprint(reduced=bool(args.reduced)))
    return 0


def cmd_lsh_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lsh_loop_plan(phase=args.phase))
    return 0


def cmd_aop_sub(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aop_sub(task=args.task))
    return 0


def cmd_aop_alt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aop_alt(sub_id=args.sub_id, steps=args.steps))
    return 0


def cmd_aop_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aop_train(alt_id=args.alt_id))
    return 0


def cmd_aop_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aop_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_aop_svd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aop_svd(near_svd=bool(args.near_svd)))
    return 0


def cmd_aop_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.aop_loop_plan(phase=args.phase))
    return 0


def cmd_lin_tsd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lin_tsd(task=args.task, count=args.count))
    return 0


def cmd_lin_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lin_init(tsd_id=args.tsd_id))
    return 0


def cmd_lin_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lin_train(init_id=args.init_id))
    return 0


def cmd_lin_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lin_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lin_fast(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lin_fast(faster_convergence=bool(args.faster_convergence)))
    return 0


def cmd_lin_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lin_loop_plan(phase=args.phase))
    return 0


def cmd_lnu_act(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnu_act(task=args.task, samples=args.samples))
    return 0


def cmd_lnu_null(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnu_null(act_id=args.act_id))
    return 0


def cmd_lnu_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnu_train(null_id=args.null_id))
    return 0


def cmd_lnu_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnu_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lnu_forget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.lnu_forget(preserves_knowledge=bool(args.preserves_knowledge))
    )
    return 0


def cmd_lnu_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnu_loop_plan(phase=args.phase))
    return 0


def cmd_hyd_share(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyd_share(task=args.task))
    return 0


def cmd_hyd_heads(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyd_heads(share_id=args.share_id, heads=args.heads))
    return 0


def cmd_hyd_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyd_route(heads_id=args.heads_id))
    return 0


def cmd_hyd_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyd_score(route_id=args.route_id, score=args.score))
    return 0


def cmd_hyd_nodomain(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyd_nodomain(no_domain_labels=bool(args.no_domain_labels)))
    return 0


def cmd_hyd_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyd_loop_plan(phase=args.phase))
    return 0


def cmd_llg_msu(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llg_msu(task=args.task, adapters=args.adapters))
    return 0


def cmd_llg_cluster(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llg_cluster(msu_id=args.msu_id, k=args.k))
    return 0


def cmd_llg_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llg_merge(cluster_id=args.cluster_id))
    return 0


def cmd_llg_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llg_score(merge_id=args.merge_id, score=args.score))
    return 0


def cmd_llg_modular(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llg_modular(modular_merge=bool(args.modular_merge)))
    return 0


def cmd_llg_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llg_loop_plan(phase=args.phase))
    return 0


def cmd_lme_plugin(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lme_plugin(task=args.task, experts=args.experts))
    return 0


def cmd_lme_balance(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lme_balance(plugin_id=args.plugin_id))
    return 0


def cmd_lme_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lme_route(balance_id=args.balance_id))
    return 0


def cmd_lme_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lme_score(route_id=args.route_id, score=args.score))
    return 0


def cmd_lme_forget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lme_forget(preserves_world=bool(args.preserves_world)))
    return 0


def cmd_lme_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lme_loop_plan(phase=args.phase))
    return 0


def cmd_mel_experts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mel_experts(task=args.task, count=args.count))
    return 0


def cmd_mel_contrast(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mel_contrast(experts_id=args.experts_id))
    return 0


def cmd_mel_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mel_gate(contrast_id=args.contrast_id))
    return 0


def cmd_mel_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mel_score(gate_id=args.gate_id, score=args.score))
    return 0


def cmd_mel_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mel_sparse(sparse_activate=bool(args.sparse_activate)))
    return 0


def cmd_mel_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mel_loop_plan(phase=args.phase))
    return 0


def cmd_lhb_pool(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lhb_pool(task=args.task, modules=args.modules))
    return 0


def cmd_lhb_compose(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lhb_compose(pool_id=args.pool_id))
    return 0


def cmd_lhb_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lhb_adapt(compose_id=args.compose_id, shots=args.shots))
    return 0


def cmd_lhb_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lhb_score(adapt_id=args.adapt_id, score=args.score))
    return 0


def cmd_lhb_nograd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lhb_nograd(gradient_free=bool(args.gradient_free)))
    return 0


def cmd_lhb_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lhb_loop_plan(phase=args.phase))
    return 0


def cmd_mlr_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mlr_scale(task=args.task, shards=args.shards))
    return 0


def cmd_mlr_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mlr_init(scale_id=args.scale_id))
    return 0


def cmd_mlr_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mlr_train(init_id=args.init_id))
    return 0


def cmd_mlr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mlr_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_mlr_demo(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mlr_demo(more_democratic=bool(args.more_democratic)))
    return 0


def cmd_mlr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mlr_loop_plan(phase=args.phase))
    return 0


def cmd_mtl_task(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mtl_task(task=args.task, tasks=args.tasks))
    return 0


def cmd_mtl_spec(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mtl_spec(task_id=args.task_id))
    return 0


def cmd_mtl_share(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mtl_share(spec_id=args.spec_id))
    return 0


def cmd_mtl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mtl_score(share_id=args.share_id, score=args.score))
    return 0


def cmd_mtl_interfere(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mtl_interfere(less_interference=bool(args.less_interference))
    )
    return 0


def cmd_mtl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mtl_loop_plan(phase=args.phase))
    return 0


def cmd_mal_mix(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mal_mix(task=args.task, experts=args.experts))
    return 0


def cmd_mal_down(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mal_down(mix_id=args.mix_id))
    return 0


def cmd_mal_up(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mal_up(down_id=args.down_id))
    return 0


def cmd_mal_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mal_score(up_id=args.up_id, score=args.score))
    return 0


def cmd_mal_eff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mal_eff(fewer_params=bool(args.fewer_params)))
    return 0


def cmd_mal_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mal_loop_plan(phase=args.phase))
    return 0


def cmd_lmi_split(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lmi_split(task=args.task, rank=args.rank))
    return 0


def cmd_lmi_inner(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lmi_inner(split_id=args.split_id))
    return 0


def cmd_lmi_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lmi_train(inner_id=args.inner_id))
    return 0


def cmd_lmi_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lmi_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lmi_tiny(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lmi_tiny(extreme_compress=bool(args.extreme_compress)))
    return 0


def cmd_lmi_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lmi_loop_plan(phase=args.phase))
    return 0


def cmd_qdy_range(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.qdy_range(task=args.task, r_min=args.r_min, r_max=args.r_max)
    )
    return 0


def cmd_qdy_quant(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qdy_quant(range_id=args.range_id, bits=args.bits))
    return 0


def cmd_qdy_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qdy_train(quant_id=args.quant_id))
    return 0


def cmd_qdy_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qdy_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_qdy_pick(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qdy_pick(pick_rank_at_infer=bool(args.pick_rank_at_infer)))
    return 0


def cmd_qdy_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qdy_loop_plan(phase=args.phase))
    return 0


def cmd_lts_tsd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lts_tsd(task=args.task, count=args.count))
    return 0


def cmd_lts_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lts_init(tsd_id=args.tsd_id))
    return 0


def cmd_lts_dash(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lts_dash(init_id=args.init_id))
    return 0


def cmd_lts_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lts_score(dash_id=args.dash_id, score=args.score))
    return 0


def cmd_lts_combo(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lts_combo(uses_both=bool(args.uses_both)))
    return 0


def cmd_lts_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lts_loop_plan(phase=args.phase))
    return 0


def cmd_slr_pool(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.slr_pool(adapters=args.adapters))
    return 0


def cmd_slr_page(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.slr_page(pool_id=args.pool_id, unified=bool(args.unified)))
    return 0


def cmd_slr_batch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.slr_batch(page_id=args.page_id, concurrent=args.concurrent)
    )
    return 0


def cmd_slr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.slr_score(batch_id=args.batch_id, score=args.score))
    return 0


def cmd_slr_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.slr_scale(thousands=bool(args.thousands)))
    return 0


def cmd_slr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.slr_loop_plan(phase=args.phase))
    return 0


def cmd_cts_collect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cts_collect(adapters=args.adapters))
    return 0


def cmd_cts_basis(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cts_basis(collect_id=args.collect_id))
    return 0


def cmd_cts_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cts_scale(basis_id=args.basis_id, adapters=args.adapters))
    return 0


def cmd_cts_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cts_score(scale_id=args.scale_id, score=args.score))
    return 0


def cmd_cts_cluster(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cts_cluster(cluster_for_large=bool(args.cluster_for_large)))
    return 0


def cmd_cts_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cts_loop_plan(phase=args.phase))
    return 0


def cmd_flo_clients(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flo_clients(clients=args.clients))
    return 0


def cmd_flo_stack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.flo_stack(
            clients_id=args.clients_id,
            hetero_ranks=bool(args.hetero_ranks),
        )
    )
    return 0


def cmd_flo_agg(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flo_agg(stack_id=args.stack_id))
    return 0


def cmd_flo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flo_score(agg_id=args.agg_id, score=args.score))
    return 0


def cmd_flo_hetero(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flo_hetero(supports_hetero=bool(args.supports_hetero)))
    return 0


def cmd_flo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.flo_loop_plan(phase=args.phase))
    return 0


def cmd_pun_backbone(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pun_backbone(model=args.model))
    return 0


def cmd_pun_sgmv(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.pun_sgmv(backbone_id=args.backbone_id, adapters=args.adapters)
    )
    return 0


def cmd_pun_sched(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pun_sched(sgmv_id=args.sgmv_id))
    return 0


def cmd_pun_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pun_score(sched_id=args.sched_id, score=args.score))
    return 0


def cmd_pun_multi(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pun_multi(multi_tenant=bool(args.multi_tenant)))
    return 0


def cmd_pun_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.pun_loop_plan(phase=args.phase))
    return 0


def cmd_mla_pipe(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mla_pipe(tasks=args.tasks, gpus=args.gpus))
    return 0


def cmd_mla_batch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mla_batch(pipe_id=args.pipe_id))
    return 0


def cmd_mla_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mla_train(batch_id=args.batch_id))
    return 0


def cmd_mla_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mla_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_mla_eff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.mla_eff(
            lower_completion_time=bool(args.lower_completion_time)
        )
    )
    return 0


def cmd_mla_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mla_loop_plan(phase=args.phase))
    return 0


def cmd_swl_alloc(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.swl_alloc(task=args.task, rank=args.rank))
    return 0


def cmd_swl_switch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.swl_switch(alloc_id=args.alloc_id, dims=args.dims))
    return 0


def cmd_swl_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.swl_train(switch_id=args.switch_id))
    return 0


def cmd_swl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.swl_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_swl_full(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.swl_full(mimics_fullrank=bool(args.mimics_fullrank)))
    return 0


def cmd_swl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.swl_loop_plan(phase=args.phase))
    return 0


def cmd_col_tune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.col_tune(task=args.task, rank=args.rank))
    return 0


def cmd_col_knot(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.col_knot(tune_id=args.tune_id))
    return 0


def cmd_col_extend(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.col_extend(knot_id=args.knot_id))
    return 0


def cmd_col_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.col_score(extend_id=args.extend_id, score=args.score))
    return 0


def cmd_col_gap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.col_gap(closes_ft_gap=bool(args.closes_ft_gap)))
    return 0


def cmd_col_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.col_loop_plan(phase=args.phase))
    return 0


def cmd_dlr_norm(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlr_norm(task=args.task, rank=args.rank))
    return 0


def cmd_dlr_bound(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.dlr_bound(
            norm_id=args.norm_id, lambda_bound=args.lambda_bound
        )
    )
    return 0


def cmd_dlr_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlr_train(bound_id=args.bound_id))
    return 0


def cmd_dlr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlr_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_dlr_robust(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlr_robust(hyperparam_robust=bool(args.hyperparam_robust)))
    return 0


def cmd_dlr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.dlr_loop_plan(phase=args.phase))
    return 0


def cmd_meo_mini(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.meo_mini(
            task=args.task,
            n_minis=args.n_minis,
            mini_rank=args.mini_rank,
        )
    )
    return 0


def cmd_meo_diag(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.meo_diag(mini_id=args.mini_id))
    return 0


def cmd_meo_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.meo_train(diag_id=args.diag_id))
    return 0


def cmd_meo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.meo_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_meo_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.meo_rank(
            higher_effective_rank=bool(args.higher_effective_rank)
        )
    )
    return 0


def cmd_meo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.meo_loop_plan(phase=args.phase))
    return 0


def cmd_rlr_warm(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlr_warm(task=args.task, steps=args.steps))
    return 0


def cmd_rlr_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlr_merge(warm_id=args.warm_id))
    return 0


def cmd_rlr_jagged(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlr_jagged(merge_id=args.merge_id))
    return 0


def cmd_rlr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlr_score(jagged_id=args.jagged_id, score=args.score))
    return 0


def cmd_rlr_high(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlr_high(high_rank_update=bool(args.high_rank_update)))
    return 0


def cmd_rlr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rlr_loop_plan(phase=args.phase))
    return 0


def cmd_eth_plane(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.eth_plane(task=args.task, reflections=args.reflections))
    return 0


def cmd_eth_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.eth_reflect(plane_id=args.plane_id))
    return 0


def cmd_eth_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.eth_train(reflect_id=args.reflect_id))
    return 0


def cmd_eth_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.eth_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_eth_plus(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.eth_plus(ether_plus=bool(args.ether_plus)))
    return 0


def cmd_eth_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.eth_loop_plan(phase=args.phase))
    return 0


def cmd_lco_concepts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lco_concepts(task=args.task, n_loras=args.n_loras))
    return 0


def cmd_lco_inject(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lco_inject(concepts_id=args.concepts_id))
    return 0


def cmd_lco_isolate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lco_isolate(inject_id=args.inject_id))
    return 0


def cmd_lco_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lco_score(isolate_id=args.isolate_id, score=args.score))
    return 0


def cmd_lco_free(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lco_free(training_free=bool(args.training_free)))
    return 0


def cmd_lco_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lco_loop_plan(phase=args.phase))
    return 0


def cmd_car_compress(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.car_compress(task=args.task, keep_rank=args.keep_rank))
    return 0


def cmd_car_recon(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.car_recon(compress_id=args.compress_id))
    return 0


def cmd_car_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.car_train(recon_id=args.recon_id))
    return 0


def cmd_car_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.car_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_car_mem(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.car_mem(activation_saved=bool(args.activation_saved)))
    return 0


def cmd_car_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.car_loop_plan(phase=args.phase))
    return 0


def cmd_lrr_pair(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrr_pair(task=args.task, n_pairs=args.n_pairs))
    return 0


def cmd_lrr_hyper(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrr_hyper(pair_id=args.pair_id))
    return 0


def cmd_lrr_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrr_merge(hyper_id=args.hyper_id))
    return 0


def cmd_lrr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrr_score(merge_id=args.merge_id, score=args.score))
    return 0


def cmd_lrr_fast(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrr_fast(realtime_merge=bool(args.realtime_merge)))
    return 0


def cmd_lrr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrr_loop_plan(phase=args.phase))
    return 0


def cmd_svf_svd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.svf_svd(task=args.task, keep=args.keep))
    return 0


def cmd_svf_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.svf_sparse(svd_id=args.svd_id))
    return 0


def cmd_svf_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.svf_train(sparse_id=args.sparse_id))
    return 0


def cmd_svf_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.svf_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_svf_geom(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.svf_geom(weight_dependent=bool(args.weight_dependent)))
    return 0


def cmd_svf_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.svf_loop_plan(phase=args.phase))
    return 0


def cmd_fly_proj(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fly_proj(task=args.task, rank=args.rank))
    return 0


def cmd_fly_topk(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fly_topk(proj_id=args.proj_id, k=args.k))
    return 0


def cmd_fly_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fly_train(topk_id=args.topk_id))
    return 0


def cmd_fly_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fly_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_fly_implicit(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fly_implicit(implicit_router=bool(args.implicit_router)))
    return 0


def cmd_fly_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fly_loop_plan(phase=args.phase))
    return 0


def cmd_nla_basis(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nla_basis(task=args.task, n_basis=args.n_basis))
    return 0


def cmd_nla_coeff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nla_coeff(basis_id=args.basis_id))
    return 0


def cmd_nla_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nla_train(coeff_id=args.coeff_id))
    return 0


def cmd_nla_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nla_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_nla_compact(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nla_compact(beyond_rank1=bool(args.beyond_rank1)))
    return 0


def cmd_nla_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nla_loop_plan(phase=args.phase))
    return 0


def cmd_mxl_experts(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mxl_experts(task=args.task, n_experts=args.n_experts))
    return 0


def cmd_mxl_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mxl_route(experts_id=args.experts_id, k=args.k))
    return 0


def cmd_mxl_attn(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mxl_attn(route_id=args.route_id))
    return 0


def cmd_mxl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mxl_score(attn_id=args.attn_id, score=args.score))
    return 0


def cmd_mxl_balance(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mxl_balance(load_balance=bool(args.load_balance)))
    return 0


def cmd_mxl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mxl_loop_plan(phase=args.phase))
    return 0


def cmd_spr_group(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spr_group(task=args.task, groups=args.groups))
    return 0


def cmd_spr_fold(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spr_fold(group_id=args.group_id))
    return 0


def cmd_spr_factor(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spr_factor(fold_id=args.fold_id))
    return 0


def cmd_spr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spr_score(factor_id=args.factor_id, score=args.score))
    return 0


def cmd_spr_unify(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(
        stele.spr_unify(unifies_loha_lokr=bool(args.unifies_loha_lokr))
    )
    return 0


def cmd_spr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.spr_loop_plan(phase=args.phase))
    return 0


def cmd_tld_tie(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tld_tie(task=args.task, layers=args.layers))
    return 0


def cmd_tld_select(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tld_select(tie_id=args.tie_id))
    return 0


def cmd_tld_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tld_scale(select_id=args.select_id))
    return 0


def cmd_tld_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tld_score(scale_id=args.scale_id, score=args.score))
    return 0


def cmd_tld_frac(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tld_frac(fraction_of_lora=bool(args.fraction_of_lora)))
    return 0


def cmd_tld_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tld_loop_plan(phase=args.phase))
    return 0


def cmd_qal_group(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qal_group(task=args.task, groups=args.groups))
    return 0


def cmd_qal_quant(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qal_quant(group_id=args.group_id, bits=args.bits))
    return 0


def cmd_qal_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qal_adapt(quant_id=args.quant_id))
    return 0


def cmd_qal_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qal_score(adapt_id=args.adapt_id, score=args.score))
    return 0


def cmd_qal_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qal_merge(merge_int4=bool(args.merge_int4)))
    return 0


def cmd_qal_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qal_loop_plan(phase=args.phase))
    return 0


def cmd_ulo_space(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ulo_space(task=args.task, dim=args.dim))
    return 0


def cmd_ulo_iso(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ulo_iso(space_id=args.space_id))
    return 0


def cmd_ulo_vec(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ulo_vec(iso_id=args.iso_id))
    return 0


def cmd_ulo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ulo_score(vec_id=args.vec_id, score=args.score))
    return 0


def cmd_ulo_one(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ulo_one(one_vector=bool(args.one_vector)))
    return 0


def cmd_ulo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ulo_loop_plan(phase=args.phase))
    return 0


def cmd_bor_row(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bor_row(task=args.task))
    return 0


def cmd_bor_col(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bor_col(row_id=args.row_id))
    return 0


def cmd_bor_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bor_train(col_id=args.col_id))
    return 0


def cmd_bor_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bor_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_bor_sym(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bor_sym(symmetric=bool(args.symmetric)))
    return 0


def cmd_bor_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bor_loop_plan(phase=args.phase))
    return 0


def cmd_qga_weight(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qga_weight(task=args.task))
    return 0


def cmd_qga_proj(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qga_proj(weight_id=args.weight_id, rank=args.rank))
    return 0


def cmd_qga_lazy(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qga_lazy(proj_id=args.proj_id))
    return 0


def cmd_qga_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qga_score(lazy_id=args.lazy_id, score=args.score))
    return 0


def cmd_qga_mem(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qga_mem(consumer_gpu=bool(args.consumer_gpu)))
    return 0


def cmd_qga_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.qga_loop_plan(phase=args.phase))
    return 0


def cmd_lfw_pool(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfw_pool(task=args.task, n_loras=args.n_loras))
    return 0


def cmd_lfw_gate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfw_gate(pool_id=args.pool_id))
    return 0


def cmd_lfw_token(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfw_token(gate_id=args.gate_id))
    return 0


def cmd_lfw_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfw_score(token_id=args.token_id, score=args.score))
    return 0


def cmd_lfw_few(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfw_few(few_shot=bool(args.few_shot)))
    return 0


def cmd_lfw_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfw_loop_plan(phase=args.phase))
    return 0


def cmd_ros_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ros_rank(task=args.task, rank=args.rank))
    return 0


def cmd_ros_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ros_sparse(rank_id=args.rank_id))
    return 0


def cmd_ros_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ros_train(sparse_id=args.sparse_id))
    return 0


def cmd_ros_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ros_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_ros_fft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ros_fft(matches_fft=bool(args.matches_fft)))
    return 0


def cmd_ros_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ros_loop_plan(phase=args.phase))
    return 0


def cmd_abb_left(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.abb_left(task=args.task, rank=args.rank))
    return 0


def cmd_abb_right(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.abb_right(left_id=args.left_id))
    return 0


def cmd_abb_hadamard(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.abb_hadamard(right_id=args.right_id))
    return 0


def cmd_abb_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.abb_score(hadamard_id=args.hadamard_id, score=args.score))
    return 0


def cmd_abb_expr(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.abb_expr(expressive=bool(args.expressive)))
    return 0


def cmd_abb_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.abb_loop_plan(phase=args.phase))
    return 0


def cmd_bha_split(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bha_split(task=args.task, blocks=args.blocks))
    return 0


def cmd_bha_hadamard(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bha_hadamard(split_id=args.split_id))
    return 0


def cmd_bha_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bha_train(hadamard_id=args.hadamard_id))
    return 0


def cmd_bha_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bha_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_bha_local(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bha_local(localized=bool(args.localized)))
    return 0


def cmd_bha_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bha_loop_plan(phase=args.phase))
    return 0


def cmd_smo_struct(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smo_struct(task=args.task, subspaces=args.subspaces))
    return 0


def cmd_smo_mod(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smo_mod(struct_id=args.struct_id))
    return 0


def cmd_smo_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smo_train(mod_id=args.mod_id))
    return 0


def cmd_smo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smo_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_smo_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smo_rank(high_rank=bool(args.high_rank)))
    return 0


def cmd_smo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.smo_loop_plan(phase=args.phase))
    return 0


def cmd_glo_prompt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.glo_prompt(task=args.task))
    return 0


def cmd_glo_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.glo_scale(prompt_id=args.prompt_id))
    return 0


def cmd_glo_search(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.glo_search(scale_id=args.scale_id))
    return 0


def cmd_glo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.glo_score(search_id=args.search_id, score=args.score))
    return 0


def cmd_glo_zero(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.glo_zero(zero_infer=bool(args.zero_infer)))
    return 0


def cmd_glo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.glo_loop_plan(phase=args.phase))
    return 0


def cmd_plr_stage(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.plr_stage(task=args.task, stages=args.stages))
    return 0


def cmd_plr_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.plr_merge(stage_id=args.stage_id))
    return 0


def cmd_plr_reset(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.plr_reset(merge_id=args.merge_id))
    return 0


def cmd_plr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.plr_score(reset_id=args.reset_id, score=args.score))
    return 0


def cmd_plr_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.plr_rank(accum_rank=bool(args.accum_rank)))
    return 0


def cmd_plr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.plr_loop_plan(phase=args.phase))
    return 0


def cmd_hir_base(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hir_base(task=args.task))
    return 0


def cmd_hir_factors(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hir_factors(base_id=args.base_id, rank=args.rank))
    return 0


def cmd_hir_hadamard(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hir_hadamard(factors_id=args.factors_id))
    return 0


def cmd_hir_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hir_score(hadamard_id=args.hadamard_id, score=args.score))
    return 0


def cmd_hir_merge(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hir_merge(zero_infer=bool(args.zero_infer)))
    return 0


def cmd_hir_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hir_loop_plan(phase=args.phase))
    return 0


def cmd_cnl_pack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cnl_pack(task=args.task, adapters=args.adapters))
    return 0


def cmd_cnl_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cnl_fuse(pack_id=args.pack_id))
    return 0


def cmd_cnl_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cnl_train(fuse_id=args.fuse_id))
    return 0


def cmd_cnl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cnl_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_cnl_hw(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cnl_hw(better_util=bool(args.better_util)))
    return 0


def cmd_cnl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cnl_loop_plan(phase=args.phase))
    return 0


def cmd_llr_window(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llr_window(task=args.task, ctx_len=args.ctx_len))
    return 0


def cmd_llr_shift(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llr_shift(window_id=args.window_id))
    return 0


def cmd_llr_lora(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llr_lora(shift_id=args.shift_id, rank=args.rank))
    return 0


def cmd_llr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llr_score(lora_id=args.lora_id, score=args.score))
    return 0


def cmd_llr_sparse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llr_sparse(sparse_train=bool(args.sparse_train)))
    return 0


def cmd_llr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.llr_loop_plan(phase=args.phase))
    return 0


def cmd_lis_layers(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lis_layers(task=args.task, n=args.n))
    return 0


def cmd_lis_sample(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lis_sample(layers_id=args.layers_id))
    return 0


def cmd_lis_unfreeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lis_unfreeze(sample_id=args.sample_id))
    return 0


def cmd_lis_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lis_score(unfreeze_id=args.unfreeze_id, score=args.score))
    return 0


def cmd_lis_memory(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lis_memory(less_opt=bool(args.less_opt)))
    return 0


def cmd_lis_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lis_loop_plan(phase=args.phase))
    return 0


def cmd_nlr_landmark(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nlr_landmark(task=args.task, k=args.k))
    return 0


def cmd_nlr_nystrom(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nlr_nystrom(landmark_id=args.landmark_id))
    return 0


def cmd_nlr_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nlr_init(nystrom_id=args.nystrom_id, rank=args.rank))
    return 0


def cmd_nlr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nlr_score(init_id=args.init_id, score=args.score))
    return 0


def cmd_nlr_cheap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nlr_cheap(cheaper_svd=bool(args.cheaper_svd)))
    return 0


def cmd_nlr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.nlr_loop_plan(phase=args.phase))
    return 0


def cmd_rsa_subspace(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsa_subspace(task=args.task, dim=args.dim))
    return 0


def cmd_rsa_project(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsa_project(subspace_id=args.subspace_id))
    return 0


def cmd_rsa_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsa_train(project_id=args.project_id))
    return 0


def cmd_rsa_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsa_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_rsa_express(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsa_express(more_expressive=bool(args.more_expressive)))
    return 0


def cmd_rsa_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.rsa_loop_plan(phase=args.phase))
    return 0


def cmd_hra_house(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hra_house(task=args.task, n=args.n))
    return 0


def cmd_hra_reflect(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hra_reflect(house_id=args.house_id))
    return 0


def cmd_hra_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hra_train(reflect_id=args.reflect_id))
    return 0


def cmd_hra_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hra_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_hra_ortho(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hra_ortho(ortho_stable=bool(args.ortho_stable)))
    return 0


def cmd_hra_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hra_loop_plan(phase=args.phase))
    return 0


def cmd_hyb_lora(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyb_lora(task=args.task))
    return 0


def cmd_hyb_boft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyb_boft(lora_id=args.lora_id))
    return 0


def cmd_hyb_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyb_fuse(boft_id=args.boft_id))
    return 0


def cmd_hyb_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyb_score(fuse_id=args.fuse_id, score=args.score))
    return 0


def cmd_hyb_stable(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyb_stable(more_stable=bool(args.more_stable)))
    return 0


def cmd_hyb_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.hyb_loop_plan(phase=args.phase))
    return 0


def cmd_lrt_tensor(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrt_tensor(task=args.task, order=args.order))
    return 0


def cmd_lrt_cp(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrt_cp(tensor_id=args.tensor_id, rank=args.rank))
    return 0


def cmd_lrt_share(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrt_share(cp_id=args.cp_id))
    return 0


def cmd_lrt_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrt_score(share_id=args.share_id, score=args.score))
    return 0


def cmd_lrt_compact(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrt_compact(fewer_params=bool(args.fewer_params)))
    return 0


def cmd_lrt_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lrt_loop_plan(phase=args.phase))
    return 0


def cmd_clo_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.clo_route(task=args.task))
    return 0


def cmd_clo_task(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.clo_task(route_id=args.route_id))
    return 0


def cmd_clo_ortho(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.clo_ortho(task_id=args.task_id))
    return 0


def cmd_clo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.clo_score(ortho_id=args.ortho_id, score=args.score))
    return 0


def cmd_clo_forget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.clo_forget(less_forget=bool(args.less_forget)))
    return 0


def cmd_clo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.clo_loop_plan(phase=args.phase))
    return 0


def cmd_alo_init(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.alo_init(task=args.task, rank=args.rank))
    return 0


def cmd_alo_ablate(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.alo_ablate(init_id=args.init_id))
    return 0


def cmd_alo_prune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.alo_prune(ablate_id=args.ablate_id))
    return 0


def cmd_alo_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.alo_score(prune_id=args.prune_id, score=args.score))
    return 0


def cmd_alo_realloc(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.alo_realloc(dynamic=bool(args.dynamic)))
    return 0


def cmd_alo_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.alo_loop_plan(phase=args.phase))
    return 0


def cmd_lnt_attn(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnt_attn(task=args.task))
    return 0


def cmd_lnt_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnt_scale(attn_id=args.attn_id))
    return 0


def cmd_lnt_train(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnt_train(scale_id=args.scale_id))
    return 0


def cmd_lnt_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnt_score(train_id=args.train_id, score=args.score))
    return 0


def cmd_lnt_cheap(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnt_cheap(cheaper_than_lora=bool(args.cheaper_than_lora)))
    return 0


def cmd_lnt_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lnt_loop_plan(phase=args.phase))
    return 0


def cmd_lfu_split(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfu_split(task=args.task))
    return 0


def cmd_lfu_fuse(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfu_fuse(split_id=args.split_id))
    return 0


def cmd_lfu_batch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfu_batch(fuse_id=args.fuse_id, jobs=args.jobs))
    return 0


def cmd_lfu_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfu_score(batch_id=args.batch_id, score=args.score))
    return 0


def cmd_lfu_speed(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfu_speed(faster_than_mlora=bool(args.faster_than_mlora)))
    return 0


def cmd_lfu_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.lfu_loop_plan(phase=args.phase))
    return 0


def cmd_ter_tucker(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ter_tucker(task=args.task, order=args.order))
    return 0


def cmd_ter_freeze(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ter_freeze(tucker_id=args.tucker_id))
    return 0


def cmd_ter_scale(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ter_scale(freeze_id=args.freeze_id))
    return 0


def cmd_ter_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ter_score(scale_id=args.scale_id, score=args.score))
    return 0


def cmd_ter_highrank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ter_highrank(high_rank_cheap=bool(args.high_rank_cheap)))
    return 0


def cmd_ter_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ter_loop_plan(phase=args.phase))
    return 0


def cmd_tnl_stack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tnl_stack(task=args.task))
    return 0


def cmd_tnl_tucker(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tnl_tucker(stack_id=args.stack_id, ranks=args.ranks))
    return 0


def cmd_tnl_mode(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tnl_mode(tucker_id=args.tucker_id))
    return 0


def cmd_tnl_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tnl_score(mode_id=args.mode_id, score=args.score))
    return 0


def cmd_tnl_budget(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tnl_budget(mode_specific=bool(args.mode_specific)))
    return 0


def cmd_tnl_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.tnl_loop_plan(phase=args.phase))
    return 0


def cmd_azt_tt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.azt_tt(task=args.task, cores=args.cores))
    return 0


def cmd_azt_ff(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.azt_ff(tt_id=args.tt_id))
    return 0


def cmd_azt_query(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.azt_query(ff_id=args.ff_id))
    return 0


def cmd_azt_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.azt_score(query_id=args.query_id, score=args.score))
    return 0


def cmd_azt_mem(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.azt_mem(zo_memory=bool(args.zo_memory)))
    return 0


def cmd_azt_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.azt_loop_plan(phase=args.phase))
    return 0


def cmd_fct_tensor(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fct_tensor(task=args.task))
    return 0


def cmd_fct_tt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fct_tt(tensor_id=args.tensor_id))
    return 0


def cmd_fct_tucker(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fct_tucker(tt_id=args.tt_id))
    return 0


def cmd_fct_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fct_score(tucker_id=args.tucker_id, score=args.score))
    return 0


def cmd_fct_tiny(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fct_tiny(tiny_params=bool(args.tiny_params)))
    return 0


def cmd_fct_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.fct_loop_plan(phase=args.phase))
    return 0


def cmd_ltr_stack(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltr_stack(task=args.task, layers=args.layers))
    return 0


def cmd_ltr_core(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltr_core(stack_id=args.stack_id))
    return 0


def cmd_ltr_share(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltr_share(core_id=args.core_id))
    return 0


def cmd_ltr_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltr_score(share_id=args.share_id, score=args.score))
    return 0


def cmd_ltr_deep(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltr_deep(better_for_deep=bool(args.better_for_deep)))
    return 0


def cmd_ltr_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltr_loop_plan(phase=args.phase))
    return 0


def cmd_cra_mha(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cra_mha(task=args.task))
    return 0


def cmd_cra_ffn(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cra_ffn(mha_id=args.mha_id))
    return 0


def cmd_cra_cpd(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cra_cpd(ffn_id=args.ffn_id))
    return 0


def cmd_cra_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cra_score(cpd_id=args.cpd_id, score=args.score))
    return 0


def cmd_cra_heads(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cra_heads(head_mode=bool(args.head_mode)))
    return 0


def cmd_cra_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.cra_loop_plan(phase=args.phase))
    return 0


def cmd_ltt_adp(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltt_adp(task=args.task))
    return 0


def cmd_ltt_rep(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltt_rep(adp_id=args.adp_id))
    return 0


def cmd_ltt_tt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltt_tt(rep_id=args.rep_id))
    return 0


def cmd_ltt_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltt_score(tt_id=args.tt_id, score=args.score))
    return 0


def cmd_ltt_tiny(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltt_tiny(sub_mb=bool(args.sub_mb)))
    return 0


def cmd_ltt_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.ltt_loop_plan(phase=args.phase))
    return 0


def cmd_c3a_kernel(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.c3a_kernel(task=args.task))
    return 0


def cmd_c3a_circ(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.c3a_circ(kernel_id=args.kernel_id))
    return 0


def cmd_c3a_fft(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.c3a_fft(circ_id=args.circ_id))
    return 0


def cmd_c3a_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.c3a_score(fft_id=args.fft_id, score=args.score))
    return 0


def cmd_c3a_rank(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.c3a_rank(high_rank=bool(args.high_rank)))
    return 0


def cmd_c3a_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.c3a_loop_plan(phase=args.phase))
    return 0


def cmd_bof_block(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bof_block(task=args.task))
    return 0


def cmd_bof_orth(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bof_orth(block_id=args.block_id))
    return 0


def cmd_bof_butter(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bof_butter(orth_id=args.orth_id))
    return 0


def cmd_bof_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bof_score(butter_id=args.butter_id, score=args.score))
    return 0


def cmd_bof_full(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bof_full(full_rank=bool(args.full_rank)))
    return 0


def cmd_bof_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.bof_loop_plan(phase=args.phase))
    return 0


def cmd_sdt_dim(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sdt_dim(task=args.task))
    return 0


def cmd_sdt_mask(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sdt_mask(dim_id=args.dim_id))
    return 0


def cmd_sdt_tune(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sdt_tune(mask_id=args.mask_id))
    return 0


def cmd_sdt_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sdt_score(tune_id=args.tune_id, score=args.score))
    return 0


def cmd_sdt_ssm(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sdt_ssm(ssm_only=bool(args.ssm_only)))
    return 0


def cmd_sdt_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.sdt_loop_plan(phase=args.phase))
    return 0


def cmd_mef_adapt(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mef_adapt(task=args.task))
    return 0


def cmd_mef_route(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mef_route(adapt_id=args.adapt_id))
    return 0


def cmd_mef_fetch(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mef_fetch(route_id=args.route_id))
    return 0


def cmd_mef_score(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mef_score(fetch_id=args.fetch_id, score=args.score))
    return 0


def cmd_mef_cpu(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mef_cpu(cpu_offload=bool(args.cpu_offload)))
    return 0


def cmd_mef_loop(args: argparse.Namespace) -> int:
    stele = _open(args.store, store_id=None, now=args.now, create=False)
    _print(stele.mef_loop_plan(phase=args.phase))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
