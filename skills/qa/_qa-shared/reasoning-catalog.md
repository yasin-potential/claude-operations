# Reasoning Patterns Catalog

Reasoning patterns are **thinking strategies**, not specific checks. Each pattern describes WHAT to think about and HOW to trace through code. The AI applies these after completing Tier 1 checklist checks within each QA layer skill.

## How to Use This Catalog

1. After Tier 1 checks complete, the orchestrator (qa-scan) determines which RPs apply based on Feature Map
2. For each applicable RP, follow the Strategy steps using code already read during Tier 1
3. Document any NEW issues found through reasoning as `R-` prefixed items (e.g., `R-07-1`)
4. R-items use the same severity scale as Tier 1 (Critical, Warning, Info)

## Pattern Structure

Each pattern has:
- **ID**: RP-XX
- **Name**: Human-readable name
- **Trigger**: Feature Map categories that activate this pattern
- **Strategy**: Step-by-step reasoning procedure
- **Example**: A concrete bug this pattern would catch
- **Applicable Skills**: Which QA layer skills should use this pattern

---

## RP-01: Data Flow Tracing

**Trigger**: `crud_list_detail`, any data appearing in more than one view/endpoint

**Strategy**:
1. Identify the data entity (DB table/column or API endpoint)
2. Trace ALL paths from source to display:
   - DB → Repository query → Service method → Controller response → Frontend fetch → Component render
3. At each hop, note any transformations, filters, or mappings applied
4. Compare: do all paths apply the same filters? Same transformations? Same access control?
5. Flag any divergence between paths as a potential inconsistency

**Example**:
A coach's patient list is displayed in two places: the admin users table (as a count "3명") and the coach detail page (as individual patient cards). The list API counts ALL assigned patients including inactive ones. The detail API only returns active patients. Result: count says 3, but detail shows 2.

**Applicable Skills**: qa-data, qa-api, qa-ui

---

## RP-02: State Lifecycle Completeness

**Trigger**: `state_machines` — any entity with a status/state/type field having 3+ possible values

**Strategy**:
1. Enumerate all possible states (from enum, DB check constraint, or frontend constants)
2. For each **consumer** of this field (UI component, API endpoint, business logic):
   a. Does it handle ALL states? Or only some?
   b. Is there a default/fallback for unknown states?
   c. What renders for each state? (Badge color, text, icon)
3. For each **state transition**:
   a. Is it validated? Can status jump from A→C without passing through B?
   b. Are side effects triggered correctly? (Notification on status change, audit log)
4. Check for **impossible states**: can the data reach a state that no UI handles?
5. Check the **detail page**: when navigating to an entity in an unexpected state, what does the user see?

**Example**:
Meeting status can be SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED. The meeting list component renders badges for SCHEDULED (blue) and COMPLETED (green). IN_PROGRESS and CANCELLED meetings show no badge — the cell is blank, confusing users.

**Applicable Skills**: qa-form, qa-ui, qa-data

---

## RP-03: Filter Consistency

**Trigger**: `crud_list_detail`, `soft_delete_entities`, `aggregations` — any query that filters data

**Strategy**:
1. Identify the filter condition (WHERE clause, query param, frontend filter)
2. Find ALL other queries/endpoints that touch the same table/resource
3. For each, ask: "Should this filter also apply here?"
4. Common missed filters:
   - Soft delete: `deletedAt IS NULL` or `WHERE deleted_at IS NULL`
   - Active status: `isActive = true` or `status != 'inactive'`
   - Role-based visibility: `coachId = currentUser.id`
   - Date ranges: not expired, within valid period
5. **Special attention to aggregation queries**: COUNT, SUM, AVG queries often miss filters that detail queries apply

**Example**:
`getAssignedPatientCount(coachId)` queries `coach_patient_assignment WHERE coach_id = ?` (no isActive filter). `getAssignedPatients(coachId)` queries the same table with `WHERE coach_id = ? AND is_active = true`. The count includes inactive patients; the detail list excludes them.

**Applicable Skills**: qa-data, qa-api

---

## RP-04: Boundary Value Reasoning

**Trigger**: Any numeric field, string length constraint, array/list, date range in `crud_list_detail` or `state_machines`

**Strategy**:
1. Identify constraints (min, max, required, nullable) at each layer (DB, DTO, Zod, Form)
2. For each constraint, reason about edge cases:
   - `min=0`: what happens with exactly 0? With -1?
   - `maxLength=100`: what happens at 100 chars? At 101? (especially for CJK where 1 char = 3 bytes)
   - `required`: what happens with empty string? Whitespace only? Null vs undefined?
   - Date range: what if start == end? What if end < start?
