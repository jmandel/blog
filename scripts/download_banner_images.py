#!/usr/bin/env python3
"""
download_banner_images.py

Build-time script to download LinkedIn banner images and update markdown files
to reference local images instead of remote URLs.

This script:
1. Scans all blog post markdown files
2. Finds banner URLs that are remote LinkedIn URLs
3. Downloads them locally if not already downloaded
4. Updates the markdown files to reference the local images
"""

import os
import re
import requests
import pathlib
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Tuple, Optional

# Configuration
CONTENT_DIR = "src/content/blog"
IMAGES_DIR = "public/images"
LINKEDIN_SUBDIR = "linkedin"

def extract_frontmatter_banner(content: str) -> Optional[str]:
    """Extract banner URL from markdown frontmatter."""
    match = re.search(r'^banner:\s*(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def is_linkedin_banner_url(url: str) -> bool:
    """Check if URL is a LinkedIn banner image URL."""
    return url and 'media.licdn.com' in url and 'article-cover_image' in url

def get_local_banner_path(article_slug: str, extension: str = 'jpg') -> Tuple[str, str]:
    """
    Get the local path for a banner image.
    Returns (relative_path_for_markdown, absolute_path_for_filesystem)
    """
    # Path relative to the public directory (for use in markdown)
    relative_path = f"/blog/images/{LINKEDIN_SUBDIR}/{article_slug}/banner.{extension}"
    
    # Absolute path for filesystem operations
    absolute_path = f"{IMAGES_DIR}/{LINKEDIN_SUBDIR}/{article_slug}/banner.{extension}"
    
    return relative_path, absolute_path

def download_banner_image(url: str, local_path: str) -> bool:
    """Download a banner image from URL to local path."""
    try:
        print(f"Downloading banner image: {url[:60]}...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Downloaded to: {local_path}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to download {url}: {e}")
        return False

def determine_image_extension(url: str, content_type: str = None) -> str:
    """Determine the appropriate file extension for an image."""
    if content_type:
        if 'jpeg' in content_type or 'jpg' in content_type:
            return 'jpg'
        elif 'png' in content_type:
            return 'png'
        elif 'gif' in content_type:
            return 'gif'
    
    # Fallback to URL analysis or default
    if '.png' in url.lower():
        return 'png'
    elif '.gif' in url.lower():
        return 'gif'
    else:
        return 'jpg'  # Default

def update_markdown_banner(file_path: str, old_url: str, new_url: str) -> bool:
    """Update the banner URL in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the banner URL in frontmatter
        updated_content = re.sub(
            r'^banner:\s*' + re.escape(old_url) + r'$',
            f'banner: {new_url}',
            content,
            flags=re.MULTILINE
        )
        
        if updated_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"✓ Updated banner URL in: {file_path}")
            return True
        else:
            print(f"✗ No banner URL found to update in: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to update {file_path}: {e}")
        return False

def extract_slug_from_filename(filename: str) -> str:
    """Extract article slug from markdown filename."""
    return os.path.splitext(filename)[0]

def process_blog_posts() -> None:
    """Main function to process all blog posts and download banner images."""
    if not os.path.exists(CONTENT_DIR):
        print(f"Content directory not found: {CONTENT_DIR}")
        return
    
    processed_count = 0
    downloaded_count = 0
    updated_count = 0
    
    # Process all markdown files in the blog directory
    for filename in os.listdir(CONTENT_DIR):
        if not filename.endswith('.md'):
            continue
            
        file_path = os.path.join(CONTENT_DIR, filename)
        article_slug = extract_slug_from_filename(filename)
        
        print(f"\nProcessing: {filename}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"✗ Failed to read {file_path}: {e}")
            continue
        
        # Extract banner URL from frontmatter
        banner_url = extract_frontmatter_banner(content)
        if not banner_url:
            print(f"  No banner URL found")
            continue
        
        # Check if it's a LinkedIn banner URL that needs to be downloaded
        if not is_linkedin_banner_url(banner_url):
            print(f"  Banner URL is not a LinkedIn URL, skipping")
            continue
        
        processed_count += 1
        
        # Determine the local path for the banner image
        relative_path, absolute_path = get_local_banner_path(article_slug)
        
        # Check if image already exists locally
        if os.path.exists(absolute_path):
            print(f"  Banner image already exists locally: {absolute_path}")
            # Still update the markdown file to use the local path
            if update_markdown_banner(file_path, banner_url, relative_path):
                updated_count += 1
            continue
        
        # Try to download the image
        if download_banner_image(banner_url, absolute_path):
            downloaded_count += 1
            
            # Update the markdown file to reference the local image
            if update_markdown_banner(file_path, banner_url, relative_path):
                updated_count += 1
        else:
            print(f"  Keeping remote URL due to download failure")
    
    print(f"\n=== Summary ===")
    print(f"Blog posts processed: {processed_count}")
    print(f"Banner images downloaded: {downloaded_count}")
    print(f"Markdown files updated: {updated_count}")

if __name__ == "__main__":
    print("Downloading banner images for blog posts...")
    process_blog_posts()
    print("Done!")