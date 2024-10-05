import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.audit_service import AuditService
# from api.prisma.client import get_prisma
from prisma.models import audit_logs as PrismaAuditLog
from prisma import Prisma

@pytest.fixture
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()

    yield client
    await client.disconnect()

@pytest.fixture
def audit_service():
    return AuditService()

@pytest.mark.asyncio
async def test_create_audit_log(audit_service, prisma_client):
    # Mock data
    audit_data = {
        "user_id": str(uuid4()),
        "action_type": "CREATE",
        "entity_type": "block",
        "entity_id": str(uuid4()),
        "timestamp": datetime.utcnow(),
    }

    # Mock Prisma client's auditlog.create method
    # async for client in prisma_client:
    #     client.audit_logs.create = AsyncMock(return_value=PrismaAuditLog(
    #         log_id=str(uuid4()),
    #         user_id=audit_data["user_id"],
    #         action_type=audit_data["action_type"],
    #         entity_type=audit_data["entity_type"],
    #         entity_id=audit_data["entity_id"],
    #         timestamp=audit_data["timestamp"],
    #     ))

    # Invoke the service method
    async for client in prisma_client:
        result = await audit_service.create_audit_log(tx=client, audit_data=audit_data)

    # Assertions
    # prisma_client.auditlog.create.assert_called_once_with(data=audit_data)
    assert result.user_id == audit_data["user_id"]
    assert result.action_type == audit_data["action_type"]
    assert result.entity_type == audit_data["entity_type"]
    assert result.entity_id == audit_data["entity_id"]

@pytest.mark.asyncio
async def test_get_audit_log_by_id(audit_service, prisma_client):
    # Mock data
    log_id = str(uuid4())
    expected_log = PrismaAuditLog(
        log_id=log_id,
        user_id=str(uuid4()),
        action_type="UPDATE",
        entity_type="pipeline",
        entity_id=str(uuid4()),
        timestamp=datetime.utcnow(),
        details="Updated a pipeline."
    )

    # Mock Prisma client's auditlog.find_unique method
    prisma_client.auditlog.find_unique = AsyncMock(return_value=expected_log)

    # Invoke the service method
    result = await audit_service.get_audit_log_by_id(tx=prisma_client, log_id=log_id)

    # Assertions
    prisma_client.auditlog.find_unique.assert_called_once_with(where={"log_id": log_id})
    assert result.log_id == log_id
    assert result.action_type == "UPDATE"
    assert result.entity_type == "pipeline"

@pytest.mark.asyncio
async def test_update_audit_log(audit_service, prisma_client):
    # Mock data
    log_id = str(uuid4())
    update_data = {
        "action_type": "DELETE",
        "details": "Deleted a block."
    }
    updated_log = PrismaAuditLog(
        log_id=log_id,
        user_id=str(uuid4()),
        action_type=update_data["action_type"],
        entity_type="block",
        entity_id=str(uuid4()),
        timestamp=datetime.utcnow(),
        details=update_data["details"]
    )

    # Mock Prisma client's auditlog.update method
    prisma_client.auditlog.update = AsyncMock(return_value=updated_log)

    # Invoke the service method
    result = await audit_service.update_audit_log(tx=prisma_client, log_id=log_id, update_data=update_data)

    # Assertions
    prisma_client.auditlog.update.assert_called_once_with(
        where={"log_id": log_id},
        data=update_data
    )
    assert result.action_type == update_data["action_type"]
    assert result.details == update_data["details"]

@pytest.mark.asyncio
async def test_list_audit_logs(audit_service, prisma_client):
    # Mock data
    expected_logs = [
        PrismaAuditLog(
            log_id=str(uuid4()),
            user_id=str(uuid4()),
            action_type="CREATE",
            entity_type="block",
            entity_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            details="Created a new block."
        ),
        PrismaAuditLog(
            log_id=str(uuid4()),
            user_id=str(uuid4()),
            action_type="UPDATE",
            entity_type="pipeline",
            entity_id=str(uuid4()),
            timestamp=datetime.utcnow(),
            details="Updated a pipeline."
        )
    ]

    # Mock Prisma client's auditlog.find_many method
    prisma_client.auditlog.find_many = AsyncMock(return_value=expected_logs)

    # Invoke the service method without filters
    result = await audit_service.list_audit_logs(tx=prisma_client)

    # Assertions
    prisma_client.auditlog.find_many.assert_called_once_with(where={})
    assert len(result) == 2
    assert result[0].action_type == "CREATE"
    assert result[1].action_type == "UPDATE"

@pytest.mark.asyncio
async def test_delete_audit_log(audit_service, prisma_client):
    # Mock data
    log_id = str(uuid4())

    # Mock Prisma client's auditlog.delete method
    prisma_client.auditlog.delete = AsyncMock(return_value=True)

    # Invoke the service method
    result = await audit_service.delete_audit_log(tx=prisma_client, log_id=log_id)

    # Assertions
    prisma_client.auditlog.delete.assert_called_once_with(where={"log_id": log_id})
    assert result is True