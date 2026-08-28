# Stele — Product Requirements Document

**Version:** 18.15.0 · **Date:** 2026-08-28 · **Status:** Active — **v18.15 shipped** (`stele-core` + `stele-mcp`)
**License:** MIT · Copyright (c) 2026 Stele contributors

**Derived from:** `stele_system_intent.yaml` v18.15.0 · `docs/patterns/patterns_session_ledger_memory.yaml` v1.3 · `docs/research/**` · shipped packages

> **Changelog vs 18.14.0:** UC-1968–1978 (SDT + MEFT, sdt_mef_shaped_report); frontiers §§406–407; MCP tools → 2003.









---

## 1. Overview

Stele is a governed experiential-memory ledger for AI agents. Agents log what worked and what failed on each task; a quarantine gate promotes only lessons backed by external evidence; and any agent retrieves the distilled, still-valid experience through one protocol before its next task.

Stele is **not** a database product, **not** an LLM extraction pipeline, and **not** a retrieval router. It is the store + contract + governance layer for one kind of knowledge — *experiential memory* (what happened during tasks: successes, failures, decisions, dead ends; Hu et al., arXiv:2512.13564) — with **zero LLM calls and zero network on the core write path** (intent C5).

**Product shape (v1.0):** a pure-Python library (`stele-core`, zero runtime deps) plus an MCP stdio server (`stele-mcp`) and a `stele` CLI. File-backed inspectable SoT + append-only journal; hybrid lexical (+ optional caller embedder) retrieval; redacted pack export/hydrate; living-ledger reinforce/pin/stale/reverify; ops dashboard (stats, timeline, attach, verify_pack, doctor, snapshot); published entry JSON Schema; memorywire-shaped projection helpers (no memorywire dependency).

Commercial packaging of experience packs (pricing, SKUs, hosted sync) lives outside this repository. This PRD specifies the **protocol product** — what any consumer must be able to do through Stele.

---

## 2. Who this is for

Anyone running agents that repeat classes of tasks and keep re-learning the same lessons:

- **Operators of multiple agents** across projects, who watch one agent make a mistake another agent solved last week.
- **Agent developers** whose per-project feedback files, handoffs, and postmortems hold real knowledge that no agent ever retrieves at the right moment.
- **Framework authors** who need a governed place to ship codified corrections (e.g., an intent-correction layer) so future intent is written by an agent that has lived through prior mistakes.
- **Privacy-conscious teams** who need memory that can prove erasure and never leaks a session's secrets into a shared store.
- **Reviewer / coordinator roles** who need a *bounded* recent-correction slice and contested queue — not a dump of raw receipt histories (C8 retrieval roles).
- **Pack recipients** (another team or agent fleet) who import a *redacted* foreign pack and must prove it helps on *their* tasks before trusting it (OP-12 scoped eval — not a WTP claim).

The common thread: agent sessions already produce the most valuable, most specific knowledge a system has — and today it is thrown away or scattered (FF-1; AGENT_SESSION_LEDGER research, Executive summary).

---

## 3. The problem

The mechanism is proven: a frozen model + agent tools + an external, tool-updated ledger measurably improves outcomes — Reflexion, ExpeL, AWM, CER, Hindsight, across benchmarks, with no weight updates (FF-1). But every naive implementation of "just remember things" fails in a documented way:

- **Dump the transcript** → context rot and negative transfer (FF-2, FF-4).
- **Auto-extract facts on write** → hallucinated memories, silent overwrites, poisoned stores (OP-4, FF-12).
- **Let the agent grade itself** → confirmation bias ratified into long-term memory (OP-2).
- **Append forever** → stale lessons actively mislead later tasks (FF-8).
- **Validate with recall Q&A** → false confidence; recall wins do not transfer to agentic action (FF-5).
- **Share the live store** → secrets + env-specific equipment leak; foreign consumers replay commands that break (FF-9, FF-13, OP-6).
- **Silent merge of contradictions** → multi-agent conflict becomes invisible poison (OP-10; R2).

Governance — not storage — is the hard part (FF-12). Storage is solved in five substrate families with no single winner (FF-11); what no off-the-shelf layer provides is the *governed lifecycle*: distilled entries in, oracle-verified promotion, temporal validity, visible multi-writer provenance, subject-indexed erasure, and evaluation on task outcomes.

---

## 4. Pain points (grounded in research)

| # | Pain | Evidence |
|---|---|---|
| P1 | Hard-won task experience is **thrown away** or scattered across files no agent retrieves | FF-1; FF-6 (capture history); ledger research Part 1 |
| P2 | **Raw trajectories poison reuse** — brittle command anchoring, false validation confidence | FF-4 (MTL, arXiv:2604.14004); FF-2 |
| P3 | **Self-graded "it worked" is not evidence** — reflections ratify the code that produced them | OP-2; MAR (arXiv:2512.20845) |
| P4 | **Extract-on-write poisons stores** — LLM call per add, hallucinated facts, silent overwrite | OP-4; storage research Part 2 |
| P5 | **Lessons expire** — "X worked" is a belief with a validity window; append-only stores serve poison after env changes | FF-8; LongMemEval (arXiv:2410.10813) |
| P6 | **Recall benchmarks lie about agentic value** — LoCoMo-saturated systems perform poorly when memory must drive actions | FF-5; MemoryArena (arXiv:2602.16313) |
| P7 | **Cross-project reuse backfires** below Insight level — only abstracted lessons transfer | FF-3 (MTL format ladder); Trace2Skill |
| P8 | **Erasure is impossible** without subject indexing across store + every derived index | FF-9; FF-12; OP-12 (open problems) |
| P9 | **Concurrent agent writers conflict silently** — merge semantics are an open research frontier, and simultaneous writes risk corrupting the store if concurrency isn't handled | OP-10 (Hu et al. survey) |
| P10 | **Wrong memory hurts** — retrieval noise and unbudgeted injection degrade the very tasks memory should help | OP-10; SRACG; BEAM; OP-9 (Compress) |
| P11 | **Rationale alone doesn't answer reusers** — <50% of reuser questions answered without links to artifacts/tests | FF-6 (Karsenty, CHI 1996) |
| P12 | **Capture systems die without short-term payoff** — the documented death of gIBIS/QuestMap | FF-6; OP-10 |
| P13 | **Model swap invalidates judgment weight** — a lesson graded under model A may mislead under model B if never re-verified | TECH_SPEC §4.1 `provenance.model_id`; C8 optional provenance |
| P14 | **Operators cannot see ledger health** — no counts, no journal trail, no pack integrity check → abandon or over-trust | OP-11 cost/ops; C4 inspectability |
| P15 | **Private receipt / judgment stores cannot be bulk-copied** into a public protocol without leaking paths and authority vocabulary | C8; intent `feedback_receipt_interoperability` |
| P16 | **Every memory framework invents its own SDK** — agents cannot carry lessons across runtimes without rewrite | OP-6; memorywire (arXiv:2606.01138); frontiers research |
| P17 | **Operators lack a one-command health check** — verify, stale, contested, and counts live in separate APIs | P14; Governed Memory silent-degradation thesis (arXiv:2603.17787) |
| P18 | **Zombie memories** — unused / net-harmful / stale-promoted lessons still pollute Select | MemArchitect (arXiv:2603.18330) |
| P19 | **Entangled poison** — trusted entries that LINK to purged seeds stay invisible after provenance purge | PurgeBench / memorywire; SSGM read-filter thesis |
| P20 | **Shared multi-principal memory** — unauthorized principals recover others' lessons; deleted facts resurface | GateMem (arXiv:2606.18829) |
| P21 | **Audit erasure / belief drift** — supersede silently drops losers; point-in-time belief is unrecoverable | TOKI (arXiv:2606.06240) |
| P22 | **Collapsed conflicts** — latest-write hides contradictions → false-confident agent actions | StateFuse (arXiv:2607.05844) |
| P23 | **Memory injection / link poison** — one poisoned write is retrieved, promoted, and reused across agents | MIND; MAPLE-Guard |
| P24 | **Snapshot tampering / lost external logs** — operators cannot prove what the ledger contained | MemMark; TRACE |

---

## 5. Use cases

> **Stele's planes:** **K** Contract (schema) · **T** Tool surface (six ops + governed helpers) · **G** Governance (quarantine → promote → REFLECT) · **R** Retrieval · **X** Export/hydrate · **L** Living ledger (outcomes, pin, stale, reverify) · **O** Ops (stats, timeline, attach, verify). (intent §architecture + v1 extensions)

### UC-1 — Auto-log a task outcome without poisoning the store
- **Scenario:** An agent finishes a task and logs "pinning the cache key to a calendar bucket fixed the stale reads."
- **Pain today (P3, P4):** Either the lesson lands unverified in long-term memory (poison) or it lands nowhere (P1).
- **Stele solution:** **T** `ADD` accepts only structured, distilled entries (C5, C6) into **G** quarantine — durable immediately, retrievable never, until promoted (C7). A distill gate rejects transcript/tool-dump shaped bodies (FF-2). Capture cost is the agent's, not the human's (mitigates P12; FF-6).
- **Requirement:** `add(entry) → {id, state: quarantined}`; schema-incomplete or non-distilled entries rejected at the boundary.

### UC-2 — Promote only lessons that survived an external oracle
- **Scenario:** The same lesson later carries a passing regression test and a production log line as evidence.
- **Pain today (P3):** No memory layer distinguishes "agent believes it" from "evidence shows it."
- **Stele solution:** **G** promotion requires oracle evidence attached to the entry — test result, env feedback, independent judge, or human sign-off (C7; OP-2, OP-4). A self-grade can never promote; the writing agent cannot act as the promote actor (C8 writer role).
- **Requirement:** `promote(id, evidence, actor) → promoted | rejected{reason}`; code-fix lessons require `test_result` + exit 0; evidence contract pluggable (an external oracle is one producer of evidence, not imported into core).

### UC-3 — Retrieve relevant experience before a task
- **Scenario:** An agent about to touch a caching layer asks: "what do we know about cache-key mistakes?"
- **Pain today (P6, P10):** Whole-ledger dumps rot context; irrelevant memories actively hurt.
- **Stele solution:** **R** hybrid search (keyword + optional semantic + temporal) over promoted entries only, filtered by scope and validity, injected as a budgeted slice (C2; OP-9 Compress). Returning nothing is a first-class answer; possibly-stale entries carry an explicit flag or can be withheld (FF-8, abstention). Empty query → ∅.
- **Requirement:** `search(query, consumer_scope, budget, as_of?, stale_policy?) → slices[] | ∅`, each slice carrying validity, staleness, provenance, links, and (when `as_of` is set) an explicit historical-state flag.

### UC-4 — Supersede a stale lesson without losing history
- **Scenario:** The library upgraded; the old lesson is now wrong for v2 but was true for v1.
- **Pain today (P5):** Overwrite loses the history; append-only serves the poison.
- **Stele solution:** **K** bi-temporal metadata (`valid_from`, `superseded_by`, `superseded_at`, `last_verified`, `expiry`) with **T** `SUPERSEDE` — invalidate, not overwrite (C6; Zep/Graphiti semantics, arXiv:2501.13956 §2).
- **Requirement:** `supersede(old_id, new_entry)`; point-in-time reads (`search(..., as_of=t)`) answer "what did we believe when?" and return the historical entry explicitly flagged as such — never presented as current.

### UC-5 — Erase on demand, provably
- **Scenario:** Two distinct triggers, same mechanism: (a) a subject (person, client, project) must be removed from the ledger — including from every index; (b) a single entry turns out to be a wrong lesson and must be truly gone, not just superseded.
- **Pain today (P8):** Embeddings and derived indexes silently retain what the store deleted; SUPERSEDE alone cannot satisfy either trigger — it invalidates, it does not erase.
- **Stele solution:** **T** `DELETE` (true erase, distinct from SUPERSEDE) keyed on either the mandatory subject/owner id or a specific entry id (C6; OP-3, FF-9); every index is derived and rebuildable, so erasure propagates by rebuild (C4).
- **Requirement:** `delete(subject_id | entry_id)` cascades; a post-delete index rebuild contains zero traces (joint test asserts this).

### UC-6 — Consolidate a growing ledger
- **Scenario:** After months of auto-logging, the ledger holds duplicates, near-duplicates, and expired entries.
- **Pain today (P5, P12):** Unmaintained memory decays into noise; per-entry human review kills adoption.
- **Stele solution:** **G** batched `REFLECT` pass — dedupe, merge, supersede, expire, surface conflicts — provenance-preserving (C7; OP-3; Memory-R1). Agreeing near-duplicates merge with provenance links; contradictory near-duplicates become **contested** (never auto-resolved).
- **Requirement:** `reflect() → ReflectReport{merged[], expired[], conflicts[], dangling_links[]}`; runs batched, never blocks writes.

### UC-7 — Reuse across projects without negative transfer
- **Scenario:** A lesson learned in project A is relevant to project B — but A's exact commands would break B.
- **Pain today (P7, P2):** Trajectory-level reuse anchors the consumer to the wrong context.
- **Stele solution:** **K** mandatory abstraction scope — three rungs, `universal` · `domain:<name>` · `project:<name>` — filtered at retrieval (C2, C6); workflow/skill entries declare environment assumptions so consumers can env-check before replaying (FF-4 gate).
- **Requirement:** Scope is a schema field, not a convention; cross-scope reads require an explicit `scope_override`, never the default; `consumer_domain` unlocks matching `domain:<name>` entries.

### UC-8 — Answer the reuser's real questions
- **Scenario:** A consumer asks *why* an approach was rejected and what test proves the chosen one.
- **Pain today (P11):** Rationale documents alone answered <50% of reuser questions (Karsenty).
- **Stele solution:** **K/T** entries record rejected options (IBIS lineage, FF-7) and `LINK` to artifacts, tests, entries, and source sessions (C6; FF-2 gist→source pointer). Retrieval can follow `kind=entry` links within budget (multi-hop depth 1–3).
- **Requirement:** `link(entry_id, kind, ref)`; `search(..., follow_links=True, follow_link_depth=n)`; `related(entry_id)` returns inbound/outbound neighborhood.

### UC-9 — Ingest from heterogeneous producers
- **Scenario:** an intent-correction layer, per-project feedback files, and session handoffs all want to feed the ledger — possibly at the same time.
- **Pain today (P9, P15):** Merging codebases or granting store internals to producers couples everything; bulk-copying private receipt trees leaks paths.
- **Stele solution:** **K** every producer writes through the same six-op protocol; core imports none of their code (C1; memorywire lesson, OP-6). Writes are serialized (single-writer lock + atomic rename). Logical conflicts surface at REFLECT, never silently (C6; mitigates P9).
- **Requirement:** Protocol is the only write path; static import scan enforces core purity; concurrent writes never corrupt an entry.

### UC-10 — Sit behind a retrieval router
- **Scenario:** A host already uses a retrieval router to decide *whether* and *how* to retrieve.
- **Pain today:** Memory layers that bundle their own routing fight the router.
- **Stele solution:** Stele stores and serves; any retrieval router fronts it as one more backend via `SearchBackend` protocol (C1; intent §ecosystem_linkage). Complementary by construction: the router owns routing, Stele owns the store.
- **Requirement:** `search()` is callable as a pure backend signal — no side effects, deterministic given store state + caller filters.

### UC-11 — Export a pack for a different audience
- **Scenario:** A team wants the distilled "build a database" experience — without the originating team's secrets or env specifics.
- **Pain today (P2; FF-9):** Sharing a live store or raw trajectories leaks secrets trajectory-level and transfers badly.
- **Stele solution:** **X** pack export: Insight/skill/workflow layers + issue trail + provenance, redacted at export, version- and expiry-stamped, audience-tiered with adaptation operators; recipe layer, never equipment layer (C3; FF-10, FF-7, FF-13). Storage ≠ pack. Subject allowlist optional. Packs carry `may_be_outdated`.
- **Requirement:** `export(scope, audience, purpose, expiry) → pack`; property tests: no secrets, no top-level trajectories, stamps present; `verify_pack(dir)` offline.

### UC-12 — Prove the ledger helps, honestly
- **Scenario:** Does retrieval-before-task actually improve outcomes, or does it just feel good?
- **Pain today (P6):** Recall Q&A over the store proves nothing about action.
- **Stele solution:** Task-outcome harness: agents on lesson-dependent tasks with vs. without Stele (intent §success_oracle; FF-5; OP-12). Includes workflow env-gate family and scoped foreign-pack transfer lift. Value claims wait for these numbers; WTP/pricing stay out of scope.
- **Requirement:** `LessonTask` / `compare_with_without` / `memory_arena_smoke` / `foreign_pack_transfer_eval` / `measure_search_overhead` in-repo; a recall benchmark is explicitly not acceptance evidence.

---

### UC-13 — Resolve contested contradictions with evidence *(new)*
- **Scenario:** REFLECT finds two near-duplicate lessons with contradictory oracle verdicts.
- **Pain today (P9):** Auto-merge picks a winner silently and poisons the store.
- **Stele solution:** **G** mark both `contested` with `contested_with` peers; `list_contested` surfaces the queue; `resolve_contested(winner, loser, evidence, actor)` evidenced-supersedes — authors cannot self-resolve (TECH_SPEC Q5 / R2).
- **Requirement:** No auto-resolve path; resolution always journals evidence.

### UC-14 — Env-check before replaying a workflow *(new)*
- **Scenario:** Agent retrieves a "rotate cache keys" workflow that assumes `linux` + `redis>=7`, but is running on Windows.
- **Pain today (P2, P7):** Replay of env-specific steps is the negative-transfer anchor (FF-4).
- **Stele solution:** **R** slices carry `env_assumptions`, `env_mismatch`, `missing_env_assumptions` when `consumer_env` is provided; harness tasks with `require_env_ok` fail on mismatch (abstention counts as success of the gate).
- **Requirement:** `search(..., consumer_env=[...])`; workflow/skill ADD requires non-empty `env_assumptions`.

### UC-15 — Choose how to handle staleness *(new)*
- **Scenario:** Operator wants possibly-stale lessons either flagged for human judgment or withheld entirely.
- **Pain today (P5):** Systems either hide staleness or serve poison as current truth.
- **Stele solution:** **R** `stale_policy="flag"|"withhold"` (FF-8 abstention); `stale_report()` lists promoted entries past the horizon for batch review.
- **Requirement:** Default `flag`; withhold returns ∅ for those slices.

### UC-16 — Re-verify after a model swap *(new)*
- **Scenario:** Fleet upgrades from model A to model B; lessons carrying `provenance.model_id=A` should not be trusted blindly.
- **Pain today (P13):** No signal; agents keep using A-era judgment under B.
- **Stele solution:** **R** `consumer_model_id` + `model_policy=flag|withhold` sets `model_mismatch`; **L** `reverify(ids, evidence)` batch-refreshes `last_verified` with new oracle evidence.
- **Requirement:** Optional `provenance.model_id` on ADD; mismatch never auto-deletes — flag or withhold only.

### UC-17 — Import a foreign pack and measure lift *(new)*
- **Scenario:** Team B receives Team A's redacted pack and wants to know if it helps *their* agents on *their* tasks.
- **Pain today (P2, OP-12):** Sharing a live store, or claiming value without an action eval.
- **Stele solution:** **X** `hydrate(pack)` ADDs as `pack-hydrate` writer (cannot self-promote); optional promote with caller evidence; `foreign_pack_transfer_eval` measures with/without lift (scoped — not WTP).
- **Requirement:** Hydrate never copies private source trees; transfer eval reports rates, not price.

### UC-18 — Reinforce lessons that actually helped *(new)*
- **Scenario:** After using a retrieved lesson, the agent (or human) confirms it helped — or marks it harmful.
- **Pain today (P5, P12):** No short-term feedback loop; ledgers go stale or get abandoned.
- **Stele solution:** **L** `record_outcome(helpful|harmful|ignored)` — helpful bumps `last_verified` and usage counters; SEARCH can prefer high-helpful / pinned entries (Generative Agents–style reinforce, FF-8 freshness).
- **Requirement:** Outcomes do not auto-contest; harmful increments counters for reviewer attention.

### UC-19 — Pin a critical lesson to the top of retrieval *(new)*
- **Scenario:** Ops knows one safety lesson must surface whenever the topic is touched.
- **Pain today (P10):** Pure BM25 may bury the critical lesson under noisy peers.
- **Stele solution:** **L** `pin(entry_id)` sets `usage.pinned`; SEARCH ranks pinned ahead of peers when `prefer_helpful=True`.
- **Requirement:** Only promoted entries pin; unpin supported.

### UC-20 — Explain and compress what was retrieved *(new)*
- **Scenario:** Agent (or debugger) needs to know *why* a slice was returned, without dumping a 4k body into a tight context budget.
- **Pain today (P10, OP-9):** Opaque retrieval + Select without Compress recreates context rot.
- **Stele solution:** **R** each slice carries `match_reasons` (terms, scope, via_link, stale, model/env flags, helpful/pinned); `body_max_chars` truncates with `body_truncated=true`.
- **Requirement:** Compression is slice-local — SoT body unchanged.

### UC-21 — Batch freshness ops for operators *(new)*
- **Scenario:** Weekly hygiene: find everything past the staleness horizon and re-verify what still holds.
- **Pain today (P5, P14):** Manual grep of files; no operator API.
- **Stele solution:** **L/O** `stale_report()` + `reverify(entry_ids, evidence)` + `verify()` store integrity (dual-location, schema, journal parse).
- **Requirement:** Reverify appends evidence and refreshes `last_verified`; verify is read-only.

### UC-22 — Walk the lesson graph *(new)*
- **Scenario:** A failure lesson LINKs to a goal, which LINKs to a decision — agent needs the chain, not one node.
- **Pain today (P11):** Flat retrieval loses structure Karsenty showed reusers need.
- **Stele solution:** **R/T** `follow_links` + `follow_link_depth` (1–3); `related(id)` inbound/outbound; REFLECT reports dangling entry LINKs.
- **Requirement:** Expansion stays inside token budget; hops marked `via_link` / `linked_from`.

### UC-23 — Reviewer gets a bounded correction slice *(new)*
- **Scenario:** A coordinator role reviews open risks and recent promotions — not the whole ledger.
- **Pain today (P10, P15):** Dumping receipt histories or full stores overwhelms and leaks.
- **Stele solution:** **O** `reviewer_corrections(limit)` — contested first, then newest promoted; never raw receipts (C8).
- **Requirement:** Bounded by `limit`; contested included by default.

### UC-24 — Ops dashboard, timeline, and artifacts *(new)*
- **Scenario:** Operator asks: how big is the store, what happened to entry X, can I attach the proving patch?
- **Pain today (P14):** Opaque file trees; no content-addressed artifacts.
- **Stele solution:** **O** `stats()` (counts by state/layer/scope, stale, contested, attachments); `timeline(entry_id)` from the journal; `attach(bytes)` content-addressed digest + optional LINK (FF-6).
- **Requirement:** Attachments keyed by sha256; journal remains append-only SoT of ops.

### UC-25 — Project a private operator receipt safely *(new)*
- **Scenario:** An operator's private receipt inventory holds a code-regression lesson worth promoting into Stele.
- **Pain today (P15):** Copying a private receipt inventory into a public protocol leaks operator paths and collapses detection/diagnosis into one blob.
- **Stele solution:** **T** `project_receipt(redacted_dict)` → ADD payload preserving expected/detection/diagnosis/change/outcome/trace; private-source fields rejected; code-fix still needs `test_result` to promote (C8).
- **Requirement:** Adapter never reads a foreign filesystem; one selected receipt at a time.

### UC-26 — Ingest a codified judgment without importing foreign frameworks *(new)*
- **Scenario:** An external tool codifies an intent correction; Stele should store it as a decision/failure_lesson.
- **Pain today (P9):** Code-merge couples frameworks; violates C1.
- **Stele solution:** **T** `judgment_entry(wire_dict)` maps title/body/rejected_options → quarantined ADD; `provenance.agent` defaults to judgment-adapter; the external producer stays outside Stele (intent §ecosystem_linkage).
- **Requirement:** Wire shape only — zero `import foreign frameworks` in core.

### UC-27 — MCP agent surface for the full lifecycle *(new)*
- **Scenario:** A coding agent in Cursor (or any MCP host) should ADD, promote, search, reflect, export, and reinforce without custom glue.
- **Pain today (P1, P12):** Lessons stay in chat and evaporate.
- **Stele solution:** **T** stdio MCP tools covering core ops + contested + living ledger + ops dashboard (TECH_SPEC §7 expanded).
- **Requirement:** One server per store (`STELE_STORE`); tools are thin JSON façades over `Stele`.

### UC-28 — Operator CLI without writing Python *(v1)*
- **Scenario:** An operator initializes a store, runs doctor, snapshots before a migrate, and searches from the shell.
- **Pain today (P14, P17):** Library-only access blocks ops adoption (FF-6 capture death without short-term payoff).
- **Stele solution:** **O** `stele` CLI: `init · schema · verify · doctor · stats · snapshot · search · attach`.
- **Requirement:** Same semantics as library; `--now` required for writes (C5 determinism).

### UC-29 — Publish a machine-readable entry contract *(v1)*
- **Scenario:** A foreign tool or memorywire router validates Stele entries before ingest.
- **Pain today (P16):** Ad-hoc JSON shapes break interop (memorywire thesis).
- **Stele solution:** **K** JSON Schema 2020-12 via `entry_json_schema()` / `stele schema` / `docs/schemas/entry.schema.json` / MCP `stele_entry_schema`.
- **Requirement:** Schema tracks `SCHEMA_VERSION`; additionalProperties false on core object.

### UC-30 — Snapshot the SoT for backup / handoff *(v1)*
- **Scenario:** Before REFLECT or a machine move, copy the ledger cold.
- **Pain today (P14):** Manual `cp -r` misses what is SoT vs derived index.
- **Stele solution:** **O/X** `snapshot(dest)` copies manifest + journal + entries + attachments; indexes excluded (rebuild).
- **Requirement:** Dest empty/new; journal records SNAPSHOT; restore = replace store root + rebuild indexes.

### UC-31 — Project to / from memorywire-shaped wire *(v1)*
- **Scenario:** A fleet already speaks memorywire `remember`/`recall`; Stele must not become another silo.
- **Pain today (P16):** Forced rewrite of every integration.
- **Stele solution:** **T** `to_memorywire_remember(entry)` / `from_memorywire_recall_hits(hits)` — projection only, zero memorywire dependency (C1).
- **Requirement:** Metadata carries `stele_id` when known; foreign hits marked `foreign: true`.

### UC-32 — One-shot operator doctor *(v1)*
- **Scenario:** Weekly hygiene: is the store intact, contested, or stale?
- **Pain today (P17):** Four API calls and interpretation.
- **Stele solution:** **O** `doctor()` / `stele doctor` / MCP `stele_doctor` → verify + stats + contested ids + stale ids + warnings.
- **Requirement:** `ok` false iff integrity failed; warnings list open contested/stale.

### UC-33 — Recover a poisoned store by provenance *(v1.1)*
- **Scenario:** An agent (or tool) wrote lessons from an untrusted source; the store must be cleaned without wiping everything.
- **Pain today:** Content detectors miss semantic poison; wipe destroys utility (PurgeBench / memorywire arXiv:2606.01138).
- **Stele solution:** **G/O** `purge_by_provenance(untrusted_sources|agents, dry_run=True|False)` — list or hard-delete matching entries; journal `PURGE`. Entangled poison in trusted sources is **not** auto-deleted.
- **Requirement:** Default dry-run; execute requires explicit flag/actor; trusted entries untouched.

### UC-34 — Batch-write quarantined lessons *(v1.1)*
- **Scenario:** A session ends with N distilled lessons; write cost must stay low (MemBench write-time concern).
- **Pain today:** N separate locks / partial failure mid-import.
- **Stele solution:** **T** `add_batch(entries)` — schema/distill/private checks first, then one lock for all ADD; all-or-nothing.
- **Requirement:** On any invalid entry, zero writes.

### UC-35 — Diff live store vs snapshot *(v1.1)*
- **Scenario:** After a week of work, compare live SoT to last backup.
- **Pain today:** Manual file tree diffs; indexes confuse operators.
- **Stele solution:** **O** `diff_stores(other_root)` → only_here / only_there / both by entry id.
- **Requirement:** Works against snapshot dest from UC-30; ignores derived indexes.

### UC-36 — Select only trusted provenance *(v1.1)*
- **Scenario:** At retrieval time, ignore lessons whose source is not in the allowlist.
- **Pain today:** Poisoned promoted entries can still be injected if not purged yet.
- **Stele solution:** **R** `search(..., trusted_sources=[...])` filters slices by `provenance.source` equality or prefix.
- **Requirement:** Empty allowlist = no extra filter (default).

### UC-37 — MemBench-shaped local eval report *(v1.1)*
- **Scenario:** CI wants capacity + latency + effectiveness proxies without claiming a leaderboard.
- **Pain today:** Only recall-style tests or full external gyms.
- **Stele solution:** **Harness** `membench_shaped_report(stele)` → capacity counts, search median ms, with/without lift. Explicitly **not** MemBench gym scores.
- **Requirement:** Deterministic; zero network/LLM.

### UC-38 — Surface LINK-entangled poison for human review *(v1.2)*
- **Scenario:** After (or before) a provenance purge, trusted entries that LINK to untrusted seeds may still inject poison by hop.
- **Pain today (P19):** Purge removes the seed; neighborhood stays silent (PurgeBench entangled case).
- **Stele solution:** **G/O** `entangled_suspects(seed_ids|untrusted_*)` — report-only queue; never auto-delete.
- **Requirement:** Suspects exclude the seeds themselves and untrusted-matching entries; CLI/MCP parity.

### UC-39 — Hygiene candidates for zombie / net-harm lessons *(v1.2)*
- **Scenario:** Weekly ops: which promoted lessons are unused-stale, net-harmful, or past the staleness horizon?
- **Pain today (P18):** MemArchitect “zombie memory” gap — no triage list without scraping usage fields by hand.
- **Stele solution:** **O** `hygiene_candidates(unused_before?)` — reasons `net_harmful` / `unused_stale` / `stale_promoted`; report only.
- **Requirement:** No auto-prune; operator chooses purge / supersede / pin.

### UC-40 — Governance-shaped local eval + prefer_fresh Select *(v1.2)*
- **Scenario:** CI wants Layer-4 governance proxies (integrity, contested, purge dry-run, hygiene, entangled) and Select soft-ranks fresher lessons.
- **Pain today:** Recall-only CI; no decay-aware Select without mutating SoT.
- **Stele solution:** **Harness** `governance_shaped_report` + **R** `search(..., prefer_fresh=True)` (SSGM read-filter proxy).
- **Requirement:** Proxies are not MemArchitect/MGB scores; prefer_fresh never writes the store.

