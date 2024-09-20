# app/controllers/pipeline_controller.py

"""
Pipeline Controller Module

This module defines the PipelineController class responsible for orchestrating pipeline-related operations
that may involve multiple services. It handles both basic CRUD operations for pipelines and complex workflows
such as creating or deleting pipelines along with their associated blocks and edges.

Responsibilities:
- Coordinating between PipelineService, BlockService, EdgeService, and AuditService to perform complex operations.
- Managing transactions to ensure data consistency across multiple service operations.
- Handling higher-level business logic that spans multiple entities.

Design Philosophy:
- Maintain high cohesion by focusing solely on pipeline-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.

Usage Example:
    from app.controllers import PipelineController

    pipeline_controller = PipelineController()
    pipeline = pipeline_controller.create_pipeline_with_dependencies(pipeline_data, blocks, edges)
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from app.services import (
    PipelineService,
    BlockService,
    EdgeService,
    AuditService
)
from app.schemas import (
    PipelineCreateSchema,
    PipelineUpdateSchema,
    PipelineResponseSchema,
    PipelineBlockCreateSchema,
    PipelineEdgeCreateSchema
)
from app.logger import ConstellationLogger

class PipelineController:
    """
    PipelineController orchestrates complex pipeline operations involving multiple services.
    """

    def __init__(self):
        """
        Initializes the PipelineController with instances of PipelineService, BlockService,
        EdgeService, and AuditService, along with the ConstellationLogger for logging purposes.
        """
        self.pipeline_service = PipelineService()
        self.block_service = BlockService()
        self.edge_service = EdgeService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Basic Pipeline Operations
    # -------------------

    def create_pipeline(self, pipeline_data: PipelineCreateSchema) -> Optional[PipelineResponseSchema]:
        """
        Creates a new pipeline.

        Args:
            pipeline_data (PipelineCreateSchema): The data required to create a new pipeline.

        Returns:
            Optional[PipelineResponseSchema]: The created pipeline data if successful, None otherwise.
        """
        return self.pipeline_service.create_pipeline(pipeline_data)

    def get_pipeline_by_id(self, pipeline_id: UUID) -> Optional[PipelineResponseSchema]:
        """
        Retrieves a pipeline by its unique identifier.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to retrieve.

        Returns:
            Optional[PipelineResponseSchema]: The pipeline data if found, None otherwise.
        """
        return self.pipeline_service.get_pipeline_by_id(pipeline_id)

    def update_pipeline(self, pipeline_id: UUID, update_data: PipelineUpdateSchema) -> Optional[PipelineResponseSchema]:
        """
        Updates an existing pipeline's information.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to update.
            update_data (PipelineUpdateSchema): The data to update for the pipeline.

        Returns:
            Optional[PipelineResponseSchema]: The updated pipeline data if successful, None otherwise.
        """
        return self.pipeline_service.update_pipeline(pipeline_id, update_data)

    def delete_pipeline(self, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        return self.pipeline_service.delete_pipeline(pipeline_id)

    def list_pipelines(self, filters: Optional[Dict[str, Any]] = None) -> Optional[List[PipelineResponseSchema]]:
        """
        Lists pipelines with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the pipelines.

        Returns:
            Optional[List[PipelineResponseSchema]]: A list of pipelines if successful, None otherwise.
        """
        return self.pipeline_service.list_pipelines(filters)

    # -------------------
    # Complex Pipeline Operations
    # -------------------

    def create_pipeline_with_dependencies(
        self,
        pipeline_data: PipelineCreateSchema,
        blocks: List[PipelineBlockCreateSchema],
        edges: List[PipelineEdgeCreateSchema]
    ) -> Optional[PipelineResponseSchema]:
        """
        Creates a pipeline along with its associated blocks and edges.

        Args:
            pipeline_data (PipelineCreateSchema): Data to create the pipeline.
            blocks (List[PipelineBlockCreateSchema]): List of blocks to assign to the pipeline.
            edges (List[PipelineEdgeCreateSchema]): List of edges to assign to the pipeline.

        Returns:
            Optional[PipelineResponseSchema]: The created pipeline data if successful, None otherwise.
        """
        try:
            # Create the pipeline
            pipeline = self.pipeline_service.create_pipeline(pipeline_data)
            if not pipeline:
                self.logger.log("PipelineController", "error", "Pipeline creation failed.")
                return None

            self.logger.log("PipelineController", "info", "Pipeline created successfully.", pipeline_id=pipeline.pipeline_id)

            # Assign blocks to the pipeline
            for block in blocks:
                assigned_block = self.block_service.create_block(block.block_data)
                if not assigned_block:
                    self.logger.log("PipelineController", "error", f"Failed to create block: {block.block_data.name}")
                    raise Exception(f"Failed to create block: {block.block_data.name}")

                pipeline_block = PipelineBlockCreateSchema(
                    pipeline_id=pipeline.pipeline_id,
                    block_id=assigned_block.block_id
                )
                assigned_pipeline_block = self.pipeline_service.assign_block_to_pipeline(pipeline_block)
                if not assigned_pipeline_block:
                    self.logger.log("PipelineController", "error", f"Failed to assign block {assigned_block.block_id} to pipeline.")
                    raise Exception(f"Failed to assign block {assigned_block.block_id} to pipeline.")

                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Block {assigned_block.block_id} assigned to pipeline {pipeline.pipeline_id}."
                )

            # Assign edges to the pipeline
            for edge in edges:
                assigned_edge = self.edge_service.create_edge(edge.edge_data)
                if not assigned_edge:
                    self.logger.log("PipelineController", "error", f"Failed to create edge: {edge.edge_data.name}")
                    raise Exception(f"Failed to create edge: {edge.edge_data.name}")

                pipeline_edge = PipelineEdgeCreateSchema(
                    pipeline_id=pipeline.pipeline_id,
                    edge_id=assigned_edge.edge_id,
                    source_block_id=edge.source_block_id,
                    target_block_id=edge.target_block_id
                )
                assigned_pipeline_edge = self.pipeline_service.assign_edge_to_pipeline(pipeline_edge)
                if not assigned_pipeline_edge:
                    self.logger.log("PipelineController", "error", f"Failed to assign edge {assigned_edge.edge_id} to pipeline.")
                    raise Exception(f"Failed to assign edge {assigned_edge.edge_id} to pipeline.")

                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Edge {assigned_edge.edge_id} assigned to pipeline {pipeline.pipeline_id}."
                )

            # Optionally, create an audit log for the creation
            audit_log = {
                "user_id": pipeline_data.created_by,
                "action_type": "CREATE",
                "entity_type": "pipeline",
                "entity_id": pipeline.pipeline_id,
                "details": f"Pipeline '{pipeline.name}' created with {len(blocks)} blocks and {len(edges)} edges."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "PipelineController",
                "info",
                "Pipeline and dependencies created successfully.",
                pipeline_id=pipeline.pipeline_id
            )
            return pipeline

        except Exception as e:
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during creating pipeline with dependencies: {e}"
            )
            # Optional: Implement rollback mechanisms here if necessary
            return None

    def delete_pipeline_with_dependencies(self, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline along with all its associated blocks and edges.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Retrieve all blocks associated with the pipeline
            pipeline_blocks = self.pipeline_service.get_pipeline_blocks(pipeline_id)
            if pipeline_blocks is None:
                self.logger.log("PipelineController", "error", "Failed to retrieve pipeline blocks.")
                return False

            # Retrieve all edges associated with the pipeline
            pipeline_edges = self.pipeline_service.get_pipeline_edges(pipeline_id)
            if pipeline_edges is None:
                self.logger.log("PipelineController", "error", "Failed to retrieve pipeline edges.")
                return False

            # Delete all edges first to maintain referential integrity
            for edge in pipeline_edges:
                success = self.pipeline_service.remove_edge_from_pipeline(edge.pipeline_edge_id)
                if not success:
                    self.logger.log("PipelineController", "error", f"Failed to delete edge {edge.pipeline_edge_id} from pipeline.")
                    raise Exception(f"Failed to delete edge {edge.pipeline_edge_id} from pipeline.")

                # Optionally, delete the edge entity itself
                self.edge_service.delete_edge(edge.edge_id)
                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Edge {edge.edge_id} deleted successfully."
                )

            # Delete all blocks
            for block in pipeline_blocks:
                success = self.pipeline_service.remove_block_from_pipeline(block.pipeline_block_id)
                if not success:
                    self.logger.log("PipelineController", "error", f"Failed to delete block {block.pipeline_block_id} from pipeline.")
                    raise Exception(f"Failed to delete block {block.pipeline_block_id} from pipeline.")

                # Optionally, delete the block entity itself
                self.block_service.delete_block(block.block_id)
                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Block {block.block_id} deleted successfully."
                )

            # Finally, delete the pipeline
            success = self.pipeline_service.delete_pipeline(pipeline_id)
            if not success:
                self.logger.log("PipelineController", "error", f"Failed to delete pipeline {pipeline_id}.")
                return False

            # Optionally, create an audit log for the deletion
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "DELETE",
                "entity_type": "pipeline",
                "entity_id": pipeline_id,
                "details": f"Pipeline {pipeline_id} and all associated blocks and edges were deleted."
            }
            self.audit_service.create_audit_log(audit_log)

            self.logger.log(
                "PipelineController",
                "info",
                f"Pipeline {pipeline_id} and all associated blocks and edges deleted successfully."
            )
            return True

        except Exception as e:
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during deleting pipeline with dependencies: {e}"
            )
            # Optional: Implement rollback mechanisms here if necessary
            return False
