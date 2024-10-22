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

from prisma import Prisma
from uuid import UUID
from typing import Optional, List, Dict, Any
from backend.app.features.core.services.block_service import BlockService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from backend.app.features.core.services.audit_service import AuditService
from backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from backend.app.utils.serialization_utils import align_dict_with_model  # Ensure this import is present
import asyncio
from prisma import Prisma
from backend.app.logger import ConstellationLogger
from prisma.models import AuditLog as PrismaAuditLog

class BlockController:
    def __init__(self, prisma: Prisma, api_key: Optional[str] = None):
        self.prisma = prisma
        self.block_service = BlockService()
        self.taxonomy_service = TaxonomyService()
        self.audit_service = AuditService()
        self.vector_embedding_service = VectorEmbeddingService(api_key)
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
                - text_to_vector: Optional[string] for vectorization
            user_id (UUID): ID of the user performing the operation.

        Returns:
            Optional[Dict[str, Any]]: The created block data if successful, None otherwise.
        """
        try:
            # Step 0: Generate vector embedding if given text_to_vector
            # generate embedding outside the transaction to avoid transaction timeout.
            text_to_vector = block_data.pop("text_to_vector", None)
            vector = None
            if text_to_vector:
                vector = await self.vector_embedding_service.generate_text_embedding(text_to_vector)
                self.logger.log("BlockController", "info", f"Vector length: {len(vector)}")

            async with self.prisma.tx(timeout=10000) as tx:
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
            import traceback
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
                - text_to_vector: Optional[List[float]] for vectorization
            user_id (UUID): UUID of the user performing the update.

        Returns:
            Optional[Dict[str, Any]]: The updated block data if successful, None otherwise.
        """
        try:
            # Step 0: Generate vector embedding if given `text_to_vector` in `update_data`
            # generate embedding outside the transaction to avoid transaction timeout.
            text_to_vector = update_data.pop("text_to_vector", None)
            vector = None
            if text_to_vector:
                vector = await self.vector_embedding_service.generate_text_embedding(text_to_vector)

            async with self.prisma.tx() as tx:
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
                    "entity_id": blocks[0].block_id if blocks else str(UUID(int=0)),  # TODO: temporary using first block id
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

    async def search_blocks_by_vector_similarity(self, query: str, user_id: UUID, top_k: int=5) -> Optional[List[Dict[str, Any]]]:
        try:
            # Step 1: generate vector embedding for the query
            query_vector = await self.vector_embedding_service.generate_text_embedding(query)
            if not query_vector:
                raise ValueError("Failed to generate vector for the query.")

            async with self.prisma.tx() as tx:
                # Step 2: Call block service
                blocks = await self.block_service.search_blocks_by_vector_similarity(tx, query_vector, top_k=top_k)

                if blocks is None:
                    raise Exception("Failed to search blocks with the provided vector")

                # Audit Logging for Search by vector
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "READ",  # Use 'READ' for searches
                    "entity_type": "block",  # If 'block_search' is not in enum, use 'block'
                    "entity_id": blocks[0]["id"] if blocks else str(UUID(int=0)),  # TODO: temporary using first block id
                    "details": {
                        "results_count": len(blocks)
                    }
                    # Removed 'users' field
                }
                # Align the audit_log without relation fields
                # aligned_audit_log = align_dict_with_model(audit_log, PrismaAuditLog)
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for block search by vector")
                
                return blocks
        except Exception as e:
            print(f"An error occurred during search blocks by vector similarity: {e}")
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

    user_id = UUID('36906826-9558-4631-b4a6-c34d6109856d')  # Example user ID
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
            },
            "text_to_vector": "In certain parts of the world, like the Maldives, Puerto Rico, and San Diego, you can witness the phenomenon of bioluminescent waves."
            # "metadata": {  # Removed as it's not part of the Prisma schema
            #     "vector": [0.1] * 512  # Example 512-dimensional vector
            # }
        }
        created_block = await controller.create_block(create_schema, user_id)
        if created_block:
            print(f"Block Created: {created_block}")
        else:
            print("Block creation failed.")

        # Step 1.5: Create a second block for testing search by vector similarity
        create_schema = {
            "name": "WildfireDataset",
            "block_type": "dataset",  # Ensure this matches the enum in Prisma
            "description": "An example dataset on wildfire for testing",
            # "created_by": user_id,  # This is added in the create_block method
            "taxonomy": {
                "general": {
                    "categories": [
                        {"name": "Climate Data"},
                        {"name": "Forest Analysis"}
                    ]
                },
                "specific": {
                    "categories": [
                        {"name": "Satellite Imagery", "parent_name": "Climate Data"},
                        {"name": "Forest Data", "parent_name": "Forest Analysis"}
                    ]
                }
            },
            "text_to_vector": "Elephants have been observed to behave in a way that indicates a high level of self-awareness, such as recognizing themselves in mirrors."
            # "metadata": {  # Removed as it's not part of the Prisma schema
            #     "vector": [0.1] * 512  # Example 512-dimensional vector
            # }
        }
        created_block2 = await controller.create_block(create_schema, user_id)
        if created_block2:
            print(f"Block Created: {created_block2}")
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
        
        if created_block:
            block_service = BlockService()
            vector = await block_service.get_block_vector(prisma, created_block["block_id"])
            if vector:
                print(f"Vector: {vector[0:5]}... (truncated)")
            else:
                print("Vector retrieval failed")

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
                },
                "text_to_vector": "There are over 7,000 languages spoken around the world today."
            }
            updated_block = await controller.update_block(created_block['block_id'], update_schema, user_id)
            if updated_block:
                print(f"Block Updated: {updated_block['block_id']}, New Name: {updated_block['name']}, New vector: {updated_block.get("vector")}")
                # print(f"Updated Taxonomy: {updated_block['taxonomy']}")
            else:
                print("Block update failed.")

            if updated_block:
                block_service = BlockService()
                vector = await block_service.get_block_vector(prisma, updated_block["block_id"])
                if vector:
                    print(f"Vector: {vector[0:5]}... (truncated)")
                else:
                    print("Vector retrieval failed")

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

        # Step 5: Perform a serach based on vector similarity
        print("\nStep 5: Performing a serach based on vector similarity...")
        query = "language"
        vector_search_results = await controller.search_blocks_by_vector_similarity(query, user_id, top_k=5)
        if vector_search_results:
            print(f"Found {len(vector_search_results)} block(s):")
            for blk in vector_search_results:
                print(f"block id: {blk["id"]}, similarity score: {blk["score"]}")
        else:
            print("No blocks found. Should not happen")

        # Step 6: Delete the blocks
        if created_block:
            print("\nStep 5: Deleting the created block...")
            deletion_success = await controller.delete_block(created_block['block_id'], user_id)
            if deletion_success:
                print(f"Block Deleted: {created_block['block_id']}")
            else:
                print("Block deletion failed.")
        if created_block2:
            deletion_success = await controller.delete_block(created_block2['block_id'], user_id)
            if deletion_success:
                print(f"Block Deleted: {created_block2['block_id']}")
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