# Stele — Technical Specification

**Version:** 0.1.1 · **Date:** 2026-07-17 · **Status:** Draft — implements nothing yet; every decision here is held to the intent's constraints
**Derived from:** `stele_system_intent.yaml` v0.1.1 · `docs/PRD.md` v0.1.1 (resolves its §9 open questions) · `docs/patterns/patterns_session_ledger_memory.yaml` v1.2

> Constraint references (C1–C7) resolve in the intent; pattern references (FF-xx / OP-xx) in the patterns file. Where this spec and the intent conflict, the intent wins, in its stated priority order: **C7 > C6 > C5 > C4 > C2 > C3 > C1**.

---

## 1. Decisions on the PRD's open questions

| # | Question | Decision |
|---|---|---|
| Q1 | Substrate for v1 SoT | **Entry-per-file JSON store + append-only ops journal** (§3). Files are the SoT (C4); SQLite enters later only as a *derived* index if scale demands it — never as truth |
| Q2 | Oracle evidence format | **Typed evidence records with local digest verification** (§5.2). Structural validation in core; no network. Self-assertions are unrepresentable as valid evidence |
| Q3 | MCP surface shape | **Named tools** (§7): eight tools that all compile to the six contract ops. Discoverability for agents beats parameter dispatch |
| Q4 | Scope taxonomy | **Three rungs:** `universal` · `domain:<name>` · `project:<name>` (§4.3). The MTL abstraction ladder (FF-3) has more than two rungs; retrieval filters respect the hierarchy |
| Q5 | REFLECT conflict semantics | **Surface, never auto-resolve** (§6.3). Conflicting promoted entries are flagged `contested`, served with the flag, resolved only by an evidenced supersede |
| Q6 | Seed migration | **Migration producer** (§8.3): feedback files → quarantined entries with `provenance.agent = "migration"`, batch-reviewed for promotion. Phase 4 |

---

## 2. Package layout (monorepo, Cairn mold)

```
packages/
  stele-core/          # schema, store, six ops, governance, retrieval, export
    src/stele_core/
      schema.py        # entry model, canonical serialization, validation
      store.py         # file SoT + journal + locking
      ops.py           # add / update / supersede / delete / search / reflect / link
      governance.py    # quarantine → promote state machine; evidence validation
      retrieval.py     # hybrid search, filters, budgeter
      index/           # derived indexes: lexical (pure-Python BM25), semantic (callable), temporal
      export.py        # pack builder + redaction pipeline
      adapters.py      # Protocols: OracleAdapter, Embedder, SearchBackend (Cairn-facing)
    intents/           # module intents (one per module, written at implementation time)
    tests/
  stele-mcp/           # MCP server wrapping stele-core (stdio transport)
    src/stele_mcp/server.py
    tests/
```

- `stele-core`: **zero runtime dependencies** (stdlib only), zero network, zero LLM (C5, C1). Python 3.11–3.13.
- `stele-mcp`: depends on `stele-core` + an MCP server library only.
- No package imports IVD/Cairn/EIF/DB drivers (C1; enforced by `tests/test_purity.py::test_core_static_import_scan`).
- **Permanent boundary, not a Phase 1 default (intent R4):** if producers systematically under-distill, the fix is a distillation-quality check in the oracle-evidence contract (§5.2) — never LLM extraction added to `stele-core`. C5 does not soften as the project matures.
- **Test path note:** the fixed test paths in §9 (as written in the intent, e.g. `tests/test_purity.py::...`) resolve under `packages/stele-core/tests/` in this layout; `stele-mcp`'s own tests live under `packages/stele-mcp/tests/`.

---

## 3. Storage layer (SoT — C4, C5)

### 3.1 On-disk layout

```
<store_root>/
  stele.json                # store manifest: schema_version, store_id, created_at
  journal.ndjson            # append-only op log: {op, entry_id, actor, ts, payload_digest}
  entries/
    quarantine/<id>.json    # one canonical JSON file per entry
    promoted/<id>.json
  attachments/<digest>      # optional evidence/artifact blobs, content-addressed
  index/                    # DERIVED, rebuildable, deletable (C4)
    lexical/  semantic/  temporal/
```

