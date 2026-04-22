---
name: generate-proposal
description: Generate interactive HTML slide proposals (PPT-style). Supports `--language korean|english` (default `korean`). Korean mode = mixed (left-column titles stay English, only project-content variables translate).
argument-hint: [--language korean|english]
---

# Generate Proposal - Client Proposal HTML Generator

Generate professional client proposals as **interactive HTML slide presentations (PPT-style)**.

Language is controlled by the `--language` flag (see Step 1). `english` produces a fully-English deck. `korean` produces a **mixed Korean deck** — left-column section titles and all hardcoded boilerplate remain English, only the project-content `{{PLACEHOLDER}}` variables are filled in Korean. See "Mixed Korean Mode" section below for the exact scope.

---

## Step-by-Step Generation Process

### Step 1: Gather Information

#### 1a. Parse `$ARGUMENTS` for the `--language` flag

Syntax: `/generate-proposal [--language korean|english]`

- Accepted values: `korean` | `english` (full words only).
- If the flag is absent, set `LANGUAGE = korean`.
- If the flag is present with an unrecognized value, stop and reply:
  > Unknown `--language` value. Use `--language korean` or `--language english`. Default is `korean` when omitted.
- Store the resolved `LANGUAGE` for use in Step 3 and Step 4.

#### 1b. Ask the user for required inputs

Ask for these **required** inputs (if not already provided). Do **not** re-ask about language — it comes from the flag.

| Input | Question | Default |
|-------|----------|---------|
| Client name | "What is the client company name?" | — |
| Project name | "What is the project title?" | — |
| Total cost | "What is the total project cost (USD)?" | — |
| Key features | "List the key features of the project" | — |
| Service flow | "Describe the user/service flow steps" | — |

