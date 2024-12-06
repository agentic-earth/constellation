# backend/app/features/core/controllers/user_controller.py

import asyncio
import traceback
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from prisma import Prisma
from prisma.models import Profile as PrismaProfile, ApiKey as PrismaApiKey
from prisma.enums import ActionTypeEnum, AuditEntityTypeEnum

from backend.app.features.core.services.user_service import UserService
from backend.app.features.core.services.api_key_service import ApiKeyService
from backend.app.features.core.services.audit_service import AuditService
from backend.app.logger import ConstellationLogger
from supabase import Client
from backend.app.database import (
    get_supabase_client,
    get_supabase_admin_client,
    connect_db,
    disconnect_db,
)


class UserController:
    def __init__(
        self,
        prisma: Prisma,
        supabase: Client,
        supabase_admin: Client,
        logger: ConstellationLogger,
    ):
        self.prisma = prisma
        self.supabase = supabase
        self.supabase_admin = supabase_admin
        self.logger = logger

        self.user_service = UserService(logger=logger, hash_salt="your_secure_salt")
        self.api_key_service = ApiKeyService(
            logger=logger, hash_salt="your_secure_salt"
        )
        self.audit_service = AuditService()

    # -------------------
    # User Registration
    # -------------------

    async def register_user(
        self, email: str, password: str, username: str
    ) -> Dict[str, Any]:
        """
        Registers a new user and logs the action.
        Ensures ACID properties using transactions.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Register User
                registration_result = (
                    await self.user_service.register_user_email_password(
                        prisma=tx,
                        supabase=self.supabase,
                        email=email,
                        password=password,
                        username=username,
                    )
                )
                if not registration_result["success"]:
                    return registration_result

                profile = registration_result.get("profile")
                if not profile:
                    return {
                        "success": False,
                        "error": "profile_missing",
                        "message": "User profile was not created.",
                    }

                user_id = UUID(profile.auth_uid)

                # Step 2: Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": ActionTypeEnum.CREATE.name,
                    "entity_type": AuditEntityTypeEnum.profile.name.lower(),
                    "entity_id": str(user_id),
                    "details": {"username": username, "email": email},
                }
                audit_log = await self.audit_service.create_audit_log(
                    tx=tx, audit_data=audit_data
                )
                if not audit_log:
                    self.logger.log(
                        "UserController",
                        "warning",
                        "User created but audit log failed.",
                        user_id=str(user_id),
                    )

                return {
                    "success": True,
                    "profile": profile.dict(),
                    "message": "User registered successfully.",
                }

        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during user registration",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return {
                "success": False,
                "error": "registration_exception",
                "message": "An error occurred during user registration.",
            }

    # -------------------
    # User Sign-In
    # -------------------

    async def sign_in_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Signs in a user using email and password.
        """
        try:
            async with self.prisma.tx() as tx:
                sign_in_result = await self.user_service.sign_in_user_email_password(
                    supabase=self.supabase, email=email, password=password
                )
                return sign_in_result

        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during user sign-in",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return {
                "success": False,
                "error": "sign_in_exception",
                "message": "An error occurred during user sign-in.",
            }

    # -------------------
    # Update User Profile
    # -------------------

    async def update_user_profile(
        self, user_id: UUID, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Updates a user's profile and logs the action.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Update profile
                updated_profile = await self.user_service.update_profile(
                    prisma=tx, user_id=user_id, update_data=update_data
                )

                if not updated_profile:
                    return {
                        "success": False,
                        "error": "update_failed",
                        "message": "Failed to update user profile.",
                    }

                # Step 2: Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": ActionTypeEnum.UPDATE.name,
                    "entity_type": AuditEntityTypeEnum.profile.name.lower(),
                    "entity_id": str(user_id),
                    "details": {"updated_fields": update_data},
                }
                audit_log = await self.audit_service.create_audit_log(
                    tx=tx, audit_data=audit_data
                )
                if not audit_log:
                    self.logger.log(
                        "UserController",
                        "warning",
                        "User profile updated but audit log failed.",
                        user_id=str(user_id),
                    )

                return {
                    "success": True,
                    "profile": updated_profile.dict(),
                    "message": "User profile updated successfully.",
                }

        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during profile update",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return {
                "success": False,
                "error": "update_exception",
                "message": "An error occurred during profile update.",
            }

    # -------------------
    # Delete User
    # -------------------

    async def delete_user(self, user_id: UUID) -> bool:
        """
        Deletes a user, revokes all API keys, and logs the action.
        Ensures ACID properties using transactions.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Revoke all API keys
                api_keys = await self.api_key_service.get_api_keys_by_user(
                    prisma=tx, user_id=user_id
                )
                for api_key in api_keys:
                    await self.api_key_service.revoke_api_key(
                        prisma=tx, api_key_id=UUID(api_key.api_key_id)
                    )

                # Step 2: Delete user from Supabase Auth
                deletion_success = await self.user_service.delete_user(
                    prisma=tx, supabase_admin=self.supabase_admin, user_id=user_id
                )
                if not deletion_success:
                    return {"success": False, "error": "supabase_deletion_failed"}

                # Step 3: Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": ActionTypeEnum.DELETE.name,
                    "entity_type": AuditEntityTypeEnum.profile.name.lower(),
                    "entity_id": str(user_id),
                    "details": {"deleted_user_id": str(user_id)},
                }
                await self.audit_service.create_audit_log(tx=tx, audit_data=audit_data)

                return {"success": True, "message": "User deleted successfully"}

        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during user deletion",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return {"success": False, "error": "deletion_exception", "message": str(e)}

    # -------------------
    # Manage API Keys
    # -------------------

    async def list_api_keys_for_user(
        self, user_id: UUID
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Lists all API keys for a user.
        """
        try:
            async with self.prisma.tx() as tx:
                api_keys = await self.api_key_service.get_api_keys_by_user(
                    prisma=tx, user_id=user_id
                )
                if api_keys is None:
                    return None
                return [key.dict() for key in api_keys]
        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during listing API keys",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return None

    async def revoke_api_key(self, user_id: UUID, api_key_id: UUID) -> bool:
        """
        Revokes a specific API key for a user and logs the action.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Revoke the API key
                revoke_success = await self.api_key_service.revoke_api_key(
                    prisma=tx, api_key_id=api_key_id
                )
                if not revoke_success:
                    return False

                # Step 2: Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": ActionTypeEnum.UPDATE.name,
                    "entity_type": AuditEntityTypeEnum.api_key.name.lower(),
                    "entity_id": str(api_key_id),
                    "details": {"action": "revoke_api_key"},
                }
                audit_log = await self.audit_service.create_audit_log(
                    tx=tx, audit_data=audit_data
                )
                if not audit_log:
                    self.logger.log(
                        "UserController",
                        "warning",
                        "API key revoked but audit log failed.",
                        user_id=str(user_id),
                    )

                return True

        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during API key revocation",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return False

    async def delete_api_key(self, user_id: UUID, api_key_id: UUID) -> bool:
        """
        Deletes a specific API key for a user and logs the action.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Delete the API key
                delete_success = await self.api_key_service.delete_api_key(
                    prisma=tx, api_key_id=api_key_id
                )
                if not delete_success:
                    return False

                # Step 2: Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": ActionTypeEnum.DELETE.name,
                    "entity_type": AuditEntityTypeEnum.api_key.name.lower(),
                    "entity_id": str(api_key_id),
                    "details": {"action": "delete_api_key"},
                }
                audit_log = await self.audit_service.create_audit_log(
                    tx=tx, audit_data=audit_data
                )
                if not audit_log:
                    self.logger.log(
                        "UserController",
                        "warning",
                        "API key deleted but audit log failed.",
                        user_id=str(user_id),
                    )

                return True

        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during API key deletion",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return False

    # -------------------
    # Additional User Operations (e.g., Password Reset, MFA)
    # -------------------
    # Implement similarly as needed
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a user's profile.
        """
        try:
            profile = await self.user_service.get_profile_by_user_id(
                prisma=self.prisma, user_id=UUID(user_id)
            )
            if profile:
                return {
                    "success": True,
                    "profile": {
                        "auth_uid": profile.auth_uid,
                        "username": profile.username,
                        "email": profile.email,
                        # Add any other profile fields you want to return
                    },
                }
            else:
                self.logger.log(
                    "UserController", "warning", "Profile not found", user_id=user_id
                )
                return {
                    "success": False,
                    "error": "profile_not_found",
                    "message": "User profile not found.",
                }
        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Failed to retrieve user profile",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return {
                "success": False,
                "error": "retrieval_error",
                "message": "Failed to retrieve user profile.",
            }

    async def create_api_key(self, user_id: str) -> Dict[str, Any]:
        """
        Creates a new API key for a user and logs the action.
        """
        try:
            async with self.prisma.tx() as tx:
                # Set expiration date (e.g., 30 days from now)
                expires_at = datetime.utcnow() + timedelta(days=30)

                # Step 1: Create the API key
                new_api_key_obj, raw_api_key = (
                    await self.api_key_service.create_api_key(
                        prisma=tx, user_id=UUID(user_id), expires_at=expires_at
                    )
                )

                if not new_api_key_obj:
                    return {
                        "success": False,
                        "error": "api_key_creation_failed",
                        "message": "Failed to create API key.",
                    }

                api_key_id = new_api_key_obj.api_key_id

                # Step 2: Audit Logging
                audit_data = {
                    "user_id": user_id,
                    "action_type": ActionTypeEnum.CREATE.name,
                    "entity_type": AuditEntityTypeEnum.api_key.name.lower(),
                    "entity_id": str(
                        api_key_id
                    ),  # Using the API key ID as the entity_id
                    "description": f"Created new API key for user {user_id}",
                }
                audit_log = await self.audit_service.create_audit_log(
                    tx=tx, audit_data=audit_data
                )
                if not audit_log:
                    self.logger.log(
                        "UserController",
                        "warning",
                        "API key created but audit log failed.",
                        user_id=user_id,
                    )

                return {
                    "success": True,
                    "api_key_id": api_key_id,  # Return the UUID
                    "raw_api_key": raw_api_key,  # Return the raw API key
                    "expires_at": expires_at.isoformat(),
                }

        except Exception as e:
            self.logger.log(
                "UserController",
                "error",
                "Exception during API key creation",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return {
                "success": False,
                "error": "internal_error",
                "message": "An error occurred during API key creation.",
            }


# -------------------
# Testing Utility
# -------------------
async def run_user_controller_tests():
    """
    Function to run UserController tests.
    """
    # Initialize Logger
    logger = ConstellationLogger()

    # Initialize Prisma client and connect to the database
    prisma = Prisma()
    await prisma.connect()

    try:
        await connect_db()
        logger.log("UserController", "info", "Prisma client connected successfully.")
    except Exception as e:
        logger.log(
            "UserController",
            "critical",
            "Failed to connect Prisma client",
            error=str(e),
            traceback=traceback.format_exc(),
        )
        return

    # Initialize Supabase clients
    supabase_client = get_supabase_client()
    supabase_admin_client = get_supabase_admin_client()

    # Create UserController instance
    user_controller = UserController(
        prisma, supabase_client, supabase_admin_client, logger
    )

    # Test user registration or sign-in
    email = "mason_lee@brown.edu"
    password = "securePassword123!"
    username = "mason_lee"
    user_id = None

    try:
        print("=== Starting User Registration ===")
        registration_result = await user_controller.register_user(
            email, password, username
        )

        if registration_result["success"]:
            print(f"User registered successfully: {registration_result['message']}")
            user_id = registration_result["profile"]["auth_uid"]
        else:
            if registration_result.get("error") == "email_exists":
                print(f"User registration failed: {registration_result['message']}")
                print("Attempting to sign in with existing credentials...")
                sign_in_result = await user_controller.sign_in_user(email, password)
                if sign_in_result["success"]:
                    print("Signed in successfully with existing account.")
                    user_id = sign_in_result["user"]["id"]
                else:
                    print(
                        f"Sign-in failed: {sign_in_result.get('message', 'Unknown error')}"
                    )
                    return
            else:
                print(f"User registration failed: {registration_result['message']}")
                return

        if user_id:
            # Test retrieving user profile
            print("\n=== Retrieving User Profile ===")
            profile = await user_controller.get_user_profile(user_id)
            if profile:
                print("User profile retrieved successfully:")
                print(f"profile: {profile}")
                print(f"User ID: {profile['profile']['auth_uid']}")
                print(f"Username: {profile['profile']['username']}")
                print(f"Email: {profile['profile']['email']}")
            else:
                print("User profile retrieval failed.")

            # Test updating user profile
            print("\n=== Updating User Profile ===")
            new_username = "new_mason_lee"
            update_data = {"username": new_username}
            update_result = await user_controller.update_user_profile(
                user_id, update_data
            )
            if update_result["success"]:
                print("User profile updated successfully:")
                print(f"New Username: {update_result['profile']['username']}")
            else:
                print(
                    f"User profile update failed: {update_result.get('message', 'Unknown error')}"
                )

            # Test listing API keys before any are created
            print("\n=== Listing API Keys for User ===")
            api_keys = await user_controller.list_api_keys_for_user(user_id)
            if api_keys is not None:
                if len(api_keys) == 0:
                    print("User has no API keys.")
                else:
                    print(f"User has {len(api_keys)} API key(s):")
                    for key in api_keys:
                        print(
                            f"- API Key ID: {key['api_key_id']}, Expires At: {key['expires_at']}, Is Active: {key['is_active']}"
                        )
            else:
                print("Failed to retrieve API keys.")

            # Test creating a new API key
            print("\n=== Creating New API Key ===")
            new_api_key_response = await user_controller.create_api_key(user_id)
            if new_api_key_response["success"]:
                api_key_id = new_api_key_response["api_key_id"]
                raw_api_key = new_api_key_response["raw_api_key"]
                print(f"New API Key created: {raw_api_key} (ID: {api_key_id})")
            else:
                print("Failed to create new API key.")

            # Test revoking API key using `api_key_id`
            if new_api_key_response["success"]:
                print("\n=== Revoking API Key ===")
                api_key_id = new_api_key_response["api_key_id"]
                print(f"Revoking API Key ID: {api_key_id}")
                try:
                    revoke_uuid = UUID(api_key_id)  # Ensure it's a valid UUID
                    revoke_result = await user_controller.revoke_api_key(
                        user_id, revoke_uuid
                    )
                    if revoke_result:
                        print("API key revoked successfully.")
                    else:
                        print("Failed to revoke API key.")
                except ValueError as ve:
                    print(f"Invalid UUID provided for revocation: {ve}")

            # Optionally, list API keys after revocation
            print("\n=== Listing API Keys for User After Revocation ===")
            api_keys_after_revocation = await user_controller.list_api_keys_for_user(
                user_id
            )
            if api_keys_after_revocation is not None:
                if len(api_keys_after_revocation) == 0:
                    print("User has no API keys.")
                else:
                    print(f"User has {len(api_keys_after_revocation)} API key(s):")
                    for key in api_keys_after_revocation:
                        print(
                            f"- API Key ID: {key['api_key_id']}, Expires At: {key['expires_at']}, Is Active: {key['is_active']}"
                        )
            else:
                print("Failed to retrieve API keys.")

            # Test deleting user
            print("\n=== Deleting User ===")
            delete_result = await user_controller.delete_user(user_id)
            if delete_result:
                print("User deleted successfully.")
            else:
                print("User deletion failed.")

    except Exception as e:
        print(f"An error occurred during testing: {str(e)}")
        logger.log(
            "UserController",
            "error",
            "Exception during user controller testing",
            error=str(e),
            traceback=traceback.format_exc(),
        )
    finally:
        # Disconnect from the database
        try:
            await disconnect_db()
            logger.log(
                "UserController", "info", "Prisma client disconnected successfully."
            )
        except Exception as e:
            logger.log(
                "UserController",
                "error",
                "Failed to disconnect Prisma client",
                error=str(e),
                traceback=traceback.format_exc(),
            )


if __name__ == "__main__":
    asyncio.run(run_user_controller_tests())
