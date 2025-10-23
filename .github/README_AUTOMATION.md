# Automation Workflows Documentation

This document describes the automated workflows configured for this repository.

## Social Media Audit Workflow

### Purpose

The `audit_socials.yml` workflow automates the process of auditing and cleaning social media references (specifically TikTok mentions) in the repository. This helps maintain consistent branding and prepare for potential platform migrations.

### What It Does

The workflow executes the `scripts/audit_socials.sh` script, which:

1. **Creates a new branch** (`audit/socials-cleanup`) for the cleanup work
2. **Generates inventory files**:
   - `audit_socials_inventory.txt` - Complete inventory of all social media references
   - `code_integration_hits.txt` - References found in code files (Python, JavaScript, etc.)
   - `candidates_dup.txt` - Potential duplicate mentions for review
3. **Replaces documentary mentions** - Updates documentation files (README.md, docs/, etc.) to use generic terms instead of specific platform names
4. **Runs basic checks** - Executes npm and pytest tests if applicable
5. **Creates a draft Pull Request** - Automatically opens a PR with all changes for review

### How to Run Manually

#### Using GitHub UI (Recommended)

1. Go to the **Actions** tab in the GitHub repository
2. Select **"Audit Social Media References"** from the workflow list
3. Click **"Run workflow"** button
4. Select the base branch (default: `main`)
5. Click **"Run workflow"** to start

#### Using GitHub CLI

```bash
# Run with default settings (main branch)
gh workflow run audit_socials.yml

# Run with custom base branch
gh workflow run audit_socials.yml -f base_branch=develop
```

### Scheduled Execution

The workflow is scheduled to run automatically:

- **Daily at 09:00 UTC**
- Can be disabled by commenting out the `schedule` trigger in the workflow file

### Running Locally

You can also run the audit script locally on your machine:

```bash
# 1. Ensure you're on the base branch
git checkout main
git pull origin main

# 2. Set environment variables (optional)
export BASE_BRANCH=main

# 3. Run the script
bash scripts/audit_socials.sh
```

**Local Requirements:**
- Git configured with appropriate credentials
- Bash shell
- Python 3.11+ (if running tests)
- Node.js 18+ (if running npm tests)
- GitHub CLI (`gh`) installed and authenticated (for PR creation)

### Generated Artifacts

The workflow uploads the following files as artifacts:

| File | Description | Retention |
|------|-------------|-----------|
| `audit_socials_inventory.txt` | Complete list of all social media references | 30 days |
| `code_integration_hits.txt` | References found in code files that need manual review | 30 days |
| `candidates_dup.txt` | Potential duplicate mentions sorted by frequency | 30 days |

**To download artifacts:**
1. Go to the workflow run page
2. Scroll to the **Artifacts** section at the bottom
3. Click on `social-media-audit-{run-number}` to download

### Security Considerations

⚠️ **Important Security Notes:**

1. **No Secrets in Scripts** - The `audit_socials.sh` script does NOT contain any hardcoded tokens or credentials
2. **GITHUB_TOKEN** - The workflow uses the built-in `GITHUB_TOKEN` for authentication (automatically provided by GitHub Actions)
3. **Code Review Required** - The script only modifies documentation files automatically. Code changes require manual review
4. **Draft PRs** - All PRs created by this workflow are marked as DRAFT and require explicit review before merging
5. **Limited Permissions** - The workflow only has `contents: write` and `pull-requests: write` permissions

### What Gets Modified

#### Automatically Modified (by script):
- `README.md` - Platform names replaced with generic terms
- Documentation files in `docs/` directory
- `CHANGELOG.md` (if exists)

#### Requires Manual Review:
- Python files (`.py`)
- JavaScript/TypeScript files (`.js`, `.ts`)
- Shell scripts (`.sh`)
- Configuration files
- Any code files identified in `code_integration_hits.txt`

### Reviewing the Draft PR

After the workflow runs:

1. **Check the Actions tab** - Verify the workflow completed successfully
2. **Download artifacts** - Review the inventory files to understand what was found
3. **Find the draft PR** - Look for a PR titled `[audit] Social media references cleanup`
4. **Review changes**:
   - Check the documentation changes
   - Review the inventory files (attached to PR)
   - Identify code files that need manual updates
5. **Manual updates** - If needed, checkout the branch and update code files
6. **Run tests** - Execute full test suite locally
7. **Mark as ready** - Remove draft status when satisfied
8. **Merge** - Merge the PR using your standard process

### Troubleshooting

#### Workflow fails with "Permission denied"
- Check that the workflow has proper permissions in the repository settings
- Verify that the `GITHUB_TOKEN` has the required scopes

#### No PR is created
- The script requires GitHub CLI (`gh`) or will skip PR creation
- Check the workflow logs for warnings
- You can manually create a PR from the `audit/socials-cleanup` branch

#### Tests fail during the workflow
- The script continues even if tests fail (non-blocking)
- Review the test failures in the workflow logs
- Fix any issues in the generated PR before merging

#### Script finds no changes
- If no social media references are found, the script will still create inventory files
- The PR may be empty if all references have already been cleaned

### Customization

To customize the workflow behavior:

1. **Change schedule** - Edit the `cron` expression in `audit_socials.yml`
2. **Modify search terms** - Edit the `grep` commands in `scripts/audit_socials.sh`
3. **Add more checks** - Extend the script with additional validation steps
4. **Change replacement logic** - Update the `sed` commands in the script

### Example Workflow Run

```
1. Workflow triggered (manual or scheduled)
2. Repository checked out
3. Dependencies installed (Python, Node)
4. Script execution:
   ├── Create branch: audit/socials-cleanup
   ├── Search for references → audit_socials_inventory.txt
   ├── Identify code hits → code_integration_hits.txt
   ├── Find duplicates → candidates_dup.txt
   ├── Update documentation files
   ├── Run tests (npm/pytest)
   └── Commit and push changes
5. Create draft PR
6. Upload artifacts
7. Generate summary
```

### Support

For issues or questions about this automation:

1. Check the workflow logs in the Actions tab
2. Review this documentation
3. Open an issue in the repository with the `automation` label
4. Include relevant error messages and workflow run links

---

**Last Updated:** 2025-10-23  
**Workflow Version:** 1.0  
**Maintained by:** Repository maintainers
