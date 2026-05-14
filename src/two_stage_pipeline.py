"""
Two-stage legal answer pipeline (primary production path for ``/api/chat``).

**Stage 1** — ``MultiLayerPipeline``: multi-source RAG over PPC, case law, and
structured corpora, with optional local reasoning / extractive composition.

**Stage 2** — Groq-backed formatter: polishes tone, structure, and Urdu/English
output while grounding checks try to keep citations aligned with retrieved law.

Configuration and API keys are read from the repository ``config`` module and
environment variables (see ``docs/ARCHITECTURE.md``).
"""
import os
import time
import json
import re
from typing import Dict, Optional, List
import requests
from multi_layer_pipeline import MultiLayerPipeline
from local_reasoning_enhancer import LocalReasoningEnhancer

try:
    from pipeline_trace import (
        configure_pipeline_logging,
        scrub_statute_numbers_from_chat_answer,
        summarize_references,
        summarize_retrieved_docs,
        trace_block,
    )
except ImportError:
    def configure_pipeline_logging():
        return None

    def scrub_statute_numbers_from_chat_answer(t: str) -> str:
        return t

    trace_block = None

    def summarize_references(refs):
        return []

    def summarize_retrieved_docs(docs):
        return []

# Import config
import sys
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

try:
    from config import PIPELINE_CONFIG, GROQ_API_KEY
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
except ImportError:
    # Fallback if config not found
    PIPELINE_CONFIG = {
        "formatter_type": "groq",
        # Groq decommissioned `llama-3.1-70b-versatile`. Use a supported model.
        "formatter_model": "llama-3.3-70b-versatile",
        "stage1": {"max_new_tokens": 150, "temperature": 0.2, "top_k": 3, "context_max_length": 1500},
        "stage2": {"temperature": 0.3, "max_tokens": 600, "top_p": 0.9},
        "grounding_guard": {
            "enabled": os.getenv("ENABLE_GROQ_GROUNDING_GUARD", "true").lower() == "true",
            "max_tokens": int(os.getenv("GROQ_GROUNDING_GUARD_MAX_TOKENS", "420")),
            "temperature": float(os.getenv("GROQ_GROUNDING_GUARD_TEMPERATURE", "0.0")),
            "timeout_s": int(os.getenv("GROQ_GROUNDING_GUARD_TIMEOUT_S", "12")),
        },
        "formatter_routing": {
            "always_on": os.getenv("GROQ_ALWAYS_ON", "true").lower() == "true",
            "auto_enabled": os.getenv("AUTO_GROQ", "true").lower() == "true",
            "min_sources_for_skip": int(os.getenv("AUTO_GROQ_MIN_SOURCES_FOR_SKIP", "2")),
            "long_question_words": int(os.getenv("AUTO_GROQ_LONG_QUESTION_WORDS", "22")),
        },
        "reasoner": {
            "enabled": os.getenv("ENABLE_LOCAL_REASONER", "true").lower() == "true",
            "model_name": os.getenv("LOCAL_REASONER_MODEL", "Qwen/Qwen2.5-3B-Instruct"),
            "max_new_tokens": int(os.getenv("LOCAL_REASONER_MAX_NEW_TOKENS", "320")),
            "temperature": float(os.getenv("LOCAL_REASONER_TEMPERATURE", "0.2")),
            "top_p": float(os.getenv("LOCAL_REASONER_TOP_P", "0.9")),
            "groq_enabled": os.getenv("ENABLE_GROQ_REASONER", "true").lower() == "true",
            "groq_model": os.getenv("GROQ_REASONER_MODEL", "llama-3.3-70b-versatile"),
            "groq_max_tokens": int(os.getenv("GROQ_REASONER_MAX_TOKENS", "220")),
            "groq_temperature": float(os.getenv("GROQ_REASONER_TEMPERATURE", "0.15")),
            "groq_timeout_s": int(os.getenv("GROQ_REASONER_TIMEOUT_S", "18")),
        },
    }

