---
name: qa-form
description: "Audit full-stack input fields — Entity -> DTO -> Schema -> Form UI consistency, validation, mutability, and security"
user-invocable: true
argument-hint: "[module] [--check N] [--group name]"
---

# QA Form — Full-Stack Input Field Auditor

Audit all input fields across the full stack (Entity -> DTO -> Zod Schema -> Form UI) for consistency issues including missing asterisks, validation gaps, field name mismatches, type mismatches, and security concerns.

## Execution Mode

- **Standalone** (`/qa-form [module]`): Diagnose-only. Scans the codebase, applies checks below, outputs a report. Does NOT modify files.
- **Via qa-scan** (`/qa-scan --check form`): qa-scan uses the checks below as its checklist for the form layer, then applies fixes.

Shared conventions (scoring, framework detection, output format): see `qa-shared/reference.md`.

## Check Filtering

```
/qa-form --check 1          # Run only Check 1
/qa-form --check 1,6,10     # Run specific checks
/qa-form --group type        # Run only type-related checks (10-12)
/qa-form --group security    # Run only security checks (19-20)
/qa-form --group business    # Run business logic questions (BQ1-BQ4) + negative test
```

| Group | Checks | Description |
|-------|--------|-------------|
| required | 1, 3, 5 | Required/Optional mismatches |
| type | 10, 11, 12 | Type mismatches |
| constraint | 6, 7, 8, 16, 17 | Constraint mismatches |
| integrity | 4, 13, 14, 15, 57 | Cross-layer integrity |
| quality | 2, 9, 18 | Code quality |
| security | 19, 20 | Security concerns |
| semantic | 21-26, 38-44, 49 | Semantic validation |
| ux | 27-31, 50-55 | UX quality |
| form | 32-37, 45-49 | Form behavior |
| crosslayer | 58, 59, 60 | Cross-layer validation conflict detection |
| business | BQ1-BQ4, NT | Business logic questions + negative test (uses cache) |

## Checks

> Check numbering is by category (not sequential) so `--check N` references remain stable as new checks are added.

### Required / Optional (Checks 1, 3, 5)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 1 | Required without asterisk | **High** | | DTO `@IsNotEmpty()` but no `*` in frontend |
| 3 | Optional with asterisk | **Medium** | | DTO `@IsOptional()` but frontend shows `*` |
| 5 | DB column no input route | **High** | | Non-nullable entity column missing from Create DTO |

### Type Matching (Checks 10, 11, 12)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 10 | Numeric type mismatch | **High** | | Numeric DB column / DTO `@IsNumber()` but frontend allows text input |
| 11 | Date type mismatch | **High** | | Date/timestamp DB column but frontend uses text input instead of date picker |
| 12 | Boolean type mismatch | **High** | | Boolean DB column but frontend uses text input instead of checkbox/toggle |

### Constraint Matching (Checks 6, 7, 8, 16, 17)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 6 | maxLength mismatch | **High** | | DB/DTO has max length but frontend doesn't enforce |
| 7 | minLength mismatch | **Medium** | | DTO `@MinLength(N)` vs Zod `.min(N)` inconsistent |
| 8 | Enum value mismatch | **Medium** | | DTO `@IsEnum()` values != frontend dropdown options |
| 16 | Decimal precision mismatch | **Medium** | | DB `decimal(10,2)` but frontend allows more decimal places |
| 17 | Numeric range mismatch | **Medium** | | DTO `@Min(0)`/`@IsPositive()` but frontend input has no `min` attribute |

