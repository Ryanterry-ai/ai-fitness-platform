import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--background)',
        foreground: 'var(--foreground)',
        primary: { DEFAULT: 'var(--primary)', foreground: 'var(--primary-foreground)' },
        secondary: { DEFAULT: 'var(--secondary)', foreground: 'var(--secondary-foreground)' },
        accent: 'var(--accent)',
        muted: { DEFAULT: 'var(--muted)', foreground: 'var(--muted-foreground)' },
        card: { DEFAULT: 'var(--card)', foreground: 'var(--card-foreground)' },
        border: 'var(--border)',
        input: 'var(--input)',
        ring: 'var(--ring)',
        destructive: 'var(--destructive)',
        success: 'var(--success)',
        warning: 'var(--warning)',
        pure: {
          yellow: '#FFD100',
          black: '#1d1d1d',
          white: '#ffffff',
          dark: '#202223',
          gray: '#6d7175',
        },
      },
      fontFamily: {
        heading: ['Oswald', 'sans-serif'],
        sans: ['Roboto', 'sans-serif'],
        body: ['Roboto', 'sans-serif'],
        mono: ['ui-monospace', 'monospace'],
      },
      borderRadius: {
        DEFAULT: '3px',
      },
      transitionTimingFunction: {
        'ease-out-custom': 'cubic-bezier(0.23, 1, 0.32, 1)',
        'ease-in-out-custom': 'cubic-bezier(0.77, 0, 0.175, 1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s cubic-bezier(0.23, 1, 0.32, 1) both',
        'scale-in': 'scaleIn 0.4s cubic-bezier(0.23, 1, 0.32, 1) both',
        'float': 'float 6s ease-in-out infinite',
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(255, 209, 0, 0.3)' },
          '50%': { boxShadow: '0 0 40px rgba(255, 209, 0, 0.6)' },
        },
      },
    },
  },
  plugins: [],
};
export default config;
