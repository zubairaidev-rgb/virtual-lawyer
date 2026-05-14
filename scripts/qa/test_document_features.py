"""
Test Document Analysis and Generation Features
"""
import requests
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_document_upload():
    """Test document upload"""
    print("=" * 60)
    print("TEST: Document Upload")
    print("=" * 60)
    
    # Check if test document exists
    test_file = Path("./test_document.pdf")
    if not test_file.exists():
        print("⚠️  No test document found. Create a test PDF/DOCX first.")
        return None
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            response = requests.post(f"{BASE_URL}/api/document/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploaded successfully")
            print(f"   Doc ID: {result['doc_id']}")
            print(f"   Chunks: {result['chunks_count']}")
            return result['doc_id']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_document_question(doc_id: str):
    """Test asking questions about document"""
    print("\n" + "=" * 60)
    print("TEST: Document Question")
    print("=" * 60)
    
    questions = [
        "What is the FIR number?",
        "What sections are mentioned?",
        "Summarize this document",
    ]
    
    for question in questions:
        try:
            response = requests.post(
                f"{BASE_URL}/api/document/question",
                json={"doc_id": doc_id, "question": question}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Question: {question}")
                print(f"   Answer: {result['answer'][:200]}...")
                print(f"   Confidence: {result['confidence']:.2f}")
            else:
                print(f"❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_extract_facts(doc_id: str):
    """Test fact extraction"""
    print("\n" + "=" * 60)
    print("TEST: Extract Facts")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/document/{doc_id}/extract")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Facts extracted:")
            print(json.dumps(result['facts'], indent=2))
            return result['facts']
        else:
            print(f"❌ Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_list_templates():
    """Test listing templates"""
    print("\n" + "=" * 60)
    print("TEST: List Templates")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/document/templates")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result['count']} templates:")
            for template in result['templates'][:5]:  # Show first 5
                print(f"   - {template['template_id']}: {template['name']}")
                print(f"     Placeholders: {len(template['placeholders'])}")
            return result['templates']
        else:
            print(f"❌ Failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_generate_document(template_id: str):
    """Test document generation"""
    print("\n" + "=" * 60)
    print("TEST: Generate Document")
    print("=" * 60)
    
    data = {
        "accused_name": "John Doe",
        "fir_number": "123/2024",
        "fir_date": "01/01/2024",
        "police_station": "Gulberg Police Station",
        "sections": ["380", "457"],
        "case_brief": "The accused is charged with theft and house trespass.",
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/document/generate",
            json={
                "template_id": template_id,
                "data": data,
                "generate_ai_sections": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document generated:")
            print(f"   Output: {result.get('output_path', 'N/A')}")
            print(f"   Placeholders filled: {result.get('placeholders_filled', 0)}/{result.get('total_placeholders', 0)}")
            return result
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_analyze_and_generate(doc_id: str, template_id: str):
    """Test complete workflow"""
    print("\n" + "=" * 60)
    print("TEST: Analyze and Generate (Complete Workflow)")
    print("=" * 60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/document/analyze-and-generate",
            json={
                "doc_id": doc_id,
                "template_id": template_id,
                "additional_data": {
                    "accused_name": "John Doe"
                }
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Complete workflow successful:")
            print(f"   Extracted facts: {len(result.get('extracted_facts', {}))} fields")
            print(f"   Generated document: {result.get('generation_result', {}).get('output_path', 'N/A')}")
            return result
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_api_connection():
    """Check if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        return True
    except:
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DOCUMENT FEATURES TESTING")
    print("=" * 60)
    
    # Check if API is running
    print("\n🔍 Checking API connection...")
    if not check_api_connection():
        print("❌ ERROR: API server is not running!")
        print(f"\nPlease start the API server first:")
        print(f"  python api_complete.py")
        print(f"\nThe API should be running on: {BASE_URL}")
        sys.exit(1)
    print("✅ API server is running!")
    
    # Check for test document
    test_file = Path("./test_document.pdf")
    if not test_file.exists():
        test_file = Path("./data/uploads/test_document.pdf")
    
    if not test_file.exists():
        print(f"\n⚠️  WARNING: test_document.pdf not found in:")
        print(f"   - ./test_document.pdf")
        print(f"   - ./data/uploads/test_document.pdf")
        print(f"\nYou can still test template generation without a document.")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
        doc_id = None
    else:
        print(f"✅ Test document found: {test_file}")
    
    print("\n" + "=" * 60)
    input("Press Enter to start testing...")
    print()
    
    # Test 1: Upload document
    doc_id = test_document_upload()
    
    if doc_id:
        # Test 2: Ask questions
        test_document_question(doc_id)
        
        # Test 3: Extract facts
        facts = test_extract_facts(doc_id)
        
        # Test 4: List templates
        templates = test_list_templates()
        
        if templates and len(templates) > 0:
            # Test 5: Generate document
            template_id = templates[0]['template_id'] if templates else None
            if template_id:
                test_generate_document(template_id)
                
                # Test 6: Complete workflow (only if we have doc_id)
                if doc_id:
                    test_analyze_and_generate(doc_id, template_id)
        else:
            print("\n⚠️  No templates found. Template generation tests skipped.")
            print("   Templates are optional - document analysis still works!")
    else:
        # Still test templates even without document
        templates = test_list_templates()
        if templates and len(templates) > 0:
            template_id = templates[0]['template_id']
            test_generate_document(template_id)
    
    print("\n" + "=" * 60)
    print("✅ TESTING COMPLETE")
    print("=" * 60)




