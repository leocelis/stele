# Stele Roadmap

Phases, in order. The [system intent](stele_system_intent.yaml) is the contract;
its joint-satisfaction test gates every implementation phase.

<<<<<<< HEAD
=======
**Handoff (2026-08-28):** [`docs/handoff/2026-08-28-v18-15-peft-proxy-catalog.md`](docs/handoff/2026-08-28-v18-15-peft-proxy-catalog.md)

>>>>>>> origin/main
## Current tip (2026-08-28)

| | |
|---|---|
| **Shipped** | **v18.16.1** — Hosted MCP doctor works on MySQL SoT (backend-agnostic verify). MCP tools unchanged. |
| **Next** | Phase 192 / v18.16 — two unused PEFT proxies. **Not started.** Prefixes not locked. |
| **Pending** | Phase 192 + Post-v18.15 list below. Phases 0–191 are done. |

## Phase 0 — Research + design intent ✅

- ✅ Source-audited research + patterns + PRD + tech spec
- ✅ Human go to implement (2026-08-20)
- ✅ Frontiers research pass (2026-08-20) — MemoryArena, Governed Memory, memorywire, survey

## Phase 1 — Contract + store core ✅

- ✅ Entry schema, file SoT + journal, six ops as pure library
- ✅ Purity tests (C1, C5) green

## Phase 2 — Governance runtime ✅

- ✅ Quarantine → promote with evidence contract
- ✅ REFLECT: dedupe / expire / surface conflicts (no auto-resolve)
- ✅ Contested resolution via evidenced supersede (`resolve_contested`)
- ✅ Self-graded never promotes (C7)

## Phase 3 — Tool surface + retrieval ✅

- ✅ MCP server (`stele-mcp`) — named tools (26 at v1.0)
- ✅ Hybrid retrieval (BM25 + optional caller embedder + temporal)
- ✅ Index rebuild lossless (C4)

## Phase 4 — Producers + seed tooling ✅

- ✅ operator receipt projection adapter (C8)
- ✅ Migration producer shape: `provenance.agent="migration"` via normal ADD
- ✅ Judgment wire adapter (`judgment_entry`) — callers ship codified dicts; Stele stays pure

## Phase 5 — Pack export + evaluation ✅ (scoped)

- ✅ Pack export with redaction / tiers / stamps (C3)
- ✅ Subject allowlist + adaptation operators (FF-7/9)
- ✅ Minimal with-vs-without task-outcome harness (`stele_core.harness`)
- ✅ Workflow env-gate task family (`workflow_env_gate_suite`, FF-4)
- ✅ Scoped foreign-pack transfer eval (`foreign_pack_transfer_eval` + `hydrate`) — not WTP
- ✅ Living ledger + ops dashboard (v0.1.6–0.1.7)
- ⏳ Cross-org WTP / product pricing claims — out of scope (research / non-goal)

## Phase 6 — v1.0 fully featured protocol ✅

- ✅ Operator CLI (`stele`)
- ✅ Entry JSON Schema 2020-12 published
- ✅ Snapshot + doctor
- ✅ memorywire-shaped projection (no dependency)
- ✅ MCP parity for attach / snapshot / doctor / schema
- ✅ PRD + TECH_SPEC + ARCHITECTURE at v1.0
- ✅ Joint + proof_run gates green

## Phase 7 — v1.1 recovery + eval depth ✅

- ✅ Provenance purge (dry-run / execute)
- ✅ Batch ADD, store diff, trusted-source Select
- ✅ MemBench-shaped local harness report
- ✅ Frontiers research §§9–10

## Phase 8 — v1.2 hygiene + governance eval ✅

- ✅ `entangled_suspects` (LINK-neighborhood human-review queue)
- ✅ `hygiene_candidates` (zombie / net-harm / stale — report only)
- ✅ `search(..., prefer_fresh=True)` (SSGM-style soft rank)
- ✅ `governance_shaped_report` harness
- ✅ Frontiers research §§11–13 (MemArchitect, SSGM, governance metrics)
- ✅ MCP tools → 31; CLI `hygiene` / `entangled`

## Phase 9 — v1.3 multi-principal ACL + forgetting ✅

- ✅ `search(..., principal_scopes=)` (GateMem ACL — no implicit universal)
- ✅ `forget_compliance` post-erasure probe
- ✅ `gatemem_shaped_report` (utility ∩ ACL ∩ forgetting proxies)
- ✅ Frontiers research §§14–16 (GateMem, governed shared memory, agent-native study)
- ✅ MCP tools → 32; CLI `forget-check`

## Phase 10 — v1.4 bi-temporal + conflict-preserving ✅

- ✅ `lineage` (TOKI audit supersede chain)
- ✅ `belief_at` (point-in-time belief)
- ✅ `conflict_surface` (StateFuse-preserving pairs)
- ✅ `memoryagent_shaped_report` (four competencies)
- ✅ Frontiers research §§17–19
- ✅ MCP tools → 35; CLI `lineage` / `belief-at` / `conflicts`

## Phase 11 — v1.5 injection gates + compress plan ✅

- ✅ `injection_scan` + `risk.py` marker catalog (MIND-inspired, no LLM)
- ✅ `withhold_injection_suspects` / `block_injection_suspects` (MAPLE gates)
- ✅ `select_budget_plan` + `maple_shaped_report`
- ✅ Frontiers research §§20–21
- ✅ MCP tools → 37; CLI `injection-scan` / `budget-plan`

## Phase 12 — v1.6 seals + attribution ✅

- ✅ `store_seal` / `verify_seal` / `entry_content_digest`
- ✅ `attribution_receipt` / `replay_consistency` (PURGE retains `removed` ids)
- ✅ `memmark_shaped_report`
- ✅ Frontiers research §§22–23 (MemMark, TRACE)
- ✅ MCP tools → 41; CLI `seal` / `verify-seal` / `receipt` / `replay-check`

## Phase 13 — v1.7 lifecycle + TEPA revoke + pack seals ✅

- ✅ `lifecycle_tier` / `lifecycle_inventory` / `search(..., lifecycle_tiers=)` (AMV-L)
- ✅ `conflict_key` + `revoke_by_key` / `unrevoke` (TEPA; state `revoked`)
- ✅ `pack_seal` / `verify_pack_seal`
- ✅ `search_explain` + `tepa_amvl_shaped_report`
- ✅ Frontiers research §§24–26
- ✅ MCP tools → 47; CLI `lifecycle` / `revoke-key` / `pack-seal` / `explain`

## Phase 14 — v1.8 graph federation proxies ✅

- ✅ `blast_radius` (LINK neighborhood)
- ✅ `merge_classify` (MELD five-outcome; report-only)
- ✅ `path_trust` + `min_path_trust` Select filter
- ✅ `meld_map_shaped_report`
- ✅ Frontiers research §§27–29 (MELD, MAP-Graph, RippleMem)
- ✅ MCP tools → 50; CLI `blast` / `merge-classify` / `path-trust`

## Phase 15 — v1.9 journal chain + activation ✅

- ✅ Journal `prev_hash`/`row_hash` + `verify_journal_chain` (GPM)
- ✅ `spread_activate` (SYNAPSE)
- ✅ `connection_density` / `prefer_dense` (SodaMem)
- ✅ `retention_score` / `min_retention` (Oblivion)
- ✅ `soda_synapse_shaped_report`
- ✅ Frontiers research §§30–33
- ✅ MCP tools → 55; CLI `journal-chain` / `spread` / `density` / `retention`

## Phase 16 — v2.0 release gate + derived index ✅

- ✅ `health_report` + `release_gate` (fail-closed; GPM-shaped)
- ✅ `cue_tags` + Select cue filter
- ✅ Optional derived SQLite FTS (`rebuild_sqlite_index` / `search_sqlite`) — SoT stays files
- ✅ `gpm_release_shaped_report`
- ✅ Frontiers research §§34–35
- ✅ MCP tools → 59; CLI `health` / `release-gate` / `rebuild-index` / `search-sqlite`

## Phase 17 — v2.1 decision receipts + import verify + lineage trust ✅

- ✅ Decision receipts on release (GPM local record; optional abstain audit)
- ✅ `verify_import` + `hydrate(require_verify=True)` (PAM-shaped halt-on-first-failure)
- ✅ Export `policy` / `policy_digest` / `policy_manifest.json`
- ✅ `lineage_trust` + `refuse_untrusted_lineage` Select filter (MemLineage-shaped)
- ✅ `pam_cava_shaped_report`
- ✅ Frontiers research §§36–38
- ✅ MCP tools → 63; CLI `verify-import` / `decisions` / `lineage-trust`

## Phase 18 — v2.2 PoEM execution + PPMF authority + claim closure ✅

- ✅ Independent execution ledger (`record_execution` / `verify_execution`) — PoEM-shaped
- ✅ `authority_gate` non-amplification firewall — PPMF-shaped
- ✅ `claim_closure` exact promoted-fact closure — GPM-shaped
- ✅ `poem_ppmf_shaped_report`
- ✅ Frontiers research §§39–41
- ✅ MCP tools → 67; CLI `record-exec` / `verify-exec` / `authority-gate` / `claim-closure`

## Phase 19 — v2.3 MemoRepair cascade + non-revival ✅

- ✅ `cascade_impact` / `cascade_exposure` (invalidated descendant exposure)
- ✅ `withdraw_cascade` barrier-first revoke of fault+descendants
- ✅ `repair_plan` predecessor-closed selection (greedy proxy; not exact min-cut)
- ✅ `non_revival_probe`
- ✅ `memorepair_shaped_report`
- ✅ Frontiers research §§42–43
- ✅ MCP tools → 71; CLI `cascade` / `withdraw-cascade` / `repair-plan`

## Phase 20 — v2.4 MemIR roles + D-Mem dual channel ✅

- ✅ Optional `memory_role` (evidence/claim/decision) + JSON Schema
- ✅ `fact_interface` / `role_collapse_scan` / `claims_only` Select
- ✅ `claim_closure(require_claim_role=True)`
- ✅ `quality_gate` + `dual_channel_search`
- ✅ `memir_dmem_shaped_report`
- ✅ Frontiers research §§44–45
- ✅ MCP tools → 75; CLI `fact-interface` / `role-scan` / `dual-search`

## Phase 21 — v2.5 GitOfThoughts commits + copyability ✅

- ✅ `commit_view` / `checkout_view` / `diff_commits` / `merge_branches` (stdlib commit log)
- ✅ `copyability_gate` (near-duplicate threshold proxy)
- ✅ `gitofthoughts_shaped_report`
- ✅ Frontiers research §§46–47
- ✅ MCP tools → 79; CLI `commit` / `checkout` / `diff-commits` / `copyability`

## Phase 22 — v2.6 ChronoMem version + MemStrata supersession ✅

- ✅ `pin_memory_version` / `activate_version` / `counterfactual_search` (read_head overlay)
- ✅ `exclude_superseded` / `stale_fact_scan` / `_version_select`
- ✅ `chronomem_strata_shaped_report`
- ✅ Frontiers research §§48–49
- ✅ MCP tools → 83; CLI `pin-version` / `activate-version` / `stale-facts`

## Phase 23 — v2.7 TARL updates + Memory Worth ✅

- ✅ `propose_update` / `apply_update` / `ledger_view` (five actions)
- ✅ `memory_worth` / `low_worth_scan` / Select `min_worth`
- ✅ `tarl_mw_shaped_report`
- ✅ Frontiers research §§50–51
- ✅ MCP tools → 88; CLI `propose-update` / `apply-update` / `ledger-view` / `memory-worth` / `low-worth`

## Phase 24 — v2.8 MemTX belief-commit + action-safety ✅

- ✅ `begin_transaction` / `stage_write` / `commit_transaction` / `abort_transaction`
- ✅ `action_safe_gate` / `in_flight_report` / `aoep_report`
- ✅ `memtx_aoep_shaped_report`
- ✅ Frontiers research §§52–53
- ✅ MCP tools → 94; CLI `begin-tx` / `commit-tx` / `abort-tx` / `action-safe` / `in-flight`

## Phase 25 — v2.9 LatticeMind + Cordon outbox ✅

- ✅ `symbolic_conflict_scan` / `classify_conflict` / `compact_render`
- ✅ `stage_effect` / `release_effects` / effect lifecycle
- ✅ `lattice_cordon_shaped_report`
- ✅ Frontiers research §§54–55
- ✅ MCP tools → 100; CLI `symbolic-conflicts` / `classify-conflict` / `compact-render` / `stage-effect` / `list-effects`

## Phase 26 — v3.0 STALE/VTA + GEM ✅

- ✅ `state_resolution` / `premise_resistance` / `ipa_gap_scan` / `related_slot_scan`
- ✅ `verify_transition` (VTA-shaped)
- ✅ `gem_report`
- ✅ `stale_gem_shaped_report`
- ✅ Frontiers research §§56–57
- ✅ MCP tools → 106; CLI `state-resolution` / `premise-resistance` / `verify-transition` / `related-slots` / `gem-report`

## Phase 27 — v3.1 StateFuse projection + TOKI ops + MemArchitect bid ✅

- ✅ `project_resolve` / `pin_projection` / `correction_handle`
- ✅ `toki_classify_operator` / `toki_anomaly_scan`
- ✅ `context_bid`
- ✅ `statefuse_toki_shaped_report`
- ✅ Frontiers research §§58–60
- ✅ MCP tools → 114; CLI `project-resolve` / `correction-handle` / `pin-projection` / `toki-classify` / `toki-anomalies` / `context-bid`

## Phase 28 — v3.2 MemoRepair min-cut + CUPMem + CMGL ✅

- ✅ `repair_select_mincut` (exact s–t min-cut)
- ✅ `adjudicate_update` / `unknown_current_slots` / `authorize_retrieval`
- ✅ `admit_gate` / `list_admit_receipts` / `verify_admit_receipt`
- ✅ `memorepair_cupmem_cmgl_shaped_report`
- ✅ Frontiers research §§61–63
- ✅ MCP tools → 120; CLI `repair-mincut` / `adjudicate` / `unknown-slots` / `authorize-retrieval` / `admit-gate`

## Phase 29 — v3.3 TierMem + MSCE ✅

