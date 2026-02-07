'''
Quick diagnostic script to check if everything is configured correctly
'''

import sys
import os
from pathlib import Path


def check_environment():
    """Check environment variables and configuration"""
    print("🔍 Checking Environment Configuration...\n")
    
    issues = []
    
    # Check OpenAI API Key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        issues.append("❌ OPENAI_API_KEY not set in environment")
    elif openai_key.startswith("sk-"):
        print("✅ OPENAI_API_KEY is set")
    else:
        issues.append("⚠️  OPENAI_API_KEY format looks incorrect")
    
    # Check required directories
    upload_dir = Path("data/tenders")
    if not upload_dir.exists():
        print(f"⚠️  Upload directory doesn't exist, will be created: {upload_dir}")
        upload_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {upload_dir}")
    else:
        print(f"✅ Upload directory exists: {upload_dir}")
    
    return issues


def check_imports():
    """Check that all critical imports work"""
    print("\n🔍 Checking Python Imports...\n")
    
    issues = []
    
    try:
        from app.api.main import app
        print("✅ FastAPI app imports successfully")
    except Exception as e:
        issues.append(f"❌ Failed to import FastAPI app: {e}")
    
    try:
        from app.agents.tenderAnalyzer.mainGraph import graph
        print("✅ LangGraph imports successfully")
    except Exception as e:
        issues.append(f"❌ Failed to import LangGraph: {e}")
    
    try:
        import openai
        print("✅ OpenAI library available")
    except Exception as e:
        issues.append(f"❌ OpenAI library not available: {e}")
    
    try:
        import langchain
        print("✅ LangChain library available")
    except Exception as e:
        issues.append(f"❌ LangChain library not available: {e}")
    
    return issues


def check_api_endpoints():
    """Check that API endpoints are defined"""
    print("\n🔍 Checking API Endpoints...\n")
    
    try:
        from app.api.main import app
        routes = [route.path for route in app.routes]
        
        expected_endpoints = [
            "/tenders/upload",
            "/proposals/upload/{tender_id}/{contractor_id}/{company_name}",
            "/tenders/{tender_id}/analyze",
            "/sse/stream",
            "/get-analysis-report"
        ]
        
        for endpoint in expected_endpoints:
            # Simple check if endpoint pattern exists
            if any(endpoint.replace("{", "").replace("}", "") in route.replace("{", "").replace("}", "") for route in routes):
                print(f"✅ Endpoint exists: {endpoint}")
            else:
                print(f"⚠️  Endpoint may be missing: {endpoint}")
        
        return []
    except Exception as e:
        return [f"❌ Failed to check endpoints: {e}"]


def main():
    """Run all diagnostic checks"""
    print("=" * 60)
    print("TenderAnalyzer Diagnostic Check")
    print("=" * 60 + "\n")
    
    all_issues = []
    
    # Run checks
    all_issues.extend(check_environment())
    all_issues.extend(check_imports())
    all_issues.extend(check_api_endpoints())
    
    # Summary
    print("\n" + "=" * 60)
    if all_issues:
        print("⚠️  ISSUES FOUND:\n")
        for issue in all_issues:
            print(f"  {issue}")
        print("\n❌ Please fix the issues above before running the demo")
        sys.exit(1)
    else:
        print("✅ All checks passed! System is ready.")
        print("\n📝 Next steps:")
        print("  1. Start backend: uv run uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000")
        print("  2. Start frontend: cd frontend && npm run dev")
        print("  3. Open browser: http://localhost:3000")
    print("=" * 60)


if __name__ == "__main__":
    main()
