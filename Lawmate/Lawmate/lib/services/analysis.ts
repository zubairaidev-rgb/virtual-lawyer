import { api, BASE_URL } from "../api";

export type CaseDetails = {
  sections: string[];
  evidence?: string;
  witnesses?: number;
  previous_cases?: number;
  bail_status?: string;
  evidence_strength?: string;
  case_description?: string;
  client_in_custody?: boolean;
  lawyer_experience?: number;
  procedural_violations?: boolean;
  flight_risk?: boolean;
};

export type RiskAnalysisResponse = {
  overall_risk: number;
  risk_level: string;
  confidence: number;
  factors: Array<{ factor: string; impact: number; description: string }>;
  recommendations: string[];
  risk_breakdown: {
    critical: boolean;
    high: boolean;
    medium: boolean;
    low: boolean;
  };
};

export type CasePredictionResponse = {
  predictions: {
    conviction_probability: number;
    acquittal_probability: number;
    bail_probability: number;
    /** Backend returns structured objects, not only strings */
    sentence_prediction:
      | string
      | {
          predictions: Array<Record<string, unknown>>;
          overall_risk: number;
        };
    timeline_prediction:
      | string
      | Record<string, string>;
  };
  risk_assessment: {
    overall_risk: number;
    risk_level: string;
    confidence: number;
  };
  recommendations: string[];
  suggested_actions: string[];
  plea_deal_probability?: number;
  plea_deal_recommendation?: string;
};

export type AdvancedAnalysisResponse = {
  comprehensive_analysis: {
    risk_analysis: RiskAnalysisResponse;
    outcome_prediction: CasePredictionResponse["predictions"];
    legal_strategy: {
      recommended_approach: string;
      key_arguments: string[];
      potential_defenses: string[];
    };
    evidence_analysis: {
      strength: string;
      weaknesses: string[];
      opportunities: string[];
    };
    defense_recommendations: string[];
    prosecution_strength: {
      overall: string;
      key_strengths: string[];
    };
    overall_assessment: {
      summary: string;
      immediate_action: string;
      long_term_strategy: string;
    };
  };
  summary: {
    overall_risk: number;
    risk_level: string;
    conviction_probability: number;
    bail_probability: number;
    immediate_action: string;
  };
};

export type ComprehensiveResponse = {
  comprehensive_results: {
    chat_response?: {
      answer: string;
      references: unknown[];
      response_time: number;
    };
    risk_analysis: RiskAnalysisResponse;
    prediction: CasePredictionResponse["predictions"];
    advanced_analysis: AdvancedAnalysisResponse["comprehensive_analysis"];
  };
  summary: {
    overall_risk: number;
    risk_level: string;
    conviction_probability: number;
    bail_probability: number;
    immediate_action: string;
  };
};

export type CaseTextAnalysisResponse = {
  case_analysis: {
    sections_involved: string[];
    risk_score: number;
    risk_category: string;
  };
  risk_assessment: RiskAnalysisResponse;
  predictions: {
    conviction_probability: number;
    bail_probability: number;
  };
  recommendations: string[];
};

export type BailPredictionResponse = {
  bail_prediction: {
    likelihood: number;
    probability: string;
    factors: string[];
    recommendation: string;
  };
  sections: string[];
  factors: {
    mitigating_factors: string[];
    aggravating_factors: string[];
  };
};

export type CitizenQuickCaseAnalysisRequest = {
  case_description: string;
  urgency?: "low" | "medium" | "high";
  city?: string;
  hearing_court?: string;
  custody_status?: "in_custody" | "not_in_custody" | "unknown";
  case_stage?: string;
  incident_date?: string;
  incident_location?: string;
  fir_status?: string;
  police_station?: string;
  witness_status?: string;
  witness_count?: number;
  evidence_summary?: string;
  available_documents?: string;
  key_question?: string;
  desired_outcome?: string;
  child_involved?: boolean;
  language?: string;
};

export type CitizenQuickCaseAnalysisResponse = {
  summary: string;
  extracted_sections: string[];
  likely_case_type: string;
  risk_score: number;
  risk_level: "Low" | "Medium" | "High";
  recommendations: string[];
  next_steps: string[];
  disclaimer: string;
  missing_information?: string[];
  confidence_note?: string;
};

/** Advocate quick triage: same response shape as citizen quick analysis; extra optional intake for the lawyer endpoint. */
export type LawyerQuickCaseAnalysisRequest = CitizenQuickCaseAnalysisRequest & {
  known_ppc_sections?: string;
  procedural_notes?: string;
  opposing_party_version?: string;
  evidence_gaps?: string;
  relief_sought?: string;
  client_goal?: string;
};

