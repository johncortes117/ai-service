"""
Test configuration and fixtures
"""
import pytest
import os
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Fixture that provides path to test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def sample_tender_pdf(test_data_dir, tmp_path):
    """Fixture that creates a sample PDF file for testing"""
    # Create a minimal valid PDF for testing
    pdf_path = tmp_path / "test_tender.pdf"
    pdf_path.write_bytes(
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f\n"
        b"0000000009 00000 n\n"
        b"0000000056 00000 n\n"
        b"0000000115 00000 n\n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n203\n%%EOF"
    )
    return pdf_path


@pytest.fixture
def mock_openai_key(monkeypatch):
    """Fixture that sets a mock OpenAI API key"""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-mock-key-for-testing")


@pytest.fixture(autouse=True)
def setup_test_env(tmp_path, monkeypatch):
    """Auto-used fixture to setup test environment"""
    # Use temporary directories for uploads during tests
    test_upload_dir = tmp_path / "uploads"
    test_upload_dir.mkdir()
    
    monkeypatch.setenv("UPLOAD_DIR", str(test_upload_dir))
    
    return test_upload_dir
