# app/services/pipeline_service.py

"""
Pipeline Service Module

This module encapsulates all pipeline-related business logic and interactions with the Supabase backend.
It provides functions to create, retrieve, update, delete pipelines, and manage their associated blocks and edges,
ensuring that all operations are logged appropriately using the Constellation Logger.

Design Philosophy:
- Utilize Supabase's REST API for standard CRUD operations for performance and reliability.
- Use Python only for advanced logic that cannot be handled directly by Supabase.
- Ensure flexibility to adapt to schema changes with minimal modifications.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from app.models import (
    Pipeline,
    PipelineCreateSchema,
    PipelineUpdateSchema,
    PipelineResponseSchema,
    PipelineBlockCreateSchema,
    PipelineBlockResponseSchema,
    PipelineEdgeCreateSchema,
    PipelineEdgeResponseSchema
)
from app.logger import ConstellationLogger
from app.utils.helpers import SupabaseClientManager
from app.schemas import PipelineResponseSchema, PipelineBlockResponseSchema, PipelineEdgeResponseSchema
from datetime import datetime


class PipelineService:
    """
    PipelineService class encapsulates all pipeline-related operations.
    """

    def __init__(self):
        """
        Initializes the PipelineService with the Supabase client and logger.
        """
        self.supabase_manager = SupabaseClientManager()
        self.logger = ConstellationLogger()

    # -------------------
    # Pipeline Operations
    # -------------------

    def create_pipeline(self, pipeline_data: PipelineCreateSchema) -> Optional[PipelineResponseSchema]:
        """
        Creates a new pipeline in the Supabase database.

        Args:
            pipeline_data (PipelineCreateSchema): The data required to create a new pipeline.

        Returns:
            Optional[PipelineResponseSchema]: The created pipeline data if successful, None otherwise.
        """
        try:
            # Convert Pydantic schema to dictionary
            data = pipeline_data.dict()
            response = self.supabase_manager.client.table("pipelines").insert(data).execute()

            if response.status_code in [200, 201] and response.data:
                created_pipeline = PipelineResponseSchema(**response.data[0])
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline created successfully",
                    pipeline_id=created_pipeline.pipeline_id,
                    name=created_pipeline.name,
                    created_by=created_pipeline.created_by
                )
                return created_pipeline
            else:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to create pipeline",
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline creation: {e}"
            )
            return None

    def get_pipeline_by_id(self, pipeline_id: UUID) -> Optional[PipelineResponseSchema]:
        """
        Retrieves a pipeline by its unique identifier.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to retrieve.

        Returns:
            Optional[PipelineResponseSchema]: The pipeline data if found, None otherwise.
        """
        try:
            response = self.supabase_manager.client.table("pipelines").select("*").eq("pipeline_id", str(pipeline_id)).single().execute()

            if response.status_code == 200 and response.data:
                pipeline = PipelineResponseSchema(**response.data)
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline retrieved successfully",
                    pipeline_id=pipeline.pipeline_id,
                    name=pipeline.name
                )
                return pipeline
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline not found",
                    pipeline_id=pipeline_id,
                    status_code=response.status_code
                )
                return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline retrieval: {e}"
            )
            return None

    def update_pipeline(self, pipeline_id: UUID, update_data: PipelineUpdateSchema) -> Optional[PipelineResponseSchema]:
        """
        Updates an existing pipeline's information.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to update.
            update_data (PipelineUpdateSchema): The data to update for the pipeline.

        Returns:
            Optional[PipelineResponseSchema]: The updated pipeline data if successful, None otherwise.
        """
        try:
            data = update_data.dict(exclude_unset=True)
            response = self.supabase_manager.client.table("pipelines").update(data).eq("pipeline_id", str(pipeline_id)).execute()

            if response.status_code == 200 and response.data:
                updated_pipeline = PipelineResponseSchema(**response.data[0])
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline updated successfully",
                    pipeline_id=updated_pipeline.pipeline_id,
                    updated_fields=list(data.keys())
                )
                return updated_pipeline
            else:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to update pipeline",
                    pipeline_id=pipeline_id,
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline update: {e}"
            )
            return None

    def delete_pipeline(self, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline from the Supabase database.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_manager.client.table("pipelines").delete().eq("pipeline_id", str(pipeline_id)).execute()

            if response.status_code == 200 and response.count > 0:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline deleted successfully",
                    pipeline_id=pipeline_id
                )
                return True
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline not found or already deleted",
                    pipeline_id=pipeline_id,
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline deletion: {e}"
            )
            return False

    def list_pipelines(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[PipelineResponseSchema]]:
        """
        Retrieves a list of pipelines with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the pipelines.

        Returns:
            Optional[List[PipelineResponseSchema]]: A list of pipelines if successful, None otherwise.
        """
        try:
            query = self.supabase_manager.client.table("pipelines").select("*")
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            response = query.execute()

            if response.status_code == 200 and response.data:
                pipelines = [PipelineResponseSchema(**pipeline) for pipeline in response.data]
                self.logger.log(
                    "PipelineService",
                    "info",
                    f"{len(pipelines)} pipelines retrieved successfully",
                    filters=filters
                )
                return pipelines
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No pipelines found",
                    filters=filters,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during listing pipelines: {e}"
            )
            return None

    # -------------------
    # Pipeline Block Operations
    # -------------------

    def assign_block_to_pipeline(self, pipeline_block_data: PipelineBlockCreateSchema) -> Optional[PipelineBlockResponseSchema]:
        """
        Assigns a block to a pipeline by creating a pipeline_block entry.

        Args:
            pipeline_block_data (PipelineBlockCreateSchema): The data required to assign a block to a pipeline.

        Returns:
            Optional[PipelineBlockResponseSchema]: The created pipeline_block data if successful, None otherwise.
        """
        try:
            data = pipeline_block_data.dict()
            response = self.supabase_manager.client.table("pipeline_blocks").insert(data).execute()

            if response.status_code in [200, 201] and response.data:
                created_pipeline_block = PipelineBlockResponseSchema(**response.data[0])
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Block assigned to pipeline successfully",
                    pipeline_block_id=created_pipeline_block.pipeline_block_id,
                    pipeline_id=created_pipeline_block.pipeline_id,
                    block_id=created_pipeline_block.block_id
                )
                return created_pipeline_block
            else:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to assign block to pipeline",
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during assigning block to pipeline: {e}"
            )
            return None

    def get_pipeline_blocks(self, pipeline_id: UUID) -> Optional[List[PipelineBlockResponseSchema]]:
        """
        Retrieves all blocks assigned to a specific pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.

        Returns:
            Optional[List[PipelineBlockResponseSchema]]: A list of pipeline_block entries if successful, None otherwise.
        """
        try:
            response = self.supabase_manager.client.table("pipeline_blocks").select("*").eq("pipeline_id", str(pipeline_id)).execute()

            if response.status_code == 200 and response.data:
                pipeline_blocks = [PipelineBlockResponseSchema(**pb) for pb in response.data]
                self.logger.log(
                    "PipelineService",
                    "info",
                    f"{len(pipeline_blocks)} blocks retrieved for pipeline {pipeline_id}",
                    pipeline_id=pipeline_id
                )
                return pipeline_blocks
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No blocks found for the pipeline",
                    pipeline_id=pipeline_id,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during retrieving pipeline blocks: {e}"
            )
            return None

    def remove_block_from_pipeline(self, pipeline_block_id: UUID) -> bool:
        """
        Removes a block from a pipeline by deleting the pipeline_block entry.

        Args:
            pipeline_block_id (UUID): The UUID of the pipeline_block entry to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_manager.client.table("pipeline_blocks").delete().eq("pipeline_block_id", str(pipeline_block_id)).execute()

            if response.status_code == 200 and response.count > 0:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Block removed from pipeline successfully",
                    pipeline_block_id=pipeline_block_id
                )
                return True
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline block not found or already deleted",
                    pipeline_block_id=pipeline_block_id,
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during removing block from pipeline: {e}"
            )
            return False

    # -------------------
    # Pipeline Edge Operations
    # -------------------

    def assign_edge_to_pipeline(self, pipeline_edge_data: PipelineEdgeCreateSchema) -> Optional[PipelineEdgeResponseSchema]:
        """
        Assigns an edge to a pipeline by creating a pipeline_edge entry.

        Args:
            pipeline_edge_data (PipelineEdgeCreateSchema): The data required to assign an edge to a pipeline.

        Returns:
            Optional[PipelineEdgeResponseSchema]: The created pipeline_edge data if successful, None otherwise.
        """
        try:
            data = pipeline_edge_data.dict()
            response = self.supabase_manager.client.table("pipeline_edges").insert(data).execute()

            if response.status_code in [200, 201] and response.data:
                created_pipeline_edge = PipelineEdgeResponseSchema(**response.data[0])
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Edge assigned to pipeline successfully",
                    pipeline_edge_id=created_pipeline_edge.pipeline_edge_id,
                    pipeline_id=created_pipeline_edge.pipeline_id,
                    edge_id=created_pipeline_edge.edge_id
                )
                return created_pipeline_edge
            else:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to assign edge to pipeline",
                    status_code=response.status_code,
                    error=response.error
                )
                return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during assigning edge to pipeline: {e}"
            )
            return None

    def get_pipeline_edges(self, pipeline_id: UUID) -> Optional[List[PipelineEdgeResponseSchema]]:
        """
        Retrieves all edges assigned to a specific pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.

        Returns:
            Optional[List[PipelineEdgeResponseSchema]]: A list of pipeline_edge entries if successful, None otherwise.
        """
        try:
            response = self.supabase_manager.client.table("pipeline_edges").select("*").eq("pipeline_id", str(pipeline_id)).execute()

            if response.status_code == 200 and response.data:
                pipeline_edges = [PipelineEdgeResponseSchema(**pe) for pe in response.data]
                self.logger.log(
                    "PipelineService",
                    "info",
                    f"{len(pipeline_edges)} edges retrieved for pipeline {pipeline_id}",
                    pipeline_id=pipeline_id
                )
                return pipeline_edges
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No edges found for the pipeline",
                    pipeline_id=pipeline_id,
                    status_code=response.status_code
                )
                return []
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during retrieving pipeline edges: {e}"
            )
            return None

    def remove_edge_from_pipeline(self, pipeline_edge_id: UUID) -> bool:
        """
        Removes an edge from a pipeline by deleting the pipeline_edge entry.

        Args:
            pipeline_edge_id (UUID): The UUID of the pipeline_edge entry to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_manager.client.table("pipeline_edges").delete().eq("pipeline_edge_id", str(pipeline_edge_id)).execute()

            if response.status_code == 200 and response.count > 0:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Edge removed from pipeline successfully",
                    pipeline_edge_id=pipeline_edge_id
                )
                return True
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline edge not found or already deleted",
                    pipeline_edge_id=pipeline_edge_id,
                    status_code=response.status_code
                )
                return False
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during removing edge from pipeline: {e}"
            )
            return False

    # -------------------
    # Advanced Operations
    # -------------------

    def increment_pipeline_run(self, pipeline_id: UUID) -> bool:
        """
        Increments the times_run and updates the average_runtime for a pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            # Retrieve current pipeline data
            pipeline = self.get_pipeline_by_id(pipeline_id)
            if not pipeline:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Cannot increment run. Pipeline not found.",
                    pipeline_id=pipeline_id
                )
                return False

            # Calculate new times_run and average_runtime
            new_times_run = pipeline.times_run + 1
            # For demonstration, assume we receive the latest runtime externally
            # Here, we'll mock it as a random value or from a parameter
            latest_runtime = 0.0  # Replace with actual runtime value
            if pipeline.average_runtime:
                new_average_runtime = ((pipeline.average_runtime * pipeline.times_run) + latest_runtime) / new_times_run
            else:
                new_average_runtime = latest_runtime

            # Update the pipeline with new metrics
            update_data = {
                "times_run": new_times_run,
                "average_runtime": new_average_runtime
            }
            response = self.supabase_manager.client.table("pipelines").update(update_data).eq("pipeline_id", str(pipeline_id)).execute()

            if response.status_code == 200 and response.data:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline run metrics updated successfully",
                    pipeline_id=pipeline_id,
                    times_run=new_times_run,
                    average_runtime=new_average_runtime
                )
                return True
            else:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to update pipeline run metrics",
                    pipeline_id=pipeline_id,
                    status_code=response.status_code,
                    error=response.error
                )
                return False
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during incrementing pipeline run: {e}"
            )
            return False
