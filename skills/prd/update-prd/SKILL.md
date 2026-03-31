---
name: update-prd
description: "Update an existing PRD with client answers, scope changes, or mixed input. Invoke when user wants to update a PRD with client feedback."
argument-hint: "Path to client input file (e.g., /path/to/client-feedback.md)"
---

You are a PRD update specialist. Your task is to surgically update an existing PRD document based on client answers to the Additional Questions section, without regenerating the entire PRD.

---

## Workflow Overview

1. Read and validate input file
2. Detect target PRD
3. Read and parse existing PRD
4. Classify input content (input-classifier skill auto-runs)
5. Match answers to questions (Question Resolution items)
6. Change Request Safety Gate (Change Request items — Impact Analysis → Diff Preview → Conflict Detection → Approval)
7. Apply approved changes
8. Update Additional Questions section
9. Update Feature Change Log
10. Save updated PRD
11. Report results

---

## Step 1: Read and Validate Input File

Read the file path from `$ARGUMENTS`.

**Supported formats**: `.md`, `.txt`, `.pdf`, or any text-based file

> **Note**: Binary formats (`.xlsx`, `.csv`) are not directly supported. If the user provides a binary file, ask them to convert it to a text-based format (e.g., copy-paste into `.md` or `.txt`) before proceeding.

**Validation checks**:
1. File path is provided
2. File exists and is readable
3. File is not empty

**If validation fails**, output error and stop:
```
Error: [specific error message]
Usage: /update-prd /path/to/client-answers.md
```

---

## Step 2: Detect Target PRD

Scan `.claude-project/prd/` directory for all PRD files matching `*_PRD_*.md` or `*_FeaturePRD_*.md` pattern.

> **Feature PRD vs Full PRD**: The system supports two PRD types:
> - `*_FeaturePRD_*.md` — Phase A output (Sections 0-4 + 2.5 + 8 only)
> - `*_PRD_*.md` — Complete merged PRD (Phase A + Phase B, Sections 0-8)
>
> Both types can be updated. When updating a Feature PRD, changes to feature sections apply directly.
> When updating a Full PRD, if changes affect entities/CRUD in Section 3/4, flag that technical sections may need refresh.

### 2.1 No PRDs Found

```
Error: No PRD files found in .claude-project/prd/
Run /generate-prd first to create a PRD.
```

### 2.2 Single PRD Found

Auto-select and confirm:
```
Found PRD: [filename]
Version: [X.X]
Open questions: [N] Required, [N] Recommended

Updating this PRD. Proceed? [Y/N]
```

### 2.3 Multiple PRDs Found

Display selection list:
```
Found [N] PRDs in .claude-project/prd/:

  1. FleetPulse_PRD_260209.md
     Version: 1.0 | Required: 6 open | Recommended: 8 open

  2. ReviewBoard_PRD_260225.md
     Version: 1.0 | Required: 3 open | Recommended: 0

Which PRD to update? [number]:
```

Wait for user selection via AskUserQuestion.

---

## Step 3: Read and Parse Existing PRD

Read the selected PRD file and extract:

### 3.1 Additional Questions Section

Find `# Additional Questions` header (match both variants):
- `# Additional Questions (Client Confirmation Required)` — has open questions
- `# Additional Questions (All Resolved)` — already complete

**If header says "All Resolved":**
```
All questions in [filename] are already resolved (Version [X.X]).
```
If input contains Change Request items → proceed to Step 4 (input-classifier will route to Change Request mode).
If input contains only Q&A items → stop execution with message:
```
No update needed. All questions are already resolved.
If you have scope changes or feature modifications, provide a change request file.
```

**Parse tables under:**
- `## Required Clarifications` — table with columns: `# | Question | Context`
- `## Recommended Clarifications` — table with columns: `# | Question | Context`
- `## Confirmed Decisions` (if exists) — table with columns: `# | Item | Decision | Source`

Build structured question list:
```
[
  {id: 1, question: "...", context: "...", category: "required"},
  {id: 2, question: "...", context: "...", category: "required"},
  {id: 1, question: "...", context: "...", category: "recommended"},
  ...
]
```

### 3.2 Feature Change Log

Find `# Feature Change Log` section. Parse the latest `## Version X.X` to determine current version number.

If no Feature Change Log exists, assume Version 1.0.

