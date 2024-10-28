import os
import subprocess
import shutil

import requests
from fastapi import HTTPException
import uuid

def generate_main_py(hf_model_name, service_name):
    content = f"""import modal
from pathlib import Path

app = modal.App(name="{service_name}")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "flask", "Pillow", "torch", "torchvision", "transformers"
)

@app.function(image=image)
@modal.wsgi_app()
def flask_app():
    from flask import Flask, request

    web_app = Flask(__name__)

    from transformers import pipeline

    from io import BytesIO
    from PIL import Image as PILImage

    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Downloading and loading Model...")

    # Initialize the pipeline
    pipe = pipeline("image-classification", model="{hf_model_name}")
    logger.info("Model loaded.")

    @web_app.post("/infer")
    def infer():
        data = request.json
        images = data.get('images')
        if not images:
            return {{"error": "No images provided."}}
        
        try:
            output = pipe(images)
            return {{"ouptut": output}}
        
        except Exception as e:
            return {{"error": "Model inference failed"}}

    return web_app
"""
    with open(f"{service_name}/main.py", "w") as f:
        f.write(content)

def check_service_deployed(service_name):

    try:
        subprocess.check_output(['modal', 'app', 'history', service_name], stderr=subprocess.STDOUT)

        return True
    except subprocess.CalledProcessError as e:
        return False


def get_service_code(hf_model_name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, hf_model_name))

def deploy_model_service(hf_model_name):

    service_name = get_service_code(hf_model_name)

    if check_service_deployed(service_name):
        return {"message": f"{hf_model_name} has already been deployed.", 
            "endpoint":  f"https://wdorji--{service_name}-flask-app.modal.run/infer", "service_name": service_name}
    
    # Create the directory if it doesn't exist
    os.makedirs(service_name, exist_ok=True)
    generate_main_py(hf_model_name, service_name)

    try:
        subprocess.check_output(['modal', 'deploy', f'{service_name}/main.py'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Issue with deploying model on modal: {e.output.decode()}")

   
    #delete directory and its contents
    shutil.rmtree(service_name)
    return {"message": f"{hf_model_name} has been deployed succesfully!", 
            "endpoint":  f"https://wdorji--{service_name}-flask-app.modal.run/infer",
            "service_name": service_name}


def delete_model_service(hf_model_name):

    service_name = get_service_code(hf_model_name)

    if not check_service_deployed(service_name):
        return {"message": f"{hf_model_name} has not been deployed yet."}
    
    try:
        subprocess.check_output(['modal', 'app', 'stop', service_name], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Issue with deleting {hf_model_name} deployment: {e.output.decode()}")

    return  {"message": f"{service_name} has been deleted succesfully!"}

def post_model_inference(service_name, data):
    endpoint = f"https://wdorji--{service_name}-flask-app.modal.run/infer"
    response = requests.post(endpoint, json={"images": data["data"]})
    return response.json()
