import { defineConfig } from 'astro/config';

import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: 'https://jmandel.github.io',
  base: '/blog',

  markdown: {
    shikiConfig: {
      theme: 'github-light',
      wrap: true
    }
  },

  vite: {
    plugins: [tailwindcss()]
  }
});