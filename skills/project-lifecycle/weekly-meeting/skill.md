---
name: weekly-meeting
description: "Generate a branded weekly meeting agenda (markdown) + presentation (HTML) from codebase activity, prior meeting notes, and user input. Auto-collects git log, changelogs, and scope docs, then interviews the user for Slack/team inputs. Output: internal agenda doc + client-facing slides."
user-invocable: true
argument-hint: "[--project 'name'] [--week 'N']"
---

# Weekly Meeting Generator

Generate weekly client meeting materials from a project's codebase state and user-provided context. Produces two artifacts:

1. **Internal agenda** — markdown doc listing progress, decisions needed, blockers, asset requests
2. **Client presentation** — branded HTML slide deck for the meeting

---

## Workflow Overview

```
┌──────────────────────┐
│ Step 1: Auto-collect │  git log, changelogs, scope docs, prior meeting notes
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 2: Interview    │  Slack chat summary, blockers, special notes
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 3: Synthesize   │  Merge auto + user input, carry forward prior open items
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 4: Generate     │  agenda.md + presentation.html
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 5: Report       │
└──────────────────────┘
```

---

## Step 1: Auto-Collect Codebase Data

### 1.1 Parse Arguments

Extract from `$ARGUMENTS`:
- **--project**: Project name (optional — auto-detect from CWD folder name if omitted)
- **--week**: Week number (optional — auto-compute from prior meeting docs)

### 1.2 Determine Date Range

- **End date**: Today
- **Start date**: Date of the most recent prior weekly meeting doc (see 1.4), OR 7 days ago if none exists

### 1.3 Collect Git Activity

Run these commands and summarize:

```bash
git log origin/dev --since="<START_DATE>" --until="<END_DATE>" --no-merges --format="%h %s (%ad) %an" --date=short
```

Group commits by:
- **feat(...)** — new features
- **fix(...)** — bug fixes
- **refactor/chore/style** — quality improvements
- **docs** — documentation

### 1.4 Read Prior Meeting Doc (Carry-Forward)

Search for the most recent prior weekly meeting file:
- `.claude-project/docs/clients/weekly/*.md`
- `.claude-project/docs/clients/weekly-*.md`
- `.claude-project/docs/meeting-agenda-*.md`

If found, extract:
- **Open decisions** — items marked as pending/awaiting client answer
- **Pending assets** — assets still unreceived
- **Action items** — from "Next Steps" section
- **Week number** — increment by 1

These become the "carry-forward" items for this week's agenda.

### 1.5 Read Project Scope & Changelogs

Check for and read (if present):
- `.claude-project/docs/PHASE*_SCOPE.md` or `*scope*.md`
- `CLAUDE.md` — for feature table and project overview
- `.claude-project/plans/*/features/*/changelog.md` — recent feature-level changes

Extract:
- Current phase goals
- Upcoming deadlines (internal + client)
- Recently updated features

---

## Step 2: Interview User

Use AskUserQuestion to gather context the codebase can't provide. Group into minimal rounds.

**Round 1 — Team & Slack Context:**

```
Please share any of the following (paste or summarize; skip any that don't apply):

1. Slack discussions — Key decisions or blockers from the dev team channel this week
2. Client feedback — Any messages from the client since last meeting
3. Blockers — Anything delaying progress or waiting on external input
4. Special notes — Things to highlight at the meeting not obvious from commits
```

Accept free-form text input. User can paste multi-line Slack excerpts.

**Round 2 — Meeting Focus:**

```
What are the top 1-3 items you want to drive at this meeting?
(e.g., "get approval on currency system", "request tutorial assets")
```

**Round 3 — Carry-Forward Confirmation** (only if prior meeting doc found):

Show the extracted carry-forward items and ask:
```
Found the following items still open from [PRIOR_DATE] meeting:

[list carry-forward items]

Are any of these now resolved? (list numbers to remove, or "none")
```

---

## Step 3: Synthesize Content

Merge auto-collected data with user input into a structured model:

```
{
  week_number: N,
  date: YYYY-MM-DD,
  project_name: "...",
  prior_meeting_date: YYYY-MM-DD or null,

  completed_this_week: [
    { category: "feat|fix|refactor|docs", title, commits: [] }
  ],

  in_progress: [
    { title, status, blocker? }
  ],

  upcoming_next_week: [ ... ],

  decisions_needed: [  // carried from prior + new
    { id, question, recommendation, deadline, source: "carry-forward|new" }
  ],

  asset_requests: [
    { name, details, deadline, fallback }
  ],

  blockers: [ ... ],

  meeting_focus: [ "top 1-3 items" ]
}
```

---

## Step 4: Generate Artifacts

### 4.1 Output Location

Save both files under the project's `.claude-project/docs/clients/weekly/` directory.

Create the directory if it doesn't exist.

**Filenames:**
- `W{NN}-agenda-{YYYY-MM-DD}.md` — internal agenda
- `W{NN}-presentation-{YYYY-MM-DD}.html` — client slides

### 4.2 Agenda Markdown Template

```markdown
# {PROJECT} — Weekly Meeting W{NN}

**Date:** {YYYY-MM-DD}
**Covers:** {PRIOR_DATE} ~ {TODAY}

---

## 1. This Week's Progress

### Completed
{grouped by category, with commit refs}

### In Progress
{list with status and any blockers}

---

## 2. Next Week Plan

{bullet list of upcoming work}

---

## 3. Decisions Needed from Client

| # | Item | Recommendation | Deadline |
|---|------|----------------|----------|
{table rows}

{mark carry-forward items with "(carry-over from W{N-1})"}

---

## 4. Asset / Resource Requests

| # | Asset | Details | Deadline | Fallback if missed |
|---|-------|---------|----------|-------------------|
{table rows}

---

## 5. Blockers & Risks

{list}

---

## 6. Meeting Focus (Top Items)

{1-3 priority items to drive at the meeting}

---

## 7. Reference — Source Data

- Git log: `git log origin/dev --since="{START}" --until="{END}"`
- Prior meeting: {path or "none"}
- Scope doc: {path or "none"}
```

