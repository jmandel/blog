// Every LinkedIn selector, label and heuristic the live fetcher relies on.
//
// When LinkedIn changes its markup, this is the one file to edit. Each entry
// is a list tried in order (first match wins), so add a new selector at the
// front and keep the old one as a fallback until it is clearly dead.
// `node scripts/linkedin_live_fetch.ts --probe` checks every extractor
// against known pages and names the entry that missed.
//
// Mapped October 2026 (Chromium 150, logged-in desktop layout).

export const SEL = {
  // --- session / safety ---------------------------------------------------
  // URL fragments that mean "not logged in" or "LinkedIn wants a human".
  // The fetcher stops (exit 3) on any of these and never tries to get past.
  blockedUrl: [/\/checkpoint\//, /\/authwall/, /\/login/, /\/uas\//, /\/signup/],
  blockedDom: ['#captcha-internal', 'form.login__form', '#challenge', 'iframe[src*="challenge"]'],
  blockedTitle: [/security verification/i, /sign in/i, /let'?s do a quick security check/i],
  // The "Me" menu in the global nav; its dropdown holds "View profile".
  // The feed's nav uses generated class names (October 2026), so the button
  // is found by its text ("Me") and the link as a /in/ link that appears
  // when the menu opens (preferring one labelled "View profile").
  meMenuProfileLink: ['a[href*="/in/"]'],

  // --- activity lists (/in/<me>/recent-activity/{articles,all}/) ----------
  articleListLink: ['li.profile-creator-shared-article__container a[href*="/pulse/"]', 'main a[href*="/pulse/"]'],
  activityCard: ['div.feed-shared-update-v2[data-urn^="urn:li:activity:"]', '[data-urn^="urn:li:activity:"]'],
  showMoreResults: ['button.scaffold-finite-scroll__load-button'],

  // --- activity list, server-driven layout ("SDUI", seen October 2026) -----
  // The profile activity list is sometimes served as a new layout with
  // generated class names and no data-urn. Stable hooks: role, componentkey,
  // aria-label, data-testid, hrefs. Post/article pages still use the
  // layout below. activityCards() tries the classic card first.
  sdui: {
    card: ['[role="listitem"][componentkey^="update-card-focus"]'],
    // componentkey "<base64 protobuf>-replaceableCommentTools<cardkey>":
    // field 1 = urn:li:activity (posts whose comments hang off the activity),
    // field 2 = urn:li:ugcPost; value = id*2 (zigzag varint). Either way it is
    // the post's comment-thread URN. For a repost it names the original.
    commentToolsKey: ['[componentkey*="-replaceableCommentTools"]'],
    activityLink: ['a[href*="/analytics/post-summary/urn:li:activity:"]', 'a[href*="/feed/update/urn:li:activity:"]'],
    quotedLink: ['a[href*="/feed/update/urn:li:"]'],
    // One selector (document order): first match is the post's author,
    // second the quoted post's. Links to the activity list aren't authors.
    actorBlock: [':is(a[href*="/in/"], a[href*="/company/"], a[href*="/school/"]):not([href*="recent-activity"]) div[aria-label]'], // non-empty ones only
    text: ['[data-testid="expandable-text-box"]'],
    articleCard: ['a[href*="/pulse/"]'],
    linkCard: ['a[href*="/safety/go/"]'],
    image: ['figure img'],
    video: ['video'],
    videoProgress: ['[role="slider"][aria-label="Progress Bar"]'],
    reactions: ['button[aria-label^="Reaction button state"]'],
    comments: ['button[aria-label="Comment"]'],
    reposts: ['button[aria-label="Repost"]'],
  },

  // --- a feed post (activity card, or the single post on /feed/update/) ---
  repostHeader: ['.update-components-header__text-view'], // "Josh Mandel, MD reposted this"
  actorLink: ['a.update-components-actor__meta-link'],
  actorName: ['.update-components-actor__title .hoverable-link-text', '.update-components-actor__title span[aria-hidden="true"]'],
  actorHeadline: ['.update-components-actor__description'],
  actorTime: ['.update-components-actor__sub-description'], // "1mo • Edited •"
  postText: ['.update-components-update-v2__commentary', '.feed-shared-update-v2__description .update-components-text'],
  quotedWrapper: ['.feed-shared-update-v2__update-content-wrapper'],
  quotedLink: ['a.update-components-mini-update-v2__link-to-details-page'],
  images: ['.update-components-image__image'],
  imageOpenButton: ['button.update-components-image__image-link'],
  lightboxImage: ['.artdeco-modal img.ivm-view-attr__img--centered', '[role="dialog"] img[src*="feedshare"]'],
  lightboxClose: ['.artdeco-modal button[aria-label="Dismiss"]', '[role="dialog"] button[aria-label*="Dismiss"]'],
  video: ['.update-components-linkedin-video video', 'video'],
  externalArticle: ['.update-components-article'], // link preview card
  externalArticleLink: ['a.update-components-article__meta', '.update-components-article__link-container a', 'a'],
  externalArticleTitle: ['.update-components-article__title'],
  externalArticleSubtitle: ['.update-components-article__subtitle', '.update-components-article__subtitle--inset'],
  firstPartyArticle: ['.update-components-article-first-party'], // card for a LinkedIn article
  // Not seen on Josh's recent posts in October 2026; written from LinkedIn's
  // usual component names and checked only by the "unknown component" scan.
  document: ['.update-components-document__container', '.document-s-container', '.update-components-document'],
  documentIframe: ['iframe[src*="document"]', 'iframe'],
  poll: ['.update-components-poll', '.feed-shared-poll'],
  pollOption: ['.update-components-poll-option', '.feed-shared-poll-option', 'li'],
  celebration: ['.update-components-celebration'],
  socialCounts: ['.social-details-social-counts'],
  reactionsCount: ['.social-details-social-counts__reactions-count', '.social-details-social-counts__social-proof-fallback-number'],
  commentsCount: ['.social-details-social-counts__comments button', 'button[aria-label*="comment"]'],
  repostsCount: ['button[aria-label*="repost"]'],

  // --- article page (/pulse/...) ------------------------------------------
  articleTitle: ['h1.reader-article-header__title', 'article h1', 'h1'],
  articleSubtitle: ['.reader-article-header__subtitle', 'h2.reader-article-header__subtitle'],
  articleCover: ['article header figure img', 'img[src*="article-cover_image"]'],
  articleDate: ['.reader-author-info__container time', 'article time'],
  articleBody: ['.reader-article-content', 'article .reader-content-blocks-container'],

  // --- comments -------------------------------------------------------------
  comment: ['article.comments-comment-entity'],
  commentIsReply: 'comments-comment-entity--reply', // class on reply <article>
  commentAuthorLink: ['a.comments-comment-meta__description-container', 'a.comments-comment-meta__image-link'],
  commentAuthorName: ['.comments-comment-meta__description-title'],
  commentAuthorHeadline: ['.comments-comment-meta__description-subtitle'],
  commentAuthorBadge: ['.comments-comment-meta__badge', '.comments-comment-meta__data'], // "Author", "• 1st"
  commentTime: ['time.comments-comment-meta__data', 'time'],
  commentText: ['.comments-comment-item__main-content', '.comments-comment-entity__content .update-components-text'],
  commentContent: ['.comments-comment-entity__content'],
  commentReactions: ['.comments-comment-social-bar__reactions-count--cr', 'button[class*="comments-comment-social-bar__reactions-count"]'],
  commentReplyCount: ['.comments-comment-social-bar__replies-count--cr', '[class*="comments-comment-social-bar__replies-count"]'],

  // --- the only things the fetcher ever clicks ------------------------------
  // Each must match both the selector and the label pattern (visible text
  // or aria-label), and must not match `neverClickText`/`neverClickAria`.
  expanders: {
    loadMoreComments: { sel: ['button.comments-comments-list__load-more-comments-button--cr', 'button[class*="load-more-comments-button"]'], label: /load more comments|show more comments|more comments/i },
    previousReplies: { sel: ['button.comments-replies-list__replies-button', 'button[class*="replies-list__replies-button"]'], label: /previous replies|more replies|load more|see \d+ more|view \d+ more/i },
    showReplies: { sel: ['button.comments-comment-social-bar__replies-count--cr', 'button[class*="replies-count"]'], label: /\d+\s+repl/i },
    seeMoreText: { sel: ['button.feed-shared-inline-show-more-text__see-more-less-toggle'], label: /more/i },
    sortTrigger: { sel: ['button.comments-sort-order-toggle__trigger'], label: /sort order|most relevant|most recent/i },
    sortMostRecent: { sel: ['.comments-sort-order-toggle .artdeco-dropdown__item', '.comments-sort-order-toggle [role="button"]', '.comments-sort-order-toggle li'], label: /most recent/i },
    meMenu: { sel: ['header button', 'nav button', 'button.global-nav__primary-link-me-menu-trigger'], label: /^me$/i },
    imageLightbox: { sel: ['button.update-components-image__image-link'], label: /.*/ },
    lightboxClose: { sel: ['.artdeco-modal button[aria-label="Dismiss"]'], label: /dismiss/i },
    // Classic list: "Show more results"; server-driven list: "Load more".
    showMoreResults: { sel: ['button.scaffold-finite-scroll__load-button', 'main button', 'button'], label: /^(show more results|load more)$/i },
  },
  // An expander whose label matches this does the opposite (e.g. "See
  // previous replies" turns into "Collapse replies" once clicked): skip it.
  expanderSkip: /collapse|hide|show less|fewer/i,
  // Never click anything whose visible text or aria-label matches these,
  // whatever selector found it (belt and braces against a selector that
  // drifts onto a Like or Reply button).
  neverClickText: /^(like|celebrate|support|love|insightful|funny|reply|comment|repost|send|share|follow|following|connect|message|save|post|delete|edit|report|hide|mute|block|subscribe|accept|ignore|unfollow)$/i,
  neverClickAria: /^(react|like|reply to|repost|send|follow|connect|save|delete|edit|report|hide|unfollow|open control menu|open reactions)/i,
};

// Text heuristics.
export const TEXT = {
  repostHeader: /reposted this/i,
  editedMarker: /\bEdited\b/,
  commentsCount: /([\d,.]+)\s*comments?/i,
  repostsCount: /([\d,.]+)\s*reposts?/i,
  repliesCount: /([\d,.]+)\s*repl/i,
  relativeTime: /^(\d+)\s*(s|m|h|d|w|mo|yr|y)\b/,
  authorBadge: /\bAuthor\b/,
};

// LinkedIn ids (activity, ugcPost, share, comment, linkedInArticle) are
// time-ordered: the top 41 bits are milliseconds since the Unix epoch.
// That gives exact UTC times for posts and comments without parsing "2w".
export function idTime(id: string | bigint): Date | null {
  try {
    const n = BigInt(id);
    const ms = Number(n >> 22n);
    if (ms < 1.1e12 || ms > 4.2e12) return null; // 2004..2103
    return new Date(ms);
  } catch {
    return null;
  }
}