### Cross-Layer Integrity (Checks 4, 13, 14, 15, 57)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 4 | Field name mismatch | **Info** | | Zod field != DTO field != Entity property |
| 13 | Nullable / Required conflict | **High** | | Entity `nullable: false` but DTO `@IsOptional()`, or the reverse |
| 14 | Orphan frontend field | **Medium** | | Zod schema has field not in any DTO — silently ignored by server |
| 15 | Orphan DTO field | **Medium** | | Create DTO has field not sent by any frontend form — always undefined |
| 57 | Immutable field in Update DTO/form | **Critical** | | Identity fields (`username`, `id`, `email`, `role`) present in Update DTO or edit form. These fields are set at creation and must NOT be modifiable post-creation. Check: (1) Update DTO must not contain the field, (2) Edit form Zod schema must not contain the field, (3) Backend service update logic must not accept the field — scan for `entity.username = ...` or `entity.email = ...` direct assignment in service update methods (bypasses DTO protection), (4) Applies to ALL update flows including admin update endpoints. If a field is found in the service layer but not in the DTO, flag as **Critical** — it means DTO protection is being bypassed |

### Quality (Checks 2, 9, 18)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 2 | Regex without error message | **Low** | | `@Matches()` or `.regex()` has no user-friendly error message |
| 9 | i18n hardcoded | **Low** | | Labels/errors/placeholders without `t()` wrapper |
| 18 | Unique constraint without hint | **Medium** | | Entity `@Unique()` but no frontend duplicate check (debounced API or button) — user sees server 500/conflict only after submit |

### Security (Checks 19, 20)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 19 | XSS-prone input | **Critical** | | User text rendered via `dangerouslySetInnerHTML` / `v-html` without sanitization |
| 20 | File upload without constraint | **Medium** | | File input without `accept` type filter or size limit |

### Semantic Validation (Checks 21-26, 38-44, 49, 56)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 21 | Name field too short | **Medium** | | `*name*` field allows minLength < 2 (1-char name is unrealistic) |
| 56 | Name field without character-type restriction | **High** | | `*name*` field (person name, not username) has no regex/pattern restricting allowed character types — special characters and numbers pass. Must have `@Matches()` in DTO AND `.regex()` in Zod. The specific pattern is project-dependent (e.g., Latin-only, CJK+Latin, etc.) |
| 22 | Email field without validation | **High** | | `*email*` field missing `@IsEmail()` / `z.string().email()` / `type="email"` |
| 23 | Password field too weak | **High** | | `*password*` field has minLength < 6 or missing `type="password"`. Registration/signup forms MUST have `confirmPassword` with `.refine()` match check — missing = **High** |
| 24 | URL field without validation | **Medium** | | `*url*`/`*link*` field missing `@IsUrl()` / `.url()` validation |
| 25 | Count/quantity allows negative | **Medium** | | `*count*`/`*quantity*`/`*sets*`/`*reps*` field allows negative or decimal |
| 26 | Price/amount allows negative | **Medium** | | `*price*`/`*amount*`/`*cost*` field allows negative values |
| 38 | Numeric-string without format constraint | **High** | | `varchar` field named `*number*`/`*code*` stored as string but has no pattern to restrict format |
| 39 | Date field missing temporal constraint | **Medium** | | `*birthday*`/`*startDate*` missing past-only or future-only validation |
| 40 | Phone field without format validation | **High** | | `*phone*`/`*tel*`/`*mobile*` missing phone number format pattern |
| 41 | Zip/postal code without format | **Medium** | | `*zip*`/`*postal*` missing format pattern for postal code validation |
| 42 | Percentage/rate out of range | **Medium** | | `*rate*`/`*percentage*`/`*percent*` missing 0-100 range constraint |
| 43 | Duration/time unrealistic values | **Medium** | | `*minutes*`/`*hours*`/`*duration*` missing positive constraint or reasonable max |
| 44 | Score/rating without range | **High** | | `*score*`/`*rating*`/`*level*` missing defined min/max range |
| 49 | Date pair missing cross-field constraint | **High** | | Paired date fields (`startDate`/`endDate`) where end date can precede start date — check UI layer AND schema layer |

