# QA Skills

QA auditing across all layers — API, data, UI, security, forms, and runtime.

## Orchestrator

**`/qa-scan`** — Universal QA orchestrator. Diagnoses, fixes, and verifies across all layers with three execution modes (quick / standard / deep).

## Pipeline Flow

```
qa-scan (orchestrator)
   │
   ├── qa-api     ── API CRUD, sync, response shapes, error handling
   ├── qa-data    ── Schema, migrations, FK relations, indexes
   ├── qa-form    ── Entity → DTO → Schema → Form UI consistency
   ├── qa-guard   ── Auth, role guards, route protection, security
   ├── qa-ui      ── States, buttons, modals, layout, a11y, i18n
   └── qa-runtime ── Playwright browser QA, console errors, CLS
```

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [qa-scan/](qa-scan/) | `/qa-scan` | Orchestrator — route to appropriate QA skills |
| [qa-api/](qa-api/) | `/qa-api` | API CRUD completeness, frontend-backend sync |
| [qa-data/](qa-data/) | `/qa-data` | Schema consistency, migrations, dead columns |
| [qa-form/](qa-form/) | `/qa-form` | Full-stack input field consistency and validation |
| [qa-guard/](qa-guard/) | `/qa-guard` | Auth & security — guards, tokens, injection |
| [qa-ui/](qa-ui/) | `/qa-ui` | UI/UX — states, navigation, accessibility |
| [qa-runtime/](qa-runtime/) | `/qa-runtime` | Playwright browser QA — actionability, a11y, CLS |

## Shared Rules

`_qa-shared/` contains foundational documents used across all QA skills:

| File | Purpose |
|------|---------|
| `reference.md` | Execution rules, framework detection, scoring |
| `profile-schema.md` | `.qa-profile.yaml` schema for project auto-detection |
| `reasoning-catalog.md` | Reasoning patterns (RP-XX) for analysis strategies |

## Naming Convention

- **Operations repo**: `skills/qa/{skill-name}/`
- **Global skills** (`~/.claude/skills/`): `{skill-name}/` (e.g., `qa-api/`)
- **Slash commands**: `/qa-scan`, `/qa-api`, etc.
