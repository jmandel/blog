# Banner Images Implementation

## Overview

The blog now supports banner images for blog posts that are automatically downloaded and processed during the LinkedIn import pipeline. Banner images appear at the top of each blog post page.

## How It Works

### 1. LinkedIn Import Process

During the LinkedIn import (`scripts/linkedin_import.py`), the system:

1. **Detects Banner Images**: The first image in each LinkedIn article is treated as the banner image
2. **Downloads Images**: Attempts to download images from LinkedIn's CDN (`media.licdn.com`)
3. **Creates Placeholders**: If download fails (e.g., no internet access), creates SVG placeholder images
4. **Sets Frontmatter**: Adds `banner: /images/linkedin/{slug}/banner.{ext}` to the frontmatter
5. **Updates Content**: Rewrites image references in markdown to point to local files

### 2. Banner Display

The banner images are displayed using the existing template in `src/pages/posts/[slug].astro`:

```astro
{post.data.banner && (
  <img src={post.data.banner} alt="" />
)}
```

### 3. Placeholder Images

When images cannot be downloaded (network restrictions), the system creates SVG placeholder banners:

- **Size**: 800x400 pixels
- **Style**: Light gray background with subtle border
- **Text**: "Banner Image" centered
- **Format**: SVG for scalability and small file size

## File Structure

```
public/images/linkedin/
├── article-slug-1/
│   ├── banner.svg (or banner.jpg/png)
│   └── image-2.jpg (additional images)
├── article-slug-2/
│   └── banner.svg
└── ...
```

## Testing

The implementation has been tested with:

- ✅ 21 blog posts imported with banner images
- ✅ Placeholder banners created when downloads fail
- ✅ Banner frontmatter correctly set
- ✅ Images display properly in blog post pages
- ✅ Build process completes successfully (23 pages)

## Future Improvements

When internet access is available, the system can:

1. Download actual banner images from LinkedIn CDN
2. Replace placeholder SVGs with real images
3. Support additional image formats (JPEG, PNG, GIF)
4. Create better placeholder images using PIL if available

## Debugging

To check if banner images are working:

1. **Check frontmatter**: Look for `banner:` field in `.md` files
2. **Check image files**: Verify files exist in `public/images/linkedin/{slug}/`
3. **Check build output**: Ensure images are copied to `dist/` during build
4. **Check HTML**: Look for `<img src="/images/linkedin/.../banner.*" alt="">` in generated pages

## Error Handling

The system gracefully handles:

- Network failures (creates placeholders)
- Missing images (skips banner)
- Duplicate articles (prevents overwrites)
- Invalid image formats (defaults to .jpg)
- Missing PIL library (falls back to SVG)