# Governed Experiential Memory — Frontiers Research (2026)

> **Status:** Source-audited companion · **v3.7** · **Date:** 2026-08-20  
> **Scope:** What *new* primary literature (2025–2026) changes the Stele product bar after the master ledger + storage research docs. Product SKU / pricing still out of scope.  
> **Method:** Primary papers (arXiv / venue / project sites). Load-bearing claims cite arXiv IDs.  
> **Companions:** `AGENT_SESSION_LEDGER_INFERENCE_TIME_MEMORY_RESEARCH_2026.md` · `AGENT_MEMORY_STORAGE_SYSTEMS_RESEARCH_2026.md` · `docs/patterns/patterns_session_ledger_memory.yaml`

---

## Executive summary

| Finding | Source | Stele implication |
|---|---|---|
| Recall-saturated systems still fail when memory must **drive later actions** across sessions | MemoryArena (arXiv:2602.16313) | Keep task-outcome harness as success oracle; never ship “LoCoMo green” as product proof |
| Memory research has converged on **write → manage → read** loops; reflection without quality gates self-poisons | Survey (arXiv:2603.07670) | Quarantine + external oracle remain non-negotiable (C7) |
| Enterprise multi-agent systems need **shared memory + governance**, not more silos | Governed Memory (arXiv:2603.17787) | Stele’s governance surface is the differentiator vs extract-and-store RAG |
| Interop needs a **vendor-neutral wire**, not another store | memorywire (arXiv:2606.01138) | Export JSON Schema + optional remember/recall projection; do not become a silo |
| Long-horizon chat memory still fails on **updates, temporal reasoning, abstention** | LongMemEval (arXiv:2410.10813; ICLR 2025) | Stale flags, supersede, empty search, withhold policies stay first-class |
| Agent-driven **link + evolve** graphs beat flat dumps on multi-hop | A-MEM (arXiv:2502.12110) | LINK / related / follow_link_depth are core, not polish |
| Multi-metric agent memory eval (accuracy/recall/**capacity**/efficiency) | MemBench (ACL 2025; arXiv:2506.21605) | Ship MemBench-*shaped* proxies in harness; simple retrieval stays competitive at scale |
| **Provenance** is the strongest lever to recover a poisoned store | memorywire + PurgeBench (arXiv:2606.01138) | `purge_by_provenance` dry-run/execute; entangled poison stays human-review |
| Write / Select / Compress / Isolate is the context-engineering stack | LangChain + field practice 2025–26 | Batch write, trusted-source Select filter, body compress already shipped |
| Passive RAG leaves a **Governance Gap** — zombie memories, contradictions, privacy | MemArchitect (arXiv:2603.18330) | Report-only hygiene candidates; never auto-delete on utility heuristics alone |
| Evolving memory needs **read filtering**, decay, and access control before consolidation | SSGM (arXiv:2603.11768) | `prefer_fresh` Select; provenance trusted filter; human-review entangled queue |
| Governance eval must measure **deletion / access / forgetting**, not only recall | Survey Layer-4 + MOA/MGB framing | `governance_shaped_report` local proxies — not a claimed MGB score |
| Shared multi-principal memory fails unless **utility ∩ access control ∩ forgetting** hold together | GateMem (arXiv:2606.18829) | `principal_scopes`, `forget_compliance`, `gatemem_shaped_report` |
| Fleet memory is a **distributed systems** problem (scope, supersession, provenance, propagation) | Governed Shared Memory / MemClaw (arXiv:2606.24535) | Keep contested + supersede + journal provenance; no silent merge |
| No single memory architecture dominates; align structure to bottleneck; prefer localized maintenance | Agent-Native Memory (arXiv:2606.24775) | Stay protocol-thin; hybrid BM25 default; REFLECT local not global rewrite |
| Contradiction resolution is **write-time concurrency control**; baselines admit audit erasure / replay / belief-drift | TOKI (arXiv:2606.06240) | `lineage` + supersede keeps losers; no LLM judge on write path |
| Collapsing conflicts raises false certainty; preserve conflict surfaces for abstention | StateFuse (arXiv:2607.05844) | `conflict_surface` pairs; contested never auto-merged |
| Four memory competencies: retrieval, test-time learning, long-range, selective forgetting | MemoryAgentBench (arXiv:2507.05257) | `belief_at` + `memoryagent_shaped_report` |
| Memory injection diverts agents from user intent; lightweight detectors beat repeated LLM audits | MIND (arXiv:2607.28103) | `injection_scan` deterministic markers (no neural IB / no LLM) |
| Poisoned memory links need gates at **write · retrieve · promote · reuse** | MAPLE-Guard (arXiv:2608.00426) | quarantine write; `withhold_injection_suspects`; `block_injection_suspects`; pack redaction |
| Long-term memory needs **snapshot attribution** when external logs are lost | MemMark (arXiv:2605.25002) | `store_seal` / `attribution_receipt` / `verify_seal` (deterministic; no keyed sampler) |
| Trajectory provenance must survive deletion **and** rewriting | TRACE (arXiv:2607.08400) | Journal + content digests; soft `replay_consistency` (not behavioral watermark) |
| Retrieval eligibility needs **utility-aware tiers**, not only TTL/LRU | AMV-L (arXiv:2603.04443) | `lifecycle_tier` / `lifecycle_tiers` Select filter |
| Stale active memory under a conflict key is **pollution**; revoke without erase | TEPA (arXiv:2608.07429) | `conflict_key` + `revoke_by_key` / state `revoked` |
| Exported packs need **attestation** independent of the live journal | product (v1.7) | `pack_seal` / `verify_pack_seal` |
| Federated claims need **five-outcome classify**, never silent rewrite | MELD (arXiv:2608.16357) | `merge_classify` report-only |
| Provenance must be an **operational Select signal**, not post-hoc audit | MAP-Graph (arXiv:2608.10509) | `path_trust` + `min_path_trust` |
| Isolated retrieval misses **associative LINK neighborhoods** | RippleMem (arXiv:2608.13334) | `blast_radius` |
| Journal integrity needs **hash-chained events**, not only flat digests | GPM (arXiv:2608.12476) | `verify_journal_chain` |
| Relevance can emerge from **spreading activation**, not cosine alone | SYNAPSE (ACL 2026 Findings) | `spread_activate` |
| Multi-signal recall should rank by **connection density** | SodaMem (arXiv:2608.08055) | `prefer_dense` / `connection_density` |
| Long-horizon control needs **decay-driven retention** | Oblivion (arXiv:2604.00131) | `retention_score` / `min_retention` |
| Public answers need **fail-closed release** at a verified head | GPM release (arXiv:2608.12476) | `release_gate` / `require_release` |
| Storage is not memory — **derived indexes** must not become SoT | True Memory (arXiv:2605.04897) | SQLite FTS derived; files remain SoT |
| Released claims need a **local decision record** at the verified head | GPM decision receipts (arXiv:2608.12476) | `issue_receipt` / `decisions/` |
| Foreign packs need **halt-on-first-failure** import verify | Portable Agent Memory (arXiv:2605.11032) | `verify_import` |
| Retrieval must refuse **untrusted lineage** ancestors | MemLineage (arXiv:2605.14421) | `lineage_trust` / `refuse_untrusted_lineage` |
| Safety skips need **proof of execution**, not memory wording | PoEM (arXiv:2608.16032) | `record_execution` / `verify_execution` |
| Consolidation must not **launder provenance authority** | PPMF (arXiv:2607.29167) | `authority_gate` |
| Released claims need **exact closure** over promoted facts | GPM claim closure (arXiv:2608.12476) | `claim_closure` |
| Invalidated sources leave **stale descendants in service** | MemoRepair (arXiv:2605.07242) | `withdraw_cascade` / `repair_plan` |
| Retracted facts must not **revive** in ordinary Select | GPM non-revival | `non_revival_probe` |
| Flat text causes **provenance-role collapse** | MemIR (arXiv:2605.25869) | `memory_role` / `fact_interface` |
| Routine retrieval needs a **quality-gated deliberation** fallback | D-Mem (arXiv:2603.18631) | `dual_channel_search` / `quality_gate` |
| Reasoning/memory views need **replay, diff, merge** | GitOfThoughts (arXiv:2606.14470) | `commit_view` / `diff_commits` |
| Memory accuracy pays mainly on **near-duplicates** | GitOfThoughts copyability τ≈0.8 | `copyability_gate` |
| Agents need **global memory version + counterfactual Select** after exposure | ChronoMem (arXiv:2607.27773) | `pin_memory_version` / `activate_version` / `counterfactual_search` |
| Similarity cannot retire stale facts; need **deterministic supersession** | MemStrata (arXiv:2606.26511) | `exclude_superseded` / `stale_fact_scan` |
| Binary Write/Hold collapses distinct update outcomes | TARL (arXiv:2608.03699) | `propose_update` / `apply_update` five actions |
| Governance needs an **outcome co-occurrence** forget signal | Memory Worth (arXiv:2604.12007) | `memory_worth` / `min_worth` / `low_worth_scan` |
| A memory **write is not a belief commit**; act only on action-safe | MemTX (arXiv:2607.23929) | `begin_transaction` / `commit_transaction` / `action_safe_gate` |
| Always-on agents need **mutation/recovery obligation** scoring | Always-On / AOEP-v0 (arXiv:2606.30306) | `aoep_report` |
| Multi-agent contradiction is a **memory** problem (symbolic + selective reconcile) | LatticeMind (arXiv:2608.08236) | `symbolic_conflict_scan` / `classify_conflict` / `compact_render` |
| Tool side effects need an **outbox** separate from belief commit | Cordon (arXiv:2606.17573) | `stage_effect` / `release_effects` |
| Implicit conflict + IPA gap: update visible ≠ behavior adapted | STALE + VTA (arXiv:2605.06527, 2608.01619) | `state_resolution` / `premise_resistance` / `verify_transition` |
| Memory correctness is a **state trajectory**, not record CRUD | GEM (arXiv:2605.26252) | `gem_report` six conditions |
| Projection resolvers must **not rewrite** replicated SoT | StateFuse deepen (arXiv:2607.05844) | `project_resolve` / `pin_projection` / `correction_handle` |
| Write operators need typed isolation + anomaly probes | TOKI deepen (arXiv:2606.06240) | `toki_classify_operator` / `toki_anomaly_scan` |
| Context slots need **triage & bid**, not passive top-k | MemArchitect (arXiv:2603.18330) | `context_bid` |
| Cascade repair needs **exact** predecessor-closed selection | MemoRepair min-cut (arXiv:2605.07242) | `repair_select_mincut` |
| Write-side adjudication before query time | CUPMem / STALE (arXiv:2605.06527) | `adjudicate_update` / `authorize_retrieval` |
| Protected writes need **procedural admit receipts** | CMGL (certified memory governance) | `admit_gate` |
| Summary-only memory loses query-critical detail | TierMem (arXiv:2602.17913) | `sufficiency_gate` / `escalate_raw` / `verified_writeback` |
| Memory should become **callable skills**, not passive context | MSCE (arXiv:2607.16621) | `crystallize_skill` / `skill_catalog` |
| Dual-layer forgetting needs **differential decay**, not one TTL | FadeMem (arXiv:2601.18642) | `fade_strength` / `fade_scan` / `fusion_candidates` |
| Relevance should use **Weibull time-decay**, not only recency rank | SSGM (arXiv:2603.11768) | `weibull_relevance` / `min_weibull` |
| Retrieval must **close evidence gaps** with follow-up probes | MemR3 (arXiv:2512.20237) | `evidence_gap` / `reflective_retrieve` |
| Forgetting should be **accessibility reduction**, not hard delete | Oblivion (arXiv:2604.00131) | `archive_plan` / `archive_apply` / `unarchive` |
| Compact memory needs **composite importance tiers** | SF-AMS (arXiv:2607.22562) | `composite_importance` / `cis_scan` |
| Memory ops should be a **controlled policy**, not fixed always-on retrieve | MemCon (arXiv:2607.13591) | `control_suggest` |
| Offline **sleep stages** consolidate + forget without wake-path LLM | SCM (arXiv:2604.20943) | `sleep_plan` / `wm_*` / `value_tag` |
| Encoding must **decouple** from consolidation at semantic boundaries | GAM (arXiv:2604.12285) | `episodic_buffer` / `semantic_boundary` / `consolidate_plan` |
| Context is a **lifecycle** (anticipate + verifiable compact) | ACM (arXiv:2607.21503) | `anticipate` / `verify_compaction` |
| Efficiency needs **sensory→STM→LTM** stages, not raw-ingest RAG | LightMem (arXiv:2510.18866) | `sensory_filter` / `stage_budget_plan` |
| Multi-hop recall needs **graph PPR**, not isolated top-k | HippoRAG (NeurIPS 2024; MemHop 2026) | `ppr_scores` / `multi_hop_retrieve` |
| Agent-written facts need **gated post-state** + risk action gates | Quipu (arXiv:2608.16813) + MAP-Graph | `write_gate` / `action_risk_gate` |
| Summaries need **compression residuals** + profile expand | ProGraph (arXiv:2607.19359) | `extract_residuals` / `profile_expand` |
| Failures need **one-shot correction paths**, not reflect-replay | EMG (experience-memory graph) | `match_correction` / `insight_inject` |
| Retrieval should **cascade channels** and fuse via RRF | AgentIR / MemFuse-style | `cascade_route` / `multi_channel_fuse` |
| Enterprise agents need **dual facts+properties** + progressive delta | Governed Memory (arXiv:2603.17787) | `dual_project` / `session_delta_*` |
| Entity retrieval must **key-filter**, not rely on embedding distance | Governed Memory isolation | `entity_context` / `entity_leak_probe` |
| Long-horizon planners need **typed context isolation** | HyMem (arXiv:2608.15703) | `hymem_classify_slot` / `hymem_isolate_pack` |
| Conflict resolution bottleneck is **assembly**, not storage | Deterministic freshness (arXiv:2606.01435) | `assemble_current` / `freshness_resolve` |
| Updates need **source-supported patch tests** + temporal tips | MemTxn (arXiv:2607.27834) | `patch_test` / `temporal_resolve` |
| Fleet memory needs **scoped propagate** without silent merge | Governed Shared Memory (arXiv:2606.24535) | `propagate_plan` / `stale_propagation_scan` |
| Runtime memory needs **query-aware budget tiers** | BudgetMem (arXiv:2602.06025) | `budget_tier_route` / `budget_module_plan` |
| Large skill libraries need **lexical rank**, not graph reach myths | Skill retrieval study (arXiv:2608.06196) | `skill_rank` / `skill_prereq_expand` |
| Retrieval should be **skill-composed primitives** | ERSkill (arXiv:2608.12720) | `route_retrieval_skill` / `run_retrieval_skill` |
| Write admission needs **support≥τ**, not utility alone | ConsistencyGate (arXiv:2607.22962) | `consistency_admit` / `support_score` |
| Retrieval must be **task-conditioned**, not raw similarity | MemGate (arXiv:2606.06054) | `retrieval_admit` / `task_conditioned_pack` |
| Governance needs **post-delete verify + rollback** | Mnemonic sovereignty survey (arXiv:2604.16548) | `post_delete_verify` / `rollback_plan` |
| Multi-tunnel answers need **density mass + citations** | SodaMem (arXiv:2608.08055) | `density_fuse` / `evidence_plan` / `cited_pack` |
| Storage budgets need **rule compress**, not LLM judges | MemRefine (arXiv:2606.13177) | `compress_candidates` / `refine_plan` |
| Coarsening needs **merge\|link\|add + bridges** | AriadneMem / MemFuse (arXiv:2608.18704) | `merge_link_add` / `bridge_discover` / `fuse_cluster` |
| Temporal answers need **verified operator plans + claim checks** | TGMS (arXiv:2607.10265) | `plan_static_verify` / `claim_verify` / `result_digest` |
| Maintenance should be **localized**, not global reorganize | MemoryData / agent-native (arXiv:2606.24775) | `localized_maintenance_plan` / `maintenance_cost_compare` |
| Authority must be **origin-bound**, not content/lineage | TMA-NM (arXiv:2606.24322) | `origin_bind` / `propagate_origin` / `act_authority_gate` |
| Indirect poisoning needs **save policy + retrieval screen** | AM-Sentry / GhostWriter (arXiv:2607.06595) | `save_policy` / `retrieval_screen` |
| Temporal memory needs **hierarchical index**, not full rewrites | MemForest / MemTree (arXiv:2605.23986) | `build_memtree` / `dirty_path_plan` / `coarse_to_fine` |
| Agent streams need **decouple→aggregate** top-down retrieval | xMemory (arXiv:2602.02007) | `theme_attach` / `split_merge_plan` / `top_down_pack` |
| Poisoning must be traced **Write→Execute→Forget** | MemSecBench (arXiv:2607.27080) | `lifecycle_report` / `selective_repair_plan` |
| Proactive interference needs **sleep-style forget** | SleepGate (arXiv:2603.14517) | `conflict_tag` / `forget_gate_plan` / `pi_depth_scan` |
| Retrieval admit needs **multi-channel consensus** | A-MemGuard | `consensus_admit` |
| Post-failure repair needs **dependency-guided replay** | DepRepair (arXiv:2608.10502) | `selective_replay_plan` / `preserve_independent` |
| Untrusted writes need **channel isolation** | MPBench (arXiv:2606.04329) | `classify_write_channel` / `source_isolation_gate` |
| Write-time filters miss **L2/L3** threats | MemPoison (arXiv:2607.14651) | `threat_tier_classify` / `dormant_trigger_scan` |
| Benign fragments can **collude** | Salami / MemCollusion (arXiv:2608.01637) | `compositional_coalition_scan` / `collusion_risk_gate` |
| Facts vs experience need **different persistence** | Knowledge layer (arXiv:2604.11364) | `classify_persistence_layer` / `knowledge_protect_scan` |
| Credentials must **never persist** | MAPLE Reject / PRISM-shaped | `credential_reject_gate` / `credential_store_scan` |
| Retrieval needs **uncertainty gating** | Oblivion Activator (arXiv:2604.00131) | `uncertainty_retrieve_gate` / `reasoning_reserve_plan` |
| Portable transfer needs **Merkle + capability scopes** | PAM deepen (arXiv:2605.11032) | `build_merkle_dag` / `issue_capability_token` / `selective_disclose` |
| Secrets must become **action handles**, not bearer keys | CapSeal (arXiv:2604.16762) | `issue_action_capability` / `capability_export_probe` |
| Trajectory safety needs **3D diagnosis**, not binary labels | AgentDoG (arXiv:2601.18491) | `diagnose_trajectory` / `safe_but_unreasonable_scan` |
| Long-horizon memory needs **tri-layer weave + dual channel** | MemWeaver (arXiv:2601.18204) | `build_hybrid_weave` / `dual_channel_retrieve` |
| Multi-hop association needs **explicit hop depth** | MemHop / ProGraph (arXiv:2607.19359) | `multi_hop_depth_score` |
| Memory architecture must **meta-evolve**, not stay static | MemEvolve (arXiv:2512.18746) | `diagnose_architecture` / `propose_architecture_variants` |
| Offline consolidation needs **dreaming + skill evolve** | MindMemOS (arXiv:2608.12428) | `dreaming_consolidate_plan` / `skill_evolve_plan` |
| Heterogeneous types need **functional boundaries** | MEMGUARD (arXiv:2605.28009) | `contamination_scan` / `type_route_retrieve` |
| Preferences drift — need **SW+EMA update**, not static prefs | PAMU (arXiv:2510.09720) | `preference_update_plan` / `preference_change_detect` |
| Production scale needs **category gates** (abstain, update, order) | BEAM benchmark | `abstention_gate` / `knowledge_update_check` / `event_order_check` |
| Hallucinations must be **localized by operation stage** | HaluMem (arXiv:2511.03506) | `localize_hallucination_stage` |
| Episodic recall needs **gists + temporal facts**, not flat RAG | REMem (arXiv:2602.13530) | `build_hybrid_episodic_graph` / `agentic_retrieve_plan` |
| Long-horizon OS needs **MemCell → MemScene → recollect** | EverMemOS (ACL 2026) | `form_memcell` / `consolidate_memscenes` / `reconstructive_recollect` |
| Long dialogue needs **STM/MTM/LPM + heat eviction** | MemoryOS (arXiv:2506.06326) | `heat_score` / `mtm_evict_plan` / `hierarchical_retrieve` |
| Distillation should admit **unpredictable** experience | NEMORI (ACL 2026) | `prediction_error_distill` / `deserves_memory_gate` |
| Facts ≠ beliefs — need **four networks + reflect** | Hindsight (arXiv:2512.12818) | `retain_plan` / `recall_multi_strategy` / `reflect_plan` |
| Agents must learn from **failures + successes** | ReasoningBank (arXiv:2509.25140) | `distill_strategy_item` / `failure_lesson_gate` / `matts_contrastive_plan` |
| Memory ops should be **evolvable skills**, not fixed | MemSkill (arXiv:2602.02474) | `select_skills` / `designer_evolve_plan` / `execute_skill_plan` |
| Managers need **ADD/UPDATE/DELETE/NOOP** discipline | Memory-R1 (arXiv:2508.19828) | `classify_memory_op` / `noop_gate` / `memory_op_plan` |
| MAS need **insight/query/interaction** hierarchy | G-Memory (arXiv:2506.07398) | `bidirectional_retrieve` / `hierarchy_update_plan` |
| Memory cycle needs **meta-guidance + in-situ probes** | MemMA (arXiv:2603.18718) | `meta_thinker_guidance` / `synthesize_probe_qa` / `repair_from_probes` |
| Agents need **reusable workflows** from success | AWM (arXiv:2409.07429) | `induce_workflow` / `retrieve_workflows` |
| Retrieval needs **query-level experience**, not answer dump | RRM (arXiv:2607.28156) | `query_level_guidance` / `isolate_factual_from_procedural` |
| Procedural memory must **distill · adapt · prune** | ReMe (arXiv:2512.10696) | `multi_faceted_distill` / `utility_prune_plan` |
| Test-time learning needs **curated cheatsheets**, not FH | Dynamic Cheatsheet (arXiv:2504.07952) | `extract_cheatsheet_snippet` / `compact_memory_gate` |
| Cross-task lessons need **insight operators** | ExpeL (arXiv:2308.10144) | `insight_op` / `retrieve_insights` |
| Long dialogue needs **prospective + retrospective** reflection | RMM (arXiv:2503.08026) | `prospective_reflect` / `retrieval_refine_plan` |
| Skills need **parallel many-to-one** consolidation | Trace2Skill (arXiv:2603.25158) | `parallel_patch_pool` / `hierarchical_merge_patches` |
| Streaming tasks need **search–predict–evolve** | Evo-Memory (arXiv:2511.20857) | `search_predict_evolve_check` / `exprag_retrieve` |
| Memory writes need **learned construction policy** | Mem-α (arXiv:2509.25911) | `memory_write_op` / `memalpha_reward_bundle` |
| Failed trajectories are **hindsight training gold** | AgentHER (arXiv:2603.21357) | `hindsight_relabel_plan` / `package_training_pair` |
| Plans need **pre-execution foresight** | PreFlect (arXiv:2602.07187) | `prospective_critique_plan` / `preflect_before_execute_gate` |
| Skill libraries need **flow-driven evolution** | SkillFlow (arXiv:2605.14089) | `skill_curation_decide` / `ttb_residual` |
| Experience needs **executable procedural Skills** | ProcMEM (arXiv:2602.01869) | `define_skill_triplet` / `ppo_gate_verify` |
| Retrieval must rank by **utility not just similarity** | MemRL (arXiv:2601.03192) | `two_phase_retrieve` / `utility_q_update` |
| Agents need a **closed experience lifecycle** | EvolveR (arXiv:2510.16079) | `distill_principle` / `lifecycle_phase_gate` |
| Self-evolution needs **question / navigate / attribute** | AgentEvolver (arXiv:2511.10395) | `self_question_task` / `attribute_step_credit` |
| Web skills need **API distillation + transfer** | SkillWeaver (arXiv:2504.07079) | `distill_skill_api` / `transfer_skill_gate` |
| Multi-skill tasks need **decompose–retrieve–compose + SAD** | SkillRoute (arXiv:2606.18051) | `sad_feedback_loop` / `compose_skill_dag` |
| Reasoning can self-improve with **zero external data** | Absolute Zero (arXiv:2505.03335) | `learnability_reward` / `propose_reasoning_task` |
| Curriculum needs **Challenger–Solver co-evolution** | R-Zero (arXiv:2508.05004) | `uncertainty_reward` / `curriculum_band_filter` |
| Long-horizon RL needs **source-indexed turn memory** | ECHO (arXiv:2606.31650) | `write_turn_memory` / `provenance_credit_mask` |
| Zero-data agents need **tool-aware curriculum↔executor** | Agent0 (arXiv:2511.16043) | `curriculum_reward` / `symbiotic_round_plan` |
| General domains need **Proposer–Solver–Judge** without env verifier | MAE (arXiv:2510.23595) | `mae_judge_score` / `mae_proposer_reward` |
| Verifiable domains need **plan + critic** against drift | SAGE (arXiv:2603.15255) | `sage_plan_steps` / `sage_drift_gate` |
| Memory should **interweave** with reasoning, not only retrieve | MemGen (arXiv:2509.24704) | `memory_trigger_decide` / `weave_latent_memory` |
| Experience needs **text + code** dual representation | Metis (arXiv:2606.24151) | `crystallize_plan_to_tool` / `dual_retrieve` |
| Reflections need **micro→meso→macro** failure synthesis | SAMULE (arXiv:2509.20562) | `intra_task_taxonomy` / `inter_task_transfer` |
| Streaming tasks need **online weight + forget** | LIVE-EVO (arXiv:2602.02369) | `update_experience_weight` / `forget_stale_experience` |
| Curriculum from **minimal seed** via Teacher/Solver/Generator | Socratic-Zero (arXiv:2509.24726) | `socratic_teacher_craft` / `socratic_generator_distill` |
| Zero-sum **self-play + RAE** transfers reasoning | SPIRAL (arXiv:2506.24119) | `spiral_rae_advantage` / `spiral_transfer_pattern` |
| Tools + experience need **procedural/semantic/episodic** hub | SMITH (arXiv:2512.11303) | `smith_create_tool` / `smith_retrieve_episode` |
| Long-term QA needs **tree+graph hybrid** evolution | H-Mem (arXiv:2605.15701) | `hmem_consolidate_nodes` / `hmem_hybrid_retrieve` |

**One-line synthesis:** Stele v7.5 = **SMITH tool hub + H-Mem hybrid memory + Socratic/SPIRAL + prior governance stack**.


---

## 1. MemoryArena — action-coupled evaluation (FF-5 hardened)

**Paper:** He et al., *MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks*, arXiv:2602.16313 (2026-02).  
**Site:** https://memoryarena.github.io/

**Claim (verified from abstract / project page):** Existing evals isolate memorization *or* single-session acting. MemoryArena couples them: agents must distill experience in early sessions and use it in later interdependent subtasks (web shopping, preference-constrained travel, progressive search, sequential formal reasoning). ~766 tasks; long horizons (~57 action steps average). Systems near-saturated on LoCoMo-class recall **perform poorly** in this agentic setting.

**Design rules for Stele v1:**

1. Product success = **task lift** (`compare_with_without`, env-gate, foreign-pack transfer, MemoryArena-shaped smoke) — not recall@k alone.
2. Distill-on-write (Insight body) is mandatory; raw trajectory dumps are negative-transfer risk (aligns FF-2 / FF-4).
3. Do not advertise LoCoMo / LongMemEval scores as Stele’s primary marketing metric.

---

## 2. Mechanisms survey — write / manage / read (FF-1 + OP-4)

**Paper:** *Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers*, arXiv:2603.07670 (2026).

**Claim:** Landscape shifted toward learned memory control and agentic benchmarks (MemBench, MemoryAgentBench, MemoryArena, A-MEM). Classic lineage still holds:

| System | Mechanism | Risk called out |
|---|---|---|
| Reflexion | Verbal post-mortems → next episode | Over-generalization / self-reinforcing error |
| ExpeL | Success/failure → reusable “rules of thumb” | Needs discriminative extraction, not dump |
| Generative Agents | Recency × relevance × importance | Multi-signal retrieval still influential |
| Think-in-Memory | Recall then dedicated think step | Retrieval ≠ reasoning |

**Design rules:**

1. **Quality gates** (confidence, contradiction, expiry) are underdeveloped industry-wide — Stele’s quarantine / contested / stale_report fill that gap.
2. Reflection that grades itself must never promote (OP-2 / C7).
3. Stele stays on the *manage* plane: schema + governance + retrieval contract — not another extraction LLM in the write path (intent R4).

---

## 3. Governed Memory — production governance architecture (OP-governance)

**Paper:** *Governed Memory: A Production Architecture for Multi-Agent Workflows*, arXiv:2603.17787 (2026-03).  
**Code note:** authors point to https://github.com/personizeai/governed-memory

**Claim:** Five structural failures in enterprise multi-agent deploy: memory silos; governance fragmentation; unstructured memories; redundant context; silent quality degradation. Architecture: dual memory (atomic facts + schema-typed properties); tiered governance routing; reflection-bounded / entity-scoped retrieval; schema lifecycle. Reported: high fact recall, governance routing precision, zero cross-entity leakage on adversarial queries, LoCoMo accuracy without retrieval penalty from governance.

**Contrast with Stele (intentional):**

| Governed Memory (paper) | Stele |
|---|---|
| Dual unstructured + typed properties | Distilled experiential layers (goal/issue/decision/…) |
| Policy routing into context | Quarantine → oracle promote; contested surface |
| Entity-scoped isolation | subject_id + scope rungs + DELETE erase |
| Often LLM-assisted schema lifecycle | Zero LLM on core write path |

**Design rules:** Shared governed memory is a **real production category**. Stele’s OSS bet is the *protocol* (inspectable SoT, evidence contract, pack portability) rather than a hosted enterprise stack. Do not dilute C5 to chase dual-modality extractors.

---

## 4. memorywire — portability protocol (OP-6 / C1 / C3)

**Paper:** *memorywire: A Vendor-Neutral Wire Format for Agent Memory Operations*, arXiv:2606.01138 (2026).  
**Spec:** five ops (`remember`, `recall`, `forget`, `merge`, `expire`) × four types (semantic, episodic, procedural, emotional); JSON Schema 2020-12; optional HITL governance channel; RRF router across backends.

**Claim:** Storage is saturated; missing layer is **interop + human review before long-term commit**. Provenance is argued as the strongest lever for recovering a poisoned store.

**Design rules for Stele v1:**

1. Publish **Stele entry JSON Schema** as a first-class artifact (machine contract).
2. Provide a **projection** helper to memorywire-shaped `remember` / `recall` payloads — Stele remains the governed SoT, not a competing backend SDK.
3. Keep HITL / evidence promotion — aligned with memorywire’s governance channel thesis.
4. Never require memorywire as a runtime dependency (C1 purity).

---

## 5. LongMemEval — abstention, updates, temporal (FF-8)

**Paper:** Wu et al., *LongMemEval*, arXiv:2410.10813 · ICLR 2025.  
**Site:** https://xiaowu0162.github.io/long-mem-eval/

**Claim:** Five abilities: extraction, multi-session reasoning, temporal reasoning, knowledge updates, **abstention**. Commercial / long-context systems drop sharply on sustained histories; “I don’t know” is a scored ability.

**Design rules:** Empty search, `stale_policy=withhold`, supersede (not overwrite), and explicit historical `as_of` flags are product features — not edge cases.

---

## 6. A-MEM — agentic linking (FF-graph)

**Paper:** Xu et al., *A-MEM: Agentic Memory for LLM Agents*, arXiv:2502.12110 (2025).

**Claim:** Zettelkasten-style notes with link generation and memory evolution improve multi-hop QA while cutting tokens vs dumping history.

**Design rules:** `LINK`, `related`, `follow_link_depth`, REFLECT dangling-link reports are v1 capabilities. Evolution that *rewrites* history without provenance is forbidden — Stele evolves via supersede + contested, not silent mutate.

---

## 7. What this pass does *not* support

- Pack willingness-to-pay / SKU pricing literature (still open; OP-12).
- That governance always improves LoCoMo — Governed Memory reports no penalty; that is *their* stack, not a Stele claim.
- That MemoryArena leaderboard status is required for Stele v1 ship — Stele ships **shaped** harnesses + intent joint tests; full gym integration is post-v1 research engineering.

---

## 8. Audit log

| Date | Action |
|---|---|
| 2026-08-20 | Initial frontiers pass: MemoryArena, survey 2603.07670, Governed Memory 2603.17787, memorywire 2606.01138, LongMemEval, A-MEM — all via arXiv/project primary pages |
| 2026-08-20 | v1.1 pass: MemBench (arXiv:2506.21605 / ACL 2025); PurgeBench provenance recovery via memorywire paper; Write/Select/Compress/Isolate field synthesis |
| 2026-08-20 | v1.2 pass: MemArchitect (arXiv:2603.18330); SSGM (arXiv:2603.11768); governance-metric framing (survey Layer-4 / MOA) |
| 2026-08-20 | v1.3 pass: GateMem (arXiv:2606.18829); Governed Shared Memory (arXiv:2606.24535); Agent-Native Memory (arXiv:2606.24775) |
| 2026-08-20 | v1.4 pass: TOKI (arXiv:2606.06240); StateFuse (arXiv:2607.05844); MemoryAgentBench (arXiv:2507.05257) |
| 2026-08-20 | v1.5 pass: MIND (arXiv:2607.28103); MAPLE-Guard (arXiv:2608.00426) |
| 2026-08-20 | v1.6 pass: MemMark (arXiv:2605.25002); TRACE (arXiv:2607.08400) |

---

## 9. MemBench — capacity & efficiency (v1.1)

**Paper:** Tan et al., *MemBench*, ACL 2025 Findings · arXiv:2506.21605.

**Claim:** Eval must cover factual vs reflective memory, participation vs observation, and metrics beyond accuracy — including **capacity** and **temporal efficiency**. At ~100k tokens, simple retrieval often beats complex memory managers on accuracy while staying faster to write.

**Stele implication:** Keep hybrid BM25 (+ optional embedder) as default Select. Ship `membench_shaped_report` as a **local CI proxy** (capacity + search ms + task lift) — never claim MemBench leaderboard scores without running the gym.

