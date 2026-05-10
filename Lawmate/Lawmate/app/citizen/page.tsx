"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  FileText,
  Users,
  Brain,
  Calendar,
  Clock,
  Award,
  ArrowRight,
  Bell,
  TrendingUp,
  Zap,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from "lucide-react"
import Link from "next/link"
import { useCitizenDashboard } from "@/lib/store/dashboardStore"
import { getUserDisplayName } from "@/lib/auth-user"
import { useLanguage } from "@/lib/language"

export default function CitizenDashboard() {
  const { t } = useLanguage()
  const [isLoaded, setIsLoaded] = useState(false)
  const [selectedFilter, setSelectedFilter] = useState("active")
  const [welcomeName, setWelcomeName] = useState("there")
  const { data: dashboardData, loading, error, refresh } = useCitizenDashboard()

  useEffect(() => {
    setIsLoaded(true)
    setWelcomeName(getUserDisplayName("there"))
  }, [])

  useEffect(() => {
    const onStorage = () => setWelcomeName(getUserDisplayName("there"))
    window.addEventListener("storage", onStorage)
    return () => window.removeEventListener("storage", onStorage)
  }, [])

  // Show error message if there's an error
  if (error) {
    console.error("Dashboard error:", error)
  }

  // Use data from store, fallback to defaults if loading or error
  const stats = dashboardData ? [
    {
      label: t("dash.active_cases"),
      value: dashboardData.stats.active_cases.toString(),
      icon: FileText,
      color: "from-primary to-accent",
      trend: `+${dashboardData.trends.cases_this_month} ${t("dash.this_month")}`,
      desc: t("dash.cases_in_progress"),
    },
    {
      label: t("dash.pending_hearings"),
      value: dashboardData.stats.pending_hearings.toString(),
      icon: Calendar,
      color: "from-accent to-secondary",
      trend: dashboardData.trends.next_hearing_date || t("dash.no_upcoming"),
      desc: t("dash.next_hearing"),
    },
    {
      label: t("dash.documents"),
      value: dashboardData.stats.documents.toString(),
      icon: FileText,
      color: "from-secondary to-primary",
      trend: `+${dashboardData.trends.documents_this_month} ${t("dash.new")}`,
      desc: t("dash.generated_docs"),
    },
    {
      label: t("dash.top_lawyers"),
      value: dashboardData.stats.top_lawyers.toString(),
      icon: Award,
      color: "from-primary to-secondary",
      trend: t("dash.top_rated"),
      desc: t("dash.recommended"),
    },
  ] : [
    { label: t("dash.active_cases"), value: "0", icon: FileText, color: "from-primary to-accent", trend: t("dash.loading"), desc: t("dash.cases_in_progress") },
    { label: t("dash.pending_hearings"), value: "0", icon: Calendar, color: "from-accent to-secondary", trend: t("dash.loading"), desc: t("dash.next_hearing") },
    { label: t("dash.documents"), value: "0", icon: FileText, color: "from-secondary to-primary", trend: t("dash.loading"), desc: t("dash.generated_docs") },
    { label: t("dash.top_lawyers"), value: "0", icon: Award, color: "from-primary to-secondary", trend: t("dash.loading"), desc: t("dash.recommended") },
  ]

  const recentCases = dashboardData?.recent_cases || []
  const recommendations = dashboardData?.recommendations || []
  const nextHearing = dashboardData?.next_hearing

  return (
    <div className="flex">
      <Sidebar userType="citizen" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
        {/* Background Animation Elements */}
        <div className="fixed inset-0 ml-64 -z-10">
          <div className="absolute top-20 right-0 w-96 h-96 bg-primary/12 rounded-full blur-3xl opacity-25 animate-float"></div>
          <div
            className="absolute bottom-0 left-1/3 w-96 h-96 bg-accent/10 rounded-full blur-3xl opacity-20 animate-float"
            style={{ animationDelay: "1.5s" }}
          ></div>
          <div
            className="absolute top-1/2 right-1/4 w-80 h-80 bg-secondary/8 rounded-full blur-3xl opacity-15 animate-float"
            style={{ animationDelay: "3s" }}
          ></div>
          <div className="absolute inset-0 bg-grid-pattern opacity-3"></div>
        </div>

        <div className="p-8">
          {/* Header Section */}
          <div
            className={`mb-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
          >
            <div className="flex items-start justify-between mb-6 flex-col md:flex-row gap-4">
              <div>
                <h1 className="text-5xl font-bold text-foreground mb-2">
                  {t("dash.welcome")} {welcomeName}
                </h1>
                <p className="text-lg text-muted-foreground">
                  {t("dash.subtitle")}
                </p>
              </div>
              <div className="flex gap-3 flex-wrap">
                {error && (
                  <Button
                    variant="outline"
                    className="bg-destructive/10 text-destructive border-destructive/20"
                    onClick={refresh}
                  >
                    {t("dash.retry")}
                  </Button>
                )}
                <Button
                  variant="outline"
                  className="bg-card/50 backdrop-blur border-border/50 hover:bg-card hover:border-primary/50 transition-all"
                >
                  <Bell className="w-4 h-4 mr-2" />
                  {t("dash.notifications")}
                </Button>
              </div>
            </div>
            {error && (
              <div className="mb-4 p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
                <p className="text-sm text-destructive">
                  <AlertCircle className="w-4 h-4 inline mr-2" />
                  {error}
                </p>
              </div>
            )}
          </div>

          {/* Stats Section */}
          <div
            className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "100ms" }}
          >
            {stats.map((stat, i) => (
              <div
                key={i}
                className="group cursor-pointer"
                style={{ animation: `fadeInUp 0.6s ease-out ${i * 100}ms forwards`, opacity: 0 }}
              >
                <Card className="p-6 border border-border/50 hover:border-primary/50 transition-all duration-300 overflow-hidden relative group-hover:shadow-lg group-hover:translate-y-[-4px]">
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}
                  ></div>
                  <div className="relative z-10">
                    <div className="flex items-center justify-between mb-4">
                      <div
                        className={`w-14 h-14 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}
                      >
                        <stat.icon className="w-7 h-7 text-white" />
                      </div>
                      <span className="text-xs font-semibold text-primary bg-primary/10 px-2.5 py-1 rounded-full">
                        {stat.trend}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                    <p className="text-3xl font-bold text-foreground group-hover:text-primary transition-colors">
                      {stat.value}
                    </p>
                    <p className="text-xs text-muted-foreground mt-2">{stat.desc}</p>
                  </div>
                </Card>
              </div>
            ))}
          </div>

          {/* Main Content Grid */}
          <div
            className={`grid grid-cols-1 lg:grid-cols-3 gap-6 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "200ms" }}
          >
            {/* Recent Cases */}
            <div className="lg:col-span-2">
              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80 hover:shadow-lg transition-all">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    <h2 className="text-xl font-bold text-foreground">{t("dash.your_cases")}</h2>
                  </div>
                  <Link href="/citizen/cases">
                    <Button variant="ghost" size="sm" className="hover:bg-primary/10">
                      {t("dash.view_all")} <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                  </Link>
                </div>
                <div className="space-y-4">
                  {loading ? (
                    <div className="flex items-center justify-center p-8">
                      <Loader2 className="w-6 h-6 animate-spin text-primary" />
                      <span className="ml-2 text-muted-foreground">{t("dash.loading_cases")}</span>
                    </div>
                  ) : recentCases.length === 0 ? (
                    <div className="text-center p-8 text-muted-foreground">
                      <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>{t("dash.no_cases")}</p>
                    </div>
                  ) : (
                    recentCases.map((case_, i) => (
                    <div
                      key={i}
                      className="group p-5 border border-border/50 rounded-lg hover:border-primary/50 hover:bg-primary/5 transition-all duration-300 cursor-pointer"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-bold text-foreground text-lg">{case_.id}</p>
                            <span
                              className={`px-3 py-1 rounded-full text-xs font-semibold whitespace-nowrap ${case_.status === "Active" ? "bg-primary/20 text-primary" : "bg-accent/20 text-accent"}`}
                            >
                              {case_.status}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {(case_ as { desc?: string; type?: string }).desc ?? case_.type ?? ""}
                          </p>
                        </div>
                      </div>
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Calendar className="w-4 h-4" />
                          {case_.date}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Zap className="w-4 h-4" />
                          {case_.court}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {t("dash.judge")} <span className="font-medium text-foreground">{case_.judge}</span>
                        </div>
                      </div>
                      <div className="mb-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-muted-foreground">{t("dash.progress")}</span>
                          <span className="text-xs font-semibold text-primary">{case_.progress}%</span>
                        </div>
                        <div className="w-full bg-border/50 rounded-full h-2 overflow-hidden">
                          <div
                            className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-300"
                            style={{ width: `${case_.progress}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">
                          Next: {(case_ as { nextAction?: string; next_action?: string }).nextAction ?? case_.next_action ?? "Follow up"}
                        </span>
                        <CheckCircle2 className="w-4 h-4 text-primary opacity-0 group-hover:opacity-100 transition-opacity" />
                      </div>
                    </div>
                    ))
                  )}
                </div>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="space-y-6">
              <Card className="p-6 border border-border/50 backdrop-blur bg-card/80">
                <h2 className="text-lg font-bold text-foreground mb-4">{t("dash.quick_actions")}</h2>
                <div className="space-y-3">
                  <Link href="/citizen/chatbot">
                    <Button className="w-full justify-start bg-gradient-to-r from-primary to-accent text-primary-foreground border-0 hover:shadow-lg transition-all group">
                      <Brain className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" />
                      {t("dash.chat_ai")}
                    </Button>
                  </Link>
                  <Link href="/citizen/cases/analyze">
                    <Button variant="outline" className="w-full justify-start bg-transparent hover:bg-primary/10 border-border/50 transition-all">
                      <TrendingUp className="w-4 h-4 mr-2" />
                      {t("dash.analyze_case")}
                    </Button>
                  </Link>
                  <Link href="/citizen/documents">
                    <Button variant="outline" className="w-full justify-start bg-transparent hover:bg-primary/10 border-border/50 transition-all">
                      <FileText className="w-4 h-4 mr-2" />
                      {t("dash.generate_doc")}
                    </Button>
                  </Link>
                  <Link href="/citizen/lawyers">
                    <Button variant="outline" className="w-full justify-start bg-transparent hover:bg-accent/10 border-border/50 transition-all">
                      <Users className="w-4 h-4 mr-2" />
                      {t("dash.find_lawyer")}
                    </Button>
                  </Link>
                </div>
              </Card>

              {/* Upcoming Hearing */}
              {nextHearing ? (
                <Card className="p-6 border border-border/50 backdrop-blur bg-gradient-to-br from-primary/10 to-accent/5 hover:shadow-lg transition-all">
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className="w-5 h-5 text-primary" />
                    <h3 className="font-bold text-foreground">{t("dash.next_hearing_card")}</h3>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{nextHearing.case_id}</p>
                  <p className="text-3xl font-bold text-foreground mb-2">{nextHearing.date}</p>
                  <p className="text-xs text-muted-foreground mb-4">{nextHearing.court} • {nextHearing.time}</p>
                  <Button size="sm" className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground border-0 hover:shadow-lg transition-all">
                    {t("dash.add_calendar")}
                  </Button>
                </Card>
              ) : (
                <Card className="p-6 border border-border/50 backdrop-blur bg-gradient-to-br from-primary/10 to-accent/5">
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className="w-5 h-5 text-primary" />
                    <h3 className="font-bold text-foreground">{t("dash.next_hearing_card")}</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">{t("dash.no_hearings")}</p>
                </Card>
              )}
            </div>
          </div>

          {/* AI Recommendations */}
          <div
            className={`mt-12 transition-all duration-1000 ${isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}`}
            style={{ transitionDelay: "300ms" }}
          >
            <Card className="p-6 border border-border/50 backdrop-blur bg-card/80">
              <div className="flex items-center gap-2 mb-6">
                <Brain className="w-5 h-5 text-primary" />
                <h2 className="text-xl font-bold text-foreground">{t("dash.ai_recommendations")}</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {loading ? (
                  <div className="col-span-3 flex items-center justify-center p-8">
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                    <span className="ml-2 text-muted-foreground">{t("dash.loading_recs")}</span>
                  </div>
                ) : recommendations.length === 0 ? (
                  <div className="col-span-3 text-center p-8 text-muted-foreground">
                    <Brain className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>{t("dash.no_recs")}</p>
                  </div>
                ) : (
                  recommendations.map((rec, i) => {
                    // Map recommendation type to icon and colors
                    const iconMap = {
                      warning: AlertCircle,
                      success: TrendingUp,
                      info: Zap,
                    }
                    const colorMap = {
                      warning: { bg: "from-amber-500/20 to-orange-500/20", border: "border-amber-200/30" },
                      success: { bg: "from-green-500/20 to-emerald-500/20", border: "border-green-200/30" },
                      info: { bg: "from-blue-500/20 to-cyan-500/20", border: "border-blue-200/30" },
                    }
                    const RecIcon = iconMap[rec.type] || AlertCircle
                    const colors = colorMap[rec.type] || colorMap.info
                    
                    return (
                      <div
                        key={i}
                        className={`p-5 rounded-lg border ${colors.border} bg-gradient-to-br ${colors.bg} hover:shadow-lg hover:translate-y-[-2px] transition-all group cursor-pointer`}
                        style={{
                          animation: `fadeInUp 0.6s ease-out ${300 + i * 100}ms backwards`,
                        }}
                      >
                        <div className="flex items-start gap-3 mb-3">
                          <RecIcon className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                          <h3 className="font-semibold text-foreground text-sm">{rec.title}</h3>
                        </div>
                        <p className="text-xs text-muted-foreground mb-4">{rec.description}</p>
                        <Button
                          size="sm"
                          variant="outline"
                          className="bg-white/50 hover:bg-white transition-all text-primary border-primary/20 w-full"
                        >
                          {rec.action} <ArrowRight className="w-3 h-3 ml-1" />
                        </Button>
                      </div>
                    )
                  })
                )}
              </div>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
