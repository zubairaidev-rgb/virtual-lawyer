"""
Fix adapter_config.json for final_model_v5
Removes unsupported parameters that cause loading errors
"""
import json
from pathlib import Path

def fix_adapter_config():
    """Fix adapter_config.json by removing unsupported parameters"""
    
    config_path = Path("models/final_model_v5/adapter_config.json")
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return
    
    print("=" * 60)
    print("FIXING ADAPTER CONFIG FOR MODEL V5")
    print("=" * 60)
    print(f"File: {config_path}")
    print()
    
    # Load config
    print("Loading config...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"   Original parameters: {len(config)}")
    
    # Parameters to remove (not supported by peft 0.11.1)
    # Keep ONLY the absolute minimum required for LoRA
    unsupported_params = [
        'arrow_config',
        'corda_config',
        'eva_config',
        'auto_mapping',
        'layer_replication',
        'layers_pattern',
        'layers_to_transform',
        'megatron_config',
        'megatron_core',
        'target_parameters',
        'trainable_token_indices',
        'ensure_weight_tying',
        'use_dora',
        'use_qalora',
        'use_rslora',
        'loftq_config',
        'exclude_modules',  # Not supported in 0.11.1
        'alpha_pattern',  # Not supported in 0.11.1
        'rank_pattern',  # Not supported in 0.11.1
        'revision',  # Not needed
        'peft_version',  # Not needed
        'inference_mode',  # Not needed
        'modules_to_save',  # Not needed if null
    ]
    
    # Remove unsupported parameters
    removed = []
    for param in unsupported_params:
        if param in config:
            del config[param]
            removed.append(param)
    
    print(f"   Removed {len(removed)} unsupported parameters:")
    for param in removed:
        print(f"      - {param}")
    
    # Keep ONLY the absolute minimum required for peft 0.11.1
    # These are the core LoRA parameters that MUST exist
    essential_params = {
        'base_model_name_or_path',
        'bias',
        'fan_in_fan_out',
        'init_lora_weights',
        'lora_alpha',
        'lora_bias',
        'lora_dropout',
        'peft_type',
        'r',
        'target_modules',
        'task_type',
    }
    
    # Remove any other non-essential parameters
    config_cleaned = {}
    for key, value in config.items():
        if key in essential_params:
            config_cleaned[key] = value
        elif value is not None and value != {} and value != []:
            # Keep non-null, non-empty values that might be needed
            config_cleaned[key] = value
    
    print(f"\n   Final parameters: {len(config_cleaned)}")
    
    # Backup original
    backup_path = config_path.with_suffix('.json.backup')
    print(f"\nCreating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    # Save fixed config
    print(f"Saving fixed config...")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_cleaned, f, indent=2, ensure_ascii=False)
    
    print(f"Config fixed!")
    print(f"   Backup saved to: {backup_path}")
    print(f"   Fixed config: {config_path}")
    print()
    print("Next steps:")
    print("   1. Test pipeline: python test_multi_layer_pipeline.py")
    print("   2. If still errors, check peft version: pip install peft>=0.7.0")

if __name__ == "__main__":
    fix_adapter_config()

