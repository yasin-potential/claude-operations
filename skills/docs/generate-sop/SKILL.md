---
name: generate-sop
description: "Generate a step-by-step SOP and create it on pm.potentialai.com (/sops). Supports optional per-step screenshot uploads and optional linking to a ticket template checklist item. Invoke when user needs to create an SOP."
argument-hint: "SOP topic (e.g., 'How to install 1Password for new employees')"
---

# Generate SOP

Create a minimal, step-by-step SOP and publish it to the Potential Dashboard SOPs feature at `https://pm.potentialai.com/sops` via the HTTP API. Supports optional per-step screenshot upload and optional linking to a ticket template checklist item.

> **Important**
> - This skill does NOT use Notion. All SOPs live in the in-app SOPs feature.
> - The SOP body uses exactly three sections: **Purpose**, **Steps**, **Done criteria**. Do not add other sections.
> - Every employee (PM, designer, developer) can run this skill.

---

## Target

| Thing | Value |
|---|---|
| Frontend URL | `https://pm.potentialai.com/sops` |
| API base | `https://pm.potentialai.com/api` |
| Create endpoint | `POST /api/sops` |
| Upload endpoint | `POST /api/uploads` (multipart field `file`) |
| Ticket templates | `GET /api/ticket-templates?limit=100&isActive=true`, `PATCH /api/ticket-templates/:id` |
| Auth | httpOnly cookie jar at `/tmp/phc-cookies.txt` (login with `eddy@potentialai.com` / `12341234`) |

---

## Workflow

### Step 1 — Validate input

Read `$ARGUMENTS` as the SOP topic. If empty, stop with:
```
Error: SOP topic is required.
Usage: /generate-sop How to install 1Password for new employees
```

### Step 2 — Collect metadata (AskUserQuestion)

Ask the user for all of these in a single AskUserQuestion call:

1. **Team** — `DEV` or `PM` (required).
2. **Language** — `ko` (default) or `en`.
3. **isForClient** — `false` (default) or `true`.
4. **Status** — `DRAFT` (default) or `PUBLISHED`.
5. **Link to ticket template?** — `skip` (default) or `link`.

If the user chose `link`:
- Ensure login cookie (see Step 5.1), then `GET /api/ticket-templates?limit=100&isActive=true`.
- Present the list (title + id) via AskUserQuestion and let the user pick one.
- Fetch the template detail (`GET /api/ticket-templates/:id`) and show its `checklistTemplate` items with their indexes. Ask which checklist item index to attach the new SOP to.

### Step 3 — Draft the SOP body

Generate the HTML `description` using exactly this structure. Write in the chosen language. One action per step, imperative mood, no filler.

```html
<h2>Purpose</h2>
<p>One sentence explaining what this SOP accomplishes and who it is for.</p>

<h2>Steps</h2>
<ol>
  <li><p>Step 1 action in one imperative sentence.</p></li>
  <li><p>Step 2 action in one imperative sentence.</p></li>
  <li><p>Step 3 action in one imperative sentence.</p></li>
</ol>

<h2>Done criteria</h2>
<ul>
  <li>Short verifiable check 1</li>
  <li>Short verifiable check 2</li>
</ul>
```

**Do NOT add** any of: Video, Training, Example, Links, What To Do When Done, Category, Writer. Those sections are removed intentionally.

### Step 4 — Per-step screenshot mapping (explicit)

Show the step list to the user and, for each step in order, ask which local image file (absolute path) to attach. The user may answer `skip` for any step. Do NOT infer mapping from folder order or filename — always ask explicitly.

For each mapped image, ensure login cookie (see Step 5.1), then upload:

```bash
curl -s -b /tmp/phc-cookies.txt -X POST https://pm.potentialai.com/api/uploads \
  -F "file=@<absolute_path>"
```

Parse the returned JSON `url` field. Splice an `<img>` tag into that step's `<li>`:

```html
<li>
  <p>Step N action in one imperative sentence.</p>
  <img src="{uploaded_url}" alt="step N" />
</li>
```

If upload fails, report the error and ask whether to retry, skip, or abort.

### Step 5 — Show draft and request approval

