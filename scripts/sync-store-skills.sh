#!/bin/bash
# Sync store skills from operations repo to global Claude skills directory
# Usage: bash scripts/sync-store-skills.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OPS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$OPS_DIR/skills/store"
SKILLS_DST="$HOME/.claude/skills"

# Verify source exists
if [ ! -d "$SKILLS_SRC" ]; then
  echo "Error: Store skills not found at $SKILLS_SRC"
  exit 1
fi

# Create destination if needed
mkdir -p "$SKILLS_DST"

# Clean existing store skills
rm -rf "$SKILLS_DST"/store-* "$SKILLS_DST"/_store-shared
echo "Cleaned existing store skills"

# Copy shared resources
if [ -d "$SKILLS_SRC/_store-shared" ]; then
  cp -r "$SKILLS_SRC/_store-shared" "$SKILLS_DST/_store-shared"
  echo "Synced: _store-shared"
fi

# Copy all store skills with store- prefix
count=0
for d in "$SKILLS_SRC"/*/; do
  name=$(basename "$d")
  [[ "$name" == "_store-shared" ]] && continue
  name="${name#_}"
  cp -r "$d" "$SKILLS_DST/store-$name"
  echo "Synced: store-$name"
  count=$((count + 1))
done

echo ""
echo "Done! $count store skills synced to $SKILLS_DST"
echo "Restart Claude Code for changes to take effect."
