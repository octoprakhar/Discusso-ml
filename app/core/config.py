from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MODEL_NAME: str = "fake-model"
    APP_ENV: str = "development"
    ML_INTERNAL_SECRET: str
    SUPABASE_URL:str
    SUPABASE_SERVICE_ROLE_KEY:str
    MAX_TAGS: int = 3

    class Config:
        env_file = ".env"

settings = Settings()
