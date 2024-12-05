# backend/app/features/core/services/api_key_service.py

import uuid
import secrets
import hashlib
from typing import Optional, List, Dict, Any
from uuid import UUID
import datetime
import traceback
from prisma import Prisma
from prisma.models import ApiKey as PrismaApiKey
from backend.app.logger import ConstellationLogger


class ApiKeyService:
    def __init__(self, logger: ConstellationLogger, hash_salt: str):
        self.logger = logger
        # In a real application, use environment variables for salts and other secrets
        self.hash_salt = hash_salt

    def generate_api_key(self) -> str:
        """
        Generates a secure, random API key.
        """
        return secrets.token_urlsafe(32)

    def hash_api_key(self, api_key: str) -> str:
        """
        Hashes the API key using SHA-256.
        """
        return hashlib.sha256((api_key + self.hash_salt).encode()).hexdigest()

    async def create_api_key(
        self, prisma: Prisma, user_id: UUID, expires_at: datetime.datetime
    ) -> tuple[Optional[PrismaApiKey], Optional[str]]:
        """
        Creates a new API key for a user.
        """
        try:
            raw_api_key = self.generate_api_key()
            hashed_api_key = self.hash_api_key(raw_api_key)

            new_api_key = await prisma.apikey.create(
                data={
                    "user_id": str(user_id),
                    "encrypted_api_key": hashed_api_key,
                    "expires_at": expires_at,
                    "is_active": True,
                }
            )
            self.logger.log(
                "ApiKeyService",
                "info",
                "API key created successfully",
                api_key_id=new_api_key.api_key_id,
                user_id=str(user_id),
            )
            return new_api_key, raw_api_key  # Return the raw API key to the user
        except Exception as e:
            self.logger.log(
                "ApiKeyService",
                "error",
                "Failed to create API key",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return None

    async def get_api_keys_by_user(
        self, prisma: Prisma, user_id: UUID
    ) -> Optional[List[PrismaApiKey]]:
        """
        Retrieves all API keys for a specific user.
        """
        try:
            api_keys = await prisma.apikey.find_many(where={"user_id": str(user_id)})
            self.logger.log(
                "ApiKeyService",
                "info",
                "Retrieved API keys for user",
                user_id=str(user_id),
                count=len(api_keys),
            )
            return api_keys
        except Exception as e:
            self.logger.log(
                "ApiKeyService",
                "error",
                "Failed to retrieve API keys",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return None

    async def revoke_api_key(self, prisma: Prisma, api_key_id: UUID) -> bool:
        """
        Revokes (deactivates) an API key.
        """
        try:
            updated_api_key = await prisma.apikey.update(
                where={"api_key_id": str(api_key_id)}, data={"is_active": False}
            )
            self.logger.log(
                "ApiKeyService",
                "info",
                "API key revoked successfully",
                api_key_id=str(api_key_id),
            )
            return True
        except Exception as e:
            self.logger.log(
                "ApiKeyService",
                "error",
                "Failed to revoke API key",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return False

    async def delete_api_key(self, prisma: Prisma, api_key_id: UUID) -> bool:
        """
        Deletes an API key from the database.
        """
        try:
            await prisma.apikey.delete(where={"api_key_id": str(api_key_id)})
            self.logger.log(
                "ApiKeyService",
                "info",
                "API key deleted successfully",
                api_key_id=str(api_key_id),
            )
            return True
        except Exception as e:
            self.logger.log(
                "ApiKeyService",
                "error",
                "Failed to delete API key",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return False

    async def validate_api_key(
        self, prisma: Prisma, raw_api_key: str
    ) -> Optional[PrismaApiKey]:
        """
        Validates an API key by hashing and comparing it with stored hashes.
        """
        try:
            hashed_key = self.hash_api_key(raw_api_key)
            api_key = await prisma.apikey.find_first(
                where={
                    "encrypted_api_key": hashed_key,
                    "is_active": True,
                    "expires_at": {"gt": datetime.datetime.utcnow()},
                }
            )
            if api_key:
                self.logger.log(
                    "ApiKeyService",
                    "info",
                    "API key validated successfully",
                    api_key_id=api_key.api_key_id,
                )
                return api_key
            else:
                self.logger.log(
                    "ApiKeyService", "warning", "Invalid or expired API key"
                )
                return None
        except Exception as e:
            self.logger.log(
                "ApiKeyService",
                "error",
                "Failed to validate API key",
                error=str(e),
                traceback=traceback.format_exc(),
            )
            return None

    # -------------------
    # Additional CRUD Operations (Optional)
    # -------------------
    # Implement similarly as needed


async def main():
    # Initialize Logger
    logger = ConstellationLogger()

    # Initialize Prisma client
    prisma = Prisma()
    try:
        await prisma.connect()
        logger.log("ApiKeyService", "info", "Prisma client connected successfully.")
    except Exception as e:
        logger.log(
            "ApiKeyService",
            "critical",
            "Failed to connect Prisma client",
            error=str(e),
            traceback=traceback.format_exc(),
        )
        return

    # Create an instance of ApiKeyService
    hash_salt = "your_hash_salt_here"  # Replace with your actual hash salt or retrieve from environment
    api_key_service = ApiKeyService(logger, hash_salt)

    # Example user_id (Replace with a valid user_id from your database)
    test_user_id = UUID("802e55c2-b804-40a6-bf26-7079cb6d5b80")
    expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)

    try:
        print("=== Creating API Key ===")
        new_api_key, raw_api_key = await api_key_service.create_api_key(
            prisma=prisma, user_id=test_user_id, expires_at=expiration_date
        )

        if new_api_key:
            print(f"New API key created: {new_api_key}")

            # Get API keys for the user
            user_keys = await api_key_service.get_api_keys_by_user(
                prisma=prisma, user_id=test_user_id
            )
            if user_keys:
                print(f"User has {len(user_keys)} API key(s)")

            # Validate the API key
            validated_key = await api_key_service.validate_api_key(
                prisma=prisma, raw_api_key=raw_api_key
            )
            if validated_key:
                print("API key is valid")

                # Revoke the API key
                revoked = await api_key_service.revoke_api_key(
                    prisma=prisma, api_key_id=validated_key.api_key_id
                )
                if revoked:
                    print("API key revoked successfully")

                # Try to validate the revoked key
                revoked_key_check = await api_key_service.validate_api_key(
                    prisma=prisma, raw_api_key=new_api_key
                )
                if not revoked_key_check:
                    print("Revoked API key is no longer valid")

                # Delete the API key
                deleted = await api_key_service.delete_api_key(
                    prisma=prisma, api_key_id=validated_key.api_key_id
                )
                if deleted:
                    print("API key deleted successfully")
            else:
                print("API key validation failed")
        else:
            print("Failed to create API key")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Disconnect from the database
        try:
            await prisma.disconnect()
            logger.log(
                "ApiKeyService", "info", "Prisma client disconnected successfully."
            )
        except Exception as e:
            logger.log(
                "ApiKeyService",
                "error",
                "Failed to disconnect Prisma client",
                error=str(e),
                traceback=traceback.format_exc(),
            )


import asyncio

if __name__ == "__main__":
    asyncio.run(main())
