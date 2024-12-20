# routes/blocks.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from uuid import UUID

from prisma.partials import (
    BlockBasicInfo,
    BlockBasicInfoWithID,
    BlockVectorContent,
    PaperBasicInfo,
    BlockUpdateInfo,
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
    vector_content: Optional[BlockVectorContent] = None,
    paper: Optional[PaperBasicInfo] = None,
    controller: BlockController = Depends(get_block_controller),
):
    block_data = block.dict(exclude_unset=True)
    vector_content_data = (
        vector_content.dict(exclude_unset=True) if vector_content else {}
    )
    paper_data = paper.dict(exclude_unset=True) if paper else {}
    combined_data = {**block_data, **vector_content_data, **paper_data}

    created_block = await controller.create_block(combined_data, user_id)
    if not created_block:
        raise HTTPException(status_code=400, detail="Block creation failed.")
    return created_block


@router.get("/{block_id}", response_model=BlockBasicInfoWithID)
async def get_block(
    block_id: UUID,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller),
):
    block = await controller.get_block_by_id(block_id, user_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found.")
    return block


@router.put("/{block_id}", response_model=BlockBasicInfo)
async def update_block(
    block_id: UUID,
    update_data: BlockUpdateInfo,
    user_id: UUID,
    vector_content: Optional[BlockVectorContent] = None,
    controller: BlockController = Depends(get_block_controller),
):
    update_dict = update_data.dict(exclude_unset=True)
    vector_content_data = (
        vector_content.dict(exclude_unset=True) if vector_content else {}
    )
    combined_data = {**update_dict, **vector_content_data}

    updated_block = await controller.update_block(block_id, combined_data, user_id)
    if not updated_block:
        raise HTTPException(status_code=400, detail="Block update failed.")
    return updated_block


@router.delete("/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_block(
    block_id: UUID,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller),
):
    success = await controller.delete_block(block_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Block deletion failed.")
    return


@router.post("/search-by-filters/", response_model=List[BlockBasicInfo])
async def search_blocks_by_filters(
    search_filters: Dict[str, Any],
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller),
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
    controller: BlockController = Depends(get_block_controller),
):
    results = await controller.search_blocks_by_vector_similarity(query, user_id, top_k)
    if results is None:
        raise HTTPException(status_code=500, detail="Similarity search failed.")
    return results


@router.get("/get-all-blocks/", response_model=List[BlockBasicInfoWithID])
async def get_all_blocks(
    user_id: str,
    controller: BlockController = Depends(get_block_controller),
):
    blocks = await controller.get_all_blocks(user_id)
    if blocks is None:
        raise HTTPException(status_code=500, detail="Failed to get all blocks.")
    return blocks


@router.get("/construct-pipeline/", response_model=Dict[str, Any])
async def construct_pipeline(
    query: str,
    user_id: UUID,
    controller: BlockController = Depends(get_block_controller),
):
    results = await controller.construct_pipeline(query, user_id)
    if results is None:
        raise HTTPException(status_code=500, detail="Construct pipeline failed.")
    return results
