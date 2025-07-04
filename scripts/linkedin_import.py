#!/usr/bin/env python3
"""
linkedin_import.py

Idempotent LinkedIn import pipeline that:
1. Extracts articles from LinkedIn export ZIP
2. Processes and cleans up content with 6 transformations
3. Generates Astro-ready Markdown files
4. Downloads and localizes images
5. Replaces existing blog content
"""

import zipfile, os, re, csv, pathlib, datetime as dt, html, shutil, urllib.parse
from bs4 import BeautifulSoup
from slugify import slugify
from markdownify import markdownify as md
import requests
from typing import Dict, Optional, List

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
BLOG_BASE_URL = "https://joshuamandel.com"
IMAGES_DIR = "public/images"
CONTENT_DIR = "src/content/blog"
LINKEDIN_SUBDIR = "linkedin"  # LinkedIn content goes in a subfolder

# --------------------------------------------------------------------------- #
# 1. Filtering step (unchanged from original)
# --------------------------------------------------------------------------- #
def extract_articles_only(src_zip: str, dst_zip: str) -> None:
    """
    Write a new ZIP containing only article HTML files and Rich_Media.csv.
    """
    with zipfile.ZipFile(src_zip, "r") as zin, \
         zipfile.ZipFile(dst_zip, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            n = info.filename
            keep = (
                (n.startswith("Articles/Articles/") and n.endswith(".html"))
                or n == "Rich_Media.csv"
            )
            if keep:
                zout.writestr(info, zin.read(n))
    print(f"[✓] Wrote filtered archive ⇒ {dst_zip}")

# --------------------------------------------------------------------------- #
# 2. Cleanup transformations
# --------------------------------------------------------------------------- #

def cleanup_linkedin_links(soup: BeautifulSoup, slug_mapping: Dict[str, str]) -> None:
    """
    Transformation 1: Rewrite links to other LinkedIn articles to point at local blog slugs
    """
    for link in soup.find_all("a", href=True):
        href = link["href"]
        
        # Match LinkedIn pulse URLs
        linkedin_match = re.search(r'linkedin\.com/pulse/([^/?]+)', href)
        if linkedin_match:
            linkedin_slug = linkedin_match.group(1)
            # Try to find matching local slug
            for local_slug, linkedin_ref in slug_mapping.items():
                if linkedin_ref in linkedin_slug or linkedin_slug in linkedin_ref:
                    link["href"] = f"/posts/{local_slug}"
                    print(f"[LINK] Rewrote LinkedIn link to local: {href} → /posts/{local_slug}")
                    break

def cleanup_redirect_wrappers(soup: BeautifulSoup) -> None:
    """
    Transformation 2: Strip LinkedIn "redir/..." wrappers and keep real external URL
    """
    for link in soup.find_all("a", href=True):
        href = link["href"]
        
        # Match LinkedIn redirect URLs
        if "linkedin.com/redir/general-malware-page?url=" in href:
            try:
                # Extract the real URL from the redirect
                parsed = urllib.parse.urlparse(href)
                params = urllib.parse.parse_qs(parsed.query)
                if "url" in params:
                    real_url = urllib.parse.unquote(params["url"][0])
                    link["href"] = real_url
                    print(f"[REDIR] Unwrapped redirect: {real_url}")
            except Exception as e:
                print(f"[WARN] Failed to unwrap redirect {href}: {e}")

def cleanup_tracking_params(soup: BeautifulSoup) -> None:
    """
    Transformation 3: Remove tracking params (?trk=..., ?utm_source=linkedin&..., etc.)
    """
    tracking_params = ['trk', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term']
    
    for link in soup.find_all("a", href=True):
        href = link["href"]
        try:
            parsed = urllib.parse.urlparse(href)
            if parsed.query:
                # Parse and filter out tracking parameters
                params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
                clean_params = {k: v for k, v in params.items() if k not in tracking_params}
                
                # Rebuild URL without tracking params
                new_query = urllib.parse.urlencode(clean_params, doseq=True)
                clean_url = urllib.parse.urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, new_query, parsed.fragment
                ))
                
                if clean_url != href:
                    link["href"] = clean_url
                    print(f"[TRACK] Removed tracking params: {href} → {clean_url}")
        except Exception as e:
            print(f"[WARN] Failed to clean tracking params from {href}: {e}")

