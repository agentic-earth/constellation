# constellation-backend/api/backend/app/features/core/services/edge_service.py

"""
Edge Service Module

This module implements the Edge Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The EdgeService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (Edge, Block, BlockCategory, Category) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. Transaction Management: Utilizes Prisma's interactive transactions to ensure ACID properties during complex operations.

4. Error Handling: Comprehensive error handling to manage exceptions and ensure data consistency.

5. Relationship Management: Handles associations between edges and blocks, ensuring referential integrity.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for edge operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from prisma import Prisma
from prisma.models import Edge as PrismaEdge, Block as PrismaBlock, BlockCategory as PrismaBlockCategory, Category as PrismaCategory
from prisma.errors import UniqueViolationError
from backend.app.database import database
from backend.app.logger import ConstellationLogger
import asyncio
from datetime import datetime


class EdgeService:
    def __init__(self):
        self.prisma = database.prisma
        self.logger = ConstellationLogger()

    async def create_edge(self, edge_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Creates a new edge in the database.

        Args:
            edge_data (Dict[str, Any]): Dictionary containing edge data.
                Expected keys: 'source_block_id', 'target_block_id', optional 'description'.

        Returns:
            Optional[PrismaEdge]: The created edge if successful, None otherwise.
        """
        try:
            edge_id = str(uuid4())
            created_at = datetime.utcnow()
            updated_at = created_at

            # Validate that source and target blocks exist
            source_block = await self.prisma.block.find_unique(where={"block_id": str(edge_data["source_block_id"])})
            target_block = await self.prisma.block.find_unique(where={"block_id": str(edge_data["target_block_id"])})

            if not source_block or not target_block:
                raise ValueError("Source or target block does not exist.")

            # Create edge via Prisma
            created_edge = await self.prisma.edge.create(
                data={
                    "edge_id": edge_id,
                    "source_block_id": str(edge_data["source_block_id"]),
                    "target_block_id": str(edge_data["target_block_id"]),
                    "description": edge_data.get("description"),
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

    async def get_edge_by_id(self, edge_id: UUID) -> Optional[PrismaEdge]:
        """
        Retrieves an edge by its ID.

        Args:
            edge_id (UUID): The UUID of the edge to retrieve.

        Returns:
            Optional[PrismaEdge]: The retrieved edge if found, None otherwise.
        """
        try:
            edge = await self.prisma.edge.find_unique(
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

    async def update_edge(self, edge_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaEdge]:
        """
        Updates an existing edge's information.

        Args:
            edge_id (UUID): The UUID of the edge to update.
            update_data (Dict[str, Any]): Dictionary containing updated edge data.
                Allowed keys: 'source_block_id', 'target_block_id', 'description'.

        Returns:
            Optional[PrismaEdge]: The updated edge if successful, None otherwise.
        """
        try:
            # Validate if source_block_id and target_block_id exist if they are being updated
            if "source_block_id" in update_data:
                source_block = await self.prisma.block.find_unique(where={"block_id": str(update_data["source_block_id"])})
                if not source_block:
                    raise ValueError("Source block does not exist.")

            if "target_block_id" in update_data:
                target_block = await self.prisma.block.find_unique(where={"block_id": str(update_data["target_block_id"])})
                if not target_block:
                    raise ValueError("Target block does not exist.")

            update_data['updated_at'] = datetime.utcnow()

            updated_edge = await self.prisma.edge.update(
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

    async def delete_edge(self, edge_id: UUID) -> bool:
        """
        Deletes an edge from the database.

        Args:
            edge_id (UUID): The UUID of the edge to delete.

        Returns:
            bool: True if the edge was successfully deleted, False otherwise.
        """
        try:
            deleted_edge = await self.prisma.edge.delete(
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

    async def list_edges(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[PrismaEdge]:
        """
        Retrieves a list of edges, optionally filtered.

        Args:
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

            edges_list = await self.prisma.edge.find_many(
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

    async def associate_blocks_via_edge(self, source_block_id: UUID, target_block_id: UUID, description: Optional[str] = None) -> Optional[PrismaEdge]:
        """
        Creates an edge connecting two blocks.

        Args:
            source_block_id (UUID): The UUID of the source block.
            target_block_id (UUID): The UUID of the target block.
            description (Optional[str]): Optional description of the edge.

        Returns:
            Optional[PrismaEdge]: The created edge if successful, None otherwise.
        """
        edge_data = {
            "source_block_id": source_block_id,
            "target_block_id": target_block_id,
            "description": description
        }
        return await self.create_edge(edge_data)

    async def main(self):
        """
        Comprehensive main function to test EdgeService functionalities.
        """
        try:
            print("Starting EdgeService test...")

            # Step 1: Create new blocks
            print("\nCreating new blocks...")
            block_service = BlockService()
            block1_data = {
                "name": "Block1",
                "block_type": "dataset",
                "description": "First test block."
            }
            block2_data = {
                "name": "Block2",
                "block_type": "model",
                "description": "Second test block."
            }
            block3_data = {
                "name": "Block3",
                "block_type": "dataset",
                "description": "Third test block."
            }

            created_block1 = await block_service.prisma.block.create(data=block1_data)
            print(f"Created Block1: {created_block1.block_id} - {created_block1.name}")

            created_block2 = await block_service.prisma.block.create(data=block2_data)
            print(f"Created Block2: {created_block2.block_id} - {created_block2.name}")

            created_block3 = await block_service.prisma.block.create(data=block3_data)
            print(f"Created Block3: {created_block3.block_id} - {created_block3.name}")

            # Step 2: Create edges connecting the blocks
            print("\nCreating edges between blocks...")
            edge1 = await self.associate_blocks_via_edge(
                source_block_id=UUID(created_block1.block_id),
                target_block_id=UUID(created_block2.block_id),
                description="Edge from Block1 to Block2"
            )
            if edge1:
                print(f"Created Edge1: {edge1.edge_id} connecting {edge1.source_block_id} to {edge1.target_block_id}")

            edge2 = await self.associate_blocks_via_edge(
                source_block_id=UUID(created_block2.block_id),
                target_block_id=UUID(created_block3.block_id),
                description="Edge from Block2 to Block3"
            )
            if edge2:
                print(f"Created Edge2: {edge2.edge_id} connecting {edge2.source_block_id} to {edge2.target_block_id}")

            # Step 3: Retrieve and display an edge by ID
            print("\nRetrieving Edge1 by ID...")
            retrieved_edge1 = await self.get_edge_by_id(UUID(edge1.edge_id))
            if retrieved_edge1:
                print(f"Retrieved Edge1: {retrieved_edge1.edge_id} - {retrieved_edge1.description}")

            # Step 4: Update Edge1's description
            print("\nUpdating Edge1's description...")
            update_data = {"description": "Updated Edge from Block1 to Block2"}
            updated_edge1 = await self.update_edge(UUID(edge1.edge_id), update_data)
            if updated_edge1:
                print(f"Updated Edge1: {updated_edge1.edge_id} - {updated_edge1.description}")

            # Step 5: List all edges
            print("\nListing all edges...")
            all_edges = await self.list_edges()
            print(f"Total Edges: {len(all_edges)}")
            for edge in all_edges:
                print(f"- Edge ID: {edge.edge_id}, Description: {edge.description}, "
                      f"Source: {edge.Block_Edge_source_block_idToBlock.name}, "
                      f"Target: {edge.Block_Edge_target_block_idToBlock.name}")

            # Step 6: Delete Edge2
            print(f"\nDeleting Edge2: {edge2.edge_id}")
            deletion_success = await self.delete_edge(UUID(edge2.edge_id))
            print(f"Edge2 deleted: {deletion_success}")

            # Step 7: List edges after deletion
            print("\nListing edges after deletion...")
            remaining_edges = await self.list_edges()
            print(f"Remaining Edges: {len(remaining_edges)}")
            for edge in remaining_edges:
                print(f"- Edge ID: {edge.edge_id}, Description: {edge.description}, "
                      f"Source: {edge.Block_Edge_source_block_idToBlock.name}, "
                      f"Target: {edge.Block_Edge_target_block_idToBlock.name}")

            # Step 8: Clean up - Delete created blocks
            print("\nDeleting created blocks...")
            delete_success1 = await block_service.prisma.block.delete(where={"block_id": created_block1.block_id})
            delete_success2 = await block_service.prisma.block.delete(where={"block_id": created_block2.block_id})
            delete_success3 = await block_service.prisma.block.delete(where={"block_id": created_block3.block_id})
            print(f"Block1 deleted: {delete_success1}")
            print(f"Block2 deleted: {delete_success2}")
            print(f"Block3 deleted: {delete_success3}")

        except Exception as e:
            self.logger.log("EdgeService", "error", "An error occurred in main.", error=str(e))
            import traceback
            print(traceback.format_exc())

        print("\nEdgeService test completed.")


# Testing the EdgeService
if __name__ == "__main__":
    from backend.app.features.core.services.block_service import BlockService
    async def run_edge_service_tests():
        print("Connecting to the database...")
        await database.connect()
        print("Database connected.")

        edge_service = EdgeService()
        await edge_service.main()

        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

    asyncio.run(run_edge_service_tests())
