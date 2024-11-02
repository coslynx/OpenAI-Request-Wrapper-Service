import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

class Settings:
    """
    Configuration settings for the application.
    """
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://user:password@localhost:5432/openai_wrapper"
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.JWT_SECRET = os.getenv("JWT_SECRET")
        self.REDIS_URL = os.getenv("REDIS_URL") or "redis://localhost:6379"

settings = Settings()