- ✅ `put_raw_page` / `sufficiency_gate` / `escalate_raw` / `verified_writeback`
- ✅ `skill_eligibility` / `crystallize_skill` / `value_backfill` / `skill_catalog`
- ✅ `tiermem_msce_shaped_report`
- ✅ Frontiers research §§64–65
- ✅ MCP tools → 127; CLI `put-raw` / `sufficiency` / `escalate-raw` / `writeback` / `crystallize-skill` / `skill-catalog`

## Phase 30 — v3.4 FadeMem + SSGM Weibull + MemR3 ✅

- ✅ `fade_strength` / `fade_scan` / `fusion_candidates`
- ✅ `weibull_relevance` + Select `min_weibull`
- ✅ `evidence_gap` / `reflective_retrieve` / `gap_tracker_update`
- ✅ `fademem_memr3_shaped_report`
- ✅ Frontiers research §§66–68
- ✅ MCP tools → 133; CLI `fade-scan` / `fusion-candidates` / `weibull` / `evidence-gap` / `reflective-retrieve`

## Phase 31 — v3.5 Archive tier + SF-AMS CIS + MemCon ✅

- ✅ `archive_plan` / `archive_apply` / `unarchive` / `list_archived` (`archived` state)
- ✅ `composite_importance` / `cis_scan`
- ✅ `control_suggest`
- ✅ `archive_sfams_memcon_shaped_report`
- ✅ Frontiers research §§69–71
- ✅ MCP tools → 140; CLI `archive-plan` / `archive-apply` / `unarchive` / `cis` / `cis-scan` / `control-suggest`

## Phase 32 — v3.6 SCM sleep + GAM buffer + ACM anticipate ✅

- ✅ `value_tag` / working-memory overlay / `sleep_trigger` / `sleep_plan` / `sleep_apply_nrem`
- ✅ `episodic_buffer` / `semantic_boundary` / `consolidate_plan`
- ✅ `anticipate` / `verify_compaction`
- ✅ `scm_gam_acm_shaped_report`
- ✅ Frontiers research §§72–74
- ✅ MCP tools → 151; CLI `value-tag` / `wm-*` / `sleep-*` / `episodic-buffer` / `semantic-boundary` / `consolidate-plan` / `anticipate` / `verify-compaction`

## Phase 33 — v3.7 LightMem + HippoRAG + Quipu/MAP-Graph ✅

- ✅ `sensory_filter` / `stage_inventory` / `topic_segments` / `stage_budget_plan`
- ✅ `ppr_scores` / `multi_hop_retrieve`
- ✅ `write_gate` / `action_risk_gate`
- ✅ `lightmem_hippo_quipu_shaped_report`
- ✅ Frontiers research §§75–77
- ✅ MCP tools → 159; CLI `sensory-filter` / `stage-*` / `multi-hop` / `write-gate` / `action-risk-gate`

## Phase 34 — v3.8 ProGraph + EMG + AgentIR ✅

- ✅ `extract_residuals` / `register_entities` / `profile_expand` / `residual_augment`
- ✅ `match_correction` / `insight_inject`
- ✅ `cascade_route` / `multi_channel_fuse`
- ✅ `prograph_emg_agentir_shaped_report`
- ✅ Frontiers research §§78–80
- ✅ MCP tools → 167; CLI `residuals` / `entities` / `profile-expand` / `residual-augment` / `match-correction` / `insight-inject` / `cascade-route` / `multi-channel`

## Phase 35 — v3.9 Governed Memory + HyMem ✅

- ✅ `dual_project` / `governance_route` / `session_delta_*` / `entity_context` / `entity_leak_probe`
- ✅ `hymem_classify_slot` / `hymem_isolate_pack`
- ✅ `govmem_hymem_shaped_report`
- ✅ Frontiers research §§81–83
- ✅ MCP tools → 176; CLI `dual-project` / `governance-route` / `session-delta-*` / `entity-context` / `entity-leak-probe` / `hymem-slot` / `hymem-isolate`

## Phase 36 — v4.0 Deterministic freshness + MemTxn + Fleet ✅

- ✅ `extract_version_markers` / `freshness_resolve` / `assemble_current` / `hop_freshness`
- ✅ `patch_test` / `temporal_resolve` / `recover_active_map`
- ✅ `fleet_scope_gate` / `propagate_plan` / `stale_propagation_scan`
- ✅ `freshness_memtxn_fleet_shaped_report`
- ✅ Frontiers research §§84–86
- ✅ MCP tools → 186; CLI `version-markers` / `freshness-resolve` / `assemble-current` / `hop-freshness` / `patch-test` / `temporal-resolve` / `recover-active-map` / `fleet-scope-gate` / `propagate-plan` / `stale-propagation`

## Phase 37 — v4.1 BudgetMem + skill ranker + ERSkill ✅

- ✅ `query_complexity` / `budget_tier_route` / `budget_module_plan`
- ✅ `skill_rank` / `skill_prereq_expand`
- ✅ `list_retrieval_primitives` / `list_retrieval_skills` / `compose_retrieval_skill` / `route_retrieval_skill` / `run_retrieval_skill`
- ✅ `budgetmem_erskill_shaped_report`
- ✅ Frontiers research §§87–89
- ✅ MCP tools → 196; CLI `query-complexity` / `budget-tier-route` / `budget-module-plan` / `skill-rank` / `skill-prereq` / `retrieval-skills` / `route-retrieval-skill` / `run-retrieval-skill`

## Phase 38 — v4.2 ConsistencyGate + MemGate + sovereignty ✅

- ✅ `support_score` / `consistency_admit`
- ✅ `retrieval_admit` / `task_conditioned_pack`
- ✅ `sovereignty_checklist` / `post_delete_verify` / `rollback_plan`
- ✅ `consistency_memgate_sovereignty_shaped_report`
- ✅ Frontiers research §§90–92
- ✅ MCP tools → 203; CLI `support-score` / `consistency-admit` / `retrieval-admit` / `task-pack` / `sovereignty-checklist` / `post-delete-verify` / `rollback-plan`

## Phase 39 — v4.3 SodaMem + MemRefine + Ariadne/MemFuse ✅

- ✅ `density_fuse` / `evidence_plan` / `cited_pack`
- ✅ `compress_candidates` / `refine_plan`
- ✅ `merge_link_add` / `bridge_discover` / `fuse_cluster`
- ✅ `sodamem_memrefine_ariadne_shaped_report`
- ✅ Frontiers research §§93–95
- ✅ MCP tools → 211; CLI `density-fuse` / `evidence-plan` / `cited-pack` / `compress-candidates` / `refine-plan` / `merge-link-add` / `bridge-discover` / `fuse-cluster`

## Phase 40 — v4.4 TGMS + MemoryData localized maintenance ✅

- ✅ `result_digest` / `operator_cost_estimate` / `plan_static_verify` / `claim_verify` / `summary_quarantine_scan`
- ✅ `localized_maintenance_plan` / `maintenance_cost_compare`
- ✅ `tgms_memdata_shaped_report`
- ✅ Frontiers research §§96–98
- ✅ MCP tools → 218; CLI `result-digest` / `operator-cost` / `plan-verify` / `claim-verify` / `summary-quarantine` / `local-maint` / `maint-cost`

## Phase 41 — v4.5 TMA-NM + AM-Sentry ✅

- ✅ `origin_bind` / `propagate_origin` / `launder_scan` / `act_authority_gate`
- ✅ `save_policy` / `retrieval_screen`
- ✅ `tmanm_amsentry_shaped_report`
- ✅ Frontiers research §§99–101
- ✅ MCP tools → 224; CLI `origin-bind` / `propagate-origin` / `launder-scan` / `act-authority` / `save-policy` / `retrieval-screen`

## Phase 42 — v4.6 MemForest/MemTree + xMemory ✅

- ✅ `build_memtree` / `dirty_path_plan` / `coarse_to_fine`
- ✅ `build_themes` / `theme_attach` / `split_merge_plan` / `top_down_pack`
- ✅ `memforest_xmemory_shaped_report`
- ✅ Frontiers research §§102–104
- ✅ MCP tools → 231; CLI `build-memtree` / `dirty-path` / `coarse-to-fine` / `build-themes` / `theme-attach` / `split-merge` / `top-down-pack`

## Phase 43 — v4.7 MemSecBench + SleepGate + A-MemGuard ✅

- ✅ `persistence_probe` / `execute_chain_probe` / `selective_repair_plan` / `lifecycle_report`
- ✅ `conflict_tag` / `forget_gate_plan` / `consolidate_survivors` / `pi_depth_scan`
- ✅ `consensus_admit`
- ✅ `memsec_sleepgate_amemguard_shaped_report`
- ✅ Frontiers research §§105–107
- ✅ MCP tools → 240; CLI `persistence-probe` / `execute-chain-probe` / `lifecycle-report` / `selective-repair` / `conflict-tag` / `forget-gate` / `consolidate-survivors` / `pi-depth` / `consensus-admit`

## Phase 44 — v4.8 DepRepair + MPBench ✅

- ✅ `build_mem_action_graph` / `dependency_trace` / `preserve_independent` / `selective_replay_plan`
- ✅ `classify_write_channel` / `source_isolation_gate` / `write_channel_inventory` / `channel_admit_batch`
- ✅ `deprepair_mpbench_shaped_report`
- ✅ Frontiers research §§108–109
- ✅ MCP tools → 248; CLI `mem-action-graph` / `dependency-trace` / `preserve-independent` / `selective-replay` / `classify-write-channel` / `source-isolation` / `write-channel-inventory` / `channel-admit-batch`

## Phase 45 — v4.9 MemPoison + Salami ✅

- ✅ `slot_coverage` / `threat_tier_classify` / `dormant_trigger_scan` / `mempoison_ladder_report`
- ✅ `compositional_coalition_scan` / `collusion_risk_gate` / `salami_pair_probe`
- ✅ `mempoison_salami_shaped_report`
- ✅ Frontiers research §§110–111
- ✅ MCP tools → 255; CLI `slot-coverage` / `threat-tier` / `dormant-scan` / `coalition-scan` / `collusion-gate` / `mempoison-ladder` / `salami-pair`

## Phase 46 — v5.0 Knowledge-layer + Credential reject + Uncertainty gate ✅

- ✅ `classify_persistence_layer` / `persistence_policy` / `layer_inventory` / `knowledge_protect_scan` / `intelligence_reject_gate`
- ✅ `credential_scan` / `credential_reject_gate` / `credential_store_scan`
- ✅ `uncertainty_score` / `uncertainty_retrieve_gate` / `reasoning_reserve_plan`
- ✅ `knowledgelayer_cred_uncertainty_shaped_report`
- ✅ Frontiers research §§112–114
- ✅ MCP tools → 266; CLI `persistence-layer` / `persistence-policy` / `layer-inventory` / `knowledge-protect` / `intelligence-reject` / `credential-scan` / `credential-reject` / `credential-store-scan` / `uncertainty-score` / `uncertainty-gate` / `reasoning-reserve`

## Phase 47 — v5.1 PAM deepen + CapSeal ✅

- ✅ `classify_memory_component` / `build_merkle_dag` / `verify_merkle_root` / `issue_capability_token` / `check_capability` / `selective_disclose` / `rehydrate_safe_plan`
- ✅ `issue_action_capability` / `capability_export_probe` / `check_action_capability` / `action_capability_inventory`
- ✅ `pam_capseal_shaped_report`
- ✅ Frontiers research §§115–116
- ✅ MCP tools → 277; CLI `memory-component` / `merkle-dag` / `verify-merkle` / `issue-cap-token` / `check-cap-token` / `selective-disclose` / `rehydrate-safe` / `issue-action-cap` / `cap-export-probe` / `check-action-cap`

## Phase 48 — v5.2 AgentDoG + MemWeaver ✅

- ✅ `classify_risk_source` / `classify_failure_mode` / `classify_real_world_harm` / `diagnose_trajectory_step` / `diagnose_trajectory` / `safe_but_unreasonable_scan` / `taxonomy_inventory`
- ✅ `weave_layer_assign` / `build_hybrid_weave` / `dual_channel_retrieve` / `experience_abstract_plan` / `temporal_session_conflict_scan` / `multi_hop_depth_score`
- ✅ `agentdog_memweaver_shaped_report`
- ✅ Frontiers research §§117–119
- ✅ MCP tools → 290; CLI `risk-source` / `failure-mode` / `real-world-harm` / `diagnose-step` / `diagnose-trajectory` / `unreasonable-scan` / `taxonomy-inventory` / `weave-layer` / `hybrid-weave` / `dual-channel` / `experience-abstract` / `temporal-conflict` / `hop-depth`

## Phase 49 — v5.3 MemEvolve + MindMemOS + MEMGUARD ✅

- ✅ `list_design_space` / `architecture_profile` / `diagnose_architecture` / `propose_architecture_variants` / `rank_architecture_fitness` / `select_architecture_parents`
- ✅ `ept_classify` / `dreaming_consolidate_plan` / `feedback_revise_plan` / `skill_evolve_plan`
- ✅ `functional_role_assign` / `contamination_scan` / `type_route_retrieve`
- ✅ `memevolve_mindmemos_shaped_report`
- ✅ Frontiers research §§120–122
- ✅ MCP tools → 303; CLI `design-space` / `arch-profile` / `arch-diagnose` / `arch-variants` / `arch-rank` / `arch-parents` / `ept` / `functional-role` / `contamination-scan` / `type-route` / `dreaming-plan` / `feedback-revise` / `skill-evolve`

## Phase 50 — v5.4 PAMU + BEAM + HaluMem ✅

- ✅ `extract_preference_signal` / `fuse_preference` / `preference_change_detect` / `preference_update_plan` / `format_preference_prompt`
- ✅ `beam_category_inventory` / `classify_beam_query` / `knowledge_update_check` / `abstention_gate` / `contradiction_resolve_plan` / `event_order_check` / `beam_eval_pack`
- ✅ `localize_hallucination_stage`
- ✅ `pamu_beam_shaped_report`
- ✅ Frontiers research §§123–125
- ✅ MCP tools → 316; CLI `pref-signal` / `pref-update` / `pref-fuse` / `pref-change` / `pref-prompt` / `beam-categories` / `beam-classify` / `knowledge-update` / `abstention-gate` / `contradiction-plan` / `event-order` / `halu-stage`

## Phase 51 — v5.5 REMem + EverMemOS ✅

