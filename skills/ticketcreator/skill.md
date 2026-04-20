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

## Size Estimation (Claude Code Adjusted)

All teams use Claude Code. Estimate in two steps:

### Step 1: Raw Estimate (without AI)

Estimate how long a developer would take **without** Claude Code (conservative baseline).

### Step 2: Apply Claude Code Coefficient

| Work Type | Coefficient | Examples |
|---|---|---|
| Pure Development | **× 1/5** | CRUD, UI changes, new feature, refactoring, migration |
| Integration / Debugging / Infra | **× 1/3** | External API integration, complex bug investigation, CI/CD, environment setup |

**Floor:** minimum **1 hour** regardless of calculation.

### Step 3: Determine Size and Due Date

`Adjusted Size = max(raw estimate × coefficient, 1)`

| Adjusted Size | Due Date | Action |
|---|---|---|
| 1–3h | Same day (D+0) | Single ticket |
| 4–6h | 1 day (D+1) | Single ticket |
| 7–9h | 1–2 days (D+1~D+2) | Single ticket |
| 10–27h | Split needed | Split into sub-tickets (each ≤ 9h) |
| 28h+ (≥4 days) | **Action Plan** | Action Plan Request ticket |

**Rules:**
- Calculate from today's date, skip weekends (Mon-Fri only)
- Bug/Config categories: bias toward Pure Development coefficient
- Integration/Requirement categories: bias toward Integration coefficient
- If user provides a due date, use it; otherwise always recommend one
- Show reasoning: `Raw: {N}h ({work type}) × 1/{coeff} = {adjusted}h → Size: {size} → Due: {YYYY-MM-DD}`

## Sub-ticket Splitting (10–27h)

If adjusted size exceeds **9 hours** but is under **28 hours**, split into sub-tickets:

1. Break the scope into independently trackable units, each **≤ 9 hours**
2. Each sub-ticket gets its own Title, Priority, Category, Due Date, Size, and Description
3. Titles should reflect sequential or logical grouping (e.g., `[1/3] ...`, `[2/3] ...`)
4. Due dates should be staggered across business days
5. Ask the user to confirm the split before generating

## Action Plan Request (28h+ / ≥4 business days)

If adjusted size is **28 hours or more**, the scope is too large for direct splitting. Do NOT create regular tickets. Instead:

1. **Create an Action Plan Request ticket** with:
   - Title prefixed with `[Action Plan]`
   - Due Date: **same day (D+0)** — the plan itself should be delivered today
   - Category: same as the original request's category
   - Priority: same as the original request

2. **Use the Action Plan Request template** (see below) instead of the category-specific template

3. **Inform the user**: explain that the total scope is 28h+, so an Action Plan Request ticket is generated instead. The developer will analyze the scope with Claude Code and create sub-tickets.

## Output Format

Output all fields needed for the ticket form:

```
**Title:** {concise title}
**URL:** {url or "N/A"}
**Priority:** {Low / Medium / High / Critical}
**Category:** {category}
**Due Date:** {YYYY-MM-DD}
**Size:** {1-9} — Raw: {N}h ({work type}) × 1/{coeff} = {adjusted}h
```

Then output the **Description** using the category-specific template below.

---

## Description Templates by Category

**All templates use the same core structure: Why / Situation / Problem / Expected (optional) / Test Checklist.**
- **Why**: Background and intent — why this ticket exists, who it affects. **Max 2 sentences.**
- **Situation**: Factual current state — what exists today, how it works. **Max 2 sentences.**
- **Problem**: What is wrong or missing in the current situation. **Max 2 sentences.**
- **Expected** *(optional)*: Observable target state after completion. Omit when the problem already implies an obvious solution. When included: **max 3 items, flat list, no nested bullets or bold sub-headers, no implementation prescriptions.**
- **Test Checklist**: Only the most important observable verifications. **Max 2 items.** Skip items that just restate Expected — include only verifications that add real value (e.g., regression risks, edge cases).

Solutions, fix approaches, and implementation details are **never** included — the assignee decides how to solve it.

## Brevity Principle

Tickets are for developers who scan, not read. Prefer short over complete. If a reader can infer it, cut it. Long tickets signal PM insecurity, not thoroughness.

### General

```
### Why
{Background and intent}

### Situation
{Current state}

### Problem
{What is wrong or missing}

### Expected
{Target state — omit if obvious from Problem}

### Test Checklist
- [ ] {Observable verification}
```

### Bug

```
### Why
{Who is affected, how it hurts them}

### Situation
1. {Steps to reproduce — start with the page/feature}

### Problem
{What the user actually sees}

### Expected
{What the user should see instead}

### Test Checklist
- [ ] {Observable verification}
```