### 3.3 PRD Body Sections

Identify all major sections for potential updates:
- Part 1: Basic Information (Terminology, Project Information, System Modules, 3rd Party API List)
- Part 2: User Application PRD (per user type sections)
- Part 3: Admin Dashboard PRD

Note locations of `TBD - Client confirmation needed` markers throughout the PRD.

---

## Step 4: Classify Input Content

The **input-classifier** skill automatically runs before any PRD modification (enforced via `block` enforcement in skill-rules.json). This step classifies the input content into processing modes.

### 4.1 Input Classification

The input-classifier analyzes the file content and classifies each item:

- **Question Resolution** — Q&A answers to existing Additional Questions
- **Change Request** — Feature add/remove/replace/modify requests
- **Mixed** — Both types present in the same input

Classification output:
```
Input Classification Result:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: [filename]
Classification: [QUESTION RESOLUTION / CHANGE REQUEST / MIXED]

Question Answers (N):
  Q1 → "[answer summary]"
  ...

Change Requests (M):
  [ADD] [description]
  [REMOVE] [description]
  [REPLACE] "[old]" → "[new]"
  ...

Routing:
  → Question Resolution mode: N items
  → Change Request mode (Safety Gate required): M items
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 Parse Question Answers

For items classified as Question Resolution, extract question-answer pairs:

**Numbered format** (highest confidence):
```
Q1: Vercel for deployment
Q2: Firebase Firestore
Required #3: Yes, include Kakao login
```

**Heading-based format**:
```
## Deployment Environment
We'll use Vercel for deployment.

## Database
Firebase Firestore for the main database.
```

**Freeform format** (lowest confidence):
```
We discussed internally and decided on the following:
- For deployment, we'll go with Vercel...
- The database will be Firebase Firestore...
```

For each identifiable answer, extract:
- The answer content
- Any reference to a question number (if present)
- Key topic keywords for matching

### 4.3 Parse Change Requests

For items classified as Change Request, extract and tag each:

| Tag | Detection Signals | Example |
|:----|:-----------------|:--------|
| `[ADD]` | "add", "include", "new feature", "we want" | "Add push notification feature" |
| `[REMOVE]` | "remove", "delete", "drop", "no longer need" | "Remove video call feature" |
| `[REPLACE]` | "replace", "change to", "switch", "rename" | "Replace My Collection with Art Feed" |
| `[MODIFY]` | "modify", "update", "adjust", "expand" | "Expand user permissions to include editor role" |
| `[EXTEND]` | "extend", "also", "additionally" | "Also support Apple login" |
| `[PERMISSION]` | "role", "access", "permission" | "Admin should also access analytics" |
| `[PRIORITY]` | "priority", "phase 2", "defer", "move up" | "Move analytics to phase 2" |
| `[REVERSE]` | Contradicts a Confirmed Decision | "Actually, don't use Toss Payments" |

---

## Step 5: Match Answers to Questions

**Applies to: Question Resolution items only.**

For each extracted answer, find the matching question from the PRD.

### 5.1 Matching Strategy (in priority order)

1. **Exact ID match**: Answer references question number directly
   - "Q1: Vercel" → matches Required Question #1
   - "Recommended #2: Not needed" → matches Recommended Question #2
   - Confidence: **exact**

2. **Keyword match**: Answer content contains keywords from a question
   - Answer mentions "deployment" → matches question about "Deployment environment?"
   - Confidence: **keyword**

3. **Semantic match**: No direct keyword overlap, but topic aligns
   - Answer about "server infrastructure" → matches question about "hosting provider"
   - Confidence: **semantic**

### 5.2 Confidence Validation

**Exact matches**: Apply directly, no confirmation needed.

**Keyword matches**: Apply directly, but note in report.

**Semantic matches**: Ask user for confirmation:
```
Low-confidence match detected:

  Answer: "We'll use Firebase for storage"
  Matched to: Required Q2 "Image storage provider?"
  Confidence: semantic

  Is this correct? [Y/N]
```

### 5.3 Unmatched Answers

If an answer cannot be matched to any existing question:
```
Unmatched answer found:
  "[answer content]"
  This does not match any open question in the PRD.

  Options:
  1. Add as general note to PRD
  2. Skip this answer
  3. Manually assign to a question