### UC-41 — Principal-scoped Select (access control) *(v1.3)*
- **Scenario:** Multiple principals share one store; a requester may only see an allowlisted set of scopes.
- **Pain today (P20):** Default scope rules still admit `universal` / cross-scope leaks under naive shared-pool use (GateMem ACL failures).
- **Stele solution:** **R** `search(..., principal_scopes=[...])` — when set, **only** those scopes; no implicit universal.
- **Requirement:** MCP/library honor the same filter; empty list → zero hits.

### UC-42 — Prove active forgetting after erasure *(v1.3)*
- **Scenario:** After subject/entry DELETE, operators must prove Search cannot resurrect the content.
- **Pain today (P20):** GateMem shows external-memory systems often recover deleted facts.
- **Stele solution:** **O/G** `forget_compliance(subject_id|entry_ids, probe_query, forbidden_substrings)` — store clear + SEARCH leak check.
- **Requirement:** Journal DELETE rows may remain (audit); entry SoT must be empty; `ok` false on any leak.

### UC-43 — GateMem-shaped local eval (utility ∩ ACL ∩ forgetting) *(v1.3)*
- **Scenario:** CI wants the three GateMem axes without claiming the gym leaderboard.
- **Pain today:** Separate harnesses; no joint three-axis proxy.
- **Stele solution:** **Harness** `gatemem_shaped_report(stele)` — utility lift + principal_scopes ACL probe + ephemeral forget probe.
- **Requirement:** Deterministic; explicitly not GateMem MGS scores.

### UC-44 — Reconstruct supersede audit lineage *(v1.4)*
- **Scenario:** After supersede/resolve, an auditor asks what replaced what and who wrote it.
- **Pain today (P21):** Systems that erase losers admit TOKI audit-erasure anomaly.
- **Stele solution:** **O** `lineage(entry_id)` — predecessors, successors (`superseded_by`), journal ops.
- **Requirement:** Loser entry remains on disk until explicit DELETE; lineage never invents missing nodes.

### UC-45 — Point-in-time belief read *(v1.4)*
- **Scenario:** “What did we believe last Tuesday?” after a supersede.
- **Pain today (P21):** Live SEARCH hides superseded; operators cannot reconstruct.
- **Stele solution:** **R** `belief_at(as_of, consumer_scope, query?)` — SEARCH or inventory of beliefs valid at `as_of`.
- **Requirement:** Later-superseded beliefs appear when still valid at `as_of`; flagged historical.

### UC-46 — Conflict-preserving contested surface *(v1.4)*
- **Scenario:** Two promoted lessons contradict; the agent must see both sides before acting.
- **Pain today (P22):** Collapsed latest-write → false certainty (StateFuse).
- **Stele solution:** **G/O** `conflict_surface()` — unique contested pairs with body previews; `preserved: true`.
- **Requirement:** No auto-merge; resolve only via evidenced `resolve_contested`.

### UC-47 — MemoryAgentBench-shaped four-competency report *(v1.4)*
- **Scenario:** CI wants retrieval / learning / long-range / selective-forgetting proxies.
- **Pain today:** Single-axis harnesses.
- **Stele solution:** **Harness** `memoryagent_shaped_report` (+ lineage audit check).
- **Requirement:** Not MemoryAgentBench leaderboard claims.

### UC-48 — Scan store for injection-marker suspects *(v1.5)*
- **Scenario:** Before promote or pack share, flag lessons that look like instruction overrides.
- **Pain today (P23):** Poisoned bodies look like tips until retrieved (MIND / MAPLE).
- **Stele solution:** **G/O** `injection_scan` — deterministic marker catalog; report only; zero LLM.
- **Requirement:** Explicitly not a neural detector; catalog listed in response.

### UC-49 — Retrieve / promote gates for injection suspects *(v1.5)*
- **Scenario:** Shared fleets must not inject or promote marker-matched poison.
- **Pain today (P23):** Prompt-level guards miss memory-link poison (MAPLE-Guard).
- **Stele solution:** **R** `search(..., withhold_injection_suspects=True)` · **G** `promote(..., block_injection_suspects=True)`.
- **Requirement:** Defaults off (compat); maple harness exercises both on.

### UC-50 — Compress plan + MAPLE-shaped lifecycle report *(v1.5)*
- **Scenario:** CI wants write/retrieve/promote/reuse gate proxies plus budget overflow visibility.
- **Pain today:** No joint lifecycle-gate report; budget truncations are opaque.
- **Stele solution:** **Harness** `maple_shaped_report` + **R** `select_budget_plan(query, budget)`.
- **Requirement:** Not MAPLE ASR / MIND accuracy claims.

### UC-51 — Tamper-evident store seal *(v1.6)*
- **Scenario:** Before handoff or after restore, prove the SoT bytes match a prior attestation.
- **Pain today (P24):** File copies can be silently edited; no content root (MemMark R3 gap).
- **Stele solution:** **O** `store_seal()` / `verify_seal(seal)` — SHA-256 over sorted entry content digests + journal digest.
- **Requirement:** Deterministic; excludes volatile `usage` counters from digests; not a TRACE watermark.

### UC-52 — Attribution receipt per entry *(v1.6)*
- **Scenario:** Auditor asks for reproducible evidence for one lesson without the full store.
- **Pain today (P24):** Timeline alone lacks a content-binding digest.
- **Stele solution:** **O** `attribution_receipt(entry_id)` — content digest + journal ops + links.
- **Requirement:** Works when entry still present; journal-only tombstones raise if neither exist.

### UC-53 — Journal↔SoT replay consistency *(v1.6)*
- **Scenario:** Soft check that ADD rows resolve to live entries or DELETE/PURGE.
- **Pain today:** Silent journal/SoT drift after manual edits.
- **Stele solution:** **O** `replay_consistency()`; PURGE journal retains `removed` id list.
- **Requirement:** Report-only; `ok` false lists `missing_after_add`.

### UC-54 — MemMark-shaped seal/receipt harness *(v1.6)*
- **Scenario:** CI wants seal roundtrip + tamper detect + receipt + replay proxies.
- **Stele solution:** **Harness** `memmark_shaped_report`.
- **Requirement:** Not MemMark/TRACE watermark claims.

### UC-55 — Lifecycle eligibility tiers *(v1.7)*
- **Scenario:** A long-running store has thousands of promoted lessons; retrieval must prefer high-utility items without deleting the rest.
- **Pain today (P10):** Flat SEARCH treats every promoted lesson as equally eligible.
- **Stele solution:** **R/O** HOT/WARM/COLD via `lifecycle_tier` / `lifecycle_inventory`; `search(..., lifecycle_tiers=)`.
- **Requirement:** Deterministic metadata filters only (C5); SoT unchanged.

### UC-56 — Keyed revoke without erasure *(v1.7)*
- **Scenario:** A preference/fact key flipped; stale active precedents must leave ordinary retrieval but stay auditable.
- **Pain today:** Append-only pollutes; LWW erases history.
- **Stele solution:** **L** optional `conflict_key`; evidenced `revoke_by_key` → `revoked`; `unrevoke` re-activates.
- **Requirement:** No auto-revoke on semantic clash; evidence required.

### UC-57 — Seal an exported pack *(v1.7)*
- **Scenario:** Receiver wants tamper-evidence on a redacted pack without the source journal.
- **Stele solution:** **O** `pack_seal` / `verify_pack_seal`.
- **Requirement:** Complements `verify_pack`; not a keyed watermark.

### UC-58 — Explain retrieval ranking *(v1.7)*
- **Scenario:** Debugger asks why lesson X beat Y.
- **Stele solution:** **R** `search_explain` adds lexical/RRF `rank_detail` + lifecycle tier.
- **Requirement:** Read-only explain; no ranking model training in core.

### UC-59 — TEPA+AMV-L shaped local harness *(v1.7)*
- **Scenario:** CI gates revoke + tiers + pack seal + explain together.
- **Stele solution:** **Harness** `tepa_amvl_shaped_report`.
- **Requirement:** Proxies only — never claim TEPA / AMV-L paper scores.

### UC-60 — Blast radius of a lesson *(v1.8)*
- **Scenario:** Before revoking or purging entry X, ops needs to know which LINK-neighbors would be affected.
- **Pain today (P11):** Flat related() is one hop; poison can hide deeper in the graph.
- **Stele solution:** **O** `blast_radius(entry_id, max_depth=1..5)` — undirected LINK neighborhood layers.
- **Requirement:** Report-only; never mutates SoT.

### UC-61 — Classify a merge without silent rewrite *(v1.8)*
- **Scenario:** Two federated claims arrive about the same fact; agent must decide insert/merge/relate/conflict/reject.
- **Pain today:** Naive union or LWW silently drops contradictions (MELD thesis).
- **Stele solution:** **O** `merge_classify(a, b)` — deterministic five-outcome from conflict_key + title Jaccard + contested/revoked.
- **Requirement:** Never auto-mutates; no NLI/LLM in core (C5/C7).

### UC-62 — Path trust as a Select gate *(v1.8)*
- **Scenario:** Multi-agent workflows must prefer memories whose provenance path is trusted.
- **Pain today (P10):** Semantic hit alone admits poisoned ancestry (MAP-Graph).
- **Stele solution:** **R** `path_trust(entry_id)` + `search(..., min_path_trust=, trusted_sources_for_trust=)`.
- **Requirement:** Multiplicative trust along LINK paths; revoked/contested edges degrade.

### UC-63 — Federation-shaped local harness *(v1.8)*
- **Scenario:** CI gates classify + blast + trust filter together.
- **Stele solution:** **Harness** `meld_map_shaped_report`.
- **Requirement:** Proxies only — never claim MELD AUC / MAP-Graph task scores.

### UC-64 — Graph module as protocol surface *(v1.8)*
- **Scenario:** Callers embed Stele graph helpers without importing federation frameworks.
- **Stele solution:** **T** `stele_core.graph` (`blast_radius`, `merge_classify`, `path_trust`) + MCP/CLI parity.
- **Requirement:** Zero runtime deps; outcomes auditable.

### UC-65 — Journal hash-chain integrity *(v1.9)*
- **Scenario:** Auditor needs fail-closed proof that journal rows were not rewritten mid-stream.
- **Pain today (P14):** Flat journal digest catches whole-file tamper but not surgical mid-chain edits as clearly.
- **Stele solution:** **O** each new row carries `prev_hash`/`row_hash`; `verify_journal_chain` / `journal_chain_head` (GPM-shaped).
- **Requirement:** Legacy unchained rows soft-accepted; new writes always chained.

### UC-66 — Spreading activation recall *(v1.9)*
- **Scenario:** Agent has seed lessons and needs associative neighbors, not only BM25 hits.
- **Stele solution:** **R** `spread_activate(seed_ids)` with hop decay + lateral inhibition (SYNAPSE-shaped).
- **Requirement:** Deterministic; no LLM on path (C5).

### UC-67 — Connection-density ranking *(v1.9)*
- **Scenario:** Prefer well-linked evidence over isolated tips under the same lexical score.
- **Stele solution:** **R** `connection_density` + `search(..., prefer_dense=True)` (SodaMem-shaped).
- **Requirement:** Soft re-rank only; SoT unchanged.

### UC-68 — Retention / decay Select gate *(v1.9)*
- **Scenario:** Long-horizon stores must withhold near-dead memories without deleting them.
- **Stele solution:** **R** `retention_score` + `search(..., min_retention=)` (Oblivion-shaped).
- **Requirement:** Half-life + usage reinforcement; pinned boosts retention.

### UC-69 — Activation suite harness *(v1.9)*
- **Scenario:** CI gates chain + spread + density + retention together.
- **Stele solution:** **Harness** `soda_synapse_shaped_report`.
- **Requirement:** Proxies only — never claim GPM/SYNAPSE/SodaMem/Oblivion paper scores.

### UC-70 — Unified health report *(v2.0)*
- **Scenario:** Operator needs one red/green view across integrity, chain, injection, contested.
- **Stele solution:** **O** `health_report()` aggregating doctor + journal chain + injection + seal root.
- **Requirement:** Barriers listed explicitly; never hides failures.

### UC-71 — Fail-closed release before export *(v2.0)*
- **Scenario:** Public pack must not ship while contested/injection/chain barriers are open.
- **Pain today:** Export always succeeds even when store is unhealthy.
- **Stele solution:** **O** `release_gate` + `export(..., require_release=True)`; head mismatch / head drift → abstain.
- **Requirement:** GPM-shaped fail-closed — no silent release.

### UC-72 — Cue tags for associative Select *(v2.0)*
- **Scenario:** Agent tags lessons with cues (`day-bucket`) and filters retrieval by cue.
- **Stele solution:** **K/R** optional `cue_tags` + `search(..., cue_tags=)`.
- **Requirement:** Max 32 tags; normalized lowercase; no LLM.

### UC-73 — Derived SQLite FTS index *(v2.0)*
- **Scenario:** Large stores need faster lexical search without abandoning file SoT.
- **Stele solution:** **R** `rebuild_sqlite_index` / `search_sqlite` (stdlib sqlite3 + FTS5).
- **Requirement:** Derived only — delete/rebuild anytime; files remain SoT (C4).

### UC-74 — Release suite harness *(v2.0)*
- **Scenario:** CI gates health + release + cues + SQLite together.
- **Stele solution:** **Harness** `gpm_release_shaped_report`.
- **Requirement:** Proxies only — never claim GPM-ReleaseBench scores.

### UC-75 — Decision receipts on release *(v2.1)*
- **Scenario:** A released pack/answer must bind claim IDs + policy version + verified journal head.
- **Pain today:** Release succeeds with no durable local record.
- **Stele solution:** **O** `release_gate(..., issue_receipt=True)` → `decisions/dr_*.json` with `receipt_digest`.
- **Requirement:** GPM default — no receipt on fail unless `record_abstain`; receipts are local, not transferable TEE attestation.

### UC-76 — Fail-closed import verify *(v2.1)*
- **Scenario:** Foreign packs must not hydrate until structure/injection/count/policy/seal checks pass.
- **Stele solution:** **O** `verify_import` + `hydrate(..., require_verify=True)` — halt on first failure (PAM-shaped).
- **Requirement:** No store write until gate passes.

### UC-77 — Policy manifest on export *(v2.1)*
- **Scenario:** Importers need an attested digest of audience/scope/layers/allowlist.
- **Stele solution:** **C** export stamps `policy` / `policy_digest` + `policy_manifest.json`.
- **Requirement:** Digest mismatch fails `verify_import`.

### UC-78 — Lineage trust Select filter *(v2.1)*
- **Scenario:** Lessons linked to contested/revoked/quarantine ancestors must be refuse-able.
- **Stele solution:** **R** `lineage_trust` labels + `search(..., refuse_untrusted_lineage=True)`.
- **Requirement:** Deterministic state walk only — no LLM (MemLineage-shaped).

### UC-79 — Decision/import suite harness *(v2.1)*
- **Scenario:** CI gates receipts + import verify + lineage refuse together.
- **Stele solution:** **Harness** `pam_cava_shaped_report`.
- **Requirement:** Proxies only — never claim PAM Transfer Continuity / CAVA / MemLineage scores.

### UC-80 — Proof-of-execution ledger *(v2.2)*
- **Scenario:** Agent memory claims “safety already done”; attacker rewords the note.
- **Pain today:** Wording filters inspect attacker-controlled text.
- **Stele solution:** **O** independent `executions.ndjson` chain via `record_execution` — only trusted runtime writes.
- **Requirement:** Never authorize from entry body text (PoEM-shaped).

### UC-81 — Verify execution before skip *(v2.2)*
- **Scenario:** Runtime may skip a safety step only if the ledger confirms it ran for that subject.
- **Stele solution:** **O** `verify_execution(step, subject_id)` — fail closed on miss / chain break / cross-subject.
- **Requirement:** Memory claims alone never set `allowed=True`.

### UC-82 — Provenance authority firewall *(v2.2)*
- **Scenario:** Pack-hydrated or session memories must not authorize critical tools after consolidation.
- **Stele solution:** **O** `authority_gate(entry_ids, action_risk=)` — non-amplification caps (PPMF-shaped).
- **Requirement:** Deterministic provenance scores only — no LLM rewrite trust.

### UC-83 — Exact claim closure *(v2.2)*
- **Scenario:** Released structured claims must each map to a promoted assertable fact at one head.
- **Stele solution:** **O** `claim_closure(claim_ids, expected_head=)`.
- **Requirement:** Head mismatch or non-promoted IDs fail closed (GPM-shaped).

### UC-84 — PoEM/PPMF suite harness *(v2.2)*
- **Scenario:** CI gates execution deny/allow + authority caps + claim closure together.
- **Stele solution:** **Harness** `poem_ppmf_shaped_report`.
- **Requirement:** Proxies only — never claim PoEM ASR / PPMF ASR scores.

### UC-85 — Cascade impact of a fault *(v2.3)*
- **Scenario:** When a source lesson is invalidated, derived LINK descendants may still steer actions.
- **Stele solution:** **O** `cascade_impact` / `cascade_exposure` over depends-on entry LINKs.
- **Requirement:** Report promoted exposure count (MemoRepair-shaped metric).

### UC-86 — Barrier-first cascade withdraw *(v2.3)*
- **Scenario:** Repair must not leave invalidated descendants in service during reconstruction.
- **Stele solution:** **O** `withdraw_cascade` revokes fault+descendants before any republish.
- **Requirement:** History retained; not DELETE; exposure_after.promoted_exposed → 0.

### UC-87 — Predecessor-closed repair plan *(v2.3)*
- **Scenario:** Operator wants cost-aware which descendants to rebuild without exhaustive repair-all.
- **Stele solution:** **O** `repair_plan(lambda_cost=, budget=)` — greedy predecessor-closure proxy.
- **Requirement:** Report-only; document not exact s–t min-cut.

### UC-88 — Non-revival probe *(v2.3)*
- **Scenario:** Withdrawn/revoked IDs must not resurface in ordinary SEARCH.
- **Stele solution:** **O** `non_revival_probe(forbidden_ids=)`.
- **Requirement:** Fail if any forbidden ID appears in hits (GPM non-revival).

### UC-89 — MemoRepair suite harness *(v2.3)*
- **Scenario:** CI gates exposure → plan → withdraw → non-revival together.
- **Stele solution:** **Harness** `memorepair_shaped_report`.
- **Requirement:** Proxies only — never claim MemoRepair ToolBench scores.

### UC-90 — Typed memory roles *(v2.4)*
- **Scenario:** Flat text collapses evidence and truth-bearing claims (source-monitoring errors).
- **Stele solution:** **K** optional `memory_role` = evidence|claim|decision (layer defaults).
- **Requirement:** JSON Schema enum; no LLM typing.

### UC-91 — Fact interface projection *(v2.4)*
- **Scenario:** Answer generation needs claim-centered bundles, not raw evidence alone.
- **Stele solution:** **R/O** `fact_interface` + `authorize_ids` (claims+decisions only).
- **Requirement:** Evidence atoms listed separately; never in authorize set.

### UC-92 — Claims-only Select + role-gated closure *(v2.4)*
- **Scenario:** Routine retrieval and release must not authorize from evidence-role IDs.
- **Stele solution:** **R** `search(..., claims_only=True)` + `claim_closure(require_claim_role=True)`.
- **Requirement:** Fail closed when evidence IDs are offered as claims.

### UC-93 — Dual-channel Select with quality gate *(v2.4)*
- **Scenario:** Routine BM25 is cheap; contested/weak hits need deliberation channel.
- **Stele solution:** **R** `dual_channel_search` + `quality_gate` (D-Mem-shaped).
- **Requirement:** Deterministic escalate reasons only.

### UC-94 — MemIR/D-Mem suite harness *(v2.4)*
- **Scenario:** CI gates roles + interface + dual channel together.
- **Stele solution:** **Harness** `memir_dmem_shaped_report`.
- **Requirement:** Proxies only — never claim MemIR LoCoMo / D-Mem F1 scores.

### UC-95 — Memory view commits *(v2.5)*
- **Scenario:** Reasoning/memory views must be replayable and tagged success/failed.
- **Stele solution:** **O** `commit_view` → `commits.ndjson` + branch refs (stdlib; no git binary).
- **Requirement:** Hash-chained; binds entry id set + journal head.

### UC-96 — Checkout / replay *(v2.5)*
- **Scenario:** Incident review needs the exact id set at a commit SHA.
- **Stele solution:** **O** `checkout_view(commit_hash)`.
- **Requirement:** Reconstructs ids only — bodies load from SoT.

### UC-97 — Diff commits *(v2.5)*
- **Scenario:** Compare success vs failed reasoning views.
- **Stele solution:** **O** `diff_commits(a, b)` entry-set only_in / shared.
- **Requirement:** Audit substrate — not accuracy improvement claim.

### UC-98 — Copyability gate *(v2.5)*
- **Scenario:** Memory helps accuracy mainly on near-duplicates (τ≈0.8).
- **Stele solution:** **R** `copyability_gate(query, threshold=0.8)`.
- **Requirement:** Below threshold → `memory_likely_helps=False` (GitOfThoughts boundary).

### UC-99 — GitOfThoughts suite harness *(v2.5)*
- **Scenario:** CI gates commit/diff/copyability together.
- **Stele solution:** **Harness** `gitofthoughts_shaped_report`.
- **Requirement:** Proxies only — never claim GitOfThoughts accuracy scores.

### UC-100 — Pin memory version *(v2.6)*
- **Scenario:** Before a risky update, ops must snapshot the whole promoted memory view.
- **Stele solution:** **O** `pin_memory_version(label)` → tagged `commits.ndjson` view of promoted ids.
- **Requirement:** ChronoMem-shaped; does not rewrite entry files.

### UC-101 — Activate / clear read HEAD *(v2.6)*
- **Scenario:** After bad exposure, Select must behave as-if at a prior version.
- **Stele solution:** **O** `activate_version(commit_hash|None)` writes `refs/read_head`.
- **Requirement:** Overlay only — SoT unchanged; clear restores live Select.

### UC-102 — Counterfactual search *(v2.6)*
- **Scenario:** Post-exposure probe without mutating read_head.
- **Stele solution:** **R** `counterfactual_search(..., version_commit=)` via `_version_select`.
- **Requirement:** Surfaces pinned ids even if later superseded in live SoT.

### UC-103 — Exclude superseded / stale-fact scan *(v2.6)*
- **Scenario:** Live Select must not serve retired facts under the same conflict_key.
- **Stele solution:** **R** `exclude_superseded` + **O** `stale_fact_scan` (MemStrata-shaped).
- **Requirement:** Deterministic winners; no similarity threshold; no LLM on read path.

### UC-104 — ChronoMem/MemStrata suite harness *(v2.6)*
- **Scenario:** CI gates pin/activate/counterfactual/stale together.
- **Stele solution:** **Harness** `chronomem_strata_shaped_report`.
- **Requirement:** Proxies only — never claim ChronoMem / MemStrata paper scores.

### UC-105 — Propose TARL update *(v2.7)*
- **Scenario:** Incoming statements must map to distinct update outcomes, not binary Write/Hold.
- **Stele solution:** **O** `propose_update` → `append|noop|revise|reject_conflict|defer_verify`.
- **Requirement:** Deterministic (conflict_key, digest, authority, injection); no LLM.

### UC-106 — Apply TARL update *(v2.7)*
- **Scenario:** Ops executes the chosen action against SoT ledgers.
- **Stele solution:** **O** `apply_update` (optional forced `action`).
- **Requirement:** revise→supersede; reject→revoked provenance retained; defer/append→quarantine.

### UC-107 — Ledger view *(v2.7)*
- **Scenario:** Inspect accepted / pending / rejected counts without scanning files by hand.
- **Stele solution:** **O** `ledger_view`.
- **Requirement:** Projection over Stele states only.

### UC-108 — Memory Worth + suppress *(v2.7)*
- **Scenario:** Suppress lessons that co-occur with failure more than success.
- **Stele solution:** **O** `memory_worth` / `low_worth_scan`; **R** `min_worth` Select filter.
- **Requirement:** Associational only — never claim causal utility.

### UC-109 — TARL/MW suite harness *(v2.7)*
- **Scenario:** CI gates five-action updates + MW suppress together.
- **Stele solution:** **Harness** `tarl_mw_shaped_report`.
- **Requirement:** Proxies only — never claim TARL-Mem / MW Spearman scores.

### UC-110 — Belief transaction lifecycle *(v2.8)*
- **Scenario:** Observations must stage before becoming actionable beliefs.
- **Stele solution:** **O** `begin_transaction` / `stage_write` / `validate_transaction` / `commit_transaction` / `abort_transaction`.
- **Requirement:** Write ≠ commit; staged entries stay tentative until promote-on-commit.

### UC-111 — Action-safety gate *(v2.8)*
- **Scenario:** Irreversible tool calls must not act on tentative or in-flight memory.
- **Stele solution:** **O** `action_safe_gate(entry_ids)`.
- **Requirement:** Fail-closed unless all ids are action_safe and no open tx overlaps conflict_key.

### UC-112 — In-flight report *(v2.8)*
- **Scenario:** Ops needs visibility into open transactions and staged ids.
- **Stele solution:** **O** `in_flight_report`.
- **Requirement:** Report-only.

### UC-113 — AOEP obligation coverage *(v2.8)*
- **Scenario:** Always-on governance must score mutation/recovery obligations.
- **Stele solution:** **O** `aoep_report`.
- **Requirement:** Local checklist proxy — not Always-On corpus scores.

### UC-114 — MemTX/AOEP suite harness *(v2.8)*
- **Scenario:** CI gates stage/commit/action-safe/in-flight/AOEP together.
- **Stele solution:** **Harness** `memtx_aoep_shaped_report`.
- **Requirement:** Proxies only — never claim MemTX backbone scores.

### UC-115 — Symbolic conflict scan *(v2.9)*
- **Scenario:** Multi-agent stores need cheap mechanical conflict detection before any LLM.
- **Stele solution:** **O** `symbolic_conflict_scan` (duplicate promoted keys + LINK triangles).
- **Requirement:** Deterministic; no LLM.

### UC-116 — Classify conflict *(v2.9)*
- **Scenario:** Distinguish credibility (one wins) vs coordination (coexist).
- **Stele solution:** **O** `classify_conflict(a, b)`.
- **Requirement:** Report-only; never silent-merge coordination.

### UC-117 — Compact render *(v2.9)*
- **Scenario:** Reader context is character-budgeted (LatticeMind budgeted track).
- **Stele solution:** **R** `compact_render(..., reader_budget=1400)`.
- **Requirement:** External budget over packed slices; report overflow ids.

### UC-118 — Effect outbox *(v2.9)*
- **Scenario:** Belief commit must not auto-fire irreversible tool side effects.
- **Stele solution:** **O** `stage_effect` / `release_effects` / `mark_effect_dispatched` / `cancel_effect` / `compensate_effect` / `list_effects`.
- **Requirement:** Stele never calls external sinks.

### UC-119 — LatticeMind/Cordon suite harness *(v2.9)*
- **Scenario:** CI gates symbolic conflict + compact render + outbox together.
- **Stele solution:** **Harness** `lattice_cordon_shaped_report`.
- **Requirement:** Proxies only — never claim LatticeMind / Cordon paper scores.

### UC-120 — State resolution *(v3.0)*
- **Scenario:** Detect whether each conflict_key has a single current winner.
- **Stele solution:** **O** `state_resolution`.
- **Requirement:** STALE State Resolution proxy — explicit keys only.

### UC-121 — Premise resistance *(v3.0)*
- **Scenario:** Reject queries that presuppose superseded state.
- **Stele solution:** **O** `premise_resistance(query)`.
- **Requirement:** Token-overlap heuristic; refuse_premise when stale dominates.

### UC-122 — IPA gap + related slots *(v3.0)*
- **Scenario:** Updated evidence can be visible while stale still surfaces; domain siblings need reverify.
- **Stele solution:** **O** `ipa_gap_scan` / `related_slot_scan`.
- **Requirement:** Report-only; fix via exclude_superseded / human reverify.

### UC-123 — VTA verify transition + GEM report *(v3.0)*
- **Scenario:** Supersede pairs need provenance/chronology verify; GEM asks for state-operator coverage.
- **Stele solution:** **O** `verify_transition` / `gem_report`.
- **Requirement:** Verified ≠ semantically true; GEM checklist is local obligations.

### UC-124 — STALE/GEM suite harness *(v3.0)*
- **Scenario:** CI gates resolution/premise/VTA/GEM together.
- **Stele solution:** **Harness** `stale_gem_shaped_report`.
- **Requirement:** Proxies only — never claim STALE/VTA/GEM paper scores.

### UC-125 — Projection resolve + pin *(v3.1)*
- **Scenario:** Contested or symmetric beliefs must abstain at read time without rewriting SoT.
- **Stele solution:** **O** `project_resolve` / `pin_projection` / `clear_projection_pin`.
- **Requirement:** Pins are overlay-only (StateFuse bounded authority).

### UC-126 — Correction handles *(v3.1)*
- **Scenario:** Callers need exact claim_id or semantic claim_ref to target corrections across replicas.
- **Stele solution:** **O** `correction_handle`.
- **Requirement:** Exact + token/conflict_key match — not NLI.

### UC-127 — TOKI operator classify *(v3.1)*
- **Scenario:** Before writing, classify LWW / evidence-weighted / await / policy with isolation precondition.
- **Stele solution:** **O** `toki_classify_operator`.
- **Requirement:** Plan-only; judge stays off write path.

### UC-128 — TOKI anomaly scan + context bid *(v3.1)*
- **Scenario:** Detect audit-erasure / belief-drift / replay proxies; triage context slots by bid.
- **Stele solution:** **O** `toki_anomaly_scan` / `context_bid`.
- **Requirement:** Report-only; no auto-delete.

### UC-129 — StateFuse/TOKI suite harness *(v3.1)*
- **Scenario:** CI gates projection pin + handles + operator + anomalies + bid together.
- **Stele solution:** **Harness** `statefuse_toki_shaped_report`.
- **Requirement:** Proxies only — never claim StateFuse/TOKI/MemArchitect paper scores.

### UC-130 — Exact min-cut repair select *(v3.2)*
- **Scenario:** After cascade withdraw, choose predecessor-closed successors optimally for λ.
- **Stele solution:** **O** `repair_select_mincut`.
- **Requirement:** Exact Picard closure via Edmonds–Karp — report-only.

