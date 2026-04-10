---
name: qa-data
description: "Audit data layer — schema consistency, migrations, dead columns, soft delete gaps, FK relations, and index coverage"
user-invocable: true
argument-hint: "[module] [--check N] [--group name]"
---

# QA Data — Data Layer Auditor

Verify database schema consistency, migration integrity, dead column detection, and soft delete compliance. Merges checks from qa-db-integrity and qa-dead-code.

## Execution Mode

- **Standalone** (`/qa-data [module]`): Diagnose-only. Scans the codebase, applies checks below, outputs a report. Does NOT modify files.
- **Via qa-scan** (`/qa-scan --check data`): qa-scan uses these checks as its checklist for the data layer, then applies fixes.

Shared conventions (scoring, framework detection, output format): see `qa-shared/reference.md`.

## Tier 1: Checklist

### Group: Schema Consistency (from qa-db-integrity)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| D-01 | Entity-Migration drift | **Critical** | | Entity column defined but not created in any migration |
| D-02 | Orphan migration column | **High*** | | Migration creates column that no entity maps to (see classification guide below) |
| D-03 | FK without index | **High** | | Foreign key column has no corresponding index |
| D-04 | Missing cascade config | **Medium** | | Parent is deletable but child has no onDelete option |
| D-05 | Nullable inconsistency | **High** | | Entity nullable setting != migration nullable setting |
| D-06 | Type mismatch | **High** | | Entity column type != migration column type |
| D-07 | Missing unique constraint | **Medium** | | Semantically unique fields (username/email/slug) lack unique constraint |
| D-08 | Soft delete gaps | **Medium*** | | Entity has deletedAt but some queries don't filter soft-deleted rows (escalate to **Critical** if query serves user-facing data — see note below) |
| D-09 | Decimal without precision/scale | **Medium** | | Decimal/float/numeric column missing explicit precision or scale |
| D-10 | Default value divergence | **High** | | Entity default vs migration DEFAULT mismatch or one side missing |
| D-11 | Raw table name mismatch | **Critical** | | QueryBuilder `leftJoin`/`innerJoin`/`from` uses hardcoded table name string that doesn't match the `@Entity('table_name')` decorator. TypeScript won't catch this — only fails at runtime. Grep for string-based joins and verify each table name against entity definitions. |
| D-12 | Immutable column missing DB-level protection | **Medium** | | Identity columns (`username`, `email`) that should be immutable post-creation lack DB-level protection. TypeORM does not natively support `update: false`, so verify that ALL service methods calling `.update()`, `.save()`, or direct property assignment on the entity exclude these fields. If protection exists only at DTO level (can be bypassed by service-level code, migrations, or seeders), flag for review. Cross-references `qa-inputs` #57 and `qa-crud` #14 for service-layer verification |

#### D-02 — Orphan Migration Column Classification Guide

Not all ghost columns (migration column with no entity mapping) are defects. Before flagging, determine the column's category:

| Category | Examples | Decision | Rationale |
|----------|----------|----------|-----------|
| **Standard extensibility pattern** | `social_login_type`, `oauth_provider`, `stripe_customer_id`, `two_factor_secret` | **Skip** | Common SaaS/auth features. Column is harmless (nullable, unused by ORM), and removing it destroys future extensibility. Removing + re-adding costs 2 migrations for no runtime benefit. |
| **Orphaned from deleted feature** | Column added for a feature that was explicitly removed (feature flag dropped, module deleted, PR reverted) | **High** — generate drop migration | Dead weight with no future intent. Check git history for deliberate removal signals. |
| **Scaffold/demo leftover** | Columns from boilerplate generators, tutorial code, or demo modules | **Manual** | Ask whether the demo module itself should be removed. If module stays, columns stay. |
| **External system dependency** | Columns written by triggers, ETL pipelines, reporting tools, or other services outside the ORM | **Skip** | ORM doesn't manage these; absence of entity mapping is expected. |
| **Truly unknown** | Cannot determine origin or intent from code, git history, or project docs | **Manual** | Escalate for human review rather than auto-deleting. |

