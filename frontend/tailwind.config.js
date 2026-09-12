/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        solar: '#fbbf24', // amber-400
        wind: '#22d3ee', // cyan-400
        battery: '#4ade80', // green-400
        diesel: '#f87171', // red-400
      }
    },
  },
  plugins: [],
}
