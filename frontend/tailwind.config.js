/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bamboo: {
          nav: '#102b3a',
          nav2: '#183d4e',
          accent: '#1e7a8c',
          accent2: '#2e9e83',
          warn: '#c77b29',
          danger: '#bb4e4e',
          bg: '#f4f7f8'
        }
      }
    },
  },
  plugins: [],
}
