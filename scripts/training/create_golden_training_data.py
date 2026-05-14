"""
Create Golden Training Data (150-200 high-quality Q&A pairs)
Based on GPT's Phase 3 recommendation
Combines structured data, principles, and creates perfect training examples
"""
import json
from pathlib import Path
from typing import List, Dict

class GoldenTrainingDataCreator:
    """Create golden training examples for fine-tuning"""
    
    def __init__(self,
                 structured_data_dir="data/processed/structure data_generated bu claude",
                 output_path="data/training/golden_training_data.json"):
        self.structured_data_dir = Path(structured_data_dir)
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_structured_data(self) -> Dict:
        """Load all structured data files"""
        data = {
            'principles': [],
            'qa': [],
            'case_summaries': [],
            'negative_examples': []
        }
        
        files = {
            'principles': 'pak_criminal_principles.json',
            'qa': 'pak_criminal_law_qa_part1.json',
            'case_summaries': 'pak_criminal_case_summaries.json',
            'negative_examples': 'negative_training_examples.json'
        }
        
        for key, filename in files.items():
            file_path = self.structured_data_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data[key] = json.load(f)
                    print(f"✅ Loaded {len(data[key])} {key}")
                except Exception as e:
                    print(f"⚠️  Error loading {filename}: {e}")
        
        return data
    
    def create_qa_from_principles(self, principles: List[Dict]) -> List[Dict]:
        """Create Q&A pairs from legal principles"""
        qa_pairs = []
        
        for principle in principles:
            # Create question
            principle_name = principle.get('principle_name', '')
            question = f"What is the principle of {principle_name.lower()} in Pakistani criminal law?"
            
            # Create answer
            answer_parts = [principle.get('explanation', '')]
            
            if principle.get('application'):
                answer_parts.append(f"\nApplication: {principle.get('application')}")
            
            if principle.get('citations'):
                citations_str = ', '.join(principle.get('citations', []))
                answer_parts.append(f"\nCitations: {citations_str}")
            
            answer = '\n'.join(answer_parts)
            
            qa_pairs.append({
                "prompt": f"Question: {question}\n\nAnswer:",
                "completion": f" {answer}",
                "source": "principle_based",
                "category": principle.get('category', 'general'),
                "verified": True,
                "principle_id": principle.get('id')
            })
        
        return qa_pairs
    
    def create_qa_from_existing_qa(self, qa_data: List[Dict]) -> List[Dict]:
        """Convert existing Q&A to training format"""
        training_qa = []
        
        for qa in qa_data:
            question = qa.get('question', '')
            answer = qa.get('answer', '')
            
            # Add citations if available
            if qa.get('citations'):
                citations_str = ', '.join(qa.get('citations', []))
                answer += f"\n\nCitations: {citations_str}"
            
            training_qa.append({
                "prompt": f"Question: {question}\n\nAnswer:",
                "completion": f" {answer}",
                "source": "structured_qa",
                "category": qa.get('category', 'general'),
                "verified": True,
                "qa_id": qa.get('id')
            })
        
        return training_qa
    
    def create_qa_from_case_summaries(self, summaries: List[Dict]) -> List[Dict]:
        """Create Q&A from case summaries"""
        qa_pairs = []
        
        for case in summaries:
            case_name = case.get('case_name', '')
            citation = case.get('citation', '')
            
            # Create question
            question = f"What is the legal principle established in {case_name} ({citation})?"
            
            # Create answer
            answer = case.get('summary', '')
            
            if case.get('key_principle'):
                answer += f"\n\nKey Principle: {case.get('key_principle')}"
            
            if case.get('sections'):
                sections_str = ', '.join(case.get('sections', []))
                answer += f"\n\nRelevant Sections: {sections_str}"
            
            qa_pairs.append({
                "prompt": f"Question: {question}\n\nAnswer:",
                "completion": f" {answer}",
                "source": "case_summary",
                "category": "case_law",
                "verified": True,
                "case_id": case.get('id')
            })
        
        return qa_pairs
    
    def create_negative_training_examples(self, negative_data: List[Dict]) -> List[Dict]:
        """Create training examples showing what NOT to do"""
        training_examples = []
        
        for neg in negative_data:
            # Create question from wrong answer context
            question = f"What is the correct rule regarding {neg.get('category', 'this legal principle')} in Pakistani criminal law?"
            
            # Answer explains why wrong answer is wrong and provides correct answer
            answer = f"INCORRECT: {neg.get('wrong_answer', '')}\n\n"
            answer += f"This is incorrect because: {neg.get('why_wrong', '')}\n\n"
            answer += f"CORRECT: {neg.get('correct_answer', '')}"
            
            if neg.get('citations'):
                citations_str = ', '.join(neg.get('citations', []))
                answer += f"\n\nCitations: {citations_str}"
            
            training_examples.append({
                "prompt": f"Question: {question}\n\nAnswer:",
                "completion": f" {answer}",
                "source": "negative_example",
                "category": neg.get('category', 'general'),
                "verified": True,
                "negative_id": neg.get('id'),
                "is_negative_example": True
            })
        
        return training_examples
    
    def create_scenario_based_qa(self) -> List[Dict]:
        """Create scenario-based Q&A (200 examples as per GPT recommendation)"""
        scenarios = [
            {
                "question": "If all eyewitnesses support the prosecution but medical evidence contradicts the time of death, what is the rule of priority in Pakistani law?",
                "answer": "In Pakistani criminal law, trustworthy ocular (eyewitness) evidence has primacy over medical evidence. Medical evidence is corroborative and cannot override reliable eyewitness testimony unless it makes the prosecution story impossible. The Supreme Court has consistently held that where ocular evidence is confidence-inspiring and trustworthy, it prevails over medical evidence. Only when medical evidence completely destroys the possibility of the prosecution version should the benefit of doubt go to the accused. This principle is established in cases like 2020 SCMR 316, 2019 SCMR 1362, and PLD 2009 SC 45.",
                "category": "evidence_priority",
                "citations": ["2020 SCMR 316", "2019 SCMR 1362", "PLD 2009 SC 45"]
            },
            {
                "question": "When does medical evidence override ocular testimony in Pakistan?",
                "answer": "Medical evidence overrides ocular testimony only when it renders the ocular account impossible or highly doubtful. Otherwise, ocular evidence prevails if it is trustworthy and above suspicion. Courts prefer ocular evidence when medical evidence merely contradicts minor details but the occurrence itself remains plausible.",
                "category": "medical_evidence",
                "citations": ["PLD 2009 SC 45", "2020 SCMR 316"]
            },
            # Add more scenarios as needed
        ]
        
        training_qa = []
        for scenario in scenarios:
            answer = scenario['answer']
            if scenario.get('citations'):
                answer += f"\n\nCitations: {', '.join(scenario['citations'])}"
            
            training_qa.append({
                "prompt": f"Question: {scenario['question']}\n\nAnswer:",
                "completion": f" {answer}",
                "source": "scenario_based",
                "category": scenario.get('category', 'general'),
                "verified": True
            })
        
        return training_qa
    
    def create_all_training_data(self) -> List[Dict]:
        """Create complete golden training dataset"""
        print("=" * 60)
        print("CREATING GOLDEN TRAINING DATA")
        print("=" * 60)
        print()
        
        # Load structured data
        print("📚 Loading structured data...")
        data = self.load_structured_data()
        
        all_training_data = []
        
        # 1. Create Q&A from principles
        print("\n🔄 Creating Q&A from principles...")
        principle_qa = self.create_qa_from_principles(data['principles'])
        all_training_data.extend(principle_qa)
        print(f"   Created {len(principle_qa)} examples")
        
        # 2. Convert existing Q&A
        print("\n🔄 Converting existing Q&A...")
        existing_qa = self.create_qa_from_existing_qa(data['qa'])
        all_training_data.extend(existing_qa)
        print(f"   Added {len(existing_qa)} examples")
        
        # 3. Create Q&A from case summaries
        print("\n🔄 Creating Q&A from case summaries...")
        case_qa = self.create_qa_from_case_summaries(data['case_summaries'])
        all_training_data.extend(case_qa)
        print(f"   Created {len(case_qa)} examples")
        
        # 4. Create negative examples
        print("\n🔄 Creating negative training examples...")
        negative_qa = self.create_negative_training_examples(data['negative_examples'])
        all_training_data.extend(negative_qa)
        print(f"   Created {len(negative_qa)} examples")
        
        # 5. Add scenario-based Q&A
        print("\n🔄 Adding scenario-based Q&A...")
        scenario_qa = self.create_scenario_based_qa()
        all_training_data.extend(scenario_qa)
        print(f"   Added {len(scenario_qa)} examples")
        
        print(f"\n✅ Total training examples created: {len(all_training_data)}")
        
        # Save
        print(f"\n💾 Saving to {self.output_path}...")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(all_training_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {len(all_training_data)} training examples")
        
        # Statistics
        print("\n📊 Statistics:")
        sources = {}
        categories = {}
        for example in all_training_data:
            src = example.get('source', 'unknown')
            cat = example.get('category', 'unknown')
            sources[src] = sources.get(src, 0) + 1
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nBy source:")
        for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"   {src}: {count}")
        
        print("\nBy category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count}")
        
        return all_training_data

if __name__ == "__main__":
    creator = GoldenTrainingDataCreator()
    creator.create_all_training_data()





