def convert_video_embeds(soup: BeautifulSoup) -> None:
    """
    Transformation 4: Convert YouTube (and Vimeo) embeds to Astro components
    """
    # Find all iframes that might contain video embeds
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if not src:
            continue
            
        # Extract YouTube video ID
        youtube_match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', src)
        if youtube_match:
            video_id = youtube_match.group(1)
            # Replace with a comment that can be post-processed
            iframe.replace_with(soup.new_string(f"<!-- YOUTUBE:{video_id} -->"))
            print(f"[VIDEO] Converted YouTube embed: {video_id}")
            continue
        
        # Extract Vimeo video ID  
        vimeo_match = re.search(r'vimeo\.com/video/(\d+)', src)
        if vimeo_match:
            video_id = vimeo_match.group(1)
            iframe.replace_with(soup.new_string(f"<!-- VIMEO:{video_id} -->"))
            print(f"[VIDEO] Converted Vimeo embed: {video_id}")
            continue
            
        # Handle LinkedIn embeds (keeping the original logic for backward compatibility)
        if "linkedin.com/embeds/publishingEmbed.html" in src:
            # Extract article ID from LinkedIn embed
            article_match = re.search(r'articleId=(\d+)', src)
            if article_match:
                article_id = article_match.group(1)
                # Convert to a comment placeholder
                iframe.replace_with(soup.new_string(f"<!-- LINKEDIN:{article_id} -->"))
                print(f"[EMBED] Converted LinkedIn embed: {article_id}")
    
    # Also check for YouTube URLs in different patterns (fallback)
    for a_tag in soup.find_all("a"):
        href = a_tag.get("href", "")
        # Handle both youtube.com/watch?v= and youtu.be/ patterns
        youtube_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', href)
        if youtube_match:
            video_id = youtube_match.group(1)
            # Replace link with embedded video placeholder
            a_tag.replace_with(soup.new_string(f"<!-- YOUTUBE:{video_id} -->"))
            print(f"[VIDEO] Converted YouTube link to embed: {video_id}")

def download_and_localize_images(soup: BeautifulSoup, article_slug: str, images_base_dir: str) -> None:
    """
    Transformation 5: Download images from LinkedIn CDN and rewrite src to local paths
    """
    images_dir = pathlib.Path(images_base_dir) / article_slug
    images_dir.mkdir(parents=True, exist_ok=True)
    
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-delayed-url")
        if not src:
            continue
            
        # Skip if already local
        if not src.startswith("http"):
            continue
            
        # Skip if not from LinkedIn CDN
        if "media.licdn.com" not in src:
            continue
            
        try:
            # Download the image
            response = requests.get(src, timeout=30)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'gif' in content_type:
                ext = '.gif'
            else:
                ext = '.jpg'  # Default
            
            # Generate filename
            img_counter = len(list(images_dir.glob("*"))) + 1
            if img_counter == 1:
                filename = f"banner{ext}"
            else:
                filename = f"image-{img_counter}{ext}"
            
            # Save image
            img_path = images_dir / filename
            with open(img_path, 'wb') as f:
                f.write(response.content)
            
            # Update img src to local path
            local_src = f"/images/{LINKEDIN_SUBDIR}/{article_slug}/{filename}"
            img["src"] = local_src
            
            # Remove LinkedIn-specific attributes
            for attr in ["data-delayed-url", "data-ghost-img"]:
                if attr in img.attrs:
                    del img[attr]
            
            print(f"[IMAGE] Downloaded and localized: {filename}")
            
        except Exception as e:
            print(f"[WARN] Failed to download image {src}: {e}")

