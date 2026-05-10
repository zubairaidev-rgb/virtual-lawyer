"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Send,
  Loader2,
  MessageCircle,
  Lightbulb,
  Copy,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
  BookOpen,
  AlertCircle,
  CheckCircle2,
} from "lucide-react"
import { sendChat } from "@/lib/services/chat"
import { useLanguage } from "@/lib/language"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  helpful?: boolean
  sources?: string[]
}

const LAWYER_CHAT_STORAGE_KEY = "lawmate_chat_lawyer_v1"
const LAWYER_CHAT_SESSION_KEY = "lawmate_chat_lawyer_session_v1"

export default function LawyerChatbotPage() {
  const { language, t } = useLanguage()

  const getWelcomeMessage = (): Message => ({
    id: "1",
    role: "assistant",
    content: language === "ur"
      ? "میں آپ کے قانونی کام میں مدد کے لیے یہاں ہوں۔ سادہ زبان میں پوچھیں، اور میں عملی قانونی تجزیہ اور حکمت عملی فراہم کروں گا۔"
      : "I'm here to support your legal workflow. Ask in plain language, and I will provide practical legal analysis and strategy guidance.",
    timestamp: new Date(),
    sources: [],
  })

  const [messages, setMessages] = useState<Message[]>([getWelcomeMessage()])

  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState("")
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    if (typeof window === "undefined") return
    try {
      const raw = localStorage.getItem(LAWYER_CHAT_STORAGE_KEY)
      if (!raw) return
      const parsed = JSON.parse(raw) as Array<{
        id: string
        role: "user" | "assistant"
        content: string
        timestamp: string
        helpful?: boolean
        sources?: string[]
      }>
      if (!Array.isArray(parsed) || parsed.length === 0) return
      const restored = parsed.map((m) => ({
        ...m,
        timestamp: new Date(m.timestamp),
      }))
      setMessages(restored)
    } catch (error) {
      console.warn("Failed to restore lawyer chat history:", error)
    }
  }, [])

  useEffect(() => {
    setMessages((prev) => {
      if (prev.length === 1 && prev[0].id === "1") {
        return [getWelcomeMessage()]
      }
      return prev
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [language])

  useEffect(() => {
    if (typeof window === "undefined") return
    try {
      let sid = localStorage.getItem(LAWYER_CHAT_SESSION_KEY) || ""
      if (!sid) {
        sid = `lawyer-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
        localStorage.setItem(LAWYER_CHAT_SESSION_KEY, sid)
      }
      setSessionId(sid)
    } catch (error) {
      console.warn("Failed to init lawyer chat session:", error)
    }
  }, [])

  useEffect(() => {
    if (typeof window === "undefined") return
    try {
      localStorage.setItem(
        LAWYER_CHAT_STORAGE_KEY,
        JSON.stringify(
          messages.map((m) => ({
            ...m,
            timestamp: m.timestamp.toISOString(),
          })),
        ),
      )
    } catch (error) {
      console.warn("Failed to persist lawyer chat history:", error)
    }
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      const history = messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .slice(-8)
        .map((m) => ({ role: m.role, content: m.content }))
      const userRaw = typeof window !== "undefined" ? localStorage.getItem("user") : null
      let userId = ""
      let userType = "lawyer"
      try {
        if (userRaw) {
          const parsed = JSON.parse(userRaw)
          userId = parsed?.id || ""
          userType = parsed?.userType || "lawyer"
        }
      } catch {
        // keep defaults
      }

      const res = await sendChat(input, false, history, {
        session_id: sessionId,
        user_id: userId,
        user_type: userType,
        language,
      })
      
      // Convert reference objects to display strings
      const formatReference = (ref: any): string => {
        if (typeof ref === 'string') return ref
        if (typeof ref === 'object' && ref !== null) {
          if (ref.type === 'PPC' && ref.section) {
            return `PPC Section ${ref.section}`
          }
          if (ref.type === 'Case Law' && ref.case_no) {
            return `Case ${ref.case_no}`
          }
          if (ref.type === 'CrPC' && ref.title) {
            return `CrPC: ${ref.title}`
          }
          if (ref.type === 'Constitution' && ref.title) {
            return `Constitution: ${ref.title}`
          }
          if (ref.title) {
            return ref.title
          }
          if (ref.source) {
            return ref.source
          }
          return `${ref.type || 'Reference'}`
        }
        return String(ref)
      }

      const sources = res.references && res.references.length > 0
        ? res.references.map(formatReference).filter(Boolean)
        : []

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: res.answer || "Sorry, I could not generate a response right now.",
        timestamp: new Date(),
        sources: sources,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (err: unknown) {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          err instanceof Error
            ? `Error contacting server: ${err.message}`
            : "Error contacting server.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleCopyMessage = (content: string, messageId: string) => {
    navigator.clipboard.writeText(content)
    setCopied(messageId)
    setTimeout(() => setCopied(null), 2000)
  }

  const handleSuggestion = (suggestion: string) => {
    setInput(suggestion)
  }

  const renderMessageContent = (content: string) => {
    const lines = content.split("\n")
    const items: React.ReactNode[] = []

    for (let i = 0; i < lines.length; i++) {
      const line = (lines[i] || "").trim()
      if (!line) {
        items.push(<div key={`sp-${i}`} className="h-2" />)
        continue
      }

      const isBullet = /^[-*•]\s+/.test(line)
      const isHeading = !isBullet && /:$/.test(line) && line.length <= 60

      if (isHeading) {
        items.push(
          <h4 key={`h-${i}`} className="font-semibold text-sm mt-3 mb-2">
            {line.replace(/:$/, "")}
          </h4>,
        )
      } else if (isBullet) {
        items.push(
          <div key={`b-${i}`} className="flex gap-2 text-sm leading-relaxed mb-1">
            <span className="mt-1.5 inline-block h-1.5 w-1.5 rounded-full bg-current opacity-80" />
            <span>{line.replace(/^[-*•]\s+/, "")}</span>
          </div>,
        )
      } else {
        items.push(
          <p key={`p-${i}`} className="text-sm leading-relaxed mb-2">
            {line}
          </p>,
        )
      }
    }

    return <div className="space-y-0.5">{items}</div>
  }

  return (
    <div className="flex">
      <Sidebar userType="lawyer" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex flex-col">
        <div className="border-b border-border/50 p-6 bg-gradient-to-r from-card/60 to-card/40 backdrop-blur sticky top-0 z-40 shadow-sm hover:shadow-md transition-all">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg animate-pulse-glow">
              <MessageCircle className="w-7 h-7 text-primary-foreground" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-foreground">{t("chat.title")}</h1>
                <div className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary/10 border border-primary/30">
                  <Sparkles className="w-3 h-3 text-primary" />
                  <span className="text-xs font-medium text-primary">{t("chat.ai_powered")}</span>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                {t("chat.subtitle")}
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-8 space-y-6 relative">
          <div className="absolute inset-0 -z-10">
            <div className="absolute top-0 right-0 w-96 h-96 bg-primary/8 rounded-full blur-3xl animate-float"></div>
            <div
              className="absolute bottom-0 left-0 w-96 h-96 bg-accent/8 rounded-full blur-3xl animate-float"
              style={{ animationDelay: "2s" }}
            ></div>
            <div className="absolute inset-0 bg-grid-pattern opacity-2"></div>
          </div>

          {messages.map((message, idx) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} animate-fadeInUp`}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className={`flex gap-3 max-w-2xl`}>
                {message.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 mt-1 shadow-lg">
                    <MessageCircle className="w-4 h-4 text-white" />
                  </div>
                )}
                <div className="group w-full">
                  <Card
                    className={`px-6 py-4 border transition-all duration-300 ${
                      message.role === "user"
                        ? "bg-gradient-to-br from-primary to-accent text-primary-foreground border-primary/50 rounded-3xl"
                        : "bg-card border-border/50 hover:border-primary/30 rounded-2xl"
                    }`}
                  >
                    {renderMessageContent(message.content)}

                    {message.role === "assistant" && message.sources && message.sources.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-border/50">
                        <p className="text-xs font-semibold text-muted-foreground mb-2 flex items-center gap-1">
                          <BookOpen className="w-3 h-3" />
                          Sources
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {message.sources.map((source, i) => (
                            <span
                              key={i}
                              className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full border border-primary/20"
                            >
                              {source}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <p
                      className={`text-xs mt-3 ${
                        message.role === "user" ? "opacity-70" : "text-muted-foreground"
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </p>
                  </Card>

                  {message.role === "assistant" && (
                    <div className="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 p-0 hover:bg-primary/10"
                        onClick={() => handleCopyMessage(message.content, message.id)}
                        title="Copy message"
                      >
                        {copied === message.id ? (
                          <CheckCircle2 className="w-3 h-3 text-primary" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 p-0 hover:bg-green-500/10"
                        onClick={() =>
                          setMessages((prev) => prev.map((m) => (m.id === message.id ? { ...m, helpful: true } : m)))
                        }
                        title="Helpful"
                      >
                        <ThumbsUp className="w-3 h-3" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 p-0 hover:bg-red-500/10"
                        onClick={() =>
                          setMessages((prev) => prev.map((m) => (m.id === message.id ? { ...m, helpful: false } : m)))
                        }
                        title="Not helpful"
                      >
                        <ThumbsDown className="w-3 h-3" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start animate-fadeInUp">
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center flex-shrink-0 shadow-lg">
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                </div>
                <Card className="px-6 py-4 border border-border/50 rounded-2xl">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      {[0, 1, 2].map((i) => (
                        <div
                          key={i}
                          className="w-2 h-2 bg-primary rounded-full animate-pulse"
                          style={{ animationDelay: `${i * 0.2}s` }}
                        ></div>
                      ))}
                    </div>
                    <span className="text-sm text-muted-foreground">{t("chat.thinking")}</span>
                  </div>
                </Card>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {messages.length === 1 && !loading && (
          <div className="px-8 py-6 bg-gradient-to-t from-card/40 to-transparent border-t border-border/30">
            <p className="text-xs font-semibold text-muted-foreground mb-4 flex items-center gap-1">
              <Lightbulb className="w-4 h-4" />
              {t("chat.suggested")}
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { text: "Bail strategy for PPC 380/457?", icon: AlertCircle },
                { text: "Key precedents for anticipatory bail", icon: CheckCircle2 },
                { text: "Cross-examination tips", icon: BookOpen },
                { text: "Remand objections checklist", icon: Sparkles },
              ].map((suggestion, i) => (
                <Button
                  key={i}
                  size="sm"
                  variant="outline"
                  className="text-xs h-auto py-2 px-3 bg-card/50 hover:bg-primary/10 border-border/50 hover:border-primary/50 transition-all group"
                  onClick={() => handleSuggestion(suggestion.text)}
                >
                  <suggestion.icon className="w-3 h-3 mr-1.5 group-hover:text-primary" />
                  {suggestion.text}
                </Button>
              ))}
            </div>
          </div>
        )}

        <div className="border-t border-border/50 bg-gradient-to-t from-card/80 to-card/40 backdrop-blur p-6 sticky bottom-0">
          <form onSubmit={handleSendMessage} className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("chat.placeholder_lawyer")}
              disabled={loading}
              className="flex-1 bg-background/50 border-border/50 focus:border-primary/50 rounded-full"
            />
            <Button
              type="submit"
              disabled={loading}
              className="px-6 bg-gradient-to-r from-primary to-accent text-primary-foreground border-0 hover:shadow-lg transition-all rounded-full"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </Button>
          </form>
          <p className="text-xs text-muted-foreground mt-3 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {t("chat.disclaimer")}
          </p>
        </div>
      </main>
    </div>
  )
}

