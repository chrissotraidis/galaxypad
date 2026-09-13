#!/usr/bin/env bash
# Run independently of local game data, generated modules, or dependency checkouts.
set -euo pipefail
root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$root"

# Permit only the dependency gitlink, never source/data files under ref/.
tracked="$(git ls-files --stage | awk '
  $1 == "160000" && $4 == "ref/ModernGekko" { next }
  { sub(/^[^\t]*\t/, ""); print }
')"
prohibited="$(printf '%s\n' "$tracked" | rg -i '(^|/)(ref|generated|extracted|game-data|runtime-data|modules|saves|save|nand|docs/artifacts|artifacts)/|\.(iso|gcm|rvz|wia|wbfs|gcz|dol|rel|rso|dylib|ipa|xcarchive|mobileprovision|provisionprofile|p12|pem|key|cer|gci|sav|raw|crash|ips|trace|log|profraw|profdata)$|(^|/)GameData\.bin$' || true)"
if [[ -n "$prohibited" ]]; then
  echo "prohibited tracked material:" >&2
  echo "$prohibited" >&2
  exit 1
fi

if git grep -l -I -E 'BEGIN [A-Z ]*PRIVATE KEY|github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}' -- .; then
  echo "possible credential material found" >&2
  exit 1
fi

if git grep -l -I -E '(^|[^[:alnum:]_])/Users/[^ ]+' -- . ':!scripts/check-public-content.sh' ':!tests/test-mobile-diagnostics.mm'; then
  echo "personal absolute path found" >&2
  exit 1
fi

env_files="$(git ls-files | rg '(^|/)\.env($|\.)' | rg -v '(^|/)\.env\.example$' || true)"
if [[ -n "$env_files" ]]; then
  echo "credential environment files must not be tracked:" >&2
  echo "$env_files" >&2
  exit 1
fi

echo "Public content checks passed"
