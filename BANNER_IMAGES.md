# Banner Images Implementation

## Overview

The blog supports banner images for blog posts that are automatically downloaded during the LinkedIn import pipeline. Banner images appear at the top of each blog post page when they can be successfully downloaded.

## How It Works

### 1. LinkedIn Import Process

During the LinkedIn import (`scripts/linkedin_import.py`), the system:

1. **Detects Banner Images**: The first image in each LinkedIn article is treated as the banner image
2. **Downloads Images**: Attempts to download images from LinkedIn's CDN (`media.licdn.com`)
3. **Sets Frontmatter**: Adds `banner: /images/linkedin/{slug}/banner.{ext}` to the frontmatter only when images are successfully downloaded
4. **Updates Content**: Rewrites image references in markdown to point to local files
5. **Graceful Fallback**: When images can't be downloaded (e.g., no internet access), no banner frontmatter is set and no placeholder files are created

### 2. Banner Display

The banner images are displayed using the existing template in `src/pages/posts/[slug].astro`:

```astro
{post.data.banner && (
  <img src={post.data.banner} alt="" />
)}
```

### 3. No Placeholder Files

The system does not create placeholder files when images cannot be downloaded. This approach:

- **Keeps the repository clean**: No placeholder or empty files are committed
- **Graceful degradation**: Posts without banner images simply don't display a banner
- **Production ready**: When images can be downloaded (e.g., in production with internet access), real banner images will be used

## File Structure

```
public/images/linkedin/
├── article-slug-1/
│   ├── banner.jpg (or banner.png/gif)
│   └── image-2.jpg (additional images)
├── article-slug-2/
│   └── banner.png
└── ...
```

Note: Image directories are only created when images are successfully downloaded.

## Testing

The implementation has been tested with:

- ✅ 21 blog posts imported without placeholder files
- ✅ No banner frontmatter set when downloads fail
- ✅ No empty directories or placeholder files created
- ✅ Build process completes successfully without banner images
- ✅ Banner functionality works when real images are available

## Future Improvements

When internet access is available, the system can:

1. Download actual banner images from LinkedIn CDN
2. Support additional image formats (JPEG, PNG, GIF)
3. Process and optimize images for web delivery
4. Add image caching and CDN integration

## Debugging

To check if banner images are working:

1. **Check frontmatter**: Look for `banner:` field in `.md` files (only present when images were successfully downloaded)
2. **Check image files**: Verify files exist in `public/images/linkedin/{slug}/`
3. **Check build output**: Ensure images are copied to `dist/` during build
4. **Check HTML**: Look for `<img src="/images/linkedin/.../banner.*" alt="">` in generated pages

## Error Handling

The system gracefully handles:

- Network failures (no banner frontmatter set)
- Missing images (no banner display)
- Duplicate articles (prevents overwrites)
- Invalid image formats (defaults to .jpg)
- Missing directories (only created when needed)