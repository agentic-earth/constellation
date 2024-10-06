# app/services/block_service.py

"""
Block Service Module

This module defines the BlockService class responsible for managing all block-related operations.
It provides methods to create, retrieve, update, and delete blocks within the database using Prisma ORM.
Additionally, it interacts with the TaxonomyService and VectorEmbeddingService to handle associated
taxonomy categories and vector embeddings, ensuring a cohesive and maintainable architecture.

Design Philosophy:
- Maintain independence from other services to uphold clear separation of concerns.
- Utilize Prisma ORM for efficient database operations and type safety.
- Ensure transactional integrity between block operations and associated taxonomy/vector embeddings.
- Implement robust error handling and comprehensive logging for production readiness.
"""

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from prisma import Prisma
from prisma.models import blocks as PrismaBlock
from backend.app.logger import ConstellationLogger
import json


class BlockService:
    """
    BlockService handles all block-related operations, including CRUD (Create, Read, Update, Delete)
    functionalities. It interacts directly with the database using Prisma ORM to manage block data and ensures
    data integrity and consistency throughout operations.
    """

    def __init__(self):
        """
        Initializes the BlockService with ConstellationLogger for logging purposes.
        """
        self.logger = ConstellationLogger()

    async def create_block(self, tx: Prisma, block_data: Dict[str, Any]) -> Optional[PrismaBlock]:
        """
        Creates a new block in the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_data (Dict[str, Any]): The data required to create a new block.

        Returns:
            Optional[PrismaBlock]: The created block data if successful, None otherwise.
        """
        try:
            # Prepare block data
            block_dict = {
                "block_id": block_data.get("block_id", str(uuid4())),
                "name": block_data.get("name"),
                "block_type": block_data.get("block_type"),
                "description": block_data.get("description"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "current_version_id": None  # To be set when creating the first version
            }

            # Create the new block using Prisma
            created_block = await tx.blocks.create(data=block_dict)

            self.logger.log(
                "BlockService",
                "info",
                "Block created successfully.",
                extra={"block_id": created_block.block_id}
            )
            return created_block

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block creation: {e}",
                extra={"traceback": traceback.format_exc(), "block_data": block_data}
            )
            return None

    async def get_block_by_id(self, tx: Prisma, block_id: UUID) -> Optional[PrismaBlock]:
        """
        Retrieves a block by its unique identifier from the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_id (UUID): The UUID of the block to retrieve.

        Returns:
            Optional[PrismaBlock]: The block data if found, None otherwise.
        """
        try:
            block = await tx.blocks.find_unique(where={"block_id": str(block_id)})

            if not block:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block not found.",
                    extra={"block_id": str(block_id)}
                )
                return None

            self.logger.log(
                "BlockService",
                "info",
                "Block retrieved successfully.",
                extra={"block_id": block.block_id}
            )
            return block

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block retrieval: {e}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return None

    async def update_block(self, tx: Prisma, block_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaBlock]:
        """
        Updates an existing block's information in the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_id (UUID): The UUID of the block to update.
            update_data (Dict[str, Any]): The data to update for the block.

        Returns:
            Optional[PrismaBlock]: The updated block data if successful, None otherwise.
        """
        try:
            # Prepare update data
            update_dict = {k: v for k, v in update_data.items() if v is not None}
            update_dict = {
                "name": update_data.get("name"),
                "block_type": update_data.get("block_type"),
                "description": update_data.get("description"),
                "updated_at": datetime.utcnow()
            }

            # Update the block using Prisma
            updated_block = await tx.blocks.update(
                where={"block_id": str(block_id)},
                data=update_dict
            )

            self.logger.log(
                "BlockService",
                "info",
                "Block updated successfully.",
                extra={"block_id": updated_block.block_id}
            )
            return updated_block

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block update: {e}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id), "update_data": update_data}
            )
            return None

    async def delete_block(self, tx: Prisma, block_id: UUID) -> bool:
        """
        Deletes a block from the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_id (UUID): The UUID of the block to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            await tx.blocks.delete(where={"block_id": str(block_id)})

            self.logger.log(
                "BlockService",
                "info",
                "Block deleted successfully.",
                extra={"block_id": str(block_id)}
            )
            return True

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block deletion: {e}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return False

    async def get_blocks_by_ids(self, tx: Prisma, block_ids: List[UUID]) -> Optional[List[PrismaBlock]]:
        """
        Retrieves multiple blocks by their unique identifiers from the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_ids (List[UUID]): A list of UUIDs of the blocks to retrieve.

        Returns:
            Optional[List[PrismaBlock]]: A list of block data if successful, None otherwise.
        """
        try:
            blocks = await tx.blocks.find_many(where={"block_id": {"in": [str(bid) for bid in block_ids]}})

            self.logger.log(
                "BlockService",
                "info",
                f"{len(blocks)} blocks retrieved successfully.",
                extra={"block_ids": [str(bid) for bid in block_ids]}
            )
            return blocks

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during multiple block retrieval: {e}",
                extra={"traceback": traceback.format_exc(), "block_ids": [str(bid) for bid in block_ids]}
            )
            return None

    async def associate_version(self, tx: Prisma, block_id: UUID, version_id: UUID) -> bool:
        """
        Associates a specific version with a block by updating the `current_version_id`.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_id (UUID): The UUID of the block.
            version_id (UUID): The UUID of the version to associate.

        Returns:
            bool: True if association was successful, False otherwise.
        """
        try:
            await tx.blocks.update(
                where={"block_id": str(block_id)},
                data={"current_version_id": str(version_id)}
            )

            self.logger.log(
                "BlockService",
                "info",
                "Version associated with block successfully.",
                extra={"block_id": str(block_id), "version_id": str(version_id)}
            )
            return True

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during version association: {e}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id), "version_id": str(version_id)}
            )
            return False

    async def list_all_blocks(self, tx: Prisma) -> Optional[List[PrismaBlock]]:
        """
        Retrieves all blocks from the database.

        Args:
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[List[PrismaBlock]]: A list of all block data if successful, None otherwise.
        """
        try:
            blocks = await tx.blocks.find_many()

            self.logger.log(
                "BlockService",
                "info",
                f"Total of {len(blocks)} blocks retrieved successfully.",
                extra={"count": len(blocks)}
            )
            return blocks

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during all blocks retrieval: {e}",
                extra={"traceback": traceback.format_exc()}
            )
            return None