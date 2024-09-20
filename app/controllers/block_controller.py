# app/controllers/block_controller.py

"""
Block Controller Module

This module defines the BlockController class responsible for managing block-related operations.
It handles both basic CRUD operations for blocks and complex workflows that may involve
multiple services or additional business logic.

Responsibilities:
- Coordinating between BlockService and AuditService to perform block-related operations.
- Managing transactions to ensure data consistency across multiple service operations.
- Handling higher-level business logic specific to blocks.

Design Philosophy:
- Maintain high cohesion by focusing solely on block-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.

Usage Example:
    from app.controllers import BlockController

    block_controller = BlockController()
    new_block = block_controller.create_block(block_data)
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from app.services import (
    BlockService,
    AuditService
)
from app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema
)
from app.logger import ConstellationLogger

class BlockController:
    """
    BlockController manages all block-related operations, coordinating between BlockService
    and AuditService to perform CRUD operations and handle complex business logic.
    """

    def __init__(self):
        """
        Initializes the BlockController with instances of BlockService and AuditService,
        along with the ConstellationLogger for logging purposes.
        """
        self.block_service = BlockService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Basic Block Operations
    # -------------------

    def create_block(self, block_data: BlockCreateSchema) -> Optional[BlockResponseSchema]:
        """
        Creates a new block.

        Args:
            block_data (BlockCreateSchema): The data required to create a new block.

        Returns:
            Optional[BlockResponseSchema]: The created block data if successful, None otherwise.
        """
        try:
            block = self.block_service.create_block(block_data)
            if block:
                # Optionally, create an audit log for the creation
                audit_log = {
                    "user_id": block_data.created_by,  # Assuming `created_by` exists in BlockCreateSchema
                    "action_type": "CREATE",
                    "entity_type": "block",
                    "entity_id": block.block_id,
                    "details": f"Block '{block.name}' created."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "BlockController",
                    "info",
                    "Block created successfully.",
                    block_id=block.block_id
                )
            return block
        except Exception as e:
            self.logger.log(
                "BlockController",
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
            block = self.block_service.get_block_by_id(block_id)
            if block:
                self.logger.log(
                    "BlockController",
                    "info",
                    "Block retrieved successfully.",
                    block_id=block.block_id
                )
            return block
        except Exception as e:
            self.logger.log(
                "BlockController",
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
            block = self.block_service.update_block(block_id, update_data)
            if block:
                # Optionally, create an audit log for the update
                audit_log = {
                    "user_id": update_data.updated_by,  # Assuming `updated_by` exists in BlockUpdateSchema
                    "action_type": "UPDATE",
                    "entity_type": "block",
                    "entity_id": block.block_id,
                    "details": f"Block '{block.name}' updated with fields: {list(update_data.dict().keys())}."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "BlockController",
                    "info",
                    "Block updated successfully.",
                    block_id=block.block_id
                )
            return block
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block update: {e}"
            )
            return None

    def delete_block(self, block_id: UUID) -> bool:
        """
        Deletes a block.

        Args:
            block_id (UUID): The UUID of the block to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            success = self.block_service.delete_block(block_id)
            if success:
                # Optionally, create an audit log for the deletion
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "DELETE",
                    "entity_type": "block",
                    "entity_id": block_id,
                    "details": f"Block with ID '{block_id}' deleted."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "BlockController",
                    "info",
                    "Block deleted successfully.",
                    block_id=block_id
                )
            return success
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block deletion: {e}"
            )
            return False

    def list_blocks(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[BlockResponseSchema]]:
        """
        Lists blocks with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the blocks.

        Returns:
            Optional[List[BlockResponseSchema]]: A list of blocks if successful, None otherwise.
        """
        try:
            blocks = self.block_service.list_blocks(filters)
            if blocks is not None:
                self.logger.log(
                    "BlockController",
                    "info",
                    f"{len(blocks)} blocks retrieved successfully.",
                    filters=filters
                )
            return blocks
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during listing blocks: {e}"
            )
            return None

    # -------------------
    # Complex Block Operations (If Any)

    def assign_version_to_block(self, block_id: UUID, version_id: UUID) -> bool:
        """
        Assigns a specific version to a block.

        Args:
            block_id (UUID): The UUID of the block.
            version_id (UUID): The UUID of the version to assign.

        Returns:
            bool: True if assignment was successful, False otherwise.
        """
        try:
            success = self.block_service.assign_version_to_block(block_id, version_id)
            if success:
                # Optionally, create an audit log for the version assignment
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "ASSIGN_VERSION",
                    "entity_type": "block",
                    "entity_id": block_id,
                    "details": f"Version '{version_id}' assigned to block '{block_id}'."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "BlockController",
                    "info",
                    "Version assigned to block successfully.",
                    block_id=block_id,
                    version_id=version_id
                )
            return success
        except Exception as e:
            self.logger.log(
                "BlockController",
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
            blocks = self.block_service.search_blocks(query)
            if blocks is not None:
                return blocks
            else:
                self.logger.log(
                    "BlockController",
                    "error",
                    "Block search failed."
                )
                return None
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block search: {e}"
            )
            return None