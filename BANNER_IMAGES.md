# Banner Images Implementation

## Overview

Banner images are normalized during the LinkedIn import workflow so every published post references local assets under `/images/linkedin/{slug}/banner.<ext>`.

## Workflow Summary

### 1. LinkedIn Import

During `scripts/linkedin_import.py` the importer:

1. Detects candidate banner images from the LinkedIn HTML export.
2. Attempts to download each banner immediately using URLs in `Rich_Media.csv`.
3. Emits markdown with `banner:` frontmatter pointing to the downloaded file when available, or the original remote URL when download fails (offline/blocked).

### 2. Banner Normalization Script

Whether run manually or via `npm run build`, `scripts/download_banner_images.py`:

1. Scans every markdown file in `src/content/blog/**` for a remote `banner:` URL.
2. Downloads missing images to `src/content/blog/linkedin/{slug}/banner.<ext>` (next to the markdown file).
3. Updates the frontmatter so it references the co-located copy (`./banner.<ext>`).
4. Skips posts that already use local banners.

Because the script is idempotent, you can run it after any manual edits or imports to ensure all banners are local before committing.

### 3. Banner Display

The Astro theme renders the banner via:

```astro
{post.data.banner && (
  <img src={post.data.banner} alt="" />
)}
```

As a result, posts without a banner simply omit the `<img>` element.

## File Structure

```
src/content/blog/linkedin/
├── article-slug-1/
│   ├── banner.png
│   └── index.md
├── article-slug-2/
│   ├── banner.jpg
│   └── index.md
└── …
```

When multiple imports run, existing images are reused if present.

## Testing Checklist

- ✅ `python3 scripts/download_banner_images.py` completes without errors.
- ✅ Frontmatter for each LinkedIn-derived post references `/images/linkedin/{slug}/banner.<ext>`.
- ✅ `npm run test-build` succeeds locally.
- ✅ Final `dist/` folder contains the copied banner assets.

## Troubleshooting

- **Remote URLs still present** – Run `python3 scripts/download_banner_images.py` from the repo root.
- **Download failures** – Check network access or LinkedIn CDN availability; the script logs failures but leaves the remote URL intact.
- **Missing files in dist** – Confirm the banner exists next to the markdown (`src/content/blog/linkedin/{slug}/banner.<ext>`); Astro will bundle it automatically through the content collection.

With this flow the repository stays consistent: markdown always points at checked-in images, ensuring GitHub Pages builds remain stable even if LinkedIn URLs expire.
