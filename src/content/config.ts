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
    }),
});

export const collections = {
  blog: blogCollection,
};
