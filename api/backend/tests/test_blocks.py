


import pytest
from uuid import uuid4, UUID
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas import BlockCreateSchema, BlockUpdateSchema, BlockResponseSchema
from backend.app.models import BlockTypeEnum

client = TestClient(app)

@pytest.fixture(scope="module")
def test_block_data():
    return {
        "name": "Test Block",
        "block_type": BlockTypeEnum.model,
        "created_by": str(uuid4())
    }

@pytest.fixture(scope="module")
def test_block(test_block_data):
    # Setup: Create a block
    response = client.post("/blocks/", json=test_block_data)
    assert response.status_code == 201
    block = response.json()
    yield block
    # Teardown: Delete the block
    block_id = block["block_id"]
    response = client.delete(f"/blocks/{block_id}")
    assert response.status_code == 204

def test_create_block():
    block_data = {
        "name": "Create Block Test",
        "block_type": BlockTypeEnum.dataset,
        "created_by": str(uuid4())
    }
    response = client.post("/blocks/", json=block_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == block_data["name"]
    assert data["block_type"] == block_data["block_type"]
    # Cleanup
    block_id = data["block_id"]
    client.delete(f"/blocks/{block_id}")

def test_get_block(test_block):
    block_id = test_block["block_id"]
    response = client.get(f"/blocks/{block_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["block_id"] == block_id

def test_update_block(test_block):
    block_id = test_block["block_id"]
    update_data = {
        "name": "Updated Test Block",
        "block_type": BlockTypeEnum.DATA_SINK.value
    }
    response = client.put(f"/blocks/{block_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["block_type"] == update_data["block_type"]

def test_delete_block():
    # Create a block to delete
    block_data = {
        "name": "Delete Block Test",
        "block_type": BlockTypeEnum.DATA_SINK.value,
        "created_by": str(uuid4())
    }
    response = client.post("/blocks/", json=block_data)
    assert response.status_code == 201
    block_id = response.json()["block_id"]
    # Delete the block
    response = client.delete(f"/blocks/{block_id}")
    assert response.status_code == 204
    # Verify deletion
    response = client.get(f"/blocks/{block_id}")
    assert response.status_code == 404

def test_list_blocks(test_block):
    response = client.get("/blocks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(block["block_id"] == test_block["block_id"] for block in data)

def test_search_blocks(test_block):
    query_params = {"name": test_block["name"]}
    response = client.get("/blocks/search/", params=query_params)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["name"] == test_block["name"]