---

## 10. Provenance recovery (v1.1)

**Paper:** memorywire arXiv:2606.01138 (+ PurgeBench companion).

**Claim:** After a store is poisoned, **forget-by-untrusted-provenance** is the strongest measured recovery lever (RC ≈ 0.64 on PurgeBench). Content-anomaly detectors alone fail on semantic poison. Entangled directives inside trusted sources defeat automatic purge — quarantine for human review.

**Stele implication:** `purge_by_provenance(dry_run|execute)` + `trusted_sources` Select filter. Entangled cases remain contested / human — do not invent auto-delete.

---

## 11. MemArchitect — policy governance vs zombie memories (v1.2)

**Paper:** *MemArchitect: A Policy Driven Memory Governance Layer*, arXiv:2603.18330 (2026).

**Claim:** Standard RAG treats memory as a passive bucket. The “Governance Gap” is missing lifecycle hygiene, consistency adjudication, provenance/trust, and efficiency/safety policies. Unmanaged stores accumulate **zombie memories** (outdated / unused facts that still pollute context). The proposed middleware uses explicit rule-based policies (decay, privacy, triage) between storage and the agent context window.

**Design rules for Stele:**

1. Ship **report-only** hygiene candidates (`hygiene_candidates`) for unused / net-harmful / stale-promoted entries — operators decide; Stele does not auto-prune on heuristics (aligns C7 / PurgeBench entangled caution).
2. Keep quarantine → oracle promote as the truth gate; MemArchitect’s “triage & bid” is a *Select* policy family, not a license for LLM write-path extraction.
3. Do not claim MemArchitect benchmark numbers; Stele’s product proof remains task lift + governance integrity.

---

## 12. SSGM — stability, safety, read filtering (v1.2)

**Paper:** *Governing Evolving Memory in LLM Agents… (SSGM)*, arXiv:2603.11768 (2026).

**Claim:** Dynamic memory evolution risks semantic drift, topology-induced leakage, and temporal obsolescence. SSGM decouples consolidation from execution: consistency checks, temporal decay, and access control **before** long-term commit; a **read filtering gate** uses provenance trust + decay (e.g. Weibull-style relevance) so stale/untrusted units never reach context.

**Design rules for Stele:**

1. `search(..., prefer_fresh=True)` soft-ranks by `last_verified` (decay proxy) — never silently mutates SoT.
2. `trusted_sources` + purge provenance remain the hard trust levers; decay is ranking, not deletion.
3. Entangled poison after purge → `entangled_suspects` human-review queue (LINK neighborhood of purged/untrusted seeds that still have trusted provenance).

---

## 13. Governance metrics (shaped harness, v1.2)

**Sources:** Survey arXiv:2603.07670 (Layer 4 — privacy leakage, deletion compliance, access-scope); Memory Ownership Architecture / MGB framing (Zenodo 2026 — proposed governance benchmark categories; empirical stack not required for Stele).

**Claim:** Recall-only evals miss whether a system can **forget**, isolate, and prove integrity. Governance-shaped local proxies (doctor ok, contested open, purge dry-run hit rate, hygiene queue size, subject erasure) are the honest OSS CI surface until a public MGB suite exists.

**Stele implication:** `governance_shaped_report` — local proxies only; never advertise as Memory Governance Benchmark scores.

---

## 14. GateMem — multi-principal utility / ACL / forgetting (v1.3)

**Paper:** Ren et al., *GateMem: Benchmarking Memory Governance in Multi-Principal Shared-Memory Agents*, arXiv:2606.18829 (2026).  
**Artifacts:** https://github.com/rzhub/GateMem

**Claim:** Single-user memory benchmarks miss shared institutional assistants (medical/office/education/household). GateMem jointly scores **utility**, **access control**, and **active forgetting** after deletion. Across baselines, **no method wins all three**; long-context often governs best at high token cost; retrieval/external memory still leaks unauthorized or deleted content.

**Design rules for Stele:**

1. `search(..., principal_scopes=[...])` — explicit scope allowlist for the requesting principal; **no implicit universal** when set (ACL dimension).
2. `forget_compliance(...)` — post-DELETE probe: store clear + SEARCH must not resurface forbidden ids/substrings (forgetting dimension).
3. `gatemem_shaped_report` — local CI proxies for the three axes; never claim GateMem MGS / leaderboard.

---

## 15. Governed shared memory / MemClaw (v1.3)

**Paper:** *Governed Shared Memory for Multi-Agent LLM Systems*, arXiv:2606.24535 (2026).

**Claim:** Fleet memory fails as unauthorized leakage, stale propagation, contradiction persistence, and provenance collapse. Provenance reconstruction is the cleanest positive result in their production measurement; scope enforcement bugs appear when API paths are asymmetric.

**Design rules:** Keep journal + `timeline` as provenance reconstruction; contested/supersede for contradictions; never allow GET-by-id style bypass of Select filters in the protocol surface (MCP tools must honor the same filters as library SEARCH).

---

## 16. Agent-native memory systems study (v1.3)

**Paper:** *Are We Ready For An Agent-Native Memory System?*, arXiv:2606.24775 (2026).

**Claim:** Across 12 systems × 5 workloads, **no architecture dominates**; effectiveness tracks bottleneck alignment. Localized maintenance beats global reorganization on cost.

**Design rules:** Stele stays a thin governed protocol (not a mega-manager); hybrid lexical Select default; REFLECT/hygiene are local ops — do not add global LLM rewrite passes on the core path.

---

## 17. TOKI — bitemporal contradiction contract (v1.4)

**Paper:** *TOKI: A Bitemporal Operator Algebra for Contradiction Resolution…*, arXiv:2606.06240 (2026).

**Claim:** Contradiction resolution is write-time concurrency control. Production heuristics (LWW, evidence-weighted merge, await-confirmation, per-rule policy) admit anomalies: **replay inconsistency**, **belief-drift skew**, **audit erasure**. Every audited baseline with an LLM judge on the write path fails ≥1 anomaly; Toki’s dual-row schema keeps the losing fact in an audit row.

**Design rules for Stele:**

1. Keep the **oracle/judge off the write path** (C5/C7) — quarantine + external evidence only.
2. `supersede` / contested resolve **must retain the loser on disk** + journal SUPERSEDE.
3. `lineage(entry_id)` reconstructs supersede chain + journal (TOKI audit defence).
4. `belief_at(as_of)` is the bi-temporal read; live SEARCH excludes superseded unless `as_of` is set.

---

## 18. StateFuse — conflict-preserving surfaces (v1.4)

**Paper:** *StateFuse: Deterministic Conflict-Preserving Memory for Multi-Agent Systems*, arXiv:2607.05844 (2026).

**Claim:** On conflict-bearing MemoryAgentBench slices, accuracy ties across surfaces; the real gain is **exposing contradictions** so agents can abstain. Collapsed latest-write surfaces hide conflicts and raise false-confident actions.

**Design rules:** `conflict_surface()` returns contested pairs with both sides; never auto-collapse (R2). Resolve only via evidenced `resolve_contested`.

---

## 19. MemoryAgentBench — four competencies (v1.4)

**Paper:** *Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions*, arXiv:2507.05257 (2025) — MemoryAgentBench.

**Claim:** Unified eval across **accurate retrieval**, **test-time learning**, **long-range understanding**, **selective forgetting** (EventQA / FactConsolidation additions).

**Stele implication:** `memoryagent_shaped_report` local proxies covering those four + lineage audit — never claim MemoryAgentBench leaderboard scores.

---

## 20. MIND — lightweight injection defense (v1.5)

**Paper:** *MIND: Lightweight… Memory Injection Defense… via Intent-Aware Information Bottleneck*, arXiv:2607.28103 (2026).

**Claim:** Memory injection diverts agents from user intent. Heavy LLM auditors are costly; MIND uses an intent-aware information bottleneck + lightweight detector and cuts attack success ~55% on ReAct-StrategyQA without accuracy/latency loss.

**Design rules for Stele:** Ship a **deterministic marker scan** (`injection_scan`) as the OSS-safe lightweight detector — no neural IB, no LLM on the write path (C5). Neural/IB detectors stay optional caller-side.

---

## 21. MAPLE-Guard — memory-link lifecycle gates (v1.5)

**Paper:** *MAPLE-Guard: Memory-Aware Link Enforcement Against Memory-Link Poisoning…*, arXiv:2608.00426 (2026).

**Claim:** Poison written once can be retrieved, promoted into shared memory, and reused across agents. Defenses on prompts/edges miss this. Gates at **write, retrieval, promotion, cross-agent reuse** cut ASR sharply on LongMemEval / AppWorld while raising multi-agent success.

**Design rules for Stele:**

1. **Write** — ADD always quarantines (already C7).
2. **Retrieve** — `search(..., withhold_injection_suspects=True)`.
3. **Promote** — `promote(..., block_injection_suspects=True)`.
4. **Reuse** — pack export redaction + `verify_pack` (existing); `maple_shaped_report` probes the four gates.
5. **Compress** — `select_budget_plan` exposes fitted vs overflow under a token budget (OP-9).

---

## 22. MemMark — snapshot attribution for memory evolution (v1.6)

**Paper:** *MemMark: State-Evolution Attribution Watermarking for Agent Long-Term Memory Systems*, arXiv:2605.25002 (2026).

**Claim:** When adversaries control snapshots and external traces are lost, attribution must live in reproducible memory-evolution evidence. MemMark embeds marks in update/link/realization choices with keyed samplers and supports R1 full-log / R2 partial / R3 snapshot-only verification.

**Design rules for Stele:** Do **not** put a keyed sampler on the write path (C5). Ship deterministic **content digests + store seals + attribution receipts** as the OSS R3-shaped attestation surface (`store_seal`, `verify_seal`, `attribution_receipt`). Keyed behavioral watermarks remain out of scope for core.

---

## 23. TRACE — two-channel trajectory provenance (v1.6)

**Paper:** *TRACE: A Two-Channel Robust Attribution Watermark…*, arXiv:2607.08400 (2026).

**Claim:** Reseller-controlled trajectory logs need watermarks that survive **deletion** (content-keyed selection channel) and **rewriting** (skeleton-keyed tally channel).

**Design rules:** Stele’s append-only journal + content digests are the inspectable provenance substrate. `replay_consistency` soft-checks journal↔SoT. Full TRACE behavioral watermarking is agent-runtime territory — not Stele-core.

---

## 24. AMV-L — lifecycle eligibility tiers (v1.7)

**Paper:** *AMV-L: Lifecycle-Managed Agent Memory for Tail-Latency Control…*, arXiv:2603.04443 (2026).

**Claim:** TTL and LRU are value-agnostic. AMV-L bounds retrieval eligibility via **HOT/WARM/COLD tiers** driven by utility metadata, cutting extreme-tail latency while preserving high-value long-lived items.

**Design rules for Stele:** Ship deterministic `lifecycle_tier` + `lifecycle_inventory` + `search(..., lifecycle_tiers=)` filters. No separate vector indexes per tier — filter after hybrid retrieval (candidate-ID scoping). Never claim AMV-L latency numbers from local proxies.

---

## 25. TEPA — revocable keyed precedents (v1.7)

**Paper:** *TEPA: Revoking Stale Memories for Conflict-Robust Language Agents*, arXiv:2608.07429 (2026).

**Claim:** Memory pollution = active stale memories that newer conflicting evidence superseded. TEPA makes **validity an explicit state**: revoke active precedents under a conflict key while preserving archive for audit. Append-only and LWW collapse under full reversal; TEPA does not.

**Design rules for Stele:**

1. Optional `conflict_key` on entries.
2. New state `revoked` (not DELETE) via evidenced `revoke_by_key` / `unrevoke`.
3. Live SEARCH excludes `revoked`; `belief_at` / lineage retain audit.
4. Do **not** auto-revoke on semantic conflict — evidence + operator/agent call required (C7).

---

## 26. Pack attestation (v1.7)

**Claim (product):** Store seals cover the live SoT; exported packs need an independent tamper-evident seal so receivers can verify redacted bundles without the source journal.

**Design rules:** `pack_seal` / `verify_pack_seal` over manifest + entry digests. Complements `verify_pack` (secrets/stamps) — does not replace it.

---

## 27. MELD — federation merge without silent rewrite (v1.8)

**Paper:** *MELD: A Protocol for Merging Knowledge Across Distributed Agentic Memories*, arXiv:2608.16357 (2026).

**Claim:** Agents can call tools across a mesh but cannot reconcile memory: no protocol for insert/merge/relate/conflict/reject. MELD admits every claim through a five-outcome procedure; contradictions are preserved, never silently resolved. Status CRDT beats LWW under partitions.

**Design rules for Stele:** Ship deterministic `merge_classify` using conflict_key + title Jaccard + contested/revoked — **report-only**. No NLI/embeddings on the core path (C5). Full pub/sub CRDT transport stays out of scope.

---

## 28. MAP-Graph — provenance as Select control (v1.8)

**Paper:** *MAP-Graph: Provenance-Aware Shared Memory for Multi-Agent Workflows*, arXiv:2608.10509 (2026).

**Claim:** Semantic retrieval alone admits unauthorized / poisoned / revoked ancestry. MAP-Graph filters by permission, then multiplies path trust, then risk-gates actions while retaining lineage.

**Design rules:** `path_trust` along LINK ancestry; `search(..., min_path_trust=)`; revoke/contest edges degrade trust. Never delete descendants silently — blast radius for ops first.

---

## 29. RippleMem — associative neighborhood (v1.8)

**Paper:** *RippleMem: From Isolated Retrieval to Associative Recollection…*, arXiv:2608.13334 (2026).

**Claim:** Isolated top-k retrieval misses support reachable by associative graph expansion. RippleMem expands typed channels within hop bounds and consolidates provenance.

**Design rules:** `blast_radius` over undirected `LINK kind=entry` within max_depth 1–5. LLM-guided pruning stays caller-side; core stays hop-bounded and deterministic.

---

## 30. GPM — governed persistent journal chain (v1.9)

**Paper:** *Governed Persistent Memory…*, arXiv:2608.12476 (2026).

**Claim:** Retrieval does not decide whether contradictory/superseded/deleted records may support claims. GPM uses source-bound state transitions and hash-chained ledgers with fail-closed release.

**Design rules:** New journal rows carry `prev_hash`/`row_hash`. `verify_journal_chain` is fail-closed for chained rows; legacy unchained rows soft-accepted. Not distributed consensus.

---

## 31. SYNAPSE — spreading activation (v1.9)

**Paper:** *SYNAPSE: … Spreading Activation*, ACL 2026 Findings.

**Claim:** Static vector similarity fails on disconnected long-term memory. Spreading activation with lateral inhibition and temporal decay surfaces relevant sub-graphs.

**Design rules:** `spread_activate(seed_ids)` along entry LINKs with hop decay + soft lateral inhibition. No embedding model required in core.

---

## 32. SodaMem — connection-density fusion (v1.9)

**Paper:** *SodaMem: Evidence-Grounded Temporal Graph Memory…*, arXiv:2608.08055 (2026).

**Claim:** Single-channel retrieval is brittle; rank by connection density across auditable links, not cosine alone.

**Design rules:** `connection_density` + `search(..., prefer_dense=True)` soft re-rank. Dense tunnels remain optional caller embedders.

---

## 33. Oblivion — decay-driven retention (v1.9)

**Paper:** *Oblivion: Self-Adaptive Agentic Memory Control through Decay-Driven Activation*, arXiv:2604.00131 (2026).

**Claim:** Always-on flat retrieval causes interference; Ebbinghaus-inspired retention should gate accessibility while reinforcing used memories.

**Design rules:** `retention_score` from last_verified half-life + helpful/pin boosts; `min_retention` Select filter. Never auto-delete on decay alone.

---

## 34. GPM fail-closed release (v2.0)

**Paper:** *Governed Persistent Memory…*, arXiv:2608.12476 (2026) — release clauses.

**Claim:** Structured release is permitted only if the verified head remains stable while the decision is formed; mismatch fails closed with no record. Barriers include conflict isolation and non-revival after retraction.

**Design rules:** `health_report` surfaces barriers; `release_gate` re-reads head (drift → abstain); `export(require_release=True)` refuses unhealthy packs.

---

## 35. Storage is not memory — derived indexes (v2.0)

**Paper:** *Storage Is Not Memory…*, arXiv:2605.04897 (2026); SLM 4.0 local SQLite practice.

**Claim:** A retrieval-centered architecture may use SQLite FTS as a projection; the event/file substrate remains authoritative.

**Design rules:** `rebuild_sqlite_index` / `search_sqlite` are optional derived FTS5 (stdlib). Delete anytime; files + journal remain SoT (C4). Never promote SQLite to truth.

---

## 36. GPM decision receipts (v2.1)

**Paper:** *Governed Persistent Memory…*, arXiv:2608.12476 (2026) — local decision record.

**Claim:** A released structured answer binds claim identifiers, policy/normalizer versions, query context, and the verified head. Head drift during formation fails closed with **no** record.

**Design rules:** `release_gate(..., issue_receipt=True)` writes `decisions/dr_*.json` only on success; abstain records require explicit `record_abstain`. Receipts are local integrity digests — not transferable TEE/CAVA attestation.

---

## 37. Portable Agent Memory import verify (v2.1)

**Paper:** *Portable Agent Memory…*, arXiv:2605.11032 (2026).

**Claim:** Import verifies artifact integrity and halts on first failure before re-hydration.

**Design rules:** `verify_import` runs structure → injection → entry_count → policy → optional seal. `hydrate(require_verify=True)` refuses until ok. Export stamps `policy_digest`.

---

## 38. MemLineage trust labels (v2.1)

**Paper:** *MemLineage…*, arXiv:2605.14421 (2026).

**Claim:** Trust propagates over memory lineage; deployments may fail closed when ancestry is untrusted.

**Design rules:** `lineage_trust` labels Trusted / Derived-Untrusted / Untrusted from contested/revoked/quarantine ancestors via entry LINKs. `refuse_untrusted_lineage` drops non-Trusted hits. Deterministic only — no LLM attribution judge.

---

## 39. Proof-of-Execution Memory (v2.2)

**Paper:** *Proof-of-Execution Memory…*, arXiv:2608.16032 (2026).

**Claim:** Forged-reasoning attacks plant memory notes claiming a safety step already ran. Wording filters fail under rewording. Defense: verify against an independent append-only execution ledger that only trusted code writes — never inspect the memory body.

**Design rules:** `executions.ndjson` hash chain via `record_execution`. `verify_execution` allows skip only on subject+step match. Cross-subject replay fails closed. Optional HMAC is caller-side (core stays unkeyed stdlib digests).

---

## 40. Provenance non-amplification firewall (v2.2)

**Paper:** *Memory Provenance Laundering…* / PPMF, arXiv:2607.29167 (2026).

**Claim:** Consolidation can rewrite untrusted observations as apparent user history, erasing low-trust source while keeping action triggers. Firewall matches action risk to platform-maintained provenance authority.

**Design rules:** `authority_gate` scores provenance (pack-hydrate / pack: capped; ci:/oracle: boosted). Critical actions require high authority. No LLM body trust.

---

## 41. Exact claim closure (v2.2)

**Paper:** GPM release clauses, arXiv:2608.12476 (2026).

**Claim:** Every released structured claim must match an assertable fact in the fresh public view with source fact identifiers at one verified head.

**Design rules:** `claim_closure(claim_ids)` requires promoted state for each ID; `expected_head` mismatch fails closed. Not free-text entailment.

---

## 42. MemoRepair barrier-first cascade (v2.3)

**Paper:** *MEMOREPAIR: Barrier-First Cascade Repair…*, arXiv:2605.07242 (2026).

**Claim:** After deletion/correction/migration, descendants can remain visible with stale support. Contract: withdraw affected cascade first, then select predecessor-closed successors under a repair–cost tradeoff (exact via s–t min-cut in the paper).

**Design rules:** `cascade_impact` / `cascade_exposure` measure promoted exposure; `withdraw_cascade` barrier-revokes fault+depends-on descendants; `repair_plan` is a **greedy predecessor-closure proxy** (not exact min-cut — documented). Republish remains evidenced promote by caller.

---

## 43. Non-revival after withdraw (v2.3)

**Paper:** GPM non-revival clauses (arXiv:2608.12476) + MemoRepair withdraw semantics.

**Claim:** Retracted/deleted records must not support ordinary retrieval after barrier.

**Design rules:** `non_revival_probe` asserts forbidden IDs absent from SEARCH hits; ordinary Select already excludes `revoked`.

---

## 44. MemIR typed roles (v2.4)

**Paper:** *Mitigating Provenance-Role Collapse…* (MEMIR), arXiv:2605.25869 (2026).

**Claim:** Unstructured flat text induces source-monitoring errors: evidence and truth-bearing claims collapse. Typed IR separates raw evidence, cues, and authorized claims.

**Design rules:** Optional `memory_role` ∈ {evidence, claim, decision}; `fact_interface` builds authorize_ids from claims+decisions only; `claim_closure(require_claim_role=True)` refuses evidence-role IDs; `role_collapse_scan` reports suspects.

---

## 45. D-Mem dual-process Select (v2.4)

**Paper:** *D-Mem: A Dual-Process Memory System…*, arXiv:2603.18631 (2026).

**Claim:** Lightweight routine retrieval plus gated Full Deliberation fallback under a multi-dimensional quality gate.

**Design rules:** `dual_channel_search` runs claims-only routine first; `quality_gate` escalates to include_contested deliberation on insufficient claims / contested / injection flags. No LLM judge on the gate.

---

## 46. GitOfThoughts commit substrate (v2.5)

**Paper:** *GitOfThoughts…*, arXiv:2606.14470 (2026).

**Claim:** Reasoning is ephemeral unless version-controlled. Git-as-substrate wins on auditability, provenance, and mergeability at accuracy parity — not because memory formats beat each other on novel problems.

**Design rules:** Stdlib `commits.ndjson` + `refs/` + `tags/` (no git binary required). `commit_view` binds entry ids + journal head; `checkout_view` / `diff_commits` / `merge_branches` for ops. Optional real-git export remains caller-side.

---

## 47. Copyability threshold (v2.5)

**Paper:** GitOfThoughts copyability boundary (τ≈0.8).

**Claim:** Memory helps accuracy mainly when the retrieved case is a near-duplicate; below threshold, expect no accuracy gain (answer retrieval, not method transfer).

**Design rules:** `copyability_gate` uses Jaccard token overlap; `memory_likely_helps` is honest about the boundary — never claim method transfer.

---

## 48. ChronoMem global version + counterfactual Select (v2.6)

**Paper:** *ChronoMem: Version Control and Semantic Rollback for Large Language Model Agent Memory*, arXiv:2607.27773 (2026).

**Claim:** Forward-only memory cannot recover after exposure to bad updates. Whole-memory version pins + rollback must support **post-exposure counterfactual** reads — answer as if later updates never occurred — without mutating SoT entry files.

**Design rules:** `pin_memory_version` commits promoted id set as a tagged view; `activate_version` / `refs/read_head` scopes Select; `counterfactual_search` uses `_version_select` (loads pinned ids even if later superseded). NL→version mapping stays caller-side (core is id/hash rollback). Proxies only — not ChronoMem ADK scores.

---

## 49. MemStrata deterministic supersession (v2.6)

**Paper:** *Temporal Validity in Retrieval Memory…* (MemStrata), arXiv:2606.26511 (2026).

**Claim:** Embedding similarity cannot distinguish stale vs current facts (AUROC ~chance). Stale-fact errors are structural for flat RAG. Fix: deterministic supersession at write time + current-fact Select — no similarity threshold, no LLM on the read path.

**Design rules:** Existing `conflict_key` + `supersede` close validity; `supersession_winners` / `exclude_superseded` hide non-winners; `stale_fact_scan` reports promoted-but-not-current exposure. Proxies only — not MemStrata evolving-benchmark accuracy claims.

---

## 50. TARL five-action updates (v2.7)

**Paper:** *TARL: Transaction-Aware Reliable Ledgers…*, arXiv:2608.03699 (2026).

**Claim:** Binary Write/Hold cannot distinguish append vs revise vs reject vs defer vs ignore — same label, different memory states. Five executable actions + accepted/pending/rejected ledgers reduce pollution while preserving conflict evidence.

**Design rules:** Deterministic `propose_update` / `apply_update` map to `append|noop|revise|reject_conflict|defer_verify` via conflict_key, body digest, authority scores, injection markers (no LLM). `ledger_view` projects Stele states. Proxies only — not TARL-Mem accuracy.

---

## 51. Memory Worth forget signal (v2.7)

**Paper:** *When to Forget: A Memory Governance Primitive* (Memory Worth), arXiv:2604.12007 (2026).

**Claim:** Static write-time importance fails as task distribution shifts. Two outcome counters (success/fail co-occurrence) yield MW → suppress/deprecate without causal claims.

**Design rules:** MW = `helpful/(helpful+harmful)` from existing `usage` counters; `memory_worth` / `low_worth_scan` / Select `min_worth`. Explicitly associational — never claim causation. Proxies only — not paper Spearman ρ.

---

## 52. MemTX transactional belief commit (v2.8)

**Paper:** *MemTX: Transactional Belief Commit for Stateful Agent Memory*, arXiv:2607.23929 (2026).

**Claim:** Treating every accepted write as immediately actionable truth drives irreversible tool harm. Write ≠ commit. Stage → validate → commit; gate actions on action-safe maturity; abort/cascade when beliefs retract.

**Design rules:** `begin_transaction` / `stage_write` (tentative quarantine) / `validate_transaction` / `commit_transaction` (promote) / `abort_transaction`. `action_safe_gate` fails closed on tentative or in-flight conflict_key overlap. Proxies only — not MemTX backbone scores.

---

## 53. Always-On AOEP obligation coverage (v2.8)

**Paper:** *Always-On Agents: A Survey of Persistent Memory, State, and Governance…*, arXiv:2606.30306 (2026) — AOEP-v0.

**Claim:** Literature over-indexes retrieve/write vs govern/recover. Evaluation should score state mutation and recovery obligations, not answer quality alone.

**Design rules:** `aoep_report` checklist over shipped surfaces (tx commit, action gate, cascade withdraw, version rollback, worth/forget). Local coverage proxy — not AOEP corpus scoring.

---

## 54. LatticeMind symbolic conflict + budgeted render (v2.9)

**Paper:** *LatticeMind: A Conflict-Aware Memory Primitive for Multi-Agent Systems*, arXiv:2608.08236 (2026).

**Claim:** Contradiction handling belongs in memory, not answer-selection. Cheap symbolic checks first; LLM reconcile only when needed. Credibility (one wins) vs coordination (coexist). Budgeted compact render stresses external memory under char limits.

**Design rules:** Deterministic `symbolic_conflict_scan` (duplicate promoted keys, LINK triangles) + `classify_conflict` + `compact_render(reader_budget≈1400)`. No LLM reconciler on core (C5). Proxies only — not ConflictBank scores.

---

## 55. Cordon effect outbox (v2.9)

**Paper:** *Cordon: Semantic Transactions for Tool-Using LLM Agents*, arXiv:2606.17573 (2026).

**Claim:** Local belief promotion must not auto-release irreversible external effects. Commit manifest separates local promote from effect outbox release; dispatched effects need compensate, not silent resend.

**Design rules:** `stage_effect` → `pending`; `release_effects` → `ready`; `mark_effect_dispatched` / `cancel_effect` / `compensate_effect`. Stele never calls external sinks. Proxies only.

---

## 56. STALE three-dimension probes + VTA (v3.0)

**Papers:** *STALE…*, arXiv:2605.06527 (2026); *When Memory Updates but Behavior Does Not* (VTA), arXiv:2608.01619 (2026).

**Claim:** Implicit conflict leaves systems retrieving updated evidence yet failing Implicit Policy Adaptation. Need State Resolution, Premise Resistance, and provenance-verified transitions (chronology — not semantic truth).

**Design rules:** Deterministic `state_resolution` / `premise_resistance` / `ipa_gap_scan` / `verify_transition` / `related_slot_scan` (domain:slot from conflict_key). No NLI on core. Proxies only — not STALE/VTA benchmark scores.

---

## 57. GEM state-operator correctness (v3.0)

**Paper:** *Is Agent Memory a Database?…* (GEM / MemState), arXiv:2605.26252 (2026).

**Claim:** Long-term memory correctness is a property of the state trajectory (ingestion, revision, forgetting, retrieval) — not of individual records.

**Design rules:** `gem_report` checklist over six conditions mapped to shipped Stele surfaces. Local obligation coverage — not a native GEM engine.

---

## 58. StateFuse projection authority deepen (v3.1)

**Paper:** *StateFuse: Deterministic Conflict-Preserving Memory…*, arXiv:2607.05844 (2026).

**Claim:** Resolvers operate only at projection time. They may select among surfaced candidates or abstain, but cannot rewrite replicated state. Dual correction handles (claim_id / claim_ref) matter when exact prior IDs are unavailable.

**Design rules:** `project_resolve` abstains on contested/symmetric; `pin_projection` is overlay-only; `correction_handle` exact + semantic. Proxies only — not MemoryAgentBench scores.

---

## 59. TOKI operator contract deepen (v3.1)

**Paper:** *TOKI: A Bitemporal Operator Algebra…*, arXiv:2606.06240 (2026).

**Claim:** Contradiction resolution is write-time concurrency control. Four heuristics (LWW / evidence-weighted / await-confirmation / per-rule) need isolation preconditions and audit-row preservation. LLM judges on the write path admit replay inconsistency, belief-drift skew, or audit erasure.

**Design rules:** `toki_classify_operator` plans without writing; `toki_anomaly_scan` reports the three anomaly proxies. Judge stays off Stele core write path.

---

## 60. MemArchitect triage & bid (v3.1)

**Paper:** *MemArchitect: A Policy Driven Memory Governance Layer*, arXiv:2603.18330 (2026).

**Claim:** Context admission should be an active triage & bid economy — every memory competes for limited slots — not passive top-k retrieval.

**Design rules:** `context_bid` scores relevance × authority × worth; report-only; never auto-deletes. Proxies only.

---

## 61. MemoRepair exact s–t min-cut (v3.2)

**Paper:** *MemoRepair: Barrier-First Cascade Repair…*, arXiv:2605.07242 (2026).

**Claim:** For fixed λ, valid successor republication is maximum-weight predecessor closure and reduces to a single s–t min-cut (Picard). Greedy is a proxy; exact cut recovers more of the repair-all ceiling at lower cost.

**Design rules:** `repair_select_mincut` via Edmonds–Karp on the closure network. Still report-only — callers withdraw then republish. Proxies only — not ToolBench scores.

---

## 62. CUPMem write-side adjudication (v3.2)

**Paper:** STALE / CUPMem prototype, arXiv:2605.06527 (2026).

**Claim:** New evidence should adjudicate whether older memories remain usable, must be revised, or are blocked before query time. Unsafe slots without a settled replacement are unknown-current.

**Design rules:** `adjudicate_update` / `unknown_current_slots` / `authorize_retrieval`. Deterministic — no NLI on core.

---

## 63. CMGL procedural admit receipts (v3.2)

**Source:** Certified Memory Governance Layer (CMGL) — local fail-closed middleware between agent runtime and memory backends.

**Claim:** Protected writes need structured authority bundles and typed admit/block receipts; natural-language-only authorization is rejected; missing authority fails closed before the adapter is called.

**Design rules:** `admit_gate` / `list_admit_receipts` / `verify_admit_receipt`. Local digests only — not product CMGL conformance.

---

## 64. TierMem provenance-linked tiers (v3.3)

**Paper:** *From Lossy to Verified: A Provenance-Aware Tiered Memory for Agents*, arXiv:2602.17913 (2026).

**Claim:** Inference-time evidence allocation — answer from cheapest sufficient evidence. Tier-1 summaries link to immutable Tier-2 raw logs; a sufficiency router escalates on miss; verified write-back consolidates grounded findings.

**Design rules:** `put_raw_page` / `sufficiency_gate` / `escalate_raw` / `verified_writeback`. Deterministic miss cues — not a trained router. Proxies only — not LoCoMo scores.

---

## 65. MSCE memory→skill co-evolution (v3.3)

**Paper:** *From Memory to Skills: Evidence-Grounded Co-Evolution…* (MSCE), arXiv:2607.16621 (2026).

**Claim:** Governed memory crystallizes into callable skills with evidence links, applicability boundaries, and reflection-weighted value backfill — not passive retrieval of traces.

**Design rules:** `skill_eligibility` / `crystallize_skill` / `value_backfill` / `skill_catalog`. Draft + optional ADD; promote still requires separate oracle. Proxies only.

---

## 66. FadeMem dual-layer forgetting (v3.4)

**Paper:** *FadeMem: Dual-Layer Forgetting for Long-Term Agent Memory*, arXiv:2601.18642 (2026).

**Claim:** Short-term and long-term memory layers need different decay; fusion consolidates near-duplicates; forgetting queues must not silently erase contested evidence.

**Design rules:** `fade_strength` / `fade_scan` / `fusion_candidates`. Report-only fade — never auto-delete. Deterministic fusion plans — not LLM merge. Proxies only — not LoCoMo scores.

---

## 67. SSGM Weibull relevance (v3.4)

**Paper:** *SSGM: Structured Shared Governance Memory…*, arXiv:2603.11768 (2026) (Weibull relevance component).

**Claim:** Retrieval eligibility should apply continuous Weibull relevance over verified age, reinforced by usage — not flat TTL alone.

**Design rules:** `weibull_relevance` + Select `min_weibull` / `weibull_eta` / `weibull_kappa`. Requires caller clock. Annotates hit slices. Proxies only.

---

## 68. MemR3 reflective evidence-gap retrieval (v3.4)

**Paper:** *MemR3: Memory Retrieval with Reflective Reasoning…*, arXiv:2512.20237 (2025).

**Claim:** After Select, measure uncovered query needs and propose follow-up probes before answering from incomplete evidence.

**Design rules:** `evidence_gap` / `reflective_retrieve` / `gap_tracker_update`. Deterministic token/digit coverage — not reflective LLM. Caller runs next Select. Proxies only.

---

## 69. Oblivion-shaped reversible archive (v3.5)

**Paper:** *Oblivion: Self-Adaptive Agentic Memory Control through Decay-Driven Activation*, arXiv:2604.00131 (2026).

