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

from backend.app.features.core.services.block_service import BlockService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from backend.app.features.core.services.vector_embedding_service import (
    VectorEmbeddingService,
)
from backend.app.features.core.services.audit_service import (
    AuditService,
)
from backend.app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema,
    BlockRetrieveSchema,
    BlockDeleteSchema,
    VectorRepresentationSchema,
    VectorRepresentationCreateSchema,
    VectorRepresentationResponseSchema,
)
from backend.app.taxonomy import SearchQuery, SearchResult
from backend.app.logger import ConstellationLogger
from prisma import Prisma


class BlockController:
    """
    BlockController manages all block-related operations, coordinating between BlockService,
    TaxonomyService, and VectorEmbeddingService to perform CRUD operations, manage taxonomy,
    handle vector embeddings, and execute similarity searches.
    """

    def __init__(self, prisma: Prisma):
        """
        Initializes the BlockController with instances of BlockService, TaxonomyService,
        VectorEmbeddingService, and AuditService, along with the ConstellationLogger for
        logging purposes.
        """
        self.prisma = prisma
        self.block_service = BlockService()
        self.taxonomy_service = TaxonomyService()
        self.vector_embedding_service = VectorEmbeddingService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    async def create_block(self, user_id: UUID, block_data: BlockCreateSchema) -> Optional[BlockResponseSchema]:
        """
        Creates a new block along with its optional taxonomy.
        Args:
            user_id (UUID): The user ID of the user creating the block.
            block_data (BlockCreateSchema): The data for creating the block.
        Returns:
            Optional[BlockResponseSchema]: The created block.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Create Block
                create_data = {
                    "name": block_data.name,
                    "block_type": block_data.block_type,
                    "description": block_data.description,
                }
                self.logger.log(
                    "BlockController",
                    "info",
                    "block_service.create_block",
                    extra={"block_data": block_data}
                )
                block = await self.block_service.create_block(tx, create_data)
                if not block:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Block creation failed.",
                    )

                # Step 2: Associate Taxonomy (if provided)
                if block_data.taxonomy:
                    taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(
                        tx=tx, block_id=block.block_id, taxonomy=block_data.taxonomy
                    )
                    if not taxonomy_success:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid taxonomy data.",
                        )
                        # Optionally, handle rollback of block creation

                # Step 3: Create Vector Embedding (if metadata provided)
                # if block_data.metadata:
                #     vector_create_data = {
                #         "entity_type": "block",
                #         "entity_id": block.block_id,
                #         "vector": block_data.metadata["vector"], # TODO: assume metadata is a dictionary with a "vector" key
                #         "taxonomy_filter": block_data.taxonomy,
                #         "created_at": datetime.utcnow(),
                #         "updated_at": datetime.utcnow()
                #     }
                #     vector_embedding_success = await self.vector_embedding_service.create_vector_embedding(
                #         tx=tx, vector_data=vector_create_data
                #     )
                #     if not vector_embedding_success:
                #         raise HTTPException(
                #             status_code=status.HTTP_400_BAD_REQUEST,
                #             detail="Vector embedding creation failed.",
                #         )

                # Step 4: Log the creation in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id, # not None
                    "action_type": "CREATE",
                    "entity_type": "block",
                    "entity_id": block.block_id,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)

                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )

                self.logger.log(
                    "BlockController",
                    "info",
                    "Block created successfully with taxonomy and vector embedding.",
                    extra={"block_id": str(block.block_id)},
                )

                block_response = BlockResponseSchema(**block.dict())
                block_response.created_by = block_data.created_by
                block_response.updated_by = block_data.created_by
                block_response.taxonomy = block_data.taxonomy
                return block_response   

        except HTTPException as he:
            # Existing exception handling
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block creation: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Existing exception handling
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block creation: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )
    
    async def get_block_by_id(self, user_id: UUID, block_data: BlockRetrieveSchema) -> Optional[BlockResponseSchema]:
        """
        Retrieves a block by its unique identifier, including its taxonomy and vector embedding.
        Args:
            user_id (UUID): The user ID of the user retrieving the block.
            block_data (BlockRetrieveSchema): The data for retrieving the block.
        Returns:
            Optional[BlockResponseSchema]: The retrieved block.
        """
        try:
            
            async with self.prisma.tx() as tx:
                # Step 1: Retrieve Block
                block = await self.block_service.get_block_by_id(tx, block_data.block_id)
                if not block:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Block not found."
                    )
                ## TODO: how to populate at once
                block_response = BlockResponseSchema(**block.dict())

                # Step 2: Retrieve Taxonomy
                taxonomy = await self.taxonomy_service.get_taxonomy_for_block(
                    tx=tx, block_id=block.block_id
                )

                if not taxonomy:
                    self.logger.log(
                        "BlockController",
                        "warning",
                        f"No taxonomy found for block {block.block_id}.",
                        extra={"block_id": str(block.block_id)},
                    )
                else:
                    block_response.taxonomy = taxonomy
                    
                # Step 3: Retrieve Vector Embedding
                vector_embedding = await self.vector_embedding_service.get_vector_embedding(
                    tx=tx, block_id=block.block_id
                )

                if vector_embedding:
                    block_response.vector_embedding = VectorRepresentationSchema(**vector_embedding.dict())
                else:
                    self.logger.log(
                        "BlockController",
                        "warning",
                        f"No vector embedding found for block {block.block_id}.",
                        extra={"block_id": str(block.block_id)},
                    )

                # Step 4: Log the retrieval in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,
                    "action_type": "READ",
                    "entity_type": "block",
                    "entity_id": block.block_id,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)

                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )

                self.logger.log(
                    "BlockController",
                    "info",
                    "Block retrieved successfully.",
                    extra={"block_id": str(block.block_id)},
                )

                return block_response

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block retrieval: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )

    async def update_block(self, user_id: UUID, block_id: UUID, update_data: BlockUpdateSchema) -> Optional[BlockResponseSchema]:
        """
        Updates an existing block's information, including optional taxonomy and vector embedding.
        Args:
            user_id (UUID): The user ID of the user updating the block.
            block_id (UUID): The ID of the block to update.
            update_data (BlockUpdateSchema): The data for updating the block.
        Returns:
            Optional[BlockResponseSchema]: The updated block.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Update Block Details
                update_block_data = {
                    "name": update_data.name,
                    "block_type": update_data.block_type,
                    "description": update_data.description,
                }

                block = await self.block_service.update_block(tx, block_id, update_block_data)
                if not block:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Block update failed.",
                    )
                block_response = BlockResponseSchema(**block.dict())

                # Step 2: Update Taxonomy Associations (if taxonomy provided)
                if update_data.taxonomy:
                    taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(
                        tx=tx, block_id=block.block_id, taxonomy=update_data.taxonomy
                    )
                    if not taxonomy_success:
                        self.logger.log(
                            "BlockController",
                            "warning",
                            f"Block {block.block_id} updated without taxonomy associations.",
                            extra={"block_id": str(block.block_id)},
                        )
                    else:
                        block_response.taxonomy = update_data.taxonomy

                # Step 3: Update Vector Embedding (if metadata provided)
                # if update_data.metadata:
                #     vector_update_data = {
                #         "entity_type": "block",
                #         "entity_id": block.block_id,
                #         "vector": update_data.metadata["vector"], # TODO: assume metadata is a dictionary with a "vector" key
                #         "taxonomy_filter": update_data.taxonomy,
                #         "updated_at": datetime.utcnow()
                #     }
                #     vector_embedding_success = await self.vector_embedding_service.update_vector_embedding(
                #         tx=tx, block_id=block.block_id, update_data=vector_update_data
                #     )
                #     if not vector_embedding_success:
                #         raise HTTPException(
                #             status_code=status.HTTP_400_BAD_REQUEST,
                #             detail="Vector embedding update failed.",
                #         )


                # Step 4: Log the update in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,  # not None
                    "action_type": "UPDATE",
                    "entity_type": "block",
                    "entity_id": block.block_id,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)

                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )

                self.logger.log(
                    "BlockController",
                    "info",
                    "Block updated successfully.",
                    extra={"block_id": str(block.block_id)},
                )

                block_response.updated_by = update_data.updated_by

                return block_response

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block update: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block update: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )

    async def delete_block(self, user_id: UUID, block_data: BlockDeleteSchema) -> bool:
        """
        Deletes a block along with its associated taxonomy and vector embedding.
        Args:
            user_id (UUID): The user ID of the user deleting the block.
            block_data (BlockDeleteSchema): The data for deleting the block.
        Returns:
            bool: True if the block was deleted successfully, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Delete Vector Embedding
                await self.vector_embedding_service.delete_vector_embedding(tx=tx, block_id=block_data.block_id)

                # Delete Block
                deleted = await self.block_service.delete_block(tx=tx, block_id=block_data.block_id)
                if not deleted:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Block deletion failed.",
                    )

                # Log the deletion in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,  # Replace with actual user ID if available
                    "action_type": "DELETE",
                    "entity_type": "block",
                    "entity_id": block_data.block_id,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)

                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )

                self.logger.log(
                    "BlockController",
                    "info",
                    "Block deleted successfully along with taxonomy and vector embedding.",
                    extra={"block_id": str(block_data.block_id)},
                )
                return True

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during block deletion: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during block deletion: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_data.block_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )

    # -------------------
    # Vector Embedding CRUD Operations
    # -------------------
    
    async def update_vector_embedding(self, user_id: UUID, block_id: UUID, update_data: VectorRepresentationCreateSchema) -> Optional[VectorRepresentationResponseSchema]:
        """
        Updates the vector embedding associated with a specific block.
        Args:
            user_id (UUID): The user ID of the user updating the vector embedding.
            block_id (UUID): The ID of the block to update.
            update_data (VectorRepresentationCreateSchema): The data for updating the vector embedding.
        Returns:
            Optional[VectorRepresentationResponseSchema]: The updated vector embedding.
        """
        try:
            async with self.prisma.tx() as tx:
                update_vector_data = {
                    "entity_type": "block",
                    "entity_id": block_id,
                    "vector": update_data.vector,
                    "taxonomy_filter": update_data.taxonomy_filter,
                    "updated_at": datetime.utcnow()
                }
                
                # remove None values from update_vector_data
                update_vector_data = {k: v for k, v in update_vector_data.items() if v is not None}
                
                updated_vector = await self.vector_embedding_service.update_vector_embedding(
                    tx=tx, block_id=block_id, update_data=update_vector_data
                )
                if not updated_vector:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Vector embedding update failed.",
                    )
    
                # Log the update in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,  # Replace with actual user ID if available
                    "action_type": "UPDATE",
                    "entity_type": "vector_embedding",
                    "entity_id": block_id,  # Assuming entity_id refers to block_id
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)

                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )
    
                self.logger.log(
                    "BlockController",
                    "info",
                    "Vector embedding updated successfully.",
                    extra={"block_id": str(block_id)},
                )

                return VectorRepresentationResponseSchema(**updated_vector.dict())
    
        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding update: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding update: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )

    async def get_vector_embedding(self, user_id: UUID, block_id: UUID) -> Optional[VectorRepresentationResponseSchema]:
        """
        Retrieves the vector embedding associated with a specific block.
        Args:
            user_id (UUID): The user ID of the user retrieving the vector embedding.
            block_id (UUID): The ID of the block to retrieve.
        Returns:
            Optional[VectorRepresentationResponseSchema]: The retrieved vector embedding.
        """
        try:
            async with self.prisma.tx() as tx:
                vector_embedding = await self.vector_embedding_service.get_vector_embedding(
                    tx=tx, block_id=block_id
                )
                if not vector_embedding:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Vector embedding not found for the block.",
                    )
    
                # Log the retrieval in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,  # Replace with actual user ID if available
                    "action_type": "READ",
                    "entity_type": "vector_embedding",
                    "entity_id": block_id,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)
                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )
    
                self.logger.log(
                    "BlockController",
                    "info",
                    "Vector embedding retrieved successfully.",
                    extra={
                        "block_id": str(block_id),
                        "vector_id": str(vector_embedding.vector_id),
                    },
                )
                return VectorRepresentationResponseSchema(**vector_embedding.dict())
    
        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding retrieval: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )

    async def create_vector_embedding(self, user_id: UUID, vector_data: VectorRepresentationCreateSchema) -> Optional[VectorRepresentationResponseSchema]:
        """
        Creates a new vector embedding for a specific block.
        Args:
            user_id (UUID): The user ID of the user creating the vector embedding.
            vector_data (VectorRepresentationCreateSchema): The data for creating the vector embedding.
        Returns:
            Optional[VectorRepresentationResponseSchema]: The created vector embedding.
        """
        try:
            async with self.prisma.tx() as tx:
                create_vector_data = {
                    "entity_type": "block",
                    "entity_id": vector_data.entity_id,
                    "vector": vector_data.vector,
                    "taxonomy_filter": vector_data.taxonomy_filter,
                }

                vector_embedding = await self.vector_embedding_service.create_vector_embedding(
                    tx=tx, vector_data=create_vector_data
                )

                if vector_embedding is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Vector embedding creation failed.",
                    )
    
                # Log the creation in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,  # Replace with actual user ID if available
                    "action_type": "CREATE",
                    "entity_type": "block",
                    "entity_id": vector_embedding.vector_id,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)

                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )
    
                self.logger.log(
                    "BlockController",
                    "info",
                    "Vector embedding created successfully.",
                    extra={
                        "entity_id": str(vector_data.entity_id),
                        "entity_type": vector_data.entity_type,
                    },
                )
                return VectorRepresentationResponseSchema(**vector_embedding.dict())
    
        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding creation: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding creation: {str(e)}",
                extra={
                    "traceback": traceback.format_exc(),
                    "entity_id": str(vector_data.entity_id),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )

    async def delete_vector_embedding(self, user_id: UUID, block_id: UUID) -> bool:
        """
        Deletes the vector embedding associated with a specific block.
        Args:
            user_id (UUID): The user ID of the user deleting the vector embedding.
            block_id (UUID): The ID of the block to delete.
        Returns:
            bool: True if the vector embedding was deleted successfully, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                deletion_success = await self.vector_embedding_service.delete_vector_embedding(
                    tx=tx, block_id=block_id
                )
                if not deletion_success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Vector embedding deletion failed.",
                    )
    
                # Log the deletion in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,  # Replace with actual user ID if available
                    "action_type": "DELETE",
                    "entity_type": "vector_embedding",
                    "entity_id": block_id,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)
                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )
    
                self.logger.log(
                    "BlockController",
                    "info",
                    "Vector embedding deleted successfully.",
                    extra={"block_id": str(block_id)},
                )
                return True
    
        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during vector embedding deletion: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during vector embedding deletion: {str(e)}",
                extra={"traceback": traceback.format_exc(), "block_id": str(block_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )

    # -------------------
    # Similarity Search Operation
    # -------------------

    # TODO: change query_text to query_vector
    async def perform_similarity_search(
        self,
        user_id: UUID,
        query_text: str,
        taxonomy_filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
    ) -> Optional[List[BlockResponseSchema]]:
        """
        Performs a similarity search over blocks based on the provided query text and optional taxonomy filters.
        Args:
            user_id (UUID): The user ID of the user performing the similarity search.
            query_text (str): The text to perform the similarity search on.
            taxonomy_filters (Optional[Dict[str, Any]]): Optional taxonomy filters for the similarity search.
            top_k (int): The number of results to return.
        Returns:
            Optional[List[BlockResponseSchema]]: The list of similar blocks.
        """
        try:
            async with self.prisma.tx() as tx:
                similar_blocks = await self.vector_embedding_service.search_similar_blocks(
                    tx=tx, query_text=query_text, taxonomy_filters=taxonomy_filters, top_k=top_k
                )
                if similar_blocks is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Similarity search failed.",
                    )
    
                # Log the search in Audit Logs
                create_audit_log_data = {
                    "user_id": user_id,  # Replace with actual user ID if available
                    "action_type": "SEARCH",
                    "entity_type": "block",
                    "entity_id": None,
                }
                audit_log = await self.audit_service.create_audit_log(tx, create_audit_log_data)
                if not audit_log:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audit log creation failed.",
                    )
    
                self.logger.log(
                    "BlockController",
                    "info",
                    f"Similarity search completed with {len(similar_blocks)} results.",
                    extra={
                        "query_text": query_text,
                        "taxonomy_filters": taxonomy_filters,
                        "top_k": top_k,
                    },
                )
                return similar_blocks

        except HTTPException as he:
            self.logger.log(
                "BlockController",
                "error",
                f"HTTPException during similarity search: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            self.logger.log(
                "BlockController",
                "critical",
                f"Exception during similarity search: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error.",
            )
