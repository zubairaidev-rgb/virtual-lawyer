"""
Master Script: Build Complete Multi-Source RAG System
Processes PPC PDF, SHC cases, and creates comprehensive RAG system
"""
import subprocess
import sys
from pathlib import Path

def run_script(script_name: str, description: str):
    """Run a Python script"""
    print("\n" + "=" * 60)
    print(f"STEP: {description}")
    print("=" * 60)
    print(f"Running: {script_name}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=False
        )
        print(f"\n✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error in {description}: {e}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Script not found: {script_name}")
        return False

def main():
    """Main function to build complete RAG system"""
    print("=" * 60)
    print("BUILDING COMPLETE MULTI-SOURCE RAG SYSTEM")
    print("=" * 60)
    print()
    print("This will:")
    print("1. Process PPC PDF into JSON")
    print("2. Process SHC cases into RAG format")
    print("3. Create base corpus (PPC, CrPC, Constitution)")
    print("4. Expand corpus with more sections")
    print("5. Merge everything into final RAG corpus")
    print()
    
    input("Press Enter to continue...")
    
    steps = [
        ("create_crpc_constitution_json.py", "Create CrPC and Constitution JSON"),
        ("process_ppc_pdf_to_json.py", "Process PPC PDF to JSON"),
        ("process_shc_cases_to_rag.py", "Process SHC Cases to RAG"),
        ("create_best_rag_corpus.py", "Create Base RAG Corpus"),
        ("expand_rag_corpus.py", "Expand Corpus with More Sections"),
    ]
    
    success_count = 0
    for script, description in steps:
        if run_script(script, description):
            success_count += 1
        else:
            print(f"\n⚠️  Warning: {description} failed, but continuing...")
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)
    print(f"✅ Completed: {success_count}/{len(steps)} steps")
    print()
    print("📝 Next steps:")
    print("   1. Test the multi-layer pipeline:")
    print("      python -m src.multi_layer_pipeline")
    print()
    print("   2. Or use in your chatbot:")
    print("      from src.multi_layer_pipeline import MultiLayerPipeline")
    print("      pipeline = MultiLayerPipeline()")
    print("      response = pipeline.generate_answer('What is Section 302 PPC?')")

if __name__ == "__main__":
    main()

