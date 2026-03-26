import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#000000",
        surface: "#0a0a0a",
        card: "#111111",
        border: "#1a1a1a",
        orange: {
          DEFAULT: "#E8522A",
          light: "#FF6B3D",
          dim: "#A83A1E",
          glow: "rgba(232, 82, 42, 0.15)",
        },
        text: {
          DEFAULT: "#F5F5F5",
          dim: "#888888",
          muted: "#555555",
        },
        bull: "#E8522A",
        bear: "#555555",
      },
      fontFamily: {
        serif: ["'KingHwa OldSong'", "Georgia", "serif"],
        sans: ["'KingHwa OldSong'", "'Inter'", "-apple-system", "sans-serif"],
        mono: ["'KingHwa OldSong'", "'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
