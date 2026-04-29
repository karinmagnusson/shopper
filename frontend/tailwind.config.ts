/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pinterest: { DEFAULT: "#E60023", hover: "#AD081B" },
      },
    },
  },
  plugins: [],
};
