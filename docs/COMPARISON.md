# Stele vs other agent memory stacks

Honest positioning for adopters. Stele is **not** trying to win every benchmark.

| Dimension | Stele | Mem0 | Zep / Graphiti | LangMem / host buffer |
|-----------|-------|------|----------------|------------------------|
| Primary goal | Governed experiential lessons | Extract + retrieve facts | Temporal KG + enterprise | Session / framework memory |
| Auto-extract every message | No (distilled ADD) | Yes | Yes (episodes) | Often |
| Promotion / oracle gate | Required (C7) | No | Partial | No |
| Writer can self-promote | No (tested) | N/A | Varies | Yes |
| Erasure / DELETE proofs | Yes (`forget_compliance`) | Varies | Varies | Usually none |
| Eval story | Task-outcome harnesses | Recall / LoCoMo marketing | Enterprise benchmarks | Host-dependent |
| Install | `pip install stele-core stele-mcp` | `pip install mem0ai` | Cloud + SDK | Built into stack |
| MCP default tools | 35 (core) | Varies | Varies | Varies |
| Core write path LLM | Forbidden (C5) | Uses LLM in pipeline | Uses LLM | Host-dependent |

**Choose Stele** when multiple agents share a codebase, failures repeat, and you already have CI or review as oracle.

**Choose Mem0** when you want fast personalization and automatic extraction.

**Choose Zep/Graphiti** when temporal knowledge graph + managed enterprise path fits.

**Choose host buffer** when memory is single-session and disposable.

See `docs/WHEN_NOT_TO_USE.md`.
