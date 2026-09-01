# Stele — Technical Specification

**Version:** 18.15.0 · **Date:** 2026-08-28 · **Status:** Active — implements **v18.15.0** (`stele-core` + `stele-mcp` + CLI)
**Derived from:** `stele_system_intent.yaml` · `docs/PRD.md` v18.15.0 · `docs/patterns/patterns_session_ledger_memory.yaml` v1.3 · frontiers research 2026

> Constraint references (C1–C8) resolve in the intent; pattern references (FF-xx / OP-xx) in the patterns file; use cases (UC-n) in the PRD. Where this spec and the intent conflict, the intent wins, in its stated priority order: **C7 > C8 > C6 > C5 > C4 > C2 > C3 > C1**.

---

## 1. Decisions on the PRD's open questions

| # | Question | Decision |
|---|---|---|
| Q1 | Substrate for v1 SoT | **Entry-per-file JSON store + append-only ops journal** (§3). Files are the SoT (C4); SQLite enters later only as a *derived* index if scale demands it — never as truth |
| Q2 | Oracle evidence format | **Typed evidence records with local digest verification** (§5.2). Structural validation in core; no network. Self-assertions are unrepresentable as valid evidence |
| Q3 | MCP surface shape | **Named tools** (§7): one tool per operation (core six + governed helpers + living-ledger + ops). Discoverability for agents beats parameter dispatch |
| Q4 | Scope taxonomy | **Three rungs:** `universal` · `domain:<name>` · `project:<name>` (§4.3). The MTL abstraction ladder (FF-3) has more than two rungs; retrieval filters respect the hierarchy |
| Q5 | REFLECT conflict semantics | **Surface, never auto-resolve** (§5.3–5.4). Conflicting promoted entries are flagged `contested`, resolved only by evidenced `resolve_contested` |
| Q6 | Seed migration | **Migration / receipt / judgment producers** (§8.3): selected redacted payloads → quarantined ADD; never bulk private-tree import (C8) |

---

## 2. Package layout (monorepo, monorepo layout)

```
packages/
  stele-core/          # schema, store, ops, governance, retrieval, export, harness, CLI
    src/stele_core/
      schema.py        # entry model, canonical serialization, validation
      schema_json.py   # JSON Schema 2020-12 export (UC-29)
      store.py         # file SoT + journal + locking + attachments
      ops.py           # public Stele façade (six ops + helpers + doctor/snapshot)
      governance.py    # quarantine → promote; contested resolve; evidence validation
      distill.py       # ADD distill gate (FF-2)
      retrieval.py     # hybrid search, filters, budgeter, link follow
      integrity.py     # verify_store
      harness.py       # task-outcome eval (OP-12 / success_oracle)
      export.py        # pack builder, redaction, hydrate, verify_pack
      adapters.py      # Embedder, OracleAdapter, SearchBackend; project_receipt;
                       # migration_entry; judgment_entry; memorywire projection
      cli.py           # `stele` operator CLI (UC-28)
      index/           # derived: lexical (BM25), semantic (callable), temporal
    tests/
  stele-mcp/           # MCP server wrapping stele-core (stdio transport)
    src/stele_mcp/server.py
    tests/
docs/
  schemas/entry.schema.json
  ARCHITECTURE.md
examples/
  lifecycle_demo.py
  proof_run.py
```

- `stele-core`: **zero runtime dependencies** (stdlib only), zero network, zero LLM on the write path (C5, C1). Python 3.11–3.13.
- `stele-mcp`: depends on `stele-core` + an MCP server library only.
- stele-core is stdlib-only (C1; `test_purity.py`).
- **Permanent boundary (intent R4):** under-distillation → stronger oracle/distill gates — never LLM extraction in core.

---

## 3. Storage layer (SoT — C4, C5)

### 3.1 On-disk layout

```
<store_root>/
  stele.json                # store manifest: schema_version, store_id, created_at
  journal.ndjson            # append-only op log: {op, entry_id, actor, ts, payload_digest}
  entries/
    quarantine/<id>.json
    promoted/<id>.json      # also holds superseded / expired / contested
  attachments/<digest>      # content-addressed blobs (UC-24)
  index/                    # DERIVED, rebuildable, deletable (C4)
    lexical/  semantic/  temporal/
```

`journal.ndjson` is the audit trail for PRD §8 governance integrity. `timeline(entry_id)` reads it (UC-24).

### 3.2 Determinism and identity

- **Canonical serialization:** JSON, UTF-8, sorted keys, `\n` endings — byte-stable.
- **Entry id:** `se_<first 16 hex of sha256(canonical entry minus id/state/evidence)>`.
- **Timestamps:** caller-supplied ISO-8601 (store never reads the clock).

### 3.3 Concurrency (PRD P9, risk R2)

- Advisory lock (`.lock`, `O_EXCL`) + atomic `rename()`.
- Multi-agent: one MCP server per store serializes writes.
- Logical conflicts surface at REFLECT / contested resolve — not via lock.

### 3.4 Erasure (C6, UC-5)

`DELETE(subject_id | entry_id)` → journal tombstone → remove file → drop+rebuild indexes. Differential joint test asserts zero residual retrieval.

### 3.5 Integrity (UC-21)

`verify()` / `verify_store`: manifest present, no dual quarantine+promoted id, schema-valid entries, journal parseable. Read-only.

---

## 4. Entry schema (C6)

### 4.1 Fields

| Field | Type | Req | Notes |
|---|---|---|---|
| `id` | string | ✓ | content-derived (§3.2) |
| `schema_version` | int | ✓ | migrations gate |
| `layer` | enum | ✓ | `goal · issue · decision · failure_lesson · workflow · skill_artifact` |
| `title` | string | ✓ | one line |
| `body` | string | ✓ | distilled Insight — distill gate rejects transcripts/tool dumps (FF-2) |
| `rejected_options` | list | issue/decision | IBIS; FF-7 |
| `scope` | string | ✓ | `universal` \| `domain:<name>` \| `project:<name>` |
| `env_assumptions` | list | workflow/skill | required non-empty (FF-4) |
| `temporal` | object | ✓ | `valid_from`, `last_verified`, `expiry?`, `superseded_by?`, `superseded_at?` |
| `provenance` | object | ✓ | `agent`, `task`, `environment`, `subject_id`, `source`, `written_at` |
| `provenance.model_id` | string | — | model-swap re-verify (UC-16; P13) |
| `assessment.domain_depth` | enum | — | `expert · practitioner · adjacent · novice` |
| `receipt_projection` | object | — | C8 adapter mapping only |
| `evidence` | list | promoted | typed records (§5.2) |
| `links` | list | — | `{kind: artifact\|test\|entry\|source, ref, digest?}` |
| `contested_with` | list[str] | contested | peer entry ids |
| `usage` | object | — | `{helpful, harmful, ignored, pinned, last_outcome?, last_outcome_at?}` (UC-18/19) |
| `state` | enum | ✓ | `quarantined · promoted · superseded · expired · contested` |

### 4.2 State machine (governance — C7)

```
            promote(evidence)                supersede(new)
quarantined ─────────────────▶ promoted ───────────────────▶ superseded
     │                            │  ▲
     │ delete / expire            │  │ resolve_contested(evidence)
     ▼                            ▼  │
  (removed)                    contested   (expiry → expired; point-in-time readable)
```

Default SEARCH: promoted only. Contested only with `include_contested=true`. Expired/superseded only via `as_of` and always `historical: true`.

### 4.3 Scope filter semantics (Q4, UC-7)

Consumer context: `project:<p>` + optional `consumer_domain=domain:<d>`. Serves: exact project ∪ matching domain ∪ `universal`. Cross-project requires `scope_override`.

### 4.4 operator receipt adapter (C8, UC-25)

`project_receipt(redacted_dict)` → ADD payload. Preserves expected / detection / diagnosis / change / outcome / trace. Rejects private-source substrings. Code-fix → promote requires `test_result` + exit 0.

### 4.5 Judgment + migration producers (UC-26, Q6)

- `judgment_entry(wire_dict)` → decision/failure_lesson/issue ADD (`agent` default `judgment-adapter`). No `import foreign frameworks`.
- `migration_entry(raw, …)` → `provenance.agent="migration"`, redacted source pointer.

---

## 5. Governance (C7)

### 5.1 Quarantine → promote (UC-2)

1. Validate evidence records (§5.2).
2. Verify local attachment digests when present (stdlib hash — C5).
3. Reject self-issued evidence (`issuer == provenance.agent`).
4. Reject when `actor == provenance.agent` (writer cannot promote own claim — C8).
5. Code-fix / `receipt_projection.code_regression` → require `test_result` + `exit_status=0`.
6. Atomic move quarantine → promoted; journal `PROMOTE`.

### 5.2 Evidence record (Q2)

```json
{
  "type": "test_result | env_feedback | independent_judge | human_signoff",
  "issuer": "<must not equal provenance.agent unless human_signoff>",
  "ref": "<path or URI>",
  "digest": "<sha256 when local>",
  "observed_at": "<ISO-8601>",
  "verdict": "supports | refutes | mixed"
}
```

`test_result` also: `command`, `exit_status`. **OracleAdapter** protocol: external process emits records; core validates only.

### 5.3 REFLECT (UC-6)

Batched over promoted (+ contested for conflict scan):
- **expire:** `expiry` passed or `stale_before` / horizon on `last_verified`.
- **conflict:** near-duplicate titles + contradictory verdicts → both `contested` + `contested_with`.
- **merge:** agreeing near-duplicates → keep one, provenance links, supersede other.
- **dangling_links:** `kind=entry` refs missing from store.

Output: `ReflectReport{merged[], expired[], conflicts[], dangling_links[]}`.

### 5.4 Contested resolve (UC-13, Q5)

`list_contested()` · `resolve_contested(winner_id, loser_id, evidence, actor)`:
- Evidenced supersede; winner → promoted (evidence appended); loser → superseded.
- Actor cannot be either entry's writing agent (no self-resolve).
- **No auto-merge path.**

---

## 6. Retrieval (C2)

### 6.1 Pipeline

```
search(query, consumer_scope, budget, …) →
  1. empty query → ∅ (C2 / OP-9)
  2. candidates: BM25 ∪ optional Embedder (RRF fuse)
  3. optional prefer_helpful / pin re-rank (UC-18/19)
  4. hard filters: state · scope/domain/override · temporal · as_of
  5. stale_policy flag|withhold (UC-15)
  6. consumer_env → env_mismatch / missing_env_assumptions (UC-14)
  7. consumer_model_id + model_policy flag|withhold (UC-16)
  8. body_max_chars compress + match_reasons (UC-20)
  9. follow_links + follow_link_depth 1..3 within budget (UC-22)
  10. budgeter: greedy whole slices
  → slices[] | ∅
```

Slice fields (indicative): `id, title, body, body_truncated, layer, scope, state, links, provenance, env_*, model_mismatch, stale, historical, contested, via_link, linked_from?, usage, match_reasons`.

### 6.2 External retrieval-router integration (UC-10)

`SearchBackend` protocol — pure function of store + query + filters. Adapter lives router-side.

### 6.3 Living-ledger helpers (UC-15/16/18/19/21)

| API | Behavior |
|---|---|
| `record_outcome(id, helpful\|harmful\|ignored)` | bumps usage; helpful refreshes `last_verified` |
| `pin(id, pinned=bool)` | SEARCH priority |
| `stale_report(now?)` | promoted past horizon |
| `reverify(ids, evidence)` | append evidence + refresh `last_verified` |
| `related(id)` | inbound/outbound LINK neighborhood |

---

## 7. MCP surface (`stele-mcp`, Q3, UC-27)

Stdio transport; one server per store (`STELE_STORE`, optional `STELE_STORE_ID`, `STELE_NOW`); serializes writes (§3.3).

### 7.1 Core six (+ promote)

| Tool | Compiles to | Notes | PRD |
|---|---|---|---|
| `stele_add` | ADD | `entry_json`; distill+schema gate | UC-1 |
| `stele_update` | UPDATE | non-state fields | — |
| `stele_promote` | governed UPDATE | `evidence_json` + distinct `actor` | UC-2 |
| `stele_supersede` | SUPERSEDE | old id + new entry JSON | UC-4 |
| `stele_delete` | DELETE | `entry_id` and/or `subject_id` | UC-5 |
| `stele_search` | SEARCH | see §7.2 params | UC-3,14–16,20,22 |
| `stele_reflect` | REFLECT | optional `stale_before` | UC-6 |
| `stele_link` | LINK | `kind` + `ref` + optional `digest` | UC-8 |

### 7.2 `stele_search` parameters

| Param | Default | Role |
|---|---|---|
| `query` | required | empty → `[]` |
| `consumer_scope` | required | project/domain/universal filter |
| `budget` | 400 | token budget (word estimate) |
| `as_of` | null | point-in-time / historical |
| `include_contested` | false | serve contested |
| `consumer_env_json` | null | FF-4 env gate |
| `consumer_domain` | null | unlock `domain:<name>` |
| `stale_policy` | `flag` | `flag` \| `withhold` |
| `consumer_model_id` | null | model mismatch |
| `model_policy` | `flag` | `flag` \| `withhold` |
| `follow_links` | false | expand `kind=entry` |
| `follow_link_depth` | 1 | 1..3 hops |
| `body_max_chars` | null | compress slice body |
| `prefer_helpful` | true | pin/helpful ranking |

### 7.3 Contested + export/hydrate

| Tool | Notes | PRD |
|---|---|---|
| `stele_list_contested` | open conflict queue | UC-13 |
| `stele_resolve_contested` | evidenced supersede | UC-13 |
| `stele_export` | redacted pack; audience + expiry | UC-11 |
| `stele_hydrate` | import pack; optional promote + evidence | UC-17 |
| `stele_verify_pack` | offline stamps + secret scan | UC-11,21 |

### 7.4 Living ledger + ops

| Tool | Notes | PRD |
|---|---|---|
| `stele_record_outcome` | helpful / harmful / ignored | UC-18 |
| `stele_pin` | pin/unpin promoted | UC-19 |
| `stele_stale_report` | batch freshness list | UC-15,21 |
| `stele_reverify` | batch `last_verified` refresh | UC-16,21 |
| `stele_related` | LINK neighborhood | UC-22 |
| `stele_verify` | store integrity | UC-21 |
| `stele_reviewer_corrections` | bounded contested-first slice | UC-23 |
| `stele_stats` | counts by state/layer/scope | UC-24 |
| `stele_timeline` | journal history for one entry | UC-24 |
| `stele_attach` | base64 bytes → content-addressed digest; optional LINK | UC-24 |
| `stele_snapshot` | cold-copy SoT to dest | UC-30 |
| `stele_doctor` | verify + stats + contested + stale | UC-32 |
| `stele_entry_schema` | JSON Schema 2020-12 | UC-29 |

Library helpers (also CLI where noted): harness runners (`memory_arena_smoke`, `foreign_pack_transfer_eval`, `measure_search_overhead`), producers (`project_receipt`, `judgment_entry`, `migration_entry`), interop (`to_memorywire_remember`, `from_memorywire_recall_hits`).

### 7.5 Operator CLI (`stele`, UC-28)

Entry point: `stele` → `stele_core.cli:main`.

| Command | Behavior |
|---|---|
| `stele init STORE` | create empty store |
| `stele schema [--out FILE]` | emit entry JSON Schema |
| `stele verify STORE` | integrity |
| `stele doctor STORE` | UC-32 report |
| `stele stats STORE` | counts |
| `stele snapshot STORE DEST` | UC-30 |
| `stele search …` | promoted search |
| `stele attach …` | UC-24 |
| `stele purge …` | UC-33 (default dry-run; `--execute` to delete) |
| `stele diff STORE OTHER` | UC-35 |
| `stele hygiene STORE` | UC-39 |
| `stele entangled STORE` | UC-38 |
| `stele forget-check STORE` | UC-42 |
| `stele lineage STORE ENTRY` | UC-44 |
| `stele belief-at STORE AS_OF` | UC-45 |
| `stele conflicts STORE` | UC-46 |
| `stele injection-scan STORE` | UC-48 |
| `stele budget-plan STORE QUERY` | UC-50 |
| `stele seal STORE` | UC-51 |
| `stele verify-seal STORE FILE` | UC-51 |
| `stele receipt STORE ENTRY` | UC-52 |
| `stele replay-check STORE` | UC-53 |
| `stele lifecycle STORE` | UC-55 |
| `stele revoke-key STORE KEY` | UC-56 |
| `stele pack-seal STORE PACK` | UC-57 |
| `stele verify-pack-seal STORE PACK SEAL` | UC-57 |
| `stele explain STORE QUERY` | UC-58 |
| `stele blast STORE ENTRY` | UC-60 |
| `stele merge-classify STORE A B` | UC-61 |
| `stele path-trust STORE ENTRY` | UC-62 |
| `stele journal-chain STORE` | UC-65 |
| `stele spread STORE` | UC-66 |
| `stele density STORE ENTRY` | UC-67 |
| `stele retention STORE ENTRY` | UC-68 |
| `stele health STORE` | UC-70 |
| `stele release-gate STORE` | UC-71 |
| `stele rebuild-index STORE` | UC-73 |
| `stele search-sqlite STORE QUERY` | UC-73 |
| `stele verify-import STORE PACK` | UC-76 |
| `stele decisions STORE` | UC-75 |
| `stele lineage-trust STORE ENTRY` | UC-78 |
| `stele record-exec STORE STEP` | UC-80 |
| `stele verify-exec STORE STEP` | UC-81 |
| `stele authority-gate STORE RISK` | UC-82 |
| `stele claim-closure STORE` | UC-83 |
| `stele cascade STORE FAULT` | UC-85 |
| `stele withdraw-cascade STORE FAULT` | UC-86 |
| `stele repair-plan STORE FAULT` | UC-87 |
| `stele fact-interface STORE` | UC-91 |
| `stele role-scan STORE` | UC-91 |
| `stele dual-search STORE QUERY` | UC-93 |
| `stele commit STORE MSG` | UC-95 |
| `stele checkout STORE HASH` | UC-96 |
| `stele diff-commits STORE A B` | UC-97 |
| `stele copyability STORE QUERY` | UC-98 |

### 7.6 Recovery + batch (UC-33–36)

| API / Tool | Behavior |
|---|---|
| `purge_by_provenance` / `stele_purge_by_provenance` | dry-run list or hard-delete by untrusted source/agent |
| `add_batch` / `stele_add_batch` | all-or-nothing multi-ADD |
| `diff_stores` / `stele_diff_stores` | id-set diff vs another root |
| `search(..., trusted_sources=)` | Select filter by provenance.source |

Library harness: `membench_shaped_report` (UC-37).

### 7.7 Hygiene + entangled + governance eval (UC-38–40)

| API / Tool | Behavior |
|---|---|
| `entangled_suspects` / `stele_entangled_suspects` | LINK neighborhood of seeds/untrusted — **report only** |
| `hygiene_candidates` / `stele_hygiene_candidates` | zombie / net-harm / stale-promoted — **report only** |
| `search(..., prefer_fresh=True)` | soft re-rank by `last_verified` (no SoT write) |
| `governance_shaped_report` | doctor + contested + purge dry-run + hygiene + entangled proxies |

### 7.8 Multi-principal ACL + forgetting (UC-41–43)

| API / Tool | Behavior |
|---|---|
| `search(..., principal_scopes=)` | explicit scope allowlist; no implicit universal when set |
| `forget_compliance` / `stele_forget_compliance` | post-DELETE store+SEARCH leak probe |
| `gatemem_shaped_report` | utility ∩ ACL ∩ forgetting local proxies |

### 7.9 Bi-temporal lineage + conflict surface (UC-44–47)

| API / Tool | Behavior |
|---|---|
| `lineage` / `stele_lineage` | supersede chain + journal (TOKI audit) |
| `belief_at` / `stele_belief_at` | point-in-time SEARCH or inventory |
| `conflict_surface` / `stele_conflict_surface` | contested pairs preserved |
| `memoryagent_shaped_report` | four-competency local proxies |

MCP tool count: **556** (see §7.70). CLI: `lineage`, `belief-at`, `conflicts`, `injection-scan`, `budget-plan`, `seal`, …

### 7.10 Injection gates + compress plan (UC-48–50)

| API / Tool | Behavior |
|---|---|
| `injection_scan` / `stele_injection_scan` | deterministic marker suspects (`risk.py`) |
| `search(..., withhold_injection_suspects=)` | MAPLE retrieval gate |
| `promote(..., block_injection_suspects=)` | MAPLE promote gate |
| `select_budget_plan` / `stele_select_budget_plan` | fitted vs overflow under budget |
| `maple_shaped_report` | write/retrieve/promote gate proxies |

### 7.11 Content seals + attribution (UC-51–54)

| API / Tool | Behavior |
|---|---|
| `store_seal` / `stele_store_seal` | SHA-256 flat seal over entry digests + journal |
| `verify_seal` / `stele_verify_seal` | compare prior seal to live SoT |
| `attribution_receipt` / `stele_attribution_receipt` | per-entry digest + journal |
| `replay_consistency` / `stele_replay_consistency` | journal↔SoT soft check |
| `memmark_shaped_report` | seal/receipt/tamper/replay proxies |
| `integrity.entry_content_digest` | belief-content SHA-256 helper |

### 7.12 Lifecycle + TEPA revoke + pack seals (UC-55–59)

| API / Tool | Behavior |
|---|---|
| `lifecycle_inventory` / `stele_lifecycle_inventory` | HOT/WARM/COLD counts (AMV-L) |
| `search(..., lifecycle_tiers=)` | eligibility filter after hybrid retrieval |
| `revoke_by_key` / `unrevoke` | TEPA-shaped keyed revoke; state `revoked` |
| `pack_seal` / `verify_pack_seal` | export-surface content seals |
| `search_explain` / `stele_search_explain` | channel `rank_detail` |
| `tepa_amvl_shaped_report` | revoke + tier + pack seal + explain proxies |

### 7.13 Graph federation proxies (UC-60–64)

| API / Tool | Behavior |
|---|---|
| `blast_radius` / `stele_blast_radius` | LINK neighborhood layers (RippleMem/MAP-Graph) |
| `merge_classify` / `stele_merge_classify` | MELD five-outcome; report-only |
| `path_trust` / `stele_path_trust` | multiplicative provenance path trust |
| `search(..., min_path_trust=)` | MAP-Graph Select gate |
| `meld_map_shaped_report` | classify + blast + trust proxies |
| `stele_core.graph` | pure helpers (zero deps) |

### 7.14 Journal chain + activation (UC-65–69)

| API / Tool | Behavior |
|---|---|
| journal `prev_hash`/`row_hash` | GPM-shaped append chain on new writes |
| `verify_journal_chain` / `stele_verify_journal_chain` | fail-closed chain report |
| `journal_chain_head` | current head digest |
| `spread_activate` / `stele_spread_activate` | SYNAPSE-shaped activation |
| `connection_density` / `prefer_dense` | SodaMem-shaped density rank |
| `retention_score` / `min_retention` | Oblivion-shaped decay gate |
| `soda_synapse_shaped_report` | combined local proxies |
| `stele_core.activation` | pure helpers |

### 7.15 Health, release gate, cues, derived index (UC-70–74)

| API / Tool | Behavior |
|---|---|
| `health_report` / `stele_health_report` | unified barriers across integrity/chain/injection |
| `release_gate` / `stele_release_gate` | GPM fail-closed; head mismatch/drift abstains |
| `export(..., require_release=True)` | blocks pack when gate fails |
| `cue_tags` + `search(..., cue_tags=)` | associative cue filter |
| `rebuild_sqlite_index` / `search_sqlite` | derived FTS5 (stdlib); files remain SoT |
| `gpm_release_shaped_report` | health+release+cue+sqlite proxies |

MCP tool count: **59** at end of v2.0. CLI: `health` / `release-gate` / `rebuild-index` / `search-sqlite`.

### 7.16 Decision receipts, import verify, lineage trust (UC-75–79)

| API / Tool | Behavior |
|---|---|
| `release_gate(..., issue_receipt=True)` | GPM local decision receipt on success |
| `list_decision_receipts` / `verify_decision_receipt` | audit + digest recompute |
| `verify_import` / `stele_verify_import` | PAM halt-on-first-failure |
| `hydrate(..., require_verify=True)` | blocked until import gate passes |
| export `policy` / `policy_digest` | attested pack policy surface |
| `lineage_trust` / `refuse_untrusted_lineage` | MemLineage-shaped Select refuse |
| `pam_cava_shaped_report` | receipt+import+lineage proxies |

MCP tool count: **63** at end of v2.1. CLI: `verify-import` / `decisions` / `lineage-trust`.

### 7.17 PoEM execution, PPMF authority, claim closure (UC-80–84)

| API / Tool | Behavior |
|---|---|
| `record_execution` / `stele_record_execution` | append-only `executions.ndjson` hash chain |
| `verify_execution` / `stele_verify_execution` | skip safety step only if ledger confirms (ignore memory text) |
| `verify_execution_chain` | integrity of execution ledger |
| `authority_gate` / `stele_authority_gate` | risk vs provenance authority (pack capped) |
| `claim_closure` / `stele_claim_closure` | exact promoted-fact closure at head |
| `poem_ppmf_shaped_report` | execution+authority+closure proxies |

Module: `stele_core.execution`. MCP tool count: **67** at end of v2.2. CLI: `record-exec` / `verify-exec` / `authority-gate` / `claim-closure`.

### 7.18 Cascade repair + non-revival (UC-85–89)

| API / Tool | Behavior |
|---|---|
| `cascade_impact` / `cascade_exposure` | depends-on descendant set + promoted exposure |
| `withdraw_cascade` / `stele_withdraw_cascade` | barrier-first revoke of fault+descendants |
| `repair_plan` / `stele_repair_plan` | greedy predecessor-closure selection (not exact min-cut) |
| `non_revival_probe` | revoked IDs must not appear in SEARCH |
| `memorepair_shaped_report` | exposure→plan→withdraw→probe proxies |

Module: `stele_core.repair`. MCP tool count: **71** at end of v2.3. CLI: `cascade` / `withdraw-cascade` / `repair-plan`.

### 7.19 Typed roles + dual-channel Select (UC-90–94)

| API / Tool | Behavior |
|---|---|
| `memory_role` field | evidence \| claim \| decision (optional) |
| `fact_interface` / `stele_fact_interface` | MemIR-shaped authorize set |
| `role_collapse_scan` / `stele_role_collapse_scan` | provenance-role collapse suspects |
| `search(..., claims_only=)` | routine channel filter |
| `claim_closure(require_claim_role=True)` | refuse evidence-role IDs |
| `quality_gate` / `dual_channel_search` | D-Mem escalate to deliberation |
| `memir_dmem_shaped_report` | roles+dual-channel proxies |

Module: `stele_core.roles`. MCP tool count: **75** at end of v2.4. CLI: `fact-interface` / `role-scan` / `dual-search`.

### 7.20 GitOfThoughts commit substrate (UC-95–99)

| API / Tool | Behavior |
|---|---|
| `commit_view` / `stele_commit_view` | append `commits.ndjson` + update branch ref |
| `checkout_view` / `stele_checkout_view` | replay entry-id set |
| `diff_commits` / `stele_diff_commits` | only_in_a / only_in_b / shared |
| `merge_branches` | union merge of two branch tips |
| `copyability_gate` / `stele_copyability_gate` | near-duplicate τ gate |
| `gitofthoughts_shaped_report` | commit+diff+copyability proxies |

Module: `stele_core.versioning`. MCP tool count: **79** at end of v2.5. CLI: `commit` / `checkout` / `diff-commits` / `copyability`.

### 7.21 ChronoMem version + MemStrata supersession (UC-100–104)

| API / Tool | Behavior |
|---|---|
| `pin_memory_version` / `stele_pin_memory_version` | commit promoted ids as tagged version view |
| `activate_version` / `stele_activate_version` | set/clear `refs/read_head` overlay |
| `counterfactual_search` / `stele_counterfactual_search` | Select at version without mutating head |
| `_version_select` | load pinned ids (incl. later-superseded) |
| `exclude_superseded` Select flag | keep supersession winners only |
| `stale_fact_scan` / `stele_stale_fact_scan` | report non-current promoted facts |
| `chronomem_strata_shaped_report` | pin+activate+cf+stale proxies |

Modules: `stele_core.versioning` (read_head) + `stele_core.strata`. MCP tool count: **83** at end of v2.6. CLI: `pin-version` / `activate-version` / `stale-facts`.

### 7.22 TARL updates + Memory Worth (UC-105–109)

| API / Tool | Behavior |
|---|---|
| `propose_update` / `stele_propose_update` | classify five-action plan (no write) |
| `apply_update` / `stele_apply_update` | execute append/noop/revise/reject/defer |
| `ledger_view` / `stele_ledger_view` | accepted/pending/rejected projection |
| `memory_worth` / `stele_memory_worth` | helpful/(helpful+harmful) |
| `low_worth_scan` / `stele_low_worth_scan` | below-threshold candidates |
| Select `min_worth` | suppress low-MW hits |
| `tarl_mw_shaped_report` | TARL+MW proxies |

Modules: `stele_core.tarl` + `stele_core.worth`. MCP tool count: **88** at end of v2.7. CLI: `propose-update` / `apply-update` / `ledger-view` / `memory-worth` / `low-worth`.

### 7.23 MemTX belief-commit + action-safety (UC-110–114)

| API / Tool | Behavior |
|---|---|
| `begin_transaction` / `stele_begin_transaction` | open staging tx |
| `stage_write` / `stele_stage_write` | ADD quarantined + attach to tx |
| `validate_transaction` | tentative-only barriers |
| `commit_transaction` / `stele_commit_transaction` | promote staged (belief commit) |
| `abort_transaction` / `stele_abort_transaction` | revoke staged tentative |
| `action_safe_gate` / `stele_action_safe_gate` | act only on action_safe; block in-flight keys |
| `in_flight_report` / `stele_in_flight_report` | open txs + staged ids |
| `aoep_report` | AOEP-v0 shaped obligation checklist |
| `memtx_aoep_shaped_report` | MemTX+AOEP proxies |

Module: `stele_core.memtx`. MCP tool count: **94** at end of v2.8. CLI: `begin-tx` / `commit-tx` / `abort-tx` / `action-safe` / `in-flight`.

### 7.24 LatticeMind + Cordon outbox (UC-115–119)

| API / Tool | Behavior |
|---|---|
| `symbolic_conflict_scan` / `stele_symbolic_conflict_scan` | duplicate keys + LINK triangles |
| `classify_conflict` / `stele_classify_conflict` | credibility vs coordination |
| `compact_render` / `stele_compact_render` | reader character budget pack |
| `stage_effect` / `stele_stage_effect` | outbox pending |
| `release_effects` / `stele_release_effects` | pending → ready |
| `list_effects` / `stele_list_effects` | outbox listing |
| `lattice_cordon_shaped_report` | Lattice+Cordon proxies |

Modules: `stele_core.lattice` + `stele_core.cordon`. MCP tool count: **100** at end of v2.9. CLI: `symbolic-conflicts` / `classify-conflict` / `compact-render` / `stage-effect` / `list-effects`.

### 7.25 STALE/VTA + GEM (UC-120–124)

| API / Tool | Behavior |
|---|---|
| `state_resolution` / `stele_state_resolution` | winner clarity per conflict_key |
| `premise_resistance` / `stele_premise_resistance` | refuse stale-dominated premises |
| `ipa_gap_scan` / `stele_ipa_gap_scan` | live Select vs winners |
| `verify_transition` / `stele_verify_transition` | VTA chronology/provenance |
| `related_slot_scan` / `stele_related_slot_scan` | same-domain reverify candidates |
| `gem_report` / `stele_gem_report` | six GEM conditions |
| `stale_gem_shaped_report` | STALE+VTA+GEM proxies |

Modules: `stele_core.stale` + `stele_core.gem`. MCP tool count: **106** at end of v3.0. CLI: `state-resolution` / `premise-resistance` / `verify-transition` / `related-slots` / `gem-report`.

### 7.26 StateFuse projection + TOKI ops + MemArchitect bid (UC-125–129)