**Claim:** Forgetting is decay-driven accessibility reduction — not hard deletion. Archived tips leave the retrieval pool but remain addressable and restorable.

**Design rules:** `archive_plan` / `archive_apply` / `unarchive` / `list_archived`. State `archived` excluded from Select. Guidance layers never auto-eligible. Actor required for apply. Proxies only.

---

## 70. SF-AMS composite importance (v3.5)

**Paper:** *SF-AMS: Strategic Forgetting for Structured Memory in LLM Agents*, arXiv:2607.22562 (2026).

**Claim:** Utility-driven hierarchical memory needs a composite importance score blending temporal decay, usage, and redundancy — then tiered control.

**Design rules:** `composite_importance` / `cis_scan` with tiers core/important/secondary/irrelevant. Deterministic blend of Weibull + MW + retention + pin/use. Proxies only — not LoCoMo F1.

---

## 71. MemCon control suggest (v3.5)

**Paper:** *Memory as a Controlled Process…* (MemCon), arXiv:2607.13591 (2026).

**Claim:** Optimal memory behavior is context-dependent (when/what/how much to retrieve, consolidate, forget) — fixed always-on retrieval is a bottleneck. MemCon learns a policy; Stele ships a deterministic heuristic suggest surface for callers.

**Design rules:** `control_suggest` actions NO_OP / RETRIEVE / RE_RETRIEVE / CONSOLIDATE / FORGET / PLAN_INJECT. Heuristic proxy — not UCB bandit training on core. Proxies only.

---

## 72. SCM sleep-consolidated memory (v3.6)

**Paper:** *SCM: Sleep-Consolidated Memory with Algorithmic Forgetting…*, arXiv:2604.20943 (2026).

**Claim:** Working-memory capacity limits + multi-dimensional value tags + offline NREM/REM/forget stages beat always-on append-only stores.

**Design rules:** `value_tag` / `wm_*` / `sleep_trigger` / `sleep_plan` / `sleep_apply_nrem`. Overlay WM (capacity 7). Sleep plans report-only; NREM apply reinforces usage only — never auto-delete. No LLM MeaningEncoder on write path. Proxies only.

---

## 73. GAM hierarchical graph decoupling (v3.6)

**Paper:** *GAM: Hierarchical Graph-based Agentic Memory…*, arXiv:2604.12285 (2026) / ACL 2026.

**Claim:** Isolate fast episodic buffering from stable semantic consolidation; trigger consolidation on semantic boundaries — not every stream token.

**Design rules:** `episodic_buffer` (quarantine) / `semantic_boundary` / `consolidate_plan`. Never auto-promote (C7). Proxies only.

---

## 74. Agentic Context Management anticipate + verify (v3.6)

**Paper:** *Agentic Context Management…*, arXiv:2607.21503 (2026).

**Claim:** Memory-as-store is too narrow; context lifecycle needs anticipation (prefetch next) and verifiable compaction (fail closed if critical facts drop).

**Design rules:** `anticipate` / `verify_compaction`. Prefetch from LINKs/conflict_key/token overlap. Compaction verify is fail-closed. Proxies only — not Synap LoCoMo scores.

---

## 75. LightMem sensory→STM→LTM efficiency (v3.7)

**Paper:** *LightMem: Lightweight and Efficient Memory-Augmented Generation*, arXiv:2510.18866 (2025).

**Claim:** Atkinson–Shiffrin stages (sensory pre-filter → topic-aware STM → sleep-time LTM) cut token/API cost while preserving accuracy.

**Design rules:** `sensory_filter` / `stage_inventory` / `topic_segments` / `stage_budget_plan`. Deterministic filters — not LLMLingua. Proxies only — not LongMemEval scores.

---

## 76. HippoRAG multi-hop PPR (v3.7)

**Paper:** Gutiérrez et al., *HippoRAG…*, NeurIPS 2024; MemHop multi-hop eval (2026 ecosystem).

**Claim:** Isolated top-k misses associative multi-hop; Personalized PageRank over a memory graph recovers linked support.

**Design rules:** `ppr_scores` / `multi_hop_retrieve` on entry LINK graph with lexical seeds. No neural embeddings on core path. Proxies only — not MemHop paper scores.

---

## 77. Quipu gated writes + MAP-Graph action risk (v3.7)

**Papers:** *Quipu…*, arXiv:2608.16813 (2026); MAP-Graph action gate (arXiv:2608.10509).

**Claim:** Agent-written knowledge must pass post-state predicates before entry; irreversible actions need risk-sensitive Allow/Block/Reverify/AskUser with trust thresholds.

**Design rules:** `write_gate` (pending predicates) / `action_risk_gate` (θ by risk; affected support blocks high). Report-only gates — wire as hard pre-check only via opt-in later. Proxies only.

---

## 78. ProGraph profiles + compression residuals (v3.8)

**Paper:** *ProGraph…*, arXiv:2607.19359 (2026).

**Claim:** Graph memory needs profile expansion beyond seed hits, and compression must preserve precision-critical residuals (dates, quantities, names, codes) that summaries drop.

**Design rules:** `extract_residuals` / `register_entities` / `profile_expand` / `residual_augment`. Deterministic regex/token proxies — not LLM co-extract. Proxies only — not ProGraph paper scores.

---

## 79. EMG experience-memory correction paths (v3.8)

**Paper family:** Experience-memory graphs / corrective skill edit paths (EMG-shaped; 2026 agent-memory ecosystem).

**Claim:** Failed lessons should map to a successful workflow/skill as a one-shot graph edit (add/delete/relabel), not an open-ended reflect-replay loop that rewrites SoT.

**Design rules:** `match_correction` / `insight_inject`. Report-only — never auto-rewrites entries. Proxies only.

---

## 80. AgentIR cascade multi-channel RRF (v3.8)

**Paper family:** AgentIR / MemFuse-style cascade routing + reciprocal rank fusion across channels (2026).

**Claim:** Expensive graph channels should skip when lexical margin is decisive; otherwise fuse lexical + PPR + residual rankings with one RRF.

**Design rules:** `cascade_route` / `multi_channel_fuse` reusing `rrf_fuse`. Proxies only — not AgentIR paper latency.

---

## 81. Governed Memory dual project + governance route (v3.9)

**Paper:** *Governed Memory: A Production Architecture for Multi-Agent Workflows*, arXiv:2603.17787 (2026).

**Claim:** Enterprise multi-agent memory fails without dual open-set facts + schema-typed properties, and without a fast (non-LLM) governance routing path for organizational context.

**Design rules:** `dual_project` / `governance_route`. Deterministic projection and hybrid ranking — C5 preserved (no LLM full path on core). Proxies only — not Personize LoCoMo scores.

---

## 82. Progressive session delta + entity isolation (v3.9)

**Paper:** same Governed Memory architecture (progressive context delivery + entity-scoped isolation).

**Claim:** Re-injecting critical governance every step wastes ~50% tokens; entity isolation must be key-filtered (CRM/subject), not embedding distance.

**Design rules:** `session_delta_*` / `entity_context` / `entity_leak_probe`. Supplementary never locked as delivered. Proxies only.

---

## 83. HyMem typed context isolation (v3.9)

**Paper:** *HyMem: Hierarchical Context Management for Long-Horizon Agents via Information Isolation*, arXiv:2608.15703 (2026).

**Claim:** Context dilution comes from raw execute/reason traces entering the planner; typed slots with schema-constrained crossover preserve focus.

**Design rules:** `hymem_classify_slot` / `hymem_isolate_pack`. Cue proxies — not HyMem Pass@1 scores.

---

## 84. Deterministic freshness assembly (v4.0)

**Paper:** *Don't Ask the LLM to Track Freshness: A Deterministic Recipe for Memory Conflict Resolution*, arXiv:2606.01435 (2026).

**Claim:** Conflict-resolution bottleneck is post-retrieval **assembly**, not storage topology. Candidate extract + Python max(serial|timestamp) beats LLM freshness judgment, especially as context grows.

**Design rules:** `extract_version_markers` / `freshness_resolve` / `assemble_current` / `hop_freshness`. Never ask an LLM which tip is current. Proxies only — not FC-SH paper scores.

---

## 85. MemTxn Ordered PatchTest + Temporal Resolver (v4.0)

**Paper:** *MemTxn: A Transaction Boundary for Source-Supported Updates…*, arXiv:2607.27834 (2026).

**Claim:** Writable memory needs a governance boundary: updates must be source-supported; conflicting facts need a deterministic visible version; faults need complete active-map recovery.

**Design rules:** `patch_test` / `temporal_resolve` / `recover_active_map` (alongside existing MemTX begin/stage/commit). Report-only where noted. Proxies only.

---

## 86. Fleet scoped propagation (v4.0)

**Paper:** *Governed Shared Memory for Multi-Agent LLM Systems*, arXiv:2606.24535 (2026).

**Claim:** Fleet memory fails via unauthorized leakage, stale propagation, contradiction persistence, provenance collapse. Propagation must be policy-scoped; stale tips beside fresher winners are pollution.

**Design rules:** `fleet_scope_gate` / `propagate_plan` / `stale_propagation_scan`. Never silent merge. Proxies only.

---

## 87. BudgetMem query-aware budget tiers (v4.1)

**Paper:** *Learning Query-Aware Budget-Tier Routing for Runtime Agent Memory*, arXiv:2602.06025 (2026).

**Claim:** Runtime memory extraction should expose Low/Mid/High tiers per module with query-aware routing for an explicit performance–cost frontier.

**Design rules:** `query_complexity` / `budget_tier_route` / `budget_module_plan`. Deterministic heuristic router — not RL policy (C5). Proxies only — not BudgetMem LoCoMo scores.

---

## 88. Skill library lexical ranker (v4.1)

**Paper:** *Comparative Approaches to Agent Retrieval over Large Skill Libraries*, arXiv:2608.06196 (2026).

**Claim:** Hybrid rankers dominate sparse skill loading; typed knowledge graphs rarely extend retrieval reach beyond the ranker's neighborhood.

**Design rules:** `skill_rank` / `skill_prereq_expand`. LINK walk for relations; do not claim graph extends reach. Proxies only.

---

## 89. ERSkill retrieval-skill composition (v4.1)

**Paper:** *ERSkill: Evolving for Skill-Guided Adaptive Memory Retrieval*, arXiv:2608.12720 (2026).

**Claim:** Retrieval behaviors should be executable skills composed from primitives, selected per query.

**Design rules:** `list_retrieval_primitives` / `compose_retrieval_skill` / `route_retrieval_skill` / `run_retrieval_skill`. Cue router — not co-evolving trie. Proxies only.

---

## 90. ConsistencyGate write-time admission (v4.2)

**Paper:** *ConsistencyGate: Preventing Memory Contamination…*, arXiv:2607.22962 (2026).

**Claim:** Memory contamination = hallucinated facts admitted as premises. Write-time admission must score support, not utility/recency.

**Design rules:** `support_score` / `consistency_admit`. Lexical τ proxy — not K LLM soft votes (C5). Proxies only.

---

## 91. MemGate query-conditioned retrieval (v4.2)

**Paper:** *Beyond Similarity: Trustworthy Memory Search…* (MemGate), arXiv:2606.06054 (2026).

**Claim:** Unconditional nearest-neighbor injection enables cross-domain leakage and jailbreak ASR; retrieval needs task-conditioned admission.

**Design rules:** `retrieval_admit` / `task_conditioned_pack`. Deterministic overlap gate — not 9M neural plug-in. Proxies only.

---

## 92. Mnemonic sovereignty primitives (v4.2)

**Paper:** *Toward Mnemonic Sovereignty* survey, arXiv:2604.16548 (2026).

**Claim:** No published architecture covers all governance primitives; post-deletion verification and rollback are shared blind spots.

**Design rules:** `sovereignty_checklist` / `post_delete_verify` / `rollback_plan`. Report-only rollback. Proxies only.

---

## 93. SodaMem evidence-grounded temporal packs (v4.3)

**Paper:** SodaMem (evidence-grounded temporal graph / density fusion), arXiv:2608.08055 (2026).

**Claim:** Multi-tunnel retrieval should accumulate connection density on evidence IDs; a planner gathers IDs before a reader emits prose; every reader block must cite.

**Design rules:** `density_fuse` / `evidence_plan` / `cited_pack`. Stdlib mass weights — not dense embeds or LLM readers. Proxies only.

---

## 94. MemRefine storage-budget compression (v4.3)

**Paper:** MemRefine, arXiv:2606.13177 (2026).

**Claim:** Post-construction memory can be compressed under a storage budget via merge/preserve/delete plans without an LLM pairwise judge on the core path.

**Design rules:** `compress_candidates` / `refine_plan`. Similarity proposes; deterministic heuristics decide. Report-only — actor applies. Proxies only.

---

## 95. AriadneMem + MemFuse coarsening (v4.3)

**Papers:** AriadneMem-style merge/link/add + bridge discovery; MemFuse multi-source cluster fusion, arXiv:2608.18704 (2026).

**Claim:** Offline coarsening chooses merge vs link vs add; online reconstruction finds LINK bridges between seed facts; clusters summarize without erasing atomic evidence IDs.

**Design rules:** `merge_link_add` / `bridge_discover` / `fuse_cluster`. Deterministic Jaccard + BFS — not iterative LLM planning. Proxies only.

---

## 96. TGMS verified temporal operators (v4.4)

**Paper:** *TGMS: An Agent-Native Bi-Temporal Graph Management System*, arXiv:2607.10265 (2026).

**Claim:** Temporal answers need typed, cost-guarded operators; plans verified before execute; claims checked against content-addressed traces; summaries quarantine on correction overlap.

**Design rules:** `result_digest` / `operator_cost_estimate` / `plan_static_verify` / `claim_verify` / `summary_quarantine_scan`. Stdlib only — not TGMS product. Proxies only.

---

## 97. MemoryData localized maintenance (v4.4)

**Paper:** *Are We Ready For An Agent-Native Memory System?* (MemoryData), arXiv:2606.24775 (2026).

**Claim:** Localized maintenance on a bounded subset is more cost-efficient than global reorganization on every write (finding O7).

**Design rules:** `localized_maintenance_plan` / `maintenance_cost_compare`. Report-only; actor applies. Proxies only.

---

## 98. Trace-grounded answer gating (v4.4)

**Paper:** TGMS claim verifier + truncation taint (arXiv:2607.10265).

**Claim:** Correct arithmetic over truncated evidence is still misleading — support ≤ weak; contradicted count/entity/ordering claims block emission.

**Design rules:** Covered by `claim_verify` (UC-224). Proxies only.

---

## 99. TMA-NM non-malleable origin authority (v4.5)

**Paper:** *Securing LLM-Agent Long-Term Memory Against Poisoning…*, arXiv:2606.24322 (2026).

**Claim:** Content- and lineage-based defenses are malleable under self-summarization, trusted-tool echo, and manufactured corroboration. Write-time origin binding + Sybil-resistant corroboration-gated elevation is necessary and sufficient.

**Design rules:** `origin_bind` / `propagate_origin` / `launder_scan` / `act_authority_gate`. Deterministic — not MEM-INV ASR. Proxies only.

---

## 100. AM-Sentry / GhostWriter two-stage defense (v4.5)

**Paper:** *When Agents Remember Too Much…* (GhostWriter + AM-Sentry), arXiv:2607.06595 (2026).

**Claim:** Indirect memory poisoning via untrusted tool inputs needs a memory-saving policy and a retrieval screen before context injection.

**Design rules:** `save_policy` / `retrieval_screen`. Marker + origin heuristics — no LLM judge on core. Proxies only.

---

## 101. Chronos temporal persistence threat (v4.5)

**Paper:** *The Chronos Vulnerability…*, arXiv:2607.19433 (2026).

**Claim:** Persistence-based deception decouples injection from activation; endpoint content filters alone are insufficient — origin-bound act gates close the gap.

**Design rules:** Covered by `act_authority_gate` + `retrieval_screen`. Proxies only.

---

## 102. MemForest / MemTree hierarchical temporal index (v4.6)

**Paper:** *MemForest: An Efficient Agent Memory System with Hierarchical Temporal Indexing*, arXiv:2605.23986 (2026).

**Claim:** Full-state rewrites and serial LLM-in-the-loop extraction dominate write latency. MemTree localizes updates to dirty paths and enables coarse-to-fine retrieval.

**Design rules:** `build_memtree` / `dirty_path_plan` / `coarse_to_fine`. Stdlib temporal buckets — not MemForest product. Proxies only.

---

## 103. xMemory decoupling and top-down retrieval (v4.6)

**Paper:** *Beyond RAG for Agent Memory: Retrieval by Decoupling and Aggregation* (xMemory), arXiv:2602.02007 (2026).

**Claim:** Flat top-k RAG returns redundant correlated spans; retrieve over themes/semantics and expand to raw leaves only when uncertainty remains.

**Design rules:** `build_themes` / `theme_attach` / `split_merge_plan` / `top_down_pack`. Deterministic Jaccard — no LLM split judge. Proxies only.

---

## 104. TiMem temporal-hierarchical consolidation (v4.6)

**Paper:** TiMem Temporal Memory Tree (ACL Findings 2026 companion to hierarchical temporal recall).

**Claim:** Long-horizon agents need temporal continuity as a first-class organizing principle with complexity-aware recall across levels.

**Design rules:** Covered by MemTree intervals + `coarse_to_fine` / `top_down_pack`. Proxies only.

---

## 105. MemSecBench Write–Execute–Forget lifecycle (v4.7)

**Paper:** *MemSecBench: Tracking Agent Memory Poisoning from Persistence to Consequence and Repair*, arXiv:2607.27080 (2026).

**Claim:** Attack resistance and selective repair are independent; adoption is the decisive Execute bottleneck; repair must preserve benign memories.

**Design rules:** `persistence_probe` / `execute_chain_probe` / `selective_repair_plan` / `lifecycle_report`. Proxies only — not paper ASR.

---

## 106. SleepGate proactive interference (v4.7)

**Paper:** *Learning to Forget: Sleep-Inspired Memory Consolidation…* (SleepGate), arXiv:2603.14517 (2026).

**Claim:** Superseded associations cause proactive interference; conflict-aware tagging + forget gate + consolidation shrink the interference horizon.

**Design rules:** `conflict_tag` / `forget_gate_plan` / `consolidate_survivors` / `pi_depth_scan`. Deterministic — not learned KV-gate NN. Proxies only.

---

## 107. A-MemGuard consensus retrieval (v4.7)

**Paper / system:** A-MemGuard consensus-based memory anomaly defense (2026 ecosystem).

**Claim:** Single-channel similarity admits poisoned memories; multi-channel consensus before context inject reduces anomalies.

**Design rules:** `consensus_admit`. Lexical + LINK + marker channels — no LLM judge. Proxies only.

---

## 108. Dependency-guided rollback repair (v4.8)

**Paper:** *From Faulty Memories to Corrected Actions: Dependency-Guided Rollback Repair…*, arXiv:2608.10502 (2026).

**Claim:** Reachability alone over-invalidates; preserve candidates with independent trusted support; selectively replay only dirty action steps.

**Design rules:** `build_mem_action_graph` / `dependency_trace` / `preserve_independent` / `selective_replay_plan`. Report-only — actor applies. Proxies only.

---

## 109. MPBench write-channel taxonomy + source isolation (v4.8)

**Paper:** *From Untrusted Input to Trusted Memory…* (MPBench), arXiv:2606.04329 (2026).

**Claim:** Four write channels and structural vulnerabilities make untrusted content exploitable when treated as authenticated user input; source isolation on the write path is required.

**Design rules:** `classify_write_channel` / `source_isolation_gate` / `write_channel_inventory` / `channel_admit_batch`. Prefix taxonomy — no LLM judge. Proxies only.

---

## 110. MemPoison L1–L3 threat ladder (v4.9)

**Paper:** *MemPoison: Uncovering Persistent Memory Threats…*, arXiv:2607.14651 (2026).

**Claim:** Write-time defenses suppress direct L1 injections but fail on compositional L2 and context-triggered dormant L3 threats.

**Design rules:** `slot_coverage` / `threat_tier_classify` / `dormant_trigger_scan` / `mempoison_ladder_report`. Marker taxonomy — not MID paper scores. Proxies only.

---

## 111. Salami / MemCollusion compositional poisoning (v4.9)

**Paper:** *Salami Attack: Stealthy Collusive Memory Poisoning…*, arXiv:2608.01637 (2026).

**Claim:** Multiple individually benign memories can jointly induce unsafe behavior; entry-wise auditors miss coalitions.

**Design rules:** `compositional_coalition_scan` / `collusion_risk_gate` / `salami_pair_probe`. Retrieval-pack firewall — no LLM judge. Proxies only.

---

## 112. Knowledge/Memory/Wisdom/Intelligence persistence (v5.0)

**Paper:** *The Missing Knowledge Layer in Cognitive Architectures for AI Agents*, arXiv:2604.11364 (2026).

**Claim:** Applying cognitive decay to factual claims is a category error; layers need distinct persistence semantics (indefinite supersession vs Ebbinghaus vs evidence-gated vs ephemeral).

**Design rules:** `classify_persistence_layer` / `persistence_policy` / `layer_inventory` / `knowledge_protect_scan` / `intelligence_reject_gate`. Proxies only.

---

## 113. Credential reject at memory write (v5.0)

**Papers / systems:** MAPLE-Guard write Reject (arXiv:2608.00426); PRISM secret leakage (arXiv:2605.10614) as pattern inspiration.

**Claim:** Credentials and secrets must never become persistent memory state; reject at write, inventory survivors for hygiene.

**Design rules:** `credential_scan` / `credential_reject_gate` / `credential_store_scan`. Stdlib patterns — not keyed vault. Proxies only.

---

## 114. Uncertainty-gated retrieval + adaptive reserve (v5.0)

**Papers:** Oblivion Decayer/Activator (arXiv:2604.00131); MemArchitect adaptive token budgeting (arXiv:2603.18330).

**Claim:** Always-on retrieval pollutes context; retrieve when uncertainty is high; split budget between reasoning and recall by confidence.

**Design rules:** `uncertainty_score` / `uncertainty_retrieve_gate` / `reasoning_reserve_plan`. Lexical uncertainty — no LLM. Proxies only.

---

## 115. Portable Agent Memory deepen — Merkle + capabilities (v5.1)

**Paper:** *Portable Agent Memory…*, arXiv:2605.11032 (2026).

**Claim:** Cross-agent transfer needs a typed (E,S,P,W,I) model, tamper-evident Merkle-DAG, capability-scoped selective disclosure, and injection-resistant rehydration — without vendor lock-in.

**Design rules:** `classify_memory_component` / `build_merkle_dag` / `verify_merkle_root` / `issue_capability_token` / `check_capability` / `selective_disclose` / `rehydrate_safe_plan`. SHA-256 unkeyed digests — Ed25519/BLAKE3 caller-side. Proxies only.

---

## 116. CapSeal non-exportable action capabilities (v5.1)

**Paper:** *CapSeal: Capability-Sealed Secret Mediation…*, arXiv:2604.16762 (2026).

**Claim:** Handing agents bearer secrets fails under prompt injection; grant narrowly scoped, non-exportable action handles mediated by a broker instead.

**Design rules:** `issue_action_capability` / `capability_export_probe` / `check_action_capability` / `action_capability_inventory`. No raw secrets in handles; export always denied. Proxies only — not a live UDS broker.

---

## 117. AgentDoG trajectory diagnostics (v5.2)

**Paper:** *AgentDoG: A Diagnostic Guardrail Framework…*, arXiv:2601.18491 (2026).

**Claim:** Agentic safety needs an orthogonal 3D taxonomy (risk source / failure mode / real-world harm) and root-cause diagnosis — including seemingly safe but unreasonable actions — beyond binary unsafe labels.

**Design rules:** `classify_risk_source` / `classify_failure_mode` / `classify_real_world_harm` / `diagnose_trajectory_step` / `diagnose_trajectory` / `safe_but_unreasonable_scan` / `taxonomy_inventory`. Lexical taxonomy proxies — not AgentDoG model weights or ATBench scores.

---

## 118. MemWeaver hybrid memory weave (v5.2)

**Paper:** *MemWeaver: Weaving Hybrid Memories…*, arXiv:2601.18204 · ACL 2026 Findings.

**Claim:** Long-horizon agents need consolidation into temporally grounded graph memory, experience abstraction, and passage evidence, retrieved via dual-channel structured+textual fusion.

**Design rules:** `weave_layer_assign` / `build_hybrid_weave` / `dual_channel_retrieve` / `experience_abstract_plan` / `temporal_session_conflict_scan`. Report-only abstraction/reconcile — no auto-write. Proxies only — not LoCoMo paper scores.

---

## 119. MemHop hop-depth path score (v5.2)

**Paper:** Profile-Graph / MemHop (arXiv:2607.19359, 2026).

**Claim:** Multi-hop association (hop depths 1–5) must be measured explicitly; single-hop recall benchmarks hide association failures.

**Design rules:** `multi_hop_depth_score` over explicit LINK paths. Proxies only — not MemHop leaderboard scores.

---

## 120. MemEvolve / EvolveLab architecture meta-evolution (v5.3)

**Paper:** *MemEvolve: Meta-Evolution of Agent Memory Systems*, arXiv:2512.18746 (ICML 2026).

**Claim:** Self-improving agents are limited by static memory architectures; Ω must be decomposed into Encode/Store/Retrieve/Manage and dual-evolved (experience + architecture) via diagnose-and-design.

**Design rules:** `list_design_space` / `architecture_profile` / `diagnose_architecture` / `propose_architecture_variants` / `rank_architecture_fitness` / `select_architecture_parents`. Variants are report-only — no auto-swap of live store policy. Proxies only.

---

## 121. MindMemOS EPT / dreaming / skill evolution (v5.3)

**Paper:** *MindMemOS: A Portable and Self-Evolving Memory Operating Layer…*, arXiv:2608.12428 (2026).

**Claim:** Long-horizon agents need entity–property–time structure, offline dreaming consolidation, corrective feedback revise, and trajectory-driven skill evolution.

**Design rules:** `ept_classify` / `dreaming_consolidate_plan` / `feedback_revise_plan` / `skill_evolve_plan`. Plans never auto-delete or auto-write skills. Proxies only — not LOCOMO/PersonaMem scores.

---

## 122. MEMGUARD functional type boundaries (v5.3)

**Paper:** *MemGuard: Preventing Memory Contamination…*, arXiv:2605.28009 (2026).

**Claim:** Heterogeneous memory contamination (semantic/episodic/procedural bleed) causes persistent hallucinations; enforce write-time roles and query-adaptive type routing.

**Design rules:** `functional_role_assign` / `contamination_scan` / `type_route_retrieve`. Lexical proxies — not HaluMem paper scores.

---

## 123. PAMU preference-aware memory update (v5.4)

**Paper:** *Preference-Aware Memory Update for Long-Term LLM Agents*, arXiv:2510.09720 (ACL 2026 Findings).

**Claim:** Storage/retrieval advances leave preference memory static; SW+EMA fusion with divergence change detection enables modular preference-aware updates without fine-tuning.

**Design rules:** `extract_preference_signal` / `fuse_preference` / `preference_change_detect` / `preference_update_plan` / `format_preference_prompt`. Report-only — no auto-write of preference entries. Proxies only — not LoCoMo paper scores.

---

## 124. BEAM-shaped evaluation categories (v5.4)

**Benchmark:** BEAM (1M/10M-scale agent memory eval) — preference following, knowledge update, abstention, contradiction resolution, temporal/event ordering, multi-session, summarization, instruction following, information extraction.

**Claim:** Production memory cannot be judged by single-hop recall alone; category-specific gates are required.

**Design rules:** `beam_category_inventory` / `classify_beam_query` / `knowledge_update_check` / `abstention_gate` / `contradiction_resolve_plan` / `event_order_check` / `beam_eval_pack`. Proxies only — not BEAM leaderboard scores. Contradiction plans never auto-collapse (C contested preserve).

---

## 125. HaluMem operation-stage localization (v5.4)

**Paper:** *HaluMem: Evaluating Hallucinations in Memory Systems of Agents*, arXiv:2511.03506 (2025/2026).

**Claim:** End-to-end QA hides where hallucinations arise; localize to extraction, updating, or QA stages.

**Design rules:** `localize_hallucination_stage`. Lexical stage proxy — not HaluMem-Medium/Long scores.

---

## 126. REMem episodic hybrid memory (v5.5)

**Paper:** *REMem: Reasoning with Episodic Memory in Language Agent*, arXiv:2602.13530 (ICLR 2026).

**Claim:** Agents need explicit episodic recollection/reasoning via time-aware gists, temporal facts, situational binding, and agentic iterative retrieval — not flat semantic RAG.

**Design rules:** `extract_episodic_gist` / `extract_temporal_facts` / `situational_bind` / `build_hybrid_episodic_graph` / `agentic_retrieve_plan` / `ordinal_event_query`. Tool plans are report-only — no LLM ReAct loop on core. Proxies only.

---

## 127. EverMemOS MemCell / MemScene lifecycle (v5.5)

**Paper:** *EverMemOS: A Self-Organizing Memory Operating System…* (ACL 2026 long).

**Claim:** Long-horizon memory should follow an engram-inspired lifecycle: MemCell formation → MemScene consolidation → reconstructive recollection with foresight filtering and necessity/sufficiency.

**Design rules:** `form_memcell` / `consolidate_memscenes` / `foresight_filter` / `reconstructive_recollect` / `profile_evolve_plan` / `necessity_sufficiency_check`. Profile/scene plans never auto-write. Proxies only — not LoCoMo/LongMemEval paper scores.

---

## 128. MemoryOS hierarchical heat paging (v5.6)

**Paper:** *Memory OS of AI Agent*, arXiv:2506.06326 (2025–2026).

**Claim:** Long conversations need OS-style STM / MTM / LPM with segmented paging and heat-based eviction/promotion — not a flat FIFO context queue.

**Design rules:** `classify_memory_tier` / `heat_score` / `segment_pages` / `stm_to_mtm_plan` / `mtm_evict_plan` / `promote_to_lpm_plan` / `hierarchical_retrieve`. Heat = α·N_visit + β·L_interaction + γ·exp(−Δt/μ). Evict/promote plans are report-only. Proxies only — not MemoryOS paper F1.

---

## 129. NEMORI prediction-error distillation (v5.6)

**Paper:** *What Deserves Memory: Adaptive Memory Distillation for LLM Agents* (NEMORI), ACL 2026 long.

**Claim:** What deserves retention is what existing knowledge cannot anticipate — distill via prediction error, not designer importance heuristics. Distillation stays management-agnostic.

**Design rules:** `integrate_episodic_narrative` / `anticipatory_schema` / `prediction_error_distill` / `deserves_memory_gate` / `distill_batch_plan`. Batch distill never auto-writes (`apply: false`). Proxies only — not LoCoMo LLM-judge scores.

---

## 130. Hindsight four-network retain / recall / reflect (v5.7)

**Paper:** *Hindsight is 20/20: Building Agent Memory that Retains, Recalls, and Reflects*, arXiv:2512.12818 (2025–2026).

**Claim:** Agent memory must separate world facts, experiences, opinions, and observations; operations are retain / recall / reflect with disposition-conditioned belief updates — not a flat RAG bag.

**Design rules:** `classify_network` / `retain_plan` / `network_inventory` / `recall_multi_strategy` / `opinion_reinforce` / `reflect_plan`. Reflect is report-only (no LLM Cara). Proxies only — not LongMemEval paper scores.

---

## 131. ReasoningBank strategy distill + MaTTS (v5.7)

**Paper:** *ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory*, arXiv:2509.25140 (2025).

**Claim:** Transferable memory is strategy items (title/description/content) distilled from *both* successes and failures; MaTTS scales contrastive experience for better memory.

**Design rules:** `distill_strategy_item` / `failure_lesson_gate` / `retrieve_strategies` / `consolidate_strategy_plan` / `matts_contrastive_plan`. Success-only banks fail the gate. Proxies only — not WebArena / SWE-Bench scores.

---

## 132. MemSkill evolvable memory skills (v5.8)

**Paper:** *MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents*, arXiv:2602.02474 (2026).

**Claim:** Memory extraction should be skill-conditioned (INSERT/UPDATE/DELETE/SKIP + evolved skills), selected by a controller at span level, with a designer that grows the skill bank from hard cases — not a fixed hand-crafted pipeline.

**Design rules:** `init_skill_bank` / `span_partition` / `select_skills` / `execute_skill_plan` / `record_hard_case` / `designer_evolve_plan`. No RL controller or LLM executor on core. Proxies only.

---

## 133. Memory-R1 ADD/UPDATE/DELETE/NOOP (v5.8)

**Paper:** *Memory-R1* (arXiv:2508.19828).

**Claim:** External memory needs an explicit manager that chooses ADD / UPDATE / DELETE / NOOP — not always-insert RAG.

**Design rules:** `classify_memory_op` / `noop_gate` / `memory_op_plan` / `conflict_update_plan` / `delete_stale_plan`. Plans are report-only (no trained RL manager on core). Proxies only.

---

## 134. G-Memory hierarchical MAS memory (v5.9)

**Paper:** *G-Memory: Tracing Hierarchical Memory for Multi-Agent Systems*, arXiv:2506.07398 (2025).

**Claim:** Multi-agent memory needs a three-tier graph (insight / query / interaction) with bi-directional traversal — not flat shared RAG.

**Design rules:** `classify_graph_tier` / `build_query_graph` / `upward_insight_traverse` / `downward_interaction_traverse` / `bidirectional_retrieve` / `hierarchy_update_plan`. Updates are report-only. Proxies only.

---

## 135. MemMA memory-cycle coordination (v5.9)

**Paper:** *MemMA: Coordinating the Memory Cycle…*, arXiv:2603.18718 (2026).

**Claim:** Construction and retrieval need Meta-Thinker guidance; sparse feedback is fixed by in-situ probe QA → verify → SKIP/MERGE/INSERT repair before commit.

**Design rules:** `meta_thinker_guidance` / `answerability_check` / `synthesize_probe_qa` / `verify_probes` / `repair_from_probes`. No LLM Meta-Thinker on core. Proxies only.

---

## 136. Agent Workflow Memory (v6.0)

**Paper:** *Agent Workflow Memory*, arXiv:2409.07429 (2024/2025).

