# Stele Roadmap

Phases, in order. A phase does not start until the previous one's gate clears.
The [system intent](stele_system_intent.yaml) is the contract for all of them;
its joint-satisfaction test gates every implementation phase.

## Phase 0 — Research + design intent ✅ (current)

- ✅ Source-audited research: inference-time ledgers ([`docs/research/`](docs/research/))
- ✅ Source-audited research: memory storage landscape
- ✅ Distilled pattern file ([`docs/patterns/`](docs/patterns/)): 13 foundational findings, 12 operational patterns, contested and not-supported claims
- ✅ System intent with 7 constraints, satisfiability analysis, and planned test paths
- ✅ PRD ([`docs/PRD.md`](docs/PRD.md)): 12 pains → 12 use cases → functional requirements by plane → success metrics → open questions blocking the tech spec
- ✅ Tech spec ([`docs/TECH_SPEC.md`](docs/TECH_SPEC.md)): resolves all six open questions — file SoT + journal, typed oracle evidence, named MCP tools, three-rung scope taxonomy, surface-only conflict handling, migration producer — plus storage layout, schema, state machine, retrieval pipeline, pack format, and the fixed test paths
- ⏳ **Gate:** human review and sign-off of the intent (PENDING_SIGNOFF)

## Phase 1 — Contract + store core

- Entry schema (content layers, bi-temporal metadata, scope tag, provenance) as code
- File-based inspectable source of truth; byte-stable serialization
- The six ops (`ADD · UPDATE · DELETE/SUPERSEDE · SEARCH · REFLECT · LINK`) as a pure library
- Purity tests: zero LLM / zero network on the core write path; static import scan
- **Gate:** schema + governance constraint tests green (C5, C6, C7)

## Phase 2 — Governance runtime

- Quarantine → promote lifecycle with oracle-evidence contract
- Batched REFLECT pass: dedupe, merge, supersede, expire — provenance-preserving
- Oracle adapter interface (EIF as the first candidate adapter)
- **Gate:** "self-graded never promotes" test green; REFLECT differential tests green

## Phase 3 — Tool surface + retrieval

- MCP server exposing the six ops
- Hybrid retrieval (keyword + semantic via caller-supplied embedder + temporal filter) over promoted entries only
- Derived-index rebuild guarantees (lossless; C4 differential test)
- Cairn adapter: Stele as a store behind Cairn's selective retrieval gate
- **Gate:** quarantine-never-served and index-rebuild tests green

## Phase 4 — Producers + seed corpus

- IVD Judgment producer adapter (protocol-only)
- Migration tooling for existing per-project feedback files → seed corpus (scope-tagged, quarantined, then reviewed)
- **Gate:** joint-satisfaction lifecycle test green end-to-end

## Phase 5 — Pack export + evaluation

- AMP-shaped pack export: redact at export, version + expiry stamps, purpose scoping, audience tiers, adaptation operators
- Task-outcome evaluation harness (agents with vs. without Stele on lesson-dependent tasks) — the only acceptance evidence for value claims
- **Gate:** export property tests green; eval harness produces its first honest numbers (whatever they are)

## Explicitly out of scope (all phases)

- Training-time memory of any kind
- LLM extraction on the write path
- Owning a database engine
- Product/pricing for experience packs
