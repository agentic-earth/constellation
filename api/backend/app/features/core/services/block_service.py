"""
Block Service Module

This module implements the Block Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The BlockService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (PrismaBlock) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. No Request/Response Models: We directly use dictionaries for input and Prisma models for output.
   This simplifies the API and reduces redundancy, as Prisma models already provide necessary structure.

4. JSON Handling: We manually convert the 'metadata' and 'taxonomy' fields to and from JSON strings.
   This ensures compatibility with Prisma's JSON field type.

5. Error Handling: Exceptions are allowed to propagate, to be handled by the caller.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for block operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import json

from prisma.models import blocks as PrismaBlock
from backend.app.database import database
from backend.app.features.core.services.taxonomy_service import TaxonomyService

class BlockService:
    def __init__(self):
        self.prisma = database.prisma
        self.taxonomy_service = TaxonomyService()

    async def create_block(self, block_data: Dict[str, Any]) -> Optional[PrismaBlock]:
        """
        Create a new block.

        Args:
            block_data (Dict[str, Any]): Dictionary containing block data.

        Returns:
            Optional[PrismaBlock]: The created block, or None if creation failed.
        """
        create_data = {
            "block_id": str(uuid4()),
            "name": block_data["name"],
            "block_type": block_data["block_type"],
            "description": block_data.get("description"),
            "created_by": str(block_data["created_by"]),
            "metadata": json.dumps(block_data.get("metadata", {})),
            "taxonomy": json.dumps(block_data.get("taxonomy", {})),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        block = await self.prisma.blocks.create(data=create_data)
        
        if block_data.get("taxonomy"):
            await self.taxonomy_service.create_taxonomy_for_block(UUID(block.block_id), block_data["taxonomy"])
        
        return block

    async def get_block_by_id(self, block_id: UUID) -> Optional[PrismaBlock]:
        """
        Retrieve a block by its ID.

        Args:
            block_id (UUID): The ID of the block to retrieve.

        Returns:
            Optional[PrismaBlock]: The retrieved block, or None if not found.
        """
        return await self.prisma.blocks.find_unique(
            where={"block_id": str(block_id)},
            include={"block_categories": {"include": {"categories": True}}}
        )

    async def update_block(self, block_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaBlock]:
        """
        Update an existing block.

        Args:
            block_id (UUID): The ID of the block to update.
            update_data (Dict[str, Any]): Dictionary containing updated block data.

        Returns:
            Optional[PrismaBlock]: The updated block, or None if update failed.
        """
        update_dict = {
            "name": update_data.get("name"),
            "block_type": update_data.get("block_type"),
            "description": update_data.get("description"),
            "updated_by": update_data.get("updated_by"),
            "metadata": json.dumps(update_data.get("metadata", {})),
            "taxonomy": json.dumps(update_data.get("taxonomy", {})),
            "updated_at": datetime.utcnow(),
        }
        update_dict = {k: v for k, v in update_dict.items() if v is not None}

        block = await self.prisma.blocks.update(
            where={"block_id": str(block_id)},
            data=update_dict,
            include={"block_categories": {"include": {"categories": True}}}
        )
        
        if update_data.get("taxonomy"):
            await self.prisma.block_categories.delete_many(where={"block_id": str(block_id)})
            await self.taxonomy_service.create_taxonomy_for_block(block_id, update_data["taxonomy"])
        
        return block

    async def delete_block(self, block_id: UUID) -> bool:
        """
        Delete a block.

        Args:
            block_id (UUID): The ID of the block to delete.

        Returns:
            bool: True if the block was successfully deleted, False otherwise.
        """
        deleted_block = await self.prisma.blocks.delete(where={"block_id": str(block_id)})
        return deleted_block is not None

    async def get_blocks_by_ids(self, block_ids: List[UUID]) -> List[PrismaBlock]:
        """
        Retrieve multiple blocks by their IDs.

        Args:
            block_ids (List[UUID]): List of block IDs to retrieve.

        Returns:
            List[PrismaBlock]: List of retrieved blocks.
        """
        return await self.prisma.blocks.find_many(
            where={"block_id": {"in": [str(bid) for bid in block_ids]}},
            include={"block_categories": {"include": {"categories": True}}}
        )

    async def list_all_blocks(self) -> List[PrismaBlock]:
        """
        List all blocks.

        Returns:
            List[PrismaBlock]: List of all blocks.
        """
        return await self.prisma.blocks.find_many(
            include={"block_categories": {"include": {"categories": True}}}
        )

    async def search_blocks_by_taxonomy(self, taxonomy_query: Dict[str, Any]) -> List[PrismaBlock]:
        """
        Search blocks by taxonomy.

        Args:
            taxonomy_query (Dict[str, Any]): Dictionary containing taxonomy search criteria.

        Returns:
            List[PrismaBlock]: List of blocks matching the taxonomy criteria.
        """
        block_ids = await self.taxonomy_service.search_blocks_by_taxonomy_query(taxonomy_query)
        if not block_ids:
            return []
        return await self.prisma.blocks.find_many(
            where={"block_id": {"in": [str(bid) for bid in block_ids]}},
            include={"block_categories": {"include": {"categories": True}}}
        )
        

async def main():
    """
    Main function to demonstrate and test the BlockService functionality.
    """
    print("Starting BlockService test...")

    print("Connecting to the database...")
    await database.connect()
    print("Database connected successfully.")

    block_service = BlockService()

    # Use this user ID for testing
    test_user_id = "11111111-1111-1111-1111-111111111111"

    try:
        # Create a new block
        print("\nCreating a new block...")
        new_block_data = {
            "name": "Test Block",
            "block_type": "text",
            "description": "This is a test block",
            "created_by": test_user_id,
            "metadata": {"key": "value"},
            "taxonomy": {"category": "test"}
        }
        created_block = await block_service.create_block(new_block_data)
        print(f"Created block: {created_block}")

        if created_block:
            # Get the created block
            print(f"\nRetrieving block with ID: {created_block.block_id}")
            retrieved_block = await block_service.get_block_by_id(UUID(created_block.block_id))
            print(f"Retrieved block: {retrieved_block}")

            # Update the block
            print(f"\nUpdating block with ID: {created_block.block_id}")
            update_data = {
                "name": "Updated Test Block",
                "description": "This is an updated test block",
                "updated_by": test_user_id,
                "metadata": {"new_key": "new_value"},
                "taxonomy": {"new_category": "updated_test"}
            }
            updated_block = await block_service.update_block(UUID(created_block.block_id), update_data)
            print(f"Updated block: {updated_block}")

            # List all blocks
            print("\nListing all blocks...")
            all_blocks = await block_service.list_all_blocks()
            print(f"Total blocks: {len(all_blocks)}")
            for block in all_blocks:
                print(f"- Block ID: {block.block_id}, Name: {block.name}")

            # Search blocks by taxonomy
            print("\nSearching blocks by taxonomy...")
            taxonomy_query = {"new_category": "updated_test"}
            found_blocks = await block_service.search_blocks_by_taxonomy(taxonomy_query)
            print(f"Found {len(found_blocks)} blocks matching the taxonomy query")

            # Delete the block
            print(f"\nDeleting block with ID: {created_block.block_id}")
            deleted = await block_service.delete_block(UUID(created_block.block_id))
            print(f"Block deleted: {deleted}")

        # List all blocks after operations
        print("\nListing all blocks after operations...")
        remaining_blocks = await block_service.list_all_blocks()
        print(f"Remaining blocks: {len(remaining_blocks)}")
        for block in remaining_blocks:
            print(f"- Block ID: {block.block_id}, Name: {block.name}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())

    finally:
        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

if __name__ == "__main__":
    asyncio.run(main())