### UC-131 — CUPMem write-side adjudicate *(v3.2)*
- **Scenario:** Incoming evidence must decide activate / revise / block / unknown-current before write.
- **Stele solution:** **O** `adjudicate_update`.
- **Requirement:** Deterministic; does not write.

### UC-132 — Unknown-current + authorize retrieval *(v3.2)*
- **Scenario:** Generation must not assert from contested/unresolved slots.
- **Stele solution:** **O** `unknown_current_slots` / `authorize_retrieval`.
- **Requirement:** Filter plan only — callers apply.

### UC-133 — CMGL admit gate *(v3.2)*
- **Scenario:** Protected writes need structured authority; NL-only auth fails closed.
- **Stele solution:** **O** `admit_gate` / `list_admit_receipts` / `verify_admit_receipt`.
- **Requirement:** Local receipts — not product CMGL.

### UC-134 — MemoRepair/CUPMem/CMGL suite harness *(v3.2)*
- **Scenario:** CI gates min-cut + adjudicate + authorize + admit together.
- **Stele solution:** **Harness** `memorepair_cupmem_cmgl_shaped_report`.
- **Requirement:** Proxies only.

### UC-135 — TierMem raw + sufficiency *(v3.3)*
- **Scenario:** Summaries may omit query-critical detail; need raw logs + miss detection.
- **Stele solution:** **O** `put_raw_page` / `sufficiency_gate`.
- **Requirement:** Deterministic miss cues — not trained router.

### UC-136 — Escalate + verified write-back *(v3.3)*
- **Scenario:** On miss, load linked raw; distill grounded summary back with provenance links.
- **Stele solution:** **O** `escalate_raw` / `verified_writeback`.
- **Requirement:** Promote still needs separate oracle (C7).

### UC-137 — Skill eligibility + crystallize *(v3.3)*
- **Scenario:** Evidence-backed lessons become callable skill_artifact drafts.
- **Stele solution:** **O** `skill_eligibility` / `crystallize_skill`.
- **Requirement:** Positive gain + evidence/links; optional ADD.

### UC-138 — Value backfill + skill catalog *(v3.3)*
- **Scenario:** Terminal outcomes update usage; list callable skills.
- **Stele solution:** **O** `value_backfill` / `skill_catalog`.
- **Requirement:** Backfill plan or apply; catalog is report surface.

### UC-139 — TierMem/MSCE suite harness *(v3.3)*
- **Scenario:** CI gates write-back + escalate + crystallize together.
- **Stele solution:** **Harness** `tiermem_msce_shaped_report`.
- **Requirement:** Proxies only — never claim TierMem/MSCE paper scores.

### UC-140 — FadeMem dual-layer strength *(v3.4)*
- **Scenario:** Hot vs pinned/long-lived lessons need different decay curves.
- **Stele solution:** **O** `fade_strength`.
- **Requirement:** SML/LML Weibull proxies — report only.

### UC-141 — Fade scan + fusion candidates *(v3.4)*
- **Scenario:** Operators need a forget/fuse queue without silent auto-delete.
- **Stele solution:** **O** `fade_scan` / `fusion_candidates`.
- **Requirement:** Never auto-deletes; fusion is a deterministic plan.

### UC-142 — SSGM Weibull Select *(v3.4)*
- **Scenario:** Retrieval should prefer relevance-decayed tips under a clock.
- **Stele solution:** **O** `weibull_relevance` + Select `min_weibull`.
- **Requirement:** Requires store clock; annotates hit slices.

### UC-143 — MemR3 evidence gap *(v3.4)*
- **Scenario:** One Select pass may leave query tokens/digits uncovered.
- **Stele solution:** **O** `evidence_gap`.
- **Requirement:** Deterministic token/digit coverage — not LLM reflection.

### UC-144 — Reflective retrieve + gap tracker *(v3.4)*
- **Scenario:** Caller needs next probes and a closed-loop gap update.
- **Stele solution:** **O** `reflective_retrieve` / `gap_tracker_update`.
- **Requirement:** Plan only — caller runs follow-up Select.

### UC-145 — FadeMem/MemR3 suite harness *(v3.4)*
- **Scenario:** CI gates fade + Weibull + reflective gap together.
- **Stele solution:** **Harness** `fademem_memr3_shaped_report`.
- **Requirement:** Proxies only — never claim FadeMem / MemR3 / SSGM paper scores.

### UC-146 — Archive plan *(v3.5)*
- **Scenario:** Aged unused episodic notes need a forget queue without delete.
- **Stele solution:** **O** `archive_plan`.
- **Requirement:** Report-only; guidance layers never eligible.

### UC-147 — Archive apply + unarchive *(v3.5)*
- **Scenario:** Operators move tips out of Select and restore later.
- **Stele solution:** **O** `archive_apply` / `unarchive` / `list_archived`.
- **Requirement:** New state `archived`; Select excludes; reversible.

### UC-148 — SF-AMS composite importance *(v3.5)*
- **Scenario:** Rank tips by blended relevance/worth/retention — not TTL alone.
- **Stele solution:** **O** `composite_importance` / `cis_scan`.
- **Requirement:** Deterministic CIS tiers — not paper CIS.

### UC-149 — MemCon control suggest *(v3.5)*
- **Scenario:** Callers need when/what/how much memory action without a fixed heuristic buried in app code.
- **Stele solution:** **O** `control_suggest`.
- **Requirement:** Heuristic proxy — not UCB bandit training.

### UC-150 — Archive/SF-AMS/MemCon suite harness *(v3.5)*
- **Scenario:** CI gates archive withhold + CIS + control together.
- **Stele solution:** **Harness** `archive_sfams_memcon_shaped_report`.
- **Requirement:** Proxies only.

### UC-151 — Schema `archived` state *(v3.5)*
- **Scenario:** Soft forget must be a first-class ledger state, not a silent flag.
- **Stele solution:** **K** `STATES` includes `archived`.
- **Requirement:** JSON Schema + validation enumerate it.

### UC-152 — SCM value tag + working memory *(v3.6)*
- **Scenario:** Wake-phase tips need capacity-limited scratch + multi-signal importance.
- **Stele solution:** **O** `value_tag` / `wm_push` / `wm_list` / `wm_clear`.
- **Requirement:** Overlay only — not SoT; capacity default 7.

### UC-153 — SCM sleep cycle *(v3.6)*
- **Scenario:** Offline consolidation should plan NREM/REM/FORGET without silent prune.
- **Stele solution:** **O** `sleep_trigger` / `sleep_plan` / `sleep_apply_nrem`.
- **Requirement:** Plan report-only; NREM apply reinforces usage only.

### UC-154 — GAM episodic buffer *(v3.6)*
- **Scenario:** Quarantine is the fast buffer; promote stays oracle-gated.
- **Stele solution:** **O** `episodic_buffer`.
- **Requirement:** Quarantined surface only.

### UC-155 — GAM boundary + consolidate plan *(v3.6)*
- **Scenario:** Topic shifts should trigger consolidate review, not stream merge into SoT.
- **Stele solution:** **O** `semantic_boundary` / `consolidate_plan`.
- **Requirement:** Never auto-promotes (C7).

### UC-156 — ACM anticipate *(v3.6)*
- **Scenario:** Prefetch likely-next tips off the critical path.
- **Stele solution:** **O** `anticipate`.
- **Requirement:** Prefetch plan from LINKs / conflict_key / token overlap.

### UC-157 — ACM compaction verify *(v3.6)*
- **Scenario:** Compaction that drops critical tokens must fail closed.
- **Stele solution:** **O** `verify_compaction`.
- **Requirement:** Critical query∩hit tokens must remain in compacted text.

### UC-158 — SCM/GAM/ACM suite harness *(v3.6)*
- **Scenario:** CI gates sleep/WM + buffer/boundary + anticipate/verify together.
- **Stele solution:** **Harness** `scm_gam_acm_shaped_report`.
- **Requirement:** Proxies only.

### UC-159 — LightMem sensory filter *(v3.7)*
- **Scenario:** Raw drafts carry stopword noise before ADD.
- **Stele solution:** **O** `sensory_filter`.
- **Requirement:** Deterministic token filter — not LLMLingua.

### UC-160 — LightMem stages + topic segments *(v3.7)*
- **Scenario:** Route work across sensory/STM/LTM efficiently.
- **Stele solution:** **O** `stage_inventory` / `topic_segments` / `stage_budget_plan`.
- **Requirement:** Atkinson–Shiffrin proxy stages.

### UC-161 — HippoRAG PPR *(v3.7)*
- **Scenario:** Multi-hop association needs graph walk beyond top-k lexical.
- **Stele solution:** **O** `ppr_scores` / `multi_hop_retrieve`.
- **Requirement:** Personalized PageRank on LINK graph — not neural HippoRAG.

### UC-162 — Quipu write gate *(v3.7)*
- **Scenario:** Pending facts must not enter until post-state predicates pass.
- **Stele solution:** **O** `write_gate`.
- **Requirement:** Report-only; fail-closed on incomplete/poison/universal-unpinned.

### UC-163 — MAP-Graph action risk gate *(v3.7)*
- **Scenario:** Irreversible actions need risk-sensitive Allow/Block/Reverify.
- **Stele solution:** **O** `action_risk_gate`.
- **Requirement:** θ by risk; affected support blocks high-risk.

### UC-164 — LightMem/HippoRAG/Quipu suite harness *(v3.7)*
- **Scenario:** CI gates filter/stages/PPR/gates together.
- **Stele solution:** **Harness** `lightmem_hippo_quipu_shaped_report`.
- **Requirement:** Proxies only.

### UC-165 — Stage budget efficiency *(v3.7)*
- **Scenario:** Reader budgets should prefer STM then LTM then sensory residual.
- **Stele solution:** Covered by `stage_budget_plan` (UC-160).
- **Requirement:** used ≤ budget.

### UC-166 — ProGraph compression residuals *(v3.8)*
- **Scenario:** Summaries drop dates, quantities, and code-like tokens that queries need.
- **Stele solution:** **O** `extract_residuals` / `residual_augment`.
- **Requirement:** Deterministic residual packs — not LLM co-extract.

### UC-167 — ProGraph entity registry + profile expand *(v3.8)*
- **Scenario:** Profile-linked neighbors must expand beyond lexical top-k.
- **Stele solution:** **O** `register_entities` / `profile_expand`.
- **Requirement:** Entity substring traversal with expand gate; no graph DB.

### UC-168 — EMG correction path match *(v3.8)*
- **Scenario:** A failure lesson needs a one-shot edit path toward a successful workflow.
- **Stele solution:** **O** `match_correction`.
- **Requirement:** Report-only add/delete/keep tokens — never auto-rewrites SoT.

### UC-169 — EMG insight inject *(v3.8)*
- **Scenario:** Callers need a loop-free guidance string from a correction path.
- **Stele solution:** **O** `insight_inject`.
- **Requirement:** Single-pass insight; no reflect-replay loop.

### UC-170 — AgentIR cascade route *(v3.8)*
- **Scenario:** Expensive PPR should skip when lexical margin is decisive.
- **Stele solution:** **O** `cascade_route`.
- **Requirement:** Margin-triggered `lexical_only` vs `full_rrf`.

### UC-171 — AgentIR multi-channel fuse *(v3.8)*
- **Scenario:** Fuse lexical + optional PPR + residual channels without a second fusion API.
- **Stele solution:** **O** `multi_channel_fuse` (reuses `rrf_fuse`).
- **Requirement:** Channel list + fused hits; Proxies only.

### UC-172 — ProGraph/EMG/AgentIR suite harness *(v3.8)*
- **Scenario:** CI gates residuals/expand/match/cascade/fuse together.
- **Stele solution:** **Harness** `prograph_emg_agentir_shaped_report`.
- **Requirement:** Proxies only.

### UC-173 — Residual-augmented reader context *(v3.8)*
- **Scenario:** Selected hits must carry query-relevant residuals into the reader pack.
- **Stele solution:** Covered by `residual_augment` (UC-166).
- **Requirement:** Residuals ranked for query relevance.

### UC-174 — Dual memory project *(v3.9)*
- **Scenario:** Callers need both open-set facts and typed properties from one entry.
- **Stele solution:** **O** `dual_project`.
- **Requirement:** Deterministic sentence facts + schema properties — not LLM dual extract.

### UC-175 — Governance route *(v3.9)*
- **Scenario:** Multi-step agents need fast policy/workflow ranking without an LLM path.
- **Stele solution:** **O** `governance_route`.
- **Requirement:** Fast hybrid only; critical vs supplementary tiers.

### UC-176 — Progressive session delta *(v3.9)*
- **Scenario:** Re-injecting the same critical governance every step wastes tokens.
- **Stele solution:** **O** `session_delta_open` / `session_delta_deliver` / `session_delta_status`.
- **Requirement:** Skip delivered critical; never lock supplementary.

### UC-177 — Entity context compile *(v3.9)*
- **Scenario:** Downstream needs a budgeted Properties + Observations block per subject.
- **Stele solution:** **O** `entity_context`.
- **Requirement:** Properties first; saturation ≈ 7.

### UC-178 — Entity leak probe *(v3.9)*
- **Scenario:** Cross-entity leakage must fail closed under adversarial same-scope neighbors.
- **Stele solution:** **O** `entity_leak_probe`.
- **Requirement:** Key prefilter (not embedding distance); leak_count == 0 when filtered.

### UC-179 — HyMem slot classify *(v3.9)*
- **Scenario:** Long-horizon agents dilute the planner with raw execute traces.
- **Stele solution:** **O** `hymem_classify_slot`.
- **Requirement:** plan/execute/reason/memory cue proxy.

### UC-180 — HyMem isolate pack *(v3.9)*
- **Scenario:** Only typed returns may cross into the planner pack.
- **Stele solution:** **O** `hymem_isolate_pack`.
- **Requirement:** dilution_ok; raw execute/reason blocked.

### UC-181 — Governed Memory / HyMem suite harness *(v3.9)*
- **Scenario:** CI gates dual/route/delta/entity/hymem together.
- **Stele solution:** **Harness** `govmem_hymem_shaped_report`.
- **Requirement:** Proxies only.

### UC-182 — Progressive token efficiency *(v3.9)*
- **Scenario:** Second delivery of the same critical set must shrink inject.
- **Stele solution:** Covered by `session_delta_deliver` (UC-176).
- **Requirement:** skipped_critical grows on repeat criticals.

### UC-183 — Version marker extract *(v4.0)*
- **Scenario:** Conflict resolution needs explicit serial/timestamp markers, not LLM guesswork.
- **Stele solution:** **O** `extract_version_markers`.
- **Requirement:** Deterministic regex + temporal fields.

### UC-184 — Freshness resolve *(v4.0)*
- **Scenario:** Among conflicting tips, the freshest must win via max(serial|ts).
- **Stele solution:** **O** `freshness_resolve`.
- **Requirement:** Python max — never LLM freshness judgment.

### UC-185 — Assemble current *(v4.0)*
- **Scenario:** Query → candidates → per-conflict_key tip assembly.
- **Stele solution:** **O** `assemble_current`.
- **Requirement:** Assembly is the bottleneck fix (arXiv:2606.01435).

### UC-186 — Hop freshness *(v4.0)*
- **Scenario:** Multi-hop questions need per-hop deterministic tips.
- **Stele solution:** **O** `hop_freshness`.
- **Requirement:** Self-Ask-shaped hops without LLM resolver.

### UC-187 — Ordered PatchTest *(v4.0)*
- **Scenario:** Pending updates must be source-supported before commit.
- **Stele solution:** **O** `patch_test`.
- **Requirement:** Cited span or ≥50% token overlap; fail closed.

### UC-188 — Temporal resolve + active map *(v4.0)*
- **Scenario:** Visible tip under conflict_key must be recoverable after faults.
- **Stele solution:** **O** `temporal_resolve` / `recover_active_map`.
- **Requirement:** Deterministic chronology; report-only map.

### UC-189 — Fleet scope gate *(v4.0)*
- **Scenario:** Cross-fleet reads must not leak via missing scope checks.
- **Stele solution:** **O** `fleet_scope_gate`.
- **Requirement:** Explicit allowlist; no implicit universal.

### UC-190 — Propagate plan + stale scan *(v4.0)*
- **Scenario:** Propagation is policy-governed; stale tips beside fresher winners are pollution.
- **Stele solution:** **O** `propagate_plan` / `stale_propagation_scan`.
- **Requirement:** Report-only; never silent merge.

### UC-191 — Freshness/MemTxn/Fleet suite harness *(v4.0)*
- **Scenario:** CI gates assembly + patch + fleet together.
- **Stele solution:** **Harness** `freshness_memtxn_fleet_shaped_report`.
- **Requirement:** Proxies only.

### UC-192 — Stale promoted tip detection *(v4.0)*
- **Scenario:** Two promoted tips under one conflict_key with different freshness must surface.
- **Stele solution:** Covered by `stale_propagation_scan` (UC-190).
- **Requirement:** Older tip listed as suspect.

### UC-193 — Query complexity *(v4.1)*
- **Scenario:** Runtime memory cost should scale with query hardness.
- **Stele solution:** **O** `query_complexity`.
- **Requirement:** Deterministic token+cue score — not RL.

### UC-194 — Budget tier route *(v4.1)*
- **Scenario:** Each memory module needs Low/Mid/High compute tiers per query.
- **Stele solution:** **O** `budget_tier_route`.
- **Requirement:** Heuristic tiers; C5 preserved (no neural router).

### UC-195 — Budget module plan *(v4.1)*
- **Scenario:** Fit module tiers under a global cost ceiling.
- **Stele solution:** **O** `budget_module_plan`.
- **Requirement:** Demote expand first; fits ≤ budget.

### UC-196 — Skill library rank *(v4.1)*
- **Scenario:** Large skill libraries need sparse on-demand loading.
- **Stele solution:** **O** `skill_rank`.
- **Requirement:** Lexical hybrid over skill_artifact/workflow — not dense+LLM edges.

### UC-197 — Skill prereq expand *(v4.1)*
- **Scenario:** Workflow relations help sequencing but must not invent reach.
- **Stele solution:** **O** `skill_prereq_expand`.
- **Requirement:** LINK walk only; graph cannot extend ranker reach.

### UC-198 — Retrieval primitives + skills *(v4.1)*
- **Scenario:** Retrieval behaviors should be reusable executable skills.
- **Stele solution:** **O** `list_retrieval_primitives` / `list_retrieval_skills` / `compose_retrieval_skill`.
- **Requirement:** Validated primitive sequences.

### UC-199 — Route + run retrieval skill *(v4.1)*
- **Scenario:** Match query demand to a skill and execute it.
- **Stele solution:** **O** `route_retrieval_skill` / `run_retrieval_skill`.
- **Requirement:** Cue router + orchestration of existing Stele ops.

### UC-200 — BudgetMem/ERSkill suite harness *(v4.1)*
- **Scenario:** CI gates tiers + skill rank + retrieval skills together.
- **Stele solution:** **Harness** `budgetmem_erskill_shaped_report`.
- **Requirement:** Proxies only.

### UC-201 — Hard-query budget escalation *(v4.1)*
- **Scenario:** Multi-cue hard queries should escalate expand/assemble tiers.
- **Stele solution:** Covered by `budget_tier_route` (UC-194).
- **Requirement:** band mid/high ⇒ expand ≥ mid.

### UC-202 — Skill-first retrieval path *(v4.1)*
- **Scenario:** Procedure queries should prefer skill_rank before lexical dump.
- **Stele solution:** Covered by `run_retrieval_skill(skill=skill_first)` (UC-199).
- **Requirement:** skill_first in built-in catalog.

### UC-203 — Consistency support score *(v4.2)*
- **Scenario:** Write admission needs a support score, not utility/recency alone.
- **Stele solution:** **O** `support_score`.
- **Requirement:** Lexical context+store overlap — not K LLM votes.

### UC-204 — Consistency admit *(v4.2)*
- **Scenario:** Contaminating facts must not silently enter as trusted premises.
- **Stele solution:** **O** `consistency_admit` → admit | quarantine | reject.
- **Requirement:** τ gate + injection reject + conflict_key quarantine.

### UC-205 — Retrieval admit *(v4.2)*
- **Scenario:** Similarity search alone leaks cross-task / jailbreak memories.
- **Stele solution:** **O** `retrieval_admit`.
- **Requirement:** Query-conditioned overlap + injection withhold.

### UC-206 — Task-conditioned pack *(v4.2)*
- **Scenario:** Reader packs must only include admitted hits under budget.
- **Stele solution:** **O** `task_conditioned_pack`.
- **Requirement:** used ≤ budget after MemGate filter.

### UC-207 — Sovereignty checklist *(v4.2)*
- **Scenario:** Operators need coverage over nine mnemonic-governance primitives.
- **Stele solution:** **O** `sovereignty_checklist`.
- **Requirement:** Explicit covered/missing list.

### UC-208 — Post-deletion verify *(v4.2)*
- **Scenario:** Delete must be verifiable — survey blind spot.
- **Stele solution:** **O** `post_delete_verify`.
- **Requirement:** Absent from store and Select hits.

### UC-209 — Rollback plan *(v4.2)*
- **Scenario:** Contaminated tips need an auditable rollback plan.
- **Stele solution:** **O** `rollback_plan`.
- **Requirement:** Report-only; actor applies revoke/delete.

### UC-210 — Consistency/MemGate/sovereignty suite harness *(v4.2)*
- **Scenario:** CI gates write admit + retrieval admit + sovereignty together.
- **Stele solution:** **Harness** `consistency_memgate_sovereignty_shaped_report`.
- **Requirement:** Proxies only.

### UC-211 — Poison reject at write gate *(v4.2)*
- **Scenario:** Injection-shaped pending bodies must reject, not quarantine-as-trust.
- **Stele solution:** Covered by `consistency_admit` (UC-204).
- **Requirement:** decision == reject on ignore-prior markers.

### UC-212 — Density fuse *(v4.3)*
- **Scenario:** Multi-tunnel hits need a single ranked evidence list by connection density.
- **Stele solution:** **O** `density_fuse`.
- **Requirement:** Mass accumulates per id; strong/direct outweighs weak/derived.

### UC-213 — Evidence plan *(v4.3)*
- **Scenario:** Planner must gather evidence IDs before reader prose.
- **Stele solution:** **O** `evidence_plan`.
- **Requirement:** Lexical + LINK-derived tunnels fuse into ranked evidence.

### UC-214 — Cited pack *(v4.3)*
- **Scenario:** Reader blocks must cite evidence ids under budget.
- **Stele solution:** **O** `cited_pack`.
- **Requirement:** Every block has `citation`; `all_cited` true when blocks present.

### UC-215 — Compress candidates *(v4.3)*
- **Scenario:** Near-duplicates should surface for compression review.
- **Stele solution:** **O** `compress_candidates`.
- **Requirement:** Similarity propose only; same-scope preference.

### UC-216 — Refine plan *(v4.3)*
- **Scenario:** Store must shrink to a target count without LLM judge.
- **Stele solution:** **O** `refine_plan`.
- **Requirement:** Report-only merge/delete actions until `final_count ≤ target`.

### UC-217 — Merge / link / add *(v4.3)*
- **Scenario:** New content needs offline coarsening against tips.
- **Stele solution:** **O** `merge_link_add`.
- **Requirement:** decision ∈ {merge, link, add} from Jaccard bands.

### UC-218 — Bridge discover *(v4.3)*
- **Scenario:** Seed facts need LINK-path bridges for multi-hop answers.
- **Stele solution:** **O** `bridge_discover`.
- **Requirement:** BFS path or found=false; max_depth honored.

### UC-219 — Fuse cluster *(v4.3)*
- **Scenario:** Multi-source events cluster without erasing atomic ids.
- **Stele solution:** **O** `fuse_cluster`.
- **Requirement:** Members list preserves entry ids + sources.

### UC-220 — SodaMem/MemRefine/Ariadne suite harness *(v4.3)*
- **Scenario:** CI gates density/cite + refine + merge/bridge together.
- **Stele solution:** **Harness** `sodamem_memrefine_ariadne_shaped_report`.
- **Requirement:** Proxies only.

### UC-221 — Result digest *(v4.4)*
- **Scenario:** Operator results need content-addressed digests for claim cites.
- **Stele solution:** **O** `result_digest`.
- **Requirement:** Stable SHA-256 over canonical JSON.

### UC-222 — Operator cost estimate *(v4.4)*
- **Scenario:** Oversized plans must fail closed before execute.
- **Stele solution:** **O** `operator_cost_estimate`.
- **Requirement:** admitted false when total > max_cost; narrow_hints present.

### UC-223 — Plan static verify *(v4.4)*
- **Scenario:** Planner DAGs need schema, ref, grounding, and cost checks.
- **Stele solution:** **O** `plan_static_verify`.
- **Requirement:** ungrounded literals and unknown ops violate; cost integrated.

### UC-224 — Claim verify *(v4.4)*
- **Scenario:** Final answers invent counts/entities against the trace.
- **Stele solution:** **O** `claim_verify`.
- **Requirement:** contradicted claims set blocked; truncated ≤ weakly_supported.

### UC-225 — Summary quarantine scan *(v4.4)*
- **Scenario:** Corrections must invalidate overlapping derived summaries.
- **Stele solution:** **O** `summary_quarantine_scan`.
- **Requirement:** valid-time overlap → quarantine action.

### UC-226 — Localized maintenance plan *(v4.4)*
- **Scenario:** Writes must not trigger global reorganize.
- **Stele solution:** **O** `localized_maintenance_plan`.
- **Requirement:** touch set bounded by radius/max_touch; global_reorganize false.

### UC-227 — Maintenance cost compare *(v4.4)*
- **Scenario:** Operators need a local-vs-global cost proxy.
- **Stele solution:** **O** `maintenance_cost_compare`.
- **Requirement:** prefer_local when local_cost ≤ global_cost.

### UC-228 — TGMS/MemoryData suite harness *(v4.4)*
- **Scenario:** CI gates plan/claim/quarantine + localized maint together.
- **Stele solution:** **Harness** `tgms_memdata_shaped_report`.
- **Requirement:** Proxies only.

### UC-229 — Origin bind *(v4.5)*
- **Scenario:** Authority must bind at write from channel, not content.
- **Stele solution:** **O** `origin_bind`.
- **Requirement:** untrusted_external → act_class none; user/trusted_tool → act.

### UC-230 — Propagate origin *(v4.5)*
- **Scenario:** Agent paraphrase must not raise untrusted authority.
- **Stele solution:** **O** `propagate_origin`.
- **Requirement:** derived inherits max untrust of sources.

### UC-231 — Launder scan *(v4.5)*
- **Scenario:** L-a/b/c laundering markers should surface for review.
- **Stele solution:** **O** `launder_scan`.
- **Requirement:** Marker proxies only; report-only.

### UC-232 — Act authority gate *(v4.5)*
- **Scenario:** Consequential acts need corroboration or user auth.
- **Stele solution:** **O** `act_authority_gate`.
- **Requirement:** deny untrusted-uncorroborated; ≥2 independent principals elevate.

### UC-233 — Save policy *(v4.5)*
- **Scenario:** GhostWriter injection should fail at write when possible.
- **Stele solution:** **O** `save_policy`.
- **Requirement:** reject directives; standard quarantines untrusted_external.

### UC-234 — Retrieval screen *(v4.5)*
- **Scenario:** Poison that survived save must not enter context.
- **Stele solution:** **O** `retrieval_screen`.
- **Requirement:** Blocks directive / untrusted-actionable hits.

### UC-235 — TMA-NM/AM-Sentry suite harness *(v4.5)*
- **Scenario:** CI gates origin/act + save/screen together.
- **Stele solution:** **Harness** `tmanm_amsentry_shaped_report`.
- **Requirement:** Proxies only.

### UC-236 — Build MemTree *(v4.6)*
- **Scenario:** Flat tips need a hierarchical temporal index per scope.
- **Stele solution:** **O** `build_memtree`.
- **Requirement:** root / intervals / leaves; files remain SoT.

### UC-237 — Dirty path plan *(v4.6)*
- **Scenario:** New tips must not trigger full-state rewrites.
- **Stele solution:** **O** `dirty_path_plan`.
- **Requirement:** global_rewrite false; cost ∝ dirty path.

### UC-238 — Coarse-to-fine retrieve *(v4.6)*
- **Scenario:** Queries should navigate interval summaries then leaves.
- **Stele solution:** **O** `coarse_to_fine`.
- **Requirement:** Leaves cite via_interval when scored.

### UC-239 — Build themes *(v4.6)*
- **Scenario:** Stream needs theme bootstrap for top-down retrieval.
- **Stele solution:** **O** `build_themes`.
- **Requirement:** Groups by conflict_key (or scope|layer).

### UC-240 — Theme attach *(v4.6)*
- **Scenario:** New semantics attach to a theme or create one.
- **Stele solution:** **O** `theme_attach`.
- **Requirement:** decision ∈ {attach, create_theme}.

### UC-241 — Split/merge plan *(v4.6)*
- **Scenario:** Overcrowded/tiny themes need structure repair.
- **Stele solution:** **O** `split_merge_plan`.
- **Requirement:** Report-only split/merge actions.

### UC-242 — Top-down pack *(v4.6)*
- **Scenario:** Multi-fact queries need theme packs with selective leaf expand.
- **Stele solution:** **O** `top_down_pack`.
- **Requirement:** Expand leaves only under theme uncertainty / budget.

### UC-243 — MemForest/xMemory suite harness *(v4.6)*
- **Scenario:** CI gates MemTree + theme pack together.
- **Stele solution:** **Harness** `memforest_xmemory_shaped_report`.
- **Requirement:** Proxies only.

### UC-244 — Persistence probe *(v4.7)*
- **Scenario:** Poison write success must be measurable after store.
- **Stele solution:** **O** `persistence_probe`.
- **Requirement:** persist_rate over poison ids.

### UC-245 — Execute chain probe *(v4.7)*
- **Scenario:** Recall → adopt → act must be separated (adoption bottleneck).
- **Stele solution:** **O** `execute_chain_probe`.
- **Requirement:** recalled / adopted / acted fields.

### UC-246 — Selective repair plan *(v4.7)*
- **Scenario:** Forget must remove poison without collateral benign loss.
- **Stele solution:** **O** `selective_repair_plan`.
- **Requirement:** selective_ok when no preserve id targeted.

### UC-247 — Lifecycle report *(v4.7)*
- **Scenario:** Operators need Write–Execute–Forget in one report.
- **Stele solution:** **O** `lifecycle_report`.
- **Requirement:** Bundles write/execute/forget proxies.

