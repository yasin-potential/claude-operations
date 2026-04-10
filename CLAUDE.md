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
3. Use [store/README.md](skills/store/README.md) as the reference model

---

## Auto-Sync to Global Skills

After creating or modifying any skill, sync between `~/.claude/skills/` and this repo.

- **Sync commands**: See [docs/sop/skill-sync-guide.md](docs/sop/skill-sync-guide.md)
- **Direction does not matter** — both locations must always match. After any skill edit, sync whichever side was NOT edited.
- Do NOT skip this step — the global directory is not a git repo and has no other way to receive updates.

### Skills Directory Structure

```
skills/
  prd/                     ← PRD lifecycle skills
    generate-prd/          ← Generate PRD from client input
    generate-korean-prd/   ← Korean PRD PDF with branding
    generate-tech-prd/     ← Technical PRD (Phase B) from Feature PRD
    update-prd/            ← Update PRD with client feedback
    pdf-to-prd/            ← Convert PDF to structured markdown PRD
    input-classifier/      ← Auto-classify input before PRD modification
  docs/                    ← Document generation skills
    generate-ppt/          ← HTML presentations with branding
    generate-sop/          ← SOP creation + Notion integration
    generate-invoice/      ← Invoice (견적서) HTML/PDF
    generate-statement/    ← Transaction statement (거래명세서) HTML/PDF
    generate-project-report/  ← Government project result report
    generate-random-project/  ← Random project specs for training
    review-command/        ← Skill file validation & compatibility check
  qa/                      ← QA auditing skills
    _qa-shared/            ← Shared patterns & conventions
    qa-api/  qa-data/  qa-form/  qa-guard/  qa-runtime/  qa-scan/  qa-ui/
  store/                   ← App store submission pipeline
    _ship/                 ← Pipeline orchestrator
    _store-shared/         ← Shared rules
    assets/  build/  deploy/  native/  prep/  review/  submit/
  fullstack/               ← Fullstack pipeline skills
    deployment/            ← Deploy to dev/staging/production
    iteration-manager/     ← Iteration cycle management
  git-workflow/            ← Git workflow skills
    create-dev-pr/         ← PR creation to dev branch
  code-cleanup/            ← Dead code analysis & removal
  project-close/           ← Project closing workflow
  project-kickoff/         ← Client kick-off presentation
  ticketcreator/           ← Structured ticket generation
```

Note: Operations uses short folder names (`store/prep/`), global uses prefixed names (`~/.claude/skills/store-prep/`).
Each category folder has a `README.md` — see [skills/README.md](skills/README.md) for the full map and convention.

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

For a practical guide to all skills with prerequisites, pipelines, and tips, see [docs/skill-guide.md](docs/skill-guide.md).