```

---

## Step 6: Change Request Safety Gate

**Applies to: Change Request items only. Skipped if no Change Requests detected.**

The prd-manager agent's Safety Gate process runs for all Change Request items.

### 6.1 Gate 1: Impact Analysis

For each change request, scan the entire PRD to identify affected sections:

```
Impact Analysis:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source: [filename]
Changes detected: [N]

1. [REPLACE] "My Collection" → "Art Feed"
   Impact: HIGH
   Affected sections (4):
   - Part 1 > Terminology
   - Part 1 > System Modules > Module 3
   - Part 2 > User > Tab 1
   - Part 2 > User > Navigation Menu

2. [ADD] Push notification for new artwork
   Impact: MEDIUM
   Affected sections (2):
   - Part 2 > User > Notifications (new)
   - Part 1 > 3rd Party API List
```

### 6.2 Gate 2: Diff Preview

For each affected section, generate Before/After preview:

```
Diff Preview:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Change 1: [REPLACE] "My Collection" → "Art Feed"

  Part 1 > Terminology:
  - BEFORE: | My Collection | User's saved artwork list |
  + AFTER:  | Art Feed | Personalized artwork discovery feed |

  Part 2 > User > Tab 1:
  - BEFORE: #### 1. My Collection Tab
  + AFTER:  #### 1. Art Feed Tab

Change 2: [ADD] Push notification
  + NEW: Part 2 > User > Notifications section
  + ADD: Part 1 > 3rd Party API: Firebase Cloud Messaging
```

### 6.3 Gate 3: Conflict Detection + Approval

Check each change against the Confirmed Decisions table:

**If conflict found:**
```
⚠ CONFLICT DETECTED:

Change: [REMOVE] Video call feature
Conflicts with: Confirmed Decision #3
  "Video call between trainer and student" (confirmed in v1.1)
  Source: Client Answer File (client-answers.md)

Options:
  1. Apply anyway (decision will be reversed, logged in Change Log)
  2. Skip this change
  3. Add to questions (ask client to re-confirm)
```

**Approval (for Medium+ risk changes):**
```
Approve changes?
  1. Apply all [N] changes
  2. Select which to apply
  3. Reject all (no changes made)
```

If "Select which to apply" → individual Approve/Reject for each change.

### 6.4 Risk-Based Gate Routing

| Risk Level | Gates | Behavior |
|:-----------|:------|:---------|
| Low | Gate 1 + Gate 2 | Show analysis, auto-apply |
| Medium | Gate 1 + Gate 2 + Gate 3 | Show analysis, require approval |
| HIGH | Gate 1 + Gate 2 + Gate 3 + Conflict Check | Show analysis, check conflicts, require approval |
| CRITICAL | All gates + Warning | Show analysis, check conflicts, explicit warning, require approval |

---

## Step 7: Apply Approved Changes

Apply only approved changes to the PRD. This step handles both Question Resolution and Change Request items.

### 7.1 Question Resolution Updates

For each confirmed answer-question pair, update the PRD body:

1. Search PRD body for `TBD - Client confirmation needed` markers related to this topic
2. Search for sections that reference the question's topic keywords
3. Identify all locations that need updating (one answer may affect multiple sections)

**Example**: Question "Which payment provider?" answered with "Toss Payments"
- Update `## 3rd Party API List` → Add "Toss Payments: Payment processing"
- Update relevant Module Flow → Add payment step details
- Update Part 3 Admin → Add payment management section reference

### 7.2 Change Request Updates

For each approved Change Request, apply based on sub-type:

**[ADD]**: Insert new content at the appropriate location
- Add to relevant section(s) identified in Impact Analysis
- Add new terminology to Part 1 > Terminology if applicable
- Add new 3rd party APIs if applicable

**[REMOVE]**: Delete content from all affected sections
- Remove from all locations identified in Impact Analysis
- Remove related terminology if no longer referenced
- Remove 3rd party APIs if no longer needed

**[REPLACE]**: Swap old content with new across all affected sections
- Replace in every location identified in Impact Analysis
- Update terminology table
- Ensure consistency — no orphaned references to the old term

**[MODIFY] / [EXTEND]**: Update existing content
- Modify the affected sections as identified
- Preserve surrounding context

**[REVERSE]**: Undo a Confirmed Decision
- Remove the decision from Confirmed Decisions table
- Revert PRD sections to pre-decision state where possible
- Log as "Decision Reversed" in Change Log

