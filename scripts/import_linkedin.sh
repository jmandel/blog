#!/bin/bash
"""
import_linkedin.sh

Simple wrapper script for LinkedIn import pipeline
Usage: ./scripts/import_linkedin.sh [path-to-linkedin-export.zip]
"""

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_DIR="$(dirname "$SCRIPT_DIR")"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <linkedin-export.zip>"
    echo ""
    echo "This script will:"
    echo "  1. Install Python dependencies"
    echo "  2. Process the LinkedIn export"
    echo "  3. Replace existing blog content"
    echo "  4. Test the build"
    exit 1
fi

EXPORT_FILE="$1"

if [ ! -f "$EXPORT_FILE" ]; then
    echo "Error: Export file not found: $EXPORT_FILE"
    exit 1
fi

echo "[INFO] Starting LinkedIn import process..."
echo "[INFO] Blog directory: $BLOG_DIR"
echo "[INFO] Export file: $EXPORT_FILE"

# Change to blog directory
cd "$BLOG_DIR"

# Install Python dependencies
echo "[INSTALL] Installing Python dependencies..."
pip3 install -r "$SCRIPT_DIR/requirements.txt"

# Run the import
echo "[IMPORT] Running LinkedIn import pipeline..."
python3 "$SCRIPT_DIR/linkedin_import.py" "$EXPORT_FILE" --workdir linkedin_work --blog-dir "$BLOG_DIR"

# Test the build
echo "[TEST] Testing Astro build..."
npm run build

echo ""
echo "[SUCCESS] LinkedIn import completed successfully!"
echo "[INFO] $(ls src/content/blog/*.md | wc -l) articles imported"
echo "[INFO] Working files are in: linkedin_work/"
echo "[INFO] Blog content has been replaced with processed LinkedIn articles"
echo ""
echo "Next steps:"
echo "  - Review the imported content in src/content/blog/"
echo "  - Check any warnings about failed image downloads"
echo "  - Commit the changes: git add . && git commit -m 'Import LinkedIn articles'"