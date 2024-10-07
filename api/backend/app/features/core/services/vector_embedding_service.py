# app/services/vector_embedding_service.py

"""
Vector Embedding Service Module

This module encapsulates all vector embedding-related business logic and interactions with the Supabase backend
utilizing pg-vector. It provides functions to create, retrieve, update, delete vector embeddings, and perform
similarity searches over the embeddings.

Design Philosophy:
- Maintain independence from other services to uphold clear separation of concerns.
- Utilize Supabase's pg-vector for efficient vector storage and similarity querying.
- Ensure transactional integrity between vector operations and Supabase metadata storage.
- Provide flexible search capabilities, allowing for searches over all vectors or subsets based on filters.
- Implement robust error handling and comprehensive logging for production readiness.
"""

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from backend.app.logger import ConstellationLogger
from backend.app.features.core.services.taxonomy_service import TaxonomyService

from prisma import Prisma
from prisma.models import vector_representations as PrismaVectorRepresentation
from prisma.models import blocks as PrismaBlock


class VectorEmbeddingService:
    """
    VectorEmbeddingService handles all vector embedding-related operations, including CRUD operations
    and similarity searches. It interacts with Supabase's pg-vector for vector storage and querying.
    """

    def __init__(self):
        self.logger = ConstellationLogger()

    async def create_vector_embedding(self, tx: Prisma, vector_data: Dict[str, Any]) -> PrismaVectorRepresentation:
        """
        Creates a new vector embedding in the database using Prisma.
        """
        try:
            # Generate UUID if not provided
            vector_create_data = {
                "vector_id": vector_data.get("vector_id", str(uuid4())),
                "entity_type": vector_data["entity_type"],
                "entity_id": vector_data["entity_id"],
                "vector": vector_data["vector"],
                "taxonomy_filter": vector_data.get("taxonomy_filter"),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }

            # Insert into database using Prisma
            created_vector = await tx.vector_representations.create(data=vector_create_data)

            self.logger.log(
                "VectorEmbeddingService",
                "info",
                "Vector embedding created successfully.",
                extra={"vector_id": str(created_vector.vector_id), "entity_id": str(created_vector.entity_id)}
            )
            return created_vector

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during vector embedding creation: {str(e)}",
                extra={"traceback": traceback.format_exc(), "vector_data": vector_data}
            )
            return None

    async def get_vector_embedding(self, tx: Prisma, block_id: UUID) -> Optional[PrismaVectorRepresentation]:
        """
        Retrieves the vector embedding associated with a specific block using Prisma.
        """
        try:
            self.logger.log(
                "VectorEmbeddingService",
                "info",
                "Retrieving vector embedding.",
                extra={"block_id": str(block_id)}
            )
            vector = await tx.vector_representations.find_unique(where={"entity_id": str(block_id)})

            if not vector:
                self.logger.log(
                    "VectorEmbeddingService",
                    "warning",
                    "Vector embedding not found for the block.",
                    extra={"block_id": str(block_id)}
                )
                return None

            self.logger.log(
                "VectorEmbeddingService",
                "info",
                "Vector embedding retrieved successfully.",
                extra={"vector": vector}
            )

            return vector

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during vector embedding retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return None

    async def update_vector_embedding(self, tx: Prisma, block_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaVectorRepresentation]:
        """
        Updates the vector embedding for a specific block using Prisma.
        """
        try:
            update_data = {
                "vector": update_data.get("vector"),
                "taxonomy_filter": update_data.get("taxonomy_filter"),
                "updated_at": datetime.utcnow()
            }

            update_data = {k: v for k, v in update_data.items() if v is not None}

            # Update using Prisma
            updated_vector = await tx.vector_representations.update(
                where={"entity_id": str(block_id)},
                data=update_data
            )

            self.logger.log(
                "VectorEmbeddingService",
                "info",
                "Vector embedding updated successfully.",
                extra={"block_id": str(block_id)}
            )
            return updated_vector

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during vector embedding update: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return None

    async def delete_vector_embedding(self, tx: Prisma, block_id: UUID) -> bool:
        """
        Deletes the vector embedding associated with a specific block from the database using Prisma.
        """
        try:
            await tx.vector_representations.delete(
                where={"entity_id": str(block_id)}
            )

            self.logger.log(
                "VectorEmbeddingService",
                "info",
                "Vector embedding deleted successfully.",
                extra={"block_id": str(block_id)}
            )
            return True

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during vector embedding deletion: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return False

    async def search_similar_vectors(self, tx: Prisma, query_vector: List[float], taxonomy_filters: Optional[Dict[str, Any]] = None, top_k: int = 10) -> Optional[List[PrismaBlock]]:
        """
        Performs a similarity search over blocks based on the provided query vector and optional taxonomy filters using Prisma.
        """
        try:
            # Step 1: Apply taxonomy filters if provided
            if taxonomy_filters:
                taxonomy_service = TaxonomyService()
                matching_blocks = await taxonomy_service.search_blocks_by_taxonomy(tx, taxonomy_filters)
                if not matching_blocks:
                    self.logger.log(
                        "VectorEmbeddingService",
                        "info",
                        "No blocks match the provided taxonomy filters.",
                        extra={"taxonomy_filters": taxonomy_filters}
                    )
                    return []
                block_ids = [str(block.block_id) for block in matching_blocks]
            else:
                block_ids = []  # No taxonomy filtering

            # Step 3: Build the SQL query for similarity search using pg-vector
            if block_ids:
                # If filtering by taxonomy, include WHERE entity_id IN (...)
                supabase_sql = f"""
                    SELECT *
                    FROM vector_representations
                    WHERE entity_id IN ({', '.join([f"'{bid}'" for bid in block_ids])})
                    ORDER BY vector <-> $1::vector ASC
                    LIMIT {top_k};
                """
            else:
                # No taxonomy filtering
                supabase_sql = f"""
                    SELECT *
                    FROM vector_representations
                    ORDER BY vector <-> $1::vector ASC
                    LIMIT {top_k};
                """

            # Perform the similarity search using Prisma's raw SQL execution
            similar_vectors = await tx.vector_representations.query_raw(
                supabase_sql,
                query_vector
            )

            if not similar_vectors:
                self.logger.log(
                    "VectorEmbeddingService",
                    "error",
                    "Failed to execute similarity search query.",
                )
                return None

            # Extract block IDs from the similar vectors
            similar_block_ids = [UUID(vector['entity_id']) for vector in similar_vectors]

            # Retrieve block details
            block_service = BlockService()
            similar_blocks = await block_service.get_blocks_by_ids(tx, similar_block_ids)

            self.logger.log(
                "VectorEmbeddingService",
                "info",
                f"Similarity search completed with {len(similar_blocks)} results.",
                extra={"taxonomy_filters": taxonomy_filters, "top_k": top_k}
            )
            return similar_blocks

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during similarity search: {str(e)}",
                extra={"traceback": traceback.format_exc(), "query_vector": query_vector}
            )
            return None

