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
- **Native posts are never overwritten**, and LinkedIn articles they claim are skipped. See "Native posts" below.

### Limitations and tips

- **"Basic" vs "Complete" exports**: LinkedIn's "Basic" export includes articles and `Rich_Media.csv` but **no `Shares.csv`**. If you need to import new shares, request a "Complete" export. A Basic export will safely add/update articles without touching existing shares.
- **Banner images require two imports for full coverage**: LinkedIn article HTML contains truncated/broken image URLs (`https://media.licdn.com/mediaD56...`) that return 404. The only reliable source of banner images is `Rich_Media.csv`, but a single export's CSV may not cover all articles (e.g., a Basic export's CSV stopped at January 2026 while articles went through April). **Workflow**: import a Basic export first to get article text, then re-import the Complete export when it arrives — its `Rich_Media.csv` will fill in the missing banners. Since the import is idempotent, running both is safe.
- **Slug stability**: Article slugs are derived from `<h1>` titles via `python-slugify`. If LinkedIn changes an article's title between exports, it will appear as a new article (new slug) while the old slug persists. You'd need to manually delete the stale slug directory.
- **Image downloads**: The import downloads images from `media.licdn.com` at import time. These URLs may expire eventually. If an image download fails, it logs a warning and continues. Re-running against a fresh export can recover images if LinkedIn has refreshed the URLs.
- **Cover photo matching**: Banner images from `Rich_Media.csv` are matched to articles by timestamp with a 2-hour tolerance window. Mismatches are possible if multiple articles were published close together.
- **No deletion of removed content**: If you delete an article on LinkedIn, the import won't remove it from the blog. Manual deletion of the slug directory is needed.
- **Working directory**: Intermediate artifacts go to `linkedin_work/` (gitignored). Safe to delete anytime.
- **Export ZIPs**: Stored in `LinkedIn exports/` (gitignored). Keep them around in case you need to re-import after script improvements.

## Native posts (written here first)

Most posts come from LinkedIn exports. Some are written here first, with graphics LinkedIn can't show, and posted to LinkedIn later. Such a *native post* replaces the LinkedIn copy, and re-imports leave it alone.

### Writing one

Put it anywhere under `src/content/blog/` **except** `linkedin/`, e.g. `src/content/blog/<slug>/index.md` with its images beside it. The importer never writes there (except to add LinkedIn link fields, below).

```yaml
---
title: "Reading 50,000 Pages of Public Comments on the Physician Fee Schedule"
date: 2026-10-05T12:00:00
added_at: 2026-10-05
slug: reading-50000-pages
draft: true            # optional: shown by `astro dev`, left out of production builds
supersedes_linkedin: "https://www.linkedin.com/pulse/…-josh-mandel-md-ab12c"   # optional, one value or a list
---
```

`supersedes_linkedin` names the LinkedIn article this post replaces: its LinkedIn URL (best), its 5-character `linkedin_id`, its imported slug, or its exact title. Without it, a native post still claims a LinkedIn article whose slug equals the native post's `slug` or the slug of its title — so an exact title match needs no field. Leave the field out until the LinkedIn version exists.

### What the import does with it (`scripts/native_posts.py`)

For each article in the export that a native post claims, the importer:
- skips writing it and deletes any earlier import of it in `linkedin/` (logged as `[NATIVE] Skipped … superseded by …`);
- adds `original_url`, `linkedin_id` and `intro_share` to the native post's frontmatter if they're missing, so the post links to the LinkedIn conversation like an imported one. It never changes the body or any field already set;
- points other articles' links to the LinkedIn version at the native post's slug.

The site applies the same claims (`src/lib/posts.ts`, used by the index, post pages and RSS), so a LinkedIn copy is hidden as soon as a native post claims it, before the next import. A `draft: true` post claims only in `astro dev`; in production builds the LinkedIn copy stays visible until the draft flag is removed.

### Checking a new export for overlaps (agents: do this every import)

LinkedIn versions often go up days or weeks after the native post, with a reworded headline, so title matching misses them. After each import, the importer prints an `[OVERLAP?]` block listing LinkedIn articles that may be the same story as a native post not yet linked to LinkedIn (no `original_url`): dates within a week, titles sharing most words, or dates within 90 days with somewhat similar titles. For each pair listed, and for any new LinkedIn article dated after a native post that the check didn't list:

1. Read both. Same story (even if edited or shortened for LinkedIn)? Add the printed `supersedes_linkedin: "<url>"` line to the native post and re-run the import — the LinkedIn copy is removed and the native post gets its LinkedIn link.
2. Different story? Leave both. The pair stops being reported once the native post is linked to its own LinkedIn version, or after 90 days unless the titles nearly match.