**Optional** (use your best judgment to fill these if user doesn't provide):
- Admin features, Our comments, Tech stack, Timeline
- Milestone breakdown (default: 30/30/40 split)
- MVP vs Post-MVP feature grouping
- Team composition for FAQ

### Step 2: Copy Template

```bash
cp templates/proposal-template.html ".claude-project/proposals/[Proposal] [PROJECT_NAME].html"
```

**Naming**: `[Proposal] Artlive.html`

#### Step 2b: Rewrite the `<base href>` tag

The template uses `<base href="../../../../../../../">` so that image paths (`src=".claude/resources/..."`) resolve from project root when the template is previewed standalone from its own location (7 dirs deep inside `.claude/operation/skills/...`).

After copy to `.claude-project/proposals/` (which is 2 dirs deep from project root), you MUST rewrite the base href:

```bash
sed -i.bak 's|<base href="\.\./\.\./\.\./\.\./\.\./\.\./\.\./">|<base href="../../">|' ".claude-project/proposals/[Proposal] [PROJECT_NAME].html" && rm ".claude-project/proposals/[Proposal] [PROJECT_NAME].html.bak"
```

Or use the Edit tool to perform the same replacement. Skipping this step causes all images to 404 in the output HTML.

### Step 3: Set Language

Branch on the `LANGUAGE` resolved in Step 1a:

- **`LANGUAGE = english`** → keep `<html lang="en">` on line 2. Fill every `{{PLACEHOLDER}}` in English.
- **`LANGUAGE = korean` (mixed mode)** → **keep `<html lang="en">`** on line 2. Do NOT change it to `ko`. The template's `data-lang="ko"` CSS would swap hardcoded boilerplate to Korean, which mixed mode intentionally avoids. Do not edit any hardcoded English text in the template. Only the project-content variables in Step 4 are filled in Korean — see "Mixed Korean Mode" section below for the exact list.

### Step 4: Replace All Variables

Replace every `{{PLACEHOLDER}}` with project-specific content. See **Variables Reference** below.

In mixed Korean mode (`LANGUAGE = korean`), fill variables according to the "Mixed Korean Mode" table below — some variables translate to Korean, others stay English.

---

## Mixed Korean Mode — What Translates vs Stays English

When `LANGUAGE = korean`, the template file stays untouched except for the `{{PLACEHOLDER}}` variable substitutions. Apply the following rules:

### Translates to Korean (project-content variables)

Fill these with Korean text in Korean mode, English text in English mode:

| Variable | Example (Korean mode) |
|----------|----------------------|
| `{{FEATURES_LIST}}` | `<li>진단 설문 및 결과 리포트</li>` |
| `{{SERVICE_FLOW_TITLE}}` | `기본 진단-상담 플로우` |
| `{{SERVICE_FLOW_STEPS}}` | `<li>부모가 진단 설문을 완료합니다</li>` |
| `{{ADMIN_FEATURES}}` | `<div class="pill-badge">사용자 관리</div>` |
| `{{OUR_COMMENT_TITLE}}` | `개선 제안 2가지` |
| `{{OUR_COMMENTS}}` | `<li>MVP에서는 UX를 단순화해야 합니다</li>` |
| `{{MVP_FEATURES}}` | `<li>Toss 결제 연동</li>` |
| `{{POST_MVP_FEATURES}}` | `<li>화상 상담 연동</li>` |
| `{{POST_MVP_FEATURES_2}}` | `<li>전문가별 맞춤 견적</li>` |
| `{{TEAM_MEMBERS_FAQ}}` | `<li>경력 10년 PM</li>` |
| `{{MILESTONE_1_NAME}}` ~ `{{MILESTONE_3_NAME}}` | `프로젝트 착수 (계약 체결)` |
| `{{TIMELINE}}` | `3개월` |

Also translate the following hardcoded slide-body blocks (title stays English per "never edit left-column titles" rule — only the card body content translates):

- **Our Process (Slide 7)** — translate the 4 step cards: Step-number pill (`Step 01` → `단계 01`), step name h3 (`Discovery & Research` → `발굴 & 리서치`; `Design & Development` → `디자인 & 개발`; `Testing & Deployment` → `테스트 & 배포`; `Maintenance & Growth` → `유지보수 & 성장`), and the step description paragraph. Left-column title `Our / Process` stays English.
- **What is Behance? (Slide 10)** — translate the right-column body: the "Behance is the Biggest Portfolio platform…" lead paragraph, the "Why it's difficult to be featured?" sub-heading (→ `Featured 선정이 어려운 이유`), and its bullet ("features only 1 project a week" → `주 1개 프로젝트만 Featured로 선정`). Left-column title `What is / Behance?` stays English. The word "Behance" itself stays English everywhere (brand name); "Featured" may stay English as a loanword, as it's commonly used in Korean design parlance.
- **Featured on Behance (Slide 11)** — card bodies stay English (they're images + generic "Check Out" CTA). Left-column title `Featured 4 Times on Behance` stays English. When generating, collect the 4 Behance gallery URLs from the user and wire each card to its specific URL; fall back to the company profile `https://www.behance.net/potentipotenti` if a specific URL is not provided.
- **To Client FAQ (Slide 14)** — translate every Q (h3) and A (p/ul body) in the 5 glass-card FAQ stack: agreement timing, project duration, server hosting cost, team composition, extra cost policy. Left-column title `To / Client` stays English. Team-composition bullets (e.g., `10 year experienced PM` → `경력 10년 PM`) follow the pattern in the Korean example.
- **Our Pricing (Slide 15)** — translate table headers (`Milestone` → `마일스톤`, `Payment Due` → `지급 시점`, `Amount (USD)` → `금액 (USD)`), row labels (`Project Kickoff (Contract Signed)` → `프로젝트 착수 (계약 체결)`, `After Delivery` → `납품 완료 후`, `Total Project Cost` → `총 프로젝트 비용`), and the section header `Only Design` → `디자인 전용`. Left-column title `Our / Pricing` and the `PROJECT BASED` pill badge stay English (they sit in the left column). All dollar amounts and percentages stay as-is.

### Stays English (always, in both modes)

Do not translate these. In Korean mode leave them in English:

- `{{CLIENT_NAME}}` — e.g., `Artlive`, `ChildSocial`
- `{{PROJECT_NAME}}` — e.g., `ChildSocial MVP`
- All currency amounts (`{{TOTAL_COST}}`, `{{MILESTONE_N_AMOUNT}}`, `{{MVP_AMOUNT}}`, `{{POST_MVP_AMOUNT}}`, `{{POST_MVP_2_AMOUNT}}`, `{{MILESTONE_N_PERCENT}}`) — keep USD format like `$20,000`, `30%`.

### Hardcoded template content (never edit)

The following are hardcoded in `templates/proposal-template.html` and must stay **exactly as-is** in both modes:

- All left-column section titles: "Who We are", "Client Request", "Table of Content", "Our Portfolio", "Our Process", "Tech Stack", "Our Clients", "Expert Team", "Clutch Reviews", "Contact Us", "Thank You", etc.
- The Who-We-Are agency description ("We're a Design and Development focused agency…")
- Every portfolio case-study slide (DiaFit, Stockify, PET, Mentora, Agrilo) — titles, descriptions, metrics
- Behance explanation, Featured Projects labels
- All Clutch review cards
- All team section headers and bio text
- All Contact Us office blocks
- Button labels ("Visit Website", "Learn more")
- Chapter numbers ("Chapter - 1", "Chapter - 2", …)
- Stats on the cover / Who-We-Are slides ("40+ Team member", "100+ Successful Project", "3+ Years of Experience")

### Step 5: Embed Images as Base64

Read each image file and convert to inline base64 for self-contained HTML:

```html
<img src="data:image/png;base64,{BASE64_DATA}" alt="Project Name" class="w-full h-auto object-contain" />
```

Shared brand and portfolio assets live in the Tier 1 resources folder at `.claude/resources/` (path relative to project root). Only proposal-specific assets (testimonial portraits) remain inside the skill at `images/`.

- **Cover image**: **ALWAYS** use `.claude/resources/case-studies/projects/cover.png` as the Slide 1 hero/cover image (the main dashboard card). Never use any other project image for the cover slide.
- **Portfolio images**: Read each project PNG from `.claude/resources/case-studies/projects/` and embed inline
- **Featured project images**: Read from `.claude/resources/case-studies/projects/featured-[1-4].png` for the Behance Featured Projects slide
- **Team images**: Read from `.claude/resources/brand/team/` — only include when names are specified in the request
- **Tech stack icons**: Read from `.claude/resources/brand/tech-stack/[category]/` and embed inline
- **Client logos**: Read from `.claude/resources/case-studies/client-logos/` and embed inline
- **Office icons**: Read from `.claude/resources/brand/offices/` for Contact slide
- **Testimonial portraits**: Read from `images/clutch-reviewer/` (skill-local) and embed inline
- **Project name = image filename** (strip the `.png` extension)

### Step 6: Validate

Run this to confirm no unreplaced placeholders remain:

```bash
grep -c '{{' ".claude-project/proposals/[Proposal] [PROJECT_NAME].html"
```

Expected: `0`

### Step 7: Publish — share as HTTPS URL

Two paths; pick whichever fits your workflow.

#### Prerequisite: bundle the HTML + assets

Both paths need the bundle folder. It's what gets uploaded.

```bash
python3 scripts/bundle-for-netlify.py ".claude-project/proposals/[Proposal] [PROJECT_NAME].html"
```

Produces a sibling folder `.claude-project/proposals/[Proposal] [PROJECT_NAME]-bundle/` with:
- `index.html` — the HTML with `<base>` stripped and every `src="..."` rewritten to `assets/<original-subpath>`
- `assets/` — every referenced image/svg copied over, preserving its subpath so filename collisions are impossible

The script HTML-decodes entities (`&amp;` → `&`) before filesystem lookups so project-image filenames with `&` in them resolve correctly. Expected bundle size: ~10–30MB.

#### Path A — CLI (recommended, one command)

One-time setup (per machine, per teammate):

```bash
npm i -g netlify-cli
netlify login   # opens browser, authorize once
```

Then deploy in one command. `scripts/publish.sh` runs the bundler first, then `netlify deploy`:

```bash
bash scripts/publish.sh ".claude-project/proposals/[Proposal] [PROJECT_NAME].html"
# production (stable URL):
# → https://<site-name>.netlify.app

# or a draft preview URL:
bash scripts/publish.sh ".claude-project/proposals/[Proposal] [PROJECT_NAME].html" --draft
```

First run per bundle folder is interactive — netlify-cli asks whether to create a new site or link to an existing one. Pick "Create & configure a new site" for a fresh deck; pick "Link this directory to an existing site" to redeploy updates to the same URL.

#### Path B — Netlify Drop (no CLI, no login)

1. Open https://app.netlify.com/drop in a browser.
2. Drag the **entire bundle folder** onto the drop zone.
3. Wait ~10s. Netlify returns an HTTPS URL like `proposal-childsocial-abc123.netlify.app`.
4. Send that URL to the client.

Fastest for ad-hoc one-offs. Each drop = new URL unless you later claim the site to an account.

---

## Variables Reference (26 total)

### Basic Info

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{CLIENT_NAME}}` | text | Client company name | `Artlive` |
| `{{PROJECT_NAME}}` | text | Project title | `Expert Artwork Appraisal Platform` |
| `{{TIMELINE}}` | text | Project duration | `3 months` |

### Client Request (Chapter 02)

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{FEATURES_LIST}}` | HTML `<li>` | Key features list | `<li>Stripe Integration</li>` |
| `{{SERVICE_FLOW_TITLE}}` | text | Title for service flow diagram | `Basic Appraisal Flow` |
| `{{SERVICE_FLOW_STEPS}}` | HTML `<li>` | Numbered flow steps | `<li>Customer searches Expert</li>` |
| `{{ADMIN_FEATURES}}` | HTML `<div>` | Admin dashboard features (pill-badge) | `<div class="pill-badge">User Management</div>` |
| `{{OUR_COMMENT_TITLE}}` | text | Title for comments section | `2 things to IMPROVE` |
| `{{OUR_COMMENTS}}` | HTML `<li>` | Improvement suggestions | `<li>Simplify UX for MVP</li>` |

### Pricing - Milestone Based (Chapter 10, Slide 31)

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{TOTAL_COST}}` | text | Total project cost | `$20,000` |
| `{{MILESTONE_1_NAME}}` | text | Milestone 1 name | `Project Kickoff (Contract Signed)` |
| `{{MILESTONE_1_PERCENT}}` | text | Milestone 1 percentage | `30%` |
| `{{MILESTONE_1_AMOUNT}}` | text | Milestone 1 dollar amount | `$6,000` |
| `{{MILESTONE_2_NAME}}` | text | Milestone 2 name | `After Design Approval` |
| `{{MILESTONE_2_PERCENT}}` | text | Milestone 2 percentage | `30%` |
| `{{MILESTONE_2_AMOUNT}}` | text | Milestone 2 dollar amount | `$6,000` |
| `{{MILESTONE_3_NAME}}` | text | Milestone 3 name | `After Development Completed` |
| `{{MILESTONE_3_PERCENT}}` | text | Milestone 3 percentage | `40%` |
| `{{MILESTONE_3_AMOUNT}}` | text | Milestone 3 dollar amount | `$8,000` |

### Pricing - Feature Based (Chapter 10, Slide 32)

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{MVP_FEATURES}}` | HTML `<li>` | MVP feature list | `<li>Photo/Video Only</li>` |
| `{{MVP_AMOUNT}}` | text | MVP cost (can differ from TOTAL_COST) | `$20,000` |
| `{{POST_MVP_FEATURES}}` | HTML `<li>` | Post-MVP group 1 features | `<li>Virtual Call</li>` |
| `{{POST_MVP_AMOUNT}}` | text | Post-MVP group 1 cost | `$3,000` |
| `{{POST_MVP_FEATURES_2}}` | HTML `<li>` | Post-MVP group 2 features | `<li>Expert Quote</li>` |
| `{{POST_MVP_2_AMOUNT}}` | text | Post-MVP group 2 cost | `$5,000` |

