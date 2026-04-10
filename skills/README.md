# Skills

All reusable Claude Code skills, organized by category.

## Category Map

| Category | Description | Orchestrator | Skills |
|----------|-------------|--------------|--------|
| [prd/](prd/) | PRD lifecycle — generate, update, convert | — | 6 |
| [qa/](qa/) | QA auditing — API, data, UI, security, runtime | `qa-scan` | 7 |
| [store/](store/) | App store submission pipeline | `store-ship` | 7 |
| [docs/](docs/) | Document generation — PPT, SOP, invoice, report | — | 7 |
| [fullstack/](fullstack/) | Fullstack pipeline — deployment, iteration | — | 2 |

## Standalone Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [code-cleanup/](code-cleanup/) | `/code-cleanup` | Dead code analysis and removal |
| [git-workflow/create-dev-pr/](git-workflow/create-dev-pr/) | `/create-dev-pr` | PR creation to dev branch |
| [project-close/](project-close/) | `/project-close` | Project closing workflow and deliverables |
| [project-kickoff/](project-kickoff/) | `/project-kickoff` | Client kick-off presentation |
| [ticketcreator/](ticketcreator/) | `/ticketcreator` | Structured ticket generation |

## Category README Convention

Every category folder **must** have a `README.md` with these sections:

| Section | Required | Content |
|---------|----------|---------|
| `# {Name} Skills` | Yes | One-line description |
| `## Orchestrator` | If exists | Orchestrator skill and what it does |
| `## Pipeline Flow` | If exists | ASCII diagram showing dependencies |
| `## Skills` | Yes | Table: Skill, Command, Description |
| `## Shared Rules` | If exists | What `_shared/` contains and how skills use it |
| `## Naming Convention` | Yes | Operations repo path ↔ global skills path mapping |

Reference model: [store/README.md](store/README.md)
