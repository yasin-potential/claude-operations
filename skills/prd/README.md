# PRD Skills

PRD lifecycle management — generate, update, convert, and classify PRD documents.

## Pipeline Flow

```
input-classifier ── determine input type
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
   generate-prd     update-prd      pdf-to-prd
         │
         ▼
   generate-tech-prd
         │
         ▼
   generate-korean-prd
```

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [generate-prd/](generate-prd/) | `/generate-prd` | Generate Feature PRD (Phase A) from client input |
| [generate-tech-prd/](generate-tech-prd/) | `/generate-tech-prd` | Generate Technical PRD (Phase B) from Feature PRD |
| [generate-korean-prd/](generate-korean-prd/) | `/generate-korean-prd` | Korean PRD PDF with company branding |
| [update-prd/](update-prd/) | `/update-prd` | Update existing PRD with client feedback |
| [pdf-to-prd/](pdf-to-prd/) | `/pdf-to-prd` | Convert PDF to structured markdown PRD |
| [input-classifier/](input-classifier/) | `/input-classifier` | Auto-classify input type before PRD modification |

## Naming Convention

- **Operations repo**: `skills/prd/{skill-name}/`
- **Global skills** (`~/.claude/skills/`): `{skill-name}/` (e.g., `generate-prd/`)
- **Slash commands**: `/generate-prd`, `/update-prd`, etc.
