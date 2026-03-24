import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const lessons = defineCollection({
  loader: glob({ pattern: '*.md', base: '../content' }),
  schema: z.object({}).passthrough(),
});

export const collections = { lessons };
