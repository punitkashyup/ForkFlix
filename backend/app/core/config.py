import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    # App configuration
    app_name: str = "Recipe Reel Manager API"
    version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # API configuration
    api_v1_prefix: str = "/api/v1"
    backend_url: str = Field(default="http://localhost:8000", env="BACKEND_URL")
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="CORS_ORIGINS"
    )
    
    # Firebase configuration
    firebase_project_id: str = Field(default="", env="FIREBASE_PROJECT_ID")
    firebase_credentials_path: str = Field(default="../firebase/firebase-admin-key.json", env="FIREBASE_CREDENTIALS_PATH")
    
    # AI API configuration
    huggingface_api_key: str = Field(default="", env="HUGGINGFACE_API_KEY")
    mistral_api_key: str = Field(default="ZUIt0gR9H2LgQg7kXDHzMOcocD1c5z3W", env="MISTRAL_API_KEY")
    
    # Instagram/Facebook configuration
    instagram_access_token: str = Field(default="", env="INSTAGRAM_ACCESS_TOKEN")
    facebook_app_access_token: str = Field(default="", env="FACEBOOK_APP_ACCESS_TOKEN")
    facebook_app_id: str = Field(default="", env="FACEBOOK_APP_ID")
    facebook_app_secret: str = Field(default="", env="FACEBOOK_APP_SECRET")
    
    # Security
    secret_key: str = Field(default="fallback_secret_key_for_development_only", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    ai_rate_limit_per_minute: int = Field(default=10, env="AI_RATE_LIMIT_PER_MINUTE")
    
    # Logging
    log_level: str = Field(default="info", env="LOG_LEVEL")
    
    @field_validator('cors_origins')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()