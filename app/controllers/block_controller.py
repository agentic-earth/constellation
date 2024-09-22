# app/controllers/block_controller.py

"""
Block Controller Module

This module defines the BlockController class responsible for managing block-related operations.
It orchestrates interactions between BlockService, TaxonomyService, and VectorEmbeddingService to
perform operations that involve blocks, taxonomy, and vector embeddings. Additionally, it handles
search functionalities based on taxonomy filters and vector similarity.

Responsibilities:
- Coordinating between BlockService, TaxonomyService, and VectorEmbeddingService to perform complex workflows.
- Handling CRUD operations for blocks, including optional taxonomy and vector embeddings.
- Managing similarity searches with optional taxonomy filters.
- Ensuring transactional integrity and robust error handling.
- Managing audit logs through AuditService.

Design Philosophy:
- Maintain high cohesion by focusing solely on block-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.
"""

import traceback
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status

from app.services.block_service import BlockService
from app.services.taxonomy_service import TaxonomyService
from app.services.vector_embedding_service import VectorEmbeddingService
from app.services.audit_service import AuditService  # Assuming AuditService exists
from app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema,
    VectorRepresentationSchema
)
from app.taxonomy import SearchQuery, SearchResult
from app.logger import ConstellationLogger


class BlockController:
    """
    BlockController manages all block-related operations, coordinating between BlockService,
    TaxonomyService, and VectorEmbeddingService to perform CRUD operations, manage taxonomy,
    handle vector embeddings, and execute similarity searches.
    """

    def __init__(self):
        """
        Initializes the BlockController with instances of BlockService, TaxonomyService,
        VectorEmbeddingService, and AuditService, along with the ConstellationLogger for
        logging purposes.
        """
        self.block_service = BlockService()
        self.taxonomy_service = TaxonomyService()
        self.vector_embedding_service = VectorEmbeddingService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Block CRUD Operations
    # -------------------

    def create_block(self, block_data: BlockCreateSchema) -> Optional[BlockResponseSchema]:
        """
        Creates a new block along with its optional taxonomy.

        Args:
            block_data (BlockCreateSchema): The data required to create a new block, including optional taxonomy and metadata.

        Returns:
            Optional[BlockResponseSchema]: The created block data if successful, None otherwise.
        """
        try:
            # Step 1: Create Block
            block = self.block_service.create_block(block_data)
            if not block:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Block creation failed.")

            # Step 2: Associate Taxonomy (if provided)
            if block_data.taxonomy:
                taxonomy_success = self.taxonomy_service.create_taxonomy_for_block(block_id=block.block_id, taxonomy=block_data.taxonomy)
                if not taxonomy_success:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid taxonomy data.")
                    # Optionally, handle rollback of block creation


            # Step 3: Create Vector Embedding (if metadata provided)

            # Step 4: Log the creation in Audit Logs
            audit_log = {
                "user_id": block_data.created_by,  # Assuming `created_by` exists in BlockCreateSchema
                "action_type": "CREATE",
                "entity_type": "block",
                "entity_id": str(block.block_id),
                "details": f"Block '{block.name}' created with taxonomy and vector embedding."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Block created successfully with taxonomy and vector embedding.",
                extra={"block_id": str(block.block_id)}
            )
            return block

        except HTTPException as he:
            # Existing exception handling
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block creation: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            # Existing exception handling
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block creation: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    def get_block_by_id(self, block_id: UUID) -> Optional[BlockResponseSchema]:
        """
        Retrieves a block by its unique identifier, including its taxonomy and vector embedding.

        Args:
            block_id (UUID): The UUID of the block to retrieve.

        Returns:
            Optional[BlockResponseSchema]: The block data if found, None otherwise.
        """
        try:
            # Step 1: Retrieve Block
            block = self.block_service.get_block_by_id(block_id)
            if not block:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found.")

            # Step 2: Retrieve Taxonomy
            taxonomy = self.taxonomy_service.get_taxonomy_for_block(block_id=block.block_id)
            if taxonomy:
                block.taxonomy = taxonomy
            else:
                self.logger.log(
                    "BlockController",
                    "warning",
                    f"No taxonomy found for block {block.block_id}.",
                    extra={"block_id": str(block.block_id)}
                )

            # Step 3: Retrieve Vector Embedding
            vector_embedding = self.vector_embedding_service.get_vector_embedding(block_id=block.block_id)
            if vector_embedding:
                block.vector_embedding = vector_embedding.dict()
            else:
                self.logger.log(
                    "BlockController",
                    "warning",
                    f"No vector embedding found for block {block.block_id}.",
                    extra={"block_id": str(block.block_id)}
                )

            # Step 4: Log the retrieval in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "READ",
                "entity_type": "block",
                "entity_id": str(block.block_id),
                "details": f"Block '{block.name}' retrieved."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Block retrieved successfully.",
                extra={"block_id": str(block.block_id)}
            )
            return block

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block retrieval: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    def update_block(self, block_id: UUID, update_data: BlockUpdateSchema) -> Optional[BlockResponseSchema]:
        """
        Updates an existing block's information, including optional taxonomy and vector embedding.

        Args:
            block_id (UUID): The UUID of the block to update.
            update_data (BlockUpdateSchema): The data to update for the block, including optional taxonomy and metadata.

        Returns:
            Optional[BlockResponseSchema]: The updated block data if successful, None otherwise.
        """
        try:
            # Step 1: Update Block Details
            block = self.block_service.update_block(block_id, update_data)
            if not block:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Block update failed.")

            # Step 2: Update Taxonomy Associations (if taxonomy provided)
            if update_data.taxonomy:
                taxonomy_success = self.taxonomy_service.create_taxonomy_for_block(block_id=block.block_id, taxonomy=update_data.taxonomy)
                if not taxonomy_success:
                    self.logger.log(
                        "BlockController",
                        "warning",
                        f"Block {block.block_id} updated without taxonomy associations.",
                        extra={"block_id": str(block.block_id)}
                    )
                    # Optionally, handle accordingly

            # Step 4: Log the update in Audit Logs
            audit_log = {
                "user_id": update_data.updated_by,  # Assuming `updated_by` exists in BlockUpdateSchema
                "action_type": "UPDATE",
                "entity_type": "block",
                "entity_id": str(block.block_id),
                "details": f"Block '{block.name}' updated with fields: {list(update_data.dict().keys())}."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Block updated successfully.",
                extra={"block_id": str(block.block_id)}
            )
            return block

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block update: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block update: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    def delete_block(self, block_id: UUID) -> bool:
        """
        Deletes a block along with its associated taxonomy and vector embedding.

        Args:
            block_id (UUID): The UUID of the block to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Step 1: Delete Vector Embedding (if exists)
            self.vector_embedding_service.delete_vector_embedding(block_id=block_id)
            if not vector_deletion_success:
                self.logger.log(
                    "BlockController",
                    "warning",
                    f"Failed to delete vector embedding for block {block_id}.",
                    extra={"block_id": str(block_id)}
                )
                # Proceed with block deletion regardless

            # Step 2: Delete Taxonomy Associations
            taxonomy_deletion_success = self.taxonomy_service.delete_taxonomy_for_block(block_id=block_id)
            if not taxonomy_deletion_success:
                self.logger.log(
                    "BlockController",
                    "warning",
                    f"Failed to delete taxonomy associations for block {block_id}.",
                    extra={"block_id": str(block_id)}
                )
                # Proceed with block deletion regardless

            # Step 3: Delete Block
            block_deletion_success = self.block_service.delete_block(block_id)
            if not block_deletion_success:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Block deletion failed.")

            # Step 4: Log the deletion in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "DELETE",
                "entity_type": "block",
                "entity_id": str(block_id),
                "details": f"Block with ID '{block_id}' deleted along with its taxonomy and vector embedding."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Block deleted successfully along with taxonomy and vector embedding.",
                extra={"block_id": str(block_id)}
            )
            return True

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block deletion: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block deletion: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    # -------------------
    # Vector Embedding CRUD Operations
    # -------------------

    def create_vector_embedding(self, block_id: UUID, text: str, taxonomy_filters: Optional[Dict[str, Any]] = None) -> Optional[VectorRepresentationSchema]:
        """
        Creates a vector embedding for a specific block.

        Args:
            block_id (UUID): UUID of the block.
            text (str): Text data to generate the embedding.
            taxonomy_filters (Optional[Dict[str, Any]]): Taxonomy constraints for the embedding.

        Returns:
            Optional[VectorRepresentationSchema]: The created vector embedding schema if successful, None otherwise.
        """
        try:
            vector_embedding = self.vector_embedding_service.create_vector_embedding(
                block_id=block_id,
                text=text,
                taxonomy_filters=taxonomy_filters
            )
            if not vector_embedding:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vector embedding creation failed.")

            # Log the creation in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "CREATE",
                "entity_type": "vector_embedding",
                "entity_id": str(vector_embedding.vector_id),
                "details": f"Vector embedding created for block '{block_id}'."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Vector embedding created successfully.",
                extra={"block_id": str(block_id), "vector_id": str(vector_embedding.vector_id)}
            )
            return vector_embedding

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding creation: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding creation: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    def get_vector_embedding(self, block_id: UUID) -> Optional[VectorRepresentationSchema]:
        """
        Retrieves the vector embedding associated with a specific block.

        Args:
            block_id (UUID): UUID of the block.

        Returns:
            Optional[VectorRepresentationSchema]: The vector embedding schema if found, None otherwise.
        """
        try:
            vector_embedding = self.vector_embedding_service.get_vector_embedding(block_id)
            if not vector_embedding:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vector embedding not found for the block.")

            # Log the retrieval in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "READ",
                "entity_type": "vector_embedding",
                "entity_id": str(vector_embedding.vector_id),
                "details": f"Vector embedding retrieved for block '{block_id}'."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Vector embedding retrieved successfully.",
                extra={"block_id": str(block_id), "vector_id": str(vector_embedding.vector_id)}
            )
            return vector_embedding

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding retrieval: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    def update_vector_embedding(self, block_id: UUID, text: Optional[str] = None, taxonomy_filters: Optional[Dict[str, Any]] = None) -> bool:
        """
        Updates the vector embedding for a specific block.

        Args:
            block_id (UUID): UUID of the block.
            text (Optional[str]): New text data to regenerate the embedding.
            taxonomy_filters (Optional[Dict[str, Any]]): New taxonomy constraints for RAG search.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            update_success = self.vector_embedding_service.update_vector_embedding(block_id, text, taxonomy_filters)
            if not update_success:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vector embedding update failed.")

            # Log the update in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "UPDATE",
                "entity_type": "vector_embedding",
                "entity_id": str(block_id),  # Assuming entity_id refers to block_id
                "details": f"Vector embedding updated for block '{block_id}'."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Vector embedding updated successfully.",
                extra={"block_id": str(block_id)}
            )
            return True

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding update: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding update: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    def delete_vector_embedding(self, block_id: UUID) -> bool:
        """
        Deletes the vector embedding associated with a specific block.

        Args:
            block_id (UUID): UUID of the block.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            deletion_success = self.vector_embedding_service.delete_vector_embedding(block_id)
            if not deletion_success:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vector embedding deletion failed.")

            # Log the deletion in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "DELETE",
                "entity_type": "vector_embedding",
                "entity_id": str(block_id),  # Assuming entity_id refers to block_id
                "details": f"Vector embedding deleted for block '{block_id}'."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                "Vector embedding deleted successfully.",
                extra={"block_id": str(block_id)}
            )
            return True

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding deletion: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding deletion: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")

    # -------------------
    # Similarity Search Operation
    # -------------------

    def perform_similarity_search(self, query_text: str, taxonomy_filters: Optional[Dict[str, Any]] = None, top_k: int = 10) -> Optional[List[BlockResponseSchema]]:
        """
        Performs a similarity search over blocks based on the provided query text and optional taxonomy filters.

        Args:
            query_text (str): The text query to generate the embedding vector for similarity search.
            taxonomy_filters (Optional[Dict[str, Any]]): Taxonomy constraints to filter the blocks before similarity search.
            top_k (int): Number of top similar blocks to retrieve.

        Returns:
            Optional[List[BlockResponseSchema]]: List of blocks matching the similarity search criteria.
        """
        try:
            similar_blocks = self.vector_embedding_service.search_similar_blocks(query_text, taxonomy_filters, top_k)
            if similar_blocks is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Similarity search failed.")

            # Log the search in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "SEARCH",
                "entity_type": "block",
                "entity_id": None,
                "details": f"Similarity search performed with query: '{query_text}' and taxonomy filters: {taxonomy_filters}."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "BlockController",
                "info",
                f"Similarity search completed with {len(similar_blocks)} results.",
                extra={"query_text": query_text, "taxonomy_filters": taxonomy_filters, "top_k": top_k}
            )
            return similar_blocks

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during similarity search: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail}
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during similarity search: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error.")