Mention every superseded article and every judgment call in your summary to the user. If unsure whether two posts are the same story, ask rather than guess.

### Keeping a native post and its LinkedIn version in sync (via a browser)

An export can be weeks away, and it never carries LinkedIn edits back into a native post. For small jobs, such as pulling a published article's edits into its native copy, fetching its cover image, or putting a native post onto LinkedIn, drive a real browser instead.

**Browser setup.** Use a separate Chromium profile with remote debugging, so the user's own browser is untouched. The user logs in once; the profile keeps the session:

```bash
chromium --user-data-dir="$SCRATCH/li-profile" --remote-debugging-port=9333 \
  --no-first-run https://www.linkedin.com/login &
```

Connect with `puppeteer-core` (`puppeteer.connect({ browserURL: "http://127.0.0.1:9333", defaultViewport: null })`). Never print cookies or tokens.

**Backporting LinkedIn edits into a native post:**
1. **Get the live text.** Open the published article (`original_url`) and take `document.querySelector('.reader-article-content').innerHTML`. Figures are `<figure>` elements with an optional `<figcaption>`. LinkedIn wraps each list in an extra `<p>` holding the same text; skip that duplicate.
2. **Diff block by block** against the native post (paragraphs, headings, list items, captions; normalize whitespace and curly quotes) and look at what actually changed. Usually it's wording, an added or removed paragraph or figure, or a TL;DR box (a `<blockquote>` becomes `> ` in markdown).
3. **Apply only the changes.** Keep the native post's own figures (SVGs, interactive charts) at the matching positions; LinkedIn's figures are flattened PNGs. Captions longer than 250 characters can't exist on LinkedIn, so keep the native post's longer captions and links unless the user's edit changed their meaning.
4. **Fix LinkedIn's link damage on the way in:**
   - It auto-links bare domains (e.g. `regulations.gov` becomes `http://regulations.gov`). Unwrap these, or point them at a specific https page.
   - Profile links are relative (`/in/name/`). Prefix them with `https://www.linkedin.com`.
   - Links to this blog (`https://joshuamandel.com/blog/posts/...`) become `/blog/posts/...`.
5. **Cover image.** Find the `img` whose src contains `article-cover_image`, fetch it from the page (so the session's cookies apply), and match it against the original file (often in `~/Downloads`) by comparing a downscaled grayscale version. Use the original full-resolution file as `banner.png`, not LinkedIn's 1280-px copy. Set `banner: ./banner.png` in the frontmatter.
6. **Build and check** before pushing: `npm run build`, then load the post. For interactive posts, hover the charts with puppeteer, check that tooltips appear, and check the console for errors.

**Putting a native post onto LinkedIn** (the user publishes, or explicitly asks you to):
- **Text.** In the article editor (`.ProseMirror`), paste HTML with a synthetic `ClipboardEvent("paste")` carrying `text/html`. Headings become h3, and lists and links survive.
- **Images.** LinkedIn takes only raster images. Render charts with puppeteer at a high device scale factor. LinkedIn stores at most **1,500 px tall** (up to about 2,232 px wide), and taller images are scaled down and look blurry. Lay tall figures out wider, or split them into parts.
  - **Inserting.** Paste a `File` through the same paste event into an *empty* paragraph. Leave a placeholder paragraph, select its text and press Backspace, then paste.
  - **Replacing.** To replace an existing image and keep its caption, use the figure's "Edit image" button, then the dialog's Delete, then upload through the dialog's file input, then Next. Click the button with `element.click()`; a mouse click on the hover overlay doesn't always register.
- **Captions** are `<textarea>`s inside each figure. Set them with the native value setter plus an `input` event; don't type into them.
- **Links in the editor.** Select the text, press Ctrl+K, set "Paste link here", then Apply. Pasting HTML over a selection doesn't replace links.
- **Cover.** "Upload from computer" opens a file chooser (`page.waitForFileChooser()`), then Next.
- **Hazards, all seen in practice:**
  - **Ctrl+A inside a caption selects the whole article,** and typing then replaces it. Undo (Ctrl+Z in the editor) recovers it.
  - **Undo can restore a select-all.** Afterwards, collapse the selection to a caret before any keyboard input.
  - **Keys reach the article.** The editor receives keystrokes from inside its figures, so check `document.activeElement` and the block count before and after every scripted edit, and stop if they change unexpectedly.
  - **Saves are immediate.** LinkedIn autosaves within seconds, so an error is saved too. After each step, confirm "Draft - saved" and the block count.
- **After publishing,** set `supersedes_linkedin` (or rely on an exact title match) so the next import skips the article.

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
