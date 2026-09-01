# Agent Session Ledger & Inference-Time Memory — Master Research (2026)

> **Status:** Living document — **v1.4** (2026-07-17) — relocated to the Stele repository; host references genericized for public release (v1.3: second source pass — AWM Mind2Web absolutes; Memory-R1 venue year)  
> **Scope:** Whether **frozen general-purpose models + agent tools that read/write an external ledger** improve outcomes — and what prior work says about **packaging exhausted build paths** (intent, issues, decisions, workflows) for reuse. **Product design is out of scope** for this document.  
> **Method:** Academic papers (1980s–2026), official vendor docs, benchmark reports, and selected practitioner/community sources. Cross-checked against the authors' private context-research corpus (context building & maintenance; error-feedback self-evolving workflows; research-to-patterns).  
> **Sourcing rule:** Load-bearing claims cite arXiv ID, venue, or canonical URL. Items marked `~` are practitioner consensus without controlled benchmarks.  
> **v1.1 focus:** Cross-org transfer, negative transfer, capture overhead, DR reuse empirics, staleness, privacy, expertise reversal, evaluation gaps.  
> **v1.2 focus:** Claim-by-claim audit vs primary sources (authors, venues, metrics, paper scope).  
> **v1.3 focus:** Re-fetched AWM Table 4 / Memory-R1 venue; storage companion audited in parallel.

**Companions:** `AGENT_MEMORY_STORAGE_SYSTEMS_RESEARCH_2026.md` (what stores exist — vector / graph / Letta / Claude memory tool; in this repository). Context-building & maintenance (Write/Select/Compress/Isolate), error-feedback self-evolving workflows (failure → memory loop), and research-to-patterns (ExpeL / rule induction) companions live in the authors' private research corpus and are not included here.

---

## Executive summary

**The core question:** After a model is trained, can an **agent layer** maintain a **ledger** (external memory of goals, issues, decisions, failures, workflows) via **tools**, inject retrieved ledger slices into context, and **produce better results** — without fine-tuning weights?

**Answer: yes — this is a major, validated research and production line.** It is **not** a crazy idea. It is also **not** a solved product category.

| Layer | Verdict | Confidence |
|-------|---------|------------|
| **Mechanism** (Model + Agent + external ledger → better inference) | Validated across many papers and production systems | ✓ High |
| **Historical precedent** (capture *why*, not just *what*) | Design rationale, CBR, worked examples — decades old | ✓ High |
| **Distillation beats raw logs** | Structured memory >> transcript dumps | ✓ High |
| **Cross-agent / cross-domain transfer of distilled experience** | Supported when **abstracted** (Insight/skill); raw trajectories often **hurt** | ✓ High (MTL 2026; Trace2Skill; ExpeL) |
| **Cross-org “foreign pack” product category** | Still **no direct SKU literature**; analogies + transfer papers only | ~ Medium |
| **Capture cost / industrial DR failure** | Documented — cognitive overhead; short-term payoff required | ✓ High (Shum; Conklin) |
| **Market / willingness to pay** | Not established by academic work | ? Open |

**One-line synthesis:** Runtime ledger architecture is proven. **Foreign reuse is real but format-sensitive** — Insights/skills transfer; raw traces often cause negative transfer. Capture overhead and privacy remain the hard constraints on packaging.

---

## Part 0 — Research questions & definitions

### 0.1 Primary questions

1. Has **Model + Agent + Context** with a **mutable external ledger** been tried **above** the training layer (no weight updates)?
2. Does maintaining that ledger **improve task outcomes** vs. stateless or full-context baselines?
3. What should a ledger **contain** (goal, issues, decisions, workflows, code, reflections)?
4. What does prior work say about **reusing** someone else's captured path (not your own session)?
5. What **fails** when ledgers are naive (dump, stale, self-confirming)?

### 0.2 Terms (used consistently in this doc)

| Term | Meaning |
|------|---------|
| **Ledger** | Durable, structured store **outside** the context window: goals, issues, decisions, rejected options, lessons, workflows, artifacts. Updated by agent tools or orchestrator. |
| **Inference-time learning** | Improvement via **read/write memory + in-context retrieval**, not gradient updates on the base model. |
| **Experiential memory** | Memory of **what happened** during tasks — successes, failures, trajectories — vs. factual/world memory (Hu et al. 2025 taxonomy). |
| **Design rationale (DR)** | Record of **issues, alternatives (incl. rejected), trade-offs, commitments** behind a design (Potts & Bruns 1988; Conklin & Begeman 1988). |
| **Path / session pack** | Distilled export of an exhausted build: intent + issue ledger + workflows + optional code — **not** a raw chat transcript. |

### 0.3 Explicit non-goals (this doc)

