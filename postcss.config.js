module.exports = {
  plugins: [
    require('postcss-preset-env')({
      stage: 1,
      browsers: ['> 1%', 'last 2 versions', 'not ie <= 8'],
      autoprefixer: {
        grid: true
      },
      features: {
        'custom-properties': false // Disable CSS custom properties polyfill
      }
    })
  ]
};