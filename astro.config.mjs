import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://jmandel.github.io',
  base: '/blog',
  markdown: {
    shikiConfig: {
      theme: 'github-light',
      wrap: true
    }
  }
});