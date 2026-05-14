"""
Process SHC case JSONs into RAG corpus format
Converts scraped case data into structured RAG documents
"""
import json
import re
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

class SHCCaseProcessor:
    """Process SHC case JSONs into RAG format"""
    
    def __init__(self, 
                 input_dir="data/raw/scraped/shc/json",
                 output_path="data/processed/shc_cases_rag.json"):
        self.input_dir = Path(input_dir)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_case_jsons(self) -> List[Dict]:
        """Load all case JSON files"""
        print(f"📚 Loading case JSONs from {self.input_dir}...")
        
        case_files = list(self.input_dir.glob("case_*.json"))
        print(f"   Found {len(case_files)} case files")
        
        cases = []
        for case_file in tqdm(case_files, desc="Loading cases"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    case_data = json.load(f)
                    cases.append(case_data)
            except Exception as e:
                print(f"   ⚠️  Error loading {case_file.name}: {e}")
                continue
        
        print(f"✅ Loaded {len(cases)} cases")
        return cases
    
    def extract_key_information(self, case: Dict) -> Dict:
        """Extract key information from case for RAG"""
        judgment_text = case.get("judgment_text", "")
        case_no = case.get("case_no", "") or case.get("case_year", "")
        parties = case.get("parties", "")
        sections = case.get("sections", [])
        
        # Extract key legal points
        key_points = []
        
        # Extract section references
        section_refs = re.findall(r'Section\s+(\d+[A-Z]?)\s+(?:PPC|CrPC|Cr\.P\.C)', judgment_text, re.IGNORECASE)
        if sections:
            section_refs.extend(sections)
        section_refs = list(set(section_refs))
        
        # Extract important legal terms
        legal_terms = re.findall(r'\b(bail|conviction|acquittal|sentence|punishment|appeal|revision|FIR|remand|confession)\b', judgment_text, re.IGNORECASE)
        
        # Create summary
        # Take first 500 chars as summary
        summary = judgment_text[:500].strip()
        if len(judgment_text) > 500:
            summary += "..."
        
        # Create full text for RAG (limit to 2000 chars for efficiency)
        full_text = judgment_text[:2000] if len(judgment_text) > 2000 else judgment_text
        
        return {
            "case_id": case.get("case_id", ""),
            "case_no": case_no,
            "parties": parties,
            "sections": section_refs,
            "summary": summary,
            "full_text": full_text,
            "legal_terms": list(set(legal_terms)),
            "judgment_date": case.get("order_date", ""),
            "bench": case.get("bench", ""),
            "pdf_url": case.get("pdf_url", ""),
        }
    
    def create_rag_documents(self, cases: List[Dict]) -> List[Dict]:
        """Convert cases to RAG documents"""
        print("\n🔄 Converting cases to RAG documents...")
        
        rag_docs = []
        
        for case in tqdm(cases, desc="Processing cases"):
            try:
                case_info = self.extract_key_information(case)
                
                # Create multiple RAG documents from one case for better retrieval
                
                # Document 1: Full case summary
                rag_docs.append({
                    "text": f"Case: {case_info['case_no']}\nParties: {case_info['parties']}\n\n{case_info['full_text']}",
                    "title": f"SHC Case {case_info['case_no']}",
                    "source": f"shc_case_{case_info['case_id']}",
                    "type": "case_law",
                    "metadata": {
                        "case_id": case_info['case_id'],
                        "case_no": case_info['case_no'],
                        "sections": case_info['sections'],
                        "legal_terms": case_info['legal_terms'],
                        "judgment_date": case_info['judgment_date'],
                        "pdf_url": case_info['pdf_url']
                    }
                })
                
                # Document 2: Section-specific (if sections mentioned)
                if case_info['sections']:
                    for section in case_info['sections']:
                        # Extract text relevant to this section
                        section_text = self._extract_section_relevant_text(case_info['full_text'], section)
                        if section_text:
                            rag_docs.append({
                                "text": f"Case {case_info['case_no']} - Section {section} PPC/CrPC:\n{section_text}",
                                "title": f"SHC Case - Section {section}",
                                "source": f"shc_case_{case_info['case_id']}_section_{section}",
                                "type": "case_law_section",
                                "metadata": {
                                    "case_id": case_info['case_id'],
                                    "section": section,
                                    "case_no": case_info['case_no']
                                }
                            })
                
            except Exception as e:
                print(f"   ⚠️  Error processing case: {e}")
                continue
        
        print(f"✅ Created {len(rag_docs)} RAG documents from {len(cases)} cases")
        return rag_docs
    
    def _extract_section_relevant_text(self, text: str, section: str) -> str:
        """Extract text relevant to a specific section"""
        # Find sentences/paragraphs mentioning the section
        pattern = rf'Section\s+{section}[^\n]*\n(.*?)(?=Section\s+\d+|$)'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0][:1000]  # Limit to 1000 chars
        
        # Fallback: return context around section mention
        section_mention = re.search(rf'Section\s+{section}[^.]*\.(.*?\.)', text, re.IGNORECASE)
        if section_mention:
            return section_mention.group(0)[:1000]
        
        return ""
    
    def process(self) -> List[Dict]:
        """Main processing function"""
        print("=" * 60)
        print("PROCESSING SHC CASES TO RAG FORMAT")
        print("=" * 60)
        print()
        
        # Load cases
        cases = self.load_case_jsons()
        
        if not cases:
            print("❌ No cases found!")
            return []
        
        # Convert to RAG documents
        rag_docs = self.create_rag_documents(cases)
        
        # Save
        print(f"\n💾 Saving to {self.output_path}...")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(rag_docs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(rag_docs)} RAG documents")
        
        # Statistics
        print("\n📊 Statistics:")
        print(f"   Total cases processed: {len(cases)}")
        print(f"   Total RAG documents: {len(rag_docs)}")
        
        # Count by type
        case_law_count = sum(1 for doc in rag_docs if doc.get('type') == 'case_law')
        section_count = sum(1 for doc in rag_docs if doc.get('type') == 'case_law_section')
        print(f"   Case law documents: {case_law_count}")
        print(f"   Section-specific documents: {section_count}")
        
        return rag_docs

if __name__ == "__main__":
    processor = SHCCaseProcessor()
    processor.process()























