


import pytest
from uuid import uuid4, UUID
from fastapi.testclient import TestClient
from app.main import app
from app.schemas import EdgeCreateSchema, EdgeUpdateSchema, EdgeResponseSchema
from app.models import DependencyTypeEnum

client = TestClient(app)

@pytest.fixture(scope="module")
def test_edge_data():
    return {
        "source_block_id": str(uuid4()),
        "target_block_id": str(uuid4()),
        "dependency_type": DependencyTypeEnum.DATA.value,
        "created_by": str(uuid4())
    }

@pytest.fixture(scope="module")
def test_edge(test_edge_data):
    # Setup: Create an edge
    response = client.post("/edges/", json=test_edge_data)
    assert response.status_code == 201
    edge = response.json()
    yield edge
    # Teardown: Delete the edge
    edge_id = edge["edge_id"]
    response = client.delete(f"/edges/{edge_id}")
    assert response.status_code == 204

def test_create_edge():
    edge_data = {
        "source_block_id": str(uuid4()),
        "target_block_id": str(uuid4()),
        "dependency_type": DependencyTypeEnum.CONTROL.value,
        "created_by": str(uuid4())
    }
    response = client.post("/edges/", json=edge_data)
    assert response.status_code == 201
    data = response.json()
    assert data["source_block_id"] == edge_data["source_block_id"]
    assert data["target_block_id"] == edge_data["target_block_id"]
    # Cleanup
    edge_id = data["edge_id"]
    client.delete(f"/edges/{edge_id}")

def test_get_edge(test_edge):
    edge_id = test_edge["edge_id"]
    response = client.get(f"/edges/{edge_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["edge_id"] == edge_id

def test_update_edge(test_edge):
    edge_id = test_edge["edge_id"]
    update_data = {
        "dependency_type": DependencyTypeEnum.CONTROL.value,
    }
    response = client.put(f"/edges/{edge_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["dependency_type"] == update_data["dependency_type"]

def test_delete_edge():
    # Create an edge to delete
    edge_data = {
        "source_block_id": str(uuid4()),
        "target_block_id": str(uuid4()),
        "dependency_type": DependencyTypeEnum.DATA.value,
        "created_by": str(uuid4())
    }
    response = client.post("/edges/", json=edge_data)
    assert response.status_code == 201
    edge_id = response.json()["edge_id"]
    # Delete the edge
    response = client.delete(f"/edges/{edge_id}")
    assert response.status_code == 204
    # Verify deletion
    response = client.get(f"/edges/{edge_id}")
    assert response.status_code == 404

def test_list_edges(test_edge):
    response = client.get("/edges/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(edge["edge_id"] == test_edge["edge_id"] for edge in data)

def test_search_edges(test_edge):
    query_params = {"dependency_type": test_edge["dependency_type"]}
    response = client.get("/edges/search/", params=query_params)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["edge_id"] == test_edge["edge_id"]