- ✅ `extract_episodic_gist` / `extract_temporal_facts` / `situational_bind` / `build_hybrid_episodic_graph` / `agentic_retrieve_plan` / `ordinal_event_query`
- ✅ `form_memcell` / `consolidate_memscenes` / `foresight_filter` / `reconstructive_recollect` / `profile_evolve_plan` / `necessity_sufficiency_check`
- ✅ `remem_evermemos_shaped_report`
- ✅ Frontiers research §§126–127
- ✅ MCP tools → 328; CLI `episodic-gist` / `temporal-facts` / `situational-bind` / `episodic-graph` / `agentic-retrieve` / `ordinal-event` / `memcell` / `memscenes` / `foresight-filter` / `recollect` / `profile-evolve` / `necessity-check`

## Phase 52 — v5.6 MemoryOS + NEMORI ✅

- ✅ `classify_memory_tier` / `heat_score` / `segment_pages` / `stm_to_mtm_plan` / `mtm_evict_plan` / `promote_to_lpm_plan` / `hierarchical_retrieve`
- ✅ `integrate_episodic_narrative` / `anticipatory_schema` / `prediction_error_distill` / `deserves_memory_gate` / `distill_batch_plan`
- ✅ `memoryos_nemori_shaped_report`
- ✅ Frontiers research §§128–129
- ✅ MCP tools → 340; CLI `memory-tier` / `heat-score` / `segment-pages` / `stm-to-mtm` / `mtm-evict` / `promote-lpm` / `hier-retrieve` / `episodic-narrative` / `anticipatory-schema` / `prediction-error` / `deserves-memory` / `distill-batch`

## Phase 53 — v5.7 Hindsight + ReasoningBank ✅

- ✅ `classify_network` / `retain_plan` / `network_inventory` / `recall_multi_strategy` / `opinion_reinforce` / `reflect_plan`
- ✅ `distill_strategy_item` / `failure_lesson_gate` / `retrieve_strategies` / `consolidate_strategy_plan` / `matts_contrastive_plan`
- ✅ `hindsight_reasoningbank_shaped_report`
- ✅ Frontiers research §§130–131
- ✅ MCP tools → 351; CLI `classify-network` / `retain-plan` / `network-inventory` / `recall-multi` / `opinion-reinforce` / `reflect-plan` / `distill-strategy` / `failure-lesson-gate` / `matts-plan`

## Phase 54 — v5.8 MemSkill + Memory-R1 ✅

- ✅ `init_skill_bank` / `span_partition` / `select_skills` / `execute_skill_plan` / `record_hard_case` / `designer_evolve_plan`
- ✅ `classify_memory_op` / `noop_gate` / `memory_op_plan` / `conflict_update_plan` / `delete_stale_plan`
- ✅ `memskill_memoryr1_shaped_report`
- ✅ Frontiers research §§132–133
- ✅ MCP tools → 362; CLI `skill-bank` / `span-partition` / `select-skills` / `execute-skills` / `hard-case` / `designer-evolve` / `memory-op` / `noop-gate` / `memory-op-plan` / `conflict-update` / `delete-stale`

## Phase 55 — v5.9 G-Memory + MemMA ✅

- ✅ `classify_graph_tier` / `build_query_graph` / `upward_insight_traverse` / `downward_interaction_traverse` / `bidirectional_retrieve` / `hierarchy_update_plan`
- ✅ `meta_thinker_guidance` / `answerability_check` / `synthesize_probe_qa` / `verify_probes` / `repair_from_probes`
- ✅ `gmemory_memma_shaped_report`
- ✅ Frontiers research §§134–135
- ✅ MCP tools → 373; CLI `graph-tier` / `query-graph` / `insight-up` / `interaction-down` / `bidir-retrieve` / `hierarchy-update` / `meta-thinker` / `answerability` / `probe-qa` / `verify-probes` / `repair-probes`

## Phase 56 — v6.0 AWM + RRM ✅

- ✅ `induce_workflow` / `online_induce_gate` / `workflow_memory_add_plan` / `retrieve_workflows` / `workflow_step_budget`
- ✅ `distill_retrieval_experience` / `anomaly_trigger` / `query_level_guidance` / `experience_lifecycle_score` / `prune_experience_plan` / `isolate_factual_from_procedural`
- ✅ `awm_rrm_shaped_report`
- ✅ Frontiers research §§136–137
- ✅ MCP tools → 384; CLI `induce-workflow` / `online-induce-gate` / `workflow-add-plan` / `retrieve-workflows` / `workflow-step-budget` / `distill-retrieval-exp` / `anomaly-trigger` / `query-level-guidance` / `experience-lifecycle` / `prune-experience` / `isolate-factual`

## Phase 57 — v6.1 ReMe + Dynamic Cheatsheet ✅

- ✅ `multi_faceted_distill` / `scenario_retrieve` / `adaptive_rewrite_plan` / `utility_after_reuse` / `selective_add_plan` / `utility_prune_plan`
- ✅ `extract_cheatsheet_snippet` / `retrieve_cheatsheet` / `curator_decide` / `compact_memory_gate` / `dc_rs_order_check`
- ✅ `reme_cheatsheet_shaped_report`
- ✅ Frontiers research §§138–139
- ✅ MCP tools → 395; CLI `multi-faceted-distill` / `scenario-retrieve` / `adaptive-rewrite` / `utility-after-reuse` / `selective-add` / `utility-prune` / `cheatsheet-snippet` / `retrieve-cheatsheet` / `curator-decide` / `compact-memory-gate` / `dc-rs-order`

## Phase 58 — v6.2 ExpeL + RMM dialogue ✅

- ✅ `experience_pool_add` / `insight_op` / `insight_importance_gate` / `retrieve_insights` / `retrieve_similar_successes`
- ✅ `prospective_reflect` / `topic_memory_bank` / `retrieve_topic_memories` / `retrospective_cite_feedback` / `rerank_memories` / `retrieval_refine_plan`
- ✅ `expel_rmm_shaped_report`
- ✅ Frontiers research §§140–141
- ✅ MCP tools → 406; CLI `experience-pool-add` / `insight-op` / `insight-importance-gate` / `retrieve-insights` / `retrieve-similar-successes` / `prospective-reflect` / `topic-memory-bank` / `retrieve-topic-memories` / `retrospective-cite` / `rerank-memories` / `retrieval-refine`

## Phase 59 — v6.3 Trace2Skill + Evo-Memory ✅

- ✅ `collect_trajectory_label` / `propose_trajectory_patch` / `parallel_patch_pool` / `hierarchical_merge_patches` / `skill_mode_gate` / `prefer_parallel_over_sequential`
- ✅ `streaming_task_append` / `exprag_retrieve` / `search_predict_evolve_check` / `evomem_refine_plan` / `evolution_similarity_hint`
- ✅ `trace2skill_evomemory_shaped_report`
- ✅ Frontiers research §§142–143
- ✅ MCP tools → 417; CLI `collect-trajectory` / `propose-patch` / `parallel-patch-pool` / `merge-patches` / `skill-mode-gate` / `prefer-parallel` / `streaming-task-append` / `exprag-retrieve` / `spe-check` / `evomem-refine` / `evolution-similarity`

## Phase 60 — v6.4 Mem-α + AgentHER ✅

- ✅ `classify_memory_slot` / `memory_write_op` / `process_chunk_plan` / `compression_ratio` / `memalpha_reward_bundle` / `length_generalization_gate`
- ✅ `classify_failure` / `extract_replay_outcome` / `hindsight_relabel_plan` / `multi_judge_accept` / `package_training_pair`
- ✅ `memalpha_agenther_shaped_report`
- ✅ Frontiers research §§144–145
- ✅ MCP tools → 428; CLI `classify-memory-slot` / `memory-write-op` / `process-chunk` / `compression-ratio` / `memalpha-reward` / `length-gen-gate` / `classify-failure` / `replay-outcome` / `hindsight-relabel` / `multi-judge` / `package-training-pair`

## Phase 61 — v6.5 PreFlect + SkillFlow ✅

- ✅ `distill_planning_error` / `prospective_critique_plan` / `revise_plan_proposal` / `replan_on_deviation` / `preflect_before_execute_gate`
- ✅ `orchestration_action_select` / `ttb_residual` / `step_importance` / `skill_marginal_flow` / `skill_curation_decide` / `phase_evolve_gate`
- ✅ `preflect_skillflow_shaped_report`
- ✅ Frontiers research §§146–147
- ✅ MCP tools → 439; CLI `distill-planning-error` / `prospective-critique` / `revise-plan` / `replan-deviation` / `preflect-gate` / `orch-action` / `ttb-residual` / `step-importance` / `skill-marginal-flow` / `skill-curation` / `phase-evolve`

## Phase 62 — v6.6 ProcMEM + MemRL ✅

- ✅ `define_skill_triplet` / `skill_select_gate` / `skill_terminate_check` / `semantic_gradient_candidate` / `ppo_gate_verify` / `skill_score_maintain`
- ✅ `ieu_record` / `two_phase_retrieve` / `utility_q_update` / `value_aware_select` / `semantic_vs_utility_warn`
- ✅ `procmem_memrl_shaped_report`
- ✅ Frontiers research §§148–149
- ✅ MCP tools → 450; CLI `define-skill` / `skill-select` / `skill-terminate` / `semantic-gradient` / `ppo-gate` / `skill-maintain` / `ieu-record` / `two-phase-retrieve` / `utility-q-update` / `value-aware-select` / `sim-util-warn`

## Phase 63 — v6.7 EvolveR + AgentEvolver ✅

- ✅ `distill_principle` / `principle_dedupe_plan` / `principle_metric_score` / `search_experience_action` / `lifecycle_phase_gate` / `prune_low_score_principles`
- ✅ `self_question_task` / `experience_when_content` / `mixed_rollout_split` / `attribute_step_credit` / `curiosity_explore_plan`
- ✅ `evolver_agentevolver_shaped_report`
- ✅ Frontiers research §§150–151
- ✅ MCP tools → 461; CLI `distill-principle` / `principle-dedupe` / `principle-score` / `search-exp-action` / `lifecycle-phase` / `prune-principles` / `self-question` / `exp-when-content` / `mixed-rollout` / `attribute-credit` / `curiosity-explore`

## Phase 64 — v6.8 SkillWeaver + SkillRoute ✅

- ✅ `propose_skill` / `practice_skill_run` / `distill_skill_api` / `hone_skill_api` / `skill_library_register` / `transfer_skill_gate`
- ✅ `decompose_task_steps` / `retrieve_skills_for_steps` / `compose_skill_dag` / `sad_feedback_loop` / `granularity_match_check`
- ✅ `skillweaver_skillroute_shaped_report`
- ✅ Frontiers research §§152–153
- ✅ MCP tools → 472; CLI `propose-skill` / `practice-skill` / `distill-skill-api` / `hone-skill-api` / `skill-library-reg` / `transfer-skill` / `decompose-task` / `retrieve-step-skills` / `compose-skill-dag` / `sad-loop` / `granularity-match`

## Phase 65 — v6.9 Absolute Zero + R-Zero ✅

- ✅ `propose_reasoning_task` / `validate_task_structure` / `learnability_reward` / `solve_reward` / `abszero_joint_objective` / `executor_verify_gate`
- ✅ `challenger_propose` / `uncertainty_reward` / `majority_vote_label` / `curriculum_band_filter` / `solver_binary_reward` / `coevolve_round_plan`
- ✅ `abszero_rzero_shaped_report`
- ✅ Frontiers research §§154–155
- ✅ MCP tools → 484; CLI `propose-reason-task` / `validate-task-struct` / `learnability-reward` / `solve-reward` / `abszero-objective` / `executor-verify` / `challenger-propose` / `uncertainty-reward` / `majority-vote` / `curriculum-band` / `solver-reward` / `coevolve-round`

## Phase 66 — v7.0 ECHO + Agent0 ✅

- ✅ `write_turn_memory` / `select_turn_memories` / `reconstruct_policy_context` / `provenance_credit_mask` / `history_collapse_gate` / `budget_binding_check`
- ✅ `curriculum_propose_task` / `tool_use_reward` / `curriculum_reward` / `executor_frontier_filter` / `tool_aware_pressure` / `symbiotic_round_plan`
- ✅ `echomem_agent0_shaped_report`
- ✅ Frontiers research §§156–157
- ✅ MCP tools → 496; CLI `write-turn-mem` / `select-turn-mem` / `reconstruct-ctx` / `credit-mask` / `collapse-gate` / `budget-binding` / `curriculum-task` / `tool-use-reward` / `curriculum-reward` / `executor-frontier` / `tool-pressure` / `symbiotic-round`

## Phase 67 — v7.1 MAE + SAGE ✅

- ✅ `mae_propose_question` / `mae_solve_attempt` / `mae_judge_score` / `mae_proposer_reward` / `mae_quality_filter` / `mae_triad_round_plan`
- ✅ `sage_challenge_task` / `sage_plan_steps` / `sage_solve_with_plan` / `sage_critic_filter` / `sage_drift_gate` / `sage_closed_loop_round`
- ✅ `mae_sagema_shaped_report`
- ✅ Frontiers research §§158–159
- ✅ MCP tools → 508; CLI `mae-propose` / `mae-solve` / `mae-judge` / `mae-proposer-reward` / `mae-quality-filter` / `mae-triad` / `sage-challenge` / `sage-plan` / `sage-solve` / `sage-critic` / `sage-drift` / `sage-loop`

## Phase 68 — v7.2 MemGen + Metis ✅

- ✅ `memory_trigger_decide` / `weave_latent_memory` / `interweave_cycle_plan` / `faculty_classify` / `weaver_only_update_gate` / `sparse_invoke_penalty`
- ✅ `text_experience_store` / `crystallize_plan_to_tool` / `dual_retrieve` / `representation_tradeoff` / `promote_kind_gate` / `metis_loop_plan`
- ✅ `memgen_metis_shaped_report`
- ✅ Frontiers research §§160–161
- ✅ MCP tools → 520; CLI `mem-trigger` / `weave-latent` / `interweave` / `faculty` / `weaver-gate` / `sparse-invoke` / `text-experience` / `crystallize` / `dual-retrieve` / `rep-tradeoff` / `promote-kind` / `metis-loop`

## Phase 69 — v7.3 SAMULE + LIVE-EVO ✅

