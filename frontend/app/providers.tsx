"use client"

import { ThemeProvider } from "next-themes"
import { LanguageProvider } from "../i18n/LanguageProvider"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <LanguageProvider>{children}</LanguageProvider>
    </ThemeProvider>
  )
}
