# app/routes/pipelines.py

"""
Pipeline Routes Module

This module defines all API endpoints related to pipeline operations, such as creating, retrieving,
updating, deleting pipelines, and managing their associated blocks and edges. It leverages the
PipelineController to perform business logic and interact with the services layer. All operations are
logged using the Constellation Logger.

Responsibilities:
- Define HTTP endpoints for pipeline-related operations.
- Validate and parse incoming request data using Pydantic schemas.
- Delegate request handling to the PipelineController.
- Handle and respond to errors appropriately.

Design Philosophy:
- Maintain thin Routes by delegating complex logic to Controllers.
- Ensure clear separation between HTTP handling and business logic.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
# from app.controllers.pipeline_controller import PipelineController
from app.features.core.controllers.pipeline_controller import PipelineController
from app.schemas import (
    PipelineCreateSchema,
    PipelineUpdateSchema,
    PipelineResponseSchema,
    PipelineBlockCreateSchema,
    PipelineEdgeCreateSchema,
    PipelineBlockResponseSchema,
    PipelineEdgeResponseSchema
)

router = APIRouter(
    prefix="/pipelines",
    tags=["Pipelines"],
    responses={404: {"description": "Not found"}},
)

# Initialize the PipelineController instance
pipeline_controller = PipelineController()

# -------------------
# Basic Pipeline Endpoints
# -------------------

@router.post("/", response_model=PipelineResponseSchema, status_code=201)
def create_pipeline(pipeline: PipelineCreateSchema):
    """
    Create a new pipeline.

    Args:
        pipeline (PipelineCreateSchema): The data required to create a new pipeline.

    Returns:
        PipelineResponseSchema: The created pipeline's data.
    """
    created_pipeline = pipeline_controller.create_pipeline(pipeline)
    if not created_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline creation failed.")
    return created_pipeline

@router.get("/{pipeline_id}", response_model=PipelineResponseSchema)
def get_pipeline(pipeline_id: UUID):
    """
    Retrieve a pipeline by its UUID.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to retrieve.

    Returns:
        PipelineResponseSchema: The pipeline's data if found.
    """
    pipeline = pipeline_controller.get_pipeline_by_id(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found.")
    return pipeline

@router.put("/{pipeline_id}", response_model=PipelineResponseSchema)
def update_pipeline(pipeline_id: UUID, pipeline_update: PipelineUpdateSchema):
    """
    Update an existing pipeline's information.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to update.
        pipeline_update (PipelineUpdateSchema): The data to update for the pipeline.

    Returns:
        PipelineResponseSchema: The updated pipeline's data if successful.
    """
    updated_pipeline = pipeline_controller.update_pipeline(pipeline_id, pipeline_update)
    if not updated_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline update failed.")
    return updated_pipeline

@router.delete("/{pipeline_id}", status_code=204)
def delete_pipeline(pipeline_id: UUID):
    """
    Delete a pipeline by its UUID.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = pipeline_controller.delete_pipeline(pipeline_id)
    if not success:
        raise HTTPException(status_code=404, detail="Pipeline not found or already deleted.")
    return

@router.get("/", response_model=List[PipelineResponseSchema])
def list_pipelines(name: Optional[str] = None, created_by: Optional[UUID] = None):
    """
    List pipelines with optional filtering by name and creator.

    Args:
        name (Optional[str]): Filter pipelines by name.
        created_by (Optional[UUID]): Filter pipelines by the creator's UUID.

    Returns:
        List[PipelineResponseSchema]: A list of pipelines matching the filters.
    """
    filters = {}
    if name:
        filters["name"] = name
    if created_by:
        filters["created_by"] = str(created_by)
    pipelines = pipeline_controller.list_pipelines(filters)
    if pipelines is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve pipelines.")
    return pipelines

# -------------------
# Complex Pipeline Operations Endpoints
# -------------------

@router.post("/with-dependencies/", response_model=PipelineResponseSchema, status_code=201)
def create_pipeline_with_dependencies(
    pipeline: PipelineCreateSchema,
    blocks: List[PipelineBlockCreateSchema] = [],
    edges: List[PipelineEdgeCreateSchema] = []
):
    """
    Create a new pipeline along with its associated blocks and edges.

    Args:
        pipeline (PipelineCreateSchema): The data required to create a new pipeline.
        blocks (List[PipelineBlockCreateSchema]): A list of blocks to assign to the pipeline.
        edges (List[PipelineEdgeCreateSchema]): A list of edges to assign to the pipeline.

    Returns:
        PipelineResponseSchema: The created pipeline's data with dependencies.
    """
    created_pipeline = pipeline_controller.create_pipeline_with_dependencies(pipeline, blocks, edges)
    if not created_pipeline:
        raise HTTPException(status_code=400, detail="Failed to create pipeline with dependencies.")
    return created_pipeline

@router.delete("/with-dependencies/{pipeline_id}", status_code=204)
def delete_pipeline_with_dependencies(pipeline_id: UUID):
    """
    Delete a pipeline along with all its associated blocks and edges.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = pipeline_controller.delete_pipeline_with_dependencies(pipeline_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete pipeline with dependencies.")
    return