3. Check if edge cases are handled at ALL layers (DB constraint, DTO validator, Zod schema, UI feedback)
4. Pay attention to "off-by-one" in pagination (page=0 vs page=1, zero-indexed vs one-indexed)

**Example**:
A `name` field has `@MaxLength(50)` in the DTO but `.max(100)` in the Zod schema. Frontend allows 100 chars, backend rejects at 50 — user sees a generic "validation failed" error with no useful message.

**Applicable Skills**: qa-form, qa-api

---

## RP-05: Permission Boundary Tracing

**Trigger**: `role_views` — any endpoint or UI element that is role-restricted

**Strategy**:
1. Map the permission: which roles can access this feature?
2. Trace the enforcement chain at each layer:
   - Backend: guard/decorator on controller → service-level check → query filter (e.g., WHERE coachId = ?)
   - Frontend: route guard → component visibility → action button visibility → API error handling
3. Check for **gaps**: is there a layer where the restriction is not enforced?
4. Check for **escalation**: can a lower role modify data that affects a higher role's view?
5. Check **response data**: does the API return fields the requesting role shouldn't see?
6. Check **cross-role side effects**: when Coach changes patient data, does Admin see the change correctly?

**Example**:
A coach can see their own patients' exercise logs. The frontend route guard correctly limits access. But the API endpoint `/exercises/logs?patientId=X` has no backend check that the requesting coach is actually assigned to patient X. Any coach can view any patient's logs by changing the patientId parameter.

**Applicable Skills**: qa-guard, qa-api, qa-ui

---

## RP-06: Temporal Consistency

**Trigger**: `scheduled_tasks`, any feature involving timestamps, scheduling, expiration, timezones

**Strategy**:
1. Identify all timestamps in the feature (createdAt, updatedAt, scheduledAt, expiresAt)
2. Check: are comparisons done in the same timezone? Is the server timezone consistent?
3. Check: is the display timezone the user's local timezone or UTC?
4. Check: are "expired" items handled? (Meeting past its date, token past its TTL, notification expired)
5. Check: race conditions on time-based logic (check-then-act, TOCTOU)
6. Check: date formatting consistency (some pages show "2026-03-24", others show "3월 24일")

**Example**:
A meeting scheduled for "2026-03-25 14:00 KST" is stored as UTC in the database. The meeting list page formats it as local time correctly. But the Zoom integration sends the UTC time to Zoom's API, which interprets it as the meeting organizer's timezone (PST), scheduling it 17 hours wrong.

**Applicable Skills**: qa-data, qa-api, qa-ui

---

## RP-07: Aggregation Parity

**Trigger**: `aggregations` — any displayed count, sum, average, or derived number

**Strategy**:
1. Identify where the aggregated number is displayed (list page column, dashboard card, badge)
2. Trace it to its source:
   - Is it a SQL COUNT/SUM? An array.length? A pre-computed field?
   - Which repository/service method computes it?
3. Find the "detail view" that shows the individual items being counted
   - Which repository/service method fetches the actual items?
4. **Compare the two queries side by side**:
   - Same table? Same JOINs?
   - Same WHERE clauses? (isActive, deletedAt, date range, role filter)
   - Same relation traversal?
5. If they diverge, the count will not match the detail view — flag as Critical

**Example**:
Admin users page shows "Coach A: 1명 (patients)". Clicking into Coach A's detail page shows 0 patients. Root cause: the count query includes inactive assignment records, but the detail query filters by `isActive = true`. The inactive patient is counted but not displayed.

**Applicable Skills**: qa-data, qa-api, qa-ui

---

## RP-08: Cascade Impact Analysis

**Trigger**: Any delete operation, status change, or relationship modification in `crud_list_detail`

**Strategy**:
1. Identify the entity being modified/deleted
2. Find all entities that reference it (FK relationships, logical references via IDs)
3. For each referencing entity:
   a. What happens when the parent is deleted? (CASCADE, SET NULL, RESTRICT, error, nothing?)
   b. What happens when the parent's status changes to inactive/deleted?
   c. Does the UI handle orphaned references? (Link to deleted entity → 404? Blank name?)
4. Check the frontend: when navigating to a detail page for an entity whose parent was deleted/deactivated, what does the user see?
5. Check notifications/messages that reference the entity — do they still work?

**Example**:
A coach is deactivated (status → inactive). Their assigned patients still have `coachId` pointing to the inactive coach. The patient's dashboard shows "Your coach: [blank]" because the coach lookup filters by `status = 'active'`. The patient can't message their coach because the chat room check requires an active assignment.

**Applicable Skills**: qa-data, qa-api, qa-ui

---

## RP-09: Concurrency & Race Conditions

**Trigger**: `realtime` — any operation that reads-then-writes, or any real-time/socket feature