# -------------------
# Testing Utility
# -------------------
async def main():
    """
    Main function to test basic CRUD operations of the VectorEmbeddingService.
    """
    import json

    # Initialize Prisma client
    prisma = Prisma()
    await prisma.connect()

    service = VectorEmbeddingService()

    # Test data
    test_block_id = uuid4()
    test_vector = [0.1] * 512  # Example 512-dimensional vector
    test_taxonomy_filters = {"category": "Climate"}

    # Create Vector Embedding
    created_vector = await service.create_vector_embedding(prisma, vector_data)
    if created_vector:
        print(f"Vector Embedding Created: {created_vector.vector_id}")

    # Retrieve Vector Embedding
    retrieved_vector = await service.get_vector_embedding(prisma, test_block_id)
    if retrieved_vector:
        print(f"Vector Embedding Retrieved: {retrieved_vector.vector_id}")

    # Update Vector Embedding
    new_vector = [0.2] * 512
    update_success = await service.update_vector_embedding(prisma, test_block_id, new_vector=new_vector, taxonomy_filters={"category": "Weather"})
    if update_success:
        print("Vector Embedding Updated Successfully.")

    # Perform Similarity Search
    search_results = await service.search_similar_blocks(prisma, query_vector=new_vector, taxonomy_filters={"category": "Weather"}, top_k=5)
    if search_results:
        print(f"Similarity Search Results: {[block.block_id for block in search_results]}")

    # Delete Vector Embedding
    deletion_success = await service.delete_vector_embedding(prisma, test_block_id)
    if deletion_success:
        print("Vector Embedding Deleted Successfully.")

    await prisma.disconnect()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())