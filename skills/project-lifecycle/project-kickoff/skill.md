---
name: project-kickoff
description: "Generate a branded HTML slide presentation for client kick-off meetings. Collects project info via interview, then generates a navigable browser-based presentation with Potential INC branding. For the initial project start, prefer /project-launch which generates this AND the Project Overview Slack Canvas together from one interview."
user-invocable: true
argument-hint: "[--project 'name'] [--client 'name']"
---

# Kickoff Meeting Presentation Generator

Generate a branded, browser-based slide presentation for client kick-off meetings. The presentation introduces "how we will work" after the contract is signed.

> **Paired with Project Overview**: At project start, the kickoff HTML and the Project Overview Slack Canvas are generated together from the draft PRD. Use `/project-launch` to produce both at once. Use this skill (`/project-kickoff`) standalone only when regenerating the presentation later (e.g., team/timeline changed).

---

## Workflow Overview

```
┌─────────────────────┐
│  Step 1              │
│  Interview           │
│  (Collect Info)      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Step 2              │
│  Auto-generate       │
│  Timeline & Tasks    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Step 3              │
│  Confirm Summary     │
│  (Brief review)      │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Step 4              │
│  Generate HTML       │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  Step 5              │
│  Report Result       │
└─────────────────────┘
```

---

## Step 1: Interview (Collect Project Info)

### 1.1 Parse Arguments

Extract from `$ARGUMENTS`:
- **--project**: Project name (e.g., "Activity Coaching")
- **--client**: Client name with honorific (e.g., "김철수 대표님")

### 1.2 Collect Required Info

Use AskUserQuestion to collect missing information. Ask as few rounds as possible by grouping questions.

**Round 1 — Project Basics** (skip any already provided via arguments):

1. **Project name** — "What is the project name?"
2. **Client name** — "Client name with title/honorific? (e.g., 김철수 대표님)"
3. **Tech stack** — "Select tech stack (can combine multiple):"
   - React + NestJS (web)
   - React Native + NestJS (mobile)
   - React + Django (web)
   - React Native + Django (mobile)
   - Custom (specify)
4. **Project duration** — "Project start and end month? (e.g., 2026.04 ~ 2026.07)"

**Round 2 — Team Members:**

The following members are **always included** (do not ask):
- CEO: Lukas
- CTO: Siam
- COO: Jayden

Ask for the remaining project team members:
```
Who are the team members for this project?
(Typical roles: PM, Designer, Backend, Frontend, QA — provide name and role)

Example:
- PM: 김민수
- Designer: 이지은
- Backend: 박준혁
- Frontend: 최서연
- QA: 정하늘
```

Multiple people can share the same role, or roles can be omitted if not needed.

**Round 3 — Phase Breakdown:**

Ask the user to define phases and their week ranges. Provide a pre-filled example based on the project duration:

```
Please confirm or adjust the phase breakdown (week ranges):

1. PM / Planning: 1-2주
2. Design: 2-4주
3. DB / Backend: 3-8주
4. Frontend: 5-10주
5. Testing / QA: 9-12주
6. Deploy: 11-12주
```

The number of total weeks is auto-calculated from the project duration. Adjust the example accordingly.

---

## Step 2: Auto-generate Timeline & Weekly Tasks

### 2.1 Generate Timeline

From the phase breakdown, create a Gantt-style timeline mapping phases to weeks/months.

### 2.2 Generate Weekly Tasks

Auto-generate weekly task descriptions from the phase breakdown. Rules:
- Each week lists the active phases and their key deliverables
- Overlap weeks show multiple active phases
- Use concise task descriptions

Example output for a 12-week project:
```
Week 1: PM - Requirements gathering, Scope definition
Week 2: PM - PRD finalization, Design - Wireframe start
Week 3: Design - UI Design, DB - Schema design
Week 4: Design - Design review, Backend - API development start
...
Week 12: QA - Final testing, Deploy - Production release
```

---

## Step 3: Confirm Summary

Present a brief summary to the user for confirmation before generating:

