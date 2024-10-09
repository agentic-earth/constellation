# constellation-backend/api/backend/app/features/core/services/taxonomy_service.py

"""
Taxonomy Service Module

This module implements the Taxonomy Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The TaxonomyService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (Category, BlockCategory, Block) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. Nested Taxonomy Handling: The service automatically parses nested taxonomy objects into categories, enabling deep taxonomy associations.

4. Transaction Management: Utilizes Prisma's interactive transactions to ensure ACID properties during complex operations.

5. Error Handling: Comprehensive error handling to manage exceptions and ensure data consistency.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for taxonomy operations.
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4
from prisma import Prisma
from prisma.models import Category as PrismaCategory, BlockCategory as PrismaBlockCategory, Block as PrismaBlock
from prisma.errors import UniqueViolationError
from backend.app.database import database
from backend.app.logger import ConstellationLogger
import asyncio
from datetime import datetime

class TaxonomyService:
    def __init__(self):
        self.prisma = database.prisma
        self.logger = ConstellationLogger()

    async def create_category(self, category_data: Dict[str, Any], transaction: Optional[Prisma] = None) -> Optional[PrismaCategory]:
        """
        Creates a new category, optionally with a parent category.

        Args:
            category_data (Dict[str, Any]): Data for creating the category.
                Expected keys: 'name', optional 'parent_id'.
            transaction (Optional[Prisma]): Prisma transaction instance.

        Returns:
            Optional[PrismaCategory]: The created category if successful, None otherwise.
        """
        try:
            prisma_instance = transaction or self.prisma
            created_category = await prisma_instance.category.create(
                data={
                    "name": category_data["name"],
                    "parent_id": str(category_data["parent_id"]) if category_data.get("parent_id") else None
                }
            )
            self.logger.log(
                "TaxonomyService",
                "info",
                "Category created successfully",
                category_id=created_category.category_id,
                category_name=created_category.name
            )
            return created_category
        except UniqueViolationError:
            # Category with this name and parent_id already exists, retrieve it
            existing_category = await self.get_category_by_name_and_parent(
                category_data["name"],
                category_data.get("parent_id")
            )
            if existing_category:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    "Category already exists, retrieved existing category.",
                    category_id=existing_category.category_id,
                    category_name=existing_category.name
                )
                return existing_category
            else:
                raise ValueError(f"Failed to create or retrieve category with name: {category_data['name']}")
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to create category", error=str(e))
            return None

    async def get_category_by_id(self, category_id: UUID, transaction: Optional[Prisma] = None) -> Optional[PrismaCategory]:
        """
        Retrieves a category by its ID, including its children.

        Args:
            category_id (UUID): The UUID of the category to retrieve.
            transaction (Optional[Prisma]): Prisma transaction instance.

        Returns:
            Optional[PrismaCategory]: The retrieved category if found, None otherwise.
        """
        try:
            prisma_instance = transaction or self.prisma
            category = await prisma_instance.category.find_unique(
                where={"category_id": str(category_id)},
                include={"children": True}
            )
            if category:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    "Category retrieved successfully",
                    category_id=category.category_id,
                    category_name=category.name
                )
            else:
                self.logger.log(
                    "TaxonomyService",
                    "warning",
                    "Category not found",
                    category_id=str(category_id)
                )
            return category
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to retrieve category by ID", error=str(e))
            return None

    async def get_category_by_name_and_parent(self, name: str, parent_id: Optional[UUID]) -> Optional[PrismaCategory]:
        """
        Retrieves a category by its name and parent_id.

        Args:
            name (str): The name of the category.
            parent_id (Optional[UUID]): The UUID of the parent category, if any.

        Returns:
            Optional[PrismaCategory]: The retrieved category if found, None otherwise.
        """
        try:
            category = await self.prisma.category.find_unique(
                where={"name_parent_id": {"name": name, "parent_id": str(parent_id) if parent_id else None}}
            )
            return category
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to retrieve category by name and parent_id", error=str(e))
            return None

    async def update_category(self, category_id: UUID, update_data: Dict[str, Any], transaction: Optional[Prisma] = None) -> Optional[PrismaCategory]:
        """
        Updates an existing category's details.

        Args:
            category_id (UUID): The UUID of the category to update.
            update_data (Dict[str, Any]): Data to update. Allowed keys: 'name', 'parent_id'.
            transaction (Optional[Prisma]): Prisma transaction instance.

        Returns:
            Optional[PrismaCategory]: The updated category if successful, None otherwise.
        """
        try:
            prisma_instance = transaction or self.prisma
            data_to_update = {}
            if "name" in update_data:
                data_to_update["name"] = update_data["name"]
            if "parent_id" in update_data:
                data_to_update["parent_id"] = str(update_data["parent_id"]) if update_data["parent_id"] else None

            updated_category = await prisma_instance.category.update(
                where={"category_id": str(category_id)},
                data=data_to_update
            )
            self.logger.log(
                "TaxonomyService",
                "info",
                "Category updated successfully",
                category_id=updated_category.category_id,
                updated_fields=list(data_to_update.keys())
            )
            return updated_category
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to update category", error=str(e))
            return None

    async def delete_category(self, category_id: UUID, transaction: Optional[Prisma] = None) -> bool:
        """
        Deletes a category by its ID.

        Args:
            category_id (UUID): The UUID of the category to delete.
            transaction (Optional[Prisma]): Prisma transaction instance.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            prisma_instance = transaction or self.prisma
            await prisma_instance.category.delete(
                where={"category_id": str(category_id)}
            )
            self.logger.log(
                "TaxonomyService",
                "info",
                "Category deleted successfully",
                category_id=str(category_id)
            )
            return True
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to delete category", error=str(e))
            return False

    async def associate_block_with_categories(self, block_id: UUID, category_ids: List[UUID], transaction: Optional[Prisma] = None) -> bool:
        """
        Associates a block with multiple categories.

        Args:
            block_id (UUID): The UUID of the block.
            category_ids (List[UUID]): A list of category UUIDs to associate with the block.
            transaction (Optional[Prisma]): Prisma transaction instance.

        Returns:
            bool: True if associations were successful, False otherwise.
        """
        try:
            prisma_instance = transaction or self.prisma
            block_categories_data = [
                {"block_id": str(block_id), "category_id": str(cat_id)}
                for cat_id in category_ids
            ]
            await prisma_instance.block_category.create_many(
                data=block_categories_data,
                skip_duplicates=True  # Prevent errors if association already exists
            )
            self.logger.log(
                "TaxonomyService",
                "info",
                "Block associated with categories successfully",
                block_id=str(block_id),
                category_ids=[str(cat_id) for cat_id in category_ids]
            )
            return True
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to associate block with categories", error=str(e))
            return False

    async def dissociate_block_from_categories(self, block_id: UUID, category_ids: List[UUID], transaction: Optional[Prisma] = None) -> bool:
        """
        Dissociates a block from multiple categories.

        Args:
            block_id (UUID): The UUID of the block.
            category_ids (List[UUID]): A list of category UUIDs to dissociate from the block.
            transaction (Optional[Prisma]): Prisma transaction instance.

        Returns:
            bool: True if dissociations were successful, False otherwise.
        """
        try:
            prisma_instance = transaction or self.prisma
            for cat_id in category_ids:
                await prisma_instance.block_category.delete_many(
                    where={
                        "block_id": str(block_id),
                        "category_id": str(cat_id)
                    }
                )
            self.logger.log(
                "TaxonomyService",
                "info",
                "Block dissociated from categories successfully",
                block_id=str(block_id),
                category_ids=[str(cat_id) for cat_id in category_ids]
            )
            return True
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to dissociate block from categories", error=str(e))
            return False

    async def create_taxonomy_for_block(self, block_id: UUID, taxonomy_data: Dict[str, Any], transaction: Prisma) -> bool:
        """
        Creates taxonomy categories and associates them with a block within a transaction.

        Args:
            block_id (UUID): The UUID of the block.
            taxonomy_data (Dict[str, Any]): Nested taxonomy data.
                Expected structure:
                {
                    "general": {
                        "name": "Category Name",
                        "parent_id": Optional[UUID],
                        ...
                    },
                    "specific": {
                        "name": "Subcategory Name",
                        "parent_id": UUID of the general category,
                        ...
                    },
                    ...
                }
            transaction (Prisma): Prisma transaction instance.

        Returns:
            bool: True if taxonomy creation and association were successful, False otherwise.
        """
        try:
            general_taxonomy = taxonomy_data.get("general")
            specific_taxonomy = taxonomy_data.get("specific")

            category_ids = []

            # Create or get general taxonomy categories
            for category in general_taxonomy.get("categories", []):
                existing_category = await se.category.find_unique(
                    where={"name_parent_id": {"name": category["name"], "parent_id": None}}
                )
                if existing_category:
                    category_ids.append(UUID(existing_category.category_id))
                else:
                    created_category = await self.create_category(
                        {"name": category["name"]},
                        transaction=transaction
                    )
                    if created_category:
                        category_ids.append(UUID(created_category.category_id))
                    else:
                        raise ValueError("Failed to create general taxonomy category.")

            # Create or get specific taxonomy categories
            for category in specific_taxonomy.get("categories", []):
                parent_name = category.get("parent_name")
                # Find the parent category by name where parent_id is None
                parent_category = await self.prisma.category.find_unique(
                    where={"name_parent_id": {"name": parent_name, "parent_id": None}}
                )
                if not parent_category:
                    raise ValueError(f"Parent category '{parent_name}' does not exist.")

                existing_category = await self.prisma.category.find_unique(
                    where={"name_parent_id": {"name": category["name"], "parent_id": str(parent_category.category_id)}}
                )
                if existing_category:
                    category_ids.append(UUID(existing_category.category_id))
                else:
                    created_category = await self.create_category(
                        {"name": category["name"], "parent_id": UUID(parent_category.category_id)},
                        transaction=transaction
                    )
                    if created_category:
                        category_ids.append(UUID(created_category.category_id))
                    else:
                        raise ValueError("Failed to create specific taxonomy category.")

            # Associate block with all categories
            association_success = await self.associate_block_with_categories(
                block_id,
                category_ids,
                transaction=transaction
            )
            if not association_success:
                raise ValueError("Failed to associate block with taxonomy categories.")

            return True
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to create taxonomy for block", error=str(e))
            return False

    async def search_blocks(self, search_filters: Dict[str, Any]) -> Optional[List[PrismaBlock]]:
        """
        Searches for blocks based on taxonomy filters.

        Args:
            search_filters (Dict[str, Any]): Filters including 'category_names' and 'block_types'.

        Returns:
            Optional[List[PrismaBlock]]: List of blocks matching the search criteria, or None if an error occurs.
        """
        try:
            category_names = search_filters.get("category_names", [])
            block_types = search_filters.get("block_types", [])

            query_filters = {}

            if block_types:
                query_filters["block_type"] = {"in": block_types}

            if category_names:
                # Fetch category_ids for the given names
                categories = await self.prisma.category.find_many(
                    where={
                        "name": {"in": category_names}
                    },
                    select={"category_id": True}
                )
                category_ids = [cat.category_id for cat in categories]
                query_filters["block_categories"] = {
                    "some": {
                        "category_id": {"in": category_ids}
                    }
                }

            blocks = await self.prisma.block.find_many(
                where=query_filters,
                include={"block_categories": True}
            )

            self.logger.log(
                "TaxonomyService",
                "info",
                "Blocks retrieved successfully based on search filters",
                filters=search_filters,
                count=len(blocks)
            )
            return blocks
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to search blocks", error=str(e))
            return None

    async def get_all_categories(self) -> Optional[List[PrismaCategory]]:
        """
        Retrieves all categories, including their hierarchical relationships.

        Returns:
            Optional[List[PrismaCategory]]: List of all categories with their children, or None if an error occurs.
        """
        try:
            categories = await self.prisma.category.find_many(
                include={"children": True}
            )
            self.logger.log(
                "TaxonomyService",
                "info",
                f"Retrieved {len(categories)} categories."
            )
            return categories
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to retrieve all categories", error=str(e))
            return None

    async def get_block_categories(self, block_id: UUID) -> Optional[List[PrismaBlockCategory]]:
        """
        Retrieves all category associations for a given block.

        Args:
            block_id (UUID): The UUID of the block.

        Returns:
            Optional[List[PrismaBlockCategory]]: List of BlockCategory associations, or None if an error occurs.
        """
        try:
            block_categories = await self.prisma.block_category.find_many(
                where={"block_id": str(block_id)},
                include={"category": True}
            )
            self.logger.log(
                "TaxonomyService",
                "info",
                f"Retrieved {len(block_categories)} category associations for block {block_id}."
            )
            return block_categories
        except Exception as e:
            self.logger.log("TaxonomyService", "error", "Failed to retrieve block categories", error=str(e))
            return None

    async def main(self):
        """
        Comprehensive main function to test TaxonomyService functionalities.
        """
        try:
            print("Starting TaxonomyService test...")

            # Example data for testing
            general_taxonomy_data = {
                "categories": [
                    {"name": "Climate Data"},
                    {"name": "Remote Sensing"}
                ]
            }

            specific_taxonomy_data = {
                "categories": [
                    {"name": "Climate Models", "parent_name": "Climate Data"},
                    {"name": "Satellite Imagery", "parent_name": "Remote Sensing"}
                ]
            }

            taxonomy_data = {
                "general": general_taxonomy_data,
                "specific": specific_taxonomy_data
            }

            # Step 1: Create a new block
            print("\nCreating a new block...")
            block_service = BlockService()
            new_block_data = {
                "name": "Block1",
                "block_type": "dataset",
                "description": "A sample block for taxonomy testing."
            }
            created_block = await block_service.prisma.block.create(data=new_block_data)
            print(f"Created Block: {created_block.block_id} - {created_block.name}")

            # Step 2: Create taxonomy and associate with block within a transaction
            print("\nCreating taxonomy and associating with block...")
            taxonomy_service = self
            async with self.prisma.transaction() as tx:
                taxonomy_success = await taxonomy_service.create_taxonomy_for_block(
                    block_id=UUID(created_block.block_id),
                    taxonomy_data=taxonomy_data,
                    transaction=tx
                )
                if taxonomy_success:
                    print("Taxonomy created and associated successfully.")
                else:
                    print("Failed to create and associate taxonomy.")

            # Step 3: Retrieve block's categories
            print("\nRetrieving block's categories...")
            block_categories = await taxonomy_service.get_block_categories(UUID(created_block.block_id))
            if block_categories:
                for bc in block_categories:
                    print(f"- Category ID: {bc.category.category_id}, Name: {bc.category.name}")
            else:
                print("No categories associated with the block.")

            # Step 4: Update a category's name
            print("\nUpdating a category's name...")
            if block_categories:
                category_to_update = block_categories[0].category
                updated_category = await taxonomy_service.update_category(
                    UUID(category_to_update.category_id),
                    {"name": "Climate Information"}
                )
                if updated_category:
                    print(f"Updated Category: {updated_category.category_id} - {updated_category.name}")
                else:
                    print("Failed to update category.")

            # Step 5: Search for blocks with specific taxonomy
            print("\nSearching for blocks with category 'Climate Information' and block type 'dataset'...")
            search_filters = {
                "category_names": ["Climate Information"],
                "block_types": ["dataset"]
            }
            matching_blocks = await taxonomy_service.search_blocks(search_filters)
            if matching_blocks:
                for blk in matching_blocks:
                    print(f"- Block ID: {blk.block_id}, Name: {blk.name}, Type: {blk.block_type}")
            else:
                print("No matching blocks found.")

            # Step 6: Dissociate a category from the block
            print("\nDissociating a category from the block...")
            if block_categories:
                category_to_dissociate = block_categories[0].category
                dissociate_success = await taxonomy_service.dissociate_block_from_categories(
                    UUID(created_block.block_id),
                    [UUID(category_to_dissociate.category_id)]
                )
                if dissociate_success:
                    print("Category dissociated successfully.")
                else:
                    print("Failed to dissociate category.")

            # Step 7: Delete the block
            print("\nDeleting the block...")
            deletion_success = await taxonomy_service.prisma.block.delete(
                where={"block_id": created_block.block_id}
            )
            if deletion_success:
                print(f"Block {created_block.block_id} deleted successfully.")
            else:
                print("Failed to delete block.")

            # Step 8: List all categories
            print("\nListing all categories...")
            all_categories = await taxonomy_service.get_all_categories()
            if all_categories:
                for cat in all_categories:
                    parent_id = cat.parent_id if cat.parent_id else "None"
                    print(f"- Category ID: {cat.category_id}, Name: {cat.name}, Parent ID: {parent_id}")
            else:
                print("No categories found.")

        except Exception as e:
            self.logger.log("TaxonomyService", "error", "An error occurred in main", error=str(e))
            import traceback
            print(traceback.format_exc())

        print("\nTaxonomyService test completed.")

# Testing the TaxonomyService
if __name__ == "__main__":
    from backend.app.database import database
    from backend.app.logger import ConstellationLogger
    #block service
    from backend.app.features.core.services.block_service import BlockService
    
    async def run_taxonomy_service_tests():
        print("Connecting to the database...")
        await database.connect()
        print("Database connected.")

        taxonomy_service = TaxonomyService()
        await taxonomy_service.main()

        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

    asyncio.run(run_taxonomy_service_tests())
