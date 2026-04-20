---
name: project-launch
description: "Project launch orchestrator. Runs a single unified interview and generates BOTH the kickoff HTML presentation AND the Project Overview Slack Canvas from a draft PRD. Use this at project start (contract signed → before PRD refinement). For regeneration or updates of a single artifact later, use /project-kickoff or /project-overview directly."
user-invocable: true
argument-hint: "[--project 'name'] [--client 'name'] [--channel 'name|id']"
---

# Project Launch Orchestrator

Generate **both** launch artifacts in one pass:

1. **Kickoff Presentation** (HTML slides) — for the in-person/video kickoff meeting
2. **Project Overview** (Slack Canvas) — pinned in the client communication channel as a living reference

Both deliverables are designed for the **draft PRD phase**: contract signed, initial PRD drafted, but PRD refinement has not yet begun. They share most source data, so this orchestrator collects it once and produces both.

> **When NOT to use this skill**: If you only need to regenerate one artifact (e.g., updating the canvas after a team change), use `/project-kickoff` or `/project-overview` directly. This orchestrator is specifically for the initial launch.

---

## Workflow Overview

```
Step 1: Detect artifacts (.claude-project/) + CLAUDE.md auto-read
Step 2: Unified interview (collect everything once)
Step 3: Confirm consolidated summary
Step 4: Generate kickoff HTML (delegate to project-kickoff logic)
Step 5: Generate overview canvas markdown (delegate to project-overview logic)
Step 6: Create Slack Canvas + share in channel
Step 7: Report both artifacts together
```

---

## Step 1: Detection Phase

Do the detection work that both downstream skills need, **once**:

1. **Scan `.claude-project/`** per the project-overview detection map:
   - `prd/*_PRD.md` → PRD path + flag as draft (default maturity)
   - `design/DESIGN_SYSTEM_*.md` → all variants, ask user to pick
   - `design/*_DesignGuide.md`, `*_DomainResearch.md`
   - `user_stories/*.yaml` → count
   - `docs/PROJECT_*.md` → list found docs
   - `status/*/` → list tracking areas

2. **Read `CLAUDE.md`** and extract:
   - Project name, description, tech stack, status, user roles
   - Skip any `{PLACEHOLDER}` values

3. **Report detection summary** before asking questions:
   ```
   Detected:
   - PRD: [found/not found]
   - Design system variants: [N variants (A-I)]
   - User stories: [N screens]
   - Project docs: [list]
   - CLAUDE.md: [project name auto-filled]
   ```

---

## Step 2: Unified Interview

Collect **every field both skills need** in grouped rounds. Pre-fill from detection. Skip anything provided via arguments.

### Round 1 — Project Basics

1. **Project name** (pre-filled from CLAUDE.md)
2. **Client name with honorific** — e.g., "우림에프엔비 / 김철수 대표님"
3. **One-line description** (pre-filled from CLAUDE.md)
4. **Tech stack** (pre-filled from CLAUDE.md, confirm)
5. **Project duration** — e.g., "2026.04 ~ 2026.07"

### Round 2 — Team

Leadership auto-included (do not ask): Lukas (CEO), Siam (CTO), Jayden (COO).

1. **Project team members** — "역할: 이름" pairs (PM, Designer, Backend, Frontend, QA)

### Round 3 — Design System & PRD Maturity

Only ask if detection found ambiguous items:

1. **Design system variant** — "디자인 시스템 변형이 N개 발견되었습니다. 이번 프로젝트에서 사용할 버전은?" (options A-I from detection)
2. **PRD maturity** — Default to "초안 (Draft)" since this is the project launch phase. Confirm with: "PRD는 초안 상태로 표시됩니다. 맞습니까? (Y/변경)"

### Round 4 — Phases & Communication

Pre-fill phases from project duration:
```
1. 기획 (PM/Planning): 1-2주차
2. 디자인: 2-4주차
3. 백엔드: 3-8주차
4. 프론트엔드: 5-10주차
5. QA: 9-12주차
6. 배포: 11-12주차
```

1. **Phase breakdown** — confirm or adjust
2. **Meeting cadence** — "정기 미팅 일정? (예: 매주 월요일 오후 2시)"

### Round 5 — Slack Channel

1. **Target channel** — "Project Overview Canvas를 어느 Slack 채널에 게시할까요?"
   - Resolve via `mcp__claude_ai_Slack__slack_search_channels` if name is given
   - If multiple matches, ask user to pick

---

## Step 3: Confirm Consolidated Summary

Present a single summary covering both artifacts:

```
## 프로젝트 런치 — 요약

### 공통 정보
- 프로젝트: [PROJECT_NAME]
- 클라이언트: [CLIENT_NAME]
- 기간: [START] ~ [END] ([N]주)
- 팀: Lukas (CEO), Siam (CTO), Jayden (COO), [PROJECT_MEMBERS]
- 기술 스택: [TECH_STACK]

### 생성될 산출물
1. 킥오프 프레젠테이션 (HTML)
   → [Kickoff] [PROJECT_NAME].html

2. 프로젝트 개요 캔버스 (Slack Canvas)
   → [프로젝트 개요] [PROJECT_NAME]
   → 게시 대상: #[CHANNEL_NAME]

### 감지된 산출물 (캔버스에 반영)
- PRD: 초안 ([PRD_PATH or "없음"])
- 디자인 시스템: 변형 [LETTER] ([DESIGN_PATH or "없음"])
- 유저 스토리: [N]개 화면
- API/DB 문서: [count]개 파일

두 산출물을 생성할까요? (Y/조정)
```

