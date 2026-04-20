---
name: daily-report
description: Generate a client-facing daily development report from dev branch commits across client projects and send via Slack
user-invocable: true
argument-hint: "[--date YYYY-MM-DD] [--dry-run] [--branch dev] [--project blink|activitycoaching|all]"
---

# Daily Report - Client-Facing Development Summary

## Purpose

Scan all projects under `~/Desktop/potential/projects/client/` for the latest `dev` branch commits, filter for client-worthy updates, and send a consolidated daily report via Slack. Designed for automated cron execution (weekdays 9 AM) but can also be invoked manually.

## Target Directory

```
~/Desktop/potential/projects/client/
├── blink/
├── activitycoaching/
└── (any future client projects)
```

The skill auto-discovers all git repositories under this directory.

## Usage

```
/daily-report                        # All client projects, yesterday, send to Slack
/daily-report --dry-run              # Preview report without sending to Slack
/daily-report --date 2026-04-01     # Report for a specific date
/daily-report --project blink        # Only report for blink project
/daily-report --branch main          # Use a different branch (default: dev)
```

### Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--date` | yesterday | Target date for the report (YYYY-MM-DD) |
| `--dry-run` | false | Preview report in console without sending to Slack |
| `--branch` | `dev` | Branch to analyze |
| `--project` | `all` | Specific project name or `all` for every client project |

## Configuration

### Slack Webhook

The skill reads the Slack Webhook URL from:
1. Environment variable: `SLACK_DAILY_REPORT_WEBHOOK`
2. Config file: `~/.claude/config/daily-report.json` → `{ "slackWebhookUrl": "https://hooks.slack.com/services/..." }`

If neither is set and `--dry-run` is not specified, the skill will error with setup instructions.

## Execution Steps

### Step 1: Discover Projects

```bash
# Find all git repos under client directory
BASE_DIR=~/Desktop/potential/projects/client
for dir in "$BASE_DIR"/*/; do
  if [ -d "$dir/.git" ]; then
    echo "$dir"
  fi
done
```

If `--project` is specified, only process that project.

### Step 2: Fetch Latest Commits (per project)

For each discovered project:

```bash
cd <project_dir>
git fetch origin <branch> 2>/dev/null

# Get commits from the target date (default: yesterday)
git log origin/<branch> --since="<date> 00:00" --until="<date> 23:59" \
  --format="%H|%an|%s|%b" --no-merges
```

- Use `--no-merges` to skip merge commits
- Collect: project name, commit hash, author, subject, body
- If the branch doesn't exist for a project, skip it silently

### Step 3: Classify Commits (Client-Facing Filter)

Analyze each commit and classify into one of these categories:

**INCLUDE (client-facing):**
- New features (`feat:`, `feature:`)
- UI/UX improvements
- Performance improvements visible to users
- New screens or pages
- API additions that enable new functionality
- Design updates

**EXCLUDE (internal-only):**
- Bug fixes we proactively found (not reported by client) — `fix:` commits for internal issues
- Refactoring (`refactor:`)
- Code cleanup, linting, formatting
- Test additions/changes (`test:`)
- CI/CD changes (`ci:`)
- Documentation changes (`docs:`)
- Dependency updates (`chore:`, `deps:`)
- Internal tooling changes
- Migration-only changes with no user-visible impact

**JUDGMENT REQUIRED:**
- Bug fixes for client-reported issues → INCLUDE (frame as "resolved issue")
- Performance fixes → INCLUDE only if user-noticeable
- Security fixes → INCLUDE (frame as "security enhancement")

When in doubt, **exclude**. The report should only contain items the client would care about.

### Step 4: Format Report

Format the report in Korean for Slack. Use Slack mrkdwn format. Group by project:

```
:rocket: *데일리 개발 리포트*
:calendar: {date} ({day of week})

---

:file_folder: *Blink*

1. *[신규 기능]* 업데이트 설명
   - 세부사항 (필요 시)

2. *[UI/UX 개선]* 업데이트 설명

:file_folder: *ActivityCoaching*

1. *[신규 기능]* 업데이트 설명

---

:chart_with_upwards_trend: *진행 현황*
- Blink: 커밋 {n}건 (공개 {m}건)
- ActivityCoaching: 커밋 {n}건 (공개 {m}건)

:speech_balloon: _문의사항이 있으시면 말씀해주세요._
```

**Category labels:** `신규 기능`, `UI/UX 개선`, `성능 개선`, `문제 해결`, `보안 강화`

**Formatting rules:**
- Each item should be 1-2 sentences, non-technical
- Avoid code jargon — describe user-visible impact
- Group related commits into a single item
- If a project has no client-facing commits, show: "내부 안정화 작업을 진행했습니다"
- If ALL projects have no client-facing commits, send a brief consolidated "내부 안정화 작업 진행" message
- Projects with zero commits for the day are omitted entirely

### Step 5: Send to Slack

Read the Slack Webhook URL from configuration (see Configuration section above).

```bash
curl -X POST -H 'Content-Type: application/json' \
  --data '{"text": "<formatted report>"}' \
  <SLACK_WEBHOOK_URL>
```

If `--dry-run`, skip this step and output the report to console only.

### Step 6: Output Summary

After execution, output:
- Projects scanned
- Commits analyzed per project
- Items included in report per project
- Slack delivery status (sent / dry-run / failed)

## Error Handling

| Error | Action |
|-------|--------|
| No Slack webhook configured | Show setup instructions, suggest `--dry-run` |
| No commits found for any project | Send "내부 안정화 작업 진행" message |
| Slack delivery failed | Output report to console as fallback, show error |
| Branch not found in a project | Skip that project silently |
| Project directory not a git repo | Skip silently |

## Slack Setup Guide

When webhook is not configured, display these instructions:

1. Go to https://api.slack.com/apps → "Create New App" → "From scratch"
2. Name: `Daily Report Bot`, select your workspace
3. Left sidebar → "Incoming Webhooks" → Toggle ON
4. "Add New Webhook to Workspace" → Select channel (or DM to yourself)
5. Copy the Webhook URL
6. Save it:
   ```bash
   # Option A: Environment variable (add to ~/.bashrc or ~/.zshrc)
   export SLACK_DAILY_REPORT_WEBHOOK="https://hooks.slack.com/services/T.../B.../xxx"

   # Option B: Config file
   mkdir -p ~/.claude/config
   echo '{"slackWebhookUrl":"https://hooks.slack.com/services/T.../B.../xxx"}' > ~/.claude/config/daily-report.json
   ```
7. Run `/daily-report --dry-run` to test
