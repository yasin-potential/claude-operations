---
name: hwp-template
description: Save and manage reusable Korean HWP/HWPX form templates per project. Use when the user asks to "save a template", "register a 한글 form", or "list templates".
---

# Manage Korean HWP/HWPX Templates

## Input
$ARGUMENTS

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `save <name> <file>` | Register a template | `/hwp-template save IRB IRB_form.hwpx` |
| `list` | List saved templates | `/hwp-template list` |
| `info <name>` | Show template details | `/hwp-template info IRB` |
| `delete <name>` | Remove a template | `/hwp-template delete IRB` |

## Storage location

Templates are saved **relative to the current project directory**:

```
{project}/
└── templates/
    ├── index.json      # template metadata
    └── {name}.hwpx     # template files
```

## Procedure

### save

1. Create `templates/` if it does not exist
2. Copy the file to `templates/{name}.hwpx`
3. Run the analyzer (see `hwp-analyze`) to extract the field list
4. Append metadata to `templates/index.json`:

```json
{
  "templates": [
    {
      "name": "IRB",
      "file": "IRB.hwpx",
      "fields": ["연구과제명", "연구책임자", "연구기간"],
      "created": "2024-01-15"
    }
  ]
}
```

### list

1. Read `templates/index.json`
2. Render the template list as a table:

```
Templates:
| Name | Fields | Registered |
|------|--------|------------|
| IRB  | 15     | 2024-01-15 |
```

### info

1. Look up the template in `templates/index.json`
2. Show:
   - Name, file path
   - Field list (slots to fill)
   - Registration date

### delete

1. Delete `templates/{name}.hwpx`
2. Remove the entry from `templates/index.json`
3. Confirm deletion to the user

## Usage from `hwp-fill`

Saved templates can be referenced by name instead of by path:

```
/hwp-fill IRB content.md
```

→ Resolves to `templates/IRB.hwpx` automatically.

## Caveats

- Template names: English letters, Korean, and digits only — no special characters.
- Saving a template with an existing name must prompt for overwrite confirmation.
- Recommend adding `templates/` to `.gitignore` since forms are often personal.
