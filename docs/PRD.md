# Stele — Product Requirements Document

**Version:** 0.1.2 · **Date:** 2026-07-17 · **Status:** Draft (use-cases phase)
**License:** MIT · Copyright (c) 2026 Leo Celis — https://leocelis.com
**Built with / verified by:** IVD — https://ivdframework.dev

**Derived from:** `stele_system_intent.yaml` v0.1.1 · `docs/patterns/patterns_session_ledger_memory.yaml` v1.2 · `docs/research/**`

> Every pain point and every solution below cites the research that grounds it. References use the form (FF-xx / OP-xx; DOC_NAME). Pattern IDs resolve in `docs/patterns/patterns_session_ledger_memory.yaml`; DOC_NAMEs resolve in `docs/research/`.

---

## 1. Overview

Stele is a governed experiential-memory ledger for AI agents. Agents log what worked and what failed on each task; a quarantine gate promotes only lessons backed by external evidence; and any agent retrieves the distilled, still-valid experience through one protocol before its next task.

Stele is **not** a database product, **not** an LLM extraction pipeline, and **not** a retrieval router. It is the store + contract + governance layer for one kind of knowledge — *experiential memory* (what happened during tasks: successes, failures, decisions, dead ends; Hu et al., arXiv:2512.13564) — with **zero LLM calls and zero network on the core write path** (intent C5).

---

## 2. Who this is for

Anyone running agents that repeat classes of tasks and keep re-learning the same lessons:

