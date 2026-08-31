/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          DEFAULT: "#0F1420",
          soft: "#171E2E",
          softer: "#1F293C",
        },
        capability: {
          DEFAULT: "#7CE0B8",
          dim: "#4E9C82",
        },
        signal: {
          amber: "#E8A45C",
          coral: "#E8735C",
        },
        ivory: "#E7E9EE",
        muted: "#8A93A6",
      },
      fontFamily: {
        display: ["Fraunces", "Iowan Old Style", "Palatino Linotype", "Palatino", "Georgia", "serif"],
        body: ["Inter", "-apple-system", "Segoe UI", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
