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
from typing import List, Optional, Dict, Any
from uuid import UUID

from prisma import Prisma

from backend.app.logger import ConstellationLogger
from backend.app.features.core.services.audit_service import AuditService
from backend.app.features.core.services.edge_service import EdgeService


class EdgeController:
    def __init__(self, prisma_client: Prisma):
        self.prisma = prisma_client
        self.logger = ConstellationLogger()
        self.edge_service = EdgeService()
        self.audit_service = AuditService()

    async def create_edge(self, edge_data: Dict[str, Any], user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Create a new edge.

        Args:
            edge_data (Dict[str, Any]): The data required to create an edge.
            user_id (UUID): The ID of the user performing the action.

        Returns:
            Optional[Dict[str, Any]]: The created edge if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                edge = await self.edge_service.create_edge(tx, edge_data)

                if not edge:
                    raise ValueError("Failed to create edge.")

                # Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": "CREATE",
                    "entity_type": "edge",
                    "entity_id": str(edge.edge_id),
                    "details": {"edge_data": edge_data}
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_data)
                if not audit_log:
                    raise Exception("Failed to create audit log")
                
                self.logger.log("EdgeController", "info", "Edge created successfully.", edge_id=str(edge.edge_id))
                return edge.dict()
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "error",
                f"Exception in create_edge: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return None

    async def get_edge(self, edge_id: UUID, user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve an edge by its ID.

        Args:
            edge_id (UUID): The ID of the edge to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The edge if found, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                edge = await self.edge_service.get_edge_by_id(tx, edge_id)
                if edge:
                    # Audit Logging
                    audit_data = {
                        "user_id": str(user_id),
                        "action_type": "READ",
                        "entity_type": "edge",
                        "entity_id": str(edge.edge_id),
                        "details": {"read_action": True}
                    }
                    audit_log = await self.audit_service.create_audit_log(tx, audit_data)
                    if not audit_log:
                        raise Exception("Failed to create audit log")
                    
                    self.logger.log("EdgeController", "info", "Edge retrieved successfully.", edge_id=str(edge.edge_id))
                    return edge.dict()
                else:
                    self.logger.log("EdgeController", "info", "Edge not found.", edge_id=str(edge_id))
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
        user_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List edges with optional filtering, pagination.

        Args:
            filters (Optional[Dict[str, Any]]): Filters to apply.
            limit (int): Maximum number of edges to retrieve.
            offset (int): Number of edges to skip.

        Returns:
            List[Dict[str, Any]]: A list of edges.
        """
        try:
            async with self.prisma.tx() as tx:
                edges = await self.edge_service.list_edges(tx, filters, limit, offset)
                if edges:
                    # Audit Logging
                    audit_data = {
                        "user_id": str(user_id),  # Assuming system access; adjust as needed
                        "action_type": "READ",
                        "entity_type": "edge",
                        "entity_id": str(edges[0].edge_id), # TODO: temporarily use first edge id
                        "details": {"filters": filters, "limit": limit, "offset": offset}
                    }
                    audit_log = await self.audit_service.create_audit_log(tx, audit_data)
                    if not audit_log:
                        raise Exception("Failed to create audit log")

                    self.logger.log("EdgeController", "info", f"Listed {len(edges)} edges.")
                    return [edge.dict() for edge in edges]
                else:
                    self.logger.log("EdgeController", "info", "No edges found.", filters=filters, limit=limit, offset=offset)
                    return []
        except Exception as e:
            self.logger.log(
                "EdgeController",
                "error",
                f"Exception in list_edges: {str(e)}",
                extra={"traceback": traceback.format_exc()}
            )
            return []

    async def update_edge(self, edge_id: UUID, update_data: Dict[str, Any], user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Update an existing edge.

        Args:
            edge_id (UUID): The ID of the edge to update.
            update_data (Dict[str, Any]): The data to update.
                Supported fields:
                - "source_block_id" (UUID): The ID of the source block.
                - "target_block_id" (UUID): The ID of the target block.
            user_id (UUID): The ID of the user performing the action.

        Returns:
            Optional[Dict[str, Any]]: The updated edge if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                edge = await self.edge_service.update_edge(tx, edge_id, update_data.copy())
                if not edge:
                    raise ValueError("Failed to update edge.")
                
                # Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": "UPDATE",
                    "entity_type": "edge",
                    "entity_id": str(edge.edge_id),
                    "details": {"update_data": update_data}
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_data)
                if not audit_log:
                    raise Exception("Failed to create audit log")
                
                self.logger.log("EdgeController", "info", "Edge updated successfully.", edge_id=str(edge.edge_id))
                return edge.dict()

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
            async with self.prisma.tx() as tx:
                success = await self.edge_service.delete_edge(tx, edge_id)
                if not success:
                    raise ValueError("Failed to delete edge.")
                
                # Audit Logging
                audit_data = {
                    "user_id": str(user_id),
                    "action_type": "DELETE",
                    "entity_type": "edge",
                    "entity_id": str(edge_id),
                    "details": {"deletion_action": True}
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_data)
                if not audit_log:
                    raise Exception("Failed to create audit log")
                
                self.logger.log("EdgeController", "info", "Edge deleted successfully.", edge_id=str(edge_id))
                return True

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
            # Test Data
            user_id = UUID("123e4567-e89b-12d3-a456-426614174000")  # Example UUID

            # Step 0: Create three blocks to create an edge
            block_controller = BlockController(self.prisma)
            print("\nCreating three blocks...")
            block_data1 = {
                "name": "Test Block1",
                "block_type": "model",
                "description": "This is a test block1."
            }
            block_data2 = {
                "name": "Test Block2",
                "block_type": "model",
                "description": "This is a test block2."
            }
            block_data3 = {
                "name": "Test Block3",
                "block_type": "model",
                "description": "This is a test block3."
            }
            created_block1 = await block_controller.create_block(block_data1, user_id)
            created_block2 = await block_controller.create_block(block_data2, user_id)
            created_block3 = await block_controller.create_block(block_data3, user_id)
            if created_block1 and created_block2 and created_block3:
                print(f"Created Blocks: {created_block1["block_id"]}")
                print(f"Created Blocks: {created_block2["block_id"]}")
                print(f"Created Blocks: {created_block3["block_id"]}")
            else:
                print("Failed to create Blocks.")

            # Step 1: Create a new edge
            print("\nCreating a new edge...")
            edge_create = {
                "source_block_id": created_block1["block_id"],
                "target_block_id": created_block2["block_id"],
            }
            created_edge = await self.create_edge(edge_create, user_id)
            if created_edge:
                print(f"Created Edge: {created_edge["edge_id"]} - {created_edge["source_block_id"]} -> {created_edge["target_block_id"]}")
            else:
                print("Failed to create Edge.")

            # Step 2: Retrieve the edge by ID
            if created_edge:
                print(f"\nRetrieving Edge with ID: {created_edge["edge_id"]}")
                retrieved_edge = await self.get_edge(created_edge["edge_id"], user_id)
                if retrieved_edge:
                    print(f"Retrieved Edge: {retrieved_edge["edge_id"]} - {retrieved_edge["source_block_id"]} -> {retrieved_edge["target_block_id"]}")
                else:
                    print("Failed to retrieve Edge.")
            else:
                print("Skipping retrieval since Edge creation failed.")

            # Step 3: List all edges
            print("\nListing all edges...")
            edges = await self.list_edges(user_id)
            print(f"Total Edges: {len(edges)}")
            for edge in edges:
                print(f"- ID: {edge["edge_id"]} - {edge["source_block_id"]} -> {edge["target_block_id"]}")

            # Step 4: Update the edge's description
            if created_edge:
                print(f"\nUpdating Edge with ID: {created_edge["edge_id"]}")
                edge_update = {
                    "source_block_id": created_block3["block_id"],
                    "target_block_id": created_block1["block_id"],
                }
                updated_edge = await self.update_edge(created_edge["edge_id"], edge_update, user_id)
                if updated_edge:
                    print(f"Updated Edge: {updated_edge["edge_id"]} - {updated_edge["source_block_id"]} -> {updated_edge["target_block_id"]}")
                else:
                    print("Failed to update Edge.")
            else:
                print("Skipping update since Edge creation failed.")

            # Step 5: Delete the edge
            if created_edge:
                print(f"\nDeleting Edge with ID: {created_edge["edge_id"]}")
                deletion_success = await self.delete_edge(created_edge["edge_id"], user_id)
                print(f"Edge deleted: {deletion_success}")
            else:
                print("Skipping deletion since Edge creation failed.")

            # Step 6: List edges after deletion
            print("\nListing edges after deletion...")
            edges_after_deletion = await self.list_edges(user_id)
            print(f"Total Edges: {len(edges_after_deletion)}")
            for edge in edges_after_deletion:
                print(f"- ID: {edge["edge_id"]} - {edge["source_block_id"]} -> {edge["target_block_id"]}")

            # Step 7: Delete the blocks
            print("\nDeleting the blocks...")
            deletion_success1 = await block_controller.delete_block(created_block1["block_id"], user_id)
            deletion_success2 = await block_controller.delete_block(created_block2["block_id"], user_id)
            deletion_success3 = await block_controller.delete_block(created_block3["block_id"], user_id)
            print(f"Blocks deleted: {deletion_success1}, {deletion_success2}, {deletion_success3}")

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
    print("Connecting to the database...")
    await prisma.connect()
    print("Database connected.")

    edge_controller = EdgeController(prisma)
    await edge_controller.main()


if __name__ == "__main__":
    from backend.app.features.core.controllers.block_controller import BlockController
    asyncio.run(run_edge_controller_tests())