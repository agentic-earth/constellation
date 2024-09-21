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

import traceback
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.schemas import (
    EdgeResponseSchema,
    EdgeCreateSchema,
    EdgeUpdateSchema,
)
from app.models import EdgeTypeEnum
from app.logger import ConstellationLogger
from app.database import get_supabase_client
from app.utils.serialization_utils import serialize_dict


class EdgeService:
    """
    EdgeService class encapsulates all edge-related operations.
    """

    def __init__(self):
        """
        Initializes the EdgeService with the Supabase client and logger.
        """
        self.client = get_supabase_client()
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
            data = edge_data.dict(exclude_unset=True)

            # Ensure edge_type is a valid enum value
            if not EdgeTypeEnum.has_value(data.get('edge_type')):
                self.logger.log(
                    "EdgeService",
                    "error",
                    f"Invalid edge_type: {data.get('edge_type')}",
                    extra={"edge_type": data.get('edge_type')}
                )
                return None

            # Add created_at and updated_at if not provided
            current_time = datetime.utcnow()
            data.setdefault('created_at', current_time)
            data.setdefault('updated_at', current_time)

            # Serialize the data
            serialized_data = serialize_dict(data)

            # Insert the new edge into the database
            response = self.client.table("edges").insert(serialized_data).execute()

            if response.data:
                # If created_by is not in the response data, set it to None
                response_data = response.data[0]
                response_data.setdefault('created_by', None)

                created_edge = EdgeResponseSchema(**response_data)
                self.logger.log(
                    "EdgeService",
                    "info",
                    f"Edge created successfully: {created_edge.edge_id}",
                    extra={
                        "edge_id": str(created_edge.edge_id),
                        "name": created_edge.name,
                        "edge_type": created_edge.edge_type.value
                    }
                )
                return created_edge
            else:
                self.logger.log(
                    "EdgeService",
                    "error",
                    "Failed to create edge",
                    extra={"error": str(response.error)}
                )
                return None
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge creation: {exc}",
                extra={"traceback": traceback.format_exc()}
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
            response = self.client.table("edges").select("*").eq("edge_id", str(edge_id)).single().execute()

            if response.data:
                edge = EdgeResponseSchema(**response.data)
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge retrieved successfully",
                    extra={
                        "edge_id": str(edge.edge_id),
                        "name": edge.name,
                        "edge_type": edge.edge_type.value
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
                extra={"traceback": traceback.format_exc()}
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

            if not data:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "No update data provided",
                    extra={"edge_id": str(edge_id)}
                )
                return None

            # Ensure edge_type is valid if it's being updated
            if 'edge_type' in data and not EdgeTypeEnum.has_value(data['edge_type']):
                self.logger.log(
                    "EdgeService",
                    "error",
                    f"Invalid edge_type: {data.get('edge_type')}",
                    extra={"edge_type": data.get('edge_type')}
                )
                return None

            # Update the 'updated_at' field
            data['updated_at'] = datetime.utcnow()

            # Serialize the data
            serialized_data = serialize_dict(data)

            # Update the edge in the database
            response = self.client.table("edges").update(serialized_data).eq("edge_id", str(edge_id)).execute()

            if response.data:
                updated_edge = EdgeResponseSchema(**response.data[0])
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge updated successfully",
                    extra={
                        "edge_id": str(updated_edge.edge_id),
                        "updated_fields": list(data.keys())
                    }
                )
                return updated_edge
            else:
                self.logger.log(
                    "EdgeService",
                    "error",
                    "Failed to update edge",
                    extra={"edge_id": str(edge_id), "error": str(response.error)}
                )
                return None
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge update: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    def delete_edge(self, edge_id: UUID) -> bool:
        """
        Deletes an edge from the Supabase database and validates the deletion.

        Args:
            edge_id (UUID): The UUID of the edge to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Perform the delete operation
            response = self.client.table("edges").delete().eq("edge_id", str(edge_id)).execute()

            if response.data and len(response.data) > 0:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge deleted successfully",
                    extra={"edge_id": str(edge_id)}
                )

                # Validate deletion by attempting to retrieve the edge without using .single()
                validation_response = self.client.table("edges").select("*").eq("edge_id", str(edge_id)).execute()

                if not validation_response.data:
                    self.logger.log(
                        "EdgeService",
                        "info",
                        "Deletion validated: Edge no longer exists",
                        extra={"edge_id": str(edge_id)}
                    )
                    return True
                else:
                    self.logger.log(
                        "EdgeService",
                        "error",
                        "Deletion validation failed: Edge still exists",
                        extra={"edge_id": str(edge_id)}
                    )
                    return False
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Edge not found or already deleted",
                    extra={"edge_id": str(edge_id)}
                )
                return False
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge deletion: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    def list_edges(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> Optional[List[EdgeResponseSchema]]:
        """
        Retrieves a list of edges with optional filtering and pagination.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the edges.
            limit (int): Maximum number of edges to retrieve.
            offset (int): Number of edges to skip for pagination.

        Returns:
            Optional[List[EdgeResponseSchema]]: A list of edges if successful, None otherwise.
        """
        try:
            query = self.client.table("edges").select("*").limit(limit).offset(offset)
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.data:
                edges = [EdgeResponseSchema(**edge) for edge in response.data]
                self.logger.log(
                    "EdgeService",
                    "info",
                    f"{len(edges)} edges retrieved successfully",
                    extra={"filters": filters, "limit": limit, "offset": offset}
                )
                return edges
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "No edges found",
                    extra={"filters": filters, "limit": limit, "offset": offset}
                )
                return []
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during listing edges: {exc}",
                extra={"traceback": traceback.format_exc()}
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
            data = {
                "current_version_id": str(version_id),
                "updated_at": datetime.utcnow()
            }
            serialized_data = serialize_dict(data)

            response = self.client.table("edges").update(serialized_data).eq("edge_id", str(edge_id)).execute()

            if response.data and len(response.data) > 0:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Assigned version to edge successfully",
                    extra={"edge_id": str(edge_id), "version_id": str(version_id)}
                )
                return True
            else:
                self.logger.log(
                    "EdgeService",
                    "error",
                    "Failed to assign version to edge",
                    extra={"edge_id": str(edge_id), "version_id": str(version_id), "error": str(response.error)}
                )
                return False
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during assigning version to edge: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    def search_edges(self, query_params: Dict[str, Any], limit: int = 100, offset: int = 0) -> Optional[List[EdgeResponseSchema]]:
        """
        Searches for edges based on provided query parameters with pagination.

        Args:
            query_params (Dict[str, Any]): A dictionary of query parameters for filtering.
            limit (int): Maximum number of edges to retrieve.
            offset (int): Number of edges to skip for pagination.

        Returns:
            Optional[List[EdgeResponseSchema]]: A list of edges matching the search criteria.
        """
        try:
            supabase_query = self.client.table("edges").select("*").limit(limit).offset(offset)

            # Apply filters based on the query parameters
            for key, value in query_params.items():
                if isinstance(value, list):
                    supabase_query = supabase_query.in_(key, value)
                else:
                    supabase_query = supabase_query.ilike(key, f"%{value}%")  # Case-insensitive LIKE

            response = supabase_query.execute()

            if response.data:
                edges = [EdgeResponseSchema(**edge) for edge in response.data]
                self.logger.log(
                    "EdgeService",
                    "info",
                    f"{len(edges)} edges found matching the search criteria.",
                    extra={"query": query_params, "limit": limit, "offset": offset}
                )
                return edges
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "No edges found matching the search criteria.",
                    extra={"query": query_params, "limit": limit, "offset": offset}
                )
                return []
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during edge search: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    def count_edges(self, filters: Optional[Dict[str, Any]] = None) -> Optional[int]:
        """
        Counts the total number of edges with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the edges.

        Returns:
            Optional[int]: The count of edges matching the filters, None otherwise.
        """
        try:
            query = self.client.table("edges").select("*", count='exact')
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.count is not None:
                self.logger.log(
                    "EdgeService",
                    "info",
                    f"Total edges count: {response.count}",
                    extra={"filters": filters}
                )
                return response.count
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Failed to retrieve edges count",
                    extra={"filters": filters}
                )
                return None
        except Exception as exc:
            self.logger.log(
                "EdgeService",
                "critical",
                f"Exception during counting edges: {exc}",
                extra={"traceback": traceback.format_exc()}
            )
            return None


if __name__ == "__main__":
    import traceback

    print("Starting EdgeService tests...")
    edge_service = EdgeService()

    # Function to generate a unique edge name
    def generate_unique_name(base_name):
        import random
        return f"{base_name}_{random.randint(1000, 9999)}"

    try:
        # Create an edge
        edge_name = generate_unique_name("Test-Edge")
        new_edge = EdgeCreateSchema(
            name=edge_name,
            edge_type=EdgeTypeEnum.primary,
            description="This is a test edge"
        )
        print(f"Creating edge: {new_edge}")
        created_edge = edge_service.create_edge(new_edge)

        if created_edge:
            print(f"Created edge: {created_edge}")

            # Get the edge
            retrieved_edge = edge_service.get_edge_by_id(created_edge.edge_id)
            if retrieved_edge:
                print(f"Retrieved edge: {retrieved_edge}")
            else:
                print("Failed to retrieve the created edge.")

            # Update the edge
            update_data = EdgeUpdateSchema(description="Updated description")
            updated_edge = edge_service.update_edge(created_edge.edge_id, update_data)
            if updated_edge:
                print(f"Updated edge: {updated_edge}")
            else:
                print("Failed to update the edge.")

            # List edges
            edges = edge_service.list_edges()
            if edges is not None:
                print(f"Listed {len(edges)} edges:")
                for edge in edges:
                    print(edge)
            else:
                print("Failed to list edges.")

            # Delete the edge
            if edge_service.delete_edge(created_edge.edge_id):
                print("Edge deleted successfully.")
            else:
                print("Failed to delete edge.")

            # Verify deletion
            post_delete_edge = edge_service.get_edge_by_id(created_edge.edge_id)
            if post_delete_edge:
                print("Error: Edge still exists after deletion.")
            else:
                print("Deletion verified: Edge no longer exists.")


            # Create another edge with a different name
            another_edge_name = generate_unique_name("Another-Test-Edge")
            another_edge = EdgeCreateSchema(
                name=another_edge_name,
                edge_type=EdgeTypeEnum.secondary,
                description="This is another test edge"
            )
            created_another_edge = edge_service.create_edge(another_edge)
            if created_another_edge:
                print(f"Created another edge: {created_another_edge}")

                # Get the new edge
                retrieved_another_edge = edge_service.get_edge_by_id(created_another_edge.edge_id)
                if retrieved_another_edge:
                    print(f"Retrieved another edge: {retrieved_another_edge}")
                else:
                    print("Failed to retrieve the created another edge.")

                # Clean up: delete the second edge
                if edge_service.delete_edge(created_another_edge.edge_id):
                    print("Second edge deleted successfully.")
                else:
                    print("Failed to delete second edge.")

                # Verify deletion of the second edge
                post_delete_another_edge = edge_service.get_edge_by_id(created_another_edge.edge_id)
                if post_delete_another_edge:
                    print("Error: Second edge still exists after deletion.")
                else:
                    print("Deletion verified: Second edge no longer exists.")
            else:
                print("Failed to create another edge.")
        else:
            print("Failed to create initial edge.")
    except Exception as exc:
        print(f"An error occurred during the test: {exc}")
        print("Traceback:")
        print(traceback.format_exc())