```
## Kick-off Presentation Summary

- Project: [PROJECT_NAME]
- Client: [CLIENT_NAME]
- Team: Lukas (CEO), Siam (CTO), Jayden (COO), [PROJECT_MEMBERS]
- Tech Stack: [TECH_STACK]
- Duration: [START] ~ [END] ([N] weeks)
- Phases: [PHASE_SUMMARY]

Proceed with generation? (Y/adjust)
```

If the user wants adjustments, collect corrections and update. Otherwise, proceed to Step 4.

---

## Step 4: Generate HTML Presentation

### 4.1 Output Location

**Directory**: Project root or current working directory
**Filename**: `[Kickoff] {ProjectName}.html`

### 4.2 Slide Structure

The presentation consists of the following slides:

| # | Slide | Content |
|---|-------|---------|
| 1 | Cover | Project name, client name, Copyright |
| 2 | Team | Team members with roles (fixed + project-specific) |
| 3 | Index | Table of contents (clickable) |
| 4 | Tech Stack | Selected technologies with icons |
| 5 | Timeline | Gantt chart visualization |
| 6 | Weekly Tasks | Week-by-week task breakdown |
| 7 | Communication | Slack + pm.potentialai.com |
| 8 | Deliverables | PRD, Swagger |
| 9 | Meeting Agenda | Discussion items, decisions |
| 10 | Q&A | Question & answer slide |
| 11 | Thank You | Contact info, closing |

### 4.3 Brand Guidelines

| Element | Value |
|---------|-------|
| Primary Accent | `#624DFF` |
| Dark Accent | `#4834CC` |
| Headings | `#050042` |
| Body Text | `#333333` |
| Sub Text | `#666666` |
| Light BG | `#f8f7ff` |
| Background | `#ffffff` |
| Font | Inter (Google Fonts) |

### 4.4 HTML Template

Generate a single self-contained HTML file with embedded CSS and JS. The presentation must support:
- **Keyboard navigation**: Left/Right arrow keys to switch slides
- **Click navigation**: Bottom dot indicators
- **Slide counter**: "3 / 10" format
- **Fullscreen**: F key or button to toggle fullscreen
- **Smooth transitions**: Slide or fade animation
- **Print-friendly**: Each slide maps to one page when printed
- **Responsive**: Works on projector resolutions

