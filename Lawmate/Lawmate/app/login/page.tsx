import { Suspense } from "react"
import { LoginPageClient } from "./login-client"

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4">
          <p className="text-muted-foreground text-sm">Loading…</p>
        </div>
      }
    >
      <LoginPageClient />
    </Suspense>
  )
}
