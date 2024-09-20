# app/services/edge_service.py

"""
Edge Service Module

This module encapsulates all edge-related business logic and interactions with the Supabase backend.
It provides functions to create, retrieve, update, and delete edges, ensuring that all operations are
logged appropriately using the Constellation Logger.

Design Philosophy:
- Utilize Supabase's REST API for standard CRUD operations for performance and reliability.
- Use Python only for advanced logic that cannot be handled directly by Supabase.
- Ensure flexibility to adapt to schema changes with minimal modifications.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from app.models import Edge, EdgeCreateSchema, EdgeUpdateSchema, EdgeResponseSchema
from app.logger import ConstellationLogger
from app.utils.helpers import SupabaseClientManager
from app.schemas import EdgeResponseSchema
from datetime import datetime


class EdgeService:
    """
    EdgeService class encapsulates all edge-related operations.
    """

    def __init__(self):
        """
        Initializes the EdgeService with the Supabase client and logger.
        """
        self.supabase_manager = SupabaseClientManager()
        self.logger = ConstellationLogger()

    def create_edge(self, edge_data: EdgeCreateSchema) -> Optional[EdgeResponseSchema]:
        """
        Creates a new edge in the Supabase database.

        Args:
            edge_data (EdgeCreateSchema): The data required to create a new edge.

        Returns:
            Optional[EdgeResponseSchema]: The created edge data if successful, None otherwise.
        """
        try:
            # Convert Pydantic schema to dictionary
            data = edge_data.dict()
            response = self.supabase_manager.client.table("edges").insert(data).execute()

            if response.status_code in [200, 201] and response.data:
                created_edge = EdgeResponseSchema(**response.data[0])
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge created successfully",
                    edge_id=created_edge.edge_id,
                    name=created_edge.name
                )
                return created_edge
            else:
                self.logger.log(
                    "EdgeService",
                    "error",
                    "Failed to create edge",
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge creation: {e}"
            )
            return None

    def get_edge_by_id(self, edge_id: UUID) -> Optional[EdgeResponseSchema]:
        """
        Retrieves an edge by its unique identifier.

        Args:
            edge_id (UUID): The UUID of the edge to retrieve.

        Returns:
            Optional[EdgeResponseSchema]: The edge data if found, None otherwise.
        """
        try:
            response = self.supabase_manager.client.table("edges").select("*").eq("edge_id", str(edge_id)).single().execute()

            if response.status_code == 200 and response.data:
                edge = EdgeResponseSchema(**response.data)
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge retrieved successfully",
                    edge_id=edge.edge_id,
                    name=edge.name
                )
                return edge
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Edge not found",
                    edge_id=edge_id,
                    status_code=response.status_code
                )
                return None
        except Exception as e:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge retrieval: {e}"
            )
            return None

    def update_edge(self, edge_id: UUID, update_data: EdgeUpdateSchema) -> Optional[EdgeResponseSchema]:
        """
        Updates an existing edge's information.

        Args:
            edge_id (UUID): The UUID of the edge to update.
            update_data (EdgeUpdateSchema): The data to update for the edge.

        Returns:
            Optional[EdgeResponseSchema]: The updated edge data if successful, None otherwise.
        """
        try:
            data = update_data.dict(exclude_unset=True)
            response = self.supabase_manager.client.table("edges").update(data).eq("edge_id", str(edge_id)).execute()

            if response.status_code == 200 and response.data:
                updated_edge = EdgeResponseSchema(**response.data[0])
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge updated successfully",
                    edge_id=updated_edge.edge_id,
                    updated_fields=list(data.keys())
                )
                return updated_edge
            else:
                self.logger.log(
                    "EdgeService",
                    "error",
                    "Failed to update edge",
                    edge_id=edge_id,
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge update: {e}"
            )
            return None

    def delete_edge(self, edge_id: UUID) -> bool:
        """
        Deletes an edge from the Supabase database.

        Args:
            edge_id (UUID): The UUID of the edge to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_manager.client.table("edges").delete().eq("edge_id", str(edge_id)).execute()

            if response.status_code == 200 and response.count > 0:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge deleted successfully",
                    edge_id=edge_id
                )
                return True
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Edge not found or already deleted",
                    edge_id=edge_id,
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge deletion: {e}"
            )
            return False

    def list_edges(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[EdgeResponseSchema]]:
        """
        Retrieves a list of edges with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the edges.

        Returns:
            Optional[List[EdgeResponseSchema]]: A list of edges if successful, None otherwise.
        """
        try:
            query = self.supabase_manager.client.table("edges").select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.status_code == 200 and response.data:
                edges = [EdgeResponseSchema(**edge) for edge in response.data]
                self.logger.log(
                    "EdgeService",
                    "info",
                    f"{len(edges)} edges retrieved successfully",
                    filters=filters
                )
                return edges
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "No edges found",
                    filters=filters,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during listing edges: {e}"
            )
            return None

    def assign_version_to_edge(self, edge_id: UUID, version_id: UUID) -> bool:
        """
        Assigns a specific version to an edge by updating the current_version_id.

        Args:
            edge_id (UUID): The UUID of the edge.
            version_id (UUID): The UUID of the version to assign.

        Returns:
            bool: True if assignment was successful, False otherwise.
        """
        try:
            data = {"current_version_id": str(version_id)}
            response = self.supabase_manager.client.table("edges").update(data).eq("edge_id", str(edge_id)).execute()

            if response.status_code == 200 and response.data:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Assigned version to edge successfully",
                    edge_id=edge_id,
                    version_id=version_id
                )
                return True
            else:
                self.logger.log(
                    "EdgeService",
                    "error",
                    "Failed to assign version to edge",
                    edge_id=edge_id,
                    version_id=version_id,
                    status_code=response.status_code,
                    error=response.error
                )
                return False
        except Exception as e:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during assigning version to edge: {e}"
            )
            return False
        

   # Existing CRUD methods...

    def search_edges(self, query: Dict[str, Any]) -> Optional[List[EdgeResponseSchema]]:
        """
        Searches for edges based on provided query parameters.

        Args:
            query (Dict[str, Any]): A dictionary of query parameters for filtering.

        Returns:
            Optional[List[EdgeResponseSchema]]: A list of edges matching the search criteria.
        """
        try:
            supabase_query = self.supabase_manager.client.table("edges").select("*")

            # Apply filters based on the query parameters
            for key, value in query.items():
                if isinstance(value, list):
                    supabase_query = supabase_query.in_(key, value)
                else:
                    supabase_query = supabase_query.ilike(key, f"%{value}%")  # Case-insensitive LIKE

            response = supabase_query.execute()

            if response.status_code == 200 and response.data:
                edges = [EdgeResponseSchema(**edge) for edge in response.data]
                self.logger.log(
                    "EdgeService",
                    "info",
                    f"{len(edges)} edges found matching the search criteria.",
                    query=query
                )
                return edges
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "No edges found matching the search criteria.",
                    query=query,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge search: {e}"
            )
            return None
