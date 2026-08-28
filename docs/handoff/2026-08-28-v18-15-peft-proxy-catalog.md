# Handoff — Stele v18.15 PEFT proxy catalog

**Date:** 2026-08-28  
**Tip:** v18.15.0 (Phase 191)  
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

## Tip of tree (this session)

| Gate | Result |
|---|---|
| Version | `18.15.0` (`stele_core.__version__`, both `pyproject.toml`, intent, README, PRD, TECH_SPEC) |
| pytest | **287 passed** |
| `examples/proof_run.py` | ALL PASS |
| MCP `@mcp.tool()` count | **2003** |
| CLI smoke | `stele sdt-dim --help`, `stele sdt-ssm --help`, `stele mef-cpu --help` |

---

## Pattern per slice (do not invent a new one)

1. Grep **CLI + ops + modules** for the prefix. Never reuse.
2. Live-fetch the arXiv/OpenReview **title** before shipping.
3. Two papers → two modules → 6 ops each (4 apply + 1 report-only flag + loop plan).
4. Wire: `ops.py`, `cli.py`, MCP, harness `*_shaped_report`, `__init__`, `examples/proof_run.py`, tests.
5. Docs: PRD +11 UC, TECH_SPEC next `7.xxx`, ROADMAP, frontiers, CHANGELOG, version bump.
6. Install **then** smoke CLI. Pytest races pip.

Report-only flags must return `apply: False`.

### Last three shipped slices

| Version | Phase | Papers | Prefixes | MCP after |
|---|---|---|---|---|
| 18.13 | 189 | CaRA + LoRETTA | `cra_*` / `ltt_*` | 1979 |
| 18.14 | 190 | C3A + BOFT | `c3a_*` / `bof_*` | 1991 |
| 18.15 | 191 | SDT + MEFT | `sdt_*` / `mef_*` | 2003 |

---

## Not done (pending)

**Next — Phase 192 / v18.16:** two unused PEFT papers, +12 MCP → **2015**, UC-1979–1989, TECH_SPEC §7.191, frontiers §§408–409.

**Git:** Commit only on explicit operator go. No branches. No stash. No push without go.

---

## Pointers

- Intent: `stele_system_intent.yaml`
- Prior handoff: `docs/handoff/2026-08-24-v18-14-peft-proxy-catalog.md`
