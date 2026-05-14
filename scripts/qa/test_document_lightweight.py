"""
ULTRA PATIENT Document Test
Gives API MUCH more time to process
"""
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:8000"
TIMEOUT = 300  # 5 minutes for upload
WAIT_TIME = 120  # 2 minutes for API startup

def wait_for_api():
    """Wait patiently for API"""
    print("⏳ Waiting for API (this may take 2-3 minutes)...")
    start = time.time()
    
    while time.time() - start < WAIT_TIME:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("\n✅ API is ready!")
                return True
        except:
            pass
        
        elapsed = int(time.time() - start)
        print(f"  Waiting... {elapsed}s / {WAIT_TIME}s", end="\r")
        time.sleep(5)
    
    print("\n⚠️  API took too long")
    return False

def test_health():
    """Test health"""
    print("\n" + "=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_templates():
    """Test templates endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: Templates")
    print("=" * 60)
    
    try:
        print("📋 Fetching templates...")
        response = requests.get(f"{BASE_URL}/api/document/templates", timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Found {result.get('count', 0)} templates")
            return True
        elif response.status_code == 503:
            print("⚠️  Document features not initialized")
            return False
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_upload():
    """Test upload with VERY long timeout"""
    print("\n" + "=" * 60)
    print("TEST 3: Document Upload (BE PATIENT)")
    print("=" * 60)
    
    # Find smallest test file
    test_file = None
    for path in [
        Path("./test_document.pdf"),
        Path("./data/uploads/test_document.pdf"),
        Path("./test_small.pdf")
    ]:
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb < 5:  # Only use files < 5MB
                test_file = path
                print(f"📤 Found test file: {path.name} ({size_mb:.2f} MB)")
                break
    
    if not test_file:
        print("⚠️  No small test file found")
        print("   Create a simple PDF < 5MB and save as test_small.pdf")
        return None
    
    print(f"📤 Uploading: {test_file.name}")
    print(f"   This may take up to 5 minutes...")
    print(f"   Your system may slow down - this is normal")
    
    try:
        start = time.time()
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            response = requests.post(
                f"{BASE_URL}/api/document/upload",
                files=files,
                timeout=TIMEOUT  # 5 minutes
            )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            doc_id = result.get('doc_id')
            print(f"✅ Upload successful in {elapsed:.1f}s!")
            print(f"   Doc ID: {doc_id}")
            return doc_id
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   {response.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        print(f"⏳ Upload timed out after {TIMEOUT}s")
        print("   Your system may be too slow for document processing")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("=" * 60)
    print("ULTRA PATIENT DOCUMENT TEST")
    print("=" * 60)
    print("\n⚠️  WARNING: This test is VERY patient")
    print("   It will wait up to 5 minutes for operations")
    print("   Your computer may slow down during processing")
    print("\n   Make sure:")
    print("   ✓ Close other heavy applications")
    print("   ✓ Have at least 4GB free RAM")
    print("   ✓ Use a small test PDF (< 5MB)")
    print("\n" + "=" * 60 + "\n")
    
    # Wait for API
    if not wait_for_api():
        print("\n❌ API did not start in time")
        print("   Start API with: python api_complete.py")
        return
    
    # Test health
    if not test_health():
        print("\n❌ API health check failed")
        return
    
    # Test templates
    templates_ok = test_templates()
    
    # Test upload if templates work
    if templates_ok:
        doc_id = test_upload()
        
        if doc_id:
            print("\n" + "=" * 60)
            print("✅ SUCCESS!")
            print("=" * 60)
            print("\nDocument upload works!")
            print(f"Doc ID: {doc_id}")
        else:
            print("\n⚠️  Upload failed")
            print("   Your system may not have enough resources")
    else:
        print("\n⚠️  Document features not ready")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()