import { defineCollection, z } from 'astro:content';

const blogCollection = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      date: z.union([z.date(), z.string()]),
      // When the post first landed in this blog (as opposed to `date`,
      // which is when it was originally authored on LinkedIn). Used as
      // the RSS pubDate so subscribers see a post when it's imported,
      // even if its authoring date is months old.
      added_at: z.union([z.date(), z.string()]).optional(),
      slug: z.string().optional(),
      banner: image().optional(),
      original_url: z.string().optional(),
      linkedin_id: z.string().optional(),
      // Native posts only (see src/lib/posts.ts): the LinkedIn article(s)
      // this post replaces, as a LinkedIn URL, linkedin_id, imported slug
      // or title; and whether to hide the post from production builds.
      supersedes_linkedin: z.union([z.string(), z.array(z.string())]).optional(),
      draft: z.boolean().optional(),
      // From a live fetch (scripts/linkedin_live_fetch.ts): the article's
      // subtitle, and the first fetch that saw its text change on LinkedIn.
      subtitle: z.string().optional(),
      linkedin_edited_at: z.union([z.date(), z.string()]).optional(),
      // Later posts of Josh's that carried this article's card; shown on the
      // article page instead of as separate post pages.
      also_posted: z
        .array(
          z.object({
            share_url: z.string(),
            share_id: z.string().optional(),
            posted_at: z.union([z.date(), z.string()]),
            commentary: z.string().optional(),
          }),
        )
        .optional(),
      intro_share: z
        .object({
          share_url: z.string(),
          share_id: z.string().optional(),
          share_type: z.string().optional(),
          posted_at: z.union([z.date(), z.string()]),
          visibility: z.string().optional(),
          shared_url: z.string().optional(),
          commentary: z.string().optional(),
        })
        .optional(),
    }),
});

const shareCollection = defineCollection({
  type: 'content',
  schema: ({ image }) => z.object({
    title: z.string(),
    date: z.union([z.date(), z.string()]),
    slug: z.string().optional(),
    share_url: z.string(),
    share_type: z.string(),
    share_id: z.string(),
    visibility: z.string().optional(),
    shared_url: z.string().optional(),
    media_url: z.string().optional(),
    // From a live fetch: Josh's "link in comments", the post it quotes,
    // a video's LinkedIn URL, and whether LinkedIn marks it edited.
    first_comment_link: z.string().optional(),
    quote_of: z.string().optional(),
    video_url: z.string().optional(),
    linkedin_edited: z.boolean().optional(),
    // First image, video poster or link card, for the home page.
    thumbnail: image().optional(),
  }),
});

export const collections = {
  blog: blogCollection,
  shares: shareCollection,
};