**Claim:** Long-horizon agents improve when they induce reusable workflows from successful trajectories and selectively retrieve them to guide later tasks (offline + online).

**Design rules:** `induce_workflow` / `online_induce_gate` / `workflow_memory_add_plan` / `retrieve_workflows` / `workflow_step_budget`. Induce only on success. Proxies only.

---

## 137. Reflective Retrieval Memory — RRM (v6.0)

**Paper:** *RRM: Experience-Driven Reflective Retrieval Memory…*, arXiv:2607.28156 (2026).

**Claim:** Procedural retrieval experience (M+/M−) must become **query-level guidance** only; answer generation stays grounded in current-store facts. Lifecycle utility + prune keep the bank compact.

**Design rules:** `distill_retrieval_experience` / `anomaly_trigger` / `query_level_guidance` / `experience_lifecycle_score` / `prune_experience_plan` / `isolate_factual_from_procedural`. Proxies only.

---

## 138. ReMe dynamic procedural memory (v6.1)

**Paper:** *Remember Me, Refine Me…*, arXiv:2512.10696 (ACL 2026 Findings).

**Claim:** Passive append-only pools rot. Agents need multi-faceted distillation (success/failure/comparative), scenario-aware reuse with rewrite, and utility-based selective add + α/β prune.

**Design rules:** `multi_faceted_distill` / `scenario_retrieve` / `adaptive_rewrite_plan` / `utility_after_reuse` / `selective_add_plan` / `utility_prune_plan`. Plans report-only. Proxies only.

---

## 139. Dynamic Cheatsheet test-time memory (v6.1)

**Paper:** *Dynamic Cheatsheet: Test-Time Learning with Adaptive Memory*, arXiv:2504.07952 (2025).

**Claim:** Black-box LMs improve when a Gen/Cur loop stores concise strategies/code/insights — not full history. DC-RS = retrieve→curate→generate; DC-Cu = generate→curate.

**Design rules:** `extract_cheatsheet_snippet` / `retrieve_cheatsheet` / `curator_decide` / `compact_memory_gate` / `dc_rs_order_check`. Proxies only.

---

## 140. ExpeL experiential insights (v6.2)

**Paper:** *ExpeL: LLM Agents Are Experiential Learners*, arXiv:2308.10144 (AAAI 2024).

**Claim:** Pool success and failure trajectories; extract cross-task insights with ADD/EDIT/UPVOTE/DOWNVOTE and importance counts; at test time retrieve insights plus similar successes.

**Design rules:** `experience_pool_add` / `insight_op` / `insight_importance_gate` / `retrieve_insights` / `retrieve_similar_successes`. Proxies only.

---

## 141. Reflective Memory Management — dialogue RMM (v6.2)

**Paper:** *In Prospect and Retrospect: Reflective Memory Management…*, arXiv:2503.08026 (ACL 2025).

**Claim:** Prospective topic-based memory (utterance/turn/session) plus retrospective cite feedback to rerank and refine retrieval beats rigid-granularity RAG for long personalized dialogue.

**Design rules:** `prospective_reflect` / `topic_memory_bank` / `retrieve_topic_memories` / `retrospective_cite_feedback` / `rerank_memories` / `retrieval_refine_plan`. Distinct from retrieval-RRM (`rrm.py`). Proxies only.

---

## 142. Trace2Skill parallel skill consolidation (v6.3)

**Paper:** *Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills*, arXiv:2603.25158 (2026).

**Claim:** Sequential per-trace skill edits overfit. Parallel error/success analysts + hierarchical merge yield one portable skill that transfers across models/OOD without test-time retrieval.

**Design rules:** `collect_trajectory_label` / `propose_trajectory_patch` / `parallel_patch_pool` / `hierarchical_merge_patches` / `skill_mode_gate` / `prefer_parallel_over_sequential`. Ungrounded failures excluded. Proxies only.

---

## 143. Evo-Memory streaming self-evolution (v6.3)

**Paper:** *Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory*, arXiv:2511.20857 (2025).

**Claim:** Static recall benchmarks miss streaming adaptation. Agents need search–predict–evolve, ExpRAG task-level reuse, and ReMem-style refine (retrieve/prune/organize); reuse gains track within-dataset similarity.

**Design rules:** `streaming_task_append` / `exprag_retrieve` / `search_predict_evolve_check` / `evomem_refine_plan` / `evolution_similarity_hint`. Distinct from REMem (`remem.py`). Proxies only.

---

## 144. Mem-α memory construction via RL signals (v6.4)

**Paper:** *Mem-α: Learning Memory Construction via Reinforcement Learning*, arXiv:2509.25911 (2025).

**Claim:** Fixed tool instructions are weak for complex memory. Agents need core/episodic/semantic slots with insert/update/delete discipline, chunked writes, and rewards for QA correctness + tool format + compression + content validity — then generalize far beyond train length.

**Design rules:** `classify_memory_slot` / `memory_write_op` / `process_chunk_plan` / `compression_ratio` / `memalpha_reward_bundle` / `length_generalization_gate`. No GRPO on core. Proxies only.

---

## 145. AgentHER hindsight failure relabeling (v6.4)

**Paper:** *AgentHER: Hindsight Experience Replay for LLM Agent Trajectory Relabeling*, arXiv:2603.21357 (2026).

**Claim:** Success-only training wastes most trajectories. Classify recoverability, extract achievements, relabel goals with multi-judge confidence, package SFT/DPO/ShareGPT — offline, trajectory unchanged.

**Design rules:** `classify_failure` / `extract_replay_outcome` / `hindsight_relabel_plan` / `multi_judge_accept` / `package_training_pair`. Proxies only.

---

## 146. PreFlect prospective reflection (v6.5)

**Paper:** *PreFlect: From Retrospective to Prospective Reflection in Large Language Model Agents*, arXiv:2602.07187 (2026).

**Claim:** Post-hoc reflection is too late for irreversible actions. Distill planning errors from contrastive trajectories, critique plans before execute, revise, and re-plan on observation deviation — re-invoking prospective critique on every replan.

**Design rules:** `distill_planning_error` / `prospective_critique_plan` / `revise_plan_proposal` / `replan_on_deviation` / `preflect_before_execute_gate`. Proxies only.

---

## 147. SkillFlow flow-driven skill evolution (v6.5)

**Paper:** *SkillFlow: Flow-Driven Recursive Skill Evolution for Agentic Orchestration*, arXiv:2605.14089 (2026).

**Claim:** Reward-max orchestration collapses strategies; LLM-judged skill evolution is unprincipled. TTB keeps reward-proportional diversity; step importance + marginal flow drive retain/refine/prune/create; phase evolve when residual plateaus.

**Design rules:** `orchestration_action_select` / `ttb_residual` / `step_importance` / `skill_marginal_flow` / `skill_curation_decide` / `phase_evolve_gate`. No TTB train loop on core. Proxies only.

---

## 148. ProcMEM procedural memory via non-parametric PPO (v6.6)

**Paper:** *ProcMEM: Learning Reusable Procedural Memory from Experience via Non-Parametric PPO for LLM Agents*, arXiv:2602.01869 (2026).

**Claim:** Episodic narratives are not reusable procedures. Formalize Skills as activation/execution/termination (Skill-MDP), refine via semantic gradients, admit only inside a PPO-style trust region, maintain by freq×gain.

**Design rules:** `define_skill_triplet` / `skill_select_gate` / `skill_terminate_check` / `semantic_gradient_candidate` / `ppo_gate_verify` / `skill_score_maintain`. No weight updates. Proxies only.

---

## 149. MemRL value-aware episodic retrieval (v6.6)

**Paper:** *MemRL: Self-Evolving Agents via Runtime Reinforcement Learning on Episodic Memory*, arXiv:2601.03192 (2026).

**Claim:** Similar ≠ useful. Store Intent-Experience-Utility, retrieve in two phases (semantic then Q), update utilities via Bellman backup at runtime — frozen LLM, plastic memory.

**Design rules:** `ieu_record` / `two_phase_retrieve` / `utility_q_update` / `value_aware_select` / `semantic_vs_utility_warn`. Proxies only.

---

## 150. EvolveR experience-driven lifecycle (v6.7)

**Paper:** *EvolveR: Self-Evolving LLM Agents through an Experience-Driven Lifecycle*, arXiv:2510.16079 (2025).

**Claim:** Raw trajectory recall does not abstract. Offline distill success/failure principles (NL + triples), dedupe/merge, score by succ/use, prune; online `search_experience` / `search_knowledge` / answer; offline freezes policy.

**Design rules:** `distill_principle` / `principle_dedupe_plan` / `principle_metric_score` / `search_experience_action` / `lifecycle_phase_gate` / `prune_low_score_principles`. No GRPO on core. Proxies only.

---

## 151. AgentEvolver self-question / navigate / attribute (v6.7)

**Paper:** *AgentEvolver: Towards Efficient Self-Evolving Agent System*, arXiv:2511.10395 (2025).

**Claim:** Handcrafted tasks and sparse rewards waste RL. Self-question synthesizes tasks from exploration; when/content experiences guide mixed rollouts; self-attribute distributes outcome credit by step scores; curiosity prefers novel states under budget.

**Design rules:** `self_question_task` / `experience_when_content` / `mixed_rollout_split` / `attribute_step_credit` / `curiosity_explore_plan`. Proxies only.

---

## 152. SkillWeaver API skill discovery (v6.8)

**Paper:** *SkillWeaver: Web Agents can Self-Improve by Discovering and Honing Skills*, arXiv:2504.07079 (2025).

**Claim:** Web agents lack procedural abstraction. Propose short-horizon skills, practice, distill Playwright-style APIs, hone via unit tests, grow a plug-and-play library; strong-agent APIs transfer to weaker agents.

**Design rules:** `propose_skill` / `practice_skill_run` / `distill_skill_api` / `hone_skill_api` / `skill_library_register` / `transfer_skill_gate`. No browser on core. Proxies only.

---

## 153. Compositional skill routing + SAD (v6.8)

**Paper:** *Compositional Skill Routing for LLM Agents: Decompose, Retrieve, and Compose*, arXiv:2606.18051 (2026).

**Claim:** Decomposition granularity is the bottleneck for multi-skill plans. Decompose → retrieve → compose DAG; Skill-Aware Decomposition feeds retrieved skill names back to re-decompose; DA match when step count equals expected skills.

**Design rules:** `decompose_task_steps` / `retrieve_skills_for_steps` / `compose_skill_dag` / `sad_feedback_loop` / `granularity_match_check`. Proxies only.

---

## 154. Absolute Zero Reasoner self-play (v6.9)

**Paper:** *Absolute Zero: Reinforced Self-play Reasoning with Zero Data*, arXiv:2505.03335 (2025).

**Claim:** Even “zero” RLVR still needs human QA sets. One model proposes and solves induction/abduction/deduction code tasks; learnability reward prefers neither trivial nor impossible; executor is the unified verifier.

**Design rules:** `propose_reasoning_task` / `validate_task_structure` / `learnability_reward` / `solve_reward` / `abszero_joint_objective` / `executor_verify_gate`. No train loop on core. Proxies only.

---

## 155. R-Zero Challenger–Solver co-evolution (v6.9)

**Paper:** *R-Zero: Self-Evolving Reasoning LLM from Zero Data*, arXiv:2508.05004 (2025).

**Claim:** Challenger is rewarded when Solver accuracy ≈ 50%; majority-vote pseudo-labels; keep only the informative band; Solver gets binary reward; rounds alternate Challenger then Solver.

**Design rules:** `challenger_propose` / `uncertainty_reward` / `majority_vote_label` / `curriculum_band_filter` / `solver_binary_reward` / `coevolve_round_plan`. Proxies only.

---

## 156. ECHO selective turn memory (v7.0)

**Paper:** *ECHO: Prune to Act, Trace to Learn with Selective Turn Memory in Agentic RL*, arXiv:2606.31650 (2026).

**Claim:** Rolling summaries collapse provenance. ECHO stores each completed turn as a source-indexed memory; when the budget binds, the policy selects records and reconstructs context; the same indices route positive outcome credit.

**Design rules:** `write_turn_memory` / `select_turn_memories` / `reconstruct_policy_context` / `provenance_credit_mask` / `history_collapse_gate` / `budget_binding_check`. Proxies only.

---

## 157. Agent0 tool-aware curriculum–executor (v7.0)

**Paper:** *Agent0: Unleashing Self-Evolving Agents from Zero Data via Tool-Integrated Reasoning*, arXiv:2511.16043 (2025).

**Claim:** Curriculum agent proposes frontier tasks rewarded by executor uncertainty + tool use; executor trains on an informative consistency band; tool success pressures harder curricula.

**Design rules:** `curriculum_propose_task` / `tool_use_reward` / `curriculum_reward` / `executor_frontier_filter` / `tool_aware_pressure` / `symbiotic_round_plan`. Proxies only.

---

## 158. Multi-Agent Evolve triad (v7.1)

**Paper:** *Multi-Agent Evolve: LLM Self-Improve through Co-evolution*, arXiv:2510.23595 (2025).

**Claim:** Absolute Zero–style methods need grounded executors. MAE uses Proposer–Solver–Judge from one backbone so general-domain Q&A can self-reward: Judge scores quality and correctness; Proposer gets difficulty bonus when Solver fails.

**Design rules:** `mae_propose_question` / `mae_solve_attempt` / `mae_judge_score` / `mae_proposer_reward` / `mae_quality_filter` / `mae_triad_round_plan`. Proxies only.

---

## 159. SAGE Challenger–Planner–Solver–Critic (v7.1)

**Paper:** *SAGE: Multi-Agent Self-Evolution for LLM Reasoning*, arXiv:2603.15255 (2026).

**Claim:** Self-play without planning drifts. SAGE adds an explicit Planner and a Critic that filters questions and plans; difficulty jumps beyond a threshold are rejected as curriculum drift.

**Design rules:** `sage_challenge_task` / `sage_plan_steps` / `sage_solve_with_plan` / `sage_critic_filter` / `sage_drift_gate` / `sage_closed_loop_round`. Proxies only.

---

## 160. MemGen generative latent memory (v7.2)

**Paper:** *MemGen: Weaving Generative Latent Memory for Self-Evolving Agents*, arXiv:2509.24704 (2025).

**Claim:** Parametric and retrieval memory miss the interweaving of thought and recollection. A trigger decides when to invoke; a weaver synthesizes latent tokens; the reasoner stays frozen while the weaver absorbs experience; faculties (planning/procedural/working) emerge without explicit supervision.

**Design rules:** `memory_trigger_decide` / `weave_latent_memory` / `interweave_cycle_plan` / `faculty_classify` / `weaver_only_update_gate` / `sparse_invoke_penalty`. Proxies only.

---

## 161. Metis dual text/code memory (v7.2)

**Paper:** *Metis: Bridging Text and Code Memory for Self-Evolving Agents*, arXiv:2606.24151 (2026).

**Claim:** Text and code memories trade off construction cost, efficiency, and transfer. Metis stores plans/facts/pitfalls as text and crystallizes only recurring plans into tools; facts and pitfalls stay textual.

**Design rules:** `text_experience_store` / `crystallize_plan_to_tool` / `dual_retrieve` / `representation_tradeoff` / `promote_kind_gate` / `metis_loop_plan`. Proxies only.

---

## 162. SAMULE multi-level reflection (v7.3)

**Paper:** *SAMULE: Self-Learning Agents Enhanced by Multi-level Reflection*, arXiv:2509.20562 (2025).

**Claim:** Success-only reflections are weak. SAMULE synthesizes micro (single trajectory), meso (intra-task error taxonomy), and macro (inter-task transfer) reflections; foresight compares predicted vs actual user responses; learning prefers failures.

**Design rules:** `single_trajectory_reflect` / `intra_task_taxonomy` / `inter_task_transfer` / `foresight_reflect` / `failure_centric_gate` / `merge_reflections`. Proxies only.

---

## 163. LIVE-EVO online memory evolution (v7.3)

**Paper:** *Live-Evo: Online Evolution of Agentic Memory from Continuous Feedback*, arXiv:2602.02369 (2026).

**Claim:** Static train/test memory folds fail under live streams. LIVE-EVO keeps an Experience Bank and Meta-Guideline Bank; contrastive memory-on vs memory-off updates weights; stale experiences are forgotten.

**Design rules:** `experience_bank_record` / `meta_guideline_record` / `compile_task_guideline` / `update_experience_weight` / `forget_stale_experience` / `liveevo_online_round`. Proxies only.

---

## 164. Socratic-Zero Teacher–Solver–Generator (v7.4)

**Paper:** *Socratic-Zero: Bootstrapping Reasoning via Data-Free Agent Co-evolution*, arXiv:2509.24726 (2025).

**Claim:** Static synthesis cannot track model capability. Teacher crafts questions at Solver weaknesses; Solver learns from preference on success/fail; Generator distills Teacher strategy so curriculum scales from ~100 seeds.

**Design rules:** `socratic_teacher_craft` / `socratic_solver_preference` / `socratic_generator_distill` / `socratic_seed_bootstrap` / `socratic_weakness_target` / `socratic_closed_loop`. Proxies only.

---

## 165. SPIRAL self-play RAE (v7.4)

**Paper:** *SPIRAL: Self-Play on Zero-Sum Games Incentivizes Reasoning via Multi-Agent Multi-Turn Reinforcement Learning*, arXiv:2506.24119 (2025).

**Claim:** Human QA sets are unnecessary when self-play generates an adaptive curriculum. Role-conditioned advantage estimation (reward − role EMA baseline) stabilizes multi-agent training; patterns (case-by-case, EV, pattern recognition) transfer to math.

**Design rules:** `spiral_self_play_match` / `spiral_rae_advantage` / `spiral_baseline_ema` / `spiral_transfer_pattern` / `spiral_opponent_strength` / `spiral_multi_game_plan`. Proxies only.

---

## 166. SMITH Shared Memory Integrated Tool Hub (v7.5)

**Paper:** *Unifying Dynamic Tool Creation and Cross-Task Experience Sharing through Cognitive Memory Architecture*, arXiv:2512.11303 (2025).

**Claim:** Tool creation and experience reuse are usually siloed. SMITH unifies them under procedural/semantic/episodic memory; tools are admitted only after sandbox pass; episodic retrieve uses semantic similarity; curriculum bands come from ensemble fail rates.

**Design rules:** `smith_store_memory` / `smith_create_tool` / `smith_retrieve_episode` / `smith_curriculum_difficulty` / `smith_tool_reuse_gate` / `smith_loop_plan`. Proxies only.

---

## 167. H-Mem hybrid tree–graph (v7.5)

**Paper:** *H-Mem: A Novel Memory Mechanism for Evolving and Retrieving Agent Memory via a Hybrid Structure*, arXiv:2605.15701 (2026).

**Claim:** Vector-, tree-, or graph-only indexes miss either temporal consolidation or multi-hop relations. H-Mem couples a temporal-semantic tree (STM→LTM) with an entity graph; retrieval decomposes queries and combines bottom-up tree hits with graph hops.

**Design rules:** `hmem_leaf_event` / `hmem_consolidate_nodes` / `hmem_link_entities` / `hmem_decompose_query` / `hmem_hybrid_retrieve` / `hmem_evolution_gate`. Proxies only. Distinct from H-MEM abstraction levels (arXiv:2507.22925).

---

## 168. HiMem episode/note hierarchy (v7.6)

**Paper:** *HiMem: Hierarchical Long-Term Memory for LLM Long-Horizon Agents*, arXiv:2601.06377 (2026).

**Claim:** Flat long-term stores struggle to bridge concrete events and stable knowledge under continuous dialogue. HiMem builds Episode Memory via topic-aware event–surprise segmentation and Note Memory via multi-stage extraction, links them hierarchically, supports hybrid vs best-effort retrieval, and treats retrieval failures as conflict-aware reconsolidation signals.

**Design rules:** `himem_segment_episode` / `himem_extract_note` / `himem_link_episode_note` / `himem_retrieve_strategy` / `himem_reconsolidate` / `himem_loop_plan`. Proxies only.

---

## 169. H-MEM abstraction-level index routing (v7.6)

**Paper:** *H-MEM: Hierarchical Memory for High-Efficiency Long-Term Reasoning in LLM Agents*, arXiv:2507.22925 (2025).

**Claim:** Unstructured vector recall over long histories is inefficient. H-MEM organizes memory into four semantic abstraction levels (section → subsection → subsubsection → content) and routes queries by descending the index only as needed.

**Design rules:** `hmeml_store_level` / `hmeml_route_query` / `hmeml_descend` / `hmeml_parent_link` / `hmeml_efficiency_score` / `hmeml_loop_plan`. Proxies only. Distinct from hybrid H-Mem (arXiv:2605.15701) in `hmem.py`.

---

## 170. HyperSkill hypergraph skill memory (v7.7)

**Paper:** *HyperSkill: Self-Evolving LLM Agents via Hypergraph-Structured Skill Memory*, arXiv:2608.16114 (2026).

**Claim:** Flat trajectory/skill stores lose n-ary associations among subtasks, skills, and outcomes. HyperSkill uses a hypergraph with subtask and skill nodes, trajectory hyperedges, dual-path retrieval, co-occurrence ranking, and structure-informed prune/merge maintenance.

**Design rules:** `hyperskill_add_subtask` / `hyperskill_add_skill` / `hyperskill_add_hyperedge` / `hyperskill_dual_path_retrieve` / `hyperskill_rank_skills` / `hyperskill_maintain_plan` / `hyperskill_loop_plan`. Proxies only.

---

## 171. DCPM dual-process cognitive memory (v7.7)

**Paper:** *Memory Beyond Recall: A Dual-Process Cognitive Memory System for Self-Evolving LLM Agents*, arXiv:2606.09483 (2026).

**Claim:** Single-surface recall collapses belief revision and cross-domain abstraction. DCPM separates a daytime System-1 writer (supersedes chains) from a nighttime System-2 engine (schema/intention induction and cross-domain collision → core schemas) over a capability hierarchy.

**Design rules:** `dcpm_day_write` / `dcpm_supersedes_chain` / `dcpm_night_induce` / `dcpm_cross_domain_collision` / `dcpm_hierarchy_level` / `dcpm_loop_plan`. Proxies only. Distinct from D-Mem quality gate (arXiv:2603.18631) in `roles.py`.

---

## 172. MemOS MemCube memory OS (v7.8)

**Paper:** *MemOS: A Memory OS for AI System*, arXiv:2507.03724 (2025); related MAG MemOS arXiv:2505.22101.

**Claim:** Parametric + activation + plaintext memories lack unified lifecycle control. MemOS elevates memory to a first-class resource via MemCubes with scheduling, lifecycle states, and compose/migrate/fuse transitions.

**Design rules:** `memos_create_cube` / `memos_schedule` / `memos_lifecycle` / `memos_compose` / `memos_migrate` / `memos_fuse_gate` / `memos_loop_plan`. Proxies only. No parameter writes on core.

---

## 173. SkillCraft Skill Mode (v7.8)

**Paper:** *SkillCraft: Can LLM Agents Learn to Use Tools Skillfully?*, arXiv:2603.00718 (2026).

**Claim:** Instance-level tool success under static tool sets misses reusable multi-step compositions. SkillCraft’s Skill Mode protocol (save/get/list/execute + coding verifier) lets agents cache verified skills and cut tokens dramatically on repetitive workflows.

**Design rules:** `skillcraft_save_skill` / `skillcraft_get_skill` / `skillcraft_list_skills` / `skillcraft_execute_skill` / `skillcraft_verify_skill` / `skillcraft_token_efficiency` / `skillcraft_loop_plan`. Proxies only. No live sandbox on core.

---

## 174. Continuum Memory Architecture (v7.9)

**Paper:** *Continuum Memory Architectures for Long-Horizon LLM Agents*, arXiv:2601.09913 (2026).

**Claim:** RAG treats memory as a stateless lookup table. CMA requires persistent mutable storage, selective retention, associative routing, temporal chaining, and consolidation — probed via knowledge updates, temporal association, associative recall, and contextual disambiguation.

**Design rules:** `cma_persist` / `cma_selective_retain` / `cma_associative_route` / `cma_temporal_chain` / `cma_consolidate` / `cma_probe_gate` / `cma_loop_plan`. Proxies only.

---

## 175. AgentFold proactive context folding (v7.9)

**Paper:** *AgentFold: Long-Horizon Web Agents with Proactive Context Management*, arXiv:2510.24699 (2025).

**Claim:** Append-only ReAct saturates context; fixed full-history summaries lose details. AgentFold treats context as a cognitive workspace with fold commands — granular condensation of the latest step or deep consolidation of multi-step ranges — keeping long horizons under a soft token budget.

**Design rules:** `agentfold_workspace_split` / `agentfold_fold_command` / `agentfold_granular_condense` / `agentfold_deep_consolidate` / `agentfold_context_budget` / `agentfold_loop_plan`. Proxies only.

---

## 176. MemEngine modular memory library (v8.0)

**Paper:** *MemEngine: A Unified and Modular Library for Developing Advanced Memory of LLM-based Agents*, arXiv:2505.02099 (WWW 2025).

**Claim:** Research memory models lack a shared pluggable stack. MemEngine layers functions → operations → models with config, reflection/optimize ops, and agent-compatible registration.

**Design rules:** `memengine_register_function` / `memengine_compose_operation` / `memengine_bind_model` / `memengine_config_set` / `memengine_reflect_plan` / `memengine_pluggable` / `memengine_loop_plan`. Proxies only.

---

## 177. SimpleMem semantic lossless compression (v8.0)

**Paper:** *SimpleMem: Efficient Lifelong Memory for LLM Agents*, arXiv:2601.02553 (2026).

**Claim:** Raw-log and lightly structured stores waste tokens and leave referential ambiguity. SimpleMem compresses into multi-view units, synthesizes related facts online, and plans retrieval depth from intent complexity — large F1 gains at far lower inference token cost.

**Design rules:** `simplemem_compress` / `simplemem_synthesize` / `simplemem_intent_scope` / `simplemem_multiview_index` / `simplemem_token_ratio` / `simplemem_loop_plan`. Proxies only.

---

## 178. O-Mem active user profiling (v8.1)

**Paper:** *O-Mem: Omni Memory System for Personalized, Long Horizon, Self-Evolving Agents*, arXiv:2511.13593 (2025).

**Claim:** Semantic-group retrieval alone misses critical user signals and injects noise. O-Mem actively extracts and updates persona attributes and event records, then retrieves hierarchically across persona and topic channels while scaling memory-time with interaction length.

**Design rules:** `omem_extract_persona` / `omem_update_event` / `omem_hierarchy_retrieve` / `omem_profile_gate` / `omem_scale_memory_time` / `omem_loop_plan`. Proxies only.

---

## 179. Mandol agglomerative memory (v8.1)

**Paper:** *Mandol: An Agglomerative Agent Memory System for Long-Term Conversations*, arXiv:2606.29778 (2026).

**Claim:** Heterogeneous vector+graph DBs fragment memory and inflate cross-DB I/O. Mandol agglomerates basic units into abstract semantic graphs via SemanticMap/SemanticGraph, hybrid retrieve without cross-DB boundaries, query-adaptive routing, and token-constrained context — all without LLMs on the retrieve path.

**Design rules:** `mandol_basic_unit` / `mandol_agglomerate` / `mandol_semantic_map_put` / `mandol_hybrid_retrieve` / `mandol_query_route` / `mandol_token_budget` / `mandol_loop_plan`. Proxies only.

---

## 180. Memanto typed semantic memory (v8.2)

**Paper:** *Memanto: Typed Semantic Memory with Information-Theoretic Retrieval for Long-Horizon Agents*, arXiv:2604.22085 (2026).

**Claim:** Hybrid graph+vector stacks impose LLM extraction, schema maintenance, and multi-query pipelines. Memanto uses a fixed typed category schema, automated conflict resolution, temporal versioning, and single-query information-theoretic retrieve with zero ingestion delay and sub-90ms soft latency.

**Design rules:** `memanto_store_typed` / `memanto_conflict_resolve` / `memanto_version` / `memanto_retrieve` / `memanto_latency_gate` / `memanto_loop_plan`. Proxies only.

---

## 181. Zep / Graphiti temporal knowledge graph (v8.2)

**Paper:** *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*, arXiv:2501.13956 (2025).

**Claim:** Static RAG cannot integrate ongoing conversation with structured business data over time. Zep’s Graphiti engine maintains a temporally-aware KG with bi-temporal stamps, entity links, and cross-session synthesis for enterprise long-horizon tasks.

**Design rules:** `zep_add_episode` / `zep_link_entities` / `zep_bitemporal` / `zep_synthesize` / `zep_cross_session` / `zep_loop_plan`. Proxies only. No live Graphiti broker on core.

---

## 182. MemGPT virtual context paging (v8.3)

**Paper:** *MemGPT: Towards LLMs as Operating Systems*, arXiv:2310.08560 (2023; Letta product lineage).

**Claim:** Fixed context windows force truncation. MemGPT treats the context as RAM and external recall/archival stores as disk, with explicit page-in/out tools and capacity flush warnings so agents manage their own working set.

**Design rules:** `memgpt_main_capacity` / `memgpt_page_out` / `memgpt_page_in` / `memgpt_recall_search` / `memgpt_archival_search` / `memgpt_loop_plan`. Proxies only. Distinct from MemoryOS segmented paging.

---

## 183. RippleMem associative recollection (v8.3)

**Paper:** *RippleMem: From Isolated Retrieval to Associative Recollection for Long-Term Agent Memory*, arXiv:2608.13334 (2026).

**Claim:** Flat retrieval returns isolated incomplete records; heavy graphs are costly. RippleMem stores episodic units on an entity-centric graph, seeds first-shot hits, then expands associatively so recollection gathers distributed evidence.

**Design rules:** `ripple_store_episode` / `ripple_link_entity` / `ripple_seed_retrieve` / `ripple_expand` / `ripple_recollect_gate` / `ripple_loop_plan`. Proxies only.

---

## 184. FluxMem connectivity-evolving memory (v8.4)

**Paper:** *Rethinking Memory as Continuously Evolving Connectivity* (FluxMem), arXiv:2605.28773 (2026).

**Claim:** Static repositories with fixed retrieval are brittle under feedback and task variation. FluxMem models memory as a heterogeneous graph and refines topology through connection formation, feedback refinement, and long-term consolidation (repair, prune, procedural circuits, maturity).

**Design rules:** `flux_connect_form` / `flux_feedback_refine` / `flux_consolidate` / `flux_repair_link` / `flux_prune_interference` / `flux_maturity_gate` / `flux_loop_plan`. Proxies only.

---

## 185. QUMem query-conditioned user-state (v8.4)

**Paper:** *QUMem: Personalized Memory for Query-Conditioned User-State Inference in LLM Agents*, arXiv:2608.16168 (2026).

**Claim:** Fixed boundaries and single top-k retrieval miss preference evolution. QUMem segments by semantic continuity, decomposes into factual/preference/insight memories, plans multi-query retrieval, and infers a temporally valid user state.

**Design rules:** `qumem_segment_episode` / `qumem_decompose` / `qumem_plan_queries` / `qumem_infer_user_state` / `qumem_temporal_valid` / `qumem_loop_plan`. Proxies only.

---

## 186. VikingMem Memory Base (v8.5)

**Paper:** *VikingMem: A Memory Base Management System for Stateful LLM-based Applications*, arXiv:2605.29640 (2026).

**Claim:** Naive RAG and rigid extractors fail across apps. VikingMem’s Memory Base uses an event–entity paradigm: selective events update persistent entities, topic timelines compress history, and time-weighted recall plus multi-vector rerank prioritize recent state.

**Design rules:** `viking_extract_event` / `viking_update_entity` / `viking_timeline_compress` / `viking_time_weighted_recall` / `viking_rerank` / `viking_loop_plan`. Proxies only. No VikingDB on core.

---

## 187. RecMem recurrence consolidation (v8.5)

**Paper:** *RecMem: Recurrence-based Memory Consolidation for Efficient and Effective Long-Running LLM Agents*, arXiv:2605.16045 (2026).

**Claim:** Eager LLM extraction on every turn wastes tokens. RecMem buffers interactions in a subconscious layer and consolidates to episodic/semantic memory only when semantic recurrence hits a threshold, then refines omitted facts.

**Design rules:** `recmem_buffer_subconscious` / `recmem_recurrence_gate` / `recmem_consolidate_episodic` / `recmem_semantic_refine` / `recmem_merge_retrieve` / `recmem_loop_plan`. Proxies only. No LLM on core write path.

---

## 188. MemoryBank Ebbinghaus companion memory (v8.6)

**Paper:** *MemoryBank: Enhancing Large Language Models with Long-Term Memory*, arXiv:2305.10250 (2023).

**Claim:** Sustained companions need summon, personality synthesis, and selective retention. MemoryBank updates memories with an Ebbinghaus-inspired forget/reinforce mechanism based on elapsed time and significance.

**Design rules:** `mbank_store_memory` / `mbank_summon` / `mbank_personality_synth` / `mbank_forget_curve` / `mbank_reinforce` / `mbank_loop_plan`. Proxies only. Fade plans report-only (no auto-delete).

---

## 189. RF-Mem recollection–familiarity retrieval (v8.6)

**Paper:** *Evoking User Memory: Personalizing LLM via Recollection-Familiarity Adaptive Retrieval* (RF-Mem), arXiv:2603.09250 (2026).

**Claim:** One-shot similarity retrieval misses deep episodic reconstruction. RF-Mem routes via familiarity (mean+entropy): high familiarity uses top-K; low familiarity activates recollection with cluster expansion and alpha-mix.

**Design rules:** `rfmem_familiarity_score` / `rfmem_path_route` / `rfmem_top_k_familiar` / `rfmem_recollect_expand` / `rfmem_alpha_mix` / `rfmem_loop_plan`. Proxies only.

---

## 190. AgeMem unified LTM/STM tool actions (v8.7)

**Paper:** *Agentic Memory: Learning Unified Long-Term and Short-Term Memory Management for Large Language Model Agents* (AgeMem), arXiv:2601.01885 (2026).

**Claim:** Separate LTM/STM controllers limit end-to-end optimization. AgeMem exposes store/retrieve/update/summarize/discard as tool actions inside the agent policy so the model decides what and when to manage memory.

**Design rules:** `agemem_ltm_store` / `agemem_stm_manage` / `agemem_retrieve` / `agemem_summarize` / `agemem_discard_plan` / `agemem_loop_plan`. Proxies only. No RL training on core; discard/summarize report-only.

