# app/features/core/services/vector_embedding_service.py

"""
Vector Embedding Service Module

This module defines the VectorEmbeddingService class responsible for managing vector embeddings.
It provides methods to create, retrieve, update, delete vector embeddings, and perform similarity searches
using Prisma. The service is designed to be lightweight, focusing solely on Prisma interactions
without handling error management or logging.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from prisma import Prisma
from backend.app.schemas import (
    VectorRepresentationCreateSchema,
    VectorRepresentationResponseSchema
)

class VectorEmbeddingService:
    """
    VectorEmbeddingService handles all vector embedding-related operations, including CRUD operations
    and similarity searches. It interacts directly with the Prisma client to manage vector embedding data.
    """

    def __init__(self, prisma: Prisma):
        """
        Initializes the VectorEmbeddingService with the Prisma client.

        Args:
            prisma (Prisma): The Prisma client instance for database interactions.
        """
        self.prisma = prisma

    async def create_vector_embedding(
        self,
        vector_data: VectorRepresentationCreateSchema
    ) -> Optional[VectorRepresentationResponseSchema]:
        """
        Creates a new vector embedding in the database.

        Args:
            vector_data (VectorRepresentationCreateSchema): The data required to create a new vector embedding.

        Returns:
            Optional[VectorRepresentationResponseSchema]: The created vector embedding data.
        """
        vector = await self.prisma.vector_representations.create(
            data={
                "vector_id": str(vector_data.vector_id) if vector_data.vector_id else str(uuid4()),
                "entity_type": vector_data.entity_type,
                "entity_id": str(vector_data.entity_id),
                "vector": vector_data.vector,
                "taxonomy_filter": vector_data.taxonomy_filter,
                "created_at": vector_data.created_at or datetime.utcnow(),
                "updated_at": vector_data.updated_at or datetime.utcnow(),
            }
        )
        return VectorRepresentationResponseSchema(**vector.__dict__)

    async def get_vector_embedding(
        self,
        entity_id: UUID
    ) -> Optional[VectorRepresentationResponseSchema]:
        """
        Retrieves a vector embedding associated with a specific entity.

        Args:
            entity_id (UUID): The UUID of the entity (e.g., block) whose vector embedding is to be retrieved.

        Returns:
            Optional[VectorRepresentationResponseSchema]: The retrieved vector embedding data.
        """
        vector = await self.prisma.vector_representations.find_unique(
            where={
                "entity_id_entity_type": {
                    "entity_id": str(entity_id),
                    "entity_type": "BLOCK"  # Assuming entity_type is 'BLOCK' for blocks
                }
            }
        )
        if vector:
            return VectorRepresentationResponseSchema(**vector.__dict__)
        return None

    async def update_vector_embedding(
        self,
        entity_id: UUID,
        new_vector: Optional[List[float]] = None,
        taxonomy_filters: Optional[Dict[str, Any]] = None
    ) -> Optional[VectorRepresentationResponseSchema]:
        """
        Updates an existing vector embedding for a specific entity.

        Args:
            entity_id (UUID): The UUID of the entity whose vector embedding is to be updated.
            new_vector (Optional[List[float]]): The new vector data.
            taxonomy_filters (Optional[Dict[str, Any]]): New taxonomy filters for the vector embedding.

        Returns:
            Optional[VectorRepresentationResponseSchema]: The updated vector embedding data.
        """
        update_data = {}
        if new_vector is not None:
            update_data["vector"] = new_vector
        if taxonomy_filters is not None:
            update_data["taxonomy_filter"] = taxonomy_filters
        if not update_data:
            return await self.get_vector_embedding(entity_id)
        
        vector = await self.prisma.vector_representations.update(
            where={
                "entity_id_entity_type": {
                    "entity_id": str(entity_id),
                    "entity_type": "BLOCK"
                }
            },
            data={
                **update_data,
                "updated_at": datetime.utcnow()
            }
        )
        return VectorRepresentationResponseSchema(**vector.__dict__)

    async def delete_vector_embedding(
        self,
        entity_id: UUID
    ) -> bool:
        """
        Deletes a vector embedding associated with a specific entity.

        Args:
            entity_id (UUID): The UUID of the entity whose vector embedding is to be deleted.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        await self.prisma.vector_representations.delete(
            where={
                "entity_id_entity_type": {
                    "entity_id": str(entity_id),
                    "entity_type": "BLOCK"
                }
            }
        )
        return True

    async def search_similar_blocks(
        self,
        query_vector: List[float],
        top_k: int = 10
    ) -> Optional[List[VectorRepresentationResponseSchema]]:
        """
        Performs a similarity search to find blocks similar to the provided query vector.

        Args:
            query_vector (List[float]): The vector to compare against existing block vectors.
            top_k (int): Number of top similar blocks to retrieve.

        Returns:
            Optional[List[VectorRepresentationResponseSchema]]: List of similar blocks.
        """
        try:
            # Convert the query_vector to a string representation
            vector_str = ','.join(map(str, query_vector))
            
            # Construct the raw SQL query
            query = f"""
            SELECT *
            FROM vector_representations
            WHERE entity_type = 'BLOCK'
            ORDER BY vector <-> '{vector_str}'::vector
            LIMIT {top_k}
            """
            
            # Execute the raw query
            similar_vectors = await self.prisma.query_raw(query)

            if similar_vectors:
                return [VectorRepresentationResponseSchema(**vec) for vec in similar_vectors]
            return []
        except Exception as e:
            print(f"Error in search_similar_blocks: {str(e)}")
            return None

