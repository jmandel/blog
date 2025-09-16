# Contributing

Thanks for helping keep the blog up to date! This project publishes static content generated from LinkedIn exports. Follow the workflow below to ensure consistent outputs.

## Local Import Workflow

1. Place the latest LinkedIn export ZIP somewhere on your machine (it can live inside the `LinkedIn exports/` folder, but ZIPs are ignored by git).
2. From the repo root run:
   ```bash
   ./scripts/local-import.sh path/to/linkedin-export.zip
   ```
   This imports content, normalizes banner images, and runs a test Astro build.
3. Review the changes:
   ```bash
   git status
   git diff
   ```
4. Commit and push:
   ```bash
   git add src/content
   git commit -m "Import LinkedIn export from YYYY-MM-DD"
   git push origin main
   ```
   GitHub Actions will build and deploy the already-generated static site.

## Development Tips

- Use `npm run dev` to preview the site locally once content has been imported.
- Re-run `python3 scripts/download_banner_images.py` any time you edit frontmatter manually; it keeps banner paths consistent.
- Large working directories such as `linkedin_work/` and archives under `LinkedIn exports/` are git-ignored on purpose—do not commit them.
- Dependencies for the Python tooling live in `scripts/requirements.txt`; install them with `pip3 install -r scripts/requirements.txt` when working on the importer.

## Pull Requests

When submitting a PR, mention which LinkedIn export was used (timestamp or filename) and confirm `npm run test-build` passes locally. This helps reviewers reproduce the same deterministic output.
