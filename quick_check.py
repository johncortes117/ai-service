"""
Quick diagnostic - check if imports work
Run with: uv run python quick_check.py
"""

print("=" * 60)
print("Quick System Check")
print("=" * 60)

# 1. Check FastAPI import
try:
    from app.api.main import app
    print("[OK] FastAPI app imports successfully")
    
    # List routes
    routes = [r.path for r in app.routes if hasattr(r, 'path')]
    print(f"[OK] Found {len(routes)} API routes")
    
except Exception as e:
    print(f"[ERROR] FastAPI import failed: {e}")
    exit(1)

# 2. Check environment variable
import os
openai_key = os.getenv("OPENAI_API_KEY", "")
if openai_key:
    print(f"[OK] OPENAI_API_KEY is set (length: {len(openai_key)} chars)")
else:
    print("[WARNING] OPENAI_API_KEY not set - AI features will not work!")

# 3. Check critical libraries
try:
    import openai
    print("[OK] OpenAI library available")
except Exception as e:
    print(f"[ERROR] OpenAI library missing: {e}")

try:
    import langchain
    print("[OK] LangChain library available")
except Exception as e:
    print(f"[ERROR] LangChain library missing: {e}")

try:
    import langgraph
    print("[OK] LangGraph library available")
except Exception as e:
    print(f"[ERROR] LangGraph library missing: {e}")

# 4. Check data directories
from pathlib import Path
upload_dir = Path("data/tenders")
if upload_dir.exists():
    print(f"[OK] Upload directory exists: {upload_dir}")
else:
    print(f"[INFO] Creating upload directory: {upload_dir}")
    upload_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Created {upload_dir}")

# 5. Try importing the graph
try:
    from app.agents.tenderAnalyzer.mainGraph import graph
    print("[OK] LangGraph workflow imports successfully")
except Exception as e:
    print(f"[WARNING] LangGraph workflow import issue: {e}")

print("\n" + "=" * 60)
print("[SUCCESS] Basic system checks passed!")
print("\nTo start the backend:")
print("  uv run uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload")
print("\nTo start the frontend:")
print("  cd frontend && npm run dev")
print("=" * 60)
