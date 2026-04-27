---
name: make-mm
description: Generate Slack-ready meeting minutes from a raw transcript or notes. Extracts decisions, action items, blockers, open mismatches, and next meeting agenda into a fixed Slack-formatted block.
user-invocable: true
argument-hint: "[--project 'name'] [--date 'YYYY-MM-DD'] [--type 'kickoff|weekly|closing|adhoc']"
---

# Meeting Minutes Generator

Accepts a raw meeting transcript or notes and outputs a single **Slack-ready meeting minutes block** — ready to copy-paste into any channel.

---

## Workflow Overview

```
┌──────────────────────┐
│ Step 1: Parse Args   │  project, date, type
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 2: Collect      │  ask for transcript if not provided
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 3: Extract      │  summary, decisions, mismatches, blockers, action items, agenda
└──────────┬───────────┘
           │
┌──────────▼───────────┐
│ Step 4: Output       │  print the formatted Slack block
└──────────────────────┘
```

---

## Step 1: Parse Arguments

Extract from `$ARGUMENTS`:

| Argument | Type | Default |
|----------|------|---------|
| `--project` | string | Must ask if missing |
| `--date` | YYYY-MM-DD | Today |
| `--type` | `kickoff \| weekly \| closing \| adhoc` | `adhoc` |

---

## Step 2: Collect Input

If the user already pasted the transcript in their message, use it directly — do not ask again.

If the transcript is missing, use AskUserQuestion:

**Round 1 — Project name** (only if `--project` was not provided):

```
What is the project name for these meeting minutes?
```

**Round 2 — Transcript** (only if not already pasted):

```
Please paste the meeting transcript, notes, or bullet points below.
Raw, unformatted, or voice-to-text output is fine.
```

---

## Step 3: Extract Structured Content

Read the full transcript and populate this model:

```
{
  project_name:    "...",
  date:            "YYYY-MM-DD",
  type:            "kickoff | weekly | closing | adhoc",
  subtitle:        "short label describing the meeting topic",

  summary:         "2–3 sentence narrative — what was the core reason for the meeting,
                    what was resolved, and what comes next",

  decisions: [
    "plain English sentence stating the agreed outcome"
  ],

  open_mismatches: [
    "• {Topic} — {what the client expects vs what the team understands or believes}"
  ],

  blockers: [
    "{Party} → {description of what is blocking and why}"
  ],

  action_items: [
    {
      priority: "high | medium | low",
      owner:    "[Name]" or "[Name + Name]" or "[Team]",
      task:     "clear imperative task description",
      deadline: "YYYY-MM-DD" or "Ongoing"
    }
  ],

  next_meeting_agenda: [
    "agenda item as a bullet"
  ]
}
```

### Extraction Rules

**Summary** — 2–3 sentences. Cover: (1) what triggered the meeting, (2) the main resolution or alignment reached, (3) what the team will do next.

**Decisions** — any outcome the group explicitly agreed on. Signal phrases: "we decided", "agreed", "confirmed", "will go with", "the rule is", "policy is", "we won't". Write as a full declarative sentence, no owner, no deadline.

**Open Mismatches** — gaps where the client's expectation does not match the team's understanding, or where something is unclear to one side. NOT the same as blockers. Format each as:
```
• {Topic} — {client side} vs {team side} or {what is unclear}
```

**Blockers** — concrete things preventing progress right now. Format each as:
```
{Party} → {description}
```
`Party` is who is blocked or waiting: "Client", "Team", "Symon", etc.

**Action Items** — assigned tasks with an implicit or explicit owner. Sort by priority (high first, then medium, then low). If no deadline is stated, infer from context or use "Ongoing".

Priority assignment:
- **High** `:red_circle:` — must be done today or by the next working day
- **Medium** `:large_yellow_circle:` — due within the current sprint or week
- **Low / Ongoing** `:white_circle:` — no hard deadline, continuous, or post-sprint

**Next Meeting Agenda** — topics that were explicitly deferred, left open, or flagged as needing follow-up at the next meeting. Include: unresolved decisions, action items that need status confirmation, and monitoring items.

---

## Step 4: Output — Slack Block

Print the following block verbatim, substituting values. Do NOT wrap in a code fence. Output the raw text so the user can copy it directly.

```
{ProjectName} · Meeting Minutes
:date: {YYYY-MM-DD}  ·  :label: {Type} — {Subtitle}

:speech_balloon: Summary
{summary}

:white_check_mark: Decisions ({N})

1. {decision 1}
2. {decision 2}
N. {decision N}


:warning: Open Mismatches ({N})
{• mismatch 1}
{• mismatch 2}

:construction: Blockers

1. {Party} → {description}
2. {Party} → {description}

:pushpin: Action Items ({N})
:red_circle: [{Owner}] {task} — {deadline}
:large_yellow_circle: [{Owner}] {task} — {deadline}
:white_circle: [{Owner}] {task} — {deadline}

:calendar: Next Meeting Agenda
• {agenda item 1}
• {agenda item 2}
```

