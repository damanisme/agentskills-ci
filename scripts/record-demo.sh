#!/usr/bin/env bash
#
# Record the README demo GIF.
#
# Usage:   bash scripts/record-demo.sh
# Output:  docs/demo.gif
#
# Requires asciinema (records the terminal) and agg (turns the recording into a
# GIF). Install hints are printed below if either is missing.
set -euo pipefail

cd "$(dirname "$0")/.."   # repo root

# --- dependency checks ------------------------------------------------------
missing=0
if ! command -v asciinema >/dev/null 2>&1; then
  echo "✗ asciinema not found.  Install:  pipx install asciinema" >&2
  missing=1
fi
if ! command -v agg >/dev/null 2>&1; then
  echo "✗ agg not found.  Install:  cargo install --git https://github.com/asciinema/agg" >&2
  echo "  (or grab a prebuilt binary from https://github.com/asciinema/agg/releases)" >&2
  missing=1
fi
if ! command -v agentskills-ci >/dev/null 2>&1; then
  echo "✗ agentskills-ci not found.  Install:  pip install agentskills-ci" >&2
  missing=1
fi
[ "$missing" -eq 0 ] || { echo "Install the above, then re-run." >&2; exit 1; }

mkdir -p docs
CAST="$(mktemp -t demo.XXXXXX.cast)"
trap 'rm -f "$CAST" "$PLAY"' EXIT

# --- the script that gets filmed -------------------------------------------
# Echo each command (so viewers see it typed) then run it, with small pauses.
PLAY="$(mktemp -t demoplay.XXXXXX.sh)"
cat > "$PLAY" <<'PLAYSCRIPT'
set -e
type_cmd() { printf '$ %s\n' "$1"; sleep 0.8; }

type_cmd "agentskills-ci score examples/skills"
agentskills-ci score examples/skills || true
sleep 2

printf '\n'
type_cmd "agentskills-ci badge examples/skills/good-skill"
agentskills-ci badge examples/skills/good-skill
sleep 2.5
PLAYSCRIPT

# --- record + convert -------------------------------------------------------
echo "Recording…"
asciinema rec "$CAST" --overwrite --cols 80 --rows 24 -c "bash $PLAY"

echo "Converting to docs/demo.gif…"
agg --cols 80 --rows 24 "$CAST" docs/demo.gif

echo
echo "✓ Wrote docs/demo.gif"
echo "  Embed it in README.md by replacing the Demo code blocks with:"
echo "    ![agentskills-ci demo](docs/demo.gif)"
