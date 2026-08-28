# Contributing to Stele

## What helps

- **Bug reports** with a minimal failing entry JSON + expected vs actual state.
- **Constraint tests** that fail on the unfixed code and pass after (intent C1–C8).
- **Research corrections** in [`docs/research/`](docs/research/) with primary sources.
- **Protocol adapters** that speak the six-op surface only (no third-party imports into core).

## Ground rules

- **Intent before implementation.** Changes track a constraint in `stele_system_intent.yaml` or a module intent.
- **Core stays pure.** `stele-core` remains stdlib-only: no LLM, no network, no DB drivers on the write path.
- **Evidence over opinion.** Research/pattern edits need a primary source.
- **No private operator paths** in public artifacts, examples, or docs (adversarial rejection tests use synthetic private-shaped strings only).

## Dev setup

```bash
make install
make check
```

## Process

1. Open an issue (or reference an intent constraint id).
2. Implement on `master` with tests.
3. Do not push or publish to PyPI without maintainer approval.
