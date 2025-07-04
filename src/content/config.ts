import { z, defineCollection } from 'astro:content';

const blogCollection = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.union([z.date(), z.string()]),
    slug: z.string().optional(),
    banner: z.string().optional(),
  }),
});

export const collections = {
  'blog': blogCollection,
};