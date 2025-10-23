#!/bin/bash
# Script: audit_socials.sh
# Purpose: Audit and clean social media references (TikTok) in the repository
# 
# This script:
# 1. Creates a new branch (audit/socials-cleanup) for the cleanup work
# 2. Searches for social media references and generates inventory files
# 3. Replaces documentary mentions of TikTok according to README guidelines
# 4. Runs basic checks (npm/pytest if applicable)
# 5. Commits changes and creates a draft Pull Request
#
# Usage:
#   ./scripts/audit_socials.sh
#
# Environment variables:
#   GITHUB_TOKEN - Required for creating PRs (will use gh CLI or GitHub API)
#
# Note: This script does NOT include tokens or credentials. 
#       GITHUB_TOKEN must be provided by the CI environment.

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
BRANCH_NAME="audit/socials-cleanup"
BASE_BRANCH="${BASE_BRANCH:-main}"
INVENTORY_FILE="audit_socials_inventory.txt"
CODE_HITS_FILE="code_integration_hits.txt"
CANDIDATES_DUP_FILE="candidates_dup.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Create audit branch
log_info "Creating branch: ${BRANCH_NAME}"
git fetch origin "${BASE_BRANCH}" || true
git checkout -b "${BRANCH_NAME}" "origin/${BASE_BRANCH}" 2>/dev/null || git checkout "${BRANCH_NAME}"

# Step 2: Generate inventory of social media references
log_info "Generating inventory of social media references..."

# Search for TikTok mentions in all text files (excluding git, node_modules, etc.)
log_info "Searching for 'TikTok' references..."
grep -r -i "tiktok" . \
    --exclude-dir=".git" \
    --exclude-dir="node_modules" \
    --exclude-dir=".venv" \
    --exclude-dir="__pycache__" \
    --exclude-dir="dist" \
    --exclude-dir="build" \
    --exclude="*.pyc" \
    --exclude="*.log" \
    --line-number \
    > "${INVENTORY_FILE}" || echo "No TikTok references found" > "${INVENTORY_FILE}"

log_info "Inventory saved to: ${INVENTORY_FILE}"

# Step 3: Identify code integration points (Python, JavaScript, shell scripts)
log_info "Identifying code integration points..."
grep -r -i "tiktok" . \
    --include="*.py" \
    --include="*.js" \
    --include="*.ts" \
    --include="*.sh" \
    --exclude-dir=".git" \
    --exclude-dir="node_modules" \
    --exclude-dir=".venv" \
    --exclude-dir="__pycache__" \
    --line-number \
    > "${CODE_HITS_FILE}" || echo "No TikTok references found in code" > "${CODE_HITS_FILE}"

log_info "Code integration points saved to: ${CODE_HITS_FILE}"

# Step 4: Find potential duplicate mentions (for manual review)
log_info "Finding potential duplicate mentions..."
# Extract just the matched lines (not file paths) and sort to find duplicates
grep -h -r -i "tiktok" . \
    --exclude-dir=".git" \
    --exclude-dir="node_modules" \
    --exclude-dir=".venv" \
    --exclude-dir="__pycache__" \
    --exclude="*.pyc" \
    --exclude="*.log" \
    2>/dev/null | sort | uniq -c | sort -rn > "${CANDIDATES_DUP_FILE}" || echo "No duplicates found" > "${CANDIDATES_DUP_FILE}"

log_info "Duplicate candidates saved to: ${CANDIDATES_DUP_FILE}"

# Step 5: Replace documentary mentions of TikTok in README and docs
log_info "Replacing documentary mentions of TikTok..."

# Only replace in documentation files, not in code
# This is a safe, conservative approach - replace "TikTok" with "Social Platform" in docs
if [ -f "README.md" ]; then
    log_info "Processing README.md..."
    # Make a backup
    cp README.md README.md.bak
    
    # Replace "TikTok" with "Social Platform" in documentation context
    # This is a simple replacement - adjust based on actual requirements
    sed -i 's/TikTok Viral ML System/Social Media Viral ML System/g' README.md
    sed -i 's/TikTok/Social Platform/g' README.md
    
    # Check if changes were made
    if ! diff -q README.md README.md.bak > /dev/null; then
        log_info "README.md updated"
        rm README.md.bak
    else
        log_info "No changes needed in README.md"
        mv README.md.bak README.md
    fi
