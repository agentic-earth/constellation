"""
Pipeline Service Module

This module implements the Pipeline Service using a Repository pattern with Prisma ORM.

Design Pattern:
- Repository Pattern: The PipelineService class acts as a repository, encapsulating the data access logic.
- Dependency Injection: The Prisma client is injected via the database singleton.

Key Design Decisions:
1. Use of Dictionaries: We use dictionaries for input data to provide flexibility in the API.
   This allows callers to provide only the necessary fields without needing to construct full objects.

2. Prisma Models: We use Prisma-generated models (pipelines, pipeline_blocks, pipeline_edges) for type hinting and as return types.
   This ensures type safety and consistency with the database schema.

3. No Request/Response Models: We directly use dictionaries for input and Prisma models for output.
   This simplifies the API and reduces redundancy, as Prisma models already provide necessary structure.

4. Error Handling: Removed from this version. Errors will propagate to the caller.

This approach balances flexibility, type safety, and simplicity, leveraging Prisma's capabilities
while providing a clean API for pipeline operations.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import asyncio

from prisma.models import Pipeline, PipelineBlock, PipelineEdge
from backend.app.database import database
from backend.app.logger import ConstellationLogger


class PipelineService:
    def __init__(self):
        self.prisma = database.prisma
        self.logger = ConstellationLogger()

    async def create_pipeline(self, pipeline_data: Dict[str, Any]) -> Pipeline:
        """
        Creates a new pipeline in the database.

        Args:
            pipeline_data (Dict[str, Any]): Dictionary containing pipeline data.

        Returns:
            pipelines: The created pipeline.
        """
        pipeline_data['pipeline_id'] = str(uuid4())
        pipeline_data['created_at'] = datetime.utcnow()
        pipeline_data['updated_at'] = datetime.utcnow()
        created_pipeline = await self.prisma.Pipeline.create(data=pipeline_data)
        self.logger.log(
            "PipelineService",
            "info",
            "Pipeline created successfully.",
            pipeline_id=created_pipeline.pipeline_id,
            pipeline_name=created_pipeline.name
        )
        return created_pipeline

    async def get_pipeline_by_id(self, pipeline_id: UUID) -> Optional[Pipeline]:
        """
        Retrieves a pipeline by its ID.

        Args:
            pipeline_id (UUID): The ID of the pipeline to retrieve.

        Returns:
            Optional[pipelines]: The retrieved pipeline, or None if not found.
        """
        pipeline = await self.prisma.Pipeline.find_unique(where={"pipeline_id": str(pipeline_id)})
        if pipeline:
            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline retrieved successfully.",
                pipeline_id=pipeline.pipeline_id,
                name=pipeline.name
            )
        else:
            self.logger.log(
                "PipelineService",
                "warning",
                "Pipeline not found.",
                pipeline_id=str(pipeline_id)
            )
        return pipeline

    async def update_pipeline(self, pipeline_id: UUID, update_data: Dict[str, Any]) -> Pipeline:
        """
        Updates an existing pipeline's information.

        Args:
            pipeline_id (UUID): The ID of the pipeline to update.
            update_data (Dict[str, Any]): Dictionary containing updated pipeline data.

        Returns:
            pipelines: The updated pipeline.
        """
        update_data['updated_at'] = datetime.utcnow()
        updated_pipeline = await self.prisma.Pipeline.update(
            where={"pipeline_id": str(pipeline_id)},
            data=update_data
        )
        self.logger.log(
            "PipelineService",
            "info",
            "Pipeline updated successfully.",
            pipeline_id=updated_pipeline.pipeline_id,
            updated_fields=list(update_data.keys())
        )
        return updated_pipeline

    async def delete_pipeline(self, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline from the database.

        Args:
            pipeline_id (UUID): The ID of the pipeline to delete.

        Returns:
            bool: True if the pipeline was successfully deleted, False otherwise.
        """
        deleted_pipeline = await self.prisma.pipelines.delete(where={"pipeline_id": str(pipeline_id)})
        if deleted_pipeline:
            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline deleted successfully.",
                pipeline_id=str(pipeline_id)
            )
            return True
        else:
            self.logger.log(
                "PipelineService",
                "warning",
                "Pipeline not found for deletion.",
                pipeline_id=str(pipeline_id)
            )
            return False

    async def list_pipelines(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[Pipeline]:
        """
        Retrieves a list of pipelines, optionally filtered.

        Args:
            filters (Optional[Dict[str, Any]]): Optional filters to apply to the query.
            limit (int): The maximum number of pipelines to retrieve.
            offset (int): The number of pipelines to skip before starting to collect the result set.

        Returns:
            List[pipelines]: A list of pipelines matching the filters.
        """
        pipelines_list = await self.prisma.Pipeline.find_many(
            where=filters or {},
            take=limit,
            skip=offset
        )
        self.logger.log(
            "PipelineService",
            "info",
            f"Retrieved {len(pipelines_list)} pipelines."
        )
        return pipelines_list

    async def assign_block_to_pipeline(self, pipeline_block_data: Dict[str, Any]) -> PipelineBlock:
        """
        Assigns a block to a pipeline.

        Args:
            pipeline_block_data (Dict[str, Any]): Dictionary containing pipeline block data.

        Returns:
            PipelineBlock: The created pipeline block association.
        """
        pipeline_block_data['pipeline_block_id'] = str(uuid4())
        pipeline_block_data['created_at'] = datetime.utcnow()
        pipeline_block_data['updated_at'] = datetime.utcnow()
        created_pipeline_block = await self.prisma.PipelineBlock.create(data=pipeline_block_data)
        self.logger.log(
            "PipelineService",
            "info",
            "Block assigned to pipeline successfully.",
            pipeline_block_id=created_pipeline_block.pipeline_block_id,
            pipeline_id=created_pipeline_block.pipeline_id,
            block_id=created_pipeline_block.block_id
        )
        return created_pipeline_block

    async def remove_block_from_pipeline(self, pipeline_block_id: UUID) -> bool:
        """
        Removes a block from a pipeline.

        Args:
            pipeline_block_id (UUID): The ID of the pipeline block association to remove.

        Returns:
            bool: True if the block was successfully removed, False otherwise.
        """
        deleted_pipeline_block = await self.prisma.PipelineBlock.delete(where={"pipeline_block_id": str(pipeline_block_id)})
        if deleted_pipeline_block:
            self.logger.log(
                "PipelineService",
                "info",
                "Block removed from pipeline successfully.",
                pipeline_block_id=str(pipeline_block_id)
            )
            return True
        else:
            self.logger.log(
                "PipelineService",
                "warning",
                "Pipeline block association not found for removal.",
                pipeline_block_id=str(pipeline_block_id)
            )
            return False

    async def assign_edge_to_pipeline(self, pipeline_edge_data: Dict[str, Any]) -> PipelineEdge:
        """
        Assigns an edge to a pipeline.

        Args:
            pipeline_edge_data (Dict[str, Any]): Dictionary containing pipeline edge data.

        Returns:
            PipelineEdge: The created pipeline edge association.
        """
        pipeline_edge_data['pipeline_edge_id'] = str(uuid4())
        pipeline_edge_data['created_at'] = datetime.utcnow()
        pipeline_edge_data['updated_at'] = datetime.utcnow()
        created_pipeline_edge = await self.prisma.PipelineEdge.create(data=pipeline_edge_data)
        self.logger.log(
            "PipelineService",
            "info",
            "Edge assigned to pipeline successfully.",
            pipeline_edge_id=created_pipeline_edge.pipeline_edge_id,
            pipeline_id=created_pipeline_edge.pipeline_id,
            edge_id=created_pipeline_edge.edge_id
        )
        return created_pipeline_edge

    async def remove_edge_from_pipeline(self, pipeline_edge_id: UUID) -> bool:
        """
        Removes an edge from a pipeline.

        Args:
            pipeline_edge_id (UUID): The ID of the pipeline edge association to remove.

        Returns:
            bool: True if the edge was successfully removed, False otherwise.
        """
        deleted_pipeline_edge = await self.prisma.PipelineEdge.delete(where={"pipeline_edge_id": str(pipeline_edge_id)})
        if deleted_pipeline_edge:
            self.logger.log(
                "PipelineService",
                "info",
                "Edge removed from pipeline successfully.",
                pipeline_edge_id=str(pipeline_edge_id)
            )
            return True
        else:
            self.logger.log(
                "PipelineService",
                "warning",
                "Pipeline edge association not found for removal.",
                pipeline_edge_id=str(pipeline_edge_id)
            )
            return False

    async def get_pipeline_blocks(self, pipeline_id: UUID) -> List[PipelineBlock]:
        """
        Retrieves all blocks associated with a pipeline.

        Args:
            pipeline_id (UUID): The ID of the pipeline.

        Returns:
            List[PipelineBlock]: A list of pipeline block associations.
        """
        pipeline_blocks_list = await self.prisma.PipelineBlock.find_many(
            where={"pipeline_id": str(pipeline_id)}
        )
        self.logger.log(
            "PipelineService",
            "info",
            f"Retrieved {len(pipeline_blocks_list)} blocks for pipeline {pipeline_id}."
        )
        return pipeline_blocks_list

    async def get_pipeline_edges(self, pipeline_id: UUID) -> List[PipelineEdge]:
        """
        Retrieves all edges associated with a pipeline.

        Args:
            pipeline_id (UUID): The ID of the pipeline.

        Returns:
            List[PipelineEdge]: A list of pipeline edge associations.
        """
        pipeline_edges_list = await self.prisma.PipelineEdge.find_many(
            where={"pipeline_id": str(pipeline_id)}
        )
        self.logger.log(
            "PipelineService",
            "info",
            f"Retrieved {len(pipeline_edges_list)} edges for pipeline {pipeline_id}."
        )
        return pipeline_edges_list

    # Add additional methods as needed...
async def main():
    from backend.app.features.core.services.block_service import BlockService
    from backend.app.features.core.services.edge_service import EdgeService
    from backend.app.features.core.services.user_service import UserService
    """
    Main function to demonstrate and test the PipelineService functionality.
    """
    print("Starting PipelineService test...")

    print("Connecting to the database...")
    await database.connect()
    print("Database connected successfully.")

    pipeline_service = PipelineService()
    user_service = UserService()  # Initialize UserService

    try:
        # Create a mock user
        print("\nCreating a mock user for pipeline creation...")
        mock_user_data = {
            "username": "pipeline_test_user",
            "email": "pipeline_test_user@example.com",
            "password_hash": "hashed_password",  # Replace with actual hashed password
            "role": "tester"  # Adjust role as necessary
        }
        
        ## if created_user is None then it already exists so we can use that user instead of creating a new one   
        created_user = await user_service.create_user(mock_user_data)
        if created_user is None:
            created_user = await user_service.get_user_by_email(mock_user_data["email"])
        print(f"Created user: {created_user}")

        # Ensure the user was created successfully
        if not created_user:
            print("Failed to create a mock user. Exiting test.")
            return

        # Create a new pipeline using the mock user's ID
        print("\nCreating a new pipeline...")
        new_pipeline_data = {
            "name": "Test Pipeline",
            "description": "This is a test pipeline.",
            "created_by": created_user.user_id  # Use the created user's ID
        }
        created_pipeline = await pipeline_service.create_pipeline(new_pipeline_data)
        print(f"Created pipeline: {created_pipeline}")

        # Get pipeline by ID
        print(f"\nRetrieving pipeline with ID: {created_pipeline.pipeline_id}")
        retrieved_pipeline = await pipeline_service.get_pipeline_by_id(UUID(created_pipeline.pipeline_id))
        print(f"Retrieved pipeline: {retrieved_pipeline}")

        # Update pipeline
        print(f"\nUpdating pipeline with ID: {created_pipeline.pipeline_id}")
        update_data = {"description": "Updated test pipeline description."}
        updated_pipeline = await pipeline_service.update_pipeline(UUID(created_pipeline.pipeline_id), update_data)
        print(f"Updated pipeline: {updated_pipeline}")

        # List pipelines
        print("\nListing all pipelines...")
        all_pipelines = await pipeline_service.list_pipelines()
        print(f"Total pipelines: {len(all_pipelines)}")
        for pipeline in all_pipelines:
            print(f"- Pipeline ID: {pipeline.pipeline_id}, Name: {pipeline.name}, Description: {pipeline.description}")

        # Assign a block to the pipeline
        print("\nAssigning a block to the pipeline...")
        # Ensure you have an existing block_id or create one using BlockService
        block_service = BlockService()
        new_block_data = {
            "name": "Mock Block for Pipeline",
            "block_type": "type_example",
            "description": "A block created for pipeline assignment",
            "created_by": created_user.user_id,
            "metadata": {"example_key": "example_value"},
            "taxonomy": {"example_category": "example_value"}
        }
        created_block = await block_service.create_block(new_block_data)
        print(f"Created block: {created_block}")

        new_pipeline_block_data = {
            "pipeline_id": created_pipeline.pipeline_id,
            "block_id": created_block.block_id,
        }
        created_pipeline_block = await pipeline_service.assign_block_to_pipeline(new_pipeline_block_data)
        print(f"Assigned block to pipeline: {created_pipeline_block}")

        # Assign an edge to the pipeline
        print("\nAssigning an edge to the pipeline...")
        # Ensure you have an existing edge_id or create one using EdgeService
        edge_service = EdgeService()
        new_edge_data = {
            "name": "Mock Edge for Pipeline",
            "edge_type": "primary",
            "description": "An edge created for pipeline assignment"
        }
        created_edge = await edge_service.create_edge(new_edge_data)
        print(f"Created edge: {created_edge}")

        new_pipeline_edge_data = {
            "pipeline_id": created_pipeline.pipeline_id,
            "edge_id": created_edge.edge_id,
            "source_block_id": created_block.block_id,  # Use the created block's ID as source
            "target_block_id": created_block.block_id   # Use the created block's ID as target (for testing)
        }
        created_pipeline_edge = await pipeline_service.assign_edge_to_pipeline(new_pipeline_edge_data)
        print(f"Assigned edge to pipeline: {created_pipeline_edge}")

        # Get pipeline blocks
        print(f"\nRetrieving blocks for pipeline ID: {created_pipeline.pipeline_id}")
        pipeline_blocks = await pipeline_service.get_pipeline_blocks(UUID(created_pipeline.pipeline_id))
        print(f"Pipeline blocks: {pipeline_blocks}")

        # Get pipeline edges
        print(f"\nRetrieving edges for pipeline ID: {created_pipeline.pipeline_id}")
        pipeline_edges = await pipeline_service.get_pipeline_edges(UUID(created_pipeline.pipeline_id))
        print(f"Pipeline edges: {pipeline_edges}")

        # Remove block from pipeline
        print(f"\nRemoving block with ID: {created_pipeline_block.pipeline_block_id} from pipeline.")
        removed_block = await pipeline_service.remove_block_from_pipeline(UUID(created_pipeline_block.pipeline_block_id))
        print(f"Block removed: {removed_block}")

        # Remove edge from pipeline
        print(f"\nRemoving edge with ID: {created_pipeline_edge.pipeline_edge_id} from pipeline.")
        removed_edge = await pipeline_service.remove_edge_from_pipeline(UUID(created_pipeline_edge.pipeline_edge_id))
        print(f"Edge removed: {removed_edge}")

        # Delete pipeline
        print(f"\nDeleting pipeline with ID: {created_pipeline.pipeline_id}")
        deleted = await pipeline_service.delete_pipeline(UUID(created_pipeline.pipeline_id))
        print(f"Pipeline deleted: {deleted}")

        # Optionally, delete the mock user and associated block and edge
        print(f"\nDeleting mock user with ID: {created_user.user_id}")
        deleted_user = await user_service.delete_user(UUID(created_user.user_id))
        print(f"Mock user deleted: {deleted_user}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        print(traceback.format_exc())

    finally:
        print("\nDisconnecting from the database...")
        await database.disconnect()
        print("Database disconnected.")

if __name__ == "__main__":
    asyncio.run(main())