### UX Quality (Checks 27-31)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 27 | Long text in single-line input | **Medium** | | `*description*`/`*content*`/`*bio*`/`*memo*` uses `<input>` instead of `<textarea>` |
| 28 | Whitespace-only accepted | **Medium** | | String field missing `.trim()` in schema — `"   "` passes validation |
| 29 | Empty string vs null | **Low** | | Optional string field sends `""` but DB expects `null` |
| 50 | Password visibility toggle missing | **Medium** | | `type="password"` input has no show/hide toggle button (Eye/EyeOff icon). Users cannot verify what they typed — increases typo risk, especially for older users |
| 51 | Password requirements not visible | **Medium** | | Password field has validation rules (minLength, maxLength, pattern) but no hint text shown BEFORE user types. Requirements only appear as error AFTER failed validation |
| 52 | Missing success feedback after mutation | **Medium** | | Form submit success triggers only navigation/redirect with no visible confirmation (toast, alert, success message). User cannot confirm the action completed |
| 53 | Missing terms/privacy agreement | **High** | | Registration/signup form has no terms of service or privacy policy agreement checkbox. Required for legal compliance in most jurisdictions |
| 54 | Missing auto-focus on first field | **Low** | | Form/page does not set `autoFocus` on the first input field — user must manually tap/click to start typing |
| 55 | Phone input without display formatting | **Low** | | Phone number input accepts raw digits but does not auto-format with hyphens/separators as user types (e.g., `01012345678` -> `010-1234-5678`). Validation may still work, but UX is poor for readability |
| 56 | Form dirty state on close | **Medium** | | Form with `isDirty=true` allows modal close / page navigation without unsaved-changes warning. Check for `useBeforeUnload`, `onBeforeUnload`, or `blocker`/`useBlocker` usage when form has editable fields |

### Form Behavior (Checks 32-37, 45-49)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 32 | Error message not displayed | **High** | | Field has validation but no error display component in UI |
| 33 | Select default value missing | **High** | | Required Select has no default value and placeholder is submittable |
| 34 | Double submission possible | **Medium** | | Submit button has no loading/disabled state — duplicate data on double-click |
| 35 | Conditional required mismatch | **Medium** | | DTO `@ValidateIf()` condition not mirrored in frontend |
| 36 | Array field min/max missing | **Medium** | | DTO `@IsArray()` + `@ArrayMinSize(1)` but frontend allows empty array |
| 37 | Default value not shown | **Low** | | Entity column has `default` value but frontend form doesn't pre-fill it |
| 45 | Validation mode onSubmit only | **High** | | `useForm` uses default `mode: 'onSubmit'` — no real-time feedback |
| 46 | String field without maxLength | **High** | | No `@MaxLength` in DTO AND no `.max()` in Zod AND no `maxLength` on HTML input — unbounded |
| 47 | Schema maxLength without HTML maxLength | **Medium** | | Schema has `.max(N)` but HTML `<input>` missing `maxLength` attribute |
| 48 | Restricted-format field without real-time filtering | **High** | | Field has character-set restriction (`.regex()` / `@Matches()`) but no `onInput` handler to silently strip invalid characters at typing time. Common patterns: username (`[^a-zA-Z0-9_]`), name (`[^a-zA-Z가-힣ㄱ-ㅎㅏ-ㅣ0-9 ]`), phone (`[^0-9+-]`), numeric (`[^0-9]`). Must use `onInput` (not `onChange`) so filtering runs before react-hook-form processes the value. Applies to ALL forms across all apps (signup, admin create/edit, detail pages) |
| 49 | Default value bypasses required input | **High** | | Numeric field has default value (0) that passes validation without user interaction |

