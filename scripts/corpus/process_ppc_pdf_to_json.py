"""
Process Pakistan Penal Code PDF into structured JSON for RAG
Extracts all sections with proper structure
"""
import fitz  # PyMuPDF
import json
import re
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

class PPCProcessor:
    """Process PPC PDF into structured JSON"""
    
    def __init__(self, pdf_path="Pakistan Penal Code.pdf", output_path="data/processed/ppc_sections.json"):
        self.pdf_path = pdf_path
        self.output_path = output_path
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self) -> str:
        """Extract all text from PPC PDF"""
        print(f"📄 Extracting text from {self.pdf_path}...")
        
        text_chunks = []
        doc = fitz.open(self.pdf_path)
        page_count = len(doc)
        
        try:
            for page_num in tqdm(range(page_count), desc="Extracting pages"):
                page = doc[page_num]
                text = page.get_text()
                text_chunks.append(text)
        finally:
            doc.close()
        
        full_text = "\n".join(text_chunks)
        print(f"✅ Extracted {len(full_text)} characters from {page_count} pages")
        return full_text
    
    def extract_sections(self, text: str) -> List[Dict]:
        """Extract PPC sections from text"""
        print("\n🔍 Extracting PPC sections...")
        
        sections = []
        
        # Pattern to match section numbers and content
        # Matches: "Section 302" or "302." or "302 PPC" etc.
        section_pattern = r'(?:Section\s+)?(\d+[A-Z]?)[\.\s]+(.*?)(?=(?:Section\s+)?\d+[A-Z]?[\.\s]|$)'
        
        # Also try more specific patterns
        patterns = [
            r'Section\s+(\d+[A-Z]?)[\.\:\-]\s*(.*?)(?=Section\s+\d+[A-Z]?|$)',
            r'(\d+[A-Z]?)[\.]\s+(.*?)(?=\d+[A-Z]?[\.]|$)',
        ]
        
        # Find all section matches
        matches = []
        for pattern in patterns:
            matches.extend(re.finditer(pattern, text, re.DOTALL | re.IGNORECASE))
        
        # Process matches
        seen_sections = set()
        for match in matches:
            section_num = match.group(1).strip()
            section_text = match.group(2).strip()
            
            # Skip if too short or already seen
            if len(section_text) < 50 or section_num in seen_sections:
                continue
            
            # Clean section text
            section_text = re.sub(r'\s+', ' ', section_text)
            section_text = section_text[:3000]  # Limit length
            
            # Extract title/description (first sentence or line)
            lines = section_text.split('\n')
            title = lines[0][:100] if lines else f"PPC Section {section_num}"
            
            sections.append({
                "section_number": section_num,
                "title": title,
                "text": section_text,
                "source": f"ppc_section_{section_num}",
                "type": "ppc_section"
            })
            
            seen_sections.add(section_num)
        
        # Also create chunks for sections that might have been missed
        # Split by common section indicators
        chunk_pattern = r'(Section\s+\d+[A-Z]?|^\d+[A-Z]?[\.])'
        chunks = re.split(chunk_pattern, text, flags=re.MULTILINE)
        
        for i in range(1, len(chunks), 2):
            if i + 1 < len(chunks):
                section_num_match = re.search(r'(\d+[A-Z]?)', chunks[i])
                if section_num_match:
                    section_num = section_num_match.group(1)
                    if section_num not in seen_sections and len(chunks[i+1]) > 100:
                        sections.append({
                            "section_number": section_num,
                            "title": f"PPC Section {section_num}",
                            "text": chunks[i+1][:3000],
                            "source": f"ppc_section_{section_num}",
                            "type": "ppc_section"
                        })
                        seen_sections.add(section_num)
        
        print(f"✅ Extracted {len(sections)} PPC sections")
        return sections
    
    def process(self) -> List[Dict]:
        """Main processing function"""
        print("=" * 60)
        print("PROCESSING PAKISTAN PENAL CODE PDF")
        print("=" * 60)
        print()
        
        # Extract text
        text = self.extract_text_from_pdf()
        
        # Extract sections
        sections = self.extract_sections(text)
        
        # Save to JSON
        print(f"\n💾 Saving to {self.output_path}...")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(sections, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(sections)} PPC sections to JSON")
        
        # Statistics
        print("\n📊 Statistics:")
        print(f"   Total sections: {len(sections)}")
        unique_sections = len(set(s['section_number'] for s in sections))
        print(f"   Unique section numbers: {unique_sections}")
        
        return sections

if __name__ == "__main__":
    processor = PPCProcessor()
    processor.process()