- Product SKU, pricing, GTM (out of scope).
- Training-time memory (LoRA, RLHF, Memory-R1's fine-tuned memory manager — noted but not central).
- Generic RAG over static docs (related but not the same as **live ledger maintenance**).

---

## Part 1 — Historical lineage (pre-LLM): why a ledger is not new

The LLM-agent version is new; the **information architecture** is not.

### 1.1 Design rationale & issue-based deliberation

**Core claim:** Reuse requires knowing **why** something was built, including **rejected** options — not only final artifacts.

| Source | Authors / year | Contribution |
|--------|----------------|--------------|
| [Recording the reasons for design decisions](https://doi.org/10.5555/55823.55863) | Potts & Bruns, ICSE 1988 | Artifact + deliberation network: **issues, alternatives, justifications** linked to specs |
| [gIBIS: a hypertext tool for exploratory policy discussion](https://doi.org/10.1145/58566.59297) | Conklin & Begeman, ACM TOIS 1988 | **IBIS**: issues → positions → arguments; captures rejected options and trade-offs |
| [Kuaba approach](https://doi.org/10.1017/s0890060408000279) | Medeiros et al., AI EDAM 2008 | DR + formal semantics for **model-based design reuse** |
| [Questions, Options, and Criteria](https://doi.org/10.1207/s15327051hci0603) | MacLean, Young, Bellotti, Moran, HCI 1991 | **QOC** notation for Design Space Analysis (canonical origin) |
| [A Cognitive Analysis of Design Rationale Representation](https://simon.buckinghamshum.net/wp-content/uploads/2008/05/Shum_PhD_Final_1992_A_Cognitive_Analysis_of_Design_Rationale_Representation.pdf) | Buckingham Shum, PhD 1992 | Cognitive analysis of DR representations **including QOC**; authoring cost vs. retrieval value |
| [Design rationale](https://en.wikipedia.org/wiki/Design_rationale) | Survey | DR for **reuse, maintenance, redesign** — indices to past knowledge |

**Mapping to agent session ledger:**

| DR / IBIS node | Agent ledger analogue |
|----------------|----------------------|
| Issue | Open problem / bug class / requirement tension |
| Position (incl. rejected) | Option tried or explicitly ruled out |
| Argument / criteria | Evidence, test result, constraint from intent |
| Artifact | Code, schema, config, deliverable |
| Commitment | Decision locked for this build |

**Known historical failure mode:** **Capture cost.** DR systems (gIBIS, QuestMap) showed value in industrial pilots but struggled with **ongoing authoring burden** unless workflow-integrated (Lee, AI Magazine survey; Buckingham Shum & Hammond cost/benefit; Conklin SCE). **Agent sessions auto-generate the raw material** — the open problem shifts to **distillation**, not blank-page journaling.

### 1.2 Case-based reasoning (CBR)

| Source | Authors | Contribution |
|--------|---------|--------------|
| *Case-Based Reasoning* | Kolodner, 1993/2005 | Solve new problems by **retrieving and adapting** prior cases |
| [Applying knowledge modelling and CBR to software reuse](https://doi.org/10.1049/ip-sen:20000897) | P.A. González, IEE Proc. Softw. 2000 | Functional descriptions + case base of **interesting experiences** in an OO component library (VisualWorks) |
| [CADET](https://www.cs.cmu.edu/afs/cs/project/cadet/ftp/docs/CADET.html) | Sycara & Navinchandra (CMU) | Case-based mechanical design: retrieve/synthesize prior designs; avoid known failures |

**Mapping:** An exhausted session pack is a **case** indexed by goal/problem class; the agent **adapts** it to a new codebase/context.

### 1.3 Cognitive apprenticeship & process-oriented worked examples

| Source | Authors | Contribution |
|--------|---------|--------------|
| [Cognitive Apprenticeship](https://www.aft.org/ae/winter1991/collins_brown_holum) | Collins, Brown, Holum, 1991 | Make expert **tacit process** visible: modeling, coaching, reflection |
| [Process-Oriented Worked Examples](https://doi.org/10.1023/B:TRUC.0000021810.70784.b0) | van Gog, Paas, van Merriënboer, Instructional Science 2004 | **Why + how** process info in examples argued to improve transfer (theoretical CLT framing) |
| [Effects of Worked Examples on Far Transfer](https://doi.org/10.17615/8td7-ta18) | Kim, 2015 (UNC dissertation) | Review: far-transfer benefits of worked examples are **mixed**; self-explanation / fading / subgoals may help; effects moderated by prior knowledge |
| [The Effortless Trap](https://arxiv.org/pdf/2606.26181) | 2026 | Worked examples land best **after productive struggle**, not as instant answer keys |

**Mapping:** A distilled session pack is a **process-oriented worked example** for a goal class ("build a database", "wire auth"). **Expertise reversal:** heavy scaffolding helps novices; experts need less — packs must declare **audience level**.

### 1.4 Engineering knowledge packaging (non-LLM industry)

| Precedent | What got packaged | Reuse mechanism |
|-----------|-------------------|-----------------|
| **ISA-88** batch control | Phases, equipment modules, recipes | Separate **equipment logic** from **recipe** — change recipe without rewriting control code |
| **Reusable AOI / template libraries** (e.g. Bosch/Rockwell case studies) | Validated logic blocks | Configure variants from library, not greenfield |
| **MasterDesign™** (International Paper) | 1.8M+ structural designs + R&D know-how | Searchable **visual catalog** of institutional expertise |

**Mapping:** Session pack = **recipe + rationale**; buyer's agent = **equipment module** that executes adapted steps in their environment.

---

## Part 2 — The inference-time stack (frozen model + agent + ledger)

### 2.1 CoALA: canonical cognitive architecture

**Paper:** [Cognitive Architectures for Language Agents](https://arxiv.org/abs/2309.02427) — Sumers, Yao, Narasimhan, Griffiths; TMLR 2024.

CoALA positions the LLM inside a system with:

- **Memory modules:** working, episodic, semantic, procedural (read/write via **internal actions**)
- **Action space:** external (tools, APIs) + internal (retrieve, write memory, reason)
- **Decision loop:** plan → act → update memory

**Key for this research:** CoALA explicitly separates **learning as memory write** from **parametric learning**. Language agents **persist information across LLM calls** in external modules — exactly the ledger layer.

### 2.2 Context engineering: Write · Select · Compress · Isolate

**Four-bucket taxonomy (canonical attribution):** LangChain / Lance Martin — [Context engineering for agents](https://www.langchain.com/blog/context-engineering-for-agents) and [Martin's writeup](https://rlancemartin.github.io/2025/06/23/context_engineering/). Anthropic's engineering post covers **overlapping practices** (note-taking, memory tool, compaction, multi-agent isolation) but does **not** originate the four-bucket labels.

| Operator | Ledger role |
|----------|-------------|
| **Write** | Agent **appends/updates** ledger files, memory tool, DB — outside window |
| **Select** | Retrieve relevant ledger slices into working context for this step |
| **Compress** | Summarize ledger sections; drop redundant tool output |
| **Isolate** | Sub-agents write to sub-ledgers; parent gets distilled summary only |

**Anthropic (official):** [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — structured **note-taking** persisted outside window; **compaction** of conversation history; **memory tool** (file-based read/write/delete) in Claude API ([cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools)).

**Distinction from compaction:** Compaction **summarizes the conversation**; ledger **keeps addressable records** (issues, decisions) that can be **selectively** retrieved later — not only a rolling summary.

---

## Part 3 — Canonical systems: inference-time memory (no base-model training)

Each row: **frozen LLM** + **external store** + **agent updates/reads** at runtime.

| System | Authors / year | What the ledger holds | How agent uses it | Training? |
|--------|----------------|----------------------|-------------------|-----------|
| **MemGPT → Letta** | Packer et al. 2023; [arXiv:2310.08560](https://arxiv.org/abs/2310.08560) | Core / archival / recall tiers (MemGPT paper); Letta: editable **memory blocks** + persisted messages | Agent memory tools (names vary by Letta version) | No |
| **Generative Agents** | Park et al. UIST 2023; [arXiv:2304.03442](https://arxiv.org/abs/2304.03442) | **Memory stream** (observations) + **reflections** | Retrieve by recency, importance, relevance; reflect → write back | No |
| **Reflexion** | Shinn et al. NeurIPS 2023; [arXiv:2303.11366](https://arxiv.org/abs/2303.11366) | **Verbal reflections** on failure (episodic buffer, bounded) | Next episode conditions on reflections | No |
| **ExpeL** | Zhao et al. AAAI 2024; [arXiv:2308.10144](https://arxiv.org/abs/2308.10144) | **Insights** + successful trajectories in experience pool | Retrieve insights + similar trajectories at test time | No |
| **Voyager** | Wang et al. NeurIPS 2023 **ALOE workshop**; [arXiv:2305.16291](https://arxiv.org/abs/2305.16291) | **Skill library** (executable code) | Retrieve + compose skills; iterative prompting w/ env feedback | No (GPT-4 black-box) |
| **Agent Workflow Memory (AWM)** | Wang et al. 2024; [arXiv:2409.07429](https://arxiv.org/abs/2409.07429) | **Workflows** (reusable sub-routines from trajectories) | Inject workflows into memory for later tasks | No |
| **CER** | Yitao Liu et al. ACL 2025; [ACL 2025.acl-long.694](https://aclanthology.org/2025.acl-long.694/); [arXiv:2506.06698](https://arxiv.org/abs/2506.06698) | Synthesized **experience buffer** (env dynamics + patterns) | **Training-free** replay during inference on WebArena | No |
| **ReadAgent** | Lee et al. ICML 2024; [PMLR v235](https://proceedings.mlr.press/v235/lee24c.html) | **Gist memories** of episodes + pointer to source | Lookup original text when detail needed | No |
| **Mem0** | Chhikara et al. 2025; [arXiv:2504.19413](https://arxiv.org/abs/2504.19413) | Extracted, consolidated **memory facts** | ADD/retrieve; graph variant for relations | No |
| **Hindsight** | Latimer et al. 2025; [arXiv:2512.12818](https://arxiv.org/abs/2512.12818) | **Four networks:** world, experience, entity, beliefs | retain · recall · reflect (CARA) | No |
| **A-Mem** | Xu et al. NeurIPS 2025; [arXiv:2502.12110](https://arxiv.org/abs/2502.12110) | Agentic **memory notes** with links (Zettelkasten-style) | Agent decides add/update/link/retrieve; memories evolve | No |
| **AgentHER** | 2026; [arXiv:2603.21357](https://arxiv.org/abs/2603.21357) | Relabeled **failure trajectories** as training data | Packages trajectories for SFT/DPO — **downstream training**, not runtime ledger | Hybrid |
| **SWE-agent trajectories** | Princeton/Stanford; [docs](https://swe-agent.com/latest/usage/trajectories/) | `.traj` JSON: thought, action, observation per step | Replay as **demonstrations**; archive for SWE-Replay | No |
| **SWE-Replay** | 2026; [arXiv:2601.22129](https://arxiv.org/abs/2601.22129) | Archive of trajectories | Branch from **critical intermediate steps** at test time | No |

### 3.1 Letta / MemGPT — closest production analogue to "agent maintains ledger via tools"

**Mechanism (verified in paper + Letta docs):**

- Context window = **RAM**; archival / recall / files = **disk**
- Agent **autonomously** calls memory tools mid-reasoning
- External memory providers pluggable ([Letta external memory tutorial](https://docs.letta.com/tutorials/integrations/external-memory/))
- Filesystem + semantic search tools benchmarked on LoCoMo ([Letta blog 2026](https://www.letta.com/blog/benchmarking-ai-agent-memory/))

**Implication:** "Agent looks for ledger and keeps it updated" is **literally** the MemGPT design pattern — shipped as Letta, memory tool in Claude API, LangGraph checkpoints, etc.

### 3.2 Reflexion & ExpeL — failure and cross-task experience

**Reflexion:** Binary/scalar env feedback → **verbal lesson** → stored → next trial. No fine-tuning. HumanEval 91% pass@1 cited vs GPT-4 80% in paper.

**ExpeL:** Across tasks, pool **success and failure** trajectories → extract **NL insights** (with UPVOTE/DOWNVOTE/EDIT) → at test time retrieve insights + similar successes. Explicitly motivated by **closed APIs** (no weight access).

**Corpus alignment:** external errors as ground truth; **distill, don't dump** (error-feedback companion research).

### 3.3 Voyager & AWM — procedural ledger (skills / workflows)

**Voyager:** Skill library of **code**; compositional; reduces catastrophic forgetting vs. weight updates.

**AWM:** Induces **workflows** from past trajectories. Paper headline (abstract): **+24.6% relative step-wise success** on Mind2Web cross-task; **+51.1% relative success rate** on WebArena vs BrowserGym baseline. AgentHER (2026) treats AWM as a strong experience-centric baseline.

**Mapping:** Exhausted session → induced **workflow** (AWM) + **skills** (Voyager) + **issues** (IBIS) = rich pack.

### 3.4 CER — explicit "continual learning at inference time"

**CER (Yitao Liu et al., ACL 2025):** Accumulates and **synthesizes** past experiences into dynamic buffer; **+51.0% relative** success on WebArena vs GPT-4o BrowserGym baseline (36.7% absolute SR); 31.9% on VisualWebArena (paper). Framed as agents not designed to learn during inference — CER fixes that **without training**.

### 3.5 Software engineering: trajectories as first-class artifacts

**SWE-agent** emits structured `.traj` files per instance — thought/action/observation — and documents converting trajectories to **custom demonstrations**.

**SWE-Replay:** Reuses trajectory archive; branches at **reasoning-intensive** steps; reduces cost vs. from-scratch sampling.

**Mapping:** An exhausted "build a database" session is a **trajectory + rationale**; buyer's agent replays **workflow**, not every wrong turn.

---

## Part 4 — Surveys & taxonomies (2024–2026)

Use these for navigation, not as primary evidence.

| Survey | arXiv / venue | Useful framing |
|--------|---------------|----------------|
| [Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564) | Hu, Liu, Yue, Zhang, et al., Dec 2025 | **Forms** (token / parametric / latent) × **Functions** (factual / **experiential** / working) × **Dynamics** (form, evolve, retrieve) |
| [Rethinking Memory Mechanisms of Foundation Agents](https://arxiv.org/pdf/2602.06052) | 2026 | **External memory** = explicit read/write; tradeoffs: latency, noise, pruning |
| [Memory for Autonomous LLM Agents](https://arxiv.org/pdf/2603.07670) | 2026 | Mechanisms, evaluation, governance; long context ≠ persistent structured memory |
| [Memory in the LLM Era: Modular Architectures](https://arxiv.org/pdf/2604.01707v2) | 2026 | Unified pipeline: extraction → management → storage → retrieval |
| CoALA | [2309.02427](https://arxiv.org/abs/2309.02427) | Positions 50+ agents in one architecture |

**Experiential memory** (Hu et al.) = closest academic label for **session ledger of builds**.

---

## Part 5 — Benchmarks: recall vs. use-in-action

| Benchmark | What it measures | Finding relevant to ledger |
|-----------|------------------|----------------------------|
| **LoCoMo** | Long conversational QA | Mem0/Hindsight score high on **recall** |
| **LongMemEval** | Multi-session reasoning, updates (Wu et al.) | Hindsight OSS 20B: **39% → 83.6%** vs same-backbone full-context on LongMemEval (Latimer et al. abstract) |
| **BEAM** | 1M–10M token scale | Can't brute-force context; needs selective memory |
| **MemoryArena** | He et al. [arXiv:2602.16313](https://arxiv.org/abs/2602.16313) | **Interdependent multi-session tasks** — must **use** memory to act; LoCoMo-saturated systems **perform poorly** here |

**Critical gap (MemoryArena, He et al. 2026):** High **recall** on chat benchmarks does not imply memory helps **agentic** decisions. Abstract wording: agents near-saturated on LoCoMo **perform poorly** in MemoryArena's agentic setting. A sellable session pack must help **action**, not just Q&A over the pack.

**Practitioner summary:** [Mem0 State of Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) — token-efficient retrieval (~7k tokens/call vs ~26k full-context on LoCoMo, vendor-reported).

---

## Part 6 — Hybrid line: learned memory *operators* (still external store)

**Memory-R1** ([arXiv:2508.19828](https://arxiv.org/abs/2508.19828); Semantic Scholar lists ACL 2025): RL-fine-tuned **Memory Manager** (ADD/UPDATE/DELETE/NOOP) + **Answer Agent** — store remains **external**; small models learn **when/how** to write ledger rows.

**Relevance:** Validates that **ledger maintenance policy** matters; heuristic append-only is suboptimal. Still not updating GPT-4/Claude **base weights**.

---

## Part 7 — What a ledger should contain (synthesis)

Combining DR/IBIS, CoALA, and agent memory papers:

### 7.1 Recommended layers

| Layer | Contents | Primary sources |
|-------|----------|-----------------|
| **Goal / intent** | Success criteria, constraints, non-goals | authored intents; DR commitments; CoALA planning |
| **Issue ledger** | Open issues, positions, rejected options, arguments | IBIS; Potts & Bruns |
| **Decision log** | What was chosen, when, with evidence pointer | DR; Hindsight belief updates |
| **Failure / lesson** | What failed, why, verbal reflection | Reflexion; ExpeL insights |
| **Workflow** | Reusable sub-routine (abstracted from instance) | AWM; ISA-88 phases |
| **Skill / artifact** | Code, schema, tests, configs | Voyager; SWE-agent trajectories |
| **Provenance** | Model, agent, date, env, test commands | Needed for trust; underweighted in most papers |

### 7.2 What NOT to store (anti-patterns)

| Anti-pattern | Why it fails | Evidence |
|--------------|--------------|----------|
| Raw full transcript | Noise, context rot, cost | Anthropic context engineering; Chroma context rot |
| Success-only traces | Wastes majority of runs; misses lessons | AgentHER; ExpeL uses failures |
| Unversioned stale facts | Wrong guidance after env change | DR reuse warnings (Lee survey); knowledge update benchmarks |
| Self-graded reflections only | Confirmation bias | MAR ([arXiv:2512.20845](https://arxiv.org/abs/2512.20845)) on Reflexion; need external or multi-judge oracles |
| One-size-fits-all pack | Expertise reversal | Worked examples literature |

### 7.3 Ledger operations (minimal CRUD)

From MemGPT, Mem0, Memory-R1, Hindsight:

- **ADD** — new issue, observation, decision
- **UPDATE** — supersede belief, close issue, merge duplicate
- **DELETE / supersede** — GDPR, wrong lessons, outdated workaround
- **SEARCH** — semantic + keyword + temporal + graph (Hindsight, Mem0 2026)
- **REFLECT** — periodic synthesis (Generative Agents, Hindsight CARA)
- **LINK** — issue → artifact → test → workflow step

---

## Part 8 — Community & production implementations (~)

Practitioner patterns **not** always peer-reviewed:

| System | Ledger mechanism | Notes |
|--------|------------------|-------|
| **Letta / MemGPT** | Memory tools + core blocks | Open source; [github.com/letta-ai/letta](https://github.com/letta-ai/letta) |
| **Claude API memory tool** | File CRUD via tool | Client implements storage backend |
| **LangGraph** | Checkpointed state + store | Thread memory as scratchpad |
| **Mem0 / Zep / Graphiti** | Managed memory layers | Commercial; benchmark marketing — verify on your workload |
| **Cursor / IDE agents** | Rules, handoffs, `@` codebase | **Procedural + episodic** ledger in repo; operator-maintained |
| **authored intents + feedback YAML** | Constraint spine + iteration ledger | intent framework pattern — intent as goal, feedback as issue trail |

**Full storage landscape (substrates, write policies, product matrix):** → `AGENT_MEMORY_STORAGE_SYSTEMS_RESEARCH_2026.md`

**~ practitioner consensus:** Durable **files in repo** (rules, handoffs, intents) outperform hoping the model "remembers" — aligns with LangChain/Martin **Write** operator and Anthropic note-taking / memory tool.

---

## Part 9 — Weak area deep dive: reusing foreign / transferred experience

> **Why this was weak in v1.0:** Most agent-memory papers study **same agent, same deployment**. Cross-org packaging was left as analogy. v1.1 fills this with CBR adaptation, DR reuse empirics, ExpeL/Trace2Skill/MTL transfer results, and explicit **negative transfer** evidence.

### 9.1 Classic CBR: retrieve is easy; **adapt** is the hard part

[Khan (2014)](https://doi.org/10.1049/iet-sen.2013.0127) — *Applications of case-based reasoning in Software Engineering: a systematic mapping study* (IET Softw.): CBR in SE repeatedly finds that retrieved solutions **are not usable as-is**. Adaptation modes (as summarized in that mapping):

| Adaptation type | Meaning | Risk if skipped |
|-----------------|---------|-----------------|
| **Substitution** | Replace a part of the solution | Wrong library / API / language |
| **Transformation** | Change solution structure | Architectural mismatch |
| **Generative** | Replay the *process* of finding the solution | Closest to “session pack as process,” not as code dump |

**Design implication (from CBR literature):** A sellable pack that ships only final code without **adaptation operators** (what to substitute, what env assumptions hold) is incomplete. Substantial adaptation **erodes** the knowledge-engineering advantage of CBR if every case must be hand-rewritten (Khan 2014 mapping, citing classic CBR).

**Failed cases help adaptation:** Recent CBR work argues that **ignoring failed cases wastes learning** — failed cases act as **repulsion** (what not to do) while successes act as **attraction** ([Leveraging both Successes and Failures in CBR](https://doi.org/10.1007/978-981-99-5834-4_3); ACIIDS 2023). This aligns with AgentHER / ExpeL: failures are signal, not waste.

**Cross-domain process transfer:** Minor et al. (AIKE 2021) transfer **process-oriented cases** (BPMN workflows) from airport baggage handling → SAP warehouse management using operators: **analogical substitution, generalisation, abstraction**. Quality assessed via 3QM process metrics — shows **workflow abstraction** is the transfer unit, not raw logs.

### 9.2 Design rationale reuse: needed, but captured DR is often insufficient

**Karsenty (CHI 1996)** — *An Empirical Evaluation of Design Rationale Documents* ([doi:10.1145/238386.238462](https://doi.org/10.1145/238386.238462)):

- Six professional designers given **solution docs + QOC rationale** for a past design.
- **>50% of designers’ questions** concerned rationale (they *need* DR).
- **<50% of those DR questions** were answered by the QOC document.
- Verdict: DR is **useful but not sufficient**; traditional capture misses what reusers actually ask.

**Lee (AI Magazine survey)** — Conklin/Burgess-Yakemovic gIBIS at NCR: reconstruction cost paid for itself by catching omissions worth **3–6×** the capture cost — but only when capture was actually done and used.

**Implication for session packs:** Even a carefully authored issue ledger will leave **unanswered reuser questions**. Packs need **links to artifacts + tests + env constraints**, not rationale alone (Karsenty’s “integrate with technical design artifacts”).

### 9.3 Capture overhead: why industrial DR systems died

This is the historical failure mode most relevant to “exhaust a session and package it.”

| Source | Finding |
|--------|---------|
| Buckingham Shum & Hammond (1994) | Argumentation-based DR: **what use at what cost?** — cognitive overhead of structuring ideas mid-design |
| Conklin QuestMap / SCE case study | Adoption requires **short-term payoff** for participants — cannot be only long-term documentation ([Conklin CSAV chapter](http://www.cognexus.org/ConklinCaseStudyChapter.pdf)) |
| Buckingham Shum (KMi) | QuestMap had industrial pockets of use then **succumbed to market pressures**; success needed **facilitators** + metacognitive skill in IBIS |
| Lee survey | Cost/benefit: “will not be used if cost outweighs benefits”; rich formalisms raise overhead |

**Agent-session angle:** Raw capture is now **cheap** (agent produces traces automatically). That removes the *blank-page* authoring cost. Remaining costs shift to:

1. **Distillation** (who pays to turn traces into Insights/skills?)
2. **Sanitization** (privacy — Part 9.6)
3. **Maintenance** (staleness — Part 9.5)
4. **Buyer adaptation** (Part 9.1)

~ Conklin’s rule still applies: if distillation is slow and buyers see no **immediate** win, packs won’t stick — same failure mode as QuestMap.

### 9.4 Modern transfer evidence: abstraction dictates transferability

#### ExpeL transfer (Zhao et al., AAAI 2024)

- Source: HotpotQA insights → Target: FEVER (both Wikipedia Docstore).
- Insights **adapted** with few target demos outperform transfer without demos.
- When domains differ, **experience-pool retrieval is dropped**; only distilled insights transfer.
- Explicit forward-transfer setting for LLM agents without weight updates.

#### Trace2Skill (Ni et al., 2026) — [arXiv:2603.25158](https://arxiv.org/abs/2603.25158)

- Distills **many trajectories in parallel** into a **unified skill directory** (SoPs), not sequential overfitting to one trajectory.
- Skills transfer **across model scales and families** and to OOD settings.
- Example: skills from Qwen3.5-35B trajectories improved Qwen3.5-122B by up to **+57.65 pp** on WikiTableQuestions.
- Beats ReasoningBank-style retrieval memories on transfer — **declarative skills > episodic retrieval banks** for portability.
- No parameter updates; no test-time retrieval module required.

#### Memory Transfer Learning for coding agents — Kim et al. (2026) — [arXiv:2604.14004](https://arxiv.org/abs/2604.14004)

First systematic study of **cross-domain** memory for coding agents (6 benchmarks; GPT-5-mini, DeepSeek, Qwen3-Coder):

| Format | Abstraction | Transfer quality |
|--------|-------------|------------------|
| **Trajectory** | Lowest (action–obs pairs) | Often **negative transfer** — brittle command anchoring |
| **Workflow** | Medium (filtered key steps) | Medium |
| **Summary** | Medium–high | Medium–high |
| **Insight** | Highest (task-agnostic principles) | **Best** — meta-knowledge (validation, inspect structure) |

**Headline:** Cross-domain memory improves average Pass@3 by **~3.7%**; gains are from **meta-knowledge**, not task-specific code. Trajectories can cause agents to **blindly replay** domain-specific CLI steps on mismatched projects (paper case studies).

**Negative transfer modes (MTL paper):**

1. Domain-mismatched misleading anchors (superficially similar, wrong context)
2. False validation confidence (skip real checks because memory “validated”)
3. Misapplied best-practice transfer (wrong language/tooling)

**Design principle (verified):** Abstraction ↑ → transferability ↑. Packs that ship **raw Cursor/Claude transcripts** as the product are the **highest negative-transfer risk** format in current literature.

#### Voyager (Wang et al., 2023)

Skill library transfers to a **new Minecraft world** for novel tasks — same game engine, different instance. Supports **procedural** portability inside a fixed ontology; weaker evidence for **cross-stack** software packs.

#### AWM offline / online (Wang et al., 2024)

- **Offline** (Mind2Web cross-task): +4.0–8.9% **relative** and +0.4–2.8 **absolute** points in step/task success vs Synapse / MindAct (paper §3.2.1).
- **Online** generalization (Table 4, gpt-4): +**7.4–8.9** / +**3.6–3.8** / +**14.0–16.9** absolute points in **step success rate** on cross-task / cross-website / cross-domain vs MindAct.
- Supports **workflow-level** foreign reuse when workflows are **induced**, not copy-pasted UI traces.

### 9.5 Staleness, knowledge updates, temporal reasoning

| Source | Finding |
|--------|---------|
| **LongMemEval** (Di Wu et al., ICLR 2025) — [arXiv:2410.10813](https://arxiv.org/abs/2410.10813) | Five abilities: extraction, multi-session, **knowledge updates**, **temporal reasoning**, **abstention**. Abstract: commercial assistants / long-context LLMs show a **~30%** accuracy drop on sustained histories; body: long-context LLMs vs oracle evidence sessions drop **~30–60%** on LongMemEvalS. Time-aware indexing/query expansion improves **temporal-reasoning memory recall by 6.8–11.3%** (when a strong LLM expands the query). |
| Hindsight / Mem0 | Explicit belief / fact update pathways — treat memory as **mutable**, not append-only forever |
| MemoryArena | Interdependent multi-session tasks — early facts become **constraints** later; stale memory breaks the loop |

**Implication for packs:** A pack without **version stamps** (library versions, API dates, model ID, last-verified date) and without **UPDATE/DELETE** semantics becomes hazardous. Abstention (“this may be outdated”) is a first-class memory skill in LongMemEval — packs should encode **confidence + expiry**.

### 9.6 Privacy, secrets, and trajectory leakage

Packaging agent sessions for sale collides with privacy research that treats leakage as a **trajectory** property, not a single message.

| Source | Finding |
|--------|---------|
| **OCELOT** (2026) — [arXiv:2606.12341](https://arxiv.org/abs/2606.12341) | Agent privacy = **cumulative, bidirectional, task-dependent** leakage across a trajectory of tool/sink releases. Per-message filters miss inference from many innocuous steps. |
| **AMP** (Agent-Memory Protocol) — Wu, Hu, Zhu, Wang, Jin; [PMLR v317](https://proceedings.mlr.press/v317/wu26a.html) | Privacy-first protocol: **redact at rest**, **pack for purpose**, **hydrate on return** — PII never leaves user boundary while preserving reasoning utility. |
| **From rights to runtime** (AAAI 2026) — [doi:10.1002/aaai.70036](https://doi.org/10.1002/aaai.70036) | Memory must be **optional, bounded, visible**; cascade erasure + receipts; purpose-aware egress on every tool call. |
| GDPR practitioner guidance (~) | Persistent memory ⇒ controller duties; Art. 17 erasure requires **user_id-indexed** memories; opaque auto-extract harder to defend than explicit remember() |

**Implication for packs:** Exhausted sessions routinely contain API keys, customer names, private repo paths, cookies. A pack pipeline needs **redact-at-export** as a first-class step — not optional polish. Academic support favors **purpose-scoped packing** over shipping full trajectories.

### 9.7 Expertise reversal: who the pack is for

| Source | Finding |
|--------|---------|
| Kalyuga, Ayres, Chandler, Sweller (2003) | **Expertise reversal effect** — techniques that help novices **hurt experts** (redundant guidance consumes working memory) |
| Kalyuga (2007) | Instruction must **adapt as expertise grows**; fade worked examples toward problem solving |
| Renkl & Atkinson | **Fading** solution steps is the recommended transition |

**Implication:** A single “database build pack” at max scaffolding helps novices and **annoys / degrades** experts. Literature supports **audience-tiered packs** or **faded layers** (Insight-only for experts; full process worked example for novices) — mirrors MTL’s abstraction ladder.

### 9.8 Evaluation gap: what is still missing

| Need | Status |
|------|--------|
| Same-agent, same-domain memory helps | Well measured (LoCoMo, LongMemEval, AWM, CER) |
| Memory helps **agentic action** | MemoryArena — LoCoMo-saturated systems still **perform poorly** |
| Cross-domain **Insight** transfer for coding | Measured (MTL +3.7% avg; format ranking) |
| Cross-model skill transfer | Measured (Trace2Skill large gains) |
| **Foreign org pack → buyer completes analogous goal** | **No standard benchmark** |
| Willingness to pay for packs | **No academic evidence** |

**Proposed research eval (not yet built):** Load pack P distilled from agent A’s goal G in env E₁; measure success of agent B on G′ in env E₂ with/without P, stratified by pack format (Trajectory / Workflow / Insight) and buyer expertise — mirrors MTL + MemoryArena + expertise reversal.

---

## Part 10 — Failure modes & open problems (expanded)

| Problem | Evidence | Severity for packaging |
|---------|----------|------------------------|
| **Raw trajectory as product** | MTL: negative transfer via brittle anchoring | Critical |
| **Capture ≠ distill** | ReadAgent gists; Mem0 extraction; Trace2Skill parallel consolidation | Critical |
| **DR incomplete for reusers** | Karsenty: <50% of DR questions answered | High |
| **No short-term payoff** | Conklin/SCE; Shum & Hammond cost/benefit | High (adoption) |
| **Stale facts** | LongMemEval KU/TR; MemoryArena constraints | High |
| **Privacy / cumulative leakage** | OCELOT; AMP; AAAI runtime privacy | High (esp. sellable packs) |
| **Expertise mismatch** | Kalyuga expertise reversal | High |
| **Retrieval noise** | Wrong memory hurts (context-research corpus; SRACG) | High |
| **Retrieval / ledger inject cost** | External memory adds latency/noise (survey tradeoffs); do **not** cite LLM sparse-attn/RAG FPGA profiling ([arXiv:2603.29002](https://arxiv.org/abs/2603.29002)) as agent-ledger evidence — that paper's 22–97% figures are for **model-internal memory-processing pipelines** (Prepare/Relevancy/Retrieve/Apply), not session packs | Medium |
| **Eval mismatch** | LoCoMo ≠ MemoryArena | High (false confidence) |
| **False validation from memory** | MTL negative-transfer mode | Medium |
| **Multi-agent ledger merge** | Hu et al. 2025 survey: emerging frontier / underexplored | Medium |
| **Liability / wrong lesson** | No case law in this corpus; analogy to DR “outdated advice” | ? Assumed risk |

---

## Part 11 — Mapping to host-project ledger artifacts (reference)

| Host construct | Ledger role |
|---------------|-------------|
| `*_intent.yaml` | Goal + constraints (procedural spine) |
| `*_feedback.yaml` | Issue trail / iteration ledger |
<<<<<<< HEAD
| Operator session handoffs | Session distillate for next operator/agent (private operator vault, not in OSS repo) |
=======
| `docs/handoff/*.md` | Session distillate for next operator/agent |
>>>>>>> origin/main
| `patterns/*_patterns.yaml` | Distilled workflows (AWM-like) |
| `docs/research/**/*.md` | Evidence base — not runtime ledger |
| Conversation-health monitors | Meta-ledger on conversation health (orthogonal) |

**Split rule:** Research/patterns inform humans; the **runtime** ledger for agents = intents, feedback, handoffs, memory tools. Strategy/reference documents never wire into pipeline code.

---

## Part 12 — Bibliography (selected, by theme)

### Design rationale & reuse (incl. capture cost / empirics)

- Potts, C. & Bruns, G. (1988). Recording the reasons for design decisions. ICSE. [doi:10.5555/55823.55863](https://doi.org/10.5555/55823.55863)
- Conklin, J. & Begeman, M. L. (1988). gIBIS. ACM TOIS. [doi:10.1145/58566.59297](https://doi.org/10.1145/58566.59297)
- MacLean, A., Young, R. M., Bellotti, V., & Moran, T. P. (1991). Questions, Options, and Criteria. Human-Computer Interaction. [doi:10.1207/s15327051hci0603](https://doi.org/10.1207/s15327051hci0603)
- Buckingham Shum, S. (1992). A Cognitive Analysis of Design Rationale Representation. PhD thesis.
- Buckingham Shum, S. & Hammond, N. (1994). Argumentation-based design rationale: what use at what cost? IJHCS.
- Karsenty, L. (1996). An empirical evaluation of design rationale documents. CHI. [doi:10.1145/238386.238462](https://doi.org/10.1145/238386.238462)
- Lee, J. Design Rationale Systems survey. AI Magazine (capture cost / NCR gIBIS).
- Conklin, J. Dialog Mapping / QuestMap SCE case study. [cognexus.org](http://www.cognexus.org/ConklinCaseStudyChapter.pdf)
- Medeiros, A. P. et al. (2008). Kuaba approach. AI EDAM. [doi:10.1017/s0890060408000279](https://doi.org/10.1017/s0890060408000279)
- Kolodner, J. (1993/2005). Case-Based Reasoning. MIT Press.
- González, P. A. (2000). Applying knowledge modelling and CBR to software reuse. IEE Proc. Softw. [doi:10.1049/ip-sen:20000897](https://doi.org/10.1049/ip-sen:20000897)
- Sycara, K. & Navinchandra, D. CADET — Case-based Design Tool (CMU). [CADET docs](https://www.cs.cmu.edu/afs/cs/project/cadet/ftp/docs/CADET.html)
- Khan, M. (2014). Applications of CBR in Software Engineering: a systematic mapping study. IET Softw. [doi:10.1049/iet-sen.2013.0127](https://doi.org/10.1049/iet-sen.2013.0127)
- Minor, M. et al. (2021). Transfer Learning Operators for Process-oriented CBR. AIKE.
- Leveraging successes and failures in CBR adaptation (ACIIDS / Springer 2023). [doi:10.1007/978-981-99-5834-4_3](https://doi.org/10.1007/978-981-99-5834-4_3)

### Learning science (incl. expertise reversal)

- Collins, A., Brown, J. S., & Holum, A. (1991). Cognitive Apprenticeship. American Educator.
- van Gog, T., Paas, F., & van Merriënboer, J. J. G. (2004). Process-oriented worked examples. Instructional Science. [doi:10.1023/B:TRUC.0000021810.70784.b0](https://doi.org/10.1023/B:TRUC.0000021810.70784.b0)
- Kim, Y. R. (2015). Effects of Worked Examples on Far Transfer. UNC dissertation. [doi:10.17615/8td7-ta18](https://doi.org/10.17615/8td7-ta18)
- Sweller, J. & Cooper, G. A. (1985). Worked example effect.
- Kalyuga, S., Ayres, P., Chandler, P., & Sweller, J. (2003). The expertise reversal effect. Educational Psychologist.
- Kalyuga, S. (2007). Expertise reversal effect and learner-tailored instruction. Educational Psychology Review.

### Inference-time agent memory (core)

- Packer, C. et al. (2023). MemGPT. [arXiv:2310.08560](https://arxiv.org/abs/2310.08560)
- Park, J. S. et al. (2023). Generative Agents. [arXiv:2304.03442](https://arxiv.org/abs/2304.03442)
- Shinn, N. et al. (2023). Reflexion. NeurIPS 2023. [arXiv:2303.11366](https://arxiv.org/abs/2303.11366)
- Zhao, A. et al. (2024). ExpeL. [arXiv:2308.10144](https://arxiv.org/abs/2308.10144)
- Wang, G. et al. (2023). Voyager. NeurIPS 2023 ALOE workshop. [arXiv:2305.16291](https://arxiv.org/abs/2305.16291)
- Wang, Z. et al. (2024). Agent Workflow Memory. [arXiv:2409.07429](https://arxiv.org/abs/2409.07429)
- Liu, Y., Si, C., Narasimhan, K. R., & Yao, S. (2025). Contextual Experience Replay. ACL. [aclanthology.org/2025.acl-long.694](https://aclanthology.org/2025.acl-long.694/) · [arXiv:2506.06698](https://arxiv.org/abs/2506.06698)
- Lee, M. et al. (2024). ReadAgent. ICML. [proceedings.mlr.press/v235/lee24c.html](https://proceedings.mlr.press/v235/lee24c.html)
- Chhikara, P. et al. (2025). Mem0. [arXiv:2504.19413](https://arxiv.org/abs/2504.19413)
- Latimer, C. et al. (2025). Hindsight. [arXiv:2512.12818](https://arxiv.org/abs/2512.12818)
- Xu, W. et al. (2025). A-MEM. NeurIPS 2025. [arXiv:2502.12110](https://arxiv.org/abs/2502.12110)
- Sumers, T. et al. (2024). CoALA. [arXiv:2309.02427](https://arxiv.org/abs/2309.02427)

### Trajectories, skills & cross-domain transfer

- Jimenez, C. et al. SWE-agent. [swe-agent.com](https://swe-agent.com/latest/usage/trajectories/)
- SWE-Replay (2026). [arXiv:2601.22129](https://arxiv.org/abs/2601.22129)
- AgentHER (2026). [arXiv:2603.21357](https://arxiv.org/abs/2603.21357)
- Ni, J. et al. (2026). Trace2Skill. [arXiv:2603.25158](https://arxiv.org/abs/2603.25158)
- Kim, K., Kang, M., Kim, T., Yang, Y., Ren, M., & Hwang, S. J. (2026). Memory Transfer Learning for coding agents. [arXiv:2604.14004](https://arxiv.org/abs/2604.14004) · [memorytransfer.github.io](https://memorytransfer.github.io/)

### Surveys, benchmarks, staleness

- Hu, Y. et al. (2025). Memory in the Age of AI Agents. [arXiv:2512.13564](https://arxiv.org/abs/2512.13564)
- He, Z. et al. (2026). MemoryArena. [arXiv:2602.16313](https://arxiv.org/abs/2602.16313)
- Wu, D. et al. (2025). LongMemEval. ICLR. [arXiv:2410.10813](https://arxiv.org/abs/2410.10813)
- Yan, S. et al. (2025). Memory-R1. [arXiv:2508.19828](https://arxiv.org/abs/2508.19828)

### Privacy (agent trajectories / memory)

- OCELOT (2026). Inference-leakage budgets for privacy-preserving LLM agents. [arXiv:2606.12341](https://arxiv.org/abs/2606.12341)
- Wu, J., Hu, M., Zhu, J., Wang, J., & Jin, Y. Agent-Memory Protocol (AMP). PMLR. [proceedings.mlr.press/v317/wu26a.html](https://proceedings.mlr.press/v317/wu26a.html)
- From rights to runtime: Privacy engineering for agentic AI. AAAI (2026). [doi:10.1002/aaai.70036](https://doi.org/10.1002/aaai.70036)

### Industry context engineering

- LangChain / Lance Martin (2025). Context engineering for agents — Write / Select / Compress / Isolate. [langchain.com/blog/...](https://www.langchain.com/blog/context-engineering-for-agents) · [rlancemartin.github.io](https://rlancemartin.github.io/2025/06/23/context_engineering/)
- Anthropic (2025). Effective context engineering for AI agents (note-taking, compaction, memory tool). [anthropic.com/engineering/...](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

---

## Part 13 — Research verdict (no product)

| Claim | Status |
|-------|--------|
| Frozen model + agent + tool-updated external ledger improves outcomes | **Supported** — many systems, benchmarks |
| Ledger should include goals, failures, workflows — not raw chat | **Supported** — DR + memory papers |
| Cross-session / cross-task reuse of distilled experience works | **Supported** — ExpeL, AWM, CER, CBR |
| Cross-domain transfer works if **abstracted** (Insight / skill / SoP) | **Supported** — MTL (+3.7%); Trace2Skill (large cross-model gains) |
| Raw trajectory packs transfer safely across stacks | **Refuted / high risk** — MTL negative transfer |
| Captured DR alone answers reuser questions | **Insufficient** — Karsenty <50% |
| Industrial DR capture without short-term payoff sticks | **Historically failed** — QuestMap / Shum cost literature |
| Someone else's packaged exhausted path is a known product category | **Still not in literature** — mechanism yes, SKU no |
| High LoCoMo score ⇒ pack helps buyer complete builds | **Refuted as general rule** — MemoryArena gap |
| Packs need privacy redaction + versioning | **Supported** — OCELOT/AMP; LongMemEval KU |

**Strongest research-backed packing rule (pre-product):** Prefer **Insight / skill / workflow** layers over **raw trajectories**; stamp **versions + expiry**; **redact** before export; **fade** scaffolding by buyer expertise.

**Stop line for this doc:** Product shape, pricing, and wedge topics are **out of scope** for this document.

---

## Part 14 — Source audit log (v1.2 — 2026-07-17)

Cross-check of load-bearing claims against primary sources (arXiv abs/html, DOI pages, ACL Anthology, IET Digital Library). Confirmed numbers left unchanged when verified.

| Issue | Was | Fix |
|-------|-----|-----|
| QOC inventors | Attributed to Buckingham Shum PhD | **MacLean et al. 1991**; Shum PhD analyzes QOC |
| CBR DOI `ip-sen:20000897` | Katalagarianos & Vassiliou 1995 | **P.A. González, IEE Proc. Softw. 2000** |
| CADET | “Kolodner et al.” | **Sycara & Navinchandra (CMU)** |
| Worked-examples far-transfer DOI | “McLaren et al.” | **Kim 2015** dissertation; claim softened to mixed far-transfer evidence |
| Write/Select/Compress/Isolate | Implied Anthropic-led | **LangChain / Lance Martin** taxonomy; Anthropic = note-taking / memory tool / compaction |
| Voyager venue | “NeurIPS 2023” (main) | **NeurIPS 2023 ALOE workshop** |
| A-Mem | Venue only | Added **[arXiv:2502.12110](https://arxiv.org/abs/2502.12110)** |
| AWM metrics | Loose “relative success” both benches | Mind2Web = **relative step-wise SR**; WebArena = **relative success rate** |
| CER | Thin cite | **Yitao Liu et al.**; **+51.0%** relative; **[arXiv:2506.06698](https://arxiv.org/abs/2506.06698)** |
| LongMemEval drop / temporal | “~30%” only; “~7–11% temporal recall” | Abstract **~30%**; long-context vs oracle **30–60%**; temporal **recall 6.8–11.3%** |
| MemoryArena wording | “fail” | Paper: **“perform poorly”** |
| Latency 22–97% (`2603.29002`) | Implied agent-ledger cost | **Retracted as ledger evidence** — paper profiles LLM memory-processing pipeline (sparse attn / RAG / MemAgent), not external session ledgers |
| IET CBR mapping | Vague “IET Softw. Eng.” | **Khan (2014)** [doi:10.1049/iet-sen.2013.0127](https://doi.org/10.1049/iet-sen.2013.0127) |
| AMP | “Wu et al., PMLR” thin | **Wu, Hu, Zhu, Wang, Jin** + PMLR URL |
| MTL | Year/arXiv only | Authors **Kim et al.** |
| Trace2Skill +57.65 pp | — | ✓ Verified (abstract) |
| MTL ~3.7% | — | ✓ Verified (Pass@3 avg) |
| Reflexion 91% vs GPT-4 80% HumanEval | — | ✓ Verified (NeurIPS 2023 paper) |
| Hindsight 39% → 83.6% | — | ✓ Verified (abstract; LongMemEval, same backbone) |
| Memory survey “Hu et al.” | Suspected wrong | ✓ Kept — **Yuyang Hu** is first author on `2512.13564` |
| AWM Mind2Web “+8.9–14.0 abs as gaps widen” | Conflated offline relative with online abs | **v1.3:** Table 4 online step-SR deltas **7.4–8.9 / 3.6–3.8 / 14.0–16.9**; offline separate |
| Memory-R1 “ACL 2026” | Unverified year | **v1.3:** cite arXiv; venue year **ACL 2025** per Semantic Scholar (Anthology page not confirmed in this pass) |

**Still thin / operator note:** MasterDesign™ / ISA-88 / Bosch AOI industry rows remain ~ practitioner packaging analogies (not LLM-agent RCTs). MAR confirmation-bias claim on Reflexion cites MAR preprint (`2512.20845`) — replication claim, not Reflexion authors’ own limitation section. Karsenty >50%/<50% left as in CHI abstract/body from prior pass (PDF fetch timed out this pass).

---

*Document compiled 2026-07-17 (v1.0). Weak areas expanded 2026-07-17 (v1.1). Source audit + corrections 2026-07-17 (v1.2–v1.3). Relocated + genericized 2026-07-17 (v1.4). Next update: new transfer / MemoryArena releases.*
