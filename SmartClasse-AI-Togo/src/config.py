# src/config.py
# Configuration & Settings pour SmartClasse

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Global settings for SmartClasse"""
    
    # API Settings
    API_TITLE: str = "SmartClasse"
    API_VERSION: str = "0.1.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # LLM Settings
    LLM_MODEL: str = "gemma4:e4b"  # via Ollama
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 2048
    LLM_CONTEXT_WINDOW: int = 8192
    
    # Ollama Settings (if using Ollama instead of direct)
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"
    OLLAMA_TIMEOUT: int = 300
    
    # Audio Settings
    WHISPER_MODEL: str = "base"  # tiny, base, small, medium, large
    WHISPER_DEVICE: str = "cpu"  # cpu or cuda
    SAMPLE_RATE: int = 16000
    
    # Languages
    SUPPORTED_LANGUAGES: list = [
        "kabyie",
        "ewe", 
        "haoussa",
        "mina",
        "tem",
        "french"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./edupath_ai.db"
    DATABASE_ENCRYPT: bool = True
    ENCRYPTION_KEY: Optional[str] = None  # Should be set from env
    
    # Feature Flags
    ENABLE_CULTURIX: bool = True  # Local wisdom integration
    ENABLE_RESEARCHIX: bool = True  # Research data collection
    ENABLE_PASSPORTIX: bool = True  # Competency passport
    ENABLE_EQUITIX: bool = True  # Girl dropout detection
    ENABLE_PARENTIX: bool = False  # SMS (requires SMS gateway)
    
    # Content
    MEPS_CURRICULUM_PATH: Optional[str] = "./data/meps_curriculum.json"
    CULTURAL_CORPUS_PATH: Optional[str] = "./data/cultural_corpus.json"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton instance
settings = Settings()
