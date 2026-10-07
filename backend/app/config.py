from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "RepoGuard AI"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # LLM
    LLM_PROVIDER: str = "ollama"  # ollama or openai
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:0.5b"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: Optional[str] = None
    
    # Paths
    WORKSPACE_DIR: Path = Path("workspace")
    DB_PATH: Path = Path("data/repoguard.db")
    
    # Execution
    COMMAND_TIMEOUT: int = 120
    MAX_REPAIR_ATTEMPTS: int = 5
    MAX_FILE_SIZE_KB: int = 500
    
    # Embedding
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
