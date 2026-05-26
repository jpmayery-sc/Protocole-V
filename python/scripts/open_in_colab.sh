#!/usr/bin/env bash
# Usage: ./scripts/open_in_colab.sh OWNER REPO PATH [BRANCH]
set -euo pipefail

OWNER=${1:-}
REPO=${2:-}
PATH_IN_REPO=${3:-}
BRANCH=${4:-}

if [ -z "$OWNER" ] || [ -z "$REPO" ] || [ -z "$PATH_IN_REPO" ]; then
  echo "Usage: $0 OWNER REPO path/to/notebook.ipynb [BRANCH]"
  exit 2
fi

if [ -z "$BRANCH" ]; then
  BRANCH=$(git rev-parse --abbrev-ref HEAD)
fi

git add -A
git commit -m "Prepare notebook for Colab" || true
git push origin "$BRANCH"

URL="https://colab.research.google.com/github/${OWNER}/${REPO}/blob/${BRANCH}/${PATH_IN_REPO}"

echo "Opening: $URL"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "$URL" >/dev/null 2>&1 || true
else
  echo "$URL"
fi

exit 0