export type OnboardingExtractionRequest = {
  case_description: string;
  city?: string;
  case_type?: string;
  urgency?: "low" | "medium" | "high";
  custody_status?: "in_custody" | "not_in_custody" | "unknown";
  uploaded_documents?: Array<{ doc_id: string; file_name: string }>;
};

export type OnboardingExtractionResponse = {
  extracted_case_profile: {
    case_type_guess: string;
    stage_guess: string;
    core_facts: string[];
    parties: string[];
    timeline_points: string[];
    evidence_found: string[];
    missing_critical_information: string[];
  };
  suggested_analysis_modes: string[];
  suggested_parameters: string[];
  one_paragraph_summary: string;
};

function mergeLawyerQuickTextForGuards(req: LawyerQuickCaseAnalysisRequest): CitizenQuickCaseAnalysisRequest {
  const merged = [
    req.case_description,
    req.known_ppc_sections,
    req.case_stage,
    req.procedural_notes,
    req.evidence_summary,
    req.evidence_gaps,
    req.available_documents,
    req.relief_sought,
    req.client_goal,
    req.key_question,
  ]
    .filter((s) => (s || "").trim().length > 0)
    .join("\n");
  return {
    case_description: merged || req.case_description,
    urgency: req.urgency,
    city: req.city,
    hearing_court: req.hearing_court,
    custody_status: req.custody_status,
    case_stage: req.case_stage,
    incident_date: req.incident_date,
    incident_location: req.incident_location,
    fir_status: req.fir_status,
    police_station: req.police_station,
    witness_status: req.witness_status,
    witness_count: req.witness_count,
    evidence_summary: req.evidence_summary,
    available_documents: req.available_documents,
    key_question: req.key_question,
    desired_outcome: req.desired_outcome,
    child_involved: req.child_involved,
  };
}

/** Groq sometimes returns 0–1 (e.g. 0.08) or 1–10; normalize to 0–100 severity. */
function normalizeRiskScore0To100(raw: unknown): number {
  if (raw === null || raw === undefined) return 50;
  const val = Number(raw);
  if (Number.isNaN(val)) return 50;
  if (val > 0 && val <= 1) return Math.max(1, Math.min(100, Math.round(val * 100)));
  if (val > 1 && val <= 10 && Number.isInteger(val)) return Math.max(1, Math.min(100, Math.round(val * 10)));
  return Math.max(0, Math.min(100, Math.round(val)));
}

function heuristicRiskFloor(req: CitizenQuickCaseAnalysisRequest): number {
  const text = (req.case_description || "").toLowerCase();
  const sectionMatches = req.case_description.match(/\b\d{2,4}[A-Za-z]?\b/g) || [];
  const sec = sectionMatches.map((s) => s.toUpperCase()).join(" ").toLowerCase();
  let floor = 22;
  const violent = [
    "murder",
    "kill",
    "killed",
    "killing",
    "death",
    "dead",
    "die",
    "qatal",
    "qatil",
    "kidnap",
    "abduct",
    "rape",
    "dacoity",
    "terror",
    "blast",
    "bomb",
    "acid",
    "narcotics",
  ];
  if (violent.some((k) => text.includes(k)) || ["302", "307", "324", "392"].some((s) => sec.includes(s))) {
    floor = 78;
  } else if (
    ["theft", "steal", "stole", "stolen", "robbery", "snatch", "snatching", "chor", "chori", "379", "380", "356"].some(
      (k) => text.includes(k),
    ) ||
    ["379", "380", "356", "457"].some((s) => sec.includes(s))
  ) {
    floor = 44;
  } else if (
    ["fraud", "420", "cyber", "online", "cheat", "cheating", "forgery", "468", "471"].some((k) => text.includes(k)) ||
    ["420", "468", "471"].some((s) => sec.includes(s))
  ) {
    floor = 52;
  } else if (["assault", "beat", "beating", "hurt", "323", "354", "harass"].some((k) => text.includes(k))) {
    floor = 48;
  }
  if (req.custody_status === "in_custody") floor = Math.min(95, floor + 8);
  if (req.urgency === "high") floor = Math.min(95, floor + 5);
  return floor;
}

function riskLevelFromScore(score: number): "Low" | "Medium" | "High" {
  if (score >= 75) return "High";
  if (score >= 45) return "Medium";
  return "Low";
}

function applyRiskGuards(
  data: CitizenQuickCaseAnalysisResponse,
  req: CitizenQuickCaseAnalysisRequest,
): CitizenQuickCaseAnalysisResponse {
  const normalized = normalizeRiskScore0To100(data.risk_score);
  const floor = heuristicRiskFloor(req);
  const merged = Math.max(0, Math.min(100, Math.max(normalized, floor)));
  return {
    ...data,
    risk_score: merged,
    risk_level: riskLevelFromScore(merged),
  };
}

