---
name: qa-scan
description: "Universal QA orchestrator — diagnose, fix, verify across all layers with three execution modes (quick/standard/deep)"
user-invocable: true
argument-hint: "[module] [--quick|--deep] [--check data|api|guard|form|ui] [--diff [ref]] [--check-only]"
---

# QA Scan — Universal QA Orchestrator

Orchestrates the full QA pipeline: build project profile, detect features, run layer checks (Tier 1 + Tier 2), cross-reference findings, and optionally apply fixes.

Replaces: `qa-fix`, `qa-page`

## Execution Modes

| Mode | Flag | Scope | Tier 1 | Tier 2 | Feature Map |
|------|------|-------|--------|--------|-------------|
| **Quick** | `--quick` | Changed files only (`git diff`) | Yes (Critical/High only) | No | No |
| **Standard** | _(default)_ | Changed features | Yes (all severities) | Yes (mapped RPs only) | Yes |
| **Deep** | `--deep` | Entire project | Yes (all severities) | Yes (all RPs) | Yes + cross-feature |

## Usage

```bash
/qa-scan                           # Standard mode on changed features
/qa-scan --quick                   # Quick mode on changed files
/qa-scan --deep                    # Deep mode on entire project
/qa-scan auth                      # Standard mode on auth module only
/qa-scan --check data              # Run only data layer
/qa-scan --check data,api          # Run data + api layers
/qa-scan --diff dev                # Scope to changes since diverging from dev branch
/qa-scan --check-only              # Diagnose only, do not fix
```

## Shared Conventions

Scoring, framework detection, output format: see `qa-shared/reference.md`.
Project Profile schema: see `qa-shared/profile-schema.md`.
Reasoning Patterns: see `qa-shared/reasoning-catalog.md`.

---

## Step 0: Project Profile

### 0a: Stack Detection
1. Load `.qa-profile.yaml` if it exists
2. Re-detect stack from `package.json` and imports (update if changed)
3. Preserve manually-set context fields from existing profile
4. If context fields missing (first run), infer from `CLAUDE.md` / `README.md`
5. Save updated profile to `.qa-profile.yaml`
6. Output detected profile summary

### 0b: Feature Map (skip in Quick mode)
1. Scan the codebase dynamically to build the Feature Map:
   - `crud_list_detail`: page files + route definitions + API service calls
   - `realtime`: socket/SSE imports and event handlers
   - `role_views`: features present in multiple apps or role-gated
   - `aggregations`: count/sum/total fields in list columns, dashboard cards
   - `soft_delete_entities`: entities with deletedAt column
   - `state_machines`: enum/status columns with 3+ values
   - `file_uploads`: multer/upload interceptors
   - `scheduled_tasks`: cron decorators, job processors
2. Output Feature Map summary (category counts)

### 0c: Feature → RP Mapping (skip in Quick mode)
1. Apply the mapping table from `profile-schema.md`
2. For Standard mode: filter to only features touched by `git diff`
3. For Deep mode: apply to ALL features
4. Output: which RPs will be applied and where

### 0d: Compile Check
1. Run the project's type-check command (e.g., `npm run type-check`, `tsc --noEmit`)
2. If compile errors exist: report them first, as they may cause false findings
3. Continue with analysis regardless (compile errors are a separate concern)

---

## Step 1: DIAGNOSE

Execute layer skills in order. Each layer runs its Tier 1 checks, then applicable Tier 2 reasoning patterns.

### Layer Execution Order

| Order | Layer | Skill | Condition |
|-------|-------|-------|-----------|
| 1 | Data | qa-data | Backend detected |
| 2 | API | qa-api | Backend + frontend detected |
| 3 | Guard | qa-guard | Auth system detected |
| 4 | Form | qa-form | Input forms detected |
| 5 | UI | qa-ui | Frontend detected |

For each layer:
1. Run all applicable Tier 1 checks (filtered by gates from Project Profile)
2. Run applicable Tier 2 RPs (mapped from Feature Map in Step 0c)
3. Collect findings with severity, file location, and description

### Quick Mode Behavior
- Skip Feature Map and Tier 2 entirely
- Identify changed files via `git diff HEAD` (or `git diff --cached` if staged)
- Map changed files to layers:
  - `*.entity.ts`, `*.migration.ts` → qa-data
  - `*.controller.ts`, `*.service.ts`, `*.repository.ts` → qa-api + qa-guard
  - `*.dto.ts` → qa-form
  - `*.tsx`, `*.vue`, `*.component.ts` → qa-ui
