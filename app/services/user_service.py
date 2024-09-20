# app/services/user_service.py

"""
User Service Module

This module encapsulates all user-related business logic and interactions with the Supabase backend.
It provides functions to create, retrieve, update, and delete users, ensuring that all operations are
logged appropriately using the Constellation Logger.

Design Philosophy:
- Utilize Supabase's REST API for standard CRUD operations for performance and reliability.
- Use Python only for advanced logic that cannot be handled directly by Supabase.
- Ensure flexibility to adapt to schema changes with minimal modifications.
"""

from typing import Optional, List
from uuid import UUID
from app.models import User, UserCreateSchema, UserUpdateSchema, UserResponseSchema
from app.logger import ConstellationLogger
from app.utils.helpers import SupabaseClientManager
from app.schemas import UserResponseSchema
from datetime import datetime


class UserService:
    """
    UserService class encapsulates all user-related operations.
    """

    def __init__(self):
        """
        Initializes the UserService with the Supabase client and logger.
        """
        self.supabase_manager = SupabaseClientManager()
        self.logger = ConstellationLogger()

    def create_user(self, user_data: UserCreateSchema) -> Optional[UserResponseSchema]:
        """
        Creates a new user in the Supabase database.

        Args:
            user_data (UserCreateSchema): The data required to create a new user.

        Returns:
            Optional[UserResponseSchema]: The created user data if successful, None otherwise.
        """
        try:
            # Convert Pydantic schema to dictionary
            data = user_data.dict()
            # Note: Password hashing should be handled before passing to this method
            response = self.supabase_manager.client.table("users").insert(data).execute()

            if response.status_code in [200, 201] and response.data:
                created_user = UserResponseSchema(**response.data[0])
                self.logger.log(
                    "UserService",
                    "info",
                    "User created successfully",
                    user_id=created_user.user_id,
                    username=created_user.username,
                    email=created_user.email
                )
                return created_user
            else:
                self.logger.log(
                    "UserService",
                    "error",
                    "Failed to create user",
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user creation: {e}"
            )
            return None

    def get_user_by_id(self, user_id: UUID) -> Optional[UserResponseSchema]:
        """
        Retrieves a user by their unique identifier.

        Args:
            user_id (UUID): The UUID of the user to retrieve.

        Returns:
            Optional[UserResponseSchema]: The user data if found, None otherwise.
        """
        try:
            response = self.supabase_manager.client.table("users").select("*").eq("user_id", str(user_id)).single().execute()

            if response.status_code == 200 and response.data:
                user = UserResponseSchema(**response.data)
                self.logger.log(
                    "UserService",
                    "info",
                    "User retrieved successfully",
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email
                )
                return user
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found",
                    user_id=user_id,
                    status_code=response.status_code
                )
                return None
        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user retrieval: {e}"
            )
            return None

    def update_user(self, user_id: UUID, update_data: UserUpdateSchema) -> Optional[UserResponseSchema]:
        """
        Updates an existing user's information.

        Args:
            user_id (UUID): The UUID of the user to update.
            update_data (UserUpdateSchema): The data to update for the user.

        Returns:
            Optional[UserResponseSchema]: The updated user data if successful, None otherwise.
        """
        try:
            data = update_data.dict(exclude_unset=True)
            response = self.supabase_manager.client.table("users").update(data).eq("user_id", str(user_id)).execute()

            if response.status_code == 200 and response.data:
                updated_user = UserResponseSchema(**response.data[0])
                self.logger.log(
                    "UserService",
                    "info",
                    "User updated successfully",
                    user_id=updated_user.user_id,
                    updated_fields=list(data.keys())
                )
                return updated_user
            else:
                self.logger.log(
                    "UserService",
                    "error",
                    "Failed to update user",
                    user_id=user_id,
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user update: {e}"
            )
            return None

    def delete_user(self, user_id: UUID) -> bool:
        """
        Deletes a user from the Supabase database.

        Args:
            user_id (UUID): The UUID of the user to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_manager.client.table("users").delete().eq("user_id", str(user_id)).execute()

            if response.status_code == 200 and response.count > 0:
                self.logger.log(
                    "UserService",
                    "info",
                    "User deleted successfully",
                    user_id=user_id
                )
                return True
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found or already deleted",
                    user_id=user_id,
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user deletion: {e}"
            )
            return False

    def list_users(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[UserResponseSchema]]:
        """
        Retrieves a list of users with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the users.

        Returns:
            Optional[List[UserResponseSchema]]: A list of users if successful, None otherwise.
        """
        try:
            query = self.supabase_manager.client.table("users").select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.status_code == 200 and response.data:
                users = [UserResponseSchema(**user) for user in response.data]
                self.logger.log(
                    "UserService",
                    "info",
                    f"{len(users)} users retrieved successfully",
                    filters=filters
                )
                return users
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "No users found",
                    filters=filters,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during listing users: {e}"
            )
            return None

    def authenticate_user(self, email: str, password: str) -> Optional[UserResponseSchema]:
        """
        Authenticates a user using their email and password.

        Args:
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            Optional[UserResponseSchema]: The authenticated user's data if successful, None otherwise.
        """
        try:
            # Note: Supabase handles authentication via its auth API.
            # This method assumes that password hashing and verification are handled externally.
            # For demonstration, we'll perform a basic check.
            response = self.supabase_manager.client.auth.sign_in(email=email, password=password)

            if response.status_code == 200 and response.user:
                user = self.get_user_by_id(UUID(response.user.id))
                self.logger.log(
                    "UserService",
                    "info",
                    "User authenticated successfully",
                    user_id=user.user_id,
                    email=user.email
                )
                return user
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "Authentication failed",
                    email=email,
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user authentication: {e}"
            )
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user by their email.
        """
        try:
            response = self.supabase_manager.client.table("users").select("*").eq("email", email).single().execute()
            if response.status_code == 200 and response.data:
                user = User(**response.data)
                self.logger.log(
                    "UserService",
                    "info",
                    "User retrieved successfully by email",
                    email=user.email
                )
                return user
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found by email",
                    email=email
                )
                return None
        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user retrieval by email: {e}"
            )
            return None