`journal.ndjson` is the audit trail: every ADD/UPDATE/PROMOTE/SUPERSEDE/DELETE/REFLECT is an immutable, timestamped, actor-attributed line. It is what makes PRD §8's "auditable" governance-integrity metric checkable rather than asserted.

### 3.2 Determinism and identity

- **Canonical serialization:** JSON, UTF-8, sorted keys, `\n` line endings, no floats for money/scores (use strings/ints) — byte-stable across runs and platforms (Cairn precedent).
- **Entry id:** `se_<first 16 hex of sha256(canonical entry minus id/state fields)>`. Content-derived → identical lessons dedupe structurally; no wall-clock in the id.
- **Timestamps:** always caller-supplied ISO-8601 UTC (the store never reads the clock) — keeps replays byte-identical and testable.

### 3.3 Concurrency (PRD P9, risk R2)

- Single-writer discipline: an advisory lock file (`.lock`, atomic `O_EXCL` create) guards mutation; writes are staged to a temp file and `rename()`d (atomic on POSIX).
- Multi-agent deployments serialize writes through the MCP server (one server per store). Cross-process readers need no lock (immutable entry files + journal replay).
- Conflicts between *logical* writers (two agents, contradictory lessons) are not a locking problem — they surface at REFLECT (§6.3).

### 3.4 Erasure (C6, UC-5)

`DELETE(subject_id | entry_id)`:
1. journal records the deletion (id + reason, no content);
2. entry file and its attachments are removed;
3. every index directory is rebuilt from surviving entries (derived-only guarantee makes this lossless — C4);
4. `reflect` report lists dangling LINKs for review.
Differential test asserts a post-delete rebuild is byte-identical to a store never containing the entry (joint test step).

---

## 4. Entry schema (C6)

### 4.1 Fields

| Field | Type | Req | Notes |
|---|---|---|---|
| `id` | string | ✓ | content-derived (§3.2) |
| `schema_version` | int | ✓ | migrations gate on it |
| `layer` | enum | ✓ | `goal · issue · decision · failure_lesson · workflow · skill_artifact` (OP-1) |
| `title` | string | ✓ | one line, imperative or declarative |
| `body` | string | ✓ | the distilled lesson — Insight-level prose, never a transcript (FF-2) |
| `rejected_options` | list | issue/decision | positions ruled out + why (IBIS; FF-7) |
| `scope` | string | ✓ | `universal` \| `domain:<name>` \| `project:<name>` (Q4) |
| `env_assumptions` | list | workflow/skill | what must hold for replay (FF-4 gate) |
| `temporal` | object | ✓ | `valid_from`, `last_verified`, `expiry?`, `superseded_by?` (FF-8) |
| `provenance` | object | ✓ | `agent`, `task`, `environment`, `subject_id`, `source` (session/trajectory pointer — FF-2), `written_at` |
| `evidence` | list | promoted only | typed records (§5.2); empty ⇒ entry can never leave quarantine |
| `links` | list | — | `{kind: artifact\|test\|entry\|source, ref, digest?}` (Karsenty; FF-6) |
| `state` | enum | ✓ | `quarantined · promoted · superseded · expired · contested` (+ tombstone in journal for deleted) |

Validation is strict at `ADD` (C6): missing required fields ⇒ typed rejection, never a partial write.

### 4.2 State machine (governance — C7)

```
            promote(evidence)                supersede(new)
quarantined ─────────────────▶ promoted ───────────────────▶ superseded
     │                            │  ▲                          
     │ delete / expire            │  │ resolve(evidenced supersede)
     ▼                            ▼  │
  (removed)                    contested   (expiry passes → expired; still readable point-in-time)
```

Only `promoted` entries are retrievable by default consumers (C2). `expired`/`superseded` remain readable via point-in-time queries (UC-4), never in default retrieval — and when they are served this way, every slice carries an explicit `historical: true` (state at time of serving ≠ current state) so PRD §8's "zero expired/superseded entries served unflagged" holds in every mode, not only the default one.

### 4.3 Scope filter semantics (Q4)

