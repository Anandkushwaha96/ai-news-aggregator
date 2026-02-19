from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI News Aggregator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # News API Configuration
    NEWS_API_KEY: Optional[str] ="75a6d446b07543e38ac17da3636fe7ae"
    NEWS_API_URL: str = "https://newsapi.org/v2"
    
    class Config:
        env_file = ".env"

settings = Settings()