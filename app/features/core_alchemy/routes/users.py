


# app/routes/users.py

"""
User Routes Module

This module defines all API endpoints related to user operations, including creating, retrieving,
updating, deleting users, and authenticating. It leverages the UserController to perform business
logic and interact with the services layer. All operations are logged using the Constellation Logger.

Responsibilities:
- Define HTTP endpoints for user-related operations.
- Validate and parse incoming request data using Pydantic schemas.
- Delegate request handling to the UserController.
- Handle and respond to errors appropriately.

Design Philosophy:
- Maintain thin Routes by delegating complex logic to Controllers.
- Ensure clear separation between HTTP handling and business logic.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from uuid import UUID
# from app.controllers.user_controller import UserController
from app.features.core.controllers.user_controller import UserController
from app.schemas import (
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema,
    TokenSchema
)
from app.auth.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

# Initialize the UserController instance
user_controller = UserController()

# -------------------
# Registration Endpoint
# -------------------

@router.post("/register", response_model=UserResponseSchema, status_code=201)
def register_user(user: UserCreateSchema):
    """
    Register a new user with hashed password.
    """
    user.password_hash = get_password_hash(user.password)
    created_user = user_controller.create_user(user)
    if not created_user:
        raise HTTPException(status_code=400, detail="User registration failed.")
    return created_user

# -------------------
# Login Endpoint
# -------------------

@router.post("/login", response_model=TokenSchema)
def login_for_access_token(form_data: UserCreateSchema):
    """
    Authenticate user and return access token.
    """
    user = authenticate_user(form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
    access_token = create_access_token(data={"sub": str(user.user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

# -------------------
# Protected User Endpoints
# -------------------

@router.get("/me", response_model=UserResponseSchema)
def read_users_me(current_user: UserResponseSchema = Depends(get_current_active_user)):
    """
    Get current logged-in user.
    """
    return current_user

# -------------------
# User Endpoints
# -------------------

@router.post("/", response_model=UserResponseSchema, status_code=201)
def create_user(user: UserCreateSchema, current_user: UserResponseSchema = Depends(get_current_active_user)):
    """
    Create a new user.

    Args:
        user (UserCreateSchema): The data required to create a new user.

    Returns:
        UserResponseSchema: The created user's data.
    """
    created_user = user_controller.create_user(user)
    if not created_user:
        raise HTTPException(status_code=400, detail="User creation failed.")
    return created_user

@router.get("/{user_id}", response_model=UserResponseSchema)
def get_user(user_id: UUID, current_user: UserResponseSchema = Depends(get_current_active_user)):
    """
    Retrieve a user by their UUID.

    Args:
        user_id (UUID): The UUID of the user to retrieve.

    Returns:
        UserResponseSchema: The user's data if found.
    """
    user = user_controller.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

@router.put("/{user_id}", response_model=UserResponseSchema)
def update_user(user_id: UUID, user_update: UserUpdateSchema, current_user: UserResponseSchema = Depends(get_current_active_user)):
    """
    Update an existing user's information.

    Args:
        user_id (UUID): The UUID of the user to update.
        user_update (UserUpdateSchema): The data to update for the user.

    Returns:
        UserResponseSchema: The updated user's data if successful.
    """
    updated_user = user_controller.update_user(user_id, user_update)
    if not updated_user:
        raise HTTPException(status_code=400, detail="User update failed.")
    return updated_user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: UUID, current_user: UserResponseSchema = Depends(get_current_active_user)):
    """
    Delete a user by their UUID.

    Args:
        user_id (UUID): The UUID of the user to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = user_controller.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or already deleted.")
    return

@router.get("/", response_model=List[UserResponseSchema])
def list_users(name: Optional[str] = None, email: Optional[str] = None, role: Optional[str] = None, current_user: UserResponseSchema = Depends(get_current_active_user)):
    """
    List users with optional filtering by name, email, and role.

    Args:
        name (Optional[str]): Filter users by name.
        email (Optional[str]): Filter users by email.
        role (Optional[str]): Filter users by role.

    Returns:
        List[UserResponseSchema]: A list of users matching the filters.
    """
    filters = {}
    if name:
        filters["username"] = name
    if email:
        filters["email"] = email
    if role:
        filters["role"] = role
    users = user_controller.list_users(filters)
    if users is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve users.")
    return users