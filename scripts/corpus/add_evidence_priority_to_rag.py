"""
Add Evidence Priority Legal Principle to RAG Corpus
This script adds the correct information about evidence priority to your RAG corpus
"""
import json
import os

def add_evidence_priority_to_rag():
    """Add evidence priority principle to RAG corpus"""
    
    # Correct legal principle entry
    evidence_priority_entry = {
        "text": """Evidence Priority Rule in Pakistani Criminal Law:

PRIMARY RULE: Ocular (eyewitness) evidence has PRIMACY over medical evidence in Pakistani criminal law.

DETAILED EXPLANATION:
1. Ocular evidence is PRIMARY: Trustworthy eyewitness testimony prevails over medical evidence
2. Medical evidence is CORROBORATIVE: It supports or challenges the ocular account but cannot override it
3. Exception: Medical evidence only overrides ocular evidence when it makes the prosecution story IMPOSSIBLE
4. Benefit of doubt: Only when medical evidence completely destroys the possibility of the prosecution version should the benefit of doubt go to the accused

ESTABLISHED PRECEDENTS:
- 2020 SCMR 316: "Where ocular evidence is trustworthy and confidence-inspiring, medical evidence cannot override it unless it makes the ocular version impossible."
- 2019 SCMR 1362: "Medical evidence is always corroborative; it cannot by itself determine guilt if ocular account is reliable."
- PLD 2009 SC 45 (Zafar Ali case): "If there is conflict, ocular evidence prevails."
- 2017 SCMR 2022: "Only when medical evidence makes the eyewitness account impossible, the benefit of doubt goes to the accused."

APPLICATION:
- When all eyewitnesses support prosecution but medical evidence contradicts: Ocular evidence prevails unless medical makes prosecution impossible
- When medical evidence shows injury impossible: Medical evidence may override
- When medical evidence contradicts time of death: Minor contradictions don't override ocular; only impossible contradictions do

LEGAL BASIS: Supreme Court of Pakistan precedents and established criminal jurisprudence principles.""",
        "title": "Evidence Priority: Ocular vs Medical Evidence in Pakistani Criminal Law",
        "source": "legal_principle_evidence_priority",
        "metadata": {
            "principle": "evidence_priority",
            "cases": ["2020 SCMR 316", "2019 SCMR 1362", "PLD 2009 SC 45", "2017 SCMR 2022"],
            "verified": True,
            "topic": "evidence_law",
            "priority": "high"
        }
    }
    
    # Paths
    corpus_path = "./data/processed/full_rag_corpus.json"
    backup_path = "./data/processed/full_rag_corpus.json.backup"
    
    # Check if corpus exists
    if not os.path.exists(corpus_path):
        print(f"❌ Corpus not found: {corpus_path}")
        print("   Creating new corpus with evidence priority entry...")
        corpus = [evidence_priority_entry]
    else:
        # Backup existing corpus
        print(f"📦 Backing up existing corpus...")
        with open(corpus_path, 'r', encoding='utf-8') as f:
            corpus = json.load(f)
        
        # Save backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(corpus, f, indent=2, ensure_ascii=False)
        print(f"   Backup saved to: {backup_path}")
        
        # Check if entry already exists
        existing_entry = None
        for i, entry in enumerate(corpus):
            if entry.get('source') == 'legal_principle_evidence_priority':
                existing_entry = i
                break
        
        if existing_entry is not None:
            print(f"   Updating existing entry at index {existing_entry}...")
            corpus[existing_entry] = evidence_priority_entry
        else:
            print(f"   Adding new evidence priority entry...")
            corpus.insert(0, evidence_priority_entry)  # Add at beginning for priority
    
    # Save updated corpus
    with open(corpus_path, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Evidence priority principle added to corpus!")
    print(f"   Total entries: {len(corpus)}")
    print(f"   Entry source: {evidence_priority_entry['source']}")
    print(f"\n⚠️  IMPORTANT: You need to rebuild embeddings after this change!")
    print(f"   Run: python -c \"from src.enhanced_rag_system import EnhancedRAGSystem; rag = EnhancedRAGSystem(); rag.load_corpus(); rag.create_embeddings(force_rebuild=True)\"")

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING EVIDENCE PRIORITY PRINCIPLE TO RAG CORPUS")
    print("=" * 60)
    add_evidence_priority_to_rag()
    print("\n" + "=" * 60)
    print("✅ COMPLETE")
    print("=" * 60)






















