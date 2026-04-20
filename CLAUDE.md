# claude-operations Rules

## All Skills Must Be Written in English

Every skill file (`SKILL.md`) in this repo **must be written entirely in English** — including descriptions, check names, instructions, examples, and comments. No other languages allowed.

---

## Skill File Convention

All skills follow the official Claude Code convention:
- **File name**: `SKILL.md` (uppercase, required)
- **Location**: `skills/<category>/<skill-name>/SKILL.md`
- **Supporting files**: Place in the same skill directory (e.g., `references/`, `templates/`)
- **Frontmatter**: Only use supported fields: `name`, `description`, `argument-hint`, `user-invocable`, `disable-model-invocation`

---

## Framework-Agnostic Requirement

All skills must work with **any framework/language combination**. Verify the following when creating or modifying a skill.

### Prohibited

- Hardcoding a specific framework (e.g., NestJS-only, TypeORM-only, React-only logic)
- Assuming a specific file structure (e.g., fixed paths like `src/modules/`, `src/entities/`)
- Searching only for framework-specific decorators/annotations (e.g., only `@Controller`, `@Entity`)

### Required

- **Framework auto-detection table**: Read `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `composer.json`, etc. to identify the framework
- **Framework-specific pattern mapping**: Branch file patterns, decorators, and structure based on detected framework
- **Unknown framework fallback**: When detection fails, fall back to generic patterns (filenames, export patterns, etc.)

### Verification Checklist

Before merging any skill PR or modification, **run `/qa-skill-review <skill-name>`** to auto-validate. The manual checklist below is for reference:

- [ ] Has framework detection logic?
- [ ] Works beyond NestJS — Express, FastAPI, Spring Boot, Laravel, Django, etc.?
- [ ] Works beyond React — Vue, Angular, Svelte, etc.?
- [ ] No hardcoded paths (`src/modules/`, `src/entities/`)?
- [ ] Has fallback logic when detection fails?
- [ ] Written entirely in English?

---

## Category README Maintenance

When adding, removing, or renaming a skill within a category:

1. **Update the category `README.md`** — Add/remove the skill from the Skills table
2. **Update `skills/README.md`** — Update the category map if skill count changed or a new category was created

When creating a new category folder:

1. Create a `README.md` following the convention in `skills/README.md` → Category README Convention
2. Add the category to the `skills/README.md` category map
3. Use [app-release/README.md](skills/app-release/README.md) as the reference model

---

## Auto-Sync to Global Skills

After creating or modifying any skill, sync between `~/.claude/skills/` and this repo.

- **Sync commands**: Copy the modified skill directory to the matching global path (`~/.claude/skills/{name}/`). Global uses the leaf folder name.
- **Direction does not matter** — both locations must always match. After any skill edit, sync whichever side was NOT edited.
- Do NOT skip this step — the global directory is not a git repo and has no other way to receive updates.

### Skills Directory Structure

```
skills/
  client/                  ← everything the client sees
    prd/                     ← PRD lifecycle
      generate-prd/            ← Generate complete PRD (Feature + Technical). Default `--full`; `--feature` / `--tech` / `--interview` flags supported.
      generate-korean-prd/     ← Korean PRD PDF with branding
      update-prd/              ← Update PRD with client feedback
      pdf-to-prd/              ← Convert PDF to structured markdown PRD
      input-classifier/        ← Auto-classify input before PRD modification
    meetings/                ← Client meeting presentations
      kickoff/                 ← Project kickoff presentation (`/kickoff`)
      weekly/                  ← Weekly meeting agenda + presentation (`/weekly`)
      closing/                 ← Project closing pipeline + presentation (`/closing`)
    billing/                 ← Client billing documents
      invoice/                 ← Invoice (견적서) HTML/PDF
      transaction-statement/   ← Transaction statement (거래명세서) HTML/PDF
    reports/                 ← Client-facing reports
      korean-government/       ← Reports for Korean government submission
        result-report/           ← Project result report (결과보고서)
  internal/                ← team-only tools
    sop/                     ← SOP creation + Notion integration
    kb/                      ← Knowledge base (ingest, compile, query)
    tickets/                 ← Structured ticket generation
    training/                ← Random project specs for training
  qa/                      ← QA auditing pipeline
    _qa-shared/              ← Shared patterns & conventions
    qa-api/  qa-data/  qa-form/  qa-guard/  qa-runtime/  qa-scan/  qa-ui/
  app-release/             ← App store release pipeline
    _ship/                   ← Pipeline orchestrator
    _store-shared/           ← Shared rules
    assets/  build/  deploy/  native/  prep/  review/  submit/
```

Note: Operations uses short folder names (`app-release/prep/`), global uses prefixed names (`~/.claude/skills/store-prep/`).
Each category folder has a `README.md` — see [skills/README.md](skills/README.md) for the full map and convention.

---

## Shared Asset Tiers

Three tiers for non-skill-specific assets. Choose by scope of reuse:

| Tier | Location | Scope | When to use |
|------|----------|-------|-------------|
| 1 | `../resources/` (repo root) | Cross-module (operation + design + mobile) | Company logo, seal, brand palette — consumed by hooks/scripts or non-synced skills only. [README](../resources/README.md) |
| 2 | `resources/` (this submodule) | Operation-only, shared across 2+ operation skills | Client logos, tech stack icons, office imagery. [README](resources/README.md) |
| 3 | `skills/.../{skill}/images/` | Single skill | Portfolio screenshots, skill-unique illustrations |

**Global-sync caveat**: Tiers 1 and 2 sit OUTSIDE `~/.claude/skills/{name}/`. Relative paths like `../../resources/` break after global sync. For skills in the auto-sync list, either (a) keep assets in Tier 3, or (b) have the sync script copy Tier 1/2 assets into the skill's own directory before pushing to `~/.claude/skills/`.

**Promotion path**: start Tier 3. Promote to Tier 2 when a second operation skill needs the asset. Promote to Tier 1 when design or mobile needs it too.

---

### Framework Detection Example

```markdown
| Framework | Detection Signal | File Patterns |
|-----------|-----------------|---------------|
| NestJS | `@nestjs/core` in package.json | `*.controller.ts`, `*.service.ts`, `*.module.ts` |
| Express | `express` in package.json | `routes/*.js`, `*.router.js` |
| FastAPI | `fastapi` in requirements.txt | `routers/*.py`, `main.py` |
| Spring Boot | `spring-boot` in pom.xml/build.gradle | `*Controller.java`, `*Service.java` |
| Django | `django` in requirements.txt | `views.py`, `urls.py`, `models.py` |
| Laravel | `laravel/framework` in composer.json | `*Controller.php`, `routes/*.php` |
```

---

## Skill Guide

For a practical guide to all skills with prerequisites, pipelines, and tips, see [resources/docs/skill-guide.md](resources/docs/skill-guide.md).

---

## Credentials

This is a **cross-module rule** defined at the root — see [../CLAUDE.md → Credentials](../CLAUDE.md) and the full guide at [../resources/docs/credentials-with-1password.md](../resources/docs/credentials-with-1password.md). Reference implementation: [scripts/bolta/](scripts/bolta/).

All new operation scripts that need API keys follow the same pattern.