| API / Tool | Behavior |
|---|---|
| `project_resolve` / `stele_project_resolve` | select or abstain; SoT unchanged |
| `pin_projection` / `stele_pin_projection` | overlay pin only |
| `clear_projection_pin` / `stele_clear_projection_pin` | clear overlay |
| `list_projection_pins` / `stele_list_projection_pins` | list overlays |
| `correction_handle` / `stele_correction_handle` | claim_id + claim_ref |
| `toki_classify_operator` / `stele_toki_classify_operator` | four-operator plan |
| `toki_anomaly_scan` / `stele_toki_anomaly_scan` | three anomaly proxies |
| `context_bid` / `stele_context_bid` | triage & bid slots |
| `statefuse_toki_shaped_report` | StateFuse+TOKI+bid proxies |

Modules: `stele_core.fuse` + `stele_core.toki_ops` + `stele_core.architect`. MCP tool count: **114** at end of v3.1. CLI: `project-resolve` / `correction-handle` / `pin-projection` / `toki-classify` / `toki-anomalies` / `context-bid`.

### 7.27 MemoRepair min-cut + CUPMem + CMGL (UC-130–134)

| API / Tool | Behavior |
|---|---|
| `repair_select_mincut` / `stele_repair_select_mincut` | exact s–t min-cut closure |
| `adjudicate_update` / `stele_adjudicate_update` | write-side CUPMem decision |
| `unknown_current_slots` / `stele_unknown_current_slots` | unsafe slots |
| `authorize_retrieval` / `stele_authorize_retrieval` | settled-slot filter |
| `admit_gate` / `stele_admit_gate` | CMGL fail-closed admit |
| `list_admit_receipts` / `stele_list_admit_receipts` | admission audit |
| `memorepair_cupmem_cmgl_shaped_report` | suite harness |

Modules: `stele_core.repair` (mincut) + `stele_core.cupmem` + `stele_core.cmgl`. MCP tool count: **120** at end of v3.2. CLI: `repair-mincut` / `adjudicate` / `unknown-slots` / `authorize-retrieval` / `admit-gate`.

### 7.28 TierMem + MSCE (UC-135–139)

| API / Tool | Behavior |
|---|---|
| `put_raw_page` / `stele_put_raw_page` | immutable Tier-2 raw |
| `sufficiency_gate` / `stele_sufficiency_gate` | hit/miss router proxy |
| `escalate_raw` / `stele_escalate_raw` | load linked raw |
| `verified_writeback` / `stele_verified_writeback` | summary + raw links |
| `skill_eligibility` / `stele_skill_eligibility` | MSCE gate |
| `crystallize_skill` / `stele_crystallize_skill` | skill draft (+ optional ADD) |
| `skill_catalog` / `stele_skill_catalog` | callable skills |
| `value_backfill` | reflection-weighted usage |
| `tiermem_msce_shaped_report` | suite harness |

Modules: `stele_core.tiermem` + `stele_core.msce`. MCP tool count: **127** at end of v3.3. CLI: `put-raw` / `sufficiency` / `escalate-raw` / `writeback` / `crystallize-skill` / `skill-catalog`.

### 7.29 FadeMem + SSGM Weibull + MemR3 (UC-140–145)

| API / Tool | Behavior |
|---|---|
| `fade_strength` / `stele_fade_strength` | dual-layer SML/LML strength |
| `fade_scan` / `stele_fade_scan` | below-threshold candidates (no delete) |
| `fusion_candidates` / `stele_fusion_candidates` | deterministic fuse/supersede pairs |
| `weibull_relevance` / `stele_weibull_relevance` | SSGM Weibull score |
| Select `min_weibull` | filter + annotate hits |
| `evidence_gap` / `stele_evidence_gap` | uncovered tokens/digits |
| `reflective_retrieve` / `stele_reflective_retrieve` | gap + next probes |
| `gap_tracker_update` | close gaps after follow-up Select |
| `fademem_memr3_shaped_report` | suite harness |

Modules: `stele_core.fademem` + `stele_core.memr3`. MCP tool count: **133** at end of v3.4. CLI: `fade-scan` / `fusion-candidates` / `weibull` / `evidence-gap` / `reflective-retrieve`.

### 7.30 Archive tier + SF-AMS CIS + MemCon (UC-146–151)

| API / Tool | Behavior |
|---|---|
| `archive_plan` / `stele_archive_plan` | utility-weighted candidates |
| `archive_apply` / `stele_archive_apply` | promoted → archived |
| `unarchive` / `stele_unarchive` | archived → promoted |
| `list_archived` / `stele_list_archived` | archive inventory |
| `composite_importance` / `stele_composite_importance` | SF-AMS CIS |
| `cis_scan` / `stele_cis_scan` | CIS ranking |
| `control_suggest` / `stele_control_suggest` | MemCon action proxy |
| `archive_sfams_memcon_shaped_report` | suite harness |

Modules: `stele_core.archive` + `stele_core.sfams` + `stele_core.memcon`. State `archived` in `STATES`. MCP tool count: **140** at end of v3.5. CLI: `archive-plan` / `archive-apply` / `unarchive` / `cis` / `cis-scan` / `control-suggest`.

### 7.31 SCM + GAM + ACM (UC-152–158)

| API / Tool | Behavior |
|---|---|
| `value_tag` / `stele_value_tag` | SCM 4D importance |
| `wm_push` / `wm_list` / `wm_clear` | capacity-7 working memory overlay |
| `sleep_trigger` / `sleep_plan` / `sleep_apply_nrem` | sleep cycle + NREM reinforce |
| `episodic_buffer` / `stele_episodic_buffer` | quarantined buffer |
| `semantic_boundary` / `stele_semantic_boundary` | topic-shift detector |
| `consolidate_plan` / `stele_consolidate_plan` | buffer→topic plan |
| `anticipate` / `stele_anticipate` | prefetch neighborhood |
| `verify_compaction` / `stele_verify_compaction` | fail-closed compact check |
| `scm_gam_acm_shaped_report` | suite harness |

Modules: `stele_core.scm` + `stele_core.gam` + `stele_core.acm`. MCP tool count: **151** at end of v3.6. CLI: `value-tag` / `wm-*` / `sleep-*` / `episodic-buffer` / `semantic-boundary` / `consolidate-plan` / `anticipate` / `verify-compaction`.

### 7.32 LightMem + HippoRAG + Quipu/MAP-Graph (UC-159–165)

| API / Tool | Behavior |
|---|---|
| `sensory_filter` / `stele_sensory_filter` | pre-compress draft text |
| `stage_inventory` / `stele_stage_inventory` | sensory/stm/ltm counts |
| `topic_segments` / `stele_topic_segments` | Jaccard topic boundaries |
| `stage_budget_plan` / `stele_stage_budget_plan` | efficiency budget split |
| `ppr_scores` / `stele_ppr_scores` | Personalized PageRank |
| `multi_hop_retrieve` / `stele_multi_hop_retrieve` | seed→PPR multi-hop |
| `write_gate` / `stele_write_gate` | Quipu pending predicates |
| `action_risk_gate` / `stele_action_risk_gate` | MAP-Graph Allow/Block/… |
| `lightmem_hippo_quipu_shaped_report` | suite harness |

Modules: `stele_core.lightmem` + `stele_core.hipporag` + `stele_core.mapgate`. MCP tool count: **159** at end of v3.7. CLI: `sensory-filter` / `stage-inventory` / `stage-budget` / `multi-hop` / `write-gate` / `action-risk-gate`.

### 7.33 ProGraph + EMG + AgentIR (UC-166–173)

| API / Tool | Behavior |
|---|---|
| `extract_residuals` / `stele_extract_residuals` | dates/quantities/names/codes from body |
| `register_entities` / `stele_register_entities` | entity→entry registry |
| `profile_expand` / `stele_profile_expand` | seed + entity expand |
| `residual_augment` / `stele_residual_augment` | query-relevant residual packs |
| `match_correction` / `stele_match_correction` | failure→success edit path |
| `insight_inject` / `stele_insight_inject` | loop-free insight string |
| `cascade_route` / `stele_cascade_route` | margin-triggered channel skip |
| `multi_channel_fuse` / `stele_multi_channel_fuse` | lexical±ppr±residual RRF |
| `prograph_emg_agentir_shaped_report` | suite harness |

Modules: `stele_core.prograph` + `stele_core.emg` + `stele_core.agentir`. MCP tool count: **167** at end of v3.8. CLI: `residuals` / `entities` / `profile-expand` / `residual-augment` / `match-correction` / `insight-inject` / `cascade-route` / `multi-channel`.

### 7.34 Governed Memory + HyMem (UC-174–182)

| API / Tool | Behavior |
|---|---|
| `dual_project` / `stele_dual_project` | atomic facts + typed properties |
| `governance_route` / `stele_governance_route` | fast hybrid policy ranking |
| `session_delta_open` / `stele_session_delta_open` | open progressive session |
| `session_delta_deliver` / `stele_session_delta_deliver` | delta inject vs skip critical |
| `session_delta_status` / `stele_session_delta_status` | inspect delivered set |
| `entity_context` / `stele_entity_context` | Properties + Observations pack |
| `entity_leak_probe` / `stele_entity_leak_probe` | cross-entity leak assert |
| `hymem_classify_slot` / `stele_hymem_classify_slot` | plan/execute/reason/memory |
| `hymem_isolate_pack` / `stele_hymem_isolate_pack` | typed planner pack |
| `govmem_hymem_shaped_report` | suite harness |

Modules: `stele_core.govmem` + `stele_core.hymem`. MCP tool count: **176** at end of v3.9. CLI: `dual-project` / `governance-route` / `session-delta-*` / `entity-context` / `entity-leak-probe` / `hymem-slot` / `hymem-isolate`.

### 7.35 Deterministic freshness + MemTxn + Fleet (UC-183–192)

| API / Tool | Behavior |
|---|---|
| `extract_version_markers` / `stele_extract_version_markers` | serial/ISO markers |
| `freshness_resolve` / `stele_freshness_resolve` | max(serial\|ts) tip |
| `assemble_current` / `stele_assemble_current` | query→group→resolve |
| `hop_freshness` / `stele_hop_freshness` | per-hop assemble |
| `patch_test` / `stele_patch_test` | Ordered PatchTest |
| `temporal_resolve` / `stele_temporal_resolve` | visible tip by key |
| `recover_active_map` / `stele_recover_active_map` | complete tip map |
| `fleet_scope_gate` / `stele_fleet_scope_gate` | scope allowlist |
| `propagate_plan` / `stele_propagate_plan` | report-only copy plan |
| `stale_propagation_scan` / `stele_stale_propagation_scan` | stale tip suspects |
| `freshness_memtxn_fleet_shaped_report` | suite harness |

Modules: `stele_core.freshness` + `stele_core.patchtxn` + `stele_core.fleetprop`. MCP tool count: **186** at end of v4.0. CLI: `version-markers` / `freshness-resolve` / `assemble-current` / `hop-freshness` / `patch-test` / `temporal-resolve` / `recover-active-map` / `fleet-scope-gate` / `propagate-plan` / `stale-propagation`.

### 7.36 BudgetMem + skill ranker + ERSkill (UC-193–202)

| API / Tool | Behavior |
|---|---|
| `query_complexity` / `stele_query_complexity` | hardness band |
| `budget_tier_route` / `stele_budget_tier_route` | Low/Mid/High per module |
| `budget_module_plan` / `stele_budget_module_plan` | fit under global budget |
| `skill_rank` / `stele_skill_rank` | lexical skill/workflow rank |
| `skill_prereq_expand` / `stele_skill_prereq_expand` | LINK prereq walk |
| `list_retrieval_primitives` / `stele_list_retrieval_primitives` | primitive catalog |
| `list_retrieval_skills` / `stele_list_retrieval_skills` | built-in skills |
| `compose_retrieval_skill` / `stele_compose_retrieval_skill` | validate sequence |
| `route_retrieval_skill` / `stele_route_retrieval_skill` | cue → skill |
| `run_retrieval_skill` / `stele_run_retrieval_skill` | execute primitives |
| `budgetmem_erskill_shaped_report` | suite harness |

Modules: `stele_core.budgetmem` + `stele_core.skillrank` + `stele_core.erskill`. MCP tool count: **196** at end of v4.1. CLI: `query-complexity` / `budget-tier-route` / `budget-module-plan` / `skill-rank` / `skill-prereq` / `retrieval-skills` / `route-retrieval-skill` / `run-retrieval-skill`.

### 7.37 ConsistencyGate + MemGate + sovereignty (UC-203–211)

| API / Tool | Behavior |
|---|---|
| `support_score` / `stele_support_score` | lexical support 0–1 |
| `consistency_admit` / `stele_consistency_admit` | admit/quarantine/reject |
| `retrieval_admit` / `stele_retrieval_admit` | query-conditioned hit filter |
| `task_conditioned_pack` / `stele_task_conditioned_pack` | admitted pack ≤ budget |
| `sovereignty_checklist` / `stele_sovereignty_checklist` | nine primitives coverage |
| `post_delete_verify` / `stele_post_delete_verify` | delete absence check |
| `rollback_plan` / `stele_rollback_plan` | report-only rollback steps |
| `consistency_memgate_sovereignty_shaped_report` | suite harness |

Modules: `stele_core.consistencygate` + `stele_core.memgate` + `stele_core.mnemonic`. MCP tool count: **203** at end of v4.2. CLI: `support-score` / `consistency-admit` / `retrieval-admit` / `task-pack` / `sovereignty-checklist` / `post-delete-verify` / `rollback-plan`.

### 7.38 SodaMem + MemRefine + Ariadne/MemFuse (UC-212–220)

| API / Tool | Behavior |
|---|---|
| `density_fuse` / `stele_density_fuse` | multi-tunnel mass per evidence id |
| `evidence_plan` / `stele_evidence_plan` | planner ID gather + fuse |
| `cited_pack` / `stele_cited_pack` | reader blocks with mandatory citations |
| `compress_candidates` / `stele_compress_candidates` | near-duplicate pairs |
| `refine_plan` / `stele_refine_plan` | storage-budget merge/delete plan |
| `merge_link_add` / `stele_merge_link_add` | merge \| link \| add decision |
| `bridge_discover` / `stele_bridge_discover` | LINK BFS bridges |
| `fuse_cluster` / `stele_fuse_cluster` | cluster summary over atomic ids |
| `sodamem_memrefine_ariadne_shaped_report` | suite harness |

Modules: `stele_core.sodamem` + `stele_core.memrefine` + `stele_core.ariadne`. MCP tool count: **211** at end of v4.3. CLI: `density-fuse` / `evidence-plan` / `cited-pack` / `compress-candidates` / `refine-plan` / `merge-link-add` / `bridge-discover` / `fuse-cluster`.

### 7.39 TGMS + MemoryData localized maintenance (UC-221–228)

| API / Tool | Behavior |
|---|---|
| `result_digest` / `stele_result_digest` | SHA-256 content digest |
| `operator_cost_estimate` / `stele_operator_cost_estimate` | pre-exec cost guard |
| `plan_static_verify` / `stele_plan_static_verify` | DAG schema/refs/grounding/cost |
| `claim_verify` / `stele_claim_verify` | claims vs execution trace |
| `summary_quarantine_scan` / `stele_summary_quarantine_scan` | correction overlap quarantine |
| `localized_maintenance_plan` / `stele_localized_maintenance_plan` | O7 bound touch set |
| `maintenance_cost_compare` / `stele_maintenance_cost_compare` | local vs global cost proxy |
| `tgms_memdata_shaped_report` | suite harness |

Modules: `stele_core.tgms` + `stele_core.memdata`. MCP tool count: **218** at end of v4.4. CLI: `result-digest` / `operator-cost` / `plan-verify` / `claim-verify` / `summary-quarantine` / `local-maint` / `maint-cost`.

### 7.40 TMA-NM + AM-Sentry (UC-229–235)

| API / Tool | Behavior |
|---|---|
| `origin_bind` / `stele_origin_bind` | channel → act_class |
| `propagate_origin` / `stele_propagate_origin` | inherit max untrust |
| `launder_scan` / `stele_launder_scan` | L-a/b/c marker proxies |
| `act_authority_gate` / `stele_act_authority_gate` | deny / elevate / user auth |
| `save_policy` / `stele_save_policy` | admit/quarantine/reject |
| `retrieval_screen` / `stele_retrieval_screen` | block before inject |
| `tmanm_amsentry_shaped_report` | suite harness |

Modules: `stele_core.tmanm` + `stele_core.amsentry`. MCP tool count: **224** at end of v4.5. CLI: `origin-bind` / `propagate-origin` / `launder-scan` / `act-authority` / `save-policy` / `retrieval-screen`.

### 7.41 MemForest/MemTree + xMemory (UC-236–243)

| API / Tool | Behavior |
|---|---|
| `build_memtree` / `stele_build_memtree` | hierarchical temporal index |
| `dirty_path_plan` / `stele_dirty_path_plan` | localized update path |
| `coarse_to_fine` / `stele_coarse_to_fine` | interval→leaf retrieve |
| `build_themes` / `stele_build_themes` | theme bootstrap |
| `theme_attach` / `stele_theme_attach` | attach or create theme |
| `split_merge_plan` / `stele_split_merge_plan` | overcrowded/tiny repair |
| `top_down_pack` / `stele_top_down_pack` | theme pack + selective expand |
| `memforest_xmemory_shaped_report` | suite harness |

Modules: `stele_core.memforest` + `stele_core.xmemory`. MCP tool count: **231** at end of v4.6. CLI: `build-memtree` / `dirty-path` / `coarse-to-fine` / `build-themes` / `theme-attach` / `split-merge` / `top-down-pack`.

### 7.42 MemSecBench + SleepGate + A-MemGuard (UC-244–252)

| API / Tool | Behavior |
|---|---|
| `persistence_probe` / `stele_persistence_probe` | Write persistence |
| `execute_chain_probe` | Recall/Adopt/Act |
| `selective_repair_plan` / `stele_selective_repair_plan` | SRSR-shaped plan |
| `lifecycle_report` / `stele_lifecycle_report` | WEF bundle |
| `conflict_tag` / `stele_conflict_tag` | supersession σ |
| `forget_gate_plan` / `stele_forget_gate_plan` | PI compress plan |
| `consolidate_survivors` / `stele_consolidate_survivors` | survivor summary |
| `pi_depth_scan` / `stele_pi_depth_scan` | PI depth |
| `consensus_admit` / `stele_consensus_admit` | multi-channel admit |
| `memsec_sleepgate_amemguard_shaped_report` | suite harness |

Modules: `stele_core.memsec` + `stele_core.sleepgate` + `stele_core.amemguard`. MCP tool count: **240** at end of v4.7. CLI: `persistence-probe` / `execute-chain-probe` / `lifecycle-report` / `selective-repair` / `conflict-tag` / `forget-gate` / `consolidate-survivors` / `pi-depth` / `consensus-admit`.

### 7.43 DepRepair + MPBench (UC-253–261)

| API / Tool | Behavior |
|---|---|
| `build_mem_action_graph` / `stele_build_mem_action_graph` | LINK + action graph |
| `dependency_trace` / `stele_dependency_trace` | downstream faults |
| `preserve_independent` / `stele_preserve_independent` | trusted support keep |
| `selective_replay_plan` / `stele_selective_replay_plan` | deactivate/quarantine/replay |
| `classify_write_channel` / `stele_classify_write_channel` | write-channel taxonomy |
| `source_isolation_gate` / `stele_source_isolation_gate` | admit/quarantine/reject |
| `write_channel_inventory` / `stele_write_channel_inventory` | channel counts |
| `channel_admit_batch` / `stele_channel_admit_batch` | batch isolation |
| `deprepair_mpbench_shaped_report` | suite harness |

Modules: `stele_core.deprepair` + `stele_core.mpbench`. MCP tool count: **248** at end of v4.8. CLI: `mem-action-graph` / `dependency-trace` / `preserve-independent` / `selective-replay` / `classify-write-channel` / `source-isolation` / `write-channel-inventory` / `channel-admit-batch`.

### 7.44 MemPoison + Salami (UC-262–269)

| API / Tool | Behavior |
|---|---|
| `slot_coverage` / `stele_slot_coverage` | semantic slots |
| `threat_tier_classify` / `stele_threat_tier_classify` | L1/L2/L3 |
| `dormant_trigger_scan` / `stele_dormant_trigger_scan` | L3 inventory |
| `compositional_coalition_scan` / `stele_compositional_coalition_scan` | salami sets |
| `collusion_risk_gate` / `stele_collusion_risk_gate` | retrieval firewall |
| `mempoison_ladder_report` / `stele_mempoison_ladder_report` | ladder inventory |
| `salami_pair_probe` / `stele_salami_pair_probe` | two-fragment probe |
| `mempoison_salami_shaped_report` | suite harness |

Modules: `stele_core.mempoison`. MCP tool count: **255** at end of v4.9. CLI: `slot-coverage` / `threat-tier` / `dormant-scan` / `coalition-scan` / `collusion-gate` / `mempoison-ladder` / `salami-pair`.

### 7.45 Knowledge-layer + Credential reject + Uncertainty (UC-270–281)

| API / Tool | Behavior |
|---|---|
| `classify_persistence_layer` / `stele_classify_persistence_layer` | K/M/W/I layer |
| `persistence_policy` / `stele_persistence_policy` | layer policy card |
| `layer_inventory` / `stele_layer_inventory` | counts |
| `knowledge_protect_scan` / `stele_knowledge_protect_scan` | no age-fade knowledge |
| `intelligence_reject_gate` / `stele_intelligence_reject_gate` | ephemeral ≠ SoT |
| `credential_scan` / `stele_credential_scan` | secret patterns |
| `credential_reject_gate` / `stele_credential_reject_gate` | write Reject |
| `credential_store_scan` / `stele_credential_store_scan` | hygiene inventory |
| `uncertainty_score` / `stele_uncertainty_score` | Decayer proxy |
| `uncertainty_retrieve_gate` / `stele_uncertainty_retrieve_gate` | Activator proxy |
| `reasoning_reserve_plan` / `stele_reasoning_reserve_plan` | adaptive budget |
| `knowledgelayer_cred_uncertainty_shaped_report` | suite harness |

Modules: `stele_core.knowledgelayer` + `stele_core.credguard` + `stele_core.oblivion_gate`. MCP tool count: **266** at end of v5.0. CLI: `persistence-layer` / `persistence-policy` / `layer-inventory` / `knowledge-protect` / `intelligence-reject` / `credential-scan` / `credential-reject` / `credential-store-scan` / `uncertainty-score` / `uncertainty-gate` / `reasoning-reserve`.

### 7.46 PAM deepen + CapSeal (UC-282–293)

| API / Tool | Behavior |
|---|---|
| `classify_memory_component` / `stele_classify_memory_component` | E/S/P/W/I |
| `build_merkle_dag` / `stele_build_merkle_dag` | SHA-256 DAG |
| `verify_merkle_root` / `stele_verify_merkle_root` | root check |
| `issue_capability_token` / `stele_issue_capability_token` | scoped token |
| `check_capability` / `stele_check_capability` | enforce token |
| `selective_disclose` / `stele_selective_disclose` | subset+ancestors |
| `rehydrate_safe_plan` / `stele_rehydrate_safe_plan` | injection-safe plan |
| `issue_action_capability` / `stele_issue_action_capability` | CapSeal handle |
| `capability_export_probe` / `stele_capability_export_probe` | never export |
| `check_action_capability` / `stele_check_action_capability` | mediate invoke |
| `action_capability_inventory` / `stele_action_capability_inventory` | inventory |
| `pam_capseal_shaped_report` | suite harness |

Modules: `stele_core.pam` + `stele_core.capseal`. MCP tool count: **277** at end of v5.1. CLI: `memory-component` / `merkle-dag` / `verify-merkle` / `issue-cap-token` / `check-cap-token` / `selective-disclose` / `rehydrate-safe` / `issue-action-cap` / `cap-export-probe` / `check-action-cap`.

### 7.47 AgentDoG + MemWeaver (UC-294–306)

| API / Tool | Behavior |
|---|---|
| `classify_risk_source` / `stele_classify_risk_source` | where (source) |
| `classify_failure_mode` / `stele_classify_failure_mode` | how (mode) |
| `classify_real_world_harm` / `stele_classify_real_world_harm` | what (harm) |
| `diagnose_trajectory_step` / `stele_diagnose_trajectory_step` | 3D step |
| `diagnose_trajectory` / `stele_diagnose_trajectory` | trajectory root cause |
| `safe_but_unreasonable_scan` / `stele_safe_but_unreasonable_scan` | soft failures |
| `taxonomy_inventory` / `stele_taxonomy_inventory` | controlled vocab |
| `weave_layer_assign` / `stele_weave_layer_assign` | GM/ExpM/PM |
| `build_hybrid_weave` / `stele_build_hybrid_weave` | tri-layer index |
| `dual_channel_retrieve` / `stele_dual_channel_retrieve` | structured+textual |
| `experience_abstract_plan` / `stele_experience_abstract_plan` | support≥τ plan |
| `temporal_session_conflict_scan` / `stele_temporal_session_conflict_scan` | reconcile plan |
| `multi_hop_depth_score` / `stele_multi_hop_depth_score` | MemHop hops |
| `agentdog_memweaver_shaped_report` | suite harness |

Modules: `stele_core.agentdog` + `stele_core.memweaver`. MCP tool count: **290** at end of v5.2. CLI: `risk-source` / `failure-mode` / `real-world-harm` / `diagnose-step` / `diagnose-trajectory` / `unreasonable-scan` / `taxonomy-inventory` / `weave-layer` / `hybrid-weave` / `dual-channel` / `experience-abstract` / `temporal-conflict` / `hop-depth`.

### 7.48 MemEvolve + MindMemOS + MEMGUARD (UC-307–319)

| API / Tool | Behavior |
|---|---|
| `list_design_space` / `stele_list_design_space` | Encode/Store/Retrieve/Manage catalog |
| `architecture_profile` / `stele_architecture_profile` | concrete Ω |
| `diagnose_architecture` / `stele_diagnose_architecture` | D(Ω) defects |
| `propose_architecture_variants` / `stele_propose_architecture_variants` | Design step |
| `rank_architecture_fitness` / `stele_rank_architecture_fitness` | fitness rank |
| `select_architecture_parents` / `stele_select_architecture_parents` | survivor K |
| `ept_classify` / `stele_ept_classify` | entity–property–time |
| `functional_role_assign` / `stele_functional_role_assign` | semantic/episodic/procedural |
| `contamination_scan` / `stele_contamination_scan` | heterogeneous bleed |
| `type_route_retrieve` / `stele_type_route_retrieve` | type-aware route |
| `dreaming_consolidate_plan` / `stele_dreaming_consolidate_plan` | offline merge/conflict |
| `feedback_revise_plan` / `stele_feedback_revise_plan` | HITL revise |
| `skill_evolve_plan` / `stele_skill_evolve_plan` | trajectory→skill |
| `memevolve_mindmemos_shaped_report` | suite harness |

Modules: `stele_core.memevolve` + `stele_core.mindmemos`. MCP tool count: **303** at end of v5.3. CLI: `design-space` / `arch-profile` / `arch-diagnose` / `arch-variants` / `arch-rank` / `arch-parents` / `ept` / `functional-role` / `contamination-scan` / `type-route` / `dreaming-plan` / `feedback-revise` / `skill-evolve`.

### 7.49 PAMU + BEAM + HaluMem (UC-320–332)

| API / Tool | Behavior |
|---|---|
| `extract_preference_signal` / `stele_extract_preference_signal` | 5-D observe |
| `fuse_preference` / `stele_fuse_preference` | SW+EMA fuse |
| `preference_change_detect` / `stele_preference_change_detect` | C_t trigger |
| `preference_update_plan` / `stele_preference_update_plan` | full pipeline |
| `format_preference_prompt` / `stele_format_preference_prompt` | NL descriptors |
| `beam_category_inventory` / `stele_beam_category_inventory` | 10 categories |
| `classify_beam_query` / `stele_classify_beam_query` | category map |
| `knowledge_update_check` / `stele_knowledge_update_check` | supersede |
| `abstention_gate` / `stele_abstention_gate` | insufficient evidence |
| `contradiction_resolve_plan` / `stele_contradiction_resolve_plan` | preserve contested |
| `event_order_check` / `stele_event_order_check` | time order |
| `localize_hallucination_stage` / `stele_localize_hallucination_stage` | extraction/updating/qa |
| `beam_eval_pack` / `stele_beam_eval_pack` | local pack |
| `pamu_beam_shaped_report` | suite harness |

Modules: `stele_core.pamu` + `stele_core.beam`. MCP tool count: **316** at end of v5.4. CLI: `pref-signal` / `pref-update` / `pref-fuse` / `pref-change` / `pref-prompt` / `beam-categories` / `beam-classify` / `knowledge-update` / `abstention-gate` / `contradiction-plan` / `event-order` / `halu-stage`.

### 7.50 REMem + EverMemOS (UC-333–344)

| API / Tool | Behavior |
|---|---|
| `extract_episodic_gist` / `stele_extract_episodic_gist` | time-aware gist |
| `extract_temporal_facts` / `stele_extract_temporal_facts` | SPO + time |
| `situational_bind` / `stele_situational_bind` | situation dims |
| `build_hybrid_episodic_graph` / `stele_build_hybrid_episodic_graph` | gist+fact graph |
| `agentic_retrieve_plan` / `stele_agentic_retrieve_plan` | iterative tools |
| `ordinal_event_query` / `stele_ordinal_event_query` | first/last |
| `form_memcell` / `stele_form_memcell` | E/F/P/M cell |
| `consolidate_memscenes` / `stele_consolidate_memscenes` | thematic scenes |
| `foresight_filter` / `stele_foresight_filter` | validity window |
| `reconstructive_recollect` / `stele_reconstructive_recollect` | scene-guided |
| `profile_evolve_plan` / `stele_profile_evolve_plan` | profile plan |
| `necessity_sufficiency_check` / `stele_necessity_sufficiency_check` | budget gate |
| `remem_evermemos_shaped_report` | suite harness |

Modules: `stele_core.remem` + `stele_core.evermemos`. MCP tool count: **328**. CLI: `episodic-gist` / `temporal-facts` / `situational-bind` / `episodic-graph` / `agentic-retrieve` / `ordinal-event` / `memcell` / `memscenes` / `foresight-filter` / `recollect` / `profile-evolve` / `necessity-check`.

### 7.51 MemoryOS + NEMORI (UC-345–356)

| API / Tool | Behavior |
|---|---|
| `classify_memory_tier` / `stele_classify_memory_tier` | STM / MTM / LPM |
| `heat_score` / `stele_heat_score` | αN+βL+γR |
| `segment_pages` / `stele_segment_pages` | topic segments |
| `stm_to_mtm_plan` / `stele_stm_to_mtm_plan` | FIFO overflow |
| `mtm_evict_plan` / `stele_mtm_evict_plan` | lowest heat |
| `promote_to_lpm_plan` / `stele_promote_to_lpm_plan` | heat ≥ τ |
| `hierarchical_retrieve` / `stele_hierarchical_retrieve` | STM+MTM+LPM |
| `integrate_episodic_narrative` / `stele_integrate_episodic_narrative` | narrative+cue |
| `anticipatory_schema` / `stele_anticipatory_schema` | predict prior |
| `prediction_error_distill` / `stele_prediction_error_distill` | novel tokens |
| `deserves_memory_gate` / `stele_deserves_memory_gate` | admit if unexpected |
| `distill_batch_plan` / `stele_distill_batch_plan` | batch plan |
| `memoryos_nemori_shaped_report` | suite harness |

Modules: `stele_core.memoryos` + `stele_core.nemori`. MCP tool count: **340**. CLI: `memory-tier` / `heat-score` / `segment-pages` / `stm-to-mtm` / `mtm-evict` / `promote-lpm` / `hier-retrieve` / `episodic-narrative` / `anticipatory-schema` / `prediction-error` / `deserves-memory` / `distill-batch`. Evict/promote/distill plans are **report-only** (`apply: false`).

### 7.52 Hindsight + ReasoningBank (UC-357–367)

