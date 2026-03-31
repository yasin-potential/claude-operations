# Global Skill Sync Commands

Sync commands for keeping `~/.claude/skills/` and `claude-operations/skills/` in sync.

## QA Skills

### operations → global
```bash
rm -rf ~/.claude/skills/qa-*
cp -r ~/Desktop/potential/projects/pipeline/claude-operations/skills/qa/_qa-fix ~/.claude/skills/qa-fix
cp -r ~/Desktop/potential/projects/pipeline/claude-operations/skills/qa/_qa-shared ~/.claude/skills/qa-shared
cp -r ~/Desktop/potential/projects/pipeline/claude-operations/skills/qa/*/qa-* ~/.claude/skills/
```

### global → operations
Place each skill in its layer directory: `data/`, `api/`, `auth/`, `inputs/`, `ui/`, `tools/` — see operations CLAUDE.md for mapping.

## Store Skills

### operations → global
```bash
rm -rf ~/.claude/skills/store-* ~/.claude/skills/_store-shared
cp -r ~/Desktop/potential/projects/pipeline/claude-operations/skills/store/_store-shared ~/.claude/skills/_store-shared
for d in ~/Desktop/potential/projects/pipeline/claude-operations/skills/store/*/; do
  name=$(basename "$d")
  [[ "$name" == "_store-shared" ]] && continue
  name="${name#_}"
  cp -r "$d" ~/.claude/skills/store-$name
done
```

### global → operations
```bash
rm -rf ~/Desktop/potential/projects/pipeline/claude-operations/skills/store/_store-shared
cp -r ~/.claude/skills/_store-shared ~/Desktop/potential/projects/pipeline/claude-operations/skills/store/_store-shared
for d in ~/.claude/skills/store-*/; do
  name=$(basename "$d")
  short="${name#store-}"
  rm -rf ~/Desktop/potential/projects/pipeline/claude-operations/skills/store/$short
  cp -r "$d" ~/Desktop/potential/projects/pipeline/claude-operations/skills/store/$short
done
```