A consumer declares its context (`project:<p>`, optionally `domain:<d>`). Retrieval serves: exact project match ∪ matching domain ∪ `universal`. Cross-scope reads (another project's entries) require an explicit `scope_override` — never the default (isolate operator; FF-3/FF-4).

---

## 5. Governance (C7)

### 5.1 Quarantine → promote

`ADD` always lands in `quarantine/`. `PROMOTE` is a specialized `UPDATE` (state transition), exposed at the API/MCP layer as `promote(id, evidence[]) → promoted | rejected{reason}` (PRD UC-2) for callers who should never need to know it compiles to `UPDATE` underneath. Promotion:
1. structurally validates every evidence record (§5.2);
2. verifies local digests of referenced artifacts when present (stdlib hash, no network — C5);
3. rejects when all evidence is issued by the writing agent itself (OP-2: the self-grade rule, mechanical);
4. moves the file `quarantine/ → promoted/` atomically and journals the transition with the evidence digest.

### 5.2 Evidence record (Q2)

```json
{
  "type": "test_result | env_feedback | independent_judge | human_signoff",
  "issuer": "<who/what produced it — must not equal provenance.agent unless type=human_signoff>",
  "ref": "<path or URI of the artifact/log>",
  "digest": "<sha256 of the artifact, when local>",
  "observed_at": "<ISO-8601>",
  "verdict": "supports | refutes | mixed"
}
```

- `test_result` additionally carries `command` + `exit_status`.
- A bare assertion has no representable form here — there is no `type` for it. That is the point (C7 "self-graded never promotes", by construction, not by policy).
- **EIF adapter** (`OracleAdapter` protocol, C1): an external process runs EIF's pipeline and *emits* evidence records; core only validates structure + digests. Any oracle satisfying the record contract works.

### 5.3 REFLECT (§6.3 for conflicts)

Batched, provenance-preserving pass over `promoted/`:
- **dedupe:** identical content-ids and near-duplicates (token-sort similarity ≥ threshold) → merge, union links/evidence, journal the merge;
- **expire:** `expiry` passed or `last_verified` older than the store's staleness horizon → state `expired`;
- **conflict:** same scope + overlapping topic (shared links or title similarity) + contradictory verdicts → both flagged `contested` + a conflict record in the report. **No auto-resolution** (Q5; R2): resolution is an evidenced supersede by a human or oracle.
Output: `ReflectReport{merged[], expired[], conflicts[], dangling_links[]}`.

---

## 6. Retrieval (C2)

### 6.1 Pipeline

```
search(query, consumer_scope, budget, as_of?) →
  1. candidate gen:   lexical (pure-Python BM25 over promoted/) ∪ semantic (optional Embedder callable)
  2. hard filters:    state=promoted at as_of · scope semantics (§4.3) · temporal validity at as_of
  3. fusion:          RRF, deterministic tie-break by entry id (Cairn precedent)
  4. staleness pass:  last_verified beyond horizon → slice flagged stale=true (FF-8 abstention);
                      as_of ≠ now → slice flagged historical=true (§4.2)
  5. budgeter:        greedy fill to token budget, whole slices only, provenance+links attached
  → slices[] | ∅        (∅ is a first-class result; no minimum-k)
```

- **Lexical default is pure-Python/zero-dep** (determinism; FTS variants are opt-in accelerations with identical semantics — Cairn FR precedent).
- **Semantic is opt-in and caller-supplied** (`Embedder` protocol: `embed(texts) -> vectors`); the default path never embeds, never networks (C5). Index stores vectors keyed by entry id; rebuildable (C4).
- Quarantined/contested/expired entries: never in default results; `contested` entries are served only with `include_contested=true` and carry the conflict flag.

### 6.2 Cairn integration (C1, UC-10)

`SearchBackend` protocol exposes `search()` as a pure function of (store state, query, filters) — no side effects, deterministic. Cairn (or any router) fronts Stele as one more signal behind its gate. Stele ships the protocol; the adapter lives Cairn-side or in glue code — core imports nothing from Cairn.

---

## 7. MCP surface (`stele-mcp`, Q3)

Stdio transport; one server per store; serializes writes (§3.3).

| Tool | Compiles to | Notes |
|---|---|---|
| `stele_add` | ADD | returns `{id, state: quarantined}` |
| `stele_update` | UPDATE | non-state fields; schema-validated |
| `stele_promote` | UPDATE (state) | evidence records required (§5) |
| `stele_supersede` | SUPERSEDE | old id + replacement entry |
| `stele_delete` | DELETE | by entry_id or subject_id; cascades (§3.4) |
| `stele_search` | SEARCH | scope, budget, as_of, include_contested |
| `stele_reflect` | REFLECT | returns ReflectReport |
| `stele_link` | LINK | entry → artifact/test/entry/source |

Eight named tools, six contract ops (`promote` is a governed UPDATE; the contract stays six — C1). Tool descriptions instruct agents to distill before ADD (FF-2) and to env-check `env_assumptions` before replaying workflow content (FF-4).

---

## 8. Export (C3) and producers (C1)

### 8.1 Pack format

```
pack/
  manifest.json    # pack_version, purpose, audience_tier, scope, created_at,
                   # expiry, source store_id, entry count, redaction report digest
  entries/         # exported entries (redacted), audience-tier filtered
  adaptation.json  # substitutions[], env_assumptions[], re_derive[] (FF-7)
  provenance/      # optional appendix: source pointers only — never raw trajectories at top level
```

### 8.2 Redaction pipeline (runs at export, trajectory-level — FF-9)

1. deterministic secret patterns (keys, tokens, connection strings, emails, paths outside the pack scope);
2. subject-id allowlist: only subjects the pack's purpose declares may appear;
3. property tests (C3): secret scan clean · stamps present · no top-level trajectory · audience tier declared.
Redaction failures **block** export — there is no force flag.

- **Audience tiers** (FF-10): `expert` (Insight layer only) · `practitioner` (+workflows) · `novice` (+worked process detail). Fading is tier selection, not content rewriting.

### 8.3 Producers

All producers speak the six ops — no exceptions (C1):
- **IVD Judgment adapter:** reads codified judgments, maps → `decision`/`failure_lesson` entries, ADDs them (quarantined; the judgment's own verification artifacts become candidate evidence).
- **Migration producer (Q6):** parses existing feedback files → entries with `provenance.agent="migration"`, `scope=project:<repo>`, `source` pointing at file+line; all quarantined; promotion via batch human sign-off (`human_signoff` evidence).

---

## 9. Test strategy (paths fixed by the intent)

| Test | Asserts | Constraint |
|---|---|---|
| `tests/test_purity.py::test_core_static_import_scan` | no ivd/cairn/eif/DB-driver imports in core | C1 |
| `tests/test_purity.py::test_write_path_zero_llm_zero_network` | counting embedder gets 0 calls; sockets disabled | C5 |
| `tests/test_schema.py::test_incomplete_entries_rejected` | golden fixtures; byte-stable round-trip | C6 |
| `tests/test_governance.py::test_self_graded_never_promotes` | self-issued evidence rejected; REFLECT provenance-preserving | C7 |
| `tests/test_retrieval.py::test_quarantine_never_served_and_filters_applied` | golden store: only valid promoted in-scope entry returned; staleness flag | C2 |
| `tests/test_store.py::test_index_rebuild_is_lossless` | drop indexes → rebuild → byte-identical results | C4 |
| `tests/test_export.py::test_pack_is_redacted_versioned_scoped` | property tests of §8.2 | C3 |
| `tests/test_joint.py::test_full_lifecycle_all_constraints` | the completion gate — full lifecycle incl. erasure cascade on one store | all |

Provenance rule (intent): these AI-planned tests cannot self-certify — each needs a human-reviewed golden fixture or an execution-derived oracle before any constraint reports PASS.

---

## 10. Non-decisions (explicitly deferred)

- SQLite/embedded-DB mirror of the SoT (only if file-store scale measurably fails; C4 shape is unchanged either way).
- Remote/multi-store sync, pack *import* semantics (open research gap — OP-12), and any hosted deployment.
- REFLECT auto-resolution policies (blocked on R2's research frontier).
- Semantic-index model choice — permanently the caller's (Embedder protocol).
- **Cost/latency measurement harness** (PRD §8 "Cost" metric): Phase 5 work per the ROADMAP. This spec fixes the budgeter's *behavior* (§6.1) but not the harness that measures its overhead — that harness is a deliverable, not an assumption to skip.
