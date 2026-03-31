---
name: generate-tech-prd
description: "Generate a Technical PRD (Phase B) from a completed Feature PRD. Produces DB Schema, Permission Matrix, and System Design sections. Run after /generate-prd (Phase A)."
argument-hint: "Path to Feature PRD file (e.g., .claude-project/prd/MyApp/MyApp_FeaturePRD_260329.md)"
---

# Generate Technical PRD — Phase B

Generate Technical PRD sections (Schema, Permissions, System Design) from a completed Feature PRD.
This skill takes the output of `/generate-prd` (Phase A) as input and produces Sections 5-7.
The final output is a complete merged PRD (Feature + Technical).

## Core Principles

1. **Feature PRD as Source of Truth**: All entities, permissions, and integrations are derived from Phase A
2. **Full Recommendation**: Technical decisions use `[💡 Recommended]` — developer team reviews (not PM)
3. **Strict Density**: Every entity needs full column-level schema, every permission cell must be filled
4. **Config Uniqueness**: Port, Redis prefix, cookie names, DB name must not collide with other projects
5. **Cross-Phase Consistency**: Section 5-7 must exactly match Feature PRD Section 3/4 entities
6. **Machine Verification**: QA uses only counting/existence rules

## Agent Configuration

| Agent | Model | Role |
|-------|-------|------|
| **tech-parser** | sonnet | Extract entities, permissions, integrations from Feature PRD |
| **config-allocator** | sonnet | Allocate unique ports, prefixes, cookie names, DB name |
| **tech-writer** | opus | Write Sections 5-7 using extracted inventories |
| **qa-tech** | sonnet | Validate against 7 technical rules |
| **support** | sonnet | Fix QA FAIL items (max 3 rounds) |

## Reference Files

All references located under `skills/prd/generate-tech-prd/references/`:
- `prd-template-tech.md` — Section 5-7 output structure
- `prompt-templates-tech.md` — Agent specs + write-mode prompts
- `depth-guide-tech.md` — Mandatory density requirements
- `validation-tech.md` — 7 technical QA rules

---

## Phase B1: Extract

### B1.1 Input Validation

Read Feature PRD path from `$ARGUMENTS`.
If no path provided, auto-detect the most recent `*_FeaturePRD_*.md` in `.claude-project/prd/`.

**Pre-check — ABORT if Feature PRD is incomplete:**
1. Scan for unresolved `[💡 Recommended:]` markers
2. If found → ABORT:
   ```
   Error: Feature PRD contains {N} unresolved [💡 Recommended:] items.
   PM must confirm all items via /generate-prd Phase A before Technical PRD can be generated.

   Unresolved items:
   - [item 1]
   - [item 2]

   Run /generate-prd to complete Phase A first.
   ```

### B1.2 Project Folder Setup

Use existing project folder from Phase A:
```bash
mkdir -p .claude-project/prd/{ProjectName}/intermediate
mkdir -p .claude-project/prd/{ProjectName}/drafts
```

### B1.3 Launch Parallel Agents

Launch **tech-parser** and **config-allocator** simultaneously.

```
┌──────────────────────────────────────────────┐
│  Parallel Execution (Phase B1)               │
│                                              │
│  tech-parser (sonnet)      → 3 inventories   │
│  config-allocator (sonnet) → project-config  │
│                                              │
└──────────────────────────────────────────────┘
```

### B1.4 Tech-Parser → 3 Inventory Files

Launch **tech-parser** (sonnet) to extract from Feature PRD:

#### entity-inventory.md
```markdown
# Entity Inventory — {ProjectName}

## Entities (Total: N)
| # | Entity | Source Routes | CRUD Operations | Estimated Columns |
|---|--------|-------------|-----------------|-------------------|

## Relationships
| Entity A | Relationship | Entity B | Source |
|----------|-------------|----------|--------|

## Status Enums (from Section 1)
| Enum | Values | Used By |
|------|--------|---------|
```

#### permission-inventory.md
```markdown
# Permission Inventory — {ProjectName}

## Actions × Roles
| Resource | Action | Source | Roles with Access | Ownership |
|----------|--------|--------|-------------------|-----------|
```

#### integration-inventory.md
```markdown
# Integration Inventory — {ProjectName}

## 3rd Party Services (from Section 2)
| Service | Purpose | Env Variables Needed |
|---------|---------|---------------------|

## Notification Channels (from Section 2.5)
| Channel | Provider | Env Variables |
|---------|---------|--------------|

## Detected Features → Conditional Sections
| Feature | Detected | Conditional Section |
|---------|----------|-------------------|
```

### B1.5 Config Allocator

Launch **config-allocator** (sonnet):

1. Read `claude-operations/docs/project-registry.md`
2. Allocate next available values:
   - `backend_port`: Next unused in range 3000-3099
   - `frontend_ports`: Next two unused in range 5173-5299
   - `redis_prefix`: `{projectslug}:` (lowercase, no hyphens)
   - `cookie_names`: `{ProjectName}Token`, `{ProjectName}RefreshToken`, `{ProjectName}AdminToken`
   - `db_name`: `{project_slug}_db`
