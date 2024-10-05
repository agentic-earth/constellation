import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.taxonomy_service import TaxonomyService
from api.prisma.client import get_prisma
from api.prisma.models import PrismaTaxonomy  # Adjust the import path as necessary

@pytest.fixture
async def prisma_client():
    client = await get_prisma()
    yield client
    await client.disconnect()

@pytest.fixture
def taxonomy_service():
    return TaxonomyService()

@pytest.mark.asyncio
async def test_create_taxonomy_for_block(taxonomy_service, prisma_client):
    # Mock data
    block_id = str(uuid4())
    taxonomy = {
        "category": "Climate Data",
        "subcategory": "Temperature",
        "tags": ["weather", "environment"]
    }

    # Mock Prisma client's taxonomy.create method
    prisma_client.taxonomy.create = AsyncMock(return_value=PrismaTaxonomy(
        taxonomy_id=str(uuid4()),
        block_id=block_id,
        category=taxonomy["category"],
        subcategory=taxonomy["subcategory"],
        tags=taxonomy["tags"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ))

    # Invoke the service method
    result = await taxonomy_service.create_taxonomy_for_block(tx=prisma_client, block_id=block_id, taxonomy=taxonomy)

    # Assertions
    prisma_client.taxonomy.create.assert_called_once_with(data={
        "block_id": block_id,
        "category": taxonomy["category"],
        "subcategory": taxonomy["subcategory"],
        "tags": taxonomy["tags"]
    })
    assert result.category == taxonomy["category"]
    assert result.subcategory == taxonomy["subcategory"]
    assert result.tags == taxonomy["tags"]

@pytest.mark.asyncio
async def test_get_taxonomy_by_block_id(taxonomy_service, prisma_client):
    # Mock data
    block_id = str(uuid4())
    expected_taxonomy = PrismaTaxonomy(
        taxonomy_id=str(uuid4()),
        block_id=block_id,
        category="Climate Data",
        subcategory="Humidity",
        tags=["weather", "environment"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Mock Prisma client's taxonomy.find_unique method
    prisma_client.taxonomy.find_unique = AsyncMock(return_value=expected_taxonomy)

    # Invoke the service method
    result = await taxonomy_service.get_taxonomy_by_block_id(tx=prisma_client, block_id=block_id)

    # Assertions
    prisma_client.taxonomy.find_unique.assert_called_once_with(where={"block_id": block_id})
    assert result.category == "Climate Data"
    assert result.subcategory == "Humidity"

@pytest.mark.asyncio
async def test_update_taxonomy(taxonomy_service, prisma_client):
    # Mock data
    taxonomy_id = str(uuid4())
    update_data = {
        "subcategory": "Rainfall",
        "tags": ["weather", "precipitation"]
    }
    updated_taxonomy = PrismaTaxonomy(
        taxonomy_id=taxonomy_id,
        block_id=str(uuid4()),
        category="Climate Data",
        subcategory=update_data["subcategory"],
        tags=update_data["tags"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Mock Prisma client's taxonomy.update method
    prisma_client.taxonomy.update = AsyncMock(return_value=updated_taxonomy)

    # Invoke the service method
    result = await taxonomy_service.update_taxonomy(tx=prisma_client, taxonomy_id=taxonomy_id, update_data=update_data)

    # Assertions
    prisma_client.taxonomy.update.assert_called_once_with(
        where={"taxonomy_id": taxonomy_id},
        data=update_data
    )
    assert result.subcategory == update_data["subcategory"]
    assert result.tags == update_data["tags"]

@pytest.mark.asyncio
async def test_delete_taxonomy(taxonomy_service, prisma_client):
    # Mock data
    taxonomy_id = str(uuid4())

    # Mock Prisma client's taxonomy.delete method
    prisma_client.taxonomy.delete = AsyncMock(return_value=True)

    # Invoke the service method
    result = await taxonomy_service.delete_taxonomy(tx=prisma_client, taxonomy_id=taxonomy_id)

    # Assertions
    prisma_client.taxonomy.delete.assert_called_once_with(where={"taxonomy_id": taxonomy_id})
    assert result is True

@pytest.mark.asyncio
async def test_build_taxonomy_tree(taxonomy_service):
    # Mock data
    categories = [
        {"id": str(uuid4()), "parentId": None, "name": "Climate Data"},
        {"id": str(uuid4()), "parentId": str(uuid4()), "name": "Temperature"},
        {"id": str(uuid4()), "parentId": str(uuid4()), "name": "Humidity"}
    ]

    # Expected taxonomy tree
    expected_tree = {
        "Climate Data": {}
    }

    # Invoke the service method
    result = taxonomy_service.build_taxonomy_tree(categories=categories)

    # Assertions
    assert result == expected_tree