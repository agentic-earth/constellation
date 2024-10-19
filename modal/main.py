import modal
from pathlib import Path
import subprocess

app = modal.App(name="modal-creator-app")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "modal", "flask"
)

# Create mounts for the Streamlit script and models
mounts = [
    modal.Mount.from_local_file(Path(__file__).parent / "utils.py",  Path("/root/utils.py")),
    modal.Mount.from_local_file(Path(__file__).parent / "config.json",  Path("/root/config.json")),
]

@app.function(image=image, mounts=mounts)
@modal.wsgi_app()
def flask_app():
    from flask import Flask, request
    from utils import deploy_model_service, delete_model_service

    web_app = Flask(__name__)
    
    @web_app.post("/deploy")
    def deploy():
        model_name = request.form.get('model_name')
        service_name = request.form.get('service_name')
        if not model_name or not service_name:
            return {"error": "Both model_name and service_name are required."}
        
        output = deploy_model_service(model_name, service_name)
        return output
    
    @web_app.post("/delete")
    def delete():
        service_name = request.form.get('service_name')
        if not service_name:
            return {"error": "service_name is required."}
        
        output = delete_model_service(service_name)
        return output

    return web_app