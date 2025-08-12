"""
AI Service API Test Suite
Run all tests for the API endpoints and functionality
"""
import sys
import os

# Add the parent directory to the path to import test modules
sys.path.append(os.path.dirname(__file__))

from test_contractors import test_contractors_endpoint
from test_annex_names import test_annex_names
from test_upload_original_names import test_upload_with_original_names
from test_pdf_extensions import test_pdf_extensions

def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 60)
    print("🚀 AI SERVICE API TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Contractors API", test_contractors_endpoint),
        ("Annex Names Structure", test_annex_names),
        ("Upload with Original Names", test_upload_with_original_names),
        ("PDF Extensions Verification", test_pdf_extensions)
    ]
    
    for test_name, test_function in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_function()
            print(f"✅ {test_name} - PASSED")
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
        print("-" * 60)
    
    print("\n🏁 ALL TESTS COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()
