"""
Add Evidence Priority Data to MultiSourceRAG Sources
Since system uses MultiSourceRAG, we need to add evidence priority data to one of its sources
"""
import json
import os

def add_evidence_priority_to_structured_data():
    """Add evidence priority principle to structured_data_rag.json"""
    
    evidence_priority_doc = {
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
        "category": "evidence_law",
        "keywords": ["ocular evidence", "medical evidence", "priority", "primacy", "eyewitness", "corroborative"]
    }
    
    # Load existing structured data
    structured_path = "./data/processed/structured_data_rag.json"
    
    if os.path.exists(structured_path):
        with open(structured_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []
    
    # Check if already exists
    exists = any(
        doc.get('source') == 'legal_principle_evidence_priority' 
        for doc in data
    )
    
    if not exists:
        data.append(evidence_priority_doc)
        
        # Save
        with open(structured_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"SUCCESS: Added evidence priority document to {structured_path}")
        print(f"   Total documents: {len(data)}")
    else:
        print("SUCCESS: Evidence priority document already exists")
    
    return evidence_priority_doc

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING EVIDENCE PRIORITY TO MULTISOURCE RAG")
    print("=" * 60)
    print()
    
    doc = add_evidence_priority_to_structured_data()
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Restart API to reload RAG")
    print("2. Test evidence priority question")
    print("3. RAG should now find this document")

