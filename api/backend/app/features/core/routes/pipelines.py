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

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from backend.app.features.core.controllers.pipeline_controller import PipelineController

from prisma.partials import (
    PipelineBasicInfo,
    PipelineBasicInfoWithID,
    BlockBasicInfo,
    EdgeBasicInfo,
)

from backend.app.dependencies import get_pipeline_controller

router = APIRouter()

# -------------------
# Basic Pipeline Endpoints
# -------------------


@router.post("/", response_model=PipelineBasicInfo, status_code=201)
async def create_pipeline(
    pipeline: PipelineBasicInfo,
    user_id: UUID,
    controller: PipelineController = Depends(get_pipeline_controller)
):
    """
    Create a new pipeline.

    Args:
        pipeline (PipelineBasicInfo): The data required to create a new pipeline.
        user_id (UUID): The UUID of the user creating the pipeline.

    Returns:
        PipelineBasicInfo: The created pipeline's data.
    """
    pipeline_data = pipeline.model_dump(exclude_none=True)  
    created_pipeline = await controller.create_pipeline(pipeline_data, user_id)
    if not created_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline creation failed.")
    return created_pipeline


@router.get("/{pipeline_id}", response_model=PipelineBasicInfoWithID)
async def get_pipeline(
    pipeline_id: UUID,
    user_id: UUID,
    controller: PipelineController = Depends(get_pipeline_controller)
):
    """
    Retrieve a pipeline by its UUID.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to retrieve.

    Returns:
        PipelineBasicInfoWithID: The pipeline's data if found.
    """
    pipeline = await controller.get_pipeline_by_id(pipeline_id, user_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found.")
    return pipeline


@router.put("/{pipeline_id}", response_model=PipelineBasicInfo)
async def update_pipeline(
    pipeline_id: UUID,
    pipeline_update: PipelineBasicInfo,
    user_id: UUID,
    controller: PipelineController = Depends(get_pipeline_controller)
):
    """
    Update an existing pipeline's information.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to update.
        pipeline_update (PipelineUpdateSchema): The data to update for the pipeline.

    Returns:
        PipelineResponseSchema: The updated pipeline's data if successful.
    """
    pipeline_update_data = pipeline_update.model_dump(exclude_none=True)
    updated_pipeline = await controller.update_pipeline(pipeline_id, pipeline_update_data, user_id)
    if not updated_pipeline:
        raise HTTPException(status_code=400, detail="Pipeline update failed.")
    return updated_pipeline


@router.delete("/{pipeline_id}", status_code=204)
async def delete_pipeline(
    pipeline_id: UUID,
    user_id: UUID,
    controller: PipelineController = Depends(get_pipeline_controller)
):
    """
    Delete a pipeline by its UUID.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = await controller.delete_pipeline(pipeline_id, user_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Pipeline not found or already deleted."
        )
    return


@router.get("/", response_model=List[PipelineBasicInfoWithID])
async def list_pipelines(
    user_id: UUID,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 10,
    offset: int = 0,
    controller: PipelineController = Depends(get_pipeline_controller)
):
    """
    List pipelines by filters.

    Args:
        filters (Optional[Dict[str, Any]]): Key-value pairs to filter the pipelines.
            Supported filters: 'name', 'user_id'.
        user_id (Optional[UUID]): Filter pipelines by the user's UUID.

    Returns:
        List[PipelineBasicInfoWithID]: A list of pipelines matching the filters.
    """
    pipelines = await controller.list_pipelines(user_id, filters, limit, offset)
    if pipelines is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve pipelines.")
    return pipelines


# -------------------
# Complex Pipeline Operations Endpoints
# -------------------


@router.post("/with-dependencies/", response_model=PipelineBasicInfo, status_code=201)
async def create_pipeline_with_dependencies(
    pipeline: PipelineBasicInfo,
    user_id: UUID,
    blocks: List[BlockBasicInfo] = [],
    edges: List[EdgeBasicInfo] = [],
    controller: PipelineController = Depends(get_pipeline_controller)
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
    pipeline_data = pipeline.model_dump(exclude_none=True)
    blocks_data = [block.model_dump(exclude_none=True) for block in blocks]
    edges_data = [edge.model_dump(exclude_none=True) for edge in edges]
    
    created_pipeline = await controller.create_pipeline_with_dependencies(
        pipeline_data, blocks_data, edges_data, user_id
    )
    if not created_pipeline:
        raise HTTPException(
            status_code=400, detail="Failed to create pipeline with dependencies."
        )
    return created_pipeline


@router.delete("/with-dependencies/{pipeline_id}", status_code=204)
async def delete_pipeline_with_dependencies(
    pipeline_id: UUID,
    user_id: UUID,
    controller: PipelineController = Depends(get_pipeline_controller)
):
    """
    Delete a pipeline along with all its associated blocks and edges.

    Args:
        pipeline_id (UUID): The UUID of the pipeline to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = await controller.delete_pipeline_with_dependencies(pipeline_id, user_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to delete pipeline with dependencies."
        )
    return

@router.post("/verify/{pipeline_id}", status_code=200)
async def verify_pipeline(
    pipeline_id: UUID,
    user_id: UUID,
    controller: PipelineController = Depends(get_pipeline_controller)
):
    verified = await controller.verify_pipeline(pipeline_id, user_id)
    if not verified:
        raise HTTPException(status_code=400, detail="Pipeline verification failed.")
    return {"message": "Pipeline verified successfully."}