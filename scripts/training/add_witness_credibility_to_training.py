"""
Add Witness Credibility Dataset to Training Data
Converts the witness credibility Q&A into fine-tuning format
"""
import json
import os

def convert_to_training_format():
    """Convert witness credibility dataset to training format"""
    
    # Load witness credibility dataset
    witness_path = "./data/training/witness_credibility_dataset.json"
    
    if not os.path.exists(witness_path):
        print(f"Error: {witness_path} not found!")
        return
    
    with open(witness_path, 'r', encoding='utf-8') as f:
        witness_data = json.load(f)
    
    # Load existing training data
    training_path = "./data/training/golden_training_data.json"
    
    if os.path.exists(training_path):
        with open(training_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    
    # Convert witness data to training format
    training_examples = []
    
    for item in witness_data:
        question = item['question']
        answer = item['answer']
        
        # Format as prompt-completion
        prompt = f"Question: {question}\nAnswer:"
        completion = f" {answer}"
        
        training_examples.append({
            "prompt": prompt,
            "completion": completion,
            "source": "witness_credibility",
            "category": item.get('category', 'witness_credibility'),
            "keywords": item.get('keywords', [])
        })
    
    # Merge with existing data
    all_data = existing_data + training_examples
    
    # Save
    with open(training_path, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"SUCCESS: Added {len(training_examples)} witness credibility examples")
    print(f"   Total training examples: {len(all_data)}")
    print(f"   Saved to: {training_path}")

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING WITNESS CREDIBILITY DATASET TO TRAINING")
    print("=" * 60)
    print()
    
    convert_to_training_format()
    
    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review training data")
    print("2. Fine-tune model on updated data")
    print("3. Test witness credibility questions")

