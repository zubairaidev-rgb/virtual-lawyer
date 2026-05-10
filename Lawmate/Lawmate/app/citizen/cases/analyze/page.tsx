import { Suspense } from "react"
import CaseAnalysisPage from "./analyze-client"
import { Loader2 } from "lucide-react"

function AnalyzeFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-primary/5">
      <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" aria-hidden />
    </div>
  )
}

export default function AnalyzePage() {
  return (
    <Suspense fallback={<AnalyzeFallback />}>
      <CaseAnalysisPage />
    </Suspense>
  )
}
