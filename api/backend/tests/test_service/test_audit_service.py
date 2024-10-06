import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from api.backend.app.features.core.services.audit_service import AuditService
from prisma.models import audit_logs as PrismaAuditLog, users as PrismaUser
from prisma import Prisma
from api.backend.app.logger import ConstellationLogger
from api.backend.app.features.core.services.user_service import UserService

logger = ConstellationLogger()

# Sample User Data
user1_id = "1" * 32
user1_data = {
    "user_id": user1_id,
    "username": "testuser",
    "email": "testuser@example.com",
    "password_hash": "hashed_password",
    "role": "admin",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

# Sample Audit Log Data
audit_log1_id = "a1" * 16
audit_log1_data = {
    "log_id": audit_log1_id,
    "user_id": user1_id,
    "action_type": "CREATE",
    "entity_type": "edge",
    "entity_id": "e1" * 16,
    "timestamp": datetime.utcnow(),
    "details": '{"key": "value"}'
}

audit_log2_id = "a2" * 16
audit_log2_data = {
    "log_id": audit_log2_id,
    "user_id": user1_id,
    "action_type": "UPDATE",
    "entity_type": "block",
    "entity_id": "b1" * 16,
    "timestamp": datetime.utcnow(),
    "details": '{"key": "new_value"}'
}

@pytest.fixture(scope="module")
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()

    yield client
    await client.disconnect()

@pytest.fixture(scope="module")
def user_service():
    return UserService()

@pytest.fixture(scope="module")
def audit_service():
    return AuditService()

@pytest.mark.asyncio
async def test_setup_user(prisma_client, user_service):
    async for client in prisma_client:
        created_user = await user_service.create_user(tx=client, user_data=user1_data)
        assert created_user is not None
        assert created_user.user_id == str(UUID(user1_id))

@pytest.mark.asyncio
async def test_create_audit_log(audit_service, prisma_client):
    logger.log("audit_service_test", "info", "Testing audit log creation")

    async for client in prisma_client:
        result = await audit_service.create_audit_log(tx=client, audit_data=audit_log1_data)

        # Assertions
        assert result is not None
        assert result.log_id == str(UUID(audit_log1_id))
        assert result.user_id == str(UUID(user1_id))
        assert result.action_type == "CREATE"
        assert result.entity_type == "edge"

@pytest.mark.asyncio
async def test_get_audit_log_by_id(audit_service, prisma_client):
    logger.log("audit_service_test", "info", "Testing get_audit_log_by_id")

    async for client in prisma_client:
        result = await audit_service.get_audit_log_by_id(tx=client, log_id=UUID(audit_log1_id))

        # Assertions
        assert result is not None
        assert result.log_id == str(UUID(audit_log1_id))
        assert result.user_id == str(UUID(user1_id))
        assert result.action_type == "CREATE"
        assert result.entity_type == "edge"

@pytest.mark.asyncio
async def test_update_audit_log(audit_service, prisma_client):
    logger.log("audit_service_test", "info", "Testing update_audit_log")

    update_data = {
        "action_type": "UPDATE",
        "details": '{"key": "updated_value"}'
    }

    async for client in prisma_client:
        result = await audit_service.update_audit_log(tx=client, log_id=UUID(audit_log1_id), update_data=update_data)

        # Assertions
        assert result is not None
        assert result.log_id == str(UUID(audit_log1_id))
        assert result.action_type == "UPDATE"
        assert result.details == '{"key": "updated_value"}'

@pytest.mark.asyncio
async def test_list_audit_logs(audit_service, prisma_client):
    logger.log("audit_service_test", "info", "Testing list_audit_logs")

    async for client in prisma_client:
        # Create another audit log for testing list function
        await audit_service.create_audit_log(tx=client, audit_data=audit_log2_data)
        
        result = await audit_service.list_audit_logs(tx=client, filters={"user_id": user1_id})

        # Assertions
        assert result is not None
        assert len(result) == 2
        assert result[0].log_id == str(UUID(audit_log1_id))
        assert result[1].log_id == str(UUID(audit_log2_id))

@pytest.mark.asyncio
async def test_delete_audit_log(audit_service, prisma_client):
    logger.log("audit_service_test", "info", "Testing delete_audit_log")

    async for client in prisma_client:
        result = await audit_service.delete_audit_log(tx=client, log_id=UUID(audit_log1_id))

        # Assertions
        assert result is True

        # Verify the log is deleted
        deleted_log = await audit_service.get_audit_log_by_id(tx=client, log_id=UUID(audit_log1_id))
        assert deleted_log is None

# Clean up
@pytest.mark.asyncio
async def test_cleanup(prisma_client, user_service, audit_service):
    async for client in prisma_client:
        # Delete remaining audit log
        await audit_service.delete_audit_log(tx=client, log_id=UUID(audit_log2_id))
        
        # Delete user
        await user_service.delete_user(tx=client, user_id=UUID(user1_id))

        # Verify user is deleted
        deleted_user = await user_service.get_user_by_id(tx=client, user_id=UUID(user1_id))
        assert deleted_user is None