---
name: project-overview
description: "Create or update a Project Overview Slack Canvas for the client communication channel. Auto-detects project artifacts (PRD, Design System, User Stories, API/DB docs) from .claude-project/, collects missing info via interview, generates a structured canvas in Korean, and shares it in the target Slack channel. For the initial project start, prefer /project-launch which generates this AND the kickoff HTML together from one interview."
user-invocable: true
argument-hint: "[--project 'name'] [--client 'name'] [--channel 'name|id'] [--update <canvas_id>]"
---

# Project Overview Canvas Generator

Create a **living Project Overview** as a Slack Canvas, pinned in the client communication channel. This is a reference document — distinct from `/project-kickoff`, which produces an HTML presentation for the kickoff meeting.

The overview answers: *"What is this project, who is on it, what artifacts exist, where are we in the process?"* — at a glance, always up to date.

> **Paired with Kickoff**: At project start, the Project Overview and the kickoff HTML are generated together from the draft PRD. Use `/project-launch` to produce both at once. Use this skill (`/project-overview`) standalone only for canvas updates (`--update <canvas_id>`) or when creating a canvas for an already-running project.

> **Important**: The skill instructions below are in English, but the **final canvas content posted to Slack must be in Korean** (it is client-facing). Use the Korean template in Step 6 verbatim.

---

## Workflow Overview

```
Step 1: Scan .claude-project/ → Detect existing artifacts
Step 2: Auto-detect project info from CLAUDE.md
Step 3: Confirm ambiguous items (design variant, PRD maturity, channel)
Step 4: Interview for missing fields
Step 5: Confirm summary
Step 6: Generate canvas markdown (Korean)
Step 7: Create canvas via Slack MCP
Step 8: Share canvas link in target channel
Step 9: Report result
```

---

## Step 1: Artifact Detection

Scan the current working directory for `.claude-project/`. If it exists, detect the following artifacts using Glob and Read tools.

### Detection Map

| Path Pattern | What to Detect | Reported As |
|--------------|----------------|-------------|
| `.claude-project/prd/*_PRD.md` | First match | "PRD: found at {path}" — flag for maturity confirmation |
| `.claude-project/design/DESIGN_SYSTEM_*.md` | All matches | "Design System: N variants ({A, B, C, ...})" — ask user to pick |
| `.claude-project/design/*_DesignGuide.md` | First match | Link in Resources section |
| `.claude-project/design/*_DomainResearch.md` | First match | Link in Resources section |
| `.claude-project/user_stories/*.yaml` | Count files | "User Stories: N screens defined" |
| `.claude-project/docs/PROJECT_KNOWLEDGE.md` | Exists? | Link in artifacts |
| `.claude-project/docs/PROJECT_API.md` | Exists? | Link in artifacts |
| `.claude-project/docs/PROJECT_DATABASE.md` | Exists? | Link in artifacts |
| `.claude-project/docs/PROJECT_API_INTEGRATION.md` | Exists? | Link in artifacts |
| `.claude-project/status/*/` | Subdir names | List status tracking areas (backend, frontend, mobile, ...) |

### If `.claude-project/` does not exist

Skip artifact detection. The artifacts section in the canvas will be marked as "아직 생성되지 않음" for each entry, and the skill proceeds with full interview.

---

## Step 2: Auto-Detect from CLAUDE.md

Read `CLAUDE.md` from the project root if present. Extract these fields where possible (skip placeholders like `{PROJECT_NAME}`):

| Canvas Field | CLAUDE.md Source |
|--------------|------------------|
| Project name | `**Project**: value` in Overview |
| Project description | Overview paragraph |
| Tech stack | Tech Stack table |
| Status | `**Status**: value` |
| User roles | User Roles table |

Treat any value matching `{...}` placeholder pattern as missing.

---

## Step 3: Confirm Ambiguous Items

Use AskUserQuestion to resolve detection ambiguities. Group into one round when possible.

