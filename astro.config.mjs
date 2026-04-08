import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://jmandel.github.io',
  base: '/blog',

  // The dev toolbar runs idle-callback work on the main thread that can
  // visibly hitch canvas animations during local dev. Production is
  // unaffected either way.
  devToolbar: { enabled: false },

  markdown: {
    shikiConfig: {
      theme: 'github-light',
      wrap: true
    }
  }
});