### UC-248 — Conflict tag *(v4.7)*
- **Scenario:** Same-key tips need supersession tags for PI.
- **Stele solution:** **O** `conflict_tag`.
- **Requirement:** Older tips superseded=true; newest current.

### UC-249 — Forget gate plan *(v4.7)*
- **Scenario:** Superseded associations should compress/evict under PI.
- **Stele solution:** **O** `forget_gate_plan`.
- **Requirement:** Report-only; keep current tip.

### UC-250 — Consolidate survivors / PI depth *(v4.7)*
- **Scenario:** Surviving tips need compact summary; depth must be visible.
- **Stele solution:** **O** `consolidate_survivors` / `pi_depth_scan`.
- **Requirement:** Anchor = newest tip; depth = active same-key count.

### UC-251 — Consensus admit *(v4.7)*
- **Scenario:** Single-channel hits should not auto-admit.
- **Stele solution:** **O** `consensus_admit`.
- **Requirement:** ≥ min_channels positive signals; marker_dirty blocks.

### UC-252 — MemSec/SleepGate/A-MemGuard suite harness *(v4.7)*
- **Scenario:** CI gates WEF + PI + consensus together.
- **Stele solution:** **Harness** `memsec_sleepgate_amemguard_shaped_report`.
- **Requirement:** Proxies only.

### UC-253 — Memory↔action graph *(v4.8)*
- **Scenario:** Repair needs typed dependencies between memories and actions.
- **Stele solution:** **O** `build_mem_action_graph`.
- **Requirement:** LINK depends-on + optional action uses_memory edges; report-only.

### UC-254 — Dependency trace *(v4.8)*
- **Scenario:** Diagnosed faults must list downstream contaminated memories.
- **Stele solution:** **O** `dependency_trace`.
- **Requirement:** Directed LINK descendants; max_depth bounded.

### UC-255 — Preserve independent support *(v4.8)*
- **Scenario:** Cascade nodes with trusted provenance must not be auto-quarantined.
- **Stele solution:** **O** `preserve_independent`.
- **Requirement:** trusted_sources match; faults never preserved as independent.

### UC-256 — Selective replay plan *(v4.8)*
- **Scenario:** After fault diagnosis, deactivate/quarantine/preserve + replay dirty actions.
- **Stele solution:** **O** `selective_replay_plan`.
- **Requirement:** Report-only; benign untouched; selective_ok when faults deactivate without collateral.

### UC-257 — Classify write channel *(v4.8)*
- **Scenario:** Writes must be typed by provenance channel (user/tool/web/agent/…).
- **Stele solution:** **O** `classify_write_channel`.
- **Requirement:** Prefix taxonomy; unknown allowed.

### UC-258 — Source isolation gate *(v4.8)*
- **Scenario:** Untrusted web must not admit like user writes.
- **Stele solution:** **O** `source_isolation_gate`.
- **Requirement:** Default deny web; quarantine tool/agent; admit user/oracle.

### UC-259 — Write channel inventory *(v4.8)*
- **Scenario:** Operators need channel counts across the store.
- **Stele solution:** **O** `write_channel_inventory`.
- **Requirement:** Counts for all known channels.

### UC-260 — Channel admit batch *(v4.8)*
- **Scenario:** Bulk candidates need the same isolation decisions.
- **Stele solution:** **O** `channel_admit_batch`.
- **Requirement:** Partition admit/quarantine/reject.

### UC-261 — DepRepair/MPBench suite harness *(v4.8)*
- **Scenario:** CI gates dependency repair + write-channel isolation together.
- **Stele solution:** **Harness** `deprepair_mpbench_shaped_report`.
- **Requirement:** Proxies only.

### UC-262 — Slot coverage *(v4.9)*
- **Scenario:** Fragments need typed semantic slots (directive/exfil/destination/trigger/authority).
- **Stele solution:** **O** `slot_coverage`.
- **Requirement:** Deterministic marker taxonomy; no LLM.

### UC-263 — Threat tier classify *(v4.9)*
- **Scenario:** Operators need MemPoison L1/L2/L3 labels per entry.
- **Stele solution:** **O** `threat_tier_classify`.
- **Requirement:** L1 explicit; L3 trigger; L2 partial slots.

### UC-264 — Dormant trigger scan *(v4.9)*
- **Scenario:** Sleeper / context-triggered payloads must be inventoryable.
- **Stele solution:** **O** `dormant_trigger_scan`.
- **Requirement:** Report-only L3 list.

### UC-265 — Compositional coalition scan *(v4.9)*
- **Scenario:** Individually benign fragments may jointly complete a critical combo.
- **Stele solution:** **O** `compositional_coalition_scan`.
- **Requirement:** Skip L1 singles; flag critical unions.

### UC-266 — Collusion risk gate *(v4.9)*
- **Scenario:** Retrieval packs must deny critical salami coalitions.
- **Stele solution:** **O** `collusion_risk_gate`.
- **Requirement:** deny|review|admit over SEARCH hits.

### UC-267 — MemPoison ladder report *(v4.9)*
- **Scenario:** Store-wide L1/L2/L3 inventory for operators.
- **Stele solution:** **O** `mempoison_ladder_report`.
- **Requirement:** Counts + sample rows.

### UC-268 — Salami pair probe *(v4.9)*
- **Scenario:** Two fragments need a collusion verdict.
- **Stele solution:** **O** `salami_pair_probe`.
- **Requirement:** collusive when critical union and neither is L1.

### UC-269 — MemPoison/Salami suite harness *(v4.9)*
- **Scenario:** CI gates L1–L3 + collusion together.
- **Stele solution:** **Harness** `mempoison_salami_shaped_report`.
- **Requirement:** Proxies only.

### UC-270 — Classify persistence layer *(v5.0)*
- **Scenario:** Knowledge must not age-fade like experiential memory.
- **Stele solution:** **O** `classify_persistence_layer`.
- **Requirement:** knowledge|memory|wisdom|intelligence with decay/supersede flags.

### UC-271 — Persistence policy *(v5.0)*
- **Scenario:** Operators need a policy card per layer.
- **Stele solution:** **O** `persistence_policy`.
- **Requirement:** Documented decay/update/ttl semantics.

### UC-272 — Layer inventory *(v5.0)*
- **Scenario:** Store-wide persistence-layer counts.
- **Stele solution:** **O** `layer_inventory`.
- **Requirement:** Counts for all four layers.

### UC-273 — Knowledge protect scan *(v5.0)*
- **Scenario:** Knowledge entries must not appear in fade sets.
- **Stele solution:** **O** `knowledge_protect_scan`.
- **Requirement:** Report violations only.

### UC-274 — Intelligence reject gate *(v5.0)*
- **Scenario:** Ephemeral inference must not enter SoT.
- **Stele solution:** **O** `intelligence_reject_gate`.
- **Requirement:** reject when classified intelligence.

### UC-275 — Credential scan *(v5.0)*
- **Scenario:** Detect API keys / PEM / JWT / cloud tokens in entries.
- **Stele solution:** **O** `credential_scan`.
- **Requirement:** Pattern hits; no LLM.

### UC-276 — Credential reject gate *(v5.0)*
- **Scenario:** Credentials must never become persistent memory.
- **Stele solution:** **O** `credential_reject_gate`.
- **Requirement:** reject on any credential hit.

### UC-277 — Credential store scan *(v5.0)*
- **Scenario:** Hygiene inventory of leaked credentials still in store.
- **Stele solution:** **O** `credential_store_scan`.
- **Requirement:** Report-only suspects list.

### UC-278 — Uncertainty score *(v5.0)*
- **Scenario:** Always-on retrieval pollutes context; need uncertainty.
- **Stele solution:** **O** `uncertainty_score`.
- **Requirement:** [0,1] from hit coverage/overlap.

### UC-279 — Uncertainty retrieve gate *(v5.0)*
- **Scenario:** Retrieve only when uncertainty is high.
- **Stele solution:** **O** `uncertainty_retrieve_gate`.
- **Requirement:** retrieve|skip decisions.

### UC-280 — Reasoning reserve plan *(v5.0)*
- **Scenario:** Adaptive budget split between reasoning and recall.
- **Stele solution:** **O** `reasoning_reserve_plan`.
- **Requirement:** High confidence → larger reasoning fraction.

### UC-281 — Knowledge/cred/uncertainty suite harness *(v5.0)*
- **Scenario:** CI gates persistence layers + credentials + uncertainty together.
- **Stele solution:** **Harness** `knowledgelayer_cred_uncertainty_shaped_report`.
- **Requirement:** Proxies only.

### UC-282 — Classify memory component *(v5.1)*
- **Scenario:** Portable memory needs E/S/P/W/I typing.
- **Stele solution:** **O** `classify_memory_component`.
- **Requirement:** Map content layer → PAM component.

### UC-283 — Build Merkle DAG *(v5.1)*
- **Scenario:** Transfer packs need tamper-evident provenance roots.
- **Stele solution:** **O** `build_merkle_dag`.
- **Requirement:** SHA-256 digests + LINK parents; unkeyed (C5).

### UC-284 — Verify Merkle root *(v5.1)*
- **Scenario:** Importers must detect DAG tampering.
- **Stele solution:** **O** `verify_merkle_root`.
- **Requirement:** match|mismatch against expected root.

### UC-285 — Issue capability token *(v5.1)*
- **Scenario:** Multi-agent handoffs need scoped ops without full store export.
- **Stele solution:** **O** `issue_capability_token`.
- **Requirement:** Unkeyed digest token; ops ⊆ {read,write,derive,redact,export,rehydrate}.

### UC-286 — Check capability *(v5.1)*
- **Scenario:** Callers must enforce token scope before ops.
- **Stele solution:** **O** `check_capability`.
- **Requirement:** Fail closed on mismatch/expiry/op/entry.

### UC-287 — Selective disclose *(v5.1)*
- **Scenario:** Export a subset with optional ancestor closure.
- **Stele solution:** **O** `selective_disclose`.
- **Requirement:** Include LINK parents when requested; return subset root.

### UC-288 — Rehydrate safe plan *(v5.1)*
- **Scenario:** Rehydration must resist memory-mediated injection.
- **Stele solution:** **O** `rehydrate_safe_plan`.
- **Requirement:** Report-only strip/admit plan.

### UC-289 — Issue action capability *(v5.1)*
- **Scenario:** Agents must not hold bearer secrets — only action handles.
- **Stele solution:** **O** `issue_action_capability`.
- **Requirement:** Non-exportable; intent cannot contain credentials.

### UC-290 — Capability export probe *(v5.1)*
- **Scenario:** Handles must never export as secrets.
- **Stele solution:** **O** `capability_export_probe`.
- **Requirement:** Always `export_allowed=false`.

### UC-291 — Check action capability *(v5.1)*
- **Scenario:** Mediated invocations need session/method/host/quota checks.
- **Stele solution:** **O** `check_action_capability`.
- **Requirement:** Fail closed on mismatch/quota/expiry.

### UC-292 — Action capability inventory *(v5.1)*
- **Scenario:** Operators need a summary of issued handles.
- **Stele solution:** **O** `action_capability_inventory`.
- **Requirement:** No secret material in rows.

### UC-293 — PAM/CapSeal suite harness *(v5.1)*
- **Scenario:** CI gates PAM + CapSeal together.
- **Stele solution:** **Harness** `pam_capseal_shaped_report`.
- **Requirement:** Proxies only.

---

## 6. Functional requirements (by plane)

| Plane | Requirement | Source |
|---|---|---|
| **K — Schema** | Content layers (goal/issue/decision/failure-lesson/workflow/skill) incl. rejected options; bi-temporal fields; three-rung scope; provenance (+ optional `model_id`); env assumptions on workflow/skill; optional `assessment.domain_depth` + `usage`; incomplete entries rejected at ADD; distill gate on body shape | C6; C8; OP-1, FF-2, FF-7, FF-8, FF-9 |
| **T — Six ops + helpers** | `ADD · UPDATE · DELETE/SUPERSEDE · SEARCH · REFLECT · LINK` as library + MCP; `promote` / `resolve_contested` as governed helpers; `project_receipt` / `migration_entry` / `judgment_entry` producers | C1; C8; OP-3 |
| **G — Quarantine** | Writes quarantined; promotion only with external-oracle evidence; writer cannot self-promote; self-issued evidence rejected; code-fix needs test_result | C7; C8; OP-2, OP-4 |
| **G — REFLECT** | Batched consolidation; contested on contradiction; dangling LINK report; no auto-resolve | C7; OP-3; R2 |
| **R — Retrieval** | Hybrid keyword + optional semantic + temporal; promoted-only; scope/domain/env/model/stale filters; budgeted slices; match_reasons; body compress; follow_links depth; prefer_helpful/pin ranking; ∅ valid | C2; OP-9, FF-4, FF-5, FF-8 |
| **X — Export/hydrate** | Redact-at-export; stamps; audience tiers; adaptation operators; subject allowlist; verify_pack; hydrate + transfer eval harness | C3; OP-6, OP-12, FF-9, FF-10, FF-13 |
| **L — Living ledger** | record_outcome; pin; stale_report; reverify | FF-8; OP-11 |
| **O — Ops** | verify store; stats; timeline; attach; reviewer_corrections; doctor; snapshot; CLI | C4; C8; UC-28–32 |
| **Interop** | entry JSON Schema; memorywire remember/recall projection helpers | OP-6; P16 |
| **Cross-cutting** | Inspectable file SoT; indexes derived + rebuildable; zero LLM/network on write path; no third-party product or DB-driver imports | C4, C5, C1; OP-5, FF-11 |

**Context-operator coverage** (intent §architecture; OP-9): **Write** = six ops · **Select** = retrieval · **Compress** = budgeted injection + body_max_chars + REFLECT · **Isolate** = scope/namespace; cross-scope reads explicit.

**Priority on conflict** (intent §constraint_satisfiability): **C7 > C8 > C6 > C5 > C4 > C2 > C3 > C1**.

---

## 7. Non-goals (out of scope)

- **Not training-time memory.** No fine-tuning, no LoRA, no weight updates.
- **Not a database engine.** Substrate stays boring and swappable; protocol is the product.
- **Not an extraction pipeline.** Writers distill; Stele governs. No LLM extraction on the core write path (intent R4).
- **Not a retrieval router.** Whether/how to retrieve is the caller's (or a retrieval router's) decision.
- **Not a replacement for intent tools, retrieval routers, or evidence oracles.** Protocol composition only.
- **Not generic document RAG.** Ledger is written *during* the work, *by* the worker.
- **Not a conversation-health monitor.** That is out of scope for Stele (OP-8).
- **Not pack SKU / pricing / WTP claims.** Capability and scoped lift only (OP-12).
- **Not bulk import of private receipt inventories.** Selected, redacted projection only (C8).

### 7.1 When Stele is not the right choice

- **Chat personalization at scale** — Mem0-class extract-and-retrieve is simpler.
- **Entity-centric world state at millions of facts** — temporal KG (Zep/Graphiti) fits better.
- **Thread-scoped scratchpads** — framework checkpoints (e.g. LangGraph); Stele is long-term memory.

---

## 8. Success metrics

From `stele_system_intent.yaml` §success_oracle and constraints, made measurable by UC-12 (+ v1 harnesses):

- **Outcome value:** agents on lesson-dependent tasks perform measurably better with Stele retrieval than without (`compare_with_without`, `memory_arena_smoke`, env-gate suite, foreign-pack lift).
- **Governance integrity:** zero self-graded entries in the promoted tier; writer cannot promote own claim; journal is the audit trail.
- **Temporal safety:** zero expired/superseded entries served unflagged; stale flag or withhold honored.
- **Erasure:** subject-keyed delete + index rebuild leaves zero traces.
- **Purity:** core write path issues zero LLM/network calls; core imports no ecosystem/DB code.
- **Portability:** SoT exports to inspectable files; index rebuild reproduces retrieval results; packs verify clean.
- **Cost:** retrieval stays within budget; `measure_search_overhead` reports median ms (accepted trade while measured).
- **Explainability:** slices carry `match_reasons`; timelines exist per entry.
- **Adoptability:** clone → install → quickstart / `proof_run.py` with no cloud account on the default path.
- **Joint satisfaction:** one lifecycle test asserts C1–C8 on the same store state (intent joint test). No implementation phase is complete while it is red.

---

## 9. Open questions (resolved — kept for history)

> **Status:** all six resolved in [`TECH_SPEC.md`](TECH_SPEC.md) §1. Implementation follows those resolutions through v1.0.

1. **Substrate for v1 SoT:** plain files + journal + advisory lock (C4; concurrency via lock).
2. **Oracle evidence format:** typed records (`test_result | env_feedback | independent_judge | human_signoff`) with issuer ≠ writer.
3. **MCP surface shape:** named tools (not a single `op` parameter).
4. **Scope taxonomy:** three rungs `universal | domain:<name> | project:<name>`.
5. **REFLECT conflict semantics:** surface contested + evidenced `resolve_contested` (no auto-merge).
6. **Seed migration:** `migration_entry` + `project_receipt` + `judgment_entry` — selected/redacted only.

---

## 10. References

- `stele_system_intent.yaml` — constraints C1–C8, architecture, ecosystem linkage, failure-mode coverage
- `docs/TECH_SPEC.md` — schema, governance, retrieval, MCP, export
- `docs/patterns/patterns_session_ledger_memory.yaml` — FF-1..13, OP-1..12
- `docs/research/AGENT_SESSION_LEDGER_INFERENCE_TIME_MEMORY_RESEARCH_2026.md`
- `docs/research/AGENT_MEMORY_STORAGE_SYSTEMS_RESEARCH_2026.md`
- `docs/research/GOVERNED_EXPERIENTIAL_MEMORY_FRONTIERS_2026.md`
- `docs/schemas/entry.schema.json` · `docs/ARCHITECTURE.md`
- `CHANGELOG.md` / `ROADMAP.md` — v1.0 ship
- 
---

## 11. Capability map (PRD ↔ v18.15.0)

