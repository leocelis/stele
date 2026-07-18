# Changelog

All notable changes to Stele are documented here.

## [0.1.6] — 2026-07-17

### Changed

Full cross-check of TECH_SPEC against PRD; PRD → v0.1.2, TECH_SPEC → v0.1.1.

- **Reconciled API signatures.** `search()` gained its resolved `consumer_scope`/`as_of` params in PRD (UC-3/UC-4, matching TECH_SPEC §6.1); `delete()` broadened in both docs to `subject_id | entry_id` — UC-5 now covers wrong-lesson single-entry erasure, not only subject erasure (intent OP-3/FF-9); `reflect()`'s report fields renamed to match TECH_SPEC's `conflicts[]`/`dangling_links[]`.
- **Reconciled the scope taxonomy.** PRD's UC-7 and FR table still described the intent's illustrative two-value enum (`universal_insight | project_scoped`) after TECH_SPEC had already resolved Q4 to three rungs (`universal` / `domain:<name>` / `project:<name>`). PRD now states the resolved taxonomy with a footnote explaining it refines the intent.
- **Closed the point-in-time flagging gap.** Neither doc previously guaranteed that entries served via `as_of` point-in-time queries carry an explicit historical marker — without it, PRD's "zero expired/superseded entries served unflagged" metric didn't hold outside the default retrieval path. Both docs now specify the `historical=true` flag.
- **Surfaced two silent risks as explicit non-decisions.** R4 ("never add LLM extraction to core, even for lazy producers") and the Phase-5 cost/latency measurement harness (required by PRD's "Cost" success metric) had no anchor in TECH_SPEC; both now have one (§2, §10).
- **Added the audit-trail and promote() traceability notes.** The journal now explicitly named as what makes PRD's "auditable" claim checkable; `promote()`'s convenience-wrapper-over-UPDATE relationship stated in both docs so the six-op/eight-tool count never reads as a contradiction.
- **UC-9 / P9 broadened** to name physical write-corruption risk under concurrency (TECH_SPEC §3.3's locking mechanism), not only the logical-conflict framing that was there before.

## [0.1.5] — 2026-07-17

### Added

- `docs/TECH_SPEC.md` — technical design derived from the intent and PRD.
  Resolves all six PRD open questions (file-based SoT + append-only journal;
  typed oracle-evidence records where self-assertions are unrepresentable;
  eight named MCP tools compiling to the six contract ops; three-rung scope
  taxonomy; surface-only conflict handling; migration producer). Specifies
  the monorepo package layout, byte-stable storage and content-derived ids,
  the governance state machine, the retrieval pipeline with staleness
  abstention and budgeting, the pack format with a blocking redaction
  pipeline, producer adapters, and the test strategy pinned to the intent's
  planned test paths.

## [0.1.4] — 2026-07-17

### Changed

- PRD → v0.1.1 after a full cross-check against the system intent: restored
  the two dropped non-goals (not-a-replacement-for-siblings; not generic
  document RAG), added the joint-satisfaction lifecycle test as the explicit
  completion gate and the injection-cost measurement condition to success
  metrics, surfaced the constraint priority ordering and the four
  context-operator coverage map in the requirements section, and added the
  wrong-lesson liability hedge to the pack-export use case.

## [0.1.3] — 2026-07-17

### Added

- `docs/PRD.md` — product requirements derived from the system intent:
  12 research-grounded pain points, 12 use cases (each generating a
  requirement), functional requirements by plane mapped to constraints
  C1–C7, when-not-to-use-Stele guidance, measurable success metrics, and
  the 6 open questions that block the tech spec.

## [0.1.2] — 2026-07-17

### Added

- OSS scaffolding parity with sibling projects: `CONTRIBUTING.md` (design-phase
  contribution model — research corrections, pattern challenges, intent review),
  `SECURITY.md` (private reporting; design-phase security commitments),
  `CODE_OF_CONDUCT.md` (Contributor Covenant v2.1), `.gitignore`.

### Changed

- Scope hygiene: product questions are now stated as plainly out of scope
  across the intent, roadmap, patterns, and research docs. This repository
  defines infrastructure.

## [0.1.1] — 2026-07-17

### Changed

- Full cross-check of the system intent against `docs/patterns/` closed the
  gaps it found: restored the true `DELETE` operation alongside `SUPERSEDE`
  (erasure vs. belief update — they are not the same op); C2 gained staleness
  abstention and budgeted injection; C3 gained audience tiers, adaptation
  operators, and the recipe-vs-equipment rule; C6 gained subject-id erasure
  indexing, source pointers, rejected-options content, and environment
  assumptions for workflow entries; added the four-operator coverage map
  (write/select/compress/isolate) and a full failure-mode coverage register
  with explicit mitigations or written acceptances; joint lifecycle test now
  exercises erasure cascade. README/ROADMAP aligned. Intent → v0.1.1.

## [0.1.0] — 2026-07-17

### Added

- Repository created (design phase — no implementation yet).
- `stele_system_intent.yaml`: system intent locking the architecture — five
  planes (contract / tool surface / governance / retrieval / export), seven
  constraints with planned test paths, satisfiability analysis, ecosystem
  boundaries (IVD producer, Cairn router, EIF oracle — protocol linkage only),
  known risks.
- `docs/research/AGENT_SESSION_LEDGER_INFERENCE_TIME_MEMORY_RESEARCH_2026.md`
  (v1.4): source-audited research on inference-time agent ledgers — relocated
  from the authors' private research corpus; host references genericized.
- `docs/research/AGENT_MEMORY_STORAGE_SYSTEMS_RESEARCH_2026.md` (v1.2):
  source-audited memory-storage landscape — relocated likewise.
- `docs/patterns/patterns_session_ledger_memory.yaml` (v1.2): distilled
  pattern file — 13 foundational findings, 12 operational patterns,
  contested findings, research-does-not-support register, quantitative
  reference.
- `README.md`, `ROADMAP.md`, MIT `LICENSE`.
