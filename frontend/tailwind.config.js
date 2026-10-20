/** AMS design system tokens — see the "AMS design system" reference sheet. */
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        navy: { DEFAULT: '#1E3A5F', 600: '#264A75', 700: '#2A4A72', 800: '#18304F', 900: '#0F1B2D' },
        accent: { DEFAULT: '#1F5FD1', hover: '#1A50B3', soft: '#EAF1FD' },
        ink: { 900: '#0F172A', 700: '#334155', 500: '#5B6B80', 400: '#94A3B8' },
        surface: '#F6F8FB',
        line: '#E2E8F0',
        ok: { dot: '#16A34A', fill: '#E8F5EC', text: '#166534' },
        bad: { dot: '#DC2626', fill: '#FDECEC', text: '#B42318' },
        warn: { dot: '#D97706', fill: '#FEF4E2', text: '#8A4B0B' },
        mute: { dot: '#94A3B8', fill: '#F1F5F9', text: '#475569' },
        info: { dot: '#1E3A5F', fill: '#EAF0F8', text: '#1E3A5F' },
      },
      borderRadius: { card: '6px' },
      boxShadow: {
        raised: '0 1px 2px rgba(15,23,42,.06), 0 2px 8px rgba(15,23,42,.06)',
        overlay: '0 10px 30px rgba(15,23,42,.18)',
      },
    },
  },
  plugins: [],
};
