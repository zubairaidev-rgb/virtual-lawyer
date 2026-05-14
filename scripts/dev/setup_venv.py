"""
Quick setup script to install required packages in venv
"""
import subprocess
import sys
import os

def check_and_install():
    """Check if packages are installed and install if missing"""
    
    required_packages = [
        'peft',
        'transformers',
        'torch',
        'sentence-transformers',
        'accelerate',
        'bitsandbytes',
    ]
    
    print("=" * 60)
    print("CHECKING AND INSTALLING REQUIRED PACKAGES")
    print("=" * 60)
    print()
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is MISSING")
            missing.append(package)
    
    if not missing:
        print("\n✅ All packages are installed!")
        return
    
    print(f"\n📦 Installing {len(missing)} missing packages...")
    print()
    
    for package in missing:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package], 
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✓ {package} installed")
        except subprocess.CalledProcessError:
            print(f"  ✗ Failed to install {package}")
            print(f"    Try manually: pip install {package}")
    
    print("\n✅ Setup complete!")
    print("\nNext step: python test_multi_layer_pipeline.py")

if __name__ == "__main__":
    check_and_install()























