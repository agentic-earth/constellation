# app/controllers/edge_controller.py

"""
Edge Controller Module

This module defines the EdgeController class responsible for managing edge-related operations.
It orchestrates interactions between EdgeService and AuditService to perform CRUD operations
and handle search functionalities.

Responsibilities:
- Coordinating between EdgeService and AuditService to perform edge-related workflows.
- Handling CRUD operations for edges.
- Managing search functionalities with optional filtering.
- Ensuring transactional integrity and robust error handling.
- Managing audit logs through AuditService.

Design Philosophy:
- Maintain high cohesion by focusing solely on edge-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.
"""

import traceback
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status

from backend.app.features.core.services.edge_service import EdgeService
from backend.app.features.core.services.audit_service import AuditService
from backend.app.schemas import (
    EdgeCreateSchema,
    EdgeUpdateSchema,
    EdgeResponseSchema,
    EdgeVerificationRequestSchema,
    EdgeVerificationResponseSchema,
)
from backend.app.logger import ConstellationLogger

from prisma.models import edges as PrismaEdge


class EdgeController:
    """
    EdgeController manages all edge-related operations, coordinating between EdgeService
    to perform CRUD operations and handle search functionalities.
    """

    def __init__(self, prisma: Prisma):
        """
        Initializes the EdgeController with instances of EdgeService and AuditService,
        along with the ConstellationLogger for logging purposes.
        """
        self.prisma = prisma
        self.edge_service = EdgeService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Edge CRUD Operations
    # -------------------

    async def create_edge(self, edge_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Creates a new edge.

        Args:
            edge_data (EdgeCreateSchema): The data required to create a new edge.

        Returns:
            EdgeResponseSchema: The created edge data if successful.

        Raises:
            HTTPException: If edge creation fails due to validation or server errors.
        """
        try:
            async with self.prisma.tx() as tx:
                edge_create_data = {
                    "name": edge_data["name"],
                    "edge_type": edge_data["edge_type"],
                    "description": edge_data["description"],
                }
                # Step 1: Create Edge
                edge = await self.edge_service.create_edge(tx, edge_create_data)
                if not edge:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Edge creation failed due to invalid data.",
                    )

                # Step 2: Log the creation in Audit Logs
                audit_log = {
                    "user_id": edge_data.created_by,  # Assuming `created_by` exists in EdgeCreateSchema
                    "action_type": "CREATE",
                    "entity_type": "edge",
                    "entity_id": str(edge.edge_id),
                    "details": f"Edge '{edge.name}' created successfully.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Step 3: Log the creation in ConstellationLogger
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge created successfully.",
                    extra={"edge_id": str(edge.edge_id)},
                )
                return edge

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "EdgeController",
                "error",
                f"HTTPException during edge creation: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge creation: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during edge creation.",
            )

    async def get_edge_by_id(self, edge_id: UUID) -> Optional[PrismaEdge]:
        """
        Retrieves an edge by its unique identifier.

        Args:
            edge_id (UUID): The UUID of the edge to retrieve.

        Returns:
            EdgeResponseSchema: The edge data if found.

        Raises:
            HTTPException: If the edge is not found or retrieval fails.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Retrieve Edge
                edge = await self.edge_service.get_edge_by_id(tx, edge_id)
                if not edge:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Edge not found."
                    )

                # Step 2: Log the retrieval in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "READ",
                    "entity_type": "edge",
                    "entity_id": str(edge.edge_id),
                    "details": f"Edge '{edge.name}' retrieved successfully.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Step 3: Log the retrieval in ConstellationLogger
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge retrieved successfully.",
                    extra={"edge_id": str(edge.edge_id)},
                )
                return edge

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "EdgeController",
                "error",
                f"HTTPException during edge retrieval: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge retrieval: {str(e)}",
                extra={"traceback": traceback.format_exc(), "edge_id": str(edge_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during edge retrieval.",
            )

    async def update_edge(self, edge_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Updates an existing edge's information.

        Args:
            edge_id (UUID): The UUID of the edge to update.
            update_data (EdgeUpdateSchema): The data to update for the edge.

        Returns:
            EdgeResponseSchema: The updated edge data if successful.

        Raises:
            HTTPException: If edge update fails due to validation or server errors.
        """
        try:
            async with self.prisma.tx() as tx:
                update_edge_data = {
                    "name": update_data["name"],
                    "edge_type": update_data["edge_type"],
                    "description": update_data["description"],
                }
                # Step 1: Update Edge Details
                edge = await self.edge_service.update_edge(tx, edge_id, update_edge_data)
                if not edge:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Edge update failed due to invalid data.",
                    )

                # Step 2: Log the update in Audit Logs
                audit_log = {
                    "user_id": update_data.updated_by,  # Assuming `updated_by` exists in EdgeUpdateSchema
                    "action_type": "UPDATE",
                    "entity_type": "edge",
                    "entity_id": str(edge.edge_id),
                    "details": f"Edge '{edge.name}' updated with fields: {list(update_data.dict().keys())}.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Step 3: Log the update in ConstellationLogger
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge updated successfully.",
                    extra={"edge_id": str(edge.edge_id)},
                )
                return edge

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "EdgeController",
                "error",
                f"HTTPException during edge update: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge update: {str(e)}",
                extra={"traceback": traceback.format_exc(), "edge_id": str(edge_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during edge update.",
            )

    def delete_edge(self, edge_id: UUID) -> bool:
        """
        Deletes an edge.

        Args:
            edge_id (UUID): The UUID of the edge to delete.

        Returns:
            bool: True if deletion was successful.

        Raises:
            HTTPException: If edge deletion fails.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Delete Edge
                deletion_success = await self.edge_service.delete_edge(tx, edge_id)
                if not deletion_success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Edge deletion failed.",
                    )

                # Step 2: Log the deletion in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "DELETE",
                    "entity_type": "edge",
                    "entity_id": str(edge_id),
                    "details": f"Edge with ID '{edge_id}' deleted successfully.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Step 3: Log the deletion in ConstellationLogger
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge deleted successfully.",
                    extra={"edge_id": str(edge_id)},
                )
                return True

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "EdgeController",
                "error",
                f"HTTPException during edge deletion: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge deletion: {str(e)}",
                extra={"traceback": traceback.format_exc(), "edge_id": str(edge_id)},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during edge deletion.",
            )

    def list_edges(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PrismaEdge]:
        """
        Retrieves a list of edges with optional filtering and pagination.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the edges.
            limit (int): Maximum number of edges to retrieve.
            offset (int): Number of edges to skip for pagination.

        Returns:
            List[EdgeResponseSchema]: A list of edges if successful.

        Raises:
            HTTPException: If edge listing fails due to server errors.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Retrieve Edges with Filters
                edges = await self.edge_service.list_edges(tx, filters=filters, limit=limit, offset=offset)
                if edges is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve edges.",
                    )

                # Step 2: Log the listing in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "READ",
                    "entity_type": "edge",
                    "entity_id": None,
                    "details": f"Listed edges with filters: {filters}, limit: {limit}, offset: {offset}.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Step 3: Log the listing in ConstellationLogger
                self.logger.log(
                    "EdgeController",
                    "info",
                    f"Listed {len(edges)} edges successfully.",
                    extra={"filters": filters, "limit": limit, "offset": offset},
                )
                return edges

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "EdgeController",
                "error",
                f"HTTPException during edge listing: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge listing: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during edge listing.",
            )

    def search_edges(
        self, query_params: Dict[str, Any], limit: int = 100, offset: int = 0
    ) -> List[EdgeResponseSchema]:
        """
        Searches for edges based on provided query parameters with pagination.

        Args:
            query_params (Dict[str, Any]): A dictionary of query parameters for filtering.
            limit (int): Maximum number of edges to retrieve.
            offset (int): Number of edges to skip for pagination.

        Returns:
            List[EdgeResponseSchema]: A list of edges matching the search criteria.

        Raises:
            HTTPException: If edge search fails due to server errors.
        """
        try:
            async with self.prisma.tx() as tx:
                # Step 1: Perform Search
                edges = await self.edge_service.search_edges(tx, query_params=query_params, limit=limit, offset=offset)
                if edges is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Edge search failed.",
                    )

                # Step 2: Count Total Matching Edges
                total_count = await self.edge_service.count_edges(tx, filters=query_params)
                if total_count is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to count edges.",
                    )

                # Step 3: Calculate Total Pages
                total_pages = (total_count + limit - 1) // limit if limit > 0 else 1

                # Step 4: Log the search in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "SEARCH",
                    "entity_type": "edge",
                    "entity_id": None,
                    "details": f"Edge search performed with filters: {query_params}, limit: {limit}, offset: {offset}.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Step 5: Log the search in ConstellationLogger
                self.logger.log(
                    "EdgeController",
                    "info",
                    f"Edge search completed with {len(edges)} results.",
                    extra={
                        "query_params": query_params,
                        "limit": limit,
                        "offset": offset,
                        "total_count": total_count,
                        "total_pages": total_pages,
                    },
                )

                # Note: Since we are restricted from using undefined schemas, we'll return the list along with pagination metadata as a dictionary.
                # This can be adjusted based on how the response is handled in the API routes.

                return edges

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "EdgeController",
                "error",
                f"HTTPException during edge search: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge search: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during edge search.",
            )

    # -------------------
    # Edge Verification Endpoint
    # -------------------
    # TODO: to be fixed
    def verify_edge(
        self, verification_request: EdgeVerificationRequestSchema
    ) -> EdgeVerificationResponseSchema:
        """
        Verifies if an edge can be created between two blocks.

        Args:
            verification_request (EdgeVerificationRequestSchema): The source and target block IDs.

        Returns:
            EdgeVerificationResponseSchema: The result of the verification.
        """
        try:
            # Use EdgeService to perform the verification
            verification_result = self.edge_service.can_connect_blocks(
                source_block_id=verification_request.source_block_id,
                target_block_id=verification_request.target_block_id,
            )

            # Log the verification in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "READ",
                "entity_type": "edge",
                "entity_id": "verification",
                "details": f"Edge verification between {verification_request.source_block_id} and {verification_request.target_block_id}.",
            }
            self.audit_service.create_audit_log(audit_log)

            # Log the verification event
            self.logger.log(
                "EdgeController",
                "info",
                "Edge verification performed.",
                extra={
                    "source_block_id": str(verification_request.source_block_id),
                    "target_block_id": str(verification_request.target_block_id),
                    "can_connect": verification_result.can_connect,
                },
            )
            return verification_result

        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge verification: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during edge verification.",
            )