| API / Tool | Behavior |
|---|---|
| `classify_network` / `stele_classify_network` | world/experience/opinion/observation |
| `retain_plan` / `stele_retain_plan` | four-network retain |
| `network_inventory` / `stele_network_inventory` | counts |
| `recall_multi_strategy` / `stele_recall_multi_strategy` | RRF lexical+temporal+entity |
| `opinion_reinforce` / `stele_opinion_reinforce` | confidence update |
| `reflect_plan` / `stele_reflect_plan` | disposition-shaped |
| `distill_strategy_item` / `stele_distill_strategy_item` | title/desc/content |
| `failure_lesson_gate` / `stele_failure_lesson_gate` | not success-only |
| `retrieve_strategies` / `stele_retrieve_strategies` | strategy retrieve |
| `consolidate_strategy_plan` / `stele_consolidate_strategy_plan` | dedupe bank |
| `matts_contrastive_plan` / `stele_matts_contrastive_plan` | MaTTS plan |
| `hindsight_reasoningbank_shaped_report` | suite harness |

Modules: `stele_core.hindsight` + `stele_core.reasoningbank`. MCP tool count: **351**. CLI: `classify-network` / `retain-plan` / `network-inventory` / `recall-multi` / `opinion-reinforce` / `reflect-plan` / `distill-strategy` / `failure-lesson-gate` / `matts-plan`. Plans are **report-only**.

### 7.53 MemSkill + Memory-R1 (UC-368–379)

| API / Tool | Behavior |
|---|---|
| `init_skill_bank` / `stele_init_skill_bank` | INSERT/UPDATE/DELETE/SKIP |
| `span_partition` / `stele_span_partition` | span windows |
| `select_skills` / `stele_select_skills` | Top-K controller |
| `execute_skill_plan` / `stele_execute_skill_plan` | skill-guided ops |
| `record_hard_case` / `stele_record_hard_case` | hard-case buffer |
| `designer_evolve_plan` / `stele_designer_evolve_plan` | refine/propose |
| `classify_memory_op` / `stele_classify_memory_op` | ADD/UPDATE/DELETE/NOOP |
| `noop_gate` / `stele_noop_gate` | redundancy NOOP |
| `memory_op_plan` / `stele_memory_op_plan` | op plan |
| `conflict_update_plan` / `stele_conflict_update_plan` | conflict UPDATE |
| `delete_stale_plan` / `stele_delete_stale_plan` | stale DELETE |
| `memskill_memoryr1_shaped_report` | suite harness |

Modules: `stele_core.memskill` + `stele_core.memoryr1`. MCP tool count: **362**. CLI: `skill-bank` / `span-partition` / `select-skills` / `execute-skills` / `hard-case` / `designer-evolve` / `memory-op` / `noop-gate` / `memory-op-plan` / `conflict-update` / `delete-stale`. Plans are **report-only**.

### 7.54 G-Memory + MemMA (UC-380–391)

| API / Tool | Behavior |
|---|---|
| `classify_graph_tier` / `stele_classify_graph_tier` | insight/query/interaction |
| `build_query_graph` / `stele_build_query_graph` | query graph |
| `upward_insight_traverse` / `stele_upward_insight_traverse` | query→insight |
| `downward_interaction_traverse` / `stele_downward_interaction_traverse` | query→interaction |
| `bidirectional_retrieve` / `stele_bidirectional_retrieve` | bi-directional |
| `hierarchy_update_plan` / `stele_hierarchy_update_plan` | post-task update |
| `meta_thinker_guidance` / `stele_meta_thinker_guidance` | construction/retrieval |
| `answerability_check` / `stele_answerability_check` | ANSWERABLE? |
| `synthesize_probe_qa` / `stele_synthesize_probe_qa` | probe QA |
| `verify_probes` / `stele_verify_probes` | in-situ verify |
| `repair_from_probes` / `stele_repair_from_probes` | SKIP/MERGE/INSERT |
| `gmemory_memma_shaped_report` | suite harness |

Modules: `stele_core.gmemory` + `stele_core.memma`. MCP tool count: **373**. CLI: `graph-tier` / `query-graph` / `insight-up` / `interaction-down` / `bidir-retrieve` / `hierarchy-update` / `meta-thinker` / `answerability` / `probe-qa` / `verify-probes` / `repair-probes`. Plans are **report-only**.

### 7.55 AWM + RRM (UC-392–403)

| API / Tool | Behavior |
|---|---|
| `induce_workflow` / `stele_induce_workflow` | induce from successful trajectory |
| `online_induce_gate` / `stele_online_induce_gate` | induce only on success label |
| `workflow_memory_add_plan` / `stele_workflow_memory_add_plan` | ADD/SKIP plan |
| `retrieve_workflows` / `stele_retrieve_workflows` | lexical workflow retrieve |
| `workflow_step_budget` / `stele_workflow_step_budget` | guided step estimate |
| `distill_retrieval_experience` / `stele_distill_retrieval_experience` | M+/M− procedural experience |
| `anomaly_trigger` / `stele_anomaly_trigger` | empty/dup/off-topic/budget |
| `query_level_guidance` / `stele_query_level_guidance` | focus only; never answer pack |
| `experience_lifecycle_score` / `stele_experience_lifecycle_score` | usage × decay utility |
| `prune_experience_plan` / `stele_prune_experience_plan` | capacity prune plan |
| `isolate_factual_from_procedural` / `stele_isolate_factual_from_procedural` | leak gate |
| `awm_rrm_shaped_report` | suite harness |

Modules: `stele_core.awm` + `stele_core.rrm`. MCP tool count: **384**. CLI: `induce-workflow` / `online-induce-gate` / `workflow-add-plan` / `retrieve-workflows` / `workflow-step-budget` / `distill-retrieval-exp` / `anomaly-trigger` / `query-level-guidance` / `experience-lifecycle` / `prune-experience` / `isolate-factual`. Plans are **report-only**.

### 7.56 ReMe + Dynamic Cheatsheet (UC-404–415)

| API / Tool | Behavior |
|---|---|
| `multi_faceted_distill` / `stele_multi_faceted_distill` | success/failure/comparative facets |
| `scenario_retrieve` / `stele_scenario_retrieve` | scenario-aware pool retrieve |
| `adaptive_rewrite_plan` / `stele_adaptive_rewrite_plan` | task-specific guidance rewrite |
| `utility_after_reuse` / `stele_utility_after_reuse` | freq/utility counters |
| `selective_add_plan` / `stele_selective_add_plan` | validated ADD/SKIP |
| `utility_prune_plan` / `stele_utility_prune_plan` | α/β prune (Eq.1 shaped) |
| `extract_cheatsheet_snippet` / `stele_extract_cheatsheet_snippet` | compact snippet |
| `retrieve_cheatsheet` / `stele_retrieve_cheatsheet` | cheatsheet retrieve |
| `curator_decide` / `stele_curator_decide` | ADD/REFINE/PRUNE/KEEP |
| `compact_memory_gate` / `stele_compact_memory_gate` | forbid FH ballooning |
| `dc_rs_order_check` / `stele_dc_rs_order_check` | DC-RS vs DC-Cu order |
| `reme_cheatsheet_shaped_report` | suite harness |

Modules: `stele_core.reme` + `stele_core.cheatsheet`. MCP tool count: **395**. CLI: `multi-faceted-distill` / `scenario-retrieve` / `adaptive-rewrite` / `utility-after-reuse` / `selective-add` / `utility-prune` / `cheatsheet-snippet` / `retrieve-cheatsheet` / `curator-decide` / `compact-memory-gate` / `dc-rs-order`. Plans are **report-only**.

### 7.57 ExpeL + RMM dialogue (UC-416–427)

| API / Tool | Behavior |
|---|---|
| `experience_pool_add` / `stele_experience_pool_add` | success/failure pool entry |
| `insight_op` / `stele_insight_op` | ADD/EDIT/UPVOTE/DOWNVOTE |
| `insight_importance_gate` / `stele_insight_importance_gate` | drop at importance 0 |
| `retrieve_insights` / `stele_retrieve_insights` | insight retrieve |
| `retrieve_similar_successes` / `stele_retrieve_similar_successes` | success recall |
| `prospective_reflect` / `stele_prospective_reflect` | topic+segment memory |
| `topic_memory_bank` / `stele_topic_memory_bank` | topic index |
| `retrieve_topic_memories` / `stele_retrieve_topic_memories` | topic retrieve |
| `retrospective_cite_feedback` / `stele_retrospective_cite_feedback` | cite vs unused |
| `rerank_memories` / `stele_rerank_memories` | lightweight rerank |
| `retrieval_refine_plan` / `stele_retrieval_refine_plan` | weight update plan |
| `expel_rmm_shaped_report` | suite harness |

Modules: `stele_core.expel` + `stele_core.reflective_mm`. MCP tool count: **406**. CLI: `experience-pool-add` / `insight-op` / `insight-importance-gate` / `retrieve-insights` / `retrieve-similar-successes` / `prospective-reflect` / `topic-memory-bank` / `retrieve-topic-memories` / `retrospective-cite` / `rerank-memories` / `retrieval-refine`. Plans are **report-only**.

### 7.58 Trace2Skill + Evo-Memory (UC-428–439)

| API / Tool | Behavior |
|---|---|
| `collect_trajectory_label` / `stele_collect_trajectory_label` | labeled success/failure |
| `propose_trajectory_patch` / `stele_propose_trajectory_patch` | error/success patch |
| `parallel_patch_pool` / `stele_parallel_patch_pool` | parallel analysts |
| `hierarchical_merge_patches` / `stele_hierarchical_merge_patches` | conflict-free merge |
| `skill_mode_gate` / `stele_skill_mode_gate` | deepen vs create |
| `prefer_parallel_over_sequential` / `stele_prefer_parallel_over_sequential` | parallel preference |
| `streaming_task_append` / `stele_streaming_task_append` | stream experience |
| `exprag_retrieve` / `stele_exprag_retrieve` | ExpRAG retrieve |
| `search_predict_evolve_check` / `stele_search_predict_evolve_check` | SPE order |
| `evomem_refine_plan` / `stele_evomem_refine_plan` | ReMem refine proxy |
| `evolution_similarity_hint` / `stele_evolution_similarity_hint` | reuse-gain hint |
| `trace2skill_evomemory_shaped_report` | suite harness |

Modules: `stele_core.trace2skill` + `stele_core.evomemory`. MCP tool count: **417**. CLI: `collect-trajectory` / `propose-patch` / `parallel-patch-pool` / `merge-patches` / `skill-mode-gate` / `prefer-parallel` / `streaming-task-append` / `exprag-retrieve` / `spe-check` / `evomem-refine` / `evolution-similarity`. Plans are **report-only**.

### 7.59 Mem-α + AgentHER (UC-440–451)

| API / Tool | Behavior |
|---|---|
| `classify_memory_slot` / `stele_classify_memory_slot` | core/episodic/semantic |
| `memory_write_op` / `stele_memory_write_op` | insert/update/delete gates |
| `process_chunk_plan` / `stele_process_chunk_plan` | sequential chunk plan |
| `compression_ratio` / `stele_compression_ratio` | r3 = 1−lm/lc |
| `memalpha_reward_bundle` / `stele_memalpha_reward_bundle` | r1–r4 combine |
| `length_generalization_gate` / `stele_length_generalization_gate` | train vs eval length |
| `classify_failure` / `stele_classify_failure` | type/severity/recoverable |
| `extract_replay_outcome` / `stele_extract_replay_outcome` | achievements |
| `hindsight_relabel_plan` / `stele_hindsight_relabel_plan` | new goal + θ |
| `multi_judge_accept` / `stele_multi_judge_accept` | both judges ≥ θ |
| `package_training_pair` / `stele_package_training_pair` | SFT/DPO/ShareGPT |
| `memalpha_agenther_shaped_report` | suite harness |

Modules: `stele_core.memalpha` + `stele_core.agenther`. MCP tool count: **428**. CLI: `classify-memory-slot` / `memory-write-op` / `process-chunk` / `compression-ratio` / `memalpha-reward` / `length-gen-gate` / `classify-failure` / `replay-outcome` / `hindsight-relabel` / `multi-judge` / `package-training-pair`. Plans are **report-only**.

### 7.60 PreFlect + SkillFlow (UC-452–463)

| API / Tool | Behavior |
|---|---|
| `distill_planning_error` / `stele_distill_planning_error` | planning-error prior |
| `prospective_critique_plan` / `stele_prospective_critique_plan` | pre-exec critique |
| `revise_plan_proposal` / `stele_revise_plan_proposal` | revise before act |
| `replan_on_deviation` / `stele_replan_on_deviation` | runtime replan |
| `preflect_before_execute_gate` / `stele_preflect_before_execute_gate` | execute gate |
| `orchestration_action_select` / `stele_orchestration_action_select` | skill/act/accept |
| `ttb_residual` / `stele_ttb_residual` | TTB Δ residual |
| `step_importance` / `stele_step_importance` | I(t) credit |
| `skill_marginal_flow` / `stele_skill_marginal_flow` | F̂(s) |
| `skill_curation_decide` / `stele_skill_curation_decide` | retain/refine/prune/create |
| `phase_evolve_gate` / `stele_phase_evolve_gate` | when to evolve |
| `preflect_skillflow_shaped_report` | suite harness |

Modules: `stele_core.preflect` + `stele_core.skillflow`. MCP tool count: **439**. CLI: `distill-planning-error` / `prospective-critique` / `revise-plan` / `replan-deviation` / `preflect-gate` / `orch-action` / `ttb-residual` / `step-importance` / `skill-marginal-flow` / `skill-curation` / `phase-evolve`. Plans are **report-only**.

### 7.61 ProcMEM + MemRL (UC-464–475)

| API / Tool | Behavior |
|---|---|
| `define_skill_triplet` / `stele_define_skill_triplet` | I/π/β skill |
| `skill_select_gate` / `stele_skill_select_gate` | activate |
| `skill_terminate_check` / `stele_skill_terminate_check` | terminate |
| `semantic_gradient_candidate` / `stele_semantic_gradient_candidate` | refine proposal |
| `ppo_gate_verify` / `stele_ppo_gate_verify` | trust-region admit |
| `skill_score_maintain` / `stele_skill_score_maintain` | freq×gain keep |
| `ieu_record` / `stele_ieu_record` | Intent-Exp-Utility |
| `two_phase_retrieve` / `stele_two_phase_retrieve` | sim then Q |
| `utility_q_update` / `stele_utility_q_update` | Bellman backup |
| `value_aware_select` / `stele_value_aware_select` | max Q pick |
| `semantic_vs_utility_warn` / `stele_semantic_vs_utility_warn` | similar≠useful |
| `procmem_memrl_shaped_report` | suite harness |

Modules: `stele_core.procmem` + `stele_core.memrl`. MCP tool count: **450**. CLI: `define-skill` / `skill-select` / `skill-terminate` / `semantic-gradient` / `ppo-gate` / `skill-maintain` / `ieu-record` / `two-phase-retrieve` / `utility-q-update` / `value-aware-select` / `sim-util-warn`. Plans are **report-only**.

### 7.62 EvolveR + AgentEvolver (UC-476–487)

| API / Tool | Behavior |
|---|---|
| `distill_principle` / `stele_distill_principle` | success/failure principle |
| `principle_dedupe_plan` / `stele_principle_dedupe_plan` | merge vs add |
| `principle_metric_score` / `stele_principle_metric_score` | succ/use score |
| `search_experience_action` / `stele_search_experience_action` | online actions |
| `lifecycle_phase_gate` / `stele_lifecycle_phase_gate` | online/offline |
| `prune_low_score_principles` / `stele_prune_low_score_principles` | prune plan |
| `self_question_task` / `stele_self_question_task` | curiosity task |
| `experience_when_content` / `stele_experience_when_content` | when+content |
| `mixed_rollout_split` / `stele_mixed_rollout_split` | η guided/vanilla |
| `attribute_step_credit` / `stele_attribute_step_credit` | step credits |
| `curiosity_explore_plan` / `stele_curiosity_explore_plan` | novelty explore |
| `evolver_agentevolver_shaped_report` | suite harness |

Modules: `stele_core.evolver` + `stele_core.agentevolver`. MCP tool count: **461**. CLI: `distill-principle` / `principle-dedupe` / `principle-score` / `search-exp-action` / `lifecycle-phase` / `prune-principles` / `self-question` / `exp-when-content` / `mixed-rollout` / `attribute-credit` / `curiosity-explore`. Plans are **report-only**.

### 7.63 SkillWeaver + SkillRoute (UC-488–499)

| API / Tool | Behavior |
|---|---|
| `propose_skill` / `stele_propose_skill` | skill proposal |
| `practice_skill_run` / `stele_practice_skill_run` | practice |
| `distill_skill_api` / `stele_distill_skill_api` | API distill |
| `hone_skill_api` / `stele_hone_skill_api` | unit-test gate |
| `skill_library_register` / `stele_skill_library_register` | library grow |
| `transfer_skill_gate` / `stele_transfer_skill_gate` | strong→weak |
| `decompose_task_steps` / `stele_decompose_task_steps` | decompose |
| `retrieve_skills_for_steps` / `stele_retrieve_skills_for_steps` | retrieve |
| `compose_skill_dag` / `stele_compose_skill_dag` | DAG compose |
| `sad_feedback_loop` / `stele_sad_feedback_loop` | SAD revise |
| `granularity_match_check` / `stele_granularity_match_check` | DA match |
| `skillweaver_skillroute_shaped_report` | suite harness |

Modules: `stele_core.skillweaver` + `stele_core.skillroute`. MCP tool count: **472**. CLI: `propose-skill` / `practice-skill` / `distill-skill-api` / `hone-skill-api` / `skill-library-reg` / `transfer-skill` / `decompose-task` / `retrieve-step-skills` / `compose-skill-dag` / `sad-loop` / `granularity-match`. Plans are **report-only**.

### 7.64 Absolute Zero + R-Zero (UC-500–511)

| API / Tool | Behavior |
|---|---|
| `propose_reasoning_task` / `stele_propose_reasoning_task` | induction/abduction/deduction |
| `validate_task_structure` / `stele_validate_task_structure` | triplet validity |
| `learnability_reward` / `stele_learnability_reward` | 1−mean_solve |
| `solve_reward` / `stele_solve_reward` | binary match |
| `abszero_joint_objective` / `stele_abszero_joint_objective` | λ propose + solve |
| `executor_verify_gate` / `stele_executor_verify_gate` | env verifier |
| `challenger_propose` / `stele_challenger_propose` | synthetic Q |
| `uncertainty_reward` / `stele_uncertainty_reward` | edge @ 50% |
| `majority_vote_label` / `stele_majority_vote_label` | pseudo-label |
| `curriculum_band_filter` / `stele_curriculum_band_filter` | \|p−½\|≤δ |
| `solver_binary_reward` / `stele_solver_binary_reward` | match label |
| `coevolve_round_plan` / `stele_coevolve_round_plan` | Challenger→Solver |
| `abszero_rzero_shaped_report` | suite harness |

Modules: `stele_core.abszero` + `stele_core.rzero`. MCP tool count: **484**. CLI: `propose-reason-task` / `validate-task-struct` / `learnability-reward` / `solve-reward` / `abszero-objective` / `executor-verify` / `challenger-propose` / `uncertainty-reward` / `majority-vote` / `curriculum-band` / `solver-reward` / `coevolve-round`. Plans are **report-only**.

### 7.65 ECHO + Agent0 (UC-512–523)

| API / Tool | Behavior |
|---|---|
| `write_turn_memory` / `stele_write_turn_memory` | source-indexed finding |
| `select_turn_memories` / `stele_select_turn_memories` | budgeted select |
| `reconstruct_policy_context` / `stele_reconstruct_policy_context` | bounded reconstruct |
| `provenance_credit_mask` / `stele_provenance_credit_mask` | credit via selected sources |
| `history_collapse_gate` / `stele_history_collapse_gate` | reject summary-only collapse |
| `budget_binding_check` / `stele_budget_binding_check` | when budget binds |
| `curriculum_propose_task` / `stele_curriculum_propose_task` | frontier task |
| `tool_use_reward` / `stele_tool_use_reward` | γ·min(N,C) |
| `curriculum_reward` / `stele_curriculum_reward` | unc+tool−rep |
| `executor_frontier_filter` / `stele_executor_frontier_filter` | consistency band |
| `tool_aware_pressure` / `stele_tool_aware_pressure` | raise complexity |
| `symbiotic_round_plan` / `stele_symbiotic_round_plan` | curriculum→executor |
| `echomem_agent0_shaped_report` | suite harness |

Modules: `stele_core.echomem` + `stele_core.agent0`. MCP tool count: **496**. CLI: `write-turn-mem` / `select-turn-mem` / `reconstruct-ctx` / `credit-mask` / `collapse-gate` / `budget-binding` / `curriculum-task` / `tool-use-reward` / `curriculum-reward` / `executor-frontier` / `tool-pressure` / `symbiotic-round`. Plans are **report-only**.

### 7.66 MAE + SAGE (UC-524–535)

| API / Tool | Behavior |
|---|---|
| `mae_propose_question` / `stele_mae_propose_question` | Proposer Q |
| `mae_solve_attempt` / `stele_mae_solve_attempt` | Solver answer |
| `mae_judge_score` / `stele_mae_judge_score` | quality + correctness |
| `mae_proposer_reward` / `stele_mae_proposer_reward` | quality + fail bonus |
| `mae_quality_filter` / `stele_mae_quality_filter` | quality floor |
| `mae_triad_round_plan` / `stele_mae_triad_round_plan` | propose→solve→judge |
| `sage_challenge_task` / `stele_sage_challenge_task` | Challenger task |
| `sage_plan_steps` / `stele_sage_plan_steps` | Planner steps |
| `sage_solve_with_plan` / `stele_sage_solve_with_plan` | plan fidelity |
| `sage_critic_filter` / `stele_sage_critic_filter` | Q+plan scores |
| `sage_drift_gate` / `stele_sage_drift_gate` | reject hard jumps |
| `sage_closed_loop_round` / `stele_sage_closed_loop_round` | challenge→…→criticize |
| `mae_sagema_shaped_report` | suite harness |

Modules: `stele_core.mae` + `stele_core.sagema`. MCP tool count: **508**. CLI: `mae-propose` / `mae-solve` / `mae-judge` / `mae-proposer-reward` / `mae-quality-filter` / `mae-triad` / `sage-challenge` / `sage-plan` / `sage-solve` / `sage-critic` / `sage-drift` / `sage-loop`. Plans are **report-only**.

### 7.67 MemGen + Metis (UC-536–547)

| API / Tool | Behavior |
|---|---|
| `memory_trigger_decide` / `stele_memory_trigger_decide` | INVOKE/SKIP |
| `weave_latent_memory` / `stele_weave_latent_memory` | latent tokens |
| `interweave_cycle_plan` / `stele_interweave_cycle_plan` | reason↔memory |
| `faculty_classify` / `stele_faculty_classify` | planning/procedural/working |
| `weaver_only_update_gate` / `stele_weaver_only_update_gate` | freeze reasoner |
| `sparse_invoke_penalty` / `stele_sparse_invoke_penalty` | sparse trigger |
| `text_experience_store` / `stele_text_experience_store` | plan/fact/pitfall |
| `crystallize_plan_to_tool` / `stele_crystallize_plan_to_tool` | reuse→tool |
| `dual_retrieve` / `stele_dual_retrieve` | text+code |
| `representation_tradeoff` / `stele_representation_tradeoff` | cost/eff/transfer |
| `promote_kind_gate` / `stele_promote_kind_gate` | plans only |
| `metis_loop_plan` / `stele_metis_loop_plan` | reflect→act |
| `memgen_metis_shaped_report` | suite harness |

Modules: `stele_core.memgen` + `stele_core.metis`. MCP tool count: **520**. CLI: `mem-trigger` / `weave-latent` / `interweave` / `faculty` / `weaver-gate` / `sparse-invoke` / `text-experience` / `crystallize` / `dual-retrieve` / `rep-tradeoff` / `promote-kind` / `metis-loop`. Plans are **report-only**.

### 7.68 SAMULE + LIVE-EVO (UC-548–559)

| API / Tool | Behavior |
|---|---|
| `single_trajectory_reflect` / `stele_single_trajectory_reflect` | micro |
| `intra_task_taxonomy` / `stele_intra_task_taxonomy` | meso |
| `inter_task_transfer` / `stele_inter_task_transfer` | macro |
| `foresight_reflect` / `stele_foresight_reflect` | predict≠actual |
| `failure_centric_gate` / `stele_failure_centric_gate` | prefer failures |
| `merge_reflections` / `stele_merge_reflections` | merge levels |
| `experience_bank_record` / `stele_experience_bank_record` | Experience Bank |
| `meta_guideline_record` / `stele_meta_guideline_record` | Meta-Guideline Bank |
| `compile_task_guideline` / `stele_compile_task_guideline` | task-adaptive |
| `update_experience_weight` / `stele_update_experience_weight` | contrastive |
| `forget_stale_experience` / `stele_forget_stale_experience` | decay |
| `liveevo_online_round` / `stele_liveevo_online_round` | retrieve→update |
| `samule_liveevo_shaped_report` | suite harness |

Modules: `stele_core.samule` + `stele_core.liveevo`. MCP tool count: **532**. CLI: `samule-micro` / `samule-meso` / `samule-macro` / `samule-foresight` / `samule-fail-gate` / `samule-merge` / `liveevo-exp` / `liveevo-meta` / `liveevo-compile` / `liveevo-weight` / `liveevo-forget` / `liveevo-round`. Plans are **report-only**.

### 7.69 Socratic-Zero + SPIRAL (UC-560–571)

| API / Tool | Behavior |
|---|---|
| `socratic_teacher_craft` / `stele_socratic_teacher_craft` | weakness→Q |
| `socratic_solver_preference` / `stele_socratic_solver_preference` | win/fail pref |
| `socratic_generator_distill` / `stele_socratic_generator_distill` | distill Teacher |
| `socratic_seed_bootstrap` / `stele_socratic_seed_bootstrap` | min seeds |
| `socratic_weakness_target` / `stele_socratic_weakness_target` | fail_rate gate |
| `socratic_closed_loop` / `stele_socratic_closed_loop` | teach→distill |
| `spiral_self_play_match` / `stele_spiral_self_play_match` | zero-sum match |
| `spiral_rae_advantage` / `stele_spiral_rae_advantage` | reward−baseline |
| `spiral_baseline_ema` / `stele_spiral_baseline_ema` | role EMA |
| `spiral_transfer_pattern` / `stele_spiral_transfer_pattern` | cognitive pattern |
| `spiral_opponent_strength` / `stele_spiral_opponent_strength` | curriculum |
| `spiral_multi_game_plan` / `stele_spiral_multi_game_plan` | match→transfer |
| `socratic_spiral_shaped_report` | suite harness |

Modules: `stele_core.socratic` + `stele_core.spiral`. MCP tool count: **544**. CLI: `socratic-teach` / `socratic-prefer` / `socratic-distill` / `socratic-seed` / `socratic-weakness` / `socratic-loop` / `spiral-match` / `spiral-rae` / `spiral-ema` / `spiral-pattern` / `spiral-opponent` / `spiral-plan`. Plans are **report-only**.

### 7.70 SMITH + H-Mem (UC-572–583)

| API / Tool | Behavior |
|---|---|
| `smith_store_memory` / `stele_smith_store_memory` | procedural/semantic/episodic |
| `smith_create_tool` / `stele_smith_create_tool` | sandbox admit |
| `smith_retrieve_episode` / `stele_smith_retrieve_episode` | similarity > θ |
| `smith_curriculum_difficulty` / `stele_smith_curriculum_difficulty` | ensemble band |
| `smith_tool_reuse_gate` / `stele_smith_tool_reuse_gate` | reuse vs create |
| `smith_loop_plan` / `stele_smith_loop_plan` | store→act |
| `hmem_leaf_event` / `stele_hmem_leaf_event` | STM leaf |
| `hmem_consolidate_nodes` / `stele_hmem_consolidate_nodes` | STM→LTM |
| `hmem_link_entities` / `stele_hmem_link_entities` | graph edge |
| `hmem_decompose_query` / `stele_hmem_decompose_query` | sub-queries |
| `hmem_hybrid_retrieve` / `stele_hmem_hybrid_retrieve` | tree+graph |
| `hmem_evolution_gate` / `stele_hmem_evolution_gate` | evolution ratio |
| `smith_hmem_shaped_report` | suite harness |

Modules: `stele_core.smith` + `stele_core.hmem`. MCP tool count: **556**. CLI: `smith-store` / `smith-tool` / `smith-episode` / `smith-curriculum` / `smith-reuse` / `smith-loop` / `hmem-leaf` / `hmem-consolidate` / `hmem-link` / `hmem-decompose` / `hmem-hybrid` / `hmem-evolution`. Plans are **report-only**.

### 7.71 HiMem + H-MEM levels (UC-584–595)

| API / Tool | Behavior |
|---|---|
| `himem_segment_episode` / `stele_himem_segment_episode` | topic + surprise boundary |
| `himem_extract_note` / `stele_himem_extract_note` | Note Memory |
| `himem_link_episode_note` / `stele_himem_link_episode_note` | episode↔note |
| `himem_retrieve_strategy` / `stele_himem_retrieve_strategy` | hybrid / best_effort |
| `himem_reconsolidate` / `stele_himem_reconsolidate` | conflict-aware revise |
| `himem_loop_plan` / `stele_himem_loop_plan` | construct→reconsolidate |
| `hmeml_store_level` / `stele_hmeml_store_level` | section→content |
| `hmeml_route_query` / `stele_hmeml_route_query` | index path |
| `hmeml_descend` / `stele_hmeml_descend` | miss → descend |
| `hmeml_parent_link` / `stele_hmeml_parent_link` | adjacency |
| `hmeml_efficiency_score` / `stele_hmeml_efficiency_score` | scan economy |
| `hmeml_loop_plan` / `stele_hmeml_loop_plan` | store→score |
| `himem_hmeml_shaped_report` | suite harness |

Modules: `stele_core.himem` + `stele_core.hmeml`. MCP tool count: **568**. CLI: `himem-segment` / `himem-note` / `himem-link` / `himem-retrieve` / `himem-reconsolidate` / `himem-loop` / `hmeml-store` / `hmeml-route` / `hmeml-descend` / `hmeml-parent` / `hmeml-efficiency` / `hmeml-loop`. Distinct from hybrid `hmem.py` (2605.15701). Plans are **report-only**.

### 7.72 HyperSkill + DCPM (UC-596–608)

| API / Tool | Behavior |
|---|---|
| `hyperskill_add_subtask` / `stele_hyperskill_add_subtask` | subtask node |
| `hyperskill_add_skill` / `stele_hyperskill_add_skill` | skill node |
| `hyperskill_add_hyperedge` / `stele_hyperskill_add_hyperedge` | n-ary trajectory edge |
| `hyperskill_dual_path_retrieve` / `stele_hyperskill_dual_path_retrieve` | subtask+trajectory |
| `hyperskill_rank_skills` / `stele_hyperskill_rank_skills` | co-occurrence × utility |
| `hyperskill_maintain_plan` / `stele_hyperskill_maintain_plan` | prune/merge plan |
| `hyperskill_loop_plan` / `stele_hyperskill_loop_plan` | store→maintain |
| `dcpm_day_write` / `stele_dcpm_day_write` | System-1 belief write |
| `dcpm_supersedes_chain` / `stele_dcpm_supersedes_chain` | revision chain |
| `dcpm_night_induce` / `stele_dcpm_night_induce` | System-2 schema induce |
| `dcpm_cross_domain_collision` / `stele_dcpm_cross_domain_collision` | core-schema abstract |
| `dcpm_hierarchy_level` / `stele_dcpm_hierarchy_level` | capability level |
| `dcpm_loop_plan` / `stele_dcpm_loop_plan` | day→collision |
| `hyperskill_dcpm_shaped_report` | suite harness |

Modules: `stele_core.hyperskill` + `stele_core.dcpm`. MCP tool count: **581**. CLI: `hyperskill-subtask` / `hyperskill-skill` / `hyperskill-hyperedge` / `hyperskill-dual` / `hyperskill-rank` / `hyperskill-maintain` / `hyperskill-loop` / `dcpm-day` / `dcpm-chain` / `dcpm-night` / `dcpm-collision` / `dcpm-level` / `dcpm-loop`. Distinct from D-Mem quality gate in `roles.py`. Plans are **report-only**.

### 7.73 MemOS + SkillCraft (UC-609–622)

