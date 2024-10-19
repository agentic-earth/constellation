import os
import subprocess
import shutil

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
        images = request.files.getlist('images')
        if not images:
            return {{"error": "No images provided."}}
        
        try:
            images_list = []
            for img in images:
                image = PILImage.open(BytesIO(img.read()))
                images_list.append(image)

            output = pipe(images_list)
            return {{"ouptut": output}}
        
        except Exception as e:
            return {{"error": "Model inference failed"}}

    return web_app
"""
    with open(f"{service_name}/main.py", "w") as f:
        f.write(content)


def deploy_model_service(hf_model_name, service_name):
    # Create the directory if it doesn't exist
    os.makedirs(service_name, exist_ok=True)
    generate_main_py(hf_model_name, service_name)

    try:
        subprocess.check_output(['modal', 'deploy', f'{service_name}/main.py'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return {"error": f"Issue with deploying model on modal: {e.output.decode()}"}
   
   #delete directory and its contents
    shutil.rmtree(service_name)
    return {"message": f"https://wdorji--{service_name}-flask-app.modal.run/infer"}


def delete_model_service(service_name):
    
    try:
        subprocess.check_output(['modal', 'app', 'stop', service_name], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return {"error": f"Issue with deleting {service_name} service on modal: {e.output.decode()}"}
    return  {"message": f"{service_name} service has been deleted succesfully!"}