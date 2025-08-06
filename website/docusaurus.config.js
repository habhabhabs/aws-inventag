// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'InvenTag Documentation',
  tagline: 'Professional AWS Cloud Governance Platform',
  favicon: 'img/favicon.svg',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://habhabhabs.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/inventag-aws/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'habhabhabs', // Usually your GitHub org/user name.
  projectName: 'inventag-aws', // Usually your repo name.
  deploymentBranch: 'gh-pages', // Branch for GitHub Pages deployment
  trailingSlash: false, // GitHub Pages compatibility

  onBrokenLinks: 'warn', // Allow broken links during migration phase
  onBrokenMarkdownLinks: 'warn', // Allow some flexibility for markdown links during migration

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          path: '../docs', // Single source of truth - read from root-level docs directory
          routeBasePath: '/', // Serve docs at the root path
          sidebarPath: './sidebars.js',
          // Edit links point to GitHub repository for dual-platform compatibility
          editUrl: 'https://github.com/habhabhabs/inventag-aws/edit/main/docs/',
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
          // Enhanced GitHub integration
          editCurrentVersion: true,
          // Breadcrumbs for better navigation
          breadcrumbs: true,
          // Include frontmatter for better GitHub compatibility
          include: ['**/*.md', '**/*.mdx'],
          exclude: [
            '**/_*.{js,jsx,ts,tsx,md,mdx}',
            '**/_*/**',
            '**/*.test.{js,jsx,ts,tsx}',
            '**/__tests__/**',
            // Temporarily exclude problematic files during migration
            '**/template-system-summary.md',
            '**/complete-readme-backup.md',
          ],
        },
        blog: false, // Disable blog functionality for this documentation site
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  // Plugins will be configured in later tasks for search functionality

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Enhanced metadata for better SEO and social sharing
      metadata: [
        {name: 'keywords', content: 'aws, cloud-governance, inventory, tagging, compliance, documentation'},
        {name: 'description', content: 'Professional AWS Cloud Governance Platform - Comprehensive documentation for InvenTag'},
      ],
      // Social card for better sharing
      image: 'img/inventag-social-card.svg',
      navbar: {
        title: 'InvenTag',
        logo: {
          alt: 'InvenTag Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Documentation',
          },
          {
            type: 'search',
            position: 'right',
          },
          {
            href: 'https://github.com/habhabhabs/inventag-aws',
            className: 'header-github-link',
            'aria-label': 'GitHub repository',
            position: 'right',
          },
        ],
        hideOnScroll: true,
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Getting Started',
                to: '/',
              },
              {
                label: 'User Guides',
                to: '/user-guides/CLI_USER_GUIDE',
              },
              {
                label: 'Architecture',
                to: '/architecture/CORE_MODULE_INTEGRATION',
              },
              {
                label: 'Development',
                to: '/development/CONTRIBUTING',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Repository',
                href: 'https://github.com/habhabhabs/inventag-aws',
              },
              {
                label: 'Issues & Bug Reports',
                href: 'https://github.com/habhabhabs/inventag-aws/issues',
              },
              {
                label: 'Discussions',
                href: 'https://github.com/habhabhabs/inventag-aws/discussions',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'Configuration Examples',
                to: '/user-guides/CONFIGURATION_EXAMPLES',
              },
              {
                label: 'Contributing Guide',
                to: '/development/CONTRIBUTING',
              },
              {
                label: 'License',
                href: 'https://github.com/habhabhabs/inventag-aws/blob/main/LICENSE',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} InvenTag Team. Built with Docusaurus. | <a href="https://github.com/habhabhabs/inventag-aws/edit/main/docs/" target="_blank" rel="noopener noreferrer">Edit on GitHub</a>`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        // Enhanced syntax highlighting for AWS and cloud technologies
        additionalLanguages: [
          'bash',
          'json',
          'yaml',
          'python',
          'javascript',
          'typescript',
          'powershell',
          'ini',
          'toml',
          'sql',
          'graphql',
          'markdown',
          'diff'
        ],
        // Custom syntax highlighting for AWS CLI and cloud commands
        magicComments: [
          {
            className: 'theme-code-block-highlighted-line',
            line: 'highlight-next-line',
            block: {start: 'highlight-start', end: 'highlight-end'},
          },
          {
            className: 'code-block-aws-command',
            line: 'aws-command',
          },
          {
            className: 'code-block-inventag-command',
            line: 'inventag-command',
          },
        ],
      },
      // Enhanced color mode configuration
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      // Table of contents configuration for better navigation
      tableOfContents: {
        minHeadingLevel: 2,
        maxHeadingLevel: 4,
      },
      // Docs configuration for better GitHub compatibility
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: true,
        },
      },
    }),
};

export default config;
