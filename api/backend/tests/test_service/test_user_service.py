import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.user_service import UserService
from api.prisma.client import get_prisma
from prisma.models import users as PrismaUser  # Adjust the import path as necessary
from prisma import Prisma

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
    # Mock data
    user_data = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "password_hash": "hashed_password",
        "role": "user"
    }
    created_user = PrismaUser(
        user_id=str(uuid4()),
        username=user_data["username"],
        email=user_data["email"],
        password_hash=user_data["password_hash"],
        role=user_data["role"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Mock Prisma client's users.create method
    # prisma_client.users.create = AsyncMock(return_value=created_user)

    # Invoke the service method
    async for client in prisma_client:
        result = await user_service.create_user(tx=client, user_data=user_data)

    assert result.username == user_data["username"]
    assert result.email == user_data["email"]
    assert result.role == user_data["role"]

@pytest.mark.asyncio
async def test_get_user_by_id(user_service, prisma_client):
    # 1. create a user
    user_data = {
        "username": "test_get_user_by_id",
        "email": "test_get_user_by_id@example.com",
        "password_hash": "hashed_password",
        "role": "user"
    }
    created_user = PrismaUser(
        user_id=str(uuid4()),
        username=user_data["username"],
        email=user_data["email"],
        password_hash=user_data["password_hash"],
        role=user_data["role"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    async for client in prisma_client:
        result = await user_service.create_user(tx=client, user_data=user_data)

    # 2. get the user by id
    async for client in prisma_client:
        result = await user_service.get_user_by_id(tx=client, user_id=created_user.user_id)

    # 3. assert the user is correct
    assert result.username == user_data["username"]
    assert result.email == user_data["email"]
    assert result.role == user_data["role"]


@pytest.mark.asyncio
async def test_update_user(user_service, prisma_client):
    # Mock data
    user_id = uuid4()
    update_data = {
        "username": "updateduser",
        "email": "updateduser@example.com",
        "role": "moderator"
    }
    updated_user = PrismaUser(
        user_id=str(user_id),
        username=update_data["username"],
        email=update_data["email"],
        password_hash="existing_hashed_password",
        role=update_data["role"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Mock Prisma client's users.update method
    prisma_client.users.update = AsyncMock(return_value=updated_user)

    # Invoke the service method
    result = await user_service.update_user(tx=prisma_client, user_id=user_id, update_data=update_data)

    # Assertions
    prisma_client.users.update.assert_called_once_with(
        where={"user_id": str(user_id)},
        data={
            "username": update_data["username"],
            "email": update_data["email"],
            "role": update_data["role"],
            "updated_at": ANY
        }
    )
    assert result.username == update_data["username"]
    assert result.email == update_data["email"]
    assert result.role == update_data["role"]

@pytest.mark.asyncio
async def test_delete_user(user_service, prisma_client):
    # Mock data
    user_id = uuid4()

    # Mock Prisma client's users.delete method
    prisma_client.users.delete = AsyncMock(return_value=True)

    # Invoke the service method
    result = await user_service.delete_user(tx=prisma_client, user_id=user_id)

    # Assertions
    prisma_client.users.delete.assert_called_once_with(where={"user_id": str(user_id)})
    assert result is True

@pytest.mark.asyncio
async def test_create_user_failure(user_service, prisma_client):
    # Mock data
    user_data = {
        "username": "failuser",
        "email": "failuser@example.com",
        "password_hash": "hashed_password",
        "role": "user"
    }

    # Mock Prisma client's users.create method to raise an exception
    prisma_client.users.create = AsyncMock(side_effect=Exception("Database Error"))

    # Invoke the service method
    result = await user_service.create_user(tx=prisma_client, user_data=user_data)

    # Assertions
    prisma_client.users.create.assert_called_once_with(data={
        "user_id": ANY,
        "username": user_data["username"],
        "email": user_data["email"],
        "password_hash": user_data["password_hash"],
        "role": user_data["role"],
        "created_at": ANY,
        "updated_at": ANY,
    })
    assert result is None

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service, prisma_client):
    # Mock data
    user_id = uuid4()

    # Mock Prisma client's users.find_unique method to return None
    prisma_client.users.find_unique = AsyncMock(return_value=None)

    # Invoke the service method
    result = await user_service.get_user_by_id(tx=prisma_client, user_id=user_id)

    # Assertions
    prisma_client.users.find_unique.assert_called_once_with(where={"user_id": str(user_id)})
    assert result is None