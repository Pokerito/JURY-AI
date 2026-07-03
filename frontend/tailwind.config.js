/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: {
          light: '#1E293B',
          DEFAULT: '#0B1120',
          dark: '#020617',
        },
        cyber: {
          cyan: '#22D3EE',
          cyanGlow: 'rgba(34, 211, 238, 0.4)',
          red: '#F43F5E',
          yellow: '#FBBF24',
          green: '#10B981',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Roboto Mono', 'monospace'],
      },
      boxShadow: {
        'glow-cyan': '0 0 15px rgba(34, 211, 238, 0.3)',
        'glow-red': '0 0 15px rgba(244, 63, 94, 0.3)',
        'glow-green': '0 0 15px rgba(16, 185, 129, 0.3)',
        'glass': 'inset 0 1px 0 0 rgba(255, 255, 255, 0.05)',
      },
      backgroundImage: {
        'mesh-gradient': 'radial-gradient(at 0% 0%, rgba(34, 211, 238, 0.15) 0px, transparent 50%), radial-gradient(at 100% 100%, rgba(147, 51, 234, 0.15) 0px, transparent 50%)'
      }
    },
  },
  plugins: [],
}
