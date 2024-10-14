# backend/app/features/core/services/user_service.py

import uuid
from typing import Optional, Dict, Any
from uuid import UUID
import asyncio
import traceback

from prisma import Prisma
from prisma.models import Profile as PrismaProfile
from backend.app.logger import ConstellationLogger
from backend.app.database import prisma_client, connect_db, get_supabase_client, get_supabase_admin_client
from supabase import Client




class UserService:
    def __init__(self, prisma: Prisma, supabase: Client, supabase_admin: Client):
        self.prisma = prisma
        self.logger = ConstellationLogger()
        self.supabase = supabase  # Regular Supabase client
        self.supabase_admin = supabase_admin  # Admin Supabase client


    # -------------------
    # User Registration
    # -------------------

    async def register_user_email_password(self, email: str, password: str, username: str) -> Dict[str, Any]:
        """
        Registers a new user using email and password via Supabase Auth.
        The corresponding Profile is created automatically via database trigger.
        """
        try:
            # Check if user already exists
            existing_user = await self.get_profile_by_email(email)
            if existing_user:
                self.logger.log("UserService", "warning", "Attempted to register existing email", email=email)
                return {"success": False, "error": "email_exists", "message": "A user with this email already exists."}

            existing_username = await self.get_profile_by_username(username)
            if existing_username:
                self.logger.log("UserService", "warning", "Attempted to register existing username", username=username)
                return {"success": False, "error": "username_exists", "message": "This username is already taken."}

            # Create user in Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"username": username}
                }
            })

            if auth_response.error:
                self.logger.log("UserService", "error", "Supabase Auth sign up failed", error=auth_response.error.message)
                return {"success": False, "error": "auth_error", "message": "Failed to create user account."}

            user = auth_response.user
            if not user:
                self.logger.log("UserService", "error", "No user returned from Supabase Auth sign up")
                return {"success": False, "error": "auth_error", "message": "Failed to create user account."}

            # If email confirmation is required, session will be null
            if not auth_response.session:
                self.logger.log("UserService", "info", "User registered but email confirmation is required", user_id=user.id)
                return {"success": True, "message": "User registered. Please check your email for confirmation."}

            # Retrieve the created Profile via Prisma
            profile = await self.prisma.profile.find_unique(where={"auth_uid": user.id})
            if profile:
                self.logger.log("UserService", "info", "User registered successfully", user_id=profile.auth_uid)
                return {"success": True, "profile": profile.dict(), "message": "User registered successfully."}
            else:
                self.logger.log("UserService", "error", "Profile not found after user registration", user_id=user.id)
                return {"success": False, "error": "profile_not_found", "message": "User account created but profile not found."}

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to register user via email/password", 
                            error=str(e), traceback=traceback.format_exc())
            return {"success": False, "error": "unknown_error", "message": "An unexpected error occurred during registration."}


    # -------------------
    # User Sign-In
    # -------------------

    async def sign_in_user_email_password(self, email: str, password: str) -> Dict[str, Any]:
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if auth_response.user and auth_response.session:
                self.logger.log("UserService", "info", "User signed in successfully", user_id=auth_response.user.id)
                return {
                    "success": True,
                    "user": auth_response.user.model_dump(),
                    "session": auth_response.session.model_dump()
                }
            else:
                self.logger.log("UserService", "error", "Sign in failed: No user or session returned")
                return {"success": False, "error": "auth_error", "message": "Sign in failed"}

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to sign in user via email/password", 
                            error=str(e), traceback=traceback.format_exc())
            return {"success": False, "error": "unknown_error", "message": str(e)}

    # -------------------
    # User Retrieval
    # -------------------

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[PrismaProfile]:
        """
        Retrieves a user's Profile by their userId (auth_uid).
        """
        try:
            profile = await self.prisma.profile.find_unique(where={"auth_uid": str(user_id)})
            if profile:
                self.logger.log("UserService", "info", "Profile retrieved successfully", user_id=profile.auth_uid)
            else:
                self.logger.log("UserService", "warning", "Profile not found for userId", user_id=str(user_id))
            return profile
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to retrieve profile by userId", 
                            error=str(e), traceback=traceback.format_exc())
            return None

    async def get_profile_by_email(self, email: str) -> Optional[PrismaProfile]:
        """
        Retrieves a user's Profile by their email.
        """
        try:
            profile = await self.prisma.profile.find_unique(where={"email": email})
            if profile:
                self.logger.log("UserService", "info", "Profile retrieved successfully by email", email=email)
            else:
                self.logger.log("UserService", "warning", "Profile not found for email", email=email)
            return profile
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to retrieve profile by email", 
                            error=str(e), traceback=traceback.format_exc())
            return None

    async def get_profile_by_username(self, username: str) -> Optional[PrismaProfile]:
        """
        Retrieves a user's Profile by their username.
        """
        try:
            profile = await self.prisma.profile.find_unique(where={"username": username})
            if profile:
                self.logger.log("UserService", "info", "Profile retrieved successfully by username", username=username)
            else:
                self.logger.log("UserService", "warning", "Profile not found for username", username=username)
            return profile
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to retrieve profile by username", 
                            error=str(e), traceback=traceback.format_exc())
            return None

    # -------------------
    # User Update
    # -------------------

    async def update_profile(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaProfile]:
        """
        Updates a user's Profile in the database via Prisma.
        """
        try:
            # Ensure email uniqueness if email is being updated
            if 'email' in update_data:
                existing_profile = await self.prisma.profile.find_unique(where={"email": update_data['email']})
                if existing_profile and existing_profile.auth_uid != str(user_id):
                    self.logger.log("UserService", "error", "Email already in use", email=update_data['email'])
                    raise ValueError("Email is already in use.")

            # Ensure username uniqueness if username is being updated
            if 'username' in update_data:
                existing_profile = await self.prisma.profile.find_unique(where={"username": update_data['username']})
                if existing_profile and existing_profile.auth_uid != str(user_id):
                    self.logger.log("UserService", "error", "Username already in use", username=update_data['username'])
                    raise ValueError("Username is already in use.")

            # Remove fields that shouldn't be manually updated
            update_data.pop('updated_at', None)
            update_data.pop('created_at', None)

            # Update the Profile
            updated_profile = await self.prisma.profile.update(
                where={"auth_uid": str(user_id)},
                data=update_data
            )
            self.logger.log("UserService", "info", "Profile updated successfully", user_id=updated_profile.auth_uid)
            return updated_profile

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to update profile", 
                            error=str(e), traceback=traceback.format_exc())
            return None

    # -------------------
    # User Deletion
    # -------------------

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Deletes a user from Supabase Auth. The corresponding Profile is deleted via trigger.
        """
        try:
            # Delete user from Supabase Auth using admin client
            auth_response = self.supabase_admin.auth.admin.delete_user(str(user_id))

            if auth_response.error:
                self.logger.log("UserService", "error", "Supabase Auth delete failed", error=auth_response.error.message)
                return False

            self.logger.log("UserService", "info", "User deleted successfully from Supabase Auth", user_id=str(user_id))
            return True

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to delete user from Supabase Auth", 
                            error=str(e), traceback=traceback.format_exc())
            return False


    # -------------------
    # Additional Methods (Sign-Up via OAuth, Password Reset, MFA, etc.)
    # -------------------
    # Implement similarly, ensuring alignment with Supabase Auth documentation and Prisma schema.

from backend.app.database import prisma_client, get_supabase_client, get_supabase_admin_client
import asyncio
import traceback


async def main():
    # Initialize Prisma and Supabase clients
    await prisma_client.connect()
    supabase_client = get_supabase_client()
    supabase_admin_client = get_supabase_admin_client()
    # Create UserService instance
    user_service = UserService(prisma_client, supabase_client, supabase_admin_client)

    # Test user registration
    email = "mason_lee@brown.edu"
    password = "securePassword123!"  # In a real scenario, this should be provided by the user
    username = "mason_lee"

    try:
        print("=== Starting User Registration ===")
        registration_result = await user_service.register_user_email_password(email, password, username)
        if registration_result["success"]:
            print(f"User registered successfully: {registration_result['message']}")
            if "profile" in registration_result:
                print(f"Profile: {registration_result['profile']}")
        else:
            print(f"User registration failed: {registration_result['message']}")
    except Exception as e:
        print(f"An error occurred during registration: {str(e)}")

    # Test user sign-in
    try:
        print("=== Starting User Sign-In ===")
        sign_in_result = await user_service.sign_in_user_email_password(email, password)
        if sign_in_result["success"]:
            user = sign_in_result["user"]
            session = sign_in_result["session"]
            print("User signed in successfully.")
            print(f"User ID: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Access Token: {session['access_token']}")
            print(f"Refresh Token: {session['refresh_token']}")
            print(f"Session Expires In: {session['expires_in']}")
            print(f"Session Expires At: {session['expires_at']}")
            print(f"Token Type: {session['token_type']}")
            print("User Metadata:")
            print(f"  App Metadata: {user['app_metadata']}")
            print(f"  User Metadata: {user['user_metadata']}")
            print(f"  Last Sign In: {user['last_sign_in_at']}")
            print(f"  Role: {user['role']}")

            # Store user_id for later use
            user_id = user['id']

            # Test retrieving user profile
            try:
                print("\n=== Retrieving User Profile ===")
                profile = await user_service.get_profile_by_user_id(user_id)
                if profile:
                    print("User profile retrieved successfully:")
                    print(f"User ID: {profile.auth_uid}")
                    print(f"Username: {profile.username}")
                    print(f"Email: {profile.email}")
                else:
                    print("User profile retrieval failed.")
            except Exception as e:
                print(f"An error occurred during profile retrieval: {str(e)}")

            # Test updating user profile
            try:
                print("\n=== Updating User Profile ===")
                new_username = "new_mason_lee"
                update_data = {"username": new_username}
                updated_profile = await user_service.update_profile(user_id, update_data)
                if updated_profile:
                    print("User profile updated successfully:")
                    print(f"New Username: {updated_profile.username}")
                else:
                    print("User profile update failed.")
            except Exception as e:
                print(f"An error occurred during profile update: {str(e)}")

            # Test deleting user
            try:
                print("\n=== Deleting User ===")
                delete_result = await user_service.delete_user(user_id)
                if delete_result:
                    print("User deleted successfully.")
                else:
                    print("User deletion failed.")
            except Exception as e:
                print(f"An error occurred during user deletion: {str(e)}")


        else:
            print(f"User sign-in failed: {sign_in_result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"An error occurred during sign-in: {str(e)}")

    # Clean up
    await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())