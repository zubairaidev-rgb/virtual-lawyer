"""
Add Witness Credibility Principles to RAG Corpus
Converts witness credibility principles into RAG documents
"""
import json
import os

def add_witness_credibility_principles():
    """Add witness credibility principles to RAG corpus"""
    
    # Load witness credibility dataset
    witness_path = "./data/training/witness_credibility_dataset.json"
    
    if not os.path.exists(witness_path):
        print(f"Error: {witness_path} not found!")
        return
    
    with open(witness_path, 'r', encoding='utf-8') as f:
        witness_data = json.load(f)
    
    # Load structured data RAG corpus
    rag_path = "./data/processed/structured_data_rag.json"
    
    if os.path.exists(rag_path):
        with open(rag_path, 'r', encoding='utf-8') as f:
            rag_data = json.load(f)
    else:
        rag_data = []
    
    # Convert witness Q&A to RAG documents
    rag_documents = []
    
    for item in witness_data:
        question = item['question']
        answer = item['answer']
        keywords = item.get('keywords', [])
        
        # Create RAG document
        text = f"Question: {question}\n\nAnswer: {answer}\n\nLegal Principle: This principle is used by Pakistani courts to assess witness credibility in criminal cases."
        
        rag_documents.append({
            "text": text,
            "title": f"Witness Credibility: {question[:50]}...",
            "source": "witness_credibility_principle",
            "category": "witness_credibility",
            "keywords": keywords,
            "question": question,
            "answer": answer
        })
    
    # Add summary document
    summary_text = """Witness Credibility Assessment in Pakistani Criminal Law:

PRIMARY TEST: Court evaluates whether witness is truthful, consistent, unbiased, and confidence-inspiring.

MATERIAL VS MINOR CONTRADICTIONS:
- Minor discrepancies (memory, timing, perception) do not destroy credibility
- Material contradictions (identity, weapon, occurrence) make testimony unreliable

INDEPENDENT CORROBORATION:
- When contradictions exist, court seeks corroboration from medical evidence, recovery, forensic evidence, FIR, or circumstances

INTERESTED/RELATED WITNESSES:
- Interested witness: Has personal stake (enmity, relationship, monetary incentive) - scrutinized more strictly
- Related witness: Family member - admissible but requires strict scrutiny
- Relationship alone does not disqualify - consistency and corroboration matter

CONTRADICTING WITNESSES:
- Court accepts version supported by independent evidence (medical, physical, probabilities)
- If doubt remains, accused gets benefit of doubt
- Both witnesses can be disbelieved if both create reasonable doubt

OCULAR VS MEDICAL EVIDENCE:
- Material medical contradictions prevail
- If medical evidence is silent/non-specific → ocular prevails
- Ocular evidence has primacy only when trustworthy, consistent, and confidence-inspiring

SPECIAL CASES:
- Hostile witness: Portions consistent with other evidence may be considered
- Child witness: Court ensures understanding of truth/falsehood, no tutoring
- Police witness: Requires independent corroboration, especially in recovery matters
- Tutored witness: Mechanical, unnatural replies rejected unless corroborated
- Trauma-affected witness: Court tolerates non-material inconsistencies

BENEFIT OF DOUBT:
- If contradictions create reasonable doubt, accused gets benefit of doubt
- Fundamental contradictions → credibility collapses → benefit of doubt"""
    
    rag_documents.append({
        "text": summary_text,
        "title": "Witness Credibility Assessment - Complete Guide",
        "source": "witness_credibility_summary",
        "category": "witness_credibility",
        "keywords": ["witness credibility", "contradictions", "corroboration", "benefit of doubt", "material contradictions"]
    })
    
    # Merge with existing data
    all_rag = rag_data + rag_documents
    
    # Save
    with open(rag_path, 'w', encoding='utf-8') as f:
        json.dump(all_rag, f, indent=2, ensure_ascii=False)
    
    print(f"SUCCESS: Added {len(rag_documents)} witness credibility documents to RAG")
    print(f"   Total RAG documents: {len(all_rag)}")
    print(f"   Saved to: {rag_path}")

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING WITNESS CREDIBILITY TO RAG CORPUS")
    print("=" * 60)
    print()
    
    add_witness_credibility_principles()
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Rebuild RAG embeddings")
    print("2. Test witness credibility questions")
    print("3. Model should now answer correctly")