// Risk Analysis
export async function analyzeRisk(caseDetails: CaseDetails): Promise<RiskAnalysisResponse> {
  return api.post<RiskAnalysisResponse>("/api/risk-analysis", {
    case_details: caseDetails,
  });
}

// Case Prediction
export async function predictCase(caseDetails: CaseDetails): Promise<CasePredictionResponse> {
  return api.post<CasePredictionResponse>("/api/case-prediction", {
    case_details: caseDetails,
  });
}

// Advanced Analysis
export async function advancedAnalysis(
  caseDetails: CaseDetails
): Promise<AdvancedAnalysisResponse> {
  return api.post<AdvancedAnalysisResponse>("/api/advanced-analysis", {
    case_details: caseDetails,
  });
}

// Comprehensive Analysis (All-in-One)
export async function comprehensiveAnalysis(
  caseDetails: CaseDetails
): Promise<ComprehensiveResponse> {
  return api.post<ComprehensiveResponse>("/api/comprehensive", {
    case_details: caseDetails,
  });
}

// Text-Based Case Analysis
export async function analyzeCaseFromText(
  caseDescription: string,
  sectionNumbers?: string[]
): Promise<CaseTextAnalysisResponse> {
  return api.post<CaseTextAnalysisResponse>("/api/case-analysis-text", {
    case_description: caseDescription,
    section_numbers: sectionNumbers || [],
  });
}

// Bail Prediction
export async function predictBail(
  sections: string[],
  mitigatingFactors: string[] = [],
  aggravatingFactors: string[] = []
): Promise<BailPredictionResponse> {
  return api.post<BailPredictionResponse>("/api/bail-prediction", {
    sections,
    mitigating_factors: mitigatingFactors,
    aggravating_factors: aggravatingFactors,
  });
}