### FAQ (Slide 30)

| Variable | Type | Description | Example |
|----------|------|-------------|---------|
| `{{TEAM_MEMBERS_FAQ}}` | HTML `<li>` | Team composition for FAQ | `<li>10 year experienced PM</li>` |

---

## Common Pitfalls

1. **`{{MVP_AMOUNT}}` vs `{{TOTAL_COST}}`**: These are different variables on different slides. `TOTAL_COST` goes on the milestone-based pricing slide (slide 31). `MVP_AMOUNT` goes on the feature-based pricing slide (slide 32). They may have the same value but they can also differ.

2. **Admin features use `<div>` not `<li>`**: `{{ADMIN_FEATURES}}` uses `<div class="pill-badge">` elements, not `<li>` elements like all other list variables.

3. **HTML entities**: Use `&amp;` for `&` in HTML content (e.g., `Design &amp; Development`).

4. **Nested lists**: `{{OUR_COMMENTS}}` should contain flat `<li>` items, not nested `<ul>` structures.

5. **Logo SVG**: The logo is defined once as a `<symbol>` at the top of the template and referenced via `<use href="#potential-logo"/>` across all slides. Do not modify individual logo references.

6. **Vertical centering**: Slides use `justify-content: center` to vertically center content. Do NOT add `flex:1` to the main content div inside a slide (it fills the full height, defeating centering). Do NOT add `padding-top` to offset for the logo — the logo is absolutely positioned.

