# app/routes/blocks.py

"""
Block Routes Module

This module defines all API endpoints related to block operations, including creating, retrieving,
updating, deleting blocks, and managing their versions. It leverages the BlockController to perform
business logic and interact with the services layer. All operations are logged using the Constellation Logger.

Responsibilities:
- Define HTTP endpoints for block-related operations.
- Validate and parse incoming request data using Pydantic schemas.
- Delegate request handling to the BlockController.
- Handle and respond to errors appropriately.

Design Philosophy:
- Maintain thin Routes by delegating complex logic to Controllers.
- Ensure clear separation between HTTP handling and business logic.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
from app.controllers.block_controller import BlockController
from app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema
)

router = APIRouter(
    prefix="/blocks",
    tags=["Blocks"],
    responses={404: {"description": "Not found"}},
)

# Initialize the BlockController instance
block_controller = BlockController()

# -------------------
# Basic Block Endpoints
# -------------------

@router.post("/", response_model=BlockResponseSchema, status_code=201)
def create_block(block: BlockCreateSchema):
    """
    Create a new block.

    Args:
        block (BlockCreateSchema): The data required to create a new block.

    Returns:
        BlockResponseSchema: The created block's data.
    """
    created_block = block_controller.create_block(block)
    if not created_block:
        raise HTTPException(status_code=400, detail="Block creation failed.")
    return created_block

@router.get("/{block_id}", response_model=BlockResponseSchema)
def get_block(block_id: UUID):
    """
    Retrieve a block by its UUID.

    Args:
        block_id (UUID): The UUID of the block to retrieve.

    Returns:
        BlockResponseSchema: The block's data if found.
    """
    block = block_controller.get_block_by_id(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found.")
    return block

@router.put("/{block_id}", response_model=BlockResponseSchema)
def update_block(block_id: UUID, block_update: BlockUpdateSchema):
    """
    Update an existing block's information.

    Args:
        block_id (UUID): The UUID of the block to update.
        block_update (BlockUpdateSchema): The data to update for the block.

    Returns:
        BlockResponseSchema: The updated block's data if successful.
    """
    updated_block = block_controller.update_block(block_id, block_update)
    if not updated_block:
        raise HTTPException(status_code=400, detail="Block update failed.")
    return updated_block

@router.delete("/{block_id}", status_code=204)
def delete_block(block_id: UUID):
    """
    Delete a block by its UUID.

    Args:
        block_id (UUID): The UUID of the block to delete.

    Returns:
        HTTP 204 No Content: If deletion was successful.
    """
    success = block_controller.delete_block(block_id)
    if not success:
        raise HTTPException(status_code=404, detail="Block not found or already deleted.")
    return

@router.get("/", response_model=List[BlockResponseSchema])
def list_blocks(name: Optional[str] = None, block_type: Optional[str] = None):
    """
    List blocks with optional filtering by name and block type.

    Args:
        name (Optional[str]): Filter blocks by name.
        block_type (Optional[str]): Filter blocks by block type.

    Returns:
        List[BlockResponseSchema]: A list of blocks matching the filters.
    """
    filters = {}
    if name:
        filters["name"] = name
    if block_type:
        filters["block_type"] = block_type
    blocks = block_controller.list_blocks(filters)
    if blocks is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve blocks.")
    return blocks

# -------------------
# Complex Block Operations Endpoints
# -------------------

@router.post("/{block_id}/assign-version/", status_code=200)
def assign_version(block_id: UUID, version_id: UUID):
    """
    Assign a specific version to a block.

    Args:
        block_id (UUID): The UUID of the block.
        version_id (UUID): The UUID of the version to assign.

    Returns:
        dict: A message indicating the result of the operation.
    """
    success = block_controller.assign_version_to_block(block_id, version_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to assign version to block.")
    return {"message": "Version assigned to block successfully."}

# -------------------
# Block Search Endpoint
# -------------------

@router.get("/search/", response_model=List[BlockResponseSchema])
def search_blocks(
    name: Optional[str] = Query(None, description="Filter by block name"),
    block_type: Optional[BlockTypeEnum] = Query(None, description="Filter by block type"),
    taxonomy: Optional[List[str]] = Query(None, description="Filter by taxonomy categories")
):
    """
    Search for blocks based on name, block type, and taxonomy categories.

    Args:
        name (Optional[str]): Filter blocks by name.
        block_type (Optional[BlockTypeEnum]): Filter blocks by block type.
        taxonomy (Optional[List[str]]): Filter blocks by taxonomy categories.

    Returns:
        List[BlockResponseSchema]: A list of blocks matching the search criteria.
    """
    query = {}
    if name:
        query["name"] = name
    if block_type:
        query["block_type"] = block_type.value
    if taxonomy:
        # Assuming taxonomy categories are stored in a separate table and linked via BlockTaxonomy
        # This might require joining or additional querying which Supabase may not support directly
        # For simplicity, we'll assume a field `taxonomy` exists in blocks for filtering
        query["taxonomy"] = taxonomy  # Adjust based on actual schema

    blocks = block_controller.search_blocks(query)
    if blocks is None:
        raise HTTPException(status_code=500, detail="Block search failed.")
    return blocks