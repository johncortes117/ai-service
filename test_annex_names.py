import requests
import json

try:
    # Test the JSON generation endpoint
    response = requests.get("http://127.0.0.1:8000/tenders/1/generate_json")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n=== ESTRUCTURA DE ANEXOS ===")
        
        for i, proposal in enumerate(data["data"]["proposals"]):
            print(f"\nPropuesta {i+1}: {proposal['companyName']}")
            print("Anexos:")
            for annex_key, annex_content in proposal["annexes"].items():
                content_preview = annex_content[:100] + "..." if len(annex_content) > 100 else annex_content
                print(f"  - {annex_key}: {content_preview}")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
