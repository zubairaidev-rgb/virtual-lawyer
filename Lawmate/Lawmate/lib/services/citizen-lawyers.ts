import { api, BASE_URL } from "../api";

export interface Lawyer {
  id: string;
  name: string;
  expertise: string;
  location: string;
  winRate: number;
  cases: number;
  rating: number;
  reviews: number;
  specialization: string[] | string;
  specializations?: string[];
  yearsExp: number;
  email?: string;
  phone?: string;
  bio?: string;
  profileImage?: string;
}

export interface LawyersResponse {
  lawyers: Lawyer[];
  total: number;
}

export interface LawyerRecommendationRequest {
  case_type?: string;
  case_description: string;
  charges_or_sections?: string;
  city?: string;
  urgency?: "low" | "medium" | "high";
  preferred_experience_years?: number;
  budget_range?: "low" | "medium" | "high";
  preferred_language?: string;
  hearing_court?: string;
  language?: "en" | "ur";
}

export interface RecommendedLawyer extends Lawyer {
  matchScore: number;
  whyRecommended: string[];
  estimatedFeeBand: "low" | "medium" | "high";
}

export interface LawyerRecommendationResponse {
  recommendations: RecommendedLawyer[];
  total: number;
  caseTags: string[];
  selectionCriteria: Record<string, number>;
}

export async function getLawyers(search?: string, specialization?: string, language?: "en" | "ur"): Promise<LawyersResponse> {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (specialization) params.append("specialization", specialization);
  if (language) params.append("language", language);
  const queryString = params.toString();
  return api.get<LawyersResponse>(`/api/lawyers${queryString ? `?${queryString}` : ""}`);
}

export async function getLawyerProfile(lawyerId: string): Promise<Lawyer> {
  return api.get<Lawyer>(`/api/lawyers/${lawyerId}`);
}

export function resolveLawyerImageUrl(imagePath?: string): string {
  if (!imagePath) return "";
  if (imagePath.startsWith("http://") || imagePath.startsWith("https://")) {
    return imagePath;
  }
  if (imagePath.startsWith("/")) {
    return `${BASE_URL}${imagePath}`;
  }
  return `${BASE_URL}/${imagePath}`;
}

export async function getLawyerRecommendations(
  payload: LawyerRecommendationRequest
): Promise<LawyerRecommendationResponse> {
  const normalizedPayload: LawyerRecommendationRequest = {
    case_type: payload.case_type?.trim() || "Criminal Case",
    ...payload,
  };

  try {
    // New route (preferred)
    return await api.post<LawyerRecommendationResponse>("/api/recommendations/lawyers", normalizedPayload);
  } catch (err: any) {
    const message = String(err?.message || "");
    // Backward-compat fallback for older backend instances
    if (message.includes("404")) {
      return api.post<LawyerRecommendationResponse>("/api/lawyers/recommendations", normalizedPayload);
    }
    throw err;
  }
}

