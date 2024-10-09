"""
Edge Controller Module

This module implements the Edge Controller, handling operations related to edges.
It integrates audit logging using the AuditService.

Design Pattern:
- Dependency Injection: Prisma client is passed to the controller and subsequently to services.
- Separation of Concerns: Controller handles HTTP requests, delegates business logic to services.

Key Integrations:
1. Audit Logging: Each operation logs relevant audit information via AuditService.
2. Schema Usage: Utilizes existing schemas from schemas.py to ensure consistency.
"""

import asyncio
import traceback
from typing import List, Optional
from uuid import UUID

from prisma import Prisma

from backend.app.logger import ConstellationLogger
from backend.app.features.core.services.audit_service import AuditService
from backend.app.features.core.services.edge_service import EdgeService
from backend.app.schemas import (
    EdgeCreateSchema,
    EdgeUpdateSchema,
    EdgeResponseSchema
)


class EdgeController:
    def __init__(self, prisma_client: Prisma):
        self.prisma = prisma_client
        self.logger = ConstellationLogger()
        self.edge_service = EdgeService()
        self.audit_service = AuditService()

    async def create_edge(self, edge_data: EdgeCreateSchema, user_id: UUID) -> Optional[EdgeResponseSchema]:
        """
        Create a new edge.

        Args:
            edge_data (EdgeCreateSchema): The data required to create an edge.
            user_id (UUID): The ID of the user performing the action.

        Returns:
            Optional[EdgeResponseSchema]: The created edge if successful, None otherwise.
        """
        try:
            edge = await self.edge_service.create_edge(self.prisma, edge_data)
            if edge:
                # Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": "CREATE",
                    "entity_type": "edge",
                    "entity_id": str(edge.id),
                    "details": {"edge_data": edge_data.dict()}
                }
                await self.audit_service.create_audit_log(self.prisma, audit_data)
                self.logger.log("EdgeController", "info", "Edge created successfully.", edge_id=str(edge.id))
                return EdgeResponseSchema.from_orm(edge)
            else:
                self.logger.log("EdgeController", "error", "Failed to create edge.")
                return None
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "error",
                f"Exception in create_edge: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    async def get_edge(self, edge_id: UUID) -> Optional[EdgeResponseSchema]:
        """
        Retrieve an edge by its ID.

        Args:
            edge_id (UUID): The ID of the edge to retrieve.

        Returns:
            Optional[EdgeResponseSchema]: The edge if found, None otherwise.
        """
        try:
            edge = await self.edge_service.get_edge_by_id(self.prisma, edge_id)
            if edge:
                # Audit Logging
                audit_data = {
                    "user_id": "system",  # Assuming system access; adjust as needed
                    "action_type": "READ",
                    "entity_type": "edge",
                    "entity_id": str(edge.id),
                    "details": {"read_action": True}
                }
                await self.audit_service.create_audit_log(self.prisma, audit_data)
                self.logger.log("EdgeController", "info", "Edge retrieved successfully.", edge_id=str(edge.id))
                return EdgeResponseSchema.from_orm(edge)
            else:
                self.logger.log("EdgeController", "warning", "Edge not found.", edge_id=str(edge_id))
                return None
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "error",
                f"Exception in get_edge: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    async def list_edges(
        self,
        filters: Optional[dict] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[EdgeResponseSchema]:
        """
        List edges with optional filtering, pagination.

        Args:
            filters (Optional[dict]): Filters to apply.
            limit (int): Maximum number of edges to retrieve.
            offset (int): Number of edges to skip.

        Returns:
            List[EdgeResponseSchema]: A list of edges.
        """
        try:
            edges = await self.edge_service.list_edges(self.prisma, filters, limit, offset)
            # Audit Logging
            audit_data = {
                "user_id": "system",  # Assuming system access; adjust as needed
                "action_type": "READ",
                "entity_type": "edge",
                "entity_id": "multiple",
                "details": {"filters": filters, "limit": limit, "offset": offset}
            }
            await self.audit_service.create_audit_log(self.prisma, audit_data)
            self.logger.log("EdgeController", "info", f"Listed {len(edges)} edges.")
            return [EdgeResponseSchema.from_orm(edge) for edge in edges]
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "error",
                f"Exception in list_edges: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return []

    async def update_edge(self, edge_id: UUID, update_data: EdgeUpdateSchema, user_id: UUID) -> Optional[EdgeResponseSchema]:
        """
        Update an existing edge.

        Args:
            edge_id (UUID): The ID of the edge to update.
            update_data (EdgeUpdateSchema): The data to update.
            user_id (UUID): The ID of the user performing the action.

        Returns:
            Optional[EdgeResponseSchema]: The updated edge if successful, None otherwise.
        """
        try:
            edge = await self.edge_service.update_edge(self.prisma, edge_id, update_data)
            if edge:
                # Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": "UPDATE",
                    "entity_type": "edge",
                    "entity_id": str(edge.id),
                    "details": {"update_data": update_data.dict()}
                }
                await self.audit_service.create_audit_log(self.prisma, audit_data)
                self.logger.log("EdgeController", "info", "Edge updated successfully.", edge_id=str(edge.id))
                return EdgeResponseSchema.from_orm(edge)
            else:
                self.logger.log("EdgeController", "error", "Failed to update edge.")
                return None
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "error",
                f"Exception in update_edge: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    async def delete_edge(self, edge_id: UUID, user_id: UUID) -> bool:
        """
        Delete an edge.

        Args:
            edge_id (UUID): The ID of the edge to delete.
            user_id (UUID): The ID of the user performing the action.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            success = await self.edge_service.delete_edge(self.prisma, edge_id)
            if success:
                # Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": "DELETE",
                    "entity_type": "edge",
                    "entity_id": str(edge_id),
                    "details": {"deletion_action": True}
                }
                await self.audit_service.create_audit_log(self.prisma, audit_data)
                self.logger.log("EdgeController", "info", "Edge deleted successfully.", edge_id=str(edge_id))
                return True
            else:
                self.logger.log("EdgeController", "warning", "Failed to delete edge.", edge_id=str(edge_id))
                return False
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "error",
                f"Exception in delete_edge: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return False

    async def main(self):
        """
        Main function to test EdgeController functionalities.
        Demonstrates creating, retrieving, listing, updating, and deleting edges.
        """
        try:
            # Connect to the database
            await self.prisma.connect()
            print("Connected to the database.")

            # Test Data
            user_id = UUID("123e4567-e89b-12d3-a456-426614174000")  # Example UUID

            # Step 1: Create a new edge
            print("\nCreating a new edge...")
            edge_create = EdgeCreateSchema(
                name="Test Edge",
                description="This is a test edge."
                # Add other required fields based on existing schema
            )
            created_edge = await self.create_edge(edge_create, user_id)
            if created_edge:
                print(f"Created Edge: {created_edge.id} - Name: {created_edge.name}")
            else:
                print("Failed to create Edge.")

            # Step 2: Retrieve the edge by ID
            if created_edge:
                print(f"\nRetrieving Edge with ID: {created_edge.id}")
                retrieved_edge = await self.get_edge(created_edge.id)
                if retrieved_edge:
                    print(f"Retrieved Edge: {retrieved_edge.id} - Name: {retrieved_edge.name}")
                else:
                    print("Failed to retrieve Edge.")
            else:
                print("Skipping retrieval since Edge creation failed.")

            # Step 3: List all edges
            print("\nListing all edges...")
            edges = await self.list_edges()
            print(f"Total Edges: {len(edges)}")
            for edge in edges:
                print(f"- ID: {edge.id}, Name: {edge.name}, Description: {edge.description}")

            # Step 4: Update the edge's description
            if created_edge:
                print(f"\nUpdating Edge with ID: {created_edge.id}")
                edge_update = EdgeUpdateSchema(
                    description="Updated description for the test edge."
                    # Add other fields if necessary
                )
                updated_edge = await self.update_edge(created_edge.id, edge_update, user_id)
                if updated_edge:
                    print(f"Updated Edge: {updated_edge.id} - Description: {updated_edge.description}")
                else:
                    print("Failed to update Edge.")
            else:
                print("Skipping update since Edge creation failed.")

            # Step 5: Delete the edge
            if created_edge:
                print(f"\nDeleting Edge with ID: {created_edge.id}")
                deletion_success = await self.delete_edge(created_edge.id, user_id)
                print(f"Edge deleted: {deletion_success}")
            else:
                print("Skipping deletion since Edge creation failed.")

            # Step 6: List edges after deletion
            print("\nListing edges after deletion...")
            edges_after_deletion = await self.list_edges()
            print(f"Total Edges: {len(edges_after_deletion)}")
            for edge in edges_after_deletion:
                print(f"- ID: {edge.id}, Name: {edge.name}, Description: {edge.description}")

        except Exception as e:
            self.logger.log("EdgeController", "error", "An error occurred in main.", error=str(e))
            print(f"An error occurred: {e}")
        finally:
            print("\nDisconnecting from the database...")
            await self.prisma.disconnect()
            print("Database disconnected.")


# -------------------
# Testing Utility
# -------------------

async def run_edge_controller_tests():
    """
    Function to run EdgeController tests.
    """
    prisma = Prisma()
    await prisma.connect()
    edge_controller = EdgeController(prisma)
    await edge_controller.main()


if __name__ == "__main__":
    asyncio.run(run_edge_controller_tests())