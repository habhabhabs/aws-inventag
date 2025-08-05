# InvenTag Documentation Website

This directory contains the Docusaurus configuration for the InvenTag documentation website.

## Overview

The documentation website is built using Docusaurus and configured to read content from the root-level `docs/` directory. This creates a single source of truth where documentation files can be viewed both on GitHub and through the enhanced Docusaurus web interface.

## Configuration

- **docusaurus.config.js**: Main Docusaurus configuration file
- **sidebars.js**: Navigation and sidebar configuration
- **src/**: Custom components and pages
- **static/**: Static assets for the documentation site

## Key Features

- Reads documentation from `../docs` (root-level docs directory)
- Configured for GitHub Pages deployment
- Single source of truth - same files work on GitHub and Docusaurus
- Edit links point to GitHub repository
- Responsive design with search functionality

## Development

To run the documentation site locally:

```bash
cd website
npm start
```

To build for production:

```bash
cd website
npm run build
```

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when changes are pushed to the main branch.

## Maintenance

This setup is designed to be low-maintenance:
- Documentation content lives in the root `docs/` directory
- Navigation is auto-generated from the folder structure
- No content duplication between GitHub and Docusaurus
- Standard Docusaurus project structure for easy updates