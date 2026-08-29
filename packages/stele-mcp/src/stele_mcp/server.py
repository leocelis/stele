"""MCP stdio server — eight named tools over stele-core (TECH_SPEC §7)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from stele_core import Stele

_STORE: Stele | None = None


def get_store() -> Stele:
    global _STORE
    if _STORE is None:
        root = Path(os.environ.get("STELE_STORE", "./.stele-store"))
        now = os.environ.get("STELE_NOW")  # optional fixed clock for tests
        # STELE_STORE_DSN wins over file path when set (hosted durable SoT).
        _STORE = Stele.open(
            root,
            store_id=os.environ.get("STELE_STORE_ID"),
            now=now,
            dsn=os.environ.get("STELE_STORE_DSN"),
        )
    return _STORE


def store_mode() -> str:
    """Return 'mysql' when DSN is configured, else 'file'."""
    return "mysql" if os.environ.get("STELE_STORE_DSN") else "file"


def _transport_security():
    """DNS-rebinding settings for hosted HTTP (stdio ignores this).

    In production, either allow an explicit host list via STELE_ALLOWED_HOSTS,
    or disable rebinding protection and rely on Bearer auth. Default FastMCP
    (localhost-only hosts) breaks App Platform ingress.
    """
    if os.environ.get("STELE_ENV") != "production":
        return None
    try:
        from mcp.server.transport_security import TransportSecuritySettings
    except ImportError:  # pragma: no cover
        try:
            from mcp.server.sse import TransportSecuritySettings
        except ImportError:
            return None

    raw = os.environ.get("STELE_ALLOWED_HOSTS", "")
    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    if hosts:
        return TransportSecuritySettings(
            enable_dns_rebinding_protection=True,
            allowed_hosts=hosts,
        )
    return TransportSecuritySettings(enable_dns_rebinding_protection=False)


mcp = FastMCP("stele", transport_security=_transport_security())


def create_app() -> FastMCP:
    """Return the FastMCP app (stdio CLI and hosted wsgi share this instance)."""
    return mcp


@mcp.tool()
def stele_add(entry_json: str, ts: str | None = None) -> str:
    """ADD a distilled structured entry into quarantine. Pass entry as JSON object string."""
    entry = json.loads(entry_json)
    result = get_store().add(entry, ts=ts)
    return json.dumps(result)


@mcp.tool()
def stele_update(entry_id: str, patch_json: str, actor: str, ts: str | None = None) -> str:
    """UPDATE non-state fields on an existing entry."""
    patch = json.loads(patch_json)
    result = get_store().update(entry_id, patch, actor=actor, ts=ts)
    return json.dumps({"id": result["id"], "state": result["state"]})


@mcp.tool()
def stele_promote(
    entry_id: str,
    evidence_json: str,
    actor: str,
    ts: str | None = None,
    block_injection_suspects: bool = False,
) -> str:
    """PROMOTE a quarantined entry with external-oracle evidence (JSON array)."""
    evidence = json.loads(evidence_json)
    result = get_store().promote(
        entry_id,
        evidence,
        actor=actor,
        ts=ts,
        block_injection_suspects=block_injection_suspects,
    )
    return json.dumps(result)


@mcp.tool()
def stele_supersede(
    old_id: str, new_entry_json: str, actor: str, ts: str | None = None
) -> str:
    """SUPERSEDE an old lesson with a new quarantined entry (history kept)."""
    new_entry = json.loads(new_entry_json)
    result = get_store().supersede(old_id, new_entry, actor=actor, ts=ts)
    return json.dumps(result)


@mcp.tool()
def stele_delete(
    actor: str,
    entry_id: str | None = None,
    subject_id: str | None = None,
    ts: str | None = None,
    reason: str = "erasure",
) -> str:
    """DELETE by entry_id or subject_id (true erase + index rebuild)."""
    result = get_store().delete(
        entry_id=entry_id, subject_id=subject_id, actor=actor, ts=ts, reason=reason
    )
    return json.dumps(result)


@mcp.tool()
def stele_search(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    as_of: str | None = None,
    include_contested: bool = False,
    consumer_env_json: str | None = None,
    consumer_domain: str | None = None,
    stale_policy: str = "flag",
    consumer_model_id: str | None = None,
    model_policy: str = "flag",
    follow_links: bool = False,
    follow_link_depth: int = 1,
    body_max_chars: int | None = None,
    prefer_helpful: bool = True,
    trusted_sources_json: str | None = None,
    prefer_fresh: bool = False,
    principal_scopes_json: str | None = None,
    withhold_injection_suspects: bool = False,
    min_weibull: float | None = None,
    weibull_eta: float = 30.0,
    weibull_kappa: float = 1.0,
) -> str:
    """SEARCH promoted entries; stale/model policies are flag or withhold."""
    consumer_env = json.loads(consumer_env_json) if consumer_env_json else None
    trusted_sources = json.loads(trusted_sources_json) if trusted_sources_json else None
    principal_scopes = json.loads(principal_scopes_json) if principal_scopes_json else None
    result = get_store().search(
        query,
        consumer_scope=consumer_scope,
        budget=budget,
        as_of=as_of,
        include_contested=include_contested,
        consumer_env=consumer_env,
        consumer_domain=consumer_domain,
        stale_policy=stale_policy,
        consumer_model_id=consumer_model_id,
        model_policy=model_policy,
        follow_links=follow_links,
        follow_link_depth=follow_link_depth,
        body_max_chars=body_max_chars,
        prefer_helpful=prefer_helpful,
        trusted_sources=trusted_sources,
        prefer_fresh=prefer_fresh,
        principal_scopes=principal_scopes,
        withhold_injection_suspects=withhold_injection_suspects,
        min_weibull=min_weibull,
        weibull_eta=weibull_eta,
        weibull_kappa=weibull_kappa,
    )
    return json.dumps(result)


@mcp.tool()
def stele_reflect(actor: str, ts: str | None = None, stale_before: str | None = None) -> str:
    """REFLECT: dedupe, expire, surface conflicts (no auto-resolve)."""
    result = get_store().reflect(actor=actor, ts=ts, stale_before=stale_before)
    return json.dumps(result)


@mcp.tool()
def stele_list_contested() -> str:
    """List contested entries awaiting evidenced resolution (TECH_SPEC Q5)."""
    return json.dumps(get_store().list_contested())


@mcp.tool()
def stele_resolve_contested(
    winner_id: str,
    loser_id: str,
    evidence_json: str,
    actor: str,
    ts: str | None = None,
) -> str:
    """Resolve a contested pair by evidenced supersede — never auto-merge."""
    evidence = json.loads(evidence_json)
    result = get_store().resolve_contested(
        winner_id=winner_id,
        loser_id=loser_id,
        evidence=evidence,
        actor=actor,
        ts=ts,
    )
    return json.dumps(result)


@mcp.tool()
def stele_link(
    entry_id: str,
    kind: str,
    ref: str,
    actor: str,
    digest: str | None = None,
    ts: str | None = None,
) -> str:
    """LINK an entry to an artifact, test, entry, or source."""
    result = get_store().link(
        entry_id, kind=kind, ref=ref, digest=digest, actor=actor, ts=ts
    )
    return json.dumps({"id": result["id"], "links": result.get("links")})


@mcp.tool()
def stele_verify() -> str:
    """C4 integrity report: dual-location, schema, journal parse."""
    return json.dumps(get_store().verify())


@mcp.tool()
def stele_reviewer_corrections(limit: int = 10, include_contested: bool = True) -> str:
    """Bounded contested-first correction slice for reviewer roles."""
    return json.dumps(
        get_store().reviewer_corrections(limit=limit, include_contested=include_contested)
    )


@mcp.tool()
def stele_hydrate(
    pack_dir: str,
    actor: str,
    ts: str | None = None,
    promote: bool = False,
    evidence_json: str | None = None,
) -> str:
    """Import a redacted pack (ADD; optional promote with external evidence)."""
    evidence = json.loads(evidence_json) if evidence_json else None
    result = get_store().hydrate(
        pack_dir, actor=actor, ts=ts, promote=promote, evidence=evidence
    )
    return json.dumps(result)


@mcp.tool()
def stele_export(
    dest: str,
    scope: str,
    audience: str,
    purpose: str,
    expiry: str,
    created_at: str | None = None,
    subject_allowlist_json: str | None = None,
) -> str:
    """Export a redacted, audience-tiered pack (storage ≠ pack)."""
    allow = json.loads(subject_allowlist_json) if subject_allowlist_json else None
    result = get_store().export(
        dest,
        scope=scope,
        audience=audience,
        purpose=purpose,
        created_at=created_at,
        expiry=expiry,
        subject_allowlist=allow,
    )
    return json.dumps(result)


@mcp.tool()
def stele_record_outcome(
    entry_id: str, outcome: str, actor: str, ts: str | None = None, note: str | None = None
) -> str:
    """Record helpful/harmful/ignored after using a lesson; helpful refreshes last_verified."""
    return json.dumps(
        get_store().record_outcome(entry_id, outcome, actor=actor, ts=ts, note=note)
    )


@mcp.tool()
def stele_pin(entry_id: str, actor: str, pinned: bool = True, ts: str | None = None) -> str:
    """Pin or unpin a promoted lesson for SEARCH priority."""
    return json.dumps(get_store().pin(entry_id, actor=actor, pinned=pinned, ts=ts))


@mcp.tool()
def stele_stale_report(now: str | None = None) -> str:
    """List promoted entries past the staleness horizon."""
    return json.dumps(get_store().stale_report(now=now))


@mcp.tool()
def stele_reverify(entry_ids_json: str, evidence_json: str, actor: str, ts: str | None = None) -> str:
    """Batch-refresh last_verified with external oracle evidence."""
    ids = json.loads(entry_ids_json)
    evidence = json.loads(evidence_json)
    return json.dumps(get_store().reverify(ids, evidence, actor=actor, ts=ts))


@mcp.tool()
def stele_related(entry_id: str) -> str:
    """Outbound + inbound LINK neighborhood for an entry."""
    return json.dumps(get_store().related(entry_id))


@mcp.tool()
def stele_stats(now: str | None = None) -> str:
    """Store health dashboard: counts by state/layer/scope."""
    return json.dumps(get_store().stats(now=now))


@mcp.tool()
def stele_timeline(entry_id: str) -> str:
    """Journal history for one entry."""
    return json.dumps(get_store().timeline(entry_id))


@mcp.tool()
def stele_verify_pack(pack_dir: str) -> str:
    """Offline pack integrity: stamps + secret scan."""
    return json.dumps(get_store().verify_pack(pack_dir))


@mcp.tool()
def stele_attach(
    data_base64: str,
    actor: str,
    entry_id: str | None = None,
    kind: str = "artifact",
    ts: str | None = None,
) -> str:
    """Content-address bytes (base64); optionally LINK to an entry (FF-6)."""
    import base64

    raw = base64.b64decode(data_base64.encode("ascii"))
    return json.dumps(
        get_store().attach(raw, entry_id=entry_id, actor=actor, kind=kind, ts=ts)
    )


@mcp.tool()
def stele_snapshot(dest: str, actor: str, ts: str | None = None) -> str:
    """Cold-copy SoT (manifest, journal, entries, attachments) to dest."""
    return json.dumps(get_store().snapshot(dest, actor=actor, ts=ts))


@mcp.tool()
def stele_doctor(now: str | None = None) -> str:
    """Operator health report: verify + stats + contested + stale."""
    return json.dumps(get_store().doctor(now=now))


@mcp.tool()
def stele_entry_schema() -> str:
    """JSON Schema 2020-12 for Stele entries (interop)."""
    return json.dumps(get_store().entry_schema())


@mcp.tool()
def stele_purge_by_provenance(
    actor: str,
    untrusted_sources_json: str = "[]",
    untrusted_agents_json: str = "[]",
    dry_run: bool = True,
    ts: str | None = None,
) -> str:
    """Provenance recovery: dry-run or purge entries from untrusted source/agent."""
    return json.dumps(
        get_store().purge_by_provenance(
            untrusted_sources=json.loads(untrusted_sources_json),
            untrusted_agents=json.loads(untrusted_agents_json),
            actor=actor,
            ts=ts,
            dry_run=dry_run,
        )
    )


@mcp.tool()
def stele_diff_stores(other_root: str) -> str:
    """Diff this store vs another root (e.g. snapshot) by entry id sets."""
    return json.dumps(get_store().diff_stores(other_root))


@mcp.tool()
def stele_add_batch(entries_json: str, ts: str | None = None, actor: str | None = None) -> str:
    """Atomic multi-ADD under one lock."""
    return json.dumps(
        get_store().add_batch(json.loads(entries_json), actor=actor, ts=ts)
    )


@mcp.tool()
def stele_entangled_suspects(
    seed_ids_json: str | None = None,
    untrusted_sources_json: str | None = None,
    untrusted_agents_json: str | None = None,
    limit: int = 50,
) -> str:
    """Human-review queue for LINK-entangled poison (report only)."""
    return json.dumps(
        get_store().entangled_suspects(
            seed_ids=json.loads(seed_ids_json) if seed_ids_json else None,
            untrusted_sources=json.loads(untrusted_sources_json)
            if untrusted_sources_json
            else None,
            untrusted_agents=json.loads(untrusted_agents_json)
            if untrusted_agents_json
            else None,
            limit=limit,
        )
    )


@mcp.tool()
def stele_hygiene_candidates(
    now: str | None = None,
    unused_before: str | None = None,
    limit: int = 50,
) -> str:
    """Zombie / net-harm hygiene report — no auto-delete."""
    return json.dumps(
        get_store().hygiene_candidates(
            now=now, unused_before=unused_before, limit=limit
        )
    )


@mcp.tool()
def stele_forget_compliance(
    consumer_scope: str,
    subject_id: str | None = None,
    entry_ids_json: str | None = None,
    probe_query: str | None = None,
    forbidden_substrings_json: str | None = None,
) -> str:
    """Post-erasure active-forgetting probe (GateMem-shaped)."""
    return json.dumps(
        get_store().forget_compliance(
            consumer_scope=consumer_scope,
            subject_id=subject_id,
            entry_ids=json.loads(entry_ids_json) if entry_ids_json else None,
            probe_query=probe_query,
            forbidden_substrings=json.loads(forbidden_substrings_json)
            if forbidden_substrings_json
            else None,
        )
    )


@mcp.tool()
def stele_lineage(entry_id: str) -> str:
    """Supersede chain + journal audit lineage (TOKI-shaped)."""
    return json.dumps(get_store().lineage(entry_id))


@mcp.tool()
def stele_belief_at(
    as_of: str,
    consumer_scope: str,
    query: str | None = None,
    budget: int = 400,
    principal_scopes_json: str | None = None,
) -> str:
    """Bi-temporal point-in-time belief inventory or SEARCH."""
    return json.dumps(
        get_store().belief_at(
            as_of,
            consumer_scope=consumer_scope,
            query=query,
            budget=budget,
            principal_scopes=json.loads(principal_scopes_json)
            if principal_scopes_json
            else None,
        )
    )


@mcp.tool()
def stele_conflict_surface(body_max_chars: int = 240) -> str:
    """Conflict-preserving contested pairs — no auto-collapse."""
    return json.dumps(get_store().conflict_surface(body_max_chars=body_max_chars))


@mcp.tool()
def stele_injection_scan(entry_ids_json: str | None = None, limit: int = 100) -> str:
    """Deterministic injection-marker scan (MIND-inspired; no LLM)."""
    return json.dumps(
        get_store().injection_scan(
            entry_ids=json.loads(entry_ids_json) if entry_ids_json else None,
            limit=limit,
        )
    )


@mcp.tool()
def stele_select_budget_plan(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    withhold_injection_suspects: bool = False,
    principal_scopes_json: str | None = None,
) -> str:
    """Compress-plane plan: fitted vs overflow under a token budget."""
    return json.dumps(
        get_store().select_budget_plan(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            withhold_injection_suspects=withhold_injection_suspects,
            principal_scopes=json.loads(principal_scopes_json)
            if principal_scopes_json
            else None,
        )
    )


@mcp.tool()
def stele_store_seal() -> str:
    """Tamper-evident content+journal seal."""
    return json.dumps(get_store().store_seal())


@mcp.tool()
def stele_verify_seal(seal_json: str) -> str:
    """Compare a prior seal JSON to the live store."""
    return json.dumps(get_store().verify_seal(json.loads(seal_json)))


@mcp.tool()
def stele_attribution_receipt(entry_id: str) -> str:
    """Deterministic attribution receipt for one entry."""
    return json.dumps(get_store().attribution_receipt(entry_id))


@mcp.tool()
def stele_replay_consistency() -> str:
    """Soft journal↔SoT replay consistency report."""
    return json.dumps(get_store().replay_consistency())


@mcp.tool()
def stele_lifecycle_inventory(
    now: str | None = None, hot_days: float = 7.0, warm_days: float = 30.0
) -> str:
    """AMV-L-shaped HOT/WARM/COLD inventory over promoted/contested entries."""
    return json.dumps(
        get_store().lifecycle_inventory(now=now, hot_days=hot_days, warm_days=warm_days)
    )


@mcp.tool()
def stele_revoke_by_key(
    conflict_key: str,
    evidence_json: str,
    actor: str,
    ts: str | None = None,
    keep_id: str | None = None,
) -> str:
    """TEPA-shaped keyed revoke — remove active precedents under conflict_key from SEARCH."""
    evidence = json.loads(evidence_json)
    return json.dumps(
        get_store().revoke_by_key(
            conflict_key, evidence=evidence, actor=actor, ts=ts, keep_id=keep_id
        )
    )


@mcp.tool()
def stele_unrevoke(
    entry_id: str, evidence_json: str, actor: str, ts: str | None = None
) -> str:
    """Re-activate a revoked entry into promoted with evidence."""
    evidence = json.loads(evidence_json)
    return json.dumps(
        get_store().unrevoke(entry_id, evidence=evidence, actor=actor, ts=ts)
    )


@mcp.tool()
def stele_pack_seal(pack_dir: str) -> str:
    """Tamper-evident content seal over an exported pack."""
    return json.dumps(get_store().pack_seal(pack_dir))


@mcp.tool()
def stele_verify_pack_seal(pack_dir: str, seal_json: str) -> str:
    """Verify a prior pack seal against the on-disk pack."""
    seal = json.loads(seal_json)
    return json.dumps(get_store().verify_pack_seal(pack_dir, seal))


@mcp.tool()
def stele_search_explain(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    lifecycle_tiers_json: str | None = None,
) -> str:
    """SEARCH with channel rank detail (lexical/RRF) and lifecycle tier labels."""
    tiers = json.loads(lifecycle_tiers_json) if lifecycle_tiers_json else None
    return json.dumps(
        get_store().search_explain(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            lifecycle_tiers=tiers,
        )
    )


@mcp.tool()
def stele_blast_radius(entry_id: str, max_depth: int = 3) -> str:
    """LINK neighborhood blast radius (who depends on this entry within N hops)."""
    return json.dumps(get_store().blast_radius(entry_id, max_depth=max_depth))


@mcp.tool()
def stele_merge_classify(
    entry_id_a: str,
    entry_id_b: str,
    merge_threshold: float = 0.85,
    relate_threshold: float = 0.45,
) -> str:
    """MELD-shaped five-outcome merge classifier — report only, never mutates."""
    return json.dumps(
        get_store().merge_classify(
            entry_id_a,
            entry_id_b,
            merge_threshold=merge_threshold,
            relate_threshold=relate_threshold,
        )
    )


@mcp.tool()
def stele_path_trust(
    entry_id: str,
    trusted_sources_json: str | None = None,
    max_depth: int = 3,
) -> str:
    """MAP-Graph-shaped multiplicative path trust along entry LINKs."""
    trusted = json.loads(trusted_sources_json) if trusted_sources_json else None
    return json.dumps(
        get_store().path_trust(
            entry_id, trusted_sources=trusted, max_depth=max_depth
        )
    )


@mcp.tool()
def stele_verify_journal_chain() -> str:
    """GPM-shaped journal hash-chain verification."""
    return json.dumps(get_store().verify_journal_chain())


@mcp.tool()
def stele_journal_chain_head() -> str:
    """Current journal chain head + row counts."""
    return json.dumps(get_store().journal_chain_head())


@mcp.tool()
def stele_spread_activate(
    seed_ids_json: str,
    max_hops: int = 2,
    decay: float = 0.5,
    lateral_inhibit: float = 0.15,
) -> str:
    """SYNAPSE-shaped spreading activation from seed entry ids along LINKs."""
    seeds = json.loads(seed_ids_json)
    return json.dumps(
        get_store().spread_activate(
            seeds, max_hops=max_hops, decay=decay, lateral_inhibit=lateral_inhibit
        )
    )


@mcp.tool()
def stele_connection_density(entry_id: str) -> str:
    """SodaMem-shaped connection density for one entry."""
    return json.dumps(get_store().connection_density(entry_id))


@mcp.tool()
def stele_retention_score(
    entry_id: str, now: str | None = None, half_life_days: float = 30.0
) -> str:
    """Oblivion-shaped retention score for one entry."""
    return json.dumps(
        get_store().retention_score(entry_id, now=now, half_life_days=half_life_days)
    )


@mcp.tool()
def stele_health_report(now: str | None = None) -> str:
    """Unified operator health — doctor + journal chain + injection + seal."""
    return json.dumps(get_store().health_report(now=now))


@mcp.tool()
def stele_release_gate(
    expected_head: str | None = None,
    allow_contested: bool = False,
    allow_injection_suspects: bool = False,
    allow_stale: bool = True,
    now: str | None = None,
    issue_receipt: bool = False,
    record_abstain: bool = False,
    actor: str | None = None,
    claim_ids_json: str | None = None,
    policy_version: str = "stele-release-1",
    query_hash: str | None = None,
) -> str:
    """GPM-shaped fail-closed release gate; optional decision receipt."""
    claim_ids = json.loads(claim_ids_json) if claim_ids_json else None
    return json.dumps(
        get_store().release_gate(
            expected_head=expected_head,
            allow_contested=allow_contested,
            allow_injection_suspects=allow_injection_suspects,
            allow_stale=allow_stale,
            now=now,
            issue_receipt=issue_receipt,
            record_abstain=record_abstain,
            actor=actor,
            claim_ids=claim_ids,
            policy_version=policy_version,
            query_hash=query_hash,
        )
    )


@mcp.tool()
def stele_rebuild_sqlite_index() -> str:
    """Rebuild derived SQLite FTS index from file SoT (stdlib; not SoT)."""
    return json.dumps(get_store().rebuild_sqlite_index())


@mcp.tool()
def stele_search_sqlite(
    query: str,
    states_json: str | None = None,
    scopes_json: str | None = None,
    cue: str | None = None,
    limit: int = 20,
) -> str:
    """Query derived SQLite FTS index."""
    states = json.loads(states_json) if states_json else None
    scopes = json.loads(scopes_json) if scopes_json else None
    return json.dumps(
        get_store().search_sqlite(
            query, states=states, scopes=scopes, cue=cue, limit=limit
        )
    )


@mcp.tool()
def stele_verify_import(
    pack_dir: str,
    expected_seal_json: str | None = None,
    expected_policy_digest: str | None = None,
) -> str:
    """PAM-shaped fail-closed import verify (halt on first failure)."""
    seal = json.loads(expected_seal_json) if expected_seal_json else None
    return json.dumps(
        get_store().verify_import(
            pack_dir,
            expected_seal=seal,
            expected_policy_digest=expected_policy_digest,
        )
    )


@mcp.tool()
def stele_list_decision_receipts(limit: int = 50) -> str:
    """List newest local decision receipts (GPM-shaped audit)."""
    return json.dumps(get_store().list_decision_receipts(limit=limit))


@mcp.tool()
def stele_verify_decision_receipt(
    receipt_json: str, require_current_head: bool = False
) -> str:
    """Verify a decision receipt digest (optional live head match)."""
    receipt = json.loads(receipt_json)
    return json.dumps(
        get_store().verify_decision_receipt(
            receipt, require_current_head=require_current_head
        )
    )


@mcp.tool()
def stele_lineage_trust(entry_id: str, max_depth: int = 3) -> str:
    """MemLineage-shaped trust label for one entry."""
    return json.dumps(get_store().lineage_trust(entry_id, max_depth=max_depth))


@mcp.tool()
def stele_record_execution(
    step: str,
    subject_id: str,
    actor: str,
    ts: str | None = None,
    detail_json: str | None = None,
) -> str:
    """PoEM-shaped proof-of-execution append (trusted runtime only)."""
    detail = json.loads(detail_json) if detail_json else None
    return json.dumps(
        get_store().record_execution(
            step, subject_id=subject_id, actor=actor, ts=ts, detail=detail
        )
    )


@mcp.tool()
def stele_verify_execution(step: str, subject_id: str) -> str:
    """Allow safety-step skip only if execution ledger confirms it ran."""
    return json.dumps(get_store().verify_execution(step, subject_id=subject_id))


@mcp.tool()
def stele_authority_gate(entry_ids_json: str, action_risk: str) -> str:
    """PPMF-shaped non-amplification firewall for action risk vs provenance."""
    entry_ids = json.loads(entry_ids_json)
    return json.dumps(get_store().authority_gate(entry_ids, action_risk=action_risk))


@mcp.tool()
def stele_claim_closure(
    claim_ids_json: str, expected_head: str | None = None
) -> str:
    """GPM-shaped exact claim closure over promoted facts."""
    claim_ids = json.loads(claim_ids_json)
    return json.dumps(
        get_store().claim_closure(claim_ids, expected_head=expected_head)
    )


@mcp.tool()
def stele_cascade_impact(fault_id: str, max_depth: int = 5) -> str:
    """MemoRepair-shaped cascade descendants of a fault entry."""
    return json.dumps(get_store().cascade_impact(fault_id, max_depth=max_depth))


@mcp.tool()
def stele_cascade_exposure(fault_id: str, max_depth: int = 5) -> str:
    """Promoted descendants still in service after a fault."""
    return json.dumps(get_store().cascade_exposure(fault_id, max_depth=max_depth))


@mcp.tool()
def stele_withdraw_cascade(
    fault_id: str,
    evidence_json: str,
    actor: str,
    ts: str | None = None,
    max_depth: int = 5,
    include_fault: bool = True,
) -> str:
    """Barrier-first cascade withdraw before repair (MemoRepair-shaped)."""
    evidence = json.loads(evidence_json)
    return json.dumps(
        get_store().withdraw_cascade(
            fault_id,
            evidence=evidence,
            actor=actor,
            ts=ts,
            max_depth=max_depth,
            include_fault=include_fault,
        )
    )


@mcp.tool()
def stele_repair_plan(
    fault_id: str,
    lambda_cost: float = 0.5,
    max_depth: int = 5,
    budget: int | None = None,
) -> str:
    """Predecessor-closed repair selection plan (report-only)."""
    return json.dumps(
        get_store().repair_plan(
            fault_id,
            lambda_cost=lambda_cost,
            max_depth=max_depth,
            budget=budget,
        )
    )


@mcp.tool()
def stele_fact_interface(entry_ids_json: str | None = None) -> str:
    """MemIR-shaped evidence/claim/decision fact interface."""
    ids = json.loads(entry_ids_json) if entry_ids_json else None
    return json.dumps(get_store().fact_interface(ids))


@mcp.tool()
def stele_role_collapse_scan(limit: int = 50) -> str:
    """Scan for provenance-role collapse suspects."""
    return json.dumps(get_store().role_collapse_scan(limit=limit))


@mcp.tool()
def stele_dual_channel_search(
    query: str,
    consumer_scope: str,
    budget: int = 400,
) -> str:
    """D-Mem-shaped routine + deliberation dual-channel Select."""
    return json.dumps(
        get_store().dual_channel_search(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_quality_gate(hits_json: str, min_hits: int = 1) -> str:
    """D-Mem-shaped quality gate over search hits JSON."""
    hits = json.loads(hits_json)
    return json.dumps(get_store().quality_gate(hits, min_hits=min_hits))


@mcp.tool()
def stele_commit_view(
    message: str,
    entry_ids_json: str,
    actor: str,
    ts: str | None = None,
    branch: str = "main",
    outcome: str | None = None,
) -> str:
    """GitOfThoughts-shaped commit of a memory view (no git binary)."""
    entry_ids = json.loads(entry_ids_json)
    return json.dumps(
        get_store().commit_view(
            message,
            entry_ids=entry_ids,
            actor=actor,
            ts=ts,
            branch=branch,
            outcome=outcome,
        )
    )


@mcp.tool()
def stele_checkout_view(commit_hash: str) -> str:
    """Replay entry-id set bound to a commit."""
    return json.dumps(get_store().checkout_view(commit_hash))


@mcp.tool()
def stele_diff_commits(a: str, b: str) -> str:
    """Entry-set diff between two commits."""
    return json.dumps(get_store().diff_commits(a, b))


@mcp.tool()
def stele_copyability_gate(
    query: str,
    consumer_scope: str,
    threshold: float = 0.8,
    budget: int = 400,
) -> str:
    """GitOfThoughts copyability threshold gate over SEARCH hits."""
    return json.dumps(
        get_store().copyability_gate(
            query,
            consumer_scope=consumer_scope,
            threshold=threshold,
            budget=budget,
        )
    )


@mcp.tool()
def stele_pin_memory_version(
    label: str, actor: str, ts: str | None = None
) -> str:
    """ChronoMem-shaped pin of all promoted entries as a named version."""
    return json.dumps(
        get_store().pin_memory_version(label, actor=actor, ts=ts)
    )


@mcp.tool()
def stele_activate_version(commit_hash: str | None = None) -> str:
    """Activate or clear ChronoMem read HEAD (None = live SoT)."""
    return json.dumps(get_store().activate_version(commit_hash))


@mcp.tool()
def stele_counterfactual_search(
    query: str,
    consumer_scope: str,
    version_commit: str,
    budget: int = 400,
) -> str:
    """Search as-if at a prior version without mutating read_head."""
    return json.dumps(
        get_store().counterfactual_search(
            query,
            consumer_scope=consumer_scope,
            version_commit=version_commit,
            budget=budget,
        )
    )


@mcp.tool()
def stele_stale_fact_scan(limit: int = 50) -> str:
    """MemStrata-shaped scan of superseded / non-current facts."""
    return json.dumps(get_store().stale_fact_scan(limit=limit))


@mcp.tool()
def stele_propose_update(entry_json: str) -> str:
    """TARL-shaped classify incoming statement (no write)."""
    return json.dumps(get_store().propose_update(json.loads(entry_json)))


@mcp.tool()
def stele_apply_update(
    entry_json: str, actor: str, action: str | None = None, ts: str | None = None
) -> str:
    """Execute TARL action (append/noop/revise/reject_conflict/defer_verify)."""
    return json.dumps(
        get_store().apply_update(
            json.loads(entry_json), actor=actor, action=action, ts=ts
        )
    )


@mcp.tool()
def stele_ledger_view() -> str:
    """TARL accepted / pending / rejected ledger projection."""
    return json.dumps(get_store().ledger_view())


@mcp.tool()
def stele_memory_worth(entry_id: str) -> str:
    """Memory Worth (helpful/(helpful+harmful)) for one entry."""
    return json.dumps(get_store().memory_worth(entry_id))


@mcp.tool()
def stele_low_worth_scan(
    threshold: float = 0.4, min_samples: int = 2, limit: int = 50
) -> str:
    """Scan entries below Memory Worth threshold."""
    return json.dumps(
        get_store().low_worth_scan(
            threshold=threshold, min_samples=min_samples, limit=limit
        )
    )


@mcp.tool()
def stele_begin_transaction(
    actor: str, risk_tier: str = "write", ts: str | None = None
) -> str:
    """MemTX open staging transaction (write ≠ commit)."""
    return json.dumps(
        get_store().begin_transaction(
            actor=actor, risk_tier=risk_tier, ts=ts
        )
    )


@mcp.tool()
def stele_stage_write(
    txid: str, entry_json: str, actor: str | None = None, ts: str | None = None
) -> str:
    """Stage tentative ADD inside an open MemTX transaction."""
    return json.dumps(
        get_store().stage_write(
            txid, json.loads(entry_json), actor=actor, ts=ts
        )
    )


@mcp.tool()
def stele_commit_transaction(
    txid: str, evidence_json: str, actor: str, ts: str | None = None
) -> str:
    """Promote staged entries — MemTX belief commit."""
    return json.dumps(
        get_store().commit_transaction(
            txid, json.loads(evidence_json), actor=actor, ts=ts
        )
    )


@mcp.tool()
def stele_abort_transaction(
    txid: str, actor: str, reason: str = "abort", ts: str | None = None
) -> str:
    """Abort MemTX transaction and revoke staged tentative entries."""
    return json.dumps(
        get_store().abort_transaction(
            txid, actor=actor, reason=reason, ts=ts
        )
    )


@mcp.tool()
def stele_action_safe_gate(entry_ids_json: str) -> str:
    """Gate irreversible tools on action-safe (promoted) beliefs only."""
    return json.dumps(
        get_store().action_safe_gate(json.loads(entry_ids_json))
    )


@mcp.tool()
def stele_in_flight_report(limit: int = 50) -> str:
    """List open MemTX transactions and staged tentative ids."""
    return json.dumps(get_store().in_flight_report(limit=limit))


@mcp.tool()
def stele_symbolic_conflict_scan(limit: int = 50) -> str:
    """LatticeMind-shaped mechanical key-conflict and LINK-cycle scan."""
    return json.dumps(get_store().symbolic_conflict_scan(limit=limit))


@mcp.tool()
def stele_classify_conflict(entry_id_a: str, entry_id_b: str) -> str:
    """Classify credibility vs coordination conflict (no LLM)."""
    return json.dumps(get_store().classify_conflict(entry_id_a, entry_id_b))


@mcp.tool()
def stele_compact_render(
    query: str,
    consumer_scope: str,
    reader_budget: int = 1400,
    budget: int = 400,
) -> str:
    """SEARCH then compact render under LatticeMind reader character budget."""
    return json.dumps(
        get_store().compact_render(
            query,
            consumer_scope=consumer_scope,
            reader_budget=reader_budget,
            budget=budget,
        )
    )


@mcp.tool()
def stele_stage_effect(
    sink: str,
    payload_json: str,
    actor: str,
    txid: str | None = None,
    belief_ids_json: str | None = None,
    ts: str | None = None,
) -> str:
    """Cordon-shaped stage irreversible tool effect in outbox."""
    belief_ids = json.loads(belief_ids_json) if belief_ids_json else None
    return json.dumps(
        get_store().stage_effect(
            sink=sink,
            payload=json.loads(payload_json),
            actor=actor,
            txid=txid,
            belief_ids=belief_ids,
            ts=ts,
        )
    )


@mcp.tool()
def stele_release_effects(
    txid: str | None = None, effect_ids_json: str | None = None
) -> str:
    """Mark pending effects ready after belief commit."""
    effect_ids = json.loads(effect_ids_json) if effect_ids_json else None
    return json.dumps(
        get_store().release_effects(txid=txid, effect_ids=effect_ids)
    )


@mcp.tool()
def stele_list_effects(
    state: str | None = None, txid: str | None = None, limit: int = 50
) -> str:
    """List Cordon effect outbox rows."""
    return json.dumps(
        get_store().list_effects(state=state, txid=txid, limit=limit)
    )


@mcp.tool()
def stele_state_resolution(conflict_key: str | None = None) -> str:
    """STALE State Resolution proxy over conflict keys."""
    return json.dumps(get_store().state_resolution(conflict_key=conflict_key))


@mcp.tool()
def stele_premise_resistance(
    query: str, consumer_scope: str | None = None
) -> str:
    """STALE Premise Resistance — refuse stale-dominated query premises."""
    return json.dumps(
        get_store().premise_resistance(query, consumer_scope=consumer_scope)
    )


@mcp.tool()
def stele_ipa_gap_scan(
    query: str, consumer_scope: str, budget: int = 400
) -> str:
    """STALE IPA gap scan (live Select vs supersession winners)."""
    return json.dumps(
        get_store().ipa_gap_scan(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_verify_transition(old_id: str, new_id: str) -> str:
    """VTA-shaped provenance/chronology verify for a supersede pair."""
    return json.dumps(get_store().verify_transition(old_id, new_id))


@mcp.tool()
def stele_related_slot_scan(conflict_key: str) -> str:
    """Same-domain propagation candidates after a state change."""
    return json.dumps(get_store().related_slot_scan(conflict_key))


@mcp.tool()
def stele_gem_report() -> str:
    """GEM six-condition obligation coverage checklist."""
    return json.dumps(get_store().gem_report())


@mcp.tool()
def stele_project_resolve(conflict_key: str) -> str:
    """StateFuse projection-time resolve — select or abstain; SoT unchanged."""
    return json.dumps(get_store().project_resolve(conflict_key))


@mcp.tool()
def stele_correction_handle(
    claim_id: str | None = None,
    claim_ref: str | None = None,
    limit: int = 20,
) -> str:
    """StateFuse exact claim_id or semantic claim_ref correction handle."""
    return json.dumps(
        get_store().correction_handle(
            claim_id=claim_id, claim_ref=claim_ref, limit=limit
        )
    )


@mcp.tool()
def stele_pin_projection(
    conflict_key: str, chosen_id: str, actor: str, ts: str | None = None
) -> str:
    """Pin projection choice without rewriting SoT entries."""
    return json.dumps(
        get_store().pin_projection(
            conflict_key, chosen_id, actor=actor, ts=ts
        )
    )


@mcp.tool()
def stele_clear_projection_pin(conflict_key: str) -> str:
    """Clear a projection pin overlay."""
    return json.dumps(get_store().clear_projection_pin(conflict_key))


@mcp.tool()
def stele_list_projection_pins(limit: int = 50) -> str:
    """List projection pins (overlay, not SoT)."""
    return json.dumps(get_store().list_projection_pins(limit=limit))


@mcp.tool()
def stele_toki_classify_operator(
    candidate_json: str,
    tip_id: str | None = None,
    evidence_json: str | None = None,
    policy_rule: str | None = None,
) -> str:
    """TOKI-shaped classify intended write operator (does not write)."""
    candidate = json.loads(candidate_json)
    evidence = json.loads(evidence_json) if evidence_json else None
    return json.dumps(
        get_store().toki_classify_operator(
            candidate,
            tip_id=tip_id,
            evidence=evidence,
            policy_rule=policy_rule,
        )
    )


@mcp.tool()
def stele_toki_anomaly_scan(limit: int = 50) -> str:
    """TOKI-shaped write-anomaly proxies."""
    return json.dumps(get_store().toki_anomaly_scan(limit=limit))


@mcp.tool()
def stele_context_bid(query: str, slots: int = 5, now: str | None = None) -> str:
    """MemArchitect-shaped triage & bid for context slots."""
    return json.dumps(get_store().context_bid(query, slots=slots, now=now))


@mcp.tool()
def stele_repair_select_mincut(
    fault_id: str, lambda_cost: float = 0.5, max_depth: int = 5
) -> str:
    """Exact MemoRepair-shaped s–t min-cut repair selection."""
    return json.dumps(
        get_store().repair_select_mincut(
            fault_id, lambda_cost=lambda_cost, max_depth=max_depth
        )
    )


@mcp.tool()
def stele_adjudicate_update(
    candidate_json: str, evidence_json: str | None = None
) -> str:
    """CUPMem-shaped write-side adjudication (does not write)."""
    candidate = json.loads(candidate_json)
    evidence = json.loads(evidence_json) if evidence_json else None
    return json.dumps(
        get_store().adjudicate_update(candidate, evidence=evidence)
    )


@mcp.tool()
def stele_unknown_current_slots() -> str:
    """CUPMem unknown-current / unsafe assertability slots."""
    return json.dumps(get_store().unknown_current_slots())


@mcp.tool()
def stele_authorize_retrieval(
    hit_ids_json: str | None = None,
    query: str = "",
    consumer_scope: str | None = None,
) -> str:
    """CUPMem authorize retrieval — settled promoted slots only."""
    hit_ids = json.loads(hit_ids_json) if hit_ids_json else None
    return json.dumps(
        get_store().authorize_retrieval(
            hit_ids, query=query, consumer_scope=consumer_scope
        )
    )


@mcp.tool()
def stele_admit_gate(
    action: str,
    actor: str,
    authority_bundle_json: str | None = None,
    entry_id: str | None = None,
    ts: str | None = None,
) -> str:
    """CMGL-shaped fail-closed procedural admit before protected writes."""
    bundle = json.loads(authority_bundle_json) if authority_bundle_json else None
    return json.dumps(
        get_store().admit_gate(
            action=action,
            actor=actor,
            authority_bundle=bundle,
            entry_id=entry_id,
            ts=ts,
        )
    )


@mcp.tool()
def stele_list_admit_receipts(limit: int = 50) -> str:
    """List CMGL-shaped governance admission receipts."""
    return json.dumps(get_store().list_admit_receipts(limit=limit))


@mcp.tool()
def stele_put_raw_page(
    text: str, actor: str, ts: str | None = None, meta_json: str | None = None
) -> str:
    """TierMem Tier-2 immutable raw page."""
    meta = json.loads(meta_json) if meta_json else None
    return json.dumps(
        get_store().put_raw_page(text, actor=actor, ts=ts, meta=meta)
    )


@mcp.tool()
def stele_sufficiency_gate(
    query: str, consumer_scope: str, budget: int = 400
) -> str:
    """TierMem sufficiency gate over summary-first Select."""
    return json.dumps(
        get_store().sufficiency_gate(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_escalate_raw(
    summary_ids_json: str, max_pages: int = 8
) -> str:
    """TierMem escalate to linked raw pages."""
    ids = json.loads(summary_ids_json)
    return json.dumps(get_store().escalate_raw(ids, max_pages=max_pages))


@mcp.tool()
def stele_verified_writeback(
    title: str,
    body: str,
    scope: str,
    raw_digests_json: str,
    actor: str,
    ts: str | None = None,
    conflict_key: str | None = None,
    promote: bool = False,
    evidence_json: str | None = None,
) -> str:
    """TierMem verified write-back of summary linked to raw digests."""
    digests = json.loads(raw_digests_json)
    evidence = json.loads(evidence_json) if evidence_json else None
    return json.dumps(
        get_store().verified_writeback(
            title=title,
            body=body,
            scope=scope,
            raw_digests=digests,
            actor=actor,
            ts=ts,
            conflict_key=conflict_key,
            promote=promote,
            evidence=evidence,
        )
    )


@mcp.tool()
def stele_skill_eligibility(entry_id: str) -> str:
    """MSCE skill eligibility check."""
    return json.dumps(get_store().skill_eligibility(entry_id))


@mcp.tool()
def stele_crystallize_skill(
    source_ids_json: str,
    title: str | None = None,
    scope: str | None = None,
    env_assumptions_json: str | None = None,
    actor: str | None = None,
    ts: str | None = None,
    write: bool = False,
) -> str:
    """MSCE crystallize skill draft; optional write."""
    source_ids = json.loads(source_ids_json)
    env = json.loads(env_assumptions_json) if env_assumptions_json else None
    return json.dumps(
        get_store().crystallize_skill(
            source_ids,
            title=title,
            scope=scope,
            env_assumptions=env,
            actor=actor,
            ts=ts,
            write=write,
        )
    )


@mcp.tool()
def stele_skill_catalog(states_json: str | None = None) -> str:
    """MSCE skill catalog."""
    states = json.loads(states_json) if states_json else None
    return json.dumps(get_store().skill_catalog(states=states))


@mcp.tool()
def stele_fade_strength(entry_id: str, now: str | None = None) -> str:
    """FadeMem dual-layer strength for one entry."""
    return json.dumps(get_store().fade_strength(entry_id, now=now))


@mcp.tool()
def stele_fade_scan(
    now: str | None = None, threshold: float = 0.15, limit: int = 50
) -> str:
    """FadeMem fade candidates below threshold (report only)."""
    return json.dumps(
        get_store().fade_scan(now=now, threshold=threshold, limit=limit)
    )


@mcp.tool()
def stele_fusion_candidates(
    min_overlap: float = 0.45, limit: int = 20
) -> str:
    """FadeMem deterministic fusion-candidate pairs."""
    return json.dumps(
        get_store().fusion_candidates(min_overlap=min_overlap, limit=limit)
    )


@mcp.tool()
def stele_weibull_relevance(
    entry_id: str,
    now: str | None = None,
    eta_days: float = 30.0,
    kappa: float = 1.0,
) -> str:
    """SSGM Weibull relevance for one entry."""
    return json.dumps(
        get_store().weibull_relevance(
            entry_id, now=now, eta_days=eta_days, kappa=kappa
        )
    )


@mcp.tool()
def stele_evidence_gap(
    query: str, consumer_scope: str, budget: int = 400
) -> str:
    """MemR3 evidence-gap over Select hits."""
    return json.dumps(
        get_store().evidence_gap(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_reflective_retrieve(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    coverage_target: float = 0.85,
) -> str:
    """MemR3 reflective retrieve plan (gap + next probes)."""
    return json.dumps(
        get_store().reflective_retrieve(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            coverage_target=coverage_target,
        )
    )


@mcp.tool()
def stele_archive_plan(
    min_age_days: float = 14.0,
    max_fade_strength: float = 0.35,
    limit: int = 50,
) -> str:
    """Utility-weighted archive candidates (report only)."""
    return json.dumps(
        get_store().archive_plan(
            min_age_days=min_age_days,
            max_fade_strength=max_fade_strength,
            limit=limit,
        )
    )


@mcp.tool()
def stele_archive_apply(
    entry_ids_json: str,
    actor: str,
    ts: str | None = None,
    require_eligible: bool = True,
) -> str:
    """Archive promoted entries out of Select (reversible)."""
    ids = json.loads(entry_ids_json)
    return json.dumps(
        get_store().archive_apply(
            ids, actor=actor, ts=ts, require_eligible=require_eligible
        )
    )


@mcp.tool()
def stele_unarchive(entry_id: str, actor: str, ts: str | None = None) -> str:
    """Restore archived entry to promoted."""
    return json.dumps(get_store().unarchive(entry_id, actor=actor, ts=ts))


@mcp.tool()
def stele_list_archived() -> str:
    """List archived entries."""
    return json.dumps(get_store().list_archived())


@mcp.tool()
def stele_composite_importance(entry_id: str, now: str | None = None) -> str:
    """SF-AMS composite importance score."""
    return json.dumps(get_store().composite_importance(entry_id, now=now))


@mcp.tool()
def stele_cis_scan(tiers_json: str | None = None, limit: int = 100) -> str:
    """SF-AMS CIS ranking scan."""
    tiers = json.loads(tiers_json) if tiers_json else None
    return json.dumps(get_store().cis_scan(tiers=tiers, limit=limit))


@mcp.tool()
def stele_control_suggest(
    query: str, consumer_scope: str, budget: int = 400
) -> str:
    """MemCon-shaped memory control action suggestion."""
    return json.dumps(
        get_store().control_suggest(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_value_tag(
    entry_id: str, task_query: str = "", now: str | None = None
) -> str:
    """SCM 4D value tag."""
    return json.dumps(
        get_store().value_tag(entry_id, now=now, task_query=task_query)
    )


@mcp.tool()
def stele_wm_push(
    entry_id: str, capacity: int | None = None, note: str = ""
) -> str:
    """Push entry into SCM working-memory ring."""
    return json.dumps(
        get_store().wm_push(entry_id, capacity=capacity, note=note)
    )


@mcp.tool()
def stele_wm_list() -> str:
    """List SCM working memory."""
    return json.dumps(get_store().wm_list())


@mcp.tool()
def stele_sleep_trigger(force: bool = False) -> str:
    """SCM sleep trigger."""
    return json.dumps(get_store().sleep_trigger(force=force))


@mcp.tool()
def stele_sleep_plan() -> str:
    """SCM sleep cycle plan (NREM/REM/FORGET)."""
    return json.dumps(get_store().sleep_plan())


@mcp.tool()
def stele_sleep_apply_nrem(actor: str, now: str | None = None) -> str:
    """Apply SCM NREM reinforce from sleep plan."""
    return json.dumps(get_store().sleep_apply_nrem(actor=actor, now=now))


@mcp.tool()
def stele_episodic_buffer(limit: int = 20) -> str:
    """GAM episodic buffer (quarantined)."""
    return json.dumps(get_store().episodic_buffer(limit=limit))


@mcp.tool()
def stele_semantic_boundary(
    previous: str, current: str, threshold: float = 0.35
) -> str:
    """GAM semantic topic-shift detector."""
    return json.dumps(
        get_store().semantic_boundary(
            previous, current, threshold=threshold
        )
    )


@mcp.tool()
def stele_consolidate_plan(
    min_overlap: float = 0.25, limit: int = 20
) -> str:
    """GAM consolidate candidates (report only)."""
    return json.dumps(
        get_store().consolidate_plan(
            min_overlap=min_overlap, limit=limit
        )
    )


@mcp.tool()
def stele_anticipate(
    query: str, consumer_scope: str, budget: int = 400, limit: int = 10
) -> str:
    """ACM anticipate prefetch."""
    return json.dumps(
        get_store().anticipate(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            limit=limit,
        )
    )


@mcp.tool()
def stele_verify_compaction(
    query: str,
    compacted_text: str,
    consumer_scope: str,
    budget: int = 400,
) -> str:
    """ACM verifiable compaction check."""
    return json.dumps(
        get_store().verify_compaction(
            query,
            compacted_text,
            consumer_scope=consumer_scope,
            budget=budget,
        )
    )


@mcp.tool()
def stele_sensory_filter(text: str, keep_ratio: float = 1.0) -> str:
    """LightMem sensory pre-compression."""
    return json.dumps(get_store().sensory_filter(text, keep_ratio=keep_ratio))


@mcp.tool()
def stele_stage_inventory() -> str:
    """LightMem stage inventory."""
    return json.dumps(get_store().stage_inventory())


@mcp.tool()
def stele_topic_segments(texts_json: str, threshold: float = 0.35) -> str:
    """LightMem topic segmentation."""
    texts = json.loads(texts_json)
    return json.dumps(get_store().topic_segments(texts, threshold=threshold))


@mcp.tool()
def stele_stage_budget_plan(
    query: str, consumer_scope: str, budget: int = 400
) -> str:
    """LightMem stage budget plan."""
    return json.dumps(
        get_store().stage_budget_plan(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_ppr_scores(
    seed_ids_json: str, damping: float = 0.85, iterations: int = 20
) -> str:
    """HippoRAG-shaped Personalized PageRank."""
    seeds = json.loads(seed_ids_json)
    return json.dumps(
        get_store().ppr_scores(
            seeds, damping=damping, iterations=iterations
        )
    )


@mcp.tool()
def stele_multi_hop_retrieve(
    query: str, seed_limit: int = 5, result_limit: int = 10
) -> str:
    """HippoRAG multi-hop retrieve."""
    return json.dumps(
        get_store().multi_hop_retrieve(
            query, seed_limit=seed_limit, result_limit=result_limit
        )
    )


@mcp.tool()
def stele_write_gate(pending_json: str) -> str:
    """Quipu write gate on pending post-state."""
    pending = json.loads(pending_json)
    return json.dumps(get_store().write_gate(pending))


@mcp.tool()
def stele_action_risk_gate(
    supporting_ids_json: str,
    risk: str = "medium",
    trusted_sources_json: str | None = None,
) -> str:
    """MAP-Graph action risk gate."""
    ids = json.loads(supporting_ids_json)
    trusted = (
        json.loads(trusted_sources_json) if trusted_sources_json else None
    )
    return json.dumps(
        get_store().action_risk_gate(
            ids, risk=risk, trusted_sources=trusted
        )
    )


@mcp.tool()
def stele_extract_residuals(entry_id: str) -> str:
    """ProGraph compression residuals for one entry."""
    return json.dumps(get_store().extract_residuals(entry_id))


@mcp.tool()
def stele_register_entities() -> str:
    """ProGraph entity registry."""
    return json.dumps(get_store().register_entities())


@mcp.tool()
def stele_profile_expand(
    query: str,
    expand_threshold: float = 0.2,
    seed_limit: int = 5,
    expand_limit: int = 10,
) -> str:
    """ProGraph profile expansion."""
    return json.dumps(
        get_store().profile_expand(
            query,
            expand_threshold=expand_threshold,
            seed_limit=seed_limit,
            expand_limit=expand_limit,
        )
    )


@mcp.tool()
def stele_residual_augment(
    query: str, entry_ids_json: str, limit_per_entry: int = 5
) -> str:
    """ProGraph residual-augmented context."""
    ids = json.loads(entry_ids_json)
    return json.dumps(
        get_store().residual_augment(
            query, ids, limit_per_entry=limit_per_entry
        )
    )


@mcp.tool()
def stele_match_correction(
    failure_id: str | None = None,
    min_overlap: float = 0.15,
    limit: int = 10,
) -> str:
    """EMG match failure lessons to successful workflows."""
    return json.dumps(
        get_store().match_correction(
            failure_id=failure_id,
            min_overlap=min_overlap,
            limit=limit,
        )
    )


@mcp.tool()
def stele_insight_inject(correction_json: str) -> str:
    """EMG format a loop-free correction insight."""
    correction = json.loads(correction_json)
    return json.dumps(get_store().insight_inject(correction))


@mcp.tool()
def stele_cascade_route(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    margin_threshold: float = 0.25,
) -> str:
    """AgentIR cascade routing decision."""
    return json.dumps(
        get_store().cascade_route(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            margin_threshold=margin_threshold,
        )
    )


@mcp.tool()
def stele_multi_channel_fuse(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    k: int = 60,
    result_limit: int = 10,
    force_full: bool = False,
) -> str:
    """AgentIR multi-channel RRF fuse."""
    return json.dumps(
        get_store().multi_channel_fuse(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            k=k,
            result_limit=result_limit,
            force_full=force_full,
        )
    )


@mcp.tool()
def stele_dual_project(entry_id: str) -> str:
    """Governed Memory dual fact/property projection."""
    return json.dumps(get_store().dual_project(entry_id))


@mcp.tool()
def stele_governance_route(
    task: str, limit: int = 7, critical_threshold: float = 0.35
) -> str:
    """Governed Memory fast governance routing."""
    return json.dumps(
        get_store().governance_route(
            task, limit=limit, critical_threshold=critical_threshold
        )
    )


@mcp.tool()
def stele_session_delta_open(session_id: str, ttl_hours: float = 24.0) -> str:
    """Open progressive-delivery session."""
    return json.dumps(
        get_store().session_delta_open(session_id, ttl_hours=ttl_hours)
    )


@mcp.tool()
def stele_session_delta_deliver(session_id: str, route_json: str) -> str:
    """Progressive delta delivery for a session."""
    route = json.loads(route_json)
    return json.dumps(get_store().session_delta_deliver(session_id, route))


@mcp.tool()
def stele_session_delta_status(session_id: str) -> str:
    """Inspect progressive-delivery session state."""
    return json.dumps(get_store().session_delta_status(session_id))


@mcp.tool()
def stele_entity_context(
    subject_id: str, budget: int = 400, saturation: int = 7
) -> str:
    """Compile entity Properties + Observations."""
    return json.dumps(
        get_store().entity_context(
            subject_id, budget=budget, saturation=saturation
        )
    )


@mcp.tool()
def stele_entity_leak_probe(
    subject_id: str,
    consumer_scope: str,
    query: str = "",
    budget: int = 400,
    prefilter: bool = True,
) -> str:
    """Probe Select hits for cross-entity leakage."""
    return json.dumps(
        get_store().entity_leak_probe(
            subject_id,
            query=query,
            consumer_scope=consumer_scope,
            budget=budget,
            prefilter=prefilter,
        )
    )


@mcp.tool()
def stele_hymem_classify_slot(text: str) -> str:
    """HyMem typed context slot classification."""
    return json.dumps(get_store().hymem_classify_slot(text))


@mcp.tool()
def stele_hymem_isolate_pack(
    items_json: str, planner_budget: int = 200
) -> str:
    """HyMem typed isolation planner pack."""
    items = json.loads(items_json)
    return json.dumps(
        get_store().hymem_isolate_pack(items, planner_budget=planner_budget)
    )


@mcp.tool()
def stele_extract_version_markers(entry_id: str) -> str:
    """Extract serial/ISO version markers."""
    return json.dumps(get_store().extract_version_markers(entry_id))


@mcp.tool()
def stele_freshness_resolve(conflict_key: str | None = None) -> str:
    """Deterministic freshness resolve."""
    return json.dumps(get_store().freshness_resolve(conflict_key=conflict_key))


@mcp.tool()
def stele_assemble_current(query: str, limit: int = 10) -> str:
    """Candidate extract + freshness assemble."""
    return json.dumps(get_store().assemble_current(query, limit=limit))


@mcp.tool()
def stele_hop_freshness(hops_json: str, limit_per_hop: int = 3) -> str:
    """Per-hop deterministic freshness assembly."""
    hops = json.loads(hops_json)
    return json.dumps(
        get_store().hop_freshness(hops, limit_per_hop=limit_per_hop)
    )


@mcp.tool()
def stele_patch_test(
    pending_json: str, source_id: str, cited_span: str | None = None
) -> str:
    """MemTxn Ordered PatchTest."""
    pending = json.loads(pending_json)
    return json.dumps(
        get_store().patch_test(pending, source_id, cited_span=cited_span)
    )


@mcp.tool()
def stele_temporal_resolve(conflict_key: str) -> str:
    """MemTxn Temporal Resolver."""
    return json.dumps(get_store().temporal_resolve(conflict_key))


@mcp.tool()
def stele_recover_active_map(conflict_keys_json: str | None = None) -> str:
    """Recover active tip map per conflict_key."""
    keys = json.loads(conflict_keys_json) if conflict_keys_json else None
    return json.dumps(get_store().recover_active_map(keys))


@mcp.tool()
def stele_fleet_scope_gate(entry_id: str, allowed_scopes_json: str) -> str:
    """Fleet scope allowlist gate."""
    scopes = json.loads(allowed_scopes_json)
    return json.dumps(
        get_store().fleet_scope_gate(entry_id, allowed_scopes=scopes)
    )


@mcp.tool()
def stele_propagate_plan(
    source_scope: str,
    target_scopes_json: str,
    query: str = "",
    limit: int = 10,
) -> str:
    """Report-only cross-scope propagation plan."""
    targets = json.loads(target_scopes_json)
    return json.dumps(
        get_store().propagate_plan(
            source_scope=source_scope,
            target_scopes=targets,
            query=query,
            limit=limit,
        )
    )


@mcp.tool()
def stele_stale_propagation_scan(limit: int = 50) -> str:
    """Scan stale promoted tips beside fresher winners."""
    return json.dumps(get_store().stale_propagation_scan(limit=limit))


@mcp.tool()
def stele_query_complexity(query: str) -> str:
    """BudgetMem query complexity heuristic."""
    return json.dumps(get_store().query_complexity(query))


@mcp.tool()
def stele_budget_tier_route(query: str) -> str:
    """BudgetMem per-module Low/Mid/High routing."""
    return json.dumps(get_store().budget_tier_route(query))


@mcp.tool()
def stele_budget_module_plan(query: str, global_budget: int = 10) -> str:
    """Fit BudgetMem tiers under a global cost budget."""
    return json.dumps(
        get_store().budget_module_plan(query, global_budget=global_budget)
    )


@mcp.tool()
def stele_skill_rank(query: str, limit: int = 5) -> str:
    """Lexical skill/workflow library ranker."""
    return json.dumps(get_store().skill_rank(query, limit=limit))


@mcp.tool()
def stele_skill_prereq_expand(
    skill_id: str, depth: int = 2, limit: int = 10
) -> str:
    """Expand skill prerequisites via LINKs."""
    return json.dumps(
        get_store().skill_prereq_expand(skill_id, depth=depth, limit=limit)
    )


@mcp.tool()
def stele_list_retrieval_primitives() -> str:
    """ERSkill retrieval primitive catalog."""
    return json.dumps(get_store().list_retrieval_primitives())


@mcp.tool()
def stele_list_retrieval_skills() -> str:
    """ERSkill built-in retrieval skills."""
    return json.dumps(get_store().list_retrieval_skills())


@mcp.tool()
def stele_compose_retrieval_skill(name: str, primitives_json: str) -> str:
    """Validate a custom retrieval skill composition."""
    primitives = json.loads(primitives_json)
    return json.dumps(get_store().compose_retrieval_skill(name, primitives))


@mcp.tool()
def stele_route_retrieval_skill(query: str) -> str:
    """Cue-based retrieval skill router."""
    return json.dumps(get_store().route_retrieval_skill(query))


@mcp.tool()
def stele_run_retrieval_skill(
    query: str,
    consumer_scope: str,
    skill: str | None = None,
    primitives_json: str | None = None,
    budget: int = 400,
) -> str:
    """Execute a retrieval skill primitive sequence."""
    primitives = json.loads(primitives_json) if primitives_json else None
    return json.dumps(
        get_store().run_retrieval_skill(
            query,
            consumer_scope=consumer_scope,
            skill=skill,
            primitives=primitives,
            budget=budget,
        )
    )


@mcp.tool()
def stele_support_score(pending_json: str, context: str = "") -> str:
    """ConsistencyGate lexical support score."""
    pending = json.loads(pending_json)
    return json.dumps(get_store().support_score(pending, context=context))


@mcp.tool()
def stele_consistency_admit(
    pending_json: str, context: str = "", tau: float = 0.35
) -> str:
    """ConsistencyGate write-time admission."""
    pending = json.loads(pending_json)
    return json.dumps(
        get_store().consistency_admit(pending, context=context, tau=tau)
    )


@mcp.tool()
def stele_retrieval_admit(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    min_overlap: float = 0.15,
) -> str:
    """MemGate query-conditioned retrieval admission."""
    return json.dumps(
        get_store().retrieval_admit(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            min_overlap=min_overlap,
        )
    )


@mcp.tool()
def stele_task_conditioned_pack(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    min_overlap: float = 0.15,
) -> str:
    """MemGate admit + pack under budget."""
    return json.dumps(
        get_store().task_conditioned_pack(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            min_overlap=min_overlap,
        )
    )


@mcp.tool()
def stele_sovereignty_checklist() -> str:
    """Mnemonic sovereignty nine-primitive checklist."""
    return json.dumps(get_store().sovereignty_checklist())


@mcp.tool()
def stele_post_delete_verify(
    deleted_ids_json: str,
    consumer_scope: str | None = None,
    probe_query: str = "",
) -> str:
    """Verify deleted IDs absent from store/Select."""
    ids = json.loads(deleted_ids_json)
    return json.dumps(
        get_store().post_delete_verify(
            ids, consumer_scope=consumer_scope, probe_query=probe_query
        )
    )


@mcp.tool()
def stele_rollback_plan(
    target_ids_json: str, reason: str = "operator_rollback"
) -> str:
    """Report-only rollback plan."""
    ids = json.loads(target_ids_json)
    return json.dumps(get_store().rollback_plan(ids, reason=reason))


@mcp.tool()
def stele_density_fuse(tunnels_json: str, limit: int = 10) -> str:
    """SodaMem multi-tunnel density fusion."""
    tunnels = json.loads(tunnels_json)
    return json.dumps(get_store().density_fuse(tunnels, limit=limit))


@mcp.tool()
def stele_evidence_plan(query: str, limit: int = 8) -> str:
    """SodaMem planner evidence ID gather + fuse."""
    return json.dumps(get_store().evidence_plan(query, limit=limit))


@mcp.tool()
def stele_cited_pack(
    query: str, evidence_ids_json: str, budget: int = 400
) -> str:
    """SodaMem reader pack with mandatory citations."""
    ids = json.loads(evidence_ids_json)
    return json.dumps(
        get_store().cited_pack(query, ids, budget=budget)
    )


@mcp.tool()
def stele_compress_candidates(
    min_similarity: float = 0.45, limit: int = 40
) -> str:
    """MemRefine near-duplicate pair proposals."""
    return json.dumps(
        get_store().compress_candidates(
            min_similarity=min_similarity, limit=limit
        )
    )


@mcp.tool()
def stele_refine_plan(
    target_count: int, min_similarity: float = 0.45
) -> str:
    """MemRefine storage-budget compression plan (report-only)."""
    return json.dumps(
        get_store().refine_plan(
            target_count=target_count, min_similarity=min_similarity
        )
    )


@mcp.tool()
def stele_merge_link_add(entry_json: str) -> str:
    """AriadneMem merge | link | add decision."""
    entry = json.loads(entry_json)
    return json.dumps(get_store().merge_link_add(entry))


@mcp.tool()
def stele_bridge_discover(
    seed_ids_json: str, max_depth: int = 3, limit: int = 20
) -> str:
    """AriadneMem LINK-path bridge discovery."""
    ids = json.loads(seed_ids_json)
    return json.dumps(
        get_store().bridge_discover(ids, max_depth=max_depth, limit=limit)
    )


@mcp.tool()
def stele_fuse_cluster(
    entry_ids_json: str, label: str | None = None
) -> str:
    """MemFuse-shaped cluster over atomic evidence ids."""
    ids = json.loads(entry_ids_json)
    return json.dumps(get_store().fuse_cluster(ids, label=label))


@mcp.tool()
def stele_result_digest(payload_json: str) -> str:
    """TGMS content-addressed result digest."""
    payload = json.loads(payload_json)
    return json.dumps(get_store().result_digest(payload))


@mcp.tool()
def stele_operator_cost_estimate(
    steps_json: str, max_cost: int = 40
) -> str:
    """TGMS pre-execution cost guard."""
    steps = json.loads(steps_json)
    return json.dumps(
        get_store().operator_cost_estimate(steps, max_cost=max_cost)
    )


@mcp.tool()
def stele_plan_static_verify(
    plan_json: str,
    task_ids_json: str | None = None,
    max_cost: int = 40,
) -> str:
    """TGMS static plan verifier."""
    plan = json.loads(plan_json)
    task_ids = json.loads(task_ids_json) if task_ids_json else None
    return json.dumps(
        get_store().plan_static_verify(
            plan, task_ids=task_ids, max_cost=max_cost
        )
    )


@mcp.tool()
def stele_claim_verify(claims_json: str, trace_json: str) -> str:
    """TGMS claim verifier against execution trace."""
    claims = json.loads(claims_json)
    trace = json.loads(trace_json)
    return json.dumps(get_store().claim_verify(claims, trace))


@mcp.tool()
def stele_summary_quarantine_scan(
    summaries_json: str, corrections_json: str
) -> str:
    """TGMS quarantine summaries overlapping corrections."""
    summaries = json.loads(summaries_json)
    corrections = json.loads(corrections_json)
    return json.dumps(
        get_store().summary_quarantine_scan(summaries, corrections)
    )


@mcp.tool()
def stele_localized_maintenance_plan(
    seed_ids_json: str, radius: int = 1, max_touch: int = 20
) -> str:
    """MemoryData O7 localized maintenance plan."""
    ids = json.loads(seed_ids_json)
    return json.dumps(
        get_store().localized_maintenance_plan(
            ids, radius=radius, max_touch=max_touch
        )
    )


@mcp.tool()
def stele_maintenance_cost_compare(
    local_touch: int, store_size: int | None = None
) -> str:
    """Compare local vs global reorganize cost proxies."""
    return json.dumps(
        get_store().maintenance_cost_compare(
            local_touch, store_size=store_size
        )
    )


@mcp.tool()
def stele_origin_bind(pending_json: str, channel_origin: str) -> str:
    """TMA-NM write-time origin binding."""
    pending = json.loads(pending_json)
    return json.dumps(
        get_store().origin_bind(pending, channel_origin=channel_origin)
    )


@mcp.tool()
def stele_propagate_origin(derived_json: str, source_ids_json: str) -> str:
    """TMA-NM non-malleable origin propagation."""
    derived = json.loads(derived_json)
    ids = json.loads(source_ids_json)
    return json.dumps(get_store().propagate_origin(derived, ids))


@mcp.tool()
def stele_launder_scan(limit: int = 40) -> str:
    """TMA-NM laundering-channel scan."""
    return json.dumps(get_store().launder_scan(limit=limit))


@mcp.tool()
def stele_act_authority_gate(
    value: str,
    driver_ids_json: str,
    trusted_principals_json: str | None = None,
    user_auth: bool = False,
    min_principals: int = 2,
) -> str:
    """TMA-NM consequential-act authority gate."""
    ids = json.loads(driver_ids_json)
    principals = (
        json.loads(trusted_principals_json)
        if trusted_principals_json
        else None
    )
    return json.dumps(
        get_store().act_authority_gate(
            value,
            ids,
            trusted_principals=principals,
            user_auth=user_auth,
            min_principals=min_principals,
        )
    )


@mcp.tool()
def stele_save_policy(
    pending_json: str,
    level: str = "standard",
    channel_origin: str = "untrusted_external",
) -> str:
    """AM-Sentry memory-saving policy."""
    pending = json.loads(pending_json)
    return json.dumps(
        get_store().save_policy(
            pending, level=level, channel_origin=channel_origin
        )
    )


@mcp.tool()
def stele_retrieval_screen(
    query: str,
    consumer_scope: str,
    budget: int = 400,
) -> str:
    """AM-Sentry retrieval screen over Select hits."""
    return json.dumps(
        get_store().retrieval_screen(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_build_memtree(scope: str | None = None) -> str:
    """MemForest MemTree hierarchical temporal index."""
    return json.dumps(get_store().build_memtree(scope=scope))


@mcp.tool()
def stele_dirty_path_plan(
    entry_json: str, scope: str | None = None
) -> str:
    """MemForest localized dirty-path update plan."""
    entry = json.loads(entry_json)
    return json.dumps(get_store().dirty_path_plan(entry, scope=scope))


@mcp.tool()
def stele_coarse_to_fine(
    query: str, scope: str | None = None, limit: int = 8
) -> str:
    """MemForest coarse-to-fine retrieval."""
    return json.dumps(
        get_store().coarse_to_fine(query, scope=scope, limit=limit)
    )


@mcp.tool()
def stele_build_themes(scope: str | None = None) -> str:
    """xMemory theme bootstrap."""
    return json.dumps(get_store().build_themes(scope=scope))


@mcp.tool()
def stele_theme_attach(
    entry_json: str, scope: str | None = None
) -> str:
    """xMemory attach-or-create theme."""
    entry = json.loads(entry_json)
    return json.dumps(get_store().theme_attach(entry, scope=scope))


@mcp.tool()
def stele_split_merge_plan(
    scope: str | None = None, max_size: int = 6, min_size: int = 2
) -> str:
    """xMemory theme split/merge plan."""
    return json.dumps(
        get_store().split_merge_plan(
            scope=scope, max_size=max_size, min_size=min_size
        )
    )


@mcp.tool()
def stele_top_down_pack(
    query: str,
    scope: str | None = None,
    budget: int = 200,
) -> str:
    """xMemory top-down theme→leaf pack."""
    return json.dumps(
        get_store().top_down_pack(query, scope=scope, budget=budget)
    )


@mcp.tool()
def stele_persistence_probe(poison_ids_json: str) -> str:
    """MemSecBench Write-stage persistence probe."""
    ids = json.loads(poison_ids_json)
    return json.dumps(get_store().persistence_probe(ids))


@mcp.tool()
def stele_execute_chain_probe(
    poison_ids_json: str,
    consumer_scope: str,
    probe_query: str = "",
    action_value: str = "",
) -> str:
    """MemSecBench Execute-stage Recall/Adopt/Act probe."""
    ids = json.loads(poison_ids_json)
    return json.dumps(
        get_store().execute_chain_probe(
            ids,
            consumer_scope=consumer_scope,
            probe_query=probe_query,
            action_value=action_value,
        )
    )


@mcp.tool()
def stele_lifecycle_report(
    poison_ids_json: str,
    consumer_scope: str,
    preserve_ids_json: str | None = None,
    probe_query: str = "",
    action_value: str = "",
) -> str:
    """MemSecBench Write–Execute–Forget lifecycle."""
    ids = json.loads(poison_ids_json)
    preserve = (
        json.loads(preserve_ids_json) if preserve_ids_json else None
    )
    return json.dumps(
        get_store().lifecycle_report(
            ids,
            consumer_scope=consumer_scope,
            preserve_ids=preserve,
            probe_query=probe_query,
            action_value=action_value,
        )
    )


@mcp.tool()
def stele_selective_repair_plan(
    poison_ids_json: str, preserve_ids_json: str | None = None
) -> str:
    """MemSecBench selective repair plan."""
    ids = json.loads(poison_ids_json)
    preserve = (
        json.loads(preserve_ids_json) if preserve_ids_json else None
    )
    return json.dumps(
        get_store().selective_repair_plan(ids, preserve_ids=preserve)
    )


@mcp.tool()
def stele_conflict_tag(conflict_key: str | None = None) -> str:
    """SleepGate supersession tags."""
    return json.dumps(get_store().conflict_tag(conflict_key=conflict_key))


@mcp.tool()
def stele_forget_gate_plan(conflict_key: str | None = None) -> str:
    """SleepGate PI forget/compress plan."""
    return json.dumps(
        get_store().forget_gate_plan(conflict_key=conflict_key)
    )


@mcp.tool()
def stele_consolidate_survivors(conflict_key: str) -> str:
    """SleepGate survivor consolidation summary."""
    return json.dumps(get_store().consolidate_survivors(conflict_key))


@mcp.tool()
def stele_pi_depth_scan(conflict_key: str) -> str:
    """SleepGate proactive-interference depth."""
    return json.dumps(get_store().pi_depth_scan(conflict_key))


@mcp.tool()
def stele_consensus_admit(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    min_channels: int = 2,
) -> str:
    """A-MemGuard multi-channel consensus admit."""
    return json.dumps(
        get_store().consensus_admit(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            min_channels=min_channels,
        )
    )


@mcp.tool()
def stele_build_mem_action_graph(actions_json: str | None = None) -> str:
    """Dependency repair: build memory↔action graph."""
    actions = json.loads(actions_json) if actions_json else None
    return json.dumps(get_store().build_mem_action_graph(actions=actions))


@mcp.tool()
def stele_dependency_trace(fault_ids_json: str, max_depth: int = 8) -> str:
    """Downstream descendants of faulty memories."""
    ids = json.loads(fault_ids_json)
    return json.dumps(
        get_store().dependency_trace(ids, max_depth=max_depth)
    )


@mcp.tool()
def stele_preserve_independent(
    fault_ids_json: str,
    trusted_sources_json: str | None = None,
    max_depth: int = 8,
) -> str:
    """Preserve cascade nodes with independent trusted support."""
    ids = json.loads(fault_ids_json)
    trusted = (
        json.loads(trusted_sources_json) if trusted_sources_json else None
    )
    return json.dumps(
        get_store().preserve_independent(
            ids, trusted_sources=trusted, max_depth=max_depth
        )
    )


@mcp.tool()
def stele_selective_replay_plan(
    fault_ids_json: str,
    trusted_sources_json: str | None = None,
    actions_json: str | None = None,
    max_depth: int = 8,
) -> str:
    """Dependency-guided selective replay plan (report-only)."""
    ids = json.loads(fault_ids_json)
    trusted = (
        json.loads(trusted_sources_json) if trusted_sources_json else None
    )
    actions = json.loads(actions_json) if actions_json else None
    return json.dumps(
        get_store().selective_replay_plan(
            ids,
            trusted_sources=trusted,
            actions=actions,
            max_depth=max_depth,
        )
    )


@mcp.tool()
def stele_classify_write_channel(entry_id: str) -> str:
    """MPBench write-channel taxonomy for one entry."""
    return json.dumps(get_store().classify_write_channel(entry_id))


@mcp.tool()
def stele_source_isolation_gate(
    entry_id: str | None = None,
    candidate_json: str | None = None,
    deny_channels_json: str | None = None,
    quarantine_channels_json: str | None = None,
) -> str:
    """MPBench source isolation admit/quarantine/reject."""
    candidate = json.loads(candidate_json) if candidate_json else None
    deny = json.loads(deny_channels_json) if deny_channels_json else None
    quar = (
        json.loads(quarantine_channels_json)
        if quarantine_channels_json
        else None
    )
    return json.dumps(
        get_store().source_isolation_gate(
            entry_id,
            candidate=candidate,
            deny_channels=deny,
            quarantine_channels=quar,
        )
    )


@mcp.tool()
def stele_write_channel_inventory() -> str:
    """MPBench inventory of write channels."""
    return json.dumps(get_store().write_channel_inventory())


@mcp.tool()
def stele_channel_admit_batch(
    candidates_json: str,
    deny_channels_json: str | None = None,
    quarantine_channels_json: str | None = None,
) -> str:
    """Batch MPBench source isolation over candidates."""
    cands = json.loads(candidates_json)
    deny = json.loads(deny_channels_json) if deny_channels_json else None
    quar = (
        json.loads(quarantine_channels_json)
        if quarantine_channels_json
        else None
    )
    return json.dumps(
        get_store().channel_admit_batch(
            cands, deny_channels=deny, quarantine_channels=quar
        )
    )


@mcp.tool()
def stele_slot_coverage(entry_id: str) -> str:
    """MemPoison/Salami semantic slot coverage."""
    return json.dumps(get_store().slot_coverage(entry_id))


@mcp.tool()
def stele_threat_tier_classify(entry_id: str) -> str:
    """MemPoison L1/L2/L3 threat tier."""
    return json.dumps(get_store().threat_tier_classify(entry_id))


@mcp.tool()
def stele_dormant_trigger_scan(limit: int = 50) -> str:
    """Scan for L3 dormant trigger-conditioned entries."""
    return json.dumps(get_store().dormant_trigger_scan(limit=limit))


@mcp.tool()
def stele_compositional_coalition_scan(
    min_slots: int = 3,
    max_coalition: int = 4,
    limit: int = 20,
) -> str:
    """Salami compositional coalitions across the store."""
    return json.dumps(
        get_store().compositional_coalition_scan(
            min_slots=min_slots,
            max_coalition=max_coalition,
            limit=limit,
        )
    )


@mcp.tool()
def stele_collusion_risk_gate(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    min_slots: int = 3,
) -> str:
    """Retrieval-time Salami collusion gate."""
    return json.dumps(
        get_store().collusion_risk_gate(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            min_slots=min_slots,
        )
    )


@mcp.tool()
def stele_mempoison_ladder_report(limit: int = 100) -> str:
    """Inventory store by MemPoison L1/L2/L3."""
    return json.dumps(get_store().mempoison_ladder_report(limit=limit))


@mcp.tool()
def stele_salami_pair_probe(entry_id_a: str, entry_id_b: str) -> str:
    """Two-fragment Salami collusion probe."""
    return json.dumps(
        get_store().salami_pair_probe(entry_id_a, entry_id_b)
    )


@mcp.tool()
def stele_classify_persistence_layer(
    entry_id: str, override: str | None = None
) -> str:
    """Knowledge/Memory/Wisdom/Intelligence persistence layer."""
    return json.dumps(
        get_store().classify_persistence_layer(entry_id, override=override)
    )


@mcp.tool()
def stele_persistence_policy(layer: str) -> str:
    """Policy card for one persistence layer."""
    return json.dumps(get_store().persistence_policy(layer))


@mcp.tool()
def stele_layer_inventory() -> str:
    """Count entries by persistence layer."""
    return json.dumps(get_store().layer_inventory())


@mcp.tool()
def stele_knowledge_protect_scan(
    faded_ids_json: str | None = None, limit: int = 50
) -> str:
    """Flag knowledge-layer entries that must not age-fade."""
    faded = json.loads(faded_ids_json) if faded_ids_json else None
    return json.dumps(
        get_store().knowledge_protect_scan(faded_ids=faded, limit=limit)
    )


@mcp.tool()
def stele_intelligence_reject_gate(
    entry_id: str | None = None, candidate_json: str | None = None
) -> str:
    """Reject ephemeral intelligence from persistence."""
    candidate = json.loads(candidate_json) if candidate_json else None
    return json.dumps(
        get_store().intelligence_reject_gate(
            entry_id=entry_id, candidate=candidate
        )
    )


@mcp.tool()
def stele_credential_scan(entry_id: str) -> str:
    """Scan one entry for credential patterns."""
    return json.dumps(get_store().credential_scan(entry_id))


@mcp.tool()
def stele_credential_reject_gate(
    entry_id: str | None = None, candidate_json: str | None = None
) -> str:
    """MAPLE-shaped write Reject for credentials."""
    candidate = json.loads(candidate_json) if candidate_json else None
    return json.dumps(
        get_store().credential_reject_gate(
            entry_id=entry_id, candidate=candidate
        )
    )


@mcp.tool()
def stele_credential_store_scan(limit: int = 50) -> str:
    """Inventory credentials still in the store."""
    return json.dumps(get_store().credential_store_scan(limit=limit))


@mcp.tool()
def stele_uncertainty_score(
    query: str, consumer_scope: str, budget: int = 400
) -> str:
    """Oblivion-shaped uncertainty over SEARCH hits."""
    return json.dumps(
        get_store().uncertainty_score(
            query, consumer_scope=consumer_scope, budget=budget
        )
    )


@mcp.tool()
def stele_uncertainty_retrieve_gate(
    query: str,
    consumer_scope: str,
    budget: int = 400,
    force: bool = False,
    uncertainty_threshold: float = 0.55,
) -> str:
    """Retrieve only when uncertainty is high."""
    return json.dumps(
        get_store().uncertainty_retrieve_gate(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            force=force,
            uncertainty_threshold=uncertainty_threshold,
        )
    )


@mcp.tool()
def stele_reasoning_reserve_plan(budget: int, confidence: float) -> str:
    """Adaptive reasoning vs recall budget split."""
    return json.dumps(
        get_store().reasoning_reserve_plan(budget, confidence=confidence)
    )


@mcp.tool()
def stele_classify_memory_component(entry_id: str) -> str:
    """PAM E/S/P/W/I memory component."""
    return json.dumps(get_store().classify_memory_component(entry_id))


@mcp.tool()
def stele_build_merkle_dag() -> str:
    """PAM Merkle-DAG over store entries."""
    return json.dumps(get_store().build_merkle_dag())


@mcp.tool()
def stele_verify_merkle_root(expected_root: str) -> str:
    """Verify store Merkle root."""
    return json.dumps(get_store().verify_merkle_root(expected_root))


@mcp.tool()
def stele_issue_capability_token(
    entry_ids_json: str,
    ops_json: str,
    audience: str,
    expires_at: str,
    components_json: str | None = None,
) -> str:
    """Issue PAM capability token."""
    comps = json.loads(components_json) if components_json else None
    return json.dumps(
        get_store().issue_capability_token(
            entry_ids=json.loads(entry_ids_json),
            ops=json.loads(ops_json),
            audience=audience,
            expires_at=expires_at,
            components=comps,
        )
    )


@mcp.tool()
def stele_check_capability(
    token: str,
    payload_json: str,
    op: str,
    entry_id: str | None = None,
) -> str:
    """Check PAM capability token."""
    return json.dumps(
        get_store().check_capability(
            token, json.loads(payload_json), op=op, entry_id=entry_id
        )
    )


@mcp.tool()
def stele_selective_disclose(
    entry_ids_json: str, include_ancestors: bool = True
) -> str:
    """PAM selective disclosure."""
    return json.dumps(
        get_store().selective_disclose(
            json.loads(entry_ids_json),
            include_ancestors=include_ancestors,
        )
    )


@mcp.tool()
def stele_rehydrate_safe_plan(entry_ids_json: str | None = None) -> str:
    """PAM injection-resistant rehydrate plan."""
    ids = json.loads(entry_ids_json) if entry_ids_json else None
    return json.dumps(get_store().rehydrate_safe_plan(ids))


@mcp.tool()
def stele_issue_action_capability(
    intent: str,
    method: str,
    host: str,
    session_id: str,
    expires_at: str,
    max_calls: int = 1,
) -> str:
    """CapSeal non-exportable action capability."""
    return json.dumps(
        get_store().issue_action_capability(
            intent=intent,
            method=method,
            host=host,
            session_id=session_id,
            max_calls=max_calls,
            expires_at=expires_at,
        )
    )


@mcp.tool()
def stele_capability_export_probe(handle: str, payload_json: str) -> str:
    """CapSeal export probe (always deny)."""
    return json.dumps(
        get_store().capability_export_probe(handle, json.loads(payload_json))
    )


@mcp.tool()
def stele_check_action_capability(
    handle: str,
    payload_json: str,
    method: str,
    host: str,
    session_id: str,
    call_count: int = 0,
) -> str:
    """Authorize CapSeal mediated invocation."""
    return json.dumps(
        get_store().check_action_capability(
            handle,
            json.loads(payload_json),
            method=method,
            host=host,
            session_id=session_id,
            call_count=call_count,
        )
    )


@mcp.tool()
def stele_action_capability_inventory(capabilities_json: str) -> str:
    """Summarize CapSeal capabilities."""
    return json.dumps(
        get_store().action_capability_inventory(json.loads(capabilities_json))
    )


@mcp.tool()
def stele_classify_risk_source(step_json: str) -> str:
    """AgentDoG risk-source (where) axis."""
    return json.dumps(get_store().classify_risk_source(json.loads(step_json)))


@mcp.tool()
def stele_classify_failure_mode(step_json: str) -> str:
    """AgentDoG failure-mode (how) axis."""
    return json.dumps(get_store().classify_failure_mode(json.loads(step_json)))


@mcp.tool()
def stele_classify_real_world_harm(step_json: str) -> str:
    """AgentDoG real-world harm (what) axis."""
    return json.dumps(get_store().classify_real_world_harm(json.loads(step_json)))


@mcp.tool()
def stele_diagnose_trajectory_step(step_json: str) -> str:
    """Fine-grained 3D diagnosis for one trajectory step."""
    return json.dumps(get_store().diagnose_trajectory_step(json.loads(step_json)))


@mcp.tool()
def stele_diagnose_trajectory(steps_json: str) -> str:
    """Trajectory-level AgentDoG diagnosis."""
    return json.dumps(get_store().diagnose_trajectory(json.loads(steps_json)))


@mcp.tool()
def stele_safe_but_unreasonable_scan(steps_json: str) -> str:
    """Surface seemingly safe but unreasonable steps."""
    return json.dumps(
        get_store().safe_but_unreasonable_scan(json.loads(steps_json))
    )


@mcp.tool()
def stele_taxonomy_inventory() -> str:
    """AgentDoG taxonomy inventory."""
    return json.dumps(get_store().taxonomy_inventory())


@mcp.tool()
def stele_weave_layer_assign(entry_id: str) -> str:
    """MemWeaver GM/ExpM/PM layer for one entry."""
    return json.dumps(get_store().weave_layer_assign(entry_id))


@mcp.tool()
def stele_build_hybrid_weave() -> str:
    """MemWeaver tri-layer weave."""
    return json.dumps(get_store().build_hybrid_weave())


@mcp.tool()
def stele_dual_channel_retrieve(
    query: str, k_r: int = 6, k_p: int = 6, k_e: int = 6
) -> str:
    """MemWeaver dual-channel retrieve."""
    return json.dumps(
        get_store().dual_channel_retrieve(query, k_r=k_r, k_p=k_p, k_e=k_e)
    )


@mcp.tool()
def stele_experience_abstract_plan(min_support: int = 2) -> str:
    """MemWeaver experience abstraction plan (report-only)."""
    return json.dumps(get_store().experience_abstract_plan(min_support=min_support))


@mcp.tool()
def stele_temporal_session_conflict_scan() -> str:
    """MemWeaver temporal session conflict scan."""
    return json.dumps(get_store().temporal_session_conflict_scan())


@mcp.tool()
def stele_multi_hop_depth_score(path_ids_json: str) -> str:
    """MemHop-shaped hop depth over an entry path."""
    return json.dumps(
        get_store().multi_hop_depth_score(json.loads(path_ids_json))
    )


@mcp.tool()
def stele_list_design_space() -> str:
    """MemEvolve/EvolveLab design space catalog."""
    return json.dumps(get_store().list_design_space())


@mcp.tool()
def stele_architecture_profile(overrides_json: str | None = None) -> str:
    """MemEvolve Ω architecture profile."""
    overrides = json.loads(overrides_json) if overrides_json else None
    return json.dumps(get_store().architecture_profile(overrides))


@mcp.tool()
def stele_diagnose_architecture(
    profile_json: str, feedback_json: str | None = None
) -> str:
    """MemEvolve defect profile D(Ω)."""
    fb = json.loads(feedback_json) if feedback_json else None
    return json.dumps(
        get_store().diagnose_architecture(json.loads(profile_json), feedback=fb)
    )


@mcp.tool()
def stele_propose_architecture_variants(
    profile_json: str, diagnosis_json: str, s: int = 3
) -> str:
    """MemEvolve Design step variants (report-only)."""
    return json.dumps(
        get_store().propose_architecture_variants(
            json.loads(profile_json), json.loads(diagnosis_json), s=s
        )
    )


@mcp.tool()
def stele_rank_architecture_fitness(candidates_json: str) -> str:
    """Rank Ω candidates by fitness."""
    return json.dumps(
        get_store().rank_architecture_fitness(json.loads(candidates_json))
    )


@mcp.tool()
def stele_select_architecture_parents(ranked_json: str, k: int = 1) -> str:
    """Select top-K architecture parents."""
    return json.dumps(
        get_store().select_architecture_parents(json.loads(ranked_json), k=k)
    )


@mcp.tool()
def stele_ept_classify(entry_id: str) -> str:
    """MindMemOS entity–property–time classify."""
    return json.dumps(get_store().ept_classify(entry_id))


@mcp.tool()
def stele_functional_role_assign(entry_id: str) -> str:
    """MEMGUARD functional role assign."""
    return json.dumps(get_store().functional_role_assign(entry_id))


@mcp.tool()
def stele_contamination_scan() -> str:
    """MEMGUARD heterogeneous contamination scan."""
    return json.dumps(get_store().contamination_scan())


@mcp.tool()
def stele_type_route_retrieve(
    query: str, allowed_roles_json: str | None = None, budget: int = 8
) -> str:
    """MEMGUARD query-adaptive type routing."""
    roles = json.loads(allowed_roles_json) if allowed_roles_json else None
    return json.dumps(
        get_store().type_route_retrieve(
            query, allowed_roles=roles, budget=budget
        )
    )


@mcp.tool()
def stele_dreaming_consolidate_plan() -> str:
    """MindMemOS dreaming consolidate plan (report-only)."""
    return json.dumps(get_store().dreaming_consolidate_plan())


@mcp.tool()
def stele_feedback_revise_plan(
    signal: str,
    entry_ids_json: str | None = None,
    mode: str = "explicit",
) -> str:
    """MindMemOS feedback revise plan."""
    ids = json.loads(entry_ids_json) if entry_ids_json else None
    return json.dumps(
        get_store().feedback_revise_plan(
            signal=signal, entry_ids=ids, mode=mode
        )
    )


@mcp.tool()
def stele_skill_evolve_plan(
    trajectories_json: str, supervised: bool = False, min_batch: int = 2
) -> str:
    """MindSkillEvolve skill update plan."""
    return json.dumps(
        get_store().skill_evolve_plan(
            json.loads(trajectories_json),
            supervised=supervised,
            min_batch=min_batch,
        )
    )


@mcp.tool()
def stele_extract_preference_signal(text: str) -> str:
    """PAMU 5-D preference signal from text."""
    return json.dumps(get_store().extract_preference_signal(text))


@mcp.tool()
def stele_fuse_preference(sw_json: str, ema_json: str, lam: float = 0.5) -> str:
    """PAMU SW+EMA fusion."""
    return json.dumps(
        get_store().fuse_preference(
            json.loads(sw_json), json.loads(ema_json), lam=lam
        )
    )


@mcp.tool()
def stele_preference_change_detect(
    sw_json: str, ema_json: str, delta: float = 0.35
) -> str:
    """PAMU preference change detection."""
    return json.dumps(
        get_store().preference_change_detect(
            json.loads(sw_json), json.loads(ema_json), delta=delta
        )
    )


@mcp.tool()
def stele_preference_update_plan(
    observations_json: str,
    window: int = 3,
    beta: float = 0.8,
    lam: float = 0.5,
    delta: float = 0.35,
) -> str:
    """PAMU preference update plan (report-only)."""
    return json.dumps(
        get_store().preference_update_plan(
            json.loads(observations_json),
            window=window,
            beta=beta,
            lam=lam,
            delta=delta,
        )
    )


@mcp.tool()
def stele_format_preference_prompt(fused_json: str) -> str:
    """PAMU NL preference prompt."""
    return json.dumps(
        get_store().format_preference_prompt(json.loads(fused_json))
    )


@mcp.tool()
def stele_beam_category_inventory() -> str:
    """BEAM ten-category inventory."""
    return json.dumps(get_store().beam_category_inventory())


@mcp.tool()
def stele_classify_beam_query(query: str) -> str:
    """Classify query into a BEAM category."""
    return json.dumps(get_store().classify_beam_query(query))


@mcp.tool()
def stele_knowledge_update_check(prior: str, current: str) -> str:
    """BEAM knowledge-update check."""
    return json.dumps(
        get_store().knowledge_update_check(prior=prior, current=current)
    )


@mcp.tool()
def stele_abstention_gate(
    query: str, evidence_count: int, min_evidence: int = 1
) -> str:
    """BEAM abstention gate."""
    return json.dumps(
        get_store().abstention_gate(
            query=query,
            evidence_count=evidence_count,
            min_evidence=min_evidence,
        )
    )


@mcp.tool()
def stele_contradiction_resolve_plan(statements_json: str) -> str:
    """BEAM contradiction resolve plan."""
    return json.dumps(
        get_store().contradiction_resolve_plan(json.loads(statements_json))
    )


@mcp.tool()
def stele_event_order_check(events_json: str) -> str:
    """BEAM event-order check."""
    return json.dumps(get_store().event_order_check(json.loads(events_json)))


@mcp.tool()
def stele_localize_hallucination_stage(
    symptom: str, context_json: str | None = None
) -> str:
    """HaluMem operation-stage localization."""
    ctx = json.loads(context_json) if context_json else None
    return json.dumps(
        get_store().localize_hallucination_stage(symptom=symptom, context=ctx)
    )


@mcp.tool()
def stele_beam_eval_pack(cases_json: str) -> str:
    """Local BEAM-shaped eval pack."""
    return json.dumps(get_store().beam_eval_pack(json.loads(cases_json)))


@mcp.tool()
def stele_extract_episodic_gist(entry_id: str) -> str:
    """REMem episodic gist."""
    return json.dumps(get_store().extract_episodic_gist(entry_id))


@mcp.tool()
def stele_extract_temporal_facts(entry_id: str) -> str:
    """REMem temporal facts."""
    return json.dumps(get_store().extract_temporal_facts(entry_id))


@mcp.tool()
def stele_situational_bind(entry_id: str) -> str:
    """REMem situational bind."""
    return json.dumps(get_store().situational_bind(entry_id))


@mcp.tool()
def stele_build_hybrid_episodic_graph() -> str:
    """REMem hybrid episodic graph."""
    return json.dumps(get_store().build_hybrid_episodic_graph())


@mcp.tool()
def stele_agentic_retrieve_plan(query: str, max_steps: int = 3) -> str:
    """REMem agentic retrieve plan."""
    return json.dumps(
        get_store().agentic_retrieve_plan(query, max_steps=max_steps)
    )


@mcp.tool()
def stele_ordinal_event_query(order: str = "first") -> str:
    """REMem ordinal event query."""
    return json.dumps(get_store().ordinal_event_query(order=order))


@mcp.tool()
def stele_form_memcell(entry_id: str) -> str:
    """EverMemOS form MemCell."""
    return json.dumps(get_store().form_memcell(entry_id))


@mcp.tool()
def stele_consolidate_memscenes(sim_threshold: float = 0.15) -> str:
    """EverMemOS consolidate MemScenes."""
    return json.dumps(
        get_store().consolidate_memscenes(sim_threshold=sim_threshold)
    )


@mcp.tool()
def stele_foresight_filter() -> str:
    """EverMemOS foresight filter."""
    return json.dumps(get_store().foresight_filter())


@mcp.tool()
def stele_reconstructive_recollect(
    query: str, n_scenes: int = 3, k_episodes: int = 5
) -> str:
    """EverMemOS reconstructive recollection."""
    return json.dumps(
        get_store().reconstructive_recollect(
            query, n_scenes=n_scenes, k_episodes=k_episodes
        )
    )


@mcp.tool()
def stele_profile_evolve_plan() -> str:
    """EverMemOS profile evolve plan."""
    return json.dumps(get_store().profile_evolve_plan())


@mcp.tool()
def stele_necessity_sufficiency_check(
    retrieved_count: int, min_needed: int = 1, max_sufficient: int = 10
) -> str:
    """EverMemOS necessity/sufficiency check."""
    return json.dumps(
        get_store().necessity_sufficiency_check(
            retrieved_count=retrieved_count,
            min_needed=min_needed,
            max_sufficient=max_sufficient,
        )
    )


@mcp.tool()
def stele_classify_memory_tier(entry_id: str) -> str:
    """MemoryOS STM/MTM/LPM tier for one entry."""
    return json.dumps(get_store().classify_memory_tier(entry_id))


@mcp.tool()
def stele_heat_score(
    n_visit: int = 0,
    l_interaction: int = 1,
    delta_t_seconds: float = 0.0,
    alpha: float = 1.0,
    beta: float = 0.5,
    gamma: float = 1.0,
) -> str:
    """MemoryOS segment heat score."""
    return json.dumps(
        get_store().heat_score(
            n_visit=n_visit,
            l_interaction=l_interaction,
            delta_t_seconds=delta_t_seconds,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
        )
    )


@mcp.tool()
def stele_segment_pages(theta: float = 0.15) -> str:
    """MemoryOS segmented paging."""
    return json.dumps(get_store().segment_pages(theta=theta))


@mcp.tool()
def stele_stm_to_mtm_plan(stm_page_ids: list[str], capacity: int = 5) -> str:
    """MemoryOS STM→MTM FIFO overflow plan."""
    return json.dumps(
        get_store().stm_to_mtm_plan(stm_page_ids, capacity=capacity)
    )


@mcp.tool()
def stele_mtm_evict_plan(max_segments: int = 3) -> str:
    """MemoryOS lowest-heat MTM eviction plan."""
    return json.dumps(get_store().mtm_evict_plan(max_segments=max_segments))


@mcp.tool()
def stele_promote_to_lpm_plan(tau: float = 5.0) -> str:
    """MemoryOS heat→LPM promotion plan."""
    return json.dumps(get_store().promote_to_lpm_plan(tau=tau))


@mcp.tool()
def stele_hierarchical_retrieve(
    query: str, top_m_segments: int = 2, top_k_pages: int = 3
) -> str:
    """MemoryOS STM+MTM+LPM hierarchical retrieve."""
    return json.dumps(
        get_store().hierarchical_retrieve(
            query, top_m_segments=top_m_segments, top_k_pages=top_k_pages
        )
    )


@mcp.tool()
def stele_integrate_episodic_narrative(entry_id: str) -> str:
    """NEMORI episodic narrative integration."""
    return json.dumps(get_store().integrate_episodic_narrative(entry_id))


@mcp.tool()
def stele_anticipatory_schema(cue: str) -> str:
    """NEMORI anticipatory schema from store."""
    return json.dumps(get_store().anticipatory_schema(cue))


@mcp.tool()
def stele_prediction_error_distill(actual: str, anticipated: str) -> str:
    """NEMORI prediction-error distillation."""
    return json.dumps(
        get_store().prediction_error_distill(
            actual=actual, anticipated=anticipated
        )
    )


@mcp.tool()
def stele_deserves_memory_gate(
    actual: str,
    anticipated: str,
    min_error_ratio: float = 0.25,
    min_novel: int = 3,
) -> str:
    """NEMORI admit-if-unexpected gate."""
    return json.dumps(
        get_store().deserves_memory_gate(
            actual=actual,
            anticipated=anticipated,
            min_error_ratio=min_error_ratio,
            min_novel=min_novel,
        )
    )


@mcp.tool()
def stele_distill_batch_plan(entry_ids: list[str] | None = None) -> str:
    """NEMORI batch distill plan (report-only)."""
    return json.dumps(get_store().distill_batch_plan(entry_ids))


@mcp.tool()
def stele_classify_network(entry_id: str) -> str:
    """Hindsight network classify."""
    return json.dumps(get_store().classify_network(entry_id))


@mcp.tool()
def stele_retain_plan(entry_ids: list[str] | None = None) -> str:
    """Hindsight retain plan."""
    return json.dumps(get_store().retain_plan(entry_ids))


@mcp.tool()
def stele_network_inventory() -> str:
    """Hindsight network inventory."""
    return json.dumps(get_store().network_inventory())


@mcp.tool()
def stele_recall_multi_strategy(
    query: str, token_budget: int = 400, top_k: int = 5
) -> str:
    """Hindsight multi-strategy recall."""
    return json.dumps(
        get_store().recall_multi_strategy(
            query, token_budget=token_budget, top_k=top_k
        )
    )


@mcp.tool()
def stele_opinion_reinforce(
    opinion_text: str,
    supporting: bool = True,
    prior_confidence: float = 0.5,
    step: float = 0.1,
) -> str:
    """Hindsight opinion reinforce."""
    return json.dumps(
        get_store().opinion_reinforce(
            opinion_text,
            supporting=supporting,
            prior_confidence=prior_confidence,
            step=step,
        )
    )


@mcp.tool()
def stele_reflect_plan(
    query: str,
    skepticism: int = 3,
    literalism: int = 3,
    empathy: int = 3,
    bias_strength: float = 0.5,
) -> str:
    """Hindsight reflect plan."""
    return json.dumps(
        get_store().reflect_plan(
            query,
            skepticism=skepticism,
            literalism=literalism,
            empathy=empathy,
            bias_strength=bias_strength,
        )
    )


@mcp.tool()
def stele_distill_strategy_item(entry_id: str, outcome: str = "success") -> str:
    """ReasoningBank distill strategy item."""
    return json.dumps(
        get_store().distill_strategy_item(entry_id, outcome=outcome)
    )


@mcp.tool()
def stele_failure_lesson_gate(
    success_count: int, failure_count: int, min_failure_share: float = 0.2
) -> str:
    """ReasoningBank failure-lesson gate."""
    return json.dumps(
        get_store().failure_lesson_gate(
            success_count=success_count,
            failure_count=failure_count,
            min_failure_share=min_failure_share,
        )
    )


@mcp.tool()
def stele_retrieve_strategies(
    strategies_json: str, query: str, top_k: int = 3
) -> str:
    """ReasoningBank retrieve strategies (JSON list)."""
    strategies = json.loads(strategies_json)
    return json.dumps(
        get_store().retrieve_strategies(strategies, query=query, top_k=top_k)
    )


@mcp.tool()
def stele_consolidate_strategy_plan(items_json: str) -> str:
    """ReasoningBank consolidate strategy plan (JSON list)."""
    items = json.loads(items_json)
    return json.dumps(get_store().consolidate_strategy_plan(items))


@mcp.tool()
def stele_matts_contrastive_plan(
    mode: str = "parallel", n_trajectories: int = 3, task_hint: str = ""
) -> str:
    """ReasoningBank MaTTS contrastive plan."""
    return json.dumps(
        get_store().matts_contrastive_plan(
            mode=mode, n_trajectories=n_trajectories, task_hint=task_hint
        )
    )


@mcp.tool()
def stele_init_skill_bank() -> str:
    """MemSkill initialize skill bank."""
    return json.dumps(get_store().init_skill_bank())


@mcp.tool()
def stele_span_partition(text: str, max_chars: int = 120) -> str:
    """MemSkill span partition."""
    return json.dumps(get_store().span_partition(text, max_chars=max_chars))


@mcp.tool()
def stele_select_skills(
    span_text: str, retrieved_hint: str = "", top_k: int = 2
) -> str:
    """MemSkill select skills."""
    return json.dumps(
        get_store().select_skills(
            span_text=span_text, retrieved_hint=retrieved_hint, top_k=top_k
        )
    )


@mcp.tool()
def stele_execute_skill_plan(span_text: str, top_k: int = 2) -> str:
    """MemSkill execute skill plan."""
    return json.dumps(
        get_store().execute_skill_plan(span_text=span_text, top_k=top_k)
    )


@mcp.tool()
def stele_record_hard_case(
    query: str,
    predicted: str = "",
    expected: str = "",
    performance: float = 0.0,
    fail: bool = True,
) -> str:
    """MemSkill record hard case."""
    return json.dumps(
        get_store().record_hard_case(
            query=query,
            predicted=predicted,
            expected=expected,
            performance=performance,
            fail=fail,
        )
    )


@mcp.tool()
def stele_designer_evolve_plan(hard_cases_json: str) -> str:
    """MemSkill designer evolve plan (JSON hard cases)."""
    cases = json.loads(hard_cases_json)
    return json.dumps(get_store().designer_evolve_plan(cases))


@mcp.tool()
def stele_classify_memory_op(candidate: str) -> str:
    """Memory-R1 classify ADD/UPDATE/DELETE/NOOP."""
    return json.dumps(get_store().classify_memory_op(candidate))


@mcp.tool()
def stele_noop_gate(candidate: str, min_overlap: float = 0.7) -> str:
    """Memory-R1 NOOP gate."""
    return json.dumps(
        get_store().noop_gate(candidate, min_overlap=min_overlap)
    )


@mcp.tool()
def stele_memory_op_plan(candidate: str) -> str:
    """Memory-R1 memory op plan."""
    return json.dumps(get_store().memory_op_plan(candidate))


@mcp.tool()
def stele_conflict_update_plan(old_text: str, new_text: str) -> str:
    """Memory-R1 conflict UPDATE plan."""
    return json.dumps(
        get_store().conflict_update_plan(old_text=old_text, new_text=new_text)
    )


@mcp.tool()
def stele_delete_stale_plan() -> str:
    """Memory-R1 DELETE stale plan."""
    return json.dumps(get_store().delete_stale_plan())


@mcp.tool()
def stele_classify_graph_tier(entry_id: str) -> str:
    """G-Memory classify graph tier."""
    return json.dumps(get_store().classify_graph_tier(entry_id))


@mcp.tool()
def stele_build_query_graph() -> str:
    """G-Memory build query graph."""
    return json.dumps(get_store().build_query_graph())


@mcp.tool()
def stele_upward_insight_traverse(query: str, top_k: int = 3) -> str:
    """G-Memory upward insight traverse."""
    return json.dumps(
        get_store().upward_insight_traverse(query, top_k=top_k)
    )


@mcp.tool()
def stele_downward_interaction_traverse(query: str, top_k: int = 3) -> str:
    """G-Memory downward interaction traverse."""
    return json.dumps(
        get_store().downward_interaction_traverse(query, top_k=top_k)
    )


@mcp.tool()
def stele_bidirectional_retrieve(query: str, top_k: int = 3) -> str:
    """G-Memory bi-directional retrieve."""
    return json.dumps(
        get_store().bidirectional_retrieve(query, top_k=top_k)
    )


@mcp.tool()
def stele_hierarchy_update_plan(
    query: str, status: str = "Resolved", new_insight: str = ""
) -> str:
    """G-Memory hierarchy update plan."""
    return json.dumps(
        get_store().hierarchy_update_plan(
            query=query, status=status, new_insight=new_insight
        )
    )


@mcp.tool()
def stele_meta_thinker_guidance(
    chunk: str, mode: str = "construction", evidence_hint: str = ""
) -> str:
    """MemMA Meta-Thinker guidance."""
    return json.dumps(
        get_store().meta_thinker_guidance(
            chunk, mode=mode, evidence_hint=evidence_hint
        )
    )


@mcp.tool()
def stele_answerability_check(query: str) -> str:
    """MemMA answerability check."""
    return json.dumps(get_store().answerability_check(query))


@mcp.tool()
def stele_synthesize_probe_qa(session_text: str, max_probes: int = 3) -> str:
    """MemMA synthesize probe QA."""
    return json.dumps(
        get_store().synthesize_probe_qa(session_text, max_probes=max_probes)
    )


@mcp.tool()
def stele_verify_probes(probes_json: str) -> str:
    """MemMA verify probes (JSON list)."""
    probes = json.loads(probes_json)
    return json.dumps(get_store().verify_probes(probes))


@mcp.tool()
def stele_repair_from_probes(probes_json: str, results_json: str) -> str:
    """MemMA repair from failed probes."""
    probes = json.loads(probes_json)
    results = json.loads(results_json)
    return json.dumps(get_store().repair_from_probes(probes, results))


@mcp.tool()
def stele_induce_workflow(
    task: str, steps_json: str, success: bool = True
) -> str:
    """AWM induce workflow from task + steps."""
    steps = json.loads(steps_json)
    return json.dumps(
        get_store().induce_workflow(task=task, steps=steps, success=success)
    )


@mcp.tool()
def stele_online_induce_gate(success_label: bool) -> str:
    """AWM online induce gate."""
    return json.dumps(get_store().online_induce_gate(success_label=success_label))


@mcp.tool()
def stele_workflow_memory_add_plan(
    workflow_json: str, existing_json: str = "[]"
) -> str:
    """AWM workflow memory add plan."""
    wf = json.loads(workflow_json)
    existing = json.loads(existing_json)
    return json.dumps(
        get_store().workflow_memory_add_plan(wf, existing=existing)
    )


@mcp.tool()
def stele_retrieve_workflows(
    workflows_json: str, query: str, top_k: int = 3
) -> str:
    """AWM retrieve workflows for a query."""
    workflows = json.loads(workflows_json)
    return json.dumps(
        get_store().retrieve_workflows(workflows, query=query, top_k=top_k)
    )


@mcp.tool()
def stele_workflow_step_budget(
    baseline_steps: int, workflow_step_count: int
) -> str:
    """AWM guided step-budget estimate."""
    return json.dumps(
        get_store().workflow_step_budget(
            baseline_steps=baseline_steps,
            workflow_step_count=workflow_step_count,
        )
    )


@mcp.tool()
def stele_distill_retrieval_experience(
    query: str,
    outcome: str,
    anomaly: str = "none",
    strategy_hint: str = "",
) -> str:
    """RRM distill procedural retrieval experience."""
    return json.dumps(
        get_store().distill_retrieval_experience(
            query=query,
            outcome=outcome,
            anomaly=anomaly,
            strategy_hint=strategy_hint,
        )
    )


@mcp.tool()
def stele_anomaly_trigger(
    hit_count: int = 0,
    prior_queries_json: str = "[]",
    current_query: str = "",
    rounds_used: int = 0,
    max_rounds: int = 5,
) -> str:
    """RRM retrieval anomaly trigger."""
    priors = json.loads(prior_queries_json)
    return json.dumps(
        get_store().anomaly_trigger(
            hit_count=hit_count,
            prior_queries=priors,
            current_query=current_query,
            rounds_used=rounds_used,
            max_rounds=max_rounds,
        )
    )


@mcp.tool()
def stele_query_level_guidance(
    experiences_json: str, query: str, anomaly: str = "none"
) -> str:
    """RRM query-level guidance (never answer facts)."""
    experiences = json.loads(experiences_json)
    return json.dumps(
        get_store().query_level_guidance(
            experiences, query=query, anomaly=anomaly
        )
    )


@mcp.tool()
def stele_experience_lifecycle_score(
    usage: int = 0,
    reuse_success: int = 0,
    age_days: float = 0.0,
    half_life_days: float = 30.0,
) -> str:
    """RRM experience lifecycle utility."""
    return json.dumps(
        get_store().experience_lifecycle_score(
            usage=usage,
            reuse_success=reuse_success,
            age_days=age_days,
            half_life_days=half_life_days,
        )
    )


@mcp.tool()
def stele_prune_experience_plan(
    experiences_json: str, capacity: int = 10, protect_new: int = 2
) -> str:
    """RRM prune experience plan."""
    experiences = json.loads(experiences_json)
    return json.dumps(
        get_store().prune_experience_plan(
            experiences, capacity=capacity, protect_new=protect_new
        )
    )


@mcp.tool()
def stele_isolate_factual_from_procedural(
    answer_ids_json: str, experience_ids_json: str
) -> str:
    """RRM gate: answer pack must not include experience ids."""
    answer_ids = json.loads(answer_ids_json)
    experience_ids = json.loads(experience_ids_json)
    return json.dumps(
        get_store().isolate_factual_from_procedural(
            answer_pack_ids=answer_ids, experience_ids=experience_ids
        )
    )


@mcp.tool()
def stele_multi_faceted_distill(
    scenario: str,
    outcome: str,
    steps_json: str = "[]",
    failure_reason: str = "",
    peer_success: str = "",
) -> str:
    """ReMe multi-faceted experience distill."""
    steps = json.loads(steps_json)
    return json.dumps(
        get_store().multi_faceted_distill(
            scenario=scenario,
            outcome=outcome,
            steps=steps,
            failure_reason=failure_reason,
            peer_success=peer_success,
        )
    )


@mcp.tool()
def stele_scenario_retrieve(
    pool_json: str, scenario: str, top_k: int = 3
) -> str:
    """ReMe scenario-aware retrieve."""
    pool = json.loads(pool_json)
    return json.dumps(
        get_store().scenario_retrieve(pool, scenario=scenario, top_k=top_k)
    )


@mcp.tool()
def stele_adaptive_rewrite_plan(
    experiences_json: str, new_scenario: str
) -> str:
    """ReMe adaptive rewrite plan."""
    experiences = json.loads(experiences_json)
    return json.dumps(
        get_store().adaptive_rewrite_plan(
            experiences, new_scenario=new_scenario
        )
    )


@mcp.tool()
def stele_utility_after_reuse(
    freq: int, utility: int, reuse_helped: bool
) -> str:
    """ReMe utility counter after reuse."""
    return json.dumps(
        get_store().utility_after_reuse(
            freq=freq, utility=utility, reuse_helped=reuse_helped
        )
    )


@mcp.tool()
def stele_selective_add_plan(
    candidate_json: str,
    pool_json: str = "[]",
    validated: bool = True,
) -> str:
    """ReMe selective add plan."""
    candidate = json.loads(candidate_json)
    pool = json.loads(pool_json)
    return json.dumps(
        get_store().selective_add_plan(
            candidate, pool=pool, validated=validated
        )
    )


@mcp.tool()
def stele_utility_prune_plan(
    pool_json: str, alpha: int = 3, beta: float = 0.3
) -> str:
    """ReMe utility prune plan."""
    pool = json.loads(pool_json)
    return json.dumps(
        get_store().utility_prune_plan(pool, alpha=alpha, beta=beta)
    )


@mcp.tool()
def stele_extract_cheatsheet_snippet(
    kind: str, title: str, body: str, max_chars: int = 240
) -> str:
    """DC extract compact cheatsheet snippet."""
    return json.dumps(
        get_store().extract_cheatsheet_snippet(
            kind=kind, title=title, body=body, max_chars=max_chars
        )
    )


@mcp.tool()
def stele_retrieve_cheatsheet(
    memory_json: str, query: str, top_k: int = 3
) -> str:
    """DC retrieve cheatsheet snippets."""
    memory = json.loads(memory_json)
    return json.dumps(
        get_store().retrieve_cheatsheet(memory, query=query, top_k=top_k)
    )


@mcp.tool()
def stele_curator_decide(
    proposed_useful: bool,
    existing_faulty: bool = False,
    superseded: bool = False,
) -> str:
    """DC curator decision."""
    return json.dumps(
        get_store().curator_decide(
            proposed_useful=proposed_useful,
            existing_faulty=existing_faulty,
            superseded=superseded,
        )
    )


@mcp.tool()
def stele_compact_memory_gate(
    entry_chars: int,
    max_entry_chars: int = 240,
    memory_chars: int = 0,
    max_memory_chars: int = 4000,
) -> str:
    """DC compact memory gate (forbid full-history ballooning)."""
    return json.dumps(
        get_store().compact_memory_gate(
            entry_chars=entry_chars,
            max_entry_chars=max_entry_chars,
            memory_chars=memory_chars,
            max_memory_chars=max_memory_chars,
        )
    )


@mcp.tool()
def stele_dc_rs_order_check(steps_json: str) -> str:
    """DC-RS / DC-Cu order check."""
    steps = json.loads(steps_json)
    return json.dumps(get_store().dc_rs_order_check(steps))


@mcp.tool()
def stele_experience_pool_add(
    task: str, outcome: str, trajectory_summary: str = ""
) -> str:
    """ExpeL experience pool add."""
    return json.dumps(
        get_store().experience_pool_add(
            task=task,
            outcome=outcome,
            trajectory_summary=trajectory_summary,
        )
    )


@mcp.tool()
def stele_insight_op(
    insights_json: str,
    op: str,
    text: str = "",
    insight_id: str | None = None,
) -> str:
    """ExpeL insight ADD/EDIT/UPVOTE/DOWNVOTE."""
    insights = json.loads(insights_json)
    return json.dumps(
        get_store().insight_op(
            insights, op=op, text=text, insight_id=insight_id
        )
    )


@mcp.tool()
def stele_insight_importance_gate(insights_json: str) -> str:
    """ExpeL drop insights at importance 0."""
    insights = json.loads(insights_json)
    return json.dumps(get_store().insight_importance_gate(insights))


@mcp.tool()
def stele_retrieve_insights(
    insights_json: str, query: str, top_k: int = 5
) -> str:
    """ExpeL retrieve insights."""
    insights = json.loads(insights_json)
    return json.dumps(
        get_store().retrieve_insights(insights, query=query, top_k=top_k)
    )


@mcp.tool()
def stele_retrieve_similar_successes(
    pool_json: str, task: str, top_k: int = 3
) -> str:
    """ExpeL retrieve similar successes."""
    pool = json.loads(pool_json)
    return json.dumps(
        get_store().retrieve_similar_successes(pool, task=task, top_k=top_k)
    )


@mcp.tool()
def stele_prospective_reflect(
    topic: str, segment: str, granularity: str = "turn"
) -> str:
    """RMM dialogue prospective reflection."""
    return json.dumps(
        get_store().prospective_reflect(
            topic=topic, segment=segment, granularity=granularity
        )
    )


@mcp.tool()
def stele_topic_memory_bank(memories_json: str) -> str:
    """RMM dialogue topic memory bank."""
    memories = json.loads(memories_json)
    return json.dumps(get_store().topic_memory_bank(memories))


@mcp.tool()
def stele_retrieve_topic_memories(
    memories_json: str, query: str, top_k: int = 5
) -> str:
    """RMM dialogue retrieve topic memories."""
    memories = json.loads(memories_json)
    return json.dumps(
        get_store().retrieve_topic_memories(
            memories, query=query, top_k=top_k
        )
    )


@mcp.tool()
def stele_retrospective_cite_feedback(
    cited_json: str, retrieved_json: str
) -> str:
    """RMM dialogue retrospective cite feedback."""
    cited = json.loads(cited_json)
    retrieved = json.loads(retrieved_json)
    return json.dumps(
        get_store().retrospective_cite_feedback(
            cited_ids=cited, all_retrieved_ids=retrieved
        )
    )


@mcp.tool()
def stele_rerank_memories(
    candidates_json: str, query: str, boosts_json: str = "{}"
) -> str:
    """RMM dialogue rerank memories."""
    candidates = json.loads(candidates_json)
    boosts = json.loads(boosts_json)
    return json.dumps(
        get_store().rerank_memories(
            candidates, query=query, cite_boosts=boosts
        )
    )


@mcp.tool()
def stele_retrieval_refine_plan(
    memories_json: str, cited_json: str, unused_json: str
) -> str:
    """RMM dialogue retrieval refine plan."""
    memories = json.loads(memories_json)
    cited = json.loads(cited_json)
    unused = json.loads(unused_json)
    return json.dumps(
        get_store().retrieval_refine_plan(
            memories, cited_ids=cited, unused_ids=unused
        )
    )


@mcp.tool()
def stele_collect_trajectory_label(
    task: str, outcome: str, lesson: str = ""
) -> str:
    """Trace2Skill labeled trajectory."""
    return json.dumps(
        get_store().collect_trajectory_label(
            task=task, outcome=outcome, lesson=lesson
        )
    )


@mcp.tool()
def stele_propose_trajectory_patch(
    trajectory_json: str, base_skill: str = "", analyst: str = "auto"
) -> str:
    """Trace2Skill propose patch from one trajectory."""
    trajectory = json.loads(trajectory_json)
    return json.dumps(
        get_store().propose_trajectory_patch(
            trajectory, base_skill=base_skill, analyst=analyst
        )
    )


@mcp.tool()
def stele_parallel_patch_pool(
    trajectories_json: str, base_skill: str = ""
) -> str:
    """Trace2Skill parallel patch pool."""
    trajectories = json.loads(trajectories_json)
    return json.dumps(
        get_store().parallel_patch_pool(
            trajectories, base_skill=base_skill
        )
    )


@mcp.tool()
def stele_hierarchical_merge_patches(
    patches_json: str, merge_branch: int = 4
) -> str:
    """Trace2Skill hierarchical merge patches."""
    patches = json.loads(patches_json)
    return json.dumps(
        get_store().hierarchical_merge_patches(
            patches, merge_branch=merge_branch
        )
    )


@mcp.tool()
def stele_skill_mode_gate(mode: str, has_human_skill: bool) -> str:
    """Trace2Skill deepen vs create gate."""
    return json.dumps(
        get_store().skill_mode_gate(
            mode=mode, has_human_skill=has_human_skill
        )
    )


@mcp.tool()
def stele_prefer_parallel_over_sequential(
    parallel_quality: float,
    sequential_quality: float,
    parallel_minutes: float,
    sequential_minutes: float,
) -> str:
    """Trace2Skill prefer parallel consolidation."""
    return json.dumps(
        get_store().prefer_parallel_over_sequential(
            parallel_quality=parallel_quality,
            sequential_quality=sequential_quality,
            parallel_minutes=parallel_minutes,
            sequential_minutes=sequential_minutes,
        )
    )


@mcp.tool()
def stele_streaming_task_append(
    memory_json: str,
    task: str,
    prediction: str = "",
    outcome: str = "unknown",
) -> str:
    """Evo-Memory streaming task append."""
    memory = json.loads(memory_json)
    return json.dumps(
        get_store().streaming_task_append(
            memory, task=task, prediction=prediction, outcome=outcome
        )
    )


@mcp.tool()
def stele_exprag_retrieve(
    memory_json: str, query: str, top_k: int = 3
) -> str:
    """Evo-Memory ExpRAG retrieve."""
    memory = json.loads(memory_json)
    return json.dumps(
        get_store().exprag_retrieve(memory, query=query, top_k=top_k)
    )


@mcp.tool()
def stele_search_predict_evolve_check(steps_json: str) -> str:
    """Evo-Memory search-predict-evolve check."""
    steps = json.loads(steps_json)
    return json.dumps(get_store().search_predict_evolve_check(steps))


@mcp.tool()
def stele_evomem_refine_plan(
    memory_size: int,
    max_memory: int = 50,
    retrieval_hit: bool = True,
    noisy: bool = False,
) -> str:
    """Evo-Memory ReMem-shaped refine plan."""
    return json.dumps(
        get_store().evomem_refine_plan(
            memory_size=memory_size,
            max_memory=max_memory,
            retrieval_hit=retrieval_hit,
            noisy=noisy,
        )
    )


@mcp.tool()
def stele_evolution_similarity_hint(
    query_tokens_json: str, cluster_tokens_json: str
) -> str:
    """Evo-Memory similarity / reuse-gain hint."""
    query_tokens = json.loads(query_tokens_json)
    cluster_tokens = json.loads(cluster_tokens_json)
    return json.dumps(
        get_store().evolution_similarity_hint(
            query_tokens=query_tokens, cluster_tokens=cluster_tokens
        )
    )


@mcp.tool()
def stele_classify_memory_slot(text: str, has_timestamp: bool = False) -> str:
    """Mem-α classify core/episodic/semantic."""
    return json.dumps(
        get_store().classify_memory_slot(
            text=text, has_timestamp=has_timestamp
        )
    )


@mcp.tool()
def stele_memory_write_op(
    slot: str,
    op: str,
    content: str = "",
    record_id: str | None = None,
) -> str:
    """Mem-α memory write tool validation."""
    return json.dumps(
        get_store().memory_write_op(
            slot=slot, op=op, content=content, record_id=record_id
        )
    )


@mcp.tool()
def stele_process_chunk_plan(
    chunk: str, existing_core_chars: int = 0, core_max: int = 512
) -> str:
    """Mem-α process chunk plan."""
    return json.dumps(
        get_store().process_chunk_plan(
            chunk=chunk,
            existing_core_chars=existing_core_chars,
            core_max=core_max,
        )
    )


@mcp.tool()
def stele_compression_ratio(memory_chars: int, chunk_chars: int) -> str:
    """Mem-α compression ratio r3."""
    return json.dumps(
        get_store().compression_ratio(
            memory_chars=memory_chars, chunk_chars=chunk_chars
        )
    )


@mcp.tool()
def stele_memalpha_reward_bundle(params_json: str) -> str:
    """Mem-α combined reward bundle (JSON kwargs)."""
    params = json.loads(params_json)
    return json.dumps(get_store().memalpha_reward_bundle(**params))


@mcp.tool()
def stele_length_generalization_gate(
    train_max_tokens: int, eval_tokens: int
) -> str:
    """Mem-α length generalization gate."""
    return json.dumps(
        get_store().length_generalization_gate(
            train_max_tokens=train_max_tokens, eval_tokens=eval_tokens
        )
    )


@mcp.tool()
def stele_classify_failure(
    failure_type: str,
    observation_chars: int = 0,
    severity: float | None = None,
) -> str:
    """AgentHER classify failure."""
    return json.dumps(
        get_store().classify_failure(
            failure_type=failure_type,
            observation_chars=observation_chars,
            severity=severity,
        )
    )


@mcp.tool()
def stele_extract_replay_outcome(
    observations_json: str, max_items: int = 5
) -> str:
    """AgentHER extract replay outcome."""
    observations = json.loads(observations_json)
    return json.dumps(
        get_store().extract_replay_outcome(
            observations=observations, max_items=max_items
        )
    )


@mcp.tool()
def stele_hindsight_relabel_plan(
    original_goal: str,
    achievements_json: str,
    confidence: float = 0.85,
    theta: float = 0.7,
) -> str:
    """AgentHER hindsight relabel plan."""
    achievements = json.loads(achievements_json)
    return json.dumps(
        get_store().hindsight_relabel_plan(
            original_goal=original_goal,
            achievements=achievements,
            confidence=confidence,
            theta=theta,
        )
    )


@mcp.tool()
def stele_multi_judge_accept(
    confidence_j1: float, confidence_j2: float, theta: float = 0.7
) -> str:
    """AgentHER multi-judge accept."""
    return json.dumps(
        get_store().multi_judge_accept(
            confidence_j1=confidence_j1,
            confidence_j2=confidence_j2,
            theta=theta,
        )
    )


@mcp.tool()
def stele_package_training_pair(
    format: str,
    hindsight_goal: str,
    original_goal: str,
    trajectory_summary: str = "",
    severity_weight: float = 1.0,
) -> str:
    """AgentHER package SFT/DPO/ShareGPT pair."""
    return json.dumps(
        get_store().package_training_pair(
            format=format,
            hindsight_goal=hindsight_goal,
            original_goal=original_goal,
            trajectory_summary=trajectory_summary,
            severity_weight=severity_weight,
        )
    )


@mcp.tool()
def stele_distill_planning_error(
    error_id: str,
    pattern: str,
    success_hint: str = "",
    failure_hint: str = "",
) -> str:
    """PreFlect distill planning error."""
    return json.dumps(
        get_store().distill_planning_error(
            error_id=error_id,
            pattern=pattern,
            success_hint=success_hint,
            failure_hint=failure_hint,
        )
    )


@mcp.tool()
def stele_prospective_critique_plan(
    plan_steps_json: str, planning_errors_json: str
) -> str:
    """PreFlect prospective critique plan."""
    plan_steps = json.loads(plan_steps_json)
    planning_errors = json.loads(planning_errors_json)
    return json.dumps(
        get_store().prospective_critique_plan(
            plan_steps=plan_steps, planning_errors=planning_errors
        )
    )


@mcp.tool()
def stele_revise_plan_proposal(
    original_steps_json: str,
    avoid_patterns_json: str,
    insert_guard: str = "verify precondition",
) -> str:
    """PreFlect revise plan proposal."""
    original_steps = json.loads(original_steps_json)
    avoid_patterns = json.loads(avoid_patterns_json)
    return json.dumps(
        get_store().revise_plan_proposal(
            original_steps=original_steps,
            avoid_patterns=avoid_patterns,
            insert_guard=insert_guard,
        )
    )


@mcp.tool()
def stele_replan_on_deviation(
    expected_observation: str,
    actual_observation: str,
    remaining_steps: int,
) -> str:
    """PreFlect replan on deviation."""
    return json.dumps(
        get_store().replan_on_deviation(
            expected_observation=expected_observation,
            actual_observation=actual_observation,
            remaining_steps=remaining_steps,
        )
    )


@mcp.tool()
def stele_preflect_before_execute_gate(
    critique_needs_revise: bool, revised_ready: bool
) -> str:
    """PreFlect before-execute gate."""
    return json.dumps(
        get_store().preflect_before_execute_gate(
            critique_needs_revise=critique_needs_revise,
            revised_ready=revised_ready,
        )
    )


@mcp.tool()
def stele_orchestration_action_select(
    action_type: str,
    skill_id: str | None = None,
    step: int = 0,
    tmax: int = 20,
) -> str:
    """SkillFlow orchestration action select."""
    return json.dumps(
        get_store().orchestration_action_select(
            action_type=action_type,
            skill_id=skill_id,
            step=step,
            tmax=tmax,
        )
    )


@mcp.tool()
def stele_ttb_residual(
    log_forward: float,
    log_backward: float,
    log_reward: float,
    log_z: float = 0.0,
    length: int = 1,
) -> str:
    """SkillFlow TTB residual."""
    return json.dumps(
        get_store().ttb_residual(
            log_forward=log_forward,
            log_backward=log_backward,
            log_reward=log_reward,
            log_z=log_z,
            length=length,
        )
    )


@mcp.tool()
def stele_step_importance(log_forward: float, log_backward: float) -> str:
    """SkillFlow step importance."""
    return json.dumps(
        get_store().step_importance(
            log_forward=log_forward, log_backward=log_backward
        )
    )


@mcp.tool()
def stele_skill_marginal_flow(
    skill_flows_json: str, skill_id: str, target_index: int = 0
) -> str:
    """SkillFlow skill marginal flow."""
    skill_flows = json.loads(skill_flows_json)
    return json.dumps(
        get_store().skill_marginal_flow(
            skill_flows=skill_flows,
            skill_id=skill_id,
            target_index=target_index,
        )
    )


@mcp.tool()
def stele_skill_curation_decide(
    mean_log_flow: float,
    centered_log_share: float,
    jensen_gap: float = 0.0,
    high_importance_step: bool = False,
) -> str:
    """SkillFlow skill curation decide."""
    return json.dumps(
        get_store().skill_curation_decide(
            mean_log_flow=mean_log_flow,
            centered_log_share=centered_log_share,
            jensen_gap=jensen_gap,
            high_importance_step=high_importance_step,
        )
    )


@mcp.tool()
def stele_phase_evolve_gate(
    residual_mean: float,
    residual_floor: float,
    plateau_eps: float = 0.05,
) -> str:
    """SkillFlow phase evolve gate."""
    return json.dumps(
        get_store().phase_evolve_gate(
            residual_mean=residual_mean,
            residual_floor=residual_floor,
            plateau_eps=plateau_eps,
        )
    )


@mcp.tool()
def stele_define_skill_triplet(
    skill_id: str, activation: str, execution: str, termination: str
) -> str:
    """ProcMEM define skill triplet."""
    return json.dumps(
        get_store().define_skill_triplet(
            skill_id=skill_id,
            activation=activation,
            execution=execution,
            termination=termination,
        )
    )


@mcp.tool()
def stele_skill_select_gate(
    state_text: str, activation: str, min_overlap: float = 0.25
) -> str:
    """ProcMEM skill select gate."""
    return json.dumps(
        get_store().skill_select_gate(
            state_text=state_text,
            activation=activation,
            min_overlap=min_overlap,
        )
    )


@mcp.tool()
def stele_skill_terminate_check(
    observation: str, termination: str, min_overlap: float = 0.3
) -> str:
    """ProcMEM skill terminate check."""
    return json.dumps(
        get_store().skill_terminate_check(
            observation=observation,
            termination=termination,
            min_overlap=min_overlap,
        )
    )


@mcp.tool()
def stele_semantic_gradient_candidate(
    success_trace: str, failure_trace: str, base_skill_id: str
) -> str:
    """ProcMEM semantic gradient candidate."""
    return json.dumps(
        get_store().semantic_gradient_candidate(
            success_trace=success_trace,
            failure_trace=failure_trace,
            base_skill_id=base_skill_id,
        )
    )


@mcp.tool()
def stele_ppo_gate_verify(
    candidate_score: float, incumbent_score: float, clip_eps: float = 0.2
) -> str:
    """ProcMEM PPO Gate verify."""
    return json.dumps(
        get_store().ppo_gate_verify(
            candidate_score=candidate_score,
            incumbent_score=incumbent_score,
            clip_eps=clip_eps,
        )
    )


@mcp.tool()
def stele_skill_score_maintain(
    frequency: int, avg_gain: float, min_score: float = 0.1
) -> str:
    """ProcMEM skill score maintain."""
    return json.dumps(
        get_store().skill_score_maintain(
            frequency=frequency, avg_gain=avg_gain, min_score=min_score
        )
    )


@mcp.tool()
def stele_ieu_record(
    intent: str, experience: str, utility: float = 0.0
) -> str:
    """MemRL Intent-Experience-Utility record."""
    return json.dumps(
        get_store().ieu_record(
            intent=intent, experience=experience, utility=utility
        )
    )


@mcp.tool()
def stele_two_phase_retrieve(
    query: str,
    memories_json: str,
    top_k_semantic: int = 5,
    top_k_utility: int = 2,
) -> str:
    """MemRL two-phase retrieve."""
    memories = json.loads(memories_json)
    return json.dumps(
        get_store().two_phase_retrieve(
            query=query,
            memories=memories,
            top_k_semantic=top_k_semantic,
            top_k_utility=top_k_utility,
        )
    )


@mcp.tool()
def stele_utility_q_update(
    current_q: float,
    reward: float,
    next_max_q: float = 0.0,
    alpha: float = 0.3,
    gamma: float = 0.9,
) -> str:
    """MemRL utility Q update."""
    return json.dumps(
        get_store().utility_q_update(
            current_q=current_q,
            reward=reward,
            next_max_q=next_max_q,
            alpha=alpha,
            gamma=gamma,
        )
    )


@mcp.tool()
def stele_value_aware_select(
    candidates_json: str, min_utility: float = 0.0
) -> str:
    """MemRL value-aware select."""
    candidates = json.loads(candidates_json)
    return json.dumps(
        get_store().value_aware_select(
            candidates=candidates, min_utility=min_utility
        )
    )


@mcp.tool()
def stele_semantic_vs_utility_warn(
    similarity: float,
    utility: float,
    sim_high: float = 0.7,
    util_low: float = 0.1,
) -> str:
    """MemRL similar≠useful warn."""
    return json.dumps(
        get_store().semantic_vs_utility_warn(
            similarity=similarity,
            utility=utility,
            sim_high=sim_high,
            util_low=util_low,
        )
    )


@mcp.tool()
def stele_distill_principle(
    kind: str, description: str, triples_json: str = "[]"
) -> str:
    """EvolveR distill principle."""
    triples = json.loads(triples_json)
    return json.dumps(
        get_store().distill_principle(
            kind=kind, description=description, triples=triples
        )
    )


@mcp.tool()
def stele_principle_dedupe_plan(
    candidate_desc: str,
    existing_descs_json: str,
    sim_threshold: float = 0.5,
) -> str:
    """EvolveR principle dedupe plan."""
    existing_descs = json.loads(existing_descs_json)
    return json.dumps(
        get_store().principle_dedupe_plan(
            candidate_desc=candidate_desc,
            existing_descs=existing_descs,
            sim_threshold=sim_threshold,
        )
    )


@mcp.tool()
def stele_principle_metric_score(
    succ_count: int, use_count: int, prune_threshold: float = 0.2
) -> str:
    """EvolveR principle metric score."""
    return json.dumps(
        get_store().principle_metric_score(
            succ_count=succ_count,
            use_count=use_count,
            prune_threshold=prune_threshold,
        )
    )


@mcp.tool()
def stele_search_experience_action(action: str, query: str = "") -> str:
    """EvolveR online action gate."""
    return json.dumps(
        get_store().search_experience_action(action=action, query=query)
    )


@mcp.tool()
def stele_lifecycle_phase_gate(
    phase: str, mutate_policy: bool = False, distill: bool = False
) -> str:
    """EvolveR lifecycle phase gate."""
    return json.dumps(
        get_store().lifecycle_phase_gate(
            phase=phase, mutate_policy=mutate_policy, distill=distill
        )
    )


@mcp.tool()
def stele_prune_low_score_principles(
    scores_json: str, threshold: float = 0.2
) -> str:
    """EvolveR prune low-score principles."""
    scores = json.loads(scores_json)
    return json.dumps(
        get_store().prune_low_score_principles(
            scores=scores, threshold=threshold
        )
    )


@mcp.tool()
def stele_self_question_task(
    exploration_summary: str, user_preference: str = ""
) -> str:
    """AgentEvolver self-question task."""
    return json.dumps(
        get_store().self_question_task(
            exploration_summary=exploration_summary,
            user_preference=user_preference,
        )
    )


@mcp.tool()
def stele_experience_when_content(when_to_use: str, content: str) -> str:
    """AgentEvolver experience when/content."""
    return json.dumps(
        get_store().experience_when_content(
            when_to_use=when_to_use, content=content
        )
    )


@mcp.tool()
def stele_mixed_rollout_split(total_rollouts: int, eta: float = 0.5) -> str:
    """AgentEvolver mixed rollout split."""
    return json.dumps(
        get_store().mixed_rollout_split(
            total_rollouts=total_rollouts, eta=eta
        )
    )


@mcp.tool()
def stele_attribute_step_credit(
    step_scores_json: str, outcome_reward: float
) -> str:
    """AgentEvolver attribute step credit."""
    step_scores = json.loads(step_scores_json)
    return json.dumps(
        get_store().attribute_step_credit(
            step_scores=step_scores, outcome_reward=outcome_reward
        )
    )


@mcp.tool()
def stele_curiosity_explore_plan(
    visited_states: int, novel_states: int, budget: int
) -> str:
    """AgentEvolver curiosity explore plan."""
    return json.dumps(
        get_store().curiosity_explore_plan(
            visited_states=visited_states,
            novel_states=novel_states,
            budget=budget,
        )
    )


@mcp.tool()
def stele_propose_skill(
    description: str, kind: str = "procedural", existing_json: str = "[]"
) -> str:
    """SkillWeaver propose skill."""
    existing = json.loads(existing_json)
    return json.dumps(
        get_store().propose_skill(
            description=description, kind=kind, existing=existing
        )
    )


@mcp.tool()
def stele_practice_skill_run(
    skill_id: str, success: bool, steps: int = 1
) -> str:
    """SkillWeaver practice skill run."""
    return json.dumps(
        get_store().practice_skill_run(
            skill_id=skill_id, success=success, steps=steps
        )
    )


@mcp.tool()
def stele_distill_skill_api(
    skill_id: str, description: str, params_json: str = "[]"
) -> str:
    """SkillWeaver distill skill API."""
    params = json.loads(params_json)
    return json.dumps(
        get_store().distill_skill_api(
            skill_id=skill_id, description=description, params=params
        )
    )


@mcp.tool()
def stele_hone_skill_api(
    unit_test_pass: bool, static_ok: bool = True
) -> str:
    """SkillWeaver hone skill API."""
    return json.dumps(
        get_store().hone_skill_api(
            unit_test_pass=unit_test_pass, static_ok=static_ok
        )
    )


@mcp.tool()
def stele_skill_library_register(api_name: str, library_size: int) -> str:
    """SkillWeaver skill library register."""
    return json.dumps(
        get_store().skill_library_register(
            api_name=api_name, library_size=library_size
        )
    )


@mcp.tool()
def stele_transfer_skill_gate(
    donor_success_rate: float, recipient_baseline: float
) -> str:
    """SkillWeaver transfer skill gate."""
    return json.dumps(
        get_store().transfer_skill_gate(
            donor_success_rate=donor_success_rate,
            recipient_baseline=recipient_baseline,
        )
    )


@mcp.tool()
def stele_decompose_task_steps(query: str, max_steps: int = 6) -> str:
    """SkillRoute decompose task steps."""
    return json.dumps(
        get_store().decompose_task_steps(query=query, max_steps=max_steps)
    )


@mcp.tool()
def stele_retrieve_skills_for_steps(
    steps_json: str, skill_catalog_json: str, top_m: int = 2
) -> str:
    """SkillRoute retrieve skills for steps."""
    steps = json.loads(steps_json)
    skill_catalog = json.loads(skill_catalog_json)
    return json.dumps(
        get_store().retrieve_skills_for_steps(
            steps=steps, skill_catalog=skill_catalog, top_m=top_m
        )
    )


@mcp.tool()
def stele_compose_skill_dag(step_skills_json: str) -> str:
    """SkillRoute compose skill DAG."""
    step_skills = json.loads(step_skills_json)
    return json.dumps(
        get_store().compose_skill_dag(step_skills=step_skills)
    )


@mcp.tool()
def stele_sad_feedback_loop(
    prior_steps_json: str, hint_skill_names_json: str
) -> str:
    """SkillRoute SAD feedback loop."""
    prior_steps = json.loads(prior_steps_json)
    hint_skill_names = json.loads(hint_skill_names_json)
    return json.dumps(
        get_store().sad_feedback_loop(
            prior_steps=prior_steps, hint_skill_names=hint_skill_names
        )
    )


@mcp.tool()
def stele_granularity_match_check(
    step_count: int, expected_skills: int
) -> str:
    """SkillRoute granularity match check."""
    return json.dumps(
        get_store().granularity_match_check(
            step_count=step_count, expected_skills=expected_skills
        )
    )


@mcp.tool()
def stele_propose_reasoning_task(mode: str, seed_hint: str = "") -> str:
    """Absolute Zero propose reasoning task."""
    return json.dumps(
        get_store().propose_reasoning_task(mode=mode, seed_hint=seed_hint)
    )


@mcp.tool()
def stele_validate_task_structure(
    mode: str,
    has_program: bool,
    has_input: bool,
    has_output: bool,
) -> str:
    """Absolute Zero validate task structure."""
    return json.dumps(
        get_store().validate_task_structure(
            has_program=has_program,
            has_input=has_input,
            has_output=has_output,
            mode=mode,
        )
    )


@mcp.tool()
def stele_learnability_reward(mean_solve_rate: float) -> str:
    """Absolute Zero learnability reward."""
    return json.dumps(
        get_store().learnability_reward(mean_solve_rate=mean_solve_rate)
    )


@mcp.tool()
def stele_solve_reward(answer_match: bool) -> str:
    """Absolute Zero solve reward."""
    return json.dumps(get_store().solve_reward(answer_match=answer_match))


@mcp.tool()
def stele_abszero_joint_objective(
    r_propose: float, r_solve: float, lambda_propose: float = 0.5
) -> str:
    """Absolute Zero joint objective."""
    return json.dumps(
        get_store().abszero_joint_objective(
            r_propose=r_propose,
            r_solve=r_solve,
            lambda_propose=lambda_propose,
        )
    )


@mcp.tool()
def stele_executor_verify_gate(
    task_valid: bool, answer_match: bool
) -> str:
    """Absolute Zero executor verify gate."""
    return json.dumps(
        get_store().executor_verify_gate(
            task_valid=task_valid, answer_match=answer_match
        )
    )


@mcp.tool()
def stele_challenger_propose(question: str) -> str:
    """R-Zero challenger propose."""
    return json.dumps(get_store().challenger_propose(question=question))


@mcp.tool()
def stele_uncertainty_reward(empirical_accuracy: float) -> str:
    """R-Zero uncertainty reward."""
    return json.dumps(
        get_store().uncertainty_reward(
            empirical_accuracy=empirical_accuracy
        )
    )


@mcp.tool()
def stele_majority_vote_label(answers_json: str) -> str:
    """R-Zero majority vote label."""
    answers = json.loads(answers_json)
    return json.dumps(get_store().majority_vote_label(answers=answers))


@mcp.tool()
def stele_curriculum_band_filter(
    empirical_accuracy: float, delta: float = 0.2
) -> str:
    """R-Zero curriculum band filter."""
    return json.dumps(
        get_store().curriculum_band_filter(
            empirical_accuracy=empirical_accuracy, delta=delta
        )
    )


@mcp.tool()
def stele_solver_binary_reward(answer: str, pseudo_label: str) -> str:
    """R-Zero solver binary reward."""
    return json.dumps(
        get_store().solver_binary_reward(
            answer=answer, pseudo_label=pseudo_label
        )
    )


@mcp.tool()
def stele_coevolve_round_plan(
    round_index: int,
    challenger_updated: bool,
    solver_updated: bool,
) -> str:
    """R-Zero coevolve round plan."""
    return json.dumps(
        get_store().coevolve_round_plan(
            round_index=round_index,
            challenger_updated=challenger_updated,
            solver_updated=solver_updated,
        )
    )


@mcp.tool()
def stele_write_turn_memory(source_turn_id: str, finding: str) -> str:
    """ECHO write turn memory."""
    return json.dumps(
        get_store().write_turn_memory(
            source_turn_id=source_turn_id, finding=finding
        )
    )


@mcp.tool()
def stele_select_turn_memories(memory_ids_json: str, budget: int) -> str:
    """ECHO select turn memories."""
    memory_ids = json.loads(memory_ids_json)
    return json.dumps(
        get_store().select_turn_memories(
            memory_ids=memory_ids, budget=budget
        )
    )


@mcp.tool()
def stele_reconstruct_policy_context(
    findings_json: str, recent_json: str, max_chars: int = 400
) -> str:
    """ECHO reconstruct policy context."""
    findings = json.loads(findings_json)
    recent = json.loads(recent_json)
    return json.dumps(
        get_store().reconstruct_policy_context(
            selected_findings=findings,
            recent_turns=recent,
            max_chars=max_chars,
        )
    )


@mcp.tool()
def stele_provenance_credit_mask(
    sources_json: str, selected_json: str, outcome_positive: bool
) -> str:
    """ECHO provenance credit mask."""
    sources = json.loads(sources_json)
    selected = json.loads(selected_json)
    return json.dumps(
        get_store().provenance_credit_mask(
            source_turn_ids=sources,
            selected_source_ids=selected,
            outcome_positive=outcome_positive,
        )
    )


@mcp.tool()
def stele_history_collapse_gate(collapsed_summary_only: bool) -> str:
    """ECHO history collapse gate."""
    return json.dumps(
        get_store().history_collapse_gate(
            collapsed_summary_only=collapsed_summary_only
        )
    )


@mcp.tool()
def stele_budget_binding_check(
    history_chars: int, budget_chars: int
) -> str:
    """ECHO budget binding check."""
    return json.dumps(
        get_store().budget_binding_check(
            history_chars=history_chars, budget_chars=budget_chars
        )
    )


@mcp.tool()
def stele_curriculum_propose_task(
    task: str, requires_tool: bool = False
) -> str:
    """Agent0 curriculum propose task."""
    return json.dumps(
        get_store().curriculum_propose_task(
            task=task, requires_tool=requires_tool
        )
    )


@mcp.tool()
def stele_tool_use_reward(
    tool_call_count: int, gamma: float = 0.25, cap: int = 4
) -> str:
    """Agent0 tool use reward."""
    return json.dumps(
        get_store().tool_use_reward(
            tool_call_count=tool_call_count, gamma=gamma, cap=cap
        )
    )


@mcp.tool()
def stele_curriculum_reward(
    r_uncertainty: float,
    r_tool: float,
    r_repetition: float = 0.0,
    format_ok: bool = True,
) -> str:
    """Agent0 curriculum reward."""
    return json.dumps(
        get_store().curriculum_reward(
            r_uncertainty=r_uncertainty,
            r_tool=r_tool,
            r_repetition=r_repetition,
            format_ok=format_ok,
        )
    )


@mcp.tool()
def stele_executor_frontier_filter(
    self_consistency: float, low: float = 0.3, high: float = 0.8
) -> str:
    """Agent0 executor frontier filter."""
    return json.dumps(
        get_store().executor_frontier_filter(
            self_consistency=self_consistency, low=low, high=high
        )
    )


@mcp.tool()
def stele_tool_aware_pressure(
    executor_tool_success_rate: float, prior_task_complexity: float
) -> str:
    """Agent0 tool-aware curriculum pressure."""
    return json.dumps(
        get_store().tool_aware_pressure(
            executor_tool_success_rate=executor_tool_success_rate,
            prior_task_complexity=prior_task_complexity,
        )
    )


@mcp.tool()
def stele_symbiotic_round_plan(
    round_index: int,
    curriculum_updated: bool,
    executor_updated: bool,
) -> str:
    """Agent0 symbiotic round plan."""
    return json.dumps(
        get_store().symbiotic_round_plan(
            round_index=round_index,
            curriculum_updated=curriculum_updated,
            executor_updated=executor_updated,
        )
    )


@mcp.tool()
def stele_mae_propose_question(question: str) -> str:
    """MAE propose question."""
    return json.dumps(get_store().mae_propose_question(question=question))


@mcp.tool()
def stele_mae_solve_attempt(answer: str) -> str:
    """MAE solve attempt."""
    return json.dumps(get_store().mae_solve_attempt(answer=answer))


@mcp.tool()
def stele_mae_judge_score(
    quality_score: float, correctness_score: float
) -> str:
    """MAE judge score."""
    return json.dumps(
        get_store().mae_judge_score(
            quality_score=quality_score,
            correctness_score=correctness_score,
        )
    )


@mcp.tool()
def stele_mae_proposer_reward(
    quality_score: float,
    solver_failed: bool,
    difficulty_weight: float = 0.5,
) -> str:
    """MAE proposer reward."""
    return json.dumps(
        get_store().mae_proposer_reward(
            quality_score=quality_score,
            solver_failed=solver_failed,
            difficulty_weight=difficulty_weight,
        )
    )


@mcp.tool()
def stele_mae_quality_filter(
    quality_score: float, min_quality: float = 0.5
) -> str:
    """MAE quality filter."""
    return json.dumps(
        get_store().mae_quality_filter(
            quality_score=quality_score, min_quality=min_quality
        )
    )


@mcp.tool()
def stele_mae_triad_round_plan(round_index: int, phase: str) -> str:
    """MAE triad round plan."""
    return json.dumps(
        get_store().mae_triad_round_plan(
            round_index=round_index, phase=phase
        )
    )


@mcp.tool()
def stele_sage_challenge_task(task: str, difficulty: float = 0.5) -> str:
    """SAGE challenge task."""
    return json.dumps(
        get_store().sage_challenge_task(task=task, difficulty=difficulty)
    )


@mcp.tool()
def stele_sage_plan_steps(steps_json: str) -> str:
    """SAGE plan steps."""
    steps = json.loads(steps_json)
    return json.dumps(get_store().sage_plan_steps(steps=steps))


@mcp.tool()
def stele_sage_solve_with_plan(
    plan_step_count: int, followed_steps: int, answer: str
) -> str:
    """SAGE solve with plan."""
    return json.dumps(
        get_store().sage_solve_with_plan(
            plan_step_count=plan_step_count,
            followed_steps=followed_steps,
            answer=answer,
        )
    )


@mcp.tool()
def stele_sage_critic_filter(
    question_score: float, plan_score: float, min_score: float = 0.5
) -> str:
    """SAGE critic filter."""
    return json.dumps(
        get_store().sage_critic_filter(
            question_score=question_score,
            plan_score=plan_score,
            min_score=min_score,
        )
    )


@mcp.tool()
def stele_sage_drift_gate(
    difficulty_delta: float, max_delta: float = 0.3
) -> str:
    """SAGE curriculum drift gate."""
    return json.dumps(
        get_store().sage_drift_gate(
            difficulty_delta=difficulty_delta, max_delta=max_delta
        )
    )


@mcp.tool()
def stele_sage_closed_loop_round(round_index: int, phase: str) -> str:
    """SAGE closed loop round."""
    return json.dumps(
        get_store().sage_closed_loop_round(
            round_index=round_index, phase=phase
        )
    )


@mcp.tool()
def stele_memory_trigger_decide(
    at_boundary: bool, uncertainty: float, threshold: float = 0.4
) -> str:
    """MemGen memory trigger decide."""
    return json.dumps(
        get_store().memory_trigger_decide(
            at_boundary=at_boundary,
            uncertainty=uncertainty,
            threshold=threshold,
        )
    )


@mcp.tool()
def stele_weave_latent_memory(stimulus: str, token_budget: int = 4) -> str:
    """MemGen weave latent memory."""
    return json.dumps(
        get_store().weave_latent_memory(
            stimulus=stimulus, token_budget=token_budget
        )
    )


@mcp.tool()
def stele_interweave_cycle_plan(step: str) -> str:
    """MemGen interweave cycle plan."""
    return json.dumps(get_store().interweave_cycle_plan(step=step))


@mcp.tool()
def stele_faculty_classify(faculty: str) -> str:
    """MemGen faculty classify."""
    return json.dumps(get_store().faculty_classify(faculty=faculty))


@mcp.tool()
def stele_weaver_only_update_gate(
    reasoner_frozen: bool, weaver_updated: bool
) -> str:
    """MemGen weaver-only update gate."""
    return json.dumps(
        get_store().weaver_only_update_gate(
            reasoner_frozen=reasoner_frozen,
            weaver_updated=weaver_updated,
        )
    )


@mcp.tool()
def stele_sparse_invoke_penalty(
    invoke_count: int,
    expected_rate: float = 0.2,
    lambda_penalty: float = 0.1,
) -> str:
    """MemGen sparse invoke penalty."""
    return json.dumps(
        get_store().sparse_invoke_penalty(
            invoke_count=invoke_count,
            expected_rate=expected_rate,
            lambda_penalty=lambda_penalty,
        )
    )


@mcp.tool()
def stele_text_experience_store(kind: str, content: str) -> str:
    """Metis text experience store."""
    return json.dumps(
        get_store().text_experience_store(kind=kind, content=content)
    )


@mcp.tool()
def stele_crystallize_plan_to_tool(
    plan_id: str, reuse_count: int, min_reuse: int = 3
) -> str:
    """Metis crystallize plan to tool."""
    return json.dumps(
        get_store().crystallize_plan_to_tool(
            plan_id=plan_id,
            reuse_count=reuse_count,
            min_reuse=min_reuse,
        )
    )


@mcp.tool()
def stele_dual_retrieve(text_json: str, code_json: str) -> str:
    """Metis dual retrieve."""
    texts = json.loads(text_json)
    codes = json.loads(code_json)
    return json.dumps(
        get_store().dual_retrieve(text_hits=texts, code_tool_ids=codes)
    )


@mcp.tool()
def stele_representation_tradeoff(
    construction_cost: float,
    execution_efficiency: float,
    transferability: float,
) -> str:
    """Metis representation tradeoff."""
    return json.dumps(
        get_store().representation_tradeoff(
            construction_cost=construction_cost,
            execution_efficiency=execution_efficiency,
            transferability=transferability,
        )
    )


@mcp.tool()
def stele_promote_kind_gate(kind: str) -> str:
    """Metis promote kind gate."""
    return json.dumps(get_store().promote_kind_gate(kind=kind))


@mcp.tool()
def stele_metis_loop_plan(phase: str) -> str:
    """Metis loop plan."""
    return json.dumps(get_store().metis_loop_plan(phase=phase))


@mcp.tool()
def stele_single_trajectory_reflect(
    trajectory_id: str, error_note: str
) -> str:
    """SAMULE single trajectory reflect."""
    return json.dumps(
        get_store().single_trajectory_reflect(
            trajectory_id=trajectory_id, error_note=error_note
        )
    )


@mcp.tool()
def stele_intra_task_taxonomy(labels_json: str) -> str:
    """SAMULE intra-task taxonomy."""
    labels = json.loads(labels_json)
    return json.dumps(get_store().intra_task_taxonomy(error_labels=labels))


@mcp.tool()
def stele_inter_task_transfer(error_type: str, strategy: str) -> str:
    """SAMULE inter-task transfer."""
    return json.dumps(
        get_store().inter_task_transfer(
            error_type=error_type, strategy=strategy
        )
    )


@mcp.tool()
def stele_foresight_reflect(predicted: str, actual: str) -> str:
    """SAMULE foresight reflect."""
    return json.dumps(
        get_store().foresight_reflect(
            predicted=predicted, actual=actual
        )
    )


@mcp.tool()
def stele_failure_centric_gate(
    success_count: int, failure_count: int
) -> str:
    """SAMULE failure-centric gate."""
    return json.dumps(
        get_store().failure_centric_gate(
            success_count=success_count, failure_count=failure_count
        )
    )


@mcp.tool()
def stele_merge_reflections(levels_json: str) -> str:
    """SAMULE merge reflections."""
    levels = json.loads(levels_json)
    return json.dumps(get_store().merge_reflections(levels_present=levels))


@mcp.tool()
def stele_experience_bank_record(
    experience: str, weight: float = 1.0
) -> str:
    """LIVE-EVO experience bank record."""
    return json.dumps(
        get_store().experience_bank_record(
            experience=experience, weight=weight
        )
    )


@mcp.tool()
def stele_meta_guideline_record(guideline: str) -> str:
    """LIVE-EVO meta guideline record."""
    return json.dumps(
        get_store().meta_guideline_record(guideline=guideline)
    )


@mcp.tool()
def stele_compile_task_guideline(
    task: str, experience_count: int, has_meta: bool
) -> str:
    """LIVE-EVO compile task guideline."""
    return json.dumps(
        get_store().compile_task_guideline(
            task=task,
            experience_count=experience_count,
            has_meta=has_meta,
        )
    )


@mcp.tool()
def stele_update_experience_weight(
    weight: float, delta_on_minus_off: float, lr: float = 0.1
) -> str:
    """LIVE-EVO update experience weight."""
    return json.dumps(
        get_store().update_experience_weight(
            weight=weight,
            delta_on_minus_off=delta_on_minus_off,
            lr=lr,
        )
    )


@mcp.tool()
def stele_forget_stale_experience(
    weight: float, min_weight: float = 0.05
) -> str:
    """LIVE-EVO forget stale experience."""
    return json.dumps(
        get_store().forget_stale_experience(
            weight=weight, min_weight=min_weight
        )
    )


@mcp.tool()
def stele_liveevo_online_round(phase: str) -> str:
    """LIVE-EVO online round."""
    return json.dumps(get_store().liveevo_online_round(phase=phase))


@mcp.tool()
def stele_socratic_teacher_craft(weakness: str, question: str) -> str:
    """Socratic-Zero teacher craft."""
    return json.dumps(
        get_store().socratic_teacher_craft(
            weakness=weakness, question=question
        )
    )


@mcp.tool()
def stele_socratic_solver_preference(success: bool, failed: bool) -> str:
    """Socratic-Zero solver preference."""
    return json.dumps(
        get_store().socratic_solver_preference(
            success=success, failed=failed
        )
    )


@mcp.tool()
def stele_socratic_generator_distill(teacher_strategy: str) -> str:
    """Socratic-Zero generator distill."""
    return json.dumps(
        get_store().socratic_generator_distill(
            teacher_strategy=teacher_strategy
        )
    )


@mcp.tool()
def stele_socratic_seed_bootstrap(
    seed_count: int, min_seeds: int = 100
) -> str:
    """Socratic-Zero seed bootstrap."""
    return json.dumps(
        get_store().socratic_seed_bootstrap(
            seed_count=seed_count, min_seeds=min_seeds
        )
    )


@mcp.tool()
def stele_socratic_weakness_target(
    fail_rate: float, threshold: float = 0.4
) -> str:
    """Socratic-Zero weakness target."""
    return json.dumps(
        get_store().socratic_weakness_target(
            fail_rate=fail_rate, threshold=threshold
        )
    )


@mcp.tool()
def stele_socratic_closed_loop(phase: str) -> str:
    """Socratic-Zero closed loop."""
    return json.dumps(get_store().socratic_closed_loop(phase=phase))


@mcp.tool()
def stele_spiral_self_play_match(game: str, role: str, won: bool) -> str:
    """SPIRAL self-play match."""
    return json.dumps(
        get_store().spiral_self_play_match(
            game=game, role=role, won=won
        )
    )


@mcp.tool()
def stele_spiral_rae_advantage(
    reward: float, role_baseline: float
) -> str:
    """SPIRAL RAE advantage."""
    return json.dumps(
        get_store().spiral_rae_advantage(
            reward=reward, role_baseline=role_baseline
        )
    )


@mcp.tool()
def stele_spiral_baseline_ema(
    baseline: float, reward: float, decay: float = 0.95
) -> str:
    """SPIRAL baseline EMA."""
    return json.dumps(
        get_store().spiral_baseline_ema(
            baseline=baseline, reward=reward, decay=decay
        )
    )


@mcp.tool()
def stele_spiral_transfer_pattern(pattern: str) -> str:
    """SPIRAL transfer pattern."""
    return json.dumps(
        get_store().spiral_transfer_pattern(pattern=pattern)
    )


@mcp.tool()
def stele_spiral_opponent_strength(
    self_elo: float, opponent_elo: float
) -> str:
    """SPIRAL opponent strength."""
    return json.dumps(
        get_store().spiral_opponent_strength(
            self_elo=self_elo, opponent_elo=opponent_elo
        )
    )


@mcp.tool()
def stele_spiral_multi_game_plan(phase: str) -> str:
    """SPIRAL multi-game plan."""
    return json.dumps(get_store().spiral_multi_game_plan(phase=phase))


@mcp.tool()
def stele_smith_store_memory(tier: str, content: str) -> str:
    """SMITH store memory."""
    return json.dumps(
        get_store().smith_store_memory(tier=tier, content=content)
    )


@mcp.tool()
def stele_smith_create_tool(tool_name: str, sandbox_pass: bool) -> str:
    """SMITH create tool."""
    return json.dumps(
        get_store().smith_create_tool(
            tool_name=tool_name, sandbox_pass=sandbox_pass
        )
    )


@mcp.tool()
def stele_smith_retrieve_episode(
    similarity: float, threshold: float = 0.5
) -> str:
    """SMITH retrieve episode."""
    return json.dumps(
        get_store().smith_retrieve_episode(
            similarity=similarity, threshold=threshold
        )
    )


@mcp.tool()
def stele_smith_curriculum_difficulty(ensemble_fail_rate: float) -> str:
    """SMITH curriculum difficulty."""
    return json.dumps(
        get_store().smith_curriculum_difficulty(
            ensemble_fail_rate=ensemble_fail_rate
        )
    )


@mcp.tool()
def stele_smith_tool_reuse_gate(
    tool_exists: bool, task_similar: bool
) -> str:
    """SMITH tool reuse gate."""
    return json.dumps(
        get_store().smith_tool_reuse_gate(
            tool_exists=tool_exists, task_similar=task_similar
        )
    )


@mcp.tool()
def stele_smith_loop_plan(phase: str) -> str:
    """SMITH loop plan."""
    return json.dumps(get_store().smith_loop_plan(phase=phase))


@mcp.tool()
def stele_hmem_leaf_event(topic: str, timestamp: str) -> str:
    """H-Mem leaf event."""
    return json.dumps(
        get_store().hmem_leaf_event(topic=topic, timestamp=timestamp)
    )


@mcp.tool()
def stele_hmem_consolidate_nodes(
    time_gap: float, same_topic: bool, max_gap: float = 1.0
) -> str:
    """H-Mem consolidate nodes."""
    return json.dumps(
        get_store().hmem_consolidate_nodes(
            time_gap=time_gap, max_gap=max_gap, same_topic=same_topic
        )
    )


@mcp.tool()
def stele_hmem_link_entities(
    entity_a: str, entity_b: str, relation: str
) -> str:
    """H-Mem link entities."""
    return json.dumps(
        get_store().hmem_link_entities(
            entity_a=entity_a, entity_b=entity_b, relation=relation
        )
    )


@mcp.tool()
def stele_hmem_decompose_query(sub_queries_json: str) -> str:
    """H-Mem decompose query."""
    subs = json.loads(sub_queries_json)
    return json.dumps(get_store().hmem_decompose_query(sub_queries=subs))


@mcp.tool()
def stele_hmem_hybrid_retrieve(tree_hits: int, graph_hops: int) -> str:
    """H-Mem hybrid retrieve."""
    return json.dumps(
        get_store().hmem_hybrid_retrieve(
            tree_hits=tree_hits, graph_hops=graph_hops
        )
    )


@mcp.tool()
def stele_hmem_evolution_gate(
    short_term_count: int, consolidated_count: int
) -> str:
    """H-Mem evolution gate."""
    return json.dumps(
        get_store().hmem_evolution_gate(
            short_term_count=short_term_count,
            consolidated_count=consolidated_count,
        )
    )


@mcp.tool()
def stele_himem_segment_episode(
    topic: str, surprise: float, surprise_threshold: float = 0.5
) -> str:
    """HiMem segment episode."""
    return json.dumps(
        get_store().himem_segment_episode(
            topic=topic,
            surprise=surprise,
            surprise_threshold=surprise_threshold,
        )
    )


@mcp.tool()
def stele_himem_extract_note(knowledge: str) -> str:
    """HiMem extract note."""
    return json.dumps(get_store().himem_extract_note(knowledge=knowledge))


@mcp.tool()
def stele_himem_link_episode_note(episode_id: str, note_id: str) -> str:
    """HiMem link episode note."""
    return json.dumps(
        get_store().himem_link_episode_note(
            episode_id=episode_id, note_id=note_id
        )
    )


@mcp.tool()
def stele_himem_retrieve_strategy(mode: str, note_hit: bool) -> str:
    """HiMem retrieve strategy."""
    return json.dumps(
        get_store().himem_retrieve_strategy(mode=mode, note_hit=note_hit)
    )


@mcp.tool()
def stele_himem_reconsolidate(conflict: bool, missing_knowledge: bool) -> str:
    """HiMem reconsolidate."""
    return json.dumps(
        get_store().himem_reconsolidate(
            conflict=conflict, missing_knowledge=missing_knowledge
        )
    )


@mcp.tool()
def stele_himem_loop_plan(phase: str) -> str:
    """HiMem loop plan."""
    return json.dumps(get_store().himem_loop_plan(phase=phase))


@mcp.tool()
def stele_hmeml_store_level(level: str, content: str) -> str:
    """H-MEM store level."""
    return json.dumps(
        get_store().hmeml_store_level(level=level, content=content)
    )


@mcp.tool()
def stele_hmeml_route_query(start_level: str) -> str:
    """H-MEM route query."""
    return json.dumps(get_store().hmeml_route_query(start_level=start_level))


@mcp.tool()
def stele_hmeml_descend(current_level: str, hit: bool) -> str:
    """H-MEM descend."""
    return json.dumps(
        get_store().hmeml_descend(current_level=current_level, hit=hit)
    )


@mcp.tool()
def stele_hmeml_parent_link(parent_level: str, child_level: str) -> str:
    """H-MEM parent link."""
    return json.dumps(
        get_store().hmeml_parent_link(
            parent_level=parent_level, child_level=child_level
        )
    )


@mcp.tool()
def stele_hmeml_efficiency_score(
    levels_scanned: int, max_levels: int = 4
) -> str:
    """H-MEM efficiency score."""
    return json.dumps(
        get_store().hmeml_efficiency_score(
            levels_scanned=levels_scanned, max_levels=max_levels
        )
    )


@mcp.tool()
def stele_hmeml_loop_plan(phase: str) -> str:
    """H-MEM loop plan."""
    return json.dumps(get_store().hmeml_loop_plan(phase=phase))


@mcp.tool()
def stele_hyperskill_add_subtask(label: str) -> str:
    """HyperSkill add subtask."""
    return json.dumps(get_store().hyperskill_add_subtask(label=label))


@mcp.tool()
def stele_hyperskill_add_skill(label: str) -> str:
    """HyperSkill add skill."""
    return json.dumps(get_store().hyperskill_add_skill(label=label))


@mcp.tool()
def stele_hyperskill_add_hyperedge(
    subtask_ids: list[str], skill_ids: list[str], utility: float
) -> str:
    """HyperSkill add hyperedge."""
    return json.dumps(
        get_store().hyperskill_add_hyperedge(
            subtask_ids=subtask_ids,
            skill_ids=skill_ids,
            utility=utility,
        )
    )


@mcp.tool()
def stele_hyperskill_dual_path_retrieve(
    subtask_hits: int, trajectory_hits: int
) -> str:
    """HyperSkill dual-path retrieve."""
    return json.dumps(
        get_store().hyperskill_dual_path_retrieve(
            subtask_hits=subtask_hits, trajectory_hits=trajectory_hits
        )
    )


@mcp.tool()
def stele_hyperskill_rank_skills(cooccurrence: int, utility: float) -> str:
    """HyperSkill rank skills."""
    return json.dumps(
        get_store().hyperskill_rank_skills(
            cooccurrence=cooccurrence, utility=utility
        )
    )


@mcp.tool()
def stele_hyperskill_maintain_plan(
    utility: float, prune_below: float = 0.2, redundant: bool = False
) -> str:
    """HyperSkill maintain plan."""
    return json.dumps(
        get_store().hyperskill_maintain_plan(
            utility=utility,
            prune_below=prune_below,
            redundant=redundant,
        )
    )


@mcp.tool()
def stele_hyperskill_loop_plan(phase: str) -> str:
    """HyperSkill loop plan."""
    return json.dumps(get_store().hyperskill_loop_plan(phase=phase))


@mcp.tool()
def stele_dcpm_day_write(
    belief: str, superseded_id: str | None = None
) -> str:
    """DCPM day write."""
    return json.dumps(
        get_store().dcpm_day_write(
            belief=belief, superseded_id=superseded_id
        )
    )


@mcp.tool()
def stele_dcpm_supersedes_chain(chain_len: int) -> str:
    """DCPM supersedes chain."""
    return json.dumps(
        get_store().dcpm_supersedes_chain(chain_len=chain_len)
    )


@mcp.tool()
def stele_dcpm_night_induce(
    fact_cluster_size: int, min_cluster: int = 3
) -> str:
    """DCPM night induce."""
    return json.dumps(
        get_store().dcpm_night_induce(
            fact_cluster_size=fact_cluster_size, min_cluster=min_cluster
        )
    )


@mcp.tool()
def stele_dcpm_cross_domain_collision(
    behavioral_similarity: float,
    semantic_similarity: float,
    behavior_threshold: float = 0.7,
    semantic_max: float = 0.3,
) -> str:
    """DCPM cross-domain collision."""
    return json.dumps(
        get_store().dcpm_cross_domain_collision(
            behavioral_similarity=behavioral_similarity,
            semantic_similarity=semantic_similarity,
            behavior_threshold=behavior_threshold,
            semantic_max=semantic_max,
        )
    )


@mcp.tool()
def stele_dcpm_hierarchy_level(level: str) -> str:
    """DCPM hierarchy level."""
    return json.dumps(get_store().dcpm_hierarchy_level(level=level))


@mcp.tool()
def stele_dcpm_loop_plan(phase: str) -> str:
    """DCPM loop plan."""
    return json.dumps(get_store().dcpm_loop_plan(phase=phase))


@mcp.tool()
def stele_memos_create_cube(kind: str, content: str) -> str:
    """MemOS create cube."""
    return json.dumps(
        get_store().memos_create_cube(kind=kind, content=content)
    )


@mcp.tool()
def stele_memos_schedule(strategy: str, candidate_count: int) -> str:
    """MemOS schedule."""
    return json.dumps(
        get_store().memos_schedule(
            strategy=strategy, candidate_count=candidate_count
        )
    )


@mcp.tool()
def stele_memos_lifecycle(state: str, action: str) -> str:
    """MemOS lifecycle."""
    return json.dumps(
        get_store().memos_lifecycle(state=state, action=action)
    )


@mcp.tool()
def stele_memos_compose(cube_ids: list[str]) -> str:
    """MemOS compose."""
    return json.dumps(get_store().memos_compose(cube_ids=cube_ids))


@mcp.tool()
def stele_memos_migrate(from_kind: str, to_kind: str) -> str:
    """MemOS migrate."""
    return json.dumps(
        get_store().memos_migrate(from_kind=from_kind, to_kind=to_kind)
    )


@mcp.tool()
def stele_memos_fuse_gate(compatible: bool, conflict: bool) -> str:
    """MemOS fuse gate."""
    return json.dumps(
        get_store().memos_fuse_gate(
            compatible=compatible, conflict=conflict
        )
    )


@mcp.tool()
def stele_memos_loop_plan(phase: str) -> str:
    """MemOS loop plan."""
    return json.dumps(get_store().memos_loop_plan(phase=phase))


@mcp.tool()
def stele_skillcraft_save_skill(
    name: str, steps: int, verified: bool
) -> str:
    """SkillCraft save skill."""
    return json.dumps(
        get_store().skillcraft_save_skill(
            name=name, steps=steps, verified=verified
        )
    )


@mcp.tool()
def stele_skillcraft_get_skill(skill_id: str) -> str:
    """SkillCraft get skill."""
    return json.dumps(get_store().skillcraft_get_skill(skill_id=skill_id))


@mcp.tool()
def stele_skillcraft_list_skills(library_size: int) -> str:
    """SkillCraft list skills."""
    return json.dumps(
        get_store().skillcraft_list_skills(library_size=library_size)
    )


@mcp.tool()
def stele_skillcraft_execute_skill(
    skill_exists: bool, params_ok: bool
) -> str:
    """SkillCraft execute skill."""
    return json.dumps(
        get_store().skillcraft_execute_skill(
            skill_exists=skill_exists, params_ok=params_ok
        )
    )


@mcp.tool()
def stele_skillcraft_verify_skill(
    syntax_ok: bool, runtime_ok: bool, nonempty_output: bool
) -> str:
    """SkillCraft verify skill."""
    return json.dumps(
        get_store().skillcraft_verify_skill(
            syntax_ok=syntax_ok,
            runtime_ok=runtime_ok,
            nonempty_output=nonempty_output,
        )
    )


@mcp.tool()
def stele_skillcraft_token_efficiency(
    tokens_baseline: int, tokens_skill_mode: int
) -> str:
    """SkillCraft token efficiency."""
    return json.dumps(
        get_store().skillcraft_token_efficiency(
            tokens_baseline=tokens_baseline,
            tokens_skill_mode=tokens_skill_mode,
        )
    )


@mcp.tool()
def stele_skillcraft_loop_plan(phase: str) -> str:
    """SkillCraft loop plan."""
    return json.dumps(get_store().skillcraft_loop_plan(phase=phase))


@mcp.tool()
def stele_cma_persist(content: str) -> str:
    """CMA persist."""
    return json.dumps(get_store().cma_persist(content=content))


@mcp.tool()
def stele_cma_selective_retain(
    utility: float, retain_threshold: float = 0.4
) -> str:
    """CMA selective retain."""
    return json.dumps(
        get_store().cma_selective_retain(
            utility=utility, retain_threshold=retain_threshold
        )
    )


@mcp.tool()
def stele_cma_associative_route(cue: str, hop_budget: int = 2) -> str:
    """CMA associative route."""
    return json.dumps(
        get_store().cma_associative_route(cue=cue, hop_budget=hop_budget)
    )


@mcp.tool()
def stele_cma_temporal_chain(
    event_a: str, event_b: str, order_ok: bool
) -> str:
    """CMA temporal chain."""
    return json.dumps(
        get_store().cma_temporal_chain(
            event_a=event_a, event_b=event_b, order_ok=order_ok
        )
    )


@mcp.tool()
def stele_cma_consolidate(
    episode_count: int, min_episodes: int = 2
) -> str:
    """CMA consolidate."""
    return json.dumps(
        get_store().cma_consolidate(
            episode_count=episode_count, min_episodes=min_episodes
        )
    )


@mcp.tool()
def stele_cma_probe_gate(probe: str, supports_mutation: bool) -> str:
    """CMA probe gate."""
    return json.dumps(
        get_store().cma_probe_gate(
            probe=probe, supports_mutation=supports_mutation
        )
    )


@mcp.tool()
def stele_cma_loop_plan(phase: str) -> str:
    """CMA loop plan."""
    return json.dumps(get_store().cma_loop_plan(phase=phase))


@mcp.tool()
def stele_agentfold_workspace_split(
    working_tokens: int, long_term_blocks: int
) -> str:
    """AgentFold workspace split."""
    return json.dumps(
        get_store().agentfold_workspace_split(
            working_tokens=working_tokens,
            long_term_blocks=long_term_blocks,
        )
    )


@mcp.tool()
def stele_agentfold_fold_command(
    mode: str, range_start: int, step_t: int
) -> str:
    """AgentFold fold command."""
    return json.dumps(
        get_store().agentfold_fold_command(
            mode=mode, range_start=range_start, step_t=step_t
        )
    )


@mcp.tool()
def stele_agentfold_granular_condense(
    last_step_tokens: int, target_tokens: int
) -> str:
    """AgentFold granular condense."""
    return json.dumps(
        get_store().agentfold_granular_condense(
            last_step_tokens=last_step_tokens, target_tokens=target_tokens
        )
    )


@mcp.tool()
def stele_agentfold_deep_consolidate(blocks_merged: int) -> str:
    """AgentFold deep consolidate."""
    return json.dumps(
        get_store().agentfold_deep_consolidate(blocks_merged=blocks_merged)
    )


@mcp.tool()
def stele_agentfold_context_budget(
    turns: int, tokens: int, soft_cap: int = 7000
) -> str:
    """AgentFold context budget."""
    return json.dumps(
        get_store().agentfold_context_budget(
            turns=turns, tokens=tokens, soft_cap=soft_cap
        )
    )


@mcp.tool()
def stele_agentfold_loop_plan(phase: str) -> str:
    """AgentFold loop plan."""
    return json.dumps(get_store().agentfold_loop_plan(phase=phase))


@mcp.tool()
def stele_memengine_register_function(name: str) -> str:
    """MemEngine register function."""
    return json.dumps(get_store().memengine_register_function(name=name))


@mcp.tool()
def stele_memengine_compose_operation(
    op: str, function_ids: list[str]
) -> str:
    """MemEngine compose operation."""
    return json.dumps(
        get_store().memengine_compose_operation(
            op=op, function_ids=function_ids
        )
    )


@mcp.tool()
def stele_memengine_bind_model(
    model_name: str, operation_ids: list[str]
) -> str:
    """MemEngine bind model."""
    return json.dumps(
        get_store().memengine_bind_model(
            model_name=model_name, operation_ids=operation_ids
        )
    )


@mcp.tool()
def stele_memengine_config_set(key: str, value: str) -> str:
    """MemEngine config set."""
    return json.dumps(
        get_store().memengine_config_set(key=key, value=value)
    )


@mcp.tool()
def stele_memengine_reflect_plan(
    entries: int, min_entries: int = 2
) -> str:
    """MemEngine reflect plan."""
    return json.dumps(
        get_store().memengine_reflect_plan(
            entries=entries, min_entries=min_entries
        )
    )


@mcp.tool()
def stele_memengine_pluggable(agent_compatible: bool) -> str:
    """MemEngine pluggable."""
    return json.dumps(
        get_store().memengine_pluggable(agent_compatible=agent_compatible)
    )


@mcp.tool()
def stele_memengine_loop_plan(phase: str) -> str:
    """MemEngine loop plan."""
    return json.dumps(get_store().memengine_loop_plan(phase=phase))


@mcp.tool()
def stele_simplemem_compress(raw_turns: int, window: int = 20) -> str:
    """SimpleMem compress."""
    return json.dumps(
        get_store().simplemem_compress(raw_turns=raw_turns, window=window)
    )


@mcp.tool()
def stele_simplemem_synthesize(
    related_facts: int, min_related: int = 2
) -> str:
    """SimpleMem synthesize."""
    return json.dumps(
        get_store().simplemem_synthesize(
            related_facts=related_facts, min_related=min_related
        )
    )


@mcp.tool()
def stele_simplemem_intent_scope(complexity: str) -> str:
    """SimpleMem intent scope."""
    return json.dumps(
        get_store().simplemem_intent_scope(complexity=complexity)
    )


@mcp.tool()
def stele_simplemem_multiview_index(
    dense: bool, sparse: bool, metadata: bool
) -> str:
    """SimpleMem multiview index."""
    return json.dumps(
        get_store().simplemem_multiview_index(
            dense=dense, sparse=sparse, metadata=metadata
        )
    )


@mcp.tool()
def stele_simplemem_token_ratio(
    tokens_baseline: int, tokens_simplemem: int
) -> str:
    """SimpleMem token ratio."""
    return json.dumps(
        get_store().simplemem_token_ratio(
            tokens_baseline=tokens_baseline,
            tokens_simplemem=tokens_simplemem,
        )
    )


@mcp.tool()
def stele_simplemem_loop_plan(phase: str) -> str:
    """SimpleMem loop plan."""
    return json.dumps(get_store().simplemem_loop_plan(phase=phase))


@mcp.tool()
def stele_omem_extract_persona(trait: str, confidence: float) -> str:
    """O-Mem extract persona."""
    return json.dumps(
        get_store().omem_extract_persona(
            trait=trait, confidence=confidence
        )
    )


@mcp.tool()
def stele_omem_update_event(event: str, timestamp: str) -> str:
    """O-Mem update event."""
    return json.dumps(
        get_store().omem_update_event(event=event, timestamp=timestamp)
    )


@mcp.tool()
def stele_omem_hierarchy_retrieve(channel: str, hits: int) -> str:
    """O-Mem hierarchy retrieve."""
    return json.dumps(
        get_store().omem_hierarchy_retrieve(channel=channel, hits=hits)
    )


@mcp.tool()
def stele_omem_profile_gate(
    confidence: float, min_confidence: float = 0.5
) -> str:
    """O-Mem profile gate."""
    return json.dumps(
        get_store().omem_profile_gate(
            confidence=confidence, min_confidence=min_confidence
        )
    )


@mcp.tool()
def stele_omem_scale_memory_time(
    interactions: int, memory_units: int
) -> str:
    """O-Mem scale memory time."""
    return json.dumps(
        get_store().omem_scale_memory_time(
            interactions=interactions, memory_units=memory_units
        )
    )


@mcp.tool()
def stele_omem_loop_plan(phase: str) -> str:
    """O-Mem loop plan."""
    return json.dumps(get_store().omem_loop_plan(phase=phase))


@mcp.tool()
def stele_mandol_basic_unit(content: str) -> str:
    """Mandol basic unit."""
    return json.dumps(get_store().mandol_basic_unit(content=content))


@mcp.tool()
def stele_mandol_agglomerate(basic_ids: list[str]) -> str:
    """Mandol agglomerate."""
    return json.dumps(get_store().mandol_agglomerate(basic_ids=basic_ids))


@mcp.tool()
def stele_mandol_semantic_map_put(key: str, vector_ok: bool) -> str:
    """Mandol semantic map put."""
    return json.dumps(
        get_store().mandol_semantic_map_put(key=key, vector_ok=vector_ok)
    )


@mcp.tool()
def stele_mandol_hybrid_retrieve(vector_hits: int, graph_hops: int) -> str:
    """Mandol hybrid retrieve."""
    return json.dumps(
        get_store().mandol_hybrid_retrieve(
            vector_hits=vector_hits, graph_hops=graph_hops
        )
    )


@mcp.tool()
def stele_mandol_query_route(query_type: str) -> str:
    """Mandol query route."""
    return json.dumps(get_store().mandol_query_route(query_type=query_type))


@mcp.tool()
def stele_mandol_token_budget(
    selected_tokens: int, max_tokens: int
) -> str:
    """Mandol token budget."""
    return json.dumps(
        get_store().mandol_token_budget(
            selected_tokens=selected_tokens, max_tokens=max_tokens
        )
    )


@mcp.tool()
def stele_mandol_loop_plan(phase: str) -> str:
    """Mandol loop plan."""
    return json.dumps(get_store().mandol_loop_plan(phase=phase))


@mcp.tool()
def stele_memanto_store_typed(category: str, content: str) -> str:
    """Memanto store typed."""
    return json.dumps(
        get_store().memanto_store_typed(category=category, content=content)
    )


@mcp.tool()
def stele_memanto_conflict_resolve(conflict: bool, newer_wins: bool) -> str:
    """Memanto conflict resolve."""
    return json.dumps(
        get_store().memanto_conflict_resolve(
            conflict=conflict, newer_wins=newer_wins
        )
    )


@mcp.tool()
def stele_memanto_version(entry_id: str, version: int) -> str:
    """Memanto version."""
    return json.dumps(
        get_store().memanto_version(entry_id=entry_id, version=version)
    )


@mcp.tool()
def stele_memanto_retrieve(query: str, single_query: bool = True) -> str:
    """Memanto retrieve."""
    return json.dumps(
        get_store().memanto_retrieve(query=query, single_query=single_query)
    )


@mcp.tool()
def stele_memanto_latency_gate(
    latency_ms: float, soft_cap_ms: float = 90.0
) -> str:
    """Memanto latency gate."""
    return json.dumps(
        get_store().memanto_latency_gate(
            latency_ms=latency_ms, soft_cap_ms=soft_cap_ms
        )
    )


@mcp.tool()
def stele_memanto_loop_plan(phase: str) -> str:
    """Memanto loop plan."""
    return json.dumps(get_store().memanto_loop_plan(phase=phase))


@mcp.tool()
def stele_zep_add_episode(content: str, valid_at: str) -> str:
    """Zep add episode."""
    return json.dumps(
        get_store().zep_add_episode(content=content, valid_at=valid_at)
    )


@mcp.tool()
def stele_zep_link_entities(
    entity_a: str, entity_b: str, relation: str
) -> str:
    """Zep link entities."""
    return json.dumps(
        get_store().zep_link_entities(
            entity_a=entity_a, entity_b=entity_b, relation=relation
        )
    )


@mcp.tool()
def stele_zep_bitemporal(valid_at: str, transaction_at: str) -> str:
    """Zep bitemporal."""
    return json.dumps(
        get_store().zep_bitemporal(
            valid_at=valid_at, transaction_at=transaction_at
        )
    )


@mcp.tool()
def stele_zep_synthesize(
    conversation_facts: int, business_facts: int
) -> str:
    """Zep synthesize."""
    return json.dumps(
        get_store().zep_synthesize(
            conversation_facts=conversation_facts,
            business_facts=business_facts,
        )
    )


@mcp.tool()
def stele_zep_cross_session(sessions: int, min_sessions: int = 2) -> str:
    """Zep cross session."""
    return json.dumps(
        get_store().zep_cross_session(
            sessions=sessions, min_sessions=min_sessions
        )
    )


@mcp.tool()
def stele_zep_loop_plan(phase: str) -> str:
    """Zep loop plan."""
    return json.dumps(get_store().zep_loop_plan(phase=phase))


@mcp.tool()
def stele_memgpt_main_capacity(
    used_tokens: int, max_tokens: int, warn_ratio: float = 0.7
) -> str:
    """MemGPT main capacity."""
    return json.dumps(
        get_store().memgpt_main_capacity(
            used_tokens=used_tokens,
            max_tokens=max_tokens,
            warn_ratio=warn_ratio,
        )
    )


@mcp.tool()
def stele_memgpt_page_out(content: str, tier: str) -> str:
    """MemGPT page out."""
    return json.dumps(
        get_store().memgpt_page_out(content=content, tier=tier)
    )


@mcp.tool()
def stele_memgpt_page_in(page_id: str, fits: bool) -> str:
    """MemGPT page in."""
    return json.dumps(
        get_store().memgpt_page_in(page_id=page_id, fits=fits)
    )


@mcp.tool()
def stele_memgpt_recall_search(query: str, hits: int) -> str:
    """MemGPT recall search."""
    return json.dumps(
        get_store().memgpt_recall_search(query=query, hits=hits)
    )


@mcp.tool()
def stele_memgpt_archival_search(query: str, page: int = 0) -> str:
    """MemGPT archival search."""
    return json.dumps(
        get_store().memgpt_archival_search(query=query, page=page)
    )


@mcp.tool()
def stele_memgpt_loop_plan(phase: str) -> str:
    """MemGPT loop plan."""
    return json.dumps(get_store().memgpt_loop_plan(phase=phase))


@mcp.tool()
def stele_ripple_store_episode(content: str) -> str:
    """RippleMem store episode."""
    return json.dumps(get_store().ripple_store_episode(content=content))


@mcp.tool()
def stele_ripple_link_entity(episode_id: str, entity: str) -> str:
    """RippleMem link entity."""
    return json.dumps(
        get_store().ripple_link_entity(
            episode_id=episode_id, entity=entity
        )
    )


@mcp.tool()
def stele_ripple_seed_retrieve(query: str, seed_hits: int) -> str:
    """RippleMem seed retrieve."""
    return json.dumps(
        get_store().ripple_seed_retrieve(query=query, seed_hits=seed_hits)
    )


@mcp.tool()
def stele_ripple_expand(seeds: int, hop: int, max_hops: int = 2) -> str:
    """RippleMem expand."""
    return json.dumps(
        get_store().ripple_expand(seeds=seeds, hop=hop, max_hops=max_hops)
    )


@mcp.tool()
def stele_ripple_recollect_gate(seed_hits: int, associated: int) -> str:
    """RippleMem recollect gate."""
    return json.dumps(
        get_store().ripple_recollect_gate(
            seed_hits=seed_hits, associated=associated
        )
    )


@mcp.tool()
def stele_ripple_loop_plan(phase: str) -> str:
    """RippleMem loop plan."""
    return json.dumps(get_store().ripple_loop_plan(phase=phase))


@mcp.tool()
def stele_flux_connect_form(src: str, dst: str, relation: str) -> str:
    """FluxMem connect form."""
    return json.dumps(
        get_store().flux_connect_form(src=src, dst=dst, relation=relation)
    )


@mcp.tool()
def stele_flux_feedback_refine(
    edge_id: str, feedback: str, keep: bool
) -> str:
    """FluxMem feedback refine."""
    return json.dumps(
        get_store().flux_feedback_refine(
            edge_id=edge_id, feedback=feedback, keep=keep
        )
    )


@mcp.tool()
def stele_flux_consolidate(circuits: int, min_success: int = 2) -> str:
    """FluxMem consolidate."""
    return json.dumps(
        get_store().flux_consolidate(
            circuits=circuits, min_success=min_success
        )
    )


@mcp.tool()
def stele_flux_repair_link(missing: bool, repaired: bool) -> str:
    """FluxMem repair link."""
    return json.dumps(
        get_store().flux_repair_link(missing=missing, repaired=repaired)
    )


@mcp.tool()
def stele_flux_prune_interference(
    noise_score: float, threshold: float = 0.5
) -> str:
    """FluxMem prune interference."""
    return json.dumps(
        get_store().flux_prune_interference(
            noise_score=noise_score, threshold=threshold
        )
    )


@mcp.tool()
def stele_flux_maturity_gate(
    generalizability: float, min_score: float = 0.5
) -> str:
    """FluxMem maturity gate."""
    return json.dumps(
        get_store().flux_maturity_gate(
            generalizability=generalizability, min_score=min_score
        )
    )


@mcp.tool()
def stele_flux_loop_plan(phase: str) -> str:
    """FluxMem loop plan."""
    return json.dumps(get_store().flux_loop_plan(phase=phase))


@mcp.tool()
def stele_qumem_segment_episode(content: str, continuity: float) -> str:
    """QUMem segment episode."""
    return json.dumps(
        get_store().qumem_segment_episode(
            content=content, continuity=continuity
        )
    )


@mcp.tool()
def stele_qumem_decompose(episode_id: str, mem_type: str) -> str:
    """QUMem decompose."""
    return json.dumps(
        get_store().qumem_decompose(
            episode_id=episode_id, mem_type=mem_type
        )
    )


@mcp.tool()
def stele_qumem_plan_queries(task: str, needs: int) -> str:
    """QUMem plan queries."""
    return json.dumps(
        get_store().qumem_plan_queries(task=task, needs=needs)
    )


@mcp.tool()
def stele_qumem_infer_user_state(
    factual: int, preference: int, insight: int
) -> str:
    """QUMem infer user state."""
    return json.dumps(
        get_store().qumem_infer_user_state(
            factual=factual, preference=preference, insight=insight
        )
    )


@mcp.tool()
def stele_qumem_temporal_valid(
    event_ts: str, query_ts: str, stale: bool
) -> str:
    """QUMem temporal valid."""
    return json.dumps(
        get_store().qumem_temporal_valid(
            event_ts=event_ts, query_ts=query_ts, stale=stale
        )
    )


@mcp.tool()
def stele_qumem_loop_plan(phase: str) -> str:
    """QUMem loop plan."""
    return json.dumps(get_store().qumem_loop_plan(phase=phase))


@mcp.tool()
def stele_viking_extract_event(content: str, high_value: bool) -> str:
    """VikingMem extract event."""
    return json.dumps(
        get_store().viking_extract_event(
            content=content, high_value=high_value
        )
    )


@mcp.tool()
def stele_viking_update_entity(entity: str, event_id: str) -> str:
    """VikingMem update entity."""
    return json.dumps(
        get_store().viking_update_entity(entity=entity, event_id=event_id)
    )


@mcp.tool()
def stele_viking_timeline_compress(topic: str, items: int) -> str:
    """VikingMem timeline compress."""
    return json.dumps(
        get_store().viking_timeline_compress(topic=topic, items=items)
    )


@mcp.tool()
def stele_viking_time_weighted_recall(
    query: str, recency_weight: float
) -> str:
    """VikingMem time-weighted recall."""
    return json.dumps(
        get_store().viking_time_weighted_recall(
            query=query, recency_weight=recency_weight
        )
    )


@mcp.tool()
def stele_viking_rerank(candidates: int, top_k: int) -> str:
    """VikingMem rerank."""
    return json.dumps(
        get_store().viking_rerank(candidates=candidates, top_k=top_k)
    )


@mcp.tool()
def stele_viking_loop_plan(phase: str) -> str:
    """VikingMem loop plan."""
    return json.dumps(get_store().viking_loop_plan(phase=phase))


@mcp.tool()
def stele_recmem_buffer_subconscious(content: str) -> str:
    """RecMem buffer subconscious."""
    return json.dumps(
        get_store().recmem_buffer_subconscious(content=content)
    )


@mcp.tool()
def stele_recmem_recurrence_gate(
    similar_count: int, threshold: int = 5
) -> str:
    """RecMem recurrence gate."""
    return json.dumps(
        get_store().recmem_recurrence_gate(
            similar_count=similar_count, threshold=threshold
        )
    )


@mcp.tool()
def stele_recmem_consolidate_episodic(cluster_size: int) -> str:
    """RecMem consolidate episodic."""
    return json.dumps(
        get_store().recmem_consolidate_episodic(cluster_size=cluster_size)
    )


@mcp.tool()
def stele_recmem_semantic_refine(omitted_facts: int) -> str:
    """RecMem semantic refine."""
    return json.dumps(
        get_store().recmem_semantic_refine(omitted_facts=omitted_facts)
    )


@mcp.tool()
def stele_recmem_merge_retrieve(
    subconscious: int, episodic: int, semantic: int
) -> str:
    """RecMem merge retrieve."""
    return json.dumps(
        get_store().recmem_merge_retrieve(
            subconscious=subconscious,
            episodic=episodic,
            semantic=semantic,
        )
    )


@mcp.tool()
def stele_recmem_loop_plan(phase: str) -> str:
    """RecMem loop plan."""
    return json.dumps(get_store().recmem_loop_plan(phase=phase))


@mcp.tool()
def stele_mbank_store_memory(content: str, significance: float) -> str:
    """MemoryBank store memory."""
    return json.dumps(
        get_store().mbank_store_memory(
            content=content, significance=significance
        )
    )


@mcp.tool()
def stele_mbank_summon(query: str, hits: int) -> str:
    """MemoryBank summon."""
    return json.dumps(get_store().mbank_summon(query=query, hits=hits))


@mcp.tool()
def stele_mbank_personality_synth(traits: int) -> str:
    """MemoryBank personality synth."""
    return json.dumps(get_store().mbank_personality_synth(traits=traits))


@mcp.tool()
def stele_mbank_forget_curve(
    days_elapsed: float, strength: float = 1.0
) -> str:
    """MemoryBank forget curve."""
    return json.dumps(
        get_store().mbank_forget_curve(
            days_elapsed=days_elapsed, strength=strength
        )
    )


@mcp.tool()
def stele_mbank_reinforce(memory_id: str, boost: float) -> str:
    """MemoryBank reinforce."""
    return json.dumps(
        get_store().mbank_reinforce(memory_id=memory_id, boost=boost)
    )


@mcp.tool()
def stele_mbank_loop_plan(phase: str) -> str:
    """MemoryBank loop plan."""
    return json.dumps(get_store().mbank_loop_plan(phase=phase))


@mcp.tool()
def stele_rfmem_familiarity_score(mean_score: float, entropy: float) -> str:
    """RF-Mem familiarity score."""
    return json.dumps(
        get_store().rfmem_familiarity_score(
            mean_score=mean_score, entropy=entropy
        )
    )


@mcp.tool()
def stele_rfmem_path_route(
    mean_score: float,
    entropy: float,
    high_mean: float = 0.7,
    low_entropy: float = 1.0,
) -> str:
    """RF-Mem path route."""
    return json.dumps(
        get_store().rfmem_path_route(
            mean_score=mean_score,
            entropy=entropy,
            high_mean=high_mean,
            low_entropy=low_entropy,
        )
    )


@mcp.tool()
def stele_rfmem_top_k_familiar(candidates: int, top_k: int) -> str:
    """RF-Mem top-k familiar."""
    return json.dumps(
        get_store().rfmem_top_k_familiar(
            candidates=candidates, top_k=top_k
        )
    )


@mcp.tool()
def stele_rfmem_recollect_expand(
    clusters: int, hops: int, max_hops: int = 3
) -> str:
    """RF-Mem recollect expand."""
    return json.dumps(
        get_store().rfmem_recollect_expand(
            clusters=clusters, hops=hops, max_hops=max_hops
        )
    )


@mcp.tool()
def stele_rfmem_alpha_mix(alpha: float, query_weight: float) -> str:
    """RF-Mem alpha mix."""
    return json.dumps(
        get_store().rfmem_alpha_mix(alpha=alpha, query_weight=query_weight)
    )


@mcp.tool()
def stele_rfmem_loop_plan(phase: str) -> str:
    """RF-Mem loop plan."""
    return json.dumps(get_store().rfmem_loop_plan(phase=phase))


@mcp.tool()
def stele_agemem_ltm_store(content: str, tier: str = "ltm") -> str:
    """AgeMem LTM/STM store."""
    return json.dumps(
        get_store().agemem_ltm_store(content=content, tier=tier)
    )


@mcp.tool()
def stele_agemem_stm_manage(capacity: int, used: int) -> str:
    """AgeMem STM manage."""
    return json.dumps(
        get_store().agemem_stm_manage(capacity=capacity, used=used)
    )


@mcp.tool()
def stele_agemem_retrieve(query: str, hits: int) -> str:
    """AgeMem retrieve."""
    return json.dumps(
        get_store().agemem_retrieve(query=query, hits=hits)
    )


@mcp.tool()
def stele_agemem_summarize(entries: int) -> str:
    """AgeMem summarize."""
    return json.dumps(get_store().agemem_summarize(entries=entries))


@mcp.tool()
def stele_agemem_discard_plan(memory_id: str, reason: str) -> str:
    """AgeMem discard plan."""
    return json.dumps(
        get_store().agemem_discard_plan(
            memory_id=memory_id, reason=reason
        )
    )


@mcp.tool()
def stele_agemem_loop_plan(phase: str) -> str:
    """AgeMem loop plan."""
    return json.dumps(get_store().agemem_loop_plan(phase=phase))


@mcp.tool()
def stele_memgas_unit(content: str, granularity: str) -> str:
    """MemGAS unit."""
    return json.dumps(
        get_store().memgas_unit(content=content, granularity=granularity)
    )


@mcp.tool()
def stele_memgas_associate(new_id: str, cluster_size: int) -> str:
    """MemGAS associate."""
    return json.dumps(
        get_store().memgas_associate(
            new_id=new_id, cluster_size=cluster_size
        )
    )


@mcp.tool()
def stele_memgas_entropy_route(entropy: float, low: float = 1.0) -> str:
    """MemGAS entropy route."""
    return json.dumps(
        get_store().memgas_entropy_route(entropy=entropy, low=low)
    )


@mcp.tool()
def stele_memgas_select_granularity(
    preferred: str, entropy: float
) -> str:
    """MemGAS select granularity."""
    return json.dumps(
        get_store().memgas_select_granularity(
            preferred=preferred, entropy=entropy
        )
    )


@mcp.tool()
def stele_memgas_filter_plan(candidates: int, keep: int) -> str:
    """MemGAS filter plan."""
    return json.dumps(
        get_store().memgas_filter_plan(candidates=candidates, keep=keep)
    )


@mcp.tool()
def stele_memgas_loop_plan(phase: str) -> str:
    """MemGAS loop plan."""
    return json.dumps(get_store().memgas_loop_plan(phase=phase))


@mcp.tool()
def stele_memwalker_segment(content: str, chunk_size: int) -> str:
    """MemWalker segment."""
    return json.dumps(
        get_store().memwalker_segment(
            content=content, chunk_size=chunk_size
        )
    )


@mcp.tool()
def stele_memwalker_build_node(summary: str, level: int) -> str:
    """MemWalker build node."""
    return json.dumps(
        get_store().memwalker_build_node(summary=summary, level=level)
    )


@mcp.tool()
def stele_memwalker_navigate(node_id: str, action: str) -> str:
    """MemWalker navigate."""
    return json.dumps(
        get_store().memwalker_navigate(node_id=node_id, action=action)
    )


@mcp.tool()
def stele_memwalker_gather(leaves: int, budget: int) -> str:
    """MemWalker gather."""
    return json.dumps(
        get_store().memwalker_gather(leaves=leaves, budget=budget)
    )


@mcp.tool()
def stele_memwalker_path_gate(depth: int, max_depth: int) -> str:
    """MemWalker path gate."""
    return json.dumps(
        get_store().memwalker_path_gate(depth=depth, max_depth=max_depth)
    )


@mcp.tool()
def stele_memwalker_loop_plan(phase: str) -> str:
    """MemWalker loop plan."""
    return json.dumps(get_store().memwalker_loop_plan(phase=phase))


@mcp.tool()
def stele_mgr_store_layer(content: str, layer: str) -> str:
    """MemGraphRAG store layer."""
    return json.dumps(
        get_store().mgr_store_layer(content=content, layer=layer)
    )


@mcp.tool()
def stele_mgr_detect_conflict(facts: int, anomalies: int) -> str:
    """MemGraphRAG detect conflict."""
    return json.dumps(
        get_store().mgr_detect_conflict(facts=facts, anomalies=anomalies)
    )


@mcp.tool()
def stele_mgr_resolve_plan(conflict_id: str) -> str:
    """MemGraphRAG resolve plan."""
    return json.dumps(get_store().mgr_resolve_plan(conflict_id=conflict_id))


@mcp.tool()
def stele_mgr_multilayer_retrieve(query: str, layers_hit: int) -> str:
    """MemGraphRAG multilayer retrieve."""
    return json.dumps(
        get_store().mgr_multilayer_retrieve(
            query=query, layers_hit=layers_hit
        )
    )


@mcp.tool()
def stele_mgr_propagate(seeds: int, damping: float = 0.85) -> str:
    """MemGraphRAG propagate."""
    return json.dumps(
        get_store().mgr_propagate(seeds=seeds, damping=damping)
    )


@mcp.tool()
def stele_mgr_loop_plan(phase: str) -> str:
    """MemGraphRAG loop plan."""
    return json.dumps(get_store().mgr_loop_plan(phase=phase))


@mcp.tool()
def stele_raptor_embed_chunk(content: str) -> str:
    """RAPTOR embed chunk."""
    return json.dumps(get_store().raptor_embed_chunk(content=content))


@mcp.tool()
def stele_raptor_cluster(chunks: int, clusters: int) -> str:
    """RAPTOR cluster."""
    return json.dumps(
        get_store().raptor_cluster(chunks=chunks, clusters=clusters)
    )


@mcp.tool()
def stele_raptor_summarize_node(level: int, children: int) -> str:
    """RAPTOR summarize node."""
    return json.dumps(
        get_store().raptor_summarize_node(level=level, children=children)
    )


@mcp.tool()
def stele_raptor_tree_traverse(depth: int, keep_per_level: int) -> str:
    """RAPTOR tree traverse."""
    return json.dumps(
        get_store().raptor_tree_traverse(
            depth=depth, keep_per_level=keep_per_level
        )
    )


@mcp.tool()
def stele_raptor_collapsed_retrieve(candidates: int, top_k: int) -> str:
    """RAPTOR collapsed retrieve."""
    return json.dumps(
        get_store().raptor_collapsed_retrieve(
            candidates=candidates, top_k=top_k
        )
    )


@mcp.tool()
def stele_raptor_loop_plan(phase: str) -> str:
    """RAPTOR loop plan."""
    return json.dumps(get_store().raptor_loop_plan(phase=phase))


@mcp.tool()
def stele_lightrag_index_entity(name: str) -> str:
    """LightRAG index entity."""
    return json.dumps(get_store().lightrag_index_entity(name=name))


@mcp.tool()
def stele_lightrag_index_relation(src: str, dst: str, rel: str) -> str:
    """LightRAG index relation."""
    return json.dumps(
        get_store().lightrag_index_relation(src=src, dst=dst, rel=rel)
    )


@mcp.tool()
def stele_lightrag_dual_retrieve(query: str, level: str) -> str:
    """LightRAG dual retrieve."""
    return json.dumps(
        get_store().lightrag_dual_retrieve(query=query, level=level)
    )


@mcp.tool()
def stele_lightrag_incremental_update(new_docs: int) -> str:
    """LightRAG incremental update."""
    return json.dumps(
        get_store().lightrag_incremental_update(new_docs=new_docs)
    )


@mcp.tool()
def stele_lightrag_graph_vector_fuse(
    graph_hits: int, vector_hits: int
) -> str:
    """LightRAG graph-vector fuse."""
    return json.dumps(
        get_store().lightrag_graph_vector_fuse(
            graph_hits=graph_hits, vector_hits=vector_hits
        )
    )


@mcp.tool()
def stele_lightrag_loop_plan(phase: str) -> str:
    """LightRAG loop plan."""
    return json.dumps(get_store().lightrag_loop_plan(phase=phase))


@mcp.tool()
def stele_memorag_memorize(corpus_chars: int) -> str:
    """MemoRAG memorize."""
    return json.dumps(get_store().memorag_memorize(corpus_chars=corpus_chars))


@mcp.tool()
def stele_memorag_clue(query: str, draft: str) -> str:
    """MemoRAG clue."""
    return json.dumps(get_store().memorag_clue(query=query, draft=draft))


@mcp.tool()
def stele_memorag_retrieve_by_clue(clue_id: str, hits: int) -> str:
    """MemoRAG retrieve by clue."""
    return json.dumps(
        get_store().memorag_retrieve_by_clue(clue_id=clue_id, hits=hits)
    )


@mcp.tool()
def stele_memorag_dual_system(role: str) -> str:
    """MemoRAG dual system."""
    return json.dumps(get_store().memorag_dual_system(role=role))


@mcp.tool()
def stele_memorag_generate_plan(evidence: int) -> str:
    """MemoRAG generate plan."""
    return json.dumps(get_store().memorag_generate_plan(evidence=evidence))


@mcp.tool()
def stele_memorag_loop_plan(phase: str) -> str:
    """MemoRAG loop plan."""
    return json.dumps(get_store().memorag_loop_plan(phase=phase))


@mcp.tool()
def stele_pageindex_build_toc(title: str, sections: int) -> str:
    """PageIndex build TOC."""
    return json.dumps(
        get_store().pageindex_build_toc(title=title, sections=sections)
    )


@mcp.tool()
def stele_pageindex_add_section(
    parent_id: str, heading: str, page_start: int
) -> str:
    """PageIndex add section."""
    return json.dumps(
        get_store().pageindex_add_section(
            parent_id=parent_id, heading=heading, page_start=page_start
        )
    )


@mcp.tool()
def stele_pageindex_reason_nav(query: str, candidates: int) -> str:
    """PageIndex reason nav."""
    return json.dumps(
        get_store().pageindex_reason_nav(
            query=query, candidates=candidates
        )
    )


@mcp.tool()
def stele_pageindex_select_section(section_id: str, relevant: bool) -> str:
    """PageIndex select section."""
    return json.dumps(
        get_store().pageindex_select_section(
            section_id=section_id, relevant=relevant
        )
    )


@mcp.tool()
def stele_pageindex_trace_path(hops: int) -> str:
    """PageIndex trace path."""
    return json.dumps(get_store().pageindex_trace_path(hops=hops))


@mcp.tool()
def stele_pageindex_loop_plan(phase: str) -> str:
    """PageIndex loop plan."""
    return json.dumps(get_store().pageindex_loop_plan(phase=phase))


@mcp.tool()
def stele_selfrag_need_retrieve(confidence: float, threshold: float = 0.5) -> str:
    """Self-RAG need retrieve."""
    return json.dumps(
        get_store().selfrag_need_retrieve(
            confidence=confidence, threshold=threshold
        )
    )


@mcp.tool()
def stele_selfrag_relevance_critique(relevant: bool) -> str:
    """Self-RAG relevance critique."""
    return json.dumps(
        get_store().selfrag_relevance_critique(relevant=relevant)
    )


@mcp.tool()
def stele_selfrag_support_critique(supported: bool) -> str:
    """Self-RAG support critique."""
    return json.dumps(
        get_store().selfrag_support_critique(supported=supported)
    )


@mcp.tool()
def stele_selfrag_utility_critique(utility: float) -> str:
    """Self-RAG utility critique."""
    return json.dumps(get_store().selfrag_utility_critique(utility=utility))


@mcp.tool()
def stele_selfrag_select_best(scores: int, pick: int) -> str:
    """Self-RAG select best."""
    return json.dumps(
        get_store().selfrag_select_best(scores=scores, pick=pick)
    )


@mcp.tool()
def stele_selfrag_loop_plan(phase: str) -> str:
    """Self-RAG loop plan."""
    return json.dumps(get_store().selfrag_loop_plan(phase=phase))


@mcp.tool()
def stele_memobrain_dep_edge(src_step: str, dst_step: str) -> str:
    """MemoBrain dep edge."""
    return json.dumps(
        get_store().memobrain_dep_edge(src_step=src_step, dst_step=dst_step)
    )


@mcp.tool()
def stele_memobrain_prune_invalid(step_id: str, invalid: bool) -> str:
    """MemoBrain prune invalid."""
    return json.dumps(
        get_store().memobrain_prune_invalid(step_id=step_id, invalid=invalid)
    )


@mcp.tool()
def stele_memobrain_fold_subtraj(steps: int) -> str:
    """MemoBrain fold subtraj."""
    return json.dumps(get_store().memobrain_fold_subtraj(steps=steps))


@mcp.tool()
def stele_memobrain_flush_budget(used: int, budget: int) -> str:
    """MemoBrain flush budget."""
    return json.dumps(
        get_store().memobrain_flush_budget(used=used, budget=budget)
    )


@mcp.tool()
def stele_memobrain_salience_keep(salience: float, min_keep: float = 0.5) -> str:
    """MemoBrain salience keep."""
    return json.dumps(
        get_store().memobrain_salience_keep(
            salience=salience, min_keep=min_keep
        )
    )


@mcp.tool()
def stele_memobrain_loop_plan(phase: str) -> str:
    """MemoBrain loop plan."""
    return json.dumps(get_store().memobrain_loop_plan(phase=phase))


@mcp.tool()
def stele_crag_evaluate_retrieval(confidence: float) -> str:
    """CRAG evaluate retrieval."""
    return json.dumps(
        get_store().crag_evaluate_retrieval(confidence=confidence)
    )


@mcp.tool()
def stele_crag_correct_refine(chunks: int) -> str:
    """CRAG correct refine."""
    return json.dumps(get_store().crag_correct_refine(chunks=chunks))


@mcp.tool()
def stele_crag_web_fallback_plan(trigger: bool) -> str:
    """CRAG web fallback plan."""
    return json.dumps(get_store().crag_web_fallback_plan(trigger=trigger))


@mcp.tool()
def stele_crag_ambiguous_blend(local_hits: int, web_hits: int) -> str:
    """CRAG ambiguous blend."""
    return json.dumps(
        get_store().crag_ambiguous_blend(
            local_hits=local_hits, web_hits=web_hits
        )
    )


@mcp.tool()
def stele_crag_action_select(action: str) -> str:
    """CRAG action select."""
    return json.dumps(get_store().crag_action_select(action=action))


@mcp.tool()
def stele_crag_loop_plan(phase: str) -> str:
    """CRAG loop plan."""
    return json.dumps(get_store().crag_loop_plan(phase=phase))


@mcp.tool()
def stele_hyde_hypothetical_doc(query: str) -> str:
    """HyDE hypothetical doc."""
    return json.dumps(get_store().hyde_hypothetical_doc(query=query))


@mcp.tool()
def stele_hyde_encode_proxy(hyp_id: str) -> str:
    """HyDE encode proxy."""
    return json.dumps(get_store().hyde_encode_proxy(hyp_id=hyp_id))


@mcp.tool()
def stele_hyde_retrieve_by_hyp(vec_id: str, k: int = 5) -> str:
    """HyDE retrieve by hyp."""
    return json.dumps(get_store().hyde_retrieve_by_hyp(vec_id=vec_id, k=k))


@mcp.tool()
def stele_hyde_filter_hallucination(retained: float) -> str:
    """HyDE filter hallucination."""
    return json.dumps(
        get_store().hyde_filter_hallucination(retained=retained)
    )


@mcp.tool()
def stele_hyde_ground_corpus(hits: int, grounded: int) -> str:
    """HyDE ground corpus."""
    return json.dumps(
        get_store().hyde_ground_corpus(hits=hits, grounded=grounded)
    )


@mcp.tool()
def stele_hyde_loop_plan(phase: str) -> str:
    """HyDE loop plan."""
    return json.dumps(get_store().hyde_loop_plan(phase=phase))


@mcp.tool()
def stele_adaptiverag_classify_complexity(hops: int) -> str:
    """Adaptive-RAG classify complexity."""
    return json.dumps(
        get_store().adaptiverag_classify_complexity(hops=hops)
    )


@mcp.tool()
def stele_adaptiverag_select_strategy(level: int) -> str:
    """Adaptive-RAG select strategy."""
    return json.dumps(get_store().adaptiverag_select_strategy(level=level))


@mcp.tool()
def stele_adaptiverag_no_retrieve(parametric_ok: bool) -> str:
    """Adaptive-RAG no retrieve."""
    return json.dumps(
        get_store().adaptiverag_no_retrieve(parametric_ok=parametric_ok)
    )


@mcp.tool()
def stele_adaptiverag_single_step(hits: int) -> str:
    """Adaptive-RAG single step."""
    return json.dumps(get_store().adaptiverag_single_step(hits=hits))


@mcp.tool()
def stele_adaptiverag_multi_step(steps: int) -> str:
    """Adaptive-RAG multi step."""
    return json.dumps(get_store().adaptiverag_multi_step(steps=steps))


@mcp.tool()
def stele_adaptiverag_loop_plan(phase: str) -> str:
    """Adaptive-RAG loop plan."""
    return json.dumps(get_store().adaptiverag_loop_plan(phase=phase))


@mcp.tool()
def stele_flare_anticipate_sentence(context: str) -> str:
    """FLARE anticipate sentence."""
    return json.dumps(get_store().flare_anticipate_sentence(context=context))


@mcp.tool()
def stele_flare_low_confidence(confidence: float, threshold: float = 0.4) -> str:
    """FLARE low confidence."""
    return json.dumps(
        get_store().flare_low_confidence(
            confidence=confidence, threshold=threshold
        )
    )


@mcp.tool()
def stele_flare_retrieve_for_regen(query: str, k: int = 3) -> str:
    """FLARE retrieve for regen."""
    return json.dumps(
        get_store().flare_retrieve_for_regen(query=query, k=k)
    )


@mcp.tool()
def stele_flare_regenerate_sentence(sent_id: str, with_docs: bool) -> str:
    """FLARE regenerate sentence."""
    return json.dumps(
        get_store().flare_regenerate_sentence(
            sent_id=sent_id, with_docs=with_docs
        )
    )


@mcp.tool()
def stele_flare_active_step(step: int, retrieved: bool) -> str:
    """FLARE active step."""
    return json.dumps(
        get_store().flare_active_step(step=step, retrieved=retrieved)
    )


@mcp.tool()
def stele_flare_loop_plan(phase: str) -> str:
    """FLARE loop plan."""
    return json.dumps(get_store().flare_loop_plan(phase=phase))


@mcp.tool()
def stele_graphreader_build_node(chunk: str) -> str:
    """GraphReader build node."""
    return json.dumps(get_store().graphreader_build_node(chunk=chunk))


@mcp.tool()
def stele_graphreader_read_node(node_id: str) -> str:
    """GraphReader read node."""
    return json.dumps(get_store().graphreader_read_node(node_id=node_id))


@mcp.tool()
def stele_graphreader_read_neighbors(node_id: str, hops: int = 1) -> str:
    """GraphReader read neighbors."""
    return json.dumps(
        get_store().graphreader_read_neighbors(node_id=node_id, hops=hops)
    )


@mcp.tool()
def stele_graphreader_note_insight(text: str) -> str:
    """GraphReader note insight."""
    return json.dumps(get_store().graphreader_note_insight(text=text))


@mcp.tool()
def stele_graphreader_reflect_plan(enough: bool) -> str:
    """GraphReader reflect plan."""
    return json.dumps(get_store().graphreader_reflect_plan(enough=enough))


@mcp.tool()
def stele_graphreader_loop_plan(phase: str) -> str:
    """GraphReader loop plan."""
    return json.dumps(get_store().graphreader_loop_plan(phase=phase))


@mcp.tool()
def stele_gretriever_node_prize(node_id: str, prize: float) -> str:
    """G-Retriever node prize."""
    return json.dumps(
        get_store().gretriever_node_prize(node_id=node_id, prize=prize)
    )


@mcp.tool()
def stele_gretriever_pcst_select(nodes: int, budget: int) -> str:
    """G-Retriever PCST select."""
    return json.dumps(
        get_store().gretriever_pcst_select(nodes=nodes, budget=budget)
    )


@mcp.tool()
def stele_gretriever_subgraph(selected: int) -> str:
    """G-Retriever subgraph."""
    return json.dumps(get_store().gretriever_subgraph(selected=selected))


@mcp.tool()
def stele_gretriever_soft_prompt_plan(subgraph_id: str) -> str:
    """G-Retriever soft prompt plan."""
    return json.dumps(
        get_store().gretriever_soft_prompt_plan(subgraph_id=subgraph_id)
    )


@mcp.tool()
def stele_gretriever_highlight(nodes: int) -> str:
    """G-Retriever highlight."""
    return json.dumps(get_store().gretriever_highlight(nodes=nodes))


@mcp.tool()
def stele_gretriever_loop_plan(phase: str) -> str:
    """G-Retriever loop plan."""
    return json.dumps(get_store().gretriever_loop_plan(phase=phase))


@mcp.tool()
def stele_rqrag_rewrite(query: str) -> str:
    """RQ-RAG rewrite."""
    return json.dumps(get_store().rqrag_rewrite(query=query))


@mcp.tool()
def stele_rqrag_decompose(query: str, parts: int) -> str:
    """RQ-RAG decompose."""
    return json.dumps(
        get_store().rqrag_decompose(query=query, parts=parts)
    )


@mcp.tool()
def stele_rqrag_disambiguate(query: str, intents: int) -> str:
    """RQ-RAG disambiguate."""
    return json.dumps(
        get_store().rqrag_disambiguate(query=query, intents=intents)
    )


@mcp.tool()
def stele_rqrag_refine_mode(mode: str) -> str:
    """RQ-RAG refine mode."""
    return json.dumps(get_store().rqrag_refine_mode(mode=mode))


@mcp.tool()
def stele_rqrag_retrieve_refined(refined_id: str, k: int = 5) -> str:
    """RQ-RAG retrieve refined."""
    return json.dumps(
        get_store().rqrag_retrieve_refined(refined_id=refined_id, k=k)
    )


@mcp.tool()
def stele_rqrag_loop_plan(phase: str) -> str:
    """RQ-RAG loop plan."""
    return json.dumps(get_store().rqrag_loop_plan(phase=phase))


@mcp.tool()
def stele_ircot_cot_step(step: int, claim: str) -> str:
    """IRCoT CoT step."""
    return json.dumps(get_store().ircot_cot_step(step=step, claim=claim))


@mcp.tool()
def stele_ircot_retrieve_guided(step_id: str, k: int = 3) -> str:
    """IRCoT retrieve guided."""
    return json.dumps(
        get_store().ircot_retrieve_guided(step_id=step_id, k=k)
    )


@mcp.tool()
def stele_ircot_interleave(cot_steps: int, retrieves: int) -> str:
    """IRCoT interleave."""
    return json.dumps(
        get_store().ircot_interleave(
            cot_steps=cot_steps, retrieves=retrieves
        )
    )


@mcp.tool()
def stele_ircot_answer_ready(enough: bool) -> str:
    """IRCoT answer ready."""
    return json.dumps(get_store().ircot_answer_ready(enough=enough))


@mcp.tool()
def stele_ircot_hallucination_check(grounded: float) -> str:
    """IRCoT hallucination check."""
    return json.dumps(
        get_store().ircot_hallucination_check(grounded=grounded)
    )


@mcp.tool()
def stele_ircot_loop_plan(phase: str) -> str:
    """IRCoT loop plan."""
    return json.dumps(get_store().ircot_loop_plan(phase=phase))


@mcp.tool()
def stele_replug_retrieve_docs(query: str, k: int = 5) -> str:
    """REPLUG retrieve docs."""
    return json.dumps(get_store().replug_retrieve_docs(query=query, k=k))


@mcp.tool()
def stele_replug_prepend_doc(doc_id: str, context: str) -> str:
    """REPLUG prepend doc."""
    return json.dumps(
        get_store().replug_prepend_doc(doc_id=doc_id, context=context)
    )


@mcp.tool()
def stele_replug_ensemble_probs(packs: int) -> str:
    """REPLUG ensemble probs."""
    return json.dumps(get_store().replug_ensemble_probs(packs=packs))


@mcp.tool()
def stele_replug_supervise_retriever(lm_gain: float) -> str:
    """REPLUG supervise retriever."""
    return json.dumps(
        get_store().replug_supervise_retriever(lm_gain=lm_gain)
    )


@mcp.tool()
def stele_replug_blackbox_forward(pack_id: str) -> str:
    """REPLUG blackbox forward."""
    return json.dumps(get_store().replug_blackbox_forward(pack_id=pack_id))


@mcp.tool()
def stele_replug_loop_plan(phase: str) -> str:
    """REPLUG loop plan."""
    return json.dumps(get_store().replug_loop_plan(phase=phase))


@mcp.tool()
def stele_iterretgen_generate(iteration: int, draft: str) -> str:
    """Iter-RetGen generate."""
    return json.dumps(
        get_store().iterretgen_generate(iteration=iteration, draft=draft)
    )


@mcp.tool()
def stele_iterretgen_use_as_query(gen_id: str) -> str:
    """Iter-RetGen use as query."""
    return json.dumps(get_store().iterretgen_use_as_query(gen_id=gen_id))


@mcp.tool()
def stele_iterretgen_retrieve_next(query_from: str, k: int = 5) -> str:
    """Iter-RetGen retrieve next."""
    return json.dumps(
        get_store().iterretgen_retrieve_next(query_from=query_from, k=k)
    )


@mcp.tool()
def stele_iterretgen_iterate(round_n: int, max_rounds: int = 3) -> str:
    """Iter-RetGen iterate."""
    return json.dumps(
        get_store().iterretgen_iterate(
            round_n=round_n, max_rounds=max_rounds
        )
    )


@mcp.tool()
def stele_iterretgen_adapt_retriever(improve: bool) -> str:
    """Iter-RetGen adapt retriever."""
    return json.dumps(
        get_store().iterretgen_adapt_retriever(improve=improve)
    )


@mcp.tool()
def stele_iterretgen_loop_plan(phase: str) -> str:
    """Iter-RetGen loop plan."""
    return json.dumps(get_store().iterretgen_loop_plan(phase=phase))


@mcp.tool()
def stele_planrag_make_plan(question: str) -> str:
    """PlanRAG make plan."""
    return json.dumps(get_store().planrag_make_plan(question=question))


@mcp.tool()
def stele_planrag_analysis_query(plan_id: str, query: str) -> str:
    """PlanRAG analysis query."""
    return json.dumps(
        get_store().planrag_analysis_query(plan_id=plan_id, query=query)
    )


@mcp.tool()
def stele_planrag_retrieve_data(query_id: str, rows: int) -> str:
    """PlanRAG retrieve data."""
    return json.dumps(
        get_store().planrag_retrieve_data(query_id=query_id, rows=rows)
    )


@mcp.tool()
def stele_planrag_replan(need_replan: bool) -> str:
    """PlanRAG replan."""
    return json.dumps(get_store().planrag_replan(need_replan=need_replan))


@mcp.tool()
def stele_planrag_decide(ready: bool) -> str:
    """PlanRAG decide."""
    return json.dumps(get_store().planrag_decide(ready=ready))


@mcp.tool()
def stele_planrag_loop_plan(phase: str) -> str:
    """PlanRAG loop plan."""
    return json.dumps(get_store().planrag_loop_plan(phase=phase))


@mcp.tool()
def stele_rrr_rewrite_query(query: str) -> str:
    """RRR rewrite query."""
    return json.dumps(get_store().rrr_rewrite_query(query=query))


@mcp.tool()
def stele_rrr_retrieve(rewrite_id: str, k: int = 5) -> str:
    """RRR retrieve."""
    return json.dumps(get_store().rrr_retrieve(rewrite_id=rewrite_id, k=k))


@mcp.tool()
def stele_rrr_read(hits: int) -> str:
    """RRR read."""
    return json.dumps(get_store().rrr_read(hits=hits))


@mcp.tool()
def stele_rrr_reader_feedback(reward: float) -> str:
    """RRR reader feedback."""
    return json.dumps(get_store().rrr_reader_feedback(reward=reward))


@mcp.tool()
def stele_rrr_train_rewriter_plan(improve: bool) -> str:
    """RRR train rewriter plan."""
    return json.dumps(get_store().rrr_train_rewriter_plan(improve=improve))


@mcp.tool()
def stele_rrr_loop_plan(phase: str) -> str:
    """RRR loop plan."""
    return json.dumps(get_store().rrr_loop_plan(phase=phase))


@mcp.tool()
def stele_dsp_bootstrap_demo(task: str, n: int = 3) -> str:
    """DSP bootstrap demo."""
    return json.dumps(get_store().dsp_bootstrap_demo(task=task, n=n))


@mcp.tool()
def stele_dsp_search(query: str, k: int = 5) -> str:
    """DSP search."""
    return json.dumps(get_store().dsp_search(query=query, k=k))


@mcp.tool()
def stele_dsp_predict(grounded: bool) -> str:
    """DSP predict."""
    return json.dumps(get_store().dsp_predict(grounded=grounded))


@mcp.tool()
def stele_dsp_compose_program(stages: int) -> str:
    """DSP compose program."""
    return json.dumps(get_store().dsp_compose_program(stages=stages))


@mcp.tool()
def stele_dsp_multihop_hop(hop: int) -> str:
    """DSP multihop hop."""
    return json.dumps(get_store().dsp_multihop_hop(hop=hop))


@mcp.tool()
def stele_dsp_loop_plan(phase: str) -> str:
    """DSP loop plan."""
    return json.dumps(get_store().dsp_loop_plan(phase=phase))


@mcp.tool()
def stele_genread_generate_context(question: str) -> str:
    """GenRead generate context."""
    return json.dumps(
        get_store().genread_generate_context(question=question)
    )


@mcp.tool()
def stele_genread_ground_optional(ctx_id: str, use_retriever: bool) -> str:
    """GenRead ground optional."""
    return json.dumps(
        get_store().genread_ground_optional(
            ctx_id=ctx_id, use_retriever=use_retriever
        )
    )


@mcp.tool()
def stele_genread_answer(ctx_id: str) -> str:
    """GenRead answer."""
    return json.dumps(get_store().genread_answer(ctx_id=ctx_id))


@mcp.tool()
def stele_genread_compare_retrieve(gen_hits: int, retrieve_hits: int) -> str:
    """GenRead compare retrieve."""
    return json.dumps(
        get_store().genread_compare_retrieve(
            gen_hits=gen_hits, retrieve_hits=retrieve_hits
        )
    )


@mcp.tool()
def stele_genread_hybrid(generate: bool, retrieve: bool) -> str:
    """GenRead hybrid."""
    return json.dumps(
        get_store().genread_hybrid(generate=generate, retrieve=retrieve)
    )


@mcp.tool()
def stele_genread_loop_plan(phase: str) -> str:
    """GenRead loop plan."""
    return json.dumps(get_store().genread_loop_plan(phase=phase))


@mcp.tool()
def stele_selfask_followup(question: str, hop: int = 0) -> str:
    """Self-Ask followup."""
    return json.dumps(
        get_store().selfask_followup(question=question, hop=hop)
    )


@mcp.tool()
def stele_selfask_search_intercept(followup_id: str, k: int = 3) -> str:
    """Self-Ask search intercept."""
    return json.dumps(
        get_store().selfask_search_intercept(followup_id=followup_id, k=k)
    )


@mcp.tool()
def stele_selfask_compose_answer(followups: int) -> str:
    """Self-Ask compose answer."""
    return json.dumps(
        get_store().selfask_compose_answer(followups=followups)
    )


@mcp.tool()
def stele_selfask_stop(enough: bool) -> str:
    """Self-Ask stop."""
    return json.dumps(get_store().selfask_stop(enough=enough))


@mcp.tool()
def stele_selfask_demo_prompt(demos: int) -> str:
    """Self-Ask demo prompt."""
    return json.dumps(get_store().selfask_demo_prompt(demos=demos))


@mcp.tool()
def stele_selfask_loop_plan(phase: str) -> str:
    """Self-Ask loop plan."""
    return json.dumps(get_store().selfask_loop_plan(phase=phase))


@mcp.tool()
def stele_react_thought(step: int, text: str) -> str:
    """ReAct thought."""
    return json.dumps(get_store().react_thought(step=step, text=text))


@mcp.tool()
def stele_react_action(action: str, arg: str) -> str:
    """ReAct action."""
    return json.dumps(get_store().react_action(action=action, arg=arg))


@mcp.tool()
def stele_react_observe(observation: str) -> str:
    """ReAct observe."""
    return json.dumps(get_store().react_observe(observation=observation))


@mcp.tool()
def stele_react_finish(answer: str) -> str:
    """ReAct finish."""
    return json.dumps(get_store().react_finish(answer=answer))


@mcp.tool()
def stele_react_trajectory(steps: int) -> str:
    """ReAct trajectory."""
    return json.dumps(get_store().react_trajectory(steps=steps))


@mcp.tool()
def stele_react_loop_plan(phase: str) -> str:
    """ReAct loop plan."""
    return json.dumps(get_store().react_loop_plan(phase=phase))


@mcp.tool()
def stele_tog_init_entity(entity: str) -> str:
    """ToG init entity."""
    return json.dumps(get_store().tog_init_entity(entity=entity))


@mcp.tool()
def stele_tog_explore_neighbors(entity_id: str, width: int = 3) -> str:
    """ToG explore neighbors."""
    return json.dumps(
        get_store().tog_explore_neighbors(entity_id=entity_id, width=width)
    )


@mcp.tool()
def stele_tog_beam_prune(paths: int, keep: int) -> str:
    """ToG beam prune."""
    return json.dumps(get_store().tog_beam_prune(paths=paths, keep=keep))


@mcp.tool()
def stele_tog_path_score(path_id: str, score: float) -> str:
    """ToG path score."""
    return json.dumps(
        get_store().tog_path_score(path_id=path_id, score=score)
    )


@mcp.tool()
def stele_tog_answer_from_paths(path_count: int) -> str:
    """ToG answer from paths."""
    return json.dumps(
        get_store().tog_answer_from_paths(path_count=path_count)
    )


@mcp.tool()
def stele_tog_loop_plan(phase: str) -> str:
    """ToG loop plan."""
    return json.dumps(get_store().tog_loop_plan(phase=phase))


@mcp.tool()
def stele_tf_api_candidate(api: str, args: str) -> str:
    """Toolformer API candidate."""
    return json.dumps(get_store().tf_api_candidate(api=api, args=args))


@mcp.tool()
def stele_tf_filter_call(candidate_id: str, useful: bool) -> str:
    """Toolformer filter call."""
    return json.dumps(
        get_store().tf_filter_call(candidate_id=candidate_id, useful=useful)
    )


@mcp.tool()
def stele_tf_execute_proxy(api: str) -> str:
    """Toolformer execute proxy."""
    return json.dumps(get_store().tf_execute_proxy(api=api))


@mcp.tool()
def stele_tf_incorporate_result(result_id: str) -> str:
    """Toolformer incorporate result."""
    return json.dumps(
        get_store().tf_incorporate_result(result_id=result_id)
    )


@mcp.tool()
def stele_tf_demo_apis(count: int) -> str:
    """Toolformer demo APIs."""
    return json.dumps(get_store().tf_demo_apis(count=count))


@mcp.tool()
def stele_tf_loop_plan(phase: str) -> str:
    """Toolformer loop plan."""
    return json.dumps(get_store().tf_loop_plan(phase=phase))


@mcp.tool()
def stele_rx_trial_run(task: str, trial: int = 0) -> str:
    """Reflexion trial run."""
    return json.dumps(get_store().rx_trial_run(task=task, trial=trial))


@mcp.tool()
def stele_rx_evaluate(trial_id: str, success: bool) -> str:
    """Reflexion evaluate."""
    return json.dumps(
        get_store().rx_evaluate(trial_id=trial_id, success=success)
    )


@mcp.tool()
def stele_rx_verbal_reflect(trial_id: str, feedback: str) -> str:
    """Reflexion verbal reflect."""
    return json.dumps(
        get_store().rx_verbal_reflect(trial_id=trial_id, feedback=feedback)
    )


@mcp.tool()
def stele_rx_memory_store(reflection_id: str) -> str:
    """Reflexion memory store."""
    return json.dumps(
        get_store().rx_memory_store(reflection_id=reflection_id)
    )


@mcp.tool()
def stele_rx_next_trial(reflections: int) -> str:
    """Reflexion next trial."""
    return json.dumps(get_store().rx_next_trial(reflections=reflections))


@mcp.tool()
def stele_rx_loop_plan(phase: str) -> str:
    """Reflexion loop plan."""
    return json.dumps(get_store().rx_loop_plan(phase=phase))


@mcp.tool()
def stele_sc_sample_path(path_idx: int, answer: str) -> str:
    """Self-Consistency sample path."""
    return json.dumps(
        get_store().sc_sample_path(path_idx=path_idx, answer=answer)
    )


@mcp.tool()
def stele_sc_collect_answers(n: int) -> str:
    """Self-Consistency collect answers."""
    return json.dumps(get_store().sc_collect_answers(n=n))


@mcp.tool()
def stele_sc_majority_vote(votes_json: str) -> str:
    """Self-Consistency majority vote (votes as JSON object)."""
    votes = json.loads(votes_json)
    return json.dumps(get_store().sc_majority_vote(votes=votes))


@mcp.tool()
def stele_sc_marginalize(paths: int, unique_answers: int) -> str:
    """Self-Consistency marginalize."""
    return json.dumps(
        get_store().sc_marginalize(
            paths=paths, unique_answers=unique_answers
        )
    )


@mcp.tool()
def stele_sc_temperature(temp: float) -> str:
    """Self-Consistency temperature."""
    return json.dumps(get_store().sc_temperature(temp=temp))


@mcp.tool()
def stele_sc_loop_plan(phase: str) -> str:
    """Self-Consistency loop plan."""
    return json.dumps(get_store().sc_loop_plan(phase=phase))


@mcp.tool()
def stele_tot_propose(parent_id: str, text: str) -> str:
    """ToT propose."""
    return json.dumps(
        get_store().tot_propose(parent_id=parent_id, text=text)
    )


@mcp.tool()
def stele_tot_evaluate(node_id: str, score: float) -> str:
    """ToT evaluate."""
    return json.dumps(get_store().tot_evaluate(node_id=node_id, score=score))


@mcp.tool()
def stele_tot_expand(breadth: int, depth: int) -> str:
    """ToT expand."""
    return json.dumps(get_store().tot_expand(breadth=breadth, depth=depth))


@mcp.tool()
def stele_tot_backtrack(from_node: str) -> str:
    """ToT backtrack."""
    return json.dumps(get_store().tot_backtrack(from_node=from_node))


@mcp.tool()
def stele_tot_select_best(candidates: int) -> str:
    """ToT select best."""
    return json.dumps(get_store().tot_select_best(candidates=candidates))


@mcp.tool()
def stele_tot_loop_plan(phase: str) -> str:
    """ToT loop plan."""
    return json.dumps(get_store().tot_loop_plan(phase=phase))


@mcp.tool()
def stele_ltm_decompose(problem: str, n_subs: int) -> str:
    """LtM decompose."""
    return json.dumps(
        get_store().ltm_decompose(problem=problem, n_subs=n_subs)
    )


@mcp.tool()
def stele_ltm_solve_sub(decomp_id: str, sub_idx: int) -> str:
    """LtM solve sub."""
    return json.dumps(
        get_store().ltm_solve_sub(decomp_id=decomp_id, sub_idx=sub_idx)
    )


@mcp.tool()
def stele_ltm_carry_forward(answered: int) -> str:
    """LtM carry forward."""
    return json.dumps(get_store().ltm_carry_forward(answered=answered))


@mcp.tool()
def stele_ltm_compose_final(subs_done: int) -> str:
    """LtM compose final."""
    return json.dumps(get_store().ltm_compose_final(subs_done=subs_done))


@mcp.tool()
def stele_ltm_easy_to_hard(exemplars: int) -> str:
    """LtM easy to hard."""
    return json.dumps(get_store().ltm_easy_to_hard(exemplars=exemplars))


@mcp.tool()
def stele_ltm_loop_plan(phase: str) -> str:
    """LtM loop plan."""
    return json.dumps(get_store().ltm_loop_plan(phase=phase))


@mcp.tool()
def stele_got_add_thought(text: str) -> str:
    """GoT add thought."""
    return json.dumps(get_store().got_add_thought(text=text))


@mcp.tool()
def stele_got_link(src: str, dst: str) -> str:
    """GoT link."""
    return json.dumps(get_store().got_link(src=src, dst=dst))


@mcp.tool()
def stele_got_aggregate(inputs: int) -> str:
    """GoT aggregate."""
    return json.dumps(get_store().got_aggregate(inputs=inputs))


@mcp.tool()
def stele_got_feedback(vertex_id: str) -> str:
    """GoT feedback."""
    return json.dumps(get_store().got_feedback(vertex_id=vertex_id))


@mcp.tool()
def stele_got_score_graph(vertices: int, edges: int) -> str:
    """GoT score graph."""
    return json.dumps(
        get_store().got_score_graph(vertices=vertices, edges=edges)
    )


@mcp.tool()
def stele_got_loop_plan(phase: str) -> str:
    """GoT loop plan."""
    return json.dumps(get_store().got_loop_plan(phase=phase))


@mcp.tool()
def stele_pot_emit_program(problem: str, lang: str = "python") -> str:
    """PoT emit program."""
    return json.dumps(
        get_store().pot_emit_program(problem=problem, lang=lang)
    )


@mcp.tool()
def stele_pot_sandbox_run(program_id: str) -> str:
    """PoT sandbox run (proxy; no real exec)."""
    return json.dumps(get_store().pot_sandbox_run(program_id=program_id))


@mcp.tool()
def stele_pot_read_result(result_id: str) -> str:
    """PoT read result."""
    return json.dumps(get_store().pot_read_result(result_id=result_id))


@mcp.tool()
def stele_pot_self_consistency(samples: int) -> str:
    """PoT self-consistency."""
    return json.dumps(get_store().pot_self_consistency(samples=samples))


@mcp.tool()
def stele_pot_disentangle(compute_offloaded: bool) -> str:
    """PoT disentangle."""
    return json.dumps(
        get_store().pot_disentangle(compute_offloaded=compute_offloaded)
    )


@mcp.tool()
def stele_pot_loop_plan(phase: str) -> str:
    """PoT loop plan."""
    return json.dumps(get_store().pot_loop_plan(phase=phase))


@mcp.tool()
def stele_aot_load_algorithm(name: str) -> str:
    """AoT load algorithm."""
    return json.dumps(get_store().aot_load_algorithm(name=name))


@mcp.tool()
def stele_aot_explore_subtree(depth: int, branch: int) -> str:
    """AoT explore subtree."""
    return json.dumps(
        get_store().aot_explore_subtree(depth=depth, branch=branch)
    )


@mcp.tool()
def stele_aot_tunnel_vision(activate: bool) -> str:
    """AoT tunnel vision."""
    return json.dumps(get_store().aot_tunnel_vision(activate=activate))


@mcp.tool()
def stele_aot_query_budget(queries: int) -> str:
    """AoT query budget."""
    return json.dumps(get_store().aot_query_budget(queries=queries))


@mcp.tool()
def stele_aot_surpass_algo(intuition: bool) -> str:
    """AoT surpass algo."""
    return json.dumps(get_store().aot_surpass_algo(intuition=intuition))


@mcp.tool()
def stele_aot_loop_plan(phase: str) -> str:
    """AoT loop plan."""
    return json.dumps(get_store().aot_loop_plan(phase=phase))


@mcp.tool()
def stele_rap_world_state(state: str) -> str:
    """RAP world state (Reasoning via Planning; not RAPTOR)."""
    return json.dumps(get_store().rap_world_state(state=state))


@mcp.tool()
def stele_rap_expand(state_id: str, actions: int) -> str:
    """RAP expand."""
    return json.dumps(
        get_store().rap_expand(state_id=state_id, actions=actions)
    )


@mcp.tool()
def stele_rap_reward(state_id: str, reward: float) -> str:
    """RAP reward."""
    return json.dumps(
        get_store().rap_reward(state_id=state_id, reward=reward)
    )


@mcp.tool()
def stele_rap_select_path(visits: int) -> str:
    """RAP select path."""
    return json.dumps(get_store().rap_select_path(visits=visits))


@mcp.tool()
def stele_rap_balance(explore: float) -> str:
    """RAP balance."""
    return json.dumps(get_store().rap_balance(explore=explore))


@mcp.tool()
def stele_rap_loop_plan(phase: str) -> str:
    """RAP loop plan."""
    return json.dumps(get_store().rap_loop_plan(phase=phase))


@mcp.tool()
def stele_sot_emit_skeleton(question: str) -> str:
    """SoT emit skeleton."""
    return json.dumps(get_store().sot_emit_skeleton(question=question))


@mcp.tool()
def stele_sot_extract_points(skeleton_id: str, points: int) -> str:
    """SoT extract points."""
    return json.dumps(
        get_store().sot_extract_points(
            skeleton_id=skeleton_id, points=points
        )
    )


@mcp.tool()
def stele_sot_parallel_expand(points: int) -> str:
    """SoT parallel expand."""
    return json.dumps(get_store().sot_parallel_expand(points=points))


@mcp.tool()
def stele_sot_router(suitable: bool) -> str:
    """SoT router."""
    return json.dumps(get_store().sot_router(suitable=suitable))


@mcp.tool()
def stele_sot_latency_gain(sequential: int, parallel: int) -> str:
    """SoT latency gain."""
    return json.dumps(
        get_store().sot_latency_gain(
            sequential=sequential, parallel=parallel
        )
    )


@mcp.tool()
def stele_sot_loop_plan(phase: str) -> str:
    """SoT loop plan."""
    return json.dumps(get_store().sot_loop_plan(phase=phase))


@mcp.tool()
def stele_bot_distill_template(task: str) -> str:
    """BoT distill template."""
    return json.dumps(get_store().bot_distill_template(task=task))


@mcp.tool()
def stele_bot_retrieve_template(query: str) -> str:
    """BoT retrieve template."""
    return json.dumps(get_store().bot_retrieve_template(query=query))


@mcp.tool()
def stele_bot_instantiate(template_id: str) -> str:
    """BoT instantiate."""
    return json.dumps(get_store().bot_instantiate(template_id=template_id))


@mcp.tool()
def stele_bot_buffer_update(templates: int) -> str:
    """BoT buffer update."""
    return json.dumps(get_store().bot_buffer_update(templates=templates))


@mcp.tool()
def stele_bot_cost_ratio(multi_query: int, bot: int) -> str:
    """BoT cost ratio."""
    return json.dumps(
        get_store().bot_cost_ratio(multi_query=multi_query, bot=bot)
    )


@mcp.tool()
def stele_bot_loop_plan(phase: str) -> str:
    """BoT loop plan."""
    return json.dumps(get_store().bot_loop_plan(phase=phase))


@mcp.tool()
def stele_sd_select_modules(task: str, modules: int) -> str:
    """Self-Discover select modules."""
    return json.dumps(
        get_store().sd_select_modules(task=task, modules=modules)
    )


@mcp.tool()
def stele_sd_adapt(select_id: str) -> str:
    """Self-Discover adapt."""
    return json.dumps(get_store().sd_adapt(select_id=select_id))


@mcp.tool()
def stele_sd_implement(adapt_id: str, keys: int) -> str:
    """Self-Discover implement."""
    return json.dumps(
        get_store().sd_implement(adapt_id=adapt_id, keys=keys)
    )


@mcp.tool()
def stele_sd_apply_instance(structure_id: str) -> str:
    """Self-Discover apply instance."""
    return json.dumps(
        get_store().sd_apply_instance(structure_id=structure_id)
    )


@mcp.tool()
def stele_sd_compute_ratio(sc_calls: int, self_discover: int) -> str:
    """Self-Discover compute ratio."""
    return json.dumps(
        get_store().sd_compute_ratio(
            sc_calls=sc_calls, self_discover=self_discover
        )
    )


@mcp.tool()
def stele_sd_loop_plan(phase: str) -> str:
    """Self-Discover loop plan."""
    return json.dumps(get_store().sd_loop_plan(phase=phase))


@mcp.tool()
def stele_mp_break_task(query: str, pieces: int) -> str:
    """Meta-Prompting break task."""
    return json.dumps(
        get_store().mp_break_task(query=query, pieces=pieces)
    )


@mcp.tool()
def stele_mp_assign_expert(piece_idx: int, expert: str) -> str:
    """Meta-Prompting assign expert."""
    return json.dumps(
        get_store().mp_assign_expert(piece_idx=piece_idx, expert=expert)
    )


@mcp.tool()
def stele_mp_oversee(messages: int) -> str:
    """Meta-Prompting oversee."""
    return json.dumps(get_store().mp_oversee(messages=messages))


@mcp.tool()
def stele_mp_verify(claim: str) -> str:
    """Meta-Prompting verify."""
    return json.dumps(get_store().mp_verify(claim=claim))


@mcp.tool()
def stele_mp_task_agnostic(scaffold: bool) -> str:
    """Meta-Prompting task-agnostic."""
    return json.dumps(get_store().mp_task_agnostic(scaffold=scaffold))


@mcp.tool()
def stele_mp_loop_plan(phase: str) -> str:
    """Meta-Prompting loop plan."""
    return json.dumps(get_store().mp_loop_plan(phase=phase))


@mcp.tool()
def stele_qs_thought_bounds(start: str, end: str) -> str:
    """Quiet-STaR thought bounds."""
    return json.dumps(get_store().qs_thought_bounds(start=start, end=end))


@mcp.tool()
def stele_qs_parallel_sample(positions: int, thoughts: int) -> str:
    """Quiet-STaR parallel sample."""
    return json.dumps(
        get_store().qs_parallel_sample(
            positions=positions, thoughts=thoughts
        )
    )


@mcp.tool()
def stele_qs_mix_head(weight: float) -> str:
    """Quiet-STaR mix head."""
    return json.dumps(get_store().qs_mix_head(weight=weight))


@mcp.tool()
def stele_qs_hard_token_aid(hard_tokens: int, helped: int) -> str:
    """Quiet-STaR hard token aid."""
    return json.dumps(
        get_store().qs_hard_token_aid(
            hard_tokens=hard_tokens, helped=helped
        )
    )


@mcp.tool()
def stele_qs_zero_shot_flag(improved: bool) -> str:
    """Quiet-STaR zero-shot flag."""
    return json.dumps(get_store().qs_zero_shot_flag(improved=improved))


@mcp.tool()
def stele_qs_loop_plan(phase: str) -> str:
    """Quiet-STaR loop plan."""
    return json.dumps(get_store().qs_loop_plan(phase=phase))


@mcp.tool()
def stele_dep_decompose(task: str, subs: int) -> str:
    """Decomposed Prompting decompose."""
    return json.dumps(get_store().dep_decompose(task=task, subs=subs))


@mcp.tool()
def stele_dep_delegate(handler: str, sub_idx: int) -> str:
    """Decomposed Prompting delegate."""
    return json.dumps(
        get_store().dep_delegate(handler=handler, sub_idx=sub_idx)
    )


@mcp.tool()
def stele_dep_recurse(depth: int) -> str:
    """Decomposed Prompting recurse."""
    return json.dumps(get_store().dep_recurse(depth=depth))


@mcp.tool()
def stele_dep_swap_symbolic(module: str) -> str:
    """Decomposed Prompting swap symbolic."""
    return json.dumps(get_store().dep_swap_symbolic(module=module))


@mcp.tool()
def stele_dep_library_size(handlers: int) -> str:
    """Decomposed Prompting library size."""
    return json.dumps(get_store().dep_library_size(handlers=handlers))


@mcp.tool()
def stele_dep_loop_plan(phase: str) -> str:
    """Decomposed Prompting loop plan."""
    return json.dumps(get_store().dep_loop_plan(phase=phase))


@mcp.tool()
def stele_star_generate(question: str) -> str:
    """STaR generate."""
    return json.dumps(get_store().star_generate(question=question))


@mcp.tool()
def stele_star_filter_correct(gen_id: str, correct: bool) -> str:
    """STaR filter correct."""
    return json.dumps(
        get_store().star_filter_correct(gen_id=gen_id, correct=correct)
    )


@mcp.tool()
def stele_star_rationalize(question: str, answer: str) -> str:
    """STaR rationalize."""
    return json.dumps(
        get_store().star_rationalize(question=question, answer=answer)
    )


@mcp.tool()
def stele_star_finetune_proxy(examples: int) -> str:
    """STaR finetune proxy."""
    return json.dumps(get_store().star_finetune_proxy(examples=examples))


@mcp.tool()
def stele_star_bootstrap_round(round_n: int) -> str:
    """STaR bootstrap round."""
    return json.dumps(get_store().star_bootstrap_round(round_n=round_n))


@mcp.tool()
def stele_star_loop_plan(phase: str) -> str:
    """STaR loop plan."""
    return json.dumps(get_store().star_loop_plan(phase=phase))


@mcp.tool()
def stele_cr_propose(step: str) -> str:
    """Cumulative Reasoning propose."""
    return json.dumps(get_store().cr_propose(step=step))


@mcp.tool()
def stele_cr_verify(proposal_id: str, valid: bool) -> str:
    """Cumulative Reasoning verify."""
    return json.dumps(
        get_store().cr_verify(proposal_id=proposal_id, valid=valid)
    )


@mcp.tool()
def stele_cr_accumulate(accepted: int) -> str:
    """Cumulative Reasoning accumulate."""
    return json.dumps(get_store().cr_accumulate(accepted=accepted))


@mcp.tool()
def stele_cr_report(steps: int) -> str:
    """Cumulative Reasoning report."""
    return json.dumps(get_store().cr_report(steps=steps))


@mcp.tool()
def stele_cr_roles(roles: int = 3) -> str:
    """Cumulative Reasoning roles."""
    return json.dumps(get_store().cr_roles(roles=roles))


@mcp.tool()
def stele_cr_loop_plan(phase: str) -> str:
    """Cumulative Reasoning loop plan."""
    return json.dumps(get_store().cr_loop_plan(phase=phase))


@mcp.tool()
def stele_ps_devise_plan(problem: str, subtasks: int) -> str:
    """Plan-and-Solve devise plan."""
    return json.dumps(
        get_store().ps_devise_plan(problem=problem, subtasks=subtasks)
    )


@mcp.tool()
def stele_ps_execute(plan_id: str, step: int) -> str:
    """Plan-and-Solve execute."""
    return json.dumps(get_store().ps_execute(plan_id=plan_id, step=step))


@mcp.tool()
def stele_ps_plus_extract(variables: int) -> str:
    """Plan-and-Solve PS+ extract."""
    return json.dumps(get_store().ps_plus_extract(variables=variables))


@mcp.tool()
def stele_ps_calc_guard(careful: bool) -> str:
    """Plan-and-Solve calc guard."""
    return json.dumps(get_store().ps_calc_guard(careful=careful))


@mcp.tool()
def stele_ps_missing_step_fix(fixed: bool) -> str:
    """Plan-and-Solve missing-step fix."""
    return json.dumps(get_store().ps_missing_step_fix(fixed=fixed))


@mcp.tool()
def stele_ps_loop_plan(phase: str) -> str:
    """Plan-and-Solve loop plan."""
    return json.dumps(get_store().ps_loop_plan(phase=phase))


@mcp.tool()
def stele_php_base_answer(question: str) -> str:
    """PHP base answer."""
    return json.dumps(get_store().php_base_answer(question=question))


@mcp.tool()
def stele_php_emit_hint(answer_id: str, hint: str) -> str:
    """PHP emit hint."""
    return json.dumps(
        get_store().php_emit_hint(answer_id=answer_id, hint=hint)
    )


@mcp.tool()
def stele_php_reask(hints: int) -> str:
    """PHP reask."""
    return json.dumps(get_store().php_reask(hints=hints))


@mcp.tool()
def stele_php_stable_stop(same_twice: bool) -> str:
    """PHP stable stop."""
    return json.dumps(get_store().php_stable_stop(same_twice=same_twice))


@mcp.tool()
def stele_php_combine_sc(reduced_paths: bool) -> str:
    """PHP combine with self-consistency."""
    return json.dumps(
        get_store().php_combine_sc(reduced_paths=reduced_paths)
    )


@mcp.tool()
def stele_php_loop_plan(phase: str) -> str:
    """PHP loop plan."""
    return json.dumps(get_store().php_loop_plan(phase=phase))


@mcp.tool()
def stele_ac_programmer(requirement: str) -> str:
    """AgentCoder programmer."""
    return json.dumps(get_store().ac_programmer(requirement=requirement))


@mcp.tool()
def stele_ac_test_designer(requirement: str, cases: int) -> str:
    """AgentCoder test designer."""
    return json.dumps(
        get_store().ac_test_designer(requirement=requirement, cases=cases)
    )


@mcp.tool()
def stele_ac_test_executor(code_id: str, suite_id: str) -> str:
    """AgentCoder test executor."""
    return json.dumps(
        get_store().ac_test_executor(code_id=code_id, suite_id=suite_id)
    )


@mcp.tool()
def stele_ac_refine(code_id: str, feedback_id: str) -> str:
    """AgentCoder refine."""
    return json.dumps(
        get_store().ac_refine(code_id=code_id, feedback_id=feedback_id)
    )


@mcp.tool()
def stele_ac_pass_gate(all_pass: bool) -> str:
    """AgentCoder pass gate."""
    return json.dumps(get_store().ac_pass_gate(all_pass=all_pass))


@mcp.tool()
def stele_ac_loop_plan(phase: str) -> str:
    """AgentCoder loop plan."""
    return json.dumps(get_store().ac_loop_plan(phase=phase))


@mcp.tool()
def stele_pal_emit_program(problem: str, lang: str = "python") -> str:
    """PAL emit program."""
    return json.dumps(
        get_store().pal_emit_program(problem=problem, lang=lang)
    )


@mcp.tool()
def stele_pal_offload_solve(program_id: str) -> str:
    """PAL offload solve."""
    return json.dumps(get_store().pal_offload_solve(program_id=program_id))


@mcp.tool()
def stele_pal_read_answer(result_id: str) -> str:
    """PAL read answer."""
    return json.dumps(get_store().pal_read_answer(result_id=result_id))


@mcp.tool()
def stele_pal_decompose_only(llm_solves: bool) -> str:
    """PAL decompose-only flag."""
    return json.dumps(get_store().pal_decompose_only(llm_solves=llm_solves))


@mcp.tool()
def stele_pal_vs_cot(program_beats_text: bool) -> str:
    """PAL vs CoT flag."""
    return json.dumps(
        get_store().pal_vs_cot(program_beats_text=program_beats_text)
    )


@mcp.tool()
def stele_pal_loop_plan(phase: str) -> str:
    """PAL loop plan."""
    return json.dumps(get_store().pal_loop_plan(phase=phase))


@mcp.tool()
def stele_fcot_translate(query: str, symbolic: str) -> str:
    """Faithful CoT translate."""
    return json.dumps(
        get_store().fcot_translate(query=query, symbolic=symbolic)
    )


@mcp.tool()
def stele_fcot_solve(chain_id: str) -> str:
    """Faithful CoT solve."""
    return json.dumps(get_store().fcot_solve(chain_id=chain_id))


@mcp.tool()
def stele_fcot_faithfulness(chain_explains: bool) -> str:
    """Faithful CoT faithfulness."""
    return json.dumps(
        get_store().fcot_faithfulness(chain_explains=chain_explains)
    )


@mcp.tool()
def stele_fcot_interleave(nl_sl: bool) -> str:
    """Faithful CoT interleave."""
    return json.dumps(get_store().fcot_interleave(nl_sl=nl_sl))


@mcp.tool()
def stele_fcot_vs_cot(faithful_beats: bool) -> str:
    """Faithful CoT vs CoT."""
    return json.dumps(
        get_store().fcot_vs_cot(faithful_beats=faithful_beats)
    )


@mcp.tool()
def stele_fcot_loop_plan(phase: str) -> str:
    """Faithful CoT loop plan."""
    return json.dumps(get_store().fcot_loop_plan(phase=phase))


@mcp.tool()
def stele_lats_expand(state: str, actions: int) -> str:
    """LATS expand."""
    return json.dumps(
        get_store().lats_expand(state=state, actions=actions)
    )


@mcp.tool()
def stele_lats_value(node_id: str, score: float) -> str:
    """LATS value."""
    return json.dumps(get_store().lats_value(node_id=node_id, score=score))


@mcp.tool()
def stele_lats_reflect(node_id: str, feedback: str) -> str:
    """LATS reflect."""
    return json.dumps(
        get_store().lats_reflect(node_id=node_id, feedback=feedback)
    )


@mcp.tool()
def stele_lats_select(node_id: str) -> str:
    """LATS select."""
    return json.dumps(get_store().lats_select(node_id=node_id))


@mcp.tool()
def stele_lats_env_feedback(useful: bool) -> str:
    """LATS env feedback."""
    return json.dumps(get_store().lats_env_feedback(useful=useful))


@mcp.tool()
def stele_lats_loop_plan(phase: str) -> str:
    """LATS loop plan."""
    return json.dumps(get_store().lats_loop_plan(phase=phase))


@mcp.tool()
def stele_voy_curriculum(level: int, task: str) -> str:
    """Voyager curriculum."""
    return json.dumps(
        get_store().voy_curriculum(level=level, task=task)
    )


@mcp.tool()
def stele_voy_skill_store(name: str, code_ref: str) -> str:
    """Voyager skill store."""
    return json.dumps(
        get_store().voy_skill_store(name=name, code_ref=code_ref)
    )


@mcp.tool()
def stele_voy_skill_retrieve(query: str) -> str:
    """Voyager skill retrieve."""
    return json.dumps(get_store().voy_skill_retrieve(query=query))


@mcp.tool()
def stele_voy_self_verify(skill_id: str, passed: bool) -> str:
    """Voyager self-verify."""
    return json.dumps(
        get_store().voy_self_verify(skill_id=skill_id, passed=passed)
    )


@mcp.tool()
def stele_voy_compose(skills: int) -> str:
    """Voyager compose."""
    return json.dumps(get_store().voy_compose(skills=skills))


@mcp.tool()
def stele_voy_loop_plan(phase: str) -> str:
    """Voyager loop plan."""
    return json.dumps(get_store().voy_loop_plan(phase=phase))


@mcp.tool()
def stele_rewoo_plan(task: str, steps: int) -> str:
    """ReWOO plan."""
    return json.dumps(get_store().rewoo_plan(task=task, steps=steps))


@mcp.tool()
def stele_rewoo_worker(plan_id: str, step: int) -> str:
    """ReWOO worker."""
    return json.dumps(
        get_store().rewoo_worker(plan_id=plan_id, step=step)
    )


@mcp.tool()
def stele_rewoo_solver(plan_id: str, evidence: int) -> str:
    """ReWOO solver."""
    return json.dumps(
        get_store().rewoo_solver(plan_id=plan_id, evidence=evidence)
    )


@mcp.tool()
def stele_rewoo_decouple(from_observation: bool) -> str:
    """ReWOO decouple."""
    return json.dumps(
        get_store().rewoo_decouple(from_observation=from_observation)
    )


@mcp.tool()
def stele_rewoo_token_save(reduced: bool) -> str:
    """ReWOO token save."""
    return json.dumps(get_store().rewoo_token_save(reduced=reduced))


@mcp.tool()
def stele_rewoo_loop_plan(phase: str) -> str:
    """ReWOO loop plan."""
    return json.dumps(get_store().rewoo_loop_plan(phase=phase))


@mcp.tool()
def stele_critic_draft(question: str) -> str:
    """CRITIC draft."""
    return json.dumps(get_store().critic_draft(question=question))


@mcp.tool()
def stele_critic_tool_check(draft_id: str, tool: str) -> str:
    """CRITIC tool check."""
    return json.dumps(
        get_store().critic_tool_check(draft_id=draft_id, tool=tool)
    )


@mcp.tool()
def stele_critic_revise(draft_id: str, critique_id: str) -> str:
    """CRITIC revise."""
    return json.dumps(
        get_store().critic_revise(
            draft_id=draft_id, critique_id=critique_id
        )
    )


@mcp.tool()
def stele_critic_iterate(rounds: int) -> str:
    """CRITIC iterate."""
    return json.dumps(get_store().critic_iterate(rounds=rounds))


@mcp.tool()
def stele_critic_stop(satisfied: bool) -> str:
    """CRITIC stop."""
    return json.dumps(get_store().critic_stop(satisfied=satisfied))


@mcp.tool()
def stele_critic_loop_plan(phase: str) -> str:
    """CRITIC loop plan."""
    return json.dumps(get_store().critic_loop_plan(phase=phase))


@mcp.tool()
def stele_dv_natural_program(claim: str, steps: int) -> str:
    """Deductive Natural Program."""
    return json.dumps(
        get_store().dv_natural_program(claim=claim, steps=steps)
    )


@mcp.tool()
def stele_dv_step_verify(program_id: str, step: int) -> str:
    """Deductive step verify."""
    return json.dumps(
        get_store().dv_step_verify(program_id=program_id, step=step)
    )


@mcp.tool()
def stele_dv_premise_scope(premises: int) -> str:
    """Deductive premise scope."""
    return json.dumps(get_store().dv_premise_scope(premises=premises))


@mcp.tool()
def stele_dv_unanimity(all_pass: bool) -> str:
    """Deductive unanimity."""
    return json.dumps(get_store().dv_unanimity(all_pass=all_pass))


@mcp.tool()
def stele_dv_ground(grounded: bool) -> str:
    """Deductive ground."""
    return json.dumps(get_store().dv_ground(grounded=grounded))


@mcp.tool()
def stele_dv_loop_plan(phase: str) -> str:
    """Deductive loop plan."""
    return json.dumps(get_store().dv_loop_plan(phase=phase))


@mcp.tool()
def stele_hgpt_plan(request: str, tasks: int) -> str:
    """HuggingGPT plan."""
    return json.dumps(get_store().hgpt_plan(request=request, tasks=tasks))


@mcp.tool()
def stele_hgpt_select(plan_id: str, model: str) -> str:
    """HuggingGPT select."""
    return json.dumps(
        get_store().hgpt_select(plan_id=plan_id, model=model)
    )


@mcp.tool()
def stele_hgpt_execute(selection_id: str) -> str:
    """HuggingGPT execute."""
    return json.dumps(get_store().hgpt_execute(selection_id=selection_id))


@mcp.tool()
def stele_hgpt_summarize(results: int) -> str:
    """HuggingGPT summarize."""
    return json.dumps(get_store().hgpt_summarize(results=results))


@mcp.tool()
def stele_hgpt_modality(modalities: int) -> str:
    """HuggingGPT modality."""
    return json.dumps(get_store().hgpt_modality(modalities=modalities))


@mcp.tool()
def stele_hgpt_loop_plan(phase: str) -> str:
    """HuggingGPT loop plan."""
    return json.dumps(get_store().hgpt_loop_plan(phase=phase))


@mcp.tool()
def stele_mad_propose(agent: str, answer: str) -> str:
    """Multiagent Debate propose."""
    return json.dumps(get_store().mad_propose(agent=agent, answer=answer))


@mcp.tool()
def stele_mad_debate(round_n: int, agents: int) -> str:
    """Multiagent Debate round."""
    return json.dumps(
        get_store().mad_debate(round_n=round_n, agents=agents)
    )


@mcp.tool()
def stele_mad_critique(proposal_id: str, critique: str) -> str:
    """Multiagent Debate critique."""
    return json.dumps(
        get_store().mad_critique(
            proposal_id=proposal_id, critique=critique
        )
    )


@mcp.tool()
def stele_mad_converge(common: bool) -> str:
    """Multiagent Debate converge."""
    return json.dumps(get_store().mad_converge(common=common))


@mcp.tool()
def stele_mad_factuality(improved: bool) -> str:
    """Multiagent Debate factuality."""
    return json.dumps(get_store().mad_factuality(improved=improved))


@mcp.tool()
def stele_mad_loop_plan(phase: str) -> str:
    """Multiagent Debate loop plan."""
    return json.dumps(get_store().mad_loop_plan(phase=phase))


@mcp.tool()
def stele_autocot_cluster(questions: int, clusters: int) -> str:
    """Auto-CoT cluster."""
    return json.dumps(
        get_store().autocot_cluster(questions=questions, clusters=clusters)
    )


@mcp.tool()
def stele_autocot_sample(cluster_id: str) -> str:
    """Auto-CoT sample."""
    return json.dumps(get_store().autocot_sample(cluster_id=cluster_id))


@mcp.tool()
def stele_autocot_generate(demo_id: str) -> str:
    """Auto-CoT generate."""
    return json.dumps(get_store().autocot_generate(demo_id=demo_id))


@mcp.tool()
def stele_autocot_heuristic(max_steps: int) -> str:
    """Auto-CoT heuristic."""
    return json.dumps(get_store().autocot_heuristic(max_steps=max_steps))


@mcp.tool()
def stele_autocot_diversity(diverse: bool) -> str:
    """Auto-CoT diversity."""
    return json.dumps(get_store().autocot_diversity(diverse=diverse))


@mcp.tool()
def stele_autocot_loop_plan(phase: str) -> str:
    """Auto-CoT loop plan."""
    return json.dumps(get_store().autocot_loop_plan(phase=phase))


@mcp.tool()
def stele_camel_roles(user_role: str, assistant_role: str) -> str:
    """CAMEL roles."""
    return json.dumps(
        get_store().camel_roles(
            user_role=user_role, assistant_role=assistant_role
        )
    )


@mcp.tool()
def stele_camel_inception(role_id: str, task: str) -> str:
    """CAMEL inception."""
    return json.dumps(
        get_store().camel_inception(role_id=role_id, task=task)
    )


@mcp.tool()
def stele_camel_turn(inception_id: str, speaker: str) -> str:
    """CAMEL turn."""
    return json.dumps(
        get_store().camel_turn(inception_id=inception_id, speaker=speaker)
    )


@mcp.tool()
def stele_camel_complete(done: bool) -> str:
    """CAMEL complete."""
    return json.dumps(get_store().camel_complete(done=done))


@mcp.tool()
def stele_camel_society(agents: int) -> str:
    """CAMEL society."""
    return json.dumps(get_store().camel_society(agents=agents))


@mcp.tool()
def stele_camel_loop_plan(phase: str) -> str:
    """CAMEL loop plan."""
    return json.dumps(get_store().camel_loop_plan(phase=phase))


@mcp.tool()
def stele_cham_inventory(tools: int) -> str:
    """Chameleon inventory."""
    return json.dumps(get_store().cham_inventory(tools=tools))


@mcp.tool()
def stele_cham_plan(task: str, modules: int) -> str:
    """Chameleon plan."""
    return json.dumps(get_store().cham_plan(task=task, modules=modules))


@mcp.tool()
def stele_cham_compose(plan_id: str, module: str) -> str:
    """Chameleon compose."""
    return json.dumps(
        get_store().cham_compose(plan_id=plan_id, module=module)
    )


@mcp.tool()
def stele_cham_execute(plan_id: str) -> str:
    """Chameleon execute."""
    return json.dumps(get_store().cham_execute(plan_id=plan_id))


@mcp.tool()
def stele_cham_constraint(inferred: bool) -> str:
    """Chameleon constraint."""
    return json.dumps(get_store().cham_constraint(inferred=inferred))


@mcp.tool()
def stele_cham_loop_plan(phase: str) -> str:
    """Chameleon loop plan."""
    return json.dumps(get_store().cham_loop_plan(phase=phase))


@mcp.tool()
def stele_rot_trigger(token: str) -> str:
    """RoT trigger."""
    return json.dumps(get_store().rot_trigger(token=token))


@mcp.tool()
def stele_rot_divide(problem: str, parts: int) -> str:
    """RoT divide."""
    return json.dumps(
        get_store().rot_divide(problem=problem, parts=parts)
    )


@mcp.tool()
def stele_rot_conquer(divide_id: str, part: int) -> str:
    """RoT conquer."""
    return json.dumps(
        get_store().rot_conquer(divide_id=divide_id, part=part)
    )


@mcp.tool()
def stele_rot_merge(parts: int) -> str:
    """RoT merge."""
    return json.dumps(get_store().rot_merge(parts=parts))


@mcp.tool()
def stele_rot_context_limit(within_limit: bool) -> str:
    """RoT context limit."""
    return json.dumps(
        get_store().rot_context_limit(within_limit=within_limit)
    )


@mcp.tool()
def stele_rot_loop_plan(phase: str) -> str:
    """RoT loop plan."""
    return json.dumps(get_store().rot_loop_plan(phase=phase))


@mcp.tool()
def stele_ap_sample(question: str, k: int) -> str:
    """Active-Prompt sample."""
    return json.dumps(get_store().ap_sample(question=question, k=k))


@mcp.tool()
def stele_ap_uncertainty(sample_id: str, score: float) -> str:
    """Active-Prompt uncertainty."""
    return json.dumps(
        get_store().ap_uncertainty(sample_id=sample_id, score=score)
    )


@mcp.tool()
def stele_ap_select(top_n: int) -> str:
    """Active-Prompt select."""
    return json.dumps(get_store().ap_select(top_n=top_n))


@mcp.tool()
def stele_ap_annotate(question_id: str, cot: str) -> str:
    """Active-Prompt annotate."""
    return json.dumps(
        get_store().ap_annotate(question_id=question_id, cot=cot)
    )


@mcp.tool()
def stele_ap_pool(size: int) -> str:
    """Active-Prompt pool."""
    return json.dumps(get_store().ap_pool(size=size))


@mcp.tool()
def stele_ap_loop_plan(phase: str) -> str:
    """Active-Prompt loop plan."""
    return json.dumps(get_store().ap_loop_plan(phase=phase))


@mcp.tool()
def stele_ana_recall(problem: str) -> str:
    """Analogical recall."""
    return json.dumps(get_store().ana_recall(problem=problem))


@mcp.tool()
def stele_ana_knowledge(problem: str, facts: int) -> str:
    """Analogical knowledge."""
    return json.dumps(
        get_store().ana_knowledge(problem=problem, facts=facts)
    )


@mcp.tool()
def stele_ana_solve(exemplar_id: str) -> str:
    """Analogical solve."""
    return json.dumps(get_store().ana_solve(exemplar_id=exemplar_id))


@mcp.tool()
def stele_ana_adapt(tailored: bool) -> str:
    """Analogical adapt."""
    return json.dumps(get_store().ana_adapt(tailored=tailored))


@mcp.tool()
def stele_ana_no_label(needs_labels: bool) -> str:
    """Analogical no-label flag."""
    return json.dumps(get_store().ana_no_label(needs_labels=needs_labels))


@mcp.tool()
def stele_ana_loop_plan(phase: str) -> str:
    """Analogical loop plan."""
    return json.dumps(get_store().ana_loop_plan(phase=phase))


@mcp.tool()
def stele_cbp_score(steps: int) -> str:
    """Complexity-Based score."""
    return json.dumps(get_store().cbp_score(steps=steps))


@mcp.tool()
def stele_cbp_select(min_steps: int, exemplars: int) -> str:
    """Complexity-Based select."""
    return json.dumps(
        get_store().cbp_select(min_steps=min_steps, exemplars=exemplars)
    )


@mcp.tool()
def stele_cbp_sample_chains(n: int) -> str:
    """Complexity-Based sample chains."""
    return json.dumps(get_store().cbp_sample_chains(n=n))


@mcp.tool()
def stele_cbp_vote_complex(prefer_complex: bool) -> str:
    """Complexity-Based vote."""
    return json.dumps(
        get_store().cbp_vote_complex(prefer_complex=prefer_complex)
    )


@mcp.tool()
def stele_cbp_robust(under_shift: bool) -> str:
    """Complexity-Based robust."""
    return json.dumps(get_store().cbp_robust(under_shift=under_shift))


@mcp.tool()
def stele_cbp_loop_plan(phase: str) -> str:
    """Complexity-Based loop plan."""
    return json.dumps(get_store().cbp_loop_plan(phase=phase))


@mcp.tool()
def stele_sb_abstract(instance: str) -> str:
    """Step-Back abstract."""
    return json.dumps(get_store().sb_abstract(instance=instance))


@mcp.tool()
def stele_sb_principle(concept_id: str, principle: str) -> str:
    """Step-Back principle."""
    return json.dumps(
        get_store().sb_principle(
            concept_id=concept_id, principle=principle
        )
    )


@mcp.tool()
def stele_sb_reason(principle_id: str) -> str:
    """Step-Back reason."""
    return json.dumps(get_store().sb_reason(principle_id=principle_id))


@mcp.tool()
def stele_sb_path(correct_path: bool) -> str:
    """Step-Back path."""
    return json.dumps(get_store().sb_path(correct_path=correct_path))


@mcp.tool()
def stele_sb_detail_trap(escaped: bool) -> str:
    """Step-Back detail trap."""
    return json.dumps(get_store().sb_detail_trap(escaped=escaped))


@mcp.tool()
def stele_sb_loop_plan(phase: str) -> str:
    """Step-Back loop plan."""
    return json.dumps(get_store().sb_loop_plan(phase=phase))


@mcp.tool()
def stele_mmcot_fuse(text: str, vision_ref: str) -> str:
    """Multimodal-CoT fuse."""
    return json.dumps(
        get_store().mmcot_fuse(text=text, vision_ref=vision_ref)
    )


@mcp.tool()
def stele_mmcot_rationale(fuse_id: str) -> str:
    """Multimodal-CoT rationale."""
    return json.dumps(get_store().mmcot_rationale(fuse_id=fuse_id))


@mcp.tool()
def stele_mmcot_infer(rationale_id: str) -> str:
    """Multimodal-CoT infer."""
    return json.dumps(get_store().mmcot_infer(rationale_id=rationale_id))


@mcp.tool()
def stele_mmcot_hallucination(mitigated: bool) -> str:
    """Multimodal-CoT hallucination flag."""
    return json.dumps(
        get_store().mmcot_hallucination(mitigated=mitigated)
    )


@mcp.tool()
def stele_mmcot_separate(two_stage: bool) -> str:
    """Multimodal-CoT separate stages."""
    return json.dumps(get_store().mmcot_separate(two_stage=two_stage))


@mcp.tool()
def stele_mmcot_loop_plan(phase: str) -> str:
    """Multimodal-CoT loop plan."""
    return json.dumps(get_store().mmcot_loop_plan(phase=phase))


@mcp.tool()
def stele_mai_abduce(claim: str, because: str) -> str:
    """Maieutic abduce."""
    return json.dumps(
        get_store().mai_abduce(claim=claim, because=because)
    )


@mcp.tool()
def stele_mai_recurse(node_id: str, depth: int) -> str:
    """Maieutic recurse."""
    return json.dumps(
        get_store().mai_recurse(node_id=node_id, depth=depth)
    )


@mcp.tool()
def stele_mai_sat(relations: int) -> str:
    """Maieutic SAT."""
    return json.dumps(get_store().mai_sat(relations=relations))


@mcp.tool()
def stele_mai_consistent(consistent: bool) -> str:
    """Maieutic consistent."""
    return json.dumps(get_store().mai_consistent(consistent=consistent))


@mcp.tool()
def stele_mai_unreliable(tolerate: bool) -> str:
    """Maieutic unreliable tolerance."""
    return json.dumps(get_store().mai_unreliable(tolerate=tolerate))


@mcp.tool()
def stele_mai_loop_plan(phase: str) -> str:
    """Maieutic loop plan."""
    return json.dumps(get_store().mai_loop_plan(phase=phase))


@mcp.tool()
def stele_sr_generate(draft: str) -> str:
    """Self-Refine generate."""
    return json.dumps(get_store().sr_generate(draft=draft))


@mcp.tool()
def stele_sr_feedback(gen_id: str) -> str:
    """Self-Refine feedback."""
    return json.dumps(get_store().sr_feedback(gen_id=gen_id))


@mcp.tool()
def stele_sr_refine(gen_id: str, feedback_id: str) -> str:
    """Self-Refine refine."""
    return json.dumps(
        get_store().sr_refine(gen_id=gen_id, feedback_id=feedback_id)
    )


@mcp.tool()
def stele_sr_iterate(rounds: int) -> str:
    """Self-Refine iterate."""
    return json.dumps(get_store().sr_iterate(rounds=rounds))


@mcp.tool()
def stele_sr_no_train(no_rl: bool) -> str:
    """Self-Refine no-train flag."""
    return json.dumps(get_store().sr_no_train(no_rl=no_rl))


@mcp.tool()
def stele_sr_loop_plan(phase: str) -> str:
    """Self-Refine loop plan."""
    return json.dumps(get_store().sr_loop_plan(phase=phase))


@mcp.tool()
def stele_mcp_recognize(knowledge: str) -> str:
    """Metacognitive recognize."""
    return json.dumps(get_store().mcp_recognize(knowledge=knowledge))


@mcp.tool()
def stele_mcp_interpret(recognize_id: str) -> str:
    """Metacognitive interpret."""
    return json.dumps(get_store().mcp_interpret(recognize_id=recognize_id))


@mcp.tool()
def stele_mcp_reevaluate(interpret_id: str) -> str:
    """Metacognitive reevaluate."""
    return json.dumps(get_store().mcp_reevaluate(interpret_id=interpret_id))


@mcp.tool()
def stele_mcp_confidence(score: int) -> str:
    """Metacognitive confidence."""
    return json.dumps(get_store().mcp_confidence(score=score))


@mcp.tool()
def stele_mcp_justify(justified: bool) -> str:
    """Metacognitive justify."""
    return json.dumps(get_store().mcp_justify(justified=justified))


@mcp.tool()
def stele_mcp_loop_plan(phase: str) -> str:
    """Metacognitive loop plan."""
    return json.dumps(get_store().mcp_loop_plan(phase=phase))


@mcp.tool()
def stele_thot_segment(context: str, pieces: int) -> str:
    """Thread of Thought segment."""
    return json.dumps(
        get_store().thot_segment(context=context, pieces=pieces)
    )


@mcp.tool()
def stele_thot_analyze(segment_id: str) -> str:
    """Thread of Thought analyze."""
    return json.dumps(get_store().thot_analyze(segment_id=segment_id))


@mcp.tool()
def stele_thot_select(analyze_id: str) -> str:
    """Thread of Thought select."""
    return json.dumps(get_store().thot_select(analyze_id=analyze_id))


@mcp.tool()
def stele_thot_synthesize(select_id: str) -> str:
    """Thread of Thought synthesize."""
    return json.dumps(get_store().thot_synthesize(select_id=select_id))


@mcp.tool()
def stele_thot_plug(plug_and_play: bool) -> str:
    """Thread of Thought plug flag."""
    return json.dumps(get_store().thot_plug(plug_and_play=plug_and_play))


@mcp.tool()
def stele_thot_loop_plan(phase: str) -> str:
    """Thread of Thought loop plan."""
    return json.dumps(get_store().thot_loop_plan(phase=phase))


@mcp.tool()
def stele_tprop_propose(problem: str) -> str:
    """Thought Propagation propose."""
    return json.dumps(get_store().tprop_propose(problem=problem))


@mcp.tool()
def stele_tprop_solve(propose_id: str) -> str:
    """Thought Propagation solve."""
    return json.dumps(get_store().tprop_solve(propose_id=propose_id))


@mcp.tool()
def stele_tprop_reuse(analog_id: str) -> str:
    """Thought Propagation reuse."""
    return json.dumps(get_store().tprop_reuse(analog_id=analog_id))


@mcp.tool()
def stele_tprop_amend(reuse_id: str) -> str:
    """Thought Propagation amend."""
    return json.dumps(get_store().tprop_amend(reuse_id=reuse_id))


@mcp.tool()
def stele_tprop_compat(plug_and_play: bool) -> str:
    """Thought Propagation compat flag."""
    return json.dumps(
        get_store().tprop_compat(plug_and_play=plug_and_play)
    )


@mcp.tool()
def stele_tprop_loop_plan(phase: str) -> str:
    """Thought Propagation loop plan."""
    return json.dumps(get_store().tprop_loop_plan(phase=phase))


@mcp.tool()
def stele_s2a_regenerate(context: str) -> str:
    """System 2 Attention regenerate."""
    return json.dumps(get_store().s2a_regenerate(context=context))


@mcp.tool()
def stele_s2a_attend(regen_id: str) -> str:
    """System 2 Attention attend."""
    return json.dumps(get_store().s2a_attend(regen_id=regen_id))


@mcp.tool()
def stele_s2a_respond(attend_id: str) -> str:
    """System 2 Attention respond."""
    return json.dumps(get_store().s2a_respond(attend_id=attend_id))


@mcp.tool()
def stele_s2a_factuality(score: int) -> str:
    """System 2 Attention factuality."""
    return json.dumps(get_store().s2a_factuality(score=score))


@mcp.tool()
def stele_s2a_sycophancy(reduced: bool) -> str:
    """System 2 Attention sycophancy flag."""
    return json.dumps(get_store().s2a_sycophancy(reduced=reduced))


@mcp.tool()
def stele_s2a_loop_plan(phase: str) -> str:
    """System 2 Attention loop plan."""
    return json.dumps(get_store().s2a_loop_plan(phase=phase))


@mcp.tool()
def stele_ccot_valid(demo: str) -> str:
    """Contrastive CoT valid demo."""
    return json.dumps(get_store().ccot_valid(demo=demo))


@mcp.tool()
def stele_ccot_invalid(demo: str) -> str:
    """Contrastive CoT invalid demo."""
    return json.dumps(get_store().ccot_invalid(demo=demo))


@mcp.tool()
def stele_ccot_contrast(valid_id: str, invalid_id: str) -> str:
    """Contrastive CoT contrast."""
    return json.dumps(
        get_store().ccot_contrast(valid_id=valid_id, invalid_id=invalid_id)
    )


@mcp.tool()
def stele_ccot_reason(contrast_id: str) -> str:
    """Contrastive CoT reason."""
    return json.dumps(get_store().ccot_reason(contrast_id=contrast_id))


@mcp.tool()
def stele_ccot_auto(construct: bool) -> str:
    """Contrastive CoT auto construct."""
    return json.dumps(get_store().ccot_auto(construct=construct))


@mcp.tool()
def stele_ccot_loop_plan(phase: str) -> str:
    """Contrastive CoT loop plan."""
    return json.dumps(get_store().ccot_loop_plan(phase=phase))


@mcp.tool()
def stele_tabcot_header(columns: str) -> str:
    """Tab-CoT header."""
    return json.dumps(get_store().tabcot_header(columns=columns))


@mcp.tool()
def stele_tabcot_row(header_id: str, step: int) -> str:
    """Tab-CoT row."""
    return json.dumps(
        get_store().tabcot_row(header_id=header_id, step=step)
    )


@mcp.tool()
def stele_tabcot_infer2d(rows: int) -> str:
    """Tab-CoT 2D infer."""
    return json.dumps(get_store().tabcot_infer2d(rows=rows))


@mcp.tool()
def stele_tabcot_extract(row_id: str) -> str:
    """Tab-CoT extract."""
    return json.dumps(get_store().tabcot_extract(row_id=row_id))


@mcp.tool()
def stele_tabcot_zeroshot(zero_shot: bool) -> str:
    """Tab-CoT zeroshot flag."""
    return json.dumps(get_store().tabcot_zeroshot(zero_shot=zero_shot))


@mcp.tool()
def stele_tabcot_loop_plan(phase: str) -> str:
    """Tab-CoT loop plan."""
    return json.dumps(get_store().tabcot_loop_plan(phase=phase))


@mcp.tool()
def stele_xot_mcts(problem: str) -> str:
    """XoT MCTS."""
    return json.dumps(get_store().xot_mcts(problem=problem))


@mcp.tool()
def stele_xot_revise(mcts_id: str) -> str:
    """XoT revise."""
    return json.dumps(get_store().xot_revise(mcts_id=mcts_id))


@mcp.tool()
def stele_xot_map(revise_id: str) -> str:
    """XoT map."""
    return json.dumps(get_store().xot_map(revise_id=revise_id))


@mcp.tool()
def stele_xot_penrose(defy: bool) -> str:
    """XoT penrose."""
    return json.dumps(get_store().xot_penrose(defy=defy))


@mcp.tool()
def stele_xot_flexible(multi_solution: bool) -> str:
    """XoT flexible flag."""
    return json.dumps(
        get_store().xot_flexible(multi_solution=multi_solution)
    )


@mcp.tool()
def stele_xot_loop_plan(phase: str) -> str:
    """XoT loop plan."""
    return json.dumps(get_store().xot_loop_plan(phase=phase))


@mcp.tool()
def stele_cove_draft(claim: str) -> str:
    """CoVe draft."""
    return json.dumps(get_store().cove_draft(claim=claim))


@mcp.tool()
def stele_cove_plan(draft_id: str) -> str:
    """CoVe plan."""
    return json.dumps(get_store().cove_plan(draft_id=draft_id))


@mcp.tool()
def stele_cove_answer(plan_id: str) -> str:
    """CoVe answer."""
    return json.dumps(get_store().cove_answer(plan_id=plan_id))


@mcp.tool()
def stele_cove_final(verify_id: str) -> str:
    """CoVe final."""
    return json.dumps(get_store().cove_final(verify_id=verify_id))


@mcp.tool()
def stele_cove_hallucination(reduced: bool) -> str:
    """CoVe hallucination flag."""
    return json.dumps(get_store().cove_hallucination(reduced=reduced))


@mcp.tool()
def stele_cove_loop_plan(phase: str) -> str:
    """CoVe loop plan."""
    return json.dumps(get_store().cove_loop_plan(phase=phase))


@mcp.tool()
def stele_ved_uncertain(consistency: int) -> str:
    """Verify-and-Edit uncertain."""
    return json.dumps(get_store().ved_uncertain(consistency=consistency))


@mcp.tool()
def stele_ved_search(query: str) -> str:
    """Verify-and-Edit search."""
    return json.dumps(get_store().ved_search(query=query))


@mcp.tool()
def stele_ved_edit(fact_id: str, rationale: str) -> str:
    """Verify-and-Edit edit."""
    return json.dumps(
        get_store().ved_edit(fact_id=fact_id, rationale=rationale)
    )


@mcp.tool()
def stele_ved_predict(edit_id: str) -> str:
    """Verify-and-Edit predict."""
    return json.dumps(get_store().ved_predict(edit_id=edit_id))


@mcp.tool()
def stele_ved_knowledge(enhanced: bool) -> str:
    """Verify-and-Edit knowledge flag."""
    return json.dumps(get_store().ved_knowledge(enhanced=enhanced))


@mcp.tool()
def stele_ved_loop_plan(phase: str) -> str:
    """Verify-and-Edit loop plan."""
    return json.dumps(get_store().ved_loop_plan(phase=phase))


@mcp.tool()
def stele_sve_forward(problem: str) -> str:
    """Self-Verification forward."""
    return json.dumps(get_store().sve_forward(problem=problem))


@mcp.tool()
def stele_sve_mask(candidate_id: str) -> str:
    """Self-Verification mask."""
    return json.dumps(get_store().sve_mask(candidate_id=candidate_id))


@mcp.tool()
def stele_sve_repredict(mask_id: str) -> str:
    """Self-Verification repredict."""
    return json.dumps(get_store().sve_repredict(mask_id=mask_id))


@mcp.tool()
def stele_sve_score(score: int) -> str:
    """Self-Verification score."""
    return json.dumps(get_store().sve_score(score=score))


@mcp.tool()
def stele_sve_select(pick_best: bool) -> str:
    """Self-Verification select."""
    return json.dumps(get_store().sve_select(pick_best=pick_best))


@mcp.tool()
def stele_sve_loop_plan(phase: str) -> str:
    """Self-Verification loop plan."""
    return json.dumps(get_store().sve_loop_plan(phase=phase))


@mcp.tool()
def stele_cod_sparse(source: str) -> str:
    """Chain of Density sparse."""
    return json.dumps(get_store().cod_sparse(source=source))


@mcp.tool()
def stele_cod_entities(sparse_id: str, count: int) -> str:
    """Chain of Density entities."""
    return json.dumps(
        get_store().cod_entities(sparse_id=sparse_id, count=count)
    )


@mcp.tool()
def stele_cod_fuse(entity_id: str) -> str:
    """Chain of Density fuse."""
    return json.dumps(get_store().cod_fuse(entity_id=entity_id))


@mcp.tool()
def stele_cod_length(fixed: bool) -> str:
    """Chain of Density length."""
    return json.dumps(get_store().cod_length(fixed=fixed))


@mcp.tool()
def stele_cod_tradeoff(prefer_dense: bool) -> str:
    """Chain of Density tradeoff."""
    return json.dumps(get_store().cod_tradeoff(prefer_dense=prefer_dense))


@mcp.tool()
def stele_cod_loop_plan(phase: str) -> str:
    """Chain of Density loop plan."""
    return json.dumps(get_store().cod_loop_plan(phase=phase))


@mcp.tool()
def stele_hsp_hint(problem: str) -> str:
    """HSP hint."""
    return json.dumps(get_store().hsp_hint(problem=problem))


@mcp.tool()
def stele_hsp_solve(hint_id: str) -> str:
    """HSP solve."""
    return json.dumps(get_store().hsp_solve(hint_id=hint_id))


@mcp.tool()
def stele_hsp_answer(solve_id: str) -> str:
    """HSP answer."""
    return json.dumps(get_store().hsp_answer(solve_id=solve_id))


@mcp.tool()
def stele_hsp_compose(base: str) -> str:
    """HSP compose."""
    return json.dumps(get_store().hsp_compose(base=base))


@mcp.tool()
def stele_hsp_quality(high_quality: bool) -> str:
    """HSP quality flag."""
    return json.dumps(get_store().hsp_quality(high_quality=high_quality))


@mcp.tool()
def stele_hsp_loop_plan(phase: str) -> str:
    """HSP loop plan."""
    return json.dumps(get_store().hsp_loop_plan(phase=phase))


@mcp.tool()
def stele_emo_stimulus(text: str) -> str:
    """EmotionPrompt stimulus."""
    return json.dumps(get_store().emo_stimulus(text=text))


@mcp.tool()
def stele_emo_append(prompt: str, stimulus_id: str) -> str:
    """EmotionPrompt append."""
    return json.dumps(
        get_store().emo_append(prompt=prompt, stimulus_id=stimulus_id)
    )


@mcp.tool()
def stele_emo_run(prompt_id: str) -> str:
    """EmotionPrompt run."""
    return json.dumps(get_store().emo_run(prompt_id=prompt_id))


@mcp.tool()
def stele_emo_truth(improved: bool) -> str:
    """EmotionPrompt truth."""
    return json.dumps(get_store().emo_truth(improved=improved))


@mcp.tool()
def stele_emo_psych(psychology: bool) -> str:
    """EmotionPrompt psych flag."""
    return json.dumps(get_store().emo_psych(psychology=psychology))


@mcp.tool()
def stele_emo_loop_plan(phase: str) -> str:
    """EmotionPrompt loop plan."""
    return json.dumps(get_store().emo_loop_plan(phase=phase))


@mcp.tool()
def stele_ape_propose(demos: str) -> str:
    """APE propose."""
    return json.dumps(get_store().ape_propose(demos=demos))


@mcp.tool()
def stele_ape_score(pool_id: str) -> str:
    """APE score."""
    return json.dumps(get_store().ape_score(pool_id=pool_id))


@mcp.tool()
def stele_ape_select(score_id: str) -> str:
    """APE select."""
    return json.dumps(get_store().ape_select(score_id=score_id))


@mcp.tool()
def stele_ape_steer(instr_id: str) -> str:
    """APE steer."""
    return json.dumps(get_store().ape_steer(instr_id=instr_id))


@mcp.tool()
def stele_ape_human(match_human: bool) -> str:
    """APE human-parity flag."""
    return json.dumps(get_store().ape_human(match_human=match_human))


@mcp.tool()
def stele_ape_loop_plan(phase: str) -> str:
    """APE loop plan."""
    return json.dumps(get_store().ape_loop_plan(phase=phase))


@mcp.tool()
def stele_pbr_init(task: str) -> str:
    """Promptbreeder init."""
    return json.dumps(get_store().pbr_init(task=task))


@mcp.tool()
def stele_pbr_mutate(pop_id: str) -> str:
    """Promptbreeder mutate."""
    return json.dumps(get_store().pbr_mutate(pop_id=pop_id))


@mcp.tool()
def stele_pbr_fitness(mut_id: str, score: int) -> str:
    """Promptbreeder fitness."""
    return json.dumps(get_store().pbr_fitness(mut_id=mut_id, score=score))


@mcp.tool()
def stele_pbr_diversity(maintain: bool) -> str:
    """Promptbreeder diversity."""
    return json.dumps(get_store().pbr_diversity(maintain=maintain))


@mcp.tool()
def stele_pbr_selfref(self_improve: bool) -> str:
    """Promptbreeder selfref flag."""
    return json.dumps(get_store().pbr_selfref(self_improve=self_improve))


@mcp.tool()
def stele_pbr_loop_plan(phase: str) -> str:
    """Promptbreeder loop plan."""
    return json.dumps(get_store().pbr_loop_plan(phase=phase))


@mcp.tool()
def stele_opro_meta(task: str) -> str:
    """OPRO meta."""
    return json.dumps(get_store().opro_meta(task=task))


@mcp.tool()
def stele_opro_propose(meta_id: str) -> str:
    """OPRO propose."""
    return json.dumps(get_store().opro_propose(meta_id=meta_id))


@mcp.tool()
def stele_opro_score(cand_id: str, score: int) -> str:
    """OPRO score."""
    return json.dumps(get_store().opro_score(cand_id=cand_id, score=score))


@mcp.tool()
def stele_opro_append(score_id: str) -> str:
    """OPRO append."""
    return json.dumps(get_store().opro_append(score_id=score_id))


@mcp.tool()
def stele_opro_best(beat_human: bool) -> str:
    """OPRO best-vs-human flag."""
    return json.dumps(get_store().opro_best(beat_human=beat_human))


@mcp.tool()
def stele_opro_loop_plan(phase: str) -> str:
    """OPRO loop plan."""
    return json.dumps(get_store().opro_loop_plan(phase=phase))


@mcp.tool()
def stele_evp_init(task: str) -> str:
    """EvoPrompt init."""
    return json.dumps(get_store().evp_init(task=task))


@mcp.tool()
def stele_evp_cross(pop_id: str) -> str:
    """EvoPrompt crossover."""
    return json.dumps(get_store().evp_cross(pop_id=pop_id))


@mcp.tool()
def stele_evp_mutate(cross_id: str) -> str:
    """EvoPrompt mutate."""
    return json.dumps(get_store().evp_mutate(cross_id=cross_id))


@mcp.tool()
def stele_evp_select(mut_id: str, score: int) -> str:
    """EvoPrompt select."""
    return json.dumps(get_store().evp_select(mut_id=mut_id, score=score))


@mcp.tool()
def stele_evp_ea(connect_ea: bool) -> str:
    """EvoPrompt EA-connect flag."""
    return json.dumps(get_store().evp_ea(connect_ea=connect_ea))


@mcp.tool()
def stele_evp_loop_plan(phase: str) -> str:
    """EvoPrompt loop plan."""
    return json.dumps(get_store().evp_loop_plan(phase=phase))


@mcp.tool()
def stele_ptg_gradient(prompt: str) -> str:
    """ProTeGi gradient."""
    return json.dumps(get_store().ptg_gradient(prompt=prompt))


@mcp.tool()
def stele_ptg_edit(grad_id: str) -> str:
    """ProTeGi edit."""
    return json.dumps(get_store().ptg_edit(grad_id=grad_id))


@mcp.tool()
def stele_ptg_beam(edit_id: str) -> str:
    """ProTeGi beam."""
    return json.dumps(get_store().ptg_beam(edit_id=edit_id))


@mcp.tool()
def stele_ptg_bandit(beam_id: str, score: int) -> str:
    """ProTeGi bandit."""
    return json.dumps(get_store().ptg_bandit(beam_id=beam_id, score=score))


@mcp.tool()
def stele_ptg_jailbreak(detect: bool) -> str:
    """ProTeGi jailbreak flag."""
    return json.dumps(get_store().ptg_jailbreak(detect=detect))


@mcp.tool()
def stele_ptg_loop_plan(phase: str) -> str:
    """ProTeGi loop plan."""
    return json.dumps(get_store().ptg_loop_plan(phase=phase))


@mcp.tool()
def stele_pag_state(prompt: str) -> str:
    """PromptAgent state."""
    return json.dumps(get_store().pag_state(prompt=prompt))


@mcp.tool()
def stele_pag_reflect(state_id: str) -> str:
    """PromptAgent reflect."""
    return json.dumps(get_store().pag_reflect(state_id=state_id))


@mcp.tool()
def stele_pag_expand(reflect_id: str) -> str:
    """PromptAgent expand."""
    return json.dumps(get_store().pag_expand(reflect_id=reflect_id))


@mcp.tool()
def stele_pag_backprop(expand_id: str, reward: int) -> str:
    """PromptAgent backprop."""
    return json.dumps(
        get_store().pag_backprop(expand_id=expand_id, reward=reward)
    )


@mcp.tool()
def stele_pag_expert(expert_level: bool) -> str:
    """PromptAgent expert flag."""
    return json.dumps(get_store().pag_expert(expert_level=expert_level))


@mcp.tool()
def stele_pag_loop_plan(phase: str) -> str:
    """PromptAgent loop plan."""
    return json.dumps(get_store().pag_loop_plan(phase=phase))


@mcp.tool()
def stele_mapo_posgrad(prompt: str) -> str:
    """MAPO positive gradient."""
    return json.dumps(get_store().mapo_posgrad(prompt=prompt))


@mcp.tool()
def stele_mapo_momentum(pos_id: str) -> str:
    """MAPO momentum."""
    return json.dumps(get_store().mapo_momentum(pos_id=pos_id))


@mcp.tool()
def stele_mapo_beam(mom_id: str) -> str:
    """MAPO beam."""
    return json.dumps(get_store().mapo_beam(mom_id=mom_id))


@mcp.tool()
def stele_mapo_ucb(beam_id: str, score: int) -> str:
    """MAPO UCB."""
    return json.dumps(get_store().mapo_ucb(beam_id=beam_id, score=score))


@mcp.tool()
def stele_mapo_faster(beat_protegi: bool) -> str:
    """MAPO vs-ProTeGi flag."""
    return json.dumps(get_store().mapo_faster(beat_protegi=beat_protegi))


@mcp.tool()
def stele_mapo_loop_plan(phase: str) -> str:
    """MAPO loop plan."""
    return json.dumps(get_store().mapo_loop_plan(phase=phase))


@mcp.tool()
def stele_grips_seed(instruction: str) -> str:
    """GrIPS seed."""
    return json.dumps(get_store().grips_seed(instruction=instruction))


@mcp.tool()
def stele_grips_edit(seed_id: str, op: str) -> str:
    """GrIPS edit."""
    return json.dumps(get_store().grips_edit(seed_id=seed_id, op=op))


@mcp.tool()
def stele_grips_score(edit_id: str, score: int) -> str:
    """GrIPS score."""
    return json.dumps(get_store().grips_score(edit_id=edit_id, score=score))


@mcp.tool()
def stele_grips_accept(score_id: str) -> str:
    """GrIPS accept."""
    return json.dumps(get_store().grips_accept(score_id=score_id))


@mcp.tool()
def stele_grips_api(api_tunable: bool) -> str:
    """GrIPS API-tunable flag."""
    return json.dumps(get_store().grips_api(api_tunable=api_tunable))


@mcp.tool()
def stele_grips_loop_plan(phase: str) -> str:
    """GrIPS loop plan."""
    return json.dumps(get_store().grips_loop_plan(phase=phase))


@mcp.tool()
def stele_tmpa_state(prompt: str, query: str) -> str:
    """TEMPERA state."""
    return json.dumps(get_store().tmpa_state(prompt=prompt, query=query))


@mcp.tool()
def stele_tmpa_act(state_id: str, component: str) -> str:
    """TEMPERA act."""
    return json.dumps(
        get_store().tmpa_act(state_id=state_id, component=component)
    )


@mcp.tool()
def stele_tmpa_reward(act_id: str, score: int) -> str:
    """TEMPERA reward."""
    return json.dumps(get_store().tmpa_reward(act_id=act_id, score=score))


@mcp.tool()
def stele_tmpa_adapt(reward_id: str) -> str:
    """TEMPERA adapt."""
    return json.dumps(get_store().tmpa_adapt(reward_id=reward_id))


@mcp.tool()
def stele_tmpa_efficiency(sample_efficient: bool) -> str:
    """TEMPERA efficiency flag."""
    return json.dumps(
        get_store().tmpa_efficiency(sample_efficient=sample_efficient)
    )


@mcp.tool()
def stele_tmpa_loop_plan(phase: str) -> str:
    """TEMPERA loop plan."""
    return json.dumps(get_store().tmpa_loop_plan(phase=phase))


@mcp.tool()
def stele_rlp_init(task: str) -> str:
    """RLPrompt init."""
    return json.dumps(get_store().rlp_init(task=task))


@mcp.tool()
def stele_rlp_sample(policy_id: str) -> str:
    """RLPrompt sample."""
    return json.dumps(get_store().rlp_sample(policy_id=policy_id))


@mcp.tool()
def stele_rlp_reward(sample_id: str, score: int) -> str:
    """RLPrompt reward."""
    return json.dumps(
        get_store().rlp_reward(sample_id=sample_id, score=score)
    )


@mcp.tool()
def stele_rlp_update(reward_id: str) -> str:
    """RLPrompt update."""
    return json.dumps(get_store().rlp_update(reward_id=reward_id))


@mcp.tool()
def stele_rlp_discrete(discrete: bool) -> str:
    """RLPrompt discrete flag."""
    return json.dumps(get_store().rlp_discrete(discrete=discrete))


@mcp.tool()
def stele_rlp_loop_plan(phase: str) -> str:
    """RLPrompt loop plan."""
    return json.dumps(get_store().rlp_loop_plan(phase=phase))


@mcp.tool()
def stele_aup_template(template: str) -> str:
    """AutoPrompt template."""
    return json.dumps(get_store().aup_template(template=template))


@mcp.tool()
def stele_aup_trigger(tmpl_id: str) -> str:
    """AutoPrompt trigger."""
    return json.dumps(get_store().aup_trigger(tmpl_id=tmpl_id))


@mcp.tool()
def stele_aup_search(trig_id: str) -> str:
    """AutoPrompt search."""
    return json.dumps(get_store().aup_search(trig_id=trig_id))


@mcp.tool()
def stele_aup_score(search_id: str, score: int) -> str:
    """AutoPrompt score."""
    return json.dumps(get_store().aup_score(search_id=search_id, score=score))


@mcp.tool()
def stele_aup_probe(parameter_free: bool) -> str:
    """AutoPrompt probe flag."""
    return json.dumps(get_store().aup_probe(parameter_free=parameter_free))


@mcp.tool()
def stele_aup_loop_plan(phase: str) -> str:
    """AutoPrompt loop plan."""
    return json.dumps(get_store().aup_loop_plan(phase=phase))


@mcp.tool()
def stele_pfx_task(task: str) -> str:
    """Prefix-Tuning task."""
    return json.dumps(get_store().pfx_task(task=task))


@mcp.tool()
def stele_pfx_prefix(task_id: str) -> str:
    """Prefix-Tuning prefix."""
    return json.dumps(get_store().pfx_prefix(task_id=task_id))


@mcp.tool()
def stele_pfx_optimize(prefix_id: str) -> str:
    """Prefix-Tuning optimize."""
    return json.dumps(get_store().pfx_optimize(prefix_id=prefix_id))


@mcp.tool()
def stele_pfx_generate(opt_id: str, score: int) -> str:
    """Prefix-Tuning generate."""
    return json.dumps(get_store().pfx_generate(opt_id=opt_id, score=score))


@mcp.tool()
def stele_pfx_freeze(freeze_lm: bool) -> str:
    """Prefix-Tuning freeze flag."""
    return json.dumps(get_store().pfx_freeze(freeze_lm=freeze_lm))


@mcp.tool()
def stele_pfx_loop_plan(phase: str) -> str:
    """Prefix-Tuning loop plan."""
    return json.dumps(get_store().pfx_loop_plan(phase=phase))


@mcp.tool()
def stele_ptv_deep(task: str) -> str:
    """P-Tuning v2 deep."""
    return json.dumps(get_store().ptv_deep(task=task))


@mcp.tool()
def stele_ptv_inject(deep_id: str) -> str:
    """P-Tuning v2 inject."""
    return json.dumps(get_store().ptv_inject(deep_id=deep_id))


@mcp.tool()
def stele_ptv_tune(inj_id: str) -> str:
    """P-Tuning v2 tune."""
    return json.dumps(get_store().ptv_tune(inj_id=inj_id))


@mcp.tool()
def stele_ptv_seqtag(tune_id: str, score: int) -> str:
    """P-Tuning v2 seqtag."""
    return json.dumps(get_store().ptv_seqtag(tune_id=tune_id, score=score))


@mcp.tool()
def stele_ptv_universal(match_finetune: bool) -> str:
    """P-Tuning v2 universal flag."""
    return json.dumps(
        get_store().ptv_universal(match_finetune=match_finetune)
    )


@mcp.tool()
def stele_ptv_loop_plan(phase: str) -> str:
    """P-Tuning v2 loop plan."""
    return json.dumps(get_store().ptv_loop_plan(phase=phase))


@mcp.tool()
def stele_ptl_soft(task: str) -> str:
    """Prompt Tuning soft."""
    return json.dumps(get_store().ptl_soft(task=task))


@mcp.tool()
def stele_ptl_prepend(soft_id: str) -> str:
    """Prompt Tuning prepend."""
    return json.dumps(get_store().ptl_prepend(soft_id=soft_id))


@mcp.tool()
def stele_ptl_optimize(prep_id: str) -> str:
    """Prompt Tuning optimize."""
    return json.dumps(get_store().ptl_optimize(prep_id=prep_id))


@mcp.tool()
def stele_ptl_scale(opt_id: str, score: int) -> str:
    """Prompt Tuning scale."""
    return json.dumps(get_store().ptl_scale(opt_id=opt_id, score=score))


@mcp.tool()
def stele_ptl_input_only(input_layer_only: bool) -> str:
    """Prompt Tuning input-only flag."""
    return json.dumps(
        get_store().ptl_input_only(input_layer_only=input_layer_only)
    )


@mcp.tool()
def stele_ptl_loop_plan(phase: str) -> str:
    """Prompt Tuning loop plan."""
    return json.dumps(get_store().ptl_loop_plan(phase=phase))


@mcp.tool()
def stele_msp_soft(query: str) -> str:
    """Soft Prompt Mixtures soft."""
    return json.dumps(get_store().msp_soft(query=query))


@mcp.tool()
def stele_msp_mix(soft_id: str) -> str:
    """Soft Prompt Mixtures mix."""
    return json.dumps(get_store().msp_mix(soft_id=soft_id))


@mcp.tool()
def stele_msp_ensemble(mix_id: str) -> str:
    """Soft Prompt Mixtures ensemble."""
    return json.dumps(get_store().msp_ensemble(mix_id=mix_id))


@mcp.tool()
def stele_msp_probe(ens_id: str, score: int) -> str:
    """Soft Prompt Mixtures probe."""
    return json.dumps(get_store().msp_probe(ens_id=ens_id, score=score))


@mcp.tool()
def stele_msp_underest(prior_underestimate: bool) -> str:
    """Soft Prompt Mixtures underestimate flag."""
    return json.dumps(
        get_store().msp_underest(prior_underestimate=prior_underestimate)
    )


@mcp.tool()
def stele_msp_loop_plan(phase: str) -> str:
    """Soft Prompt Mixtures loop plan."""
    return json.dumps(get_store().msp_loop_plan(phase=phase))


@mcp.tool()
def stele_spot_source(source_task: str) -> str:
    """SPoT source."""
    return json.dumps(get_store().spot_source(source_task=source_task))


@mcp.tool()
def stele_spot_init(src_id: str, target_task: str) -> str:
    """SPoT init."""
    return json.dumps(
        get_store().spot_init(src_id=src_id, target_task=target_task)
    )


@mcp.tool()
def stele_spot_embed(src_id: str) -> str:
    """SPoT embed."""
    return json.dumps(get_store().spot_embed(src_id=src_id))


@mcp.tool()
def stele_spot_retrieve(emb_id: str, score: int) -> str:
    """SPoT retrieve."""
    return json.dumps(get_store().spot_retrieve(emb_id=emb_id, score=score))


@mcp.tool()
def stele_spot_vs_tune(beat_model_tuning: bool) -> str:
    """SPoT vs model-tuning flag."""
    return json.dumps(
        get_store().spot_vs_tune(beat_model_tuning=beat_model_tuning)
    )


@mcp.tool()
def stele_spot_loop_plan(phase: str) -> str:
    """SPoT loop plan."""
    return json.dumps(get_store().spot_loop_plan(phase=phase))


@mcp.tool()
def stele_atm_source(source_task: str) -> str:
    """ATTEMPT source."""
    return json.dumps(get_store().atm_source(source_task=source_task))


@mcp.tool()
def stele_atm_target(target_task: str) -> str:
    """ATTEMPT target."""
    return json.dumps(get_store().atm_target(target_task=target_task))


@mcp.tool()
def stele_atm_attend(src_id: str, tgt_id: str) -> str:
    """ATTEMPT attend."""
    return json.dumps(get_store().atm_attend(src_id=src_id, tgt_id=tgt_id))


@mcp.tool()
def stele_atm_mix(attn_id: str, score: int) -> str:
    """ATTEMPT mix."""
    return json.dumps(get_store().atm_mix(attn_id=attn_id, score=score))


@mcp.tool()
def stele_atm_modular(modular: bool) -> str:
    """ATTEMPT modular flag."""
    return json.dumps(get_store().atm_modular(modular=modular))


@mcp.tool()
def stele_atm_loop_plan(phase: str) -> str:
    """ATTEMPT loop plan."""
    return json.dumps(get_store().atm_loop_plan(phase=phase))


@mcp.tool()
def stele_mptp_shared(corpus: str) -> str:
    """MPT shared."""
    return json.dumps(get_store().mptp_shared(corpus=corpus))


@mcp.tool()
def stele_mptp_factor(shared_id: str, task: str) -> str:
    """MPT factor."""
    return json.dumps(get_store().mptp_factor(shared_id=shared_id, task=task))


@mcp.tool()
def stele_mptp_transfer(factor_id: str) -> str:
    """MPT transfer."""
    return json.dumps(get_store().mptp_transfer(factor_id=factor_id))


@mcp.tool()
def stele_mptp_score(xfer_id: str, score: int) -> str:
    """MPT score."""
    return json.dumps(get_store().mptp_score(xfer_id=xfer_id, score=score))


@mcp.tool()
def stele_mptp_efficient(param_efficient: bool) -> str:
    """MPT efficiency flag."""
    return json.dumps(
        get_store().mptp_efficient(param_efficient=param_efficient)
    )


@mcp.tool()
def stele_mptp_loop_plan(phase: str) -> str:
    """MPT loop plan."""
    return json.dumps(get_store().mptp_loop_plan(phase=phase))


@mcp.tool()
def stele_lora_freeze(base_frozen: bool) -> str:
    """LoRA freeze flag."""
    return json.dumps(get_store().lora_freeze(base_frozen=base_frozen))


@mcp.tool()
def stele_lora_rank(task: str, rank: int) -> str:
    """LoRA rank."""
    return json.dumps(get_store().lora_rank(task=task, rank=rank))


@mcp.tool()
def stele_lora_train(rank_id: str) -> str:
    """LoRA train."""
    return json.dumps(get_store().lora_train(rank_id=rank_id))


@mcp.tool()
def stele_lora_merge(train_id: str, score: int) -> str:
    """LoRA merge."""
    return json.dumps(get_store().lora_merge(train_id=train_id, score=score))


@mcp.tool()
def stele_lora_latency(zero_extra: bool) -> str:
    """LoRA latency flag."""
    return json.dumps(get_store().lora_latency(zero_extra=zero_extra))


@mcp.tool()
def stele_lora_loop_plan(phase: str) -> str:
    """LoRA loop plan."""
    return json.dumps(get_store().lora_loop_plan(phase=phase))


@mcp.tool()
def stele_adf_extract(task: str) -> str:
    """AdapterFusion extract."""
    return json.dumps(get_store().adf_extract(task=task))


@mcp.tool()
def stele_adf_compose(adapter_id: str) -> str:
    """AdapterFusion compose."""
    return json.dumps(get_store().adf_compose(adapter_id=adapter_id))


@mcp.tool()
def stele_adf_attend(compose_id: str) -> str:
    """AdapterFusion attend."""
    return json.dumps(get_store().adf_attend(compose_id=compose_id))


@mcp.tool()
def stele_adf_score(fusion_id: str, score: int) -> str:
    """AdapterFusion score."""
    return json.dumps(get_store().adf_score(fusion_id=fusion_id, score=score))


@mcp.tool()
def stele_adf_nondestruct(nondestructive: bool) -> str:
    """AdapterFusion nondestructive flag."""
    return json.dumps(
        get_store().adf_nondestruct(nondestructive=nondestructive)
    )


@mcp.tool()
def stele_adf_loop_plan(phase: str) -> str:
    """AdapterFusion loop plan."""
    return json.dumps(get_store().adf_loop_plan(phase=phase))


@mcp.tool()
def stele_cmp_insert(task: str) -> str:
    """Compacter insert."""
    return json.dumps(get_store().cmp_insert(task=task))


@mcp.tool()
def stele_cmp_kronecker(adapter_id: str, n: int) -> str:
    """Compacter kronecker."""
    return json.dumps(get_store().cmp_kronecker(adapter_id=adapter_id, n=n))


@mcp.tool()
def stele_cmp_train(kron_id: str) -> str:
    """Compacter train."""
    return json.dumps(get_store().cmp_train(kron_id=kron_id))


@mcp.tool()
def stele_cmp_score(train_id: str, score: int) -> str:
    """Compacter score."""
    return json.dumps(get_store().cmp_score(train_id=train_id, score=score))


@mcp.tool()
def stele_cmp_compact(param_efficient: bool) -> str:
    """Compacter efficiency flag."""
    return json.dumps(
        get_store().cmp_compact(param_efficient=param_efficient)
    )


@mcp.tool()
def stele_cmp_loop_plan(phase: str) -> str:
    """Compacter loop plan."""
    return json.dumps(get_store().cmp_loop_plan(phase=phase))


@mcp.tool()
def stele_ia3_vector(task: str) -> str:
    """(IA)^3 vector."""
    return json.dumps(get_store().ia3_vector(task=task))


@mcp.tool()
def stele_ia3_scale(vector_id: str) -> str:
    """(IA)^3 scale."""
    return json.dumps(get_store().ia3_scale(vector_id=vector_id))


@mcp.tool()
def stele_ia3_train(scale_id: str) -> str:
    """(IA)^3 train."""
    return json.dumps(get_store().ia3_train(scale_id=scale_id))


@mcp.tool()
def stele_ia3_score(train_id: str, score: int) -> str:
    """(IA)^3 score."""
    return json.dumps(get_store().ia3_score(train_id=train_id, score=score))


@mcp.tool()
def stele_ia3_mixed(mixed_batch: bool) -> str:
    """(IA)^3 mixed-batch flag."""
    return json.dumps(get_store().ia3_mixed(mixed_batch=mixed_batch))


@mcp.tool()
def stele_ia3_loop_plan(phase: str) -> str:
    """(IA)^3 loop plan."""
    return json.dumps(get_store().ia3_loop_plan(phase=phase))


@mcp.tool()
def stele_bft_freeze(weights_frozen: bool) -> str:
    """BitFit freeze flag."""
    return json.dumps(get_store().bft_freeze(weights_frozen=weights_frozen))


@mcp.tool()
def stele_bft_bias(task: str) -> str:
    """BitFit bias."""
    return json.dumps(get_store().bft_bias(task=task))


@mcp.tool()
def stele_bft_train(bias_id: str) -> str:
    """BitFit train."""
    return json.dumps(get_store().bft_train(bias_id=bias_id))


@mcp.tool()
def stele_bft_score(train_id: str, score: int) -> str:
    """BitFit score."""
    return json.dumps(get_store().bft_score(train_id=train_id, score=score))


@mcp.tool()
def stele_bft_tiny(fraction_pct: int) -> str:
    """BitFit tiny-fraction flag."""
    return json.dumps(get_store().bft_tiny(fraction_pct=fraction_pct))


@mcp.tool()
def stele_bft_loop_plan(phase: str) -> str:
    """BitFit loop plan."""
    return json.dumps(get_store().bft_loop_plan(phase=phase))


@mcp.tool()
def stele_dora_decompose(task: str) -> str:
    """DoRA decompose."""
    return json.dumps(get_store().dora_decompose(task=task))


@mcp.tool()
def stele_dora_magnitude(decomp_id: str) -> str:
    """DoRA magnitude."""
    return json.dumps(get_store().dora_magnitude(decomp_id=decomp_id))


@mcp.tool()
def stele_dora_direction(mag_id: str, rank: int) -> str:
    """DoRA direction."""
    return json.dumps(get_store().dora_direction(mag_id=mag_id, rank=rank))


@mcp.tool()
def stele_dora_score(dir_id: str, score: int) -> str:
    """DoRA score."""
    return json.dumps(get_store().dora_score(dir_id=dir_id, score=score))


@mcp.tool()
def stele_dora_vs_lora(closes_gap: bool) -> str:
    """DoRA vs LoRA flag."""
    return json.dumps(get_store().dora_vs_lora(closes_gap=closes_gap))


@mcp.tool()
def stele_dora_loop_plan(phase: str) -> str:
    """DoRA loop plan."""
    return json.dumps(get_store().dora_loop_plan(phase=phase))


@mcp.tool()
def stele_qlo_quantize(bits: int) -> str:
    """QLoRA quantize."""
    return json.dumps(get_store().qlo_quantize(bits=bits))


@mcp.tool()
def stele_qlo_nf4(quant_id: str) -> str:
    """QLoRA NF4."""
    return json.dumps(get_store().qlo_nf4(quant_id=quant_id))


@mcp.tool()
def stele_qlo_adapter(nf4_id: str, rank: int) -> str:
    """QLoRA adapter."""
    return json.dumps(get_store().qlo_adapter(nf4_id=nf4_id, rank=rank))


@mcp.tool()
def stele_qlo_score(adapter_id: str, score: int) -> str:
    """QLoRA score."""
    return json.dumps(
        get_store().qlo_score(adapter_id=adapter_id, score=score)
    )


@mcp.tool()
def stele_qlo_memory(double_quant: bool) -> str:
    """QLoRA memory flag."""
    return json.dumps(get_store().qlo_memory(double_quant=double_quant))


@mcp.tool()
def stele_qlo_loop_plan(phase: str) -> str:
    """QLoRA loop plan."""
    return json.dumps(get_store().qlo_loop_plan(phase=phase))


@mcp.tool()
def stele_adl_init(task: str, budget: int) -> str:
    """AdaLoRA init."""
    return json.dumps(get_store().adl_init(task=task, budget=budget))


@mcp.tool()
def stele_adl_svd(init_id: str) -> str:
    """AdaLoRA SVD."""
    return json.dumps(get_store().adl_svd(init_id=init_id))


@mcp.tool()
def stele_adl_prune(svd_id: str, keep: int) -> str:
    """AdaLoRA prune."""
    return json.dumps(get_store().adl_prune(svd_id=svd_id, keep=keep))


@mcp.tool()
def stele_adl_score(prune_id: str, score: int) -> str:
    """AdaLoRA score."""
    return json.dumps(get_store().adl_score(prune_id=prune_id, score=score))


@mcp.tool()
def stele_adl_adaptive(adaptive_rank: bool) -> str:
    """AdaLoRA adaptive-rank flag."""
    return json.dumps(
        get_store().adl_adaptive(adaptive_rank=adaptive_rank)
    )


@mcp.tool()
def stele_adl_loop_plan(phase: str) -> str:
    """AdaLoRA loop plan."""
    return json.dumps(get_store().adl_loop_plan(phase=phase))


@mcp.tool()
def stele_vra_share(task: str, rank: int) -> str:
    """VeRA share."""
    return json.dumps(get_store().vra_share(task=task, rank=rank))


@mcp.tool()
def stele_vra_scale(share_id: str) -> str:
    """VeRA scale."""
    return json.dumps(get_store().vra_scale(share_id=share_id))


@mcp.tool()
def stele_vra_train(scale_id: str) -> str:
    """VeRA train."""
    return json.dumps(get_store().vra_train(scale_id=scale_id))


@mcp.tool()
def stele_vra_score(train_id: str, score: int) -> str:
    """VeRA score."""
    return json.dumps(get_store().vra_score(train_id=train_id, score=score))


@mcp.tool()
def stele_vra_tiny(vector_only: bool) -> str:
    """VeRA tiny flag."""
    return json.dumps(get_store().vra_tiny(vector_only=vector_only))


@mcp.tool()
def stele_vra_loop_plan(phase: str) -> str:
    """VeRA loop plan."""
    return json.dumps(get_store().vra_loop_plan(phase=phase))


@mcp.tool()
def stele_adp_insert(task: str) -> str:
    """AdapterDrop insert."""
    return json.dumps(get_store().adp_insert(task=task))


@mcp.tool()
def stele_adp_drop(adapter_id: str, lower_layers: int) -> str:
    """AdapterDrop drop."""
    return json.dumps(
        get_store().adp_drop(
            adapter_id=adapter_id, lower_layers=lower_layers
        )
    )


@mcp.tool()
def stele_adp_infer(drop_id: str) -> str:
    """AdapterDrop infer."""
    return json.dumps(get_store().adp_infer(drop_id=drop_id))


@mcp.tool()
def stele_adp_score(infer_id: str, score: int) -> str:
    """AdapterDrop score."""
    return json.dumps(get_store().adp_score(infer_id=infer_id, score=score))


@mcp.tool()
def stele_adp_efficient(multi_task: bool) -> str:
    """AdapterDrop efficiency flag."""
    return json.dumps(get_store().adp_efficient(multi_task=multi_task))


@mcp.tool()
def stele_adp_loop_plan(phase: str) -> str:
    """AdapterDrop loop plan."""
    return json.dumps(get_store().adp_loop_plan(phase=phase))


@mcp.tool()
def stele_psa_svd(task: str, rank: int) -> str:
    """PiSSA SVD."""
    return json.dumps(get_store().psa_svd(task=task, rank=rank))


@mcp.tool()
def stele_psa_principal(svd_id: str) -> str:
    """PiSSA principal."""
    return json.dumps(get_store().psa_principal(svd_id=svd_id))


@mcp.tool()
def stele_psa_residual(principal_id: str) -> str:
    """PiSSA residual."""
    return json.dumps(get_store().psa_residual(principal_id=principal_id))


@mcp.tool()
def stele_psa_score(residual_id: str, score: int) -> str:
    """PiSSA score."""
    return json.dumps(
        get_store().psa_score(residual_id=residual_id, score=score)
    )


@mcp.tool()
def stele_psa_fast(faster_than_lora: bool) -> str:
    """PiSSA fast-convergence flag."""
    return json.dumps(
        get_store().psa_fast(faster_than_lora=faster_than_lora)
    )


@mcp.tool()
def stele_psa_loop_plan(phase: str) -> str:
    """PiSSA loop plan."""
    return json.dumps(get_store().psa_loop_plan(phase=phase))


@mcp.tool()
def stele_dpr_diff(task: str) -> str:
    """Diff Pruning diff."""
    return json.dumps(get_store().dpr_diff(task=task))


@mcp.tool()
def stele_dpr_mask(diff_id: str) -> str:
    """Diff Pruning mask."""
    return json.dumps(get_store().dpr_mask(diff_id=diff_id))


@mcp.tool()
def stele_dpr_prune(mask_id: str, sparsity_pct: int) -> str:
    """Diff Pruning prune."""
    return json.dumps(
        get_store().dpr_prune(mask_id=mask_id, sparsity_pct=sparsity_pct)
    )


@mcp.tool()
def stele_dpr_score(prune_id: str, score: int) -> str:
    """Diff Pruning score."""
    return json.dumps(get_store().dpr_score(prune_id=prune_id, score=score))


@mcp.tool()
def stele_dpr_sparse(no_new_params: bool) -> str:
    """Diff Pruning sparse flag."""
    return json.dumps(get_store().dpr_sparse(no_new_params=no_new_params))


@mcp.tool()
def stele_dpr_loop_plan(phase: str) -> str:
    """Diff Pruning loop plan."""
    return json.dumps(get_store().dpr_loop_plan(phase=phase))


@mcp.tool()
def stele_tlo_base(task: str, rank: int) -> str:
    """Tied-LoRA base."""
    return json.dumps(get_store().tlo_base(task=task, rank=rank))


@mcp.tool()
def stele_tlo_tie(base_id: str, layers: int) -> str:
    """Tied-LoRA tie."""
    return json.dumps(get_store().tlo_tie(base_id=base_id, layers=layers))


@mcp.tool()
def stele_tlo_train(tie_id: str) -> str:
    """Tied-LoRA train."""
    return json.dumps(get_store().tlo_train(tie_id=tie_id))


@mcp.tool()
def stele_tlo_score(train_id: str, score: int) -> str:
    """Tied-LoRA score."""
    return json.dumps(get_store().tlo_score(train_id=train_id, score=score))


@mcp.tool()
def stele_tlo_efficient(weight_tied: bool) -> str:
    """Tied-LoRA efficiency flag."""
    return json.dumps(get_store().tlo_efficient(weight_tied=weight_tied))


@mcp.tool()
def stele_tlo_loop_plan(phase: str) -> str:
    """Tied-LoRA loop plan."""
    return json.dumps(get_store().tlo_loop_plan(phase=phase))


@mcp.tool()
def stele_lrp_split(task: str) -> str:
    """LoRA+ split."""
    return json.dumps(get_store().lrp_split(task=task))


@mcp.tool()
def stele_lrp_ratio(split_id: str, lambda_ratio: int) -> str:
    """LoRA+ ratio."""
    return json.dumps(
        get_store().lrp_ratio(split_id=split_id, lambda_ratio=lambda_ratio)
    )


@mcp.tool()
def stele_lrp_train(ratio_id: str) -> str:
    """LoRA+ train."""
    return json.dumps(get_store().lrp_train(ratio_id=ratio_id))


@mcp.tool()
def stele_lrp_score(train_id: str, score: int) -> str:
    """LoRA+ score."""
    return json.dumps(get_store().lrp_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lrp_speed(faster_than_lora: bool) -> str:
    """LoRA+ speed flag."""
    return json.dumps(
        get_store().lrp_speed(faster_than_lora=faster_than_lora)
    )


@mcp.tool()
def stele_lrp_loop_plan(phase: str) -> str:
    """LoRA+ loop plan."""
    return json.dumps(get_store().lrp_loop_plan(phase=phase))


@mcp.tool()
def stele_lfa_freeze_a(task: str, rank: int) -> str:
    """LoRA-FA freeze A."""
    return json.dumps(get_store().lfa_freeze_a(task=task, rank=rank))


@mcp.tool()
def stele_lfa_train_b(a_id: str) -> str:
    """LoRA-FA train B."""
    return json.dumps(get_store().lfa_train_b(a_id=a_id))


@mcp.tool()
def stele_lfa_merge(train_id: str) -> str:
    """LoRA-FA merge."""
    return json.dumps(get_store().lfa_merge(train_id=train_id))


@mcp.tool()
def stele_lfa_score(merge_id: str, score: int) -> str:
    """LoRA-FA score."""
    return json.dumps(get_store().lfa_score(merge_id=merge_id, score=score))


@mcp.tool()
def stele_lfa_memory(activation_saved: bool) -> str:
    """LoRA-FA memory flag."""
    return json.dumps(
        get_store().lfa_memory(activation_saved=activation_saved)
    )


@mcp.tool()
def stele_lfa_loop_plan(phase: str) -> str:
    """LoRA-FA loop plan."""
    return json.dumps(get_store().lfa_loop_plan(phase=phase))


@mcp.tool()
def stele_dyl_range(task: str, r_min: int, r_max: int) -> str:
    """DyLoRA range."""
    return json.dumps(
        get_store().dyl_range(task=task, r_min=r_min, r_max=r_max)
    )


@mcp.tool()
def stele_dyl_sample(range_id: str) -> str:
    """DyLoRA sample."""
    return json.dumps(get_store().dyl_sample(range_id=range_id))


@mcp.tool()
def stele_dyl_select(sample_id: str, rank: int) -> str:
    """DyLoRA select."""
    return json.dumps(get_store().dyl_select(sample_id=sample_id, rank=rank))


@mcp.tool()
def stele_dyl_score(select_id: str, score: int) -> str:
    """DyLoRA score."""
    return json.dumps(
        get_store().dyl_score(select_id=select_id, score=score)
    )


@mcp.tool()
def stele_dyl_searchfree(search_free: bool) -> str:
    """DyLoRA search-free flag."""
    return json.dumps(get_store().dyl_searchfree(search_free=search_free))


@mcp.tool()
def stele_dyl_loop_plan(phase: str) -> str:
    """DyLoRA loop plan."""
    return json.dumps(get_store().dyl_loop_plan(phase=phase))


@mcp.tool()
def stele_lxs_svd(task: str, rank: int) -> str:
    """LoRA-XS SVD."""
    return json.dumps(get_store().lxs_svd(task=task, rank=rank))


@mcp.tool()
def stele_lxs_r(svd_id: str) -> str:
    """LoRA-XS R."""
    return json.dumps(get_store().lxs_r(svd_id=svd_id))


@mcp.tool()
def stele_lxs_train(r_id: str) -> str:
    """LoRA-XS train."""
    return json.dumps(get_store().lxs_train(r_id=r_id))


@mcp.tool()
def stele_lxs_score(train_id: str, score: int) -> str:
    """LoRA-XS score."""
    return json.dumps(get_store().lxs_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lxs_tiny(r_squared_only: bool) -> str:
    """LoRA-XS tiny flag."""
    return json.dumps(get_store().lxs_tiny(r_squared_only=r_squared_only))


@mcp.tool()
def stele_lxs_loop_plan(phase: str) -> str:
    """LoRA-XS loop plan."""
    return json.dumps(get_store().lxs_loop_plan(phase=phase))


@mcp.tool()
def stele_asy_role(task: str) -> str:
    """AsymmetryLoRA role."""
    return json.dumps(get_store().asy_role(task=task))


@mcp.tool()
def stele_asy_freeze_a(role_id: str) -> str:
    """AsymmetryLoRA freeze A."""
    return json.dumps(get_store().asy_freeze_a(role_id=role_id))


@mcp.tool()
def stele_asy_train_b(a_id: str) -> str:
    """AsymmetryLoRA train B."""
    return json.dumps(get_store().asy_train_b(a_id=a_id))


@mcp.tool()
def stele_asy_score(train_id: str, score: int) -> str:
    """AsymmetryLoRA score."""
    return json.dumps(get_store().asy_score(train_id=train_id, score=score))


@mcp.tool()
def stele_asy_bound(tighter_bound: bool) -> str:
    """AsymmetryLoRA bound flag."""
    return json.dumps(get_store().asy_bound(tighter_bound=tighter_bound))


@mcp.tool()
def stele_asy_loop_plan(phase: str) -> str:
    """AsymmetryLoRA loop plan."""
    return json.dumps(get_store().asy_loop_plan(phase=phase))


@mcp.tool()
def stele_lga_grad(task: str, samples: int) -> str:
    """LoRA-GA grad."""
    return json.dumps(get_store().lga_grad(task=task, samples=samples))


@mcp.tool()
def stele_lga_svd(grad_id: str) -> str:
    """LoRA-GA svd."""
    return json.dumps(get_store().lga_svd(grad_id=grad_id))


@mcp.tool()
def stele_lga_scale(svd_id: str) -> str:
    """LoRA-GA scale."""
    return json.dumps(get_store().lga_scale(svd_id=svd_id))


@mcp.tool()
def stele_lga_score(scale_id: str, score: int) -> str:
    """LoRA-GA score."""
    return json.dumps(get_store().lga_score(scale_id=scale_id, score=score))


@mcp.tool()
def stele_lga_fast(faster_convergence: bool) -> str:
    """LoRA-GA fast flag."""
    return json.dumps(
        get_store().lga_fast(faster_convergence=faster_convergence)
    )


@mcp.tool()
def stele_lga_loop_plan(phase: str) -> str:
    """LoRA-GA loop plan."""
    return json.dumps(get_store().lga_loop_plan(phase=phase))


@mcp.tool()
def stele_mor_square(task: str, side: int) -> str:
    """MoRA square."""
    return json.dumps(get_store().mor_square(task=task, side=side))


@mcp.tool()
def stele_mor_compress(square_id: str) -> str:
    """MoRA compress."""
    return json.dumps(get_store().mor_compress(square_id=square_id))


@mcp.tool()
def stele_mor_expand(compress_id: str) -> str:
    """MoRA expand."""
    return json.dumps(get_store().mor_expand(compress_id=compress_id))


@mcp.tool()
def stele_mor_score(expand_id: str, score: int) -> str:
    """MoRA score."""
    return json.dumps(get_store().mor_score(expand_id=expand_id, score=score))


@mcp.tool()
def stele_mor_merge(mergeable: bool) -> str:
    """MoRA merge flag."""
    return json.dumps(get_store().mor_merge(mergeable=mergeable))


@mcp.tool()
def stele_mor_loop_plan(phase: str) -> str:
    """MoRA loop plan."""
    return json.dumps(get_store().mor_loop_plan(phase=phase))


@mcp.tool()
def stele_rsl_rank(task: str, rank: int) -> str:
    """rsLoRA rank."""
    return json.dumps(get_store().rsl_rank(task=task, rank=rank))


@mcp.tool()
def stele_rsl_scale(rank_id: str) -> str:
    """rsLoRA scale."""
    return json.dumps(get_store().rsl_scale(rank_id=rank_id))


@mcp.tool()
def stele_rsl_train(scale_id: str) -> str:
    """rsLoRA train."""
    return json.dumps(get_store().rsl_train(scale_id=scale_id))


@mcp.tool()
def stele_rsl_score(train_id: str, score: int) -> str:
    """rsLoRA score."""
    return json.dumps(get_store().rsl_score(train_id=train_id, score=score))


@mcp.tool()
def stele_rsl_stable(no_collapse: bool) -> str:
    """rsLoRA stable flag."""
    return json.dumps(get_store().rsl_stable(no_collapse=no_collapse))


@mcp.tool()
def stele_rsl_loop_plan(phase: str) -> str:
    """rsLoRA loop plan."""
    return json.dumps(get_store().rsl_loop_plan(phase=phase))


@mcp.tool()
def stele_lkr_factors(task: str, factor_a: int, factor_b: int) -> str:
    """LoKr factors."""
    return json.dumps(
        get_store().lkr_factors(
            task=task, factor_a=factor_a, factor_b=factor_b
        )
    )


@mcp.tool()
def stele_lkr_kron(factors_id: str) -> str:
    """LoKr kron."""
    return json.dumps(get_store().lkr_kron(factors_id=factors_id))


@mcp.tool()
def stele_lkr_vectorize(kron_id: str) -> str:
    """LoKr vectorize."""
    return json.dumps(get_store().lkr_vectorize(kron_id=kron_id))


@mcp.tool()
def stele_lkr_score(vector_id: str, score: int) -> str:
    """LoKr score."""
    return json.dumps(
        get_store().lkr_score(vector_id=vector_id, score=score)
    )


@mcp.tool()
def stele_lkr_preserve(rank_preserved: bool) -> str:
    """LoKr preserve flag."""
    return json.dumps(
        get_store().lkr_preserve(rank_preserved=rank_preserved)
    )


@mcp.tool()
def stele_lkr_loop_plan(phase: str) -> str:
    """LoKr loop plan."""
    return json.dumps(get_store().lkr_loop_plan(phase=phase))


@mcp.tool()
def stele_lha_pair(task: str, rank: int) -> str:
    """LoHa pair."""
    return json.dumps(get_store().lha_pair(task=task, rank=rank))


@mcp.tool()
def stele_lha_hadamard(pair_id: str) -> str:
    """LoHa hadamard."""
    return json.dumps(get_store().lha_hadamard(pair_id=pair_id))


@mcp.tool()
def stele_lha_train(hadamard_id: str) -> str:
    """LoHa train."""
    return json.dumps(get_store().lha_train(hadamard_id=hadamard_id))


@mcp.tool()
def stele_lha_score(train_id: str, score: int) -> str:
    """LoHa score."""
    return json.dumps(get_store().lha_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lha_express(more_expressivity: bool) -> str:
    """LoHa express flag."""
    return json.dumps(
        get_store().lha_express(more_expressivity=more_expressivity)
    )


@mcp.tool()
def stele_lha_loop_plan(phase: str) -> str:
    """LoHa loop plan."""
    return json.dumps(get_store().lha_loop_plan(phase=phase))


@mcp.tool()
def stele_fft_basis(task: str, n_coeff: int) -> str:
    """FourierFT basis."""
    return json.dumps(get_store().fft_basis(task=task, n_coeff=n_coeff))


@mcp.tool()
def stele_fft_coeff(basis_id: str) -> str:
    """FourierFT coeff."""
    return json.dumps(get_store().fft_coeff(basis_id=basis_id))


@mcp.tool()
def stele_fft_idft(coeff_id: str) -> str:
    """FourierFT idft."""
    return json.dumps(get_store().fft_idft(coeff_id=coeff_id))


@mcp.tool()
def stele_fft_score(idft_id: str, score: int) -> str:
    """FourierFT score."""
    return json.dumps(get_store().fft_score(idft_id=idft_id, score=score))


@mcp.tool()
def stele_fft_sparse(spectral_sparse: bool) -> str:
    """FourierFT sparse flag."""
    return json.dumps(
        get_store().fft_sparse(spectral_sparse=spectral_sparse)
    )


@mcp.tool()
def stele_fft_loop_plan(phase: str) -> str:
    """FourierFT loop plan."""
    return json.dumps(get_store().fft_loop_plan(phase=phase))


@mcp.tool()
def stele_had_insert(task: str, bottleneck: int) -> str:
    """Houlsby insert."""
    return json.dumps(
        get_store().had_insert(task=task, bottleneck=bottleneck)
    )


@mcp.tool()
def stele_had_freeze(insert_id: str) -> str:
    """Houlsby freeze."""
    return json.dumps(get_store().had_freeze(insert_id=insert_id))


@mcp.tool()
def stele_had_train(freeze_id: str) -> str:
    """Houlsby train."""
    return json.dumps(get_store().had_train(freeze_id=freeze_id))


@mcp.tool()
def stele_had_score(train_id: str, score: int) -> str:
    """Houlsby score."""
    return json.dumps(get_store().had_score(train_id=train_id, score=score))


@mcp.tool()
def stele_had_latency(adds_latency: bool) -> str:
    """Houlsby latency flag."""
    return json.dumps(get_store().had_latency(adds_latency=adds_latency))


@mcp.tool()
def stele_had_loop_plan(phase: str) -> str:
    """Houlsby loop plan."""
    return json.dumps(get_store().had_loop_plan(phase=phase))


@mcp.tool()
def stele_rft_repr(task: str, layers: int) -> str:
    """ReFT repr."""
    return json.dumps(get_store().rft_repr(task=task, layers=layers))


@mcp.tool()
def stele_rft_edit(repr_id: str) -> str:
    """ReFT edit."""
    return json.dumps(get_store().rft_edit(repr_id=repr_id))


@mcp.tool()
def stele_rft_train(edit_id: str) -> str:
    """ReFT train."""
    return json.dumps(get_store().rft_train(edit_id=edit_id))


@mcp.tool()
def stele_rft_score(train_id: str, score: int) -> str:
    """ReFT score."""
    return json.dumps(get_store().rft_score(train_id=train_id, score=score))


@mcp.tool()
def stele_rft_weightless(no_weight_update: bool) -> str:
    """ReFT weightless flag."""
    return json.dumps(
        get_store().rft_weightless(no_weight_update=no_weight_update)
    )


@mcp.tool()
def stele_rft_loop_plan(phase: str) -> str:
    """ReFT loop plan."""
    return json.dumps(get_store().rft_loop_plan(phase=phase))


@mcp.tool()
def stele_oft_ortho(task: str, block: int) -> str:
    """OFT ortho."""
    return json.dumps(get_store().oft_ortho(task=task, block=block))


@mcp.tool()
def stele_oft_butterfly(ortho_id: str, factors: int) -> str:
    """OFT butterfly."""
    return json.dumps(
        get_store().oft_butterfly(ortho_id=ortho_id, factors=factors)
    )


@mcp.tool()
def stele_oft_train(butterfly_id: str) -> str:
    """OFT train."""
    return json.dumps(get_store().oft_train(butterfly_id=butterfly_id))


@mcp.tool()
def stele_oft_score(train_id: str, score: int) -> str:
    """OFT score."""
    return json.dumps(get_store().oft_score(train_id=train_id, score=score))


@mcp.tool()
def stele_oft_energy(hypersphere_preserved: bool) -> str:
    """OFT energy flag."""
    return json.dumps(
        get_store().oft_energy(hypersphere_preserved=hypersphere_preserved)
    )


@mcp.tool()
def stele_oft_loop_plan(phase: str) -> str:
    """OFT loop plan."""
    return json.dumps(get_store().oft_loop_plan(phase=phase))


@mcp.tool()
def stele_mss_shard(task: str, shards: int) -> str:
    """MiSS shard."""
    return json.dumps(get_store().mss_shard(task=task, shards=shards))


@mcp.tool()
def stele_mss_share(shard_id: str) -> str:
    """MiSS share."""
    return json.dumps(get_store().mss_share(shard_id=shard_id))


@mcp.tool()
def stele_mss_train(share_id: str) -> str:
    """MiSS train."""
    return json.dumps(get_store().mss_train(share_id=share_id))


@mcp.tool()
def stele_mss_score(train_id: str, score: int) -> str:
    """MiSS score."""
    return json.dumps(get_store().mss_score(train_id=train_id, score=score))


@mcp.tool()
def stele_mss_pareto(better_tradeoff: bool) -> str:
    """MiSS pareto flag."""
    return json.dumps(
        get_store().mss_pareto(better_tradeoff=better_tradeoff)
    )


@mcp.tool()
def stele_mss_loop_plan(phase: str) -> str:
    """MiSS loop plan."""
    return json.dumps(get_store().mss_loop_plan(phase=phase))


@mcp.tool()
def stele_drl_rank(task: str, rank: int) -> str:
    """DropLoRA rank."""
    return json.dumps(get_store().drl_rank(task=task, rank=rank))


@mcp.tool()
def stele_drl_mask(rank_id: str, keep_prob: int) -> str:
    """DropLoRA mask."""
    return json.dumps(
        get_store().drl_mask(rank_id=rank_id, keep_prob=keep_prob)
    )


@mcp.tool()
def stele_drl_train(mask_id: str) -> str:
    """DropLoRA train."""
    return json.dumps(get_store().drl_train(mask_id=mask_id))


@mcp.tool()
def stele_drl_score(train_id: str, score: int) -> str:
    """DropLoRA score."""
    return json.dumps(get_store().drl_score(train_id=train_id, score=score))


@mcp.tool()
def stele_drl_infer(no_extra_cost: bool) -> str:
    """DropLoRA infer flag."""
    return json.dumps(get_store().drl_infer(no_extra_cost=no_extra_cost))


@mcp.tool()
def stele_drl_loop_plan(phase: str) -> str:
    """DropLoRA loop plan."""
    return json.dumps(get_store().drl_loop_plan(phase=phase))


@mcp.tool()
def stele_gal_grad(task: str) -> str:
    """GaLore grad."""
    return json.dumps(get_store().gal_grad(task=task))


@mcp.tool()
def stele_gal_project(grad_id: str, rank: int) -> str:
    """GaLore project."""
    return json.dumps(get_store().gal_project(grad_id=grad_id, rank=rank))


@mcp.tool()
def stele_gal_step(project_id: str) -> str:
    """GaLore step."""
    return json.dumps(get_store().gal_step(project_id=project_id))


@mcp.tool()
def stele_gal_score(step_id: str, score: int) -> str:
    """GaLore score."""
    return json.dumps(get_store().gal_score(step_id=step_id, score=score))


@mcp.tool()
def stele_gal_full(updates_all_weights: bool) -> str:
    """GaLore full flag."""
    return json.dumps(
        get_store().gal_full(updates_all_weights=updates_all_weights)
    )


@mcp.tool()
def stele_gal_loop_plan(phase: str) -> str:
    """GaLore loop plan."""
    return json.dumps(get_store().gal_loop_plan(phase=phase))


@mcp.tool()
def stele_shr_mask(task: str, pct: int) -> str:
    """SHiRA mask."""
    return json.dumps(get_store().shr_mask(task=task, pct=pct))


@mcp.tool()
def stele_shr_tune(mask_id: str) -> str:
    """SHiRA tune."""
    return json.dumps(get_store().shr_tune(mask_id=mask_id))


@mcp.tool()
def stele_shr_switch(tune_id: str) -> str:
    """SHiRA switch."""
    return json.dumps(get_store().shr_switch(tune_id=tune_id))


@mcp.tool()
def stele_shr_score(switch_id: str, score: int) -> str:
    """SHiRA score."""
    return json.dumps(
        get_store().shr_score(switch_id=switch_id, score=score)
    )


@mcp.tool()
def stele_shr_fusion(less_concept_loss: bool) -> str:
    """SHiRA fusion flag."""
    return json.dumps(
        get_store().shr_fusion(less_concept_loss=less_concept_loss)
    )


@mcp.tool()
def stele_shr_loop_plan(phase: str) -> str:
    """SHiRA loop plan."""
    return json.dumps(get_store().shr_loop_plan(phase=phase))


@mcp.tool()
def stele_wft_wave(task: str, n_coeff: int) -> str:
    """WaveFT wave."""
    return json.dumps(get_store().wft_wave(task=task, n_coeff=n_coeff))


@mcp.tool()
def stele_wft_sparse(wave_id: str) -> str:
    """WaveFT sparse."""
    return json.dumps(get_store().wft_sparse(wave_id=wave_id))


@mcp.tool()
def stele_wft_idwt(sparse_id: str) -> str:
    """WaveFT idwt."""
    return json.dumps(get_store().wft_idwt(sparse_id=sparse_id))


@mcp.tool()
def stele_wft_score(idwt_id: str, score: int) -> str:
    """WaveFT score."""
    return json.dumps(get_store().wft_score(idwt_id=idwt_id, score=score))


@mcp.tool()
def stele_wft_granular(below_lora_min: bool) -> str:
    """WaveFT granular flag."""
    return json.dumps(
        get_store().wft_granular(below_lora_min=below_lora_min)
    )


@mcp.tool()
def stele_wft_loop_plan(phase: str) -> str:
    """WaveFT loop plan."""
    return json.dumps(get_store().wft_loop_plan(phase=phase))


@mcp.tool()
def stele_lpr_equiv(task: str) -> str:
    """LoRA-Pro equiv."""
    return json.dumps(get_store().lpr_equiv(task=task))


@mcp.tool()
def stele_lpr_adjust(equiv_id: str) -> str:
    """LoRA-Pro adjust."""
    return json.dumps(get_store().lpr_adjust(equiv_id=equiv_id))


@mcp.tool()
def stele_lpr_train(adjust_id: str) -> str:
    """LoRA-Pro train."""
    return json.dumps(get_store().lpr_train(adjust_id=adjust_id))


@mcp.tool()
def stele_lpr_score(train_id: str, score: int) -> str:
    """LoRA-Pro score."""
    return json.dumps(get_store().lpr_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lpr_bridge(closer_to_fft: bool) -> str:
    """LoRA-Pro bridge flag."""
    return json.dumps(get_store().lpr_bridge(closer_to_fft=closer_to_fft))


@mcp.tool()
def stele_lpr_loop_plan(phase: str) -> str:
    """LoRA-Pro loop plan."""
    return json.dumps(get_store().lpr_loop_plan(phase=phase))


@mcp.tool()
def stele_krl_kron(task: str, factor: int) -> str:
    """Kron-LoRA kron."""
    return json.dumps(get_store().krl_kron(task=task, factor=factor))


@mcp.tool()
def stele_krl_lora(kron_id: str, rank: int) -> str:
    """Kron-LoRA lora."""
    return json.dumps(get_store().krl_lora(kron_id=kron_id, rank=rank))


@mcp.tool()
def stele_krl_train(lora_id: str) -> str:
    """Kron-LoRA train."""
    return json.dumps(get_store().krl_train(lora_id=lora_id))


@mcp.tool()
def stele_krl_score(train_id: str, score: int) -> str:
    """Kron-LoRA score."""
    return json.dumps(get_store().krl_score(train_id=train_id, score=score))


@mcp.tool()
def stele_krl_compress(more_compression: bool) -> str:
    """Kron-LoRA compress flag."""
    return json.dumps(
        get_store().krl_compress(more_compression=more_compression)
    )


@mcp.tool()
def stele_krl_loop_plan(phase: str) -> str:
    """Kron-LoRA loop plan."""
    return json.dumps(get_store().krl_loop_plan(phase=phase))


@mcp.tool()
def stele_mil_svd(task: str, rank: int) -> str:
    """MiLoRA svd."""
    return json.dumps(get_store().mil_svd(task=task, rank=rank))


@mcp.tool()
def stele_mil_minor(svd_id: str) -> str:
    """MiLoRA minor."""
    return json.dumps(get_store().mil_minor(svd_id=svd_id))


@mcp.tool()
def stele_mil_freeze(minor_id: str) -> str:
    """MiLoRA freeze."""
    return json.dumps(get_store().mil_freeze(minor_id=minor_id))


@mcp.tool()
def stele_mil_score(freeze_id: str, score: int) -> str:
    """MiLoRA score."""
    return json.dumps(get_store().mil_score(freeze_id=freeze_id, score=score))


@mcp.tool()
def stele_mil_preserve(preserves_principal: bool) -> str:
    """MiLoRA preserve flag."""
    return json.dumps(
        get_store().mil_preserve(preserves_principal=preserves_principal)
    )


@mcp.tool()
def stele_mil_loop_plan(phase: str) -> str:
    """MiLoRA loop plan."""
    return json.dumps(get_store().mil_loop_plan(phase=phase))


@mcp.tool()
def stele_cda_cov(task: str) -> str:
    """CorDA cov."""
    return json.dumps(get_store().cda_cov(task=task))


@mcp.tool()
def stele_cda_mode(cov_id: str, mode: str) -> str:
    """CorDA mode."""
    return json.dumps(get_store().cda_mode(cov_id=cov_id, mode=mode))


@mcp.tool()
def stele_cda_adapt(mode_id: str) -> str:
    """CorDA adapt."""
    return json.dumps(get_store().cda_adapt(mode_id=mode_id))


@mcp.tool()
def stele_cda_score(adapt_id: str, score: int) -> str:
    """CorDA score."""
    return json.dumps(get_store().cda_score(adapt_id=adapt_id, score=score))


@mcp.tool()
def stele_cda_forget(less_forgetting: bool) -> str:
    """CorDA forget flag."""
    return json.dumps(
        get_store().cda_forget(less_forgetting=less_forgetting)
    )


@mcp.tool()
def stele_cda_loop_plan(phase: str) -> str:
    """CorDA loop plan."""
    return json.dumps(get_store().cda_loop_plan(phase=phase))


@mcp.tool()
def stele_lfq_quant(task: str, bits: int) -> str:
    """LoftQ quant."""
    return json.dumps(get_store().lfq_quant(task=task, bits=bits))


@mcp.tool()
def stele_lfq_init(quant_id: str, rank: int) -> str:
    """LoftQ init."""
    return json.dumps(get_store().lfq_init(quant_id=quant_id, rank=rank))


@mcp.tool()
def stele_lfq_train(init_id: str) -> str:
    """LoftQ train."""
    return json.dumps(get_store().lfq_train(init_id=init_id))


@mcp.tool()
def stele_lfq_score(train_id: str, score: int) -> str:
    """LoftQ score."""
    return json.dumps(get_store().lfq_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lfq_gap(closes_qlora_gap: bool) -> str:
    """LoftQ gap flag."""
    return json.dumps(
        get_store().lfq_gap(closes_qlora_gap=closes_qlora_gap)
    )


@mcp.tool()
def stele_lfq_loop_plan(phase: str) -> str:
    """LoftQ loop plan."""
    return json.dumps(get_store().lfq_loop_plan(phase=phase))


@mcp.tool()
def stele_lds_prelaunch(task: str) -> str:
    """LoRA-Dash prelaunch."""
    return json.dumps(get_store().lds_prelaunch(task=task))


@mcp.tool()
def stele_lds_tsd(prelaunch_id: str, count: int) -> str:
    """LoRA-Dash tsd."""
    return json.dumps(
        get_store().lds_tsd(prelaunch_id=prelaunch_id, count=count)
    )


@mcp.tool()
def stele_lds_dash(tsd_id: str) -> str:
    """LoRA-Dash dash."""
    return json.dumps(get_store().lds_dash(tsd_id=tsd_id))


@mcp.tool()
def stele_lds_score(dash_id: str, score: int) -> str:
    """LoRA-Dash score."""
    return json.dumps(get_store().lds_score(dash_id=dash_id, score=score))


@mcp.tool()
def stele_lds_impact(maximizes_tsd: bool) -> str:
    """LoRA-Dash impact flag."""
    return json.dumps(get_store().lds_impact(maximizes_tsd=maximizes_tsd))


@mcp.tool()
def stele_lds_loop_plan(phase: str) -> str:
    """LoRA-Dash loop plan."""
    return json.dumps(get_store().lds_loop_plan(phase=phase))


@mcp.tool()
def stele_dlo_adapters(task: str, rank: int) -> str:
    """Delta-LoRA adapters."""
    return json.dumps(get_store().dlo_adapters(task=task, rank=rank))


@mcp.tool()
def stele_dlo_delta(adapters_id: str) -> str:
    """Delta-LoRA delta."""
    return json.dumps(get_store().dlo_delta(adapters_id=adapters_id))


@mcp.tool()
def stele_dlo_propagate(delta_id: str) -> str:
    """Delta-LoRA propagate."""
    return json.dumps(get_store().dlo_propagate(delta_id=delta_id))


@mcp.tool()
def stele_dlo_score(propagate_id: str, score: int) -> str:
    """Delta-LoRA score."""
    return json.dumps(
        get_store().dlo_score(propagate_id=propagate_id, score=score)
    )


@mcp.tool()
def stele_dlo_highrank(high_rank_capacity: bool) -> str:
    """Delta-LoRA highrank flag."""
    return json.dumps(
        get_store().dlo_highrank(high_rank_capacity=high_rank_capacity)
    )


@mcp.tool()
def stele_dlo_loop_plan(phase: str) -> str:
    """Delta-LoRA loop plan."""
    return json.dumps(get_store().dlo_loop_plan(phase=phase))


@mcp.tool()
def stele_lon_grad(task: str) -> str:
    """LoRA-One grad."""
    return json.dumps(get_store().lon_grad(task=task))


@mcp.tool()
def stele_lon_align(grad_id: str, rank: int) -> str:
    """LoRA-One align."""
    return json.dumps(get_store().lon_align(grad_id=grad_id, rank=rank))


@mcp.tool()
def stele_lon_train(align_id: str) -> str:
    """LoRA-One train."""
    return json.dumps(get_store().lon_train(align_id=align_id))


@mcp.tool()
def stele_lon_score(train_id: str, score: int) -> str:
    """LoRA-One score."""
    return json.dumps(get_store().lon_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lon_immediate(immediate_align: bool) -> str:
    """LoRA-One immediate flag."""
    return json.dumps(
        get_store().lon_immediate(immediate_align=immediate_align)
    )


@mcp.tool()
def stele_lon_loop_plan(phase: str) -> str:
    """LoRA-One loop plan."""
    return json.dumps(get_store().lon_loop_plan(phase=phase))


@mcp.tool()
def stele_olr_qr(task: str, rank: int) -> str:
    """OLoRA qr."""
    return json.dumps(get_store().olr_qr(task=task, rank=rank))


@mcp.tool()
def stele_olr_ortho(qr_id: str) -> str:
    """OLoRA ortho."""
    return json.dumps(get_store().olr_ortho(qr_id=qr_id))


@mcp.tool()
def stele_olr_train(ortho_id: str) -> str:
    """OLoRA train."""
    return json.dumps(get_store().olr_train(ortho_id=ortho_id))


@mcp.tool()
def stele_olr_score(train_id: str, score: int) -> str:
    """OLoRA score."""
    return json.dumps(get_store().olr_score(train_id=train_id, score=score))


@mcp.tool()
def stele_olr_stable(stable_landscape: bool) -> str:
    """OLoRA stable flag."""
    return json.dumps(
        get_store().olr_stable(stable_landscape=stable_landscape)
    )


@mcp.tool()
def stele_olr_loop_plan(phase: str) -> str:
    """OLoRA loop plan."""
    return json.dumps(get_store().olr_loop_plan(phase=phase))


@mcp.tool()
def stele_lsp_select(task: str, fraction: int) -> str:
    """LoRA-SP select."""
    return json.dumps(get_store().lsp_select(task=task, fraction=fraction))


@mcp.tool()
def stele_lsp_freeze(select_id: str) -> str:
    """LoRA-SP freeze."""
    return json.dumps(get_store().lsp_freeze(select_id=select_id))


@mcp.tool()
def stele_lsp_train(freeze_id: str) -> str:
    """LoRA-SP train."""
    return json.dumps(get_store().lsp_train(freeze_id=freeze_id))


@mcp.tool()
def stele_lsp_score(train_id: str, score: int) -> str:
    """LoRA-SP score."""
    return json.dumps(get_store().lsp_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lsp_memory(lower_memory: bool) -> str:
    """LoRA-SP memory flag."""
    return json.dumps(get_store().lsp_memory(lower_memory=lower_memory))


@mcp.tool()
def stele_lsp_loop_plan(phase: str) -> str:
    """LoRA-SP loop plan."""
    return json.dumps(get_store().lsp_loop_plan(phase=phase))


@mcp.tool()
def stele_qps_quant(task: str, bits: int) -> str:
    """QPiSSA quant."""
    return json.dumps(get_store().qps_quant(task=task, bits=bits))


@mcp.tool()
def stele_qps_principal(quant_id: str, rank: int) -> str:
    """QPiSSA principal."""
    return json.dumps(
        get_store().qps_principal(quant_id=quant_id, rank=rank)
    )


@mcp.tool()
def stele_qps_train(principal_id: str) -> str:
    """QPiSSA train."""
    return json.dumps(get_store().qps_train(principal_id=principal_id))


@mcp.tool()
def stele_qps_score(train_id: str, score: int) -> str:
    """QPiSSA score."""
    return json.dumps(get_store().qps_score(train_id=train_id, score=score))


@mcp.tool()
def stele_qps_error(smaller_than_qlora: bool) -> str:
    """QPiSSA error flag."""
    return json.dumps(
        get_store().qps_error(smaller_than_qlora=smaller_than_qlora)
    )


@mcp.tool()
def stele_qps_loop_plan(phase: str) -> str:
    """QPiSSA loop plan."""
    return json.dumps(get_store().qps_loop_plan(phase=phase))


@mcp.tool()
def stele_msl_split(task: str, rank: int) -> str:
    """MoSLoRA split."""
    return json.dumps(get_store().msl_split(task=task, rank=rank))


@mcp.tool()
def stele_msl_mixer(split_id: str) -> str:
    """MoSLoRA mixer."""
    return json.dumps(get_store().msl_mixer(split_id=split_id))


@mcp.tool()
def stele_msl_train(mixer_id: str) -> str:
    """MoSLoRA train."""
    return json.dumps(get_store().msl_train(mixer_id=mixer_id))


@mcp.tool()
def stele_msl_score(train_id: str, score: int) -> str:
    """MoSLoRA score."""
    return json.dumps(get_store().msl_score(train_id=train_id, score=score))


@mcp.tool()
def stele_msl_fuse(flexible_fuse: bool) -> str:
    """MoSLoRA fuse flag."""
    return json.dumps(get_store().msl_fuse(flexible_fuse=flexible_fuse))


@mcp.tool()
def stele_msl_loop_plan(phase: str) -> str:
    """MoSLoRA loop plan."""
    return json.dumps(get_store().msl_loop_plan(phase=phase))


@mcp.tool()
def stele_ldr_eval(task: str) -> str:
    """LoRA-drop eval."""
    return json.dumps(get_store().ldr_eval(task=task))


@mcp.tool()
def stele_ldr_keep(eval_id: str, keep_pct: int) -> str:
    """LoRA-drop keep."""
    return json.dumps(
        get_store().ldr_keep(eval_id=eval_id, keep_pct=keep_pct)
    )


@mcp.tool()
def stele_ldr_share(keep_id: str) -> str:
    """LoRA-drop share."""
    return json.dumps(get_store().ldr_share(keep_id=keep_id))


@mcp.tool()
def stele_ldr_score(share_id: str, score: int) -> str:
    """LoRA-drop score."""
    return json.dumps(get_store().ldr_score(share_id=share_id, score=score))


@mcp.tool()
def stele_ldr_prune(half_params: bool) -> str:
    """LoRA-drop prune flag."""
    return json.dumps(get_store().ldr_prune(half_params=half_params))


@mcp.tool()
def stele_ldr_loop_plan(phase: str) -> str:
    """LoRA-drop loop plan."""
    return json.dumps(get_store().ldr_loop_plan(phase=phase))


@mcp.tool()
def stele_vbl_bank(task: str, size: int) -> str:
    """VB-LoRA bank."""
    return json.dumps(get_store().vbl_bank(task=task, size=size))


@mcp.tool()
def stele_vbl_topk(bank_id: str, k: int) -> str:
    """VB-LoRA topk."""
    return json.dumps(get_store().vbl_topk(bank_id=bank_id, k=k))


@mcp.tool()
def stele_vbl_compose(topk_id: str) -> str:
    """VB-LoRA compose."""
    return json.dumps(get_store().vbl_compose(topk_id=topk_id))


@mcp.tool()
def stele_vbl_score(compose_id: str, score: int) -> str:
    """VB-LoRA score."""
    return json.dumps(
        get_store().vbl_score(compose_id=compose_id, score=score)
    )


@mcp.tool()
def stele_vbl_extreme(extreme_compression: bool) -> str:
    """VB-LoRA extreme flag."""
    return json.dumps(
        get_store().vbl_extreme(extreme_compression=extreme_compression)
    )


@mcp.tool()
def stele_vbl_loop_plan(phase: str) -> str:
    """VB-LoRA loop plan."""
    return json.dumps(get_store().vbl_loop_plan(phase=phase))


@mcp.tool()
def stele_opl_proj(task: str) -> str:
    """OPLoRA proj."""
    return json.dumps(get_store().opl_proj(task=task))


@mcp.tool()
def stele_opl_constrain(proj_id: str, rank: int) -> str:
    """OPLoRA constrain."""
    return json.dumps(get_store().opl_constrain(proj_id=proj_id, rank=rank))


@mcp.tool()
def stele_opl_train(constrain_id: str) -> str:
    """OPLoRA train."""
    return json.dumps(get_store().opl_train(constrain_id=constrain_id))


@mcp.tool()
def stele_opl_score(train_id: str, score: int) -> str:
    """OPLoRA score."""
    return json.dumps(get_store().opl_score(train_id=train_id, score=score))


@mcp.tool()
def stele_opl_forget(less_forgetting: bool) -> str:
    """OPLoRA forget flag."""
    return json.dumps(
        get_store().opl_forget(less_forgetting=less_forgetting)
    )


@mcp.tool()
def stele_opl_loop_plan(phase: str) -> str:
    """OPLoRA loop plan."""
    return json.dumps(get_store().opl_loop_plan(phase=phase))


@mcp.tool()
def stele_gel_idim(task: str, layer: int) -> str:
    """GeLoRA idim."""
    return json.dumps(get_store().gel_idim(task=task, layer=layer))


@mcp.tool()
def stele_gel_rank(idim_id: str, rank: int) -> str:
    """GeLoRA rank."""
    return json.dumps(get_store().gel_rank(idim_id=idim_id, rank=rank))


@mcp.tool()
def stele_gel_train(rank_id: str) -> str:
    """GeLoRA train."""
    return json.dumps(get_store().gel_train(rank_id=rank_id))


@mcp.tool()
def stele_gel_score(train_id: str, score: int) -> str:
    """GeLoRA score."""
    return json.dumps(get_store().gel_score(train_id=train_id, score=score))


@mcp.tool()
def stele_gel_budget(within_budget: bool) -> str:
    """GeLoRA budget flag."""
    return json.dumps(get_store().gel_budget(within_budget=within_budget))


@mcp.tool()
def stele_gel_loop_plan(phase: str) -> str:
    """GeLoRA loop plan."""
    return json.dumps(get_store().gel_loop_plan(phase=phase))


@mcp.tool()
def stele_geo_dyn(task: str) -> str:
    """GeoLoRA dyn."""
    return json.dumps(get_store().geo_dyn(task=task))


@mcp.tool()
def stele_geo_budget(dyn_id: str, layers: int) -> str:
    """GeoLoRA budget."""
    return json.dumps(get_store().geo_budget(dyn_id=dyn_id, layers=layers))


@mcp.tool()
def stele_geo_train(budget_id: str) -> str:
    """GeoLoRA train."""
    return json.dumps(get_store().geo_train(budget_id=budget_id))


@mcp.tool()
def stele_geo_score(train_id: str, score: int) -> str:
    """GeoLoRA score."""
    return json.dumps(get_store().geo_score(train_id=train_id, score=score))


@mcp.tool()
def stele_geo_ortho(exact_ortho: bool) -> str:
    """GeoLoRA ortho flag."""
    return json.dumps(get_store().geo_ortho(exact_ortho=exact_ortho))


@mcp.tool()
def stele_geo_loop_plan(phase: str) -> str:
    """GeoLoRA loop plan."""
    return json.dumps(get_store().geo_loop_plan(phase=phase))


@mcp.tool()
def stele_rlo_bases(task: str, count: int) -> str:
    """RandLoRA bases."""
    return json.dumps(get_store().rlo_bases(task=task, count=count))


@mcp.tool()
def stele_rlo_scale(bases_id: str) -> str:
    """RandLoRA scale."""
    return json.dumps(get_store().rlo_scale(bases_id=bases_id))


@mcp.tool()
def stele_rlo_train(scale_id: str) -> str:
    """RandLoRA train."""
    return json.dumps(get_store().rlo_train(scale_id=scale_id))


@mcp.tool()
def stele_rlo_score(train_id: str, score: int) -> str:
    """RandLoRA score."""
    return json.dumps(get_store().rlo_score(train_id=train_id, score=score))


@mcp.tool()
def stele_rlo_fullrank(full_rank_update: bool) -> str:
    """RandLoRA fullrank flag."""
    return json.dumps(
        get_store().rlo_fullrank(full_rank_update=full_rank_update)
    )


@mcp.tool()
def stele_rlo_loop_plan(phase: str) -> str:
    """RandLoRA loop plan."""
    return json.dumps(get_store().rlo_loop_plan(phase=phase))


@mcp.tool()
def stele_lsh_graph(task: str) -> str:
    """LoRAShear graph."""
    return json.dumps(get_store().lsh_graph(task=task))


@mcp.tool()
def stele_lsh_prune(graph_id: str, ratio_pct: int) -> str:
    """LoRAShear prune."""
    return json.dumps(
        get_store().lsh_prune(graph_id=graph_id, ratio_pct=ratio_pct)
    )


@mcp.tool()
def stele_lsh_recover(prune_id: str) -> str:
    """LoRAShear recover."""
    return json.dumps(get_store().lsh_recover(prune_id=prune_id))


@mcp.tool()
def stele_lsh_score(recover_id: str, score: int) -> str:
    """LoRAShear score."""
    return json.dumps(
        get_store().lsh_score(recover_id=recover_id, score=score)
    )


@mcp.tool()
def stele_lsh_footprint(reduced: bool) -> str:
    """LoRAShear footprint flag."""
    return json.dumps(get_store().lsh_footprint(reduced=reduced))


@mcp.tool()
def stele_lsh_loop_plan(phase: str) -> str:
    """LoRAShear loop plan."""
    return json.dumps(get_store().lsh_loop_plan(phase=phase))


@mcp.tool()
def stele_aop_sub(task: str) -> str:
    """Alternating OPLoRA subproblem."""
    return json.dumps(get_store().aop_sub(task=task))


@mcp.tool()
def stele_aop_alt(sub_id: str, steps: int) -> str:
    """Alternating OPLoRA ALS steps."""
    return json.dumps(get_store().aop_alt(sub_id=sub_id, steps=steps))


@mcp.tool()
def stele_aop_train(alt_id: str) -> str:
    """Alternating OPLoRA train."""
    return json.dumps(get_store().aop_train(alt_id=alt_id))


@mcp.tool()
def stele_aop_score(train_id: str, score: int) -> str:
    """Alternating OPLoRA score."""
    return json.dumps(get_store().aop_score(train_id=train_id, score=score))


@mcp.tool()
def stele_aop_svd(near_svd: bool) -> str:
    """Alternating OPLoRA near-SVD flag."""
    return json.dumps(get_store().aop_svd(near_svd=near_svd))


@mcp.tool()
def stele_aop_loop_plan(phase: str) -> str:
    """Alternating OPLoRA loop plan."""
    return json.dumps(get_store().aop_loop_plan(phase=phase))


@mcp.tool()
def stele_lin_tsd(task: str, count: int) -> str:
    """LoRA-Init TSD."""
    return json.dumps(get_store().lin_tsd(task=task, count=count))


@mcp.tool()
def stele_lin_init(tsd_id: str) -> str:
    """LoRA-Init init."""
    return json.dumps(get_store().lin_init(tsd_id=tsd_id))


@mcp.tool()
def stele_lin_train(init_id: str) -> str:
    """LoRA-Init train."""
    return json.dumps(get_store().lin_train(init_id=init_id))


@mcp.tool()
def stele_lin_score(train_id: str, score: int) -> str:
    """LoRA-Init score."""
    return json.dumps(get_store().lin_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lin_fast(faster_convergence: bool) -> str:
    """LoRA-Init fast flag."""
    return json.dumps(
        get_store().lin_fast(faster_convergence=faster_convergence)
    )


@mcp.tool()
def stele_lin_loop_plan(phase: str) -> str:
    """LoRA-Init loop plan."""
    return json.dumps(get_store().lin_loop_plan(phase=phase))


@mcp.tool()
def stele_lnu_act(task: str, samples: int) -> str:
    """LoRA-Null activations."""
    return json.dumps(get_store().lnu_act(task=task, samples=samples))


@mcp.tool()
def stele_lnu_null(act_id: str) -> str:
    """LoRA-Null null space."""
    return json.dumps(get_store().lnu_null(act_id=act_id))


@mcp.tool()
def stele_lnu_train(null_id: str) -> str:
    """LoRA-Null train."""
    return json.dumps(get_store().lnu_train(null_id=null_id))


@mcp.tool()
def stele_lnu_score(train_id: str, score: int) -> str:
    """LoRA-Null score."""
    return json.dumps(get_store().lnu_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lnu_forget(preserves_knowledge: bool) -> str:
    """LoRA-Null forget flag."""
    return json.dumps(
        get_store().lnu_forget(preserves_knowledge=preserves_knowledge)
    )


@mcp.tool()
def stele_lnu_loop_plan(phase: str) -> str:
    """LoRA-Null loop plan."""
    return json.dumps(get_store().lnu_loop_plan(phase=phase))


@mcp.tool()
def stele_hyd_share(task: str) -> str:
    """HydraLoRA shared A."""
    return json.dumps(get_store().hyd_share(task=task))


@mcp.tool()
def stele_hyd_heads(share_id: str, heads: int) -> str:
    """HydraLoRA multi-B heads."""
    return json.dumps(get_store().hyd_heads(share_id=share_id, heads=heads))


@mcp.tool()
def stele_hyd_route(heads_id: str) -> str:
    """HydraLoRA MoE route."""
    return json.dumps(get_store().hyd_route(heads_id=heads_id))


@mcp.tool()
def stele_hyd_score(route_id: str, score: int) -> str:
    """HydraLoRA score."""
    return json.dumps(get_store().hyd_score(route_id=route_id, score=score))


@mcp.tool()
def stele_hyd_nodomain(no_domain_labels: bool) -> str:
    """HydraLoRA no-domain flag."""
    return json.dumps(
        get_store().hyd_nodomain(no_domain_labels=no_domain_labels)
    )


@mcp.tool()
def stele_hyd_loop_plan(phase: str) -> str:
    """HydraLoRA loop plan."""
    return json.dumps(get_store().hyd_loop_plan(phase=phase))


@mcp.tool()
def stele_llg_msu(task: str, adapters: int) -> str:
    """LoRA-LEGO MSUs."""
    return json.dumps(get_store().llg_msu(task=task, adapters=adapters))


@mcp.tool()
def stele_llg_cluster(msu_id: str, k: int) -> str:
    """LoRA-LEGO cluster."""
    return json.dumps(get_store().llg_cluster(msu_id=msu_id, k=k))


@mcp.tool()
def stele_llg_merge(cluster_id: str) -> str:
    """LoRA-LEGO merge."""
    return json.dumps(get_store().llg_merge(cluster_id=cluster_id))


@mcp.tool()
def stele_llg_score(merge_id: str, score: int) -> str:
    """LoRA-LEGO score."""
    return json.dumps(get_store().llg_score(merge_id=merge_id, score=score))


@mcp.tool()
def stele_llg_modular(modular_merge: bool) -> str:
    """LoRA-LEGO modular flag."""
    return json.dumps(get_store().llg_modular(modular_merge=modular_merge))


@mcp.tool()
def stele_llg_loop_plan(phase: str) -> str:
    """LoRA-LEGO loop plan."""
    return json.dumps(get_store().llg_loop_plan(phase=phase))


@mcp.tool()
def stele_lme_plugin(task: str, experts: int) -> str:
    """LoRAMoE plugin."""
    return json.dumps(get_store().lme_plugin(task=task, experts=experts))


@mcp.tool()
def stele_lme_balance(plugin_id: str) -> str:
    """LoRAMoE balance."""
    return json.dumps(get_store().lme_balance(plugin_id=plugin_id))


@mcp.tool()
def stele_lme_route(balance_id: str) -> str:
    """LoRAMoE route."""
    return json.dumps(get_store().lme_route(balance_id=balance_id))


@mcp.tool()
def stele_lme_score(route_id: str, score: int) -> str:
    """LoRAMoE score."""
    return json.dumps(get_store().lme_score(route_id=route_id, score=score))


@mcp.tool()
def stele_lme_forget(preserves_world: bool) -> str:
    """LoRAMoE forget flag."""
    return json.dumps(get_store().lme_forget(preserves_world=preserves_world))


@mcp.tool()
def stele_lme_loop_plan(phase: str) -> str:
    """LoRAMoE loop plan."""
    return json.dumps(get_store().lme_loop_plan(phase=phase))


@mcp.tool()
def stele_mel_experts(task: str, count: int) -> str:
    """MoELoRA experts."""
    return json.dumps(get_store().mel_experts(task=task, count=count))


@mcp.tool()
def stele_mel_contrast(experts_id: str) -> str:
    """MoELoRA contrast."""
    return json.dumps(get_store().mel_contrast(experts_id=experts_id))


@mcp.tool()
def stele_mel_gate(contrast_id: str) -> str:
    """MoELoRA gate."""
    return json.dumps(get_store().mel_gate(contrast_id=contrast_id))


@mcp.tool()
def stele_mel_score(gate_id: str, score: int) -> str:
    """MoELoRA score."""
    return json.dumps(get_store().mel_score(gate_id=gate_id, score=score))


@mcp.tool()
def stele_mel_sparse(sparse_activate: bool) -> str:
    """MoELoRA sparse flag."""
    return json.dumps(get_store().mel_sparse(sparse_activate=sparse_activate))


@mcp.tool()
def stele_mel_loop_plan(phase: str) -> str:
    """MoELoRA loop plan."""
    return json.dumps(get_store().mel_loop_plan(phase=phase))


@mcp.tool()
def stele_lhb_pool(task: str, modules: int) -> str:
    """LoraHub pool."""
    return json.dumps(get_store().lhb_pool(task=task, modules=modules))


@mcp.tool()
def stele_lhb_compose(pool_id: str) -> str:
    """LoraHub compose."""
    return json.dumps(get_store().lhb_compose(pool_id=pool_id))


@mcp.tool()
def stele_lhb_adapt(compose_id: str, shots: int) -> str:
    """LoraHub adapt."""
    return json.dumps(get_store().lhb_adapt(compose_id=compose_id, shots=shots))


@mcp.tool()
def stele_lhb_score(adapt_id: str, score: int) -> str:
    """LoraHub score."""
    return json.dumps(get_store().lhb_score(adapt_id=adapt_id, score=score))


@mcp.tool()
def stele_lhb_nograd(gradient_free: bool) -> str:
    """LoraHub nograd flag."""
    return json.dumps(get_store().lhb_nograd(gradient_free=gradient_free))


@mcp.tool()
def stele_lhb_loop_plan(phase: str) -> str:
    """LoraHub loop plan."""
    return json.dumps(get_store().lhb_loop_plan(phase=phase))


@mcp.tool()
def stele_mlr_scale(task: str, shards: int) -> str:
    """MultiLoRA scale."""
    return json.dumps(get_store().mlr_scale(task=task, shards=shards))


@mcp.tool()
def stele_mlr_init(scale_id: str) -> str:
    """MultiLoRA init."""
    return json.dumps(get_store().mlr_init(scale_id=scale_id))


@mcp.tool()
def stele_mlr_train(init_id: str) -> str:
    """MultiLoRA train."""
    return json.dumps(get_store().mlr_train(init_id=init_id))


@mcp.tool()
def stele_mlr_score(train_id: str, score: int) -> str:
    """MultiLoRA score."""
    return json.dumps(get_store().mlr_score(train_id=train_id, score=score))


@mcp.tool()
def stele_mlr_demo(more_democratic: bool) -> str:
    """MultiLoRA democratic flag."""
    return json.dumps(get_store().mlr_demo(more_democratic=more_democratic))


@mcp.tool()
def stele_mlr_loop_plan(phase: str) -> str:
    """MultiLoRA loop plan."""
    return json.dumps(get_store().mlr_loop_plan(phase=phase))


@mcp.tool()
def stele_mtl_task(task: str, tasks: int) -> str:
    """MTL-LoRA task set."""
    return json.dumps(get_store().mtl_task(task=task, tasks=tasks))


@mcp.tool()
def stele_mtl_spec(task_id: str) -> str:
    """MTL-LoRA task-specific transforms."""
    return json.dumps(get_store().mtl_spec(task_id=task_id))


@mcp.tool()
def stele_mtl_share(spec_id: str) -> str:
    """MTL-LoRA dynamic share."""
    return json.dumps(get_store().mtl_share(spec_id=spec_id))


@mcp.tool()
def stele_mtl_score(share_id: str, score: int) -> str:
    """MTL-LoRA score."""
    return json.dumps(get_store().mtl_score(share_id=share_id, score=score))


@mcp.tool()
def stele_mtl_interfere(less_interference: bool) -> str:
    """MTL-LoRA interference flag."""
    return json.dumps(
        get_store().mtl_interfere(less_interference=less_interference)
    )


@mcp.tool()
def stele_mtl_loop_plan(phase: str) -> str:
    """MTL-LoRA loop plan."""
    return json.dumps(get_store().mtl_loop_plan(phase=phase))


@mcp.tool()
def stele_mal_mix(task: str, experts: int) -> str:
    """MALoRA expert mix."""
    return json.dumps(get_store().mal_mix(task=task, experts=experts))


@mcp.tool()
def stele_mal_down(mix_id: str) -> str:
    """MALoRA shared down-proj."""
    return json.dumps(get_store().mal_down(mix_id=mix_id))


@mcp.tool()
def stele_mal_up(down_id: str) -> str:
    """MALoRA asymmetric up-proj."""
    return json.dumps(get_store().mal_up(down_id=down_id))


@mcp.tool()
def stele_mal_score(up_id: str, score: int) -> str:
    """MALoRA score."""
    return json.dumps(get_store().mal_score(up_id=up_id, score=score))


@mcp.tool()
def stele_mal_eff(fewer_params: bool) -> str:
    """MALoRA efficiency flag."""
    return json.dumps(get_store().mal_eff(fewer_params=fewer_params))


@mcp.tool()
def stele_mal_loop_plan(phase: str) -> str:
    """MALoRA loop plan."""
    return json.dumps(get_store().mal_loop_plan(phase=phase))


@mcp.tool()
def stele_lmi_split(task: str, rank: int) -> str:
    """LoRA-Mini split."""
    return json.dumps(get_store().lmi_split(task=task, rank=rank))


@mcp.tool()
def stele_lmi_inner(split_id: str) -> str:
    """LoRA-Mini inner trainable."""
    return json.dumps(get_store().lmi_inner(split_id=split_id))


@mcp.tool()
def stele_lmi_train(inner_id: str) -> str:
    """LoRA-Mini train."""
    return json.dumps(get_store().lmi_train(inner_id=inner_id))


@mcp.tool()
def stele_lmi_score(train_id: str, score: int) -> str:
    """LoRA-Mini score."""
    return json.dumps(get_store().lmi_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lmi_tiny(extreme_compress: bool) -> str:
    """LoRA-Mini compress flag."""
    return json.dumps(get_store().lmi_tiny(extreme_compress=extreme_compress))


@mcp.tool()
def stele_lmi_loop_plan(phase: str) -> str:
    """LoRA-Mini loop plan."""
    return json.dumps(get_store().lmi_loop_plan(phase=phase))


@mcp.tool()
def stele_qdy_range(task: str, r_min: int, r_max: int) -> str:
    """QDyLoRA rank range."""
    return json.dumps(
        get_store().qdy_range(task=task, r_min=r_min, r_max=r_max)
    )


@mcp.tool()
def stele_qdy_quant(range_id: str, bits: int) -> str:
    """QDyLoRA quantize."""
    return json.dumps(get_store().qdy_quant(range_id=range_id, bits=bits))


@mcp.tool()
def stele_qdy_train(quant_id: str) -> str:
    """QDyLoRA train."""
    return json.dumps(get_store().qdy_train(quant_id=quant_id))


@mcp.tool()
def stele_qdy_score(train_id: str, score: int) -> str:
    """QDyLoRA score."""
    return json.dumps(get_store().qdy_score(train_id=train_id, score=score))


@mcp.tool()
def stele_qdy_pick(pick_rank_at_infer: bool) -> str:
    """QDyLoRA pick-rank flag."""
    return json.dumps(
        get_store().qdy_pick(pick_rank_at_infer=pick_rank_at_infer)
    )


@mcp.tool()
def stele_qdy_loop_plan(phase: str) -> str:
    """QDyLoRA loop plan."""
    return json.dumps(get_store().qdy_loop_plan(phase=phase))


@mcp.tool()
def stele_lts_tsd(task: str, count: int) -> str:
    """LoRA-TSD identify directions."""
    return json.dumps(get_store().lts_tsd(task=task, count=count))


@mcp.tool()
def stele_lts_init(tsd_id: str) -> str:
    """LoRA-TSD init from TSDs."""
    return json.dumps(get_store().lts_init(tsd_id=tsd_id))


@mcp.tool()
def stele_lts_dash(init_id: str) -> str:
    """LoRA-TSD dash amplify."""
    return json.dumps(get_store().lts_dash(init_id=init_id))


@mcp.tool()
def stele_lts_score(dash_id: str, score: int) -> str:
    """LoRA-TSD score."""
    return json.dumps(get_store().lts_score(dash_id=dash_id, score=score))


@mcp.tool()
def stele_lts_combo(uses_both: bool) -> str:
    """LoRA-TSD Init+Dash combo flag."""
    return json.dumps(get_store().lts_combo(uses_both=uses_both))


@mcp.tool()
def stele_lts_loop_plan(phase: str) -> str:
    """LoRA-TSD loop plan."""
    return json.dumps(get_store().lts_loop_plan(phase=phase))


@mcp.tool()
def stele_slr_pool(adapters: int) -> str:
    """S-LoRA adapter pool."""
    return json.dumps(get_store().slr_pool(adapters=adapters))


@mcp.tool()
def stele_slr_page(pool_id: str, unified: bool) -> str:
    """S-LoRA Unified Paging."""
    return json.dumps(get_store().slr_page(pool_id=pool_id, unified=unified))


@mcp.tool()
def stele_slr_batch(page_id: str, concurrent: int) -> str:
    """S-LoRA heterogeneous batch."""
    return json.dumps(
        get_store().slr_batch(page_id=page_id, concurrent=concurrent)
    )


@mcp.tool()
def stele_slr_score(batch_id: str, score: int) -> str:
    """S-LoRA score."""
    return json.dumps(get_store().slr_score(batch_id=batch_id, score=score))


@mcp.tool()
def stele_slr_scale(thousands: bool) -> str:
    """S-LoRA scale flag."""
    return json.dumps(get_store().slr_scale(thousands=thousands))


@mcp.tool()
def stele_slr_loop_plan(phase: str) -> str:
    """S-LoRA loop plan."""
    return json.dumps(get_store().slr_loop_plan(phase=phase))


@mcp.tool()
def stele_cts_collect(adapters: int) -> str:
    """Compress-then-Serve collect."""
    return json.dumps(get_store().cts_collect(adapters=adapters))


@mcp.tool()
def stele_cts_basis(collect_id: str) -> str:
    """Compress-then-Serve shared basis."""
    return json.dumps(get_store().cts_basis(collect_id=collect_id))


@mcp.tool()
def stele_cts_scale(basis_id: str, adapters: int) -> str:
    """Compress-then-Serve per-adapter scales."""
    return json.dumps(
        get_store().cts_scale(basis_id=basis_id, adapters=adapters)
    )


@mcp.tool()
def stele_cts_score(scale_id: str, score: int) -> str:
    """Compress-then-Serve score."""
    return json.dumps(get_store().cts_score(scale_id=scale_id, score=score))


@mcp.tool()
def stele_cts_cluster(cluster_for_large: bool) -> str:
    """Compress-then-Serve cluster flag."""
    return json.dumps(
        get_store().cts_cluster(cluster_for_large=cluster_for_large)
    )


@mcp.tool()
def stele_cts_loop_plan(phase: str) -> str:
    """Compress-then-Serve loop plan."""
    return json.dumps(get_store().cts_loop_plan(phase=phase))


@mcp.tool()
def stele_flo_clients(clients: int) -> str:
    """FLoRA client set."""
    return json.dumps(get_store().flo_clients(clients=clients))


@mcp.tool()
def stele_flo_stack(clients_id: str, hetero_ranks: bool) -> str:
    """FLoRA stack adapters."""
    return json.dumps(
        get_store().flo_stack(
            clients_id=clients_id, hetero_ranks=hetero_ranks
        )
    )


@mcp.tool()
def stele_flo_agg(stack_id: str) -> str:
    """FLoRA stacking aggregation."""
    return json.dumps(get_store().flo_agg(stack_id=stack_id))


@mcp.tool()
def stele_flo_score(agg_id: str, score: int) -> str:
    """FLoRA score."""
    return json.dumps(get_store().flo_score(agg_id=agg_id, score=score))


@mcp.tool()
def stele_flo_hetero(supports_hetero: bool) -> str:
    """FLoRA hetero flag."""
    return json.dumps(
        get_store().flo_hetero(supports_hetero=supports_hetero)
    )


@mcp.tool()
def stele_flo_loop_plan(phase: str) -> str:
    """FLoRA loop plan."""
    return json.dumps(get_store().flo_loop_plan(phase=phase))


@mcp.tool()
def stele_pun_backbone(model: str) -> str:
    """Punica shared backbone."""
    return json.dumps(get_store().pun_backbone(model=model))


@mcp.tool()
def stele_pun_sgmv(backbone_id: str, adapters: int) -> str:
    """Punica SGMV batch."""
    return json.dumps(
        get_store().pun_sgmv(backbone_id=backbone_id, adapters=adapters)
    )


@mcp.tool()
def stele_pun_sched(sgmv_id: str) -> str:
    """Punica scheduler."""
    return json.dumps(get_store().pun_sched(sgmv_id=sgmv_id))


@mcp.tool()
def stele_pun_score(sched_id: str, score: int) -> str:
    """Punica score."""
    return json.dumps(get_store().pun_score(sched_id=sched_id, score=score))


@mcp.tool()
def stele_pun_multi(multi_tenant: bool) -> str:
    """Punica multi-tenant flag."""
    return json.dumps(get_store().pun_multi(multi_tenant=multi_tenant))


@mcp.tool()
def stele_pun_loop_plan(phase: str) -> str:
    """Punica loop plan."""
    return json.dumps(get_store().pun_loop_plan(phase=phase))


@mcp.tool()
def stele_mla_pipe(tasks: int, gpus: int) -> str:
    """mLoRA pipeline."""
    return json.dumps(get_store().mla_pipe(tasks=tasks, gpus=gpus))


@mcp.tool()
def stele_mla_batch(pipe_id: str) -> str:
    """mLoRA BatchLoRA."""
    return json.dumps(get_store().mla_batch(pipe_id=pipe_id))


@mcp.tool()
def stele_mla_train(batch_id: str) -> str:
    """mLoRA train."""
    return json.dumps(get_store().mla_train(batch_id=batch_id))


@mcp.tool()
def stele_mla_score(train_id: str, score: int) -> str:
    """mLoRA score."""
    return json.dumps(get_store().mla_score(train_id=train_id, score=score))


@mcp.tool()
def stele_mla_eff(lower_completion_time: bool) -> str:
    """mLoRA efficiency flag."""
    return json.dumps(
        get_store().mla_eff(lower_completion_time=lower_completion_time)
    )


@mcp.tool()
def stele_mla_loop_plan(phase: str) -> str:
    """mLoRA loop plan."""
    return json.dumps(get_store().mla_loop_plan(phase=phase))


@mcp.tool()
def stele_swl_alloc(task: str, rank: int) -> str:
    """SwitchLoRA allocate."""
    return json.dumps(get_store().swl_alloc(task=task, rank=rank))


@mcp.tool()
def stele_swl_switch(alloc_id: str, dims: int) -> str:
    """SwitchLoRA switch dims."""
    return json.dumps(get_store().swl_switch(alloc_id=alloc_id, dims=dims))


@mcp.tool()
def stele_swl_train(switch_id: str) -> str:
    """SwitchLoRA train."""
    return json.dumps(get_store().swl_train(switch_id=switch_id))


@mcp.tool()
def stele_swl_score(train_id: str, score: int) -> str:
    """SwitchLoRA score."""
    return json.dumps(get_store().swl_score(train_id=train_id, score=score))


@mcp.tool()
def stele_swl_full(mimics_fullrank: bool) -> str:
    """SwitchLoRA full-rank mimic flag."""
    return json.dumps(get_store().swl_full(mimics_fullrank=mimics_fullrank))


@mcp.tool()
def stele_swl_loop_plan(phase: str) -> str:
    """SwitchLoRA loop plan."""
    return json.dumps(get_store().swl_loop_plan(phase=phase))


@mcp.tool()
def stele_col_tune(task: str, rank: int) -> str:
    """COLA tune LoRA link."""
    return json.dumps(get_store().col_tune(task=task, rank=rank))


@mcp.tool()
def stele_col_knot(tune_id: str) -> str:
    """COLA tie knot."""
    return json.dumps(get_store().col_knot(tune_id=tune_id))


@mcp.tool()
def stele_col_extend(knot_id: str) -> str:
    """COLA extend chain."""
    return json.dumps(get_store().col_extend(knot_id=knot_id))


@mcp.tool()
def stele_col_score(extend_id: str, score: int) -> str:
    """COLA score."""
    return json.dumps(get_store().col_score(extend_id=extend_id, score=score))


@mcp.tool()
def stele_col_gap(closes_ft_gap: bool) -> str:
    """COLA FT-gap flag."""
    return json.dumps(get_store().col_gap(closes_ft_gap=closes_ft_gap))


@mcp.tool()
def stele_col_loop_plan(phase: str) -> str:
    """COLA loop plan."""
    return json.dumps(get_store().col_loop_plan(phase=phase))


@mcp.tool()
def stele_dlr_norm(task: str, rank: int) -> str:
    """DeLoRA normalize."""
    return json.dumps(get_store().dlr_norm(task=task, rank=rank))


@mcp.tool()
def stele_dlr_bound(norm_id: str, lambda_bound: int) -> str:
    """DeLoRA Frobenius bound."""
    return json.dumps(
        get_store().dlr_bound(norm_id=norm_id, lambda_bound=lambda_bound)
    )


@mcp.tool()
def stele_dlr_train(bound_id: str) -> str:
    """DeLoRA train."""
    return json.dumps(get_store().dlr_train(bound_id=bound_id))


@mcp.tool()
def stele_dlr_score(train_id: str, score: int) -> str:
    """DeLoRA score."""
    return json.dumps(get_store().dlr_score(train_id=train_id, score=score))


@mcp.tool()
def stele_dlr_robust(hyperparam_robust: bool) -> str:
    """DeLoRA robustness flag."""
    return json.dumps(
        get_store().dlr_robust(hyperparam_robust=hyperparam_robust)
    )


@mcp.tool()
def stele_dlr_loop_plan(phase: str) -> str:
    """DeLoRA loop plan."""
    return json.dumps(get_store().dlr_loop_plan(phase=phase))


@mcp.tool()
def stele_meo_mini(task: str, n_minis: int, mini_rank: int) -> str:
    """MELoRA mini ensemble."""
    return json.dumps(
        get_store().meo_mini(
            task=task, n_minis=n_minis, mini_rank=mini_rank
        )
    )


@mcp.tool()
def stele_meo_diag(mini_id: str) -> str:
    """MELoRA block-diagonal."""
    return json.dumps(get_store().meo_diag(mini_id=mini_id))


@mcp.tool()
def stele_meo_train(diag_id: str) -> str:
    """MELoRA train."""
    return json.dumps(get_store().meo_train(diag_id=diag_id))


@mcp.tool()
def stele_meo_score(train_id: str, score: int) -> str:
    """MELoRA score."""
    return json.dumps(get_store().meo_score(train_id=train_id, score=score))


@mcp.tool()
def stele_meo_rank(higher_effective_rank: bool) -> str:
    """MELoRA effective-rank flag."""
    return json.dumps(
        get_store().meo_rank(higher_effective_rank=higher_effective_rank)
    )


@mcp.tool()
def stele_meo_loop_plan(phase: str) -> str:
    """MELoRA loop plan."""
    return json.dumps(get_store().meo_loop_plan(phase=phase))


@mcp.tool()
def stele_rlr_warm(task: str, steps: int) -> str:
    """ReLoRA warm-start."""
    return json.dumps(get_store().rlr_warm(task=task, steps=steps))


@mcp.tool()
def stele_rlr_merge(warm_id: str) -> str:
    """ReLoRA merge restart."""
    return json.dumps(get_store().rlr_merge(warm_id=warm_id))


@mcp.tool()
def stele_rlr_jagged(merge_id: str) -> str:
    """ReLoRA jagged LR."""
    return json.dumps(get_store().rlr_jagged(merge_id=merge_id))


@mcp.tool()
def stele_rlr_score(jagged_id: str, score: int) -> str:
    """ReLoRA score."""
    return json.dumps(
        get_store().rlr_score(jagged_id=jagged_id, score=score)
    )


@mcp.tool()
def stele_rlr_high(high_rank_update: bool) -> str:
    """ReLoRA high-rank flag."""
    return json.dumps(
        get_store().rlr_high(high_rank_update=high_rank_update)
    )


@mcp.tool()
def stele_rlr_loop_plan(phase: str) -> str:
    """ReLoRA loop plan."""
    return json.dumps(get_store().rlr_loop_plan(phase=phase))


@mcp.tool()
def stele_eth_plane(task: str, reflections: int) -> str:
    """ETHER hyperplane alloc."""
    return json.dumps(
        get_store().eth_plane(task=task, reflections=reflections)
    )


@mcp.tool()
def stele_eth_reflect(plane_id: str) -> str:
    """ETHER reflect."""
    return json.dumps(get_store().eth_reflect(plane_id=plane_id))


@mcp.tool()
def stele_eth_train(reflect_id: str) -> str:
    """ETHER train."""
    return json.dumps(get_store().eth_train(reflect_id=reflect_id))


@mcp.tool()
def stele_eth_score(train_id: str, score: int) -> str:
    """ETHER score."""
    return json.dumps(get_store().eth_score(train_id=train_id, score=score))


@mcp.tool()
def stele_eth_plus(ether_plus: bool) -> str:
    """ETHER+ flag."""
    return json.dumps(get_store().eth_plus(ether_plus=ether_plus))


@mcp.tool()
def stele_eth_loop_plan(phase: str) -> str:
    """ETHER loop plan."""
    return json.dumps(get_store().eth_loop_plan(phase=phase))


@mcp.tool()
def stele_lco_concepts(task: str, n_loras: int) -> str:
    """LoRA-Composer multi-concept set."""
    return json.dumps(
        get_store().lco_concepts(task=task, n_loras=n_loras)
    )


@mcp.tool()
def stele_lco_inject(concepts_id: str) -> str:
    """LoRA-Composer inject."""
    return json.dumps(get_store().lco_inject(concepts_id=concepts_id))


@mcp.tool()
def stele_lco_isolate(inject_id: str) -> str:
    """LoRA-Composer isolate."""
    return json.dumps(get_store().lco_isolate(inject_id=inject_id))


@mcp.tool()
def stele_lco_score(isolate_id: str, score: int) -> str:
    """LoRA-Composer score."""
    return json.dumps(
        get_store().lco_score(isolate_id=isolate_id, score=score)
    )


@mcp.tool()
def stele_lco_free(training_free: bool) -> str:
    """LoRA-Composer training-free flag."""
    return json.dumps(get_store().lco_free(training_free=training_free))


@mcp.tool()
def stele_lco_loop_plan(phase: str) -> str:
    """LoRA-Composer loop plan."""
    return json.dumps(get_store().lco_loop_plan(phase=phase))


@mcp.tool()
def stele_car_compress(task: str, keep_rank: int) -> str:
    """CARE-LoRA compress activations."""
    return json.dumps(
        get_store().car_compress(task=task, keep_rank=keep_rank)
    )


@mcp.tool()
def stele_car_recon(compress_id: str) -> str:
    """CARE-LoRA reconstruct."""
    return json.dumps(get_store().car_recon(compress_id=compress_id))


@mcp.tool()
def stele_car_train(recon_id: str) -> str:
    """CARE-LoRA train."""
    return json.dumps(get_store().car_train(recon_id=recon_id))


@mcp.tool()
def stele_car_score(train_id: str, score: int) -> str:
    """CARE-LoRA score."""
    return json.dumps(get_store().car_score(train_id=train_id, score=score))


@mcp.tool()
def stele_car_mem(activation_saved: bool) -> str:
    """CARE-LoRA memory flag."""
    return json.dumps(
        get_store().car_mem(activation_saved=activation_saved)
    )


@mcp.tool()
def stele_car_loop_plan(phase: str) -> str:
    """CARE-LoRA loop plan."""
    return json.dumps(get_store().car_loop_plan(phase=phase))


@mcp.tool()
def stele_lrr_pair(task: str, n_pairs: int) -> str:
    """LoRA.rar subject-style pairs."""
    return json.dumps(get_store().lrr_pair(task=task, n_pairs=n_pairs))


@mcp.tool()
def stele_lrr_hyper(pair_id: str) -> str:
    """LoRA.rar hypernetwork."""
    return json.dumps(get_store().lrr_hyper(pair_id=pair_id))


@mcp.tool()
def stele_lrr_merge(hyper_id: str) -> str:
    """LoRA.rar merge."""
    return json.dumps(get_store().lrr_merge(hyper_id=hyper_id))


@mcp.tool()
def stele_lrr_score(merge_id: str, score: int) -> str:
    """LoRA.rar score."""
    return json.dumps(get_store().lrr_score(merge_id=merge_id, score=score))


@mcp.tool()
def stele_lrr_fast(realtime_merge: bool) -> str:
    """LoRA.rar realtime flag."""
    return json.dumps(get_store().lrr_fast(realtime_merge=realtime_merge))


@mcp.tool()
def stele_lrr_loop_plan(phase: str) -> str:
    """LoRA.rar loop plan."""
    return json.dumps(get_store().lrr_loop_plan(phase=phase))


@mcp.tool()
def stele_svf_svd(task: str, keep: int) -> str:
    """SVFT singular-vector factor."""
    return json.dumps(get_store().svf_svd(task=task, keep=keep))


@mcp.tool()
def stele_svf_sparse(svd_id: str) -> str:
    """SVFT sparse pattern."""
    return json.dumps(get_store().svf_sparse(svd_id=svd_id))


@mcp.tool()
def stele_svf_train(sparse_id: str) -> str:
    """SVFT train."""
    return json.dumps(get_store().svf_train(sparse_id=sparse_id))


@mcp.tool()
def stele_svf_score(train_id: str, score: int) -> str:
    """SVFT score."""
    return json.dumps(get_store().svf_score(train_id=train_id, score=score))


@mcp.tool()
def stele_svf_geom(weight_dependent: bool) -> str:
    """SVFT geometry flag."""
    return json.dumps(
        get_store().svf_geom(weight_dependent=weight_dependent)
    )


@mcp.tool()
def stele_svf_loop_plan(phase: str) -> str:
    """SVFT loop plan."""
    return json.dumps(get_store().svf_loop_plan(phase=phase))


@mcp.tool()
def stele_fly_proj(task: str, rank: int) -> str:
    """FlyLoRA frozen projection."""
    return json.dumps(get_store().fly_proj(task=task, rank=rank))


@mcp.tool()
def stele_fly_topk(proj_id: str, k: int) -> str:
    """FlyLoRA top-k experts."""
    return json.dumps(get_store().fly_topk(proj_id=proj_id, k=k))


@mcp.tool()
def stele_fly_train(topk_id: str) -> str:
    """FlyLoRA train."""
    return json.dumps(get_store().fly_train(topk_id=topk_id))


@mcp.tool()
def stele_fly_score(train_id: str, score: int) -> str:
    """FlyLoRA score."""
    return json.dumps(get_store().fly_score(train_id=train_id, score=score))


@mcp.tool()
def stele_fly_implicit(implicit_router: bool) -> str:
    """FlyLoRA implicit-router flag."""
    return json.dumps(
        get_store().fly_implicit(implicit_router=implicit_router)
    )


@mcp.tool()
def stele_fly_loop_plan(phase: str) -> str:
    """FlyLoRA loop plan."""
    return json.dumps(get_store().fly_loop_plan(phase=phase))


@mcp.tool()
def stele_nla_basis(task: str, n_basis: int) -> str:
    """NOLA random bases."""
    return json.dumps(get_store().nla_basis(task=task, n_basis=n_basis))


@mcp.tool()
def stele_nla_coeff(basis_id: str) -> str:
    """NOLA coefficients."""
    return json.dumps(get_store().nla_coeff(basis_id=basis_id))


@mcp.tool()
def stele_nla_train(coeff_id: str) -> str:
    """NOLA train."""
    return json.dumps(get_store().nla_train(coeff_id=coeff_id))


@mcp.tool()
def stele_nla_score(train_id: str, score: int) -> str:
    """NOLA score."""
    return json.dumps(get_store().nla_score(train_id=train_id, score=score))


@mcp.tool()
def stele_nla_compact(beyond_rank1: bool) -> str:
    """NOLA compact flag."""
    return json.dumps(get_store().nla_compact(beyond_rank1=beyond_rank1))


@mcp.tool()
def stele_nla_loop_plan(phase: str) -> str:
    """NOLA loop plan."""
    return json.dumps(get_store().nla_loop_plan(phase=phase))


@mcp.tool()
def stele_mxl_experts(task: str, n_experts: int) -> str:
    """MixLoRA FFN experts."""
    return json.dumps(
        get_store().mxl_experts(task=task, n_experts=n_experts)
    )


@mcp.tool()
def stele_mxl_route(experts_id: str, k: int) -> str:
    """MixLoRA top-k router."""
    return json.dumps(get_store().mxl_route(experts_id=experts_id, k=k))


@mcp.tool()
def stele_mxl_attn(route_id: str) -> str:
    """MixLoRA attention LoRAs."""
    return json.dumps(get_store().mxl_attn(route_id=route_id))


@mcp.tool()
def stele_mxl_score(attn_id: str, score: int) -> str:
    """MixLoRA score."""
    return json.dumps(get_store().mxl_score(attn_id=attn_id, score=score))


@mcp.tool()
def stele_mxl_balance(load_balance: bool) -> str:
    """MixLoRA load-balance flag."""
    return json.dumps(get_store().mxl_balance(load_balance=load_balance))


@mcp.tool()
def stele_mxl_loop_plan(phase: str) -> str:
    """MixLoRA loop plan."""
    return json.dumps(get_store().mxl_loop_plan(phase=phase))


@mcp.tool()
def stele_spr_group(task: str, groups: int) -> str:
    """SuperLoRA grouping."""
    return json.dumps(get_store().spr_group(task=task, groups=groups))


@mcp.tool()
def stele_spr_fold(group_id: str) -> str:
    """SuperLoRA fold."""
    return json.dumps(get_store().spr_fold(group_id=group_id))


@mcp.tool()
def stele_spr_factor(fold_id: str) -> str:
    """SuperLoRA factor."""
    return json.dumps(get_store().spr_factor(fold_id=fold_id))


@mcp.tool()
def stele_spr_score(factor_id: str, score: int) -> str:
    """SuperLoRA score."""
    return json.dumps(
        get_store().spr_score(factor_id=factor_id, score=score)
    )


@mcp.tool()
def stele_spr_unify(unifies_loha_lokr: bool) -> str:
    """SuperLoRA unify flag."""
    return json.dumps(
        get_store().spr_unify(unifies_loha_lokr=unifies_loha_lokr)
    )


@mcp.tool()
def stele_spr_loop_plan(phase: str) -> str:
    """SuperLoRA loop plan."""
    return json.dumps(get_store().spr_loop_plan(phase=phase))


@mcp.tool()
def stele_tld_tie(task: str, layers: int) -> str:
    """Tied-LoRA weight tying."""
    return json.dumps(get_store().tld_tie(task=task, layers=layers))


@mcp.tool()
def stele_tld_select(tie_id: str) -> str:
    """Tied-LoRA selective train."""
    return json.dumps(get_store().tld_select(tie_id=tie_id))


@mcp.tool()
def stele_tld_scale(select_id: str) -> str:
    """Tied-LoRA scale vectors."""
    return json.dumps(get_store().tld_scale(select_id=select_id))


@mcp.tool()
def stele_tld_score(scale_id: str, score: int) -> str:
    """Tied-LoRA score."""
    return json.dumps(
        get_store().tld_score(scale_id=scale_id, score=score)
    )


@mcp.tool()
def stele_tld_frac(fraction_of_lora: bool) -> str:
    """Tied-LoRA fraction flag."""
    return json.dumps(
        get_store().tld_frac(fraction_of_lora=fraction_of_lora)
    )


@mcp.tool()
def stele_tld_loop_plan(phase: str) -> str:
    """Tied-LoRA loop plan."""
    return json.dumps(get_store().tld_loop_plan(phase=phase))


@mcp.tool()
def stele_qal_group(task: str, groups: int) -> str:
    """QA-LoRA grouping."""
    return json.dumps(get_store().qal_group(task=task, groups=groups))


@mcp.tool()
def stele_qal_quant(group_id: str, bits: int) -> str:
    """QA-LoRA quantize."""
    return json.dumps(get_store().qal_quant(group_id=group_id, bits=bits))


@mcp.tool()
def stele_qal_adapt(quant_id: str) -> str:
    """QA-LoRA grouped adapters."""
    return json.dumps(get_store().qal_adapt(quant_id=quant_id))


@mcp.tool()
def stele_qal_score(adapt_id: str, score: int) -> str:
    """QA-LoRA score."""
    return json.dumps(
        get_store().qal_score(adapt_id=adapt_id, score=score)
    )


@mcp.tool()
def stele_qal_merge(merge_int4: bool) -> str:
    """QA-LoRA INT4 merge flag."""
    return json.dumps(get_store().qal_merge(merge_int4=merge_int4))


@mcp.tool()
def stele_qal_loop_plan(phase: str) -> str:
    """QA-LoRA loop plan."""
    return json.dumps(get_store().qal_loop_plan(phase=phase))


@mcp.tool()
def stele_ulo_space(task: str, dim: int) -> str:
    """Uni-LoRA subspace."""
    return json.dumps(get_store().ulo_space(task=task, dim=dim))


@mcp.tool()
def stele_ulo_iso(space_id: str) -> str:
    """Uni-LoRA isometric projection."""
    return json.dumps(get_store().ulo_iso(space_id=space_id))


@mcp.tool()
def stele_ulo_vec(iso_id: str) -> str:
    """Uni-LoRA shared vector."""
    return json.dumps(get_store().ulo_vec(iso_id=iso_id))


@mcp.tool()
def stele_ulo_score(vec_id: str, score: int) -> str:
    """Uni-LoRA score."""
    return json.dumps(get_store().ulo_score(vec_id=vec_id, score=score))


@mcp.tool()
def stele_ulo_one(one_vector: bool) -> str:
    """Uni-LoRA one-vector flag."""
    return json.dumps(get_store().ulo_one(one_vector=one_vector))


@mcp.tool()
def stele_ulo_loop_plan(phase: str) -> str:
    """Uni-LoRA loop plan."""
    return json.dumps(get_store().ulo_loop_plan(phase=phase))


@mcp.tool()
def stele_bor_row(task: str) -> str:
    """BoRA row magnitudes."""
    return json.dumps(get_store().bor_row(task=task))


@mcp.tool()
def stele_bor_col(row_id: str) -> str:
    """BoRA column magnitudes."""
    return json.dumps(get_store().bor_col(row_id=row_id))


@mcp.tool()
def stele_bor_train(col_id: str) -> str:
    """BoRA train."""
    return json.dumps(get_store().bor_train(col_id=col_id))


@mcp.tool()
def stele_bor_score(train_id: str, score: int) -> str:
    """BoRA score."""
    return json.dumps(
        get_store().bor_score(train_id=train_id, score=score)
    )


@mcp.tool()
def stele_bor_sym(symmetric: bool) -> str:
    """BoRA symmetry flag."""
    return json.dumps(get_store().bor_sym(symmetric=symmetric))


@mcp.tool()
def stele_bor_loop_plan(phase: str) -> str:
    """BoRA loop plan."""
    return json.dumps(get_store().bor_loop_plan(phase=phase))


@mcp.tool()
def stele_qga_weight(task: str) -> str:
    """Q-GaLore INT8 weights."""
    return json.dumps(get_store().qga_weight(task=task))


@mcp.tool()
def stele_qga_proj(weight_id: str, rank: int) -> str:
    """Q-GaLore INT4 projection."""
    return json.dumps(get_store().qga_proj(weight_id=weight_id, rank=rank))


@mcp.tool()
def stele_qga_lazy(proj_id: str) -> str:
    """Q-GaLore lazy SVD."""
    return json.dumps(get_store().qga_lazy(proj_id=proj_id))


@mcp.tool()
def stele_qga_score(lazy_id: str, score: int) -> str:
    """Q-GaLore score."""
    return json.dumps(get_store().qga_score(lazy_id=lazy_id, score=score))


@mcp.tool()
def stele_qga_mem(consumer_gpu: bool) -> str:
    """Q-GaLore memory flag."""
    return json.dumps(get_store().qga_mem(consumer_gpu=consumer_gpu))


@mcp.tool()
def stele_qga_loop_plan(phase: str) -> str:
    """Q-GaLore loop plan."""
    return json.dumps(get_store().qga_loop_plan(phase=phase))


@mcp.tool()
def stele_lfw_pool(task: str, n_loras: int) -> str:
    """LoRA-Flow skill pool."""
    return json.dumps(get_store().lfw_pool(task=task, n_loras=n_loras))


@mcp.tool()
def stele_lfw_gate(pool_id: str) -> str:
    """LoRA-Flow fusion gate."""
    return json.dumps(get_store().lfw_gate(pool_id=pool_id))


@mcp.tool()
def stele_lfw_token(gate_id: str) -> str:
    """LoRA-Flow token weights."""
    return json.dumps(get_store().lfw_token(gate_id=gate_id))


@mcp.tool()
def stele_lfw_score(token_id: str, score: int) -> str:
    """LoRA-Flow score."""
    return json.dumps(
        get_store().lfw_score(token_id=token_id, score=score)
    )


@mcp.tool()
def stele_lfw_few(few_shot: bool) -> str:
    """LoRA-Flow few-shot flag."""
    return json.dumps(get_store().lfw_few(few_shot=few_shot))


@mcp.tool()
def stele_lfw_loop_plan(phase: str) -> str:
    """LoRA-Flow loop plan."""
    return json.dumps(get_store().lfw_loop_plan(phase=phase))


@mcp.tool()
def stele_ros_rank(task: str, rank: int) -> str:
    """RoSA low-rank branch."""
    return json.dumps(get_store().ros_rank(task=task, rank=rank))


@mcp.tool()
def stele_ros_sparse(rank_id: str) -> str:
    """RoSA sparse residual."""
    return json.dumps(get_store().ros_sparse(rank_id=rank_id))


@mcp.tool()
def stele_ros_train(sparse_id: str) -> str:
    """RoSA train."""
    return json.dumps(get_store().ros_train(sparse_id=sparse_id))


@mcp.tool()
def stele_ros_score(train_id: str, score: int) -> str:
    """RoSA score."""
    return json.dumps(get_store().ros_score(train_id=train_id, score=score))


@mcp.tool()
def stele_ros_fft(matches_fft: bool) -> str:
    """RoSA FFT-recovery flag."""
    return json.dumps(get_store().ros_fft(matches_fft=matches_fft))


@mcp.tool()
def stele_ros_loop_plan(phase: str) -> str:
    """RoSA loop plan."""
    return json.dumps(get_store().ros_loop_plan(phase=phase))


@mcp.tool()
def stele_abb_left(task: str, rank: int) -> str:
    """ABBA left factor."""
    return json.dumps(get_store().abb_left(task=task, rank=rank))


@mcp.tool()
def stele_abb_right(left_id: str) -> str:
    """ABBA right factor."""
    return json.dumps(get_store().abb_right(left_id=left_id))


@mcp.tool()
def stele_abb_hadamard(right_id: str) -> str:
    """ABBA Hadamard."""
    return json.dumps(get_store().abb_hadamard(right_id=right_id))


@mcp.tool()
def stele_abb_score(hadamard_id: str, score: int) -> str:
    """ABBA score."""
    return json.dumps(
        get_store().abb_score(hadamard_id=hadamard_id, score=score)
    )


@mcp.tool()
def stele_abb_expr(expressive: bool) -> str:
    """ABBA expressivity flag."""
    return json.dumps(get_store().abb_expr(expressive=expressive))


@mcp.tool()
def stele_abb_loop_plan(phase: str) -> str:
    """ABBA loop plan."""
    return json.dumps(get_store().abb_loop_plan(phase=phase))


@mcp.tool()
def stele_bha_split(task: str, blocks: int) -> str:
    """BoHA block split."""
    return json.dumps(get_store().bha_split(task=task, blocks=blocks))


@mcp.tool()
def stele_bha_hadamard(split_id: str) -> str:
    """BoHA per-block Hadamard."""
    return json.dumps(get_store().bha_hadamard(split_id=split_id))


@mcp.tool()
def stele_bha_train(hadamard_id: str) -> str:
    """BoHA train."""
    return json.dumps(get_store().bha_train(hadamard_id=hadamard_id))


@mcp.tool()
def stele_bha_score(train_id: str, score: int) -> str:
    """BoHA score."""
    return json.dumps(get_store().bha_score(train_id=train_id, score=score))


@mcp.tool()
def stele_bha_local(localized: bool) -> str:
    """BoHA localized-rank flag."""
    return json.dumps(get_store().bha_local(localized=localized))


@mcp.tool()
def stele_bha_loop_plan(phase: str) -> str:
    """BoHA loop plan."""
    return json.dumps(get_store().bha_loop_plan(phase=phase))


@mcp.tool()
def stele_smo_struct(task: str, subspaces: int) -> str:
    """SMoA subspaces."""
    return json.dumps(
        get_store().smo_struct(task=task, subspaces=subspaces)
    )


@mcp.tool()
def stele_smo_mod(struct_id: str) -> str:
    """SMoA modulation."""
    return json.dumps(get_store().smo_mod(struct_id=struct_id))


@mcp.tool()
def stele_smo_train(mod_id: str) -> str:
    """SMoA train."""
    return json.dumps(get_store().smo_train(mod_id=mod_id))


@mcp.tool()
def stele_smo_score(train_id: str, score: int) -> str:
    """SMoA score."""
    return json.dumps(get_store().smo_score(train_id=train_id, score=score))


@mcp.tool()
def stele_smo_rank(high_rank: bool) -> str:
    """SMoA high-rank flag."""
    return json.dumps(get_store().smo_rank(high_rank=high_rank))


@mcp.tool()
def stele_smo_loop_plan(phase: str) -> str:
    """SMoA loop plan."""
    return json.dumps(get_store().smo_loop_plan(phase=phase))


@mcp.tool()
def stele_glo_prompt(task: str) -> str:
    """GLoRA prompt module."""
    return json.dumps(get_store().glo_prompt(task=task))


@mcp.tool()
def stele_glo_scale(prompt_id: str) -> str:
    """GLoRA scale."""
    return json.dumps(get_store().glo_scale(prompt_id=prompt_id))


@mcp.tool()
def stele_glo_search(scale_id: str) -> str:
    """GLoRA layer search."""
    return json.dumps(get_store().glo_search(scale_id=scale_id))


@mcp.tool()
def stele_glo_score(search_id: str, score: int) -> str:
    """GLoRA score."""
    return json.dumps(
        get_store().glo_score(search_id=search_id, score=score)
    )


@mcp.tool()
def stele_glo_zero(zero_infer: bool) -> str:
    """GLoRA zero-infer flag."""
    return json.dumps(get_store().glo_zero(zero_infer=zero_infer))


@mcp.tool()
def stele_glo_loop_plan(phase: str) -> str:
    """GLoRA loop plan."""
    return json.dumps(get_store().glo_loop_plan(phase=phase))


@mcp.tool()
def stele_plr_stage(task: str, stages: int) -> str:
    """PeriodicLoRA stage."""
    return json.dumps(get_store().plr_stage(task=task, stages=stages))


@mcp.tool()
def stele_plr_merge(stage_id: str) -> str:
    """PeriodicLoRA merge into W."""
    return json.dumps(get_store().plr_merge(stage_id=stage_id))


@mcp.tool()
def stele_plr_reset(merge_id: str) -> str:
    """PeriodicLoRA reinit."""
    return json.dumps(get_store().plr_reset(merge_id=merge_id))


@mcp.tool()
def stele_plr_score(reset_id: str, score: int) -> str:
    """PeriodicLoRA score."""
    return json.dumps(
        get_store().plr_score(reset_id=reset_id, score=score)
    )


@mcp.tool()
def stele_plr_rank(accum_rank: bool) -> str:
    """PeriodicLoRA accumulated-rank flag."""
    return json.dumps(get_store().plr_rank(accum_rank=accum_rank))


@mcp.tool()
def stele_plr_loop_plan(phase: str) -> str:
    """PeriodicLoRA loop plan."""
    return json.dumps(get_store().plr_loop_plan(phase=phase))


@mcp.tool()
def stele_hir_base(task: str) -> str:
    """HiRA freeze W0."""
    return json.dumps(get_store().hir_base(task=task))


@mcp.tool()
def stele_hir_factors(base_id: str, rank: int) -> str:
    """HiRA A, B factors."""
    return json.dumps(get_store().hir_factors(base_id=base_id, rank=rank))


@mcp.tool()
def stele_hir_hadamard(factors_id: str) -> str:
    """HiRA W0 ⊙ (BA)."""
    return json.dumps(get_store().hir_hadamard(factors_id=factors_id))


@mcp.tool()
def stele_hir_score(hadamard_id: str, score: int) -> str:
    """HiRA score."""
    return json.dumps(
        get_store().hir_score(hadamard_id=hadamard_id, score=score)
    )


@mcp.tool()
def stele_hir_merge(zero_infer: bool) -> str:
    """HiRA merge-into-W0 flag."""
    return json.dumps(get_store().hir_merge(zero_infer=zero_infer))


@mcp.tool()
def stele_hir_loop_plan(phase: str) -> str:
    """HiRA loop plan."""
    return json.dumps(get_store().hir_loop_plan(phase=phase))


@mcp.tool()
def stele_cnl_pack(task: str, adapters: int) -> str:
    """PLoRA concurrent pack."""
    return json.dumps(get_store().cnl_pack(task=task, adapters=adapters))


@mcp.tool()
def stele_cnl_fuse(pack_id: str) -> str:
    """PLoRA concurrent fuse."""
    return json.dumps(get_store().cnl_fuse(pack_id=pack_id))


@mcp.tool()
def stele_cnl_train(fuse_id: str) -> str:
    """PLoRA concurrent train."""
    return json.dumps(get_store().cnl_train(fuse_id=fuse_id))


@mcp.tool()
def stele_cnl_score(train_id: str, score: int) -> str:
    """PLoRA concurrent score."""
    return json.dumps(
        get_store().cnl_score(train_id=train_id, score=score)
    )


@mcp.tool()
def stele_cnl_hw(better_util: bool) -> str:
    """PLoRA concurrent util flag."""
    return json.dumps(get_store().cnl_hw(better_util=better_util))


@mcp.tool()
def stele_cnl_loop_plan(phase: str) -> str:
    """PLoRA concurrent loop plan."""
    return json.dumps(get_store().cnl_loop_plan(phase=phase))


@mcp.tool()
def stele_llr_window(task: str, ctx_len: int) -> str:
    """LongLoRA long-context window."""
    return json.dumps(get_store().llr_window(task=task, ctx_len=ctx_len))


@mcp.tool()
def stele_llr_shift(window_id: str) -> str:
    """LongLoRA S2-Attn shift."""
    return json.dumps(get_store().llr_shift(window_id=window_id))


@mcp.tool()
def stele_llr_lora(shift_id: str, rank: int) -> str:
    """LongLoRA adapter."""
    return json.dumps(get_store().llr_lora(shift_id=shift_id, rank=rank))


@mcp.tool()
def stele_llr_score(lora_id: str, score: int) -> str:
    """LongLoRA score."""
    return json.dumps(get_store().llr_score(lora_id=lora_id, score=score))


@mcp.tool()
def stele_llr_sparse(sparse_train: bool) -> str:
    """LongLoRA sparse-train flag."""
    return json.dumps(get_store().llr_sparse(sparse_train=sparse_train))


@mcp.tool()
def stele_llr_loop_plan(phase: str) -> str:
    """LongLoRA loop plan."""
    return json.dumps(get_store().llr_loop_plan(phase=phase))


@mcp.tool()
def stele_lis_layers(task: str, n: int) -> str:
    """LISA layer set."""
    return json.dumps(get_store().lis_layers(task=task, n=n))


@mcp.tool()
def stele_lis_sample(layers_id: str) -> str:
    """LISA importance sample."""
    return json.dumps(get_store().lis_sample(layers_id=layers_id))


@mcp.tool()
def stele_lis_unfreeze(sample_id: str) -> str:
    """LISA unfreeze sampled layers."""
    return json.dumps(get_store().lis_unfreeze(sample_id=sample_id))


@mcp.tool()
def stele_lis_score(unfreeze_id: str, score: int) -> str:
    """LISA score."""
    return json.dumps(
        get_store().lis_score(unfreeze_id=unfreeze_id, score=score)
    )


@mcp.tool()
def stele_lis_memory(less_opt: bool) -> str:
    """LISA optimizer-memory flag."""
    return json.dumps(get_store().lis_memory(less_opt=less_opt))


@mcp.tool()
def stele_lis_loop_plan(phase: str) -> str:
    """LISA loop plan."""
    return json.dumps(get_store().lis_loop_plan(phase=phase))


@mcp.tool()
def stele_nlr_landmark(task: str, k: int) -> str:
    """NLoRA Nyström landmarks."""
    return json.dumps(get_store().nlr_landmark(task=task, k=k))


@mcp.tool()
def stele_nlr_nystrom(landmark_id: str) -> str:
    """NLoRA Nyström sketch."""
    return json.dumps(get_store().nlr_nystrom(landmark_id=landmark_id))


@mcp.tool()
def stele_nlr_init(nystrom_id: str, rank: int) -> str:
    """NLoRA init from sketch."""
    return json.dumps(get_store().nlr_init(nystrom_id=nystrom_id, rank=rank))


@mcp.tool()
def stele_nlr_score(init_id: str, score: int) -> str:
    """NLoRA score."""
    return json.dumps(get_store().nlr_score(init_id=init_id, score=score))


@mcp.tool()
def stele_nlr_cheap(cheaper_svd: bool) -> str:
    """NLoRA cheaper-than-SVD flag."""
    return json.dumps(get_store().nlr_cheap(cheaper_svd=cheaper_svd))


@mcp.tool()
def stele_nlr_loop_plan(phase: str) -> str:
    """NLoRA loop plan."""
    return json.dumps(get_store().nlr_loop_plan(phase=phase))


@mcp.tool()
def stele_rsa_subspace(task: str, dim: int) -> str:
    """ROSA random subspace."""
    return json.dumps(get_store().rsa_subspace(task=task, dim=dim))


@mcp.tool()
def stele_rsa_project(subspace_id: str) -> str:
    """ROSA project into subspace."""
    return json.dumps(get_store().rsa_project(subspace_id=subspace_id))


@mcp.tool()
def stele_rsa_train(project_id: str) -> str:
    """ROSA train in subspace."""
    return json.dumps(get_store().rsa_train(project_id=project_id))


@mcp.tool()
def stele_rsa_score(train_id: str, score: int) -> str:
    """ROSA score."""
    return json.dumps(get_store().rsa_score(train_id=train_id, score=score))


@mcp.tool()
def stele_rsa_express(more_expressive: bool) -> str:
    """ROSA expressiveness flag."""
    return json.dumps(get_store().rsa_express(more_expressive=more_expressive))


@mcp.tool()
def stele_rsa_loop_plan(phase: str) -> str:
    """ROSA loop plan."""
    return json.dumps(get_store().rsa_loop_plan(phase=phase))


@mcp.tool()
def stele_hra_house(task: str, n: int) -> str:
    """HRA Householder vectors."""
    return json.dumps(get_store().hra_house(task=task, n=n))


@mcp.tool()
def stele_hra_reflect(house_id: str) -> str:
    """HRA compose reflections."""
    return json.dumps(get_store().hra_reflect(house_id=house_id))


@mcp.tool()
def stele_hra_train(reflect_id: str) -> str:
    """HRA train adapter."""
    return json.dumps(get_store().hra_train(reflect_id=reflect_id))


@mcp.tool()
def stele_hra_score(train_id: str, score: int) -> str:
    """HRA score."""
    return json.dumps(get_store().hra_score(train_id=train_id, score=score))


@mcp.tool()
def stele_hra_ortho(ortho_stable: bool) -> str:
    """HRA orthogonal-stable flag."""
    return json.dumps(get_store().hra_ortho(ortho_stable=ortho_stable))


@mcp.tool()
def stele_hra_loop_plan(phase: str) -> str:
    """HRA loop plan."""
    return json.dumps(get_store().hra_loop_plan(phase=phase))


@mcp.tool()
def stele_hyb_lora(task: str) -> str:
    """Hybrid PEFT LoRA-GA branch."""
    return json.dumps(get_store().hyb_lora(task=task))


@mcp.tool()
def stele_hyb_boft(lora_id: str) -> str:
    """Hybrid PEFT BOFT branch."""
    return json.dumps(get_store().hyb_boft(lora_id=lora_id))


@mcp.tool()
def stele_hyb_fuse(boft_id: str) -> str:
    """Hybrid PEFT fuse branches."""
    return json.dumps(get_store().hyb_fuse(boft_id=boft_id))


@mcp.tool()
def stele_hyb_score(fuse_id: str, score: int) -> str:
    """Hybrid PEFT score."""
    return json.dumps(get_store().hyb_score(fuse_id=fuse_id, score=score))


@mcp.tool()
def stele_hyb_stable(more_stable: bool) -> str:
    """Hybrid PEFT stability flag."""
    return json.dumps(get_store().hyb_stable(more_stable=more_stable))


@mcp.tool()
def stele_hyb_loop_plan(phase: str) -> str:
    """Hybrid PEFT loop plan."""
    return json.dumps(get_store().hyb_loop_plan(phase=phase))


@mcp.tool()
def stele_lrt_tensor(task: str, order: int) -> str:
    """LoRTA unified tensor."""
    return json.dumps(get_store().lrt_tensor(task=task, order=order))


@mcp.tool()
def stele_lrt_cp(tensor_id: str, rank: int) -> str:
    """LoRTA CP decompose."""
    return json.dumps(get_store().lrt_cp(tensor_id=tensor_id, rank=rank))


@mcp.tool()
def stele_lrt_share(cp_id: str) -> str:
    """LoRTA share factors."""
    return json.dumps(get_store().lrt_share(cp_id=cp_id))


@mcp.tool()
def stele_lrt_score(share_id: str, score: int) -> str:
    """LoRTA score."""
    return json.dumps(get_store().lrt_score(share_id=share_id, score=score))


@mcp.tool()
def stele_lrt_compact(fewer_params: bool) -> str:
    """LoRTA fewer-params flag."""
    return json.dumps(get_store().lrt_compact(fewer_params=fewer_params))


@mcp.tool()
def stele_lrt_loop_plan(phase: str) -> str:
    """LoRTA loop plan."""
    return json.dumps(get_store().lrt_loop_plan(phase=phase))


@mcp.tool()
def stele_clo_route(task: str) -> str:
    """C-LoRA shared route."""
    return json.dumps(get_store().clo_route(task=task))


@mcp.tool()
def stele_clo_task(route_id: str) -> str:
    """C-LoRA bind task."""
    return json.dumps(get_store().clo_task(route_id=route_id))


@mcp.tool()
def stele_clo_ortho(task_id: str) -> str:
    """C-LoRA orthogonality."""
    return json.dumps(get_store().clo_ortho(task_id=task_id))


@mcp.tool()
def stele_clo_score(ortho_id: str, score: int) -> str:
    """C-LoRA score."""
    return json.dumps(get_store().clo_score(ortho_id=ortho_id, score=score))


@mcp.tool()
def stele_clo_forget(less_forget: bool) -> str:
    """C-LoRA less-forgetting flag."""
    return json.dumps(get_store().clo_forget(less_forget=less_forget))


@mcp.tool()
def stele_clo_loop_plan(phase: str) -> str:
    """C-LoRA loop plan."""
    return json.dumps(get_store().clo_loop_plan(phase=phase))


@mcp.tool()
def stele_alo_init(task: str, rank: int) -> str:
    """ALoRA equal-rank init."""
    return json.dumps(get_store().alo_init(task=task, rank=rank))


@mcp.tool()
def stele_alo_ablate(init_id: str) -> str:
    """ALoRA AB-LoRA importance."""
    return json.dumps(get_store().alo_ablate(init_id=init_id))


@mcp.tool()
def stele_alo_prune(ablate_id: str) -> str:
    """ALoRA prune and reallocate."""
    return json.dumps(get_store().alo_prune(ablate_id=ablate_id))


@mcp.tool()
def stele_alo_score(prune_id: str, score: int) -> str:
    """ALoRA score."""
    return json.dumps(get_store().alo_score(prune_id=prune_id, score=score))


@mcp.tool()
def stele_alo_realloc(dynamic: bool) -> str:
    """ALoRA dynamic-realloc flag."""
    return json.dumps(get_store().alo_realloc(dynamic=dynamic))


@mcp.tool()
def stele_alo_loop_plan(phase: str) -> str:
    """ALoRA loop plan."""
    return json.dumps(get_store().alo_loop_plan(phase=phase))


@mcp.tool()
def stele_lnt_attn(task: str) -> str:
    """LN Tuning attention LN select."""
    return json.dumps(get_store().lnt_attn(task=task))


@mcp.tool()
def stele_lnt_scale(attn_id: str) -> str:
    """LN Tuning scale (gamma)."""
    return json.dumps(get_store().lnt_scale(attn_id=attn_id))


@mcp.tool()
def stele_lnt_train(scale_id: str) -> str:
    """LN Tuning train."""
    return json.dumps(get_store().lnt_train(scale_id=scale_id))


@mcp.tool()
def stele_lnt_score(train_id: str, score: int) -> str:
    """LN Tuning score."""
    return json.dumps(get_store().lnt_score(train_id=train_id, score=score))


@mcp.tool()
def stele_lnt_cheap(cheaper_than_lora: bool) -> str:
    """LN Tuning cheaper-than-LoRA flag."""
    return json.dumps(
        get_store().lnt_cheap(cheaper_than_lora=cheaper_than_lora)
    )


@mcp.tool()
def stele_lnt_loop_plan(phase: str) -> str:
    """LN Tuning loop plan."""
    return json.dumps(get_store().lnt_loop_plan(phase=phase))


@mcp.tool()
def stele_lfu_split(task: str) -> str:
    """LoRAFusion graph split."""
    return json.dumps(get_store().lfu_split(task=task))


@mcp.tool()
def stele_lfu_fuse(split_id: str) -> str:
    """LoRAFusion kernel fuse."""
    return json.dumps(get_store().lfu_fuse(split_id=split_id))


@mcp.tool()
def stele_lfu_batch(fuse_id: str, jobs: int) -> str:
    """LoRAFusion multi-job batch."""
    return json.dumps(get_store().lfu_batch(fuse_id=fuse_id, jobs=jobs))


@mcp.tool()
def stele_lfu_score(batch_id: str, score: int) -> str:
    """LoRAFusion score."""
    return json.dumps(get_store().lfu_score(batch_id=batch_id, score=score))


@mcp.tool()
def stele_lfu_speed(faster_than_mlora: bool) -> str:
    """LoRAFusion faster-than-mLoRA flag."""
    return json.dumps(
        get_store().lfu_speed(faster_than_mlora=faster_than_mlora)
    )


@mcp.tool()
def stele_lfu_loop_plan(phase: str) -> str:
    """LoRAFusion loop plan."""
    return json.dumps(get_store().lfu_loop_plan(phase=phase))


@mcp.tool()
def stele_ter_tucker(task: str, order: int) -> str:
    """TeRA tensorize ΔW."""
    return json.dumps(get_store().ter_tucker(task=task, order=order))


@mcp.tool()
def stele_ter_freeze(tucker_id: str) -> str:
    """TeRA freeze random factors."""
    return json.dumps(get_store().ter_freeze(tucker_id=tucker_id))


@mcp.tool()
def stele_ter_scale(freeze_id: str) -> str:
    """TeRA per-layer scale vectors."""
    return json.dumps(get_store().ter_scale(freeze_id=freeze_id))


@mcp.tool()
def stele_ter_score(scale_id: str, score: int) -> str:
    """TeRA score."""
    return json.dumps(get_store().ter_score(scale_id=scale_id, score=score))


@mcp.tool()
def stele_ter_highrank(high_rank_cheap: bool) -> str:
    """TeRA high-rank-cheap flag."""
    return json.dumps(
        get_store().ter_highrank(high_rank_cheap=high_rank_cheap)
    )


@mcp.tool()
def stele_ter_loop_plan(phase: str) -> str:
    """TeRA loop plan."""
    return json.dumps(get_store().ter_loop_plan(phase=phase))


@mcp.tool()
def stele_tnl_stack(task: str) -> str:
    """TensLoRA stack LoRA updates."""
    return json.dumps(get_store().tnl_stack(task=task))


@mcp.tool()
def stele_tnl_tucker(stack_id: str, ranks: int) -> str:
    """TensLoRA Tucker factor."""
    return json.dumps(get_store().tnl_tucker(stack_id=stack_id, ranks=ranks))


@mcp.tool()
def stele_tnl_mode(tucker_id: str) -> str:
    """TensLoRA per-mode ranks."""
    return json.dumps(get_store().tnl_mode(tucker_id=tucker_id))


@mcp.tool()
def stele_tnl_score(mode_id: str, score: int) -> str:
    """TensLoRA score."""
    return json.dumps(get_store().tnl_score(mode_id=mode_id, score=score))


@mcp.tool()
def stele_tnl_budget(mode_specific: bool) -> str:
    """TensLoRA mode-specific budget flag."""
    return json.dumps(get_store().tnl_budget(mode_specific=mode_specific))


@mcp.tool()
def stele_tnl_loop_plan(phase: str) -> str:
    """TensLoRA loop plan."""
    return json.dumps(get_store().tnl_loop_plan(phase=phase))


@mcp.tool()
def stele_azt_tt(task: str, cores: int) -> str:
    """AdaZeta tensor-train adapter."""
    return json.dumps(get_store().azt_tt(task=task, cores=cores))


@mcp.tool()
def stele_azt_ff(tt_id: str) -> str:
    """AdaZeta fast-forward contraction."""
    return json.dumps(get_store().azt_ff(tt_id=tt_id))


@mcp.tool()
def stele_azt_query(ff_id: str) -> str:
    """AdaZeta adaptive ZO queries."""
    return json.dumps(get_store().azt_query(ff_id=ff_id))


@mcp.tool()
def stele_azt_score(query_id: str, score: int) -> str:
    """AdaZeta score."""
    return json.dumps(get_store().azt_score(query_id=query_id, score=score))


@mcp.tool()
def stele_azt_mem(zo_memory: bool) -> str:
    """AdaZeta ZO-memory flag."""
    return json.dumps(get_store().azt_mem(zo_memory=zo_memory))


@mcp.tool()
def stele_azt_loop_plan(phase: str) -> str:
    """AdaZeta loop plan."""
    return json.dumps(get_store().azt_loop_plan(phase=phase))


@mcp.tool()
def stele_fct_tensor(task: str) -> str:
    """FacT 3D increment tensor."""
    return json.dumps(get_store().fct_tensor(task=task))


@mcp.tool()
def stele_fct_tt(tensor_id: str) -> str:
    """FacT Tensor-Train factors."""
    return json.dumps(get_store().fct_tt(tensor_id=tensor_id))


@mcp.tool()
def stele_fct_tucker(tt_id: str) -> str:
    """FacT Tucker factors."""
    return json.dumps(get_store().fct_tucker(tt_id=tt_id))


@mcp.tool()
def stele_fct_score(tucker_id: str, score: int) -> str:
    """FacT score."""
    return json.dumps(get_store().fct_score(tucker_id=tucker_id, score=score))


@mcp.tool()
def stele_fct_tiny(tiny_params: bool) -> str:
    """FacT tiny-params flag."""
    return json.dumps(get_store().fct_tiny(tiny_params=tiny_params))


@mcp.tool()
def stele_fct_loop_plan(phase: str) -> str:
    """FacT loop plan."""
    return json.dumps(get_store().fct_loop_plan(phase=phase))


@mcp.tool()
def stele_ltr_stack(task: str, layers: int) -> str:
    """LoTR stack Q/V across depth."""
    return json.dumps(get_store().ltr_stack(task=task, layers=layers))


@mcp.tool()
def stele_ltr_core(stack_id: str) -> str:
    """LoTR shared core tensor."""
    return json.dumps(get_store().ltr_core(stack_id=stack_id))


@mcp.tool()
def stele_ltr_share(core_id: str) -> str:
    """LoTR share left/right factors."""
    return json.dumps(get_store().ltr_share(core_id=core_id))


@mcp.tool()
def stele_ltr_score(share_id: str, score: int) -> str:
    """LoTR score."""
    return json.dumps(get_store().ltr_score(share_id=share_id, score=score))


@mcp.tool()
def stele_ltr_deep(better_for_deep: bool) -> str:
    """LoTR better-for-deep flag."""
    return json.dumps(get_store().ltr_deep(better_for_deep=better_for_deep))


@mcp.tool()
def stele_ltr_loop_plan(phase: str) -> str:
    """LoTR loop plan."""
    return json.dumps(get_store().ltr_loop_plan(phase=phase))


@mcp.tool()
def stele_cra_mha(task: str) -> str:
    """CaRA MHA tensor."""
    return json.dumps(get_store().cra_mha(task=task))


@mcp.tool()
def stele_cra_ffn(mha_id: str) -> str:
    """CaRA FFN tensor."""
    return json.dumps(get_store().cra_ffn(mha_id=mha_id))


@mcp.tool()
def stele_cra_cpd(ffn_id: str) -> str:
    """CaRA CP decompose."""
    return json.dumps(get_store().cra_cpd(ffn_id=ffn_id))


@mcp.tool()
def stele_cra_score(cpd_id: str, score: int) -> str:
    """CaRA score."""
    return json.dumps(get_store().cra_score(cpd_id=cpd_id, score=score))


@mcp.tool()
def stele_cra_heads(head_mode: bool) -> str:
    """CaRA head-mode flag."""
    return json.dumps(get_store().cra_heads(head_mode=head_mode))


@mcp.tool()
def stele_cra_loop_plan(phase: str) -> str:
    """CaRA loop plan."""
    return json.dumps(get_store().cra_loop_plan(phase=phase))


@mcp.tool()
def stele_ltt_adp(task: str) -> str:
    """LoRETTA adapter branch."""
    return json.dumps(get_store().ltt_adp(task=task))


@mcp.tool()
def stele_ltt_rep(adp_id: str) -> str:
    """LoRETTA reparam branch."""
    return json.dumps(get_store().ltt_rep(adp_id=adp_id))


@mcp.tool()
def stele_ltt_tt(rep_id: str) -> str:
    """LoRETTA tensor-train cores."""
    return json.dumps(get_store().ltt_tt(rep_id=rep_id))


@mcp.tool()
def stele_ltt_score(tt_id: str, score: int) -> str:
    """LoRETTA score."""
    return json.dumps(get_store().ltt_score(tt_id=tt_id, score=score))


@mcp.tool()
def stele_ltt_tiny(sub_mb: bool) -> str:
    """LoRETTA sub-MB flag."""
    return json.dumps(get_store().ltt_tiny(sub_mb=sub_mb))


@mcp.tool()
def stele_ltt_loop_plan(phase: str) -> str:
    """LoRETTA loop plan."""
    return json.dumps(get_store().ltt_loop_plan(phase=phase))


@mcp.tool()
def stele_c3a_kernel(task: str) -> str:
    """C3A convolution kernel."""
    return json.dumps(get_store().c3a_kernel(task=task))


@mcp.tool()
def stele_c3a_circ(kernel_id: str) -> str:
    """C3A circulant lift."""
    return json.dumps(get_store().c3a_circ(kernel_id=kernel_id))


@mcp.tool()
def stele_c3a_fft(circ_id: str) -> str:
    """C3A FFT multiply."""
    return json.dumps(get_store().c3a_fft(circ_id=circ_id))


@mcp.tool()
def stele_c3a_score(fft_id: str, score: int) -> str:
    """C3A score."""
    return json.dumps(get_store().c3a_score(fft_id=fft_id, score=score))


@mcp.tool()
def stele_c3a_rank(high_rank: bool) -> str:
    """C3A high-rank flag."""
    return json.dumps(get_store().c3a_rank(high_rank=high_rank))


@mcp.tool()
def stele_c3a_loop_plan(phase: str) -> str:
    """C3A loop plan."""
    return json.dumps(get_store().c3a_loop_plan(phase=phase))


@mcp.tool()
def stele_bof_block(task: str) -> str:
    """BOFT butterfly block."""
    return json.dumps(get_store().bof_block(task=task))


@mcp.tool()
def stele_bof_orth(block_id: str) -> str:
    """BOFT orthogonal factor."""
    return json.dumps(get_store().bof_orth(block_id=block_id))


@mcp.tool()
def stele_bof_butter(orth_id: str) -> str:
    """BOFT butterfly factorize."""
    return json.dumps(get_store().bof_butter(orth_id=orth_id))


@mcp.tool()
def stele_bof_score(butter_id: str, score: int) -> str:
    """BOFT score."""
    return json.dumps(get_store().bof_score(butter_id=butter_id, score=score))


@mcp.tool()
def stele_bof_full(full_rank: bool) -> str:
    """BOFT full-orthogonal flag."""
    return json.dumps(get_store().bof_full(full_rank=full_rank))


@mcp.tool()
def stele_bof_loop_plan(phase: str) -> str:
    """BOFT loop plan."""
    return json.dumps(get_store().bof_loop_plan(phase=phase))


@mcp.tool()
def stele_sdt_dim(task: str) -> str:
    """SDT sparse SSM dimension."""
    return json.dumps(get_store().sdt_dim(task=task))


@mcp.tool()
def stele_sdt_mask(dim_id: str) -> str:
    """SDT sparse mask."""
    return json.dumps(get_store().sdt_mask(dim_id=dim_id))


@mcp.tool()
def stele_sdt_tune(mask_id: str) -> str:
    """SDT sparse dimension tune."""
    return json.dumps(get_store().sdt_tune(mask_id=mask_id))


@mcp.tool()
def stele_sdt_score(tune_id: str, score: int) -> str:
    """SDT score."""
    return json.dumps(get_store().sdt_score(tune_id=tune_id, score=score))


@mcp.tool()
def stele_sdt_ssm(ssm_only: bool) -> str:
    """SDT SSM-targeted flag."""
    return json.dumps(get_store().sdt_ssm(ssm_only=ssm_only))


@mcp.tool()
def stele_sdt_loop_plan(phase: str) -> str:
    """SDT loop plan."""
    return json.dumps(get_store().sdt_loop_plan(phase=phase))


@mcp.tool()
def stele_mef_adapt(task: str) -> str:
    """MEFT sparse adapter."""
    return json.dumps(get_store().mef_adapt(task=task))


@mcp.tool()
def stele_mef_route(adapt_id: str) -> str:
    """MEFT MoE / key-expert router."""
    return json.dumps(get_store().mef_route(adapt_id=adapt_id))


@mcp.tool()
def stele_mef_fetch(route_id: str) -> str:
    """MEFT sparse neuron fetch."""
    return json.dumps(get_store().mef_fetch(route_id=route_id))


@mcp.tool()
def stele_mef_score(fetch_id: str, score: int) -> str:
    """MEFT score."""
    return json.dumps(get_store().mef_score(fetch_id=fetch_id, score=score))


@mcp.tool()
def stele_mef_cpu(cpu_offload: bool) -> str:
    """MEFT CPU-offload flag."""
    return json.dumps(get_store().mef_cpu(cpu_offload=cpu_offload))


@mcp.tool()
def stele_mef_loop_plan(phase: str) -> str:
    """MEFT loop plan."""
    return json.dumps(get_store().mef_loop_plan(phase=phase))


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
