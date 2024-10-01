from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID
from app.features.core.controllers.user_controller import UserController
from app.schemas import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from app.utils.auth import get_current_user

router = APIRouter()
user_controller = UserController()

@router.post("/users", response_model=UserResponseSchema, status_code=201)
async def create_user(user_data: UserCreateSchema):
    """
    Create a new user.

    Args:
        user_data (UserCreateSchema): The data required to create a new user.

    Returns:
        UserResponseSchema: The created user data.

    Raises:
        HTTPException: If user creation fails.
    """
    user = user_controller.create_user(user_data)
    if user:
        return user
    raise HTTPException(status_code=400, detail="Failed to create user")

@router.get("/users/{user_id}", response_model=UserResponseSchema)
async def get_user(user_id: UUID):
    """
    Retrieve a user by their ID.

    Args:
        user_id (UUID): The UUID of the user to retrieve.

    Returns:
        UserResponseSchema: The user data.

    Raises:
        HTTPException: If the user is not found.
    """
    user = user_controller.get_user_by_id(user_id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{user_id}", response_model=UserResponseSchema)
async def update_user(user_id: UUID, update_data: UserUpdateSchema):
    """
    Update an existing user's information.

    Args:
        user_id (UUID): The UUID of the user to update.
        update_data (UserUpdateSchema): The data to update for the user.

    Returns:
        UserResponseSchema: The updated user data.

    Raises:
        HTTPException: If the user update fails.
    """
    updated_user = user_controller.update_user(user_id, update_data)
    if updated_user:
        return updated_user
    raise HTTPException(status_code=404, detail="User not found or update failed")

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: UUID):
    """
    Delete a user.

    Args:
        user_id (UUID): The UUID of the user to delete.

    Raises:
        HTTPException: If the user deletion fails.
    """
    success = user_controller.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found or deletion failed")

@router.get("/users", response_model=List[UserResponseSchema])
async def list_users(filters: Optional[dict] = None):
    """
    List users with optional filtering.

    Args:
        filters (Optional[dict]): Key-value pairs to filter the users.

    Returns:
        List[UserResponseSchema]: A list of users.

    Raises:
        HTTPException: If retrieving the user list fails.
    """
    users = user_controller.list_users(filters)
    if users is not None:
        return users
    raise HTTPException(status_code=500, detail="Failed to retrieve users")

@router.post("/users/authenticate", response_model=UserResponseSchema)
async def authenticate_user(email: str, password: str):
    """
    Authenticate a user using their email and password.

    Args:
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        UserResponseSchema: The authenticated user's data.

    Raises:
        HTTPException: If authentication fails.
    """
    user = user_controller.authenticate_user(email, password)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Authentication failed")

# Protected route example
@router.get("/users/me", response_model=UserResponseSchema)
async def get_current_user(current_user: UserResponseSchema = Depends(get_current_user)):
    """
    Get the current authenticated user's information.

    Args:
        current_user (UserResponseSchema): The current authenticated user, obtained from the auth dependency.

    Returns:
        UserResponseSchema: The current user's data.
    """
    return current_user