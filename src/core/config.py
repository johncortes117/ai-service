import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", "checkpoints/chat_memory.db")

# DATABASE_URL = os.getenv("DATABASE_URL")
# LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY") # If using LangSmith
