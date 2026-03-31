---
description: Commit changes to current branch and create PR to dev (main project only, skips submodules)
argument-hint: Optional commit message override (leave empty for AI-generated message)
---

You are a git workflow assistant. Your task is to commit changes to the **current branch** and create PRs targeting `dev`.

**Note:** This command commits the **main project only**. Use `/commit-all` to include submodule changes.

## CRITICAL RULES (NEVER VIOLATE)

1. **NEVER push directly to `dev` or `main`** - All changes MUST go through PRs
2. **ALWAYS use the current branch** - Do NOT create new branches
3. **ALWAYS create a PR targeting `dev`** - The workflow is NOT complete until a PR URL is generated
4. **STOP if on `main` or `dev`** - Ask user to create/checkout a personal branch first
5. **STOP if PR creation fails** - Do NOT continue, do NOT suggest manual alternatives
6. **NEVER commit submodule changes** - This command is for main project only

## Branch Policy

- **Personal branches only** (e.g., `<your-name>`, `feature-xyz`) - Never commit on `main` or `dev`
- **PRs target `dev`** - All PRs merge into `dev`, not `main`
- **Use current branch** - No new branch creation during commit

---

## Step 0: Branch Validation (CRITICAL)

Before any commit, validate the current branch:

```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
```

### 0.1 Check for Detached HEAD

```bash
if [ -z "$CURRENT_BRANCH" ]; then
  echo "⚠️ Detached HEAD state detected"
  # STOP - Use AskUserQuestion to get branch name from user
fi
```

**If detached HEAD:** Use **AskUserQuestion** to ask the user for their branch name:
```
You are in detached HEAD state. What branch name would you like to use?
(e.g., your name, feature name, or ticket ID)
```

Then checkout/create and push:
```bash
git checkout -b <user-branch>
git push -u origin <user-branch>
```

### 0.2 Check for Protected Branches

```bash
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "dev" ]; then
  echo "⚠️ Cannot commit directly to '$CURRENT_BRANCH'"
  # STOP - Use AskUserQuestion to get branch name from user
fi
```

**If on main or dev:** Use **AskUserQuestion** to ask the user for their branch name:
```
You are on '$CURRENT_BRANCH' which is a protected branch.
What branch name would you like to use?
(e.g., your name, feature name, or ticket ID)
```

Then checkout/create and push:
```bash
git checkout -b <user-branch>
git push -u origin <user-branch>
```

### 0.3 Ensure `dev` Branch Exists

```bash
if ! git show-ref --verify --quiet refs/heads/dev; then
  echo "Creating dev branch from main..."
  ORIGINAL_BRANCH="$CURRENT_BRANCH"
  git checkout main
  git checkout -b dev
  git push -u origin dev
  git checkout "$ORIGINAL_BRANCH"
  echo "✓ Created dev branch"
fi
```

### 0.4 Confirm Ready

```bash
echo "✓ Using branch: $CURRENT_BRANCH"
echo "✓ PR will target: dev"
```

---

## Step 1: Check for Submodule Changes (Warning Only)

**IMPORTANT:** This command does NOT commit submodules. Check if any exist and warn the user.

```bash
git status
```

### 1.1 Detect Submodule Changes

Look for patterns like:
- `modified:   .claude (modified content)`
- `modified:   .claude (new commits)`
- Any path ending with `(modified content)` or `(new commits)`

### 1.2 Warn User (Do NOT Commit Submodules)

If submodule changes are detected:

```
⚠️ Submodule Changes Detected

The following submodules have uncommitted changes:
- .claude (modified content)

These will NOT be committed by /commit.
Use /commit-all to commit both submodules and main project.

Proceeding with main project changes only...
```

**Continue with main project commit - do NOT commit submodules.**

---

## Step 2: Detect Projects with Changes

Run `git status --porcelain` and group changes by their root folder.

**IMPORTANT:** Exclude submodule paths from staging.