3. Write `project-config.md` to intermediate/
4. Append new entry to `project-registry.md`

---

## Phase B2: Write

Launch **tech-writer** (opus).

**Input:**
- Feature PRD (full document)
- `entity-inventory.md`
- `permission-inventory.md`
- `integration-inventory.md`
- `project-config.md`

**Reference:**
- `depth-guide-tech.md`
- `prd-template-tech.md`

### Tech-Writer Sections

- **Section 5**: Tech Stack & System Design
  - Technologies table
  - Third-Party Integrations
  - Key Architectural Decisions
  - Environment Variables (using `project-config.md` values)
  - Conditional subsections (Auth Flow, File Pipeline, Real-time, Billing, Multi-tenancy)
- **Section 6**: Data Model — Full Schema
  - Entity Relationships
  - Full Schema per entity (minimum 5 columns, PK, FK, constraints)
  - Status Enums (matching Feature PRD Section 1)
  - Index Hints
  - Soft Delete policy
- **Section 7**: Permission Matrix
  - Action × Role Matrix (no empty cells)
  - Ownership Rules
  - Role Hierarchy

### TBD Handling

- All technical decisions: fill with `[💡 Recommended]` best-practice defaults
- Developer team reviews (not PM confirmation gate)

### Output File

- `.claude-project/prd/{ProjectName}/drafts/section-5-7.md`

---

## Phase B3: QA + Fix (Max 3 Rounds)

### B3.1 QA Validation

Launch **qa-tech** (sonnet) to validate against 7 rules.

> Detailed rules: see `references/validation-tech.md`

| # | Rule | FAIL Condition |
|---|------|---------------|
| 9 | Tech Stack Completeness | Technologies < 5 layers, or 3rd party missing |
| 10 | Entity Coverage | CRUD entity from Feature PRD missing from Section 6 |
| 11 | Permission Completeness | Action without Permission Matrix entry, or empty cells |
| 14 | Full Schema Completeness | Entity without schema, < 5 columns, missing PK/FK |
| 16 | Config Uniqueness | Port/prefix/cookie/DB collision with existing project |
| C1 | Cross-Phase Consistency | Entity mismatch between Feature PRD and Section 5-7 |
| C2 | FK Integrity | FK references non-existent entity or column |

### B3.2 FAIL Handling

Same as Phase A: support fixes → qa re-validates → max 3 rounds → manual intervention if still failing.

---

## Phase B4: Merge + Deliver

### B4.1 Merge into Complete PRD

1. Read Feature PRD
2. Insert Sections 5-7 after Section 4
3. Update Section 8 (Open Questions) with any technical questions
4. Verify section numbering and cross-references

### B4.2 Save Final Files

- Complete PRD: `[AppName]_PRD_[YYMMDD].md` in `.claude-project/prd/{ProjectName}/`
- Feature PRD preserved as-is (for audit/reference)

### B4.3 Result Report

```markdown
## Technical PRD Generation Complete

### Output
- Complete PRD: `.claude-project/prd/{ProjectName}/[AppName]_PRD_[YYMMDD].md`
- Feature PRD: preserved at original location

### Summary
- Section 5: Tech Stack & System Design ✅
  - Technologies: {N} layers
  - Third-Party: {M} services
  - Conditional sections: {list}
- Section 6: Data Model — Full Schema ✅
  - Entities: {K} tables
  - Relationships: {R} defined
  - Index hints: {I} recommended
- Section 7: Permission Matrix ✅
  - Matrix: {R} roles × {A} resources
  - Ownership rules: {O} defined
- QA Validation: PASS ({N} rounds, 7 rules)
- Config allocated: port {PORT}, DB {DB_NAME}

### Output Structure
.claude-project/prd/{ProjectName}/
├── intermediate/
│   ├── entity-inventory.md
│   ├── permission-inventory.md
│   ├── integration-inventory.md
│   └── project-config.md
├── drafts/
├── {AppName}_FeaturePRD_{YYMMDD}.md   ← Phase A output (preserved)
└── {AppName}_PRD_{YYMMDD}.md          ← Complete merged PRD

### Next Steps
1. Review the complete PRD with the development team
2. Begin development setup using Section 5 tech stack
3. Create database schema from Section 6
4. Implement permission guards from Section 7
```

---

## Error Handling

| Situation | Response |
|-----------|----------|
| Feature PRD has unresolved `[💡 Recommended:]` | ABORT with list of unresolved items |
| Feature PRD not found | Error message with expected path format |
| Agent timeout/failure | Retry once, then mark failed and continue |
| QA 3-round FAIL | Present FAIL items + manual intervention request |
| Config registry not found | Warn and generate without config allocation |
| Token limit exceeded | Write sections sequentially |
