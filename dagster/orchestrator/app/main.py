from fastapi import FastAPI
from pydantic import BaseModel
from dagster import (
    asset,
    define_asset_job,
    repository,
)
from dagster import DagsterInstance

app = FastAPI()