**Key principle:** A ghost column that is nullable, has no index cost, and follows a recognizable pattern is NOT a defect — it is latent infrastructure. The cost of keeping it (a few bytes per row) is far lower than the cost of removing and re-adding it across environments.

#### D-08 — Soft Delete Gap Severity Escalation

Default severity is **Medium**, but escalate to **Critical** when:
- The query result is **rendered in user-facing UI** (chat messages, room lists, activity feeds, notifications)
- The query result is **returned in API responses** consumed by end users

Keep as **Medium** when:
- The query is used **internally only** (analytics, background jobs, admin-only reports, seeder scripts)

### Group: Dead Columns (from qa-dead-code)

| # | Check | Severity | Gate | Description |
|---|-------|----------|------|-------------|
| D-13 | No Create DTO path | **High** | | Entity column not in any Create DTO for that entity |
| D-14 | No Update DTO path | **Medium** | | Entity column not in any Update DTO for that entity |
| D-15 | No programmatic write | **High** | | Entity column never assigned in any service/repository method |
| D-16 | Response DTO ghost | **Medium** | | Entity column in Response DTO but never populated (always null) |
| D-17 | Read-only column | **Info** | | Entity column only used in WHERE/ORDER BY/SELECT but never written |

**Composite severity escalation:**
- Column fails D-13 + D-14 + D-15 = **Critical** (true dead column — no write path exists)
- Column fails D-13 + D-14 but passes D-15 = **Low** (system-managed column — verify intentional)
- Column fails only D-13 or only D-14 = report at individual check severity

#### Dead Column Exclusion Rules

These column types are always excluded from dead column analysis:

| Column Type | Detection Pattern |
|-------------|-------------------|
| Primary key | `@PrimaryGeneratedColumn` |
| createdAt / updatedAt / deletedAt | `@CreateDateColumn`, `@UpdateDateColumn`, `@DeleteDateColumn` |
| Relation properties | `@ManyToOne`, `@OneToMany`, `@OneToOne`, `@ManyToMany` |
| Join columns | `@JoinColumn` + adjacent relation decorator |
| Generated columns | `@Generated` |
| Virtual columns | `@VirtualColumn` |
| BaseEntity inherited columns | Detected via `extends BaseEntity` |

#### DTO Inheritance Resolution

| Pattern | Resolution |
|---------|-----------|
| `PartialType(CreateDto)` | All fields from CreateDto, all optional |
| `OmitType(CreateDto, ['field1', 'field2'])` | All fields from CreateDto except listed |
| `PickType(CreateDto, ['field1', 'field2'])` | Only listed fields from CreateDto |
| `IntersectionType(DtoA, DtoB)` | Union of fields from both DTOs |
| `extends PartialType(OmitType(Create, [...]))` | Chain: first Omit, then make all optional |

### Cross-Skill Triggers

| Condition found by qa-data | Trigger | Reason |
|----------------------------|---------|--------|
| New Entity column discovered (D-01) | → `qa-inputs` (full pipeline check) | New column needs Entity→DTO→Zod→Form coverage |
| Enum column with 3+ values | → `qa-inputs` BQ3 (State Transitions) | Verify state transition rules exist |
| Unique constraint on field (D-07) | → `qa-inputs` #18 (Unique constraint hint) | Frontend should show duplicate check |

## Tier 2: Reasoning Patterns

After completing Tier 1 checks, apply these reasoning patterns from `qa-shared/reasoning-catalog.md`:

- **RP-03: Filter Consistency** — For each query that filters by a condition (isActive, deletedAt, date range), find ALL other queries on the same table and verify they apply the same filters where appropriate. Pay special attention to COUNT/aggregation queries vs detail queries.
- **RP-08: Cascade Impact Analysis** — For each entity with delete/deactivate operations, trace all referencing entities and verify they handle the parent's deletion/deactivation gracefully.
- **RP-12: Soft Delete Ripple** — For each soft-deletable entity, find ALL queries (including raw SQL, QueryBuilder, JOINs) and verify deletedAt filtering. Check for raw queries that bypass ORM auto-filtering.

Document findings from reasoning as R-prefixed items (e.g., R-03-1, R-08-1, R-12-1).