| API / Tool | Behavior |
|---|---|
| `memos_create_cube` / `stele_memos_create_cube` | MemCube unit |
| `memos_schedule` / `stele_memos_schedule` | LRU/semantic/label |
| `memos_lifecycle` / `stele_memos_lifecycle` | freeze/thaw/migrate/fuse |
| `memos_compose` / `stele_memos_compose` | compose cubes |
| `memos_migrate` / `stele_memos_migrate` | kind transition plan |
| `memos_fuse_gate` / `stele_memos_fuse_gate` | fuse admit |
| `memos_loop_plan` / `stele_memos_loop_plan` | create→compose |
| `skillcraft_save_skill` / `stele_skillcraft_save_skill` | verified save |
| `skillcraft_get_skill` / `stele_skillcraft_get_skill` | get by id |
| `skillcraft_list_skills` / `stele_skillcraft_list_skills` | library size |
| `skillcraft_execute_skill` / `stele_skillcraft_execute_skill` | cached invoke |
| `skillcraft_verify_skill` / `stele_skillcraft_verify_skill` | coding verifier |
| `skillcraft_token_efficiency` / `stele_skillcraft_token_efficiency` | reduction ratio |
| `skillcraft_loop_plan` / `stele_skillcraft_loop_plan` | explore→execute |
| `memos_skillcraft_shaped_report` | suite harness |

Modules: `stele_core.memos` + `stele_core.skillcraft`. MCP tool count: **595**. CLI: `memos-*` / `skillcraft-*`. No live sandbox / parameter writes on core. Plans are **report-only**.

### 7.74 CMA + AgentFold (UC-623–635)

| API / Tool | Behavior |
|---|---|
| `cma_persist` / `stele_cma_persist` | mutable persist |
| `cma_selective_retain` / `stele_cma_selective_retain` | retain gate |
| `cma_associative_route` / `stele_cma_associative_route` | cue hops |
| `cma_temporal_chain` / `stele_cma_temporal_chain` | event order |
| `cma_consolidate` / `stele_cma_consolidate` | abstraction |
| `cma_probe_gate` / `stele_cma_probe_gate` | behavioral probes |
| `cma_loop_plan` / `stele_cma_loop_plan` | persist→consolidate |
| `agentfold_workspace_split` / `stele_agentfold_workspace_split` | working vs LTM |
| `agentfold_fold_command` / `stele_agentfold_fold_command` | granular/deep |
| `agentfold_granular_condense` / `stele_agentfold_granular_condense` | last-step compress |
| `agentfold_deep_consolidate` / `stele_agentfold_deep_consolidate` | multi-block merge |
| `agentfold_context_budget` / `stele_agentfold_context_budget` | soft cap |
| `agentfold_loop_plan` / `stele_agentfold_loop_plan` | act→budget |
| `cma_agentfold_shaped_report` | suite harness |

Modules: `stele_core.cma` + `stele_core.agentfold`. MCP tool count: **608**. CLI: `cma-*` / `agentfold-*`. Plans are **report-only**.

### 7.75 MemEngine + SimpleMem (UC-636–648)

| API / Tool | Behavior |
|---|---|
| `memengine_register_function` / `stele_memengine_register_function` | level-0 function |
| `memengine_compose_operation` / `stele_memengine_compose_operation` | level-1 op |
| `memengine_bind_model` / `stele_memengine_bind_model` | level-2 model |
| `memengine_config_set` / `stele_memengine_config_set` | hyper-params |
| `memengine_reflect_plan` / `stele_memengine_reflect_plan` | reflect gate |
| `memengine_pluggable` / `stele_memengine_pluggable` | plug-and-play |
| `memengine_loop_plan` / `stele_memengine_loop_plan` | function→reflect |
| `simplemem_compress` / `stele_simplemem_compress` | structured units |
| `simplemem_synthesize` / `stele_simplemem_synthesize` | online merge |
| `simplemem_intent_scope` / `stele_simplemem_intent_scope` | adaptive k |
| `simplemem_multiview_index` / `stele_simplemem_multiview_index` | dense/sparse/meta |
| `simplemem_token_ratio` / `stele_simplemem_token_ratio` | reduction factor |
| `simplemem_loop_plan` / `stele_simplemem_loop_plan` | compress→retrieve |
| `memengine_simplemem_shaped_report` | suite harness |

Modules: `stele_core.memengine` + `stele_core.simplemem`. MCP tool count: **621**. CLI: `memengine-*` / `simplemem-*`. Plans are **report-only**.

### 7.76 O-Mem + Mandol (UC-649–661)

| API / Tool | Behavior |
|---|---|
| `omem_extract_persona` / `stele_omem_extract_persona` | persona trait |
| `omem_update_event` / `stele_omem_update_event` | event record |
| `omem_hierarchy_retrieve` / `stele_omem_hierarchy_retrieve` | persona/topic |
| `omem_profile_gate` / `stele_omem_profile_gate` | confidence admit |
| `omem_scale_memory_time` / `stele_omem_scale_memory_time` | density |
| `omem_loop_plan` / `stele_omem_loop_plan` | extract→gate |
| `mandol_basic_unit` / `stele_mandol_basic_unit` | basic layer |
| `mandol_agglomerate` / `stele_mandol_agglomerate` | abstract layer |
| `mandol_semantic_map_put` / `stele_mandol_semantic_map_put` | fused map |
| `mandol_hybrid_retrieve` / `stele_mandol_hybrid_retrieve` | no cross-DB I/O |
| `mandol_query_route` / `stele_mandol_query_route` | adaptive route |
| `mandol_token_budget` / `stele_mandol_token_budget` | token cap |
| `mandol_loop_plan` / `stele_mandol_loop_plan` | basic→budget |
| `omem_mandol_shaped_report` | suite harness |

Modules: `stele_core.omem` + `stele_core.mandol`. MCP tool count: **634**. CLI: `omem-*` / `mandol-*`. Plans are **report-only**.

### 7.77 Memanto + Zep (UC-662–673)

| API / Tool | Behavior |
|---|---|
| `memanto_store_typed` / `stele_memanto_store_typed` | 13 categories |
| `memanto_conflict_resolve` / `stele_memanto_conflict_resolve` | newer/older |
| `memanto_version` / `stele_memanto_version` | temporal versions |
| `memanto_retrieve` / `stele_memanto_retrieve` | single-query |
| `memanto_latency_gate` / `stele_memanto_latency_gate` | ≤90ms soft |
| `memanto_loop_plan` / `stele_memanto_loop_plan` | store→conflict |
| `zep_add_episode` / `stele_zep_add_episode` | temporal episode |
| `zep_link_entities` / `stele_zep_link_entities` | graph edge |
| `zep_bitemporal` / `stele_zep_bitemporal` | valid vs txn time |
| `zep_synthesize` / `stele_zep_synthesize` | convo+business |
| `zep_cross_session` / `stele_zep_cross_session` | multi-session |
| `zep_loop_plan` / `stele_zep_loop_plan` | episode→retrieve |
| `memanto_zep_shaped_report` | suite harness |

Modules: `stele_core.memanto` + `stele_core.zep`. MCP tool count: **646**. CLI: `memanto-*` / `zep-*`. No live Graphiti broker. Plans are **report-only**.

### 7.78 MemGPT + RippleMem (UC-674–685)

| API / Tool | Behavior |
|---|---|
| `memgpt_main_capacity` / `stele_memgpt_main_capacity` | warn/flush gate |
| `memgpt_page_out` / `stele_memgpt_page_out` | recall/archival eviction |
| `memgpt_page_in` / `stele_memgpt_page_in` | page fault load |
| `memgpt_recall_search` / `stele_memgpt_recall_search` | recall hits |
| `memgpt_archival_search` / `stele_memgpt_archival_search` | paginated archival |
| `memgpt_loop_plan` / `stele_memgpt_loop_plan` | capacity→search |
| `ripple_store_episode` / `stele_ripple_store_episode` | episodic unit |
| `ripple_link_entity` / `stele_ripple_link_entity` | entity graph edge |
| `ripple_seed_retrieve` / `stele_ripple_seed_retrieve` | first-shot seeds |
| `ripple_expand` / `stele_ripple_expand` | associative hops |
| `ripple_recollect_gate` / `stele_ripple_recollect_gate` | completeness |
| `ripple_loop_plan` / `stele_ripple_loop_plan` | store→recollect |
| `memgpt_ripple_shaped_report` | suite harness |

Modules: `stele_core.memgpt` + `stele_core.ripplemem`. MCP tool count: **658**. CLI: `memgpt-*` / `ripple-*`. Distinct from MemoryOS paging. Plans are **report-only**.

### 7.79 FluxMem + QUMem (UC-686–698)

| API / Tool | Behavior |
|---|---|
| `flux_connect_form` / `stele_flux_connect_form` | form edge |
| `flux_feedback_refine` / `stele_flux_feedback_refine` | feedback keep |
| `flux_consolidate` / `stele_flux_consolidate` | procedural circuits |
| `flux_repair_link` / `stele_flux_repair_link` | repair missing |
| `flux_prune_interference` / `stele_flux_prune_interference` | prune noise |
| `flux_maturity_gate` / `stele_flux_maturity_gate` | maturity metric |
| `flux_loop_plan` / `stele_flux_loop_plan` | connect→mature |
| `qumem_segment_episode` / `stele_qumem_segment_episode` | continuity episode |
| `qumem_decompose` / `stele_qumem_decompose` | factual/pref/insight |
| `qumem_plan_queries` / `stele_qumem_plan_queries` | multi-query plan |
| `qumem_infer_user_state` / `stele_qumem_infer_user_state` | user state |
| `qumem_temporal_valid` / `stele_qumem_temporal_valid` | stale gate |
| `qumem_loop_plan` / `stele_qumem_loop_plan` | segment→infer |
| `fluxmem_qumem_shaped_report` | suite harness |

Modules: `stele_core.fluxmem` + `stele_core.qumem`. MCP tool count: **671**. CLI: `flux-*` / `qumem-*`. Plans are **report-only**.

### 7.80 VikingMem + RecMem (UC-699–710)

| API / Tool | Behavior |
|---|---|
| `viking_extract_event` / `stele_viking_extract_event` | selective event |
| `viking_update_entity` / `stele_viking_update_entity` | entity evolution |
| `viking_timeline_compress` / `stele_viking_timeline_compress` | topic timeline |
| `viking_time_weighted_recall` / `stele_viking_time_weighted_recall` | recency recall |
| `viking_rerank` / `stele_viking_rerank` | multi-vector top-k |
| `viking_loop_plan` / `stele_viking_loop_plan` | extract→recall |
| `recmem_buffer_subconscious` / `stele_recmem_buffer_subconscious` | subconscious buffer |
| `recmem_recurrence_gate` / `stele_recmem_recurrence_gate` | recurrence trigger |
| `recmem_consolidate_episodic` / `stele_recmem_consolidate_episodic` | episodic plan |
| `recmem_semantic_refine` / `stele_recmem_semantic_refine` | recover facts |
| `recmem_merge_retrieve` / `stele_recmem_merge_retrieve` | three-tier merge |
| `recmem_loop_plan` / `stele_recmem_loop_plan` | buffer→refine |
| `vikingmem_recmem_shaped_report` | suite harness |

Modules: `stele_core.vikingmem` + `stele_core.recmem`. MCP tool count: **683**. CLI: `viking-*` / `recmem-*`. Plans are **report-only**.

### 7.81 MemoryBank + RF-Mem (UC-711–722)

| API / Tool | Behavior |
|---|---|
| `mbank_store_memory` / `stele_mbank_store_memory` | store + significance |
| `mbank_summon` / `stele_mbank_summon` | summon relevant |
| `mbank_personality_synth` / `stele_mbank_personality_synth` | personality |
| `mbank_forget_curve` / `stele_mbank_forget_curve` | Ebbinghaus fade plan |
| `mbank_reinforce` / `stele_mbank_reinforce` | reinforce after recall |
| `mbank_loop_plan` / `stele_mbank_loop_plan` | store→forget |
| `rfmem_familiarity_score` / `stele_rfmem_familiarity_score` | mean+entropy |
| `rfmem_path_route` / `stele_rfmem_path_route` | familiar vs recollect |
| `rfmem_top_k_familiar` / `stele_rfmem_top_k_familiar` | top-K path |
| `rfmem_recollect_expand` / `stele_rfmem_recollect_expand` | cluster hops |
| `rfmem_alpha_mix` / `stele_rfmem_alpha_mix` | alpha-mix proxy |
| `rfmem_loop_plan` / `stele_rfmem_loop_plan` | score→mix |
| `memorybank_rfmem_shaped_report` | suite harness |

Modules: `stele_core.memorybank` + `stele_core.rfmem`. MCP tool count: **695**. CLI: `mbank-*` / `rfmem-*`. Forget plans are **report-only** (no auto-delete).

### 7.82 AgeMem + MemGAS (UC-723–734)

| API / Tool | Behavior |
|---|---|
| `agemem_ltm_store` / `stele_agemem_ltm_store` | LTM/STM store tool |
| `agemem_stm_manage` / `stele_agemem_stm_manage` | STM capacity |
| `agemem_retrieve` / `stele_agemem_retrieve` | unified retrieve |
| `agemem_summarize` / `stele_agemem_summarize` | summarize plan |
| `agemem_discard_plan` / `stele_agemem_discard_plan` | discard plan |
| `agemem_loop_plan` / `stele_agemem_loop_plan` | store→summarize |
| `memgas_unit` / `stele_memgas_unit` | multi-granularity unit |
| `memgas_associate` / `stele_memgas_associate` | cluster associate |
| `memgas_entropy_route` / `stele_memgas_entropy_route` | entropy router |
| `memgas_select_granularity` / `stele_memgas_select_granularity` | choose grain |
| `memgas_filter_plan` / `stele_memgas_filter_plan` | filter plan |
| `memgas_loop_plan` / `stele_memgas_loop_plan` | unit→select |
| `agemem_memgas_shaped_report` | suite harness |

Modules: `stele_core.agemem` + `stele_core.memgas`. MCP tool count: **707**. CLI: `agemem-*` / `memgas-*`. Discard/summarize/filter plans are **report-only**.

### 7.83 MemWalker + MemGraphRAG (UC-735–746)

| API / Tool | Behavior |
|---|---|
| `memwalker_segment` / `stele_memwalker_segment` | chunk long text |
| `memwalker_build_node` / `stele_memwalker_build_node` | summary tree node |
| `memwalker_navigate` / `stele_memwalker_navigate` | child/revert/stay |
| `memwalker_gather` / `stele_memwalker_gather` | leaf budget |
| `memwalker_path_gate` / `stele_memwalker_path_gate` | depth gate |
| `memwalker_loop_plan` / `stele_memwalker_loop_plan` | segment→gather |
| `mgr_store_layer` / `stele_mgr_store_layer` | ontology/fact/passage |
| `mgr_detect_conflict` / `stele_mgr_detect_conflict` | conflict detect |
| `mgr_resolve_plan` / `stele_mgr_resolve_plan` | resolve plan |
| `mgr_multilayer_retrieve` / `stele_mgr_multilayer_retrieve` | multi-layer retrieve |
| `mgr_propagate` / `stele_mgr_propagate` | PPR-style propagate |
| `mgr_loop_plan` / `stele_mgr_loop_plan` | store→propagate |
| `memwalker_memgraphrag_shaped_report` | suite harness |

Modules: `stele_core.memwalker` + `stele_core.memgraphrag`. MCP tool count: **719**. CLI: `memwalker-*` / `mgr-*`. Resolve plans are **report-only**.

### 7.84 RAPTOR + LightRAG (UC-747–758)

| API / Tool | Behavior |
|---|---|
| `raptor_embed_chunk` / `stele_raptor_embed_chunk` | leaf chunk id |
| `raptor_cluster` / `stele_raptor_cluster` | cluster leaves |
| `raptor_summarize_node` / `stele_raptor_summarize_node` | recursive summary |
| `raptor_tree_traverse` / `stele_raptor_tree_traverse` | layer prune |
| `raptor_collapsed_retrieve` / `stele_raptor_collapsed_retrieve` | all-layer top-k |
| `raptor_loop_plan` / `stele_raptor_loop_plan` | embed→retrieve |
| `lightrag_index_entity` / `stele_lightrag_index_entity` | entity index |
| `lightrag_index_relation` / `stele_lightrag_index_relation` | relation edge |
| `lightrag_dual_retrieve` / `stele_lightrag_dual_retrieve` | low/high/both |
| `lightrag_incremental_update` / `stele_lightrag_incremental_update` | incremental |
| `lightrag_graph_vector_fuse` / `stele_lightrag_graph_vector_fuse` | fuse hits |
| `lightrag_loop_plan` / `stele_lightrag_loop_plan` | index→update |
| `raptor_lightrag_shaped_report` | suite harness |

Modules: `stele_core.raptor` + `stele_core.lightrag`. MCP tool count: **731**. CLI: `raptor-*` / `lightrag-*`. Summarize plans are **report-only**.

### 7.85 MemoRAG + PageIndex (UC-759–770)

| API / Tool | Behavior |
|---|---|
| `memorag_memorize` / `stele_memorag_memorize` | global memory |
| `memorag_clue` / `stele_memorag_clue` | draft clues |
| `memorag_retrieve_by_clue` / `stele_memorag_retrieve_by_clue` | clue retrieve |
| `memorag_dual_system` / `stele_memorag_dual_system` | memory/generator |
| `memorag_generate_plan` / `stele_memorag_generate_plan` | answer plan |
| `memorag_loop_plan` / `stele_memorag_loop_plan` | memorize→generate |
| `pageindex_build_toc` / `stele_pageindex_build_toc` | TOC tree |
| `pageindex_add_section` / `stele_pageindex_add_section` | natural section |
| `pageindex_reason_nav` / `stele_pageindex_reason_nav` | reason over TOC |
| `pageindex_select_section` / `stele_pageindex_select_section` | keep/prune |
| `pageindex_trace_path` / `stele_pageindex_trace_path` | traceable path |
| `pageindex_loop_plan` / `stele_pageindex_loop_plan` | toc→select |
| `memorag_pageindex_shaped_report` | suite harness |

Modules: `stele_core.memorag` + `stele_core.pageindex`. MCP tool count: **743**. CLI: `memorag-*` / `pageindex-*`. Generate plans are **report-only**. No vector DB on core.

### 7.86 Self-RAG + MemoBrain (UC-771–782)

| API / Tool | Behavior |
|---|---|
| `selfrag_need_retrieve` / `stele_selfrag_need_retrieve` | on-demand retrieve decide |
| `selfrag_relevance_critique` / `stele_selfrag_relevance_critique` | relevance token |
| `selfrag_support_critique` / `stele_selfrag_support_critique` | support token |
| `selfrag_utility_critique` / `stele_selfrag_utility_critique` | utility score |
| `selfrag_select_best` / `stele_selfrag_select_best` | best continuation |
| `selfrag_loop_plan` / `stele_selfrag_loop_plan` | decide→generate |
| `memobrain_dep_edge` / `stele_memobrain_dep_edge` | dependency edge |
| `memobrain_prune_invalid` / `stele_memobrain_prune_invalid` | prune invalid (report-only) |
| `memobrain_fold_subtraj` / `stele_memobrain_fold_subtraj` | fold sub-trajectory |
| `memobrain_flush_budget` / `stele_memobrain_flush_budget` | budget flush plan |
| `memobrain_salience_keep` / `stele_memobrain_salience_keep` | salience keep |
| `memobrain_loop_plan` / `stele_memobrain_loop_plan` | dep→flush |
| `selfrag_memobrain_shaped_report` | suite harness |

Modules: `stele_core.selfrag` + `stele_core.memobrain`. MCP tool count: **755**. CLI: `selfrag-*` / `memobrain-*`. Prune/flush/fold plans are **report-only**.

### 7.87 CRAG + HyDE (UC-783–794)

| API / Tool | Behavior |
|---|---|
| `crag_evaluate_retrieval` / `stele_crag_evaluate_retrieval` | Correct/Incorrect/Ambiguous |
| `crag_correct_refine` / `stele_crag_correct_refine` | decompose-recompose |
| `crag_web_fallback_plan` / `stele_crag_web_fallback_plan` | web plan (no live net) |
| `crag_ambiguous_blend` / `stele_crag_ambiguous_blend` | local+web blend |
| `crag_action_select` / `stele_crag_action_select` | action echo |
| `crag_loop_plan` / `stele_crag_loop_plan` | evaluate→blend |
| `hyde_hypothetical_doc` / `stele_hyde_hypothetical_doc` | hyp doc from query |
| `hyde_encode_proxy` / `stele_hyde_encode_proxy` | encode proxy |
| `hyde_retrieve_by_hyp` / `stele_hyde_retrieve_by_hyp` | hyp neighborhood |
| `hyde_filter_hallucination` / `stele_hyde_filter_hallucination` | dense filter |
| `hyde_ground_corpus` / `stele_hyde_ground_corpus` | ground to corpus |
| `hyde_loop_plan` / `stele_hyde_loop_plan` | hyp→ground |
| `crag_hyde_shaped_report` | suite harness |

Modules: `stele_core.crag` + `stele_core.hyde`. MCP tool count: **767**. CLI: `crag-*` / `hyde-*`. Web fallback is **report-only**. No live LLM/Contriever on core.

### 7.88 Adaptive-RAG + FLARE (UC-795–806)

| API / Tool | Behavior |
|---|---|
| `adaptiverag_classify_complexity` / `stele_adaptiverag_classify_complexity` | hops → level |
| `adaptiverag_select_strategy` / `stele_adaptiverag_select_strategy` | no/single/multi |
| `adaptiverag_no_retrieve` / `stele_adaptiverag_no_retrieve` | parametric path |
| `adaptiverag_single_step` / `stele_adaptiverag_single_step` | one-shot retrieve |
| `adaptiverag_multi_step` / `stele_adaptiverag_multi_step` | iterative |
| `adaptiverag_loop_plan` / `stele_adaptiverag_loop_plan` | classify→adapt |
| `flare_anticipate_sentence` / `stele_flare_anticipate_sentence` | forward look |
| `flare_low_confidence` / `stele_flare_low_confidence` | low-token gate |
| `flare_retrieve_for_regen` / `stele_flare_retrieve_for_regen` | active retrieve |
| `flare_regenerate_sentence` / `stele_flare_regenerate_sentence` | regen plan |
| `flare_active_step` / `stele_flare_active_step` | step record |
| `flare_loop_plan` / `stele_flare_loop_plan` | anticipate→regen |
| `adaptiverag_flare_shaped_report` | suite harness |

Modules: `stele_core.adaptiverag` + `stele_core.flare`. MCP tool count: **779**. CLI: `adaptiverag-*` / `flare-*`. Regen plans are **report-only**.

### 7.89 GraphReader + G-Retriever (UC-807–818)

| API / Tool | Behavior |
|---|---|
| `graphreader_build_node` / `stele_graphreader_build_node` | chunk → node |
| `graphreader_read_node` / `stele_graphreader_read_node` | coarse read |
| `graphreader_read_neighbors` / `stele_graphreader_read_neighbors` | fine explore |
| `graphreader_note_insight` / `stele_graphreader_note_insight` | insight note |
| `graphreader_reflect_plan` / `stele_graphreader_reflect_plan` | enough? |
| `graphreader_loop_plan` / `stele_graphreader_loop_plan` | plan→reflect |
| `gretriever_node_prize` / `stele_gretriever_node_prize` | node prize |
| `gretriever_pcst_select` / `stele_gretriever_pcst_select` | PCST proxy |
| `gretriever_subgraph` / `stele_gretriever_subgraph` | subgraph id |
| `gretriever_soft_prompt_plan` / `stele_gretriever_soft_prompt_plan` | soft prompt |
| `gretriever_highlight` / `stele_gretriever_highlight` | highlight |
| `gretriever_loop_plan` / `stele_gretriever_loop_plan` | prize→prompt |
| `graphreader_gretriever_shaped_report` | suite harness |

Modules: `stele_core.graphreader` + `stele_core.gretriever`. MCP tool count: **791**. CLI: `graphreader-*` / `gretriever-*`. Reflect/soft-prompt plans are **report-only**. No GNN on core.

### 7.90 RQ-RAG + IRCoT (UC-819–830)

| API / Tool | Behavior |
|---|---|
| `rqrag_rewrite` / `stele_rqrag_rewrite` | rewrite query |
| `rqrag_decompose` / `stele_rqrag_decompose` | sub-queries |
| `rqrag_disambiguate` / `stele_rqrag_disambiguate` | intent variants |
| `rqrag_refine_mode` / `stele_rqrag_refine_mode` | mode select |
| `rqrag_retrieve_refined` / `stele_rqrag_retrieve_refined` | retrieve |
| `rqrag_loop_plan` / `stele_rqrag_loop_plan` | mode→answer |
| `ircot_cot_step` / `stele_ircot_cot_step` | CoT sentence |
| `ircot_retrieve_guided` / `stele_ircot_retrieve_guided` | CoT-guided |
| `ircot_interleave` / `stele_ircot_interleave` | pairs |
| `ircot_answer_ready` / `stele_ircot_answer_ready` | stop plan |
| `ircot_hallucination_check` / `stele_ircot_hallucination_check` | grounded |
| `ircot_loop_plan` / `stele_ircot_loop_plan` | cot→answer |
| `rqrag_ircot_shaped_report` | suite harness |

Modules: `stele_core.rqrag` + `stele_core.ircot`. MCP tool count: **803**. CLI: `rqrag-*` / `ircot-*`. Answer-ready plans are **report-only**.

### 7.91 REPLUG + Iter-RetGen (UC-831–842)

| API / Tool | Behavior |
|---|---|
| `replug_retrieve_docs` / `stele_replug_retrieve_docs` | retrieve k |
| `replug_prepend_doc` / `stele_replug_prepend_doc` | prepend pack |
| `replug_ensemble_probs` / `stele_replug_ensemble_probs` | ensemble |
| `replug_supervise_retriever` / `stele_replug_supervise_retriever` | LM supervise |
| `replug_blackbox_forward` / `stele_replug_blackbox_forward` | frozen LM |
| `replug_loop_plan` / `stele_replug_loop_plan` | retrieve→ensemble |
| `iterretgen_generate` / `stele_iterretgen_generate` | generation draft |
| `iterretgen_use_as_query` / `stele_iterretgen_use_as_query` | gen→query |
| `iterretgen_retrieve_next` / `stele_iterretgen_retrieve_next` | next retrieve |
| `iterretgen_iterate` / `stele_iterretgen_iterate` | continue/stop |
| `iterretgen_adapt_retriever` / `stele_iterretgen_adapt_retriever` | adapt plan |
| `iterretgen_loop_plan` / `stele_iterretgen_loop_plan` | generate→iterate |
| `replug_iterretgen_shaped_report` | suite harness |

Modules: `stele_core.replug` + `stele_core.iterretgen`. MCP tool count: **815**. CLI: `replug-*` / `iterretgen-*`. Supervise/adapt plans are **report-only**.

### 7.92 PlanRAG + Rewrite-Retrieve-Read (UC-843–854)

| API / Tool | Behavior |
|---|---|
| `planrag_make_plan` / `stele_planrag_make_plan` | decision plan |
| `planrag_analysis_query` / `stele_planrag_analysis_query` | analysis query |
| `planrag_retrieve_data` / `stele_planrag_retrieve_data` | data rows |
| `planrag_replan` / `stele_planrag_replan` | replan gate |
| `planrag_decide` / `stele_planrag_decide` | decide |
| `planrag_loop_plan` / `stele_planrag_loop_plan` | plan→decide |
| `rrr_rewrite_query` / `stele_rrr_rewrite_query` | rewrite |
| `rrr_retrieve` / `stele_rrr_retrieve` | retrieve |
| `rrr_read` / `stele_rrr_read` | frozen read |
| `rrr_reader_feedback` / `stele_rrr_reader_feedback` | reward |
| `rrr_train_rewriter_plan` / `stele_rrr_train_rewriter_plan` | train plan |
| `rrr_loop_plan` / `stele_rrr_loop_plan` | rewrite→feedback |
| `planrag_rrr_shaped_report` | suite harness |

Modules: `stele_core.planrag` + `stele_core.rrr`. MCP tool count: **827**. CLI: `planrag-*` / `rrr-*`. Replan/decide/train plans are **report-only**.

### 7.93 DSP + GenRead (UC-855–866)

| API / Tool | Behavior |
|---|---|
| `dsp_bootstrap_demo` / `stele_dsp_bootstrap_demo` | demonstrations |
| `dsp_search` / `stele_dsp_search` | search stage |
| `dsp_predict` / `stele_dsp_predict` | predict stage |
| `dsp_compose_program` / `stele_dsp_compose_program` | program |
| `dsp_multihop_hop` / `stele_dsp_multihop_hop` | multi-hop |
| `dsp_loop_plan` / `stele_dsp_loop_plan` | demo→compose |
| `genread_generate_context` / `stele_genread_generate_context` | gen context |
| `genread_ground_optional` / `stele_genread_ground_optional` | optional RM |
| `genread_answer` / `stele_genread_answer` | answer |
| `genread_compare_retrieve` / `stele_genread_compare_retrieve` | compare |
| `genread_hybrid` / `stele_genread_hybrid` | hybrid |
| `genread_loop_plan` / `stele_genread_loop_plan` | generate→compare |
| `dsp_genread_shaped_report` | suite harness |

Modules: `stele_core.dsp` + `stele_core.genread`. MCP tool count: **839**. CLI: `dsp-*` / `genread-*`. Not the DSPy product runtime.

### 7.94 Self-Ask + ReAct (UC-867–878)

| API / Tool | Behavior |
|---|---|
| `selfask_followup` / `stele_selfask_followup` | follow-up Q |
| `selfask_search_intercept` / `stele_selfask_search_intercept` | search |
| `selfask_compose_answer` / `stele_selfask_compose_answer` | compose |
| `selfask_stop` / `stele_selfask_stop` | stop gate |
| `selfask_demo_prompt` / `stele_selfask_demo_prompt` | demos |
| `selfask_loop_plan` / `stele_selfask_loop_plan` | followup→stop |
| `react_thought` / `stele_react_thought` | Thought |
| `react_action` / `stele_react_action` | Action |
| `react_observe` / `stele_react_observe` | Observe |
| `react_finish` / `stele_react_finish` | Finish |
| `react_trajectory` / `stele_react_trajectory` | trajectory |
| `react_loop_plan` / `stele_react_loop_plan` | thought→finish |
| `selfask_react_shaped_report` | suite harness |

Modules: `stele_core.selfask` + `stele_core.react`. MCP tool count: **851**. CLI: `selfask-*` / `react-*`. Action/finish/stop are **report-only**.

### 7.95 Think-on-Graph + Toolformer (UC-879–890)

| API / Tool | Behavior |
|---|---|
| `tog_init_entity` / `stele_tog_init_entity` | seed entity |
| `tog_explore_neighbors` / `stele_tog_explore_neighbors` | expand |
| `tog_beam_prune` / `stele_tog_beam_prune` | beam prune |
| `tog_path_score` / `stele_tog_path_score` | path score |
| `tog_answer_from_paths` / `stele_tog_answer_from_paths` | answer |
| `tog_loop_plan` / `stele_tog_loop_plan` | init→answer |
| `tf_api_candidate` / `stele_tf_api_candidate` | API candidate |
| `tf_filter_call` / `stele_tf_filter_call` | usefulness filter |
| `tf_execute_proxy` / `stele_tf_execute_proxy` | proxy exec |
| `tf_incorporate_result` / `stele_tf_incorporate_result` | incorporate |
| `tf_demo_apis` / `stele_tf_demo_apis` | demos |
| `tf_loop_plan` / `stele_tf_loop_plan` | candidate→incorporate |
| `tog_toolformer_shaped_report` | suite harness |

Modules: `stele_core.thinkongraph` + `stele_core.toolformer`. MCP tool count: **863**. CLI: `tog-*` / `tf-*`. Prune/filter/execute are **report-only**.

### 7.96 Reflexion + Self-Consistency (UC-891–902)

| API / Tool | Behavior |
|---|---|
| `rx_trial_run` / `stele_rx_trial_run` | trial |
| `rx_evaluate` / `stele_rx_evaluate` | evaluate |
| `rx_verbal_reflect` / `stele_rx_verbal_reflect` | reflect |
| `rx_memory_store` / `stele_rx_memory_store` | episodic store |
| `rx_next_trial` / `stele_rx_next_trial` | next trial |
| `rx_loop_plan` / `stele_rx_loop_plan` | trial→store |
| `sc_sample_path` / `stele_sc_sample_path` | sample path |
| `sc_collect_answers` / `stele_sc_collect_answers` | collect |
| `sc_majority_vote` / `stele_sc_majority_vote` | majority |
| `sc_marginalize` / `stele_sc_marginalize` | marginalize |
| `sc_temperature` / `stele_sc_temperature` | temp |
| `sc_loop_plan` / `stele_sc_loop_plan` | sample→marginalize |
| `reflexion_selfcons_shaped_report` | suite harness |

