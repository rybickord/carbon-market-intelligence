/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Carbon intelligence color system
        // Black/near-black foundation
        'carbon': {
          DEFAULT: '#020C09',      // Primary background
          surface: '#0D1715',      // Section surface
          elevated: '#111C19',     // Elevated elements
        },
        // OLD NAMES (for backward compatibility with existing components)
        'carbon-dark': {
          DEFAULT: '#020C09',
          secondary: '#0D1715',
          elevated: '#111C19',
          surface: '#111C19',
        },
        // Warm white text hierarchy
        'ivory': {
          DEFAULT: '#F4F1E8',      // Primary text
          secondary: '#AEB5B1',    // Secondary text  
          muted: '#78827E',        // Muted text
        },
        // Primary accent (cyan/mint - keeping both names)
        'cyan': {
          DEFAULT: '#00C8C8',
          light: '#1AD6D6',
          dark: '#00A3A3',
        },
        'mint': {
          DEFAULT: '#00C8C8',      // Same as cyan for compatibility
          light: '#1AD6D6',
          dark: '#00A3A3',
        },
        // Analytical blue
        'royal': {
          DEFAULT: '#1A3FD6',
          light: '#2E52E0',
          dark: '#1432B8',
        },
        // Data visualization colors
        'data-blue': '#1A3FD6',    // Same as royal
        // Utility colors
        'positive': '#4ADE80',
        'warning': '#F4C95D',
        'negative': '#F87171',
        'gold': {
          DEFAULT: '#D6B56A',
          light: '#E4C88A',
          dark: '#C4A354',
        },
        // Scenario accent
        'scenario-accent': '#9B8AFB',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        'display-1': ['5rem', { lineHeight: '1', letterSpacing: '-0.025em', fontWeight: '700' }],
        'display-2': ['4rem', { lineHeight: '1', letterSpacing: '-0.025em', fontWeight: '700' }],
        'display-3': ['3rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }],
        'display-4': ['2.25rem', { lineHeight: '1.1', letterSpacing: '-0.02em', fontWeight: '700' }],
      },
      spacing: {
        '18': '4.5rem',
        '22': '5.5rem',
        '26': '6.5rem',
        '30': '7.5rem',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      boxShadow: {
        'soft': '0 2px 15px -3px rgba(0, 0, 0, 0.3), 0 10px 20px -2px rgba(0, 0, 0, 0.2)',
        'soft-lg': '0 10px 40px -10px rgba(0, 0, 0, 0.4), 0 20px 25px -5px rgba(0, 0, 0, 0.2)',
        'mint': '0 0 30px -5px rgba(53, 224, 178, 0.2)',
      },
    },
  },
  plugins: [],
}
