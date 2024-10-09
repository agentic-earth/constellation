# constellation-backend/api/backend/app/features/core/services/user_service.py

import uuid
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import asyncio

from prisma.models import Profile as PrismaUser
from backend.app.database import supabase, database
from backend.app.logger import ConstellationLogger

class UserService:
    def __init__(self):
        self.prisma = database.prisma
        self.logger = ConstellationLogger()
        self.supabase = supabase  # Supabase client

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[PrismaUser]:
        """
        Creates a new user using Supabase Auth and stores additional user data in the database.
        """
        try:
            # Extract required fields
            email = user_data.get('email')
            password = user_data.get('password')
            username = user_data.get('username')
            
            if not email or not password or not username:
                raise ValueError("Email, username, and password are required to create a user")
            
            # Create user in Supabase Auth
            # Create user using Supabase Admin API
            auth_response = await self.supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "user_metadata": {"username": username},
                "email_confirm": True  # Automatically confirm email for testing
            })

            if auth_response.get("error"):
                self.logger.log("UserService", "error", "Supabase Auth sign up failed", error=auth_response["error"])
                return None

            user = auth_response.get("user")
            if not user:
                self.logger.log("UserService", "error", "No user returned from Supabase Auth sign up")
                return None

            # Assign auth_uid from Supabase user ID
            auth_uid = user.get("id") or str(uuid.uuid4())
            user_data['auth_uid'] = auth_uid
            user_data['username'] = username
            user_data['email'] = email
            user_data['role'] = user_data.get('role', 'user')  # Default role
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            
            # Remove password from user_data to avoid storing it in Prisma
            user_data.pop('password', None)

            # Store additional user data in the database
            created_user = await self.prisma.profile.create(data=user_data)
            self.logger.log(
                "UserService",
                "info",
                "User created successfully",
                auth_uid=created_user.auth_uid
            )
            return created_user

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to create user", error=str(e))
            # Optional: Rollback Supabase Auth user creation if Prisma fails
            if 'user' in locals() and user:
                await self.supabase.auth.admin.delete_user(user.id)
                self.logger.log("UserService", "info", "Rolled back Supabase Auth user creation")
            return None
        
    async def get_user_by_id(self, auth_uid: UUID) -> Optional[PrismaUser]:
        """
        Retrieves a user by their auth_uid.
        """
        try:
            user = await self.prisma.profile.find_unique(where={"auth_uid": str(auth_uid)})
            if user:
                self.logger.log(
                    "UserService",
                    "info",
                    "User retrieved successfully",
                    auth_uid=user.auth_uid
                )
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found with provided auth_uid",
                    auth_uid=str(auth_uid)
                )
            return user
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to retrieve user by ID", error=str(e))
            return None

    async def get_user_by_email(self, email: str) -> Optional[PrismaUser]:
        """
        Retrieves a user by their email.
        """
        try:
            user = await self.prisma.profile.find_unique(where={"email": email})
            if user:
                self.logger.log(
                    "UserService",
                    "info",
                    "User retrieved successfully",
                    auth_uid=user.auth_uid
                )
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found with provided email",
                    email=email
                )
            return user
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to retrieve user by email", error=str(e))
            return None

    async def get_user_by_username(self, username: str) -> Optional[PrismaUser]:
        """
        Retrieves a user by their username.
        """
        try:
            user = await self.prisma.profile.find_unique(where={"username": username})
            if user:
                self.logger.log(
                    "UserService",
                    "info",
                    "User retrieved successfully",
                    auth_uid=user.auth_uid
                )
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found with provided username",
                    username=username
                )
            return user
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to retrieve user by username", error=str(e))
            return None

    async def update_user(self, auth_uid: UUID, update_data: Dict[str, Any]) -> Optional[PrismaUser]:
        """
        Updates user information in the database.
        """
        try:
            update_data['updated_at'] = datetime.utcnow()
            updated_user = await self.prisma.profile.update(
                where={"auth_uid": str(auth_uid)},
                data=update_data
            )
            self.logger.log(
                "UserService",
                "info",
                "User updated successfully",
                auth_uid=updated_user.auth_uid
            )
            return updated_user
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to update user", error=str(e))
            return None

    async def delete_user(self, auth_uid: UUID) -> bool:
        """
        Deletes a user from Supabase Auth and the database.
        """
        try:
            # Delete user from Supabase Auth
            auth_response = await self.supabase.auth.admin.delete_user(str(auth_uid))
            if auth_response.get("error"):
                self.logger.log("UserService", "error", "Supabase Auth delete failed", error=auth_response["error"])
                return False

            # Delete user data from the database
            await self.prisma.profile.delete(where={"auth_uid": str(auth_uid)})
            self.logger.log(
                "UserService",
                "info",
                "User deleted successfully",
                auth_uid=str(auth_uid)
            )
            return True
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to delete user", error=str(e))
            return False

    async def list_users(self, limit: int = 50, page: int = 1) -> List[PrismaUser]:
        """
        Lists users with pagination.
        """
        try:
            skip = (page - 1) * limit
            users = await self.prisma.profile.find_many(take=limit, skip=skip)
            self.logger.log(
                "UserService",
                "info",
                f"Listed {len(users)} users",
                limit=limit,
                page=page
            )
            return users
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to list users", error=str(e))
            return []
    
    # Additional methods for MFA, password reset, etc., can be added here

    async def get_user_by_username_and_email(self, username: Optional[str] = None, email: Optional[str] = None, auth_uid: Optional[UUID] = None) -> Optional[PrismaUser]:
        """
        Retrieves a user based on provided parameters. This method allows fetching by username, email, or auth_uid.

        Args:
            username (Optional[str]): The username of the user to retrieve.
            email (Optional[str]): The email address of the user to retrieve.
            auth_uid (Optional[UUID]): The auth_uid of the user to retrieve.

        Returns:
            Optional[PrismaUser]: The retrieved user, or None if not found.
        """
        try:
            where_clause = {}
            if auth_uid:
                where_clause["auth_uid"] = str(auth_uid)
            elif email:
                where_clause["email"] = email
            elif username:
                where_clause["username"] = username
            else:
                self.logger.log("UserService", "warning", "No criteria provided for user retrieval")
                return None

            user = await self.prisma.profile.find_unique(where=where_clause)
            if user:
                self.logger.log(
                    "UserService",
                    "info",
                    "User retrieved successfully",
                    auth_uid=user.auth_uid
                )
            else:
                self.logger.log(
                    "UserService",
                    "warning",
                    "User not found with provided criteria",
                    criteria=where_clause
                )
            return user
        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to retrieve user: {str(e)}")
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
            "password": "secure_password",  # Note: Ensure password is handled securely
            "role": "user"
        }
        created_user = await user_service.create_user(new_user_data)
        print(f"Created user: {created_user}")

        if created_user:
            # Get user by ID
            print(f"\nRetrieving user with auth_uid: {created_user.auth_uid}")
            retrieved_user = await user_service.get_user_by_id(UUID(created_user.auth_uid))
            print(f"Retrieved user: {retrieved_user}")

            # Get user by Email
            print(f"\nRetrieving user with email: {created_user.email}")
            user_by_email = await user_service.get_user_by_email(created_user.email)
            print(f"Retrieved user by email: {user_by_email}")

            # Get user by Username
            print(f"\nRetrieving user with username: {created_user.username}")
            user_by_username = await user_service.get_user_by_username(created_user.username)
            print(f"Retrieved user by username: {user_by_username}")

            # Alternatively, use the generalized method
            print("\nRetrieving user using generalized method by username...")
            user_general = await user_service.get_user_by_username_and_email(username=created_user.username)
            print(f"Retrieved user using generalized method: {user_general}")

            # Update user
            print(f"\nUpdating user with auth_uid: {created_user.auth_uid}")
            update_data = {"username": "updated_testuser"}
            updated_user = await user_service.update_user(UUID(created_user.auth_uid), update_data)
            print(f"Updated user: {updated_user}")

            # List users
            print("\nListing all users...")
            all_users = await user_service.list_users()
            print(f"Total users: {len(all_users)}")
            for user in all_users:
                print(f"- Auth UID: {user.auth_uid}, Username: {user.username}, Email: {user.email}")

            # Delete user
            print(f"\nDeleting user with auth_uid: {created_user.auth_uid}")
            deleted = await user_service.delete_user(UUID(created_user.auth_uid))
            print(f"User deleted: {deleted}")

        # List users after operations
        print("\nListing all users after operations...")
        remaining_users = await user_service.list_users()
        print(f"Remaining users: {len(remaining_users)}")
        for user in remaining_users:
            print(f"- Auth UID: {user.auth_uid}, Username: {user.username}, Email: {user.email}")

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
