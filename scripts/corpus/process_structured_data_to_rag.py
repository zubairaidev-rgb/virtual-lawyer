"""
Process structured JSON data from Claude to RAG corpus
Handles: principles, Q&A, case summaries, negative examples
"""
import json
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

class StructuredDataProcessor:
    """Process structured JSON data to RAG format"""
    
    def __init__(self,
                 input_dir="data/processed/structure data_generated bu claude",
                 output_path="data/processed/structured_data_rag.json"):
        self.input_dir = Path(input_dir)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def process_principles(self, principles_data: List[Dict]) -> List[Dict]:
        """Process legal principles to RAG format"""
        rag_docs = []
        
        for principle in principles_data:
            # Create comprehensive text
            text_parts = [
                f"Legal Principle: {principle.get('principle_name', 'Unknown')}",
                f"Category: {principle.get('category', 'general')}",
                f"\nExplanation: {principle.get('explanation', '')}",
            ]
            
            if principle.get('application'):
                text_parts.append(f"\nApplication: {principle.get('application')}")
            
            if principle.get('islamic_basis'):
                text_parts.append(f"\nIslamic Basis: {principle.get('islamic_basis')}")
            
            if principle.get('citations'):
                citations_str = ', '.join(principle.get('citations', []))
                text_parts.append(f"\nCitations: {citations_str}")
            
            if principle.get('wrong_application'):
                text_parts.append(f"\nWrong Application (Avoid): {principle.get('wrong_application')}")
            
            text = '\n'.join(text_parts)
            
            rag_doc = {
                "text": text,
                "title": principle.get('principle_name', 'Legal Principle'),
                "source": f"principle_{principle.get('id', 'unknown')}",
                "type": "legal_principle",
                "metadata": {
                    "principle_id": principle.get('id'),
                    "category": principle.get('category'),
                    "citations": principle.get('citations', []),
                    "verified": True
                }
            }
            
            rag_docs.append(rag_doc)
        
        return rag_docs
    
    def process_qa(self, qa_data: List[Dict]) -> List[Dict]:
        """Process Q&A pairs to RAG format"""
        rag_docs = []
        
        for qa in qa_data:
            # Create text with question and answer
            text = f"Question: {qa.get('question', '')}\n\nAnswer: {qa.get('answer', '')}"
            
            if qa.get('citations'):
                citations_str = ', '.join(qa.get('citations', []))
                text += f"\n\nCitations: {citations_str}"
            
            if qa.get('principles'):
                principles_str = ', '.join(qa.get('principles', []))
                text += f"\n\nRelated Principles: {principles_str}"
            
            rag_doc = {
                "text": text,
                "title": qa.get('question', '')[:100],
                "source": f"qa_{qa.get('id', 'unknown')}",
                "type": "qa_pair",
                "metadata": {
                    "qa_id": qa.get('id'),
                    "category": qa.get('category'),
                    "citations": qa.get('citations', []),
                    "principles": qa.get('principles', []),
                    "verified": True
                }
            }
            
            rag_docs.append(rag_doc)
        
        return rag_docs
    
    def process_case_summaries(self, summaries_data: List[Dict]) -> List[Dict]:
        """Process case summaries to RAG format"""
        rag_docs = []
        
        for case in summaries_data:
            text_parts = [
                f"Case: {case.get('case_name', 'Unknown Case')}",
                f"Citation: {case.get('citation', 'N/A')}",
                f"\nSummary: {case.get('summary', '')}",
            ]
            
            if case.get('key_principle'):
                text_parts.append(f"\nKey Principle: {case.get('key_principle')}")
            
            if case.get('sections'):
                sections_str = ', '.join(case.get('sections', []))
                text_parts.append(f"\nRelevant Sections: {sections_str}")
            
            text = '\n'.join(text_parts)
            
            rag_doc = {
                "text": text,
                "title": case.get('case_name', 'Case Summary'),
                "source": f"case_summary_{case.get('id', 'unknown')}",
                "type": "case_summary",
                "metadata": {
                    "case_id": case.get('id'),
                    "citation": case.get('citation'),
                    "sections": case.get('sections', []),
                    "verified": True
                }
            }
            
            rag_docs.append(rag_doc)
        
        return rag_docs
    
    def process_negative_examples(self, negative_data: List[Dict]) -> List[Dict]:
        """Process negative examples to RAG format (for training, not RAG)"""
        # Negative examples are for training, but we can create RAG docs explaining why they're wrong
        rag_docs = []
        
        for neg in negative_data:
            text = f"WRONG ANSWER (Do NOT use): {neg.get('wrong_answer', '')}\n\n"
            text += f"CORRECT ANSWER: {neg.get('correct_answer', '')}\n\n"
            text += f"Why Wrong: {neg.get('why_wrong', '')}"
            
            if neg.get('citations'):
                citations_str = ', '.join(neg.get('citations', []))
                text += f"\n\nCorrect Citations: {citations_str}"
            
            rag_doc = {
                "text": text,
                "title": f"Common Error: {neg.get('category', 'general')}",
                "source": f"negative_example_{neg.get('id', 'unknown')}",
                "type": "error_correction",
                "metadata": {
                    "negative_id": neg.get('id'),
                    "category": neg.get('category'),
                    "correct_principle": neg.get('correct_principle'),
                    "verified": True
                }
            }
            
            rag_docs.append(rag_doc)
        
        return rag_docs
    
    def process_all_files(self) -> List[Dict]:
        """Process all structured JSON files"""
        print("=" * 60)
        print("PROCESSING STRUCTURED DATA TO RAG CORPUS")
        print("=" * 60)
        print()
        
        all_rag_docs = []
        
        # Process each file
        json_files = {
            "pak_criminal_principles.json": self.process_principles,
            "pak_criminal_law_qa_part1.json": self.process_qa,
            "pak_criminal_case_summaries.json": self.process_case_summaries,
            "negative_training_examples.json": self.process_negative_examples,
        }
        
        for filename, processor_func in json_files.items():
            file_path = self.input_dir / filename
            
            if not file_path.exists():
                print(f"⚠️  File not found: {filename}")
                continue
            
            print(f"\n📄 Processing: {filename}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"   Loaded {len(data)} items")
                
                # Process
                rag_docs = processor_func(data)
                all_rag_docs.extend(rag_docs)
                
                print(f"   Created {len(rag_docs)} RAG documents")
                
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
                continue
        
        print(f"\n✅ Total RAG documents created: {len(all_rag_docs)}")
        
        # Save
        print(f"\n💾 Saving to {self.output_path}...")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(all_rag_docs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(all_rag_docs)} RAG documents")
        
        # Statistics by type
        print("\n📊 Statistics by type:")
        types = {}
        for doc in all_rag_docs:
            doc_type = doc.get('type', 'unknown')
            types[doc_type] = types.get(doc_type, 0) + 1
        
        for doc_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"   {doc_type}: {count} documents")
        
        return all_rag_docs

if __name__ == "__main__":
    processor = StructuredDataProcessor()
    processor.process_all_files()





















