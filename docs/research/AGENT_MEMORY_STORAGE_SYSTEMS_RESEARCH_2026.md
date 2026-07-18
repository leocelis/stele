# Agent Memory Storage Systems — Landscape Research (2026)

> **Status:** Living document — **v1.2** (2026-07-17) — relocated to the Stele repository; host references genericized for public release (v1.1: source cross-check vs arXiv/docs/GitHub licenses — Part 11 audit log)  
> **Scope:** What **storage / memory layers** exist for LLM agents — substrates, products, write/read models, and how they relate to a **session ledger**. **Not** product SKU / pricing for packs.  
> **Companion:** `AGENT_SESSION_LEDGER_INFERENCE_TIME_MEMORY_RESEARCH_2026.md` (why ledgers / transfer / packing).  
> **Also related (private-corpus companions, not included):** context building & maintenance research (Write/Select/Compress/Isolate + Mem0 hygiene); FalkorDB/Graphiti deep research (Graphiti production caveats).  
> **Sourcing rule:** Load-bearing metrics cite paper/venue. Items marked `~` are vendor blogs / community comparisons — re-benchmark on your traffic.

---

## Executive summary

**Question:** Beyond “put stuff in the context window,” what **memory storage** options exist for agents?

**Answer:** A crowded category with **five substrate families** and many products that mix them. There is **no single winner**. Choose by **who writes memory** (agent tools vs auto-extract), **what shape** (facts / graph / files / tiers), and **whether time/versioning matters**.

| Family | What it stores | Who writes | Best fit |
|--------|----------------|------------|----------|
| **A. File / tool ledger** | Markdown, NOTES, `/memories` files | Agent (or human) via tools | Coding agents, inspectable packs, Claude memory tool |
| **B. Tiered OS runtime** | Core blocks + recall + archival | Agent self-manages via tools | Long-lived stateful agents (Letta / MemGPT) |
| **C. Extract-and-retrieve** | Salient facts → vector (± graph) | Platform LLM on write | Chat personalization, Mem0-style |
| **D. Temporal knowledge graph** | Entities/edges with validity windows | Extraction pipeline | Facts that **change over time** (Zep / Graphiti) |
| **E. Framework store / checkpoint** | Namespaced KV + thread state | App / LangGraph | Already-on LangGraph; DIY policy |

**One-line synthesis:** Storage is solved in many shapes; **governance** (dedupe, UPDATE/DELETE, `user_id`, expiry, redaction) is the hard part — same lesson as the ledger research.

---

## Part 0 — Definitions

| Term | Meaning |
|------|---------|
| **Substrate** | Physical/logical store: files, vector DB, graph DB, SQL, object store |
| **Memory layer** | Product/library that decides **what** to write, **how** to index, **how** to retrieve into prompts |
| **Write policy** | Agent-tool edits vs passive LLM extraction vs human-authored |
| **Working memory** | What sits in the context window **now** |
| **Long-term memory** | Durable store outside the window |
| **Session pack** | Distilled export of a build path (see ledger companion) — a **portable artifact**, not a runtime DB |

**Non-goals:** Training-time memory (LoRA, Memory-R1 manager weights); generic document RAG without agent write-back.

---

## Part 1 — Substrate taxonomy (what can hold memory)

### 1.1 Files & directories (ledger-native)

- Plain markdown / YAML in a repo (`CLAUDE.md`, handoffs, intents, feedback YAML)
- Claude API **memory tool** — virtual `/memories` tree; **client executes** `view | create | str_replace | insert | delete | rename` ([docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool))
- IDE agent rules + `@` codebase as procedural + episodic store

**Pros:** Human-readable, git-diffable, pack-friendly, easy redaction review.  
**Cons:** Weak semantic search unless you add an index; agent must **choose** what to write.

### 1.2 Vector stores (fact / chunk recall)

- pgvector, Qdrant, Chroma, Pinecone, Weaviate, etc.
- Typical path: embed memory text → ANN search → inject top-k

