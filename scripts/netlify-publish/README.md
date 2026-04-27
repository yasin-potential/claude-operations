# Netlify Publish

Bundle any generated HTML deck into a [Netlify](https://www.netlify.com/) Drop-ready folder and deploy it as a sharable HTTPS URL. Shared utility — used by [`generate-proposal`](../../skills/client/proposals/generate-proposal/SKILL.md) today, designed to also serve `kickoff`, `closing`, `weekly`, and `generate-project-overview`.

**No credentials needed.** `netlify-cli` handles auth via a one-time browser login that persists in `~/.netlify/`. Unlike [`bolta/`](../bolta/), this dir has no `.env.1password.*` files and no `check-env.mjs`.

---

## Team Onboarding — first time

### Prerequisites

- Node.js 18+ (`node --version`)
- A [Netlify account](https://app.netlify.com/signup) (free tier is fine)

### 1. Install netlify-cli

```bash
npm i -g netlify-cli
netlify --version   # confirm
```

### 2. Authorize once

```bash
netlify login
```

A browser window opens; click **Authorize**. Token persists in `~/.netlify/` — you won't be asked again on this machine.

```bash
netlify status   # should print your account/teams
```

That's it. No `op signin`, no env files.

---

## Usage

### Bundle only (no deploy)

```bash
python3 .claude/operation/scripts/netlify-publish/bundle-for-netlify.py path/to/file.html
```

Produces a sibling folder `path/to/file-bundle/` containing:
- `index.html` with rewritten asset paths (no `<base>` tag, `src="assets/..."`)
- `assets/` with every image/SVG the HTML referenced via `src=".claude/..."` or `href=".claude/..."`

You can drag the folder onto [app.netlify.com/drop](https://app.netlify.com/drop) for a manual deploy.

### Bundle + deploy (one command)

```bash
# Production (stable URL):
bash .claude/operation/scripts/netlify-publish/publish.sh path/to/file.html
# → https://<site-name>.netlify.app

# Draft / preview URL:
bash .claude/operation/scripts/netlify-publish/publish.sh path/to/file.html --draft
```

`publish.sh` runs the bundler first, then `netlify deploy --prod --dir=.` (or `--draft`) from inside the bundle dir.

---

## How asset resolution works

The bundler walks up from the input HTML to find the project's `.claude/` ancestor (the project root). Any `src="..."` or `href="..."` whose path resolves under `.claude/` (after stripping `../` and `./` prefixes) gets:

1. Copied into `<bundle>/assets/<path>` (preserving subpaths)
2. Rewritten in the output HTML to `assets/<web_path>`, where `web_path()` strips the leading `.claude/` so hosts that ignore dotfiles (Netlify, GitHub Pages) still serve the file

External URLs (`http://`, `https://`, `data:`, `mailto:`, `#anchor`) are left untouched.

---

## Re-deploys

Each bundle keeps its own `.netlify/` state dir. The bundler preserves it across rebuilds (moves it aside, then restores it after re-bundling) so re-running `publish.sh` against the same HTML updates the **existing** Netlify site instead of creating a fresh one each time.

If you want a clean new site, delete the bundle's `.netlify/` dir before re-running.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `WARNING: N referenced files not found on disk` | The HTML references assets under `.claude/...` that don't exist. Check the source skill's image paths. |
| `ERROR: netlify-cli not installed` | `npm i -g netlify-cli` |
| `netlify deploy` prompts for login | Run `netlify login` first (one-time per machine) |
| Site looks broken (no images) | Confirm the original HTML used `.claude/...` paths for assets — only those get bundled |
