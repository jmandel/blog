// LinkedIn videos that play from YouTube instead. The decision lives in
// src/data/youtube.json (written by scripts/youtube_match.py), keyed by the
// LinkedIn post's activity URN, or article:<linkedin_id>#<n> for the n-th
// video in an article. Nothing is guessed here: no entry, no change.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const REGISTRY = join(process.cwd(), 'src/data/youtube.json');
let cache;

export function registry() {
  if (cache) return cache;
  try {
    cache = JSON.parse(readFileSync(REGISTRY, 'utf8')).videos || {};
  } catch {
    cache = {};
  }
  return cache;
}

const idOf = (urn) => ((urn || '').match(/(\d{15,})/) || [])[1];

/** The registry entry for a post, by its share id (ugcPost/share) or activity URN. */
export function entryForPost(shareOrActivity) {
  const id = idOf(shareOrActivity) || shareOrActivity;
  if (!id) return null;
  for (const [key, e] of Object.entries(registry())) {
    if (idOf(key) === id || idOf(e.share_urn) === id) return { key, ...e };
  }
  return null;
}

export const watchUrl = (id) => `https://www.youtube.com/watch?v=${id}`;
export const embedUrl = (id) => `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`;

const el = (tagName, properties = {}, children = []) => ({ type: 'element', tagName, properties, children });
const text = (value) => ({ type: 'text', value });
const textOf = (n) => (n.type === 'text' ? n.value : (n.children || []).map(textOf).join(''));
const firstEl = (n, tag) => {
  if (n.type === 'element' && n.tagName === tag) return n;
  for (const c of n.children || []) {
    const f = firstEl(c, tag);
    if (f) return f;
  }
  return null;
};

// Click-to-play: the poster is a link to YouTube; with JS, a click swaps in
// the youtube-nocookie player, so nothing loads from YouTube until then.
const SCRIPT = `document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[data-yt]');if(!a)return;e.preventDefault();var f=document.createElement('iframe');f.src='https://www.youtube-nocookie.com/embed/'+a.dataset.yt+'?autoplay=1&rel=0';f.title=a.getAttribute('aria-label')||'YouTube video';f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';f.allowFullscreen=true;f.className='yt-embed__frame';a.replaceWith(f);});`;

/** The embed for a registry entry, around a poster (an <img> hast node). */
export function embedNode(entry, poster, originalUrl, originalLabel) {
  const id = entry.youtube_id;
  const facade = el('a', { className: ['yt-embed__facade'], href: watchUrl(id), dataYt: id, ariaLabel: `Play video${entry.title ? `: ${entry.title}` : ''}` }, [
    poster || el('img', { src: `https://i.ytimg.com/vi/${id}/hqdefault.jpg`, alt: '', loading: 'lazy' }),
    el('span', { className: ['yt-embed__play'], ariaHidden: 'true' }),
  ]);
  const caption = [el('a', { href: watchUrl(id), dataLinkedinVideo: 'true' }, [text('Watch on YouTube')])];
  if (originalUrl) caption.push(text(' · '), el('a', { href: originalUrl, dataLinkedinVideo: 'true' }, [text(originalLabel)]));
  return el('figure', { className: ['yt-embed'] }, [facade, el('figcaption', {}, caption)]);
}

export function relatedNodes(entry) {
  return (entry.related || []).map((r) =>
    el('p', { className: ['yt-related'] }, [el('a', { href: watchUrl(r.youtube_id), dataLinkedinVideo: 'true' }, [text(r.label || 'Related video on YouTube')])]));
}

export const scriptNode = () => el('script', {}, [text(SCRIPT)]);

/**
 * Rehype plugin. Finds the importer's video blocks (a poster paragraph, then
 * a "Watch the video on LinkedIn" paragraph) and, when the registry has a
 * YouTube copy, replaces them with the embed. Either way the LinkedIn links
 * are marked so rehypeLocalLinkedIn leaves them pointing at LinkedIn.
 */
