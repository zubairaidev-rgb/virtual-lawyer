"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import {
  FileText,
  Download,
  Plus,
  Copy,
  Trash2,
  Eye,
  Upload,
  Brain,
  FileQuestion,
  FileCheck,
  FileSearch,
  Loader2,
  X,
  CheckCircle2,
  AlertCircle,
  Sparkles,
  FileEdit,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import {
  uploadDocument,
  listUserDocuments,
  listTemplates,
  extractFacts,
  getSummary,
  askQuestion,
  generateDocument,
  analyzeAndGenerate,
  suggestDocumentType,
  getTemplateDetails,
  type TemplateInfo,
} from "@/lib/services/documents"
import { getDocumentApiRole } from "@/lib/auth-user"
import { useLanguage } from "@/lib/language"

interface UploadedDocument {
  doc_id: string
  file_name: string
  chunks_count: number
  text_length: number
  status: string
  uploaded_at?: string
  is_sample?: boolean
}

interface GeneratedDocument {
  id: string
  name: string
  template_id: string
  template_name?: string
  output_path?: string
  created_at: string
  status: "Ready" | "Draft"
}

export default function DocumentsPage() {
  const { t } = useLanguage()
  const [isLoaded, setIsLoaded] = useState(false)
  const [activeTab, setActiveTab] = useState<"uploaded" | "generated" | "templates" | "analyze">("uploaded")
  
  // Document states
  const [uploadedDocs, setUploadedDocs] = useState<UploadedDocument[]>([])
  const [generatedDocs, setGeneratedDocs] = useState<GeneratedDocument[]>([])
  const [templates, setTemplates] = useState<TemplateInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Upload state
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(false)
  
  // Analysis state
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)
  const [docFacts, setDocFacts] = useState<any>(null)
  const [docSummary, setDocSummary] = useState<string | null>(null)
  const [docQuestion, setDocQuestion] = useState("")
  const [docAnswer, setDocAnswer] = useState<any>(null)
  
  // Generation state
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const [templateDetails, setTemplateDetails] = useState<any>(null)
  const [templateData, setTemplateData] = useState<Record<string, string>>({})
  const [templateDataJson, setTemplateDataJson] = useState<string>("")
  const [jsonError, setJsonError] = useState<string | null>(null)
  const [generateWithAI, setGenerateWithAI] = useState(true)
  
  // Suggestion state
  const [suggestionFacts, setSuggestionFacts] = useState<Record<string, string>>({})
  const [suggestions, setSuggestions] = useState<any[]>([])

  const getSessionEmail = (): string | undefined => {
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem("user") : null
      if (!raw) return undefined
      const u = JSON.parse(raw) as { email?: string }
      return u.email
    } catch {
      return undefined
    }
  }

  const loadUploadedDocs = async () => {
    try {
      const email = getSessionEmail()
      const res = await listUserDocuments(email, getDocumentApiRole("citizen"))
      setUploadedDocs(
        res.documents.map((d) => ({
          doc_id: d.doc_id,
          file_name: d.file_name,
          chunks_count: d.chunks_count,
          text_length: d.text_length,
          status: d.status,
          uploaded_at: d.uploaded_at,
          is_sample: d.is_sample,
        }))
      )
    } catch (err) {
      console.error("Failed to load documents:", err)
    }
  }

  useEffect(() => {
    setIsLoaded(true)
    loadTemplates()
    void loadUploadedDocs()
  }, [language])

  const loadTemplates = async () => {
    try {
      const templatesList = await listTemplates(undefined, language)
      setTemplates(templatesList)
    } catch (err: any) {
      console.error("Failed to load templates:", err)
    }
  }

  const handleFileUpload = async () => {
    if (!uploadFile) return

    setUploadProgress(true)
    setError(null)

    try {
      const email = getSessionEmail()
      await uploadDocument(uploadFile, {
        email,
        role: getDocumentApiRole("citizen"),
      })
      await loadUploadedDocs()
      setUploadFile(null)
      setActiveTab("uploaded")
    } catch (err: any) {
      setError(err.message || "Upload failed")
    } finally {
      setUploadProgress(false)
    }
  }

  const handleExtractFacts = async (docId: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await extractFacts(docId)
      setDocFacts(result)
      setSelectedDoc(docId)
      setActiveTab("analyze")
    } catch (err: any) {
      setError(err.message || "Failed to extract facts")
    } finally {
      setLoading(false)
    }
  }

  const handleGetSummary = async (docId: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await getSummary(docId)
      setDocSummary(result.summary)
      setSelectedDoc(docId)
      setActiveTab("analyze")
    } catch (err: any) {
      setError(err.message || "Failed to get summary")
    } finally {
      setLoading(false)
    }
  }

  const handleAskQuestion = async (docId: string, question: string) => {
    if (!question.trim()) return

    setLoading(true)
    setError(null)
    try {
      const result = await askQuestion(docId, question)
      setDocAnswer(result)
      setSelectedDoc(docId)
      setActiveTab("analyze")
    } catch (err: any) {
      setError(err.message || "Failed to get answer")
    } finally {
      setLoading(false)
    }
  }

  const handleTemplateClick = async (templateId: string) => {
    if (!templateId || templateId.trim() === "") {
      setError("Invalid template selected")
      return
    }
    console.log("Loading template details for:", templateId)
    setSelectedTemplate(templateId)
    setLoading(true)
    setError(null)
    setJsonError(null)
    try {
      const details = await getTemplateDetails(templateId, language)
      console.log("Template details received:", details)
      setTemplateDetails(details)
      // Initialize with example data
      if (details.example_data) {
        const exampleJson = JSON.stringify(details.example_data, null, 2)
        setTemplateDataJson(exampleJson)
        setTemplateData(details.example_data)
      } else {
        // If no example data, create empty structure
        const emptyData: Record<string, string> = {}
        if (details.placeholders) {
          details.placeholders.forEach((p: string) => {
            emptyData[p] = ""
          })
        }
        setTemplateDataJson(JSON.stringify(emptyData, null, 2))
        setTemplateData(emptyData)
      }
      // Scroll to the form
      setTimeout(() => {
        const formElement = document.getElementById("template-form")
        if (formElement) {
          formElement.scrollIntoView({ behavior: "smooth", block: "start" })
        }
      }, 100)
    } catch (err: any) {
      console.error("Error loading template details:", err)
      setError(err.message || "Failed to load template details")
      setSelectedTemplate(null)
      setTemplateDetails(null)
    } finally {
      setLoading(false)
    }
  }

  const handleJsonChange = (value: string) => {
    setTemplateDataJson(value)
    setJsonError(null)
    try {
      const parsed = JSON.parse(value)
      setTemplateData(parsed)
    } catch (err) {
      setJsonError("Invalid JSON format")
    }
  }

  const handleGenerateDocument = async () => {
    if (!selectedTemplate) {
      setError("Please select a template")
      return
    }

    setLoading(true)
    setError(null)
    try {
      // Convert form data to the format expected by backend
      // Remove empty values and ensure all keys are properly formatted
      const dataToSend: Record<string, string> = {}
      for (const [key, value] of Object.entries(templateData)) {
        if (value && String(value).trim() !== "") {
          dataToSend[key] = String(value).trim()
        }
      }
      
      console.log("Sending data to backend:", dataToSend)
      console.log("Template ID:", selectedTemplate)
      
      const result = await generateDocument(selectedTemplate, dataToSend, generateWithAI)

      console.log("Generation result:", result)

      // Check if document was generated successfully
      if (!result.output_path) {
        throw new Error("Document generation failed - no output file created")
      }

      // Add generated document to list
      setGeneratedDocs((prev) => [
        {
          id: Date.now().toString(),
          name: result.template_name || `Generated Document`,
          template_id: selectedTemplate,
          template_name: result.template_name,
          output_path: result.output_path,
          created_at: new Date().toISOString(),
          status: "Ready",
        },
        ...prev,
      ])

      setTemplateData({})
      setTemplateDataJson("")
      setTemplateDetails(null)
      setSelectedTemplate(null)
      setActiveTab("generated")
    } catch (err: any) {
      setError(err.message || "Failed to generate document")
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyzeAndGenerate = async (docId: string, templateId: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeAndGenerate(docId, templateId)
      setGeneratedDocs((prev) => [
        {
          id: Date.now().toString(),
          name: `Generated from ${docId}`,
          template_id: templateId,
          created_at: new Date().toISOString(),
          status: "Ready",
        },
        ...prev,
      ])
      setActiveTab("generated")
    } catch (err: any) {
      setError(err.message || "Failed to analyze and generate")
    } finally {
      setLoading(false)
    }
  }

  const handleSuggestDocumentType = async () => {
    if (Object.keys(suggestionFacts).length === 0) {
      setError("Please enter case facts")
      return
    }

    setLoading(true)
    setError(null)
    try {
      const result = await suggestDocumentType(suggestionFacts)
      setSuggestions(result.suggestions || [])
      setActiveTab("templates")
    } catch (err: any) {
      setError(err.message || "Failed to get suggestions")
    } finally {
      setLoading(false)
    }
  }

  const stats = {
    total: uploadedDocs.length + generatedDocs.length,
    uploaded: uploadedDocs.length,
    generated: generatedDocs.length,
    ready: generatedDocs.filter((d) => d.status === "Ready").length,
  }

  return (
    <div className="flex">
      <Sidebar userType="citizen" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-accent/5">
        <div className="fixed inset-0 ml-64 -z-10">
          <div className="absolute top-20 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl opacity-20 animate-float"></div>
          <div
            className="absolute bottom-0 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-20 animate-float"
            style={{ animationDelay: "1s" }}
          ></div>
        </div>

        <div className="p-8">
          {/* Header */}
          <div
            className={`mb-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
          >
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div>
                <h1 className="text-4xl font-bold text-foreground mb-2">{t("docs.title")}</h1>
                <p className="text-muted-foreground">{t("docs.subtitle")}</p>
              </div>
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={() => setActiveTab("templates")}
                  className="bg-card/50 backdrop-blur border-border/50"
                >
                  <FileSearch className="w-4 h-4 mr-2" />
                  {t("docs.browse_templates")}
                </Button>
                <Button
                  onClick={() => setActiveTab("uploaded")}
                  className="gradient-primary text-primary-foreground border-0"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  {t("docs.upload_btn")}
                </Button>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div
            className={`grid grid-cols-1 md:grid-cols-4 gap-6 mb-8 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "100ms" }}
          >
            {[
              { labelKey: "docs.total", value: stats.total, icon: FileText, color: "from-primary to-accent" },
              { labelKey: "docs.uploaded", value: stats.uploaded, icon: Upload, color: "from-accent to-secondary" },
              { labelKey: "docs.generated", value: stats.generated, icon: FileEdit, color: "from-secondary to-primary" },
              { labelKey: "docs.ready", value: stats.ready, icon: CheckCircle2, color: "from-primary to-accent" },
            ].map((stat, i) => (
              <Card
                key={i}
                className="p-6 border border-border/50 hover:border-primary/50 transition-all group cursor-pointer"
                style={{
                  animation: `fadeInUp 0.6s ease-out ${i * 100}ms forwards`,
                  opacity: 0,
                }}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{t(stat.labelKey)}</p>
                    <p className="text-3xl font-bold text-foreground mt-2">{stat.value}</p>
                  </div>
                  <div
                    className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}
                  >
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Error Display */}
          {error && (
            <Card className="p-4 mb-6 border-destructive/50 bg-destructive/10">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <p className="font-semibold">{error}</p>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setError(null)}
                  className="ml-auto"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </Card>
          )}

          {/* Tabs */}
          <div className="mb-6 flex gap-2 border-b border-border/50">
            {[
              { id: "uploaded", labelKey: "docs.tab_uploaded", icon: Upload },
              { id: "generated", labelKey: "docs.tab_generated", icon: FileEdit },
              { id: "templates", labelKey: "docs.tab_templates", icon: FileText },
              { id: "analyze", labelKey: "docs.tab_analyze", icon: Brain },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 flex items-center gap-2 border-b-2 transition-all ${
                  activeTab === tab.id
                    ? "border-primary text-primary font-semibold"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {t(tab.labelKey)}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="transition-all duration-300">
            {/* Uploaded Documents Tab */}
            {activeTab === "uploaded" && (
              <div className="space-y-6">
                {/* Upload Section */}
                <Card className="p-6 border border-border/50">
                  <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Upload className="w-5 h-5 text-primary" />
                    {t("docs.upload_section")}
                  </h2>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">{t("docs.select_file")}</label>
                      <Input
                        type="file"
                        accept=".pdf,.docx"
                        onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                        className="w-full"
                      />
                      {uploadFile && (
                        <p className="text-sm text-muted-foreground mt-2">Selected: {uploadFile.name}</p>
                      )}
                    </div>
                    <Button
                      onClick={handleFileUpload}
                      disabled={!uploadFile || uploadProgress}
                      className="bg-gradient-to-r from-primary to-accent text-primary-foreground"
                    >
                      {uploadProgress ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Uploading...
                        </>
                      ) : (
                        <>
                          <Upload className="w-4 h-4 mr-2" />
                          {t("docs.upload_btn")}
                        </>
                      )}
                    </Button>
                  </div>
                </Card>

                {/* Uploaded Documents List */}
                <div className="space-y-4">
                  {uploadedDocs.length === 0 ? (
                    <Card className="p-12 text-center border border-border/50">
                      <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                      <p className="text-muted-foreground">{t("docs.none_uploaded")}</p>
                    </Card>
                  ) : (
                    uploadedDocs.map((doc, idx) => (
                      <Card
                        key={doc.doc_id}
                        className="p-6 border border-border/50 hover:border-primary/50 hover:shadow-lg transition-all group"
                        style={{
                          animation: `fadeInUp 0.6s ease-out ${idx * 100}ms forwards`,
                          opacity: 0,
                        }}
                      >
                        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                          <div className="flex gap-4 flex-1">
                            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg flex-shrink-0">
                              <FileText className="w-7 h-7 text-white" />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-semibold text-foreground text-lg">{doc.file_name}</h3>
                              <div className="flex gap-4 mt-2 text-sm text-muted-foreground flex-wrap">
                                <span>ID: {doc.doc_id}</span>
                                <span>•</span>
                                <span>{doc.chunks_count} chunks</span>
                                <span>•</span>
                                <span>{doc.text_length} characters</span>
                                {doc.uploaded_at && (
                                  <>
                                    <span>•</span>
                                    <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                                  </>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-3 flex-wrap">
                            <Badge className="bg-primary/10 text-primary">{doc.status}</Badge>
                            <div className="flex gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setSelectedDoc(doc.doc_id)
                                  setActiveTab("analyze")
                                }}
                                className="bg-transparent hover:bg-primary/10"
                              >
                                <Brain className="w-4 h-4 mr-2" />
                                Analyze
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleExtractFacts(doc.doc_id)}
                                className="bg-transparent hover:bg-primary/10"
                              >
                                <FileCheck className="w-4 h-4 mr-2" />
                                Extract Facts
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleGetSummary(doc.doc_id)}
                                className="bg-transparent hover:bg-primary/10"
                              >
                                <FileSearch className="w-4 h-4 mr-2" />
                                Summary
                              </Button>
                            </div>
                          </div>
                        </div>
                      </Card>
                    ))
                  )}
                </div>
              </div>
            )}

            {/* Generated Documents Tab */}
            {activeTab === "generated" && (
              <div className="space-y-4">
                {generatedDocs.length === 0 ? (
                  <Card className="p-12 text-center border border-border/50">
                    <FileEdit className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                    <p className="text-muted-foreground mb-4">{t("docs.none_generated")}</p>
                    <Button
                      onClick={() => setActiveTab("templates")}
                      className="gradient-primary text-primary-foreground"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Generate Document
                    </Button>
                  </Card>
                ) : (
                  generatedDocs.map((doc, idx) => (
                    <Card
                      key={doc.id}
                      className="p-6 border border-border/50 hover:border-primary/50 hover:shadow-lg transition-all"
                      style={{
                        animation: `fadeInUp 0.6s ease-out ${idx * 100}ms forwards`,
                        opacity: 0,
                      }}
                    >
                      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                        <div className="flex gap-4 flex-1">
                          <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-accent to-secondary flex items-center justify-center shadow-lg flex-shrink-0">
                            <FileEdit className="w-7 h-7 text-white" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-foreground text-lg">{doc.name}</h3>
                            <div className="flex gap-4 mt-2 text-sm text-muted-foreground flex-wrap">
                              <span>Template: {doc.template_name || doc.template_id}</span>
                              <span>•</span>
                              <span>{new Date(doc.created_at).toLocaleDateString()}</span>
                              {doc.output_path && (
                                <>
                                  <span>•</span>
                                  <span className="text-primary">Ready to download</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <Badge
                            className={
                              doc.status === "Ready"
                                ? "bg-primary/10 text-primary"
                                : "bg-muted/10 text-muted-foreground"
                            }
                          >
                            {doc.status}
                          </Badge>
                          <div className="flex gap-2">
                            {doc.output_path && (
                              <>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  className="bg-transparent hover:bg-primary/10 border-2"
                                  onClick={() => {
                                    const filename = doc.output_path?.split('/').pop() || doc.output_path?.split('\\').pop()
                                    if (filename) {
                                      const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/document/download/${encodeURIComponent(filename)}?format=docx`
                                      const link = document.createElement('a')
                                      link.href = url
                                      link.download = filename
                                      document.body.appendChild(link)
                                      link.click()
                                      document.body.removeChild(link)
                                    }
                                  }}
                                  title="Download as DOCX"
                                >
                                  <FileText className="w-4 h-4 mr-2" />
                                  DOCX
                                </Button>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </Card>
                  ))
                )}
              </div>
            )}

            {/* Templates Tab */}
            {activeTab === "templates" && (
              <div className="space-y-6">
                {/* Document Type Suggestion */}
                <Card className="p-6 border border-border/50">
                  <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-primary" />
                    {t("docs.ai_suggest")}
                  </h2>
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium mb-2 block">{t("docs.enter_facts")}</label>
                      <Textarea
                        value={JSON.stringify(suggestionFacts, null, 2)}
                        onChange={(e) => {
                          try {
                            setSuggestionFacts(JSON.parse(e.target.value))
                          } catch {
                            // Allow partial JSON
                          }
                        }}
                        placeholder='{"case_type": "bail", "section": "302", "status": "pending"}'
                        rows={4}
                        className="w-full font-mono text-sm"
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Enter case facts to get AI-powered document type suggestions
                      </p>
                    </div>
                    <Button
                      onClick={handleSuggestDocumentType}
                      disabled={loading || Object.keys(suggestionFacts).length === 0}
                      className="bg-gradient-to-r from-primary to-accent text-primary-foreground"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Getting Suggestions...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          {t("docs.get_suggestions")}
                        </>
                      )}
                    </Button>
                  </div>
                </Card>

                {/* Suggestions Display */}
                {suggestions.length > 0 && (
                  <Card className="p-6 border border-primary/50 bg-primary/5">
                    <h3 className="font-semibold mb-4">Suggested Document Types:</h3>
                    <div className="space-y-2">
                      {suggestions.map((suggestion, i) => (
                        <div
                          key={i}
                          className="p-4 border border-border/50 rounded-lg hover:border-primary/50 transition-all cursor-pointer"
                          onClick={() => {
                            const templateId = suggestion.template_id || suggestion.id || ""
                            if (templateId) {
                              handleTemplateClick(templateId)
                              setActiveTab("templates")
                            }
                          }}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-semibold">{suggestion.name}</p>
                              <p className="text-sm text-muted-foreground">{suggestion.reason}</p>
                            </div>
                            <Badge className="bg-primary/10 text-primary">
                              {Math.round(suggestion.relevance_score * 100)}% match
                            </Badge>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                )}

                {/* Templates List */}
                <div>
                  <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    {t("docs.available_templates")}
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {templates.length === 0 ? (
                      <Card className="p-12 text-center border border-border/50 col-span-full">
                        <FileText className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                        <p className="text-muted-foreground">Loading templates...</p>
                      </Card>
                    ) : (
                      templates.map((template) => (
                        <Card
                          key={template.id || template.template_id}
                          className={`p-6 border transition-all cursor-pointer ${
                            selectedTemplate === (template.id || template.template_id)
                              ? "border-primary bg-primary/5 shadow-lg"
                              : "border-border/50 hover:border-primary/50 hover:shadow-md"
                          }`}
                          onClick={() => {
                            const templateId = template.id || template.template_id || ""
                            if (templateId) {
                              handleTemplateClick(templateId)
                            }
                          }}
                        >
                          <div className="flex items-start justify-between mb-3">
                            <FileText className="w-8 h-8 text-primary" />
                            {selectedTemplate === (template.id || template.template_id) && (
                              <CheckCircle2 className="w-5 h-5 text-primary" />
                            )}
                          </div>
                          <h3 className="font-semibold text-foreground mb-2">
                            {template.name || template.id || template.template_id}
                          </h3>
                          {template.category && (
                            <Badge className="mb-2 bg-accent/10 text-accent">
                              {template.category}
                            </Badge>
                          )}
                          {(template.placeholder_count || (template.placeholders && template.placeholders.length)) && (
                            <p className="text-xs text-muted-foreground">
                              {template.placeholder_count || template.placeholders.length} {t("docs.fields_required")}
                            </p>
                          )}
                        </Card>
                      ))
                    )}
                  </div>
                </div>

                {/* Template Data Form */}
                {selectedTemplate && templateDetails && (
                  <Card id="template-form" className="p-6 border border-primary/50 bg-primary/5 mt-6">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h3 className="text-xl font-bold mb-1">{templateDetails.name || selectedTemplate}</h3>
                        <p className="text-sm text-muted-foreground">
                          Fill in the required information below. Edit the JSON directly or use the form fields.
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedTemplate(null)
                          setTemplateDetails(null)
                          setTemplateData({})
                          setTemplateDataJson("")
                        }}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>

                    {/* Template Info */}
                    <div className="mb-6 p-4 bg-muted/50 rounded-lg">
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Category:</span>
                          <span className="ml-2 font-medium">{templateDetails.category || "General"}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Required Fields:</span>
                          <span className="ml-2 font-medium">{templateDetails.total_placeholders}</span>
                        </div>
                      </div>
                    </div>

                    {/* Placeholder Descriptions */}
                    {templateDetails.placeholders && templateDetails.placeholders.length > 0 ? (
                      <div className="mb-6">
                        <h4 className="font-semibold mb-3 flex items-center gap-2">
                          <FileCheck className="w-4 h-4" />
                          {t("docs.req_info")}
                        </h4>
                        <div className="space-y-2 max-h-48 overflow-y-auto">
                          {templateDetails.placeholders.map((placeholder: string) => {
                            const desc = templateDetails.placeholder_descriptions?.[placeholder]
                            const displayLabel = desc?.label || desc?.original_name || placeholder
                            return (
                              <div
                                key={placeholder}
                                className="p-3 bg-background rounded-lg border border-border/50"
                              >
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2">
                                      <span className="font-medium text-sm">{displayLabel}</span>
                                      {desc?.required && (
                                        <Badge variant="destructive" className="text-xs">{t("docs.required")}</Badge>
                                      )}
                                    </div>
                                    {desc?.description && (
                                      <p className="text-xs text-muted-foreground mt-1">
                                        {desc.description}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    ) : (
                      <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                        <p className="text-sm text-yellow-800 dark:text-yellow-200">
                          <AlertCircle className="w-4 h-4 inline mr-2" />
                          No placeholders detected in this template. You can still generate the document with custom data.
                        </p>
                      </div>
                    )}

                    {/* User-Friendly Form */}
                    <div className="mb-6">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-semibold flex items-center gap-2">
                          <FileEdit className="w-4 h-4" />
                          {t("docs.fill_info")}
                        </h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            // Reset to example data
                            setTemplateData(templateDetails.example_data || {})
                            setTemplateDataJson(JSON.stringify(templateDetails.example_data || {}, null, 2))
                            setJsonError(null)
                          }}
                        >
                          {t("docs.reset_form")}
                        </Button>
                      </div>
                      
                      <div className="space-y-4">
                        {templateDetails.placeholders && templateDetails.placeholders.length > 0 ? (
                          templateDetails.placeholders.map((placeholderKey: string) => {
                            const desc = templateDetails.placeholder_descriptions?.[placeholderKey]
                            const displayLabel = desc?.label || desc?.original_name || placeholderKey
                            const fieldType = desc?.type || "text"
                            const isRequired = desc?.required || false
                            const currentValue = templateData[placeholderKey] || ""
                            const examplePlaceholder = desc?.example || (language === "ur" ? `${displayLabel} درج کریں` : `Enter ${displayLabel.toLowerCase()}`)

                            return (
                              <div key={placeholderKey} className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                  {displayLabel}
                                  {isRequired && (
                                    <Badge variant="destructive" className="text-xs">{t("docs.required")}</Badge>
                                  )}
                                </label>
                                {desc?.description && (
                                  <p className="text-xs text-muted-foreground -mt-1">
                                    {desc.description}
                                  </p>
                                )}
                                {fieldType === "textarea" ? (
                                  <Textarea
                                    value={currentValue}
                                    onChange={(e) => {
                                      const newData = { ...templateData, [placeholderKey]: e.target.value }
                                      setTemplateData(newData)
                                      setTemplateDataJson(JSON.stringify(newData, null, 2))
                                    }}
                                    placeholder={examplePlaceholder}
                                    rows={4}
                                    className="w-full border-2 border-border focus:border-primary transition-colors"
                                  />
                                ) : (
                                  <Input
                                    type={fieldType === "date" ? "date" : fieldType === "email" ? "email" : fieldType === "tel" ? "tel" : "text"}
                                    value={currentValue}
                                    onChange={(e) => {
                                      const newData = { ...templateData, [placeholderKey]: e.target.value }
                                      setTemplateData(newData)
                                      setTemplateDataJson(JSON.stringify(newData, null, 2))
                                    }}
                                    placeholder={examplePlaceholder}
                                    className="w-full border-2 border-border focus:border-primary transition-colors"
                                    required={isRequired}
                                  />
                                )}
                              </div>
                            )
                          })
                        ) : (
                          <div className="p-4 bg-muted/50 rounded-lg">
                            <p className="text-sm text-muted-foreground">
                              No specific fields required. You can generate the document with default values.
                            </p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Options */}
                    <div className="mb-6">
                      <div className="flex items-center gap-2 p-3 bg-muted/30 rounded-lg">
                        <input
                          type="checkbox"
                          id="generateWithAI"
                          checked={generateWithAI}
                          onChange={(e) => setGenerateWithAI(e.target.checked)}
                          className="w-4 h-4"
                        />
                        <label htmlFor="generateWithAI" className="text-sm cursor-pointer flex-1">
                          <span className="font-medium">Generate AI-powered sections</span>
                          <span className="text-muted-foreground ml-2">
                            (Auto-generate case brief, arguments, grounds, etc. if not provided)
                          </span>
                        </label>
                      </div>
                    </div>

                    {/* Generate Button */}
                    <Button
                      onClick={handleGenerateDocument}
                      disabled={loading || Object.keys(templateData).length === 0}
                      className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground"
                      size="lg"
                    >
                      {loading ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          {t("docs.generating")}
                        </>
                      ) : (
                        <>
                          <FileEdit className="w-4 h-4 mr-2" />
                          {t("docs.generate")}
                        </>
                      )}
                    </Button>
                  </Card>
                )}
              </div>
            )}

            {/* Analyze Document Tab */}
            {activeTab === "analyze" && (
              <div className="space-y-6">
                {!selectedDoc ? (
                  <Card className="p-12 text-center border border-border/50">
                    <Brain className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
                    <p className="text-muted-foreground">Select a document to analyze</p>
                    <Button
                      onClick={() => setActiveTab("uploaded")}
                      className="mt-4 gradient-primary text-primary-foreground"
                    >
                      Go to Uploaded Documents
                    </Button>
                  </Card>
                ) : (
                  <>
                    {/* Document Info */}
                    <Card className="p-6 border border-border/50">
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-bold flex items-center gap-2">
                          <Brain className="w-5 h-5 text-primary" />
                          Analyzing: {uploadedDocs.find((d) => d.doc_id === selectedDoc)?.file_name || selectedDoc}
                        </h2>
                        <Button
                          variant="outline"
                          onClick={() => {
                            setSelectedDoc(null)
                            setDocFacts(null)
                            setDocSummary(null)
                            setDocAnswer(null)
                          }}
                        >
                          <X className="w-4 h-4 mr-2" />
                          Close
                        </Button>
                      </div>
                    </Card>

                    {/* Question Answering */}
                    <Card className="p-6 border border-border/50">
                      <h3 className="font-semibold mb-4 flex items-center gap-2">
                        <FileQuestion className="w-5 h-5 text-primary" />
                        Ask Question About Document
                      </h3>
                      <div className="space-y-4">
                        <Textarea
                          value={docQuestion}
                          onChange={(e) => setDocQuestion(e.target.value)}
                          placeholder="Ask a question about the document..."
                          rows={3}
                        />
                        <Button
                          onClick={() => handleAskQuestion(selectedDoc, docQuestion)}
                          disabled={loading || !docQuestion.trim()}
                          className="bg-gradient-to-r from-primary to-accent text-primary-foreground"
                        >
                          {loading ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Analyzing...
                            </>
                          ) : (
                            <>
                              <Brain className="w-4 h-4 mr-2" />
                              Ask Question
                            </>
                          )}
                        </Button>
                        {docAnswer && (
                          <div className="p-4 bg-muted/50 rounded-lg">
                            <p className="font-semibold mb-2">Answer:</p>
                            <p className="text-sm">{docAnswer.answer}</p>
                            {docAnswer.confidence && (
                              <p className="text-xs text-muted-foreground mt-2">
                                Confidence: {Math.round(docAnswer.confidence * 100)}%
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    </Card>

                    {/* Extracted Facts */}
                    {docFacts && (
                      <Card className="p-6 border border-border/50">
                        <h3 className="font-semibold mb-4 flex items-center gap-2">
                          <FileCheck className="w-5 h-5 text-primary" />
                          Extracted Facts
                        </h3>
                        <div className="space-y-2">
                          {Object.entries(docFacts.facts || {}).map(([key, value]) => (
                            <div key={key} className="p-3 bg-muted/50 rounded-lg">
                              <p className="font-medium text-sm">{key}:</p>
                              <p className="text-sm text-muted-foreground">{String(value)}</p>
                            </div>
                          ))}
                        </div>
                        {docFacts.summary && (
                          <div className="mt-4 p-4 bg-primary/10 rounded-lg">
                            <p className="font-semibold mb-2">Summary:</p>
                            <p className="text-sm">{docFacts.summary}</p>
                          </div>
                        )}
                      </Card>
                    )}

                    {/* Document Summary */}
                    {docSummary && (
                      <Card className="p-6 border border-border/50">
                        <h3 className="font-semibold mb-4 flex items-center gap-2">
                          <FileSearch className="w-5 h-5 text-primary" />
                          Document Summary
                        </h3>
                        <div className="p-4 bg-muted/50 rounded-lg">
                          <p className="text-sm whitespace-pre-wrap">{docSummary}</p>
                        </div>
                      </Card>
                    )}

                    {/* Quick Actions */}
                    <Card className="p-6 border border-border/50">
                      <h3 className="font-semibold mb-4">Quick Actions</h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <Button
                          variant="outline"
                          onClick={() => handleExtractFacts(selectedDoc)}
                          disabled={loading}
                          className="w-full"
                        >
                          <FileCheck className="w-4 h-4 mr-2" />
                          Extract Facts
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => handleGetSummary(selectedDoc)}
                          disabled={loading}
                          className="w-full"
                        >
                          <FileSearch className="w-4 h-4 mr-2" />
                          Get Summary
                        </Button>
                        <Button
                          variant="outline"
                          onClick={() => {
                            if (selectedTemplate) {
                              handleAnalyzeAndGenerate(selectedDoc, selectedTemplate)
                            } else {
                              setActiveTab("templates")
                            }
                          }}
                          disabled={loading || !selectedTemplate}
                          className="w-full"
                        >
                          <Sparkles className="w-4 h-4 mr-2" />
                          Generate Document
                        </Button>
                      </div>
                    </Card>
                  </>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
