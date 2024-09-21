# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl
from typing import Optional
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        SUPABASE_URL (AnyHttpUrl): The URL of the Supabase project.
        SUPABASE_KEY (str): The Supabase service role key.
        LOG_LEVEL (str): The logging level (e.g., INFO, DEBUG).
        LOG_FORMAT (str): The format string for log messages.
        SECRET_KEY (str): The secret key for JWT token generation.
    """
    
    SUPABASE_URL: AnyHttpUrl = Field(..., validation_alias="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., validation_alias="SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(None, validation_alias="SUPABASE_SERVICE_KEY")
    LOG_LEVEL: str = Field("INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        validation_alias="LOG_FORMAT"
    )
    SECRET_KEY: str = Field(default="default-secret-key", validation_alias="SECRET_KEY")
    # Add more configuration variables as needed
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra='ignore'  # This will ignore any extra fields in the environment
    )

# Initialize the settings object
settings = Settings()

#print("Loaded settings:", settings.dict())
