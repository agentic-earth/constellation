# app/controllers/user_controller.py

"""
User Controller Module

This module defines the UserController class responsible for orchestrating user-related operations.
It handles CRUD operations, authentication, and any advanced user-specific business logic by interacting
with the UserService and AuditService. All actions are logged using the Constellation Logger.

Responsibilities:
- Coordinating between UserService and AuditService to perform user-related operations.
- Managing higher-level business logic that may involve multiple services.
- Ensuring data consistency and handling transactions if necessary.
- Handling exceptions and logging appropriately.

Design Philosophy:
- Maintain high cohesion by focusing solely on user-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.

Usage Example:
    from backend.app.controllers import UserController

    user_controller = UserController()
    new_user = user_controller.create_user(user_data)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from backend.app.features.core.services import UserService, AuditService
from backend.app.schemas import UserCreateSchema, UserUpdateSchema, UserResponseSchema
from backend.app.logger import ConstellationLogger

from prisma import Prisma
from prisma.models import users as PrismaUser


class UserController:
    """
    UserController orchestrates user-related operations by interacting with UserService and AuditService.
    """

    def __init__(self, prisma: Prisma):
        """
        Initializes the UserController with instances of UserService, AuditService, and ConstellationLogger.
        """
        self.prisma = prisma
        self.user_service = UserService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Basic User Operations
    # -------------------

    async def create_user(self, user_data: UserCreateSchema) -> Optional[PrismaUser]:
        """
        Creates a new user.

        Args:
            user_data (UserCreateSchema): The data required to create a new user.

        Returns:
            Optional[UserResponseSchema]: The created user data if successful, None otherwise.
        """
        async with self.prisma.tx() as tx:
            user = await self.user_service.create_user(tx, user_data)
            if user:
                await self.audit_service.create_audit_log(
                    {
                        "user_id": user.user_id,
                        "action_type": "CREATE",
                        "entity_type": "user",
                        "entity_id": user.user_id,
                        "details": f"User '{user.username}' created.",
                    }
                )
                self.logger.log(
                    "UserController",
                    "info",
                    "User created successfully.",
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                )
            else:
                self.logger.log(
                    "UserController",
                    "error",
                    "User creation failed.",
                    user_data=user_data.dict(),
                )
            return user

    async def get_user_by_id(self, user_id: UUID) -> Optional[PrismaUser]:
        """
        Retrieves a user by their unique identifier.

        Args:
            user_id (UUID): The UUID of the user to retrieve.

        Returns:
            Optional[UserResponseSchema]: The user data if found, None otherwise.
        """
        async with self.prisma.tx() as tx:
            user = await self.user_service.get_user_by_id(tx, user_id)
            if user:
                await self.audit_service.create_audit_log(
                    {
                        "user_id": user_id,
                        "action_type": "READ",
                        "entity_type": "user",
                        "entity_id": user_id,
                        "details": f"User '{updated_user.username}' READ.",
                    }
                )
                self.logger.log(
                    "UserController",
                    "info",
                    "User retrieved successfully.",
                    user_id=user.user_id,
                    username=user.username,
                    email=user.email,
                )
            else:
                self.logger.log(
                    "UserController", "warning", "User not found.", user_id=user_id
                )
            return user

    async def update_user(
        self, user_id: UUID, update_data: UserUpdateSchema
    ) -> Optional[PrismaUser]:
        """
        Updates an existing user's information.

        Args:
            user_id (UUID): The UUID of the user to update.
            update_data (UserUpdateSchema): The data to update for the user.

        Returns:
            Optional[UserResponseSchema]: The updated user data if successful, None otherwise.
        """
        async with self.prisma.tx() as tx:
            updated_user = await self.user_service.update_user(tx, user_id, update_data)
            if updated_user:
                await self.audit_service.create_audit_log(
                    {
                        "user_id": user_id,
                        "action_type": "UPDATE",
                        "entity_type": "user",
                        "entity_id": user_id,
                        "details": f"User '{updated_user.username}' updated.",
                    }
                )
                self.logger.log(
                    "UserController",
                    "info",
                    "User updated successfully.",
                    user_id=updated_user.user_id,
                    username=updated_user.username,
                    email=updated_user.email,
                )
            else:
                self.logger.log(
                    "UserController",
                    "error",
                    "User update failed.",
                    user_id=user_id,
                    update_data=update_data.dict(),
                )
            return updated_user

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Deletes a user.

        Args:
            user_id (UUID): The UUID of the user to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        async with self.prisma.tx() as tx:
            success = await self.user_service.delete_user(tx, user_id)
            if success:
                await self.audit_service.create_audit_log(
                    {
                        "user_id": user_id,
                        "action_type": "DELETE",
                        "entity_type": "user",
                        "entity_id": user_id,
                        "details": f"User with ID '{user_id}' deleted.",
                    }
                )
                self.logger.log(
                    "UserController", "info", "User deleted successfully.", user_id=user_id
                )
            else:
                self.logger.log(
                    "UserController",
                    "warning",
                    "User deletion failed or user already deleted.",
                    user_id=user_id,
                )
            return success

    async def list_users(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Optional[List[PrismaUser]]:
        """
        Lists users with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the users.

        Returns:
            Optional[List[UserResponseSchema]]: A list of users if successful, None otherwise.
        """
        async with self.prisma.tx() as tx:
            users = await self.user_service.list_users(tx, filters)
            if users is not None:
                self.logger.log(
                    "UserController",
                    "info",
                    f"{len(users)} users retrieved successfully.",
                    filters=filters,
                )
            else:
                self.logger.log(
                    "UserController", "error", "Failed to retrieve users.", filters=filters
                )
            return users

    # TODO: to be fixed
    def authenticate_user(
        self, email: str, password: str
    ) -> Optional[UserResponseSchema]:
        """
        Authenticates a user using their email and password.

        Args:
            email (str): The user's email.
            password (str): The user's password.

        Returns:
            Optional[UserResponseSchema]: The authenticated user's data if successful, None otherwise.
        """
        user = self.user_service.authenticate_user(email, password)
        if user:
            self.audit_service.create_audit_log(
                {
                    "user_id": user.user_id,
                    "action_type": "READ",
                    "entity_type": "user",
                    "entity_id": user.user_id,
                    "details": f"User '{user.username}' authenticated successfully.",
                }
            )
            self.logger.log(
                "UserController",
                "info",
                "User authenticated successfully.",
                user_id=user.user_id,
                username=user.username,
                email=user.email,
            )
        else:
            self.logger.log(
                "UserController", "warning", "User authentication failed.", email=email
            )
        return user
