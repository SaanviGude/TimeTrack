import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        blue: {
          50: '#eff6ff',
          100: '#dbeafe', 
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#0A74DA',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        purple: {
          200: '#e9d5ff',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          600: '#4b5563',
          900: '#111827',
        }
      },
      animation: {
        'drift': 'drift 40s ease-in-out infinite alternate',
      },
      keyframes: {
        drift: {
          '0%': { transform: 'translate(0, 0) rotate(0deg)' },
          '25%': { transform: 'translate(15px, -20px) rotate(3deg)' },
          '50%': { transform: 'translate(-20px, 25px) rotate(-5deg)' },
          '75%': { transform: 'translate(10px, -15px) rotate(2deg)' },
          '100%': { transform: 'translate(0, 0) rotate(0deg)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
