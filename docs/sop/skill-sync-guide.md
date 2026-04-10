# Skill Sync Guide

## Architecture

```
~/.claude/skills/          ← working copy (edit & test here)
        │
        ├─ pre-commit ──→  claude-operations/skills/  (team repo)
        │                   global → ops (auto, only existing skills)
        │
        └─ post-merge ←──  claude-operations/skills/
                            NEW skills only (interactive prompt)
```

**Core principle:** `~/.claude/skills/` is the single source of truth for content. Operations repo only stores structure for team sharing.

## Hooks

### pre-commit (commit 시)

Global에서 수정한 스킬을 operations 구조에 자동 반영 후 커밋에 포함.

- 이미 operations에 존재하는 스킬만 동기화
- `diff`로 변경된 스킬만 복사 → `git add`
- 새 스킬을 operations에 추가하려면 수동으로 디렉토리 생성 필요

### post-merge (pull 시)

팀원이 추가한 새 스킬을 감지하고 선택적으로 global에 추가.

- Global에 이미 있는 스킬은 건드리지 않음 (덮어쓰기 없음)
- 새 스킬만 목록으로 표시 → 번호/all/skip 선택

## Naming Convention

| Operations path | Global name |
|---|---|
| `qa/_qa-shared/` | `qa-shared` |
| `qa/qa-*/` | `qa-*` (as-is) |
| `store/_store-shared/` | `_store-shared` (as-is) |
| `store/_ship/` | `store-ship` |
| `store/*/` | `store-{name}` |
| `docs/*/` | `{child-name}` |
| `fullstack/*/` | `{child-name}` |
| `git-workflow/*/` | `{child-name}` |
| `prd/*/` | `{child-name}` |
| Top-level (e.g. `code-cleanup/`) | `{dir-name}` |

## First-time Setup

Hooks are in `.git/hooks/` (not tracked by git). New team members need:

```bash
# 1. Initial full sync (one-time)
bash scripts/sync-skills-to-local.sh

# Hooks are already in .git/hooks/ after clone? No — copy from teammate or recreate:
# See .git/hooks/pre-commit and .git/hooks/post-merge
```

## Adding a New Skill to Operations

When you create a new skill in global and want to share with team:

```bash
# 1. Create the directory in operations (follow group structure)
mkdir -p skills/docs/my-new-skill

# 2. Commit — pre-commit hook will auto-sync content from global
git commit -m "feat(skills): add my-new-skill"
```

## Files

| File | Tracked | Purpose |
|---|---|---|
| `scripts/skill-map.sh` | Yes | Shared mapping functions (ops ↔ global) |
| `scripts/sync-skills-to-local.sh` | No (.gitignore) | One-time full sync for first setup |
| `.git/hooks/pre-commit` | No (.git) | Global → ops before commit |
| `.git/hooks/post-merge` | No (.git) | Detect new skills after pull |