### 4.3 Presentation HTML

Generate a single self-contained HTML file. Reuse the **exact CSS framework** from `project-kickoff/skill.md` Section 4.4 (colors, fonts, slide container, nav bar, slide counter, fullscreen button, navigation JS). All styling rules, Inter font loading, navigation dots, and keyboard controls are identical.

**Brand Guidelines (same as kickoff):**

| Element | Value |
|---------|-------|
| Primary Accent | `#624DFF` |
| Dark Accent | `#4834CC` |
| Headings | `#050042` |
| Body Text | `#333333` |
| Light BG | `#f8f7ff` |
| Font | Inter (Google Fonts) |

**Slide Structure:**

| # | Slide | Content |
|---|-------|---------|
| 1 | Cover | Project name, "Weekly Meeting W{NN}", date |
| 2 | Agenda | 6-item table of contents |
| 3 | Last Week Recap | Carry-forward items resolved + open |
| 4 | This Week Completed | Grouped by category (feat/fix/etc.) |
| 5 | In Progress | Current work + status |
| 6 | Next Week Plan | Upcoming work |
| 7 | Decisions Needed | Table of CDs with recommendations |
| 8 | Asset Requests | Table with deadlines + fallback |
| 9 | Blockers & Risks | Bulleted list |
| 10 | Q&A | Q&A slide |
| 11 | Thank You | Contact info |

### 4.4 Slide Content Notes

**Slide 1 (Cover)** — use `.slide-cover` with:
```
WEEKLY MEETING
{PROJECT_NAME}
Week {NN} · {YYYY-MM-DD}
```

**Slide 3 (Last Week Recap)** — two-column layout:
- Left: "✓ Resolved" (green accent)
- Right: "→ Still Open" (orange accent, carried to this meeting)

Skip this slide entirely if no prior meeting exists.

**Slide 4 (This Week Completed)** — use `.task-card` grid. One card per category, listing key items.

**Slide 7 (Decisions Needed)** — use a styled table. Mark carry-forward items with a small badge `[W{N-1}]` in orange.

**Slide 8 (Asset Requests)** — use table with red deadline tags for urgent items (< 7 days away).

**Slides 10, 11 (Q&A, Thank You)** — identical to kickoff skill.

### 4.5 Reuse Kickoff Template

When generating the HTML, copy the complete `<style>` block, navigation `<script>`, and logo SVG from `project-kickoff/skill.md` (sections 4.4, 4.6, 4.7). Only the slide content (`<body>` inner) differs.

**Do not re-invent the CSS** — use the exact same classes (`slide`, `slide-cover`, `slide-title`, `section-number`, `task-card`, `tasks-grid`, `info-card`, `agenda-list`, `nav-bar`, `nav-dot`, `slide-counter`, `fullscreen-btn`, `slide-logo`) so the visual style matches.

---

## Step 5: Report Result

```
Weekly meeting materials generated.

Week:         W{NN}
Date:         {YYYY-MM-DD}
Project:      {PROJECT_NAME}
Covers:       {PRIOR_DATE} ~ {TODAY} ({N} commits)

Files:
  Agenda:       {agenda_path}
  Presentation: {presentation_path}

Carry-forward: {count} open items from prior meeting
Decisions:     {count} pending client answers
Assets:        {count} pending from client

Open the HTML in browser for the meeting:
  - Arrow keys: Navigate
  - F: Fullscreen
  - Ctrl+P: Save as PDF
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| No git history in range | Note "No commits this week" in agenda, still generate |
| No prior meeting doc | Skip carry-forward step, skip Slide 3 |
| No scope doc | Skip deadlines section, continue |
| User skips all interview rounds | Generate with auto-collected data only |
| `.claude-project/docs/clients/weekly/` creation fails | Fall back to `.claude-project/docs/` |

---

## Examples

### Example 1: First Weekly Meeting (no prior)

```bash
/weekly-meeting --project "Blink"
```
- Auto-detects no prior meeting doc
- Sets start date to 7 days ago
- Skips carry-forward slide
- Output: `W01-agenda-2026-04-10.md` + `W01-presentation-2026-04-10.html`

### Example 2: Ongoing Project

```bash
/weekly-meeting
```
- Auto-detects project name from CWD
- Finds prior meeting `W03-agenda-2026-04-03.md`
- Carries forward 3 open decisions + 2 pending assets
- Prompts user: "Are any of these now resolved?"
- Output: `W04-agenda-2026-04-10.md` + `W04-presentation-2026-04-10.html`

### Example 3: Override Week Number

```bash
/weekly-meeting --week 5
```
- Forces week label to W05 (useful when a week was skipped)

---

## Design Principles

1. **Auto > Manual** — scrape everything possible from codebase first, only ask for what the codebase can't tell you.
2. **Carry-forward by default** — open items from last meeting should never be forgotten.
3. **Two artifacts** — markdown is for the PM, HTML is for the client. Same data, different audiences.
4. **Consistent branding** — reuse kickoff styling so all Potential Inc client materials look like one family.
5. **One-shot generation** — no iterative back-and-forth. One interview round, then generate.
