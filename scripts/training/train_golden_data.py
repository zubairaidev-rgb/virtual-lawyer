"""
Train Model on Golden Training Data Only
Since model v5 is already trained on previous data, we only train on golden data
"""
import os
import json
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, PeftModel
import bitsandbytes as bnb

class GoldenDataTrainer:
    """Train model on golden training data only"""
    
    def __init__(self, 
                model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                golden_data_path="./data/training/golden_training_data.json",
                base_model_path="./models/final_model_v5",  # Load existing fine-tuned model
                output_dir="./models/fine-tuned/golden_model"):
        
        self.model_name = model_name
        self.golden_data_path = golden_data_path
        self.base_model_path = base_model_path
        self.output_dir = output_dir
        
        os.makedirs(output_dir, exist_ok=True)
    
    def load_model_and_tokenizer(self):
        """Load existing fine-tuned model (v5)"""
        print(f"🤖 Loading existing fine-tuned model from {self.base_model_path}")
        print("   ⚙️  Using 8-bit quantization for memory efficiency...")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        # Load base model in 8-bit
        # Note: Don't use torch_dtype=torch.float16 when training with 8-bit optimizer
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            load_in_8bit=True,
            device_map="auto"
            # torch_dtype removed - let 8-bit quantization handle precision
        )
        
        # Load existing LoRA weights (model v5)
        print(f"   📥 Loading existing LoRA weights from {self.base_model_path}...")
        self.model = PeftModel.from_pretrained(self.model, self.base_model_path)
        
        # Prepare for additional training
        self.model = prepare_model_for_kbit_training(self.model)
        
        # Enable gradient checkpointing to save memory
        if hasattr(self.model, 'gradient_checkpointing_enable'):
            self.model.gradient_checkpointing_enable()
        
        print("✅ Model loaded successfully")
        print(f"   Model size: ~4GB in 8-bit")
        print(f"   Device: {next(self.model.parameters()).device}")
    
    def setup_lora(self):
        """Configure LoRA for additional fine-tuning"""
        print("\n🔧 Setting up LoRA for additional training...")
        
        # Use same LoRA config as original training
        lora_config = LoraConfig(
            r=16,  # Rank
            lora_alpha=32,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        # Model already has LoRA, we'll continue training on it
        self.model.print_trainable_parameters()
        
        print("✅ LoRA ready for additional training")
    
    def prepare_golden_dataset(self):
        """Load and prepare golden training dataset"""
        print(f"\n📚 Loading golden training data from {self.golden_data_path}...")

        with open(self.golden_data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} golden training examples")

        # Format for training
        def format_example(example):
            text = example['prompt'] + example['completion']
            return {"text": text}

        formatted_data = [format_example(ex) for ex in data]

        # Create HuggingFace dataset
        dataset = Dataset.from_list(formatted_data)

        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=512,
                padding="max_length"
            )

        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )

        # Split into train/eval (90/10 split)
        split = tokenized_dataset.train_test_split(test_size=0.1)
        self.train_dataset = split['train']
        self.eval_dataset = split['test']

        print(f"✅ Golden dataset prepared:")
        print(f"   Train: {len(self.train_dataset)} examples")
        print(f"   Eval: {len(self.eval_dataset)} examples")

        return self.train_dataset, self.eval_dataset
    
    def train(self, num_epochs=3, batch_size=1, gradient_accumulation_steps=4):
        """Train the model on golden data"""
        print("\n🚀 Starting training on golden data...")
        print(f"   Epochs: {num_epochs}")
        print(f"   Batch size: {batch_size}")
        print(f"   Gradient accumulation: {gradient_accumulation_steps}")
        print(f"   Effective batch size: {batch_size * gradient_accumulation_steps}")
        print(f"   Training examples: {len(self.train_dataset)}")
        
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            learning_rate=2e-4,  # Slightly lower for fine-tuning on fine-tuned model
            fp16=False,  # Disable fp16 when using 8-bit optimizer (causes AssertionError)
            bf16=False,  # Disable bf16 as well to avoid conflicts
            logging_steps=10,
            eval_strategy="steps",
            eval_steps=50,
            save_steps=100,
            save_total_limit=3,
            load_best_model_at_end=True,
            report_to="none",
            optim="paged_adamw_8bit",
            gradient_checkpointing=True,
            dataloader_pin_memory=False  # Can help with memory issues
        )
        
        data_collator = DataCollatorForLanguageModeling(tokenizer=self.tokenizer, mlm=False)
        
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=self.train_dataset,
            eval_dataset=self.eval_dataset,
            data_collator=data_collator
        )
        
        print("\n⏳ Training on golden data...")
        print("   This will improve the model with high-quality examples")
        print("   Note: Using full precision (no fp16) to avoid optimizer conflicts")
        
        trainer.train()
        
        print("\n✅ Training complete!")
        
        final_path = os.path.join(self.output_dir, "final_golden_model")
        trainer.save_model(final_path)
        self.tokenizer.save_pretrained(final_path)
        
        print(f"✅ Model saved to: {final_path}")
        print(f"\n📝 Next steps:")
        print(f"   1. Update model path in api_complete.py to: {final_path}")
        print(f"   2. Test the model with problematic questions")
        print(f"   3. Verify improvements in legal accuracy")
    
    def run_full_pipeline(self):
        """Run complete training pipeline"""
        print("=" * 60)
        print("TRAINING ON GOLDEN DATA ONLY")
        print("=" * 60)
        print("\nThis will:")
        print("  1. Load existing fine-tuned model (v5)")
        print("  2. Train ONLY on golden training data")
        print("  3. Save as new model with golden data improvements")
        print()
        
        # 1. Load model
        self.load_model_and_tokenizer()
        
        # 2. Setup LoRA (already configured, just verify)
        self.setup_lora()
        
        # 3. Prepare golden dataset
        self.prepare_golden_dataset()
        
        # 4. Train
        self.train()
        
        print("\n" + "=" * 60)
        print("✅ GOLDEN DATA TRAINING COMPLETE!")
        print("=" * 60)

if __name__ == "__main__":
    trainer = GoldenDataTrainer()
    trainer.run_full_pipeline()

