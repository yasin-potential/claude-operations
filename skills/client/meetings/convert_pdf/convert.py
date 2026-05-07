"""Convert an HTML slide deck to a multi-page PDF, one slide per page.

Designed for decks produced by the /weekly, /kickoff, and /closing skills, which
share a common CSS framework: every slide is a `.slide` element, only the one
with the `.active` class is visible at a time, and `.prev` marks slides the
viewer has already passed.

Usage:
    python convert.py <input.html> [--out <output.pdf>]
                                   [--theme light|dark]
                                   [--width 1920] [--height 1080]
                                   [--dpr 2]
                                   [--slide-selector .slide]

Behaviour:
    1. Launches headless Chromium at the requested viewport.
    2. Loads the HTML, forces a deterministic theme, hides nav chrome.
    3. Counts slides matching the selector (default `.slide`).
    4. For each slide, directly toggles the .active/.prev classes (no reliance
       on the deck's transition timing) and takes a screenshot.
    5. Combines PNGs into a multi-page PDF via Pillow. PDF page size matches
       the source PNG, so the slide aspect ratio is preserved exactly.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError as e:
    raise SystemExit("Pillow is required. Install with: pip install pillow") from e

try:
    from playwright.async_api import (
        TimeoutError as PlaywrightTimeoutError,
        async_playwright,
    )
except ImportError as e:
    raise SystemExit(
        "playwright is required. Install with: pip install playwright "
        "&& python -m playwright install chromium"
    ) from e


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Convert an HTML slide deck to a multi-page PDF (one slide per page)."
    )
    p.add_argument("html", type=Path, help="Path to the input HTML deck.")
    p.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output PDF path (default: same basename as input, .pdf extension, same directory).",
    )
    p.add_argument(
        "--theme",
        choices=["light", "dark"],
        default="light",
        help="Force a theme on the deck before capture (default: light).",
    )
    p.add_argument("--width", type=int, default=1920, help="Viewport width (default: 1920).")
    p.add_argument("--height", type=int, default=1080, help="Viewport height (default: 1080).")
    p.add_argument(
        "--dpr",
        type=int,
        default=2,
        help="Device pixel ratio for crisper output (default: 2). Drop to 1 for smaller files.",
    )
    p.add_argument(
        "--slide-selector",
        default=".slide",
        help="CSS selector for slide elements (default: .slide).",
    )
    return p.parse_args()


HIDE_CHROME_CSS = """
.nav-bar, .slide-counter, .chrome-btn { display: none !important; }
"""


async def capture_slides(
    html_path: Path,
    out_dir: Path,
    *,
    theme: str,
    width: int,
    height: int,
    dpr: int,
    slide_selector: str,
) -> list[Path]:
    """Render `html_path` headless and dump each slide as a PNG into `out_dir`."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=dpr,
            reduced_motion="reduce",
            color_scheme=theme,
        )
        page = await ctx.new_page()
        await page.goto(html_path.resolve().as_uri())
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except PlaywrightTimeoutError:
            # Some decks keep long-poll connections alive (Google Fonts, analytics)
            # — the framework is interactive long before networkidle ever fires.
            # Fall back to "load" + a short settle, which is sufficient here.
            await page.wait_for_load_state("load")
            await page.wait_for_timeout(500)

        # Force the requested theme — handles decks that read localStorage on load.
        await page.evaluate(
            "(t) => document.documentElement.setAttribute('data-theme', t)", theme
        )
        # Hide deck chrome (nav bar, theme toggle, etc.) so the PDF shows pure slides.
        await page.add_style_tag(content=HIDE_CHROME_CSS)
        await page.wait_for_timeout(200)

        slide_count = await page.evaluate(
            "(sel) => document.querySelectorAll(sel).length", slide_selector
        )
        if not slide_count:
            await browser.close()
            raise SystemExit(
                f"No slides matched selector '{slide_selector}'. "
                "Pass --slide-selector if the deck uses a different class."
            )

        paths: list[Path] = []
        for i in range(slide_count):
            await page.evaluate(
                """([sel, idx]) => {
                    const slides = document.querySelectorAll(sel);
                    slides.forEach((s, j) => {
                        s.classList.remove('active', 'prev');
                        if (j < idx) s.classList.add('prev');
                        if (j === idx) s.classList.add('active');
                    });
                }""",
                [slide_selector, i],
            )
            # Confirm the toggled slide actually became visible before screenshotting —
            # protects against a stuck transition or a typo in --slide-selector
            # that would otherwise produce a blank page in the PDF.
            try:
                await page.locator(f"{slide_selector}.active").wait_for(
                    state="visible", timeout=2000
                )
            except PlaywrightTimeoutError:
                await browser.close()
                print(
                    f"ERROR: slide {i + 1}/{slide_count} did not become visible within 2s "
                    f"after toggling .active (selector={slide_selector!r}). "
                    "Aborting before producing a broken PDF.",
                    file=sys.stderr,
                )
                raise SystemExit(3)
            out = out_dir / f"slide_{i:03d}.png"
            await page.screenshot(path=str(out), full_page=False)
            paths.append(out)
            print(f"  captured slide {i + 1}/{slide_count}")

        await browser.close()
    return paths


def build_pdf(images: list[Path], pdf_out: Path) -> None:
    """Write `images` as a multi-page PDF preserving each image's aspect."""
    frames = [Image.open(p).convert("RGB") for p in images]
    first, rest = frames[0], frames[1:]
    first.save(
        pdf_out,
        format="PDF",
        save_all=True,
        append_images=rest,
        resolution=144.0,
    )


async def main() -> int:
    args = parse_args()
    html_path: Path = args.html
    if not html_path.exists():
        print(f"Input not found: {html_path}", file=sys.stderr)
        return 2

    pdf_out: Path = args.out or html_path.with_suffix(".pdf")
    pdf_out.parent.mkdir(parents=True, exist_ok=True)

    print(f"Source : {html_path}")
    print(f"Output : {pdf_out}")
    print(
        f"Render : {args.width}x{args.height} @ {args.dpr}x DPR, theme={args.theme}, selector={args.slide_selector!r}"
    )

    with tempfile.TemporaryDirectory(prefix="deck_pdf_") as td:
        tmp = Path(td)
        print("Capturing slides...")
        images = await capture_slides(
            html_path,
            tmp,
            theme=args.theme,
            width=args.width,
            height=args.height,
            dpr=args.dpr,
            slide_selector=args.slide_selector,
        )
        print(f"Building PDF with {len(images)} pages (16:9 per page preserved)...")
        build_pdf(images, pdf_out)

    size_kb = pdf_out.stat().st_size / 1024
    print(f"Done: {pdf_out} ({size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
