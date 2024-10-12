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
from backend.app.logger import ConstellationLogger
from backend.app.database import database
from backend.app.utils.serialization_utils import align_dict_with_model  # Ensure this import is present
import asyncio


class BlockController:
    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        self.block_service = BlockService()
        self.taxonomy_service = TaxonomyService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger().get_logger("BlockController")

    async def create_block(self, block_data: Dict[str, Any], user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Creates a new block along with its taxonomy and audit log within a transaction.

        Args:
            block_data (Dict[str, Any]): Data for creating the block.
            user_id (UUID): ID of the user performing the operation.

        Returns:
            Optional[Dict[str, Any]]: The created block data if successful, None otherwise.
        """
        async with self.prisma.tx() as transaction:
            try:
                block_data['created_by'] = str(user_id)
                block_data.pop('metadata', None)  # Removed 'metadata' as it's not in Prisma schema

                # Step 1: Create Block
                created_block = await self.block_service.create_block(block_data, transaction)
                if not created_block:
                    raise ValueError("Failed to create block.")

                # Step 2: Create Taxonomy and associate with Block
                if "taxonomy" in block_data:
                    taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(
                        UUID(created_block["block_id"]),
                        block_data["taxonomy"],
                        transaction=transaction
                    )
                    if not taxonomy_success:
                        raise ValueError("Failed to create taxonomy for block.")

                # Step 3: Audit Logging
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "CREATE",
                    "entity_type": "block",  # Should be lowercase as per Prisma enum
                    "entity_id": str(created_block["block_id"]),
                    "details": {"block_name": block_data["name"]}
                    # Removed 'users' field
                }
                # Align the audit_log without relation fields
                aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                await self.audit_service.create_audit_log(aligned_audit_log, transaction=transaction)

                return created_block

            except Exception as e:
                print(f"An error occurred during block creation: {e}")
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
            block = await self.block_service.get_block_by_id(block_id)
            if block:
                return block
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
            user_id (UUID): UUID of the user performing the update.

        Returns:
            Optional[Dict[str, Any]]: The updated block data if successful, None otherwise.
        """
        async with self.prisma.tx() as transaction:
            try:
                update_data.pop('metadata', None)  # Removed 'metadata' as it's not in Prisma schema

                # Step 1: Update Block
                updated_block = await self.block_service.update_block(block_id, update_data, transaction)
                if not updated_block:
                    raise ValueError("Failed to update block.")

                # Step 2: Update Taxonomy if provided
                if "taxonomy" in update_data:
                    taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(
                        block_id,
                        update_data["taxonomy"],
                        transaction=transaction
                    )
                    if not taxonomy_success:
                        raise ValueError("Failed to update taxonomy for block.")

                # Step 3: Audit Logging
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "UPDATE",
                    "entity_type": "block",  # Should be lowercase as per Prisma enum
                    "entity_id": str(block_id),
                    "details": {"updated_fields": update_data}
                    # Removed 'users' field
                }
                # Align the audit_log without relation fields
                aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                await self.audit_service.create_audit_log(aligned_audit_log, transaction=transaction)

                return updated_block

            except Exception as e:
                print(f"An error occurred during block update: {e}")
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
        async with self.prisma.tx() as transaction:
            try:
                # Step 1: Delete Block
                deletion_success = await self.block_service.delete_block(block_id, transaction)
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
                aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                await self.audit_service.create_audit_log(aligned_audit_log, transaction=transaction)

                return True
            except Exception as e:
                print(f"An error occurred during block deletion: {e}")
                print(traceback.format_exc())
                return False

    async def search_blocks(self, search_filters: Dict[str, Any], user_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """
        Searches for blocks based on taxonomy filters.

        Args:
            search_filters (Dict[str, Any]): Filters including 'category_names' and 'block_types'.
            user_id (UUID): UUID of the user performing the search.

        Returns:
            Optional[List[Dict[str, Any]]]: List of blocks matching the search criteria, or None if an error occurs.
        """
        try:
            blocks = await self.taxonomy_service.search_blocks(search_filters)
            if blocks is not None:
                return blocks
            else:
                print("No blocks found matching the search criteria.")
                return []
        except Exception as e:
            print(f"An error occurred during block search: {e}")
            import traceback
            print(traceback.format_exc())
            return None

    async def perform_search(self, search_filters: Dict[str, Any], user_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """
        Wrapper method to perform search and handle audit logging.

        Args:
            search_filters (Dict[str, Any]): Filters for searching blocks.
            user_id (UUID): UUID of the user performing the search.

        Returns:
            Optional[List[Dict[str, Any]]]: List of matching blocks, or None if an error occurs.
        """
        try:
            search_results = await self.search_blocks(search_filters, user_id)
            if search_results is not None:
                # Audit Logging for Search
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "READ",  # Use 'READ' for searches
                    "entity_type": "block",  # If 'block_search' is not in enum, use 'block'
                    "entity_id": str(uuid4()),  # Consider revising if needed
                    "details": {
                        "search_filters": search_filters,
                        "results_count": len(search_results)
                    }
                    # Removed 'users' field
                }
                # Align the audit_log without relation fields
                await self.audit_service.create_audit_log(audit_log)
                return search_results
            else:
                return None
        except Exception as e:
            print(f"An error occurred during perform_search: {e}")
            print(traceback.format_exc())
            return None
        
    async def perform_similarity_search(self, query: List[float], top_k: int, user_id: UUID) -> Optional[List[Dict[str, Any]]]:
        """
        Performs a similarity search based on a query vector.

        Args:
            query (List[float]): Query vector for similarity search.
            top_k (int): Number of results to return.
            user_id (UUID): UUID of the user performing the search.

        Returns:
            Optional[List[Dict[str, Any]]]: List of blocks matching the search criteria, or None if an error occurs.
        """
        try:
            blocks = await self.block_service.search_blocks_by_vector_similarity(query, top_k)
            
            # Audit Logging for Similarity Search
            audit_log = {
                "user_id": str(user_id),
                "action_type": "READ",
                "entity_type": "block",
                "entity_id": str(uuid4()),
                "details": {
                    "top_k": top_k,
                    "results_count": len(blocks) if blocks is not None else 0
                }
            }
            await self.audit_service.create_audit_log(audit_log)

            return blocks if blocks is not None else []
        except Exception as e:
            print(f"An error occurred during similarity search: {e}")
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
    await database.prisma.connect()
    print("Connected to database.")
    controller = BlockController(database.prisma)

    user_id = UUID('12345678-1234-5678-1234-567812345678')  # Example user ID
    print(f"Using test user ID: {user_id}")

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
        print(f"Block Created: {created_block['block_id']}")
    else:
        print("Block creation failed.")

    # Step 2: Retrieve the created block
    if created_block:
        print("\nStep 2: Retrieving the created block...")
        retrieved_block = await controller.get_block_by_id(created_block['block_id'], user_id)
        if retrieved_block:
            print(f"Block Retrieved: {retrieved_block['block_id']}, Name: {retrieved_block['name']}")
            print(f"Taxonomy: {retrieved_block['taxonomy']}")
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
            # "metadata": {  # Removed as it's not part of the Prisma schema
            #     "vector": [0.2] * 512
            # }
        }
        updated_block = await controller.update_block(created_block['block_id'], update_schema, user_id)
        if updated_block:
            print(f"Block Updated: {updated_block['block_id']}, New Name: {updated_block['name']}")
            print(f"Updated Taxonomy: {updated_block['taxonomy']}")
        else:
            print("Block update failed.")

    # Step 4: Perform a search based on taxonomy filters
    print("\nStep 4: Performing a search for blocks with 'Climate Data' category and block type 'model'...")
    search_filters = {
        "category_names": ["Climate Data"],
        "block_types": ["model"]
    }
    search_results = await controller.perform_search(search_filters, user_id)
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

    # Step 6: Perform a similarity search
    print("\nStep 6: Performing a similarity search...")
    query = [0.1] * 512  # Example query vector
    top_k = 5  # Number of results to return
    similarity_results = await controller.perform_similarity_search(query, top_k, user_id)
    if similarity_results is not None:
        print(f"Found {len(similarity_results)} similar block(s):")
        for blk in similarity_results:
            print(f"- Block ID: {blk['block_id']}, Name: {blk['name']}, Type: {blk['block_type']}")
    else:
        print("Error happened during similarity search.")

    print("\nDisconnecting from database...")
    await database.prisma.disconnect()
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(main())