"""
SAFE Document Features Test Script
- Non-blocking (no input() calls)
- All requests have timeouts
- Better error handling
- Can run without user interaction
"""
import requests
import json
import sys
import os
from pathlib import Path
import signal
from typing import Optional

BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # 30 second timeout for all requests

# Handle Ctrl+C gracefully
def signal_handler(sig, frame):
    print("\n\n⚠️  Test interrupted by user (Ctrl+C)")
    print("Exiting safely...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def safe_request_get(url: str, timeout: int = TIMEOUT) -> Optional[requests.Response]:
    """Safe GET request with timeout"""
    try:
        response = requests.get(url, timeout=timeout)
        return response
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after {timeout} seconds")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - is the API running on {BASE_URL}?")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def safe_request_post(url: str, json_data: dict = None, files: dict = None, timeout: int = TIMEOUT) -> Optional[requests.Response]:
    """Safe POST request with timeout"""
    try:
        if files:
            response = requests.post(url, files=files, timeout=timeout)
        else:
            response = requests.post(url, json=json_data, timeout=timeout)
        return response
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out after {timeout} seconds")
        return None
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - is the API running on {BASE_URL}?")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_api_connection() -> bool:
    """Check if API is running with timeout"""
    print("🔍 Checking API connection...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=3)
        print("✅ API server is running!")
        return True
    except requests.exceptions.Timeout:
        print("❌ API connection timed out - server may be slow or not responding")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to API server at {BASE_URL}")
        print(f"\n   Please start the API server first:")
        print(f"   python api_complete.py")
        return False
    except Exception as e:
        print(f"❌ Error checking API: {e}")
        return False

def test_document_upload(test_file_path: Path) -> Optional[str]:
    """Test document upload with timeout"""
    print("\n" + "=" * 60)
    print("TEST: Document Upload")
    print("=" * 60)
    
    if not test_file_path.exists():
        print(f"⚠️  Test document not found: {test_file_path}")
        return None
    
    print(f"📤 Uploading: {test_file_path.name}...")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path.name, f, 'application/pdf')}
            response = safe_request_post(f"{BASE_URL}/api/document/upload", files=files, timeout=60)
        
        if response and response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploaded successfully")
            print(f"   Doc ID: {result.get('doc_id', 'N/A')}")
            print(f"   Chunks: {result.get('chunks_count', 'N/A')}")
            return result.get('doc_id')
        else:
            if response:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Error uploading document: {e}")
        return None

def test_document_question(doc_id: str) -> bool:
    """Test asking questions about document"""
    print("\n" + "=" * 60)
    print("TEST: Document Question")
    print("=" * 60)
    
    questions = [
        "What is the FIR number?",
        "What sections are mentioned?",
        "Summarize this document",
    ]
    
    success_count = 0
    for question in questions:
        print(f"\n❓ Asking: {question[:50]}...")
        response = safe_request_post(
            f"{BASE_URL}/api/document/question",
            json_data={"doc_id": doc_id, "question": question},
            timeout=60
        )
        
        if response and response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'N/A')
            print(f"✅ Answer: {answer[:150]}...")
            confidence = result.get('confidence', 0)
            if confidence:
                print(f"   Confidence: {confidence:.2f}")
            success_count += 1
        else:
            if response:
                print(f"❌ Failed: {response.status_code}")
            else:
                print(f"❌ Request failed or timed out")
    
    print(f"\n📊 Questions answered: {success_count}/{len(questions)}")
    return success_count > 0

def test_extract_facts(doc_id: str) -> Optional[dict]:
    """Test fact extraction"""
    print("\n" + "=" * 60)
    print("TEST: Extract Facts")
    print("=" * 60)
    
    print("🔍 Extracting facts...")
    response = safe_request_get(f"{BASE_URL}/api/document/{doc_id}/extract", timeout=30)
    
    if response and response.status_code == 200:
        result = response.json()
        facts = result.get('facts', {})
        print("✅ Facts extracted:")
        
        # Print key facts
        if facts.get('fir_number'):
            print(f"   FIR Number: {facts['fir_number']}")
        if facts.get('sections'):
            print(f"   Sections: {facts['sections']}")
        if facts.get('police_station'):
            print(f"   Police Station: {facts['police_station']}")
        if facts.get('fir_date'):
            print(f"   FIR Date: {facts['fir_date']}")
        
        return facts
    else:
        if response:
            print(f"❌ Failed: {response.status_code}")
        return None

