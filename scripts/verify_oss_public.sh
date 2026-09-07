#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "OSS verify FAIL: $*" >&2; exit 1; }

if rg -n '^<<<<<<<|^=======|^>>>>>>>' packages docs examples README.md SECURITY.md ROADMAP.md CHANGELOG.md; then
  fail "git conflict markers in public tree"
fi

# Adopter-facing docs and deploy — no operator / private-vault narrative.
# Assemble needles from fragments so this public script stays grep-clean.
DOC_PATHS=(docs examples README.md SECURITY.md CHANGELOG.md ROADMAP.md deploy)
_VAULT_A=limit
_VAULT_B=less/
_COSMIC_A=Cosmic
_COSMIC_B=' Rewind'
_WS_A='leocelis/'
_WS_B=workspace
_ADA_A=ada-
_ADA_B=cluster
_TREL_A=Trel
_TREL_B=lo
_PR_A=PR-
_PR_B='AP[0-9]'
_CARD_A='card '
_CARD_B='M[0-9]'
_DOC_NEEDLE="${_VAULT_A}${_VAULT_B}"
_PLAN_NEEDLE="${_ADA_A}${_ADA_B}|${_TREL_A}${_TREL_B}|${_CARD_A}${_CARD_B}|${_COSMIC_A}${_COSMIC_B}|${_PR_A}${_PR_B}|${_WS_A}${_WS_B}"
if rg -n "${_DOC_NEEDLE}" "${DOC_PATHS[@]}"; then
  fail "private vault path token in adopter-facing docs"
fi
if rg -n "${_PLAN_NEEDLE}" "${DOC_PATHS[@]}"; then
  fail "internal planning identifier in adopter-facing docs"
fi

# Source tree — vault path token only outside tests (ledger path strings are C8 redaction tests).
if rg -n "${_DOC_NEEDLE}" packages --glob '!**/tests/**'; then
  fail "private vault path token in production package code"
fi

echo "OSS verify PASS"
