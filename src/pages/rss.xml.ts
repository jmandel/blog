import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIRoute } from 'astro';

// Strip Markdown/HTML down to a plain-text excerpt for the RSS description.
function excerpt(body: string, maxChars = 320): string {
  return body
    .replace(/<[^>]+>/g, ' ')        // strip HTML tags
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '') // strip markdown images
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1') // flatten markdown links to text
    .replace(/[#>*_`~]/g, '')        // strip markdown punctuation
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maxChars)
    .trimEnd() + '…';
}

// Prefer the import date (when the post landed in the blog) so new
// subscribers see a post when it was actually published here, not on
// its original LinkedIn authoring date.
function pubDateFor(post: { data: { added_at?: Date | string; date: Date | string } }): Date {
  const raw = post.data.added_at ?? post.data.date;
  return raw instanceof Date ? raw : new Date(raw);
}

export const GET: APIRoute = async (context) => {
  const posts = await getCollection('blog');

  const sorted = posts
    .map((post) => ({ post, pubDate: pubDateFor(post) }))
    .sort((a, b) => b.pubDate.getTime() - a.pubDate.getTime());

  return rss({
    title: 'Interop Blog',
    description:
      'Musings on healthcare IT, FHIR, EHR systems, and digital health innovation — by Josh Mandel, MD.',
    site: context.site!,
    items: sorted.map(({ post, pubDate }) => ({
      title: post.data.title,
      pubDate,
      link: `/posts/${post.data.slug ?? post.slug}/`,
      description: excerpt(post.body ?? ''),
    })),
    customData: `<language>en-us</language>`,
    trailingSlash: false,
  });
};
