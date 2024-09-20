# app/config.py

from pydantic import BaseSettings, Field, AnyHttpUrl
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
        DATABASE_URL (Optional[AnyHttpUrl]): The database URL if needed separately.
        SECRET_KEY (str): The secret key for JWT token generation.
    """
    
    SUPABASE_URL: AnyHttpUrl = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
        env="LOG_FORMAT"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key")
    # Add more configuration variables as needed
    
    class Config:
        """
        Configuration for Pydantic's BaseSettings.
        
        Attributes:
            env_file (str): The path to the .env file.
            env_file_encoding (str): The encoding of the .env file.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"

# Initialize the settings object
settings = Settings()
