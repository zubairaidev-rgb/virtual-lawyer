"""
Clean RAG corpus - remove non-criminal law content, keep only PPC, CrPC, Constitution, and relevant cases
"""
import json
import re
from pathlib import Path

def is_criminal_law_relevant(text: str) -> bool:
    """Check if text is relevant to criminal law"""
    text_lower = text.lower()
    
    # Keywords that indicate criminal law relevance
    criminal_keywords = [
        'ppc', 'penal code', 'criminal procedure', 'crpc', 'cr.p.c',
        'section 302', 'section 376', 'section 420', 'section 395',
        'murder', 'theft', 'robbery', 'rape', 'assault', 'bail',
        'arrest', 'conviction', 'sentence', 'punishment', 'fine',
        'imprisonment', 'cognizable', 'non-cognizable', 'bailable',
        'non-bailable', 'fir', 'first information report',
        'constitution', 'fundamental right', 'article 10', 'article 4'
    ]
    
    # Check if text contains criminal law keywords
    keyword_count = sum(1 for keyword in criminal_keywords if keyword in text_lower)
    
    # Must have at least 2 criminal law keywords
    if keyword_count < 2:
        return False
    
    # Exclude non-criminal law topics
    exclude_keywords = [
        'privatisation', 'commission ordinance', 'telecommunication',
        'electric power', 'gas regulatory', 'banking', 'insurance',
        'tax', 'customs', 'excise', 'income tax', 'sales tax'
    ]
    
    for exclude in exclude_keywords:
        if exclude in text_lower:
            return False
    
    return True

def clean_document(doc: dict) -> dict:
    """Clean a single document"""
    text = doc.get('text', '')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Truncate very long texts (keep first 2000 chars)
    if len(text) > 2000:
        text = text[:2000] + "..."
    
    doc['text'] = text.strip()
    return doc

def clean_rag_corpus():
    """Main cleaning function"""
    input_path = Path("data/processed/full_rag_corpus.json")
    output_path = Path("data/processed/full_rag_corpus_clean.json")
    
    print("=" * 60)
    print("CLEANING RAG CORPUS")
    print("=" * 60)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print()
    
    # Check if input file exists
    if not input_path.exists():
        print(f"❌ Error: {input_path} not found!")
        print()
        print("💡 Solution: Rebuild RAG corpus first by running:")
        print("   python rebuild_rag_corpus.py")
        print()
        return
    
    # Load corpus
    print("📚 Loading corpus...")
    with open(input_path, 'r', encoding='utf-8') as f:
        corpus = json.load(f)
    
    print(f"   Original documents: {len(corpus)}")
    
    # Filter and clean
    print("\n🧹 Cleaning documents...")
    cleaned_corpus = []
    removed_count = 0
    
    for i, doc in enumerate(corpus):
        if i % 1000 == 0:
            print(f"   Processing: {i}/{len(corpus)}")
        
        text = doc.get('text', '')
        
        # Check if relevant
        if is_criminal_law_relevant(text):
            cleaned_doc = clean_document(doc)
            cleaned_corpus.append(cleaned_doc)
        else:
            removed_count += 1
    
    print(f"\n✅ Cleaning complete!")
    print(f"   Kept: {len(cleaned_corpus)} documents")
    print(f"   Removed: {removed_count} documents")
    print(f"   Reduction: {(removed_count/len(corpus)*100):.1f}%")
    
    # Save cleaned corpus
    print(f"\n💾 Saving cleaned corpus...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved to: {output_path}")
    
    # Stats
    print("\n📊 Corpus Statistics:")
    ppc_count = sum(1 for doc in cleaned_corpus if 'ppc' in doc.get('source', '').lower())
    case_count = sum(1 for doc in cleaned_corpus if 'case' in doc.get('source', '').lower())
    constitution_count = sum(1 for doc in cleaned_corpus if 'constitution' in doc.get('source', '').lower())
    crpc_count = sum(1 for doc in cleaned_corpus if 'crpc' in doc.get('source', '').lower() or 'cr.p.c' in doc.get('source', '').lower())
    
    print(f"   PPC sections: {ppc_count}")
    print(f"   CrPC sections: {crpc_count}")
    print(f"   Constitution: {constitution_count}")
    print(f"   Case laws: {case_count}")
    print(f"   Other: {len(cleaned_corpus) - ppc_count - case_count - constitution_count - crpc_count}")

if __name__ == "__main__":
    clean_rag_corpus()