7. **Title position**: All section titles (`title-line1` / `title-line2`) must be placed at the **top** of the slide content in their own wrapper div (`margin-bottom:24px`), with content below. Do NOT place titles in a left-right flex layout next to content.

---

## Template Structure (Slides)

| # | Slide | Type | Variables Used |
|---|-------|------|----------------|
| 1 | Cover | PROJECT | `CLIENT_NAME` |
| 2 | Table of Contents | BOILERPLATE | — |
| 3 | Who We Are | BOILERPLATE | — |
| 4 | Client Request - Features | PROJECT | `PROJECT_NAME`, `FEATURES_LIST` |
| 5 | Client Request - Flow | PROJECT | `SERVICE_FLOW_TITLE`, `SERVICE_FLOW_STEPS` |
| 6 | Client Request - Admin | PROJECT | `ADMIN_FEATURES` |
| 7 | Our Comment | PROJECT | `OUR_COMMENT_TITLE`, `OUR_COMMENTS` |
| 8 | Our Process | BOILERPLATE | — |
| 8+N | **Portfolio Projects (1 slide per project image)** | **AUTO-GENERATED** | — |
| — | What is Behance? | BOILERPLATE | — |
| — | Featured Projects | BOILERPLATE | — |
| — | Our Clients | BOILERPLATE | — |
| — | Expert Team | BOILERPLATE | — |
| — | Project Team | PROJECT | Team member names/images |
| — | Tech Stack | BOILERPLATE | — |
| — | Clutch Reviews | BOILERPLATE | — |
| — | To Client FAQ | PROJECT | `TIMELINE`, `TEAM_MEMBERS_FAQ` |
| — | Pricing - Milestones | PROJECT | `TOTAL_COST`, `MILESTONE_1/2/3_*` |
| — | Pricing - Feature Based | PROJECT | `MVP_FEATURES`, `MVP_AMOUNT`, `POST_MVP_*` |
| — | Contact Us | BOILERPLATE | — |
| — | Thank You | BOILERPLATE | — |