---

## 191. MemGAS multi-granularity association (v8.7)

**Paper:** *From Single to Multi-Granularity: Toward Long-Term Memory Association and Selection of Conversational Agents* (MemGAS), arXiv:2505.19549 (2025).

**Claim:** Single-granularity segmentation is suboptimal. MemGAS builds multi-granularity units, associates via clustering, routes with an entropy-based selector, and filters retrieved candidates.

**Design rules:** `memgas_unit` / `memgas_associate` / `memgas_entropy_route` / `memgas_select_granularity` / `memgas_filter_plan` / `memgas_loop_plan`. Proxies only. No GMM/LLM on core.

---

## 192. MemWalker interactive summary-tree reading (v8.8)

**Paper:** *Walking Down the Memory Maze: Beyond Context Limit through Interactive Reading* (MemWalker), arXiv:2310.05029 (2023).

**Claim:** Fixed windows cannot ingest long documents in one pass. MemWalker builds a query-independent summary tree, then navigates from the root (child / revert) to gather leaf evidence under budget.

**Design rules:** `memwalker_segment` / `memwalker_build_node` / `memwalker_navigate` / `memwalker_gather` / `memwalker_path_gate` / `memwalker_loop_plan`. Proxies only. No LLM prompting on core.

---

## 193. MemGraphRAG three-layer global memory (v8.8)

**Paper:** *MemGraphRAG: Memory-based Multi-Agent System for Graph Retrieval-Augmented Generation*, arXiv:2606.00610 (2026).

**Claim:** Pipeline GraphRAG lacks shared global consistency. MemGraphRAG uses ontology/fact/passage memory with extract/detect/resolve agents, multilayer retrieve, and Personalized PageRank-style propagation.

**Design rules:** `mgr_store_layer` / `mgr_detect_conflict` / `mgr_resolve_plan` / `mgr_multilayer_retrieve` / `mgr_propagate` / `mgr_loop_plan`. Proxies only. Resolve plans report-only.

---

## 194. RAPTOR recursive tree-organized retrieval (v8.9)

**Paper:** *RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval*, arXiv:2401.18059 (2024).

**Claim:** Flat chunk RAG misses document-level abstraction. RAPTOR recursively embeds, clusters, and summarizes into a tree; query-time tree traversal or collapsed-tree retrieve integrates multi-level context.

**Design rules:** `raptor_embed_chunk` / `raptor_cluster` / `raptor_summarize_node` / `raptor_tree_traverse` / `raptor_collapsed_retrieve` / `raptor_loop_plan`. Proxies only. No LLM summarization on core.

---

## 195. LightRAG dual-level graph+vector RAG (v8.9)

**Paper:** *LightRAG: Simple and Fast Retrieval-Augmented Generation* (EMNLP 2025 Findings).

**Claim:** Heavy GraphRAG is slow to update. LightRAG indexes entities and relations with dual-level (low/high) retrieval, incremental updates, and fused graph+vector hits for faster, accurate RAG.

**Design rules:** `lightrag_index_entity` / `lightrag_index_relation` / `lightrag_dual_retrieve` / `lightrag_incremental_update` / `lightrag_graph_vector_fuse` / `lightrag_loop_plan`. Proxies only.

---

## 196. MemoRAG memory-clued retrieval (v9.0)

**Paper:** *MemoRAG: Moving towards Next-Gen RAG Via Memory-Inspired Knowledge Discovery*, arXiv:2409.05591 (TheWebConf 2025).

**Claim:** Query–passage matching fails on ambiguous needs. MemoRAG forms a global memory of the corpus, generates draft clues, and retrieves with those clues via a dual light-memory / expressive-generator system.

**Design rules:** `memorag_memorize` / `memorag_clue` / `memorag_retrieve_by_clue` / `memorag_dual_system` / `memorag_generate_plan` / `memorag_loop_plan`. Proxies only. No LLM on core.

---

## 197. PageIndex vectorless TOC navigation (v9.0)

**System:** PageIndex (VectifyAI, 2025) — vectorless, reasoning-based RAG over hierarchical document trees.

**Claim:** Chunk+vector RAG fragments long professional documents. PageIndex builds a TOC-like tree of natural sections and navigates by reasoning over titles/structure with traceable paths — no vector DB required on core.

**Design rules:** `pageindex_build_toc` / `pageindex_add_section` / `pageindex_reason_nav` / `pageindex_select_section` / `pageindex_trace_path` / `pageindex_loop_plan`. Proxies only.

---

## 198. Self-RAG on-demand retrieve + critique (v9.1)

**Paper:** *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*, arXiv:2310.11511 (ICLR 2024).

**Claim:** Indiscriminate RAG hurts versatility. Self-RAG decides when to retrieve, critiques relevance/support/utility via reflection tokens, and selects the best continuation.

**Design rules:** `selfrag_need_retrieve` / `selfrag_relevance_critique` / `selfrag_support_critique` / `selfrag_utility_critique` / `selfrag_select_best` / `selfrag_loop_plan`. Proxies only — not trained reflection tokens.

---

## 199. MemoBrain executive memory (v9.1)

**Paper:** *MemoBrain: Executive Memory as an Agentic Brain for Reasoning*, arXiv:2601.08079.

**Claim:** Long-horizon tool agents drown in passive context. MemoBrain builds a dependency-aware memory graph, prunes invalid steps, folds sub-trajectories, and flushes under a fixed budget while keeping a high-salience backbone.

**Design rules:** `memobrain_dep_edge` / `memobrain_prune_invalid` / `memobrain_fold_subtraj` / `memobrain_flush_budget` / `memobrain_salience_keep` / `memobrain_loop_plan`. Proxies only. Plans report-only; no auto-delete.

---

## 200. CRAG corrective retrieval (v9.2)

**Paper:** *Corrective Retrieval Augmented Generation*, arXiv:2401.15884.

**Claim:** RAG fails silently on bad retrieval. CRAG evaluates confidence and triggers Correct (refine), Incorrect (web fallback), or Ambiguous (blend), with decompose-then-recompose.

**Design rules:** `crag_evaluate_retrieval` / `crag_correct_refine` / `crag_web_fallback_plan` / `crag_ambiguous_blend` / `crag_action_select` / `crag_loop_plan`. Proxies only. No live web on core.

---

## 201. HyDE hypothetical document embeddings (v9.2)

**Paper:** *Precise Zero-Shot Dense Retrieval without Relevance Labels* (HyDE), arXiv:2212.10496 (ACL 2023).

**Claim:** Query–document mismatch hurts zero-shot dense retrieval. HyDE generates a hypothetical answer doc, encodes it, retrieves real neighbors, and grounds via a dense bottleneck that filters hallucinations.

**Design rules:** `hyde_hypothetical_doc` / `hyde_encode_proxy` / `hyde_retrieve_by_hyp` / `hyde_filter_hallucination` / `hyde_ground_corpus` / `hyde_loop_plan`. Proxies only — not InstructGPT/Contriever.

---

## 202. Adaptive-RAG complexity routing (v9.3)

**Paper:** *Adaptive-RAG: Learning to Adapt Retrieval-Augmented Large Language Models through Question Complexity*, arXiv:2403.14403 (NAACL 2024).

**Claim:** Fixed RAG strategy wastes compute on simple queries and under-serves multi-hop ones. Adaptive-RAG classifies complexity and routes to no-retrieval, single-step, or multi-step retrieval.

**Design rules:** `adaptiverag_classify_complexity` / `adaptiverag_select_strategy` / `adaptiverag_no_retrieve` / `adaptiverag_single_step` / `adaptiverag_multi_step` / `adaptiverag_loop_plan`. Proxies only.

---

## 203. FLARE forward-looking active retrieval (v9.3)

**Paper:** *Active Retrieval Augmented Generation* (FLARE), arXiv:2305.06983 (EMNLP 2023).

**Claim:** One-shot retrieve-and-generate fails on long-form text. FLARE anticipates the next sentence, retrieves when confidence is low, and regenerates with fresh docs.

**Design rules:** `flare_anticipate_sentence` / `flare_low_confidence` / `flare_retrieve_for_regen` / `flare_regenerate_sentence` / `flare_active_step` / `flare_loop_plan`. Proxies only. Regen report-only.

---

## 204. GraphReader graph exploration agent (v9.4)

**Paper:** *GraphReader: Building Graph-based Agent to Enhance Long-Context Abilities of Large Language Models*, arXiv:2406.14550.

**Claim:** Long contexts overwhelm fixed windows. GraphReader structures text as a graph and explores coarse-to-fine via read node/neighbors, notes, and reflection until enough evidence.

**Design rules:** `graphreader_build_node` / `graphreader_read_node` / `graphreader_read_neighbors` / `graphreader_note_insight` / `graphreader_reflect_plan` / `graphreader_loop_plan`. Proxies only.

---

## 205. G-Retriever PCST subgraph RAG (v9.4)

**Paper:** *G-Retriever: Retrieval-Augmented Generation for Textual Graph Understanding and Question Answering*, arXiv:2402.07630 (NeurIPS 2024).

**Claim:** Chat-with-graph needs structure-aware RAG. G-Retriever assigns node prizes, selects a Prize-Collecting Steiner Tree subgraph, soft-prompts the LLM, and highlights relevant parts.

**Design rules:** `gretriever_node_prize` / `gretriever_pcst_select` / `gretriever_subgraph` / `gretriever_soft_prompt_plan` / `gretriever_highlight` / `gretriever_loop_plan`. Proxies only — not a real PCST solver/GNN.

---

## 206. RQ-RAG query refine (v9.5)

**Paper:** *RQ-RAG: Learning to Refine Queries for Retrieval Augmented Generation*, arXiv:2404.00610.

**Claim:** Raw user queries are often ambiguous or multi-hop. RQ-RAG explicitly rewrites, decomposes, or disambiguates before retrieval.

**Design rules:** `rqrag_rewrite` / `rqrag_decompose` / `rqrag_disambiguate` / `rqrag_refine_mode` / `rqrag_retrieve_refined` / `rqrag_loop_plan`. Proxies only.

---

## 207. IRCoT interleaved CoT retrieval (v9.5)

**Paper:** *Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions*, arXiv:2212.10509 (ACL 2023).

**Claim:** One-shot retrieve-and-read fails multi-step QA. IRCoT interleaves CoT sentences with retrieval so each step guides the next search and retrieved docs improve CoT.

**Design rules:** `ircot_cot_step` / `ircot_retrieve_guided` / `ircot_interleave` / `ircot_answer_ready` / `ircot_hallucination_check` / `ircot_loop_plan`. Proxies only. Answer-ready report-only.

---

## 208. REPLUG black-box retrieve-and-plug (v9.6)

**Paper:** *REPLUG: Retrieval-Augmented Black-Box Language Models*, arXiv:2301.12652 (NAACL 2024).

**Claim:** Large LMs should stay frozen. REPLUG retrieves docs, prepends each to the input, ensembles parallel forwards, and can supervise the retriever from LM likelihood gains.

**Design rules:** `replug_retrieve_docs` / `replug_prepend_doc` / `replug_ensemble_probs` / `replug_supervise_retriever` / `replug_blackbox_forward` / `replug_loop_plan`. Proxies only.

---

## 209. Iter-RetGen iterative retrieve–generate synergy (v9.6)

**Paper:** *Enhancing Retrieval-Augmented Large Language Models with Iterative Retrieval-Generation Synergy* (Iter-RetGen), arXiv:2305.15294 (EMNLP 2023 Findings).

**Claim:** One retrieve-then-generate pass under-retrieves complex needs. Iter-RetGen uses the draft answer as context for the next retrieve, iterates, and can adapt the retriever.

**Design rules:** `iterretgen_generate` / `iterretgen_use_as_query` / `iterretgen_retrieve_next` / `iterretgen_iterate` / `iterretgen_adapt_retriever` / `iterretgen_loop_plan`. Proxies only. Adapt report-only.

---

## 210. PlanRAG plan-then-retrieve Decision QA (v9.7)

**Paper:** *PlanRAG: A Plan-then-Retrieval Augmented Generation for Generative Large Language Models as Decision Makers*, arXiv:2406.12430.

**Claim:** Decision QA needs analysis before answer. PlanRAG plans first, emits data-analysis queries, retrieves, optionally replans, then decides.

**Design rules:** `planrag_make_plan` / `planrag_analysis_query` / `planrag_retrieve_data` / `planrag_replan` / `planrag_decide` / `planrag_loop_plan`. Proxies only. No live SQL/Cypher on core.

---

## 211. Rewrite-Retrieve-Read (v9.7)

**Paper:** *Query Rewriting for Retrieval-Augmented Large Language Models* (Rewrite-Retrieve-Read), arXiv:2305.14283.

**Claim:** Raw queries mismatch needed knowledge. RRR rewrites first, then retrieves and reads with a frozen LLM; reader feedback can train a small rewriter (plan-only here).

**Design rules:** `rrr_rewrite_query` / `rrr_retrieve` / `rrr_read` / `rrr_reader_feedback` / `rrr_train_rewriter_plan` / `rrr_loop_plan`. Proxies only. Distinct from RQ-RAG refine modes.

---

## 212. DSP Demonstrate–Search–Predict (v9.8)

**Paper:** *Demonstrate–Search–Predict: Composing retrieval and language models for knowledge-intensive NLP*, arXiv:2212.14024.

**Claim:** Simple retrieve-then-read underuses frozen LM+RM. DSP programs bootstrap demos, search, and predict in composable multi-hop pipelines.

**Design rules:** `dsp_bootstrap_demo` / `dsp_search` / `dsp_predict` / `dsp_compose_program` / `dsp_multihop_hop` / `dsp_loop_plan`. Proxies only — not DSPy product.

---

## 213. GenRead generate-then-read (v9.8)

**Paper:** *Generate rather than Retrieve: Large Language Models are Strong Context Generators* (GenRead), arXiv:2302.08468.

**Claim:** Retrievers can miss; LLMs can generate useful context first. GenRead generates context, optionally grounds with retrieve, answers, and can hybridize.

**Design rules:** `genread_generate_context` / `genread_ground_optional` / `genread_answer` / `genread_compare_retrieve` / `genread_hybrid` / `genread_loop_plan`. Proxies only.

---

## 214. Self-Ask follow-up questions (v9.9)

**Paper:** *Measuring and Narrowing the Compositionality Gap in Language Models* (Self-Ask), arXiv:2210.04695.

**Claim:** Multi-hop QA needs intermediate questions. Self-Ask emits follow-ups, intercepts them for search, then composes the final answer.

**Design rules:** `selfask_followup` / `selfask_search_intercept` / `selfask_compose_answer` / `selfask_stop` / `selfask_demo_prompt` / `selfask_loop_plan`. Proxies only.

---

## 215. ReAct thought–act–observe (v9.9)

**Paper:** *ReAct: Synergizing Reasoning and Acting in Language Models*, arXiv:2210.03629.

**Claim:** Reasoning and acting should interleave. ReAct produces Thought → Action → Observe trajectories, finishing when grounded enough.

**Design rules:** `react_thought` / `react_action` / `react_observe` / `react_finish` / `react_trajectory` / `react_loop_plan`. Proxies only. No live env APIs on core.

---

## 216. Think-on-Graph beam explore (v10.0)

**Paper:** *Think-on-Graph: Deep and Responsible Reasoning of Large Language Model on Knowledge Graph*, arXiv:2307.07697.

**Claim:** Treat the LLM as an agent that beam-searches a KG: explore neighbors, prune paths, score, answer from retained paths — training-free LLM⊗KG.

**Design rules:** `tog_init_entity` / `tog_explore_neighbors` / `tog_beam_prune` / `tog_path_score` / `tog_answer_from_paths` / `tog_loop_plan`. Proxies only.

---

## 217. Toolformer API call selection (v10.0)

**Paper:** *Toolformer: Language Models Can Teach Themselves to Use Tools*, arXiv:2302.04761.

**Claim:** Models should decide which APIs to call, when, with what args, and how to fold results into prediction — from few demos, self-supervised filter.

**Design rules:** `tf_api_candidate` / `tf_filter_call` / `tf_execute_proxy` / `tf_incorporate_result` / `tf_demo_apis` / `tf_loop_plan`. Proxies only. No live network on core.

---

## 218. Reflexion verbal reinforcement (v10.1)

**Paper:** *Reflexion: Language Agents with Verbal Reinforcement Learning*, arXiv:2303.11366.

**Claim:** Agents improve across trials via linguistic feedback stored in episodic memory — not weight updates.

**Design rules:** `rx_trial_run` / `rx_evaluate` / `rx_verbal_reflect` / `rx_memory_store` / `rx_next_trial` / `rx_loop_plan`. Proxies only.

---

## 219. Self-Consistency sample-and-vote (v10.1)

**Paper:** *Self-Consistency Improves Chain of Thought Reasoning in Language Models*, arXiv:2203.11171.

**Claim:** Sample diverse CoT paths, then majority-vote / marginalize answers instead of greedy decode.

**Design rules:** `sc_sample_path` / `sc_collect_answers` / `sc_majority_vote` / `sc_marginalize` / `sc_temperature` / `sc_loop_plan`. Proxies only.

---

## 220. Tree of Thoughts deliberate search (v10.2)

**Paper:** *Tree of Thoughts: Deliberate Problem Solving with Large Language Models*, arXiv:2305.10601.

**Claim:** Explore a tree of intermediate “thoughts” with evaluate / expand / backtrack instead of left-to-right token greed.

**Design rules:** `tot_propose` / `tot_evaluate` / `tot_expand` / `tot_backtrack` / `tot_select_best` / `tot_loop_plan`. Proxies only.

---

## 221. Least-to-Most decompose-then-solve (v10.2)

**Paper:** *Least-to-Most Prompting Enables Complex Reasoning in Large Language Models*, arXiv:2205.10625.

**Claim:** Break hard problems into easier subproblems; solve in order; carry answers forward for easy-to-hard generalization.

**Design rules:** `ltm_decompose` / `ltm_solve_sub` / `ltm_carry_forward` / `ltm_compose_final` / `ltm_easy_to_hard` / `ltm_loop_plan`. Proxies only.

---

## 222. Graph of Thoughts DAG reasoning (v10.3)

**Paper:** *Graph of Thoughts: Solving Elaborate Problems with Large Language Models*, arXiv:2308.09687.

**Claim:** Model LLM thoughts as an arbitrary graph — aggregate, feedback loops, score — beyond trees/chains.

**Design rules:** `got_add_thought` / `got_link` / `got_aggregate` / `got_feedback` / `got_score_graph` / `got_loop_plan`. Proxies only.

---

## 223. Program of Thoughts code+interpreter (v10.3)

**Paper:** *Program of Thoughts Prompting: Disentangling Computation from Reasoning for Numerical Reasoning Tasks*, arXiv:2211.12588.

**Claim:** Express reasoning as a program; offload computation to an interpreter so the model does not arithmetic-hallucinate.

**Design rules:** `pot_emit_program` / `pot_sandbox_run` / `pot_read_result` / `pot_self_consistency` / `pot_disentangle` / `pot_loop_plan`. Proxies only. Core never executes untrusted code.

---

## 224. Algorithm of Thoughts in-context search (v10.4)

**Paper:** *Algorithm of Thoughts: Enhancing Exploration of Ideas in Large Language Models*, arXiv:2308.10379.

**Claim:** Encode the search algorithm in-context so one (or few) queries explore subtrees with tunnel-vision pruning — fewer tokens than multi-query ToT.

**Design rules:** `aot_load_algorithm` / `aot_explore_subtree` / `aot_tunnel_vision` / `aot_query_budget` / `aot_surpass_algo` / `aot_loop_plan`. Proxies only.

---

## 225. Reasoning via Planning (RAP) world-model MCTS (v10.4)

**Paper:** *Reasoning with Language Model is Planning with World Model*, arXiv:2305.14992.

**Claim:** Use the LLM as world model + agent; MCTS expands, rewards, selects paths with explore/exploit balance.

**Design rules:** `rap_world_state` / `rap_expand` / `rap_reward` / `rap_select_path` / `rap_balance` / `rap_loop_plan`. Proxies only. Distinct from RAPTOR.

---

## 226. Skeleton-of-Thought parallel expand (v10.5)

**Paper:** *Skeleton-of-Thought: Prompting LLMs for Efficient Parallel Generation*, arXiv:2307.15337.

**Claim:** Emit a skeleton first, then expand points in parallel to cut sequential decode latency; optional router gates when SoT applies.

**Design rules:** `sot_emit_skeleton` / `sot_extract_points` / `sot_parallel_expand` / `sot_router` / `sot_latency_gain` / `sot_loop_plan`. Proxies only.

---

## 227. Buffer of Thoughts meta-buffer (v10.5)

**Paper:** *Buffer of Thoughts: Thought-Augmented Reasoning with Large Language Models*, arXiv:2406.04271.

**Claim:** Distill reusable thought-templates into a meta-buffer; retrieve and instantiate per problem; buffer-manager grows capacity cheaper than multi-query ToT/GoT.

**Design rules:** `bot_distill_template` / `bot_retrieve_template` / `bot_instantiate` / `bot_buffer_update` / `bot_cost_ratio` / `bot_loop_plan`. Proxies only.

---

## 228. Self-Discover structure composition (v10.6)

**Paper:** *Self-Discover: Large Language Models Self-Compose Reasoning Structures*, arXiv:2402.03620.

**Claim:** Select atomic reasoning modules, adapt, implement a JSON structure once per task, then fill it per instance — far fewer calls than self-consistency.

**Design rules:** `sd_select_modules` / `sd_adapt` / `sd_implement` / `sd_apply_instance` / `sd_compute_ratio` / `sd_loop_plan`. Proxies only.

---

## 229. Meta-Prompting conductor+experts (v10.6)

**Paper:** *Meta-Prompting: Enhancing Language Models with Task-Agnostic Scaffolding*, arXiv:2401.12954.

**Claim:** One conductor LM breaks tasks, assigns expert personas, oversees history, and verifies — task-agnostic scaffolding.

**Design rules:** `mp_break_task` / `mp_assign_expert` / `mp_oversee` / `mp_verify` / `mp_task_agnostic` / `mp_loop_plan`. Proxies only.

---

## 230. Quiet-STaR think-before-speak (v10.7)

**Paper:** *Quiet-STaR: Language Models Can Teach Themselves to Think Before Speaking*, arXiv:2403.09629.

**Claim:** Generate internal thoughts at each token (with start/end markers and a mix head) so hard tokens and zero-shot QA improve without task fine-tuning.

**Design rules:** `qs_thought_bounds` / `qs_parallel_sample` / `qs_mix_head` / `qs_hard_token_aid` / `qs_zero_shot_flag` / `qs_loop_plan`. Proxies only.

---

## 231. Decomposed Prompting modular handlers (v10.7)

**Paper:** *Decomposed Prompting: A Modular Approach for Solving Complex Tasks*, arXiv:2210.02406.

**Claim:** Decompose into a shared library of sub-task handlers; recurse or swap symbolic modules — modular, not Least-to-Most sequential carry.

**Design rules:** `dep_decompose` / `dep_delegate` / `dep_recurse` / `dep_swap_symbolic` / `dep_library_size` / `dep_loop_plan`. Proxies only.

---

## 232. STaR self-taught rationale bootstrap (v10.8)

**Paper:** *STaR: Self-Taught Reasoner Bootstrapping Reasoning With Reasoning*, arXiv:2203.14465.

**Claim:** Generate rationales, keep correct ones, rationalize failures given the answer, fine-tune, repeat — bootstrap from few rationale seeds. Distinct from Quiet-STaR.

**Design rules:** `star_generate` / `star_filter_correct` / `star_rationalize` / `star_finetune_proxy` / `star_bootstrap_round` / `star_loop_plan`. Proxies only.

---

## 233. Cumulative Reasoning proposer/verifier/reporter (v10.8)

**Paper:** *Cumulative Reasoning with Large Language Models*, arXiv:2308.04371.

**Claim:** Orchestrate proposer, verifier, and reporter roles; accumulate verified steps into a compiled solution.

**Design rules:** `cr_propose` / `cr_verify` / `cr_accumulate` / `cr_report` / `cr_roles` / `cr_loop_plan`. Proxies only.

---

## 234. Plan-and-Solve zero-shot CoT (v10.9)

**Paper:** *Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models*, arXiv:2305.04091.

**Claim:** First plan subtasks, then execute; PS+ adds variable extraction and calculation guards to cut missing-step and calc errors. Distinct from PlanRAG.

**Design rules:** `ps_devise_plan` / `ps_execute` / `ps_plus_extract` / `ps_calc_guard` / `ps_missing_step_fix` / `ps_loop_plan`. Proxies only.

---

## 235. Progressive-Hint Prompting (v10.9)

**Paper:** *Progressive-Hint Prompting Improves Reasoning in Large Language Models*, arXiv:2304.09797.

**Claim:** Use prior answers as hints in follow-up rounds; stop when consecutive answers stabilize; orthogonal to CoT and self-consistency.

**Design rules:** `php_base_answer` / `php_emit_hint` / `php_reask` / `php_stable_stop` / `php_combine_sc` / `php_loop_plan`. Proxies only.

---

## 236. AgentCoder multi-agent code generation (v11.0)

**Paper:** *AgentCoder: Multi-Agent-based Code Generation with Iterative Testing and Optimisation*, arXiv:2312.13010.

**Claim:** Separate programmer, test designer, and test executor agents; executor feedback drives programmer refinement until tests pass.

**Design rules:** `ac_programmer` / `ac_test_designer` / `ac_test_executor` / `ac_refine` / `ac_pass_gate` / `ac_loop_plan`. Proxies only — no real exec.

---

## 237. PAL — Program-aided Language Models (v11.0)

**Paper:** *PAL: Program-aided Language Models*, arXiv:2211.10435.

**Claim:** LLM emits a program as intermediate reasoning; a runtime interpreter solves; LLM only decomposes. Distinct from Program of Thoughts (`pot_*`).

**Design rules:** `pal_emit_program` / `pal_offload_solve` / `pal_read_answer` / `pal_decompose_only` / `pal_vs_cot` / `pal_loop_plan`. Proxies only — never real exec on core.

---

## 238. Faithful Chain-of-Thought (v11.1)

**Paper:** *Faithful Chain-of-Thought Reasoning*, arXiv:2301.13379.

**Claim:** Translate NL → symbolic chain, then deterministic solve so the chain faithfully explains the answer. Distinct from PAL / PoT.

**Design rules:** `fcot_translate` / `fcot_solve` / `fcot_faithfulness` / `fcot_interleave` / `fcot_vs_cot` / `fcot_loop_plan`. Proxies only.

---

## 239. Language Agent Tree Search — LATS (v11.1)

**Paper:** *Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models*, arXiv:2310.04406.

**Claim:** MCTS-style expand/value/reflect/select with environment feedback; LM as agent, value, and optimizer. Distinct from RAP (`rap_*`).

**Design rules:** `lats_expand` / `lats_value` / `lats_reflect` / `lats_select` / `lats_env_feedback` / `lats_loop_plan`. Proxies only.

---

## 240. Voyager skill library + curriculum (v11.2)

**Paper:** *Voyager: An Open-Ended Embodied Agent with Large Language Models*, arXiv:2305.16291.

**Claim:** Automatic curriculum, ever-growing skill library (store/retrieve), iterative self-verification; compositional lifelong skills. Proxies only — no Minecraft.

**Design rules:** `voy_curriculum` / `voy_skill_store` / `voy_skill_retrieve` / `voy_self_verify` / `voy_compose` / `voy_loop_plan`. Proxies only.

---

## 241. ReWOO — Reasoning WithOut Observation (v11.2)

**Paper:** *ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models*, arXiv:2305.18323.

**Claim:** Planner foresight, workers gather evidence without interleaving observations into reasoning, solver finishes; reduces tokens vs ReAct-style loops.

**Design rules:** `rewoo_plan` / `rewoo_worker` / `rewoo_solver` / `rewoo_decouple` / `rewoo_token_save` / `rewoo_loop_plan`. Proxies only — ≠ ReAct.

---

## 242. CRITIC — tool-interactive self-correct (v11.3)

**Paper:** *CRITIC: Large Language Models Can Self-Correct with Tool-Interactive Critiquing*, arXiv:2305.11738.

**Claim:** Draft → tool critique (search/code) → revise; iterate verify→correct. Distinct from Reflexion (verbal RL without external tools).

**Design rules:** `critic_draft` / `critic_tool_check` / `critic_revise` / `critic_iterate` / `critic_stop` / `critic_loop_plan`. Proxies only.

---

## 243. Deductive Verification / Natural Program (v11.3)

**Paper:** *Deductive Verification of Chain-of-Thought Reasoning*, arXiv:2306.03872.

**Claim:** Natural Program steps; premise-scoped per-step verify; unanimity before accepting the chain. Distinct from Faithful CoT.

**Design rules:** `dv_natural_program` / `dv_step_verify` / `dv_premise_scope` / `dv_unanimity` / `dv_ground` / `dv_loop_plan`. Proxies only.

---

## 244. HuggingGPT — LLM controller over models (v11.4)

**Paper:** *HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face*, arXiv:2303.17580.

**Claim:** LLM plans tasks, selects models by description, executes subtasks, summarizes across modalities. Proxies only — no live Hugging Face.

**Design rules:** `hgpt_plan` / `hgpt_select` / `hgpt_execute` / `hgpt_summarize` / `hgpt_modality` / `hgpt_loop_plan`. Proxies only.

---

## 245. Multiagent Debate (v11.4)

**Paper:** *Improving Factuality and Reasoning in Language Models through Multiagent Debate*, arXiv:2305.14325.

**Claim:** Multiple agents propose and debate over rounds until a common answer; improves factuality. Distinct from Meta-Prompting.

**Design rules:** `mad_propose` / `mad_debate` / `mad_critique` / `mad_converge` / `mad_factuality` / `mad_loop_plan`. Proxies only.

---

## 246. Auto-CoT — automatic demonstration construction (v11.5)

**Paper:** *Automatic Chain of Thought Prompting in Large Language Models*, arXiv:2210.03493.

**Claim:** Cluster questions for diversity, sample representatives, generate Zero-Shot-CoT chains as demos — no manual CoT crafting.

**Design rules:** `autocot_cluster` / `autocot_sample` / `autocot_generate` / `autocot_heuristic` / `autocot_diversity` / `autocot_loop_plan`. Proxies only.

---

## 247. CAMEL — communicative role-playing agents (v11.5)

**Paper:** *CAMEL: Communicative Agents for "Mind" Exploration of Large Language Model Society*, arXiv:2303.17760.

**Claim:** Role-playing with inception prompting enables autonomous multi-agent cooperation. Distinct from Multiagent Debate.

**Design rules:** `camel_roles` / `camel_inception` / `camel_turn` / `camel_complete` / `camel_society` / `camel_loop_plan`. Proxies only.

---

## 248. Chameleon — plug-and-play compositional reasoning (v11.6)

**Paper:** *Chameleon: Plug-and-Play Compositional Reasoning with Large Language Models*, arXiv:2304.09842.

**Claim:** LLM planner composes plug-and-play tools (search, vision, code, heuristics) into a program. Distinct from HuggingGPT.

**Design rules:** `cham_inventory` / `cham_plan` / `cham_compose` / `cham_execute` / `cham_constraint` / `cham_loop_plan`. Proxies only.

---

## 249. Recursion of Thought — multi-context divide-and-conquer (v11.6)

**Paper:** *Recursion of Thought: A Divide-and-Conquer Approach to Multi-Context Reasoning with Language Models*, arXiv:2306.06891.

**Claim:** Special trigger tokens divide long CoT into sub-contexts, conquer each, merge — stays within context limits. Distinct from Least-to-Most.

**Design rules:** `rot_trigger` / `rot_divide` / `rot_conquer` / `rot_merge` / `rot_context_limit` / `rot_loop_plan`. Proxies only.

---

## 250. Active-Prompt — uncertainty-guided CoT annotation (v11.7)

**Paper:** *Active Prompting with Chain-of-Thought for Large Language Models*, arXiv:2302.12246.

**Claim:** Sample answers, score uncertainty, select hardest questions for human CoT annotation. Distinct from Auto-CoT (diversity clustering).

**Design rules:** `ap_sample` / `ap_uncertainty` / `ap_select` / `ap_annotate` / `ap_pool` / `ap_loop_plan`. Proxies only.

---

## 251. Analogical Prompting — self-generated exemplars (v11.7)

**Paper:** *Large Language Models as Analogical Reasoners*, arXiv:2310.01714.

**Claim:** Self-generate relevant exemplars/knowledge in-context before solving; no manual labels. Distinct from Active-Prompt / Auto-CoT.

**Design rules:** `ana_recall` / `ana_knowledge` / `ana_solve` / `ana_adapt` / `ana_no_label` / `ana_loop_plan`. Proxies only.

---

## 252. Complexity-Based Prompting (v11.8)

**Paper:** *Complexity-Based Prompting for Multi-Step Reasoning*, arXiv:2210.00720.

**Claim:** Prefer CoT exemplars with more reasoning steps; at decode time, vote among complex chains. Distinct from Auto-CoT / Active-Prompt.

**Design rules:** `cbp_score` / `cbp_select` / `cbp_sample_chains` / `cbp_vote_complex` / `cbp_robust` / `cbp_loop_plan`. Proxies only.

---

## 253. Step-Back Prompting — reason via abstraction (v11.8)

**Paper:** *Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models*, arXiv:2310.06117.

**Claim:** Abstract to concepts/principles first, then reason — escapes detail traps. Distinct from Least-to-Most.

**Design rules:** `sb_abstract` / `sb_principle` / `sb_reason` / `sb_path` / `sb_detail_trap` / `sb_loop_plan`. Proxies only.

---

## 254. Multimodal-CoT — text+vision two-stage CoT (v11.9)

**Paper:** *Multimodal Chain-of-Thought Reasoning in Language Models*, arXiv:2302.00923.

**Claim:** Fuse text and vision, generate multimodal rationales, then infer answers — mitigates hallucination vs text-only CoT.

**Design rules:** `mmcot_fuse` / `mmcot_rationale` / `mmcot_infer` / `mmcot_hallucination` / `mmcot_separate` / `mmcot_loop_plan`. Proxies only — no vision I/O on core.

---