def test_list_templates() -> Optional[list]:
    """Test listing templates"""
    print("\n" + "=" * 60)
    print("TEST: List Templates")
    print("=" * 60)
    
    print("📋 Fetching templates...")
    response = safe_request_get(f"{BASE_URL}/api/document/templates", timeout=10)
    
    if response and response.status_code == 200:
        result = response.json()
        templates = result.get('templates', [])
        count = result.get('count', len(templates))
        print(f"✅ Found {count} templates:")
        
        for i, template in enumerate(templates[:5], 1):  # Show first 5
            template_id = template.get('template_id', 'N/A')
            name = template.get('name', 'N/A')
            placeholders_count = len(template.get('placeholders', []))
            print(f"   {i}. {template_id}")
            print(f"      Name: {name}")
            print(f"      Placeholders: {placeholders_count}")
        
        if count > 5:
            print(f"   ... and {count - 5} more")
        
        return templates
    else:
        if response:
            print(f"❌ Failed: {response.status_code}")
        else:
            print("❌ No response from server")
        return None

def test_generate_document(template_id: str) -> bool:
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
    
    print(f"📝 Generating document from template: {template_id}")
    print("   (This may take 30-60 seconds...)")
    
    response = safe_request_post(
        f"{BASE_URL}/api/document/generate",
        json_data={
            "template_id": template_id,
            "data": data,
            "generate_ai_sections": False  # Disable AI to speed up
        },
        timeout=120  # 2 minutes for generation
    )
    
    if response and response.status_code == 200:
        result = response.json()
        output_path = result.get('output_path', 'N/A')
        print(f"✅ Document generated!")
        print(f"   Output: {output_path}")
        
        filled = result.get('placeholders_filled', 0)
        total = result.get('total_placeholders', 0)
        if total > 0:
            print(f"   Placeholders filled: {filled}/{total}")
        return True
    else:
        if response:
            print(f"❌ Failed: {response.status_code}")
            print(f"   {response.text[:300]}")
        else:
            print("❌ Request timed out or failed")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("DOCUMENT FEATURES TESTING (SAFE MODE)")
    print("=" * 60)
    print("\n⚙️  Safe mode enabled:")
    print("   - No blocking input() calls")
    print("   - All requests have timeouts")
    print("   - Graceful error handling")
    print("   - Press Ctrl+C to stop safely")
    
    # Check API connection
    if not check_api_connection():
        print("\n❌ Cannot proceed without API server")
        print("\nTo start the API server:")
        print("   python api_complete.py")
        sys.exit(1)
    
    # Find test document
    test_file = None
    possible_paths = [
        Path("./test_document.pdf"),
        Path("./data/uploads/test_document.pdf"),
    ]
    
    for path in possible_paths:
        if path.exists():
            test_file = path
            break
    
    if not test_file:
        print("\n⚠️  WARNING: test_document.pdf not found!")
        print("   Searched in:")
        for path in possible_paths:
            print(f"   - {path}")
        print("\n   Continuing with template-only tests...")
        doc_id = None
    else:
        print(f"\n✅ Test document found: {test_file}")
        print("\n" + "=" * 60)
        print("Starting tests in 2 seconds...")
        print("(Press Ctrl+C to cancel)")
        print("=" * 60)
        try:
            import time
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n\n⚠️  Test cancelled by user")
            sys.exit(0)
        
        # Test 1: Upload document
        doc_id = test_document_upload(test_file)
    
    # Test document features if we have doc_id
    if doc_id:
        # Test 2: Ask questions
        test_document_question(doc_id)
        
        # Test 3: Extract facts
        facts = test_extract_facts(doc_id)
    else:
        print("\n⏭️  Skipping document-based tests (no document uploaded)")
    
    # Test 4: List templates
    templates = test_list_templates()
    
    # Test 5: Generate document (if templates exist)
    if templates and len(templates) > 0:
        template_id = templates[0].get('template_id')
        if template_id:
            test_generate_document(template_id)
    else:
        print("\n⚠️  No templates found - skipping generation test")
        print("   Templates are optional - document analysis still works!")
    
    print("\n" + "=" * 60)
    print("✅ TESTING COMPLETE")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - If tests timed out, the API server may be slow")
    print("   - Check API server logs for errors")
    print("   - Document uploads may take time for large files")
    print("   - Template generation can be slow if AI is enabled")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)