fi

# Process other documentation files
for doc_file in docs/*.md CHANGELOG.md; do
    if [ -f "$doc_file" ]; then
        log_info "Processing ${doc_file}..."
        cp "$doc_file" "${doc_file}.bak"
        sed -i 's/TikTok/Social Platform/g' "$doc_file"
        
        if ! diff -q "$doc_file" "${doc_file}.bak" > /dev/null; then
            log_info "${doc_file} updated"
            rm "${doc_file}.bak"
        else
            log_info "No changes needed in ${doc_file}"
            mv "${doc_file}.bak" "$doc_file"
        fi
    fi
done

# Step 6: Run basic checks
log_info "Running basic checks..."

# Check if npm is available and package.json exists
if [ -f "package.json" ] && command -v npm &> /dev/null; then
    log_info "Running npm checks..."
    npm install --quiet || log_warn "npm install had issues"
    npm test || log_warn "npm tests failed (non-blocking)"
else
    log_info "Skipping npm checks (not applicable)"
fi

# Check if Python tests exist
if [ -f "requirements.txt" ] && command -v python3 &> /dev/null; then
    log_info "Running Python checks..."
    
    # Only run tests if pytest is available
    if python3 -c "import pytest" 2>/dev/null; then
        PYTHONPATH=. python3 -m pytest -q --maxfail=1 || log_warn "Python tests failed (non-blocking)"
    else
        log_info "pytest not installed, skipping Python tests"
    fi
else
    log_info "Skipping Python checks (not applicable)"
fi

# Step 7: Commit changes
log_info "Committing changes..."

# Add generated inventory files
git add "${INVENTORY_FILE}" "${CODE_HITS_FILE}" "${CANDIDATES_DUP_FILE}"

# Add any modified documentation files
git add README.md docs/ CHANGELOG.md 2>/dev/null || true

# Check if there are changes to commit
if git diff --staged --quiet; then
    log_warn "No changes to commit"
else
    git commit -m "audit: Generate social media reference inventory and clean docs

- Generated inventory of TikTok references
- Identified code integration points
- Found duplicate mention candidates
- Replaced documentary mentions in README and docs
- Ran basic checks (npm/pytest)

Files generated:
- ${INVENTORY_FILE}
- ${CODE_HITS_FILE}
- ${CANDIDATES_DUP_FILE}"

    log_info "Changes committed successfully"
fi

# Step 8: Push branch
log_info "Pushing branch to origin..."
git push -u origin "${BRANCH_NAME}" --force || log_error "Failed to push branch"

# Step 9: Create draft PR using GitHub CLI or API
log_info "Creating draft Pull Request..."

if command -v gh &> /dev/null; then
    # Using GitHub CLI
    log_info "Using GitHub CLI to create PR..."
    gh pr create \
        --title "[audit] Social media references cleanup" \
        --body "## Automated Social Media Audit

This PR was automatically generated by the audit_socials.sh script.

### Changes:
- Generated inventory of social media references
- Identified code integration points that need manual review
- Replaced documentary mentions of TikTok in README and documentation
- Ran basic checks (npm/pytest)

### Generated Files:
- \`${INVENTORY_FILE}\` - Complete inventory of all social media references
- \`${CODE_HITS_FILE}\` - References in code that need manual review
- \`${CANDIDATES_DUP_FILE}\` - Potential duplicate mentions

### Next Steps:
1. Review the inventory files (also available as workflow artifacts)
2. Manually update code references as needed
3. Run full test suite
4. Remove 'draft' status when ready to merge

⚠️ **Security Note**: This PR only modifies documentation. Code changes require manual review." \
        --base "${BASE_BRANCH}" \
        --head "${BRANCH_NAME}" \
        --draft || log_warn "Failed to create PR with gh CLI"
else
    log_warn "GitHub CLI (gh) not found. PR must be created manually."
    log_info "Branch ${BRANCH_NAME} has been pushed to origin."
    log_info "Please create a draft PR manually at: https://github.com/your-repo/compare/${BASE_BRANCH}...${BRANCH_NAME}"
fi

log_info "Script completed successfully!"
log_info "Review the generated inventory files:"
log_info "  - ${INVENTORY_FILE}"
log_info "  - ${CODE_HITS_FILE}"
log_info "  - ${CANDIDATES_DUP_FILE}"
