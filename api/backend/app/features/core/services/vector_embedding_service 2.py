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

from pydantic import BaseModel

from backend.app.schemas import VectorRepresentationSchema, BlockResponseSchema
from backend.app.logger import ConstellationLogger
from backend.app.database import get_supabase_client
from backend.app.utils.serialization_utils import serialize_dict

from supabase import Client
from postgrest import APIError as PostgrestError


class VectorEmbeddingService:
    """
    VectorEmbeddingService handles all vector embedding-related operations, including CRUD operations
    and similarity searches. It interacts with Supabase's pg-vector for vector storage and querying.
    """

    def __init__(self):
        """
        Initializes the VectorEmbeddingService with the Supabase client and logger.
        """
        self.supabase_client: Client = get_supabase_client()
        self.logger = ConstellationLogger()

    def create_vector_embedding(self, vector_data: VectorRepresentationSchema) -> Optional[VectorRepresentationSchema]:
        """
        Creates a new vector embedding in Supabase's `vector_representations` table.

        Args:
            vector_data (VectorRepresentationSchema): The vector embedding data to create.

        Returns:
            Optional[VectorRepresentationSchema]: The created vector embedding schema if successful, None otherwise.
        """
        try:
            # Generate UUID if not provided
            if not vector_data.vector_id:
                vector_data.vector_id = uuid4()

            # Add timestamps
            current_time = datetime.utcnow()
            vector_data.created_at = current_time
            vector_data.updated_at = current_time

            # Insert into Supabase
            response = self.supabase_client.table("vector_representations").insert(serialize_dict(vector_data.dict())).execute()

            if response.error:
                self.logger.log(
                    "VectorEmbeddingService",
                    "error",
                    "Failed to insert vector embedding into Supabase.",
                    extra={"error": response.error.message, "vector_data": vector_data.dict()}
                )
                return None

            self.logger.log(
                "VectorEmbeddingService",
                "info",
                "Vector embedding created successfully.",
                extra={"vector_id": str(vector_data.vector_id), "entity_id": str(vector_data.entity_id)}
            )
            return vector_data

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during vector embedding creation: {str(e)}",
                extra={"traceback": traceback.format_exc(), "vector_data": vector_data.dict()}
            )
            return None

    def get_vector_embedding(self, block_id: UUID) -> Optional[VectorRepresentationSchema]:
        """
        Retrieves the vector embedding associated with a specific block.

        Args:
            block_id (UUID): UUID of the block.

        Returns:
            Optional[VectorRepresentationSchema]: The vector embedding schema if found, None otherwise.
        """
        try:
            response = self.supabase_client.table("vector_representations").select("*").eq("entity_id", str(block_id)).eq("entity_type", "block").single().execute()

            if response.data:
                vector_schema = VectorRepresentationSchema(**response.data)
                self.logger.log(
                    "VectorEmbeddingService",
                    "info",
                    "Vector embedding retrieved successfully.",
                    extra={"vector_id": str(vector_schema.vector_id), "block_id": str(block_id)}
                )
                return vector_schema
            else:
                self.logger.log(
                    "VectorEmbeddingService",
                    "warning",
                    "Vector embedding not found for the block.",
                    extra={"block_id": str(block_id)}
                )
                return None

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during vector embedding retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return None

    def update_vector_embedding(self, block_id: UUID, new_vector: Optional[List[float]] = None, taxonomy_filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Updates the vector embedding for a specific block.

        Args:
            block_id (UUID): UUID of the block.
            new_vector (Optional[List[float]]): New vector data to update.
            taxonomy_filters (Optional[Dict[str, Any]]): New taxonomy constraints for RAG search.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            update_data = {}
            if new_vector:
                update_data["vector"] = new_vector
            if taxonomy_filters:
                update_data["taxonomy_filter"] = taxonomy_filters
            if update_data:
                update_data["updated_at"] = datetime.utcnow()

                response = self.supabase_client.table("vector_representations").update(serialize_dict(update_data)).eq("entity_id", str(block_id)).eq("entity_type", "block").execute()

                if response.error:
                    self.logger.log(
                        "VectorEmbeddingService",
                        "error",
                        "Failed to update vector embedding in Supabase.",
                        extra={"error": response.error.message, "block_id": str(block_id), "update_data": update_data}
                    )
                    return False

                self.logger.log(
                    "VectorEmbeddingService",
                    "info",
                    "Vector embedding updated successfully.",
                    extra={"block_id": str(block_id)}
                )
                return True
            else:
                self.logger.log(
                    "VectorEmbeddingService",
                    "warning",
                    "No update data provided for vector embedding.",
                    extra={"block_id": str(block_id)}
                )
                return False

        except Exception as e:
            self.logger.log(
                "VectorEmbeddingService",
                "critical",
                f"Exception during vector embedding update: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            return False

    def delete_vector_embedding(self, block_id: UUID) -> bool:
        """
        Deletes the vector embedding associated with a specific block from Supabase.

        Args:
            block_id (UUID): UUID of the block.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_client.table("vector_representations").delete().eq("entity_id", str(block_id)).eq("entity_type", "block").execute()

            if response.error:
                self.logger.log(
                    "VectorEmbeddingService",
                    "error",
                    "Failed to delete vector embedding from Supabase.",
                    extra={"error": response.error.message, "block_id": str(block_id)}
                )
                return False

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

    def search_similar_blocks(self, query_vector: List[float], taxonomy_filters: Optional[Dict[str, Any]] = None, top_k: int = 10) -> Optional[List[BlockResponseSchema]]:
        """
        Performs a similarity search over blocks based on the provided query vector and optional taxonomy filters.

        Args:
            query_vector (List[float]): The vector to search against.
            taxonomy_filters (Optional[Dict[str, Any]]): Taxonomy constraints to filter the blocks before similarity search.
            top_k (int): Number of top similar blocks to retrieve.

        Returns:
            Optional[List[BlockResponseSchema]]: List of blocks matching the similarity search criteria.
        """
        try:
            # Step 1: Apply taxonomy filters if provided
            if taxonomy_filters:
                taxonomy_service = TaxonomyService()
                matching_blocks = taxonomy_service.search_blocks_by_taxonomy(taxonomy_filters)
                if not matching_blocks:
                    self.logger.log(
                        "VectorEmbeddingService",
                        "info",
                        "No blocks match the provided taxonomy filters.",
                        extra={"taxonomy_filters": taxonomy_filters}
                    )
                    return []
                block_ids = [str(block['block_id']) for block in matching_blocks]
            else:
                block_ids = None  # No taxonomy filtering

            # Step 2: Construct the similarity search query
            search_query = {
                "vector": query_vector,
                "similarity_threshold": None,  # Adjust as needed
                "top_k": top_k
            }

            # Step 3: Build the Supabase SQL query for similarity search using pg-vector
            if block_ids:
                # If filtering by taxonomy, include WHERE entity_id IN (...)
                supabase_sql = f"""
                    SELECT *
                    FROM vector_representations
                    WHERE entity_type = 'block'
                    AND entity_id IN ({', '.join([f"'{bid}'" for bid in block_ids])})
                    ORDER BY vector <-> '[{', '.join(map(str, query_vector))}]'::vector
                    LIMIT {top_k};
                """
            else:
                # No taxonomy filtering
                supabase_sql = f"""
                    SELECT *
                    FROM vector_representations
                    WHERE entity_type = 'block'
                    ORDER BY vector <-> '[{', '.join(map(str, query_vector))}]'::vector
                    LIMIT {top_k};
                """

            # Execute the SQL query
            response = self.supabase_client.rpc("pg_execute_sql", {"sql": supabase_sql}).execute()

            if response.error:
                self.logger.log(
                    "VectorEmbeddingService",
                    "error",
                    "Failed to execute similarity search query.",
                    extra={"error": response.error.message, "sql": supabase_sql}
                )
                return None

            similar_vectors = response.data

            if not similar_vectors:
                self.logger.log(
                    "VectorEmbeddingService",
                    "info",
                    "No similar vectors found for the query.",
                    extra={"query_vector": query_vector, "taxonomy_filters": taxonomy_filters}
                )
                return []

            # Extract block IDs from the similar vectors
            similar_block_ids = [UUID(vector['entity_id']) for vector in similar_vectors]

            # Retrieve block details
            block_service = BlockService()
            similar_blocks = block_service.get_blocks_by_ids(similar_block_ids)

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
def main():
    """
    Main function to test basic CRUD operations of the VectorEmbeddingService.
    """
    import json

    service = VectorEmbeddingService()

    # Test data
    test_block_id = uuid4()
    test_vector = [0.1] * 512  # Example 512-dimensional vector
    test_taxonomy_filters = {"category": "Climate"}

    # Create Vector Embedding
    vector_data = VectorRepresentationSchema(
        vector_id=uuid4(),
        entity_type="block",
        entity_id=test_block_id,
        vector=test_vector,
        taxonomy_filter=test_taxonomy_filters,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    created_vector = service.create_vector_embedding(vector_data)
    if created_vector:
        print(f"Vector Embedding Created: {created_vector.vector_id}")

    # Retrieve Vector Embedding
    retrieved_vector = service.get_vector_embedding(test_block_id)
    if retrieved_vector:
        print(f"Vector Embedding Retrieved: {retrieved_vector.vector_id}")

    # Update Vector Embedding
    new_vector = [0.2] * 512
    update_success = service.update_vector_embedding(test_block_id, new_vector=new_vector, taxonomy_filters={"category": "Weather"})
    if update_success:
        print("Vector Embedding Updated Successfully.")

    # Perform Similarity Search
    search_results = service.search_similar_blocks(query_vector=new_vector, taxonomy_filters={"category": "Weather"}, top_k=5)
    if search_results:
        print(f"Similarity Search Results: {[block.block_id for block in search_results]}")

    # Delete Vector Embedding
    deletion_success = service.delete_vector_embedding(test_block_id)
    if deletion_success:
        print("Vector Embedding Deleted Successfully.")

if __name__ == "__main__":
    main()
