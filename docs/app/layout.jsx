import { Footer, Layout, Navbar } from 'nextra-theme-docs'
import { Head } from 'nextra/components'
import { getPageMap } from 'nextra/page-map'
import 'nextra-theme-docs/style.css'

export const metadata = {
  title: {
    template: '%s – GlassGen'
  },
  description: 'GlassGen: Flexible synthetic data generation service',
  openGraph: {
    title: 'GlassGen'
  }
}

const navbar = (
  <Navbar
    logo={
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <img
          src="/logo_glassgen.png"
          alt="GlassGen Logo"
          style={{ height: '32px' }}
        />
        <span style={{ fontWeight: 600, fontSize: '1.2rem' }}>GlassGen</span>
      </div>
    }
    projectLink="https://github.com/glassflow/glassgen"
  />
)

const footer = (
  <Footer>GlassGen {new Date().getFullYear()} © GlassFlow.</Footer>
)

export default async function RootLayout({ children }) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <Head
        color={{
          hue: { dark: 210, light: 210 },
          saturation: { dark: 100, light: 100 }
        }}
      >
        <link rel="icon" type="image/png" href="/logo_glassgen.png" />
      </Head>
      <body>
        <Layout
          navbar={navbar}
          footer={footer}
          docsRepositoryBase="https://github.com/glassflow/glassgen/tree/main/docs"
          pageMap={await getPageMap()}
        >
          {children}
        </Layout>
      </body>
    </html>
  )
}
