---
name: input-classifier
description: Automatically classifies input content for PRD updates — detects Q&A answers, change requests, or mixed input and routes to the appropriate processing mode
---

# Input Classifier Skill

Automatically analyzes input file content and classifies it into processing modes before any PRD modification is allowed. This skill acts as a guardrail — PRD files cannot be modified until classification is complete.

## Overview

When `/update-prd` is executed, this skill runs **before** any PRD file is modified. It reads the input file, detects what type of content it contains, and routes each item to the appropriate processing mode.

**Context dependency**: This skill is registered in `skill-rules.json` with `fileTriggers` on PRD files (`.claude-project/prd/*_PRD_*.md`), meaning it blocks PRD file edits until classification completes. The input file path is provided by the `/update-prd` command via `$ARGUMENTS` — this skill does NOT independently determine which file to classify.

## Classification Categories

### 1. Question Resolution

Client answers to existing Additional Questions in the PRD.

**Detection patterns:**
- Direct question number references: `Q1`, `Q2`, `Required #3`, `Recommended #2`
- Answer-style headings: `## Deployment Environment`, `## Database Choice`
- Freeform answers with keyword overlap to existing PRD questions
- Response format indicators: numbered lists matching question counts

### 2. Change Request

Requests to modify existing PRD features, scope, or decisions.

**Detection patterns:**
- Addition signals: "add", "include", "new feature", "also need", "we want"
- Removal signals: "remove", "delete", "no longer need", "drop", "cancel"
- Replacement signals: "replace", "change to", "switch from", "instead of", "rename"
- Modification signals: "modify", "update", "adjust", "revise", "expand", "reduce"
- Scope change signals: "out of scope", "add to scope", "phase 2", "priority change"

### 3. Mixed

Input contains both Q&A answers and change requests.

**Detection:** Both Question Resolution and Change Request patterns found in the same input.

---

## Classification Process

### Step 1: Read Input Content

Read the input file provided to `/update-prd`. Supported formats: `.md`, `.txt`, `.pdf`, or any text-based file.

> **Note**: Binary formats (`.xlsx`, `.csv`) are not directly readable. If the user provides a binary file, ask them to convert it to a text-based format first.

### Step 2: Load Target PRD Questions

Read the target PRD's Additional Questions section to compare against input content:
- Extract all Required Clarifications (question text + context)
- Extract all Recommended Clarifications (question text + context)
- Extract all Confirmed Decisions (for conflict detection later)

### Step 3: Classify Each Item

For each identifiable item in the input:

**3.1 Check for Question Resolution signals:**
- Does it reference a question number? → Question Resolution
- Does it contain keywords matching an existing PRD question? → Question Resolution
- Does it directly answer an existing question topic? → Question Resolution

**3.2 Check for Change Request signals:**
- Does it request adding a new feature not in the PRD? → Change Request (ADD)
- Does it request removing an existing feature? → Change Request (REMOVE)
- Does it request replacing one feature with another? → Change Request (REPLACE)
- Does it request modifying existing feature behavior? → Change Request (MODIFY)

**3.3 Handle ambiguous items:**
- If an item could be either Q&A or Change Request, classify based on the dominant pattern
- If truly ambiguous, ask user for clarification via AskUserQuestion:
  ```
  Ambiguous item detected:
    "[item content]"

  How should this be classified?
    1. Question Answer — resolves an existing question
    2. Change Request — modifies PRD scope/features
    3. Skip — ignore this item
  ```

### Step 4: Generate Classification Result

Output the classification summary before proceeding.

---

## Output Format

### Question Resolution Only

```
Input Classification Result:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: [filename]
Classification: QUESTION RESOLUTION

Question Answers (N):
  Q1 → "[answer summary]"
  Q3 → "[answer summary]"
  Q5 → "[answer summary]"

Routing:
  → Question Resolution mode: N items
  → Proceeding with standard Q&A matching...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Change Request Only

```
Input Classification Result:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: [filename]
Classification: CHANGE REQUEST

Change Requests (N):
  [ADD] Push notification feature
  [REPLACE] "My Collection" → "Art Feed"
  [REMOVE] Video call feature

Routing:
  → Change Request mode (Safety Gate required): N items
  → Running Impact Analysis...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Mixed Input

```
Input Classification Result:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: [filename]
Classification: MIXED

Question Answers (N):
  Q1 → "[answer summary]"
  Q3 → "[answer summary]"

Change Requests (M):
  [REPLACE] "My Collection" → "Art Feed"
  [ADD] Push notification feature

Routing:
  → Question Resolution mode: N items (processing first)
  → Change Request mode (Safety Gate required): M items (processing after Q&A)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Change Request Sub-Types

| Sub-Type | Tag | Risk Level | Description |
|:---------|:----|:-----------|:------------|
| Add feature | `[ADD]` | Medium | New feature not in current PRD |
| Remove feature | `[REMOVE]` | HIGH | Remove existing feature from PRD |
| Replace feature | `[REPLACE]` | HIGH | Swap one feature for another |
| Modify feature | `[MODIFY]` | Medium | Change behavior of existing feature |
| Extend feature | `[EXTEND]` | Medium | Add capabilities to existing feature |
| Change permission | `[PERMISSION]` | HIGH | Alter user role access |
| Change priority | `[PRIORITY]` | Low | Reorder feature priority |
| Reverse decision | `[REVERSE]` | CRITICAL | Contradict a Confirmed Decision |

---

## Rules

1. **Always classify before modifying** — No PRD file may be edited until classification is complete
2. **Preserve all items** — Every identifiable item must be classified, nothing is silently dropped
3. **Ask when ambiguous** — If classification confidence is low, ask the user rather than guessing
4. **Q&A first in mixed mode** — When both types are present, process Question Resolution items first
5. **Cascade conflict awareness** — In mixed mode, Q&A resolution may add new Confirmed Decisions. Change Requests processed afterward must run Conflict Detection against the **updated** Confirmed Decisions list (including newly added ones from Q&A), not just the original list
6. **Tag all Change Requests** — Every Change Request must have a sub-type tag (`[ADD]`, `[REMOVE]`, etc.)
7. **Risk level assignment** — Every Change Request must have a risk level for Safety Gate routing
