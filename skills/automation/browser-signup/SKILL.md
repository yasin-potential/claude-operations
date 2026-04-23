---
name: browser-signup
description: Managed platform-signup service. PM-operated Playwright framework that registers clients on DUNS, Apple Developer, Google Play, Meta Business, etc. Human-in-the-loop pauses only for CAPTCHA and SMS codes (forwarded by client via KakaoTalk). Credentials per-client in 1Password. First flow is DUNS; framework is reusable.
argument-hint: <flow-name> --client=<slug> [--resume=<checkpoint>] [--run-id=<id>]
user-invocable: true
---

# browser-signup

A Playwright-based framework + concrete flows for running platform-account registrations on behalf of clients who struggle with them (language barriers, CAPTCHA friction, form confusion). **PM drives end-to-end**; client's only effort is filling an intake form once and forwarding any verification SMS via KakaoTalk.

## Service model

| Client touch | Cost | Frequency |
|---|---|---|
| Fill intake form | ~10 min | Once per client relationship |
| Forward Apple SMS via KakaoTalk | ~30 sec × 1–2 | Only Apple Developer, only during enrollment |
| Nothing else | 0 | — |

PM handles: all form filling, all CAPTCHAs, all email verifications, all payment entry, all document uploads, all submissions. The intake form includes a data-accuracy certification that client signs once.

Scope: digital platform signups only (DUNS, Apple Developer, Google Play, Meta Business, etc.). No banking, no tax agency work, no anything requiring a licensed 대리인.

## When to use this skill

- Client needs to register on a platform with a Korean-unfriendly signup flow.
- PM will operate the full registration on client's behalf.
- Signed intake form is the deliverable that gates running.

## When NOT to use this skill

- Pure API signups (use the API).
- Regulated financial KYC (Stripe Atlas, Wise, Mercury, etc.) — requires licensed agent.
- Korean government portals (홈택스 등) — do not offer without proper certification.
- Unattended CAPTCHA-solving or SMS-receive services — ToS violations for every supported platform.

## Available flows

| Project | Flow | Status |
|---|---|---|
| `duns-iupdate` | DUNS number registration via D&B | Scaffolded; selectors need live codegen verification. See [playbook](flows/duns-iupdate/playbook.md). |
| `apple-developer-enroll` | Apple Developer Program (Organization) | Planned — needs first client + live codegen session |
| `google-play-enroll` | Google Play Console (Organization) | Planned |
| `meta-business-verification` | Meta Business Manager verification | Planned |

## Quick start — new client onboarding

```bash
cd .claude/operation/skills/automation/browser-signup

# 1. First-time tool install (once per machine)
npm install
npx playwright install chromium
op signin

# 2. Per client — set up their vault + env file
#    See resources/1password-vault-setup.md for vault structure
cp .env.1password.test .env.1password.<client-slug>
# edit .env.1password.<client-slug> — change all op:// refs to <Client Slug> - Platforms vault

# 3. Verify credentials resolve
./scripts/run-flow.sh --client=<slug> --project=duns-iupdate -- --list

# 4. Run the flow
./scripts/run-flow.sh --client=<slug> --project=duns-iupdate
```

## Running a flow

`flow:client` (recommended for client engagements) — routes to the client's env-file automatically:

```bash
./scripts/run-flow.sh --client=acme --project=duns-iupdate
./scripts/run-flow.sh --client=acme --project=apple-developer-enroll
```

`flow` (internal Potential use only) — uses `.env.1password.test`:

```bash
npm run flow -- --project=duns-iupdate
```

Artifacts land at `artifacts/<client-slug>/<flow>/<run-id>/` (for client work) or `artifacts/<flow>/<run-id>/` (for internal use).

## Resume a prior run

Checkpoints auto-save at every `waitForHuman` and `waitForSMSCode` pause. To resume:

```bash
./scripts/run-flow.sh --client=acme --project=duns-iupdate \
  --run-id=2026-04-23_14-12-05 --resume=post-email
```

## Adding a new flow

1. Create `flows/<name>/` with:
   - `<name>.spec.ts` — orchestrates steps via fixtures.
   - `schema.json` — form fields with `${ENV_VAR}` placeholders.
   - `playbook.md` — PM operator runbook, including HITL gotchas.
   - `page-objects/` — one class per distinct portal page.
2. Register the flow as a Playwright project in [playwright.config.ts](playwright.config.ts).
3. Add per-flow fields to the 1Password vault template in [resources/1password-vault-setup.md](resources/1password-vault-setup.md).
4. Update [check-env.mjs](check-env.mjs) with newly required env vars.
5. Run `npx playwright codegen -- <start-url>` to capture real selectors. Refactor codegen output into Page Objects — never ship raw codegen code.

## Framework primitives

All exposed as Playwright fixtures from [framework/fixtures.ts](framework/fixtures.ts):

