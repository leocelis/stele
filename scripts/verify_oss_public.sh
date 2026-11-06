#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "OSS verify FAIL: $*" >&2; exit 1; }

# git grep ships with git, so this check cannot pass just because a search tool
# is missing. Exit 0 = found, 1 = clean, anything else = the scan did not run.
scan() {
  local message=$1 pattern=$2 rc=0
  shift 2
  git grep --untracked -nIE "$pattern" -- "$@" || rc=$?
  case "$rc" in
    0) fail "$message" ;;
    1) ;;
    *) fail "scan could not run (git grep exit $rc): $message" ;;
  esac
}

scan "git conflict markers in public tree" '^<<<<<<<|^=======|^>>>>>>>' \
  packages docs examples README.md SECURITY.md ROADMAP.md CHANGELOG.md

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
scan "private vault path token in adopter-facing docs" "${_DOC_NEEDLE}" "${DOC_PATHS[@]}"
scan "internal planning identifier in adopter-facing docs" "${_PLAN_NEEDLE}" "${DOC_PATHS[@]}"

# Source tree — vault path token only outside tests (ledger path strings are C8 redaction tests).
scan "private vault path token in production package code" "${_DOC_NEEDLE}" \
  packages ':(exclude)**/tests/**'

echo "OSS verify PASS"