- ✅ `single_trajectory_reflect` / `intra_task_taxonomy` / `inter_task_transfer` / `foresight_reflect` / `failure_centric_gate` / `merge_reflections`
- ✅ `experience_bank_record` / `meta_guideline_record` / `compile_task_guideline` / `update_experience_weight` / `forget_stale_experience` / `liveevo_online_round`
- ✅ `samule_liveevo_shaped_report`
- ✅ Frontiers research §§162–163
- ✅ MCP tools → 532; CLI `samule-micro` / `samule-meso` / `samule-macro` / `samule-foresight` / `samule-fail-gate` / `samule-merge` / `liveevo-exp` / `liveevo-meta` / `liveevo-compile` / `liveevo-weight` / `liveevo-forget` / `liveevo-round`

## Phase 70 — v7.4 Socratic-Zero + SPIRAL ✅

- ✅ `socratic_teacher_craft` / `socratic_solver_preference` / `socratic_generator_distill` / `socratic_seed_bootstrap` / `socratic_weakness_target` / `socratic_closed_loop`
- ✅ `spiral_self_play_match` / `spiral_rae_advantage` / `spiral_baseline_ema` / `spiral_transfer_pattern` / `spiral_opponent_strength` / `spiral_multi_game_plan`
- ✅ `socratic_spiral_shaped_report`
- ✅ Frontiers research §§164–165
- ✅ MCP tools → 544; CLI `socratic-teach` / `socratic-prefer` / `socratic-distill` / `socratic-seed` / `socratic-weakness` / `socratic-loop` / `spiral-match` / `spiral-rae` / `spiral-ema` / `spiral-pattern` / `spiral-opponent` / `spiral-plan`

## Phase 71 — v7.5 SMITH + H-Mem ✅

- ✅ `smith_store_memory` / `smith_create_tool` / `smith_retrieve_episode` / `smith_curriculum_difficulty` / `smith_tool_reuse_gate` / `smith_loop_plan`
- ✅ `hmem_leaf_event` / `hmem_consolidate_nodes` / `hmem_link_entities` / `hmem_decompose_query` / `hmem_hybrid_retrieve` / `hmem_evolution_gate`
- ✅ `smith_hmem_shaped_report`
- ✅ Frontiers research §§166–167
- ✅ MCP tools → 556; CLI `smith-store` / `smith-tool` / `smith-episode` / `smith-curriculum` / `smith-reuse` / `smith-loop` / `hmem-leaf` / `hmem-consolidate` / `hmem-link` / `hmem-decompose` / `hmem-hybrid` / `hmem-evolution`

## Phase 72 — v7.6 HiMem + H-MEM levels ✅

- ✅ `himem_segment_episode` / `himem_extract_note` / `himem_link_episode_note` / `himem_retrieve_strategy` / `himem_reconsolidate` / `himem_loop_plan`
- ✅ `hmeml_store_level` / `hmeml_route_query` / `hmeml_descend` / `hmeml_parent_link` / `hmeml_efficiency_score` / `hmeml_loop_plan`
- ✅ `himem_hmeml_shaped_report`
- ✅ Frontiers research §§168–169
- ✅ MCP tools → 568; CLI `himem-segment` / `himem-note` / `himem-link` / `himem-retrieve` / `himem-reconsolidate` / `himem-loop` / `hmeml-store` / `hmeml-route` / `hmeml-descend` / `hmeml-parent` / `hmeml-efficiency` / `hmeml-loop`

## Phase 73 — v7.7 HyperSkill + DCPM ✅

- ✅ `hyperskill_add_subtask` / `hyperskill_add_skill` / `hyperskill_add_hyperedge` / `hyperskill_dual_path_retrieve` / `hyperskill_rank_skills` / `hyperskill_maintain_plan` / `hyperskill_loop_plan`
- ✅ `dcpm_day_write` / `dcpm_supersedes_chain` / `dcpm_night_induce` / `dcpm_cross_domain_collision` / `dcpm_hierarchy_level` / `dcpm_loop_plan`
- ✅ `hyperskill_dcpm_shaped_report`
- ✅ Frontiers research §§170–171
- ✅ MCP tools → 581; CLI `hyperskill-*` / `dcpm-*`

## Phase 74 — v7.8 MemOS + SkillCraft ✅

- ✅ `memos_create_cube` / `memos_schedule` / `memos_lifecycle` / `memos_compose` / `memos_migrate` / `memos_fuse_gate` / `memos_loop_plan`
- ✅ `skillcraft_save_skill` / `skillcraft_get_skill` / `skillcraft_list_skills` / `skillcraft_execute_skill` / `skillcraft_verify_skill` / `skillcraft_token_efficiency` / `skillcraft_loop_plan`
- ✅ `memos_skillcraft_shaped_report`
- ✅ Frontiers research §§172–173
- ✅ MCP tools → 595; CLI `memos-*` / `skillcraft-*`

## Phase 75 — v7.9 CMA + AgentFold ✅

- ✅ `cma_persist` / `cma_selective_retain` / `cma_associative_route` / `cma_temporal_chain` / `cma_consolidate` / `cma_probe_gate` / `cma_loop_plan`
- ✅ `agentfold_workspace_split` / `agentfold_fold_command` / `agentfold_granular_condense` / `agentfold_deep_consolidate` / `agentfold_context_budget` / `agentfold_loop_plan`
- ✅ `cma_agentfold_shaped_report`
- ✅ Frontiers research §§174–175
- ✅ MCP tools → 608; CLI `cma-*` / `agentfold-*`

## Phase 76 — v8.0 MemEngine + SimpleMem ✅

- ✅ `memengine_register_function` / `memengine_compose_operation` / `memengine_bind_model` / `memengine_config_set` / `memengine_reflect_plan` / `memengine_pluggable` / `memengine_loop_plan`
- ✅ `simplemem_compress` / `simplemem_synthesize` / `simplemem_intent_scope` / `simplemem_multiview_index` / `simplemem_token_ratio` / `simplemem_loop_plan`
- ✅ `memengine_simplemem_shaped_report`
- ✅ Frontiers research §§176–177
- ✅ MCP tools → 621; CLI `memengine-*` / `simplemem-*`

## Phase 77 — v8.1 O-Mem + Mandol ✅

- ✅ `omem_extract_persona` / `omem_update_event` / `omem_hierarchy_retrieve` / `omem_profile_gate` / `omem_scale_memory_time` / `omem_loop_plan`
- ✅ `mandol_basic_unit` / `mandol_agglomerate` / `mandol_semantic_map_put` / `mandol_hybrid_retrieve` / `mandol_query_route` / `mandol_token_budget` / `mandol_loop_plan`
- ✅ `omem_mandol_shaped_report`
- ✅ Frontiers research §§178–179
- ✅ MCP tools → 634; CLI `omem-*` / `mandol-*`

## Phase 78 — v8.2 Memanto + Zep ✅

- ✅ `memanto_store_typed` / `memanto_conflict_resolve` / `memanto_version` / `memanto_retrieve` / `memanto_latency_gate` / `memanto_loop_plan`
- ✅ `zep_add_episode` / `zep_link_entities` / `zep_bitemporal` / `zep_synthesize` / `zep_cross_session` / `zep_loop_plan`
- ✅ `memanto_zep_shaped_report`
- ✅ Frontiers research §§180–181
- ✅ MCP tools → 646; CLI `memanto-*` / `zep-*`

## Phase 79 — v8.3 MemGPT + RippleMem ✅

- ✅ `memgpt_main_capacity` / `memgpt_page_out` / `memgpt_page_in` / `memgpt_recall_search` / `memgpt_archival_search` / `memgpt_loop_plan`
- ✅ `ripple_store_episode` / `ripple_link_entity` / `ripple_seed_retrieve` / `ripple_expand` / `ripple_recollect_gate` / `ripple_loop_plan`
- ✅ `memgpt_ripple_shaped_report`
- ✅ Frontiers research §§182–183
- ✅ MCP tools → 658; CLI `memgpt-*` / `ripple-*`

## Phase 80 — v8.4 FluxMem + QUMem ✅

- ✅ `flux_connect_form` / `flux_feedback_refine` / `flux_consolidate` / `flux_repair_link` / `flux_prune_interference` / `flux_maturity_gate` / `flux_loop_plan`
- ✅ `qumem_segment_episode` / `qumem_decompose` / `qumem_plan_queries` / `qumem_infer_user_state` / `qumem_temporal_valid` / `qumem_loop_plan`
- ✅ `fluxmem_qumem_shaped_report`
- ✅ Frontiers research §§184–185
- ✅ MCP tools → 671; CLI `flux-*` / `qumem-*`

## Phase 81 — v8.5 VikingMem + RecMem ✅

- ✅ `viking_extract_event` / `viking_update_entity` / `viking_timeline_compress` / `viking_time_weighted_recall` / `viking_rerank` / `viking_loop_plan`
- ✅ `recmem_buffer_subconscious` / `recmem_recurrence_gate` / `recmem_consolidate_episodic` / `recmem_semantic_refine` / `recmem_merge_retrieve` / `recmem_loop_plan`
- ✅ `vikingmem_recmem_shaped_report`
- ✅ Frontiers research §§186–187
- ✅ MCP tools → 683; CLI `viking-*` / `recmem-*`

## Phase 82 — v8.6 MemoryBank + RF-Mem ✅

- ✅ `mbank_store_memory` / `mbank_summon` / `mbank_personality_synth` / `mbank_forget_curve` / `mbank_reinforce` / `mbank_loop_plan`
- ✅ `rfmem_familiarity_score` / `rfmem_path_route` / `rfmem_top_k_familiar` / `rfmem_recollect_expand` / `rfmem_alpha_mix` / `rfmem_loop_plan`
- ✅ `memorybank_rfmem_shaped_report`
- ✅ Frontiers research §§188–189
- ✅ MCP tools → 695; CLI `mbank-*` / `rfmem-*`

## Phase 83 — v8.7 AgeMem + MemGAS ✅

- ✅ `agemem_ltm_store` / `agemem_stm_manage` / `agemem_retrieve` / `agemem_summarize` / `agemem_discard_plan` / `agemem_loop_plan`
- ✅ `memgas_unit` / `memgas_associate` / `memgas_entropy_route` / `memgas_select_granularity` / `memgas_filter_plan` / `memgas_loop_plan`
- ✅ `agemem_memgas_shaped_report`
- ✅ Frontiers research §§190–191
- ✅ MCP tools → 707; CLI `agemem-*` / `memgas-*`

## Phase 84 — v8.8 MemWalker + MemGraphRAG ✅

- ✅ `memwalker_segment` / `memwalker_build_node` / `memwalker_navigate` / `memwalker_gather` / `memwalker_path_gate` / `memwalker_loop_plan`
- ✅ `mgr_store_layer` / `mgr_detect_conflict` / `mgr_resolve_plan` / `mgr_multilayer_retrieve` / `mgr_propagate` / `mgr_loop_plan`
- ✅ `memwalker_memgraphrag_shaped_report`
- ✅ Frontiers research §§192–193
- ✅ MCP tools → 719; CLI `memwalker-*` / `mgr-*`

## Phase 85 — v8.9 RAPTOR + LightRAG ✅

- ✅ `raptor_embed_chunk` / `raptor_cluster` / `raptor_summarize_node` / `raptor_tree_traverse` / `raptor_collapsed_retrieve` / `raptor_loop_plan`
- ✅ `lightrag_index_entity` / `lightrag_index_relation` / `lightrag_dual_retrieve` / `lightrag_incremental_update` / `lightrag_graph_vector_fuse` / `lightrag_loop_plan`
- ✅ `raptor_lightrag_shaped_report`
- ✅ Frontiers research §§194–195
- ✅ MCP tools → 731; CLI `raptor-*` / `lightrag-*`

## Phase 86 — v9.0 MemoRAG + PageIndex ✅

- ✅ `memorag_memorize` / `memorag_clue` / `memorag_retrieve_by_clue` / `memorag_dual_system` / `memorag_generate_plan` / `memorag_loop_plan`
- ✅ `pageindex_build_toc` / `pageindex_add_section` / `pageindex_reason_nav` / `pageindex_select_section` / `pageindex_trace_path` / `pageindex_loop_plan`
- ✅ `memorag_pageindex_shaped_report`
- ✅ Frontiers research §§196–197
- ✅ MCP tools → 743; CLI `memorag-*` / `pageindex-*`

## Phase 87 — v9.1 Self-RAG + MemoBrain ✅

- ✅ `selfrag_need_retrieve` / `selfrag_relevance_critique` / `selfrag_support_critique` / `selfrag_utility_critique` / `selfrag_select_best` / `selfrag_loop_plan`
- ✅ `memobrain_dep_edge` / `memobrain_prune_invalid` / `memobrain_fold_subtraj` / `memobrain_flush_budget` / `memobrain_salience_keep` / `memobrain_loop_plan`
- ✅ `selfrag_memobrain_shaped_report`
- ✅ Frontiers research §§198–199
- ✅ MCP tools → 755; CLI `selfrag-*` / `memobrain-*`

## Phase 88 — v9.2 CRAG + HyDE ✅

- ✅ `crag_evaluate_retrieval` / `crag_correct_refine` / `crag_web_fallback_plan` / `crag_ambiguous_blend` / `crag_action_select` / `crag_loop_plan`
- ✅ `hyde_hypothetical_doc` / `hyde_encode_proxy` / `hyde_retrieve_by_hyp` / `hyde_filter_hallucination` / `hyde_ground_corpus` / `hyde_loop_plan`
- ✅ `crag_hyde_shaped_report`
- ✅ Frontiers research §§200–201
- ✅ MCP tools → 767; CLI `crag-*` / `hyde-*`

## Phase 89 — v9.3 Adaptive-RAG + FLARE ✅

- ✅ `adaptiverag_classify_complexity` / `adaptiverag_select_strategy` / `adaptiverag_no_retrieve` / `adaptiverag_single_step` / `adaptiverag_multi_step` / `adaptiverag_loop_plan`
- ✅ `flare_anticipate_sentence` / `flare_low_confidence` / `flare_retrieve_for_regen` / `flare_regenerate_sentence` / `flare_active_step` / `flare_loop_plan`
- ✅ `adaptiverag_flare_shaped_report`
- ✅ Frontiers research §§202–203
- ✅ MCP tools → 779; CLI `adaptiverag-*` / `flare-*`

## Phase 90 — v9.4 GraphReader + G-Retriever ✅

