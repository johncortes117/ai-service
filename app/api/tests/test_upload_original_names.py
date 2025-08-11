import requests
import io

def test_upload_with_original_names():
    """Test uploading files with original names to see the new behavior"""
    
    # Create some test PDF content (simple text that can be read)
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000125 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n213\n%%EOF"
    
    # Prepare files with custom names
    files = [
        ("principal_file", ("principal_document.pdf", io.BytesIO(pdf_content), "application/pdf")),
        ("attachment_files", ("anexo_1_certificados.pdf", io.BytesIO(pdf_content), "application/pdf")),
        ("attachment_files", ("anexo_2_experiencia.pdf", io.BytesIO(pdf_content), "application/pdf")),
        ("attachment_files", ("anexo_3_calidad.pdf", io.BytesIO(pdf_content), "application/pdf"))
    ]
    
    # Additional form data
    tender_id = "3"  # Use tender 3 to test fresh uploads
    contractor_id = "1"
    company_name = "TEST_COMPANY_WITH_PDF_EXTENSION"
    
    try:
        print("🔄 Uploading files with original names...")
        # Use the correct endpoint with path parameters
        url = f"http://127.0.0.1:8000/proposals/upload_differentiated/{tender_id}/{contractor_id}/{company_name}"
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:  # Accept both 200 and 201
            result = response.json()
            print("✅ Upload successful!")
            print(f"Principal file: {result['principal_file']}")
            print(f"Attachment files: {result['attachment_files']}")
            
            # Now test the JSON generation
            print("\n🔄 Testing JSON generation...")
            json_response = requests.get("http://127.0.0.1:8000/tenders/3/generate_json")
            print(f"JSON Status Code: {json_response.status_code}")
            
            if json_response.status_code == 200:
                json_data = json_response.json()
                print("\n=== ANEXOS CON EXTENSIÓN .PDF ===")
                
                for i, proposal in enumerate(json_data["data"]["proposals"]):
                    if proposal["companyName"] == "TEST_COMPANY_WITH_PDF_EXTENSION":
                        print(f"\nPropuesta de prueba: {proposal['companyName']}")
                        print("Anexos con extensión .pdf:")
                        for annex_key, annex_content in proposal["annexes"].items():
                            print(f"  - {annex_key}")
                        break
            else:
                print(f"Error en JSON: {json_response.text}")
        else:
            print(f"Error en upload: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_upload_with_original_names()
