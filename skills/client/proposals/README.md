# Proposals Skills

Client-facing proposal generation — interactive HTML slide decks (PPT-style) with bilingual Korean/English support.

## Skills

| Skill | Command | Output |
|-------|---------|--------|
| [generate-proposal/](generate-proposal/) | `/generate-proposal` | `[Proposal] {ProjectName}.html` — 26-variable template with base64-embedded assets, Korean or English per-file. |
| [generate-project-overview/](generate-project-overview/) | `/generate-project-overview` | `[Overview] {ProjectName}.html` — branded HTML deck (light+dark, brand tokens) summarizing one-liner, glossary, user types, deliverables, per-deliverable features, timeline, open questions. On confirmation, writes a `.md` companion and hands off to `/generate-prd`. |

## Naming Convention

- **Operations repo**: `skills/client/proposals/{skill-name}/`
- **Global skills** (`~/.claude/skills/`): `{skill-name}/` (e.g., `generate-proposal/`)
- **Slash commands**: `/generate-proposal`
