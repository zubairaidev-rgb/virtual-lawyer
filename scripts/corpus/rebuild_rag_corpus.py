"""
Rebuild RAG Corpus from available sources
This script recreates full_rag_corpus.json from available data
"""
import json
import os
from pathlib import Path
from typing import List, Dict
import re

def find_training_data_files() -> List[Path]:
    """Find all available training data files"""
    possible_locations = [
        "data/processed/training_data_v5.json",
        "data/processed/training_data_final_clean.json",
        "data/processed/training_data_with_shc.json",
        "data/raw/cases_instruct_train_fixed.json",
        "data/raw/cases_instruct_train.json",
    ]
    
    found_files = []
    for loc in possible_locations:
        path = Path(loc)
        if path.exists():
            found_files.append(path)
            print(f"   ✅ Found: {loc}")
    
    return found_files

def extract_ppc_sections_from_training_data(data: List[Dict]) -> List[Dict]:
    """Extract PPC section information from training data"""
    ppc_docs = []
    
    for item in data:
        prompt = item.get("prompt", "")
        completion = item.get("completion", "")
        combined = f"{prompt} {completion}"
        
        # Check if it mentions PPC sections
        if re.search(r'Section\s+\d+[A-Z]?\s+PPC', combined, re.IGNORECASE):
            # Extract section number
            section_match = re.search(r'Section\s+(\d+[A-Z]?)\s+PPC', combined, re.IGNORECASE)
            if section_match:
                section_num = section_match.group(1)
                ppc_docs.append({
                    "text": combined[:2000],  # Limit length
                    "title": f"PPC Section {section_num}",
                    "source": f"ppc_section_{section_num}"
                })
    
    return ppc_docs

def create_rag_documents_from_training_data(data: List[Dict]) -> List[Dict]:
    """Convert training data into RAG documents"""
    rag_docs = []
    
    print(f"   Processing {len(data)} training examples...")
    
    for i, item in enumerate(data):
        if i % 1000 == 0:
            print(f"      Processed: {i}/{len(data)}")
        
        prompt = item.get("prompt", "").strip()
        completion = item.get("completion", "").strip()
        
        # Skip empty entries
        if not prompt and not completion:
            continue
        
        # Combine prompt and completion for context
        text = f"{prompt}\n\n{completion}".strip()
        
        # Limit length
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        # Create RAG document
        rag_docs.append({
            "text": text,
            "title": prompt[:100] if prompt else "Legal Information",
            "source": "training_data"
        })
    
    return rag_docs

def create_basic_ppc_corpus() -> List[Dict]:
    """Create basic PPC corpus with essential sections"""
    print("   Creating basic PPC corpus from common sections...")
    
    # Essential PPC sections (common questions)
    essential_sections = {
        "302": {
            "text": "Section 302 PPC - Punishment for qatl-i-amd (murder). Whoever commits qatl-i-amd shall be punished with death, or imprisonment for life, and shall also be liable to fine. Qatl-i-amd means intentional killing. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 302 - Murder"
        },
        "376": {
            "text": "Section 376 PPC - Punishment for rape. Whoever commits rape shall be punished with death or imprisonment for life, and shall also be liable to fine. Rape is a non-bailable and cognizable offence.",
            "title": "PPC Section 376 - Rape"
        },
        "420": {
            "text": "Section 420 PPC - Cheating and dishonestly inducing delivery of property. Whoever cheats and thereby dishonestly induces the person deceived to deliver any property, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 420 - Cheating"
        },
        "395": {
            "text": "Section 395 PPC - Punishment for dacoity. Whoever commits dacoity shall be punished with imprisonment for life, or with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine. Dacoity is robbery committed by five or more persons. This is a non-bailable and cognizable offence.",
            "title": "PPC Section 395 - Dacoity"
        },
        "382": {
            "text": "Section 382 PPC - Theft after preparation made for causing death, hurt or restraint in order to the committing of the theft. Whoever commits theft, having made preparation for causing death, or hurt, or restraint, or fear of death, or of hurt, or of restraint, to any person, in order to the committing of such theft, shall be punished with rigorous imprisonment for a term which may extend to ten years, and shall also be liable to fine.",
            "title": "PPC Section 382 - Theft with preparation"
        },
    }
    
    corpus = []
    for section_num, info in essential_sections.items():
        corpus.append({
            "text": info["text"],
            "title": info["title"],
            "source": f"ppc_section_{section_num}"
        })
    
    return corpus

def rebuild_rag_corpus():
    """Main function to rebuild RAG corpus"""
    print("=" * 60)
    print("REBUILDING RAG CORPUS")
    print("=" * 60)
    print()
    
    output_path = Path("data/processed/full_rag_corpus.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    all_docs = []
    
    # Step 1: Try to find training data files
    print("🔍 Step 1: Looking for training data files...")
    training_files = find_training_data_files()
    
    if training_files:
        print(f"\n   Found {len(training_files)} training data file(s)")
        # Use the first (most recent) file
        training_file = training_files[0]
        print(f"   Using: {training_file}")
        
        print(f"\n📚 Loading training data from {training_file}...")
        try:
            with open(training_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            print(f"   ✅ Loaded {len(training_data)} training examples")
            
            # Convert to RAG documents
            print("\n🔄 Converting training data to RAG documents...")
            rag_docs = create_rag_documents_from_training_data(training_data)
            all_docs.extend(rag_docs)
            print(f"   ✅ Created {len(rag_docs)} RAG documents from training data")
            
        except Exception as e:
            print(f"   ❌ Error loading {training_file}: {e}")
            print("   Will create basic corpus instead...")
    else:
        print("   ⚠️  No training data files found")
        print("   Will create basic corpus with essential PPC sections...")
    
    # Step 2: Add basic PPC sections (always add these)
    print("\n🔍 Step 2: Adding essential PPC sections...")
    basic_ppc = create_basic_ppc_corpus()
    all_docs.extend(basic_ppc)
    print(f"   ✅ Added {len(basic_ppc)} essential PPC sections")
    
    # Step 3: Remove duplicates (by text content)
    print("\n🔍 Step 3: Removing duplicates...")
    seen_texts = set()
    unique_docs = []
    for doc in all_docs:
        text_hash = hash(doc['text'][:500])  # Hash first 500 chars
        if text_hash not in seen_texts:
            seen_texts.add(text_hash)
            unique_docs.append(doc)
    
    print(f"   ✅ Removed {len(all_docs) - len(unique_docs)} duplicates")
    print(f"   Final corpus size: {len(unique_docs)} documents")
    
    # Step 4: Save corpus
    print(f"\n💾 Saving RAG corpus to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(unique_docs, f, ensure_ascii=False, indent=2)
    
    print(f"✅ RAG corpus saved!")
    print(f"   Location: {output_path}")
    print(f"   Total documents: {len(unique_docs)}")
    
    # Stats
    print("\n📊 Corpus Statistics:")
    ppc_count = sum(1 for doc in unique_docs if 'ppc' in doc.get('source', '').lower())
    training_count = sum(1 for doc in unique_docs if 'training' in doc.get('source', '').lower())
    
    print(f"   PPC sections: {ppc_count}")
    print(f"   Training data: {training_count}")
    print(f"   Other: {len(unique_docs) - ppc_count - training_count}")
    
    print("\n" + "=" * 60)
    print("✅ REBUILD COMPLETE")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print("   1. Run: python clean_rag_corpus.py")
    print("   2. Test: python test_chatbot_v5.py")

if __name__ == "__main__":
    rebuild_rag_corpus()























