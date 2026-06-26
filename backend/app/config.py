import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


class Settings:
    # JWT Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "my-secret-key")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
    )

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Qdrant
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

    # Gemini API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is missing from .env file"
            )

        if not cls.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL is missing from .env file"
            )


settings = Settings()
settings.validate()

print("Configuration loaded successfully")
print("GEMINI_API_KEY exists:", bool(settings.GEMINI_API_KEY))
print("QDRANT_HOST:", settings.QDRANT_HOST)
print("QDRANT_PORT:", settings.QDRANT_PORT)