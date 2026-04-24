---
name: weekly
description: "Generate 3 weekly client meeting artifacts from codebase + user input: (1) pre-meeting preview (D-1 share), (2) internal agenda markdown, (3) client-facing HTML slides. Auto-collects git log, carry-forward items, and prior This Week Plan commitments for delivery review. Output language auto-detects from invocation language (Korean request → Korean output, English request → English output)."
user-invocable: true
argument-hint: "[--project 'name'] [--week 'N'] [--meeting 'YYYY-MM-DD HH:MM']"
---

# Weekly Meeting Generator

Generate weekly client meeting materials from a project's codebase state and user-provided context. Produces **three artifacts**:

1. **Pre-meeting preview** — short markdown digest to share with the client ~1 day before the meeting (Slack/email-ready)
2. **Internal agenda** — markdown doc with full progress review, decisions, blockers, asset requests (PM-facing)
3. **Client presentation** — branded HTML slide deck for the meeting itself

**Output language** auto-detects from invocation context: if the user invokes this skill with a Korean prompt/context, all three artifacts render in Korean; English invocation renders in English. SKILL.md itself remains in English per repo convention.

---

## Workflow Overview

```
┌──────────────────────┐
│ Step 1: Auto-collect │  git log, prior meeting commitments, carry-forward, meeting config
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 2: Interview    │  Slack summary, R/Y/G health, meeting focus, delivery review
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 3: Synthesize   │  Build progress review with committed-vs-actual, merge user input
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 4: Generate     │  preview.md + agenda.md + presentation.html
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
- **--project**: Project name (optional — auto-detect from CWD folder name)
- **--week**: Week number (optional — auto-compute from prior meeting docs)
- **--meeting**: Meeting datetime in `YYYY-MM-DD HH:MM` format (optional — overrides config and interview)

Also detect `output_language` from invocation context: if the user's prompt or recent conversation is in Korean, set `output_language = "ko"`; default to `"en"` otherwise.

### 1.2 Determine Date Range

- **End date**: Today
- **Start date**: Date of the most recent prior weekly meeting doc (see 1.4), OR 7 days ago if none exists

### 1.3 Collect Git Activity (for Reference section only)

Run:

```bash
git log origin/dev --since="<START_DATE>" --until="<END_DATE>" --no-merges --format="%h %s (%ad) %an" --date=short
```

**Scope of use — strict:**
- The git log output populates **Agenda §7 Reference only** (commit count, contributor names, key ticket IDs, a handful of key commit hashes).
- **Do NOT** auto-synthesize `delivered[]`, `active[]`, theme labels, summaries, or bucket assignments from the commit log. The skill repeatedly misjudged `delivered` vs `active` by parsing commit subjects — the fix is to stop inferring from commits entirely. The PM writes the themes directly in Round-1 bullet 5 (§2).
- The git log is useful as **PM-facing evidence while the PM composes the themes** — they can scroll commit subjects to jog memory. It is never transformed into client-facing text by the skill.

### 1.4 Read Prior Meeting Doc

Search for the most recent prior weekly meeting:
- `.claude-project/meetings/{ProjectName}/weekly/[Weekly] *.md`

Sort by the `(YYYY-MM-DD)` suffix in the filename (descending) to pick the most recent. Ignore `[Weekly-Preview]` files and `.html` files — the internal agenda `.md` is the source of truth.

Extract from the prior `.md`:

- **This Week Plan items (from the prior meeting)** — parse the prior doc's "This Week Plan" section. Try structured table first (Item / Owner / Due columns). Fall back to bullet-list parsing for legacy docs. From the current meeting's perspective, the prior doc's "This Week Plan" describes last week's commitments; these rows populate the "Committed" column of the current Agenda §2 Progress Review committed-vs-actual table.
- **Open decisions** — rows in Decisions Needed that were not resolved
- **Pending assets** — assets not yet received
- **Week number** — increment by 1

### 1.5 Read Meeting Config

Check `.claude-project/meetings/{ProjectName}/config.json`:

```json
{
  "weekly_meeting": {
    "day_of_week": "monday",
    "time": "14:00",
    "timezone": "Asia/Seoul",
    "link": "https://meet.google.com/xxx-yyyy-zzz",
    "expected_duration_min": 30
  }
}
```

If present: compute next meeting datetime from `day_of_week` + `time` (next occurrence on or after today, in the given timezone). Use `link` and `expected_duration_min` in the Preview artifact.

If config file is missing or fields are incomplete: fall back to asking in interview Round 2 (see §2).

CLI `--meeting` argument always overrides both config and interview.

### 1.6 Read Project Scope & Changelogs

Optionally read (skip silently if not present):
- `.claude-project/docs/PHASE*_SCOPE.md` or `*scope*.md`
- `CLAUDE.md` — feature table and project overview
- `.claude-project/plans/*/features/*/changelog.md`

Extract current phase goals, upcoming deadlines (internal + client), recently updated features.

---

## Step 2: Interview User

Use AskUserQuestion to gather context the codebase can't provide. Minimize the number of rounds — batch related questions.

**Round 1 — Team & Slack Context + This Week's Themes:**

```
Please share any of the following (paste or summarize; skip any that don't apply):

1. Slack discussions — Key decisions or blockers from the dev team channel this week
2. Client feedback — Any messages from the client since last meeting
3. Blockers — Anything delaying progress or waiting on external input
4. Special notes — Things to highlight at the meeting not obvious from commits

5. **Weekly themes (REQUIRED)** — Write the 4–6 themes that moved this week. For each row give me:
   - Theme label — product-surface term from the PRD (e.g. "Admin dashboard", "Worker mobile app", "Payment & refund", "Languages + test data", "Planning", "Design"). No commit-type labels like "feat" or "fix".
   - One-sentence summary — ≤ 20 words, your own words, plain language. Describe holistically — the theme's state and progression, not a single commit.
   - Bucket — `delivered` if a PRD-scope milestone closed this week (PRD finalized, design handed off, a contract signed — one-shot deliverables). `active` for everything else that progressed but didn't fully close. When in doubt, pick `active`.

   Example:
     Theme: Payment & refund | Bucket: active | Summary: Admin-side workflow wired end-to-end; worker-side deposit flow still ahead
     Theme: Planning         | Bucket: delivered | Summary: Final PRD v1.4 delivered; 3-role scope confirmed
```

The git log (§1.3) is collected for Agenda §7 Reference only — the PM uses it to jog memory while writing the themes. The skill does NOT auto-generate themes, summaries, or buckets from commits. Previous versions of this skill did and got `delivered` vs `active` wrong enough times that we moved to PM-authored input.

**Round 2 — Meeting Setup & Health:**

Ask these together in one round:

1. **Meeting datetime** — only if config missing/incomplete AND `--meeting` arg not provided.
   Prompt: `"Meeting date/time (YYYY-MM-DD HH:MM) and link if any. Example: 2026-04-21 14:00, https://meet.google.com/xxx"`
2. **Project Health** — one of: `green` (on track), `yellow` (at risk but manageable), `red` (off track, intervention needed). Plus one-line note explaining why.

We no longer ask for "Meeting Focus" — the slide sequence (Summary → This Week → Decisions → Assets → Discussion → Blockers) itself IS the agenda. A separate forward-looking focus statement duplicated that work for no reader gain.

**Round 3 — Delivery Review** (only if prior meeting's This Week Plan items were extracted in §1.4):

Show each committed item and ask for delivery status:

```
Last week we committed to the following items. What's the delivery status of each?

[for each item from prior This Week Plan]
{item} — status? (done / in_progress / missed / descoped) + optional note
```

This populates the Progress Review table's "Actual" and "Status" columns.

**Round 4 — Carry-Forward Confirmation** (only if prior meeting has open decisions or pending assets):

```
Found the following items still open from {PRIOR_DATE} meeting:

[list carry-forward items]

Are any of these now resolved? (list numbers to remove, or "none")
```

---

## Step 3: Synthesize Content

Merge auto-collected data with user input into a structured model:

```
{
  week_number: N,
  date: YYYY-MM-DD,                      // today
  meeting_datetime: "YYYY-MM-DD HH:MM",  // from config / CLI / interview
  meeting_link: "..." or null,
  expected_duration_min: 30,             // from config or default
  project_name: "...",
  prior_meeting_date: YYYY-MM-DD or null,
  output_language: "ko" | "en",          // auto-detected from invocation

  health: {
    status: "green" | "yellow" | "red",
    note: "one-line explanation"
  },

  progress_review: [                     // merged last-week commitments + this-week actuals
    {
      committed: "text from prior This Week Plan",
      actual: "what was delivered / current state",
      status: "done" | "in_progress" | "missed" | "descoped",
      commits: []                        // optional commit refs
    }
  ],

  // `delivered` and `active` are populated EXCLUSIVELY from Round-1 bullet 5 (PM input).
  // Do NOT cluster commits and generate these arrays automatically — the skill historically
  // got the bucket wrong by parsing commit subjects (see §1.3 rationale).

  delivered: [                           // ONE-SHOT milestones that closed this week — no status column needed
    {
      theme: "product-surface label from PRD (PM-authored)",
      summary: "PM's one-sentence summary (≤ 20 words, plain language, no ticket IDs)"
    }
  ],

  active: [                              // ONGOING themes with progress this week — default bucket
    {
      theme: "product-surface label (PM-authored)",
      summary: "PM's summary of this week's progress (≤ 20 words, describe holistically)"
    }
  ],

  // -------------------------------------------------------
  // BUCKET RULES — the PM picks the bucket in Round-1 bullet 5. The skill only renders.
  // Rules, shown here so the PM knows what to pick:
  //
  //   `delivered` — a one-shot milestone closed this week with a clear finish line
  //                 (PRD finalized, design handed off, a contract signed). Evidence
  //                 of full PRD-scope closure for the theme.
  //
  //   `active`    — default for ongoing development. Use when PRD scope is larger
  //                 than what shipped this week. When in doubt, pick `active`.
  //
  // Anti-patterns the PM should avoid:
  //   - "A page was fixed" → `delivered`. No — that closes one page, not the theme.
  //   - "Admin-side wired end-to-end" → `delivered`. No — that's half the theme.
  //   - "First language locale done" → `delivered`. No — other locales still scoped.
  //
  // Aim for 4–6 themes total across both buckets.

  this_week_plan: [                      // every row MUST have owner + due
    { item, owner, due }
  ],

  decisions_needed: [
    { id, question, recommendation, deadline, source: "carry-forward" | "new" }
  ],

  asset_requests: [
    { name, details, deadline, fallback }
  ],

  discussion_items: [                     // proposals / positions we want client alignment on at the meeting (not a yes/no decision, not a deliverable request)
    {
      topic: "short label, e.g. 'Languages'",
      points: [ "bullet 1", "bullet 2" ],
      notes: [ "optional caveats — e.g. 'AI-translation only; quality review not feasible'" ]
    }
  ],

  blockers: [
    { item, severity: "red" | "yellow", impact }
  ]
}
```

### 3.1 Client-Facing Writing Rules (applies to Preview + Slides; partially to Agenda body)

The client is non-technical. PRD terminology — not internal engineering shorthand — is the **only acceptable vocabulary** in client-facing artifacts. Before writing any client-facing text, grep `prd.md` / `CLAUDE.md` / `.claude-project/docs/` for the domain's canonical term and use THAT.

**Hard bans in Preview `.md` and the HTML slide deck:**

| Banned | Replace with |
|---|---|
| Ticket IDs (`FSP-067`, `FSP-067 ~ FSP-082`) | plain-language description of the work |
| Commit hashes (`ce8e804`) | plain-language description; commits stay in Agenda §Reference only |
| Tech acronyms unless universally known (`SMTP`, `IAM`, `i18n`, `CDN`, `PG`, `HTML prototype`, `API integration`) | PRD's term or a plain phrase — `SMTP` → "outbound email service"; `IAM access` → "team access to our cloud account"; `i18n` → "multi-language support"; `HTML prototype` → "approved designs"; `API integration` → "data connections" or drop the word |
| Engineering verbs (`wire`, `scaffold`, `rebuild`, `refactor`, `seed`, `integrate`) | user-visible verbs — `wire end-to-end` → "connect all the steps"; `seed 20 workers` → "load sample data for testing" |
| Jira / sprint / phase labels (`Phase 1`, `Sprint 3`, `v1.4`) in body text | describe by what is being built, not by internal status |

**Milestone line — strict format (≤ 20 words, one sentence, schedule-focused):**

Template: `{where we are now} — {next gate with date}, {launch target with date}`

Good: *"Development underway — testing begins next week, launch targeted late May."*
Bad: *"6-week MVP build under PRD v1.4 + 2026-04-15 scope override — 3 merged roles, 4 languages, manual bank transfer. Mid-implementation, heading into QA entry."*

If the scope docs don't give a launch date, derive from PRD timeline (e.g. "6-week MVP" + PRD version date). If no date anywhere, just the current phase + next gate.

**Table description cells — ≤ 20 words, plain language:**

Every "Details", "Recommendation", "Deliverable", and "Impact" cell in Preview / Slides must:
- Lead with a concrete noun or verb the client recognizes
- Fit on one line at 1920×1080 without wrapping (< 20 words is the safe rule)
- Avoid nested acronyms, stacked clauses, or "so that" explanations of what the team will do

Bad: *"Confirm required fields per category so intake forms can be designed"*
Good: *"Which fields should the Flight / Bus / Admin Agent application forms collect?"*

Bad: *"Root account created; IAM access for our team"*
Good: *"AWS account set up, with access shared to our team"*

**Summary theme labels — client-recognizable product surfaces:**

Use product-surface categories (what the client sees in the product), not engineering categories:
- `Admin UI` → `Admin dashboard`
- `Worker Mobile` → `Worker mobile app`
- `Backend` → `Platform services` or name the visible feature ("Payment & refund tracking")
- `i18n + Seed` → `Languages + test data`
- `Planning` / `Design` → keep as-is

**Language follows `output_language`:**

All the rules above apply to the rendered language. If `output_language != "en"`, use the canonical domain terms from the PRD for that locale. Never mix languages within a single artifact.

**Time-axis labels — disambiguate Summary (past) from Plan (future):**

The Summary section recaps the past 7 days; the This Week Plan section commits to the next 7 days. The English template historically used "Delivered this week" / "Active this week" for Summary AND "This Week Plan" for the forward section — which read fine in English but caused real confusion in locales where a single word covers both the just-past week and the just-starting week on a Monday-morning meeting. Render the headings so the time axis is unambiguous in BOTH languages:

| Section | English heading | Localization requirement |
|---|---|---|
| Summary → delivered bucket | `Last week — Delivered` | Heading MUST reference the prior 7 days |
| Summary → active bucket | `Last week — In progress` | Heading MUST reference the prior 7 days |
| This Week Plan | `This Week Plan` | Heading references the NEXT 7 days |

The data model field names (`delivered[]`, `active[]`) are unchanged — only the rendered headings shift to past-tense framing for Summary. The Plan stays future-tense. Localized renderings must preserve the past/future distinction: if the target locale uses the same word for "last week" and "this week", pick distinct time-axis words for the two sections and keep them stable across the Agenda markdown, slide HTML, and any Preview copy-paste.

**Agenda `.md` has looser rules:** the PM is the audience. Ticket IDs and commit hashes are allowed in the Reference column or the §7 Source Data section for traceability. Body text should still be plain-language where possible — the PM copies blocks of the Agenda into the Slides later.

---

**Classifying client-facing items — pick ONE bucket per row, never duplicate across:**

| Bucket | When to use | Example |
|---|---|---|
| `decisions_needed` | A specific question with a deadline where the client must give us a yes/no or a pick. | "Pick the service name." · "Which data retention period (1yr / 3yr / 5yr)?" |
| `asset_requests` | A deliverable the client must hand over (file, account, credential, signed doc). | "Logo file (SVG)." · "AWS root account." · "Legal-reviewed privacy policy." |
| `discussion_items` | A position, proposal, or scope change we want client alignment on — not a yes/no. Often has sub-bullets and caveats. | "We propose KR+EN+RU+VN as base language set (+1 optional). AI-translation; quality review not feasible." · "Proposed affiliation-approval flow: manual by POC, ops admin visibility, unregistered → text input." |

When an item fits more than one bucket, put it where the client experience is clearest. If the same language scope appears in `decisions_needed` as "pick a locale" AND in `discussion_items` as "here's our proposal," remove the decisions_needed row — the discussion already frames it.

---

## Step 4: Generate Artifacts

### 4.1 Output Location & Filenames

All artifacts are saved under `.claude-project/meetings/{ProjectName}/weekly/`. Create the directory if it doesn't exist.

| Artifact | Filename | PDF? |
|---|---|---|
| Pre-meeting preview (D-1 Slack share) | `[Weekly-Preview] {Project} ({YYYY-MM-DD}).md` | **No** — Slack-native mrkdwn, rendered directly in Slack. A PDF would be a lossy copy. |
| Internal agenda | `[Weekly] {Project} ({YYYY-MM-DD}).md` | **No** — PM edits it during/after the meeting, stays in Markdown. |
| Client slides | `[Weekly] {Project} ({YYYY-MM-DD}).html` | **Yes** — also emit `[Weekly] {Project} ({YYYY-MM-DD}).pdf` (same base name, `.pdf`). Clients who can't run the HTML (email, offline) still get the deck. |

`{YYYY-MM-DD}` is the **meeting date** (from `meeting_datetime` when available; otherwise today). The week number `W{NN}` is rendered inside the document content, not in the filename.

**PDF generation — HTML only.** After writing the three source files, run a headless-browser PDF export on the slide `.html` *only*. Do NOT run `md-to-pdf` on the preview or agenda `.md` files. Canonical command on macOS:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf-no-header \
  --virtual-time-budget=10000 \
  --print-to-pdf="[Weekly] {Project} ({YYYY-MM-DD}).pdf" \
  "file:///<absolute-path>/[Weekly] {Project} ({YYYY-MM-DD}).html"
```

Fallbacks if Chrome is not installed: try `/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge`, then `chromium`, then `wkhtmltopdf`. The HTML's `@media print` block forces the light palette, hides chrome controls, and page-breaks between slides — do not alter those rules in the generated HTML.

**Rationale:** The Preview's value is in Slack's live rendering (`*bold*`, emoji, unfurling). Flattening it to PDF strips that and leaves a 140KB file no one opens. The Agenda stays editable so the PM can annotate in place. Only the slides deserve a PDF because clients present/archive them.

### 4.2 Preview Markdown Template (Slack-optimized, action-only)

The Preview is **a D-1 Slack heads-up — NOT a mini-deck.** Its single job is to give the client the list of things they need to **prep or think about before** the meeting. Everything else (last-week review, agenda, blockers, KPIs) belongs in the slides, not here. A client reading the Preview should see "I need to give answers on 4 decisions, line up 7 deliverables, and think about 2 discussion topics" — that's it.

The file is designed to be pasted directly into Slack. Slack mrkdwn ≠ CommonMark, so use Slack's dialect.

Render in `output_language` (auto-detected). Translate labels and keep prose conversational.

```
👋 Hi team — tomorrow's weekly at {YYYY-MM-DD HH:MM} {timezone} ({meeting_link or "link TBD"}).

Last week's update and this week's plan will be walked through at the meeting. Before then, please review the items that need your input:


📌 Decisions needed ({N})

{Group decisions by deadline, earliest first. For each deadline group:}
Due {M/D} — {count} item{s}:
{for each decision, numbered with GLOBAL index:}
{n}. {question} — {short recommendation, ≤ 12 words}


📦 Asset requests ({N})

{Group assets by deadline, earliest first. For each deadline group:}
Due {M/D}:
{for each asset, bullet:}
• {name}


💬 Discussion items ({N})

{for each discussion_item, one line each:}
{n}. {topic} ({1-phrase summary of what we're proposing, ≤ 10 words})


See you tomorrow 🙏
```

**What's explicitly NOT in the Preview:**
- No Agenda list (the slide deck IS the agenda)
- No "Last week review" bullets (walked through at the meeting, or covered in the .pdf if client opens it)
- No Blockers & risks / no Q&A (meeting-only content)
- No fallback hints on assets (contingency talk happens at the meeting)
- No discussion notes/caveats (those are for the meeting discussion)
- No health status or milestone (client doesn't need this at D-1)

**Length target: under 1000 characters.** If the Preview exceeds 1000 chars, cut detail from recommendations/summaries — never drop an entire row. The client reads this on mobile Slack; past 1 screen they stop scrolling and miss the CTAs.

**Asset list: just the name, no details, no fallback.** The client knows what a "logo file" is. If clarification is needed (e.g. the Cloud hosting asset needs "access for our team"), add a short parenthetical — but asset rows should fit on one mobile line each.

**Discussion items: one line each.** The full bullets and notes live on the slide; the Preview tells the client the topic exists and invites them to pre-think about it.

**Slack mrkdwn rules (critical — do NOT use CommonMark syntax):**

**ZERO `*` and ZERO `_` in the Preview file.** The raw `.md` is opened by the PM in an IDE where asterisks and underscores are visual noise. Emoji carries hierarchy; no bold/italic markers needed anywhere.

**Section headers use a leading emoji only — no bold wrapping.**

Topic → emoji mapping (stable, use these exactly):

| Block | Emoji | Example header |
|---|---|---|
| Decisions needed | 📌 | `📌 Decisions needed (4)` |
| Asset requests | 📦 | `📦 Asset requests (7)` |
| Discussion items | 💬 | `💬 Discussion items (2)` |

Slack will render the emoji + trailing text inline; no formatting markers required. Bullets (`•`) and numbered lists (`1.`) carry sub-structure. Blank lines separate blocks.

**Deadline sub-headers:** plain text, no markers — `Due {M/D} — {N} items:` (trailing colon) immediately followed by the list.

**Asset lines:** bullet + name only. If clarification is essential (e.g. "access for our team"), inline parens. Never any `*` / `_` / fallback detail.

**Discussion items:** one line each, `{n}. {topic} ({short summary})`. No sub-bullets, no Notes block.

| Do | Don't | Why |
|---|---|---|
| Emoji-prefix section headers (`📌 Decisions needed (N)`) | `*Decisions needed*` or `*Section*` with asterisk wrapping | Asterisks in the raw `.md` hurt readability for the PM; Slack renders emoji + plain text fine |
| Plain text everywhere (dates, item names, deadlines, recommendations) | `*bold*` anywhere in the Preview | Zero-bold policy. No exceptions for emphasis. |
| Drop italics entirely (`_..._` → plain) | `_italic_` anywhere | Italic adds `_` noise without Slack signal gain in an action-only message |
| Emoji + `*bold*` as section labels | `#` / `##` / `###` headers | Slack does not render Markdown headers — they show as literal `#` characters |
| `>` blockquote for meeting-meta line AND the "please review" CTA | Plain text with extra asterisks | Slack renders `>` as a left-bar callout — the Slack-native way to emphasize a single invitation block |
| Single blank line between sections | Double blank lines, or `---` horizontal rules | Slack collapses multi-blank and renders `---` as literal text |
| `•` bullets (or `-`) with 2-space indent for nesting | GFM task lists `- [ ]` | Slack does not render checkboxes in plain messages |
| Inline separator `·` (middle dot) for meta info on one line | Multiple lines for short meta | Keeps meta scannable without eating vertical space |
| Dates as `M/D` (e.g. `4/18`) in body, full `YYYY-MM-DD` only in the meta line | Repeating full ISO dates inline | Verbose in running text |
| Deadline grouping: italic subheader `_By *{M/D}* · {N} items_` with items listed beneath | Per-item `· by *{M/D}*` tails on every line | Repeating the deadline on every line is visual noise, wraps awkwardly on long items, and buries urgency. Grouping lets the reader scan "what's due by when" at a glance |
| Numbered list for Decisions (ordered, client references "item 3") | Bullets for Decisions | Clients scan by number at the meeting |
| Bulleted list for Assets (flat scan) | Numbered for Assets | Order rarely matters; scanning is the job |

**Content rules:**
- **Summary section is always rendered when `delivered` OR `active` OR `progress_review` has at least one row.** Only omit if all three are empty.
- Skip empty subsections entirely (e.g., omit "Asset requests" block if the list is empty, and drop the `(N)` from agenda item 4).
- Keep each decision/asset line **scannable on one screen-width** — one line per item if possible. Wrap long recommendations by trimming, not by line-breaking mid-sentence.
- Do not include blockers detail, internal metrics, health status, or full progress text. Those stay in the internal agenda. The Preview is the *invitation*, not the meeting.
- Opening emoji (👋) and closing emoji (🙏) are part of the voice — keep them. They set a warm tone that a plain meeting notice lacks.

**Why this matters:** Previous versions of this template used CommonMark (`##` headers, `---` rules, `**bold**`). When pasted into Slack, those rendered as literal syntax characters, making the message look unpolished to the client. This template is the fix.

### 4.3 Internal Agenda Markdown Template

6 sections, PM-facing, contains full detail. Render in `output_language`.

```markdown
# {PROJECT} — Weekly Meeting W{NN}

**Date:** {YYYY-MM-DD}
**Covers:** {PRIOR_DATE} ~ {TODAY}
**Health:** {status badge} {health.status} — {health.note}

---

## 1. Summary

- **Health:** {🟢 | 🟡 | 🔴} {note}
- **Last week — Delivered:**
{for each `delivered[]` entry (omit the bullet entirely if delivered is empty):}
  - *{theme}* — {summary}
- **Last week — In progress:**
{for each `active[]` entry:}
  - *{theme}* — {summary}

The weekly Summary is **retrospective only** and splits into TWO buckets:
- *Delivered* = one-shot milestones that closed last week (PRD finalized, design handed off, etc.). Empty-is-OK — some weeks just don't close a milestone.
- *In progress* = ongoing themes that progressed last week. Default for most rows. These are never "done" mid-project, so no status label is needed — their presence in the list = "we progressed this here".

Time-axis discipline: the Summary's two buckets describe the **past** week. The "This Week Plan" section in §3 describes the **next** week. Never label Summary buckets with "this week" alone — see §3.1 Time-axis labels.

No status column, no `done/in_progress` labels. The two buckets carry that information by where an item is placed.

Project-level milestones belong in the kickoff deck; the meeting agenda is in the Preview. Do not add a Meeting Focus, Milestone, or forward-looking list here.

---

## 2. Progress Review

{If progress_review has rows — committed-vs-actual table from the prior meeting's This Week Plan:}

| # | Committed (from W{N-1}) | Actual | Status |
|---|-------------------------|--------|--------|
{rows; Status column uses ✓ done / → in progress / ✗ missed / ~ descoped}

### Last week — Delivered

{If delivered[] has rows:}

| # | Theme | What closed | Commits |
|---|-------|-------------|---------|
{for each delivered[] row, with commit refs as inline code}

### Last week — In progress

| # | Theme | What progressed | Commits |
|---|-------|-----------------|---------|
{for each active[] row, with commit refs as inline code}

*NO status column on the Delivered/In-progress sub-tables — placement in the section IS the status signal. Commits column here is Agenda-only (PM reference); client-facing slide drops it.*

---

## 3. This Week Plan

| # | Item | Owner | Due |
|---|------|-------|-----|
{rows — every cell required}

---

## 4. Decisions & Assets (Client Action Needed)

### Decisions Needed

| # | Item | Recommendation | Deadline |
|---|------|----------------|----------|
{rows; mark carry-forward rows with "(carry-over from W{N-1})"}

### Asset / Resource Requests

| # | Asset | Details | Deadline | Fallback if missed |
|---|-------|---------|----------|--------------------|
{rows}

---

## 5. Discussion Items

{for each discussion_item — render each as a numbered subsection:}

### 5.{i}. {topic}

- {point 1}
- {point 2}
...

{if notes:}

_Notes:_
- _{note 1}_
- _{note 2}_

*If discussion_items is empty, omit Section 5 entirely and renumber Blockers → 5, Reference → 6.*

---

## 6. Blockers & Risks

| Severity | Item | Impact |
|----------|------|--------|
{rows — severity rendered as 🔴 / 🟡}

---

## 7. Reference — Source Data

- Git log: `git log origin/dev --since="{START}" --until="{END}"`
- Prior meeting: {path or "none"}
- Scope doc: {path or "none"}
- Meeting config: {path or "none"}
```

### 4.4 Presentation HTML — Slide Structure

9 slides max. Reuse the **exact CSS framework** from [kickoff/SKILL.md](../kickoff/SKILL.md) §4.3 (tokens) + §4.4 (CSS) + §4.6 (JS) + §4.7 (logo SVG). All theme tokens, slide container rules, navigation, keyboard shortcuts, responsive breakpoints, reduced-motion handling, and light/dark toggle live in the kickoff skill — copy them verbatim.

| # | Slide | Content |
|---|-------|---------|
| 1 | Cover | `WEEKLY MEETING` / {PROJECT_NAME} / `Week {NN} · {YYYY-MM-DD}` |
| 2 | Summary | Health badge (🟢/🟡/🔴) + **two themed tables** with past-tense headings: "Last week — Delivered" (one-shot milestones closed) and "Last week — In progress" (ongoing themes that progressed). Localized renderings must keep past-tense framing — see §3.1 Time-axis labels. No Status column, no milestone, no meeting focus. Summary IS the last-week slide — there is no separate Last Week Review slide. |
| 3 | This Week Plan | Table: Item / Owner / Due. Forward-looking — describes the NEXT 7 days, not the week just passed. |
| 4 | Decisions Needed | Styled table; carry-forward rows show `[W{N-1}]` badge |
| 5 | Asset Requests | Table with deadlines (< 7 days rendered in red), fallback column |
| 6 | Discussion Items | Card-per-topic layout: topic title + bullet points + optional notes/caveats. Omit slide if `discussion_items` is empty. |
| 7 | Blockers & Risks | Severity badge + item + impact |
| 8 | Q&A | Q&A slide (identical to kickoff) |
| 9 | Thank You | Contact info (identical to kickoff) |

### 4.5 Slide Content Notes

**Brand tokens:** use the canonical `var(--…)` set from [kickoff/SKILL.md §4.3](../kickoff/SKILL.md). Do not hand-write hex values. Both `[data-theme="light"]` and `[data-theme="dark"]` variants must be emitted. Honor `prefers-color-scheme` on first load.

**Status color tokens used by weekly-specific slides:**
- Done / Green health → `var(--ok)` (`#10B981`)
- In progress / Yellow health / carry-forward badge → `var(--warn)` (`#F59E0B`)
- Missed / Red health / urgent deadline (< 7 days) → `var(--err)` (`#EF4444`)

**Slide 1 (Cover)** — use `.slide-cover`:
```
WEEKLY MEETING
{PROJECT_NAME}
Week {NN} · {YYYY-MM-DD}
```

**Slide 2 (Summary)** — retrospective only. Layout:
- Row 1: Health badge + one-line note
- Row 2: subheading `Last week — Delivered` + small table (Theme / What closed) — 1–2 rows typical, omit whole block if `delivered` is empty
- Row 3: subheading `Last week — In progress` + small table (Theme / What progressed) — 3–5 rows

**No Status column anywhere.** The bucket is the status — Delivered means closed last week, In-progress means progressed last week. Don't add `done`/`in progress` badges; they're redundant and — historically — easily misapplied.

**Never claim Delivered without PRD-scope closure.** A fixed page, a wired admin flow, or a single-language i18n pass is NOT Delivered. If unsure, put it in `active[]`. See §3 synthesis rules.

**Headings must name the time axis.** Summary buckets = past week. Plan section = next week. Never label Summary as "This week" alone — that collides with the Plan slide and breaks in locales where a single word covers both windows. See §3.1 Time-axis labels for the canonical heading set.

**Do NOT** render a milestone line, meeting-focus list, or any prose sentence here. Plain-language theme labels only; no ticket IDs or commit hashes on this slide (those stay in Agenda §Reference).

**Slide 3 (This Week Plan)** — table with Item / Owner / Due columns. Owner column may use a name pill.

**Slide 4 (Decisions Needed)** — styled table. Carry-forward rows: add a small `[W{N-1}]` badge with `var(--warn)` background next to the item.

**Slide 5 (Asset Requests)** — deadline cell rendered in `var(--err)` text when the deadline is within 7 days.

**Slide 6 (Discussion Items)** — card-grid layout, one card per topic. Each card:
- Topic title (`<h3>`, colored with `var(--accent)`)
- Bullet list of points (may nest one level for sub-caveats)
- If `notes[]` present, render as a muted italic `Notes:` block with its own bullets at the bottom of the card, visually distinct (`var(--muted)` color, `var(--bg)` background with a thin left border in `var(--warn)`)

Two cards → side-by-side on ≥1366px viewports, stacked below. Three or more → auto-fill grid with `minmax(360px, 1fr)` columns. Omit the slide entirely when `discussion_items` is empty.

**Slide 7 (Blockers & Risks)** — each row shows a severity pill (🔴 / 🟡) followed by item and impact.

**Slides 8, 9 (Q&A, Thank You)** — identical to kickoff skill §4.5.

### 4.6 Reuse Kickoff Template

When generating the HTML, copy the complete `<style>` block, both `<script>` IIFEs, and the logo SVG from [kickoff/SKILL.md](../kickoff/SKILL.md) §4.3 + §4.4 + §4.6 + §4.7. Only the slide content (`<body>` inner) differs.

**Do not re-invent the CSS.** Use the exact same classes (`slide`, `slide-cover`, `slide-title`, `section-number`, `task-card`, `tasks-grid`, `info-card`, `agenda-list`, `nav-bar`, `nav-dot`, `slide-counter`, `chrome-btn`, `theme-toggle`, `fullscreen-btn`, `slide-logo`) so visual style and theme behavior match across all client deliverables.

**Include the chrome markup** — copy the `<button class="chrome-btn theme-toggle">` + `<button class="chrome-btn fullscreen-btn">` + `<nav class="nav-bar">` + `<div class="slide-counter">` block from kickoff §4.5 verbatim. Nav dots auto-populate from `slides.length` — don't hand-write them.

### 4.7 Pre-delivery Checklist

Run the full 13-point checklist from [kickoff/SKILL.md §4.8](../kickoff/SKILL.md) before Step 5 reporting. Any HIGH fail blocks delivery.

**Weekly-specific additions:**

| # | Check | Severity |
|---|---|---|
| W-1 | Summary slide renders Health badge (correct color token: green=`--ok`, yellow=`--warn`, red=`--err`) + one-line health note + TWO sub-sections with past-tense headings: `Last week — Delivered` (may be empty-omitted) and `Last week — In progress`. NEVER "Active this week" / "Delivered this week" (collides with the This Week Plan slide; see §3.1 Time-axis labels for localized variants). NO Status column, NO milestone, NO meeting-focus list, NO prose. | HIGH |
| W-2 | Summary slide's tables: Theme pill + What-shipped/What-progressed text. No Status badges, no `done`/`in progress` labels — the section header carries the bucket semantics. There is NO separate "Last Week Review" slide. | HIGH |
| W-3 | This Week Plan table: every row has non-empty Owner and Due cells | HIGH |
| W-4 | Decisions Needed: every row has recommendation + deadline; carry-forward rows show `[W{N-1}]` badge with `var(--warn)` background | HIGH |
| W-5 | Asset Requests: rows with deadline < 7 days render the deadline cell in `var(--err)` text | HIGH |
| W-6 | Summary slide's `Last week — In progress` section is populated (≥1 row) whenever development happened last week. `Last week — Delivered` section renders only if `delivered[]` is non-empty (empty is common — don't fake it). Never claim Delivered without evidence of full PRD-scope closure for that theme. | MEDIUM |
| W-7 | Preview `.md` is action-only: opening line + 3 action blocks (Decisions, Assets, Discussion) + sign-off. **Explicitly absent**: Agenda list, Last-week bullets, Blockers, Health, Milestone, asset fallbacks, discussion notes. **ZERO `*` and ZERO `_` in the entire file.** Section headers use emoji-prefix (📌 / 📦 / 💬) — no bold wrapping. Total length under 1000 chars. | HIGH |
| W-8 | Preview `.md` and Internal agenda `.md` are both rendered in the same `output_language` (no language mixing) | HIGH |
| W-9 | Commit references (`abc1234`) are styled as `<code>` with monospace font and `var(--bg-soft)` background | LOW |
| W-10 | The output directory contains exactly ONE `.pdf` file, matching the slide `.html` base name. No `[Weekly-Preview] *.pdf` or separate agenda `.pdf` is emitted. | HIGH |
| W-11 | If `discussion_items` is non-empty: Slide 6, Preview `💬 Discussion items` section, and Agenda §5 all render. Each topic card has title + ≥1 point. `notes[]` (if any) render as a visually distinct muted/italic block, not mixed in with `points[]`. | HIGH |
| W-12 | No item appears in more than one of `decisions_needed` / `asset_requests` / `discussion_items`. Dedupe at synthesis time — a language decision covered in a Discussion Item must be removed from Decisions. | HIGH |
| W-13 | Preview `.md` and slide `.html` contain ZERO ticket IDs (e.g. `FSP-067`) and ZERO commit hashes (e.g. `ce8e804`). These belong only in the Agenda `.md` §Reference section. | HIGH |
| W-14 | Each `delivered[i]` / `active[i]` summary is ≤ 20 words, names a concrete product-surface deliverable (not "60 commits", not a ticket ID). Themes use PRD vocabulary (Admin dashboard, Worker mobile app, Payment & refund, etc.), not commit-type labels (feat/fix). | HIGH |
| W-15 | Every table description/details/recommendation/impact cell in Preview + Slides is ≤ 20 words, uses PRD terminology (grep'd from `prd.md`/`CLAUDE.md`), and contains no banned acronyms from §3.1. | HIGH |
| W-16 | Summary theme labels are product-surface terms (what the client sees — "Admin dashboard", "Worker mobile app"), not engineering labels ("Admin UI", "Worker Mobile", "Backend"). | MEDIUM |
| W-17 | `delivered[]` and `active[]` are populated from Round-1 bullet 5 (PM input). The skill MUST NOT auto-generate them by clustering commits. Commits appear only in Agenda §7 Reference (count, authors, ticket IDs, a handful of key hashes) — never transformed into theme summaries. | HIGH |
| W-18 | Summary section headings use past-tense framing (`Last week — Delivered` / `Last week — In progress`). Plan section uses forward-tense (`This Week Plan`). No artifact labels Summary as "this week" alone — it collides with the Plan section and breaks in locales where a single word covers both windows. Applies to Agenda `.md`, slide HTML, and any copy-paste into the Preview. | HIGH |

---

## Step 5: Report Result

```
Weekly meeting materials generated.

Week:          W{NN}
Meeting:       {meeting_datetime}  ({meeting_link or "no link"})
Project:       {PROJECT_NAME}
Health:        {🟢|🟡|🔴} {note}
Covers:        {PRIOR_DATE} ~ {TODAY}  ({N} commits)
Delivery:      {M}/{T} last-week commitments delivered

Files:
  Preview (Slack):   {preview_path}       ← .md only, paste into Slack
  Agenda (PM):       {agenda_path}        ← .md only, edit during meeting
  Slides (HTML):     {presentation_path}  ← open in browser for meeting
  Slides (PDF):      {presentation_pdf}   ← archival / email fallback

Carry-forward: {count} open items from prior meeting
Decisions:     {count} pending client answers
Assets:        {count} pending from client
Blockers:      {count} (🔴{red_count} 🟡{yellow_count})

Workflow:
  D-1: paste Preview.md body directly into Slack (Slack mrkdwn renders it live)
  D-0: open Presentation.html for the meeting (F = fullscreen, T = theme); share .pdf for offline clients
  Post-meeting: edit Agenda.md in place with notes and decisions taken
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| No git history in range | Note "No commits this week" in agenda, still generate all 3 artifacts |
| No prior meeting doc | `progress_review = []`. `delivered[]` and `active[]` still come from PM input in Round-1 bullet 5. Summary renders normally from those arrays. §2 Progress Review skips the committed-vs-actual table and shows only the `Last week — Delivered` + `Last week — In progress` sub-tables. |
| No scope doc | Skip milestone line in Summary |
| No config AND no `--meeting` AND user skips Round 2 meeting-time prompt | Use "TBD" placeholder in Preview; warn in Step 5 report |
| User skips all interview rounds | Generate with auto-collected data only; health defaults to `yellow` with note "status not provided" |
| `.claude-project/meetings/{ProjectName}/weekly/` creation fails | Fall back to `.claude-project/meetings/` |

---

## Examples

### Example 1: First Weekly Meeting (no prior)

```bash
/weekly --project "Blink" --meeting "2026-04-21 14:00"
```
- No prior meeting detected → `progress_review = []`. PM fills Round-1 bullet 5 with 4–6 themes (each with label + summary + bucket).
- Summary slide renders Health + `Last week — Delivered` table (1–2 rows) + `Last week — In progress` table (3–5 rows). No Status column.
- Preview `.md` skips the last-week enumeration — only Decisions + Assets + Discussion blocks.
- Start date = 7 days ago
- Output:
  - `[Weekly-Preview] Blink (2026-04-21).md`
  - `[Weekly] Blink (2026-04-21).md`
  - `[Weekly] Blink (2026-04-21).html` + `.pdf`

### Example 2: Ongoing Project with Config

```bash
/weekly
```
- Auto-detects project name from CWD
- Reads `config.json` → next meeting Monday 14:00
- Finds prior meeting `[Weekly] Blink (2026-04-14).md`
- Extracts last week's This Week Plan → asks delivery status per item in Round 3
- Carries forward 3 open decisions + 2 pending assets, confirms resolution in Round 4
- Outputs 3 files dated with next Monday

### Example 3: Korean Output

When the user invokes `/weekly` with a Korean prompt or context, the skill detects the language and renders all three artifacts (Preview, Agenda, Presentation slides) in Korean. No additional flag required. SKILL.md itself remains English.

### Example 4: Override Week Number

```bash
/weekly --week 5
```
- Forces the week label to W05 (useful when a week was skipped)

---

## Design Principles

1. **Auto where reliable, manual where not** — scrape the codebase for things that auto-work (prior meeting docs, git log → Reference section, config file). Interview the PM for things the skill historically got wrong (theme labels, bucket assignment, summaries). The git log is evidence; the PM is the author.
2. **Deliver what you promised** — when prior commitments exist, §2 Progress Review compares them against actual delivery (committed-vs-actual table). The Summary slide's `Last week — Delivered` + `Last week — In progress` sub-tables show what moved last week, with the bucket carrying the status signal. The client always sees what they paid for. No silent drift, no blank slides.
3. **Three artifacts, one data model** — Preview for D-1 client share, Agenda for PM internal use, Presentation for D-0 client meeting. Same synthesized data, three audiences.
4. **Consistent branding** — reuse kickoff styling so all Potential Inc client materials look like one family.
5. **Language follows invocation** — Korean in → Korean out; English in → English out. Never mix languages within a single generation.
6. **Slim over heavy** — 7 sections, up to 9 slides. Summary absorbs the last-week review (one slide, not two). Discussion Items is optional (rendered only when `discussion_items` is non-empty). Deck length adapts to what's actually worth discussing in 30 minutes.
