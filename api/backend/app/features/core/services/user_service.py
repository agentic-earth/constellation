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

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from backend.app.models import User
from backend.app.schemas import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from backend.app.logger import ConstellationLogger
from prisma import Prisma
from prisma.models import users as PrismaUser
from datetime import datetime
import traceback


class UserService:
    """
    UserService class encapsulates all user-related operations.
    """

    def __init__(self):
        """
        Initializes the UserService with the logger.
        """
        self.logger = ConstellationLogger()
        # Removed SupabaseClientManager initialization
        # Prisma transactions are passed externally

    # -------------------
    # User Operations
    # -------------------

    async def create_user(self, tx: Prisma, user_data: Dict[str, Any]) -> Optional[PrismaUser]:
        """
        Creates a new user in the Prisma-managed database.

        Args:
            tx (Prisma): The Prisma transaction object.
            user_data (Dict[str, Any]): The data required to create a new user.

        Returns:
            Optional[PrismaUser]: The created user data if successful, None otherwise.
        """
        try:
            # Prepare user data
            current_time = datetime.utcnow()
            user_dict = {
                "user_id": user_data.get("user_id", str(uuid4())),
                "username": user_data["username"],
                "email": user_data["email"],
                "password_hash": user_data["password_hash"],
                "role": user_data["role"],
                "created_at": current_time,
                "updated_at": current_time,
            }

            # Insert the new user into Prisma
            created_user = await tx.users.create(data=user_dict)

            if not created_user:
                self.logger.log(
                    "UserService",
                    "error",
                    "Failed to create user in Prisma.",
                    extra={"user_data": user_dict}
                )
                return None

            self.logger.log(
                "UserService",
                "info",
                "User created successfully.",
                extra={"user_id": created_user.user_id, "username": created_user.username, "email": created_user.email}
            )
            return created_user

        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user creation: {e}",
                extra={"traceback": traceback.format_exc(), "user_data": user_data}
            )
            return None

    async def get_user_by_id(self, tx: Prisma, user_id: UUID) -> Optional[PrismaUser]:
        """
        Retrieves a user by their unique identifier.

        Args:
            tx (Prisma): The Prisma transaction object.
            user_id (UUID): The UUID of the user to retrieve.

        Returns:
            Optional[PrismaUser]: The user data if found, None otherwise.
        """
        try:
            # Retrieve the user from Prisma
            user = await tx.users.find_unique(where={"user_id": str(user_id)})

            if not user:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found.",
                    extra={"user_id": user_id}
                )
                return None

            self.logger.log(
                "UserService",
                "info",
                "User retrieved successfully.",
                extra={"user_id": user.user_id, "username": user.username, "email": user.email}
            )
            return user

        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user retrieval: {e}",
                extra={"traceback": traceback.format_exc(), "user_id": user_id}
            )
            return None

    async def update_user(self, tx: Prisma, user_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaUser]:
        """
        Updates an existing user's information.

        Args:
            tx (Prisma): The Prisma transaction object.
            user_id (UUID): The UUID of the user to update.
            update_data (Dict[str, Any]): The data to update for the user.

        Returns:
            Optional[PrismaUser]: The updated user data if successful, None otherwise.
        """
        try:
            # Prepare update data
            current_time = datetime.utcnow()
            update_dict = {
                "username": update_data.get("username"),
                "email": update_data.get("email"),
                "password_hash": update_data.get("password_hash"),
                "role": update_data.get("role"),
                "updated_at": current_time,
            }

            # Remove keys with None values to avoid overwriting existing data with null
            update_dict = {k: v for k, v in update_dict.items() if v is not None}

            # Update the user in Prisma
            updated_user = await tx.users.update(
                where={"user_id": str(user_id)},
                data=update_dict
            )

            if not updated_user:
                self.logger.log(
                    "UserService",
                    "error",
                    "Failed to update user in Prisma.",
                    extra={"user_id": user_id, "update_data": update_data}
                )
                return None

            self.logger.log(
                "UserService",
                "info",
                "User updated successfully.",
                extra={"user_id": updated_user.user_id, "updated_fields": list(update_dict.keys())}
            )
            return updated_user

        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user update: {e}",
                extra={"traceback": traceback.format_exc(), "user_id": user_id, "update_data": update_data}
            )
            return None

    async def delete_user(self, tx: Prisma, user_id: UUID) -> bool:
        """
        Deletes a user from the Prisma-managed database.

        Args:
            tx (Prisma): The Prisma transaction object.
            user_id (UUID): The UUID of the user to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Delete the user from Prisma
            deleted_user = await tx.users.delete(where={"user_id": str(user_id)})

            if not deleted_user:
                self.logger.log(
                    "UserService",
                    "error",
                    "Failed to delete user from Prisma.",
                    extra={"user_id": user_id}
                )
                return False

            self.logger.log(
                "UserService",
                "info",
                "User deleted successfully.",
                extra={"user_id": user_id}
            )
            return True

        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user deletion: {e}",
                extra={"traceback": traceback.format_exc(), "user_id": user_id}
            )
            return False

    async def list_users(self, tx: Prisma, filters: Optional[Dict[str, Any]] = None) -> Optional[List[PrismaUser]]:
        """
        Retrieves a list of users with optional filtering.

        Args:
            tx (Prisma): The Prisma transaction object.
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the users.

        Returns:
            Optional[List[PrismaUser]]: A list of users if successful, None otherwise.
        """
        try:
            # Retrieve the list of users from Prisma with optional filtering
            users = await tx.users.find_many(where=filters)

            if not users:
                self.logger.log(
                    "UserService",
                    "warning",
                    "No users found.",
                    extra={"filters": filters}
                )
                return None

            self.logger.log(
                "UserService",
                "info",
                "Users retrieved successfully.",
                extra={"count": len(users)}
            )
            return users

        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during listing users: {e}",
                extra={"traceback": traceback.format_exc(), "filters": filters}
            )
            return None

    ## TODO: to be fixed
    async def authenticate_user(self, tx: Prisma, email: str, password: str) -> Optional[PrismaUser]:
        """
        Authenticates a user using their email and password.

        Args:
            tx (Prisma): The Prisma transaction object.
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            Optional[PrismaUser]: The authenticated user's data if successful, None otherwise.
        """
        try:
            # Retrieve the user by email
            user = await tx.users.find_unique(where={"email": email})

            if not user:
                self.logger.log(
                    "UserService",
                    "warning",
                    "Authentication failed: User not found.",
                    extra={"email": email}
                )
                return None

            # Verify password (assuming password_hash is stored)
            if not verify_password(password, user.password_hash):
                self.logger.log(
                    "UserService",
                    "warning",
                    "Authentication failed: Incorrect password.",
                    extra={"email": email}
                )
                return None

            self.logger.log(
                "UserService",
                "info",
                "User authenticated successfully.",
                extra={"user_id": user.user_id, "email": user.email}
            )
            return user

        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user authentication: {e}",
                extra={"traceback": traceback.format_exc(), "email": email}
            )
            return None

    async def get_user_by_email(self, tx: Prisma, email: str) -> Optional[PrismaUser]:
        """
        Retrieves a user by their email.

        Args:
            tx (Prisma): The Prisma transaction object.
            email (str): The user's email.

        Returns:
            Optional[PrismaUser]: The user data if found, None otherwise.
        """
        try:
            # Retrieve the user by email from Prisma
            user = await tx.users.find_unique(where={"email": email})

            if not user:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found by email.",
                    extra={"email": email}
                )
                return None

            self.logger.log(
                "UserService",
                "info",
                "User retrieved successfully by email.",
                extra={"user_id": user.user_id, "email": user.email}
            )
            return user

        except Exception as e:
            self.logger.log(
                "UserService",
                "critical",
                f"Exception during user retrieval by email: {e}",
                extra={"traceback": traceback.format_exc(), "email": email}
            )
            return None