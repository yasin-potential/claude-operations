---
name: ticketcreator
description: Generate structured project tickets with category-specific templates. Outputs Title, URL, Priority, Category, Due Date, and Description.
user-invocable: true
---

# ticketcreator — Unified Ticket Generator

Generate a structured project ticket in English from the user's description.

## Role

You are a **PM writing a ticket for developers**. Strict role separation:

- **PM scope (include):** Context, observable problem/situation, expected behavior, acceptance criteria, test checklist
- **Developer scope (never include):** File paths, line numbers, code references, implementation details, conditions/logic, root cause analysis, solution approach

## Input

The user provides a description of the issue, request, or task. Before generating, ensure you have:
1. Enough information to determine the **Category**
2. A clear understanding of the **observable problem or need**
3. The **URL** if applicable

If any critical information is missing, ask before generating.

## Scope Validation

Before generating, assess whether the request contains multiple independently trackable work items:
- Each ticket should represent a unit whose progress (not started / in progress / done) can be monitored individually
- If a request bundles multiple trackable units, suggest splitting into separate tickets
- Example: "Add video beauty filter" → multiple trackable units → suggest: "Adjust video brightness to 120%" + "Add skin smoothing filter (20%) to home screen"
- Ask the user to confirm the split before generating

## Categories

`General` · `Bug` · `Change Request` · `Requirement` · `Setup` · `Onboarding` · `Integration` · `Config` · `Team`

## Due Date Estimation

All teams use Claude Code, so estimate aggressively. Always recommend a due date based on complexity:

| Complexity | Duration (business days) | Criteria |
|---|---|---|
| Trivial | Same day (D+0) | Config change, text fix, simple bug with clear cause |
| Small | 1 day (D+1) | Single API/screen change, straightforward feature addition |
| Medium | 2 days (D+2) | Multi-file coordination, new feature module, DB migration |
| Large | 3+ days → **Action Plan** | Cross-module feature, schema redesign, multi-service integration |

**Rules:**
- Calculate from today's date, skip weekends (Mon-Fri only)
- Bug/Config categories: bias toward Trivial/Small
- Integration/Requirement categories: bias toward Medium+
- If user provides a due date, use it; otherwise always recommend one
- Show reasoning: `Complexity: {level} → Due: {YYYY-MM-DD} ({N} business days)`

## Action Plan Request (>2 business days / 16h)

If estimated work exceeds **2 business days (16 hours)** — i.e., complexity is **Large (3+ days)** — do NOT create a regular ticket. Instead:

1. **Create an Action Plan Request ticket** with:
   - Title prefixed with `[Action Plan]`
   - Due Date: **same day (D+0)** — the plan itself should be delivered today
   - Category: same as the original request's category
   - Priority: same as the original request

2. **Use the Action Plan Request template** (see below) instead of the category-specific template

3. **Inform the user**: explain that the request is estimated at 3+ days, so an Action Plan Request ticket is generated instead. The developer will analyze the scope with Claude Code and create daily sub-tickets.

## Output Format

Output all fields needed for the ticket form:

```
**Title:** {concise title}
**URL:** {url or "N/A"}
**Priority:** {Low / Medium / High / Critical}
**Category:** {category}
**Due Date:** {YYYY-MM-DD}
**Complexity:** {Trivial/Small/Medium/Large} → {N} business days
```

Then output the **Description** using the category-specific template below.

---

## Description Templates by Category

### General

```
### Context
{Background and purpose}

### Details
{What needs to be done or communicated}

### Acceptance Criteria
- [ ] {Criterion}
```

### Bug

```
### Steps to Reproduce
1. {Step — start with the page/feature where the bug occurs}

### Current Behavior
{What actually happens — observable only}

### Expected Behavior
{What should happen instead}

### Test Checklist
- [ ] {Verification}
```

### Change Request

```
### Context
{Why this feature exists, who uses it, why change is needed}

### Current Situation
{What is the current state — observable behavior}

### Expected Behavior
{Numbered sections with bold headers per distinct change}

### Test Checklist
- [ ] {Verification per behavior change}
```

### Requirement

```
### Context
{Business need, target users, motivation}

### Requirement
{What the new feature should do — user-facing description}

### Acceptance Criteria
- [ ] {Criterion}

### Out of Scope
{Explicitly excluded items, if any}
```

### Setup

```
### Context
{What needs to be set up and why}

### Scope
{Systems/tools/environments involved}

### Steps
1. {Step}

### Done Criteria
- [ ] {Verification}
```

### Onboarding

```
### Context
{Who is being onboarded, role, timeline}

### Tasks
- [ ] {Task}

### Resources
{Links, docs, credentials to provide}
```

### Integration

```
### Context
{Which systems, why integration is needed}

### Scope
{Data flow, endpoints, services}

### Requirements
{What the integration should achieve}

### Test Checklist
- [ ] {Verification}
```

### Config

```
### Context
{What needs to be configured and why}

### Changes
{Current state → Desired state}

### Affected Environments
{Dev / Staging / Production}

### Verification
- [ ] {Confirmation}
```

### Team

```
### Context
{What team matter needs attention}

### Details
{Roles, responsibilities, process changes}

### Action Items
- [ ] {Action}
```