Modules: `stele_core.reflexion` + `stele_core.selfcons`. MCP tool count: **875**. CLI: `rx-*` / `sc-*`. Evaluate/store are **report-only**.

### 7.97 Tree of Thoughts + Least-to-Most (UC-903–914)

| API / Tool | Behavior |
|---|---|
| `tot_propose` / `stele_tot_propose` | propose thought |
| `tot_evaluate` / `stele_tot_evaluate` | evaluate |
| `tot_expand` / `stele_tot_expand` | expand budget |
| `tot_backtrack` / `stele_tot_backtrack` | backtrack |
| `tot_select_best` / `stele_tot_select_best` | select |
| `tot_loop_plan` / `stele_tot_loop_plan` | propose→select |
| `ltm_decompose` / `stele_ltm_decompose` | decompose |
| `ltm_solve_sub` / `stele_ltm_solve_sub` | solve sub |
| `ltm_carry_forward` / `stele_ltm_carry_forward` | carry |
| `ltm_compose_final` / `stele_ltm_compose_final` | compose |
| `ltm_easy_to_hard` / `stele_ltm_easy_to_hard` | exemplars |
| `ltm_loop_plan` / `stele_ltm_loop_plan` | decompose→compose |
| `tot_ltm_shaped_report` | suite harness |

Modules: `stele_core.treeofthoughts` + `stele_core.leasttomost`. MCP tool count: **887**. CLI: `tot-*` / `ltm-*`. Backtrack is **report-only**.

### 7.98 Graph of Thoughts + Program of Thoughts (UC-915–926)

| API / Tool | Behavior |
|---|---|
| `got_add_thought` / `stele_got_add_thought` | add vertex |
| `got_link` / `stele_got_link` | edge |
| `got_aggregate` / `stele_got_aggregate` | aggregate |
| `got_feedback` / `stele_got_feedback` | feedback |
| `got_score_graph` / `stele_got_score_graph` | score |
| `got_loop_plan` / `stele_got_loop_plan` | add→score |
| `pot_emit_program` / `stele_pot_emit_program` | emit program |
| `pot_sandbox_run` / `stele_pot_sandbox_run` | sandbox proxy |
| `pot_read_result` / `stele_pot_read_result` | read |
| `pot_self_consistency` / `stele_pot_self_consistency` | samples |
| `pot_disentangle` / `stele_pot_disentangle` | offload flag |
| `pot_loop_plan` / `stele_pot_loop_plan` | emit→vote |
| `got_pot_shaped_report` | suite harness |

Modules: `stele_core.graphofthoughts` + `stele_core.programofthoughts`. MCP tool count: **899**. CLI: `got-*` / `pot-*`. Aggregate/feedback/sandbox are **report-only**; no real `exec`.

### 7.99 Algorithm of Thoughts + Reasoning via Planning (UC-927–938)

| API / Tool | Behavior |
|---|---|
| `aot_load_algorithm` / `stele_aot_load_algorithm` | load algo |
| `aot_explore_subtree` / `stele_aot_explore_subtree` | explore |
| `aot_tunnel_vision` / `stele_aot_tunnel_vision` | tunnel |
| `aot_query_budget` / `stele_aot_query_budget` | budget |
| `aot_surpass_algo` / `stele_aot_surpass_algo` | intuition |
| `aot_loop_plan` / `stele_aot_loop_plan` | load→budget |
| `rap_world_state` / `stele_rap_world_state` | world state |
| `rap_expand` / `stele_rap_expand` | expand |
| `rap_reward` / `stele_rap_reward` | reward |
| `rap_select_path` / `stele_rap_select_path` | select |
| `rap_balance` / `stele_rap_balance` | explore/exploit |
| `rap_loop_plan` / `stele_rap_loop_plan` | state→select |
| `aot_rap_shaped_report` | suite harness |

Modules: `stele_core.algorithmofthoughts` + `stele_core.reasoningviaplanning`. MCP tool count: **911**. CLI: `aot-*` / `rap-*`. Tunnel/select are **report-only**. RAP ≠ RAPTOR.

### 7.100 Skeleton-of-Thought + Buffer of Thoughts (UC-939–950)

| API / Tool | Behavior |
|---|---|
| `sot_emit_skeleton` / `stele_sot_emit_skeleton` | skeleton |
| `sot_extract_points` / `stele_sot_extract_points` | extract |
| `sot_parallel_expand` / `stele_sot_parallel_expand` | expand |
| `sot_router` / `stele_sot_router` | router |
| `sot_latency_gain` / `stele_sot_latency_gain` | latency |
| `sot_loop_plan` / `stele_sot_loop_plan` | skeleton→route |
| `bot_distill_template` / `stele_bot_distill_template` | distill |
| `bot_retrieve_template` / `stele_bot_retrieve_template` | retrieve |
| `bot_instantiate` / `stele_bot_instantiate` | instantiate |
| `bot_buffer_update` / `stele_bot_buffer_update` | update |
| `bot_cost_ratio` / `stele_bot_cost_ratio` | cost |
| `bot_loop_plan` / `stele_bot_loop_plan` | distill→update |
| `sot_bot_shaped_report` | suite harness |

Modules: `stele_core.skeletonofthought` + `stele_core.bufferofthoughts`. MCP tool count: **923**. CLI: `sot-*` / `bot-*`. Expand/router/update are **report-only**.

### 7.101 Self-Discover + Meta-Prompting (UC-951–962)

| API / Tool | Behavior |
|---|---|
| `sd_select_modules` / `stele_sd_select_modules` | select |
| `sd_adapt` / `stele_sd_adapt` | adapt |
| `sd_implement` / `stele_sd_implement` | implement JSON |
| `sd_apply_instance` / `stele_sd_apply_instance` | apply |
| `sd_compute_ratio` / `stele_sd_compute_ratio` | compute |
| `sd_loop_plan` / `stele_sd_loop_plan` | select→apply |
| `mp_break_task` / `stele_mp_break_task` | break |
| `mp_assign_expert` / `stele_mp_assign_expert` | assign |
| `mp_oversee` / `stele_mp_oversee` | oversee |
| `mp_verify` / `stele_mp_verify` | verify |
| `mp_task_agnostic` / `stele_mp_task_agnostic` | scaffold |
| `mp_loop_plan` / `stele_mp_loop_plan` | break→verify |
| `sd_mp_shaped_report` | suite harness |

Modules: `stele_core.selfdiscover` + `stele_core.metaprompting`. MCP tool count: **935**. CLI: `sd-*` / `mp-*`. Apply/verify are **report-only**.

### 7.102 Quiet-STaR + Decomposed Prompting (UC-963–974)

| API / Tool | Behavior |
|---|---|
| `qs_thought_bounds` / `stele_qs_thought_bounds` | delimiters |
| `qs_parallel_sample` / `stele_qs_parallel_sample` | sample |
| `qs_mix_head` / `stele_qs_mix_head` | mix |
| `qs_hard_token_aid` / `stele_qs_hard_token_aid` | hard tokens |
| `qs_zero_shot_flag` / `stele_qs_zero_shot_flag` | zero-shot |
| `qs_loop_plan` / `stele_qs_loop_plan` | bounds→aid |
| `dep_decompose` / `stele_dep_decompose` | decompose |
| `dep_delegate` / `stele_dep_delegate` | delegate |
| `dep_recurse` / `stele_dep_recurse` | recurse |
| `dep_swap_symbolic` / `stele_dep_swap_symbolic` | symbolic swap |
| `dep_library_size` / `stele_dep_library_size` | library |
| `dep_loop_plan` / `stele_dep_loop_plan` | decompose→swap |
| `qs_dep_shaped_report` | suite harness |

Modules: `stele_core.quietstar` + `stele_core.decomposedprompting`. MCP tool count: **947**. CLI: `qs-*` / `dep-*`. Zero-shot/swap are **report-only**. Decomposed ≠ Least-to-Most.

### 7.103 STaR + Cumulative Reasoning (UC-975–986)

| API / Tool | Behavior |
|---|---|
| `star_generate` / `stele_star_generate` | generate |
| `star_filter_correct` / `stele_star_filter_correct` | filter |
| `star_rationalize` / `stele_star_rationalize` | rationalize |
| `star_finetune_proxy` / `stele_star_finetune_proxy` | finetune |
| `star_bootstrap_round` / `stele_star_bootstrap_round` | round |
| `star_loop_plan` / `stele_star_loop_plan` | generate→finetune |
| `cr_propose` / `stele_cr_propose` | propose |
| `cr_verify` / `stele_cr_verify` | verify |
| `cr_accumulate` / `stele_cr_accumulate` | accumulate |
| `cr_report` / `stele_cr_report` | report |
| `cr_roles` / `stele_cr_roles` | roles |
| `cr_loop_plan` / `stele_cr_loop_plan` | propose→report |
| `star_cr_shaped_report` | suite harness |

Modules: `stele_core.selftaughtreasoner` + `stele_core.cumulativereasoning`. MCP tool count: **959**. CLI: `star-*` / `cr-*`. Filter/finetune/verify are **report-only**. STaR ≠ Quiet-STaR.

### 7.104 Plan-and-Solve + Progressive-Hint Prompting (UC-987–998)

| API / Tool | Behavior |
|---|---|
| `ps_devise_plan` / `stele_ps_devise_plan` | plan |
| `ps_execute` / `stele_ps_execute` | execute |
| `ps_plus_extract` / `stele_ps_plus_extract` | PS+ vars |
| `ps_calc_guard` / `stele_ps_calc_guard` | calc guard |
| `ps_missing_step_fix` / `stele_ps_missing_step_fix` | missing-step |
| `ps_loop_plan` / `stele_ps_loop_plan` | plan→guard |
| `php_base_answer` / `stele_php_base_answer` | base |
| `php_emit_hint` / `stele_php_emit_hint` | hint |
| `php_reask` / `stele_php_reask` | reask |
| `php_stable_stop` / `stele_php_stable_stop` | stop |
| `php_combine_sc` / `stele_php_combine_sc` | +SC |
| `php_loop_plan` / `stele_php_loop_plan` | base→stop |
| `ps_php_shaped_report` | suite harness |

Modules: `stele_core.planandsolve` + `stele_core.progressivehint`. MCP tool count: **971**. CLI: `ps-*` / `php-*`. Guard/stop are **report-only**. PS ≠ PlanRAG.

### 7.105 AgentCoder + PAL (UC-999–1010)

| API / Tool | Behavior |
|---|---|
| `ac_programmer` / `stele_ac_programmer` | programmer |
| `ac_test_designer` / `stele_ac_test_designer` | test design |
| `ac_test_executor` / `stele_ac_test_executor` | execute |
| `ac_refine` / `stele_ac_refine` | refine |
| `ac_pass_gate` / `stele_ac_pass_gate` | pass gate |
| `ac_loop_plan` / `stele_ac_loop_plan` | program→refine |
| `pal_emit_program` / `stele_pal_emit_program` | emit |
| `pal_offload_solve` / `stele_pal_offload_solve` | offload |
| `pal_read_answer` / `stele_pal_read_answer` | read |
| `pal_decompose_only` / `stele_pal_decompose_only` | decompose flag |
| `pal_vs_cot` / `stele_pal_vs_cot` | vs CoT |
| `pal_loop_plan` / `stele_pal_loop_plan` | emit→flag |
| `ac_pal_shaped_report` | suite harness |

Modules: `stele_core.agentcoder` + `stele_core.programaided`. MCP tool count: **983**. CLI: `ac-*` / `pal-*`. Executor/offload are **report-only**. PAL ≠ PoT (`pot_*`).

### 7.106 Faithful CoT + LATS (UC-1011–1022)

| API / Tool | Behavior |
|---|---|
| `fcot_translate` / `stele_fcot_translate` | translate |
| `fcot_solve` / `stele_fcot_solve` | solve |
| `fcot_faithfulness` / `stele_fcot_faithfulness` | faithful |
| `fcot_interleave` / `stele_fcot_interleave` | NL+SL |
| `fcot_vs_cot` / `stele_fcot_vs_cot` | vs CoT |
| `fcot_loop_plan` / `stele_fcot_loop_plan` | translate→flag |
| `lats_expand` / `stele_lats_expand` | expand |
| `lats_value` / `stele_lats_value` | value |
| `lats_reflect` / `stele_lats_reflect` | reflect |
| `lats_select` / `stele_lats_select` | select |
| `lats_env_feedback` / `stele_lats_env_feedback` | env |
| `lats_loop_plan` / `stele_lats_loop_plan` | expand→select |
| `fcot_lats_shaped_report` | suite harness |

Modules: `stele_core.faithfulcot` + `stele_core.lats`. MCP tool count: **995**. CLI: `fcot-*` / `lats-*`. Solve/env are **report-only**. LATS ≠ RAP (`rap_*`).

### 7.107 Voyager + ReWOO (UC-1023–1034)

| API / Tool | Behavior |
|---|---|
| `voy_curriculum` / `stele_voy_curriculum` | curriculum |
| `voy_skill_store` / `stele_voy_skill_store` | store |
| `voy_skill_retrieve` / `stele_voy_skill_retrieve` | retrieve |
| `voy_self_verify` / `stele_voy_self_verify` | verify |
| `voy_compose` / `stele_voy_compose` | compose |
| `voy_loop_plan` / `stele_voy_loop_plan` | curriculum→verify |
| `rewoo_plan` / `stele_rewoo_plan` | plan |
| `rewoo_worker` / `stele_rewoo_worker` | worker |
| `rewoo_solver` / `stele_rewoo_solver` | solve |
| `rewoo_decouple` / `stele_rewoo_decouple` | decouple |
| `rewoo_token_save` / `stele_rewoo_token_save` | tokens |
| `rewoo_loop_plan` / `stele_rewoo_loop_plan` | plan→flag |
| `voy_rewoo_shaped_report` | suite harness |

Modules: `stele_core.voyager` + `stele_core.rewoo`. MCP tool count: **1007**. CLI: `voy-*` / `rewoo-*`. Verify/token_save are **report-only**. ReWOO ≠ ReAct.

### 7.108 CRITIC + Deductive Verification (UC-1035–1046)

| API / Tool | Behavior |
|---|---|
| `critic_draft` / `stele_critic_draft` | draft |
| `critic_tool_check` / `stele_critic_tool_check` | tool critique |
| `critic_revise` / `stele_critic_revise` | revise |
| `critic_iterate` / `stele_critic_iterate` | iterate |
| `critic_stop` / `stele_critic_stop` | stop |
| `critic_loop_plan` / `stele_critic_loop_plan` | draft→stop |
| `dv_natural_program` / `stele_dv_natural_program` | Natural Program |
| `dv_step_verify` / `stele_dv_step_verify` | step verify |
| `dv_premise_scope` / `stele_dv_premise_scope` | premises |
| `dv_unanimity` / `stele_dv_unanimity` | unanimity |
| `dv_ground` / `stele_dv_ground` | ground |
| `dv_loop_plan` / `stele_dv_loop_plan` | program→ground |
| `critic_dv_shaped_report` | suite harness |

Modules: `stele_core.critic` + `stele_core.deductive`. MCP tool count: **1019**. CLI: `critic-*` / `dv-*`. Stop/unanimity are **report-only**. CRITIC ≠ Reflexion; DV ≠ Faithful CoT.

### 7.109 HuggingGPT + Multiagent Debate (UC-1047–1058)

| API / Tool | Behavior |
|---|---|
| `hgpt_plan` / `stele_hgpt_plan` | plan |
| `hgpt_select` / `stele_hgpt_select` | select |
| `hgpt_execute` / `stele_hgpt_execute` | execute |
| `hgpt_summarize` / `stele_hgpt_summarize` | summarize |
| `hgpt_modality` / `stele_hgpt_modality` | modalities |
| `hgpt_loop_plan` / `stele_hgpt_loop_plan` | plan→summarize |
| `mad_propose` / `stele_mad_propose` | propose |
| `mad_debate` / `stele_mad_debate` | debate |
| `mad_critique` / `stele_mad_critique` | critique |
| `mad_converge` / `stele_mad_converge` | converge |
| `mad_factuality` / `stele_mad_factuality` | factuality |
| `mad_loop_plan` / `stele_mad_loop_plan` | propose→converge |
| `hgpt_mad_shaped_report` | suite harness |

Modules: `stele_core.hugginggpt` + `stele_core.multiagentdebate`. MCP tool count: **1031**. CLI: `hgpt-*` / `mad-*`. Execute/converge are **report-only**. MAD ≠ Meta-Prompting.

### 7.110 Auto-CoT + CAMEL (UC-1059–1070)

| API / Tool | Behavior |
|---|---|
| `autocot_cluster` / `stele_autocot_cluster` | cluster |
| `autocot_sample` / `stele_autocot_sample` | sample |
| `autocot_generate` / `stele_autocot_generate` | generate |
| `autocot_heuristic` / `stele_autocot_heuristic` | heuristic |
| `autocot_diversity` / `stele_autocot_diversity` | diversity |
| `autocot_loop_plan` / `stele_autocot_loop_plan` | cluster→heuristic |
| `camel_roles` / `stele_camel_roles` | roles |
| `camel_inception` / `stele_camel_inception` | inception |
| `camel_turn` / `stele_camel_turn` | turn |
| `camel_complete` / `stele_camel_complete` | complete |
| `camel_society` / `stele_camel_society` | society |
| `camel_loop_plan` / `stele_camel_loop_plan` | roles→complete |
| `autocot_camel_shaped_report` | suite harness |

Modules: `stele_core.autocot` + `stele_core.camel`. MCP tool count: **1043**. CLI: `autocot-*` / `camel-*`. Complete is **report-only**. CAMEL ≠ MAD.

### 7.111 Chameleon + Recursion of Thought (UC-1071–1082)

| API / Tool | Behavior |
|---|---|
| `cham_inventory` / `stele_cham_inventory` | inventory |
| `cham_plan` / `stele_cham_plan` | plan |
| `cham_compose` / `stele_cham_compose` | compose |
| `cham_execute` / `stele_cham_execute` | execute |
| `cham_constraint` / `stele_cham_constraint` | constraint |
| `cham_loop_plan` / `stele_cham_loop_plan` | inventory→execute |
| `rot_trigger` / `stele_rot_trigger` | trigger |
| `rot_divide` / `stele_rot_divide` | divide |
| `rot_conquer` / `stele_rot_conquer` | conquer |
| `rot_merge` / `stele_rot_merge` | merge |
| `rot_context_limit` / `stele_rot_context_limit` | limit |
| `rot_loop_plan` / `stele_rot_loop_plan` | trigger→merge |
| `cham_rot_shaped_report` | suite harness |

Modules: `stele_core.chameleon` + `stele_core.recursionofthought`. MCP tool count: **1055**. CLI: `cham-*` / `rot-*`. Execute/limit are **report-only**. Chameleon ≠ HuggingGPT; RoT ≠ Least-to-Most.

### 7.112 Active-Prompt + Analogical Prompting (UC-1083–1094)

| API / Tool | Behavior |
|---|---|
| `ap_sample` / `stele_ap_sample` | sample |
| `ap_uncertainty` / `stele_ap_uncertainty` | uncertainty |
| `ap_select` / `stele_ap_select` | select |
| `ap_annotate` / `stele_ap_annotate` | annotate |
| `ap_pool` / `stele_ap_pool` | pool |
| `ap_loop_plan` / `stele_ap_loop_plan` | sample→annotate |
| `ana_recall` / `stele_ana_recall` | recall |
| `ana_knowledge` / `stele_ana_knowledge` | knowledge |
| `ana_solve` / `stele_ana_solve` | solve |
| `ana_adapt` / `stele_ana_adapt` | adapt |
| `ana_no_label` / `stele_ana_no_label` | no labels |
| `ana_loop_plan` / `stele_ana_loop_plan` | recall→adapt |
| `ap_ana_shaped_report` | suite harness |

Modules: `stele_core.activeprompt` + `stele_core.analogical`. MCP tool count: **1067**. CLI: `ap-*` / `ana-*`. No-label is **report-only**. Active-Prompt ≠ Auto-CoT.

### 7.113 Complexity-Based + Step-Back Prompting (UC-1095–1106)

| API / Tool | Behavior |
|---|---|
| `cbp_score` / `stele_cbp_score` | score |
| `cbp_select` / `stele_cbp_select` | select |
| `cbp_sample_chains` / `stele_cbp_sample_chains` | sample |
| `cbp_vote_complex` / `stele_cbp_vote_complex` | vote |
| `cbp_robust` / `stele_cbp_robust` | robust |
| `cbp_loop_plan` / `stele_cbp_loop_plan` | score→vote |
| `sb_abstract` / `stele_sb_abstract` | abstract |
| `sb_principle` / `stele_sb_principle` | principle |
| `sb_reason` / `stele_sb_reason` | reason |
| `sb_path` / `stele_sb_path` | path |
| `sb_detail_trap` / `stele_sb_detail_trap` | detail trap |
| `sb_loop_plan` / `stele_sb_loop_plan` | abstract→path |
| `cbp_sb_shaped_report` | suite harness |

Modules: `stele_core.complexityprompt` + `stele_core.stepback`. MCP tool count: **1079**. CLI: `cbp-*` / `sb-*`. Vote/detail_trap are **report-only**. Step-Back ≠ Least-to-Most.

### 7.114 Multimodal-CoT + Maieutic Prompting (UC-1107–1118)

| API / Tool | Behavior |
|---|---|
| `mmcot_fuse` / `stele_mmcot_fuse` | fuse |
| `mmcot_rationale` / `stele_mmcot_rationale` | rationale |
| `mmcot_infer` / `stele_mmcot_infer` | infer |
| `mmcot_hallucination` / `stele_mmcot_hallucination` | hallucination |
| `mmcot_separate` / `stele_mmcot_separate` | two-stage |
| `mmcot_loop_plan` / `stele_mmcot_loop_plan` | fuse→flag |
| `mai_abduce` / `stele_mai_abduce` | abduce |
| `mai_recurse` / `stele_mai_recurse` | recurse |
| `mai_sat` / `stele_mai_sat` | SAT |
| `mai_consistent` / `stele_mai_consistent` | consistent |
| `mai_unreliable` / `stele_mai_unreliable` | unreliable |
| `mai_loop_plan` / `stele_mai_loop_plan` | abduce→consistent |
| `mmcot_mai_shaped_report` | suite harness |

Modules: `stele_core.multimodalcot` + `stele_core.maieutic`. MCP tool count: **1091**. CLI: `mmcot-*` / `mai-*`. Separate/unreliable are **report-only**. No vision I/O on core.

### 7.115 Self-Refine + Metacognitive Prompting (UC-1119–1130)

| API / Tool | Behavior |
|---|---|
| `sr_generate` / `stele_sr_generate` | generate |
| `sr_feedback` / `stele_sr_feedback` | feedback |
| `sr_refine` / `stele_sr_refine` | refine |
| `sr_iterate` / `stele_sr_iterate` | iterate |
| `sr_no_train` / `stele_sr_no_train` | no-train |
| `sr_loop_plan` / `stele_sr_loop_plan` | generate→iterate |
| `mcp_recognize` / `stele_mcp_recognize` | recognize |
| `mcp_interpret` / `stele_mcp_interpret` | interpret |
| `mcp_reevaluate` / `stele_mcp_reevaluate` | reevaluate |
| `mcp_confidence` / `stele_mcp_confidence` | confidence |
| `mcp_justify` / `stele_mcp_justify` | justify |
| `mcp_loop_plan` / `stele_mcp_loop_plan` | recognize→confidence |
| `sr_mcp_shaped_report` | suite harness |

Modules: `stele_core.selfrefine` + `stele_core.metacognitive`. MCP tool count: **1103**. CLI: `sr-*` / `mcp-*`. No-train/justify are **report-only**. Self-Refine ≠ CRITIC; `mcp_*` ≠ Meta-Prompting (`mp_*`).

### 7.116 Thread of Thought + Thought Propagation (UC-1131–1142)

| API / Tool | Behavior |
|---|---|
| `thot_segment` / `stele_thot_segment` | segment |
| `thot_analyze` / `stele_thot_analyze` | analyze |
| `thot_select` / `stele_thot_select` | select |
| `thot_synthesize` / `stele_thot_synthesize` | synthesize |
| `thot_plug` / `stele_thot_plug` | plug |
| `thot_loop_plan` / `stele_thot_loop_plan` | segment→synthesize |
| `tprop_propose` / `stele_tprop_propose` | propose |
| `tprop_solve` / `stele_tprop_solve` | solve |
| `tprop_reuse` / `stele_tprop_reuse` | reuse |
| `tprop_amend` / `stele_tprop_amend` | amend |
| `tprop_compat` / `stele_tprop_compat` | compat |
| `tprop_loop_plan` / `stele_tprop_loop_plan` | propose→amend |
| `thot_tprop_shaped_report` | suite harness |

Modules: `stele_core.threadofthought` + `stele_core.thoughtpropagation`. MCP tool count: **1115**. CLI: `thot-*` / `tprop-*`. Plug/compat are **report-only**. `tprop_*` ≠ Analogical (`ana_*`).

### 7.117 System 2 Attention + Contrastive CoT (UC-1143–1154)

| API / Tool | Behavior |
|---|---|
| `s2a_regenerate` / `stele_s2a_regenerate` | regenerate |
| `s2a_attend` / `stele_s2a_attend` | attend |
| `s2a_respond` / `stele_s2a_respond` | respond |
| `s2a_factuality` / `stele_s2a_factuality` | factuality |
| `s2a_sycophancy` / `stele_s2a_sycophancy` | sycophancy |
| `s2a_loop_plan` / `stele_s2a_loop_plan` | regenerate→factuality |
| `ccot_valid` / `stele_ccot_valid` | valid |
| `ccot_invalid` / `stele_ccot_invalid` | invalid |
| `ccot_contrast` / `stele_ccot_contrast` | contrast |
| `ccot_reason` / `stele_ccot_reason` | reason |
| `ccot_auto` / `stele_ccot_auto` | auto |
| `ccot_loop_plan` / `stele_ccot_loop_plan` | valid→reason |
| `s2a_ccot_shaped_report` | suite harness |

Modules: `stele_core.system2attention` + `stele_core.contrastivecot`. MCP tool count: **1127**. CLI: `s2a-*` / `ccot-*`. Sycophancy/auto are **report-only**. `ccot_*` ≠ Auto-CoT (`autocot_*`).

### 7.118 Tab-CoT + Everything of Thoughts (UC-1155–1166)

| API / Tool | Behavior |
|---|---|
| `tabcot_header` / `stele_tabcot_header` | header |
| `tabcot_row` / `stele_tabcot_row` | row |
| `tabcot_infer2d` / `stele_tabcot_infer2d` | infer2d |
| `tabcot_extract` / `stele_tabcot_extract` | extract |
| `tabcot_zeroshot` / `stele_tabcot_zeroshot` | zeroshot |
| `tabcot_loop_plan` / `stele_tabcot_loop_plan` | header→extract |
| `xot_mcts` / `stele_xot_mcts` | mcts |
| `xot_revise` / `stele_xot_revise` | revise |
| `xot_map` / `stele_xot_map` | map |
| `xot_penrose` / `stele_xot_penrose` | penrose |
| `xot_flexible` / `stele_xot_flexible` | flexible |
| `xot_loop_plan` / `stele_xot_loop_plan` | mcts→penrose |
| `tabcot_xot_shaped_report` | suite harness |

Modules: `stele_core.tabcot` + `stele_core.everythingofthoughts`. MCP tool count: **1139**. CLI: `tabcot-*` / `xot-*`. Zeroshot/flexible are **report-only**. No real MCTS on core. `tabcot_*` ≠ `ccot_*`.

### 7.119 Chain-of-Verification + Verify-and-Edit (UC-1167–1178)

| API / Tool | Behavior |
|---|---|
| `cove_draft` / `stele_cove_draft` | draft |
| `cove_plan` / `stele_cove_plan` | plan |
| `cove_answer` / `stele_cove_answer` | answer |
| `cove_final` / `stele_cove_final` | final |
| `cove_hallucination` / `stele_cove_hallucination` | hallucination |
| `cove_loop_plan` / `stele_cove_loop_plan` | draft→final |
| `ved_uncertain` / `stele_ved_uncertain` | uncertain |
| `ved_search` / `stele_ved_search` | search |
| `ved_edit` / `stele_ved_edit` | edit |
| `ved_predict` / `stele_ved_predict` | predict |
| `ved_knowledge` / `stele_ved_knowledge` | knowledge |
| `ved_loop_plan` / `stele_ved_loop_plan` | uncertain→predict |
| `cove_ved_shaped_report` | suite harness |

Modules: `stele_core.chainofverification` + `stele_core.verifyandedit`. MCP tool count: **1151**. CLI: `cove-*` / `ved-*`. Hallucination/knowledge are **report-only**. No retrieval I/O on core. `cove_*` ≠ CRITIC; `ved_*` ≠ CoVe.

### 7.120 Self-Verification + Chain of Density (UC-1179–1190)

| API / Tool | Behavior |
|---|---|
| `sve_forward` / `stele_sve_forward` | forward |
| `sve_mask` / `stele_sve_mask` | mask |
| `sve_repredict` / `stele_sve_repredict` | repredict |
| `sve_score` / `stele_sve_score` | score |
| `sve_select` / `stele_sve_select` | select |
| `sve_loop_plan` / `stele_sve_loop_plan` | forward→score |
| `cod_sparse` / `stele_cod_sparse` | sparse |
| `cod_entities` / `stele_cod_entities` | entities |
| `cod_fuse` / `stele_cod_fuse` | fuse |
| `cod_length` / `stele_cod_length` | length |
| `cod_tradeoff` / `stele_cod_tradeoff` | tradeoff |
| `cod_loop_plan` / `stele_cod_loop_plan` | sparse→length |
| `sve_cod_shaped_report` | suite harness |

Modules: `stele_core.selfverification` + `stele_core.chainofdensity`. MCP tool count: **1163**. CLI: `sve-*` / `cod-*`. Select/tradeoff are **report-only**. `sve_*` ≠ CoVe; `cod_*` = Chain of Density (not code).

### 7.121 Hint-before-Solving + EmotionPrompt (UC-1191–1202)

| API / Tool | Behavior |
|---|---|
| `hsp_hint` / `stele_hsp_hint` | hint |
| `hsp_solve` / `stele_hsp_solve` | solve |
| `hsp_answer` / `stele_hsp_answer` | answer |
| `hsp_compose` / `stele_hsp_compose` | compose |
| `hsp_quality` / `stele_hsp_quality` | quality |
| `hsp_loop_plan` / `stele_hsp_loop_plan` | hint→compose |
| `emo_stimulus` / `stele_emo_stimulus` | stimulus |
| `emo_append` / `stele_emo_append` | append |
| `emo_run` / `stele_emo_run` | run |
| `emo_truth` / `stele_emo_truth` | truth |
| `emo_psych` / `stele_emo_psych` | psych |
| `emo_loop_plan` / `stele_emo_loop_plan` | stimulus→truth |
| `hsp_emo_shaped_report` | suite harness |

Modules: `stele_core.hintbeforesolving` + `stele_core.emotionprompt`. MCP tool count: **1175**. CLI: `hsp-*` / `emo-*`. Quality/psych are **report-only**. HSP ≠ Progressive-Hint (`php_*`).

### 7.122 Automatic Prompt Engineer + Promptbreeder (UC-1203–1214)

| API / Tool | Behavior |
|---|---|
| `ape_propose` / `stele_ape_propose` | propose |
| `ape_score` / `stele_ape_score` | score |
| `ape_select` / `stele_ape_select` | select |
| `ape_steer` / `stele_ape_steer` | steer |
| `ape_human` / `stele_ape_human` | human |
| `ape_loop_plan` / `stele_ape_loop_plan` | propose→steer |
| `pbr_init` / `stele_pbr_init` | init |
| `pbr_mutate` / `stele_pbr_mutate` | mutate |
| `pbr_fitness` / `stele_pbr_fitness` | fitness |
| `pbr_diversity` / `stele_pbr_diversity` | diversity |
| `pbr_selfref` / `stele_pbr_selfref` | selfref |
| `pbr_loop_plan` / `stele_pbr_loop_plan` | init→diversity |
| `ape_pbr_shaped_report` | suite harness |

