import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", "checkpoints/chat_memory.db")

# Next.js Frontend Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS = [
    "http://localhost:3000",    # Next.js development
    "http://127.0.0.1:3000",    # Alternative localhost
    "http://localhost:3001",    # Alternative port
    "https://your-domain.com",  # Production domain (change this)
]

# API Configuration
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", 8000))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# File Upload Configuration
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 50 * 1024 * 1024))  # 50MB default
ALLOWED_FILE_EXTENSIONS = [".pdf", ".docx", ".doc"]
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data")

# Future Security Configuration (not needed yet)
# SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# DATABASE_URL = os.getenv("DATABASE_URL")
# LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY") # If using LangSmith
