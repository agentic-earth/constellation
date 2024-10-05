import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.block_service import BlockService
from api.prisma.client import get_prisma
from api.prisma.models import PrismaBlock  # Adjust the import path as necessary

@pytest.fixture
async def prisma_client():
    client = await get_prisma()
    yield client
    await client.disconnect()

@pytest.fixture
def block_service():
    return BlockService()

@pytest.mark.asyncio
async def test_create_block(block_service, prisma_client):
    # Mock data
    block_data = {
        "block_id": str(uuid4()),
        "name": "Test Block",
        "block_type": "dataset",
        "description": "A block for testing.",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "current_version_id": str(uuid4()),
        "created_by": str(uuid4()),
        "taxonomy": None,
        "metadata": None,
        "vector_embedding": None
    }

    # Mock Prisma client's block.create method
    prisma_client.block.create = AsyncMock(return_value=PrismaBlock(**block_data))

    # Invoke the service method
    result = await block_service.create_block(tx=prisma_client, block_data=block_data)

    # Assertions
    prisma_client.block.create.assert_called_once_with(data=block_data)
    assert result.name == "Test Block"
    assert result.block_type == "dataset"

@pytest.mark.asyncio
async def test_get_block_by_id(block_service, prisma_client):
    # Mock data
    block_id = str(uuid4())
    expected_block = PrismaBlock(
        block_id=block_id,
        name="Existing Block",
        block_type="model",
        description="An existing block.",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        current_version_id=str(uuid4()),
        created_by=str(uuid4()),
        taxonomy=None,
        metadata=None,
        vector_embedding=None
    )

    # Mock Prisma client's block.find_unique method
    prisma_client.block.find_unique = AsyncMock(return_value=expected_block)

    # Invoke the service method
    result = await block_service.get_block_by_id(tx=prisma_client, block_id=block_id)

    # Assertions
    prisma_client.block.find_unique.assert_called_once_with(where={"block_id": block_id})
    assert result.name == "Existing Block"
    assert result.block_type == "model"

@pytest.mark.asyncio
async def test_update_block(block_service, prisma_client):
    # Mock data
    block_id = str(uuid4())
    update_data = {
        "name": "Updated Block",
        "block_type": "model",
        "description": "Updated description.",
        "taxonomy": {"category": "Updated Category"},
        "metadata": {"key": "value"},
        "updated_at": datetime.utcnow()
    }
    updated_block = PrismaBlock(
        block_id=block_id,
        name=update_data["name"],
        block_type=update_data["block_type"],
        description=update_data["description"],
        created_at=datetime.utcnow(),
        updated_at=update_data["updated_at"],
        current_version_id=str(uuid4()),
        created_by=str(uuid4()),
        taxonomy=update_data["taxonomy"],
        metadata=update_data["metadata"],
        vector_embedding=None
    )

    # Mock Prisma client's block.update method
    prisma_client.block.update = AsyncMock(return_value=updated_block)

    # Invoke the service method
    result = await block_service.update_block(tx=prisma_client, block_id=block_id, update_data=update_data)

    # Assertions
    prisma_client.block.update.assert_called_once_with(
        where={"block_id": block_id},
        data=update_data
    )
    assert result.name == update_data["name"]
    assert result.description == update_data["description"]
    assert result.taxonomy == update_data["taxonomy"]

@pytest.mark.asyncio
async def test_delete_block(block_service, prisma_client):
    # Mock data
    block_id = str(uuid4())

    # Mock Prisma client's block.delete method
    prisma_client.block.delete = AsyncMock(return_value=True)

    # Invoke the service method
    result = await block_service.delete_block(tx=prisma_client, block_id=block_id)

    # Assertions
    prisma_client.block.delete.assert_called_once_with(where={"block_id": block_id})
    assert result is True

@pytest.mark.asyncio
async def test_get_blocks_by_ids(block_service, prisma_client):
    # Mock data
    block_ids = [str(uuid4()), str(uuid4())]
    expected_blocks = [
        PrismaBlock(
            block_id=block_ids[0],
            name="Block One",
            block_type="dataset",
            description="First block.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            current_version_id=str(uuid4()),
            created_by=str(uuid4()),
            taxonomy=None,
            metadata=None,
            vector_embedding=None
        ),
        PrismaBlock(
            block_id=block_ids[1],
            name="Block Two",
            block_type="model",
            description="Second block.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            current_version_id=str(uuid4()),
            created_by=str(uuid4()),
            taxonomy=None,
            metadata=None,
            vector_embedding=None
        )
    ]

    # Mock Prisma client's block.find_many method
    prisma_client.block.find_many = AsyncMock(return_value=expected_blocks)

    # Invoke the service method
    result = await block_service.get_blocks_by_ids(tx=prisma_client, block_ids=block_ids)

    # Assertions
    prisma_client.block.find_many.assert_called_once_with(where={"block_id": {"in": block_ids}})
    assert len(result) == 2
    assert result[0].name == "Block One"
    assert result[1].name == "Block Two"