## 255. Maieutic Prompting — SAT over explanation trees (v11.9)

**Paper:** *Maieutic Prompting: Logically Consistent Reasoning with Recursive Explanations*, arXiv:2205.11822.

**Claim:** Abductive recursive explanation trees; infer via satisfiability even when explanations are noisy.

**Design rules:** `mai_abduce` / `mai_recurse` / `mai_sat` / `mai_consistent` / `mai_unreliable` / `mai_loop_plan`. Proxies only.

---

## 256. Self-Refine — iterative self-feedback (v12.0)

**Paper:** *SELF-REFINE: Iterative Refinement with Self-Feedback*, arXiv:2303.17651.

**Claim:** Same LLM generates, critiques, and refines iteratively without extra training or RL.

**Design rules:** `sr_generate` / `sr_feedback` / `sr_refine` / `sr_iterate` / `sr_no_train` / `sr_loop_plan`. Proxies only. ≠ CRITIC (external verifier).

---

## 257. Metacognitive Prompting — introspective NLU (v12.0)

**Paper:** *Metacognitive Prompting Improves Understanding in Large Language Models*, arXiv:2308.05342.

**Claim:** Structured self-aware steps (recognize → interpret → re-evaluate → confidence) beat CoT on NLU.

**Design rules:** `mcp_recognize` / `mcp_interpret` / `mcp_reevaluate` / `mcp_confidence` / `mcp_justify` / `mcp_loop_plan`. Proxies only. ≠ Meta-Prompting (`mp_*`).

---

## 258. Thread of Thought — chaotic context threads (v12.1)

**Paper:** *Thread of Thought Unraveling Chaotic Contexts*, arXiv:2311.08734.

**Claim:** Segment and analyze chaotic contexts with distractors; select pertinent info then synthesize — plug-and-play with other prompts.

**Design rules:** `thot_segment` / `thot_analyze` / `thot_select` / `thot_synthesize` / `thot_plug` / `thot_loop_plan`. Proxies only.

---

## 259. Thought Propagation — analogical reuse (v12.1)

**Paper:** *Thought Propagation: An Analogical Approach to Complex Reasoning with Large Language Models*, arXiv:2310.03965.

**Claim:** Propose/solve analogous problems, reuse insights to amend scratch solutions — reduces from-scratch error accumulation.

**Design rules:** `tprop_propose` / `tprop_solve` / `tprop_reuse` / `tprop_amend` / `tprop_compat` / `tprop_loop_plan`. Proxies only. ≠ Analogical Prompting (`ana_*`).

---

## 260. System 2 Attention — regenerate then attend (v12.2)

**Paper:** *System 2 Attention (is something you might need too)*, arXiv:2311.11829.

**Claim:** Soft attention absorbs irrelevant context; regenerate relevant context first, then respond — raises factuality/objectivity, cuts sycophancy.

**Design rules:** `s2a_regenerate` / `s2a_attend` / `s2a_respond` / `s2a_factuality` / `s2a_sycophancy` / `s2a_loop_plan`. Proxies only.

---

## 261. Contrastive Chain-of-Thought — valid vs invalid demos (v12.2)

**Paper:** *Contrastive Chain-of-Thought Prompting*, arXiv:2311.09277.

**Claim:** Pair valid and invalid reasoning demonstrations so the model learns mistakes to avoid while stepping through answers.

**Design rules:** `ccot_valid` / `ccot_invalid` / `ccot_contrast` / `ccot_reason` / `ccot_auto` / `ccot_loop_plan`. Proxies only. ≠ Auto-CoT (`autocot_*`).

---

## 262. Tab-CoT — tabular 2D chain of thought (v12.3)

**Paper:** *Tab-CoT: Zero-shot Tabular Chain of Thought*, arXiv:2305.17812.

**Claim:** Structure CoT as a table (step/subquestion/process/result) so reasoning flows across rows and columns in zero-/few-shot settings.

**Design rules:** `tabcot_header` / `tabcot_row` / `tabcot_infer2d` / `tabcot_extract` / `tabcot_zeroshot` / `tabcot_loop_plan`. Proxies only. ≠ Contrastive CoT (`ccot_*`).

---

## 263. Everything of Thoughts (XoT) — Penrose triangle (v12.3)

**Paper:** *Everything of Thoughts: Defying the Law of Penrose Triangle for Thought Generation*, arXiv:2311.04254.

**Claim:** MCTS+RL cognitive maps jointly chase performance, efficiency, and flexibility with collaborative thought revision.

**Design rules:** `xot_mcts` / `xot_revise` / `xot_map` / `xot_penrose` / `xot_flexible` / `xot_loop_plan`. Proxies only — no real MCTS/RL on core. ≠ ToT/GoT.

---

## 264. Chain-of-Verification — draft, verify, revise (v12.4)

**Paper:** *Chain-of-Verification Reduces Hallucination in Large Language Models*, arXiv:2309.11495.

**Claim:** Draft → plan verification questions → answer them independently → emit a verified response to cut factual hallucinations.

**Design rules:** `cove_draft` / `cove_plan` / `cove_answer` / `cove_final` / `cove_hallucination` / `cove_loop_plan`. Proxies only. ≠ CRITIC / Deductive Verification.

---

## 265. Verify-and-Edit — knowledge-enhanced CoT (v12.4)

**Paper:** *Verify-and-Edit: A Knowledge-Enhanced Chain-of-Thought Framework*, arXiv:2305.03268.

**Claim:** Detect uncertain CoT via consistency, retrieve supporting facts, edit the rationale, then re-predict.

**Design rules:** `ved_uncertain` / `ved_search` / `ved_edit` / `ved_predict` / `ved_knowledge` / `ved_loop_plan`. Proxies only — no retrieval I/O on core. ≠ CoVe (`cove_*`).

---

## 266. Self-Verification — backward condition check (v12.5)

**Paper:** *Large Language Models are Better Reasoners with Self-Verification*, arXiv:2212.09561.

**Claim:** Forward CoT candidates, then backward-mask conditions and re-predict them to score/select the best conclusion.

**Design rules:** `sve_forward` / `sve_mask` / `sve_repredict` / `sve_score` / `sve_select` / `sve_loop_plan`. Proxies only. ≠ CoVe (`cove_*`) / Voyager self-verify.

---

## 267. Chain of Density — sparse-to-dense summaries (v12.5)

**Paper:** *From Sparse to Dense: GPT-4 Summarization with Chain of Density Prompting*, arXiv:2309.04269.

**Claim:** Start entity-sparse, iteratively fuse missing entities at fixed length — denser summaries humans often prefer.

**Design rules:** `cod_sparse` / `cod_entities` / `cod_fuse` / `cod_length` / `cod_tradeoff` / `cod_loop_plan`. Proxies only. `cod_*` ≠ code.

---

## 268. Hint-before-Solving — hints then reason (v12.6)

**Paper:** *Hint-before-Solving Prompting: Guiding LLMs to Effectively Utilize Encoded Knowledge*, arXiv:2402.14310.

**Claim:** Emit knowledge/key-idea hints before intermediate steps; orthogonal compose with CoT / Least-to-Most / Plan-and-Solve.

**Design rules:** `hsp_hint` / `hsp_solve` / `hsp_answer` / `hsp_compose` / `hsp_quality` / `hsp_loop_plan`. Proxies only. ≠ Progressive-Hint (`php_*`).

---

## 269. EmotionPrompt — emotional stimuli (v12.6)

**Paper:** *Large Language Models Understand and Can be Enhanced by Emotional Stimuli*, arXiv:2307.11760.

**Claim:** Append psychology-inspired emotional stimuli to prompts to lift accuracy, truthfulness, and responsibility metrics.

**Design rules:** `emo_stimulus` / `emo_append` / `emo_run` / `emo_truth` / `emo_psych` / `emo_loop_plan`. Proxies only.

---

## 270. Automatic Prompt Engineer — instruction search (v12.7)

**Paper:** *Large Language Models Are Human-Level Prompt Engineers*, arXiv:2211.01910.

**Claim:** Treat instructions as programs; propose candidates with an LLM, score/select by zero-shot performance — often matches human prompt engineers.

**Design rules:** `ape_propose` / `ape_score` / `ape_select` / `ape_steer` / `ape_human` / `ape_loop_plan`. Proxies only. ≠ Active-Prompt (`ap_*`).

---

## 271. Promptbreeder — self-referential evolution (v12.7)

**Paper:** *Promptbreeder: Self-Referential Self-Improvement via Prompt Evolution*, arXiv:2309.16797.

**Claim:** Evolve task prompts and mutation-prompts together with diversity maintenance to avoid APE's diminishing returns.

**Design rules:** `pbr_init` / `pbr_mutate` / `pbr_fitness` / `pbr_diversity` / `pbr_selfref` / `pbr_loop_plan`. Proxies only. ≠ APE (`ape_*`).

---

## 272. OPRO — Optimization by PROmpting (v12.8)

**Paper:** *Large Language Models as Optimizers*, arXiv:2309.03409.

**Claim:** Treat the LLM as a black-box optimizer: meta-prompt carries a scored trajectory of prior instructions; each step proposes, scores, and appends better candidates (strong gains on GSM8K / BBH vs human prompts).

**Design rules:** `opro_meta` / `opro_propose` / `opro_score` / `opro_append` / `opro_best` / `opro_loop_plan`. Proxies only. ≠ APE (`ape_*`).

---

## 273. EvoPrompt — LLM × evolutionary algorithms (v12.8)

**Paper:** *EvoPrompt: Connecting LLMs with Evolutionary Algorithms Yields Powerful Prompt Optimizers*, arXiv:2309.08532.

**Claim:** Evolve a prompt population with LLM-mediated crossover/mutation and development-set selection; connects discrete EAs to natural-language prompts without gradients.

**Design rules:** `evp_init` / `evp_cross` / `evp_mutate` / `evp_select` / `evp_ea` / `evp_loop_plan`. Proxies only. Prefix `evp_*` — not `evo_*` (evomemory/evolver) or Promptbreeder.

---

## 274. ProTeGi — textual gradients + beam (v12.9)

**Paper:** *Automatic Prompt Optimization with "Gradient Descent" and Beam Search*, arXiv:2305.03495 (EMNLP 2023).

**Claim:** Form natural-language "gradients" that criticize the current prompt from minibatch errors, edit opposite the gradient, and select via beam search + bandits — up to ~31% gains including jailbreak detection.

**Design rules:** `ptg_gradient` / `ptg_edit` / `ptg_beam` / `ptg_bandit` / `ptg_jailbreak` / `ptg_loop_plan`. Proxies only. ≠ OPRO (`opro_*`).

---

## 275. PromptAgent — MCTS prompt planning (v12.9)

**Paper:** *PromptAgent: Strategic Planning with Language Models Enables Expert-level Prompt Optimization*, arXiv:2310.16427.

**Claim:** Cast prompt optimization as MCTS over prompt states; self-reflection error feedback are actions; backpropagate rewards to grow expert-level prompts.

**Design rules:** `pag_state` / `pag_reflect` / `pag_expand` / `pag_backprop` / `pag_expert` / `pag_loop_plan`. Proxies only. ≠ ProTeGi (`ptg_*`) / Active-Prompt (`ap_*`).

---

## 276. MAPO — momentum-aided prompt optimization (v13.0)

**Paper:** *Introducing MAPO: Momentum-Aided Gradient Descent Prompt Optimization*, arXiv:2410.19499.

**Claim:** Extend ProTeGi with positive textual gradients and momentum memory; beam + UCB selection yields faster convergence and fewer API calls vs ProTeGi.

**Design rules:** `mapo_posgrad` / `mapo_momentum` / `mapo_beam` / `mapo_ucb` / `mapo_faster` / `mapo_loop_plan`. Proxies only. ≠ ProTeGi (`ptg_*`).

---

## 277. GrIPS — gradient-free edit search (v13.0)

**Paper:** *GrIPS: Gradient-free, Edit-based Instruction Search for Prompting Large Language Models*, arXiv:2203.07281.

**Claim:** Improve human-readable instructional prompts via local phrase edits (add/paraphrase/swap/delete) without gradients — suitable for API-only models.

**Design rules:** `grips_seed` / `grips_edit` / `grips_score` / `grips_accept` / `grips_api` / `grips_loop_plan`. Proxies only. ≠ MAPO / ProTeGi.

---

## 278. TEMPERA — test-time RL prompt editing (v13.1)

**Paper:** *TEMPERA: Test-Time Prompting via Reinforcement Learning*, arXiv:2211.11890 (ICLR 2023).

**Claim:** Query-adaptive RL edits over instructions, few-shot exemplars, and verbalizers; interpretable per-query prompts with strong sample efficiency vs fine-tuning / RLPrompt / AutoPrompt.

**Design rules:** `tmpa_state` / `tmpa_act` / `tmpa_reward` / `tmpa_adapt` / `tmpa_efficiency` / `tmpa_loop_plan`. Proxies only. Prefix `tmpa_*` — not `sc_temperature`.

---

## 279. RLPrompt — discrete RL soft prompts (v13.1)

**Paper:** *RLPrompt: Optimizing Discrete Text Prompts with Reinforcement Learning*, arXiv:2205.12548.

**Claim:** Optimize discrete prompt tokens with RL against black-box task reward — API-friendly alternative to continuous prompt tuning.

**Design rules:** `rlp_init` / `rlp_sample` / `rlp_reward` / `rlp_update` / `rlp_discrete` / `rlp_loop_plan`. Proxies only. ≠ TEMPERA (`tmpa_*`).

---

## 280. AutoPrompt — gradient-guided discrete triggers (v13.2)

**Paper:** *AutoPrompt: Eliciting Knowledge from Language Models with Automatically Generated Prompts*, arXiv:2010.15980.

**Claim:** Gradient-guided search finds shared discrete trigger tokens that maximize label likelihood in cloze templates — parameter-free probing often competitive with supervised baselines.

**Design rules:** `aup_template` / `aup_trigger` / `aup_search` / `aup_score` / `aup_probe` / `aup_loop_plan`. Proxies only. ≠ Active-Prompt (`ap_*`).

---

## 281. Prefix-Tuning — continuous prefixes for generation (v13.2)

**Paper:** *Prefix-Tuning: Optimizing Continuous Prompts for Generation*, arXiv:2101.00190.

**Claim:** Optimize continuous task-specific prefix vectors while freezing the LM — expressive soft prompts for NLG with tiny trainable footprint.

**Design rules:** `pfx_task` / `pfx_prefix` / `pfx_optimize` / `pfx_generate` / `pfx_freeze` / `pfx_loop_plan`. Proxies only. ≠ AutoPrompt discrete triggers.

---

## 282. P-Tuning v2 — deep prompts for NLU (v13.3)

**Paper:** *P-Tuning v2: Prompt Tuning Can Be Comparable to Fine-tuning Universally Across Scales and Tasks*, arXiv:2110.07602.

**Claim:** Deep continuous prompts at every transformer layer close the gap to finetuning on NLU and hard sequence tagging with only 0.1%–3% tuned parameters (no verbalizer required).

**Design rules:** `ptv_deep` / `ptv_inject` / `ptv_tune` / `ptv_seqtag` / `ptv_universal` / `ptv_loop_plan`. Proxies only. ≠ Prefix-Tuning (`pfx_*`).

---

## 283. Prompt Tuning — input-layer soft prompts (v13.3)

**Paper:** *The Power of Scale for Parameter-Efficient Prompt Tuning*, arXiv:2104.08691 (Lester et al.).

**Claim:** Soft prompt embeddings prepended at the input layer scale toward finetuning quality as model size grows, with a tiny trainable footprint.

**Design rules:** `ptl_soft` / `ptl_prepend` / `ptl_optimize` / `ptl_scale` / `ptl_input_only` / `ptl_loop_plan`. Proxies only. ≠ deep P-Tuning v2 (`ptv_*`).

---

## 284. Soft Prompt Mixtures — learn how to ask (v13.4)

**Paper:** *Learning How to Ask: Querying LMs with Mixtures of Soft Prompts*, arXiv:2104.06599 (Qin & Eisner, NAACL 2021).

**Claim:** Soft-word continuous prompts learned by gradient descent, mixed and ensembled, recover more factual knowledge from LMs than hand-written cloze prompts.

**Design rules:** `msp_soft` / `msp_mix` / `msp_ensemble` / `msp_probe` / `msp_underest` / `msp_loop_plan`. Proxies only. ≠ Prompt Tuning (`ptl_*`).

---

## 285. SPoT — Soft Prompt Transfer (v13.4)

**Paper:** *SPoT: Better Frozen Model Adaptation through Soft Prompt Transfer*, arXiv:2110.07904.

**Claim:** Transfer soft prompts from source to target tasks; task-embedding retrieval predicts positive transfer; matches/beats model tuning on SuperGLUE with far fewer params.

**Design rules:** `spot_source` / `spot_init` / `spot_embed` / `spot_retrieve` / `spot_vs_tune` / `spot_loop_plan`. Proxies only. ≠ Soft Prompt Mixtures (`msp_*`).

---

## 286. ATTEMPT — attentional mixtures of soft prompts (v13.5)

**Paper:** *ATTEMPT: Parameter-Efficient Multi-task Tuning via Attentional Mixtures of Soft Prompts*, arXiv:2205.11961 (EMNLP 2022).

**Claim:** Instance-wise attention interpolates frozen source soft prompts with a trainable target prompt; highly modular and parameter-efficient multitask transfer.

**Design rules:** `atm_source` / `atm_target` / `atm_attend` / `atm_mix` / `atm_modular` / `atm_loop_plan`. Proxies only. ≠ SPoT (`spot_*`) / Soft Prompt Mixtures (`msp_*`).

---

## 287. Multitask Prompt Tuning — shared × low-rank factors (v13.5)

**Paper:** *Multitask Prompt Tuning Enables Parameter-Efficient Transfer Learning*, arXiv:2303.02861.

**Claim:** Decompose multitask soft prompts into a shared matrix times low-rank task factors; transfer with multiplicative updates — beats ATTEMPT with fewer task-specific params on SuperGLUE.

**Design rules:** `mptp_shared` / `mptp_factor` / `mptp_transfer` / `mptp_score` / `mptp_efficient` / `mptp_loop_plan`. Proxies only. ≠ ATTEMPT (`atm_*`).

---

## 288. LoRA — low-rank adaptation of frozen weights (v13.6)

**Paper:** *LoRA: Low-Rank Adaptation of Large Language Models*, arXiv:2106.09685 (ICLR 2022).

**Claim:** Freeze W0; train low-rank ΔW=BA; merge at inference with no added latency — PEFT without adapter-layer depth.

**Design rules:** `lora_freeze` / `lora_rank` / `lora_train` / `lora_merge` / `lora_latency` / `lora_loop_plan`. Proxies only. ≠ AdapterFusion (`adf_*`) / Multitask Prompt Tuning (`mptp_*`).

---

## 289. AdapterFusion — non-destructive adapter composition (v13.6)

**Paper:** *AdapterFusion: Non-Destructive Task Composition for Transfer Learning*, arXiv:2005.00247 (EACL 2021).

**Claim:** Extract task adapters, then compose via attention Ψ without catastrophic forgetting — knowledge extraction separated from composition.

**Design rules:** `adf_extract` / `adf_compose` / `adf_attend` / `adf_score` / `adf_nondestruct` / `adf_loop_plan`. Proxies only. ≠ LoRA (`lora_*`) / ATTEMPT (`atm_*`).

---

## 290. Compacter — hypercomplex low-rank adapters (v13.7)

**Paper:** *Compacter: Efficient Low-Rank Hypercomplex Adapter Layers*, arXiv:2106.04647 (NeurIPS 2021).

**Claim:** Parameterize Houlsby-style bottlenecks with Kronecker / hypercomplex factors — orders-of-magnitude fewer trainable params while matching adapter quality.

**Design rules:** `cmp_insert` / `cmp_kronecker` / `cmp_train` / `cmp_score` / `cmp_compact` / `cmp_loop_plan`. Proxies only. ≠ LoRA (`lora_*`) / AdapterFusion (`adf_*`).

---

## 291. (IA)^3 — infused activation rescale (v13.7)

**Paper:** *Few-Shot Parameter-Efficient Fine-Tuning is Better and Cheaper than In-Context Learning*, arXiv:2205.05638 (NeurIPS 2022).

**Claim:** Learned vectors element-wise rescale inner activations; tiny PEFT footprint and mixed-task batches without new depth.

**Design rules:** `ia3_vector` / `ia3_scale` / `ia3_train` / `ia3_score` / `ia3_mixed` / `ia3_loop_plan`. Proxies only. ≠ Compacter (`cmp_*`) / LoRA (`lora_*`).

---

## 292. BitFit — bias-only fine-tuning (v13.8)

**Paper:** *BitFit: Simple Parameter-efficient Fine-tuning for Transformer-based Masked Language-models*, arXiv:2106.10199 (ACL 2022).

**Claim:** Freeze all weights; train only bias terms (+ task head) — competitive GLUE with ≪0.1% trainable params.

**Design rules:** `bft_freeze` / `bft_bias` / `bft_train` / `bft_score` / `bft_tiny` / `bft_loop_plan`. Proxies only. ≠ LoRA (`lora_*`) / DoRA (`dora_*`).

---

## 293. DoRA — weight-decomposed low-rank adaptation (v13.8)

**Paper:** *DoRA: Weight-Decomposed Low-Rank Adaptation*, arXiv:2402.09353.

**Claim:** Decompose W into magnitude and direction; apply LoRA on direction to close the LoRA↔full-FT gap without full fine-tuning cost.

**Design rules:** `dora_decompose` / `dora_magnitude` / `dora_direction` / `dora_score` / `dora_vs_lora` / `dora_loop_plan`. Proxies only. ≠ LoRA (`lora_*`) / BitFit (`bft_*`) / dormant scan.

---

## 294. QLoRA — 4-bit quantized LoRA finetuning (v13.9)

**Paper:** *QLoRA: Efficient Finetuning of Quantized LLMs*, arXiv:2305.14314 (NeurIPS 2023).

**Claim:** Freeze NF4 4-bit base; train LoRA; double quantization + paged optimizers recover 16-bit FT quality at a fraction of the memory.

**Design rules:** `qlo_quantize` / `qlo_nf4` / `qlo_adapter` / `qlo_score` / `qlo_memory` / `qlo_loop_plan`. Proxies only. ≠ LoRA (`lora_*`) / AdaLoRA (`adl_*`).

---

## 295. AdaLoRA — adaptive-rank LoRA (v13.9)

**Paper:** *AdaLoRA: Adaptive Budget Allocation for Parameter-Efficient Fine-Tuning*, arXiv:2303.10512 (ICLR 2023).

**Claim:** Dynamically allocate rank via SVD importance; prune unimportant singular values to concentrate the parameter budget.

**Design rules:** `adl_init` / `adl_svd` / `adl_prune` / `adl_score` / `adl_adaptive` / `adl_loop_plan`. Proxies only. ≠ QLoRA (`qlo_*`) / Adaptive-RAG CLI.

---

## 296. VeRA — vector-based random matrix adaptation (v14.0)

**Paper:** *VeRA: Vector-based Random Matrix Adaptation*, arXiv:2310.11454 (ICLR 2024).

**Claim:** Share frozen random low-rank matrices across layers; train only tiny per-layer scaling vectors — far fewer trainable params than LoRA at similar quality.

**Design rules:** `vra_share` / `vra_scale` / `vra_train` / `vra_score` / `vra_tiny` / `vra_loop_plan`. Proxies only. ≠ LoRA (`lora_*`) / AdapterDrop (`adp_*`).

---

## 297. AdapterDrop — drop lower-layer adapters (v14.0)

**Paper:** *AdapterDrop: On the Efficiency of Adapters in Transformers*, arXiv:2010.11918 (EACL 2021).

**Claim:** Remove adapters from lower transformer layers during training/inference; cut multi-task overhead with minimal quality loss; also prunes AdapterFusion lower adapters.

**Design rules:** `adp_insert` / `adp_drop` / `adp_infer` / `adp_score` / `adp_efficient` / `adp_loop_plan`. Proxies only. ≠ AdapterFusion (`adf_*`) / VeRA (`vra_*`).

---

## 298. PiSSA — principal singular adaptation (v14.1)

**Paper:** *PiSSA: Principal Singular Values and Singular Vectors Adaptation of Large Language Models*, arXiv:2404.02948 (NeurIPS 2024).

**Claim:** Same LoRA architecture, but init A,B from principal SVD of W and freeze residual — faster convergence and better end quality than Gaussian/zero LoRA init.

**Design rules:** `psa_svd` / `psa_principal` / `psa_residual` / `psa_score` / `psa_fast` / `psa_loop_plan`. Proxies only. ≠ LoRA (`lora_*`) / Diff Pruning (`dpr_*`).

---

## 299. Diff Pruning — sparse difference-vector PEFT (v14.1)

**Paper:** *Parameter-Efficient Transfer Learning with Diff Pruning*, arXiv:2012.07463 (ACL 2021).

**Claim:** Learn a sparse task-specific ΔW over frozen pretrained weights — no new adapter layers; competitive with adapters at far fewer trainable params.

**Design rules:** `dpr_diff` / `dpr_mask` / `dpr_prune` / `dpr_score` / `dpr_sparse` / `dpr_loop_plan`. Proxies only. ≠ BitFit (`bft_*`) / PiSSA (`psa_*`).

---

## 300. Tied-LoRA — weight-tied LoRA across layers (v14.2)

**Paper:** *Tied-LoRA: Enhancing parameter efficiency of LoRA with weight tying*, arXiv:2311.09578.

**Claim:** Tie LoRA weights across layers to shrink the trainable footprint while keeping mergeability into the base model.

**Design rules:** `tlo_base` / `tlo_tie` / `tlo_train` / `tlo_score` / `tlo_efficient` / `tlo_loop_plan`. Proxies only. ≠ VeRA (`vra_*`) / LoRA+ (`lrp_*`).

---

## 301. LoRA+ — dual learning rates for A and B (v14.2)

**Paper:** *LoRA+: Efficient Low Rank Adaptation of Large Models*, arXiv:2402.12354.

**Claim:** Set λ = lr_B / lr_A ≫ 1 so B learns features faster — up to ~2× finetune speed and better task alignment vs equal-LR LoRA.

**Design rules:** `lrp_split` / `lrp_ratio` / `lrp_train` / `lrp_score` / `lrp_speed` / `lrp_loop_plan`. Proxies only. ≠ Tied-LoRA (`tlo_*`) / standard LoRA (`lora_*`).

---

## 302. LoRA-FA — freeze A, train B only (v14.3)

**Paper:** *LoRA-FA: Memory-efficient Low-rank Adaptation for Large Language Models Fine-tuning*, arXiv:2308.03303.

**Claim:** Freeze randomly initialized A; train only B — large activation-memory savings while staying competitive with full LoRA.

**Design rules:** `lfa_freeze_a` / `lfa_train_b` / `lfa_merge` / `lfa_score` / `lfa_memory` / `lfa_loop_plan`. Proxies only. ≠ LoRA+ (`lrp_*`) / DyLoRA (`dyl_*`).

---

## 303. DyLoRA — dynamic search-free rank (v14.3)

**Paper:** *DyLoRA: Parameter Efficient Tuning of Pre-trained Models using Dynamic Search-Free Low-Rank Adaptation*, arXiv:2210.07558.

**Claim:** Train across a rank range; truncate randomly during training; pick rank at inference without expensive search.

**Design rules:** `dyl_range` / `dyl_sample` / `dyl_select` / `dyl_score` / `dyl_searchfree` / `dyl_loop_plan`. Proxies only. ≠ AdaLoRA (`adl_*`) / LoRA-FA (`lfa_*`).

---

## 304. LoRA-XS — trainable r×r only (v14.4)

**Paper:** *LoRA-XS: Low-Rank Adaptation with Extremely Small Number of Parameters*, arXiv:2405.17604.

**Claim:** Freeze SVD-initialized A and B; train only an r×r matrix R between them — extreme storage/parameter efficiency vs LoRA/VeRA.

**Design rules:** `lxs_svd` / `lxs_r` / `lxs_train` / `lxs_score` / `lxs_tiny` / `lxs_loop_plan`. Proxies only. ≠ VeRA (`vra_*`) / AsymmetryLoRA (`asy_*`).

---

## 305. AsymmetryLoRA — train B, freeze orthogonal A (v14.4)

**Paper:** *Asymmetry in Low-Rank Adapters of Foundation Models*, arXiv:2402.16842 · ICML 2024.

**Claim:** A extracts features, B maps to output; training B (with frozen random orthogonal A) is more effective and tightens generalization bounds.

**Design rules:** `asy_role` / `asy_freeze_a` / `asy_train_b` / `asy_score` / `asy_bound` / `asy_loop_plan`. Proxies only. ≠ LoRA-FA (`lfa_*`) / LoRA-XS (`lxs_*`).

---

## 306. LoRA-GA — gradient-approximation init (v14.5)

**Paper:** *LoRA-GA: Low-Rank Adaptation with Gradient Approximation*, arXiv:2407.05000 · NeurIPS 2024.

**Claim:** Initialize A,B via SVD of sampled gradients (plus stable scale) so the low-rank update approximates full fine-tuning — faster convergence without changing LoRA architecture.

**Design rules:** `lga_grad` / `lga_svd` / `lga_scale` / `lga_score` / `lga_fast` / `lga_loop_plan`. Proxies only. ≠ PiSSA (`psa_*`) / MoRA (`mor_*`).

---

## 307. MoRA — high-rank square updates (v14.5)

**Paper:** *MoRA: High-Rank Updating for Parameter-Efficient Fine-Tuning*, arXiv:2405.12130.

**Claim:** Replace low-rank BA with a square matrix M plus non-parameter compress/expand ops to maximize rank(ΔW) at the same parameter budget — stronger on knowledge-intensive fine-tuning; still mergeable.

**Design rules:** `mor_square` / `mor_compress` / `mor_expand` / `mor_score` / `mor_merge` / `mor_loop_plan`. Proxies only. ≠ MemoRAG (`memorag_*`) / LoRA-GA (`lga_*`).

---

## 308. rsLoRA — rank-stabilized 1/√r scale (v14.6)

**Paper:** *A Rank Stabilization Scaling Factor for Fine-Tuning with LoRA*, arXiv:2312.03732.

**Claim:** Scale adapters by 1/√r instead of 1/r so higher ranks do not collapse gradients — unlocks compute/performance trade-off at inference-identical cost.

**Design rules:** `rsl_rank` / `rsl_scale` / `rsl_train` / `rsl_score` / `rsl_stable` / `rsl_loop_plan`. Proxies only. ≠ LoRA+ (`lrp_*`) / LoKr (`lkr_*`).

---

## 309. LoKr — Kronecker-product adapters (v14.6)

**Paper:** *LoKr / Kronecker product low-rank adaptation*, arXiv:2309.14859 (PEFT LoKr).

**Claim:** Replace BA with a Kronecker product of factors — preserves rank structure, vectorizable without full ΔW reconstruct; common for diffusion adapters.

**Design rules:** `lkr_factors` / `lkr_kron` / `lkr_vectorize` / `lkr_score` / `lkr_preserve` / `lkr_loop_plan`. Proxies only. ≠ MoRA (`mor_*`) / rsLoRA (`rsl_*`).

---

## 310. LoHa — Hadamard product of low-rank pairs (v14.7)

**Paper:** *LoHa / FedPara-style Hadamard low-rank adaptation*, arXiv:2108.06098 (applied in PEFT as LoHa).

**Claim:** Approximate ΔW via Hadamard product of two low-rank products (four matrices) — more expressivity than BA at a similar parameter budget.

**Design rules:** `lha_pair` / `lha_hadamard` / `lha_train` / `lha_score` / `lha_express` / `lha_loop_plan`. Proxies only. ≠ LoKr (`lkr_*`) / FourierFT (`fft_*`).

---

## 311. FourierFT — spectral coefficients via DFT (v14.7)

**Paper:** *Parameter-Efficient Fine-Tuning with Discrete Fourier Transform*, arXiv:2405.03003.

**Claim:** Learn sparse Fourier spectral coefficients and reconstruct ΔW via inverse DFT — extreme parameter reduction without low-rank factorization.

**Design rules:** `fft_basis` / `fft_coeff` / `fft_idft` / `fft_score` / `fft_sparse` / `fft_loop_plan`. Proxies only. ≠ LoRA / LoHa (`lha_*`).

---

## 312. Houlsby adapters — bottleneck series modules (v14.8)

**Paper:** *Parameter-Efficient Transfer Learning for NLP*, arXiv:1902.00751 · ICML 2019.

**Claim:** Insert small bottleneck adapters after attention/FFN while freezing the base — near full fine-tune quality with a few percent task-specific parameters; adds inference latency vs mergeable LoRA.

**Design rules:** `had_insert` / `had_freeze` / `had_train` / `had_score` / `had_latency` / `had_loop_plan`. Proxies only. ≠ LoHa (`lha_*`) / AdapterDrop (`adp_*`) / ReFT (`rft_*`).

---

## 313. ReFT — representation finetuning (v14.8)

**Paper:** *ReFT: Representation Finetuning for Language Models*, arXiv:2404.03592.

**Claim:** Edit hidden representations (LoReFT-style) instead of weights — intervene in activation space; no weight ΔW required.

**Design rules:** `rft_repr` / `rft_edit` / `rft_train` / `rft_score` / `rft_weightless` / `rft_loop_plan`. Proxies only. ≠ Stele REFLECT contested resolve / Houlsby (`had_*`).

---

## 314. OFT/BOFT — orthogonal / butterfly finetuning (v14.9)

**Paper:** *Controlling Text-to-Image Diffusion by Orthogonal Finetuning* (OFT) · *Parameter-Efficient Orthogonal Finetuning via Butterfly Factorization* (BOFT), arXiv:2311.06243.

**Claim:** Multiplicative orthogonal transforms preserve hyperspherical energy; BOFT butterfly factorization cuts OFT parameter cost while staying mergeable.

**Design rules:** `oft_ortho` / `oft_butterfly` / `oft_train` / `oft_score` / `oft_energy` / `oft_loop_plan`. Proxies only. ≠ BitFit (`bft_*`) / MiSS (`mss_*`).

---

## 315. MiSS — matrix shard sharing (v14.9)

**Paper:** *MiSS: Revisiting the Trade-off in LoRA with an Efficient Shard-Sharing Structure*, arXiv:2409.15371.

