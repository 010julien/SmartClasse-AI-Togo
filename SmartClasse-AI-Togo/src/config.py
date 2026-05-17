# src/config.py
# Configuration & Settings pour SmartClasse

from typing import List, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global settings for SmartClasse"""

    # API Settings
    API_TITLE: str = "SmartClasse"
    API_VERSION: str = "0.1.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS — restreindre les origines en production via la variable ALLOWED_ORIGINS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8010",
        "http://127.0.0.1:8010",
        "http://10.0.2.2:8010",
    ]

    # LLM Settings
    LLM_MODEL: str = "gemma4:e4b"  # via Ollama - Gemma 4 (optimized)
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_TOKENS: int = 512  # 512 tokens = réponses pédagogiques complètes (~380 mots)
    LLM_CONTEXT_WINDOW: int = 4096  # Suffisant pour le prompt avancé + historique
    # Quantized LLM fallback
    USE_QUANTIZED_LLM: bool = False
    QUANTIZED_MODEL_PATH: Optional[str] = "models/gemma-4-9b-q4.gguf"

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
        "french",
    ]

    # Database
    DATABASE_URL: str = "sqlite:///./edupath_ai.db"
    DATABASE_ENCRYPT: bool = True
    ENCRYPTION_KEY: Optional[str] = None  # Obligatoire en production

    # Feature Flags
    ENABLE_CULTURIX: bool = True
    ENABLE_RESEARCHIX: bool = True
    ENABLE_PASSPORTIX: bool = True
    ENABLE_EQUITIX: bool = True
    ENABLE_PARENTIX: bool = False  # SMS (requires SMS gateway)

    # SMS / Parent communication
    SMS_PROVIDER: str = "africastalking"
    AFRICASTALKING_USERNAME: Optional[str] = None
    AFRICASTALKING_API_KEY: Optional[str] = None
    AFRICASTALKING_SENDER_ID: Optional[str] = None
    DEFAULT_PARENT_SMS_LANGUAGE: str = "french"

    # Content
    MEPS_CURRICULUM_PATH: Optional[str] = "./data/meps_curriculum.json"
    CULTURAL_CORPUS_PATH: Optional[str] = "./data/cultural_corpus.json"

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.DATABASE_ENCRYPT and not self.ENCRYPTION_KEY:
            if not self.DEBUG:
                raise ValueError(
                    "ENCRYPTION_KEY doit être défini quand DATABASE_ENCRYPT=True en production. "
                    "Définissez DEBUG=True pour contourner cette vérification en développement."
                )
            import logging
            logging.getLogger(__name__).warning(
                "DATABASE_ENCRYPT=True mais ENCRYPTION_KEY n'est pas défini. "
                "La base de données ne sera PAS chiffrée. Définissez ENCRYPTION_KEY dans .env."
            )
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()
