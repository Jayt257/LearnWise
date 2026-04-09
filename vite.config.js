/**
 * vite.config.js
 * Vite build configuration for LearnWise React app.
 * - Integrates Tailwind CSS v4 via the official @tailwindcss/vite plugin.
 * - Sets up path alias "@" → src/ for clean imports.
 * - Proxies /api/* to the Python backend in development.
 */

import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // All /api/* requests forwarded to Flask/FastAPI backend
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});
