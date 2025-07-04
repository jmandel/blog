# Healthcare Technology Blog

A static blog built with [Astro](https://astro.build) featuring insights and analysis on healthcare IT, FHIR standards, EHR systems, and digital health innovation.

## Features

- **Static Site Generation**: Built with Astro for fast loading and excellent SEO
- **Responsive Design**: Clean, professional layout that works on all devices
- **Content Collections**: Organized blog posts with frontmatter support
- **GitHub Pages Integration**: Automatic deployment on every commit
- **Healthcare Focus**: Specialized content covering:
  - Healthcare interoperability and FHIR standards
  - Electronic Health Record (EHR) systems and regulations
  - Prior authorization and clinical workflow optimization
  - AI and machine learning applications in healthcare
  - Digital health policy and CMS regulations
  - Model Context Protocol (MCP) and healthcare AI integration

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jmandel/blog.git
   cd blog
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:4321/blog](http://localhost:4321/blog) in your browser

### Building for Production

```bash
npm run build
```

The built site will be available in the `dist/` directory.

## Project Structure

```
├── public/              # Static assets
├── src/
│   ├── content/
│   │   └── blog/       # Blog posts (Markdown)
│   ├── layouts/        # Page layouts
│   ├── pages/          # Page components
│   └── components/     # Reusable components
├── .github/
│   └── workflows/      # GitHub Actions
└── astro.config.mjs    # Astro configuration
```

## Adding Content

Blog posts are stored in `src/content/blog/` as Markdown files with frontmatter:

```markdown
---
title: "Your Post Title"
date: 2025-01-01T00:00:00
slug: your-post-slug
banner: "https://example.com/image.jpg"
---

Your post content here...
```

## Deployment

The site automatically deploys to GitHub Pages when changes are pushed to the main branch. The deployment is handled by the GitHub Actions workflow in `.github/workflows/deploy.yml`.

## Technologies Used

- [Astro](https://astro.build) - Static site generator
- [Markdown](https://www.markdownguide.org/) - Content format
- [GitHub Pages](https://pages.github.com/) - Hosting
- [GitHub Actions](https://github.com/features/actions) - CI/CD

## License

ISC License - see the package.json file for details.