### 7.3 Update Rules (CRITICAL — inherited from generate-prd)

1. **No guessing**: Only write what the client explicitly stated
   - Client says "Toss Payments" → Write "Toss Payments"
   - Do NOT add "with subscription support" unless client said so

2. **Traceable changes**: Every update must be traceable to the input file
   - If you can't point to a specific client statement, don't write it

3. **Partial answers → New questions**: If client's answer is incomplete:
   - Apply what's clear
   - Add new question for what's unclear
   - Example: Client says "Kakao login" → Apply Kakao login, add question "What profile data scope should be retrieved from Kakao login?"

4. **Terminology sync**: If answer introduces new terms:
   - Add to Part 1 > Terminology table
   - Use consistently throughout updated sections

5. **No re-referencing old PRD content**: Only use the client input file as source for changes. Do not infer from existing PRD content.

6. **Rejected changes are skipped**: Changes rejected during Safety Gate approval are NOT applied. They are logged in the report as "Rejected".

7. **Deferred changes become questions**: Changes deferred to "ask client to re-confirm" are added to the Additional Questions section.

### 7.4 Section Update Format

When updating a section, replace only the affected content:

**Before:**
```markdown
### 3rd Party API List
- TBD - Client confirmation needed
```

**After:**
```markdown
### 3rd Party API List
- **Toss Payments**: Payment processing
- **Kakao Login**: Social authentication
```

---

## Step 8: Update Additional Questions Section

### 8.1 Move Answered Questions to Confirmed Decisions

For each resolved question, remove from its original table and add to the Confirmed Decisions section.

**Create or append to Confirmed Decisions:**
```markdown
## Confirmed Decisions

| # | Item | Decision | Source |
|:-:|:-----|:---------|:-------|
| 1 | Payment provider | Toss Payments | Client Answer File ([filename]) |
| 2 | Social login | Kakao, Google, Apple | Client Answer File ([filename]) |
```

### 8.2 Keep Unanswered Questions

Retain unanswered questions in their original tables. Renumber sequentially (no gaps).

**Before (6 questions):**
```markdown
## Required Clarifications
| # | Question | Context |
|:-:|:---------|:--------|
| 1 | Payment provider? | Needed for 3rd party integration |
| 2 | Social login options? | Needed for auth flow |
| 3 | Max users per account? | Needed for permission design |
```

**After (Q1 and Q2 answered, Q3 remains):**
```markdown
## Required Clarifications
| # | Question | Context |
|:-:|:---------|:--------|
| 1 | Max users per account? | Needed for permission design |
```

### 8.3 Add New Questions

If client answers reveal new ambiguities, add to the appropriate table:

```markdown
## Required Clarifications
| # | Question | Context |
|:-:|:---------|:--------|
| 1 | Max users per account? | Needed for permission design |
| 2 | Kakao login profile scope? | Client confirmed Kakao login but scope not specified |
| 3 | Toss Payments subscription support? | Client confirmed Toss but subscription model unclear |
```

### 8.4 Update Section Header

**If ALL questions resolved (both Required and Recommended empty):**
```markdown
# Additional Questions (All Resolved)
```

Remove the Required/Recommended tables and keep only Confirmed Decisions.

**If questions remain:**
```markdown
# Additional Questions (Client Confirmation Required)
```

Keep existing structure with updated tables.

---

## Step 9: Update Feature Change Log

### 9.1 Determine New Version

Parse current version from the latest `## Version X.X` entry.
- Increment minor version: 1.0 → 1.1, 1.1 → 1.2, etc.
- If no version exists, this becomes Version 1.1 (assuming initial PRD was 1.0)

### 9.2 Add New Version Entry

Insert new version **above** existing versions (newest first):

