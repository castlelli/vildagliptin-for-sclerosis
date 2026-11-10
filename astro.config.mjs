// @ts-check
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://castlelli.github.io',
  base: '/vildagliptin-for-sclerosis',
  trailingSlash: 'always',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'pt'],
    routing: { prefixDefaultLocale: false },
  },
});
