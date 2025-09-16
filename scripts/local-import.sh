#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 path/to/linkedin-export.zip" >&2
  exit 1
fi

ZIP_PATH="$1"
if [[ ! -f "$ZIP_PATH" ]]; then
  echo "LinkedIn export not found: $ZIP_PATH" >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv is required. Install it from https://docs.astral.sh/uv/ first." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

UV_ENV=".venv-import"

echo "=== Step 0: Prepare uv environment ($UV_ENV) ==="
uv venv "$UV_ENV"
uv pip sync --python "$UV_ENV" scripts/requirements.txt

if [[ ! -d node_modules ]]; then
  echo "=== Installing npm dependencies ==="
  npm install
fi

echo "=== Step 1: Importing '$ZIP_PATH' ==="
uv run --python "$UV_ENV" python scripts/linkedin_import.py "$ZIP_PATH" --workdir linkedin_work --blog-dir .

echo "=== Step 2: Normalizing banner metadata ==="
uv run --python "$UV_ENV" python scripts/download_banner_images.py

echo "=== Step 3: Verifying Astro build ==="
npm run test-build

echo "\n✓ Import complete. Review the git diff, commit, and push to publish."