export async function analyzeCitizenCaseQuick(
  request: CitizenQuickCaseAnalysisRequest
): Promise<CitizenQuickCaseAnalysisResponse> {
  const res = await fetch(`${BASE_URL}/api/citizen/case-quick-analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (res.ok) {
    const data = (await res.json()) as CitizenQuickCaseAnalysisResponse;
    return applyRiskGuards(data, request);
  }

  // If backend is not updated yet, return a dynamic local fallback
  // based on citizen text so results differ per case.
  if (res.status === 404) {
    const text = (request.case_description || "").toLowerCase();
    const sectionMatches = (request.case_description.match(/\b\d{2,4}[A-Za-z]?\b/g) || []).slice(0, 8);
    const sections = Array.from(new Set(sectionMatches.map((s) => s.toUpperCase())));

    let riskScore = 45;
    if (
      ["murder", "kill", "killed", "death", "dead", "302", "kidnap", "terror", "narcotics", "rape", "qatal"].some((k) =>
        text.includes(k),
      )
    ) {
      riskScore = 82;
    } else if (["fraud", "420", "cyber", "harassment", "cheating", "theft", "steal", "robbery", "379"].some((k) => text.includes(k))) {
      riskScore = 62;
    } else if (["bail", "custody", "arrest"].some((k) => text.includes(k))) {
      riskScore = 58;
    }

    if ((request.urgency || "medium") === "high") riskScore = Math.min(95, riskScore + 5);
    if ((request.custody_status || "unknown") === "in_custody") riskScore = Math.min(95, riskScore + 6);

    riskScore = Math.max(0, Math.min(100, Math.max(riskScore, heuristicRiskFloor(request))));
    const riskLevel = riskLevelFromScore(riskScore);
    const recommendations = [
      "Keep FIR copy, arrest memo, and all police documents in one folder.",
      "Write a clear timeline of events with dates, locations, and witness names.",
      "Consult a criminal lawyer before giving detailed statements.",
    ];
    if ((request.custody_status || "") === "in_custody") {
      recommendations.unshift("Discuss urgent bail preparation and hearing strategy immediately.");
    }
    if (text.includes("cyber")) {
      recommendations.push("Preserve digital evidence (screenshots, logs, chats, transaction IDs).");
    }

    return {
      summary: "Quick analysis generated in compatibility mode from your case description.",
      extracted_sections: sections,
      likely_case_type: "Criminal Matter",
      risk_score: riskScore,
      risk_level: riskLevel,
      recommendations: recommendations.slice(0, 6),
      next_steps: [
        "Share all available documents with your lawyer.",
        "Track hearing/court deadlines carefully.",
        "Do not delete chats/files that may be evidence.",
      ],
      disclaimer: "Backend quick-analysis endpoint is unavailable; this is a compatibility estimate.",
    };
  }

  const errText = await res.text().catch(() => "");
  throw new Error(`Request failed: ${res.status} ${res.statusText} ${errText}`.trim());
}

export async function analyzeLawyerCaseQuick(
  request: LawyerQuickCaseAnalysisRequest
): Promise<CitizenQuickCaseAnalysisResponse> {
  const guardInput = mergeLawyerQuickTextForGuards(request);
  const res = await fetch(`${BASE_URL}/api/lawyer/case-quick-analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      case_description: request.case_description,
      urgency: request.urgency ?? "medium",
      city: request.city ?? "",
      hearing_court: request.hearing_court ?? "",
      custody_status: request.custody_status ?? "unknown",
      case_stage: request.case_stage ?? "",
      incident_date: request.incident_date ?? "",
      incident_location: request.incident_location ?? "",
      fir_status: request.fir_status ?? "",
      police_station: request.police_station ?? "",
      witness_status: request.witness_status ?? "",
      witness_count: request.witness_count ?? 0,
      evidence_summary: request.evidence_summary ?? "",
      available_documents: request.available_documents ?? "",
      key_question: request.key_question ?? "",
      desired_outcome: request.desired_outcome ?? "",
      child_involved: request.child_involved ?? false,
      known_ppc_sections: request.known_ppc_sections ?? "",
      procedural_notes: request.procedural_notes ?? "",
      opposing_party_version: request.opposing_party_version ?? "",
      evidence_gaps: request.evidence_gaps ?? "",
      relief_sought: request.relief_sought ?? "",
      client_goal: request.client_goal ?? "",
    }),
  });

  if (res.ok) {
    const data = (await res.json()) as CitizenQuickCaseAnalysisResponse;
    return applyRiskGuards(data, guardInput);
  }

  if (res.status === 404) {
    const text = (guardInput.case_description || "").toLowerCase();
    const sectionMatches = (guardInput.case_description.match(/\b\d{2,4}[A-Za-z]?\b/g) || []).slice(0, 8);
    const sections = Array.from(new Set(sectionMatches.map((s) => s.toUpperCase())));

    let riskScore = 45;
    if (
      ["murder", "kill", "killed", "death", "dead", "302", "kidnap", "terror", "narcotics", "rape", "qatal"].some((k) =>
        text.includes(k)
      )
    ) {
      riskScore = 82;
    } else if (["fraud", "420", "cyber", "harassment", "cheating", "theft", "steal", "robbery", "379"].some((k) => text.includes(k))) {
      riskScore = 62;
    } else if (["bail", "custody", "arrest"].some((k) => text.includes(k))) {
      riskScore = 58;
    }

    if ((request.urgency || "medium") === "high") riskScore = Math.min(95, riskScore + 5);
    if ((request.custody_status || "unknown") === "in_custody") riskScore = Math.min(95, riskScore + 6);

    riskScore = Math.max(0, Math.min(100, Math.max(riskScore, heuristicRiskFloor(guardInput))));
    const riskLevel = riskLevelFromScore(riskScore);
    const recommendations = [
      "Map prosecution witnesses to each charge element; prepare impeachment or contradiction notes.",
      "Index FIR, seizure memos, and medico-legal reports for chain-of-custody gaps.",
      "Draft bail or discharge grounds tied to investigation defects where applicable.",
    ];
    if ((request.custody_status || "") === "in_custody") {
      recommendations.unshift("File or press bail with custody timeline and hardship grounds without delay.");
    }
    if (text.includes("cyber")) {
      recommendations.push("Verify digital evidence handling under applicable procedure; request certified server logs where relevant.");
    }

    return {
      summary: "Quick advocate triage generated in compatibility mode from your memo and optional sections.",
      extracted_sections: sections,
      likely_case_type: "Criminal Matter",
      risk_score: riskScore,
      risk_level: riskLevel,
      recommendations: recommendations.slice(0, 6),
      next_steps: [
        "Align written submissions with oral arguments for the next hearing.",
        "Confirm limitation and service requirements for any interlocutory relief.",
        "Brief the client on realistic outcomes and disclosure obligations.",
      ],
      disclaimer: "Lawyer quick-analysis endpoint is unavailable; this is a compatibility estimate.",
    };
  }

  const errText = await res.text().catch(() => "");
  throw new Error(`Request failed: ${res.status} ${res.statusText} ${errText}`.trim());
}

export async function extractOnboardingCaseProfile(
  request: OnboardingExtractionRequest
): Promise<OnboardingExtractionResponse> {
  return api.post<OnboardingExtractionResponse>("/api/case-onboarding/extract", request);
}



