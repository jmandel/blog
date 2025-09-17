#!/usr/bin/env python3
"""Orchestrate LinkedIn article + share imports into the Astro blog."""

from __future__ import annotations

import argparse
import pathlib
import sys
import zipfile
from typing import Iterable

from linkedin_articles import LinkedInArticleProcessor
from linkedin_shares import LinkedInShareProcessor

FILTERED_ARCHIVE_NAME = "linkedin_articles_extract.zip"


def extract_articles_only(src_zip: pathlib.Path, dst_zip: pathlib.Path) -> None:
    """Write a new ZIP that contains only article HTML and Rich_Media.csv."""
    with zipfile.ZipFile(src_zip, "r") as zin, zipfile.ZipFile(
        dst_zip, "w", compression=zipfile.ZIP_DEFLATED
    ) as zout:
        for info in zin.infolist():
            path_obj = pathlib.PurePosixPath(info.filename)
            is_article_html = (
                path_obj.suffix.lower() == ".html"
                and any(part.lower() == "articles" for part in path_obj.parts)
            )
            is_rich_media = path_obj.name == "Rich_Media.csv"
            if is_article_html or is_rich_media:
                zout.writestr(info, zin.read(info.filename))
    print(f"[ZIP] Wrote filtered archive ⇒ {dst_zip}")


def run_import(export_zip: pathlib.Path, workdir: pathlib.Path, blog_dir: pathlib.Path) -> None:
    workdir.mkdir(parents=True, exist_ok=True)

    filtered_zip = workdir / FILTERED_ARCHIVE_NAME
    extract_articles_only(export_zip, filtered_zip)

    article_processor = LinkedInArticleProcessor(str(filtered_zip), workdir, blog_dir)
    articles = article_processor.collect_articles()

    share_processor = LinkedInShareProcessor(str(export_zip), workdir, blog_dir)
    shares = share_processor.collect_shares()
    intro_map = share_processor.process_shares(shares, articles)

    article_processor.process_articles(articles, intro_map)

    print("\n[✓] Import complete. Blog content refreshed with articles and shares.")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import LinkedIn articles and shares")
    parser.add_argument("export_zip", help="Path to a LinkedIn data export ZIP file")
    parser.add_argument(
        "--workdir", default="linkedin_work", help="Working directory for temporary artifacts"
    )
    parser.add_argument("--blog-dir", default=".", help="Astro blog root directory")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    export_zip = pathlib.Path(args.export_zip).expanduser()
    if not export_zip.exists():
        print(f"Error: export ZIP not found: {export_zip}")
        return 1

    workdir = pathlib.Path(args.workdir).expanduser()
    blog_dir = pathlib.Path(args.blog_dir).expanduser()

    print(f"[START] Processing LinkedIn export: {export_zip}")
    print(f"[CONFIG] Working directory: {workdir}")
    print(f"[CONFIG] Blog directory: {blog_dir}")

    run_import(export_zip, workdir, blog_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
