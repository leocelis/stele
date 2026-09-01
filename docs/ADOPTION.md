# Adoption stories

## 1. CI-oracle promotion

**Problem:** Agent logs “fix worked” but the next agent ignores it.

**Flow:** `stele_add` (quarantine) → CI green → `stele_promote` with `test_result` evidence → `stele_search` before next task.

**Proof:** `examples/proof_run.py` PASS.

## 2. Human oracle (HITL)

**Problem:** Lessons need reviewer sign-off.

**Flow:** `stele_add` → `stele_list_contested` → human `stele_resolve_contested` or promote with human-review evidence (see TECH_SPEC).

## 3. Fleet pack export

**Problem:** Share redacted lessons across environments.

**Flow:** `stele_export` with subject allowlist → `stele_verify_pack` on receiver → `stele_hydrate` into local store.

**Proof:** `packages/stele-core/tests/test_export.py`.