---

## Step 4: Generate Kickoff HTML (+ Auto QA)

Follow the full HTML generation logic from `~/.claude/skills/project-kickoff/skill.md`. Specifically:

- Use the HTML template, slide structure (11 slides), brand guidelines, and JavaScript navigation from that skill
- Output filename: `[Kickoff] {PROJECT_NAME}.html` in the project root
- Do not re-interview — use the data already collected in Step 2
- **Then run Playwright QA**: follow `project-kickoff/skill.md` Step 5 (Playwright QA Verification) verbatim — 1920×1080 viewport, slide-by-slide inspection, auto-fix with structural fixes propagated to the skill template. Collect the QA report for Step 7.

> **Reference**: See `~/.claude/skills/project-kickoff/skill.md` sections 4.1-4.7 for the HTML template and Step 5 for the QA procedure.

---

## Step 5: Generate Overview Canvas Markdown

Follow the Korean canvas template from `~/.claude/skills/project-overview/skill.md` Step 6. Specifically:

- Use the Korean `# {PROJECT_NAME} - 프로젝트 개요` markdown template verbatim
- Fill in all placeholders from Step 2 data + Step 1 detection
- Mark PRD as `_초안 (Draft)_`
- Check artifact checkboxes per the rules in that skill

> **Reference**: See `~/.claude/skills/project-overview/skill.md` Step 6 for full Korean canvas template.

---

## Step 6: Create & Share Canvas

1. Call `mcp__claude_ai_Slack__slack_create_canvas`:
   ```
   title: "[프로젝트 개요] {PROJECT_NAME}"
   content: {Korean markdown from Step 5}
   ```

2. Store returned `canvas_id` and canvas link.

3. Call `mcp__claude_ai_Slack__slack_send_message` to the target channel:
   ```
   :rocket: *프로젝트가 시작되었습니다 — {PROJECT_NAME}*

   {CANVAS_LINK}

   이 캔버스에는 프로젝트 기본 정보, 팀, 일정, 주요 산출물 링크가 포함되어 있습니다.
   오늘 킥오프 미팅에서 더 자세한 내용을 공유드리며, 캔버스는 프로젝트 진행 중 지속적으로 업데이트됩니다.
   ```

---

## Step 7: Report Result

```
프로젝트 런치 준비 완료.

[1/2] 킥오프 프레젠테이션
→ [Kickoff] {PROJECT_NAME}.html
→ 브라우저에서 열어 프레젠테이션 가능 (화살표 키 이동, F 전체화면)
→ Playwright QA: {N}개 슬라이드 검증, {M}개 이슈 발견, {K}개 자동 수정 ({J}개 템플릿 반영)

[2/2] 프로젝트 개요 캔버스
→ {CANVAS_LINK}
→ 채널 #{CHANNEL_NAME}에 공유 완료
→ Canvas ID: {CANVAS_ID}

감지된 산출물:
- PRD: 초안 ({PRD_PATH or "없음"})
- 디자인 시스템: 변형 {LETTER}
- 유저 스토리: {N}개 화면
- API/DB 문서: {count}개 파일

다음 단계: PRD 고도화 → /update-prd 또는 /generate-prd
캔버스 업데이트 시: /project-overview --update {CANVAS_ID}
킥오프 재생성 시: /project-kickoff
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| HTML generation fails but canvas succeeds | Report canvas link; surface HTML error; suggest `/project-kickoff` to retry |
| Canvas creation fails but HTML succeeds | Report HTML file; print canvas markdown to console as fallback |
| Both fail | Report both errors; no partial cleanup needed |
| Slack MCP unavailable | Skip canvas step, generate HTML only, warn user |
| No `.claude-project/` | Proceed with interview-only flow; artifacts section marked "_(아직 생성되지 않음)_" |
| User cancels at Step 3 | Stop; no files created |

---

## Relationship to Other Skills

| Skill | When to Use |
|-------|-------------|
| `/project-launch` (this) | Initial project start — generate BOTH artifacts together from draft PRD |
| `/project-kickoff` | Regenerate kickoff HTML only (e.g., team changed, timeline shifted) |
| `/project-overview` | Update canvas only (`--update <canvas_id>`) or create canvas independently later |
| `/update-prd` / `/generate-prd` | Next phase — PRD refinement after launch artifacts are delivered |

---

## Example

```
/project-launch --client "우림에프엔비 / 김철수 대표님" --channel "woorim-market"
```

Flow:
1. Detects PRD draft, 9 design variants, 14 user stories in `.claude-project/`
2. Reads CLAUDE.md → project name "woorim-market", tech stack auto-filled
3. Interviews: duration, team, design variant (picks B), phases, meeting cadence
4. Confirms summary
5. Generates `[Kickoff] woorim-market.html`
6. Creates canvas `[프로젝트 개요] woorim-market` and posts to `#woorim-market`
7. Reports both artifacts with next-step guidance
