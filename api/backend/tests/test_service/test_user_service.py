import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from api.backend.app.features.core.services.user_service import UserService
from prisma.models import users as PrismaUser  # Adjust the import path as necessary
from prisma import Prisma
from api.backend.app.logger import ConstellationLogger


logger = ConstellationLogger()

user1_id = "1" * 32
user2_id = "2" * 32
user3_id = "3" * 32

user1_data = {
    "user_id": user1_id,
    "username": "user1",
    "email": "user1@example.com",
    "password_hash": "hashed_password1",
    "role": "admin",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

user2_data = {
    "user_id": user2_id,
    "username": "user2",
    "email": "user2@example.com",
    "password_hash": "hashed_password2",
    "role": "editor",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

user3_data = {
    "user_id": user3_id,
    "username": "user3",
    "email": "user3@example.com",
    "password_hash": "hashed_password3",
    "role": "viewer",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}


@pytest.fixture
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()

    yield client
    await client.disconnect()


@pytest.fixture
def user_service():
    return UserService()


@pytest.mark.asyncio
async def test_create_user(user_service, prisma_client):
    logger.log("user_service_test", "info", "Creating user", extra={"user_data": user1_data})
    # Invoke the service method
    async for client in prisma_client:
        result = await user_service.create_user(tx=client, user_data=user1_data)

    # Assertions
    assert result.username == "user1"
    assert result.email == "user1@example.com"
    assert result.role == "admin"


@pytest.mark.asyncio
async def test_get_user_by_id(user_service, prisma_client):
    logger.log("user_service_test", "info", "Retrieving user by ID", extra={"user_id": user1_id})
    # Invoke the service method
    async for client in prisma_client:
        result = await user_service.get_user_by_id(tx=client, user_id=UUID(user1_id))

    # Assertions
    assert result.username == "user1"
    assert result.email == "user1@example.com"


@pytest.mark.asyncio
async def test_update_user(user_service, prisma_client):
    logger.log("user_service_test", "info", "Updating user", extra={"user_id": user1_id, "update_data": {"username": "updated_user1"}})
    # Mock update data
    update_data = {
        "username": "updated_user1",
        "email": "updated_user1@example.com",
        "updated_at": datetime.utcnow()
    }

    async for client in prisma_client:
        result = await user_service.update_user(tx=client, user_id=UUID(user1_id), update_data=update_data)

    # Assertions
    assert result.username == "updated_user1"
    assert result.email == "updated_user1@example.com"


@pytest.mark.asyncio
async def test_delete_user(user_service, prisma_client):
    logger.log("user_service_test", "info", "Deleting user", extra={"user_id": user1_id})
    # Invoke the service method
    async for client in prisma_client:
        result = await user_service.delete_user(tx=client, user_id=UUID(user1_id))

    # Assertions
    assert result is True


@pytest.mark.asyncio
async def test_list_users(user_service, prisma_client):
    logger.log("user_service_test", "info", "Listing users")

    async for client in prisma_client:
        await user_service.create_user(tx=client, user_data=user2_data)
        await user_service.create_user(tx=client, user_data=user3_data)
        result = await user_service.list_users(tx=client)

    # Assertions
    assert result is not None
    assert len(result) == 2
    assert result[0].username == "user2"
    assert result[1].username == "user3"


# @pytest.mark.asyncio
# async def test_authenticate_user_success(user_service, prisma_client):
#     logger.log("user_service_test", "info", "Authenticating user", extra={"email": user1_data["email"], "password": "correct_password"})
#     # Invoke the service method
#     async for client in prisma_client:
#         client.users.find_unique = AsyncMock(return_value=PrismaUser(**user1_data))
#         # Mock verify_password to return True
#         with pytest.MonkeyPatch.context() as m:
#             m.setattr("api.backend.app.features.core.services.user_service.verify_password", AsyncMock(return_value=True))
#             result = await user_service.authenticate_user(tx=client, email=user1_data["email"], password="correct_password")

#     # Assertions
#     assert result.username == "user1"
#     assert result.email == "user1@example.com"


# @pytest.mark.asyncio
# async def test_authenticate_user_failure_wrong_password(user_service, prisma_client):
#     logger.log("user_service_test", "info", "Authenticating user with wrong password", extra={"email": user1_data["email"], "password": "wrong_password"})
#     # Invoke the service method
#     async for client in prisma_client:
#         client.users.find_unique = AsyncMock(return_value=PrismaUser(**user1_data))
#         # Mock verify_password to return False
#         with pytest.MonkeyPatch.context() as m:
#             m.setattr("api.backend.app.features.core.services.user_service.verify_password", AsyncMock(return_value=False))
#             result = await user_service.authenticate_user(tx=client, email=user1_data["email"], password="wrong_password")

#     # Assertions
#     assert result is None


# @pytest.mark.asyncio
# async def test_authenticate_user_failure_user_not_found(user_service, prisma_client):
#     logger.log("user_service_test", "info", "Authenticating non-existent user", extra={"email": "nonexistent@example.com", "password": "any_password"})
#     # Invoke the service method
#     async for client in prisma_client:
#         client.users.find_unique = AsyncMock(return_value=None)
#         result = await user_service.authenticate_user(tx=client, email="nonexistent@example.com", password="any_password")

#     # Assertions
#     assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email(user_service, prisma_client):
    logger.log("user_service_test", "info", "Retrieving user by email", extra={"email": user2_data["email"]})
    # Invoke the service method
    async for client in prisma_client:
        result = await user_service.get_user_by_email(tx=client, email=user2_data["email"])

    # Assertions
    assert result.username == "user2"
    assert result.email == "user2@example.com"