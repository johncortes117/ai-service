import requests

def test_pdf_extensions():
    """Test that PDF extensions are properly included in annex names"""
    # Test the JSON generation to see if .pdf extensions are showing
    response = requests.get("http://127.0.0.1:8000/tenders/3/generate_json")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n=== VERIFICAR EXTENSIONES .PDF ===")
        
        for proposal in data["data"]["proposals"]:
            if proposal["companyName"] == "TEST_COMPANY_WITH_PDF_EXTENSION":
                print(f"\nCompany: {proposal['companyName']}")
                print("Anexos encontrados:")
                for key in proposal["annexes"].keys():
                    print(f"  - {key}")
                break
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_pdf_extensions()
