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

from backend.app.taxonomy import Taxonomy, GeneralTaxonomy, EarthObservationModelTaxonomy, WeatherClimateModelTaxonomy, DatasetTaxonomy
from backend.app.logger import ConstellationLogger
from backend.app.database import get_supabase_client
from backend.app.utils.serialization_utils import serialize_dict
from prisma import Prisma
from backend.app.schemas import TaxonomyCategoryCreateSchema, TaxonomyCategoryResponseSchema


class TaxonomyService:
    """
    TaxonomyService handles all taxonomy-related operations, including creating and retrieving taxonomy categories.
    It interacts directly with the Prisma client to manage taxonomy data.
    """

    def __init__(self, prisma: Prisma):
        self.prisma = prisma

    async def create_or_get_category(self, name: str, parent_id: Optional[UUID] = None) -> Optional[UUID]:
        category = await self.prisma.categories.find_unique(where={"name_parent_id": {"name": name, "parent_id": str(parent_id) if parent_id else None}})
        if category:
            return UUID(category.category_id)
        new_category = await self.prisma.categories.create(
            data={
                "category_id": uuid4(),
                "name": name,
                "parent_id": str(parent_id) if parent_id else None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        return UUID(new_category.category_id)

    async def process_taxonomy(self, taxonomy: Dict[str, Any], parent_id: Optional[UUID] = None) -> List[UUID]:
        category_ids = []
        for key, value in taxonomy.items():
            category_id = await self.create_or_get_category(name=key, parent_id=parent_id)
            if category_id:
                category_ids.append(category_id)
                if isinstance(value, dict):
                    sub_category_ids = await self.process_taxonomy(taxonomy=value, parent_id=category_id)
                    category_ids.extend(sub_category_ids)
        return category_ids

    async def associate_block_with_categories(self, block_id: UUID, category_ids: List[UUID]) -> bool:
        await self.prisma.block_categories.create_many(
            data=[
                {
                    "block_category_id": uuid4(),
                    "block_id": str(block_id),
                    "category_id": str(category_id),
                    "created_at": datetime.utcnow(),
                }
                for category_id in category_ids
            ]
        )
        return True

    async def create_taxonomy_for_block(self, block_id: UUID, taxonomy: Dict[str, Any]) -> bool:
        category_ids = await self.process_taxonomy(taxonomy)
        return await self.associate_block_with_categories(block_id, category_ids)

    async def get_taxonomy_for_block(self, block_id: UUID) -> Optional[Dict[str, Any]]:
        block_categories = await self.prisma.block_categories.find_many(where={"block_id": str(block_id)}, include={"category": True})
        if not block_categories:
            return None
        taxonomy = {}
        for bc in block_categories:
            category = bc.category
            if category.parent_id:
                parent = await self.prisma.categories.find_unique(where={"category_id": category.parent_id})
                taxonomy.setdefault(parent.name, {})[category.name] = {}
            else:
                taxonomy[category.name] = {}
        return taxonomy