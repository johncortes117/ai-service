import requests
import json

def test_contractors_endpoint():
    """Test the contractors endpoint"""
    
    # Test with tender 1 (should have contractors)
    print("🔄 Testing contractors endpoint for tender 1...")
    
    response = requests.get("http://127.0.0.1:8000/tenders/1/contractors")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Success!")
        print(f"Message: {data['message']}")
        print(f"Tender ID: {data['tender_id']}")
        print(f"Total Contractors: {data['total_contractors']}")
        
        print("\n=== CONTRACTORS LIST ===")
        for contractor in data["contractors"]:
            print(f"\nContractor {contractor['contractorId']}:")
            print(f"  Total Companies: {contractor['totalCompanies']}")
            print("  Companies:")
            for company in contractor["companies"]:
                print(f"    - {company}")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test with non-existent tender
    print("\n🔄 Testing with non-existent tender...")
    response2 = requests.get("http://127.0.0.1:8000/tenders/999/contractors")
    print(f"Status Code: {response2.status_code}")
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"Total Contractors: {data2['total_contractors']}")
        print("(Should be 0 for non-existent tender)")
    else:
        print(f"Response: {response2.text}")

if __name__ == "__main__":
    test_contractors_endpoint()
