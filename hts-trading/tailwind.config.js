/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0f0f23',
        'dark-card': '#1a1a2e',
        'dark-border': '#16213e',
      }
    },
  },
  plugins: [],
}