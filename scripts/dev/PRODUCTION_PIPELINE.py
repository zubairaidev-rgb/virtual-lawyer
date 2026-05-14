"""
PRODUCTION-READY Two-Stage Pipeline
No. 1 Pakistan Criminal Law Model

This is the complete, optimized pipeline ready for production use.
"""
import os
import sys
from pathlib import Path

_scripts_dir = Path(__file__).resolve().parents[1]
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
from _repo import bootstrap_path  # noqa: E402

bootstrap_path()

# Import config to set API key
try:
    from config import GROQ_API_KEY, PIPELINE_CONFIG
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
except ImportError:
    print("WARNING: config.py not found. Using environment variables.")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from two_stage_pipeline import TwoStagePipeline

class ProductionPipeline:
    """
    Production-ready pipeline for Pakistan Criminal Law
    Optimized for best performance and quality
    """
    
    def __init__(self):
        """Initialize production pipeline"""
        print("=" * 70)
        print("INITIALIZING PRODUCTION PIPELINE")
        print("No. 1 Pakistan Criminal Law Model")
        print("=" * 70)
        
        # Initialize two-stage pipeline
        self.pipeline = TwoStagePipeline(
            peft_model_path="./models/final_model_v5",
            formatter_type="groq",
            formatter_api_key=GROQ_API_KEY
        )
        
        print("\n" + "=" * 70)
        print("PRODUCTION PIPELINE READY")
        print("=" * 70)
        print("\nFeatures:")
        print("  - Stage 1: Fine-tuned model with 7,873 legal documents")
        print("  - Stage 2: Groq Llama 3.1 70B for formatting")
        print("  - Optimized for speed and quality")
        print("  - Production-ready error handling")
        print()
    
    def ask(self, question: str, use_formatter: bool = True) -> dict:
        """
        Ask a question and get formatted answer
        
        Args:
            question: User question
            use_formatter: Use Stage 2 formatter (recommended: True)
        
        Returns:
            Dict with answer and metadata
        """
        try:
            result = self.pipeline.generate_answer(question, use_formatter=use_formatter)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return {
                "question": question,
                "answer": "I apologize, but I encountered an error processing your question. Please try again.",
                "error": str(e)
            }
    
    def chat(self):
        """Interactive chat mode"""
        print("=" * 70)
        print("PAKISTAN CRIMINAL LAW CHATBOT - PRODUCTION MODE")
        print("=" * 70)
        print("Type 'exit' to quit\n")
        
        while True:
            question = input("You: ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print("\nProcessing...")
            result = self.ask(question, use_formatter=True)
            
            print(f"\nAnswer ({result.get('response_time', 0):.1f}s):")
            print(f"{result['answer']}\n")
            
            if result.get('references'):
                print("References:")
                for i, ref in enumerate(result['references'][:3], 1):
                    if ref.get('type') == 'PPC':
                        print(f"   {i}. PPC Section {ref.get('section', 'N/A')}")
                    elif ref.get('type') == 'Case Law':
                        print(f"   {i}. SHC Case {ref.get('case_no', 'N/A')}")
                    elif ref.get('type') == 'CrPC':
                        print(f"   {i}. CrPC Section")
                    elif ref.get('type') == 'Constitution':
                        print(f"   {i}. Constitution Article")
            
            print(f"\n[Sources: {result.get('sources_count', 0)} | Formatted: {result.get('formatted', False)}]")
            print("-" * 70 + "\n")

if __name__ == "__main__":
    # Initialize production pipeline
    pipeline = ProductionPipeline()
    
    # Test questions
    test_questions = [
        "What is Section 302 PPC?",
        "Is Section 302 bailable?",
        "What are my rights when arrested in Pakistan?",
        "How to get bail in a murder case?",
    ]
    
    print("\n" + "=" * 70)
    print("RUNNING PRODUCTION TESTS")
    print("=" * 70)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n\nTest {i}/{len(test_questions)}: {question}")
        print("-" * 70)
        
        result = pipeline.ask(question, use_formatter=True)
        
        print(f"\nAnswer ({result.get('response_time', 0):.1f}s):")
        print(result['answer'])
        
        if result.get('stage1_time') and result.get('stage2_time'):
            print(f"\nTiming:")
            print(f"  Stage 1: {result['stage1_time']:.1f}s")
            print(f"  Stage 2: {result['stage2_time']:.1f}s")
        
        if result.get('references'):
            print(f"\nReferences: {len(result['references'])}")
    
    print("\n" + "=" * 70)
    print("PRODUCTION TESTS COMPLETE")
    print("=" * 70)
    print("\nTo start interactive chat, run:")
    print("  pipeline = ProductionPipeline()")
    print("  pipeline.chat()")























