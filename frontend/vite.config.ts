import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// `base: './'` keeps asset URLs relative so the built `dist/` folder can be
// dropped into any directory on a plain Apache/PHP host (e.g. public_html/ams/).
export default defineConfig({
  plugins: [react()],
  base: './',
  server: { port: 5173 },
});