### Formatting Rules

- **Project name**: use the `--project` value exactly as given.
- **Type label**: capitalize first letter of each word (e.g., `Ad-hoc — Post-Client Debrief`, `Weekly — Sprint 12 Debrief`).
- **Subtitle**: derive from the meeting topic — concise, 3–6 words.
- **Decisions list**: one decision per line, no bullets, no numbering, no owner/deadline.
- **Open Mismatches**: prefix each with `•` and a space.
- **Blockers**: one per line, `{Party} → {description}`, no bullets.
- **Action items**: sorted high → medium → low. Format exactly:
  ```
  :red_circle: [{Owner}] {task description} — {YYYY-MM-DD or "Ongoing"}
  ```
- **Next Meeting Agenda**: prefix each with `•` and a space.
- **Sections with zero items**: omit the section entirely (do not print an empty header).
- **Counts in headers**: always reflect the actual number of items extracted.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| No transcript provided after two asks | Output a blank template with all section headers and `(none recorded)` under each |
| Project name not provided | Default to `"[Project]"` as a placeholder |
| No decisions found | Omit `:white_check_mark: Decisions` section entirely |
| No blockers found | Omit `:construction: Blockers` section entirely |
| No open mismatches found | Omit `:warning: Open Mismatches` section entirely |
| Owner unclear | Use `[TBD]` |
| Deadline not mentioned | Infer from context; if impossible, use `"Ongoing"` |

---

## Example

### Input

```
/make-mm --project "Elite4Print" --type "adhoc"
```
User pastes a voice-to-text Zoom transcript from an internal debrief after a client call.

### Output

```
Elite4Print · Meeting Minutes
:date: 2026-04-27  ·  :label: Ad-hoc — Post-Client Debrief

:speech_balloon: Summary
Internal debrief after a client meeting where Lucas flagged that a ticket description was too vague to understand. Team aligned on enforcing clearer ticket standards, confirmed the refund anomaly is resolved via recent deployments, and scoped a new invoice breakdown feature as a post-bugfix extension.

:white_check_mark: Decisions (5)

All tickets must include a clear goal, context, and expected outcome — vague one-liners are not acceptable
All tracking stays in the PM Dashboard — Notion and Google Docs are ruled out per company policy
Refund anomaly is considered resolved via recent deployments — no reproduction needed, team monitors proactively
Invoice breakdown (shipping cost per order + reward point deduction on refunds) = feature extension, starts only after current bug sprint closes
Symon replies to Lucas's thread first with full ticket details; Murad adds supplementary clarification after


:warning: Open Mismatches (2)
• CSV / work order task — Lucas is unclear on the ticket goal; team understands the task but the written description did not communicate it
• Refund reproduction — Client may expect a sit-together session to reproduce; team believes the issue is already fixed and prefers proactive monitoring only

:construction: Blockers
Client → Waiting on team reply to the CSV task clarification thread
Team → Refund root cause is unknown — logs show nothing suspicious, monitoring only
Team → Slack is cluttered with mixed internal and client messages — important messages are getting buried

:pushpin: Action Items (8)
:red_circle: [Symon] Reply to Lucas on the CSV task thread with full ticket goal and details — 2026-04-27
:red_circle: [Murad] Add supplementary clarification lines to Symon's reply in the same thread — 2026-04-27
:red_circle: [Symon] Share last night's client meeting MM with the full team — 2026-04-27
:large_yellow_circle: [Symon + Siam] Audit all open client tickets and rewrite unclear descriptions — 2026-04-29
:large_yellow_circle: [Symon] Create ticket for invoice breakdown extension (shipping cost + reward points) — 2026-04-29
:large_yellow_circle: [Murad] Propose PM Dashboard enhancements to support detailed ticket descriptions — 2026-05-01
:large_yellow_circle: [Team] Monitor proactively for recurrence of refund / invoice anomaly — Ongoing
:white_circle: [Symon + Murad] Close current bug-fix scope: refund point logs + price quotation page fixes — by 2026-05-13

:calendar: Next Meeting Agenda
• Status of ticket-description audit across all open client tickets
• PM Dashboard enhancement proposal from Murad
• Confirmed deadline for current bug-fix scope
• Invoice breakdown extension ticket status
• Any recurrence of the refund / invoice anomaly
```

---

## Design Principles

1. **Transcript in, Slack block out** — no files, no HTML, no markdown documents. One clean text block ready to paste.
2. **Open Mismatches are not blockers** — a mismatch is a perception gap between client and team; a blocker is something preventing work from moving.
3. **Decisions are stand-alone facts** — no owner, no deadline in the decisions list. They are agreed truths.
4. **Action items are always owned** — ambiguous ownership is `[TBD]`, never silent.
5. **Omit, never empty** — a section with no items is dropped entirely, not printed with a blank body.
