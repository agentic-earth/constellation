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

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.schemas import (
    BlockResponseSchema,
    BlockCreateSchema,
    BlockUpdateSchema,
)

from app.models import BlockTypeEnum

from app.logger import ConstellationLogger
from app.database import get_supabase_client
from app.utils.serialization_utils import serialize_dict


class BlockService:
    """
    BlockService class encapsulates all block-related operations.
    """

    def __init__(self):
        """
        Initializes the BlockService with the Supabase client and logger.
        """
        self.client = get_supabase_client()
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
            data = block_data.dict(exclude_unset=True)

            # Ensure block_type is a valid enum value
            if not BlockTypeEnum.has_value(data['block_type']):
                self.logger.log(
                    "BlockService",
                    "error",
                    f"Invalid block_type: {data['block_type']}",
                    extra={"block_type": data['block_type']}
                )
                return None

            # Add created_at and updated_at if not provided
            current_time = datetime.utcnow()
            data.setdefault('created_at', current_time)
            data.setdefault('updated_at', current_time)

            # Serialize the data
            serialized_data = serialize_dict(data)

            # Insert the new block into the database
            response = self.client.table("blocks").insert(serialized_data).execute()

            if response.data:
                # If created_by is not in the response data, set it to None
                response_data = response.data[0]
                response_data.setdefault('created_by', None)

                created_block = BlockResponseSchema(**response_data)
                self.logger.log(
                    "BlockService",
                    "info",
                    f"Block created successfully: {created_block.block_id}",
                    extra={
                        "block_id": str(created_block.block_id),
                        "name": created_block.name,
                        "block_type": created_block.block_type.value
                    }
                )
                return created_block
            else:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to create block",
                    extra={"error": str(response.error)}
                )
                return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block creation: {str(e)}",
                extra={"traceback": traceback.format_exc()}
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
            response = self.client.table("blocks").select("*").eq("block_id", str(block_id)).single().execute()

            if response.data:
                block = BlockResponseSchema(**response.data)
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block retrieved successfully",
                    extra={
                        "block_id": str(block.block_id),
                        "name": block.name,
                        "block_type": block.block_type.value
                    }
                )
                return block
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block not found",
                    extra={"block_id": str(block_id)}
                )
                return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block retrieval: {e}",
                extra={"traceback": traceback.format_exc()}
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

            if not data:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "No update data provided",
                    extra={"block_id": str(block_id)}
                )
                return None

            # Update the 'updated_at' field
            data['updated_at'] = datetime.utcnow()

            # Serialize the data
            serialized_data = serialize_dict(data)

            # Update the block in the database
            response = self.client.table("blocks").update(serialized_data).eq("block_id", str(block_id)).execute()

            if response.data:
                updated_block = BlockResponseSchema(**response.data[0])
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block updated successfully",
                    extra={
                        "block_id": str(updated_block.block_id),
                        "updated_fields": list(data.keys())
                    }
                )
                return updated_block
            else:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to update block",
                    extra={"block_id": str(block_id), "error": str(response.error)}
                )
                return None
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block update: {e}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    def delete_block(self, block_id: UUID) -> bool:
        """
        Deletes a block from the Supabase database and validates the deletion.

        Args:
            block_id (UUID): The UUID of the block to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Perform the delete operation
            response = self.client.table("blocks").delete().eq("block_id", str(block_id)).execute()

            if response.data and len(response.data) > 0:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Block deleted successfully",
                    extra={"block_id": str(block_id)}
                )

                # Validate deletion by attempting to retrieve the block without using .single()
                validation_response = self.client.table("blocks").select("*").eq("block_id", str(block_id)).execute()

                if not validation_response.data:
                    self.logger.log(
                        "BlockService",
                        "info",
                        "Deletion validated: Block no longer exists",
                        extra={"block_id": str(block_id)}
                    )
                    return True
                else:
                    self.logger.log(
                        "BlockService",
                        "error",
                        "Deletion validation failed: Block still exists",
                        extra={"block_id": str(block_id)}
                    )
                    return False
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Block not found or already deleted",
                    extra={"block_id": str(block_id)}
                )
                return False
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during block deletion: {e}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    def list_blocks(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> Optional[List[BlockResponseSchema]]:
        """
        Retrieves a list of blocks with optional filtering and pagination.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the blocks.
            limit (int): Maximum number of blocks to retrieve.
            offset (int): Number of blocks to skip for pagination.

        Returns:
            Optional[List[BlockResponseSchema]]: A list of blocks if successful, None otherwise.
        """
        try:
            query = self.client.table("blocks").select("*").limit(limit).offset(offset)
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.data:
                blocks = [BlockResponseSchema(**block) for block in response.data]
                self.logger.log(
                    "BlockService",
                    "info",
                    f"{len(blocks)} blocks retrieved successfully",
                    extra={"filters": filters, "limit": limit, "offset": offset}
                )
                return blocks
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "No blocks found",
                    extra={"filters": filters, "limit": limit, "offset": offset}
                )
                return []
        except Exception as e:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during listing blocks: {e}",
                extra={"traceback": traceback.format_exc()}
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
            data = {"current_version_id": str(version_id), "updated_at": datetime.utcnow()}
            response = self.client.table("blocks").update(data).eq("block_id", str(block_id)).execute()

            if response.data and len(response.data) > 0:
                self.logger.log(
                    "BlockService",
                    "info",
                    "Assigned version to block successfully",
                    extra={"block_id": str(block_id), "version_id": str(version_id)}
                )
                return True
            else:
                self.logger.log(
                    "BlockService",
                    "error",
                    "Failed to assign version to block",
                    extra={"block_id": str(block_id), "version_id": str(version_id), "error": str(response.error)}
                )
                return False
        except Exception as exc:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during assigning version to block: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    def count_blocks(self, filters: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Counts the total number of blocks with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the blocks.

        Returns:
            Optional[int]: The count of blocks matching the filters, None otherwise.
        """
        try:
            query = self.client.table("blocks").select("*", count='exact')
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.count is not None:
                self.logger.log(
                    "BlockService",
                    "info",
                    f"Total blocks count: {response.count}",
                    extra={"filters": filters}
                )
                return response.count
            else:
                self.logger.log(
                    "BlockService",
                    "warning",
                    "Failed to retrieve blocks count",
                    extra={"filters": filters}
                )
                return None
        except Exception as exc:
            self.logger.log(
                "BlockService",
                "critical",
                f"Exception during counting blocks: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return None


if __name__ == "__main__":
    import traceback

    print("Starting BlockService tests...")
    block_service = BlockService()

    # Function to generate a unique block name
    def generate_unique_name(base_name):
        import random
        return f"{base_name}_{random.randint(1000, 9999)}"

    try:
        # Create a block
        block_name = generate_unique_name("Test Block")
        new_block = BlockCreateSchema(
            name=block_name,
            block_type=BlockTypeEnum.dataset,
            description="This is a test block"
        )
        print(f"Creating block: {new_block}")
        created_block = block_service.create_block(new_block)

        if created_block:
            print(f"Created block: {created_block}")

            # Get the block
            retrieved_block = block_service.get_block_by_id(created_block.block_id)
            if retrieved_block:
                print(f"Retrieved block: {retrieved_block}")
            else:
                print("Failed to retrieve the created block.")

            # Update the block
            update_data = BlockUpdateSchema(description="Updated description")
            updated_block = block_service.update_block(created_block.block_id, update_data)
            if updated_block:
                print(f"Updated block: {updated_block}")
            else:
                print("Failed to update the block.")

            # List blocks
            blocks = block_service.list_blocks()
            if blocks is not None:
                print(f"Listed {len(blocks)} blocks:")
                for block in blocks:
                    print(block)
            else:
                print("Failed to list blocks.")

            # Delete the block
            if block_service.delete_block(created_block.block_id):
                print("Block deleted successfully.")
            else:
                print("Failed to delete block.")

            # Verify deletion
            post_delete_block = block_service.get_block_by_id(created_block.block_id)
            if post_delete_block:
                print("Error: Block still exists after deletion.")
            else:
                print("Deletion verified: Block no longer exists.")

            # Create another block with a different name
            another_block_name = generate_unique_name("Another Test Block")
            another_block = BlockCreateSchema(
                name=another_block_name,
                block_type=BlockTypeEnum.model,
                description="This is another test block"
            )
            created_another_block = block_service.create_block(another_block)
            if created_another_block:
                print(f"Created another block: {created_another_block}")

                # Get the new block
                retrieved_another_block = block_service.get_block_by_id(created_another_block.block_id)
                if retrieved_another_block:
                    print(f"Retrieved another block: {retrieved_another_block}")
                else:
                    print("Failed to retrieve the created another block.")

                # Clean up: delete the second block
                if block_service.delete_block(created_another_block.block_id):
                    print("Second block deleted successfully.")
                else:
                    print("Failed to delete second block.")

                # Verify deletion of the second block
                post_delete_another_block = block_service.get_block_by_id(created_another_block.block_id)
                if post_delete_another_block:
                    print("Error: Second block still exists after deletion.")
                else:
                    print("Deletion verified: Second block no longer exists.")
            else:
                print("Failed to create another block.")
        else:
            print("Failed to create initial block.")
    except Exception as exc:
        print(f"An error occurred during the test: {str(exc)}")
        print("Traceback:")
        print(traceback.format_exc())
