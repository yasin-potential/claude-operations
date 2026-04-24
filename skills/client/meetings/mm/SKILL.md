---
name: mm
description: "Generate meeting minutes from a transcript — short summary, decisions approved, mismatches, blockers from both sides, and action items. Outputs an internal .md report (for developers and memory) + a Slack-ready summary to share with the client."
user-invocable: true
argument-hint: "[--project 'name'] [--date 'YYYY-MM-DD'] [--source 'path/to/transcript.txt']"
---

# Meeting Minutes Generator

Analyse a meeting transcript and produce two precision artifacts:

1. **Internal `.md` report** — structured minutes for the dev team and project memory. Precise enough that any team member who was not in the meeting can act immediately.
2. **Slack summary** — a short, copy-pasteable block to send to the client and all attendees.

> **Principle:** Every line must be precise and actionable. No filler. If it cannot be acted on or referenced, cut it.

---

## Workflow Overview

```
┌─────────────────────┐
│ Step 1: Collect     │  Arguments + transcript input (paste or file)
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Step 2: Analyse     │  Parse transcript → extract structured data
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Step 3: Generate    │  Write .md report + Slack summary
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Step 4: Memory      │  Save key decisions + action items to project memory
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│ Step 5: Report      │
└─────────────────────┘
```

---

## Step 1: Collect Input

### 1.1 Parse Arguments

Extract from `$ARGUMENTS`:

| Arg | Required | Default |
|-----|----------|---------|
| `--project` | No | Auto-detect from CWD folder name or `package.json` name |
| `--date` | No | Today's date (`YYYY-MM-DD`) |
| `--source` | No | Path to a `.txt` / `.md` transcript file |

### 1.2 Obtain Transcript

**If `--source` is provided:**
Read the file at that path. Accept `.txt`, `.md`, `.vtt`, or any plain-text format.

**If no `--source` is provided:**
Use `AskUserQuestion` with a single prompt:

```
Paste the meeting transcript below.

This can be:
  - A raw copy-paste from Zoom, Google Meet, or Teams auto-transcript
  - A copy from the project dashboard meeting recording
  - A text summary someone typed during the meeting
  - A Slack thread recap

Paste everything — the more complete, the more accurate the minutes.
```

Accept the full pasted block as the transcript. Do not truncate or pre-process it before analysis.

### 1.3 Collect Attendees (optional fast-follow)

If attendees are not clearly identifiable from the transcript, ask in one follow-up:

```
Who attended? (Name, role — one per line. Skip if already in the transcript.)
```

Accept "skip" to proceed without a named attendee list.

---

## Step 2: Analyse the Transcript

Perform a single structured analysis pass. Extract all of the following from the transcript. Do not invent, assume, or pad — only include what is explicitly stated or directly implied.

### 2.1 Short Summary

Write **3–5 sentences** covering:
- The purpose of the meeting
- What was discussed at a high level
- The overall outcome or tone

No bullet points. Plain prose. Write it so someone who skipped the meeting understands the context in 30 seconds.

### 2.2 Decisions Taken / Approved

List every decision that was explicitly agreed to, approved, or confirmed during the meeting. Include:
- **What** was decided
- **Who** approved it (if stated)
- **Any conditions** attached (e.g., "approved if X is delivered by Friday")

Format as a numbered list. If nothing was formally decided, write: *No formal decisions recorded.*

**Decision criteria:** A decision is recorded only if both parties acknowledged it. Do not list items that were merely discussed or proposed without agreement.

### 2.3 Mismatches

List every point where the **client's expectation or understanding differed from the team's**. Include:
- The topic
- What the client understood / expected
- What the team understood / built
- Whether it was resolved in the meeting or remains open

Format as a two-column comparison where possible. If no mismatches occurred, write: *No mismatches identified.*

**Mismatch criteria:** A mismatch is a gap — something the client thought was done, planned differently, or interpreted differently than the team. It is not the same as a blocker or a decision.

### 2.4 Blockers

List all blockers raised by **either side**. Separate clearly:

**Client-side blockers** — things the team is waiting on from the client (assets, approvals, content, credentials, decisions not yet made).

**Team-side blockers** — things the team has flagged as blocking their progress (unresolved technical issues, unclear requirements, missing access, third-party delays).

For each blocker include:
- What is blocked
- Who owns unblocking it
- Target resolution date (if mentioned)

If no blockers were raised, write: *No blockers raised.*

### 2.5 Action Items

List every task, follow-up, or commitment mentioned in the meeting. For each:

| Field | Rule |
|-------|------|
| **Task** | One clear sentence. What exactly needs to happen. |
| **Owner** | Name or role. If unclear from transcript, write "TBD". |
| **Deadline** | Exact date if mentioned. If not mentioned, write "Not specified". |
| **Side** | Client or Team |
| **Priority** | High / Medium / Low — infer from urgency language in transcript. |

Include every commitment made, even informally ("I'll send that over by tomorrow"). Do not filter.

---

## Step 3: Generate Artifacts

### 3.1 Output Location

Save the `.md` file at:

```
.claude-project/meetings/{ProjectName}/minutes/[MM] {ProjectName} ({YYYY-MM-DD}).md
```

Create the directory if it does not exist.

### 3.2 Internal `.md` Report Template

