# QA Shared Reference

Common rules, scoring, and conventions shared by all QA skills.

This document defines shared rules, detection patterns, scoring mechanisms, and output conventions used by all `qa-*` skills. Individual QA skills reference this document to avoid duplication and ensure consistency.

---

## Execution Rule: Self-Verification & Auto-Retry

**Every Step in every QA skill MUST follow this rule:**

1. After completing a Step, output the Step's checklist
2. If any item is unchecked (`[ ]`), automatically re-execute ONLY the missing items
3. After re-execution, output the checklist again
4. Repeat until all items are `[x]` (maximum 3 retries)
5. If still incomplete after 3 retries, mark as `[SKIP]` with reason and proceed

**Output format for each Step:**
```
━━━ Step N Complete ━━━
[x] Item 1
[x] Item 2
[ ] Item 3 ← Missing detected, retrying...

━━━ Step N Retry 1/3 ━━━
[x] Item 3 ← Completed

Step N: ALL PASSED (N/N) → Proceeding to Step N+1
```

---

## File Validation (Common)

All QA skills validate the input file identically:

1. File path is provided
2. File exists and is readable
3. File extension is supported: `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.ts`, `.js`

**If validation fails:**
```
Error: [specific error message]
Usage: /qa-<skill> <page-or-component-file-path> [options]
```

---

## Frontend Framework Detection (Common)

All QA skills use the same framework detection logic. Read the target file and project's `package.json`:

| Signal | Framework |
|--------|-----------|
| `import ... from 'react'` or JSX/TSX + `react` in package.json | React |
| `<template>` + `<script>` + `.vue` extension | Vue |
| `@Component` decorator + `@angular/core` in package.json | Angular |
| `.svelte` extension | Svelte |
| `<form>` + no framework imports + `.html` extension | Plain HTML |

---

## Backend Framework Detection (Common)

Skills with `--backend` or `--depth full` support use this detection:

| Signal | Framework |
|--------|-----------|
| `@nestjs/common` in package.json | NestJS |
| `express` in package.json (no nest) | Express |
| `manage.py` in root | Django |
| `pom.xml` or `build.gradle` with spring-boot | Spring Boot |
| `composer.json` with laravel | Laravel |

If `--backend` path provided, use that path. Otherwise, look for sibling `backend/` directory.

---

## Mobile Wrapper Detection (Common)

Detects if the project wraps a web app inside a native container. Sets `apps[].type = "mobile-wrapper"` and enables platform gates (`webview_checks`, `has_native_wrapper`, `safe_area`).

| Wrapper | Detection Signal | Scan Path |
|---------|-----------------|-----------|
| Flutter WebView | `pubspec.yaml` with `flutter_inappwebview` or `webview_flutter` in dependencies | Sibling `mobile/`, `app/`, or any dir with `pubspec.yaml` |
| Capacitor | `capacitor.config.ts` or `capacitor.config.json` exists, or `@capacitor/core` in package.json | Project root or sibling dirs |
| React Native WebView | `react-native-webview` in package.json | Sibling `mobile/` or project root |
| Cordova | `config.xml` with `<widget>` element | Project root |
| Tauri | `tauri.conf.json` or `src-tauri/` directory | Project root |
| Expo | `app.json` with `"expo"` key + `expo` in package.json | Project root |
| None | No wrapper detected | — |

**When a wrapper is detected:**
1. Set `context.deployment = "webview-wrapped"`
2. Add appropriate platforms to `context.platform[]` (e.g., `["android-webview", "ios-webview"]`)
3. Gates `webview_checks`, `has_native_wrapper`, `safe_area`, `is_mobile_target` become `true`
4. QA checks gated on these values will activate automatically

**Native wrapper-level checks** (applied when `has_native_wrapper` is true):
- Flutter: `SafeArea` widget usage, `SystemNavigator.pop()` for exit, back button handling via `PopScope`
- Capacitor: `StatusBar` plugin, `SafeArea` plugin, `App.addListener('backButton')`, `Keyboard` plugin
- React Native: `SafeAreaView` component, `BackHandler` API, `KeyboardAvoidingView`

---

## Configuration File Support

All QA skills check for an optional `.qa-config.json` file at the project root:

```json
{
  "outputDir": ".claude-project/qa",
  "defaultDepth": "full",
  "backendPath": "backend/src",
  "scoring": {
    "passThreshold": 80,
    "needsAttentionThreshold": 60,
    "criticalPenalty": -15,
    "warningPenalty": -5,
    "maxBonus": 10
  },
  "ignore": {
    "files": ["**/test/**", "**/__mocks__/**"],
    "rules": []
  },
  "framework": {
    "frontend": "react",
    "backend": "nestjs",
    "uiLibrary": "shadcn"
  }
}
```

