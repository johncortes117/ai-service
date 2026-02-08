"""
System Health Checks
Replaces the functionality of check_system.py with standard pytest tests.
"""
import os
import sys
import importlib
from pathlib import Path
import pytest
from app.api.main import app

def test_environment_variables():
    """Check that required environment variables are set."""
    openai_key = os.getenv("OPENAI_API_KEY")
    assert openai_key is not None, "OPENAI_API_KEY environment variable is not set."
    assert openai_key.startswith("sk-"), "OPENAI_API_KEY format appears incorrect (should start with 'sk-')."

def test_data_directories_exist(tmp_path):
    """Check that data directories exist or are createable."""
    # We check the actual configured paths from the app, assuming they are relative to project root
    # or absolute. Ideally, we import them from config.
    from app.core import constants
    
    expected_dirs = [
        constants.DATA_DIR,
        constants.TENDERS_DIR,
        constants.PROPOSALS_DIR
    ]
    
    for directory in expected_dirs:
        # Check if directory exists or can be created
        if not directory.exists():
            try:
                directory.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                pytest.fail(f"Could not create directory {directory}: {e}")
        assert directory.exists(), f"Directory {directory} does not exist."
        assert directory.is_dir(), f"Path {directory} is not a directory."

def test_critical_imports():
    """Check that critical libraries and modules can be imported."""
    
    # Check FastAPI app import (already imported at top, but engaging explicit check)
    assert app is not None, "FastAPI app instance is None."
    
    # Check LangGraph
    try:
        from app.agents.tenderAnalyzer.mainGraph import agentGraph
        assert agentGraph is not None
    except ImportError as e:
        pytest.fail(f"Failed to verify LangGraph import: {e}")
    except Exception as e:
        pytest.fail(f"Error importing LangGraph graph: {e}")

    # Check OpenAI
    try:
        import openai
        assert openai is not None
    except ImportError:
        pytest.fail("OpenAI library not installed.")

    # Check LangChain
    try:
        import langchain
        assert langchain is not None
    except ImportError:
        pytest.fail("LangChain library not installed.")

def test_api_endpoints_definition():
    """Verify that expected API endpoints are registered in the FastAPI app."""
    routes = [route.path for route in app.routes]
    
    # Define expected endpoints patterns
    # Note: These are path templates, e.g., /tenders/{tender_id}
    expected_endpoints = [
        "/tenders/upload",
        # Updated to reflect recent changes (removed contractor_id)
        "/proposals/upload/{tender_id}/{company_name}/{ruc}", 
        "/tenders/{tender_id}/analyze",
        "/sse/stream",
        "/get-analysis-report"
    ]
    
    for expected in expected_endpoints:
        # We normalize the path for checking (basic substring match or exact match depending on implementation)
        # FastAPI routes include path parameters in check.
        
        # Exact match check for routes with parameters requires understanding FastAPI router storage
        # Here we do a simple check if the route is present in the list of route paths
        
        # Adjusting expectations for routers mounted with prefixes if any, or flat routes
        found = False
        for route in routes:
            if route == expected:
                found = True
                break
            # Relaxed check for parameterized routes if exact match fails
            if not found and "{" in expected: 
                # Very basic fuzzy match: strict check is better but hard with just strings
                pass 
        
        # A more robust check: verify that at least one route matches the pattern
        # For simplicity in this health check, we just assert the specific known paths exist
        assert expected in routes, f"Endpoint {expected} not found in registered routes: {routes}"
