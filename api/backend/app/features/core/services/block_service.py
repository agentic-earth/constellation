# app/services/block_service.py

"""
Block Service Module

This module defines the BlockService class responsible for managing all block-related operations.
It provides methods to create, retrieve, update, and delete blocks within the Supabase backend.
Additionally, it interacts with the TaxonomyService and VectorEmbeddingService to handle associated
taxonomy categories and vector embeddings, ensuring a cohesive and maintainable architecture.

Design Philosophy:
- Maintain independence from other services to uphold clear separation of concerns.
- Utilize Supabase's pg-vector for efficient vector storage and similarity querying.
- Ensure transactional integrity between block operations and associated taxonomy/vector embeddings.
- Implement robust error handling and comprehensive logging for production readiness.
"""

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import BaseModel, ValidationError

from supabase import Client
from postgrest import APIError as PostgrestError

from backend.app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema,
    VectorRepresentationSchema
)

from backend.app.logger import ConstellationLogger
from backend.app.database import get_supabase_client
from backend.app.utils.serialization_utils import serialize_dict


class BlockService:
    """
    BlockService handles all block-related operations, including CRUD (Create, Read, Update, Delete)
    functionalities. It interacts directly with the Supabase backend to manage block data and ensures
    data integrity and consistency throughout operations.
    """

    def __init__(self):
        """
        Initializes the BlockService with the Supabase client and ConstellationLogger for logging purposes.
        """
        self.supabase_client: Client = get_supabase_client()
        self.logger = ConstellationLogger()

    def create_block(self, block_data: BlockCreateSchema) -> Optional[BlockResponseSchema]:
        """
        Creates a new block in the Supabase `blocks` table.

        Args:
            block_data (BlockCreateSchema): The data required to create a new block.

        Returns:
            Optional[BlockResponseSchema]: The created block data if successful, None otherwise.
        """
        try:
            # Generate UUID for the new block if not provided
            if not block_data.block_id:
                block_id = uuid4()
            else:
                block_id = block_data.block_id
            print("new block id:", block_id)

            # Prepare block data with timestamps
            current_time = datetime.utcnow()
            block_dict = block_data.dict(exclude_unset=True)
            block_dict.update({
                "block_id": str(block_id),
                "created_at": current_time.isoformat(),
                "updated_at": current_time.isoformat(),
                "current_version_id": None  # To be set when creating the first version
            })

            # Insert the new block into Supabase
            response = self.supabase_client.table("blocks").insert(serialize_dict(block_dict)).execute()
            print("insert new block success")

            # if response.error:
            #     self.logger.log(
            #         "BlockService",
            #         "error",
            #         "Failed to create block in Supabase.",
            #         extra={"error": response.error.message, "block_data": block_dict}
            #     )
            #     return None

            # Construct the BlockResponseSchema
            created_block = BlockResponseSchema(
                block_id=UUID(block_dict["block_id"]),
                name=block_dict["name"],
                block_type=block_dict["block_type"],
                description=block_dict.get("description", ""),
                created_at=current_time,
                updated_at=current_time,
                current_version_id=None,  # To be updated by the caller if necessary
                taxonomy=None,
                vector_embedding=None
            )

            self.logger.log(
                "BlockService",
                "info",
                "Block created successfully.",
                extra={"block_id": str(created_block.block_id)}
            )
            return created_block

        except ValidationError as ve:
            self.logger.log(
                "BlockService",
                "error",
                "Validation error during block creation.",
                extra={"error": ve.errors(), "block_data": block_data.dict()}
            )
            return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block creation: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_data": block_data.dict()}
            )
            return None

    def get_block_by_id(self, block_id: UUID) -> Optional[BlockResponseSchema]:
        """
        Retrieves a block by its unique identifier from the Supabase `blocks` table.

        Args:
            block_id (UUID): The UUID of the block to retrieve.

        Returns:
            Optional[BlockResponseSchema]: The block data if found, None otherwise.
        """
        try:
            response = self.supabase_client.table("blocks").select("*").eq("block_id", str(block_id)).single().execute()

            if response.error:
                if "No rows found" in response.error.message:
                    self.logger.log(
                        "BlockService",
                        "warning",
                        "Block not found.",
                        extra={"block_id": str(block_id)}
                    )
                else:
                    self.logger.log(
                        "BlockService",
                        "error",
                        "Failed to retrieve block from Supabase.",
                        extra={"error": response.error.message, "block_id": str(block_id)}
                    )
                return None

            block_data = response.data

            # Construct the BlockResponseSchema
            retrieved_block = BlockResponseSchema(
                block_id=UUID(block_data["block_id"]),
                name=block_data["name"],
                block_type=block_data["block_type"],
                description=block_data.get("description", ""),
                created_at=block_data["created_at"],
                updated_at=block_data["updated_at"],
                current_version_id=UUID(block_data["current_version_id"]) if block_data.get("current_version_id") else None,
                taxonomy=None,
                vector_embedding=None
            )

            self.logger.log(
                "BlockService",
                "info",
                "Block retrieved successfully.",
                extra={"block_id": str(retrieved_block.block_id)}
            )
            return retrieved_block

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return None

    def update_block(self, block_id: UUID, update_data: BlockUpdateSchema) -> Optional[BlockResponseSchema]:
        """
        Updates an existing block's information in the Supabase `blocks` table.

        Args:
            block_id (UUID): The UUID of the block to update.
            update_data (BlockUpdateSchema): The data to update for the block.

        Returns:
            Optional[BlockResponseSchema]: The updated block data if successful, None otherwise.
        """
        try:
            # Prepare update data with updated_at timestamp
            current_time = datetime.utcnow()
            update_dict = update_data.dict(exclude_unset=True)
            update_dict.update({
                "updated_at": current_time.isoformat()
            })

            # Update the block in Supabase
            response = self.supabase_client.table("blocks").update(serialize_dict(update_dict)).eq("block_id", str(block_id)).execute()

            if response.error:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to update block in Supabase.",
                    extra={"error": response.error.message, "block_id": str(block_id), "update_data": update_dict}
                )
                return None

            # Retrieve the updated block
            updated_block = self.get_block_by_id(block_id)
            if updated_block:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block updated successfully.",
                    extra={"block_id": str(updated_block.block_id)}
                )
                return updated_block
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block updated but retrieval failed.",
                    extra={"block_id": str(block_id)}
                )
                return None

        except ValidationError as ve:
            self.logger.log(
                "BlockService",
                "error",
                "Validation error during block update.",
                extra={"error": ve.errors(), "update_data": update_data.dict()}
            )
            return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block update: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id), "update_data": update_data.dict()}
            )
            return None

    def delete_block(self, block_id: UUID) -> bool:
        """
        Deletes a block from the Supabase `blocks` table.

        Args:
            block_id (UUID): The UUID of the block to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_client.table("blocks").delete().eq("block_id", str(block_id)).execute()

            if response.error:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to delete block from Supabase.",
                    extra={"error": response.error.message, "block_id": str(block_id)}
                )
                return False

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
                f"Exception during block deletion: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return False

    def get_blocks_by_ids(self, block_ids: List[UUID]) -> Optional[List[BlockResponseSchema]]:
        """
        Retrieves multiple blocks by their unique identifiers from the Supabase `blocks` table.

        Args:
            block_ids (List[UUID]): A list of UUIDs of the blocks to retrieve.

        Returns:
            Optional[List[BlockResponseSchema]]: A list of block data if successful, None otherwise.
        """
        try:
            # Convert UUIDs to strings for the query
            block_ids_str = [str(bid) for bid in block_ids]

            response = self.supabase_client.table("blocks").select("*").in_("block_id", block_ids_str).execute()

            if response.error:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to retrieve blocks from Supabase.",
                    extra={"error": response.error.message, "block_ids": block_ids_str}
                )
                return None

            blocks = []
            for block_data in response.data:
                block = BlockResponseSchema(
                    block_id=UUID(block_data["block_id"]),
                    name=block_data["name"],
                    block_type=block_data["block_type"],
                    description=block_data.get("description", ""),
                    created_at=block_data["created_at"],
                    updated_at=block_data["updated_at"],
                    current_version_id=UUID(block_data["current_version_id"]) if block_data.get("current_version_id") else None,
                    taxonomy=None,
                    vector_embedding=None
                )
                blocks.append(block)

            self.logger.log(
                "BlockService",
                "info",
                f"{len(blocks)} blocks retrieved successfully.",
                extra={"block_ids": block_ids_str}
            )
            return blocks

        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during multiple block retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_ids": [str(bid) for bid in block_ids]}
            )
            return None

    def associate_version(self, block_id: UUID, version_id: UUID) -> bool:
        """
        Associates a specific version with a block by updating the `current_version_id`.

        Args:
            block_id (UUID): The UUID of the block.
            version_id (UUID): The UUID of the version to associate.

        Returns:
            bool: True if association was successful, False otherwise.
        """
        try:
            update_data = {
                "current_version_id": str(version_id),
                "updated_at": datetime.utcnow().isoformat()
            }

            response = self.supabase_client.table("blocks").update(serialize_dict(update_data)).eq("block_id", str(block_id)).execute()

            if response.error:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to associate version with block in Supabase.",
                    extra={"error": response.error.message, "block_id": str(block_id), "version_id": str(version_id)}
                )
                return False

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
                f"Exception during version association: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id), "version_id": str(version_id)}
            )
            return False

    def list_all_blocks(self) -> Optional[List[BlockResponseSchema]]:
        """
        Retrieves all blocks from the Supabase `blocks` table.

        Returns:
            Optional[List[BlockResponseSchema]]: A list of all block data if successful, None otherwise.
        """
        try:
            response = self.supabase_client.table("blocks").select("*").execute()

            if response.error:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to retrieve all blocks from Supabase.",
                    extra={"error": response.error.message}
                )
                return None

            blocks = []
            for block_data in response.data:
                block = BlockResponseSchema(
                    block_id=UUID(block_data["block_id"]),
                    name=block_data["name"],
                    block_type=block_data["block_type"],
                    description=block_data.get("description", ""),
                    created_at=block_data["created_at"],
                    updated_at=block_data["updated_at"],
                    current_version_id=UUID(block_data["current_version_id"]) if block_data.get("current_version_id") else None,
                    taxonomy=None,
                    vector_embedding=None
                )
                blocks.append(block)

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
                f"Exception during all blocks retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None
