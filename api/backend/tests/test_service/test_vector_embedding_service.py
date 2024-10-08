import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from prisma import Prisma
from prisma.models import vector_representations as PrismaVectorRepresentation
from prisma.models import blocks as PrismaBlock

from api.backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from api.backend.app.logger import ConstellationLogger


logger = ConstellationLogger()

# Test Data
block1_id = "b1"*16
block1_data = {
    "block_id": block1_id,
    "name": "Block 1",
    "block_type": "dataset",
    "description": "Description 1",
}

vector1_id = "c1"*16
vector1_data = {
    "vector_id": vector1_id,
    "entity_type": "block",
    "entity_id": block1_id,
    "vector": [0.1] * 512,
    "taxonomy_filter": json.dumps({"category": "Climate"}),
}

test_taxonomy_filters = json.dumps({"category": "Climate"})

updated_vector = [0.2] * 512
updated_taxonomy_filters = json.dumps({"category": "Weather"})

# block2 and vector2
block2_id = "b2"*16
block2_data = {
    "block_id": block2_id,
    "name": "Block 2",
    "block_type": "dataset",
    "description": "Description 2",
}

vector2_id = "c2"*16
vector2_data = {
    "vector_id": vector2_id,
    "entity_type": "block",
    "entity_id": block2_id,
    "vector": [0.3] * 512,
    "taxonomy_filter": json.dumps({"category": "Climate"}),
}

# block3 and vector3
block3_id = "b3"*16
block3_data = {
    "block_id": block3_id,
    "name": "Block 3",
    "block_type": "dataset",
    "description": "Description 3",
}

vector3_id = "c3"*16
vector3_data = {
    "vector_id": vector3_id,
    "entity_type": "block",
    "entity_id": block3_id,
    "vector": [0.1] * 256 + [0.2] * 256,
    "taxonomy_filter": json.dumps({"category": "Climate"}),
}

# block4 and vector4
block4_id = "b4"*16
block4_data = {
    "block_id": block4_id,
    "name": "Block 4",
    "block_type": "dataset",
    "description": "Description 4",
}

vector4_id = "c4"*16
vector4_data = {
    "vector_id": vector4_id,
    "entity_type": "block",
    "entity_id": block4_id,
    "vector": [0.1] * 512,
    "taxonomy_filter": json.dumps({"category": "Climate"}),
}


@pytest.fixture
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()

    yield client
    await client.disconnect()


@pytest.fixture
def vector_embedding_service():
    return VectorEmbeddingService()


@pytest.mark.asyncio
async def test_setup(vector_embedding_service, prisma_client):
    async for client in prisma_client:
        await client.blocks.create(data=block1_data)
        await client.blocks.create(data=block2_data)
        await client.blocks.create(data=block3_data)
        await client.blocks.create(data=block4_data)

@pytest.mark.asyncio
async def test_create_vector_embedding(vector_embedding_service, prisma_client):
    logger.log("vector_embedding_service_test", "info", "Creating vector embedding", extra={"vector_data": vector1_data})
    # Invoke the service method
    async for client in prisma_client:
        created_vector = await vector_embedding_service.create_vector_embedding(client, vector1_data)
        logger.log("vector_embedding_service_test", "info", "Vector embedding created successfully.", extra={"created_vector": created_vector})

        # Assertions
        assert created_vector is not None
        assert created_vector.vector_id is not None
        assert created_vector.entity_type == vector1_data["entity_type"]
        assert created_vector.entity_id == str(UUID(block1_id))
        assert created_vector.vector == vector1_data["vector"]
        assert created_vector.taxonomy_filter == json.loads(vector1_data["taxonomy_filter"])


@pytest.mark.asyncio
async def test_get_vector_embedding(vector_embedding_service, prisma_client):
    async for client in prisma_client:
        retrieved_vector = await vector_embedding_service.get_vector_embedding(client, UUID(block1_id))

        logger.log("vector_embedding_service_test", "info", "Vector embedding retrieved successfully.", extra={"retrieved_vector": retrieved_vector})
        # Assertions
        assert retrieved_vector is not None
        assert retrieved_vector.vector_id == str(UUID(vector1_id))
        assert retrieved_vector.entity_type == "block"
        assert retrieved_vector.entity_id == str(UUID(block1_id))
        assert retrieved_vector.vector == vector1_data["vector"]
        assert retrieved_vector.taxonomy_filter == json.loads(vector1_data["taxonomy_filter"])


@pytest.mark.asyncio
async def test_update_vector_embedding(vector_embedding_service, prisma_client):
    logger.log("vector_embedding_service_test", "info", "Updating vector embedding")

    # Prepare update data
    update_vector_data = {
        "vector": updated_vector,
        "taxonomy_filter": updated_taxonomy_filters
    }

    # Invoke the service method
    async for client in prisma_client:
        updated_vector_data = await vector_embedding_service.update_vector_embedding(
            client,
            UUID(block1_id),
            update_vector_data
        )

        assert updated_vector_data is not None
        assert updated_vector_data.vector == updated_vector
        assert updated_vector_data.taxonomy_filter == json.loads(updated_taxonomy_filters)

@pytest.mark.asyncio
async def test_search_similar_vectors(vector_embedding_service, prisma_client):
    query_vector = [0.4] * 512
    
    async for client in prisma_client:
        await vector_embedding_service.create_vector_embedding(client, vector2_data)
        await vector_embedding_service.create_vector_embedding(client, vector3_data)
        await vector_embedding_service.create_vector_embedding(client, vector4_data)

        # Invoke the service method
        result = await vector_embedding_service.search_similar_blocks(tx=client, query_vector=query_vector)

        logger.log("vector_embedding_service_test", "info", "Similarity search completed.", extra={"result": result})

        # Assertions
        assert len(result) == 4
        assert result[0].entity_type == "block"

@pytest.mark.asyncio
async def test_delete_vector_embedding(vector_embedding_service, prisma_client):
    logger.log("vector_embedding_service_test", "info", "Deleting vector embedding")

    # Invoke the service method
    async for client in prisma_client:
        delete_success = await vector_embedding_service.delete_vector_embedding(client, UUID(block1_id))

    # Assertions
    assert delete_success is True