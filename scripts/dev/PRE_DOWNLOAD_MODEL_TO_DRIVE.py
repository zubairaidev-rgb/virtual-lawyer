# ============================================
# PRE-DOWNLOAD MODEL TO DRIVE (Run Once)
# ============================================
# This cell downloads the base model to Google Drive
# Run this ONCE, then use COLAB_Training_v5_FAST.py with USE_DRIVE_MODEL = True
# This avoids slow downloads in future training runs

from google.colab import drive
from huggingface_hub import snapshot_download
import os

# Mount Drive
drive.mount('/content/drive')

BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
DRIVE_MODEL_CACHE = "/content/drive/MyDrive/models/TinyLlama-1.1B-Chat-v1.0"

print("=" * 60)
print("PRE-DOWNLOADING BASE MODEL TO DRIVE")
print("=" * 60)
print(f"Model: {BASE_MODEL}")
print(f"Destination: {DRIVE_MODEL_CACHE}")
print()
print("⚠️  This will take 5-10 minutes")
print("⚠️  You only need to do this ONCE")
print("⚠️  After this, all future training will be much faster!")
print()
print("Starting download...")
print()

if os.path.exists(DRIVE_MODEL_CACHE):
    # Check if it's complete
    model_files = ["model.safetensors", "pytorch_model.bin", "config.json"]
    has_model = any(os.path.exists(os.path.join(DRIVE_MODEL_CACHE, f)) for f in model_files)
    
    if has_model:
        print(f"✅ Model already exists on Drive: {DRIVE_MODEL_CACHE}")
        print("   You can use it in your training script!")
    else:
        print(f"⚠️  Incomplete model found. Re-downloading...")
        import shutil
        shutil.rmtree(DRIVE_MODEL_CACHE, ignore_errors=True)
else:
    os.makedirs(os.path.dirname(DRIVE_MODEL_CACHE), exist_ok=True)

try:
    snapshot_download(
        repo_id=BASE_MODEL,
        local_dir=DRIVE_MODEL_CACHE,
        local_dir_use_symlinks=False,
        resume_download=True  # Resume if interrupted
    )
    print()
    print("=" * 60)
    print("✅ MODEL DOWNLOADED SUCCESSFULLY!")
    print("=" * 60)
    print(f"Location: {DRIVE_MODEL_CACHE}")
    print()
    print("📝 Next steps:")
    print("   1. Use COLAB_Training_v5_FAST.py for training")
    print("   2. The script will automatically detect and use this model")
    print("   3. Future training will be much faster!")
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERROR DOWNLOADING MODEL")
    print("=" * 60)
    print(f"Error: {e}")
    print()
    print("💡 Solutions:")
    print("   1. Check your internet connection")
    print("   2. Restart runtime and try again")
    print("   3. The download may resume automatically if you re-run this cell")























