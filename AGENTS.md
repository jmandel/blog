# Agent Instructions

## LinkedIn Import

### How to run

```bash
./scripts/local-import.sh path/to/linkedin-export.zip
```

This is the single entry point. It handles the Python venv, runs the import pipeline, normalizes banner images, and verifies the Astro build.

### What it does

1. **`scripts/linkedin_import.py`** — Orchestrator. Filters the export ZIP to extract article HTML + `Rich_Media.csv`, then delegates to the article and share processors.

2. **`scripts/linkedin_articles.py`** — Parses each article's HTML, extracts metadata (title, dates, linkedin_id), then:
   - Rewrites inter-article LinkedIn links to local `/blog/posts/{slug}` paths
   - Unwraps LinkedIn redirect wrappers to reveal true URLs
   - Strips tracking parameters (`?trk=`, `?utm_*`)
   - Converts YouTube/Vimeo iframes to embeds
   - Downloads and co-locates inline images from `media.licdn.com`
   - Matches cover photos from `Rich_Media.csv` by timestamp proximity
   - Outputs markdown + frontmatter to `src/content/blog/linkedin/{slug}/index.md`

3. **`scripts/linkedin_shares.py`** — Reads `Shares.csv` (if present), deduplicates by share ID, then:
   - Matches "intro" shares to articles using a scoring algorithm (time proximity + title similarity + URL matching)
   - Intro shares get embedded in the article's frontmatter as `intro_share:`
   - Standalone shares get written to `src/content/shares/linkedin/share-{id}/index.md`

4. **`scripts/download_banner_images.py`** — Post-processing pass that downloads any remote banner URLs still in frontmatter and replaces them with local paths.

### Merge semantics (idempotent import)

The import is additive/idempotent:
- Articles and shares already in the blog that are **not** in the new export are **preserved unchanged**.
- Articles and shares that **are** in the new export **overwrite** the existing version (the individual directory is cleaned and regenerated).
- Running the same export twice produces identical results.

### Limitations and tips

- **"Basic" vs "Complete" exports**: LinkedIn's "Basic" export includes articles and `Rich_Media.csv` but **no `Shares.csv`**. If you need to import new shares, request a "Complete" export. A Basic export will safely add/update articles without touching existing shares.
- **Banner images require two imports for full coverage**: LinkedIn article HTML contains truncated/broken image URLs (`https://media.licdn.com/mediaD56...`) that return 404. The only reliable source of banner images is `Rich_Media.csv`, but a single export's CSV may not cover all articles (e.g., a Basic export's CSV stopped at January 2026 while articles went through April). **Workflow**: import a Basic export first to get article text, then re-import the Complete export when it arrives — its `Rich_Media.csv` will fill in the missing banners. Since the import is idempotent, running both is safe.
- **Slug stability**: Article slugs are derived from `<h1>` titles via `python-slugify`. If LinkedIn changes an article's title between exports, it will appear as a new article (new slug) while the old slug persists. You'd need to manually delete the stale slug directory.
- **Image downloads**: The import downloads images from `media.licdn.com` at import time. These URLs may expire eventually. If an image download fails, it logs a warning and continues. Re-running against a fresh export can recover images if LinkedIn has refreshed the URLs.
- **Cover photo matching**: Banner images from `Rich_Media.csv` are matched to articles by timestamp with a 2-hour tolerance window. Mismatches are possible if multiple articles were published close together.
- **No deletion of removed content**: If you delete an article on LinkedIn, the import won't remove it from the blog. Manual deletion of the slug directory is needed.
- **Working directory**: Intermediate artifacts go to `linkedin_work/` (gitignored). Safe to delete anytime.
- **Export ZIPs**: Stored in `LinkedIn exports/` (gitignored). Keep them around in case you need to re-import after script improvements.