- Run only Critical and High severity Tier 1 checks on those files
- Output: minimal report, Critical/High findings only

### Standard Mode Behavior
- Build full Feature Map
- Identify changed features via `git diff`:
  - Map changed files to modules/features
  - Determine which Feature Map categories are affected
- Run Tier 1 (all severities) on changed features
- Run Tier 2 (only RPs mapped to changed features)
- Output: full report for changed features

### Deep Mode Behavior
- Build full Feature Map
- Run Tier 1 (all severities) on ALL features
- Run Tier 2 (ALL applicable RPs on ALL features)
- Cross-feature analysis:
  - Compare filter conditions across ALL aggregation queries
  - Verify role_views parity across ALL roles
  - Check soft_delete ripple across ALL queries
- Output: comprehensive project-wide report with score

### Cross-Layer Auto-Triggers

After all layers report Tier 1 findings, check for cross-layer implications:

```
New entity/column found (qa-data)     → queue qa-form for that entity
New endpoint found (qa-api)           → queue qa-guard for that endpoint
Status/enum field found (qa-data)     → queue qa-form BQ3 + qa-ui RP-02
Delete endpoint found (qa-api)        → queue qa-data RP-08
Aggregation field found (qa-api)      → queue qa-ui RP-07
Identity field in DTO (qa-form)       → queue qa-guard permission check
```

No manual trigger map needed. The orchestrator matches findings by entity/field name.

---

## Step 2: FIX (unless `--check-only`)

Group findings by file and apply fixes in dependency order:

1. **Data layer fixes** (migrations, constraints, schema)
   - Run type-check after data fixes
2. **API layer fixes** (endpoints, response shapes, error handling)
3. **Guard layer fixes** (missing guards, permission checks)
4. **Form layer fixes** (DTO/Zod/Form consistency)
   - Run type-check after form fixes
5. **UI layer fixes** (states, buttons, modals, lists, layout)
   - Run linter after UI fixes

### Fix Safety Rules
- Never modify test files unless the test is testing the wrong behavior
- Never remove existing functionality — only add missing checks/filters/handlers
- If a fix is ambiguous (multiple valid approaches), skip and note as "manual fix needed"
- After each fix group, verify the fix compiles before proceeding

---

## Step 3: VERIFY