### 3.1 Design System Variant (if multiple variants found)

```
Question: "디자인 시스템 변형이 N개 발견되었습니다. 이번 프로젝트에서 사용할 버전은?"
Options: List each variant (A, B, C, ...) with the file path
```

Save the selected variant letter and file path.

### 3.2 PRD Maturity (if PRD found)

```
Question: "PRD가 {path}에 있습니다. 현재 성숙도는?"
Options:
- 초안 (Draft) — 추가 보완 필요 (early-stage 기본값, Recommended)
- 검토 중 (In Review) — 클라이언트 검토 진행 중
- 검토 완료 (Reviewed) — 피드백 반영 완료
- 승인됨 (Approved) — 최종 확정
```

### 3.3 Slack Channel Target

```
Question: "어느 Slack 채널에 게시할까요?"
```

If the user provides a name (not an ID starting with `C`), call `mcp__claude_ai_Slack__slack_search_channels` to resolve. If multiple matches, ask user to pick.

---

## Step 4: Interview for Missing Fields

Only ask for fields that were not auto-detected or provided via arguments.

### Conversation-Level Reuse Check

Before starting the interview, check if `/project-kickoff` was run earlier in the same session. If so:

```
"이번 세션에서 /project-kickoff을 실행하셨네요. 동일한 프로젝트 정보
(클라이언트, 기간, 팀, 단계)를 캔버스에 재사용할까요? (Y/조정)"
```

If yes, skip to Step 5. Otherwise, proceed with the interview below.

### Round 1 — Project Basics (skip auto-detected fields)

1. **Project name** — pre-filled from CLAUDE.md if available
2. **Client name with honorific** — e.g., "우림에프엔비 / 김철수 대표님"
3. **One-line description** — "이 프로젝트를 한 문장으로 설명한다면?" (pre-fill from CLAUDE.md)
4. **Tech stack** — pre-fill from CLAUDE.md, confirm
5. **Project duration** — "프로젝트 시작/종료 월? (예: 2026.04 ~ 2026.07)"

### Round 2 — Team & Communication

Leadership is always auto-included (do not ask):
- Lukas (CEO), Siam (CTO), Jayden (COO)

1. **Project team members** — "프로젝트 팀 구성원? (역할: 이름)"
2. **Meeting cadence** — "정기 미팅 일정? (예: 매주 월요일 오후 2시)"

### Round 3 — Phase Breakdown

Pre-fill based on the project duration. Ask user to confirm or adjust:

```
1. 기획 (PM/Planning): 1-2주차
2. 디자인 (Design): 2-4주차
3. 백엔드 개발 (Backend): 3-8주차
4. 프론트엔드 개발 (Frontend): 5-10주차
5. QA/테스팅: 9-12주차
6. 배포 (Deploy): 11-12주차
```

---

## Step 5: Confirm Summary

Present a brief summary in Korean before generation:

```
## 프로젝트 개요 캔버스 — 요약

- 프로젝트: [PROJECT_NAME]
- 클라이언트: [CLIENT_NAME]
- 기간: [START] ~ [END] ([N]주)
- 팀: Lukas (CEO), Siam (CTO), Jayden (COO), [PROJECT_MEMBERS]
- 기술 스택: [TECH_STACK]
- 대상 채널: #[CHANNEL_NAME] ([CHANNEL_ID])

## 감지된 산출물
- PRD: [status] ([path or "없음"])
- 디자인 시스템: 변형 [LETTER] ([path or "없음"])
- 유저 스토리: [N]개 화면 ([path or "없음"])
- API 문서: [path or "없음"]
- DB 스키마: [path or "없음"]

캔버스를 생성할까요? (Y/조정)
```

---

## Step 6: Generate Canvas Markdown (Korean)

Build the canvas content using the Korean template below. Replace `{...}` placeholders with collected values. For artifacts that were not found, mark as `_(아직 생성되지 않음)_`.