export function rehypeYouTube() {
  return (tree, file) => {
    const fm = file?.data?.astro?.frontmatter || {};
    let n = 0;
    let embedded = false;
    const embeddedIds = new Set();
    const visit = (parent) => {
      const kids = parent.children || [];
      for (let i = 0; i < kids.length; i++) {
        const node = kids[i];
        const link = node.type === 'element' && node.tagName === 'p' && firstEl(node, 'a');
        if (!link || !/^Watch the video on LinkedIn/.test(textOf(link).trim())) {
          if (node.children) visit(node);
          continue;
        }
        n++;
        // The poster paragraph just before it (skipping whitespace).
        let j = i - 1;
        while (j >= 0 && kids[j].type === 'text' && !kids[j].value.trim()) j--;
        const posterPara = j >= 0 && kids[j].type === 'element' && firstEl(kids[j], 'img') ? kids[j] : null;
        // An article's video link names the article itself, which the
        // importer already rewrote to this page; point it back at LinkedIn.
        if (!/^https?:\/\//.test(link.properties.href) && fm.original_url) link.properties.href = fm.original_url;
        const linkedinUrl = link.properties.href;
        link.properties.dataLinkedinVideo = 'true';
        const posterLink = posterPara && firstEl(posterPara, 'a');
        if (posterLink) {
          posterLink.properties.dataLinkedinVideo = 'true';
          if (!/^https?:\/\//.test(posterLink.properties.href) && fm.original_url) posterLink.properties.href = fm.original_url;
        }
        const entry = fm.share_id ? entryForPost(fm.share_id) : fm.linkedin_id ? registry()[`article:${fm.linkedin_id}#${n}`] : null;
        if (!entry) continue;
        const repl = [];
        if (entry.youtube_id) {
          const poster = posterPara ? firstEl(posterPara, 'img') : null;
          const label = fm.share_id ? 'Original post on LinkedIn' : 'Original on LinkedIn';
          repl.push(embedNode(entry, poster, fm.share_id ? null : linkedinUrl, label));
          embedded = true;
          embeddedIds.add(entry.youtube_id);
        } else {
          if (posterPara) repl.push(posterPara);
          repl.push(node);
        }
        repl.push(...relatedNodes(entry));
        const start = posterPara ? j : i;
        kids.splice(start, i - start + 1, ...repl);
        i = start + repl.length - 1;
      }
    };
    visit(tree);
    // The same video embedded again elsewhere on the page (old imports turn
    // YouTube links into players): keep one player, make the other a link.
    if (embeddedIds.size) {
      const ytId = (src) => ((src || '').match(/youtube(?:-nocookie)?\.com\/embed\/([\w-]{11})/) || [])[1];
      // These sit mid-sentence ("In the <video>, I …"), where the old import
      // swapped a link for a player.
      const link = (id) => el('a', { href: watchUrl(id), dataLinkedinVideo: 'true' }, [text('video on YouTube')]);
      const dedupe = (parent) => {
        const kids = parent.children || [];
        for (let i = 0; i < kids.length; i++) {
          const k = kids[i];
          if (k.type === 'raw' && /youtube\.com\/embed\//.test(k.value)) {
            // Inline HTML arrives as one raw node per tag; the stray
            // </iframe> left behind is ignored by browsers.
            k.value = k.value.replace(/<iframe[^>]*youtube(?:-nocookie)?\.com\/embed\/([\w-]{11})[^>]*>(?:<\/iframe>)?/g,
              (m, id) => (embeddedIds.has(id) ? `<a href="${watchUrl(id)}">video on YouTube</a>` : m));
            continue;
          }
          if (k.type !== 'element') continue;
          const frame = k.tagName === 'iframe' ? k : (k.tagName === 'div' && (k.properties?.className || []).includes('youtube-embed') ? firstEl(k, 'iframe') : null);
          const id = frame && ytId(frame.properties?.src);
          if (id && embeddedIds.has(id)) { kids[i] = link(id); continue; }
          dedupe(k);
        }
      };
      dedupe(tree);
    }
    if (embedded) tree.children.push(scriptNode());
  };
}