> **Note**: Slide numbers after Portfolio are dynamic because the total number of portfolio slides depends on how many images exist in `.claude/resources/case-studies/projects/`.

---

## Boilerplate Sections (Fixed Content)

These sections are pre-filled in the template. Do NOT modify unless updating company info:

- **Who We Are** — Company stats (40+ team, 100+ projects, 3+ years)
- **Our Process** — 4-step workflow (Discovery → Design → Testing → Maintenance)
- **Portfolio** — DiaFit, Stockify, PET, Mentora, Agrilo (5 projects × 2 slides each)
- **Behance** — Featured explanation + 2×2 grid (images from `.claude/resources/case-studies/projects/featured-[1-4].png`)
- **Clients** — Client logo grid (images from `.claude/resources/case-studies/client-logos/`)
- **Expert Team** — Leadership, Design (6+3), Full-Stack (6+2), Backend, Mobile & QA
- **Tech Stack** — 5-column technology grid (icons from `.claude/resources/brand/tech-stack/`)
- **Testimonials** — 4 Clutch review cards (portraits from `images/clutch-reviewer/`)
- **Contact** — 3 office locations (icons from `.claude/resources/brand/offices/`)
- **Thank You** — Closing slide

---

## Brand Guidelines

> **Brand guidelines:** See `.claude/base/brand/BRAND_GUIDELINES.md` for the canonical color palette, typography, and logo rules.

This document uses the **Dark Theme** palette with the following proposal-specific overrides:

| Element | Value | CSS Variable |
|---------|-------|--------------|
| **Accent** | `#EBFE5B` (Lime Green) | `--accent` |
| Gradient Border | `linear-gradient(135deg, rgba(98,77,255,0.4), rgba(235,254,91,0.4))` | — |

### Layout

| Property | Value |
|----------|-------|
| Orientation | 16:9 Full Screen (100vw × 100vh) |
| Slide Padding | `56px 64px` |
| Content Alignment | Vertically centered (`justify-content: center`) |
| Logo | Fixed top-left (`position: absolute; top: 28px; left: 40px`) |
| Title Style | Line 1: White (400wt) + Line 2: Lime Green (700wt) |
| Title Position | **Always at the TOP** of the slide content, never side-by-side |
| Assets Source | https://potentialai.com |

### Title Layout Rule

**All slide titles MUST be placed at the top of the content, NOT in a left-right (side-by-side) layout.**

Correct pattern:
```html
<div style="margin-bottom:24px;">
  <div class="title-line1" style="font-size:48px;">Section</div>
  <div class="title-line2" style="font-size:48px;">Title</div>
</div>
<div>
  <!-- Content goes below the title -->
</div>
```

Do NOT use this pattern (left-right flex with title on the left):
```html
<!-- WRONG: title on the left, content on the right -->
<div style="display:flex; gap:48px;">
  <div style="flex:0 0 200px;">Title</div>
  <div style="flex:1;">Content</div>
</div>
```

**Important**: Do NOT use `flex:1` on the main content wrapper inside a slide — it defeats vertical centering. Use `flex:1` only on inner column elements for horizontal layout. Do NOT add `padding-top` to push content below the logo — the logo is absolutely positioned and does not affect content flow.

### Project Team Card Layout

**Project team members MUST be displayed horizontally in a single row**, not stacked vertically by role group. Each card shows the member photo, name, role, and a color-coded badge for their department.

Correct pattern:
```html
<div class="flex justify-center gap-8 stagger-enter">
    <!-- Each member card: 200px wide, displayed side by side -->
    <div class="flex flex-col w-[200px] group">
        <div class="h-52 bg-[#111] rounded-xl overflow-hidden mb-3 border border-white/5 ...">
            <img src="..." class="w-full h-full object-cover grayscale group-hover:grayscale-0 ...">
        </div>
        <h4 class="text-sm font-bold text-white ...">Member Name</h4>
        <p class="text-[10px] text-gray-500 uppercase ...">Role Title</p>
        <span class="inline-block w-fit bg-lime-400 text-black font-bold px-3 py-0.5 rounded-full text-[10px] uppercase ...">Department</span>
    </div>
    <!-- ... more members in the same row -->
</div>
```

