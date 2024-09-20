# app/services/block_service.py

"""
Block Service Module

This module encapsulates all block-related business logic and interactions with the Supabase backend.
It provides functions to create, retrieve, update, and delete blocks, ensuring that all operations are
logged appropriately using the Constellation Logger.

Design Philosophy:
- Utilize Supabase's REST API for standard CRUD operations for performance and reliability.
- Use Python only for advanced logic that cannot be handled directly by Supabase.
- Ensure flexibility to adapt to schema changes with minimal modifications.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from app.models import Block, BlockCreateSchema, BlockUpdateSchema, BlockResponseSchema
from app.logger import ConstellationLogger
from app.utils.helpers import SupabaseClientManager
from app.schemas import BlockResponseSchema
from datetime import datetime


class BlockService:
    """
    BlockService class encapsulates all block-related operations.
    """

    def __init__(self):
        """
        Initializes the BlockService with the Supabase client and logger.
        """
        self.supabase_manager = SupabaseClientManager()
        self.logger = ConstellationLogger()

    def create_block(self, block_data: BlockCreateSchema) -> Optional[BlockResponseSchema]:
        """
        Creates a new block in the Supabase database.

        Args:
            block_data (BlockCreateSchema): The data required to create a new block.

        Returns:
            Optional[BlockResponseSchema]: The created block data if successful, None otherwise.
        """
        try:
            # Convert Pydantic schema to dictionary
            data = block_data.dict()
            response = self.supabase_manager.client.table("blocks").insert(data).execute()

            if response.status_code in [200, 201] and response.data:
                created_block = BlockResponseSchema(**response.data[0])
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block created successfully",
                    block_id=created_block.block_id,
                    name=created_block.name,
                    block_type=created_block.block_type
                )
                return created_block
            else:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to create block",
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block creation: {e}"
            )
            return None

    def get_block_by_id(self, block_id: UUID) -> Optional[BlockResponseSchema]:
        """
        Retrieves a block by its unique identifier.

        Args:
            block_id (UUID): The UUID of the block to retrieve.

        Returns:
            Optional[BlockResponseSchema]: The block data if found, None otherwise.
        """
        try:
            response = self.supabase_manager.client.table("blocks").select("*").eq("block_id", str(block_id)).single().execute()

            if response.status_code == 200 and response.data:
                block = BlockResponseSchema(**response.data)
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block retrieved successfully",
                    block_id=block.block_id,
                    name=block.name,
                    block_type=block.block_type
                )
                return block
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block not found",
                    block_id=block_id,
                    status_code=response.status_code
                )
                return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block retrieval: {e}"
            )
            return None

    def update_block(self, block_id: UUID, update_data: BlockUpdateSchema) -> Optional[BlockResponseSchema]:
        """
        Updates an existing block's information.

        Args:
            block_id (UUID): The UUID of the block to update.
            update_data (BlockUpdateSchema): The data to update for the block.

        Returns:
            Optional[BlockResponseSchema]: The updated block data if successful, None otherwise.
        """
        try:
            data = update_data.dict(exclude_unset=True)
            response = self.supabase_manager.client.table("blocks").update(data).eq("block_id", str(block_id)).execute()

            if response.status_code == 200 and response.data:
                updated_block = BlockResponseSchema(**response.data[0])
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block updated successfully",
                    block_id=updated_block.block_id,
                    updated_fields=list(data.keys())
                )
                return updated_block
            else:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to update block",
                    block_id=block_id,
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block update: {e}"
            )
            return None

    def delete_block(self, block_id: UUID) -> bool:
        """
        Deletes a block from the Supabase database.

        Args:
            block_id (UUID): The UUID of the block to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_manager.client.table("blocks").delete().eq("block_id", str(block_id)).execute()

            if response.status_code == 200 and response.count > 0:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block deleted successfully",
                    block_id=block_id
                )
                return True
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block not found or already deleted",
                    block_id=block_id,
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block deletion: {e}"
            )
            return False

    def list_blocks(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[BlockResponseSchema]]:
        """
        Retrieves a list of blocks with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the blocks.

        Returns:
            Optional[List[BlockResponseSchema]]: A list of blocks if successful, None otherwise.
        """
        try:
            query = self.supabase_manager.client.table("blocks").select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.status_code == 200 and response.data:
                blocks = [BlockResponseSchema(**block) for block in response.data]
                self.logger.log(
                    "BlockService",
                    "info",
                    f"{len(blocks)} blocks retrieved successfully",
                    filters=filters
                )
                return blocks
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "No blocks found",
                    filters=filters,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during listing blocks: {e}"
            )
            return None

    def assign_version_to_block(self, block_id: UUID, version_id: UUID) -> bool:
        """
        Assigns a specific version to a block by updating the current_version_id.

        Args:
            block_id (UUID): The UUID of the block.
            version_id (UUID): The UUID of the version to assign.

        Returns:
            bool: True if assignment was successful, False otherwise.
        """
        try:
            data = {"current_version_id": str(version_id)}
            response = self.supabase_manager.client.table("blocks").update(data).eq("block_id", str(block_id)).execute()

            if response.status_code == 200 and response.data:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Assigned version to block successfully",
                    block_id=block_id,
                    version_id=version_id
                )
                return True
            else:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to assign version to block",
                    block_id=block_id,
                    version_id=version_id,
                    status_code=response.status_code,
                    error=response.error
                )
                return False
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during assigning version to block: {e}"
            )
            return False
        
    def search_blocks(self, query: Dict[str, Any]) -> Optional[List[BlockResponseSchema]]:
        """
        Searches for blocks based on provided query parameters.

        Args:
            query (Dict[str, Any]): A dictionary of query parameters for filtering.

        Returns:
            Optional[List[BlockResponseSchema]]: A list of blocks matching the search criteria.
        """
        try:
            supabase_query = self.supabase_manager.client.table("blocks").select("*")

            # Apply filters based on the query parameters
            for key, value in query.items():
                if isinstance(value, list):
                    supabase_query = supabase_query.in_(key, value)
                else:
                    supabase_query = supabase_query.ilike(key, f"%{value}%")  # Case-insensitive LIKE

            response = supabase_query.execute()

            if response.status_code == 200 and response.data:
                blocks = [BlockResponseSchema(**block) for block in response.data]
                self.logger.log(
                    "BlockService",
                    "info",
                    f"{len(blocks)} blocks found matching the search criteria.",
                    query=query
                )
                return blocks
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "No blocks found matching the search criteria.",
                    query=query,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block search: {e}"
            )
            return None