**Claim:** Update weight shards with a single shared trainable matrix D (zero-init) instead of dual BA — lower optimization complexity and a better performance–memory–efficiency Pareto position.

**Design rules:** `mss_shard` / `mss_share` / `mss_train` / `mss_score` / `mss_pareto` / `mss_loop_plan`. Proxies only. ≠ Soft Prompt Mixtures (`msp_*`) / OFT (`oft_*`).

---

## 316. DropLoRA — stochastic rank prune / dynamic subspace (v15.0)

**Paper:** *DropLoRA: Sparse Low-Rank Adaptation for Parameter-Efficient Fine-Tuning*, arXiv:2508.17337.

**Claim:** Bernoulli prune on the rank dimension between A and B each step — dynamic subspace learning; no extra parameters or inference cost vs LoRA.

**Design rules:** `drl_rank` / `drl_mask` / `drl_train` / `drl_score` / `drl_infer` / `drl_loop_plan`. Proxies only. ≠ DoRA (`dora_*`) / DyLoRA (`dyl_*`) / dormant-scan.

---

## 317. GaLore — gradient low-rank projection (v15.0)

**Paper:** *GaLore: Memory-Efficient LLM Training by Gradient Low-Rank Projection*, arXiv:2403.03507.

**Claim:** Project full-parameter gradients onto low-rank subspaces for memory-efficient training — updates all weights (optimizer path), not an adapter.

**Design rules:** `gal_grad` / `gal_project` / `gal_step` / `gal_score` / `gal_full` / `gal_loop_plan`. Proxies only. ≠ LoRA-GA (`lga_*`) / DropLoRA (`drl_*`).

---

## 318. SHiRA — sparse high-rank adapters (v15.1)

**Paper:** *Sparse High Rank Adapters*, arXiv:2406.13175 · NeurIPS 2024.

**Claim:** Tune ~1–2% of base weights via a sparse mask — no inference overhead, rapid fused switching, and lower multi-adapter concept loss than LoRA.

**Design rules:** `shr_mask` / `shr_tune` / `shr_switch` / `shr_score` / `shr_fusion` / `shr_loop_plan`. Proxies only. ≠ DropLoRA (`drl_*`) / WaveFT (`wft_*`).

---

## 319. WaveFT — wavelet-domain sparse updates (v15.1)

**Paper:** *Exploring Sparsity for Parameter Efficient Fine Tuning Using Wavelets*, arXiv:2505.12532.

**Claim:** Learn sparse coefficients in the wavelet domain of ΔW and reconstruct via IDWT — finer parameter budgets than LoRA’s minimum rank.

**Design rules:** `wft_wave` / `wft_sparse` / `wft_idwt` / `wft_score` / `wft_granular` / `wft_loop_plan`. Proxies only. ≠ FourierFT (`fft_*`) / SHiRA (`shr_*`).

---

## 320. LoRA-Pro — equivalent-gradient optimization (v15.2)

**Paper:** *LoRA-Pro: Are Low-Rank Adapters Properly Optimized?*, arXiv:2407.18242.

**Claim:** Adjust LoRA gradients so the equivalent gradient of BA matches full fine-tuning — closes the LoRA↔FFT optimization gap without changing the BA structure.

**Design rules:** `lpr_equiv` / `lpr_adjust` / `lpr_train` / `lpr_score` / `lpr_bridge` / `lpr_loop_plan`. Proxies only. ≠ LoRA+ (`lrp_*`) / LoRA-GA (`lga_*`) / Kron-LoRA (`krl_*`).

---

## 321. Kron-LoRA — hybrid Kronecker–LoRA (v15.2)

**Paper:** *Kron-LoRA: Hybrid Kronecker-LoRA Adapters for Scalable, Sustainable Fine-tuning*, arXiv:2508.01961.

**Claim:** Two-stage adapter — Kronecker factors plus LoRA low-rank update — for multiplicative parameter compression vs plain LoRA.

**Design rules:** `krl_kron` / `krl_lora` / `krl_train` / `krl_score` / `krl_compress` / `krl_loop_plan`. Proxies only. ≠ LoKr (`lkr_*`) / LoRA-Pro (`lpr_*`) / MoRA (`mor_*`).

---

## 322. MiLoRA — minor singular components (v15.3)

**Paper:** *MiLoRA: Harnessing Minor Singular Components for Parameter-Efficient LLM Finetuning*, arXiv:2406.09044.

**Claim:** Update only minor singular components while freezing principal ones — adapts in a subspace orthogonal to pretrained knowledge so the principal matrix is preserved.

**Design rules:** `mil_svd` / `mil_minor` / `mil_freeze` / `mil_score` / `mil_preserve` / `mil_loop_plan`. Proxies only. ≠ PiSSA (`psa_*`) / MoRA (`mor_*`) / CorDA (`cda_*`).

---

## 323. CorDA — context-oriented decomposition (v15.3)

**Paper:** *Dynamic Context-oriented Decomposition for Task-aware Low-rank Adaptation…* (CorDA / CorDA++), arXiv:2506.13187.

**Claim:** Task-aware SVD on W·activation-covariance — KPM freezes principal (less forgetting); IPM adapts principal (faster convergence).

**Design rules:** `cda_cov` / `cda_mode` / `cda_adapt` / `cda_score` / `cda_forget` / `cda_loop_plan`. Proxies only. ≠ PiSSA (`psa_*`) / MiLoRA (`mil_*`) / LoRA-Pro (`lpr_*`).

---

## 324. LoftQ — LoRA-fine-tuning-aware quantization (v15.4)

**Paper:** *LoftQ: LoRA-Fine-Tuning-Aware Quantization for Large Language Models*, arXiv:2310.08659.

**Claim:** Alternate quantization and low-rank approximation so LoRA init closes the discrepancy between quantized backbone and full-precision weights — better than QLoRA init especially at low bits.

**Design rules:** `lfq_quant` / `lfq_init` / `lfq_train` / `lfq_score` / `lfq_gap` / `lfq_loop_plan`. Proxies only. ≠ QLoRA (`qlo_*`) / PiSSA (`psa_*`) / LoRA-Dash (`lds_*`).

---

## 325. LoRA-Dash — task-specific directions (v15.4)

**Paper:** *Task-Specific Directions… / Unleashing the Power of Task-Specific Directions…* (LoRA-Dash), arXiv:2409.01035.

**Claim:** Pre-launch identifies task-specific directions (TSDs); dash phase amplifies them during fine-tuning for stronger task adaptation.

**Design rules:** `lds_prelaunch` / `lds_tsd` / `lds_dash` / `lds_score` / `lds_impact` / `lds_loop_plan`. Proxies only. ≠ LoftQ (`lfq_*`) / LoRA-Pro (`lpr_*`) / LoRA-XS (`lxs_*`).

---

## 326. Delta-LoRA — high-rank via Δ(AB) (v15.5)

**Paper:** *Delta-LoRA: Fine-Tuning High-Rank Parameters with the Delta of Low-Rank Matrices*, arXiv:2309.02411.

**Claim:** Update A/B with AdamW and propagate Δ(AB) into pretrained W without storing W gradients — high-rank capacity at LoRA memory cost.

**Design rules:** `dlo_adapters` / `dlo_delta` / `dlo_propagate` / `dlo_score` / `dlo_highrank` / `dlo_loop_plan`. Proxies only. ≠ DoRA (`dora_*`) / DropLoRA (`drl_*`) / LoRA-One (`lon_*`).

---

## 327. LoRA-One — one-step gradient alignment (v15.5)

**Paper:** *LoRA-One: One-Step Full Gradient Could Suffice for Fine-Tuning Large Language Models…*, arXiv:2502.01235.

**Claim:** Initialize adapters from the one-step full fine-tuning gradient so they align with optimal singular subspaces immediately — theory-driven PEFT.

**Design rules:** `lon_grad` / `lon_align` / `lon_train` / `lon_score` / `lon_immediate` / `lon_loop_plan`. Proxies only. ≠ LoRA-GA (`lga_*`) / LoRA-Pro (`lpr_*`) / Delta-LoRA (`dlo_*`).

---

## 328. OLoRA — orthonormal QR initialization (v15.6)

**Paper:** *OLoRA: Orthonormal Low-Rank Adaptation of Large Language Models*, arXiv:2406.01775.

**Claim:** QR orthonormal init for adaptation matrices — approximates final W with a more stable optimization landscape and faster convergence than Gaussian/zero LoRA init.

**Design rules:** `olr_qr` / `olr_ortho` / `olr_train` / `olr_score` / `olr_stable` / `olr_loop_plan`. Proxies only. ≠ LoRA-One (`lon_*`) / OFT (`oft_*`) / LoRA-SP (`lsp_*`).

---

## 329. LoRA-SP — streamlined partial parameter adaptation (v15.6)

**Paper:** *LoRA-SP: Streamlined Partial Parameter Adaptation…*, arXiv:2403.08822.

**Claim:** Randomized half-selective freezing inside A/B — update ~half adapter params to cut memory while retaining competitive task performance.

**Design rules:** `lsp_select` / `lsp_freeze` / `lsp_train` / `lsp_score` / `lsp_memory` / `lsp_loop_plan`. Proxies only. ≠ SPoT (`spot_*`) / DropLoRA (`drl_*`) / OLoRA (`olr_*`).

---

## 330. QPiSSA — quantized PiSSA (v15.7)

**Paper:** *PiSSA…* (QPiSSA section), arXiv:2404.02948.

**Claim:** PiSSA principal-component adapters on a 4-bit quantized backbone — smaller initial quantization error than QLoRA; stronger GSM8K results at 70B scale.

**Design rules:** `qps_quant` / `qps_principal` / `qps_train` / `qps_score` / `qps_error` / `qps_loop_plan`. Proxies only. ≠ PiSSA (`psa_*`) / QLoRA (`qlo_*`) / LoftQ (`lfq_*`).

---

## 331. MoSLoRA — mixture-of-subspaces LoRA (v15.7)

**Paper:** *Mixture-of-Subspaces in Low-Rank Adaptation* (MoSLoRA), arXiv:2406.11909 · EMNLP 2024.

**Claim:** Learnable mixer between A and B fuses rank-1 subspaces more flexibly than identity LoRA — negligible extra params, mergeable at inference.

**Design rules:** `msl_split` / `msl_mixer` / `msl_train` / `msl_score` / `msl_fuse` / `msl_loop_plan`. Proxies only. ≠ MiSS (`mss_*`) / Soft Prompt Mixtures (`msp_*`) / QPiSSA (`qps_*`).

---

## 332. LoRA-drop — output-based LoRA pruning (v15.8)

**Paper:** *LoRA-drop: Efficient LoRA Parameter Pruning based on Output Evaluation*, arXiv:2402.07721 · COLING 2025.

**Claim:** Score LoRA layers by output magnitude; keep important layers and share one LoRA across the rest — ~50% params with competitive accuracy.

**Design rules:** `ldr_eval` / `ldr_keep` / `ldr_share` / `ldr_score` / `ldr_prune` / `ldr_loop_plan`. Proxies only. ≠ DropLoRA (`drl_*`) / LoRA-Dash (`lds_*`) / VB-LoRA (`vbl_*`).

---

## 333. VB-LoRA — vector-bank LoRA (v15.8)

**Paper:** *VB-LoRA: Extreme Parameter Efficient Fine-Tuning with Vector Banks*, arXiv:2405.15179 · NeurIPS 2024.

**Claim:** Divide-and-share via a global vector bank + top-k admixture — composites all LoRA matrices; ~0.4% of LoRA storage on Llama2-13B with competitive quality.

**Design rules:** `vbl_bank` / `vbl_topk` / `vbl_compose` / `vbl_score` / `vbl_extreme` / `vbl_loop_plan`. Proxies only. ≠ VeRA (`vra_*`) / LoRA-XS (`lxs_*`) / LoRA-drop (`ldr_*`).

---

## 334. OPLoRA — orthogonal projection LoRA (v15.9)

**Paper:** *OPLoRA: Orthogonal Projection LoRA Prevents Catastrophic Forgetting during Parameter-Efficient Fine-Tuning*, arXiv:2510.13003.

**Claim:** Double-sided orthogonal projections constrain LoRA updates away from pretrained subspaces — reduces catastrophic forgetting during PEFT.

**Design rules:** `opl_proj` / `opl_constrain` / `opl_train` / `opl_score` / `opl_forget` / `opl_loop_plan`. Proxies only. ≠ OLoRA (`olr_*`) / GeLoRA (`gel_*`) / alternating-update OPLoRA (arXiv:2509.19977).

---

## 335. GeLoRA — geometric adaptive ranks (v15.9)

**Paper:** *GeLoRA: Geometric Adaptive Ranks For Efficient LoRA Fine-tuning*, arXiv:2412.09250.

**Claim:** Intrinsic dimensionality of hidden states gives a lower bound for per-layer LoRA rank — better accuracy within the same parameter budget.

**Design rules:** `gel_idim` / `gel_rank` / `gel_train` / `gel_score` / `gel_budget` / `gel_loop_plan`. Proxies only. ≠ GeoLoRA (`geo_*` reserved) / GaLore (`gal_*`) / OPLoRA (`opl_*`).

---

## 336. GeoLoRA — geometric dynamical low-rank (v16.0)

**Paper:** *GeoLoRA: Geometric integration for parameter efficient fine-tuning*, arXiv:2410.18720 · ICLR 2025.

**Claim:** Dynamical low-rank integration with a single backprop over adapters — adaptive budget allocation, exact orthonormal factors, faster/more robust than AdaLoRA-style methods.

**Design rules:** `geo_dyn` / `geo_budget` / `geo_train` / `geo_score` / `geo_ortho` / `geo_loop_plan`. Proxies only. ≠ GeLoRA (`gel_*`) / GaLore (`gal_*`) / RandLoRA (`rlo_*`).

---

## 337. RandLoRA — full-rank via random bases (v16.0)

**Paper:** *RandLoRA: Full-rank parameter-efficient fine-tuning of large models*, arXiv:2502.00987.

**Claim:** Learn diagonal scales on frozen random low-rank bases to realize full-rank updates — closes LoRA↔full-FT gaps especially on vision-language tasks.

**Design rules:** `rlo_bases` / `rlo_scale` / `rlo_train` / `rlo_score` / `rlo_fullrank` / `rlo_loop_plan`. Proxies only. ≠ VeRA (`vra_*`) / LoRA (`lora_*`) / GeoLoRA (`geo_*`).

---

## 338. LoRAShear — structured prune + recover (v16.1)

**Paper:** *LoRAShear: Efficient Large Language Model Structured Pruning and Knowledge Recovery*, arXiv:2310.18356.

**Claim:** Dependency graphs over LoRA modules + LHSPG progressive structured prune with knowledge transfer, then dynamic recovery fine-tuning — ~20% footprint cut with ~1% quality drop on one GPU.

**Design rules:** `lsh_graph` / `lsh_prune` / `lsh_recover` / `lsh_score` / `lsh_footprint` / `lsh_loop_plan`. Proxies only. ≠ LoRA-SP (`lsp_*`) / DropLoRA (`drl_*`) / alternating OPLoRA (`aop_*`).

---

## 339. Alternating OPLoRA — LoRSum / ALS toward SVDLoRA (v16.1)

**Paper:** *Faster Than SVD, Smarter Than SGD: The OPLoRA Alternating Update*, arXiv:2509.19977.

**Claim:** Cast LoRA optimization as alternating least-squares (LoRSum) so 1–2 steps approach truncated-SVD LoRA without forming the full matrix; recovers prior preconditioned LoRA as the one-step case.

**Design rules:** `aop_sub` / `aop_alt` / `aop_train` / `aop_score` / `aop_svd` / `aop_loop_plan`. Proxies only. ≠ orthogonal-projection OPLoRA (`opl_*`, arXiv:2510.13003) / OLoRA (`olr_*`) / LoRAShear (`lsh_*`).

---

## 340. LoRA-Init — TSD-based adapter initialization (v16.2)

**Paper:** *Task-Specific Directions: Definition, Exploration, and Utilization in Parameter Efficient Fine-Tuning*, arXiv:2409.01035 (LoRA-Init companion to LoRA-Dash).

**Claim:** Initialize LoRA from the task-specific directions that need the most adjustment — faster convergence and better downstream performance than non-task-specific init.

**Design rules:** `lin_tsd` / `lin_init` / `lin_train` / `lin_score` / `lin_fast` / `lin_loop_plan`. Proxies only. ≠ LoRA-Dash (`lds_*`) / LoRA-Null (`lnu_*`) / LoRA-One (`lon_*`).

---

## 341. LoRA-Null — activation null-space init (v16.2)

**Paper:** *Put the Space of LoRA Initialization to the Extreme to Preserve Pre-trained Knowledge*, arXiv:2503.02659.

**Claim:** Initialize LoRA in the null space of pre-trained *activations* (not weights) — better knowledge preservation than MiLoRA-style weight null spaces while keeping fine-tuning quality.

**Design rules:** `lnu_act` / `lnu_null` / `lnu_train` / `lnu_score` / `lnu_forget` / `lnu_loop_plan`. Proxies only. ≠ MiLoRA (`mil_*`) / LoRA-Init (`lin_*`) / OLoRA (`olr_*`).

---

## 342. HydraLoRA — shared-A multi-B MoE (v16.3)

**Paper:** *HydraLoRA: An Asymmetric LoRA Architecture for Efficient Fine-Tuning*, arXiv:2404.19245 · NeurIPS 2024.

**Claim:** Asymmetric shared A + multiple B heads with MoE routing — outperforms domain-guided multi-LoRA without requiring domain labels at train or inference.

**Design rules:** `hyd_share` / `hyd_heads` / `hyd_route` / `hyd_score` / `hyd_nodomain` / `hyd_loop_plan`. Proxies only. ≠ AsymmetryLoRA (`asy_*`) / LoRA-LEGO (`llg_*`).

---

## 343. LoRA-LEGO — rank-wise MSU merge (v16.3)

**Paper:** *Merging LoRAs like Playing LEGO: Pushing the Modularity of LoRA to Extremes Through Rank-Wise Clustering*, arXiv:2409.16167.

**Claim:** Treat per-rank columns as Minimal Semantic Units, cluster across adapters, assemble merged LoRA from centroids + dual reweight — stronger modular merging than naive composition.

**Design rules:** `llg_msu` / `llg_cluster` / `llg_merge` / `llg_score` / `llg_modular` / `llg_loop_plan`. Proxies only. ≠ HydraLoRA (`hyd_*`) / LoraHub.

---

## 344. LoRAMoE — MoE plugin vs world forgetting (v16.4)

**Paper:** *LoRAMoE: Alleviate World Knowledge Forgetting in Large Language Models via MoE-Style Plugin*, arXiv:2312.09979 · ACL 2024.

**Claim:** Freeze backbone; route multiple LoRA experts with localized balancing so some experts keep world knowledge while others serve SFT tasks — scales instruction data without catastrophic knowledge wipe.

**Design rules:** `lme_plugin` / `lme_balance` / `lme_route` / `lme_score` / `lme_forget` / `lme_loop_plan`. Proxies only. ≠ MoELoRA (`mel_*`) / HydraLoRA (`hyd_*`) / MiLoRA (`mil_*`).

---

## 345. MoELoRA — contrastive LoRA experts (v16.4)

**Paper:** *MoELoRA: Contrastive Learning Guided Mixture of Experts on Parameter-Efficient Fine-Tuning for Large Language Models*, arXiv:2402.12851.

**Claim:** Treat LoRA modules as MoE experts; contrastive guidance for distinct features; gate activates sparse task-relevant experts.

**Design rules:** `mel_experts` / `mel_contrast` / `mel_gate` / `mel_score` / `mel_sparse` / `mel_loop_plan`. Proxies only. ≠ LoRAMoE (`lme_*`) / MiLoRA (`mil_*`) / HydraLoRA (`hyd_*`).

---

## 346. LoraHub — dynamic LoRA composition (v16.5)

**Paper:** *LoraHub: Efficient Cross-Task Generalization via Dynamic LoRA Composition*, arXiv:2307.13269 · COLM 2024.

**Claim:** Compose + gradient-free adapt of multiple task LoRAs from few shots — ICL-like BBH trade-off without in-context tokens at inference.

**Design rules:** `lhb_pool` / `lhb_compose` / `lhb_adapt` / `lhb_score` / `lhb_nograd` / `lhb_loop_plan`. Proxies only. ≠ LoRA-LEGO (`llg_*`) / MultiLoRA (`mlr_*`) / HydraLoRA (`hyd_*`).

---

## 347. MultiLoRA — democratic multi-task LoRA (v16.5)

**Paper:** *MultiLoRA: Democratizing LoRA for Better Multi-Task Learning*, arXiv:2311.11501.

**Claim:** Horizontally scale LoRA along rank + init change to reduce top-singular dominance — more democratic updates closer to full FT for multi-task mixes.

**Design rules:** `mlr_scale` / `mlr_init` / `mlr_train` / `mlr_score` / `mlr_demo` / `mlr_loop_plan`. Proxies only. ≠ LoraHub (`lhb_*`) / MiLoRA (`mil_*`) / MoELoRA (`mel_*`).

---

## 348. MTL-LoRA — task-specific + shared MTL (v16.6)

**Paper:** *MTL-LoRA: Low-Rank Adaptation for Multi-Task Learning*, arXiv:2410.09437.

**Claim:** Task-specific low-rank transforms plus dynamic task-agnostic sharing — cuts interference that uniform LoRA shows in multi-task settings.

**Design rules:** `mtl_task` / `mtl_spec` / `mtl_share` / `mtl_score` / `mtl_interfere` / `mtl_loop_plan`. Proxies only. ≠ MultiLoRA (`mlr_*`) / MALoRA (`mal_*`) / MoELoRA (`mel_*`).

---

## 349. MALoRA — mixture of asymmetric LoRA (v16.6)

**Paper:** *MALoRA: Mixture of Asymmetric Low-Rank Adaptation for Enhanced Multi-Task Learning*, arXiv:2410.22782 · NAACL Findings 2025.

**Claim:** Shared down-proj subspace + higher-rank up-proj per expert — ~30–48% fewer params and ~1.2× faster than MoLoRA while beating multi-task baselines.

**Design rules:** `mal_mix` / `mal_down` / `mal_up` / `mal_score` / `mal_eff` / `mal_loop_plan`. Proxies only. ≠ MTL-LoRA (`mtl_*`) / MoELoRA (`mel_*`) / AsymmetryLoRA (`asy_*`).

---

## 350. LoRA-Mini — selective inner-matrix train (v16.7)

**Paper:** *LoRA-Mini: Adaptation Matrices Decomposition and Selective Training*, arXiv:2411.15804 · AAAI CoLoRAI 2025.

**Claim:** Decompose each low-rank factor into four parts; train only the two inner matrices — up to ~20× fewer trainable params with LoRA-comparable quality.

**Design rules:** `lmi_split` / `lmi_inner` / `lmi_train` / `lmi_score` / `lmi_tiny` / `lmi_loop_plan`. Proxies only. ≠ LoRA-XS (`lxs_*`) / QDyLoRA (`qdy_*`) / MiLoRA (`mil_*`).

---

## 351. QDyLoRA — quantized dynamic ranks (v16.7)

**Paper:** *QDyLoRA: Quantized Dynamic Low-Rank Adaptation for Efficient Large Language Model Tuning*, arXiv:2402.10462.

**Claim:** DyLoRA nested ranks + QLoRA-style 4-bit quant — one fine-tune covers a rank range under low memory; pick optimal nested rank at inference.

**Design rules:** `qdy_range` / `qdy_quant` / `qdy_train` / `qdy_score` / `qdy_pick` / `qdy_loop_plan`. Proxies only. ≠ QLoRA (`qlo_*`) / DyLoRA (`dyl_*`) / LoRA-Mini (`lmi_*`).

---

## 352. LoRA-TSD — Init+Dash combined (v16.8)

**Paper:** *Task-Specific Directions: Definition, Exploration, and Utilization in Parameter Efficient Fine-Tuning*, arXiv:2409.01035 (LoRA-TSD = LoRA-Init + LoRA-Dash).

**Claim:** Identify TSDs, initialize LoRA with them, then amplify those directions during training — the full TSD-based LoRA loop beyond Dash or Init alone.

**Design rules:** `lts_tsd` / `lts_init` / `lts_dash` / `lts_score` / `lts_combo` / `lts_loop_plan`. Proxies only. ≠ LoRA-Dash (`lds_*`) / LoRA-Init (`lin_*`) / S-LoRA (`slr_*`).

---

## 353. S-LoRA — scalable multi-adapter serving (v16.8)

**Paper:** *S-LoRA: Serving Thousands of Concurrent LoRA Adapters*, arXiv:2311.03285.

**Claim:** Host-memory adapter store + Unified Paging (adapters + KV) + heterogeneous batched LoRA compute — serve thousands of adapters with small overhead vs naive PEFT/vLLM packing.

**Design rules:** `slr_pool` / `slr_page` / `slr_batch` / `slr_score` / `slr_scale` / `slr_loop_plan`. Proxies only. ≠ rsLoRA / LoRA-TSD (`lts_*`).

---

## 354. Compress then Serve — joint LoRA compression (v16.9)

**Paper:** *Compress then Serve: Serving Thousands of LoRA Adapters with Little Overhead*, arXiv:2407.00066 · ICML 2025.

**Claim:** Joint-compress many LoRAs into a shared basis + per-adapter scales; cluster for large collections — higher throughput vs naive multi-LoRA serving at matched GPU memory.

**Design rules:** `cts_collect` / `cts_basis` / `cts_scale` / `cts_score` / `cts_cluster` / `cts_loop_plan`. Proxies only. ≠ S-LoRA (`slr_*`) / FLoRA (`flo_*`).

---

## 355. FLoRA — federated heterogeneous LoRA (v16.9)

**Paper:** *FLoRA: Federated Fine-Tuning Large Language Models with Heterogeneous Low-Rank Adaptations*, arXiv:2409.05976.

**Claim:** Stack local A/B adapters for noise-free aggregation; supports heterogeneous ranks across clients — unlike FedAvg-style LoRA averaging.

**Design rules:** `flo_clients` / `flo_stack` / `flo_agg` / `flo_score` / `flo_hetero` / `flo_loop_plan`. Proxies only. ≠ LoRA+ (`lrp_*`) / Compress-then-Serve (`cts_*`).

---

## 356. Punica — multi-tenant LoRA serving (v17.0)

**Paper:** *Punica: Multi-Tenant LoRA Serving*, arXiv:2310.18547.

**Claim:** SGMV CUDA batching keeps one pretrained copy while serving many LoRA adapters — ~12× throughput vs naive multi-LoRA systems at ~2ms extra latency/token.

**Design rules:** `pun_backbone` / `pun_sgmv` / `pun_sched` / `pun_score` / `pun_multi` / `pun_loop_plan`. Proxies only. ≠ S-LoRA (`slr_*`) / Compress-then-Serve (`cts_*`) / mLoRA (`mla_*`).

---

## 357. mLoRA — pipeline-parallel multi-adapter fine-tune (v17.0)

**Paper:** *mLoRA: Fine-Tuning LoRA Adapters via Highly-Efficient Pipeline Parallelism in Multiple GPUs*, arXiv:2312.02515.

**Claim:** LoRA-aware pipeline parallelism + BatchLoRA operator — lower completion time vs FSDP; fit larger simultaneous fine-tunes on cost-effective GPUs.

**Design rules:** `mla_pipe` / `mla_batch` / `mla_train` / `mla_score` / `mla_eff` / `mla_loop_plan`. Proxies only. ≠ MiLoRA (`mil_*`) / MultiLoRA (`mlr_*`) / Punica (`pun_*`).

---

## 358. SwitchLoRA — switched subspace pre-training (v17.1)

**Paper:** *SwitchLoRA: Switched Low-Rank Adaptation Can Learn Full-Rank Information*, arXiv:2406.06564.

**Claim:** Frequently replace a few LoRA dimensions to approximate full-rank pre-training with low optimizer-state disruption — can beat full-rank perplexity while cutting communication.

**Design rules:** `swl_alloc` / `swl_switch` / `swl_train` / `swl_score` / `swl_full` / `swl_loop_plan`. Proxies only. ≠ COLA (`col_*`) / ReLoRA / Delta-LoRA (`dlo_*`).

---

## 359. Chain of LoRA (COLA) — residual LoRA chain (v17.1)

**Paper:** *Chain of LoRA: Efficient Fine-tuning of Language Models via Residual Learning*, arXiv:2401.04151.

**Claim:** Tune → merge BA into W → fresh LoRA (Frank-Wolfe residual path) closes LoRA↔full-FT gap without extra compute/memory vs LoRA.

**Design rules:** `col_tune` / `col_knot` / `col_extend` / `col_score` / `col_gap` / `col_loop_plan`. Proxies only. ≠ SwitchLoRA (`swl_*`) / Chain-of-Density / Chain-of-Verification.

---

## 360. DeLoRA — decoupled angle vs strength (v17.2)

**Paper:** *DeLoRA: Decoupling Angles and Strength in Low-rank Adaptation*, arXiv:2503.18225 · ICLR 2025.

**Claim:** Normalize BA and scale by a Frobenius boundary λ — decouple direction learning from adaptation strength for stronger hyperparameter / long-train robustness than LoRA.

**Design rules:** `dlr_norm` / `dlr_bound` / `dlr_train` / `dlr_score` / `dlr_robust` / `dlr_loop_plan`. Proxies only. ≠ Delta-LoRA (`dlo_*`) / MELoRA (`meo_*`) / DoRA.

---

## 361. MELoRA — mini-ensemble block-diagonal LoRA (v17.2)

**Paper:** *MELoRA: Mini-Ensemble Low-Rank Adapters for Parameter-Efficient Fine-Tuning*, arXiv:2402.17263.

**Claim:** Stack thinner mini-LoRAs in parallel on the diagonal — effective rank sums without extra parameter count vs a single LoRA of equal total params.

**Design rules:** `meo_mini` / `meo_diag` / `meo_train` / `meo_score` / `meo_rank` / `meo_loop_plan`. Proxies only. ≠ MoELoRA (`mel_*`) / MultiLoRA (`mlr_*`) / DeLoRA (`dlr_*`).

---

## 362. ReLoRA — high-rank via restarted LoRA (v17.3)

**Paper:** *ReLoRA: High-Rank Training Through Low-Rank Updates*, arXiv:2307.05695.

**Claim:** Warm-start full-rank, then periodically merge LoRA into W and restart with jagged LR / partial optimizer reset — aggregate high-rank updates with lower memory than full training.

**Design rules:** `rlr_warm` / `rlr_merge` / `rlr_jagged` / `rlr_score` / `rlr_high` / `rlr_loop_plan`. Proxies only. ≠ rsLoRA (`rsl_*`) / COLA (`col_*`) / ETHER (`eth_*`).

---

## 363. ETHER — hyperplane-reflection PEFT (v17.3)

**Paper:** *ETHER: Efficient Finetuning of Large-Scale Models with Hyperplane Reflections*, arXiv:2405.20271.

**Claim:** Extremely parameter-efficient finetuning via hyperplane reflections (ETHER / ETHER+) — strong LR robustness vs LoRA / VeRA at tiny parameter budgets.

**Design rules:** `eth_plane` / `eth_reflect` / `eth_train` / `eth_score` / `eth_plus` / `eth_loop_plan`. Proxies only. ≠ ReLoRA (`rlr_*`) / VeRA / DeLoRA (`dlr_*`).

---

## 364. LoRA-Composer — training-free multi-concept LoRA (v17.4)

**Paper:** *LoRA-Composer: Leveraging Low-Rank Adaptation for Multi-Concept Customization in Training-Free Diffusion Models*, arXiv:2403.11627.

**Claim:** Compose multiple concept LoRAs without fusion training — injection (anti-vanishing), isolation (anti-confusion), latent re-init for regional concept control.

**Design rules:** `lco_concepts` / `lco_inject` / `lco_isolate` / `lco_score` / `lco_free` / `lco_loop_plan`. Proxies only. ≠ COLA (`col_*`) / CARE-LoRA (`car_*`) / MultiLoRA (`mlr_*`).

---

## 365. CARE-LoRA — compressed activation reconstruction (v17.4)

**Paper:** *CARE-LoRA: Compressed Activation REconstruction for Memory-Efficient LoRA*, arXiv:2607.11940.

**Claim:** Cut LoRA fine-tune activation memory by compressing retained activations and reconstructing gradients — without full recomputation tax.

**Design rules:** `car_compress` / `car_recon` / `car_train` / `car_score` / `car_mem` / `car_loop_plan`. Proxies only. ≠ LoRA-Composer (`lco_*`) / Compress-then-Serve (`cts_*`) / LoRA-FA (`lfa_*`).

---

## 366. LoRA.rar — hypernet subject–style merge (v17.5)

**Paper:** *LoRA.rar: Learning to Merge LoRAs via Hypernetworks for Subject-Style Conditioned Image Generation*, arXiv:2412.05148.

**Claim:** Pre-train a small hypernetwork on content–style LoRA pairs so unseen subject+style merges happen in one forward pass — thousands of times faster than per-pair optimization (ZipLoRA).

**Design rules:** `lrr_pair` / `lrr_hyper` / `lrr_merge` / `lrr_score` / `lrr_fast` / `lrr_loop_plan`. Proxies only. ≠ LoRA-Composer (`lco_*`) / ReLoRA (`rlr_*`) / SVFT (`svf_*`).

---

## 367. SVFT — singular-vector PEFT (v17.5)

**Paper:** *SVFT: Parameter-Efficient Fine-Tuning with Singular Vectors*, arXiv:2405.19597.

**Claim:** ΔW is a sparse combination of W's own singular vectors; only coefficients train. Recovers up to ~96% of full fine-tune at 0.006–0.25% trainable params.

**Design rules:** `svf_svd` / `svf_sparse` / `svf_train` / `svf_score` / `svf_geom` / `svf_loop_plan`. Proxies only. ≠ LoRA.rar (`lrr_*`) / PiSSA / LoRA-XS (`lxs_*`).

---

## 368. FlyLoRA — implicit rank-wise MoE (v17.6)

**Paper:** *FlyLoRA: Boosting Task Decoupling and Parameter Efficiency via Implicit Rank-Wise Mixture-of-Experts*, arXiv:2510.08396.