### Cross-Layer Validation Conflicts (Checks 58, 59, 60)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| 58 | DTO vs Zod constraint divergence | **Critical** | | Same field has different constraints between DTO and Zod/inline validation. Compare field-by-field for each Create/Update flow: (1) `@MaxLength(N)` vs `.max(M)` where N != M, (2) `@MinLength(N)` vs `.min(M)` where N != M, (3) `@IsOptional()` but Zod has no `.optional()` or vice versa, (4) `@Matches(/pattern/)` vs `.regex(/pattern/)` with different patterns. **Scan**: For each mutation endpoint, pair the DTO file with the corresponding frontend form. Compare constraints field by field. **Exception**: If `QA_BUSINESS_DECISIONS.md` lists the divergence under "Intentional Divergences" with a confirmed date, skip it |
| 59 | Inline validation vs schema validation | **High** | | Form validation done via inline JavaScript (`if (value.length > 20)`, `useState`-based checks) instead of through the Zod schema, creating a shadow validation layer that can diverge from both the schema and the DTO. **Scan**: Find `useState`-based form fields with inline length/pattern checks that have no corresponding Zod schema field. These inline checks are invisible to schema-based analysis and often have different thresholds than the DTO |
| 60 | Password policy cross-flow parity | **Critical** | | All password-accepting flows must enforce identical constraints. Flows to check: (1) Registration/Signup — auth register DTO + frontend signup form, (2) Password Change (self) — change-password DTO + frontend form, (3) Password Reset (admin) — admin reset-password DTO + admin detail page, (4) Password Reset (forgot) — reset-password DTO + frontend form. Compare `minLength`, `maxLength`, and `pattern` across ALL flows. Flag any flow where constraints differ from others. **Exception**: `QA_BUSINESS_DECISIONS.md` "Intentional Divergences" entries are skipped |
| 61 | iOS input auto-zoom | **Critical** | `platform_ios` | Input fields with font-size < 16px (`text-sm`, `text-xs`) trigger automatic viewport zoom on iOS Safari/WebView when focused. All `<input>`, `<textarea>`, `<select>` must use font-size >= 16px (`text-base` or larger). **Scan**: Search for `text-sm`, `text-xs`, or custom font sizes below 16px on any form input element |
| 62 | Missing inputmode attribute | **High** | `is_mobile_target` | Number/phone/email inputs lack `inputmode` attribute (`numeric`, `tel`, `email`). Mobile keyboard won't show the appropriate layout, forcing users to switch keyboards manually. **Scan**: Find inputs with `type="number"`, `type="tel"`, `type="email"` and verify matching `inputMode` prop exists |
| 63 | Missing enterKeyHint | **Medium** | `is_mobile_target` | Form inputs lack `enterKeyHint` attribute (`done`, `next`, `search`, `send`). Mobile keyboard shows generic "return" instead of contextual action label |
| 64 | Missing autocomplete attribute | **Medium** | `is_mobile_target` | Form inputs lack `autocomplete` attribute. Mobile autofill and password managers cannot assist users. Critical for login forms (`username`, `current-password`) and personal info (`name`, `email`, `tel`) |

---

## Business Logic Questions (BQ1-BQ4)

> **Unlike pattern checks above, these are reasoning-based questions** the AI evaluates against the code context. Results are cached in `QA_BUSINESS_DECISIONS.md` at the project root.

### Cache Behavior

1. **First run**: Evaluate all questions for every Entity/field. Write results to `QA_BUSINESS_DECISIONS.md`
2. **Subsequent runs**: Read cache -> skip Confirmed items -> only evaluate NEW entities/fields (not in cache) or CHANGED ones (detected via `git diff` against Entity/DTO files)
3. **Force re-evaluation**: `/qa-form --group business --no-cache` ignores cache and re-evaluates everything

### BQ1: Field Mutability Review — **Critical**

For each field in every Update DTO and edit form, ask:

> "Should this field be modifiable after creation?"

Decision framework:

| Field Category | Examples | Expected Answer | If violated |
|----------------|----------|----------------|-------------|
| Identity fields | `username`, `email`, `id` | Almost always **NO** | **Critical** — identity change breaks references, sessions, audit trails |
| Profile fields | `fullName`, `phone`, `birth`, `image` | Almost always **YES** (by self + admin) | **Medium** — verify both self-update and admin-update flows exist |
| System fields | `role`, `isActive`, `coachId` | **YES by admin only**, NO by user | **High** — if in user self-update DTO, privilege escalation risk |
| Computed fields | `createdAt`, `updatedAt`, `score` | **NO** — system-managed | **Critical** — should never appear in any Update DTO |
| Audit fields | `adminNotes`, `withdrawalDate` | **YES by admin only** | **Medium** — check admin-only access |

