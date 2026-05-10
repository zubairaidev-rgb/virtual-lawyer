"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Shield, ArrowRight, Eye, EyeOff } from "lucide-react"
import Link from "next/link"

export default function SignupPage() {
  const router = useRouter()
  const [userType, setUserType] = useState<"citizen" | "lawyer" | null>(null)
  const [formData, setFormData] = useState({ name: "", email: "", password: "", confirmPassword: "" })
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    if (userType && formData.name && formData.email && formData.password && formData.confirmPassword) {
      if (formData.password !== formData.confirmPassword) {
        alert("Passwords do not match")
        return
      }
      setIsLoading(true)
      try {
        const { signup } = await import("@/lib/services/auth")
        const response = await signup({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          userType: userType as "citizen" | "lawyer"
        })
        if (response.success) {
          // Store user info in localStorage (in production, use proper auth)
          localStorage.setItem("user", JSON.stringify(response.user))
          const accessToken = response.access_token || response.token
          if (accessToken) {
            localStorage.setItem("token", accessToken)
          }
          router.push(`/${userType}`)
        }
      } catch (error: any) {
        console.error("Signup error:", error)
        alert(error.message || "Signup failed. Please try again.")
      } finally {
        setIsLoading(false)
      }
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-accent/5 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Animation */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl opacity-30 animate-float"></div>
        <div
          className="absolute bottom-1/4 left-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl opacity-30 animate-float"
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
          <p className="text-muted-foreground">Create your account</p>
        </div>

        {/* Role Selection */}
        {!userType ? (
          <Card className="p-8 border border-border/50 backdrop-blur bg-card/80 animate-fadeInUp">
            <p className="text-sm font-semibold text-foreground mb-6">Choose your role</p>
            <div className="space-y-3">
              {[
                {
                  role: "citizen" as const,
                  label: "I'm a Citizen",
                  desc: "Seeking legal guidance and case management",
                },
                {
                  role: "lawyer" as const,
                  label: "I'm a Lawyer",
                  desc: "Offering legal services and case management",
                },
              ].map((item) => (
                <button
                  key={item.role}
                  onClick={() => setUserType(item.role)}
                  className="w-full p-4 rounded-lg border-2 border-border hover:border-primary bg-transparent hover:bg-primary/5 transition-all duration-300 text-left group"
                >
                  <p className="font-semibold text-foreground group-hover:text-primary transition-colors">
                    {item.label}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
                </button>
              ))}
            </div>
          </Card>
        ) : (
          <Card className="p-8 border border-border/50 backdrop-blur bg-card/80 animate-fadeInUp">
            <button
              onClick={() => {
                setUserType(null)
                setFormData({ name: "", email: "", password: "", confirmPassword: "" })
              }}
              className="text-sm text-primary hover:text-primary/80 mb-6 flex items-center gap-1 transition-colors"
            >
              ← Change role
            </button>

            <form onSubmit={handleSignup} className="space-y-4">
              <div>
                <Label htmlFor="name" className="text-sm font-semibold text-foreground">
                  Full Name
                </Label>
                <Input
                  id="name"
                  type="text"
                  placeholder="Enter your name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="mt-2 bg-background/50 border-border/50 focus:border-primary/50"
                  disabled={isLoading}
                />
              </div>

              <div>
                <Label htmlFor="email" className="text-sm font-semibold text-foreground">
                  Email Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
                    placeholder="Create a password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
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

              <div>
                <Label htmlFor="confirm" className="text-sm font-semibold text-foreground">
                  Confirm Password
                </Label>
                <div className="relative mt-2">
                  <Input
                    id="confirm"
                    type={showConfirm ? "text" : "password"}
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    className="bg-background/50 border-border/50 focus:border-primary/50 pr-10"
                    disabled={isLoading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirm(!showConfirm)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    disabled={isLoading}
                  >
                    {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
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
                    Creating account...
                  </>
                ) : (
                  <>
                    Create Account
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </form>

            <p className="text-center text-sm text-muted-foreground mt-6">
              Already have an account?{" "}
              <Link href="/login" className="text-primary hover:underline font-semibold">
                Sign in
              </Link>
            </p>
          </Card>
        )}
      </div>
    </div>
  )
}
