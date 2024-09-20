# app/controllers/edge_controller.py

"""
Edge Controller Module

This module defines the EdgeController class responsible for managing edge-related operations.
It handles both basic CRUD operations for edges and complex workflows that may involve
multiple services or additional business logic.

Responsibilities:
- Coordinating between EdgeService and AuditService to perform edge-related operations.
- Managing transactions to ensure data consistency across multiple service operations.
- Handling higher-level business logic specific to edges.

Design Philosophy:
- Maintain high cohesion by focusing solely on edge-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.

Usage Example:
    from app.controllers import EdgeController

    edge_controller = EdgeController()
    new_edge = edge_controller.create_edge(edge_data)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from app.services import (
    EdgeService,
    AuditService
)
from app.schemas import (
    EdgeCreateSchema,
    EdgeUpdateSchema,
    EdgeResponseSchema
)
from app.logger import ConstellationLogger

class EdgeController:
    """
    EdgeController manages all edge-related operations, coordinating between EdgeService
    and AuditService to perform CRUD operations and handle complex business logic.
    """

    def __init__(self):
        """
        Initializes the EdgeController with instances of EdgeService and AuditService,
        along with the ConstellationLogger for logging purposes.
        """
        self.edge_service = EdgeService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Basic Edge Operations
    # -------------------

    def create_edge(self, edge_data: EdgeCreateSchema) -> Optional[EdgeResponseSchema]:
        """
        Creates a new edge.

        Args:
            edge_data (EdgeCreateSchema): The data required to create a new edge.

        Returns:
            Optional[EdgeResponseSchema]: The created edge data if successful, None otherwise.
        """
        try:
            edge = self.edge_service.create_edge(edge_data)
            if edge:
                # Optionally, create an audit log for the creation
                audit_log = {
                    "user_id": edge_data.created_by,  # Assuming `created_by` exists in EdgeCreateSchema
                    "action_type": "CREATE",
                    "entity_type": "edge",
                    "entity_id": edge.edge_id,
                    "details": f"Edge '{edge.name}' created."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge created successfully.",
                    edge_id=edge.edge_id
                )
            return edge
        except Exception as e:
            self.logger.log(
                "EdgeController",
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
            edge = self.edge_service.get_edge_by_id(edge_id)
            if edge:
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge retrieved successfully.",
                    edge_id=edge.edge_id
                )
            return edge
        except Exception as e:
            self.logger.log(
                "EdgeController",
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
            edge = self.edge_service.update_edge(edge_id, update_data)
            if edge:
                # Optionally, create an audit log for the update
                audit_log = {
                    "user_id": update_data.updated_by,  # Assuming `updated_by` exists in EdgeUpdateSchema
                    "action_type": "UPDATE",
                    "entity_type": "edge",
                    "entity_id": edge.edge_id,
                    "details": f"Edge '{edge.name}' updated with fields: {list(update_data.dict().keys())}."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge updated successfully.",
                    edge_id=edge.edge_id
                )
            return edge
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge update: {e}"
            )
            return None

    def delete_edge(self, edge_id: UUID) -> bool:
        """
        Deletes an edge.

        Args:
            edge_id (UUID): The UUID of the edge to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            success = self.edge_service.delete_edge(edge_id)
            if success:
                # Optionally, create an audit log for the deletion
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "DELETE",
                    "entity_type": "edge",
                    "entity_id": edge_id,
                    "details": f"Edge with ID '{edge_id}' deleted."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Edge deleted successfully.",
                    edge_id=edge_id
                )
            return success
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge deletion: {e}"
            )
            return False

    def list_edges(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[EdgeResponseSchema]]:
        """
        Lists edges with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the edges.

        Returns:
            Optional[List[EdgeResponseSchema]]: A list of edges if successful, None otherwise.
        """
        try:
            edges = self.edge_service.list_edges(filters)
            if edges is not None:
                self.logger.log(
                    "EdgeController",
                    "info",
                    f"{len(edges)} edges retrieved successfully.",
                    filters=filters
                )
            return edges
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during listing edges: {e}"
            )
            return None

    # -------------------
    # Complex Edge Operations (If Any)
    # -------------------
    
    # Example of a complex operation: Assigning a version to an edge
    def assign_version_to_edge(self, edge_id: UUID, version_id: UUID) -> bool:
        """
        Assigns a specific version to an edge.

        Args:
            edge_id (UUID): The UUID of the edge.
            version_id (UUID): The UUID of the version to assign.

        Returns:
            bool: True if assignment was successful, False otherwise.
        """
        try:
            success = self.edge_service.assign_version_to_edge(edge_id, version_id)
            if success:
                # Optionally, create an audit log for the version assignment
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "ASSIGN_VERSION",
                    "entity_type": "edge",
                    "entity_id": edge_id,
                    "details": f"Version '{version_id}' assigned to edge '{edge_id}'."
                }
                self.audit_service.create_audit_log(audit_log)
                self.logger.log(
                    "EdgeController",
                    "info",
                    "Version assigned to edge successfully.",
                    edge_id=edge_id,
                    version_id=version_id
                )
            return success
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during assigning version to edge: {e}"
            )
            return False

    def search_edges(self, query: Dict[str, Any]) -> Optional[List[EdgeResponseSchema]]:
        """
        Searches for edges based on provided query parameters.

        Args:
            query (Dict[str, Any]): A dictionary of query parameters for filtering.

        Returns:
            Optional[List[EdgeResponseSchema]]: A list of edges matching the search criteria.
        """
        try:
            edges = self.edge_service.search_edges(query)
            if edges is not None:
                return edges
            else:
                self.logger.log(
                    "EdgeController",
                    "error",
                    "Edge search failed."
                )
                return None
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "critical",
                f"Exception during edge search: {e}"
            )
            return None