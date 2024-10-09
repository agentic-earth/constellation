# constellation-backend/api/backend/app/features/core/services/user_service.py

import uuid
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import asyncio

from prisma import Prisma
from prisma.models import Profile as PrismaProfile
from backend.app.logger import ConstellationLogger
from backend.app.database import connect_supabase
class UserService:
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        self.logger = ConstellationLogger()
        self.supabase = connect_supabase()  # Supabase client

    # -------------------
    # User Registration
    # -------------------

    async def register_user_email_password(self, email: str, password: str, username: str) -> Optional[PrismaProfile]:
        """
        Registers a new user using email and password via Supabase Auth.
        The corresponding Profile is created automatically via database trigger.
        """
        try:
            # Create user in Supabase Auth
            auth_response = await self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"username": username}
                }
            })

            if auth_response.error:
                self.logger.log("UserService", "error", "Supabase Auth sign up failed", error=auth_response.error.message)
                return None

            user = auth_response.user
            if not user:
                self.logger.log("UserService", "error", "No user returned from Supabase Auth sign up")
                return None

            # Wait briefly to allow trigger to create the Profile
            await asyncio.sleep(1)  # Adjust as necessary

            # Retrieve the created Profile via Prisma
            profile = await self.prisma.profile.find_unique(where={"userId": user.id})
            if profile:
                self.logger.log("UserService", "info", "User registered successfully", user_id=profile.userId)
                return profile
            else:
                self.logger.log("UserService", "error", "Profile not found after user registration", user_id=user.id)
                return None

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to register user via email/password", error=str(e))
            return None

    async def register_user_oauth(self, provider: str) -> Dict[str, Any]:
        """
        Initiates OAuth sign-up/sign-in process using a third-party provider via Supabase Auth.
        """
        try:
            # Initiate OAuth sign-in
            response = await self.supabase.auth.sign_in_with_oauth({
                "provider": provider
            })

            if response.error:
                self.logger.log("UserService", "error", f"Supabase Auth OAuth sign in failed for provider {provider}", error=response.error.message)
                return {"success": False, "error": response.error.message}

            # Redirect user to OAuth provider's sign-in page
            # The actual redirect should be handled in the frontend
            self.logger.log("UserService", "info", f"Initiated OAuth sign in for provider {provider}")
            return {"success": True, "url": response.url}

        except Exception as e:
            self.logger.log("UserService", "error", f"Failed to initiate OAuth sign in for provider {provider}", error=str(e))
            return {"success": False, "error": str(e)}

    # -------------------
    # User Sign-In
    # -------------------

    async def sign_in_user_email_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Signs in a user using email and password via Supabase Auth.
        Returns session data if successful.
        """
        try:
            auth_response = await self.supabase.auth.sign_in({
                "email": email,
                "password": password
            })

            if auth_response.error:
                self.logger.log("UserService", "error", "Supabase Auth sign in failed", error=auth_response.error.message)
                return None

            session = auth_response.session
            if session:
                self.logger.log("UserService", "info", "User signed in successfully", user_id=session.user.id)
                return {"success": True, "session": session}
            else:
                self.logger.log("UserService", "error", "No session returned after sign in")
                return None

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to sign in user via email/password", error=str(e))
            return None

    # -------------------
    # User Retrieval
    # -------------------

    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[PrismaProfile]:
        """
        Retrieves a user's Profile by their userId (auth_uid).
        """
        try:
            profile = await self.prisma.profile.find_unique(where={"userId": str(user_id)})
            if profile:
                self.logger.log("UserService", "info", "Profile retrieved successfully", user_id=profile.userId)
            else:
                self.logger.log("UserService", "warning", "Profile not found for userId", user_id=str(user_id))
            return profile
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to retrieve profile by userId", error=str(e))
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
            self.logger.log("UserService", "error", "Failed to retrieve profile by email", error=str(e))
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
            self.logger.log("UserService", "error", "Failed to retrieve profile by username", error=str(e))
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
                if existing_profile and existing_profile.userId != str(user_id):
                    self.logger.log("UserService", "error", "Email already in use", email=update_data['email'])
                    raise ValueError("Email is already in use.")

            # Update the Profile
            update_data['updated_at'] = datetime.utcnow()
            updated_profile = await self.prisma.profile.update(
                where={"userId": str(user_id)},
                data=update_data
            )
            self.logger.log("UserService", "info", "Profile updated successfully", user_id=updated_profile.userId)
            return updated_profile

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to update profile", error=str(e))
            return None

    async def update_auth_user_email(self, user_id: UUID, new_email: str) -> Optional[Dict[str, Any]]:
        """
        Updates a user's email in Supabase Auth.
        """
        try:
            auth_response = await self.supabase.auth.update_user({
                "id": str(user_id),
                "email": new_email
            })

            if auth_response.error:
                self.logger.log("UserService", "error", "Supabase Auth email update failed", error=auth_response.error.message)
                return {"success": False, "error": auth_response.error.message}

            self.logger.log("UserService", "info", "Supabase Auth email updated successfully", user_id=str(user_id))
            return {"success": True}

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to update user email in Supabase Auth", error=str(e))
            return {"success": False, "error": str(e)}

    # -------------------
    # User Deletion
    # -------------------

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Deletes a user from Supabase Auth. The corresponding Profile is deleted via trigger.
        """
        try:
            # Delete user from Supabase Auth
            auth_response = await self.supabase.auth.admin.delete_user(str(user_id))
            if auth_response.error:
                self.logger.log("UserService", "error", "Supabase Auth delete failed", error=auth_response.error.message)
                return False

            self.logger.log("UserService", "info", "User deleted successfully from Supabase Auth", user_id=str(user_id))
            return True

        except Exception as e:
            self.logger.log("UserService", "error", "Failed to delete user from Supabase Auth", error=str(e))
            return False

    # -------------------
    # Password Reset
    # -------------------

    async def send_password_reset_email(self, email: str, redirect_to: str) -> bool:
        """
        Sends a password reset email via Supabase Auth.
        """
        try:
            reset_response = await self.supabase.auth.reset_password_for_email(email, {
                "redirect_to": redirect_to
            })

            if reset_response.error:
                self.logger.log("UserService", "error", "Failed to send password reset email", error=reset_response.error.message)
                return False

            self.logger.log("UserService", "info", "Password reset email sent successfully", email=email)
            return True

        except Exception as e:
            self.logger.log("UserService", "error", "Exception occurred while sending password reset email", error=str(e))
            return False

    async def update_user_password(self, user_id: UUID, new_password: str) -> bool:
        """
        Updates a user's password via Supabase Auth.
        """
        try:
            update_response = await self.supabase.auth.update_user({
                "id": str(user_id),
                "password": new_password
            })

            if update_response.error:
                self.logger.log("UserService", "error", "Failed to update user password", error=update_response.error.message)
                return False

            self.logger.log("UserService", "info", "User password updated successfully", user_id=str(user_id))
            return True

        except Exception as e:
            self.logger.log("UserService", "error", "Exception occurred while updating user password", error=str(e))
            return False

    # -------------------
    # Multi-Factor Authentication (MFA)
    # -------------------

    async def enroll_mfa(self, user_id: UUID, factor_type: str, friendly_name: str) -> Optional[Dict[str, Any]]:
        """
        Enrolls a user in MFA (currently supports TOTP).
        """
        try:
            mfa_response = await self.supabase.auth.mfa.enroll({
                "user_id": str(user_id),
                "factor_type": factor_type,
                "friendly_name": friendly_name
            })

            if mfa_response.error:
                self.logger.log("UserService", "error", "Failed to enroll MFA factor", error=mfa_response.error.message)
                return {"success": False, "error": mfa_response.error.message}

            self.logger.log("UserService", "info", "MFA factor enrolled successfully", user_id=str(user_id))
            return {"success": True, "factor": mfa_response.factor}

        except Exception as e:
            self.logger.log("UserService", "error", "Exception occurred while enrolling MFA factor", error=str(e))
            return {"success": False, "error": str(e)}

    async def verify_mfa_challenge(self, user_id: UUID, factor_id: str, code: str) -> Optional[Dict[str, Any]]:
        """
        Verifies an MFA challenge for a user.
        """
        try:
            verify_response = await self.supabase.auth.mfa.verify({
                "user_id": str(user_id),
                "factor_id": factor_id,
                "code": code
            })

            if verify_response.error:
                self.logger.log("UserService", "error", "Failed to verify MFA challenge", error=verify_response.error.message)
                return {"success": False, "error": verify_response.error.message}

            self.logger.log("UserService", "info", "MFA challenge verified successfully", user_id=str(user_id))
            return {"success": True}

        except Exception as e:
            self.logger.log("UserService", "error", "Exception occurred while verifying MFA challenge", error=str(e))
            return {"success": False, "error": str(e)}

    # -------------------
    # Utility Methods
    # -------------------

    async def list_users(self, limit: int = 50, page: int = 1) -> List[PrismaProfile]:
        """
        Lists users with pagination via Prisma.
        """
        try:
            skip = (page - 1) * limit
            profiles = await self.prisma.profile.find_many(take=limit, skip=skip)
            self.logger.log("UserService", "info", f"Listed {len(profiles)} users", limit=limit, page=page)
            return profiles
        except Exception as e:
            self.logger.log("UserService", "error", "Failed to list users", error=str(e))
            return []

    # Additional methods for linking/unlinking OAuth identities, handling sessions, etc., can be added here.


