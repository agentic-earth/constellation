import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.block_service import BlockService
from prisma.models import blocks as PrismaBlock  # Adjust the import path as necessary
from prisma import Prisma
from api.backend.app.logger import ConstellationLogger

logger = ConstellationLogger()

block1_id = "1"*32
block2_id = "2"*32
block3_id = "3"*32

block1_data = {
    "block_id": block1_id,
    "name": "Block 1",
    "block_type": "dataset",
    "description": "Description 1",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    # "current_version_id": str(uuid4()),
}

block2_data = {
    "block_id": block2_id,
    "name": "Block 2",
    "block_type": "model",
    "description": "Description 2",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    # "current_version_id": str(uuid4()),
}

block3_data = {
    "block_id": block3_id,
    "name": "Block 3",
    "block_type": "dataset",
    "description": "Description 3",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    # "current_version_id": str(uuid4()),
}


@pytest.fixture
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()

    yield client
    await client.disconnect()

@pytest.fixture
def block_service():
    return BlockService()

@pytest.mark.asyncio
async def test_create_block(block_service, prisma_client):
    logger.log("block_service_test", "info", "Creating block", extra={"block_data": block1_data})
    # Invoke the service method
    async for client in prisma_client:
        result = await block_service.create_block(tx=client, block_data=block1_data)
    
    # Assertions
    assert result.name == "Block 1"
    assert result.block_type == "dataset"

@pytest.mark.asyncio
async def test_get_block_by_id(block_service, prisma_client):
    # Invoke the service method
    async for client in prisma_client:
        result = await block_service.get_block_by_id(tx=client, block_id=block1_id)

    # Assertions
    assert result.name == "Block 1"
    assert result.block_type == "dataset"

@pytest.mark.asyncio
async def test_update_block(block_service, prisma_client):
    # Mock update data
    update_data = {
        "name": "Block after update",
        "block_type": "model",
        "description": "Description after update.",
        "updated_at": datetime.utcnow()
    }

    async for client in prisma_client:
        # Invoke the service method
        result = await block_service.update_block(tx=client, block_id=block1_id, update_data=update_data)

    # Assertions
    assert result.name == "Block after update"
    assert result.description == "Description after update."

@pytest.mark.asyncio
async def test_delete_block(block_service, prisma_client):
    # Invoke the service method
    async for client in prisma_client:
        result = await block_service.delete_block(tx=client, block_id=block1_id)

    # Assertions
    assert result is True

@pytest.mark.asyncio
async def test_get_blocks_by_ids(block_service, prisma_client):
    # Mock data
    block_ids = [block2_id, block3_id]

    # Invoke the service method
    async for client in prisma_client:
        await client.blocks.create(data=block2_data)
        await client.blocks.create(data=block3_data)
        result = await block_service.get_blocks_by_ids(tx=client, block_ids=block_ids)

    # Assertions
    assert len(result) == 2
    assert result[0].name == "Block 2"
    assert result[1].name == "Block 3"

@pytest.mark.asyncio
async def test_list_all_blocks(block_service, prisma_client):
    # Invoke the service method
    async for client in prisma_client:
        result = await block_service.list_all_blocks(tx=client)
    
    print(result)
    assert result is not None or not []
