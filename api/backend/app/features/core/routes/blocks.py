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

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from prisma import Prisma
from backend.app.schemas import BlockCreateSchema, BlockUpdateSchema, BlockResponseSchema
from backend.app.features.core.controllers.block_controller import BlockController

router = APIRouter()
prisma = Prisma()

@router.on_event("startup")
async def startup():
    await prisma.connect()

@router.on_event("shutdown")
async def shutdown():
    await prisma.disconnect()

@router.post("/", response_model=BlockResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_block(block: BlockCreateSchema, user_id: UUID):
    controller = BlockController(prisma)
    created_block = await controller.create_block(block, user_id)
    if not created_block:
        raise HTTPException(status_code=400, detail="Block creation failed.")
    return created_block

@router.get("/{block_id}", response_model=BlockResponseSchema)
async def get_block(block_id: UUID, user_id: UUID):
    controller = BlockController(prisma)
    block = await controller.get_block_by_id(block_id, user_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found.")
    return block

@router.put("/{block_id}", response_model=BlockResponseSchema)
async def update_block(block_id: UUID, update_data: BlockUpdateSchema, user_id: UUID):
    controller = BlockController(prisma)
    updated_block = await controller.update_block(block_id, update_data, user_id)
    if not updated_block:
        raise HTTPException(status_code=400, detail="Block update failed.")
    return updated_block

@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(block_id: UUID, user_id: UUID):
    controller = BlockController(prisma)
    success = await controller.delete_block(block_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Block deletion failed.")
    return

@router.post("/search/", response_model=List[BlockResponseSchema])
async def similarity_search(query: List[float], top_k: int = 10, user_id: UUID = Depends()):
    controller = BlockController(prisma)
    results = await controller.perform_similarity_search(query, top_k, user_id)
    if results is None:
        raise HTTPException(status_code=500, detail="Similarity search failed.")
    return results