# browser-signup

Playwright framework for signup/KYC portals with human-in-the-loop pauses. See [SKILL.md](SKILL.md) for the skill-level overview.

Credentials live in 1Password — no secrets ever touch disk.

---

## Team Onboarding — first time

### Prerequisites

- Access to the **Potential 1Password team** (account: `team-potentialai.1password.com`). Ask an admin if you're not added.
- Node.js 18+ (`node --version`)
- Homebrew (macOS) or equivalent

### 1. Install dependencies

```bash
# 1Password CLI (once per machine)
brew install 1password-cli

# Project deps
cd .claude/operation/skills/automation/browser-signup
npm install
npx playwright install chromium
```

### 2. Enable 1Password CLI integration

Open **1Password desktop app** → Settings (`⌘,`):

- **Security** tab → enable **Touch ID** (or system auth)
- **Developer** tab → check ✅ **Integrate with 1Password CLI**

Then sign in via CLI:

```bash
op signin
op whoami   # should print your account / team-potentialai.1password.com
```

### 3. Verify access to 1Password items

```bash
npm run check
```

Expected output:

```
browser-signup env check

  ✓ DUNS_COMPANY_NAME_EN present (pot***tl)
  ✓ DUNS_REPRESENTATIVE present (...)
  ...
Ready. Next: npm run flow -- --project=duns-iupdate
```

If you see `permission denied reading op://Shared/DUNS Registration/...`, ask an admin to grant your 1Password account access to the **Shared** vault.

### 4. Framework smoke test

```bash
npm run smoke
```

Runs the minimal `example.com` + form fill tests in [framework/\_\_tests\_\_/fixtures.spec.ts](framework/__tests__/fixtures.spec.ts). No credentials required — verifies Playwright + fixtures are wired correctly.

### 5. First DUNS run (headed)

```bash
npm run flow -- --project=duns-iupdate --headed
```

A Chromium window opens. The flow pauses at each human checkpoint with a desktop notification — follow [flows/duns-iupdate/playbook.md](flows/duns-iupdate/playbook.md).

---

## 1Password item reference

| | |
|---|---|
| Account | `team-potentialai.1password.com` |
| Vault | `Shared` |
| Item (DUNS) | `DUNS Registration` |
| Fields | `test_company_name_en`, `test_company_name_ko`, `test_representative`, `test_business_registration_number`, `test_address_en`, `test_phone`, `test_email`, `test_business_cert_path` + matching `live_*` fields |

Env-file mappings: [.env.1password.test](.env.1password.test) and [.env.1password.live](.env.1password.live) — both **committed** (references only, no real values).

---

## npm scripts

| Command | What it does |
|---|---|
| `npm run check` | Validate test credentials resolve from 1Password |
| `npm run check:live` | Validate live credentials resolve |
| `npm run flow -- --project=<name>` | Run a flow in test mode |
| `npm run flow:live -- --project=<name>` | Run a flow in LIVE mode |
| `npm run smoke` | Framework-only smoke tests, no credentials |
| `npm run codegen -- <url>` | Record selectors interactively |
| `npm run show-trace <path>` | Open a trace in the trace viewer |
| `npm run show-report` | Open the last HTML report |

Pass script flags after `--`:

```bash
npm run flow -- --project=duns-iupdate --headed --run-id=2026-04-23_14-12-05 --resume=post-email
```

---

## Directory layout

```
browser-signup/
├── SKILL.md                    Entrypoint for the skill
├── README.md                   You are here
├── package.json                Dependencies + op run scripts
├── playwright.config.ts        Headed default, one project per flow
├── tsconfig.json
├── check-env.mjs               Validates op vars, warns on plaintext .env
├── .env.1password.test|live    op:// pointers (committed, safe)
├── .env.example                Fallback plaintext template (gitignored in use)
├── framework/
│   ├── fixtures.ts             fillForm, waitForHuman, checkpoint, resumeFrom, uploadDocument, ...
│   ├── form-schema.ts          Schema type + runner
│   ├── checkpoint.ts           storageState + URL save/load
│   ├── notify.ts               Desktop alert for HITL pauses
│   └── __tests__/              Framework smoke tests
├── flows/
│   └── duns-iupdate/
│       ├── playbook.md         Human operator runbook
│       ├── schema.json         Form field map
│       ├── page-objects/       Per-page selectors
│       └── duns-iupdate.spec.ts
└── artifacts/                  gitignored: traces, screenshots, storageState
```

---

## Adding a new flow

See [SKILL.md → Adding a new flow](SKILL.md#adding-a-new-flow).

---

## Fallback — plain `.env` (not recommended)

If you can't use 1Password CLI, copy `.env.example` to `.env` and paste values manually. `.env` is gitignored but **never commit** it and **never paste live creds into Slack/chat**.

---

## Security

- `.env.1password.*` files contain **only references**, never real secrets. Safe to commit.
- `.env` (plaintext) is gitignored. Delete it once 1Password is working.
- `artifacts/` is gitignored. Traces may contain form values — clean them before sharing.
- Live-mode runs use the same ToS-compliant HITL pattern as test runs.
- For CI: use 1Password service accounts with `OP_SERVICE_ACCOUNT_TOKEN`, not desktop integration.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `account is not signed in` | `op signin` |
| `permission denied reading op://Shared/...` | Ask admin to grant Shared vault access |
| `npx playwright install` fails | Retry behind a network that allows browser-download CDN |
| Browser doesn't open | Check `headless: false` isn't overridden by `CI=true` in your environment |
| Inspector doesn't appear at pause | Happens in CI mode. Set `CI=` empty and rerun locally |
| Selectors fail on a page | `npx playwright codegen <url>` to find new selectors, update Page Objects |

---

## Related

- Skill entrypoint: [SKILL.md](SKILL.md)
- Credentials rule: [../../../CLAUDE.md → Credentials](../../../../CLAUDE.md)
- 1Password wiring guide: [../../../resources/docs/credentials-with-1password.md](../../../../resources/docs/credentials-with-1password.md)
- Reference Node script pattern: [../../scripts/bolta/](../../scripts/bolta/)
