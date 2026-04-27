#!/usr/bin/env python3
"""
Bundle a generated proposal HTML into a Netlify-Drop-ready folder.

Usage:
    python3 scripts/bundle-for-netlify.py <path-to-generated-html>

Produces a sibling folder `<html-basename>-bundle/` containing:
- index.html with rewritten paths (no <base> tag, src="assets/...")
- assets/ with every image/asset the HTML references (preserving subpaths)

Drag the folder onto https://app.netlify.com/drop for an HTTPS URL.
"""

import html as htmllib
import re
import shutil
import sys
from pathlib import Path


def find_project_root(html_path: Path) -> Path:
    for parent in [html_path.parent, *html_path.parents]:
        if (parent / ".claude").is_dir():
            return parent
    raise SystemExit(f"Could not locate project root (no .claude/ ancestor of {html_path})")


def normalize_src(src: str) -> str | None:
    """Return project-root-relative path for a src we should bundle, or None to skip.

    Decodes HTML entities (e.g. &amp; → &) so filesystem lookups match the actual file names.
    """
    s = htmllib.unescape(src.strip())
    if s.startswith(("http://", "https://", "data:", "#", "mailto:")):
        return None
    while s.startswith("../"):
        s = s[3:]
    if s.startswith("./"):
        s = s[2:]
    if not s.startswith(".claude/"):
        return None
    return s


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    html_path = Path(sys.argv[1]).resolve()
    if not html_path.is_file():
        raise SystemExit(f"Not a file: {html_path}")

    project_root = find_project_root(html_path)
    bundle_dir = html_path.parent / f"{html_path.stem}-bundle"
    assets_dir = bundle_dir / "assets"

    # Preserve `.netlify/` (contains the site link) across rebuilds so re-deploys of the same
    # proposal update the existing Netlify site instead of creating a fresh one each time.
    netlify_backup = None
    if bundle_dir.exists():
        netlify_dir = bundle_dir / ".netlify"
        if netlify_dir.is_dir():
            netlify_backup = bundle_dir.parent / f".{bundle_dir.name}.netlify.bak"
            if netlify_backup.exists():
                shutil.rmtree(netlify_backup)
            shutil.move(str(netlify_dir), str(netlify_backup))
        shutil.rmtree(bundle_dir)
    assets_dir.mkdir(parents=True)
    if netlify_backup is not None:
        shutil.move(str(netlify_backup), str(bundle_dir / ".netlify"))

    html = html_path.read_text(encoding="utf-8")

    # Strip <base ...> tag (whole line). Both template-preview base and generation-time base.
    html = re.sub(r'<base\b[^>]*>(?:<!--[^>]*-->)?\n?', "", html)

    referenced: set[str] = set()
    missing: list[str] = []

    def web_path(rel: str) -> str:
        """Strip the leading `.claude/` so hosts that ignore dotfiles (Netlify, GitHub Pages) still serve assets."""
        return rel.removeprefix(".claude/") if rel.startswith(".claude/") else rel

    def rewrite(match: re.Match) -> str:
        full = match.group(0)
        attr = match.group(1)
        src = match.group(2)
        rel = normalize_src(src)
        if rel is None:
            return full
        referenced.add(rel)
        src_fs = project_root / rel
        if not src_fs.is_file():
            missing.append(rel)
            return full
        return full.replace(src, f"assets/{web_path(rel)}", 1)

    # Match src="..." and href="..." (covers <img>, <image>, <use href>, etc.)
    html = re.sub(r'(src|href)="([^"]+)"', rewrite, html)

    for rel in sorted(referenced):
        src_fs = project_root / rel
        if not src_fs.is_file():
            continue
        dst_fs = assets_dir / web_path(rel)
        dst_fs.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_fs, dst_fs)

    (bundle_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"Bundle ready: {bundle_dir}")
    print(f"  HTML:    index.html")
    print(f"  Assets:  {len(referenced)} files under assets/")
    if missing:
        print(f"  WARNING: {len(missing)} referenced files not found on disk:")
        for m in missing[:10]:
            print(f"    - {m}")
        if len(missing) > 10:
            print(f"    ... and {len(missing) - 10} more")
    print()
    print("Share:")
    print("  1. Open https://app.netlify.com/drop")
    print(f"  2. Drag the entire folder: {bundle_dir}")
    print("  3. Copy the .netlify.app URL Netlify returns")
    print()
    print("Or, if netlify-cli is installed and you're logged in:")
    print(f'  netlify deploy --prod --dir="{bundle_dir}"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
