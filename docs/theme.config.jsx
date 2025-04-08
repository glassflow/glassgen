export default {
  logo: <span style={{ fontWeight: 600 }}>GlassGen</span>,
  project: {
    link: 'https://github.com/glassflow/glassgen'
  },
  docsRepositoryBase: 'https://github.com/glassflow/glassgen/tree/main/docs',
  footer: {
    text: `GlassGen ${new Date().getFullYear()} © GlassFlow.`
  },
  useNextSeoProps() {
    return {
      titleTemplate: '%s – GlassGen'
    }
  },
  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta name="description" content="GlassGen: Flexible synthetic data generation service" />
      <meta name="og:title" content="GlassGen" />
    </>
  ),
  primaryHue: 210,
  primarySaturation: 100
} 