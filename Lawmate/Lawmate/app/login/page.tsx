"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Shield, ArrowRight, Eye, EyeOff, Zap } from "lucide-react"
import Link from "next/link"

export default function LoginPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [userType, setUserType] = useState<"citizen" | "lawyer" | "admin" | null>(null)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const redirectPath = searchParams.get("redirect")

  useEffect(() => {
    try {
      const raw = localStorage.getItem("user")
      if (!raw) return
      const user = JSON.parse(raw) as { userType?: "citizen" | "lawyer" | "admin" }
      // Only auto-redirect when user was sent here from a protected route.
      // For direct /login visits, let user pick role and login normally.
      if (user?.userType && redirectPath) {
        router.replace(`/${user.userType}`)
      }
    } catch {
      localStorage.removeItem("user")
      localStorage.removeItem("token")
    }
  }, [router, redirectPath])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (userType && email && password) {
      setIsLoading(true)
      try {
        const { login } = await import("@/lib/services/auth")
        const response = await login({
          email: email.trim().toLowerCase(),
          password,
          userType: userType as "citizen" | "lawyer" | "admin"
        })
        if (response.success) {
          // Store user info in localStorage (in production, use proper auth)
          localStorage.setItem("user", JSON.stringify(response.user))
          const accessToken = response.access_token || response.token
          if (accessToken) {
            localStorage.setItem("token", accessToken)
          }
          const roleFromBackend = response.user?.userType as "citizen" | "lawyer" | "admin" | undefined
          const targetRole = roleFromBackend || userType
          if (redirectPath && redirectPath.startsWith("/")) {
            router.push(redirectPath)
          } else {
            router.push(`/${targetRole}`)
          }
        }
      } catch (error: any) {
        console.error("Login error:", error)
        alert(error.message || "Login failed. Please try again.")
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-30 animate-float"></div>
        <div
          className="absolute bottom-1/4 left-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl opacity-30 animate-float"
          style={{ animationDelay: "1s" }}
        ></div>
      </div>

      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-12 animate-fadeInUp">
          <div className="flex items-center justify-center gap-2 mb-6 group">
            <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
              <Shield className="w-8 h-8 text-primary-foreground" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-foreground mb-2">Lawmate</h1>
          <p className="text-muted-foreground">Access Criminal Legal Justice with AI</p>
        </div>

        {/* Role Selection */}
        {!userType ? (
          <Card
            className="p-8 border border-border/50 backdrop-blur bg-card/80 animate-fadeInUp"
            style={{ animationDelay: "100ms" }}
          >
            <p className="text-sm font-semibold text-foreground mb-6">Select your role to continue</p>
            <div className="space-y-3">
              {[
                {
                  role: "citizen" as const,
                  label: "Citizen / Public User",
                  desc: "Access legal guidance and case management",
                  icon: Zap,
                },
                {
                  role: "lawyer" as const,
                  label: "Lawyer / Legal Professional",
                  desc: "Manage clients and cases",
                  icon: Shield,
                },
                {
                  role: "admin" as const,
                  label: "Administrator",
                  desc: "System administration and monitoring",
                  icon: ArrowRight,
                },
              ].map((item) => (
                <button
                  key={item.role}
                  onClick={() => setUserType(item.role)}
                  className="w-full p-4 rounded-lg border-2 border-border hover:border-primary bg-transparent hover:bg-primary/5 transition-all duration-300 text-left group"
                >
                  <div className="flex items-start gap-3">
                    <item.icon className="w-5 h-5 text-primary mt-0.5" />
                    <div>
                      <p className="font-semibold text-foreground group-hover:text-primary transition-colors">
                        {item.label}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </Card>
        ) : (
          <Card className="p-8 border border-border/50 backdrop-blur bg-card/80 animate-fadeInUp">
            <button
              onClick={() => {
                setUserType(null)
                setEmail("")
                setPassword("")
              }}
              className="text-sm text-primary hover:text-primary/80 mb-6 flex items-center gap-1 transition-colors"
            >
              ← Change role
            </button>

            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <Label htmlFor="email" className="text-sm font-semibold text-foreground">
                  Email Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-2 bg-background/50 border-border/50 focus:border-primary/50"
                  disabled={isLoading}
                />
              </div>

              <div>
                <Label htmlFor="password" className="text-sm font-semibold text-foreground">
                  Password
                </Label>
                <div className="relative mt-2">
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="bg-background/50 border-border/50 focus:border-primary/50 pr-10"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    disabled={isLoading}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-primary to-accent text-primary-foreground border-0 hover:shadow-lg transition-all"
                size="lg"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full mr-2"></div>
                    Signing in...
                  </>
                ) : (
                  <>
                    Sign In as {userType.charAt(0).toUpperCase() + userType.slice(1)}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </form>

            <p className="text-center text-sm text-muted-foreground mt-6">
              Don't have an account?{" "}
              <Link href="/signup" className="text-primary hover:underline font-semibold">
                Sign up
              </Link>
            </p>
          </Card>
        )}
      </div>
    </div>
  )
}
