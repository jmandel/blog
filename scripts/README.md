# LinkedIn Import Pipeline

This directory contains scripts to import and process LinkedIn article exports for the Astro blog.

## Overview

The LinkedIn import pipeline is designed to be **idempotent** - it can be run multiple times to replace all blog content with an updated LinkedIn export. It performs the following transformations:

1. **LinkedIn Link Rewriting**: Converts links to other LinkedIn articles to point to local blog posts
2. **Redirect Unwrapping**: Strips LinkedIn redirect wrappers to reveal real external URLs
3. **Tracking Parameter Removal**: Removes tracking parameters (`?trk=...`, `?utm_source=...`, etc.)
4. **Video Embed Conversion**: Converts YouTube/Vimeo embeds to simple placeholders
5. **Image Localization**: Downloads images from LinkedIn CDN and rewrites paths to local copies
6. **CSS/Class Cleanup**: Removes LinkedIn-specific CSS classes and inline styles

## Files

- `linkedin_import.py` - Main import script with all transformations
- `import_linkedin.sh` - Simple wrapper script for easy execution
- `download_and_import.sh` - Script that downloads the sample export and runs import
- `requirements.txt` - Python dependencies

## Usage

### Basic Import

```bash
# Install dependencies and run import
./scripts/import_linkedin.sh path/to/linkedin-export.zip
```

### Manual Process

```bash
# 1. Install dependencies
pip3 install -r scripts/requirements.txt

# 2. Run the import
python3 scripts/linkedin_import.py linkedin-export.zip --blog-dir .

# 3. Test the build
npm run build
```

### Download Sample and Import

```bash
# Downloads the sample export from the GitHub issue and runs import
./scripts/download_and_import.sh
```

## What the Pipeline Does

1. **Extracts** article HTML files and Rich_Media.csv from the LinkedIn export ZIP
2. **Processes** each article:
   - Parses HTML and extracts metadata (title, date, etc.)
   - Applies all 6 cleanup transformations
   - Downloads and localizes images
   - Converts to clean Markdown with proper front matter
3. **Replaces** existing blog content in `src/content/blog/`
4. **Tests** that the Astro build still works

## Output

The pipeline generates:
- Clean Markdown files in `src/content/blog/` with proper YAML front matter
- Downloaded images in `public/images/[article-slug]/`
- Working files in `linkedin_work/` for inspection

## Front Matter Format

Each generated Markdown file includes:

```yaml
---
title: "Article Title"
date: 2025-07-02T04:22:13
slug: article-slug
original_url: "https://www.linkedin.com/pulse/original-linkedin-url"
linkedin_id: abcd1
banner: /images/article-slug/banner.jpg  # if image found
---
```

## Idempotent Design

The pipeline is designed to be run repeatedly:
- Completely replaces existing content
- Clears old images before downloading new ones
- Can be used for incremental updates when new LinkedIn exports are available

## Dependencies

- Python 3.6+
- beautifulsoup4
- python-slugify  
- markdownify
- requests

## Notes

- Image downloads may fail in restricted environments (sandbox, no internet access)
- LinkedIn embeds are converted to simple placeholders
- The pipeline preserves the original LinkedIn article URLs for reference
- All transformations are logged to console for review