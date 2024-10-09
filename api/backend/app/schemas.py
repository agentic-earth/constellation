# constellation-backend/api/backend/app/schemas.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from uuid import UUID

# Custom schema for user creation with password validation
class UserCreateInput(BaseModel):
    username: str = Field(..., description="Unique username for the user.")
    email: EmailStr = Field(..., description="Valid email address for the user.")
    password: str = Field(..., description="Password for the user account.")

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Add more checks as needed
        return v