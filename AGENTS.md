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

5. **`scripts/backfill_linkedin_banners.py`** — One-shot recovery script for articles missing banners. Walks `src/content/blog/linkedin/`, finds articles with no `banner.*` file, fetches the live LinkedIn URL, extracts `og:image` from the HTML, downloads the image, and saves it. Detects and skips bogus fallbacks (LinkedIn profile-pic 96x96 PNGs and SVG placeholders). Run with: `uv run --python .venv-import python scripts/backfill_linkedin_banners.py`

### Merge semantics (idempotent import)

The import is additive/idempotent:
- Articles and shares already in the blog that are **not** in the new export are **preserved unchanged**.
- Articles and shares that **are** in the new export **overwrite** the existing version (the individual directory is cleaned and regenerated).
- **Manually-placed `banner.*` files survive re-imports.** The article processor saves the banner before cleaning the directory and restores it if the new import didn't produce one of its own. So you can safely drop a `banner.png` into any article folder.
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

### Banner image recovery: lessons from April 2026

After the April 2026 import, ~21 articles were left without banners despite the export being current. Here's what was wrong and how to handle it next time, so future agents don't waste time re-discovering all of this.

**What's broken in LinkedIn's export format:**

1. **`Rich_Media.csv` stops including article cover photos around February 2026.** It still records videos and other media types from later dates, but the entries `"You uploaded a article cover photo on ..."` simply stop. This appears to be a permanent change in LinkedIn's export pipeline, not a snapshot lag — both Basic and Complete exports generated weeks apart show the exact same cutoff. **Don't waste time requesting another export hoping it will be fresher.**

2. **Article HTML files contain truncated/broken image URLs.** Inside each `.html` file you'll see things like `<img src="https://media.licdn.com/mediaD5612AQHG6ExtLq-hww">`. These URLs return 404 — they're missing the `/dms/image/v2/...` path structure and the signature query string. The image processor's filter on this pattern (line ~440 of `linkedin_articles.py`: `if "/media" in src and "/dms/image/" not in src: img.decompose()`) is intentional — these URLs are unrecoverable.

3. **Article HTML `<head>` has no useful metadata.** No `og:image`, no structured data, no canonical link with image hints. Don't bother grepping the export's HTML for image URLs as a workaround.

**The recovery path that works:**

The live LinkedIn article pages (the `original_url` in each article's frontmatter) DO have proper `og:image` meta tags pointing to real cover image URLs with valid signatures. Fetching these public pages with a normal browser User-Agent works without authentication. This is what `scripts/backfill_linkedin_banners.py` does.

**Critical gotcha — bogus og:image fallbacks:**

For articles where the author never set a custom cover, LinkedIn's `og:image` falls back to one of two placeholders:
- A **96x96 PNG of the author's profile picture** (~800 bytes, 8-bit colormap)
- A small **SVG placeholder** (~1300 bytes, served as `image/svg+xml` even when the URL ends in `.jpg`)

These look like successful downloads but produce ugly, wrong banners. Always validate before saving. The backfill script's `is_bogus_banner()` function does this. Detection rules:
- Content type contains `svg` OR file starts with `<?xml`/`<svg` → SVG placeholder
- PNG with width and height ≤200 and roughly square (|w−h|<10) → profile picture
- Total bytes < 4096 → too small to be a real banner

**If a backfilled banner makes it through these checks but still looks wrong:** delete the `banner.*` file AND remove the `banner: ./banner.X` line from that article's frontmatter, then re-run the backfill. The script's idempotent — it only touches articles with no `banner.*` file.

**The 4 articles that genuinely have no cover image** (as of April 2026):
- `an-order-to-harm`
- `cms-rfi-mcp-now-it-s-your-turn-to-analyze-10k-pages`
- `healthcare-s-high-tech-future-forgets-one-thing-the-humans`
- `speeding-spec-development-by-making-ais-argue`

If a future LinkedIn export DOES include cover photos for these (e.g., LinkedIn fixes their pipeline, or the author retroactively uploads covers), the standard `local-import.sh` flow will pick them up automatically.

**Why the `linkedin_articles.py` per-article rmtree won't clobber backfilled banners:** the article processor saves any existing `banner.*` file in memory before the rmtree and restores it after image processing if the import didn't produce its own banner. So backfilled and manually-placed banners both survive future imports cleanly.
