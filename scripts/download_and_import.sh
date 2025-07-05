#!/bin/bash
"""
download_and_import.sh

Automated script to download LinkedIn export and run the import pipeline
"""

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BLOG_DIR="$(dirname "$SCRIPT_DIR")"
EXPORT_URL="https://github.com/user-attachments/files/21061241/linkedin_articles_extract.zip"
EXPORT_FILE="linkedin_articles_extract.zip"
WORKDIR="linkedin_work"

echo "[INFO] Blog directory: $BLOG_DIR"
echo "[INFO] Script directory: $SCRIPT_DIR"

# Change to blog directory
cd "$BLOG_DIR"

# Install Python dependencies
echo "[INSTALL] Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt"
elif command -v pip &> /dev/null; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "[ERROR] Neither pip nor pip3 found. Please install Python and pip."
    exit 1
fi

# Download LinkedIn export if not already present
if [ ! -f "$EXPORT_FILE" ]; then
    echo "[DOWNLOAD] Downloading LinkedIn export..."
    if command -v wget &> /dev/null; then
        wget -O "$EXPORT_FILE" "$EXPORT_URL"
    elif command -v curl &> /dev/null; then
        curl -L -o "$EXPORT_FILE" "$EXPORT_URL"
    else
        echo "[ERROR] Neither wget nor curl found. Please download the LinkedIn export manually:"
        echo "  URL: $EXPORT_URL"
        echo "  Save as: $EXPORT_FILE"
        exit 1
    fi
else
    echo "[INFO] LinkedIn export already exists: $EXPORT_FILE"
fi

# Run the import
echo "[IMPORT] Running LinkedIn import pipeline..."
python3 "$SCRIPT_DIR/linkedin_import.py" "$EXPORT_FILE" --workdir "$WORKDIR" --blog-dir "$BLOG_DIR"

# Test the build
echo "[TEST] Testing Astro build..."
npm run build

# Check banner image status
echo "[BANNER] Checking banner image status..."
BANNER_COUNT=$(find public/images/linkedin -name "banner.*" 2>/dev/null | wc -l)
echo "[BANNER] Found $BANNER_COUNT banner images"

# Check posts with banners in frontmatter
BANNER_POSTS=$(grep -l "^banner:" src/content/blog/linkedin/*.md 2>/dev/null | wc -l)
echo "[BANNER] $BANNER_POSTS posts have banner frontmatter"

echo "[SUCCESS] LinkedIn import completed successfully!"
echo "[INFO] Working files are in: $WORKDIR"
echo "[INFO] Blog content has been replaced with processed LinkedIn articles"
echo "[INFO] Banner images are ready for blog posts"