<p align="center">
  <strong>Stele</strong><br>
  <em>The governed experiential-memory ledger for AI agents — log what worked and what failed, promote only oracle-verified lessons, and let any agent build solid context from real experience.</em>
</p>

---

## What is Stele?

A **stele** is a stone raised to record what happened — deeds, laws, warnings — for those who come after. Stele is the same idea for AI agents: a **centralized ledger of task experience**. Agents automatically log what worked and what failed on each task; a governance gate promotes only lessons backed by external evidence; and any agent — today's or a future one — retrieves the distilled experience through one protocol before its next task.

Sister project to [Cairn](https://github.com/leocelis/cairn): *Cairn marks the way; Stele records what was learned on it.*

**Status: design phase.** The architecture is locked in [`stele_system_intent.yaml`](stele_system_intent.yaml), derived from two source-audited research documents published in this repository. No code yet — research first, intent second, implementation only after the intent clears human review. That ordering is the method, not an accident.

## Why

Agent sessions produce the most valuable knowledge a system has — what actually worked, what failed, and why — and today that value is thrown away. The research (all claims source-audited, see [`docs/research/`](docs/research/)) shows the naive fixes fail in documented ways:

- **Raw transcript dumps hurt.** Trajectory-level memory causes negative transfer across contexts — brittle command anchoring, false validation confidence (Memory Transfer Learning, [arXiv:2604.14004](https://arxiv.org/abs/2604.14004)). Only distilled, Insight-level content transfers safely.
- **Unverified auto-extraction poisons the store.** Extract-on-write pipelines hallucinate facts and silently overwrite; a self-graded "it worked" is confirmation bias, not evidence.
- **Append-only memories go stale and mislead.** "X worked" is a belief with a validity window, not a permanent fact ([LongMemEval](https://arxiv.org/abs/2410.10813): knowledge updates, temporal reasoning, abstention).
- **Recall benchmarks lie about agentic value.** Systems that saturate conversational-recall benchmarks still perform poorly when memory must drive *actions* ([MemoryArena](https://arxiv.org/abs/2602.16313)).

Stele inverts each failure: distilled entries only, oracle-gated promotion, bi-temporal validity with supersede-not-delete, and task-outcome evaluation as the only acceptance evidence.

## Architecture (five planes)

| Plane | What it does |
|---|---|
| **Contract** | Entry schema (goal / issue / decision / failure-lesson / workflow / skill) + bi-temporal metadata (`valid_from`, `superseded_by`, `last_verified`, `expiry`) + abstraction scope (`universal_insight` vs `project_scoped`) + mandatory provenance |
| **Tool surface** | Six operations — `ADD · UPDATE · DELETE/SUPERSEDE · SEARCH · REFLECT · LINK` — exposed as an MCP server and importable library. The only read/write path. `SUPERSEDE` invalidates a belief (history kept); `DELETE` truly erases (redaction, wrong lessons) |
| **Governance** | Writes land in **quarantine**; promotion requires **external-oracle evidence** (test result, environment feedback, independent judge, human sign-off). Batched REFLECT pass consolidates, dedupes, expires |
| **Retrieval** | Hybrid keyword + semantic + temporal search over **promoted entries only**, filtered by validity and scope, injected as budgeted slices. Returning nothing is a first-class answer; possibly-stale entries carry an explicit flag |
| **Export** | Packs: redacted, versioned, purpose-scoped, **audience-tiered** distillates that ship adaptation operators (what to substitute, which environment assumptions must hold). The live store is never the sharing surface — **storage ≠ pack** |

Core purity rules (test-enforced once implementation lands): zero LLM calls and zero network on the core write path; the source of truth is inspectable and file-exportable; every index is derived and losslessly rebuildable.

## Ecosystem

Stele composes with its sibling projects over **protocol boundaries only** — the core imports none of their code:

- **[IVD](https://github.com/leocelis/ivd)** — *producer.* IVD's Judgment layer captures intent corrections inside the development loop; an adapter ships codified judgments into Stele through the same six-op protocol as every other writer.
- **[Cairn](https://github.com/leocelis/cairn)** — *retrieval router (optional).* Cairn's selective gate decides whether and how to retrieve; Stele is one more store behind its adapters. Cairn routes, Stele stores — complementary by construction.
- **[EIF](https://github.com/leocelis/eif)** — *promotion oracle (optional).* EIF's falsification/calibration pipeline is one way to produce the evidence promotion requires; any oracle satisfying the evidence contract works.

## Repository layout

```
stele_system_intent.yaml     # the locked design decisions (start here)
docs/PRD.md                  # product requirements — pains, use cases, metrics
docs/TECH_SPEC.md            # technical design — storage, schema, ops, tests
docs/research/               # source-audited research the design derives from
docs/patterns/               # distilled pattern file (findings → rules)
ROADMAP.md                   # phases; what is decided vs. what is pending
CHANGELOG.md
```

## Reading order

1. [`stele_system_intent.yaml`](stele_system_intent.yaml) — the decisions and their constraints
2. [`docs/PRD.md`](docs/PRD.md) — who it's for, the 12 pains, the 12 use cases, success metrics
3. [`docs/TECH_SPEC.md`](docs/TECH_SPEC.md) — the technical design: storage layout, entry schema, governance state machine, retrieval pipeline, MCP surface, test strategy
4. [`docs/patterns/patterns_session_ledger_memory.yaml`](docs/patterns/patterns_session_ledger_memory.yaml) — the distilled evidence (13 foundational findings, 12 operational patterns, what research does *not* support)
5. [`docs/research/`](docs/research/) — the full audited research (inference-time ledgers; memory storage landscape)

## License

[MIT](LICENSE)
