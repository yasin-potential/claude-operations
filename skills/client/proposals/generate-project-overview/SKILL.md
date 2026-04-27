---
name: generate-project-overview
description: Use when a PM needs a one-page project overview deck before committing to a full PRD. Produces a branded HTML slide deck (light+dark toggle, Plus Jakarta Sans, brand tokens) with one-liner, glossary, user types, deliverables, per-deliverable feature lists, timeline, and open questions. Supports `--language korean|english` (default `korean`, mirrors generate-proposal's mixed mode). On user confirmation, extracts a markdown answers file and hands off to generate-prd.
argument-hint: "[--language korean|english]"
---

# Generate Project Overview - Branded HTML Deck (PRD Precursor)

Generate a one-page project overview as a **branded HTML slide deck** that the PM and client can align on before committing to a full PRD. The deck follows the brand guideline at `.claude/resources/brand/BRAND-GUIDELINE.md` — light+dark toggle, Plus Jakarta Sans, brand color tokens, accessibility floor.

On user confirmation, the skill extracts a markdown answers file from the same input data and invokes `/generate-prd` with that file.

Language is controlled by the `--language` flag. `english` = fully English deck. `korean` = **mixed Korean deck** — slide section titles (`One Liner`, `Terminology`, `User Types`, `Deliverables`, `Features`, `Timeline`, `Need to Discuss`) and chrome (nav, theme toggle labels) stay English; only the *content* (definitions, role descriptions, feature names, open questions) is filled in Korean. Mirrors `generate-proposal`'s mixed-mode rule.

---

## Step-by-Step Generation Process

### Step 1: Parse `$ARGUMENTS` for the `--language` flag

Syntax: `/generate-project-overview [--language korean|english]`

- Accepted values: `korean` | `english` (full words only).
- If the flag is absent, set `LANGUAGE = korean`.
- If the flag is present with an unrecognized value, stop and reply:
  > Unknown `--language` value. Use `--language korean` or `--language english`. Default is `korean` when omitted.
- Store the resolved `LANGUAGE` for use in Step 3.

### Step 2: Interview the user

Ask for these **required** inputs in order. Do **not** re-ask about language — it comes from the flag.

| # | Input | Question |
|---|-------|----------|
| 1 | Client name | "What is the client company name?" |
| 2a | Project name | "What is the project title?" |
| 2b | Tentative? | "Is this name final or tentative (가칭)?" — if tentative, append `(가칭)` to displayed `{{PROJECT_NAME}}` everywhere except the filename. |
| 3 | One-liner | "In one sentence, what does this build?" — **cap at 60 Korean chars / 90 English chars**. If user gives longer, ask them to trim. Keep it punchy — what + for whom (e.g., `반려견 주인을 검증된 도그워커와 연결하는 산책 대행 앱`). |
| 4 | Domain glossary | "List 3-8 project-specific terms with definitions. Domain vocabulary only — skip general tech terms. Keep each definition under 80 Korean chars / 120 English chars." |
| 5 | User types | "Who are the user roles? For each: role name, short description (1 sentence), primary goal (≤ 30 chars)." |
| 6 | Deliverables | "What products ship? (e.g., `app`, `admin-dashboard`, `vendor-dashboard`). Add a one-line scope summary per item (≤ 80 chars)." |
| 7 | Features per deliverable | "For each deliverable above, list 5-15 features. Each item ≤ 40 Korean chars / 60 English chars. If a feature needs detail, split into two items rather than one long line." Ask once per deliverable so each gets its own list. |
| 8 | Timeline | "Rough milestones: phase name, duration, deliverable scope. Map each phase to one of: Discovery, Design, Dev, QA, Launch (drives the brand phase color)." |
| 9 | Open questions | "What's still unresolved? List as questions — items blocking PRD finalization." |

If the user can't answer one, mark it `_TBD_` in the output rather than skipping the slide.

**Length caps exist for layout, not for thoroughness** — Korean text without spaces wraps poorly inside cards; long lines overflow on the dark theme. When trimming, drop redundant phrasing rather than substance.

### Step 3: Render the template

Read `templates/overview-template.html`. The template is a single HTML file based on `.claude/resources/brand/templates/deck-base.html` with all brand tokens inlined. It contains nine slide regions:

1. Cover (slide-cover)
2. One Liner
3. Terminology
4. User Types
5. Deliverables
6. **Features** — repeats once per deliverable. The template has a `<!-- {{FEATURES_SLIDES}} -->` placeholder; replace it with N copies of the feature-slide block (one per deliverable).
7. Timeline
8. Need to Discuss
9. Thank You (slide-thankyou)

Replace every `{{PLACEHOLDER}}` per the **Variables Reference** below.

**Per-deliverable feature slides:** Use this exact block, repeated once per deliverable in the same order as `## Deliverables`. Replace `{{FEATURES_SLIDES}}` with the concatenation of all blocks.

```html
<section class="slide" data-slide="0" aria-labelledby="slide-features-__N__-title">
    <div class="slide-logo" aria-hidden="true">{{LOGO_WORDMARK_SVG}}</div>
    <div class="section-number" aria-hidden="true">05</div>
    <h1 id="slide-features-__N__-title" class="slide-title">Features &mdash; {{DELIVERABLE_NAME}}</h1>
    <div class="slide-content">
        <ul class="feature-list">
            {{FEATURE_ITEMS}}
        </ul>
    </div>
</section>
```

- `data-slide="0"` — leave as `0` on every slide. The bundled JS re-indexes all `.slide` elements at runtime, so per-section indices do not need to be hand-maintained.
- `__N__` — deliverable index starting at 1, used only to make the `aria-labelledby` id unique. Examples: `slide-features-1-title`, `slide-features-2-title`.
- The decorative section number `05` is shared by all feature slides (regardless of how many deliverables), so it stays as the literal `05` in every per-deliverable block.
- `{{DELIVERABLE_NAME}}` stays English (kebab-case: `app`, `admin-dashboard`).
- `{{FEATURE_ITEMS}}` — rendered `<li>...</li>` set, one per feature.
- `{{LOGO_WORDMARK_SVG}}` — paste the wordmark SVG block verbatim from the `<div class="slide-logo">` of any other content slide in `overview-template.html` (e.g., the Terminology slide). Do not invent your own SVG.

**Decorative section-number scheme** (used in the static `.section-number` element of each content slide; already populated in the template — only the feature slides require the value to be filled):

| Section | Number | Where |
|---------|--------|-------|
| One Liner | 01 | already in template |
| Terminology | 02 | already in template |
| User Types | 03 | already in template |
| Deliverables | 04 | already in template |
| Features | 05 | feature slide block above |
| Timeline | 06 | already in template |
| Need to Discuss | 07 | already in template |

Cover and Thank-You slides have no section number.

### Step 4: Write the deck file

Write the rendered HTML to:

```
.claude-project/proposals/[Overview] {{PROJECT_NAME}}.html
```

Filename uses the `[Overview]` literal prefix (mirrors `[Proposal]` from generate-proposal). Create the `.claude-project/proposals/` directory if missing. `{{PROJECT_NAME}}` in the filename always stays English regardless of `LANGUAGE`.

After writing, update the `<title>` tag of the output file to `[Overview] {{PROJECT_NAME}}` (replace the literal `{{PROJECT_NAME}}` placeholder, since the head `<title>` references it). The `nav-bar` and slide indices are generated at runtime from `.slide` elements — no manual nav or `data-slide` edits needed.

**If `LANGUAGE = korean`, additionally apply every row of the translation table in the "Korean mode rule" section** to the rendered file (Edit tool, one Edit per row). This swaps section titles, table headers, the cover label, and the THANK YOU heading from English to Korean. Skipping this pass leaves the deck half-localized.

### Step 5: Confirm with the user

Print the file path, then a 5-line summary:
1. Project name + client
2. Number of deliverables
3. Total feature count across deliverables
4. Timeline span
5. Number of open questions

Then ask exactly:

> Confirm this overview, or revise? On confirmation I'll extract a markdown answers file and feed it into `/generate-prd`.

If the user requests revisions, edit the HTML in place using the Edit tool, then re-run Step 5.

### Step 6: On confirmation — extract markdown and hand off to `/generate-prd`

Build a markdown companion file from the same input data collected in Step 2.

**English mode (`LANGUAGE = english`)** — use English H2 section names and English table headers:

```markdown
# [Overview] {{PROJECT_NAME}}

**Client:** {{CLIENT_NAME}}
**Generated:** {{TODAY}}
**Language:** english

## One Liner

{{ONE_LINER}}

## Terminology

| Term | Definition |
|------|------------|
{{TERMINOLOGY_ROWS}}

## User Types

| Role | Description | Primary Goal |
|------|-------------|--------------|
{{USER_TYPE_ROWS}}

## Deliverables

{{DELIVERABLES_LIST}}

## Features

### {{DELIVERABLE_NAME}}

- {{FEATURE_1}}
...

## Timeline

| Milestone | Duration | Deliverable |
|-----------|----------|-------------|
{{TIMELINE_ROWS}}

## Need to Discuss

{{NEED_TO_DISCUSS}}
```

**Korean mode (`LANGUAGE = korean`)** — use Korean H2 section names + Korean table headers; if Q2b = tentative, append `(가칭)` to the H1:

```markdown
# [Overview] {{PROJECT_NAME}}{{ (가칭) if tentative }}

**클라이언트:** {{CLIENT_NAME}}
**작성일:** {{TODAY}}
**언어:** korean

## 한 줄 소개

{{ONE_LINER}}

## 용어 사전

| 용어 | 정의 |
|------|------|
{{TERMINOLOGY_ROWS}}

## 사용자 타입

| 역할 | 설명 | 핵심 목표 |
|------|------|-----------|
{{USER_TYPE_ROWS}}

## 결과물

{{DELIVERABLES_LIST}}

## 기능

### {{DELIVERABLE_NAME}}

- {{FEATURE_1}}
...

## 타임라인

| 마일스톤 | 기간 | 결과물 |
|----------|------|--------|
{{TIMELINE_ROWS}}

## 논의 필요

{{NEED_TO_DISCUSS}}
```

Write to:

```
.claude-project/proposals/[Overview] {{PROJECT_NAME}}.md
```

Then invoke:

```
/generate-prd <path-to-the-markdown-file>
```

The companion `.md` is the same shape `pre-intake-en.md` plays today — `/generate-prd` accepts it directly. No format conversion needed.

If the user requests revisions before this step, edit the HTML, then re-run Step 5. The markdown is regenerated from the HTML data only on confirmation.

---

## Variables Reference

| Variable | Source | Translates in Korean mode? |
|----------|--------|----------------------------|
| `{{CLIENT_NAME}}` | Q1 | No (always English) |
| `{{PROJECT_NAME}}` | Q2a | No (English). When Q2b = tentative, render with `(가칭)` suffix on the cover and markdown H1; filename stays plain. |
| `{{TODAY}}` | Auto-filled with current date (`YYYY.MM.DD`) | No |
| `{{ONE_LINER}}` | Q3 | Yes — keep ≤ 60 Korean chars / 90 English chars. |
| `{{TERMINOLOGY_ROWS}}` | Q4 | Yes (term + definition both translate). Table headers `용어 / 정의` per the translation table. |
| `{{USER_TYPE_ROWS}}` | Q5 | Yes (role + description + goal translate). |
| `{{DELIVERABLES_LIST}}` | Q6 | Deliverable name stays English (kebab-case); scope summary translates. |
| `{{FEATURES_SLIDES}}` | Q7 | Slide title `기능 — <name>` (deliverable name stays English); feature items translate. |
| `{{TIMELINE_ROWS}}` | Q8 | Phase label and scope translate (`발굴 / 디자인 / 개발 / QA / 런칭`); CSS class on phase-bar stays English (`phase-discovery` etc.); durations: number stays numeric, unit translates (`8 weeks` → `8주`). |
| `{{NEED_TO_DISCUSS}}` | Q9 | Yes |
| `{{LANGUAGE}}` | Step 1 | No |

### HTML fragment shapes for each placeholder

The template expects pre-rendered HTML fragments at these placeholders. Emit exactly this shape:

**`{{TERMINOLOGY_ROWS}}`** — one `<tr>` per term:
```html
<tr><td class="term">SKU</td><td class="def">Stock Keeping Unit — unique identifier for each variant of a product.</td></tr>
```

**`{{USER_TYPE_ROWS}}`** — one `<div class="user-card">` per role:
```html
<div class="user-card">
    <div class="role">Buyer</div>
    <div class="role-desc">Individual purchaser browsing the catalog and placing orders.</div>
    <div class="role-goal">Find and order the right product fast</div>
</div>
```

**`{{DELIVERABLES_LIST}}`** — one `<div class="deliverable-card">` per deliverable:
```html
<div class="deliverable-card">
    <div class="name">app</div>
    <div class="scope">Customer-facing iOS/Android app for browsing, ordering, and tracking deliveries.</div>
</div>
```

**`{{FEATURE_ITEMS}}`** (inside each feature slide block) — one `<li>` per feature:
```html
<li>Login / signup</li>
```

**`{{TIMELINE_ROWS}}`** — one `<tr>` per milestone. The phase-bar class is one of `phase-discovery`, `phase-design`, `phase-dev`, `phase-qa`, `phase-launch` (Q8 maps the phase):
```html
<tr>
    <td><div class="phase-cell"><span class="phase-bar phase-design"></span><span>Design</span></div></td>
    <td class="duration">3 weeks</td>
    <td class="scope">Wireframes, visual design, prototype validation.</td>
</tr>
```

**`{{NEED_TO_DISCUSS}}`** — one `<li>` per question:
```html
<li>Should the app support guest checkout, or require account creation?</li>
```

Generate these fragments locally (in-memory) before writing the file. Do not write multiple passes.

### Korean mode rule (critical) — minimize English

When `LANGUAGE = korean`, **translate as much as possible to Korean**. The deck is for a Korean PM and Korean client — leaving English boilerplate makes the artifact feel un-localized. The only things that must stay English are technical identifiers and brand chrome.

**Translate to Korean — overwrite the literal text in the template** (use the Edit tool on the rendered file after copy):

| English (template default) | Korean (replace with) |
|----------------------------|------------------------|
| `Project Overview` (cover `.project-label`) | `프로젝트 오버뷰` |
| `<h1 class="slide-title">One Liner</h1>` | `<h1 class="slide-title">한 줄 소개</h1>` |
| `<div class="one-liner-meta">One Liner</div>` | `<div class="one-liner-meta">한 줄 소개</div>` |
| `<h1 class="slide-title">Terminology</h1>` | `<h1 class="slide-title">용어 사전</h1>` |
| `<th>Term</th><th>Definition</th>` | `<th>용어</th><th>정의</th>` |
| `<h1 class="slide-title">User Types</h1>` | `<h1 class="slide-title">사용자 타입</h1>` |
| `<h1 class="slide-title">Deliverables</h1>` | `<h1 class="slide-title">결과물</h1>` |
| `<h1 ... class="slide-title">Features &mdash; {{DELIVERABLE_NAME}}</h1>` | `<h1 ... class="slide-title">기능 — {{DELIVERABLE_NAME}}</h1>` (deliverable name itself stays kebab-case English) |
| `<h1 class="slide-title">Timeline</h1>` | `<h1 class="slide-title">타임라인</h1>` |
| `<th>Milestone</th><th>Duration</th><th>Deliverable</th>` | `<th>마일스톤</th><th>기간</th><th>결과물</th>` |
| `<h1 class="slide-title">Need to Discuss</h1>` | `<h1 class="slide-title">논의 필요</h1>` |
| `<h1 ... class="thankyou-title">THANK YOU</h1>` | `<h1 ... class="thankyou-title">감사합니다</h1>` |
| Phase names inside timeline `phase-cell` text spans (`Discovery`, `Design`, `Dev`, `QA`, `Launch`) | `발굴`, `디자인`, `개발`, `QA`, `런칭` (the `phase-*` CSS class on the bar stays English — that is what drives the brand color token) |
| Phase durations like `3 weeks` | `3주` (numbers stay numeric, the `weeks` unit translates) |

**Stay English — do not translate**:

- `{{CLIENT_NAME}}` — client/company names
- `{{PROJECT_NAME}}` — project names. **Exception:** if the user marked the name tentative in Q2b, append `(가칭)` so it reads like `DogWalker (가칭)` on the cover and in markdown. The filename always stays `[Overview] DogWalker.html` (no `(가칭)` in the filename).
- Deliverable kebab-case names (`app`, `admin-dashboard`, `vendor-dashboard`) — these are technical identifiers
- Brand wordmark text (`Potential` in the SVG)
- `contact@potentialai.com` and `Copyright 2026. Potential INC. All rights reserved` (legal)
- Currency amounts (`$20,000`, `30%`) — keep USD format, do not convert to KRW
- Phase color CSS classes (`phase-discovery`, `phase-design`, `phase-dev`, `phase-qa`, `phase-launch`) — these are CSS hooks
- Chrome controls (theme toggle, fullscreen) — these are aria labels for screen readers, leave as-is
- `<html lang>` — leave as `en` from the template default; do not change to `ko`

**Tentative project name (Q2b answer = "tentative")**:

- Cover slide `<h1 class="project-name">`: render as `{{PROJECT_NAME}} (가칭)` (e.g., `DogWalker (가칭)`).
- Markdown companion file (Step 6): the H1 heading line — `# [Overview] {{PROJECT_NAME}} (가칭)`.
- Filename: **never** include `(가칭)` — keep `[Overview] {{PROJECT_NAME}}.html` and `.md` so the filesystem stays clean.

**Korean line-break hygiene** — Korean lacks word spacing inside compound nouns; long lines overflow cards. The template's `word-break: keep-all` + `overflow-wrap: anywhere` already handle most cases. When writing content fragments, **also**:

- Insert a space before parentheticals: `의뢰 작성 (Pet 선택)` not `의뢰 작성(Pet 선택)`.
- Use ` · ` (with surrounding spaces) as a separator inside a single bullet, never `·` adjacent to text. Example: `결제 · 이용 내역 조회`.
- Use ` / ` (with surrounding spaces) for "or": `수락 / 거절`.
- Hard-cap any single line per the Q3–Q7 limits. If a feature genuinely needs more text, split into two `<li>` items.

---

## Brand Compliance Checklist

Before declaring the deck done, confirm:

- [ ] Plus Jakarta Sans loaded via Google Fonts (preconnect + stylesheet links present in `<head>`).
- [ ] `:root` defines all brand primitives (`--brand-purple`, `--brand-lime`, `--brand-navy`, `--brand-dark`).
- [ ] Both `[data-theme="light"]` and `[data-theme="dark"]` semantic token blocks present.
- [ ] Theme toggle button + `T` keybinding work; theme persists via `localStorage.meetingTheme`.
- [ ] No raw hex outside `:root` / `[data-theme]` blocks.
- [ ] Cover and Thank-You slides have the glow-orb pseudo-elements.
- [ ] Cover uses inlined `potential_logo.svg` paths via `currentColor` (do not link to file path — global-sync safe).
- [ ] Content slides have the top-left wordmark via `.slide-logo` with `.mk` (accent) + `.wm` (heading) classes.
- [ ] Exactly one `<h1>` per slide. Decorative section numbers wrapped in `aria-hidden`.
- [ ] `:focus-visible` ring on every nav dot, button, link.
- [ ] Nav dots are visual 10px with `::before` 44×44px hit target.
- [ ] `prefers-reduced-motion: reduce` block present.
- [ ] Print stylesheet forces light palette + `page-break-after: always` per slide.
- [ ] Phase color bars in the Timeline slide use `--phase-discovery|design|dev|qa|launch` only.

If any item fails, fix the template (`templates/overview-template.html`) — not the per-deck output. Then propagate per the Brand Guideline §13 change-management rule.

---

## Hand-off Compatibility with `/generate-prd`

The companion `.md` written in Step 6 is structured to be consumable by `generate-prd` as its answers file. Mapping:

| Overview section | Maps to PRD Phase A intake |
|------------------|----------------------------|
| One Liner | App description / mission |
| Terminology | Domain vocabulary for feature naming |
| User Types | Section 1 (User roles) |
| Deliverables | Section 2 (Modules) |
| Features (per deliverable) | Section 2.5 (Module → feature breakdown) |
| Timeline | Project schedule |
| Need to Discuss | Items requiring PM decision in Phase 1 Critical Review |

Items marked `_TBD_` surface as Phase 1 questions during PRD generation.
