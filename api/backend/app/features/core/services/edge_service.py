# app/services/edge_service.py

"""
Edge Service Module

This module encapsulates all edge-related business logic and interactions with the Prisma ORM.
It provides functions to create, retrieve, update, and delete edges, ensuring that all operations are
logged appropriately using the Constellation Logger.

Design Philosophy:
- Utilize Prisma ORM for database operations, ensuring type safety and efficient queries.
- Use Python only for advanced logic that cannot be handled directly by the database.
- Ensure flexibility to adapt to schema changes with minimal modifications.
"""

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from prisma import Prisma
from prisma.models import edges as PrismaEdge
from backend.app.logger import ConstellationLogger


class EdgeService:
    """
    EdgeService class encapsulates all edge-related operations.
    """

    def __init__(self):
        """
        Initializes the EdgeService with the logger.
        """
        self.logger = ConstellationLogger()

    async def create_edge(self, tx: Prisma, edge_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Creates a new edge in the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            edge_data (Dict[str, Any]): The data required to create a new edge.

        Returns:
            Optional[PrismaEdge]: The created edge data if successful, None otherwise.
        """
        try:
            # Prepare edge data dictionary
            create_data = {
                "edge_id": edge_data.get("edge_id", str(uuid4())),
                "name": edge_data.get("name"),
                "edge_type": edge_data.get("edge_type"),
                "description": edge_data.get("description", None),
                "source_block_id": str(edge_data.get("source_block_id")) if edge_data.get("source_block_id") else None,
                "target_block_id": str(edge_data.get("target_block_id")) if edge_data.get("target_block_id") else None,
                "created_at": edge_data.get("created_at", datetime.utcnow()),
                "updated_at": edge_data.get("updated_at", datetime.utcnow()),
                "current_version_id": str(edge_data.get("current_version_id")) if edge_data.get("current_version_id") else None,
            }

            # Remove keys with None values to avoid overwriting existing data with null
            create_data = {k: v for k, v in create_data.items() if v is not None}

            # Create the new edge using Prisma
            created_edge = await tx.edges.create(data=create_data)

            self.logger.log(
                "EdgeService",
                "info",
                f"Edge created successfully: {created_edge.edge_id}",
                extra={
                    "edge_id": created_edge.edge_id,
                    "name": created_edge.name,
                    "edge_type": created_edge.edge_type
                }
            )
            return created_edge
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge creation: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    async def get_edge_by_id(self, tx: Prisma, edge_id: UUID) -> Optional[PrismaEdge]:
        """
        Retrieves an edge by its unique identifier.

        Args:
            tx (Prisma): The Prisma transaction object.
            edge_id (UUID): The UUID of the edge to retrieve.

        Returns:
            Optional[PrismaEdge]: The edge data if found, None otherwise.
        """
        try:
            edge = await tx.edges.find_unique(where={"edge_id": str(edge_id)})

            if edge:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge retrieved successfully",
                    extra={
                        "edge_id": edge.edge_id,
                        "name": edge.name,
                        "edge_type": edge.edge_type
                    }
                )
                return edge
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Edge not found",
                    extra={"edge_id": str(edge_id)}
                )
                return None
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge retrieval: {exc}",
                extra={"traceback": traceback.format_exc(), "edge_id": str(edge_id)}
            )
            return None

    async def update_edge(self, tx: Prisma, edge_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Updates an existing edge's information.

        Args:
            tx (Prisma): The Prisma transaction object.
            edge_id (UUID): The UUID of the edge to update.
            update_data (Dict[str, Any]): The data to update for the edge.

        Returns:
            Optional[PrismaEdge]: The updated edge data if successful, None otherwise.
        """
        try:
            if not update_data:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "No update data provided",
                    extra={"edge_id": str(edge_id)}
                )
                return None

            # Validate edge_type if it's being updated
            # if 'edge_type' in update_data:
            #     # Implement validation logic if necessary
            #     pass

            # Prepare update data with snake_case keys
            update_dict = {
                "name": update_data.get("name"),
                "edge_type": update_data.get("edge_type"),
                "description": update_data.get("description", None),
                "source_block_id": str(update_data.get("source_block_id")) if update_data.get("source_block_id") else None,
                "target_block_id": str(update_data.get("target_block_id")) if update_data.get("target_block_id") else None,
                "updated_at": update_data.get("updated_at", datetime.utcnow()),
                "current_version_id": str(update_data.get("current_version_id")) if update_data.get("current_version_id") else None,
            }

            # Remove keys with None values to avoid overwriting existing data with null
            update_dict = {k: v for k, v in update_dict.items() if v is not None}

            if not update_dict:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "No valid update data provided after processing.",
                    extra={"edge_id": str(edge_id)}
                )
                return None

            # Update the edge using Prisma
            updated_edge = await tx.edges.update(
                where={"edge_id": str(edge_id)},
                data=update_dict
            )

            self.logger.log(
                "EdgeService",
                "info",
                "Edge updated successfully",
                extra={
                    "edge_id": updated_edge.edge_id,
                    "updated_fields": list(update_dict.keys())
                }
            )
            return updated_edge
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge update: {exc}",
                extra={"traceback": traceback.format_exc(), "edge_id": str(edge_id), "update_data": update_data}
            )
            return None

    async def delete_edge(self, tx: Prisma, edge_id: UUID) -> bool:
        """
        Deletes an edge from the database.

        Args:
            tx (Prisma): The Prisma transaction object.
            edge_id (UUID): The UUID of the edge to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            deleted_edge = await tx.edges.delete(where={"edge_id": str(edge_id)})

            if deleted_edge:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge deleted successfully.",
                    extra={"edge_id": str(edge_id)}
                )
                return True
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Edge not found or already deleted.",
                    extra={"edge_id": str(edge_id)}
                )
                return False
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge deletion: {exc}",
                extra={"traceback": traceback.format_exc(), "edge_id": str(edge_id)}
            )
            return False

    async def list_edges(self, tx: Prisma, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> Optional[List[PrismaEdge]]:
        """
        Retrieves a list of edges with optional filtering and pagination.

        Args:
            tx (Prisma): The Prisma transaction object.
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the edges.
            limit (int): Maximum number of edges to retrieve.
            offset (int): Number of edges to skip for pagination.

        Returns:
            Optional[List[PrismaEdge]]: A list of edges if successful, None otherwise.
        """
        try:
            where_clause = filters or {}
            edges = await tx.edges.find_many(
                where=where_clause,
                take=limit,
                skip=offset
            )

            self.logger.log(
                "EdgeService",
                "info",
                f"{len(edges)} edges retrieved successfully.",
                extra={"filters": filters, "limit": limit, "offset": offset}
            )
            return edges
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during listing edges: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    async def assign_version_to_edge(self, tx: Prisma, edge_id: UUID, version_id: UUID) -> bool:
        """
        Assigns a specific version to an edge by updating the `current_version_id`.

        Args:
            tx (Prisma): The Prisma transaction object.
            edge_id (UUID): The UUID of the edge.
            version_id (UUID): The UUID of the version to assign.

        Returns:
            bool: True if assignment was successful, False otherwise.
        """
        try:
            updated_edge = await tx.edges.update(
                where={"edge_id": str(edge_id)},
                data={"current_version_id": str(version_id)}
            )

            if updated_edge:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Assigned version to edge successfully.",
                    extra={"edge_id": str(edge_id), "version_id": str(version_id)}
                )
                return True
            else:
                self.logger.log(
                    "EdgeService",
                    "error",
                    "Failed to assign version to edge.",
                    extra={"edge_id": str(edge_id), "version_id": str(version_id)}
                )
                return False
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during assigning version to edge: {exc}",
                extra={"traceback": traceback.format_exc(), "edge_id": str(edge_id), "version_id": str(version_id)}
            )
            return False

    # async def search_edges(self, tx: Prisma, query_params: Dict[str, Any], limit: int = 100, offset: int = 0) -> Optional[List[EdgeResponseSchema]]:
    #     """
    #     Searches for edges based on provided query parameters with pagination.

    #     Args:
    #         tx (Prisma): The Prisma transaction object.
    #         query_params (Dict[str, Any]): A dictionary of query parameters for filtering.
    #         limit (int): Maximum number of edges to retrieve.
    #         offset (int): Number of edges to skip for pagination.

    #     Returns:
    #         Optional[List[PrismaEdge]]: A list of edges matching the search criteria.
    #     """
    #     try:
    #         where_clause = {}
    #         for key, value in query_params.items():
    #             if isinstance(value, list):
    #                 where_clause[key] = {"in": value}
    #             else:
    #                 where_clause[key] = {"contains": value, "mode": "insensitive"}

    #         edges = await tx.edge.find_many(
    #             where=where_clause,
    #             take=limit,
    #             skip=offset
    #         )

    #         self.logger.log(
    #             "EdgeService",
    #             "info",
    #             f"{len(edge_responses)} edges found matching the search criteria.",
    #             extra={"query": query_params, "limit": limit, "offset": offset}
    #         )
    #         return edges
    #     except Exception as exc:
    #         self.logger.log(
    #             "EdgeService",
    #             "critical",
    #             f"Exception during edge search: {exc}",
    #             extra={"traceback": traceback.format_exc()}
    #         )
    #         return None

    # async def count_edges(self, tx: Prisma, filters: Optional[Dict[str, Any]] = None) -> Optional[int]:
    #     """
    #     Counts the total number of edges with optional filtering.

    #     Args:
    #         tx (Prisma): The Prisma transaction object.
    #         filters (Optional[Dict[str, Any]]): Key-value pairs to filter the edges.

    #     Returns:
    #         Optional[int]: The count of edges matching the filters, None otherwise.
    #     """
    #     try:
    #         where_clause = filters or {}
    #         count = await tx.edge.count(where=where_clause)

    #         self.logger.log(
    #             "EdgeService",
    #             "info",
    #             f"Total edges count: {count}",
    #             extra={"filters": filters}
    #         )
    #         return count
    #     except Exception as exc:
    #         self.logger.log(
    #             "EdgeService",
    #             "critical",
    #             f"Exception during counting edges: {exc}",
    #             extra={"traceback": traceback.format_exc()}
    #         )
    #         return None

    # # TODO: To be fixed
    # async def can_connect_blocks(self, tx: Prisma, source_block_id: UUID, target_block_id: UUID) -> EdgeVerificationResponseSchema:
    #     """
    #     Determines if two blocks can be connected via an edge based on business rules.

    #     Args:
    #         tx (Prisma): The Prisma transaction object.
    #         source_block_id (UUID): The UUID of the source block.
    #         target_block_id (UUID): The UUID of the target block.

    #     Returns:
    #         Dict[str, Any]: The result of the verification.
    #     """
    #     response = {
    #         "can_connect": True,
    #         "reasons": [],
    #         "existing_edges": []
    #     }
    #     try:
    #         # Rule 1: Check for existing edges
    #         existing = await tx.edges.find_many(
    #             where={
    #                 "source_block_id": str(source_block_id),
    #                 "target_block_id": str(target_block_id)
    #             }
    #         )

    #         if existing:
    #             response["can_connect"] = False
    #             response["reasons"].append("An edge already exists between these blocks.")
    #             response["existing_edges"] = [edge.dict() for edge in existing]

    #         # Rule 2: Enforce specific edge types (example)
    #         # Fetch source and target block types
    #         source_block = await tx.blocks.find_unique(where={"block_id": str(source_block_id)})
    #         target_block = await tx.blocks.find_unique(where={"block_id": str(target_block_id)})

    #         if source_block and target_block:
    #             # Example Rule: Only 'primary' blocks can connect to 'secondary' blocks
    #             if source_block.block_type == "primary" and target_block.block_type != "secondary":
    #                 response["can_connect"] = False
    #                 response["reasons"].append("Primary blocks can only connect to secondary blocks.")

    #         # Rule 3: Prevent cycles (Advanced)
    #         if await self.creates_cycle(tx, source_block_id, target_block_id):
    #             response["can_connect"] = False
    #             response["reasons"].append("Connecting these blocks would create a cycle in the graph.")

    #         return response

    #     except Exception as exc:
    #         self.logger.log(
    #             "EdgeService",
    #             "critical",
    #             f"Exception during block connection verification: {exc}",
    #             extra={"traceback": traceback.format_exc()}
    #         )
    #         response["can_connect"] = False
    #         response["reasons"].append("An error occurred during verification.")
    #         return response

    # async def creates_cycle(self, tx: Prisma, source_block_id: UUID, target_block_id: UUID) -> bool:
    #     """
    #     Determines if adding an edge would create a cycle in the graph.

    #     Args:
    #         tx (Prisma): The Prisma transaction object.
    #         source_block_id (UUID): The UUID of the source block.
    #         target_block_id (UUID): The UUID of the target block.

    #     Returns:
    #         bool: True if a cycle would be created, False otherwise.
    #     """
    #     try:
    #         # Perform a Depth-First Search (DFS) from the target block to see if we can reach the source block
    #         stack = [target_block_id]
    #         visited = set()

    #         while stack:
    #             current = stack.pop()
    #             if current == source_block_id:
    #                 return True
    #             if current not in visited:
    #                 visited.add(current)
    #                 # Get all outgoing edges from current block
    #                 edges = await tx.edges.find_many(
    #                     where={"source_block_id": str(current)},
    #                     select={"target_block_id": True}
    #                 )
    #                 for edge in edges:
    #                     stack.append(UUID(edge.target_block_id))
    #         return False
    #     except Exception as e:
    #         self.logger.log(
    #             "EdgeService",
    #             "critical",
    #             f"Exception during cycle detection: {str(e)}",
    #             extra={"traceback": traceback.format_exc(), "source_block_id": str(source_block_id), "target_block_id": str(target_block_id)}
    #         )
    #         # Default to cycle creation prevention on error
    #         return True