```markdown
## Version [NEW_VERSION] ([TODAY'S DATE: YYYY-MM-DD])

| Change Type | Risk | Before | After | Source |
|:-----------|:-----|:-------|:------|:-------|
| **Question Resolved** | Low | Q: "[question text]" (TBD) | [answer] | Client File ([filename]) |
| **Feature Updated** | Low | [section]: TBD | [updated content summary] | Client File ([filename]) |
| **Feature Added** | Medium | - | [new feature description] | Client File ([filename]) |
| **Feature Replaced** | HIGH | [old feature] | [new feature] | Client File ([filename]) |
| **Feature Removed** | HIGH | [removed feature] | - | Client File ([filename]) |
| **Decision Reversed** | CRITICAL | Decision #[N]: [old] | [new decision] | Client File ([filename]) |
| **Change Rejected** | - | [proposed change] | (rejected by user) | Safety Gate Review |
| **Terminology Added** | Low | - | [new term]: [definition] | Client File ([filename]) |
| **New Question Added** | - | - | "[new question text]" | Revealed by client input |

### Change Details
#### Update Round [N]
- **Source Document**: [client input filename]
- **Input Classification**: [Question Resolution / Change Request / Mixed]
- **Questions Resolved**: [N] of [total open]
- **Change Requests Applied**: [N] of [total detected]
- **Change Requests Rejected**: [N]
- **PRD Sections Updated**: [N] sections
- **New Questions Added**: [N]
- **Remaining Open Questions**: [N] Required, [N] Recommended
```

### 9.3 Change Type Categories

Use these change types in the table:

| Change Type | Risk | When to Use |
|:-----------|:-----|:------------|
| **Question Resolved** | Low | An Additional Question was answered |
| **Clarification** | Low | Minor clarification that doesn't change features |
| **Feature Updated** | Low | A PRD section was updated with new information |
| **Feature Extended** | Medium | Existing feature gained additional capability |
| **Feature Added** | Medium | A completely new feature was added |
| **Feature Replaced** | HIGH | An existing feature was swapped for another |
| **Feature Removed** | HIGH | An existing feature was deleted |
| **Permission Change** | HIGH | User role access was modified |
| **Behavior Change** | HIGH | Existing feature behavior was altered |
| **Decision Reversed** | CRITICAL | Client contradicted a previously confirmed decision |
| **Terminology Added** | Low | New term added to Terminology section |
| **Terminology Changed** | Low | Existing term definition updated |
| **New Question Added** | - | New question emerged from the input |
| **Change Rejected** | - | Proposed change was rejected during Safety Gate review |

---

## Step 10: Save Updated PRD

### 10.1 Save Strategy

Overwrite the same file at the same path. Do NOT create a new file.

**Rationale**: Version history is tracked within the Feature Change Log section. The filename uses the original creation date, and internal versioning (1.0 → 1.1 → 1.2) tracks evolution.

### 10.2 Verify Save

After saving, read the file back to verify:
- File is not empty
- Additional Questions section is properly formatted
- Feature Change Log has the new version entry
- No markdown formatting errors

---

## Step 11: Report Results

Output the following report:

```markdown
## PRD Update Complete

### Output
- **File**: `.claude-project/prd/[filename].md`
- **Version**: [old] → [new] (e.g., 1.0 → 1.1)
- **Source**: [client input filename]
- **Input Classification**: [Question Resolution / Change Request / Mixed]

### Questions Resolved: [N]
| # | Question | Answer |
|:-:|:---------|:-------|
| 1 | [Question text] | [Answer summary] |
| 2 | [Question text] | [Answer summary] |

### Change Requests: [N applied] / [N total]

#### Applied: [N]
| # | Type | Description | Risk | Sections Affected |
|:-:|:-----|:------------|:-----|:-----------------:|
| 1 | [REPLACE] | "X" → "Y" | HIGH | 4 |
| 2 | [ADD] | Feature Z | Medium | 2 |

#### Rejected: [N]
| # | Type | Description | Reason |
|:-:|:-----|:------------|:-------|
| 1 | [REMOVE] | Feature W | User rejected |

#### Deferred: [N]
| # | Type | Description | Action |
|:-:|:-----|:------------|:-------|
| 1 | [REVERSE] | Decision #3 | Added to questions for client re-confirmation |

### PRD Sections Updated: [N]
- **[Section name]**: [What changed]
- **[Section name]**: [What changed]

### Remaining Questions: [N]

#### Required: [N] remaining
| # | Question |
|:-:|:---------|
| 1 | [Question text] |

#### Recommended: [N] remaining
| # | Question |
|:-:|:---------|
| 1 | [Question text] |

### New Questions Added: [N]
| # | Question | Context |
|:-:|:---------|:--------|
| 1 | [New question] | [Why this emerged from the input] |

### Technical Section Impact
- [If Full PRD and entity/CRUD changes detected]:
  ⚠️ Changes affect entities or CRUD operations in Section 3/4.
  Technical sections (5-7: Schema, Permissions, System Design) may be outdated.
  Run `/generate-tech-prd --refresh [prd-path]` to regenerate technical sections.
- [If Feature PRD]: No technical sections to refresh (run /generate-tech-prd when ready)

### Next Steps
1. [If questions remain] Send remaining [N] questions to client for next round
2. [If all resolved] PRD finalized — ready for development or /generate-korean-prd
3. [If new questions] Collect answers for [N] new questions and run /update-prd again
4. [If changes rejected] Review rejected changes with client if needed
5. [If changes deferred] Await client re-confirmation on deferred items
6. [If tech refresh needed] Run `/generate-tech-prd` to update Schema/Permissions
```

