# constellation-backend/api/backend/app/features/core/routes/edges.py

"""
Edge Routes Module

This module defines all API endpoints related to edge operations, including creating, retrieving,
updating, deleting edges, and managing their versions. It leverages the EdgeController to perform
business logic and interact with the services layer. All operations are logged using the Constellation Logger.

Responsibilities:
- Define HTTP endpoints for edge-related operations.
- Validate and parse incoming request data using Pydantic schemas.
- Delegate request handling to the EdgeController.
- Handle and respond to errors appropriately.

Design Philosophy:
- Maintain thin Routes by delegating complex logic to Controllers.
- Ensure clear separation between HTTP handling and business logic.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional, Dict, Any
from uuid import UUID
from backend.app.features.core.controllers.edge_controller import EdgeController

from prisma.partials import (
    EdgeBasicInfo,
    EdgeBasicInfoWithID,
    EdgeUpdate
)

from backend.app.dependencies import get_edge_controller

router = APIRouter()

# -------------------
# Edge Endpoints
# -------------------

@router.post("/", response_model=EdgeBasicInfo, status_code=status.HTTP_201_CREATED)
async def create_edge(
    edge: EdgeBasicInfo,
    user_id: UUID,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Create a new edge.

    Args:
        edge (EdgeBasicInfo): The data required to create a new edge.
        user_id (UUID): The ID of the user performing the action.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        EdgeBasicInfo: The created edge's data.
    """
    edge_data = edge.model_dump(exclude_none=True)
    created_edge = await controller.create_edge(edge_data, user_id)
    if not created_edge:
        raise HTTPException(status_code=400, detail="Edge creation failed.")
    return created_edge

@router.get("/{edge_id}", response_model=EdgeBasicInfoWithID)
async def get_edge(
    edge_id: UUID,
    user_id: UUID,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Retrieve an edge by its UUID.

    Args:
        edge_id (UUID): The UUID of the edge to retrieve.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        EdgeBasicInfoWithID: The edge's data if found.
    """
    edge = await controller.get_edge_by_id(edge_id, user_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found.")
    return edge

@router.put("/{edge_id}", response_model=EdgeBasicInfo)
async def update_edge(
    edge_id: UUID,
    edge_update: EdgeUpdate,
    user_id: UUID,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Update an existing edge's information.

    Args:
        edge_id (UUID): The UUID of the edge to update.
        edge_update (EdgeUpdateSchema): The data to update for the edge.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        EdgeBasicInfo: The updated edge's data if successful.
    """
    edge_update_data = edge_update.model_dump(exclude_none=True)
    updated_edge = await controller.update_edge(edge_id, edge_update_data, user_id)
    if not updated_edge:
        raise HTTPException(status_code=400, detail="Edge update failed.")
    return updated_edge

@router.delete("/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    edge_id: UUID,
    user_id: UUID,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Delete an edge by its UUID.

    Args:
        edge_id (UUID): The UUID of the edge to delete.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = await controller.delete_edge(edge_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Edge deletion failed.")
    return

# @router.get("/", response_model=List[EdgeBasicInfoWithID])
# async def list_edges(
#     user_id: UUID,
#     filters: Optional[Dict[str, Any]] = Query(None, description="Filters to apply"),
#     limit: Optional[int] = Query(100, description="Maximum number of edges to retrieve"),
#     offset: Optional[int] = Query(0, description="Number of edges to skip"),
#     controller: EdgeController = Depends(get_edge_controller)
# ):
#     """
#     List edges with optional filtering by name and associated block.

#     Args:
#         filters (Optional[Dict[str, Any]]): Filters to apply.
#             Supported filters:
#                 - 'source_block_id': UUID
#                 - 'target_block_id': UUID
#                 - 'name_contains': string
#         limit (Optional[int]): Maximum number of edges to retrieve.
#         offset (Optional[int]): Number of edges to skip.
#         controller (EdgeController): The injected EdgeController instance.

#     Returns:
#         List[EdgeBasicInfoWithID]: A list of edges matching the filters.
#     """
#     edges = await controller.list_edges(filters, user_id, limit, offset)
#     return edges

# -------------------
# Complex Edge Operations Endpoints
# -------------------

# @router.post("/{edge_id}/assign-version/", status_code=status.HTTP_200_OK)
# async def assign_version(
#     edge_id: UUID,
#     version_id: UUID,
#     user_id: UUID,
#     controller: EdgeController = Depends(get_edge_controller)
# ):
#     """
#     Assign a specific version to an edge.

#     Args:
#         edge_id (UUID): The UUID of the edge.
#         version_id (UUID): The UUID of the version to assign.
#         user_id (UUID): The ID of the user performing the action.
#         controller (EdgeController): The injected EdgeController instance.

#     Returns:
#         dict: A message indicating the result of the operation.
#     """
#     try:
#         success = await controller.assign_version_to_edge(edge_id, version_id)
#         return {"message": "Version assigned to edge successfully."}
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error during version assignment.")

# -------------------
# Edge Verification Endpoint
# -------------------

# @router.post("/verify/", response_model=EdgeVerificationResponseSchema, status_code=status.HTTP_200_OK)
# async def verify_edge(
#     verification_request: EdgeVerificationRequestSchema,
#     controller: EdgeController = Depends(get_edge_controller)
# ):
#     """
#     Verify if an edge can be created between two blocks.

#     Args:
#         verification_request (EdgeVerificationRequestSchema): The source and target block IDs.
#         controller (EdgeController): The injected EdgeController instance.

#     Returns:
#         EdgeVerificationResponseSchema: The result of the verification.
#     """
#     try:
#         verification_result = await controller.verify_edge(verification_request)
#         return verification_result
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error during edge verification.")