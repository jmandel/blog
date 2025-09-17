#!/usr/bin/env python3
"""Article processing helpers for the LinkedIn import pipeline."""

from __future__ import annotations

import csv
import os
import pathlib
import re
import shutil
import subprocess
import urllib.parse
import zipfile
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Match

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from slugify import slugify

CONTENT_DIR = "src/content/blog"
LINKEDIN_SUBDIR = "linkedin"

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})?")
ID_RE = re.compile(r"-([a-z0-9]{5})$")


@dataclass
class ArticleData:
    """Structured data for a LinkedIn article."""

    filename: str
    basename: str
    title: str
    slug: str
    created_at: datetime
    published_at: Optional[datetime]
    linkedin_id: str
    original_url: str
    html: str


@dataclass
class IntroShareMeta:
    share_url: str
    share_id: Optional[str]
    share_type: Optional[str]
    posted_at: datetime
    visibility: Optional[str]
    shared_url: Optional[str]
    commentary: Optional[str]


class LinkedInArticleProcessor:
    """Process LinkedIn article exports into local markdown content."""

    def __init__(self, export_zip: str, workdir: pathlib.Path, blog_dir: pathlib.Path) -> None:
        self.export_zip = export_zip
        self.workdir = workdir
        self.blog_dir = blog_dir

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def collect_articles(self) -> List[ArticleData]:
        articles: List[ArticleData] = []
        with zipfile.ZipFile(self.export_zip) as zf:
            for info in zf.infolist():
                if not info.filename.lower().endswith(".html"):
                    continue
                path_obj = pathlib.PurePosixPath(info.filename)
                if not any(part.lower() == "articles" for part in path_obj.parts):
                    continue

                raw_html = zf.read(info.filename).decode("utf-8", "ignore")
                soup = BeautifulSoup(raw_html, "html.parser")
                title_tag = soup.find("h1")
                if not title_tag:
                    print(f"[WARN] Skipping article without <h1>: {info.filename}")
                    continue

                title = title_tag.get_text(strip=True)
                if not title:
                    print(f"[WARN] Skipping article with empty title: {info.filename}")
                    continue

                slug = slugify(title, lowercase=True)
                if not slug:
                    print(f"[WARN] Could not slugify title '{title}', skipping")
                    continue

                created_at = self._parse_timestamp(soup.find("p", class_="created"), fallback_filename=info.filename)
                published_at = self._parse_timestamp(soup.find("p", class_="published"))

                basename = os.path.basename(info.filename)[:-5]
                linkedin_id_match = ID_RE.search(basename)
                linkedin_id = linkedin_id_match.group(1) if linkedin_id_match else ""

                original_url = f"https://www.linkedin.com/pulse/{basename}"

                articles.append(
                    ArticleData(
                        filename=info.filename,
                        basename=basename,
                        title=title,
                        slug=slug,
                        created_at=created_at,
                        published_at=published_at,
                        linkedin_id=linkedin_id,
                        original_url=original_url,
                        html=raw_html,
                    )
                )
        return articles

    def process_articles(
        self,
        articles: Iterable[ArticleData],
        intro_share_map: Dict[str, IntroShareMeta],
    ) -> None:
        articles = list(articles)
        slug_mapping = {article.slug: article.basename for article in articles}
        linkedin_id_mapping = {
            article.linkedin_id: article.slug for article in articles if article.linkedin_id
        }

        work_articles_dir = self.workdir / "articles"
        if work_articles_dir.exists():
            shutil.rmtree(work_articles_dir)
        work_articles_dir.mkdir(parents=True, exist_ok=True)

        blog_linkedin_dir = self.blog_dir / CONTENT_DIR / LINKEDIN_SUBDIR
        if blog_linkedin_dir.exists():
            print(f"[CLEAN] Removing existing LinkedIn content from {blog_linkedin_dir}")
            shutil.rmtree(blog_linkedin_dir)
        blog_linkedin_dir.mkdir(parents=True, exist_ok=True)

        rich_media_rows = self._load_rich_media()
        cover_photos = self._parse_rich_media_csv(rich_media_rows)

        article_count = 0
        for article in articles:
            soup = BeautifulSoup(article.html, "html.parser")
            self._cleanup_linkedin_links(soup, slug_mapping)
            self._cleanup_redirect_wrappers(soup)
            self._cleanup_tracking_params(soup)
            self._convert_video_embeds(soup)
            self._strip_metadata_paragraphs(soup)
            image_info = self._download_and_localize_images(
                soup,
                article.slug,
                blog_linkedin_dir / article.slug,
                article.published_at or article.created_at,
                cover_photos,
            )
            self._cleanup_css_and_classes(soup)

            article_content = soup.find("article") or soup.body
            if article_content:
                body_md = md(str(article_content), strip=["script", "style"])
            else:
                body_md = md(str(soup), strip=["script", "style"])

            body_md = re.sub(
                r'<!-- YOUTUBE:([a-zA-Z0-9_-]+) -->',
                r'<div class="youtube-embed"><iframe width="560" height="315" src="https://www.youtube.com/embed/\1" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>',
                body_md,
            )
            body_md = re.sub(
                r'<!-- VIMEO:(\d+) -->',
                r'<iframe src="https://player.vimeo.com/video/\1" width="640" height="360" frameborder="0" allowfullscreen></iframe>',
                body_md,
            )

            def replace_linkedin_embed(match: Match[str]) -> str:
                linkedin_id = match.group(1)
                if linkedin_id in linkedin_id_mapping:
                    local_slug = linkedin_id_mapping[linkedin_id]
                    return f'[Related Article: {local_slug}](/blog/posts/{local_slug})'
                return f'[LinkedIn Article: {linkedin_id}]'

            body_md = re.sub(
                r'<!-- LINKEDIN:(\d+) -->',
                replace_linkedin_embed,
                body_md,
            )

            body_md = re.sub(
                r'^\[.*?\]\(/blog/posts/[^)]+\)\n=+\n',
                '',
                body_md,
                flags=re.MULTILINE,
            )

            banner_fm: Optional[str] = None
            if image_info.get("banner_filename"):
                banner_fm = f"./{image_info['banner_filename']}"
            elif image_info.get("banner_url"):
                banner_fm = image_info["banner_url"]
            else:
                for candidate in ("banner.jpg", "banner.png", "banner.gif"):
                    candidate_path = blog_linkedin_dir / article.slug / candidate
                    if candidate_path.exists():
                        banner_fm = f"./{candidate}"
                        break

            safe_title = article.title.replace('"', '\\"')
            fm_lines = [
                "---",
                f'title: "{safe_title}"',
                f"date: {article.created_at.isoformat()}",
                f"slug: {article.slug}",
                f'original_url: "{article.original_url}"',
            ]
            if article.linkedin_id:
                fm_lines.append(f"linkedin_id: {article.linkedin_id}")
            if banner_fm:
                fm_lines.append(f"banner: {banner_fm}")

            intro = intro_share_map.get(article.slug)
            if intro:
                fm_lines.append("intro_share:")
                fm_lines.append(f'  share_url: "{intro.share_url}"')
                if intro.share_id:
                    fm_lines.append(f'  share_id: "{intro.share_id}"')
                if intro.share_type:
                    fm_lines.append(f'  share_type: "{intro.share_type}"')
                fm_lines.append(f'  posted_at: "{intro.posted_at.isoformat()}"')
                if intro.visibility:
                    fm_lines.append(f'  visibility: "{intro.visibility}"')
                if intro.shared_url:
                    fm_lines.append(f'  shared_url: "{intro.shared_url}"')
                if intro.commentary:
                    fm_lines.append("  commentary: |")
                    for line in intro.commentary.splitlines() or [""]:
                        fm_lines.append(f"    {line}")

            fm_lines.append("---")
            fm_lines.append("")

            work_md_path = work_articles_dir / f"{article.created_at.date()}-{article.slug}.md"
            with work_md_path.open("w", encoding="utf-8") as out:
                out.write("\n".join(fm_lines))
                out.write(body_md)

            blog_article_dir = blog_linkedin_dir / article.slug
            blog_article_dir.mkdir(parents=True, exist_ok=True)
            blog_md_path = blog_article_dir / "index.md"
            with blog_md_path.open("w", encoding="utf-8") as out:
                out.write("\n".join(fm_lines))
                out.write(body_md)

            article_count += 1
            print(f"[ARTICLE] {article.slug} → {blog_md_path.relative_to(self.blog_dir)}")

        print(f"\n[✓] Processed {article_count} articles")
        print(f"[✓] Markdown ready in {work_articles_dir}")
        print(f"[✓] Blog content updated in {blog_linkedin_dir}")

        banner_script = pathlib.Path(__file__).resolve().parent / "download_banner_images.py"
        if banner_script.exists():
            print(f"[BANNER] Running {banner_script.name} to normalize banners...")
            subprocess.run(
                ["python3", str(banner_script)],
                check=True,
                cwd=self.blog_dir,
            )
        else:
            print("[BANNER] Skipping banner normalization (script not found)")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _parse_timestamp(self, tag: Optional[BeautifulSoup], fallback_filename: Optional[str] = None) -> datetime:
        if tag:
            match = DATE_RE.search(tag.get_text())
            if match:
                try:
                    return datetime.fromisoformat(match.group(0))
                except ValueError:
                    pass
        if fallback_filename:
            match = DATE_RE.search(fallback_filename)
            if match:
                try:
                    return datetime.fromisoformat(match.group(1))
                except ValueError:
                    pass
        return datetime.now()

    def _load_rich_media(self) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        with zipfile.ZipFile(self.export_zip) as zf:
            if "Rich_Media.csv" in zf.namelist():
                with zf.open("Rich_Media.csv") as fh:
                    reader = csv.DictReader((line.decode("utf-8", "ignore") for line in fh))
                    rows.extend(reader)
        return rows

    def _parse_rich_media_csv(self, rich_media_data: List[Dict[str, str]]) -> Dict[str, str]:
        cover_photos: Dict[str, str] = {}
        for row in rich_media_data:
            description = row.get("Date/Time", "")
            media_link = row.get("Media Link", "")
            if "article cover photo" in description and media_link:
                time_match = re.search(r'on ([A-Za-z]+ \d+, \d+) at (\d+:\d+) (AM|PM)', description)
                if not time_match:
                    continue
                date_str, time_str, ampm = time_match.groups()
                try:
                    full_time_str = f"{date_str} {time_str} {ampm}"
                    dt_obj = datetime.strptime(full_time_str, "%B %d, %Y %I:%M %p")
                    cover_photos[dt_obj.strftime("%Y-%m-%d %H:%M")] = media_link
                    print(f"[CSV] Found cover photo for {dt_obj}: {media_link[:60]}...")
                except Exception:
                    print(f"[WARN] Failed to parse timestamp from: {description}")
        return cover_photos

    def _cleanup_linkedin_links(self, soup: BeautifulSoup, slug_mapping: Dict[str, str]) -> None:
        for link in soup.find_all("a", href=True):
            href = link["href"]
            linkedin_match = re.search(r'linkedin\.com/pulse/([^/?]+)', href)
            if not linkedin_match:
                continue
            linkedin_slug = linkedin_match.group(1)
            for local_slug, linkedin_ref in slug_mapping.items():
                if linkedin_ref in linkedin_slug or linkedin_slug in linkedin_ref:
                    link["href"] = f"/blog/posts/{local_slug}"
                    print(f"[LINK] Rewrote LinkedIn link to local: {href} → /blog/posts/{local_slug}")
                    break

    def _cleanup_redirect_wrappers(self, soup: BeautifulSoup) -> None:
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "linkedin.com/redir/general-malware-page?url=" not in href:
                continue
            try:
                parsed = urllib.parse.urlparse(href)
                params = urllib.parse.parse_qs(parsed.query)
                if "url" in params:
                    real_url = urllib.parse.unquote(params["url"][0])
                    link["href"] = real_url
                    print(f"[REDIR] Unwrapped redirect: {real_url}")
            except Exception as exc:
                print(f"[WARN] Failed to unwrap redirect {href}: {exc}")

    def _cleanup_tracking_params(self, soup: BeautifulSoup) -> None:
        tracking_params = {'trk', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'}
        for link in soup.find_all("a", href=True):
            href = link["href"]
            try:
                parsed = urllib.parse.urlparse(href)
                if not parsed.query:
                    continue
                params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
                clean_params = {k: v for k, v in params.items() if k not in tracking_params}
                new_query = urllib.parse.urlencode(clean_params, doseq=True)
                clean_url = urllib.parse.urlunparse(
                    (parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)
                )
                if clean_url != href:
                    link["href"] = clean_url
                    print(f"[TRACK] Removed tracking params: {href} → {clean_url}")
            except Exception as exc:
                print(f"[WARN] Failed to clean tracking params from {href}: {exc}")

    def _convert_video_embeds(self, soup: BeautifulSoup) -> None:
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src", "")
            if not src:
                continue
            youtube_match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', src)
            if youtube_match:
                iframe.replace_with(soup.new_string(f"<!-- YOUTUBE:{youtube_match.group(1)} -->"))
                print(f"[VIDEO] Converted YouTube embed: {youtube_match.group(1)}")
                continue
            vimeo_match = re.search(r'vimeo\.com/video/(\d+)', src)
            if vimeo_match:
                iframe.replace_with(soup.new_string(f"<!-- VIMEO:{vimeo_match.group(1)} -->"))
                print(f"[VIDEO] Converted Vimeo embed: {vimeo_match.group(1)}")
                continue
            if "linkedin.com/embeds/publishingEmbed.html" in src:
                article_match = re.search(r'articleId=(\d+)', src)
                if article_match:
                    iframe.replace_with(soup.new_string(f"<!-- LINKEDIN:{article_match.group(1)} -->"))
                    print(f"[EMBED] Converted LinkedIn embed: {article_match.group(1)}")
        for a_tag in soup.find_all("a"):
            href = a_tag.get("href", "")
            youtube_match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)', href)
            if youtube_match:
                a_tag.replace_with(soup.new_string(f"<!-- YOUTUBE:{youtube_match.group(1)} -->"))
                print(f"[VIDEO] Converted YouTube link to embed: {youtube_match.group(1)}")

    def _download_and_localize_images(
        self,
        soup: BeautifulSoup,
        article_slug: str,
        content_dir: pathlib.Path,
        article_datetime: datetime,
        cover_photos: Dict[str, str],
    ) -> Dict[str, Optional[str]]:
        content_dir.mkdir(parents=True, exist_ok=True)
        result: Dict[str, Optional[str]] = {"banner_url": None, "banner_filename": None}
        img_counter = 0

        banner_downloaded = False
        banner_found = False
        article_time_key = article_datetime.strftime("%Y-%m-%d %H:%M")
        if article_time_key in cover_photos:
            banner_found = True
            banner_downloaded = self._try_download_banner(cover_photos[article_time_key], content_dir, result)

        if not banner_found:
            best_match = None
            best_diff = float("inf")
            for time_key, banner_url in cover_photos.items():
                try:
                    csv_dt = datetime.strptime(time_key, "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                diff = abs((article_datetime - csv_dt).total_seconds())
                if diff <= 7200 and diff < best_diff:
                    best_diff = diff
                    best_match = banner_url
            if best_match:
                banner_found = True
                banner_downloaded = self._try_download_banner(best_match, content_dir, result)

        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-delayed-url")
            if not src or not src.startswith("http"):
                continue
            if "media.licdn.com" not in src:
                continue
            if "/media" in src and "/dms/image/" not in src:
                img.decompose()
                continue

            img_counter += 1
            is_banner = img_counter == 1 and not banner_found
            try:
                response = requests.get(src, timeout=30)
                response.raise_for_status()
            except Exception as exc:
                print(f"[WARN] Failed to download image {src}: {exc}")
                if is_banner and not result.get("banner_url"):
                    result["banner_url"] = src
                img.decompose()
                continue

            content_type = response.headers.get("content-type", "")
            if "jpeg" in content_type or "jpg" in content_type:
                ext = ".jpg"
            elif "png" in content_type:
                ext = ".png"
            elif "gif" in content_type:
                ext = ".gif"
            else:
                ext = ".jpg"

            filename = "banner" + ext if is_banner else f"image-{img_counter}{ext}"
            with open(content_dir / filename, "wb") as fh:
                fh.write(response.content)
            img["src"] = f"./{filename}"
            for attr in ["data-delayed-url", "data-ghost-img"]:
                img.attrs.pop(attr, None)

            if is_banner:
                result["banner_filename"] = filename
            print(f"[IMAGE] Downloaded and localized: {filename}")

        return result

    def _try_download_banner(self, url: str, content_dir: pathlib.Path, result: Dict[str, Optional[str]]) -> bool:
        result["banner_url"] = url
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except Exception as exc:
            print(f"[WARN] Failed to download banner from CSV {url}: {exc}")
            return False

        content_type = response.headers.get("content-type", "")
        if "jpeg" in content_type or "jpg" in content_type:
            ext = ".jpg"
        elif "png" in content_type:
            ext = ".png"
        elif "gif" in content_type:
            ext = ".gif"
        else:
            ext = ".jpg"

        filename = "banner" + ext
        with open(content_dir / filename, "wb") as fh:
            fh.write(response.content)
        result["banner_filename"] = filename
        print(f"[CSV] Successfully downloaded banner: {filename}")
        return True

    def _cleanup_css_and_classes(self, soup: BeautifulSoup) -> None:
        linkedin_classes = ['share-article', 'article-wrap', 'core-rail', 'feed-shared-inline-video']
        for element in soup.find_all(class_=True):
            original_classes = element.get('class', [])
            clean_classes = [cls for cls in original_classes if not any(lc in cls for lc in linkedin_classes)]
            if clean_classes != original_classes:
                if clean_classes:
                    element['class'] = clean_classes
                else:
                    del element['class']
        for element in soup.find_all(style=True):
            style = element['style']
            if any(prop in style.lower() for prop in ['linkedin', 'feed-', 'share-']):
                del element['style']
            elif 'display:none' in style or 'visibility:hidden' in style:
                element.decompose()

    def _strip_metadata_paragraphs(self, soup: BeautifulSoup) -> None:
        for tag in list(soup.find_all("p")):
            text = (tag.get_text() or "").strip()
            cls = " ".join(tag.get("class", []))
            if not text:
                continue
            if text.startswith("Created on") or text.startswith("Published on"):
                tag.decompose()
                continue
            if "created" in cls or "published" in cls:
                tag.decompose()
