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

5. **Live fetch sidecar (optional).** A zip from `scripts/linkedin_live_fetch.ts` (see "LinkedIn live fetch" below) carries a `Live/` folder. When it is present, `scripts/linkedin_live_sidecar.py` supplies real cover and inline images, post media, the true intro post of each article, and "link in comments"; `scripts/linkedin_threads.py` merges the comment threads into `src/data/linkedin/`. A normal export has no `Live/` folder and imports exactly as before.

6. **`scripts/backfill_linkedin_banners.py`** — One-shot recovery script for articles missing banners. Walks `src/content/blog/linkedin/`, finds articles with no `banner.*` file, fetches the live LinkedIn URL, extracts `og:image` from the HTML, downloads the image, and saves it. Detects and skips bogus fallbacks (LinkedIn profile-pic 96x96 PNGs and SVG placeholders). Run with: `uv run --python .venv-import python scripts/backfill_linkedin_banners.py`

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

## Link conventions (blog vs LinkedIn)

Readers should always know whether a link keeps them on the blog or sends them to LinkedIn, and content should live on the blog whenever the blog has it.

- **Mark links that leave the site.** Every link that leaves the site gets a trailing ↗, added by one CSS rule in `src/styles/base.css` (`.main a[href^="http"]…::after`). Links within the blog get none, and image-only links (cards) are left unmarked. Don't add arrows by hand.
- **Name LinkedIn links consistently**, with "on LinkedIn" in the text:
  - "Original on LinkedIn": an article's header chip. LinkedIn may have newer edits.
  - "Original post on LinkedIn": a post page's header chip.
  - "Reply on LinkedIn": each conversation's header. Newer comments, and where to reply.
  - "original on LinkedIn": a quoted post.
  - "Watch the video on LinkedIn": video we can't host (see "Videos": a registered YouTube copy plays instead).
  - Commenters' names link to their LinkedIn profiles (the ↗ shows it).
