"""
Install PDF processing dependencies
"""
import subprocess
import sys

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("INSTALLING PDF PROCESSING DEPENDENCIES")
    print("=" * 60)
    print()
    
    # Try pdfplumber first (already in requirements.txt)
    print("Installing pdfplumber...")
    if install_package("pdfplumber"):
        print("\nSUCCESS: pdfplumber installed successfully!")
        print("   You can now run: python process_new_pdfs_to_rag.py")
        return
    
    # Fallback to PyMuPDF
    print("\nInstalling PyMuPDF as fallback...")
    if install_package("PyMuPDF"):
        print("\nSUCCESS: PyMuPDF installed successfully!")
        print("   You can now run: python process_new_pdfs_to_rag.py")
        return
    
    print("\nERROR: Failed to install PDF libraries")
    print("   Please install manually:")
    print("   pip install pdfplumber")
    print("   OR")
    print("   pip install PyMuPDF")

if __name__ == "__main__":
    main()

