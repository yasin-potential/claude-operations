#!/usr/bin/env bash
# Wrapper around `op run + playwright test` that picks the right env-file per client.
#
# Usage:
#   ./scripts/run-flow.sh --client=<slug> --project=<flow> [playwright args...]
#
# Examples:
#   ./scripts/run-flow.sh --client=acme --project=duns-iupdate
#   ./scripts/run-flow.sh --client=acme --project=apple-developer-enroll --run-id=2026-04-23_14-12 --resume=post-email
#   ./scripts/run-flow.sh --client=potential --project=duns-iupdate      # uses internal test creds
#
# The env-file is `.env.1password.<slug>`. Client-specific env-files are gitignored.
# Client slug is also passed to Playwright as `--client=<slug>` so artifacts land in `artifacts/<slug>/...`.

set -euo pipefail

CLIENT=""
OP_ACCOUNT="team-potentialai.1password.com"
PLAYWRIGHT_ARGS=()

for arg in "$@"; do
  case "$arg" in
    --client=*)
      CLIENT="${arg#*=}"
      PLAYWRIGHT_ARGS+=("$arg")
      ;;
    --op-account=*)
      OP_ACCOUNT="${arg#*=}"
      ;;
    *)
      PLAYWRIGHT_ARGS+=("$arg")
      ;;
  esac
done

if [[ -z "$CLIENT" ]]; then
  echo "Error: --client=<slug> is required" >&2
  echo "Examples:" >&2
  echo "  $0 --client=acme --project=duns-iupdate" >&2
  echo "  $0 --client=potential --project=duns-iupdate" >&2
  exit 1
fi

ENV_FILE=".env.1password.${CLIENT}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: $ENV_FILE not found" >&2
  echo "" >&2
  echo "Create it from the template in SKILL.md → Adding a new client." >&2
  echo "It should contain op:// pointers to the client's 1Password vault item." >&2
  exit 1
fi

echo "▶ Running flow for client: $CLIENT"
echo "  env-file: $ENV_FILE"
echo "  playwright args: ${PLAYWRIGHT_ARGS[*]}"
echo ""

op run \
  --account "$OP_ACCOUNT" \
  --env-file="$ENV_FILE" \
  -- npx playwright test "${PLAYWRIGHT_ARGS[@]}"
