from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from prisma import Prisma
from prisma.models import Pipeline as PrismaPipeline, PipelineBlock as PrismaPipelineBlock, PipelineEdge as PrismaPipelineEdge
from prisma.errors import UniqueViolationError
from backend.app.logger import ConstellationLogger
import asyncio
from datetime import datetime, timezone


class PipelineService:
    def __init__(self):
        self.logger = ConstellationLogger()

    async def create_pipeline(self, prisma: Prisma, pipeline_data: Dict[str, Any]) -> Optional[PrismaPipeline]:
        """
        Creates a new pipeline in the database.

        Args:
            prisma (Prisma): The Prisma client instance.
            pipeline_data (Dict[str, Any]): Dictionary containing pipeline creation data.
                Expected keys: 'name', 'description', 'user_id'.

        Returns:
            Optional[PrismaPipeline]: The created pipeline if successful, None otherwise.
        """
        try:
            pipeline_id = str(uuid4())
            created_at = datetime.now(timezone.utc)
            updated_at = created_at

            # Ensure user exists
            user = await prisma.profile.find_unique(where={"auth_uid": str(pipeline_data["user_id"])})
            if not user:
                raise ValueError("User does not exist.")

            # Create pipeline via Prisma
            pipeline = await prisma.pipeline.create(
                data={
                    "pipeline_id": pipeline_id,
                    "name": pipeline_data["name"],
                    "description": pipeline_data.get("description"),
                    "user_id": str(pipeline_data["user_id"]),
                    "created_at": created_at,
                    "updated_at": updated_at
                }
            )

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline created successfully.",
                pipeline_id=pipeline.pipeline_id,
                name=pipeline.name,
                user_id=pipeline.user_id
            )

            return pipeline
        except UniqueViolationError as e:
            self.logger.log("PipelineService", "error", "Unique violation when creating pipeline.", error=str(e))
            return None
        except Exception as e:
            self.logger.log("PipelineService", "error", "Error creating pipeline.", error=str(e))
            return None

    async def get_pipeline_by_id(self, prisma: Prisma, pipeline_id: UUID) -> Optional[PrismaPipeline]:
        """
        Retrieves a pipeline by its UUID.

        Args:
            prisma (Prisma): The Prisma client instance.
            pipeline_id (UUID): The UUID of the pipeline to retrieve.

        Returns:
            Optional[PrismaPipeline]: The pipeline if found, None otherwise.
        """
        try:
            pipeline = await prisma.pipeline.find_unique(
                where={"pipeline_id": str(pipeline_id)},
                include={
                    "PipelineBlock": {
                        "include": {
                            "Block": True
                        }
                    },
                    "PipelineEdge": {
                        "include": {
                            "Edge": True
                        }
                    }
                }
            )
            if pipeline:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline retrieved successfully.",
                    pipeline_id=pipeline.pipeline_id
                )
                return pipeline
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline not found.",
                    pipeline_id=str(pipeline_id)
                )
                return None
        except Exception as e:
            self.logger.log("PipelineService", "error", "Error retrieving pipeline.", error=str(e))
            return None

    async def update_pipeline(self, prisma: Prisma, pipeline_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaPipeline]:
        """
        Updates an existing pipeline's information.

        Args:
            prisma (Prisma): The Prisma client instance.
            pipeline_id (UUID): The UUID of the pipeline to update.
            update_data (Dict[str, Any]): Dictionary containing updated pipeline data.
                Allowed keys: 'name', 'description'.

        Returns:
            Optional[PrismaPipeline]: The updated pipeline if successful, None otherwise.
        """
        try:
            update_data['updated_at'] = datetime.now(timezone.utc)
            updated_pipeline = await prisma.pipeline.update(
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
        except Exception as e:
            self.logger.log("PipelineService", "error", "Error updating pipeline.", error=str(e))
            return None

    async def delete_pipeline(self, prisma: Prisma, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline by its UUID.

        Args:
            prisma (Prisma): The Prisma client instance.
            pipeline_id (UUID): The UUID of the pipeline to delete.

        Returns:
            bool: True if the pipeline was successfully deleted, False otherwise.
        """
        try:
            await prisma.pipeline.delete(where={"pipeline_id": str(pipeline_id)})
            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline deleted successfully.",
                pipeline_id=str(pipeline_id)
            )
            return True
        except Exception as e:
            self.logger.log("PipelineService", "error", "Error deleting pipeline.", error=str(e))
            return False

    async def assign_version_to_pipeline(self, prisma: Prisma, pipeline_id: UUID, version_id: UUID) -> bool:
        """
        Assigns a specific version to a pipeline.

        Args:
            prisma (Prisma): The Prisma client instance.
            pipeline_id (UUID): The UUID of the pipeline to update.
            version_id (UUID): The UUID of the version to assign.

        Returns:
            bool: True if the version was successfully assigned, False otherwise.
        """
        try:
            # Ensure the version exists
            version = await prisma.edge.find_unique(where={"edge_id": str(version_id)})
            if not version:
                raise ValueError("Version does not exist.")

            updated_pipeline = await prisma.pipeline.update(
                where={"pipeline_id": str(pipeline_id)},
                data={"current_version_id": str(version_id)}
            )
            self.logger.log(
                "PipelineService",
                "info",
                "Version assigned to pipeline successfully.",
                pipeline_id=str(pipeline_id),
                version_id=str(version_id)
            )
            return True
        except Exception as e:
            self.logger.log("PipelineService", "error", "Error assigning version to pipeline.", error=str(e))
            return False

    async def search_pipelines(self, prisma: Prisma, search_params: Dict[str, Any]) -> List[PrismaPipeline]:
        """
        Searches for pipelines based on given parameters.

        Args:
            prisma (Prisma): The Prisma client instance.
            search_params (Dict[str, Any]): Dictionary containing search parameters.
                Possible keys: 'name', 'user_id'.

        Returns:
            List[PrismaPipeline]: A list of pipelines matching the search criteria.
        """
        try:
            where_clause = {}
            if 'name' in search_params:
                where_clause['name'] = {"contains": search_params['name']}
            if 'user_id' in search_params:
                where_clause['user_id'] = str(search_params['user_id'])

            pipelines = await prisma.pipeline.find_many(
                where=where_clause,
                include={
                    "PipelineBlock": {
                        "include": {
                            "Block": True
                        }
                    },
                    "PipelineEdge": {
                        "include": {
                            "Edge": True
                        }
                    }
                }
            )
            self.logger.log(
                "PipelineService",
                "info",
                "Pipelines searched successfully.",
                search_params=search_params,
                pipelines_found=len(pipelines)
            )
            return pipelines
        except Exception as e:
            self.logger.log("PipelineService", "error", "Error searching pipelines.", error=str(e))
            return []

    async def list_pipelines(self, prisma: Prisma, limit: int = 100, offset: int = 0) -> List[PrismaPipeline]:
        """
        Lists all pipelines with pagination.

        Args:
            prisma (Prisma): The Prisma client instance.
            limit (int): The maximum number of pipelines to return.
            offset (int): The number of pipelines to skip.

        Returns:
            List[PrismaPipeline]: A list of pipelines.
        """
        try:
            pipelines = await prisma.pipeline.find_many(
                skip=offset,
                take=limit,
                include={
                    "PipelineBlock": {
                        "include": {
                            "Block": True
                        }
                    },
                    "PipelineEdge": {
                        "include": {
                            "Edge": True
                        }
                    }
                }
            )
            self.logger.log(
                "PipelineService",
                "info",
                "Pipelines listed successfully.",
                limit=limit,
                offset=offset,
                pipelines_found=len(pipelines)
            )
            return pipelines
        except Exception as e:
            self.logger.log("PipelineService", "error", "Error listing pipelines.", error=str(e))
            return []

    # ... (rest of the class, including the main method for testing)
    # -------------------
    # Main function for testing
    # -------------------
    
    async def main(self):
        """
        Main function to demonstrate and test the PipelineService functionalities.
        """
        prisma = Prisma()
        await prisma.connect()
        print("Connected to the database.")

        try:
            # Step 1: Create a new pipeline
            print("\nCreating a new pipeline...")
            pipeline_data = {
                "name": "Test Pipeline",
                "description": "This is a test pipeline.",
                "user_id": UUID("123e4567-e89b-12d3-a456-426614174000")  # Replace with actual user ID
            }
            created_pipeline = await self.create_pipeline(prisma, pipeline_data)
            if created_pipeline:
                print(f"Pipeline created: {created_pipeline.pipeline_id} - {created_pipeline.name}")
            else:
                print("Failed to create pipeline.")

            # Step 2: Retrieve the created pipeline
            if created_pipeline:
                print(f"\nRetrieving pipeline with ID: {created_pipeline.pipeline_id}")
                fetched_pipeline = await self.get_pipeline_by_id(prisma, UUID(created_pipeline.pipeline_id))
                if fetched_pipeline:
                    print(f"Fetched Pipeline: {fetched_pipeline.pipeline_id} - {fetched_pipeline.name}")
                else:
                    print("Pipeline not found.")

            # Step 3: Update the pipeline
            if created_pipeline:
                print(f"\nUpdating pipeline with ID: {created_pipeline.pipeline_id}")
                update_data = {
                    "name": "Updated Test Pipeline",
                    "description": "This pipeline has been updated."
                }
                updated_pipeline = await self.update_pipeline(prisma, UUID(created_pipeline.pipeline_id), update_data)
                if updated_pipeline:
                    print(f"Updated Pipeline: {updated_pipeline.pipeline_id} - {updated_pipeline.name}")
                else:
                    print("Failed to update pipeline.")

            # Step 4: Assign a version to the pipeline
            if created_pipeline:
                print(f"\nAssigning version to pipeline with ID: {created_pipeline.pipeline_id}")
                version_id = UUID("123e4567-e89b-12d3-a456-426614174001")  # Replace with actual version ID
                assign_success = await self.assign_version_to_pipeline(prisma, UUID(created_pipeline.pipeline_id), version_id)
                print(f"Version assigned: {assign_success}")

            # Step 5: Search for pipelines
            print("\nSearching for pipelines with name containing 'Updated'...")
            search_params = {
                "name": "Updated"
            }
            found_pipelines = await self.search_pipelines(prisma, search_params)
            print(f"Pipelines found: {len(found_pipelines)}")
            for p in found_pipelines:
                print(f"- {p.pipeline_id} - {p.name}")

            # Step 6: List all pipelines
            print("\nListing all pipelines...")
            all_pipelines = await self.list_pipelines(prisma, limit=10, offset=0)
            print(f"Total Pipelines: {len(all_pipelines)}")
            for p in all_pipelines:
                print(f"- {p.pipeline_id} - {p.name}")

            # Step 7: Delete the pipeline
            if created_pipeline:
                print(f"\nDeleting pipeline with ID: {created_pipeline.pipeline_id}")
                deletion_success = await self.delete_pipeline(prisma, UUID(created_pipeline.pipeline_id))
                print(f"Pipeline deleted: {deletion_success}")

        except Exception as e:
            self.logger.log("PipelineService", "error", "An error occurred in main.", error=str(e))
            print(f"An error occurred: {e}")
        finally:
            print("\nDisconnecting from the database...")
            await prisma.disconnect()
            print("Database disconnected.")

# -------------------
# Testing Utility
# -------------------

async def run_pipeline_service_tests():
    """
    Function to run PipelineService tests.
    """
    pipeline_service = PipelineService()
    await pipeline_service.main()

if __name__ == "__main__":
    asyncio.run(run_pipeline_service_tests())