Modules: `stele_core.automaticpromptengineer` + `stele_core.promptbreeder`. MCP tool count: **1187**. CLI: `ape-*` / `pbr-*`. Human/selfref are **report-only**. APE ≠ Active-Prompt (`ap_*`); `pbr_*` ≠ Progressive-Hint.

### 7.123 OPRO + EvoPrompt (UC-1215–1226)

| API / Tool | Behavior |
|---|---|
| `opro_meta` / `stele_opro_meta` | meta |
| `opro_propose` / `stele_opro_propose` | propose |
| `opro_score` / `stele_opro_score` | score |
| `opro_append` / `stele_opro_append` | append |
| `opro_best` / `stele_opro_best` | best |
| `opro_loop_plan` / `stele_opro_loop_plan` | meta→append |
| `evp_init` / `stele_evp_init` | init |
| `evp_cross` / `stele_evp_cross` | cross |
| `evp_mutate` / `stele_evp_mutate` | mutate |
| `evp_select` / `stele_evp_select` | select |
| `evp_ea` / `stele_evp_ea` | ea |
| `evp_loop_plan` / `stele_evp_loop_plan` | init→select |
| `opro_evp_shaped_report` | suite harness |

Modules: `stele_core.optimizationbyprompting` + `stele_core.evoprompt`. MCP tool count: **1199**. CLI: `opro-*` / `evp-*`. Best/ea are **report-only**. OPRO ≠ APE; `evp_*` ≠ `evo_*` (evomemory/evolver) / Promptbreeder.

### 7.124 ProTeGi + PromptAgent (UC-1227–1238)

| API / Tool | Behavior |
|---|---|
| `ptg_gradient` / `stele_ptg_gradient` | gradient |
| `ptg_edit` / `stele_ptg_edit` | edit |
| `ptg_beam` / `stele_ptg_beam` | beam |
| `ptg_bandit` / `stele_ptg_bandit` | bandit |
| `ptg_jailbreak` / `stele_ptg_jailbreak` | jailbreak |
| `ptg_loop_plan` / `stele_ptg_loop_plan` | gradient→bandit |
| `pag_state` / `stele_pag_state` | state |
| `pag_reflect` / `stele_pag_reflect` | reflect |
| `pag_expand` / `stele_pag_expand` | expand |
| `pag_backprop` / `stele_pag_backprop` | backprop |
| `pag_expert` / `stele_pag_expert` | expert |
| `pag_loop_plan` / `stele_pag_loop_plan` | state→backprop |
| `ptg_pag_shaped_report` | suite harness |

Modules: `stele_core.protegi` + `stele_core.promptagent`. MCP tool count: **1211**. CLI: `ptg-*` / `pag-*`. Jailbreak/expert are **report-only**. ProTeGi ≠ OPRO; PromptAgent ≠ Active-Prompt (`ap_*`).

### 7.125 MAPO + GrIPS (UC-1239–1250)

| API / Tool | Behavior |
|---|---|
| `mapo_posgrad` / `stele_mapo_posgrad` | posgrad |
| `mapo_momentum` / `stele_mapo_momentum` | momentum |
| `mapo_beam` / `stele_mapo_beam` | beam |
| `mapo_ucb` / `stele_mapo_ucb` | ucb |
| `mapo_faster` / `stele_mapo_faster` | faster |
| `mapo_loop_plan` / `stele_mapo_loop_plan` | posgrad→ucb |
| `grips_seed` / `stele_grips_seed` | seed |
| `grips_edit` / `stele_grips_edit` | edit |
| `grips_score` / `stele_grips_score` | score |
| `grips_accept` / `stele_grips_accept` | accept |
| `grips_api` / `stele_grips_api` | api |
| `grips_loop_plan` / `stele_grips_loop_plan` | seed→accept |
| `mapo_grips_shaped_report` | suite harness |

Modules: `stele_core.momentumaidedprompt` + `stele_core.grips`. MCP tool count: **1223**. CLI: `mapo-*` / `grips-*`. Faster/api are **report-only**. MAPO ≠ ProTeGi; GrIPS ≠ textual-gradient descent.

### 7.126 TEMPERA + RLPrompt (UC-1251–1262)

| API / Tool | Behavior |
|---|---|
| `tmpa_state` / `stele_tmpa_state` | state |
| `tmpa_act` / `stele_tmpa_act` | act |
| `tmpa_reward` / `stele_tmpa_reward` | reward |
| `tmpa_adapt` / `stele_tmpa_adapt` | adapt |
| `tmpa_efficiency` / `stele_tmpa_efficiency` | efficiency |
| `tmpa_loop_plan` / `stele_tmpa_loop_plan` | state→adapt |
| `rlp_init` / `stele_rlp_init` | init |
| `rlp_sample` / `stele_rlp_sample` | sample |
| `rlp_reward` / `stele_rlp_reward` | reward |
| `rlp_update` / `stele_rlp_update` | update |
| `rlp_discrete` / `stele_rlp_discrete` | discrete |
| `rlp_loop_plan` / `stele_rlp_loop_plan` | init→update |
| `tmpa_rlp_shaped_report` | suite harness |

Modules: `stele_core.tempera` + `stele_core.rlprompt`. MCP tool count: **1235**. CLI: `tmpa-*` / `rlp-*`. Efficiency/discrete are **report-only**. TEMPERA ≠ `sc_temperature`; RLPrompt ≠ TEMPERA.

### 7.127 AutoPrompt + Prefix-Tuning (UC-1263–1274)

| API / Tool | Behavior |
|---|---|
| `aup_template` / `stele_aup_template` | template |
| `aup_trigger` / `stele_aup_trigger` | trigger |
| `aup_search` / `stele_aup_search` | search |
| `aup_score` / `stele_aup_score` | score |
| `aup_probe` / `stele_aup_probe` | probe |
| `aup_loop_plan` / `stele_aup_loop_plan` | template→score |
| `pfx_task` / `stele_pfx_task` | task |
| `pfx_prefix` / `stele_pfx_prefix` | prefix |
| `pfx_optimize` / `stele_pfx_optimize` | optimize |
| `pfx_generate` / `stele_pfx_generate` | generate |
| `pfx_freeze` / `stele_pfx_freeze` | freeze |
| `pfx_loop_plan` / `stele_pfx_loop_plan` | task→generate |
| `aup_pfx_shaped_report` | suite harness |

Modules: `stele_core.autoprompt` + `stele_core.prefixtuning`. MCP tool count: **1247**. CLI: `aup-*` / `pfx-*`. Probe/freeze are **report-only**. AutoPrompt ≠ Active-Prompt (`ap_*`); Prefix-Tuning ≠ discrete AutoPrompt.

### 7.128 P-Tuning v2 + Prompt Tuning (UC-1275–1286)

| API / Tool | Behavior |
|---|---|
| `ptv_deep` / `stele_ptv_deep` | deep |
| `ptv_inject` / `stele_ptv_inject` | inject |
| `ptv_tune` / `stele_ptv_tune` | tune |
| `ptv_seqtag` / `stele_ptv_seqtag` | seqtag |
| `ptv_universal` / `stele_ptv_universal` | universal |
| `ptv_loop_plan` / `stele_ptv_loop_plan` | deep→seqtag |
| `ptl_soft` / `stele_ptl_soft` | soft |
| `ptl_prepend` / `stele_ptl_prepend` | prepend |
| `ptl_optimize` / `stele_ptl_optimize` | optimize |
| `ptl_scale` / `stele_ptl_scale` | scale |
| `ptl_input_only` / `stele_ptl_input_only` | input_only |
| `ptl_loop_plan` / `stele_ptl_loop_plan` | soft→scale |
| `ptv_ptl_shaped_report` | suite harness |

Modules: `stele_core.ptuningv2` + `stele_core.prompttuning`. MCP tool count: **1259**. CLI: `ptv-*` / `ptl-*`. Universal/input_only are **report-only**. P-Tuning v2 ≠ Prefix-Tuning; Prompt Tuning ≠ deep P-Tuning v2.

### 7.129 Soft Prompt Mixtures + SPoT (UC-1287–1298)

| API / Tool | Behavior |
|---|---|
| `msp_soft` / `stele_msp_soft` | soft |
| `msp_mix` / `stele_msp_mix` | mix |
| `msp_ensemble` / `stele_msp_ensemble` | ensemble |
| `msp_probe` / `stele_msp_probe` | probe |
| `msp_underest` / `stele_msp_underest` | underest |
| `msp_loop_plan` / `stele_msp_loop_plan` | soft→probe |
| `spot_source` / `stele_spot_source` | source |
| `spot_init` / `stele_spot_init` | init |
| `spot_embed` / `stele_spot_embed` | embed |
| `spot_retrieve` / `stele_spot_retrieve` | retrieve |
| `spot_vs_tune` / `stele_spot_vs_tune` | vs_tune |
| `spot_loop_plan` / `stele_spot_loop_plan` | source→retrieve |
| `msp_spot_shaped_report` | suite harness |

Modules: `stele_core.softpromptmixtures` + `stele_core.softprompttransfer`. MCP tool count: **1271**. CLI: `msp-*` / `spot-*`. Underest/vs_tune are **report-only**. Mixtures ≠ Prompt Tuning; SPoT ≠ single-task soft prompts.

### 7.130 ATTEMPT + Multitask Prompt Tuning (UC-1299–1310)

| API / Tool | Behavior |
|---|---|
| `atm_source` / `stele_atm_source` | source |
| `atm_target` / `stele_atm_target` | target |
| `atm_attend` / `stele_atm_attend` | attend |
| `atm_mix` / `stele_atm_mix` | mix |
| `atm_modular` / `stele_atm_modular` | modular |
| `atm_loop_plan` / `stele_atm_loop_plan` | source→mix |
| `mptp_shared` / `stele_mptp_shared` | shared |
| `mptp_factor` / `stele_mptp_factor` | factor |
| `mptp_transfer` / `stele_mptp_transfer` | transfer |
| `mptp_score` / `stele_mptp_score` | score |
| `mptp_efficient` / `stele_mptp_efficient` | efficient |
| `mptp_loop_plan` / `stele_mptp_loop_plan` | shared→score |
| `atm_mptp_shaped_report` | suite harness |

Modules: `stele_core.attemptprompt` + `stele_core.multitaskprompttuning`. MCP tool count: **1283**. CLI: `atm-*` / `mptp-*`. Modular/efficient are **report-only**. ATTEMPT ≠ SPoT; MPT ≠ ATTEMPT attentional mix.

### 7.131 LoRA + AdapterFusion (UC-1311–1322)

| API / Tool | Behavior |
|---|---|
| `lora_freeze` / `stele_lora_freeze` | freeze W0 |
| `lora_rank` / `stele_lora_rank` | allocate rank r |
| `lora_train` / `stele_lora_train` | train BA |
| `lora_merge` / `stele_lora_merge` | merge BA→W0 |
| `lora_latency` / `stele_lora_latency` | zero-extra latency |
| `lora_loop_plan` / `stele_lora_loop_plan` | freeze→merge |
| `adf_extract` / `stele_adf_extract` | task adapter |
| `adf_compose` / `stele_adf_compose` | compose adapters |
| `adf_attend` / `stele_adf_attend` | fusion Ψ |
| `adf_score` / `stele_adf_score` | score |
| `adf_nondestruct` / `stele_adf_nondestruct` | nondestructive |
| `adf_loop_plan` / `stele_adf_loop_plan` | extract→score |
| `lora_adf_shaped_report` | suite harness |

Modules: `stele_core.lora` + `stele_core.adapterfusion`. MCP tool count: **1295**. CLI: `lora-*` / `adf-*`. Latency/nondestruct are **report-only**. LoRA ≠ AdapterFusion; AdapterFusion ≠ ATTEMPT.

### 7.132 Compacter + (IA)^3 (UC-1323–1334)

| API / Tool | Behavior |
|---|---|
| `cmp_insert` / `stele_cmp_insert` | insert adapters |
| `cmp_kronecker` / `stele_cmp_kronecker` | hypercomplex factors |
| `cmp_train` / `stele_cmp_train` | train adapters+LN |
| `cmp_score` / `stele_cmp_score` | score |
| `cmp_compact` / `stele_cmp_compact` | compact flag |
| `cmp_loop_plan` / `stele_cmp_loop_plan` | insert→score |
| `ia3_vector` / `stele_ia3_vector` | rescale vectors |
| `ia3_scale` / `stele_ia3_scale` | element-wise scale |
| `ia3_train` / `stele_ia3_train` | train vectors |
| `ia3_score` / `stele_ia3_score` | score |
| `ia3_mixed` / `stele_ia3_mixed` | mixed-batch |
| `ia3_loop_plan` / `stele_ia3_loop_plan` | vector→score |
| `cmp_ia3_shaped_report` | suite harness |

Modules: `stele_core.compacter` + `stele_core.ia3`. MCP tool count: **1307**. CLI: `cmp-*` / `ia3-*`. Compact/mixed are **report-only**. Compacter ≠ LoRA; (IA)^3 ≠ Compacter.

### 7.133 BitFit + DoRA (UC-1335–1346)

| API / Tool | Behavior |
|---|---|
| `bft_freeze` / `stele_bft_freeze` | freeze weights |
| `bft_bias` / `stele_bft_bias` | bias subset |
| `bft_train` / `stele_bft_train` | train biases |
| `bft_score` / `stele_bft_score` | score |
| `bft_tiny` / `stele_bft_tiny` | tiny fraction |
| `bft_loop_plan` / `stele_bft_loop_plan` | freeze→score |
| `dora_decompose` / `stele_dora_decompose` | mag+direction |
| `dora_magnitude` / `stele_dora_magnitude` | magnitude |
| `dora_direction` / `stele_dora_direction` | LoRA on direction |
| `dora_score` / `stele_dora_score` | score |
| `dora_vs_lora` / `stele_dora_vs_lora` | vs LoRA gap |
| `dora_loop_plan` / `stele_dora_loop_plan` | decompose→score |
| `bft_dora_shaped_report` | suite harness |

Modules: `stele_core.bitfit` + `stele_core.dora`. MCP tool count: **1319**. CLI: `bft-*` / `dora-*`. Tiny/vs_lora are **report-only**. BitFit ≠ LoRA; DoRA ≠ LoRA (direction-aware).

### 7.134 QLoRA + AdaLoRA (UC-1347–1358)

| API / Tool | Behavior |
|---|---|
| `qlo_quantize` / `stele_qlo_quantize` | 4-bit freeze |
| `qlo_nf4` / `stele_qlo_nf4` | NF4 dtype |
| `qlo_adapter` / `stele_qlo_adapter` | LoRA on NF4 |
| `qlo_score` / `stele_qlo_score` | score |
| `qlo_memory` / `stele_qlo_memory` | double quant |
| `qlo_loop_plan` / `stele_qlo_loop_plan` | quantize→score |
| `adl_init` / `stele_adl_init` | budget init |
| `adl_svd` / `stele_adl_svd` | SVD factor |
| `adl_prune` / `stele_adl_prune` | prune ranks |
| `adl_score` / `stele_adl_score` | score |
| `adl_adaptive` / `stele_adl_adaptive` | adaptive rank |
| `adl_loop_plan` / `stele_adl_loop_plan` | init→score |
| `qlo_adl_shaped_report` | suite harness |

Modules: `stele_core.qlora` + `stele_core.adalora`. MCP tool count: **1331**. CLI: `qlo-*` / `adl-*`. Memory/adaptive are **report-only**. QLoRA ≠ LoRA alone; AdaLoRA ≠ Adaptive-RAG (`adaptiverag-*`).

### 7.135 VeRA + AdapterDrop (UC-1359–1370)

| API / Tool | Behavior |
|---|---|
| `vra_share` / `stele_vra_share` | shared random A,B |
| `vra_scale` / `stele_vra_scale` | scaling vectors |
| `vra_train` / `stele_vra_train` | train vectors |
| `vra_score` / `stele_vra_score` | score |
| `vra_tiny` / `stele_vra_tiny` | vector-only |
| `vra_loop_plan` / `stele_vra_loop_plan` | share→score |
| `adp_insert` / `stele_adp_insert` | insert adapters |
| `adp_drop` / `stele_adp_drop` | drop lower layers |
| `adp_infer` / `stele_adp_infer` | multi-task infer |
| `adp_score` / `stele_adp_score` | score |
| `adp_efficient` / `stele_adp_efficient` | multi-task flag |
| `adp_loop_plan` / `stele_adp_loop_plan` | insert→score |
| `vra_adp_shaped_report` | suite harness |

Modules: `stele_core.vera` + `stele_core.adapterdrop`. MCP tool count: **1343**. CLI: `vra-*` / `adp-*`. Tiny/efficient are **report-only**. VeRA ≠ LoRA; AdapterDrop ≠ AdapterFusion (`adf_*`).

### 7.136 PiSSA + Diff Pruning (UC-1371–1382)

| API / Tool | Behavior |
|---|---|
| `psa_svd` / `stele_psa_svd` | SVD of W |
| `psa_principal` / `stele_psa_principal` | init A,B |
| `psa_residual` / `stele_psa_residual` | freeze W^res |
| `psa_score` / `stele_psa_score` | score |
| `psa_fast` / `stele_psa_fast` | vs LoRA speed |
| `psa_loop_plan` / `stele_psa_loop_plan` | svd→score |
| `dpr_diff` / `stele_dpr_diff` | ΔW vector |
| `dpr_mask` / `stele_dpr_mask` | sparsity mask |
| `dpr_prune` / `stele_dpr_prune` | prune |
| `dpr_score` / `stele_dpr_score` | score |
| `dpr_sparse` / `stele_dpr_sparse` | no new params |
| `dpr_loop_plan` / `stele_dpr_loop_plan` | diff→score |
| `psa_dpr_shaped_report` | suite harness |

Modules: `stele_core.pissa` + `stele_core.diffpruning`. MCP tool count: **1355**. CLI: `psa-*` / `dpr-*`. Fast/sparse are **report-only**. PiSSA ≠ LoRA init; Diff Pruning ≠ BitFit.

### 7.137 Tied-LoRA + LoRA+ (UC-1383–1394)

| API / Tool | Behavior |
|---|---|
| `tlo_base` / `stele_tlo_base` | base factors |
| `tlo_tie` / `stele_tlo_tie` | tie across layers |
| `tlo_train` / `stele_tlo_train` | train tied |
| `tlo_score` / `stele_tlo_score` | score |
| `tlo_efficient` / `stele_tlo_efficient` | weight-tied |
| `tlo_loop_plan` / `stele_tlo_loop_plan` | base→score |
| `lrp_split` / `stele_lrp_split` | A/B roles |
| `lrp_ratio` / `stele_lrp_ratio` | λ = lr_B/lr_A |
| `lrp_train` / `stele_lrp_train` | dual-LR train |
| `lrp_score` / `stele_lrp_score` | score |
| `lrp_speed` / `stele_lrp_speed` | vs LoRA speed |
| `lrp_loop_plan` / `stele_lrp_loop_plan` | split→score |
| `tlo_lrp_shaped_report` | suite harness |

Modules: `stele_core.tiedlora` + `stele_core.loraplus`. MCP tool count: **1367**. CLI: `tlo-*` / `lrp-*`. Efficient/speed are **report-only**. Tied-LoRA ≠ VeRA; LoRA+ ≠ LoRA equal-LR.

### 7.138 LoRA-FA + DyLoRA (UC-1395–1406)

| API / Tool | Behavior |
|---|---|
| `lfa_freeze_a` / `stele_lfa_freeze_a` | freeze random A |
| `lfa_train_b` / `stele_lfa_train_b` | train B only |
| `lfa_merge` / `stele_lfa_merge` | merge BA→W |
| `lfa_score` / `stele_lfa_score` | score |
| `lfa_memory` / `stele_lfa_memory` | activation save |
| `lfa_loop_plan` / `stele_lfa_loop_plan` | freeze_a→score |
| `dyl_range` / `stele_dyl_range` | rank range |
| `dyl_sample` / `stele_dyl_sample` | sample rank |
| `dyl_select` / `stele_dyl_select` | select at infer |
| `dyl_score` / `stele_dyl_score` | score |
| `dyl_searchfree` / `stele_dyl_searchfree` | search-free |
| `dyl_loop_plan` / `stele_dyl_loop_plan` | range→score |
| `lfa_dyl_shaped_report` | suite harness |

Modules: `stele_core.lorafa` + `stele_core.dylora`. MCP tool count: **1379**. CLI: `lfa-*` / `dyl-*`. Memory/searchfree are **report-only**. LoRA-FA ≠ LoRA+; DyLoRA ≠ AdaLoRA.

### 7.139 LoRA-XS + AsymmetryLoRA (UC-1407–1417)

| API / Tool | Behavior |
|---|---|
| `lxs_svd` / `stele_lxs_svd` | SVD-init frozen A,B |
| `lxs_r` / `stele_lxs_r` | allocate r×r R |
| `lxs_train` / `stele_lxs_train` | train R only |
| `lxs_score` / `stele_lxs_score` | score |
| `lxs_tiny` / `stele_lxs_tiny` | r² footprint |
| `lxs_loop_plan` / `stele_lxs_loop_plan` | svd→score |
| `asy_role` / `stele_asy_role` | A=extract, B=map |
| `asy_freeze_a` / `stele_asy_freeze_a` | freeze orthogonal A |
| `asy_train_b` / `stele_asy_train_b` | train B only |
| `asy_score` / `stele_asy_score` | score |
| `asy_bound` / `stele_asy_bound` | tighter bound |
| `asy_loop_plan` / `stele_asy_loop_plan` | role→score |
| `lxs_asy_shaped_report` | suite harness |

Modules: `stele_core.loraxs` + `stele_core.asymmetrylora`. MCP tool count: **1391**. CLI: `lxs-*` / `asy-*`. Tiny/bound are **report-only**. LoRA-XS ≠ VeRA; AsymmetryLoRA ≠ LoRA-FA.

### 7.140 LoRA-GA + MoRA (UC-1418–1428)

| API / Tool | Behavior |
|---|---|
| `lga_grad` / `stele_lga_grad` | sample gradients |
| `lga_svd` / `stele_lga_svd` | SVD on grads |
| `lga_scale` / `stele_lga_scale` | stable scale |
| `lga_score` / `stele_lga_score` | score |
| `lga_fast` / `stele_lga_fast` | faster convergence |
| `lga_loop_plan` / `stele_lga_loop_plan` | grad→score |
| `mor_square` / `stele_mor_square` | square M |
| `mor_compress` / `stele_mor_compress` | compress op |
| `mor_expand` / `stele_mor_expand` | expand op |
| `mor_score` / `stele_mor_score` | score |
| `mor_merge` / `stele_mor_merge` | mergeable |
| `mor_loop_plan` / `stele_mor_loop_plan` | square→score |
| `lga_mor_shaped_report` | suite harness |

Modules: `stele_core.loraga` + `stele_core.mora`. MCP tool count: **1403**. CLI: `lga-*` / `mor-*`. Fast/merge are **report-only**. LoRA-GA ≠ PiSSA; MoRA ≠ MemoRAG.

### 7.141 rsLoRA + LoKr (UC-1429–1439)

| API / Tool | Behavior |
|---|---|
| `rsl_rank` / `stele_rsl_rank` | declare rank |
| `rsl_scale` / `stele_rsl_scale` | 1/√r scale |
| `rsl_train` / `stele_rsl_train` | train |
| `rsl_score` / `stele_rsl_score` | score |
| `rsl_stable` / `stele_rsl_stable` | no collapse |
| `rsl_loop_plan` / `stele_rsl_loop_plan` | rank→score |
| `lkr_factors` / `stele_lkr_factors` | Kronecker factors |
| `lkr_kron` / `stele_lkr_kron` | Kronecker product |
| `lkr_vectorize` / `stele_lkr_vectorize` | vectorize |
| `lkr_score` / `stele_lkr_score` | score |
| `lkr_preserve` / `stele_lkr_preserve` | rank preserved |
| `lkr_loop_plan` / `stele_lkr_loop_plan` | factors→score |
| `rsl_lkr_shaped_report` | suite harness |

Modules: `stele_core.rslora` + `stele_core.lokr`. MCP tool count: **1415**. CLI: `rsl-*` / `lkr-*`. Stable/preserve are **report-only**. rsLoRA ≠ LoRA+; LoKr ≠ MoRA.

### 7.142 LoHa + FourierFT (UC-1440–1450)

| API / Tool | Behavior |
|---|---|
| `lha_pair` / `stele_lha_pair` | two low-rank pairs |
| `lha_hadamard` / `stele_lha_hadamard` | Hadamard product |
| `lha_train` / `stele_lha_train` | train four matrices |
| `lha_score` / `stele_lha_score` | score |
| `lha_express` / `stele_lha_express` | expressivity |
| `lha_loop_plan` / `stele_lha_loop_plan` | pair→score |
| `fft_basis` / `stele_fft_basis` | Fourier basis |
| `fft_coeff` / `stele_fft_coeff` | spectral coeffs |
| `fft_idft` / `stele_fft_idft` | inverse DFT |
| `fft_score` / `stele_fft_score` | score |
| `fft_sparse` / `stele_fft_sparse` | spectral sparse |
| `fft_loop_plan` / `stele_fft_loop_plan` | basis→score |
| `lha_fft_shaped_report` | suite harness |

Modules: `stele_core.loha` + `stele_core.fourierft`. MCP tool count: **1427**. CLI: `lha-*` / `fft-*`. Express/sparse are **report-only**. LoHa ≠ LoKr; FourierFT ≠ LoRA.

### 7.143 Houlsby + ReFT (UC-1451–1461)

| API / Tool | Behavior |
|---|---|
| `had_insert` / `stele_had_insert` | insert bottleneck |
| `had_freeze` / `stele_had_freeze` | freeze base |
| `had_train` / `stele_had_train` | train adapters |
| `had_score` / `stele_had_score` | score |
| `had_latency` / `stele_had_latency` | adds latency |
| `had_loop_plan` / `stele_had_loop_plan` | insert→score |
| `rft_repr` / `stele_rft_repr` | select layers |
| `rft_edit` / `stele_rft_edit` | LoReFT edit |
| `rft_train` / `stele_rft_train` | train |
| `rft_score` / `stele_rft_score` | score |
| `rft_weightless` / `stele_rft_weightless` | no weight ΔW |
| `rft_loop_plan` / `stele_rft_loop_plan` | repr→score |
| `had_rft_shaped_report` | suite harness |

Modules: `stele_core.houlsby` + `stele_core.reft`. MCP tool count: **1439**. CLI: `had-*` / `rft-*`. Latency/weightless are **report-only**. Houlsby ≠ LoHa; ReFT ≠ REFLECT.

### 7.144 OFT/BOFT + MiSS (UC-1462–1472)

| API / Tool | Behavior |
|---|---|
| `oft_ortho` / `stele_oft_ortho` | orthogonal block |
| `oft_butterfly` / `stele_oft_butterfly` | butterfly factors |
| `oft_train` / `stele_oft_train` | train |
| `oft_score` / `stele_oft_score` | score |
| `oft_energy` / `stele_oft_energy` | hypersphere |
| `oft_loop_plan` / `stele_oft_loop_plan` | ortho→score |
| `mss_shard` / `stele_mss_shard` | weight shards |
| `mss_share` / `stele_mss_share` | shared D |
| `mss_train` / `stele_mss_train` | train D |
| `mss_score` / `stele_mss_score` | score |
| `mss_pareto` / `stele_mss_pareto` | trade-off |
| `mss_loop_plan` / `stele_mss_loop_plan` | shard→score |
| `oft_mss_shaped_report` | suite harness |

Modules: `stele_core.oft` + `stele_core.miss`. MCP tool count: **1451**. CLI: `oft-*` / `mss-*`. Energy/pareto are **report-only**. OFT ≠ BitFit; MiSS ≠ Soft Prompt Mixtures.

### 7.145 DropLoRA + GaLore (UC-1473–1483)

| API / Tool | Behavior |
|---|---|
| `drl_rank` / `stele_drl_rank` | declare rank |
| `drl_mask` / `stele_drl_mask` | Bernoulli mask |
| `drl_train` / `stele_drl_train` | dynamic subspace |
| `drl_score` / `stele_drl_score` | score |
| `drl_infer` / `stele_drl_infer` | no extra cost |
| `drl_loop_plan` / `stele_drl_loop_plan` | rank→score |
| `gal_grad` / `stele_gal_grad` | capture grads |
| `gal_project` / `stele_gal_project` | project subspace |
| `gal_step` / `stele_gal_step` | optimizer step |
| `gal_score` / `stele_gal_score` | score |
| `gal_full` / `stele_gal_full` | full weights |
| `gal_loop_plan` / `stele_gal_loop_plan` | grad→score |
| `drl_gal_shaped_report` | suite harness |

Modules: `stele_core.droplora` + `stele_core.galore`. MCP tool count: **1463**. CLI: `drl-*` / `gal-*`. Infer/full are **report-only**. DropLoRA ≠ DoRA; GaLore ≠ LoRA-GA.

### 7.146 SHiRA + WaveFT (UC-1484–1494)

| API / Tool | Behavior |
|---|---|
| `shr_mask` / `stele_shr_mask` | sparse mask |
| `shr_tune` / `stele_shr_tune` | tune base % |
| `shr_switch` / `stele_shr_switch` | rapid switch |
| `shr_score` / `stele_shr_score` | score |
| `shr_fusion` / `stele_shr_fusion` | less concept loss |
| `shr_loop_plan` / `stele_shr_loop_plan` | mask→score |
| `wft_wave` / `stele_wft_wave` | wavelet basis |
| `wft_sparse` / `stele_wft_sparse` | sparse coeffs |
| `wft_idwt` / `stele_wft_idwt` | IDWT → ΔW |
| `wft_score` / `stele_wft_score` | score |
| `wft_granular` / `stele_wft_granular` | below LoRA min |
| `wft_loop_plan` / `stele_wft_loop_plan` | wave→score |
| `shr_wft_shaped_report` | suite harness |

Modules: `stele_core.shira` + `stele_core.waveft`. MCP tool count: **1475**. CLI: `shr-*` / `wft-*`. Fusion/granular are **report-only**. SHiRA ≠ DropLoRA; WaveFT ≠ FourierFT.

### 7.147 LoRA-Pro + Kron-LoRA (UC-1495–1505)

| API / Tool | Behavior |
|---|---|
| `lpr_equiv` / `stele_lpr_equiv` | equivalent gradient |
| `lpr_adjust` / `stele_lpr_adjust` | closed-form A/B adjust |
| `lpr_train` / `stele_lpr_train` | train |
| `lpr_score` / `stele_lpr_score` | score |
| `lpr_bridge` / `stele_lpr_bridge` | closer to FFT |
| `lpr_loop_plan` / `stele_lpr_loop_plan` | equiv→score |
| `krl_kron` / `stele_krl_kron` | Kronecker stage |
| `krl_lora` / `stele_krl_lora` | LoRA stage |
| `krl_train` / `stele_krl_train` | train hybrid |
| `krl_score` / `stele_krl_score` | score |
| `krl_compress` / `stele_krl_compress` | multiplicative compress |
| `krl_loop_plan` / `stele_krl_loop_plan` | kron→score |
| `lpr_krl_shaped_report` | suite harness |

Modules: `stele_core.lorapro` + `stele_core.kronlora`. MCP tool count: **1487**. CLI: `lpr-*` / `krl-*`. Bridge/compress are **report-only**. LoRA-Pro ≠ LoRA+ / LoRA-GA; Kron-LoRA ≠ LoKr.

### 7.148 MiLoRA + CorDA (UC-1506–1516)

