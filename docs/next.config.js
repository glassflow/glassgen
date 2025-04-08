const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.jsx',
  defaultShowCopyCode: true,
  staticImage: true,
  latex: true,
  flexsearch: {
    codeblocks: false
  }
})

module.exports = withNextra({
  reactStrictMode: true,
  images: {
    unoptimized: true
  },
  basePath: '',
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ]
  }
}) 