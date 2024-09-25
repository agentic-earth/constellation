import requests
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

url = "/blocks/"

data = {
    "name": "Sample Block",
    "block_type": "dataset",
    "description": "This is a sample block for dataset.",
    # "created_by": str(uuid.UUID('123e4567-e89b-12d3-a456-426614174000')),  # Example UUID
}

response = client.post(url, json=data)

if response.status_code == 201:
    print("Block created successfully:", response.json())
else:
    print("Failed to create block:", response.status_code, response.text)
