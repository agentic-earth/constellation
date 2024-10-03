# constellation-backend/api/backend/app/features/core/services/taxonomy_service.py

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from prisma import Prisma
from prisma.models import categories as PrismaCategory, block_categories as PrismaBlockCategory
from backend.app.schemas import TaxonomyCategoryCreateSchema

class TaxonomyService:
    """
    TaxonomyService handles all taxonomy-related operations, including creating and retrieving taxonomy categories.
    It interacts directly with the Prisma client to manage taxonomy data.
    """

    def __init__(self, prisma: Prisma):
        self.prisma = prisma

    async def create_category(self, name: str, parent_id: Optional[UUID] = None) -> PrismaCategory:
        category = await self.prisma.categories.create(
            data={
                "category_id": str(uuid4()),
                "name": name,
                "parent_id": str(parent_id) if parent_id else None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )
        return category

    async def get_or_create_category(self, name: str, parent_id: Optional[UUID] = None) -> PrismaCategory:
        category = await self.prisma.categories.find_unique(
            where={
                "name_parent_id": {
                    "name": name,
                    "parent_id": str(parent_id) if parent_id else None
                }
            }
        )
        if category:
            return category
        else:
            return await self.create_category(name, parent_id)

    async def process_taxonomy(self, taxonomy: Dict[str, Any], parent_id: Optional[UUID] = None) -> List[UUID]:
        category_ids = []
        for name, sub_taxonomy in taxonomy.items():
            category = await self.get_or_create_category(name, parent_id)
            category_id = UUID(category.category_id)
            category_ids.append(category_id)
            if isinstance(sub_taxonomy, dict):
                sub_category_ids = await self.process_taxonomy(sub_taxonomy, category_id)
                category_ids.extend(sub_category_ids)
        return category_ids

    async def associate_block_with_categories(self, block_id: UUID, category_ids: List[UUID]) -> bool:
        # Use create_many for bulk insertion
        await self.prisma.block_categories.create_many(
            data=[
                {
                    "block_category_id": str(uuid4()),
                    "block_id": str(block_id),
                    "category_id": str(category_id),
                    "created_at": datetime.utcnow(),
                }
                for category_id in category_ids
            ],
            skip_duplicates=True  # Avoid duplicate entries
        )
        return True

    async def create_taxonomy_for_block(self, block_id: UUID, taxonomy: Dict[str, Any]) -> bool:
        category_ids = await self.process_taxonomy(taxonomy)
        return await self.associate_block_with_categories(block_id, category_ids)

    async def get_taxonomy_for_block(self, block_id: UUID) -> Optional[Dict[str, Any]]:
        block_categories = await self.prisma.block_categories.find_many(
            where={"block_id": str(block_id)},
            include={"categories": True}
        )
        if not block_categories:
            return None

        # Build taxonomy hierarchy
        taxonomy = {}
        category_map = {}
        for bc in block_categories:
            category = bc.categories
            category_map[category.category_id] = {
                "name": category.name,
                "parent_id": UUID(category.parent_id) if category.parent_id else None
            }

        for category_id, info in category_map.items():
            if info["parent_id"]:
                parent = category_map.get(str(info["parent_id"]), None)
                if parent:
                    taxonomy.setdefault(parent["name"], {})[info["name"]] = {}
            else:
                taxonomy[info["name"]] = {}

        return taxonomy

    async def search_blocks_by_taxonomy(self, taxonomy_query: Dict[str, Any]) -> List[UUID]:
        """
        Search for blocks that match the given taxonomy query.
        This function retrieves all relevant category IDs based on the taxonomy query and
        then finds blocks associated with any of these categories.
        """
        # Process the taxonomy query to get relevant category IDs
        category_ids = await self.process_taxonomy(taxonomy_query)

        # Retrieve block IDs associated with these categories
        block_categories = await self.prisma.block_categories.find_many(
            where={"category_id": {"in": [str(cid) for cid in category_ids]}},
            select={"block_id": True}
        )

        block_ids = list({UUID(bc.block_id) for bc in block_categories})

        return block_ids