def cleanup_css_and_classes(soup: BeautifulSoup) -> None:
    """
    Transformation 6: Flatten inline CSS & LinkedIn classes
    """
    # Remove LinkedIn-specific classes
    linkedin_classes = ['share-article', 'article-wrap', 'core-rail', 'feed-shared-inline-video']
    
    for element in soup.find_all(class_=True):
        original_classes = element.get('class', [])
        clean_classes = [cls for cls in original_classes if not any(lc in cls for lc in linkedin_classes)]
        
        if clean_classes != original_classes:
            if clean_classes:
                element['class'] = clean_classes
            else:
                del element['class']
    
    # Remove or simplify inline styles
    for element in soup.find_all(style=True):
        style = element['style']
        # Remove LinkedIn-specific styles but keep basic formatting
        if any(prop in style.lower() for prop in ['linkedin', 'feed-', 'share-']):
            del element['style']
        elif 'display:none' in style or 'visibility:hidden' in style:
            element.decompose()  # Remove hidden elements entirely

# --------------------------------------------------------------------------- #
# 3. Main processing functions
# --------------------------------------------------------------------------- #

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})?")
ID_RE   = re.compile(r"-([a-z0-9]{5})$")      # last -5 chars after last dash

def _parse_date(soup: BeautifulSoup, filename: str) -> dt.datetime:
    """Find a date in the HTML or fallback to the filename."""
    # a) <p class="created">Created on 2025-07-02 04:22</p>
    tag = soup.find("p", class_="created")
    if tag:
        m = DATE_RE.search(tag.get_text())
        if m:
            return dt.datetime.fromisoformat(m.group(0))
    # b) prefix in filename 2025-07-02 04:22:13.0-slug.html
    m = DATE_RE.search(filename)
    if m:
        return dt.datetime.fromisoformat(m.group(1))
    # c) give up — use "now"
    return dt.datetime.now()

def build_slug_mapping(article_zip: str) -> Dict[str, str]:
    """
    Build a mapping of slugs to LinkedIn references for link rewriting
    """
    slug_mapping = {}
    
    with zipfile.ZipFile(article_zip) as zin:
        for info in zin.infolist():
            if not info.filename.endswith(".html"):
                continue
                
            raw = zin.read(info.filename).decode("utf-8", "ignore")
            soup = BeautifulSoup(raw, "html.parser")
            
            # Extract title and create slug
            title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text(strip=True)
                slug = slugify(title, lowercase=True)
                
                # Extract LinkedIn reference
                basename = os.path.basename(info.filename)[:-5]  # strip .html
                slug_mapping[slug] = basename
    
    return slug_mapping

def build_linkedin_id_mapping(article_zip: str) -> Dict[str, str]:
    """
    Build a mapping of LinkedIn article IDs to local article slugs
    """
    id_to_slug_mapping = {}
    
    with zipfile.ZipFile(article_zip) as zin:
        for info in zin.infolist():
            if not info.filename.endswith(".html"):
                continue
                
            raw = zin.read(info.filename).decode("utf-8", "ignore")
            soup = BeautifulSoup(raw, "html.parser")
            
            # Extract title and create slug
            title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text(strip=True)
                slug = slugify(title, lowercase=True)
                
                # Look for LinkedIn article ID in embeds within this article
                for iframe in soup.find_all("iframe"):
                    src = iframe.get("src", "")
                    if "linkedin.com/embeds/publishingEmbed.html" in src:
                        article_match = re.search(r'articleId=(\d+)', src)
                        if article_match:
                            article_id = article_match.group(1)
                            id_to_slug_mapping[article_id] = slug
    
    return id_to_slug_mapping