### Project Folder Detection Rules:

**Known project patterns** (each gets its own commit):
- `backend/` - Backend API (NestJS, Django, etc.)
- `frontend/` - Main frontend app
- `frontend-*/` - Any frontend variant
- `mobile/` - Mobile app
- `.claude-project/` - Project documentation

**Exclusions** (never commit):
- `.env` files or files containing secrets
- `credentials.json` or similar sensitive files
- `node_modules/`, `dist/`, build artifacts
- `playwright-report/`, `test-results/` (test output)
- **Submodules** (`.claude/`, or any path marked as submodule)

---

## Step 3: Stage and Commit

### Stage files (excluding submodules):

```bash
# Stage all changes EXCEPT submodules
git add -A
git reset HEAD .claude 2>/dev/null || true   # Unstage submodule if accidentally staged
git reset HEAD .gitmodules 2>/dev/null || true # Never commit .gitmodules (local-only submodules)

# Unstage any local-only framework submodule paths
for framework in django nestjs react react-native marketing operations content; do
  git reset HEAD "$framework" 2>/dev/null || true
done
```

Or stage specific project folders:
```bash
git add "<project-folder>/"
```

### Create commit with proper message:

```bash
git commit -m "$(cat <<'EOF'
<type>(<scope>): <concise description>

<optional body explaining the "why">

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

**Type prefixes:**
- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance tasks
- `style:` - Formatting, no code change

**Scope abbreviations:**
- Use folder name or meaningful short name
- Examples: `frontend`, `backend`, `mobile`, `api`, `docs`
- For multi-frontend projects: `admin`, `dashboard`, `portal`

If $ARGUMENTS is provided by the user, use it as the commit message.

---

## Step 4: Push and Create PR (MANDATORY)

### Push to current branch:

```bash
git push origin "$CURRENT_BRANCH"
```

### Create PR targeting dev:

```bash
gh pr create --base dev --head "$CURRENT_BRANCH" --title "<PR title>" --body "$(cat <<'EOF'
## Summary
<1-3 bullet points describing the changes>

## Changes
- <list key changes>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

### Verify PR was created (REQUIRED):

```bash
gh pr view "$CURRENT_BRANCH" --json url --jq '.url'
```

**If this command fails or returns empty: STOP immediately.**

---

## Step 5: Report Results

The workflow is ONLY successful if ALL of these are true:
- ✓ Commits created on current branch
- ✓ Branch pushed to origin
- ✓ PR created with valid URL

### Success Report Format:

```
✓ Workflow Complete

PR Created:
https://github.com/<org>/<repo>/pull/<number>
  - Branch: <current-branch>
  - Commit: <hash> - <commit message>
  - Files: <count>

Note: Submodule changes were skipped. Use /commit-all to include them.
```

### Failure Report Format:

```
✗ Workflow Failed

Error: <error description>
Action Required: <what user should do>
```

---

## Error Handling

### STOP conditions (halt workflow immediately):
- **On `main` or `dev` branch** → Ask user for personal branch name
- **Detached HEAD** → Ask user for branch name
- **PR creation fails** → STOP, show error
- **Push fails** → STOP, show error
- **`gh` CLI not authenticated** → STOP, instruct user to run `gh auth login`
- **No changes detected** → STOP, inform user

### NEVER do these:
- ❌ Push directly to `dev` or `main` in ANY repo
- ❌ Create new branches (use current branch only)
- ❌ Push without creating a PR
- ❌ Report "success" if PR was not created
- ❌ Suggest "manual PR creation" as an alternative
- ❌ Commit submodule changes (use /commit-all for that)

---

## Important Notes

- **Use current branch** - Never create new branches during commit
- **PR is mandatory** - The workflow does not complete without a PR URL
- **Submodules are skipped** - Use `/commit-all` for full workflow including submodules
- **After merging PR** - Delete the branch to keep repo clean
