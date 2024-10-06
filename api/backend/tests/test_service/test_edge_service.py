import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from api.backend.app.features.core.services.edge_service import EdgeService
from prisma.models import edges as PrismaEdge  # Adjust the import path as necessary
from prisma import Prisma
from api.backend.app.logger import ConstellationLogger

logger = ConstellationLogger()

edge1_id = "1"*32
edge2_id = "2"*32
edge3_id = "3"*32

edge1_data = {
    "edge_id": edge1_id,
    "name": "Edge 1",
    "edge_type": "type_a",
    "description": "Description 1",
    "source_block_id": "a"*32,
    "target_block_id": "b"*32,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    # "current_version_id": "f1"*16,
}

edge2_data = {
    "edge_id": edge2_id,
    "name": "Edge 2",
    "edge_type": "type_b",
    "description": "Description 2",
    "source_block_id": "c"*32,
    "target_block_id": "d"*32,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    # "current_version_id": "f2"*16,
}

edge3_data = {
    "edge_id": edge3_id,
    "name": "Edge 3",
    "edge_type": "type_c",
    "description": "Description 3",
    "source_block_id": "e"*32,
    "target_block_id": "f"*32,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    # "current_version_id": "f3"*16,
}


@pytest.fixture
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()

    yield client
    await client.disconnect()


@pytest.fixture
def edge_service():
    return EdgeService()


@pytest.mark.asyncio
async def test_create_edge(edge_service, prisma_client):
    logger.log("edge_service_test", "info", "Creating edge", extra={"edge_data": edge1_data})
    # Invoke the service method
    async for client in prisma_client:
        result = await edge_service.create_edge(tx=client, edge_data=edge1_data)

    # Assertions
    assert result.name == "Edge 1"
    assert result.edge_type == "type_a"


@pytest.mark.asyncio
async def test_get_edge_by_id(edge_service, prisma_client):
    logger.log("edge_service_test", "info", "Retrieving edge by ID", extra={"edge_id": edge1_id})
    # Invoke the service method
    async for client in prisma_client:
        result = await edge_service.get_edge_by_id(tx=client, edge_id=UUID(edge1_id))

    # Assertions
    assert result.name == "Edge 1"
    assert result.edge_type == "type_a"


@pytest.mark.asyncio
async def test_update_edge(edge_service, prisma_client):
    logger.log("edge_service_test", "info", "Updating edge", extra={"edge_id": edge1_id, "update_data": {"name": "Updated Edge 1"}})
    # Mock update data
    update_data = {
        "name": "Updated Edge 1",
        "description": "Updated Description",
        "updated_at": datetime.utcnow()
    }

    async for client in prisma_client:
        result = await edge_service.update_edge(tx=client, edge_id=UUID(edge1_id), update_data=update_data)

    # Assertions
    assert result.name == "Updated Edge 1"
    assert result.description == "Updated Description"


@pytest.mark.asyncio
async def test_delete_edge(edge_service, prisma_client):
    logger.log("edge_service_test", "info", "Deleting edge", extra={"edge_id": edge1_id})
    # Invoke the service method
    async for client in prisma_client:
        result = await edge_service.delete_edge(tx=client, edge_id=UUID(edge1_id))

    # Assertions
    assert result is True


@pytest.mark.asyncio
async def test_list_edges(edge_service, prisma_client):
    logger.log("edge_service_test", "info", "Listing edges", extra={"limit": 10, "offset": 0})
    # Mock filter and pagination
    limit = 10
    offset = 0

    async for client in prisma_client:
        await edge_service.create_edge(tx=client, edge_data=edge2_data)
        await edge_service.create_edge(tx=client, edge_data=edge3_data)
        result = await edge_service.list_edges(tx=client, limit=limit, offset=offset)

    # Assertions
    assert result is not None
    assert len(result) == 2
    assert result[0].name == "Edge 2"
    assert result[1].name == "Edge 3"


@pytest.mark.asyncio
async def test_assign_version_to_edge(edge_service, prisma_client):
    logger.log("edge_service_test", "info", "Assigning version to edge", extra={"edge_id": edge1_id, "version_id": "v4"*8})
    # Invoke the service method
    version_id = UUID("f4"*8 + "f4"*8)  # Adjust to a valid UUID if necessary
    updated_edge_data = edge2_data.copy()
    updated_edge_data["current_version_id"] = str(version_id)

    async for client in prisma_client:
        result = await edge_service.assign_version_to_edge(tx=client, edge_id=UUID(edge2_id), version_id=version_id)

    # Assertions
    assert result is True