# claude-operations

Claude Code operations skills - PRD generation, SOP creation, presentations, deployment, workflow automation, and full-stack QA.

## Overview

This repo contains operations-focused skills for Claude Code. Add it as a submodule to projects that need document generation, deployment workflows, project management, or automated QA capabilities.

## Installation

```bash
cd your-project/.claude
git submodule add https://github.com/potentialInc/claude-operations.git operations
```

## Available Skills

### PRD Lifecycle (`skills/prd/`)

| Skill | Description | Usage |
|-------|-------------|-------|
| `generate-prd` | Generate comprehensive PRD from client input | `/generate-prd <input-file>` |
| `generate-korean-prd` | Generate Korean PRD with company watermark | `/generate-korean-prd <input-file>` |
| `update-prd` | Update PRD with client feedback | `/update-prd <feedback-file>` |
| `pdf-to-prd` | Convert PRD PDF to structured markdown | `/pdf-to-prd <pdf-file>` |
| `generate-tech-prd` | Generate Technical PRD (Phase B) from Feature PRD | `/generate-tech-prd <prd-file>` |
| `input-classifier` | Auto-classify input before PRD modification | Auto-triggered on PRD edit |

### Document Generation (`skills/docs/`)

| Skill | Description | Usage |
|-------|-------------|-------|
| `generate-ppt` | Generate HTML presentations with branding | `/generate-ppt <topic>` |
| `generate-sop` | Generate SOP and create in Notion | `/generate-sop <process>` |
| `generate-invoice` | Generate invoice (견적서) HTML/PDF | `/generate-invoice` |
| `generate-statement` | Generate transaction statement (거래명세서) HTML/PDF | `/generate-statement` |
| `generate-project-report` | Generate Korean project result report | `/generate-project-report <repo-path>` |
| `generate-random-project` | Generate random project specs for training | `/generate-random-project` |
| `review-command` | Review skill file compatibility | `/review-command <skill-file>` |

### QA Skills (`skills/qa/`) — 7 individual + 1 orchestrator

Framework-agnostic full-stack QA auditing. Works with any frontend (React, Vue, Angular, Svelte) and backend (NestJS, Express, Spring Boot, Django, Laravel).

| Skill | Description | Usage |
|-------|-------------|-------|
| `qa-api` | API layer audit — CRUD, sync, response shapes | `/qa-api [module]` |
| `qa-data` | Data layer audit — schema, migrations, indexes | `/qa-data [module]` |
| `qa-form` | Full-stack input field consistency | `/qa-form [module]` |
| `qa-guard` | Auth & security audit — guards, permissions | `/qa-guard [module]` |
| `qa-runtime` | Playwright-based browser QA | `/qa-runtime [module]` |
| `qa-scan` | Universal QA orchestrator (quick/standard/deep) | `/qa-scan [module]` |
| `qa-ui` | UI/UX layer audit — states, modals, a11y | `/qa-ui [module]` |

### Store Submission (`skills/store/`)

| Skill | Description | Usage |
|-------|-------------|-------|
| `store-prep` | App store submission preparation | `/store-prep` |
| `store-assets` | App icon, screenshots, splash screen | `/store-assets` |
| `store-native` | Capacitor native app wrapper | `/store-native` |
| `store-deploy` | Production server deployment | `/store-deploy` |
| `store-build` | Release build (AAB/IPA) | `/store-build` |
| `store-submit` | Store console upload & submission | `/store-submit` |
| `store-review` | Store rejection handling | `/store-review` |
| `store-ship` | Full pipeline orchestrator | `/store-ship` |

### Workflow Skills

| Skill | Description | Usage |
|-------|-------------|-------|
| `deployment` | Deploy to dev/staging/production | Context-triggered |
| `iteration-manager` | Fullstack pipeline iteration cycles | Context-triggered |
| `create-dev-pr` | Create PR to dev branch | Context-triggered |
| `code-cleanup` | Analyze and remove dead code | `/code-cleanup` |

### Knowledge Base (`skills/kb/`)

| Skill | Description | Usage |
|-------|-------------|-------|
| `kb` | Knowledge base management — ingest, compile, query | `/kb <command> [project]` |

