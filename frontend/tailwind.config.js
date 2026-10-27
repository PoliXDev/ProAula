/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        meadow: {
          lime: "#d9ed92",
          light: "#b5e48c",
          willow: "#99d98c",
          emerald: "#76c893",
          mist: "#52b69a",
          teal: "#34a0a4",
          bondi: "#168aad",
          cerulean: "#1a759f",
          baltic: "#1e6091",
          yale: "#184e77",
        },
      },
      fontFamily: {
        display: ['"Plus Jakarta Sans"', "sans-serif"],
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
}