- **Link out only where LinkedIn adds something** (newer edits, newer comments, replying, video). Otherwise keep the content on the blog. For example, the intro-post box on an article ("Introduced on LinkedIn") has no button, because its conversation is shown on the page.
- **One page per piece of content.** A post of Josh's that carries the card of an article the blog has is not given its own post page. The importer folds it into the article (`also_posted` in the article's frontmatter, written after articles are regenerated; shown as "Also posted on LinkedIn, <date>" under the intro post), and its comments already appear in the article's conversation column. Links to such a post go to the article.
- **Links to LinkedIn copies of things the blog has go to the blog's page.** `src/lib/linkmap.mjs` maps LinkedIn article URLs (`/pulse/...`, via each post's `original_url`/`supersedes_linkedin`; native posts win) and post URLs (`/feed/update/urn:li:activity|ugcPost|share:…`, via share pages, articles' `intro_share`, and the `same_as` relations from the live fetch) to blog URLs. It's applied in three places:
  - Markdown, through a rehype plugin registered in `astro.config.mjs`;
  - comment text, in `LinkedInThreads.astro`;
  - link cards and the "Linked article" note on post pages.
- **Clear the content cache locally.** Astro caches rendered Markdown, so after changing the plugin or the map, run `rm -rf node_modules/.astro .astro/data-store.json` before a local build. CI builds start clean.

## Videos: YouTube copies of LinkedIn videos

LinkedIn streams video in pieces, so the blog can't host or embed it. Where Josh's YouTube channel (https://www.youtube.com/channel/UCqV1UeP3YSFQeK3Nu_FGl2w) has the same video, the blog plays that instead. The decision is recorded, never guessed at build time.

**Registry: `src/data/youtube.json`** (tracked). Keyed by the LinkedIn post's activity URN (`urn:li:activity:…`), or `article:<linkedin_id>#<n>` for the n-th video inside an article. Each entry has:
- `youtube_id`: the copy to play, or `null` for "checked, no equivalent". A null entry keeps its `candidates` and isn't checked again unless you pass `--recheck`.
- `match`: `duration+title`, `manual` or `uploaded` (`none` when null), plus `checked_at`, an optional `note` and the LinkedIn `share_urn`, URL, duration and date.
- `related` (optional): other, non-equivalent videos, shown as labelled links (e.g. "Longer version on YouTube").

**Matcher: `scripts/youtube_match.py`.**
- It lists the channel with `yt-dlp --flat-playlist` (cached a day in `linkedin_work/youtube_channel.json`) and checks every LinkedIn video from the live fetch (`linkedin_work/live/Live/items`) that has no entry.
- A match needs the duration within ±2 s **and** at least half of the YouTube title's words in the post, and, when the upload date is known (fetched per candidate only, and cached), an upload within 60 days of the post.
- **Duration alone is not a match.** The channel's only 444 s video is an unrelated SMART Health Check-In demo, exactly the length of the gpt-live-1 voice demo.
- Confident matches are written; everything else is recorded as null with its candidates and printed for the user to decide.

```bash
.venv-import/bin/python scripts/youtube_match.py                       # check new videos
.venv-import/bin/python scripts/youtube_match.py --set <key> <id> --uploaded   # after Josh uploads a copy
.venv-import/bin/python scripts/youtube_match.py --set <key> <id> --note "why" # manual choice (e.g. a different cut)
.venv-import/bin/python scripts/youtube_match.py --related <key> <id> "Longer version on YouTube"
.venv-import/bin/python scripts/youtube_match.py --clear <key>               # check again next run
```

**Getting a copy to upload.** `node scripts/linkedin_live_fetch.ts --capture-video https://www.linkedin.com/feed/update/urn:li:activity:<id>/` loads the post once (paced, read-only), takes the highest-bitrate progressive MP4 named in the page's data (ffmpeg on the player's DASH/HLS manifest as a fallback) and writes `linkedin_work/video/<activity id>.mp4`. It checks the duration against the post's. The folder is gitignored; never commit videos. Josh uploads the file himself; then record it with `--set … --uploaded`. Don't upload anything to YouTube on his behalf.

**Rendering** (`src/lib/youtube.mjs`):
- **Post and article bodies:** the rehype plugin `rehypeYouTube`, registered before `rehypeLocalLinkedIn` in `astro.config.mjs`, finds the importer's video block (a poster, then "Watch the video on LinkedIn"). It looks the block up by the page's `share_id`, or by `linkedin_id` and position.
  - With a `youtube_id`, the block becomes a click-to-play embed: the LinkedIn poster links to YouTube, and a click swaps in the `youtube-nocookie.com` player, so nothing loads from YouTube until then. The caption reads "Watch on YouTube", plus "Original on LinkedIn" for articles (post pages already have the "Original post on LinkedIn" chip).
  - If the page already embeds the same video elsewhere (old imports turned YouTube links into players), that copy becomes a "video on YouTube" link.
  - With no entry, or a null one, the block is unchanged. Its LinkedIn links are marked (`data-linkedin-video`) so the link map leaves them pointing at LinkedIn; before this they were rewritten to the page itself.
- **Intro posts** of articles (`intro_share`) get the same treatment in `posts/[slug].astro`, with YouTube's thumbnail as the poster (the LinkedIn poster isn't kept for intro posts). When the entry is null, the box shows "Watch the video on LinkedIn".
- `related` videos render as labelled links (↗ from the CSS rule).

As of October 2026:
- **Matched (`duration+title`):** the two videos inside the Kill-the-Clipboard articles (`article:3tssc#1`, `article:9jpqc#1`). Both articles also link those YouTube videos themselves.
- **Manual:** the ACO post (`urn:li:activity:7492546574942629888`) plays `pyIkbTBgksg`, the longer 20:59 demo the user prefers over the 15:00 LinkedIn cut.
- **Waiting for an upload:** the gpt-live-1 voice demo (`urn:li:activity:7506820918892056576`). Its MP4 is in `linkedin_work/video/`.

## LinkedIn live fetch (browser)

`scripts/linkedin_live_fetch.ts` reads Josh's own articles and posts, and the comment threads on them, from LinkedIn through an already logged-in browser. It writes them as a LinkedIn export (`Articles/Articles/*.html`, `Shares.csv`, `Rich_Media.csv`) plus a `Live/` sidecar, zipped, so `./scripts/local-import.sh` takes it unchanged.

