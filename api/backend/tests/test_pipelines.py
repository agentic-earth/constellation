


import pytest
from uuid import uuid4, UUID
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas import (
    PipelineCreateSchema,
    PipelineUpdateSchema,
    PipelineResponseSchema,
    PipelineBlockCreateSchema,
    PipelineEdgeCreateSchema
)
from backend.app.models import DependencyTypeEnum, BlockTypeEnum

client = TestClient(app)

@pytest.fixture(scope="module")
def test_pipeline_data():
    return {
        "name": "Test Pipeline",
        "description": "A pipeline created for testing purposes.",
        "created_by": str(uuid4())
    }

@pytest.fixture(scope="module")
def test_pipeline(test_pipeline_data):
    # Setup: Create a pipeline
    response = client.post("/pipelines/", json=test_pipeline_data)
    assert response.status_code == 201
    pipeline = response.json()
    yield pipeline
    # Teardown: Delete the pipeline
    pipeline_id = pipeline["pipeline_id"]
    response = client.delete(f"/pipelines/{pipeline_id}")
    assert response.status_code == 204

def test_create_pipeline():
    pipeline_data = {
        "name": "Create Pipeline Test",
        "description": "Testing pipeline creation.",
        "created_by": str(uuid4())
    }
    response = client.post("/pipelines/", json=pipeline_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == pipeline_data["name"]
    # Cleanup
    pipeline_id = data["pipeline_id"]
    client.delete(f"/pipelines/{pipeline_id}")

def test_get_pipeline(test_pipeline):
    pipeline_id = test_pipeline["pipeline_id"]
    response = client.get(f"/pipelines/{pipeline_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["pipeline_id"] == pipeline_id

def test_update_pipeline(test_pipeline):
    pipeline_id = test_pipeline["pipeline_id"]
    update_data = {
        "name": "Updated Test Pipeline",
        "description": "An updated description."
    }
    response = client.put(f"/pipelines/{pipeline_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_pipeline():
    # Create a pipeline to delete
    pipeline_data = {
        "name": "Delete Pipeline Test",
        "description": "Pipeline created to test deletion.",
        "created_by": str(uuid4())
    }
    response = client.post("/pipelines/", json=pipeline_data)
    assert response.status_code == 201
    pipeline_id = response.json()["pipeline_id"]
    # Delete the pipeline
    response = client.delete(f"/pipelines/{pipeline_id}")
    assert response.status_code == 204
    # Verify deletion
    response = client.get(f"/pipelines/{pipeline_id}")
    assert response.status_code == 404

def test_list_pipelines(test_pipeline):
    response = client.get("/pipelines/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(pipeline["pipeline_id"] == test_pipeline["pipeline_id"] for pipeline in data)

def test_create_pipeline_with_dependencies():
    pipeline_data = {
        "name": "Pipeline with Dependencies",
        "description": "Testing pipeline creation with blocks and edges.",
        "created_by": str(uuid4())
    }
    blocks = [
        {
            "name": "Block 1",
            "block_type": BlockTypeEnum.DATA_SOURCE.value,
            "created_by": str(uuid4())
        },
        {
            "name": "Block 2",
            "block_type": BlockTypeEnum.PROCESSING.value,
            "created_by": str(uuid4())
        }
    ]
    edges = [
        {
            "source_block_name": "Block 1",
            "target_block_name": "Block 2",
            "dependency_type": DependencyTypeEnum.DATA.value,
            "created_by": str(uuid4())
        }
    ]
    payload = {
        "pipeline": pipeline_data,
        "blocks": blocks,
        "edges": edges
    }
    response = client.post("/pipelines/with-dependencies/", json=payload)
    assert response.status_code == 201
    data = response.json()
    pipeline_id = data["pipeline_id"]
    # Cleanup
    response = client.delete(f"/pipelines/with-dependencies/{pipeline_id}")
    assert response.status_code == 204

def test_delete_pipeline_with_dependencies():
    # Create a pipeline with dependencies to delete
    pipeline_data = {
        "name": "Pipeline to Delete with Dependencies",
        "description": "Testing deletion of pipeline with dependencies.",
        "created_by": str(uuid4())
    }
    blocks = [
        {
            "name": "Block A",
            "block_type": BlockTypeEnum.DATA_SOURCE.value,
            "created_by": str(uuid4())
        },
        {
            "name": "Block B",
            "block_type": BlockTypeEnum.DATA_SINK.value,
            "created_by": str(uuid4())
        }
    ]
    edges = [
        {
            "source_block_name": "Block A",
            "target_block_name": "Block B",
            "dependency_type": DependencyTypeEnum.DATA.value,
            "created_by": str(uuid4())
        }
    ]
    payload = {
        "pipeline": pipeline_data,
        "blocks": blocks,
        "edges": edges
    }
    # Create the pipeline with dependencies
    response = client.post("/pipelines/with-dependencies/", json=payload)
    assert response.status_code == 201
    data = response.json()
    pipeline_id = data["pipeline_id"]
    # Delete the pipeline with dependencies
    response = client.delete(f"/pipelines/with-dependencies/{pipeline_id}")
    assert response.status_code == 204
    # Verify deletion
    response = client.get(f"/pipelines/{pipeline_id}")
    assert response.status_code == 404