- **Operators of multiple agents** across projects, who watch one agent make a mistake another agent solved last week.
- **Agent developers** whose per-project feedback files, handoffs, and postmortems hold real knowledge that no agent ever retrieves at the right moment.
- **Framework authors** who need a governed place to ship codified corrections (e.g., IVD's Judgment layer) so future intent is written by an agent that has lived through prior mistakes.
- **Privacy-conscious teams** who need memory that can prove erasure and never leaks a session's secrets into a shared store.

The common thread: agent sessions already produce the most valuable, most specific knowledge a system has — and today it is thrown away or scattered (FF-1; AGENT_SESSION_LEDGER research, Executive summary).

---

## 3. The problem

The mechanism is proven: a frozen model + agent tools + an external, tool-updated ledger measurably improves outcomes — Reflexion, ExpeL, AWM, CER, Hindsight, across benchmarks, with no weight updates (FF-1). But every naive implementation of "just remember things" fails in a documented way:

- **Dump the transcript** → context rot and negative transfer (FF-2, FF-4).
- **Auto-extract facts on write** → hallucinated memories, silent overwrites, poisoned stores (OP-4, FF-12).
- **Let the agent grade itself** → confirmation bias ratified into long-term memory (OP-2).
- **Append forever** → stale lessons actively mislead later tasks (FF-8).
- **Validate with recall Q&A** → false confidence; recall wins do not transfer to agentic action (FF-5).

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

---

## 5. Use cases

> **Stele's planes:** **K** Contract (schema) · **T** Tool surface (six ops) · **G** Governance (quarantine → promote → REFLECT) · **R** Retrieval · **X** Export. (intent §architecture)

### UC-1 — Auto-log a task outcome without poisoning the store
- **Scenario:** An agent finishes a task and logs "pinning the cache key to a calendar bucket fixed the stale reads."
- **Pain today (P3, P4):** Either the lesson lands unverified in long-term memory (poison) or it lands nowhere (P1).
- **Stele solution:** **T** `ADD` accepts only structured, distilled entries (C5, C6) into **G** quarantine — durable immediately, retrievable never, until promoted (C7). Capture cost is the agent's, not the human's (mitigates P12; FF-6).
- **Requirement:** `add(entry) → {id, state: quarantined}`; schema-incomplete entries rejected at the boundary.

### UC-2 — Promote only lessons that survived an external oracle
- **Scenario:** The same lesson later carries a passing regression test and a production log line as evidence.
- **Pain today (P3):** No memory layer distinguishes "agent believes it" from "evidence shows it."
- **Stele solution:** **G** promotion requires oracle evidence attached to the entry — test result, env feedback, independent judge, or human sign-off (C7; OP-2, OP-4). A self-grade can never promote, by construction.
- **Requirement:** `promote(id, evidence) → promoted | rejected{reason}`; evidence contract pluggable (EIF adapter is one implementation).

### UC-3 — Retrieve relevant experience before a task
- **Scenario:** An agent about to touch a caching layer asks: "what do we know about cache-key mistakes?"
- **Pain today (P6, P10):** Whole-ledger dumps rot context; irrelevant memories actively hurt.
- **Stele solution:** **R** hybrid search (keyword + semantic + temporal) over promoted entries only, filtered by scope and validity, injected as a budgeted slice (C2; OP-9 Compress). Returning nothing is a first-class answer; possibly-stale entries carry an explicit flag (FF-8, abstention).
- **Requirement:** `search(query, consumer_scope, budget, as_of?) → slices[] | ∅`, each slice carrying validity, staleness, and (when `as_of` is set) an explicit historical-state flag (TECH_SPEC §6.1).

### UC-4 — Supersede a stale lesson without losing history
- **Scenario:** The library upgraded; the old lesson is now wrong for v2 but was true for v1.
- **Pain today (P5):** Overwrite loses the history; append-only serves the poison.
- **Stele solution:** **K** bi-temporal metadata (`valid_from`, `superseded_by`, `last_verified`, `expiry`) with **T** `SUPERSEDE` — invalidate, not overwrite (C6; Zep/Graphiti semantics, arXiv:2501.13956 §2).
- **Requirement:** `supersede(old_id, new_entry)`; point-in-time reads (`search(..., as_of=t)`) answer "what did we believe when?" and return the historical entry explicitly flagged as such — never presented as current (closes the loop on the "zero unflagged expired/superseded" success metric, §8).

### UC-5 — Erase on demand, provably
- **Scenario:** Two distinct triggers, same mechanism: (a) a subject (person, client, project) must be removed from the ledger — including from every index; (b) a single entry turns out to be a wrong lesson and must be truly gone, not just superseded.
- **Pain today (P8):** Embeddings and derived indexes silently retain what the store deleted; SUPERSEDE alone cannot satisfy either trigger — it invalidates, it does not erase.
- **Stele solution:** **T** `DELETE` (true erase, distinct from SUPERSEDE) keyed on either the mandatory subject/owner id or a specific entry id (C6; OP-3, FF-9 — "erasure and wrong lessons" are both DELETE's job); every index is derived and rebuildable, so erasure propagates by rebuild (C4).
- **Requirement:** `delete(subject_id | entry_id)` cascades; a post-delete index rebuild contains zero traces (joint test asserts this).

### UC-6 — Consolidate a growing ledger
- **Scenario:** After months of auto-logging, the ledger holds duplicates, near-duplicates, and expired entries.
- **Pain today (P5, P12):** Unmaintained memory decays into noise; per-entry human review kills adoption.
- **Stele solution:** **G** batched `REFLECT` pass — dedupe, merge, supersede, expire, surface conflicts — provenance-preserving (C7; OP-3; Memory-R1: maintenance policy matters).
- **Requirement:** `reflect() → ReflectReport{merged[], expired[], conflicts[], dangling_links[]}` (TECH_SPEC §5.3); runs batched, never blocks writes.

### UC-7 — Reuse across projects without negative transfer
- **Scenario:** A lesson learned in project A is relevant to project B — but A's exact commands would break B.
- **Pain today (P7, P2):** Trajectory-level reuse anchors the consumer to the wrong context.
- **Stele solution:** **K** mandatory abstraction scope — three rungs, `universal` · `domain:<name>` · `project:<name>` — filtered at retrieval (C2, C6)¹; workflow/skill entries declare environment assumptions so consumers can env-check before replaying (FF-4 gate).
- **Requirement:** Scope is a schema field, not a convention; cross-scope reads require an explicit override, never the default.

  ¹ *Refines the intent's illustrative two-value enum (`universal_insight | project_scoped`, C6) after resolving PRD §9 Q4 — the MTL ladder (FF-3) has more than two rungs. Resolution and exact literal values: [`TECH_SPEC.md`](TECH_SPEC.md) §4.3.*

### UC-8 — Answer the reuser's real questions
- **Scenario:** A consumer asks *why* an approach was rejected and what test proves the chosen one.
- **Pain today (P11):** Rationale documents alone answered <50% of reuser questions (Karsenty).
- **Stele solution:** **K/T** entries record rejected options (IBIS lineage, FF-7) and `LINK` to artifacts, tests, and source sessions (C6; FF-2 gist→source pointer).
- **Requirement:** `link(entry_id, artifact_ref, kind)`; retrieval returns links alongside content.

### UC-9 — Ingest from heterogeneous producers
- **Scenario:** IVD's Judgment layer, per-project feedback files, and session handoffs all want to feed the ledger — possibly at the same time.
- **Pain today (P9):** Merging codebases or granting store internals to producers couples everything to everything; concurrent writers can also physically corrupt a naive store.
- **Stele solution:** **K** every producer — including the IVD adapter — writes through the same six-op protocol; core imports none of their code (C1; memorywire lesson, OP-6). Writes are serialized (single-writer lock + atomic rename, TECH_SPEC §3.3) so concurrent producers cannot corrupt the store; logical conflicts (contradictory lessons) still surface at REFLECT, never silently (C6; mitigates P9).
- **Requirement:** Protocol is the only write path; a static import scan enforces core purity; concurrent writes never corrupt an entry.

### UC-10 — Sit behind a retrieval router
- **Scenario:** A host already uses Cairn to decide *whether* and *how* to retrieve.
- **Pain today:** Memory layers that bundle their own routing fight the router.
- **Stele solution:** Stele stores and serves; Cairn (or any router) fronts it as one more backend (C1; intent §ecosystem_linkage). Complementary by construction: Cairn owns routing, Stele owns the store.
- **Requirement:** `search()` is callable as a pure backend signal — no side effects, deterministic given store state.

### UC-11 — Export a pack for a different audience
- **Scenario:** A team wants the distilled "build a database" experience — without the originating team's secrets or env specifics.
- **Pain today (P2; FF-9):** Sharing a live store or raw trajectories leaks secrets trajectory-level and transfers badly.
- **Stele solution:** **X** pack export: Insight/skill/workflow layers + issue trail + provenance, redacted at export, version- and expiry-stamped, audience-tiered with adaptation operators; recipe layer, never equipment layer (C3; FF-10, FF-7, FF-13). Storage ≠ pack. Expiry stamps + staleness abstention are also the wrong-lesson liability hedge (intent §failure_mode_coverage): no case law exists on bad-lesson liability, so packs must carry their own "may be outdated" signal, revisited before any pack crosses an internal boundary.
- **Requirement:** `export(scope, audience, purpose) → pack`; property tests: no secrets, no top-level trajectories, stamps present.

### UC-12 — Prove the ledger helps, honestly
- **Scenario:** Does retrieval-before-task actually improve outcomes, or does it just feel good?
- **Pain today (P6):** Recall Q&A over the store proves nothing about action.
- **Stele solution:** Task-outcome harness: agents on lesson-dependent tasks with vs. without Stele (intent §success_oracle; FF-5; OP-12 proposed eval). Value claims wait for these numbers, whatever they are.
- **Requirement:** Reproducible eval harness in-repo; a recall benchmark is explicitly not acceptance evidence.

---

## 6. Functional requirements (by plane)

| Plane | Requirement | Source |
|---|---|---|
| **K — Schema** | Content layers (goal/issue/decision/failure-lesson/workflow/skill) incl. rejected options; bi-temporal fields; three-rung scope tag (`universal` / `domain:<name>` / `project:<name>` — refines C6's illustrative enum, see UC-7¹); provenance (agent, task, env, subject_id, oracle pointer, source pointer); env assumptions on workflow entries; incomplete entries rejected at ADD | C6; OP-1, FF-7, FF-8, FF-9, FF-2 |
| **T — Six ops** | `ADD · UPDATE · DELETE/SUPERSEDE · SEARCH · REFLECT · LINK` as library + MCP server; the only read/write path (`promote` is a governed `UPDATE` exposed as a convenience wrapper — the contract stays six ops, TECH_SPEC §5.1/§7) | C1; OP-3 |
| **G — Quarantine** | Writes quarantined; promotion only with external-oracle evidence; self-grade never promotes; oracle adapter interface | C7; OP-2, OP-4 |
| **G — REFLECT** | Batched consolidation: dedupe/merge/supersede/expire; provenance-preserving; conflict surfacing | C7; OP-3; Memory-R1 |
| **R — Retrieval** | Hybrid keyword + semantic (caller-supplied embedder) + temporal; promoted-only; scope + validity filters; budgeted slices; staleness flags; ∅ is a valid result | C2; OP-9, FF-5, FF-8 |
| **X — Export** | Redact-at-export; version + expiry stamps; purpose scoping; audience tiers; adaptation operators; recipe-not-equipment | C3; OP-6, FF-9, FF-10, FF-13 |
| **Cross-cutting** | Inspectable file-exportable SoT; all indexes derived + losslessly rebuildable; zero LLM / zero network on core write path; no imports from IVD/Cairn/EIF/DB drivers in core | C4, C5, C1; OP-5, FF-11 |

**Context-operator coverage** (intent §architecture; OP-9): the four context-engineering operators all land on a plane — **Write** = the six ops (producers append/update outside the window) · **Select** = retrieval plane (promoted slices only) · **Compress** = budgeted injection at read time + REFLECT consolidation at rest · **Isolate** = scope/namespace on every entry; producers write into their scope, cross-scope reads are explicit. A ledger with Write but no Select is a write-only log; Select without Compress re-creates context rot.

**Priority on conflict** (intent §constraint_satisfiability): when requirements collide during implementation, governance and schema integrity win over convenience — **C7 > C6 > C5 > C4 > C2 > C3 > C1**.

---

## 7. Non-goals (out of scope)

- **Not training-time memory.** No fine-tuning, no LoRA, no weight updates — the context level is the whole game (intent §meta.layer).
- **Not a database engine.** The substrate stays boring and swappable; the protocol is the product (FF-11 selection rule).
- **Not an extraction pipeline.** Writers distill; Stele governs. Adding LLM extraction to the core is explicitly forbidden even as a remedy for lazy producers (intent R4).
- **Not a retrieval router.** Whether/how to retrieve is the caller's (or Cairn's) decision; Stele serves what was asked.
- **Not a replacement for IVD, Cairn, or EIF.** Stele composes with them over protocol boundaries only — IVD stays the intent/judgment framework, Cairn stays the router, EIF stays the verifier (intent §ecosystem_linkage; CoALA separates memory modules from decision procedures).
- **Not generic document RAG.** A ledger is written *during* the work, *by* the worker — retrieval over a static corpus nobody writes back to is a different problem with different tools (OP-9 scope note).
- **Not a conversation-health monitor.** Turn-level fidelity is Horizon's domain — orthogonal (OP-8).
- **Product/SKU/pricing for packs:** out of scope for this repository.

### 7.1 When Stele is not the right choice

- **Chat personalization at scale** ("remember the user likes short answers") — an extract-and-retrieve layer (Mem0-class) is simpler and fits; Stele's governance is overhead there.
- **Entity-centric world state with rich temporal queries across millions of facts** — a temporal knowledge graph (Zep/Graphiti) is built for that write path; Stele deliberately is not.
- **Thread-scoped scratchpads** — framework checkpoints (e.g., LangGraph) already do this; Stele is long-term memory, not working memory.

---

## 8. Success metrics

From `stele_system_intent.yaml` §success_oracle and constraints, made measurable by UC-12:

- **Outcome value:** agents on lesson-dependent tasks perform measurably better with Stele retrieval than without (task-outcome harness; never recall Q&A).
- **Governance integrity:** zero self-graded entries in the promoted tier; every promoted entry carries oracle evidence — the append-only ops journal (TECH_SPEC §3.1) is the audit trail that makes this checkable, not just claimed.
- **Temporal safety:** zero expired/superseded entries served unflagged.
- **Erasure:** subject-keyed delete + index rebuild leaves zero traces (differential test).
- **Purity:** core write path issues zero LLM/network calls (counting embedder + sockets-disabled tests); core imports no ecosystem/DB code (static scan).
- **Portability:** SoT exports to inspectable files; a from-scratch index rebuild reproduces byte-identical retrieval results.
- **Cost:** retrieval injection stays within its declared budget, and the harness measures the ledger's latency/token overhead alongside its outcome value — inject cost is an accepted trade only while it is measured (intent §failure_mode_coverage). The measurement harness ships with the Phase 5 evaluation work (ROADMAP; TECH_SPEC §10) — tracked, not silently dropped.
- **Adoptability:** clone → install → quickstart with no cloud account, no API key, on the default path.
- **Joint satisfaction (the completion gate):** one lifecycle test asserts all seven constraints on the same store state — ADD (structured, quarantined) → oracle promote → filtered retrieval with staleness flags → lossless index rebuild → redacted tiered export → subject-keyed DELETE with erasure cascade → core purity scan. No implementation phase is complete while it is red (intent §constraint_satisfiability.joint_satisfaction_test).

---

## 9. Open questions (block tech spec)

> **Status:** all six resolved in [`TECH_SPEC.md`](TECH_SPEC.md) §1 — kept here for the record of what had to be decided.

1. **Substrate for v1 SoT:** plain files vs. embedded DB (e.g., SQLite) with file export — both satisfy C4; pick on write-concurrency needs (P9) at Phase 1 start.
2. **Oracle evidence format:** minimum viable evidence contract (typed result? URI + hash? signed attestation?) — must be strict enough to block self-grades, loose enough for human sign-off.
3. **MCP surface shape:** six named tools vs. one tool with an `op` parameter — decide against MCP client ergonomics.
4. **Scope taxonomy:** is the binary `universal_insight | project_scoped` enough, or does a domain tier belong between them? (FF-3 suggests the ladder has more rungs.)
5. **REFLECT conflict semantics:** merge policy when two agents promote contradictory lessons — surface-only in v1 (per R2), but the resolution UX needs design.
6. **Seed migration:** mapping existing per-project feedback files into the schema (which fields are recoverable, which default) — Phase 4 input.

---

## 10. References

- `stele_system_intent.yaml` — constraints C1–C7, architecture, ecosystem linkage, failure-mode coverage
- `docs/patterns/patterns_session_ledger_memory.yaml` — FF-1..13, OP-1..12, contested + not-supported registers
- `docs/research/AGENT_SESSION_LEDGER_INFERENCE_TIME_MEMORY_RESEARCH_2026.md` — mechanism, transfer, privacy, staleness, capture-cost history
- `docs/research/AGENT_MEMORY_STORAGE_SYSTEMS_RESEARCH_2026.md` — substrate families, write policies, product landscape, cost shapes
- Ecosystem: [IVD](https://github.com/leocelis/ivd) · [Cairn](https://github.com/leocelis/cairn) · [EIF](https://github.com/leocelis/eif)
