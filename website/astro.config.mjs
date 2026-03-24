// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://currycan.github.io',
  base: '/study-all',
  output: 'static',
  vite: {
    plugins: [tailwindcss()],
  },
});
