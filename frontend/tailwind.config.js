/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Professional Government Portal Theme Colors
        govblue: {
          50: '#f0f7ff',
          100: '#e0effe',
          800: '#1e3a8a', // Deep primary blue
          900: '#1e293b',
        },
        govteal: {
          500: '#0d9488',
          700: '#0f766e', // Deep secondary teal
        },
        govorange: {
          500: '#f97316', // Saffron highlight accent
        }
      }
    },
  },
  plugins: [],
}
