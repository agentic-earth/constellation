"""
User Service Module

This module implements the User Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The UserService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (PrismaUser) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. No Request/Response Models: We directly use dictionaries for input and Prisma models for output.
   This simplifies the API and reduces redundancy, as Prisma models already provide necessary structure.

4. Error Handling: Exceptions are allowed to propagate, to be handled by the caller.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for user operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from prisma.models import users as PrismaUser
from backend.app.database import database
from backend.app.logger import ConstellationLogger

class UserService:
    def __init__(self):
        self.prisma = database.prisma
        self.logger = ConstellationLogger()

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[PrismaUser]:
        """
        Creates a new user in the database.

        Args:
            user_data (Dict[str, Any]): Dictionary containing user data.

        Returns:
            Optional[PrismaUser]: The created user, or None if creation failed.
        """
        try:
            user_data['user_id'] = str(uuid4())
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            created_user = await self.prisma.users.create(data=user_data)
            self.logger.log("UserService", "info", "User created successfully", user_id=created_user.user_id)
            return created_user
        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to create user: {str(e)}")
            return None

    async def get_user_by_id(self, user_id: UUID) -> Optional[PrismaUser]:
        """
        Retrieves a user by their ID.

        Args:
            user_id (UUID): The ID of the user to retrieve.

        Returns:
            Optional[PrismaUser]: The retrieved user, or None if not found.
        """
        try:
            user = await self.prisma.users.find_unique(where={"user_id": str(user_id)})
            if user:
                self.logger.log("UserService", "info", "User retrieved successfully", user_id=user.user_id)
            else:
                self.logger.log("UserService", "warning", "User not found", user_id=str(user_id))
            return user
        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to retrieve user: {str(e)}")
            return None

    async def update_user(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaUser]:
        """
        Updates an existing user's information.

        Args:
            user_id (UUID): The ID of the user to update.
            update_data (Dict[str, Any]): Dictionary containing updated user data.

        Returns:
            Optional[PrismaUser]: The updated user, or None if update failed.
        """
        try:
            update_data['updated_at'] = datetime.utcnow()
            updated_user = await self.prisma.users.update(
                where={"user_id": str(user_id)},
                data=update_data
            )
            self.logger.log("UserService", "info", "User updated successfully", user_id=updated_user.user_id)
            return updated_user
        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to update user: {str(e)}")
            return None

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Deletes a user from the database.

        Args:
            user_id (UUID): The ID of the user to delete.

        Returns:
            bool: True if the user was successfully deleted, False otherwise.
        """
        try:
            deleted_user = await self.prisma.users.delete(where={"user_id": str(user_id)})
            if deleted_user:
                self.logger.log("UserService", "info", "User deleted successfully", user_id=str(user_id))
                return True
            else:
                self.logger.log("UserService", "warning", "User not found for deletion", user_id=str(user_id))
                return False
        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to delete user: {str(e)}")
            return False

    async def list_users(self, filters: Optional[Dict[str, Any]] = None) -> List[PrismaUser]:
        """
        Retrieves a list of users, optionally filtered.

        Args:
            filters (Optional[Dict[str, Any]]): Optional filters to apply to the query.

        Returns:
            List[PrismaUser]: A list of users matching the filters.
        """
        try:
            users = await self.prisma.users.find_many(where=filters or {})
            self.logger.log("UserService", "info", f"Retrieved {len(users)} users")
            return users
        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to list users: {str(e)}")
            return []

    async def get_user_by_email(self, email: str) -> Optional[PrismaUser]:
        """
        Retrieves a user by their email address.

        Args:
            email (str): The email address of the user to retrieve.

        Returns:
            Optional[PrismaUser]: The retrieved user, or None if not found.
        """
        try:
            user = await self.prisma.users.find_unique(where={"email": email})
            if user:
                self.logger.log("UserService", "info", "User retrieved successfully by email", email=email)
            else:
                self.logger.log("UserService", "warning", "User not found by email", email=email)
            return user
        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to retrieve user by email: {str(e)}")
            return None

async def main():
    """
    Main function to demonstrate and test the UserService functionality.
    """
    print("Starting UserService test...")

    print("Connecting to the database...")
    await database.connect()
    print("Database connected successfully.")

    user_service = UserService()

    try:
        # Create a new user
        print("\nCreating a new user...")
        new_user_data = {
            "username": "testuser1",
            "email": "testuser1@example.com",
            "password_hash": "hashed_password",
            "role": "user"
        }
        created_user = await user_service.create_user(new_user_data)
        print(f"Created user: {created_user}")

        if created_user:
            # Get user by ID
            print(f"\nRetrieving user with ID: {created_user.user_id}")
            retrieved_user = await user_service.get_user_by_id(UUID(created_user.user_id))
            print(f"Retrieved user: {retrieved_user}")

            # Update user
            print(f"\nUpdating user with ID: {created_user.user_id}")
            update_data = {"username": "updated_testuser"}
            updated_user = await user_service.update_user(UUID(created_user.user_id), update_data)
            print(f"Updated user: {updated_user}")

            # Get user by email
            print(f"\nRetrieving user with email: {created_user.email}")
            user_by_email = await user_service.get_user_by_email(created_user.email)
            print(f"Retrieved user by email: {user_by_email}")

            # List users
            print("\nListing all users...")
            all_users = await user_service.list_users()
            print(f"Total users: {len(all_users)}")
            for user in all_users:
                print(f"- User ID: {user.user_id}, Username: {user.username}, Email: {user.email}")

            # Delete user
            print(f"\nDeleting user with ID: {created_user.user_id}")
            deleted = await user_service.delete_user(UUID(created_user.user_id))
            print(f"User deleted: {deleted}")

        # List users after operations
        print("\nListing all users after operations...")
        remaining_users = await user_service.list_users()
        print(f"Remaining users: {len(remaining_users)}")
        for user in remaining_users:
            print(f"- User ID: {user.user_id}, Username: {user.username}, Email: {user.email}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())

    finally:
        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

if __name__ == "__main__":
    asyncio.run(main())