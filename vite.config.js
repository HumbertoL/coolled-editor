import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  // .jt files are hand-written JSON with a non-standard extension; treat them
  // as static assets so `?url` glob imports resolve to a fetchable URL.
  assetsInclude: ['**/*.jt'],
  server: {
    // CRA honoured PORT; Vite does not, and tooling that assigns a free
    // port (.claude/launch.json) relies on it.
    port: Number(process.env.PORT) || 3000,
  },
  build: {
    // Firebase hosting serves `build/` (firebase.json), not Vite's `dist/`.
    outDir: 'build',
  },
  preview: {
    port: Number(process.env.PORT) || 4173,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/setupTests.js',
  },
});