All fields are optional. Missing fields use defaults. If no config file exists, all defaults apply.

---

## Score Calculation (Standardized)

All QA skills use this scoring system:

### Base Rules

```
Base Score: 100
Deductions:
  - CRITICAL issue: -15 points each
  - WARNING issue: -5 points each
  - INFO issue: 0 points (no deduction)

Score = max(0, 100 - sum(deductions))

Bonus:
  - Bonuses are capped at +10 total (score cannot exceed 100)
  - Bonus items are skill-specific (see individual skills)

Final Score = min(100, Score + Bonus)
```

### Severity Definitions

| Severity | Description | Deduction |
|----------|-------------|-----------|
| **CRITICAL** | Security risk, data loss, UX-breaking bug, accessibility barrier | -15 points |
| **WARNING** | Potential bug, missing feature, degraded UX, inconsistency | -5 points |
| **INFO** | Nice-to-have improvement, documentation note, minor polish | 0 points |

### Status Thresholds

| Status | Score Range | Meaning |
|--------|------------|---------|
| **PASS** | >= 80 | Meets quality standards; minor improvements optional |
| **NEEDS ATTENTION** | 60-79 | Usable but has notable gaps; should address before release |
| **FAIL** | < 60 | Significant issues; must fix before release |

### Coverage Multiplier (Optional)

When analysis is incomplete (e.g., only 2 of 5 tables analyzed because imports unresolvable):

```
Adjusted Category Score = Raw Category Score × (analyzed_items / total_items)
```

This prevents inflated scores from partial analysis.

---

## Common Error Handling

All QA skills handle these common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| File not found | Invalid path provided | Check file path and try again |
| Unsupported file type | Wrong extension | Supported: `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.ts`, `.js` |
| Framework not detected | Unusual import structure or no package.json | Falls back to generic pattern scanning |
| Backend path not found | `--backend` invalid or no sibling `backend/` | Runs frontend-only analysis (`--depth shallow`) |
| Circular imports | Complex import chain | Breaks after 10 levels; notes as "unresolvable" |
| package.json not found | No package manager | Falls back to import-based detection only |

Skill-specific errors are listed in each skill's Error Handling section.

---

## Output Directory & File Naming

### Report Directory

Default: `.claude-project/qa/`
Override: `outputDir` in `.qa-config.json`

### File Naming Convention

```
[ComponentName]_[Feature]_QA_Report_[YYMMDD].md    — Full report
[ComponentName]_[Feature]_TestCases_[YYMMDD].md     — Test cases (if large)
```

Feature suffixes by skill:
| Skill | Feature Suffix |
|-------|---------------|
| `qa-data` | `Data` |
| `qa-api` | `API` |
| `qa-guard` | `Guard` |
| `qa-form` | `Form` |
| `qa-ui` | `UI` |
| `qa-runtime` | `Runtime` |
| `qa-scan` | `Scan` |

### Report Header Template

All reports use this header format:

```
+====================================================================+
|                   QA [Feature] Report                              |
+====================================================================+
|  Component:     [ComponentName]                                    |
|  File:          [file-path]                                        |
|  Framework:     [React + library / Vue + library / etc.]           |
|  Backend:       [NestJS / Express / N/A]  (if applicable)          |
|  Report Date:   [YYYY-MM-DD HH:MM]                                |
|  Depth:         [full / shallow]                                   |
|  Overall Score: [N]/100                                            |
|  Status:        [PASS | NEEDS ATTENTION | FAIL]                    |
+====================================================================+
```

---

## Cross-Skill Dependency Matrix

When analyzing a page, these skills are commonly run together:

| If you find... | Also run... | Reason |
|---------------|-------------|--------|
| Forms inside modals | `qa-form` on modal component | Form validation coverage |
| Modals that push history | `qa-ui --sub nav` | Back button may close modal or navigate |
| Tables with row actions | `qa-guard` | Row actions may be role-gated |
| Tables with data fetching | `qa-ui --sub states` | Tables need loading/error/empty states |
| Permission-gated delete | `qa-ui --sub modals` | Delete confirmation modal quality |
| Navigation after form submit | `qa-ui --sub nav` | Post-submit redirect correctness |
| API-driven pages | `qa-api` | API synchronization and caching |
| CRUD operations | `qa-api` | Create/Read/Update/Delete flow coverage |
| Database operations | `qa-data` | Data integrity and constraint validation |
| Complex layouts | `qa-ui --sub layout` | Responsive and layout consistency |

Use `qa-scan` to automatically run all relevant skills for a module.

---

## Cross-Skill Trigger System

Skills can declare **triggers** — conditions that, when found, recommend running specific checks in other skills. This creates cascading verification across skill boundaries.

### How Triggers Work