### Change Request

```
### Why
{Who requested, business reason}

### Situation
{Current behavior}

### Problem
{What needs to change and why}

### Expected
{Target behavior — omit if obvious from Problem}

### Test Checklist
- [ ] {Observable verification}
```

### Requirement

```
### Why
{Business need, target users}

### Situation
{What the user cannot do today}

### Problem
{Gap or limitation}

### Expected
{User-facing capability after completion}

### Test Checklist
- [ ] {Observable verification}

### Out of Scope
{Explicitly excluded items, if any}
```

### Setup

```
### Why
{Why this setup is needed}

### Situation
{Current environment/tool state}

### Problem
{What is missing or blocking}

### Expected
{Target state after setup — omit if obvious}

### Test Checklist
- [ ] {Observable verification}
```

### Onboarding

```
### Why
{Who is being onboarded, role, timeline}

### Situation
{What access/resources they have today}

### Problem
{What is missing for them to start}

### Expected
{What access/resources they should have}

### Test Checklist
- [ ] {Observable verification}

### Resources
{Links, docs, credentials to provide}
```

### Integration

```
### Why
{Which systems, why integration is needed}

### Situation
{Current connection state}

### Problem
{What is not connected or working}

### Expected
{Integration outcome — omit if obvious}

### Test Checklist
- [ ] {Observable verification}
```

### Config

```
### Why
{Why this config change is needed}

### Situation
{Current configuration state}

### Problem
{What is misconfigured or missing}

### Expected
{Target configuration state — omit if obvious}

### Affected Environments
{Dev / Staging / Production}

### Test Checklist
- [ ] {Observable verification}
```

### Team

```
### Why
{Why this team matter needs attention}

### Situation
{Current team state or process}

### Problem
{What is not working}

### Expected
{Target team state or process — omit if obvious}

### Test Checklist
- [ ] {Observable verification}
```

### Action Plan Request

Used automatically when complexity exceeds 2 business days (16h).

```
### Why
{What the user/PM originally requested and why}

### Situation
{Current state relevant to the request}

### Problem
{Why this cannot be done as a single ticket}

### Expected Deliverables
- Action plan broken into **sub-tickets** (each ≤ 9 hours, Claude Code adjusted)
- Each sub-ticket must have: Title, Priority, Category, Due Date, Size (1-9), Test Checklist
- Sub-tickets should be independently verifiable by PM

### Constraints
{Deadlines, dependencies on other teams/features, environment requirements}

### Test Checklist
- [ ] Action plan delivered by end of day
- [ ] Each sub-ticket is ≤ 9 hours (Size 1-9)
- [ ] Sub-tickets cover the full scope of the original request
- [ ] Each sub-ticket has an observable Test Checklist
```

---

## Delivery

By default, output the ticket as **text only** in the conversation. After presenting the ticket, ask:

> **API로 직접 올릴까요?**

Only proceed with API upload if the user confirms.

## API Upload Flow (optional)

Only execute when the user explicitly requests upload.

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
| Size | `size` | Integer 1-9 (estimated hours, Claude Code adjusted) |
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
2. **Simple, intuitive English** — Write for a reader whose English is a second language. Short sentences, common words, no jargon or complex grammar. Prefer "user cannot see X" over "X is not rendered in the interface".
3. **Korean UI text** — Include as-is with English translation in parentheses
3. **No implementation details** — Zero file paths, code, variable names, function names
4. **No solution prescriptions** — Do NOT propose fixes: no column additions, endpoint specs, sub-tabs, progress bars, UI structures, algorithm choices. The assignee decides how to solve it.
5. **Observable behavior only** — Describe what the user sees, not what the code does
6. **Problem-focused titles** — Titles describe the problem/situation, not the solution. ❌ "Add category column to Project" → ✅ "Projects cannot be filtered by type"
7. **Why / Situation / Problem / Expected structure** — All description templates follow this structure plus Test Checklist. Expected is optional — omit when Problem implies an obvious solution.
7a. **Brevity limits** — Why ≤ 2 sentences, Situation ≤ 2 sentences, Problem ≤ 2 sentences, Expected ≤ 3 flat items (no nested bullets/bold sub-headers), Test Checklist ≤ 2 items (only high-value verifications, not restatements of Expected)
8. **Infer fields** — Determine Priority and Category from context; confirm if ambiguous
9. **Scope check** — Suggest splitting if request contains multiple independently trackable units
10. **Text-first delivery** — Output ticket as text in conversation by default. API upload is optional — only when user requests it
