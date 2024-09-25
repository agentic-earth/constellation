from fastapi import FastAPI
from pydantic import BaseModel
from dagster import (
    asset,
    define_asset_job,
    repository,
)

app = FastAPI()


# Example schema to define how clients send asset data
class AssetData(BaseModel):
    name: str
    value: str


# Store for dynamic assets and pipelines
dynamic_assets = {}


# Route to dynamically create assets and pipelines
@app.post("/create_pipeline")
def create_pipeline(asset_data: AssetData):
    # Define asset dynamically based on input
    @asset(name=asset_data.name)
    def dynamic_asset():
        return asset_data.value

    # Store the dynamic asset
    dynamic_assets[asset_data.name] = dynamic_asset

    # Define a job that uses the dynamically created asset
    asset_job = define_asset_job(f"{asset_data.name}_job", selection=[dynamic_asset])

    return {"message": f"Pipeline for asset {asset_data.name} created!"}


# Optionally, create a repository to register all assets
@repository
def my_repository():
    return list(dynamic_assets.values())


@app.post("/run_pipeline")
def run_pipeline(asset_name: str):
    asset = dynamic_assets.get(asset_name)
    if not asset:
        return {"error": f"No asset found for {asset_name}"}

    asset_job = define_asset_job(f"{asset_name}_job", selection=[asset])

    # Execute the asset job
    result = execute_pipeline(asset_job)

    if result.success:
        return {"message": f"Pipeline {asset_name} executed successfully!"}
    else:
        return {"error": f"Pipeline {asset_name} execution failed!"}