### Canvas Title

```
[프로젝트 개요] {PROJECT_NAME}
```

### Canvas Content Template (Korean — verbatim, do not translate to English)

```markdown
# {PROJECT_NAME} - 프로젝트 개요

> {ONE_LINE_DESCRIPTION}

---

## 기본 정보

| 항목 | 내용 |
|------|------|
| 클라이언트 | {CLIENT_NAME} |
| 프로젝트 | {PROJECT_NAME} |
| 기간 | {START_MONTH} ~ {END_MONTH} (총 {N}주) |
| 상태 | {STATUS} |
| 대시보드 | [pm.potentialai.com](https://pm.potentialai.com) |

---

## 팀 구성

**Leadership**
- Lukas — CEO
- Siam — CTO
- Jayden — COO

**프로젝트 팀**
- {ROLE}: {NAME}
- {ROLE}: {NAME}

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | {FRONTEND} |
| Backend | {BACKEND} |
| Database | {DATABASE} |
| Deployment | {DEPLOYMENT} |

---

## 프로젝트 산출물

- [{X}] **PRD (요구사항 정의서)** — _{PRD_STATUS}_ ({PRD_PATH or "아직 생성되지 않음"})
- [{X}] **디자인 시스템** — 변형 {LETTER} 선정 ({DESIGN_PATH or "아직 생성되지 않음"})
- [{X}] **유저 스토리** — {N}개 화면 ({USER_STORIES_PATH or "아직 생성되지 않음"})
- [{X}] **API 문서** — ({API_DOC_PATH or "백엔드 단계에서 생성 예정"})
- [{X}] **데이터베이스 스키마** — ({DB_DOC_PATH or "백엔드 단계에서 생성 예정"})

> **참고**: 초안 상태로 표시된 산출물은 추가 보완 중입니다. 클라이언트 검토 및 피드백을 환영합니다.

---

## 프로젝트 단계

- [ ] **1단계: 기획 (PM/Planning)** — {X}-{Y}주차
- [ ] **2단계: 디자인 (Design)** — {X}-{Y}주차
- [ ] **3단계: 백엔드 개발 (Backend)** — {X}-{Y}주차
- [ ] **4단계: 프론트엔드 개발 (Frontend)** — {X}-{Y}주차
- [ ] **5단계: QA / 테스팅** — {X}-{Y}주차
- [ ] **6단계: 배포 (Deploy)** — {X}-{Y}주차

---

## 커뮤니케이션

| 채널 | 용도 |
|------|------|
| ![](#{CHANNEL_ID}) | 주요 프로젝트 커뮤니케이션 |
| [프로젝트 대시보드](https://pm.potentialai.com) | 진행 상황 및 마일스톤 추적 |

**정기 미팅**: {MEETING_CADENCE}

---

## 주요 마일스톤

- [ ] PRD 최종 확정
- [ ] 디자인 승인
- [ ] 백엔드 API 완성
- [ ] 프론트엔드 완성
- [ ] QA 통과
- [ ] 프로덕션 배포

---

## 참고 자료

- 대시보드: [pm.potentialai.com](https://pm.potentialai.com)
- 문의: [contact@potentialai.com](mailto:contact@potentialai.com)

---

*Potential INC | Copyright {YEAR}*
```

### Checkbox Rules

For the **프로젝트 산출물** section, check `[x]` if:
- PRD: status is "승인됨 (Approved)"
- 디자인 시스템: variant has been selected
- 유저 스토리: at least 1 yaml file exists
- API/DB 문서: file exists

Otherwise leave as `[ ]`.

---

## Step 7: Create Canvas via Slack MCP

### New Canvas (default)

Call `mcp__claude_ai_Slack__slack_create_canvas`:

```
title: "[프로젝트 개요] {PROJECT_NAME}"
content: {generated Korean markdown from Step 6}
```

