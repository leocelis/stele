# Contributing to Stele

Thanks for your interest. Stele is in its **design phase** — the architecture is
locked in [`stele_system_intent.yaml`](stele_system_intent.yaml) and there is no
implementation yet, so contributions look different from a typical code repo.

## What helps right now

- **Research corrections.** Every load-bearing claim in [`docs/research/`](docs/research/)
  cites a primary source (arXiv ID, venue, or canonical URL) and has survived a
  source audit (audit logs: ledger doc Part 14, storage doc Part 11). If you find
  a claim that misstates its source, open an issue with the primary-source
  evidence. This is the highest-value contribution possible today.
- **Pattern challenges.** [`docs/patterns/`](docs/patterns/) distills the research
  into design rules. If you know of published evidence that contradicts a finding
  (FF-n) or an operational pattern (OP-n), bring the citation.
- **Intent review.** The seven constraints in the system intent are open to
  scrutiny before implementation starts — conflicts, missing edge cases, or
  unsatisfiable pairs are exactly what the review gate exists to catch.

## Ground rules

- **Evidence over opinion.** Changes to research or pattern files require a
  primary source. Vendor blogs and community benchmarks are admitted only as
  `~`-marked (contested) items, never as `✓` evidence.
- **Intent before implementation.** Once code lands, every change tracks back to
  a constraint in an intent file. Code that satisfies no constraint doesn't merge.
- **Claims stay honest.** Anything not test-enforced or benchmark-measured is
  labeled as such. Do not promote a thesis to a fact in any document.

## Process

1. Open an issue describing the correction/challenge with sources.
2. For text changes, a PR referencing the issue. Keep audited numbers intact
   unless the correction *is* the audited number, with the primary source cited
   in the PR.
3. Doc-only changes update the affected file's version/changelog notes.

## Code contributions

Not yet — the roadmap ([`ROADMAP.md`](ROADMAP.md)) gates implementation on
human sign-off of the intent (Phase 0 gate). Watch the repo; Phase 1 will open
with the schema and the six-op library, each with its own module intent and
test contract.