Badge colors by department:
- **Design**: `bg-lime-400 text-black`
- **Full-Stack**: `bg-brand-purple text-white`
- **Operations**: `bg-white/10 text-white border border-white/20`

---

## Portfolio Projects & Images

**Image Source**: `.claude/resources/case-studies/projects/`
**Rules**:
- **Auto-generate portfolio slides from ALL images** in `.claude/resources/case-studies/projects/`, creating one slide per image file
- **Excluded images** (do NOT create portfolio slides for these):
  - `cover.png` — Reserved for Slide 1 cover only
  - `featured-1.png` — Reserved for Behance Featured slide
  - `featured-2.png` — Reserved for Behance Featured slide
  - `featured-3.png` — Reserved for Behance Featured slide
  - `featured-4.png` — Reserved for Behance Featured slide
- **If new images are added** to the `.claude/resources/case-studies/projects/` folder, they MUST automatically get a portfolio slide. Do not hardcode a fixed list — always scan the folder and include every image except the excluded ones above.
- **Project name = image filename** (strip the file extension). If the filename contains ` - ` or ` -  `, split into project name (before) and project type (after). E.g. `DiaFit -  Healthtech AI App.png` → name: "DiaFit", type: "Healthtech AI App"
- **Base64 embed images** — Read image files and convert to inline `data:image/png;base64,` for self-contained HTML

### Portfolio Slide HTML Pattern

**CRITICAL**: Every project image MUST get its own slide using this exact pattern. Do NOT skip any images.

```html
<!-- SLIDE N: PORTFOLIO - PROJECT_NAME -->
<section class="slide">
    <div class="w-full max-w-7xl mx-auto px-6 grid grid-cols-12 gap-8 items-center relative z-20">
        <div class="col-span-4 stagger-enter">
            <h2 class="text-5xl font-bold mb-4">{{PROJECT_NAME}} -</h2>
            <h2 class="text-5xl font-bold text-lime-400 mb-12">{{PROJECT_TYPE}}</h2>
            <div class="grid grid-cols-2 gap-8 mb-12">
                <div>
                    <div class="text-sm text-gray-400 mb-1">Platform</div>
                    <div class="text-xl text-lime-400 font-medium">Design &amp; Development</div>
                </div>
                <div>
                    <div class="text-sm text-gray-400 mb-1">Project Duration</div>
                    <div class="text-xl text-lime-400 font-medium">{{DURATION}}</div>
                </div>
            </div>
            <div class="flex items-center gap-4">
                <button class="bg-brand-purple text-white px-8 py-3 rounded-full font-medium hover:bg-brand-purple/90 transition">Live Link</button>
                <button class="w-12 h-12 rounded-full bg-brand-purple/20 flex items-center justify-center text-brand-purple hover:bg-brand-purple hover:text-white transition">→</button>
            </div>
        </div>
        <div class="col-span-8 stagger-enter relative">
            <div class="rounded-xl overflow-hidden border border-white/10 shadow-2xl">
                <img src="data:image/png;base64,{{BASE64}}" class="w-full h-auto object-cover opacity-80" alt="{{PROJECT_NAME}}">
            </div>
        </div>
    </div>
</section>
```

Portfolio slides are inserted **after the "Our Process" slide** and **before the "What is Behance?" slide**.

### Portfolio Priority Ordering Rule

**Portfolio slides MUST be sorted by relevance to the proposal's project type.** Projects whose tags match the proposal domain appear first, followed by the rest alphabetically.

**How to apply:**
1. Identify the proposal's domain keywords (e.g. "fintech mobile app" → keywords: `fintech`, `mobile`, `app`, `finance`, `payment`)
2. Score each project: count how many of its tags match the proposal keywords
3. Sort: highest-scoring projects first, then alphabetically for ties