| API / Tool | Behavior |
|---|---|
| `mil_svd` / `stele_mil_svd` | SVD split |
| `mil_minor` / `stele_mil_minor` | minor components |
| `mil_freeze` / `stele_mil_freeze` | freeze principal |
| `mil_score` / `stele_mil_score` | score |
| `mil_preserve` / `stele_mil_preserve` | preserve principal |
| `mil_loop_plan` / `stele_mil_loop_plan` | svd→score |
| `cda_cov` / `stele_cda_cov` | task covariance |
| `cda_mode` / `stele_cda_mode` | KPM / IPM |
| `cda_adapt` / `stele_cda_adapt` | adapt |
| `cda_score` / `stele_cda_score` | score |
| `cda_forget` / `stele_cda_forget` | less forgetting |
| `cda_loop_plan` / `stele_cda_loop_plan` | cov→score |
| `mil_cda_shaped_report` | suite harness |

Modules: `stele_core.milora` + `stele_core.corda`. MCP tool count: **1499**. CLI: `mil-*` / `cda-*`. Preserve/forget are **report-only**. MiLoRA ≠ PiSSA; CorDA ≠ PiSSA / MiLoRA.

### 7.149 LoftQ + LoRA-Dash (UC-1517–1527)

| API / Tool | Behavior |
|---|---|
| `lfq_quant` / `stele_lfq_quant` | quantize backbone |
| `lfq_init` / `stele_lfq_init` | LoRA init ≈ W−Q |
| `lfq_train` / `stele_lfq_train` | train |
| `lfq_score` / `stele_lfq_score` | score |
| `lfq_gap` / `stele_lfq_gap` | close QLoRA gap |
| `lfq_loop_plan` / `stele_lfq_loop_plan` | quant→score |
| `lds_prelaunch` / `stele_lds_prelaunch` | detect TSDs |
| `lds_tsd` / `stele_lds_tsd` | select TSDs |
| `lds_dash` / `stele_lds_dash` | amplify TSDs |
| `lds_score` / `stele_lds_score` | score |
| `lds_impact` / `stele_lds_impact` | maximize TSD |
| `lds_loop_plan` / `stele_lds_loop_plan` | prelaunch→score |
| `lfq_lds_shaped_report` | suite harness |

Modules: `stele_core.loftq` + `stele_core.loradash`. MCP tool count: **1511**. CLI: `lfq-*` / `lds-*`. Gap/impact are **report-only**. LoftQ ≠ QLoRA; LoRA-Dash ≠ LoRA-Pro / LoRA-XS.

### 7.150 Delta-LoRA + LoRA-One (UC-1528–1538)

| API / Tool | Behavior |
|---|---|
| `dlo_adapters` / `stele_dlo_adapters` | A/B adapters |
| `dlo_delta` / `stele_dlo_delta` | Δ(AB) |
| `dlo_propagate` / `stele_dlo_propagate` | push into W |
| `dlo_score` / `stele_dlo_score` | score |
| `dlo_highrank` / `stele_dlo_highrank` | high-rank capacity |
| `dlo_loop_plan` / `stele_dlo_loop_plan` | adapters→score |
| `lon_grad` / `stele_lon_grad` | one-step full grad |
| `lon_align` / `stele_lon_align` | subspace align init |
| `lon_train` / `stele_lon_train` | train |
| `lon_score` / `stele_lon_score` | score |
| `lon_immediate` / `stele_lon_immediate` | immediate align |
| `lon_loop_plan` / `stele_lon_loop_plan` | grad→score |
| `dlo_lon_shaped_report` | suite harness |

Modules: `stele_core.deltalora` + `stele_core.loraone`. MCP tool count: **1523**. CLI: `dlo-*` / `lon-*`. Highrank/immediate are **report-only**. Delta-LoRA ≠ DoRA / DropLoRA; LoRA-One ≠ LoRA-GA / LoRA-Pro.

### 7.151 OLoRA + LoRA-SP (UC-1539–1549)

| API / Tool | Behavior |
|---|---|
| `olr_qr` / `stele_olr_qr` | QR init |
| `olr_ortho` / `stele_olr_ortho` | orthonormal lock |
| `olr_train` / `stele_olr_train` | train |
| `olr_score` / `stele_olr_score` | score |
| `olr_stable` / `stele_olr_stable` | stable landscape |
| `olr_loop_plan` / `stele_olr_loop_plan` | qr→score |
| `lsp_select` / `stele_lsp_select` | half-select mask |
| `lsp_freeze` / `stele_lsp_freeze` | freeze rest |
| `lsp_train` / `stele_lsp_train` | train selected |
| `lsp_score` / `stele_lsp_score` | score |
| `lsp_memory` / `stele_lsp_memory` | lower memory |
| `lsp_loop_plan` / `stele_lsp_loop_plan` | select→score |
| `olr_lsp_shaped_report` | suite harness |

Modules: `stele_core.olora` + `stele_core.lorasp`. MCP tool count: **1535**. CLI: `olr-*` / `lsp-*`. Stable/memory are **report-only**. OLoRA ≠ LoRA-One; LoRA-SP ≠ SPoT / DropLoRA.

### 7.152 QPiSSA + MoSLoRA (UC-1550–1560)

| API / Tool | Behavior |
|---|---|
| `qps_quant` / `stele_qps_quant` | quantized backbone |
| `qps_principal` / `stele_qps_principal` | principal adapters |
| `qps_train` / `stele_qps_train` | train |
| `qps_score` / `stele_qps_score` | score |
| `qps_error` / `stele_qps_error` | smaller than QLoRA |
| `qps_loop_plan` / `stele_qps_loop_plan` | quant→score |
| `msl_split` / `stele_msl_split` | A/B split |
| `msl_mixer` / `stele_msl_mixer` | learnable mixer |
| `msl_train` / `stele_msl_train` | train |
| `msl_score` / `stele_msl_score` | score |
| `msl_fuse` / `stele_msl_fuse` | flexible fuse |
| `msl_loop_plan` / `stele_msl_loop_plan` | split→score |
| `qps_msl_shaped_report` | suite harness |

Modules: `stele_core.qpissa` + `stele_core.moslora`. MCP tool count: **1547**. CLI: `qps-*` / `msl-*`. Error/fuse are **report-only**. QPiSSA ≠ PiSSA / QLoRA; MoSLoRA ≠ MiSS / Soft Prompt Mixtures.

### 7.153 LoRA-drop + VB-LoRA (UC-1561–1571)

| API / Tool | Behavior |
|---|---|
| `ldr_eval` / `stele_ldr_eval` | output importance |
| `ldr_keep` / `stele_ldr_keep` | keep top layers |
| `ldr_share` / `stele_ldr_share` | share rest |
| `ldr_score` / `stele_ldr_score` | score |
| `ldr_prune` / `stele_ldr_prune` | ~half params |
| `ldr_loop_plan` / `stele_ldr_loop_plan` | eval→score |
| `vbl_bank` / `stele_vbl_bank` | vector bank |
| `vbl_topk` / `stele_vbl_topk` | top-k admixture |
| `vbl_compose` / `stele_vbl_compose` | compose LoRAs |
| `vbl_score` / `stele_vbl_score` | score |
| `vbl_extreme` / `stele_vbl_extreme` | extreme compression |
| `vbl_loop_plan` / `stele_vbl_loop_plan` | bank→score |
| `ldr_vbl_shaped_report` | suite harness |

Modules: `stele_core.loradrop` + `stele_core.vblora`. MCP tool count: **1559**. CLI: `ldr-*` / `vbl-*`. Prune/extreme are **report-only**. LoRA-drop ≠ DropLoRA; VB-LoRA ≠ VeRA / LoRA-XS.

### 7.154 OPLoRA + GeLoRA (UC-1572–1582)

| API / Tool | Behavior |
|---|---|
| `opl_proj` / `stele_opl_proj` | orthogonal bases |
| `opl_constrain` / `stele_opl_constrain` | orthogonal complement |
| `opl_train` / `stele_opl_train` | train |
| `opl_score` / `stele_opl_score` | score |
| `opl_forget` / `stele_opl_forget` | less forgetting |
| `opl_loop_plan` / `stele_opl_loop_plan` | proj→score |
| `gel_idim` / `stele_gel_idim` | intrinsic dim |
| `gel_rank` / `stele_gel_rank` | adaptive rank |
| `gel_train` / `stele_gel_train` | train |
| `gel_score` / `stele_gel_score` | score |
| `gel_budget` / `stele_gel_budget` | within budget |
| `gel_loop_plan` / `stele_gel_loop_plan` | idim→score |
| `opl_gel_shaped_report` | suite harness |

Modules: `stele_core.oplora` + `stele_core.gelora`. MCP tool count: **1571**. CLI: `opl-*` / `gel-*`. Forget/budget are **report-only**. OPLoRA ≠ OLoRA / alternating-update OPLoRA; GeLoRA ≠ GeoLoRA / GaLore.

### 7.155 GeoLoRA + RandLoRA (UC-1583–1593)

| API / Tool | Behavior |
|---|---|
| `geo_dyn` / `stele_geo_dyn` | dynamical state |
| `geo_budget` / `stele_geo_budget` | allocate budget |
| `geo_train` / `stele_geo_train` | single-pass train |
| `geo_score` / `stele_geo_score` | score |
| `geo_ortho` / `stele_geo_ortho` | exact ortho |
| `geo_loop_plan` / `stele_geo_loop_plan` | dyn→score |
| `rlo_bases` / `stele_rlo_bases` | random bases |
| `rlo_scale` / `stele_rlo_scale` | diagonal scales |
| `rlo_train` / `stele_rlo_train` | train |
| `rlo_score` / `stele_rlo_score` | score |
| `rlo_fullrank` / `stele_rlo_fullrank` | full-rank update |
| `rlo_loop_plan` / `stele_rlo_loop_plan` | bases→score |
| `geo_rlo_shaped_report` | suite harness |

Modules: `stele_core.geolora` + `stele_core.randlora`. MCP tool count: **1583**. CLI: `geo-*` / `rlo-*`. Ortho/fullrank are **report-only**. GeoLoRA ≠ GeLoRA; RandLoRA ≠ VeRA / LoRA.

### 7.156 LoRAShear + alternating OPLoRA (UC-1594–1604)

| API / Tool | Behavior |
|---|---|
| `lsh_graph` / `stele_lsh_graph` | dependency graph |
| `lsh_prune` / `stele_lsh_prune` | LHSPG structured prune |
| `lsh_recover` / `stele_lsh_recover` | knowledge recovery |
| `lsh_score` / `stele_lsh_score` | score |
| `lsh_footprint` / `stele_lsh_footprint` | footprint reduced |
| `lsh_loop_plan` / `stele_lsh_loop_plan` | graph→score |
| `aop_sub` / `stele_aop_sub` | LoRSum subproblem |
| `aop_alt` / `stele_aop_alt` | ALS steps |
| `aop_train` / `stele_aop_train` | train |
| `aop_score` / `stele_aop_score` | score |
| `aop_svd` / `stele_aop_svd` | near-SVDLoRA |
| `aop_loop_plan` / `stele_aop_loop_plan` | sub→score |
| `lsh_aop_shaped_report` | suite harness |

Modules: `stele_core.lorashear` + `stele_core.oplora_alt`. MCP tool count: **1595**. CLI: `lsh-*` / `aop-*`. Footprint/near-SVD are **report-only**. LoRAShear ≠ LoRA-SP; alternating OPLoRA ≠ orthogonal OPLoRA (`opl_*`).

### 7.157 LoRA-Init + LoRA-Null (UC-1605–1615)

| API / Tool | Behavior |
|---|---|
| `lin_tsd` / `stele_lin_tsd` | identify TSDs |
| `lin_init` / `stele_lin_init` | TSD init |
| `lin_train` / `stele_lin_train` | train |
| `lin_score` / `stele_lin_score` | score |
| `lin_fast` / `stele_lin_fast` | faster convergence |
| `lin_loop_plan` / `stele_lin_loop_plan` | tsd→score |
| `lnu_act` / `stele_lnu_act` | sample activations |
| `lnu_null` / `stele_lnu_null` | activation null space |
| `lnu_train` / `stele_lnu_train` | train |
| `lnu_score` / `stele_lnu_score` | score |
| `lnu_forget` / `stele_lnu_forget` | preserve knowledge |
| `lnu_loop_plan` / `stele_lnu_loop_plan` | act→score |
| `lin_lnu_shaped_report` | suite harness |

Modules: `stele_core.lorainit` + `stele_core.loranull`. MCP tool count: **1607**. CLI: `lin-*` / `lnu-*`. Fast/forget are **report-only**. LoRA-Init ≠ LoRA-Dash (`lds_*`); LoRA-Null ≠ MiLoRA (`mil_*`).

### 7.158 HydraLoRA + LoRA-LEGO (UC-1616–1626)

| API / Tool | Behavior |
|---|---|
| `hyd_share` / `stele_hyd_share` | shared A |
| `hyd_heads` / `stele_hyd_heads` | multi-B heads |
| `hyd_route` / `stele_hyd_route` | MoE route |
| `hyd_score` / `stele_hyd_score` | score |
| `hyd_nodomain` / `stele_hyd_nodomain` | no domain labels |
| `hyd_loop_plan` / `stele_hyd_loop_plan` | share→score |
| `llg_msu` / `stele_llg_msu` | collect MSUs |
| `llg_cluster` / `stele_llg_cluster` | rank-wise cluster |
| `llg_merge` / `stele_llg_merge` | assemble merge |
| `llg_score` / `stele_llg_score` | score |
| `llg_modular` / `stele_llg_modular` | modular merge |
| `llg_loop_plan` / `stele_llg_loop_plan` | msu→score |
| `hyd_llg_shaped_report` | suite harness |

Modules: `stele_core.hydralora` + `stele_core.loralego`. MCP tool count: **1619**. CLI: `hyd-*` / `llg-*`. Nodomain/modular are **report-only**. HydraLoRA ≠ AsymmetryLoRA (`asy_*`); LoRA-LEGO ≠ LoRAHub.

### 7.159 LoRAMoE + MoELoRA (UC-1627–1637)

| API / Tool | Behavior |
|---|---|
| `lme_plugin` / `stele_lme_plugin` | MoE LoRA plugin |
| `lme_balance` / `stele_lme_balance` | localized balance |
| `lme_route` / `stele_lme_route` | route experts |
| `lme_score` / `stele_lme_score` | score |
| `lme_forget` / `stele_lme_forget` | preserve world knowledge |
| `lme_loop_plan` / `stele_lme_loop_plan` | plugin→score |
| `mel_experts` / `stele_mel_experts` | LoRA experts |
| `mel_contrast` / `stele_mel_contrast` | contrastive specialize |
| `mel_gate` / `stele_mel_gate` | sparse gate |
| `mel_score` / `stele_mel_score` | score |
| `mel_sparse` / `stele_mel_sparse` | sparse activate |
| `mel_loop_plan` / `stele_mel_loop_plan` | experts→score |
| `lme_mel_shaped_report` | suite harness |

Modules: `stele_core.loramoe` + `stele_core.moelora`. MCP tool count: **1631**. CLI: `lme-*` / `mel-*`. Forget/sparse are **report-only**. LoRAMoE ≠ MoELoRA (`mel_*`); MoELoRA ≠ MiLoRA (`mil_*`).

### 7.160 LoraHub + MultiLoRA (UC-1638–1648)

| API / Tool | Behavior |
|---|---|
| `lhb_pool` / `stele_lhb_pool` | candidate LoRAs |
| `lhb_compose` / `stele_lhb_compose` | linear compose |
| `lhb_adapt` / `stele_lhb_adapt` | few-shot adapt w |
| `lhb_score` / `stele_lhb_score` | score |
| `lhb_nograd` / `stele_lhb_nograd` | gradient-free |
| `lhb_loop_plan` / `stele_lhb_loop_plan` | pool→score |
| `mlr_scale` / `stele_mlr_scale` | horizontal shards |
| `mlr_init` / `stele_mlr_init` | democratic init |
| `mlr_train` / `stele_mlr_train` | train |
| `mlr_score` / `stele_mlr_score` | score |
| `mlr_demo` / `stele_mlr_demo` | more democratic |
| `mlr_loop_plan` / `stele_mlr_loop_plan` | scale→score |
| `lhb_mlr_shaped_report` | suite harness |

Modules: `stele_core.lorahub` + `stele_core.multilora`. MCP tool count: **1643**. CLI: `lhb-*` / `mlr-*`. Nograd/demo are **report-only**. LoraHub ≠ LoRA-LEGO; MultiLoRA ≠ MiLoRA (`mil_*`).

### 7.161 MTL-LoRA + MALoRA (UC-1649–1659)

| API / Tool | Behavior |
|---|---|
| `mtl_task` / `stele_mtl_task` | multi-task set |
| `mtl_spec` / `stele_mtl_spec` | task-specific transforms |
| `mtl_share` / `stele_mtl_share` | dynamic share |
| `mtl_score` / `stele_mtl_score` | score |
| `mtl_interfere` / `stele_mtl_interfere` | less interference |
| `mtl_loop_plan` / `stele_mtl_loop_plan` | task→score |
| `mal_mix` / `stele_mal_mix` | asymmetric experts |
| `mal_down` / `stele_mal_down` | shared down-proj |
| `mal_up` / `stele_mal_up` | higher-rank up-proj |
| `mal_score` / `stele_mal_score` | score |
| `mal_eff` / `stele_mal_eff` | fewer params |
| `mal_loop_plan` / `stele_mal_loop_plan` | mix→score |
| `mtl_mal_shaped_report` | suite harness |

Modules: `stele_core.mtllora` + `stele_core.malora`. MCP tool count: **1655**. CLI: `mtl-*` / `mal-*`. Interfere/eff are **report-only**. MTL-LoRA ≠ MultiLoRA; MALoRA ≠ MoELoRA / AsymmetryLoRA.

### 7.162 LoRA-Mini + QDyLoRA (UC-1660–1670)

| API / Tool | Behavior |
|---|---|
| `lmi_split` / `stele_lmi_split` | split factors |
| `lmi_inner` / `stele_lmi_inner` | train inner only |
| `lmi_train` / `stele_lmi_train` | train |
| `lmi_score` / `stele_lmi_score` | score |
| `lmi_tiny` / `stele_lmi_tiny` | extreme compress |
| `lmi_loop_plan` / `stele_lmi_loop_plan` | split→score |
| `qdy_range` / `stele_qdy_range` | nested ranks |
| `qdy_quant` / `stele_qdy_quant` | 4/8-bit quant |
| `qdy_train` / `stele_qdy_train` | one-shot train |
| `qdy_score` / `stele_qdy_score` | score |
| `qdy_pick` / `stele_qdy_pick` | pick rank at infer |
| `qdy_loop_plan` / `stele_qdy_loop_plan` | range→score |
| `lmi_qdy_shaped_report` | suite harness |

Modules: `stele_core.loramini` + `stele_core.qdylora`. MCP tool count: **1667**. CLI: `lmi-*` / `qdy-*`. Tiny/pick are **report-only**. LoRA-Mini ≠ LoRA-XS; QDyLoRA ≠ QLoRA / DyLoRA alone.

### 7.163 LoRA-TSD + S-LoRA (UC-1671–1681)

| API / Tool | Behavior |
|---|---|
| `lts_tsd` / `stele_lts_tsd` | identify TSDs |
| `lts_init` / `stele_lts_init` | Init from TSDs |
| `lts_dash` / `stele_lts_dash` | Dash amplify |
| `lts_score` / `stele_lts_score` | score |
| `lts_combo` / `stele_lts_combo` | Init+Dash combo |
| `lts_loop_plan` / `stele_lts_loop_plan` | tsd→score |
| `slr_pool` / `stele_slr_pool` | host adapter pool |
| `slr_page` / `stele_slr_page` | Unified Paging |
| `slr_batch` / `stele_slr_batch` | heterogeneous batch |
| `slr_score` / `stele_slr_score` | score |
| `slr_scale` / `stele_slr_scale` | thousands scale |
| `slr_loop_plan` / `stele_slr_loop_plan` | pool→score |
| `lts_slr_shaped_report` | suite harness |

Modules: `stele_core.loratsd` + `stele_core.slora`. MCP tool count: **1679**. CLI: `lts-*` / `slr-*`. Combo/scale are **report-only**. LoRA-TSD ≠ LoRA-Dash / LoRA-Init alone; S-LoRA ≠ rsLoRA.

### 7.164 Compress-then-Serve + FLoRA (UC-1682–1692)

| API / Tool | Behavior |
|---|---|
| `cts_collect` / `stele_cts_collect` | collect adapters |
| `cts_basis` / `stele_cts_basis` | shared basis |
| `cts_scale` / `stele_cts_scale` | per-adapter scales |
| `cts_score` / `stele_cts_score` | score |
| `cts_cluster` / `stele_cts_cluster` | cluster-for-large |
| `cts_loop_plan` / `stele_cts_loop_plan` | collect→score |
| `flo_clients` / `stele_flo_clients` | federated clients |
| `flo_stack` / `stele_flo_stack` | stack A/B |
| `flo_agg` / `stele_flo_agg` | noise-free agg |
| `flo_score` / `stele_flo_score` | score |
| `flo_hetero` / `stele_flo_hetero` | hetero ranks |
| `flo_loop_plan` / `stele_flo_loop_plan` | clients→score |
| `cts_flo_shaped_report` | suite harness |

Modules: `stele_core.compressthenserve` + `stele_core.flora`. MCP tool count: **1691**. CLI: `cts-*` / `flo-*`. Cluster/hetero are **report-only**. Compress-then-Serve ≠ S-LoRA; FLoRA ≠ LoRA+ (`lrp_*`).

### 7.165 Punica + mLoRA (UC-1693–1703)

| API / Tool | Behavior |
|---|---|
| `pun_backbone` / `stele_pun_backbone` | shared backbone |
| `pun_sgmv` / `stele_pun_sgmv` | SGMV batch |
| `pun_sched` / `stele_pun_sched` | multi-tenant sched |
| `pun_score` / `stele_pun_score` | score |
| `pun_multi` / `stele_pun_multi` | multi-tenant flag |
| `pun_loop_plan` / `stele_pun_loop_plan` | backbone→score |
| `mla_pipe` / `stele_mla_pipe` | LoRA-aware pipe |
| `mla_batch` / `stele_mla_batch` | BatchLoRA |
| `mla_train` / `stele_mla_train` | train |
| `mla_score` / `stele_mla_score` | score |
| `mla_eff` / `stele_mla_eff` | completion-time flag |
| `mla_loop_plan` / `stele_mla_loop_plan` | pipe→score |
| `pun_mla_shaped_report` | suite harness |

Modules: `stele_core.punica` + `stele_core.mlora`. MCP tool count: **1703**. CLI: `pun-*` / `mla-*`. Multi/eff are **report-only**. Punica ≠ S-LoRA; mLoRA ≠ MiLoRA (`mil_*`) / MultiLoRA (`mlr_*`).

### 7.166 SwitchLoRA + Chain of LoRA (UC-1704–1714)

| API / Tool | Behavior |
|---|---|
| `swl_alloc` / `stele_swl_alloc` | allocate adapters |
| `swl_switch` / `stele_swl_switch` | switch dims |
| `swl_train` / `stele_swl_train` | train |
| `swl_score` / `stele_swl_score` | score |
| `swl_full` / `stele_swl_full` | full-rank mimic |
| `swl_loop_plan` / `stele_swl_loop_plan` | alloc→score |
| `col_tune` / `stele_col_tune` | tune link |
| `col_knot` / `stele_col_knot` | merge BA |
| `col_extend` / `stele_col_extend` | extend chain |
| `col_score` / `stele_col_score` | score |
| `col_gap` / `stele_col_gap` | FT-gap flag |
| `col_loop_plan` / `stele_col_loop_plan` | tune→score |
| `swl_col_shaped_report` | suite harness |

Modules: `stele_core.switchlora` + `stele_core.chainoflora`. MCP tool count: **1715**. CLI: `swl-*` / `col-*`. Full/gap are **report-only**. SwitchLoRA ≠ ReLoRA; COLA ≠ Chain-of-Density / CoVe.

### 7.167 DeLoRA + MELoRA (UC-1715–1725)

| API / Tool | Behavior |
|---|---|
| `dlr_norm` / `stele_dlr_norm` | normalize BA |
| `dlr_bound` / `stele_dlr_bound` | Frobenius λ |
| `dlr_train` / `stele_dlr_train` | train |
| `dlr_score` / `stele_dlr_score` | score |
| `dlr_robust` / `stele_dlr_robust` | robustness flag |
| `dlr_loop_plan` / `stele_dlr_loop_plan` | norm→score |
| `meo_mini` / `stele_meo_mini` | mini ensemble |
| `meo_diag` / `stele_meo_diag` | block-diagonal |
| `meo_train` / `stele_meo_train` | train |
| `meo_score` / `stele_meo_score` | score |
| `meo_rank` / `stele_meo_rank` | effective rank |
| `meo_loop_plan` / `stele_meo_loop_plan` | mini→score |
| `dlr_meo_shaped_report` | suite harness |

Modules: `stele_core.delora` + `stele_core.melora_ensemble`. MCP tool count: **1727**. CLI: `dlr-*` / `meo-*`. Robust/rank are **report-only**. DeLoRA ≠ Delta-LoRA (`dlo_*`); MELoRA ≠ MoELoRA (`mel_*`).

### 7.168 ReLoRA + ETHER (UC-1726–1736)

| API / Tool | Behavior |
|---|---|
| `rlr_warm` / `stele_rlr_warm` | full-rank warm-start |
| `rlr_merge` / `stele_rlr_merge` | merge + restart |
| `rlr_jagged` / `stele_rlr_jagged` | jagged LR / opt reset |
| `rlr_score` / `stele_rlr_score` | score |
| `rlr_high` / `stele_rlr_high` | high-rank flag |
| `rlr_loop_plan` / `stele_rlr_loop_plan` | warm→score |
| `eth_plane` / `stele_eth_plane` | hyperplane alloc |
| `eth_reflect` / `stele_eth_reflect` | reflect transform |
| `eth_train` / `stele_eth_train` | train |
| `eth_score` / `stele_eth_score` | score |
| `eth_plus` / `stele_eth_plus` | ETHER+ flag |
| `eth_loop_plan` / `stele_eth_loop_plan` | plane→score |
| `rlr_eth_shaped_report` | suite harness |

Modules: `stele_core.relora` + `stele_core.ether`. MCP tool count: **1739**. CLI: `rlr-*` / `eth-*`. High/plus are **report-only**. ReLoRA ≠ rsLoRA / COLA; ETHER ≠ VeRA / OFT.

### 7.169 LoRA-Composer + CARE-LoRA (UC-1737–1747)

| API / Tool | Behavior |
|---|---|
| `lco_concepts` / `stele_lco_concepts` | multi-concept LoRA set |
| `lco_inject` / `stele_lco_inject` | concept injection |
| `lco_isolate` / `stele_lco_isolate` | concept isolation |
| `lco_score` / `stele_lco_score` | score |
| `lco_free` / `stele_lco_free` | training-free flag |
| `lco_loop_plan` / `stele_lco_loop_plan` | concepts→score |
| `car_compress` / `stele_car_compress` | compress activations |
| `car_recon` / `stele_car_recon` | reconstruct grads |
| `car_train` / `stele_car_train` | train |
| `car_score` / `stele_car_score` | score |
| `car_mem` / `stele_car_mem` | activation-memory flag |
| `car_loop_plan` / `stele_car_loop_plan` | compress→score |
| `lco_car_shaped_report` | suite harness |

Modules: `stele_core.loracomposer` + `stele_core.carelora`. MCP tool count: **1751**. CLI: `lco-*` / `car-*`. Free/mem are **report-only**. LoRA-Composer ≠ COLA (`col_*`); CARE ≠ Compress-then-Serve (`cts_*`) / LoRA-FA (`lfa_*`).

### 7.170 LoRA.rar + SVFT (UC-1748–1758)

| API / Tool | Behavior |
|---|---|
| `lrr_pair` / `stele_lrr_pair` | subject–style LoRA pairs |
| `lrr_hyper` / `stele_lrr_hyper` | hypernet merge coeffs |
| `lrr_merge` / `stele_lrr_merge` | apply merge |
| `lrr_score` / `stele_lrr_score` | score |
| `lrr_fast` / `stele_lrr_fast` | realtime-merge flag |
| `lrr_loop_plan` / `stele_lrr_loop_plan` | pair→score |
| `svf_svd` / `stele_svf_svd` | singular-vector factor of W |
| `svf_sparse` / `stele_svf_sparse` | sparse coefficient pattern |
| `svf_train` / `stele_svf_train` | train coefficients |
| `svf_score` / `stele_svf_score` | score |
| `svf_geom` / `stele_svf_geom` | weight-dependent geometry flag |
| `svf_loop_plan` / `stele_svf_loop_plan` | svd→score |
| `lrr_svf_shaped_report` | suite harness |

Modules: `stele_core.lorarar` + `stele_core.svft`. MCP tool count: **1763**. CLI: `lrr-*` / `svf-*`. Fast/geom are **report-only**. LoRA.rar ≠ LoRA-Composer (`lco_*`) / ReLoRA (`rlr_*`); SVFT ≠ PiSSA / LoRA-XS (`lxs_*`).

### 7.171 FlyLoRA + NOLA (UC-1759–1769)

| API / Tool | Behavior |
|---|---|
| `fly_proj` / `stele_fly_proj` | frozen sparse random A |
| `fly_topk` / `stele_fly_topk` | rank-wise top-k experts |
| `fly_train` / `stele_fly_train` | train B |
| `fly_score` / `stele_fly_score` | score |
| `fly_implicit` / `stele_fly_implicit` | implicit-router flag |
| `fly_loop_plan` / `stele_fly_loop_plan` | proj→score |
| `nla_basis` / `stele_nla_basis` | frozen random bases |
| `nla_coeff` / `stele_nla_coeff` | mixture coefficients |
| `nla_train` / `stele_nla_train` | train coefficients |
| `nla_score` / `stele_nla_score` | score |
| `nla_compact` / `stele_nla_compact` | beyond-rank-1 flag |
| `nla_loop_plan` / `stele_nla_loop_plan` | basis→score |
| `fly_nla_shaped_report` | suite harness |

Modules: `stele_core.flylora` + `stele_core.nola`. MCP tool count: **1775**. CLI: `fly-*` / `nla-*`. Implicit/compact are **report-only**. FlyLoRA ≠ FLoRA (`flo_*`); NOLA ≠ VeRA / VB-LoRA (`vbl_*`).

### 7.172 MixLoRA + SuperLoRA (UC-1770–1780)

| API / Tool | Behavior |
|---|---|
| `mxl_experts` / `stele_mxl_experts` | LoRA experts in FFN |
| `mxl_route` / `stele_mxl_route` | top-k router |
| `mxl_attn` / `stele_mxl_attn` | independent attention LoRAs |
| `mxl_score` / `stele_mxl_score` | score |
| `mxl_balance` / `stele_mxl_balance` | load-balance flag |
| `mxl_loop_plan` / `stele_mxl_loop_plan` | experts→score |
| `spr_group` / `stele_spr_group` | group ΔW |
| `spr_fold` / `stele_spr_fold` | fold / reshape |
| `spr_factor` / `stele_spr_factor` | tensor / Kronecker factor |
| `spr_score` / `stele_spr_score` | score |
| `spr_unify` / `stele_spr_unify` | LoHA/LoKr unify flag |
| `spr_loop_plan` / `stele_spr_loop_plan` | group→score |
| `mxl_spr_shaped_report` | suite harness |

Modules: `stele_core.mixlora` + `stele_core.superlora`. MCP tool count: **1787**. CLI: `mxl-*` / `spr-*`. Balance/unify are **report-only**. MixLoRA ≠ MultiLoRA (`mlr_*`) / FlyLoRA (`fly_*`); SuperLoRA ≠ S-LoRA (`slr_*`) / LoHA (`lha_*`).

### 7.173 Tied-LoRA + QA-LoRA (UC-1781–1791)

| API / Tool | Behavior |
|---|---|
| `tld_tie` / `stele_tld_tie` | tie A/B across layers |
| `tld_select` / `stele_tld_select` | selective train/freeze |
| `tld_scale` / `stele_tld_scale` | per-layer scale vectors |
| `tld_score` / `stele_tld_score` | score |
| `tld_frac` / `stele_tld_frac` | fraction-of-LoRA flag |
| `tld_loop_plan` / `stele_tld_loop_plan` | tie→score |
| `qal_group` / `stele_qal_group` | column groups |
| `qal_quant` / `stele_qal_quant` | group-wise quantize |
| `qal_adapt` / `stele_qal_adapt` | shared group LoRA |
| `qal_score` / `stele_qal_score` | score |
| `qal_merge` / `stele_qal_merge` | INT4 merge-without-PTQ flag |
| `qal_loop_plan` / `stele_qal_loop_plan` | group→score |
| `tld_qal_shaped_report` | suite harness |