1. Each skill defines a `## Cross-Skill Triggers` section listing conditions and their target checks
2. **In orchestrated mode** (`qa-fix`, `qa-page`): The orchestrator reads triggers and queues the target checks automatically
3. **In standalone mode** (`/qa-inputs`): Triggers appear as recommendations in the report output — not auto-executed

### Current Trigger Map

| Source Skill | Condition | Target | Target Check |
|-------------|-----------|--------|-------------|
| qa-form | New Update DTO field (BQ1) | qa-guard | G-17 Role-Based Field Editability |
| qa-form | Identity field in service (#57) | qa-api | A-14 Service Layer Identity Bypass |
| qa-form | Sensitive field in response (BQ4) | qa-guard | G-18 Response Field Filtering |
| qa-form | Enum 3+ values (BQ3) | qa-data | D-12 Immutable Column Protection |
| qa-guard | New role-restricted endpoint | qa-form | BQ2 Role-Based Editability |
| qa-guard | Role mismatch (G-04) | qa-form | #57 Immutable Field |
| qa-api | New Update endpoint (A-01) | qa-form | BQ1 Field Mutability |
| qa-api | Missing ownership (A-09) | qa-guard | G-05 Missing current-user validation |
| qa-data | New Entity column (D-01) | qa-form | Full pipeline check |
| qa-data | Enum column 3+ values | qa-form | BQ3 State Transitions |
| qa-data | Unique constraint (D-07) | qa-form | #18 Unique constraint hint |

---

## Business Logic Cache Files

Some QA skills generate project-level cache files to avoid re-evaluating stable business logic decisions on every run.

### QA_BUSINESS_DECISIONS.md

- **Generated by**: `qa-form --group business` or qa-scan Step 4 (LEARN)
- **Location**: Project root
- **Purpose**: Cache results of business logic questions (BQ1-BQ4), forbidden operations, and intentional divergences
- **Cache behavior**: Confirmed entries are skipped on subsequent runs. New/changed entities trigger re-evaluation
- **Force refresh**: `--no-cache` flag ignores all cached entries

### QA_REGRESSION_PATTERNS.md

- **Generated by**: qa-scan Step 4 (LEARN) — automatically after every fix
- **Location**: Project root
- **Purpose**: Record bug patterns that escaped QA, so the same class of bug is caught in future runs
- **Scan behavior**: Every QA run checks all patterns (including Quick mode). If a pattern's fix is missing or reverted, flag as **Critical**

**Template** (auto-created on first LEARN step):

```markdown
# QA Regression Patterns

> Auto-generated by qa-scan Step 4 (LEARN). Each entry represents a bug that QA missed.
> Every QA run scans these patterns. If a fix is missing or reverted → Critical.

## [Pattern Name]
- **Bug**: [One-line description]
- **Root Cause**: [Why QA missed it]
- **Detection Rule**: [grep/scan pattern]
- **Fix Location**: [file:line]
- **Check**: [Check ID or "NEW → qa-ui Y-39"]
- **Project**: [Project name]
- **Added**: [Date]
```

### Candidate Check Lifecycle

Candidate checks (`[CANDIDATE]` prefix) are new checks drafted by Step 4 (LEARN) when no existing check covers a bug class.

| Stage | State | Behavior |
|-------|-------|----------|
| Draft | `[CANDIDATE]` in check name | Added to skill check table immediately; runs in all modes |
| Validation | 3 runs with correct detection (no false positives) | Track in `runs_ok` counter in regression pattern |
| Promotion | Counter reaches 3 | Remove `[CANDIDATE]` prefix — check is now permanent |
| Rejection | False positive detected | Refine detection rule or demote to `[DEPRECATED]` and skip |

---

## QA Coverage Map

All QA skills MUST update `QA_COVERAGE.md` at the project root after each run to track which modules have been audited.

### Update Protocol

After completing a QA run, append or update the corresponding row in `QA_COVERAGE.md`:
1. If the file doesn't exist, create it from the template below
2. Find the row matching the audited module/page — update it
3. If no matching row exists, add a new row
4. Update the Summary section totals

### Coverage File Template (`QA_COVERAGE.md`)

```markdown
# QA Coverage Map

> Auto-updated by QA skills on each run. Do not edit manually.

## Summary
- Total modules: 0
- Audited: 0 (0%)
- Unaudited: 0
- Last full audit: -

## Coverage by Module

| Module | Page/File | Last QA | Skills Run | Score | Issues | Risk |
|--------|-----------|---------|------------|-------|--------|------|

## Unaudited Modules
> Modules detected in the codebase but never QA'd.

| Module | Files | Risk Score |
|--------|-------|------------|

## Stale Modules
> Modules changed after their last QA run.

| Module | Last Changed | Last QA | Days Stale |
|--------|-------------|---------|------------|
```

### Viewing Coverage

```
/qa-inputs --coverage          # Show current coverage map without running checks
/qa-fix --coverage             # Show coverage across all skill types
```

---

## Change-Aware QA

QA skills support a `--changed` flag to focus analysis on recently modified code only.

### How It Works

1. `--changed`: Uses `git diff HEAD~1 --name-only` to find changed files
2. `--changed HEAD~N`: Uses `git diff HEAD~N --name-only` for wider range
3. `--changed branch`: Uses `git diff branch...HEAD --name-only` to compare against a branch
4. Map changed files to modules (extract module name from file path)
5. Run checks ONLY on the identified modules
6. Cross-reference with `QA_COVERAGE.md` to flag modules that changed after their last QA

### File-to-Module Mapping

```
backend/src/modules/{module}/    → module name = {module}
frontend/app/pages/{module}/     → module name = {module}
frontend-dashboard/app/pages/{module}/ → module name = dashboard-{module}
```

For non-standard paths, use the parent directory name as the module identifier.

### Example Usage

```
/qa-inputs --changed              # QA only modules changed in last commit
/qa-inputs --changed HEAD~5       # QA modules changed in last 5 commits
/qa-crud --changed dev            # QA modules changed since diverging from dev
```

---

## Risk-Based Priority

QA skills support a `--risk-first` flag to prioritize high-risk modules in the report and execution order.

### Risk Score Formula

```
Risk = (days_since_last_qa × 1)
     + (recent_change_count × 2)
     + (user_facing × 3)
     + (auth_payment_related × 5)
```

| Factor | How to detect | Weight |
|--------|--------------|--------|
| Days since last QA | `QA_COVERAGE.md` Last QA column | ×1 per day |
| Recent change count | `git log --oneline --since="2 weeks ago" -- {module_path} \| wc -l` | ×2 per commit |
| User-facing | Module serves patient/coach frontend (not admin-only) | +3 if true |
| Auth/payment related | Module path contains `auth`, `payment`, `billing`, `security` | +5 if true |

### Usage

```
/qa-inputs --risk-first           # Sort report by risk score (highest first)
/qa-fix --risk-first --changed    # Fix high-risk changed modules first
```

### Report Output

When `--risk-first` is active, add a Risk Summary section at the top of the report:

```
━━━ Risk Summary ━━━
🔴 HIGH (15+): admin/users (score: 22), auth/login (score: 18)
🟡 MEDIUM (5-14): exercises (score: 8)
🟢 LOW (0-4): surveys (score: 2)
```

---

## Pre-Commit Lightweight QA

A minimal QA check set designed to run on changed files BEFORE committing, catching only the most critical issues.

### Pre-Commit Check Set

These are the highest-impact checks that catch dangerous bugs with minimal execution time:

| Check | Source Skill | What it catches |
|-------|-------------|----------------|
| #57 | qa-form | Identity field in Update DTO (username/email editable) |
| #58 | qa-form | DTO vs Zod constraint divergence |
| #13 | qa-form | Nullable/Required conflict between Entity and DTO |
| A-14 | qa-api | Service layer identity field bypass |
| #60 | qa-form | Password policy cross-flow parity |

### Usage

```
/qa-inputs --precommit            # Run pre-commit checks on changed files only
```

### Behavior

1. Automatically detects changed files via `git diff --cached --name-only` (staged files)
2. If no staged files, falls back to `git diff --name-only` (unstaged changes)
3. Maps files to modules, runs only the 5 pre-commit checks on those modules
4. Output is minimal: only CRITICAL findings are shown
5. If any CRITICAL found: output warning banner
6. If no CRITICAL found: output one-line "Pre-commit QA: PASS"

### Integration with Git Hooks (Optional)

Can be invoked via a pre-commit hook if the project uses Husky or similar:
```json
// .husky/pre-commit (conceptual — actual invocation depends on Claude Code CLI availability)
// This is for documentation purposes; actual hook setup is manual
```

---

## Canary Check — QA Execution Quality Verification

Canary checks are **known issues intentionally left in test files** that QA MUST detect. If QA completes without finding a canary, the execution was incomplete or flawed.

### How It Works

1. Project maintainer creates `QA_CANARY.md` at the project root (optional — not all projects need this)
2. Each canary entry describes: what the known issue is, which QA check should find it, and where it lives
3. At the END of every QA run, the skill checks if canaries were detected
4. If a canary was missed → append warning: `⚠️ Canary missed: [description]. QA execution may be incomplete.`

### Canary File Template (`QA_CANARY.md`)

```markdown
# QA Canary Checks

> Known issues intentionally placed in test/canary files.
> QA skills MUST detect these. Missing a canary = incomplete QA execution.

| ID | Expected Check | Expected Finding | File/Location | Last Verified |
|----|---------------|-----------------|---------------|---------------|
| C1 | qa-inputs #57 | username in Update DTO | test/canary/update-canary.dto.ts | 2026-03-21 |
| C2 | qa-crud #14 | entity.email = in update method | test/canary/canary.service.ts | 2026-03-21 |
```

### Important Notes

- Canary files should live in a `test/canary/` directory and be excluded from production builds
- Canaries should be simple, obvious issues — not edge cases. They test whether QA ran at all, not whether QA is clever
- If `QA_CANARY.md` doesn't exist, skip canary verification silently (no error)

---

## Supported Extensions

All QA skills support: `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.ts`, `.js`

---

## Read-Only Guarantee

Individual QA skills (qa-auth, qa-crud, etc.) are **read-only** — they analyze and report only.

**Exception:** `qa-fix` is the only QA skill that modifies files (Phase 2: Fix). It follows Safety Rules defined in its own skill.md.

---

## Framework-Specific Pattern Mappings

All QA skills MUST use the detected framework to select the correct scanning patterns from the tables below. Never hardcode patterns for a single framework — always branch based on detection results. When detection fails, use the **Generic Fallback** row.

### Router / Navigation Patterns

| Framework | Router Import | Programmatic Navigate | Replace (no history) | Go Back | Route Guard / Auth Redirect |
|-----------|--------------|----------------------|---------------------|---------|----------------------------|
| React Router | `import { useNavigate } from 'react-router-dom'` | `navigate('/path')` | `navigate('/path', { replace: true })` | `navigate(-1)` | `<Route>` wrapper or loader redirect |
| Next.js (App) | `import { useRouter } from 'next/navigation'` | `router.push('/path')` | `router.replace('/path')` | `router.back()` | Middleware `middleware.ts` or layout redirect |
| Next.js (Pages) | `import { useRouter } from 'next/router'` | `router.push('/path')` | `router.replace('/path')` | `router.back()` | `getServerSideProps` redirect |
| Vue Router | `import { useRouter } from 'vue-router'` | `router.push('/path')` | `router.replace('/path')` | `router.back()` or `router.go(-1)` | `beforeEach` navigation guard |
| Nuxt | Auto-imported `useRouter()`, `navigateTo()` | `navigateTo('/path')` | `navigateTo('/path', { replace: true })` | `router.back()` | `defineNuxtRouteMiddleware` |
| Angular | `import { Router } from '@angular/router'` | `this.router.navigate(['/path'])` | `this.router.navigate(['/path'], { replaceUrl: true })` | `this.location.back()` | `CanActivate` guard |
| SvelteKit | `import { goto } from '$app/navigation'` | `goto('/path')` | `goto('/path', { replaceState: true })` | `history.back()` | `+page.server.ts` load redirect |
| Generic Fallback | `window.location` or `history` API | `window.location.href = '/path'` | `window.location.replace('/path')` | `history.back()` | Check for redirect patterns in route handlers |

**Grep patterns for detecting navigation calls:**
```
React Router:    navigate\(|useNavigate|<Navigate |<Link
Next.js:         router\.push|router\.replace|router\.back|useRouter|<Link
Vue Router:      router\.push|router\.replace|router\.back|router\.go|useRouter|<router-link|<RouterLink
Nuxt:            navigateTo|useRouter|<NuxtLink
Angular:         this\.router\.navigate|this\.location\.back|routerLink|\[routerLink\]
SvelteKit:       goto\(|<a href
Generic:         window\.location|history\.pushState|history\.replaceState|history\.back
```

### CSS / Styling Framework Patterns

| Framework | Detection Signal | Class Syntax | Layout Patterns | Spacing Patterns |
|-----------|-----------------|-------------|-----------------|-----------------|
| Tailwind CSS | `tailwindcss` in devDependencies or `tailwind.config` file exists | Utility classes: `flex`, `p-4`, `gap-2` | `flex`, `grid`, `flex-col`, `items-center` | `p-{n}`, `m-{n}`, `gap-{n}`, `space-y-{n}` |
| CSS Modules | `*.module.css` or `*.module.scss` files exist | `styles.className` or `styles['class-name']` | Read `.module.css` for layout properties | Read `.module.css` for spacing values |
| Styled Components | `styled-components` in dependencies | `` styled.div`...` `` or `css` prop | Read template literal for `display`, `flex` | Read template literal for `padding`, `margin`, `gap` |
| Emotion | `@emotion/styled` or `@emotion/react` in dependencies | `` styled.div`...` `` or `css` prop | Same as Styled Components | Same as Styled Components |
| SCSS/SASS | `*.scss` or `*.sass` files with class usage | BEM-style: `.block__element--modifier` | Read `.scss` files for layout properties | Read `.scss` files for spacing values |
| Plain CSS | `*.css` files without module suffix | Standard class names | Read `.css` files for layout properties | Read `.css` files for spacing values |
| UnoCSS | `unocss` in devDependencies | Utility classes similar to Tailwind | Same as Tailwind | Same as Tailwind |
| Generic Fallback | None of the above detected | Inspect `className` or `class` attributes | Grep for `display:\s*flex|display:\s*grid` in stylesheets | Grep for `padding|margin|gap` in stylesheets |

**Layout consistency audit strategy by CSS framework:**
- **Utility-class frameworks** (Tailwind, UnoCSS): Compare `className` strings directly across same-type pages
- **CSS-in-JS** (Styled Components, Emotion): Read the styled definitions and compare CSS properties
- **External stylesheets** (CSS Modules, SCSS, Plain CSS): Resolve class → stylesheet → compare computed CSS properties
- **Generic fallback**: Grep for inline `style` attributes and compare values

### ORM / Data Layer Patterns

| ORM | Detection Signal | Entity/Model Files | Column/Field Definition | Relation Definition |
|-----|-----------------|-------------------|------------------------|-------------------|
| TypeORM | `typeorm` in dependencies | `**/*.entity.ts` | `@Column({ type, nullable, length })` | `@ManyToOne`, `@OneToMany`, `@JoinColumn` |
| Prisma | `@prisma/client` in dependencies | `prisma/schema.prisma` | `fieldName Type @db.VarChar(100)` | `relation` fields with `@relation` |
| Sequelize | `sequelize` in dependencies | `**/models/*.{js,ts}` | `DataTypes.STRING(100)`, `allowNull` | `belongsTo`, `hasMany`, `belongsToMany` |
| Mongoose | `mongoose` in dependencies | `**/*.schema.ts` or `**/*.model.ts` | `{ type: String, required: true, maxlength: 100 }` | `{ type: Schema.Types.ObjectId, ref: 'Model' }` |
| Django ORM | `django` in requirements.txt | `**/models.py` | `models.CharField(max_length=100, null=False)` | `models.ForeignKey`, `models.ManyToManyField` |
| SQLAlchemy | `sqlalchemy` in requirements.txt | `**/models.py` or `**/models/*.py` | `Column(String(100), nullable=False)` | `relationship()`, `ForeignKey` |
| Drizzle | `drizzle-orm` in dependencies | `**/schema.ts` or `**/schema/*.ts` | `varchar('name', { length: 100 })` | `relations()` |
| Eloquent (Laravel) | `laravel/framework` in composer.json | `app/Models/*.php` | `$fillable`, `$casts`, migration `$table->string('name', 100)` | `belongsTo()`, `hasMany()`, `belongsToMany()` |
| Generic Fallback | No ORM detected | Grep for SQL files, raw queries | Look for CREATE TABLE statements | Look for FOREIGN KEY constraints |

### DTO / Validation Layer Patterns

| Framework | Detection Signal | DTO/Schema Files | Validation Decorators/Methods | Partial/Pick Types |
|-----------|-----------------|-----------------|------------------------------|-------------------|
| class-validator (NestJS) | `class-validator` in dependencies | `**/*.dto.ts` | `@IsString()`, `@MinLength(n)`, `@IsOptional()` | `PartialType()`, `PickType()`, `OmitType()` |
| Zod | `zod` in dependencies | Grep for `z.object` in `**/*.{ts,tsx}` | `.string()`, `.min(n)`, `.max(n)`, `.optional()` | `.partial()`, `.pick()`, `.omit()` |
| Yup | `yup` in dependencies | Grep for `yup.object` in `**/*.{ts,tsx}` | `.string()`, `.min(n)`, `.max(n)`, `.notRequired()` | N/A (manual) |
| Joi | `joi` in dependencies | Grep for `Joi.object` in `**/*.{ts,js}` | `Joi.string()`, `.min(n)`, `.max(n)`, `.optional()` | N/A (manual) |
| Django Serializers | `rest_framework` in requirements.txt | `**/serializers.py` | `CharField(max_length=100, required=True)` | `fields = '__all__'` or explicit list |
| Laravel Requests | `laravel/framework` in composer.json | `app/Http/Requests/*.php` | `'name' => 'required\|string\|max:100'` | Rule arrays in `rules()` method |
| Spring Validation | `spring-boot-starter-validation` in pom.xml | `**/dto/*.java` or `**/request/*.java` | `@NotBlank`, `@Size(min, max)`, `@Valid` | N/A (separate classes) |
| Valibot | `valibot` in dependencies | Grep for `v.object` in `**/*.{ts,tsx}` | `v.string()`, `v.minLength(n)`, `v.optional()` | `v.partial()`, `v.pick()`, `v.omit()` |
| Generic Fallback | No validation library detected | Grep for manual if/throw validation | Look for manual length/type checks | N/A |

### Form Library Patterns

| Library | Detection Signal | Form Hook/Setup | Field Registration | Submit Handler |
|---------|-----------------|----------------|-------------------|---------------|
| React Hook Form | `react-hook-form` in dependencies | `useForm()`, `useFormContext()` | `register('field')` or `<Controller>` | `handleSubmit(onSubmit)` |
| Formik | `formik` in dependencies | `useFormik()` or `<Formik>` | `<Field name="field">` | `onSubmit` prop |
| VeeValidate (Vue) | `vee-validate` in dependencies | `useForm()`, `useField()` | `useField('field')` or `<Field>` | `handleSubmit(onSubmit)` |
| FormKit (Vue) | `@formkit/vue` in dependencies | `<FormKit type="form">` | `<FormKit type="text" name="field">` | `@submit` event |
| Angular Reactive Forms | `@angular/forms` in package.json | `FormBuilder`, `FormGroup`, `FormControl` | `formControlName="field"` | `(ngSubmit)="onSubmit()"` |
| Angular Template Forms | `@angular/forms` in package.json | `ngModel` | `[(ngModel)]="field"` | `(ngSubmit)="onSubmit()"` |
| Svelte Forms | Native or `svelte-forms-lib` | `bind:value` or `createForm()` | `bind:value={field}` | `on:submit` |
| Plain HTML | No form library | `<form>` element | `<input name="field">` | `form.addEventListener('submit')` or `onsubmit` |
| Generic Fallback | Unknown library | Grep for `<form` or form submission | Grep for `name=` attributes on inputs | Grep for submit handlers |

### Table / List Library Patterns

| Library | Detection Signal | Table Component | Column Definition | Sorting | Pagination |
|---------|-----------------|----------------|-------------------|---------|-----------|
| TanStack Table (React) | `@tanstack/react-table` in dependencies | `useReactTable()`, `flexRender` | `columnHelper.accessor()` or column defs array | `getSortedRowModel()` | `getPaginationRowModel()` |
| TanStack Table (Vue) | `@tanstack/vue-table` in dependencies | `useVueTable()`, `FlexRender` | `columnHelper.accessor()` or column defs array | `getSortedRowModel()` | `getPaginationRowModel()` |
| AG Grid | `ag-grid-react` or `ag-grid-vue` in dependencies | `<AgGridReact>` or `<ag-grid-vue>` | `columnDefs` prop | `sortable: true` in colDef | `pagination: true` prop |
| Ant Design Table | `antd` in dependencies | `<Table>` | `columns` prop array | `sorter` in column def | `pagination` prop |
| Material UI Table | `@mui/material` in dependencies | `<Table>`, `<DataGrid>` | `<TableCell>` or `columns` for DataGrid | `<TableSortLabel>` or `sortModel` | `<TablePagination>` or `paginationModel` |
| Element Plus Table (Vue) | `element-plus` in dependencies | `<el-table>` | `<el-table-column>` | `sortable` prop | `<el-pagination>` |
| Vuetify Table | `vuetify` in dependencies | `<v-data-table>` | `headers` prop | Built-in with `headers` sort | Built-in pagination |
| PrimeVue Table | `primevue` in dependencies | `<DataTable>` | `<Column>` | `sortable` prop | `<Paginator>` or built-in |
| Angular Material Table | `@angular/material` in package.json | `<mat-table>` | `<ng-container matColumnDef>` | `matSort`, `matSortHeader` | `<mat-paginator>` |
| Plain HTML | No table library | `<table>` element | `<th>`, `<td>` | Manual click handlers | Manual page controls |
| Generic Fallback | Unknown library | Grep for `<table` or list rendering | Grep for column/header definitions | Grep for sort-related props/handlers | Grep for page/offset/limit patterns |

### Data Fetching Patterns

| Library | Detection Signal | Query Hook/Method | Mutation Hook/Method | Cache Invalidation |
|---------|-----------------|------------------|---------------------|--------------------|
| TanStack Query (React) | `@tanstack/react-query` in dependencies | `useQuery()`, `useSuspenseQuery()` | `useMutation()` | `queryClient.invalidateQueries()` |
| TanStack Query (Vue) | `@tanstack/vue-query` in dependencies | `useQuery()` | `useMutation()` | `queryClient.invalidateQueries()` |
| SWR | `swr` in dependencies | `useSWR()` | `useSWRMutation()` | `mutate()` |
| Apollo Client | `@apollo/client` in dependencies | `useQuery()`, `useLazyQuery()` | `useMutation()` | `refetchQueries`, `cache.modify()` |
| RTK Query | `@reduxjs/toolkit` with `createApi` | `useGetXQuery()` (generated) | `useUpdateXMutation()` (generated) | `invalidatesTags` |
| Axios + manual | `axios` in dependencies (no query lib) | `axios.get()` in `useEffect` or lifecycle | `axios.post()`, `axios.put()` | Manual state update or re-fetch |
| Fetch API | No HTTP library | `fetch()` in `useEffect` or lifecycle | `fetch()` with method POST/PUT/DELETE | Manual state update or re-fetch |
| Nuxt useFetch | `nuxt` in dependencies | `useFetch()`, `useAsyncData()` | `$fetch()` | `refreshNuxtData()`, `refresh()` |
| Angular HttpClient | `@angular/common/http` | `this.http.get()` | `this.http.post()` | Manual re-fetch via service |
| Generic Fallback | No pattern matched | Grep for HTTP calls in components | Grep for POST/PUT/DELETE calls | Grep for refetch/reload patterns |

### UI Component Library Detection

| Library | Detection Signal | Button | Modal/Dialog | Select/Dropdown | Toast/Notification |
|---------|-----------------|--------|-------------|----------------|--------------------|
| shadcn/ui | `@radix-ui/*` + `components/ui/` dir | `<Button>` | `<Dialog>`, `<AlertDialog>` | `<Select>`, `<Combobox>` | Sonner: `toast()` |
| Radix UI | `@radix-ui/*` in dependencies | `<Button>` | `<Dialog.Root>` | `<Select.Root>` | Custom |
| Material UI (MUI) | `@mui/material` in dependencies | `<Button>` | `<Dialog>`, `<Modal>` | `<Select>`, `<Autocomplete>` | `<Snackbar>`, `<Alert>` |
| Ant Design | `antd` in dependencies | `<Button>` | `<Modal>` | `<Select>` | `message.success()`, `notification.open()` |
| Chakra UI | `@chakra-ui/react` in dependencies | `<Button>` | `<Modal>` | `<Select>` | `toast()` |
| Element Plus | `element-plus` in dependencies | `<el-button>` | `<el-dialog>` | `<el-select>` | `ElMessage()`, `ElNotification()` |
| Vuetify | `vuetify` in dependencies | `<v-btn>` | `<v-dialog>` | `<v-select>` | `<v-snackbar>` |
| PrimeVue | `primevue` in dependencies | `<Button>` | `<Dialog>` | `<Dropdown>`, `<Select>` | `toast.add()` via ToastService |
| Headless UI | `@headlessui/react` or `@headlessui/vue` | N/A (unstyled) | `<Dialog>` | `<Listbox>`, `<Combobox>` | Custom |
| Angular Material | `@angular/material` in package.json | `<button mat-button>` | `MatDialog.open()` | `<mat-select>` | `MatSnackBar.open()` |
| Bootstrap | `bootstrap` or `react-bootstrap` in deps | `<Button>` / `<button class="btn">` | `<Modal>` / `.modal` | `<Form.Select>` / `<select class="form-select">` | Toast component or custom |
| Generic Fallback | No UI lib detected | `<button>` | `[role="dialog"]` or custom | `<select>` | Grep for toast/notification/alert patterns |

### Page File Patterns

| Framework | Page Files | Layout Files | Route Config |
|-----------|-----------|-------------|-------------|
| React Router | `pages/**/*.tsx` or route-defined components | `**/layout.tsx`, `**/Layout.tsx` | `createBrowserRouter()` or `<Route>` JSX |
| Next.js (App) | `app/**/page.tsx` | `app/**/layout.tsx` | File-system routing |
| Next.js (Pages) | `pages/**/*.tsx` | `pages/_app.tsx`, `pages/_document.tsx` | File-system routing |
| Vue Router | `views/**/*.vue` or `pages/**/*.vue` | `layouts/**/*.vue`, `App.vue` | `createRouter()` in `router/index.ts` |
| Nuxt | `pages/**/*.vue` | `layouts/**/*.vue` | File-system routing |
| Angular | `**/*.component.ts` | `**/*-layout.component.ts` | `Routes` array in `*-routing.module.ts` or `app.routes.ts` |
| SvelteKit | `src/routes/**/+page.svelte` | `src/routes/**/+layout.svelte` | File-system routing |
| Generic Fallback | Grep for components rendering `<main>` or full pages | Grep for components wrapping `children`/`<slot>`/`<Outlet>`/`<router-view>` | Grep for route definitions |

**How skills should use this section:**

1. Run framework detection (Frontend + Backend + CSS + ORM as needed)
2. Look up the detected framework in the relevant table above
3. Use the framework-specific patterns for scanning, grepping, and analysis
4. If the framework is not in the table, use the **Generic Fallback** row
5. Report the detected framework in the output header
