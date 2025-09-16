# LinkedIn Import Pipeline

This directory contains scripts to import and process LinkedIn article exports for the Astro blog.

## Overview

The LinkedIn import pipeline is designed to be **idempotent** – it can be run repeatedly to replace all LinkedIn-derived blog content with a fresh export. The tooling handles:

1. **LinkedIn Link Rewriting**: Converts links to other LinkedIn articles so they point to local `/posts/{slug}` pages.
2. **Redirect Unwrapping**: Strips LinkedIn redirect wrappers to reveal the true external destination.
3. **Tracking Parameter Removal**: Removes `?trk=…`, `?utm_*`, and similar query params.
4. **Video Embed Conversion**: Converts YouTube and Vimeo embeds into simple placeholders that render with Astro shortcodes.
5. **Image Localization**: Downloads inline images and post banners, rewriting markdown to use local copies.
6. **CSS/Class Cleanup**: Removes LinkedIn-specific CSS classes and inline styles.

## Files

- `local-import.sh` – One-command workflow for importing a ZIP, normalizing banners, and test-building the site.
- `linkedin_import.py` – Main import script with all transformations.
- `download_banner_images.py` – Normalizes banner images across existing markdown.
- `import_linkedin.sh` – Legacy wrapper retained for backwards compatibility.
- `requirements.txt` – Python dependencies for the Python-based tooling.

## Recommended Local Workflow

Run the helper script and let it orchestrate everything:

```bash
./scripts/local-import.sh path/to/linkedin-export.zip
```

### What the script does

1. Ensures a `.venv-import` `uv` environment exists and syncs `scripts/requirements.txt`.
2. Runs `linkedin_import.py` to regenerate `src/content/blog/linkedin/{slug}/index.md` and download banners into the same folder.
3. Re-runs `download_banner_images.py` (via the same `uv` env) to catch any remaining remote references.
4. Installs Node dependencies on first run and executes `npm run test-build` to verify Astro builds.

After the script finishes, review the git diff, commit, and push to trigger GitHub Pages.

### Manual Workflow (optional)

If you need fine-grained control or want to output to a scratch directory, you can execute the individual steps yourself:

```bash
uv venv .venv-import
uv pip sync --python .venv-import scripts/requirements.txt
uv run --python .venv-import python scripts/linkedin_import.py linkedin-export.zip --workdir linkedin_work --blog-dir .
uv run --python .venv-import python scripts/download_banner_images.py
npm run test-build
```

## Manual Process

If you need to run each step by hand:

```bash
pip3 install -r scripts/requirements.txt
python3 scripts/linkedin_import.py linkedin-export.zip --workdir linkedin_work --blog-dir .
python3 scripts/download_banner_images.py
npm run test-build
```

## Continuous Deployment Notes

GitHub Actions now **only builds** the already-generated static assets. Heavy processing (imports, downloads) should happen locally before committing. The default workflow (`.github/workflows/deploy.yml`) installs Node dependencies, runs `npm run build`, and deploys the generated `dist/` folder to GitHub Pages.

## Output

Running the importer produces:

- Markdown articles in `src/content/blog/linkedin/{slug}/index.md`
- Banners stored alongside each article as `src/content/blog/linkedin/{slug}/banner.<ext>`
- Working files in `linkedin_work/`

All generated files are deterministic, so repeated imports with the same ZIP yield identical output.

## Frontmatter Reference

Each generated markdown file follows this structure:

```yaml
---
title: "Article Title"
date: 2025-07-02T04:22:13
slug: article-slug
original_url: "https://www.linkedin.com/pulse/original-linkedin-url"
linkedin_id: abcd1
banner: /images/linkedin/article-slug/banner.jpg
---
```

## Dependencies

- Python 3.9+
- `beautifulsoup4`
- `python-slugify`
- `markdownify`
- `requests`

Install them with `pip3 install -r scripts/requirements.txt`.

## Troubleshooting Tips

- Ensure `LinkedIn exports/*.zip` is git-ignored so large archives do not end up in commits.
- Delete `linkedin_work/` when you want a clean slate; it is ignored by git.
- If banner downloads fail locally (e.g., network issues), the build falls back to remote URLs – rerun `download_banner_images.py` once connectivity is restored.
