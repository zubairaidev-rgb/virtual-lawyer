"""
Process new PDFs from new_search_data folder to RAG corpus
Handles multiple PDFs about bail, forensic science, criminal law, QSO, etc.
"""
import json
import re
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import os

# Try to import PDF library (prefer pdfplumber, fallback to PyMuPDF)
PDF_LIBRARY = None
try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
    print("✅ Using pdfplumber for PDF processing")
except ImportError:
    try:
        import fitz  # PyMuPDF
        PDF_LIBRARY = 'fitz'
        print("✅ Using PyMuPDF (fitz) for PDF processing")
    except ImportError:
        PDF_LIBRARY = None
        print("⚠️  WARNING: No PDF library found!")
        print("   Install one of:")
        print("   - pip install pdfplumber  (recommended, already in requirements.txt)")
        print("   - pip install PyMuPDF")

class NewPDFProcessor:
    """Process new PDFs to RAG format"""
    
    def __init__(self, 
                 input_dir="data/raw/new_search_data",
                 output_path="data/processed/new_pdfs_rag.json"):
        self.input_dir = Path(input_dir)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict:
        """Extract text from a single PDF"""
        if PDF_LIBRARY is None:
            print(f"   ⚠️  Cannot process {pdf_path.name}: No PDF library installed")
            print(f"      Install: pip install pdfplumber")
            return None
        
        try:
            text_chunks = []
            page_count = 0
            
            if PDF_LIBRARY == 'pdfplumber':
                # Use pdfplumber (already in requirements.txt)
                with pdfplumber.open(str(pdf_path)) as pdf:
                    page_count = len(pdf.pages)
                    for page_num, page in enumerate(pdf.pages):
                        try:
                            text = page.extract_text()
                            if text and text.strip():
                                text_chunks.append(text.strip())
                        except Exception as page_error:
                            print(f"      ⚠️  Error on page {page_num + 1}: {page_error}")
                            continue
            
            elif PDF_LIBRARY == 'fitz':
                # Use PyMuPDF (fitz)
                doc = fitz.open(str(pdf_path))
                page_count = len(doc)
                
                for page_num in range(page_count):
                    try:
                        page = doc[page_num]
                        text = page.get_text()
                        if text and text.strip():
                            text_chunks.append(text.strip())
                    except Exception as page_error:
                        print(f"      ⚠️  Error on page {page_num + 1}: {page_error}")
                        continue
                
                doc.close()
            
            # Combine all text
            full_text = "\n".join(text_chunks)
            
            if not full_text.strip():
                print(f"   ⚠️  No text extracted from {pdf_path.name}")
                return None
            
            return {
                "filename": pdf_path.name,
                "text": full_text,
                "pages": page_count,
                "char_count": len(full_text)
            }
        except Exception as e:
            print(f"   ⚠️  Error processing {pdf_path.name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def categorize_pdf(self, filename: str, text: str) -> str:
        """Categorize PDF based on filename and content"""
        filename_lower = filename.lower()
        text_lower = text.lower()[:1000]  # Check first 1000 chars
        
        # Category detection
        if 'bail' in filename_lower or 'bail' in text_lower:
            return 'bail'
        elif 'forensic' in filename_lower or 'forensic' in text_lower:
            return 'forensic_medicine'
        elif 'qanun' in filename_lower or 'qso' in filename_lower or 'evidence' in filename_lower:
            return 'qso_evidence'
        elif 'penal code' in filename_lower or 'ppc' in filename_lower:
            return 'ppc'
        elif 'jurisdiction' in filename_lower:
            return 'jurisdiction'
        elif 'criminal' in filename_lower:
            return 'criminal_law_general'
        else:
            return 'general'
    
    def extract_key_sections(self, text: str, category: str) -> List[Dict]:
        """Extract key sections/chunks from text"""
        chunks = []
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        
        # For each paragraph, create a chunk
        for i, para in enumerate(paragraphs):
            if len(para) < 100:  # Skip too short
                continue
            
            # Limit chunk size (2000 chars max)
            if len(para) > 2000:
                # Split long paragraphs
                words = para.split()
                current_chunk = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) > 2000:
                        if current_chunk:
                            chunks.append({
                                "text": ' '.join(current_chunk),
                                "chunk_index": len(chunks)
                            })
                        current_chunk = [word]
                        current_length = len(word)
                    else:
                        current_chunk.append(word)
                        current_length += len(word) + 1
                
                if current_chunk:
                    chunks.append({
                        "text": ' '.join(current_chunk),
                        "chunk_index": len(chunks)
                    })
            else:
                chunks.append({
                    "text": para,
                    "chunk_index": len(chunks)
                })
        
        return chunks
    
    def extract_legal_principles(self, text: str) -> List[str]:
        """Extract legal principles mentioned in text"""
        principles = []
        
        # Look for common legal principle patterns
        patterns = [
            r'(?:principle|rule|doctrine|maxim)[\s:]+([^\.]+)',
            r'(?:established|held|decided)[\s:]+([^\.]+)',
            r'(?:court|judge)[\s]+(?:held|observed|stated)[\s:]+([^\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            principles.extend([m.strip() for m in matches if len(m.strip()) > 20])
        
        return list(set(principles[:10]))  # Limit to 10 unique
    
    def extract_case_citations(self, text: str) -> List[str]:
        """Extract case citations from text"""
        citations = []
        
        # Patterns for case citations
        patterns = [
            r'\d{4}\s+SCMR\s+\d+',  # 2020 SCMR 316
            r'PLD\s+\d{4}\s+SC\s+\d+',  # PLD 2009 SC 45
            r'\d{4}\s+YLR\s+\d+',  # 2020 YLR 123
            r'PLD\s+\d{4}\s+\w+\s+\d+',  # PLD 2009 Lahore 123
            r'\d{4}\s+MLD\s+\d+',  # 2020 MLD 123
            r'\d{4}\s+PCrLJ\s+\d+',  # 2020 PCrLJ 123
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)
        
        return list(set(citations))
    
    def create_rag_documents(self, pdf_data: Dict) -> List[Dict]:
        """Create RAG documents from PDF data"""
        rag_docs = []
        
        filename = pdf_data['filename']
        text = pdf_data['text']
        category = self.categorize_pdf(filename, text)
        
        # Extract metadata
        principles = self.extract_legal_principles(text)
        citations = self.extract_case_citations(text)
        
        # Extract sections/chunks
        chunks = self.extract_key_sections(text, category)
        
        # Create RAG documents
        for chunk in chunks:
            # Create title
            title_words = chunk['text'][:100].split()[:10]
            title = ' '.join(title_words) + '...' if len(chunk['text']) > 100 else chunk['text']
            
            rag_doc = {
                "text": chunk['text'],
                "title": title,
                "source": f"new_pdf_{Path(filename).stem}",
                "type": category,
                "metadata": {
                    "filename": filename,
                    "category": category,
                    "chunk_index": chunk['chunk_index'],
                    "principles": principles,
                    "citations": citations,
                    "char_count": len(chunk['text'])
                }
            }
            
            rag_docs.append(rag_doc)
        
        return rag_docs
    
    def process_all_pdfs(self) -> List[Dict]:
        """Process all PDFs in input directory"""
        print("=" * 60)
        print("PROCESSING NEW PDFs TO RAG CORPUS")
        print("=" * 60)
        print()
        
        # Check if PDF library is available
        if PDF_LIBRARY is None:
            print("=" * 60)
            print("ERROR: No PDF library installed!")
            print("=" * 60)
            print("\nPlease install pdfplumber (recommended):")
            print("   pip install pdfplumber")
            print("\nOr install PyMuPDF:")
            print("   pip install PyMuPDF")
            print("\nAfter installing, run this script again.")
            print("=" * 60)
            return []
        
        print(f"Using {PDF_LIBRARY} for PDF processing")
        
        # Find all PDFs
        pdf_files = list(self.input_dir.glob("*.pdf"))
        print(f"📚 Found {len(pdf_files)} PDF files")
        
        if not pdf_files:
            print("❌ No PDF files found!")
            return []
        
        all_rag_docs = []
        
        # Process each PDF
        for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
            print(f"\n📄 Processing: {pdf_file.name}")
            
            # Extract text
            pdf_data = self.extract_text_from_pdf(pdf_file)
            if not pdf_data:
                continue
            
            print(f"   Extracted {pdf_data['pages']} pages, {pdf_data['char_count']} characters")
            
            # Create RAG documents
            rag_docs = self.create_rag_documents(pdf_data)
            all_rag_docs.extend(rag_docs)
            
            print(f"   Created {len(rag_docs)} RAG documents")
        
        print(f"\n✅ Total RAG documents created: {len(all_rag_docs)}")
        
        # Save
        print(f"\n💾 Saving to {self.output_path}...")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(all_rag_docs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(all_rag_docs)} RAG documents")
        
        # Statistics by category
        print("\n📊 Statistics by category:")
        categories = {}
        for doc in all_rag_docs:
            cat = doc.get('type', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count} documents")
        
        return all_rag_docs

if __name__ == "__main__":
    processor = NewPDFProcessor()
    processor.process_all_pdfs()

