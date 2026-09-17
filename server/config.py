import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables explicitly from .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv(find_dotenv())

class Settings:
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    
    # Local XAMPP MySQL Database Settings
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_NAME: str = os.getenv("DB_NAME", "support_tickets_db")
    
    # Construct default MySQL URL for XAMPP if DATABASE_URL is not set
    _default_db_url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}" if DB_PASSWORD else f"mysql+pymysql://{DB_USER}:@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DATABASE_URL: str = os.getenv("DATABASE_URL", _default_db_url)
    
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "auto").lower()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")

settings = Settings()