**Scan procedure**:
1. List all Update DTOs (both user-facing and admin-facing)
2. For each field, classify by category above
3. Flag any field where the actual editability doesn't match the expected answer
4. Record decision in `QA_BUSINESS_DECISIONS.md` -> BQ1 table

### BQ2: Role-Based Editability — **High**

For each entity with update endpoints accessible by multiple roles, ask:

> "Which fields should each role be able to edit?"

**Scan procedure**:
1. Find all Update DTOs grouped by entity (e.g., `UpdateUserDto` in users/ vs admin/)
2. Compare field lists between roles
3. Flag: (a) Admin-only fields present in user self-update DTO, (b) User-editable fields missing from admin update DTO (admin should have superset)
4. Record in `QA_BUSINESS_DECISIONS.md` -> BQ2 table

### BQ3: State Transition Validity — **Medium**

For enum/status fields with 3+ values, ask:

> "Can any value transition to any other value, or are there rules?"

**Scan procedure**:
1. Find Entity columns with enum types or DTO fields with `@IsIn([...])` / `@IsEnum()`
2. If 2 values (binary toggle): no transition rules needed, skip
3. If 3+ values: check service layer for transition validation logic (e.g., `if (current === BLOCK) throw`)
4. If no transition logic exists, flag for review — not necessarily a bug, but should be a conscious decision
5. Record in `QA_BUSINESS_DECISIONS.md` -> BQ3 table

### BQ4: Sensitive Field Exposure — **High**

For each field in GET API responses, ask:

> "Should all roles see this field, or should it be filtered?"

**Scan procedure**:
1. Identify fields that are semantically sensitive: `adminNotes`, `internalNotes`, `withdrawalDate`, `coachStatus`, `salary`, `ssn`
2. Check if the same GET endpoint serves all roles or if role-specific serialization exists
3. Flag if admin-only fields appear in user-facing GET responses
4. Record in `QA_BUSINESS_DECISIONS.md` -> BQ4 table

---

## Negative Test — Forbidden Operations (NT)

> **Explicitly list what should be IMPOSSIBLE**, then verify it's actually blocked.

### Execution

1. **Build the forbidden list**: For each Entity, derive forbidden operations from BQ1/BQ2 results + common sense rules
2. **Verify each item**: Check that the forbidden operation is actually blocked at DTO level, service level, or both
3. **Flag unblocked items**: If a forbidden operation has no blocking mechanism, flag as **Critical**

### Common Forbidden Operation Patterns

| Pattern | Example | How to verify blocked |
|---------|---------|----------------------|
| Identity field mutation | User.username change via any endpoint | Field absent from ALL Update DTOs + no `entity.username =` in service update methods |
| Self-privilege escalation | User changing own `role` or `isActive` | Field absent from user self-update DTO (may exist in admin DTO) |
| Computed field override | Writing `createdAt`, `updatedAt` directly | Field absent from ALL DTOs + no direct assignment in services |
| Cross-user data access | User A editing User B's profile | Ownership check in service (`where: { id: currentUser.id }`) |
| Deleted entity resurrection | Restoring soft-deleted records without admin | Restore endpoint has admin role guard |

### Cache

Forbidden operations list is stored in `QA_BUSINESS_DECISIONS.md` -> "Forbidden Operations" section. On subsequent runs, only verify NEW entities or CHANGED entities.

---

## Regression Guard

> **Learn from past QA failures.** Each bug that escaped QA becomes a detection pattern.

### How it works

1. When a bug is found that QA should have caught, add it to `QA_REGRESSION_PATTERNS.md` at the project root
2. On each QA run, scan all regression patterns and verify the fix is still in place
3. If a pattern's fix is missing or reverted, flag as **Critical**

