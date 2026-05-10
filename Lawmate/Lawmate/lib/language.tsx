"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

export type Language = "en" | "ur"

interface LanguageContextType {
  language: Language
  toggleLanguage: () => void
  isUrdu: boolean
  t: (key: string) => string
}

const TRANSLATIONS: Record<string, Record<Language, string>> = {
  // Sidebar navigation
  "nav.dashboard": { en: "Dashboard", ur: "ڈیش بورڈ" },
  "nav.ai_assistant": { en: "AI Assistant", ur: "اے آئی معاون" },
  "nav.my_cases": { en: "My Cases", ur: "میرے مقدمات" },
  "nav.documents": { en: "Documents", ur: "دستاویزات" },
  "nav.find_lawyers": { en: "Find Lawyers", ur: "وکیل تلاش کریں" },
  "nav.my_clients": { en: "My Clients", ur: "میرے مؤکلین" },
  "nav.cases": { en: "Cases", ur: "مقدمات" },
  "nav.analytics": { en: "Analytics", ur: "تجزیات" },
  "nav.users": { en: "Users", ur: "صارفین" },
  "nav.lawyers": { en: "Lawyers", ur: "وکلاء" },
  "nav.settings": { en: "Settings", ur: "ترتیبات" },
  "nav.logout": { en: "Logout", ur: "لاگ آؤٹ" },
  "nav.switch_lang": { en: "اردو", ur: "English" },

  // Chat
  "chat.placeholder_citizen": {
    en: "Ask about Pakistan criminal law...",
    ur: "پاکستان کے فوجداری قانون کے بارے میں پوچھیں...",
  },
  "chat.placeholder_lawyer": {
    en: "Ask for legal analysis or strategy...",
    ur: "قانونی تجزیہ یا حکمت عملی پوچھیں...",
  },
  "chat.send": { en: "Send", ur: "بھیجیں" },
  "chat.welcome_citizen": {
    en: "I'm here to help with legal matters in Pakistan. Share your question in plain language, and I will respond with practical legal guidance tailored to your situation.",
    ur: "میں پاکستان میں قانونی معاملات میں آپ کی مدد کے لیے یہاں ہوں۔ اپنا سوال سادہ الفاظ میں بتائیں، اور میں آپ کی صورتحال کے مطابق عملی قانونی رہنمائی فراہم کروں گا۔",
  },
  "chat.welcome_lawyer": {
    en: "I'm here to support your legal workflow. Ask in plain language, and I will provide practical legal analysis and strategy guidance.",
    ur: "میں آپ کے قانونی کام میں مدد کے لیے یہاں ہوں۔ سادہ زبان میں پوچھیں، اور میں عملی قانونی تجزیہ اور حکمت عملی فراہم کروں گا۔",
  },

  // Auth
  "auth.email": { en: "Email Address", ur: "ای میل پتہ" },
  "auth.password": { en: "Password", ur: "پاس ورڈ" },
  "auth.name": { en: "Full Name", ur: "پورا نام" },
  "auth.login": { en: "Sign In", ur: "لاگ ان" },
  "auth.signup": { en: "Sign Up", ur: "سائن اپ" },
}

const LanguageContext = createContext<LanguageContextType>({
  language: "en",
  toggleLanguage: () => {},
  isUrdu: false,
  t: (key) => key,
})

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>("en")

  useEffect(() => {
    try {
      const saved = localStorage.getItem("lawmate_language") as Language | null
      if (saved === "en" || saved === "ur") {
        setLanguage(saved)
      }
    } catch {}
  }, [])

  useEffect(() => {
    document.documentElement.lang = language
  }, [language])

  const toggleLanguage = () => {
    const next: Language = language === "en" ? "ur" : "en"
    setLanguage(next)
    try {
      localStorage.setItem("lawmate_language", next)
    } catch {}
  }

  const t = (key: string): string =>
    TRANSLATIONS[key]?.[language] ?? TRANSLATIONS[key]?.["en"] ?? key

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, isUrdu: language === "ur", t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  return useContext(LanguageContext)
}
