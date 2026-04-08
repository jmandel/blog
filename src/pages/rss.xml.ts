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

function toDate(raw: Date | string): Date {
  return raw instanceof Date ? raw : new Date(raw);
}

// `pubDate` uses the import date so feed readers treat a post as "new"
// when it lands in the blog. The canonical Dublin Core `dc:date`
// element carries the original LinkedIn authoring date, so readers
// that care can display or sort by it.
export const GET: APIRoute = async (context) => {
  const posts = await getCollection('blog');

  const sorted = posts
    .map((post) => ({
      post,
      pubDate: toDate(post.data.added_at ?? post.data.date),
      originalDate: toDate(post.data.date),
    }))
    .sort((a, b) => b.pubDate.getTime() - a.pubDate.getTime());

  return rss({
    title: 'Interop Blog',
    description:
      'Musings on healthcare IT, FHIR, EHR systems, and digital health innovation — by Josh Mandel, MD.',
    site: context.site!,
    xmlns: { dc: 'http://purl.org/dc/elements/1.1/' },
    items: sorted.map(({ post, pubDate, originalDate }) => ({
      title: post.data.title,
      pubDate,
      link: `/posts/${post.data.slug ?? post.slug}/`,
      description: excerpt(post.body ?? ''),
      customData: `<dc:date>${originalDate.toISOString()}</dc:date>`,
    })),
    customData: `<language>en-us</language>`,
    trailingSlash: false,
  });
};