---

## Error Handling

### File Not Found
```
Error: File not found at [path]
Please check the file path and try again.
Usage: /update-prd /path/to/client-answers.md
```

### Empty File
```
Error: The input file is empty.
Please provide a file with client answers.
```

### No PRD Found
```
Error: No PRD files found in .claude-project/prd/
Please run /generate-prd first to create a PRD.
```

### No Additional Questions Section
```
Warning: No "Additional Questions" section found in [filename].
This PRD may have been created manually or the section was removed.

Question Resolution mode is unavailable.
If the input contains Change Requests, they will still be processed via Safety Gate.
```

### All Questions Already Resolved (Q&A mode only)
```
All questions in [filename] are already resolved (Version [X.X]).

If you have scope changes or feature modifications, provide a change request file.
The input-classifier will auto-detect and route to Change Request mode.
```

### No Items Matched
```
Warning: Could not match any items from [filename] to the PRD.

No question answers matched and no change requests detected.

Open questions in PRD:
1. [Question 1]
2. [Question 2]
...

Please ensure the input file:
- References question numbers (Q1, Q2, etc.) OR
- Contains keywords related to the questions above OR
- Contains clear change requests (add/remove/replace/modify features)
```

### Input File is the PRD Itself
```
Error: The input file appears to be the PRD itself, not a client input file.
Please provide the client's answer or change request file, not the PRD.
Usage: /update-prd /path/to/client-input.md
```

### All Changes Rejected
```
All [N] proposed changes were rejected during Safety Gate review.
No modifications were made to the PRD.

Rejected changes:
1. [TAG] [description] — [reason]
2. [TAG] [description] — [reason]

The PRD remains at Version [X.X].
```

### Conflict with Confirmed Decision
```
⚠ Change conflicts with existing Confirmed Decision.

Change: [TAG] [description]
Conflicts with: Confirmed Decision #[N]
  "[decision text]" (confirmed in v[X.X])
  Source: [original source]

This has been flagged for user review during Safety Gate approval.
```

---

## Usage Examples

**Update PRD with client answers:**
```
/update-prd /Users/user/Documents/client-answers.md
```
→ input-classifier detects Q&A → Question Resolution mode

**Update PRD with scope changes:**
```
/update-prd /Users/user/Documents/scope-changes.md
```
→ input-classifier detects change requests → Safety Gate → Change Request mode

**Update PRD with mixed input (answers + changes):**
```
/update-prd /Users/user/Documents/client-feedback.txt
```
→ input-classifier detects mixed → Q&A first, then Safety Gate for changes

**Update PRD from various text formats:**
```
/update-prd /path/to/meeting-notes.pdf
/update-prd /path/to/client-email.txt
```

---

## Notes

- Each `/update-prd` run increments the minor version (1.0 → 1.1 → 1.2)
- The PRD filename does not change between updates — version history is in the Change Log
- Multiple rounds of updates are expected: generate → update → update → ... → complete
- All changes are strictly based on the client input file — no guessing or inference
- New questions may emerge from answers or change requests — this is normal and expected
- When all questions are resolved, the PRD is considered finalized
- The **input-classifier** skill auto-detects input type — users do not need to specify Q&A vs change request
- Change Requests go through **Safety Gate** (Impact Analysis → Diff Preview → Conflict Detection → Approval)
- HIGH/CRITICAL risk changes require explicit user approval before application
- Rejected changes are logged in the Change Log but not applied to the PRD
- The prd-manager agent can perform Safety Gate review independently via "review changes"
