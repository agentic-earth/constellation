# constellation-backend/api/backend/app/features/core/services/edge_service.py

"""
Edge Service Module

This module implements the Edge Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The EdgeService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected as an argument into each method.

Key Design Decisions:
1. Pass Prisma Client: Each method receives the Prisma client as an argument, promoting better testability and decoupling.
2. Use Timezone-Aware Datetimes: Replaced `utcnow` with `datetime.now(timezone.utc)` to handle timezone-aware objects.
3. Main Function for Testing: Added a main function to demonstrate and test the EdgeService functionalities.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from prisma import Prisma
from prisma.models import Edge as PrismaEdge, Block as PrismaBlock
from prisma.errors import UniqueViolationError
from backend.app.logger import ConstellationLogger
import asyncio
from datetime import datetime, timezone


class EdgeService:
    def __init__(self):
        self.logger = ConstellationLogger()

    async def create_edge(self, prisma: Prisma, edge_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Creates a new edge in the database.

        Args:
            prisma (Prisma): The Prisma client instance.
            edge_data (Dict[str, Any]): Dictionary containing edge data.
                Expected keys: 'source_block_id', 'target_block_id'.

        Returns:
            Optional[PrismaEdge]: The created edge if successful, None otherwise.
        """
        try:
            edge_id = str(uuid4())
            created_at = datetime.now(timezone.utc)
            updated_at = created_at

            # Validate that source and target blocks exist
            source_block = await prisma.block.find_unique(where={"block_id": str(edge_data["source_block_id"])})
            target_block = await prisma.block.find_unique(where={"block_id": str(edge_data["target_block_id"])})

            if not source_block or not target_block:
                raise ValueError("Source or target block does not exist.")

            # Create edge via Prisma
            created_edge = await prisma.edge.create(
                data={
                    "edge_id": edge_id,
                    "source_block_id": str(edge_data["source_block_id"]),
                    "target_block_id": str(edge_data["target_block_id"]),
                    "created_at": created_at,
                    "updated_at": updated_at
                }
            )

            self.logger.log(
                "EdgeService",
                "info",
                "Edge created successfully.",
                edge_id=created_edge.edge_id,
                source_block_id=created_edge.source_block_id,
                target_block_id=created_edge.target_block_id
            )

            return created_edge
        except Exception as e:
            self.logger.log("EdgeService", "error", "Failed to create edge.", error=str(e))
            return None

    async def get_edge_by_id(self, prisma: Prisma, edge_id: UUID) -> Optional[PrismaEdge]:
        """
        Retrieves an edge by its ID.

        Args:
            prisma (Prisma): The Prisma client instance.
            edge_id (UUID): The UUID of the edge to retrieve.

        Returns:
            Optional[PrismaEdge]: The retrieved edge if found, None otherwise.
        """
        try:
            edge = await prisma.edge.find_unique(
                where={"edge_id": str(edge_id)},
                include={
                    "Block_Edge_source_block_idToBlock": True,
                    "Block_Edge_target_block_idToBlock": True
                }
            )

            if edge:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge retrieved successfully.",
                    edge_id=edge.edge_id
                )
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Edge not found.",
                    edge_id=str(edge_id)
                )

            return edge
        except Exception as e:
            self.logger.log("EdgeService", "error", "Failed to retrieve edge by ID.", error=str(e))
            return None

    async def update_edge(self, prisma: Prisma, edge_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Updates an existing edge's information.

        Args:
            prisma (Prisma): The Prisma client instance.
            edge_id (UUID): The UUID of the edge to update.
            update_data (Dict[str, Any]): Dictionary containing updated edge data.
                Allowed keys: 'source_block_id', 'target_block_id'.

        Returns:
            Optional[PrismaEdge]: The updated edge if successful, None otherwise.
        """
        try:
            # Validate if source_block_id and target_block_id exist if they are being updated
            if "source_block_id" in update_data:
                source_block = await prisma.block.find_unique(where={"block_id": str(update_data["source_block_id"])})
                if not source_block:
                    raise ValueError("Source block does not exist.")

            if "target_block_id" in update_data:
                target_block = await prisma.block.find_unique(where={"block_id": str(update_data["target_block_id"])})
                if not target_block:
                    raise ValueError("Target block does not exist.")

            update_data['updated_at'] = datetime.now(timezone.utc)

            updated_edge = await prisma.edge.update(
                where={"edge_id": str(edge_id)},
                data=update_data
            )

            self.logger.log(
                "EdgeService",
                "info",
                "Edge updated successfully.",
                edge_id=updated_edge.edge_id,
                updated_fields=list(update_data.keys())
            )

            return updated_edge
        except Exception as e:
            self.logger.log("EdgeService", "error", "Failed to update edge.", error=str(e))
            return None

    async def delete_edge(self, prisma: Prisma, edge_id: UUID) -> bool:
        """
        Deletes an edge from the database.

        Args:
            prisma (Prisma): The Prisma client instance.
            edge_id (UUID): The UUID of the edge to delete.

        Returns:
            bool: True if the edge was successfully deleted, False otherwise.
        """
        try:
            deleted_edge = await prisma.edge.delete(
                where={"edge_id": str(edge_id)}
            )

            if deleted_edge:
                self.logger.log(
                    "EdgeService",
                    "info",
                    "Edge deleted successfully.",
                    edge_id=str(edge_id)
                )
                return True
            else:
                self.logger.log(
                    "EdgeService",
                    "warning",
                    "Edge not found for deletion.",
                    edge_id=str(edge_id)
                )
                return False
        except Exception as e:
            self.logger.log("EdgeService", "error", "Failed to delete edge.", error=str(e))
            return False

    async def list_edges(self, prisma: Prisma, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[PrismaEdge]:
        """
        Retrieves a list of edges, optionally filtered.

        Args:
            prisma (Prisma): The Prisma client instance.
            filters (Optional[Dict[str, Any]]): Optional filters to apply to the query.
                Supported filters:
                    - 'source_block_id': UUID
                    - 'target_block_id': UUID
                    - 'name_contains': string
            limit (int): The maximum number of edges to retrieve.
            offset (int): The number of edges to skip before starting to collect the result set.

        Returns:
            List[PrismaEdge]: A list of edges matching the filters.
        """
        try:
            prisma_filters = {}

            if filters:
                if "source_block_id" in filters:
                    prisma_filters["source_block_id"] = str(filters["source_block_id"])
                if "target_block_id" in filters:
                    prisma_filters["target_block_id"] = str(filters["target_block_id"])
                if "name_contains" in filters:
                    prisma_filters["name"] = {"contains": filters["name_contains"], "mode": "insensitive"}

            edges_list = await prisma.edge.find_many(
                where=prisma_filters,
                include={
                    "Block_Edge_source_block_idToBlock": True,
                    "Block_Edge_target_block_idToBlock": True
                },
                take=limit,
                skip=offset
            )

            self.logger.log(
                "EdgeService",
                "info",
                f"Retrieved {len(edges_list)} edges.",
                filters=filters,
                limit=limit,
                offset=offset
            )

            return edges_list
        except Exception as e:
            self.logger.log("EdgeService", "error", "Failed to list edges.", error=str(e))
            return []

    async def associate_blocks_via_edge(self, prisma: Prisma, source_block_id: UUID, target_block_id: UUID) -> Optional[PrismaEdge]:
        """
        Creates an edge connecting two blocks.

        Args:
            prisma (Prisma): The Prisma client instance.
            source_block_id (UUID): The UUID of the source block.
            target_block_id (UUID): The UUID of the target block.

        Returns:
            Optional[PrismaEdge]: The created edge if successful, None otherwise.
        """
        edge_data = {
            "source_block_id": source_block_id,
            "target_block_id": target_block_id
        }
        return await self.create_edge(prisma, edge_data)

    async def main(self):
        """
        Comprehensive main function to test EdgeService functionalities.
        """
        try:
            # Initialize Prisma client
            prisma = Prisma()
            await prisma.connect()
            print("Connected to the database.")

            # Initialize EdgeService
            edge_service = EdgeService()

            # Step 1: Create new blocks
            print("\nCreating new blocks...")
            block1 = await prisma.block.create(
                data={
                    "name": "Block1",
                    "block_type": "dataset",
                    "description": "First test block."
                }
            )
            print(f"Created Block1: {block1.block_id} - {block1.name}")

            block2 = await prisma.block.create(
                data={
                    "name": "Block2",
                    "block_type": "model",
                    "description": "Second test block."
                }
            )
            print(f"Created Block2: {block2.block_id} - {block2.name}")

            block3 = await prisma.block.create(
                data={
                    "name": "Block3",
                    "block_type": "dataset",
                    "description": "Third test block."
                }
            )
            print(f"Created Block3: {block3.block_id} - {block3.name}")

            # Step 2: Create edges connecting the blocks
            print("\nCreating edges between blocks...")
            edge1 = await edge_service.associate_blocks_via_edge(
                prisma=prisma,
                source_block_id=UUID(block1.block_id),
                target_block_id=UUID(block2.block_id)
            )
            if edge1:
                print(f"Created Edge1: {edge1.edge_id} connecting {edge1.source_block_id} to {edge1.target_block_id}")
            else:
                print("Failed to create Edge1.")

            edge2 = await edge_service.associate_blocks_via_edge(
                prisma=prisma,
                source_block_id=UUID(block2.block_id),
                target_block_id=UUID(block3.block_id)
            )
            if edge2:
                print(f"Created Edge2: {edge2.edge_id} connecting {edge2.source_block_id} to {edge2.target_block_id}")
            else:
                print("Failed to create Edge2.")

            # Step 3: Retrieve and display an edge by ID
            print("\nRetrieving Edge1 by ID...")
            retrieved_edge1 = await edge_service.get_edge_by_id(prisma, UUID(edge1.edge_id))
            if retrieved_edge1:
                print(f"Retrieved Edge1: {retrieved_edge1.edge_id} - Source: {retrieved_edge1.source_block_id} - Target: {retrieved_edge1.target_block_id}")
            else:
                print("Failed to retrieve Edge1.")

            # Step 4: Update Edge1's target_block_id
            print("\nUpdating Edge1's target_block_id...")
            update_data = {"target_block_id": block3.block_id}  # Changing target from Block2 to Block3
            updated_edge1 = await edge_service.update_edge(prisma, UUID(edge1.edge_id), update_data)
            if updated_edge1:
                print(f"Updated Edge1: {updated_edge1.edge_id} - New Target: {updated_edge1.target_block_id}")
            else:
                print("Failed to update Edge1.")

            # Step 5: List all edges
            print("\nListing all edges...")
            all_edges = await edge_service.list_edges(prisma)
            print(f"Total Edges: {len(all_edges)}")
            for edge in all_edges:
                print(f"- Edge ID: {edge.edge_id}, Source: {edge.source_block_id}, Target: {edge.target_block_id}")

            # Step 6: Delete Edge2
            print(f"\nDeleting Edge2: {edge2.edge_id}")
            deletion_success = await edge_service.delete_edge(prisma, UUID(edge2.edge_id))
            print(f"Edge2 deleted: {deletion_success}")

            # Step 7: List edges after deletion
            print("\nListing edges after deletion...")
            remaining_edges = await edge_service.list_edges(prisma)
            print(f"Remaining Edges: {len(remaining_edges)}")
            for edge in remaining_edges:
                print(f"- Edge ID: {edge.edge_id}, Source: {edge.source_block_id}, Target: {edge.target_block_id}")

            # Step 8: Clean up - Delete created blocks
            print("\nDeleting created blocks...")
            delete_success1 = await prisma.block.delete(where={"block_id": block1.block_id})
            print(f"Block1 deleted: {'Success' if delete_success1 else 'Failure'}")
            delete_success2 = await prisma.block.delete(where={"block_id": block2.block_id})
            print(f"Block2 deleted: {'Success' if delete_success2 else 'Failure'}")
            delete_success3 = await prisma.block.delete(where={"block_id": block3.block_id})
            print(f"Block3 deleted: {'Success' if delete_success3 else 'Failure'}")

        except Exception as e:
            self.logger.log("EdgeService", "error", "An error occurred in main.", error=str(e))
            print(f"An error occurred: {e}")
        finally:
            print("\nDisconnecting from the database...")
            await prisma.disconnect()
            print("Database disconnected.")

# -------------------
# Testing Utility
# -------------------

async def run_edge_service_tests():
    """
    Function to run EdgeService tests.
    """
    edge_service = EdgeService()
    await edge_service.main()

if __name__ == "__main__":
    asyncio.run(run_edge_service_tests())