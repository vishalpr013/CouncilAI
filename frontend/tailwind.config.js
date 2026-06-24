/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark: '#0a0a0a',     // Warm deep black
          card: '#121212',     // Matte black card
          accent: '#d97736',   // Copper accent
          accentLight: '#f6ad55', // Light copper
          border: '#262626',   // Border color
          text: '#eaeaea',     // Primary text
          muted: '#a3a3a3'     // Muted text
        }
      },
      fontFamily: {
        serif: ['Georgia', 'ui-serif', 'serif'], // Fallback to Georgia for elegant serif
        sans: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