Store the returned `canvas_id` and canvas link.

### Update Existing Canvas (`--update <canvas_id>`)

If the user passed `--update <canvas_id>`:

1. Warn the user (in Korean):
   ```
   "캔버스 전체 내용이 교체됩니다. 수동으로 체크한 항목 등은 초기화됩니다. 진행할까요? (Y/n)"
   ```
2. Call `mcp__claude_ai_Slack__slack_update_canvas`:
   ```
   canvas_id: <provided>
   action: "replace"
   content: {generated Korean markdown}
   ```
   (No `section_id` — full replacement is intentional here.)

---

## Step 8: Share Canvas in Channel

Call `mcp__claude_ai_Slack__slack_send_message`:

**For new canvas:**

```
channel_id: {resolved channel ID}
message:
:pushpin: *프로젝트 개요가 생성되었습니다*

{CANVAS_LINK}

이 캔버스에는 프로젝트 기본 정보, 팀 구성, 일정, 주요 산출물 링크가 포함되어 있습니다.
프로젝트 진행 중 산출물이 추가/업데이트되며, 체크리스트를 통해 진행 상황을 확인하실 수 있습니다.
```

**For update mode:**

```
:arrows_counterclockwise: *프로젝트 개요가 업데이트되었습니다*

{CANVAS_LINK}
```

---

## Step 9: Report Result

```
프로젝트 개요 캔버스가 생성되었습니다.

캔버스: [CANVAS_LINK]
채널: #[CHANNEL_NAME]
프로젝트: [PROJECT_NAME]
클라이언트: [CLIENT_NAME]

감지된 산출물:
- PRD: [status]
- 디자인 시스템: 변형 [LETTER]
- 유저 스토리: [N]개 화면
- API/DB 문서: [count]개 파일

업데이트 시: /project-overview --update [CANVAS_ID]
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| No `.claude-project/` directory | Skip artifact detection, proceed with full interview |
| CLAUDE.md not found | Skip auto-detection |
| CLAUDE.md has placeholder values (`{...}`) | Treat as missing, ask via interview |
| Multiple design system variants | Ask user to pick via AskUserQuestion |
| No PRD found | Mark as "_(아직 생성되지 않음)_" in canvas |
| Slack channel not found | Ask user to verify name or provide channel ID |
| `slack_create_canvas` fails | Print full markdown to console as fallback so user can manually create |
| `slack_send_message` fails | Canvas was created; report canvas link directly, warn about message failure |
| `--update` with invalid canvas_id | Report error, suggest creating new canvas |
| Slack MCP not available | Error: "Slack MCP integration is required" |

---

## Fixed Content Reference

### Leadership (always included, plain text — no @mentions)
- Lukas — CEO
- Siam — CTO
- Jayden — COO

### Communication
- Slack channel (resolved at runtime)
- pm.potentialai.com (project dashboard)

### Company Info
- Company: Potential INC
- Email: contact@potentialai.com
- Copyright year: Current year

---

## Examples

### Example 1: Full auto-detection in woorim-market

```
/project-overview --client "우림에프엔비 / 김철수 대표님" --channel "woorim-market"
```

Skill detects:
- PRD at `.claude-project/prd/woorim-market_PRD.md`
- 9 design system variants (A-I) → asks user to pick
- 14 user story yaml files
- All 4 PROJECT_*.md docs

Then asks: design variant?, PRD maturity?, project duration, team, phases.

Generates Korean canvas, posts to `#woorim-market` channel.

### Example 2: Update mode

```
/project-overview --update F0123456789
```

Re-collects/confirms info, replaces existing canvas content, posts update notification in Korean.

### Example 3: No `.claude-project/`

```
/project-overview --project "Health App" --channel "health-app-client"
```

Falls back to full interview (no artifact detection). Generates Korean canvas with all artifacts marked as "_(아직 생성되지 않음)_".
