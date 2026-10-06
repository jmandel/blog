import { getCollection, type CollectionEntry } from 'astro:content';

type Post = CollectionEntry<'blog'>;

// Posts are LinkedIn imports (src/content/blog/linkedin/) or native posts
// written here (anywhere else under src/content/blog/). A native post
// supersedes the LinkedIn article it names in `supersedes_linkedin`, or
// whose slug matches its own; the importer then stops writing that
// article (scripts/native_posts.py). Filtering here too keeps the site
// right between writing a native post and the next import.
// Native posts with `draft: true` show in `astro dev` only.

const slugify = (s: string) =>
  s.toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '')
    .replace(/['’]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

function claimKey(value: string): string {
  const pulse = value.match(/linkedin\.com\/pulse\/([^/?#]+)/);
  if (pulse) return 'pulse:' + pulse[1].toLowerCase();
  if (/^[a-z0-9]{5}$/.test(value)) return 'id:' + value;
  return slugify(value);
}

const isLinkedIn = (post: Post) => post.id.startsWith('linkedin/');
export const postSlug = (post: Post) => post.data.slug ?? post.slug;

export async function getPosts(): Promise<Post[]> {
  const all = await getCollection('blog');
  // A draft only claims its LinkedIn copy where the draft itself is shown,
  // so a draft never leaves the blog with neither version.
  const shown = (p: Post) => !(p.data.draft && import.meta.env.PROD);
  const natives = all.filter((p) => !isLinkedIn(p) && shown(p));
  const claimed = new Set<string>();
  for (const p of natives) {
    claimed.add(postSlug(p));
    claimed.add(slugify(p.data.title));
    const claims = p.data.supersedes_linkedin;
    for (const c of Array.isArray(claims) ? claims : claims ? [claims] : []) claimed.add(claimKey(c));
  }
  const superseded = (p: Post) =>
    claimed.has(postSlug(p)) ||
    (p.data.original_url && claimed.has(claimKey(p.data.original_url))) ||
    (p.data.linkedin_id && claimed.has('id:' + p.data.linkedin_id));
  return all.filter((p) => (isLinkedIn(p) ? !superseded(p) : shown(p)));
}