| Fixture | Purpose |
|---|---|
| `flow` | Flow context: `{ flowName, runId, client? }`. Auto-derived from project + argv. |
| `fillForm(schema)` | Schema-driven form fill. Supports text, email, tel, select, checkbox, radio, in-frame fields. Optional per-field validation. |
| `waitForHuman({ reason, checkpoint, timeoutMin })` | PM-driven pause. Desktop notification, `page.pause()`, auto-saves checkpoint after resume. |
| `waitForSMSCode({ inputSelector, expectedFrom, checkpoint })` | Special case of `waitForHuman` for SMS codes forwarded by client via KakaoTalk. Clearer messaging, shorter default timeout. |
| `checkpoint(name)` | Saves `storageState` + URL + full-page screenshot to `artifacts/<client>/<flow>/<run-id>/<name>.{json,storage.json,png}`. |
| `resumeFrom(name)` | Loads a prior checkpoint, navigates to its saved URL. Requires `--run-id=<id>`. |
| `uploadDocument({...})` | Wraps `setInputFiles` with optional frame targeting + preview assertion. |
| `expectOtpEntered(selector, timeoutMin?)` | Wait until a human types into an input. Never reads SMS. |
| `saveResult(result)` | Writes final delivery payload to `artifacts/<client>/<flow>/<run-id>/result.json`. |
| `writeHandoff(content)` | Writes client-facing delivery doc to `artifacts/<client>/<flow>/<run-id>/handoff.md`. |

## 1Password — credentials pattern

**Per-client vault**: `<Client Slug> - Platforms` in the `team-potentialai.1password.com` account. One vault per client, one item per flow.

**Env file**: `.env.1password.<client-slug>` — committed (gitignored except for `.test` and `.live`). Contains only `op://` pointers:

```
CLIENT_SLUG=acme
DUNS_COMPANY_NAME_EN=op://Acme Corp - Platforms/Entity Data/company_name_en
APPLE_DEV_TOTP=op://Acme Corp - Platforms/Apple Developer/one-time password
CC_NUMBER=op://Acme Corp - Platforms/Payment/number
...
```

`op run` resolves `op://` pointers into env vars in-memory at runtime. Secrets never touch disk. TOTP fields regenerate fresh codes on every invocation — no authenticator app needed.

Full vault structure: [resources/1password-vault-setup.md](resources/1password-vault-setup.md).

## SMS verification pattern (Korean clients)

Korean clients forward incoming SMS via KakaoTalk. Encode this as `waitForSMSCode` in the flow spec:

```ts
await waitForSMSCode({
  inputSelector: 'input[name="verificationCode"]',
  expectedFrom: 'Apple',
  reason: 'Apple sent SMS to client. Wait for KakaoTalk forward, paste code, click Resume.',
  checkpoint: 'sms-verified',
  timeoutMin: 10,
});
```

Client-facing script for the SMS forward: [resources/client-faq-apple.md](resources/client-faq-apple.md) (Korean).

## Artifacts

```
artifacts/
├── <client-slug>/                     # one per client engagement
│   └── <flow>/<run-id>/
│       ├── <checkpoint>.json           # meta
│       ├── <checkpoint>.storage.json   # cookies + localStorage
│       ├── <checkpoint>.png            # full-page screenshot
│       ├── result.json                 # final output (DUNS number, team ID, etc.)
│       └── handoff.md                  # client-facing delivery doc
├── _runs/                              # Playwright default output
└── _report/                            # HTML report (npm run show-report)
```

All `artifacts/` is gitignored. Retain per-client runs for 1 year (evidence of what was submitted); delete sooner if engagement ends earlier.

## Product deliverables

These are the sellable artifacts of the service, referenced in client-facing conversations:

| Artifact | File | Purpose |
|---|---|---|
| PM onboarding guide (Korean) | [resources/pm-guide-korean.md](resources/pm-guide-korean.md) | Step-by-step guide for new PMs learning the skill |
| Intake form | [resources/intake-form-template.md](resources/intake-form-template.md) | One-time data collection + data-accuracy certification, reused across all flows |
| Apple client FAQ | [resources/client-faq-apple.md](resources/client-faq-apple.md) | KakaoTalk SMS forwarding instructions (Korean) |
| 1Password vault setup | [resources/1password-vault-setup.md](resources/1password-vault-setup.md) | Per-client vault structure + access management |
| DUNS delivery email | [resources/delivery-duns.md](resources/delivery-duns.md) | Template for end-of-flow client email |

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Error: --client=<slug> is required` | Use `./scripts/run-flow.sh` with `--client=<slug>` |
| `.env.1password.<slug> not found` | Copy `.env.1password.test` to `.env.1password.<slug>`, update `op://` paths to client vault |
| `permission denied reading op://...` | Client vault not shared with your 1Password account, or wrong vault name |
| `account is not signed in` | `op signin` |
| `resumeFrom requires --run-id=...` | Pass `--run-id=<id>` matching a directory under `artifacts/<client>/<flow>/` |
| SMS pause never hits code | Client's SMS forwarding failed. Retry by clicking "Resend code" in the portal, expect new SMS within 60s |
| Selectors broken after portal redesign | Rerun `npx playwright codegen -- <url>` and update Page Objects |

## Security

- Per-client 1Password vault; revoke access at engagement end.
- `artifacts/` contains screenshots of filled forms — do not commit, do not Slack raw.
- `storageState.json` files contain live session cookies — do not share.
- Business certificate PDFs live as 1Password attachments, not on PM's laptop. Local `business_cert_path` copies are deleted after each run.
- Live-mode runs use the same HITL pattern as test — no ToS-violating bypasses anywhere.