Modules: `stele_core.tiedlora` + `stele_core.qalora`. MCP tool count: **1799**. CLI: `tld-*` / `qal-*`. Frac/merge are **report-only**. Tied-LoRA ≠ VeRA (`vra_*`) / NOLA (`nla_*`); QA-LoRA ≠ QLoRA (`qlo_*`) / LoftQ (`lfq_*`).

### 7.174 Uni-LoRA + BoRA (UC-1792–1802)

| API / Tool | Behavior |
|---|---|
| `ulo_space` / `stele_ulo_space` | shared subspace |
| `ulo_iso` / `stele_ulo_iso` | isometric projection |
| `ulo_vec` / `stele_ulo_vec` | one trainable vector |
| `ulo_score` / `stele_ulo_score` | score |
| `ulo_one` / `stele_ulo_one` | one-vector flag |
| `ulo_loop_plan` / `stele_ulo_loop_plan` | space→score |
| `bor_row` / `stele_bor_row` | row magnitudes |
| `bor_col` / `stele_bor_col` | column magnitudes |
| `bor_train` / `stele_bor_train` | train |
| `bor_score` / `stele_bor_score` | score |
| `bor_sym` / `stele_bor_sym` | row/col symmetry flag |
| `bor_loop_plan` / `stele_bor_loop_plan` | row→score |
| `ulo_bor_shaped_report` | suite harness |

Modules: `stele_core.unilora` + `stele_core.bora`. MCP tool count: **1811**. CLI: `ulo-*` / `bor-*`. One/sym are **report-only**. Uni-LoRA ≠ Tied-LoRA (`tlo_*` / `tld_*`) / VeRA (`vra_*`); BoRA ≠ DoRA (`dora_*`).

### 7.175 Q-GaLore + LoRA-Flow (UC-1803–1813)

| API / Tool | Behavior |
|---|---|
| `qga_weight` / `stele_qga_weight` | INT8 weights |
| `qga_proj` / `stele_qga_proj` | INT4 gradient projection |
| `qga_lazy` / `stele_qga_lazy` | layer-adaptive SVD |
| `qga_score` / `stele_qga_score` | score |
| `qga_mem` / `stele_qga_mem` | 16GB-class GPU flag |
| `qga_loop_plan` / `stele_qga_loop_plan` | weight→score |
| `lfw_pool` / `stele_lfw_pool` | LoRA skill pool |
| `lfw_gate` / `stele_lfw_gate` | tiny fusion gate |
| `lfw_token` / `stele_lfw_token` | token-level mix |
| `lfw_score` / `stele_lfw_score` | score |
| `lfw_few` / `stele_lfw_few` | ~200-shot flag |
| `lfw_loop_plan` / `stele_lfw_loop_plan` | pool→score |
| `qga_lfw_shaped_report` | suite harness |

Modules: `stele_core.qgalore` + `stele_core.loraflow`. MCP tool count: **1823**. CLI: `qga-*` / `lfw-*`. Mem/few are **report-only**. Q-GaLore ≠ GaLore (`gal_*`) / QLoRA (`qlo_*`); LoRA-Flow ≠ FLoRA (`flo_*`) / S-LoRA (`slr_*`).

### 7.176 RoSA + ABBA (UC-1814–1824)

| API / Tool | Behavior |
|---|---|
| `ros_rank` / `stele_ros_rank` | low-rank branch |
| `ros_sparse` / `stele_ros_sparse` | sparse residual |
| `ros_train` / `stele_ros_train` | joint train |
| `ros_score` / `stele_ros_score` | score |
| `ros_fft` / `stele_ros_fft` | FFT-recovery flag |
| `ros_loop_plan` / `stele_ros_loop_plan` | rank→score |
| `abb_left` / `stele_abb_left` | first low-rank factor |
| `abb_right` / `stele_abb_right` | second low-rank factor |
| `abb_hadamard` / `stele_abb_hadamard` | Hadamard product |
| `abb_score` / `stele_abb_score` | score |
| `abb_expr` / `stele_abb_expr` | W0-free expressivity flag |
| `abb_loop_plan` / `stele_abb_loop_plan` | left→score |
| `ros_abb_shaped_report` | suite harness |

Modules: `stele_core.rosa` + `stele_core.abba`. MCP tool count: **1835**. CLI: `ros-*` / `abb-*`. Fft/expr are **report-only**. RoSA ≠ LoRA / DoRA (`dora_*`); ABBA ≠ LoHA (`lha_*`) / HiRA.

### 7.177 BoHA + SMoA (UC-1825–1835)

| API / Tool | Behavior |
|---|---|
| `bha_split` / `stele_bha_split` | block partition |
| `bha_hadamard` / `stele_bha_hadamard` | per-block W⊙BA |
| `bha_train` / `stele_bha_train` | train |
| `bha_score` / `stele_bha_score` | score |
| `bha_local` / `stele_bha_local` | localized-rank flag |
| `bha_loop_plan` / `stele_bha_loop_plan` | split→score |
| `smo_struct` / `stele_smo_struct` | disjoint subspaces |
| `smo_mod` / `stele_smo_mod` | structured modulation |
| `smo_train` / `stele_smo_train` | train |
| `smo_score` / `stele_smo_score` | score |
| `smo_rank` / `stele_smo_rank` | high-rank flag |
| `smo_loop_plan` / `stele_smo_loop_plan` | struct→score |
| `bha_smo_shaped_report` | suite harness |

Modules: `stele_core.boha` + `stele_core.smoa`. MCP tool count: **1847**. CLI: `bha-*` / `smo-*`. Local/rank are **report-only**. BoHA ≠ LoHA (`lha_*`) / ABBA (`abb_*`); SMoA ≠ MoRA (`mor_*`) / MixLoRA (`mxl_*`).

### 7.178 GLoRA + PeriodicLoRA (UC-1836–1846)

| API / Tool | Behavior |
|---|---|
| `glo_prompt` / `stele_glo_prompt` | generalized prompt |
| `glo_scale` / `stele_glo_scale` | weight/activation scale |
| `glo_search` / `stele_glo_search` | layer-wise search |
| `glo_score` / `stele_glo_score` | score |
| `glo_zero` / `stele_glo_zero` | zero extra infer flag |
| `glo_loop_plan` / `stele_glo_loop_plan` | prompt→score |
| `plr_stage` / `stele_plr_stage` | periodic stage |
| `plr_merge` / `stele_plr_merge` | unload BA into W |
| `plr_reset` / `stele_plr_reset` | reinit LoRA |
| `plr_score` / `stele_plr_score` | score |
| `plr_rank` / `stele_plr_rank` | accumulated-rank flag |
| `plr_loop_plan` / `stele_plr_loop_plan` | stage→score |
| `glo_plr_shaped_report` | suite harness |

Modules: `stele_core.glora` + `stele_core.periodiclora`. MCP tool count: **1859**. CLI: `glo-*` / `plr-*`. Zero/rank are **report-only**. GLoRA ≠ GaLore (`gal_*`) / FLoRA (`flo_*`); PeriodicLoRA ≠ ReLoRA (`rlr_*`) / LoRA-Pro (`lpr_*`).

### 7.179 HiRA + concurrent PLoRA (UC-1847–1857)

| API / Tool | Behavior |
|---|---|
| `hir_base` / `stele_hir_base` | freeze W0 |
| `hir_factors` / `stele_hir_factors` | low-rank A, B |
| `hir_hadamard` / `stele_hir_hadamard` | W0 ⊙ (BA) |
| `hir_score` / `stele_hir_score` | score |
| `hir_merge` / `stele_hir_merge` | merge-into-W0 flag |
| `hir_loop_plan` / `stele_hir_loop_plan` | base→score |
| `cnl_pack` / `stele_cnl_pack` | pack concurrent adapters |
| `cnl_fuse` / `stele_cnl_fuse` | fuse batched forward |
| `cnl_train` / `stele_cnl_train` | concurrent train |
| `cnl_score` / `stele_cnl_score` | score |
| `cnl_hw` / `stele_cnl_hw` | util flag |
| `cnl_loop_plan` / `stele_cnl_loop_plan` | pack→score |
| `hir_cnl_shaped_report` | suite harness |

Modules: `stele_core.hira` + `stele_core.concurrentlora`. MCP tool count: **1871**. CLI: `hir-*` / `cnl-*`. Merge/hw are **report-only**. HiRA ≠ SHiRA (`shr_*`) / LoHA (`lha_*`); PLoRA ≠ PeriodicLoRA (`plr_*`) / MixLoRA (`mxl_*`).

### 7.180 LongLoRA + LISA (UC-1858–1868)

| API / Tool | Behavior |
|---|---|
| `llr_window` / `stele_llr_window` | long-context window |
| `llr_shift` / `stele_llr_shift` | S2-Attn shift |
| `llr_lora` / `stele_llr_lora` | LoRA adapter |
| `llr_score` / `stele_llr_score` | score |
| `llr_sparse` / `stele_llr_sparse` | sparse-train flag |
| `llr_loop_plan` / `stele_llr_loop_plan` | window→score |
| `lis_layers` / `stele_lis_layers` | layer set |
| `lis_sample` / `stele_lis_sample` | importance sample |
| `lis_unfreeze` / `stele_lis_unfreeze` | unfreeze sampled |
| `lis_score` / `stele_lis_score` | score |
| `lis_memory` / `stele_lis_memory` | optimizer-memory flag |
| `lis_loop_plan` / `stele_lis_loop_plan` | layers→score |
| `llr_lis_shaped_report` | suite harness |

Modules: `stele_core.longlora` + `stele_core.lisa`. MCP tool count: **1883**. CLI: `llr-*` / `lis-*`. Sparse/memory are **report-only**. LongLoRA ≠ LoRA-FA (`lfa_*`) / HiRA (`hir_*`); LISA ≠ LoftQ (`lfq_*`) / MiLoRA (`mil_*`).

### 7.181 NLoRA + ROSA random subspace (UC-1869–1879)

| API / Tool | Behavior |
|---|---|
| `nlr_landmark` / `stele_nlr_landmark` | Nyström landmarks |
| `nlr_nystrom` / `stele_nlr_nystrom` | Nyström sketch |
| `nlr_init` / `stele_nlr_init` | init from sketch |
| `nlr_score` / `stele_nlr_score` | score |
| `nlr_cheap` / `stele_nlr_cheap` | cheaper-than-SVD flag |
| `nlr_loop_plan` / `stele_nlr_loop_plan` | landmark→score |
| `rsa_subspace` / `stele_rsa_subspace` | random subspace |
| `rsa_project` / `stele_rsa_project` | project into subspace |
| `rsa_train` / `stele_rsa_train` | train in subspace |
| `rsa_score` / `stele_rsa_score` | score |
| `rsa_express` / `stele_rsa_express` | expressiveness flag |
| `rsa_loop_plan` / `stele_rsa_loop_plan` | subspace→score |
| `nlr_rsa_shaped_report` | suite harness |

Modules: `stele_core.nlora` + `stele_core.randsub`. MCP tool count: **1895**. CLI: `nlr-*` / `rsa-*`. Cheap/express are **report-only**. NLoRA ≠ S-LoRA (`slr_*`) / PiSSA (`pis_*`); ROSA ≠ RoSA (`ros_*`) / rsLoRA (`rsl_*`).

### 7.182 HRA + Hybrid PEFT (UC-1880–1890)

| API / Tool | Behavior |
|---|---|
| `hra_house` / `stele_hra_house` | Householder vectors |
| `hra_reflect` / `stele_hra_reflect` | compose reflections |
| `hra_train` / `stele_hra_train` | train adapter |
| `hra_score` / `stele_hra_score` | score |
| `hra_ortho` / `stele_hra_ortho` | orthogonal-stable flag |
| `hra_loop_plan` / `stele_hra_loop_plan` | house→score |
| `hyb_lora` / `stele_hyb_lora` | LoRA-GA branch |
| `hyb_boft` / `stele_hyb_boft` | BOFT branch |
| `hyb_fuse` / `stele_hyb_fuse` | fuse by grad-norm |
| `hyb_score` / `stele_hyb_score` | score |
| `hyb_stable` / `stele_hyb_stable` | stability flag |
| `hyb_loop_plan` / `stele_hyb_loop_plan` | lora→score |
| `hra_hyb_shaped_report` | suite harness |

Modules: `stele_core.hra` + `stele_core.hybridpeft`. MCP tool count: **1907**. CLI: `hra-*` / `hyb-*`. Ortho/stable are **report-only**. HRA ≠ HiRA (`hir_*`) / OFT (`oft_*`); Hybrid PEFT ≠ LoRA-GA (`lga_*`) / OFT (`oft_*`).

### 7.183 LoRTA + C-LoRA (UC-1891–1901)

| API / Tool | Behavior |
|---|---|
| `lrt_tensor` / `stele_lrt_tensor` | 5th-order update tensor |
| `lrt_cp` / `stele_lrt_cp` | CP decompose |
| `lrt_share` / `stele_lrt_share` | share factors |
| `lrt_score` / `stele_lrt_score` | score |
| `lrt_compact` / `stele_lrt_compact` | fewer-params flag |
| `lrt_loop_plan` / `stele_lrt_loop_plan` | tensor→score |
| `clo_route` / `stele_clo_route` | shared continual route |
| `clo_task` / `stele_clo_task` | bind sequential task |
| `clo_ortho` / `stele_clo_ortho` | orthogonality vs prior |
| `clo_score` / `stele_clo_score` | score |
| `clo_forget` / `stele_clo_forget` | less-forgetting flag |
| `clo_loop_plan` / `stele_clo_loop_plan` | route→score |
| `lrt_clo_shaped_report` | suite harness |

Modules: `stele_core.lorta` + `stele_core.clora`. MCP tool count: **1919**. CLI: `lrt-*` / `clo-*`. Compact/forget are **report-only**. LoRTA ≠ LoRA-TSD (`tsd_*`) / HiRA (`hir_*`); C-LoRA ≠ ConcurrentLoRA (`cnl_*`) / LoRTA (`lrt_*`).

### 7.184 ALoRA + LN Tuning (UC-1902–1912)

| API / Tool | Behavior |
|---|---|
| `alo_init` / `stele_alo_init` | equal-rank gates |
| `alo_ablate` / `stele_alo_ablate` | AB-LoRA importance |
| `alo_prune` / `stele_alo_prune` | prune + realloc |
| `alo_score` / `stele_alo_score` | score |
| `alo_realloc` / `stele_alo_realloc` | dynamic-realloc flag |
| `alo_loop_plan` / `stele_alo_loop_plan` | init→score |
| `lnt_attn` / `stele_lnt_attn` | attention LN select |
| `lnt_scale` / `stele_lnt_scale` | LN gamma |
| `lnt_train` / `stele_lnt_train` | LN-only train |
| `lnt_score` / `stele_lnt_score` | score |
| `lnt_cheap` / `stele_lnt_cheap` | cheaper-than-LoRA flag |
| `lnt_loop_plan` / `stele_lnt_loop_plan` | attn→score |
| `alo_lnt_shaped_report` | suite harness |

Modules: `stele_core.alora` + `stele_core.lntuning`. MCP tool count: **1931**. CLI: `alo-*` / `lnt-*`. Realloc/cheap are **report-only**. ALoRA ≠ AdaLoRA (`adl_*`) / C-LoRA (`clo_*`); LN Tuning ≠ LoRA-Null (`lnu_*`) / ALoRA (`alo_*`).

### 7.185 LoRAFusion + TeRA (UC-1913–1923)

| API / Tool | Behavior |
|---|---|
| `lfu_split` / `stele_lfu_split` | graph split |
| `lfu_fuse` / `stele_lfu_fuse` | kernel fuse |
| `lfu_batch` / `stele_lfu_batch` | multi-job pack |
| `lfu_score` / `stele_lfu_score` | score |
| `lfu_speed` / `stele_lfu_speed` | faster-than-mLoRA flag |
| `lfu_loop_plan` / `stele_lfu_loop_plan` | split→score |
| `ter_tucker` / `stele_ter_tucker` | tensorize ΔW |
| `ter_freeze` / `stele_ter_freeze` | freeze random factors |
| `ter_scale` / `stele_ter_scale` | per-layer scales |
| `ter_score` / `stele_ter_score` | score |
| `ter_highrank` / `stele_ter_highrank` | high-rank-cheap flag |
| `ter_loop_plan` / `stele_ter_loop_plan` | tucker→score |
| `lfu_ter_shaped_report` | suite harness |

Modules: `stele_core.lorafusion` + `stele_core.tera`. MCP tool count: **1943**. CLI: `lfu-*` / `ter-*`. Speed/highrank are **report-only**. LoRAFusion ≠ Hybrid PEFT (`hyb_*`) / FlyLoRA (`fly_*`); TeRA ≠ LoRTA (`lrt_*`) / VeRA (`vra_*`).

### 7.186 TensLoRA + AdaZeta (UC-1924–1934)

| API / Tool | Behavior |
|---|---|
| `tnl_stack` / `stele_tnl_stack` | stack LoRA updates |
| `tnl_tucker` / `stele_tnl_tucker` | Tucker factor |
| `tnl_mode` / `stele_tnl_mode` | per-mode ranks |
| `tnl_score` / `stele_tnl_score` | score |
| `tnl_budget` / `stele_tnl_budget` | mode-specific budget flag |
| `tnl_loop_plan` / `stele_tnl_loop_plan` | stack→score |
| `azt_tt` / `stele_azt_tt` | tensor-train adapter |
| `azt_ff` / `stele_azt_ff` | fast-forward contraction |
| `azt_query` / `stele_azt_query` | adaptive ZO queries |
| `azt_score` / `stele_azt_score` | score |
| `azt_mem` / `stele_azt_mem` | ZO-memory flag |
| `azt_loop_plan` / `stele_azt_loop_plan` | tt→score |
| `tnl_azt_shaped_report` | suite harness |

Modules: `stele_core.tenslora` + `stele_core.adazeta`. MCP tool count: **1955**. CLI: `tnl-*` / `azt-*`. Budget/mem are **report-only**. TensLoRA ≠ LoRTA (`lrt_*`) / TeRA (`ter_*`); AdaZeta ≠ AdaLoRA (`adl_*`) / TensLoRA (`tnl_*`).

### 7.187 FacT + LoTR (UC-1935–1945)

| API / Tool | Behavior |
|---|---|
| `fct_tensor` / `stele_fct_tensor` | 3D increment tensor |
| `fct_tt` / `stele_fct_tt` | Tensor-Train factors |
| `fct_tucker` / `stele_fct_tucker` | Tucker factors |
| `fct_score` / `stele_fct_score` | score |
| `fct_tiny` / `stele_fct_tiny` | tiny-params flag |
| `fct_loop_plan` / `stele_fct_loop_plan` | tensor→score |
| `ltr_stack` / `stele_ltr_stack` | stack Q/V across depth |
| `ltr_core` / `stele_ltr_core` | shared core tensor |
| `ltr_share` / `stele_ltr_share` | share left/right |
| `ltr_score` / `stele_ltr_score` | score |
| `ltr_deep` / `stele_ltr_deep` | better-for-deep flag |
| `ltr_loop_plan` / `stele_ltr_loop_plan` | stack→score |
| `fct_ltr_shaped_report` | suite harness |

Modules: `stele_core.fact` + `stele_core.lotr`. MCP tool count: **1967**. CLI: `fct-*` / `ltr-*`. Tiny/deep are **report-only**. FacT ≠ TensLoRA (`tnl_*`) / LoRTA (`lrt_*`); LoTR ≠ LoRTA (`lrt_*`) / FacT (`fct_*`).

### 7.188 CaRA + LoRETTA (UC-1946–1956)

| API / Tool | Behavior |
|---|---|
| `cra_mha` / `stele_cra_mha` | MHA tensor |
| `cra_ffn` / `stele_cra_ffn` | FFN tensor |
| `cra_cpd` / `stele_cra_cpd` | CP decompose |
| `cra_score` / `stele_cra_score` | score |
| `cra_heads` / `stele_cra_heads` | head-mode flag |
| `cra_loop_plan` / `stele_cra_loop_plan` | mha→score |
| `ltt_adp` / `stele_ltt_adp` | tensorized adapter |
| `ltt_rep` / `stele_ltt_rep` | TT reparam |
| `ltt_tt` / `stele_ltt_tt` | TT cores |
| `ltt_score` / `stele_ltt_score` | score |
| `ltt_tiny` / `stele_ltt_tiny` | sub-MB flag |
| `ltt_loop_plan` / `stele_ltt_loop_plan` | adp→score |
| `cra_ltt_shaped_report` | suite harness |

Modules: `stele_core.cara` + `stele_core.loretta`. MCP tool count: **1979**. CLI: `cra-*` / `ltt-*`. Heads/tiny are **report-only**. CaRA ≠ CARE-LoRA (`car_*`) / FacT (`fct_*`); LoRETTA ≠ LoRTA (`lrt_*`) / LoTR (`ltr_*`).

### 7.189 C3A + BOFT (UC-1957–1967)

| API / Tool | Behavior |
|---|---|
| `c3a_kernel` / `stele_c3a_kernel` | convolution kernel |
| `c3a_circ` / `stele_c3a_circ` | circulant ΔW |
| `c3a_fft` / `stele_c3a_fft` | FFT multiply |
| `c3a_score` / `stele_c3a_score` | score |
| `c3a_rank` / `stele_c3a_rank` | high-rank flag |
| `c3a_loop_plan` / `stele_c3a_loop_plan` | kernel→score |
| `bof_block` / `stele_bof_block` | butterfly block |
| `bof_orth` / `stele_bof_orth` | orthogonal factor |
| `bof_butter` / `stele_bof_butter` | butterfly factorize |
| `bof_score` / `stele_bof_score` | score |
| `bof_full` / `stele_bof_full` | full-orthogonal flag |
| `bof_loop_plan` / `stele_bof_loop_plan` | block→score |
| `c3a_bof_shaped_report` | suite harness |

Modules: `stele_core.c3a` + `stele_core.boft`. MCP tool count: **1991**. CLI: `c3a-*` / `bof-*`. Rank/full are **report-only**. C3A ≠ CaRA (`cra_*`); BOFT ≠ BitFit (`bft_*`) / OFT (`oft_*`).

### 7.190 SDT + MEFT (UC-1968–1978)

| API / Tool | Behavior |
|---|---|
| `sdt_dim` / `stele_sdt_dim` | sparse SSM dimension |
| `sdt_mask` / `stele_sdt_mask` | sparse mask |
| `sdt_tune` / `stele_sdt_tune` | sparse dimension tune |
| `sdt_score` / `stele_sdt_score` | score |
| `sdt_ssm` / `stele_sdt_ssm` | SSM-targeted flag |
| `sdt_loop_plan` / `stele_sdt_loop_plan` | dim→score |
| `mef_adapt` / `stele_mef_adapt` | sparse adapter |
| `mef_route` / `stele_mef_route` | MoE / key-expert router |
| `mef_fetch` / `stele_mef_fetch` | sparse neuron fetch |
| `mef_score` / `stele_mef_score` | score |
| `mef_cpu` / `stele_mef_cpu` | CPU-offload flag |
| `mef_loop_plan` / `stele_mef_loop_plan` | adapt→score |
| `sdt_mef_shaped_report` | suite harness |

Modules: `stele_core.sdt` + `stele_core.meft`. MCP tool count: **2003**. CLI: `sdt-*` / `mef-*`. SSM/CPU flags are **report-only**. SDT ≠ LoRA (`lora_*`); MEFT ≠ MiSS (`mss_*`).

Writes require `--now` (caller clock).








Tool descriptions must instruct: distill before ADD (FF-2); env-check `env_assumptions` before replaying workflows (FF-4).

---

## 8. Export (C3) and producers (C1)

### 8.1 Pack format

```
pack/
  manifest.json    # pack_version, purpose, audience_tier, scope, created_at,
                   # expiry, source_store_id, entry_count, redaction_report_digest,
                   # may_be_outdated
  entries/         # redacted entries, audience-tier filtered
  adaptation.json  # substitutions[], env_assumptions[], re_derive[]
  provenance/      # optional appendix: source pointers only
  redaction_report.json
```

### 8.2 Redaction + verify (UC-11)

Export pipeline: secret patterns → subject allowlist → strip equipment lines to `re_derive` (FF-13) → stamps. Failures block export (no force flag).

`verify_pack(dir)`: stamps present, audience valid, secret scan clean, no top-level trajectory fields.

Audience tiers (FF-10): `expert` · `practitioner` · `novice`.

### 8.3 Hydrate + transfer eval (UC-17)

`hydrate(pack, actor, promote?, evidence?)`: ADD payloads with `provenance.agent=pack-hydrate` (cannot self-promote); optional external promote. `foreign_pack_transfer_eval` measures with/without lift — **not** a WTP claim.

### 8.4 Producers

| Producer | Function | Notes |
|---|---|---|
| Judgment | `judgment_entry` | wire dict only; caller supplies the payload |
| operator receipt | `project_receipt` | C8 causal map; private paths rejected |
| Migration | `migration_entry` | `agent=migration`; batch human_signoff |
| memorywire out | `to_memorywire_remember` | episodic/procedural map from layer; no dep |
| memorywire in | `from_memorywire_recall_hits` | stubs; `foreign` when no `stele_id` |

---

## 9. Test strategy

| Test | Asserts | Constraint / UC |
|---|---|---|
| `test_purity.py::test_core_static_import_scan` | stdlib + stele_core only | C1 |
| `test_purity.py::test_write_path_zero_llm_zero_network` | embedder 0; sockets blocked | C5 |
| `test_schema.py::test_incomplete_entries_rejected` | incomplete raise; round-trip | C6 |
| `test_governance.py::test_self_graded_never_promotes` | self-issue rejected | C7 |
| `test_retrieval.py::test_quarantine_never_served_and_filters_applied` | promoted-only + filters | C2 |
| `test_store.py::test_index_rebuild_is_lossless` | drop+rebuild identical | C4 |
| `test_export.py::test_pack_is_redacted_versioned_scoped` | stamps + redaction | C3 |
| `test_receipt_adapter.py::…` | C8 projection + private reject | C8 |
| `test_joint.py::test_full_lifecycle_all_constraints` | C1–C8 on one store | joint |
| `test_contested_and_env_gate.py` | contested + env gate | UC-13,14 |
| `test_v013_features.py` … `test_v017_features.py` | living ledger, packs, ops | UC-15–24 |
| `test_v100_features.py` | schema, snapshot, doctor, CLI, memorywire | UC-28–32 |
| `test_v110_features.py` | purge, batch, diff, trusted_sources, membench | UC-33–37 |
| `test_v120_features.py` | entangled, hygiene, prefer_fresh, governance report | UC-38–40 |
| `test_v130_features.py` | principal_scopes, forget_compliance, gatemem | UC-41–43 |
| `test_v140_features.py` | lineage, belief_at, conflict_surface, memoryagent | UC-44–47 |
| `test_v150_features.py` | injection_scan, gates, budget_plan, maple | UC-48–50 |
| `test_v160_features.py` | seal, receipt, replay, memmark | UC-51–54 |
| `test_v170_features.py` | lifecycle, revoke, pack seal, explain | UC-55–59 |
| `test_v180_features.py` | blast, merge_classify, path_trust | UC-60–64 |
| `test_v190_features.py` | journal chain, spread, density, retention | UC-65–69 |
| `test_v200_features.py` | health, release, cues, sqlite | UC-70–74 |
| `test_v210_features.py` | receipts, import, lineage | UC-75–79 |
| `test_v220_features.py` | execution, authority, closure | UC-80–84 |
| `test_v230_features.py` | cascade, withdraw, repair plan | UC-85–89 |
| `test_v240_features.py` | roles, fact interface, dual channel | UC-90–94 |
| `test_v250_features.py` | commits, diff, copyability | UC-95–99 |
| `packages/stele-mcp/tests/test_server.py` | 79 named tools (AST) | UC-27 |
| `examples/proof_run.py` | end-to-end PASS/FAIL gate | success_oracle |

Paths resolve under `packages/stele-core/tests/` unless noted. Provenance rule: `ai_generated` alone never marks a constraint PASS.

---

## 10. Non-decisions (explicitly deferred)

- SQLite/embedded-DB mirror of the SoT (only if file-store scale fails; C4 unchanged).
- Remote/multi-store sync and hosted deployment.
- REFLECT **auto**-resolution (blocked on R2) — evidenced resolve is shipped.
- Semantic-index model choice — permanently caller `Embedder`.
- Pack **pricing / WTP** product claims (non-goal); scoped transfer *lift* harness is shipped.
- Bulk private receipt-inventory migration (C8 forbids).
- Full MemoryArena gym integration (shaped smoke + task harnesses ship; research gym is post-v1).

**Shipped that §10 previously deferred:** pack hydrate (scoped), cost/latency harness (`measure_search_overhead`), contested resolution UX (`resolve_contested`), MCP `attach` / snapshot / doctor / entry_schema, CLI, memorywire projection, JSON Schema export.

---

## 11. Spec ↔ PRD capability index

| PRD UC | Primary TECH_SPEC section |
|---|---|
| UC-1..12 | §§3–8 core |
| UC-13 | §5.4 |
| UC-14..16,18–22 | §6 |
| UC-17 | §8.3 |
| UC-23..24 | §3.5, §7.4 |
| UC-25..26 | §4.4–4.5, §8.4 |
| UC-27 | §7 |
| UC-28 | §7.5 |
| UC-29 | §2 `schema_json.py`, §7.4 |
| UC-30 | §7.4 snapshot |
| UC-31 | §8.4 |
| UC-32 | §7.4 doctor |
| UC-33–36 | §7.6 |
| UC-37 | §9 harness |
| UC-38–40 | §7.7 |
| UC-41–43 | §7.8 |
| UC-44–47 | §7.9 |
| UC-48–50 | §7.10 |
| UC-51–54 | §7.11 |
| UC-55–59 | §7.12 |
| UC-60–64 | §7.13 |
| UC-65–69 | §7.14 |
| UC-70–74 | §7.15 |
| UC-75–79 | §7.16 |
| UC-80–84 | §7.17 |
| UC-85–89 | §7.18 |
| UC-90–94 | §7.19 |
| UC-95–99 | §7.20 |
| UC-100–104 | §7.21 |
| UC-105–109 | §7.22 |
| UC-110–114 | §7.23 |
| UC-115–119 | §7.24 |
| UC-120–124 | §7.25 |
| UC-125–129 | §7.26 |
| UC-130–134 | §7.27 |
| UC-135–139 | §7.28 |
| UC-140–145 | §7.29 |
| UC-146–151 | §7.30 |
| UC-152–158 | §7.31 |
| UC-159–165 | §7.32 |
| UC-166–173 | §7.33 |
| UC-174–182 | §7.34 |
| UC-183–192 | §7.35 |
| UC-193–202 | §7.36 |
| UC-203–211 | §7.37 |
| UC-212–220 | §7.38 |
| UC-221–228 | §7.39 |
| UC-229–235 | §7.40 |
| UC-236–243 | §7.41 |
| UC-244–252 | §7.42 |
| UC-253–261 | §7.43 |
| UC-262–269 | §7.44 |
| UC-270–281 | §7.45 |
| UC-282–293 | §7.46 |
| UC-294–306 | §7.47 |
| UC-307–319 | §7.48 |
| UC-320–332 | §7.49 |
| UC-333–344 | §7.50 |
| UC-345–356 | §7.51 |
| UC-357–367 | §7.52 |
| UC-368–379 | §7.53 |
| UC-380–391 | §7.54 |
| UC-392–403 | §7.55 |
| UC-404–415 | §7.56 |
| UC-416–427 | §7.57 |
| UC-428–439 | §7.58 |
| UC-440–451 | §7.59 |
| UC-452–463 | §7.60 |
| UC-464–475 | §7.61 |
| UC-476–487 | §7.62 |
| UC-488–499 | §7.63 |
| UC-500–511 | §7.64 |
| UC-512–523 | §7.65 |
| UC-524–535 | §7.66 |
| UC-536–547 | §7.67 |
| UC-548–559 | §7.68 |
| UC-560–571 | §7.69 |
| UC-572–583 | §7.70 |

