from fastapi import FastAPI
from modal_creator.utils import deploy_model_service, delete_model_service

app = FastAPI()


@app.post("/deploy")
async def deploy(model_name: str):
    output = deploy_model_service(model_name)
    return output


@app.post("/delete")
async def delete(model_name: str):
    output = delete_model_service(model_name)
    return output
