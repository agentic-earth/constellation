# app/services/taxonomy_service.py

"""
Taxonomy Service Module

This module encapsulates all taxonomy-related business logic and interactions with the Supabase backend.
It provides functions to create, retrieve, update, and delete taxonomy categories, ensuring that all operations are
maintained consistently across the database.

Design Philosophy:
- Maintain independence from other services to uphold clear separation of concerns.
- Utilize Supabase's REST API for standard CRUD operations for performance and reliability.
- Handle complex taxonomy parsing and hierarchical management within Python.
- Ensure flexibility to adapt to taxonomy changes with minimal modifications.
"""

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from app.taxonomy import Taxonomy, GeneralTaxonomy, EarthObservationModelTaxonomy, WeatherClimateModelTaxonomy, DatasetTaxonomy
from app.logger import ConstellationLogger
from app.database import get_supabase_client
from app.utils.serialization_utils import serialize_dict


class TaxonomyService:
    """
    TaxonomyService handles all taxonomy-related operations, including parsing taxonomy JSON,
    managing taxonomy categories, associating categories with blocks, and facilitating taxonomy-based searches.
    """

    def __init__(self):
        """
        Initializes the TaxonomyService with the Supabase client and logger.
        """
        self.client = get_supabase_client()
        self.logger = ConstellationLogger()

    def create_or_get_category(self, name: str, parent_id: Optional[UUID] = None) -> Optional[UUID]:
        """
        Creates a new category or retrieves an existing one based on name and parent_id.

        Args:
            name (str): Name of the category.
            parent_id (Optional[UUID]): UUID of the parent category, if any.

        Returns:
            Optional[UUID]: The UUID of the created or existing category.
        """
        try:
            # Query to find existing category
            query = self.client.table("categories").select("category_id").eq("name", name)
            if parent_id:
                query = query.eq("parent_id", str(parent_id))
            response = query.execute()

            if response.data:
                category_id = UUID(response.data[0]['category_id'])
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    f"Existing category found: {name} (ID: {category_id})",
                    extra={"category_name": name, "category_id": str(category_id)}
                )
                return category_id

            # If not found, create a new category
            new_category_id = uuid4()
            current_time = datetime.utcnow()

            category_data = {
                "category_id": str(new_category_id),
                "name": name,
                "parent_id": str(parent_id) if parent_id else None,
                "created_at": current_time.isoformat(),
                "updated_at": current_time.isoformat()
            }

            insert_response = self.client.table("categories").insert(serialize_dict(category_data)).execute()

            if insert_response.error:
                self.logger.log(
                    "TaxonomyService",
                    "error",
                    f"Failed to create category: {name}",
                    extra={"error": insert_response.error.message}
                )
                return None

            self.logger.log(
                "TaxonomyService",
                "info",
                f"Category created: {name} (ID: {new_category_id})",
                extra={"category_name": name, "category_id": str(new_category_id)}
            )
            return new_category_id

        except Exception as e:
            self.logger.log(
                "TaxonomyService",
                "critical",
                f"Exception in create_or_get_category: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    def process_taxonomy(self, taxonomy: Dict[str, Any], parent_id: Optional[UUID] = None) -> List[UUID]:
        """
        Processes nested taxonomy and ensures all categories exist in the database.

        Args:
            taxonomy (Dict[str, Any]): Nested taxonomy dictionary.
            parent_id (Optional[UUID]): UUID of the parent category, if any.

        Returns:
            List[UUID]: List of category UUIDs associated with the block.
        """
        category_ids = []
        for key, value in taxonomy.items():
            category_id = self.create_or_get_category(name=key, parent_id=parent_id)
            if category_id:
                category_ids.append(category_id)
                if isinstance(value, dict):
                    sub_category_ids = self.process_taxonomy(taxonomy=value, parent_id=category_id)
                    category_ids.extend(sub_category_ids)
            else:
                self.logger.log(
                    "TaxonomyService",
                    "warning",
                    f"Failed to process category: {key}",
                    extra={"category_name": key, "parent_id": parent_id}
                )
        return category_ids

    def associate_block_with_categories(self, block_id: UUID, category_ids: List[UUID]) -> bool:
        """
        Associates a block with multiple taxonomy categories.

        Args:
            block_id (UUID): UUID of the block.
            category_ids (List[UUID]): List of category UUIDs to associate with the block.

        Returns:
            bool: True if associations are successful, False otherwise.
        """
        try:
            current_time = datetime.utcnow()
            associations = [
                {
                    "block_category_id": str(uuid4()),
                    "block_id": str(block_id),
                    "category_id": str(category_id),
                    "created_at": current_time.isoformat()
                }
                for category_id in category_ids
            ]

            insert_response = self.client.table("block_categories").insert(serialize_dict(associations)).execute()

            if insert_response.error:
                self.logger.log(
                    "TaxonomyService",
                    "error",
                    "Failed to associate block with categories",
                    extra={"block_id": str(block_id), "error": insert_response.error.message}
                )
                return False

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

    def create_taxonomy_for_block(self, block_id: UUID, taxonomy: Taxonomy) -> bool:
        """
        Creates taxonomy categories and associates them with a block.

        Args:
            block_id (UUID): UUID of the block.
            taxonomy (Taxonomy): Taxonomy data structured according to Pydantic models.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            taxonomy_dict = taxonomy.dict(exclude_unset=True)

            # Process general taxonomy
            general_taxonomy = taxonomy_dict.get('general', {})
            general_categories = self.process_taxonomy(taxonomy=general_taxonomy)

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

                specific_categories = self.process_taxonomy(taxonomy=specific_taxonomy)
                general_categories.extend(specific_categories)

            # Associate block with all processed categories
            success = self.associate_block_with_categories(block_id=block_id, category_ids=general_categories)
            return success

        except Exception as e:
            self.logger.log(
                "TaxonomyService",
                "critical",
                f"Exception in create_taxonomy_for_block: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    def search_blocks_by_taxonomy(self, taxonomy_filters: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        """
        Searches for blocks that match the given taxonomy filters.

        Args:
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
            response = self.client.table("categories").select("category_id").in_("name", category_names).execute()

            if response.error:
                self.logger.log(
                    "TaxonomyService",
                    "error",
                    "Failed to retrieve category IDs for search",
                    extra={"error": response.error.message}
                )
                return None

            category_ids = [UUID(cat['category_id']) for cat in response.data]

            if not category_ids:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    "No categories found matching the filters",
                    extra={"taxonomy_filters": taxonomy_filters}
                )
                return []

            # Retrieve block_ids associated with these category_ids
            response = self.client.table("block_categories").select("block_id").in_("category_id", [str(cid) for cid in category_ids]).execute()

            if response.error:
                self.logger.log(
                    "TaxonomyService",
                    "error",
                    "Failed to retrieve block IDs for search",
                    extra={"error": response.error.message}
                )
                return None

            block_ids = list(set([UUID(block['block_id']) for block in response.data]))

            if not block_ids:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    "No blocks found matching the taxonomy filters",
                    extra={"taxonomy_filters": taxonomy_filters}
                )
                return []

            # Retrieve block details
            response = self.client.table("blocks").select("*").in_("block_id", [str(bid) for bid in block_ids]).execute()

            if response.error:
                self.logger.log(
                    "TaxonomyService",
                    "error",
                    "Failed to retrieve blocks for search",
                    extra={"error": response.error.message}
                )
                return None

            self.logger.log(
                "TaxonomyService",
                "info",
                f"Found {len(response.data)} blocks matching the taxonomy filters",
                extra={"taxonomy_filters": taxonomy_filters}
            )
            return response.data

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

    def get_taxonomy_for_block(self, block_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieves the taxonomy associated with a specific block.

        Args:
            block_id (UUID): UUID of the block.

        Returns:
            Optional[Dict[str, Any]]: Nested taxonomy dictionary if found, None otherwise.
        """
        try:
            # Retrieve associated category_ids
            response = self.client.table("block_categories").select("category_id").eq("block_id", str(block_id)).execute()

            if response.error:
                self.logger.log(
                    "TaxonomyService",
                    "error",
                    "Failed to retrieve category IDs for block.",
                    extra={"block_id": str(block_id), "error": response.error.message}
                )
                return None

            category_ids = [UUID(cat['category_id']) for cat in response.data]
            if not category_ids:
                self.logger.log(
                    "TaxonomyService",
                    "info",
                    f"No taxonomy associated with block {block_id}.",
                    extra={"block_id": str(block_id)}
                )
                return None

            # Retrieve category details
            response = self.client.table("categories").select("category_id", "name", "parent_id").in_("category_id", [str(cid) for cid in category_ids]).execute()

            if response.error:
                self.logger.log(
                    "TaxonomyService",
                    "error",
                    "Failed to retrieve category details for block.",
                    extra={"block_id": str(block_id), "error": response.error.message}
                )
                return None

            categories = response.data
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
        category_map = {UUID(cat['category_id']): cat for cat in categories}

        for cat_id, cat in category_map.items():
            parent_id = UUID(cat['parent_id']) if cat['parent_id'] else None
            if parent_id and parent_id in category_map:
                parent = taxonomy_dict.setdefault(category_map[parent_id]['name'], {})
                parent[cat['name']] = {}
            else:
                taxonomy_dict[cat['name']] = {}

        return taxonomy_dict
