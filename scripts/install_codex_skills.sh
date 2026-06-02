#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${CODEX_HOME:-$HOME/.codex}/skills"

install_skill() {
  local name="$1"
  local src="$ROOT/skills/$name"
  local dst="$TARGET/$name"
  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "Missing skill source: $src/SKILL.md" >&2
    exit 1
  fi
  mkdir -p "$dst"
  cp "$src/SKILL.md" "$dst/SKILL.md"
  echo "Installed $name -> $dst"
}

mkdir -p "$TARGET"
install_skill "hermes-project-operating-manual"
install_skill "hermes-architecture"

echo "Done. Restart Codex or start a new thread if the skills list is cached."

