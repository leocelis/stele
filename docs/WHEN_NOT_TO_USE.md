# When not to use Stele

Stele is a **governed experiential-memory ledger**, not a general chat memory layer.

Do **not** use Stele when:

1. **You want automatic fact extraction from every user message** — Stele requires distilled entries and external-oracle promotion (intent C7).
2. **You need “remember my name/preferences” personalization at scale** — extract-and-retrieve memory stacks are simpler for that workload.
3. **You have no oracle** (CI, human reviewer, EIF/IVD, or equivalent) — quarantined entries never become searchable.
4. **You want zero setup and a managed cloud with self-serve keys** — deploy Stele yourself (see `deploy/README.md`) or use a hosted memory SaaS until then.
5. **You only need ephemeral session context** — use the host’s conversation buffer; Stele is for cross-session, cross-agent experience.

Use Stele when agents repeat the same failures, you need erasure proofs, or you want memory that cannot self-promote without evidence.

See `docs/COMPARISON.md` for product-level tradeoffs.
