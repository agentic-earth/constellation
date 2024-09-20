# app/routes/edges.py

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

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
from app.controllers.edge_controller import EdgeController
from app.schemas import (
    EdgeCreateSchema,
    EdgeUpdateSchema,
    EdgeResponseSchema
)

router = APIRouter(
    prefix="/edges",
    tags=["Edges"],
    responses={404: {"description": "Not found"}},
)

# Initialize the EdgeController instance
edge_controller = EdgeController()

# -------------------
# Basic Edge Endpoints
# -------------------

@router.post("/", response_model=EdgeResponseSchema, status_code=201)
def create_edge(edge: EdgeCreateSchema):
    """
    Create a new edge.

    Args:
        edge (EdgeCreateSchema): The data required to create a new edge.

    Returns:
        EdgeResponseSchema: The created edge's data.
    """
    created_edge = edge_controller.create_edge(edge)
    if not created_edge:
        raise HTTPException(status_code=400, detail="Edge creation failed.")
    return created_edge

@router.get("/{edge_id}", response_model=EdgeResponseSchema)
def get_edge(edge_id: UUID):
    """
    Retrieve an edge by its UUID.

    Args:
        edge_id (UUID): The UUID of the edge to retrieve.

    Returns:
        EdgeResponseSchema: The edge's data if found.
    """
    edge = edge_controller.get_edge_by_id(edge_id)
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found.")
    return edge

@router.put("/{edge_id}", response_model=EdgeResponseSchema)
def update_edge(edge_id: UUID, edge_update: EdgeUpdateSchema):
    """
    Update an existing edge's information.

    Args:
        edge_id (UUID): The UUID of the edge to update.
        edge_update (EdgeUpdateSchema): The data to update for the edge.

    Returns:
        EdgeResponseSchema: The updated edge's data if successful.
    """
    updated_edge = edge_controller.update_edge(edge_id, edge_update)
    if not updated_edge:
        raise HTTPException(status_code=400, detail="Edge update failed.")
    return updated_edge

@router.delete("/{edge_id}", status_code=204)
def delete_edge(edge_id: UUID):
    """
    Delete an edge by its UUID.

    Args:
        edge_id (UUID): The UUID of the edge to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = edge_controller.delete_edge(edge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Edge not found or already deleted.")
    return

@router.get("/", response_model=List[EdgeResponseSchema])
def list_edges(name: Optional[str] = None, block_id: Optional[UUID] = None):
    """
    List edges with optional filtering by name and associated block.

    Args:
        name (Optional[str]): Filter edges by name.
        block_id (Optional[UUID]): Filter edges by associated block ID.

    Returns:
        List[EdgeResponseSchema]: A list of edges matching the filters.
    """
    filters = {}
    if name:
        filters["name"] = name
    if block_id:
        filters["block_id"] = str(block_id)  # Assuming edges have a 'block_id' field
    edges = edge_controller.list_edges(filters)
    if edges is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve edges.")
    return edges

# -------------------
# Complex Edge Operations Endpoints
# -------------------

@router.post("/{edge_id}/assign-version/", status_code=200)
def assign_version(edge_id: UUID, version_id: UUID):
    """
    Assign a specific version to an edge.

    Args:
        edge_id (UUID): The UUID of the edge.
        version_id (UUID): The UUID of the version to assign.

    Returns:
        dict: A message indicating the result of the operation.
    """
    success = edge_controller.assign_version_to_edge(edge_id, version_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign version to edge.")
    return {"message": "Version assigned to edge successfully."}


# -------------------
# Edge Search Endpoint
# -------------------

@router.get("/search/", response_model=List[EdgeResponseSchema])
def search_edges(
    name: Optional[str] = Query(None, description="Filter by edge name"),
    taxonomy: Optional[List[str]] = Query(None, description="Filter by taxonomy categories")
):
    """
    Search for edges based on name and taxonomy categories.

    Args:
        name (Optional[str]): Filter edges by name.
        taxonomy (Optional[List[str]]): Filter edges by taxonomy categories.

    Returns:
        List[EdgeResponseSchema]: A list of edges matching the search criteria.
    """
    query = {}
    if name:
        query["name"] = name
    if taxonomy:
        # Similar to blocks, adjust based on actual schema and how taxonomy is linked
        query["taxonomy"] = taxonomy  # Adjust based on actual schema

    edges = edge_controller.search_edges(query)
    if edges is None:
        raise HTTPException(status_code=500, detail="Edge search failed.")
    return edges