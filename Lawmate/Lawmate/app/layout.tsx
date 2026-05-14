/**
 * Root layout: global fonts, analytics, and app-wide providers (language + dashboard store).
 * Role-specific shells live under app/citizen, app/lawyer, and app/admin.
 */
import type React from "react"
import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { DashboardProvider } from "@/lib/store/dashboardStore"
import { LanguageProvider } from "@/lib/language"
import "./globals.css"

const _geist = Geist({ subsets: ["latin"] })
const _geistMono = Geist_Mono({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Lawmate - Criminal Legal Assistance",
  description: "AI-powered criminal legal assistance and case management system",
  generator: "v0.app",
  icons: {
    icon: [
      {
        url: "/icon-light-32x32.png",
        media: "(prefers-color-scheme: light)",
      },
      {
        url: "/icon-dark-32x32.png",
        media: "(prefers-color-scheme: dark)",
      },
      {
        url: "/icon.svg",
        type: "image/svg+xml",
      },
    ],
    apple: "/apple-icon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`font-sans antialiased`}>
        <LanguageProvider>
          <DashboardProvider>
            {children}
          </DashboardProvider>
        </LanguageProvider>
        <Analytics />
      </body>
    </html>
  )
}
