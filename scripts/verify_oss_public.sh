#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "OSS verify FAIL: $*" >&2; exit 1; }

if rg -n '^<<<<<<<|^=======|^>>>>>>>' packages docs examples README.md SECURITY.md ROADMAP.md CHANGELOG.md; then
  fail "git conflict markers in public tree"
fi

# Adopter-facing docs and deploy — no operator / private-vault narrative.
DOC_PATHS=(docs examples README.md SECURITY.md CHANGELOG.md ROADMAP.md deploy)
if rg -n 'limitless/' "${DOC_PATHS[@]}"; then
  fail "limitless/ path in adopter-facing docs"
fi
if rg -n 'ada-cluster|Trello|card M[0-9]|Cosmic Rewind|PR-AP[0-9]|leocelis/workspace' "${DOC_PATHS[@]}"; then
  fail "internal planning identifier in adopter-facing docs"
fi

# Source tree — limitless only outside tests (ledger/tenants strings are C8 redaction tests).
if rg -n 'limitless/' packages --glob '!**/tests/**'; then
  fail "limitless/ in production package code"
fi

echo "OSS verify PASS"