| Project | Image File | Type | Duration | Tags |
|---------|-----------|------|----------|------|
| 343Pet | `343Pet -  Pet HealthCare App.png` | Pet HealthCare App | 3 Months | `mobile`, `healthtech`, `app` |
| Agrilo | `Agrilo -  Agritech AI Agent.png` | Agritech AI Agent | 4 Months | `ai`, `agritech`, `agent` |
| CART | `CART -  Card Traders App.png` | Card Traders App | 3 Months | `mobile`, `marketplace`, `e-commerce`, `fintech` |
| Dexulin | `Dexulin -  Smart Health & Fitness Tracking App.png` | Smart Health & Fitness Tracking | 3 Months | `mobile`, `healthtech`, `fitness`, `app` |
| DiaFit | `DiaFit -  Healthtech AI App.png` | Healthtech AI App | 4 Months | `mobile`, `healthtech`, `ai`, `app` |
| Elite4print | `Elite4print -  E-commerce & ERP Solution.png` | E-commerce & ERP | 3 Months | `web`, `e-commerce`, `erp`, `dashboard` |
| Hacamong | `Hacamong -  Reliable Babysitter Finder App.png` | Babysitter Finder App | 3 Months | `mobile`, `marketplace`, `app` |
| K-Talk | `K-Talk -  Korean Language Learning Platform.png` | Language Learning Platform | 3 Months | `web`, `education`, `platform` |
| Maloha | `Maloha -  Real-time Voice Translation App.png` | Voice Translation App | 3 Months | `mobile`, `ai`, `translation`, `app` |
| Mentora | `Mentora -  AI Student Managment.png` | AI Student Management | 3 Months | `web`, `ai`, `education`, `dashboard` |
| NearWork | `NearWork -  Smart job portal website.png` | Smart Job Portal | 3 Months | `web`, `marketplace`, `portal` |
| Omni | `Omni -  Fitness Tracking App.png` | Fitness Tracking App | 3 Months | `mobile`, `fitness`, `healthtech`, `app` |
| Park Park | `Park Park -  Smart Parking Lot Sharing Platform.png` | Smart Parking | 3 Months | `mobile`, `platform`, `sharing` |
| Personal Expense Tracking | `Personal Expense Tracking - AI Agent.png` | AI Agent | 3 Months | `mobile`, `fintech`, `ai`, `finance`, `app` |
| Silvara | `Silvara -  Personal Health Companion App.png` | Health Companion | 1 Month | `mobile`, `healthtech`, `ai`, `app` |
| Stockify | `Stockify -   AI Business Automation.png` | AI Business Automation | 3 Months | `web`, `ai`, `fintech`, `automation`, `dashboard` |
| Thrill | `Thrill -  Adventure Matching Platform.png` | Adventure Matching | 3 Months | `mobile`, `social`, `platform` |
| Tobeone | `Tobeone -  Community app.png` | Community App | 3 Months | `mobile`, `social`, `community`, `app` |
| Tustix | `Tustix -  Ticket & Supplier Management Dashboard.png` | Ticket Dashboard | 3 Months | `web`, `dashboard`, `management` |

**Example** — Proposal for "fintech mobile app":
- Keywords: `fintech`, `mobile`, `finance`, `app`
- Priority order: Personal Expense Tracking (4 tags match) → CART (2) → Stockify (1) → DiaFit, Dexulin, Omni, Silvara, etc. (1 each: `mobile`/`app`) → rest alphabetically

### Featured Project Images (Behance Slide)

**Image Source**: `.claude/resources/case-studies/projects/`

| Image File | Used On |
|-----------|---------|
| `featured-1.png` | Featured Projects slide (2×2 grid) |
| `featured-2.png` | Featured Projects slide (2×2 grid) |
| `featured-3.png` | Featured Projects slide (2×2 grid) |
| `featured-4.png` | Featured Projects slide (2×2 grid) |

---

## Tech Stack Images

**Image Source**: `.claude/resources/brand/tech-stack/`
**Rule**: Embed each icon inline as base64 next to the tech name in the Tech Stack slide.

### Design
| Tech | Image File |
|------|-----------|
| Figma | `design/figma.png` |
| Motion | `design/motion.png` |
| After Effects | `design/after-effects.png` |
| Cinema 4D | `design/cinema-4d.png` |

### Frontend
| Tech | Image File |
|------|-----------|
| React | `front-end/react.png` |
| Vue.js | `front-end/vue-js.png` |
| Next.js | `front-end/nextjs.png` |
| Angular | `front-end/angular.png` |

### Backend
| Tech | Image File |
|------|-----------|
| Python | `backend/python.png` |
| Django | `backend/django.png` |
| Node.js | `backend/nodejs.png` |

### Mobile
| Tech | Image File |
|------|-----------|
| Flutter | `mobile/flutter.png` |
| React Native | `mobile/react-native.png` |

### Infra
| Tech | Image File |
|------|-----------|
| AWS | `infra/aws.png` |

---

## Client Logos

**Image Source**: `.claude/resources/case-studies/client-logos/`
**Rule**: Embed client logos inline as base64 in the Our Clients slide grid.

