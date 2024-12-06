import subprocess
import pytest
from fastapi.testclient import TestClient

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

os.chdir("..")

from modal_creator.app.main import app
from modal_creator.assets.utils import get_service_code, convert_image_to_base64


client = TestClient(app)

VALID_MODEL_NAME = "EdBianchi/vit-fire-detection"
INVALID_MODEL_NAME = "dummy_model"


def test_deploy():

    service_name = get_service_code(VALID_MODEL_NAME)
    subprocess.run(["modal", "app", "stop", service_name])

    response = client.get("/deploy?model_name=" + VALID_MODEL_NAME)

    assert response.status_code == 200
    assert response.json() == {
        "message": f"{VALID_MODEL_NAME} has been deployed succesfully!",
        "endpoint": f"https://wdorji--{service_name}-flask-app.modal.run/infer",
        "service_name": service_name,
    }

    response = client.get("/deploy?model_name=" + VALID_MODEL_NAME)

    assert response.status_code == 200
    assert response.json() == {
        "message": f"{VALID_MODEL_NAME} has already been deployed.",
        "endpoint": f"https://wdorji--{service_name}-flask-app.modal.run/infer",
        "service_name": service_name,
    }

    response = client.get("/deploy?model_name=" + INVALID_MODEL_NAME)

    assert response.status_code == 500
    assert response.json() == {"detail": "Issue with deploying model on modal"}

    subprocess.run(["modal", "app", "stop", service_name])


def test_infer():

    response = client.post(
        "/infer?model_name=" + VALID_MODEL_NAME,
        json={"data": [convert_image_to_base64("modal_creator/assets/forest.jpg")]},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": f"{VALID_MODEL_NAME} has not been deployed yet."
    }

    service_name = get_service_code(VALID_MODEL_NAME)
    subprocess.run(["modal", "app", "stop", service_name])

    client.get("/deploy?model_name=" + VALID_MODEL_NAME)

    response = client.post(
        "/infer?model_name=" + VALID_MODEL_NAME,
        json={"data": [convert_image_to_base64("modal_creator/assets/forest.jpg")]},
    )
    assert response.status_code == 200
    assert (
        max(response.json()["output"][0], key=lambda x: x["score"])["label"] == "Normal"
    )

    response = client.post("/infer?model_name=" + VALID_MODEL_NAME, json={"data": []})
    assert response.status_code == 200
    assert response.json() == {"output": "No images provided."}

    subprocess.run(["modal", "app", "stop", service_name])


def test_delete():

    response = client.delete("/delete?model_name=" + VALID_MODEL_NAME)
    assert response.status_code == 200
    assert response.json() == {
        "message": f"{VALID_MODEL_NAME} has not been deployed yet."
    }

    service_name = get_service_code(VALID_MODEL_NAME)
    subprocess.run(["modal", "app", "stop", service_name])

    client.get("/deploy?model_name=" + VALID_MODEL_NAME)

    response = client.delete("/delete?model_name=" + VALID_MODEL_NAME)
    assert response.status_code == 200
    assert response.json() == {
        "message": f"{VALID_MODEL_NAME} has been deleted succesfully!"
    }