```markdown
# {PROJECT} — Meeting Minutes

**Date:** {YYYY-MM-DD}
**Attendees:** {list or "See transcript"}
**Meeting type:** {e.g., Weekly sync / Ad-hoc / Demo / Feedback session}
**Source:** {Transcript source — dashboard recording, paste, etc.}

---

## Summary

{3–5 sentence plain prose summary}

---

## Decisions Taken

{Numbered list — each decision on one line.
 Mark approved decisions with ✅
 Mark conditional decisions with ⚠ and state the condition.}

---

## Mismatches

| Topic | Client understood | Team understood | Status |
|-------|------------------|-----------------|--------|
| {item} | {client view} | {team view} | Resolved / Open |

---

## Blockers

### Client Side
{Numbered list. Each item: what is blocked, who unblocks it, target date.}

### Team Side
{Numbered list. Each item: what is blocked, who unblocks it, target date.}

---

## Action Items

| # | Task | Owner | Side | Deadline | Priority |
|---|------|-------|------|----------|----------|
| 1 | {task} | {owner} | Client/Team | {date or "Not specified"} | High/Med/Low |

---

## Notes

{Any additional context that does not fit above — quotes worth preserving, tone observations,
 follow-up meeting scheduled, etc. Keep brief. Delete this section if empty.}
```

### 3.3 Slack Summary

After writing the `.md` file, print the following block to the conversation so the PM can copy-paste it directly into Slack. Do not save this as a file.

Format:

```
*📋 Meeting Minutes — {PROJECT} | {YYYY-MM-DD}*

*Summary*
{2–3 sentence version of the summary — even tighter than the .md version}

*✅ Decisions*
{Bullet list — one line per decision. Approved items only.}

*⚠ Open Mismatches*
{Bullet list — only unresolved mismatches. Skip if none.}

*🚧 Blockers*
{Client: bullet list}
{Team: bullet list}
{Skip entire section if no blockers.}

*📌 Action Items*
{Formatted list:
 → [Owner] {Task} — by {date or "TBD"}
 Keep to max 8 items. If more exist, note "Full list in meeting minutes doc."}

---
_Minutes generated {YYYY-MM-DD} · Potential INC_
```

**Slack formatting rules:**
- Use `*bold*` for headers (Slack markdown)
- Use `→` prefix for action items
- Max 8 action items displayed — if there are more, truncate with "Full list in meeting minutes doc."
- Keep the entire summary under 40 lines so it reads cleanly in Slack without collapsing
- No HTML, no triple backticks in the final Slack block

---

## Step 4: Save to Memory

After generating the `.md` file, save a project memory with the key extractable facts. Write to the project's memory file (`.claude/projects/{cwd}/memory/` or the current session memory system).

Save as a `project` type memory:

**Content:**
```
Meeting: {ProjectName} — {YYYY-MM-DD}
Key decisions: {comma-separated one-liners of each decision}
Open action items (team): {count} items, next deadline {earliest deadline}
Open action items (client): {count} items, next deadline {earliest deadline}
Unresolved mismatches: {count} — {brief topic list}
Blockers: {client count} client-side, {team count} team-side
```

**Why:** Future conversations can reference this memory to know what was agreed, what is blocked, and what the team owes the client — without re-reading the transcript.

---

## Step 5: Report Result

After all artifacts are generated, print:

```
Meeting minutes generated.

Project:    {PROJECT_NAME}
Date:       {YYYY-MM-DD}
Source:     {transcript source}

Report:     .claude-project/meetings/{ProjectName}/minutes/[MM] {ProjectName} ({YYYY-MM-DD}).md

Summary:    {decisions count} decisions  ·  {mismatches count} mismatches  ·  {total action items} action items
            {client blockers count} client blockers  ·  {team blockers count} team blockers

Memory:     Saved to project memory

Slack summary printed above — copy and paste directly into Slack.
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Transcript is empty or too short (<50 words) | Ask user to paste the transcript again — the input may have been cut off |
| No attendees identifiable | Proceed without attendee list; write "Not recorded" in the header |
| Transcript is in a non-English language | Analyse in the original language, generate all outputs in English. Note the source language in the report header. |
| No action items found | Write "No action items recorded" in the table section — do not fabricate tasks |
| No decisions found | Write "No formal decisions recorded" — do not infer decisions from discussion |
| Output directory creation fails | Fall back to `.claude-project/meetings/minutes/` |
| Memory system unavailable | Skip Step 4, note "Memory not saved" in the Step 5 report |

---

## Quality Rules

Before outputting either artifact, verify:

| # | Check | Severity |
|---|-------|----------|
| 1 | Every action item has an owner (Name, role, or "TBD") — never owner-less | HIGH |
| 2 | Every decision is explicitly stated as agreed — not merely discussed | HIGH |
| 3 | Mismatches table separates "client view" from "team view" in distinct columns | HIGH |
| 4 | Blockers are split into Client Side and Team Side — never mixed | HIGH |
| 5 | Slack summary is ≤40 lines and uses Slack markdown only (`*bold*`, `_italic_`, bullets) | MEDIUM |
| 6 | Summary prose is 3–5 sentences — not bullet points, not longer | MEDIUM |
| 7 | No invented data — every item traceable to the transcript | HIGH |
| 8 | Action items table includes Priority column populated for all rows | LOW |

---

## Examples

### Example 1: Paste transcript

```bash
/mm --project "Artlive"
```
→ Prompts for transcript paste → Analyses → Writes `[MM] Artlive (2026-04-24).md` → Prints Slack summary

### Example 2: From file

```bash
/mm --project "Artlive" --source ".claude-project/meetings/transcript-2026-04-24.txt"
```
→ Reads the file → Analyses → Writes `.md` → Prints Slack summary → Saves memory

### Example 3: Override date

```bash
/mm --project "Artlive" --date "2026-04-21"
```
→ Uses April 21st as the meeting date regardless of today's date
→ Useful when processing a transcript from a past meeting
