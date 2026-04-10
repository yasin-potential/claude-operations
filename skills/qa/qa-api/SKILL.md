---
name: qa-api
description: "Audit API layer — CRUD completeness, frontend-backend sync, response shapes, error handling, and pagination"
user-invocable: true
argument-hint: "[module] [--check N]"
---

# QA API — API Layer Auditor

Verify CRUD endpoint completeness and frontend-backend API synchronization. Merges checks from qa-crud and qa-api-sync.

## Execution Mode

- **Standalone** (`/qa-api [module]`): Diagnose-only. Scans the codebase, applies checks below, outputs a report. Does NOT modify files.
- **Via qa-scan** (`/qa-scan --check api`): qa-scan uses these checks for the API layer.

Shared conventions (scoring, framework detection, output format): see `qa-shared/reference.md`.

## Tier 1: Checklist

### CRUD Completeness (from qa-crud)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| A-01 | Missing CRUD operation | **High** | | Entity has Create but no Read, etc. |
| A-02 | Missing pagination | **High** | | List endpoint returns all records without page/limit |
| A-03 | Missing search/filter | **Medium** | | List endpoint has no search/filter params |
| A-04 | Missing sort | **Low** | | List endpoint has no sort/order params |
| A-05 | Inconsistent response shape | **Medium** | | Some endpoints wrap in {data,meta} but others return raw |
| A-06 | Missing error response | **High** | | No exception handling for not-found, conflict, validation |
| A-07 | No soft delete | **Medium** | | Entity has deletedAt but controller uses hard delete |
| A-08 | Missing bulk operations | **Low** | | Only single-item CRUD, no bulk support |
| A-09 | Missing ownership check | **High** | | Update/Delete doesn't verify requesting user owns resource |
| A-10 | Frontend CRUD gap | **High** | | Backend endpoint exists but no frontend UI action |
| A-11 | Missing status toggle | **Medium** | | Entity has isActive/status column but no toggle endpoint or UI |
| A-12 | Response field completeness | **High** | | GET endpoint response missing entity columns that should be exposed |
| A-13 | Static route shadowed by parameterized route | **High** | `backend_nestjs` | `@Patch('users/:id')` declared before `@Patch('users/bulk-status')` causes parameterized route to capture the static segment |
| A-14 | Service layer identity field bypass | **Critical** | | Service method directly assigns identity fields (`username`, `email`, `id`) on entity objects outside of create/register methods. **Scan**: Grep for patterns like `entity.username = ...`, `entity.email = ...`, `.update(id, { username: ... })`, `Object.assign(entity, { username: ... })` in all service files. Exclude: (1) create/register methods where identity assignment is expected, (2) entity construction in tests/seeders. Any match in an update/save flow = identity field mutation bypassing DTO protection |

### API Sync (from qa-api-sync)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| AS-01 | Route mismatch | **Critical** | | Frontend calls URL that doesn't exist in backend |
| AS-02 | HTTP method mismatch | **Critical** | | Frontend uses POST but backend expects PATCH |
| AS-03 | Missing query params | **High** | | Backend accepts search/filter/pagination but frontend doesn't send |
| AS-04 | Missing body params | **High** | | DTO requires fields frontend doesn't include |
| AS-05 | Extra body params | **Medium** | | Frontend sends fields not in DTO |
| AS-06 | Response type mismatch | **Medium** | | Frontend TypeScript interface doesn't match backend response |
| AS-07 | Unused backend endpoint | **Info** | | Controller endpoint with no frontend caller |
| AS-08 | Missing error handling | **Medium** | | Frontend service call with no try/catch |
| AS-09 | Auth header missing | **High** | | Protected endpoint but frontend doesn't include auth |
| AS-10 | Content-Type mismatch | **Medium** | | Endpoint expects multipart but frontend sends JSON |
| AS-11 | Route parameter shadowing | **Critical** | `backend_nestjs` | Static route declared after parameterized route with same prefix — never reachable at runtime |
| AS-12 | Incomplete submit payload | **High** | | Frontend form collects a value but the submit handler doesn't include it in the API call payload |
| AS-13 | Service layer field drop | **High** | | Service method receives a DTO field but doesn't pass it through to the repository/database layer |
| AS-14 | Response construction field omission | **High** | | Service method hand-builds a response object that omits entity fields the frontend expects |

## Tier 2: Reasoning Patterns

After Tier 1, apply:

- **RP-01: Data Flow Tracing** — For each data entity displayed in the frontend, trace the full path: DB → Repository → Service → Controller → Frontend fetch → Component render. Flag any transformations, filters, or field omissions that differ between paths.
- **RP-07: Aggregation Parity** — For each aggregated count/sum displayed in a list or dashboard, trace its computation back to the query. Find the detail view showing individual items. Compare the two queries' filter conditions side-by-side.
- **RP-11: Cross-App Consistency** — For features present in multiple frontend apps, verify they call the same API endpoints with the same parameters and display the same data.

Document findings as R-prefixed items.

## Cross-Skill Triggers

| Condition found | Trigger | Reason |
|-----------------|---------|--------|
| New Update endpoint discovered (A-01) | → `qa-inputs` BQ1 (Field Mutability) | Every new update endpoint needs field mutability review |
| Missing ownership check (A-09) | → `qa-auth` #5 (Missing current-user validation) | Cross-validate auth enforcement |
| Bulk operation without size limit (A-08) | → `qa-security` (request size limits) | Prevent DoS via unbounded batch operations |