# -------------------
# Testing Utility
# -------------------
async def main():
    """
    Main function to test the VectorEmbeddingService functionalities.
    It performs the following steps:
    1. Creates a new vector embedding.
    2. Retrieves the created vector embedding.
    3. Updates the vector embedding.
    4. Performs a similarity search.
    5. Deletes the vector embedding.
    """
    from backend.app.database import database
    from backend.app.schemas import VectorRepresentationCreateSchema
    import uuid

    # Connect to the database
    await database.prisma.connect()
    prisma_client = database.prisma

    # Initialize the service
    vector_service = VectorEmbeddingService(prisma_client)

    # Example entity_id (UUID)
    entity_id = uuid.uuid4()

    # Step 1: Create Vector Embedding
    create_schema = VectorRepresentationCreateSchema(
        vector_id=uuid.uuid4(),
        entity_type="BLOCK",
        entity_id=entity_id,
        vector=[0.1]*512,  # Example 512-dimensional vector
        taxonomy_filter={"Science": {"Physics": {}}},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_vector = await vector_service.create_vector_embedding(create_schema)
    print(f"Vector Embedding Created: {created_vector.vector_id}")

    # Step 2: Retrieve Vector Embedding
    retrieved_vector = await vector_service.get_vector_embedding(entity_id)
    if retrieved_vector:
        print(f"Vector Embedding Retrieved: {retrieved_vector.vector_id}")
    else:
        print("Vector Embedding Retrieval Failed.")

    # Step 3: Update Vector Embedding
    updated_vector = await vector_service.update_vector_embedding(
        entity_id=entity_id,
        new_vector=[0.2]*512,
        taxonomy_filters={"Science": {"Chemistry": {}}}
    )
    if updated_vector:
        print(f"Vector Embedding Updated: {updated_vector.vector_id}")
    else:
        print("Vector Embedding Update Failed.")

    # Step 4: Similarity Search
    similar_blocks = await vector_service.search_similar_blocks(query_vector=[0.2]*512, top_k=5)
    if similar_blocks:
        print("Similarity Search Results:")
        for vec in similar_blocks:
            print(f" - Vector ID: {vec.vector_id}, Entity ID: {vec.entity_id}")
    else:
        print("No Similar Blocks Found.")

    # Step 5: Delete Vector Embedding
    deletion_success = await vector_service.delete_vector_embedding(entity_id)
    if deletion_success:
        print("Vector Embedding Deleted Successfully.")
    else:
        print("Vector Embedding Deletion Failed.")

    # Disconnect from the database
    await database.prisma.disconnect()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())