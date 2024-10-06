import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from api.backend.app.features.core.services.pipeline_service import PipelineService
from prisma.models import (
    pipelines as PrismaPipeline,
    pipeline_blocks as PrismaPipelineBlock,
    pipeline_edges as PrismaPipelineEdge,
    blocks as PrismaBlock,
    edges as PrismaEdge,
    users as PrismaUser
)  # Adjust the import paths as necessary
from prisma import Prisma
from api.backend.app.logger import ConstellationLogger
from api.backend.app.features.core.services.user_service import UserService
from api.backend.app.features.core.services.block_service import BlockService
from api.backend.app.features.core.services.edge_service import EdgeService

import json

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

# Sample Block Data
block1_id = "b1" * 16
block2_id = "b2" * 16
block3_id = "b3" * 16

block1_data = {
    "block_id": block1_id,
    "name": "Block 1",
    "block_type": "dataset",
    "description": "Description for Block 1",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

block2_data = {
    "block_id": block2_id,
    "name": "Block 2",
    "block_type": "model",
    "description": "Description for Block 2",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

block3_data = {
    "block_id": block3_id,
    "name": "Block 3",
    "block_type": "dataset",
    "description": "Description for Block 3",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

# Sample Edge Data (No cycles)
edge1_id = "e1" * 16
edge2_id = "e2" * 16

edge1_data = {
    "edge_id": edge1_id,
    "name": "Edge 1",
    "edge_type": "type_a",
    "description": "Description for Edge 1",
    "source_block_id": block1_id,
    "target_block_id": block2_id,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

edge2_data = {
    "edge_id": edge2_id,
    "name": "Edge 2",
    "edge_type": "type_b",
    "description": "Description for Edge 2",
    "source_block_id": block2_id,
    "target_block_id": block3_id,
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
}

# Sample Pipeline Data
pipeline1_id = "fa" * 16
pipeline1_data = {
    "pipeline_id": pipeline1_id,
    "name": "Pipeline 1",
    "created_by": user1_id,
    "description": "Description for Pipeline 1",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "times_run": 0,
    "average_runtime": 0.0,
    "dagster_pipeline_config": '{"config_key": "config_value"}',
}

pipeline2_id = "fb" * 16
pipeline2_data = {
    "pipeline_id": pipeline2_id,
    "name": "Pipeline 2",
    "created_by": user1_id,
    "description": "Description for Pipeline 2",
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow(),
    "times_run": 0,
    "average_runtime": 0.0,
    "dagster_pipeline_config": '{"config_key": "config_value"}',
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
def block_service():
    return BlockService()

@pytest.fixture(scope="module")
def edge_service():
    return EdgeService()

@pytest.fixture(scope="module")
def pipeline_service():
    return PipelineService()

@pytest.mark.asyncio
async def test_setup_pipeline_environment(prisma_client, user_service, block_service, edge_service):
    async for client in prisma_client:
        created_user = await user_service.create_user(tx=client, user_data=user1_data)
        assert created_user is not None

        created_block1 = await block_service.create_block(tx=client, block_data=block1_data)
        created_block2 = await block_service.create_block(tx=client, block_data=block2_data)
        created_block3 = await block_service.create_block(tx=client, block_data=block3_data)

        assert created_block1 is not None
        assert created_block2 is not None
        assert created_block3 is not None

        created_edge1 = await edge_service.create_edge(tx=client, edge_data=edge1_data)
        created_edge2 = await edge_service.create_edge(tx=client, edge_data=edge2_data)

        assert created_edge1 is not None
        assert created_edge2 is not None
    
    # # Cleanup (optional)
    # await client.users.delete(where={"user_id": created_user.user_id})
    # await client.blocks.delete(where={"block_id": created_block1.block_id})
    # await client.blocks.delete(where={"block_id": created_block2.block_id})
    # await client.blocks.delete(where={"block_id": created_block3.block_id})
    # await client.edges.delete(where={"edge_id": created_edge1.edge_id})
    # await client.edges.delete(where={"edge_id": created_edge2.edge_id})

@pytest.mark.asyncio
async def test_create_pipeline(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing pipeline creation")

    async for client in prisma_client:
        result = await pipeline_service.create_pipeline(tx=client, pipeline_data=pipeline1_data)

        # Assertions
        assert result is not None
        assert result.name == "Pipeline 1"
        assert result.created_by == str(UUID(user1_id))

@pytest.mark.asyncio
async def test_get_pipeline_by_id(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing get_pipeline_by_id")

    async for client in prisma_client:
        result = await pipeline_service.get_pipeline_by_id(tx=client, pipeline_id=UUID(pipeline1_id))

        # Assertions
        assert result is not None
        assert result.name == "Pipeline 1"
        assert result.pipeline_id == str(UUID(pipeline1_id))

@pytest.mark.asyncio
async def test_update_pipeline(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing update_pipeline")

    update_data = {
        "description": "Updated Description for Pipeline 1",
        "times_run": 5,
        "average_runtime": 123.45,
        "dagster_pipeline_config": '{"config_key": "new_config_value"}'
    }

    async for client in prisma_client:
        result = await pipeline_service.update_pipeline(tx=client, pipeline_id=UUID(pipeline1_id), update_data=update_data)

        # Assertions
        assert result is not None
        assert result.description == "Updated Description for Pipeline 1"
        assert result.times_run == 5
        assert result.average_runtime == 123.45
        assert result.dagster_pipeline_config == {"config_key": "new_config_value"}

@pytest.mark.asyncio
async def test_list_pipelines(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing list_pipelines")

    async for client in prisma_client:
        await pipeline_service.create_pipeline(tx=client, pipeline_data=pipeline2_data)
        result = await pipeline_service.list_pipelines(tx=client, filters={"created_by": user1_id})

        # Assertions
        assert result is not None
        assert len(result) == 2
        assert result[0].name == "Pipeline 1"
        assert result[1].name == "Pipeline 2"

@pytest.mark.asyncio
async def test_assign_block_to_pipeline(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing assign_block_to_pipeline")

    pipeline_block_data = {
        "pipeline_block_id": "bbb1" * 8,
        "block_id": block1_id,
        "pipeline_id": pipeline1_id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    async for client in prisma_client:
        result = await pipeline_service.assign_block_to_pipeline(tx=client, pipeline_block_data=pipeline_block_data)

        # Assertions
        assert result is not None
        assert result.pipeline_block_id == str(UUID(pipeline_block_data["pipeline_block_id"]))
        assert result.block_id == str(UUID(block1_id))
        assert result.pipeline_id == str(UUID(pipeline1_id))

@pytest.mark.asyncio
async def test_get_pipeline_blocks(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing get_pipeline_blocks")

    async for client in prisma_client:
        result = await pipeline_service.get_pipeline_blocks(tx=client, pipeline_id=UUID(pipeline1_id))

        # Assertions
        assert result is not None
        assert len(result) == 1
        assert result[0].pipeline_block_id == str(UUID("bbb1" * 8))
        assert result[0].block_id == str(UUID(block1_id))
        assert result[0].pipeline_id == str(UUID(pipeline1_id))

@pytest.mark.asyncio
async def test_assign_edge_to_pipeline(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing assign_edge_to_pipeline")

    pipeline_edge_data = {
        "pipeline_edge_id": "eee1" * 8,
        "pipeline_id": pipeline1_id,
        "edge_id": edge1_id,
        "source_block_id": edge1_data["source_block_id"],
        "target_block_id": edge1_data["target_block_id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    async for client in prisma_client:
        result = await pipeline_service.assign_edge_to_pipeline(tx=client, pipeline_edge_data=pipeline_edge_data)

        # Assertions
        assert result is not None
        assert result.pipeline_edge_id == str(UUID(pipeline_edge_data["pipeline_edge_id"]))
        assert result.edge_id == str(UUID(edge1_id))
        assert result.pipeline_id == str(UUID(pipeline1_id))

@pytest.mark.asyncio
async def test_get_pipeline_edges(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing get_pipeline_edges")

    async for client in prisma_client:
        result = await pipeline_service.get_pipeline_edges(tx=client, pipeline_id=UUID(pipeline1_id))

        # Assertions
        assert result is not None
        assert len(result) == 1
        assert result[0].pipeline_edge_id == str(UUID("eee1" * 8))
        assert result[0].edge_id == str(UUID(edge1_id))
        assert result[0].pipeline_id == str(UUID(pipeline1_id))

@pytest.mark.asyncio
async def test_increment_pipeline_run(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing increment_pipeline_run")

    latest_runtime = 200.5

    async for client in prisma_client:
        result = await pipeline_service.increment_pipeline_run(tx=client, pipeline_id=UUID(pipeline1_id), latest_runtime=latest_runtime)

        # Assertions
        assert result is True

@pytest.mark.asyncio
async def test_remove_block_from_pipeline(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing remove_block_from_pipeline")

    async for client in prisma_client:
        result = await pipeline_service.remove_block_from_pipeline(tx=client, pipeline_block_id=UUID("bbb1" * 8))

        # Assertions
        assert result is True

@pytest.mark.asyncio
async def test_remove_edge_from_pipeline(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing remove_edge_from_pipeline")

    async for client in prisma_client:
        result = await pipeline_service.remove_edge_from_pipeline(tx=client, pipeline_edge_id=UUID("eee1" * 8))

        # Assertions
        assert result is True

@pytest.mark.asyncio
async def test_delete_pipeline(pipeline_service, prisma_client):
    logger.log("pipeline_service_test", "info", "Testing delete_pipeline")

    async for client in prisma_client:
        result = await pipeline_service.delete_pipeline(tx=client, pipeline_id=UUID(pipeline1_id))

        # Assertions
        assert result is True