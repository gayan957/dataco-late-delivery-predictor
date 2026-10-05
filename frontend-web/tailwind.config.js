/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', 'sans-serif'] },
      colors: {
        navy: {
          950: '#060b18',
          900: '#0d1526',
          800: '#141f38',
          700: '#1e2d52',
        },
      },
    },
  },
  plugins: [],
}
