---
name: convert-pdf
description: "Convert any meeting HTML deck (kickoff, weekly, closing) to a multi-page PDF where each slide becomes one 16:9 page — content full-bleed, aspect ratio preserved, no A4 cropping or flow break. Headless Playwright + Pillow under the hood."
user-invocable: true
argument-hint: "[path-to-html] [--out path-to-pdf] [--theme light|dark] [--width N] [--height N]"
---

# Meeting Deck — HTML to PDF

Convert any HTML slide deck produced by `/kickoff`, `/weekly`, or `/closing` into a multi-page PDF that perfectly mirrors the rendered HTML — one slide per PDF page, original 16:9 aspect ratio preserved, content centered, nothing reflowed.

## When to use

- Client wants the deck as a PDF for offline review or email attachment.
- Deck must look exactly like the HTML version (charts, badges, deadline tags, gradient orbs).
- A4 / Letter page sizes would crop or break the layout — this skill keeps the slide aspect.

## Prerequisites

| Dependency | Install |
|---|---|
| Python 3.10+ | (system) |
| `playwright` (Python) | `pip install playwright` |
| Chromium for Playwright | `python -m playwright install chromium` |
| `Pillow` | `pip install pillow` |

If any dependency is missing, install before running.

## Workflow

### Step 1 — Locate the HTML deck

If the user passed a path, use it directly. Otherwise auto-detect:

1. If invoked from a meeting subfolder (`.claude-project/meetings/{Project}/{kickoff|weekly|closing}/`), glob the matching prefix (`[Kickoff] *.html`, `[Weekly] *.html`, `[Closing] *.html`) and pick the **most recent** by `(YYYY-MM-DD)` suffix.
2. If invoked from a project root, glob `.claude-project/meetings/**/*.html` and pick the most recent.
3. If still ambiguous, ask the user via AskUserQuestion which file to convert.

Confirm the chosen path back to the user before running.

### Step 2 — Run the converter

Invoke `convert.py` from this skill folder with the resolved HTML path. The script:

1. Launches headless Chromium at 1920×1080 (override with `--width` / `--height`).
2. Loads the HTML via `file://` URL, waits for `networkidle` with a 15 s upper bound, forces the light theme (or `--theme dark`).
3. Hides chrome elements (nav bar, slide counter, theme + fullscreen buttons) via injected CSS.
4. Counts slides by querying `document.querySelectorAll('.slide').length` — works for any deck count.
5. Drives slide navigation by directly mutating `.active` / `.prev` classes on each slide (bypasses CSS transitions for deterministic capture).
6. Validates each slide is actually visible after the class toggle (waits up to 2 s); if a slide never reaches `visible`, prints which slide failed and exits non-zero rather than producing a broken PDF.
7. Screenshots each slide at 2× device pixel ratio (crisp at any zoom).
8. Combines PNGs into a multi-page PDF via Pillow's `Image.save(..., format='PDF', save_all=True)`. PDF page size matches the source PNG, so the slide aspect is preserved exactly.
9. Saves the output as `[Same Base Name].pdf` next to the source HTML, or to `--out PATH` if specified.

Command shape:

```bash
python "<this-skill>/convert.py" "<path/to/deck.html>" [--out "<path.pdf>"] [--theme light|dark] [--width 1920] [--height 1080]
```

### Step 3 — Report

Print the absolute output path, the captured page count, and the file size. If any slide failed to render, the script already exited non-zero with the failing slide index — relay that to the user and stop.

## Why each slide becomes one page

The HTML decks position every `.slide` absolutely with `transform: translateX(...)`. Only the `.active` slide is visible at any time. A naive `page.pdf()` call would print only the document flow, missing the navigated state.

This skill instead **screenshots each slide individually** then composes a multi-page PDF where each page = one full-bleed PNG at the slide's native 1920×1080 aspect. Result:

- Aspect ratio preserved (no A4 letterboxing or cropping).
- Content fully centered and complete (rendered exactly as the HTML displays it).
- No flow break (each slide is one atomic page).
- Gradient orbs, badges, status tags, gantt bars all preserved (it's a true visual capture, not a DOM reformat).

## Trade-offs

- **Text is rasterized.** Each PDF page is a PNG, so the text is not selectable/searchable. This matches the visual fidelity goal. If selectable text is required later, switch to a vector path (Playwright `page.pdf()` per slide with custom `width` / `height` matching the slide, then merge — accepts some layout risk).
- **DPR=2 increases file size.** A typical 11-slide deck is ~2.5 MB. Drop to DPR=1 for ~700 KB at the cost of zoom crispness.

## Naming convention

- **Operations repo**: `skills/client/meetings/convert_pdf/`
- **Global skills** (`~/.claude/skills/`): `convert-pdf/`
- **Slash command**: `/convert-pdf`

## Reusing the script directly

The Python script is self-contained and importable. Other skills (e.g., kickoff, weekly, closing) can call it via subprocess:

```python
import subprocess, sys
subprocess.run([
    sys.executable,
    "<path-to>/convert.py",
    str(html_path),
    "--out", str(pdf_path),
], check=True)
```

## See also

- [`kickoff/SKILL.md`](../kickoff/SKILL.md) — produces kickoff decks (verified working with this converter)
- [`weekly/SKILL.md`](../weekly/SKILL.md) — produces weekly decks (verified working with this converter)
- [`closing/SKILL.md`](../closing/SKILL.md) — produces closing decks (verified working with this converter)
