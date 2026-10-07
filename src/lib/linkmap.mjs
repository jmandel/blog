// Map LinkedIn article URLs to this blog's copies, so links that would send
// a reader to LinkedIn for content the blog already has stay on the blog.
// Read straight from the content files (frontmatter original_url,
// supersedes_linkedin and slug) so both the Markdown plugin in
// astro.config.mjs and components can use it.
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

// Relative to the repo root (builds run there); a path relative to this file
// breaks once Astro bundles it into dist/chunks.
const ROOT = join(process.cwd(), 'src/content/blog');
let cache;

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (name === 'index.md' || name === 'index.mdx') out.push(p);
  }
  return out;
}

const pulseBase = (url) => (url.match(/linkedin\.com\/pulse\/([^/?#"'\s]+)/i) || [])[1]?.toLowerCase().replace(/\/$/, '');

export function linkMap() {
  if (cache) return cache;
  cache = new Map();
  const native = [];
  for (const file of walk(ROOT)) {
    const fm = (readFileSync(file, 'utf8').match(/^---\n([\s\S]*?)\n---/) || [])[1] || '';
    const slug = ((fm.match(/^slug:[ \t]*(.+)$/m) || [])[1] || file.split('/').slice(-2)[0]).trim().replace(/^"|"$/g, '');
    const isNative = !file.includes('/blog/linkedin/');
    for (const m of fm.matchAll(/linkedin\.com\/pulse\/[^"'\s]+/gi)) {
      const b = pulseBase(m[0]);
      if (!b) continue;
      if (isNative) native.push([b, slug]);
      else if (!cache.has(b)) cache.set(b, slug);
    }
  }
  // A native post that supersedes an article wins over the imported copy.
  for (const [b, slug] of native) cache.set(b, slug);
  return cache;
}

// LinkedIn posts the blog has a page for: share id → page, plus activity
// ids mapped to their share through the live fetch's same_as relations.
const SHARES = join(process.cwd(), 'src/content/shares');
const RELATIONS = join(process.cwd(), 'src/data/linkedin/relations.json');
let postCache;
function postMap() {
  if (postCache) return postCache;
  postCache = new Map();
  let files = [];
  try { files = walk(SHARES); } catch {}
  for (const file of files) {
    const fm = (readFileSync(file, 'utf8').match(/^---\n([\s\S]*?)\n---/) || [])[1] || '';
    const id = (fm.match(/^share_id:[ \t]*"?(\d+)/m) || [])[1];
    const slug = ((fm.match(/^slug:[ \t]*(.+)$/m) || [])[1] || file.split('/').slice(-2)[0]).trim().replace(/^"|"$/g, '');
    if (id) postCache.set(id, `shares/${slug}`);
  }
  // A post that introduced an article lives on the article's page.
  for (const file of walk(ROOT)) {
    const fm = (readFileSync(file, 'utf8').match(/^---\n([\s\S]*?)\n---/) || [])[1] || '';
    const id = (fm.match(/^intro_share:\n(?:[ \t]+.*\n)*?[ \t]+share_id:[ \t]*"?(\d+)/m) || [])[1];
    const slug = ((fm.match(/^slug:[ \t]*(.+)$/m) || [])[1] || file.split('/').slice(-2)[0]).trim().replace(/^"|"$/g, '');
    if (id && !postCache.has(id)) postCache.set(id, `posts/${slug}`);
    for (const m of fm.matchAll(/^\s+share_id:[ \t]*"?(\d+)/gm)) if (!postCache.has(m[1])) postCache.set(m[1], `posts/${slug}`);
  }
  try {
    for (const r of JSON.parse(readFileSync(RELATIONS, 'utf8'))) {
      if (r.rel !== 'same_as') continue;
      const a = (r.from.match(/(\d{15,})/) || [])[1], b = (r.to.match(/(\d{15,})/) || [])[1];
      if (a && b && postCache.has(b) && !postCache.has(a)) postCache.set(a, postCache.get(b));
    }
  } catch {}
  return postCache;
}

/** This blog's URL for a LinkedIn article or post URL, or null. */
export function localUrlFor(url, base = '/blog') {
  if (!url) return null;
  const b = pulseBase(url);
  const slug = b && linkMap().get(b);
  if (slug) return `${base}/posts/${slug}`;
  const id = (url.match(/linkedin\.com\/(?:feed\/update|posts)\/[^?#]*?(?:activity|ugcPost|share)[:%3A]+(\d{15,})/i) || [])[1];
  const share = id && postMap().get(id);
  return share ? `${base}/${share}` : null;
}

/** Rehype plugin: rewrite links to LinkedIn articles the blog has. */
export function rehypeLocalLinkedIn() {
  return (tree) => {
    const visit = (node) => {
      // Video links stay on LinkedIn (or YouTube): the blog page can't play them.
      if (node.type === 'element' && node.tagName === 'a' && typeof node.properties?.href === 'string' && !node.properties.dataLinkedinVideo) {
        const local = localUrlFor(node.properties.href);
        if (local) node.properties.href = local;
      }
      (node.children || []).forEach(visit);
    };
    visit(tree);
  };
}
