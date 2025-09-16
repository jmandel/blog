# Interop Blog

A static blog built with [Astro](https://astro.build) featuring insights and analysis on healthcare interoperability, FHIR standards, EHR systems, and digital health innovation.

## Features

- **Static Site Generation** – Built with Astro for fast loading and great SEO.
- **Responsive Design** – Clean, professional layout that works on all devices.
- **Content Collections** – Markdown frontmatter drives post metadata and routing.
- **GitHub Pages Integration** – Automatic deployment on every push to `main`.
- **Healthcare Focus** – Specialized content covering policy, interoperability, and MCP/AI topics.

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm
- Python 3.9+ (required for the LinkedIn import tooling)

### Installation

```bash
git clone https://github.com/jmandel/blog.git
cd blog
npm install
```

### Local Development

Run the Astro dev server and open <http://localhost:4321/blog>:

```bash
npm run dev
```

### Building for Production

```bash
npm run build
```

For a full verification that includes banner normalization and the Astro build, run:

```bash
npm run test-build
```

The production-ready site is emitted into the `dist/` directory.

## Project Structure

```
├── public/              # Static assets copied as-is (includes banner images)
├── src/
│   ├── content/
│   │   └── blog/        # Markdown posts with frontmatter
│   ├── layouts/
│   ├── pages/
│   └── components/
├── scripts/             # LinkedIn import + banner tooling
├── LinkedIn exports/    # Optional storage for raw LinkedIn ZIP files (ignored)
└── .github/workflows/   # GitHub Pages deployment workflow
```

## Adding Content

Blog posts live in `src/content/blog/` as Markdown files with frontmatter:

```markdown
---
title: "Your Post Title"
date: 2025-01-01T00:00:00
slug: your-post-slug
banner: /images/linkedin/your-post-slug/banner.jpg
---

Post content here…
```

Banner images should point at local paths under `/images/linkedin/{slug}/` so the static site is self-contained.

## LinkedIn Import Workflow

Most content is generated from LinkedIn exports. The helper script will set everything up (including the `uv` environment) and validate the Astro build for you:

```bash
./scripts/local-import.sh "LinkedIn exports/2025-07-02-export.zip"
```

The script handles:

1. Creating/updating a `.venv-import` `uv` environment and syncing `scripts/requirements.txt`.
2. Running `scripts/linkedin_import.py` to rewrite `src/content/blog/linkedin/{slug}/index.md` and download banners into the same folder (`banner.png`).
3. Re-running `scripts/download_banner_images.py` to catch any lingering remote banners.
4. Installing Node dependencies (if needed) and executing `npm run test-build` to ensure Astro still builds.

Afterward, review the git diff, commit `src/content/`, and push. GitHub Actions will build and deploy the already-generated static site.

If you need to run each step manually (for debugging, custom dirs, etc.), see `scripts/README.md` for the explicit commands.

## Deployment

Deployments are handled by GitHub Actions (`.github/workflows/deploy.yml`). The workflow checks out the repository, installs Node dependencies, runs `npm run build`, and publishes the resulting `dist/` folder to GitHub Pages.

## Technologies Used

- [Astro](https://astro.build)
- [Markdown](https://www.markdownguide.org/)
- [GitHub Pages](https://pages.github.com/)
- [GitHub Actions](https://github.com/features/actions)

## License

ISC License – see `package.json` for details.