- ✅ `graphreader_build_node` / `graphreader_read_node` / `graphreader_read_neighbors` / `graphreader_note_insight` / `graphreader_reflect_plan` / `graphreader_loop_plan`
- ✅ `gretriever_node_prize` / `gretriever_pcst_select` / `gretriever_subgraph` / `gretriever_soft_prompt_plan` / `gretriever_highlight` / `gretriever_loop_plan`
- ✅ `graphreader_gretriever_shaped_report`
- ✅ Frontiers research §§204–205
- ✅ MCP tools → 791; CLI `graphreader-*` / `gretriever-*`

## Phase 91 — v9.5 RQ-RAG + IRCoT ✅

- ✅ `rqrag_rewrite` / `rqrag_decompose` / `rqrag_disambiguate` / `rqrag_refine_mode` / `rqrag_retrieve_refined` / `rqrag_loop_plan`
- ✅ `ircot_cot_step` / `ircot_retrieve_guided` / `ircot_interleave` / `ircot_answer_ready` / `ircot_hallucination_check` / `ircot_loop_plan`
- ✅ `rqrag_ircot_shaped_report`
- ✅ Frontiers research §§206–207
- ✅ MCP tools → 803; CLI `rqrag-*` / `ircot-*`

## Phase 92 — v9.6 REPLUG + Iter-RetGen ✅

- ✅ `replug_retrieve_docs` / `replug_prepend_doc` / `replug_ensemble_probs` / `replug_supervise_retriever` / `replug_blackbox_forward` / `replug_loop_plan`
- ✅ `iterretgen_generate` / `iterretgen_use_as_query` / `iterretgen_retrieve_next` / `iterretgen_iterate` / `iterretgen_adapt_retriever` / `iterretgen_loop_plan`
- ✅ `replug_iterretgen_shaped_report`
- ✅ Frontiers research §§208–209
- ✅ MCP tools → 815; CLI `replug-*` / `iterretgen-*`

## Phase 93 — v9.7 PlanRAG + Rewrite-Retrieve-Read ✅

- ✅ `planrag_make_plan` / `planrag_analysis_query` / `planrag_retrieve_data` / `planrag_replan` / `planrag_decide` / `planrag_loop_plan`
- ✅ `rrr_rewrite_query` / `rrr_retrieve` / `rrr_read` / `rrr_reader_feedback` / `rrr_train_rewriter_plan` / `rrr_loop_plan`
- ✅ `planrag_rrr_shaped_report`
- ✅ Frontiers research §§210–211
- ✅ MCP tools → 827; CLI `planrag-*` / `rrr-*`

## Phase 94 — v9.8 DSP + GenRead ✅

- ✅ `dsp_bootstrap_demo` / `dsp_search` / `dsp_predict` / `dsp_compose_program` / `dsp_multihop_hop` / `dsp_loop_plan`
- ✅ `genread_generate_context` / `genread_ground_optional` / `genread_answer` / `genread_compare_retrieve` / `genread_hybrid` / `genread_loop_plan`
- ✅ `dsp_genread_shaped_report`
- ✅ Frontiers research §§212–213
- ✅ MCP tools → 839; CLI `dsp-*` / `genread-*`

## Phase 95 — v9.9 Self-Ask + ReAct ✅

- ✅ `selfask_followup` / `selfask_search_intercept` / `selfask_compose_answer` / `selfask_stop` / `selfask_demo_prompt` / `selfask_loop_plan`
- ✅ `react_thought` / `react_action` / `react_observe` / `react_finish` / `react_trajectory` / `react_loop_plan`
- ✅ `selfask_react_shaped_report`
- ✅ Frontiers research §§214–215
- ✅ MCP tools → 851; CLI `selfask-*` / `react-*`

## Phase 96 — v10.0 Think-on-Graph + Toolformer ✅

- ✅ `tog_init_entity` / `tog_explore_neighbors` / `tog_beam_prune` / `tog_path_score` / `tog_answer_from_paths` / `tog_loop_plan`
- ✅ `tf_api_candidate` / `tf_filter_call` / `tf_execute_proxy` / `tf_incorporate_result` / `tf_demo_apis` / `tf_loop_plan`
- ✅ `tog_toolformer_shaped_report`
- ✅ Frontiers research §§216–217
- ✅ MCP tools → 863; CLI `tog-*` / `tf-*`

## Phase 97 — v10.1 Reflexion + Self-Consistency ✅

- ✅ `rx_trial_run` / `rx_evaluate` / `rx_verbal_reflect` / `rx_memory_store` / `rx_next_trial` / `rx_loop_plan`
- ✅ `sc_sample_path` / `sc_collect_answers` / `sc_majority_vote` / `sc_marginalize` / `sc_temperature` / `sc_loop_plan`
- ✅ `reflexion_selfcons_shaped_report`
- ✅ Frontiers research §§218–219
- ✅ MCP tools → 875; CLI `rx-*` / `sc-*`

## Phase 98 — v10.2 Tree of Thoughts + Least-to-Most ✅

- ✅ `tot_propose` / `tot_evaluate` / `tot_expand` / `tot_backtrack` / `tot_select_best` / `tot_loop_plan`
- ✅ `ltm_decompose` / `ltm_solve_sub` / `ltm_carry_forward` / `ltm_compose_final` / `ltm_easy_to_hard` / `ltm_loop_plan`
- ✅ `tot_ltm_shaped_report`
- ✅ Frontiers research §§220–221
- ✅ MCP tools → 887; CLI `tot-*` / `ltm-*`

## Phase 99 — v10.3 Graph of Thoughts + Program of Thoughts ✅

- ✅ `got_add_thought` / `got_link` / `got_aggregate` / `got_feedback` / `got_score_graph` / `got_loop_plan`
- ✅ `pot_emit_program` / `pot_sandbox_run` / `pot_read_result` / `pot_self_consistency` / `pot_disentangle` / `pot_loop_plan`
- ✅ `got_pot_shaped_report`
- ✅ Frontiers research §§222–223
- ✅ MCP tools → 899; CLI `got-*` / `pot-*`

## Phase 100 — v10.4 Algorithm of Thoughts + Reasoning via Planning ✅

- ✅ `aot_load_algorithm` / `aot_explore_subtree` / `aot_tunnel_vision` / `aot_query_budget` / `aot_surpass_algo` / `aot_loop_plan`
- ✅ `rap_world_state` / `rap_expand` / `rap_reward` / `rap_select_path` / `rap_balance` / `rap_loop_plan`
- ✅ `aot_rap_shaped_report`
- ✅ Frontiers research §§224–225
- ✅ MCP tools → 911; CLI `aot-*` / `rap-*`

## Phase 101 — v10.5 Skeleton-of-Thought + Buffer of Thoughts ✅

- ✅ `sot_emit_skeleton` / `sot_extract_points` / `sot_parallel_expand` / `sot_router` / `sot_latency_gain` / `sot_loop_plan`
- ✅ `bot_distill_template` / `bot_retrieve_template` / `bot_instantiate` / `bot_buffer_update` / `bot_cost_ratio` / `bot_loop_plan`
- ✅ `sot_bot_shaped_report`
- ✅ Frontiers research §§226–227
- ✅ MCP tools → 923; CLI `sot-*` / `bot-*`

## Phase 102 — v10.6 Self-Discover + Meta-Prompting ✅

- ✅ `sd_select_modules` / `sd_adapt` / `sd_implement` / `sd_apply_instance` / `sd_compute_ratio` / `sd_loop_plan`
- ✅ `mp_break_task` / `mp_assign_expert` / `mp_oversee` / `mp_verify` / `mp_task_agnostic` / `mp_loop_plan`
- ✅ `sd_mp_shaped_report`
- ✅ Frontiers research §§228–229
- ✅ MCP tools → 935; CLI `sd-*` / `mp-*`

## Phase 103 — v10.7 Quiet-STaR + Decomposed Prompting ✅

- ✅ `qs_thought_bounds` / `qs_parallel_sample` / `qs_mix_head` / `qs_hard_token_aid` / `qs_zero_shot_flag` / `qs_loop_plan`
- ✅ `dep_decompose` / `dep_delegate` / `dep_recurse` / `dep_swap_symbolic` / `dep_library_size` / `dep_loop_plan`
- ✅ `qs_dep_shaped_report`
- ✅ Frontiers research §§230–231
- ✅ MCP tools → 947; CLI `qs-*` / `dep-*`

## Phase 104 — v10.8 STaR + Cumulative Reasoning ✅

- ✅ `star_generate` / `star_filter_correct` / `star_rationalize` / `star_finetune_proxy` / `star_bootstrap_round` / `star_loop_plan`
- ✅ `cr_propose` / `cr_verify` / `cr_accumulate` / `cr_report` / `cr_roles` / `cr_loop_plan`
- ✅ `star_cr_shaped_report`
- ✅ Frontiers research §§232–233
- ✅ MCP tools → 959; CLI `star-*` / `cr-*`

## Phase 105 — v10.9 Plan-and-Solve + Progressive-Hint Prompting ✅

- ✅ `ps_devise_plan` / `ps_execute` / `ps_plus_extract` / `ps_calc_guard` / `ps_missing_step_fix` / `ps_loop_plan`
- ✅ `php_base_answer` / `php_emit_hint` / `php_reask` / `php_stable_stop` / `php_combine_sc` / `php_loop_plan`
- ✅ `ps_php_shaped_report`
- ✅ Frontiers research §§234–235
- ✅ MCP tools → 971; CLI `ps-*` / `php-*`

## Phase 106 — v11.0 AgentCoder + PAL ✅

- ✅ `ac_programmer` / `ac_test_designer` / `ac_test_executor` / `ac_refine` / `ac_pass_gate` / `ac_loop_plan`
- ✅ `pal_emit_program` / `pal_offload_solve` / `pal_read_answer` / `pal_decompose_only` / `pal_vs_cot` / `pal_loop_plan`
- ✅ `ac_pal_shaped_report`
- ✅ Frontiers research §§236–237
- ✅ MCP tools → 983; CLI `ac-*` / `pal-*`

## Phase 107 — v11.1 Faithful CoT + LATS ✅

- ✅ `fcot_translate` / `fcot_solve` / `fcot_faithfulness` / `fcot_interleave` / `fcot_vs_cot` / `fcot_loop_plan`
- ✅ `lats_expand` / `lats_value` / `lats_reflect` / `lats_select` / `lats_env_feedback` / `lats_loop_plan`
- ✅ `fcot_lats_shaped_report`
- ✅ Frontiers research §§238–239
- ✅ MCP tools → 995; CLI `fcot-*` / `lats-*`

## Phase 108 — v11.2 Voyager + ReWOO ✅

- ✅ `voy_curriculum` / `voy_skill_store` / `voy_skill_retrieve` / `voy_self_verify` / `voy_compose` / `voy_loop_plan`
- ✅ `rewoo_plan` / `rewoo_worker` / `rewoo_solver` / `rewoo_decouple` / `rewoo_token_save` / `rewoo_loop_plan`
- ✅ `voy_rewoo_shaped_report`
- ✅ Frontiers research §§240–241
- ✅ MCP tools → 1007; CLI `voy-*` / `rewoo-*`

## Phase 109 — v11.3 CRITIC + Deductive Verification ✅

- ✅ `critic_draft` / `critic_tool_check` / `critic_revise` / `critic_iterate` / `critic_stop` / `critic_loop_plan`
- ✅ `dv_natural_program` / `dv_step_verify` / `dv_premise_scope` / `dv_unanimity` / `dv_ground` / `dv_loop_plan`
- ✅ `critic_dv_shaped_report`
- ✅ Frontiers research §§242–243
- ✅ MCP tools → 1019; CLI `critic-*` / `dv-*`

## Phase 110 — v11.4 HuggingGPT + Multiagent Debate ✅

- ✅ `hgpt_plan` / `hgpt_select` / `hgpt_execute` / `hgpt_summarize` / `hgpt_modality` / `hgpt_loop_plan`
- ✅ `mad_propose` / `mad_debate` / `mad_critique` / `mad_converge` / `mad_factuality` / `mad_loop_plan`
- ✅ `hgpt_mad_shaped_report`
- ✅ Frontiers research §§244–245
- ✅ MCP tools → 1031; CLI `hgpt-*` / `mad-*`

## Phase 111 — v11.5 Auto-CoT + CAMEL ✅

- ✅ `autocot_cluster` / `autocot_sample` / `autocot_generate` / `autocot_heuristic` / `autocot_diversity` / `autocot_loop_plan`
- ✅ `camel_roles` / `camel_inception` / `camel_turn` / `camel_complete` / `camel_society` / `camel_loop_plan`
- ✅ `autocot_camel_shaped_report`
- ✅ Frontiers research §§246–247
- ✅ MCP tools → 1043; CLI `autocot-*` / `camel-*`

## Phase 112 — v11.6 Chameleon + Recursion of Thought ✅

- ✅ `cham_inventory` / `cham_plan` / `cham_compose` / `cham_execute` / `cham_constraint` / `cham_loop_plan`
- ✅ `rot_trigger` / `rot_divide` / `rot_conquer` / `rot_merge` / `rot_context_limit` / `rot_loop_plan`
- ✅ `cham_rot_shaped_report`
- ✅ Frontiers research §§248–249
- ✅ MCP tools → 1055; CLI `cham-*` / `rot-*`

## Phase 113 — v11.7 Active-Prompt + Analogical Prompting ✅

- ✅ `ap_sample` / `ap_uncertainty` / `ap_select` / `ap_annotate` / `ap_pool` / `ap_loop_plan`
- ✅ `ana_recall` / `ana_knowledge` / `ana_solve` / `ana_adapt` / `ana_no_label` / `ana_loop_plan`
- ✅ `ap_ana_shaped_report`
- ✅ Frontiers research §§250–251
- ✅ MCP tools → 1067; CLI `ap-*` / `ana-*`

## Phase 114 — v11.8 Complexity-Based + Step-Back Prompting ✅

- ✅ `cbp_score` / `cbp_select` / `cbp_sample_chains` / `cbp_vote_complex` / `cbp_robust` / `cbp_loop_plan`
- ✅ `sb_abstract` / `sb_principle` / `sb_reason` / `sb_path` / `sb_detail_trap` / `sb_loop_plan`
- ✅ `cbp_sb_shaped_report`
- ✅ Frontiers research §§252–253
- ✅ MCP tools → 1079; CLI `cbp-*` / `sb-*`

