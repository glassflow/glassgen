export default {
  logo: (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <img
        src="/logo_glassgen.png"
        alt="GlassGen Logo"
        style={{ height: '32px' }}
      />
      <span style={{ fontWeight: 600, fontSize: '1.2rem' }}>GlassGen</span>
    </div>
  ),
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
      <link rel="icon" type="image/png" href="/logo_glassgen.png" />
    </>
  ),
  primaryHue: 210,
  primarySaturation: 100
} 