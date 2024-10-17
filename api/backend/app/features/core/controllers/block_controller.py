# app/features/core/controllers/block_controller.py

"""
Block Controller Module

This module defines the BlockController class responsible for managing block-related operations.
It orchestrates interactions between BlockService, TaxonomyService, and AuditService to
perform operations that involve blocks and taxonomy. Additionally, it handles
search functionalities based on taxonomy filters.

Responsibilities:
- Create, retrieve, update, and delete blocks.
- Manage taxonomy associations for blocks.
- Perform search operations based on taxonomy filters.
- Handle audit logging for all block operations.
- Ensure transactional safety and data consistency.
"""

import sys
sys.path.append("/Users/justinxiao/Downloads/coursecode/CSCI2340/constellation-backend/api")
sys.path.append("/Users/justinxiao/Downloads/coursecode/CSCI2340/constellation-backend/api/backend")

import traceback
from prisma import Prisma
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from backend.app.features.core.services.block_service import BlockService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from backend.app.features.core.services.audit_service import AuditService
from backend.app.utils.serialization_utils import align_dict_with_model  # Ensure this import is present
import asyncio
from prisma import Prisma
from backend.app.logger import ConstellationLogger
from prisma.models import AuditLog as PrismaAuditLog

class BlockController:
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        self.block_service = BlockService()
        self.taxonomy_service = TaxonomyService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    async def create_block(self, block_data: Dict[str, Any], user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Creates a new block along with its taxonomy and audit log within a transaction.

        Args:
            block_data (Dict[str, Any]): Data for creating the block.
                - name: str
                - block_type: BlockTypeEnum
                - description: str
                - taxonomy: Optional[Dict[str, Any]]
                - vector: Optional[List[float]]
            user_id (UUID): ID of the user performing the operation.

        Returns:
            Optional[Dict[str, Any]]: The created block data if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                vector = block_data.pop("vector", None)
                taxonomy = block_data.pop("taxonomy", None)

                # Step 1: Create Block
                created_block = await self.block_service.create_block(tx=tx, block_data=block_data, vector=vector)
                if not created_block:
                    raise ValueError("Failed to create block.")

                # Step 2: Create Taxonomy and associate with Block
                if taxonomy:
                    taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(
                        tx,
                        UUID(created_block.block_id),
                        taxonomy,
                    )
                    if not taxonomy_success:
                        raise ValueError("Failed to create taxonomy for block.")

                # Step 3: Audit Logging
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "CREATE",
                    "entity_type": "block",  # Should be lowercase as per Prisma enum
                    "entity_id": str(created_block.block_id),
                    "details": {"block_name": block_data["name"]}
                    # Removed 'users' field
                }
                # Align the audit_log without relation fields
                # aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for block creation")

                return created_block.dict()

        except Exception as e:
            print(f"An error occurred during block creation: {e}")
            import traceback
            print(traceback.format_exc())
            return None

    async def get_block_by_id(self, block_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves a block by its ID.

        Args:
            block_id (UUID): UUID of the block to retrieve.
            user_id (UUID): UUID of the user performing the operation.

        Returns:
            Optional[Dict[str, Any]]: The retrieved block data if found, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                block = await self.block_service.get_block_by_id(tx=tx, block_id=block_id)
                if block:
                    return block.dict()
                else:
                    print(f"Block with ID {block_id} not found.")
                    return None
        except Exception as e:
            print(f"An error occurred during block retrieval: {e}")
            print(traceback.format_exc())
            return None

    async def update_block(self, block_id: UUID, update_data: Dict[str, Any], user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Updates an existing block's details and taxonomy within a transaction.

        Args:
            block_id (UUID): UUID of the block to update.
            update_data (Dict[str, Any]): Data to update the block.
                - name: str
                - block_type: BlockTypeEnum
                - description: str
                - taxonomy: Optional[Dict[str, Any]]
                - vector: Optional[List[float]]
            user_id (UUID): UUID of the user performing the update.

        Returns:
            Optional[Dict[str, Any]]: The updated block data if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                vector = update_data.pop('vector', None)
                taxonomy = update_data.pop('taxonomy', None)

                # Step 1: Update Block
                updated_block = await self.block_service.update_block(tx=tx, block_id=block_id, update_data=update_data.copy(), vector=vector)
                if not updated_block:
                    raise ValueError("Failed to update block.")

                # Step 2: Update Taxonomy if provided
                if taxonomy:
                    taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(
                        tx,
                        block_id,
                        taxonomy,
                    )
                    if not taxonomy_success:
                        raise ValueError("Failed to update taxonomy for block.")

                # Step 3: Audit Logging
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "UPDATE",
                    "entity_type": "block",  # Should be lowercase as per Prisma enum
                    "entity_id": str(block_id),
                    "details": {"updated_fields": update_data.copy()}
                    # Removed 'users' field
                }
                self.logger.log("BlockController", "info", "Audit log data is valid.", extra={"update_block audit_log": audit_log})
                # Align the audit_log without relation fields
                # aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for block update")

                return updated_block.dict()

        except Exception as e:
            print(f"An error occurred during block update: {e}")
            import traceback
            print(traceback.format_exc())
            return None

    async def delete_block(self, block_id: UUID, user_id: UUID) -> bool:
        """
        Deletes a block along with its taxonomy associations and audit log within a transaction.

        Args:
            block_id (UUID): UUID of the block to delete.
            user_id (UUID): UUID of the user performing the deletion.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Delete Block
                deletion_success = await self.block_service.delete_block(tx=tx, block_id=block_id)
                if not deletion_success:
                    raise ValueError("Failed to delete block.")

                # Step 2: Audit Logging
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "DELETE",
                    "entity_type": "block",  # Should be lowercase as per Prisma enum
                    "entity_id": str(block_id),
                    "details": {"block_id": str(block_id)}
                    # Removed 'users' field
                }
                # Align the audit_log without relation fields
                # aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for block deletion")

                return True
        except Exception as e:
            print(f"An error occurred during block deletion: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    async def search_blocks(self, search_filters: Dict[str, Any], user_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """
        Wrapper method to perform search and handle audit logging.

        Args:
            search_filters (Dict[str, Any]): Filters for searching blocks.
            user_id (UUID): UUID of the user performing the search.

        Returns:
            Optional[List[Dict[str, Any]]]: List of matching blocks, or None if an error occurs.
        """
        try:
            async with self.prisma.tx() as tx:
                blocks = await self.taxonomy_service.search_blocks(tx, search_filters)
                if blocks is None:
                    raise Exception("Failed to search blocks with the provided filters")

                # Audit Logging for Search
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "READ",  # Use 'READ' for searches
                    "entity_type": "block",  # If 'block_search' is not in enum, use 'block'
                    "entity_id": blocks[0].block_id,  # TODO: temporary using first block id
                    "details": {
                        "search_filters": search_filters,
                        "results_count": len(blocks)
                    }
                    # Removed 'users' field
                }
                # Align the audit_log without relation fields
                # aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for block search")

                return [block.dict() for block in blocks]
        except Exception as e:
            print(f"An error occurred during search blocks: {e}")
            import traceback
            print(traceback.format_exc())
            return None

# -------------------
# Testing Utility
# -------------------

async def main():
    """
    Main function to test the BlockController functionality with correct schemas and taxonomies.
    """
    print("Starting BlockController test...")
    prisma = Prisma()
    await prisma.connect()
    print("Connected to database.")
    controller = BlockController(prisma)

    user_id = UUID('123e4567-e89b-12d3-a456-426614174000')  # Example user ID
    print(f"Using test user ID: {user_id}")

    try:
        # Step 1: Create a new block (Earth Observation Model)
        print("\nStep 1: Creating a new Earth Observation Model block...")
        create_schema = {
            "name": "EarthObservationModelExample",
            "block_type": "model",  # Ensure this matches the enum in Prisma
            "description": "An example Earth Observation model for testing.",
            # "created_by": user_id,  # This is added in the create_block method
            "taxonomy": {
                "general": {
                    "categories": [
                        {"name": "Climate Data"},
                        {"name": "Geospatial Analysis"}
                    ]
                },
                "specific": {
                    "categories": [
                        {"name": "Satellite Imagery", "parent_name": "Climate Data"},
                        {"name": "Data Processing", "parent_name": "Geospatial Analysis"}
                    ]
                }
            }
            # "metadata": {  # Removed as it's not part of the Prisma schema
            #     "vector": [0.1] * 512  # Example 512-dimensional vector
            # }
        }
        created_block = await controller.create_block(create_schema, user_id)
        if created_block:
            print(f"Block Created: {created_block}")
        else:
            print("Block creation failed.")

        # Step 2: Retrieve the created block
        if created_block:
            print("\nStep 2: Retrieving the created block...")
            retrieved_block = await controller.get_block_by_id(created_block['block_id'], user_id)
            if retrieved_block:
                print(f"Block Retrieved: {retrieved_block['block_id']}, Name: {retrieved_block['name']}")
                # print(f"Taxonomy: {retrieved_block['taxonomy']}")
            else:
                print("Block retrieval failed.")

        # Step 3: Update the block's name and taxonomy (to Weather/Climate Model)
        if created_block:
            print("\nStep 3: Updating the block to a Weather/Climate Model...")
            update_schema = {
                "name": "UpdatedWeatherClimateModelExample",
                "taxonomy": {
                    "general": {
                        "categories": [
                            {"name": "Climate Data"},
                            {"name": "Meteorological Analysis"}
                        ]
                    },
                    "specific": {
                        "categories": [
                            {"name": "Climate Modeling", "parent_name": "Climate Data"},
                            {"name": "Weather Forecasting", "parent_name": "Meteorological Analysis"}
                        ]
                    }
                }
            }
            updated_block = await controller.update_block(created_block['block_id'], update_schema, user_id)
            if updated_block:
                print(f"Block Updated: {updated_block['block_id']}, New Name: {updated_block['name']}")
                # print(f"Updated Taxonomy: {updated_block['taxonomy']}")
            else:
                print("Block update failed.")

        # Step 4: Perform a search based on taxonomy filters
        print("\nStep 4: Performing a search for blocks with 'Climate Data' category and block type 'model'...")
        search_filters = {
            "category_names": ["Climate Data"],
            "block_types": ["model"]
        }
        search_results = await controller.search_blocks(search_filters, user_id)
        if search_results:
            print(f"Found {len(search_results)} block(s):")
            for blk in search_results:
                print(f"- Block ID: {blk['block_id']}, Name: {blk['name']}, Type: {blk['block_type']}")
        else:
            print("No blocks found matching the search criteria.")

        # Step 5: Delete the block
        if created_block:
            print("\nStep 5: Deleting the created block...")
            deletion_success = await controller.delete_block(created_block['block_id'], user_id)
            if deletion_success:
                print(f"Block Deleted: {created_block['block_id']}")
            else:
                print("Block deletion failed.")
    except Exception as e:
        print(f"An error occurred during the test: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        print("\nDisconnecting from database...")
        await prisma.disconnect()
        print("Test completed.")

if __name__ == "__main__":
    asyncio.run(main())