## Phase 115 — v11.9 Multimodal-CoT + Maieutic Prompting ✅

- ✅ `mmcot_fuse` / `mmcot_rationale` / `mmcot_infer` / `mmcot_hallucination` / `mmcot_separate` / `mmcot_loop_plan`
- ✅ `mai_abduce` / `mai_recurse` / `mai_sat` / `mai_consistent` / `mai_unreliable` / `mai_loop_plan`
- ✅ `mmcot_mai_shaped_report`
- ✅ Frontiers research §§254–255
- ✅ MCP tools → 1091; CLI `mmcot-*` / `mai-*`

## Phase 116 — v12.0 Self-Refine + Metacognitive Prompting ✅

- ✅ `sr_generate` / `sr_feedback` / `sr_refine` / `sr_iterate` / `sr_no_train` / `sr_loop_plan`
- ✅ `mcp_recognize` / `mcp_interpret` / `mcp_reevaluate` / `mcp_confidence` / `mcp_justify` / `mcp_loop_plan`
- ✅ `sr_mcp_shaped_report`
- ✅ Frontiers research §§256–257
- ✅ MCP tools → 1103; CLI `sr-*` / `mcp-*`

## Phase 117 — v12.1 Thread of Thought + Thought Propagation ✅

- ✅ `thot_segment` / `thot_analyze` / `thot_select` / `thot_synthesize` / `thot_plug` / `thot_loop_plan`
- ✅ `tprop_propose` / `tprop_solve` / `tprop_reuse` / `tprop_amend` / `tprop_compat` / `tprop_loop_plan`
- ✅ `thot_tprop_shaped_report`
- ✅ Frontiers research §§258–259
- ✅ MCP tools → 1115; CLI `thot-*` / `tprop-*`

## Phase 118 — v12.2 System 2 Attention + Contrastive CoT ✅

- ✅ `s2a_regenerate` / `s2a_attend` / `s2a_respond` / `s2a_factuality` / `s2a_sycophancy` / `s2a_loop_plan`
- ✅ `ccot_valid` / `ccot_invalid` / `ccot_contrast` / `ccot_reason` / `ccot_auto` / `ccot_loop_plan`
- ✅ `s2a_ccot_shaped_report`
- ✅ Frontiers research §§260–261
- ✅ MCP tools → 1127; CLI `s2a-*` / `ccot-*`

## Phase 119 — v12.3 Tab-CoT + Everything of Thoughts ✅

- ✅ `tabcot_header` / `tabcot_row` / `tabcot_infer2d` / `tabcot_extract` / `tabcot_zeroshot` / `tabcot_loop_plan`
- ✅ `xot_mcts` / `xot_revise` / `xot_map` / `xot_penrose` / `xot_flexible` / `xot_loop_plan`
- ✅ `tabcot_xot_shaped_report`
- ✅ Frontiers research §§262–263
- ✅ MCP tools → 1139; CLI `tabcot-*` / `xot-*`

## Phase 120 — v12.4 Chain-of-Verification + Verify-and-Edit ✅

- ✅ `cove_draft` / `cove_plan` / `cove_answer` / `cove_final` / `cove_hallucination` / `cove_loop_plan`
- ✅ `ved_uncertain` / `ved_search` / `ved_edit` / `ved_predict` / `ved_knowledge` / `ved_loop_plan`
- ✅ `cove_ved_shaped_report`
- ✅ Frontiers research §§264–265
- ✅ MCP tools → 1151; CLI `cove-*` / `ved-*`

## Phase 121 — v12.5 Self-Verification + Chain of Density ✅

- ✅ `sve_forward` / `sve_mask` / `sve_repredict` / `sve_score` / `sve_select` / `sve_loop_plan`
- ✅ `cod_sparse` / `cod_entities` / `cod_fuse` / `cod_length` / `cod_tradeoff` / `cod_loop_plan`
- ✅ `sve_cod_shaped_report`
- ✅ Frontiers research §§266–267
- ✅ MCP tools → 1163; CLI `sve-*` / `cod-*`

## Phase 122 — v12.6 Hint-before-Solving + EmotionPrompt ✅

- ✅ `hsp_hint` / `hsp_solve` / `hsp_answer` / `hsp_compose` / `hsp_quality` / `hsp_loop_plan`
- ✅ `emo_stimulus` / `emo_append` / `emo_run` / `emo_truth` / `emo_psych` / `emo_loop_plan`
- ✅ `hsp_emo_shaped_report`
- ✅ Frontiers research §§268–269
- ✅ MCP tools → 1175; CLI `hsp-*` / `emo-*`

## Phase 123 — v12.7 Automatic Prompt Engineer + Promptbreeder ✅

- ✅ `ape_propose` / `ape_score` / `ape_select` / `ape_steer` / `ape_human` / `ape_loop_plan`
- ✅ `pbr_init` / `pbr_mutate` / `pbr_fitness` / `pbr_diversity` / `pbr_selfref` / `pbr_loop_plan`
- ✅ `ape_pbr_shaped_report`
- ✅ Frontiers research §§270–271
- ✅ MCP tools → 1187; CLI `ape-*` / `pbr-*`

## Phase 124 — v12.8 OPRO + EvoPrompt ✅

- ✅ `opro_meta` / `opro_propose` / `opro_score` / `opro_append` / `opro_best` / `opro_loop_plan`
- ✅ `evp_init` / `evp_cross` / `evp_mutate` / `evp_select` / `evp_ea` / `evp_loop_plan`
- ✅ `opro_evp_shaped_report`
- ✅ Frontiers research §§272–273
- ✅ MCP tools → 1199; CLI `opro-*` / `evp-*`

## Phase 125 — v12.9 ProTeGi + PromptAgent ✅

- ✅ `ptg_gradient` / `ptg_edit` / `ptg_beam` / `ptg_bandit` / `ptg_jailbreak` / `ptg_loop_plan`
- ✅ `pag_state` / `pag_reflect` / `pag_expand` / `pag_backprop` / `pag_expert` / `pag_loop_plan`
- ✅ `ptg_pag_shaped_report`
- ✅ Frontiers research §§274–275
- ✅ MCP tools → 1211; CLI `ptg-*` / `pag-*`

## Phase 126 — v13.0 MAPO + GrIPS ✅

- ✅ `mapo_posgrad` / `mapo_momentum` / `mapo_beam` / `mapo_ucb` / `mapo_faster` / `mapo_loop_plan`
- ✅ `grips_seed` / `grips_edit` / `grips_score` / `grips_accept` / `grips_api` / `grips_loop_plan`
- ✅ `mapo_grips_shaped_report`
- ✅ Frontiers research §§276–277
- ✅ MCP tools → 1223; CLI `mapo-*` / `grips-*`

## Phase 127 — v13.1 TEMPERA + RLPrompt ✅

- ✅ `tmpa_state` / `tmpa_act` / `tmpa_reward` / `tmpa_adapt` / `tmpa_efficiency` / `tmpa_loop_plan`
- ✅ `rlp_init` / `rlp_sample` / `rlp_reward` / `rlp_update` / `rlp_discrete` / `rlp_loop_plan`
- ✅ `tmpa_rlp_shaped_report`
- ✅ Frontiers research §§278–279
- ✅ MCP tools → 1235; CLI `tmpa-*` / `rlp-*`

## Phase 128 — v13.2 AutoPrompt + Prefix-Tuning ✅

- ✅ `aup_template` / `aup_trigger` / `aup_search` / `aup_score` / `aup_probe` / `aup_loop_plan`
- ✅ `pfx_task` / `pfx_prefix` / `pfx_optimize` / `pfx_generate` / `pfx_freeze` / `pfx_loop_plan`
- ✅ `aup_pfx_shaped_report`
- ✅ Frontiers research §§280–281
- ✅ MCP tools → 1247; CLI `aup-*` / `pfx-*`

## Phase 129 — v13.3 P-Tuning v2 + Prompt Tuning ✅

- ✅ `ptv_deep` / `ptv_inject` / `ptv_tune` / `ptv_seqtag` / `ptv_universal` / `ptv_loop_plan`
- ✅ `ptl_soft` / `ptl_prepend` / `ptl_optimize` / `ptl_scale` / `ptl_input_only` / `ptl_loop_plan`
- ✅ `ptv_ptl_shaped_report`
- ✅ Frontiers research §§282–283
- ✅ MCP tools → 1259; CLI `ptv-*` / `ptl-*`

## Phase 130 — v13.4 Soft Prompt Mixtures + SPoT ✅

- ✅ `msp_soft` / `msp_mix` / `msp_ensemble` / `msp_probe` / `msp_underest` / `msp_loop_plan`
- ✅ `spot_source` / `spot_init` / `spot_embed` / `spot_retrieve` / `spot_vs_tune` / `spot_loop_plan`
- ✅ `msp_spot_shaped_report`
- ✅ Frontiers research §§284–285
- ✅ MCP tools → 1271; CLI `msp-*` / `spot-*`

## Phase 131 — v13.5 ATTEMPT + Multitask Prompt Tuning ✅

- ✅ `atm_source` / `atm_target` / `atm_attend` / `atm_mix` / `atm_modular` / `atm_loop_plan`
- ✅ `mptp_shared` / `mptp_factor` / `mptp_transfer` / `mptp_score` / `mptp_efficient` / `mptp_loop_plan`
- ✅ `atm_mptp_shaped_report`
- ✅ Frontiers research §§286–287
- ✅ MCP tools → 1283; CLI `atm-*` / `mptp-*`

## Phase 132 — v13.6 LoRA + AdapterFusion ✅

- ✅ `lora_freeze` / `lora_rank` / `lora_train` / `lora_merge` / `lora_latency` / `lora_loop_plan`
- ✅ `adf_extract` / `adf_compose` / `adf_attend` / `adf_score` / `adf_nondestruct` / `adf_loop_plan`
- ✅ `lora_adf_shaped_report`
- ✅ Frontiers research §§288–289
- ✅ MCP tools → 1295; CLI `lora-*` / `adf-*`

## Phase 133 — v13.7 Compacter + (IA)^3 ✅

- ✅ `cmp_insert` / `cmp_kronecker` / `cmp_train` / `cmp_score` / `cmp_compact` / `cmp_loop_plan`
- ✅ `ia3_vector` / `ia3_scale` / `ia3_train` / `ia3_score` / `ia3_mixed` / `ia3_loop_plan`
- ✅ `cmp_ia3_shaped_report`
- ✅ Frontiers research §§290–291
- ✅ MCP tools → 1307; CLI `cmp-*` / `ia3-*`

## Phase 134 — v13.8 BitFit + DoRA ✅

- ✅ `bft_freeze` / `bft_bias` / `bft_train` / `bft_score` / `bft_tiny` / `bft_loop_plan`
- ✅ `dora_decompose` / `dora_magnitude` / `dora_direction` / `dora_score` / `dora_vs_lora` / `dora_loop_plan`
- ✅ `bft_dora_shaped_report`
- ✅ Frontiers research §§292–293
- ✅ MCP tools → 1319; CLI `bft-*` / `dora-*`

## Phase 135 — v13.9 QLoRA + AdaLoRA ✅

- ✅ `qlo_quantize` / `qlo_nf4` / `qlo_adapter` / `qlo_score` / `qlo_memory` / `qlo_loop_plan`
- ✅ `adl_init` / `adl_svd` / `adl_prune` / `adl_score` / `adl_adaptive` / `adl_loop_plan`
- ✅ `qlo_adl_shaped_report`
- ✅ Frontiers research §§294–295
- ✅ MCP tools → 1331; CLI `qlo-*` / `adl-*`

## Phase 136 — v14.0 VeRA + AdapterDrop ✅

- ✅ `vra_share` / `vra_scale` / `vra_train` / `vra_score` / `vra_tiny` / `vra_loop_plan`
- ✅ `adp_insert` / `adp_drop` / `adp_infer` / `adp_score` / `adp_efficient` / `adp_loop_plan`
- ✅ `vra_adp_shaped_report`
- ✅ Frontiers research §§296–297
- ✅ MCP tools → 1343; CLI `vra-*` / `adp-*`

## Phase 137 — v14.1 PiSSA + Diff Pruning ✅

- ✅ `psa_svd` / `psa_principal` / `psa_residual` / `psa_score` / `psa_fast` / `psa_loop_plan`
- ✅ `dpr_diff` / `dpr_mask` / `dpr_prune` / `dpr_score` / `dpr_sparse` / `dpr_loop_plan`
- ✅ `psa_dpr_shaped_report`
- ✅ Frontiers research §§298–299
- ✅ MCP tools → 1355; CLI `psa-*` / `dpr-*`

## Phase 138 — v14.2 Tied-LoRA + LoRA+ ✅

- ✅ `tlo_base` / `tlo_tie` / `tlo_train` / `tlo_score` / `tlo_efficient` / `tlo_loop_plan`
- ✅ `lrp_split` / `lrp_ratio` / `lrp_train` / `lrp_score` / `lrp_speed` / `lrp_loop_plan`
- ✅ `tlo_lrp_shaped_report`
- ✅ Frontiers research §§300–301
- ✅ MCP tools → 1367; CLI `tlo-*` / `lrp-*`

## Phase 139 — v14.3 LoRA-FA + DyLoRA ✅

- ✅ `lfa_freeze_a` / `lfa_train_b` / `lfa_merge` / `lfa_score` / `lfa_memory` / `lfa_loop_plan`
- ✅ `dyl_range` / `dyl_sample` / `dyl_select` / `dyl_score` / `dyl_searchfree` / `dyl_loop_plan`
- ✅ `lfa_dyl_shaped_report`
- ✅ Frontiers research §§302–303
- ✅ MCP tools → 1379; CLI `lfa-*` / `dyl-*`

## Phase 140 — v14.4 LoRA-XS + AsymmetryLoRA ✅

- ✅ `lxs_svd` / `lxs_r` / `lxs_train` / `lxs_score` / `lxs_tiny` / `lxs_loop_plan`
- ✅ `asy_role` / `asy_freeze_a` / `asy_train_b` / `asy_score` / `asy_bound` / `asy_loop_plan`
- ✅ `lxs_asy_shaped_report`
- ✅ Frontiers research §§304–305
- ✅ MCP tools → 1391; CLI `lxs-*` / `asy-*`

## Phase 141 — v14.5 LoRA-GA + MoRA ✅

