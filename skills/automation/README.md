# Automation Skills

Browser and workflow automation — signup, KYC, portal flows.

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| [browser-signup](browser-signup/) | `/browser-signup` | Playwright framework + DUNS registration flow, with HITL pauses for CAPTCHA/OTP/3DS. Credentials via 1Password. Extensible to AWS signup and future flows. |

## Framework Philosophy

Automation skills in this category share one rule: **no CAPTCHA-solving services, no SMS-receive APIs, no unattended credential bypass**. Every flow is ToS-compliant and pauses for a human at verification gates. The framework's job is to make the non-human parts reliable and resumable.

## Naming Convention

- **Operations repo**: short names (`automation/browser-signup/`)
- **Global skills** (`~/.claude/skills/`): prefixed names (`automation-browser-signup/`) — sync via the usual skill-sync pattern
- **Slash commands**: `/browser-signup`, `/<flow-name>` as additional flows land

## Adding a new automation skill

1. Create a new skill folder under this category.
2. If the skill needs credentials, follow [CLAUDE.md → Credentials](../../../CLAUDE.md) (1Password `op run` only — never plaintext `.env`).
3. Add it to the table above.
4. Register in [../skill-rules.json](../skill-rules.json).
5. Update [../README.md](../README.md) if this category moves from 1 skill to >1.
