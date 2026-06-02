import type { Metadata, Viewport } from "next"
import { Poppins } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"

const poppins = Poppins({
  weight: ["300", "400", "500", "600", "700", "800"],
  subsets: ["latin"],
  display: "swap",
})

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
}

export const metadata: Metadata = {
  title: "NedLang — AI Language Learning",
  description: "Personalized AI-powered language learning with internationally recognized frameworks.",
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html className="h-full antialiased" suppressHydrationWarning>
      <body className={`${poppins.className} min-h-full flex flex-col`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
