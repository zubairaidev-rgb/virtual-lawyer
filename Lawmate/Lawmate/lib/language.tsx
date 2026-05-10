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

  // Chat page
  "chat.title": { en: "Legal AI Assistant", ur: "قانونی اے آئی معاون" },
  "chat.ai_powered": { en: "AI Powered", ur: "اے آئی سے چالو" },
  "chat.subtitle": {
    en: "24/7 Criminal Law Guidance • Instant Answers • Expert Sources",
    ur: "۲۴ گھنٹے فوجداری قانون رہنمائی • فوری جوابات • ماہر ذرائع",
  },
  "chat.placeholder_citizen": {
    en: "Ask about Pakistan criminal law...",
    ur: "پاکستان کے فوجداری قانون کے بارے میں پوچھیں...",
  },
  "chat.placeholder_lawyer": {
    en: "Ask for legal analysis or strategy...",
    ur: "قانونی تجزیہ یا حکمت عملی پوچھیں...",
  },
  "chat.send": { en: "Send", ur: "بھیجیں" },
  "chat.thinking": { en: "Thinking...", ur: "سوچ رہا ہوں..." },
  "chat.sources": { en: "Sources", ur: "ذرائع" },
  "chat.suggested": { en: "Suggested Questions", ur: "تجویز کردہ سوالات" },
  "chat.disclaimer": {
    en: "AI responses are informational. Consult qualified lawyers for legal advice.",
    ur: "اے آئی کے جوابات معلوماتی ہیں۔ قانونی مشورے کے لیے مستند وکیل سے رجوع کریں۔",
  },
  "chat.welcome_citizen": {
    en: "I'm here to help with legal matters in Pakistan. Share your question in plain language, and I will respond with practical legal guidance tailored to your situation.",
    ur: "میں پاکستان میں قانونی معاملات میں آپ کی مدد کے لیے یہاں ہوں۔ اپنا سوال سادہ الفاظ میں بتائیں، اور میں آپ کی صورتحال کے مطابق عملی قانونی رہنمائی فراہم کروں گا۔",
  },
  "chat.welcome_lawyer": {
    en: "I'm here to support your legal workflow. Ask in plain language, and I will provide practical legal analysis and strategy guidance.",
    ur: "میں آپ کے قانونی کام میں مدد کے لیے یہاں ہوں۔ سادہ زبان میں پوچھیں، اور میں عملی قانونی تجزیہ اور حکمت عملی فراہم کروں گا۔",
  },
  "chat.suggest_fir": { en: "What is FIR?", ur: "ایف آئی آر کیا ہے؟" },
  "chat.suggest_bail": { en: "How to get bail?", ur: "ضمانت کیسے ملتی ہے؟" },
  "chat.suggest_appeal": { en: "Appeal process", ur: "اپیل کا طریقہ" },
  "chat.suggest_rights": { en: "My constitutional rights", ur: "میرے آئینی حقوق" },

  // Cases page
  "cases.title": { en: "My Cases", ur: "میرے مقدمات" },
  "cases.subtitle": {
    en: "Track all your ongoing and completed criminal cases",
    ur: "اپنے تمام جاری اور مکمل فوجداری مقدمات ٹریک کریں",
  },
  "cases.add": { en: "Add Case", ur: "مقدمہ شامل کریں" },
  "cases.filter_all": { en: "All Cases", ur: "تمام مقدمات" },
  "cases.filter_active": { en: "Active", ur: "فعال" },
  "cases.filter_hearing": { en: "Hearing Scheduled", ur: "سماعت طے شدہ" },
  "cases.filter_appeal": { en: "Appeal Filed", ur: "اپیل دائر" },
  "cases.filter_closed": { en: "Closed", ur: "بند" },
  "cases.loading": { en: "Loading cases...", ur: "مقدمات لوڈ ہو رہے ہیں..." },
  "cases.error_loading": { en: "Error loading cases", ur: "مقدمات لوڈ کرنے میں خرابی" },
  "cases.retry": { en: "Retry", ur: "دوبارہ کوشش" },
  "cases.none_found": { en: "No cases found", ur: "کوئی مقدمہ نہیں ملا" },
  "cases.none_desc": {
    en: "You don't have any cases matching this filter.",
    ur: "اس فلٹر سے میل کھاتا کوئی مقدمہ نہیں ہے۔",
  },
  "cases.create_first": { en: "Create Your First Case", ur: "اپنا پہلا مقدمہ بنائیں" },
  "cases.court": { en: "Court", ur: "عدالت" },
  "cases.judge": { en: "Judge", ur: "جج" },
  "cases.documents": { en: "Documents", ur: "دستاویزات" },
  "cases.lawyer": { en: "Lawyer", ur: "وکیل" },
  "cases.not_assigned": { en: "Not assigned", ur: "تفویض نہیں" },
  "cases.summary": { en: "Case Summary", ur: "مقدمے کا خلاصہ" },
  "cases.next_hearing": { en: "Next Hearing", ur: "اگلی سماعت" },
  "cases.view_details": { en: "View Details", ur: "تفصیل دیکھیں" },

  // Documents page
  "docs.title": { en: "My Documents", ur: "میری دستاویزات" },
  "docs.subtitle": {
    en: "Upload, analyze, and generate legal documents",
    ur: "قانونی دستاویزات اپ لوڈ، تجزیہ اور تیار کریں",
  },
  "docs.total": { en: "Total Documents", ur: "کل دستاویزات" },
  "docs.uploaded": { en: "Uploaded", ur: "اپ لوڈ شدہ" },
  "docs.generated": { en: "Generated", ur: "تیار شدہ" },
  "docs.ready": { en: "Ready", ur: "تیار" },
  "docs.tab_uploaded": { en: "Uploaded Documents", ur: "اپ لوڈ شدہ دستاویزات" },
  "docs.tab_generated": { en: "Generated Documents", ur: "تیار شدہ دستاویزات" },
  "docs.tab_templates": { en: "Templates", ur: "سانچے" },
  "docs.tab_analyze": { en: "Analyze Document", ur: "دستاویز کا تجزیہ" },
  "docs.browse_templates": { en: "Browse Templates", ur: "سانچے دیکھیں" },
  "docs.upload_btn": { en: "Upload Document", ur: "دستاویز اپ لوڈ کریں" },
  "docs.upload_section": { en: "Upload Document", ur: "دستاویز اپ لوڈ کریں" },
  "docs.select_file": { en: "Select PDF or DOCX file", ur: "PDF یا DOCX فائل منتخب کریں" },
  "docs.none_uploaded": { en: "No documents uploaded yet", ur: "ابھی تک کوئی دستاویز اپ لوڈ نہیں" },
  "docs.none_generated": { en: "No documents generated yet", ur: "ابھی تک کوئی دستاویز تیار نہیں" },

  // Auth
  "auth.email": { en: "Email Address", ur: "ای میل پتہ" },
  "auth.password": { en: "Password", ur: "پاس ورڈ" },
  "auth.name": { en: "Full Name", ur: "پورا نام" },
  "auth.login": { en: "Sign In", ur: "لاگ ان" },
  "auth.signup": { en: "Sign Up", ur: "سائن اپ" },

  // Citizen Dashboard
  "dash.welcome": { en: "Welcome back,", ur: "خوش آمدید،" },
  "dash.subtitle": { en: "Your legal journey — Pakistan criminal law guidance powered by AI", ur: "آپ کا قانونی سفر — اے آئی سے چالو پاکستان فوجداری قانون رہنمائی" },
  "dash.notifications": { en: "Notifications", ur: "اطلاعات" },
  "dash.retry": { en: "Retry", ur: "دوبارہ کوشش" },
  "dash.active_cases": { en: "Active Cases", ur: "فعال مقدمات" },
  "dash.cases_in_progress": { en: "Cases in progress", ur: "زیر عمل مقدمات" },
  "dash.pending_hearings": { en: "Pending Hearings", ur: "زیر التوا سماعتیں" },
  "dash.next_hearing": { en: "Next hearing scheduled", ur: "اگلی سماعت طے شدہ" },
  "dash.documents": { en: "Documents", ur: "دستاویزات" },
  "dash.generated_docs": { en: "Generated documents", ur: "تیار شدہ دستاویزات" },
  "dash.top_lawyers": { en: "Top Lawyers", ur: "اعلیٰ وکلاء" },
  "dash.recommended": { en: "Recommended for you", ur: "آپ کے لیے تجویز کردہ" },
  "dash.top_rated": { en: "Top rated", ur: "اعلیٰ درجہ بند" },
  "dash.loading": { en: "Loading...", ur: "لوڈ ہو رہا ہے..." },
  "dash.loading_cases": { en: "Loading cases...", ur: "مقدمات لوڈ ہو رہے ہیں..." },
  "dash.your_cases": { en: "Your Cases", ur: "آپ کے مقدمات" },
  "dash.view_all": { en: "View All", ur: "سب دیکھیں" },
  "dash.no_cases": { en: "No cases found", ur: "کوئی مقدمہ نہیں ملا" },
  "dash.judge": { en: "Judge:", ur: "جج:" },
  "dash.progress": { en: "Progress", ur: "پیشرفت" },
  "dash.quick_actions": { en: "Quick Actions", ur: "فوری اقدامات" },
  "dash.chat_ai": { en: "Chat with AI", ur: "اے آئی سے بات کریں" },
  "dash.analyze_case": { en: "Analyze Case", ur: "مقدمہ تجزیہ" },
  "dash.generate_doc": { en: "Generate Document", ur: "دستاویز تیار کریں" },
  "dash.find_lawyer": { en: "Find Lawyer", ur: "وکیل تلاش کریں" },
  "dash.next_hearing_card": { en: "Next Hearing", ur: "اگلی سماعت" },
  "dash.add_calendar": { en: "Add to Calendar", ur: "کیلنڈر میں شامل کریں" },
  "dash.no_hearings": { en: "No upcoming hearings", ur: "کوئی آئندہ سماعت نہیں" },
  "dash.ai_recommendations": { en: "AI-Powered Recommendations", ur: "اے آئی سے چالو سفارشات" },
  "dash.loading_recs": { en: "Loading recommendations...", ur: "سفارشات لوڈ ہو رہی ہیں..." },
  "dash.no_recs": { en: "No recommendations at this time", ur: "اس وقت کوئی سفارش نہیں" },
  "dash.this_month": { en: "this month", ur: "اس ماہ" },
  "dash.no_upcoming": { en: "No upcoming", ur: "کوئی آئندہ نہیں" },
  "dash.new": { en: "new", ur: "نئی" },

  // Case Analysis page
  "analysis.title": { en: "Case Analysis", ur: "مقدمے کا تجزیہ" },
  "analysis.subtitle": { en: "Add full case facts in simple language. More details give more accurate Pakistan criminal-law guidance.", ur: "اپنے مقدمے کے تمام حقائق سادہ زبان میں لکھیں۔ زیادہ تفصیل سے زیادہ درست پاکستانی فوجداری قانون رہنمائی ملے گی۔" },
  "analysis.onboarding": { en: "Case Onboarding", ur: "مقدمہ داخلہ" },
  "analysis.desc": { en: "Case Description *", ur: "مقدمے کی تفصیل *" },
  "analysis.desc_ph": { en: "Write complete timeline: what happened, when, where, who was involved, what police did, and what help you need.", ur: "مکمل ترتیب لکھیں: کیا ہوا، کب، کہاں، کون شامل تھا، پولیس نے کیا کیا، اور آپ کو کیا مدد چاہیے۔" },
  "analysis.main_q": { en: "Main Legal Question (optional)", ur: "اہم قانونی سوال (اختیاری)" },
  "analysis.main_q_ph": { en: "e.g., Police refused FIR. What is my next legal remedy?", ur: "مثال: پولیس نے ایف آئی آر درج کرنے سے انکار کیا۔ میرا اگلا قانونی علاج کیا ہے؟" },
  "analysis.loading_case": { en: "Loading selected case details...", ur: "منتخب مقدمے کی تفصیل لوڈ ہو رہی ہے..." },
  "analysis.case_type": { en: "Case Type (from selected case)", ur: "مقدمے کی قسم (منتخب مقدمے سے)" },
  "analysis.case_type_ph": { en: "Criminal Matter", ur: "فوجداری معاملہ" },
  "analysis.case_summary": { en: "Case Summary", ur: "مقدمے کا خلاصہ" },
  "analysis.case_summary_ph": { en: "A concise summary of this case (auto-filled after prepare step if empty).", ur: "اس مقدمے کا مختصر خلاصہ (اگر خالی ہو تو تیاری کے مرحلے کے بعد خود بھر جائے گا)۔" },
  "analysis.urgency": { en: "Urgency", ur: "فوریت" },
  "analysis.low": { en: "Low", ur: "کم" },
  "analysis.medium": { en: "Medium", ur: "درمیانہ" },
  "analysis.high": { en: "High", ur: "زیادہ" },
  "analysis.city": { en: "City (optional)", ur: "شہر (اختیاری)" },
  "analysis.court": { en: "Hearing Court (optional)", ur: "سماعتی عدالت (اختیاری)" },
  "analysis.custody": { en: "Custody Status", ur: "حراست کی صورتحال" },
  "analysis.custody_unknown": { en: "Unknown", ur: "نامعلوم" },
  "analysis.in_custody": { en: "In Custody", ur: "حراست میں" },
  "analysis.not_in_custody": { en: "Not in Custody", ur: "حراست میں نہیں" },
  "analysis.stage": { en: "Case Stage", ur: "مقدمے کا مرحلہ" },
  "analysis.stage_ph": { en: "Pre-FIR / Post-FIR / Investigation / Trial", ur: "ایف آئی آر سے پہلے / بعد / تفتیش / مقدمہ" },
  "analysis.incident_date": { en: "Incident Date (optional)", ur: "واقعے کی تاریخ (اختیاری)" },
  "analysis.incident_loc": { en: "Incident Location", ur: "واقعے کی جگہ" },
  "analysis.fir_rel": { en: "FIR Relevance", ur: "ایف آئی آر متعلقہ" },
  "analysis.applicable": { en: "Applicable", ur: "قابل اطلاق" },
  "analysis.not_applicable": { en: "Not applicable in this case", ur: "اس مقدمے میں قابل اطلاق نہیں" },
  "analysis.fir_status": { en: "FIR Status", ur: "ایف آئی آر کی صورتحال" },
  "analysis.fir_status_ph": { en: "Registered / Refused / Under process", ur: "درج / انکار / زیر کارروائی" },
  "analysis.police_station": { en: "Police Station (optional)", ur: "پولیس اسٹیشن (اختیاری)" },
  "analysis.witness_rel": { en: "Witness Relevance", ur: "گواہ متعلقہ" },
  "analysis.witness_status": { en: "Witness Status", ur: "گواہ کی صورتحال" },
  "analysis.witness_count": { en: "Witness Count", ur: "گواہوں کی تعداد" },
  "analysis.evidence_rel": { en: "Evidence Relevance", ur: "شہادت متعلقہ" },
  "analysis.evidence_summary": { en: "Evidence Summary", ur: "شہادت کا خلاصہ" },
  "analysis.doc_rel": { en: "Document Relevance", ur: "دستاویز متعلقہ" },
  "analysis.avail_docs": { en: "Available Documents", ur: "دستیاب دستاویزات" },
  "analysis.desired_outcome": { en: "Desired Outcome", ur: "مطلوبہ نتیجہ" },
  "analysis.desired_ph": { en: "FIR registration, bail, recovery, protection, cancellation, etc.", ur: "ایف آئی آر درج، ضمانت، بازیابی، تحفظ، منسوخی وغیرہ" },
  "analysis.child_involved": { en: "Child/juvenile involved in this case", ur: "اس مقدمے میں بچہ/نوجوان شامل ہے" },
  "analysis.run": { en: "Run Analysis", ur: "تجزیہ چلائیں" },
  "analysis.generate": { en: "Generate Summary + Analysis", ur: "خلاصہ + تجزیہ تیار کریں" },
  "analysis.preparing": { en: "Preparing Summary...", ur: "خلاصہ تیار ہو رہا ہے..." },
  "analysis.generating": { en: "Generating Analysis...", ur: "تجزیہ تیار ہو رہا ہے..." },
  "analysis.reset": { en: "Reset Prepare Step", ur: "تیاری کا مرحلہ دوبارہ شروع کریں" },
  "analysis.click_hint": { en: "Click \"Generate Summary + Analysis\" to run complete case analysis in one step.", ur: "مکمل مقدمے کا تجزیہ ایک قدم میں چلانے کے لیے \"خلاصہ + تجزیہ تیار کریں\" پر کلک کریں۔" },
  "analysis.case_summary_result": { en: "Case Summary", ur: "مقدمے کا خلاصہ" },
  "analysis.risk_score": { en: "Risk Score", ur: "خطرے کا اسکور" },
  "analysis.risk": { en: "Risk", ur: "خطرہ" },
  "analysis.case_type_result": { en: "Likely Case Type", ur: "ممکنہ مقدمے کی قسم" },
  "analysis.sections": { en: "Extracted Sections", ur: "نکالی گئی دفعات" },
  "analysis.recommendations": { en: "Recommendations", ur: "سفارشات" },
  "analysis.next_steps": { en: "Immediate Next Steps", ur: "فوری اگلے اقدامات" },
  "analysis.prepared_summary": { en: "Prepared Case Summary", ur: "تیار شدہ مقدمے کا خلاصہ" },

  // Find Lawyers page
  "lawyers.title": { en: "Find Lawyers", ur: "وکیل تلاش کریں" },
  "lawyers.subtitle": { en: "Browse and connect with experienced criminal law specialists", ur: "تجربہ کار فوجداری قانون کے ماہرین سے ملیں اور رابطہ کریں" },
  "lawyers.rec_title": { en: "Criminal Case Lawyer Recommendation System", ur: "فوجداری مقدمے کے وکیل کی سفارشی نظام" },
  "lawyers.rec_desc": { en: "Enter your criminal case details below. The system will rank best-fit lawyers using professional criteria.", ur: "نیچے اپنے فوجداری مقدمے کی تفصیلات درج کریں۔ نظام پیشہ ورانہ معیار سے بہترین وکیل ترتیب دے گا۔" },
  "lawyers.case_type": { en: "Case Type", ur: "مقدمے کی قسم" },
  "lawyers.city": { en: "City / Preferred Location", ur: "شہر / ترجیحی مقام" },
  "lawyers.court": { en: "Hearing Court (Optional)", ur: "سماعتی عدالت (اختیاری)" },
  "lawyers.urgency": { en: "Urgency", ur: "فوریت" },
  "lawyers.budget": { en: "Budget Range", ur: "بجٹ حد" },
  "lawyers.experience": { en: "Preferred minimum experience (years)", ur: "ترجیحی کم از کم تجربہ (سال)" },
  "lawyers.language": { en: "Preferred language (Optional)", ur: "ترجیحی زبان (اختیاری)" },
  "lawyers.case_desc": { en: "Case Description *", ur: "مقدمے کی تفصیل *" },
  "lawyers.find_btn": { en: "Find Best Lawyers", ur: "بہترین وکیل تلاش کریں" },
  "lawyers.finding": { en: "Finding Lawyers...", ur: "وکیل تلاش ہو رہے ہیں..." },
  "lawyers.search_ph": { en: "Search lawyers by name or specialization...", ur: "نام یا تخصص سے وکیل تلاش کریں..." },
  "lawyers.showing": { en: "Showing", ur: "دکھا رہے ہیں" },
  "lawyers.of": { en: "of", ur: "میں سے" },
  "lawyers.cases_won": { en: "Cases Won", ur: "جیتے گئے مقدمات" },
  "lawyers.experience_label": { en: "Experience", ur: "تجربہ" },
  "lawyers.success": { en: "Success", ur: "کامیابی" },
  "lawyers.response_time": { en: "Response Time:", ur: "جواب کا وقت:" },
  "lawyers.hourly_rate": { en: "Hourly Rate:", ur: "فی گھنٹہ شرح:" },
  "lawyers.languages": { en: "Languages:", ur: "زبانیں:" },
  "lawyers.message": { en: "Message", ur: "پیغام" },
  "lawyers.consult": { en: "Consult", ur: "مشاورت" },
  "lawyers.view_profile": { en: "View Full Profile & Availability", ur: "مکمل پروفائل اور دستیابی دیکھیں" },
  "lawyers.available": { en: "Available", ur: "دستیاب" },
  "lawyers.verified": { en: "Verified", ur: "تصدیق شدہ" },
  "lawyers.filters": { en: "Filters", ur: "فلٹرز" },
  "lawyers.highest_rated": { en: "Highest Rated", ur: "اعلیٰ درجہ بند" },

  // Documents page extra
  "docs.ai_suggest": { en: "AI Document Type Suggestion", ur: "اے آئی دستاویز قسم تجویز" },
  "docs.enter_facts": { en: "Enter Case Facts (JSON format or key-value pairs)", ur: "مقدمے کے حقائق درج کریں (JSON فارمیٹ)" },
  "docs.get_suggestions": { en: "Get Suggestions", ur: "تجاویز حاصل کریں" },
  "docs.available_templates": { en: "Available Templates", ur: "دستیاب سانچے" },
  "docs.req_info": { en: "Required Information", ur: "ضروری معلومات" },
  "docs.fill_info": { en: "Fill Document Information", ur: "دستاویز کی معلومات بھریں" },
  "docs.required": { en: "Required", ur: "ضروری" },
  "docs.reset_form": { en: "Reset Form", ur: "فارم دوبارہ شروع کریں" },
  "docs.fields_required": { en: "fields required", ur: "فیلڈز ضروری ہیں" },
  "docs.generate": { en: "Generate Document", ur: "دستاویز تیار کریں" },
  "docs.generating": { en: "Generating...", ur: "تیار ہو رہی ہے..." },
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
