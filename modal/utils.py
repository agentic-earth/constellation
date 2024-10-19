import os
import subprocess
import shutil

def generate_main_py(hf_model_name, service_name):
    content = f"""import modal
from pathlib import Path

app = modal.App(name="{service_name}")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "flask", "Pillow", "torch", "torchvision", "transformers", "boto3"
)

mounts = [
    modal.Mount.from_local_file(Path(__file__).parent / "../config.json",  Path("/root/config.json"))
]

@app.function(image=image, mounts=mounts)
@modal.wsgi_app()
def flask_app():
    from flask import Flask, request

    web_app = Flask(__name__)

    from transformers import AutoModelForImageClassification, AutoImageProcessor

    from io import BytesIO
    from PIL import Image as PILImage

    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("Downloading and loading Model...")
    processor = AutoImageProcessor.from_pretrained("{hf_model_name}")  # Updated model name
    model = AutoModelForImageClassification.from_pretrained("{hf_model_name}")  # Updated model name
    logger.info("Model loaded.")

    @web_app.post("/infer")
    def infer():
        import torch
        import boto3
        import json
        import os

        with open('config.json') as config_file:
            config = json.load(config_file)

        access_key = config["AWS_ACCESS_KEY_ID"]
        secret_key = config["AWS_SECRET_ACCESS_KEY"]
        bucket_name = config["BUCKET_NAME"]
        region = config["REGION"]

        # Read the uploaded image file
        s3_key = request.form.get('s3_key')

        s3_client = boto3.client('s3', aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region)
        
        s3_client.download_file(bucket_name, s3_key, "pre.pt")

        inputs = torch.load("pre.pt")

        os.remove("pre.pt")
        
        # Run the image through the model
        with torch.no_grad():
            outputs = model(**inputs)

        # Get the predicted class
        logits = outputs.logits

        predicted_class_idx = logits.argmax(-1).item()
        output = model.config.id2label[predicted_class_idx]

        return {{"output": output}}  

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