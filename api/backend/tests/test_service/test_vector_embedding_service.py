import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from api.prisma.client import get_prisma
from api.prisma.models import PrismaVectorEmbedding  # Adjust the import path as necessary

@pytest.fixture
async def prisma_client():
    client = await get_prisma()
    yield client
    await client.disconnect()

@pytest.fixture
def vector_embedding_service():
    return VectorEmbeddingService()

@pytest.mark.asyncio
async def test_create_vector_embedding(vector_embedding_service, prisma_client):
    # Mock data
    embedding_data = {
        "vector_embedding_id": str(uuid4()),
        "entity_type": "block",
        "entity_id": str(uuid4()),
        "vector": [0.1, 0.2, 0.3],
        "taxonomy_filter": {"category": "Climate Data"},
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Mock Prisma client's vector_embedding.create method
    prisma_client.vector_embedding.create = AsyncMock(return_value=PrismaVectorEmbedding(**embedding_data))

    # Invoke the service method
    result = await vector_embedding_service.create_vector_embedding(tx=prisma_client, embedding_data=embedding_data)

    # Assertions
    prisma_client.vector_embedding.create.assert_called_once_with(data=embedding_data)
    assert result.entity_type == "block"
    assert result.vector == [0.1, 0.2, 0.3]

@pytest.mark.asyncio
async def test_get_vector_embedding_by_id(vector_embedding_service, prisma_client):
    # Mock data
    embedding_id = str(uuid4())
    expected_embedding = PrismaVectorEmbedding(
        vector_embedding_id=embedding_id,
        entity_type="block",
        entity_id=str(uuid4()),
        vector=[0.1, 0.2, 0.3],
        taxonomy_filter={"category": "Climate Data"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Mock Prisma client's vector_embedding.find_unique method
    prisma_client.vector_embedding.find_unique = AsyncMock(return_value=expected_embedding)

    # Invoke the service method
    result = await vector_embedding_service.get_vector_embedding_by_id(tx=prisma_client, embedding_id=embedding_id)

    # Assertions
    prisma_client.vector_embedding.find_unique.assert_called_once_with(where={"vector_embedding_id": embedding_id})
    assert result.entity_type == "block"
    assert result.vector == [0.1, 0.2, 0.3]

@pytest.mark.asyncio
async def test_update_vector_embedding(vector_embedding_service, prisma_client):
    # Mock data
    embedding_id = str(uuid4())
    update_data = {
        "vector": [0.4, 0.5, 0.6],
        "taxonomy_filter": {"category": "Updated Climate Data"}
    }
    updated_embedding = PrismaVectorEmbedding(
        vector_embedding_id=embedding_id,
        entity_type="block",
        entity_id=str(uuid4()),
        vector=update_data["vector"],
        taxonomy_filter=update_data["taxonomy_filter"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Mock Prisma client's vector_embedding.update method
    prisma_client.vector_embedding.update = AsyncMock(return_value=updated_embedding)

    # Invoke the service method
    result = await vector_embedding_service.update_vector_embedding(tx=prisma_client, embedding_id=embedding_id, update_data=update_data)

    # Assertions
    prisma_client.vector_embedding.update.assert_called_once_with(
        where={"vector_embedding_id": embedding_id},
        data=update_data
    )
    assert result.vector == update_data["vector"]
    assert result.taxonomy_filter == update_data["taxonomy_filter"]

@pytest.mark.asyncio
async def test_delete_vector_embedding(vector_embedding_service, prisma_client):
    # Mock data
    embedding_id = str(uuid4())

    # Mock Prisma client's vector_embedding.delete method
    prisma_client.vector_embedding.delete = AsyncMock(return_value=True)

    # Invoke the service method
    result = await vector_embedding_service.delete_vector_embedding(tx=prisma_client, embedding_id=embedding_id)

    # Assertions
    prisma_client.vector_embedding.delete.assert_called_once_with(where={"vector_embedding_id": embedding_id})
    assert result is True

@pytest.mark.asyncio
async def test_search_similar_vectors(vector_embedding_service, prisma_client):
    # Mock data
    query_text = "Sample query"
    taxonomy_filters = {"category": "Climate Data"}
    top_k = 3
    expected_results = [
        PrismaVectorEmbedding(
            vector_embedding_id=str(uuid4()),
            entity_type="block",
            entity_id=str(uuid4()),
            vector=[0.1, 0.2, 0.3],
            taxonomy_filter=taxonomy_filters,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]

    # Mock Prisma client's vector_embedding.find_many method
    prisma_client.vector_embedding.find_many = AsyncMock(return_value=expected_results)

    # Invoke the service method
    result = await vector_embedding_service.search_similar_vectors(tx=prisma_client, query_text=query_text, taxonomy_filters=taxonomy_filters, top_k=top_k)

    # Assertions
    prisma_client.vector_embedding.find_many.assert_called_once()
    assert len(result) == 1
    assert result[0].entity_type == "block"
    assert result[0].taxonomy_filter == taxonomy_filters