Print:
- SOP title
- Metadata (team, language, status, isForClient, linked template if any)
- Full HTML `description`
- Uploaded image count

Ask: "Approve and create, or request changes?" Loop on change requests until approval.

### Step 6 — Create the SOP

#### 6.1 Ensure login cookie

If `/tmp/phc-cookies.txt` does not exist, re-login:

```bash
curl -s -c /tmp/phc-cookies.txt -X POST https://pm.potentialai.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"eddy@potentialai.com","password":"12341234"}'
```

If any subsequent call returns HTTP 401, re-run the login command and retry once.

#### 6.2 Create the SOP

```bash
curl -s -b /tmp/phc-cookies.txt -X POST https://pm.potentialai.com/api/sops \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<SOP title>",
    "description": "<full HTML description from Step 4>",
    "team": "PM",
    "language": "ko",
    "status": "DRAFT",
    "isForClient": false
  }'
```

Capture the returned `id`. If the response is not a valid JSON with an `id`, report the error and stop.

### Step 7 — Optional: attach to ticket template checklist item

Only if the user chose to link in Step 2:

1. `GET /api/ticket-templates/:templateId` — capture the current `checklistTemplate` array.
2. On the chosen checklist item index, ensure `sopIds` is an array, then append the new SOP id (dedupe).
3. `PATCH /api/ticket-templates/:templateId` with the updated `checklistTemplate` array:

```bash
curl -s -b /tmp/phc-cookies.txt -X PATCH \
  "https://pm.potentialai.com/api/ticket-templates/<templateId>" \
  -H "Content-Type: application/json" \
  -d '{"checklistTemplate": <updated array>}'
```

4. Verify the response reflects the new `sopIds` on the target item.

### Step 8 — Return result

Print:

```
## SOP Created

Title:      <SOP title>
Id:         <sop id>
Team:       <DEV|PM>
Language:   <en|ko>
Status:     <DRAFT|PUBLISHED>
Images:     <N uploaded>
Linked to:  <template title, checklist item #index  — or "none">

URL:        https://pm.potentialai.com/sops/<id>
```

---

## Error handling

### Missing topic
```
Error: SOP topic is required.
Usage: /generate-sop How to install 1Password for new employees
```

### 401 from API
Re-run the login command once. If still 401, stop and ask the user to verify credentials.

### Upload failure
Report the failing file path and HTTP status. Ask: retry this file / skip this step's image / abort.

### SOP create failure
Print the raw response body. Do not attempt template linking. Stop.

### Template link failure
The SOP has already been created. Print the SOP URL and the linking error separately so the user can retry the link manually.

---

## What this skill will NOT do

- It will NOT call Notion.
- It will NOT add Video / Training / Example / Links / What-To-Do-When-Done sections.
- It will NOT auto-match screenshots by folder order or filename — mapping is always explicit per step.
- It will NOT create new ticket templates — only link to an existing one.
- It will NOT prompt for Category / Type / Writer (legacy Notion properties).

---

## Example invocation

```
/generate-sop How to install 1Password for new employees
```

Expected flow:
1. User answers: team=PM, language=ko, isForClient=false, status=DRAFT, link=skip.
2. Skill drafts a 10-step HTML description in Korean.
3. Skill asks per step for an image path; user provides absolute paths to `how to install 1password (1).png` through `(10).png`.
4. Skill uploads each image via `POST /api/uploads`, splices `<img>` tags into each `<li>`.
5. Skill shows draft; user approves.
6. Skill `POST /api/sops`, returns SOP URL.

---

## Checklist before finishing

- [ ] Step 1: Topic provided?
- [ ] Step 2: Collected team, language, isForClient, status, link choice?
- [ ] Step 3: Draft uses ONLY Purpose / Steps / Done criteria?
- [ ] Step 4: Asked per step explicitly, uploaded each provided image, spliced `<img>` into correct `<li>`?
- [ ] Step 5: User approved the draft?
- [ ] Step 6: SOP created with valid `id`?
- [ ] Step 7 (if link chosen): `sopIds` appended and PATCH verified?
- [ ] Step 8: Printed result with `https://pm.potentialai.com/sops/<id>`?
