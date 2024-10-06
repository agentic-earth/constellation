# app/services/taxonomy_service.py

"""
Taxonomy Service Module

This module encapsulates all taxonomy-related business logic and interactions with the Prisma ORM.
It provides functions to create, retrieve, update, and delete taxonomy categories, ensuring that all operations are
maintained consistently across the database.

Design Philosophy:
- Maintain independence from other services to uphold clear separation of concerns.
- Utilize Prisma ORM for database operations, ensuring type safety and efficient queries.
- Handle complex taxonomy parsing and hierarchical management within Python.
- Ensure flexibility to adapt to taxonomy changes with minimal modifications.
"""

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from prisma import Prisma
from backend.app.taxonomy import Taxonomy, GeneralTaxonomy, EarthObservationModelTaxonomy, WeatherClimateModelTaxonomy, DatasetTaxonomy
from backend.app.logger import ConstellationLogger


class TaxonomyService:
    """
    TaxonomyService handles all taxonomy-related operations, including parsing taxonomy JSON,
    managing taxonomy categories, associating categories with blocks, and facilitating taxonomy-based searches.
    """

    def __init__(self):
        """
        Initializes the TaxonomyService with the logger.
        """
        self.logger = ConstellationLogger()

    async def create_or_get_category(self, tx: Prisma, name: str, parent_id: Optional[UUID] = None) -> Optional[UUID]:
        """
        Creates a new category or retrieves an existing one based on name and parent_id.

        Args:
            tx (Prisma): The Prisma transaction object.
            name (str): Name of the category.
            parent_id (Optional[UUID]): UUID of the parent category, if any.

        Returns:
            Optional[UUID]: The UUID of the created or existing category.
        """
        try:
            # Query to find existing category
            existing_category = await tx.taxonomycategory.find_first(
                where={"name": name, "parentId": str(parent_id) if parent_id else None}
            )

            if existing_category:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    f"Existing category found: {name} (ID: {existing_category.id})",
                    extra={"category_name": name, "category_id": existing_category.id}
                )
                return UUID(existing_category.id)

            # If not found, create a new category
            new_category = await tx.taxonomycategory.create(
                data={
                    "name": name,
                    "parentId": str(parent_id) if parent_id else None
                }
            )

            self.logger.log(
                "TaxonomyService",
                "info",
                f"Category created: {name} (ID: {new_category.id})",
                extra={"category_name": name, "category_id": new_category.id}
            )
            return UUID(new_category.id)

        except Exception as e:
            self.logger.log(
                "TaxonomyService",
                "critical",
                f"Exception in create_or_get_category: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    async def process_taxonomy(self, tx: Prisma, taxonomy: Dict[str, Any], parent_id: Optional[UUID] = None) -> List[UUID]:
        """
        Processes nested taxonomy and ensures all categories exist in the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            taxonomy (Dict[str, Any]): Nested taxonomy dictionary.
            parent_id (Optional[UUID]): UUID of the parent category, if any.

        Returns:
            List[UUID]: List of category UUIDs associated with the block.
        """
        category_ids = []
        for key, value in taxonomy.items():
            category_id = await self.create_or_get_category(tx, name=key, parent_id=parent_id)
            if category_id:
                category_ids.append(category_id)
                if isinstance(value, dict):
                    sub_category_ids = await self.process_taxonomy(tx, taxonomy=value, parent_id=category_id)
                    category_ids.extend(sub_category_ids)
            else:
                self.logger.log(
                    "TaxonomyService",
                    "warning",
                    f"Failed to process category: {key}",
                    extra={"category_name": key, "parent_id": parent_id}
                )
        return category_ids

    async def associate_block_with_categories(self, tx: Prisma, block_id: UUID, category_ids: List[UUID]) -> bool:
        """
        Associates a block with multiple taxonomy categories.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_id (UUID): UUID of the block.
            category_ids (List[UUID]): List of category UUIDs to associate with the block.

        Returns:
            bool: True if associations are successful, False otherwise.
        """
        try:
            for category_id in category_ids:
                await tx.blocktaxonomy.create(
                    data={
                        "blockId": str(block_id),
                        "categoryId": str(category_id)
                    }
                )

            self.logger.log(
                "TaxonomyService",
                "info",
                f"Block {block_id} associated with categories: {category_ids}",
                extra={"block_id": str(block_id), "category_ids": [str(cid) for cid in category_ids]}
            )
            return True

        except Exception as e:
            self.logger.log(
                "TaxonomyService",
                "critical",
                f"Exception in associate_block_with_categories: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    async def create_taxonomy_for_block(self, tx: Prisma, block_id: UUID, taxonomy: Taxonomy) -> bool:
        """
        Creates taxonomy categories and associates them with a block.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_id (UUID): UUID of the block.
            taxonomy (Taxonomy): Taxonomy data structured according to Pydantic models.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            taxonomy_dict = taxonomy.dict(exclude_unset=True)

            # Process general taxonomy
            general_taxonomy = taxonomy_dict.get('general', {})
            general_categories = await self.process_taxonomy(tx, taxonomy=general_taxonomy)

            # Process specific taxonomy based on paper type
            specific_taxonomy = taxonomy_dict.get('specific')
            if specific_taxonomy:
                # Determine taxonomy type
                paper_type = general_taxonomy.get('paper_type')
                if paper_type == "Earth Observation Model":
                    specific_taxonomy = specific_taxonomy.get('earth_observation', {})
                elif paper_type == "Weather/Climate Model":
                    specific_taxonomy = specific_taxonomy.get('weather_climate', {})
                elif paper_type == "Dataset":
                    specific_taxonomy = specific_taxonomy.get('dataset', {})
                else:
                    specific_taxonomy = {}

                specific_categories = await self.process_taxonomy(tx, taxonomy=specific_taxonomy)
                general_categories.extend(specific_categories)

            # Associate block with all processed categories
            success = await self.associate_block_with_categories(tx, block_id=block_id, category_ids=general_categories)
            return success

        except Exception as e:
            self.logger.log(
                "TaxonomyService",
                "critical",
                f"Exception in create_taxonomy_for_block: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    async def search_blocks_by_taxonomy(self, tx: Prisma, taxonomy_filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Searches for blocks that match the given taxonomy filters.

        Args:
            tx (Prisma): The Prisma transaction object.
            taxonomy_filters (Dict[str, Any]): Filters based on taxonomy categories.

        Returns:
            Optional[List[Dict[str, Any]]]: List of blocks matching the filters, or None if an error occurs.
        """
        try:
            # Flatten taxonomy filters to handle nested structures
            flattened_filters = self.flatten_taxonomy(taxonomy_filters)

            # Extract category names from flattened filters
            category_names = list(flattened_filters.keys())
            if not category_names:
                self.logger.log(
                    "TaxonomyService",
                    "warning",
                    "No valid taxonomy filters provided.",
                    extra={"taxonomy_filters": taxonomy_filters}
                )
                return []

            # Retrieve category_ids matching the filter names
            categories = await tx.taxonomycategory.find_many(
                where={"name": {"in": category_names}}
            )

            category_ids = [UUID(cat.id) for cat in categories]

            if not category_ids:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    "No categories found matching the filters",
                    extra={"taxonomy_filters": taxonomy_filters}
                )
                return []

            # Retrieve block_ids associated with these category_ids
            block_taxonomies = await tx.blocktaxonomy.find_many(
                where={"categoryId": {"in": [str(cid) for cid in category_ids]}}
            )

            block_ids = list(set([UUID(bt.blockId) for bt in block_taxonomies]))

            if not block_ids:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    "No blocks found matching the taxonomy filters",
                    extra={"taxonomy_filters": taxonomy_filters}
                )
                return []

            # Retrieve block details
            blocks = await tx.block.find_many(
                where={"id": {"in": [str(bid) for bid in block_ids]}}
            )

            self.logger.log(
                "TaxonomyService",
                "info",
                f"Found {len(blocks)} blocks matching the taxonomy filters",
                extra={"taxonomy_filters": taxonomy_filters}
            )
            return [block.dict() for block in blocks]

        except Exception as e:
            self.logger.log(
                "TaxonomyService",
                "critical",
                f"Exception in search_blocks_by_taxonomy: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    def flatten_taxonomy(self, taxonomy: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        Flattens a nested taxonomy dictionary.

        Args:
            taxonomy (Dict[str, Any]): Nested taxonomy.
            parent_key (str): Base key string.
            sep (str): Separator between keys.

        Returns:
            Dict[str, Any]: Flattened taxonomy.
        """
        items = {}
        for k, v in taxonomy.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self.flatten_taxonomy(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items

    async def get_taxonomy_for_block(self, tx: Prisma, block_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves the taxonomy associated with a specific block.

        Args:
            tx (Prisma): The Prisma transaction object.
            block_id (UUID): UUID of the block.

        Returns:
            Optional[Dict[str, Any]]: Nested taxonomy dictionary if found, None otherwise.
        """
        try:
            # Retrieve associated category_ids
            block_taxonomies = await tx.blocktaxonomy.find_many(
                where={"blockId": str(block_id)},
                include={"category": True}
            )

            if not block_taxonomies:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    f"No taxonomy associated with block {block_id}.",
                    extra={"block_id": str(block_id)}
                )
                return None

            categories = [bt.category for bt in block_taxonomies]
            taxonomy_tree = self.build_taxonomy_tree(categories)

            self.logger.log(
                "TaxonomyService",
                "info",
                f"Taxonomy retrieved for block {block_id}.",
                extra={"block_id": str(block_id)}
            )
            return taxonomy_tree

        except Exception as e:
            self.logger.log(
                "TaxonomyService",
                "critical",
                f"Exception in get_taxonomy_for_block: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    def build_taxonomy_tree(self, categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Builds a nested taxonomy tree from a flat list of categories.

        Args:
            categories (List[Dict[str, Any]]): List of category dictionaries.

        Returns:
            Dict[str, Any]: Nested taxonomy dictionary.
        """
        taxonomy_dict = {}
        category_map = {UUID(cat['id']): cat for cat in categories}

        for cat_id, cat in category_map.items():
            parent_id = UUID(cat['parentId']) if cat['parentId'] else None
            if parent_id and parent_id in category_map:
                parent = taxonomy_dict.setdefault(category_map[parent_id]['name'], {})
                parent[cat['name']] = {}
            else:
                taxonomy_dict[cat['name']] = {}

        return taxonomy_dict