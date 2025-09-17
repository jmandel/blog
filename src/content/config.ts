import { defineCollection, z } from 'astro:content';

const blogCollection = defineCollection({
  type: 'content',
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      date: z.union([z.date(), z.string()]),
      slug: z.string().optional(),
      banner: image().optional(),
      original_url: z.string().optional(),
      linkedin_id: z.string().optional(),
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
  schema: z.object({
    title: z.string(),
    date: z.union([z.date(), z.string()]),
    slug: z.string().optional(),
    share_url: z.string(),
    share_type: z.string(),
    share_id: z.string(),
    visibility: z.string().optional(),
    shared_url: z.string().optional(),
    media_url: z.string().optional(),
  }),
});

export const collections = {
  blog: blogCollection,
  shares: shareCollection,
};
