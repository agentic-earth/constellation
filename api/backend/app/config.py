# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AnyHttpUrl, PostgresDsn
from typing import Optional
import os
from pathlib import Path
import dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
dotenv.load_dotenv(ROOT_DIR / ".env", override=True)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        SUPABASE_URL (AnyHttpUrl): The URL of the Supabase project.
        SUPABASE_KEY (str): The Supabase service role key.
        LOG_LEVEL (str): The logging level (e.g., INFO, DEBUG).
        LOG_FORMAT (str): The format string for log messages.
        SECRET_KEY (str): The secret key for JWT token generation.
        OPENAI_API_KEY (str): The OpenAI API key.
        OPENAI_API_KEY (str): The OpenAI API key.
    """

    SUPABASE_URL: AnyHttpUrl = Field(default=os.getenv("SUPABASE_URL"))
    SUPABASE_KEY: str = Field(default=os.getenv("SUPABASE_KEY"))
    SUPABASE_SERVICE_KEY: Optional[str] = Field(
        default=os.getenv("SUPABASE_SERVICE_KEY")
    )
    LOG_LEVEL: str = Field(
        default=os.getenv("LOG_LEVEL") if os.getenv("LOG_LEVEL") else "INFO"
    )
    LOG_FORMAT: str = Field(
        default=(
            os.getenv("LOG_FORMAT")
            if os.getenv("LOG_FORMAT")
            else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    SECRET_KEY: str = Field(
        default=(
            os.getenv("SECRET_KEY") if os.getenv("SECRET_KEY") else "default-secret-key"
        )
    )
    OPENAI_API_KEY: str = Field(default=os.getenv("OPENAI_API_KEY"))
    DATABASE_URL: PostgresDsn = Field(
        default=(os.getenv("DATABASE_URL") if os.getenv("DATABASE_URL") else "")
    )

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # This will ignore any extra fields in the environment
    )


# Initialize the settings object
settings = Settings()