**Pros:** Cheap recall at scale; mature ops.  
**Cons:** Flat facts struggle with **temporal contradiction** and multi-hop relations unless metadata/schema is careful.

### 1.3 Knowledge graphs (± temporal)

- Neo4j, FalkorDB, Memgraph, Arango… behind Graphiti / Cognee / Mem0g
- **Bi-temporal** (valid time + transaction time): Graphiti / Zep — facts are **invalidated**, not deleted ([arXiv:2501.13956](https://arxiv.org/abs/2501.13956))

**Pros:** Entity-centric + “what was true when?”  
**Cons:** Expensive write path (LLM extract); ops weight; our FalkorDB deep-dive (private corpus) documents **production risks** on FalkorDB + Graphiti scale walls.

### 1.4 Hierarchical / OS-style tiers

MemGPT → Letta ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560); [Letta memory docs](https://docs.letta.com/guides/agents/memory)):

| Tier | Analogue | Role |
|------|----------|------|
| **Core / memory blocks** | RAM / pinned registers | Always in prompt; agent edits via tools |
| **Recall** | Searchable conversation history | Out-of-window messages still queryable |
| **Archival** | Disk | Long-term insert/search |

**API note:** MemGPT paper tool names (`core_memory_append`, `archival_memory_insert`, …) describe the **pattern**. Current Letta docs center on editable **memory blocks** + persistence of all messages/tools in a DB — verify tool names against the Letta version you deploy.

**Pros:** Agent **owns** memory budget; inspectable tool trail.  
**Cons:** Extra turns/cost for tool-mediated recall; more runtime than a library.

### 1.5 Structured multi-network (research → product)

**Hindsight** ([arXiv:2512.12818](https://arxiv.org/abs/2512.12818)): world / experience / entity / belief networks; retain · recall · reflect (CARA). Strong LongMemEval numbers vs full-context baseline (see ledger companion).

**A-MEM** ([arXiv:2502.12110](https://arxiv.org/abs/2502.12110)): Zettelkasten-style linked notes; agentic add/update/link/evolve.

### 1.6 Checkpoints & framework stores

- **LangGraph** checkpoints = thread-scoped short-term state (scratchpad across steps)
- **LangGraph Store / LangMem** = cross-thread long-term KV/vector primitives inside the LangChain ecosystem (~)
- Cloudflare **Durable Objects** (~) = edge-persistent actor state for agent sessions

**Pros:** Native to orchestration graph.  
**Cons:** Policy (what to promote to long-term) is **your** job unless you add Mem0/Zep/etc.

---

## Part 2 — Write policies (the real fork)

| Policy | Examples | Write cost | Failure mode |
|--------|----------|------------|--------------|
| **Agent-managed tools** | Letta, Claude memory tool, repo NOTES | Low–medium per edit; LLM decides | Agent forgets to write / writes junk |
| **Extract-on-write** | Mem0, Zep/Graphiti ingest | High (LLM extract + embed ± graph) | Hallucinated facts; silent overwrite |
| **Human / intent authored** | IVD intents, feedback YAML | Human time | Incomplete unless workflow-enforced |
| **Hybrid** | Extract candidates → quarantine → promote | Medium | Best governance; more plumbing |

Ledger research + CONTEXT master spine agree: **unverified auto-extract → long-term store** is a poisoning path.

---

## Part 3 — Product & framework landscape (2026)

Confidence markers: ✓ paper/docs verified · ~ vendor/community · ? assumed.

### 3.1 Comparison matrix (storage-centric)

| System | Substrate | Write policy | Open path | Managed | Notes |
|--------|-----------|--------------|-----------|---------|-------|
| **Letta** (ex-MemGPT) | Tiered blocks + DB | Agent tools | Apache-2.0 ✓ GitHub | Emerging cloud | Runtime, not drop-in library ✓ |
| **Mem0** | Vector ± graph (Mem0ᵍ) | Extract-on-add | Apache-2.0 ✓ GitHub | Yes | LOCOMO: **+26% relative** LLM-as-Judge vs OpenAI memory baseline; **>90%** token cost cut and **~91%** lower p95 latency vs full-context ✓ [arXiv:2504.19413](https://arxiv.org/abs/2504.19413) |
| **Zep** | Temporal KG (Graphiti) | Extract + bi-temporal stamp | Graphiti Apache-2.0 ✓ | Zep Cloud | DMR **94.8%** vs MemGPT **93.4%**; LongMemEvalS Table 2: Zep **63.8%/71.2%** vs full-context **55.4%/60.2%** (gpt-4o-mini/gpt-4o); ~**1.6k** vs **115k** context tokens; ~**90%** latency cut ✓ [arXiv:2501.13956](https://arxiv.org/abs/2501.13956) |
| **Graphiti** | Bi-temporal KG | Episode ingest | Apache-2.0 ✓ GitHub | Via Zep | Backend: Neo4j / FalkorDB / … — see FalkorDB companion research |
| **Hindsight** | 4-network hybrid | retain/recall/reflect | MIT ✓ (`vectorize-io/hindsight`) | Yes (~ cloud) | LongMemEval 39%→83.6% (20B) — see ledger companion ✓ |
| **A-MEM** | Linked notes | Agentic organize | Research code | — | NeurIPS 2025 ✓ arXiv comment |
| **Cognee** | Graph + vector ECL | Pipeline ingest | Open core (~) | Yes (~) | Multi-source cognify (~) |
| **LangMem / LangGraph Store** | KV + vector | App-defined | MIT (~ LangMem) | No | Best if already LangGraph (~) |
| **Claude memory tool** | Client files/DB | Agent file ops | N/A (API tool) | You host data | Prefix `/memories`; commands view/create/str_replace/insert/delete/rename ✓ [docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) |
| **OpenAI ChatGPT memory** | Hosted consumer | Auto | No public agent API (~) | Yes | Not a buildable agent store for custom agents (~) |
| **Supermemory / MemoryOS / MemOS** | Mixed | Mixed | Mixed (~) | Mixed (~) | Crowded long-tail — treat as alternatives, re-bench |
| **Repo + IVD/feedback** | Files / git | Human + agent | Always | N/A | Reference procedural ledger ✓ practice |

### 3.2 Academic / reference systems (storage shape)

Already covered in ledger research for **mechanism**; storage angle here:

| System | Storage shape |
|--------|---------------|
| Generative Agents | Memory stream + reflections (append + retrieve by score) |
| Reflexion | Bounded episodic reflection buffer |
| ExpeL / AWM / CER | Experience / workflow / synthesized buffers (often in-memory or DB per experiment) |
| ReadAgent | Gist memories + pointers to source text |
| SWE-agent `.traj` | JSON trajectories on disk — demonstration archive |

### 3.3 Portability & protocols (thin but important)

| Effort | What it is | Why it matters |
|--------|------------|----------------|
| **AMP** (Wu et al., PMLR) | redact / pack / hydrate | Privacy-preserving pack boundary |
| **memorywire** ([arXiv:2606.01138](https://arxiv.org/abs/2606.01138)) | Vendor-neutral wire format for memory ops | Migration without full rebuild |
| **OSS AMP pack formats** (~ GitHub “Agent Memory Protocol”) | Signed markdown packs | Adjacent to the session-pack packaging idea — not the same as AMP PMLR paper |

Heterogeneity is real: Mem0 keys by `user_id`; Letta by `agent_id` + tags; Cognee internal IDs may not surface for delete (memorywire abstract). **Expect field loss on migrate.**

---

## Part 4 — Benchmarks: what storage claims actually mean

| Benchmark | Measures | Storage implication |
|-----------|----------|---------------------|
| **LoCoMo** | Long conversational QA | Favors extract+retrieve (Mem0 paper) |
| **LongMemEval** | Multi-session + updates + temporal + abstention | Favors mutable / temporal stores (Zep, Hindsight) |
| **DMR** (MemGPT) | Short multi-session retrieval | Easy for modern context windows; weak discriminator alone (Zep paper notes this) |
| **MemoryArena** | Memory → **action** across interdependent sessions | High LoCoMo ≠ good agentic use |

**Rule:** Vendor LongMemEval leaderboards disagree wildly across blogs (~). Prefer paper tables + **your** harness. MemoryArena gap still applies to any store.

---

## Part 5 — Cost & ops shapes

| Path | Write cost | Read cost | Ops burden |
|------|------------|-----------|------------|
| File / Claude memory tool | Cheap I/O | Agent must search/list | Low; you own backup/ACL |
| Mem0 extract | LLM every add | Cheap ANN | Medium |
| Graphiti/Zep | Very high (extract + graph) | Cheap traversal + RRF | High (graph DB) |
| Letta tiers | Tool calls + DB | Tool calls | Medium–high (server runtime) |
| LangGraph checkpoint only | Cheap | Thread-local | Low — but not cross-session LTM |

Companion Graphiti/FalkorDB research: FalkorDB has **critical open bugs** — treat FalkorDB as **dev-only** until cleared (see that doc).

**Do not** treat secondary blog pairings “Graphiti 63.8% vs Mem0 49.0% LongMemEval” as paper-comparable — **63.8%** in Zep Table 2 is **Zep + gpt-4o-mini vs full-context 55.4%**, not a Mem0 head-to-head in that paper.

---

## Part 6 — Mapping to session packs

| Pack need | Prefer substrate | Avoid |
|-----------|------------------|-------|
| Human review before sale | **Files** / AMP-style pack | Opaque vector blobs without export |
| Cross-org transfer | Insight/skill **artifacts** (ledger MTL) | Raw Mem0 dump / full trajectories |
| Time-sensitive APIs | Temporal graph **or** versioned files with expiry | Append-only vectors |
| Coding-agent reuse | Repo ledger + optional skill dir | Chat-only personalization stores |
| Privacy | Redact-at-export; `user_id` index | Unindexed embeddings of PII |

**Storage ≠ pack.** A Mem0/Zep/Letta DB is a **runtime**. A sellable pack is a **distilled, redacted, versioned export** — closer to Trace2Skill skills + IBIS issue ledger than to a live graph DB.

---

## Part 7 — Selection guide (one reference default)

**Reference default stack (host agent projects):**

1. **Primary LTM:** git-backed files — intents, feedback YAML, handoffs, patterns (established practice).  
2. **Agent write surface:** Claude-style memory tool **or** Letta blocks **only if** you need autonomous mid-session curation beyond files.  
3. **Optional recall index:** Mem0-class extract over **approved** facts — never raw transcripts; require subject_id + TTL.  
4. **Temporal KG (Graphiti):** only if a workload needs “what was true when?” **and** you accept extract cost + backend ops (prefer Neo4j over FalkorDB for prod per existing research).  
5. **Orchestration state:** LangGraph checkpoints for thread scratchpad — do not confuse with LTM.

**Do not** start with a managed memory SaaS as the system of record for build packs.

---

## Part 8 — Open problems

| Gap | Status |
|-----|--------|
| Shared wire format across vendors | Emerging (memorywire); not adopted |
| Fair cross-vendor LongMemEval | Contested (~ blogs) |
| Memory → agentic action | MemoryArena — LoCoMo-saturated systems still **perform poorly** |
| GDPR erase across vector+graph+files | Requires subject_id everywhere (CONTEXT Part 32) |
| Foreign pack import into buyer store | No standard — open research gap |

---

## Part 9 — Bibliography (selected)

### Papers

- Packer et al. (2023). MemGPT. [arXiv:2310.08560](https://arxiv.org/abs/2310.08560)
- Chhikara et al. (2025). Mem0. [arXiv:2504.19413](https://arxiv.org/abs/2504.19413)
- Rasmussen et al. (2025). Zep / Graphiti. [arXiv:2501.13956](https://arxiv.org/abs/2501.13956)
- Latimer et al. (2025). Hindsight. [arXiv:2512.12818](https://arxiv.org/abs/2512.12818)
- Xu et al. (2025). A-MEM. [arXiv:2502.12110](https://arxiv.org/abs/2502.12110)
- Munirathinam (2026). memorywire. [arXiv:2606.01138](https://arxiv.org/abs/2606.01138)
- Wu, Hu, Zhu, Wang, Jin. Agent-Memory Protocol (AMP). [PMLR v317](https://proceedings.mlr.press/v317/wu26a.html)

### Docs / products

- Letta memory: [docs.letta.com/guides/agents/memory](https://docs.letta.com/guides/agents/memory)
- Claude memory tool: [platform.claude.com/.../memory-tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)
- LangChain context engineering: [langchain.com/blog/context-engineering-for-agents](https://www.langchain.com/blog/context-engineering-for-agents)

### Internal companions

- `AGENT_SESSION_LEDGER_INFERENCE_TIME_MEMORY_RESEARCH_2026.md` (this repository)
- Context building & maintenance; FalkorDB/Graphiti and graph-database deep dives (private corpus, not included)

---

## Part 10 — Verdict

| Claim | Status |
|-------|--------|
| Multiple production-ready memory **storage** layers exist | **Supported** |
| Vector extract (Mem0-class) is enough for all agent memory | **False** — weak on temporal / agentic action |
| Temporal KG is free lunch | **False** — write cost + ops; backend risk |
| Agent-tool file/block memory is closest to “ledger” | **Supported** — Letta, Claude memory tool, repo files |
| Managed memory SaaS should be SoT for sellable packs | **Rejected** — export/redact/version in files/skills |
| Pick by substrate + write policy, not GitHub stars | **Supported** |

**Strongest packing-aligned storage rule:** Prefer **inspectable file/skill ledgers** as SoT; add Mem0/Graphiti only as **indexes** over governed facts.

---

## Part 11 — Source audit log (v1.1 — 2026-07-17)

Re-fetched: arXiv abs/html for Mem0, Zep, MemGPT, A-MEM, Hindsight, memorywire, OCELOT; Claude memory-tool docs; GitHub license API for Graphiti/Letta/Mem0/Hindsight; Semantic Scholar for Memory-R1 venue metadata.

| Issue | Was | Fix |
|-------|-----|-----|
| Graphiti **63.8%** vs Mem0 **49.0%** | Paired as comparable LongMemEval | **63.8%** = Zep+gpt-4o-mini on LongMemEvalS (Table 2); Mem0 **49%** not in Zep paper — removed pairing |
| Token cost **1.68–2.25× Mem0** | Cited as from FalkorDB research | **Removed** — not found as a primary-sourced figure in that doc body |
| Zep LongMemEval metrics | Only “+18.5% / 90% latency” | Added Table 2 absolutes: **63.8%/71.2%** vs **55.4%/60.2%**; **~1.6k** vs **115k** tokens |
| Mem0 efficiency | “~90% token save” | Paper: **>90%** token cost vs full-context; **~91%** lower p95 latency; +26% relative J vs OpenAI memory |
| Licenses Letta/Mem0/Graphiti/Hindsight | Soft | **Apache-2.0** (Letta/Mem0/Graphiti) and **MIT** (Hindsight) via GitHub API |
| Letta tool names | MemGPT paper names as current | Note: pattern holds; **verify Letta version APIs** |
| Claude path | Implied | Confirmed **`/memories`** prefix + six commands from official docs |
| MemoryArena wording | “fails” | **“perform poorly”** (paper abstract) |
| A-MEM NeurIPS 2025 | Soft | ✓ arXiv comment: NeurIPS 2025 |
| Bi-temporal Zep/Graphiti | Soft | ✓ Zep paper §2 — T / T′ + edge invalidation |

**Still ~ :** Cognee open-core details; LangMem MIT; OpenAI ChatGPT memory (no public agent memory API — Mem0 paper also notes lack of selective retrieval API); Supermemory/MemoryOS long-tail.

---

*Compiled 2026-07-17 (v1.0). Source audit 2026-07-17 (v1.1).*