**Claim:** Frozen sparse random A acts as an implicit router; top-k rank-1 experts on B cut intra- and inter-task interference without extra router params.

**Design rules:** `fly_proj` / `fly_topk` / `fly_train` / `fly_score` / `fly_implicit` / `fly_loop_plan`. Proxies only. ≠ FLoRA (`flo_*`) / NOLA (`nla_*`) / MixLoRA.

---

## 369. NOLA — random-basis LoRA compression (v17.6)

**Paper:** *NOLA: Compressing LoRA using Linear Combination of Random Basis*, arXiv:2310.02556.

**Claim:** Reparameterize A/B as mixtures of frozen random bases; train coefficients only. Breaks LoRA's rank-1 parameter floor (~20× more compact on LLaMA-2 70B).

**Design rules:** `nla_basis` / `nla_coeff` / `nla_train` / `nla_score` / `nla_compact` / `nla_loop_plan`. Proxies only. ≠ FlyLoRA (`fly_*`) / VeRA / VB-LoRA (`vbl_*`).

---

## 370. MixLoRA — LoRA sparse MoE (v17.7)

**Paper:** *MixLoRA: Enhancing Large Language Models Fine-Tuning with LoRA-based Mixture of Experts*, arXiv:2404.15159.

**Claim:** Insert LoRA experts into frozen FFN with a top-k router, plus independent attention LoRAs and a load-balance loss. ~9% multi-task gain vs PEFT baselines; 40% GPU memory cut in their serving stack.

**Design rules:** `mxl_experts` / `mxl_route` / `mxl_attn` / `mxl_score` / `mxl_balance` / `mxl_loop_plan`. Proxies only. ≠ MultiLoRA (`mlr_*`) / FlyLoRA (`fly_*`) / SuperLoRA (`spr_*`).

---

## 371. SuperLoRA — unified LoRA family (v17.7)

**Paper:** *SuperLoRA: Parameter-Efficient Unified Adaptation of Multi-Layer Attention Modules*, arXiv:2403.11887.

**Claim:** One hyperparameter set (group, fold, shuffle, project, tensor factor) covers LoHA/LoKr and new variants; 3–10× fewer params than LoRA in the tiny-budget regime.

**Design rules:** `spr_group` / `spr_fold` / `spr_factor` / `spr_score` / `spr_unify` / `spr_loop_plan`. Proxies only. ≠ MixLoRA (`mxl_*`) / S-LoRA (`slr_*`) / LoHA (`lha_*`).

---

## 372. Tied-LoRA — weight tying + selective train (v17.8)

**Paper:** *Tied-LoRA: Enhancing parameter efficiency of LoRA with Weight Tying*, arXiv:2311.09578.

**Claim:** Share low-rank matrices across layers and freeze a subset; a Tied-LoRA config matches LoRA on several tasks at a fraction of trainable params, especially at high rank.

**Design rules:** `tld_tie` / `tld_select` / `tld_scale` / `tld_score` / `tld_frac` / `tld_loop_plan`. Proxies only. ≠ VeRA (`vra_*`) / NOLA (`nla_*`) / QA-LoRA (`qal_*`).

---

## 373. QA-LoRA — quantization-aware LoRA (v17.8)

**Paper:** *QA-LoRA: Quantization-Aware Low-Rank Adaptation of Large Language Models*, arXiv:2309.14717.

**Claim:** Group-wise operators raise quantization degrees of freedom and share LoRA per group, so INT4 weights merge without a PTQ step — unlike QLoRA.

**Design rules:** `qal_group` / `qal_quant` / `qal_adapt` / `qal_score` / `qal_merge` / `qal_loop_plan`. Proxies only. ≠ QLoRA (`qlo_*`) / LoftQ (`lfq_*`) / Tied-LoRA (`tld_*`).

---

## 374. Uni-LoRA — one vector reconstructs all LoRAs (v17.9)

**Paper:** *Uni-LoRA: One Vector is All You Need*, arXiv:2506.00799.

**Claim:** Tied-LoRA / VeRA / VB-LoRA are projections from a small subspace; an isometric global P lets one trainable vector rebuild every LoRA block.

**Design rules:** `ulo_space` / `ulo_iso` / `ulo_vec` / `ulo_score` / `ulo_one` / `ulo_loop_plan`. Proxies only. ≠ Tied-LoRA (`tlo_*` / `tld_*`) / VeRA (`vra_*`) / BoRA (`bor_*`).

---

## 375. BoRA — bi-dimensional magnitude (v17.9)

**Paper:** *BoRA: Bi-dimensional Weight-Decomposed Low-Rank Adaptation*, arXiv:2412.06441.

**Claim:** DoRA only scales along one axis; BoRA adds row and column magnitudes so the update is symmetric in both dimensions.

**Design rules:** `bor_row` / `bor_col` / `bor_train` / `bor_score` / `bor_sym` / `bor_loop_plan`. Proxies only. ≠ DoRA (`dora_*`) / Uni-LoRA (`ulo_*`).

---

## 376. Q-GaLore — quantized GaLore (v18.0)

**Paper:** *Q-GaLore: Quantized GaLore with INT4 Projection and Layer-Adaptive Low-Rank Gradients*, arXiv:2407.08296.

**Claim:** INT8 weights + INT4 projections plus lazy per-layer SVD cut memory vs GaLore/LoRA (~50% in FT) and can pretrain LLaMA-7B on a 16GB GPU.

**Design rules:** `qga_weight` / `qga_proj` / `qga_lazy` / `qga_score` / `qga_mem` / `qga_loop_plan`. Proxies only. ≠ GaLore (`gal_*`) / QLoRA (`qlo_*`) / LoRA-Flow (`lfw_*`).

---

## 377. LoRA-Flow — token-level LoRA fusion (v18.0)

**Paper:** *LoRA-Flow: Dynamic LoRA Fusion for Large Language Models in Generative Tasks*, arXiv:2402.11455.

**Claim:** A tiny prefix-conditioned gate mixes several LoRAs per token (~0.2% extra params, ~200 examples), beating static task-level fusion on generative mixes.

**Design rules:** `lfw_pool` / `lfw_gate` / `lfw_token` / `lfw_score` / `lfw_few` / `lfw_loop_plan`. Proxies only. ≠ FLoRA (`flo_*`) / S-LoRA (`slr_*`) / Q-GaLore (`qga_*`).

---

## 378. RoSA — robust sparse + low-rank (v18.1)

**Paper:** *RoSA: Accurate Parameter-Efficient Fine-Tuning via Robust Adaptation*, arXiv:2401.04679.

**Claim:** Train a LoRA-scale low-rank term plus a highly sparse residual (RPCA-style). Matches or beats LoRA at the same budget and can recover full fine-tune on some generative tasks.

**Design rules:** `ros_rank` / `ros_sparse` / `ros_train` / `ros_score` / `ros_fft` / `ros_loop_plan`. Proxies only. ≠ LoRA / DoRA (`dora_*`) / ABBA (`abb_*`).

---

## 379. ABBA — Hadamard of two adapters (v18.1)

**Paper:** *ABBA-Adapters: Efficient and Expressive Fine-Tuning of Foundation Models*, arXiv:2505.14238.

**Claim:** ΔW = (B1A1) ⊙ (B2A2). Unlike HiRA, both factors are learned, so high effective rank is not locked to W0.

**Design rules:** `abb_left` / `abb_right` / `abb_hadamard` / `abb_score` / `abb_expr` / `abb_loop_plan`. Proxies only. ≠ LoHA (`lha_*`) / HiRA / RoSA (`ros_*`).

---

## 380. BoHA — blockwise Hadamard (v18.2)

**Paper:** *BoHA: Blockwise Hadamard Product Adaptation for Parameter-Efficient Fine-Tuning*, arXiv:2509.21637.

**Claim:** Global HiRA-style W⊙BA couples every entry to W0's energy. Blocking the product localizes rank lift and avoids spectral collapse.

**Design rules:** `bha_split` / `bha_hadamard` / `bha_train` / `bha_score` / `bha_local` / `bha_loop_plan`. Proxies only. ≠ LoHA (`lha_*`) / ABBA (`abb_*`) / SMoA (`smo_*`).

---

## 381. SMoA — high-rank structured modulation (v18.2)

**Paper:** *High-Rank Structured Modulation for Parameter-Efficient Fine-Tuning*, arXiv:2601.07507.

**Claim:** Modulate disjoint subspaces so effective rank rises without extra parameters and without overlapping LoRA directions.

**Design rules:** `smo_struct` / `smo_mod` / `smo_train` / `smo_score` / `smo_rank` / `smo_loop_plan`. Proxies only. ≠ MoRA (`mor_*`) / MixLoRA (`mxl_*`) / BoHA (`bha_*`).

---

## 382. GLoRA — generalized LoRA prompt (v18.3)

**Paper:** *One-for-All: Generalized LoRA for Parameter-Efficient Fine-tuning*, arXiv:2306.07967.

**Claim:** A prompt module rescales weights and activations and searches per-layer adapters. Reparam keeps inference cost at zero vs vanilla LoRA.

**Design rules:** `glo_prompt` / `glo_scale` / `glo_search` / `glo_score` / `glo_zero` / `glo_loop_plan`. Proxies only. ≠ GaLore (`gal_*`) / FLoRA (`flo_*`) / PeriodicLoRA (`plr_*`).

---

## 383. PeriodicLoRA — stacked low-rank stages (v18.3)

**Paper:** *PeriodicLoRA: Breaking the Low-Rank Bottleneck in LoRA Optimization*, arXiv:2402.16141.

**Claim:** Merge BA into W at each stage then reinit. Stacked low-rank updates raise effective rank with no extra memory (~1.8× LoRA learning capacity in the paper).

**Design rules:** `plr_stage` / `plr_merge` / `plr_reset` / `plr_score` / `plr_rank` / `plr_loop_plan`. Proxies only. ≠ ReLoRA (`rlr_*`) / LoRA-Pro (`lpr_*`) / GLoRA (`glo_*`).

---

## 384. HiRA — Hadamard high-rank adaptation (v18.4)

**Paper:** *HiRA: Parameter-Efficient Hadamard High-Rank Adaptation for Large Language Models*, ICLR 2025 Oral, OpenReview:TwJrTz9cRS (no arXiv ID after live fetch).

**Claim:** Form ΔW = W0 ⊙ (BA). A low-rank pair modulates frozen W0 elementwise so the effective update rank is high, then merges like LoRA (zero extra infer).

**Design rules:** `hir_base` / `hir_factors` / `hir_hadamard` / `hir_score` / `hir_merge` / `hir_loop_plan`. Proxies only. ≠ SHiRA (`shr_*`) / LoHA (`lha_*`) / PeriodicLoRA (`plr_*`).

---

## 385. PLoRA — concurrent LoRA training (v18.4)

**Paper:** *PLoRA: Efficient Concurrent LoRA Training for Large Language Models*, arXiv:2508.02932.

**Claim:** Fuse many LoRA adapters into one packed forward so concurrent fine-tunes share GPU work instead of serializing per adapter.

**Design rules:** `cnl_pack` / `cnl_fuse` / `cnl_train` / `cnl_score` / `cnl_hw` / `cnl_loop_plan`. Proxies only. ≠ PeriodicLoRA (`plr_*`) / MixLoRA (`mxl_*`) / HiRA (`hir_*`).

---

## 386. LongLoRA — shifted sparse long context (v18.5)

**Paper:** *LongLoRA: Efficient Fine-tuning of Long-Context Large Language Models*, arXiv:2309.12307.

**Claim:** Train long context with shifted sparse attention (S2-Attn), then LoRA. Sparse train attention is optional at infer; context extends without full dense attention cost.

**Design rules:** `llr_window` / `llr_shift` / `llr_lora` / `llr_score` / `llr_sparse` / `llr_loop_plan`. Proxies only. ≠ LoRA-FA (`lfa_*`) / HiRA (`hir_*`) / LISA (`lis_*`).

---

## 387. LISA — layerwise importance sampling (v18.5)

**Paper:** *LISA: Layerwise Importance Sampling for Memory-Efficient Large Language Model Fine-Tuning*, arXiv:2403.17919.

**Claim:** Sample which layers to unfreeze each step so optimizer state stays small vs full LoRA, without keeping every layer live.

**Design rules:** `lis_layers` / `lis_sample` / `lis_unfreeze` / `lis_score` / `lis_memory` / `lis_loop_plan`. Proxies only. ≠ LoftQ (`lfq_*`) / MiLoRA (`mil_*`) / LongLoRA (`llr_*`).

---

## 388. NLoRA — Nyström-initiated LoRA (v18.6)

**Paper:** *NLoRA: Nyström-Initiated Low-Rank Adaptation for Large Language Models*, arXiv:2502.14482.

**Claim:** Nyström landmarks initialize LoRA cheaper than full SVD (PiSSA-style) while keeping the same adapter shape.

**Design rules:** `nlr_landmark` / `nlr_nystrom` / `nlr_init` / `nlr_score` / `nlr_cheap` / `nlr_loop_plan`. Proxies only. ≠ S-LoRA (`slr_*`) / PiSSA (`pis_*`) / LISA (`lis_*`).

---

## 389. ROSA — random subspace adaptation (v18.6)

**Paper:** *ROSA: Random Subspace Adaptation for Efficient Fine-Tuning*, arXiv:2407.07802.

**Claim:** Adapt a random subspace of arbitrary dimension so expressiveness beats LoRA at the same memory, with zero extra infer cost.

**Design rules:** `rsa_subspace` / `rsa_project` / `rsa_train` / `rsa_score` / `rsa_express` / `rsa_loop_plan`. Proxies only. ≠ RoSA robust (`ros_*`) / rsLoRA (`rsl_*`) / NLoRA (`nlr_*`).

---

## 390. HRA — Householder reflection adaptation (v18.7)

**Paper:** *Bridging The Gap between Low-rank and Orthogonal Adaptation via Householder Reflection Adaptation*, arXiv:2405.17484.

**Claim:** Householder reflections sit between LoRA and orthogonal adapters — more stable than LoRA, cheaper than full OFT.

**Design rules:** `hra_house` / `hra_reflect` / `hra_train` / `hra_score` / `hra_ortho` / `hra_loop_plan`. Proxies only. ≠ HiRA (`hir_*`) / OFT (`oft_*`) / OLoRA (`olr_*`).

---

## 391. Hybrid PEFT — LoRA-GA + BOFT fusion (v18.7)

**Paper:** *Hybrid and Unitary PEFT for Resource-Efficient Large Language Models*, arXiv:2507.18076.

**Claim:** Fuse LoRA-GA’s fast start with BOFT orthogonal stability using per-layer gradient-norm weights.

**Design rules:** `hyb_lora` / `hyb_boft` / `hyb_fuse` / `hyb_score` / `hyb_stable` / `hyb_loop_plan`. Proxies only. ≠ LoRA-GA (`lga_*`) / OFT (`oft_*`) / HRA (`hra_*`).

---

## 392. LoRTA — low-rank tensor adaptation (v18.8)

**Paper:** *LoRTA: Efficient Low Rank Tensor Adaptation of Large Language Models*, arXiv:2410.04060.

**Claim:** A 5th-order CP tensor shares updates across layers, heads, and matrices — 10–100× fewer params than LoRA.

**Design rules:** `lrt_tensor` / `lrt_cp` / `lrt_share` / `lrt_score` / `lrt_compact` / `lrt_loop_plan`. Proxies only. ≠ LoRA-TSD (`tsd_*`) / HiRA (`hir_*`) / C-LoRA (`clo_*`).

---

## 393. C-LoRA — continual LoRA (v18.8)

**Paper:** *C-LoRA: Continual Low-Rank Adaptation for Pre-trained Models*, arXiv:2502.17920.

**Claim:** One shared adapter plus a learnable route, with orthogonality so sequential tasks forget less than per-task LoRA.

**Design rules:** `clo_route` / `clo_task` / `clo_ortho` / `clo_score` / `clo_forget` / `clo_loop_plan`. Proxies only. ≠ ConcurrentLoRA (`cnl_*`) / LoRTA (`lrt_*`) / Hybrid PEFT (`hyb_*`).

---

## 394. ALoRA — allocating LoRA ranks (v18.9)

**Paper:** *ALoRA: Allocating Low-Rank Adaptation for Fine-tuning Large Language Models*, arXiv:2403.16187.

**Claim:** AB-LoRA scores each rank, prunes dead ones, and reallocates budget to hotter modules — better than fixed-rank LoRA at the same parameter count.

**Design rules:** `alo_init` / `alo_ablate` / `alo_prune` / `alo_score` / `alo_realloc` / `alo_loop_plan`. Proxies only. ≠ AdaLoRA (`adl_*`) / C-LoRA (`clo_*`) / LN Tuning (`lnt_*`).

---

## 395. LN Tuning — attention LayerNorm scales (v18.9)

**Paper:** *Tuning LayerNorm in Attention: Towards Efficient Multi-Modal LLM Finetuning*, arXiv:2312.11420.

**Claim:** Train attention LayerNorm gammas only — cheaper than LoRA, still useful for multimodal adapters.

**Design rules:** `lnt_attn` / `lnt_scale` / `lnt_train` / `lnt_score` / `lnt_cheap` / `lnt_loop_plan`. Proxies only. ≠ LoRA-Null (`lnu_*`) / ALoRA (`alo_*`) / BitFit (`bft_*`).

---

## 396. LoRAFusion — fused kernels + multi-job LoRA (v18.10)

**Paper:** *LoRAFusion: Efficient LoRA Fine-Tuning for LLMs*, arXiv:2510.00206.

**Claim:** Fuse memory-bound LoRA ops and bin-pack multi-job microbatches — up to ~2× vs Megatron-LM, faster than mLoRA, no extra infer cost.

**Design rules:** `lfu_split` / `lfu_fuse` / `lfu_batch` / `lfu_score` / `lfu_speed` / `lfu_loop_plan`. Proxies only. ≠ Hybrid PEFT (`hyb_*`) / FlyLoRA (`fly_*`) / ConcurrentLoRA (`cnl_*`).

---

## 397. TeRA — high-rank tensor net, vector cost (v18.10)

**Paper:** *TeRA: Vector-based Random Tensor Network for High-Rank Adaptation of Large Language Models*, arXiv:2509.03234.

**Claim:** Tucker-like net with frozen random factors; only tiny per-layer scales train — high-rank updates at vector-PEFT cost.

**Design rules:** `ter_tucker` / `ter_freeze` / `ter_scale` / `ter_score` / `ter_highrank` / `ter_loop_plan`. Proxies only. ≠ LoRTA (`lrt_*`) / VeRA (`vra_*`) / LoRAFusion (`lfu_*`).

---

## 398. TensLoRA — tensor alternatives to LoRA (v18.11)

**Paper:** *TensLoRA: Tensor Alternatives for Low-Rank Adaptation*, arXiv:2509.19391.

**Claim:** Stack LoRA updates into a higher-order tensor, Tucker-factor it, and set per-mode ranks (QKV vs depth vs heads) so the budget matches the task.

**Design rules:** `tnl_stack` / `tnl_tucker` / `tnl_mode` / `tnl_score` / `tnl_budget` / `tnl_loop_plan`. Proxies only. ≠ LoRTA (`lrt_*`) / TeRA (`ter_*`) / AdaZeta (`azt_*`).

---

## 399. AdaZeta — ZO tensor-train adapters (v18.11)

**Paper:** *AdaZeta: Adaptive Zeroth-Order Tensor-Train Adaption for Memory-Efficient Large Language Models Fine-Tuning*, arXiv:2406.18060.

**Claim:** Tensor-train adapters plus adaptive zeroth-order queries — less memory than FO LoRA, more stable than MeZO-LoRA.

**Design rules:** `azt_tt` / `azt_ff` / `azt_query` / `azt_score` / `azt_mem` / `azt_loop_plan`. Proxies only. ≠ AdaLoRA (`adl_*`) / TensLoRA (`tnl_*`) / TeRA (`ter_*`).

---

## 400. FacT — factor-tuning ViT increments (v18.12)

**Paper:** *FacT: Factor-Tuning for Lightweight Adaptation on Vision Transformer*, arXiv:2212.03145.

**Claim:** Stack ViT weight increments into one 3D tensor, then Tensor-Train or Tucker factors — down to ~8K params, still competitive on VTAB-1K.

**Design rules:** `fct_tensor` / `fct_tt` / `fct_tucker` / `fct_score` / `fct_tiny` / `fct_loop_plan`. Proxies only. ≠ TensLoRA (`tnl_*`) / LoTR (`ltr_*`) / LoRTA (`lrt_*`).

---

## 401. LoTR — low tensor-rank across depth (v18.12)

**Paper:** *LoTR: Low Tensor Rank Weight Adaptation*, arXiv:2402.01376.

**Claim:** Share left/right LoRA factors across layers; only a small core tensor is per-block — better param scaling on deep stacks than per-layer LoRA.

**Design rules:** `ltr_stack` / `ltr_core` / `ltr_share` / `ltr_score` / `ltr_deep` / `ltr_loop_plan`. Proxies only. ≠ LoRTA (`lrt_*`) / FacT (`fct_*`) / TensLoRA (`tnl_*`).

---

## 402. CaRA — canonical CP rank on ViT tensors (v18.13)

**Paper:** *Canonical Rank Adaptation: An Efficient Fine-Tuning Strategy for Vision Transformers*, ICML 2025, OpenReview:vexHifrbJg (no arXiv after live fetch).

**Claim:** Split ViT into an MHA tensor and an FFN tensor, then CP-decompose both — fewer params than LoRA, better VTAB-1k / FGVC.

**Design rules:** `cra_mha` / `cra_ffn` / `cra_cpd` / `cra_score` / `cra_heads` / `cra_loop_plan`. Proxies only. ≠ CARE-LoRA (`car_*`) / FacT (`fct_*`) / LoRETTA (`ltt_*`).

---

## 403. LoRETTA — economic tensor-train adapters (v18.13)

**Paper:** *LoRETTA: Low-Rank Economic Tensor-Train Adaptation for Ultra-Low-Parameter Fine-Tuning of Large Language Models*, arXiv:2402.11417.

**Claim:** Tensor-train adapters (adp) or TT reparam of weights (rep) — up to 100× fewer params than LoRA on LLaMA-2-7B; rep can sit under 1MB.

**Design rules:** `ltt_adp` / `ltt_rep` / `ltt_tt` / `ltt_score` / `ltt_tiny` / `ltt_loop_plan`. Proxies only. ≠ LoRTA (`lrt_*`) / LoTR (`ltr_*`) / CaRA (`cra_*`).

---

## 404. C3A — circular-convolution adaptation (v18.14)

**Paper:** *Parameter-Efficient Fine-Tuning via Circular Convolution*, arXiv:2407.19342.

**Claim:** Replace BA with a circulant kernel (FFT multiply) so rank is not tied to param count — high-rank ΔW at LoRA-like cost.

**Design rules:** `c3a_kernel` / `c3a_circ` / `c3a_fft` / `c3a_score` / `c3a_rank` / `c3a_loop_plan`. Proxies only. ≠ CaRA (`cra_*`) / BOFT (`bof_*`).

---

## 405. BOFT — butterfly orthogonal finetuning (v18.14)

**Paper:** *Parameter-Efficient Orthogonal Finetuning via Butterfly Factorization*, arXiv:2311.06243.

**Claim:** Factor orthogonal adapters as butterfly blocks — OFT is the dense special case; fewer params, same orthogonal inductive bias.

**Design rules:** `bof_block` / `bof_orth` / `bof_butter` / `bof_score` / `bof_full` / `bof_loop_plan`. Proxies only. ≠ BitFit (`bft_*`) / OFT (`oft_*`) / C3A (`c3a_*`).

---

## 406. SDT — sparse dimension tuning for SSMs (v18.15)

**Paper:** *Parameter-Efficient Fine-Tuning of State Space Models*, arXiv:2410.09016.

**Claim:** LoRA works on SSM linear projections but fails on SSM modules; Sparse Dimension Tuning (SDT) targets SSM dims and, combined with LoRA on projections, reaches SOTA on SSM-based models.

**Design rules:** `sdt_dim` / `sdt_mask` / `sdt_tune` / `sdt_score` / `sdt_ssm` / `sdt_loop_plan`. Proxies only. ≠ MEFT (`mef_*`) / LoRA family prefixes.

---

## 407. MEFT — memory-efficient sparse adapter (v18.15)

**Paper:** *MEFT: Memory-Efficient Fine-Tuning through Sparse Adapter*, arXiv:2406.04984.

**Claim:** Place large sparse adapters in CPU memory; MoE-like routing fetches only activated neurons to GPU — bigger capacity under a fixed GPU budget.

**Design rules:** `mef_adapt` / `mef_route` / `mef_fetch` / `mef_score` / `mef_cpu` / `mef_loop_plan`. Proxies only. ≠ SDT (`sdt_*`) / MiSS (`mss_*`).

---

## References (primary)

1. He et al. MemoryArena. arXiv:2602.16313 · https://memoryarena.github.io/
2. Memory for Autonomous LLM Agents… arXiv:2603.07670
3. Governed Memory. arXiv:2603.17787
4. memorywire. arXiv:2606.01138
5. Wu et al. LongMemEval. arXiv:2410.10813 · ICLR 2025
6. Xu et al. A-MEM. arXiv:2502.12110
7. Tan et al. MemBench. arXiv:2506.21605 · ACL 2025 Findings
8. MemArchitect. arXiv:2603.18330
9. SSGM. arXiv:2603.11768
10. GateMem. arXiv:2606.18829
11. Governed Shared Memory (MemClaw). arXiv:2606.24535
12. Agent-Native Memory Systems. arXiv:2606.24775
13. TOKI. arXiv:2606.06240
14. StateFuse. arXiv:2607.05844
15. MemoryAgentBench. arXiv:2507.05257
16. MIND. arXiv:2607.28103
17. MAPLE-Guard. arXiv:2608.00426
18. MemMark. arXiv:2605.25002
19. TRACE. arXiv:2607.08400
20. AMV-L. arXiv:2603.04443
21. Mem-α. arXiv:2509.25911
22. AgentHER. arXiv:2603.21357
23. PreFlect. arXiv:2602.07187
24. SkillFlow. arXiv:2605.14089
25. ProcMEM. arXiv:2602.01869
26. MemRL. arXiv:2601.03192
27. EvolveR. arXiv:2510.16079
28. AgentEvolver. arXiv:2511.10395
29. SkillWeaver. arXiv:2504.07079
30. Compositional Skill Routing. arXiv:2606.18051
31. Absolute Zero. arXiv:2505.03335
32. R-Zero. arXiv:2508.05004
33. ECHO. arXiv:2606.31650
34. Agent0. arXiv:2511.16043
35. Multi-Agent Evolve. arXiv:2510.23595
36. SAGE (multi-agent). arXiv:2603.15255
37. MemGen. arXiv:2509.24704
38. Metis. arXiv:2606.24151
39. SAMULE. arXiv:2509.20562
40. LIVE-EVO. arXiv:2602.02369
41. Socratic-Zero. arXiv:2509.24726
42. SPIRAL. arXiv:2506.24119
43. SMITH. arXiv:2512.11303
44. H-Mem (hybrid). arXiv:2605.15701
21. TEPA. arXiv:2608.07429
22. MELD. arXiv:2608.16357
23. MAP-Graph. arXiv:2608.10509
24. RippleMem. arXiv:2608.13334
25. GPM. arXiv:2608.12476
26. SYNAPSE. ACL 2026 Findings
27. SodaMem. arXiv:2608.08055
28. Oblivion. arXiv:2604.00131
29. True Memory / Storage≠Memory. arXiv:2605.04897
30. Portable Agent Memory. arXiv:2605.11032
31. MemLineage. arXiv:2605.14421
32. CAVA (adjacent; deployer attestation — caller-side). arXiv:2607.13716
33. PPMF / Provenance Laundering. arXiv:2607.29167
34. PoEM / Proof-of-Execution Memory. arXiv:2608.16032
35. MemoRepair. arXiv:2605.07242
36. MemIR / Provenance-Role Collapse. arXiv:2605.25869
37. D-Mem. arXiv:2603.18631
38. GitOfThoughts. arXiv:2606.14470
39. ChronoMem. arXiv:2607.27773
40. MemStrata / Temporal Validity in Retrieval Memory. arXiv:2606.26511
41. TARL. arXiv:2608.03699
42. Memory Worth / When to Forget. arXiv:2604.12007
43. MemTX. arXiv:2607.23929
44. Always-On Agents / AOEP-v0. arXiv:2606.30306
45. LatticeMind. arXiv:2608.08236
46. Cordon. arXiv:2606.17573
47. STALE. arXiv:2605.06527
48. VTA / Implicit stale dependencies. arXiv:2608.01619
49. GEM / MemState. arXiv:2605.26252
50. CMGL (Certified Memory Governance Layer). https://github.com/kadubon/certified-memory-governance-layer
51. TierMem. arXiv:2602.17913
52. MSCE. arXiv:2607.16621
53. FadeMem. arXiv:2601.18642
54. MemR3. arXiv:2512.20237
55. Oblivion. arXiv:2604.00131
56. SF-AMS. arXiv:2607.22562
57. MemCon. arXiv:2607.13591
58. SCM. arXiv:2604.20943
59. GAM. arXiv:2604.12285
60. Agentic Context Management. arXiv:2607.21503
61. LightMem. arXiv:2510.18866
62. HippoRAG. NeurIPS 2024
63. Quipu. arXiv:2608.16813
64. ProGraph. arXiv:2607.19359
65. EMG / experience-memory correction paths (2026 ecosystem)
66. AgentIR / MemFuse-style cascade RRF (2026 ecosystem)
67. Governed Memory. arXiv:2603.17787
68. HyMem. arXiv:2608.15703
69. Deterministic freshness assembly. arXiv:2606.01435
70. MemTxn. arXiv:2607.27834
71. Governed Shared Memory / MemClaw. arXiv:2606.24535
72. BudgetMem. arXiv:2602.06025
73. Skill library retrieval study. arXiv:2608.06196
74. ERSkill. arXiv:2608.12720
75. ConsistencyGate. arXiv:2607.22962
76. MemGate. arXiv:2606.06054
77. Mnemonic sovereignty survey. arXiv:2604.16548
78. SodaMem. arXiv:2608.08055
79. MemRefine. arXiv:2606.13177
80. MemFuse. arXiv:2608.18704
81. TGMS. arXiv:2607.10265
82. Agent-native memory / MemoryData. arXiv:2606.24775
83. TMA-NM / MEM-INV. arXiv:2606.24322
84. GhostWriter / AM-Sentry. arXiv:2607.06595
85. Chronos vulnerability. arXiv:2607.19433
86. MemForest / MemTree. arXiv:2605.23986
87. xMemory. arXiv:2602.02007
88. MemSecBench. arXiv:2607.27080
89. SleepGate. arXiv:2603.14517
90. DepRepair. arXiv:2608.10502
91. MPBench / Untrusted Input. arXiv:2606.04329
92. MemPoison. arXiv:2607.14651
93. Salami / MemCollusion. arXiv:2608.01637
94. Knowledge layer. arXiv:2604.11364
95. PRISM secret leakage. arXiv:2605.10614
96. CapSeal. arXiv:2604.16762
97. AgentDoG. arXiv:2601.18491
98. MemWeaver. arXiv:2601.18204
99. MemHop / ProGraph. arXiv:2607.19359
100. MemEvolve. arXiv:2512.18746
101. MindMemOS. arXiv:2608.12428
102. MEMGUARD. arXiv:2605.28009
103. PAMU. arXiv:2510.09720
104. BEAM benchmark (agent memory at 1M/10M scale)
105. HaluMem. arXiv:2511.03506
106. REMem. arXiv:2602.13530
107. EverMemOS. ACL 2026 long
108. Hu et al. LoRA. arXiv:2106.09685 · ICLR 2022
109. Pfeiffer et al. AdapterFusion. arXiv:2005.00247 · EACL 2021
110. Mahabadi et al. Compacter. arXiv:2106.04647 · NeurIPS 2021
111. Liu et al. (IA)^3 / T-Few. arXiv:2205.05638 · NeurIPS 2022
112. Ben Zaken et al. BitFit. arXiv:2106.10199 · ACL 2022
113. Liu et al. DoRA. arXiv:2402.09353
114. Dettmers et al. QLoRA. arXiv:2305.14314 · NeurIPS 2023
115. Zhang et al. AdaLoRA. arXiv:2303.10512 · ICLR 2023
116. Kopiczko et al. VeRA. arXiv:2310.11454 · ICLR 2024
117. Rücklé et al. AdapterDrop. arXiv:2010.11918 · EACL 2021
118. Meng et al. PiSSA. arXiv:2404.02948 · NeurIPS 2024
119. Guo et al. Diff Pruning. arXiv:2012.07463 · ACL 2021
120. Renduchintala et al. Tied-LoRA. arXiv:2311.09578
121. Hayou et al. LoRA+. arXiv:2402.12354
122. Zhang et al. LoRA-FA. arXiv:2308.03303
123. Valipour et al. DyLoRA. arXiv:2210.07558
124. Bałazy et al. LoRA-XS. arXiv:2405.17604
125. Zhu et al. AsymmetryLoRA. arXiv:2402.16842 · ICML 2024
126. Wang et al. LoRA-GA. arXiv:2407.05000 · NeurIPS 2024
127. Jiang et al. MoRA. arXiv:2405.12130
128. Kalajdzievski. rsLoRA. arXiv:2312.03732
129. Yeh et al. LoKr. arXiv:2309.14859
130. Hyeon-Woo et al. / PEFT LoHa. arXiv:2108.06098
131. Gao et al. FourierFT. arXiv:2405.03003
132. Houlsby et al. Parameter-Efficient Transfer Learning. arXiv:1902.00751 · ICML 2019
133. Wu et al. ReFT. arXiv:2404.03592
134. Qiu et al. OFT / Liu et al. BOFT. arXiv:2311.06243
135. Zhang et al. MiSS. arXiv:2409.15371
136. Zhang et al. DropLoRA. arXiv:2508.17337
137. Zhao et al. GaLore. arXiv:2403.03507
138. Bhardwaj et al. SHiRA. arXiv:2406.13175 · NeurIPS 2024
139. Bilican et al. WaveFT. arXiv:2505.12532