def linkedin_zip_to_markdown(article_zip: str, output_dir: str, blog_base_dir: str) -> None:
    """
    Read a trimmed ZIP and emit cleaned Markdown files, replacing existing content.
    """
    out_dir = pathlib.Path(output_dir).expanduser()
    articles_dir = out_dir / "articles"
    articles_dir.mkdir(parents=True, exist_ok=True)
    
    # Build slug mapping for internal link rewriting
    slug_mapping = build_slug_mapping(article_zip)
    
    # Build LinkedIn ID to slug mapping for embed conversion
    linkedin_id_mapping = build_linkedin_id_mapping(article_zip)
    
    # Clear existing LinkedIn blog content (idempotent approach)
    linkedin_content_dir = pathlib.Path(blog_base_dir) / CONTENT_DIR / LINKEDIN_SUBDIR
    if linkedin_content_dir.exists():
        print(f"[CLEAN] Removing existing LinkedIn content from {linkedin_content_dir}")
        shutil.rmtree(linkedin_content_dir)
    linkedin_content_dir.mkdir(parents=True, exist_ok=True)
    
    # Clear existing LinkedIn images
    linkedin_images_dir = pathlib.Path(blog_base_dir) / IMAGES_DIR / LINKEDIN_SUBDIR
    if linkedin_images_dir.exists():
        print(f"[CLEAN] Removing existing LinkedIn images from {linkedin_images_dir}")
        shutil.rmtree(linkedin_images_dir)
    linkedin_images_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Rich_Media.csv
    rich_media = {}
    processed_slugs = set()  # Track processed slugs to avoid duplicates
    article_count = 0
    
    with zipfile.ZipFile(article_zip) as zin:
        if "Rich_Media.csv" in zin.namelist():
            with zin.open("Rich_Media.csv") as f:
                reader = csv.DictReader((l.decode("utf-8", "ignore") for l in f))
                for row in reader:
                    rich_media[row.get("Description", "")] = row
        
        # Process each HTML article
        for info in zin.infolist():
            if not info.filename.endswith(".html"):
                continue
            
            print(f"\n[PROCESS] {info.filename}")
            
            raw = zin.read(info.filename).decode("utf-8", "ignore")
            soup = BeautifulSoup(raw, "html.parser")
            
            # ------ metadata ------------------------------------------------
            title_tag = soup.find("h1")
            if not title_tag:
                print(f"[WARN] No title found in {info.filename}, skipping")
                continue
                
            title = title_tag.get_text(strip=True)
            if not title:
                print(f"[WARN] Empty title in {info.filename}, skipping")
                continue
                
            date = _parse_date(soup, info.filename)
            slug = slugify(title, lowercase=True)
            
            if not slug:
                print(f"[WARN] Could not generate slug for '{title}' in {info.filename}, skipping")
                continue
            
            # Check for duplicate slugs
            if slug in processed_slugs:
                print(f"[WARN] Duplicate slug '{slug}' for '{title}' in {info.filename}, skipping")
                continue
            
            processed_slugs.add(slug)
            
            # Build URL + ID (best-effort)
            basename = os.path.basename(info.filename)[:-5]  # strip .html
            m = ID_RE.search(basename)
            art_id = m.group(1) if m else ""
            original_url = f"https://www.linkedin.com/pulse/{basename}"
            
            # ------ Apply all cleanup transformations --------------------
            cleanup_linkedin_links(soup, slug_mapping)
            cleanup_redirect_wrappers(soup)
            cleanup_tracking_params(soup)
            convert_video_embeds(soup)
            download_and_localize_images(soup, slug, str(pathlib.Path(blog_base_dir) / IMAGES_DIR / LINKEDIN_SUBDIR))
            cleanup_css_and_classes(soup)
            
            # ------ Generate markdown -----------------------------------
            article_content = soup.find("article") or soup.body
            if article_content:
                body_md = md(str(article_content), strip=["script", "style"])
            else:
                body_md = md(str(soup), strip=["script", "style"])
            
            # Post-process to convert video placeholders to Astro components
            body_md = re.sub(
                r'<!-- YOUTUBE:([a-zA-Z0-9_-]+) -->',
                r'<YouTube id="\1" />',
                body_md
            )
            body_md = re.sub(
                r'<!-- VIMEO:(\d+) -->',
                r'<iframe src="https://player.vimeo.com/video/\1" width="640" height="360" frameborder="0" allowfullscreen></iframe>',
                body_md
            )
            
            # Convert LinkedIn embeds to local article links
            def replace_linkedin_embed(match):
                linkedin_id = match.group(1)
                if linkedin_id in linkedin_id_mapping:
                    local_slug = linkedin_id_mapping[linkedin_id]
                    return f'[Related Article: {local_slug}](/posts/{local_slug})'
                else:
                    return f'[LinkedIn Article: {linkedin_id}]'
            
            body_md = re.sub(
                r'<!-- LINKEDIN:(\d+) -->',
                replace_linkedin_embed,
                body_md
            )
            
            # Find banner image
            banner_path = pathlib.Path(blog_base_dir) / IMAGES_DIR / LINKEDIN_SUBDIR / slug / "banner.jpg"
            banner_png_path = pathlib.Path(blog_base_dir) / IMAGES_DIR / LINKEDIN_SUBDIR / slug / "banner.png"
            
            banner_fm = None
            if banner_path.exists():
                banner_fm = f"/images/{LINKEDIN_SUBDIR}/{slug}/banner.jpg"
            elif banner_png_path.exists():
                banner_fm = f"/images/{LINKEDIN_SUBDIR}/{slug}/banner.png"
            
            # ------ write .md file ---------------------------------------
            fm_lines = [
                "---",
                f'title: "{html.escape(title)}"',
                f"date: {date.isoformat()}",
                f"slug: {slug}",
                f'original_url: "{original_url}"',
            ]
            if art_id:
                fm_lines.append(f"linkedin_id: {art_id}")
            if banner_fm:
                fm_lines.append(f"banner: {banner_fm}")
            fm_lines.append("---")
            
            # Add component imports if needed
            imports = []
            if "<YouTube" in body_md:
                imports.append("import YouTube from '../../../components/YouTube.astro';")
            
            if imports:
                fm_lines.append("")
                fm_lines.extend(imports)
            
            fm_lines.append("")  # Empty line before content
            
            # Write to both output dir and blog content dir
            md_filename = f"{date.date()}-{slug}.md"
            
            # Output dir (for inspection)
            md_path = articles_dir / md_filename
            with md_path.open("w", encoding="utf-8") as fp:
                fp.write("\n".join(fm_lines))
                fp.write(body_md)
            
            # Blog content dir (for Astro)
            blog_md_path = linkedin_content_dir / f"{slug}.md"
            with blog_md_path.open("w", encoding="utf-8") as fp:
                fp.write("\n".join(fm_lines))
                fp.write(body_md)
            
            print(f"[+] {md_filename} → {blog_md_path.relative_to(pathlib.Path(blog_base_dir))}")
            article_count += 1
    
    print(f"\n[✓] Processed {article_count} unique articles")
    print(f"[✓] Markdown ready in {articles_dir}")
    print(f"[✓] Blog content updated in {linkedin_content_dir}")