**Commands:**
- `/kb ingest <project> <type> <path>` — Ingest Slack exports, standups, meetings
- `/kb standup <project>` — Log today's standup
- `/kb decision <project> "<title>"` — Record architecture decision
- `/kb ask "<question>"` — Query knowledge base
- `/kb compile <project> [weekly|monthly]` — Generate summaries
- `/kb reindex` — Rebuild all indexes
- `/kb recent [days]` — Show recent activity
- `/kb search "<query>"` — Full-text search

## Available Agents

| Agent | Description | Invocation |
|-------|-------------|------------|
| `prd-manager` | PRD lifecycle dashboard, question tracking, Safety Gate guardian | "PRD status" or "Review these changes" |

## Structure

```
claude-operations/
├── README.md
├── CLAUDE.md
├── agents/
│   └── prd-manager.md
├── skills/
│   ├── prd/
│   │   ├── generate-prd/
│   │   │   ├── SKILL.md
│   │   │   └── references/           ← Supporting files
│   │   ├── generate-korean-prd/
│   │   │   └── SKILL.md
│   │   ├── generate-tech-prd/
│   │   │   ├── SKILL.md
│   │   │   └── references/           ← Supporting files
│   │   ├── update-prd/
│   │   │   └── SKILL.md
│   │   ├── pdf-to-prd/
│   │   │   └── SKILL.md
│   │   └── input-classifier/
│   │       └── SKILL.md
│   ├── docs/
│   │   ├── generate-ppt/
│   │   │   └── SKILL.md
│   │   ├── generate-sop/
│   │   │   └── SKILL.md
│   │   ├── generate-invoice/
│   │   │   └── SKILL.md
│   │   ├── generate-statement/
│   │   │   └── SKILL.md
│   │   ├── generate-project-report/
│   │   │   ├── SKILL.md
│   │   │   └── references/           ← Supporting files
│   │   ├── generate-random-project/
│   │   │   └── SKILL.md
│   │   └── review-command/
│   │       └── SKILL.md
│   ├── qa/
│   │   ├── _qa-shared/
│   │   ├── qa-api/  qa-data/  qa-form/  qa-guard/
│   │   ├── qa-runtime/  qa-scan/  qa-ui/
│   │   └── (each with SKILL.md)
│   ├── store/
│   │   ├── _ship/  _store-shared/
│   │   ├── assets/  build/  deploy/  native/  prep/  review/  submit/
│   │   └── (each with SKILL.md)
│   ├── fullstack/
│   │   ├── deployment/
│   │   │   └── SKILL.md
│   │   └── iteration-manager/
│   │       └── SKILL.md
│   ├── git-workflow/
│   │   └── create-dev-pr/
│   │       └── SKILL.md
│   ├── kb/
│   │   └── skill.md
│   └── code-cleanup/
│       └── SKILL.md
├── docs/
│   ├── project-registry.md
│   ├── references/
│   └── sop/
└── scripts/
```

## Usage Examples

```bash
# Generate a PRD from client requirements
/generate-prd client-requirements.pdf

# Create a presentation
/generate-ppt "Q1 Product Roadmap"

# Update PRD with client answers or scope changes (auto-detects)
/update-prd client-feedback.md

# Create an SOP and add to Notion
/generate-sop "New Employee Onboarding"

# Run QA scan
/qa-scan users

# Run specific QA check
/qa-api products
```

## When to Use

Add this submodule when your project involves:
- Document generation (PRD, SOP, presentations, invoices)
- Project initialization and setup workflows
- Deployment pipelines
- Git workflow automation
- Team training with generated projects
- Automated QA auditing (full-stack, framework-agnostic)
- App store submission pipeline

## Related Repos

| Repo | Purpose |
|------|---------|
| [claude-base](https://github.com/potentialInc/claude-base) | Core shared configuration |
| [claude-marketing](https://github.com/potentialInc/claude-marketing) | Marketing and growth skills |
| [claude-react](https://github.com/potentialInc/claude-react) | React frontend skills |
| [claude-nestjs](https://github.com/potentialInc/claude-nestjs) | NestJS backend skills |
