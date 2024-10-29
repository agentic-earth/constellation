# routes/blocks.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from uuid import UUID

from prisma.partials import (
    BlockBasicInfo,
    BlockBasicInfoWithID,
)

from backend.app.features.core.controllers.block_controller import BlockController
from backend.app.dependencies import get_block_controller

router = APIRouter()

# -------------------
# Block Endpoints
# -------------------

@router.post("/", response_model=BlockBasicInfo, status_code=status.HTTP_201_CREATED)
async def create_block(
    block: BlockBasicInfo,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    block_data = block.dict(exclude_unset=True)
    created_block = await controller.create_block(block_data, user_id)
    if not created_block:
        raise HTTPException(status_code=400, detail="Block creation failed.")
    return created_block

@router.get("/{block_id}", response_model=BlockBasicInfoWithID)
async def get_block(
    block_id: UUID,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    block = await controller.get_block_by_id(block_id, user_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found.")
    return block

@router.put("/{block_id}", response_model=BlockBasicInfo)
async def update_block(
    block_id: UUID,
    update_data: BlockBasicInfo,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    update_dict = update_data.dict(exclude_unset=True)
    updated_block = await controller.update_block(block_id, update_dict, user_id)
    if not updated_block:
        raise HTTPException(status_code=400, detail="Block update failed.")
    return updated_block

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

@router.post("/search-by-filters/", response_model=List[BlockBasicInfo])
async def search_blocks_by_filters(
    search_filters: Dict[str, Any],
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller)
):
    results = await controller.search_blocks_by_filters(search_filters, user_id)
    if results is None:
        raise HTTPException(status_code=500, detail="Similarity search failed.")
    return results

@router.post("/search-by-vector/", response_model=List[BlockBasicInfo])
async def search_blocks_by_vector(
    query: str,
    user_id: UUID,
    top_k: int = 10,
    controller: BlockController = Depends(get_block_controller)
):
    results = await controller.search_blocks_by_vector_similarity(query, user_id, top_k)
    if results is None:
        raise HTTPException(status_code=500, detail="Similarity search failed.")
    return results
