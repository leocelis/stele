# Stele OSS guide — read this first

**Audience:** adopters, contributors, strangers on GitHub.

## Read order (30 minutes)

1. `README.md` — wedge + install + core MCP URL
2. `docs/QUICKSTART.md` — pip, library, CLI, MCP core, doctor
3. `docs/COMPARISON.md` — vs Mem0 / Zep / LangMem
4. `docs/WHEN_NOT_TO_USE.md` — disqualifiers
5. `docs/TECH_SPEC.md` §1–7 — schema + MCP core tools only
6. `stele_system_intent.yaml` — constraints C1–C8 (if implementing)

## Skip unless you are implementing

- `docs/PRD.md` (3k+ lines — product archive)
- `docs/research/GOVERNED_EXPERIENTIAL_MEMORY_FRONTIERS_2026.md` (research corpus)
- Full MCP surface (`stele-mcp-full`, `/sse` without `/core`) — PEFT research library

## Surfaces

| Surface | Tools | Use |
|---------|-------|-----|
| `stele-mcp` / `/core/sse` | 35 | Production agent memory |
| `stele-mcp-full` / `/sse` | ~2000 | Operator research reproduction |

## Verify locally

```bash
make check
make verify-oss
python examples/quickstart_core.py
python examples/proof_run.py
```