# --------------------------------------------------------------------------- #
# 4. Main execution
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    import argparse, sys
    
    ap = argparse.ArgumentParser(description="Import and process LinkedIn articles for Astro blog")
    ap.add_argument("export_zip", help="LinkedIn data export ZIP file")
    ap.add_argument("--workdir", default="linkedin_work", help="Working directory for processing")
    ap.add_argument("--blog-dir", default=".", help="Blog root directory")
    args = ap.parse_args()
    
    if not os.path.exists(args.export_zip):
        print(f"Error: Export ZIP file not found: {args.export_zip}")
        sys.exit(1)
    
    workdir = pathlib.Path(args.workdir)
    workdir.mkdir(exist_ok=True)
    
    print(f"[START] Processing LinkedIn export: {args.export_zip}")
    print(f"[CONFIG] Working directory: {workdir}")
    print(f"[CONFIG] Blog directory: {args.blog_dir}")
    
    # Step 1: Extract articles only
    filtered_zip = workdir / "linkedin_articles_extract.zip"
    extract_articles_only(args.export_zip, filtered_zip)
    
    # Step 2: Process to markdown with all cleanup transformations
    linkedin_zip_to_markdown(filtered_zip, workdir, args.blog_dir)
    
    print(f"\n[✓] Import complete! Blog content has been replaced.")
    print(f"[INFO] Working files saved in: {workdir}")