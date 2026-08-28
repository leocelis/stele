# Handoff — Stele v18.14 PEFT proxy catalog

**Date:** 2026-08-24  
**Tip:** v18.14.0 (Phase 190)  
**Status:** green, uncommitted unless an operator already committed  
**Audience:** next operator/agent continuing Stele

This is a session distillate. Full history lives in `CHANGELOG.md` and `ROADMAP.md`. Do not treat this file as a second product contract — the intent + PRD + TECH_SPEC win.

---

## What Stele is (do not drift)

Stele is a **governed experiential-memory ledger** for AI agents:

- Agents log what worked and what failed.
- New entries start **quarantined**.
- Promotion needs an **external oracle** (writer ≠ judge).
- Contested records **stay contested** until evidenced supersede — never auto-collapse.
- Core write path: **no LLM, no network, stdlib only**.

It is **not** a database product, **not** an LLM extractor, **not** a GPU trainer. PEFT modules in this repo are **proxies** (stdlib dicts + report-only flags) that encode *how* a memory update is allowed to land. They do not train neural nets.

---

## Tip of tree (verified this session)

| Gate | Result |
|---|---|
| Version | `18.14.0` (`stele_core.__version__`, both `pyproject.toml`, intent, README, PRD, TECH_SPEC) |
| pytest | **286 passed** |
| `examples/proof_run.py` | ALL PASS |
| MCP `@mcp.tool()` count | **1991** |
| CLI smoke | `stele c3a-kernel --help`, `stele bof-full --help` |

---

## Product core (shipped, stable)

These are the features operators actually use. Do not “improve” them by adding LLM calls to the write path.

| Area | What exists | Why |
|---|---|---|
| Add + quarantine | `add` starts locked | Unproven notes cannot teach the next agent |
| Promote | Oracle evidence required | Writer ≠ judge |
| Search + consumer scope | Scoped retrieval | No implicit universal / cross-tenant leak |
| Contested keep | `list_contested` / `resolve_contested` | Conflicts stay visible until evidenced |
| Supersede + stale | bi-temporal + `stale_policy` | Old advice expires |
| Pin / reinforce / reverify | living ledger | Important stays; weak gets checked |
| Erase / purge by provenance | `forget_compliance`, `purge_by_provenance` | Privacy + poison cleanup with a probe |
| Entangled suspects | neighborhood review queue | Linked junk after an id rewrite |
| Hygiene candidates | report-only | Clutter without silent delete |
| Lineage / belief-at / conflict | `lineage`, `belief_at`, `conflict_surface` | “What did we believe on date X?” |
| Pack export / hydrate / snapshot | redacted packs + snapshots | Backup and handoff without a hidden DB |
| Doctor / stats / timeline / diff | ops surface | Health, what changed, when |
| CLI + MCP | `stele` + `stele-mcp` | Same contract, two doors |

---

## PEFT proxy catalog (this long-running work)

Pattern per slice (do not invent a new one):

1. Grep **CLI + ops + modules** for the prefix. Never reuse. Never overwrite an existing module (`loraplus.py`, `mora.py` were the lesson).
2. Live-fetch the arXiv/OpenReview **title** before shipping. IDs lie; titles are the check.
3. Two papers → two modules → 6 ops each (4 apply + 1 report-only flag + loop plan).
4. Wire: `ops.py`, `cli.py` (`cmd_*` after `build_parser`), MCP `@mcp.tool()`, harness `*_shaped_report`, `__init__`, `examples/proof_run.py`, tests.
5. Docs: PRD +11 UC, TECH_SPEC next `7.xxx`, ROADMAP next phase, frontiers two new §§, CHANGELOG, version bump everywhere.
6. Install **then** smoke CLI (`from stele_core.cli import build_parser, cmd_*`). Pytest races pip.

Report-only flags (`*_tiny`, `*_heads`, `*_rank`, `*_full`, …) must return `apply: False`. They never silently overwrite.

### Last three shipped slices

| Version | Phase | Papers | Prefixes | MCP after | UC | TECH_SPEC | Frontiers |
|---|---|---|---|---|---|---|---|
| 18.12 | 188 | FacT (2212.03145) + LoTR (2402.01376) | `fct_*` / `ltr_*` | 1967 | 1935–1945 | §7.187 | §§400–401 |
| 18.13 | 189 | CaRA (ICML 2025, OpenReview:vexHifrbJg, no arXiv) + LoRETTA (2402.11417) | `cra_*` / `ltt_*` | 1979 | 1946–1956 | §7.188 | §§402–403 |
| 18.14 | 190 | C3A (2407.19342) + BOFT (2311.06243) | `c3a_*` / `bof_*` | 1991 | 1957–1967 | §7.189 | §§404–405 |

CaRA has **no arXiv** after live fetch. Do not invent one. BOFT prefix is `bof_*` because `bft_*` is BitFit. Do not collide with OFT (`oft_*`).

### Prefix landmines (never reuse)

| Prefix | Owner |
|---|---|
| `bft_*` | BitFit |
| `oft_*` | OFT (file `oft.py` already has butterfly helpers — do not overwrite) |
| `bof_*` | BOFT (v18.14) |
| `c3a_*` | C3A |
| `cra_*` | CaRA |
| `car_*` | CARE-LoRA |
| `ltt_*` | LoRETTA |
| `lrt_*` | LoRTA |
| `ltr_*` | LoTR |
| `mss_*` | MiSS (`miss.py`; arXiv:2409.15371 title is MiSS, not Bone) |
| `mor_*` | MoRA |
| `lpl_*` / loraplus module | LoRA+ (do not overwrite `loraplus.py`) |

Always grep again. This table is not complete.

---

## Not done (pending)

**Next implementation slice — Phase 191 / v18.15 (not started):**

- Two unused PEFT papers, stdlib proxies, +12 MCP → **2003**.
- UC-1968–1978, TECH_SPEC §7.190, ROADMAP Phase 191, frontiers §§406–407.
- Research started, **prefixes not locked:**
  - *Parameter-Efficient Fine-Tuning of State Space Models* (arXiv:2410.09016) — SDT / SDLoRA family.
  - *MEFT: Memory-Efficient Fine-Tuning through Sparse Adapter* (arXiv:2406.04984).
- Grep CLI+ops+modules before naming. Re-live-fetch titles. Do not ship if the prefix exists.

**Post-v18.14 (research / ops — not blocking):** see `ROADMAP.md` “Post-v18.14”. Includes: real-git adapter, NL→version mapping, native GEM/graph backend (non-goal for core), external gym adapters, hosted CRDT sync, HMAC watermarks, LLM-on-write-path (non-goal), hard `admit_gate`/`write_gate` opt-in, auto-delete on fade.

**Git:** this session did not commit or push. Commit only on explicit operator go. No branches. No stash.

---

## How to continue (one loop)

1. Read this file + `ROADMAP.md` current-tip + `CHANGELOG.md` head.
2. Grep prefixes. Live-fetch two titles.
3. New modules only. Wire. Docs. Version `18.15.0`.
4. `pip install -e` both packages, then CLI smoke, then full pytest + `examples/proof_run.py`.
5. Stop. One rec: group-commit on `master` if the operator wants a checkpoint. Do not push.

---

## Pointers

- Intent: `stele_system_intent.yaml`
- PRD: `docs/PRD.md`
- TECH_SPEC: `docs/TECH_SPEC.md`
- Frontiers: `docs/research/GOVERNED_EXPERIENTIAL_MEMORY_FRONTIERS_2026.md`
- Roadmap: `ROADMAP.md`
- Changelog: `CHANGELOG.md`
