const path = require('path');

module.exports = (ctx) => ({
  plugins: [
    require('postcss-import'),
    require('tailwindcss')(path.resolve(__dirname, 'tailwind.config.js')),
    // require('cssnano')({preset: 'default'})

    // process.env.FLASK_PROD === 'production' && require('@fullhuman/postcss-purgecss')({
    //   content: [
    //     path.resolve(__dirname, 'templates/**/*.html')
    //   ],
    //   defaultExtractor: content => content.match(/[A-Za-z0-9-_:/]+/g) || []
    // })
  ],
});

// How to use cssnano?