### Action Plan Request

Used automatically when complexity exceeds 2 business days (16h).

```
### Context
{Background: what the user/PM originally requested and why}

### Scope Summary
{High-level description of what needs to be done — PM perspective, no implementation details}

### Constraints
{Deadlines, dependencies on other teams/features, environment requirements}

### Expected Deliverables
- Action plan broken into **daily sub-tickets** (max 1 business day each, ≤8h)
- Each sub-ticket must have: Title, Priority, Category, Due Date, Acceptance Criteria
- Sub-tickets should be independently verifiable by PM

### Acceptance Criteria
- [ ] Action plan delivered by end of day
- [ ] Each sub-ticket is ≤1 business day of work
- [ ] Sub-tickets cover the full scope of the original request
- [ ] Each sub-ticket has clear, observable acceptance criteria
```

---

## API Upload Flow

After generating the ticket output, ask the user to confirm before uploading.

### Step 1: Authenticate

```bash
curl -s -c /tmp/phc-cookies.txt -X POST https://pm.potentialai.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eddy@potentialai.com","password":"12341234"}'
```

### Step 2: Resolve Project

Fetch the project list and match by name:
```bash
curl -s -b /tmp/phc-cookies.txt "https://pm.potentialai.com/api/projects"
```

- If the user specified a project name → match from list
- If not specified → show project list and ask the user to choose
- Extract `id` and `name` from the matched project

### Step 3: Resolve Assignee from Project Memory

**Never use a hardcoded assignee default.** Instead:

1. Read the current project's memory index: `C:\Users\vhxj3\.claude\projects\{encoded-cwd}\memory\MEMORY.md`
2. Look for an entry tagged `team` or `assignees` (e.g., `team_members.md`). It should contain a table of team members with their roles and PM tool user IDs.
3. Based on the ticket's **category**, pick the assignee:
   - **Dev categories** (Bug, Change Request, Requirement, Integration, Config) → project's **Lead Developer**
   - **PM categories** (General, Team, Onboarding, Setup) → project's **PM**
4. If the project memory has no team file, or the needed role is missing:
   - Ask the user who to assign (show the project's team members from the API if available)
   - After the user answers, **save the answer to project memory** as a `team` memory so future tickets don't need to ask
5. The user can always override the resolved assignee before upload

### Step 4: Confirm with User

Use the resolved project name in the confirmation:

> **'{프로젝트이름}' 티켓에 올릴까요?**

Never auto-upload without this confirmation.

### Step 5: Create Ticket

```bash
curl -s -b /tmp/phc-cookies.txt -X POST \
  "https://pm.potentialai.com/api/tickets/project/{projectId}" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

### Field Mapping (Skill Output → API Body)

| Skill Output | API Field | Transformation |
|---|---|---|
| Title | `title` | As-is |
| URL | `url` | As-is (omit if "N/A") |
| Priority | `priority` | Uppercase + `Critical` → `URGENT` |
| Category | `category` | Uppercase + spaces to `_` (e.g., `Change Request` → `CHANGE_REQUEST`) |
| Due Date | `dueDate` | As-is (YYYY-MM-DD) |
| Description | `description` | Convert markdown to HTML (see below) |
| — | `assigneeIds` | Resolved from project memory (see Step 3). Never hardcoded. |

### Priority Mapping

| Skill Output | API Value |
|---|---|
| Low | `LOW` |
| Medium | `MEDIUM` |
| High | `HIGH` |
| Critical | `URGENT` |

### Category Mapping

| Skill Output | API Value |
|---|---|
| General | `GENERAL` |
| Bug | `BUG` |
| Change Request | `CHANGE_REQUEST` |
| Requirement | `REQUIREMENTS` |
| Setup | `SETUP` |
| Onboarding | `ONBOARDING` |
| Integration | `INTEGRATION` |
| Config | `CONFIG` |
| Team | `TEAM` |

### Description: Markdown → HTML Conversion

Convert the description template output to HTML before sending:
- `### Heading` → `<h3>Heading</h3>`
- `- [ ] item` → `<ul><li>☐ item</li></ul>` (group consecutive items)
- `1. step` → `<ol><li>step</li></ol>` (group consecutive items)
- `{text}` → `<p>text</p>` (plain paragraphs)
- `**bold**` → `<strong>bold</strong>`
- Line breaks between sections → preserved with `<br>`

### Post-Upload

On success, display:
```
✅ Ticket created successfully!
🔗 https://pm.potentialai.com/projects/{projectId}/tickets
```

On failure (e.g., 401), re-authenticate and retry once. If still failing, show the error and the curl command for manual execution.

---

## Rules

1. **English only** — All ticket content in English
2. **Korean UI text** — Include as-is with English translation in parentheses
3. **No implementation details** — Zero file paths, code, variable names, function names
4. **Observable behavior only** — Describe what the user sees, not what the code does
5. **Infer fields** — Determine Priority and Category from context; confirm if ambiguous
6. **Scope check** — Suggest splitting if request contains multiple independently trackable units
7. **Always confirm before upload** — Never auto-upload; always show project name and ask for confirmation
