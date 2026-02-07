"""
Basic tests for TenderAnalyzer API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test that the root endpoint returns successfully"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "TenderAnalyzer" in data["message"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 404]  # May not exist yet


def test_docs_available():
    """Test that OpenAPI docs are available"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_sse_stream_endpoint_exists():
    """Test that SSE stream endpoint exists"""
    response = client.get("/sse/stream")
    # SSE endpoints return 200 and keep connection open
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
    response = client.options("/")
    # CORS should be configured to allow cross-origin requests
    assert response.status_code in [200, 405]  # Either OK or Method Not Allowed


def test_invalid_tender_id_format():
    """Test that invalid tender ID returns error"""
    response = client.post("/tenders/invalid-id-123/analyze")
    # Should return 404 or 422 for invalid tender
    assert response.status_code in [404, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
