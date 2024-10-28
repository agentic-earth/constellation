from fastapi import FastAPI
from modal_creator.utils import deploy_model_service, delete_model_service, post_model_inference

app = FastAPI()
services_map = {}


@app.post("/deploy")
async def deploy(model_name: str):
    output = deploy_model_service(model_name)
    services_map[model_name] = output["service_name"]
    return output


@app.post("/infer")
async def infer(model_name: str, data: dict):
    service_name = services_map[model_name]
    output = post_model_inference(service_name, data)
    return output


@app.post("/delete")
async def delete(model_name: str):
    output = delete_model_service(model_name)
    del services_map[model_name]
    return output