**Strategy**:
1. Identify read-modify-write sequences in service methods
2. Check: is there locking, optimistic concurrency (version field), or transaction isolation?
3. For real-time features:
   a. Does a socket event update match the REST API state?
   b. If user A sends a message via socket, does user B's REST-fetched message list include it?
   c. Are socket event handlers idempotent? (What if the same event is received twice?)
4. For forms: can two users edit the same entity simultaneously? What happens when both save?
5. For cache: does a mutation invalidate the correct cache key? Are there stale reads?

**Example**:
Coach opens a patient's exercise log page (fetched via REST). Patient completes an exercise, triggering a socket event. The socket handler updates a different cache key than what the page is watching. Coach's page shows stale data until manual refresh.

**Applicable Skills**: qa-api, qa-ui

---

## RP-10: Error Path Completeness

**Trigger**: Any operation that can fail — present in almost all features

**Strategy**:
1. For each API call in a feature, identify all failure modes:
   - Network failure / timeout
   - 400 Bad Request (validation error)
   - 401 Unauthorized / 403 Forbidden
   - 404 Not Found
   - 409 Conflict (duplicate, stale data)
   - 500 Internal Server Error
2. For each failure mode, trace the error path:
   - Backend: does the service throw the right exception type?
   - Frontend: does the error handler distinguish error types?
   - UI: does the user see a meaningful, actionable message?
3. Check: does the error state clean up properly? (Loading spinner stops, form re-enables, submit button unlocks)
4. Check: after an error, can the user retry? Is the retry mechanism appropriate?
5. Check: for destructive operations (delete), does failure leave the system in a consistent state?

**Example**:
User submits a form. Backend returns 409 Conflict (duplicate username). Frontend's generic error handler shows "Something went wrong." The user has no idea the username is taken and keeps retrying with the same username.

**Applicable Skills**: qa-api, qa-ui, qa-guard

---

## RP-11: Cross-App Consistency

**Trigger**: `role_views` — any feature that exists in multiple apps (frontend, dashboard, mobile)

**Strategy**:
1. Identify the feature across all apps that implement it
2. Compare API calls: do they call the same endpoints? Same parameters?
3. Compare displayed data: same fields? Same formatting? Same sort order?
4. Compare UX patterns: if one app has search, do others? If one has pagination, do others?
5. Compare role restrictions: same permissions enforced?
6. Check real-time sync: if a mutation in one app affects data in another, is it reflected?
7. Check navigation: can a user reach the same feature via consistent paths across apps?

**Example**:
The notification page exists in both patient frontend and admin dashboard. The patient version shows unread count and supports mark-as-read. The admin version shows notifications but has no unread count and no mark-as-read — inconsistent feature parity despite both calling the same API.

**Applicable Skills**: qa-api, qa-ui

---

## RP-12: Soft Delete Ripple

**Trigger**: `soft_delete_entities` — any entity with a `deletedAt` column or equivalent

**Strategy**:
1. Find ALL queries that touch the soft-deletable entity's table
2. For each query:
   a. Does it explicitly filter by `deletedAt IS NULL` (or ORM equivalent)?
   b. If the ORM auto-filters soft-deleted records (e.g., TypeORM global scope), are there any raw queries that bypass this?
3. Check JOINs: if entity A is soft-deleted, do queries for entity B (which JOINs to A) handle the case where A.deletedAt is not null?
4. Check UI references: links/badges/counts that reference soft-deleted entities — what does the user see?
   - Link to deleted entity → should show "deleted" indicator or redirect
   - Count including deleted entities → inflated number
   - Assignment to deleted entity → broken relationship
5. Check the API: when a GET endpoint returns a related entity that has been soft-deleted, does it include it or filter it out? Is this consistent?

**Example**:
A patient is soft-deleted (withdrawn). The coach's patient list correctly filters them out. But the admin's "Coach summary" card still counts the deleted patient in the total because the count query uses a raw SQL `SELECT COUNT(*) FROM coach_patient_assignment WHERE coach_id = ?` without checking the patient's `deletedAt`.

**Applicable Skills**: qa-data, qa-api

---

## Adding New Reasoning Patterns

When a bug escapes QA and cannot be mapped to any existing RP:

1. Record the bug in the project's `QA_REGRESSION_PATTERNS.md`
2. Generalize: what **class** of issue does this represent?
3. Draft a new RP following the pattern structure above
4. Assign the next ID (RP-13, RP-14, etc.)
5. Define clear Trigger, Strategy, and Example
6. Map to applicable QA layer skills
7. Update the Feature → RP Mapping table in `profile-schema.md`

When a bug CAN be mapped to an existing RP but the RP didn't catch it:
1. Add the bug as a new Example under the existing RP
2. Refine the Strategy if a step was too vague to catch this specific case
3. Consider whether the Trigger needs broadening
