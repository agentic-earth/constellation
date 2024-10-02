from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from prisma import Prisma
from backend.app.schemas import BlockCreateSchema, BlockUpdateSchema, BlockResponseSchema

class BlockService:
    """
    BlockService handles all block-related operations, including CRUD (Create, Read, Update, Delete) functionalities.
    It interacts directly with the Prisma client to manage block data.
    """

    def __init__(self, prisma: Prisma):
        self.prisma = prisma

    async def create_block(self, block_data: BlockCreateSchema) -> Optional[BlockResponseSchema]:
        block = await self.prisma.blocks.create(
            data={
                "block_id": uuid4(),
                "name": block_data.name,
                "block_type": block_data.block_type.value,
                "description": block_data.description,
                "created_by": block_data.created_by,
                "metadata": block_data.metadata,
                "taxonomy": block_data.taxonomy,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        return BlockResponseSchema(**block.__dict__)

    async def get_block_by_id(self, block_id: UUID) -> Optional[BlockResponseSchema]:
        block = await self.prisma.blocks.find_unique(where={"block_id": str(block_id)})
        if block:
            return BlockResponseSchema(**block.__dict__)
        return None

    async def update_block(self, block_id: UUID, update_data: BlockUpdateSchema) -> Optional[BlockResponseSchema]:
        block = await self.prisma.blocks.update(
            where={"block_id": str(block_id)},
            data={
                "name": update_data.name,
                "block_type": update_data.block_type.value if update_data.block_type else None,
                "description": update_data.description,
                "updated_by": update_data.updated_by,
                "metadata": update_data.metadata,
                "taxonomy": update_data.taxonomy,
                "updated_at": datetime.utcnow(),
            },
        )
        return BlockResponseSchema(**block.__dict__)

    async def delete_block(self, block_id: UUID) -> bool:
        deleted_block = await self.prisma.blocks.delete(where={"block_id": str(block_id)})
        return deleted_block is not None

    async def get_blocks_by_ids(self, block_ids: List[UUID]) -> Optional[List[BlockResponseSchema]]:
        blocks = await self.prisma.blocks.find_many(where={"block_id": {"in": [str(bid) for bid in block_ids]}})
        return [BlockResponseSchema(**block.__dict__) for block in blocks] if blocks else None

    async def list_all_blocks(self) -> Optional[List[BlockResponseSchema]]:
        blocks = await self.prisma.blocks.find_many()
        return [BlockResponseSchema(**block.__dict__) for block in blocks] if blocks else None