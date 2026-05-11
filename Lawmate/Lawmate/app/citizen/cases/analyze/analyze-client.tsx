"use client"

import { useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { AlertCircle, Brain, Loader2, CheckCircle2, XCircle, BarChart3, Lightbulb } from "lucide-react"
import {
  analyzeCitizenCaseQuick,
  extractOnboardingCaseProfile,
  type CitizenQuickCaseAnalysisResponse,
  type OnboardingExtractionResponse,
} from "@/lib/services/analysis"
import { getCaseDetails } from "@/lib/services/cases"
import { useLanguage } from "@/lib/language"

export default function CaseAnalysisPage() {
  const { t, language } = useLanguage()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)
  const [onboardingLoading, setOnboardingLoading] = useState(false)
  const [caseDescription, setCaseDescription] = useState("")
  const [caseType, setCaseType] = useState("")
  const [caseSummary, setCaseSummary] = useState("")
  const [urgency, setUrgency] = useState<"low" | "medium" | "high">("medium")
  const [city, setCity] = useState("")
  const [hearingCourt, setHearingCourt] = useState("")
  const [custodyStatus, setCustodyStatus] = useState<"in_custody" | "not_in_custody" | "unknown">("unknown")
  const [caseStage, setCaseStage] = useState("")
  const [incidentDate, setIncidentDate] = useState("")
  const [incidentLocation, setIncidentLocation] = useState("")
  const [firApplicability, setFirApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [firStatus, setFirStatus] = useState("")
  const [policeStation, setPoliceStation] = useState("")
  const [witnessApplicability, setWitnessApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [witnessStatus, setWitnessStatus] = useState("")
  const [witnessCount, setWitnessCount] = useState(0)
  const [evidenceApplicability, setEvidenceApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [evidenceSummary, setEvidenceSummary] = useState("")
  const [documentsApplicability, setDocumentsApplicability] = useState<"applicable" | "not_applicable" | "unknown">("unknown")
  const [availableDocuments, setAvailableDocuments] = useState("")
  const [keyQuestion, setKeyQuestion] = useState("")
  const [desiredOutcome, setDesiredOutcome] = useState("")
  const [childInvolved, setChildInvolved] = useState(false)
  const [results, setResults] = useState<CitizenQuickCaseAnalysisResponse | null>(null)
  const [onboardingProfile, setOnboardingProfile] = useState<OnboardingExtractionResponse | null>(null)
  const [prefillLoading, setPrefillLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const caseId = searchParams.get("caseId")
    if (!caseId) return

    const prefillCase = async () => {
      setPrefillLoading(true)
      try {
        const details = await getCaseDetails(caseId)
        setCaseDescription(details.description || "")
        setCaseSummary(details.case_summary || "")
        setCaseType(details.case_type || "")
        setHearingCourt(details.court || "")
        setIncidentDate(details.filing_date || "")
        setCaseStage((details.status as string) || "")
        setFirStatus(details.fir_number ? "registered" : "")
        setPoliceStation(details.police_station || "")
        if (details.fir_number) setFirApplicability("applicable")
        setKeyQuestion(`Please analyze this case (${details.case_type || "criminal matter"}) and suggest best legal steps.`)
        setDesiredOutcome("Best legal strategy and next steps")
      } catch (err: any) {
        setError(err.message || "Failed to auto-load case details.")
      } finally {
        setPrefillLoading(false)
      }
    }

    void prefillCase()
  }, [searchParams])

  const handlePrepareAnalysis = async () => {
    setOnboardingLoading(true)
    setError(null)
    setResults(null)
    try {
      const response = await extractOnboardingCaseProfile({
        case_description: caseDescription,
        city,
        case_type: caseType,
        urgency,
        custody_status: custodyStatus,
        language,
      })
      setOnboardingProfile(response)
      if (!caseSummary) setCaseSummary(response.one_paragraph_summary)
      if (!keyQuestion) setKeyQuestion(
        language === "ur"
          ? `اس مقدمے (${caseType || "فوجداری معاملہ"}) کا تجزیہ کریں اور بہترین قانونی حکمت عملی بتائیں۔`
          : `Analyze ${caseType || "this matter"} and suggest strongest legal strategy.`
      )
      if (!desiredOutcome) setDesiredOutcome(
        language === "ur"
          ? "واضح قانونی حکمت عملی، فوری عمل کا منصوبہ، اور عملی قانونی راستہ۔"
          : "Clear legal strategy, immediate action plan, and practical remedy path."
      )
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to prepare analysis."
      setError(message)
    } finally {
      setOnboardingLoading(false)
    }
  }

  const handleAnalyze = async (preparedProfile?: OnboardingExtractionResponse) => {
    const effectiveProfile = preparedProfile || onboardingProfile
    if (!effectiveProfile) {
      setError("Unable to prepare analysis inputs. Please try again.")
      return
    }
    if (!keyQuestion.trim() || !desiredOutcome.trim()) {
      setError("Please add both Main Legal Question and Desired Outcome before final analysis.")
      return
    }
    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const effectiveFirStatus =
        firApplicability === "not_applicable" ? "not_applicable" : firStatus || firApplicability
      const effectiveWitnessStatus =
        witnessApplicability === "not_applicable" ? "not_applicable" : witnessStatus || witnessApplicability
      const effectiveWitnessCount = witnessApplicability === "applicable" ? witnessCount : 0
      const effectiveEvidenceSummary =
        evidenceApplicability === "not_applicable" ? "not_applicable" : evidenceSummary
      const effectiveDocuments =
        documentsApplicability === "not_applicable" ? "not_applicable" : availableDocuments

      const response = await analyzeCitizenCaseQuick({
        case_description: `${caseDescription}\n\nCase Summary: ${caseSummary || effectiveProfile.one_paragraph_summary}`,
        urgency,
        city,
        hearing_court: hearingCourt,
        custody_status: custodyStatus,
        case_stage: caseStage,
        incident_date: incidentDate,
        incident_location: incidentLocation,
        fir_status: effectiveFirStatus,
        police_station: policeStation,
        witness_status: effectiveWitnessStatus,
        witness_count: effectiveWitnessCount,
        evidence_summary: effectiveEvidenceSummary,
        available_documents: effectiveDocuments,
        key_question: keyQuestion,
        desired_outcome: desiredOutcome,
        child_involved: childInvolved,
        language,
      })
      setResults(response)
    } catch (err: any) {
      setError(err.message || "Analysis failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  const handleRunFullAnalysis = async () => {
    if (caseDescription.trim().length < 20) return

    setError(null)
    setResults(null)
    setOnboardingLoading(true)

    try {
      const prepared = await extractOnboardingCaseProfile({
        case_description: caseDescription,
        city,
        case_type: caseType,
        urgency,
        custody_status: custodyStatus,
        language,
      })

      setOnboardingProfile(prepared)
      if (!caseSummary) setCaseSummary(prepared.one_paragraph_summary)
      if (!keyQuestion) setKeyQuestion(
        language === "ur"
          ? `اس مقدمے (${caseType || "فوجداری معاملہ"}) کا تجزیہ کریں اور بہترین قانونی حکمت عملی بتائیں۔`
          : `Analyze ${caseType || "this matter"} and suggest strongest legal strategy.`
      )
      if (!desiredOutcome) setDesiredOutcome(
        language === "ur"
          ? "واضح قانونی حکمت عملی، فوری عمل کا منصوبہ، اور عملی قانونی راستہ۔"
          : "Clear legal strategy, immediate action plan, and practical remedy path."
      )
      setOnboardingLoading(false)

      await handleAnalyze(prepared)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to run analysis."
      setError(message)
    } finally {
      setOnboardingLoading(false)
    }
  }

  const getRiskColor = (risk: number) => {
    if (risk >= 80) return "text-destructive"
    if (risk >= 60) return "text-orange-500"
    if (risk >= 40) return "text-yellow-500"
    return "text-green-500"
  }

  const getRiskBg = (risk: number) => {
    if (risk >= 80) return "bg-destructive/20 border-destructive/50"
    if (risk >= 60) return "bg-orange-500/20 border-orange-500/50"
    if (risk >= 40) return "bg-yellow-500/20 border-yellow-500/50"
    return "bg-green-500/20 border-green-500/50"
  }

  return (
    <div className="flex">
      <Sidebar userType="citizen" />
      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-primary/5 p-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">{t("analysis.title")}</h1>
            <p className="text-muted-foreground">{t("analysis.subtitle")}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Form */}
            <div className="lg:col-span-1 space-y-6">
              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <Brain className="w-5 h-5 text-primary" />
                  {t("analysis.onboarding")}
                </h2>
                <div className="space-y-2">
                  <label className="text-sm font-medium mb-2 block">{t("analysis.desc")}</label>
                  <Textarea value={caseDescription} onChange={(e) => setCaseDescription(e.target.value)} placeholder={t("analysis.desc_ph")} rows={8} />
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.main_q")}</label>
                    <Input value={keyQuestion} onChange={(e) => setKeyQuestion(e.target.value)} placeholder={t("analysis.main_q_ph")} />
                  </div>
                  {prefillLoading && <p className="text-xs text-muted-foreground">{t("analysis.loading_case")}</p>}
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.case_type")}</label>
                    <Input value={caseType} onChange={(e) => setCaseType(e.target.value)} placeholder={t("analysis.case_type_ph")} />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.case_summary")}</label>
                    <Textarea value={caseSummary} onChange={(e) => setCaseSummary(e.target.value)} placeholder={t("analysis.case_summary_ph")} rows={3} />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.urgency")}</label>
                    <select value={urgency} onChange={(e) => setUrgency(e.target.value as "low" | "medium" | "high")} className="w-full px-3 py-2 border rounded-md bg-background">
                      <option value="low">{t("analysis.low")}</option>
                      <option value="medium">{t("analysis.medium")}</option>
                      <option value="high">{t("analysis.high")}</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.city")}</label>
                    <Input value={city} onChange={(e) => setCity(e.target.value)} placeholder="Islamabad" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.court")}</label>
                    <Input value={hearingCourt} onChange={(e) => setHearingCourt(e.target.value)} placeholder="Sessions Court" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.custody")}</label>
                    <select value={custodyStatus} onChange={(e) => setCustodyStatus(e.target.value as "in_custody" | "not_in_custody" | "unknown")} className="w-full px-3 py-2 border rounded-md bg-background">
                      <option value="unknown">{t("analysis.custody_unknown")}</option>
                      <option value="in_custody">{t("analysis.in_custody")}</option>
                      <option value="not_in_custody">{t("analysis.not_in_custody")}</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.stage")}</label>
                    <Input value={caseStage} onChange={(e) => setCaseStage(e.target.value)} placeholder={t("analysis.stage_ph")} />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.incident_date")}</label>
                    <Input type="date" value={incidentDate} onChange={(e) => setIncidentDate(e.target.value)} />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.incident_loc")}</label>
                    <Input value={incidentLocation} onChange={(e) => setIncidentLocation(e.target.value)} placeholder="Area, city, place of incident" />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.fir_rel")}</label>
                    <select value={firApplicability} onChange={(e) => setFirApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")} className="w-full px-3 py-2 border rounded-md bg-background">
                      <option value="unknown">{t("analysis.custody_unknown")}</option>
                      <option value="applicable">{t("analysis.applicable")}</option>
                      <option value="not_applicable">{t("analysis.not_applicable")}</option>
                    </select>
                  </div>
                  {firApplicability === "applicable" && (
                    <>
                      <div>
                        <label className="text-sm font-medium mb-2 block">{t("analysis.fir_status")}</label>
                        <Input value={firStatus} onChange={(e) => setFirStatus(e.target.value)} placeholder={t("analysis.fir_status_ph")} />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">{t("analysis.police_station")}</label>
                        <Input
                          value={policeStation}
                          onChange={(e) => setPoliceStation(e.target.value)}
                          placeholder="e.g., Civil Lines Police Station"
                        />
                      </div>
                    </>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.witness_rel")}</label>
                    <select value={witnessApplicability} onChange={(e) => setWitnessApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")} className="w-full px-3 py-2 border rounded-md bg-background">
                      <option value="unknown">{t("analysis.custody_unknown")}</option>
                      <option value="applicable">{t("analysis.applicable")}</option>
                      <option value="not_applicable">{t("analysis.not_applicable")}</option>
                    </select>
                  </div>
                  {witnessApplicability === "applicable" && (
                    <>
                      <div>
                        <label className="text-sm font-medium mb-2 block">{t("analysis.witness_status")}</label>
                        <Input value={witnessStatus} onChange={(e) => setWitnessStatus(e.target.value)} placeholder="Available / hostile / unknown" />
                      </div>
                      <div>
                        <label className="text-sm font-medium mb-2 block">{t("analysis.witness_count")}</label>
                        <Input type="number" min={0} value={witnessCount} onChange={(e) => setWitnessCount(Number.parseInt(e.target.value, 10) || 0)} />
                      </div>
                    </>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.evidence_rel")}</label>
                    <select value={evidenceApplicability} onChange={(e) => setEvidenceApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")} className="w-full px-3 py-2 border rounded-md bg-background">
                      <option value="unknown">{t("analysis.custody_unknown")}</option>
                      <option value="applicable">{t("analysis.applicable")}</option>
                      <option value="not_applicable">{t("analysis.not_applicable")}</option>
                    </select>
                  </div>
                  {evidenceApplicability === "applicable" && (
                    <div>
                      <label className="text-sm font-medium mb-2 block">{t("analysis.evidence_summary")}</label>
                      <Textarea value={evidenceSummary} onChange={(e) => setEvidenceSummary(e.target.value)} placeholder="CCTV, medico-legal report, screenshots, call logs, receipts, photos, etc." rows={3} />
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.doc_rel")}</label>
                    <select value={documentsApplicability} onChange={(e) => setDocumentsApplicability(e.target.value as "applicable" | "not_applicable" | "unknown")} className="w-full px-3 py-2 border rounded-md bg-background">
                      <option value="unknown">{t("analysis.custody_unknown")}</option>
                      <option value="applicable">{t("analysis.applicable")}</option>
                      <option value="not_applicable">{t("analysis.not_applicable")}</option>
                    </select>
                  </div>
                  {documentsApplicability === "applicable" && (
                    <div>
                      <label className="text-sm font-medium mb-2 block">{t("analysis.avail_docs")}</label>
                      <Textarea value={availableDocuments} onChange={(e) => setAvailableDocuments(e.target.value)} placeholder="FIR copy, notices, medical reports, arrest memo, court orders" rows={2} />
                    </div>
                  )}
                  <div>
                    <label className="text-sm font-medium mb-2 block">{t("analysis.desired_outcome")}</label>
                    <Input value={desiredOutcome} onChange={(e) => setDesiredOutcome(e.target.value)} placeholder={t("analysis.desired_ph")} />
                  </div>
                  <label className="flex items-center gap-2 text-sm font-medium mt-1">
                    <input type="checkbox" checked={childInvolved} onChange={(e) => setChildInvolved(e.target.checked)} className="w-4 h-4" />
                    {t("analysis.child_involved")}
                  </label>
                </div>
              </Card>

              <Card className="p-6 border border-border/50">
                <h2 className="text-xl font-bold mb-4">{t("analysis.run")}</h2>
                <div className="space-y-4">
                  <Button onClick={handleRunFullAnalysis} disabled={onboardingLoading || loading || caseDescription.trim().length < 20} className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground">
                    {onboardingLoading ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{t("analysis.preparing")}</>
                    ) : loading ? (
                      <><Loader2 className="w-4 h-4 mr-2 animate-spin" />{t("analysis.generating")}</>
                    ) : (
                      <><Brain className="w-4 h-4 mr-2" />{t("analysis.generate")}</>
                    )}
                  </Button>
                  {onboardingProfile && (
                    <p className="text-xs text-muted-foreground">
                      Summary was auto-prepared before analysis. You can edit fields and run again anytime.
                    </p>
                  )}
                  <Button variant="outline" onClick={() => { setOnboardingProfile(null); setResults(null) }} className="w-full">
                    {t("analysis.reset")}
                  </Button>
                  <p className="text-xs text-muted-foreground">
                    One click now runs both steps: summary preparation and full legal analysis.
                  </p>
                </div>
              </Card>
            </div>

            {/* Results */}
            <div className="lg:col-span-2 space-y-6">
              {onboardingProfile && (
                <Card className="p-6 border border-border/50 bg-gradient-to-br from-card to-card/80">
                  <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-primary" />
                    {t("analysis.prepared_summary")}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-3">{onboardingProfile.one_paragraph_summary}</p>
                </Card>
              )}
              {error && (
                <Card className="p-6 border-destructive/50 bg-destructive/10">
                  <div className="flex items-center gap-2 text-destructive">
                    <XCircle className="w-5 h-5" />
                    <p className="font-semibold">Error: {error}</p>
                  </div>
                </Card>
              )}

              {results && (
                <>
                  <Card className="p-6 border border-border/50 bg-gradient-to-br from-card to-card/80">
                    <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
                      <BarChart3 className="w-6 h-6 text-primary" />
                      {t("analysis.case_summary_result")}
                    </h2>
                    <p className="text-sm text-muted-foreground mb-4">{results.summary}</p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className={`p-4 rounded-lg border ${getRiskBg(results.risk_score)}`}>
                        <p className="text-sm text-muted-foreground mb-1">{t("analysis.risk_score")}</p>
                        <p className={`text-3xl font-bold ${getRiskColor(results.risk_score)}`}>{results.risk_score}%</p>
                        <p className="text-xs text-muted-foreground mt-1">{results.risk_level} {t("analysis.risk")}</p>
                      </div>
                      <div className="p-4 rounded-lg border border-border/50 bg-card">
                        <p className="text-sm text-muted-foreground mb-1">{t("analysis.case_type_result")}</p>
                        <p className="text-lg font-semibold text-foreground">{results.likely_case_type}</p>
                      </div>
                      <div className="p-4 rounded-lg border border-border/50 bg-card">
                        <p className="text-sm text-muted-foreground mb-1">{t("analysis.sections")}</p>
                        <p className="text-sm font-semibold text-foreground">
                          {results.extracted_sections.length > 0 ? results.extracted_sections.join(", ") : "Not clearly identified"}
                        </p>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-6 border border-border/50">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <Lightbulb className="w-5 h-5 text-primary" />
                      {t("analysis.recommendations")}
                    </h3>
                    <ul className="space-y-2">
                      {results.recommendations.map((rec, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{rec}</p>
                        </li>
                      ))}
                    </ul>
                  </Card>

                  <Card className="p-6 border border-border/50">
                    <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-primary" />
                      {t("analysis.next_steps")}
                    </h3>
                    <ul className="space-y-2">
                      {results.next_steps.map((step, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <CheckCircle2 className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{step}</p>
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs text-muted-foreground mt-4">{results.disclaimer}</p>
                  </Card>
                </>
              )}

              {!results && !error && (
                <Card className="p-12 text-center border border-border/50">
                  <Brain className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                  <p className="text-muted-foreground">{t("analysis.click_hint")}</p>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

