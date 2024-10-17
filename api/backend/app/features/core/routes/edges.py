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
from backend.app.schemas import (
    EdgeCreateSchema,
    EdgeUpdateSchema,
    EdgeResponseSchema,
    EdgeVerificationRequestSchema,
    EdgeVerificationResponseSchema
)
from backend.app.dependencies import get_edge_controller

router = APIRouter(
    prefix="/edges",
    tags=["Edges"],
    responses={404: {"description": "Not found"}},
)

# -------------------
# Edge Endpoints
# -------------------

@router.post("/", response_model=EdgeResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_edge(
    edge: EdgeCreateSchema,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Create a new edge.

    Args:
        edge (EdgeCreateSchema): The data required to create a new edge.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        EdgeResponseSchema: The created edge's data.
    """
    try:
        created_edge = await controller.create_edge(edge)
        return created_edge
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during edge creation.")

@router.get("/{edge_id}", response_model=EdgeResponseSchema)
async def get_edge(
    edge_id: UUID,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Retrieve an edge by its UUID.

    Args:
        edge_id (UUID): The UUID of the edge to retrieve.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        EdgeResponseSchema: The edge's data if found.
    """
    try:
        edge = await controller.get_edge_by_id(edge_id)
        return edge
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during edge retrieval.")

@router.put("/{edge_id}", response_model=EdgeResponseSchema)
async def update_edge(
    edge_id: UUID,
    edge_update: EdgeUpdateSchema,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Update an existing edge's information.

    Args:
        edge_id (UUID): The UUID of the edge to update.
        edge_update (EdgeUpdateSchema): The data to update for the edge.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        EdgeResponseSchema: The updated edge's data if successful.
    """
    try:
        updated_edge = await controller.update_edge(edge_id, edge_update)
        return updated_edge
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during edge update.")

@router.delete("/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_edge(
    edge_id: UUID,
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
    try:
        await controller.delete_edge(edge_id)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during edge deletion.")
    return

@router.get("/", response_model=List[EdgeResponseSchema])
async def list_edges(
    name: Optional[str] = Query(None, description="Filter edges by name"),
    block_id: Optional[UUID] = Query(None, description="Filter edges by associated block ID"),
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    List edges with optional filtering by name and associated block.

    Args:
        name (Optional[str]): Filter edges by name.
        block_id (Optional[UUID]): Filter edges by associated block ID.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        List[EdgeResponseSchema]: A list of edges matching the filters.
    """
    try:
        filters: Dict[str, Any] = {}
        if name:
            filters["name"] = name
        if block_id:
            filters["block_id"] = str(block_id)  # Adjust based on actual schema
        edges = await controller.list_edges(filters)
        return edges
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during edge listing.")

# -------------------
# Complex Edge Operations Endpoints
# -------------------

@router.post("/{edge_id}/assign-version/", status_code=status.HTTP_200_OK)
async def assign_version(
    edge_id: UUID,
    version_id: UUID,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Assign a specific version to an edge.

    Args:
        edge_id (UUID): The UUID of the edge.
        version_id (UUID): The UUID of the version to assign.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        dict: A message indicating the result of the operation.
    """
    try:
        success = await controller.assign_version_to_edge(edge_id, version_id)
        return {"message": "Version assigned to edge successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during version assignment.")

# -------------------
# Edge Verification Endpoint
# -------------------

@router.post("/verify/", response_model=EdgeVerificationResponseSchema, status_code=status.HTTP_200_OK)
async def verify_edge(
    verification_request: EdgeVerificationRequestSchema,
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Verify if an edge can be created between two blocks.

    Args:
        verification_request (EdgeVerificationRequestSchema): The source and target block IDs.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        EdgeVerificationResponseSchema: The result of the verification.
    """
    try:
        verification_result = await controller.verify_edge(verification_request)
        return verification_result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during edge verification.")

# -------------------
# Edge Search Endpoint
# -------------------

@router.get("/search/", response_model=List[EdgeResponseSchema])
async def search_edges(
    name: Optional[str] = Query(None, description="Filter by edge name"),
    taxonomy: Optional[List[str]] = Query(None, description="Filter by taxonomy categories"),
    controller: EdgeController = Depends(get_edge_controller)
):
    """
    Search for edges based on name and taxonomy categories.

    Args:
        name (Optional[str]): Filter edges by name.
        taxonomy (Optional[List[str]]): Filter edges by taxonomy categories.
        controller (EdgeController): The injected EdgeController instance.

    Returns:
        List[EdgeResponseSchema]: A list of edges matching the search criteria.
    """
    try:
        query: Dict[str, Any] = {}
        if name:
            query["name"] = name
        if taxonomy:
            query["taxonomy"] = taxonomy  # Adjust based on actual schema
        edges = await controller.search_edges(query)
        return edges
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error during edge search.")