| Client | Image File |
|--------|-----------|
| HaKaMong | `hakamong.png` |
| NearWork | `nearwork.png` |
| KTalk | `ktalk.png` |
| CART | `cart.png` |
| Omni | `omni.png` |
| ParkPark | `parkpark.png` |
| 343Pet | `343pet.png` |
| Tobeone | `tobeone.png` |
| Maloha | `maloha.png` |
| Elite4Print | `elite4print.png` |
| Silvara.AI | `silvara-ai.png` |
| Saero | `saero.png` |
| iTTech | `ittech.png` |
| Yonsei University | `yonsei-university.png` |
| Korea University | `korea-university.png` |
| Payments | `payments.png` |
| Dx-i Soft | `dxi-soft.png` |
| Able | `able.png` |
| AI Solutions | `ai-solutions.png` |
| DVSN Studios | `dvsn-studios.png` |
| Kongju National University | `kongju-university.png` |
| BGF Retail | `bgf-retail.png` |
| Dexulin | `dexulin.png` |

---

## Office Icons

**Image Source**: `.claude/resources/brand/offices/`
**Rule**: Embed office flag/icon SVGs inline for the Contact Us slide.

| Office | Image File |
|--------|-----------|
| HQ - South Korea | `south-korea.png` |
| USA | `usa.png` |
| Bangladesh | `bangladesh.png` |

---

## Team Images

**Image Source**: `.claude/resources/brand/team/`
**Rule**: Only use a team member's image when their name is specifically mentioned in the proposal. Files are named with the lowercase shortname from `.claude/resources/team-directory.md` — match by the `Name` column there.

### CEO & CTO
| Name | Image File |
|------|-----------|
| Shin Lukas Dongsub | `ceo-cto/lukas.png` |
| Siam Maruf | `ceo-cto/siam.png` |

### Design Team
| Name | Image File |
|------|-----------|
| Nazirul Hoque | `design-team/nazirul.png` |
| Shamima Nasrin | `design-team/shamima.png` |
| Md Forhad Alam | `design-team/forhad-alam.png` |
| MD Ahosan Habib | `design-team/habib.png` |
| Abu MD Ehsan | `design-team/ehsan.png` |
| Md Foysal Alam | `design-team/foysal.png` |
| Redwanul Haque | `design-team/redwan.png` |
| Rukaiya Sharmeen | `design-team/rukaiya.png` |
| Tasfia | `design-team/tasfia.png` |
| MD Romjan | `design-team/romjan.png` |
| Mehedi Hasan | `design-team/mehedi.png` |
| Mosarrof Hossain | `design-team/mosarrof.png` |

### Full-Stack Team
| Name | Image File |
|------|-----------|
| Md Hossen Rana | `full-stack-team/rana.png` |
| G M Zulkar Nine | `full-stack-team/zulkar.png` |
| Atik Bhuiyan | `full-stack-team/atik.png` |
| Abdullah Al Nomaan | `full-stack-team/nomaan.png` |
| Shamim Hossain | `full-stack-team/shamim.png` |
| Md. Mohibulla | `full-stack-team/mohibulla.png` |
| Forhad | `full-stack-team/forhad.png` |
| Abdur Rahman | `full-stack-team/abdur.png` |
| Muksitur Rahman | `full-stack-team/muksitur.png` |
| Dolan Bairagi | `full-stack-team/dolan.png` |
| Hasan Al Mahmud | `full-stack-team/hasan.png` |
| Meherab Irfan | `full-stack-team/meherab.png` |
| Talha Mahmud | `full-stack-team/talha.png` |
| Israt Jahan Rothy | `full-stack-team/israt.png` |
| Md. Tonmoy Khan | `full-stack-team/tonmoy.png` |
| Md. Zihad Hossion | `full-stack-team/zihad.png` |
| Saiful Islam | `full-stack-team/saiful.png` |

### Operations Team
| Name | Image File |
|------|-----------|
| Jayden | `operation-team/jayden.png` |
| Riaz Uddin | `operation-team/riaz.png` |
| Eddy | `operation-team/eddy.png` |
| Istimam Hossen Akib | `operation-team/akib.png` |
| Symon Barua | `operation-team/symon.png` |
| Yasin Billah | `operation-team/yasin.png` |
| Rahid Uddin Ahmed | `operation-team/rahid.png` |

---

## Output Location

```
.claude-project/proposals/
└── [Proposal] [PROJECT_NAME].html
```

One file per generation. Language is set via `<html lang="ko|en">` at the top of the file; re-run the skill with a different language to produce a second file (overwrites unless the project name differs).

---

## Related Files

- **Template**: `templates/proposal-template.html`
- **Korean Content**: `prompts/content-korean.md`
- **English Content**: `prompts/content-english.md`
- **Guide**: `prompts/template-guide.md`

---

**Skill Status**: COMPLETE
**Output Format**: HTML (16:9 Full Screen)
**Languages**: Korean, English
