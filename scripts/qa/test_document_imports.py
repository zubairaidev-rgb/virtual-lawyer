"""
Test if document modules can be imported
"""
import sys
from pathlib import Path

_scripts_dir = Path(__file__).resolve().parents[1]
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))
from _repo import bootstrap_path  # noqa: E402

bootstrap_path()

print("Testing document feature imports...")
print("=" * 60)

# Test docxtpl
try:
    from docxtpl import DocxTemplate
    print("✅ docxtpl imported successfully")
except ImportError as e:
    print(f"❌ docxtpl import failed: {e}")

# Test python-docx
try:
    from docx import Document
    print("✅ python-docx imported successfully")
except ImportError as e:
    print(f"❌ python-docx import failed: {e}")

# Test document_analyzer
try:
    from document_analyzer import DocumentAnalyzer
    print("✅ DocumentAnalyzer imported successfully")
except ImportError as e:
    print(f"❌ DocumentAnalyzer import failed: {e}")

# Test document_generator
try:
    from document_generator import DocumentGenerator
    print("✅ DocumentGenerator imported successfully")
except ImportError as e:
    print(f"❌ DocumentGenerator import failed: {e}")

print("=" * 60)
print("Import test complete!")





















