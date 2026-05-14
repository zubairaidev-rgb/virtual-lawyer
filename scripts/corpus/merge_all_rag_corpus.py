"""
Merge all RAG corpus sources into one comprehensive corpus
Combines: PPC, SHC cases, CrPC, Constitution, new PDFs, structured data
"""
import json
from pathlib import Path
from typing import List, Dict

class RAGCorpusMerger:
    """Merge all RAG sources into comprehensive corpus"""
    
    def __init__(self,
                 output_path="data/processed/comprehensive_rag_corpus.json"):
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Define all corpus sources
        self.corpus_sources = {
            'ppc': 'data/processed/ppc_sections.json',
            'shc_cases': 'data/processed/shc_cases_rag.json',
            'crpc': 'data/processed/crpc_sections.json',
            'constitution': 'data/processed/constitution_articles.json',
            'new_pdfs': 'data/processed/new_pdfs_rag.json',
            'structured_data': 'data/processed/structured_data_rag.json',
            'full_rag_corpus': 'data/processed/full_rag_corpus.json',  # Existing
        }
    
    def load_corpus(self, path: str) -> List[Dict]:
        """Load a corpus file"""
        file_path = Path(path)
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"   ⚠️  Error loading {path}: {e}")
            return []
    
    def merge_all_corpora(self) -> List[Dict]:
        """Merge all corpus sources"""
        print("=" * 60)
        print("MERGING ALL RAG CORPUS SOURCES")
        print("=" * 60)
        print()
        
        all_docs = []
        stats = {}
        
        # Load each corpus
        for name, path in self.corpus_sources.items():
            print(f"📚 Loading {name}...")
            docs = self.load_corpus(path)
            
            if docs:
                # Add source tag to metadata
                for doc in docs:
                    if 'metadata' not in doc:
                        doc['metadata'] = {}
                    doc['metadata']['source_corpus'] = name
                
                all_docs.extend(docs)
                stats[name] = len(docs)
                print(f"   ✅ Loaded {len(docs)} documents")
            else:
                stats[name] = 0
                print(f"   ⚠️  No documents found or file doesn't exist")
        
        print(f"\n✅ Total documents: {len(all_docs)}")
        
        # Remove duplicates (by text content)
        print("\n🔄 Removing duplicates...")
        seen_texts = set()
        unique_docs = []
        
        for doc in all_docs:
            text = doc.get('text', '')
            # Create hash of first 200 chars for duplicate detection
            text_hash = hash(text[:200])
            
            if text_hash not in seen_texts:
                seen_texts.add(text_hash)
                unique_docs.append(doc)
        
        removed = len(all_docs) - len(unique_docs)
        print(f"   Removed {removed} duplicates")
        print(f"   Unique documents: {len(unique_docs)}")
        
        # Save merged corpus
        print(f"\n💾 Saving merged corpus to {self.output_path}...")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(unique_docs, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(unique_docs)} unique documents")
        
        # Statistics
        print("\n📊 Statistics by source:")
        for name, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"   {name}: {count} documents")
        
        # Statistics by type
        print("\n📊 Statistics by document type:")
        types = {}
        for doc in unique_docs:
            doc_type = doc.get('type', 'unknown')
            types[doc_type] = types.get(doc_type, 0) + 1
        
        for doc_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            print(f"   {doc_type}: {count} documents")
        
        return unique_docs

if __name__ == "__main__":
    merger = RAGCorpusMerger()
    merger.merge_all_corpora()





















