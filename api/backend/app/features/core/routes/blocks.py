# routes/blocks.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from backend.app.schemas.block_schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema
)
from backend.app.controllers.block_controller import BlockController
from backend.app.dependencies import get_block_controller

router = APIRouter()

@router.post("/", response_model=BlockResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_block(
    block: BlockCreateSchema,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    block_data = block.dict(exclude_unset=True)
    created_block = await controller.create_block(block_data, user_id)
    if not created_block:
        raise HTTPException(status_code=400, detail="Block creation failed.")
    return BlockResponseSchema(**created_block)

@router.get("/{block_id}", response_model=BlockResponseSchema)
async def get_block(
    block_id: UUID,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    block = await controller.get_block_by_id(block_id, user_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found.")
    return BlockResponseSchema(**block)

@router.put("/{block_id}", response_model=BlockResponseSchema)
async def update_block(
    block_id: UUID,
    update_data: BlockUpdateSchema,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    update_dict = update_data.dict(exclude_unset=True)
    updated_block = await controller.update_block(block_id, update_dict, user_id)
    if not updated_block:
        raise HTTPException(status_code=400, detail="Block update failed.")
    return BlockResponseSchema(**updated_block)

@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(
    block_id: UUID,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    success = await controller.delete_block(block_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Block deletion failed.")
    return

@router.post("/search/", response_model=List[BlockResponseSchema])
async def similarity_search(
    query: List[float],
    top_k: int = 10,
    user_id: UUID = Depends(),
    controller: BlockController = Depends(get_block_controller)
):
    results = await controller.perform_similarity_search(query, top_k, user_id)
    if results is None:
        raise HTTPException(status_code=500, detail="Similarity search failed.")
    return [BlockResponseSchema(**result) for result in results]