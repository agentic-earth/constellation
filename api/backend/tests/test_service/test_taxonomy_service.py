import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4, UUID
from datetime import datetime

from api.backend.app.features.core.services.taxonomy_service import TaxonomyService
from api.backend.app.features.core.services.block_service import BlockService
from prisma.models import taxonomy_categories as PrismaTaxonomyCategory, block_taxonomies as PrismaBlockTaxonomy, blocks as PrismaBlock  # Adjust the import paths as necessary
from prisma import Prisma
from api.backend.app.logger import ConstellationLogger

logger = ConstellationLogger()

# Sample Category Data
category1_id = "1" * 32
category2_id = "2" * 32
category3_id = "3" * 32
category4_id = "4" * 32

category1_data = {
    "category_id": category1_id,
    "name": "Science",
    "parentId": None
}

category2_data = {
    "category_id": category2_id,
    "name": "Physics",
    "parentId": category1_id
}

category3_data = {
    "category_id": category3_id,
    "name": "Quantum Mechanics",
    "parentId": category2_id
}

category4_data = {
    "category_id": category4_id,
    "name": "Astrophysics",
    "parentId": category2_id
}

# Sample Block Data
block1_id = "b1" * 16
block2_id = "b2" * 16

@pytest.fixture
async def prisma_client():
    client = Prisma(datasource={'url': 'postgresql://postgres:password@localhost:5432/postgres'})
    await client.connect()

    yield client
    await client.disconnect()

@pytest.fixture
def taxonomy_service():
    return TaxonomyService()

@pytest.mark.asyncio
async def test_create_or_get_category_new(taxonomy_service, prisma_client):
    logger.log("taxonomy_service_test", "info", "Creating new category", extra={"name": category2_data["name"], "parent_id": category2_data["parentId"]})
    # Mock no existing category and creation
    async for client in prisma_client:
        result = await taxonomy_service.create_or_get_category(tx=client, category_data=category1_data)

    # Assertions
    assert result is not None

@pytest.mark.asyncio
async def test_create_or_get_category_existing(taxonomy_service, prisma_client):
    logger.log("taxonomy_service_test", "info", "Creating or getting existing category", extra={"name": category1_data["name"], "parent_id": category1_data["parentId"]})
    # Mock existing category
    async for client in prisma_client:
        result = await taxonomy_service.create_or_get_category(tx=client, category_data=category1_data)

    # Assertions
    assert result is not None

@pytest.mark.asyncio
async def test_process_taxonomy(taxonomy_service, prisma_client):
    logger.log("taxonomy_service_test", "info", "Processing taxonomy", extra={"taxonomy": {"Science": {"Physics": {"Quantum Mechanics": {}, "Astrophysics": {}}}}})
    taxonomy_input = {
        "Science": {
            "Physics": {
                "Quantum Mechanics": {},
                "Astrophysics": {}
            }
        }
    }

    async for client in prisma_client:
        result = await taxonomy_service.process_taxonomy(tx=client, taxonomy=taxonomy_input)

    # Assertions
    assert len(result) == 4

@pytest.mark.asyncio
async def test_associate_block_with_categories_success(taxonomy_service, prisma_client):
    logger.log("taxonomy_service_test", "info", "Associating block with categories", extra={"block_id": block1_id, "category_ids": [category1_id, category2_id]})
    category_ids = [category1_id]

    block1_data = {
        "block_id": block1_id,
        "name": "Block 1",
        "block_type": "dataset",
        "description": "Description 1",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    async for client in prisma_client:
        await BlockService().create_block(tx=client, block_data=block1_data)
        result = await taxonomy_service.associate_block_with_categories(tx=client, block_id=block1_id, category_ids=category_ids)

    # Assertions
    assert result is True

@pytest.mark.asyncio
async def test_create_taxonomy_for_block(taxonomy_service, prisma_client):
    logger.log("taxonomy_service_test", "info", "Creating taxonomy for block", extra={"block_id": block2_id, "taxonomy": {"Science": {"Physics": {"Quantum Mechanics": {}, "Astrophysics": {}}}}})
    taxonomy_input = {
        "general": {
            "paper_type": "Physics"
        },
        "specific": {
            "earth_observation": {},
            "weather_climate": {}
        }
    }

    block2_data = {
        "block_id": block2_id,
        "name": "Block 2",
        "block_type": "dataset",
        "description": "Description 2",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    async for client in prisma_client:
        await BlockService().create_block(tx=client, block_data=block2_data)
        result = await taxonomy_service.create_taxonomy_for_block(tx=client, block_id=block2_id, taxonomy=taxonomy_input)

    # Assertions
    assert result is True

@pytest.mark.asyncio
async def test_search_blocks_by_taxonomy(taxonomy_service, prisma_client):
    logger.log("taxonomy_service_test", "info", "Searching blocks by taxonomy", extra={"taxonomy_filters": {"Physics": "Quantum Mechanics"}})
    taxonomy_filters = {"Science": "Quantum Mechanics"}
    # Flattened filters: {"Physics": "Quantum Mechanics"}

    async for client in prisma_client:
        result = await taxonomy_service.search_blocks_by_taxonomy(tx=client, taxonomy_filters=taxonomy_filters)

    # Assertions
    assert result is not None
    assert len(result) == 1
    assert result[0].name == "Block 1"

@pytest.mark.asyncio
async def test_get_taxonomy_for_block(taxonomy_service, prisma_client):
    logger.log("taxonomy_service_test", "info", "Getting taxonomy for block", extra={"block_id": block1_id})

    expected_taxonomy = {
        "Science": {}
    }

    async for client in prisma_client:
        result = await taxonomy_service.get_taxonomy_for_block(tx=client, block_id=UUID(block1_id))

    # Assertions
    assert result == expected_taxonomy

# Additional tests can be added similarly for edge cases and failure scenarios.