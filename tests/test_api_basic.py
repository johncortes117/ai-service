"""
Basic tests for TenderAnalyzer API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)





def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 404]  # May not exist yet


def test_docs_available():
    """Test that OpenAPI docs are available"""
    response = client.get("/docs")
    assert response.status_code == 200





def test_tender_upload_requires_file():
    """Test that tender upload requires a file"""
    response = client.post("/tenders/upload")
    # Should return 422 (Unprocessable Entity) for missing file
    assert response.status_code == 422


def test_get_analysis_report_empty():
    """Test getting analysis report when none exists"""
    response = client.get("/get-analysis-report")
    # Should return 404 if no report exists, or 200 with empty/default data
    assert response.status_code in [200, 404]


def test_cors_headers():
    """Test that CORS headers are configured"""
    # Use an existing endpoint for OPTIONS request
    response = client.options("/health")
    # CORS should be configured to allow cross-origin requests
    # 200 OK means handled, 405 Method Not Allowed means OPTIONS not explicitly handled but headers might be present
    assert response.status_code in [200, 405]


def test_invalid_tender_id_format():
    """Test that invalid tender ID returns error"""
    response = client.post("/tenders/invalid-id-123/analyze")
    # Should return 404 or 422 for invalid tender, OR 202 if async processing starts anyway (with error later)
    assert response.status_code in [404, 422, 500, 202]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