### Pattern file format (`QA_REGRESSION_PATTERNS.md`)

```markdown
## [Pattern Name]
- **Bug**: [What happened]
- **Root Cause**: [Why QA missed it]
- **Detection Rule**: [How to detect this pattern in code]
- **Fix Location**: [File path and what the fix looks like]
- **Added**: [Date]
```

### Scan procedure

1. If `QA_REGRESSION_PATTERNS.md` exists, read all patterns
2. For each pattern, execute its Detection Rule against the current codebase
3. If the pattern is detected (meaning the bug has returned or a similar bug exists), flag as **Critical** with reference to the original bug

---

## Cross-Skill Triggers

> When this skill discovers certain conditions, it should trigger checks in other skills.

| Condition found by qa-form | Trigger | Reason |
|----------------------------|---------|--------|
| New Update DTO field discovered (BQ1) | -> `qa-auth` Check #17 (Role-Based Field Editability) | New editable field needs role access verification |
| Identity field found in service layer (#57) | -> `qa-crud` Check #14 (Service Layer Identity Bypass) | Confirms the bypass is real, not a false positive |
| Sensitive field in GET response (BQ4) | -> `qa-auth` Check #18 (Response Field Filtering) | Sensitive field needs role-based filtering |
| Enum field with 3+ values found (BQ3) | -> `qa-db-integrity` Check #12 | Verify DB-level constraints exist for state transitions |

**Implementation**: When running via `qa-scan` or `qa-page`, the orchestrator reads these triggers and queues the target checks. In standalone mode, triggers are listed in the report as recommendations.

---

## QA_BUSINESS_DECISIONS.md Template

On first run of `--group business`, auto-generate this file at the project root if it doesn't exist:

```markdown
# QA Business Logic Decisions

> Auto-generated by qa-form. Used as cache for business logic checks.
> Mark "Intentional" in Notes column to suppress future warnings.
> Entries with Confirmed dates are skipped on subsequent runs unless the related code changes.

## BQ1: Field Mutability

| Entity | Field | In Update DTO? | Mutable? | By Whom? | Confirmed | Notes |
|--------|-------|----------------|----------|----------|-----------|-------|

## BQ2: Role-Based Editability

| Entity | Field | Admin Edit? | User Edit? | Consistent? | Confirmed | Notes |
|--------|-------|-------------|------------|-------------|-----------|-------|

## BQ3: State Transitions

| Entity | Field | Values | Transition Rules? | Confirmed | Notes |
|--------|-------|--------|-------------------|-----------|-------|

## BQ4: Sensitive Fields

| Entity | Field | Visible to All? | Should Be? | Confirmed | Notes |
|--------|-------|-----------------|------------|-----------|-------|

## Forbidden Operations (Negative Test)

| Entity | Operation | Blocked At | Verified? | Confirmed | Notes |
|--------|-----------|------------|-----------|-----------|-------|

## Intentional Divergences (Check #58/#60 exceptions)

| Flow | Field | DTO Constraint | Frontend Constraint | Reason | Confirmed |
|------|-------|---------------|---------------------|--------|-----------|
```

---

## Tier 2: Reasoning Patterns

After completing all Tier 1 checks and Business Logic Questions, apply these reasoning patterns from `qa-shared/reasoning-catalog.md`:

- **RP-02: State Lifecycle Completeness** — For each entity with a status/state field (detected during BQ3), verify ALL consumers handle ALL states. Check UI components, API endpoints, and business logic for missing state handlers.
- **RP-04: Boundary Value Reasoning** — For each constrained field (min/max length, numeric range, date range), reason about edge cases at each layer. Verify that boundary behavior is consistent across DB constraint, DTO validator, Zod schema, and UI feedback.
- **BQ1-BQ4 (already Tier 2)** — The existing Business Logic Questions are already reasoning-based. They remain part of this skill's Tier 2 analysis.

Document findings from reasoning as R-prefixed items (e.g., R-02-1, R-04-1).
