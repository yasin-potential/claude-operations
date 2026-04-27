#!/usr/bin/env bash
# Publish a generated proposal HTML to Netlify as a sharable HTTPS URL.
#
# Usage:
#   bash scripts/publish.sh <path-to-generated-html>           # prod deploy, stable URL
#   bash scripts/publish.sh <path-to-generated-html> --draft   # draft (preview) URL
#
# Runs the bundler first (creates sibling <name>-bundle/), then deploys via netlify-cli.
# Prerequisites (one-time, per user):
#   npm i -g netlify-cli
#   netlify login     # opens a browser, authorizes once
set -euo pipefail

if [[ $# -lt 1 ]]; then
    sed -n '3,11p' "$0" >&2
    exit 2
fi

HTML_PATH="$1"
MODE="${2:---prod}"
if [[ "$MODE" == "--draft" ]]; then
    DEPLOY_FLAGS=()
else
    DEPLOY_FLAGS=("--prod")
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -f "$HTML_PATH" ]]; then
    echo "ERROR: not a file: $HTML_PATH" >&2
    exit 1
fi

if ! command -v netlify >/dev/null 2>&1; then
    echo "ERROR: netlify-cli not installed. Run: npm i -g netlify-cli" >&2
    exit 1
fi

# Step 1: bundle
python3 "$SCRIPT_DIR/bundle-for-netlify.py" "$HTML_PATH"

# Step 2: derive bundle path (same logic as the bundler)
HTML_DIR="$(cd "$(dirname "$HTML_PATH")" && pwd)"
HTML_STEM="$(basename "$HTML_PATH" .html)"
BUNDLE_DIR="$HTML_DIR/${HTML_STEM}-bundle"

if [[ ! -d "$BUNDLE_DIR" ]]; then
    echo "ERROR: bundle not created at $BUNDLE_DIR" >&2
    exit 1
fi

echo
echo "Deploying $BUNDLE_DIR to Netlify..."
echo

# Step 3: deploy. `cd` into the bundle first so netlify-cli reads/writes .netlify/state.json
# INSIDE the bundle instead of walking up and sharing state across proposals.
# --dir=. targets the current (bundle) directory; --prod pins a stable URL; --draft = preview.
cd "$BUNDLE_DIR"
netlify deploy "${DEPLOY_FLAGS[@]}" --dir=.
