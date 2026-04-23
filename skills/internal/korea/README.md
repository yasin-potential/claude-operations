# Korea Skills

Korea-specific tooling — document formats, government filings, domestic services.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [hwp-analyze/](hwp-analyze/) | `/hwp-analyze` | Analyze HWP/HWPX file structure (tables, fields, filled vs. empty cells) |
| [hwp-fill/](hwp-fill/) | `/hwp-fill` | Fill an HWP/HWPX form with values from MD or user input |
| [hwp-template/](hwp-template/) | `/hwp-template` | Save and manage HWPX form templates per project |

## HWP Pipeline

```
HWPX form ──▶ /hwp-analyze ──▶ field list
                                  │
          /hwp-template save ◀────┤
                                  ▼
       MD content ───▶ /hwp-fill ──▶ new HWPX
```

## OS Support

| OS | .hwp | .hwpx | Method |
|----|------|-------|--------|
| Windows (with 한글 installed) | Yes | Yes | `pyhwpx` library |
| macOS / Linux | No | Yes | Direct XML editing (unzip → edit `section0.xml` → zip) |

On macOS/Linux, `.hwp` is not supported — ask the user to re-save as `.hwpx` from 한글.

## Attribution

Upstream: [nathankim0/easy-hwp](https://github.com/nathankim0/easy-hwp) — MIT License.
Migrated from the marketplace plugin layout (`plugins/easy-hwp/skills/*`) into this operation skills bucket, with SKILL.md files translated to English per [operation/CLAUDE.md](../../../CLAUDE.md) rule. See [LICENSE](LICENSE).

## Naming Convention

- **Operations repo**: `skills/internal/korea/{skill-name}/`
- **Global skills** (`~/.claude/skills/`): `{skill-name}/` (flattened — `hwp-analyze/`, `hwp-fill/`, `hwp-template/`)
- **Slash commands**: `/hwp-analyze`, `/hwp-fill`, `/hwp-template`
