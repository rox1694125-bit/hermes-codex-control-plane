#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/project [--force]" >&2
  exit 2
fi

PROJECT="$1"
FORCE="${2:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="$ROOT/templates/project-standard"

if [[ ! -d "$PROJECT" ]]; then
  echo "Project directory does not exist: $PROJECT" >&2
  exit 1
fi

copy_file() {
  local rel="$1"
  local src="$TEMPLATE/$rel"
  local dst="$PROJECT/$rel"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" && "$FORCE" != "--force" ]]; then
    echo "Skip existing $rel"
    return
  fi
  cp "$src" "$dst"
  echo "Wrote $rel"
}

copy_file "AGENTS.md"
copy_file "PROJECT_BRIEF.md"
copy_file "WORKPLAN.md"
copy_file "docs/DECISIONS.md"
copy_file "docs/RISKS.md"

mkdir -p "$PROJECT/docs/project-log"
echo "Ensured docs/project-log/"

echo "Done. Review and customize the generated files before using the protocol."