- ✅ `lga_grad` / `lga_svd` / `lga_scale` / `lga_score` / `lga_fast` / `lga_loop_plan`
- ✅ `mor_square` / `mor_compress` / `mor_expand` / `mor_score` / `mor_merge` / `mor_loop_plan`
- ✅ `lga_mor_shaped_report`
- ✅ Frontiers research §§306–307
- ✅ MCP tools → 1403; CLI `lga-*` / `mor-*`

## Phase 142 — v14.6 rsLoRA + LoKr ✅

- ✅ `rsl_rank` / `rsl_scale` / `rsl_train` / `rsl_score` / `rsl_stable` / `rsl_loop_plan`
- ✅ `lkr_factors` / `lkr_kron` / `lkr_vectorize` / `lkr_score` / `lkr_preserve` / `lkr_loop_plan`
- ✅ `rsl_lkr_shaped_report`
- ✅ Frontiers research §§308–309
- ✅ MCP tools → 1415; CLI `rsl-*` / `lkr-*`

## Phase 143 — v14.7 LoHa + FourierFT ✅

- ✅ `lha_pair` / `lha_hadamard` / `lha_train` / `lha_score` / `lha_express` / `lha_loop_plan`
- ✅ `fft_basis` / `fft_coeff` / `fft_idft` / `fft_score` / `fft_sparse` / `fft_loop_plan`
- ✅ `lha_fft_shaped_report`
- ✅ Frontiers research §§310–311
- ✅ MCP tools → 1427; CLI `lha-*` / `fft-*`

## Phase 144 — v14.8 Houlsby + ReFT ✅

- ✅ `had_insert` / `had_freeze` / `had_train` / `had_score` / `had_latency` / `had_loop_plan`
- ✅ `rft_repr` / `rft_edit` / `rft_train` / `rft_score` / `rft_weightless` / `rft_loop_plan`
- ✅ `had_rft_shaped_report`
- ✅ Frontiers research §§312–313
- ✅ MCP tools → 1439; CLI `had-*` / `rft-*`

## Phase 145 — v14.9 OFT/BOFT + MiSS ✅

- ✅ `oft_ortho` / `oft_butterfly` / `oft_train` / `oft_score` / `oft_energy` / `oft_loop_plan`
- ✅ `mss_shard` / `mss_share` / `mss_train` / `mss_score` / `mss_pareto` / `mss_loop_plan`
- ✅ `oft_mss_shaped_report`
- ✅ Frontiers research §§314–315
- ✅ MCP tools → 1451; CLI `oft-*` / `mss-*`

## Phase 146 — v15.0 DropLoRA + GaLore ✅

- ✅ `drl_rank` / `drl_mask` / `drl_train` / `drl_score` / `drl_infer` / `drl_loop_plan`
- ✅ `gal_grad` / `gal_project` / `gal_step` / `gal_score` / `gal_full` / `gal_loop_plan`
- ✅ `drl_gal_shaped_report`
- ✅ Frontiers research §§316–317
- ✅ MCP tools → 1463; CLI `drl-*` / `gal-*`

## Phase 147 — v15.1 SHiRA + WaveFT ✅

- ✅ `shr_mask` / `shr_tune` / `shr_switch` / `shr_score` / `shr_fusion` / `shr_loop_plan`
- ✅ `wft_wave` / `wft_sparse` / `wft_idwt` / `wft_score` / `wft_granular` / `wft_loop_plan`
- ✅ `shr_wft_shaped_report`
- ✅ Frontiers research §§318–319
- ✅ MCP tools → 1475; CLI `shr-*` / `wft-*`

## Phase 148 — v15.2 LoRA-Pro + Kron-LoRA ✅

- ✅ `lpr_equiv` / `lpr_adjust` / `lpr_train` / `lpr_score` / `lpr_bridge` / `lpr_loop_plan`
- ✅ `krl_kron` / `krl_lora` / `krl_train` / `krl_score` / `krl_compress` / `krl_loop_plan`
- ✅ `lpr_krl_shaped_report`
- ✅ Frontiers research §§320–321
- ✅ MCP tools → 1487; CLI `lpr-*` / `krl-*`

## Phase 149 — v15.3 MiLoRA + CorDA ✅

- ✅ `mil_svd` / `mil_minor` / `mil_freeze` / `mil_score` / `mil_preserve` / `mil_loop_plan`
- ✅ `cda_cov` / `cda_mode` / `cda_adapt` / `cda_score` / `cda_forget` / `cda_loop_plan`
- ✅ `mil_cda_shaped_report`
- ✅ Frontiers research §§322–323
- ✅ MCP tools → 1499; CLI `mil-*` / `cda-*`

## Phase 150 — v15.4 LoftQ + LoRA-Dash ✅

- ✅ `lfq_quant` / `lfq_init` / `lfq_train` / `lfq_score` / `lfq_gap` / `lfq_loop_plan`
- ✅ `lds_prelaunch` / `lds_tsd` / `lds_dash` / `lds_score` / `lds_impact` / `lds_loop_plan`
- ✅ `lfq_lds_shaped_report`
- ✅ Frontiers research §§324–325
- ✅ MCP tools → 1511; CLI `lfq-*` / `lds-*`

## Phase 151 — v15.5 Delta-LoRA + LoRA-One ✅

- ✅ `dlo_adapters` / `dlo_delta` / `dlo_propagate` / `dlo_score` / `dlo_highrank` / `dlo_loop_plan`
- ✅ `lon_grad` / `lon_align` / `lon_train` / `lon_score` / `lon_immediate` / `lon_loop_plan`
- ✅ `dlo_lon_shaped_report`
- ✅ Frontiers research §§326–327
- ✅ MCP tools → 1523; CLI `dlo-*` / `lon-*`

## Phase 152 — v15.6 OLoRA + LoRA-SP ✅

- ✅ `olr_qr` / `olr_ortho` / `olr_train` / `olr_score` / `olr_stable` / `olr_loop_plan`
- ✅ `lsp_select` / `lsp_freeze` / `lsp_train` / `lsp_score` / `lsp_memory` / `lsp_loop_plan`
- ✅ `olr_lsp_shaped_report`
- ✅ Frontiers research §§328–329
- ✅ MCP tools → 1535; CLI `olr-*` / `lsp-*`

## Phase 153 — v15.7 QPiSSA + MoSLoRA ✅

- ✅ `qps_quant` / `qps_principal` / `qps_train` / `qps_score` / `qps_error` / `qps_loop_plan`
- ✅ `msl_split` / `msl_mixer` / `msl_train` / `msl_score` / `msl_fuse` / `msl_loop_plan`
- ✅ `qps_msl_shaped_report`
- ✅ Frontiers research §§330–331
- ✅ MCP tools → 1547; CLI `qps-*` / `msl-*`

## Phase 154 — v15.8 LoRA-drop + VB-LoRA ✅

- ✅ `ldr_eval` / `ldr_keep` / `ldr_share` / `ldr_score` / `ldr_prune` / `ldr_loop_plan`
- ✅ `vbl_bank` / `vbl_topk` / `vbl_compose` / `vbl_score` / `vbl_extreme` / `vbl_loop_plan`
- ✅ `ldr_vbl_shaped_report`
- ✅ Frontiers research §§332–333
- ✅ MCP tools → 1559; CLI `ldr-*` / `vbl-*`

## Phase 155 — v15.9 OPLoRA + GeLoRA ✅

- ✅ `opl_proj` / `opl_constrain` / `opl_train` / `opl_score` / `opl_forget` / `opl_loop_plan`
- ✅ `gel_idim` / `gel_rank` / `gel_train` / `gel_score` / `gel_budget` / `gel_loop_plan`
- ✅ `opl_gel_shaped_report`
- ✅ Frontiers research §§334–335
- ✅ MCP tools → 1571; CLI `opl-*` / `gel-*`

## Phase 156 — v16.0 GeoLoRA + RandLoRA ✅

- ✅ `geo_dyn` / `geo_budget` / `geo_train` / `geo_score` / `geo_ortho` / `geo_loop_plan`
- ✅ `rlo_bases` / `rlo_scale` / `rlo_train` / `rlo_score` / `rlo_fullrank` / `rlo_loop_plan`
- ✅ `geo_rlo_shaped_report`
- ✅ Frontiers research §§336–337
- ✅ MCP tools → 1583; CLI `geo-*` / `rlo-*`

## Phase 157 — v16.1 LoRAShear + alternating OPLoRA ✅

- ✅ `lsh_graph` / `lsh_prune` / `lsh_recover` / `lsh_score` / `lsh_footprint` / `lsh_loop_plan`
- ✅ `aop_sub` / `aop_alt` / `aop_train` / `aop_score` / `aop_svd` / `aop_loop_plan`
- ✅ `lsh_aop_shaped_report`
- ✅ Frontiers research §§338–339
- ✅ MCP tools → 1595; CLI `lsh-*` / `aop-*`

## Phase 158 — v16.2 LoRA-Init + LoRA-Null ✅

- ✅ `lin_tsd` / `lin_init` / `lin_train` / `lin_score` / `lin_fast` / `lin_loop_plan`
- ✅ `lnu_act` / `lnu_null` / `lnu_train` / `lnu_score` / `lnu_forget` / `lnu_loop_plan`
- ✅ `lin_lnu_shaped_report`
- ✅ Frontiers research §§340–341
- ✅ MCP tools → 1607; CLI `lin-*` / `lnu-*`

## Phase 159 — v16.3 HydraLoRA + LoRA-LEGO ✅

- ✅ `hyd_share` / `hyd_heads` / `hyd_route` / `hyd_score` / `hyd_nodomain` / `hyd_loop_plan`
- ✅ `llg_msu` / `llg_cluster` / `llg_merge` / `llg_score` / `llg_modular` / `llg_loop_plan`
- ✅ `hyd_llg_shaped_report`
- ✅ Frontiers research §§342–343
- ✅ MCP tools → 1619; CLI `hyd-*` / `llg-*`

## Phase 160 — v16.4 LoRAMoE + MoELoRA ✅

- ✅ `lme_plugin` / `lme_balance` / `lme_route` / `lme_score` / `lme_forget` / `lme_loop_plan`
- ✅ `mel_experts` / `mel_contrast` / `mel_gate` / `mel_score` / `mel_sparse` / `mel_loop_plan`
- ✅ `lme_mel_shaped_report`
- ✅ Frontiers research §§344–345
- ✅ MCP tools → 1631; CLI `lme-*` / `mel-*`

## Phase 161 — v16.5 LoraHub + MultiLoRA ✅

- ✅ `lhb_pool` / `lhb_compose` / `lhb_adapt` / `lhb_score` / `lhb_nograd` / `lhb_loop_plan`
- ✅ `mlr_scale` / `mlr_init` / `mlr_train` / `mlr_score` / `mlr_demo` / `mlr_loop_plan`
- ✅ `lhb_mlr_shaped_report`
- ✅ Frontiers research §§346–347
- ✅ MCP tools → 1643; CLI `lhb-*` / `mlr-*`

## Phase 162 — v16.6 MTL-LoRA + MALoRA ✅

- ✅ `mtl_task` / `mtl_spec` / `mtl_share` / `mtl_score` / `mtl_interfere` / `mtl_loop_plan`
- ✅ `mal_mix` / `mal_down` / `mal_up` / `mal_score` / `mal_eff` / `mal_loop_plan`
- ✅ `mtl_mal_shaped_report`
- ✅ Frontiers research §§348–349
- ✅ MCP tools → 1655; CLI `mtl-*` / `mal-*`

## Phase 163 — v16.7 LoRA-Mini + QDyLoRA ✅

- ✅ `lmi_split` / `lmi_inner` / `lmi_train` / `lmi_score` / `lmi_tiny` / `lmi_loop_plan`
- ✅ `qdy_range` / `qdy_quant` / `qdy_train` / `qdy_score` / `qdy_pick` / `qdy_loop_plan`
- ✅ `lmi_qdy_shaped_report`
- ✅ Frontiers research §§350–351
- ✅ MCP tools → 1667; CLI `lmi-*` / `qdy-*`

## Phase 164 — v16.8 LoRA-TSD + S-LoRA ✅

- ✅ `lts_tsd` / `lts_init` / `lts_dash` / `lts_score` / `lts_combo` / `lts_loop_plan`
- ✅ `slr_pool` / `slr_page` / `slr_batch` / `slr_score` / `slr_scale` / `slr_loop_plan`
- ✅ `lts_slr_shaped_report`
- ✅ Frontiers research §§352–353
- ✅ MCP tools → 1679; CLI `lts-*` / `slr-*`

## Phase 165 — v16.9 Compress-then-Serve + FLoRA ✅

- ✅ `cts_collect` / `cts_basis` / `cts_scale` / `cts_score` / `cts_cluster` / `cts_loop_plan`
- ✅ `flo_clients` / `flo_stack` / `flo_agg` / `flo_score` / `flo_hetero` / `flo_loop_plan`
- ✅ `cts_flo_shaped_report`
- ✅ Frontiers research §§354–355
- ✅ MCP tools → 1691; CLI `cts-*` / `flo-*`

## Phase 166 — v17.0 Punica + mLoRA ✅

- ✅ `pun_backbone` / `pun_sgmv` / `pun_sched` / `pun_score` / `pun_multi` / `pun_loop_plan`
- ✅ `mla_pipe` / `mla_batch` / `mla_train` / `mla_score` / `mla_eff` / `mla_loop_plan`
- ✅ `pun_mla_shaped_report`
- ✅ Frontiers research §§356–357
- ✅ MCP tools → 1703; CLI `pun-*` / `mla-*`

## Phase 167 — v17.1 SwitchLoRA + Chain of LoRA ✅

- ✅ `swl_alloc` / `swl_switch` / `swl_train` / `swl_score` / `swl_full` / `swl_loop_plan`
- ✅ `col_tune` / `col_knot` / `col_extend` / `col_score` / `col_gap` / `col_loop_plan`
- ✅ `swl_col_shaped_report`
- ✅ Frontiers research §§358–359
- ✅ MCP tools → 1715; CLI `swl-*` / `col-*`

## Phase 168 — v17.2 DeLoRA + MELoRA ✅

