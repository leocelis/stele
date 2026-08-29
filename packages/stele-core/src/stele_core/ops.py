"""Public six-op (+ promote/link) API over SteleStore (C1–C8)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.adapters import project_receipt
from stele_core.distill import assert_distilled_entry
from stele_core.activation import (
    connection_density as act_connection_density,
    retention_score,
    spread_activate as act_spread_activate,
)
from stele_core.derived_index import rebuild_sqlite_index, search_sqlite_index
from stele_core.execution import (
    authority_gate as exec_authority_gate,
    claim_closure as exec_claim_closure,
    list_executions as exec_list_executions,
    record_execution as exec_record_execution,
    verify_execution_chain as exec_verify_execution_chain,
    verify_execution_claim as exec_verify_execution_claim,
)
from stele_core.repair import (
    cascade_descendants as repair_cascade_descendants,
    cascade_exposure as repair_cascade_exposure,
    non_revival_probe as repair_non_revival_probe,
    repair_plan as repair_repair_plan,
    repair_select_mincut as repair_repair_select_mincut,
)
from stele_core.cupmem import (
    adjudicate_update as cupmem_adjudicate_update,
    authorize_retrieval as cupmem_authorize_retrieval,
    unknown_current_slots as cupmem_unknown_current_slots,
)
from stele_core.cmgl import (
    admit_gate as cmgl_admit_gate,
    list_admit_receipts as cmgl_list_admit_receipts,
    verify_admit_receipt as cmgl_verify_admit_receipt,
)
from stele_core.tiermem import (
    escalate as tiermem_escalate,
    get_raw_page as tiermem_get_raw_page,
    put_raw_page as tiermem_put_raw_page,
    sufficiency_gate as tiermem_sufficiency_gate,
    summary_entry_template as tiermem_summary_entry_template,
)
from stele_core.msce import (
    crystallize_skill as msce_crystallize_skill,
    skill_catalog as msce_skill_catalog,
    skill_eligibility as msce_skill_eligibility,
    value_backfill as msce_value_backfill,
)
from stele_core.fademem import (
    fade_scan as fade_fade_scan,
    fade_strength as fade_fade_strength,
    fusion_candidates as fade_fusion_candidates,
    weibull_relevance as fade_weibull_relevance,
)
from stele_core.memr3 import (
    evidence_gap as memr3_evidence_gap,
    gap_tracker_update as memr3_gap_tracker_update,
    reflective_retrieve_plan as memr3_reflective_retrieve_plan,
)
from stele_core.archive import (
    archive_plan as arch_archive_plan,
    list_archived as arch_list_archived,
)
from stele_core.sfams import (
    cis_scan as sfams_cis_scan,
    composite_importance as sfams_composite_importance,
)
from stele_core.memcon import control_suggest as memcon_control_suggest
from stele_core.scm import (
    sleep_cycle_plan as scm_sleep_cycle_plan,
    sleep_trigger as scm_sleep_trigger,
    value_tag as scm_value_tag,
    wm_clear as scm_wm_clear,
    wm_list as scm_wm_list,
    wm_push as scm_wm_push,
)
from stele_core.gam import (
    consolidate_candidates as gam_consolidate_candidates,
    episodic_buffer as gam_episodic_buffer,
    semantic_boundary as gam_semantic_boundary,
)
from stele_core.acm import (
    anticipate_prefetch as acm_anticipate_prefetch,
    verify_compaction as acm_verify_compaction,
)
from stele_core.lightmem import (
    assign_stage as light_assign_stage,
    sensory_filter as light_sensory_filter,
    stage_budget_plan as light_stage_budget_plan,
    stage_inventory as light_stage_inventory,
    topic_segments as light_topic_segments,
)
from stele_core.hipporag import (
    multi_hop_retrieve as hippo_multi_hop_retrieve,
    ppr_scores as hippo_ppr_scores,
)
from stele_core.mapgate import (
    action_risk_gate as map_action_risk_gate,
    write_gate as map_write_gate,
)
from stele_core.prograph import (
    extract_residuals as pg_extract_residuals,
    profile_expand as pg_profile_expand,
    register_entities as pg_register_entities,
    residual_augment as pg_residual_augment,
)
from stele_core.emg import (
    insight_inject as emg_insight_inject,
    match_correction as emg_match_correction,
)
from stele_core.agentir import (
    cascade_route as air_cascade_route,
    multi_channel_fuse as air_multi_channel_fuse,
)
from stele_core.govmem import (
    dual_project as gm_dual_project,
    entity_context as gm_entity_context,
    entity_leak_probe as gm_entity_leak_probe,
    governance_route as gm_governance_route,
    session_delta_deliver as gm_session_delta_deliver,
    session_delta_open as gm_session_delta_open,
    session_delta_status as gm_session_delta_status,
)
from stele_core.hymem import (
    classify_slot as hy_classify_slot,
    isolate_pack as hy_isolate_pack,
)
from stele_core.freshness import (
    assemble_current as fr_assemble_current,
    extract_version_markers as fr_extract_version_markers,
    freshness_resolve as fr_freshness_resolve,
    hop_freshness as fr_hop_freshness,
)
from stele_core.patchtxn import (
    patch_test as pt_patch_test,
    recover_active_map as pt_recover_active_map,
    temporal_resolve as pt_temporal_resolve,
)
from stele_core.fleetprop import (
    fleet_scope_gate as fp_fleet_scope_gate,
    propagate_plan as fp_propagate_plan,
    stale_propagation_scan as fp_stale_propagation_scan,
)
from stele_core.budgetmem import (
    budget_module_plan as bm_budget_module_plan,
    budget_tier_route as bm_budget_tier_route,
    query_complexity as bm_query_complexity,
    tier_params as bm_tier_params,
)
from stele_core.skillrank import (
    skill_prereq_expand as sr_skill_prereq_expand,
    skill_rank as sr_skill_rank,
)
from stele_core.erskill import (
    BUILTIN_SKILLS,
    compose_retrieval_skill as er_compose_retrieval_skill,
    list_primitives as er_list_primitives,
    list_retrieval_skills as er_list_retrieval_skills,
    route_retrieval_skill as er_route_retrieval_skill,
)
from stele_core.consistencygate import (
    consistency_admit as cg_consistency_admit,
    support_score as cg_support_score,
)
from stele_core.memgate import (
    retrieval_admit as mg_retrieval_admit,
    task_conditioned_pack as mg_task_conditioned_pack,
)
from stele_core.mnemonic import (
    post_delete_verify as mn_post_delete_verify,
    rollback_plan as mn_rollback_plan,
    sovereignty_checklist as mn_sovereignty_checklist,
)
from stele_core.sodamem import (
    cited_pack as soda_cited_pack,
    density_fuse as soda_density_fuse,
    evidence_plan as soda_evidence_plan,
)
from stele_core.memrefine import (
    compress_candidates as mr_compress_candidates,
    refine_plan as mr_refine_plan,
)
from stele_core.ariadne import (
    bridge_discover as ar_bridge_discover,
    fuse_cluster as ar_fuse_cluster,
    merge_link_add as ar_merge_link_add,
)
from stele_core.tgms import (
    claim_verify as tgms_claim_verify,
    operator_cost_estimate as tgms_operator_cost_estimate,
    plan_static_verify as tgms_plan_static_verify,
    result_digest as tgms_result_digest,
    summary_quarantine_scan as tgms_summary_quarantine_scan,
)
from stele_core.memdata import (
    localized_maintenance_plan as md_localized_maintenance_plan,
    maintenance_cost_compare as md_maintenance_cost_compare,
)
from stele_core.tmanm import (
    act_authority_gate as tma_act_authority_gate,
    launder_scan as tma_launder_scan,
    origin_bind as tma_origin_bind,
    propagate_origin as tma_propagate_origin,
)
from stele_core.amsentry import (
    retrieval_screen as am_retrieval_screen,
    save_policy as am_save_policy,
)
from stele_core.memforest import (
    build_memtree as mf_build_memtree,
    coarse_to_fine as mf_coarse_to_fine,
    dirty_path_plan as mf_dirty_path_plan,
)
from stele_core.xmemory import (
    build_themes_from_entries as xm_build_themes_from_entries,
    split_merge_plan as xm_split_merge_plan,
    theme_attach as xm_theme_attach,
    top_down_pack as xm_top_down_pack,
)
from stele_core.memsec import (
    execute_chain_probe as ms_execute_chain_probe,
    lifecycle_report as ms_lifecycle_report,
    persistence_probe as ms_persistence_probe,
    selective_repair_plan as ms_selective_repair_plan,
)
from stele_core.sleepgate import (
    conflict_tag as sg_conflict_tag,
    consolidate_survivors as sg_consolidate_survivors,
    forget_gate_plan as sg_forget_gate_plan,
    pi_depth_scan as sg_pi_depth_scan,
)
from stele_core.amemguard import consensus_admit as ag_consensus_admit
from stele_core.deprepair import (
    build_mem_action_graph as dr_build_mem_action_graph,
    dependency_trace as dr_dependency_trace,
    preserve_independent as dr_preserve_independent,
    selective_replay_plan as dr_selective_replay_plan,
)
from stele_core.mpbench import (
    channel_admit_batch as mp_channel_admit_batch,
    classify_write_channel as mp_classify_write_channel,
    source_isolation_gate as mp_source_isolation_gate,
    write_channel_inventory as mp_write_channel_inventory,
)
from stele_core.mempoison import (
    collusion_risk_gate as mpz_collusion_risk_gate,
    compositional_coalition_scan as mpz_compositional_coalition_scan,
    dormant_trigger_scan as mpz_dormant_trigger_scan,
    mempoison_ladder_report as mpz_mempoison_ladder_report,
    salami_pair_probe as mpz_salami_pair_probe,
    slot_coverage as mpz_slot_coverage,
    threat_tier_classify as mpz_threat_tier_classify,
)
from stele_core.knowledgelayer import (
    classify_persistence_layer as kl_classify_persistence_layer,
    intelligence_reject_gate as kl_intelligence_reject_gate,
    knowledge_protect_scan as kl_knowledge_protect_scan,
    layer_inventory as kl_layer_inventory,
    persistence_policy as kl_persistence_policy,
)
from stele_core.credguard import (
    credential_reject_gate as cg_credential_reject_gate,
    credential_scan_entry as cg_credential_scan_entry,
    credential_store_scan as cg_credential_store_scan,
)
from stele_core.oblivion_gate import (
    reasoning_reserve_plan as og_reasoning_reserve_plan,
    uncertainty_retrieve_gate as og_uncertainty_retrieve_gate,
    uncertainty_score as og_uncertainty_score,
)
from stele_core.pam import (
    build_merkle_dag as pam_build_merkle_dag,
    check_capability as pam_check_capability,
    classify_memory_component as pam_classify_memory_component,
    issue_capability_token as pam_issue_capability_token,
    rehydrate_safe_plan as pam_rehydrate_safe_plan,
    selective_disclose as pam_selective_disclose,
    verify_merkle_root as pam_verify_merkle_root,
)
from stele_core.capseal import (
    action_capability_inventory as cs_action_capability_inventory,
    capability_export_probe as cs_capability_export_probe,
    check_action_capability as cs_check_action_capability,
    issue_action_capability as cs_issue_action_capability,
)
from stele_core.agentdog import (
    classify_failure_mode as ad_classify_failure_mode,
    classify_real_world_harm as ad_classify_real_world_harm,
    classify_risk_source as ad_classify_risk_source,
    diagnose_trajectory as ad_diagnose_trajectory,
    diagnose_trajectory_step as ad_diagnose_trajectory_step,
    safe_but_unreasonable_scan as ad_safe_but_unreasonable_scan,
    taxonomy_inventory as ad_taxonomy_inventory,
)
from stele_core.memweaver import (
    build_hybrid_weave as mw_build_hybrid_weave,
    dual_channel_retrieve as mw_dual_channel_retrieve,
    experience_abstract_plan as mw_experience_abstract_plan,
    multi_hop_depth_score as mw_multi_hop_depth_score,
    temporal_session_conflict_scan as mw_temporal_session_conflict_scan,
    weave_layer_assign as mw_weave_layer_assign,
)
from stele_core.memevolve import (
    architecture_profile as me_architecture_profile,
    diagnose_architecture as me_diagnose_architecture,
    list_design_space as me_list_design_space,
    propose_architecture_variants as me_propose_architecture_variants,
    rank_architecture_fitness as me_rank_architecture_fitness,
    select_architecture_parents as me_select_architecture_parents,
)
from stele_core.mindmemos import (
    contamination_scan as mm_contamination_scan,
    dreaming_consolidate_plan as mm_dreaming_consolidate_plan,
    ept_classify as mm_ept_classify,
    feedback_revise_plan as mm_feedback_revise_plan,
    functional_role_assign as mm_functional_role_assign,
    skill_evolve_plan as mm_skill_evolve_plan,
    type_route_retrieve as mm_type_route_retrieve,
)
from stele_core.pamu import (
    extract_preference_signal as pu_extract_preference_signal,
    format_preference_prompt as pu_format_preference_prompt,
    fuse_preference as pu_fuse_preference,
    preference_change_detect as pu_preference_change_detect,
    preference_update_plan as pu_preference_update_plan,
)
from stele_core.beam import (
    abstention_gate as bm_abstention_gate,
    beam_category_inventory as bm_beam_category_inventory,
    beam_eval_pack as bm_beam_eval_pack,
    classify_beam_query as bm_classify_beam_query,
    contradiction_resolve_plan as bm_contradiction_resolve_plan,
    event_order_check as bm_event_order_check,
    knowledge_update_check as bm_knowledge_update_check,
    localize_hallucination_stage as bm_localize_hallucination_stage,
)
from stele_core.remem import (
    agentic_retrieve_plan as rm_agentic_retrieve_plan,
    build_hybrid_episodic_graph as rm_build_hybrid_episodic_graph,
    extract_episodic_gist as rm_extract_episodic_gist,
    extract_temporal_facts as rm_extract_temporal_facts,
    ordinal_event_query as rm_ordinal_event_query,
    situational_bind as rm_situational_bind,
)
from stele_core.evermemos import (
    consolidate_memscenes as ev_consolidate_memscenes,
    foresight_filter as ev_foresight_filter,
    form_memcell as ev_form_memcell,
    necessity_sufficiency_check as ev_necessity_sufficiency_check,
    profile_evolve_plan as ev_profile_evolve_plan,
    reconstructive_recollect as ev_reconstructive_recollect,
)
from stele_core.memoryos import (
    classify_memory_tier as mo_classify_memory_tier,
    heat_score as mo_heat_score,
    hierarchical_retrieve as mo_hierarchical_retrieve,
    mtm_evict_plan as mo_mtm_evict_plan,
    promote_to_lpm_plan as mo_promote_to_lpm_plan,
    segment_pages as mo_segment_pages,
    stm_to_mtm_plan as mo_stm_to_mtm_plan,
)
from stele_core.nemori import (
    anticipatory_schema as nm_anticipatory_schema,
    deserves_memory_gate as nm_deserves_memory_gate,
    distill_batch_plan as nm_distill_batch_plan,
    integrate_episodic_narrative as nm_integrate_episodic_narrative,
    prediction_error_distill as nm_prediction_error_distill,
)
from stele_core.hindsight import (
    classify_network as hs_classify_network,
    network_inventory as hs_network_inventory,
    opinion_reinforce as hs_opinion_reinforce,
    recall_multi_strategy as hs_recall_multi_strategy,
    reflect_plan as hs_reflect_plan,
    retain_plan as hs_retain_plan,
)
from stele_core.reasoningbank import (
    consolidate_strategy_plan as rb_consolidate_strategy_plan,
    distill_strategy_item as rb_distill_strategy_item,
    failure_lesson_gate as rb_failure_lesson_gate,
    matts_contrastive_plan as rb_matts_contrastive_plan,
    retrieve_strategies as rb_retrieve_strategies,
)
from stele_core.memskill import (
    designer_evolve_plan as ms_designer_evolve_plan,
    execute_skill_plan as ms_execute_skill_plan,
    init_skill_bank as ms_init_skill_bank,
    record_hard_case as ms_record_hard_case,
    select_skills as ms_select_skills,
    span_partition as ms_span_partition,
)
from stele_core.memoryr1 import (
    classify_memory_op as mr_classify_memory_op,
    conflict_update_plan as mr_conflict_update_plan,
    delete_stale_plan as mr_delete_stale_plan,
    memory_op_plan as mr_memory_op_plan,
    noop_gate as mr_noop_gate,
)
from stele_core.gmemory import (
    bidirectional_retrieve as gm_bidirectional_retrieve,
    build_query_graph as gm_build_query_graph,
    classify_graph_tier as gm_classify_graph_tier,
    downward_interaction_traverse as gm_downward_interaction_traverse,
    hierarchy_update_plan as gm_hierarchy_update_plan,
    upward_insight_traverse as gm_upward_insight_traverse,
)
from stele_core.memma import (
    answerability_check as mm_answerability_check,
    meta_thinker_guidance as mm_meta_thinker_guidance,
    repair_from_probes as mm_repair_from_probes,
    synthesize_probe_qa as mm_synthesize_probe_qa,
    verify_probes as mm_verify_probes,
)
from stele_core.awm import (
    induce_workflow as awm_induce_workflow,
    online_induce_gate as awm_online_induce_gate,
    retrieve_workflows as awm_retrieve_workflows,
    workflow_memory_add_plan as awm_workflow_memory_add_plan,
    workflow_step_budget as awm_workflow_step_budget,
)
from stele_core.rrm import (
    anomaly_trigger as rrm_anomaly_trigger,
    distill_retrieval_experience as rrm_distill_retrieval_experience,
    experience_lifecycle_score as rrm_experience_lifecycle_score,
    isolate_factual_from_procedural as rrm_isolate_factual_from_procedural,
    prune_experience_plan as rrm_prune_experience_plan,
    query_level_guidance as rrm_query_level_guidance,
)
from stele_core.reme import (
    adaptive_rewrite_plan as reme_adaptive_rewrite_plan,
    multi_faceted_distill as reme_multi_faceted_distill,
    scenario_retrieve as reme_scenario_retrieve,
    selective_add_plan as reme_selective_add_plan,
    utility_after_reuse as reme_utility_after_reuse,
    utility_prune_plan as reme_utility_prune_plan,
)
from stele_core.cheatsheet import (
    compact_memory_gate as dc_compact_memory_gate,
    curator_decide as dc_curator_decide,
    dc_rs_order_check as dc_dc_rs_order_check,
    extract_cheatsheet_snippet as dc_extract_cheatsheet_snippet,
    retrieve_cheatsheet as dc_retrieve_cheatsheet,
)
from stele_core.expel import (
    experience_pool_add as expel_experience_pool_add,
    insight_importance_gate as expel_insight_importance_gate,
    insight_op as expel_insight_op,
    retrieve_insights as expel_retrieve_insights,
    retrieve_similar_successes as expel_retrieve_similar_successes,
)
from stele_core.reflective_mm import (
    prospective_reflect as rmm_d_prospective_reflect,
    rerank_memories as rmm_d_rerank_memories,
    retrieval_refine_plan as rmm_d_retrieval_refine_plan,
    retrospective_cite_feedback as rmm_d_retrospective_cite_feedback,
    retrieve_topic_memories as rmm_d_retrieve_topic_memories,
    topic_memory_bank as rmm_d_topic_memory_bank,
)
from stele_core.trace2skill import (
    collect_trajectory_label as t2s_collect_trajectory_label,
    hierarchical_merge_patches as t2s_hierarchical_merge_patches,
    parallel_patch_pool as t2s_parallel_patch_pool,
    prefer_parallel_over_sequential as t2s_prefer_parallel_over_sequential,
    propose_trajectory_patch as t2s_propose_trajectory_patch,
    skill_mode_gate as t2s_skill_mode_gate,
)
from stele_core.evomemory import (
    evolution_similarity_hint as evo_evolution_similarity_hint,
    evomem_refine_plan as evo_evomem_refine_plan,
    exprag_retrieve as evo_exprag_retrieve,
    search_predict_evolve_check as evo_search_predict_evolve_check,
    streaming_task_append as evo_streaming_task_append,
)
from stele_core.memalpha import (
    classify_memory_slot as ma_classify_memory_slot,
    compression_ratio as ma_compression_ratio,
    length_generalization_gate as ma_length_generalization_gate,
    memalpha_reward_bundle as ma_memalpha_reward_bundle,
    memory_write_op as ma_memory_write_op,
    process_chunk_plan as ma_process_chunk_plan,
)
from stele_core.agenther import (
    classify_failure as ah_classify_failure,
    extract_replay_outcome as ah_extract_replay_outcome,
    hindsight_relabel_plan as ah_hindsight_relabel_plan,
    multi_judge_accept as ah_multi_judge_accept,
    package_training_pair as ah_package_training_pair,
)
from stele_core.preflect import (
    distill_planning_error as pf_distill_planning_error,
    preflect_before_execute_gate as pf_preflect_before_execute_gate,
    prospective_critique_plan as pf_prospective_critique_plan,
    replan_on_deviation as pf_replan_on_deviation,
    revise_plan_proposal as pf_revise_plan_proposal,
)
from stele_core.skillflow import (
    orchestration_action_select as sf_orchestration_action_select,
    phase_evolve_gate as sf_phase_evolve_gate,
    skill_curation_decide as sf_skill_curation_decide,
    skill_marginal_flow as sf_skill_marginal_flow,
    step_importance as sf_step_importance,
    ttb_residual as sf_ttb_residual,
)
from stele_core.procmem import (
    define_skill_triplet as pm_define_skill_triplet,
    ppo_gate_verify as pm_ppo_gate_verify,
    semantic_gradient_candidate as pm_semantic_gradient_candidate,
    skill_score_maintain as pm_skill_score_maintain,
    skill_select_gate as pm_skill_select_gate,
    skill_terminate_check as pm_skill_terminate_check,
)
from stele_core.memrl import (
    ieu_record as mr_ieu_record,
    semantic_vs_utility_warn as mr_semantic_vs_utility_warn,
    two_phase_retrieve as mr_two_phase_retrieve,
    utility_q_update as mr_utility_q_update,
    value_aware_select as mr_value_aware_select,
)
from stele_core.evolver import (
    distill_principle as ev_distill_principle,
    lifecycle_phase_gate as ev_lifecycle_phase_gate,
    principle_dedupe_plan as ev_principle_dedupe_plan,
    principle_metric_score as ev_principle_metric_score,
    prune_low_score_principles as ev_prune_low_score_principles,
    search_experience_action as ev_search_experience_action,
)
from stele_core.agentevolver import (
    attribute_step_credit as ae_attribute_step_credit,
    curiosity_explore_plan as ae_curiosity_explore_plan,
    experience_when_content as ae_experience_when_content,
    mixed_rollout_split as ae_mixed_rollout_split,
    self_question_task as ae_self_question_task,
)
from stele_core.skillweaver import (
    distill_skill_api as sw_distill_skill_api,
    hone_skill_api as sw_hone_skill_api,
    practice_skill_run as sw_practice_skill_run,
    propose_skill as sw_propose_skill,
    skill_library_register as sw_skill_library_register,
    transfer_skill_gate as sw_transfer_skill_gate,
)
from stele_core.skillroute import (
    compose_skill_dag as sr_compose_skill_dag,
    decompose_task_steps as sr_decompose_task_steps,
    granularity_match_check as sr_granularity_match_check,
    retrieve_skills_for_steps as sr_retrieve_skills_for_steps,
    sad_feedback_loop as sr_sad_feedback_loop,
)
from stele_core.abszero import (
    abszero_joint_objective as az_abszero_joint_objective,
    executor_verify_gate as az_executor_verify_gate,
    learnability_reward as az_learnability_reward,
    propose_reasoning_task as az_propose_reasoning_task,
    solve_reward as az_solve_reward,
    validate_task_structure as az_validate_task_structure,
)
from stele_core.rzero import (
    challenger_propose as rz_challenger_propose,
    coevolve_round_plan as rz_coevolve_round_plan,
    curriculum_band_filter as rz_curriculum_band_filter,
    majority_vote_label as rz_majority_vote_label,
    solver_binary_reward as rz_solver_binary_reward,
    uncertainty_reward as rz_uncertainty_reward,
)
from stele_core.echomem import (
    budget_binding_check as em_budget_binding_check,
    history_collapse_gate as em_history_collapse_gate,
    provenance_credit_mask as em_provenance_credit_mask,
    reconstruct_policy_context as em_reconstruct_policy_context,
    select_turn_memories as em_select_turn_memories,
    write_turn_memory as em_write_turn_memory,
)
from stele_core.agent0 import (
    curriculum_propose_task as a0_curriculum_propose_task,
    curriculum_reward as a0_curriculum_reward,
    executor_frontier_filter as a0_executor_frontier_filter,
    symbiotic_round_plan as a0_symbiotic_round_plan,
    tool_aware_pressure as a0_tool_aware_pressure,
    tool_use_reward as a0_tool_use_reward,
)
from stele_core.mae import (
    mae_judge_score as mae_judge_score_fn,
    mae_propose_question as mae_propose_question_fn,
    mae_proposer_reward as mae_proposer_reward_fn,
    mae_quality_filter as mae_quality_filter_fn,
    mae_solve_attempt as mae_solve_attempt_fn,
    mae_triad_round_plan as mae_triad_round_plan_fn,
)
from stele_core.sagema import (
    sage_challenge_task as sage_challenge_task_fn,
    sage_closed_loop_round as sage_closed_loop_round_fn,
    sage_critic_filter as sage_critic_filter_fn,
    sage_drift_gate as sage_drift_gate_fn,
    sage_plan_steps as sage_plan_steps_fn,
    sage_solve_with_plan as sage_solve_with_plan_fn,
)
from stele_core.memgen import (
    faculty_classify as mg_faculty_classify,
    interweave_cycle_plan as mg_interweave_cycle_plan,
    memory_trigger_decide as mg_memory_trigger_decide,
    sparse_invoke_penalty as mg_sparse_invoke_penalty,
    weave_latent_memory as mg_weave_latent_memory,
    weaver_only_update_gate as mg_weaver_only_update_gate,
)
from stele_core.metis import (
    crystallize_plan_to_tool as mt_crystallize_plan_to_tool,
    dual_retrieve as mt_dual_retrieve,
    metis_loop_plan as mt_metis_loop_plan,
    promote_kind_gate as mt_promote_kind_gate,
    representation_tradeoff as mt_representation_tradeoff,
    text_experience_store as mt_text_experience_store,
)
from stele_core.samule import (
    failure_centric_gate as sa_failure_centric_gate,
    foresight_reflect as sa_foresight_reflect,
    inter_task_transfer as sa_inter_task_transfer,
    intra_task_taxonomy as sa_intra_task_taxonomy,
    merge_reflections as sa_merge_reflections,
    single_trajectory_reflect as sa_single_trajectory_reflect,
)
from stele_core.liveevo import (
    compile_task_guideline as le_compile_task_guideline,
    experience_bank_record as le_experience_bank_record,
    forget_stale_experience as le_forget_stale_experience,
    liveevo_online_round as le_liveevo_online_round,
    meta_guideline_record as le_meta_guideline_record,
    update_experience_weight as le_update_experience_weight,
)
from stele_core.socratic import (
    socratic_closed_loop as so_socratic_closed_loop,
    socratic_generator_distill as so_socratic_generator_distill,
    socratic_seed_bootstrap as so_socratic_seed_bootstrap,
    socratic_solver_preference as so_socratic_solver_preference,
    socratic_teacher_craft as so_socratic_teacher_craft,
    socratic_weakness_target as so_socratic_weakness_target,
)
from stele_core.spiral import (
    spiral_baseline_ema as sp_spiral_baseline_ema,
    spiral_multi_game_plan as sp_spiral_multi_game_plan,
    spiral_opponent_strength as sp_spiral_opponent_strength,
    spiral_rae_advantage as sp_spiral_rae_advantage,
    spiral_self_play_match as sp_spiral_self_play_match,
    spiral_transfer_pattern as sp_spiral_transfer_pattern,
)
from stele_core.smith import (
    smith_create_tool as sm_smith_create_tool,
    smith_curriculum_difficulty as sm_smith_curriculum_difficulty,
    smith_loop_plan as sm_smith_loop_plan,
    smith_retrieve_episode as sm_smith_retrieve_episode,
    smith_store_memory as sm_smith_store_memory,
    smith_tool_reuse_gate as sm_smith_tool_reuse_gate,
)
from stele_core.hmem import (
    hmem_consolidate_nodes as hm_hmem_consolidate_nodes,
    hmem_decompose_query as hm_hmem_decompose_query,
    hmem_evolution_gate as hm_hmem_evolution_gate,
    hmem_hybrid_retrieve as hm_hmem_hybrid_retrieve,
    hmem_leaf_event as hm_hmem_leaf_event,
    hmem_link_entities as hm_hmem_link_entities,
)
from stele_core.himem import (
    himem_extract_note as hi_himem_extract_note,
    himem_link_episode_note as hi_himem_link_episode_note,
    himem_loop_plan as hi_himem_loop_plan,
    himem_reconsolidate as hi_himem_reconsolidate,
    himem_retrieve_strategy as hi_himem_retrieve_strategy,
    himem_segment_episode as hi_himem_segment_episode,
)
from stele_core.hmeml import (
    hmeml_descend as hl_hmeml_descend,
    hmeml_efficiency_score as hl_hmeml_efficiency_score,
    hmeml_loop_plan as hl_hmeml_loop_plan,
    hmeml_parent_link as hl_hmeml_parent_link,
    hmeml_route_query as hl_hmeml_route_query,
    hmeml_store_level as hl_hmeml_store_level,
)
from stele_core.hyperskill import (
    hyperskill_add_hyperedge as hs_hyperskill_add_hyperedge,
    hyperskill_add_skill as hs_hyperskill_add_skill,
    hyperskill_add_subtask as hs_hyperskill_add_subtask,
    hyperskill_dual_path_retrieve as hs_hyperskill_dual_path_retrieve,
    hyperskill_loop_plan as hs_hyperskill_loop_plan,
    hyperskill_maintain_plan as hs_hyperskill_maintain_plan,
    hyperskill_rank_skills as hs_hyperskill_rank_skills,
)
from stele_core.dcpm import (
    dcpm_cross_domain_collision as dc_dcpm_cross_domain_collision,
    dcpm_day_write as dc_dcpm_day_write,
    dcpm_hierarchy_level as dc_dcpm_hierarchy_level,
    dcpm_loop_plan as dc_dcpm_loop_plan,
    dcpm_night_induce as dc_dcpm_night_induce,
    dcpm_supersedes_chain as dc_dcpm_supersedes_chain,
)
from stele_core.memos import (
    memos_compose as mo_memos_compose,
    memos_create_cube as mo_memos_create_cube,
    memos_fuse_gate as mo_memos_fuse_gate,
    memos_lifecycle as mo_memos_lifecycle,
    memos_loop_plan as mo_memos_loop_plan,
    memos_migrate as mo_memos_migrate,
    memos_schedule as mo_memos_schedule,
)
from stele_core.skillcraft import (
    skillcraft_execute_skill as sc_skillcraft_execute_skill,
    skillcraft_get_skill as sc_skillcraft_get_skill,
    skillcraft_list_skills as sc_skillcraft_list_skills,
    skillcraft_loop_plan as sc_skillcraft_loop_plan,
    skillcraft_save_skill as sc_skillcraft_save_skill,
    skillcraft_token_efficiency as sc_skillcraft_token_efficiency,
    skillcraft_verify_skill as sc_skillcraft_verify_skill,
)
from stele_core.cma import (
    cma_associative_route as cm_cma_associative_route,
    cma_consolidate as cm_cma_consolidate,
    cma_loop_plan as cm_cma_loop_plan,
    cma_persist as cm_cma_persist,
    cma_probe_gate as cm_cma_probe_gate,
    cma_selective_retain as cm_cma_selective_retain,
    cma_temporal_chain as cm_cma_temporal_chain,
)
from stele_core.agentfold import (
    agentfold_context_budget as af_agentfold_context_budget,
    agentfold_deep_consolidate as af_agentfold_deep_consolidate,
    agentfold_fold_command as af_agentfold_fold_command,
    agentfold_granular_condense as af_agentfold_granular_condense,
    agentfold_loop_plan as af_agentfold_loop_plan,
    agentfold_workspace_split as af_agentfold_workspace_split,
)
from stele_core.memengine import (
    memengine_bind_model as me_memengine_bind_model,
    memengine_compose_operation as me_memengine_compose_operation,
    memengine_config_set as me_memengine_config_set,
    memengine_loop_plan as me_memengine_loop_plan,
    memengine_pluggable as me_memengine_pluggable,
    memengine_reflect_plan as me_memengine_reflect_plan,
    memengine_register_function as me_memengine_register_function,
)
from stele_core.simplemem import (
    simplemem_compress as sm_simplemem_compress,
    simplemem_intent_scope as sm_simplemem_intent_scope,
    simplemem_loop_plan as sm_simplemem_loop_plan,
    simplemem_multiview_index as sm_simplemem_multiview_index,
    simplemem_synthesize as sm_simplemem_synthesize,
    simplemem_token_ratio as sm_simplemem_token_ratio,
)
from stele_core.omem import (
    omem_extract_persona as om_omem_extract_persona,
    omem_hierarchy_retrieve as om_omem_hierarchy_retrieve,
    omem_loop_plan as om_omem_loop_plan,
    omem_profile_gate as om_omem_profile_gate,
    omem_scale_memory_time as om_omem_scale_memory_time,
    omem_update_event as om_omem_update_event,
)
from stele_core.mandol import (
    mandol_agglomerate as md_mandol_agglomerate,
    mandol_basic_unit as md_mandol_basic_unit,
    mandol_hybrid_retrieve as md_mandol_hybrid_retrieve,
    mandol_loop_plan as md_mandol_loop_plan,
    mandol_query_route as md_mandol_query_route,
    mandol_semantic_map_put as md_mandol_semantic_map_put,
    mandol_token_budget as md_mandol_token_budget,
)
from stele_core.memanto import (
    memanto_conflict_resolve as ma_memanto_conflict_resolve,
    memanto_latency_gate as ma_memanto_latency_gate,
    memanto_loop_plan as ma_memanto_loop_plan,
    memanto_retrieve as ma_memanto_retrieve,
    memanto_store_typed as ma_memanto_store_typed,
    memanto_version as ma_memanto_version,
)
from stele_core.zep import (
    zep_add_episode as zp_zep_add_episode,
    zep_bitemporal as zp_zep_bitemporal,
    zep_cross_session as zp_zep_cross_session,
    zep_link_entities as zp_zep_link_entities,
    zep_loop_plan as zp_zep_loop_plan,
    zep_synthesize as zp_zep_synthesize,
)
from stele_core.memgpt import (
    memgpt_archival_search as mg_memgpt_archival_search,
    memgpt_loop_plan as mg_memgpt_loop_plan,
    memgpt_main_capacity as mg_memgpt_main_capacity,
    memgpt_page_in as mg_memgpt_page_in,
    memgpt_page_out as mg_memgpt_page_out,
    memgpt_recall_search as mg_memgpt_recall_search,
)
from stele_core.ripplemem import (
    ripple_expand as rp_ripple_expand,
    ripple_link_entity as rp_ripple_link_entity,
    ripple_loop_plan as rp_ripple_loop_plan,
    ripple_recollect_gate as rp_ripple_recollect_gate,
    ripple_seed_retrieve as rp_ripple_seed_retrieve,
    ripple_store_episode as rp_ripple_store_episode,
)
from stele_core.fluxmem import (
    flux_connect_form as fx_flux_connect_form,
    flux_consolidate as fx_flux_consolidate,
    flux_feedback_refine as fx_flux_feedback_refine,
    flux_loop_plan as fx_flux_loop_plan,
    flux_maturity_gate as fx_flux_maturity_gate,
    flux_prune_interference as fx_flux_prune_interference,
    flux_repair_link as fx_flux_repair_link,
)
from stele_core.qumem import (
    qumem_decompose as qm_qumem_decompose,
    qumem_infer_user_state as qm_qumem_infer_user_state,
    qumem_loop_plan as qm_qumem_loop_plan,
    qumem_plan_queries as qm_qumem_plan_queries,
    qumem_segment_episode as qm_qumem_segment_episode,
    qumem_temporal_valid as qm_qumem_temporal_valid,
)
from stele_core.vikingmem import (
    viking_extract_event as vk_viking_extract_event,
    viking_loop_plan as vk_viking_loop_plan,
    viking_rerank as vk_viking_rerank,
    viking_time_weighted_recall as vk_viking_time_weighted_recall,
    viking_timeline_compress as vk_viking_timeline_compress,
    viking_update_entity as vk_viking_update_entity,
)
from stele_core.recmem import (
    recmem_buffer_subconscious as rm_recmem_buffer_subconscious,
    recmem_consolidate_episodic as rm_recmem_consolidate_episodic,
    recmem_loop_plan as rm_recmem_loop_plan,
    recmem_merge_retrieve as rm_recmem_merge_retrieve,
    recmem_recurrence_gate as rm_recmem_recurrence_gate,
    recmem_semantic_refine as rm_recmem_semantic_refine,
)
from stele_core.memorybank import (
    mbank_forget_curve as mb_mbank_forget_curve,
    mbank_loop_plan as mb_mbank_loop_plan,
    mbank_personality_synth as mb_mbank_personality_synth,
    mbank_reinforce as mb_mbank_reinforce,
    mbank_store_memory as mb_mbank_store_memory,
    mbank_summon as mb_mbank_summon,
)
from stele_core.rfmem import (
    rfmem_alpha_mix as rf_rfmem_alpha_mix,
    rfmem_familiarity_score as rf_rfmem_familiarity_score,
    rfmem_loop_plan as rf_rfmem_loop_plan,
    rfmem_path_route as rf_rfmem_path_route,
    rfmem_recollect_expand as rf_rfmem_recollect_expand,
    rfmem_top_k_familiar as rf_rfmem_top_k_familiar,
)
from stele_core.agemem import (
    agemem_discard_plan as ag_agemem_discard_plan,
    agemem_loop_plan as ag_agemem_loop_plan,
    agemem_ltm_store as ag_agemem_ltm_store,
    agemem_retrieve as ag_agemem_retrieve,
    agemem_stm_manage as ag_agemem_stm_manage,
    agemem_summarize as ag_agemem_summarize,
)
from stele_core.memgas import (
    memgas_associate as mg_memgas_associate,
    memgas_entropy_route as mg_memgas_entropy_route,
    memgas_filter_plan as mg_memgas_filter_plan,
    memgas_loop_plan as mg_memgas_loop_plan,
    memgas_select_granularity as mg_memgas_select_granularity,
    memgas_unit as mg_memgas_unit,
)
from stele_core.memwalker import (
    memwalker_build_node as mw_memwalker_build_node,
    memwalker_gather as mw_memwalker_gather,
    memwalker_loop_plan as mw_memwalker_loop_plan,
    memwalker_navigate as mw_memwalker_navigate,
    memwalker_path_gate as mw_memwalker_path_gate,
    memwalker_segment as mw_memwalker_segment,
)
from stele_core.memgraphrag import (
    mgr_detect_conflict as mgr_mgr_detect_conflict,
    mgr_loop_plan as mgr_mgr_loop_plan,
    mgr_multilayer_retrieve as mgr_mgr_multilayer_retrieve,
    mgr_propagate as mgr_mgr_propagate,
    mgr_resolve_plan as mgr_mgr_resolve_plan,
    mgr_store_layer as mgr_mgr_store_layer,
)
from stele_core.raptor import (
    raptor_cluster as rp_raptor_cluster,
    raptor_collapsed_retrieve as rp_raptor_collapsed_retrieve,
    raptor_embed_chunk as rp_raptor_embed_chunk,
    raptor_loop_plan as rp_raptor_loop_plan,
    raptor_summarize_node as rp_raptor_summarize_node,
    raptor_tree_traverse as rp_raptor_tree_traverse,
)
from stele_core.lightrag import (
    lightrag_dual_retrieve as lr_lightrag_dual_retrieve,
    lightrag_graph_vector_fuse as lr_lightrag_graph_vector_fuse,
    lightrag_incremental_update as lr_lightrag_incremental_update,
    lightrag_index_entity as lr_lightrag_index_entity,
    lightrag_index_relation as lr_lightrag_index_relation,
    lightrag_loop_plan as lr_lightrag_loop_plan,
)
from stele_core.memorag import (
    memorag_clue as mr_memorag_clue,
    memorag_dual_system as mr_memorag_dual_system,
    memorag_generate_plan as mr_memorag_generate_plan,
    memorag_loop_plan as mr_memorag_loop_plan,
    memorag_memorize as mr_memorag_memorize,
    memorag_retrieve_by_clue as mr_memorag_retrieve_by_clue,
)
from stele_core.pageindex import (
    pageindex_add_section as pi_pageindex_add_section,
    pageindex_build_toc as pi_pageindex_build_toc,
    pageindex_loop_plan as pi_pageindex_loop_plan,
    pageindex_reason_nav as pi_pageindex_reason_nav,
    pageindex_select_section as pi_pageindex_select_section,
    pageindex_trace_path as pi_pageindex_trace_path,
)
from stele_core.selfrag import (
    selfrag_loop_plan as sr_selfrag_loop_plan,
    selfrag_need_retrieve as sr_selfrag_need_retrieve,
    selfrag_relevance_critique as sr_selfrag_relevance_critique,
    selfrag_select_best as sr_selfrag_select_best,
    selfrag_support_critique as sr_selfrag_support_critique,
    selfrag_utility_critique as sr_selfrag_utility_critique,
)
from stele_core.memobrain import (
    memobrain_dep_edge as mb_memobrain_dep_edge,
    memobrain_flush_budget as mb_memobrain_flush_budget,
    memobrain_fold_subtraj as mb_memobrain_fold_subtraj,
    memobrain_loop_plan as mb_memobrain_loop_plan,
    memobrain_prune_invalid as mb_memobrain_prune_invalid,
    memobrain_salience_keep as mb_memobrain_salience_keep,
)
from stele_core.crag import (
    crag_action_select as cg_crag_action_select,
    crag_ambiguous_blend as cg_crag_ambiguous_blend,
    crag_correct_refine as cg_crag_correct_refine,
    crag_evaluate_retrieval as cg_crag_evaluate_retrieval,
    crag_loop_plan as cg_crag_loop_plan,
    crag_web_fallback_plan as cg_crag_web_fallback_plan,
)
from stele_core.hyde import (
    hyde_encode_proxy as hy_hyde_encode_proxy,
    hyde_filter_hallucination as hy_hyde_filter_hallucination,
    hyde_ground_corpus as hy_hyde_ground_corpus,
    hyde_hypothetical_doc as hy_hyde_hypothetical_doc,
    hyde_loop_plan as hy_hyde_loop_plan,
    hyde_retrieve_by_hyp as hy_hyde_retrieve_by_hyp,
)
from stele_core.adaptiverag import (
    adaptiverag_classify_complexity as ar_adaptiverag_classify_complexity,
    adaptiverag_loop_plan as ar_adaptiverag_loop_plan,
    adaptiverag_multi_step as ar_adaptiverag_multi_step,
    adaptiverag_no_retrieve as ar_adaptiverag_no_retrieve,
    adaptiverag_select_strategy as ar_adaptiverag_select_strategy,
    adaptiverag_single_step as ar_adaptiverag_single_step,
)
from stele_core.flare import (
    flare_active_step as fl_flare_active_step,
    flare_anticipate_sentence as fl_flare_anticipate_sentence,
    flare_loop_plan as fl_flare_loop_plan,
    flare_low_confidence as fl_flare_low_confidence,
    flare_regenerate_sentence as fl_flare_regenerate_sentence,
    flare_retrieve_for_regen as fl_flare_retrieve_for_regen,
)
from stele_core.graphreader import (
    graphreader_build_node as gr_graphreader_build_node,
    graphreader_loop_plan as gr_graphreader_loop_plan,
    graphreader_note_insight as gr_graphreader_note_insight,
    graphreader_read_neighbors as gr_graphreader_read_neighbors,
    graphreader_read_node as gr_graphreader_read_node,
    graphreader_reflect_plan as gr_graphreader_reflect_plan,
)
from stele_core.gretriever import (
    gretriever_highlight as gv_gretriever_highlight,
    gretriever_loop_plan as gv_gretriever_loop_plan,
    gretriever_node_prize as gv_gretriever_node_prize,
    gretriever_pcst_select as gv_gretriever_pcst_select,
    gretriever_soft_prompt_plan as gv_gretriever_soft_prompt_plan,
    gretriever_subgraph as gv_gretriever_subgraph,
)
from stele_core.rqrag import (
    rqrag_decompose as rq_rqrag_decompose,
    rqrag_disambiguate as rq_rqrag_disambiguate,
    rqrag_loop_plan as rq_rqrag_loop_plan,
    rqrag_refine_mode as rq_rqrag_refine_mode,
    rqrag_retrieve_refined as rq_rqrag_retrieve_refined,
    rqrag_rewrite as rq_rqrag_rewrite,
)
from stele_core.ircot import (
    ircot_answer_ready as ir_ircot_answer_ready,
    ircot_cot_step as ir_ircot_cot_step,
    ircot_hallucination_check as ir_ircot_hallucination_check,
    ircot_interleave as ir_ircot_interleave,
    ircot_loop_plan as ir_ircot_loop_plan,
    ircot_retrieve_guided as ir_ircot_retrieve_guided,
)
from stele_core.replug import (
    replug_blackbox_forward as rp_replug_blackbox_forward,
    replug_ensemble_probs as rp_replug_ensemble_probs,
    replug_loop_plan as rp_replug_loop_plan,
    replug_prepend_doc as rp_replug_prepend_doc,
    replug_retrieve_docs as rp_replug_retrieve_docs,
    replug_supervise_retriever as rp_replug_supervise_retriever,
)
from stele_core.iterretgen import (
    iterretgen_adapt_retriever as it_iterretgen_adapt_retriever,
    iterretgen_generate as it_iterretgen_generate,
    iterretgen_iterate as it_iterretgen_iterate,
    iterretgen_loop_plan as it_iterretgen_loop_plan,
    iterretgen_retrieve_next as it_iterretgen_retrieve_next,
    iterretgen_use_as_query as it_iterretgen_use_as_query,
)
from stele_core.planrag import (
    planrag_analysis_query as pr_planrag_analysis_query,
    planrag_decide as pr_planrag_decide,
    planrag_loop_plan as pr_planrag_loop_plan,
    planrag_make_plan as pr_planrag_make_plan,
    planrag_replan as pr_planrag_replan,
    planrag_retrieve_data as pr_planrag_retrieve_data,
)
from stele_core.rrr import (
    rrr_loop_plan as rr_rrr_loop_plan,
    rrr_read as rr_rrr_read,
    rrr_reader_feedback as rr_rrr_reader_feedback,
    rrr_retrieve as rr_rrr_retrieve,
    rrr_rewrite_query as rr_rrr_rewrite_query,
    rrr_train_rewriter_plan as rr_rrr_train_rewriter_plan,
)
from stele_core.dsp import (
    dsp_bootstrap_demo as ds_dsp_bootstrap_demo,
    dsp_compose_program as ds_dsp_compose_program,
    dsp_loop_plan as ds_dsp_loop_plan,
    dsp_multihop_hop as ds_dsp_multihop_hop,
    dsp_predict as ds_dsp_predict,
    dsp_search as ds_dsp_search,
)
from stele_core.genread import (
    genread_answer as gn_genread_answer,
    genread_compare_retrieve as gn_genread_compare_retrieve,
    genread_generate_context as gn_genread_generate_context,
    genread_ground_optional as gn_genread_ground_optional,
    genread_hybrid as gn_genread_hybrid,
    genread_loop_plan as gn_genread_loop_plan,
)
from stele_core.selfask import (
    selfask_compose_answer as sa_selfask_compose_answer,
    selfask_demo_prompt as sa_selfask_demo_prompt,
    selfask_followup as sa_selfask_followup,
    selfask_loop_plan as sa_selfask_loop_plan,
    selfask_search_intercept as sa_selfask_search_intercept,
    selfask_stop as sa_selfask_stop,
)
from stele_core.react import (
    react_action as rc_react_action,
    react_finish as rc_react_finish,
    react_loop_plan as rc_react_loop_plan,
    react_observe as rc_react_observe,
    react_thought as rc_react_thought,
    react_trajectory as rc_react_trajectory,
)
from stele_core.thinkongraph import (
    tog_answer_from_paths as tog_tog_answer_from_paths,
    tog_beam_prune as tog_tog_beam_prune,
    tog_explore_neighbors as tog_tog_explore_neighbors,
    tog_init_entity as tog_tog_init_entity,
    tog_loop_plan as tog_tog_loop_plan,
    tog_path_score as tog_tog_path_score,
)
from stele_core.toolformer import (
    tf_api_candidate as tf_tf_api_candidate,
    tf_demo_apis as tf_tf_demo_apis,
    tf_execute_proxy as tf_tf_execute_proxy,
    tf_filter_call as tf_tf_filter_call,
    tf_incorporate_result as tf_tf_incorporate_result,
    tf_loop_plan as tf_tf_loop_plan,
)
from stele_core.reflexion import (
    rx_evaluate as rx_rx_evaluate,
    rx_loop_plan as rx_rx_loop_plan,
    rx_memory_store as rx_rx_memory_store,
    rx_next_trial as rx_rx_next_trial,
    rx_trial_run as rx_rx_trial_run,
    rx_verbal_reflect as rx_rx_verbal_reflect,
)
from stele_core.selfcons import (
    sc_collect_answers as sc_sc_collect_answers,
    sc_loop_plan as sc_sc_loop_plan,
    sc_majority_vote as sc_sc_majority_vote,
    sc_marginalize as sc_sc_marginalize,
    sc_sample_path as sc_sc_sample_path,
    sc_temperature as sc_sc_temperature,
)
from stele_core.treeofthoughts import (
    tot_backtrack as tot_tot_backtrack,
    tot_evaluate as tot_tot_evaluate,
    tot_expand as tot_tot_expand,
    tot_loop_plan as tot_tot_loop_plan,
    tot_propose as tot_tot_propose,
    tot_select_best as tot_tot_select_best,
)
from stele_core.leasttomost import (
    ltm_carry_forward as ltm_ltm_carry_forward,
    ltm_compose_final as ltm_ltm_compose_final,
    ltm_decompose as ltm_ltm_decompose,
    ltm_easy_to_hard as ltm_ltm_easy_to_hard,
    ltm_loop_plan as ltm_ltm_loop_plan,
    ltm_solve_sub as ltm_ltm_solve_sub,
)
from stele_core.graphofthoughts import (
    got_add_thought as got_got_add_thought,
    got_aggregate as got_got_aggregate,
    got_feedback as got_got_feedback,
    got_link as got_got_link,
    got_loop_plan as got_got_loop_plan,
    got_score_graph as got_got_score_graph,
)
from stele_core.programofthoughts import (
    pot_disentangle as pot_pot_disentangle,
    pot_emit_program as pot_pot_emit_program,
    pot_loop_plan as pot_pot_loop_plan,
    pot_read_result as pot_pot_read_result,
    pot_sandbox_run as pot_pot_sandbox_run,
    pot_self_consistency as pot_pot_self_consistency,
)
from stele_core.algorithmofthoughts import (
    aot_explore_subtree as aot_aot_explore_subtree,
    aot_load_algorithm as aot_aot_load_algorithm,
    aot_loop_plan as aot_aot_loop_plan,
    aot_query_budget as aot_aot_query_budget,
    aot_surpass_algo as aot_aot_surpass_algo,
    aot_tunnel_vision as aot_aot_tunnel_vision,
)
from stele_core.reasoningviaplanning import (
    rap_balance as rap_rap_balance,
    rap_expand as rap_rap_expand,
    rap_loop_plan as rap_rap_loop_plan,
    rap_reward as rap_rap_reward,
    rap_select_path as rap_rap_select_path,
    rap_world_state as rap_rap_world_state,
)
from stele_core.skeletonofthought import (
    sot_emit_skeleton as sot_sot_emit_skeleton,
    sot_extract_points as sot_sot_extract_points,
    sot_latency_gain as sot_sot_latency_gain,
    sot_loop_plan as sot_sot_loop_plan,
    sot_parallel_expand as sot_sot_parallel_expand,
    sot_router as sot_sot_router,
)
from stele_core.bufferofthoughts import (
    bot_buffer_update as bot_bot_buffer_update,
    bot_cost_ratio as bot_bot_cost_ratio,
    bot_distill_template as bot_bot_distill_template,
    bot_instantiate as bot_bot_instantiate,
    bot_loop_plan as bot_bot_loop_plan,
    bot_retrieve_template as bot_bot_retrieve_template,
)
from stele_core.selfdiscover import (
    sd_adapt as sd_sd_adapt,
    sd_apply_instance as sd_sd_apply_instance,
    sd_compute_ratio as sd_sd_compute_ratio,
    sd_implement as sd_sd_implement,
    sd_loop_plan as sd_sd_loop_plan,
    sd_select_modules as sd_sd_select_modules,
)
from stele_core.metaprompting import (
    mp_assign_expert as mp_mp_assign_expert,
    mp_break_task as mp_mp_break_task,
    mp_loop_plan as mp_mp_loop_plan,
    mp_oversee as mp_mp_oversee,
    mp_task_agnostic as mp_mp_task_agnostic,
    mp_verify as mp_mp_verify,
)
from stele_core.quietstar import (
    qs_hard_token_aid as qs_qs_hard_token_aid,
    qs_loop_plan as qs_qs_loop_plan,
    qs_mix_head as qs_qs_mix_head,
    qs_parallel_sample as qs_qs_parallel_sample,
    qs_thought_bounds as qs_qs_thought_bounds,
    qs_zero_shot_flag as qs_qs_zero_shot_flag,
)
from stele_core.decomposedprompting import (
    dep_decompose as dep_dep_decompose,
    dep_delegate as dep_dep_delegate,
    dep_library_size as dep_dep_library_size,
    dep_loop_plan as dep_dep_loop_plan,
    dep_recurse as dep_dep_recurse,
    dep_swap_symbolic as dep_dep_swap_symbolic,
)
from stele_core.selftaughtreasoner import (
    star_bootstrap_round as star_star_bootstrap_round,
    star_filter_correct as star_star_filter_correct,
    star_finetune_proxy as star_star_finetune_proxy,
    star_generate as star_star_generate,
    star_loop_plan as star_star_loop_plan,
    star_rationalize as star_star_rationalize,
)
from stele_core.cumulativereasoning import (
    cr_accumulate as cr_cr_accumulate,
    cr_loop_plan as cr_cr_loop_plan,
    cr_propose as cr_cr_propose,
    cr_report as cr_cr_report,
    cr_roles as cr_cr_roles,
    cr_verify as cr_cr_verify,
)
from stele_core.planandsolve import (
    ps_calc_guard as ps_ps_calc_guard,
    ps_devise_plan as ps_ps_devise_plan,
    ps_execute as ps_ps_execute,
    ps_loop_plan as ps_ps_loop_plan,
    ps_missing_step_fix as ps_ps_missing_step_fix,
    ps_plus_extract as ps_ps_plus_extract,
)
from stele_core.progressivehint import (
    php_base_answer as php_php_base_answer,
    php_combine_sc as php_php_combine_sc,
    php_emit_hint as php_php_emit_hint,
    php_loop_plan as php_php_loop_plan,
    php_reask as php_php_reask,
    php_stable_stop as php_php_stable_stop,
)
from stele_core.agentcoder import (
    ac_loop_plan as ac_ac_loop_plan,
    ac_pass_gate as ac_ac_pass_gate,
    ac_programmer as ac_ac_programmer,
    ac_refine as ac_ac_refine,
    ac_test_designer as ac_ac_test_designer,
    ac_test_executor as ac_ac_test_executor,
)
from stele_core.programaided import (
    pal_decompose_only as pal_pal_decompose_only,
    pal_emit_program as pal_pal_emit_program,
    pal_loop_plan as pal_pal_loop_plan,
    pal_offload_solve as pal_pal_offload_solve,
    pal_read_answer as pal_pal_read_answer,
    pal_vs_cot as pal_pal_vs_cot,
)
from stele_core.faithfulcot import (
    fcot_faithfulness as fcot_fcot_faithfulness,
    fcot_interleave as fcot_fcot_interleave,
    fcot_loop_plan as fcot_fcot_loop_plan,
    fcot_solve as fcot_fcot_solve,
    fcot_translate as fcot_fcot_translate,
    fcot_vs_cot as fcot_fcot_vs_cot,
)
from stele_core.lats import (
    lats_env_feedback as lats_lats_env_feedback,
    lats_expand as lats_lats_expand,
    lats_loop_plan as lats_lats_loop_plan,
    lats_reflect as lats_lats_reflect,
    lats_select as lats_lats_select,
    lats_value as lats_lats_value,
)
from stele_core.voyager import (
    voy_compose as voy_voy_compose,
    voy_curriculum as voy_voy_curriculum,
    voy_loop_plan as voy_voy_loop_plan,
    voy_self_verify as voy_voy_self_verify,
    voy_skill_retrieve as voy_voy_skill_retrieve,
    voy_skill_store as voy_voy_skill_store,
)
from stele_core.rewoo import (
    rewoo_decouple as rewoo_rewoo_decouple,
    rewoo_loop_plan as rewoo_rewoo_loop_plan,
    rewoo_plan as rewoo_rewoo_plan,
    rewoo_solver as rewoo_rewoo_solver,
    rewoo_token_save as rewoo_rewoo_token_save,
    rewoo_worker as rewoo_rewoo_worker,
)
from stele_core.critic import (
    critic_draft as critic_critic_draft,
    critic_iterate as critic_critic_iterate,
    critic_loop_plan as critic_critic_loop_plan,
    critic_revise as critic_critic_revise,
    critic_stop as critic_critic_stop,
    critic_tool_check as critic_critic_tool_check,
)
from stele_core.deductive import (
    dv_ground as dv_dv_ground,
    dv_loop_plan as dv_dv_loop_plan,
    dv_natural_program as dv_dv_natural_program,
    dv_premise_scope as dv_dv_premise_scope,
    dv_step_verify as dv_dv_step_verify,
    dv_unanimity as dv_dv_unanimity,
)
from stele_core.hugginggpt import (
    hgpt_execute as hgpt_hgpt_execute,
    hgpt_loop_plan as hgpt_hgpt_loop_plan,
    hgpt_modality as hgpt_hgpt_modality,
    hgpt_plan as hgpt_hgpt_plan,
    hgpt_select as hgpt_hgpt_select,
    hgpt_summarize as hgpt_hgpt_summarize,
)
from stele_core.multiagentdebate import (
    mad_converge as mad_mad_converge,
    mad_critique as mad_mad_critique,
    mad_debate as mad_mad_debate,
    mad_factuality as mad_mad_factuality,
    mad_loop_plan as mad_mad_loop_plan,
    mad_propose as mad_mad_propose,
)
from stele_core.autocot import (
    autocot_cluster as autocot_autocot_cluster,
    autocot_diversity as autocot_autocot_diversity,
    autocot_generate as autocot_autocot_generate,
    autocot_heuristic as autocot_autocot_heuristic,
    autocot_loop_plan as autocot_autocot_loop_plan,
    autocot_sample as autocot_autocot_sample,
)
from stele_core.camel import (
    camel_complete as camel_camel_complete,
    camel_inception as camel_camel_inception,
    camel_loop_plan as camel_camel_loop_plan,
    camel_roles as camel_camel_roles,
    camel_society as camel_camel_society,
    camel_turn as camel_camel_turn,
)
from stele_core.chameleon import (
    cham_compose as cham_cham_compose,
    cham_constraint as cham_cham_constraint,
    cham_execute as cham_cham_execute,
    cham_inventory as cham_cham_inventory,
    cham_loop_plan as cham_cham_loop_plan,
    cham_plan as cham_cham_plan,
)
from stele_core.recursionofthought import (
    rot_conquer as rot_rot_conquer,
    rot_context_limit as rot_rot_context_limit,
    rot_divide as rot_rot_divide,
    rot_loop_plan as rot_rot_loop_plan,
    rot_merge as rot_rot_merge,
    rot_trigger as rot_rot_trigger,
)
from stele_core.activeprompt import (
    ap_annotate as ap_ap_annotate,
    ap_loop_plan as ap_ap_loop_plan,
    ap_pool as ap_ap_pool,
    ap_sample as ap_ap_sample,
    ap_select as ap_ap_select,
    ap_uncertainty as ap_ap_uncertainty,
)
from stele_core.analogical import (
    ana_adapt as ana_ana_adapt,
    ana_knowledge as ana_ana_knowledge,
    ana_loop_plan as ana_ana_loop_plan,
    ana_no_label as ana_ana_no_label,
    ana_recall as ana_ana_recall,
    ana_solve as ana_ana_solve,
)
from stele_core.complexityprompt import (
    cbp_loop_plan as cbp_cbp_loop_plan,
    cbp_robust as cbp_cbp_robust,
    cbp_sample_chains as cbp_cbp_sample_chains,
    cbp_score as cbp_cbp_score,
    cbp_select as cbp_cbp_select,
    cbp_vote_complex as cbp_cbp_vote_complex,
)
from stele_core.stepback import (
    sb_abstract as sb_sb_abstract,
    sb_detail_trap as sb_sb_detail_trap,
    sb_loop_plan as sb_sb_loop_plan,
    sb_path as sb_sb_path,
    sb_principle as sb_sb_principle,
    sb_reason as sb_sb_reason,
)
from stele_core.multimodalcot import (
    mmcot_fuse as mmcot_mmcot_fuse,
    mmcot_hallucination as mmcot_mmcot_hallucination,
    mmcot_infer as mmcot_mmcot_infer,
    mmcot_loop_plan as mmcot_mmcot_loop_plan,
    mmcot_rationale as mmcot_mmcot_rationale,
    mmcot_separate as mmcot_mmcot_separate,
)
from stele_core.maieutic import (
    mai_abduce as mai_mai_abduce,
    mai_consistent as mai_mai_consistent,
    mai_loop_plan as mai_mai_loop_plan,
    mai_recurse as mai_mai_recurse,
    mai_sat as mai_mai_sat,
    mai_unreliable as mai_mai_unreliable,
)
from stele_core.selfrefine import (
    sr_feedback as sr_sr_feedback,
    sr_generate as sr_sr_generate,
    sr_iterate as sr_sr_iterate,
    sr_loop_plan as sr_sr_loop_plan,
    sr_no_train as sr_sr_no_train,
    sr_refine as sr_sr_refine,
)
from stele_core.metacognitive import (
    mcp_confidence as mcp_mcp_confidence,
    mcp_interpret as mcp_mcp_interpret,
    mcp_justify as mcp_mcp_justify,
    mcp_loop_plan as mcp_mcp_loop_plan,
    mcp_recognize as mcp_mcp_recognize,
    mcp_reevaluate as mcp_mcp_reevaluate,
)
from stele_core.threadofthought import (
    thot_analyze as thot_thot_analyze,
    thot_loop_plan as thot_thot_loop_plan,
    thot_plug as thot_thot_plug,
    thot_segment as thot_thot_segment,
    thot_select as thot_thot_select,
    thot_synthesize as thot_thot_synthesize,
)
from stele_core.thoughtpropagation import (
    tprop_amend as tprop_tprop_amend,
    tprop_compat as tprop_tprop_compat,
    tprop_loop_plan as tprop_tprop_loop_plan,
    tprop_propose as tprop_tprop_propose,
    tprop_reuse as tprop_tprop_reuse,
    tprop_solve as tprop_tprop_solve,
)
from stele_core.system2attention import (
    s2a_attend as s2a_s2a_attend,
    s2a_factuality as s2a_s2a_factuality,
    s2a_loop_plan as s2a_s2a_loop_plan,
    s2a_regenerate as s2a_s2a_regenerate,
    s2a_respond as s2a_s2a_respond,
    s2a_sycophancy as s2a_s2a_sycophancy,
)
from stele_core.contrastivecot import (
    ccot_auto as ccot_ccot_auto,
    ccot_contrast as ccot_ccot_contrast,
    ccot_invalid as ccot_ccot_invalid,
    ccot_loop_plan as ccot_ccot_loop_plan,
    ccot_reason as ccot_ccot_reason,
    ccot_valid as ccot_ccot_valid,
)
from stele_core.tabcot import (
    tabcot_extract as tabcot_tabcot_extract,
    tabcot_header as tabcot_tabcot_header,
    tabcot_infer2d as tabcot_tabcot_infer2d,
    tabcot_loop_plan as tabcot_tabcot_loop_plan,
    tabcot_row as tabcot_tabcot_row,
    tabcot_zeroshot as tabcot_tabcot_zeroshot,
)
from stele_core.everythingofthoughts import (
    xot_flexible as xot_xot_flexible,
    xot_loop_plan as xot_xot_loop_plan,
    xot_map as xot_xot_map,
    xot_mcts as xot_xot_mcts,
    xot_penrose as xot_xot_penrose,
    xot_revise as xot_xot_revise,
)
from stele_core.chainofverification import (
    cove_answer as cove_cove_answer,
    cove_draft as cove_cove_draft,
    cove_final as cove_cove_final,
    cove_hallucination as cove_cove_hallucination,
    cove_loop_plan as cove_cove_loop_plan,
    cove_plan as cove_cove_plan,
)
from stele_core.verifyandedit import (
    ved_edit as ved_ved_edit,
    ved_knowledge as ved_ved_knowledge,
    ved_loop_plan as ved_ved_loop_plan,
    ved_predict as ved_ved_predict,
    ved_search as ved_ved_search,
    ved_uncertain as ved_ved_uncertain,
)
from stele_core.selfverification import (
    sve_forward as sve_sve_forward,
    sve_loop_plan as sve_sve_loop_plan,
    sve_mask as sve_sve_mask,
    sve_repredict as sve_sve_repredict,
    sve_score as sve_sve_score,
    sve_select as sve_sve_select,
)
from stele_core.chainofdensity import (
    cod_entities as cod_cod_entities,
    cod_fuse as cod_cod_fuse,
    cod_length as cod_cod_length,
    cod_loop_plan as cod_cod_loop_plan,
    cod_sparse as cod_cod_sparse,
    cod_tradeoff as cod_cod_tradeoff,
)
from stele_core.hintbeforesolving import (
    hsp_answer as hsp_hsp_answer,
    hsp_compose as hsp_hsp_compose,
    hsp_hint as hsp_hsp_hint,
    hsp_loop_plan as hsp_hsp_loop_plan,
    hsp_quality as hsp_hsp_quality,
    hsp_solve as hsp_hsp_solve,
)
from stele_core.emotionprompt import (
    emo_append as emo_emo_append,
    emo_loop_plan as emo_emo_loop_plan,
    emo_psych as emo_emo_psych,
    emo_run as emo_emo_run,
    emo_stimulus as emo_emo_stimulus,
    emo_truth as emo_emo_truth,
)
from stele_core.automaticpromptengineer import (
    ape_human as ape_ape_human,
    ape_loop_plan as ape_ape_loop_plan,
    ape_propose as ape_ape_propose,
    ape_score as ape_ape_score,
    ape_select as ape_ape_select,
    ape_steer as ape_ape_steer,
)
from stele_core.promptbreeder import (
    pbr_diversity as pbr_pbr_diversity,
    pbr_fitness as pbr_pbr_fitness,
    pbr_init as pbr_pbr_init,
    pbr_loop_plan as pbr_pbr_loop_plan,
    pbr_mutate as pbr_pbr_mutate,
    pbr_selfref as pbr_pbr_selfref,
)
from stele_core.optimizationbyprompting import (
    opro_append as opro_opro_append,
    opro_best as opro_opro_best,
    opro_loop_plan as opro_opro_loop_plan,
    opro_meta as opro_opro_meta,
    opro_propose as opro_opro_propose,
    opro_score as opro_opro_score,
)
from stele_core.evoprompt import (
    evp_cross as evp_evp_cross,
    evp_ea as evp_evp_ea,
    evp_init as evp_evp_init,
    evp_loop_plan as evp_evp_loop_plan,
    evp_mutate as evp_evp_mutate,
    evp_select as evp_evp_select,
)
from stele_core.protegi import (
    ptg_bandit as ptg_ptg_bandit,
    ptg_beam as ptg_ptg_beam,
    ptg_edit as ptg_ptg_edit,
    ptg_gradient as ptg_ptg_gradient,
    ptg_jailbreak as ptg_ptg_jailbreak,
    ptg_loop_plan as ptg_ptg_loop_plan,
)
from stele_core.promptagent import (
    pag_backprop as pag_pag_backprop,
    pag_expand as pag_pag_expand,
    pag_expert as pag_pag_expert,
    pag_loop_plan as pag_pag_loop_plan,
    pag_reflect as pag_pag_reflect,
    pag_state as pag_pag_state,
)
from stele_core.momentumaidedprompt import (
    mapo_beam as mapo_mapo_beam,
    mapo_faster as mapo_mapo_faster,
    mapo_loop_plan as mapo_mapo_loop_plan,
    mapo_momentum as mapo_mapo_momentum,
    mapo_posgrad as mapo_mapo_posgrad,
    mapo_ucb as mapo_mapo_ucb,
)
from stele_core.grips import (
    grips_accept as grips_grips_accept,
    grips_api as grips_grips_api,
    grips_edit as grips_grips_edit,
    grips_loop_plan as grips_grips_loop_plan,
    grips_score as grips_grips_score,
    grips_seed as grips_grips_seed,
)
from stele_core.tempera import (
    tmpa_act as tmpa_tmpa_act,
    tmpa_adapt as tmpa_tmpa_adapt,
    tmpa_efficiency as tmpa_tmpa_efficiency,
    tmpa_loop_plan as tmpa_tmpa_loop_plan,
    tmpa_reward as tmpa_tmpa_reward,
    tmpa_state as tmpa_tmpa_state,
)
from stele_core.rlprompt import (
    rlp_discrete as rlp_rlp_discrete,
    rlp_init as rlp_rlp_init,
    rlp_loop_plan as rlp_rlp_loop_plan,
    rlp_reward as rlp_rlp_reward,
    rlp_sample as rlp_rlp_sample,
    rlp_update as rlp_rlp_update,
)
from stele_core.autoprompt import (
    aup_loop_plan as aup_aup_loop_plan,
    aup_probe as aup_aup_probe,
    aup_score as aup_aup_score,
    aup_search as aup_aup_search,
    aup_template as aup_aup_template,
    aup_trigger as aup_aup_trigger,
)
from stele_core.prefixtuning import (
    pfx_freeze as pfx_pfx_freeze,
    pfx_generate as pfx_pfx_generate,
    pfx_loop_plan as pfx_pfx_loop_plan,
    pfx_optimize as pfx_pfx_optimize,
    pfx_prefix as pfx_pfx_prefix,
    pfx_task as pfx_pfx_task,
)
from stele_core.ptuningv2 import (
    ptv_deep as ptv_ptv_deep,
    ptv_inject as ptv_ptv_inject,
    ptv_loop_plan as ptv_ptv_loop_plan,
    ptv_seqtag as ptv_ptv_seqtag,
    ptv_tune as ptv_ptv_tune,
    ptv_universal as ptv_ptv_universal,
)
from stele_core.prompttuning import (
    ptl_input_only as ptl_ptl_input_only,
    ptl_loop_plan as ptl_ptl_loop_plan,
    ptl_optimize as ptl_ptl_optimize,
    ptl_prepend as ptl_ptl_prepend,
    ptl_scale as ptl_ptl_scale,
    ptl_soft as ptl_ptl_soft,
)
from stele_core.softpromptmixtures import (
    msp_ensemble as msp_msp_ensemble,
    msp_loop_plan as msp_msp_loop_plan,
    msp_mix as msp_msp_mix,
    msp_probe as msp_msp_probe,
    msp_soft as msp_msp_soft,
    msp_underest as msp_msp_underest,
)
from stele_core.softprompttransfer import (
    spot_embed as spot_spot_embed,
    spot_init as spot_spot_init,
    spot_loop_plan as spot_spot_loop_plan,
    spot_retrieve as spot_spot_retrieve,
    spot_source as spot_spot_source,
    spot_vs_tune as spot_spot_vs_tune,
)
from stele_core.attemptprompt import (
    atm_attend as atm_atm_attend,
    atm_loop_plan as atm_atm_loop_plan,
    atm_mix as atm_atm_mix,
    atm_modular as atm_atm_modular,
    atm_source as atm_atm_source,
    atm_target as atm_atm_target,
)
from stele_core.multitaskprompttuning import (
    mptp_efficient as mptp_mptp_efficient,
    mptp_factor as mptp_mptp_factor,
    mptp_loop_plan as mptp_mptp_loop_plan,
    mptp_score as mptp_mptp_score,
    mptp_shared as mptp_mptp_shared,
    mptp_transfer as mptp_mptp_transfer,
)
from stele_core.lora import (
    lora_freeze as lora_lora_freeze,
    lora_latency as lora_lora_latency,
    lora_loop_plan as lora_lora_loop_plan,
    lora_merge as lora_lora_merge,
    lora_rank as lora_lora_rank,
    lora_train as lora_lora_train,
)
from stele_core.adapterfusion import (
    adf_attend as adf_adf_attend,
    adf_compose as adf_adf_compose,
    adf_extract as adf_adf_extract,
    adf_loop_plan as adf_adf_loop_plan,
    adf_nondestruct as adf_adf_nondestruct,
    adf_score as adf_adf_score,
)
from stele_core.compacter import (
    cmp_compact as cmp_cmp_compact,
    cmp_insert as cmp_cmp_insert,
    cmp_kronecker as cmp_cmp_kronecker,
    cmp_loop_plan as cmp_cmp_loop_plan,
    cmp_score as cmp_cmp_score,
    cmp_train as cmp_cmp_train,
)
from stele_core.ia3 import (
    ia3_loop_plan as ia3_ia3_loop_plan,
    ia3_mixed as ia3_ia3_mixed,
    ia3_scale as ia3_ia3_scale,
    ia3_score as ia3_ia3_score,
    ia3_train as ia3_ia3_train,
    ia3_vector as ia3_ia3_vector,
)
from stele_core.bitfit import (
    bft_bias as bft_bft_bias,
    bft_freeze as bft_bft_freeze,
    bft_loop_plan as bft_bft_loop_plan,
    bft_score as bft_bft_score,
    bft_tiny as bft_bft_tiny,
    bft_train as bft_bft_train,
)
from stele_core.dora import (
    dora_decompose as dora_dora_decompose,
    dora_direction as dora_dora_direction,
    dora_loop_plan as dora_dora_loop_plan,
    dora_magnitude as dora_dora_magnitude,
    dora_score as dora_dora_score,
    dora_vs_lora as dora_dora_vs_lora,
)
from stele_core.qlora import (
    qlo_adapter as qlo_qlo_adapter,
    qlo_loop_plan as qlo_qlo_loop_plan,
    qlo_memory as qlo_qlo_memory,
    qlo_nf4 as qlo_qlo_nf4,
    qlo_quantize as qlo_qlo_quantize,
    qlo_score as qlo_qlo_score,
)
from stele_core.adalora import (
    adl_adaptive as adl_adl_adaptive,
    adl_init as adl_adl_init,
    adl_loop_plan as adl_adl_loop_plan,
    adl_prune as adl_adl_prune,
    adl_score as adl_adl_score,
    adl_svd as adl_adl_svd,
)
from stele_core.vera import (
    vra_loop_plan as vra_vra_loop_plan,
    vra_scale as vra_vra_scale,
    vra_score as vra_vra_score,
    vra_share as vra_vra_share,
    vra_tiny as vra_vra_tiny,
    vra_train as vra_vra_train,
)
from stele_core.adapterdrop import (
    adp_drop as adp_adp_drop,
    adp_efficient as adp_adp_efficient,
    adp_infer as adp_adp_infer,
    adp_insert as adp_adp_insert,
    adp_loop_plan as adp_adp_loop_plan,
    adp_score as adp_adp_score,
)
from stele_core.pissa import (
    psa_fast as psa_psa_fast,
    psa_loop_plan as psa_psa_loop_plan,
    psa_principal as psa_psa_principal,
    psa_residual as psa_psa_residual,
    psa_score as psa_psa_score,
    psa_svd as psa_psa_svd,
)
from stele_core.diffpruning import (
    dpr_diff as dpr_dpr_diff,
    dpr_loop_plan as dpr_dpr_loop_plan,
    dpr_mask as dpr_dpr_mask,
    dpr_prune as dpr_dpr_prune,
    dpr_score as dpr_dpr_score,
    dpr_sparse as dpr_dpr_sparse,
)
from stele_core.tiedlora import (
    tlo_base as tlo_tlo_base,
    tlo_efficient as tlo_tlo_efficient,
    tlo_loop_plan as tlo_tlo_loop_plan,
    tlo_score as tlo_tlo_score,
    tlo_tie as tlo_tlo_tie,
    tlo_train as tlo_tlo_train,
)
from stele_core.loraplus import (
    lrp_loop_plan as lrp_lrp_loop_plan,
    lrp_ratio as lrp_lrp_ratio,
    lrp_score as lrp_lrp_score,
    lrp_speed as lrp_lrp_speed,
    lrp_split as lrp_lrp_split,
    lrp_train as lrp_lrp_train,
)
from stele_core.lorafa import (
    lfa_freeze_a as lfa_lfa_freeze_a,
    lfa_loop_plan as lfa_lfa_loop_plan,
    lfa_memory as lfa_lfa_memory,
    lfa_merge as lfa_lfa_merge,
    lfa_score as lfa_lfa_score,
    lfa_train_b as lfa_lfa_train_b,
)
from stele_core.dylora import (
    dyl_loop_plan as dyl_dyl_loop_plan,
    dyl_range as dyl_dyl_range,
    dyl_sample as dyl_dyl_sample,
    dyl_score as dyl_dyl_score,
    dyl_searchfree as dyl_dyl_searchfree,
    dyl_select as dyl_dyl_select,
)
from stele_core.loraxs import (
    lxs_loop_plan as lxs_lxs_loop_plan,
    lxs_r as lxs_lxs_r,
    lxs_score as lxs_lxs_score,
    lxs_svd as lxs_lxs_svd,
    lxs_tiny as lxs_lxs_tiny,
    lxs_train as lxs_lxs_train,
)
from stele_core.asymmetrylora import (
    asy_bound as asy_asy_bound,
    asy_freeze_a as asy_asy_freeze_a,
    asy_loop_plan as asy_asy_loop_plan,
    asy_role as asy_asy_role,
    asy_score as asy_asy_score,
    asy_train_b as asy_asy_train_b,
)
from stele_core.loraga import (
    lga_fast as lga_lga_fast,
    lga_grad as lga_lga_grad,
    lga_loop_plan as lga_lga_loop_plan,
    lga_scale as lga_lga_scale,
    lga_score as lga_lga_score,
    lga_svd as lga_lga_svd,
)
from stele_core.mora import (
    mor_compress as mor_mor_compress,
    mor_expand as mor_mor_expand,
    mor_loop_plan as mor_mor_loop_plan,
    mor_merge as mor_mor_merge,
    mor_score as mor_mor_score,
    mor_square as mor_mor_square,
)
from stele_core.rslora import (
    rsl_loop_plan as rsl_rsl_loop_plan,
    rsl_rank as rsl_rsl_rank,
    rsl_scale as rsl_rsl_scale,
    rsl_score as rsl_rsl_score,
    rsl_stable as rsl_rsl_stable,
    rsl_train as rsl_rsl_train,
)
from stele_core.lokr import (
    lkr_factors as lkr_lkr_factors,
    lkr_kron as lkr_lkr_kron,
    lkr_loop_plan as lkr_lkr_loop_plan,
    lkr_preserve as lkr_lkr_preserve,
    lkr_score as lkr_lkr_score,
    lkr_vectorize as lkr_lkr_vectorize,
)
from stele_core.loha import (
    lha_express as lha_lha_express,
    lha_hadamard as lha_lha_hadamard,
    lha_loop_plan as lha_lha_loop_plan,
    lha_pair as lha_lha_pair,
    lha_score as lha_lha_score,
    lha_train as lha_lha_train,
)
from stele_core.fourierft import (
    fft_basis as fft_fft_basis,
    fft_coeff as fft_fft_coeff,
    fft_idft as fft_fft_idft,
    fft_loop_plan as fft_fft_loop_plan,
    fft_score as fft_fft_score,
    fft_sparse as fft_fft_sparse,
)
from stele_core.houlsby import (
    had_freeze as had_had_freeze,
    had_insert as had_had_insert,
    had_latency as had_had_latency,
    had_loop_plan as had_had_loop_plan,
    had_score as had_had_score,
    had_train as had_had_train,
)
from stele_core.reft import (
    rft_edit as rft_rft_edit,
    rft_loop_plan as rft_rft_loop_plan,
    rft_repr as rft_rft_repr,
    rft_score as rft_rft_score,
    rft_train as rft_rft_train,
    rft_weightless as rft_rft_weightless,
)
from stele_core.oft import (
    oft_butterfly as oft_oft_butterfly,
    oft_energy as oft_oft_energy,
    oft_loop_plan as oft_oft_loop_plan,
    oft_ortho as oft_oft_ortho,
    oft_score as oft_oft_score,
    oft_train as oft_oft_train,
)
from stele_core.miss import (
    mss_loop_plan as mss_mss_loop_plan,
    mss_pareto as mss_mss_pareto,
    mss_score as mss_mss_score,
    mss_share as mss_mss_share,
    mss_shard as mss_mss_shard,
    mss_train as mss_mss_train,
)
from stele_core.droplora import (
    drl_infer as drl_drl_infer,
    drl_loop_plan as drl_drl_loop_plan,
    drl_mask as drl_drl_mask,
    drl_rank as drl_drl_rank,
    drl_score as drl_drl_score,
    drl_train as drl_drl_train,
)
from stele_core.galore import (
    gal_full as gal_gal_full,
    gal_grad as gal_gal_grad,
    gal_loop_plan as gal_gal_loop_plan,
    gal_project as gal_gal_project,
    gal_score as gal_gal_score,
    gal_step as gal_gal_step,
)
from stele_core.shira import (
    shr_fusion as shr_shr_fusion,
    shr_loop_plan as shr_shr_loop_plan,
    shr_mask as shr_shr_mask,
    shr_score as shr_shr_score,
    shr_switch as shr_shr_switch,
    shr_tune as shr_shr_tune,
)
from stele_core.waveft import (
    wft_granular as wft_wft_granular,
    wft_idwt as wft_wft_idwt,
    wft_loop_plan as wft_wft_loop_plan,
    wft_score as wft_wft_score,
    wft_sparse as wft_wft_sparse,
    wft_wave as wft_wft_wave,
)
from stele_core.lorapro import (
    lpr_adjust as lpr_lpr_adjust,
    lpr_bridge as lpr_lpr_bridge,
    lpr_equiv as lpr_lpr_equiv,
    lpr_loop_plan as lpr_lpr_loop_plan,
    lpr_score as lpr_lpr_score,
    lpr_train as lpr_lpr_train,
)
from stele_core.kronlora import (
    krl_compress as krl_krl_compress,
    krl_kron as krl_krl_kron,
    krl_loop_plan as krl_krl_loop_plan,
    krl_lora as krl_krl_lora,
    krl_score as krl_krl_score,
    krl_train as krl_krl_train,
)
from stele_core.milora import (
    mil_freeze as mil_mil_freeze,
    mil_loop_plan as mil_mil_loop_plan,
    mil_minor as mil_mil_minor,
    mil_preserve as mil_mil_preserve,
    mil_score as mil_mil_score,
    mil_svd as mil_mil_svd,
)
from stele_core.corda import (
    cda_adapt as cda_cda_adapt,
    cda_cov as cda_cda_cov,
    cda_forget as cda_cda_forget,
    cda_loop_plan as cda_cda_loop_plan,
    cda_mode as cda_cda_mode,
    cda_score as cda_cda_score,
)
from stele_core.loftq import (
    lfq_gap as lfq_lfq_gap,
    lfq_init as lfq_lfq_init,
    lfq_loop_plan as lfq_lfq_loop_plan,
    lfq_quant as lfq_lfq_quant,
    lfq_score as lfq_lfq_score,
    lfq_train as lfq_lfq_train,
)
from stele_core.loradash import (
    lds_dash as lds_lds_dash,
    lds_impact as lds_lds_impact,
    lds_loop_plan as lds_lds_loop_plan,
    lds_prelaunch as lds_lds_prelaunch,
    lds_score as lds_lds_score,
    lds_tsd as lds_lds_tsd,
)
from stele_core.deltalora import (
    dlo_adapters as dlo_dlo_adapters,
    dlo_delta as dlo_dlo_delta,
    dlo_highrank as dlo_dlo_highrank,
    dlo_loop_plan as dlo_dlo_loop_plan,
    dlo_propagate as dlo_dlo_propagate,
    dlo_score as dlo_dlo_score,
)
from stele_core.loraone import (
    lon_align as lon_lon_align,
    lon_grad as lon_lon_grad,
    lon_immediate as lon_lon_immediate,
    lon_loop_plan as lon_lon_loop_plan,
    lon_score as lon_lon_score,
    lon_train as lon_lon_train,
)
from stele_core.olora import (
    olr_loop_plan as olr_olr_loop_plan,
    olr_ortho as olr_olr_ortho,
    olr_qr as olr_olr_qr,
    olr_score as olr_olr_score,
    olr_stable as olr_olr_stable,
    olr_train as olr_olr_train,
)
from stele_core.lorasp import (
    lsp_freeze as lsp_lsp_freeze,
    lsp_loop_plan as lsp_lsp_loop_plan,
    lsp_memory as lsp_lsp_memory,
    lsp_score as lsp_lsp_score,
    lsp_select as lsp_lsp_select,
    lsp_train as lsp_lsp_train,
)
from stele_core.qpissa import (
    qps_error as qps_qps_error,
    qps_loop_plan as qps_qps_loop_plan,
    qps_principal as qps_qps_principal,
    qps_quant as qps_qps_quant,
    qps_score as qps_qps_score,
    qps_train as qps_qps_train,
)
from stele_core.moslora import (
    msl_fuse as msl_msl_fuse,
    msl_loop_plan as msl_msl_loop_plan,
    msl_mixer as msl_msl_mixer,
    msl_score as msl_msl_score,
    msl_split as msl_msl_split,
    msl_train as msl_msl_train,
)
from stele_core.loradrop import (
    ldr_eval as ldr_ldr_eval,
    ldr_keep as ldr_ldr_keep,
    ldr_loop_plan as ldr_ldr_loop_plan,
    ldr_prune as ldr_ldr_prune,
    ldr_score as ldr_ldr_score,
    ldr_share as ldr_ldr_share,
)
from stele_core.vblora import (
    vbl_bank as vbl_vbl_bank,
    vbl_compose as vbl_vbl_compose,
    vbl_extreme as vbl_vbl_extreme,
    vbl_loop_plan as vbl_vbl_loop_plan,
    vbl_score as vbl_vbl_score,
    vbl_topk as vbl_vbl_topk,
)
from stele_core.oplora import (
    opl_constrain as opl_opl_constrain,
    opl_forget as opl_opl_forget,
    opl_loop_plan as opl_opl_loop_plan,
    opl_proj as opl_opl_proj,
    opl_score as opl_opl_score,
    opl_train as opl_opl_train,
)
from stele_core.gelora import (
    gel_budget as gel_gel_budget,
    gel_idim as gel_gel_idim,
    gel_loop_plan as gel_gel_loop_plan,
    gel_rank as gel_gel_rank,
    gel_score as gel_gel_score,
    gel_train as gel_gel_train,
)
from stele_core.geolora import (
    geo_budget as geo_geo_budget,
    geo_dyn as geo_geo_dyn,
    geo_loop_plan as geo_geo_loop_plan,
    geo_ortho as geo_geo_ortho,
    geo_score as geo_geo_score,
    geo_train as geo_geo_train,
)
from stele_core.randlora import (
    rlo_bases as rlo_rlo_bases,
    rlo_fullrank as rlo_rlo_fullrank,
    rlo_loop_plan as rlo_rlo_loop_plan,
    rlo_scale as rlo_rlo_scale,
    rlo_score as rlo_rlo_score,
    rlo_train as rlo_rlo_train,
)
from stele_core.lorashear import (
    lsh_footprint as lsh_lsh_footprint,
    lsh_graph as lsh_lsh_graph,
    lsh_loop_plan as lsh_lsh_loop_plan,
    lsh_prune as lsh_lsh_prune,
    lsh_recover as lsh_lsh_recover,
    lsh_score as lsh_lsh_score,
)
from stele_core.oplora_alt import (
    aop_alt as aop_aop_alt,
    aop_loop_plan as aop_aop_loop_plan,
    aop_score as aop_aop_score,
    aop_sub as aop_aop_sub,
    aop_svd as aop_aop_svd,
    aop_train as aop_aop_train,
)
from stele_core.lorainit import (
    lin_fast as lin_lin_fast,
    lin_init as lin_lin_init,
    lin_loop_plan as lin_lin_loop_plan,
    lin_score as lin_lin_score,
    lin_train as lin_lin_train,
    lin_tsd as lin_lin_tsd,
)
from stele_core.loranull import (
    lnu_act as lnu_lnu_act,
    lnu_forget as lnu_lnu_forget,
    lnu_loop_plan as lnu_lnu_loop_plan,
    lnu_null as lnu_lnu_null,
    lnu_score as lnu_lnu_score,
    lnu_train as lnu_lnu_train,
)
from stele_core.hydralora import (
    hyd_heads as hyd_hyd_heads,
    hyd_loop_plan as hyd_hyd_loop_plan,
    hyd_nodomain as hyd_hyd_nodomain,
    hyd_route as hyd_hyd_route,
    hyd_score as hyd_hyd_score,
    hyd_share as hyd_hyd_share,
)
from stele_core.loralego import (
    llg_cluster as llg_llg_cluster,
    llg_loop_plan as llg_llg_loop_plan,
    llg_merge as llg_llg_merge,
    llg_modular as llg_llg_modular,
    llg_msu as llg_llg_msu,
    llg_score as llg_llg_score,
)
from stele_core.loramoe import (
    lme_balance as lme_lme_balance,
    lme_forget as lme_lme_forget,
    lme_loop_plan as lme_lme_loop_plan,
    lme_plugin as lme_lme_plugin,
    lme_route as lme_lme_route,
    lme_score as lme_lme_score,
)
from stele_core.moelora import (
    mel_contrast as mel_mel_contrast,
    mel_experts as mel_mel_experts,
    mel_gate as mel_mel_gate,
    mel_loop_plan as mel_mel_loop_plan,
    mel_score as mel_mel_score,
    mel_sparse as mel_mel_sparse,
)
from stele_core.lorahub import (
    lhb_adapt as lhb_lhb_adapt,
    lhb_compose as lhb_lhb_compose,
    lhb_loop_plan as lhb_lhb_loop_plan,
    lhb_nograd as lhb_lhb_nograd,
    lhb_pool as lhb_lhb_pool,
    lhb_score as lhb_lhb_score,
)
from stele_core.multilora import (
    mlr_demo as mlr_mlr_demo,
    mlr_init as mlr_mlr_init,
    mlr_loop_plan as mlr_mlr_loop_plan,
    mlr_scale as mlr_mlr_scale,
    mlr_score as mlr_mlr_score,
    mlr_train as mlr_mlr_train,
)
from stele_core.mtllora import (
    mtl_interfere as mtl_mtl_interfere,
    mtl_loop_plan as mtl_mtl_loop_plan,
    mtl_score as mtl_mtl_score,
    mtl_share as mtl_mtl_share,
    mtl_spec as mtl_mtl_spec,
    mtl_task as mtl_mtl_task,
)
from stele_core.malora import (
    mal_down as mal_mal_down,
    mal_eff as mal_mal_eff,
    mal_loop_plan as mal_mal_loop_plan,
    mal_mix as mal_mal_mix,
    mal_score as mal_mal_score,
    mal_up as mal_mal_up,
)
from stele_core.loramini import (
    lmi_inner as lmi_lmi_inner,
    lmi_loop_plan as lmi_lmi_loop_plan,
    lmi_score as lmi_lmi_score,
    lmi_split as lmi_lmi_split,
    lmi_tiny as lmi_lmi_tiny,
    lmi_train as lmi_lmi_train,
)
from stele_core.qdylora import (
    qdy_loop_plan as qdy_qdy_loop_plan,
    qdy_pick as qdy_qdy_pick,
    qdy_quant as qdy_qdy_quant,
    qdy_range as qdy_qdy_range,
    qdy_score as qdy_qdy_score,
    qdy_train as qdy_qdy_train,
)
from stele_core.loratsd import (
    lts_combo as lts_lts_combo,
    lts_dash as lts_lts_dash,
    lts_init as lts_lts_init,
    lts_loop_plan as lts_lts_loop_plan,
    lts_score as lts_lts_score,
    lts_tsd as lts_lts_tsd,
)
from stele_core.slora import (
    slr_batch as slr_slr_batch,
    slr_loop_plan as slr_slr_loop_plan,
    slr_page as slr_slr_page,
    slr_pool as slr_slr_pool,
    slr_scale as slr_slr_scale,
    slr_score as slr_slr_score,
)
from stele_core.compressthenserve import (
    cts_basis as cts_cts_basis,
    cts_cluster as cts_cts_cluster,
    cts_collect as cts_cts_collect,
    cts_loop_plan as cts_cts_loop_plan,
    cts_scale as cts_cts_scale,
    cts_score as cts_cts_score,
)
from stele_core.flora import (
    flo_agg as flo_flo_agg,
    flo_clients as flo_flo_clients,
    flo_hetero as flo_flo_hetero,
    flo_loop_plan as flo_flo_loop_plan,
    flo_score as flo_flo_score,
    flo_stack as flo_flo_stack,
)
from stele_core.punica import (
    pun_backbone as pun_pun_backbone,
    pun_loop_plan as pun_pun_loop_plan,
    pun_multi as pun_pun_multi,
    pun_sched as pun_pun_sched,
    pun_score as pun_pun_score,
    pun_sgmv as pun_pun_sgmv,
)
from stele_core.mlora import (
    mla_batch as mla_mla_batch,
    mla_eff as mla_mla_eff,
    mla_loop_plan as mla_mla_loop_plan,
    mla_pipe as mla_mla_pipe,
    mla_score as mla_mla_score,
    mla_train as mla_mla_train,
)
from stele_core.switchlora import (
    swl_alloc as swl_swl_alloc,
    swl_full as swl_swl_full,
    swl_loop_plan as swl_swl_loop_plan,
    swl_score as swl_swl_score,
    swl_switch as swl_swl_switch,
    swl_train as swl_swl_train,
)
from stele_core.chainoflora import (
    col_extend as col_col_extend,
    col_gap as col_col_gap,
    col_knot as col_col_knot,
    col_loop_plan as col_col_loop_plan,
    col_score as col_col_score,
    col_tune as col_col_tune,
)
from stele_core.delora import (
    dlr_bound as dlr_dlr_bound,
    dlr_loop_plan as dlr_dlr_loop_plan,
    dlr_norm as dlr_dlr_norm,
    dlr_robust as dlr_dlr_robust,
    dlr_score as dlr_dlr_score,
    dlr_train as dlr_dlr_train,
)
from stele_core.melora_ensemble import (
    meo_diag as meo_meo_diag,
    meo_loop_plan as meo_meo_loop_plan,
    meo_mini as meo_meo_mini,
    meo_rank as meo_meo_rank,
    meo_score as meo_meo_score,
    meo_train as meo_meo_train,
)
from stele_core.relora import (
    rlr_high as rlr_rlr_high,
    rlr_jagged as rlr_rlr_jagged,
    rlr_loop_plan as rlr_rlr_loop_plan,
    rlr_merge as rlr_rlr_merge,
    rlr_score as rlr_rlr_score,
    rlr_warm as rlr_rlr_warm,
)
from stele_core.ether import (
    eth_loop_plan as eth_eth_loop_plan,
    eth_plane as eth_eth_plane,
    eth_plus as eth_eth_plus,
    eth_reflect as eth_eth_reflect,
    eth_score as eth_eth_score,
    eth_train as eth_eth_train,
)
from stele_core.loracomposer import (
    lco_concepts as lco_lco_concepts,
    lco_free as lco_lco_free,
    lco_inject as lco_lco_inject,
    lco_isolate as lco_lco_isolate,
    lco_loop_plan as lco_lco_loop_plan,
    lco_score as lco_lco_score,
)
from stele_core.carelora import (
    car_compress as car_car_compress,
    car_loop_plan as car_car_loop_plan,
    car_mem as car_car_mem,
    car_recon as car_car_recon,
    car_score as car_car_score,
    car_train as car_car_train,
)
from stele_core.lorarar import (
    lrr_fast as lrr_lrr_fast,
    lrr_hyper as lrr_lrr_hyper,
    lrr_loop_plan as lrr_lrr_loop_plan,
    lrr_merge as lrr_lrr_merge,
    lrr_pair as lrr_lrr_pair,
    lrr_score as lrr_lrr_score,
)
from stele_core.svft import (
    svf_geom as svf_svf_geom,
    svf_loop_plan as svf_svf_loop_plan,
    svf_score as svf_svf_score,
    svf_sparse as svf_svf_sparse,
    svf_svd as svf_svf_svd,
    svf_train as svf_svf_train,
)
from stele_core.flylora import (
    fly_implicit as fly_fly_implicit,
    fly_loop_plan as fly_fly_loop_plan,
    fly_proj as fly_fly_proj,
    fly_score as fly_fly_score,
    fly_topk as fly_fly_topk,
    fly_train as fly_fly_train,
)
from stele_core.nola import (
    nla_basis as nla_nla_basis,
    nla_coeff as nla_nla_coeff,
    nla_compact as nla_nla_compact,
    nla_loop_plan as nla_nla_loop_plan,
    nla_score as nla_nla_score,
    nla_train as nla_nla_train,
)
from stele_core.mixlora import (
    mxl_attn as mxl_mxl_attn,
    mxl_balance as mxl_mxl_balance,
    mxl_experts as mxl_mxl_experts,
    mxl_loop_plan as mxl_mxl_loop_plan,
    mxl_route as mxl_mxl_route,
    mxl_score as mxl_mxl_score,
)
from stele_core.superlora import (
    spr_factor as spr_spr_factor,
    spr_fold as spr_spr_fold,
    spr_group as spr_spr_group,
    spr_loop_plan as spr_spr_loop_plan,
    spr_score as spr_spr_score,
    spr_unify as spr_spr_unify,
)
from stele_core.tiedlora import (
    tld_frac as tld_tld_frac,
    tld_loop_plan as tld_tld_loop_plan,
    tld_scale as tld_tld_scale,
    tld_score as tld_tld_score,
    tld_select as tld_tld_select,
    tld_tie as tld_tld_tie,
)
from stele_core.qalora import (
    qal_adapt as qal_qal_adapt,
    qal_group as qal_qal_group,
    qal_loop_plan as qal_qal_loop_plan,
    qal_merge as qal_qal_merge,
    qal_quant as qal_qal_quant,
    qal_score as qal_qal_score,
)
from stele_core.unilora import (
    ulo_iso as ulo_ulo_iso,
    ulo_loop_plan as ulo_ulo_loop_plan,
    ulo_one as ulo_ulo_one,
    ulo_score as ulo_ulo_score,
    ulo_space as ulo_ulo_space,
    ulo_vec as ulo_ulo_vec,
)
from stele_core.bora import (
    bor_col as bor_bor_col,
    bor_loop_plan as bor_bor_loop_plan,
    bor_row as bor_bor_row,
    bor_score as bor_bor_score,
    bor_sym as bor_bor_sym,
    bor_train as bor_bor_train,
)
from stele_core.qgalore import (
    qga_lazy as qga_qga_lazy,
    qga_loop_plan as qga_qga_loop_plan,
    qga_mem as qga_qga_mem,
    qga_proj as qga_qga_proj,
    qga_score as qga_qga_score,
    qga_weight as qga_qga_weight,
)
from stele_core.loraflow import (
    lfw_few as lfw_lfw_few,
    lfw_gate as lfw_lfw_gate,
    lfw_loop_plan as lfw_lfw_loop_plan,
    lfw_pool as lfw_lfw_pool,
    lfw_score as lfw_lfw_score,
    lfw_token as lfw_lfw_token,
)
from stele_core.rosa import (
    ros_fft as ros_ros_fft,
    ros_loop_plan as ros_ros_loop_plan,
    ros_rank as ros_ros_rank,
    ros_score as ros_ros_score,
    ros_sparse as ros_ros_sparse,
    ros_train as ros_ros_train,
)
from stele_core.abba import (
    abb_expr as abb_abb_expr,
    abb_hadamard as abb_abb_hadamard,
    abb_left as abb_abb_left,
    abb_loop_plan as abb_abb_loop_plan,
    abb_right as abb_abb_right,
    abb_score as abb_abb_score,
)
from stele_core.boha import (
    bha_hadamard as bha_bha_hadamard,
    bha_local as bha_bha_local,
    bha_loop_plan as bha_bha_loop_plan,
    bha_score as bha_bha_score,
    bha_split as bha_bha_split,
    bha_train as bha_bha_train,
)
from stele_core.smoa import (
    smo_loop_plan as smo_smo_loop_plan,
    smo_mod as smo_smo_mod,
    smo_rank as smo_smo_rank,
    smo_score as smo_smo_score,
    smo_struct as smo_smo_struct,
    smo_train as smo_smo_train,
)
from stele_core.glora import (
    glo_loop_plan as glo_glo_loop_plan,
    glo_prompt as glo_glo_prompt,
    glo_scale as glo_glo_scale,
    glo_score as glo_glo_score,
    glo_search as glo_glo_search,
    glo_zero as glo_glo_zero,
)
from stele_core.periodiclora import (
    plr_loop_plan as plr_plr_loop_plan,
    plr_merge as plr_plr_merge,
    plr_rank as plr_plr_rank,
    plr_reset as plr_plr_reset,
    plr_score as plr_plr_score,
    plr_stage as plr_plr_stage,
)
from stele_core.hira import (
    hir_base as hir_hir_base,
    hir_factors as hir_hir_factors,
    hir_hadamard as hir_hir_hadamard,
    hir_loop_plan as hir_hir_loop_plan,
    hir_merge as hir_hir_merge,
    hir_score as hir_hir_score,
)
from stele_core.concurrentlora import (
    cnl_fuse as cnl_cnl_fuse,
    cnl_hw as cnl_cnl_hw,
    cnl_loop_plan as cnl_cnl_loop_plan,
    cnl_pack as cnl_cnl_pack,
    cnl_score as cnl_cnl_score,
    cnl_train as cnl_cnl_train,
)
from stele_core.longlora import (
    llr_loop_plan as llr_llr_loop_plan,
    llr_lora as llr_llr_lora,
    llr_score as llr_llr_score,
    llr_shift as llr_llr_shift,
    llr_sparse as llr_llr_sparse,
    llr_window as llr_llr_window,
)
from stele_core.lisa import (
    lis_layers as lis_lis_layers,
    lis_loop_plan as lis_lis_loop_plan,
    lis_memory as lis_lis_memory,
    lis_sample as lis_lis_sample,
    lis_score as lis_lis_score,
    lis_unfreeze as lis_lis_unfreeze,
)
from stele_core.nlora import (
    nlr_cheap as nlr_nlr_cheap,
    nlr_init as nlr_nlr_init,
    nlr_landmark as nlr_nlr_landmark,
    nlr_loop_plan as nlr_nlr_loop_plan,
    nlr_nystrom as nlr_nlr_nystrom,
    nlr_score as nlr_nlr_score,
)
from stele_core.randsub import (
    rsa_express as rsa_rsa_express,
    rsa_loop_plan as rsa_rsa_loop_plan,
    rsa_project as rsa_rsa_project,
    rsa_score as rsa_rsa_score,
    rsa_subspace as rsa_rsa_subspace,
    rsa_train as rsa_rsa_train,
)
from stele_core.hra import (
    hra_house as hra_hra_house,
    hra_loop_plan as hra_hra_loop_plan,
    hra_ortho as hra_hra_ortho,
    hra_reflect as hra_hra_reflect,
    hra_score as hra_hra_score,
    hra_train as hra_hra_train,
)
from stele_core.hybridpeft import (
    hyb_boft as hyb_hyb_boft,
    hyb_fuse as hyb_hyb_fuse,
    hyb_loop_plan as hyb_hyb_loop_plan,
    hyb_lora as hyb_hyb_lora,
    hyb_score as hyb_hyb_score,
    hyb_stable as hyb_hyb_stable,
)
from stele_core.lorta import (
    lrt_compact as lrt_lrt_compact,
    lrt_cp as lrt_lrt_cp,
    lrt_loop_plan as lrt_lrt_loop_plan,
    lrt_score as lrt_lrt_score,
    lrt_share as lrt_lrt_share,
    lrt_tensor as lrt_lrt_tensor,
)
from stele_core.clora import (
    clo_forget as clo_clo_forget,
    clo_loop_plan as clo_clo_loop_plan,
    clo_ortho as clo_clo_ortho,
    clo_route as clo_clo_route,
    clo_score as clo_clo_score,
    clo_task as clo_clo_task,
)
from stele_core.alora import (
    alo_ablate as alo_alo_ablate,
    alo_init as alo_alo_init,
    alo_loop_plan as alo_alo_loop_plan,
    alo_prune as alo_alo_prune,
    alo_realloc as alo_alo_realloc,
    alo_score as alo_alo_score,
)
from stele_core.lntuning import (
    lnt_attn as lnt_lnt_attn,
    lnt_cheap as lnt_lnt_cheap,
    lnt_loop_plan as lnt_lnt_loop_plan,
    lnt_scale as lnt_lnt_scale,
    lnt_score as lnt_lnt_score,
    lnt_train as lnt_lnt_train,
)
from stele_core.lorafusion import (
    lfu_batch as lfu_lfu_batch,
    lfu_fuse as lfu_lfu_fuse,
    lfu_loop_plan as lfu_lfu_loop_plan,
    lfu_score as lfu_lfu_score,
    lfu_speed as lfu_lfu_speed,
    lfu_split as lfu_lfu_split,
)
from stele_core.tera import (
    ter_freeze as ter_ter_freeze,
    ter_highrank as ter_ter_highrank,
    ter_loop_plan as ter_ter_loop_plan,
    ter_scale as ter_ter_scale,
    ter_score as ter_ter_score,
    ter_tucker as ter_ter_tucker,
)
from stele_core.tenslora import (
    tnl_budget as tnl_tnl_budget,
    tnl_loop_plan as tnl_tnl_loop_plan,
    tnl_mode as tnl_tnl_mode,
    tnl_score as tnl_tnl_score,
    tnl_stack as tnl_tnl_stack,
    tnl_tucker as tnl_tnl_tucker,
)
from stele_core.adazeta import (
    azt_ff as azt_azt_ff,
    azt_loop_plan as azt_azt_loop_plan,
    azt_mem as azt_azt_mem,
    azt_query as azt_azt_query,
    azt_score as azt_azt_score,
    azt_tt as azt_azt_tt,
)
from stele_core.fact import (
    fct_loop_plan as fct_fct_loop_plan,
    fct_score as fct_fct_score,
    fct_tensor as fct_fct_tensor,
    fct_tiny as fct_fct_tiny,
    fct_tt as fct_fct_tt,
    fct_tucker as fct_fct_tucker,
)
from stele_core.lotr import (
    ltr_core as ltr_ltr_core,
    ltr_deep as ltr_ltr_deep,
    ltr_loop_plan as ltr_ltr_loop_plan,
    ltr_score as ltr_ltr_score,
    ltr_share as ltr_ltr_share,
    ltr_stack as ltr_ltr_stack,
)
from stele_core.cara import (
    cra_cpd as cra_cra_cpd,
    cra_ffn as cra_cra_ffn,
    cra_heads as cra_cra_heads,
    cra_loop_plan as cra_cra_loop_plan,
    cra_mha as cra_cra_mha,
    cra_score as cra_cra_score,
)
from stele_core.loretta import (
    ltt_adp as ltt_ltt_adp,
    ltt_loop_plan as ltt_ltt_loop_plan,
    ltt_rep as ltt_ltt_rep,
    ltt_score as ltt_ltt_score,
    ltt_tiny as ltt_ltt_tiny,
    ltt_tt as ltt_ltt_tt,
)
from stele_core.c3a import (
    c3a_circ as c3a_c3a_circ,
    c3a_fft as c3a_c3a_fft,
    c3a_kernel as c3a_c3a_kernel,
    c3a_loop_plan as c3a_c3a_loop_plan,
    c3a_rank as c3a_c3a_rank,
    c3a_score as c3a_c3a_score,
)
from stele_core.boft import (
    bof_block as bof_bof_block,
    bof_butter as bof_bof_butter,
    bof_full as bof_bof_full,
    bof_loop_plan as bof_bof_loop_plan,
    bof_orth as bof_bof_orth,
    bof_score as bof_bof_score,
)
from stele_core.sdt import (
    sdt_dim as sdt_sdt_dim,
    sdt_loop_plan as sdt_sdt_loop_plan,
    sdt_mask as sdt_sdt_mask,
    sdt_score as sdt_sdt_score,
    sdt_ssm as sdt_sdt_ssm,
    sdt_tune as sdt_sdt_tune,
)
from stele_core.meft import (
    mef_adapt as mef_mef_adapt,
    mef_cpu as mef_mef_cpu,
    mef_fetch as mef_mef_fetch,
    mef_loop_plan as mef_mef_loop_plan,
    mef_route as mef_mef_route,
    mef_score as mef_mef_score,
)
from stele_core.roles import (
    infer_memory_role,
    project_fact_interface,
    quality_gate as roles_quality_gate,
    role_collapse_scan,
)
from stele_core.versioning import (
    checkout_view as ver_checkout_view,
    commit_view as ver_commit_view,
    copyability_gate as ver_copyability_gate,
    diff_commits as ver_diff_commits,
    get_read_head as ver_get_read_head,
    list_commits as ver_list_commits,
    merge_refs as ver_merge_refs,
    set_read_head as ver_set_read_head,
    tag_commit as ver_tag_commit,
    verify_commit_chain as ver_verify_commit_chain,
)
from stele_core.strata import (
    is_current_fact,
    stale_fact_scan as strata_stale_fact_scan,
    supersession_winners,
)
from stele_core.tarl import (
    TARL_ACTIONS,
    classify_update as tarl_classify_update,
    ledger_view as tarl_ledger_view,
)
from stele_core.worth import (
    low_worth_scan as worth_low_worth_scan,
    memory_worth as worth_memory_worth,
    passes_min_worth,
)
from stele_core.memtx import (
    action_safe_gate as memtx_action_safe_gate,
    aoep_checklist as memtx_aoep_checklist,
    begin_transaction as memtx_begin_transaction,
    get_transaction as memtx_get_transaction,
    list_transactions as memtx_list_transactions,
    mark_aborted as memtx_mark_aborted,
    mark_committed as memtx_mark_committed,
    maturity_of as memtx_maturity_of,
    stage_entry as memtx_stage_entry,
    validate_transaction as memtx_validate_transaction,
)
from stele_core.lattice import (
    classify_conflict as lattice_classify_conflict,
    compact_render as lattice_compact_render,
    symbolic_conflict_scan as lattice_symbolic_conflict_scan,
)
from stele_core.cordon import (
    cancel_effect as cordon_cancel_effect,
    compensate_effect as cordon_compensate_effect,
    list_effects as cordon_list_effects,
    mark_dispatched as cordon_mark_dispatched,
    release_effects as cordon_release_effects,
    stage_effect as cordon_stage_effect,
)
from stele_core.stale import (
    ipa_gap_scan as stale_ipa_gap_scan,
    premise_resistance as stale_premise_resistance,
    related_slot_scan as stale_related_slot_scan,
    state_resolution as stale_state_resolution,
    verify_transition as stale_verify_transition,
)
from stele_core.gem import gem_correctness_report
from stele_core.fuse import (
    clear_projection_pin as fuse_clear_projection_pin,
    correction_handle as fuse_correction_handle,
    get_projection_pin as fuse_get_projection_pin,
    list_projection_pins as fuse_list_projection_pins,
    pin_projection as fuse_pin_projection,
    project_resolve as fuse_project_resolve,
)
from stele_core.toki_ops import (
    anomaly_scan as toki_anomaly_scan,
    classify_write_operator as toki_classify_write_operator,
    tip_for_conflict_key as toki_tip_for_conflict_key,
)
from stele_core.architect import context_bid as architect_context_bid
from stele_core.decision import (
    issue_decision_receipt,
    list_decision_receipts,
    verify_decision_receipt,
)
from stele_core.export import (
    export_pack,
    hydrate_pack,
    pack_seal,
    verify_import,
    verify_pack,
    verify_pack_seal,
)
from stele_core.governance import (
    apply_promote,
    apply_resolve_contested,
    validate_promotion_evidence,
)
from stele_core.graph import blast_radius as graph_blast_radius
from stele_core.graph import lineage_trust as graph_lineage_trust
from stele_core.graph import merge_classify as graph_merge_classify
from stele_core.graph import path_trust as graph_path_trust
from stele_core.index.lexical import tokenize
from stele_core.index.temporal import is_stale
from stele_core.integrity import (
    attribution_receipt,
    journal_chain_head,
    replay_consistency,
    store_seal,
    verify_journal_chain,
    verify_seal,
    verify_store,
)
from stele_core.lifecycle import LIFECYCLE_TIERS, lifecycle_inventory, lifecycle_tier, parse_conflict_key
from stele_core.retrieval import Retriever, _scope_allows, _valid_at_point
from stele_core.risk import INJECTION_MARKERS, scan_entry, scan_text
from stele_core.schema import (
    OUTCOME_KINDS,
    SchemaError,
    derive_entry_id,
    normalize_usage,
    private_source_fields_present,
    validate_entry,
    validate_evidence,
    validate_scope,
)
from stele_core.store import SteleStore, require_ts


def _title_sim(a: str, b: str) -> float:
    ta, tb = set(tokenize(a)), set(tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


class Stele:
    """Facade: ADD · UPDATE · PROMOTE · SUPERSEDE · DELETE · SEARCH · REFLECT · LINK · EXPORT."""

    def __init__(
        self,
        store: SteleStore,
        *,
        embedder: Any | None = None,
        now: str | None = None,
        staleness_horizon: str | None = None,
    ):
        self.store = store
        self.embedder = embedder
        self._now = now
        self.retriever = Retriever(
            store, embedder=embedder, staleness_horizon=staleness_horizon
        )

    @classmethod
    def open(
        cls,
        root: str | Path,
        *,
        store_id: str | None = None,
        embedder: Any | None = None,
        now: str | None = None,
        staleness_horizon: str | None = None,
        create: bool = True,
        dsn: str | None = None,
    ) -> Stele:
        import os

        resolved_dsn = dsn if dsn is not None else os.environ.get("STELE_STORE_DSN")
        if resolved_dsn:
            from stele_core.mysql_store import MySQLSteleStore

            store: Any = MySQLSteleStore(
                resolved_dsn,
                scratch_root=Path(root),
                store_id=store_id,
                create=create,
            )
        else:
            store = SteleStore(Path(root), store_id=store_id, create=create)
        return cls(
            store,
            embedder=embedder,
            now=now,
            staleness_horizon=staleness_horizon,
        )

    def rebuild_indexes(self) -> None:
        self.retriever.rebuild(lexical_only=False)

    # ----- writers ---------------------------------------------------------

    def add(self, entry: Mapping[str, Any], *, actor: str | None = None, ts: str | None = None) -> dict[str, Any]:
        hits = private_source_fields_present(entry)
        if hits:
            raise SchemaError(f"private-source fields forbidden: {hits}")
        assert_distilled_entry(entry)
        ts = require_ts(ts or self._now)
        data = dict(entry)
        data["state"] = "quarantined"
        validated = validate_entry(data, allow_state="quarantined")
        # Re-derive id from content after normalization
        validated["id"] = derive_entry_id({k: v for k, v in validated.items() if k != "id"})
        actor = actor or validated["provenance"]["agent"]
        with self.store:
            written = self.store.write_entry(validated, actor=actor, ts=ts, op="ADD")
        return {"id": written["id"], "state": "quarantined"}

    def add_batch(
        self,
        entries: Sequence[Mapping[str, Any]],
        *,
        actor: str | None = None,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """
        Atomic multi-ADD under one lock (MemBench write-efficiency).

        All-or-nothing: if any entry fails schema/distill/private checks, nothing is written.
        """
        ts = require_ts(ts or self._now)
        prepared: list[dict[str, Any]] = []
        for entry in entries:
            hits = private_source_fields_present(entry)
            if hits:
                raise SchemaError(f"private-source fields forbidden: {hits}")
            assert_distilled_entry(entry)
            data = dict(entry)
            data["state"] = "quarantined"
            validated = validate_entry(data, allow_state="quarantined")
            validated["id"] = derive_entry_id({k: v for k, v in validated.items() if k != "id"})
            prepared.append(validated)
        ids: list[str] = []
        with self.store:
            for validated in prepared:
                act = actor or validated["provenance"]["agent"]
                written = self.store.write_entry(validated, actor=act, ts=ts, op="ADD")
                ids.append(written["id"])
        return {"ids": ids, "count": len(ids), "state": "quarantined"}

    def add_receipt(self, receipt: Mapping[str, Any], *, ts: str | None = None) -> dict[str, Any]:
        ts = require_ts(ts or self._now)
        payload = project_receipt(receipt, written_at=ts)
        return self.add(payload, ts=ts)

    def update(
        self,
        entry_id: str,
        patch: Mapping[str, Any],
        *,
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        ts = require_ts(ts or self._now)
        with self.store:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            if "state" in patch:
                raise SchemaError("use promote/supersede/reflect for state transitions")
            merged = dict(entry)
            for k, v in patch.items():
                if k in {"id", "evidence"}:
                    continue
                merged[k] = v
            merged["id"] = entry_id
            merged["state"] = entry["state"]
            written = self.store.write_entry(merged, actor=actor, ts=ts, op="UPDATE")
        self.retriever.rebuild(lexical_only=True)
        return written

    def promote(
        self,
        entry_id: str,
        evidence: Sequence[Mapping[str, Any]],
        *,
        actor: str,
        ts: str | None = None,
        require_test_result_for_code_fix: bool = False,
        block_injection_suspects: bool = False,
    ) -> dict[str, Any]:
        ts = require_ts(ts or self._now)
        if block_injection_suspects:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            hit = scan_entry(entry)
            if hit["suspect"]:
                raise SchemaError(
                    f"promote blocked: injection markers {hit['markers']} (MAPLE promote gate)"
                )
        with self.store:
            written = apply_promote(
                self.store,
                entry_id,
                evidence,
                actor=actor,
                ts=ts,
                require_test_result_for_code_fix=require_test_result_for_code_fix,
            )
        self.retriever.rebuild(lexical_only=True)
        return {"id": written["id"], "state": written["state"]}

    def supersede(
        self,
        old_id: str,
        new_entry: Mapping[str, Any],
        *,
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        ts = require_ts(ts or self._now)
        if self.store.read_entry(old_id) is None:
            raise SchemaError(f"unknown entry: {old_id}")
        # New lesson lands quarantined; old is invalidated after ADD succeeds.
        added = self.add(new_entry, actor=actor, ts=ts)
        with self.store:
            old = self.store.read_entry(old_id)
            if old is None:
                raise SchemaError(f"unknown entry: {old_id}")
            old["state"] = "superseded"
            old["temporal"]["superseded_by"] = added["id"]
            old["temporal"]["superseded_at"] = ts
            self.store.write_entry(old, actor=actor, ts=ts, op="SUPERSEDE")
        self.retriever.rebuild(lexical_only=True)
        return {"old_id": old_id, "new_id": added["id"], "new_state": "quarantined"}

    def delete(
        self,
        *,
        entry_id: str | None = None,
        subject_id: str | None = None,
        actor: str,
        ts: str | None = None,
        reason: str = "erasure",
    ) -> dict[str, Any]:
        ts = require_ts(ts or self._now)
        if not entry_id and not subject_id:
            raise SchemaError("delete requires entry_id or subject_id")
        removed: list[str] = []
        with self.store:
            if entry_id:
                if self.store.delete_entry_file(entry_id, actor=actor, ts=ts, reason=reason):
                    removed.append(entry_id)
            if subject_id:
                for e in list(self.store.iter_entries()):
                    if e["provenance"].get("subject_id") == subject_id:
                        if self.store.delete_entry_file(
                            e["id"], actor=actor, ts=ts, reason=reason
                        ):
                            removed.append(e["id"])
            self.store.drop_indexes()
        self.retriever.rebuild(lexical_only=True)
        return {"removed": sorted(set(removed))}

    def link(
        self,
        entry_id: str,
        *,
        kind: str,
        ref: str,
        digest: str | None = None,
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        ts = require_ts(ts or self._now)
        link: dict[str, Any] = {"kind": kind, "ref": ref}
        if digest:
            link["digest"] = digest
        with self.store:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            links = list(entry.get("links") or [])
            links.append(link)
            entry["links"] = links
            written = self.store.write_entry(entry, actor=actor, ts=ts, op="LINK")
        return written

    # ----- readers ---------------------------------------------------------

    def _version_select(
        self,
        query: str,
        *,
        consumer_scope: str,
        version: str,
        budget: int = 400,
        body_max_chars: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        ChronoMem Select from a pinned entry-id view.

        Loads SoT by id and ranks lexically — ignores live superseded/expired
        filters so rollback still surfaces the pinned snapshot.
        """
        view = ver_checkout_view(self.store.root, version)
        allowed = list(view.get("entry_ids") or [])
        qtok = set(tokenize(query or ""))
        scored: list[tuple[float, dict[str, Any]]] = []
        for eid in allowed:
            entry = self.store.read_entry(str(eid))
            if entry is None:
                continue
            if str(entry.get("scope") or "") != consumer_scope:
                continue
            text = f"{entry.get('title') or ''} {entry.get('body') or ''}"
            etok = set(tokenize(text))
            if not qtok or not (qtok & etok):
                continue
            score = len(qtok & etok) / len(qtok | etok)
            body = str(entry.get("body") or "")
            clipped = body
            truncated = False
            if (
                body_max_chars is not None
                and body_max_chars > 0
                and len(body) > body_max_chars
            ):
                clipped = body[:body_max_chars].rstrip() + "…"
                truncated = True
            scored.append(
                (
                    score,
                    {
                        "id": entry["id"],
                        "title": entry.get("title"),
                        "body": clipped,
                        "body_truncated": truncated,
                        "layer": entry.get("layer"),
                        "scope": entry.get("scope"),
                        "state": entry.get("state"),
                        "conflict_key": entry.get("conflict_key"),
                        "provenance": entry.get("provenance"),
                        "temporal": entry.get("temporal"),
                        "historical": True,
                        "read_version": version,
                        "score": round(score, 6),
                    },
                )
            )
        scored.sort(key=lambda x: (-x[0], x[1].get("id") or ""))
        out: list[dict[str, Any]] = []
        used = 0
        for _, slice_ in scored:
            cost = len(str(slice_.get("body") or "")) + len(
                str(slice_.get("title") or "")
            )
            if used + cost > budget and out:
                break
            used += cost
            out.append(slice_)
        return out

    def search(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        as_of: str | None = None,
        include_contested: bool = False,
        scope_override: Sequence[str] | None = None,
        consumer_domain: str | None = None,
        consumer_env: Sequence[str] | None = None,
        stale_policy: str = "flag",
        consumer_model_id: str | None = None,
        model_policy: str = "flag",
        follow_links: bool = False,
        follow_link_depth: int = 1,
        body_max_chars: int | None = None,
        prefer_helpful: bool = True,
        trusted_sources: Sequence[str] | None = None,
        prefer_fresh: bool = False,
        principal_scopes: Sequence[str] | None = None,
        withhold_injection_suspects: bool = False,
        lifecycle_tiers: Sequence[str] | None = None,
        with_rank_detail: bool = False,
        hot_days: float = 7.0,
        warm_days: float = 30.0,
        min_path_trust: float | None = None,
        trusted_sources_for_trust: Sequence[str] | None = None,
        prefer_dense: bool = False,
        min_retention: float | None = None,
        half_life_days: float = 30.0,
        min_weibull: float | None = None,
        weibull_eta: float = 30.0,
        weibull_kappa: float = 1.0,
        cue_tags: Sequence[str] | None = None,
        refuse_untrusted_lineage: bool = False,
        lineage_max_depth: int = 3,
        memory_roles: Sequence[str] | None = None,
        claims_only: bool = False,
        exclude_superseded: bool = False,
        respect_read_head: bool = True,
        version_commit: str | None = None,
        min_worth: float | None = None,
        worth_min_samples: int = 1,
        worth_unknown_ok: bool = True,
    ) -> list[dict[str, Any]]:
        # Resolve ChronoMem read overlay before live Select
        version = version_commit
        if version is None and respect_read_head:
            version = ver_get_read_head(self.store.root)
        if version:
            # Pinned view Select — must surface later-superseded ids
            slices = self._version_select(
                query,
                consumer_scope=consumer_scope,
                version=version,
                budget=budget,
                body_max_chars=body_max_chars,
            )
        else:
            slices = self.retriever.search(
                query,
                consumer_scope=consumer_scope,
                budget=budget,
                as_of=as_of,
                include_contested=include_contested,
                scope_override=scope_override,
                consumer_domain=consumer_domain,
                consumer_env=consumer_env,
                stale_policy=stale_policy,
                consumer_model_id=consumer_model_id,
                model_policy=model_policy,
                follow_links=follow_links,
                follow_link_depth=follow_link_depth,
                body_max_chars=body_max_chars,
                prefer_helpful=prefer_helpful,
                now=self._now or as_of,
                with_rank_detail=with_rank_detail,
            )
        if trusted_sources:
            allow = {s.strip() for s in trusted_sources if s and str(s).strip()}
            slices = [
                s
                for s in slices
                if str((s.get("provenance") or {}).get("source") or "") in allow
                or any(
                    str((s.get("provenance") or {}).get("source") or "").startswith(p)
                    for p in allow
                )
            ]
        if principal_scopes is not None:
            # GateMem-shaped access control: explicit allowlist; no implicit universal.
            allow_scopes = {str(s).strip() for s in principal_scopes if s and str(s).strip()}
            for s in allow_scopes:
                validate_scope(s)
            slices = [s for s in slices if str(s.get("scope") or "") in allow_scopes]
        if withhold_injection_suspects:
            # MAPLE-Guard retrieval gate proxy — deterministic marker filter.
            kept: list[dict[str, Any]] = []
            for s in slices:
                markers = scan_text(f"{s.get('title') or ''}\n{s.get('body') or ''}")
                if markers:
                    continue
                kept.append(s)
            slices = kept
        if cue_tags is not None:
            want = {str(c).strip().lower() for c in cue_tags if c and str(c).strip()}
            if not want:
                raise SchemaError("cue_tags filter requires at least one tag")
            filtered_cues: list[dict[str, Any]] = []
            for s in slices:
                eid = str(s.get("id") or "")
                entry = self.store.read_entry(eid)
                tags = {str(t).lower() for t in ((entry or {}).get("cue_tags") or [])}
                if want & tags:
                    s["cue_tags"] = sorted(tags)
                    filtered_cues.append(s)
            slices = filtered_cues
        now_ts = self._now or as_of
        all_entries = list(self.store.iter_entries()) if (
            prefer_dense
            or min_retention is not None
            or min_weibull is not None
            or min_path_trust is not None
            or refuse_untrusted_lineage
            or now_ts
        ) else []
        if now_ts:
            for s in slices:
                eid = s.get("id")
                entry = self.store.read_entry(str(eid)) if eid else None
                if entry:
                    s["lifecycle_tier"] = lifecycle_tier(
                        entry, now=now_ts, hot_days=hot_days, warm_days=warm_days
                    )
                    s["retention_score"] = retention_score(
                        entry, now=now_ts, half_life_days=half_life_days
                    )
                    s["weibull_relevance"] = fade_weibull_relevance(
                        entry,
                        now=now_ts,
                        eta_days=weibull_eta,
                        kappa=weibull_kappa,
                    )
                    if entry.get("cue_tags") and "cue_tags" not in s:
                        s["cue_tags"] = entry["cue_tags"]
        if lifecycle_tiers is not None:
            allow_tiers = {str(t).strip().lower() for t in lifecycle_tiers if t}
            bad = allow_tiers - LIFECYCLE_TIERS
            if bad:
                raise SchemaError(f"lifecycle_tiers must be subset of {sorted(LIFECYCLE_TIERS)}")
            if not now_ts:
                raise SchemaError("lifecycle_tiers filter requires store clock (--now) or as_of")
            slices = [s for s in slices if s.get("lifecycle_tier") in allow_tiers]
        if min_retention is not None:
            if min_retention < 0 or min_retention > 1:
                raise SchemaError("min_retention must be in [0, 1]")
            if not now_ts:
                raise SchemaError("min_retention requires store clock (--now) or as_of")
            slices = [s for s in slices if float(s.get("retention_score") or 0) >= min_retention]
        if min_weibull is not None:
            if min_weibull < 0 or min_weibull > 1:
                raise SchemaError("min_weibull must be in [0, 1]")
            if not now_ts:
                raise SchemaError("min_weibull requires store clock (--now) or as_of")
            slices = [
                s
                for s in slices
                if float(s.get("weibull_relevance") or 0) >= min_weibull
            ]
        if min_path_trust is not None:
            if min_path_trust < 0 or min_path_trust > 1:
                raise SchemaError("min_path_trust must be in [0, 1]")
            filtered: list[dict[str, Any]] = []
            for s in slices:
                eid = str(s.get("id") or "")
                try:
                    pt = graph_path_trust(
                        all_entries,
                        eid,
                        trusted_sources=trusted_sources_for_trust or trusted_sources,
                    )
                except KeyError:
                    continue
                s["path_trust"] = pt["path_trust"]
                if pt["path_trust"] >= min_path_trust:
                    filtered.append(s)
            slices = filtered
        if prefer_dense:
            for s in slices:
                eid = str(s.get("id") or "")
                try:
                    dens = act_connection_density(all_entries, eid)
                    s["connection_density"] = dens["density"]
                    s["link_degree"] = dens["degree"]
                except KeyError:
                    s["connection_density"] = 0.0
                    s["link_degree"] = 0
            slices = sorted(
                slices,
                key=lambda x: (-float(x.get("connection_density") or 0), x.get("id") or ""),
            )
        if prefer_fresh:
            # SSGM-style read filter proxy: soft rank by last_verified (no SoT mutate).
            def _last_verified(s: dict[str, Any]) -> str:
                eid = s.get("id")
                if eid:
                    e = self.store.read_entry(str(eid))
                    if e:
                        return str((e.get("temporal") or {}).get("last_verified") or "")
                return str(s.get("last_verified") or "")

            slices = sorted(slices, key=_last_verified, reverse=True)
        if refuse_untrusted_lineage:
            kept_lin: list[dict[str, Any]] = []
            for s in slices:
                eid = str(s.get("id") or "")
                try:
                    lt = graph_lineage_trust(
                        all_entries, eid, max_depth=lineage_max_depth
                    )
                except KeyError:
                    continue
                s["lineage_trust"] = lt["label"]
                if lt["label"] == "Trusted":
                    kept_lin.append(s)
            slices = kept_lin
        # Attach / filter MemIR-shaped memory roles
        for s in slices:
            eid = str(s.get("id") or "")
            entry = self.store.read_entry(eid)
            if entry:
                s["memory_role"] = infer_memory_role(entry)
        if memory_roles is not None or claims_only:
            allow_roles = (
                {"claim", "decision"}
                if claims_only
                else {str(r).strip().lower() for r in (memory_roles or []) if r}
            )
            if not allow_roles:
                raise SchemaError("memory_roles filter requires at least one role")
            bad = allow_roles - {"evidence", "claim", "decision"}
            if bad:
                raise SchemaError(f"memory_roles must be subset of evidence|claim|decision")
            slices = [s for s in slices if s.get("memory_role") in allow_roles]
        # MemStrata-shaped supersession filter (skip under version Select —
        # pinned snapshot intentionally includes later-superseded facts)
        if exclude_superseded and not version:
            winners = supersession_winners(list(self.store.iter_entries()))
            kept_cur: list[dict[str, Any]] = []
            for s in slices:
                eid = str(s.get("id") or "")
                entry = self.store.read_entry(eid)
                if entry is None:
                    continue
                if is_current_fact(entry, winners):
                    kept_cur.append(s)
            slices = kept_cur
        # Memory Worth Select suppression
        if min_worth is not None:
            kept_mw: list[dict[str, Any]] = []
            for s in slices:
                eid = str(s.get("id") or "")
                entry = self.store.read_entry(eid)
                if entry is None:
                    continue
                report = worth_memory_worth(entry)
                s["memory_worth"] = report.get("mw")
                s["worth_samples"] = report.get("samples")
                if passes_min_worth(
                    entry,
                    min_worth=min_worth,
                    min_samples=worth_min_samples,
                    unknown_ok=worth_unknown_ok,
                ):
                    kept_mw.append(s)
            slices = kept_mw
        return slices

    def search_explain(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """SEARCH with channel rank detail (UC-58)."""
        return self.search(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            with_rank_detail=True,
            **kwargs,
        )

    def verify_journal_chain(self) -> dict[str, Any]:
        """GPM-shaped journal hash-chain verification."""
        return verify_journal_chain(self.store)

    def journal_chain_head(self) -> dict[str, Any]:
        """Current journal chain head + counts."""
        return journal_chain_head(self.store)

    def spread_activate(
        self,
        seed_ids: Sequence[str],
        *,
        max_hops: int = 2,
        decay: float = 0.5,
        lateral_inhibit: float = 0.15,
    ) -> dict[str, Any]:
        """SYNAPSE-shaped spreading activation from seed entry ids."""
        return act_spread_activate(
            self.store.iter_entries(),
            seed_ids=seed_ids,
            max_hops=max_hops,
            decay=decay,
            lateral_inhibit=lateral_inhibit,
        )

    def connection_density(self, entry_id: str) -> dict[str, Any]:
        """SodaMem-shaped connection density for one entry."""
        try:
            return act_connection_density(self.store.iter_entries(), entry_id)
        except KeyError as exc:
            raise SchemaError(f"unknown entry: {entry_id}") from exc

    def retention_score(
        self,
        entry_id: str,
        *,
        now: str | None = None,
        half_life_days: float = 30.0,
    ) -> dict[str, Any]:
        """Oblivion-shaped retention score for one entry."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        ts = require_ts(now or self._now)
        score = retention_score(entry, now=ts, half_life_days=half_life_days)
        return {"id": entry_id, "retention_score": score, "now": ts, "half_life_days": half_life_days}

    def blast_radius(self, entry_id: str, *, max_depth: int = 3) -> dict[str, Any]:
        """LINK neighborhood blast radius (RippleMem/MAP-Graph shaped)."""
        try:
            return graph_blast_radius(
                self.store.iter_entries(), entry_id, max_depth=max_depth
            )
        except KeyError as exc:
            raise SchemaError(f"unknown entry: {entry_id}") from exc

    def merge_classify(
        self,
        entry_id_a: str,
        entry_id_b: str,
        *,
        merge_threshold: float = 0.85,
        relate_threshold: float = 0.45,
    ) -> dict[str, Any]:
        """MELD-shaped five-outcome merge classifier — report only, never mutates."""
        a = self.store.read_entry(entry_id_a)
        b = self.store.read_entry(entry_id_b)
        if a is None:
            raise SchemaError(f"unknown entry: {entry_id_a}")
        if b is None:
            raise SchemaError(f"unknown entry: {entry_id_b}")
        result = graph_merge_classify(
            a,
            b,
            merge_threshold=merge_threshold,
            relate_threshold=relate_threshold,
        )
        result["a"] = entry_id_a
        result["b"] = entry_id_b
        return result

    def path_trust(
        self,
        entry_id: str,
        *,
        trusted_sources: Sequence[str] | None = None,
        max_depth: int = 3,
    ) -> dict[str, Any]:
        """MAP-Graph-shaped multiplicative path trust along entry LINKs."""
        try:
            return graph_path_trust(
                self.store.iter_entries(),
                entry_id,
                trusted_sources=trusted_sources,
                max_depth=max_depth,
            )
        except KeyError as exc:
            raise SchemaError(f"unknown entry: {entry_id}") from exc

    def lifecycle_inventory(
        self,
        *,
        now: str | None = None,
        hot_days: float = 7.0,
        warm_days: float = 30.0,
    ) -> dict[str, Any]:
        """AMV-L-shaped tier inventory over promoted/contested surface."""
        ts = require_ts(now or self._now)
        return lifecycle_inventory(
            self.store.iter_entries(),
            now=ts,
            hot_days=hot_days,
            warm_days=warm_days,
        )

    def revoke_by_key(
        self,
        conflict_key: str,
        *,
        evidence: Sequence[Mapping[str, Any]],
        actor: str,
        ts: str | None = None,
        keep_id: str | None = None,
    ) -> dict[str, Any]:
        """
        TEPA-shaped keyed revoke: remove active precedents under conflict_key
        from ordinary retrieval while retaining them on disk for audit.
        """
        ts = require_ts(ts or self._now)
        key = parse_conflict_key(conflict_key)
        if not evidence:
            raise SchemaError("revoke_by_key requires external evidence")
        validated_ev = [validate_evidence(x) for x in evidence]
        revoked_ids: list[str] = []
        kept: str | None = None
        with self.store:
            for e in list(self.store.iter_entries(states={"promoted", "contested"})):
                if str(e.get("conflict_key") or "") != key:
                    continue
                if keep_id and e["id"] == keep_id:
                    kept = e["id"]
                    continue
                e["state"] = "revoked"
                e["temporal"]["revoked_at"] = ts
                e["temporal"]["revoked_key"] = key
                e["evidence"] = list(e.get("evidence") or []) + validated_ev
                self.store.write_entry(e, actor=actor, ts=ts, op="REVOKE")
                revoked_ids.append(e["id"])
        self.retriever.rebuild(lexical_only=True)
        return {
            "conflict_key": key,
            "revoked": revoked_ids,
            "kept": kept,
            "count": len(revoked_ids),
            "note": "TEPA-shaped revoke — history retained; not DELETE",
        }

    def unrevoke(
        self,
        entry_id: str,
        *,
        evidence: Sequence[Mapping[str, Any]],
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """Re-activate a revoked precedent into promoted (evidenced)."""
        ts = require_ts(ts or self._now)
        if not evidence:
            raise SchemaError("unrevoke requires external evidence")
        validated_ev = [validate_evidence(x) for x in evidence]
        with self.store:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            if entry.get("state") != "revoked":
                raise SchemaError("unrevoke only applies to revoked entries")
            entry["state"] = "promoted"
            entry["temporal"]["last_verified"] = ts
            entry["temporal"].pop("revoked_at", None)
            entry["temporal"].pop("revoked_key", None)
            entry["evidence"] = list(entry.get("evidence") or []) + validated_ev
            written = self.store.write_entry(entry, actor=actor, ts=ts, op="UNREVOKE")
        self.retriever.rebuild(lexical_only=True)
        return {"id": written["id"], "state": "promoted"}

    def pack_seal(self, pack_dir: str | Path) -> dict[str, Any]:
        """Tamper-evident seal over an exported pack."""
        return pack_seal(Path(pack_dir))

    def verify_pack_seal(self, pack_dir: str | Path, seal: Mapping[str, Any]) -> dict[str, Any]:
        """Compare a prior pack seal to the on-disk pack."""
        return verify_pack_seal(Path(pack_dir), dict(seal))

    def reflect(
        self,
        *,
        actor: str,
        ts: str | None = None,
        similarity_threshold: float = 0.8,
        stale_before: str | None = None,
    ) -> dict[str, Any]:
        """Batched consolidation: dedupe, expire, surface conflicts — no auto-resolve."""
        ts = require_ts(ts or self._now)
        merged: list[dict[str, str]] = []
        expired: list[str] = []
        conflicts: list[dict[str, Any]] = []
        dangling_links: list[dict[str, str]] = []

        with self.store:
            promoted = list(self.store.iter_entries(states={"promoted", "contested"}))

            # expire
            for e in list(promoted):
                exp = e["temporal"].get("expiry")
                if exp and exp <= ts or stale_before and e["temporal"]["last_verified"] < stale_before:
                    e["state"] = "expired"
                    self.store.write_entry(e, actor=actor, ts=ts, op="REFLECT_EXPIRE")
                    expired.append(e["id"])

            promoted = list(self.store.iter_entries(states={"promoted"}))

            # Near-duplicates: contradictory evidence → contested (Q5);
            # agreeing near-duplicates → provenance-preserving merge.
            seen: set[str] = set()
            for i, a in enumerate(promoted):
                if a["id"] in seen:
                    continue
                for b in promoted[i + 1 :]:
                    if b["id"] in seen:
                        continue
                    if a["scope"] != b["scope"] or a["id"] == b["id"]:
                        continue
                    if _title_sim(a["title"], b["title"]) < similarity_threshold:
                        continue

                    va = {e.get("verdict") for e in (a.get("evidence") or [])}
                    vb = {e.get("verdict") for e in (b.get("evidence") or [])}
                    contradictory = ("supports" in va and "refutes" in vb) or (
                        "refutes" in va and "supports" in vb
                    )
                    if contradictory:
                        a["state"] = "contested"
                        b["state"] = "contested"
                        a["contested_with"] = sorted(
                            set(a.get("contested_with") or []) | {b["id"]}
                        )
                        b["contested_with"] = sorted(
                            set(b.get("contested_with") or []) | {a["id"]}
                        )
                        self.store.write_entry(a, actor=actor, ts=ts, op="REFLECT_CONFLICT")
                        self.store.write_entry(b, actor=actor, ts=ts, op="REFLECT_CONFLICT")
                        conflicts.append({"a": a["id"], "b": b["id"]})
                        seen.add(a["id"])
                        seen.add(b["id"])
                        continue

                    a["links"] = _uniq_links(a.get("links"), b.get("links"))
                    a["links"] = _uniq_links(
                        a["links"],
                        [
                            {"kind": "entry", "ref": b["id"]},
                            {
                                "kind": "source",
                                "ref": (
                                    f"merged-from:{b['id']}:"
                                    f"agent={b['provenance']['agent']}:"
                                    f"task={b['provenance']['task']}"
                                ),
                            },
                        ],
                    )
                    a["evidence"] = list(a.get("evidence") or []) + list(
                        b.get("evidence") or []
                    )
                    self.store.write_entry(a, actor=actor, ts=ts, op="REFLECT_MERGE")
                    b["state"] = "superseded"
                    b["temporal"]["superseded_by"] = a["id"]
                    b["temporal"]["superseded_at"] = ts
                    self.store.write_entry(b, actor=actor, ts=ts, op="REFLECT_MERGE_DROP")
                    seen.add(b["id"])
                    merged.append({"kept": a["id"], "dropped": b["id"]})

            # dangling links
            by_id = {e["id"]: e for e in self.store.iter_entries()}
            for e in self.store.iter_entries():
                for link in e.get("links") or []:
                    if link.get("kind") == "entry":
                        ref = link["ref"]
                        if ref not in by_id and not self.store.read_entry(ref):
                            dangling_links.append({"from": e["id"], "ref": ref})

        self.retriever.rebuild(lexical_only=True)
        return {
            "merged": merged,
            "expired": expired,
            "conflicts": conflicts,
            "dangling_links": dangling_links,
        }

    def list_contested(self) -> list[dict[str, Any]]:
        """Surface open conflicts for human/oracle resolution (no auto-merge)."""
        out: list[dict[str, Any]] = []
        for e in self.store.iter_entries(states={"contested"}):
            out.append(
                {
                    "id": e["id"],
                    "title": e["title"],
                    "scope": e["scope"],
                    "contested_with": list(e.get("contested_with") or []),
                    "provenance": e["provenance"],
                }
            )
        return sorted(out, key=lambda x: x["id"])

    def conflict_surface(self, *, body_max_chars: int = 240) -> dict[str, Any]:
        """
        StateFuse-shaped conflict-preserving surface — pairs stay visible; never collapsed.

        Returns unique contested pairs with both sides' titles/body previews.
        """
        pairs: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()

        def _clip(text: str) -> str:
            t = str(text or "")
            if body_max_chars and len(t) > body_max_chars:
                return t[:body_max_chars].rstrip() + "…"
            return t

        for e in self.store.iter_entries(states={"contested"}):
            for other_id in e.get("contested_with") or []:
                oid = str(other_id)
                key = tuple(sorted([e["id"], oid]))
                if key in seen:
                    continue
                seen.add(key)  # type: ignore[arg-type]
                other = self.store.read_entry(oid)
                pairs.append(
                    {
                        "a": {
                            "id": e["id"],
                            "title": e.get("title"),
                            "state": e.get("state"),
                            "body": _clip(str(e.get("body") or "")),
                        },
                        "b": {
                            "id": oid,
                            "title": (other or {}).get("title"),
                            "state": (other or {}).get("state"),
                            "body": _clip(str((other or {}).get("body") or "")),
                            "missing": other is None,
                        },
                        "preserved": True,
                    }
                )
        return {
            "conflicts": pairs,
            "count": len(pairs),
            "note": "conflict-preserving — no auto-collapse (StateFuse thesis)",
        }

    def resolve_contested(
        self,
        *,
        winner_id: str,
        loser_id: str,
        evidence: Sequence[Mapping[str, Any]],
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """Evidenced supersede of a contested pair (TECH_SPEC Q5 — never auto-resolve)."""
        ts = require_ts(ts or self._now)
        with self.store:
            result = apply_resolve_contested(
                self.store,
                winner_id=winner_id,
                loser_id=loser_id,
                evidence=evidence,
                actor=actor,
                ts=ts,
            )
        self.retriever.rebuild(lexical_only=True)
        return result

    def verify(self) -> dict[str, Any]:
        """C4 integrity report over the live store."""
        return verify_store(self.store)

    def store_seal(self) -> dict[str, Any]:
        """Tamper-evident content+journal seal (MemMark R3-adjacent)."""
        return store_seal(self.store)

    def verify_seal(self, seal: Mapping[str, Any]) -> dict[str, Any]:
        """Compare a prior seal to the live store."""
        return verify_seal(self.store, dict(seal))

    def attribution_receipt(self, entry_id: str) -> dict[str, Any]:
        """Deterministic attribution receipt for one entry."""
        return attribution_receipt(self.store, entry_id)

    def replay_consistency(self) -> dict[str, Any]:
        """Soft journal↔SoT replay consistency report."""
        return replay_consistency(self.store)

    def reviewer_corrections(
        self,
        *,
        limit: int = 10,
        include_contested: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Bounded recent-correction slice for reviewer/coordinator roles (C8).

        Contested entries first (open risk), then newest promoted lessons.
        Never dumps raw receipt histories.
        """
        if limit < 1:
            raise SchemaError("limit must be >= 1")
        contested: list[dict[str, Any]] = []
        if include_contested:
            for e in self.store.iter_entries(states={"contested"}):
                contested.append(_correction_slice(e, kind="contested"))
        promoted: list[dict[str, Any]] = []
        for e in self.store.iter_entries(states={"promoted"}):
            promoted.append(_correction_slice(e, kind="promoted"))
        promoted.sort(key=lambda x: x["last_verified"], reverse=True)
        return (contested + promoted)[:limit]

    def hydrate(
        self,
        pack_dir: str | Path,
        *,
        actor: str,
        ts: str | None = None,
        promote: bool = False,
        evidence: Sequence[Mapping[str, Any]] | None = None,
        require_verify: bool = False,
        expected_seal: Mapping[str, Any] | None = None,
        expected_policy_digest: str | None = None,
    ) -> dict[str, Any]:
        """
        Import a redacted pack: ADD payloads, optionally promote with caller evidence.

        Storage ≠ pack: hydrate never copies private source trees.
        When require_verify=True, PAM-shaped verify_import must pass first.
        """
        ts = require_ts(ts or self._now)
        if require_verify:
            gate = verify_import(
                Path(pack_dir),
                expected_seal=dict(expected_seal) if expected_seal else None,
                expected_policy_digest=expected_policy_digest,
            )
            if not gate.get("ok"):
                raise SchemaError(
                    f"verify_import blocked hydrate: halted_at={gate.get('halted_at')}"
                )
        payloads = hydrate_pack(Path(pack_dir), written_at=ts)
        added_ids: list[str] = []
        for payload in payloads:
            assert_distilled_entry(payload)
            added = self.add(payload, actor="pack-hydrate", ts=ts)
            added_ids.append(added["id"])
            if promote:
                if not evidence:
                    raise SchemaError("hydrate promote=True requires external evidence")
                self.promote(added["id"], evidence, actor=actor, ts=ts)
        return {"added": added_ids, "promoted": bool(promote), "count": len(added_ids)}

    def export(
        self,
        dest: str | Path,
        *,
        scope: str | Sequence[str],
        audience: str,
        purpose: str,
        created_at: str | None = None,
        expiry: str,
        subject_allowlist: Sequence[str] | None = None,
        entry_ids: Sequence[str] | None = None,
        require_release: bool = False,
        allow_contested: bool = False,
    ) -> dict[str, Any]:
        created_at = require_ts(created_at or self._now)
        gate: dict[str, Any] | None = None
        if require_release:
            gate = self.release_gate(
                allow_contested=allow_contested,
                now=created_at,
            )
            if not gate.get("ok"):
                raise SchemaError(
                    f"release_gate blocked export: {gate.get('barriers')}"
                )
        manifest = export_pack(
            self.store,
            Path(dest),
            scope=scope,
            audience=audience,
            purpose=purpose,
            created_at=created_at,
            expiry=expiry,
            subject_allowlist=subject_allowlist,
            entry_ids=entry_ids,
        )
        if gate is not None:
            manifest = dict(manifest)
            manifest["release_head"] = gate.get("head")
            manifest["release_ok"] = True
        return manifest

    def record_outcome(
        self,
        entry_id: str,
        outcome: str,
        *,
        actor: str,
        ts: str | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        """
        Consumer feedback after using a lesson (reinforce / demote; FF-8).

        helpful → bumps last_verified; harmful → counters for reviewer attention.
        Does not auto-contest (that still needs evidenced resolve).
        """
        if outcome not in OUTCOME_KINDS:
            raise SchemaError(f"outcome must be one of {sorted(OUTCOME_KINDS)}")
        ts = require_ts(ts or self._now)
        with self.store:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            if entry["state"] not in {"promoted", "contested"}:
                raise SchemaError("outcome only applies to promoted/contested entries")
            usage = normalize_usage(entry.get("usage"))
            usage[outcome] = int(usage.get(outcome) or 0) + 1
            usage["last_outcome"] = outcome
            usage["last_outcome_at"] = ts
            entry["usage"] = usage
            if outcome == "helpful":
                entry["temporal"]["last_verified"] = ts
            if note:
                links = list(entry.get("links") or [])
                links.append(
                    {
                        "kind": "source",
                        "ref": f"outcome:{outcome}:actor={actor}:{note[:120]}",
                    }
                )
                entry["links"] = links
            written = self.store.write_entry(
                entry, actor=actor, ts=ts, op=f"OUTCOME_{outcome.upper()}"
            )
        return {
            "id": written["id"],
            "usage": written.get("usage"),
            "last_verified": written["temporal"]["last_verified"],
        }

    def pin(
        self,
        entry_id: str,
        *,
        actor: str,
        pinned: bool = True,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """Pin a promoted lesson so SEARCH ranks it ahead of peers."""
        ts = require_ts(ts or self._now)
        with self.store:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            if entry["state"] != "promoted":
                raise SchemaError("only promoted entries can be pinned")
            usage = normalize_usage(entry.get("usage"))
            usage["pinned"] = bool(pinned)
            entry["usage"] = usage
            written = self.store.write_entry(entry, actor=actor, ts=ts, op="PIN")
        return {"id": written["id"], "pinned": pinned}

    def stale_report(self, *, now: str | None = None) -> list[dict[str, Any]]:
        """List promoted entries past the staleness horizon (FF-8 batch review)."""
        point = require_ts(now or self._now)
        horizon = self.retriever.staleness_horizon
        out: list[dict[str, Any]] = []
        for e in self.store.iter_entries(states={"promoted"}):
            if is_stale(e, point, horizon):
                out.append(
                    {
                        "id": e["id"],
                        "title": e["title"],
                        "scope": e["scope"],
                        "last_verified": e["temporal"]["last_verified"],
                        "expiry": e["temporal"].get("expiry"),
                        "helpful": (e.get("usage") or {}).get("helpful", 0),
                        "harmful": (e.get("usage") or {}).get("harmful", 0),
                    }
                )
        out.sort(key=lambda x: x["last_verified"])
        return out

    def reverify(
        self,
        entry_ids: Sequence[str],
        evidence: Sequence[Mapping[str, Any]],
        *,
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """Batch-refresh last_verified with external oracle evidence (model swap / FF-8)."""
        ts = require_ts(ts or self._now)
        refreshed: list[str] = []
        with self.store:
            for eid in entry_ids:
                entry = self.store.read_entry(eid)
                if entry is None:
                    raise SchemaError(f"unknown entry: {eid}")
                if entry["state"] != "promoted":
                    raise SchemaError(f"reverify requires promoted state: {eid}")
                validated = validate_promotion_evidence(
                    entry, evidence, store=self.store
                )
                entry["evidence"] = list(entry.get("evidence") or []) + list(validated)
                entry["temporal"]["last_verified"] = ts
                self.store.write_entry(entry, actor=actor, ts=ts, op="REVERIFY")
                refreshed.append(eid)
        return {"refreshed": refreshed, "last_verified": ts}

    def related(self, entry_id: str) -> dict[str, Any]:
        """Graph neighborhood via LINK kind=entry (FF-6) — outbound + inbound."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        outbound = [
            {"kind": lnk.get("kind"), "ref": lnk.get("ref")}
            for lnk in (entry.get("links") or [])
        ]
        inbound: list[dict[str, str]] = []
        for other in self.store.iter_entries():
            if other["id"] == entry_id:
                continue
            for lnk in other.get("links") or []:
                if lnk.get("kind") == "entry" and lnk.get("ref") == entry_id:
                    inbound.append({"from": other["id"], "title": other["title"]})
        return {"id": entry_id, "outbound": outbound, "inbound": inbound}

    def stats(self, *, now: str | None = None) -> dict[str, Any]:
        """Store health dashboard — counts by state/layer; stale + contested flags."""
        by_state: dict[str, int] = {}
        by_layer: dict[str, int] = {}
        by_scope: dict[str, int] = {}
        total = 0
        for e in self.store.iter_entries():
            total += 1
            by_state[e["state"]] = by_state.get(e["state"], 0) + 1
            by_layer[e["layer"]] = by_layer.get(e["layer"], 0) + 1
            by_scope[e["scope"]] = by_scope.get(e["scope"], 0) + 1
        stale_n = len(self.stale_report(now=now)) if (now or self._now) else 0
        return {
            "store_id": self.store.store_id,
            "total": total,
            "by_state": by_state,
            "by_layer": by_layer,
            "by_scope": by_scope,
            "stale_promoted": stale_n,
            "contested": by_state.get("contested", 0),
            "attachments": len(list(self.store.attachments.glob("*"))),
        }

    def timeline(self, entry_id: str) -> list[dict[str, Any]]:
        """Journal history for one entry (C4 inspectability)."""
        rows = [
            {"op": r["op"], "actor": r["actor"], "ts": r["ts"]}
            for r in self.store.iter_journal(entry_id=entry_id)
        ]
        if not rows and self.store.read_entry(entry_id) is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return rows

    def lineage(self, entry_id: str) -> dict[str, Any]:
        """
        TOKI-shaped audit lineage — supersede chain + journal; loser rows stay on disk.

        Walks superseded_by forward and predecessors that point at this id.
        Never erases the losing fact (audit-erasure anomaly exclusion).
        """
        entry = self.store.read_entry(entry_id)
        if entry is None and not any(
            True for _ in self.store.iter_journal(entry_id=entry_id)
        ):
            raise SchemaError(f"unknown entry: {entry_id}")

        chain_forward: list[dict[str, Any]] = []
        cur = entry
        seen: set[str] = {entry_id}
        while cur is not None:
            nxt = (cur.get("temporal") or {}).get("superseded_by")
            if not nxt or nxt in seen:
                break
            seen.add(str(nxt))
            nxt_e = self.store.read_entry(str(nxt))
            chain_forward.append(
                {
                    "id": str(nxt),
                    "title": (nxt_e or {}).get("title"),
                    "state": (nxt_e or {}).get("state"),
                    "missing": nxt_e is None,
                }
            )
            cur = nxt_e

        predecessors: list[dict[str, Any]] = []
        for e in self.store.iter_entries():
            if (e.get("temporal") or {}).get("superseded_by") == entry_id:
                predecessors.append(
                    {
                        "id": e["id"],
                        "title": e.get("title"),
                        "state": e.get("state"),
                        "superseded_at": (e.get("temporal") or {}).get("superseded_at"),
                    }
                )

        return {
            "id": entry_id,
            "present": entry is not None,
            "state": (entry or {}).get("state"),
            "title": (entry or {}).get("title"),
            "superseded_by": (entry or {}).get("temporal", {}).get("superseded_by")
            if entry
            else None,
            "predecessors": predecessors,
            "successors": chain_forward,
            "journal": [
                {"op": r["op"], "actor": r["actor"], "ts": r["ts"]}
                for r in self.store.iter_journal(entry_id=entry_id)
            ],
            "note": "audit rows preserved — TOKI audit-erasure defence",
        }

    def belief_at(
        self,
        as_of: str,
        *,
        consumer_scope: str,
        query: str | None = None,
        budget: int = 400,
        consumer_domain: str | None = None,
        principal_scopes: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """
        Bi-temporal point-in-time belief (TOKI / LongMemEval updates).

        With query: SEARCH at as_of (historical flags on). Without query: inventory
        of beliefs valid at as_of in scope (compact id/title/state).
        """
        point = require_ts(as_of)
        if query is not None and str(query).strip():
            slices = self.search(
                str(query),
                consumer_scope=consumer_scope,
                as_of=point,
                budget=budget,
                consumer_domain=consumer_domain,
                principal_scopes=principal_scopes,
            )
            return {
                "as_of": point,
                "mode": "search",
                "slices": slices,
                "count": len(slices),
            }

        beliefs: list[dict[str, Any]] = []
        for e in self.store.iter_entries():
            if not _valid_at_point(e, point):
                continue
            if not _scope_allows(
                e["scope"],
                consumer_scope,
                consumer_domain=consumer_domain,
                scope_override=None,
            ):
                continue
            if principal_scopes is not None:
                allow = {str(s).strip() for s in principal_scopes if s and str(s).strip()}
                if e["scope"] not in allow:
                    continue
            beliefs.append(
                {
                    "id": e["id"],
                    "title": e.get("title"),
                    "state": e.get("state"),
                    "scope": e.get("scope"),
                    "valid_from": e["temporal"]["valid_from"],
                    "superseded_at": e["temporal"].get("superseded_at"),
                    "historical": e.get("state") in {"superseded", "expired"},
                }
            )
        beliefs.sort(key=lambda x: x["id"])
        return {
            "as_of": point,
            "mode": "inventory",
            "beliefs": beliefs,
            "count": len(beliefs),
            "note": "includes later-superseded beliefs still valid at as_of",
        }

    def attach(
        self,
        data: bytes,
        *,
        entry_id: str | None = None,
        actor: str,
        ts: str | None = None,
        kind: str = "artifact",
    ) -> dict[str, Any]:
        """Store bytes by digest; optionally LINK to an entry (FF-6)."""
        ts = require_ts(ts or self._now)
        digest = self.store.put_attachment(data)
        result: dict[str, Any] = {"digest": digest, "bytes": len(data)}
        if entry_id:
            linked = self.link(
                entry_id, kind=kind, ref=f"attachment:{digest}", digest=digest, actor=actor, ts=ts
            )
            result["entry_id"] = linked["id"]
        return result

    def verify_pack(self, pack_dir: str | Path) -> dict[str, Any]:
        """C3 offline pack check (stamps + secret scan)."""
        return verify_pack(Path(pack_dir))

    def entry_schema(self) -> dict[str, Any]:
        """JSON Schema 2020-12 for Stele entries (interop / tooling)."""
        from stele_core.schema_json import entry_json_schema

        return entry_json_schema()

    def snapshot(self, dest: str | Path, *, actor: str, ts: str | None = None) -> dict[str, Any]:
        """
        Cold copy of SoT (manifest, journal, entries, attachments) — not indexes.

        Indexes are derived; rebuild after restore. Journal records SNAPSHOT.
        File-backed stores only — MySQL durable SoT is not a Path tree to copy.
        """
        import shutil

        if getattr(self.store, "backend", "file") != "file":
            raise SchemaError(
                "snapshot is file-store only; hosted MySQL SoT has no Path layout to copy"
            )
        ts = require_ts(ts or self._now)
        dest_p = Path(dest)
        if dest_p.exists() and any(dest_p.iterdir()):
            raise SchemaError(f"snapshot dest must be empty or new: {dest_p}")
        dest_p.mkdir(parents=True, exist_ok=True)
        with self.store:
            for name in ("stele.json", "journal.ndjson"):
                src = self.store.root / name
                if src.exists():
                    shutil.copy2(src, dest_p / name)
            for sub in ("entries", "attachments"):
                src_d = self.store.root / sub
                if src_d.exists():
                    shutil.copytree(src_d, dest_p / sub, dirs_exist_ok=True)
            self.store.journal(
                "SNAPSHOT",
                entry_id=None,
                actor=actor,
                payload={"dest": str(dest_p.resolve())},
                ts=ts,
            )
        return {
            "dest": str(dest_p.resolve()),
            "store_id": self.store.store_id,
            "entries": self.stats().get("total", 0),
        }

    def doctor(self, *, now: str | None = None) -> dict[str, Any]:
        """Operator health: verify + stats + contested + stale in one report."""
        v = self.verify()
        st = self.stats(now=now)
        contested = self.list_contested()
        stale = self.stale_report(now=now)
        ok = bool(v.get("ok"))
        return {
            "ok": ok,
            "verify": v,
            "stats": st,
            "contested_ids": [c.get("id") for c in contested],
            "stale_ids": [s.get("id") for s in stale],
            "warnings": ([] if ok else ["store integrity failed"])
            + (["contested entries open"] if contested else [])
            + (["stale promoted entries"] if stale else []),
        }

    def health_report(self, *, now: str | None = None) -> dict[str, Any]:
        """
        Unified operator health — doctor + journal chain + injection + seal head.
        """
        doc = self.doctor(now=now)
        chain = self.verify_journal_chain()
        seal = self.store_seal()
        inj = self.injection_scan(limit=50)
        replay = self.replay_consistency()
        barriers: list[str] = []
        if not doc.get("ok"):
            barriers.append("store_integrity")
        if not chain.get("ok"):
            barriers.append("journal_chain")
        if not replay.get("ok"):
            barriers.append("replay_consistency")
        if doc.get("contested_ids"):
            barriers.append("contested_open")
        if inj.get("count", 0) > 0:
            barriers.append("injection_suspects")
        return {
            "ok": len(barriers) == 0,
            "barriers": barriers,
            "doctor": doc,
            "journal_chain": {
                "ok": chain.get("ok"),
                "head": chain.get("head"),
                "row_count": chain.get("row_count"),
            },
            "seal_root": seal.get("root"),
            "injection_suspects": inj.get("count", 0),
            "replay_ok": replay.get("ok"),
            "note": "unified health — not a product SLA claim",
        }

    def release_gate(
        self,
        *,
        expected_head: str | None = None,
        allow_contested: bool = False,
        allow_injection_suspects: bool = False,
        allow_stale: bool = True,
        now: str | None = None,
        issue_receipt: bool = False,
        record_abstain: bool = False,
        actor: str | None = None,
        claim_ids: Sequence[str] | None = None,
        policy_version: str = "stele-release-1",
        query_hash: str | None = None,
    ) -> dict[str, Any]:
        """
        GPM-shaped fail-closed release gate before public pack/export.

        Re-reads journal head; mismatches against expected_head fail closed.
        When issue_receipt=True and released, writes a local decision receipt.
        Abstain receipts only when record_abstain=True (GPM default: no record).
        """
        health = self.health_report(now=now)
        barriers = list(health.get("barriers") or [])
        head = (health.get("journal_chain") or {}).get("head")
        if expected_head is not None and expected_head != head:
            barriers.append("head_mismatch")
        # Re-verify head after forming decision view (GPM fail-closed).
        head2 = self.journal_chain_head().get("head")
        if head2 != head:
            barriers.append("head_drift")
        if allow_contested:
            barriers = [b for b in barriers if b != "contested_open"]
        if allow_injection_suspects:
            barriers = [b for b in barriers if b != "injection_suspects"]
        if not allow_stale:
            stale = self.stale_report(now=now)
            if stale:
                barriers.append("stale_promoted")
        # Dedupe preserve order
        seen: set[str] = set()
        uniq: list[str] = []
        for b in barriers:
            if b not in seen:
                seen.add(b)
                uniq.append(b)
        ok = len(uniq) == 0
        out: dict[str, Any] = {
            "ok": ok,
            "released": ok,
            "barriers": uniq,
            "head": head2 or head,
            "seal_root": health.get("seal_root"),
            "note": "fail-closed release — abstain when barriers non-empty (GPM-shaped)",
        }
        if issue_receipt and ok:
            if not actor:
                raise SchemaError("issue_receipt requires actor")
            ts = require_ts(now or self._now)
            receipt = issue_decision_receipt(
                self.store.root,
                kind="release",
                head=out["head"],
                barriers=uniq,
                released=True,
                actor=actor,
                ts=ts,
                claim_ids=list(claim_ids or []),
                policy_version=policy_version,
                query_hash=query_hash,
                seal_root=out.get("seal_root"),
            )
            out["receipt"] = receipt
        elif issue_receipt and record_abstain and not ok:
            if not actor:
                raise SchemaError("issue_receipt requires actor")
            ts = require_ts(now or self._now)
            receipt = issue_decision_receipt(
                self.store.root,
                kind="abstain",
                head=out["head"],
                barriers=uniq,
                released=False,
                actor=actor,
                ts=ts,
                claim_ids=list(claim_ids or []),
                policy_version=policy_version,
                query_hash=query_hash,
                seal_root=out.get("seal_root"),
            )
            out["receipt"] = receipt
        return out

    def verify_import(
        self,
        pack_dir: str | Path,
        *,
        expected_seal: Mapping[str, Any] | None = None,
        expected_policy_digest: str | None = None,
    ) -> dict[str, Any]:
        """PAM-shaped fail-closed import verify (no store write)."""
        return verify_import(
            Path(pack_dir),
            expected_seal=dict(expected_seal) if expected_seal else None,
            expected_policy_digest=expected_policy_digest,
        )

    def list_decision_receipts(self, *, limit: int = 50) -> list[dict[str, Any]]:
        """Newest-first local decision receipts."""
        return list_decision_receipts(self.store.root, limit=limit)

    def verify_decision_receipt(
        self,
        receipt: Mapping[str, Any],
        *,
        require_current_head: bool = False,
    ) -> dict[str, Any]:
        """Recompute receipt digest; optionally require live journal head match."""
        live_head = None
        if require_current_head:
            live_head = self.journal_chain_head().get("head")
        return verify_decision_receipt(
            self.store.root,
            dict(receipt),
            require_current_head=require_current_head,
            live_head=live_head,
        )

    def lineage_trust(self, entry_id: str, *, max_depth: int = 3) -> dict[str, Any]:
        """MemLineage-shaped trust label for one entry."""
        return graph_lineage_trust(
            list(self.store.iter_entries()), entry_id, max_depth=max_depth
        )

    def record_execution(
        self,
        step: str,
        *,
        subject_id: str,
        actor: str,
        ts: str | None = None,
        detail: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """PoEM-shaped proof-of-execution append (independent of memory bodies)."""
        ts = require_ts(ts or self._now)
        return exec_record_execution(
            self.store.root,
            step=step,
            subject_id=subject_id,
            actor=actor,
            ts=ts,
            detail=detail,
        )

    def verify_execution(
        self, step: str, *, subject_id: str
    ) -> dict[str, Any]:
        """Allow safety-step skip only if execution ledger confirms it ran."""
        return exec_verify_execution_claim(
            self.store.root, step=step, subject_id=subject_id
        )

    def verify_execution_chain(self) -> dict[str, Any]:
        """Verify PoEM-shaped execution ledger hash chain."""
        return exec_verify_execution_chain(self.store.root)

    def list_executions(
        self, *, subject_id: str | None = None, limit: int = 50
    ) -> list[dict[str, Any]]:
        """List recent execution ledger rows."""
        return exec_list_executions(
            self.store.root, subject_id=subject_id, limit=limit
        )

    def authority_gate(
        self,
        entry_ids: Sequence[str],
        *,
        action_risk: str,
    ) -> dict[str, Any]:
        """PPMF-shaped non-amplification: risk vs provenance authority."""
        return exec_authority_gate(
            list(self.store.iter_entries()),
            list(entry_ids),
            action_risk=action_risk,
        )

    def claim_closure(
        self,
        claim_ids: Sequence[str],
        *,
        expected_head: str | None = None,
        require_claim_role: bool = False,
    ) -> dict[str, Any]:
        """GPM-shaped exact claim closure over promoted facts at journal head."""
        head = self.journal_chain_head().get("head")
        result = exec_claim_closure(
            list(self.store.iter_entries()),
            list(claim_ids),
            journal_head=head,
            expected_head=expected_head,
        )
        if require_claim_role and result.get("closed"):
            iface = project_fact_interface(
                list(self.store.iter_entries()), entry_ids=list(claim_ids)
            )
            evidence_only = [
                e["id"]
                for e in iface.get("evidence") or []
                if e["id"] in set(claim_ids)
            ]
            if evidence_only:
                result = dict(result)
                result["ok"] = False
                result["closed"] = False
                result["barriers"] = list(result.get("barriers") or []) + [
                    f"evidence_role_not_authorizing:{i}" for i in evidence_only
                ]
                result["note"] = (
                    "claim closure refused evidence-role IDs (MemIR-shaped)"
                )
        return result

    def cascade_impact(self, fault_id: str, *, max_depth: int = 5) -> dict[str, Any]:
        """MemoRepair-shaped cascade descendants of a fault entry."""
        try:
            return repair_cascade_descendants(
                list(self.store.iter_entries()), fault_id, max_depth=max_depth
            )
        except KeyError as exc:
            raise SchemaError(f"unknown entry: {fault_id}") from exc

    def cascade_exposure(self, fault_id: str, *, max_depth: int = 5) -> dict[str, Any]:
        """Promoted descendants still in service (invalidated exposure metric)."""
        try:
            return repair_cascade_exposure(
                list(self.store.iter_entries()), fault_id, max_depth=max_depth
            )
        except KeyError as exc:
            raise SchemaError(f"unknown entry: {fault_id}") from exc

    def withdraw_cascade(
        self,
        fault_id: str,
        *,
        evidence: Sequence[Mapping[str, Any]],
        actor: str,
        ts: str | None = None,
        max_depth: int = 5,
        include_fault: bool = True,
    ) -> dict[str, Any]:
        """
        Barrier-first cascade withdraw (MemoRepair-shaped).

        Revokes fault (optional) + all depends-on descendants before any repair.
        History retained on disk — not DELETE.
        """
        ts = require_ts(ts or self._now)
        if not evidence:
            raise SchemaError("withdraw_cascade requires external evidence")
        validated_ev = [validate_evidence(x) for x in evidence]
        impact = self.cascade_impact(fault_id, max_depth=max_depth)
        targets = list(impact["ids"])
        if include_fault:
            targets = [fault_id] + targets
        # Deduplicate preserve order
        seen: set[str] = set()
        ordered: list[str] = []
        for tid in targets:
            if tid not in seen:
                seen.add(tid)
                ordered.append(tid)
        withdrawn: list[str] = []
        with self.store:
            for tid in ordered:
                e = self.store.read_entry(tid)
                if e is None:
                    continue
                if e.get("state") == "revoked":
                    withdrawn.append(tid)
                    continue
                e["state"] = "revoked"
                e["temporal"] = dict(e.get("temporal") or {})
                e["temporal"]["revoked_at"] = ts
                e["temporal"]["withdraw_reason"] = "cascade_barrier"
                e["temporal"]["cascade_fault"] = fault_id
                e["evidence"] = list(e.get("evidence") or []) + validated_ev
                self.store.write_entry(e, actor=actor, ts=ts, op="WITHDRAW")
                withdrawn.append(tid)
        self.retriever.rebuild(lexical_only=True)
        return {
            "fault_id": fault_id,
            "withdrawn": withdrawn,
            "count": len(withdrawn),
            "exposure_after": self.cascade_exposure(fault_id, max_depth=max_depth),
            "note": "barrier-first withdraw — repair_plan next; not exhaustive auto-repair",
        }

    def repair_plan(
        self,
        fault_id: str,
        *,
        lambda_cost: float = 0.5,
        max_depth: int = 5,
        budget: int | None = None,
    ) -> dict[str, Any]:
        """MemoRepair-shaped predecessor-closed repair selection (report-only)."""
        try:
            return repair_repair_plan(
                list(self.store.iter_entries()),
                fault_id,
                lambda_cost=lambda_cost,
                max_depth=max_depth,
                budget=budget,
            )
        except KeyError as exc:
            raise SchemaError(f"unknown entry: {fault_id}") from exc

    def repair_select_mincut(
        self,
        fault_id: str,
        *,
        lambda_cost: float = 0.5,
        max_depth: int = 5,
    ) -> dict[str, Any]:
        """Exact MemoRepair-shaped s–t min-cut repair selection (report-only)."""
        try:
            return repair_repair_select_mincut(
                list(self.store.iter_entries()),
                fault_id,
                lambda_cost=lambda_cost,
                max_depth=max_depth,
            )
        except KeyError as exc:
            raise SchemaError(f"unknown entry: {fault_id}") from exc

    def adjudicate_update(
        self,
        candidate: Mapping[str, Any],
        *,
        evidence: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """CUPMem-shaped write-side adjudication (does not write)."""
        return cupmem_adjudicate_update(
            list(self.store.iter_entries()), candidate, evidence=evidence
        )

    def unknown_current_slots(self) -> dict[str, Any]:
        """CUPMem unknown-current / unsafe assertability slots."""
        return cupmem_unknown_current_slots(list(self.store.iter_entries()))

    def authorize_retrieval(
        self,
        hit_ids: Sequence[str] | None = None,
        *,
        query: str = "",
        consumer_scope: str | None = None,
    ) -> dict[str, Any]:
        """CUPMem authorize retrieval — filter to settled promoted slots."""
        if hit_ids is None:
            if not consumer_scope:
                raise SchemaError(
                    "authorize_retrieval needs hit_ids or consumer_scope"
                )
            hits = self.search(
                query or "a", consumer_scope=consumer_scope, budget=2000
            )
            hit_ids = [str(h.get("id")) for h in hits]
        return cupmem_authorize_retrieval(
            list(self.store.iter_entries()), list(hit_ids)
        )

    def admit_gate(
        self,
        *,
        action: str,
        actor: str,
        authority_bundle: Mapping[str, Any] | None = None,
        entry_id: str | None = None,
        ts: str | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        """CMGL-shaped fail-closed procedural admit before protected writes."""
        ts = require_ts(ts or self._now)
        return cmgl_admit_gate(
            self.store.root,
            action=action,
            actor=actor,
            ts=ts,
            authority_bundle=authority_bundle,
            entry_id=entry_id,
            note=note,
        )

    def list_admit_receipts(self, *, limit: int = 50) -> dict[str, Any]:
        return cmgl_list_admit_receipts(self.store.root, limit=limit)

    def verify_admit_receipt(
        self, receipt: Mapping[str, Any]
    ) -> dict[str, Any]:
        return cmgl_verify_admit_receipt(receipt)

    def put_raw_page(
        self,
        text: str,
        *,
        actor: str,
        ts: str | None = None,
        meta: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """TierMem Tier-2 immutable raw page (content-addressed)."""
        ts = require_ts(ts or self._now)
        return tiermem_put_raw_page(
            self.store.root, text, actor=actor, ts=ts, meta=meta
        )

    def sufficiency_gate(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
    ) -> dict[str, Any]:
        """TierMem sufficiency check over summary-first Select hits."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        # Enrich hits with full entry bodies/links for router
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            if e:
                enriched.append(e)
            else:
                enriched.append(dict(h))
        gate = tiermem_sufficiency_gate(query, enriched)
        gate["hits"] = [str(h.get("id")) for h in hits]
        return gate

    def escalate_raw(
        self,
        summary_ids: Sequence[str],
        *,
        max_pages: int = 8,
    ) -> dict[str, Any]:
        """TierMem escalate to linked Tier-2 raw pages."""
        return tiermem_escalate(
            self.store.root,
            list(self.store.iter_entries()),
            summary_ids,
            max_pages=max_pages,
        )

    def verified_writeback(
        self,
        *,
        title: str,
        body: str,
        scope: str,
        raw_digests: Sequence[str],
        actor: str,
        ts: str | None = None,
        conflict_key: str | None = None,
        promote: bool = False,
        evidence: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """
        TierMem verified write-back: ADD summary linked to raw digests.

        Optionally promote when evidence provided.
        """
        ts = require_ts(ts or self._now)
        digests = [str(d) for d in raw_digests if d]
        if not digests:
            raise SchemaError("verified_writeback requires raw_digests")
        for d in digests:
            if tiermem_get_raw_page(self.store.root, d) is None:
                att = self.store.root / "attachments" / d
                if not att.is_file():
                    raise SchemaError(f"unknown raw digest: {d}")
        draft = tiermem_summary_entry_template(
            title=title,
            body=body,
            scope=scope,
            raw_digests=digests,
            provenance={
                "agent": "tiermem_writer",
                "task": "tiermem_writeback",
                "environment": "local",
                "subject_id": "writeback",
                "source": "tiermem:writeback",
                "written_at": ts,
            },
            temporal={"valid_from": ts, "last_verified": ts},
            conflict_key=conflict_key,
        )
        added = self.add(draft, actor=actor, ts=ts)
        out: dict[str, Any] = {
            "id": added["id"],
            "state": added["state"],
            "raw_digests": digests,
            "note": "TierMem verified write-back — summary linked to raw",
        }
        if promote:
            if not evidence:
                raise SchemaError("promote=True requires evidence")
            # Separate oracle actor from entry writer (C7).
            self.promote(added["id"], evidence, actor=actor, ts=ts)
            out["state"] = "promoted"
        return out

    def skill_eligibility(self, entry_id: str) -> dict[str, Any]:
        """MSCE skill eligibility for one entry."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return msce_skill_eligibility(entry)

    def crystallize_skill(
        self,
        source_ids: Sequence[str],
        *,
        title: str | None = None,
        scope: str | None = None,
        env_assumptions: Sequence[str] | None = None,
        actor: str | None = None,
        ts: str | None = None,
        write: bool = False,
    ) -> dict[str, Any]:
        """MSCE crystallize skill draft; optionally ADD as quarantined skill_artifact."""
        result = msce_crystallize_skill(
            list(self.store.iter_entries()),
            source_ids,
            title=title,
            scope=scope,
            env_assumptions=env_assumptions,
        )
        if not write or not result.get("ok"):
            return result
        ts = require_ts(ts or self._now)
        draft = dict(result["draft"])
        act = actor or str((draft.get("provenance") or {}).get("agent") or "msce")
        added = self.add(draft, actor=act, ts=ts)
        result["id"] = added["id"]
        result["state"] = added["state"]
        result["written"] = True
        return result

    def value_backfill(
        self,
        entry_id: str,
        *,
        terminal_success: bool,
        reflection_weight: float = 1.0,
        apply: bool = False,
        actor: str | None = None,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """MSCE reflection-weighted usage backfill plan; optionally apply."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        plan = msce_value_backfill(
            entry,
            terminal_success=terminal_success,
            reflection_weight=reflection_weight,
        )
        if not apply:
            return plan
        ts = require_ts(ts or self._now)
        act = actor or "msce"
        with self.store:
            e = self.store.read_entry(entry_id)
            if e is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            from stele_core.schema import normalize_usage

            e["usage"] = normalize_usage(plan["usage_after"])
            self.store.write_entry(e, actor=act, ts=ts, op="USAGE_BACKFILL")
        plan["applied"] = True
        return plan

    def skill_catalog(
        self, *, states: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """MSCE skill catalog over skill_artifact entries."""
        return msce_skill_catalog(
            list(self.store.iter_entries()), states=states
        )

    def fade_strength(self, entry_id: str, *, now: str | None = None) -> dict[str, Any]:
        """FadeMem dual-layer strength for one entry."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        ts = require_ts(now or self._now)
        return fade_fade_strength(entry, now=ts)

    def fade_scan(
        self,
        *,
        now: str | None = None,
        threshold: float = 0.15,
        limit: int = 50,
    ) -> dict[str, Any]:
        """FadeMem fade candidates below threshold (report only)."""
        ts = require_ts(now or self._now)
        return fade_fade_scan(
            list(self.store.iter_entries()),
            now=ts,
            threshold=threshold,
            limit=limit,
        )

    def fusion_candidates(
        self, *, min_overlap: float = 0.45, limit: int = 20
    ) -> dict[str, Any]:
        """FadeMem deterministic fusion-candidate pairs."""
        return fade_fusion_candidates(
            list(self.store.iter_entries()),
            min_overlap=min_overlap,
            limit=limit,
        )

    def weibull_relevance(
        self,
        entry_id: str,
        *,
        now: str | None = None,
        eta_days: float = 30.0,
        kappa: float = 1.0,
    ) -> dict[str, Any]:
        """SSGM Weibull relevance for one entry."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        ts = require_ts(now or self._now)
        score = fade_weibull_relevance(
            entry, now=ts, eta_days=eta_days, kappa=kappa
        )
        return {
            "id": entry_id,
            "weibull_relevance": score,
            "eta_days": eta_days,
            "kappa": kappa,
            "note": "SSGM Weibull relevance proxy",
        }

    def evidence_gap(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
    ) -> dict[str, Any]:
        """MemR3 evidence-gap over Select hits."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return memr3_evidence_gap(query, enriched)

    def reflective_retrieve(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        coverage_target: float = 0.85,
    ) -> dict[str, Any]:
        """MemR3 reflective retrieve plan (gap + next probes)."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return memr3_reflective_retrieve_plan(
            query, enriched, coverage_target=coverage_target
        )

    def gap_tracker_update(
        self,
        prior_gaps: Sequence[Mapping[str, Any]],
        *,
        query: str,
        consumer_scope: str,
        budget: int = 400,
    ) -> dict[str, Any]:
        """Update MemR3 gap tracker after a follow-up Select."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return memr3_gap_tracker_update(prior_gaps, enriched)

    def archive_plan(
        self,
        *,
        now: str | None = None,
        min_age_days: float = 14.0,
        max_fade_strength: float = 0.35,
        mw_ceiling: float = 0.45,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Utility-weighted archive candidates (report only)."""
        ts = require_ts(now or self._now)
        return arch_archive_plan(
            list(self.store.iter_entries()),
            now=ts,
            min_age_days=min_age_days,
            max_fade_strength=max_fade_strength,
            mw_ceiling=mw_ceiling,
            limit=limit,
        )

    def archive_apply(
        self,
        entry_ids: Sequence[str],
        *,
        actor: str,
        ts: str | None = None,
        require_eligible: bool = True,
        min_age_days: float = 14.0,
    ) -> dict[str, Any]:
        """Move promoted entries to archived (out of Select). Reversible."""
        act = str(actor or "").strip()
        if not act:
            raise SchemaError("actor is required")
        now = require_ts(ts or self._now)
        archived: list[str] = []
        skipped: list[dict[str, Any]] = []
        with self.store:
            for eid in entry_ids:
                entry = self.store.read_entry(str(eid))
                if entry is None:
                    skipped.append({"id": eid, "reason": "unknown"})
                    continue
                if require_eligible:
                    from stele_core.archive import archive_eligible

                    gate = archive_eligible(
                        entry, now=now, min_age_days=min_age_days
                    )
                    if not gate.get("eligible"):
                        skipped.append(
                            {
                                "id": eid,
                                "reason": "not_eligible",
                                "details": gate.get("reasons"),
                            }
                        )
                        continue
                if entry.get("state") != "promoted":
                    skipped.append({"id": eid, "reason": "not_promoted"})
                    continue
                entry["state"] = "archived"
                self.store.write_entry(entry, actor=act, ts=now, op="ARCHIVE")
                archived.append(str(eid))
        if archived:
            self.retriever.rebuild(lexical_only=True)
        return {
            "archived": archived,
            "count": len(archived),
            "skipped": skipped,
            "ok": True,
            "note": "Archived out of Select — use unarchive to restore",
        }

    def unarchive(
        self,
        entry_id: str,
        *,
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """Restore archived → promoted."""
        act = str(actor or "").strip()
        if not act:
            raise SchemaError("actor is required")
        now = require_ts(ts or self._now)
        with self.store:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise SchemaError(f"unknown entry: {entry_id}")
            if entry.get("state") != "archived":
                raise SchemaError(
                    f"only archived entries can unarchive, got {entry.get('state')}"
                )
            entry["state"] = "promoted"
            self.store.write_entry(entry, actor=act, ts=now, op="UNARCHIVE")
        self.retriever.rebuild(lexical_only=True)
        return {"id": entry_id, "state": "promoted", "ok": True}

    def list_archived(self) -> dict[str, Any]:
        """List archived entries."""
        return arch_list_archived(list(self.store.iter_entries()))

    def composite_importance(
        self,
        entry_id: str,
        *,
        now: str | None = None,
    ) -> dict[str, Any]:
        """SF-AMS CIS for one entry."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        ts = require_ts(now or self._now)
        return sfams_composite_importance(entry, now=ts)

    def cis_scan(
        self,
        *,
        now: str | None = None,
        tiers: Sequence[str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """SF-AMS CIS ranking scan."""
        ts = require_ts(now or self._now)
        return sfams_cis_scan(
            list(self.store.iter_entries()), now=ts, tiers=tiers, limit=limit
        )

    def control_suggest(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        now: str | None = None,
    ) -> dict[str, Any]:
        """MemCon-shaped control action suggestion."""
        ts = require_ts(now or self._now)
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return memcon_control_suggest(
            query=query,
            hits=enriched,
            entries=list(self.store.iter_entries()),
            now=ts,
        )

    def value_tag(
        self,
        entry_id: str,
        *,
        now: str | None = None,
        task_query: str = "",
    ) -> dict[str, Any]:
        """SCM 4D value tag for one entry."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        ts = require_ts(now or self._now)
        return scm_value_tag(
            entry,
            now=ts,
            peer_entries=list(self.store.iter_entries()),
            task_query=task_query,
        )

    def wm_push(
        self, entry_id: str, *, capacity: int | None = None, note: str = ""
    ) -> dict[str, Any]:
        """Push id into SCM working-memory ring."""
        if self.store.read_entry(entry_id) is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return scm_wm_push(
            self.store.root, entry_id, capacity=capacity, note=note
        )

    def wm_list(self) -> dict[str, Any]:
        """List SCM working-memory overlay."""
        return scm_wm_list(self.store.root)

    def wm_clear(self) -> dict[str, Any]:
        """Clear SCM working-memory overlay."""
        return scm_wm_clear(self.store.root)

    def sleep_trigger(
        self,
        *,
        now: str | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """SCM sleep trigger from WM entropy / conflict density."""
        ts = require_ts(now or self._now)
        wm = scm_wm_list(self.store.root)
        return scm_sleep_trigger(
            list(self.store.iter_entries()),
            now=ts,
            wm_ids=wm.get("ids") or [],
            force=force,
        )

    def sleep_plan(self, *, now: str | None = None) -> dict[str, Any]:
        """SCM NREM/REM/FORGET sleep cycle plan (report only)."""
        ts = require_ts(now or self._now)
        wm = scm_wm_list(self.store.root)
        return scm_sleep_cycle_plan(
            list(self.store.iter_entries()),
            now=ts,
            wm_ids=wm.get("ids") or [],
        )

    def sleep_apply_nrem(
        self,
        *,
        actor: str,
        now: str | None = None,
    ) -> dict[str, Any]:
        """Apply NREM reinforce actions from sleep plan (usage helpful++)."""
        act = str(actor or "").strip()
        if not act:
            raise SchemaError("actor is required")
        ts = require_ts(now or self._now)
        plan = self.sleep_plan(now=ts)
        reinforced: list[str] = []
        with self.store:
            for row in plan.get("nrem") or []:
                if row.get("action") != "reinforce":
                    continue
                eid = str(row.get("id") or "")
                entry = self.store.read_entry(eid)
                if entry is None or entry.get("state") not in {
                    "promoted",
                    "contested",
                }:
                    continue
                from stele_core.schema import normalize_usage

                usage = normalize_usage(entry.get("usage"))
                usage["helpful"] = int(usage.get("helpful") or 0) + 1
                usage["last_outcome"] = "helpful"
                usage["last_outcome_at"] = ts
                entry["usage"] = usage
                self.store.write_entry(entry, actor=act, ts=ts, op="NREM_REINFORCE")
                reinforced.append(eid)
        return {
            "reinforced": reinforced,
            "count": len(reinforced),
            "ok": True,
            "note": "SCM NREM apply — reinforce only; no auto-archive/link",
        }

    def episodic_buffer(self, *, limit: int = 20) -> dict[str, Any]:
        """GAM episodic buffer (quarantined)."""
        return gam_episodic_buffer(
            list(self.store.iter_entries()), limit=limit
        )

    def semantic_boundary(
        self, previous: str, current: str, *, threshold: float = 0.35
    ) -> dict[str, Any]:
        """GAM topic-shift detector."""
        return gam_semantic_boundary(
            previous, current, threshold=threshold
        )

    def consolidate_plan(
        self, *, min_overlap: float = 0.25, limit: int = 20
    ) -> dict[str, Any]:
        """GAM consolidate candidates from quarantine → promoted topics."""
        entries = list(self.store.iter_entries())
        buf = [e for e in entries if e.get("state") == "quarantined"]
        promoted = [e for e in entries if e.get("state") == "promoted"]
        return gam_consolidate_candidates(
            buf, promoted, min_overlap=min_overlap, limit=limit
        )

    def anticipate(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        limit: int = 10,
    ) -> dict[str, Any]:
        """ACM anticipate prefetch from hit neighborhood."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return acm_anticipate_prefetch(
            query,
            enriched,
            list(self.store.iter_entries()),
            limit=limit,
        )

    def verify_compaction(
        self,
        query: str,
        compacted_text: str,
        *,
        consumer_scope: str,
        budget: int = 400,
    ) -> dict[str, Any]:
        """ACM verifiable compaction check against Select hits."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return acm_verify_compaction(query, enriched, compacted_text)

    def sensory_filter(
        self, text: str, *, keep_ratio: float = 1.0
    ) -> dict[str, Any]:
        """LightMem sensory pre-compression."""
        return light_sensory_filter(text, keep_ratio=keep_ratio)

    def stage_inventory(self, *, now: str | None = None) -> dict[str, Any]:
        """LightMem sensory/stm/ltm inventory."""
        ts = require_ts(now or self._now)
        wm = scm_wm_list(self.store.root)
        return light_stage_inventory(
            list(self.store.iter_entries()),
            now=ts,
            wm_ids=wm.get("ids") or [],
        )

    def topic_segments(
        self, texts: Sequence[str], *, threshold: float = 0.35
    ) -> dict[str, Any]:
        """LightMem topic segmentation."""
        return light_topic_segments(texts, threshold=threshold)

    def stage_budget_plan(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        now: str | None = None,
    ) -> dict[str, Any]:
        """LightMem stage-aware budget allocation over Select hits."""
        ts = require_ts(now or self._now)
        wm = scm_wm_list(self.store.root)
        wm_ids = wm.get("ids") or []
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget * 2)
        by_stage: dict[str, list[dict[str, Any]]] = {
            "sensory": [],
            "stm": [],
            "ltm": [],
        }
        for h in hits:
            e = self.store.read_entry(str(h.get("id"))) or dict(h)
            stage = light_assign_stage(e, now=ts, wm_ids=wm_ids)
            row = dict(e)
            row["stage"] = stage
            by_stage.setdefault(stage, []).append(row)
        return light_stage_budget_plan(query, by_stage, budget=budget)

    def ppr_scores(
        self,
        seed_ids: Sequence[str],
        *,
        damping: float = 0.85,
        iterations: int = 20,
    ) -> dict[str, Any]:
        """HippoRAG-shaped Personalized PageRank."""
        return hippo_ppr_scores(
            list(self.store.iter_entries()),
            seed_ids,
            damping=damping,
            iterations=iterations,
        )

    def multi_hop_retrieve(
        self,
        query: str,
        *,
        seed_limit: int = 5,
        result_limit: int = 10,
    ) -> dict[str, Any]:
        """HippoRAG multi-hop retrieve (lexical seed + PPR)."""
        return hippo_multi_hop_retrieve(
            query,
            list(self.store.iter_entries()),
            seed_limit=seed_limit,
            result_limit=result_limit,
        )

    def write_gate(self, pending: Mapping[str, Any]) -> dict[str, Any]:
        """Quipu-shaped write gate on pending post-state (does not write)."""
        return map_write_gate(pending, list(self.store.iter_entries()))

    def action_risk_gate(
        self,
        supporting_ids: Sequence[str],
        *,
        risk: str = "medium",
        trusted_sources: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """MAP-Graph risk-sensitive action gate."""
        return map_action_risk_gate(
            list(self.store.iter_entries()),
            supporting_ids,
            risk=risk,
            trusted_sources=trusted_sources,
        )

    def extract_residuals(self, entry_id: str) -> dict[str, Any]:
        """ProGraph compression residuals for one entry."""
        e = self.store.read_entry(str(entry_id))
        if e is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return pg_extract_residuals(e)

    def register_entities(self) -> dict[str, Any]:
        """ProGraph entity registry over the store."""
        return pg_register_entities(list(self.store.iter_entries()))

    def profile_expand(
        self,
        query: str,
        *,
        expand_threshold: float = 0.2,
        seed_limit: int = 5,
        expand_limit: int = 10,
    ) -> dict[str, Any]:
        """ProGraph profile expansion (entity traversal)."""
        return pg_profile_expand(
            query,
            list(self.store.iter_entries()),
            expand_threshold=expand_threshold,
            seed_limit=seed_limit,
            expand_limit=expand_limit,
        )

    def residual_augment(
        self,
        query: str,
        entry_ids: Sequence[str],
        *,
        limit_per_entry: int = 5,
    ) -> dict[str, Any]:
        """Attach query-relevant residuals to selected entries."""
        return pg_residual_augment(
            query,
            entry_ids,
            list(self.store.iter_entries()),
            limit_per_entry=limit_per_entry,
        )

    def match_correction(
        self,
        *,
        failure_id: str | None = None,
        min_overlap: float = 0.15,
        limit: int = 10,
    ) -> dict[str, Any]:
        """EMG match failure lessons to successful workflows/skills."""
        return emg_match_correction(
            list(self.store.iter_entries()),
            failure_id=failure_id,
            min_overlap=min_overlap,
            limit=limit,
        )

    def insight_inject(self, correction: Mapping[str, Any]) -> dict[str, Any]:
        """EMG format a loop-free correction insight (does not write)."""
        return emg_insight_inject(correction)

    def cascade_route(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        margin_threshold: float = 0.25,
    ) -> dict[str, Any]:
        """AgentIR cascade routing decision from lexical margin."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return air_cascade_route(
            query, enriched, margin_threshold=margin_threshold
        )

    def multi_channel_fuse(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        k: int = 60,
        result_limit: int = 10,
        force_full: bool = False,
    ) -> dict[str, Any]:
        """AgentIR multi-channel RRF (lexical ± PPR ± residual)."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return air_multi_channel_fuse(
            query,
            list(self.store.iter_entries()),
            enriched,
            k=k,
            result_limit=result_limit,
            force_full=force_full,
        )

    def dual_project(self, entry_id: str) -> dict[str, Any]:
        """Governed Memory dual fact/property projection."""
        e = self.store.read_entry(str(entry_id))
        if e is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return gm_dual_project(e)

    def governance_route(
        self,
        task: str,
        *,
        limit: int = 7,
        critical_threshold: float = 0.35,
    ) -> dict[str, Any]:
        """Governed Memory fast governance routing."""
        return gm_governance_route(
            task,
            list(self.store.iter_entries()),
            limit=limit,
            critical_threshold=critical_threshold,
        )

    def session_delta_open(
        self, session_id: str, *, ttl_hours: float = 24.0
    ) -> dict[str, Any]:
        """Open progressive-delivery session state."""
        return gm_session_delta_open(
            self.store.root, session_id, ttl_hours=ttl_hours
        )

    def session_delta_deliver(
        self, session_id: str, route: Mapping[str, Any]
    ) -> dict[str, Any]:
        """Deliver only delta governance context for a session."""
        return gm_session_delta_deliver(self.store.root, session_id, route)

    def session_delta_status(self, session_id: str) -> dict[str, Any]:
        """Inspect progressive-delivery session state."""
        return gm_session_delta_status(self.store.root, session_id)

    def entity_context(
        self,
        subject_id: str,
        *,
        budget: int = 400,
        saturation: int = 7,
    ) -> dict[str, Any]:
        """Compile entity Properties + Observations under budget."""
        return gm_entity_context(
            list(self.store.iter_entries()),
            subject_id=subject_id,
            budget=budget,
            saturation=saturation,
        )

    def entity_leak_probe(
        self,
        subject_id: str,
        *,
        query: str = "",
        consumer_scope: str,
        budget: int = 400,
        prefilter: bool = True,
    ) -> dict[str, Any]:
        """Probe Select hits for cross-entity subject leakage."""
        hits = self.search(
            query or "a", consumer_scope=consumer_scope, budget=budget
        )
        return gm_entity_leak_probe(
            hits,
            subject_id=subject_id,
            entries=list(self.store.iter_entries()),
            prefilter=prefilter,
        )

    def hymem_classify_slot(self, text: str) -> dict[str, Any]:
        """HyMem typed context slot classification."""
        return hy_classify_slot(text)

    def hymem_isolate_pack(
        self,
        items: Sequence[Mapping[str, Any]],
        *,
        planner_budget: int = 200,
    ) -> dict[str, Any]:
        """HyMem typed isolation planner pack."""
        return hy_isolate_pack(items, planner_budget=planner_budget)

    def extract_version_markers(self, entry_id: str) -> dict[str, Any]:
        """Extract serial/ISO version markers from one entry."""
        e = self.store.read_entry(str(entry_id))
        if e is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return fr_extract_version_markers(e)

    def freshness_resolve(
        self, *, conflict_key: str | None = None
    ) -> dict[str, Any]:
        """Deterministic max(serial|ts) among candidates."""
        return fr_freshness_resolve(
            list(self.store.iter_entries()), conflict_key=conflict_key
        )

    def assemble_current(
        self, query: str, *, limit: int = 10
    ) -> dict[str, Any]:
        """Candidate extract + per-conflict_key freshness resolve."""
        return fr_assemble_current(
            query, list(self.store.iter_entries()), limit=limit
        )

    def hop_freshness(
        self, hops: Sequence[str], *, limit_per_hop: int = 3
    ) -> dict[str, Any]:
        """Per-hop deterministic freshness assembly."""
        return fr_hop_freshness(
            hops, list(self.store.iter_entries()), limit_per_hop=limit_per_hop
        )

    def patch_test(
        self,
        pending: Mapping[str, Any],
        source_id: str,
        *,
        cited_span: str | None = None,
    ) -> dict[str, Any]:
        """MemTxn Ordered PatchTest against a source entry."""
        source = self.store.read_entry(str(source_id))
        if source is None:
            raise SchemaError(f"unknown source: {source_id}")
        return pt_patch_test(pending, source, cited_span=cited_span)

    def temporal_resolve(self, conflict_key: str) -> dict[str, Any]:
        """MemTxn Temporal Resolver for one conflict_key."""
        return pt_temporal_resolve(
            list(self.store.iter_entries()), conflict_key=conflict_key
        )

    def recover_active_map(
        self, conflict_keys: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """Recover one visible tip per conflict_key."""
        return pt_recover_active_map(
            list(self.store.iter_entries()), conflict_keys=conflict_keys
        )

    def fleet_scope_gate(
        self, entry_id: str, *, allowed_scopes: Sequence[str]
    ) -> dict[str, Any]:
        """Fleet/tenant scope allowlist gate."""
        e = self.store.read_entry(str(entry_id))
        if e is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return fp_fleet_scope_gate(e, allowed_scopes=allowed_scopes)

    def propagate_plan(
        self,
        *,
        source_scope: str,
        target_scopes: Sequence[str],
        query: str = "",
        limit: int = 10,
    ) -> dict[str, Any]:
        """Report-only cross-scope propagation plan."""
        return fp_propagate_plan(
            list(self.store.iter_entries()),
            source_scope=source_scope,
            target_scopes=target_scopes,
            query=query,
            limit=limit,
        )

    def stale_propagation_scan(self, *, limit: int = 50) -> dict[str, Any]:
        """Scan for stale promoted tips beside fresher conflict_key winners."""
        return fp_stale_propagation_scan(
            list(self.store.iter_entries()), limit=limit
        )

    def query_complexity(self, query: str) -> dict[str, Any]:
        """BudgetMem query complexity heuristic."""
        return bm_query_complexity(query)

    def budget_tier_route(self, query: str) -> dict[str, Any]:
        """BudgetMem per-module Low/Mid/High routing."""
        return bm_budget_tier_route(query)

    def budget_module_plan(
        self, query: str, *, global_budget: int = 10
    ) -> dict[str, Any]:
        """Fit BudgetMem tiers under a global cost budget."""
        return bm_budget_module_plan(query, global_budget=global_budget)

    def skill_rank(self, query: str, *, limit: int = 5) -> dict[str, Any]:
        """Lexical skill/workflow library ranker."""
        return sr_skill_rank(
            query, list(self.store.iter_entries()), limit=limit
        )

    def skill_prereq_expand(
        self, skill_id: str, *, depth: int = 2, limit: int = 10
    ) -> dict[str, Any]:
        """Expand skill prerequisites via entry LINKs."""
        return sr_skill_prereq_expand(
            skill_id,
            list(self.store.iter_entries()),
            depth=depth,
            limit=limit,
        )

    def list_retrieval_primitives(self) -> dict[str, Any]:
        """ERSkill retrieval primitive catalog."""
        return er_list_primitives()

    def list_retrieval_skills(self) -> dict[str, Any]:
        """ERSkill built-in retrieval skills."""
        return er_list_retrieval_skills()

    def compose_retrieval_skill(
        self, name: str, primitives: Sequence[str]
    ) -> dict[str, Any]:
        """Validate a custom retrieval skill composition."""
        return er_compose_retrieval_skill(name, primitives)

    def route_retrieval_skill(self, query: str) -> dict[str, Any]:
        """Cue-based retrieval skill router."""
        return er_route_retrieval_skill(query)

    def run_retrieval_skill(
        self,
        query: str,
        *,
        consumer_scope: str,
        skill: str | None = None,
        primitives: Sequence[str] | None = None,
        budget: int = 400,
    ) -> dict[str, Any]:
        """
        Execute a retrieval skill's primitive sequence (report-only orchestration).
        """
        if primitives is not None:
            composed = er_compose_retrieval_skill(
                skill or "custom", primitives
            )
            seq = list(composed["primitives"])
            skill_name = composed["name"]
        elif skill:
            if skill not in BUILTIN_SKILLS:
                raise SchemaError(f"unknown skill: {skill}")
            seq = list(BUILTIN_SKILLS[skill])
            skill_name = skill
        else:
            routed = er_route_retrieval_skill(query)
            seq = list(routed["primitives"])
            skill_name = str(routed["skill"])

        tiers = bm_budget_tier_route(query)["tiers"]
        params = bm_tier_params(tiers.get("candidate_pull", "mid"))
        steps: list[dict[str, Any]] = []
        hits: list[dict[str, Any]] = []
        entry_ids: list[str] = []

        for prim in seq:
            if prim == "lexical_search":
                hits = self.search(
                    query,
                    consumer_scope=consumer_scope,
                    budget=budget,
                    follow_links=False,
                    body_max_chars=params.get("body_max_chars"),
                )
                entry_ids = [str(h.get("id")) for h in hits if h.get("id")]
                steps.append(
                    {
                        "primitive": prim,
                        "count": len(hits),
                        "ids": entry_ids[: params.get("result_limit", 10)],
                    }
                )
            elif prim == "follow_links":
                hits = self.search(
                    query,
                    consumer_scope=consumer_scope,
                    budget=budget,
                    follow_links=True,
                    body_max_chars=params.get("body_max_chars"),
                )
                entry_ids = [str(h.get("id")) for h in hits if h.get("id")]
                steps.append(
                    {
                        "primitive": prim,
                        "count": len(hits),
                        "ids": entry_ids[: params.get("result_limit", 10)],
                    }
                )
            elif prim == "freshness_assemble":
                ac = self.assemble_current(
                    query, limit=int(params.get("result_limit") or 10)
                )
                entry_ids = [
                    str(r.get("id"))
                    for r in ac.get("resolved") or []
                    if r.get("id")
                ]
                steps.append(
                    {
                        "primitive": prim,
                        "count": ac.get("count"),
                        "ids": entry_ids,
                    }
                )
            elif prim == "multi_hop":
                mh = self.multi_hop_retrieve(
                    query,
                    seed_limit=int(params.get("seed_limit") or 5),
                    result_limit=int(params.get("result_limit") or 10),
                )
                entry_ids = [
                    str(h.get("id")) for h in mh.get("hits") or [] if h.get("id")
                ]
                steps.append(
                    {
                        "primitive": prim,
                        "count": mh.get("count"),
                        "ids": entry_ids,
                    }
                )
            elif prim == "residual_augment":
                if not entry_ids:
                    entry_ids = [
                        str(h.get("id")) for h in hits if h.get("id")
                    ][:5]
                ra = self.residual_augment(query, entry_ids[:5])
                steps.append(
                    {
                        "primitive": prim,
                        "count": ra.get("count"),
                        "packs": ra.get("packs"),
                    }
                )
            elif prim == "skill_rank":
                sr = self.skill_rank(
                    query, limit=int(params.get("result_limit") or 5)
                )
                entry_ids = [
                    str(h.get("id")) for h in sr.get("hits") or [] if h.get("id")
                ]
                steps.append(
                    {
                        "primitive": prim,
                        "count": sr.get("count"),
                        "ids": entry_ids,
                    }
                )
            else:
                raise SchemaError(f"unhandled primitive: {prim}")

        return {
            "query": query,
            "skill": skill_name,
            "primitives": seq,
            "tiers": tiers,
            "steps": steps,
            "final_ids": entry_ids[: int(params.get("result_limit") or 10)],
            "count": len(entry_ids),
            "ok": True,
            "note": "run_retrieval_skill — orchestrates existing Stele ops; not ERSkill paper scores",
        }

    def support_score(
        self,
        pending: Mapping[str, Any],
        *,
        context: str = "",
    ) -> dict[str, Any]:
        """ConsistencyGate lexical support score for a candidate."""
        return cg_support_score(
            pending,
            context=context,
            store_entries=list(self.store.iter_entries()),
        )

    def consistency_admit(
        self,
        pending: Mapping[str, Any],
        *,
        context: str = "",
        tau: float = 0.35,
    ) -> dict[str, Any]:
        """ConsistencyGate write-time admit/quarantine/reject."""
        return cg_consistency_admit(
            pending,
            context=context,
            store_entries=list(self.store.iter_entries()),
            tau=tau,
        )

    def retrieval_admit(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        min_overlap: float = 0.15,
    ) -> dict[str, Any]:
        """MemGate query-conditioned admission over Select hits."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return mg_retrieval_admit(
            query, enriched, min_overlap=min_overlap
        )

    def task_conditioned_pack(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        min_overlap: float = 0.15,
    ) -> dict[str, Any]:
        """MemGate admit + pack under token budget."""
        hits = self.search(
            query, consumer_scope=consumer_scope, budget=budget * 2
        )
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return mg_task_conditioned_pack(
            query,
            enriched,
            budget=budget,
            min_overlap=min_overlap,
        )

    def sovereignty_checklist(self) -> dict[str, Any]:
        """Mnemonic sovereignty nine-primitive coverage checklist."""
        return mn_sovereignty_checklist()

    def post_delete_verify(
        self,
        deleted_ids: Sequence[str],
        *,
        consumer_scope: str | None = None,
        probe_query: str = "",
    ) -> dict[str, Any]:
        """Verify deleted IDs absent from store and optional Select."""
        hits = None
        if consumer_scope is not None:
            hits = self.search(
                probe_query or "a",
                consumer_scope=consumer_scope,
                budget=2000,
            )
        return mn_post_delete_verify(
            list(self.store.iter_entries()),
            deleted_ids=deleted_ids,
            search_hits=hits,
        )

    def rollback_plan(
        self,
        target_ids: Sequence[str],
        *,
        reason: str = "operator_rollback",
    ) -> dict[str, Any]:
        """Report-only rollback plan for target entry IDs."""
        return mn_rollback_plan(
            list(self.store.iter_entries()),
            target_ids=target_ids,
            reason=reason,
        )

    def density_fuse(
        self,
        tunnels: Sequence[Mapping[str, Any]],
        *,
        limit: int = 10,
    ) -> dict[str, Any]:
        """SodaMem multi-tunnel density fusion."""
        return soda_density_fuse(tunnels, limit=limit)

    def evidence_plan(
        self,
        query: str,
        *,
        limit: int = 8,
    ) -> dict[str, Any]:
        """SodaMem planner: gather evidence IDs then fuse."""
        return soda_evidence_plan(
            query, list(self.store.iter_entries()), limit=limit
        )

    def cited_pack(
        self,
        query: str,
        evidence_ids: Sequence[str],
        *,
        budget: int = 400,
    ) -> dict[str, Any]:
        """SodaMem reader pack with mandatory citations."""
        return soda_cited_pack(
            query,
            evidence_ids,
            list(self.store.iter_entries()),
            budget=budget,
        )

    def compress_candidates(
        self,
        *,
        min_similarity: float = 0.45,
        limit: int = 40,
    ) -> dict[str, Any]:
        """MemRefine near-duplicate pair proposals."""
        return mr_compress_candidates(
            list(self.store.iter_entries()),
            min_similarity=min_similarity,
            limit=limit,
        )

    def refine_plan(
        self,
        *,
        target_count: int,
        min_similarity: float = 0.45,
    ) -> dict[str, Any]:
        """MemRefine storage-budget compression plan (report-only)."""
        return mr_refine_plan(
            list(self.store.iter_entries()),
            target_count=target_count,
            min_similarity=min_similarity,
        )

    def merge_link_add(
        self,
        new_entry: Mapping[str, Any],
        *,
        merge_threshold: float = 0.75,
        link_threshold: float = 0.45,
    ) -> dict[str, Any]:
        """AriadneMem merge | link | add decision."""
        return ar_merge_link_add(
            new_entry,
            list(self.store.iter_entries()),
            merge_threshold=merge_threshold,
            link_threshold=link_threshold,
        )

    def bridge_discover(
        self,
        seed_ids: Sequence[str],
        *,
        max_depth: int = 3,
        limit: int = 20,
    ) -> dict[str, Any]:
        """AriadneMem LINK-path bridge discovery."""
        return ar_bridge_discover(
            seed_ids,
            list(self.store.iter_entries()),
            max_depth=max_depth,
            limit=limit,
        )

    def fuse_cluster(
        self,
        entry_ids: Sequence[str],
        *,
        label: str | None = None,
    ) -> dict[str, Any]:
        """MemFuse-shaped cluster over atomic evidence ids."""
        return ar_fuse_cluster(
            entry_ids,
            list(self.store.iter_entries()),
            label=label,
        )

    def result_digest(self, payload: Any) -> dict[str, Any]:
        """TGMS content-addressed result digest."""
        return tgms_result_digest(payload)

    def operator_cost_estimate(
        self,
        steps: Sequence[Mapping[str, Any]],
        *,
        max_cost: int = 40,
    ) -> dict[str, Any]:
        """TGMS pre-execution cost guard."""
        return tgms_operator_cost_estimate(steps, max_cost=max_cost)

    def plan_static_verify(
        self,
        plan: Mapping[str, Any],
        *,
        task_ids: Sequence[str] | None = None,
        max_cost: int = 40,
    ) -> dict[str, Any]:
        """TGMS static plan verifier (schema/refs/grounding/cost)."""
        return tgms_plan_static_verify(
            plan, task_ids=task_ids, max_cost=max_cost
        )

    def claim_verify(
        self,
        claims: Sequence[Mapping[str, Any]],
        trace: Mapping[str, Any],
    ) -> dict[str, Any]:
        """TGMS claim verifier against execution trace."""
        return tgms_claim_verify(claims, trace)

    def summary_quarantine_scan(
        self,
        summaries: Sequence[Mapping[str, Any]],
        corrections: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """TGMS quarantine summaries overlapping correction intervals."""
        return tgms_summary_quarantine_scan(summaries, corrections)

    def localized_maintenance_plan(
        self,
        seed_ids: Sequence[str],
        *,
        radius: int = 1,
        max_touch: int = 20,
    ) -> dict[str, Any]:
        """MemoryData O7 localized maintenance (report-only)."""
        return md_localized_maintenance_plan(
            seed_ids,
            list(self.store.iter_entries()),
            radius=radius,
            max_touch=max_touch,
        )

    def maintenance_cost_compare(
        self,
        local_touch: int,
        *,
        store_size: int | None = None,
    ) -> dict[str, Any]:
        """Compare local vs global reorganize cost proxies."""
        size = (
            store_size
            if store_size is not None
            else sum(1 for _ in self.store.iter_entries())
        )
        return md_maintenance_cost_compare(local_touch, store_size=size)

    def origin_bind(
        self,
        pending: Mapping[str, Any],
        *,
        channel_origin: str,
    ) -> dict[str, Any]:
        """TMA-NM write-time origin → act_class binding."""
        return tma_origin_bind(pending, channel_origin=channel_origin)

    def propagate_origin(
        self,
        derived: Mapping[str, Any],
        source_ids: Sequence[str],
    ) -> dict[str, Any]:
        """TMA-NM non-malleable origin propagation from source entries."""
        by_id = {str(e.get("id")): e for e in self.store.iter_entries()}
        sources: list[dict[str, Any]] = []
        for sid in source_ids:
            e = by_id.get(str(sid))
            if e is None:
                continue
            auth = e.get("authority") if isinstance(e.get("authority"), Mapping) else {}
            origin = str(auth.get("origin") or "")
            if not origin:
                src = str((e.get("provenance") or {}).get("source") or "")
                if src.startswith(("user:", "oracle:")):
                    origin = "user"
                elif src.startswith("tool:"):
                    origin = "trusted_tool"
                elif src.startswith("agent:"):
                    origin = "agent"
                else:
                    origin = "untrusted_external"
            sources.append({"id": e.get("id"), "origin": origin})
        return tma_propagate_origin(derived, sources)

    def launder_scan(self, *, limit: int = 40) -> dict[str, Any]:
        """TMA-NM laundering-channel marker scan."""
        return tma_launder_scan(list(self.store.iter_entries()), limit=limit)

    def act_authority_gate(
        self,
        value: str,
        driver_ids: Sequence[str],
        *,
        trusted_principals: Sequence[str] | None = None,
        user_auth: bool = False,
        min_principals: int = 2,
    ) -> dict[str, Any]:
        """TMA-NM consequential-act gate with Sybil-resistant elevation."""
        by_id = {str(e.get("id")): e for e in self.store.iter_entries()}
        drivers = []
        for did in driver_ids:
            e = by_id.get(str(did))
            if e is not None:
                drivers.append(e)
        return tma_act_authority_gate(
            value,
            drivers,
            trusted_principals=trusted_principals,
            user_auth=user_auth,
            min_principals=min_principals,
        )

    def save_policy(
        self,
        pending: Mapping[str, Any],
        *,
        level: str = "standard",
        channel_origin: str = "untrusted_external",
    ) -> dict[str, Any]:
        """AM-Sentry memory-saving policy."""
        return am_save_policy(
            pending, level=level, channel_origin=channel_origin
        )

    def retrieval_screen(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        block_untrusted_act: bool = True,
    ) -> dict[str, Any]:
        """AM-Sentry retrieval screen over Select hits."""
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        enriched: list[dict[str, Any]] = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id")))
            enriched.append(e if e else dict(h))
        return am_retrieval_screen(
            enriched,
            context=query,
            block_untrusted_act=block_untrusted_act,
        )

    def build_memtree(self, *, scope: str | None = None) -> dict[str, Any]:
        """MemForest MemTree hierarchical temporal index."""
        return mf_build_memtree(list(self.store.iter_entries()), scope=scope)

    def dirty_path_plan(
        self,
        new_entry: Mapping[str, Any],
        *,
        scope: str | None = None,
    ) -> dict[str, Any]:
        """Localized MemTree dirty-path update plan."""
        tree = mf_build_memtree(
            list(self.store.iter_entries()),
            scope=scope or new_entry.get("scope"),
        )
        return mf_dirty_path_plan(tree, new_entry)

    def coarse_to_fine(
        self,
        query: str,
        *,
        scope: str | None = None,
        limit: int = 8,
    ) -> dict[str, Any]:
        """MemForest coarse-to-fine retrieval."""
        entries = list(self.store.iter_entries())
        tree = mf_build_memtree(entries, scope=scope)
        return mf_coarse_to_fine(query, tree, entries, limit=limit)

    def build_themes(self, *, scope: str | None = None) -> dict[str, Any]:
        """xMemory theme bootstrap from conflict_key."""
        return xm_build_themes_from_entries(
            list(self.store.iter_entries()), scope=scope
        )

    def theme_attach(
        self,
        entry: Mapping[str, Any],
        *,
        scope: str | None = None,
        min_overlap: float = 0.2,
    ) -> dict[str, Any]:
        """xMemory attach-or-create theme."""
        themes = xm_build_themes_from_entries(
            list(self.store.iter_entries()), scope=scope
        ).get("themes") or []
        return xm_theme_attach(entry, themes, min_overlap=min_overlap)

    def split_merge_plan(
        self,
        *,
        scope: str | None = None,
        max_size: int = 6,
        min_size: int = 2,
    ) -> dict[str, Any]:
        """xMemory theme split/merge plan (report-only)."""
        themes = xm_build_themes_from_entries(
            list(self.store.iter_entries()), scope=scope
        ).get("themes") or []
        return xm_split_merge_plan(
            themes, max_size=max_size, min_size=min_size
        )

    def top_down_pack(
        self,
        query: str,
        *,
        scope: str | None = None,
        budget: int = 200,
        expand_threshold: float = 0.35,
    ) -> dict[str, Any]:
        """xMemory top-down theme→leaf pack under budget."""
        entries = list(self.store.iter_entries())
        themes = xm_build_themes_from_entries(entries, scope=scope).get(
            "themes"
        ) or []
        return xm_top_down_pack(
            query,
            themes,
            entries,
            budget=budget,
            expand_threshold=expand_threshold,
        )

    def persistence_probe(
        self, poison_ids: Sequence[str]
    ) -> dict[str, Any]:
        """MemSecBench Write-stage persistence probe."""
        return ms_persistence_probe(
            list(self.store.iter_entries()), poison_ids=poison_ids
        )

    def execute_chain_probe(
        self,
        poison_ids: Sequence[str],
        *,
        consumer_scope: str,
        probe_query: str = "",
        action_value: str = "",
    ) -> dict[str, Any]:
        """MemSecBench Execute-stage recall/adopt/act probe."""
        hits = self.search(
            probe_query or "a",
            consumer_scope=consumer_scope,
            budget=2000,
            include_contested=True,
        )
        return ms_execute_chain_probe(
            list(self.store.iter_entries()),
            hits,
            poison_ids=poison_ids,
            action_value=action_value,
        )

    def selective_repair_plan(
        self,
        poison_ids: Sequence[str],
        *,
        preserve_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """MemSecBench selective repair plan (report-only)."""
        return ms_selective_repair_plan(
            list(self.store.iter_entries()),
            poison_ids=poison_ids,
            preserve_ids=preserve_ids,
        )

    def lifecycle_report(
        self,
        poison_ids: Sequence[str],
        *,
        consumer_scope: str,
        preserve_ids: Sequence[str] | None = None,
        probe_query: str = "",
        action_value: str = "",
    ) -> dict[str, Any]:
        """MemSecBench Write–Execute–Forget lifecycle bundle."""
        hits = self.search(
            probe_query or "a",
            consumer_scope=consumer_scope,
            budget=2000,
            include_contested=True,
        )
        return ms_lifecycle_report(
            list(self.store.iter_entries()),
            hits,
            poison_ids=poison_ids,
            preserve_ids=preserve_ids,
            action_value=action_value,
        )

    def conflict_tag(
        self, *, conflict_key: str | None = None
    ) -> dict[str, Any]:
        """SleepGate supersession tags."""
        return sg_conflict_tag(
            list(self.store.iter_entries()), conflict_key=conflict_key
        )

    def forget_gate_plan(
        self, *, conflict_key: str | None = None
    ) -> dict[str, Any]:
        """SleepGate PI forget/compress plan."""
        return sg_forget_gate_plan(
            list(self.store.iter_entries()), conflict_key=conflict_key
        )

    def consolidate_survivors(self, conflict_key: str) -> dict[str, Any]:
        """SleepGate survivor consolidation summary."""
        return sg_consolidate_survivors(
            list(self.store.iter_entries()), conflict_key=conflict_key
        )

    def pi_depth_scan(self, conflict_key: str) -> dict[str, Any]:
        """SleepGate proactive-interference depth."""
        return sg_pi_depth_scan(
            list(self.store.iter_entries()), conflict_key=conflict_key
        )

    def consensus_admit(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        min_channels: int = 2,
    ) -> dict[str, Any]:
        """A-MemGuard multi-channel consensus admit."""
        hits = self.search(
            query, consumer_scope=consumer_scope, budget=budget
        )
        return ag_consensus_admit(
            query,
            hits,
            list(self.store.iter_entries()),
            min_channels=min_channels,
        )

    def build_mem_action_graph(
        self,
        *,
        actions: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Dependency-guided repair: memory↔action graph."""
        return dr_build_mem_action_graph(
            list(self.store.iter_entries()), actions=actions
        )

    def dependency_trace(
        self,
        fault_ids: Sequence[str],
        *,
        max_depth: int = 8,
    ) -> dict[str, Any]:
        """Downstream descendants of faulty memories."""
        return dr_dependency_trace(
            list(self.store.iter_entries()),
            fault_ids,
            max_depth=max_depth,
        )

    def preserve_independent(
        self,
        fault_ids: Sequence[str],
        *,
        trusted_sources: Sequence[str] | None = None,
        max_depth: int = 8,
    ) -> dict[str, Any]:
        """Preserve cascade nodes with independent trusted support."""
        return dr_preserve_independent(
            list(self.store.iter_entries()),
            fault_ids,
            trusted_sources=trusted_sources,
            max_depth=max_depth,
        )

    def selective_replay_plan(
        self,
        fault_ids: Sequence[str],
        *,
        trusted_sources: Sequence[str] | None = None,
        actions: Sequence[Mapping[str, Any]] | None = None,
        max_depth: int = 8,
    ) -> dict[str, Any]:
        """Dependency-guided selective replay plan (report-only)."""
        return dr_selective_replay_plan(
            list(self.store.iter_entries()),
            fault_ids,
            trusted_sources=trusted_sources,
            actions=actions,
            max_depth=max_depth,
        )

    def classify_write_channel(self, entry_id: str) -> dict[str, Any]:
        """MPBench write-channel taxonomy for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return mp_classify_write_channel(e)

    def source_isolation_gate(
        self,
        entry_id: str | None = None,
        *,
        candidate: Mapping[str, Any] | None = None,
        deny_channels: Sequence[str] | None = None,
        quarantine_channels: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """MPBench source isolation admit/quarantine/reject."""
        if candidate is not None:
            entry = candidate
        elif entry_id:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise KeyError(entry_id)
        else:
            raise SchemaError("entry_id or candidate is required")
        return mp_source_isolation_gate(
            entry,
            deny_channels=deny_channels,
            quarantine_channels=quarantine_channels,
        )

    def write_channel_inventory(self) -> dict[str, Any]:
        """MPBench inventory of write channels in the store."""
        return mp_write_channel_inventory(list(self.store.iter_entries()))

    def channel_admit_batch(
        self,
        candidates: Sequence[Mapping[str, Any]],
        *,
        deny_channels: Sequence[str] | None = None,
        quarantine_channels: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Batch MPBench source isolation over candidates."""
        return mp_channel_admit_batch(
            candidates,
            deny_channels=deny_channels,
            quarantine_channels=quarantine_channels,
        )

    def slot_coverage(self, entry_id: str) -> dict[str, Any]:
        """MemPoison/Salami semantic slot coverage for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return mpz_slot_coverage(e)

    def threat_tier_classify(self, entry_id: str) -> dict[str, Any]:
        """MemPoison L1/L2/L3 threat tier for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return mpz_threat_tier_classify(e)

    def dormant_trigger_scan(self, *, limit: int = 50) -> dict[str, Any]:
        """Scan for L3 dormant / trigger-conditioned entries."""
        return mpz_dormant_trigger_scan(
            list(self.store.iter_entries()), limit=limit
        )

    def compositional_coalition_scan(
        self,
        *,
        min_slots: int = 3,
        max_coalition: int = 4,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Salami compositional coalitions across the store."""
        return mpz_compositional_coalition_scan(
            list(self.store.iter_entries()),
            min_slots=min_slots,
            max_coalition=max_coalition,
            limit=limit,
        )

    def collusion_risk_gate(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        min_slots: int = 3,
    ) -> dict[str, Any]:
        """Retrieval-time Salami collusion gate over search hits."""
        hits = self.search(
            query, consumer_scope=consumer_scope, budget=budget
        )
        return mpz_collusion_risk_gate(
            hits,
            list(self.store.iter_entries()),
            min_slots=min_slots,
        )

    def mempoison_ladder_report(self, *, limit: int = 100) -> dict[str, Any]:
        """Inventory store by MemPoison L1/L2/L3."""
        return mpz_mempoison_ladder_report(
            list(self.store.iter_entries()), limit=limit
        )

    def salami_pair_probe(
        self, entry_id_a: str, entry_id_b: str
    ) -> dict[str, Any]:
        """Two-fragment Salami collusion probe."""
        a = self.store.read_entry(entry_id_a)
        b = self.store.read_entry(entry_id_b)
        if a is None:
            raise KeyError(entry_id_a)
        if b is None:
            raise KeyError(entry_id_b)
        return mpz_salami_pair_probe(a, b)

    def classify_persistence_layer(
        self, entry_id: str, *, override: str | None = None
    ) -> dict[str, Any]:
        """Knowledge/Memory/Wisdom/Intelligence persistence layer."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return kl_classify_persistence_layer(e, override=override)

    def persistence_policy(self, layer: str) -> dict[str, Any]:
        """Policy card for one persistence layer."""
        return kl_persistence_policy(layer)

    def layer_inventory(self) -> dict[str, Any]:
        """Count entries by persistence layer."""
        return kl_layer_inventory(list(self.store.iter_entries()))

    def knowledge_protect_scan(
        self,
        *,
        faded_ids: Sequence[str] | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Flag knowledge-layer entries that must not age-fade."""
        return kl_knowledge_protect_scan(
            list(self.store.iter_entries()),
            faded_ids=faded_ids,
            limit=limit,
        )

    def intelligence_reject_gate(
        self,
        *,
        candidate: Mapping[str, Any] | None = None,
        entry_id: str | None = None,
    ) -> dict[str, Any]:
        """Reject ephemeral intelligence candidates from persistence."""
        if candidate is not None:
            entry = candidate
        elif entry_id:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise KeyError(entry_id)
        else:
            raise SchemaError("entry_id or candidate is required")
        return kl_intelligence_reject_gate(entry)

    def credential_scan(self, entry_id: str) -> dict[str, Any]:
        """Scan one entry for credential/secret patterns."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return cg_credential_scan_entry(e)

    def credential_reject_gate(
        self,
        *,
        candidate: Mapping[str, Any] | None = None,
        entry_id: str | None = None,
    ) -> dict[str, Any]:
        """MAPLE-shaped write Reject for credentials."""
        if candidate is not None:
            entry = candidate
        elif entry_id:
            entry = self.store.read_entry(entry_id)
            if entry is None:
                raise KeyError(entry_id)
        else:
            raise SchemaError("entry_id or candidate is required")
        return cg_credential_reject_gate(entry)

    def credential_store_scan(self, *, limit: int = 50) -> dict[str, Any]:
        """Inventory store entries that still contain credentials."""
        return cg_credential_store_scan(
            list(self.store.iter_entries()), limit=limit
        )

    def uncertainty_score(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
    ) -> dict[str, Any]:
        """Oblivion-shaped uncertainty over SEARCH hits."""
        hits = self.search(
            query, consumer_scope=consumer_scope, budget=budget
        )
        return og_uncertainty_score(query, hits)

    def uncertainty_retrieve_gate(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        force: bool = False,
        uncertainty_threshold: float = 0.55,
    ) -> dict[str, Any]:
        """Retrieve only when uncertainty is high."""
        hits = self.search(
            query, consumer_scope=consumer_scope, budget=budget
        )
        return og_uncertainty_retrieve_gate(
            query,
            hits,
            force=force,
            uncertainty_threshold=uncertainty_threshold,
        )

    def reasoning_reserve_plan(
        self, budget: int, *, confidence: float
    ) -> dict[str, Any]:
        """MemArchitect adaptive reasoning vs recall budget split."""
        return og_reasoning_reserve_plan(budget, confidence=confidence)

    def classify_memory_component(self, entry_id: str) -> dict[str, Any]:
        """PAM E/S/P/W/I memory component for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return pam_classify_memory_component(e)

    def build_merkle_dag(self) -> dict[str, Any]:
        """PAM Merkle-DAG over store entries (SHA-256)."""
        return pam_build_merkle_dag(list(self.store.iter_entries()))

    def verify_merkle_root(self, expected_root: str) -> dict[str, Any]:
        """Verify store Merkle root matches expected."""
        return pam_verify_merkle_root(
            list(self.store.iter_entries()), expected_root=expected_root
        )

    def issue_capability_token(
        self,
        *,
        entry_ids: Sequence[str],
        ops: Sequence[str],
        audience: str,
        expires_at: str,
        components: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Issue PAM capability token (unkeyed digest)."""
        return pam_issue_capability_token(
            entry_ids=entry_ids,
            ops=ops,
            audience=audience,
            expires_at=expires_at,
            components=components,
        )

    def check_capability(
        self,
        token: str,
        payload: Mapping[str, Any],
        *,
        op: str,
        entry_id: str | None = None,
        now: str | None = None,
    ) -> dict[str, Any]:
        """Check PAM capability token for an operation."""
        return pam_check_capability(
            token,
            payload,
            op=op,
            entry_id=entry_id,
            now=now or self._now,
        )

    def selective_disclose(
        self,
        entry_ids: Sequence[str],
        *,
        include_ancestors: bool = True,
    ) -> dict[str, Any]:
        """PAM selective disclosure with optional ancestor closure."""
        return pam_selective_disclose(
            list(self.store.iter_entries()),
            entry_ids=entry_ids,
            include_ancestors=include_ancestors,
        )

    def rehydrate_safe_plan(
        self, entry_ids: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """PAM injection-resistant rehydrate plan."""
        entries = list(self.store.iter_entries())
        if entry_ids is not None:
            want = {str(i) for i in entry_ids if i}
            entries = [e for e in entries if str(e.get("id")) in want]
        return pam_rehydrate_safe_plan(entries)

    def issue_action_capability(
        self,
        *,
        intent: str,
        method: str,
        host: str,
        session_id: str,
        max_calls: int = 1,
        expires_at: str,
    ) -> dict[str, Any]:
        """CapSeal non-exportable action capability handle."""
        return cs_issue_action_capability(
            intent=intent,
            method=method,
            host=host,
            session_id=session_id,
            max_calls=max_calls,
            expires_at=expires_at,
        )

    def capability_export_probe(
        self, handle: str, payload: Mapping[str, Any]
    ) -> dict[str, Any]:
        """CapSeal: capability handles must never export as bearer secrets."""
        return cs_capability_export_probe(handle, payload)

    def check_action_capability(
        self,
        handle: str,
        payload: Mapping[str, Any],
        *,
        method: str,
        host: str,
        session_id: str,
        call_count: int = 0,
        now: str | None = None,
    ) -> dict[str, Any]:
        """Authorize one CapSeal mediated invocation."""
        return cs_check_action_capability(
            handle,
            payload,
            method=method,
            host=host,
            session_id=session_id,
            call_count=call_count,
            now=now or self._now,
        )

    def action_capability_inventory(
        self, capabilities: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """Summarize CapSeal capability payloads."""
        return cs_action_capability_inventory(capabilities)

    def classify_risk_source(self, step: Mapping[str, Any]) -> dict[str, Any]:
        """AgentDoG risk-source (where) axis."""
        return ad_classify_risk_source(step)

    def classify_failure_mode(self, step: Mapping[str, Any]) -> dict[str, Any]:
        """AgentDoG failure-mode (how) axis."""
        return ad_classify_failure_mode(step)

    def classify_real_world_harm(self, step: Mapping[str, Any]) -> dict[str, Any]:
        """AgentDoG real-world harm (what) axis."""
        return ad_classify_real_world_harm(step)

    def diagnose_trajectory_step(self, step: Mapping[str, Any]) -> dict[str, Any]:
        """Fine-grained 3D diagnosis for one trajectory step."""
        return ad_diagnose_trajectory_step(step)

    def diagnose_trajectory(
        self, steps: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """Trajectory-level AgentDoG diagnosis."""
        return ad_diagnose_trajectory(steps)

    def safe_but_unreasonable_scan(
        self, steps: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """Surface seemingly safe but unreasonable steps."""
        return ad_safe_but_unreasonable_scan(steps)

    def taxonomy_inventory(self) -> dict[str, Any]:
        """AgentDoG controlled-vocab inventory."""
        return ad_taxonomy_inventory()

    def weave_layer_assign(self, entry_id: str) -> dict[str, Any]:
        """MemWeaver GM/ExpM/PM layer for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return mw_weave_layer_assign(e)

    def build_hybrid_weave(self) -> dict[str, Any]:
        """MemWeaver tri-layer weave over the store."""
        return mw_build_hybrid_weave(list(self.store.iter_entries()))

    def dual_channel_retrieve(
        self,
        query: str,
        *,
        k_r: int = 6,
        k_p: int = 6,
        k_e: int = 6,
    ) -> dict[str, Any]:
        """MemWeaver dual-channel retrieve (structured + textual)."""
        return mw_dual_channel_retrieve(
            list(self.store.iter_entries()),
            query=query,
            k_r=k_r,
            k_p=k_p,
            k_e=k_e,
        )

    def experience_abstract_plan(
        self, *, min_support: int = 2
    ) -> dict[str, Any]:
        """MemWeaver experience abstraction plan (report-only)."""
        return mw_experience_abstract_plan(
            list(self.store.iter_entries()), min_support=min_support
        )

    def temporal_session_conflict_scan(self) -> dict[str, Any]:
        """MemWeaver session-level temporal conflict reconcile plan."""
        return mw_temporal_session_conflict_scan(list(self.store.iter_entries()))

    def multi_hop_depth_score(
        self, path_ids: Sequence[str]
    ) -> dict[str, Any]:
        """MemHop-shaped hop depth over an explicit entry path."""
        return mw_multi_hop_depth_score(
            path_ids, list(self.store.iter_entries())
        )

    def list_design_space(self) -> dict[str, Any]:
        """MemEvolve/EvolveLab four-component design space."""
        return me_list_design_space()

    def architecture_profile(
        self, overrides: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        """Concrete Ω = (Encode, Store, Retrieve, Manage) profile."""
        return me_architecture_profile(overrides)

    def diagnose_architecture(
        self,
        profile: Mapping[str, Any],
        *,
        feedback: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """MemEvolve defect profile D(Ω)."""
        return me_diagnose_architecture(profile, feedback=feedback)

    def propose_architecture_variants(
        self,
        profile: Mapping[str, Any],
        diagnosis: Mapping[str, Any],
        *,
        s: int = 3,
    ) -> dict[str, Any]:
        """MemEvolve Design step — S variants (report-only)."""
        return me_propose_architecture_variants(profile, diagnosis, s=s)

    def rank_architecture_fitness(
        self, candidates: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """Rank Ω candidates by success / cost / latency fitness."""
        return me_rank_architecture_fitness(candidates)

    def select_architecture_parents(
        self,
        ranked: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        *,
        k: int = 1,
    ) -> dict[str, Any]:
        """Outer-loop survivor budget K."""
        return me_select_architecture_parents(ranked, k=k)

    def ept_classify(self, entry_id: str) -> dict[str, Any]:
        """MindMemOS entity–property–time view of one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return mm_ept_classify(e)

    def functional_role_assign(self, entry_id: str) -> dict[str, Any]:
        """MEMGUARD functional role for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return mm_functional_role_assign(e)

    def contamination_scan(self) -> dict[str, Any]:
        """MEMGUARD heterogeneous contamination scan."""
        return mm_contamination_scan(list(self.store.iter_entries()))

    def type_route_retrieve(
        self,
        query: str,
        *,
        allowed_roles: Sequence[str] | None = None,
        budget: int = 8,
    ) -> dict[str, Any]:
        """MEMGUARD query-adaptive type routing."""
        return mm_type_route_retrieve(
            list(self.store.iter_entries()),
            query=query,
            allowed_roles=allowed_roles,
            budget=budget,
        )

    def dreaming_consolidate_plan(self) -> dict[str, Any]:
        """MindMemOS offline dreaming consolidate plan (report-only)."""
        return mm_dreaming_consolidate_plan(list(self.store.iter_entries()))

    def feedback_revise_plan(
        self,
        *,
        signal: str,
        entry_ids: Sequence[str] | None = None,
        mode: str = "explicit",
    ) -> dict[str, Any]:
        """MindMemOS corrective feedback → revise actions."""
        return mm_feedback_revise_plan(
            signal=signal, entry_ids=entry_ids, mode=mode
        )

    def skill_evolve_plan(
        self,
        trajectories: Sequence[Mapping[str, Any]],
        *,
        supervised: bool = False,
        min_batch: int = 2,
    ) -> dict[str, Any]:
        """MindSkillEvolve trajectory → skill update plan."""
        return mm_skill_evolve_plan(
            trajectories, supervised=supervised, min_batch=min_batch
        )

    def extract_preference_signal(self, text: str) -> dict[str, Any]:
        """PAMU 5-D preference observation from text."""
        return pu_extract_preference_signal(text)

    def fuse_preference(
        self,
        sw: Mapping[str, float],
        ema: Mapping[str, float],
        *,
        lam: float = 0.5,
    ) -> dict[str, Any]:
        """PAMU SW+EMA fusion."""
        return pu_fuse_preference(sw, ema, lam=lam)

    def preference_change_detect(
        self,
        sw: Mapping[str, float],
        ema: Mapping[str, float],
        *,
        delta: float = 0.35,
    ) -> dict[str, Any]:
        """PAMU divergence change detection."""
        return pu_preference_change_detect(sw, ema, delta=delta)

    def preference_update_plan(
        self,
        observations: Sequence[Mapping[str, Any] | str],
        *,
        window: int = 3,
        beta: float = 0.8,
        lam: float = 0.5,
        delta: float = 0.35,
    ) -> dict[str, Any]:
        """PAMU full preference update plan (report-only)."""
        return pu_preference_update_plan(
            observations, window=window, beta=beta, lam=lam, delta=delta
        )

    def format_preference_prompt(
        self, fused: Mapping[str, float]
    ) -> dict[str, Any]:
        """PAMU NL preference prompt from fused vector."""
        return pu_format_preference_prompt(fused)

    def beam_category_inventory(self) -> dict[str, Any]:
        """BEAM ten-category inventory."""
        return bm_beam_category_inventory()

    def classify_beam_query(self, query: str) -> dict[str, Any]:
        """Classify query into a BEAM category."""
        return bm_classify_beam_query(query)

    def knowledge_update_check(
        self, *, prior: str, current: str
    ) -> dict[str, Any]:
        """BEAM knowledge-update supersede check."""
        return bm_knowledge_update_check(prior=prior, current=current)

    def abstention_gate(
        self,
        *,
        query: str,
        evidence_count: int,
        min_evidence: int = 1,
    ) -> dict[str, Any]:
        """BEAM abstention when evidence is insufficient."""
        return bm_abstention_gate(
            query=query,
            evidence_count=evidence_count,
            min_evidence=min_evidence,
        )

    def contradiction_resolve_plan(
        self, statements: Sequence[Mapping[str, Any] | str]
    ) -> dict[str, Any]:
        """BEAM contradiction resolve plan (preserve contested)."""
        return bm_contradiction_resolve_plan(statements)

    def event_order_check(
        self, events: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """BEAM event-ordering check."""
        return bm_event_order_check(events)

    def localize_hallucination_stage(
        self,
        *,
        symptom: str,
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """HaluMem operation-stage localization."""
        return bm_localize_hallucination_stage(symptom=symptom, context=context)

    def beam_eval_pack(
        self, cases: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """Local BEAM-shaped eval pack."""
        return bm_beam_eval_pack(cases)

    def extract_episodic_gist(self, entry_id: str) -> dict[str, Any]:
        """REMem time-aware episodic gist."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return rm_extract_episodic_gist(e)

    def extract_temporal_facts(self, entry_id: str) -> dict[str, Any]:
        """REMem temporal SPO facts."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return rm_extract_temporal_facts(e)

    def situational_bind(self, entry_id: str) -> dict[str, Any]:
        """REMem situational dimension binding."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return rm_situational_bind(e)

    def build_hybrid_episodic_graph(self) -> dict[str, Any]:
        """REMem hybrid gist+fact graph over the store."""
        return rm_build_hybrid_episodic_graph(list(self.store.iter_entries()))

    def agentic_retrieve_plan(
        self, query: str, *, max_steps: int = 3
    ) -> dict[str, Any]:
        """REMem-I agentic retrieval plan (report-only)."""
        return rm_agentic_retrieve_plan(
            list(self.store.iter_entries()), query=query, max_steps=max_steps
        )

    def ordinal_event_query(self, *, order: str = "first") -> dict[str, Any]:
        """REMem first/last event by timeline."""
        return rm_ordinal_event_query(
            list(self.store.iter_entries()), order=order
        )

    def form_memcell(self, entry_id: str) -> dict[str, Any]:
        """EverMemOS MemCell formation."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return ev_form_memcell(e)

    def consolidate_memscenes(
        self, *, sim_threshold: float = 0.15
    ) -> dict[str, Any]:
        """EverMemOS MemScene consolidation."""
        return ev_consolidate_memscenes(
            list(self.store.iter_entries()), sim_threshold=sim_threshold
        )

    def foresight_filter(self, *, now: str | None = None) -> dict[str, Any]:
        """EverMemOS foresight validity filter."""
        consol = ev_consolidate_memscenes(list(self.store.iter_entries()))
        return ev_foresight_filter(consol["cells"], now=now or self._now)

    def reconstructive_recollect(
        self,
        query: str,
        *,
        n_scenes: int = 3,
        k_episodes: int = 5,
    ) -> dict[str, Any]:
        """EverMemOS reconstructive recollection."""
        return ev_reconstructive_recollect(
            list(self.store.iter_entries()),
            query=query,
            n_scenes=n_scenes,
            k_episodes=k_episodes,
        )

    def profile_evolve_plan(self) -> dict[str, Any]:
        """EverMemOS scene-driven profile evolution plan."""
        return ev_profile_evolve_plan(list(self.store.iter_entries()))

    def necessity_sufficiency_check(
        self,
        *,
        retrieved_count: int,
        min_needed: int = 1,
        max_sufficient: int = 10,
    ) -> dict[str, Any]:
        """EverMemOS Phase-III retrieval budget check."""
        return ev_necessity_sufficiency_check(
            retrieved_count=retrieved_count,
            min_needed=min_needed,
            max_sufficient=max_sufficient,
        )

    def classify_memory_tier(self, entry_id: str) -> dict[str, Any]:
        """MemoryOS STM/MTM/LPM tier for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return mo_classify_memory_tier(e, now=self._now)

    def heat_score(
        self,
        *,
        n_visit: int = 0,
        l_interaction: int = 1,
        delta_t_seconds: float = 0.0,
        alpha: float = 1.0,
        beta: float = 0.5,
        gamma: float = 1.0,
    ) -> dict[str, Any]:
        """MemoryOS segment heat score."""
        return mo_heat_score(
            n_visit=n_visit,
            l_interaction=l_interaction,
            delta_t_seconds=delta_t_seconds,
            alpha=alpha,
            beta=beta,
            gamma=gamma,
        )

    def segment_pages(self, *, theta: float = 0.15) -> dict[str, Any]:
        """MemoryOS segmented paging over the store."""
        return mo_segment_pages(list(self.store.iter_entries()), theta=theta)

    def stm_to_mtm_plan(
        self,
        stm_page_ids: Sequence[str],
        *,
        capacity: int = 5,
    ) -> dict[str, Any]:
        """MemoryOS STM→MTM FIFO overflow plan."""
        return mo_stm_to_mtm_plan(stm_page_ids, capacity=capacity)

    def mtm_evict_plan(
        self,
        segments: Sequence[Mapping[str, Any]] | None = None,
        *,
        max_segments: int = 3,
    ) -> dict[str, Any]:
        """MemoryOS lowest-heat MTM eviction plan."""
        segs = list(segments) if segments is not None else self.segment_pages()["segments"]
        return mo_mtm_evict_plan(segs, max_segments=max_segments)

    def promote_to_lpm_plan(
        self,
        segments: Sequence[Mapping[str, Any]] | None = None,
        *,
        tau: float = 5.0,
    ) -> dict[str, Any]:
        """MemoryOS heat→LPM promotion plan."""
        segs = list(segments) if segments is not None else self.segment_pages()["segments"]
        return mo_promote_to_lpm_plan(segs, tau=tau)

    def hierarchical_retrieve(
        self,
        query: str,
        *,
        top_m_segments: int = 2,
        top_k_pages: int = 3,
    ) -> dict[str, Any]:
        """MemoryOS STM+MTM+LPM hierarchical retrieve."""
        return mo_hierarchical_retrieve(
            list(self.store.iter_entries()),
            query=query,
            now=self._now,
            top_m_segments=top_m_segments,
            top_k_pages=top_k_pages,
        )

    def integrate_episodic_narrative(self, entry_id: str) -> dict[str, Any]:
        """NEMORI episodic narrative integration."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return nm_integrate_episodic_narrative(e)

    def anticipatory_schema(self, cue: str) -> dict[str, Any]:
        """NEMORI anticipatory schema from store."""
        return nm_anticipatory_schema(list(self.store.iter_entries()), cue=cue)

    def prediction_error_distill(
        self, *, actual: str, anticipated: str
    ) -> dict[str, Any]:
        """NEMORI prediction-error distillation."""
        return nm_prediction_error_distill(actual=actual, anticipated=anticipated)

    def deserves_memory_gate(
        self,
        *,
        actual: str,
        anticipated: str,
        min_error_ratio: float = 0.25,
        min_novel: int = 3,
    ) -> dict[str, Any]:
        """NEMORI admit-if-unexpected gate."""
        return nm_deserves_memory_gate(
            actual=actual,
            anticipated=anticipated,
            min_error_ratio=min_error_ratio,
            min_novel=min_novel,
        )

    def distill_batch_plan(
        self, entry_ids: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """NEMORI batch distill plan (report-only)."""
        entries = list(self.store.iter_entries())
        if entry_ids is not None:
            want = {str(i) for i in entry_ids if i}
            entries = [e for e in entries if str(e.get("id")) in want]
        return nm_distill_batch_plan(entries)

    def classify_network(self, entry_id: str) -> dict[str, Any]:
        """Hindsight network for one entry."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return hs_classify_network(e)

    def retain_plan(self, entry_ids: Sequence[str] | None = None) -> dict[str, Any]:
        """Hindsight retain plan across four networks."""
        entries = list(self.store.iter_entries())
        if entry_ids is not None:
            want = {str(i) for i in entry_ids if i}
            entries = [e for e in entries if str(e.get("id")) in want]
        return hs_retain_plan(entries)

    def network_inventory(self) -> dict[str, Any]:
        """Hindsight network inventory."""
        return hs_network_inventory(list(self.store.iter_entries()))

    def recall_multi_strategy(
        self,
        query: str,
        *,
        token_budget: int = 400,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Hindsight multi-strategy recall (RRF lexical proxy)."""
        return hs_recall_multi_strategy(
            list(self.store.iter_entries()),
            query=query,
            token_budget=token_budget,
            top_k=top_k,
        )

    def opinion_reinforce(
        self,
        opinion_text: str,
        *,
        supporting: bool = True,
        prior_confidence: float = 0.5,
        step: float = 0.1,
    ) -> dict[str, Any]:
        """Hindsight opinion confidence update plan."""
        return hs_opinion_reinforce(
            opinion_text=opinion_text,
            supporting=supporting,
            prior_confidence=prior_confidence,
            step=step,
        )

    def reflect_plan(
        self,
        query: str,
        *,
        skepticism: int = 3,
        literalism: int = 3,
        empathy: int = 3,
        bias_strength: float = 0.5,
        token_budget: int = 400,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """Hindsight Cara-shaped reflect plan."""
        recalled = self.recall_multi_strategy(
            query, token_budget=token_budget, top_k=top_k
        )["hits"]
        return hs_reflect_plan(
            query=query,
            recalled=recalled,
            skepticism=skepticism,
            literalism=literalism,
            empathy=empathy,
            bias_strength=bias_strength,
        )

    def distill_strategy_item(
        self, entry_id: str, *, outcome: str = "success"
    ) -> dict[str, Any]:
        """ReasoningBank strategy item distill."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return rb_distill_strategy_item(e, outcome=outcome)

    def failure_lesson_gate(
        self, *, success_count: int, failure_count: int, min_failure_share: float = 0.2
    ) -> dict[str, Any]:
        """ReasoningBank failure-lesson coverage gate."""
        return rb_failure_lesson_gate(
            success_count=success_count,
            failure_count=failure_count,
            min_failure_share=min_failure_share,
        )

    def retrieve_strategies(
        self,
        strategies: Sequence[Mapping[str, Any]],
        *,
        query: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """ReasoningBank retrieve strategies."""
        return rb_retrieve_strategies(strategies, query=query, top_k=top_k)

    def consolidate_strategy_plan(
        self, items: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """ReasoningBank consolidate strategy bank plan."""
        return rb_consolidate_strategy_plan(items)

    def matts_contrastive_plan(
        self,
        *,
        mode: str = "parallel",
        n_trajectories: int = 3,
        task_hint: str = "",
    ) -> dict[str, Any]:
        """ReasoningBank MaTTS contrastive scaling plan."""
        return rb_matts_contrastive_plan(
            mode=mode, n_trajectories=n_trajectories, task_hint=task_hint
        )

    def init_skill_bank(
        self, extra: Sequence[Mapping[str, Any]] | None = None
    ) -> dict[str, Any]:
        """MemSkill initialize skill bank."""
        return ms_init_skill_bank(extra)

    def span_partition(self, text: str, *, max_chars: int = 120) -> dict[str, Any]:
        """MemSkill span partition."""
        return ms_span_partition(text, max_chars=max_chars)

    def select_skills(
        self,
        *,
        span_text: str,
        retrieved_hint: str = "",
        top_k: int = 2,
        extra_skills: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """MemSkill controller Top-K skill select."""
        bank = ms_init_skill_bank(extra_skills)["skills"]
        return ms_select_skills(
            bank, span_text=span_text, retrieved_hint=retrieved_hint, top_k=top_k
        )

    def execute_skill_plan(
        self,
        *,
        span_text: str,
        selected_skills: Sequence[Mapping[str, Any]] | None = None,
        top_k: int = 2,
    ) -> dict[str, Any]:
        """MemSkill executor skill-guided op plan."""
        selected = list(selected_skills) if selected_skills is not None else None
        if selected is None:
            selected = self.select_skills(span_text=span_text, top_k=top_k)["selected"]
        return ms_execute_skill_plan(span_text=span_text, selected_skills=selected)

    def record_hard_case(
        self,
        *,
        query: str,
        predicted: str = "",
        expected: str = "",
        performance: float = 0.0,
        fail: bool = True,
    ) -> dict[str, Any]:
        """MemSkill hard-case buffer record."""
        return ms_record_hard_case(
            query=query,
            predicted=predicted,
            expected=expected,
            performance=performance,
            fail=fail,
        )

    def designer_evolve_plan(
        self,
        hard_cases: Sequence[Mapping[str, Any]],
        *,
        extra_skills: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """MemSkill designer evolve plan from hard cases."""
        bank = ms_init_skill_bank(extra_skills)["skills"]
        return ms_designer_evolve_plan(hard_cases, current_skills=bank)

    def classify_memory_op(
        self, candidate: str, *, entry_ids: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """Memory-R1 ADD/UPDATE/DELETE/NOOP classify."""
        entries = list(self.store.iter_entries())
        if entry_ids is not None:
            want = {str(i) for i in entry_ids if i}
            entries = [e for e in entries if str(e.get("id")) in want]
        bodies = [f"{e.get('title') or ''}\n{e.get('body') or ''}" for e in entries]
        return mr_classify_memory_op(candidate=candidate, existing_bodies=bodies)

    def noop_gate(
        self,
        candidate: str,
        *,
        min_overlap: float = 0.7,
        entry_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Memory-R1 NOOP redundancy gate."""
        entries = list(self.store.iter_entries())
        if entry_ids is not None:
            want = {str(i) for i in entry_ids if i}
            entries = [e for e in entries if str(e.get("id")) in want]
        bodies = [f"{e.get('title') or ''}\n{e.get('body') or ''}" for e in entries]
        return mr_noop_gate(
            candidate=candidate, existing_bodies=bodies, min_overlap=min_overlap
        )

    def memory_op_plan(self, candidate: str) -> dict[str, Any]:
        """Memory-R1 memory operation plan."""
        return mr_memory_op_plan(
            candidate=candidate, existing_entries=list(self.store.iter_entries())
        )

    def conflict_update_plan(
        self, *, old_text: str, new_text: str
    ) -> dict[str, Any]:
        """Memory-R1 conflict UPDATE plan."""
        return mr_conflict_update_plan(old_text=old_text, new_text=new_text)

    def delete_stale_plan(
        self, *, revoke_markers: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """Memory-R1 DELETE stale plan."""
        return mr_delete_stale_plan(
            list(self.store.iter_entries()), revoke_markers=revoke_markers
        )

    def classify_graph_tier(self, entry_id: str) -> dict[str, Any]:
        """G-Memory insight/query/interaction tier."""
        e = self.store.read_entry(entry_id)
        if e is None:
            raise KeyError(entry_id)
        return gm_classify_graph_tier(e)

    def build_query_graph(self) -> dict[str, Any]:
        """G-Memory query graph over the store."""
        return gm_build_query_graph(list(self.store.iter_entries()))

    def upward_insight_traverse(
        self, query: str, *, top_k: int = 3
    ) -> dict[str, Any]:
        """G-Memory upward insight traverse."""
        return gm_upward_insight_traverse(
            list(self.store.iter_entries()), query=query, top_k=top_k
        )

    def downward_interaction_traverse(
        self, query: str, *, top_k: int = 3
    ) -> dict[str, Any]:
        """G-Memory downward interaction traverse."""
        return gm_downward_interaction_traverse(
            list(self.store.iter_entries()), query=query, top_k=top_k
        )

    def bidirectional_retrieve(
        self, query: str, *, top_k: int = 3
    ) -> dict[str, Any]:
        """G-Memory bi-directional retrieve."""
        return gm_bidirectional_retrieve(
            list(self.store.iter_entries()), query=query, top_k=top_k
        )

    def hierarchy_update_plan(
        self,
        *,
        query: str,
        status: str,
        used_insight_ids: Sequence[str] | None = None,
        new_insight: str = "",
    ) -> dict[str, Any]:
        """G-Memory hierarchy update plan."""
        return gm_hierarchy_update_plan(
            query=query,
            status=status,
            used_insight_ids=used_insight_ids,
            new_insight=new_insight,
        )

    def meta_thinker_guidance(
        self,
        chunk: str,
        *,
        mode: str = "construction",
        evidence_hint: str = "",
    ) -> dict[str, Any]:
        """MemMA Meta-Thinker guidance."""
        return mm_meta_thinker_guidance(
            chunk=chunk, mode=mode, evidence_hint=evidence_hint
        )

    def answerability_check(
        self, query: str, *, evidence_blobs: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """MemMA answerability check."""
        blobs = list(evidence_blobs) if evidence_blobs is not None else [
            f"{e.get('title') or ''}\n{e.get('body') or ''}"
            for e in self.store.iter_entries()
        ]
        return mm_answerability_check(query=query, evidence_blobs=blobs)

    def synthesize_probe_qa(
        self, session_text: str, *, max_probes: int = 3
    ) -> dict[str, Any]:
        """MemMA synthesize probe QA."""
        return mm_synthesize_probe_qa(session_text, max_probes=max_probes)

    def verify_probes(
        self,
        probes: Sequence[Mapping[str, Any]],
        *,
        evidence_blobs: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """MemMA verify probes against evidence."""
        blobs = list(evidence_blobs) if evidence_blobs is not None else [
            f"{e.get('title') or ''}\n{e.get('body') or ''}"
            for e in self.store.iter_entries()
        ]
        return mm_verify_probes(probes, evidence_blobs=blobs)

    def repair_from_probes(
        self,
        probes: Sequence[Mapping[str, Any]],
        verify_results: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """MemMA repair plan from failed probes."""
        bodies = [
            f"{e.get('title') or ''}\n{e.get('body') or ''}"
            for e in self.store.iter_entries()
        ]
        return mm_repair_from_probes(
            probes, verify_results, existing_bodies=bodies
        )

    def induce_workflow(
        self,
        *,
        task: str,
        steps: Sequence[str],
        success: bool = True,
    ) -> dict[str, Any]:
        """AWM induce workflow from trajectory."""
        return awm_induce_workflow(task=task, steps=steps, success=success)

    def online_induce_gate(self, *, success_label: bool) -> dict[str, Any]:
        """AWM online induce gate."""
        return awm_online_induce_gate(success_label=success_label)

    def workflow_memory_add_plan(
        self,
        new_workflow: Mapping[str, Any],
        *,
        existing: Sequence[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """AWM add workflow plan."""
        return awm_workflow_memory_add_plan(list(existing or []), new_workflow)

    def retrieve_workflows(
        self,
        workflows: Sequence[Mapping[str, Any]],
        *,
        query: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """AWM retrieve workflows."""
        return awm_retrieve_workflows(workflows, query=query, top_k=top_k)

    def workflow_step_budget(
        self, *, baseline_steps: int, workflow_step_count: int
    ) -> dict[str, Any]:
        """AWM step-budget estimate."""
        return awm_workflow_step_budget(
            baseline_steps=baseline_steps,
            workflow_step_count=workflow_step_count,
        )

    def distill_retrieval_experience(
        self,
        *,
        query: str,
        outcome: str,
        anomaly: str = "none",
        strategy_hint: str = "",
    ) -> dict[str, Any]:
        """RRM distill procedural retrieval experience."""
        return rrm_distill_retrieval_experience(
            query=query,
            outcome=outcome,
            anomaly=anomaly,
            strategy_hint=strategy_hint,
        )

    def anomaly_trigger(
        self,
        *,
        hit_count: int = 0,
        prior_queries: Sequence[str] | None = None,
        current_query: str = "",
        rounds_used: int = 0,
        max_rounds: int = 5,
    ) -> dict[str, Any]:
        """RRM retrieval anomaly trigger."""
        return rrm_anomaly_trigger(
            hit_count=hit_count,
            prior_queries=prior_queries,
            current_query=current_query,
            rounds_used=rounds_used,
            max_rounds=max_rounds,
        )

    def query_level_guidance(
        self,
        experiences: Sequence[Mapping[str, Any]],
        *,
        query: str,
        anomaly: str = "none",
    ) -> dict[str, Any]:
        """RRM query-level retrieval guidance."""
        return rrm_query_level_guidance(
            experiences, query=query, anomaly=anomaly
        )

    def experience_lifecycle_score(
        self,
        *,
        usage: int = 0,
        reuse_success: int = 0,
        age_days: float = 0.0,
        half_life_days: float = 30.0,
    ) -> dict[str, Any]:
        """RRM experience utility score."""
        return rrm_experience_lifecycle_score(
            usage=usage,
            reuse_success=reuse_success,
            age_days=age_days,
            half_life_days=half_life_days,
        )

    def prune_experience_plan(
        self,
        experiences: Sequence[Mapping[str, Any]],
        *,
        capacity: int = 10,
        protect_new: int = 2,
    ) -> dict[str, Any]:
        """RRM prune experience plan."""
        return rrm_prune_experience_plan(
            experiences, capacity=capacity, protect_new=protect_new
        )

    def isolate_factual_from_procedural(
        self,
        *,
        answer_pack_ids: Sequence[str],
        experience_ids: Sequence[str],
    ) -> dict[str, Any]:
        """RRM factual/procedural isolation gate."""
        return rrm_isolate_factual_from_procedural(
            answer_pack_ids=answer_pack_ids, experience_ids=experience_ids
        )

    def multi_faceted_distill(
        self,
        *,
        scenario: str,
        outcome: str,
        steps: Sequence[str] | None = None,
        failure_reason: str = "",
        peer_success: str = "",
    ) -> dict[str, Any]:
        """ReMe multi-faceted experience distill."""
        return reme_multi_faceted_distill(
            scenario=scenario,
            outcome=outcome,
            steps=steps,
            failure_reason=failure_reason,
            peer_success=peer_success,
        )

    def scenario_retrieve(
        self,
        pool: Sequence[Mapping[str, Any]],
        *,
        scenario: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """ReMe scenario-aware retrieve."""
        return reme_scenario_retrieve(pool, scenario=scenario, top_k=top_k)

    def adaptive_rewrite_plan(
        self,
        experiences: Sequence[Mapping[str, Any]],
        *,
        new_scenario: str,
    ) -> dict[str, Any]:
        """ReMe adaptive rewrite plan."""
        return reme_adaptive_rewrite_plan(
            experiences, new_scenario=new_scenario
        )

    def utility_after_reuse(
        self, *, freq: int, utility: int, reuse_helped: bool
    ) -> dict[str, Any]:
        """ReMe utility counter update."""
        return reme_utility_after_reuse(
            freq=freq, utility=utility, reuse_helped=reuse_helped
        )

    def selective_add_plan(
        self,
        candidate: Mapping[str, Any],
        *,
        pool: Sequence[Mapping[str, Any]] | None = None,
        require_validated: bool = True,
        validated: bool = True,
    ) -> dict[str, Any]:
        """ReMe selective add plan."""
        return reme_selective_add_plan(
            list(pool or []),
            candidate,
            require_validated=require_validated,
            validated=validated,
        )

    def utility_prune_plan(
        self,
        pool: Sequence[Mapping[str, Any]],
        *,
        alpha: int = 3,
        beta: float = 0.3,
    ) -> dict[str, Any]:
        """ReMe utility prune plan."""
        return reme_utility_prune_plan(pool, alpha=alpha, beta=beta)

    def extract_cheatsheet_snippet(
        self,
        *,
        kind: str,
        title: str,
        body: str,
        max_chars: int = 240,
    ) -> dict[str, Any]:
        """DC extract compact cheatsheet snippet."""
        return dc_extract_cheatsheet_snippet(
            kind=kind, title=title, body=body, max_chars=max_chars
        )

    def retrieve_cheatsheet(
        self,
        memory: Sequence[Mapping[str, Any]],
        *,
        query: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """DC retrieve cheatsheet snippets."""
        return dc_retrieve_cheatsheet(memory, query=query, top_k=top_k)

    def curator_decide(
        self,
        *,
        proposed_useful: bool,
        existing_faulty: bool = False,
        superseded: bool = False,
    ) -> dict[str, Any]:
        """DC curator decision."""
        return dc_curator_decide(
            proposed_useful=proposed_useful,
            existing_faulty=existing_faulty,
            superseded=superseded,
        )

    def compact_memory_gate(
        self,
        *,
        entry_chars: int,
        max_entry_chars: int = 240,
        memory_chars: int = 0,
        max_memory_chars: int = 4000,
    ) -> dict[str, Any]:
        """DC compact memory gate (forbid FH ballooning)."""
        return dc_compact_memory_gate(
            entry_chars=entry_chars,
            max_entry_chars=max_entry_chars,
            memory_chars=memory_chars,
            max_memory_chars=max_memory_chars,
        )

    def dc_rs_order_check(self, steps: Sequence[str]) -> dict[str, Any]:
        """DC-RS / DC-Cu order check."""
        return dc_dc_rs_order_check(steps)

    def experience_pool_add(
        self,
        *,
        task: str,
        outcome: str,
        trajectory_summary: str = "",
    ) -> dict[str, Any]:
        """ExpeL experience pool add."""
        return expel_experience_pool_add(
            task=task, outcome=outcome, trajectory_summary=trajectory_summary
        )

    def insight_op(
        self,
        insights: Sequence[Mapping[str, Any]],
        *,
        op: str,
        text: str = "",
        insight_id: str | None = None,
    ) -> dict[str, Any]:
        """ExpeL insight ADD/EDIT/UPVOTE/DOWNVOTE."""
        return expel_insight_op(
            insights, op=op, text=text, insight_id=insight_id
        )

    def insight_importance_gate(
        self, insights: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """ExpeL drop insights at importance 0."""
        return expel_insight_importance_gate(insights)

    def retrieve_insights(
        self,
        insights: Sequence[Mapping[str, Any]],
        *,
        query: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """ExpeL retrieve insights."""
        return expel_retrieve_insights(insights, query=query, top_k=top_k)

    def retrieve_similar_successes(
        self,
        pool: Sequence[Mapping[str, Any]],
        *,
        task: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """ExpeL retrieve similar successes."""
        return expel_retrieve_similar_successes(pool, task=task, top_k=top_k)

    def prospective_reflect(
        self,
        *,
        topic: str,
        segment: str,
        granularity: str = "turn",
    ) -> dict[str, Any]:
        """RMM dialogue prospective reflection."""
        return rmm_d_prospective_reflect(
            topic=topic, segment=segment, granularity=granularity
        )

    def topic_memory_bank(
        self, memories: Sequence[Mapping[str, Any]]
    ) -> dict[str, Any]:
        """RMM dialogue topic memory bank index."""
        return rmm_d_topic_memory_bank(memories)

    def retrieve_topic_memories(
        self,
        memories: Sequence[Mapping[str, Any]],
        *,
        query: str,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """RMM dialogue topic retrieve."""
        return rmm_d_retrieve_topic_memories(
            memories, query=query, top_k=top_k
        )

    def retrospective_cite_feedback(
        self,
        *,
        cited_ids: Sequence[str],
        all_retrieved_ids: Sequence[str],
    ) -> dict[str, Any]:
        """RMM dialogue retrospective cite feedback."""
        return rmm_d_retrospective_cite_feedback(
            cited_ids=cited_ids, all_retrieved_ids=all_retrieved_ids
        )

    def rerank_memories(
        self,
        candidates: Sequence[Mapping[str, Any]],
        *,
        query: str,
        cite_boosts: Mapping[str, float] | None = None,
    ) -> dict[str, Any]:
        """RMM dialogue rerank memories."""
        return rmm_d_rerank_memories(
            candidates, query=query, cite_boosts=cite_boosts
        )

    def retrieval_refine_plan(
        self,
        memories: Sequence[Mapping[str, Any]],
        *,
        cited_ids: Sequence[str],
        unused_ids: Sequence[str],
        cite_delta: float = 0.15,
        unused_delta: float = 0.05,
    ) -> dict[str, Any]:
        """RMM dialogue retrieval refine plan."""
        return rmm_d_retrieval_refine_plan(
            memories,
            cited_ids=cited_ids,
            unused_ids=unused_ids,
            cite_delta=cite_delta,
            unused_delta=unused_delta,
        )

    def collect_trajectory_label(
        self, *, task: str, outcome: str, lesson: str = ""
    ) -> dict[str, Any]:
        """Trace2Skill labeled trajectory."""
        return t2s_collect_trajectory_label(
            task=task, outcome=outcome, lesson=lesson
        )

    def propose_trajectory_patch(
        self,
        trajectory: Mapping[str, Any],
        *,
        base_skill: str = "",
        analyst: str = "auto",
    ) -> dict[str, Any]:
        """Trace2Skill propose patch from one trajectory."""
        return t2s_propose_trajectory_patch(
            trajectory=trajectory, base_skill=base_skill, analyst=analyst
        )

    def parallel_patch_pool(
        self,
        trajectories: Sequence[Mapping[str, Any]],
        *,
        base_skill: str = "",
    ) -> dict[str, Any]:
        """Trace2Skill parallel patch pool."""
        return t2s_parallel_patch_pool(
            trajectories, base_skill=base_skill
        )

    def hierarchical_merge_patches(
        self,
        patches: Sequence[Mapping[str, Any]],
        *,
        merge_branch: int = 4,
    ) -> dict[str, Any]:
        """Trace2Skill hierarchical merge."""
        return t2s_hierarchical_merge_patches(
            patches, merge_branch=merge_branch
        )

    def skill_mode_gate(
        self, *, mode: str, has_human_skill: bool
    ) -> dict[str, Any]:
        """Trace2Skill deepen vs create gate."""
        return t2s_skill_mode_gate(
            mode=mode, has_human_skill=has_human_skill
        )

    def prefer_parallel_over_sequential(
        self,
        *,
        parallel_quality: float,
        sequential_quality: float,
        parallel_minutes: float,
        sequential_minutes: float,
    ) -> dict[str, Any]:
        """Trace2Skill parallel vs sequential preference."""
        return t2s_prefer_parallel_over_sequential(
            parallel_quality=parallel_quality,
            sequential_quality=sequential_quality,
            parallel_minutes=parallel_minutes,
            sequential_minutes=sequential_minutes,
        )

    def streaming_task_append(
        self,
        memory: Sequence[Mapping[str, Any]],
        *,
        task: str,
        prediction: str = "",
        outcome: str = "unknown",
    ) -> dict[str, Any]:
        """Evo-Memory streaming task append."""
        return evo_streaming_task_append(
            memory, task=task, prediction=prediction, outcome=outcome
        )

    def exprag_retrieve(
        self,
        memory: Sequence[Mapping[str, Any]],
        *,
        query: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """Evo-Memory ExpRAG retrieve."""
        return evo_exprag_retrieve(memory, query=query, top_k=top_k)

    def search_predict_evolve_check(
        self, steps: Sequence[str]
    ) -> dict[str, Any]:
        """Evo-Memory SPE protocol check."""
        return evo_search_predict_evolve_check(steps)

    def evomem_refine_plan(
        self,
        *,
        memory_size: int,
        max_memory: int = 50,
        retrieval_hit: bool = True,
        noisy: bool = False,
    ) -> dict[str, Any]:
        """Evo-Memory ReMem-shaped refine plan."""
        return evo_evomem_refine_plan(
            memory_size=memory_size,
            max_memory=max_memory,
            retrieval_hit=retrieval_hit,
            noisy=noisy,
        )

    def evolution_similarity_hint(
        self,
        *,
        query_tokens: Sequence[str],
        cluster_tokens: Sequence[str],
    ) -> dict[str, Any]:
        """Evo-Memory similarity/reuse hint."""
        return evo_evolution_similarity_hint(
            query_tokens=query_tokens, cluster_tokens=cluster_tokens
        )

    def classify_memory_slot(
        self, *, text: str, has_timestamp: bool = False
    ) -> dict[str, Any]:
        """Mem-α classify core/episodic/semantic."""
        return ma_classify_memory_slot(text=text, has_timestamp=has_timestamp)

    def memory_write_op(
        self,
        *,
        slot: str,
        op: str,
        content: str = "",
        record_id: str | None = None,
    ) -> dict[str, Any]:
        """Mem-α memory write tool validation."""
        return ma_memory_write_op(
            slot=slot, op=op, content=content, record_id=record_id
        )

    def process_chunk_plan(
        self,
        *,
        chunk: str,
        existing_core_chars: int = 0,
        core_max: int = 512,
    ) -> dict[str, Any]:
        """Mem-α chunk processing plan."""
        return ma_process_chunk_plan(
            chunk=chunk,
            existing_core_chars=existing_core_chars,
            core_max=core_max,
        )

    def compression_ratio(
        self, *, memory_chars: int, chunk_chars: int
    ) -> dict[str, Any]:
        """Mem-α compression reward r3."""
        return ma_compression_ratio(
            memory_chars=memory_chars, chunk_chars=chunk_chars
        )

    def memalpha_reward_bundle(
        self,
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
        """Mem-α combined reward bundle."""
        return ma_memalpha_reward_bundle(
            qa_correct=qa_correct,
            qa_total=qa_total,
            tool_success=tool_success,
            tool_total=tool_total,
            memory_chars=memory_chars,
            chunk_chars=chunk_chars,
            content_valid=content_valid,
            content_total=content_total,
            beta=beta,
            gamma=gamma,
        )

    def length_generalization_gate(
        self, *, train_max_tokens: int, eval_tokens: int
    ) -> dict[str, Any]:
        """Mem-α length generalization gate."""
        return ma_length_generalization_gate(
            train_max_tokens=train_max_tokens, eval_tokens=eval_tokens
        )

    def classify_failure(
        self,
        *,
        failure_type: str,
        observation_chars: int = 0,
        severity: float | None = None,
    ) -> dict[str, Any]:
        """AgentHER failure classify."""
        return ah_classify_failure(
            failure_type=failure_type,
            observation_chars=observation_chars,
            severity=severity,
        )

    def extract_replay_outcome(
        self, *, observations: Sequence[str], max_items: int = 5
    ) -> dict[str, Any]:
        """AgentHER replay outcome extract."""
        return ah_extract_replay_outcome(
            observations=observations, max_items=max_items
        )

    def hindsight_relabel_plan(
        self,
        *,
        original_goal: str,
        achievements: Sequence[str],
        confidence: float = 0.85,
        theta: float = 0.7,
    ) -> dict[str, Any]:
        """AgentHER hindsight relabel plan."""
        return ah_hindsight_relabel_plan(
            original_goal=original_goal,
            achievements=achievements,
            confidence=confidence,
            theta=theta,
        )

    def multi_judge_accept(
        self,
        *,
        confidence_j1: float,
        confidence_j2: float,
        theta: float = 0.7,
    ) -> dict[str, Any]:
        """AgentHER multi-judge accept."""
        return ah_multi_judge_accept(
            confidence_j1=confidence_j1,
            confidence_j2=confidence_j2,
            theta=theta,
        )

    def package_training_pair(
        self,
        *,
        format: str,
        hindsight_goal: str,
        original_goal: str,
        trajectory_summary: str = "",
        severity_weight: float = 1.0,
    ) -> dict[str, Any]:
        """AgentHER package SFT/DPO/ShareGPT pair."""
        return ah_package_training_pair(
            format=format,
            hindsight_goal=hindsight_goal,
            original_goal=original_goal,
            trajectory_summary=trajectory_summary,
            severity_weight=severity_weight,
        )

    def distill_planning_error(
        self,
        *,
        error_id: str,
        pattern: str,
        success_hint: str = "",
        failure_hint: str = "",
    ) -> dict[str, Any]:
        """PreFlect distill planning error."""
        return pf_distill_planning_error(
            error_id=error_id,
            pattern=pattern,
            success_hint=success_hint,
            failure_hint=failure_hint,
        )

    def prospective_critique_plan(
        self,
        *,
        plan_steps: Sequence[str],
        planning_errors: Sequence[dict[str, Any]],
    ) -> dict[str, Any]:
        """PreFlect prospective critique."""
        return pf_prospective_critique_plan(
            plan_steps=plan_steps, planning_errors=planning_errors
        )

    def revise_plan_proposal(
        self,
        *,
        original_steps: Sequence[str],
        avoid_patterns: Sequence[str],
        insert_guard: str = "verify precondition",
    ) -> dict[str, Any]:
        """PreFlect revise plan proposal."""
        return pf_revise_plan_proposal(
            original_steps=original_steps,
            avoid_patterns=avoid_patterns,
            insert_guard=insert_guard,
        )

    def replan_on_deviation(
        self,
        *,
        expected_observation: str,
        actual_observation: str,
        remaining_steps: int,
    ) -> dict[str, Any]:
        """PreFlect dynamic re-plan trigger."""
        return pf_replan_on_deviation(
            expected_observation=expected_observation,
            actual_observation=actual_observation,
            remaining_steps=remaining_steps,
        )

    def preflect_before_execute_gate(
        self, *, critique_needs_revise: bool, revised_ready: bool
    ) -> dict[str, Any]:
        """PreFlect execute gate."""
        return pf_preflect_before_execute_gate(
            critique_needs_revise=critique_needs_revise,
            revised_ready=revised_ready,
        )

    def orchestration_action_select(
        self,
        *,
        action_type: str,
        skill_id: str | None = None,
        step: int = 0,
        tmax: int = 20,
    ) -> dict[str, Any]:
        """SkillFlow orchestration action."""
        return sf_orchestration_action_select(
            action_type=action_type,
            skill_id=skill_id,
            step=step,
            tmax=tmax,
        )

    def ttb_residual(
        self,
        *,
        log_forward: float,
        log_backward: float,
        log_reward: float,
        log_z: float = 0.0,
        length: int = 1,
    ) -> dict[str, Any]:
        """SkillFlow TTB residual."""
        return sf_ttb_residual(
            log_forward=log_forward,
            log_backward=log_backward,
            log_reward=log_reward,
            log_z=log_z,
            length=length,
        )

    def step_importance(
        self, *, log_forward: float, log_backward: float
    ) -> dict[str, Any]:
        """SkillFlow step importance I(t)."""
        return sf_step_importance(
            log_forward=log_forward, log_backward=log_backward
        )

    def skill_marginal_flow(
        self,
        *,
        skill_flows: Sequence[float],
        skill_id: str,
        target_index: int = 0,
    ) -> dict[str, Any]:
        """SkillFlow skill marginal flow."""
        return sf_skill_marginal_flow(
            skill_flows=skill_flows,
            skill_id=skill_id,
            target_index=target_index,
        )

    def skill_curation_decide(
        self,
        *,
        mean_log_flow: float,
        centered_log_share: float,
        jensen_gap: float = 0.0,
        high_importance_step: bool = False,
    ) -> dict[str, Any]:
        """SkillFlow skill curation decision."""
        return sf_skill_curation_decide(
            mean_log_flow=mean_log_flow,
            centered_log_share=centered_log_share,
            jensen_gap=jensen_gap,
            high_importance_step=high_importance_step,
        )

    def phase_evolve_gate(
        self,
        *,
        residual_mean: float,
        residual_floor: float,
        plateau_eps: float = 0.05,
    ) -> dict[str, Any]:
        """SkillFlow phase evolve gate."""
        return sf_phase_evolve_gate(
            residual_mean=residual_mean,
            residual_floor=residual_floor,
            plateau_eps=plateau_eps,
        )

    def define_skill_triplet(
        self,
        *,
        skill_id: str,
        activation: str,
        execution: str,
        termination: str,
    ) -> dict[str, Any]:
        """ProcMEM skill triplet."""
        return pm_define_skill_triplet(
            skill_id=skill_id,
            activation=activation,
            execution=execution,
            termination=termination,
        )

    def skill_select_gate(
        self,
        *,
        state_text: str,
        activation: str,
        min_overlap: float = 0.25,
    ) -> dict[str, Any]:
        """ProcMEM skill select gate."""
        return pm_skill_select_gate(
            state_text=state_text,
            activation=activation,
            min_overlap=min_overlap,
        )

    def skill_terminate_check(
        self,
        *,
        observation: str,
        termination: str,
        min_overlap: float = 0.3,
    ) -> dict[str, Any]:
        """ProcMEM skill terminate check."""
        return pm_skill_terminate_check(
            observation=observation,
            termination=termination,
            min_overlap=min_overlap,
        )

    def semantic_gradient_candidate(
        self,
        *,
        success_trace: str,
        failure_trace: str,
        base_skill_id: str,
    ) -> dict[str, Any]:
        """ProcMEM semantic gradient candidate."""
        return pm_semantic_gradient_candidate(
            success_trace=success_trace,
            failure_trace=failure_trace,
            base_skill_id=base_skill_id,
        )

    def ppo_gate_verify(
        self,
        *,
        candidate_score: float,
        incumbent_score: float,
        clip_eps: float = 0.2,
    ) -> dict[str, Any]:
        """ProcMEM PPO Gate verify."""
        return pm_ppo_gate_verify(
            candidate_score=candidate_score,
            incumbent_score=incumbent_score,
            clip_eps=clip_eps,
        )

    def skill_score_maintain(
        self,
        *,
        frequency: int,
        avg_gain: float,
        min_score: float = 0.1,
    ) -> dict[str, Any]:
        """ProcMEM skill score maintain."""
        return pm_skill_score_maintain(
            frequency=frequency,
            avg_gain=avg_gain,
            min_score=min_score,
        )

    def ieu_record(
        self, *, intent: str, experience: str, utility: float = 0.0
    ) -> dict[str, Any]:
        """MemRL Intent-Experience-Utility record."""
        return mr_ieu_record(
            intent=intent, experience=experience, utility=utility
        )

    def two_phase_retrieve(
        self,
        *,
        query: str,
        memories: Sequence[dict[str, Any]],
        top_k_semantic: int = 5,
        top_k_utility: int = 2,
    ) -> dict[str, Any]:
        """MemRL two-phase retrieve."""
        return mr_two_phase_retrieve(
            query=query,
            memories=memories,
            top_k_semantic=top_k_semantic,
            top_k_utility=top_k_utility,
        )

    def utility_q_update(
        self,
        *,
        current_q: float,
        reward: float,
        next_max_q: float = 0.0,
        alpha: float = 0.3,
        gamma: float = 0.9,
    ) -> dict[str, Any]:
        """MemRL utility Q update."""
        return mr_utility_q_update(
            current_q=current_q,
            reward=reward,
            next_max_q=next_max_q,
            alpha=alpha,
            gamma=gamma,
        )

    def value_aware_select(
        self,
        *,
        candidates: Sequence[dict[str, Any]],
        min_utility: float = 0.0,
    ) -> dict[str, Any]:
        """MemRL value-aware select."""
        return mr_value_aware_select(
            candidates=candidates, min_utility=min_utility
        )

    def semantic_vs_utility_warn(
        self,
        *,
        similarity: float,
        utility: float,
        sim_high: float = 0.7,
        util_low: float = 0.1,
    ) -> dict[str, Any]:
        """MemRL similar≠useful warn."""
        return mr_semantic_vs_utility_warn(
            similarity=similarity,
            utility=utility,
            sim_high=sim_high,
            util_low=util_low,
        )

    def distill_principle(
        self,
        *,
        kind: str,
        description: str,
        triples: Sequence[Sequence[str]] | None = None,
    ) -> dict[str, Any]:
        """EvolveR distill principle."""
        return ev_distill_principle(
            kind=kind, description=description, triples=triples
        )

    def principle_dedupe_plan(
        self,
        *,
        candidate_desc: str,
        existing_descs: Sequence[str],
        sim_threshold: float = 0.5,
    ) -> dict[str, Any]:
        """EvolveR principle dedupe plan."""
        return ev_principle_dedupe_plan(
            candidate_desc=candidate_desc,
            existing_descs=existing_descs,
            sim_threshold=sim_threshold,
        )

    def principle_metric_score(
        self,
        *,
        succ_count: int,
        use_count: int,
        prune_threshold: float = 0.2,
    ) -> dict[str, Any]:
        """EvolveR principle metric score."""
        return ev_principle_metric_score(
            succ_count=succ_count,
            use_count=use_count,
            prune_threshold=prune_threshold,
        )

    def search_experience_action(
        self, *, action: str, query: str = ""
    ) -> dict[str, Any]:
        """EvolveR online action gate."""
        return ev_search_experience_action(action=action, query=query)

    def lifecycle_phase_gate(
        self,
        *,
        phase: str,
        mutate_policy: bool = False,
        distill: bool = False,
    ) -> dict[str, Any]:
        """EvolveR lifecycle phase gate."""
        return ev_lifecycle_phase_gate(
            phase=phase, mutate_policy=mutate_policy, distill=distill
        )

    def prune_low_score_principles(
        self, *, scores: Sequence[float], threshold: float = 0.2
    ) -> dict[str, Any]:
        """EvolveR prune low-score principles."""
        return ev_prune_low_score_principles(
            scores=scores, threshold=threshold
        )

    def self_question_task(
        self, *, exploration_summary: str, user_preference: str = ""
    ) -> dict[str, Any]:
        """AgentEvolver self-question task."""
        return ae_self_question_task(
            exploration_summary=exploration_summary,
            user_preference=user_preference,
        )

    def experience_when_content(
        self, *, when_to_use: str, content: str
    ) -> dict[str, Any]:
        """AgentEvolver experience when/content."""
        return ae_experience_when_content(
            when_to_use=when_to_use, content=content
        )

    def mixed_rollout_split(
        self, *, total_rollouts: int, eta: float = 0.5
    ) -> dict[str, Any]:
        """AgentEvolver mixed rollout split."""
        return ae_mixed_rollout_split(
            total_rollouts=total_rollouts, eta=eta
        )

    def attribute_step_credit(
        self, *, step_scores: Sequence[float], outcome_reward: float
    ) -> dict[str, Any]:
        """AgentEvolver attribute step credit."""
        return ae_attribute_step_credit(
            step_scores=step_scores, outcome_reward=outcome_reward
        )

    def curiosity_explore_plan(
        self, *, visited_states: int, novel_states: int, budget: int
    ) -> dict[str, Any]:
        """AgentEvolver curiosity explore plan."""
        return ae_curiosity_explore_plan(
            visited_states=visited_states,
            novel_states=novel_states,
            budget=budget,
        )

    def propose_skill(
        self,
        *,
        description: str,
        kind: str = "procedural",
        existing: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """SkillWeaver propose skill."""
        return sw_propose_skill(
            description=description, kind=kind, existing=existing
        )

    def practice_skill_run(
        self, *, skill_id: str, success: bool, steps: int = 1
    ) -> dict[str, Any]:
        """SkillWeaver practice skill run."""
        return sw_practice_skill_run(
            skill_id=skill_id, success=success, steps=steps
        )

    def distill_skill_api(
        self,
        *,
        skill_id: str,
        description: str,
        params: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """SkillWeaver distill skill API."""
        return sw_distill_skill_api(
            skill_id=skill_id, description=description, params=params
        )

    def hone_skill_api(
        self, *, unit_test_pass: bool, static_ok: bool = True
    ) -> dict[str, Any]:
        """SkillWeaver hone skill API."""
        return sw_hone_skill_api(
            unit_test_pass=unit_test_pass, static_ok=static_ok
        )

    def skill_library_register(
        self, *, api_name: str, library_size: int
    ) -> dict[str, Any]:
        """SkillWeaver skill library register."""
        return sw_skill_library_register(
            api_name=api_name, library_size=library_size
        )

    def transfer_skill_gate(
        self, *, donor_success_rate: float, recipient_baseline: float
    ) -> dict[str, Any]:
        """SkillWeaver transfer skill gate."""
        return sw_transfer_skill_gate(
            donor_success_rate=donor_success_rate,
            recipient_baseline=recipient_baseline,
        )

    def decompose_task_steps(
        self, *, query: str, max_steps: int = 6
    ) -> dict[str, Any]:
        """SkillRoute decompose task steps."""
        return sr_decompose_task_steps(query=query, max_steps=max_steps)

    def retrieve_skills_for_steps(
        self,
        *,
        steps: Sequence[str],
        skill_catalog: Sequence[dict[str, Any]],
        top_m: int = 2,
    ) -> dict[str, Any]:
        """SkillRoute retrieve skills for steps."""
        return sr_retrieve_skills_for_steps(
            steps=steps, skill_catalog=skill_catalog, top_m=top_m
        )

    def compose_skill_dag(
        self, *, step_skills: Sequence[str]
    ) -> dict[str, Any]:
        """SkillRoute compose skill DAG."""
        return sr_compose_skill_dag(step_skills=step_skills)

    def sad_feedback_loop(
        self,
        *,
        prior_steps: Sequence[str],
        hint_skill_names: Sequence[str],
    ) -> dict[str, Any]:
        """SkillRoute SAD feedback loop."""
        return sr_sad_feedback_loop(
            prior_steps=prior_steps, hint_skill_names=hint_skill_names
        )

    def granularity_match_check(
        self, *, step_count: int, expected_skills: int
    ) -> dict[str, Any]:
        """SkillRoute granularity match check."""
        return sr_granularity_match_check(
            step_count=step_count, expected_skills=expected_skills
        )

    def propose_reasoning_task(
        self, *, mode: str, seed_hint: str = ""
    ) -> dict[str, Any]:
        """Absolute Zero propose reasoning task."""
        return az_propose_reasoning_task(mode=mode, seed_hint=seed_hint)

    def validate_task_structure(
        self,
        *,
        has_program: bool,
        has_input: bool,
        has_output: bool,
        mode: str,
    ) -> dict[str, Any]:
        """Absolute Zero validate task structure."""
        return az_validate_task_structure(
            has_program=has_program,
            has_input=has_input,
            has_output=has_output,
            mode=mode,
        )

    def learnability_reward(
        self, *, mean_solve_rate: float
    ) -> dict[str, Any]:
        """Absolute Zero learnability reward."""
        return az_learnability_reward(mean_solve_rate=mean_solve_rate)

    def solve_reward(self, *, answer_match: bool) -> dict[str, Any]:
        """Absolute Zero solve reward."""
        return az_solve_reward(answer_match=answer_match)

    def abszero_joint_objective(
        self,
        *,
        r_propose: float,
        r_solve: float,
        lambda_propose: float = 0.5,
    ) -> dict[str, Any]:
        """Absolute Zero joint objective."""
        return az_abszero_joint_objective(
            r_propose=r_propose,
            r_solve=r_solve,
            lambda_propose=lambda_propose,
        )

    def executor_verify_gate(
        self, *, task_valid: bool, answer_match: bool
    ) -> dict[str, Any]:
        """Absolute Zero executor verify gate."""
        return az_executor_verify_gate(
            task_valid=task_valid, answer_match=answer_match
        )

    def challenger_propose(self, *, question: str) -> dict[str, Any]:
        """R-Zero challenger propose."""
        return rz_challenger_propose(question=question)

    def uncertainty_reward(
        self, *, empirical_accuracy: float
    ) -> dict[str, Any]:
        """R-Zero uncertainty reward."""
        return rz_uncertainty_reward(empirical_accuracy=empirical_accuracy)

    def majority_vote_label(
        self, *, answers: Sequence[str]
    ) -> dict[str, Any]:
        """R-Zero majority vote label."""
        return rz_majority_vote_label(answers=answers)

    def curriculum_band_filter(
        self, *, empirical_accuracy: float, delta: float = 0.2
    ) -> dict[str, Any]:
        """R-Zero curriculum band filter."""
        return rz_curriculum_band_filter(
            empirical_accuracy=empirical_accuracy, delta=delta
        )

    def solver_binary_reward(
        self, *, answer: str, pseudo_label: str
    ) -> dict[str, Any]:
        """R-Zero solver binary reward."""
        return rz_solver_binary_reward(
            answer=answer, pseudo_label=pseudo_label
        )

    def coevolve_round_plan(
        self,
        *,
        round_index: int,
        challenger_updated: bool,
        solver_updated: bool,
    ) -> dict[str, Any]:
        """R-Zero coevolve round plan."""
        return rz_coevolve_round_plan(
            round_index=round_index,
            challenger_updated=challenger_updated,
            solver_updated=solver_updated,
        )

    def write_turn_memory(
        self, *, source_turn_id: str, finding: str
    ) -> dict[str, Any]:
        """ECHO write turn memory."""
        return em_write_turn_memory(
            source_turn_id=source_turn_id, finding=finding
        )

    def select_turn_memories(
        self, *, memory_ids: Sequence[str], budget: int
    ) -> dict[str, Any]:
        """ECHO select turn memories."""
        return em_select_turn_memories(memory_ids=memory_ids, budget=budget)

    def reconstruct_policy_context(
        self,
        *,
        selected_findings: Sequence[str],
        recent_turns: Sequence[str],
        max_chars: int = 400,
    ) -> dict[str, Any]:
        """ECHO reconstruct policy context."""
        return em_reconstruct_policy_context(
            selected_findings=selected_findings,
            recent_turns=recent_turns,
            max_chars=max_chars,
        )

    def provenance_credit_mask(
        self,
        *,
        source_turn_ids: Sequence[str],
        selected_source_ids: Sequence[str],
        outcome_positive: bool,
    ) -> dict[str, Any]:
        """ECHO provenance credit mask."""
        return em_provenance_credit_mask(
            source_turn_ids=source_turn_ids,
            selected_source_ids=selected_source_ids,
            outcome_positive=outcome_positive,
        )

    def history_collapse_gate(
        self, *, collapsed_summary_only: bool
    ) -> dict[str, Any]:
        """ECHO history collapse gate."""
        return em_history_collapse_gate(
            collapsed_summary_only=collapsed_summary_only
        )

    def budget_binding_check(
        self, *, history_chars: int, budget_chars: int
    ) -> dict[str, Any]:
        """ECHO budget binding check."""
        return em_budget_binding_check(
            history_chars=history_chars, budget_chars=budget_chars
        )

    def curriculum_propose_task(
        self, *, task: str, requires_tool: bool = False
    ) -> dict[str, Any]:
        """Agent0 curriculum propose task."""
        return a0_curriculum_propose_task(
            task=task, requires_tool=requires_tool
        )

    def tool_use_reward(
        self, *, tool_call_count: int, gamma: float = 0.25, cap: int = 4
    ) -> dict[str, Any]:
        """Agent0 tool use reward."""
        return a0_tool_use_reward(
            tool_call_count=tool_call_count, gamma=gamma, cap=cap
        )

    def curriculum_reward(
        self,
        *,
        r_uncertainty: float,
        r_tool: float,
        r_repetition: float = 0.0,
        lambda_unc: float = 0.5,
        lambda_tool: float = 0.6,
        format_ok: bool = True,
    ) -> dict[str, Any]:
        """Agent0 curriculum reward."""
        return a0_curriculum_reward(
            r_uncertainty=r_uncertainty,
            r_tool=r_tool,
            r_repetition=r_repetition,
            lambda_unc=lambda_unc,
            lambda_tool=lambda_tool,
            format_ok=format_ok,
        )

    def executor_frontier_filter(
        self,
        *,
        self_consistency: float,
        low: float = 0.3,
        high: float = 0.8,
    ) -> dict[str, Any]:
        """Agent0 executor frontier filter."""
        return a0_executor_frontier_filter(
            self_consistency=self_consistency, low=low, high=high
        )

    def tool_aware_pressure(
        self,
        *,
        executor_tool_success_rate: float,
        prior_task_complexity: float,
    ) -> dict[str, Any]:
        """Agent0 tool-aware curriculum pressure."""
        return a0_tool_aware_pressure(
            executor_tool_success_rate=executor_tool_success_rate,
            prior_task_complexity=prior_task_complexity,
        )

    def symbiotic_round_plan(
        self,
        *,
        round_index: int,
        curriculum_updated: bool,
        executor_updated: bool,
    ) -> dict[str, Any]:
        """Agent0 symbiotic round plan."""
        return a0_symbiotic_round_plan(
            round_index=round_index,
            curriculum_updated=curriculum_updated,
            executor_updated=executor_updated,
        )

    def mae_propose_question(self, *, question: str) -> dict[str, Any]:
        """MAE propose question."""
        return mae_propose_question_fn(question=question)

    def mae_solve_attempt(self, *, answer: str) -> dict[str, Any]:
        """MAE solve attempt."""
        return mae_solve_attempt_fn(answer=answer)

    def mae_judge_score(
        self, *, quality_score: float, correctness_score: float
    ) -> dict[str, Any]:
        """MAE judge score."""
        return mae_judge_score_fn(
            quality_score=quality_score,
            correctness_score=correctness_score,
        )

    def mae_proposer_reward(
        self,
        *,
        quality_score: float,
        solver_failed: bool,
        difficulty_weight: float = 0.5,
    ) -> dict[str, Any]:
        """MAE proposer reward."""
        return mae_proposer_reward_fn(
            quality_score=quality_score,
            solver_failed=solver_failed,
            difficulty_weight=difficulty_weight,
        )

    def mae_quality_filter(
        self, *, quality_score: float, min_quality: float = 0.5
    ) -> dict[str, Any]:
        """MAE quality filter."""
        return mae_quality_filter_fn(
            quality_score=quality_score, min_quality=min_quality
        )

    def mae_triad_round_plan(
        self, *, round_index: int, phase: str
    ) -> dict[str, Any]:
        """MAE triad round plan."""
        return mae_triad_round_plan_fn(
            round_index=round_index, phase=phase
        )

    def sage_challenge_task(
        self, *, task: str, difficulty: float = 0.5
    ) -> dict[str, Any]:
        """SAGE challenge task."""
        return sage_challenge_task_fn(task=task, difficulty=difficulty)

    def sage_plan_steps(self, *, steps: Sequence[str]) -> dict[str, Any]:
        """SAGE plan steps."""
        return sage_plan_steps_fn(steps=steps)

    def sage_solve_with_plan(
        self,
        *,
        plan_step_count: int,
        followed_steps: int,
        answer: str,
    ) -> dict[str, Any]:
        """SAGE solve with plan."""
        return sage_solve_with_plan_fn(
            plan_step_count=plan_step_count,
            followed_steps=followed_steps,
            answer=answer,
        )

    def sage_critic_filter(
        self,
        *,
        question_score: float,
        plan_score: float,
        min_score: float = 0.5,
    ) -> dict[str, Any]:
        """SAGE critic filter."""
        return sage_critic_filter_fn(
            question_score=question_score,
            plan_score=plan_score,
            min_score=min_score,
        )

    def sage_drift_gate(
        self, *, difficulty_delta: float, max_delta: float = 0.3
    ) -> dict[str, Any]:
        """SAGE curriculum drift gate."""
        return sage_drift_gate_fn(
            difficulty_delta=difficulty_delta, max_delta=max_delta
        )

    def sage_closed_loop_round(
        self, *, round_index: int, phase: str
    ) -> dict[str, Any]:
        """SAGE closed loop round."""
        return sage_closed_loop_round_fn(
            round_index=round_index, phase=phase
        )

    def memory_trigger_decide(
        self,
        *,
        at_boundary: bool,
        uncertainty: float,
        threshold: float = 0.4,
    ) -> dict[str, Any]:
        """MemGen memory trigger decide."""
        return mg_memory_trigger_decide(
            at_boundary=at_boundary,
            uncertainty=uncertainty,
            threshold=threshold,
        )

    def weave_latent_memory(
        self, *, stimulus: str, token_budget: int = 4
    ) -> dict[str, Any]:
        """MemGen weave latent memory."""
        return mg_weave_latent_memory(
            stimulus=stimulus, token_budget=token_budget
        )

    def interweave_cycle_plan(self, *, step: str) -> dict[str, Any]:
        """MemGen interweave cycle plan."""
        return mg_interweave_cycle_plan(step=step)

    def faculty_classify(self, *, faculty: str) -> dict[str, Any]:
        """MemGen faculty classify."""
        return mg_faculty_classify(faculty=faculty)

    def weaver_only_update_gate(
        self, *, reasoner_frozen: bool, weaver_updated: bool
    ) -> dict[str, Any]:
        """MemGen weaver-only update gate."""
        return mg_weaver_only_update_gate(
            reasoner_frozen=reasoner_frozen,
            weaver_updated=weaver_updated,
        )

    def sparse_invoke_penalty(
        self,
        *,
        invoke_count: int,
        expected_rate: float = 0.2,
        lambda_penalty: float = 0.1,
    ) -> dict[str, Any]:
        """MemGen sparse invoke penalty."""
        return mg_sparse_invoke_penalty(
            invoke_count=invoke_count,
            expected_rate=expected_rate,
            lambda_penalty=lambda_penalty,
        )

    def text_experience_store(
        self, *, kind: str, content: str
    ) -> dict[str, Any]:
        """Metis text experience store."""
        return mt_text_experience_store(kind=kind, content=content)

    def crystallize_plan_to_tool(
        self, *, plan_id: str, reuse_count: int, min_reuse: int = 3
    ) -> dict[str, Any]:
        """Metis crystallize plan to tool."""
        return mt_crystallize_plan_to_tool(
            plan_id=plan_id,
            reuse_count=reuse_count,
            min_reuse=min_reuse,
        )

    def dual_retrieve(
        self,
        *,
        text_hits: Sequence[str],
        code_tool_ids: Sequence[str],
    ) -> dict[str, Any]:
        """Metis dual retrieve."""
        return mt_dual_retrieve(
            text_hits=text_hits, code_tool_ids=code_tool_ids
        )

    def representation_tradeoff(
        self,
        *,
        construction_cost: float,
        execution_efficiency: float,
        transferability: float,
    ) -> dict[str, Any]:
        """Metis representation tradeoff."""
        return mt_representation_tradeoff(
            construction_cost=construction_cost,
            execution_efficiency=execution_efficiency,
            transferability=transferability,
        )

    def promote_kind_gate(self, *, kind: str) -> dict[str, Any]:
        """Metis promote kind gate."""
        return mt_promote_kind_gate(kind=kind)

    def metis_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Metis loop plan."""
        return mt_metis_loop_plan(phase=phase)

    def single_trajectory_reflect(
        self, *, trajectory_id: str, error_note: str
    ) -> dict[str, Any]:
        """SAMULE single trajectory reflect."""
        return sa_single_trajectory_reflect(
            trajectory_id=trajectory_id, error_note=error_note
        )

    def intra_task_taxonomy(
        self, *, error_labels: Sequence[str]
    ) -> dict[str, Any]:
        """SAMULE intra-task taxonomy."""
        return sa_intra_task_taxonomy(error_labels=error_labels)

    def inter_task_transfer(
        self, *, error_type: str, strategy: str
    ) -> dict[str, Any]:
        """SAMULE inter-task transfer."""
        return sa_inter_task_transfer(
            error_type=error_type, strategy=strategy
        )

    def foresight_reflect(
        self, *, predicted: str, actual: str
    ) -> dict[str, Any]:
        """SAMULE foresight reflect."""
        return sa_foresight_reflect(predicted=predicted, actual=actual)

    def failure_centric_gate(
        self, *, success_count: int, failure_count: int
    ) -> dict[str, Any]:
        """SAMULE failure-centric gate."""
        return sa_failure_centric_gate(
            success_count=success_count, failure_count=failure_count
        )

    def merge_reflections(
        self, *, levels_present: Sequence[str]
    ) -> dict[str, Any]:
        """SAMULE merge reflections."""
        return sa_merge_reflections(levels_present=levels_present)

    def experience_bank_record(
        self, *, experience: str, weight: float = 1.0
    ) -> dict[str, Any]:
        """LIVE-EVO experience bank record."""
        return le_experience_bank_record(
            experience=experience, weight=weight
        )

    def meta_guideline_record(self, *, guideline: str) -> dict[str, Any]:
        """LIVE-EVO meta guideline record."""
        return le_meta_guideline_record(guideline=guideline)

    def compile_task_guideline(
        self, *, task: str, experience_count: int, has_meta: bool
    ) -> dict[str, Any]:
        """LIVE-EVO compile task guideline."""
        return le_compile_task_guideline(
            task=task,
            experience_count=experience_count,
            has_meta=has_meta,
        )

    def update_experience_weight(
        self,
        *,
        weight: float,
        delta_on_minus_off: float,
        lr: float = 0.1,
    ) -> dict[str, Any]:
        """LIVE-EVO update experience weight."""
        return le_update_experience_weight(
            weight=weight,
            delta_on_minus_off=delta_on_minus_off,
            lr=lr,
        )

    def forget_stale_experience(
        self, *, weight: float, min_weight: float = 0.05
    ) -> dict[str, Any]:
        """LIVE-EVO forget stale experience."""
        return le_forget_stale_experience(
            weight=weight, min_weight=min_weight
        )

    def liveevo_online_round(self, *, phase: str) -> dict[str, Any]:
        """LIVE-EVO online round."""
        return le_liveevo_online_round(phase=phase)

    def socratic_teacher_craft(
        self, *, weakness: str, question: str
    ) -> dict[str, Any]:
        """Socratic-Zero teacher craft."""
        return so_socratic_teacher_craft(
            weakness=weakness, question=question
        )

    def socratic_solver_preference(
        self, *, success: bool, failed: bool
    ) -> dict[str, Any]:
        """Socratic-Zero solver preference."""
        return so_socratic_solver_preference(
            success=success, failed=failed
        )

    def socratic_generator_distill(
        self, *, teacher_strategy: str
    ) -> dict[str, Any]:
        """Socratic-Zero generator distill."""
        return so_socratic_generator_distill(
            teacher_strategy=teacher_strategy
        )

    def socratic_seed_bootstrap(
        self, *, seed_count: int, min_seeds: int = 100
    ) -> dict[str, Any]:
        """Socratic-Zero seed bootstrap."""
        return so_socratic_seed_bootstrap(
            seed_count=seed_count, min_seeds=min_seeds
        )

    def socratic_weakness_target(
        self, *, fail_rate: float, threshold: float = 0.4
    ) -> dict[str, Any]:
        """Socratic-Zero weakness target."""
        return so_socratic_weakness_target(
            fail_rate=fail_rate, threshold=threshold
        )

    def socratic_closed_loop(self, *, phase: str) -> dict[str, Any]:
        """Socratic-Zero closed loop."""
        return so_socratic_closed_loop(phase=phase)

    def spiral_self_play_match(
        self, *, game: str, role: str, won: bool
    ) -> dict[str, Any]:
        """SPIRAL self-play match."""
        return sp_spiral_self_play_match(game=game, role=role, won=won)

    def spiral_rae_advantage(
        self, *, reward: float, role_baseline: float
    ) -> dict[str, Any]:
        """SPIRAL RAE advantage."""
        return sp_spiral_rae_advantage(
            reward=reward, role_baseline=role_baseline
        )

    def spiral_baseline_ema(
        self, *, baseline: float, reward: float, decay: float = 0.95
    ) -> dict[str, Any]:
        """SPIRAL baseline EMA."""
        return sp_spiral_baseline_ema(
            baseline=baseline, reward=reward, decay=decay
        )

    def spiral_transfer_pattern(self, *, pattern: str) -> dict[str, Any]:
        """SPIRAL transfer pattern."""
        return sp_spiral_transfer_pattern(pattern=pattern)

    def spiral_opponent_strength(
        self, *, self_elo: float, opponent_elo: float
    ) -> dict[str, Any]:
        """SPIRAL opponent strength."""
        return sp_spiral_opponent_strength(
            self_elo=self_elo, opponent_elo=opponent_elo
        )

    def spiral_multi_game_plan(self, *, phase: str) -> dict[str, Any]:
        """SPIRAL multi-game plan."""
        return sp_spiral_multi_game_plan(phase=phase)

    def smith_store_memory(
        self, *, tier: str, content: str
    ) -> dict[str, Any]:
        """SMITH store memory."""
        return sm_smith_store_memory(tier=tier, content=content)

    def smith_create_tool(
        self, *, tool_name: str, sandbox_pass: bool
    ) -> dict[str, Any]:
        """SMITH create tool."""
        return sm_smith_create_tool(
            tool_name=tool_name, sandbox_pass=sandbox_pass
        )

    def smith_retrieve_episode(
        self, *, similarity: float, threshold: float = 0.5
    ) -> dict[str, Any]:
        """SMITH retrieve episode."""
        return sm_smith_retrieve_episode(
            similarity=similarity, threshold=threshold
        )

    def smith_curriculum_difficulty(
        self, *, ensemble_fail_rate: float
    ) -> dict[str, Any]:
        """SMITH curriculum difficulty."""
        return sm_smith_curriculum_difficulty(
            ensemble_fail_rate=ensemble_fail_rate
        )

    def smith_tool_reuse_gate(
        self, *, tool_exists: bool, task_similar: bool
    ) -> dict[str, Any]:
        """SMITH tool reuse gate."""
        return sm_smith_tool_reuse_gate(
            tool_exists=tool_exists, task_similar=task_similar
        )

    def smith_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SMITH loop plan."""
        return sm_smith_loop_plan(phase=phase)

    def hmem_leaf_event(
        self, *, topic: str, timestamp: str
    ) -> dict[str, Any]:
        """H-Mem leaf event."""
        return hm_hmem_leaf_event(topic=topic, timestamp=timestamp)

    def hmem_consolidate_nodes(
        self,
        *,
        time_gap: float,
        max_gap: float = 1.0,
        same_topic: bool,
    ) -> dict[str, Any]:
        """H-Mem consolidate nodes."""
        return hm_hmem_consolidate_nodes(
            time_gap=time_gap, max_gap=max_gap, same_topic=same_topic
        )

    def hmem_link_entities(
        self, *, entity_a: str, entity_b: str, relation: str
    ) -> dict[str, Any]:
        """H-Mem link entities."""
        return hm_hmem_link_entities(
            entity_a=entity_a, entity_b=entity_b, relation=relation
        )

    def hmem_decompose_query(
        self, *, sub_queries: Sequence[str]
    ) -> dict[str, Any]:
        """H-Mem decompose query."""
        return hm_hmem_decompose_query(sub_queries=sub_queries)

    def hmem_hybrid_retrieve(
        self, *, tree_hits: int, graph_hops: int
    ) -> dict[str, Any]:
        """H-Mem hybrid retrieve."""
        return hm_hmem_hybrid_retrieve(
            tree_hits=tree_hits, graph_hops=graph_hops
        )

    def hmem_evolution_gate(
        self, *, short_term_count: int, consolidated_count: int
    ) -> dict[str, Any]:
        """H-Mem evolution gate."""
        return hm_hmem_evolution_gate(
            short_term_count=short_term_count,
            consolidated_count=consolidated_count,
        )

    def himem_segment_episode(
        self,
        *,
        topic: str,
        surprise: float,
        surprise_threshold: float = 0.5,
    ) -> dict[str, Any]:
        """HiMem segment episode."""
        return hi_himem_segment_episode(
            topic=topic,
            surprise=surprise,
            surprise_threshold=surprise_threshold,
        )

    def himem_extract_note(self, *, knowledge: str) -> dict[str, Any]:
        """HiMem extract note."""
        return hi_himem_extract_note(knowledge=knowledge)

    def himem_link_episode_note(
        self, *, episode_id: str, note_id: str
    ) -> dict[str, Any]:
        """HiMem link episode note."""
        return hi_himem_link_episode_note(
            episode_id=episode_id, note_id=note_id
        )

    def himem_retrieve_strategy(
        self, *, mode: str, note_hit: bool
    ) -> dict[str, Any]:
        """HiMem retrieve strategy."""
        return hi_himem_retrieve_strategy(mode=mode, note_hit=note_hit)

    def himem_reconsolidate(
        self, *, conflict: bool, missing_knowledge: bool
    ) -> dict[str, Any]:
        """HiMem reconsolidate."""
        return hi_himem_reconsolidate(
            conflict=conflict, missing_knowledge=missing_knowledge
        )

    def himem_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HiMem loop plan."""
        return hi_himem_loop_plan(phase=phase)

    def hmeml_store_level(
        self, *, level: str, content: str
    ) -> dict[str, Any]:
        """H-MEM store level."""
        return hl_hmeml_store_level(level=level, content=content)

    def hmeml_route_query(self, *, start_level: str) -> dict[str, Any]:
        """H-MEM route query."""
        return hl_hmeml_route_query(start_level=start_level)

    def hmeml_descend(
        self, *, current_level: str, hit: bool
    ) -> dict[str, Any]:
        """H-MEM descend."""
        return hl_hmeml_descend(current_level=current_level, hit=hit)

    def hmeml_parent_link(
        self, *, parent_level: str, child_level: str
    ) -> dict[str, Any]:
        """H-MEM parent link."""
        return hl_hmeml_parent_link(
            parent_level=parent_level, child_level=child_level
        )

    def hmeml_efficiency_score(
        self, *, levels_scanned: int, max_levels: int = 4
    ) -> dict[str, Any]:
        """H-MEM efficiency score."""
        return hl_hmeml_efficiency_score(
            levels_scanned=levels_scanned, max_levels=max_levels
        )

    def hmeml_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """H-MEM loop plan."""
        return hl_hmeml_loop_plan(phase=phase)

    def hyperskill_add_subtask(self, *, label: str) -> dict[str, Any]:
        """HyperSkill add subtask."""
        return hs_hyperskill_add_subtask(label=label)

    def hyperskill_add_skill(self, *, label: str) -> dict[str, Any]:
        """HyperSkill add skill."""
        return hs_hyperskill_add_skill(label=label)

    def hyperskill_add_hyperedge(
        self,
        *,
        subtask_ids: list[str],
        skill_ids: list[str],
        utility: float,
    ) -> dict[str, Any]:
        """HyperSkill add hyperedge."""
        return hs_hyperskill_add_hyperedge(
            subtask_ids=subtask_ids,
            skill_ids=skill_ids,
            utility=utility,
        )

    def hyperskill_dual_path_retrieve(
        self, *, subtask_hits: int, trajectory_hits: int
    ) -> dict[str, Any]:
        """HyperSkill dual-path retrieve."""
        return hs_hyperskill_dual_path_retrieve(
            subtask_hits=subtask_hits, trajectory_hits=trajectory_hits
        )

    def hyperskill_rank_skills(
        self, *, cooccurrence: int, utility: float
    ) -> dict[str, Any]:
        """HyperSkill rank skills."""
        return hs_hyperskill_rank_skills(
            cooccurrence=cooccurrence, utility=utility
        )

    def hyperskill_maintain_plan(
        self,
        *,
        utility: float,
        prune_below: float = 0.2,
        redundant: bool = False,
    ) -> dict[str, Any]:
        """HyperSkill maintain plan."""
        return hs_hyperskill_maintain_plan(
            utility=utility,
            prune_below=prune_below,
            redundant=redundant,
        )

    def hyperskill_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HyperSkill loop plan."""
        return hs_hyperskill_loop_plan(phase=phase)

    def dcpm_day_write(
        self, *, belief: str, superseded_id: str | None = None
    ) -> dict[str, Any]:
        """DCPM day write."""
        return dc_dcpm_day_write(
            belief=belief, superseded_id=superseded_id
        )

    def dcpm_supersedes_chain(self, *, chain_len: int) -> dict[str, Any]:
        """DCPM supersedes chain."""
        return dc_dcpm_supersedes_chain(chain_len=chain_len)

    def dcpm_night_induce(
        self, *, fact_cluster_size: int, min_cluster: int = 3
    ) -> dict[str, Any]:
        """DCPM night induce."""
        return dc_dcpm_night_induce(
            fact_cluster_size=fact_cluster_size, min_cluster=min_cluster
        )

    def dcpm_cross_domain_collision(
        self,
        *,
        behavioral_similarity: float,
        semantic_similarity: float,
        behavior_threshold: float = 0.7,
        semantic_max: float = 0.3,
    ) -> dict[str, Any]:
        """DCPM cross-domain collision."""
        return dc_dcpm_cross_domain_collision(
            behavioral_similarity=behavioral_similarity,
            semantic_similarity=semantic_similarity,
            behavior_threshold=behavior_threshold,
            semantic_max=semantic_max,
        )

    def dcpm_hierarchy_level(self, *, level: str) -> dict[str, Any]:
        """DCPM hierarchy level."""
        return dc_dcpm_hierarchy_level(level=level)

    def dcpm_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """DCPM loop plan."""
        return dc_dcpm_loop_plan(phase=phase)

    def memos_create_cube(
        self, *, kind: str, content: str
    ) -> dict[str, Any]:
        """MemOS create cube."""
        return mo_memos_create_cube(kind=kind, content=content)

    def memos_schedule(
        self, *, strategy: str, candidate_count: int
    ) -> dict[str, Any]:
        """MemOS schedule."""
        return mo_memos_schedule(
            strategy=strategy, candidate_count=candidate_count
        )

    def memos_lifecycle(
        self, *, state: str, action: str
    ) -> dict[str, Any]:
        """MemOS lifecycle."""
        return mo_memos_lifecycle(state=state, action=action)

    def memos_compose(self, *, cube_ids: list[str]) -> dict[str, Any]:
        """MemOS compose."""
        return mo_memos_compose(cube_ids=cube_ids)

    def memos_migrate(
        self, *, from_kind: str, to_kind: str
    ) -> dict[str, Any]:
        """MemOS migrate."""
        return mo_memos_migrate(from_kind=from_kind, to_kind=to_kind)

    def memos_fuse_gate(
        self, *, compatible: bool, conflict: bool
    ) -> dict[str, Any]:
        """MemOS fuse gate."""
        return mo_memos_fuse_gate(
            compatible=compatible, conflict=conflict
        )

    def memos_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemOS loop plan."""
        return mo_memos_loop_plan(phase=phase)

    def skillcraft_save_skill(
        self, *, name: str, steps: int, verified: bool
    ) -> dict[str, Any]:
        """SkillCraft save skill."""
        return sc_skillcraft_save_skill(
            name=name, steps=steps, verified=verified
        )

    def skillcraft_get_skill(self, *, skill_id: str) -> dict[str, Any]:
        """SkillCraft get skill."""
        return sc_skillcraft_get_skill(skill_id=skill_id)

    def skillcraft_list_skills(
        self, *, library_size: int
    ) -> dict[str, Any]:
        """SkillCraft list skills."""
        return sc_skillcraft_list_skills(library_size=library_size)

    def skillcraft_execute_skill(
        self, *, skill_exists: bool, params_ok: bool
    ) -> dict[str, Any]:
        """SkillCraft execute skill."""
        return sc_skillcraft_execute_skill(
            skill_exists=skill_exists, params_ok=params_ok
        )

    def skillcraft_verify_skill(
        self,
        *,
        syntax_ok: bool,
        runtime_ok: bool,
        nonempty_output: bool,
    ) -> dict[str, Any]:
        """SkillCraft verify skill."""
        return sc_skillcraft_verify_skill(
            syntax_ok=syntax_ok,
            runtime_ok=runtime_ok,
            nonempty_output=nonempty_output,
        )

    def skillcraft_token_efficiency(
        self, *, tokens_baseline: int, tokens_skill_mode: int
    ) -> dict[str, Any]:
        """SkillCraft token efficiency."""
        return sc_skillcraft_token_efficiency(
            tokens_baseline=tokens_baseline,
            tokens_skill_mode=tokens_skill_mode,
        )

    def skillcraft_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SkillCraft loop plan."""
        return sc_skillcraft_loop_plan(phase=phase)

    def cma_persist(self, *, content: str) -> dict[str, Any]:
        """CMA persist."""
        return cm_cma_persist(content=content)

    def cma_selective_retain(
        self, *, utility: float, retain_threshold: float = 0.4
    ) -> dict[str, Any]:
        """CMA selective retain."""
        return cm_cma_selective_retain(
            utility=utility, retain_threshold=retain_threshold
        )

    def cma_associative_route(
        self, *, cue: str, hop_budget: int = 2
    ) -> dict[str, Any]:
        """CMA associative route."""
        return cm_cma_associative_route(cue=cue, hop_budget=hop_budget)

    def cma_temporal_chain(
        self, *, event_a: str, event_b: str, order_ok: bool
    ) -> dict[str, Any]:
        """CMA temporal chain."""
        return cm_cma_temporal_chain(
            event_a=event_a, event_b=event_b, order_ok=order_ok
        )

    def cma_consolidate(
        self, *, episode_count: int, min_episodes: int = 2
    ) -> dict[str, Any]:
        """CMA consolidate."""
        return cm_cma_consolidate(
            episode_count=episode_count, min_episodes=min_episodes
        )

    def cma_probe_gate(
        self, *, probe: str, supports_mutation: bool
    ) -> dict[str, Any]:
        """CMA probe gate."""
        return cm_cma_probe_gate(
            probe=probe, supports_mutation=supports_mutation
        )

    def cma_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CMA loop plan."""
        return cm_cma_loop_plan(phase=phase)

    def agentfold_workspace_split(
        self, *, working_tokens: int, long_term_blocks: int
    ) -> dict[str, Any]:
        """AgentFold workspace split."""
        return af_agentfold_workspace_split(
            working_tokens=working_tokens,
            long_term_blocks=long_term_blocks,
        )

    def agentfold_fold_command(
        self, *, mode: str, range_start: int, step_t: int
    ) -> dict[str, Any]:
        """AgentFold fold command."""
        return af_agentfold_fold_command(
            mode=mode, range_start=range_start, step_t=step_t
        )

    def agentfold_granular_condense(
        self, *, last_step_tokens: int, target_tokens: int
    ) -> dict[str, Any]:
        """AgentFold granular condense."""
        return af_agentfold_granular_condense(
            last_step_tokens=last_step_tokens, target_tokens=target_tokens
        )

    def agentfold_deep_consolidate(
        self, *, blocks_merged: int
    ) -> dict[str, Any]:
        """AgentFold deep consolidate."""
        return af_agentfold_deep_consolidate(blocks_merged=blocks_merged)

    def agentfold_context_budget(
        self, *, turns: int, tokens: int, soft_cap: int = 7000
    ) -> dict[str, Any]:
        """AgentFold context budget."""
        return af_agentfold_context_budget(
            turns=turns, tokens=tokens, soft_cap=soft_cap
        )

    def agentfold_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AgentFold loop plan."""
        return af_agentfold_loop_plan(phase=phase)

    def memengine_register_function(self, *, name: str) -> dict[str, Any]:
        """MemEngine register function."""
        return me_memengine_register_function(name=name)

    def memengine_compose_operation(
        self, *, op: str, function_ids: list[str]
    ) -> dict[str, Any]:
        """MemEngine compose operation."""
        return me_memengine_compose_operation(
            op=op, function_ids=function_ids
        )

    def memengine_bind_model(
        self, *, model_name: str, operation_ids: list[str]
    ) -> dict[str, Any]:
        """MemEngine bind model."""
        return me_memengine_bind_model(
            model_name=model_name, operation_ids=operation_ids
        )

    def memengine_config_set(
        self, *, key: str, value: str
    ) -> dict[str, Any]:
        """MemEngine config set."""
        return me_memengine_config_set(key=key, value=value)

    def memengine_reflect_plan(
        self, *, entries: int, min_entries: int = 2
    ) -> dict[str, Any]:
        """MemEngine reflect plan."""
        return me_memengine_reflect_plan(
            entries=entries, min_entries=min_entries
        )

    def memengine_pluggable(
        self, *, agent_compatible: bool
    ) -> dict[str, Any]:
        """MemEngine pluggable."""
        return me_memengine_pluggable(agent_compatible=agent_compatible)

    def memengine_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemEngine loop plan."""
        return me_memengine_loop_plan(phase=phase)

    def simplemem_compress(
        self, *, raw_turns: int, window: int = 20
    ) -> dict[str, Any]:
        """SimpleMem compress."""
        return sm_simplemem_compress(raw_turns=raw_turns, window=window)

    def simplemem_synthesize(
        self, *, related_facts: int, min_related: int = 2
    ) -> dict[str, Any]:
        """SimpleMem synthesize."""
        return sm_simplemem_synthesize(
            related_facts=related_facts, min_related=min_related
        )

    def simplemem_intent_scope(self, *, complexity: str) -> dict[str, Any]:
        """SimpleMem intent scope."""
        return sm_simplemem_intent_scope(complexity=complexity)

    def simplemem_multiview_index(
        self, *, dense: bool, sparse: bool, metadata: bool
    ) -> dict[str, Any]:
        """SimpleMem multiview index."""
        return sm_simplemem_multiview_index(
            dense=dense, sparse=sparse, metadata=metadata
        )

    def simplemem_token_ratio(
        self, *, tokens_baseline: int, tokens_simplemem: int
    ) -> dict[str, Any]:
        """SimpleMem token ratio."""
        return sm_simplemem_token_ratio(
            tokens_baseline=tokens_baseline,
            tokens_simplemem=tokens_simplemem,
        )

    def simplemem_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SimpleMem loop plan."""
        return sm_simplemem_loop_plan(phase=phase)

    def omem_extract_persona(
        self, *, trait: str, confidence: float
    ) -> dict[str, Any]:
        """O-Mem extract persona."""
        return om_omem_extract_persona(trait=trait, confidence=confidence)

    def omem_update_event(
        self, *, event: str, timestamp: str
    ) -> dict[str, Any]:
        """O-Mem update event."""
        return om_omem_update_event(event=event, timestamp=timestamp)

    def omem_hierarchy_retrieve(
        self, *, channel: str, hits: int
    ) -> dict[str, Any]:
        """O-Mem hierarchy retrieve."""
        return om_omem_hierarchy_retrieve(channel=channel, hits=hits)

    def omem_profile_gate(
        self, *, confidence: float, min_confidence: float = 0.5
    ) -> dict[str, Any]:
        """O-Mem profile gate."""
        return om_omem_profile_gate(
            confidence=confidence, min_confidence=min_confidence
        )

    def omem_scale_memory_time(
        self, *, interactions: int, memory_units: int
    ) -> dict[str, Any]:
        """O-Mem scale memory time."""
        return om_omem_scale_memory_time(
            interactions=interactions, memory_units=memory_units
        )

    def omem_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """O-Mem loop plan."""
        return om_omem_loop_plan(phase=phase)

    def mandol_basic_unit(self, *, content: str) -> dict[str, Any]:
        """Mandol basic unit."""
        return md_mandol_basic_unit(content=content)

    def mandol_agglomerate(
        self, *, basic_ids: list[str]
    ) -> dict[str, Any]:
        """Mandol agglomerate."""
        return md_mandol_agglomerate(basic_ids=basic_ids)

    def mandol_semantic_map_put(
        self, *, key: str, vector_ok: bool
    ) -> dict[str, Any]:
        """Mandol semantic map put."""
        return md_mandol_semantic_map_put(key=key, vector_ok=vector_ok)

    def mandol_hybrid_retrieve(
        self, *, vector_hits: int, graph_hops: int
    ) -> dict[str, Any]:
        """Mandol hybrid retrieve."""
        return md_mandol_hybrid_retrieve(
            vector_hits=vector_hits, graph_hops=graph_hops
        )

    def mandol_query_route(self, *, query_type: str) -> dict[str, Any]:
        """Mandol query route."""
        return md_mandol_query_route(query_type=query_type)

    def mandol_token_budget(
        self, *, selected_tokens: int, max_tokens: int
    ) -> dict[str, Any]:
        """Mandol token budget."""
        return md_mandol_token_budget(
            selected_tokens=selected_tokens, max_tokens=max_tokens
        )

    def mandol_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Mandol loop plan."""
        return md_mandol_loop_plan(phase=phase)

    def memanto_store_typed(
        self, *, category: str, content: str
    ) -> dict[str, Any]:
        """Memanto store typed."""
        return ma_memanto_store_typed(category=category, content=content)

    def memanto_conflict_resolve(
        self, *, conflict: bool, newer_wins: bool
    ) -> dict[str, Any]:
        """Memanto conflict resolve."""
        return ma_memanto_conflict_resolve(
            conflict=conflict, newer_wins=newer_wins
        )

    def memanto_version(
        self, *, entry_id: str, version: int
    ) -> dict[str, Any]:
        """Memanto version."""
        return ma_memanto_version(entry_id=entry_id, version=version)

    def memanto_retrieve(
        self, *, query: str, single_query: bool = True
    ) -> dict[str, Any]:
        """Memanto retrieve."""
        return ma_memanto_retrieve(query=query, single_query=single_query)

    def memanto_latency_gate(
        self, *, latency_ms: float, soft_cap_ms: float = 90.0
    ) -> dict[str, Any]:
        """Memanto latency gate."""
        return ma_memanto_latency_gate(
            latency_ms=latency_ms, soft_cap_ms=soft_cap_ms
        )

    def memanto_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Memanto loop plan."""
        return ma_memanto_loop_plan(phase=phase)

    def zep_add_episode(
        self, *, content: str, valid_at: str
    ) -> dict[str, Any]:
        """Zep add episode."""
        return zp_zep_add_episode(content=content, valid_at=valid_at)

    def zep_link_entities(
        self, *, entity_a: str, entity_b: str, relation: str
    ) -> dict[str, Any]:
        """Zep link entities."""
        return zp_zep_link_entities(
            entity_a=entity_a, entity_b=entity_b, relation=relation
        )

    def zep_bitemporal(
        self, *, valid_at: str, transaction_at: str
    ) -> dict[str, Any]:
        """Zep bitemporal."""
        return zp_zep_bitemporal(
            valid_at=valid_at, transaction_at=transaction_at
        )

    def zep_synthesize(
        self, *, conversation_facts: int, business_facts: int
    ) -> dict[str, Any]:
        """Zep synthesize."""
        return zp_zep_synthesize(
            conversation_facts=conversation_facts,
            business_facts=business_facts,
        )

    def zep_cross_session(
        self, *, sessions: int, min_sessions: int = 2
    ) -> dict[str, Any]:
        """Zep cross session."""
        return zp_zep_cross_session(
            sessions=sessions, min_sessions=min_sessions
        )

    def zep_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Zep loop plan."""
        return zp_zep_loop_plan(phase=phase)

    def memgpt_main_capacity(
        self,
        *,
        used_tokens: int,
        max_tokens: int,
        warn_ratio: float = 0.7,
    ) -> dict[str, Any]:
        """MemGPT main capacity."""
        return mg_memgpt_main_capacity(
            used_tokens=used_tokens,
            max_tokens=max_tokens,
            warn_ratio=warn_ratio,
        )

    def memgpt_page_out(self, *, content: str, tier: str) -> dict[str, Any]:
        """MemGPT page out."""
        return mg_memgpt_page_out(content=content, tier=tier)

    def memgpt_page_in(self, *, page_id: str, fits: bool) -> dict[str, Any]:
        """MemGPT page in."""
        return mg_memgpt_page_in(page_id=page_id, fits=fits)

    def memgpt_recall_search(
        self, *, query: str, hits: int
    ) -> dict[str, Any]:
        """MemGPT recall search."""
        return mg_memgpt_recall_search(query=query, hits=hits)

    def memgpt_archival_search(
        self, *, query: str, page: int = 0
    ) -> dict[str, Any]:
        """MemGPT archival search."""
        return mg_memgpt_archival_search(query=query, page=page)

    def memgpt_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemGPT loop plan."""
        return mg_memgpt_loop_plan(phase=phase)

    def ripple_store_episode(self, *, content: str) -> dict[str, Any]:
        """RippleMem store episode."""
        return rp_ripple_store_episode(content=content)

    def ripple_link_entity(
        self, *, episode_id: str, entity: str
    ) -> dict[str, Any]:
        """RippleMem link entity."""
        return rp_ripple_link_entity(episode_id=episode_id, entity=entity)

    def ripple_seed_retrieve(
        self, *, query: str, seed_hits: int
    ) -> dict[str, Any]:
        """RippleMem seed retrieve."""
        return rp_ripple_seed_retrieve(query=query, seed_hits=seed_hits)

    def ripple_expand(
        self, *, seeds: int, hop: int, max_hops: int = 2
    ) -> dict[str, Any]:
        """RippleMem expand."""
        return rp_ripple_expand(seeds=seeds, hop=hop, max_hops=max_hops)

    def ripple_recollect_gate(
        self, *, seed_hits: int, associated: int
    ) -> dict[str, Any]:
        """RippleMem recollect gate."""
        return rp_ripple_recollect_gate(
            seed_hits=seed_hits, associated=associated
        )

    def ripple_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RippleMem loop plan."""
        return rp_ripple_loop_plan(phase=phase)

    def flux_connect_form(
        self, *, src: str, dst: str, relation: str
    ) -> dict[str, Any]:
        """FluxMem connect form."""
        return fx_flux_connect_form(src=src, dst=dst, relation=relation)

    def flux_feedback_refine(
        self, *, edge_id: str, feedback: str, keep: bool
    ) -> dict[str, Any]:
        """FluxMem feedback refine."""
        return fx_flux_feedback_refine(
            edge_id=edge_id, feedback=feedback, keep=keep
        )

    def flux_consolidate(
        self, *, circuits: int, min_success: int = 2
    ) -> dict[str, Any]:
        """FluxMem consolidate."""
        return fx_flux_consolidate(
            circuits=circuits, min_success=min_success
        )

    def flux_repair_link(
        self, *, missing: bool, repaired: bool
    ) -> dict[str, Any]:
        """FluxMem repair link."""
        return fx_flux_repair_link(missing=missing, repaired=repaired)

    def flux_prune_interference(
        self, *, noise_score: float, threshold: float = 0.5
    ) -> dict[str, Any]:
        """FluxMem prune interference."""
        return fx_flux_prune_interference(
            noise_score=noise_score, threshold=threshold
        )

    def flux_maturity_gate(
        self, *, generalizability: float, min_score: float = 0.5
    ) -> dict[str, Any]:
        """FluxMem maturity gate."""
        return fx_flux_maturity_gate(
            generalizability=generalizability, min_score=min_score
        )

    def flux_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """FluxMem loop plan."""
        return fx_flux_loop_plan(phase=phase)

    def qumem_segment_episode(
        self, *, content: str, continuity: float
    ) -> dict[str, Any]:
        """QUMem segment episode."""
        return qm_qumem_segment_episode(
            content=content, continuity=continuity
        )

    def qumem_decompose(
        self, *, episode_id: str, mem_type: str
    ) -> dict[str, Any]:
        """QUMem decompose."""
        return qm_qumem_decompose(episode_id=episode_id, mem_type=mem_type)

    def qumem_plan_queries(
        self, *, task: str, needs: int
    ) -> dict[str, Any]:
        """QUMem plan queries."""
        return qm_qumem_plan_queries(task=task, needs=needs)

    def qumem_infer_user_state(
        self, *, factual: int, preference: int, insight: int
    ) -> dict[str, Any]:
        """QUMem infer user state."""
        return qm_qumem_infer_user_state(
            factual=factual, preference=preference, insight=insight
        )

    def qumem_temporal_valid(
        self, *, event_ts: str, query_ts: str, stale: bool
    ) -> dict[str, Any]:
        """QUMem temporal valid."""
        return qm_qumem_temporal_valid(
            event_ts=event_ts, query_ts=query_ts, stale=stale
        )

    def qumem_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """QUMem loop plan."""
        return qm_qumem_loop_plan(phase=phase)

    def viking_extract_event(
        self, *, content: str, high_value: bool
    ) -> dict[str, Any]:
        """VikingMem extract event."""
        return vk_viking_extract_event(content=content, high_value=high_value)

    def viking_update_entity(
        self, *, entity: str, event_id: str
    ) -> dict[str, Any]:
        """VikingMem update entity."""
        return vk_viking_update_entity(entity=entity, event_id=event_id)

    def viking_timeline_compress(
        self, *, topic: str, items: int
    ) -> dict[str, Any]:
        """VikingMem timeline compress."""
        return vk_viking_timeline_compress(topic=topic, items=items)

    def viking_time_weighted_recall(
        self, *, query: str, recency_weight: float
    ) -> dict[str, Any]:
        """VikingMem time-weighted recall."""
        return vk_viking_time_weighted_recall(
            query=query, recency_weight=recency_weight
        )

    def viking_rerank(
        self, *, candidates: int, top_k: int
    ) -> dict[str, Any]:
        """VikingMem rerank."""
        return vk_viking_rerank(candidates=candidates, top_k=top_k)

    def viking_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """VikingMem loop plan."""
        return vk_viking_loop_plan(phase=phase)

    def recmem_buffer_subconscious(self, *, content: str) -> dict[str, Any]:
        """RecMem buffer subconscious."""
        return rm_recmem_buffer_subconscious(content=content)

    def recmem_recurrence_gate(
        self, *, similar_count: int, threshold: int = 5
    ) -> dict[str, Any]:
        """RecMem recurrence gate."""
        return rm_recmem_recurrence_gate(
            similar_count=similar_count, threshold=threshold
        )

    def recmem_consolidate_episodic(
        self, *, cluster_size: int
    ) -> dict[str, Any]:
        """RecMem consolidate episodic."""
        return rm_recmem_consolidate_episodic(cluster_size=cluster_size)

    def recmem_semantic_refine(
        self, *, omitted_facts: int
    ) -> dict[str, Any]:
        """RecMem semantic refine."""
        return rm_recmem_semantic_refine(omitted_facts=omitted_facts)

    def recmem_merge_retrieve(
        self, *, subconscious: int, episodic: int, semantic: int
    ) -> dict[str, Any]:
        """RecMem merge retrieve."""
        return rm_recmem_merge_retrieve(
            subconscious=subconscious,
            episodic=episodic,
            semantic=semantic,
        )

    def recmem_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RecMem loop plan."""
        return rm_recmem_loop_plan(phase=phase)

    def mbank_store_memory(
        self, *, content: str, significance: float
    ) -> dict[str, Any]:
        """MemoryBank store memory."""
        return mb_mbank_store_memory(
            content=content, significance=significance
        )

    def mbank_summon(self, *, query: str, hits: int) -> dict[str, Any]:
        """MemoryBank summon."""
        return mb_mbank_summon(query=query, hits=hits)

    def mbank_personality_synth(self, *, traits: int) -> dict[str, Any]:
        """MemoryBank personality synth."""
        return mb_mbank_personality_synth(traits=traits)

    def mbank_forget_curve(
        self, *, days_elapsed: float, strength: float = 1.0
    ) -> dict[str, Any]:
        """MemoryBank forget curve."""
        return mb_mbank_forget_curve(
            days_elapsed=days_elapsed, strength=strength
        )

    def mbank_reinforce(
        self, *, memory_id: str, boost: float
    ) -> dict[str, Any]:
        """MemoryBank reinforce."""
        return mb_mbank_reinforce(memory_id=memory_id, boost=boost)

    def mbank_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemoryBank loop plan."""
        return mb_mbank_loop_plan(phase=phase)

    def rfmem_familiarity_score(
        self, *, mean_score: float, entropy: float
    ) -> dict[str, Any]:
        """RF-Mem familiarity score."""
        return rf_rfmem_familiarity_score(
            mean_score=mean_score, entropy=entropy
        )

    def rfmem_path_route(
        self,
        *,
        mean_score: float,
        entropy: float,
        high_mean: float = 0.7,
        low_entropy: float = 1.0,
    ) -> dict[str, Any]:
        """RF-Mem path route."""
        return rf_rfmem_path_route(
            mean_score=mean_score,
            entropy=entropy,
            high_mean=high_mean,
            low_entropy=low_entropy,
        )

    def rfmem_top_k_familiar(
        self, *, candidates: int, top_k: int
    ) -> dict[str, Any]:
        """RF-Mem top-k familiar."""
        return rf_rfmem_top_k_familiar(candidates=candidates, top_k=top_k)

    def rfmem_recollect_expand(
        self, *, clusters: int, hops: int, max_hops: int = 3
    ) -> dict[str, Any]:
        """RF-Mem recollect expand."""
        return rf_rfmem_recollect_expand(
            clusters=clusters, hops=hops, max_hops=max_hops
        )

    def rfmem_alpha_mix(
        self, *, alpha: float, query_weight: float
    ) -> dict[str, Any]:
        """RF-Mem alpha mix."""
        return rf_rfmem_alpha_mix(alpha=alpha, query_weight=query_weight)

    def rfmem_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RF-Mem loop plan."""
        return rf_rfmem_loop_plan(phase=phase)

    def agemem_ltm_store(
        self, *, content: str, tier: str = "ltm"
    ) -> dict[str, Any]:
        """AgeMem LTM/STM store."""
        return ag_agemem_ltm_store(content=content, tier=tier)

    def agemem_stm_manage(
        self, *, capacity: int, used: int
    ) -> dict[str, Any]:
        """AgeMem STM manage."""
        return ag_agemem_stm_manage(capacity=capacity, used=used)

    def agemem_retrieve(self, *, query: str, hits: int) -> dict[str, Any]:
        """AgeMem retrieve."""
        return ag_agemem_retrieve(query=query, hits=hits)

    def agemem_summarize(self, *, entries: int) -> dict[str, Any]:
        """AgeMem summarize."""
        return ag_agemem_summarize(entries=entries)

    def agemem_discard_plan(
        self, *, memory_id: str, reason: str
    ) -> dict[str, Any]:
        """AgeMem discard plan."""
        return ag_agemem_discard_plan(memory_id=memory_id, reason=reason)

    def agemem_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AgeMem loop plan."""
        return ag_agemem_loop_plan(phase=phase)

    def memgas_unit(
        self, *, content: str, granularity: str
    ) -> dict[str, Any]:
        """MemGAS unit."""
        return mg_memgas_unit(content=content, granularity=granularity)

    def memgas_associate(
        self, *, new_id: str, cluster_size: int
    ) -> dict[str, Any]:
        """MemGAS associate."""
        return mg_memgas_associate(new_id=new_id, cluster_size=cluster_size)

    def memgas_entropy_route(
        self, *, entropy: float, low: float = 1.0
    ) -> dict[str, Any]:
        """MemGAS entropy route."""
        return mg_memgas_entropy_route(entropy=entropy, low=low)

    def memgas_select_granularity(
        self, *, preferred: str, entropy: float
    ) -> dict[str, Any]:
        """MemGAS select granularity."""
        return mg_memgas_select_granularity(
            preferred=preferred, entropy=entropy
        )

    def memgas_filter_plan(
        self, *, candidates: int, keep: int
    ) -> dict[str, Any]:
        """MemGAS filter plan."""
        return mg_memgas_filter_plan(candidates=candidates, keep=keep)

    def memgas_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemGAS loop plan."""
        return mg_memgas_loop_plan(phase=phase)

    def memwalker_segment(
        self, *, content: str, chunk_size: int
    ) -> dict[str, Any]:
        """MemWalker segment."""
        return mw_memwalker_segment(content=content, chunk_size=chunk_size)

    def memwalker_build_node(
        self, *, summary: str, level: int
    ) -> dict[str, Any]:
        """MemWalker build node."""
        return mw_memwalker_build_node(summary=summary, level=level)

    def memwalker_navigate(
        self, *, node_id: str, action: str
    ) -> dict[str, Any]:
        """MemWalker navigate."""
        return mw_memwalker_navigate(node_id=node_id, action=action)

    def memwalker_gather(
        self, *, leaves: int, budget: int
    ) -> dict[str, Any]:
        """MemWalker gather."""
        return mw_memwalker_gather(leaves=leaves, budget=budget)

    def memwalker_path_gate(
        self, *, depth: int, max_depth: int
    ) -> dict[str, Any]:
        """MemWalker path gate."""
        return mw_memwalker_path_gate(depth=depth, max_depth=max_depth)

    def memwalker_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemWalker loop plan."""
        return mw_memwalker_loop_plan(phase=phase)

    def mgr_store_layer(
        self, *, content: str, layer: str
    ) -> dict[str, Any]:
        """MemGraphRAG store layer."""
        return mgr_mgr_store_layer(content=content, layer=layer)

    def mgr_detect_conflict(
        self, *, facts: int, anomalies: int
    ) -> dict[str, Any]:
        """MemGraphRAG detect conflict."""
        return mgr_mgr_detect_conflict(facts=facts, anomalies=anomalies)

    def mgr_resolve_plan(self, *, conflict_id: str) -> dict[str, Any]:
        """MemGraphRAG resolve plan."""
        return mgr_mgr_resolve_plan(conflict_id=conflict_id)

    def mgr_multilayer_retrieve(
        self, *, query: str, layers_hit: int
    ) -> dict[str, Any]:
        """MemGraphRAG multilayer retrieve."""
        return mgr_mgr_multilayer_retrieve(
            query=query, layers_hit=layers_hit
        )

    def mgr_propagate(
        self, *, seeds: int, damping: float = 0.85
    ) -> dict[str, Any]:
        """MemGraphRAG propagate."""
        return mgr_mgr_propagate(seeds=seeds, damping=damping)

    def mgr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemGraphRAG loop plan."""
        return mgr_mgr_loop_plan(phase=phase)

    def raptor_embed_chunk(self, *, content: str) -> dict[str, Any]:
        """RAPTOR embed chunk."""
        return rp_raptor_embed_chunk(content=content)

    def raptor_cluster(
        self, *, chunks: int, clusters: int
    ) -> dict[str, Any]:
        """RAPTOR cluster."""
        return rp_raptor_cluster(chunks=chunks, clusters=clusters)

    def raptor_summarize_node(
        self, *, level: int, children: int
    ) -> dict[str, Any]:
        """RAPTOR summarize node."""
        return rp_raptor_summarize_node(level=level, children=children)

    def raptor_tree_traverse(
        self, *, depth: int, keep_per_level: int
    ) -> dict[str, Any]:
        """RAPTOR tree traverse."""
        return rp_raptor_tree_traverse(
            depth=depth, keep_per_level=keep_per_level
        )

    def raptor_collapsed_retrieve(
        self, *, candidates: int, top_k: int
    ) -> dict[str, Any]:
        """RAPTOR collapsed retrieve."""
        return rp_raptor_collapsed_retrieve(
            candidates=candidates, top_k=top_k
        )

    def raptor_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RAPTOR loop plan."""
        return rp_raptor_loop_plan(phase=phase)

    def lightrag_index_entity(self, *, name: str) -> dict[str, Any]:
        """LightRAG index entity."""
        return lr_lightrag_index_entity(name=name)

    def lightrag_index_relation(
        self, *, src: str, dst: str, rel: str
    ) -> dict[str, Any]:
        """LightRAG index relation."""
        return lr_lightrag_index_relation(src=src, dst=dst, rel=rel)

    def lightrag_dual_retrieve(
        self, *, query: str, level: str
    ) -> dict[str, Any]:
        """LightRAG dual retrieve."""
        return lr_lightrag_dual_retrieve(query=query, level=level)

    def lightrag_incremental_update(
        self, *, new_docs: int
    ) -> dict[str, Any]:
        """LightRAG incremental update."""
        return lr_lightrag_incremental_update(new_docs=new_docs)

    def lightrag_graph_vector_fuse(
        self, *, graph_hits: int, vector_hits: int
    ) -> dict[str, Any]:
        """LightRAG graph-vector fuse."""
        return lr_lightrag_graph_vector_fuse(
            graph_hits=graph_hits, vector_hits=vector_hits
        )

    def lightrag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LightRAG loop plan."""
        return lr_lightrag_loop_plan(phase=phase)

    def memorag_memorize(self, *, corpus_chars: int) -> dict[str, Any]:
        """MemoRAG memorize."""
        return mr_memorag_memorize(corpus_chars=corpus_chars)

    def memorag_clue(self, *, query: str, draft: str) -> dict[str, Any]:
        """MemoRAG clue."""
        return mr_memorag_clue(query=query, draft=draft)

    def memorag_retrieve_by_clue(
        self, *, clue_id: str, hits: int
    ) -> dict[str, Any]:
        """MemoRAG retrieve by clue."""
        return mr_memorag_retrieve_by_clue(clue_id=clue_id, hits=hits)

    def memorag_dual_system(self, *, role: str) -> dict[str, Any]:
        """MemoRAG dual system."""
        return mr_memorag_dual_system(role=role)

    def memorag_generate_plan(self, *, evidence: int) -> dict[str, Any]:
        """MemoRAG generate plan."""
        return mr_memorag_generate_plan(evidence=evidence)

    def memorag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemoRAG loop plan."""
        return mr_memorag_loop_plan(phase=phase)

    def pageindex_build_toc(
        self, *, title: str, sections: int
    ) -> dict[str, Any]:
        """PageIndex build TOC."""
        return pi_pageindex_build_toc(title=title, sections=sections)

    def pageindex_add_section(
        self, *, parent_id: str, heading: str, page_start: int
    ) -> dict[str, Any]:
        """PageIndex add section."""
        return pi_pageindex_add_section(
            parent_id=parent_id, heading=heading, page_start=page_start
        )

    def pageindex_reason_nav(
        self, *, query: str, candidates: int
    ) -> dict[str, Any]:
        """PageIndex reason nav."""
        return pi_pageindex_reason_nav(query=query, candidates=candidates)

    def pageindex_select_section(
        self, *, section_id: str, relevant: bool
    ) -> dict[str, Any]:
        """PageIndex select section."""
        return pi_pageindex_select_section(
            section_id=section_id, relevant=relevant
        )

    def pageindex_trace_path(self, *, hops: int) -> dict[str, Any]:
        """PageIndex trace path."""
        return pi_pageindex_trace_path(hops=hops)

    def pageindex_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PageIndex loop plan."""
        return pi_pageindex_loop_plan(phase=phase)

    def selfrag_need_retrieve(
        self, *, confidence: float, threshold: float = 0.5
    ) -> dict[str, Any]:
        """Self-RAG need retrieve."""
        return sr_selfrag_need_retrieve(
            confidence=confidence, threshold=threshold
        )

    def selfrag_relevance_critique(self, *, relevant: bool) -> dict[str, Any]:
        """Self-RAG relevance critique."""
        return sr_selfrag_relevance_critique(relevant=relevant)

    def selfrag_support_critique(self, *, supported: bool) -> dict[str, Any]:
        """Self-RAG support critique."""
        return sr_selfrag_support_critique(supported=supported)

    def selfrag_utility_critique(self, *, utility: float) -> dict[str, Any]:
        """Self-RAG utility critique."""
        return sr_selfrag_utility_critique(utility=utility)

    def selfrag_select_best(
        self, *, scores: int, pick: int
    ) -> dict[str, Any]:
        """Self-RAG select best."""
        return sr_selfrag_select_best(scores=scores, pick=pick)

    def selfrag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Self-RAG loop plan."""
        return sr_selfrag_loop_plan(phase=phase)

    def memobrain_dep_edge(
        self, *, src_step: str, dst_step: str
    ) -> dict[str, Any]:
        """MemoBrain dep edge."""
        return mb_memobrain_dep_edge(src_step=src_step, dst_step=dst_step)

    def memobrain_prune_invalid(
        self, *, step_id: str, invalid: bool
    ) -> dict[str, Any]:
        """MemoBrain prune invalid."""
        return mb_memobrain_prune_invalid(step_id=step_id, invalid=invalid)

    def memobrain_fold_subtraj(self, *, steps: int) -> dict[str, Any]:
        """MemoBrain fold subtraj."""
        return mb_memobrain_fold_subtraj(steps=steps)

    def memobrain_flush_budget(
        self, *, used: int, budget: int
    ) -> dict[str, Any]:
        """MemoBrain flush budget."""
        return mb_memobrain_flush_budget(used=used, budget=budget)

    def memobrain_salience_keep(
        self, *, salience: float, min_keep: float = 0.5
    ) -> dict[str, Any]:
        """MemoBrain salience keep."""
        return mb_memobrain_salience_keep(
            salience=salience, min_keep=min_keep
        )

    def memobrain_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MemoBrain loop plan."""
        return mb_memobrain_loop_plan(phase=phase)

    def crag_evaluate_retrieval(self, *, confidence: float) -> dict[str, Any]:
        """CRAG evaluate retrieval."""
        return cg_crag_evaluate_retrieval(confidence=confidence)

    def crag_correct_refine(self, *, chunks: int) -> dict[str, Any]:
        """CRAG correct refine."""
        return cg_crag_correct_refine(chunks=chunks)

    def crag_web_fallback_plan(self, *, trigger: bool) -> dict[str, Any]:
        """CRAG web fallback plan."""
        return cg_crag_web_fallback_plan(trigger=trigger)

    def crag_ambiguous_blend(
        self, *, local_hits: int, web_hits: int
    ) -> dict[str, Any]:
        """CRAG ambiguous blend."""
        return cg_crag_ambiguous_blend(
            local_hits=local_hits, web_hits=web_hits
        )

    def crag_action_select(self, *, action: str) -> dict[str, Any]:
        """CRAG action select."""
        return cg_crag_action_select(action=action)

    def crag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CRAG loop plan."""
        return cg_crag_loop_plan(phase=phase)

    def hyde_hypothetical_doc(self, *, query: str) -> dict[str, Any]:
        """HyDE hypothetical doc."""
        return hy_hyde_hypothetical_doc(query=query)

    def hyde_encode_proxy(self, *, hyp_id: str) -> dict[str, Any]:
        """HyDE encode proxy."""
        return hy_hyde_encode_proxy(hyp_id=hyp_id)

    def hyde_retrieve_by_hyp(
        self, *, vec_id: str, k: int = 5
    ) -> dict[str, Any]:
        """HyDE retrieve by hyp."""
        return hy_hyde_retrieve_by_hyp(vec_id=vec_id, k=k)

    def hyde_filter_hallucination(self, *, retained: float) -> dict[str, Any]:
        """HyDE filter hallucination."""
        return hy_hyde_filter_hallucination(retained=retained)

    def hyde_ground_corpus(
        self, *, hits: int, grounded: int
    ) -> dict[str, Any]:
        """HyDE ground corpus."""
        return hy_hyde_ground_corpus(hits=hits, grounded=grounded)

    def hyde_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HyDE loop plan."""
        return hy_hyde_loop_plan(phase=phase)

    def adaptiverag_classify_complexity(self, *, hops: int) -> dict[str, Any]:
        """Adaptive-RAG classify complexity."""
        return ar_adaptiverag_classify_complexity(hops=hops)

    def adaptiverag_select_strategy(self, *, level: int) -> dict[str, Any]:
        """Adaptive-RAG select strategy."""
        return ar_adaptiverag_select_strategy(level=level)

    def adaptiverag_no_retrieve(self, *, parametric_ok: bool) -> dict[str, Any]:
        """Adaptive-RAG no retrieve."""
        return ar_adaptiverag_no_retrieve(parametric_ok=parametric_ok)

    def adaptiverag_single_step(self, *, hits: int) -> dict[str, Any]:
        """Adaptive-RAG single step."""
        return ar_adaptiverag_single_step(hits=hits)

    def adaptiverag_multi_step(self, *, steps: int) -> dict[str, Any]:
        """Adaptive-RAG multi step."""
        return ar_adaptiverag_multi_step(steps=steps)

    def adaptiverag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Adaptive-RAG loop plan."""
        return ar_adaptiverag_loop_plan(phase=phase)

    def flare_anticipate_sentence(self, *, context: str) -> dict[str, Any]:
        """FLARE anticipate sentence."""
        return fl_flare_anticipate_sentence(context=context)

    def flare_low_confidence(
        self, *, confidence: float, threshold: float = 0.4
    ) -> dict[str, Any]:
        """FLARE low confidence."""
        return fl_flare_low_confidence(
            confidence=confidence, threshold=threshold
        )

    def flare_retrieve_for_regen(
        self, *, query: str, k: int = 3
    ) -> dict[str, Any]:
        """FLARE retrieve for regen."""
        return fl_flare_retrieve_for_regen(query=query, k=k)

    def flare_regenerate_sentence(
        self, *, sent_id: str, with_docs: bool
    ) -> dict[str, Any]:
        """FLARE regenerate sentence."""
        return fl_flare_regenerate_sentence(
            sent_id=sent_id, with_docs=with_docs
        )

    def flare_active_step(
        self, *, step: int, retrieved: bool
    ) -> dict[str, Any]:
        """FLARE active step."""
        return fl_flare_active_step(step=step, retrieved=retrieved)

    def flare_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """FLARE loop plan."""
        return fl_flare_loop_plan(phase=phase)

    def graphreader_build_node(self, *, chunk: str) -> dict[str, Any]:
        """GraphReader build node."""
        return gr_graphreader_build_node(chunk=chunk)

    def graphreader_read_node(self, *, node_id: str) -> dict[str, Any]:
        """GraphReader read node."""
        return gr_graphreader_read_node(node_id=node_id)

    def graphreader_read_neighbors(
        self, *, node_id: str, hops: int = 1
    ) -> dict[str, Any]:
        """GraphReader read neighbors."""
        return gr_graphreader_read_neighbors(node_id=node_id, hops=hops)

    def graphreader_note_insight(self, *, text: str) -> dict[str, Any]:
        """GraphReader note insight."""
        return gr_graphreader_note_insight(text=text)

    def graphreader_reflect_plan(self, *, enough: bool) -> dict[str, Any]:
        """GraphReader reflect plan."""
        return gr_graphreader_reflect_plan(enough=enough)

    def graphreader_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GraphReader loop plan."""
        return gr_graphreader_loop_plan(phase=phase)

    def gretriever_node_prize(
        self, *, node_id: str, prize: float
    ) -> dict[str, Any]:
        """G-Retriever node prize."""
        return gv_gretriever_node_prize(node_id=node_id, prize=prize)

    def gretriever_pcst_select(
        self, *, nodes: int, budget: int
    ) -> dict[str, Any]:
        """G-Retriever PCST select."""
        return gv_gretriever_pcst_select(nodes=nodes, budget=budget)

    def gretriever_subgraph(self, *, selected: int) -> dict[str, Any]:
        """G-Retriever subgraph."""
        return gv_gretriever_subgraph(selected=selected)

    def gretriever_soft_prompt_plan(
        self, *, subgraph_id: str
    ) -> dict[str, Any]:
        """G-Retriever soft prompt plan."""
        return gv_gretriever_soft_prompt_plan(subgraph_id=subgraph_id)

    def gretriever_highlight(self, *, nodes: int) -> dict[str, Any]:
        """G-Retriever highlight."""
        return gv_gretriever_highlight(nodes=nodes)

    def gretriever_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """G-Retriever loop plan."""
        return gv_gretriever_loop_plan(phase=phase)

    def rqrag_rewrite(self, *, query: str) -> dict[str, Any]:
        """RQ-RAG rewrite."""
        return rq_rqrag_rewrite(query=query)

    def rqrag_decompose(self, *, query: str, parts: int) -> dict[str, Any]:
        """RQ-RAG decompose."""
        return rq_rqrag_decompose(query=query, parts=parts)

    def rqrag_disambiguate(
        self, *, query: str, intents: int
    ) -> dict[str, Any]:
        """RQ-RAG disambiguate."""
        return rq_rqrag_disambiguate(query=query, intents=intents)

    def rqrag_refine_mode(self, *, mode: str) -> dict[str, Any]:
        """RQ-RAG refine mode."""
        return rq_rqrag_refine_mode(mode=mode)

    def rqrag_retrieve_refined(
        self, *, refined_id: str, k: int = 5
    ) -> dict[str, Any]:
        """RQ-RAG retrieve refined."""
        return rq_rqrag_retrieve_refined(refined_id=refined_id, k=k)

    def rqrag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RQ-RAG loop plan."""
        return rq_rqrag_loop_plan(phase=phase)

    def ircot_cot_step(self, *, step: int, claim: str) -> dict[str, Any]:
        """IRCoT CoT step."""
        return ir_ircot_cot_step(step=step, claim=claim)

    def ircot_retrieve_guided(
        self, *, step_id: str, k: int = 3
    ) -> dict[str, Any]:
        """IRCoT retrieve guided."""
        return ir_ircot_retrieve_guided(step_id=step_id, k=k)

    def ircot_interleave(
        self, *, cot_steps: int, retrieves: int
    ) -> dict[str, Any]:
        """IRCoT interleave."""
        return ir_ircot_interleave(cot_steps=cot_steps, retrieves=retrieves)

    def ircot_answer_ready(self, *, enough: bool) -> dict[str, Any]:
        """IRCoT answer ready."""
        return ir_ircot_answer_ready(enough=enough)

    def ircot_hallucination_check(self, *, grounded: float) -> dict[str, Any]:
        """IRCoT hallucination check."""
        return ir_ircot_hallucination_check(grounded=grounded)

    def ircot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """IRCoT loop plan."""
        return ir_ircot_loop_plan(phase=phase)

    def replug_retrieve_docs(
        self, *, query: str, k: int = 5
    ) -> dict[str, Any]:
        """REPLUG retrieve docs."""
        return rp_replug_retrieve_docs(query=query, k=k)

    def replug_prepend_doc(
        self, *, doc_id: str, context: str
    ) -> dict[str, Any]:
        """REPLUG prepend doc."""
        return rp_replug_prepend_doc(doc_id=doc_id, context=context)

    def replug_ensemble_probs(self, *, packs: int) -> dict[str, Any]:
        """REPLUG ensemble probs."""
        return rp_replug_ensemble_probs(packs=packs)

    def replug_supervise_retriever(self, *, lm_gain: float) -> dict[str, Any]:
        """REPLUG supervise retriever."""
        return rp_replug_supervise_retriever(lm_gain=lm_gain)

    def replug_blackbox_forward(self, *, pack_id: str) -> dict[str, Any]:
        """REPLUG blackbox forward."""
        return rp_replug_blackbox_forward(pack_id=pack_id)

    def replug_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """REPLUG loop plan."""
        return rp_replug_loop_plan(phase=phase)

    def iterretgen_generate(
        self, *, iteration: int, draft: str
    ) -> dict[str, Any]:
        """Iter-RetGen generate."""
        return it_iterretgen_generate(iteration=iteration, draft=draft)

    def iterretgen_use_as_query(self, *, gen_id: str) -> dict[str, Any]:
        """Iter-RetGen use as query."""
        return it_iterretgen_use_as_query(gen_id=gen_id)

    def iterretgen_retrieve_next(
        self, *, query_from: str, k: int = 5
    ) -> dict[str, Any]:
        """Iter-RetGen retrieve next."""
        return it_iterretgen_retrieve_next(query_from=query_from, k=k)

    def iterretgen_iterate(
        self, *, round_n: int, max_rounds: int = 3
    ) -> dict[str, Any]:
        """Iter-RetGen iterate."""
        return it_iterretgen_iterate(round_n=round_n, max_rounds=max_rounds)

    def iterretgen_adapt_retriever(self, *, improve: bool) -> dict[str, Any]:
        """Iter-RetGen adapt retriever."""
        return it_iterretgen_adapt_retriever(improve=improve)

    def iterretgen_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Iter-RetGen loop plan."""
        return it_iterretgen_loop_plan(phase=phase)

    def planrag_make_plan(self, *, question: str) -> dict[str, Any]:
        """PlanRAG make plan."""
        return pr_planrag_make_plan(question=question)

    def planrag_analysis_query(
        self, *, plan_id: str, query: str
    ) -> dict[str, Any]:
        """PlanRAG analysis query."""
        return pr_planrag_analysis_query(plan_id=plan_id, query=query)

    def planrag_retrieve_data(
        self, *, query_id: str, rows: int
    ) -> dict[str, Any]:
        """PlanRAG retrieve data."""
        return pr_planrag_retrieve_data(query_id=query_id, rows=rows)

    def planrag_replan(self, *, need_replan: bool) -> dict[str, Any]:
        """PlanRAG replan."""
        return pr_planrag_replan(need_replan=need_replan)

    def planrag_decide(self, *, ready: bool) -> dict[str, Any]:
        """PlanRAG decide."""
        return pr_planrag_decide(ready=ready)

    def planrag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PlanRAG loop plan."""
        return pr_planrag_loop_plan(phase=phase)

    def rrr_rewrite_query(self, *, query: str) -> dict[str, Any]:
        """RRR rewrite query."""
        return rr_rrr_rewrite_query(query=query)

    def rrr_retrieve(self, *, rewrite_id: str, k: int = 5) -> dict[str, Any]:
        """RRR retrieve."""
        return rr_rrr_retrieve(rewrite_id=rewrite_id, k=k)

    def rrr_read(self, *, hits: int) -> dict[str, Any]:
        """RRR read."""
        return rr_rrr_read(hits=hits)

    def rrr_reader_feedback(self, *, reward: float) -> dict[str, Any]:
        """RRR reader feedback."""
        return rr_rrr_reader_feedback(reward=reward)

    def rrr_train_rewriter_plan(self, *, improve: bool) -> dict[str, Any]:
        """RRR train rewriter plan."""
        return rr_rrr_train_rewriter_plan(improve=improve)

    def rrr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RRR loop plan."""
        return rr_rrr_loop_plan(phase=phase)

    def dsp_bootstrap_demo(
        self, *, task: str, n: int = 3
    ) -> dict[str, Any]:
        """DSP bootstrap demo."""
        return ds_dsp_bootstrap_demo(task=task, n=n)

    def dsp_search(self, *, query: str, k: int = 5) -> dict[str, Any]:
        """DSP search."""
        return ds_dsp_search(query=query, k=k)

    def dsp_predict(self, *, grounded: bool) -> dict[str, Any]:
        """DSP predict."""
        return ds_dsp_predict(grounded=grounded)

    def dsp_compose_program(self, *, stages: int) -> dict[str, Any]:
        """DSP compose program."""
        return ds_dsp_compose_program(stages=stages)

    def dsp_multihop_hop(self, *, hop: int) -> dict[str, Any]:
        """DSP multihop hop."""
        return ds_dsp_multihop_hop(hop=hop)

    def dsp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """DSP loop plan."""
        return ds_dsp_loop_plan(phase=phase)

    def genread_generate_context(self, *, question: str) -> dict[str, Any]:
        """GenRead generate context."""
        return gn_genread_generate_context(question=question)

    def genread_ground_optional(
        self, *, ctx_id: str, use_retriever: bool
    ) -> dict[str, Any]:
        """GenRead ground optional."""
        return gn_genread_ground_optional(
            ctx_id=ctx_id, use_retriever=use_retriever
        )

    def genread_answer(self, *, ctx_id: str) -> dict[str, Any]:
        """GenRead answer."""
        return gn_genread_answer(ctx_id=ctx_id)

    def genread_compare_retrieve(
        self, *, gen_hits: int, retrieve_hits: int
    ) -> dict[str, Any]:
        """GenRead compare retrieve."""
        return gn_genread_compare_retrieve(
            gen_hits=gen_hits, retrieve_hits=retrieve_hits
        )

    def genread_hybrid(
        self, *, generate: bool, retrieve: bool
    ) -> dict[str, Any]:
        """GenRead hybrid."""
        return gn_genread_hybrid(generate=generate, retrieve=retrieve)

    def genread_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GenRead loop plan."""
        return gn_genread_loop_plan(phase=phase)

    def selfask_followup(
        self, *, question: str, hop: int = 0
    ) -> dict[str, Any]:
        """Self-Ask followup."""
        return sa_selfask_followup(question=question, hop=hop)

    def selfask_search_intercept(
        self, *, followup_id: str, k: int = 3
    ) -> dict[str, Any]:
        """Self-Ask search intercept."""
        return sa_selfask_search_intercept(followup_id=followup_id, k=k)

    def selfask_compose_answer(self, *, followups: int) -> dict[str, Any]:
        """Self-Ask compose answer."""
        return sa_selfask_compose_answer(followups=followups)

    def selfask_stop(self, *, enough: bool) -> dict[str, Any]:
        """Self-Ask stop."""
        return sa_selfask_stop(enough=enough)

    def selfask_demo_prompt(self, *, demos: int) -> dict[str, Any]:
        """Self-Ask demo prompt."""
        return sa_selfask_demo_prompt(demos=demos)

    def selfask_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Self-Ask loop plan."""
        return sa_selfask_loop_plan(phase=phase)

    def react_thought(self, *, step: int, text: str) -> dict[str, Any]:
        """ReAct thought."""
        return rc_react_thought(step=step, text=text)

    def react_action(self, *, action: str, arg: str) -> dict[str, Any]:
        """ReAct action."""
        return rc_react_action(action=action, arg=arg)

    def react_observe(self, *, observation: str) -> dict[str, Any]:
        """ReAct observe."""
        return rc_react_observe(observation=observation)

    def react_finish(self, *, answer: str) -> dict[str, Any]:
        """ReAct finish."""
        return rc_react_finish(answer=answer)

    def react_trajectory(self, *, steps: int) -> dict[str, Any]:
        """ReAct trajectory."""
        return rc_react_trajectory(steps=steps)

    def react_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ReAct loop plan."""
        return rc_react_loop_plan(phase=phase)

    def tog_init_entity(self, *, entity: str) -> dict[str, Any]:
        """ToG init entity."""
        return tog_tog_init_entity(entity=entity)

    def tog_explore_neighbors(
        self, *, entity_id: str, width: int = 3
    ) -> dict[str, Any]:
        """ToG explore neighbors."""
        return tog_tog_explore_neighbors(entity_id=entity_id, width=width)

    def tog_beam_prune(self, *, paths: int, keep: int) -> dict[str, Any]:
        """ToG beam prune."""
        return tog_tog_beam_prune(paths=paths, keep=keep)

    def tog_path_score(self, *, path_id: str, score: float) -> dict[str, Any]:
        """ToG path score."""
        return tog_tog_path_score(path_id=path_id, score=score)

    def tog_answer_from_paths(self, *, path_count: int) -> dict[str, Any]:
        """ToG answer from paths."""
        return tog_tog_answer_from_paths(path_count=path_count)

    def tog_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ToG loop plan."""
        return tog_tog_loop_plan(phase=phase)

    def tf_api_candidate(self, *, api: str, args: str) -> dict[str, Any]:
        """Toolformer API candidate."""
        return tf_tf_api_candidate(api=api, args=args)

    def tf_filter_call(
        self, *, candidate_id: str, useful: bool
    ) -> dict[str, Any]:
        """Toolformer filter call."""
        return tf_tf_filter_call(candidate_id=candidate_id, useful=useful)

    def tf_execute_proxy(self, *, api: str) -> dict[str, Any]:
        """Toolformer execute proxy."""
        return tf_tf_execute_proxy(api=api)

    def tf_incorporate_result(self, *, result_id: str) -> dict[str, Any]:
        """Toolformer incorporate result."""
        return tf_tf_incorporate_result(result_id=result_id)

    def tf_demo_apis(self, *, count: int) -> dict[str, Any]:
        """Toolformer demo APIs."""
        return tf_tf_demo_apis(count=count)

    def tf_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Toolformer loop plan."""
        return tf_tf_loop_plan(phase=phase)

    def rx_trial_run(self, *, task: str, trial: int = 0) -> dict[str, Any]:
        """Reflexion trial run."""
        return rx_rx_trial_run(task=task, trial=trial)

    def rx_evaluate(self, *, trial_id: str, success: bool) -> dict[str, Any]:
        """Reflexion evaluate."""
        return rx_rx_evaluate(trial_id=trial_id, success=success)

    def rx_verbal_reflect(
        self, *, trial_id: str, feedback: str
    ) -> dict[str, Any]:
        """Reflexion verbal reflect."""
        return rx_rx_verbal_reflect(trial_id=trial_id, feedback=feedback)

    def rx_memory_store(self, *, reflection_id: str) -> dict[str, Any]:
        """Reflexion memory store."""
        return rx_rx_memory_store(reflection_id=reflection_id)

    def rx_next_trial(self, *, reflections: int) -> dict[str, Any]:
        """Reflexion next trial."""
        return rx_rx_next_trial(reflections=reflections)

    def rx_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Reflexion loop plan."""
        return rx_rx_loop_plan(phase=phase)

    def sc_sample_path(
        self, *, path_idx: int, answer: str
    ) -> dict[str, Any]:
        """Self-Consistency sample path."""
        return sc_sc_sample_path(path_idx=path_idx, answer=answer)

    def sc_collect_answers(self, *, n: int) -> dict[str, Any]:
        """Self-Consistency collect answers."""
        return sc_sc_collect_answers(n=n)

    def sc_majority_vote(self, *, votes: dict[str, int]) -> dict[str, Any]:
        """Self-Consistency majority vote."""
        return sc_sc_majority_vote(votes=votes)

    def sc_marginalize(
        self, *, paths: int, unique_answers: int
    ) -> dict[str, Any]:
        """Self-Consistency marginalize."""
        return sc_sc_marginalize(paths=paths, unique_answers=unique_answers)

    def sc_temperature(self, *, temp: float) -> dict[str, Any]:
        """Self-Consistency temperature."""
        return sc_sc_temperature(temp=temp)

    def sc_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Self-Consistency loop plan."""
        return sc_sc_loop_plan(phase=phase)

    def tot_propose(self, *, parent_id: str, text: str) -> dict[str, Any]:
        """ToT propose."""
        return tot_tot_propose(parent_id=parent_id, text=text)

    def tot_evaluate(self, *, node_id: str, score: float) -> dict[str, Any]:
        """ToT evaluate."""
        return tot_tot_evaluate(node_id=node_id, score=score)

    def tot_expand(self, *, breadth: int, depth: int) -> dict[str, Any]:
        """ToT expand."""
        return tot_tot_expand(breadth=breadth, depth=depth)

    def tot_backtrack(self, *, from_node: str) -> dict[str, Any]:
        """ToT backtrack."""
        return tot_tot_backtrack(from_node=from_node)

    def tot_select_best(self, *, candidates: int) -> dict[str, Any]:
        """ToT select best."""
        return tot_tot_select_best(candidates=candidates)

    def tot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ToT loop plan."""
        return tot_tot_loop_plan(phase=phase)

    def ltm_decompose(self, *, problem: str, n_subs: int) -> dict[str, Any]:
        """LtM decompose."""
        return ltm_ltm_decompose(problem=problem, n_subs=n_subs)

    def ltm_solve_sub(
        self, *, decomp_id: str, sub_idx: int
    ) -> dict[str, Any]:
        """LtM solve sub."""
        return ltm_ltm_solve_sub(decomp_id=decomp_id, sub_idx=sub_idx)

    def ltm_carry_forward(self, *, answered: int) -> dict[str, Any]:
        """LtM carry forward."""
        return ltm_ltm_carry_forward(answered=answered)

    def ltm_compose_final(self, *, subs_done: int) -> dict[str, Any]:
        """LtM compose final."""
        return ltm_ltm_compose_final(subs_done=subs_done)

    def ltm_easy_to_hard(self, *, exemplars: int) -> dict[str, Any]:
        """LtM easy to hard."""
        return ltm_ltm_easy_to_hard(exemplars=exemplars)

    def ltm_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LtM loop plan."""
        return ltm_ltm_loop_plan(phase=phase)

    def got_add_thought(self, *, text: str) -> dict[str, Any]:
        """GoT add thought."""
        return got_got_add_thought(text=text)

    def got_link(self, *, src: str, dst: str) -> dict[str, Any]:
        """GoT link."""
        return got_got_link(src=src, dst=dst)

    def got_aggregate(self, *, inputs: int) -> dict[str, Any]:
        """GoT aggregate."""
        return got_got_aggregate(inputs=inputs)

    def got_feedback(self, *, vertex_id: str) -> dict[str, Any]:
        """GoT feedback."""
        return got_got_feedback(vertex_id=vertex_id)

    def got_score_graph(
        self, *, vertices: int, edges: int
    ) -> dict[str, Any]:
        """GoT score graph."""
        return got_got_score_graph(vertices=vertices, edges=edges)

    def got_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GoT loop plan."""
        return got_got_loop_plan(phase=phase)

    def pot_emit_program(
        self, *, problem: str, lang: str = "python"
    ) -> dict[str, Any]:
        """PoT emit program."""
        return pot_pot_emit_program(problem=problem, lang=lang)

    def pot_sandbox_run(self, *, program_id: str) -> dict[str, Any]:
        """PoT sandbox run."""
        return pot_pot_sandbox_run(program_id=program_id)

    def pot_read_result(self, *, result_id: str) -> dict[str, Any]:
        """PoT read result."""
        return pot_pot_read_result(result_id=result_id)

    def pot_self_consistency(self, *, samples: int) -> dict[str, Any]:
        """PoT self-consistency."""
        return pot_pot_self_consistency(samples=samples)

    def pot_disentangle(
        self, *, compute_offloaded: bool
    ) -> dict[str, Any]:
        """PoT disentangle."""
        return pot_pot_disentangle(compute_offloaded=compute_offloaded)

    def pot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PoT loop plan."""
        return pot_pot_loop_plan(phase=phase)

    def aot_load_algorithm(self, *, name: str) -> dict[str, Any]:
        """AoT load algorithm."""
        return aot_aot_load_algorithm(name=name)

    def aot_explore_subtree(
        self, *, depth: int, branch: int
    ) -> dict[str, Any]:
        """AoT explore subtree."""
        return aot_aot_explore_subtree(depth=depth, branch=branch)

    def aot_tunnel_vision(self, *, activate: bool) -> dict[str, Any]:
        """AoT tunnel vision."""
        return aot_aot_tunnel_vision(activate=activate)

    def aot_query_budget(self, *, queries: int) -> dict[str, Any]:
        """AoT query budget."""
        return aot_aot_query_budget(queries=queries)

    def aot_surpass_algo(self, *, intuition: bool) -> dict[str, Any]:
        """AoT surpass algo."""
        return aot_aot_surpass_algo(intuition=intuition)

    def aot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AoT loop plan."""
        return aot_aot_loop_plan(phase=phase)

    def rap_world_state(self, *, state: str) -> dict[str, Any]:
        """RAP world state."""
        return rap_rap_world_state(state=state)

    def rap_expand(self, *, state_id: str, actions: int) -> dict[str, Any]:
        """RAP expand."""
        return rap_rap_expand(state_id=state_id, actions=actions)

    def rap_reward(self, *, state_id: str, reward: float) -> dict[str, Any]:
        """RAP reward."""
        return rap_rap_reward(state_id=state_id, reward=reward)

    def rap_select_path(self, *, visits: int) -> dict[str, Any]:
        """RAP select path."""
        return rap_rap_select_path(visits=visits)

    def rap_balance(self, *, explore: float) -> dict[str, Any]:
        """RAP balance."""
        return rap_rap_balance(explore=explore)

    def rap_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RAP loop plan."""
        return rap_rap_loop_plan(phase=phase)

    def sot_emit_skeleton(self, *, question: str) -> dict[str, Any]:
        """SoT emit skeleton."""
        return sot_sot_emit_skeleton(question=question)

    def sot_extract_points(
        self, *, skeleton_id: str, points: int
    ) -> dict[str, Any]:
        """SoT extract points."""
        return sot_sot_extract_points(skeleton_id=skeleton_id, points=points)

    def sot_parallel_expand(self, *, points: int) -> dict[str, Any]:
        """SoT parallel expand."""
        return sot_sot_parallel_expand(points=points)

    def sot_router(self, *, suitable: bool) -> dict[str, Any]:
        """SoT router."""
        return sot_sot_router(suitable=suitable)

    def sot_latency_gain(
        self, *, sequential: int, parallel: int
    ) -> dict[str, Any]:
        """SoT latency gain."""
        return sot_sot_latency_gain(sequential=sequential, parallel=parallel)

    def sot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SoT loop plan."""
        return sot_sot_loop_plan(phase=phase)

    def bot_distill_template(self, *, task: str) -> dict[str, Any]:
        """BoT distill template."""
        return bot_bot_distill_template(task=task)

    def bot_retrieve_template(self, *, query: str) -> dict[str, Any]:
        """BoT retrieve template."""
        return bot_bot_retrieve_template(query=query)

    def bot_instantiate(self, *, template_id: str) -> dict[str, Any]:
        """BoT instantiate."""
        return bot_bot_instantiate(template_id=template_id)

    def bot_buffer_update(self, *, templates: int) -> dict[str, Any]:
        """BoT buffer update."""
        return bot_bot_buffer_update(templates=templates)

    def bot_cost_ratio(
        self, *, multi_query: int, bot: int
    ) -> dict[str, Any]:
        """BoT cost ratio."""
        return bot_bot_cost_ratio(multi_query=multi_query, bot=bot)

    def bot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """BoT loop plan."""
        return bot_bot_loop_plan(phase=phase)

    def sd_select_modules(
        self, *, task: str, modules: int
    ) -> dict[str, Any]:
        """Self-Discover select modules."""
        return sd_sd_select_modules(task=task, modules=modules)

    def sd_adapt(self, *, select_id: str) -> dict[str, Any]:
        """Self-Discover adapt."""
        return sd_sd_adapt(select_id=select_id)

    def sd_implement(self, *, adapt_id: str, keys: int) -> dict[str, Any]:
        """Self-Discover implement."""
        return sd_sd_implement(adapt_id=adapt_id, keys=keys)

    def sd_apply_instance(self, *, structure_id: str) -> dict[str, Any]:
        """Self-Discover apply instance."""
        return sd_sd_apply_instance(structure_id=structure_id)

    def sd_compute_ratio(
        self, *, sc_calls: int, self_discover: int
    ) -> dict[str, Any]:
        """Self-Discover compute ratio."""
        return sd_sd_compute_ratio(
            sc_calls=sc_calls, self_discover=self_discover
        )

    def sd_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Self-Discover loop plan."""
        return sd_sd_loop_plan(phase=phase)

    def mp_break_task(self, *, query: str, pieces: int) -> dict[str, Any]:
        """Meta-Prompting break task."""
        return mp_mp_break_task(query=query, pieces=pieces)

    def mp_assign_expert(
        self, *, piece_idx: int, expert: str
    ) -> dict[str, Any]:
        """Meta-Prompting assign expert."""
        return mp_mp_assign_expert(piece_idx=piece_idx, expert=expert)

    def mp_oversee(self, *, messages: int) -> dict[str, Any]:
        """Meta-Prompting oversee."""
        return mp_mp_oversee(messages=messages)

    def mp_verify(self, *, claim: str) -> dict[str, Any]:
        """Meta-Prompting verify."""
        return mp_mp_verify(claim=claim)

    def mp_task_agnostic(self, *, scaffold: bool) -> dict[str, Any]:
        """Meta-Prompting task-agnostic."""
        return mp_mp_task_agnostic(scaffold=scaffold)

    def mp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Meta-Prompting loop plan."""
        return mp_mp_loop_plan(phase=phase)

    def qs_thought_bounds(self, *, start: str, end: str) -> dict[str, Any]:
        """Quiet-STaR thought bounds."""
        return qs_qs_thought_bounds(start=start, end=end)

    def qs_parallel_sample(
        self, *, positions: int, thoughts: int
    ) -> dict[str, Any]:
        """Quiet-STaR parallel sample."""
        return qs_qs_parallel_sample(positions=positions, thoughts=thoughts)

    def qs_mix_head(self, *, weight: float) -> dict[str, Any]:
        """Quiet-STaR mix head."""
        return qs_qs_mix_head(weight=weight)

    def qs_hard_token_aid(
        self, *, hard_tokens: int, helped: int
    ) -> dict[str, Any]:
        """Quiet-STaR hard token aid."""
        return qs_qs_hard_token_aid(
            hard_tokens=hard_tokens, helped=helped
        )

    def qs_zero_shot_flag(self, *, improved: bool) -> dict[str, Any]:
        """Quiet-STaR zero-shot flag."""
        return qs_qs_zero_shot_flag(improved=improved)

    def qs_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Quiet-STaR loop plan."""
        return qs_qs_loop_plan(phase=phase)

    def dep_decompose(self, *, task: str, subs: int) -> dict[str, Any]:
        """Decomposed Prompting decompose."""
        return dep_dep_decompose(task=task, subs=subs)

    def dep_delegate(
        self, *, handler: str, sub_idx: int
    ) -> dict[str, Any]:
        """Decomposed Prompting delegate."""
        return dep_dep_delegate(handler=handler, sub_idx=sub_idx)

    def dep_recurse(self, *, depth: int) -> dict[str, Any]:
        """Decomposed Prompting recurse."""
        return dep_dep_recurse(depth=depth)

    def dep_swap_symbolic(self, *, module: str) -> dict[str, Any]:
        """Decomposed Prompting swap symbolic."""
        return dep_dep_swap_symbolic(module=module)

    def dep_library_size(self, *, handlers: int) -> dict[str, Any]:
        """Decomposed Prompting library size."""
        return dep_dep_library_size(handlers=handlers)

    def dep_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Decomposed Prompting loop plan."""
        return dep_dep_loop_plan(phase=phase)

    def star_generate(self, *, question: str) -> dict[str, Any]:
        """STaR generate."""
        return star_star_generate(question=question)

    def star_filter_correct(
        self, *, gen_id: str, correct: bool
    ) -> dict[str, Any]:
        """STaR filter correct."""
        return star_star_filter_correct(gen_id=gen_id, correct=correct)

    def star_rationalize(
        self, *, question: str, answer: str
    ) -> dict[str, Any]:
        """STaR rationalize."""
        return star_star_rationalize(question=question, answer=answer)

    def star_finetune_proxy(self, *, examples: int) -> dict[str, Any]:
        """STaR finetune proxy."""
        return star_star_finetune_proxy(examples=examples)

    def star_bootstrap_round(self, *, round_n: int) -> dict[str, Any]:
        """STaR bootstrap round."""
        return star_star_bootstrap_round(round_n=round_n)

    def star_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """STaR loop plan."""
        return star_star_loop_plan(phase=phase)

    def cr_propose(self, *, step: str) -> dict[str, Any]:
        """Cumulative Reasoning propose."""
        return cr_cr_propose(step=step)

    def cr_verify(self, *, proposal_id: str, valid: bool) -> dict[str, Any]:
        """Cumulative Reasoning verify."""
        return cr_cr_verify(proposal_id=proposal_id, valid=valid)

    def cr_accumulate(self, *, accepted: int) -> dict[str, Any]:
        """Cumulative Reasoning accumulate."""
        return cr_cr_accumulate(accepted=accepted)

    def cr_report(self, *, steps: int) -> dict[str, Any]:
        """Cumulative Reasoning report."""
        return cr_cr_report(steps=steps)

    def cr_roles(self, *, roles: int = 3) -> dict[str, Any]:
        """Cumulative Reasoning roles."""
        return cr_cr_roles(roles=roles)

    def cr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Cumulative Reasoning loop plan."""
        return cr_cr_loop_plan(phase=phase)

    def ps_devise_plan(
        self, *, problem: str, subtasks: int
    ) -> dict[str, Any]:
        """Plan-and-Solve devise plan."""
        return ps_ps_devise_plan(problem=problem, subtasks=subtasks)

    def ps_execute(self, *, plan_id: str, step: int) -> dict[str, Any]:
        """Plan-and-Solve execute."""
        return ps_ps_execute(plan_id=plan_id, step=step)

    def ps_plus_extract(self, *, variables: int) -> dict[str, Any]:
        """Plan-and-Solve PS+ extract."""
        return ps_ps_plus_extract(variables=variables)

    def ps_calc_guard(self, *, careful: bool) -> dict[str, Any]:
        """Plan-and-Solve calc guard."""
        return ps_ps_calc_guard(careful=careful)

    def ps_missing_step_fix(self, *, fixed: bool) -> dict[str, Any]:
        """Plan-and-Solve missing-step fix."""
        return ps_ps_missing_step_fix(fixed=fixed)

    def ps_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Plan-and-Solve loop plan."""
        return ps_ps_loop_plan(phase=phase)

    def php_base_answer(self, *, question: str) -> dict[str, Any]:
        """PHP base answer."""
        return php_php_base_answer(question=question)

    def php_emit_hint(
        self, *, answer_id: str, hint: str
    ) -> dict[str, Any]:
        """PHP emit hint."""
        return php_php_emit_hint(answer_id=answer_id, hint=hint)

    def php_reask(self, *, hints: int) -> dict[str, Any]:
        """PHP reask."""
        return php_php_reask(hints=hints)

    def php_stable_stop(self, *, same_twice: bool) -> dict[str, Any]:
        """PHP stable stop."""
        return php_php_stable_stop(same_twice=same_twice)

    def php_combine_sc(self, *, reduced_paths: bool) -> dict[str, Any]:
        """PHP combine with self-consistency."""
        return php_php_combine_sc(reduced_paths=reduced_paths)

    def php_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PHP loop plan."""
        return php_php_loop_plan(phase=phase)

    def ac_programmer(self, *, requirement: str) -> dict[str, Any]:
        """AgentCoder programmer."""
        return ac_ac_programmer(requirement=requirement)

    def ac_test_designer(
        self, *, requirement: str, cases: int
    ) -> dict[str, Any]:
        """AgentCoder test designer."""
        return ac_ac_test_designer(requirement=requirement, cases=cases)

    def ac_test_executor(
        self, *, code_id: str, suite_id: str
    ) -> dict[str, Any]:
        """AgentCoder test executor."""
        return ac_ac_test_executor(code_id=code_id, suite_id=suite_id)

    def ac_refine(
        self, *, code_id: str, feedback_id: str
    ) -> dict[str, Any]:
        """AgentCoder refine."""
        return ac_ac_refine(code_id=code_id, feedback_id=feedback_id)

    def ac_pass_gate(self, *, all_pass: bool) -> dict[str, Any]:
        """AgentCoder pass gate."""
        return ac_ac_pass_gate(all_pass=all_pass)

    def ac_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AgentCoder loop plan."""
        return ac_ac_loop_plan(phase=phase)

    def pal_emit_program(
        self, *, problem: str, lang: str = "python"
    ) -> dict[str, Any]:
        """PAL emit program."""
        return pal_pal_emit_program(problem=problem, lang=lang)

    def pal_offload_solve(self, *, program_id: str) -> dict[str, Any]:
        """PAL offload solve."""
        return pal_pal_offload_solve(program_id=program_id)

    def pal_read_answer(self, *, result_id: str) -> dict[str, Any]:
        """PAL read answer."""
        return pal_pal_read_answer(result_id=result_id)

    def pal_decompose_only(self, *, llm_solves: bool) -> dict[str, Any]:
        """PAL decompose-only flag."""
        return pal_pal_decompose_only(llm_solves=llm_solves)

    def pal_vs_cot(self, *, program_beats_text: bool) -> dict[str, Any]:
        """PAL vs CoT flag."""
        return pal_pal_vs_cot(program_beats_text=program_beats_text)

    def pal_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PAL loop plan."""
        return pal_pal_loop_plan(phase=phase)

    def fcot_translate(
        self, *, query: str, symbolic: str
    ) -> dict[str, Any]:
        """Faithful CoT translate."""
        return fcot_fcot_translate(query=query, symbolic=symbolic)

    def fcot_solve(self, *, chain_id: str) -> dict[str, Any]:
        """Faithful CoT solve."""
        return fcot_fcot_solve(chain_id=chain_id)

    def fcot_faithfulness(
        self, *, chain_explains: bool
    ) -> dict[str, Any]:
        """Faithful CoT faithfulness."""
        return fcot_fcot_faithfulness(chain_explains=chain_explains)

    def fcot_interleave(self, *, nl_sl: bool) -> dict[str, Any]:
        """Faithful CoT interleave."""
        return fcot_fcot_interleave(nl_sl=nl_sl)

    def fcot_vs_cot(self, *, faithful_beats: bool) -> dict[str, Any]:
        """Faithful CoT vs CoT."""
        return fcot_fcot_vs_cot(faithful_beats=faithful_beats)

    def fcot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Faithful CoT loop plan."""
        return fcot_fcot_loop_plan(phase=phase)

    def lats_expand(
        self, *, state: str, actions: int
    ) -> dict[str, Any]:
        """LATS expand."""
        return lats_lats_expand(state=state, actions=actions)

    def lats_value(
        self, *, node_id: str, score: float
    ) -> dict[str, Any]:
        """LATS value."""
        return lats_lats_value(node_id=node_id, score=score)

    def lats_reflect(
        self, *, node_id: str, feedback: str
    ) -> dict[str, Any]:
        """LATS reflect."""
        return lats_lats_reflect(node_id=node_id, feedback=feedback)

    def lats_select(self, *, node_id: str) -> dict[str, Any]:
        """LATS select."""
        return lats_lats_select(node_id=node_id)

    def lats_env_feedback(self, *, useful: bool) -> dict[str, Any]:
        """LATS env feedback."""
        return lats_lats_env_feedback(useful=useful)

    def lats_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LATS loop plan."""
        return lats_lats_loop_plan(phase=phase)

    def voy_curriculum(
        self, *, level: int, task: str
    ) -> dict[str, Any]:
        """Voyager curriculum."""
        return voy_voy_curriculum(level=level, task=task)

    def voy_skill_store(
        self, *, name: str, code_ref: str
    ) -> dict[str, Any]:
        """Voyager skill store."""
        return voy_voy_skill_store(name=name, code_ref=code_ref)

    def voy_skill_retrieve(self, *, query: str) -> dict[str, Any]:
        """Voyager skill retrieve."""
        return voy_voy_skill_retrieve(query=query)

    def voy_self_verify(
        self, *, skill_id: str, passed: bool
    ) -> dict[str, Any]:
        """Voyager self-verify."""
        return voy_voy_self_verify(skill_id=skill_id, passed=passed)

    def voy_compose(self, *, skills: int) -> dict[str, Any]:
        """Voyager compose."""
        return voy_voy_compose(skills=skills)

    def voy_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Voyager loop plan."""
        return voy_voy_loop_plan(phase=phase)

    def rewoo_plan(self, *, task: str, steps: int) -> dict[str, Any]:
        """ReWOO plan."""
        return rewoo_rewoo_plan(task=task, steps=steps)

    def rewoo_worker(
        self, *, plan_id: str, step: int
    ) -> dict[str, Any]:
        """ReWOO worker."""
        return rewoo_rewoo_worker(plan_id=plan_id, step=step)

    def rewoo_solver(
        self, *, plan_id: str, evidence: int
    ) -> dict[str, Any]:
        """ReWOO solver."""
        return rewoo_rewoo_solver(plan_id=plan_id, evidence=evidence)

    def rewoo_decouple(
        self, *, from_observation: bool
    ) -> dict[str, Any]:
        """ReWOO decouple."""
        return rewoo_rewoo_decouple(from_observation=from_observation)

    def rewoo_token_save(self, *, reduced: bool) -> dict[str, Any]:
        """ReWOO token save."""
        return rewoo_rewoo_token_save(reduced=reduced)

    def rewoo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ReWOO loop plan."""
        return rewoo_rewoo_loop_plan(phase=phase)

    def critic_draft(self, *, question: str) -> dict[str, Any]:
        """CRITIC draft."""
        return critic_critic_draft(question=question)

    def critic_tool_check(
        self, *, draft_id: str, tool: str
    ) -> dict[str, Any]:
        """CRITIC tool check."""
        return critic_critic_tool_check(draft_id=draft_id, tool=tool)

    def critic_revise(
        self, *, draft_id: str, critique_id: str
    ) -> dict[str, Any]:
        """CRITIC revise."""
        return critic_critic_revise(
            draft_id=draft_id, critique_id=critique_id
        )

    def critic_iterate(self, *, rounds: int) -> dict[str, Any]:
        """CRITIC iterate."""
        return critic_critic_iterate(rounds=rounds)

    def critic_stop(self, *, satisfied: bool) -> dict[str, Any]:
        """CRITIC stop."""
        return critic_critic_stop(satisfied=satisfied)

    def critic_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CRITIC loop plan."""
        return critic_critic_loop_plan(phase=phase)

    def dv_natural_program(
        self, *, claim: str, steps: int
    ) -> dict[str, Any]:
        """Deductive Natural Program."""
        return dv_dv_natural_program(claim=claim, steps=steps)

    def dv_step_verify(
        self, *, program_id: str, step: int
    ) -> dict[str, Any]:
        """Deductive step verify."""
        return dv_dv_step_verify(program_id=program_id, step=step)

    def dv_premise_scope(self, *, premises: int) -> dict[str, Any]:
        """Deductive premise scope."""
        return dv_dv_premise_scope(premises=premises)

    def dv_unanimity(self, *, all_pass: bool) -> dict[str, Any]:
        """Deductive unanimity."""
        return dv_dv_unanimity(all_pass=all_pass)

    def dv_ground(self, *, grounded: bool) -> dict[str, Any]:
        """Deductive ground."""
        return dv_dv_ground(grounded=grounded)

    def dv_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Deductive loop plan."""
        return dv_dv_loop_plan(phase=phase)

    def hgpt_plan(self, *, request: str, tasks: int) -> dict[str, Any]:
        """HuggingGPT plan."""
        return hgpt_hgpt_plan(request=request, tasks=tasks)

    def hgpt_select(
        self, *, plan_id: str, model: str
    ) -> dict[str, Any]:
        """HuggingGPT select."""
        return hgpt_hgpt_select(plan_id=plan_id, model=model)

    def hgpt_execute(self, *, selection_id: str) -> dict[str, Any]:
        """HuggingGPT execute."""
        return hgpt_hgpt_execute(selection_id=selection_id)

    def hgpt_summarize(self, *, results: int) -> dict[str, Any]:
        """HuggingGPT summarize."""
        return hgpt_hgpt_summarize(results=results)

    def hgpt_modality(self, *, modalities: int) -> dict[str, Any]:
        """HuggingGPT modality."""
        return hgpt_hgpt_modality(modalities=modalities)

    def hgpt_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HuggingGPT loop plan."""
        return hgpt_hgpt_loop_plan(phase=phase)

    def mad_propose(self, *, agent: str, answer: str) -> dict[str, Any]:
        """Multiagent Debate propose."""
        return mad_mad_propose(agent=agent, answer=answer)

    def mad_debate(
        self, *, round_n: int, agents: int
    ) -> dict[str, Any]:
        """Multiagent Debate round."""
        return mad_mad_debate(round_n=round_n, agents=agents)

    def mad_critique(
        self, *, proposal_id: str, critique: str
    ) -> dict[str, Any]:
        """Multiagent Debate critique."""
        return mad_mad_critique(proposal_id=proposal_id, critique=critique)

    def mad_converge(self, *, common: bool) -> dict[str, Any]:
        """Multiagent Debate converge."""
        return mad_mad_converge(common=common)

    def mad_factuality(self, *, improved: bool) -> dict[str, Any]:
        """Multiagent Debate factuality."""
        return mad_mad_factuality(improved=improved)

    def mad_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Multiagent Debate loop plan."""
        return mad_mad_loop_plan(phase=phase)

    def autocot_cluster(
        self, *, questions: int, clusters: int
    ) -> dict[str, Any]:
        """Auto-CoT cluster."""
        return autocot_autocot_cluster(
            questions=questions, clusters=clusters
        )

    def autocot_sample(self, *, cluster_id: str) -> dict[str, Any]:
        """Auto-CoT sample."""
        return autocot_autocot_sample(cluster_id=cluster_id)

    def autocot_generate(self, *, demo_id: str) -> dict[str, Any]:
        """Auto-CoT generate."""
        return autocot_autocot_generate(demo_id=demo_id)

    def autocot_heuristic(self, *, max_steps: int) -> dict[str, Any]:
        """Auto-CoT heuristic."""
        return autocot_autocot_heuristic(max_steps=max_steps)

    def autocot_diversity(self, *, diverse: bool) -> dict[str, Any]:
        """Auto-CoT diversity."""
        return autocot_autocot_diversity(diverse=diverse)

    def autocot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Auto-CoT loop plan."""
        return autocot_autocot_loop_plan(phase=phase)

    def camel_roles(
        self, *, user_role: str, assistant_role: str
    ) -> dict[str, Any]:
        """CAMEL roles."""
        return camel_camel_roles(
            user_role=user_role, assistant_role=assistant_role
        )

    def camel_inception(
        self, *, role_id: str, task: str
    ) -> dict[str, Any]:
        """CAMEL inception."""
        return camel_camel_inception(role_id=role_id, task=task)

    def camel_turn(
        self, *, inception_id: str, speaker: str
    ) -> dict[str, Any]:
        """CAMEL turn."""
        return camel_camel_turn(inception_id=inception_id, speaker=speaker)

    def camel_complete(self, *, done: bool) -> dict[str, Any]:
        """CAMEL complete."""
        return camel_camel_complete(done=done)

    def camel_society(self, *, agents: int) -> dict[str, Any]:
        """CAMEL society."""
        return camel_camel_society(agents=agents)

    def camel_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CAMEL loop plan."""
        return camel_camel_loop_plan(phase=phase)

    def cham_inventory(self, *, tools: int) -> dict[str, Any]:
        """Chameleon inventory."""
        return cham_cham_inventory(tools=tools)

    def cham_plan(self, *, task: str, modules: int) -> dict[str, Any]:
        """Chameleon plan."""
        return cham_cham_plan(task=task, modules=modules)

    def cham_compose(
        self, *, plan_id: str, module: str
    ) -> dict[str, Any]:
        """Chameleon compose."""
        return cham_cham_compose(plan_id=plan_id, module=module)

    def cham_execute(self, *, plan_id: str) -> dict[str, Any]:
        """Chameleon execute."""
        return cham_cham_execute(plan_id=plan_id)

    def cham_constraint(self, *, inferred: bool) -> dict[str, Any]:
        """Chameleon constraint."""
        return cham_cham_constraint(inferred=inferred)

    def cham_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Chameleon loop plan."""
        return cham_cham_loop_plan(phase=phase)

    def rot_trigger(self, *, token: str) -> dict[str, Any]:
        """RoT trigger."""
        return rot_rot_trigger(token=token)

    def rot_divide(self, *, problem: str, parts: int) -> dict[str, Any]:
        """RoT divide."""
        return rot_rot_divide(problem=problem, parts=parts)

    def rot_conquer(
        self, *, divide_id: str, part: int
    ) -> dict[str, Any]:
        """RoT conquer."""
        return rot_rot_conquer(divide_id=divide_id, part=part)

    def rot_merge(self, *, parts: int) -> dict[str, Any]:
        """RoT merge."""
        return rot_rot_merge(parts=parts)

    def rot_context_limit(self, *, within_limit: bool) -> dict[str, Any]:
        """RoT context limit."""
        return rot_rot_context_limit(within_limit=within_limit)

    def rot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RoT loop plan."""
        return rot_rot_loop_plan(phase=phase)

    def ap_sample(self, *, question: str, k: int) -> dict[str, Any]:
        """Active-Prompt sample."""
        return ap_ap_sample(question=question, k=k)

    def ap_uncertainty(
        self, *, sample_id: str, score: float
    ) -> dict[str, Any]:
        """Active-Prompt uncertainty."""
        return ap_ap_uncertainty(sample_id=sample_id, score=score)

    def ap_select(self, *, top_n: int) -> dict[str, Any]:
        """Active-Prompt select."""
        return ap_ap_select(top_n=top_n)

    def ap_annotate(
        self, *, question_id: str, cot: str
    ) -> dict[str, Any]:
        """Active-Prompt annotate."""
        return ap_ap_annotate(question_id=question_id, cot=cot)

    def ap_pool(self, *, size: int) -> dict[str, Any]:
        """Active-Prompt pool."""
        return ap_ap_pool(size=size)

    def ap_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Active-Prompt loop plan."""
        return ap_ap_loop_plan(phase=phase)

    def ana_recall(self, *, problem: str) -> dict[str, Any]:
        """Analogical recall."""
        return ana_ana_recall(problem=problem)

    def ana_knowledge(
        self, *, problem: str, facts: int
    ) -> dict[str, Any]:
        """Analogical knowledge."""
        return ana_ana_knowledge(problem=problem, facts=facts)

    def ana_solve(self, *, exemplar_id: str) -> dict[str, Any]:
        """Analogical solve."""
        return ana_ana_solve(exemplar_id=exemplar_id)

    def ana_adapt(self, *, tailored: bool) -> dict[str, Any]:
        """Analogical adapt."""
        return ana_ana_adapt(tailored=tailored)

    def ana_no_label(self, *, needs_labels: bool) -> dict[str, Any]:
        """Analogical no-label flag."""
        return ana_ana_no_label(needs_labels=needs_labels)

    def ana_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Analogical loop plan."""
        return ana_ana_loop_plan(phase=phase)

    def cbp_score(self, *, steps: int) -> dict[str, Any]:
        """Complexity-Based score."""
        return cbp_cbp_score(steps=steps)

    def cbp_select(
        self, *, min_steps: int, exemplars: int
    ) -> dict[str, Any]:
        """Complexity-Based select."""
        return cbp_cbp_select(min_steps=min_steps, exemplars=exemplars)

    def cbp_sample_chains(self, *, n: int) -> dict[str, Any]:
        """Complexity-Based sample chains."""
        return cbp_cbp_sample_chains(n=n)

    def cbp_vote_complex(self, *, prefer_complex: bool) -> dict[str, Any]:
        """Complexity-Based vote."""
        return cbp_cbp_vote_complex(prefer_complex=prefer_complex)

    def cbp_robust(self, *, under_shift: bool) -> dict[str, Any]:
        """Complexity-Based robust."""
        return cbp_cbp_robust(under_shift=under_shift)

    def cbp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Complexity-Based loop plan."""
        return cbp_cbp_loop_plan(phase=phase)

    def sb_abstract(self, *, instance: str) -> dict[str, Any]:
        """Step-Back abstract."""
        return sb_sb_abstract(instance=instance)

    def sb_principle(
        self, *, concept_id: str, principle: str
    ) -> dict[str, Any]:
        """Step-Back principle."""
        return sb_sb_principle(concept_id=concept_id, principle=principle)

    def sb_reason(self, *, principle_id: str) -> dict[str, Any]:
        """Step-Back reason."""
        return sb_sb_reason(principle_id=principle_id)

    def sb_path(self, *, correct_path: bool) -> dict[str, Any]:
        """Step-Back path."""
        return sb_sb_path(correct_path=correct_path)

    def sb_detail_trap(self, *, escaped: bool) -> dict[str, Any]:
        """Step-Back detail trap."""
        return sb_sb_detail_trap(escaped=escaped)

    def sb_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Step-Back loop plan."""
        return sb_sb_loop_plan(phase=phase)

    def mmcot_fuse(
        self, *, text: str, vision_ref: str
    ) -> dict[str, Any]:
        """Multimodal-CoT fuse."""
        return mmcot_mmcot_fuse(text=text, vision_ref=vision_ref)

    def mmcot_rationale(self, *, fuse_id: str) -> dict[str, Any]:
        """Multimodal-CoT rationale."""
        return mmcot_mmcot_rationale(fuse_id=fuse_id)

    def mmcot_infer(self, *, rationale_id: str) -> dict[str, Any]:
        """Multimodal-CoT infer."""
        return mmcot_mmcot_infer(rationale_id=rationale_id)

    def mmcot_hallucination(self, *, mitigated: bool) -> dict[str, Any]:
        """Multimodal-CoT hallucination flag."""
        return mmcot_mmcot_hallucination(mitigated=mitigated)

    def mmcot_separate(self, *, two_stage: bool) -> dict[str, Any]:
        """Multimodal-CoT separate stages."""
        return mmcot_mmcot_separate(two_stage=two_stage)

    def mmcot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Multimodal-CoT loop plan."""
        return mmcot_mmcot_loop_plan(phase=phase)

    def mai_abduce(
        self, *, claim: str, because: str
    ) -> dict[str, Any]:
        """Maieutic abduce."""
        return mai_mai_abduce(claim=claim, because=because)

    def mai_recurse(
        self, *, node_id: str, depth: int
    ) -> dict[str, Any]:
        """Maieutic recurse."""
        return mai_mai_recurse(node_id=node_id, depth=depth)

    def mai_sat(self, *, relations: int) -> dict[str, Any]:
        """Maieutic SAT."""
        return mai_mai_sat(relations=relations)

    def mai_consistent(self, *, consistent: bool) -> dict[str, Any]:
        """Maieutic consistent."""
        return mai_mai_consistent(consistent=consistent)

    def mai_unreliable(self, *, tolerate: bool) -> dict[str, Any]:
        """Maieutic unreliable tolerance."""
        return mai_mai_unreliable(tolerate=tolerate)

    def mai_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Maieutic loop plan."""
        return mai_mai_loop_plan(phase=phase)

    def sr_generate(self, *, draft: str) -> dict[str, Any]:
        """Self-Refine generate."""
        return sr_sr_generate(draft=draft)

    def sr_feedback(self, *, gen_id: str) -> dict[str, Any]:
        """Self-Refine feedback."""
        return sr_sr_feedback(gen_id=gen_id)

    def sr_refine(
        self, *, gen_id: str, feedback_id: str
    ) -> dict[str, Any]:
        """Self-Refine refine."""
        return sr_sr_refine(gen_id=gen_id, feedback_id=feedback_id)

    def sr_iterate(self, *, rounds: int) -> dict[str, Any]:
        """Self-Refine iterate."""
        return sr_sr_iterate(rounds=rounds)

    def sr_no_train(self, *, no_rl: bool) -> dict[str, Any]:
        """Self-Refine no-train flag."""
        return sr_sr_no_train(no_rl=no_rl)

    def sr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Self-Refine loop plan."""
        return sr_sr_loop_plan(phase=phase)

    def mcp_recognize(self, *, knowledge: str) -> dict[str, Any]:
        """Metacognitive recognize."""
        return mcp_mcp_recognize(knowledge=knowledge)

    def mcp_interpret(self, *, recognize_id: str) -> dict[str, Any]:
        """Metacognitive interpret."""
        return mcp_mcp_interpret(recognize_id=recognize_id)

    def mcp_reevaluate(self, *, interpret_id: str) -> dict[str, Any]:
        """Metacognitive reevaluate."""
        return mcp_mcp_reevaluate(interpret_id=interpret_id)

    def mcp_confidence(self, *, score: int) -> dict[str, Any]:
        """Metacognitive confidence."""
        return mcp_mcp_confidence(score=score)

    def mcp_justify(self, *, justified: bool) -> dict[str, Any]:
        """Metacognitive justify."""
        return mcp_mcp_justify(justified=justified)

    def mcp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Metacognitive loop plan."""
        return mcp_mcp_loop_plan(phase=phase)

    def thot_segment(
        self, *, context: str, pieces: int
    ) -> dict[str, Any]:
        """Thread of Thought segment."""
        return thot_thot_segment(context=context, pieces=pieces)

    def thot_analyze(self, *, segment_id: str) -> dict[str, Any]:
        """Thread of Thought analyze."""
        return thot_thot_analyze(segment_id=segment_id)

    def thot_select(self, *, analyze_id: str) -> dict[str, Any]:
        """Thread of Thought select."""
        return thot_thot_select(analyze_id=analyze_id)

    def thot_synthesize(self, *, select_id: str) -> dict[str, Any]:
        """Thread of Thought synthesize."""
        return thot_thot_synthesize(select_id=select_id)

    def thot_plug(self, *, plug_and_play: bool) -> dict[str, Any]:
        """Thread of Thought plug flag."""
        return thot_thot_plug(plug_and_play=plug_and_play)

    def thot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Thread of Thought loop plan."""
        return thot_thot_loop_plan(phase=phase)

    def tprop_propose(self, *, problem: str) -> dict[str, Any]:
        """Thought Propagation propose."""
        return tprop_tprop_propose(problem=problem)

    def tprop_solve(self, *, propose_id: str) -> dict[str, Any]:
        """Thought Propagation solve."""
        return tprop_tprop_solve(propose_id=propose_id)

    def tprop_reuse(self, *, analog_id: str) -> dict[str, Any]:
        """Thought Propagation reuse."""
        return tprop_tprop_reuse(analog_id=analog_id)

    def tprop_amend(self, *, reuse_id: str) -> dict[str, Any]:
        """Thought Propagation amend."""
        return tprop_tprop_amend(reuse_id=reuse_id)

    def tprop_compat(self, *, plug_and_play: bool) -> dict[str, Any]:
        """Thought Propagation compat flag."""
        return tprop_tprop_compat(plug_and_play=plug_and_play)

    def tprop_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Thought Propagation loop plan."""
        return tprop_tprop_loop_plan(phase=phase)

    def s2a_regenerate(self, *, context: str) -> dict[str, Any]:
        """System 2 Attention regenerate."""
        return s2a_s2a_regenerate(context=context)

    def s2a_attend(self, *, regen_id: str) -> dict[str, Any]:
        """System 2 Attention attend."""
        return s2a_s2a_attend(regen_id=regen_id)

    def s2a_respond(self, *, attend_id: str) -> dict[str, Any]:
        """System 2 Attention respond."""
        return s2a_s2a_respond(attend_id=attend_id)

    def s2a_factuality(self, *, score: int) -> dict[str, Any]:
        """System 2 Attention factuality."""
        return s2a_s2a_factuality(score=score)

    def s2a_sycophancy(self, *, reduced: bool) -> dict[str, Any]:
        """System 2 Attention sycophancy flag."""
        return s2a_s2a_sycophancy(reduced=reduced)

    def s2a_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """System 2 Attention loop plan."""
        return s2a_s2a_loop_plan(phase=phase)

    def ccot_valid(self, *, demo: str) -> dict[str, Any]:
        """Contrastive CoT valid demo."""
        return ccot_ccot_valid(demo=demo)

    def ccot_invalid(self, *, demo: str) -> dict[str, Any]:
        """Contrastive CoT invalid demo."""
        return ccot_ccot_invalid(demo=demo)

    def ccot_contrast(
        self, *, valid_id: str, invalid_id: str
    ) -> dict[str, Any]:
        """Contrastive CoT contrast."""
        return ccot_ccot_contrast(valid_id=valid_id, invalid_id=invalid_id)

    def ccot_reason(self, *, contrast_id: str) -> dict[str, Any]:
        """Contrastive CoT reason."""
        return ccot_ccot_reason(contrast_id=contrast_id)

    def ccot_auto(self, *, construct: bool) -> dict[str, Any]:
        """Contrastive CoT auto construct."""
        return ccot_ccot_auto(construct=construct)

    def ccot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Contrastive CoT loop plan."""
        return ccot_ccot_loop_plan(phase=phase)

    def tabcot_header(self, *, columns: str) -> dict[str, Any]:
        """Tab-CoT header."""
        return tabcot_tabcot_header(columns=columns)

    def tabcot_row(
        self, *, header_id: str, step: int
    ) -> dict[str, Any]:
        """Tab-CoT row."""
        return tabcot_tabcot_row(header_id=header_id, step=step)

    def tabcot_infer2d(self, *, rows: int) -> dict[str, Any]:
        """Tab-CoT 2D infer."""
        return tabcot_tabcot_infer2d(rows=rows)

    def tabcot_extract(self, *, row_id: str) -> dict[str, Any]:
        """Tab-CoT extract."""
        return tabcot_tabcot_extract(row_id=row_id)

    def tabcot_zeroshot(self, *, zero_shot: bool) -> dict[str, Any]:
        """Tab-CoT zeroshot flag."""
        return tabcot_tabcot_zeroshot(zero_shot=zero_shot)

    def tabcot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Tab-CoT loop plan."""
        return tabcot_tabcot_loop_plan(phase=phase)

    def xot_mcts(self, *, problem: str) -> dict[str, Any]:
        """XoT MCTS."""
        return xot_xot_mcts(problem=problem)

    def xot_revise(self, *, mcts_id: str) -> dict[str, Any]:
        """XoT revise."""
        return xot_xot_revise(mcts_id=mcts_id)

    def xot_map(self, *, revise_id: str) -> dict[str, Any]:
        """XoT map."""
        return xot_xot_map(revise_id=revise_id)

    def xot_penrose(self, *, defy: bool) -> dict[str, Any]:
        """XoT penrose."""
        return xot_xot_penrose(defy=defy)

    def xot_flexible(self, *, multi_solution: bool) -> dict[str, Any]:
        """XoT flexible flag."""
        return xot_xot_flexible(multi_solution=multi_solution)

    def xot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """XoT loop plan."""
        return xot_xot_loop_plan(phase=phase)

    def cove_draft(self, *, claim: str) -> dict[str, Any]:
        """CoVe draft."""
        return cove_cove_draft(claim=claim)

    def cove_plan(self, *, draft_id: str) -> dict[str, Any]:
        """CoVe plan."""
        return cove_cove_plan(draft_id=draft_id)

    def cove_answer(self, *, plan_id: str) -> dict[str, Any]:
        """CoVe answer."""
        return cove_cove_answer(plan_id=plan_id)

    def cove_final(self, *, verify_id: str) -> dict[str, Any]:
        """CoVe final."""
        return cove_cove_final(verify_id=verify_id)

    def cove_hallucination(self, *, reduced: bool) -> dict[str, Any]:
        """CoVe hallucination flag."""
        return cove_cove_hallucination(reduced=reduced)

    def cove_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CoVe loop plan."""
        return cove_cove_loop_plan(phase=phase)

    def ved_uncertain(self, *, consistency: int) -> dict[str, Any]:
        """Verify-and-Edit uncertain."""
        return ved_ved_uncertain(consistency=consistency)

    def ved_search(self, *, query: str) -> dict[str, Any]:
        """Verify-and-Edit search."""
        return ved_ved_search(query=query)

    def ved_edit(
        self, *, fact_id: str, rationale: str
    ) -> dict[str, Any]:
        """Verify-and-Edit edit."""
        return ved_ved_edit(fact_id=fact_id, rationale=rationale)

    def ved_predict(self, *, edit_id: str) -> dict[str, Any]:
        """Verify-and-Edit predict."""
        return ved_ved_predict(edit_id=edit_id)

    def ved_knowledge(self, *, enhanced: bool) -> dict[str, Any]:
        """Verify-and-Edit knowledge flag."""
        return ved_ved_knowledge(enhanced=enhanced)

    def ved_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Verify-and-Edit loop plan."""
        return ved_ved_loop_plan(phase=phase)

    def sve_forward(self, *, problem: str) -> dict[str, Any]:
        """Self-Verification forward."""
        return sve_sve_forward(problem=problem)

    def sve_mask(self, *, candidate_id: str) -> dict[str, Any]:
        """Self-Verification mask."""
        return sve_sve_mask(candidate_id=candidate_id)

    def sve_repredict(self, *, mask_id: str) -> dict[str, Any]:
        """Self-Verification repredict."""
        return sve_sve_repredict(mask_id=mask_id)

    def sve_score(self, *, score: int) -> dict[str, Any]:
        """Self-Verification score."""
        return sve_sve_score(score=score)

    def sve_select(self, *, pick_best: bool) -> dict[str, Any]:
        """Self-Verification select."""
        return sve_sve_select(pick_best=pick_best)

    def sve_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Self-Verification loop plan."""
        return sve_sve_loop_plan(phase=phase)

    def cod_sparse(self, *, source: str) -> dict[str, Any]:
        """Chain of Density sparse."""
        return cod_cod_sparse(source=source)

    def cod_entities(
        self, *, sparse_id: str, count: int
    ) -> dict[str, Any]:
        """Chain of Density entities."""
        return cod_cod_entities(sparse_id=sparse_id, count=count)

    def cod_fuse(self, *, entity_id: str) -> dict[str, Any]:
        """Chain of Density fuse."""
        return cod_cod_fuse(entity_id=entity_id)

    def cod_length(self, *, fixed: bool) -> dict[str, Any]:
        """Chain of Density length."""
        return cod_cod_length(fixed=fixed)

    def cod_tradeoff(self, *, prefer_dense: bool) -> dict[str, Any]:
        """Chain of Density tradeoff."""
        return cod_cod_tradeoff(prefer_dense=prefer_dense)

    def cod_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Chain of Density loop plan."""
        return cod_cod_loop_plan(phase=phase)

    def hsp_hint(self, *, problem: str) -> dict[str, Any]:
        """HSP hint."""
        return hsp_hsp_hint(problem=problem)

    def hsp_solve(self, *, hint_id: str) -> dict[str, Any]:
        """HSP solve."""
        return hsp_hsp_solve(hint_id=hint_id)

    def hsp_answer(self, *, solve_id: str) -> dict[str, Any]:
        """HSP answer."""
        return hsp_hsp_answer(solve_id=solve_id)

    def hsp_compose(self, *, base: str) -> dict[str, Any]:
        """HSP compose."""
        return hsp_hsp_compose(base=base)

    def hsp_quality(self, *, high_quality: bool) -> dict[str, Any]:
        """HSP quality flag."""
        return hsp_hsp_quality(high_quality=high_quality)

    def hsp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HSP loop plan."""
        return hsp_hsp_loop_plan(phase=phase)

    def emo_stimulus(self, *, text: str) -> dict[str, Any]:
        """EmotionPrompt stimulus."""
        return emo_emo_stimulus(text=text)

    def emo_append(
        self, *, prompt: str, stimulus_id: str
    ) -> dict[str, Any]:
        """EmotionPrompt append."""
        return emo_emo_append(prompt=prompt, stimulus_id=stimulus_id)

    def emo_run(self, *, prompt_id: str) -> dict[str, Any]:
        """EmotionPrompt run."""
        return emo_emo_run(prompt_id=prompt_id)

    def emo_truth(self, *, improved: bool) -> dict[str, Any]:
        """EmotionPrompt truth."""
        return emo_emo_truth(improved=improved)

    def emo_psych(self, *, psychology: bool) -> dict[str, Any]:
        """EmotionPrompt psych flag."""
        return emo_emo_psych(psychology=psychology)

    def emo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """EmotionPrompt loop plan."""
        return emo_emo_loop_plan(phase=phase)

    def ape_propose(self, *, demos: str) -> dict[str, Any]:
        """APE propose."""
        return ape_ape_propose(demos=demos)

    def ape_score(self, *, pool_id: str) -> dict[str, Any]:
        """APE score."""
        return ape_ape_score(pool_id=pool_id)

    def ape_select(self, *, score_id: str) -> dict[str, Any]:
        """APE select."""
        return ape_ape_select(score_id=score_id)

    def ape_steer(self, *, instr_id: str) -> dict[str, Any]:
        """APE steer."""
        return ape_ape_steer(instr_id=instr_id)

    def ape_human(self, *, match_human: bool) -> dict[str, Any]:
        """APE human-parity flag."""
        return ape_ape_human(match_human=match_human)

    def ape_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """APE loop plan."""
        return ape_ape_loop_plan(phase=phase)

    def pbr_init(self, *, task: str) -> dict[str, Any]:
        """Promptbreeder init."""
        return pbr_pbr_init(task=task)

    def pbr_mutate(self, *, pop_id: str) -> dict[str, Any]:
        """Promptbreeder mutate."""
        return pbr_pbr_mutate(pop_id=pop_id)

    def pbr_fitness(
        self, *, mut_id: str, score: int
    ) -> dict[str, Any]:
        """Promptbreeder fitness."""
        return pbr_pbr_fitness(mut_id=mut_id, score=score)

    def pbr_diversity(self, *, maintain: bool) -> dict[str, Any]:
        """Promptbreeder diversity."""
        return pbr_pbr_diversity(maintain=maintain)

    def pbr_selfref(self, *, self_improve: bool) -> dict[str, Any]:
        """Promptbreeder selfref flag."""
        return pbr_pbr_selfref(self_improve=self_improve)

    def pbr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Promptbreeder loop plan."""
        return pbr_pbr_loop_plan(phase=phase)

    def opro_meta(self, *, task: str) -> dict[str, Any]:
        """OPRO meta."""
        return opro_opro_meta(task=task)

    def opro_propose(self, *, meta_id: str) -> dict[str, Any]:
        """OPRO propose."""
        return opro_opro_propose(meta_id=meta_id)

    def opro_score(self, *, cand_id: str, score: int) -> dict[str, Any]:
        """OPRO score."""
        return opro_opro_score(cand_id=cand_id, score=score)

    def opro_append(self, *, score_id: str) -> dict[str, Any]:
        """OPRO append."""
        return opro_opro_append(score_id=score_id)

    def opro_best(self, *, beat_human: bool) -> dict[str, Any]:
        """OPRO best-vs-human flag."""
        return opro_opro_best(beat_human=beat_human)

    def opro_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """OPRO loop plan."""
        return opro_opro_loop_plan(phase=phase)

    def evp_init(self, *, task: str) -> dict[str, Any]:
        """EvoPrompt init."""
        return evp_evp_init(task=task)

    def evp_cross(self, *, pop_id: str) -> dict[str, Any]:
        """EvoPrompt crossover."""
        return evp_evp_cross(pop_id=pop_id)

    def evp_mutate(self, *, cross_id: str) -> dict[str, Any]:
        """EvoPrompt mutate."""
        return evp_evp_mutate(cross_id=cross_id)

    def evp_select(
        self, *, mut_id: str, score: int
    ) -> dict[str, Any]:
        """EvoPrompt select."""
        return evp_evp_select(mut_id=mut_id, score=score)

    def evp_ea(self, *, connect_ea: bool) -> dict[str, Any]:
        """EvoPrompt EA-connect flag."""
        return evp_evp_ea(connect_ea=connect_ea)

    def evp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """EvoPrompt loop plan."""
        return evp_evp_loop_plan(phase=phase)

    def ptg_gradient(self, *, prompt: str) -> dict[str, Any]:
        """ProTeGi gradient."""
        return ptg_ptg_gradient(prompt=prompt)

    def ptg_edit(self, *, grad_id: str) -> dict[str, Any]:
        """ProTeGi edit."""
        return ptg_ptg_edit(grad_id=grad_id)

    def ptg_beam(self, *, edit_id: str) -> dict[str, Any]:
        """ProTeGi beam."""
        return ptg_ptg_beam(edit_id=edit_id)

    def ptg_bandit(
        self, *, beam_id: str, score: int
    ) -> dict[str, Any]:
        """ProTeGi bandit."""
        return ptg_ptg_bandit(beam_id=beam_id, score=score)

    def ptg_jailbreak(self, *, detect: bool) -> dict[str, Any]:
        """ProTeGi jailbreak flag."""
        return ptg_ptg_jailbreak(detect=detect)

    def ptg_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ProTeGi loop plan."""
        return ptg_ptg_loop_plan(phase=phase)

    def pag_state(self, *, prompt: str) -> dict[str, Any]:
        """PromptAgent state."""
        return pag_pag_state(prompt=prompt)

    def pag_reflect(self, *, state_id: str) -> dict[str, Any]:
        """PromptAgent reflect."""
        return pag_pag_reflect(state_id=state_id)

    def pag_expand(self, *, reflect_id: str) -> dict[str, Any]:
        """PromptAgent expand."""
        return pag_pag_expand(reflect_id=reflect_id)

    def pag_backprop(
        self, *, expand_id: str, reward: int
    ) -> dict[str, Any]:
        """PromptAgent backprop."""
        return pag_pag_backprop(expand_id=expand_id, reward=reward)

    def pag_expert(self, *, expert_level: bool) -> dict[str, Any]:
        """PromptAgent expert flag."""
        return pag_pag_expert(expert_level=expert_level)

    def pag_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PromptAgent loop plan."""
        return pag_pag_loop_plan(phase=phase)

    def mapo_posgrad(self, *, prompt: str) -> dict[str, Any]:
        """MAPO positive gradient."""
        return mapo_mapo_posgrad(prompt=prompt)

    def mapo_momentum(self, *, pos_id: str) -> dict[str, Any]:
        """MAPO momentum."""
        return mapo_mapo_momentum(pos_id=pos_id)

    def mapo_beam(self, *, mom_id: str) -> dict[str, Any]:
        """MAPO beam."""
        return mapo_mapo_beam(mom_id=mom_id)

    def mapo_ucb(self, *, beam_id: str, score: int) -> dict[str, Any]:
        """MAPO UCB."""
        return mapo_mapo_ucb(beam_id=beam_id, score=score)

    def mapo_faster(self, *, beat_protegi: bool) -> dict[str, Any]:
        """MAPO vs-ProTeGi flag."""
        return mapo_mapo_faster(beat_protegi=beat_protegi)

    def mapo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MAPO loop plan."""
        return mapo_mapo_loop_plan(phase=phase)

    def grips_seed(self, *, instruction: str) -> dict[str, Any]:
        """GrIPS seed."""
        return grips_grips_seed(instruction=instruction)

    def grips_edit(self, *, seed_id: str, op: str) -> dict[str, Any]:
        """GrIPS edit."""
        return grips_grips_edit(seed_id=seed_id, op=op)

    def grips_score(
        self, *, edit_id: str, score: int
    ) -> dict[str, Any]:
        """GrIPS score."""
        return grips_grips_score(edit_id=edit_id, score=score)

    def grips_accept(self, *, score_id: str) -> dict[str, Any]:
        """GrIPS accept."""
        return grips_grips_accept(score_id=score_id)

    def grips_api(self, *, api_tunable: bool) -> dict[str, Any]:
        """GrIPS API-tunable flag."""
        return grips_grips_api(api_tunable=api_tunable)

    def grips_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GrIPS loop plan."""
        return grips_grips_loop_plan(phase=phase)

    def tmpa_state(self, *, prompt: str, query: str) -> dict[str, Any]:
        """TEMPERA state."""
        return tmpa_tmpa_state(prompt=prompt, query=query)

    def tmpa_act(
        self, *, state_id: str, component: str
    ) -> dict[str, Any]:
        """TEMPERA act."""
        return tmpa_tmpa_act(state_id=state_id, component=component)

    def tmpa_reward(
        self, *, act_id: str, score: int
    ) -> dict[str, Any]:
        """TEMPERA reward."""
        return tmpa_tmpa_reward(act_id=act_id, score=score)

    def tmpa_adapt(self, *, reward_id: str) -> dict[str, Any]:
        """TEMPERA adapt."""
        return tmpa_tmpa_adapt(reward_id=reward_id)

    def tmpa_efficiency(
        self, *, sample_efficient: bool
    ) -> dict[str, Any]:
        """TEMPERA efficiency flag."""
        return tmpa_tmpa_efficiency(sample_efficient=sample_efficient)

    def tmpa_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """TEMPERA loop plan."""
        return tmpa_tmpa_loop_plan(phase=phase)

    def rlp_init(self, *, task: str) -> dict[str, Any]:
        """RLPrompt init."""
        return rlp_rlp_init(task=task)

    def rlp_sample(self, *, policy_id: str) -> dict[str, Any]:
        """RLPrompt sample."""
        return rlp_rlp_sample(policy_id=policy_id)

    def rlp_reward(
        self, *, sample_id: str, score: int
    ) -> dict[str, Any]:
        """RLPrompt reward."""
        return rlp_rlp_reward(sample_id=sample_id, score=score)

    def rlp_update(self, *, reward_id: str) -> dict[str, Any]:
        """RLPrompt update."""
        return rlp_rlp_update(reward_id=reward_id)

    def rlp_discrete(self, *, discrete: bool) -> dict[str, Any]:
        """RLPrompt discrete flag."""
        return rlp_rlp_discrete(discrete=discrete)

    def rlp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RLPrompt loop plan."""
        return rlp_rlp_loop_plan(phase=phase)

    def aup_template(self, *, template: str) -> dict[str, Any]:
        """AutoPrompt template."""
        return aup_aup_template(template=template)

    def aup_trigger(self, *, tmpl_id: str) -> dict[str, Any]:
        """AutoPrompt trigger."""
        return aup_aup_trigger(tmpl_id=tmpl_id)

    def aup_search(self, *, trig_id: str) -> dict[str, Any]:
        """AutoPrompt search."""
        return aup_aup_search(trig_id=trig_id)

    def aup_score(
        self, *, search_id: str, score: int
    ) -> dict[str, Any]:
        """AutoPrompt score."""
        return aup_aup_score(search_id=search_id, score=score)

    def aup_probe(self, *, parameter_free: bool) -> dict[str, Any]:
        """AutoPrompt probe flag."""
        return aup_aup_probe(parameter_free=parameter_free)

    def aup_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AutoPrompt loop plan."""
        return aup_aup_loop_plan(phase=phase)

    def pfx_task(self, *, task: str) -> dict[str, Any]:
        """Prefix-Tuning task."""
        return pfx_pfx_task(task=task)

    def pfx_prefix(self, *, task_id: str) -> dict[str, Any]:
        """Prefix-Tuning prefix."""
        return pfx_pfx_prefix(task_id=task_id)

    def pfx_optimize(self, *, prefix_id: str) -> dict[str, Any]:
        """Prefix-Tuning optimize."""
        return pfx_pfx_optimize(prefix_id=prefix_id)

    def pfx_generate(
        self, *, opt_id: str, score: int
    ) -> dict[str, Any]:
        """Prefix-Tuning generate."""
        return pfx_pfx_generate(opt_id=opt_id, score=score)

    def pfx_freeze(self, *, freeze_lm: bool) -> dict[str, Any]:
        """Prefix-Tuning freeze flag."""
        return pfx_pfx_freeze(freeze_lm=freeze_lm)

    def pfx_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Prefix-Tuning loop plan."""
        return pfx_pfx_loop_plan(phase=phase)

    def ptv_deep(self, *, task: str) -> dict[str, Any]:
        """P-Tuning v2 deep."""
        return ptv_ptv_deep(task=task)

    def ptv_inject(self, *, deep_id: str) -> dict[str, Any]:
        """P-Tuning v2 inject."""
        return ptv_ptv_inject(deep_id=deep_id)

    def ptv_tune(self, *, inj_id: str) -> dict[str, Any]:
        """P-Tuning v2 tune."""
        return ptv_ptv_tune(inj_id=inj_id)

    def ptv_seqtag(
        self, *, tune_id: str, score: int
    ) -> dict[str, Any]:
        """P-Tuning v2 seqtag."""
        return ptv_ptv_seqtag(tune_id=tune_id, score=score)

    def ptv_universal(self, *, match_finetune: bool) -> dict[str, Any]:
        """P-Tuning v2 universal flag."""
        return ptv_ptv_universal(match_finetune=match_finetune)

    def ptv_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """P-Tuning v2 loop plan."""
        return ptv_ptv_loop_plan(phase=phase)

    def ptl_soft(self, *, task: str) -> dict[str, Any]:
        """Prompt Tuning soft."""
        return ptl_ptl_soft(task=task)

    def ptl_prepend(self, *, soft_id: str) -> dict[str, Any]:
        """Prompt Tuning prepend."""
        return ptl_ptl_prepend(soft_id=soft_id)

    def ptl_optimize(self, *, prep_id: str) -> dict[str, Any]:
        """Prompt Tuning optimize."""
        return ptl_ptl_optimize(prep_id=prep_id)

    def ptl_scale(
        self, *, opt_id: str, score: int
    ) -> dict[str, Any]:
        """Prompt Tuning scale."""
        return ptl_ptl_scale(opt_id=opt_id, score=score)

    def ptl_input_only(
        self, *, input_layer_only: bool
    ) -> dict[str, Any]:
        """Prompt Tuning input-only flag."""
        return ptl_ptl_input_only(input_layer_only=input_layer_only)

    def ptl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Prompt Tuning loop plan."""
        return ptl_ptl_loop_plan(phase=phase)

    def msp_soft(self, *, query: str) -> dict[str, Any]:
        """Soft Prompt Mixtures soft."""
        return msp_msp_soft(query=query)

    def msp_mix(self, *, soft_id: str) -> dict[str, Any]:
        """Soft Prompt Mixtures mix."""
        return msp_msp_mix(soft_id=soft_id)

    def msp_ensemble(self, *, mix_id: str) -> dict[str, Any]:
        """Soft Prompt Mixtures ensemble."""
        return msp_msp_ensemble(mix_id=mix_id)

    def msp_probe(
        self, *, ens_id: str, score: int
    ) -> dict[str, Any]:
        """Soft Prompt Mixtures probe."""
        return msp_msp_probe(ens_id=ens_id, score=score)

    def msp_underest(
        self, *, prior_underestimate: bool
    ) -> dict[str, Any]:
        """Soft Prompt Mixtures underestimate flag."""
        return msp_msp_underest(prior_underestimate=prior_underestimate)

    def msp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Soft Prompt Mixtures loop plan."""
        return msp_msp_loop_plan(phase=phase)

    def spot_source(self, *, source_task: str) -> dict[str, Any]:
        """SPoT source."""
        return spot_spot_source(source_task=source_task)

    def spot_init(
        self, *, src_id: str, target_task: str
    ) -> dict[str, Any]:
        """SPoT init."""
        return spot_spot_init(src_id=src_id, target_task=target_task)

    def spot_embed(self, *, src_id: str) -> dict[str, Any]:
        """SPoT embed."""
        return spot_spot_embed(src_id=src_id)

    def spot_retrieve(
        self, *, emb_id: str, score: int
    ) -> dict[str, Any]:
        """SPoT retrieve."""
        return spot_spot_retrieve(emb_id=emb_id, score=score)

    def spot_vs_tune(
        self, *, beat_model_tuning: bool
    ) -> dict[str, Any]:
        """SPoT vs model-tuning flag."""
        return spot_spot_vs_tune(beat_model_tuning=beat_model_tuning)

    def spot_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SPoT loop plan."""
        return spot_spot_loop_plan(phase=phase)

    def atm_source(self, *, source_task: str) -> dict[str, Any]:
        """ATTEMPT source."""
        return atm_atm_source(source_task=source_task)

    def atm_target(self, *, target_task: str) -> dict[str, Any]:
        """ATTEMPT target."""
        return atm_atm_target(target_task=target_task)

    def atm_attend(
        self, *, src_id: str, tgt_id: str
    ) -> dict[str, Any]:
        """ATTEMPT attend."""
        return atm_atm_attend(src_id=src_id, tgt_id=tgt_id)

    def atm_mix(self, *, attn_id: str, score: int) -> dict[str, Any]:
        """ATTEMPT mix."""
        return atm_atm_mix(attn_id=attn_id, score=score)

    def atm_modular(self, *, modular: bool) -> dict[str, Any]:
        """ATTEMPT modular flag."""
        return atm_atm_modular(modular=modular)

    def atm_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ATTEMPT loop plan."""
        return atm_atm_loop_plan(phase=phase)

    def mptp_shared(self, *, corpus: str) -> dict[str, Any]:
        """MPT shared."""
        return mptp_mptp_shared(corpus=corpus)

    def mptp_factor(
        self, *, shared_id: str, task: str
    ) -> dict[str, Any]:
        """MPT factor."""
        return mptp_mptp_factor(shared_id=shared_id, task=task)

    def mptp_transfer(self, *, factor_id: str) -> dict[str, Any]:
        """MPT transfer."""
        return mptp_mptp_transfer(factor_id=factor_id)

    def mptp_score(
        self, *, xfer_id: str, score: int
    ) -> dict[str, Any]:
        """MPT score."""
        return mptp_mptp_score(xfer_id=xfer_id, score=score)

    def mptp_efficient(
        self, *, param_efficient: bool
    ) -> dict[str, Any]:
        """MPT efficiency flag."""
        return mptp_mptp_efficient(param_efficient=param_efficient)

    def mptp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MPT loop plan."""
        return mptp_mptp_loop_plan(phase=phase)

    def lora_freeze(self, *, base_frozen: bool) -> dict[str, Any]:
        """LoRA freeze flag."""
        return lora_lora_freeze(base_frozen=base_frozen)

    def lora_rank(self, *, task: str, rank: int) -> dict[str, Any]:
        """LoRA rank."""
        return lora_lora_rank(task=task, rank=rank)

    def lora_train(self, *, rank_id: str) -> dict[str, Any]:
        """LoRA train."""
        return lora_lora_train(rank_id=rank_id)

    def lora_merge(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA merge."""
        return lora_lora_merge(train_id=train_id, score=score)

    def lora_latency(self, *, zero_extra: bool) -> dict[str, Any]:
        """LoRA latency flag."""
        return lora_lora_latency(zero_extra=zero_extra)

    def lora_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA loop plan."""
        return lora_lora_loop_plan(phase=phase)

    def adf_extract(self, *, task: str) -> dict[str, Any]:
        """AdapterFusion extract."""
        return adf_adf_extract(task=task)

    def adf_compose(self, *, adapter_id: str) -> dict[str, Any]:
        """AdapterFusion compose."""
        return adf_adf_compose(adapter_id=adapter_id)

    def adf_attend(self, *, compose_id: str) -> dict[str, Any]:
        """AdapterFusion attend."""
        return adf_adf_attend(compose_id=compose_id)

    def adf_score(
        self, *, fusion_id: str, score: int
    ) -> dict[str, Any]:
        """AdapterFusion score."""
        return adf_adf_score(fusion_id=fusion_id, score=score)

    def adf_nondestruct(
        self, *, nondestructive: bool
    ) -> dict[str, Any]:
        """AdapterFusion nondestructive flag."""
        return adf_adf_nondestruct(nondestructive=nondestructive)

    def adf_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AdapterFusion loop plan."""
        return adf_adf_loop_plan(phase=phase)

    def cmp_insert(self, *, task: str) -> dict[str, Any]:
        """Compacter insert."""
        return cmp_cmp_insert(task=task)

    def cmp_kronecker(self, *, adapter_id: str, n: int) -> dict[str, Any]:
        """Compacter kronecker."""
        return cmp_cmp_kronecker(adapter_id=adapter_id, n=n)

    def cmp_train(self, *, kron_id: str) -> dict[str, Any]:
        """Compacter train."""
        return cmp_cmp_train(kron_id=kron_id)

    def cmp_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """Compacter score."""
        return cmp_cmp_score(train_id=train_id, score=score)

    def cmp_compact(self, *, param_efficient: bool) -> dict[str, Any]:
        """Compacter efficiency flag."""
        return cmp_cmp_compact(param_efficient=param_efficient)

    def cmp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Compacter loop plan."""
        return cmp_cmp_loop_plan(phase=phase)

    def ia3_vector(self, *, task: str) -> dict[str, Any]:
        """(IA)^3 vector."""
        return ia3_ia3_vector(task=task)

    def ia3_scale(self, *, vector_id: str) -> dict[str, Any]:
        """(IA)^3 scale."""
        return ia3_ia3_scale(vector_id=vector_id)

    def ia3_train(self, *, scale_id: str) -> dict[str, Any]:
        """(IA)^3 train."""
        return ia3_ia3_train(scale_id=scale_id)

    def ia3_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """(IA)^3 score."""
        return ia3_ia3_score(train_id=train_id, score=score)

    def ia3_mixed(self, *, mixed_batch: bool) -> dict[str, Any]:
        """(IA)^3 mixed-batch flag."""
        return ia3_ia3_mixed(mixed_batch=mixed_batch)

    def ia3_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """(IA)^3 loop plan."""
        return ia3_ia3_loop_plan(phase=phase)

    def bft_freeze(self, *, weights_frozen: bool) -> dict[str, Any]:
        """BitFit freeze flag."""
        return bft_bft_freeze(weights_frozen=weights_frozen)

    def bft_bias(self, *, task: str) -> dict[str, Any]:
        """BitFit bias."""
        return bft_bft_bias(task=task)

    def bft_train(self, *, bias_id: str) -> dict[str, Any]:
        """BitFit train."""
        return bft_bft_train(bias_id=bias_id)

    def bft_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """BitFit score."""
        return bft_bft_score(train_id=train_id, score=score)

    def bft_tiny(self, *, fraction_pct: int) -> dict[str, Any]:
        """BitFit tiny-fraction flag."""
        return bft_bft_tiny(fraction_pct=fraction_pct)

    def bft_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """BitFit loop plan."""
        return bft_bft_loop_plan(phase=phase)

    def dora_decompose(self, *, task: str) -> dict[str, Any]:
        """DoRA decompose."""
        return dora_dora_decompose(task=task)

    def dora_magnitude(self, *, decomp_id: str) -> dict[str, Any]:
        """DoRA magnitude."""
        return dora_dora_magnitude(decomp_id=decomp_id)

    def dora_direction(
        self, *, mag_id: str, rank: int
    ) -> dict[str, Any]:
        """DoRA direction."""
        return dora_dora_direction(mag_id=mag_id, rank=rank)

    def dora_score(
        self, *, dir_id: str, score: int
    ) -> dict[str, Any]:
        """DoRA score."""
        return dora_dora_score(dir_id=dir_id, score=score)

    def dora_vs_lora(self, *, closes_gap: bool) -> dict[str, Any]:
        """DoRA vs LoRA flag."""
        return dora_dora_vs_lora(closes_gap=closes_gap)

    def dora_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """DoRA loop plan."""
        return dora_dora_loop_plan(phase=phase)

    def qlo_quantize(self, *, bits: int) -> dict[str, Any]:
        """QLoRA quantize."""
        return qlo_qlo_quantize(bits=bits)

    def qlo_nf4(self, *, quant_id: str) -> dict[str, Any]:
        """QLoRA NF4."""
        return qlo_qlo_nf4(quant_id=quant_id)

    def qlo_adapter(self, *, nf4_id: str, rank: int) -> dict[str, Any]:
        """QLoRA adapter."""
        return qlo_qlo_adapter(nf4_id=nf4_id, rank=rank)

    def qlo_score(
        self, *, adapter_id: str, score: int
    ) -> dict[str, Any]:
        """QLoRA score."""
        return qlo_qlo_score(adapter_id=adapter_id, score=score)

    def qlo_memory(self, *, double_quant: bool) -> dict[str, Any]:
        """QLoRA memory flag."""
        return qlo_qlo_memory(double_quant=double_quant)

    def qlo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """QLoRA loop plan."""
        return qlo_qlo_loop_plan(phase=phase)

    def adl_init(self, *, task: str, budget: int) -> dict[str, Any]:
        """AdaLoRA init."""
        return adl_adl_init(task=task, budget=budget)

    def adl_svd(self, *, init_id: str) -> dict[str, Any]:
        """AdaLoRA SVD."""
        return adl_adl_svd(init_id=init_id)

    def adl_prune(self, *, svd_id: str, keep: int) -> dict[str, Any]:
        """AdaLoRA prune."""
        return adl_adl_prune(svd_id=svd_id, keep=keep)

    def adl_score(
        self, *, prune_id: str, score: int
    ) -> dict[str, Any]:
        """AdaLoRA score."""
        return adl_adl_score(prune_id=prune_id, score=score)

    def adl_adaptive(self, *, adaptive_rank: bool) -> dict[str, Any]:
        """AdaLoRA adaptive-rank flag."""
        return adl_adl_adaptive(adaptive_rank=adaptive_rank)

    def adl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AdaLoRA loop plan."""
        return adl_adl_loop_plan(phase=phase)

    def vra_share(self, *, task: str, rank: int) -> dict[str, Any]:
        """VeRA share."""
        return vra_vra_share(task=task, rank=rank)

    def vra_scale(self, *, share_id: str) -> dict[str, Any]:
        """VeRA scale."""
        return vra_vra_scale(share_id=share_id)

    def vra_train(self, *, scale_id: str) -> dict[str, Any]:
        """VeRA train."""
        return vra_vra_train(scale_id=scale_id)

    def vra_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """VeRA score."""
        return vra_vra_score(train_id=train_id, score=score)

    def vra_tiny(self, *, vector_only: bool) -> dict[str, Any]:
        """VeRA tiny flag."""
        return vra_vra_tiny(vector_only=vector_only)

    def vra_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """VeRA loop plan."""
        return vra_vra_loop_plan(phase=phase)

    def adp_insert(self, *, task: str) -> dict[str, Any]:
        """AdapterDrop insert."""
        return adp_adp_insert(task=task)

    def adp_drop(
        self, *, adapter_id: str, lower_layers: int
    ) -> dict[str, Any]:
        """AdapterDrop drop."""
        return adp_adp_drop(adapter_id=adapter_id, lower_layers=lower_layers)

    def adp_infer(self, *, drop_id: str) -> dict[str, Any]:
        """AdapterDrop infer."""
        return adp_adp_infer(drop_id=drop_id)

    def adp_score(
        self, *, infer_id: str, score: int
    ) -> dict[str, Any]:
        """AdapterDrop score."""
        return adp_adp_score(infer_id=infer_id, score=score)

    def adp_efficient(self, *, multi_task: bool) -> dict[str, Any]:
        """AdapterDrop efficiency flag."""
        return adp_adp_efficient(multi_task=multi_task)

    def adp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AdapterDrop loop plan."""
        return adp_adp_loop_plan(phase=phase)

    def psa_svd(self, *, task: str, rank: int) -> dict[str, Any]:
        """PiSSA SVD."""
        return psa_psa_svd(task=task, rank=rank)

    def psa_principal(self, *, svd_id: str) -> dict[str, Any]:
        """PiSSA principal."""
        return psa_psa_principal(svd_id=svd_id)

    def psa_residual(self, *, principal_id: str) -> dict[str, Any]:
        """PiSSA residual."""
        return psa_psa_residual(principal_id=principal_id)

    def psa_score(
        self, *, residual_id: str, score: int
    ) -> dict[str, Any]:
        """PiSSA score."""
        return psa_psa_score(residual_id=residual_id, score=score)

    def psa_fast(self, *, faster_than_lora: bool) -> dict[str, Any]:
        """PiSSA fast-convergence flag."""
        return psa_psa_fast(faster_than_lora=faster_than_lora)

    def psa_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PiSSA loop plan."""
        return psa_psa_loop_plan(phase=phase)

    def dpr_diff(self, *, task: str) -> dict[str, Any]:
        """Diff Pruning diff."""
        return dpr_dpr_diff(task=task)

    def dpr_mask(self, *, diff_id: str) -> dict[str, Any]:
        """Diff Pruning mask."""
        return dpr_dpr_mask(diff_id=diff_id)

    def dpr_prune(
        self, *, mask_id: str, sparsity_pct: int
    ) -> dict[str, Any]:
        """Diff Pruning prune."""
        return dpr_dpr_prune(mask_id=mask_id, sparsity_pct=sparsity_pct)

    def dpr_score(
        self, *, prune_id: str, score: int
    ) -> dict[str, Any]:
        """Diff Pruning score."""
        return dpr_dpr_score(prune_id=prune_id, score=score)

    def dpr_sparse(self, *, no_new_params: bool) -> dict[str, Any]:
        """Diff Pruning sparse flag."""
        return dpr_dpr_sparse(no_new_params=no_new_params)

    def dpr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Diff Pruning loop plan."""
        return dpr_dpr_loop_plan(phase=phase)

    def tlo_base(self, *, task: str, rank: int) -> dict[str, Any]:
        """Tied-LoRA base."""
        return tlo_tlo_base(task=task, rank=rank)

    def tlo_tie(self, *, base_id: str, layers: int) -> dict[str, Any]:
        """Tied-LoRA tie."""
        return tlo_tlo_tie(base_id=base_id, layers=layers)

    def tlo_train(self, *, tie_id: str) -> dict[str, Any]:
        """Tied-LoRA train."""
        return tlo_tlo_train(tie_id=tie_id)

    def tlo_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """Tied-LoRA score."""
        return tlo_tlo_score(train_id=train_id, score=score)

    def tlo_efficient(self, *, weight_tied: bool) -> dict[str, Any]:
        """Tied-LoRA efficiency flag."""
        return tlo_tlo_efficient(weight_tied=weight_tied)

    def tlo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Tied-LoRA loop plan."""
        return tlo_tlo_loop_plan(phase=phase)

    def lrp_split(self, *, task: str) -> dict[str, Any]:
        """LoRA+ split."""
        return lrp_lrp_split(task=task)

    def lrp_ratio(
        self, *, split_id: str, lambda_ratio: int
    ) -> dict[str, Any]:
        """LoRA+ ratio."""
        return lrp_lrp_ratio(split_id=split_id, lambda_ratio=lambda_ratio)

    def lrp_train(self, *, ratio_id: str) -> dict[str, Any]:
        """LoRA+ train."""
        return lrp_lrp_train(ratio_id=ratio_id)

    def lrp_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA+ score."""
        return lrp_lrp_score(train_id=train_id, score=score)

    def lrp_speed(self, *, faster_than_lora: bool) -> dict[str, Any]:
        """LoRA+ speed flag."""
        return lrp_lrp_speed(faster_than_lora=faster_than_lora)

    def lrp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA+ loop plan."""
        return lrp_lrp_loop_plan(phase=phase)

    def lfa_freeze_a(self, *, task: str, rank: int) -> dict[str, Any]:
        """LoRA-FA freeze A."""
        return lfa_lfa_freeze_a(task=task, rank=rank)

    def lfa_train_b(self, *, a_id: str) -> dict[str, Any]:
        """LoRA-FA train B."""
        return lfa_lfa_train_b(a_id=a_id)

    def lfa_merge(self, *, train_id: str) -> dict[str, Any]:
        """LoRA-FA merge."""
        return lfa_lfa_merge(train_id=train_id)

    def lfa_score(
        self, *, merge_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-FA score."""
        return lfa_lfa_score(merge_id=merge_id, score=score)

    def lfa_memory(self, *, activation_saved: bool) -> dict[str, Any]:
        """LoRA-FA memory flag."""
        return lfa_lfa_memory(activation_saved=activation_saved)

    def lfa_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-FA loop plan."""
        return lfa_lfa_loop_plan(phase=phase)

    def dyl_range(
        self, *, task: str, r_min: int, r_max: int
    ) -> dict[str, Any]:
        """DyLoRA range."""
        return dyl_dyl_range(task=task, r_min=r_min, r_max=r_max)

    def dyl_sample(self, *, range_id: str) -> dict[str, Any]:
        """DyLoRA sample."""
        return dyl_dyl_sample(range_id=range_id)

    def dyl_select(self, *, sample_id: str, rank: int) -> dict[str, Any]:
        """DyLoRA select."""
        return dyl_dyl_select(sample_id=sample_id, rank=rank)

    def dyl_score(
        self, *, select_id: str, score: int
    ) -> dict[str, Any]:
        """DyLoRA score."""
        return dyl_dyl_score(select_id=select_id, score=score)

    def dyl_searchfree(self, *, search_free: bool) -> dict[str, Any]:
        """DyLoRA search-free flag."""
        return dyl_dyl_searchfree(search_free=search_free)

    def dyl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """DyLoRA loop plan."""
        return dyl_dyl_loop_plan(phase=phase)

    def lxs_svd(self, *, task: str, rank: int) -> dict[str, Any]:
        """LoRA-XS SVD."""
        return lxs_lxs_svd(task=task, rank=rank)

    def lxs_r(self, *, svd_id: str) -> dict[str, Any]:
        """LoRA-XS R."""
        return lxs_lxs_r(svd_id=svd_id)

    def lxs_train(self, *, r_id: str) -> dict[str, Any]:
        """LoRA-XS train."""
        return lxs_lxs_train(r_id=r_id)

    def lxs_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-XS score."""
        return lxs_lxs_score(train_id=train_id, score=score)

    def lxs_tiny(self, *, r_squared_only: bool) -> dict[str, Any]:
        """LoRA-XS tiny flag."""
        return lxs_lxs_tiny(r_squared_only=r_squared_only)

    def lxs_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-XS loop plan."""
        return lxs_lxs_loop_plan(phase=phase)

    def asy_role(self, *, task: str) -> dict[str, Any]:
        """AsymmetryLoRA role."""
        return asy_asy_role(task=task)

    def asy_freeze_a(self, *, role_id: str) -> dict[str, Any]:
        """AsymmetryLoRA freeze A."""
        return asy_asy_freeze_a(role_id=role_id)

    def asy_train_b(self, *, a_id: str) -> dict[str, Any]:
        """AsymmetryLoRA train B."""
        return asy_asy_train_b(a_id=a_id)

    def asy_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """AsymmetryLoRA score."""
        return asy_asy_score(train_id=train_id, score=score)

    def asy_bound(self, *, tighter_bound: bool) -> dict[str, Any]:
        """AsymmetryLoRA bound flag."""
        return asy_asy_bound(tighter_bound=tighter_bound)

    def asy_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AsymmetryLoRA loop plan."""
        return asy_asy_loop_plan(phase=phase)

    def lga_grad(self, *, task: str, samples: int) -> dict[str, Any]:
        """LoRA-GA grad."""
        return lga_lga_grad(task=task, samples=samples)

    def lga_svd(self, *, grad_id: str) -> dict[str, Any]:
        """LoRA-GA svd."""
        return lga_lga_svd(grad_id=grad_id)

    def lga_scale(self, *, svd_id: str) -> dict[str, Any]:
        """LoRA-GA scale."""
        return lga_lga_scale(svd_id=svd_id)

    def lga_score(
        self, *, scale_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-GA score."""
        return lga_lga_score(scale_id=scale_id, score=score)

    def lga_fast(self, *, faster_convergence: bool) -> dict[str, Any]:
        """LoRA-GA fast flag."""
        return lga_lga_fast(faster_convergence=faster_convergence)

    def lga_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-GA loop plan."""
        return lga_lga_loop_plan(phase=phase)

    def mor_square(self, *, task: str, side: int) -> dict[str, Any]:
        """MoRA square."""
        return mor_mor_square(task=task, side=side)

    def mor_compress(self, *, square_id: str) -> dict[str, Any]:
        """MoRA compress."""
        return mor_mor_compress(square_id=square_id)

    def mor_expand(self, *, compress_id: str) -> dict[str, Any]:
        """MoRA expand."""
        return mor_mor_expand(compress_id=compress_id)

    def mor_score(
        self, *, expand_id: str, score: int
    ) -> dict[str, Any]:
        """MoRA score."""
        return mor_mor_score(expand_id=expand_id, score=score)

    def mor_merge(self, *, mergeable: bool) -> dict[str, Any]:
        """MoRA merge flag."""
        return mor_mor_merge(mergeable=mergeable)

    def mor_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MoRA loop plan."""
        return mor_mor_loop_plan(phase=phase)

    def rsl_rank(self, *, task: str, rank: int) -> dict[str, Any]:
        """rsLoRA rank."""
        return rsl_rsl_rank(task=task, rank=rank)

    def rsl_scale(self, *, rank_id: str) -> dict[str, Any]:
        """rsLoRA scale."""
        return rsl_rsl_scale(rank_id=rank_id)

    def rsl_train(self, *, scale_id: str) -> dict[str, Any]:
        """rsLoRA train."""
        return rsl_rsl_train(scale_id=scale_id)

    def rsl_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """rsLoRA score."""
        return rsl_rsl_score(train_id=train_id, score=score)

    def rsl_stable(self, *, no_collapse: bool) -> dict[str, Any]:
        """rsLoRA stable flag."""
        return rsl_rsl_stable(no_collapse=no_collapse)

    def rsl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """rsLoRA loop plan."""
        return rsl_rsl_loop_plan(phase=phase)

    def lkr_factors(
        self, *, task: str, factor_a: int, factor_b: int
    ) -> dict[str, Any]:
        """LoKr factors."""
        return lkr_lkr_factors(
            task=task, factor_a=factor_a, factor_b=factor_b
        )

    def lkr_kron(self, *, factors_id: str) -> dict[str, Any]:
        """LoKr kron."""
        return lkr_lkr_kron(factors_id=factors_id)

    def lkr_vectorize(self, *, kron_id: str) -> dict[str, Any]:
        """LoKr vectorize."""
        return lkr_lkr_vectorize(kron_id=kron_id)

    def lkr_score(
        self, *, vector_id: str, score: int
    ) -> dict[str, Any]:
        """LoKr score."""
        return lkr_lkr_score(vector_id=vector_id, score=score)

    def lkr_preserve(self, *, rank_preserved: bool) -> dict[str, Any]:
        """LoKr preserve flag."""
        return lkr_lkr_preserve(rank_preserved=rank_preserved)

    def lkr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoKr loop plan."""
        return lkr_lkr_loop_plan(phase=phase)

    def lha_pair(self, *, task: str, rank: int) -> dict[str, Any]:
        """LoHa pair."""
        return lha_lha_pair(task=task, rank=rank)

    def lha_hadamard(self, *, pair_id: str) -> dict[str, Any]:
        """LoHa hadamard."""
        return lha_lha_hadamard(pair_id=pair_id)

    def lha_train(self, *, hadamard_id: str) -> dict[str, Any]:
        """LoHa train."""
        return lha_lha_train(hadamard_id=hadamard_id)

    def lha_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoHa score."""
        return lha_lha_score(train_id=train_id, score=score)

    def lha_express(self, *, more_expressivity: bool) -> dict[str, Any]:
        """LoHa express flag."""
        return lha_lha_express(more_expressivity=more_expressivity)

    def lha_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoHa loop plan."""
        return lha_lha_loop_plan(phase=phase)

    def fft_basis(self, *, task: str, n_coeff: int) -> dict[str, Any]:
        """FourierFT basis."""
        return fft_fft_basis(task=task, n_coeff=n_coeff)

    def fft_coeff(self, *, basis_id: str) -> dict[str, Any]:
        """FourierFT coeff."""
        return fft_fft_coeff(basis_id=basis_id)

    def fft_idft(self, *, coeff_id: str) -> dict[str, Any]:
        """FourierFT idft."""
        return fft_fft_idft(coeff_id=coeff_id)

    def fft_score(
        self, *, idft_id: str, score: int
    ) -> dict[str, Any]:
        """FourierFT score."""
        return fft_fft_score(idft_id=idft_id, score=score)

    def fft_sparse(self, *, spectral_sparse: bool) -> dict[str, Any]:
        """FourierFT sparse flag."""
        return fft_fft_sparse(spectral_sparse=spectral_sparse)

    def fft_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """FourierFT loop plan."""
        return fft_fft_loop_plan(phase=phase)

    def had_insert(self, *, task: str, bottleneck: int) -> dict[str, Any]:
        """Houlsby insert."""
        return had_had_insert(task=task, bottleneck=bottleneck)

    def had_freeze(self, *, insert_id: str) -> dict[str, Any]:
        """Houlsby freeze."""
        return had_had_freeze(insert_id=insert_id)

    def had_train(self, *, freeze_id: str) -> dict[str, Any]:
        """Houlsby train."""
        return had_had_train(freeze_id=freeze_id)

    def had_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """Houlsby score."""
        return had_had_score(train_id=train_id, score=score)

    def had_latency(self, *, adds_latency: bool) -> dict[str, Any]:
        """Houlsby latency flag."""
        return had_had_latency(adds_latency=adds_latency)

    def had_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Houlsby loop plan."""
        return had_had_loop_plan(phase=phase)

    def rft_repr(self, *, task: str, layers: int) -> dict[str, Any]:
        """ReFT repr."""
        return rft_rft_repr(task=task, layers=layers)

    def rft_edit(self, *, repr_id: str) -> dict[str, Any]:
        """ReFT edit."""
        return rft_rft_edit(repr_id=repr_id)

    def rft_train(self, *, edit_id: str) -> dict[str, Any]:
        """ReFT train."""
        return rft_rft_train(edit_id=edit_id)

    def rft_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """ReFT score."""
        return rft_rft_score(train_id=train_id, score=score)

    def rft_weightless(self, *, no_weight_update: bool) -> dict[str, Any]:
        """ReFT weightless flag."""
        return rft_rft_weightless(no_weight_update=no_weight_update)

    def rft_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ReFT loop plan."""
        return rft_rft_loop_plan(phase=phase)

    def oft_ortho(self, *, task: str, block: int) -> dict[str, Any]:
        """OFT ortho."""
        return oft_oft_ortho(task=task, block=block)

    def oft_butterfly(
        self, *, ortho_id: str, factors: int
    ) -> dict[str, Any]:
        """OFT butterfly."""
        return oft_oft_butterfly(ortho_id=ortho_id, factors=factors)

    def oft_train(self, *, butterfly_id: str) -> dict[str, Any]:
        """OFT train."""
        return oft_oft_train(butterfly_id=butterfly_id)

    def oft_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """OFT score."""
        return oft_oft_score(train_id=train_id, score=score)

    def oft_energy(self, *, hypersphere_preserved: bool) -> dict[str, Any]:
        """OFT energy flag."""
        return oft_oft_energy(hypersphere_preserved=hypersphere_preserved)

    def oft_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """OFT loop plan."""
        return oft_oft_loop_plan(phase=phase)

    def mss_shard(self, *, task: str, shards: int) -> dict[str, Any]:
        """MiSS shard."""
        return mss_mss_shard(task=task, shards=shards)

    def mss_share(self, *, shard_id: str) -> dict[str, Any]:
        """MiSS share."""
        return mss_mss_share(shard_id=shard_id)

    def mss_train(self, *, share_id: str) -> dict[str, Any]:
        """MiSS train."""
        return mss_mss_train(share_id=share_id)

    def mss_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """MiSS score."""
        return mss_mss_score(train_id=train_id, score=score)

    def mss_pareto(self, *, better_tradeoff: bool) -> dict[str, Any]:
        """MiSS pareto flag."""
        return mss_mss_pareto(better_tradeoff=better_tradeoff)

    def mss_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MiSS loop plan."""
        return mss_mss_loop_plan(phase=phase)

    def drl_rank(self, *, task: str, rank: int) -> dict[str, Any]:
        """DropLoRA rank."""
        return drl_drl_rank(task=task, rank=rank)

    def drl_mask(self, *, rank_id: str, keep_prob: int) -> dict[str, Any]:
        """DropLoRA mask."""
        return drl_drl_mask(rank_id=rank_id, keep_prob=keep_prob)

    def drl_train(self, *, mask_id: str) -> dict[str, Any]:
        """DropLoRA train."""
        return drl_drl_train(mask_id=mask_id)

    def drl_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """DropLoRA score."""
        return drl_drl_score(train_id=train_id, score=score)

    def drl_infer(self, *, no_extra_cost: bool) -> dict[str, Any]:
        """DropLoRA infer flag."""
        return drl_drl_infer(no_extra_cost=no_extra_cost)

    def drl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """DropLoRA loop plan."""
        return drl_drl_loop_plan(phase=phase)

    def gal_grad(self, *, task: str) -> dict[str, Any]:
        """GaLore grad."""
        return gal_gal_grad(task=task)

    def gal_project(self, *, grad_id: str, rank: int) -> dict[str, Any]:
        """GaLore project."""
        return gal_gal_project(grad_id=grad_id, rank=rank)

    def gal_step(self, *, project_id: str) -> dict[str, Any]:
        """GaLore step."""
        return gal_gal_step(project_id=project_id)

    def gal_score(
        self, *, step_id: str, score: int
    ) -> dict[str, Any]:
        """GaLore score."""
        return gal_gal_score(step_id=step_id, score=score)

    def gal_full(self, *, updates_all_weights: bool) -> dict[str, Any]:
        """GaLore full flag."""
        return gal_gal_full(updates_all_weights=updates_all_weights)

    def gal_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GaLore loop plan."""
        return gal_gal_loop_plan(phase=phase)

    def shr_mask(self, *, task: str, pct: int) -> dict[str, Any]:
        """SHiRA mask."""
        return shr_shr_mask(task=task, pct=pct)

    def shr_tune(self, *, mask_id: str) -> dict[str, Any]:
        """SHiRA tune."""
        return shr_shr_tune(mask_id=mask_id)

    def shr_switch(self, *, tune_id: str) -> dict[str, Any]:
        """SHiRA switch."""
        return shr_shr_switch(tune_id=tune_id)

    def shr_score(
        self, *, switch_id: str, score: int
    ) -> dict[str, Any]:
        """SHiRA score."""
        return shr_shr_score(switch_id=switch_id, score=score)

    def shr_fusion(self, *, less_concept_loss: bool) -> dict[str, Any]:
        """SHiRA fusion flag."""
        return shr_shr_fusion(less_concept_loss=less_concept_loss)

    def shr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SHiRA loop plan."""
        return shr_shr_loop_plan(phase=phase)

    def wft_wave(self, *, task: str, n_coeff: int) -> dict[str, Any]:
        """WaveFT wave."""
        return wft_wft_wave(task=task, n_coeff=n_coeff)

    def wft_sparse(self, *, wave_id: str) -> dict[str, Any]:
        """WaveFT sparse."""
        return wft_wft_sparse(wave_id=wave_id)

    def wft_idwt(self, *, sparse_id: str) -> dict[str, Any]:
        """WaveFT idwt."""
        return wft_wft_idwt(sparse_id=sparse_id)

    def wft_score(
        self, *, idwt_id: str, score: int
    ) -> dict[str, Any]:
        """WaveFT score."""
        return wft_wft_score(idwt_id=idwt_id, score=score)

    def wft_granular(self, *, below_lora_min: bool) -> dict[str, Any]:
        """WaveFT granular flag."""
        return wft_wft_granular(below_lora_min=below_lora_min)

    def wft_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """WaveFT loop plan."""
        return wft_wft_loop_plan(phase=phase)

    def lpr_equiv(self, *, task: str) -> dict[str, Any]:
        """LoRA-Pro equiv."""
        return lpr_lpr_equiv(task=task)

    def lpr_adjust(self, *, equiv_id: str) -> dict[str, Any]:
        """LoRA-Pro adjust."""
        return lpr_lpr_adjust(equiv_id=equiv_id)

    def lpr_train(self, *, adjust_id: str) -> dict[str, Any]:
        """LoRA-Pro train."""
        return lpr_lpr_train(adjust_id=adjust_id)

    def lpr_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-Pro score."""
        return lpr_lpr_score(train_id=train_id, score=score)

    def lpr_bridge(self, *, closer_to_fft: bool) -> dict[str, Any]:
        """LoRA-Pro bridge flag."""
        return lpr_lpr_bridge(closer_to_fft=closer_to_fft)

    def lpr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-Pro loop plan."""
        return lpr_lpr_loop_plan(phase=phase)

    def krl_kron(self, *, task: str, factor: int) -> dict[str, Any]:
        """Kron-LoRA kron."""
        return krl_krl_kron(task=task, factor=factor)

    def krl_lora(self, *, kron_id: str, rank: int) -> dict[str, Any]:
        """Kron-LoRA lora."""
        return krl_krl_lora(kron_id=kron_id, rank=rank)

    def krl_train(self, *, lora_id: str) -> dict[str, Any]:
        """Kron-LoRA train."""
        return krl_krl_train(lora_id=lora_id)

    def krl_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """Kron-LoRA score."""
        return krl_krl_score(train_id=train_id, score=score)

    def krl_compress(self, *, more_compression: bool) -> dict[str, Any]:
        """Kron-LoRA compress flag."""
        return krl_krl_compress(more_compression=more_compression)

    def krl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Kron-LoRA loop plan."""
        return krl_krl_loop_plan(phase=phase)

    def mil_svd(self, *, task: str, rank: int) -> dict[str, Any]:
        """MiLoRA svd."""
        return mil_mil_svd(task=task, rank=rank)

    def mil_minor(self, *, svd_id: str) -> dict[str, Any]:
        """MiLoRA minor."""
        return mil_mil_minor(svd_id=svd_id)

    def mil_freeze(self, *, minor_id: str) -> dict[str, Any]:
        """MiLoRA freeze."""
        return mil_mil_freeze(minor_id=minor_id)

    def mil_score(
        self, *, freeze_id: str, score: int
    ) -> dict[str, Any]:
        """MiLoRA score."""
        return mil_mil_score(freeze_id=freeze_id, score=score)

    def mil_preserve(self, *, preserves_principal: bool) -> dict[str, Any]:
        """MiLoRA preserve flag."""
        return mil_mil_preserve(preserves_principal=preserves_principal)

    def mil_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MiLoRA loop plan."""
        return mil_mil_loop_plan(phase=phase)

    def cda_cov(self, *, task: str) -> dict[str, Any]:
        """CorDA cov."""
        return cda_cda_cov(task=task)

    def cda_mode(self, *, cov_id: str, mode: str) -> dict[str, Any]:
        """CorDA mode."""
        return cda_cda_mode(cov_id=cov_id, mode=mode)

    def cda_adapt(self, *, mode_id: str) -> dict[str, Any]:
        """CorDA adapt."""
        return cda_cda_adapt(mode_id=mode_id)

    def cda_score(
        self, *, adapt_id: str, score: int
    ) -> dict[str, Any]:
        """CorDA score."""
        return cda_cda_score(adapt_id=adapt_id, score=score)

    def cda_forget(self, *, less_forgetting: bool) -> dict[str, Any]:
        """CorDA forget flag."""
        return cda_cda_forget(less_forgetting=less_forgetting)

    def cda_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CorDA loop plan."""
        return cda_cda_loop_plan(phase=phase)

    def lfq_quant(self, *, task: str, bits: int) -> dict[str, Any]:
        """LoftQ quant."""
        return lfq_lfq_quant(task=task, bits=bits)

    def lfq_init(self, *, quant_id: str, rank: int) -> dict[str, Any]:
        """LoftQ init."""
        return lfq_lfq_init(quant_id=quant_id, rank=rank)

    def lfq_train(self, *, init_id: str) -> dict[str, Any]:
        """LoftQ train."""
        return lfq_lfq_train(init_id=init_id)

    def lfq_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoftQ score."""
        return lfq_lfq_score(train_id=train_id, score=score)

    def lfq_gap(self, *, closes_qlora_gap: bool) -> dict[str, Any]:
        """LoftQ gap flag."""
        return lfq_lfq_gap(closes_qlora_gap=closes_qlora_gap)

    def lfq_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoftQ loop plan."""
        return lfq_lfq_loop_plan(phase=phase)

    def lds_prelaunch(self, *, task: str) -> dict[str, Any]:
        """LoRA-Dash prelaunch."""
        return lds_lds_prelaunch(task=task)

    def lds_tsd(self, *, prelaunch_id: str, count: int) -> dict[str, Any]:
        """LoRA-Dash tsd."""
        return lds_lds_tsd(prelaunch_id=prelaunch_id, count=count)

    def lds_dash(self, *, tsd_id: str) -> dict[str, Any]:
        """LoRA-Dash dash."""
        return lds_lds_dash(tsd_id=tsd_id)

    def lds_score(
        self, *, dash_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-Dash score."""
        return lds_lds_score(dash_id=dash_id, score=score)

    def lds_impact(self, *, maximizes_tsd: bool) -> dict[str, Any]:
        """LoRA-Dash impact flag."""
        return lds_lds_impact(maximizes_tsd=maximizes_tsd)

    def lds_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-Dash loop plan."""
        return lds_lds_loop_plan(phase=phase)

    def dlo_adapters(self, *, task: str, rank: int) -> dict[str, Any]:
        """Delta-LoRA adapters."""
        return dlo_dlo_adapters(task=task, rank=rank)

    def dlo_delta(self, *, adapters_id: str) -> dict[str, Any]:
        """Delta-LoRA delta."""
        return dlo_dlo_delta(adapters_id=adapters_id)

    def dlo_propagate(self, *, delta_id: str) -> dict[str, Any]:
        """Delta-LoRA propagate."""
        return dlo_dlo_propagate(delta_id=delta_id)

    def dlo_score(
        self, *, propagate_id: str, score: int
    ) -> dict[str, Any]:
        """Delta-LoRA score."""
        return dlo_dlo_score(propagate_id=propagate_id, score=score)

    def dlo_highrank(self, *, high_rank_capacity: bool) -> dict[str, Any]:
        """Delta-LoRA highrank flag."""
        return dlo_dlo_highrank(high_rank_capacity=high_rank_capacity)

    def dlo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Delta-LoRA loop plan."""
        return dlo_dlo_loop_plan(phase=phase)

    def lon_grad(self, *, task: str) -> dict[str, Any]:
        """LoRA-One grad."""
        return lon_lon_grad(task=task)

    def lon_align(self, *, grad_id: str, rank: int) -> dict[str, Any]:
        """LoRA-One align."""
        return lon_lon_align(grad_id=grad_id, rank=rank)

    def lon_train(self, *, align_id: str) -> dict[str, Any]:
        """LoRA-One train."""
        return lon_lon_train(align_id=align_id)

    def lon_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-One score."""
        return lon_lon_score(train_id=train_id, score=score)

    def lon_immediate(self, *, immediate_align: bool) -> dict[str, Any]:
        """LoRA-One immediate flag."""
        return lon_lon_immediate(immediate_align=immediate_align)

    def lon_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-One loop plan."""
        return lon_lon_loop_plan(phase=phase)

    def olr_qr(self, *, task: str, rank: int) -> dict[str, Any]:
        """OLoRA qr."""
        return olr_olr_qr(task=task, rank=rank)

    def olr_ortho(self, *, qr_id: str) -> dict[str, Any]:
        """OLoRA ortho."""
        return olr_olr_ortho(qr_id=qr_id)

    def olr_train(self, *, ortho_id: str) -> dict[str, Any]:
        """OLoRA train."""
        return olr_olr_train(ortho_id=ortho_id)

    def olr_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """OLoRA score."""
        return olr_olr_score(train_id=train_id, score=score)

    def olr_stable(self, *, stable_landscape: bool) -> dict[str, Any]:
        """OLoRA stable flag."""
        return olr_olr_stable(stable_landscape=stable_landscape)

    def olr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """OLoRA loop plan."""
        return olr_olr_loop_plan(phase=phase)

    def lsp_select(self, *, task: str, fraction: int) -> dict[str, Any]:
        """LoRA-SP select."""
        return lsp_lsp_select(task=task, fraction=fraction)

    def lsp_freeze(self, *, select_id: str) -> dict[str, Any]:
        """LoRA-SP freeze."""
        return lsp_lsp_freeze(select_id=select_id)

    def lsp_train(self, *, freeze_id: str) -> dict[str, Any]:
        """LoRA-SP train."""
        return lsp_lsp_train(freeze_id=freeze_id)

    def lsp_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-SP score."""
        return lsp_lsp_score(train_id=train_id, score=score)

    def lsp_memory(self, *, lower_memory: bool) -> dict[str, Any]:
        """LoRA-SP memory flag."""
        return lsp_lsp_memory(lower_memory=lower_memory)

    def lsp_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-SP loop plan."""
        return lsp_lsp_loop_plan(phase=phase)

    def qps_quant(self, *, task: str, bits: int) -> dict[str, Any]:
        """QPiSSA quant."""
        return qps_qps_quant(task=task, bits=bits)

    def qps_principal(self, *, quant_id: str, rank: int) -> dict[str, Any]:
        """QPiSSA principal."""
        return qps_qps_principal(quant_id=quant_id, rank=rank)

    def qps_train(self, *, principal_id: str) -> dict[str, Any]:
        """QPiSSA train."""
        return qps_qps_train(principal_id=principal_id)

    def qps_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """QPiSSA score."""
        return qps_qps_score(train_id=train_id, score=score)

    def qps_error(self, *, smaller_than_qlora: bool) -> dict[str, Any]:
        """QPiSSA error flag."""
        return qps_qps_error(smaller_than_qlora=smaller_than_qlora)

    def qps_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """QPiSSA loop plan."""
        return qps_qps_loop_plan(phase=phase)

    def msl_split(self, *, task: str, rank: int) -> dict[str, Any]:
        """MoSLoRA split."""
        return msl_msl_split(task=task, rank=rank)

    def msl_mixer(self, *, split_id: str) -> dict[str, Any]:
        """MoSLoRA mixer."""
        return msl_msl_mixer(split_id=split_id)

    def msl_train(self, *, mixer_id: str) -> dict[str, Any]:
        """MoSLoRA train."""
        return msl_msl_train(mixer_id=mixer_id)

    def msl_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """MoSLoRA score."""
        return msl_msl_score(train_id=train_id, score=score)

    def msl_fuse(self, *, flexible_fuse: bool) -> dict[str, Any]:
        """MoSLoRA fuse flag."""
        return msl_msl_fuse(flexible_fuse=flexible_fuse)

    def msl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MoSLoRA loop plan."""
        return msl_msl_loop_plan(phase=phase)

    def ldr_eval(self, *, task: str) -> dict[str, Any]:
        """LoRA-drop eval."""
        return ldr_ldr_eval(task=task)

    def ldr_keep(self, *, eval_id: str, keep_pct: int) -> dict[str, Any]:
        """LoRA-drop keep."""
        return ldr_ldr_keep(eval_id=eval_id, keep_pct=keep_pct)

    def ldr_share(self, *, keep_id: str) -> dict[str, Any]:
        """LoRA-drop share."""
        return ldr_ldr_share(keep_id=keep_id)

    def ldr_score(
        self, *, share_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-drop score."""
        return ldr_ldr_score(share_id=share_id, score=score)

    def ldr_prune(self, *, half_params: bool) -> dict[str, Any]:
        """LoRA-drop prune flag."""
        return ldr_ldr_prune(half_params=half_params)

    def ldr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-drop loop plan."""
        return ldr_ldr_loop_plan(phase=phase)

    def vbl_bank(self, *, task: str, size: int) -> dict[str, Any]:
        """VB-LoRA bank."""
        return vbl_vbl_bank(task=task, size=size)

    def vbl_topk(self, *, bank_id: str, k: int) -> dict[str, Any]:
        """VB-LoRA topk."""
        return vbl_vbl_topk(bank_id=bank_id, k=k)

    def vbl_compose(self, *, topk_id: str) -> dict[str, Any]:
        """VB-LoRA compose."""
        return vbl_vbl_compose(topk_id=topk_id)

    def vbl_score(
        self, *, compose_id: str, score: int
    ) -> dict[str, Any]:
        """VB-LoRA score."""
        return vbl_vbl_score(compose_id=compose_id, score=score)

    def vbl_extreme(self, *, extreme_compression: bool) -> dict[str, Any]:
        """VB-LoRA extreme flag."""
        return vbl_vbl_extreme(extreme_compression=extreme_compression)

    def vbl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """VB-LoRA loop plan."""
        return vbl_vbl_loop_plan(phase=phase)

    def opl_proj(self, *, task: str) -> dict[str, Any]:
        """OPLoRA proj."""
        return opl_opl_proj(task=task)

    def opl_constrain(self, *, proj_id: str, rank: int) -> dict[str, Any]:
        """OPLoRA constrain."""
        return opl_opl_constrain(proj_id=proj_id, rank=rank)

    def opl_train(self, *, constrain_id: str) -> dict[str, Any]:
        """OPLoRA train."""
        return opl_opl_train(constrain_id=constrain_id)

    def opl_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """OPLoRA score."""
        return opl_opl_score(train_id=train_id, score=score)

    def opl_forget(self, *, less_forgetting: bool) -> dict[str, Any]:
        """OPLoRA forget flag."""
        return opl_opl_forget(less_forgetting=less_forgetting)

    def opl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """OPLoRA loop plan."""
        return opl_opl_loop_plan(phase=phase)

    def gel_idim(self, *, task: str, layer: int) -> dict[str, Any]:
        """GeLoRA idim."""
        return gel_gel_idim(task=task, layer=layer)

    def gel_rank(self, *, idim_id: str, rank: int) -> dict[str, Any]:
        """GeLoRA rank."""
        return gel_gel_rank(idim_id=idim_id, rank=rank)

    def gel_train(self, *, rank_id: str) -> dict[str, Any]:
        """GeLoRA train."""
        return gel_gel_train(rank_id=rank_id)

    def gel_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """GeLoRA score."""
        return gel_gel_score(train_id=train_id, score=score)

    def gel_budget(self, *, within_budget: bool) -> dict[str, Any]:
        """GeLoRA budget flag."""
        return gel_gel_budget(within_budget=within_budget)

    def gel_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GeLoRA loop plan."""
        return gel_gel_loop_plan(phase=phase)

    def geo_dyn(self, *, task: str) -> dict[str, Any]:
        """GeoLoRA dyn."""
        return geo_geo_dyn(task=task)

    def geo_budget(self, *, dyn_id: str, layers: int) -> dict[str, Any]:
        """GeoLoRA budget."""
        return geo_geo_budget(dyn_id=dyn_id, layers=layers)

    def geo_train(self, *, budget_id: str) -> dict[str, Any]:
        """GeoLoRA train."""
        return geo_geo_train(budget_id=budget_id)

    def geo_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """GeoLoRA score."""
        return geo_geo_score(train_id=train_id, score=score)

    def geo_ortho(self, *, exact_ortho: bool) -> dict[str, Any]:
        """GeoLoRA ortho flag."""
        return geo_geo_ortho(exact_ortho=exact_ortho)

    def geo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GeoLoRA loop plan."""
        return geo_geo_loop_plan(phase=phase)

    def rlo_bases(self, *, task: str, count: int) -> dict[str, Any]:
        """RandLoRA bases."""
        return rlo_rlo_bases(task=task, count=count)

    def rlo_scale(self, *, bases_id: str) -> dict[str, Any]:
        """RandLoRA scale."""
        return rlo_rlo_scale(bases_id=bases_id)

    def rlo_train(self, *, scale_id: str) -> dict[str, Any]:
        """RandLoRA train."""
        return rlo_rlo_train(scale_id=scale_id)

    def rlo_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """RandLoRA score."""
        return rlo_rlo_score(train_id=train_id, score=score)

    def rlo_fullrank(self, *, full_rank_update: bool) -> dict[str, Any]:
        """RandLoRA fullrank flag."""
        return rlo_rlo_fullrank(full_rank_update=full_rank_update)

    def rlo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RandLoRA loop plan."""
        return rlo_rlo_loop_plan(phase=phase)

    def lsh_graph(self, *, task: str) -> dict[str, Any]:
        """LoRAShear graph."""
        return lsh_lsh_graph(task=task)

    def lsh_prune(self, *, graph_id: str, ratio_pct: int) -> dict[str, Any]:
        """LoRAShear prune."""
        return lsh_lsh_prune(graph_id=graph_id, ratio_pct=ratio_pct)

    def lsh_recover(self, *, prune_id: str) -> dict[str, Any]:
        """LoRAShear recover."""
        return lsh_lsh_recover(prune_id=prune_id)

    def lsh_score(
        self, *, recover_id: str, score: int
    ) -> dict[str, Any]:
        """LoRAShear score."""
        return lsh_lsh_score(recover_id=recover_id, score=score)

    def lsh_footprint(self, *, reduced: bool) -> dict[str, Any]:
        """LoRAShear footprint flag."""
        return lsh_lsh_footprint(reduced=reduced)

    def lsh_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRAShear loop plan."""
        return lsh_lsh_loop_plan(phase=phase)

    def aop_sub(self, *, task: str) -> dict[str, Any]:
        """Alternating OPLoRA subproblem."""
        return aop_aop_sub(task=task)

    def aop_alt(self, *, sub_id: str, steps: int) -> dict[str, Any]:
        """Alternating OPLoRA ALS steps."""
        return aop_aop_alt(sub_id=sub_id, steps=steps)

    def aop_train(self, *, alt_id: str) -> dict[str, Any]:
        """Alternating OPLoRA train."""
        return aop_aop_train(alt_id=alt_id)

    def aop_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """Alternating OPLoRA score."""
        return aop_aop_score(train_id=train_id, score=score)

    def aop_svd(self, *, near_svd: bool) -> dict[str, Any]:
        """Alternating OPLoRA near-SVD flag."""
        return aop_aop_svd(near_svd=near_svd)

    def aop_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Alternating OPLoRA loop plan."""
        return aop_aop_loop_plan(phase=phase)

    def lin_tsd(self, *, task: str, count: int) -> dict[str, Any]:
        """LoRA-Init TSD."""
        return lin_lin_tsd(task=task, count=count)

    def lin_init(self, *, tsd_id: str) -> dict[str, Any]:
        """LoRA-Init init."""
        return lin_lin_init(tsd_id=tsd_id)

    def lin_train(self, *, init_id: str) -> dict[str, Any]:
        """LoRA-Init train."""
        return lin_lin_train(init_id=init_id)

    def lin_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-Init score."""
        return lin_lin_score(train_id=train_id, score=score)

    def lin_fast(self, *, faster_convergence: bool) -> dict[str, Any]:
        """LoRA-Init fast flag."""
        return lin_lin_fast(faster_convergence=faster_convergence)

    def lin_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-Init loop plan."""
        return lin_lin_loop_plan(phase=phase)

    def lnu_act(self, *, task: str, samples: int) -> dict[str, Any]:
        """LoRA-Null activations."""
        return lnu_lnu_act(task=task, samples=samples)

    def lnu_null(self, *, act_id: str) -> dict[str, Any]:
        """LoRA-Null null space."""
        return lnu_lnu_null(act_id=act_id)

    def lnu_train(self, *, null_id: str) -> dict[str, Any]:
        """LoRA-Null train."""
        return lnu_lnu_train(null_id=null_id)

    def lnu_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-Null score."""
        return lnu_lnu_score(train_id=train_id, score=score)

    def lnu_forget(self, *, preserves_knowledge: bool) -> dict[str, Any]:
        """LoRA-Null forget flag."""
        return lnu_lnu_forget(preserves_knowledge=preserves_knowledge)

    def lnu_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-Null loop plan."""
        return lnu_lnu_loop_plan(phase=phase)

    def hyd_share(self, *, task: str) -> dict[str, Any]:
        """HydraLoRA shared A."""
        return hyd_hyd_share(task=task)

    def hyd_heads(self, *, share_id: str, heads: int) -> dict[str, Any]:
        """HydraLoRA multi-B heads."""
        return hyd_hyd_heads(share_id=share_id, heads=heads)

    def hyd_route(self, *, heads_id: str) -> dict[str, Any]:
        """HydraLoRA MoE route."""
        return hyd_hyd_route(heads_id=heads_id)

    def hyd_score(
        self, *, route_id: str, score: int
    ) -> dict[str, Any]:
        """HydraLoRA score."""
        return hyd_hyd_score(route_id=route_id, score=score)

    def hyd_nodomain(self, *, no_domain_labels: bool) -> dict[str, Any]:
        """HydraLoRA no-domain flag."""
        return hyd_hyd_nodomain(no_domain_labels=no_domain_labels)

    def hyd_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HydraLoRA loop plan."""
        return hyd_hyd_loop_plan(phase=phase)

    def llg_msu(self, *, task: str, adapters: int) -> dict[str, Any]:
        """LoRA-LEGO MSUs."""
        return llg_llg_msu(task=task, adapters=adapters)

    def llg_cluster(self, *, msu_id: str, k: int) -> dict[str, Any]:
        """LoRA-LEGO cluster."""
        return llg_llg_cluster(msu_id=msu_id, k=k)

    def llg_merge(self, *, cluster_id: str) -> dict[str, Any]:
        """LoRA-LEGO merge."""
        return llg_llg_merge(cluster_id=cluster_id)

    def llg_score(
        self, *, merge_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-LEGO score."""
        return llg_llg_score(merge_id=merge_id, score=score)

    def llg_modular(self, *, modular_merge: bool) -> dict[str, Any]:
        """LoRA-LEGO modular flag."""
        return llg_llg_modular(modular_merge=modular_merge)

    def llg_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-LEGO loop plan."""
        return llg_llg_loop_plan(phase=phase)

    def lme_plugin(self, *, task: str, experts: int) -> dict[str, Any]:
        """LoRAMoE plugin."""
        return lme_lme_plugin(task=task, experts=experts)

    def lme_balance(self, *, plugin_id: str) -> dict[str, Any]:
        """LoRAMoE balance."""
        return lme_lme_balance(plugin_id=plugin_id)

    def lme_route(self, *, balance_id: str) -> dict[str, Any]:
        """LoRAMoE route."""
        return lme_lme_route(balance_id=balance_id)

    def lme_score(
        self, *, route_id: str, score: int
    ) -> dict[str, Any]:
        """LoRAMoE score."""
        return lme_lme_score(route_id=route_id, score=score)

    def lme_forget(self, *, preserves_world: bool) -> dict[str, Any]:
        """LoRAMoE forget flag."""
        return lme_lme_forget(preserves_world=preserves_world)

    def lme_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRAMoE loop plan."""
        return lme_lme_loop_plan(phase=phase)

    def mel_experts(self, *, task: str, count: int) -> dict[str, Any]:
        """MoELoRA experts."""
        return mel_mel_experts(task=task, count=count)

    def mel_contrast(self, *, experts_id: str) -> dict[str, Any]:
        """MoELoRA contrast."""
        return mel_mel_contrast(experts_id=experts_id)

    def mel_gate(self, *, contrast_id: str) -> dict[str, Any]:
        """MoELoRA gate."""
        return mel_mel_gate(contrast_id=contrast_id)

    def mel_score(
        self, *, gate_id: str, score: int
    ) -> dict[str, Any]:
        """MoELoRA score."""
        return mel_mel_score(gate_id=gate_id, score=score)

    def mel_sparse(self, *, sparse_activate: bool) -> dict[str, Any]:
        """MoELoRA sparse flag."""
        return mel_mel_sparse(sparse_activate=sparse_activate)

    def mel_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MoELoRA loop plan."""
        return mel_mel_loop_plan(phase=phase)

    def lhb_pool(self, *, task: str, modules: int) -> dict[str, Any]:
        """LoraHub pool."""
        return lhb_lhb_pool(task=task, modules=modules)

    def lhb_compose(self, *, pool_id: str) -> dict[str, Any]:
        """LoraHub compose."""
        return lhb_lhb_compose(pool_id=pool_id)

    def lhb_adapt(self, *, compose_id: str, shots: int) -> dict[str, Any]:
        """LoraHub adapt."""
        return lhb_lhb_adapt(compose_id=compose_id, shots=shots)

    def lhb_score(
        self, *, adapt_id: str, score: int
    ) -> dict[str, Any]:
        """LoraHub score."""
        return lhb_lhb_score(adapt_id=adapt_id, score=score)

    def lhb_nograd(self, *, gradient_free: bool) -> dict[str, Any]:
        """LoraHub nograd flag."""
        return lhb_lhb_nograd(gradient_free=gradient_free)

    def lhb_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoraHub loop plan."""
        return lhb_lhb_loop_plan(phase=phase)

    def mlr_scale(self, *, task: str, shards: int) -> dict[str, Any]:
        """MultiLoRA scale."""
        return mlr_mlr_scale(task=task, shards=shards)

    def mlr_init(self, *, scale_id: str) -> dict[str, Any]:
        """MultiLoRA init."""
        return mlr_mlr_init(scale_id=scale_id)

    def mlr_train(self, *, init_id: str) -> dict[str, Any]:
        """MultiLoRA train."""
        return mlr_mlr_train(init_id=init_id)

    def mlr_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """MultiLoRA score."""
        return mlr_mlr_score(train_id=train_id, score=score)

    def mlr_demo(self, *, more_democratic: bool) -> dict[str, Any]:
        """MultiLoRA democratic flag."""
        return mlr_mlr_demo(more_democratic=more_democratic)

    def mlr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MultiLoRA loop plan."""
        return mlr_mlr_loop_plan(phase=phase)

    def mtl_task(self, *, task: str, tasks: int) -> dict[str, Any]:
        """MTL-LoRA task set."""
        return mtl_mtl_task(task=task, tasks=tasks)

    def mtl_spec(self, *, task_id: str) -> dict[str, Any]:
        """MTL-LoRA task-specific transforms."""
        return mtl_mtl_spec(task_id=task_id)

    def mtl_share(self, *, spec_id: str) -> dict[str, Any]:
        """MTL-LoRA dynamic share."""
        return mtl_mtl_share(spec_id=spec_id)

    def mtl_score(
        self, *, share_id: str, score: int
    ) -> dict[str, Any]:
        """MTL-LoRA score."""
        return mtl_mtl_score(share_id=share_id, score=score)

    def mtl_interfere(self, *, less_interference: bool) -> dict[str, Any]:
        """MTL-LoRA interference flag."""
        return mtl_mtl_interfere(less_interference=less_interference)

    def mtl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MTL-LoRA loop plan."""
        return mtl_mtl_loop_plan(phase=phase)

    def mal_mix(self, *, task: str, experts: int) -> dict[str, Any]:
        """MALoRA expert mix."""
        return mal_mal_mix(task=task, experts=experts)

    def mal_down(self, *, mix_id: str) -> dict[str, Any]:
        """MALoRA shared down-proj."""
        return mal_mal_down(mix_id=mix_id)

    def mal_up(self, *, down_id: str) -> dict[str, Any]:
        """MALoRA asymmetric up-proj."""
        return mal_mal_up(down_id=down_id)

    def mal_score(
        self, *, up_id: str, score: int
    ) -> dict[str, Any]:
        """MALoRA score."""
        return mal_mal_score(up_id=up_id, score=score)

    def mal_eff(self, *, fewer_params: bool) -> dict[str, Any]:
        """MALoRA efficiency flag."""
        return mal_mal_eff(fewer_params=fewer_params)

    def mal_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MALoRA loop plan."""
        return mal_mal_loop_plan(phase=phase)

    def lmi_split(self, *, task: str, rank: int) -> dict[str, Any]:
        """LoRA-Mini split."""
        return lmi_lmi_split(task=task, rank=rank)

    def lmi_inner(self, *, split_id: str) -> dict[str, Any]:
        """LoRA-Mini inner trainable."""
        return lmi_lmi_inner(split_id=split_id)

    def lmi_train(self, *, inner_id: str) -> dict[str, Any]:
        """LoRA-Mini train."""
        return lmi_lmi_train(inner_id=inner_id)

    def lmi_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-Mini score."""
        return lmi_lmi_score(train_id=train_id, score=score)

    def lmi_tiny(self, *, extreme_compress: bool) -> dict[str, Any]:
        """LoRA-Mini compress flag."""
        return lmi_lmi_tiny(extreme_compress=extreme_compress)

    def lmi_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-Mini loop plan."""
        return lmi_lmi_loop_plan(phase=phase)

    def qdy_range(
        self, *, task: str, r_min: int, r_max: int
    ) -> dict[str, Any]:
        """QDyLoRA rank range."""
        return qdy_qdy_range(task=task, r_min=r_min, r_max=r_max)

    def qdy_quant(self, *, range_id: str, bits: int) -> dict[str, Any]:
        """QDyLoRA quantize."""
        return qdy_qdy_quant(range_id=range_id, bits=bits)

    def qdy_train(self, *, quant_id: str) -> dict[str, Any]:
        """QDyLoRA train."""
        return qdy_qdy_train(quant_id=quant_id)

    def qdy_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """QDyLoRA score."""
        return qdy_qdy_score(train_id=train_id, score=score)

    def qdy_pick(self, *, pick_rank_at_infer: bool) -> dict[str, Any]:
        """QDyLoRA pick-rank flag."""
        return qdy_qdy_pick(pick_rank_at_infer=pick_rank_at_infer)

    def qdy_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """QDyLoRA loop plan."""
        return qdy_qdy_loop_plan(phase=phase)

    def lts_tsd(self, *, task: str, count: int) -> dict[str, Any]:
        """LoRA-TSD identify directions."""
        return lts_lts_tsd(task=task, count=count)

    def lts_init(self, *, tsd_id: str) -> dict[str, Any]:
        """LoRA-TSD init from TSDs."""
        return lts_lts_init(tsd_id=tsd_id)

    def lts_dash(self, *, init_id: str) -> dict[str, Any]:
        """LoRA-TSD dash amplify."""
        return lts_lts_dash(init_id=init_id)

    def lts_score(
        self, *, dash_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-TSD score."""
        return lts_lts_score(dash_id=dash_id, score=score)

    def lts_combo(self, *, uses_both: bool) -> dict[str, Any]:
        """LoRA-TSD Init+Dash combo flag."""
        return lts_lts_combo(uses_both=uses_both)

    def lts_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-TSD loop plan."""
        return lts_lts_loop_plan(phase=phase)

    def slr_pool(self, *, adapters: int) -> dict[str, Any]:
        """S-LoRA adapter pool."""
        return slr_slr_pool(adapters=adapters)

    def slr_page(self, *, pool_id: str, unified: bool) -> dict[str, Any]:
        """S-LoRA Unified Paging."""
        return slr_slr_page(pool_id=pool_id, unified=unified)

    def slr_batch(
        self, *, page_id: str, concurrent: int
    ) -> dict[str, Any]:
        """S-LoRA heterogeneous batch."""
        return slr_slr_batch(page_id=page_id, concurrent=concurrent)

    def slr_score(
        self, *, batch_id: str, score: int
    ) -> dict[str, Any]:
        """S-LoRA score."""
        return slr_slr_score(batch_id=batch_id, score=score)

    def slr_scale(self, *, thousands: bool) -> dict[str, Any]:
        """S-LoRA scale flag."""
        return slr_slr_scale(thousands=thousands)

    def slr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """S-LoRA loop plan."""
        return slr_slr_loop_plan(phase=phase)

    def cts_collect(self, *, adapters: int) -> dict[str, Any]:
        """Compress-then-Serve collect."""
        return cts_cts_collect(adapters=adapters)

    def cts_basis(self, *, collect_id: str) -> dict[str, Any]:
        """Compress-then-Serve shared basis."""
        return cts_cts_basis(collect_id=collect_id)

    def cts_scale(
        self, *, basis_id: str, adapters: int
    ) -> dict[str, Any]:
        """Compress-then-Serve per-adapter scales."""
        return cts_cts_scale(basis_id=basis_id, adapters=adapters)

    def cts_score(
        self, *, scale_id: str, score: int
    ) -> dict[str, Any]:
        """Compress-then-Serve score."""
        return cts_cts_score(scale_id=scale_id, score=score)

    def cts_cluster(self, *, cluster_for_large: bool) -> dict[str, Any]:
        """Compress-then-Serve cluster flag."""
        return cts_cts_cluster(cluster_for_large=cluster_for_large)

    def cts_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Compress-then-Serve loop plan."""
        return cts_cts_loop_plan(phase=phase)

    def flo_clients(self, *, clients: int) -> dict[str, Any]:
        """FLoRA client set."""
        return flo_flo_clients(clients=clients)

    def flo_stack(
        self, *, clients_id: str, hetero_ranks: bool
    ) -> dict[str, Any]:
        """FLoRA stack adapters."""
        return flo_flo_stack(
            clients_id=clients_id, hetero_ranks=hetero_ranks
        )

    def flo_agg(self, *, stack_id: str) -> dict[str, Any]:
        """FLoRA stacking aggregation."""
        return flo_flo_agg(stack_id=stack_id)

    def flo_score(
        self, *, agg_id: str, score: int
    ) -> dict[str, Any]:
        """FLoRA score."""
        return flo_flo_score(agg_id=agg_id, score=score)

    def flo_hetero(self, *, supports_hetero: bool) -> dict[str, Any]:
        """FLoRA hetero flag."""
        return flo_flo_hetero(supports_hetero=supports_hetero)

    def flo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """FLoRA loop plan."""
        return flo_flo_loop_plan(phase=phase)

    def pun_backbone(self, *, model: str) -> dict[str, Any]:
        """Punica shared backbone."""
        return pun_pun_backbone(model=model)

    def pun_sgmv(self, *, backbone_id: str, adapters: int) -> dict[str, Any]:
        """Punica SGMV batch."""
        return pun_pun_sgmv(backbone_id=backbone_id, adapters=adapters)

    def pun_sched(self, *, sgmv_id: str) -> dict[str, Any]:
        """Punica scheduler."""
        return pun_pun_sched(sgmv_id=sgmv_id)

    def pun_score(
        self, *, sched_id: str, score: int
    ) -> dict[str, Any]:
        """Punica score."""
        return pun_pun_score(sched_id=sched_id, score=score)

    def pun_multi(self, *, multi_tenant: bool) -> dict[str, Any]:
        """Punica multi-tenant flag."""
        return pun_pun_multi(multi_tenant=multi_tenant)

    def pun_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Punica loop plan."""
        return pun_pun_loop_plan(phase=phase)

    def mla_pipe(self, *, tasks: int, gpus: int) -> dict[str, Any]:
        """mLoRA pipeline."""
        return mla_mla_pipe(tasks=tasks, gpus=gpus)

    def mla_batch(self, *, pipe_id: str) -> dict[str, Any]:
        """mLoRA BatchLoRA."""
        return mla_mla_batch(pipe_id=pipe_id)

    def mla_train(self, *, batch_id: str) -> dict[str, Any]:
        """mLoRA train."""
        return mla_mla_train(batch_id=batch_id)

    def mla_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """mLoRA score."""
        return mla_mla_score(train_id=train_id, score=score)

    def mla_eff(self, *, lower_completion_time: bool) -> dict[str, Any]:
        """mLoRA efficiency flag."""
        return mla_mla_eff(lower_completion_time=lower_completion_time)

    def mla_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """mLoRA loop plan."""
        return mla_mla_loop_plan(phase=phase)

    def swl_alloc(self, *, task: str, rank: int) -> dict[str, Any]:
        """SwitchLoRA allocate."""
        return swl_swl_alloc(task=task, rank=rank)

    def swl_switch(self, *, alloc_id: str, dims: int) -> dict[str, Any]:
        """SwitchLoRA switch dims."""
        return swl_swl_switch(alloc_id=alloc_id, dims=dims)

    def swl_train(self, *, switch_id: str) -> dict[str, Any]:
        """SwitchLoRA train."""
        return swl_swl_train(switch_id=switch_id)

    def swl_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """SwitchLoRA score."""
        return swl_swl_score(train_id=train_id, score=score)

    def swl_full(self, *, mimics_fullrank: bool) -> dict[str, Any]:
        """SwitchLoRA full-rank mimic flag."""
        return swl_swl_full(mimics_fullrank=mimics_fullrank)

    def swl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SwitchLoRA loop plan."""
        return swl_swl_loop_plan(phase=phase)

    def col_tune(self, *, task: str, rank: int) -> dict[str, Any]:
        """COLA tune LoRA link."""
        return col_col_tune(task=task, rank=rank)

    def col_knot(self, *, tune_id: str) -> dict[str, Any]:
        """COLA tie knot."""
        return col_col_knot(tune_id=tune_id)

    def col_extend(self, *, knot_id: str) -> dict[str, Any]:
        """COLA extend chain."""
        return col_col_extend(knot_id=knot_id)

    def col_score(
        self, *, extend_id: str, score: int
    ) -> dict[str, Any]:
        """COLA score."""
        return col_col_score(extend_id=extend_id, score=score)

    def col_gap(self, *, closes_ft_gap: bool) -> dict[str, Any]:
        """COLA FT-gap flag."""
        return col_col_gap(closes_ft_gap=closes_ft_gap)

    def col_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """COLA loop plan."""
        return col_col_loop_plan(phase=phase)

    def dlr_norm(self, *, task: str, rank: int) -> dict[str, Any]:
        """DeLoRA normalize."""
        return dlr_dlr_norm(task=task, rank=rank)

    def dlr_bound(
        self, *, norm_id: str, lambda_bound: int
    ) -> dict[str, Any]:
        """DeLoRA Frobenius bound."""
        return dlr_dlr_bound(norm_id=norm_id, lambda_bound=lambda_bound)

    def dlr_train(self, *, bound_id: str) -> dict[str, Any]:
        """DeLoRA train."""
        return dlr_dlr_train(bound_id=bound_id)

    def dlr_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """DeLoRA score."""
        return dlr_dlr_score(train_id=train_id, score=score)

    def dlr_robust(self, *, hyperparam_robust: bool) -> dict[str, Any]:
        """DeLoRA robustness flag."""
        return dlr_dlr_robust(hyperparam_robust=hyperparam_robust)

    def dlr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """DeLoRA loop plan."""
        return dlr_dlr_loop_plan(phase=phase)

    def meo_mini(
        self, *, task: str, n_minis: int, mini_rank: int
    ) -> dict[str, Any]:
        """MELoRA mini ensemble."""
        return meo_meo_mini(
            task=task, n_minis=n_minis, mini_rank=mini_rank
        )

    def meo_diag(self, *, mini_id: str) -> dict[str, Any]:
        """MELoRA block-diagonal."""
        return meo_meo_diag(mini_id=mini_id)

    def meo_train(self, *, diag_id: str) -> dict[str, Any]:
        """MELoRA train."""
        return meo_meo_train(diag_id=diag_id)

    def meo_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """MELoRA score."""
        return meo_meo_score(train_id=train_id, score=score)

    def meo_rank(self, *, higher_effective_rank: bool) -> dict[str, Any]:
        """MELoRA effective-rank flag."""
        return meo_meo_rank(higher_effective_rank=higher_effective_rank)

    def meo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MELoRA loop plan."""
        return meo_meo_loop_plan(phase=phase)

    def rlr_warm(self, *, task: str, steps: int) -> dict[str, Any]:
        """ReLoRA warm-start."""
        return rlr_rlr_warm(task=task, steps=steps)

    def rlr_merge(self, *, warm_id: str) -> dict[str, Any]:
        """ReLoRA merge restart."""
        return rlr_rlr_merge(warm_id=warm_id)

    def rlr_jagged(self, *, merge_id: str) -> dict[str, Any]:
        """ReLoRA jagged LR."""
        return rlr_rlr_jagged(merge_id=merge_id)

    def rlr_score(
        self, *, jagged_id: str, score: int
    ) -> dict[str, Any]:
        """ReLoRA score."""
        return rlr_rlr_score(jagged_id=jagged_id, score=score)

    def rlr_high(self, *, high_rank_update: bool) -> dict[str, Any]:
        """ReLoRA high-rank flag."""
        return rlr_rlr_high(high_rank_update=high_rank_update)

    def rlr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ReLoRA loop plan."""
        return rlr_rlr_loop_plan(phase=phase)

    def eth_plane(self, *, task: str, reflections: int) -> dict[str, Any]:
        """ETHER hyperplane alloc."""
        return eth_eth_plane(task=task, reflections=reflections)

    def eth_reflect(self, *, plane_id: str) -> dict[str, Any]:
        """ETHER reflect."""
        return eth_eth_reflect(plane_id=plane_id)

    def eth_train(self, *, reflect_id: str) -> dict[str, Any]:
        """ETHER train."""
        return eth_eth_train(reflect_id=reflect_id)

    def eth_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """ETHER score."""
        return eth_eth_score(train_id=train_id, score=score)

    def eth_plus(self, *, ether_plus: bool) -> dict[str, Any]:
        """ETHER+ flag."""
        return eth_eth_plus(ether_plus=ether_plus)

    def eth_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ETHER loop plan."""
        return eth_eth_loop_plan(phase=phase)

    def lco_concepts(self, *, task: str, n_loras: int) -> dict[str, Any]:
        """LoRA-Composer multi-concept set."""
        return lco_lco_concepts(task=task, n_loras=n_loras)

    def lco_inject(self, *, concepts_id: str) -> dict[str, Any]:
        """LoRA-Composer inject."""
        return lco_lco_inject(concepts_id=concepts_id)

    def lco_isolate(self, *, inject_id: str) -> dict[str, Any]:
        """LoRA-Composer isolate."""
        return lco_lco_isolate(inject_id=inject_id)

    def lco_score(
        self, *, isolate_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA-Composer score."""
        return lco_lco_score(isolate_id=isolate_id, score=score)

    def lco_free(self, *, training_free: bool) -> dict[str, Any]:
        """LoRA-Composer training-free flag."""
        return lco_lco_free(training_free=training_free)

    def lco_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-Composer loop plan."""
        return lco_lco_loop_plan(phase=phase)

    def car_compress(self, *, task: str, keep_rank: int) -> dict[str, Any]:
        """CARE-LoRA compress activations."""
        return car_car_compress(task=task, keep_rank=keep_rank)

    def car_recon(self, *, compress_id: str) -> dict[str, Any]:
        """CARE-LoRA reconstruct."""
        return car_car_recon(compress_id=compress_id)

    def car_train(self, *, recon_id: str) -> dict[str, Any]:
        """CARE-LoRA train."""
        return car_car_train(recon_id=recon_id)

    def car_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """CARE-LoRA score."""
        return car_car_score(train_id=train_id, score=score)

    def car_mem(self, *, activation_saved: bool) -> dict[str, Any]:
        """CARE-LoRA memory flag."""
        return car_car_mem(activation_saved=activation_saved)

    def car_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CARE-LoRA loop plan."""
        return car_car_loop_plan(phase=phase)

    def lrr_pair(self, *, task: str, n_pairs: int) -> dict[str, Any]:
        """LoRA.rar subject–style pairs."""
        return lrr_lrr_pair(task=task, n_pairs=n_pairs)

    def lrr_hyper(self, *, pair_id: str) -> dict[str, Any]:
        """LoRA.rar hypernetwork."""
        return lrr_lrr_hyper(pair_id=pair_id)

    def lrr_merge(self, *, hyper_id: str) -> dict[str, Any]:
        """LoRA.rar merge."""
        return lrr_lrr_merge(hyper_id=hyper_id)

    def lrr_score(
        self, *, merge_id: str, score: int
    ) -> dict[str, Any]:
        """LoRA.rar score."""
        return lrr_lrr_score(merge_id=merge_id, score=score)

    def lrr_fast(self, *, realtime_merge: bool) -> dict[str, Any]:
        """LoRA.rar realtime flag."""
        return lrr_lrr_fast(realtime_merge=realtime_merge)

    def lrr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA.rar loop plan."""
        return lrr_lrr_loop_plan(phase=phase)

    def svf_svd(self, *, task: str, keep: int) -> dict[str, Any]:
        """SVFT singular-vector factor."""
        return svf_svf_svd(task=task, keep=keep)

    def svf_sparse(self, *, svd_id: str) -> dict[str, Any]:
        """SVFT sparse pattern."""
        return svf_svf_sparse(svd_id=svd_id)

    def svf_train(self, *, sparse_id: str) -> dict[str, Any]:
        """SVFT train coefficients."""
        return svf_svf_train(sparse_id=sparse_id)

    def svf_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """SVFT score."""
        return svf_svf_score(train_id=train_id, score=score)

    def svf_geom(self, *, weight_dependent: bool) -> dict[str, Any]:
        """SVFT geometry flag."""
        return svf_svf_geom(weight_dependent=weight_dependent)

    def svf_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SVFT loop plan."""
        return svf_svf_loop_plan(phase=phase)

    def fly_proj(self, *, task: str, rank: int) -> dict[str, Any]:
        """FlyLoRA frozen projection."""
        return fly_fly_proj(task=task, rank=rank)

    def fly_topk(self, *, proj_id: str, k: int) -> dict[str, Any]:
        """FlyLoRA top-k experts."""
        return fly_fly_topk(proj_id=proj_id, k=k)

    def fly_train(self, *, topk_id: str) -> dict[str, Any]:
        """FlyLoRA train."""
        return fly_fly_train(topk_id=topk_id)

    def fly_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """FlyLoRA score."""
        return fly_fly_score(train_id=train_id, score=score)

    def fly_implicit(self, *, implicit_router: bool) -> dict[str, Any]:
        """FlyLoRA implicit-router flag."""
        return fly_fly_implicit(implicit_router=implicit_router)

    def fly_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """FlyLoRA loop plan."""
        return fly_fly_loop_plan(phase=phase)

    def nla_basis(self, *, task: str, n_basis: int) -> dict[str, Any]:
        """NOLA random bases."""
        return nla_nla_basis(task=task, n_basis=n_basis)

    def nla_coeff(self, *, basis_id: str) -> dict[str, Any]:
        """NOLA coefficients."""
        return nla_nla_coeff(basis_id=basis_id)

    def nla_train(self, *, coeff_id: str) -> dict[str, Any]:
        """NOLA train."""
        return nla_nla_train(coeff_id=coeff_id)

    def nla_score(
        self, *, train_id: str, score: int
    ) -> dict[str, Any]:
        """NOLA score."""
        return nla_nla_score(train_id=train_id, score=score)

    def nla_compact(self, *, beyond_rank1: bool) -> dict[str, Any]:
        """NOLA compact flag."""
        return nla_nla_compact(beyond_rank1=beyond_rank1)

    def nla_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """NOLA loop plan."""
        return nla_nla_loop_plan(phase=phase)

    def mxl_experts(self, *, task: str, n_experts: int) -> dict[str, Any]:
        """MixLoRA FFN experts."""
        return mxl_mxl_experts(task=task, n_experts=n_experts)

    def mxl_route(self, *, experts_id: str, k: int) -> dict[str, Any]:
        """MixLoRA top-k router."""
        return mxl_mxl_route(experts_id=experts_id, k=k)

    def mxl_attn(self, *, route_id: str) -> dict[str, Any]:
        """MixLoRA attention LoRAs."""
        return mxl_mxl_attn(route_id=route_id)

    def mxl_score(
        self, *, attn_id: str, score: int
    ) -> dict[str, Any]:
        """MixLoRA score."""
        return mxl_mxl_score(attn_id=attn_id, score=score)

    def mxl_balance(self, *, load_balance: bool) -> dict[str, Any]:
        """MixLoRA load-balance flag."""
        return mxl_mxl_balance(load_balance=load_balance)

    def mxl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MixLoRA loop plan."""
        return mxl_mxl_loop_plan(phase=phase)

    def spr_group(self, *, task: str, groups: int) -> dict[str, Any]:
        """SuperLoRA grouping."""
        return spr_spr_group(task=task, groups=groups)

    def spr_fold(self, *, group_id: str) -> dict[str, Any]:
        """SuperLoRA fold."""
        return spr_spr_fold(group_id=group_id)

    def spr_factor(self, *, fold_id: str) -> dict[str, Any]:
        """SuperLoRA factor."""
        return spr_spr_factor(fold_id=fold_id)

    def spr_score(
        self, *, factor_id: str, score: int
    ) -> dict[str, Any]:
        """SuperLoRA score."""
        return spr_spr_score(factor_id=factor_id, score=score)

    def spr_unify(self, *, unifies_loha_lokr: bool) -> dict[str, Any]:
        """SuperLoRA unify flag."""
        return spr_spr_unify(unifies_loha_lokr=unifies_loha_lokr)

    def spr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SuperLoRA loop plan."""
        return spr_spr_loop_plan(phase=phase)

    def tld_tie(self, *, task: str, layers: int) -> dict[str, Any]:
        """Tied-LoRA weight tying."""
        return tld_tld_tie(task=task, layers=layers)

    def tld_select(self, *, tie_id: str) -> dict[str, Any]:
        """Tied-LoRA selective train."""
        return tld_tld_select(tie_id=tie_id)

    def tld_scale(self, *, select_id: str) -> dict[str, Any]:
        """Tied-LoRA scale vectors."""
        return tld_tld_scale(select_id=select_id)

    def tld_score(
        self, *, scale_id: str, score: int
    ) -> dict[str, Any]:
        """Tied-LoRA score."""
        return tld_tld_score(scale_id=scale_id, score=score)

    def tld_frac(self, *, fraction_of_lora: bool) -> dict[str, Any]:
        """Tied-LoRA fraction flag."""
        return tld_tld_frac(fraction_of_lora=fraction_of_lora)

    def tld_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Tied-LoRA loop plan."""
        return tld_tld_loop_plan(phase=phase)

    def qal_group(self, *, task: str, groups: int) -> dict[str, Any]:
        """QA-LoRA grouping."""
        return qal_qal_group(task=task, groups=groups)

    def qal_quant(self, *, group_id: str, bits: int) -> dict[str, Any]:
        """QA-LoRA quantize."""
        return qal_qal_quant(group_id=group_id, bits=bits)

    def qal_adapt(self, *, quant_id: str) -> dict[str, Any]:
        """QA-LoRA grouped adapters."""
        return qal_qal_adapt(quant_id=quant_id)

    def qal_score(
        self, *, adapt_id: str, score: int
    ) -> dict[str, Any]:
        """QA-LoRA score."""
        return qal_qal_score(adapt_id=adapt_id, score=score)

    def qal_merge(self, *, merge_int4: bool) -> dict[str, Any]:
        """QA-LoRA INT4 merge flag."""
        return qal_qal_merge(merge_int4=merge_int4)

    def qal_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """QA-LoRA loop plan."""
        return qal_qal_loop_plan(phase=phase)

    def ulo_space(self, *, task: str, dim: int) -> dict[str, Any]:
        """Uni-LoRA subspace."""
        return ulo_ulo_space(task=task, dim=dim)

    def ulo_iso(self, *, space_id: str) -> dict[str, Any]:
        """Uni-LoRA isometric projection."""
        return ulo_ulo_iso(space_id=space_id)

    def ulo_vec(self, *, iso_id: str) -> dict[str, Any]:
        """Uni-LoRA shared vector."""
        return ulo_ulo_vec(iso_id=iso_id)

    def ulo_score(self, *, vec_id: str, score: int) -> dict[str, Any]:
        """Uni-LoRA score."""
        return ulo_ulo_score(vec_id=vec_id, score=score)

    def ulo_one(self, *, one_vector: bool) -> dict[str, Any]:
        """Uni-LoRA one-vector flag."""
        return ulo_ulo_one(one_vector=one_vector)

    def ulo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Uni-LoRA loop plan."""
        return ulo_ulo_loop_plan(phase=phase)

    def bor_row(self, *, task: str) -> dict[str, Any]:
        """BoRA row magnitudes."""
        return bor_bor_row(task=task)

    def bor_col(self, *, row_id: str) -> dict[str, Any]:
        """BoRA column magnitudes."""
        return bor_bor_col(row_id=row_id)

    def bor_train(self, *, col_id: str) -> dict[str, Any]:
        """BoRA train."""
        return bor_bor_train(col_id=col_id)

    def bor_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """BoRA score."""
        return bor_bor_score(train_id=train_id, score=score)

    def bor_sym(self, *, symmetric: bool) -> dict[str, Any]:
        """BoRA symmetry flag."""
        return bor_bor_sym(symmetric=symmetric)

    def bor_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """BoRA loop plan."""
        return bor_bor_loop_plan(phase=phase)

    def qga_weight(self, *, task: str) -> dict[str, Any]:
        """Q-GaLore INT8 weights."""
        return qga_qga_weight(task=task)

    def qga_proj(self, *, weight_id: str, rank: int) -> dict[str, Any]:
        """Q-GaLore INT4 projection."""
        return qga_qga_proj(weight_id=weight_id, rank=rank)

    def qga_lazy(self, *, proj_id: str) -> dict[str, Any]:
        """Q-GaLore lazy SVD."""
        return qga_qga_lazy(proj_id=proj_id)

    def qga_score(self, *, lazy_id: str, score: int) -> dict[str, Any]:
        """Q-GaLore score."""
        return qga_qga_score(lazy_id=lazy_id, score=score)

    def qga_mem(self, *, consumer_gpu: bool) -> dict[str, Any]:
        """Q-GaLore memory flag."""
        return qga_qga_mem(consumer_gpu=consumer_gpu)

    def qga_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Q-GaLore loop plan."""
        return qga_qga_loop_plan(phase=phase)

    def lfw_pool(self, *, task: str, n_loras: int) -> dict[str, Any]:
        """LoRA-Flow skill pool."""
        return lfw_lfw_pool(task=task, n_loras=n_loras)

    def lfw_gate(self, *, pool_id: str) -> dict[str, Any]:
        """LoRA-Flow fusion gate."""
        return lfw_lfw_gate(pool_id=pool_id)

    def lfw_token(self, *, gate_id: str) -> dict[str, Any]:
        """LoRA-Flow token weights."""
        return lfw_lfw_token(gate_id=gate_id)

    def lfw_score(self, *, token_id: str, score: int) -> dict[str, Any]:
        """LoRA-Flow score."""
        return lfw_lfw_score(token_id=token_id, score=score)

    def lfw_few(self, *, few_shot: bool) -> dict[str, Any]:
        """LoRA-Flow few-shot flag."""
        return lfw_lfw_few(few_shot=few_shot)

    def lfw_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRA-Flow loop plan."""
        return lfw_lfw_loop_plan(phase=phase)

    def ros_rank(self, *, task: str, rank: int) -> dict[str, Any]:
        """RoSA low-rank branch."""
        return ros_ros_rank(task=task, rank=rank)

    def ros_sparse(self, *, rank_id: str) -> dict[str, Any]:
        """RoSA sparse residual."""
        return ros_ros_sparse(rank_id=rank_id)

    def ros_train(self, *, sparse_id: str) -> dict[str, Any]:
        """RoSA train."""
        return ros_ros_train(sparse_id=sparse_id)

    def ros_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """RoSA score."""
        return ros_ros_score(train_id=train_id, score=score)

    def ros_fft(self, *, matches_fft: bool) -> dict[str, Any]:
        """RoSA FFT-recovery flag."""
        return ros_ros_fft(matches_fft=matches_fft)

    def ros_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """RoSA loop plan."""
        return ros_ros_loop_plan(phase=phase)

    def abb_left(self, *, task: str, rank: int) -> dict[str, Any]:
        """ABBA left factor."""
        return abb_abb_left(task=task, rank=rank)

    def abb_right(self, *, left_id: str) -> dict[str, Any]:
        """ABBA right factor."""
        return abb_abb_right(left_id=left_id)

    def abb_hadamard(self, *, right_id: str) -> dict[str, Any]:
        """ABBA Hadamard."""
        return abb_abb_hadamard(right_id=right_id)

    def abb_score(self, *, hadamard_id: str, score: int) -> dict[str, Any]:
        """ABBA score."""
        return abb_abb_score(hadamard_id=hadamard_id, score=score)

    def abb_expr(self, *, expressive: bool) -> dict[str, Any]:
        """ABBA expressivity flag."""
        return abb_abb_expr(expressive=expressive)

    def abb_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ABBA loop plan."""
        return abb_abb_loop_plan(phase=phase)

    def bha_split(self, *, task: str, blocks: int) -> dict[str, Any]:
        """BoHA block split."""
        return bha_bha_split(task=task, blocks=blocks)

    def bha_hadamard(self, *, split_id: str) -> dict[str, Any]:
        """BoHA per-block Hadamard."""
        return bha_bha_hadamard(split_id=split_id)

    def bha_train(self, *, hadamard_id: str) -> dict[str, Any]:
        """BoHA train."""
        return bha_bha_train(hadamard_id=hadamard_id)

    def bha_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """BoHA score."""
        return bha_bha_score(train_id=train_id, score=score)

    def bha_local(self, *, localized: bool) -> dict[str, Any]:
        """BoHA localized-rank flag."""
        return bha_bha_local(localized=localized)

    def bha_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """BoHA loop plan."""
        return bha_bha_loop_plan(phase=phase)

    def smo_struct(self, *, task: str, subspaces: int) -> dict[str, Any]:
        """SMoA subspaces."""
        return smo_smo_struct(task=task, subspaces=subspaces)

    def smo_mod(self, *, struct_id: str) -> dict[str, Any]:
        """SMoA modulation."""
        return smo_smo_mod(struct_id=struct_id)

    def smo_train(self, *, mod_id: str) -> dict[str, Any]:
        """SMoA train."""
        return smo_smo_train(mod_id=mod_id)

    def smo_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """SMoA score."""
        return smo_smo_score(train_id=train_id, score=score)

    def smo_rank(self, *, high_rank: bool) -> dict[str, Any]:
        """SMoA high-rank flag."""
        return smo_smo_rank(high_rank=high_rank)

    def smo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SMoA loop plan."""
        return smo_smo_loop_plan(phase=phase)

    def glo_prompt(self, *, task: str) -> dict[str, Any]:
        """GLoRA prompt module."""
        return glo_glo_prompt(task=task)

    def glo_scale(self, *, prompt_id: str) -> dict[str, Any]:
        """GLoRA scale."""
        return glo_glo_scale(prompt_id=prompt_id)

    def glo_search(self, *, scale_id: str) -> dict[str, Any]:
        """GLoRA layer search."""
        return glo_glo_search(scale_id=scale_id)

    def glo_score(self, *, search_id: str, score: int) -> dict[str, Any]:
        """GLoRA score."""
        return glo_glo_score(search_id=search_id, score=score)

    def glo_zero(self, *, zero_infer: bool) -> dict[str, Any]:
        """GLoRA zero-infer flag."""
        return glo_glo_zero(zero_infer=zero_infer)

    def glo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """GLoRA loop plan."""
        return glo_glo_loop_plan(phase=phase)

    def plr_stage(self, *, task: str, stages: int) -> dict[str, Any]:
        """PeriodicLoRA stage."""
        return plr_plr_stage(task=task, stages=stages)

    def plr_merge(self, *, stage_id: str) -> dict[str, Any]:
        """PeriodicLoRA merge into W."""
        return plr_plr_merge(stage_id=stage_id)

    def plr_reset(self, *, merge_id: str) -> dict[str, Any]:
        """PeriodicLoRA reinit."""
        return plr_plr_reset(merge_id=merge_id)

    def plr_score(self, *, reset_id: str, score: int) -> dict[str, Any]:
        """PeriodicLoRA score."""
        return plr_plr_score(reset_id=reset_id, score=score)

    def plr_rank(self, *, accum_rank: bool) -> dict[str, Any]:
        """PeriodicLoRA accumulated-rank flag."""
        return plr_plr_rank(accum_rank=accum_rank)

    def plr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PeriodicLoRA loop plan."""
        return plr_plr_loop_plan(phase=phase)

    def hir_base(self, *, task: str) -> dict[str, Any]:
        """HiRA freeze W0."""
        return hir_hir_base(task=task)

    def hir_factors(self, *, base_id: str, rank: int) -> dict[str, Any]:
        """HiRA low-rank A, B."""
        return hir_hir_factors(base_id=base_id, rank=rank)

    def hir_hadamard(self, *, factors_id: str) -> dict[str, Any]:
        """HiRA W0 ⊙ (BA)."""
        return hir_hir_hadamard(factors_id=factors_id)

    def hir_score(self, *, hadamard_id: str, score: int) -> dict[str, Any]:
        """HiRA score."""
        return hir_hir_score(hadamard_id=hadamard_id, score=score)

    def hir_merge(self, *, zero_infer: bool) -> dict[str, Any]:
        """HiRA merge-into-W0 flag."""
        return hir_hir_merge(zero_infer=zero_infer)

    def hir_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HiRA loop plan."""
        return hir_hir_loop_plan(phase=phase)

    def cnl_pack(self, *, task: str, adapters: int) -> dict[str, Any]:
        """PLoRA concurrent pack."""
        return cnl_cnl_pack(task=task, adapters=adapters)

    def cnl_fuse(self, *, pack_id: str) -> dict[str, Any]:
        """PLoRA concurrent fuse."""
        return cnl_cnl_fuse(pack_id=pack_id)

    def cnl_train(self, *, fuse_id: str) -> dict[str, Any]:
        """PLoRA concurrent train."""
        return cnl_cnl_train(fuse_id=fuse_id)

    def cnl_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """PLoRA concurrent score."""
        return cnl_cnl_score(train_id=train_id, score=score)

    def cnl_hw(self, *, better_util: bool) -> dict[str, Any]:
        """PLoRA concurrent util flag."""
        return cnl_cnl_hw(better_util=better_util)

    def cnl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """PLoRA concurrent loop plan."""
        return cnl_cnl_loop_plan(phase=phase)

    def llr_window(self, *, task: str, ctx_len: int) -> dict[str, Any]:
        """LongLoRA long-context window."""
        return llr_llr_window(task=task, ctx_len=ctx_len)

    def llr_shift(self, *, window_id: str) -> dict[str, Any]:
        """LongLoRA S2-Attn shift."""
        return llr_llr_shift(window_id=window_id)

    def llr_lora(self, *, shift_id: str, rank: int) -> dict[str, Any]:
        """LongLoRA adapter."""
        return llr_llr_lora(shift_id=shift_id, rank=rank)

    def llr_score(self, *, lora_id: str, score: int) -> dict[str, Any]:
        """LongLoRA score."""
        return llr_llr_score(lora_id=lora_id, score=score)

    def llr_sparse(self, *, sparse_train: bool) -> dict[str, Any]:
        """LongLoRA sparse-train flag."""
        return llr_llr_sparse(sparse_train=sparse_train)

    def llr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LongLoRA loop plan."""
        return llr_llr_loop_plan(phase=phase)

    def lis_layers(self, *, task: str, n: int) -> dict[str, Any]:
        """LISA layer set."""
        return lis_lis_layers(task=task, n=n)

    def lis_sample(self, *, layers_id: str) -> dict[str, Any]:
        """LISA importance sample."""
        return lis_lis_sample(layers_id=layers_id)

    def lis_unfreeze(self, *, sample_id: str) -> dict[str, Any]:
        """LISA unfreeze sampled layers."""
        return lis_lis_unfreeze(sample_id=sample_id)

    def lis_score(self, *, unfreeze_id: str, score: int) -> dict[str, Any]:
        """LISA score."""
        return lis_lis_score(unfreeze_id=unfreeze_id, score=score)

    def lis_memory(self, *, less_opt: bool) -> dict[str, Any]:
        """LISA optimizer-memory flag."""
        return lis_lis_memory(less_opt=less_opt)

    def lis_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LISA loop plan."""
        return lis_lis_loop_plan(phase=phase)

    def nlr_landmark(self, *, task: str, k: int) -> dict[str, Any]:
        """NLoRA Nyström landmarks."""
        return nlr_nlr_landmark(task=task, k=k)

    def nlr_nystrom(self, *, landmark_id: str) -> dict[str, Any]:
        """NLoRA Nyström sketch."""
        return nlr_nlr_nystrom(landmark_id=landmark_id)

    def nlr_init(self, *, nystrom_id: str, rank: int) -> dict[str, Any]:
        """NLoRA init from sketch."""
        return nlr_nlr_init(nystrom_id=nystrom_id, rank=rank)

    def nlr_score(self, *, init_id: str, score: int) -> dict[str, Any]:
        """NLoRA score."""
        return nlr_nlr_score(init_id=init_id, score=score)

    def nlr_cheap(self, *, cheaper_svd: bool) -> dict[str, Any]:
        """NLoRA cheaper-than-SVD flag."""
        return nlr_nlr_cheap(cheaper_svd=cheaper_svd)

    def nlr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """NLoRA loop plan."""
        return nlr_nlr_loop_plan(phase=phase)

    def rsa_subspace(self, *, task: str, dim: int) -> dict[str, Any]:
        """ROSA random subspace."""
        return rsa_rsa_subspace(task=task, dim=dim)

    def rsa_project(self, *, subspace_id: str) -> dict[str, Any]:
        """ROSA project into subspace."""
        return rsa_rsa_project(subspace_id=subspace_id)

    def rsa_train(self, *, project_id: str) -> dict[str, Any]:
        """ROSA train in subspace."""
        return rsa_rsa_train(project_id=project_id)

    def rsa_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """ROSA score."""
        return rsa_rsa_score(train_id=train_id, score=score)

    def rsa_express(self, *, more_expressive: bool) -> dict[str, Any]:
        """ROSA expressiveness flag."""
        return rsa_rsa_express(more_expressive=more_expressive)

    def rsa_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ROSA loop plan."""
        return rsa_rsa_loop_plan(phase=phase)

    def hra_house(self, *, task: str, n: int) -> dict[str, Any]:
        """HRA Householder vectors."""
        return hra_hra_house(task=task, n=n)

    def hra_reflect(self, *, house_id: str) -> dict[str, Any]:
        """HRA compose reflections."""
        return hra_hra_reflect(house_id=house_id)

    def hra_train(self, *, reflect_id: str) -> dict[str, Any]:
        """HRA train adapter."""
        return hra_hra_train(reflect_id=reflect_id)

    def hra_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """HRA score."""
        return hra_hra_score(train_id=train_id, score=score)

    def hra_ortho(self, *, ortho_stable: bool) -> dict[str, Any]:
        """HRA orthogonal-stable flag."""
        return hra_hra_ortho(ortho_stable=ortho_stable)

    def hra_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """HRA loop plan."""
        return hra_hra_loop_plan(phase=phase)

    def hyb_lora(self, *, task: str) -> dict[str, Any]:
        """Hybrid PEFT LoRA-GA branch."""
        return hyb_hyb_lora(task=task)

    def hyb_boft(self, *, lora_id: str) -> dict[str, Any]:
        """Hybrid PEFT BOFT branch."""
        return hyb_hyb_boft(lora_id=lora_id)

    def hyb_fuse(self, *, boft_id: str) -> dict[str, Any]:
        """Hybrid PEFT fuse branches."""
        return hyb_hyb_fuse(boft_id=boft_id)

    def hyb_score(self, *, fuse_id: str, score: int) -> dict[str, Any]:
        """Hybrid PEFT score."""
        return hyb_hyb_score(fuse_id=fuse_id, score=score)

    def hyb_stable(self, *, more_stable: bool) -> dict[str, Any]:
        """Hybrid PEFT stability flag."""
        return hyb_hyb_stable(more_stable=more_stable)

    def hyb_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """Hybrid PEFT loop plan."""
        return hyb_hyb_loop_plan(phase=phase)

    def lrt_tensor(self, *, task: str, order: int) -> dict[str, Any]:
        """LoRTA unified tensor."""
        return lrt_lrt_tensor(task=task, order=order)

    def lrt_cp(self, *, tensor_id: str, rank: int) -> dict[str, Any]:
        """LoRTA CP decompose."""
        return lrt_lrt_cp(tensor_id=tensor_id, rank=rank)

    def lrt_share(self, *, cp_id: str) -> dict[str, Any]:
        """LoRTA share factors."""
        return lrt_lrt_share(cp_id=cp_id)

    def lrt_score(self, *, share_id: str, score: int) -> dict[str, Any]:
        """LoRTA score."""
        return lrt_lrt_score(share_id=share_id, score=score)

    def lrt_compact(self, *, fewer_params: bool) -> dict[str, Any]:
        """LoRTA fewer-params flag."""
        return lrt_lrt_compact(fewer_params=fewer_params)

    def lrt_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRTA loop plan."""
        return lrt_lrt_loop_plan(phase=phase)

    def clo_route(self, *, task: str) -> dict[str, Any]:
        """C-LoRA shared route."""
        return clo_clo_route(task=task)

    def clo_task(self, *, route_id: str) -> dict[str, Any]:
        """C-LoRA bind task."""
        return clo_clo_task(route_id=route_id)

    def clo_ortho(self, *, task_id: str) -> dict[str, Any]:
        """C-LoRA orthogonality."""
        return clo_clo_ortho(task_id=task_id)

    def clo_score(self, *, ortho_id: str, score: int) -> dict[str, Any]:
        """C-LoRA score."""
        return clo_clo_score(ortho_id=ortho_id, score=score)

    def clo_forget(self, *, less_forget: bool) -> dict[str, Any]:
        """C-LoRA less-forgetting flag."""
        return clo_clo_forget(less_forget=less_forget)

    def clo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """C-LoRA loop plan."""
        return clo_clo_loop_plan(phase=phase)

    def alo_init(self, *, task: str, rank: int) -> dict[str, Any]:
        """ALoRA equal-rank init."""
        return alo_alo_init(task=task, rank=rank)

    def alo_ablate(self, *, init_id: str) -> dict[str, Any]:
        """ALoRA AB-LoRA importance."""
        return alo_alo_ablate(init_id=init_id)

    def alo_prune(self, *, ablate_id: str) -> dict[str, Any]:
        """ALoRA prune and reallocate."""
        return alo_alo_prune(ablate_id=ablate_id)

    def alo_score(self, *, prune_id: str, score: int) -> dict[str, Any]:
        """ALoRA score."""
        return alo_alo_score(prune_id=prune_id, score=score)

    def alo_realloc(self, *, dynamic: bool) -> dict[str, Any]:
        """ALoRA dynamic-realloc flag."""
        return alo_alo_realloc(dynamic=dynamic)

    def alo_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """ALoRA loop plan."""
        return alo_alo_loop_plan(phase=phase)

    def lnt_attn(self, *, task: str) -> dict[str, Any]:
        """LN Tuning attention LN select."""
        return lnt_lnt_attn(task=task)

    def lnt_scale(self, *, attn_id: str) -> dict[str, Any]:
        """LN Tuning scale (gamma)."""
        return lnt_lnt_scale(attn_id=attn_id)

    def lnt_train(self, *, scale_id: str) -> dict[str, Any]:
        """LN Tuning train."""
        return lnt_lnt_train(scale_id=scale_id)

    def lnt_score(self, *, train_id: str, score: int) -> dict[str, Any]:
        """LN Tuning score."""
        return lnt_lnt_score(train_id=train_id, score=score)

    def lnt_cheap(self, *, cheaper_than_lora: bool) -> dict[str, Any]:
        """LN Tuning cheaper-than-LoRA flag."""
        return lnt_lnt_cheap(cheaper_than_lora=cheaper_than_lora)

    def lnt_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LN Tuning loop plan."""
        return lnt_lnt_loop_plan(phase=phase)

    def lfu_split(self, *, task: str) -> dict[str, Any]:
        """LoRAFusion graph split."""
        return lfu_lfu_split(task=task)

    def lfu_fuse(self, *, split_id: str) -> dict[str, Any]:
        """LoRAFusion kernel fuse."""
        return lfu_lfu_fuse(split_id=split_id)

    def lfu_batch(self, *, fuse_id: str, jobs: int) -> dict[str, Any]:
        """LoRAFusion multi-job batch."""
        return lfu_lfu_batch(fuse_id=fuse_id, jobs=jobs)

    def lfu_score(self, *, batch_id: str, score: int) -> dict[str, Any]:
        """LoRAFusion score."""
        return lfu_lfu_score(batch_id=batch_id, score=score)

    def lfu_speed(self, *, faster_than_mlora: bool) -> dict[str, Any]:
        """LoRAFusion faster-than-mLoRA flag."""
        return lfu_lfu_speed(faster_than_mlora=faster_than_mlora)

    def lfu_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRAFusion loop plan."""
        return lfu_lfu_loop_plan(phase=phase)

    def ter_tucker(self, *, task: str, order: int) -> dict[str, Any]:
        """TeRA tensorize ΔW."""
        return ter_ter_tucker(task=task, order=order)

    def ter_freeze(self, *, tucker_id: str) -> dict[str, Any]:
        """TeRA freeze random factors."""
        return ter_ter_freeze(tucker_id=tucker_id)

    def ter_scale(self, *, freeze_id: str) -> dict[str, Any]:
        """TeRA per-layer scale vectors."""
        return ter_ter_scale(freeze_id=freeze_id)

    def ter_score(self, *, scale_id: str, score: int) -> dict[str, Any]:
        """TeRA score."""
        return ter_ter_score(scale_id=scale_id, score=score)

    def ter_highrank(self, *, high_rank_cheap: bool) -> dict[str, Any]:
        """TeRA high-rank-cheap flag."""
        return ter_ter_highrank(high_rank_cheap=high_rank_cheap)

    def ter_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """TeRA loop plan."""
        return ter_ter_loop_plan(phase=phase)

    def tnl_stack(self, *, task: str) -> dict[str, Any]:
        """TensLoRA stack LoRA updates."""
        return tnl_tnl_stack(task=task)

    def tnl_tucker(self, *, stack_id: str, ranks: int) -> dict[str, Any]:
        """TensLoRA Tucker factor."""
        return tnl_tnl_tucker(stack_id=stack_id, ranks=ranks)

    def tnl_mode(self, *, tucker_id: str) -> dict[str, Any]:
        """TensLoRA per-mode ranks."""
        return tnl_tnl_mode(tucker_id=tucker_id)

    def tnl_score(self, *, mode_id: str, score: int) -> dict[str, Any]:
        """TensLoRA score."""
        return tnl_tnl_score(mode_id=mode_id, score=score)

    def tnl_budget(self, *, mode_specific: bool) -> dict[str, Any]:
        """TensLoRA mode-specific budget flag."""
        return tnl_tnl_budget(mode_specific=mode_specific)

    def tnl_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """TensLoRA loop plan."""
        return tnl_tnl_loop_plan(phase=phase)

    def azt_tt(self, *, task: str, cores: int) -> dict[str, Any]:
        """AdaZeta tensor-train adapter."""
        return azt_azt_tt(task=task, cores=cores)

    def azt_ff(self, *, tt_id: str) -> dict[str, Any]:
        """AdaZeta fast-forward contraction."""
        return azt_azt_ff(tt_id=tt_id)

    def azt_query(self, *, ff_id: str) -> dict[str, Any]:
        """AdaZeta adaptive ZO queries."""
        return azt_azt_query(ff_id=ff_id)

    def azt_score(self, *, query_id: str, score: int) -> dict[str, Any]:
        """AdaZeta score."""
        return azt_azt_score(query_id=query_id, score=score)

    def azt_mem(self, *, zo_memory: bool) -> dict[str, Any]:
        """AdaZeta ZO-memory flag."""
        return azt_azt_mem(zo_memory=zo_memory)

    def azt_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """AdaZeta loop plan."""
        return azt_azt_loop_plan(phase=phase)

    def fct_tensor(self, *, task: str) -> dict[str, Any]:
        """FacT 3D increment tensor."""
        return fct_fct_tensor(task=task)

    def fct_tt(self, *, tensor_id: str) -> dict[str, Any]:
        """FacT Tensor-Train factors."""
        return fct_fct_tt(tensor_id=tensor_id)

    def fct_tucker(self, *, tt_id: str) -> dict[str, Any]:
        """FacT Tucker factors."""
        return fct_fct_tucker(tt_id=tt_id)

    def fct_score(self, *, tucker_id: str, score: int) -> dict[str, Any]:
        """FacT score."""
        return fct_fct_score(tucker_id=tucker_id, score=score)

    def fct_tiny(self, *, tiny_params: bool) -> dict[str, Any]:
        """FacT tiny-params flag."""
        return fct_fct_tiny(tiny_params=tiny_params)

    def fct_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """FacT loop plan."""
        return fct_fct_loop_plan(phase=phase)

    def ltr_stack(self, *, task: str, layers: int) -> dict[str, Any]:
        """LoTR stack Q/V across depth."""
        return ltr_ltr_stack(task=task, layers=layers)

    def ltr_core(self, *, stack_id: str) -> dict[str, Any]:
        """LoTR shared core tensor."""
        return ltr_ltr_core(stack_id=stack_id)

    def ltr_share(self, *, core_id: str) -> dict[str, Any]:
        """LoTR share left/right factors."""
        return ltr_ltr_share(core_id=core_id)

    def ltr_score(self, *, share_id: str, score: int) -> dict[str, Any]:
        """LoTR score."""
        return ltr_ltr_score(share_id=share_id, score=score)

    def ltr_deep(self, *, better_for_deep: bool) -> dict[str, Any]:
        """LoTR better-for-deep flag."""
        return ltr_ltr_deep(better_for_deep=better_for_deep)

    def ltr_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoTR loop plan."""
        return ltr_ltr_loop_plan(phase=phase)

    def cra_mha(self, *, task: str) -> dict[str, Any]:
        """CaRA MHA tensor."""
        return cra_cra_mha(task=task)

    def cra_ffn(self, *, mha_id: str) -> dict[str, Any]:
        """CaRA FFN tensor."""
        return cra_cra_ffn(mha_id=mha_id)

    def cra_cpd(self, *, ffn_id: str) -> dict[str, Any]:
        """CaRA CP decompose."""
        return cra_cra_cpd(ffn_id=ffn_id)

    def cra_score(self, *, cpd_id: str, score: int) -> dict[str, Any]:
        """CaRA score."""
        return cra_cra_score(cpd_id=cpd_id, score=score)

    def cra_heads(self, *, head_mode: bool) -> dict[str, Any]:
        """CaRA head-mode flag."""
        return cra_cra_heads(head_mode=head_mode)

    def cra_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """CaRA loop plan."""
        return cra_cra_loop_plan(phase=phase)

    def ltt_adp(self, *, task: str) -> dict[str, Any]:
        """LoRETTA adapter branch."""
        return ltt_ltt_adp(task=task)

    def ltt_rep(self, *, adp_id: str) -> dict[str, Any]:
        """LoRETTA reparam branch."""
        return ltt_ltt_rep(adp_id=adp_id)

    def ltt_tt(self, *, rep_id: str) -> dict[str, Any]:
        """LoRETTA tensor-train cores."""
        return ltt_ltt_tt(rep_id=rep_id)

    def ltt_score(self, *, tt_id: str, score: int) -> dict[str, Any]:
        """LoRETTA score."""
        return ltt_ltt_score(tt_id=tt_id, score=score)

    def ltt_tiny(self, *, sub_mb: bool) -> dict[str, Any]:
        """LoRETTA sub-MB flag."""
        return ltt_ltt_tiny(sub_mb=sub_mb)

    def ltt_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """LoRETTA loop plan."""
        return ltt_ltt_loop_plan(phase=phase)

    def c3a_kernel(self, *, task: str) -> dict[str, Any]:
        """C3A convolution kernel."""
        return c3a_c3a_kernel(task=task)

    def c3a_circ(self, *, kernel_id: str) -> dict[str, Any]:
        """C3A circulant lift."""
        return c3a_c3a_circ(kernel_id=kernel_id)

    def c3a_fft(self, *, circ_id: str) -> dict[str, Any]:
        """C3A FFT multiply."""
        return c3a_c3a_fft(circ_id=circ_id)

    def c3a_score(self, *, fft_id: str, score: int) -> dict[str, Any]:
        """C3A score."""
        return c3a_c3a_score(fft_id=fft_id, score=score)

    def c3a_rank(self, *, high_rank: bool) -> dict[str, Any]:
        """C3A high-rank flag."""
        return c3a_c3a_rank(high_rank=high_rank)

    def c3a_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """C3A loop plan."""
        return c3a_c3a_loop_plan(phase=phase)

    def bof_block(self, *, task: str) -> dict[str, Any]:
        """BOFT butterfly block."""
        return bof_bof_block(task=task)

    def bof_orth(self, *, block_id: str) -> dict[str, Any]:
        """BOFT orthogonal factor."""
        return bof_bof_orth(block_id=block_id)

    def bof_butter(self, *, orth_id: str) -> dict[str, Any]:
        """BOFT butterfly factorize."""
        return bof_bof_butter(orth_id=orth_id)

    def bof_score(self, *, butter_id: str, score: int) -> dict[str, Any]:
        """BOFT score."""
        return bof_bof_score(butter_id=butter_id, score=score)

    def bof_full(self, *, full_rank: bool) -> dict[str, Any]:
        """BOFT full-orthogonal flag."""
        return bof_bof_full(full_rank=full_rank)

    def bof_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """BOFT loop plan."""
        return bof_bof_loop_plan(phase=phase)

    def sdt_dim(self, *, task: str) -> dict[str, Any]:
        """SDT sparse SSM dimension."""
        return sdt_sdt_dim(task=task)

    def sdt_mask(self, *, dim_id: str) -> dict[str, Any]:
        """SDT sparse mask."""
        return sdt_sdt_mask(dim_id=dim_id)

    def sdt_tune(self, *, mask_id: str) -> dict[str, Any]:
        """SDT sparse dimension tune."""
        return sdt_sdt_tune(mask_id=mask_id)

    def sdt_score(self, *, tune_id: str, score: int) -> dict[str, Any]:
        """SDT score."""
        return sdt_sdt_score(tune_id=tune_id, score=score)

    def sdt_ssm(self, *, ssm_only: bool) -> dict[str, Any]:
        """SDT SSM-targeted flag."""
        return sdt_sdt_ssm(ssm_only=ssm_only)

    def sdt_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """SDT loop plan."""
        return sdt_sdt_loop_plan(phase=phase)

    def mef_adapt(self, *, task: str) -> dict[str, Any]:
        """MEFT sparse adapter."""
        return mef_mef_adapt(task=task)

    def mef_route(self, *, adapt_id: str) -> dict[str, Any]:
        """MEFT MoE / key-expert router."""
        return mef_mef_route(adapt_id=adapt_id)

    def mef_fetch(self, *, route_id: str) -> dict[str, Any]:
        """MEFT sparse neuron fetch."""
        return mef_mef_fetch(route_id=route_id)

    def mef_score(self, *, fetch_id: str, score: int) -> dict[str, Any]:
        """MEFT score."""
        return mef_mef_score(fetch_id=fetch_id, score=score)

    def mef_cpu(self, *, cpu_offload: bool) -> dict[str, Any]:
        """MEFT CPU-offload flag."""
        return mef_mef_cpu(cpu_offload=cpu_offload)

    def mef_loop_plan(self, *, phase: str) -> dict[str, Any]:
        """MEFT loop plan."""
        return mef_mef_loop_plan(phase=phase)

    def non_revival_probe(
        self,
        *,
        consumer_scope: str,
        forbidden_ids: Sequence[str],
        probe_query: str = "",
    ) -> dict[str, Any]:
        """Assert revoked/withdrawn IDs do not surface in SEARCH."""
        hits = self.search(probe_query or "a", consumer_scope=consumer_scope, budget=2000)
        return repair_non_revival_probe(
            list(self.store.iter_entries()),
            hits,
            forbidden_ids=list(forbidden_ids),
        )

    def fact_interface(
        self, entry_ids: Sequence[str] | None = None
    ) -> dict[str, Any]:
        """MemIR-shaped evidence/claim/decision fact interface."""
        return project_fact_interface(
            list(self.store.iter_entries()),
            entry_ids=list(entry_ids) if entry_ids is not None else None,
        )

    def role_collapse_scan(self, *, limit: int = 50) -> dict[str, Any]:
        """Report provenance-role collapse suspects (MemIR-shaped)."""
        return role_collapse_scan(list(self.store.iter_entries()), limit=limit)

    def quality_gate(
        self,
        hits: Sequence[Mapping[str, Any]],
        *,
        min_hits: int = 1,
        require_claim: bool = True,
    ) -> dict[str, Any]:
        """D-Mem-shaped quality gate over search hits."""
        return roles_quality_gate(
            list(hits), min_hits=min_hits, require_claim=require_claim
        )

    def dual_channel_search(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        D-Mem / MemWeaver-shaped dual channel: routine (claims_only) + deliberation.

        Deliberation includes contested and all roles; quality_gate decides escalate.
        """
        routine = self.search(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            claims_only=True,
            **{k: v for k, v in kwargs.items() if k not in {"include_contested", "claims_only"}},
        )
        gate = self.quality_gate(routine)
        deliberation: list[dict[str, Any]] = []
        if gate.get("escalate_deliberation"):
            deliberation = self.search(
                query,
                consumer_scope=consumer_scope,
                budget=budget,
                include_contested=True,
                claims_only=False,
                **{k: v for k, v in kwargs.items() if k not in {"include_contested", "claims_only"}},
            )
        return {
            "routine": routine,
            "deliberation": deliberation,
            "quality_gate": gate,
            "channel_used": "deliberation" if deliberation else "routine",
            "fact_interface": self.fact_interface(
                [str(h.get("id")) for h in (deliberation or routine)]
            ),
            "note": "dual-channel Select — routine claims-only; deliberation on escalate",
        }

    def commit_view(
        self,
        message: str,
        *,
        entry_ids: Sequence[str],
        actor: str,
        ts: str | None = None,
        branch: str = "main",
        parent: str | None = None,
        score: float | None = None,
        outcome: str | None = None,
    ) -> dict[str, Any]:
        """GitOfThoughts-shaped commit of a memory view (stdlib; no git)."""
        ts = require_ts(ts or self._now)
        head = self.journal_chain_head().get("head")
        return ver_commit_view(
            self.store.root,
            message=message,
            actor=actor,
            ts=ts,
            entry_ids=list(entry_ids),
            journal_head=head,
            parent=parent,
            branch=branch,
            score=score,
            outcome=outcome,
        )

    def checkout_view(self, commit_hash: str) -> dict[str, Any]:
        """Replay entry-id set bound to a commit."""
        return ver_checkout_view(self.store.root, commit_hash)

    def diff_commits(self, a: str, b: str) -> dict[str, Any]:
        """Entry-set diff between two commits."""
        return ver_diff_commits(self.store.root, a, b)

    def merge_branches(
        self,
        ours: str,
        theirs: str,
        *,
        actor: str,
        ts: str | None = None,
        into_branch: str = "main",
    ) -> dict[str, Any]:
        """Union-merge two branch tips into a new commit."""
        ts = require_ts(ts or self._now)
        return ver_merge_refs(
            self.store.root,
            ours,
            theirs,
            into_branch=into_branch,
            actor=actor,
            ts=ts,
        )

    def list_commits(
        self, *, limit: int = 50, branch: str | None = None
    ) -> list[dict[str, Any]]:
        """Newest-first commit log."""
        return ver_list_commits(self.store.root, limit=limit, branch=branch)

    def verify_commit_chain(self) -> dict[str, Any]:
        """Verify GitOfThoughts-shaped commit hash chain."""
        return ver_verify_commit_chain(self.store.root)

    def tag_commit(
        self, tag: str, commit_hash: str, *, actor: str, ts: str | None = None
    ) -> dict[str, Any]:
        """Tag a commit (success/failed/custom)."""
        ts = require_ts(ts or self._now)
        return ver_tag_commit(
            self.store.root, tag, commit_hash, actor=actor, ts=ts
        )

    def copyability_gate(
        self,
        query: str,
        *,
        consumer_scope: str,
        threshold: float = 0.8,
        budget: int = 400,
    ) -> dict[str, Any]:
        """
        GitOfThoughts copyability threshold gate over SEARCH hits.

        Below τ≈0.8 → memory_likely_helps=False (accuracy parity warning).
        """
        hits = self.search(query, consumer_scope=consumer_scope, budget=budget)
        entries = []
        for h in hits:
            e = self.store.read_entry(str(h.get("id") or ""))
            if e:
                entries.append(e)
        gate = ver_copyability_gate(query, entries, threshold=threshold)
        gate["hit_count"] = len(hits)
        return gate

    def pin_memory_version(
        self,
        label: str,
        *,
        actor: str,
        ts: str | None = None,
        states: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """
        ChronoMem-shaped whole-memory version: commit all entries in states
        (default promoted) as a named tagged view.
        """
        ts = require_ts(ts or self._now)
        want = set(states or ["promoted"])
        ids = [
            e["id"]
            for e in self.store.iter_entries()
            if e.get("state") in want
        ]
        if not ids:
            raise SchemaError("pin_memory_version requires at least one entry in states")
        result = self.commit_view(
            f"version:{label}",
            entry_ids=ids,
            actor=actor,
            ts=ts,
            branch="versions",
            outcome=None,
        )
        self.tag_commit(label, result["commit"]["commit_hash"], actor=actor, ts=ts)
        result["label"] = label
        result["note"] = "ChronoMem-shaped global memory version pin"
        return result

    def activate_version(self, commit_hash: str | None) -> dict[str, Any]:
        """Set or clear ChronoMem read HEAD (None clears to live SoT)."""
        return ver_set_read_head(self.store.root, commit_hash)

    def active_version(self) -> dict[str, Any]:
        """Report current read HEAD overlay."""
        head = ver_get_read_head(self.store.root)
        if not head:
            return {"read_head": None, "live": True}
        return {
            "read_head": head,
            "live": False,
            "view": ver_checkout_view(self.store.root, head),
        }

    def counterfactual_search(
        self,
        query: str,
        *,
        consumer_scope: str,
        version_commit: str,
        budget: int = 400,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Search as-if at a prior version without mutating read_head (post-exposure probe).
        """
        hits = self.search(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            version_commit=version_commit,
            respect_read_head=False,
            **kwargs,
        )
        return {
            "version_commit": version_commit,
            "hits": hits,
            "count": len(hits),
            "note": "counterfactual Select — future updates excluded from view",
        }

    def stale_fact_scan(self, *, limit: int = 50) -> dict[str, Any]:
        """MemStrata-shaped scan of superseded-but-still-promoted exposure."""
        return strata_stale_fact_scan(list(self.store.iter_entries()), limit=limit)

    def propose_update(self, candidate: Mapping[str, Any]) -> dict[str, Any]:
        """TARL-shaped classify only — no SoT mutation."""
        return tarl_classify_update(candidate, list(self.store.iter_entries()))

    def apply_update(
        self,
        candidate: Mapping[str, Any],
        *,
        actor: str,
        ts: str | None = None,
        action: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute a TARL action (or classify then execute).

        append → ADD quarantined · noop → no write · revise → SUPERSEDE ·
        defer_verify → ADD quarantined · reject_conflict → ADD then revoke.
        """
        ts = require_ts(ts or self._now)
        plan = self.propose_update(candidate)
        if action is not None:
            if action not in TARL_ACTIONS:
                raise SchemaError(f"action must be one of {sorted(TARL_ACTIONS)}")
            plan = {
                **plan,
                "action": action,
                "reasons": list(plan.get("reasons") or []) + ["forced"],
                "note": "forced action override",
            }
        act = str(plan.get("action") or "")
        if act not in TARL_ACTIONS:
            raise SchemaError(f"action must be one of {sorted(TARL_ACTIONS)}")

        if act == "noop":
            return {
                "action": "noop",
                "plan": plan,
                "id": plan.get("target_id"),
                "state": None,
                "note": "no SoT mutation",
            }
        if act == "append" or act == "defer_verify":
            added = self.add(candidate, actor=actor, ts=ts)
            return {
                "action": act,
                "plan": plan,
                "id": added["id"],
                "state": added["state"],
                "ledger": "pending",
            }
        if act == "revise":
            target = plan.get("target_id")
            if not target:
                # classify under forced revise without target → append
                added = self.add(candidate, actor=actor, ts=ts)
                return {
                    "action": "append",
                    "plan": plan,
                    "id": added["id"],
                    "state": added["state"],
                    "ledger": "pending",
                    "note": "revise without target fell back to append",
                }
            result = self.supersede(str(target), candidate, actor=actor, ts=ts)
            return {
                "action": "revise",
                "plan": plan,
                "id": result["new_id"],
                "old_id": result["old_id"],
                "state": result["new_state"],
                "ledger": "pending",
            }
        # reject_conflict — preserve provenance on rejected ledger
        added = self.add(candidate, actor=actor, ts=ts)
        with self.store:
            entry = self.store.read_entry(added["id"])
            if entry is None:
                raise SchemaError("reject write vanished")
            entry["state"] = "revoked"
            entry["temporal"]["revoked_at"] = ts
            entry["temporal"]["revoked_reason"] = "tarl_reject_conflict"
            self.store.write_entry(entry, actor=actor, ts=ts, op="TARL_REJECT")
        self.retriever.rebuild(lexical_only=True)
        return {
            "action": "reject_conflict",
            "plan": plan,
            "id": added["id"],
            "state": "revoked",
            "ledger": "rejected",
            "target_id": plan.get("target_id"),
        }

    def ledger_view(self) -> dict[str, Any]:
        """TARL accepted / pending / rejected projection."""
        return tarl_ledger_view(list(self.store.iter_entries()))

    def memory_worth(self, entry_id: str) -> dict[str, Any]:
        """Memory Worth report for one entry."""
        entry = self.store.read_entry(entry_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {entry_id}")
        return worth_memory_worth(entry)

    def low_worth_scan(
        self,
        *,
        threshold: float = 0.4,
        min_samples: int = 2,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Scan for low Memory Worth entries (suppress candidates)."""
        return worth_low_worth_scan(
            list(self.store.iter_entries()),
            threshold=threshold,
            min_samples=min_samples,
            limit=limit,
        )

    def begin_transaction(
        self,
        *,
        actor: str,
        ts: str | None = None,
        risk_tier: str = "write",
        note: str | None = None,
    ) -> dict[str, Any]:
        """MemTX-shaped open staging transaction (write ≠ commit)."""
        ts = require_ts(ts or self._now)
        return memtx_begin_transaction(
            self.store.root, actor=actor, ts=ts, risk_tier=risk_tier, note=note
        )

    def stage_write(
        self,
        txid: str,
        entry: Mapping[str, Any],
        *,
        actor: str | None = None,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """ADD as quarantined (tentative) and attach to open transaction."""
        ts = require_ts(ts or self._now)
        tx = memtx_get_transaction(self.store.root, txid)
        if tx.get("state") != "open":
            raise SchemaError(f"stage_write requires open tx, got {tx.get('state')}")
        added = self.add(entry, actor=actor, ts=ts)
        tx_row = memtx_stage_entry(self.store.root, txid, added["id"])
        return {
            "txid": txid,
            "id": added["id"],
            "state": added["state"],
            "maturity": "tentative",
            "staged_ids": tx_row.get("staged_ids"),
            "note": "MemTX stage — tentative; not action-safe until commit",
        }

    def validate_transaction(self, txid: str) -> dict[str, Any]:
        """Validate staged tentative entries before belief commit."""
        return memtx_validate_transaction(
            self.store.root, txid, list(self.store.iter_entries())
        )

    def commit_transaction(
        self,
        txid: str,
        evidence: Sequence[Mapping[str, Any]],
        *,
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """Promote all staged entries (belief commit) under one evidence set."""
        ts = require_ts(ts or self._now)
        gate = self.validate_transaction(txid)
        if not gate.get("ok"):
            raise SchemaError(f"commit blocked: {gate.get('barriers')}")
        promoted: list[str] = []
        for eid in gate.get("staged_ids") or []:
            self.promote(str(eid), evidence, actor=actor, ts=ts)
            promoted.append(str(eid))
        row = memtx_mark_committed(
            self.store.root, txid, promoted_ids=promoted
        )
        return {
            "ok": True,
            "txid": txid,
            "promoted": promoted,
            "count": len(promoted),
            "state": row.get("state"),
            "note": "MemTX commit — beliefs now action_safe",
        }

    def abort_transaction(
        self,
        txid: str,
        *,
        actor: str,
        ts: str | None = None,
        reason: str = "abort",
    ) -> dict[str, Any]:
        """Abort open/validated tx; revoke staged tentative entries."""
        ts = require_ts(ts or self._now)
        tx = memtx_get_transaction(self.store.root, txid)
        if tx.get("state") in {"committed", "aborted"}:
            raise SchemaError(f"transaction already terminal: {tx.get('state')}")
        revoked: list[str] = []
        with self.store:
            for eid in tx.get("staged_ids") or []:
                e = self.store.read_entry(str(eid))
                if e is None:
                    continue
                if e.get("state") != "quarantined":
                    continue
                e["state"] = "revoked"
                e["temporal"] = dict(e.get("temporal") or {})
                e["temporal"]["revoked_at"] = ts
                e["temporal"]["revoked_reason"] = f"memtx_abort:{reason}"
                self.store.write_entry(e, actor=actor, ts=ts, op="TX_ABORT")
                revoked.append(str(eid))
        self.retriever.rebuild(lexical_only=True)
        row = memtx_mark_aborted(self.store.root, txid, reason=reason)
        return {
            "ok": True,
            "txid": txid,
            "revoked": revoked,
            "state": row.get("state"),
            "note": "MemTX abort — staged tentative revoked",
        }

    def action_safe_gate(
        self,
        entry_ids: Sequence[str],
        *,
        require_action_safe: bool = True,
    ) -> dict[str, Any]:
        """Gate irreversible tools on action-safe (promoted) beliefs only."""
        open_txs = memtx_list_transactions(self.store.root, state="open", limit=100)
        return memtx_action_safe_gate(
            list(self.store.iter_entries()),
            entry_ids,
            open_txs=open_txs,
            require_action_safe=require_action_safe,
        )

    def in_flight_report(self, *, limit: int = 50) -> dict[str, Any]:
        """List open transactions and tentative staged ids."""
        open_txs = memtx_list_transactions(
            self.store.root, state="open", limit=limit
        )
        staged: list[dict[str, Any]] = []
        for tx in open_txs:
            for eid in tx.get("staged_ids") or []:
                e = self.store.read_entry(str(eid))
                staged.append(
                    {
                        "txid": tx.get("txid"),
                        "id": eid,
                        "maturity": memtx_maturity_of(e) if e else "missing",
                        "conflict_key": (e or {}).get("conflict_key"),
                    }
                )
        return {
            "open_transactions": open_txs,
            "staged": staged,
            "count_open": len(open_txs),
            "count_staged": len(staged),
            "note": "MemTX in-flight — dirty reads blocked by action_safe_gate",
        }

    def aoep_report(self) -> dict[str, Any]:
        """Always-On AOEP-v0 shaped obligation coverage for this build."""
        return memtx_aoep_checklist(
            {
                "transaction_commit": True,
                "action_safe_gate": True,
                "cascade_withdraw": True,
                "version_rollback": True,
                "forget_or_worth": True,
            }
        )

    def symbolic_conflict_scan(self, *, limit: int = 50) -> dict[str, Any]:
        """LatticeMind-shaped mechanical conflict/cycle scan."""
        return lattice_symbolic_conflict_scan(
            list(self.store.iter_entries()), limit=limit
        )

    def classify_conflict(self, entry_id_a: str, entry_id_b: str) -> dict[str, Any]:
        """Credibility vs coordination classification (no LLM)."""
        a = self.store.read_entry(entry_id_a)
        b = self.store.read_entry(entry_id_b)
        if a is None or b is None:
            raise SchemaError("both entries required for classify_conflict")
        return lattice_classify_conflict(a, b)

    def compact_render(
        self,
        query: str,
        *,
        consumer_scope: str,
        reader_budget: int = 1400,
        budget: int = 400,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """SEARCH then LatticeMind compact render under reader character budget."""
        hits = self.search(
            query, consumer_scope=consumer_scope, budget=budget, **kwargs
        )
        report = lattice_compact_render(hits, reader_budget=reader_budget)
        report["query"] = query
        report["hit_count"] = len(hits)
        return report

    def stage_effect(
        self,
        *,
        sink: str,
        payload: Mapping[str, Any],
        actor: str,
        ts: str | None = None,
        txid: str | None = None,
        belief_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Cordon-shaped stage irreversible tool effect in outbox."""
        ts = require_ts(ts or self._now)
        return cordon_stage_effect(
            self.store.root,
            txid=txid,
            sink=sink,
            payload=payload,
            actor=actor,
            ts=ts,
            belief_ids=belief_ids,
        )

    def release_effects(
        self,
        *,
        txid: str | None = None,
        effect_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Mark pending effects ready after belief commit."""
        return cordon_release_effects(
            self.store.root, txid=txid, effect_ids=effect_ids
        )

    def mark_effect_dispatched(
        self, effect_id: str, *, receipt: str | None = None
    ) -> dict[str, Any]:
        return cordon_mark_dispatched(
            self.store.root, effect_id, receipt=receipt
        )

    def cancel_effect(
        self, effect_id: str, *, reason: str = "cancel"
    ) -> dict[str, Any]:
        return cordon_cancel_effect(self.store.root, effect_id, reason=reason)

    def compensate_effect(
        self, effect_id: str, *, reason: str = "compensate"
    ) -> dict[str, Any]:
        return cordon_compensate_effect(
            self.store.root, effect_id, reason=reason
        )

    def list_effects(
        self,
        *,
        state: str | None = None,
        txid: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        return cordon_list_effects(
            self.store.root, state=state, txid=txid, limit=limit
        )

    def state_resolution(
        self, *, conflict_key: str | None = None
    ) -> dict[str, Any]:
        """STALE State Resolution proxy over conflict keys."""
        return stale_state_resolution(
            list(self.store.iter_entries()), conflict_key=conflict_key
        )

    def premise_resistance(
        self, query: str, *, consumer_scope: str | None = None
    ) -> dict[str, Any]:
        """STALE Premise Resistance — refuse queries dominated by stale tokens."""
        entries = list(self.store.iter_entries())
        if consumer_scope:
            entries = [e for e in entries if e.get("scope") == consumer_scope]
        return stale_premise_resistance(query, entries)

    def ipa_gap_scan(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
    ) -> dict[str, Any]:
        """STALE IPA gap: live Select without exclude_superseded vs winners."""
        live = self.search(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            exclude_superseded=False,
        )
        return stale_ipa_gap_scan(
            list(self.store.iter_entries()),
            live_hit_ids=[str(h.get("id")) for h in live],
        )

    def verify_transition(self, old_id: str, new_id: str) -> dict[str, Any]:
        """VTA-shaped provenance/chronology verify for a supersede pair."""
        old = self.store.read_entry(old_id)
        new = self.store.read_entry(new_id)
        if old is None or new is None:
            raise SchemaError("both entries required for verify_transition")
        return stale_verify_transition(old, new)

    def related_slot_scan(self, conflict_key: str) -> dict[str, Any]:
        """Same-domain propagation candidates after a state change."""
        return stale_related_slot_scan(
            list(self.store.iter_entries()), conflict_key
        )

    def gem_report(self) -> dict[str, Any]:
        """GEM six-condition obligation coverage for this build."""
        return gem_correctness_report(
            {
                "exclude_superseded_or_winners": True,
                "verify_transition_or_tarl": True,
                "quarantine_promote": True,
                "supersede_or_revoke": True,
                "delete_or_forget_compliance": True,
                "scope_acl_or_action_safe": True,
            }
        )

    def project_resolve(self, conflict_key: str) -> dict[str, Any]:
        """StateFuse projection-time resolver — select or abstain; never mutates SoT."""
        pin = fuse_get_projection_pin(self.store.root, conflict_key)
        pinned_id = str(pin.get("chosen_id")) if pin else None
        return fuse_project_resolve(
            list(self.store.iter_entries()),
            conflict_key,
            pinned_id=pinned_id,
        )

    def correction_handle(
        self,
        *,
        claim_id: str | None = None,
        claim_ref: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """StateFuse dual correction handles (exact id + semantic ref)."""
        return fuse_correction_handle(
            list(self.store.iter_entries()),
            claim_id=claim_id,
            claim_ref=claim_ref,
            limit=limit,
        )

    def pin_projection(
        self,
        conflict_key: str,
        chosen_id: str,
        *,
        actor: str,
        ts: str | None = None,
    ) -> dict[str, Any]:
        """Pin a projection choice without rewriting SoT entries."""
        ts = require_ts(ts or self._now)
        entry = self.store.read_entry(chosen_id)
        if entry is None:
            raise SchemaError(f"unknown entry: {chosen_id}")
        if str(entry.get("conflict_key") or "") != str(conflict_key).strip():
            raise SchemaError("chosen_id conflict_key mismatch")
        return fuse_pin_projection(
            self.store.root,
            conflict_key=conflict_key,
            chosen_id=chosen_id,
            actor=actor,
            ts=ts,
        )

    def clear_projection_pin(self, conflict_key: str) -> dict[str, Any]:
        return fuse_clear_projection_pin(self.store.root, conflict_key)

    def list_projection_pins(self, *, limit: int = 50) -> dict[str, Any]:
        return fuse_list_projection_pins(self.store.root, limit=limit)

    def toki_classify_operator(
        self,
        candidate: Mapping[str, Any],
        *,
        tip_id: str | None = None,
        evidence: Sequence[Mapping[str, Any]] | None = None,
        policy_rule: str | None = None,
    ) -> dict[str, Any]:
        """TOKI-shaped classify intended write operator (does not write)."""
        tip = None
        if tip_id:
            tip = self.store.read_entry(tip_id)
            if tip is None:
                raise SchemaError(f"unknown tip: {tip_id}")
        else:
            key = str(candidate.get("conflict_key") or "").strip()
            if key:
                tip = toki_tip_for_conflict_key(
                    list(self.store.iter_entries()), key
                )
        return toki_classify_write_operator(
            tip, candidate, evidence=evidence, policy_rule=policy_rule
        )

    def toki_anomaly_scan(self, *, limit: int = 50) -> dict[str, Any]:
        """TOKI-shaped write-anomaly proxies (audit erasure / drift / replay)."""
        journal: list[dict[str, Any]] = []
        jpath = self.store.root / "journal.ndjson"
        if jpath.is_file():
            from stele_core.schema import canonical_loads as _loads

            for line in jpath.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    journal.append(_loads(line))
                except Exception:  # noqa: BLE001
                    continue
        return toki_anomaly_scan(
            list(self.store.iter_entries()), journal_rows=journal, limit=limit
        )

    def context_bid(
        self, query: str, *, slots: int = 5, now: str | None = None
    ) -> dict[str, Any]:
        """MemArchitect-shaped triage & bid for context slots (report only)."""
        ts = now or self._now
        return architect_context_bid(
            list(self.store.iter_entries()), query, slots=slots, now=ts
        )

    def rebuild_sqlite_index(self) -> dict[str, Any]:
        """Rebuild derived SQLite FTS index from file SoT (stdlib)."""
        return rebuild_sqlite_index(self.store.root, self.store.iter_entries())

    def search_sqlite(
        self,
        query: str,
        *,
        states: Sequence[str] | None = None,
        scopes: Sequence[str] | None = None,
        cue: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Query derived SQLite FTS index (empty if not rebuilt)."""
        return search_sqlite_index(
            self.store.root,
            query,
            states=states,
            scopes=scopes,
            cue=cue,
            limit=limit,
        )

    def purge_by_provenance(
        self,
        *,
        untrusted_sources: Sequence[str] | None = None,
        untrusted_agents: Sequence[str] | None = None,
        actor: str,
        ts: str | None = None,
        dry_run: bool = True,
    ) -> dict[str, Any]:
        """
        Provenance-driven recovery (PurgeBench / memorywire recover thesis).

        Entries whose provenance.source or provenance.agent matches an untrusted
        token are listed (dry_run) or hard-deleted. Does not auto-solve entangled
        poison inside trusted sources — those stay for contested/human review.
        """
        ts = require_ts(ts or self._now)
        sources = {s.strip() for s in (untrusted_sources or []) if s and s.strip()}
        agents = {a.strip() for a in (untrusted_agents or []) if a and a.strip()}
        if not sources and not agents:
            raise SchemaError("purge_by_provenance requires untrusted_sources and/or untrusted_agents")

        would: list[dict[str, Any]] = []
        for e in self.store.iter_entries():
            prov = e.get("provenance") or {}
            src = str(prov.get("source") or "")
            ag = str(prov.get("agent") or "")
            hit_src = any(tok in src or src == tok for tok in sources)
            hit_ag = any(tok == ag for tok in agents)
            if hit_src or hit_ag:
                would.append(
                    {
                        "id": e["id"],
                        "state": e["state"],
                        "source": src,
                        "agent": ag,
                        "title": e.get("title"),
                        "match": "source" if hit_src else "agent",
                    }
                )

        if dry_run:
            return {
                "dry_run": True,
                "would_purge": would,
                "count": len(would),
                "kept_note": "trusted-source entangled poison is not auto-purged",
            }

        removed: list[str] = []
        with self.store:
            for row in would:
                if self.store.delete_entry_file(
                    row["id"], actor=actor, ts=ts, reason="purge_by_provenance"
                ):
                    removed.append(row["id"])
            self.store.journal(
                "PURGE",
                entry_id=None,
                actor=actor,
                payload={"removed": removed, "sources": sorted(sources), "agents": sorted(agents)},
                ts=ts,
            )
            self.store.drop_indexes()
        self.retriever.rebuild(lexical_only=True)
        return {"dry_run": False, "removed": sorted(removed), "count": len(removed)}

    def diff_stores(self, other_root: str | Path) -> dict[str, Any]:
        """Compare this store to another root (e.g. a snapshot) by entry id sets."""
        other = SteleStore(Path(other_root), create=False)
        a = {e["id"] for e in self.store.iter_entries()}
        b = {e["id"] for e in other.iter_entries()}
        return {
            "only_here": sorted(a - b),
            "only_there": sorted(b - a),
            "both": sorted(a & b),
            "here_count": len(a),
            "there_count": len(b),
        }

    def entangled_suspects(
        self,
        *,
        seed_ids: Sequence[str] | None = None,
        untrusted_sources: Sequence[str] | None = None,
        untrusted_agents: Sequence[str] | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        Human-review queue for LINK-entangled poison (PurgeBench / memorywire).

        Seeds = explicit ids and/or live entries matching untrusted provenance.
        Suspects = remaining entries that LINK to a seed (or are linked from one)
        but do **not** themselves match the untrusted tokens — report only.
        """
        sources = {s.strip() for s in (untrusted_sources or []) if s and str(s).strip()}
        agents = {a.strip() for a in (untrusted_agents or []) if a and str(a).strip()}
        seeds: set[str] = {s for s in (seed_ids or []) if s}

        def _untrusted(e: dict[str, Any]) -> bool:
            prov = e.get("provenance") or {}
            src = str(prov.get("source") or "")
            ag = str(prov.get("agent") or "")
            hit_src = any(tok in src or src == tok for tok in sources)
            hit_ag = any(tok == ag for tok in agents)
            return hit_src or hit_ag

        for e in self.store.iter_entries():
            if _untrusted(e):
                seeds.add(e["id"])

        if not seeds:
            return {
                "seeds": [],
                "suspects": [],
                "count": 0,
                "note": "no seeds — pass seed_ids and/or untrusted_sources/agents",
            }

        by_id = {e["id"]: e for e in self.store.iter_entries()}
        suspects: list[dict[str, Any]] = []
        seen: set[str] = set()

        def _add_suspect(eid: str, via: str, seed: str) -> None:
            if eid in seeds or eid in seen or eid not in by_id:
                return
            e = by_id[eid]
            if _untrusted(e):
                return
            seen.add(eid)
            suspects.append(
                {
                    "id": eid,
                    "title": e.get("title"),
                    "state": e.get("state"),
                    "source": str((e.get("provenance") or {}).get("source") or ""),
                    "via": via,
                    "seed": seed,
                }
            )

        for seed in seeds:
            se = by_id.get(seed)
            if se is None:
                continue
            for lnk in se.get("links") or []:
                if lnk.get("kind") == "entry" and lnk.get("ref"):
                    _add_suspect(str(lnk["ref"]), "outbound_from_seed", seed)
            for other in by_id.values():
                if other["id"] == seed:
                    continue
                for lnk in other.get("links") or []:
                    if lnk.get("kind") == "entry" and lnk.get("ref") == seed:
                        _add_suspect(other["id"], "inbound_to_seed", seed)

        suspects = suspects[: max(0, int(limit))]
        return {
            "seeds": sorted(seeds),
            "suspects": suspects,
            "count": len(suspects),
            "note": "human review only — not auto-purged",
        }

    def hygiene_candidates(
        self,
        *,
        now: str | None = None,
        unused_before: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """
        MemArchitect-shaped zombie / net-harm report — **no auto-delete**.

        Reasons: net_harmful (harmful > helpful), unused_stale (no outcomes and
        last_verified before unused_before), stale_promoted (past horizon).
        """
        point = require_ts(now or self._now)
        horizon = self.retriever.staleness_horizon
        cutoff = unused_before  # ISO; optional
        rows: list[dict[str, Any]] = []
        for e in self.store.iter_entries(states={"promoted", "contested"}):
            usage = e.get("usage") or {}
            helpful = int(usage.get("helpful") or 0)
            harmful = int(usage.get("harmful") or 0)
            ignored = int(usage.get("ignored") or 0)
            reasons: list[str] = []
            if harmful > helpful:
                reasons.append("net_harmful")
            last_v = str(e["temporal"]["last_verified"])
            outcomes = helpful + harmful + ignored
            if cutoff and outcomes == 0 and last_v < cutoff:
                reasons.append("unused_stale")
            if is_stale(e, point, horizon):
                reasons.append("stale_promoted")
            if not reasons:
                continue
            rows.append(
                {
                    "id": e["id"],
                    "title": e.get("title"),
                    "state": e["state"],
                    "last_verified": last_v,
                    "helpful": helpful,
                    "harmful": harmful,
                    "reasons": reasons,
                }
            )
        rows.sort(key=lambda r: (len(r["reasons"]), r["harmful"], r["last_verified"]), reverse=True)
        rows = rows[: max(0, int(limit))]
        return {
            "candidates": rows,
            "count": len(rows),
            "as_of": point,
            "unused_before": cutoff,
            "note": "report only — operator decides purge/supersede/pin",
        }

    def injection_scan(
        self,
        *,
        entry_ids: Sequence[str] | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """
        MIND-inspired lightweight injection scan — deterministic markers, no LLM.

        Report-only. Pair with withhold_injection_suspects / block_injection_suspects
        for MAPLE-style retrieval and promote gates.
        """
        suspects: list[dict[str, Any]] = []
        id_filter = {str(i) for i in (entry_ids or []) if i} or None
        for e in self.store.iter_entries():
            if id_filter is not None and e["id"] not in id_filter:
                continue
            row = scan_entry(e)
            if row["suspect"]:
                suspects.append(row)
            if len(suspects) >= max(0, int(limit)):
                break
        return {
            "suspects": suspects,
            "count": len(suspects),
            "markers_catalog": list(INJECTION_MARKERS),
            "note": "heuristic markers only — not a neural detector (MIND thesis adapted)",
        }

    def select_budget_plan(
        self,
        query: str,
        *,
        consumer_scope: str,
        budget: int = 400,
        withhold_injection_suspects: bool = False,
        principal_scopes: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """
        Compress-plane plan: what SEARCH would inject under a token budget.

        Runs search at the given budget and at a high ceiling to count overflow.
        """
        ceiling = max(int(budget) * 20, 10_000)
        fitted = self.search(
            query,
            consumer_scope=consumer_scope,
            budget=budget,
            withhold_injection_suspects=withhold_injection_suspects,
            principal_scopes=principal_scopes,
        )
        wide = self.search(
            query,
            consumer_scope=consumer_scope,
            budget=ceiling,
            withhold_injection_suspects=withhold_injection_suspects,
            principal_scopes=principal_scopes,
        )
        fitted_ids = {s["id"] for s in fitted}
        overflow = [s["id"] for s in wide if s["id"] not in fitted_ids]
        return {
            "budget": budget,
            "fitted": [{"id": s["id"], "title": s.get("title")} for s in fitted],
            "fitted_count": len(fitted),
            "overflow_ids": overflow,
            "overflow_count": len(overflow),
            "note": "token estimate via retrieval budget — Compress plane (OP-9)",
        }

    def forget_compliance(
        self,
        *,
        consumer_scope: str,
        subject_id: str | None = None,
        entry_ids: Sequence[str] | None = None,
        probe_query: str | None = None,
        forbidden_substrings: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """
        GateMem-shaped active-forgetting probe (post DELETE).

        Asserts entry files for subject/ids are gone and SEARCH does not resurface
        forbidden substrings or deleted ids. Journal DELETE rows may remain (audit).
        """
        if not subject_id and not entry_ids and not forbidden_substrings and not probe_query:
            raise SchemaError(
                "forget_compliance needs subject_id, entry_ids, probe_query, and/or forbidden_substrings"
            )
        id_set = {str(i) for i in (entry_ids or []) if i}
        remaining: list[str] = []
        for e in self.store.iter_entries():
            if subject_id and str((e.get("provenance") or {}).get("subject_id") or "") == subject_id:
                remaining.append(e["id"])
            elif e["id"] in id_set:
                remaining.append(e["id"])

        leaks: list[dict[str, Any]] = []
        needles = [str(s) for s in (forbidden_substrings or []) if s and str(s).strip()]
        if probe_query is not None and str(probe_query).strip():
            hits = self.search(str(probe_query), consumer_scope=consumer_scope)
            for h in hits:
                if h["id"] in id_set:
                    leaks.append({"id": h["id"], "reason": "deleted_id_in_search"})
                    continue
                blob = f"{h.get('title') or ''}\n{h.get('body') or ''}".lower()
                for n in needles:
                    if n.lower() in blob:
                        leaks.append(
                            {
                                "id": h["id"],
                                "reason": "forbidden_substring",
                                "needle": n,
                            }
                        )
                        break
        elif needles:
            # Full-store body scan when no probe query (strict).
            for e in self.store.iter_entries():
                blob = f"{e.get('title') or ''}\n{e.get('body') or ''}".lower()
                for n in needles:
                    if n.lower() in blob:
                        leaks.append(
                            {
                                "id": e["id"],
                                "reason": "forbidden_substring_store",
                                "needle": n,
                            }
                        )
                        break

        return {
            "ok": len(remaining) == 0 and len(leaks) == 0,
            "store_clear": len(remaining) == 0,
            "remaining_ids": sorted(set(remaining)),
            "search_leaks": leaks,
            "note": "journal may retain DELETE audit rows; entry SoT must be empty",
        }


def _correction_slice(entry: dict[str, Any], *, kind: str) -> dict[str, Any]:
    return {
        "id": entry["id"],
        "kind": kind,
        "title": entry["title"],
        "layer": entry["layer"],
        "scope": entry["scope"],
        "last_verified": entry["temporal"]["last_verified"],
        "contested_with": list(entry.get("contested_with") or []),
        "links": list(entry.get("links") or [])[:8],
    }


def _uniq_links(a: Any, b: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for link in list(a or []) + list(b or []):
        key = f"{link.get('kind')}:{link.get('ref')}"
        if key not in seen:
            seen.add(key)
            out.append(link)
    return out
