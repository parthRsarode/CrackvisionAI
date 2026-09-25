/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        civilNavy: '#0f1f38',
        civilDark: '#0a1322',
        steel: '#1e293b',
        steelBorder: '#cbd5e1',
        safetyOrange: '#ea580c',
        safetyAmber: '#d97706',
        cadBlue: '#0284c7',
        blueprint: '#1e40af',
        concrete: '#f8fafc',
        concreteCard: '#ffffff',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      boxShadow: {
        cad: '0 1px 3px 0 rgba(15, 23, 42, 0.08), 0 1px 2px -1px rgba(15, 23, 42, 0.08)',
        'cad-hover': '0 4px 6px -1px rgba(15, 23, 42, 0.1), 0 2px 4px -2px rgba(15, 23, 42, 0.1)',
      },
    },
  },
  plugins: [],
}