> **IMPORTANT**: The HTML file must be completely self-contained (no external dependencies except Google Fonts). All CSS, JS, and SVG assets must be inline.

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Kickoff] [PROJECT_NAME]</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        /* === Reset & Base === */
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Inter', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
            background: #050042;
            color: #333;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }

        /* === Slide Container === */
        .slides-container {
            width: 100vw;
            height: 100vh;
            position: relative;
            overflow: hidden;
        }

        .slide {
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px 80px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            background: #ffffff;
        }

        .slide.active {
            opacity: 1;
            transform: translateX(0);
        }

        .slide.prev {
            opacity: 0;
            transform: translateX(-100%);
        }

        /* === Cover Slide === */
        .slide-cover {
            background: linear-gradient(135deg, #050042 0%, #624DFF 100%);
            color: white;
            text-align: center;
        }

        .slide-cover .project-label {
            font-size: 31px;
            font-weight: 500;
            letter-spacing: 6px;
            text-transform: uppercase;
            color: rgba(255,255,255,0.7);
            margin-bottom: 28px;
        }

        .slide-cover .project-name {
            font-size: 88px;
            font-weight: 900;
            letter-spacing: 2px;
            margin-bottom: 24px;
        }

        .slide-cover .client-name {
            font-size: 42px;
            font-weight: 400;
            color: rgba(255,255,255,0.8);
            margin-bottom: 14px;
        }

        .slide-cover .project-date {
            font-size: 28px;
            color: rgba(255,255,255,0.5);
        }

        .slide-cover .copyright {
            position: absolute;
            bottom: 64px;
            font-size: 15px;
            color: rgba(255,255,255,0.4);
        }

        /* === Section Title === */
        .slide .section-number {
            font-size: 96px;
            font-weight: 900;
            color: #624DFF;
            opacity: 0.15;
            position: absolute;
            top: 40px;
            left: 80px;
        }

        .slide .slide-title {
            font-size: 44px;
            font-weight: 800;
            color: #050042;
            margin-bottom: 40px;
            align-self: flex-start;
        }

        /* === Content Styles === */
        .content-grid {
            display: grid;
            gap: 24px;
            width: 100%;
        }

        .tech-card {
            background: #f8f7ff;
            border-radius: 16px;
            padding: 36px;
            display: flex;
            align-items: center;
            gap: 24px;
            border: 1px solid rgba(98, 77, 255, 0.1);
        }

        .tech-card .tech-icon {
            width: 64px;
            height: 64px;
            background: #624DFF;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 28px;
            font-weight: 700;
            flex-shrink: 0;
        }

        .tech-card .tech-info h3 {
            font-size: 24px;
            font-weight: 700;
            color: #050042;
            margin-bottom: 6px;
        }

        .tech-card .tech-info p {
            font-size: 17px;
            color: #666;
        }

        /* === Team Slide === */
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 24px;
            width: 100%;
            max-width: 900px;
        }

        .team-member {
            text-align: center;
            padding: 24px 16px;
        }

        .team-avatar {
            width: 88px;
            height: 88px;
            border-radius: 50%;
            background: #624DFF;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 14px;
            color: white;
            font-size: 32px;
            font-weight: 700;
        }

        .team-avatar.executive {
            background: #050042;
        }

        .team-member .member-name {
            font-size: 22px;
            font-weight: 700;
            color: #050042;
            margin-bottom: 6px;
        }

        .team-member .member-role {
            font-size: 17px;
            font-weight: 500;
            color: #624DFF;
        }

        .team-divider {
            width: 100%;
            max-width: 900px;
            border: none;
            border-top: 1px solid rgba(98, 77, 255, 0.15);
            margin: 8px 0 16px;
        }

        .team-section-label {
            font-size: 15px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 18px;
            align-self: flex-start;
            max-width: 900px;
            width: 100%;
        }

        /* === Timeline (Gantt) === */
        .gantt-container {
            width: 100%;
            overflow-x: auto;
        }

        .gantt-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 16px;
        }

        .gantt-table th {
            padding: 14px 4px;
            text-align: center;
            font-weight: 600;
            color: #050042;
            border-bottom: 2px solid #624DFF;
            font-size: 13px;
        }

        .gantt-table th.phase-col {
            text-align: left;
            padding-left: 16px;
            width: 180px;
            min-width: 180px;
        }

        .gantt-table td {
            padding: 12px 4px;
            text-align: center;
            border-bottom: 1px solid #f0f0f0;
            position: relative;
        }

        .gantt-table td.phase-name {
            text-align: left;
            padding-left: 16px;
            font-weight: 600;
            color: #050042;
            white-space: nowrap;
        }

        .gantt-bar {
            height: 32px;
            border-radius: 6px;
            position: absolute;
            top: 50%;
            left: 2px;
            right: 2px;
            transform: translateY(-50%);
        }

        .gantt-bar.pm { background: #624DFF; }
        .gantt-bar.design { background: #8B7AFF; }
        .gantt-bar.backend { background: #4834CC; }
        .gantt-bar.frontend { background: #A594FF; }
        .gantt-bar.qa { background: #C4BAFF; }
        .gantt-bar.deploy { background: #050042; }

        /* === Weekly Tasks === */
        .tasks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            width: 100%;
            max-height: calc(100vh - 180px);
            overflow-y: auto;
        }

        .task-card {
            background: #f8f7ff;
            border-radius: 14px;
            padding: 28px;
            border-left: 4px solid #624DFF;
        }

        .task-card .week-label {
            font-size: 15px;
            font-weight: 700;
            color: #624DFF;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .task-card .task-list {
            font-size: 17px;
            color: #333;
            line-height: 1.6;
        }

        /* === Communication / Deliverables === */
        .info-cards {
            display: flex;
            gap: 32px;
            width: 100%;
        }

        .info-card {
            flex: 1;
            background: #f8f7ff;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            border: 1px solid rgba(98, 77, 255, 0.1);
        }

        .info-card .card-icon {
            width: 72px;
            height: 72px;
            background: #624DFF;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            color: white;
            font-size: 32px;
        }

        .info-card h3 {
            font-size: 24px;
            font-weight: 700;
            color: #050042;
            margin-bottom: 12px;
        }

        .info-card p {
            font-size: 19px;
            color: #666;
            line-height: 1.8;
        }

        .info-card a {
            color: #624DFF;
            text-decoration: none;
            font-weight: 600;
        }

        /* === Agenda Slide === */
        .agenda-list {
            width: 100%;
            max-width: 700px;
        }

        .agenda-item {
            display: flex;
            align-items: center;
            gap: 24px;
            padding: 24px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .agenda-item .agenda-num {
            width: 48px;
            height: 48px;
            background: #624DFF;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 20px;
            flex-shrink: 0;
        }

        .agenda-item .agenda-text {
            font-size: 26px;
            color: #050042;
            font-weight: 500;
        }

        /* === Q&A Slide === */
        .slide-qa {
            background: linear-gradient(135deg, #f8f7ff 0%, #ffffff 100%);
            text-align: center;
        }

        .slide-qa .qa-title {
            font-size: 96px;
            font-weight: 900;
            color: #624DFF;
            margin-bottom: 20px;
        }

        .slide-qa .qa-sub {
            font-size: 28px;
            color: #666;
        }

        /* === Thank You Slide === */
        .slide-thankyou {
            background: linear-gradient(135deg, #050042 0%, #624DFF 100%);
            color: white;
            text-align: center;
        }

        .slide-thankyou .thankyou-title {
            font-size: 72px;
            font-weight: 900;
            margin-bottom: 28px;
        }

        .slide-thankyou .contact-email {
            font-size: 24px;
            color: rgba(255,255,255,0.7);
        }

        .slide-thankyou .copyright {
            position: absolute;
            bottom: 64px;
            font-size: 15px;
            color: rgba(255,255,255,0.4);
        }

        /* === Navigation === */
        .nav-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 48px;
            background: rgba(5, 0, 66, 0.95);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .nav-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: rgba(255,255,255,0.3);
            cursor: pointer;
            transition: all 0.3s;
            border: none;
            padding: 0;
        }

        .nav-dot.active {
            background: #624DFF;
            width: 28px;
            border-radius: 5px;
        }

        .slide-counter {
            position: fixed;
            bottom: 56px;
            right: 24px;
            font-size: 13px;
            color: rgba(5, 0, 66, 0.4);
            font-weight: 500;
            z-index: 100;
        }

        .fullscreen-btn {
            position: fixed;
            top: 16px;
            right: 16px;
            width: 36px;
            height: 36px;
            background: rgba(5, 0, 66, 0.08);
            border: none;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 100;
            color: #050042;
            font-size: 16px;
            transition: background 0.2s;
        }

        .fullscreen-btn:hover {
            background: rgba(5, 0, 66, 0.15);
        }

        /* === Potential Logo (top-left on content slides) === */
        .slide-logo {
            position: absolute;
            top: 24px;
            left: 40px;
        }

        .slide-logo svg {
            width: 120px;
            height: auto;
        }

        /* === Print === */
        @media print {
            body { overflow: visible; background: white; }
            .slides-container { height: auto; overflow: visible; }
            .slide {
                position: relative;
                transform: none;
                opacity: 1;
                page-break-after: always;
                height: 100vh;
            }
            .slide.prev { transform: none; opacity: 1; }
            .nav-bar, .slide-counter, .fullscreen-btn { display: none; }
        }
    </style>
</head>
<body>
```

> The template above provides the CSS framework. When generating, produce the complete HTML with all slide content filled in. See Section 4.5 for slide content templates.

### 4.5 Slide Content Templates

#### Slide 1: Cover
```html
<div class="slide slide-cover active" data-slide="0">
    <div class="project-label">KICKOFF MEETING</div>
    <div class="project-name">[PROJECT_NAME]</div>
    <div class="client-name">[CLIENT_NAME]</div>
    <div class="project-date">[START_MONTH] ~ [END_MONTH]</div>
    <div class="copyright">Copyright [YEAR]. Potential INC. All rights reserved</div>
</div>
```

#### Slide 2: Team
```html
<div class="slide" data-slide="1">
    <div class="slide-logo"><!-- LOGO_SVG_DARK --></div>
    <div class="section-number">02</div>
    <div class="slide-title">Team</div>

    <div class="team-section-label">Leadership</div>
    <div class="team-grid">
        <div class="team-member">
            <div class="team-avatar executive">L</div>
            <div class="member-name">Lukas</div>
            <div class="member-role">CEO</div>
        </div>
        <div class="team-member">
            <div class="team-avatar executive">S</div>
            <div class="member-name">Siam</div>
            <div class="member-role">CTO</div>
        </div>
        <div class="team-member">
            <div class="team-avatar executive">J</div>
            <div class="member-name">Jayden</div>
            <div class="member-role">COO</div>
        </div>
    </div>

    <hr class="team-divider">

    <div class="team-section-label">Project Team</div>
    <div class="team-grid">
        <!-- Repeat for each project team member -->
        <div class="team-member">
            <div class="team-avatar">[INITIAL]</div>
            <div class="member-name">[NAME]</div>
            <div class="member-role">[ROLE]</div>
        </div>
    </div>
</div>
```

The avatar shows the first character of the member's name. For Korean names, use the first syllable. For English names, use the first letter.
- Executive avatars use `.team-avatar.executive` (dark `#050042` background)
- Project team avatars use `.team-avatar` (purple `#624DFF` background)

#### Slide 3: Index
Content slide listing all sections (01~08) as a vertical list. Each item shows the section number and title. Style with `.agenda-list` / `.agenda-item` pattern.

Sections:
```
01  Team
02  Tech Stack
03  Timeline
04  Weekly Tasks
05  Communication
06  Deliverables
07  Meeting Agenda
08  Q&A
```

#### Slide 4: Tech Stack
Display selected technologies as `.tech-card` items in a grid.

Tech icon mappings (use first letter as icon text):
| Tech | Icon Letter | Description |
|------|-------------|-------------|
| React | R | Frontend Web Framework |
| React Native | RN | Cross-platform Mobile Framework |
| NestJS | N | Backend API Framework (Node.js) |
| Django | D | Backend API Framework (Python) |
| PostgreSQL | P | Relational Database |
| TypeScript | TS | Primary Language |

Always include PostgreSQL and TypeScript alongside the user's selection.

#### Slide 5: Timeline (Gantt Chart)
Render a `.gantt-table` with:
- Columns: Phase name + one column per week (grouped by month headers)
- Rows: One per phase (PM, Design, DB/Backend, Frontend, QA, Deploy)
- Colored bars spanning the active weeks for each phase

Use `colspan` for month groupings in the header row.

#### Slide 6: Weekly Tasks
Render `.task-card` items in a `.tasks-grid`. Each card shows:
- Week number label
- Comma-separated list of active tasks for that week

If the project exceeds 12 weeks, split into two slides (Weeks 1-12, Weeks 13+).

#### Slide 7: Communication
Two `.info-card` items side by side:

**Card 1 — Slack**
- Icon: `#` (hash symbol)
- Title: Slack
- Description: "Real-time communication channel for project updates, questions, and quick coordination."

**Card 2 — Project Dashboard**
- Icon: `📊` (or grid icon via SVG)
- Title: Project Dashboard
- Description: "Track project progress, milestones, and deliverables."
- Link: pm.potentialai.com

#### Slide 8: Deliverables
Two `.info-card` items:

**Card 1 — PRD**
- Title: PRD (Product Requirements Document)
- Description: "Comprehensive requirements document defining features, user stories, and acceptance criteria."

**Card 2 — Swagger**
- Title: Swagger (API Documentation)
- Description: "Interactive API documentation for all backend endpoints. Available after backend development phase."

#### Slide 9: Meeting Agenda
Standard agenda items using `.agenda-list`:
1. Project overview & scope confirmation
2. Tech stack & architecture
3. Timeline & milestones review
4. Communication & collaboration process
5. Q&A and open discussion

#### Slide 10: Q&A
```html
<div class="slide slide-qa" data-slide="9">
    <div class="qa-title">Q&A</div>
    <div class="qa-sub">Questions & Discussion</div>
</div>
```

#### Slide 11: Thank You
```html
<div class="slide slide-thankyou" data-slide="10">
    <div class="thankyou-title">THANK YOU</div>
    <div class="contact-email">contact@potentialai.com</div>
    <div class="copyright">Copyright [YEAR]. Potential INC. All rights reserved</div>
</div>
```

### 4.6 JavaScript (Navigation)

Include at the bottom of `<body>`:

```javascript
<script>
(function() {
    const slides = document.querySelectorAll('.slide');
    let current = 0;

    function goTo(n) {
        if (n < 0 || n >= slides.length) return;
        slides[current].classList.remove('active');
        slides[current].classList.add(n > current ? 'prev' : '');
        slides.forEach((s, i) => {
            s.classList.remove('active', 'prev');
            if (i < n) s.classList.add('prev');
        });
        current = n;
        slides[current].classList.add('active');
        updateNav();
    }

    function next() { goTo(current + 1); }
    function prev() { goTo(current - 1); }

    function updateNav() {
        document.querySelectorAll('.nav-dot').forEach((d, i) => {
            d.classList.toggle('active', i === current);
        });
        document.querySelector('.slide-counter').textContent =
            (current + 1) + ' / ' + slides.length;
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); next(); }
        if (e.key === 'ArrowLeft') { e.preventDefault(); prev(); }
        if (e.key === 'f' || e.key === 'F') {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
    });

    document.querySelectorAll('.nav-dot').forEach((dot, i) => {
        dot.addEventListener('click', () => goTo(i));
    });

    document.querySelector('.fullscreen-btn').addEventListener('click', () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    });

    updateNav();
})();
</script>
```

### 4.7 Logo SVG

Use text-based SVG for the Potential logo on content slides:

```svg
<svg width="120" height="32" viewBox="0 0 120 32" xmlns="http://www.w3.org/2000/svg">
    <text x="0" y="24" font-family="Inter, sans-serif" font-size="22" font-weight="800" fill="#050042">Potential</text>
</svg>
```

For cover/thankyou slides (white version):
```svg
<svg width="120" height="32" viewBox="0 0 120 32" xmlns="http://www.w3.org/2000/svg">
    <text x="0" y="24" font-family="Inter, sans-serif" font-size="22" font-weight="800" fill="#ffffff">Potential</text>
</svg>
```

---

## Step 5: Playwright QA Verification (Auto)

After HTML generation, **automatically** verify the presentation using Playwright MCP before reporting to the user. This catches layout issues (overflow, clipping, element collision) that would otherwise surface only when the client opens the file.

### 5.1 Launch Browser

1. Navigate Playwright to the generated file: `file:///<absolute path to [Kickoff] PROJECT_NAME.html>`
2. Set viewport to **1920×1080** (Full HD projector standard)
3. Wait for network idle + 500ms for fonts to settle

### 5.2 Slide-by-Slide Inspection

For each slide from 0 to N-1:

1. Navigate to the slide:
   - Slide 0 is already active on load
   - Subsequent slides: click `.nav-dot[data-goto="N"]` or press `ArrowRight`
2. Wait 600ms for the transition animation to finish
3. Capture a full-page screenshot
4. Run DOM inspection (via Playwright `evaluate`):
   - **Vertical overflow**: `.slide.active` children extend below `window.innerHeight - 48px` (nav bar)
   - **Horizontal overflow**: any element `scrollWidth > clientWidth`
   - **Text clipping**: headings/paragraphs with `overflow: hidden` and truncated content
   - **Grid wrapping**: team/tech grid items breaking onto too many rows
   - **Nav-bar collision**: content covered by `.nav-bar`

### 5.3 Per-Slide Checklist

| Slide | Specific Checks |
|-------|-----------------|
| 1. Cover | `project-name` fits one line; `client-name` not wrapping mid-word; `project-date` visible above copyright |
| 2. Team | All members fit in grid without overflow; avatars not clipped; Leadership + Project Team both visible |
| 3. Index | All 8 sections visible without scroll |
| 4. Tech Stack | 2-column grid aligned; icons and text vertically centered in each card |
| 5. Timeline (Gantt) | All week columns visible; phase-col text not truncated; bars aligned to correct weeks |
| 6. Weekly Tasks | Cards fit grid; if too many → vertical scroll works; no horizontal scroll |
| 7. Communication | Two info-cards equal width; text fits in card |
| 8. Deliverables | Two info-cards equal width; text fits in card |
| 9. Meeting Agenda | All items visible without scroll |
| 10. Q&A | Centered; no overflow |
| 11. Thank You | Centered; copyright at bottom, not clipped |

### 5.4 Fix Issues

For each issue found, classify and apply the fix:

**Structural issue** (CSS/layout) → Fix in **BOTH** the generated HTML AND the skill template
- Examples: font-size too large causing wrap, grid column count wrong, padding misalignment, gap insufficient, max-width too small
- Propagate to: `~/.claude/skills/project-kickoff/skill.md` (section 4.4 CSS)
- Rationale: future generations benefit from the fix

**Content-specific issue** → Fix in the generated HTML only
- Examples: a particularly long client name needs `<br>`, a project name is too long for the chosen font-size, a team has 8+ members instead of typical 5
- Do NOT propagate to skill.md — these are project-specific

### 5.5 Re-Verify

After applying fixes, re-run Step 5.2 inspection to confirm all issues are resolved. Maximum **3 iterations**; if issues persist after 3 rounds, report the remaining ones to the user in Step 6 and let them decide.

### 5.6 Close Browser

Close the Playwright browser session after verification is complete (pass or max iterations).

### 5.7 QA Report (feed into Step 6)

Collect findings for the final report:
- Slides inspected: N
- Issues found: M
- Issues auto-fixed: K
- Issues propagated to skill.md: J (structural only)
- Remaining issues: M - K (reported to user)

---

## Step 6: Report Result

### Success Message

```
Kickoff presentation generated and verified.

File: [OUTPUT_PATH]
Slides: [SLIDE_COUNT]
Project: [PROJECT_NAME]
Client: [CLIENT_NAME]
Duration: [START] ~ [END] ([N] weeks)

QA (Playwright, 1920×1080):
- Slides inspected: [N]
- Issues found: [M]
- Auto-fixed in HTML: [K]
- Propagated to skill template: [J]
- Remaining issues: [M - K] ([list or "none"])

Open the HTML file in a browser to present.
- Arrow keys: Navigate slides
- F: Toggle fullscreen
- Click dots: Jump to slide
```

---

## Fixed Content Reference

### Communication Tools (hardcoded)
- **Slack**: Real-time communication
- **pm.potentialai.com**: Project dashboard with client view

### Deliverables (hardcoded)
- **PRD**: Product Requirements Document
- **Swagger**: API Documentation

### Company Info (hardcoded)
- Company: Potential INC
- Email: contact@potentialai.com
- Copyright year: Current year

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Project name missing | Ask via AskUserQuestion |
| Client name missing | Ask via AskUserQuestion |
| Tech stack not selected | Ask via AskUserQuestion |
| Duration not provided | Ask via AskUserQuestion |
| Phase breakdown unclear | Provide sensible defaults, ask to confirm |
| User cancels at confirmation | Stop and report |
| Playwright MCP unavailable | Skip Step 5 QA, warn user in Step 6 report, continue with HTML file |
| QA iteration limit reached (3) | Report remaining issues in Step 6, let user decide whether to fix manually |
| Screenshot/inspection fails mid-run | Close browser, report partial QA results, do not block the final output |

---

## Examples

### Example 1: Full Arguments

```bash
/kickoff-meeting --project "Activity Coaching" --client "김철수 대표님"
```
-> Asks for: tech stack, duration, phase breakdown
-> Output: `[Kickoff] Activity Coaching.html`

### Example 2: No Arguments (Fully Interactive)

```bash
/kickoff-meeting
```
-> Asks for: everything (project name, client, tech stack, duration, phases)
-> Brief confirmation -> Generate

### Example 3: Mobile Project

```bash
/kickoff-meeting --project "Health App"
```
-> User selects: React Native + NestJS
-> Duration: 2026.05 ~ 2026.09 (20 weeks)
-> Output: `[Kickoff] Health App.html`