| UC | Shipped surface (indicative) | Since |
|---|---|---|
| UC-1..12 | Core lifecycle + export + harness | 0.1.0–0.1.2 |
| UC-13 | `list_contested` / `resolve_contested` | 0.1.2 |
| UC-14 | `consumer_env` + env-gate harness | 0.1.1–0.1.2 |
| UC-15 | `stale_policy` / `stale_report` | 0.1.3 / 0.1.6 |
| UC-16 | `consumer_model_id` / `reverify` | 0.1.4 / 0.1.6 |
| UC-17 | `hydrate` / `foreign_pack_transfer_eval` | 0.1.3 |
| UC-18..19 | `record_outcome` / `pin` | 0.1.6 |
| UC-20 | `match_reasons` / `body_max_chars` | 0.1.6 |
| UC-21 | `verify` / `stale_report` / `reverify` | 0.1.3–0.1.6 |
| UC-22 | `follow_links` / `follow_link_depth` / `related` | 0.1.4 / 0.1.7 |
| UC-23 | `reviewer_corrections` | 0.1.3 |
| UC-24 | `stats` / `timeline` / `attach` / `verify_pack` | 0.1.7 |
| UC-25..26 | `project_receipt` / `judgment_entry` | 0.1.1 / 0.1.5 |
| UC-27 | `stele-mcp` (2003 named tools) | 0.1.0 → 18.15.0 |
| UC-28 | `stele` CLI | 1.0.0 |
| UC-29 | `entry_json_schema` / `docs/schemas/entry.schema.json` | 1.0.0 |
| UC-30 | `snapshot` | 1.0.0 |
| UC-31 | `to_memorywire_remember` / `from_memorywire_recall_hits` | 1.0.0 |
| UC-32 | `doctor` | 1.0.0 |
| UC-33 | `purge_by_provenance` | 1.1.0 |
| UC-34 | `add_batch` | 1.1.0 |
| UC-35 | `diff_stores` | 1.1.0 |
| UC-36 | `search(..., trusted_sources=)` | 1.1.0 |
| UC-37 | `membench_shaped_report` | 1.1.0 |
| UC-38 | `entangled_suspects` | 1.2.0 |
| UC-39 | `hygiene_candidates` | 1.2.0 |
| UC-40 | `governance_shaped_report` + `prefer_fresh` | 1.2.0 |
| UC-41 | `search(..., principal_scopes=)` | 1.3.0 |
| UC-42 | `forget_compliance` | 1.3.0 |
| UC-43 | `gatemem_shaped_report` | 1.3.0 |
| UC-44 | `lineage` | 1.4.0 |
| UC-45 | `belief_at` | 1.4.0 |
| UC-46 | `conflict_surface` | 1.4.0 |
| UC-47 | `memoryagent_shaped_report` | 1.4.0 |
| UC-48 | `injection_scan` | 1.5.0 |
| UC-49 | `withhold_injection_suspects` / `block_injection_suspects` | 1.5.0 |
| UC-50 | `select_budget_plan` + `maple_shaped_report` | 1.5.0 |
| UC-51 | `store_seal` / `verify_seal` | 1.6.0 |
| UC-52 | `attribution_receipt` | 1.6.0 |
| UC-53 | `replay_consistency` | 1.6.0 |
| UC-54 | `memmark_shaped_report` | 1.6.0 |
| UC-55 | `lifecycle_inventory` + `lifecycle_tiers` Select | 1.7.0 |
| UC-56 | `revoke_by_key` / `unrevoke` | 1.7.0 |
| UC-57 | `pack_seal` / `verify_pack_seal` | 1.7.0 |
| UC-58 | `search_explain` | 1.7.0 |
| UC-59 | `tepa_amvl_shaped_report` | 1.7.0 |
| UC-60 | `blast_radius` | 1.8.0 |
| UC-61 | `merge_classify` | 1.8.0 |
| UC-62 | `path_trust` + `min_path_trust` | 1.8.0 |
| UC-63 | `meld_map_shaped_report` | 1.8.0 |
| UC-64 | `stele_core.graph` module | 1.8.0 |
| UC-65 | `verify_journal_chain` / `journal_chain_head` | 1.9.0 |
| UC-66 | `spread_activate` | 1.9.0 |
| UC-67 | `connection_density` / `prefer_dense` | 1.9.0 |
| UC-68 | `retention_score` / `min_retention` | 1.9.0 |
| UC-69 | `soda_synapse_shaped_report` | 1.9.0 |
| UC-70 | `health_report` | 2.0.0 |
| UC-71 | `release_gate` / `require_release` export | 2.0.0 |
| UC-72 | `cue_tags` Select filter | 2.0.0 |
| UC-73 | `rebuild_sqlite_index` / `search_sqlite` | 2.0.0 |
| UC-74 | `gpm_release_shaped_report` | 2.0.0 |
| UC-75 | decision receipts / `issue_receipt` | 2.1.0 |
| UC-76 | `verify_import` / `require_verify` hydrate | 2.1.0 |
| UC-77 | export `policy_digest` | 2.1.0 |
| UC-78 | `lineage_trust` / `refuse_untrusted_lineage` | 2.1.0 |
| UC-79 | `pam_cava_shaped_report` | 2.1.0 |
| UC-80 | `record_execution` / execution chain | 2.2.0 |
| UC-81 | `verify_execution` | 2.2.0 |
| UC-82 | `authority_gate` | 2.2.0 |
| UC-83 | `claim_closure` | 2.2.0 |
| UC-84 | `poem_ppmf_shaped_report` | 2.2.0 |
| UC-85 | `cascade_impact` / `cascade_exposure` | 2.3.0 |
| UC-86 | `withdraw_cascade` | 2.3.0 |
| UC-87 | `repair_plan` | 2.3.0 |
| UC-88 | `non_revival_probe` | 2.3.0 |
| UC-89 | `memorepair_shaped_report` | 2.3.0 |
| UC-90 | `memory_role` schema | 2.4.0 |
| UC-91 | `fact_interface` / `role_collapse_scan` | 2.4.0 |
| UC-92 | `claims_only` / `require_claim_role` | 2.4.0 |
| UC-93 | `dual_channel_search` / `quality_gate` | 2.4.0 |
| UC-94 | `memir_dmem_shaped_report` | 2.4.0 |
| UC-95 | `commit_view` | 2.5.0 |
| UC-96 | `checkout_view` | 2.5.0 |
| UC-97 | `diff_commits` / `merge_branches` | 2.5.0 |
| UC-98 | `copyability_gate` | 2.5.0 |
| UC-99 | `gitofthoughts_shaped_report` | 2.5.0 |
| UC-100 | `pin_memory_version` | 2.6.0 |
| UC-101 | `activate_version` / `active_version` | 2.6.0 |
| UC-102 | `counterfactual_search` | 2.6.0 |
| UC-103 | `exclude_superseded` / `stale_fact_scan` | 2.6.0 |
| UC-104 | `chronomem_strata_shaped_report` | 2.6.0 |
| UC-105 | `propose_update` | 2.7.0 |
| UC-106 | `apply_update` | 2.7.0 |
| UC-107 | `ledger_view` | 2.7.0 |
| UC-108 | `memory_worth` / `min_worth` / `low_worth_scan` | 2.7.0 |
| UC-109 | `tarl_mw_shaped_report` | 2.7.0 |
| UC-110 | `begin_transaction` / `stage_write` / `commit_transaction` / `abort_transaction` | 2.8.0 |
| UC-111 | `action_safe_gate` | 2.8.0 |
| UC-112 | `in_flight_report` | 2.8.0 |
| UC-113 | `aoep_report` | 2.8.0 |
| UC-114 | `memtx_aoep_shaped_report` | 2.8.0 |
| UC-115 | `symbolic_conflict_scan` | 2.9.0 |
| UC-116 | `classify_conflict` | 2.9.0 |
| UC-117 | `compact_render` | 2.9.0 |
| UC-118 | `stage_effect` / `release_effects` / effect lifecycle | 2.9.0 |
| UC-119 | `lattice_cordon_shaped_report` | 2.9.0 |
| UC-120 | `state_resolution` | 3.0.0 |
| UC-121 | `premise_resistance` | 3.0.0 |
| UC-122 | `ipa_gap_scan` / `related_slot_scan` | 3.0.0 |
| UC-123 | `verify_transition` / `gem_report` | 3.0.0 |
| UC-124 | `stale_gem_shaped_report` | 3.0.0 |
| UC-125 | `project_resolve` / `pin_projection` | 3.1.0 |
| UC-126 | `correction_handle` | 3.1.0 |
| UC-127 | `toki_classify_operator` | 3.1.0 |
| UC-128 | `toki_anomaly_scan` / `context_bid` | 3.1.0 |
| UC-129 | `statefuse_toki_shaped_report` | 3.1.0 |
| UC-130 | `repair_select_mincut` | 3.2.0 |
| UC-131 | `adjudicate_update` | 3.2.0 |
| UC-132 | `unknown_current_slots` / `authorize_retrieval` | 3.2.0 |
| UC-133 | `admit_gate` / `list_admit_receipts` | 3.2.0 |
| UC-134 | `memorepair_cupmem_cmgl_shaped_report` | 3.2.0 |
| UC-135 | `put_raw_page` / `sufficiency_gate` | 3.3.0 |
| UC-136 | `escalate_raw` / `verified_writeback` | 3.3.0 |
| UC-137 | `skill_eligibility` / `crystallize_skill` | 3.3.0 |
| UC-138 | `value_backfill` / `skill_catalog` | 3.3.0 |
| UC-139 | `tiermem_msce_shaped_report` | 3.3.0 |
| UC-140 | `fade_strength` | 3.4.0 |
| UC-141 | `fade_scan` / `fusion_candidates` | 3.4.0 |
| UC-142 | `weibull_relevance` / `min_weibull` | 3.4.0 |
| UC-143 | `evidence_gap` | 3.4.0 |
| UC-144 | `reflective_retrieve` / `gap_tracker_update` | 3.4.0 |
| UC-145 | `fademem_memr3_shaped_report` | 3.4.0 |
| UC-146 | `archive_plan` | 3.5.0 |
| UC-147 | `archive_apply` / `unarchive` / `list_archived` | 3.5.0 |
| UC-148 | `composite_importance` / `cis_scan` | 3.5.0 |
| UC-149 | `control_suggest` | 3.5.0 |
| UC-150 | `archive_sfams_memcon_shaped_report` | 3.5.0 |
| UC-151 | state `archived` | 3.5.0 |
| UC-152 | `value_tag` / `wm_*` | 3.6.0 |
| UC-153 | `sleep_trigger` / `sleep_plan` / `sleep_apply_nrem` | 3.6.0 |
| UC-154 | `episodic_buffer` | 3.6.0 |
| UC-155 | `semantic_boundary` / `consolidate_plan` | 3.6.0 |
| UC-156 | `anticipate` | 3.6.0 |
| UC-157 | `verify_compaction` | 3.6.0 |
| UC-158 | `scm_gam_acm_shaped_report` | 3.6.0 |
| UC-159 | `sensory_filter` | 3.7.0 |
| UC-160 | `stage_inventory` / `topic_segments` / `stage_budget_plan` | 3.7.0 |
| UC-161 | `ppr_scores` / `multi_hop_retrieve` | 3.7.0 |
| UC-162 | `write_gate` | 3.7.0 |
| UC-163 | `action_risk_gate` | 3.7.0 |
| UC-164 | `lightmem_hippo_quipu_shaped_report` | 3.7.0 |
| UC-165 | stage budget efficiency | 3.7.0 |
| UC-166 | `extract_residuals` / `residual_augment` | 3.8.0 |
| UC-167 | `register_entities` / `profile_expand` | 3.8.0 |
| UC-168 | `match_correction` | 3.8.0 |
| UC-169 | `insight_inject` | 3.8.0 |
| UC-170 | `cascade_route` | 3.8.0 |
| UC-171 | `multi_channel_fuse` | 3.8.0 |
| UC-172 | `prograph_emg_agentir_shaped_report` | 3.8.0 |
| UC-173 | residual-augmented reader context | 3.8.0 |
| UC-174 | `dual_project` | 3.9.0 |
| UC-175 | `governance_route` | 3.9.0 |
| UC-176 | `session_delta_*` | 3.9.0 |
| UC-177 | `entity_context` | 3.9.0 |
| UC-178 | `entity_leak_probe` | 3.9.0 |
| UC-179 | `hymem_classify_slot` | 3.9.0 |
| UC-180 | `hymem_isolate_pack` | 3.9.0 |
| UC-181 | `govmem_hymem_shaped_report` | 3.9.0 |
| UC-182 | progressive token efficiency | 3.9.0 |
| UC-183 | `extract_version_markers` | 4.0.0 |
| UC-184 | `freshness_resolve` | 4.0.0 |
| UC-185 | `assemble_current` | 4.0.0 |
| UC-186 | `hop_freshness` | 4.0.0 |
| UC-187 | `patch_test` | 4.0.0 |
| UC-188 | `temporal_resolve` / `recover_active_map` | 4.0.0 |
| UC-189 | `fleet_scope_gate` | 4.0.0 |
| UC-190 | `propagate_plan` / `stale_propagation_scan` | 4.0.0 |
| UC-191 | `freshness_memtxn_fleet_shaped_report` | 4.0.0 |
| UC-192 | stale promoted tip detection | 4.0.0 |
| UC-193 | `query_complexity` | 4.1.0 |
| UC-194 | `budget_tier_route` | 4.1.0 |
| UC-195 | `budget_module_plan` | 4.1.0 |
| UC-196 | `skill_rank` | 4.1.0 |
| UC-197 | `skill_prereq_expand` | 4.1.0 |
| UC-198 | retrieval primitives/skills compose | 4.1.0 |
| UC-199 | `route_retrieval_skill` / `run_retrieval_skill` | 4.1.0 |
| UC-200 | `budgetmem_erskill_shaped_report` | 4.1.0 |
| UC-201 | hard-query budget escalation | 4.1.0 |
| UC-202 | skill-first retrieval path | 4.1.0 |
| UC-203 | `support_score` | 4.2.0 |
| UC-204 | `consistency_admit` | 4.2.0 |
| UC-205 | `retrieval_admit` | 4.2.0 |
| UC-206 | `task_conditioned_pack` | 4.2.0 |
| UC-207 | `sovereignty_checklist` | 4.2.0 |
| UC-208 | `post_delete_verify` | 4.2.0 |
| UC-209 | `rollback_plan` | 4.2.0 |
| UC-210 | `consistency_memgate_sovereignty_shaped_report` | 4.2.0 |
| UC-211 | poison reject at write gate | 4.2.0 |
| UC-212 | `density_fuse` | 4.3.0 |
| UC-213 | `evidence_plan` | 4.3.0 |
| UC-214 | `cited_pack` | 4.3.0 |
| UC-215 | `compress_candidates` | 4.3.0 |
| UC-216 | `refine_plan` | 4.3.0 |
| UC-217 | `merge_link_add` | 4.3.0 |
| UC-218 | `bridge_discover` | 4.3.0 |
| UC-219 | `fuse_cluster` | 4.3.0 |
| UC-220 | `sodamem_memrefine_ariadne_shaped_report` | 4.3.0 |
| UC-221 | `result_digest` | 4.4.0 |
| UC-222 | `operator_cost_estimate` | 4.4.0 |
| UC-223 | `plan_static_verify` | 4.4.0 |
| UC-224 | `claim_verify` | 4.4.0 |
| UC-225 | `summary_quarantine_scan` | 4.4.0 |
| UC-226 | `localized_maintenance_plan` | 4.4.0 |
| UC-227 | `maintenance_cost_compare` | 4.4.0 |
| UC-228 | `tgms_memdata_shaped_report` | 4.4.0 |
| UC-229 | `origin_bind` | 4.5.0 |
| UC-230 | `propagate_origin` | 4.5.0 |
| UC-231 | `launder_scan` | 4.5.0 |
| UC-232 | `act_authority_gate` | 4.5.0 |
| UC-233 | `save_policy` | 4.5.0 |
| UC-234 | `retrieval_screen` | 4.5.0 |
| UC-235 | `tmanm_amsentry_shaped_report` | 4.5.0 |
| UC-236 | `build_memtree` | 4.6.0 |
| UC-237 | `dirty_path_plan` | 4.6.0 |
| UC-238 | `coarse_to_fine` | 4.6.0 |
| UC-239 | `build_themes` | 4.6.0 |
| UC-240 | `theme_attach` | 4.6.0 |
| UC-241 | `split_merge_plan` | 4.6.0 |
| UC-242 | `top_down_pack` | 4.6.0 |
| UC-243 | `memforest_xmemory_shaped_report` | 4.6.0 |
| UC-244 | `persistence_probe` | 4.7.0 |
| UC-245 | `execute_chain_probe` | 4.7.0 |
| UC-246 | `selective_repair_plan` | 4.7.0 |
| UC-247 | `lifecycle_report` | 4.7.0 |
| UC-248 | `conflict_tag` | 4.7.0 |
| UC-249 | `forget_gate_plan` | 4.7.0 |
| UC-250 | `consolidate_survivors` / `pi_depth_scan` | 4.7.0 |
| UC-251 | `consensus_admit` | 4.7.0 |
| UC-252 | `memsec_sleepgate_amemguard_shaped_report` | 4.7.0 |
| UC-253 | `build_mem_action_graph` | 4.8.0 |
| UC-254 | `dependency_trace` | 4.8.0 |
| UC-255 | `preserve_independent` | 4.8.0 |
| UC-256 | `selective_replay_plan` | 4.8.0 |
| UC-257 | `classify_write_channel` | 4.8.0 |
| UC-258 | `source_isolation_gate` | 4.8.0 |
| UC-259 | `write_channel_inventory` | 4.8.0 |
| UC-260 | `channel_admit_batch` | 4.8.0 |
| UC-261 | `deprepair_mpbench_shaped_report` | 4.8.0 |
| UC-262 | `slot_coverage` | 4.9.0 |
| UC-263 | `threat_tier_classify` | 4.9.0 |
| UC-264 | `dormant_trigger_scan` | 4.9.0 |
| UC-265 | `compositional_coalition_scan` | 4.9.0 |
| UC-266 | `collusion_risk_gate` | 4.9.0 |
| UC-267 | `mempoison_ladder_report` | 4.9.0 |
| UC-268 | `salami_pair_probe` | 4.9.0 |
| UC-269 | `mempoison_salami_shaped_report` | 4.9.0 |
| UC-270 | `classify_persistence_layer` | 5.0.0 |
| UC-271 | `persistence_policy` | 5.0.0 |
| UC-272 | `layer_inventory` | 5.0.0 |
| UC-273 | `knowledge_protect_scan` | 5.0.0 |
| UC-274 | `intelligence_reject_gate` | 5.0.0 |
| UC-275 | `credential_scan` | 5.0.0 |
| UC-276 | `credential_reject_gate` | 5.0.0 |
| UC-277 | `credential_store_scan` | 5.0.0 |
| UC-278 | `uncertainty_score` | 5.0.0 |
| UC-279 | `uncertainty_retrieve_gate` | 5.0.0 |
| UC-280 | `reasoning_reserve_plan` | 5.0.0 |
| UC-281 | `knowledgelayer_cred_uncertainty_shaped_report` | 5.0.0 |
| UC-282 | `classify_memory_component` | 5.1.0 |
| UC-283 | `build_merkle_dag` | 5.1.0 |
| UC-284 | `verify_merkle_root` | 5.1.0 |
| UC-285 | `issue_capability_token` | 5.1.0 |
| UC-286 | `check_capability` | 5.1.0 |
| UC-287 | `selective_disclose` | 5.1.0 |
| UC-288 | `rehydrate_safe_plan` | 5.1.0 |
| UC-289 | `issue_action_capability` | 5.1.0 |
| UC-290 | `capability_export_probe` | 5.1.0 |
| UC-291 | `check_action_capability` | 5.1.0 |
| UC-292 | `action_capability_inventory` | 5.1.0 |
| UC-293 | `pam_capseal_shaped_report` | 5.1.0 |
| UC-294 | `classify_risk_source` | 5.2.0 |
| UC-295 | `classify_failure_mode` | 5.2.0 |
| UC-296 | `classify_real_world_harm` | 5.2.0 |
| UC-297 | `diagnose_trajectory_step` | 5.2.0 |
| UC-298 | `diagnose_trajectory` | 5.2.0 |
| UC-299 | `safe_but_unreasonable_scan` | 5.2.0 |
| UC-300 | `taxonomy_inventory` | 5.2.0 |
| UC-301 | `weave_layer_assign` | 5.2.0 |
| UC-302 | `build_hybrid_weave` | 5.2.0 |
| UC-303 | `dual_channel_retrieve` | 5.2.0 |
| UC-304 | `experience_abstract_plan` | 5.2.0 |
| UC-305 | `temporal_session_conflict_scan` | 5.2.0 |
| UC-306 | `multi_hop_depth_score` / `agentdog_memweaver_shaped_report` | 5.2.0 |
| UC-307 | `list_design_space` | 5.3.0 |
| UC-308 | `architecture_profile` | 5.3.0 |
| UC-309 | `diagnose_architecture` | 5.3.0 |
| UC-310 | `propose_architecture_variants` | 5.3.0 |
| UC-311 | `rank_architecture_fitness` | 5.3.0 |
| UC-312 | `select_architecture_parents` | 5.3.0 |
| UC-313 | `ept_classify` | 5.3.0 |
| UC-314 | `functional_role_assign` | 5.3.0 |
| UC-315 | `contamination_scan` | 5.3.0 |
| UC-316 | `type_route_retrieve` | 5.3.0 |
| UC-317 | `dreaming_consolidate_plan` | 5.3.0 |
| UC-318 | `feedback_revise_plan` | 5.3.0 |
| UC-319 | `skill_evolve_plan` / `memevolve_mindmemos_shaped_report` | 5.3.0 |
| UC-320 | `extract_preference_signal` | 5.4.0 |
| UC-321 | `fuse_preference` | 5.4.0 |
| UC-322 | `preference_change_detect` | 5.4.0 |
| UC-323 | `preference_update_plan` | 5.4.0 |
| UC-324 | `format_preference_prompt` | 5.4.0 |
| UC-325 | `beam_category_inventory` | 5.4.0 |
| UC-326 | `classify_beam_query` | 5.4.0 |
| UC-327 | `knowledge_update_check` | 5.4.0 |
| UC-328 | `abstention_gate` | 5.4.0 |
| UC-329 | `contradiction_resolve_plan` | 5.4.0 |
| UC-330 | `event_order_check` | 5.4.0 |
| UC-331 | `localize_hallucination_stage` | 5.4.0 |
| UC-332 | `beam_eval_pack` / `pamu_beam_shaped_report` | 5.4.0 |
| UC-333 | `extract_episodic_gist` | 5.5.0 |
| UC-334 | `extract_temporal_facts` | 5.5.0 |
| UC-335 | `situational_bind` | 5.5.0 |
| UC-336 | `build_hybrid_episodic_graph` | 5.5.0 |
| UC-337 | `agentic_retrieve_plan` | 5.5.0 |
| UC-338 | `ordinal_event_query` | 5.5.0 |
| UC-339 | `form_memcell` | 5.5.0 |
| UC-340 | `consolidate_memscenes` | 5.5.0 |
| UC-341 | `foresight_filter` | 5.5.0 |
| UC-342 | `reconstructive_recollect` | 5.5.0 |
| UC-343 | `profile_evolve_plan` | 5.5.0 |
| UC-344 | `necessity_sufficiency_check` / `remem_evermemos_shaped_report` | 5.5.0 |
| UC-345 | `classify_memory_tier` | 5.6.0 |
| UC-346 | `heat_score` | 5.6.0 |
| UC-347 | `segment_pages` | 5.6.0 |
| UC-348 | `stm_to_mtm_plan` | 5.6.0 |
| UC-349 | `mtm_evict_plan` | 5.6.0 |
| UC-350 | `promote_to_lpm_plan` | 5.6.0 |
| UC-351 | `hierarchical_retrieve` | 5.6.0 |
| UC-352 | `integrate_episodic_narrative` | 5.6.0 |
| UC-353 | `anticipatory_schema` | 5.6.0 |
| UC-354 | `prediction_error_distill` | 5.6.0 |
| UC-355 | `deserves_memory_gate` | 5.6.0 |
| UC-356 | `distill_batch_plan` / `memoryos_nemori_shaped_report` | 5.6.0 |
| UC-357 | `classify_network` / `retain_plan` / `network_inventory` | 5.7.0 |
| UC-358 | `recall_multi_strategy` | 5.7.0 |
| UC-359 | `opinion_reinforce` | 5.7.0 |
| UC-360 | `reflect_plan` | 5.7.0 |
| UC-361 | `distill_strategy_item` | 5.7.0 |
| UC-362 | `failure_lesson_gate` | 5.7.0 |
| UC-363 | `retrieve_strategies` | 5.7.0 |
| UC-364 | `consolidate_strategy_plan` | 5.7.0 |
| UC-365 | `matts_contrastive_plan` | 5.7.0 |
| UC-366–367 | `hindsight_reasoningbank_shaped_report` | 5.7.0 |
| UC-368 | `init_skill_bank` / `span_partition` | 5.8.0 |
| UC-369 | `select_skills` | 5.8.0 |
| UC-370 | `execute_skill_plan` | 5.8.0 |
| UC-371 | `record_hard_case` | 5.8.0 |
| UC-372 | `designer_evolve_plan` | 5.8.0 |
| UC-373 | `classify_memory_op` | 5.8.0 |
| UC-374 | `noop_gate` | 5.8.0 |
| UC-375 | `memory_op_plan` | 5.8.0 |
| UC-376 | `conflict_update_plan` | 5.8.0 |
| UC-377 | `delete_stale_plan` | 5.8.0 |
| UC-378–379 | `memskill_memoryr1_shaped_report` | 5.8.0 |
| UC-380 | `classify_graph_tier` / `build_query_graph` | 5.9.0 |
| UC-381 | `upward_insight_traverse` | 5.9.0 |
| UC-382 | `downward_interaction_traverse` | 5.9.0 |
| UC-383 | `bidirectional_retrieve` | 5.9.0 |
| UC-384 | `hierarchy_update_plan` | 5.9.0 |
| UC-385 | `meta_thinker_guidance` | 5.9.0 |
| UC-386 | `answerability_check` | 5.9.0 |
| UC-387 | `synthesize_probe_qa` | 5.9.0 |
| UC-388 | `verify_probes` | 5.9.0 |
| UC-389 | `repair_from_probes` | 5.9.0 |
| UC-390–391 | `gmemory_memma_shaped_report` | 5.9.0 |
| UC-392 | `induce_workflow` / `online_induce_gate` | 6.0.0 |
| UC-393 | `workflow_memory_add_plan` | 6.0.0 |
| UC-394 | `retrieve_workflows` | 6.0.0 |
| UC-395 | `workflow_step_budget` | 6.0.0 |
| UC-396 | `distill_retrieval_experience` | 6.0.0 |
| UC-397 | `anomaly_trigger` | 6.0.0 |
| UC-398 | `query_level_guidance` | 6.0.0 |
| UC-399 | `experience_lifecycle_score` | 6.0.0 |
| UC-400 | `prune_experience_plan` | 6.0.0 |
| UC-401 | `isolate_factual_from_procedural` | 6.0.0 |
| UC-402–403 | `awm_rrm_shaped_report` | 6.0.0 |
| UC-404 | `multi_faceted_distill` | 6.1.0 |
| UC-405 | `scenario_retrieve` | 6.1.0 |
| UC-406 | `adaptive_rewrite_plan` | 6.1.0 |
| UC-407 | `utility_after_reuse` | 6.1.0 |
| UC-408 | `selective_add_plan` | 6.1.0 |
| UC-409 | `utility_prune_plan` | 6.1.0 |
| UC-410 | `extract_cheatsheet_snippet` | 6.1.0 |
| UC-411 | `retrieve_cheatsheet` | 6.1.0 |
| UC-412 | `curator_decide` | 6.1.0 |
| UC-413 | `compact_memory_gate` | 6.1.0 |
| UC-414 | `dc_rs_order_check` | 6.1.0 |
| UC-415 | `reme_cheatsheet_shaped_report` | 6.1.0 |
| UC-416 | `experience_pool_add` | 6.2.0 |
| UC-417 | `insight_op` | 6.2.0 |
| UC-418 | `insight_importance_gate` | 6.2.0 |
| UC-419 | `retrieve_insights` | 6.2.0 |
| UC-420 | `retrieve_similar_successes` | 6.2.0 |
| UC-421 | `prospective_reflect` | 6.2.0 |
| UC-422 | `topic_memory_bank` | 6.2.0 |
| UC-423 | `retrieve_topic_memories` | 6.2.0 |
| UC-424 | `retrospective_cite_feedback` | 6.2.0 |
| UC-425 | `rerank_memories` | 6.2.0 |
| UC-426 | `retrieval_refine_plan` | 6.2.0 |
| UC-427 | `expel_rmm_shaped_report` | 6.2.0 |
| UC-428 | `collect_trajectory_label` / `propose_trajectory_patch` | 6.3.0 |
| UC-429 | `parallel_patch_pool` | 6.3.0 |
| UC-430 | `hierarchical_merge_patches` | 6.3.0 |
| UC-431 | `skill_mode_gate` | 6.3.0 |
| UC-432 | `prefer_parallel_over_sequential` | 6.3.0 |
| UC-433 | `streaming_task_append` | 6.3.0 |
| UC-434 | `exprag_retrieve` | 6.3.0 |
| UC-435 | `search_predict_evolve_check` | 6.3.0 |
| UC-436 | `evomem_refine_plan` | 6.3.0 |
| UC-437 | `evolution_similarity_hint` | 6.3.0 |
| UC-438–439 | `trace2skill_evomemory_shaped_report` | 6.3.0 |
| UC-440 | `classify_memory_slot` / `memory_write_op` | 6.4.0 |
| UC-441 | `process_chunk_plan` | 6.4.0 |
| UC-442 | `compression_ratio` | 6.4.0 |
| UC-443 | `memalpha_reward_bundle` | 6.4.0 |
| UC-444 | `length_generalization_gate` | 6.4.0 |
| UC-445 | `classify_failure` | 6.4.0 |
| UC-446 | `extract_replay_outcome` | 6.4.0 |
| UC-447 | `hindsight_relabel_plan` | 6.4.0 |
| UC-448 | `multi_judge_accept` | 6.4.0 |
| UC-449 | `package_training_pair` | 6.4.0 |
| UC-450–451 | `memalpha_agenther_shaped_report` | 6.4.0 |
| UC-452 | `distill_planning_error` | 6.5.0 |
| UC-453 | `prospective_critique_plan` | 6.5.0 |
| UC-454 | `revise_plan_proposal` | 6.5.0 |
| UC-455 | `replan_on_deviation` | 6.5.0 |
| UC-456 | `preflect_before_execute_gate` | 6.5.0 |
| UC-457 | `orchestration_action_select` | 6.5.0 |
| UC-458 | `ttb_residual` | 6.5.0 |
| UC-459 | `step_importance` | 6.5.0 |
| UC-460 | `skill_marginal_flow` | 6.5.0 |
| UC-461 | `skill_curation_decide` | 6.5.0 |
| UC-462 | `phase_evolve_gate` | 6.5.0 |
| UC-463 | `preflect_skillflow_shaped_report` | 6.5.0 |
| UC-464 | `define_skill_triplet` | 6.6.0 |
| UC-465 | `skill_select_gate` / `skill_terminate_check` | 6.6.0 |
| UC-466 | `semantic_gradient_candidate` | 6.6.0 |
| UC-467 | `ppo_gate_verify` | 6.6.0 |
| UC-468 | `skill_score_maintain` | 6.6.0 |
| UC-469 | `ieu_record` | 6.6.0 |
| UC-470 | `two_phase_retrieve` | 6.6.0 |
| UC-471 | `utility_q_update` | 6.6.0 |
| UC-472 | `value_aware_select` | 6.6.0 |
| UC-473 | `semantic_vs_utility_warn` | 6.6.0 |
| UC-474–475 | `procmem_memrl_shaped_report` | 6.6.0 |
| UC-476 | `distill_principle` | 6.7.0 |
| UC-477 | `principle_dedupe_plan` | 6.7.0 |
| UC-478 | `principle_metric_score` | 6.7.0 |
| UC-479 | `search_experience_action` | 6.7.0 |
| UC-480 | `lifecycle_phase_gate` | 6.7.0 |
| UC-481 | `prune_low_score_principles` | 6.7.0 |
| UC-482 | `self_question_task` | 6.7.0 |
| UC-483 | `experience_when_content` | 6.7.0 |
| UC-484 | `mixed_rollout_split` | 6.7.0 |
| UC-485 | `attribute_step_credit` | 6.7.0 |
| UC-486 | `curiosity_explore_plan` | 6.7.0 |
| UC-487 | `evolver_agentevolver_shaped_report` | 6.7.0 |
| UC-488 | `propose_skill` / `practice_skill_run` | 6.8.0 |
| UC-489 | `distill_skill_api` / `hone_skill_api` | 6.8.0 |
| UC-490 | `skill_library_register` | 6.8.0 |
| UC-491 | `transfer_skill_gate` | 6.8.0 |
| UC-492 | `decompose_task_steps` | 6.8.0 |
| UC-493 | `retrieve_skills_for_steps` | 6.8.0 |
| UC-494 | `compose_skill_dag` | 6.8.0 |
| UC-495 | `sad_feedback_loop` | 6.8.0 |
| UC-496 | `granularity_match_check` | 6.8.0 |
| UC-497–499 | `skillweaver_skillroute_shaped_report` | 6.8.0 |
| UC-500 | `propose_reasoning_task` | 6.9.0 |
| UC-501 | `validate_task_structure` | 6.9.0 |
| UC-502 | `learnability_reward` / `solve_reward` | 6.9.0 |
| UC-503 | `abszero_joint_objective` | 6.9.0 |
| UC-504 | `executor_verify_gate` | 6.9.0 |
| UC-505 | `challenger_propose` | 6.9.0 |
| UC-506 | `uncertainty_reward` | 6.9.0 |
| UC-507 | `majority_vote_label` | 6.9.0 |
| UC-508 | `curriculum_band_filter` | 6.9.0 |
| UC-509 | `solver_binary_reward` | 6.9.0 |
| UC-510 | `coevolve_round_plan` | 6.9.0 |
| UC-511 | `abszero_rzero_shaped_report` | 6.9.0 |
| UC-512 | `write_turn_memory` | 7.0.0 |
| UC-513 | `select_turn_memories` | 7.0.0 |
| UC-514 | `reconstruct_policy_context` | 7.0.0 |
| UC-515 | `provenance_credit_mask` | 7.0.0 |
| UC-516 | `history_collapse_gate` | 7.0.0 |
| UC-517 | `budget_binding_check` | 7.0.0 |
| UC-518 | `curriculum_propose_task` | 7.0.0 |
| UC-519 | `tool_use_reward` / `curriculum_reward` | 7.0.0 |
| UC-520 | `executor_frontier_filter` | 7.0.0 |
| UC-521 | `tool_aware_pressure` | 7.0.0 |
| UC-522 | `symbiotic_round_plan` | 7.0.0 |
| UC-523 | `echomem_agent0_shaped_report` | 7.0.0 |
| UC-524 | `mae_propose_question` | 7.1.0 |
| UC-525 | `mae_solve_attempt` | 7.1.0 |
| UC-526 | `mae_judge_score` | 7.1.0 |
| UC-527 | `mae_proposer_reward` | 7.1.0 |
| UC-528 | `mae_quality_filter` | 7.1.0 |
| UC-529 | `mae_triad_round_plan` | 7.1.0 |
| UC-530 | `sage_challenge_task` | 7.1.0 |
| UC-531 | `sage_plan_steps` / `sage_solve_with_plan` | 7.1.0 |
| UC-532 | `sage_critic_filter` | 7.1.0 |
| UC-533 | `sage_drift_gate` | 7.1.0 |
| UC-534 | `sage_closed_loop_round` | 7.1.0 |
| UC-535 | `mae_sagema_shaped_report` | 7.1.0 |
| UC-536 | `memory_trigger_decide` | 7.2.0 |
| UC-537 | `weave_latent_memory` | 7.2.0 |
| UC-538 | `interweave_cycle_plan` | 7.2.0 |
| UC-539 | `faculty_classify` | 7.2.0 |
| UC-540 | `weaver_only_update_gate` | 7.2.0 |
| UC-541 | `sparse_invoke_penalty` | 7.2.0 |
| UC-542 | `text_experience_store` | 7.2.0 |
| UC-543 | `crystallize_plan_to_tool` | 7.2.0 |
| UC-544 | `dual_retrieve` | 7.2.0 |
| UC-545 | `representation_tradeoff` / `promote_kind_gate` | 7.2.0 |
| UC-546 | `metis_loop_plan` | 7.2.0 |
| UC-547 | `memgen_metis_shaped_report` | 7.2.0 |
| UC-548 | `single_trajectory_reflect` | 7.3.0 |
| UC-549 | `intra_task_taxonomy` | 7.3.0 |
| UC-550 | `inter_task_transfer` | 7.3.0 |
| UC-551 | `foresight_reflect` | 7.3.0 |
| UC-552 | `failure_centric_gate` | 7.3.0 |
| UC-553 | `merge_reflections` | 7.3.0 |
| UC-554 | `experience_bank_record` | 7.3.0 |
| UC-555 | `meta_guideline_record` | 7.3.0 |
| UC-556 | `compile_task_guideline` | 7.3.0 |
| UC-557 | `update_experience_weight` | 7.3.0 |
| UC-558 | `forget_stale_experience` / `liveevo_online_round` | 7.3.0 |
| UC-559 | `samule_liveevo_shaped_report` | 7.3.0 |
| UC-560 | `socratic_teacher_craft` | 7.4.0 |
| UC-561 | `socratic_solver_preference` | 7.4.0 |
| UC-562 | `socratic_generator_distill` | 7.4.0 |
| UC-563 | `socratic_seed_bootstrap` | 7.4.0 |
| UC-564 | `socratic_weakness_target` | 7.4.0 |
| UC-565 | `socratic_closed_loop` | 7.4.0 |
| UC-566 | `spiral_self_play_match` | 7.4.0 |
| UC-567 | `spiral_rae_advantage` / `spiral_baseline_ema` | 7.4.0 |
| UC-568 | `spiral_transfer_pattern` | 7.4.0 |
| UC-569 | `spiral_opponent_strength` | 7.4.0 |
| UC-570 | `spiral_multi_game_plan` | 7.4.0 |
| UC-571 | `socratic_spiral_shaped_report` | 7.4.0 |
| UC-572 | `smith_store_memory` | 7.5.0 |
| UC-573 | `smith_create_tool` | 7.5.0 |
| UC-574 | `smith_retrieve_episode` | 7.5.0 |
| UC-575 | `smith_curriculum_difficulty` | 7.5.0 |
| UC-576 | `smith_tool_reuse_gate` | 7.5.0 |
| UC-577 | `smith_loop_plan` | 7.5.0 |
| UC-578 | `hmem_leaf_event` | 7.5.0 |
| UC-579 | `hmem_consolidate_nodes` | 7.5.0 |
| UC-580 | `hmem_link_entities` | 7.5.0 |
| UC-581 | `hmem_decompose_query` / `hmem_hybrid_retrieve` | 7.5.0 |
| UC-582 | `hmem_evolution_gate` | 7.5.0 |
| UC-583 | `smith_hmem_shaped_report` | 7.5.0 |
| UC-584 | `himem_segment_episode` | 7.6.0 |
| UC-585 | `himem_extract_note` | 7.6.0 |
| UC-586 | `himem_link_episode_note` | 7.6.0 |
| UC-587 | `himem_retrieve_strategy` | 7.6.0 |
| UC-588 | `himem_reconsolidate` | 7.6.0 |
| UC-589 | `himem_loop_plan` | 7.6.0 |
| UC-590 | `hmeml_store_level` | 7.6.0 |
| UC-591 | `hmeml_route_query` | 7.6.0 |
| UC-592 | `hmeml_descend` | 7.6.0 |
| UC-593 | `hmeml_parent_link` | 7.6.0 |
| UC-594 | `hmeml_efficiency_score` / `hmeml_loop_plan` | 7.6.0 |
| UC-595 | `himem_hmeml_shaped_report` | 7.6.0 |
| UC-596 | `hyperskill_add_subtask` / `hyperskill_add_skill` | 7.7.0 |
| UC-597 | `hyperskill_add_hyperedge` | 7.7.0 |
| UC-598 | `hyperskill_dual_path_retrieve` | 7.7.0 |
| UC-599 | `hyperskill_rank_skills` | 7.7.0 |
| UC-600 | `hyperskill_maintain_plan` | 7.7.0 |
| UC-601 | `hyperskill_loop_plan` | 7.7.0 |
| UC-602 | `dcpm_day_write` | 7.7.0 |
| UC-603 | `dcpm_supersedes_chain` | 7.7.0 |
| UC-604 | `dcpm_night_induce` | 7.7.0 |
| UC-605 | `dcpm_cross_domain_collision` | 7.7.0 |
| UC-606 | `dcpm_hierarchy_level` | 7.7.0 |
| UC-607 | `dcpm_loop_plan` | 7.7.0 |
| UC-608 | `hyperskill_dcpm_shaped_report` | 7.7.0 |
| UC-609 | `memos_create_cube` | 7.8.0 |
| UC-610 | `memos_schedule` | 7.8.0 |
| UC-611 | `memos_lifecycle` | 7.8.0 |
| UC-612 | `memos_compose` | 7.8.0 |
| UC-613 | `memos_migrate` | 7.8.0 |
| UC-614 | `memos_fuse_gate` | 7.8.0 |
| UC-615 | `memos_loop_plan` | 7.8.0 |
| UC-616 | `skillcraft_save_skill` | 7.8.0 |
| UC-617 | `skillcraft_get_skill` / `skillcraft_list_skills` | 7.8.0 |
| UC-618 | `skillcraft_execute_skill` | 7.8.0 |
| UC-619 | `skillcraft_verify_skill` | 7.8.0 |
| UC-620 | `skillcraft_token_efficiency` | 7.8.0 |
| UC-621 | `skillcraft_loop_plan` | 7.8.0 |
| UC-622 | `memos_skillcraft_shaped_report` | 7.8.0 |
| UC-623 | `cma_persist` | 7.9.0 |
| UC-624 | `cma_selective_retain` | 7.9.0 |
| UC-625 | `cma_associative_route` | 7.9.0 |
| UC-626 | `cma_temporal_chain` | 7.9.0 |
| UC-627 | `cma_consolidate` | 7.9.0 |
| UC-628 | `cma_probe_gate` | 7.9.0 |
| UC-629 | `cma_loop_plan` | 7.9.0 |
| UC-630 | `agentfold_workspace_split` | 7.9.0 |
| UC-631 | `agentfold_fold_command` | 7.9.0 |
| UC-632 | `agentfold_granular_condense` | 7.9.0 |
| UC-633 | `agentfold_deep_consolidate` | 7.9.0 |
| UC-634 | `agentfold_context_budget` / `agentfold_loop_plan` | 7.9.0 |
| UC-635 | `cma_agentfold_shaped_report` | 7.9.0 |
| UC-636 | `memengine_register_function` | 8.0.0 |
| UC-637 | `memengine_compose_operation` | 8.0.0 |
| UC-638 | `memengine_bind_model` | 8.0.0 |
| UC-639 | `memengine_config_set` | 8.0.0 |
| UC-640 | `memengine_reflect_plan` | 8.0.0 |
| UC-641 | `memengine_pluggable` / `memengine_loop_plan` | 8.0.0 |
| UC-642 | `simplemem_compress` | 8.0.0 |
| UC-643 | `simplemem_synthesize` | 8.0.0 |
| UC-644 | `simplemem_intent_scope` | 8.0.0 |
| UC-645 | `simplemem_multiview_index` | 8.0.0 |
| UC-646 | `simplemem_token_ratio` | 8.0.0 |
| UC-647 | `simplemem_loop_plan` | 8.0.0 |
| UC-648 | `memengine_simplemem_shaped_report` | 8.0.0 |
| UC-649 | `omem_extract_persona` | 8.1.0 |
| UC-650 | `omem_update_event` | 8.1.0 |
| UC-651 | `omem_hierarchy_retrieve` | 8.1.0 |
| UC-652 | `omem_profile_gate` | 8.1.0 |
| UC-653 | `omem_scale_memory_time` | 8.1.0 |
| UC-654 | `omem_loop_plan` | 8.1.0 |
| UC-655 | `mandol_basic_unit` | 8.1.0 |
| UC-656 | `mandol_agglomerate` | 8.1.0 |
| UC-657 | `mandol_semantic_map_put` | 8.1.0 |
| UC-658 | `mandol_hybrid_retrieve` | 8.1.0 |
| UC-659 | `mandol_query_route` | 8.1.0 |
| UC-660 | `mandol_token_budget` / `mandol_loop_plan` | 8.1.0 |
| UC-661 | `omem_mandol_shaped_report` | 8.1.0 |
| UC-662 | `memanto_store_typed` | 8.2.0 |
| UC-663 | `memanto_conflict_resolve` | 8.2.0 |
| UC-664 | `memanto_version` | 8.2.0 |
| UC-665 | `memanto_retrieve` | 8.2.0 |
| UC-666 | `memanto_latency_gate` | 8.2.0 |
| UC-667 | `memanto_loop_plan` | 8.2.0 |
| UC-668 | `zep_add_episode` | 8.2.0 |
| UC-669 | `zep_link_entities` | 8.2.0 |
| UC-670 | `zep_bitemporal` | 8.2.0 |
| UC-671 | `zep_synthesize` | 8.2.0 |
| UC-672 | `zep_cross_session` / `zep_loop_plan` | 8.2.0 |
| UC-673 | `memanto_zep_shaped_report` | 8.2.0 |
| UC-674 | `memgpt_main_capacity` | 8.3.0 |
| UC-675 | `memgpt_page_out` | 8.3.0 |
| UC-676 | `memgpt_page_in` | 8.3.0 |
| UC-677 | `memgpt_recall_search` | 8.3.0 |
| UC-678 | `memgpt_archival_search` | 8.3.0 |
| UC-679 | `memgpt_loop_plan` | 8.3.0 |
| UC-680 | `ripple_store_episode` | 8.3.0 |
| UC-681 | `ripple_link_entity` | 8.3.0 |
| UC-682 | `ripple_seed_retrieve` | 8.3.0 |
| UC-683 | `ripple_expand` | 8.3.0 |
| UC-684 | `ripple_recollect_gate` / `ripple_loop_plan` | 8.3.0 |
| UC-685 | `memgpt_ripple_shaped_report` | 8.3.0 |

