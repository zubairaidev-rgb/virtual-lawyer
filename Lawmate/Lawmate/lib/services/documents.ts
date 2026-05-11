import { api, BASE_URL } from "../api";

export type TemplateInfo = {
  id?: string;
  template_id?: string;
  name?: string;
  placeholders?: string[];
  category?: string;
};

export async function listTemplates(category?: string, language?: string) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (language) params.set("language", language);
  const query = params.toString() ? `?${params.toString()}` : "";
  const res = await api.get<{ templates: TemplateInfo[]; count: number }>(
    `/api/document/templates${query}`
  );
  return res.templates;
}

export async function getTemplateDetails(template_id: string, language?: string) {
  if (!template_id || template_id.trim() === "") {
    throw new Error("Template ID is required");
  }
  const encodedId = template_id.split('/').map(part => encodeURIComponent(part)).join('/');
  const langParam = language ? `?language=${encodeURIComponent(language)}` : "";
  return api.get<{
    template_id: string;
    name?: string;
    category?: string;
    placeholders: string[];
    placeholder_descriptions: Record<
      string,
      { label?: string; description: string; type: string; required: boolean; example?: string }
    >;
    example_data: Record<string, string>;
    total_placeholders: number;
  }>(`/api/document/templates/${encodedId}${langParam}`);
}

export type UserDocumentMeta = {
  doc_id: string;
  file_name: string;
  chunks_count: number;
  text_length: number;
  status: string;
  uploaded_at?: string;
  owner_email?: string;
  owner_role?: string;
  is_sample?: boolean;
};

/** Lists uploads for the logged-in user (persists across refresh; includes demo samples). */
export async function listUserDocuments(
  email?: string,
  role?: "citizen" | "lawyer"
) {
  const params = new URLSearchParams();
  if (email) params.set("email", email);
  if (role) params.set("role", role);
  const q = params.toString();
  const path = `/api/document/list${q ? `?${q}` : ""}`;
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });
  // Older API processes started before this route existed return 404 — restart the backend.
  if (res.status === 404) {
    console.warn(
      "[Lawmate] GET /api/document/list is missing on the API. Restart the backend (e.g. python api_complete.py) so document lists persist after refresh."
    );
    return { documents: [], total: 0 };
  }
  if (!res.ok) {
    const errText = await res.text().catch(() => "");
    throw new Error(
      `Request failed: ${res.status} ${res.statusText} ${errText}`.trim()
    );
  }
  const text = await res.text();
  const data = text
    ? (JSON.parse(text) as { documents: UserDocumentMeta[]; total: number })
    : { documents: [], total: 0 };
  return data;
}

export async function uploadDocument(
  file: File,
  opts?: { email?: string; role?: "citizen" | "lawyer" }
) {
  const fd = new FormData();
  fd.append("file", file);
  if (opts?.email) fd.append("user_email", opts.email);
  if (opts?.role) fd.append("user_role", opts.role);
  return api.postMultipart<{
    doc_id: string;
    file_name: string;
    chunks_count: number;
    text_length: number;
    status: string;
  }>("/api/document/upload", fd);
}

export async function extractFacts(doc_id: string) {
  return api.get<{ doc_id: string; facts: Record<string, unknown>; summary: string }>(
    `/api/document/${doc_id}/extract`
  );
}

export async function getSummary(doc_id: string) {
  return api.get<{ doc_id: string; summary: string }>(
    `/api/document/${doc_id}/summary`
  );
}

export async function askQuestion(doc_id: string, question: string) {
  return api.post<{
    answer: string;
    context: string;
    chunks_used: number;
    relevant_chunks: unknown[];
    confidence: number;
  }>("/api/document/question", { doc_id, question });
}

export async function generateDocument(
  template_id: string,
  data: Record<string, unknown>,
  generate_ai_sections = false
) {
  return api.post<{
    output_path?: string;
    output_filename?: string;
    pdf_path?: string;
    pdf_filename?: string;
    placeholders_filled?: number;
    total_placeholders?: number;
    template_name?: string;
  }>("/api/document/generate", { template_id, data, generate_ai_sections });
}

export async function analyzeAndGenerate(
  doc_id: string,
  template_id: string,
  additional_data?: Record<string, unknown>
) {
  return api.post<{
    extracted_facts: Record<string, unknown>;
    generation_result: Record<string, unknown>;
  }>("/api/document/analyze-and-generate", {
    doc_id,
    template_id,
    additional_data,
  });
}

export async function suggestDocumentType(facts: Record<string, unknown>) {
  return api.post<{
    suggestions: Array<{
      template_id: string;
      name: string;
      category: string;
      relevance_score: number;
      reason: string;
    }>;
    count: number;
  }>("/api/document/suggest", facts);
}