1. Re-read ONLY modified files
2. Re-check ONLY flagged items from Step 1
3. Classify each finding:
   - **RESOLVED**: Issue no longer present after fix
   - **UNRESOLVED**: Issue persists (fix didn't work or was skipped)
   - **REGRESSION**: New issue introduced by fix
4. Fix regressions once (max 1 retry)
5. Output final verification report

---

## Step 4: LEARN (auto, after every fix)

Capture what QA missed so it doesn't miss it again. Runs automatically after Step 3 completes — no user action needed.

### 4a: Classify each fixed issue

For each RESOLVED finding from Step 3, determine its origin:

| Origin | Criteria | Action |
|--------|----------|--------|
| **Existing check missed it** | A Tier 1 check exists that should have caught this, but didn't fire (wrong Gate, insufficient detection pattern, or too narrow scope) | → Fix the check in skill.md + add regression pattern |
| **No check exists** | No Tier 1 check covers this bug class | → Draft a new `[CANDIDATE]` check |
| **Business logic gap** | Bug is project-specific (intentional divergence, domain rule) | → Add to `QA_BUSINESS_DECISIONS.md` |
| **Reasoning pattern gap** | A Tier 2 RP should have caught this through tracing, but the strategy was incomplete | → Refine the RP in `reasoning-catalog.md` |

### 4b: Write regression pattern

For each fixed issue classified as "existing check missed" or "no check exists", append to `QA_REGRESSION_PATTERNS.md` at the project root:

```markdown
## [Pattern Name]
- **Bug**: [One-line description of what went wrong]
- **Root Cause**: [Why QA missed it — wrong gate, narrow detection, missing check]
- **Detection Rule**: [Concrete grep/scan pattern to find this class of bug]
- **Fix Location**: [file:line — what the fix looks like]
- **Check**: [Check ID that should catch this, or "NEW → [skill]" if none exists]
- **Project**: [Project name — for cross-project pattern tracking]
- **Added**: [Date]
```

If `QA_REGRESSION_PATTERNS.md` doesn't exist, create it from the template in `qa-shared/reference.md`.

### 4c: Draft candidate checks (when no check exists)

When a bug has no matching Tier 1 check:

1. Determine which layer skill it belongs to (qa-data, qa-api, qa-guard, qa-form, qa-ui)
2. Draft a check entry with all fields:
   ```
   | [NEXT-ID] | [CANDIDATE] [Check Name] | **[Severity]** | [Gate] | [Description with Detection and Fix guidance] |
   ```
3. Append to the appropriate skill's check table with `[CANDIDATE]` prefix in the Check name
4. `[CANDIDATE]` checks are included in subsequent QA runs immediately
5. After 3 runs where the check fires correctly (no false positives), promote by removing the `[CANDIDATE]` prefix

### 4d: Update global skill (cross-project learning)

If the regression pattern or candidate check is **not project-specific** (i.e., it could apply to any project with the same stack):

1. Add the check/pattern to the **global skill** (`~/.claude/skills/qa-*/skill.md`)
2. Sync to `claude-operations/skills/qa/` (source of truth)
3. All future projects automatically benefit

Skip this step if the pattern is purely project-specific (e.g., a business rule unique to this domain).

### 4e: Output learning summary

```
━━━ Step 4: Learning Capture ━━━
Patterns learned: N
  [NEW] qa-ui Y-39: WebView height uses MediaQuery instead of Expanded (from login safe-area fix)
  [FIX] qa-ui Y-36: Added Android system nav bar to detection description
  [BIZ] QA_BUSINESS_DECISIONS.md: password limit 20/72 is intentional

Regression patterns added: N → QA_REGRESSION_PATTERNS.md
Candidate checks added: N → qa-ui/skill.md [CANDIDATE]
Global skill updated: Yes/No
```

### Learning in Quick Mode

Quick mode (`--quick`) does NOT run Step 4 automatically (quick = speed priority).
However, if `QA_REGRESSION_PATTERNS.md` exists, Quick mode always checks regression patterns (takes <1s).

### Learning in Check-Only Mode

`--check-only` mode skips Step 2 (FIX) and Step 3 (VERIFY), so Step 4 is also skipped.
However, `--check-only --learn` forces Step 4 to run on the diagnostic findings — useful for "what would QA have missed?" analysis without fixing.

---

## Output Format

### Quick Mode Output
```
━━━ QA Quick Scan ━━━
Files scanned: N (from git diff)
Duration: ~Ns

[CRITICAL] file.ts:42 — Description
[HIGH] file.ts:88 — Description

Result: N critical, M high findings
```

### Standard Mode Output
```
━━━ QA Standard Scan ━━━
Profile: [framework] | [domain] | [language]
Features changed: N
RPs applied: RP-03, RP-07

[Layer: Data]
  Tier 1: N findings
  Tier 2 (RP-03): M findings

[Layer: API]
  ...

Score: NN/100 — [PASS|NEEDS ATTENTION|FAIL]
```

### Deep Mode Output
```
━━━ QA Deep Scan ━━━
Profile: [framework] | [domain] | [language]
Feature Map: N features across M categories
RPs applied: RP-01 through RP-12

[Detailed per-layer report...]

[Cross-Feature Analysis]
  Aggregation Parity: N checked, M inconsistent
  Soft Delete Ripple: N checked, M missing filters
  Role Parity: N features, M with gaps

Overall Score: NN/100 — [PASS|NEEDS ATTENTION|FAIL]
```

---

## Layer Skill Reference

Each layer skill is invoked by qa-scan but can also run independently:

| Skill | Command | Layer |
|-------|---------|-------|
| qa-data | `/qa-data [module]` | Schema, migrations, dead columns, soft delete |
| qa-api | `/qa-api [module]` | CRUD completeness, API sync, response shapes |
| qa-guard | `/qa-guard [module]` | Auth guards, security, permissions |
| qa-form | `/qa-form [module]` | Entity → DTO → Schema → Form consistency |
| qa-ui | `/qa-ui [module] [--sub category]` | All UI/UX checks (states, buttons, modals, lists, a11y, layout, perf, nav, i18n) |
| qa-runtime | `/qa-runtime [--viewport mobile\|multi]` | Playwright browser-based testing |
