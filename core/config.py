import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Resolve Absolute Path for DB to avoid Vercel CWD issues
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # core/
    ROOT_DIR = os.path.dirname(BASE_DIR) # roo/
    DB_PATH = os.path.join(ROOT_DIR, "pharma_agent.db")
    
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DB_PATH}")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
    
    # OpenRouter / OpenAI Config
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-3.5-turbo") # Default or user choice

settings = Settings()