class TwoStagePipeline:
    """
    Two-stage pipeline:
    1. Your model: Retrieves context and generates initial answer
    2. Formatting model: Formats and improves the answer
    """
    
    def __init__(self,
                 peft_model_path="./models/final_model_v5",
                 formatter_type="groq",  # "groq", "huggingface", "openai", "claude"
                 formatter_api_key=None):
        """
        Initialize two-stage pipeline
        
        Args:
            peft_model_path: Path to your fine-tuned model
            formatter_type: Type of formatting model to use
            formatter_api_key: API key for formatting model (if needed)
        """
        print("=" * 60)
        print("INITIALIZING TWO-STAGE PIPELINE")
        print("=" * 60)
        
        # Stage 1: Your fine-tuned model
        stage1_mode = os.getenv("STAGE1_MODE", "extractive").lower()
        print(f"\nStage 1: Initializing local stage1 pipeline (mode={stage1_mode})...")
        self.stage1_model = MultiLayerPipeline(
            peft_model_path=peft_model_path,
            use_rag=True
        )
        print("Stage 1 ready!")
        
        # Stage 2: Formatting model
        print(f"\nStage 2: Setting up {formatter_type} formatter...")
        self.formatter_type = formatter_type
        self.formatter_api_key = formatter_api_key or os.getenv(f"{formatter_type.upper()}_API_KEY")
        
        if not self.formatter_api_key and formatter_type in ["groq", "openai", "claude"]:
            print(f"WARNING: {formatter_type.upper()}_API_KEY not found!")
            print(f"Set it as environment variable or pass as argument")
            print("Continuing without formatter (will use Stage 1 only)...")
            self.use_formatter = False
        else:
            self.use_formatter = True
            print(f"Stage 2 ready! Using {formatter_type}")

        # Stage 1.5: Optional local 7B reasoning enhancer
        reasoner_cfg = PIPELINE_CONFIG.get("reasoner", {})
        self.reasoner = None
        self.use_reasoner = bool(reasoner_cfg.get("enabled", False))
        if self.use_reasoner:
            try:
                self.reasoner = LocalReasoningEnhancer(
                    model_name=reasoner_cfg.get("model_name", "Qwen/Qwen2.5-7B-Instruct"),
                    max_new_tokens=reasoner_cfg.get("max_new_tokens", 220),
                    temperature=reasoner_cfg.get("temperature", 0.2),
                    top_p=reasoner_cfg.get("top_p", 0.9),
                )
                self.use_reasoner = self.reasoner.available
            except Exception as e:
                print(f"Stage 1.5 disabled due to error: {e}")
                self.reasoner = None
                self.use_reasoner = False
        else:
            print("Stage 1.5 disabled (ENABLE_LOCAL_REASONER=false)")
        
        print("\n" + "=" * 60)
        print("TWO-STAGE PIPELINE READY")
        print("=" * 60)
        configure_pipeline_logging()

    def _groq_model_candidates(self, primary_model: str) -> List[str]:
        """
        Return ordered Groq model candidates for graceful fallback on rate limits.
        """
        env_models = os.getenv("GROQ_FALLBACK_MODELS", "").strip()
        fallback_models = [m.strip() for m in env_models.split(",") if m.strip()] if env_models else [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
        ]
        ordered = [primary_model] + [m for m in fallback_models if m != primary_model]
        # de-duplicate while preserving order
        seen = set()
        out: List[str] = []
        for m in ordered:
            if m in seen:
                continue
            seen.add(m)
            out.append(m)
        return out

    def _groq_chat_with_fallback(
        self,
        *,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        top_p: float = 0.9,
        timeout_s: int = 30,
    ) -> Optional[str]:
        if not self.formatter_api_key:
            return None
        primary_model = PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile")
        models = self._groq_model_candidates(primary_model)
        last_error = ""

        for model_name in models:
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.formatter_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "top_p": top_p,
                        "stream": False,
                    },
                    timeout=timeout_s,
                )
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()

                # Only continue to fallback model when we hit rate limits.
                err_text = response.text
                try:
                    err_json = response.json()
                    err_text = err_json.get("error", {}).get("message", err_text)
                except Exception:
                    pass
                last_error = f"{response.status_code}: {err_text}"
                if response.status_code != 429:
                    break
                print(f"Groq model {model_name} rate-limited; trying fallback model...")
            except Exception as e:
                last_error = str(e)
                continue

        if last_error:
            print(f"Groq fallback exhausted: {last_error}")
        return None

    def _extract_target_section(self, question: str) -> tuple[str, str]:
        q = (question or "").lower()
        m = re.search(r"section\s+(\d+[a-z]?)\s*(ppc|crpc)", q)
        if m:
            return m.group(1), m.group(2)
        m2 = re.search(r"section\s+(\d+[a-z]?)", q)
        if m2:
            section = m2.group(1)
            code = "crpc" if "crpc" in q else ("ppc" if "ppc" in q else "ppc")
            return section, code
        return "", ""

    def _format_statute_lookup_with_groq(self, question: str, context: str, references: list, initial_answer: str) -> str:
        """
        Section lookup mode: force exact, concise, citation-safe section explanation.
        """
        section, code = self._extract_target_section(question)
        code_label = (code or "ppc").upper()
        refs = []
        for ref in (references or [])[:8]:
            if not isinstance(ref, dict):
                continue
            label = ref.get("title") or ref.get("case_no") or ref.get("section") or ref.get("type")
            if label:
                refs.append(f"- {label}")
        refs_text = "\n".join(refs) if refs else "- No references found"

        prompt = f"""You are a Pakistan criminal law assistant in STRICT section-lookup mode.

User asked about: Section {section or 'N/A'} {code_label}

Rules:
1) Explain ONLY the requested section (or closest grounded match) from provided context/references.
2) If exact section is not present in references, clearly say "exact section text not found in current corpus".
3) Do not switch topic to unrelated arrest/FIR/remedy templates.
4) Keep answer concise and direct.
5) Include section label explicitly in the answer when grounded.

Question:
{question}

Context:
{(context or '')[:2200]}

References:
{refs_text}

Draft:
{initial_answer}

Return only final user-facing answer text."""

        formatted = self._groq_chat_with_fallback(
            messages=[
                {"role": "system", "content": "You produce strict, grounded section explanations under Pakistan law."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=320,
            temperature=0.1,
            top_p=0.9,
            timeout_s=25,
        )
        return formatted or initial_answer

    def _reason_with_groq(self, draft_answer: str, question: str, context: str, references: list) -> str:
        """Fast legal reasoning refinement with Groq (Stage 1.5)."""
        reasoner_cfg = PIPELINE_CONFIG.get("reasoner", {})
        model_name = reasoner_cfg.get("groq_model", PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile"))
        max_tokens = int(reasoner_cfg.get("groq_max_tokens", 220))
        temperature = float(reasoner_cfg.get("groq_temperature", 0.15))
        timeout_s = int(reasoner_cfg.get("groq_timeout_s", 18))

        refs = []
        for ref in (references or [])[:5]:
            if not isinstance(ref, dict):
                continue
            label = ref.get("title") or ref.get("case_no") or ref.get("section") or ref.get("type")
            if label:
                refs.append(f"- {label}")
        refs_text = "\n".join(refs) if refs else "- No references provided"

        prompt = f"""You are a Pakistan criminal law reasoning assistant.

Task: Improve the grounded draft answer with concise reasoning and direct conclusion.

Rules:
1) Use only the draft/context/references provided.
2) Do not invent section numbers, case citations, or legal facts.
3) Start with a direct answer sentence.
4) Apply facts to law clearly (Rule -> Application -> Conclusion).
5) Keep concise and practical for a non-lawyer.
6) Do not output legal section labels in the body (sources are shown separately in UI).

Question:
{question}

Grounded draft:
{draft_answer}

Context:
{(context or '')[:1800]}

References:
{refs_text}

Return only the improved final answer text."""

        try:
            refined = self._groq_chat_with_fallback(
                messages=[
                    {"role": "system", "content": "You are an expert Pakistan criminal law assistant focused on accurate reasoning."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                timeout_s=timeout_s,
            )
            if refined:
                if trace_block:
                    trace_block(
                        "STAGE1.5 / GROQ / RESPONSE",
                        {"raw_reasoner_output": refined},
                    )
                return refined
            return draft_answer
        except Exception:
            return draft_answer

    def _is_answer_weak(self, answer: str) -> bool:
        if not answer:
            return True
        text = answer.strip()
        lower = text.lower()
        if len(re.findall(r"\w+", text)) < 50:
            return True
        weak_markers = [
            "apply these legal points through counsel",
            "verify court-specific procedure before action",
            "i could not find sufficiently relevant legal material",
            "retrieval gap:",
        ]
        if any(m in lower for m in weak_markers):
            return True
        return False

    def _ensure_readable_chat_format(self, text: str) -> str:
        """
        Keep model output readable without forcing a fixed template.
        """
        if not text:
            return text

        cleaned = re.sub(r"\r\n?", "\n", text).strip()
        # Normalize bullet markers from model output.
        cleaned = re.sub(r"(?m)^\*\s+", "- ", cleaned)
        # If the model already returned multiline output, keep it.
        non_empty_lines = [ln.strip() for ln in cleaned.split("\n") if ln.strip()]
        if len(non_empty_lines) >= 2:
            return cleaned

        # For single long paragraphs, only add soft line breaks after sentence boundaries.
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", cleaned.replace("\n", " "))
            if s.strip()
        ]
        if len(sentences) < 4:
            return cleaned

        return "\n\n".join(sentences).strip()

    def _trim_incomplete_tail(self, text: str) -> str:
        """Drop likely truncated trailing fragments from model output."""
        if not text:
            return text
        lines = [ln.rstrip() for ln in text.split("\n")]
        while lines:
            tail = lines[-1].strip()
            if not tail:
                lines.pop()
                continue
            # Common truncation patterns after grounding/format passes.
            if tail.endswith("as per.") or tail.endswith("as per") or tail.endswith("the"):
                lines.pop()
                continue
            # If final non-heading line has no terminal punctuation, drop it.
            is_heading = tail.endswith(":") and len(tail.split()) <= 8
            if (not is_heading) and (tail[-1] not in ".!?"):
                lines.pop()
                continue
            break
        return "\n".join(lines).strip()

    def _ground_with_groq(self, answer: str, references: list, question: str) -> str:
        """
        Use Groq to remove/repair unsupported section/case mentions.
        Keeps answer conservative when references are thin.
        """
        guard_cfg = PIPELINE_CONFIG.get("grounding_guard", {})
        if not guard_cfg.get("enabled", True):
            return answer
        if not self.formatter_api_key:
            return answer
        if not answer:
            return answer

        model_name = PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile")
        max_tokens = int(guard_cfg.get("max_tokens", 220))
        temperature = float(guard_cfg.get("temperature", 0.0))
        timeout_s = int(guard_cfg.get("timeout_s", 12))

        refs = []
        for ref in (references or [])[:8]:
            if not isinstance(ref, dict):
                continue
            refs.append(
                f"- type={ref.get('type','')} title={ref.get('title','')} "
                f"section={ref.get('section','')} case_no={ref.get('case_no','')}"
            )
        refs_text = "\n".join(refs) if refs else "- none"

        prompt = f"""You are a legal grounding checker for Pakistan criminal law outputs.

Task:
Given ANSWER and REFERENCES, remove or generalize any section/case citation in ANSWER that is not supported by REFERENCES.
Do NOT add new section numbers or case numbers.
Keep legal meaning intact and concise.
Do NOT return truncated text. Ensure all sentences are complete.

Question:
{question}

REFERENCES (allowed support):
{refs_text}

ANSWER:
{answer}

Return only corrected ANSWER text."""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.formatter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "You remove unsupported legal citations and keep only grounded ones."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": 0.9,
                    "stream": False,
                },
                timeout=timeout_s,
            )
            if response.status_code == 200:
                result = response.json()
                corrected = result["choices"][0]["message"]["content"].strip()
                if corrected:
                    if trace_block:
                        trace_block(
                            "GROUNDING_GUARD / GROQ",
                            {"input_answer": answer, "corrected_answer": corrected},
                        )
                    return corrected
            return answer
        except Exception:
            return answer

    def _build_groq_display_sources(
        self,
        question: str,
        answer: str,
        context: str,
        references: list,
    ) -> List[str]:
        """
        Create user-facing Sources labels via Groq (no backend raw dump).
        Must stay within provided grounded references/context.
        """
        if not self.formatter_api_key:
            return []

        allowed = []
        for ref in (references or [])[:10]:
            if not isinstance(ref, dict):
                continue
            label = ref.get("title") or ref.get("case_no") or ref.get("section") or ref.get("type")
            rtype = ref.get("type", "Reference")
            if label:
                allowed.append(f"{rtype}: {label}")
        allowed_text = "\n".join(f"- {x}" for x in allowed) if allowed else "- No explicit legal references"

        prompt = f"""You are generating frontend source labels for a legal chatbot.

Rules:
1) Output STRICT JSON array of strings only (no markdown, no explanation).
2) Use only legal sources grounded in ALLOWED REFERENCES/CONTEXT.
3) Keep labels short and readable for UI chips.
4) Do NOT include technical/provider/model labels.
5) Return 1 to 5 items max.

Question:
{question}

Answer:
{answer[:1200]}

Allowed References:
{allowed_text}

Context (optional):
{(context or '')[:1200]}

Return JSON array now."""

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.formatter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile"),
                    "messages": [
                        {"role": "system", "content": "You output only JSON arrays of strings."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.0,
                    "max_tokens": 160,
                    "top_p": 0.9,
                    "stream": False,
                },
                timeout=10,
            )
            if response.status_code != 200:
                return []

            raw = response.json()["choices"][0]["message"]["content"].strip()
            # tolerate fenced output
            raw = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                cleaned = [str(x).strip() for x in parsed if str(x).strip()]
                return cleaned[:5]
            return []
        except Exception:
            return []

    def _should_run_formatter(self, question: str, stage1_result: Dict, stage1_5_answer: str, requested: bool) -> tuple[bool, str]:
        if not self.use_formatter:
            return False, "formatter_unavailable"

        routing_cfg = PIPELINE_CONFIG.get("formatter_routing", {})
        always_on = bool(routing_cfg.get("always_on", True))
        if always_on:
            return True, "always_on"
        auto_enabled = bool(routing_cfg.get("auto_enabled", True))
        if requested:
            return True, "explicit_request"
        if not auto_enabled:
            return False, "auto_disabled"

        confidence = str(stage1_result.get("confidence", "medium")).lower()
        sources_count = int(stage1_result.get("sources_count", 0) or 0)
        min_sources_for_skip = int(routing_cfg.get("min_sources_for_skip", 2))
        long_question_words = int(routing_cfg.get("long_question_words", 22))
        word_count = len(re.findall(r"\w+", question or ""))
        has_gap = "retrieval gap:" in (stage1_5_answer or "").lower()
        weak_answer = self._is_answer_weak(stage1_5_answer)

        should_run = (
            confidence != "high"
            or sources_count < min_sources_for_skip
            or word_count >= long_question_words
            or has_gap
            or weak_answer
        )
        reason = (
            f"auto_route conf={confidence} sources={sources_count} words={word_count} "
            f"gap={has_gap} weak={weak_answer}"
        )
        return should_run, reason
    
    def _format_with_groq(self, initial_answer: str, question: str, context: str, references: list) -> str:
        """Format answer using Groq API (FREE, FAST) - OPTIMIZED FOR PAKISTAN CRIMINAL LAW"""
        
        # Build references text
        ref_text = ""
        if references:
            ref_text = "\nREFERENCES:\n"
            for i, ref in enumerate(references[:3], 1):
                if ref.get('type') == 'PPC':
                    ref_text += f"{i}. PPC Section {ref.get('section', 'N/A')}\n"
                elif ref.get('type') == 'Case Law':
                    ref_text += f"{i}. SHC Case {ref.get('case_no', 'N/A')}\n"
                elif ref.get('type') == 'CrPC':
                    ref_text += f"{i}. CrPC Section\n"
                elif ref.get('type') == 'Constitution':
                    ref_text += f"{i}. Constitution Article {ref.get('article', 'N/A')}\n"
        
        # Use improved prompts if available
        try:
            # Try importing from src directory
            try:
                from src.improved_prompts import build_stage2_prompt
            except ImportError:
                from improved_prompts import build_stage2_prompt
            
            prompt = build_stage2_prompt(
                question=question,
                initial_answer=initial_answer,
                context=context,
                references=references
            )
        except (ImportError, Exception) as e:
            # Fallback to original prompt if improved prompts not available
            print(f"   Note: Using default prompt (improved_prompts not available: {e})")
            # Enhanced fallback prompt that PRESERVES context information
            prompt = f"""You are an expert Pakistan criminal law assistant. Your task is to format and improve a legal answer while PRESERVING all correct legal information from the context.

CRITICAL RULE: The initial answer was generated using legal context. You MUST preserve any correct legal information from that context, especially about evidence priority, legal principles, and case citations.

ORIGINAL QUESTION: {question}

INITIAL ANSWER (needs improvement):
{initial_answer}

RELEVANT LEGAL CONTEXT (SOURCE OF INFORMATION):
{context[:1000]}

{ref_text}

CRITICAL TASKS:
1. PRESERVE all correct legal information from context (especially evidence priority rules)
2. If context says "ocular evidence has primacy" - KEEP that in your answer
3. If context contains case citations (PLD 2009 SC 45, 2020 SCMR 316, etc.) - INCLUDE them in your answer
4. Extract and include proper case citations from context (format: "PLD 2009 SC 45", "2020 SCMR 316")
5. Remove ALL prefixes like "For example:", "In this regard:", "Here,", etc.
6. Start directly with the answer - no introductory phrases
7. Complete any incomplete or cut-off sentences
8. Ensure the answer directly and clearly addresses the question
9. Format in a structured, professional manner
10. Maintain 100% legal accuracy - do NOT change any legal facts
11. Keep all section numbers, case names, and legal terms accurate
12. DO NOT remove context-based information - only improve formatting
13. If context mentions "PLD 2009 SC 45" or "2020 SCMR 316" - include these citations

REQUIRED FORMAT:
1. Direct Answer: Clear, concise answer (2-4 sentences) that directly addresses the question
2. Legal Basis: Relevant PPC/CrPC sections or Constitution articles (if applicable)
3. Key Details: Punishment, bail status, or other important information (if applicable)

STRICT RULES:
- Answer MUST be about Pakistan law ONLY (PPC, CrPC, Constitution)
- Do NOT mention US, UK, Indian (IPC), or Bangladesh law
- Do NOT add information not present in the initial answer
- Do NOT make up section numbers or case names
- Only improve structure, clarity, and completeness
- Keep all legal terminology accurate

FORMATTED ANSWER (start directly, no prefixes):"""

        try:
            # Use config if available
            config = PIPELINE_CONFIG.get("stage2", {})
            if trace_block:
                trace_block(
                    "STAGE2 / GROQ / REQUEST",
                    {
                        "model": PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile"),
                        "user_prompt_to_groq": prompt,
                    },
                )

            formatted = self._groq_chat_with_fallback(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Pakistan criminal law assistant. You format legal answers to be clear, complete, and professional. You NEVER add information not in the source, and you ALWAYS maintain legal accuracy."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.get("max_tokens", 600),
                temperature=config.get("temperature", 0.3),
                top_p=config.get("top_p", 0.9),
                timeout_s=30,
            )
            if formatted:
                if trace_block:
                    trace_block(
                        "STAGE2 / GROQ / RESPONSE",
                        {"raw_model_output": formatted},
                    )
                return formatted
            print("Groq formatter unavailable after fallback attempts; using Stage 1 answer")
            return initial_answer
                
        except Exception as e:
            print(f"Error formatting with Groq: {e}")
            import traceback
            traceback.print_exc()
            return initial_answer
    
    def _format_with_huggingface(self, initial_answer: str, question: str, context: str, references: list) -> str:
        """Format answer using Hugging Face Inference API (FREE)"""
        
        prompt = f"""Format and improve this legal answer about Pakistan criminal law:

Question: {question}

Initial Answer:
{initial_answer}

Context:
{context[:800]}

Task: Format the answer clearly, remove "For example:" prefixes, complete sentences, and ensure it directly answers the question.

Formatted Answer:"""

        try:
            # Using Mistral 7B for formatting
            response = requests.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
                headers={
                    "Authorization": f"Bearer {self.formatter_api_key}" if self.formatter_api_key else None
                },
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 400,
                        "temperature": 0.3,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    formatted = result[0].get('generated_text', initial_answer).strip()
                    return formatted
                return initial_answer
            else:
                print(f"Hugging Face API error: {response.status_code}")
                return initial_answer
                
        except Exception as e:
            print(f"Error formatting with Hugging Face: {e}")
            return initial_answer
    
    def _format_with_openai(self, initial_answer: str, question: str, context: str, references: list) -> str:
        """Format answer using OpenAI GPT-3.5 Turbo (PAID but CHEAP)"""
        
        prompt = f"""You are an expert legal text formatter. Improve and format this legal answer about Pakistan criminal law.

ORIGINAL QUESTION: {question}

INITIAL ANSWER (needs formatting):
{initial_answer}

RELEVANT CONTEXT:
{context[:1000]}

TASK:
1. Format the answer clearly and professionally
2. Remove any "For example:" or similar prefixes
3. Complete any incomplete sentences
4. Ensure direct answer to the question
5. Maintain all legal accuracy
6. Use structured format: Direct Answer → Legal Basis → Details

IMPORTANT:
- Keep ALL legal information accurate
- Do NOT add information not in the initial answer
- Only improve structure and clarity
- Answer must be about Pakistan law ONLY

FORMATTED ANSWER:"""

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.formatter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are an expert legal text formatter for Pakistan criminal law."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                formatted = result['choices'][0]['message']['content'].strip()
                return formatted
            else:
                print(f"OpenAI API error: {response.status_code}")
                return initial_answer
                
        except Exception as e:
            print(f"Error formatting with OpenAI: {e}")
            return initial_answer
    
    def generate_answer(self, question: str, use_formatter: bool = True) -> Dict:
        """
        Generate answer using two-stage pipeline
        
        Args:
            question: User question
            use_formatter: Whether to use Stage 2 formatter
        
        Returns:
            Dict with answer, references, timing, etc.
        """
        total_start = time.time()
        
        # Stage 1: Your model generates initial answer
        print("\n" + "=" * 60)
        print("STAGE 1: Retrieval + Initial Answer Generation")
        print("=" * 60)
        stage1_start = time.time()
        
        # Use optimized settings from config
        config = PIPELINE_CONFIG.get("stage1", {})
        
        stage1_result = self.stage1_model.generate_answer(
            question,
            max_new_tokens=config.get("max_new_tokens", 150),
            temperature=config.get("temperature", 0.2)
        )

        stage1_time = time.time() - stage1_start
        print(f"\nStage 1 complete in {stage1_time:.1f}s")
        print(f"Initial answer length: {len(stage1_result['answer'])} chars")
        if trace_block:
            trace_block(
                "TWO_STAGE / STAGE1 SUMMARY",
                {
                    "question": question,
                    "intent": stage1_result.get("intent"),
                    "confidence": stage1_result.get("confidence"),
                    "retrieved_summary": summarize_retrieved_docs(
                        stage1_result.get("retrieved_docs") or []
                    ),
                    "references_summary": summarize_references(stage1_result.get("references")),
                    "stage1_initial_answer": stage1_result.get("answer", ""),
                },
            )
        
        # Stage 1.5: Local reasoning enhancement (optional)
        stage1_5_time = 0
        stage1_5_answer = stage1_result['answer']
        reasoner_cfg = PIPELINE_CONFIG.get("reasoner", {})
        use_groq_reasoner = bool(reasoner_cfg.get("groq_enabled", True)) and bool(self.formatter_api_key)
        reasoner_mode = "none"
        reasoner_model_used = ""
        if use_groq_reasoner or (self.use_reasoner and self.reasoner):
            print("\n" + "=" * 60)
            if use_groq_reasoner:
                rname = reasoner_cfg.get("groq_model", PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile"))
                print(f"STAGE 1.5: Groq reasoning enhancement ({rname})")
            else:
                rname = PIPELINE_CONFIG.get("reasoner", {}).get("model_name", "local")
                print(f"STAGE 1.5: Local reasoning enhancement ({rname})")
            print("=" * 60)
            stage1_5_start = time.time()
            try:
                if use_groq_reasoner:
                    reasoner_mode = "groq"
                    reasoner_model_used = reasoner_cfg.get("groq_model", PIPELINE_CONFIG.get("formatter_model", "llama-3.3-70b-versatile"))
                    context = (stage1_result.get("context") or "").strip()
                    if not context and stage1_result.get("retrieved_docs"):
                        context = "\n\n".join(
                            (doc.get("text") or "")[:1200] for doc in stage1_result["retrieved_docs"][:3]
                        )
                    stage1_5_answer = self._reason_with_groq(
                        draft_answer=stage1_result["answer"],
                        question=question,
                        context=context,
                        references=stage1_result.get("references", []),
                    )
                else:
                    reasoner_mode = "local"
                    reasoner_model_used = PIPELINE_CONFIG.get("reasoner", {}).get("model_name", "local")
                    stage1_5_answer = self.reasoner.enhance(
                        question=question,
                        answer=stage1_result['answer'],
                        references=stage1_result.get('references', []),
                    )
            except Exception as e:
                print(f"Stage 1.5 failed, using Stage 1 answer: {e}")
                stage1_5_answer = stage1_result['answer']
            stage1_5_time = time.time() - stage1_5_start
            print(f"\nStage 1.5 complete in {stage1_5_time:.1f}s")
            print(f"Enhanced answer length: {len(stage1_5_answer)} chars")
            if trace_block:
                trace_block(
                    "TWO_STAGE / STAGE1.5 (LOCAL REASONER)",
                    {
                        "input_to_reasoner": stage1_result.get("answer", ""),
                        "output_from_reasoner": stage1_5_answer,
                    },
                )

        # Stage 2: Formatting (explicit request or auto-route)
        should_run_formatter, formatter_reason = self._should_run_formatter(
            question=question,
            stage1_result=stage1_result,
            stage1_5_answer=stage1_5_answer,
            requested=use_formatter,
        )
        stage2_applied = False
        if trace_block:
            trace_block(
                "TWO_STAGE / FORMATTER ROUTING",
                {
                    "requested_use_formatter": use_formatter,
                    "should_run_formatter": should_run_formatter,
                    "routing_reason": formatter_reason,
                },
            )

        if should_run_formatter:
            print("\n" + "=" * 60)
            print("STAGE 2: Formatting & Improvement")
            print("=" * 60)
            stage2_start = time.time()
            
            # Full RAG context from Stage 1 (required for coherent Groq formatting)
            context = (stage1_result.get("context") or "").strip()
            if not context and stage1_result.get("retrieved_docs"):
                context = "\n\n".join(
                    (doc.get("text") or "")[:1200] for doc in stage1_result["retrieved_docs"][:3]
                )
            
            # Format based on formatter type
            if self.formatter_type == "groq":
                if stage1_result.get("intent") == "statute_lookup":
                    formatted_answer = self._format_statute_lookup_with_groq(
                        question=question,
                        context=context,
                        references=stage1_result.get("references", []),
                        initial_answer=stage1_5_answer,
                    )
                else:
                    formatted_answer = self._format_with_groq(
                        stage1_5_answer,
                        question,
                        context,
                        stage1_result.get('references', [])
                    )
            elif self.formatter_type == "huggingface":
                formatted_answer = self._format_with_huggingface(
                    stage1_5_answer,
                    question,
                    context,
                    stage1_result.get('references', [])
                )
            elif self.formatter_type == "openai":
                formatted_answer = self._format_with_openai(
                    stage1_5_answer,
                    question,
                    context,
                    stage1_result.get('references', [])
                )
            else:
                formatted_answer = stage1_5_answer
            
            stage2_time = time.time() - stage2_start
            print(f"\nStage 2 complete in {stage2_time:.1f}s")
            print(f"Formatted answer length: {len(formatted_answer)} chars")
            
            final_answer = formatted_answer
            stage2_applied = True
        else:
            final_answer = stage1_5_answer
            stage2_time = 0

        final_answer = self._ground_with_groq(
            answer=final_answer or "",
            references=stage1_result.get("references", []),
            question=question,
        )
        final_answer = self._trim_incomplete_tail(final_answer or "")
        final_answer = self._ensure_readable_chat_format(final_answer or "")
        final_answer = self._trim_incomplete_tail(final_answer or "")
        # Keep explicit section numbers for section-lookup questions.
        if stage1_result.get("intent") != "statute_lookup":
            final_answer = scrub_statute_numbers_from_chat_answer(final_answer or "")
        display_sources = self._build_groq_display_sources(
            question=question,
            answer=final_answer,
            context=stage1_result.get("context", ""),
            references=stage1_result.get("references", []),
        )

        total_time = time.time() - total_start

        if trace_block:
            trace_block(
                "TWO_STAGE / FINAL (AFTER SECTION SCRUB FOR CHAT)",
                {"final_answer_for_client": final_answer},
            )

        return {
            "question": question,
            "answer": final_answer,
            "initial_answer": stage1_result['answer'],  # For comparison
            "reasoned_answer": stage1_5_answer if self.use_reasoner else None,
            "references": stage1_result.get('references', []),
            "display_references": display_sources,
            "context_used": stage1_result.get('context_used', False),
            "sources_count": stage1_result.get('sources_count', 0),
            "response_time": total_time,
            "stage1_time": stage1_time,
            "stage1_5_time": stage1_5_time,
            "stage2_time": stage2_time,
            "formatted": stage2_applied,
            "reasoned": self.use_reasoner,
            "reasoner_mode": reasoner_mode,
            "reasoner_model_used": reasoner_model_used,
            "formatter_mode": self.formatter_type if stage2_applied else "none",
            "formatter_model_used": PIPELINE_CONFIG.get("formatter_model", "") if stage2_applied else "",
            "intent": stage1_result.get("intent", "general"),
            "confidence": stage1_result.get("confidence", "medium"),
            "structured_answer": stage1_result.get("structured_answer"),
        }

if __name__ == "__main__":
    # Example usage
    import sys
    
    # Check for API key
    formatter_type = "groq"  # Change to "huggingface", "openai", etc.
    api_key = os.getenv("GROQ_API_KEY")  # or OPENAI_API_KEY, etc.
    
    if not api_key and formatter_type in ["groq", "openai"]:
        print("WARNING: API key not found. Set GROQ_API_KEY or OPENAI_API_KEY environment variable")
        print("Continuing without formatter...")
    
    pipeline = TwoStagePipeline(
        peft_model_path="./models/final_model_v5",
        formatter_type=formatter_type,
        formatter_api_key=api_key
    )
    
    # Test
    question = "What is Section 302 PPC?"
    print(f"\nTesting with question: {question}")
    result = pipeline.generate_answer(question, use_formatter=True)
    
    print("\n" + "=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(f"\n{result['answer']}\n")
    print(f"Total time: {result['response_time']:.1f}s")
    print(f"  Stage 1: {result['stage1_time']:.1f}s")
    print(f"  Stage 2: {result['stage2_time']:.1f}s")
    print(f"Formatted: {result['formatted']}")

