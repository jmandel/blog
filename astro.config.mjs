import { defineConfig } from 'astro/config';
import { rehypeLocalLinkedIn } from './src/lib/linkmap.mjs';
import { rehypeYouTube } from './src/lib/youtube.mjs';

export default defineConfig({
  site: 'https://joshuamandel.com',
  base: '/blog',

  // The dev toolbar runs idle-callback work on the main thread that can
  // visibly hitch canvas animations during local dev. Production is
  // unaffected either way.
  devToolbar: { enabled: false },

  markdown: {
    // Links to LinkedIn articles the blog has point at the blog's copy.
    // LinkedIn videos with a YouTube copy in src/data/youtube.json play from
    // YouTube (runs first, and marks video links that must stay on LinkedIn).
    rehypePlugins: [rehypeYouTube, rehypeLocalLinkedIn],
    shikiConfig: {
      theme: 'github-light',
      wrap: true
    }
  }
});