**When to use it.** For new articles and posts between exports, for everything the export gets wrong (cover and inline images, post images, video, "link in comments"), and for the comment threads, which the export doesn't have. **Keep requesting the official export (a "Complete" one, about quarterly)** as the full backup: it covers what the live fetch doesn't (posts older than the activity list reaches, drafts, everything else in the account). Import both; the import is idempotent and the newer data wins.

**Rules (LinkedIn's user agreement discourages automated access):**
- Read-only. The fetcher navigates, scrolls, and clicks only the expanders listed in `scripts/linkedin_live/selectors.ts` (`SEL.expanders`: load more comments, previous replies, comment sort, the Me menu, the image viewer, show more results). Every click is re-checked against `neverClickText`/`neverClickAria` (Like, Reply, Repost, Follow, …). Never add an expander that changes anything.
- Human pacing: 3–6.5 s plus jitter between page loads (`--min-delay`/`--max-delay`), gradual scrolling, 0.5–1.6 s around each click, one tab. At most `--max-pages` loads per run (default 150; `lnkd.in` lookups count too) and `--max-clicks` expanders per thread (default 80).
- If LinkedIn shows a login, checkpoint or captcha, the fetcher stops with exit code 3 and saves `Live/error-page.{html,png}`. **Stop and ask the user;** never try to get past it.
- It opens its own tab in the browser on CDP port 9333 (see "Browser setup" under the native-post sync section below) and closes it when done. It never prints cookies or headers.

### Commands

```bash
npm install                                  # puppeteer-core (dev dependency)
node scripts/linkedin_live_fetch.ts --probe  # health check: known pages, all extractors (~3 loads; output in linkedin_work/live-probe)
node scripts/linkedin_live_fetch.ts --only https://www.linkedin.com/pulse/<article>/ --only https://www.linkedin.com/feed/update/urn:li:activity:<id>/
node scripts/linkedin_live_fetch.ts --articles --posts --since 2026-09-01 --dry-run   # plan only (2 loads)
node scripts/linkedin_live_fetch.ts --articles --posts                                # everything new
./scripts/local-import.sh linkedin_work/live/linkedin-live.zip
```

Options: `--articles` / `--posts` (both when neither and no `--only`), `--since <date>` (posts; default: 3 days before the newest share in the blog), `--only <url>` (repeatable; an article also fetches the post that announced it), `--out <dir>` (default `linkedin_work/live`), `--max-pages N`, `--max-clicks N`, `--refetch` (ignore items already fetched in `--out`), `--build-only` (rebuild the zip and report from `--out`, no browser), `--profile <url>` (skip the Me menu), `--no-threads`, `--capture-video <post url>` (save the post's video as an MP4 for uploading to YouTube; see "Videos"), `--extract-file <saved.html>` (run every in-page extractor on a saved page, e.g. `Live/error-page.html`, in a tab with all network blocked: no LinkedIn load, for checking a selector fix).

Discovery: the profile URL comes from the Me menu (cached in `linkedin_work/live_state.json`). Articles come from `/in/<me>/recent-activity/articles/`, newest first, stopping after three in a row the blog already has (by `linkedin_id`, `original_url` or a native post's `supersedes_linkedin`). Posts come from `/recent-activity/all/`, scrolling until items are older than `--since`. Each original or quote post gets its own page load; reposts are recorded from the list card; a post whose thread was already captured with its article is recorded without a load.

**Resumable.** Every item is written to `Live/items/` as soon as it is fetched, and items already there are skipped, so a run stopped by the page budget (exit 4), an error or Ctrl-C continues where it left off when re-run with the same `--out`. `Live/log.jsonl` has one line per page load, thread, item and skipped expander.

### What the sidecar adds

`Live/manifest.json` (`schema: linkedin-live/1`): `articles`, `posts`, `relations`, `threads` (index), all keyed by LinkedIn URNs. Media files are in `Live/media/<sha256 prefix>.<ext>`, one copy per content hash; every reference records `file`, `sha256`, `source_url` and how it was fetched (`via`).

- **Articles:** title, subtitle, `created_at` (from the `urn:li:linkedInArticle` id, the export's "Created on"), `published_at`, the stored article HTML (the same `contentHtml` the export contains, else the rendered `.reader-article-content`), the cover image (largest copy, fetched through the page), every inline image at its largest stored size (`shrink_1500_2232`), captions and alt text, links with LinkedIn redirects unwrapped, embeds, reaction/comment/repost counts, `text_hash`, and `edited_at` (LinkedIn shows no edit date on articles; this is the first fetch that saw the text change).
- **Posts:** exact time (LinkedIn ids are time-ordered: `id >> 22` is milliseconds since 1970, so "2w" is never parsed), activity and share URNs, kind (original / quote / repost), "Edited" flag, text with links (`lnkd.in` resolved), @-mentions with profile URLs, hashtags, media (images at the viewer's larger size, video poster + duration + auto-captions `.vtt`, link previews with title and image, LinkedIn article cards, documents, polls), the quoted post (URN, author, text, images), counts, and Josh's first comment if it holds a link (`first_comment_link`).
- **Relations** (`from`, `rel`, `to`, `method`): `announces` (post → article, from the article page itself), `links_to` (post → article, from a card or a link), `quotes` / `reposts` (→ original, with `own`), `follows_up` (post → earlier post it links to), `first_comment_link` (post → URL or article), `superseded_by` (article → native post), `thread` and `same_as` (activity ↔ share URN).

What the importer does with it: real `banner.*` and `image-N.*` files (no Rich_Media.csv or og:image backfill needed), share pages with their images, article and link-preview cards (thumbnail and title, linking to this blog's copy of the article when there is one), video poster and link, documents, polls, the quoted post as a blockquote, `first_comment_link`, `quote_of`, `video_url` and `linkedin_edited` frontmatter, `subtitle` and `linkedin_edited_at` on articles, and the article's `intro_share` taken from the article page instead of the time-and-title heuristic (`[LIVE] Intro post … confirmed`, or a printed disagreement). When a live zip lacks an article's intro post, the earlier `intro_share` is kept. When it has the post but not the article (a `--posts` run lists the announcements of articles the blog already has), the post is never written as a standalone share if it is already some post's `intro_share`; otherwise the earliest post carrying that article's card becomes the `intro_share` of the blog's copy (imported or native, only if it has none), logged as `[LIVE] Intro post … → …`.

The fetcher also prints `CHANGED on LinkedIn since …` (text hash differs from the last fetch) and `BACKPORT? <article> → <native post>: N LinkedIn paragraph(s) not in the native post` (5-word-phrase comparison, captions excluded). It only reports; backport by hand as described in "Keeping a native post and its LinkedIn version in sync".

### Comment threads

**One thread, keyed by its URN.** Comments hang off a post (`urn:li:ugcPost:…`, `urn:li:share:…`, occasionally `urn:li:activity:…`). An article page shows the comments of the post that announced it: checked on the PFS, remote-monitoring, MyChart Takeout, 7,000-clicks and 10,000-pages articles, where the article page and the post list the same comment ids and the same counts. So each thread is stored once and listed for every page it belongs on. A later post about the article (a reshare, a follow-up with the article card) has its own URN and so its own thread. A comment belongs to exactly one thread.

Which post announced an article: a fetched post page whose comments are the article's thread is ground truth (`method` in the `announces` relation says so); otherwise the activity the article page names. Don't match by time alone: a scheduled post's activity can be a day younger than its ugcPost (the "Understanding ACO Quality Reporting" video post). In October 2026 this agreed with the importer's time-and-title heuristic on all 20 articles fetched.

**Capture** (`expandThread` in `scripts/linkedin_live/page.ts`): switch the sort to "Most recent" (recorded in `sort`), then repeatedly scroll to the end (lazy loading) and click "Load more comments", then "See previous replies" / "Load more replies", re-querying after every click until none is left, the click cap or the 4-minute thread budget is reached. A button whose label turned into "Collapse replies" is skipped (`SEL.expanderSkip`). "…more" in comments is not clicked: the full text is already in the DOM. Per thread it records `expanders_used`, `expanders_left` (with labels) and `stuck`.

**Stored** (tracked, published with the site):
- `src/data/linkedin/threads/<urn>.json`, one per thread:
  ```
  { schema: "linkedin-thread/1", thread_urn, url, pages: ["article:<linkedin_id>", "share:<share id>"],
    label: "article" | "post", subjects: [{kind, activity_urn, linkedin_id, url}],
    displayed: {comments, reactions, reposts}, captured: {total, top_level, replies}, complete, sort,
    first_fetched, last_fetched,
    comments: [{ id: "urn:li:comment:(ugcPost:…,…)", parent_id, created_at,
                 author: {name, headline, profile_url, is_self, is_post_author},
                 text, html, links: [{text, url}], mentions: [{name, url, kind}], hashtags,
                 media: [{type: image|gif|link_preview, file, url, alt, title}],
                 reactions, edited, first_seen, last_seen, deleted?, deleted_seen? }] }
  ```
  `html` is built by the fetcher from text, `<a href>` and `<br>` only.
- `public/linkedin-media/<sha>.<ext>`: images in comments.
- `src/data/linkedin/relations.json`: the relations above, merged by (from, rel, to).

**Incremental.** The importer (`scripts/linkedin_threads.py`) merges each snapshot by comment id: new comments get `first_seen`, all seen ones `last_seen`; a comment missing from a *complete* capture is kept with `deleted: true` (never dropped); a partial capture marks nothing deleted.

**Display** (`src/components/LinkedInThreads.astro`, on `posts/[slug]` and `shares/[slug]`): an article page shows the threads listing `article:<its linkedin_id>` (also through a native post's `linkedin_id`, `original_url` or `supersedes_linkedin`, so a superseding native post shows the article's conversation) and `share:<its intro share id>`; a share page shows `share:<share_id>`. Threads of later posts that link to an article appear on that article's page too, under "On a LinkedIn post from <date>"; the article's own thread comes first. Every comment and reply is shown (no "show more" collapsing). On screens 1,300 px and wider the conversation sits in its own scrolling column beside the article (`PostLayout`'s `aside` slot). Top-level comments in date order with replies nested, author linked to their profile, headline, date, "edited", reaction counts, images; Josh's comments get an "Author" badge and a tinted background. Deleted comments are hidden unless they have replies.

### Reading the report

Every run ends with `Live/report.json` and a summary: one line per item, `OK` / `WARN` / `FAIL`, with comments captured / displayed. Exit codes: 0 clean, 2 some item FAILed, 3 LinkedIn blocked (login/checkpoint), 4 page budget reached, 1 error.

- **FAIL** means the data is thin and must not be imported as is: article body under 300 characters or no title, a media download failed (the failure lists each source tried: page response, page fetch, direct, with the HTTP status), comments short by more than 20% or with an expander still visible, more than two comments missing author/time/text, a post with no share URN.
- **WARN**: no cover image, no `linkedInArticle` URN (created date falls back), unknown post components (a media type nobody wrote an extractor for), a comment showing more replies than captured, comments short with no expander left (LinkedIn's count includes deleted or hidden comments), an unresolved `lnkd.in` link.

### Runbook for the supervising agent

**Missing images after a build.** Astro collapses byte-identical image files, and an article's original-size banner once went missing from `dist/` because a post's link card held an identical copy. Card thumbnails are now resized and re-encoded (`save_thumb` in `linkedin_shares.py`, needs Pillow). After any import, check that every `<img src>` in `dist/**/*.html` exists on disk; it's a few lines of Python, and the build itself doesn't catch it.

**Empty post list.** If the activity page yields no cards at all, the fetcher stops with an error (exit 1) rather than reporting a clean run without posts. This happened once in October 2026: the page hadn't rendered its cards. A plain re-run fixed it.

1. **Probe** (`--probe`): loads the activity list (`probe:post-list`: at least 3 cards, URNs, authors, times; names the layout it saw), the remote-monitoring article and the PFS post, and recaptures both threads. All items must be OK and both threads complete. Run it before any larger run and after any fix (~4 loads).
2. **Small run**: `--only` two or three URLs, or `--posts --since <last week>`. Check the report and the zip (`unzip -l`), import into a scratch copy, `npm run build`, look at a page.
3. **Full run**: `--articles --posts`. Re-run until it ends without exit 4. Then import, build, and check `git diff`: new articles and shares, changed threads, no unexpected rewrites of existing posts.
4. **Never commit** until the report has no FAIL, the import ran, `npm run build` passes, and you have looked at the diff. Then commit only on the user's go-ahead.

Common failures and fixes. Every LinkedIn selector and text heuristic is in `scripts/linkedin_live/selectors.ts`, each a list tried in order; fix it there, then re-run `--probe` and compare counts with the previous `report.json`.
- **Selector drift** (FAIL with "selectors.ts: …", empty titles or bodies, all comments missing a field): open the page in the browser, find the new class or attribute, add it at the front of that list. The feed's nav uses generated class names, which is why the Me menu is found by its text. Save the page (`Live/error-page.html` is written on any error) and iterate with `--extract-file` instead of reloading LinkedIn.
- **New activity-list layout (seen October 2026).** `/recent-activity/all/` is sometimes served as a server-driven layout (A/B or rollout): no `data-urn`, no `feed-shared-update-v2`, generated class names, `[componentkey]` attributes, and `networkidle` never settles (the fetcher waits on `domcontentloaded` plus a delay). Symptom: `--posts` stops with "post list: no activity cards found". `activityCards()` now tries the classic cards, then `SEL.sdui`: cards are `[role=listitem][componentkey^="update-card-focus"]`; the post's URN is decoded from the `componentkey` of its `…-replaceableCommentTools…` element (base64 protobuf: field 1 = `urn:li:activity`, field 2 = `urn:li:ugcPost`, value = id×2), which is the comment-thread URN; the activity URN comes from the "View analytics" link on Josh's own posts; authors are `a[href*="/in/"] div[aria-label]`; text is `[data-testid="expandable-text-box"]`; links are wrapped in `/safety/go/?url=` (unwrapped); counts come from the Reaction/Comment/Repost buttons; images take the largest `srcset` entry. The page scrolls an inner container, not the window (the document is one screen tall), and older posts load with a "Load more" button: `scrollGradually` scrolls whichever element scrolls, and `SEL.expanders.showMoreResults` accepts "Show more results" or "Load more". A first fix that only parsed cards found 20 and stopped silently, so the run now WARNs (`post-list`) whenever the list ends before `--since`. On this layout a repost card shows the original post, not Josh's repost activity, so reposts are keyed `post-repost-<original id>` and their `reposts` relation names the original (`repost_of`); a repost already stored from the classic layout is de-duplicated at build. Post and article pages were unchanged. The report's `post-list` log line and the probe name the layout seen.
- **Thread short with an expander visible**: the label changed (`expanders_left_labels` in the thread file shows it); adjust `SEL.expanders.*.label` or `.sel`. Short with nothing visible and the gap small: usually deleted or hidden comments; a WARN is fine.
- **Lazy loading** (items or comments missing at the end): raise the scroll steps in `scrollGradually` calls; don't raise pacing speed.
- **Unknown post components** (WARN): a new media type; add an extractor in `page.ts` (`post()`) and its selectors.
- **Media download 403/failed**: signed URLs expire after a few weeks; re-fetch the item with `--refetch --only <url>`.
- **Login, checkpoint, captcha, or pages that load empty / "too many requests"**: stop, tell the user, wait. Don't retry in a loop, don't lower the delays.

### Limits

- Videos: LinkedIn streams them as DASH/HLS segments (a `blob:` URL), so there is no single file; the poster, duration, auto-captions and post URL are kept.
- Documents (PDF carousels) and polls have extractors written from LinkedIn's component names but no live example yet; the "unknown component" check flags anything else new.
- Post images come from LinkedIn's image viewer (the largest copy it serves); article images are LinkedIn's stored copies (at most 1,500 px tall), not the originals.
- Reposts are recorded from the activity card only. The classic card has Josh's repost activity but not the original's URN (the relation names the original's author); the server-driven card has the original's URN but not Josh's repost activity or its time, so `--since` filters those by the original's date.
- The activity list reaches back a few months at most; older posts need the official export.
- Comment authors' profile photos aren't stored.

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
1. **Get the live text.** (`scripts/linkedin_live_fetch.ts` lists candidates: its `BACKPORT?` lines name native posts with LinkedIn paragraphs they lack, and `Live/items/article-<id>.json` holds the live HTML and text.) Open the published article (`original_url`) and take `document.querySelector('.reader-article-content').innerHTML`. Figures are `<figure>` elements with an optional `<figcaption>`. LinkedIn wraps each list in an extra `<p>` holding the same text; skip that duplicate.
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
