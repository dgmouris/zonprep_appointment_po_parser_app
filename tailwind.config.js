module.exports = {
  content: [
    './apps/**/*.html',
    './assets/**/*.js',
    './assets/**/*.ts',
    './assets/**/*.jsx',
    './assets/**/*.tsx',
    './templates/**/*.html',
    './apps/web/templatetags/form_tags.py',
    "./node_modules/react-tailwindcss-datepicker/dist/index.esm.{js,ts}",
  ],
  safelist: [
    'alert-success',
    'alert-info',
    'alert-error',
    'alert-warning',
    'pg-bg-danger',
    'pg-bg-success',
  ],
  theme: {
    extend: {
      aspectRatio: {
        '3/2': '3 / 2',
      },
    },
    container: {
      center: true,
      // padding: '2rem',
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require("daisyui"),
  ],
}