- ✅ `dlr_norm` / `dlr_bound` / `dlr_train` / `dlr_score` / `dlr_robust` / `dlr_loop_plan`
- ✅ `meo_mini` / `meo_diag` / `meo_train` / `meo_score` / `meo_rank` / `meo_loop_plan`
- ✅ `dlr_meo_shaped_report`
- ✅ Frontiers research §§360–361
- ✅ MCP tools → 1727; CLI `dlr-*` / `meo-*`

## Phase 169 — v17.3 ReLoRA + ETHER ✅

- ✅ `rlr_warm` / `rlr_merge` / `rlr_jagged` / `rlr_score` / `rlr_high` / `rlr_loop_plan`
- ✅ `eth_plane` / `eth_reflect` / `eth_train` / `eth_score` / `eth_plus` / `eth_loop_plan`
- ✅ `rlr_eth_shaped_report`
- ✅ Frontiers research §§362–363
- ✅ MCP tools → 1739; CLI `rlr-*` / `eth-*`

## Phase 170 — v17.4 LoRA-Composer + CARE-LoRA ✅

- ✅ `lco_concepts` / `lco_inject` / `lco_isolate` / `lco_score` / `lco_free` / `lco_loop_plan`
- ✅ `car_compress` / `car_recon` / `car_train` / `car_score` / `car_mem` / `car_loop_plan`
- ✅ `lco_car_shaped_report`
- ✅ Frontiers research §§364–365
- ✅ MCP tools → 1751; CLI `lco-*` / `car-*`

## Phase 171 — v17.5 LoRA.rar + SVFT ✅

- ✅ `lrr_pair` / `lrr_hyper` / `lrr_merge` / `lrr_score` / `lrr_fast` / `lrr_loop_plan`
- ✅ `svf_svd` / `svf_sparse` / `svf_train` / `svf_score` / `svf_geom` / `svf_loop_plan`
- ✅ `lrr_svf_shaped_report`
- ✅ Frontiers research §§366–367
- ✅ MCP tools → 1763; CLI `lrr-*` / `svf-*`

## Phase 172 — v17.6 FlyLoRA + NOLA ✅

- ✅ `fly_proj` / `fly_topk` / `fly_train` / `fly_score` / `fly_implicit` / `fly_loop_plan`
- ✅ `nla_basis` / `nla_coeff` / `nla_train` / `nla_score` / `nla_compact` / `nla_loop_plan`
- ✅ `fly_nla_shaped_report`
- ✅ Frontiers research §§368–369
- ✅ MCP tools → 1775; CLI `fly-*` / `nla-*`

## Phase 173 — v17.7 MixLoRA + SuperLoRA ✅

- ✅ `mxl_experts` / `mxl_route` / `mxl_attn` / `mxl_score` / `mxl_balance` / `mxl_loop_plan`
- ✅ `spr_group` / `spr_fold` / `spr_factor` / `spr_score` / `spr_unify` / `spr_loop_plan`
- ✅ `mxl_spr_shaped_report`
- ✅ Frontiers research §§370–371
- ✅ MCP tools → 1787; CLI `mxl-*` / `spr-*`

## Phase 174 — v17.8 Tied-LoRA + QA-LoRA ✅

- ✅ `tld_tie` / `tld_select` / `tld_scale` / `tld_score` / `tld_frac` / `tld_loop_plan`
- ✅ `qal_group` / `qal_quant` / `qal_adapt` / `qal_score` / `qal_merge` / `qal_loop_plan`
- ✅ `tld_qal_shaped_report`
- ✅ Frontiers research §§372–373
- ✅ MCP tools → 1799; CLI `tld-*` / `qal-*`

## Phase 175 — v17.9 Uni-LoRA + BoRA ✅

- ✅ `ulo_space` / `ulo_iso` / `ulo_vec` / `ulo_score` / `ulo_one` / `ulo_loop_plan`
- ✅ `bor_row` / `bor_col` / `bor_train` / `bor_score` / `bor_sym` / `bor_loop_plan`
- ✅ `ulo_bor_shaped_report`
- ✅ Frontiers research §§374–375
- ✅ MCP tools → 1811; CLI `ulo-*` / `bor-*`

## Phase 176 — v18.0 Q-GaLore + LoRA-Flow ✅

- ✅ `qga_weight` / `qga_proj` / `qga_lazy` / `qga_score` / `qga_mem` / `qga_loop_plan`
- ✅ `lfw_pool` / `lfw_gate` / `lfw_token` / `lfw_score` / `lfw_few` / `lfw_loop_plan`
- ✅ `qga_lfw_shaped_report`
- ✅ Frontiers research §§376–377
- ✅ MCP tools → 1823; CLI `qga-*` / `lfw-*`

## Phase 177 — v18.1 RoSA + ABBA ✅

- ✅ `ros_rank` / `ros_sparse` / `ros_train` / `ros_score` / `ros_fft` / `ros_loop_plan`
- ✅ `abb_left` / `abb_right` / `abb_hadamard` / `abb_score` / `abb_expr` / `abb_loop_plan`
- ✅ `ros_abb_shaped_report`
- ✅ Frontiers research §§378–379
- ✅ MCP tools → 1835; CLI `ros-*` / `abb-*`

## Phase 178 — v18.2 BoHA + SMoA ✅

- ✅ `bha_split` / `bha_hadamard` / `bha_train` / `bha_score` / `bha_local` / `bha_loop_plan`
- ✅ `smo_struct` / `smo_mod` / `smo_train` / `smo_score` / `smo_rank` / `smo_loop_plan`
- ✅ `bha_smo_shaped_report`
- ✅ Frontiers research §§380–381
- ✅ MCP tools → 1847; CLI `bha-*` / `smo-*`

## Phase 179 — v18.3 GLoRA + PeriodicLoRA ✅

- ✅ `glo_prompt` / `glo_scale` / `glo_search` / `glo_score` / `glo_zero` / `glo_loop_plan`
- ✅ `plr_stage` / `plr_merge` / `plr_reset` / `plr_score` / `plr_rank` / `plr_loop_plan`
- ✅ `glo_plr_shaped_report`
- ✅ Frontiers research §§382–383
- ✅ MCP tools → 1859; CLI `glo-*` / `plr-*`

## Phase 180 — v18.4 HiRA + concurrent PLoRA ✅

- ✅ `hir_base` / `hir_factors` / `hir_hadamard` / `hir_score` / `hir_merge` / `hir_loop_plan`
- ✅ `cnl_pack` / `cnl_fuse` / `cnl_train` / `cnl_score` / `cnl_hw` / `cnl_loop_plan`
- ✅ `hir_cnl_shaped_report`
- ✅ Frontiers research §§384–385
- ✅ MCP tools → 1871; CLI `hir-*` / `cnl-*`

## Phase 181 — v18.5 LongLoRA + LISA ✅

- ✅ `llr_window` / `llr_shift` / `llr_lora` / `llr_score` / `llr_sparse` / `llr_loop_plan`
- ✅ `lis_layers` / `lis_sample` / `lis_unfreeze` / `lis_score` / `lis_memory` / `lis_loop_plan`
- ✅ `llr_lis_shaped_report`
- ✅ Frontiers research §§386–387
- ✅ MCP tools → 1883; CLI `llr-*` / `lis-*`

## Phase 182 — v18.6 NLoRA + ROSA random subspace ✅

- ✅ `nlr_landmark` / `nlr_nystrom` / `nlr_init` / `nlr_score` / `nlr_cheap` / `nlr_loop_plan`
- ✅ `rsa_subspace` / `rsa_project` / `rsa_train` / `rsa_score` / `rsa_express` / `rsa_loop_plan`
- ✅ `nlr_rsa_shaped_report`
- ✅ Frontiers research §§388–389
- ✅ MCP tools → 1895; CLI `nlr-*` / `rsa-*`

## Phase 183 — v18.7 HRA + Hybrid PEFT ✅

- ✅ `hra_house` / `hra_reflect` / `hra_train` / `hra_score` / `hra_ortho` / `hra_loop_plan`
- ✅ `hyb_lora` / `hyb_boft` / `hyb_fuse` / `hyb_score` / `hyb_stable` / `hyb_loop_plan`
- ✅ `hra_hyb_shaped_report`
- ✅ Frontiers research §§390–391
- ✅ MCP tools → 1907; CLI `hra-*` / `hyb-*`

## Phase 184 — v18.8 LoRTA + C-LoRA ✅

- ✅ `lrt_tensor` / `lrt_cp` / `lrt_share` / `lrt_score` / `lrt_compact` / `lrt_loop_plan`
- ✅ `clo_route` / `clo_task` / `clo_ortho` / `clo_score` / `clo_forget` / `clo_loop_plan`
- ✅ `lrt_clo_shaped_report`
- ✅ Frontiers research §§392–393
- ✅ MCP tools → 1919; CLI `lrt-*` / `clo-*`

## Phase 185 — v18.9 ALoRA + LN Tuning ✅

- ✅ `alo_init` / `alo_ablate` / `alo_prune` / `alo_score` / `alo_realloc` / `alo_loop_plan`
- ✅ `lnt_attn` / `lnt_scale` / `lnt_train` / `lnt_score` / `lnt_cheap` / `lnt_loop_plan`
- ✅ `alo_lnt_shaped_report`
- ✅ Frontiers research §§394–395
- ✅ MCP tools → 1931; CLI `alo-*` / `lnt-*`

## Phase 186 — v18.10 LoRAFusion + TeRA ✅

- ✅ `lfu_split` / `lfu_fuse` / `lfu_batch` / `lfu_score` / `lfu_speed` / `lfu_loop_plan`
- ✅ `ter_tucker` / `ter_freeze` / `ter_scale` / `ter_score` / `ter_highrank` / `ter_loop_plan`
- ✅ `lfu_ter_shaped_report`
- ✅ Frontiers research §§396–397
- ✅ MCP tools → 1943; CLI `lfu-*` / `ter-*`

## Phase 187 — v18.11 TensLoRA + AdaZeta ✅

- ✅ `tnl_stack` / `tnl_tucker` / `tnl_mode` / `tnl_score` / `tnl_budget` / `tnl_loop_plan`
- ✅ `azt_tt` / `azt_ff` / `azt_query` / `azt_score` / `azt_mem` / `azt_loop_plan`
- ✅ `tnl_azt_shaped_report`
- ✅ Frontiers research §§398–399
- ✅ MCP tools → 1955; CLI `tnl-*` / `azt-*`

## Phase 188 — v18.12 FacT + LoTR ✅

- ✅ `fct_tensor` / `fct_tt` / `fct_tucker` / `fct_score` / `fct_tiny` / `fct_loop_plan`
- ✅ `ltr_stack` / `ltr_core` / `ltr_share` / `ltr_score` / `ltr_deep` / `ltr_loop_plan`
- ✅ `fct_ltr_shaped_report`
- ✅ Frontiers research §§400–401
- ✅ MCP tools → 1967; CLI `fct-*` / `ltr-*`

## Phase 189 — v18.13 CaRA + LoRETTA ✅

- ✅ `cra_mha` / `cra_ffn` / `cra_cpd` / `cra_score` / `cra_heads` / `cra_loop_plan`
- ✅ `ltt_adp` / `ltt_rep` / `ltt_tt` / `ltt_score` / `ltt_tiny` / `ltt_loop_plan`
- ✅ `cra_ltt_shaped_report`
- ✅ Frontiers research §§402–403
- ✅ MCP tools → 1979; CLI `cra-*` / `ltt-*`

## Phase 190 — v18.14 C3A + BOFT ✅

- ✅ `c3a_kernel` / `c3a_circ` / `c3a_fft` / `c3a_score` / `c3a_rank` / `c3a_loop_plan`
- ✅ `bof_block` / `bof_orth` / `bof_butter` / `bof_score` / `bof_full` / `bof_loop_plan`
- ✅ `c3a_bof_shaped_report`
- ✅ Frontiers research §§404–405
- ✅ MCP tools → 1991; CLI `c3a-*` / `bof-*`

## Phase 191 — v18.15 SDT + MEFT ✅

- ✅ `sdt_dim` / `sdt_mask` / `sdt_tune` / `sdt_score` / `sdt_ssm` / `sdt_loop_plan`
- ✅ `mef_adapt` / `mef_route` / `mef_fetch` / `mef_score` / `mef_cpu` / `mef_loop_plan`
- ✅ `sdt_mef_shaped_report`
- ✅ Frontiers research §§406–407
- ✅ MCP tools → 2003; CLI `sdt-*` / `mef-*`
- ✅ Live-fetched titles: *Parameter-Efficient Fine-Tuning of State Space Models* (2410.09016); *MEFT: Memory-Efficient Fine-Tuning through Sparse Adapter* (2406.04984)
- ✅ Prefixes locked: `sdt_*` / `mef_*` (grep-clean at ship)

## Phase 192 — v18.16 next PEFT pair ⏳ pending

- ⏳ Two unused PEFT papers as stdlib proxies (6 ops each + harness +12 MCP)
- ⏳ Live-fetch titles; grep CLI + ops + modules before locking prefixes
- ⏳ Do not reuse `sdt_*` / `mef_*` / `bft_*` / `oft_*` / `bof_*` / `c3a_*` / `cra_*` / `ltt_*` / `mss_*`
- ⏳ PRD UC-1979–1989 · TECH_SPEC §7.191 · frontiers §§408–409 · MCP → 2015 · version 18.16.0

## Post-v18.15 (research / ops — not blocking)

- Optional real-git adapter (export commits as git repo) — caller-side
- ChronoMem NL→version mapping / LatticeMind LLM reconciler / STALE implicit NLI — caller-side
- Native GEM engine / MemState property-graph backend — explicit non-goal for core
- Full external gym integration (MemoryArena / MemBench / MemHop / LightMem harness adapters)
- Hosted multi-store sync / full MELD CRDT transport (explicit non-goal today)
- Keyed TRACE/MemMark / PoEM HMAC watermarks (caller-side secret; never required on core write path)
- TOKI LLM judge / SCM MeaningEncoder / LightMem LLMLingua on write path — explicit non-goal
- Wire `admit_gate` / `write_gate` as hard pre-check inside ADD/promote (opt-in policy flag)
- Learned TierMem miss detector / MemSkill skill designer / MemCon UCB trainer — caller-side
- Auto-delete on fade/archive/sleep forget alone — explicit non-goal (plans are report-only; apply needs actor)

## Explicitly out of scope (all phases)

- Training-time memory · LLM extraction on write path · owning a DB engine as SoT · pack pricing
