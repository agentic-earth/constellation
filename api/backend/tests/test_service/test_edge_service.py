import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.edge_service import EdgeService
from api.prisma.client import get_prisma
from api.prisma.models import PrismaEdge  # Adjust the import path as necessary

@pytest.fixture
async def prisma_client():
    client = await get_prisma()
    yield client
    await client.disconnect()

@pytest.fixture
def edge_service():
    return EdgeService()

@pytest.mark.asyncio
async def test_create_edge(edge_service, prisma_client):
    # Mock data
    edge_data = {
        "edge_id": str(uuid4()),
        "name": "Test Edge",
        "edge_type": "primary",
        "description": "An edge for testing.",
        "source_block_id": str(uuid4()),
        "target_block_id": str(uuid4()),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "current_version_id": str(uuid4())
    }

    # Mock Prisma client's edges.create method
    prisma_client.edges.create = AsyncMock(return_value=PrismaEdge(**edge_data))

    # Invoke the service method
    result = await edge_service.create_edge(tx=prisma_client, edge_data=edge_data)

    # Assertions
    prisma_client.edges.create.assert_called_once_with(data=edge_data)
    assert result.name == "Test Edge"
    assert result.edge_type == "primary"

@pytest.mark.asyncio
async def test_get_edge_by_id(edge_service, prisma_client):
    # Mock data
    edge_id = str(uuid4())
    expected_edge = PrismaEdge(
        edge_id=edge_id,
        name="Existing Edge",
        edge_type="secondary",
        description="An existing edge.",
        source_block_id=str(uuid4()),
        target_block_id=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        current_version_id=str(uuid4())
    )

    # Mock Prisma client's edges.find_unique method
    prisma_client.edges.find_unique = AsyncMock(return_value=expected_edge)

    # Invoke the service method
    result = await edge_service.get_edge_by_id(tx=prisma_client, edge_id=edge_id)

    # Assertions
    prisma_client.edges.find_unique.assert_called_once_with(where={"edge_id": edge_id})
    assert result.name == "Existing Edge"
    assert result.edge_type == "secondary"

@pytest.mark.asyncio
async def test_update_edge(edge_service, prisma_client):
    # Mock data
    edge_id = str(uuid4())
    update_data = {
        "description": "Updated edge description.",
        "current_version_id": str(uuid4())
    }
    updated_edge = PrismaEdge(
        edge_id=edge_id,
        name="Updated Edge",
        edge_type="primary",
        description=update_data["description"],
        source_block_id=str(uuid4()),
        target_block_id=str(uuid4()),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        current_version_id=update_data["current_version_id"]
    )

    # Mock Prisma client's edges.update method
    prisma_client.edges.update = AsyncMock(return_value=updated_edge)

    # Invoke the service method
    result = await edge_service.update_edge(tx=prisma_client, edge_id=edge_id, edge_data=update_data)

    # Assertions
    prisma_client.edges.update.assert_called_once_with(
        where={"edge_id": edge_id},
        data=update_data
    )
    assert result.description == update_data["description"]
    assert result.current_version_id == update_data["current_version_id"]

@pytest.mark.asyncio
async def test_delete_edge(edge_service, prisma_client):
    # Mock data
    edge_id = str(uuid4())

    # Mock Prisma client's edges.delete method
    prisma_client.edges.delete = AsyncMock(return_value=True)

    # Invoke the service method
    result = await edge_service.delete_edge(tx=prisma_client, edge_id=edge_id)

    # Assertions
    prisma_client.edges.delete.assert_called_once_with(where={"edge_id": edge_id})
    assert result is True

@pytest.mark.asyncio
async def test_creates_cycle(edge_service, prisma_client):
    # Mock data
    source_block_id = uuid4()
    target_block_id = uuid4()

    # Mock Prisma client's edges.find_many method to simulate no cycle
    prisma_client.edges.find_many = AsyncMock(return_value=[])

    # Invoke the service method
    result = await edge_service.creates_cycle(tx=prisma_client, source_block_id=source_block_id, target_block_id=target_block_id)

    # Assertions
    prisma_client.edges.find_many.assert_called()
    assert result is False