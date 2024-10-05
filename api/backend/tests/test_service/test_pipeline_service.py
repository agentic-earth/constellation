import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime

from api.backend.app.features.core.services.pipeline_service import PipelineService
from api.prisma.client import get_prisma
from api.prisma.models import PrismaPipeline  # Adjust the import path as necessary

@pytest.fixture
async def prisma_client():
    client = await get_prisma()
    yield client
    await client.disconnect()

@pytest.fixture
def pipeline_service():
    return PipelineService()

@pytest.mark.asyncio
async def test_create_pipeline(pipeline_service, prisma_client):
    # Mock data
    pipeline_data = {
        "pipeline_id": str(uuid4()),
        "name": "Test Pipeline",
        "description": "A pipeline for testing.",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "dagster_pipeline_config": {},
        "created_by": str(uuid4()),
        "times_run": 0,
        "average_runtime": 0.0
    }

    # Mock Prisma client's pipeline.create method
    prisma_client.pipeline.create = AsyncMock(return_value=PrismaPipeline(**pipeline_data))

    # Invoke the service method
    result = await pipeline_service.create_pipeline(tx=prisma_client, pipeline_data=pipeline_data)

    # Assertions
    prisma_client.pipeline.create.assert_called_once_with(data=pipeline_data)
    assert result.name == "Test Pipeline"
    assert result.description == "A pipeline for testing."

@pytest.mark.asyncio
async def test_get_pipeline(pipeline_service, prisma_client):
    # Mock data
    pipeline_id = str(uuid4())
    expected_pipeline = PrismaPipeline(
        pipeline_id=pipeline_id,
        name="Existing Pipeline",
        description="An existing pipeline.",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        dagster_pipeline_config={},
        created_by=str(uuid4()),
        times_run=5,
        average_runtime=12.5
    )

    # Mock Prisma client's pipeline.find_unique method
    prisma_client.pipeline.find_unique = AsyncMock(return_value=expected_pipeline)

    # Invoke the service method
    result = await pipeline_service.get_pipeline(tx=prisma_client, pipeline_id=pipeline_id)

    # Assertions
    prisma_client.pipeline.find_unique.assert_called_once_with(where={"pipeline_id": pipeline_id})
    assert result.name == "Existing Pipeline"
    assert result.times_run == 5

@pytest.mark.asyncio
async def test_update_pipeline(pipeline_service, prisma_client):
    # Mock data
    pipeline_id = str(uuid4())
    update_data = {
        "description": "Updated pipeline description.",
        "times_run": 10,
        "average_runtime": 15.0
    }
    updated_pipeline = PrismaPipeline(
        pipeline_id=pipeline_id,
        name="Updated Pipeline",
        description=update_data["description"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        dagster_pipeline_config={},
        created_by=str(uuid4()),
        times_run=update_data["times_run"],
        average_runtime=update_data["average_runtime"]
    )

    # Mock Prisma client's pipeline.update method
    prisma_client.pipeline.update = AsyncMock(return_value=updated_pipeline)

    # Invoke the service method
    result = await pipeline_service.update_pipeline(tx=prisma_client, pipeline_id=pipeline_id, update_data=update_data)

    # Assertions
    prisma_client.pipeline.update.assert_called_once_with(
        where={"pipeline_id": pipeline_id},
        data=update_data
    )
    assert result.description == update_data["description"]
    assert result.times_run == update_data["times_run"]

@pytest.mark.asyncio
async def test_delete_pipeline(pipeline_service, prisma_client):
    # Mock data
    pipeline_id = str(uuid4())

    # Mock Prisma client's pipeline.delete method
    prisma_client.pipeline.delete = AsyncMock(return_value=True)

    # Invoke the service method
    result = await pipeline_service.delete_pipeline(tx=prisma_client, pipeline_id=pipeline_id)

    # Assertions
    prisma_client.pipeline.delete.assert_called_once_with(where={"pipeline_id": pipeline_id})
    assert result is True

@pytest.mark.asyncio
async def test_list_pipelines(pipeline_service, prisma_client):
    # Mock data
    expected_pipelines = [
        PrismaPipeline(
            pipeline_id=str(uuid4()),
            name="Pipeline One",
            description="First pipeline.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            dagster_pipeline_config={},
            created_by=str(uuid4()),
            times_run=3,
            average_runtime=10.0
        ),
        PrismaPipeline(
            pipeline_id=str(uuid4()),
            name="Pipeline Two",
            description="Second pipeline.",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            dagster_pipeline_config={},
            created_by=str(uuid4()),
            times_run=7,
            average_runtime=20.0
        )
    ]

    # Mock Prisma client's pipeline.find_many method
    prisma_client.pipeline.find_many = AsyncMock(return_value=expected_pipelines)

    # Invoke the service method
    result = await pipeline_service.list_pipelines(tx=prisma_client)

    # Assertions
    prisma_client.pipeline.find_many.assert_called_once_with(where={})
    assert len(result) == 2
    assert result[0].name == "Pipeline One"
    assert result[1].name == "Pipeline Two"