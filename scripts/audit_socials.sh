#!/usr/bin/env bash
set -euo pipefail

# scripts/audit_socials.sh
# Usage: ./scripts/audit_socials.sh
# Requirements: git with push access, gh CLI (optional), jq (optional)
# This script:
# - creates branch audit/socials-cleanup from detected main branch
# - generates audits (inventory, integration hits, candidate duplicates)
# - replaces documentary "TikTok" mentions using README as source of truth
# - commits changes in separate commits, runs basic tests, pushes branch and creates a draft PR
#
# SECURITY: Never include secrets or tokens in this script.

main_branch="$(git remote show origin | sed -n 's/.*HEAD branch: //p')"
if [ -z "$main_branch" ]; then
  if git show-ref --verify --quiet refs/heads/main; then
    main_branch="main"
  else
    main_branch="master"
  fi
fi

echo "Main branch detected: $main_branch"
git fetch origin "$main_branch"
git checkout -b audit/socials-cleanup "origin/$main_branch"

# Find README (first match)
readme_candidates=(README.md README.rst README.adoc README)
readme_file=""
for f in "${readme_candidates[@]}"; do
  if [ -f "$f" ]; then
    readme_file="$f"
    break
  fi
done

socials_found=()
if [ -n "$readme_file" ]; then
  echo "Using README file: $readme_file"
  while IFS= read -r line; do
    l="$(echo "$line" | tr '[:upper:]' '[:lower:]')"
    for s in twitter x instagram facebook linkedin youtube github mastodon reddit tiktok; do
      if echo "$l" | grep -qi "$s"; then
        socials_found+=("$s")
      fi
    done
  done < "$readme_file"
  # unique
  socials_found=($(printf "%s\n" "${socials_found[@]}" | awk '!seen[$0]++'))
fi

if [ "${#socials_found[@]}" -gt 0 ]; then
  echo "Socials in README: ${socials_found[*]}"
  tgt=()
  for s in "${socials_found[@]}"; do
    if [ "$s" != "tiktok" ]; then
      tgt+=("$s")
    fi
  done
  if [ "${#tgt[@]}" -gt 0 ]; then
    replacement="$(IFS=, ; echo "${tgt[*]}")"
  else
    replacement="redes sociales"
  fi
else
  echo "No socials found in README. Defaulting to 'redes sociales'."
  replacement="redes sociales"
fi

echo "Documentation replacement: '$replacement'"

# 1) Inventory of mentions
grep -RIn --exclude-dir=.git -E "tiktok|tik tok|tik_tok|twitter|\\bx\\b|instagram|facebook|linkedin|youtube|mastodon|github|reddit|gologin|GoLogin|ultralytics|ultralytic|google cloud|gcloud" . > audit_socials_inventory.txt || true
git add audit_socials_inventory.txt
git commit -m "audit: add inventory of social media references" || true

# 2) Heuristic code integration hits
grep -RIn --exclude-dir=.git -E "tiktok|tik_tok|gologin|GoLogin|ultralytics|gcloud|google cloud" . | grep -iE "import|require|http|api|endpoint|client|auth" > code_integration_hits.txt || true
if [ -s code_integration_hits.txt ]; then
  git add code_integration_hits.txt
  git commit -m "audit: probable integration hits for manual review" || true
fi

# 3) Candidate duplicates by filename
git ls-files | grep -Ei "(social|tiktok|twitter|instagram|gologin|gcloud|ultralytics)" > candidates_dup.txt || true
git add candidates_dup.txt
git commit -m "audit: candidate files for consolidation" || true

# 4) Replace documentary 'TikTok' in docs
doc_patterns=('*.md' '*.rst' '*.txt' 'docs/*.*')
for pat in "${doc_patterns[@]}"; do
  for f in $(git ls-files -- "$pat" 2>/dev/null || true); do
    if file "$f" | grep -qE 'text'; then
      if grep -qi "tiktok" "$f"; then
        sed -E -i.bak -e "s/([Tt]ik[Tt]ok)/${replacement}/gI" "$f" || true
        rm -f "${f}.bak"
        git add "$f"
        git commit -m "docs: replace isolated 'TikTok' mentions in $f with '${replacement}'" || true
      fi
    fi
  done
done

# 5) Flag code integrations (do not auto-change)
grep -RIn --exclude-dir=.git -E "tiktok|tik_tok|gologin|GoLogin|ultralytics|gcloud|google cloud" . | grep -iE "import|require|http|api|endpoint|client|auth" > code_integration_hits.txt || true
if [ -s code_integration_hits.txt ]; then
  git add code_integration_hits.txt
  git commit -m "audit: list probable integration code locations for manual review" || true
fi

# 6) Run common tests (best effort)
echo "Running available tests (best-effort)"
if [ -f package.json ] && command -v npm >/dev/null 2>&1; then
  npm install --no-audit --no-fund || true
  npm test || echo "npm test failed or not defined"
fi
if (ls | grep -E "pyproject.toml|requirements.txt|setup.py" >/dev/null 2>&1) && command -v pytest >/dev/null 2>&1; then
  pytest || echo "pytest failed or not defined"
fi

# 7) Push branch and create draft PR (if gh installed)
git push -u origin HEAD

pr_title="[audit] Socials cleanup — sustituir TikTok y purgar integraciones"
pr_body="Resumen y artefactos:\n- inventory: audit_socials_inventory.txt\n- code hits: code_integration_hits.txt\n- candidates: candidates_dup.txt\n\nSe reemplazaron las menciones documentales de 'TikTok' por: ${replacement}.\nNO se modificaron integraciones activas; están listadas para revisión."

if command -v gh >/dev/null 2>&1; then
  gh pr create --title "$pr_title" --body "$pr_body" --base "$main_branch" --head "$(git rev-parse --abbrev-ref HEAD)" --draft
  echo "Draft PR created with gh CLI."
else
  echo "gh CLI not available. Create a draft PR from branch audit/socials-cleanup -> $main_branch and use the generated files."
fi

echo "Done. Review audit_socials_inventory.txt, code_integration_hits.txt, candidates_dup.txt and the draft PR."