**Still out of PRD scope (do not treat as missing UCs):** pack pricing, hosted multi-store sync, bulk private-inventory migration, public WTP claims, full MemoryArena / MemBench gym integration (shaped harnesses ship; gyms are post-v1 research engineering).
| UC-686 | `flux_connect_form` | 8.4.0 |
| UC-687 | `flux_feedback_refine` | 8.4.0 |
| UC-688 | `flux_consolidate` | 8.4.0 |
| UC-689 | `flux_repair_link` | 8.4.0 |
| UC-690 | `flux_prune_interference` | 8.4.0 |
| UC-691 | `flux_maturity_gate` / `flux_loop_plan` | 8.4.0 |
| UC-692 | `qumem_segment_episode` | 8.4.0 |
| UC-693 | `qumem_decompose` | 8.4.0 |
| UC-694 | `qumem_plan_queries` | 8.4.0 |
| UC-695 | `qumem_infer_user_state` | 8.4.0 |
| UC-696 | `qumem_temporal_valid` | 8.4.0 |
| UC-697 | `qumem_loop_plan` | 8.4.0 |
| UC-698 | `fluxmem_qumem_shaped_report` | 8.4.0 |
| UC-699 | `viking_extract_event` | 8.5.0 |
| UC-700 | `viking_update_entity` | 8.5.0 |
| UC-701 | `viking_timeline_compress` | 8.5.0 |
| UC-702 | `viking_time_weighted_recall` | 8.5.0 |
| UC-703 | `viking_rerank` | 8.5.0 |
| UC-704 | `viking_loop_plan` | 8.5.0 |
| UC-705 | `recmem_buffer_subconscious` | 8.5.0 |
| UC-706 | `recmem_recurrence_gate` | 8.5.0 |
| UC-707 | `recmem_consolidate_episodic` | 8.5.0 |
| UC-708 | `recmem_semantic_refine` | 8.5.0 |
| UC-709 | `recmem_merge_retrieve` / `recmem_loop_plan` | 8.5.0 |
| UC-710 | `vikingmem_recmem_shaped_report` | 8.5.0 |
| UC-711 | `mbank_store_memory` | 8.6.0 |
| UC-712 | `mbank_summon` | 8.6.0 |
| UC-713 | `mbank_personality_synth` | 8.6.0 |
| UC-714 | `mbank_forget_curve` | 8.6.0 |
| UC-715 | `mbank_reinforce` | 8.6.0 |
| UC-716 | `mbank_loop_plan` | 8.6.0 |
| UC-717 | `rfmem_familiarity_score` | 8.6.0 |
| UC-718 | `rfmem_path_route` | 8.6.0 |
| UC-719 | `rfmem_top_k_familiar` | 8.6.0 |
| UC-720 | `rfmem_recollect_expand` | 8.6.0 |
| UC-721 | `rfmem_alpha_mix` / `rfmem_loop_plan` | 8.6.0 |
| UC-722 | `memorybank_rfmem_shaped_report` | 8.6.0 |
| UC-723 | `agemem_ltm_store` | 8.7.0 |
| UC-724 | `agemem_stm_manage` | 8.7.0 |
| UC-725 | `agemem_retrieve` | 8.7.0 |
| UC-726 | `agemem_summarize` | 8.7.0 |
| UC-727 | `agemem_discard_plan` | 8.7.0 |
| UC-728 | `agemem_loop_plan` | 8.7.0 |
| UC-729 | `memgas_unit` | 8.7.0 |
| UC-730 | `memgas_associate` | 8.7.0 |
| UC-731 | `memgas_entropy_route` | 8.7.0 |
| UC-732 | `memgas_select_granularity` | 8.7.0 |
| UC-733 | `memgas_filter_plan` / `memgas_loop_plan` | 8.7.0 |
| UC-734 | `agemem_memgas_shaped_report` | 8.7.0 |
| UC-735 | `memwalker_segment` | 8.8.0 |
| UC-736 | `memwalker_build_node` | 8.8.0 |
| UC-737 | `memwalker_navigate` | 8.8.0 |
| UC-738 | `memwalker_gather` | 8.8.0 |
| UC-739 | `memwalker_path_gate` | 8.8.0 |
| UC-740 | `memwalker_loop_plan` | 8.8.0 |
| UC-741 | `mgr_store_layer` | 8.8.0 |
| UC-742 | `mgr_detect_conflict` | 8.8.0 |
| UC-743 | `mgr_resolve_plan` | 8.8.0 |
| UC-744 | `mgr_multilayer_retrieve` | 8.8.0 |
| UC-745 | `mgr_propagate` / `mgr_loop_plan` | 8.8.0 |
| UC-746 | `memwalker_memgraphrag_shaped_report` | 8.8.0 |
| UC-747 | `raptor_embed_chunk` | 8.9.0 |
| UC-748 | `raptor_cluster` | 8.9.0 |
| UC-749 | `raptor_summarize_node` | 8.9.0 |
| UC-750 | `raptor_tree_traverse` | 8.9.0 |
| UC-751 | `raptor_collapsed_retrieve` | 8.9.0 |
| UC-752 | `raptor_loop_plan` | 8.9.0 |
| UC-753 | `lightrag_index_entity` | 8.9.0 |
| UC-754 | `lightrag_index_relation` | 8.9.0 |
| UC-755 | `lightrag_dual_retrieve` | 8.9.0 |
| UC-756 | `lightrag_incremental_update` | 8.9.0 |
| UC-757 | `lightrag_graph_vector_fuse` / `lightrag_loop_plan` | 8.9.0 |
| UC-758 | `raptor_lightrag_shaped_report` | 8.9.0 |
| UC-759 | `memorag_memorize` | 9.0.0 |
| UC-760 | `memorag_clue` | 9.0.0 |
| UC-761 | `memorag_retrieve_by_clue` | 9.0.0 |
| UC-762 | `memorag_dual_system` | 9.0.0 |
| UC-763 | `memorag_generate_plan` | 9.0.0 |
| UC-764 | `memorag_loop_plan` | 9.0.0 |
| UC-765 | `pageindex_build_toc` | 9.0.0 |
| UC-766 | `pageindex_add_section` | 9.0.0 |
| UC-767 | `pageindex_reason_nav` | 9.0.0 |
| UC-768 | `pageindex_select_section` | 9.0.0 |
| UC-769 | `pageindex_trace_path` / `pageindex_loop_plan` | 9.0.0 |
| UC-770 | `memorag_pageindex_shaped_report` | 9.0.0 |
| UC-771 | `selfrag_need_retrieve` | 9.1.0 |
| UC-772 | `selfrag_relevance_critique` | 9.1.0 |
| UC-773 | `selfrag_support_critique` | 9.1.0 |
| UC-774 | `selfrag_utility_critique` | 9.1.0 |
| UC-775 | `selfrag_select_best` | 9.1.0 |
| UC-776 | `selfrag_loop_plan` | 9.1.0 |
| UC-777 | `memobrain_dep_edge` | 9.1.0 |
| UC-778 | `memobrain_prune_invalid` | 9.1.0 |
| UC-779 | `memobrain_fold_subtraj` | 9.1.0 |
| UC-780 | `memobrain_flush_budget` | 9.1.0 |
| UC-781 | `memobrain_salience_keep` / `memobrain_loop_plan` | 9.1.0 |
| UC-782 | `selfrag_memobrain_shaped_report` | 9.1.0 |
| UC-783 | `crag_evaluate_retrieval` | 9.2.0 |
| UC-784 | `crag_correct_refine` | 9.2.0 |
| UC-785 | `crag_web_fallback_plan` | 9.2.0 |
| UC-786 | `crag_ambiguous_blend` | 9.2.0 |
| UC-787 | `crag_action_select` | 9.2.0 |
| UC-788 | `crag_loop_plan` | 9.2.0 |
| UC-789 | `hyde_hypothetical_doc` | 9.2.0 |
| UC-790 | `hyde_encode_proxy` | 9.2.0 |
| UC-791 | `hyde_retrieve_by_hyp` | 9.2.0 |
| UC-792 | `hyde_filter_hallucination` | 9.2.0 |
| UC-793 | `hyde_ground_corpus` / `hyde_loop_plan` | 9.2.0 |
| UC-794 | `crag_hyde_shaped_report` | 9.2.0 |
| UC-795 | `adaptiverag_classify_complexity` | 9.3.0 |
| UC-796 | `adaptiverag_select_strategy` | 9.3.0 |
| UC-797 | `adaptiverag_no_retrieve` | 9.3.0 |
| UC-798 | `adaptiverag_single_step` | 9.3.0 |
| UC-799 | `adaptiverag_multi_step` | 9.3.0 |
| UC-800 | `adaptiverag_loop_plan` | 9.3.0 |
| UC-801 | `flare_anticipate_sentence` | 9.3.0 |
| UC-802 | `flare_low_confidence` | 9.3.0 |
| UC-803 | `flare_retrieve_for_regen` | 9.3.0 |
| UC-804 | `flare_regenerate_sentence` | 9.3.0 |
| UC-805 | `flare_active_step` / `flare_loop_plan` | 9.3.0 |
| UC-806 | `adaptiverag_flare_shaped_report` | 9.3.0 |
| UC-807 | `graphreader_build_node` | 9.4.0 |
| UC-808 | `graphreader_read_node` | 9.4.0 |
| UC-809 | `graphreader_read_neighbors` | 9.4.0 |
| UC-810 | `graphreader_note_insight` | 9.4.0 |
| UC-811 | `graphreader_reflect_plan` | 9.4.0 |
| UC-812 | `graphreader_loop_plan` | 9.4.0 |
| UC-813 | `gretriever_node_prize` | 9.4.0 |
| UC-814 | `gretriever_pcst_select` | 9.4.0 |
| UC-815 | `gretriever_subgraph` | 9.4.0 |
| UC-816 | `gretriever_soft_prompt_plan` | 9.4.0 |
| UC-817 | `gretriever_highlight` / `gretriever_loop_plan` | 9.4.0 |
| UC-818 | `graphreader_gretriever_shaped_report` | 9.4.0 |
| UC-819 | `rqrag_rewrite` | 9.5.0 |
| UC-820 | `rqrag_decompose` | 9.5.0 |
| UC-821 | `rqrag_disambiguate` | 9.5.0 |
| UC-822 | `rqrag_refine_mode` | 9.5.0 |
| UC-823 | `rqrag_retrieve_refined` | 9.5.0 |
| UC-824 | `rqrag_loop_plan` | 9.5.0 |
| UC-825 | `ircot_cot_step` | 9.5.0 |
| UC-826 | `ircot_retrieve_guided` | 9.5.0 |
| UC-827 | `ircot_interleave` | 9.5.0 |
| UC-828 | `ircot_answer_ready` | 9.5.0 |
| UC-829 | `ircot_hallucination_check` / `ircot_loop_plan` | 9.5.0 |
| UC-830 | `rqrag_ircot_shaped_report` | 9.5.0 |
| UC-831 | `replug_retrieve_docs` | 9.6.0 |
| UC-832 | `replug_prepend_doc` | 9.6.0 |
| UC-833 | `replug_ensemble_probs` | 9.6.0 |
| UC-834 | `replug_supervise_retriever` | 9.6.0 |
| UC-835 | `replug_blackbox_forward` | 9.6.0 |
| UC-836 | `replug_loop_plan` | 9.6.0 |
| UC-837 | `iterretgen_generate` | 9.6.0 |
| UC-838 | `iterretgen_use_as_query` | 9.6.0 |
| UC-839 | `iterretgen_retrieve_next` | 9.6.0 |
| UC-840 | `iterretgen_iterate` | 9.6.0 |
| UC-841 | `iterretgen_adapt_retriever` / `iterretgen_loop_plan` | 9.6.0 |
| UC-842 | `replug_iterretgen_shaped_report` | 9.6.0 |
| UC-843 | `planrag_make_plan` | 9.7.0 |
| UC-844 | `planrag_analysis_query` | 9.7.0 |
| UC-845 | `planrag_retrieve_data` | 9.7.0 |
| UC-846 | `planrag_replan` | 9.7.0 |
| UC-847 | `planrag_decide` | 9.7.0 |
| UC-848 | `planrag_loop_plan` | 9.7.0 |
| UC-849 | `rrr_rewrite_query` | 9.7.0 |
| UC-850 | `rrr_retrieve` | 9.7.0 |
| UC-851 | `rrr_read` | 9.7.0 |
| UC-852 | `rrr_reader_feedback` | 9.7.0 |
| UC-853 | `rrr_train_rewriter_plan` / `rrr_loop_plan` | 9.7.0 |
| UC-854 | `planrag_rrr_shaped_report` | 9.7.0 |
| UC-855 | `dsp_bootstrap_demo` | 9.8.0 |
| UC-856 | `dsp_search` | 9.8.0 |
| UC-857 | `dsp_predict` | 9.8.0 |
| UC-858 | `dsp_compose_program` | 9.8.0 |
| UC-859 | `dsp_multihop_hop` | 9.8.0 |
| UC-860 | `dsp_loop_plan` | 9.8.0 |
| UC-861 | `genread_generate_context` | 9.8.0 |
| UC-862 | `genread_ground_optional` | 9.8.0 |
| UC-863 | `genread_answer` | 9.8.0 |
| UC-864 | `genread_compare_retrieve` | 9.8.0 |
| UC-865 | `genread_hybrid` / `genread_loop_plan` | 9.8.0 |
| UC-866 | `dsp_genread_shaped_report` | 9.8.0 |
| UC-867 | `selfask_followup` | 9.9.0 |
| UC-868 | `selfask_search_intercept` | 9.9.0 |
| UC-869 | `selfask_compose_answer` | 9.9.0 |
| UC-870 | `selfask_stop` | 9.9.0 |
| UC-871 | `selfask_demo_prompt` | 9.9.0 |
| UC-872 | `selfask_loop_plan` | 9.9.0 |
| UC-873 | `react_thought` | 9.9.0 |
| UC-874 | `react_action` | 9.9.0 |
| UC-875 | `react_observe` | 9.9.0 |
| UC-876 | `react_finish` | 9.9.0 |
| UC-877 | `react_trajectory` / `react_loop_plan` | 9.9.0 |
| UC-878 | `selfask_react_shaped_report` | 9.9.0 |
| UC-879 | `tog_init_entity` | 10.0.0 |
| UC-880 | `tog_explore_neighbors` | 10.0.0 |
| UC-881 | `tog_beam_prune` | 10.0.0 |
| UC-882 | `tog_path_score` | 10.0.0 |
| UC-883 | `tog_answer_from_paths` | 10.0.0 |
| UC-884 | `tog_loop_plan` | 10.0.0 |
| UC-885 | `tf_api_candidate` | 10.0.0 |
| UC-886 | `tf_filter_call` | 10.0.0 |
| UC-887 | `tf_execute_proxy` | 10.0.0 |
| UC-888 | `tf_incorporate_result` | 10.0.0 |
| UC-889 | `tf_demo_apis` / `tf_loop_plan` | 10.0.0 |
| UC-890 | `tog_toolformer_shaped_report` | 10.0.0 |
| UC-891 | `rx_trial_run` | 10.1.0 |
| UC-892 | `rx_evaluate` | 10.1.0 |
| UC-893 | `rx_verbal_reflect` | 10.1.0 |
| UC-894 | `rx_memory_store` | 10.1.0 |
| UC-895 | `rx_next_trial` | 10.1.0 |
| UC-896 | `rx_loop_plan` | 10.1.0 |
| UC-897 | `sc_sample_path` | 10.1.0 |
| UC-898 | `sc_collect_answers` | 10.1.0 |
| UC-899 | `sc_majority_vote` | 10.1.0 |
| UC-900 | `sc_marginalize` | 10.1.0 |
| UC-901 | `sc_temperature` / `sc_loop_plan` | 10.1.0 |
| UC-902 | `reflexion_selfcons_shaped_report` | 10.1.0 |
| UC-903 | `tot_propose` | 10.2.0 |
| UC-904 | `tot_evaluate` | 10.2.0 |
| UC-905 | `tot_expand` | 10.2.0 |
| UC-906 | `tot_backtrack` | 10.2.0 |
| UC-907 | `tot_select_best` | 10.2.0 |
| UC-908 | `tot_loop_plan` | 10.2.0 |
| UC-909 | `ltm_decompose` | 10.2.0 |
| UC-910 | `ltm_solve_sub` | 10.2.0 |
| UC-911 | `ltm_carry_forward` | 10.2.0 |
| UC-912 | `ltm_compose_final` | 10.2.0 |
| UC-913 | `ltm_easy_to_hard` / `ltm_loop_plan` | 10.2.0 |
| UC-914 | `tot_ltm_shaped_report` | 10.2.0 |
| UC-915 | `got_add_thought` | 10.3.0 |
| UC-916 | `got_link` | 10.3.0 |
| UC-917 | `got_aggregate` | 10.3.0 |
| UC-918 | `got_feedback` | 10.3.0 |
| UC-919 | `got_score_graph` | 10.3.0 |
| UC-920 | `got_loop_plan` | 10.3.0 |
| UC-921 | `pot_emit_program` | 10.3.0 |
| UC-922 | `pot_sandbox_run` | 10.3.0 |
| UC-923 | `pot_read_result` | 10.3.0 |
| UC-924 | `pot_self_consistency` | 10.3.0 |
| UC-925 | `pot_disentangle` / `pot_loop_plan` | 10.3.0 |
| UC-926 | `got_pot_shaped_report` | 10.3.0 |
| UC-927 | `aot_load_algorithm` | 10.4.0 |
| UC-928 | `aot_explore_subtree` | 10.4.0 |
| UC-929 | `aot_tunnel_vision` | 10.4.0 |
| UC-930 | `aot_query_budget` | 10.4.0 |
| UC-931 | `aot_surpass_algo` | 10.4.0 |
| UC-932 | `aot_loop_plan` | 10.4.0 |
| UC-933 | `rap_world_state` | 10.4.0 |
| UC-934 | `rap_expand` | 10.4.0 |
| UC-935 | `rap_reward` | 10.4.0 |
| UC-936 | `rap_select_path` | 10.4.0 |
| UC-937 | `rap_balance` / `rap_loop_plan` | 10.4.0 |
| UC-938 | `aot_rap_shaped_report` | 10.4.0 |
| UC-939 | `sot_emit_skeleton` | 10.5.0 |
| UC-940 | `sot_extract_points` | 10.5.0 |
| UC-941 | `sot_parallel_expand` | 10.5.0 |
| UC-942 | `sot_router` | 10.5.0 |
| UC-943 | `sot_latency_gain` | 10.5.0 |
| UC-944 | `sot_loop_plan` | 10.5.0 |
| UC-945 | `bot_distill_template` | 10.5.0 |
| UC-946 | `bot_retrieve_template` | 10.5.0 |
| UC-947 | `bot_instantiate` | 10.5.0 |
| UC-948 | `bot_buffer_update` | 10.5.0 |
| UC-949 | `bot_cost_ratio` / `bot_loop_plan` | 10.5.0 |
| UC-950 | `sot_bot_shaped_report` | 10.5.0 |
| UC-951 | `sd_select_modules` | 10.6.0 |
| UC-952 | `sd_adapt` | 10.6.0 |
| UC-953 | `sd_implement` | 10.6.0 |
| UC-954 | `sd_apply_instance` | 10.6.0 |
| UC-955 | `sd_compute_ratio` | 10.6.0 |
| UC-956 | `sd_loop_plan` | 10.6.0 |
| UC-957 | `mp_break_task` | 10.6.0 |
| UC-958 | `mp_assign_expert` | 10.6.0 |
| UC-959 | `mp_oversee` | 10.6.0 |
| UC-960 | `mp_verify` | 10.6.0 |
| UC-961 | `mp_task_agnostic` / `mp_loop_plan` | 10.6.0 |
| UC-962 | `sd_mp_shaped_report` | 10.6.0 |
| UC-963 | `qs_thought_bounds` | 10.7.0 |
| UC-964 | `qs_parallel_sample` | 10.7.0 |
| UC-965 | `qs_mix_head` | 10.7.0 |
| UC-966 | `qs_hard_token_aid` | 10.7.0 |
| UC-967 | `qs_zero_shot_flag` | 10.7.0 |
| UC-968 | `qs_loop_plan` | 10.7.0 |
| UC-969 | `dep_decompose` | 10.7.0 |
| UC-970 | `dep_delegate` | 10.7.0 |
| UC-971 | `dep_recurse` | 10.7.0 |
| UC-972 | `dep_swap_symbolic` | 10.7.0 |
| UC-973 | `dep_library_size` / `dep_loop_plan` | 10.7.0 |
| UC-974 | `qs_dep_shaped_report` | 10.7.0 |
| UC-975 | `star_generate` | 10.8.0 |
| UC-976 | `star_filter_correct` | 10.8.0 |
| UC-977 | `star_rationalize` | 10.8.0 |
| UC-978 | `star_finetune_proxy` | 10.8.0 |
| UC-979 | `star_bootstrap_round` | 10.8.0 |
| UC-980 | `star_loop_plan` | 10.8.0 |
| UC-981 | `cr_propose` | 10.8.0 |
| UC-982 | `cr_verify` | 10.8.0 |
| UC-983 | `cr_accumulate` | 10.8.0 |
| UC-984 | `cr_report` | 10.8.0 |
| UC-985 | `cr_roles` / `cr_loop_plan` | 10.8.0 |
| UC-986 | `star_cr_shaped_report` | 10.8.0 |
| UC-987 | `ps_devise_plan` | 10.9.0 |
| UC-988 | `ps_execute` | 10.9.0 |
| UC-989 | `ps_plus_extract` | 10.9.0 |
| UC-990 | `ps_calc_guard` | 10.9.0 |
| UC-991 | `ps_missing_step_fix` | 10.9.0 |
| UC-992 | `ps_loop_plan` | 10.9.0 |
| UC-993 | `php_base_answer` | 10.9.0 |
| UC-994 | `php_emit_hint` | 10.9.0 |
| UC-995 | `php_reask` | 10.9.0 |
| UC-996 | `php_stable_stop` | 10.9.0 |
| UC-997 | `php_combine_sc` / `php_loop_plan` | 10.9.0 |
| UC-998 | `ps_php_shaped_report` | 10.9.0 |
| UC-999 | `ac_programmer` | 11.0.0 |
| UC-1000 | `ac_test_designer` | 11.0.0 |
| UC-1001 | `ac_test_executor` | 11.0.0 |
| UC-1002 | `ac_refine` | 11.0.0 |
| UC-1003 | `ac_pass_gate` | 11.0.0 |
| UC-1004 | `ac_loop_plan` | 11.0.0 |
| UC-1005 | `pal_emit_program` | 11.0.0 |
| UC-1006 | `pal_offload_solve` | 11.0.0 |
| UC-1007 | `pal_read_answer` | 11.0.0 |
| UC-1008 | `pal_decompose_only` | 11.0.0 |
| UC-1009 | `pal_vs_cot` / `pal_loop_plan` | 11.0.0 |
| UC-1010 | `ac_pal_shaped_report` | 11.0.0 |
| UC-1011 | `fcot_translate` | 11.1.0 |
| UC-1012 | `fcot_solve` | 11.1.0 |
| UC-1013 | `fcot_faithfulness` | 11.1.0 |
| UC-1014 | `fcot_interleave` | 11.1.0 |
| UC-1015 | `fcot_vs_cot` | 11.1.0 |
| UC-1016 | `fcot_loop_plan` | 11.1.0 |
| UC-1017 | `lats_expand` | 11.1.0 |
| UC-1018 | `lats_value` | 11.1.0 |
| UC-1019 | `lats_reflect` | 11.1.0 |
| UC-1020 | `lats_select` | 11.1.0 |
| UC-1021 | `lats_env_feedback` / `lats_loop_plan` | 11.1.0 |
| UC-1022 | `fcot_lats_shaped_report` | 11.1.0 |
| UC-1023 | `voy_curriculum` | 11.2.0 |
| UC-1024 | `voy_skill_store` | 11.2.0 |
| UC-1025 | `voy_skill_retrieve` | 11.2.0 |
| UC-1026 | `voy_self_verify` | 11.2.0 |
| UC-1027 | `voy_compose` | 11.2.0 |
| UC-1028 | `voy_loop_plan` | 11.2.0 |
| UC-1029 | `rewoo_plan` | 11.2.0 |
| UC-1030 | `rewoo_worker` | 11.2.0 |
| UC-1031 | `rewoo_solver` | 11.2.0 |
| UC-1032 | `rewoo_decouple` | 11.2.0 |
| UC-1033 | `rewoo_token_save` / `rewoo_loop_plan` | 11.2.0 |
| UC-1034 | `voy_rewoo_shaped_report` | 11.2.0 |
| UC-1035 | `critic_draft` | 11.3.0 |
| UC-1036 | `critic_tool_check` | 11.3.0 |
| UC-1037 | `critic_revise` | 11.3.0 |
| UC-1038 | `critic_iterate` | 11.3.0 |
| UC-1039 | `critic_stop` | 11.3.0 |
| UC-1040 | `critic_loop_plan` | 11.3.0 |
| UC-1041 | `dv_natural_program` | 11.3.0 |
| UC-1042 | `dv_step_verify` | 11.3.0 |
| UC-1043 | `dv_premise_scope` | 11.3.0 |
| UC-1044 | `dv_unanimity` | 11.3.0 |
| UC-1045 | `dv_ground` / `dv_loop_plan` | 11.3.0 |
| UC-1046 | `critic_dv_shaped_report` | 11.3.0 |
| UC-1047 | `hgpt_plan` | 11.4.0 |
| UC-1048 | `hgpt_select` | 11.4.0 |
| UC-1049 | `hgpt_execute` | 11.4.0 |
| UC-1050 | `hgpt_summarize` | 11.4.0 |
| UC-1051 | `hgpt_modality` | 11.4.0 |
| UC-1052 | `hgpt_loop_plan` | 11.4.0 |
| UC-1053 | `mad_propose` | 11.4.0 |
| UC-1054 | `mad_debate` | 11.4.0 |
| UC-1055 | `mad_critique` | 11.4.0 |
| UC-1056 | `mad_converge` | 11.4.0 |
| UC-1057 | `mad_factuality` / `mad_loop_plan` | 11.4.0 |
| UC-1058 | `hgpt_mad_shaped_report` | 11.4.0 |
| UC-1059 | `autocot_cluster` | 11.5.0 |
| UC-1060 | `autocot_sample` | 11.5.0 |
| UC-1061 | `autocot_generate` | 11.5.0 |
| UC-1062 | `autocot_heuristic` | 11.5.0 |
| UC-1063 | `autocot_diversity` | 11.5.0 |
| UC-1064 | `autocot_loop_plan` | 11.5.0 |
| UC-1065 | `camel_roles` | 11.5.0 |
| UC-1066 | `camel_inception` | 11.5.0 |
| UC-1067 | `camel_turn` | 11.5.0 |
| UC-1068 | `camel_complete` | 11.5.0 |
| UC-1069 | `camel_society` / `camel_loop_plan` | 11.5.0 |
| UC-1070 | `autocot_camel_shaped_report` | 11.5.0 |
| UC-1071 | `cham_inventory` | 11.6.0 |
| UC-1072 | `cham_plan` | 11.6.0 |
| UC-1073 | `cham_compose` | 11.6.0 |
| UC-1074 | `cham_execute` | 11.6.0 |
| UC-1075 | `cham_constraint` | 11.6.0 |
| UC-1076 | `cham_loop_plan` | 11.6.0 |
| UC-1077 | `rot_trigger` | 11.6.0 |
| UC-1078 | `rot_divide` | 11.6.0 |
| UC-1079 | `rot_conquer` | 11.6.0 |
| UC-1080 | `rot_merge` | 11.6.0 |
| UC-1081 | `rot_context_limit` / `rot_loop_plan` | 11.6.0 |
| UC-1082 | `cham_rot_shaped_report` | 11.6.0 |
| UC-1083 | `ap_sample` | 11.7.0 |
| UC-1084 | `ap_uncertainty` | 11.7.0 |
| UC-1085 | `ap_select` | 11.7.0 |
| UC-1086 | `ap_annotate` | 11.7.0 |
| UC-1087 | `ap_pool` | 11.7.0 |
| UC-1088 | `ap_loop_plan` | 11.7.0 |
| UC-1089 | `ana_recall` | 11.7.0 |
| UC-1090 | `ana_knowledge` | 11.7.0 |
| UC-1091 | `ana_solve` | 11.7.0 |
| UC-1092 | `ana_adapt` | 11.7.0 |
| UC-1093 | `ana_no_label` / `ana_loop_plan` | 11.7.0 |
| UC-1094 | `ap_ana_shaped_report` | 11.7.0 |
| UC-1095 | `cbp_score` | 11.8.0 |
| UC-1096 | `cbp_select` | 11.8.0 |
| UC-1097 | `cbp_sample_chains` | 11.8.0 |
| UC-1098 | `cbp_vote_complex` | 11.8.0 |
| UC-1099 | `cbp_robust` | 11.8.0 |
| UC-1100 | `cbp_loop_plan` | 11.8.0 |
| UC-1101 | `sb_abstract` | 11.8.0 |
| UC-1102 | `sb_principle` | 11.8.0 |
| UC-1103 | `sb_reason` | 11.8.0 |
| UC-1104 | `sb_path` | 11.8.0 |
| UC-1105 | `sb_detail_trap` / `sb_loop_plan` | 11.8.0 |
| UC-1106 | `cbp_sb_shaped_report` | 11.8.0 |
| UC-1107 | `mmcot_fuse` | 11.9.0 |
| UC-1108 | `mmcot_rationale` | 11.9.0 |
| UC-1109 | `mmcot_infer` | 11.9.0 |
| UC-1110 | `mmcot_hallucination` | 11.9.0 |
| UC-1111 | `mmcot_separate` | 11.9.0 |
| UC-1112 | `mmcot_loop_plan` | 11.9.0 |
| UC-1113 | `mai_abduce` | 11.9.0 |
| UC-1114 | `mai_recurse` | 11.9.0 |
| UC-1115 | `mai_sat` | 11.9.0 |
| UC-1116 | `mai_consistent` | 11.9.0 |
| UC-1117 | `mai_unreliable` / `mai_loop_plan` | 11.9.0 |
| UC-1118 | `mmcot_mai_shaped_report` | 11.9.0 |
| UC-1119 | `sr_generate` | 12.0.0 |
| UC-1120 | `sr_feedback` | 12.0.0 |
| UC-1121 | `sr_refine` | 12.0.0 |
| UC-1122 | `sr_iterate` | 12.0.0 |
| UC-1123 | `sr_no_train` | 12.0.0 |
| UC-1124 | `sr_loop_plan` | 12.0.0 |
| UC-1125 | `mcp_recognize` | 12.0.0 |
| UC-1126 | `mcp_interpret` | 12.0.0 |
| UC-1127 | `mcp_reevaluate` | 12.0.0 |
| UC-1128 | `mcp_confidence` | 12.0.0 |
| UC-1129 | `mcp_justify` / `mcp_loop_plan` | 12.0.0 |
| UC-1130 | `sr_mcp_shaped_report` | 12.0.0 |
| UC-1131 | `thot_segment` | 12.1.0 |
| UC-1132 | `thot_analyze` | 12.1.0 |
| UC-1133 | `thot_select` | 12.1.0 |
| UC-1134 | `thot_synthesize` | 12.1.0 |
| UC-1135 | `thot_plug` | 12.1.0 |
| UC-1136 | `thot_loop_plan` | 12.1.0 |
| UC-1137 | `tprop_propose` | 12.1.0 |
| UC-1138 | `tprop_solve` | 12.1.0 |
| UC-1139 | `tprop_reuse` | 12.1.0 |
| UC-1140 | `tprop_amend` | 12.1.0 |
| UC-1141 | `tprop_compat` / `tprop_loop_plan` | 12.1.0 |
| UC-1142 | `thot_tprop_shaped_report` | 12.1.0 |
| UC-1143 | `s2a_regenerate` | 12.2.0 |
| UC-1144 | `s2a_attend` | 12.2.0 |
| UC-1145 | `s2a_respond` | 12.2.0 |
| UC-1146 | `s2a_factuality` | 12.2.0 |
| UC-1147 | `s2a_sycophancy` | 12.2.0 |
| UC-1148 | `s2a_loop_plan` | 12.2.0 |
| UC-1149 | `ccot_valid` | 12.2.0 |
| UC-1150 | `ccot_invalid` | 12.2.0 |
| UC-1151 | `ccot_contrast` | 12.2.0 |
| UC-1152 | `ccot_reason` | 12.2.0 |
| UC-1153 | `ccot_auto` / `ccot_loop_plan` | 12.2.0 |
| UC-1154 | `s2a_ccot_shaped_report` | 12.2.0 |
| UC-1155 | `tabcot_header` | 12.3.0 |
| UC-1156 | `tabcot_row` | 12.3.0 |
| UC-1157 | `tabcot_infer2d` | 12.3.0 |
| UC-1158 | `tabcot_extract` | 12.3.0 |
| UC-1159 | `tabcot_zeroshot` | 12.3.0 |
| UC-1160 | `tabcot_loop_plan` | 12.3.0 |
| UC-1161 | `xot_mcts` | 12.3.0 |
| UC-1162 | `xot_revise` | 12.3.0 |
| UC-1163 | `xot_map` | 12.3.0 |
| UC-1164 | `xot_penrose` | 12.3.0 |
| UC-1165 | `xot_flexible` / `xot_loop_plan` | 12.3.0 |
| UC-1166 | `tabcot_xot_shaped_report` | 12.3.0 |
| UC-1167 | `cove_draft` | 12.4.0 |
| UC-1168 | `cove_plan` | 12.4.0 |
| UC-1169 | `cove_answer` | 12.4.0 |
| UC-1170 | `cove_final` | 12.4.0 |
| UC-1171 | `cove_hallucination` | 12.4.0 |
| UC-1172 | `cove_loop_plan` | 12.4.0 |
| UC-1173 | `ved_uncertain` | 12.4.0 |
| UC-1174 | `ved_search` | 12.4.0 |
| UC-1175 | `ved_edit` | 12.4.0 |
| UC-1176 | `ved_predict` | 12.4.0 |
| UC-1177 | `ved_knowledge` / `ved_loop_plan` | 12.4.0 |
| UC-1178 | `cove_ved_shaped_report` | 12.4.0 |
| UC-1179 | `sve_forward` | 12.5.0 |
| UC-1180 | `sve_mask` | 12.5.0 |
| UC-1181 | `sve_repredict` | 12.5.0 |
| UC-1182 | `sve_score` | 12.5.0 |
| UC-1183 | `sve_select` | 12.5.0 |
| UC-1184 | `sve_loop_plan` | 12.5.0 |
| UC-1185 | `cod_sparse` | 12.5.0 |
| UC-1186 | `cod_entities` | 12.5.0 |
| UC-1187 | `cod_fuse` | 12.5.0 |
| UC-1188 | `cod_length` | 12.5.0 |
| UC-1189 | `cod_tradeoff` / `cod_loop_plan` | 12.5.0 |
| UC-1190 | `sve_cod_shaped_report` | 12.5.0 |
| UC-1191 | `hsp_hint` | 12.6.0 |
| UC-1192 | `hsp_solve` | 12.6.0 |
| UC-1193 | `hsp_answer` | 12.6.0 |
| UC-1194 | `hsp_compose` | 12.6.0 |
| UC-1195 | `hsp_quality` | 12.6.0 |
| UC-1196 | `hsp_loop_plan` | 12.6.0 |
| UC-1197 | `emo_stimulus` | 12.6.0 |
| UC-1198 | `emo_append` | 12.6.0 |
| UC-1199 | `emo_run` | 12.6.0 |
| UC-1200 | `emo_truth` | 12.6.0 |
| UC-1201 | `emo_psych` / `emo_loop_plan` | 12.6.0 |
| UC-1202 | `hsp_emo_shaped_report` | 12.6.0 |
| UC-1203 | `ape_propose` | 12.7.0 |
| UC-1204 | `ape_score` | 12.7.0 |
| UC-1205 | `ape_select` | 12.7.0 |
| UC-1206 | `ape_steer` | 12.7.0 |
| UC-1207 | `ape_human` | 12.7.0 |
| UC-1208 | `ape_loop_plan` | 12.7.0 |
| UC-1209 | `pbr_init` | 12.7.0 |
| UC-1210 | `pbr_mutate` | 12.7.0 |
| UC-1211 | `pbr_fitness` | 12.7.0 |
| UC-1212 | `pbr_diversity` | 12.7.0 |
| UC-1213 | `pbr_selfref` / `pbr_loop_plan` | 12.7.0 |
| UC-1214 | `ape_pbr_shaped_report` | 12.7.0 |
| UC-1215 | `opro_meta` | 12.8.0 |
| UC-1216 | `opro_propose` | 12.8.0 |
| UC-1217 | `opro_score` | 12.8.0 |
| UC-1218 | `opro_append` | 12.8.0 |
| UC-1219 | `opro_best` | 12.8.0 |
| UC-1220 | `opro_loop_plan` | 12.8.0 |
| UC-1221 | `evp_init` | 12.8.0 |
| UC-1222 | `evp_cross` | 12.8.0 |
| UC-1223 | `evp_mutate` | 12.8.0 |
| UC-1224 | `evp_select` | 12.8.0 |
| UC-1225 | `evp_ea` / `evp_loop_plan` | 12.8.0 |
| UC-1226 | `opro_evp_shaped_report` | 12.8.0 |
| UC-1227 | `ptg_gradient` | 12.9.0 |
| UC-1228 | `ptg_edit` | 12.9.0 |
| UC-1229 | `ptg_beam` | 12.9.0 |
| UC-1230 | `ptg_bandit` | 12.9.0 |
| UC-1231 | `ptg_jailbreak` | 12.9.0 |
| UC-1232 | `ptg_loop_plan` | 12.9.0 |
| UC-1233 | `pag_state` | 12.9.0 |
| UC-1234 | `pag_reflect` | 12.9.0 |
| UC-1235 | `pag_expand` | 12.9.0 |
| UC-1236 | `pag_backprop` | 12.9.0 |
| UC-1237 | `pag_expert` / `pag_loop_plan` | 12.9.0 |
| UC-1238 | `ptg_pag_shaped_report` | 12.9.0 |
| UC-1239 | `mapo_posgrad` | 13.0.0 |
| UC-1240 | `mapo_momentum` | 13.0.0 |
| UC-1241 | `mapo_beam` | 13.0.0 |
| UC-1242 | `mapo_ucb` | 13.0.0 |
| UC-1243 | `mapo_faster` | 13.0.0 |
| UC-1244 | `mapo_loop_plan` | 13.0.0 |
| UC-1245 | `grips_seed` | 13.0.0 |
| UC-1246 | `grips_edit` | 13.0.0 |
| UC-1247 | `grips_score` | 13.0.0 |
| UC-1248 | `grips_accept` | 13.0.0 |
| UC-1249 | `grips_api` / `grips_loop_plan` | 13.0.0 |
| UC-1250 | `mapo_grips_shaped_report` | 13.0.0 |
| UC-1251 | `tmpa_state` | 13.1.0 |
| UC-1252 | `tmpa_act` | 13.1.0 |
| UC-1253 | `tmpa_reward` | 13.1.0 |
| UC-1254 | `tmpa_adapt` | 13.1.0 |
| UC-1255 | `tmpa_efficiency` | 13.1.0 |
| UC-1256 | `tmpa_loop_plan` | 13.1.0 |
| UC-1257 | `rlp_init` | 13.1.0 |
| UC-1258 | `rlp_sample` | 13.1.0 |
| UC-1259 | `rlp_reward` | 13.1.0 |
| UC-1260 | `rlp_update` | 13.1.0 |
| UC-1261 | `rlp_discrete` / `rlp_loop_plan` | 13.1.0 |
| UC-1262 | `tmpa_rlp_shaped_report` | 13.1.0 |
| UC-1263 | `aup_template` | 13.2.0 |
| UC-1264 | `aup_trigger` | 13.2.0 |
| UC-1265 | `aup_search` | 13.2.0 |
| UC-1266 | `aup_score` | 13.2.0 |
| UC-1267 | `aup_probe` | 13.2.0 |
| UC-1268 | `aup_loop_plan` | 13.2.0 |
| UC-1269 | `pfx_task` | 13.2.0 |
| UC-1270 | `pfx_prefix` | 13.2.0 |
| UC-1271 | `pfx_optimize` | 13.2.0 |
| UC-1272 | `pfx_generate` | 13.2.0 |
| UC-1273 | `pfx_freeze` / `pfx_loop_plan` | 13.2.0 |
| UC-1274 | `aup_pfx_shaped_report` | 13.2.0 |
| UC-1275 | `ptv_deep` | 13.3.0 |
| UC-1276 | `ptv_inject` | 13.3.0 |
| UC-1277 | `ptv_tune` | 13.3.0 |
| UC-1278 | `ptv_seqtag` | 13.3.0 |
| UC-1279 | `ptv_universal` | 13.3.0 |
| UC-1280 | `ptv_loop_plan` | 13.3.0 |
| UC-1281 | `ptl_soft` | 13.3.0 |
| UC-1282 | `ptl_prepend` | 13.3.0 |
| UC-1283 | `ptl_optimize` | 13.3.0 |
| UC-1284 | `ptl_scale` | 13.3.0 |
| UC-1285 | `ptl_input_only` / `ptl_loop_plan` | 13.3.0 |
| UC-1286 | `ptv_ptl_shaped_report` | 13.3.0 |
| UC-1287 | `msp_soft` | 13.4.0 |
| UC-1288 | `msp_mix` | 13.4.0 |
| UC-1289 | `msp_ensemble` | 13.4.0 |
| UC-1290 | `msp_probe` | 13.4.0 |
| UC-1291 | `msp_underest` | 13.4.0 |
| UC-1292 | `msp_loop_plan` | 13.4.0 |
| UC-1293 | `spot_source` | 13.4.0 |
| UC-1294 | `spot_init` | 13.4.0 |
| UC-1295 | `spot_embed` | 13.4.0 |
| UC-1296 | `spot_retrieve` | 13.4.0 |
| UC-1297 | `spot_vs_tune` / `spot_loop_plan` | 13.4.0 |
| UC-1298 | `msp_spot_shaped_report` | 13.4.0 |
| UC-1299 | `atm_source` | 13.5.0 |
| UC-1300 | `atm_target` | 13.5.0 |
| UC-1301 | `atm_attend` | 13.5.0 |
| UC-1302 | `atm_mix` | 13.5.0 |
| UC-1303 | `atm_modular` | 13.5.0 |
| UC-1304 | `atm_loop_plan` | 13.5.0 |
| UC-1305 | `mptp_shared` | 13.5.0 |
| UC-1306 | `mptp_factor` | 13.5.0 |
| UC-1307 | `mptp_transfer` | 13.5.0 |
| UC-1308 | `mptp_score` | 13.5.0 |
| UC-1309 | `mptp_efficient` / `mptp_loop_plan` | 13.5.0 |
| UC-1310 | `atm_mptp_shaped_report` | 13.5.0 |
| UC-1311 | `lora_freeze` | 13.6.0 |
| UC-1312 | `lora_rank` | 13.6.0 |
| UC-1313 | `lora_train` | 13.6.0 |
| UC-1314 | `lora_merge` | 13.6.0 |
| UC-1315 | `lora_latency` | 13.6.0 |
| UC-1316 | `lora_loop_plan` | 13.6.0 |
| UC-1317 | `adf_extract` | 13.6.0 |
| UC-1318 | `adf_compose` | 13.6.0 |
| UC-1319 | `adf_attend` | 13.6.0 |
| UC-1320 | `adf_score` | 13.6.0 |
| UC-1321 | `adf_nondestruct` / `adf_loop_plan` | 13.6.0 |
| UC-1322 | `lora_adf_shaped_report` | 13.6.0 |
| UC-1323 | `cmp_insert` | 13.7.0 |
| UC-1324 | `cmp_kronecker` | 13.7.0 |
| UC-1325 | `cmp_train` | 13.7.0 |
| UC-1326 | `cmp_score` | 13.7.0 |
| UC-1327 | `cmp_compact` | 13.7.0 |
| UC-1328 | `cmp_loop_plan` | 13.7.0 |
| UC-1329 | `ia3_vector` | 13.7.0 |
| UC-1330 | `ia3_scale` | 13.7.0 |
| UC-1331 | `ia3_train` | 13.7.0 |
| UC-1332 | `ia3_score` | 13.7.0 |
| UC-1333 | `ia3_mixed` / `ia3_loop_plan` | 13.7.0 |
| UC-1334 | `cmp_ia3_shaped_report` | 13.7.0 |
| UC-1335 | `bft_freeze` | 13.8.0 |
| UC-1336 | `bft_bias` | 13.8.0 |
| UC-1337 | `bft_train` | 13.8.0 |
| UC-1338 | `bft_score` | 13.8.0 |
| UC-1339 | `bft_tiny` | 13.8.0 |
| UC-1340 | `bft_loop_plan` | 13.8.0 |
| UC-1341 | `dora_decompose` | 13.8.0 |
| UC-1342 | `dora_magnitude` | 13.8.0 |
| UC-1343 | `dora_direction` | 13.8.0 |
| UC-1344 | `dora_score` | 13.8.0 |
| UC-1345 | `dora_vs_lora` / `dora_loop_plan` | 13.8.0 |
| UC-1346 | `bft_dora_shaped_report` | 13.8.0 |
| UC-1347 | `qlo_quantize` | 13.9.0 |
| UC-1348 | `qlo_nf4` | 13.9.0 |
| UC-1349 | `qlo_adapter` | 13.9.0 |
| UC-1350 | `qlo_score` | 13.9.0 |
| UC-1351 | `qlo_memory` | 13.9.0 |
| UC-1352 | `qlo_loop_plan` | 13.9.0 |
| UC-1353 | `adl_init` | 13.9.0 |
| UC-1354 | `adl_svd` | 13.9.0 |
| UC-1355 | `adl_prune` | 13.9.0 |
| UC-1356 | `adl_score` | 13.9.0 |
| UC-1357 | `adl_adaptive` / `adl_loop_plan` | 13.9.0 |
| UC-1358 | `qlo_adl_shaped_report` | 13.9.0 |
| UC-1359 | `vra_share` | 14.0.0 |
| UC-1360 | `vra_scale` | 14.0.0 |
| UC-1361 | `vra_train` | 14.0.0 |
| UC-1362 | `vra_score` | 14.0.0 |
| UC-1363 | `vra_tiny` | 14.0.0 |
| UC-1364 | `vra_loop_plan` | 14.0.0 |
| UC-1365 | `adp_insert` | 14.0.0 |
| UC-1366 | `adp_drop` | 14.0.0 |
| UC-1367 | `adp_infer` | 14.0.0 |
| UC-1368 | `adp_score` | 14.0.0 |
| UC-1369 | `adp_efficient` / `adp_loop_plan` | 14.0.0 |
| UC-1370 | `vra_adp_shaped_report` | 14.0.0 |
| UC-1371 | `psa_svd` | 14.1.0 |
| UC-1372 | `psa_principal` | 14.1.0 |
| UC-1373 | `psa_residual` | 14.1.0 |
| UC-1374 | `psa_score` | 14.1.0 |
| UC-1375 | `psa_fast` | 14.1.0 |
| UC-1376 | `psa_loop_plan` | 14.1.0 |
| UC-1377 | `dpr_diff` | 14.1.0 |
| UC-1378 | `dpr_mask` | 14.1.0 |
| UC-1379 | `dpr_prune` | 14.1.0 |
| UC-1380 | `dpr_score` | 14.1.0 |
| UC-1381 | `dpr_sparse` / `dpr_loop_plan` | 14.1.0 |
| UC-1382 | `psa_dpr_shaped_report` | 14.1.0 |
| UC-1383 | `tlo_base` | 14.2.0 |
| UC-1384 | `tlo_tie` | 14.2.0 |
| UC-1385 | `tlo_train` | 14.2.0 |
| UC-1386 | `tlo_score` | 14.2.0 |
| UC-1387 | `tlo_efficient` | 14.2.0 |
| UC-1388 | `tlo_loop_plan` | 14.2.0 |
| UC-1389 | `lrp_split` | 14.2.0 |
| UC-1390 | `lrp_ratio` | 14.2.0 |
| UC-1391 | `lrp_train` | 14.2.0 |
| UC-1392 | `lrp_score` | 14.2.0 |
| UC-1393 | `lrp_speed` / `lrp_loop_plan` | 14.2.0 |
| UC-1394 | `tlo_lrp_shaped_report` | 14.2.0 |
| UC-1395 | `lfa_freeze_a` | 14.3.0 |
| UC-1396 | `lfa_train_b` | 14.3.0 |
| UC-1397 | `lfa_merge` | 14.3.0 |
| UC-1398 | `lfa_score` | 14.3.0 |
| UC-1399 | `lfa_memory` | 14.3.0 |
| UC-1400 | `lfa_loop_plan` | 14.3.0 |
| UC-1401 | `dyl_range` | 14.3.0 |
| UC-1402 | `dyl_sample` | 14.3.0 |
| UC-1403 | `dyl_select` | 14.3.0 |
| UC-1404 | `dyl_score` | 14.3.0 |
| UC-1405 | `dyl_searchfree` / `dyl_loop_plan` | 14.3.0 |
| UC-1406 | `lfa_dyl_shaped_report` | 14.3.0 |
| UC-1407 | `lxs_svd` | 14.4.0 |
| UC-1408 | `lxs_r` | 14.4.0 |
| UC-1409 | `lxs_train` | 14.4.0 |
| UC-1410 | `lxs_score` | 14.4.0 |
| UC-1411 | `lxs_tiny` / `lxs_loop_plan` | 14.4.0 |
| UC-1412 | `asy_role` | 14.4.0 |
| UC-1413 | `asy_freeze_a` | 14.4.0 |
| UC-1414 | `asy_train_b` | 14.4.0 |
| UC-1415 | `asy_score` | 14.4.0 |
| UC-1416 | `asy_bound` / `asy_loop_plan` | 14.4.0 |
| UC-1417 | `lxs_asy_shaped_report` | 14.4.0 |
| UC-1418 | `lga_grad` | 14.5.0 |
| UC-1419 | `lga_svd` | 14.5.0 |
| UC-1420 | `lga_scale` | 14.5.0 |
| UC-1421 | `lga_score` | 14.5.0 |
| UC-1422 | `lga_fast` / `lga_loop_plan` | 14.5.0 |
| UC-1423 | `mor_square` | 14.5.0 |
| UC-1424 | `mor_compress` | 14.5.0 |
| UC-1425 | `mor_expand` | 14.5.0 |
| UC-1426 | `mor_score` | 14.5.0 |
| UC-1427 | `mor_merge` / `mor_loop_plan` | 14.5.0 |
| UC-1428 | `lga_mor_shaped_report` | 14.5.0 |
| UC-1429 | `rsl_rank` | 14.6.0 |
| UC-1430 | `rsl_scale` | 14.6.0 |
| UC-1431 | `rsl_train` | 14.6.0 |
| UC-1432 | `rsl_score` | 14.6.0 |
| UC-1433 | `rsl_stable` / `rsl_loop_plan` | 14.6.0 |
| UC-1434 | `lkr_factors` | 14.6.0 |
| UC-1435 | `lkr_kron` | 14.6.0 |
| UC-1436 | `lkr_vectorize` | 14.6.0 |
| UC-1437 | `lkr_score` | 14.6.0 |
| UC-1438 | `lkr_preserve` / `lkr_loop_plan` | 14.6.0 |
| UC-1439 | `rsl_lkr_shaped_report` | 14.6.0 |
| UC-1440 | `lha_pair` | 14.7.0 |
| UC-1441 | `lha_hadamard` | 14.7.0 |
| UC-1442 | `lha_train` | 14.7.0 |
| UC-1443 | `lha_score` | 14.7.0 |
| UC-1444 | `lha_express` / `lha_loop_plan` | 14.7.0 |
| UC-1445 | `fft_basis` | 14.7.0 |
| UC-1446 | `fft_coeff` | 14.7.0 |
| UC-1447 | `fft_idft` | 14.7.0 |
| UC-1448 | `fft_score` | 14.7.0 |
| UC-1449 | `fft_sparse` / `fft_loop_plan` | 14.7.0 |
| UC-1450 | `lha_fft_shaped_report` | 14.7.0 |
| UC-1451 | `had_insert` | 14.8.0 |
| UC-1452 | `had_freeze` | 14.8.0 |
| UC-1453 | `had_train` | 14.8.0 |
| UC-1454 | `had_score` | 14.8.0 |
| UC-1455 | `had_latency` / `had_loop_plan` | 14.8.0 |
| UC-1456 | `rft_repr` | 14.8.0 |
| UC-1457 | `rft_edit` | 14.8.0 |
| UC-1458 | `rft_train` | 14.8.0 |
| UC-1459 | `rft_score` | 14.8.0 |
| UC-1460 | `rft_weightless` / `rft_loop_plan` | 14.8.0 |
| UC-1461 | `had_rft_shaped_report` | 14.8.0 |
| UC-1462 | `oft_ortho` | 14.9.0 |
| UC-1463 | `oft_butterfly` | 14.9.0 |
| UC-1464 | `oft_train` | 14.9.0 |
| UC-1465 | `oft_score` | 14.9.0 |
| UC-1466 | `oft_energy` / `oft_loop_plan` | 14.9.0 |
| UC-1467 | `mss_shard` | 14.9.0 |
| UC-1468 | `mss_share` | 14.9.0 |
| UC-1469 | `mss_train` | 14.9.0 |
| UC-1470 | `mss_score` | 14.9.0 |
| UC-1471 | `mss_pareto` / `mss_loop_plan` | 14.9.0 |
| UC-1472 | `oft_mss_shaped_report` | 14.9.0 |
| UC-1473 | `drl_rank` | 15.0.0 |
| UC-1474 | `drl_mask` | 15.0.0 |
| UC-1475 | `drl_train` | 15.0.0 |
| UC-1476 | `drl_score` | 15.0.0 |
| UC-1477 | `drl_infer` / `drl_loop_plan` | 15.0.0 |
| UC-1478 | `gal_grad` | 15.0.0 |
| UC-1479 | `gal_project` | 15.0.0 |
| UC-1480 | `gal_step` | 15.0.0 |
| UC-1481 | `gal_score` | 15.0.0 |
| UC-1482 | `gal_full` / `gal_loop_plan` | 15.0.0 |
| UC-1483 | `drl_gal_shaped_report` | 15.0.0 |
| UC-1484 | `shr_mask` | 15.1.0 |
| UC-1485 | `shr_tune` | 15.1.0 |
| UC-1486 | `shr_switch` | 15.1.0 |
| UC-1487 | `shr_score` | 15.1.0 |
| UC-1488 | `shr_fusion` / `shr_loop_plan` | 15.1.0 |
| UC-1489 | `wft_wave` | 15.1.0 |
| UC-1490 | `wft_sparse` | 15.1.0 |
| UC-1491 | `wft_idwt` | 15.1.0 |
| UC-1492 | `wft_score` | 15.1.0 |
| UC-1493 | `wft_granular` / `wft_loop_plan` | 15.1.0 |
| UC-1494 | `shr_wft_shaped_report` | 15.1.0 |
| UC-1495 | `lpr_equiv` | 15.2.0 |
| UC-1496 | `lpr_adjust` | 15.2.0 |
| UC-1497 | `lpr_train` | 15.2.0 |
| UC-1498 | `lpr_score` | 15.2.0 |
| UC-1499 | `lpr_bridge` / `lpr_loop_plan` | 15.2.0 |
| UC-1500 | `krl_kron` | 15.2.0 |
| UC-1501 | `krl_lora` | 15.2.0 |
| UC-1502 | `krl_train` | 15.2.0 |
| UC-1503 | `krl_score` | 15.2.0 |
| UC-1504 | `krl_compress` / `krl_loop_plan` | 15.2.0 |
| UC-1505 | `lpr_krl_shaped_report` | 15.2.0 |
| UC-1506 | `mil_svd` | 15.3.0 |
| UC-1507 | `mil_minor` | 15.3.0 |
| UC-1508 | `mil_freeze` | 15.3.0 |
| UC-1509 | `mil_score` | 15.3.0 |
| UC-1510 | `mil_preserve` / `mil_loop_plan` | 15.3.0 |
| UC-1511 | `cda_cov` | 15.3.0 |
| UC-1512 | `cda_mode` | 15.3.0 |
| UC-1513 | `cda_adapt` | 15.3.0 |
| UC-1514 | `cda_score` | 15.3.0 |
| UC-1515 | `cda_forget` / `cda_loop_plan` | 15.3.0 |
| UC-1516 | `mil_cda_shaped_report` | 15.3.0 |
| UC-1517 | `lfq_quant` | 15.4.0 |
| UC-1518 | `lfq_init` | 15.4.0 |
| UC-1519 | `lfq_train` | 15.4.0 |
| UC-1520 | `lfq_score` | 15.4.0 |
| UC-1521 | `lfq_gap` / `lfq_loop_plan` | 15.4.0 |
| UC-1522 | `lds_prelaunch` | 15.4.0 |
| UC-1523 | `lds_tsd` | 15.4.0 |
| UC-1524 | `lds_dash` | 15.4.0 |
| UC-1525 | `lds_score` | 15.4.0 |
| UC-1526 | `lds_impact` / `lds_loop_plan` | 15.4.0 |
| UC-1527 | `lfq_lds_shaped_report` | 15.4.0 |
| UC-1528 | `dlo_adapters` | 15.5.0 |
| UC-1529 | `dlo_delta` | 15.5.0 |
| UC-1530 | `dlo_propagate` | 15.5.0 |
| UC-1531 | `dlo_score` | 15.5.0 |
| UC-1532 | `dlo_highrank` / `dlo_loop_plan` | 15.5.0 |
| UC-1533 | `lon_grad` | 15.5.0 |
| UC-1534 | `lon_align` | 15.5.0 |
| UC-1535 | `lon_train` | 15.5.0 |
| UC-1536 | `lon_score` | 15.5.0 |
| UC-1537 | `lon_immediate` / `lon_loop_plan` | 15.5.0 |
| UC-1538 | `dlo_lon_shaped_report` | 15.5.0 |
| UC-1539 | `olr_qr` | 15.6.0 |
| UC-1540 | `olr_ortho` | 15.6.0 |
| UC-1541 | `olr_train` | 15.6.0 |
| UC-1542 | `olr_score` | 15.6.0 |
| UC-1543 | `olr_stable` / `olr_loop_plan` | 15.6.0 |
| UC-1544 | `lsp_select` | 15.6.0 |
| UC-1545 | `lsp_freeze` | 15.6.0 |
| UC-1546 | `lsp_train` | 15.6.0 |
| UC-1547 | `lsp_score` | 15.6.0 |
| UC-1548 | `lsp_memory` / `lsp_loop_plan` | 15.6.0 |
| UC-1549 | `olr_lsp_shaped_report` | 15.6.0 |
| UC-1550 | `qps_quant` | 15.7.0 |
| UC-1551 | `qps_principal` | 15.7.0 |
| UC-1552 | `qps_train` | 15.7.0 |
| UC-1553 | `qps_score` | 15.7.0 |
| UC-1554 | `qps_error` / `qps_loop_plan` | 15.7.0 |
| UC-1555 | `msl_split` | 15.7.0 |
| UC-1556 | `msl_mixer` | 15.7.0 |
| UC-1557 | `msl_train` | 15.7.0 |
| UC-1558 | `msl_score` | 15.7.0 |
| UC-1559 | `msl_fuse` / `msl_loop_plan` | 15.7.0 |
| UC-1560 | `qps_msl_shaped_report` | 15.7.0 |
| UC-1561 | `ldr_eval` | 15.8.0 |
| UC-1562 | `ldr_keep` | 15.8.0 |
| UC-1563 | `ldr_share` | 15.8.0 |
| UC-1564 | `ldr_score` | 15.8.0 |
| UC-1565 | `ldr_prune` / `ldr_loop_plan` | 15.8.0 |
| UC-1566 | `vbl_bank` | 15.8.0 |
| UC-1567 | `vbl_topk` | 15.8.0 |
| UC-1568 | `vbl_compose` | 15.8.0 |
| UC-1569 | `vbl_score` | 15.8.0 |
| UC-1570 | `vbl_extreme` / `vbl_loop_plan` | 15.8.0 |
| UC-1571 | `ldr_vbl_shaped_report` | 15.8.0 |
| UC-1572 | `opl_proj` | 15.9.0 |
| UC-1573 | `opl_constrain` | 15.9.0 |
| UC-1574 | `opl_train` | 15.9.0 |
| UC-1575 | `opl_score` | 15.9.0 |
| UC-1576 | `opl_forget` / `opl_loop_plan` | 15.9.0 |
| UC-1577 | `gel_idim` | 15.9.0 |
| UC-1578 | `gel_rank` | 15.9.0 |
| UC-1579 | `gel_train` | 15.9.0 |
| UC-1580 | `gel_score` | 15.9.0 |
| UC-1581 | `gel_budget` / `gel_loop_plan` | 15.9.0 |
| UC-1582 | `opl_gel_shaped_report` | 15.9.0 |
| UC-1583 | `geo_dyn` | 16.0.0 |
| UC-1584 | `geo_budget` | 16.0.0 |
| UC-1585 | `geo_train` | 16.0.0 |
| UC-1586 | `geo_score` | 16.0.0 |
| UC-1587 | `geo_ortho` / `geo_loop_plan` | 16.0.0 |
| UC-1588 | `rlo_bases` | 16.0.0 |
| UC-1589 | `rlo_scale` | 16.0.0 |
| UC-1590 | `rlo_train` | 16.0.0 |
| UC-1591 | `rlo_score` | 16.0.0 |
| UC-1592 | `rlo_fullrank` / `rlo_loop_plan` | 16.0.0 |
| UC-1593 | `geo_rlo_shaped_report` | 16.0.0 |
| UC-1594 | `lsh_graph` | 16.1.0 |
| UC-1595 | `lsh_prune` | 16.1.0 |
| UC-1596 | `lsh_recover` | 16.1.0 |
| UC-1597 | `lsh_score` | 16.1.0 |
| UC-1598 | `lsh_footprint` / `lsh_loop_plan` | 16.1.0 |
| UC-1599 | `aop_sub` | 16.1.0 |
| UC-1600 | `aop_alt` | 16.1.0 |
| UC-1601 | `aop_train` | 16.1.0 |
| UC-1602 | `aop_score` | 16.1.0 |
| UC-1603 | `aop_svd` / `aop_loop_plan` | 16.1.0 |
| UC-1604 | `lsh_aop_shaped_report` | 16.1.0 |
| UC-1605 | `lin_tsd` | 16.2.0 |
| UC-1606 | `lin_init` | 16.2.0 |
| UC-1607 | `lin_train` | 16.2.0 |
| UC-1608 | `lin_score` | 16.2.0 |
| UC-1609 | `lin_fast` / `lin_loop_plan` | 16.2.0 |
| UC-1610 | `lnu_act` | 16.2.0 |
| UC-1611 | `lnu_null` | 16.2.0 |
| UC-1612 | `lnu_train` | 16.2.0 |
| UC-1613 | `lnu_score` | 16.2.0 |
| UC-1614 | `lnu_forget` / `lnu_loop_plan` | 16.2.0 |
| UC-1615 | `lin_lnu_shaped_report` | 16.2.0 |
| UC-1616 | `hyd_share` | 16.3.0 |
| UC-1617 | `hyd_heads` | 16.3.0 |
| UC-1618 | `hyd_route` | 16.3.0 |
| UC-1619 | `hyd_score` | 16.3.0 |
| UC-1620 | `hyd_nodomain` / `hyd_loop_plan` | 16.3.0 |
| UC-1621 | `llg_msu` | 16.3.0 |
| UC-1622 | `llg_cluster` | 16.3.0 |
| UC-1623 | `llg_merge` | 16.3.0 |
| UC-1624 | `llg_score` | 16.3.0 |
| UC-1625 | `llg_modular` / `llg_loop_plan` | 16.3.0 |
| UC-1626 | `hyd_llg_shaped_report` | 16.3.0 |
| UC-1627 | `lme_plugin` | 16.4.0 |
| UC-1628 | `lme_balance` | 16.4.0 |
| UC-1629 | `lme_route` | 16.4.0 |
| UC-1630 | `lme_score` | 16.4.0 |
| UC-1631 | `lme_forget` / `lme_loop_plan` | 16.4.0 |
| UC-1632 | `mel_experts` | 16.4.0 |
| UC-1633 | `mel_contrast` | 16.4.0 |
| UC-1634 | `mel_gate` | 16.4.0 |
| UC-1635 | `mel_score` | 16.4.0 |
| UC-1636 | `mel_sparse` / `mel_loop_plan` | 16.4.0 |
| UC-1637 | `lme_mel_shaped_report` | 16.4.0 |
| UC-1638 | `lhb_pool` | 16.5.0 |
| UC-1639 | `lhb_compose` | 16.5.0 |
| UC-1640 | `lhb_adapt` | 16.5.0 |
| UC-1641 | `lhb_score` | 16.5.0 |
| UC-1642 | `lhb_nograd` / `lhb_loop_plan` | 16.5.0 |
| UC-1643 | `mlr_scale` | 16.5.0 |
| UC-1644 | `mlr_init` | 16.5.0 |
| UC-1645 | `mlr_train` | 16.5.0 |
| UC-1646 | `mlr_score` | 16.5.0 |
| UC-1647 | `mlr_demo` / `mlr_loop_plan` | 16.5.0 |
| UC-1648 | `lhb_mlr_shaped_report` | 16.5.0 |
| UC-1649 | `mtl_task` | 16.6.0 |
| UC-1650 | `mtl_spec` | 16.6.0 |
| UC-1651 | `mtl_share` | 16.6.0 |
| UC-1652 | `mtl_score` | 16.6.0 |
| UC-1653 | `mtl_interfere` / `mtl_loop_plan` | 16.6.0 |
| UC-1654 | `mal_mix` | 16.6.0 |
| UC-1655 | `mal_down` | 16.6.0 |
| UC-1656 | `mal_up` | 16.6.0 |
| UC-1657 | `mal_score` | 16.6.0 |
| UC-1658 | `mal_eff` / `mal_loop_plan` | 16.6.0 |
| UC-1659 | `mtl_mal_shaped_report` | 16.6.0 |
| UC-1660 | `lmi_split` | 16.7.0 |
| UC-1661 | `lmi_inner` | 16.7.0 |
| UC-1662 | `lmi_train` | 16.7.0 |
| UC-1663 | `lmi_score` | 16.7.0 |
| UC-1664 | `lmi_tiny` / `lmi_loop_plan` | 16.7.0 |
| UC-1665 | `qdy_range` | 16.7.0 |
| UC-1666 | `qdy_quant` | 16.7.0 |
| UC-1667 | `qdy_train` | 16.7.0 |
| UC-1668 | `qdy_score` | 16.7.0 |
| UC-1669 | `qdy_pick` / `qdy_loop_plan` | 16.7.0 |
| UC-1670 | `lmi_qdy_shaped_report` | 16.7.0 |
| UC-1671 | `lts_tsd` | 16.8.0 |
| UC-1672 | `lts_init` | 16.8.0 |
| UC-1673 | `lts_dash` | 16.8.0 |
| UC-1674 | `lts_score` | 16.8.0 |
| UC-1675 | `lts_combo` / `lts_loop_plan` | 16.8.0 |
| UC-1676 | `slr_pool` | 16.8.0 |
| UC-1677 | `slr_page` | 16.8.0 |
| UC-1678 | `slr_batch` | 16.8.0 |
| UC-1679 | `slr_score` | 16.8.0 |
| UC-1680 | `slr_scale` / `slr_loop_plan` | 16.8.0 |
| UC-1681 | `lts_slr_shaped_report` | 16.8.0 |
| UC-1682 | `cts_collect` | 16.9.0 |
| UC-1683 | `cts_basis` | 16.9.0 |
| UC-1684 | `cts_scale` | 16.9.0 |
| UC-1685 | `cts_score` | 16.9.0 |
| UC-1686 | `cts_cluster` / `cts_loop_plan` | 16.9.0 |
| UC-1687 | `flo_clients` | 16.9.0 |
| UC-1688 | `flo_stack` | 16.9.0 |
| UC-1689 | `flo_agg` | 16.9.0 |
| UC-1690 | `flo_score` | 16.9.0 |
| UC-1691 | `flo_hetero` / `flo_loop_plan` | 16.9.0 |
| UC-1692 | `cts_flo_shaped_report` | 16.9.0 |
| UC-1693 | `pun_backbone` | 17.0.0 |
| UC-1694 | `pun_sgmv` | 17.0.0 |
| UC-1695 | `pun_sched` | 17.0.0 |
| UC-1696 | `pun_score` | 17.0.0 |
| UC-1697 | `pun_multi` / `pun_loop_plan` | 17.0.0 |
| UC-1698 | `mla_pipe` | 17.0.0 |
| UC-1699 | `mla_batch` | 17.0.0 |
| UC-1700 | `mla_train` | 17.0.0 |
| UC-1701 | `mla_score` | 17.0.0 |
| UC-1702 | `mla_eff` / `mla_loop_plan` | 17.0.0 |
| UC-1703 | `pun_mla_shaped_report` | 17.0.0 |
| UC-1704 | `swl_alloc` | 17.1.0 |
| UC-1705 | `swl_switch` | 17.1.0 |
| UC-1706 | `swl_train` | 17.1.0 |
| UC-1707 | `swl_score` | 17.1.0 |
| UC-1708 | `swl_full` / `swl_loop_plan` | 17.1.0 |
| UC-1709 | `col_tune` | 17.1.0 |
| UC-1710 | `col_knot` | 17.1.0 |
| UC-1711 | `col_extend` | 17.1.0 |
| UC-1712 | `col_score` | 17.1.0 |
| UC-1713 | `col_gap` / `col_loop_plan` | 17.1.0 |
| UC-1714 | `swl_col_shaped_report` | 17.1.0 |
| UC-1715 | `dlr_norm` | 17.2.0 |
| UC-1716 | `dlr_bound` | 17.2.0 |
| UC-1717 | `dlr_train` | 17.2.0 |
| UC-1718 | `dlr_score` | 17.2.0 |
| UC-1719 | `dlr_robust` / `dlr_loop_plan` | 17.2.0 |
| UC-1720 | `meo_mini` | 17.2.0 |
| UC-1721 | `meo_diag` | 17.2.0 |
| UC-1722 | `meo_train` | 17.2.0 |
| UC-1723 | `meo_score` | 17.2.0 |
| UC-1724 | `meo_rank` / `meo_loop_plan` | 17.2.0 |
| UC-1725 | `dlr_meo_shaped_report` | 17.2.0 |
| UC-1726 | `rlr_warm` | 17.3.0 |
| UC-1727 | `rlr_merge` | 17.3.0 |
| UC-1728 | `rlr_jagged` | 17.3.0 |
| UC-1729 | `rlr_score` | 17.3.0 |
| UC-1730 | `rlr_high` / `rlr_loop_plan` | 17.3.0 |
| UC-1731 | `eth_plane` | 17.3.0 |
| UC-1732 | `eth_reflect` | 17.3.0 |
| UC-1733 | `eth_train` | 17.3.0 |
| UC-1734 | `eth_score` | 17.3.0 |
| UC-1735 | `eth_plus` / `eth_loop_plan` | 17.3.0 |
| UC-1736 | `rlr_eth_shaped_report` | 17.3.0 |
| UC-1737 | `lco_concepts` | 17.4.0 |
| UC-1738 | `lco_inject` | 17.4.0 |
| UC-1739 | `lco_isolate` | 17.4.0 |
| UC-1740 | `lco_score` | 17.4.0 |
| UC-1741 | `lco_free` / `lco_loop_plan` | 17.4.0 |
| UC-1742 | `car_compress` | 17.4.0 |
| UC-1743 | `car_recon` | 17.4.0 |
| UC-1744 | `car_train` | 17.4.0 |
| UC-1745 | `car_score` | 17.4.0 |
| UC-1746 | `car_mem` / `car_loop_plan` | 17.4.0 |
| UC-1747 | `lco_car_shaped_report` | 17.4.0 |
| UC-1748 | `lrr_pair` | 17.5.0 |
| UC-1749 | `lrr_hyper` | 17.5.0 |
| UC-1750 | `lrr_merge` | 17.5.0 |
| UC-1751 | `lrr_score` | 17.5.0 |
| UC-1752 | `lrr_fast` / `lrr_loop_plan` | 17.5.0 |
| UC-1753 | `svf_svd` | 17.5.0 |
| UC-1754 | `svf_sparse` | 17.5.0 |
| UC-1755 | `svf_train` | 17.5.0 |
| UC-1756 | `svf_score` | 17.5.0 |
| UC-1757 | `svf_geom` / `svf_loop_plan` | 17.5.0 |
| UC-1758 | `lrr_svf_shaped_report` | 17.5.0 |
| UC-1759 | `fly_proj` | 17.6.0 |
| UC-1760 | `fly_topk` | 17.6.0 |
| UC-1761 | `fly_train` | 17.6.0 |
| UC-1762 | `fly_score` | 17.6.0 |
| UC-1763 | `fly_implicit` / `fly_loop_plan` | 17.6.0 |
| UC-1764 | `nla_basis` | 17.6.0 |
| UC-1765 | `nla_coeff` | 17.6.0 |
| UC-1766 | `nla_train` | 17.6.0 |
| UC-1767 | `nla_score` | 17.6.0 |
| UC-1768 | `nla_compact` / `nla_loop_plan` | 17.6.0 |
| UC-1769 | `fly_nla_shaped_report` | 17.6.0 |
| UC-1770 | `mxl_experts` | 17.7.0 |
| UC-1771 | `mxl_route` | 17.7.0 |
| UC-1772 | `mxl_attn` | 17.7.0 |
| UC-1773 | `mxl_score` | 17.7.0 |
| UC-1774 | `mxl_balance` / `mxl_loop_plan` | 17.7.0 |
| UC-1775 | `spr_group` | 17.7.0 |
| UC-1776 | `spr_fold` | 17.7.0 |
| UC-1777 | `spr_factor` | 17.7.0 |
| UC-1778 | `spr_score` | 17.7.0 |
| UC-1779 | `spr_unify` / `spr_loop_plan` | 17.7.0 |
| UC-1780 | `mxl_spr_shaped_report` | 17.7.0 |
| UC-1781 | `tld_tie` | 17.8.0 |
| UC-1782 | `tld_select` | 17.8.0 |
| UC-1783 | `tld_scale` | 17.8.0 |
| UC-1784 | `tld_score` | 17.8.0 |
| UC-1785 | `tld_frac` / `tld_loop_plan` | 17.8.0 |
| UC-1786 | `qal_group` | 17.8.0 |
| UC-1787 | `qal_quant` | 17.8.0 |
| UC-1788 | `qal_adapt` | 17.8.0 |
| UC-1789 | `qal_score` | 17.8.0 |
| UC-1790 | `qal_merge` / `qal_loop_plan` | 17.8.0 |
| UC-1791 | `tld_qal_shaped_report` | 17.8.0 |
| UC-1792 | `ulo_space` | 17.9.0 |
| UC-1793 | `ulo_iso` | 17.9.0 |
| UC-1794 | `ulo_vec` | 17.9.0 |
| UC-1795 | `ulo_score` | 17.9.0 |
| UC-1796 | `ulo_one` / `ulo_loop_plan` | 17.9.0 |
| UC-1797 | `bor_row` | 17.9.0 |
| UC-1798 | `bor_col` | 17.9.0 |
| UC-1799 | `bor_train` | 17.9.0 |
| UC-1800 | `bor_score` | 17.9.0 |
| UC-1801 | `bor_sym` / `bor_loop_plan` | 17.9.0 |
| UC-1802 | `ulo_bor_shaped_report` | 17.9.0 |
| UC-1803 | `qga_weight` | 18.0.0 |
| UC-1804 | `qga_proj` | 18.0.0 |
| UC-1805 | `qga_lazy` | 18.0.0 |
| UC-1806 | `qga_score` | 18.0.0 |
| UC-1807 | `qga_mem` / `qga_loop_plan` | 18.0.0 |
| UC-1808 | `lfw_pool` | 18.0.0 |
| UC-1809 | `lfw_gate` | 18.0.0 |
| UC-1810 | `lfw_token` | 18.0.0 |
| UC-1811 | `lfw_score` | 18.0.0 |
| UC-1812 | `lfw_few` / `lfw_loop_plan` | 18.0.0 |
| UC-1813 | `qga_lfw_shaped_report` | 18.0.0 |
| UC-1814 | `ros_rank` | 18.1.0 |
| UC-1815 | `ros_sparse` | 18.1.0 |
| UC-1816 | `ros_train` | 18.1.0 |
| UC-1817 | `ros_score` | 18.1.0 |
| UC-1818 | `ros_fft` / `ros_loop_plan` | 18.1.0 |
| UC-1819 | `abb_left` | 18.1.0 |
| UC-1820 | `abb_right` | 18.1.0 |
| UC-1821 | `abb_hadamard` | 18.1.0 |
| UC-1822 | `abb_score` | 18.1.0 |
| UC-1823 | `abb_expr` / `abb_loop_plan` | 18.1.0 |
| UC-1824 | `ros_abb_shaped_report` | 18.1.0 |
| UC-1825 | `bha_split` | 18.2.0 |
| UC-1826 | `bha_hadamard` | 18.2.0 |
| UC-1827 | `bha_train` | 18.2.0 |
| UC-1828 | `bha_score` | 18.2.0 |
| UC-1829 | `bha_local` / `bha_loop_plan` | 18.2.0 |
| UC-1830 | `smo_struct` | 18.2.0 |
| UC-1831 | `smo_mod` | 18.2.0 |
| UC-1832 | `smo_train` | 18.2.0 |
| UC-1833 | `smo_score` | 18.2.0 |
| UC-1834 | `smo_rank` / `smo_loop_plan` | 18.2.0 |
| UC-1835 | `bha_smo_shaped_report` | 18.2.0 |
| UC-1836 | `glo_prompt` | 18.3.0 |
| UC-1837 | `glo_scale` | 18.3.0 |
| UC-1838 | `glo_search` | 18.3.0 |
| UC-1839 | `glo_score` | 18.3.0 |
| UC-1840 | `glo_zero` / `glo_loop_plan` | 18.3.0 |
| UC-1841 | `plr_stage` | 18.3.0 |
| UC-1842 | `plr_merge` | 18.3.0 |
| UC-1843 | `plr_reset` | 18.3.0 |
| UC-1844 | `plr_score` | 18.3.0 |
| UC-1845 | `plr_rank` / `plr_loop_plan` | 18.3.0 |
| UC-1846 | `glo_plr_shaped_report` | 18.3.0 |
| UC-1847 | `hir_base` | 18.4.0 |
| UC-1848 | `hir_factors` | 18.4.0 |
| UC-1849 | `hir_hadamard` | 18.4.0 |
| UC-1850 | `hir_score` | 18.4.0 |
| UC-1851 | `hir_merge` / `hir_loop_plan` | 18.4.0 |
| UC-1852 | `cnl_pack` | 18.4.0 |
| UC-1853 | `cnl_fuse` | 18.4.0 |
| UC-1854 | `cnl_train` | 18.4.0 |
| UC-1855 | `cnl_score` | 18.4.0 |
| UC-1856 | `cnl_hw` / `cnl_loop_plan` | 18.4.0 |
| UC-1857 | `hir_cnl_shaped_report` | 18.4.0 |
| UC-1858 | `llr_window` | 18.5.0 |
| UC-1859 | `llr_shift` | 18.5.0 |
| UC-1860 | `llr_lora` | 18.5.0 |
| UC-1861 | `llr_score` | 18.5.0 |
| UC-1862 | `llr_sparse` / `llr_loop_plan` | 18.5.0 |
| UC-1863 | `lis_layers` | 18.5.0 |
| UC-1864 | `lis_sample` | 18.5.0 |
| UC-1865 | `lis_unfreeze` | 18.5.0 |
| UC-1866 | `lis_score` | 18.5.0 |
| UC-1867 | `lis_memory` / `lis_loop_plan` | 18.5.0 |
| UC-1868 | `llr_lis_shaped_report` | 18.5.0 |
| UC-1869 | `nlr_landmark` | 18.6.0 |
| UC-1870 | `nlr_nystrom` | 18.6.0 |
| UC-1871 | `nlr_init` | 18.6.0 |
| UC-1872 | `nlr_score` | 18.6.0 |
| UC-1873 | `nlr_cheap` / `nlr_loop_plan` | 18.6.0 |
| UC-1874 | `rsa_subspace` | 18.6.0 |
| UC-1875 | `rsa_project` | 18.6.0 |
| UC-1876 | `rsa_train` | 18.6.0 |
| UC-1877 | `rsa_score` | 18.6.0 |
| UC-1878 | `rsa_express` / `rsa_loop_plan` | 18.6.0 |
| UC-1879 | `nlr_rsa_shaped_report` | 18.6.0 |
| UC-1880 | `hra_house` | 18.7.0 |
| UC-1881 | `hra_reflect` | 18.7.0 |
| UC-1882 | `hra_train` | 18.7.0 |
| UC-1883 | `hra_score` | 18.7.0 |
| UC-1884 | `hra_ortho` / `hra_loop_plan` | 18.7.0 |
| UC-1885 | `hyb_lora` | 18.7.0 |
| UC-1886 | `hyb_boft` | 18.7.0 |
| UC-1887 | `hyb_fuse` | 18.7.0 |
| UC-1888 | `hyb_score` | 18.7.0 |
| UC-1889 | `hyb_stable` / `hyb_loop_plan` | 18.7.0 |
| UC-1890 | `hra_hyb_shaped_report` | 18.7.0 |
| UC-1891 | `lrt_tensor` | 18.8.0 |
| UC-1892 | `lrt_cp` | 18.8.0 |
| UC-1893 | `lrt_share` | 18.8.0 |
| UC-1894 | `lrt_score` | 18.8.0 |
| UC-1895 | `lrt_compact` / `lrt_loop_plan` | 18.8.0 |
| UC-1896 | `clo_route` | 18.8.0 |
| UC-1897 | `clo_task` | 18.8.0 |
| UC-1898 | `clo_ortho` | 18.8.0 |
| UC-1899 | `clo_score` | 18.8.0 |
| UC-1900 | `clo_forget` / `clo_loop_plan` | 18.8.0 |
| UC-1901 | `lrt_clo_shaped_report` | 18.8.0 |
| UC-1902 | `alo_init` | 18.9.0 |
| UC-1903 | `alo_ablate` | 18.9.0 |
| UC-1904 | `alo_prune` | 18.9.0 |
| UC-1905 | `alo_score` | 18.9.0 |
| UC-1906 | `alo_realloc` / `alo_loop_plan` | 18.9.0 |
| UC-1907 | `lnt_attn` | 18.9.0 |
| UC-1908 | `lnt_scale` | 18.9.0 |
| UC-1909 | `lnt_train` | 18.9.0 |
| UC-1910 | `lnt_score` | 18.9.0 |
| UC-1911 | `lnt_cheap` / `lnt_loop_plan` | 18.9.0 |
| UC-1912 | `alo_lnt_shaped_report` | 18.9.0 |
| UC-1913 | `lfu_split` | 18.10.0 |
| UC-1914 | `lfu_fuse` | 18.10.0 |
| UC-1915 | `lfu_batch` | 18.10.0 |
| UC-1916 | `lfu_score` | 18.10.0 |
| UC-1917 | `lfu_speed` / `lfu_loop_plan` | 18.10.0 |
| UC-1918 | `ter_tucker` | 18.10.0 |
| UC-1919 | `ter_freeze` | 18.10.0 |
| UC-1920 | `ter_scale` | 18.10.0 |
| UC-1921 | `ter_score` | 18.10.0 |
| UC-1922 | `ter_highrank` / `ter_loop_plan` | 18.10.0 |
| UC-1923 | `lfu_ter_shaped_report` | 18.10.0 |
| UC-1924 | `tnl_stack` | 18.11.0 |
| UC-1925 | `tnl_tucker` | 18.11.0 |
| UC-1926 | `tnl_mode` | 18.11.0 |
| UC-1927 | `tnl_score` | 18.11.0 |
| UC-1928 | `tnl_budget` / `tnl_loop_plan` | 18.11.0 |
| UC-1929 | `azt_tt` | 18.11.0 |
| UC-1930 | `azt_ff` | 18.11.0 |
| UC-1931 | `azt_query` | 18.11.0 |
| UC-1932 | `azt_score` | 18.11.0 |
| UC-1933 | `azt_mem` / `azt_loop_plan` | 18.11.0 |
| UC-1934 | `tnl_azt_shaped_report` | 18.11.0 |
| UC-1935 | `fct_tensor` | 18.12.0 |
| UC-1936 | `fct_tt` | 18.12.0 |
| UC-1937 | `fct_tucker` | 18.12.0 |
| UC-1938 | `fct_score` | 18.12.0 |
| UC-1939 | `fct_tiny` / `fct_loop_plan` | 18.12.0 |
| UC-1940 | `ltr_stack` | 18.12.0 |
| UC-1941 | `ltr_core` | 18.12.0 |
| UC-1942 | `ltr_share` | 18.12.0 |
| UC-1943 | `ltr_score` | 18.12.0 |
| UC-1944 | `ltr_deep` / `ltr_loop_plan` | 18.12.0 |
| UC-1945 | `fct_ltr_shaped_report` | 18.12.0 |
| UC-1946 | `cra_mha` | 18.13.0 |
| UC-1947 | `cra_ffn` | 18.13.0 |
| UC-1948 | `cra_cpd` | 18.13.0 |
| UC-1949 | `cra_score` | 18.13.0 |
| UC-1950 | `cra_heads` / `cra_loop_plan` | 18.13.0 |
| UC-1951 | `ltt_adp` | 18.13.0 |
| UC-1952 | `ltt_rep` | 18.13.0 |
| UC-1953 | `ltt_tt` | 18.13.0 |
| UC-1954 | `ltt_score` | 18.13.0 |
| UC-1955 | `ltt_tiny` / `ltt_loop_plan` | 18.13.0 |
| UC-1956 | `cra_ltt_shaped_report` | 18.13.0 |
| UC-1957 | `c3a_kernel` | 18.14.0 |
| UC-1958 | `c3a_circ` | 18.14.0 |
| UC-1959 | `c3a_fft` | 18.14.0 |
| UC-1960 | `c3a_score` | 18.14.0 |
| UC-1961 | `c3a_rank` / `c3a_loop_plan` | 18.14.0 |
| UC-1962 | `bof_block` | 18.14.0 |
| UC-1963 | `bof_orth` | 18.14.0 |
| UC-1964 | `bof_butter` | 18.14.0 |
| UC-1965 | `bof_score` | 18.14.0 |
| UC-1966 | `bof_full` / `bof_loop_plan` | 18.14.0 |
| UC-1967 | `c3a_bof_shaped_report` | 18.14.0 |
| UC-1968 | `sdt_dim` | 18.15.0 |
| UC-1969 | `sdt_mask` | 18.15.0 |
| UC-1970 | `sdt_tune` | 18.15.0 |
| UC-1971 | `sdt_score` | 18.15.0 |
| UC-1972 | `sdt_ssm` / `sdt_loop_plan` | 18.15.0 |
| UC-1973 | `mef_adapt` | 18.15.0 |
| UC-1974 | `mef_route` | 18.15.0 |
| UC-1975 | `mef_fetch` | 18.15.0 |
| UC-1976 | `mef_score` | 18.15.0 |
| UC-1977 | `mef_cpu` / `mef_loop_plan` | 18.15.0 |
| UC-1978 | `sdt_mef_shaped_report` | 18.15.0 |
