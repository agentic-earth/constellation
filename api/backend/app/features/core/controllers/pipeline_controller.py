# app/controllers/pipeline_controller.py

"""
Pipeline Controller Module

This module defines the PipelineController class responsible for managing pipeline-related operations.
It orchestrates interactions between PipelineService, BlockService, EdgeService, and AuditService
to perform CRUD operations and handle complex workflows involving pipelines, their associated blocks,
and edges.

Responsibilities:
- Coordinating between PipelineService, BlockService, EdgeService, and AuditService to perform complex operations.
- Handling CRUD operations for pipelines, including the association of blocks and edges.
- Managing advanced workflows such as creating or deleting pipelines along with their dependencies.
- Ensuring transactional integrity and robust error handling.
- Managing audit logs through AuditService.

Design Philosophy:
- Maintain high cohesion by focusing solely on pipeline-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.
"""

import traceback
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status

from backend.app.features.core.services.pipeline_service import PipelineService
from backend.app.features.core.services.block_service import BlockService
from backend.app.features.core.services.edge_service import EdgeService
from backend.app.features.core.services.audit_service import AuditService
from backend.app.schemas import (
    PipelineCreateSchema,
    PipelineUpdateSchema,
    PipelineResponseSchema,
    PipelineBlockCreateSchema,
    PipelineEdgeCreateSchema,
    PipelineBlockResponseSchema,
    PipelineEdgeResponseSchema,
    PipelineVerificationRequestSchema,
    PipelineVerificationResponseSchema,
)
from backend.app.logger import ConstellationLogger
from prisma import Prisma
from prisma.models import pipelines as PrismaPipeline


class PipelineController:
    """
    PipelineController manages all pipeline-related operations, coordinating between PipelineService,
    BlockService, EdgeService, and AuditService to perform CRUD operations and handle complex workflows.
    """

    def __init__(self, prisma: Prisma):
        """
        Initializes the PipelineController with instances of PipelineService, BlockService,
        EdgeService, and AuditService, along with the ConstellationLogger for logging purposes.
        """
        self.prisma = prisma
        self.pipeline_service = PipelineService()
        self.block_service = BlockService()
        self.edge_service = EdgeService()
        self.audit_service = AuditService()
        self.logger = ConstellationLogger()

    # -------------------
    # Pipeline CRUD Operations
    # -------------------

    async def create_pipeline(self, pipeline_data: PipelineCreateSchema) -> Optional[PrismaPipeline]:
        """
        Creates a new pipeline.

        Args:
            pipeline_data (PipelineCreateSchema): The data required to create a new pipeline.

        Returns:
            PrismaPipeline: The created pipeline data if successful.

        Raises:
            HTTPException: If pipeline creation fails due to validation or server errors.
        """
        try:
            async with self.prisma.tx() as tx:
                # Create the pipeline using the PipelineService
                pipeline = await self.pipeline_service.create_pipeline(tx, pipeline_data)
                if not pipeline:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Pipeline creation failed due to invalid data.",
                    )

                # Log the creation in Audit Logs
                audit_log = {
                    "user_id": pipeline_data.created_by,
                    "action_type": "CREATE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": f"Pipeline '{pipeline.name}' created successfully.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Log the creation event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline created successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "PipelineController",
                "error",
                f"HTTPException during pipeline creation: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline creation: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline creation.",
            )

    async def get_pipeline_by_id(self, pipeline_id: UUID) -> Optional[PrismaPipeline]:
        """
        Retrieves a pipeline by its unique identifier.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to retrieve.

        Returns:
            PrismaPipeline: The pipeline data if found.

        Raises:
            HTTPException: If the pipeline is not found or retrieval fails.
        """
        try:
            async with self.prisma.tx() as tx:
                # Retrieve the pipeline using the PipelineService
                pipeline = await self.pipeline_service.get_pipeline_by_id(tx, pipeline_id)
                if not pipeline:
                    # Log the failed retrieval in Audit Logs
                    audit_log = {
                        "user_id": None,  # Replace with actual user ID if available
                        "action_type": "READ",
                        "entity_type": "pipeline",
                        "entity_id": str(pipeline_id),
                        "details": "Pipeline not found.",
                    }
                    self.audit_service.create_audit_log(audit_log)

                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="Pipeline not found."
                    )

                # Log the successful retrieval in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "READ",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": f"Pipeline '{pipeline.name}' retrieved successfully.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Log the retrieval event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline retrieved successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "PipelineController",
                "error",
                f"HTTPException during pipeline retrieval: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline retrieval: {str(e)}",
                extra={
                    "traceback": traceback.format_exc(),
                    "pipeline_id": str(pipeline_id),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline retrieval.",
            )

    async def update_pipeline(self, pipeline_id: UUID, update_data: PipelineUpdateSchema) -> Optional[PrismaPipeline]:
        """
        Updates an existing pipeline's information.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to update.
            update_data (PipelineUpdateSchema): The data to update for the pipeline.

        Returns:
            PipelineResponseSchema: The updated pipeline data if successful.

        Raises:
            HTTPException: If pipeline update fails due to validation or server errors.
        """
        try:
            async with self.prisma.tx() as tx:
                # Update the pipeline using the PipelineService
                pipeline = await self.pipeline_service.update_pipeline(tx, pipeline_id, update_data)
                if not pipeline:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Pipeline update failed due to invalid data.",
                    )

                # Log the update in Audit Logs
                audit_log = {
                    "user_id": update_data.updated_by,
                    "action_type": "UPDATE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": f"Pipeline '{pipeline.name}' updated with fields: {list(update_data.dict().keys())}.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Log the update event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline updated successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "PipelineController",
                "error",
                f"HTTPException during pipeline update: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline update: {str(e)}",
                extra={
                    "traceback": traceback.format_exc(),
                    "pipeline_id": str(pipeline_id),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline update.",
            )

    async def delete_pipeline(self, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        Raises:
            HTTPException: If pipeline deletion fails.
        """
        try:
            async with self.prisma.tx() as tx:
                # Delete the pipeline using the PipelineService
                deletion_success = self.pipeline_service.delete_pipeline(pipeline_id)
                if not deletion_success:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Pipeline deletion failed.",
                    )

                # Log the deletion in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "DELETE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline_id),
                    "details": f"Pipeline '{pipeline_id}' deleted successfully.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Log the deletion event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline deleted successfully.",
                    extra={"pipeline_id": str(pipeline_id)},
                )
                return True

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "PipelineController",
                "error",
                f"HTTPException during pipeline deletion: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline deletion: {str(e)}",
                extra={
                    "traceback": traceback.format_exc(),
                    "pipeline_id": str(pipeline_id),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline deletion.",
            )

    async def list_pipelines(self, filters: Optional[Dict[str, Any]] = None) -> List[PrismaPipeline]:
        """
        Lists pipelines with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the pipelines.

        Returns:
            List[PipelineResponseSchema]: A list of pipelines if successful, empty list otherwise.

        Raises:
            HTTPException: If pipeline listing fails due to server errors.
        """
        try:
            async with self.prisma.tx() as tx:
                # List pipelines using the PipelineService
                pipelines = self.pipeline_service.list_pipelines(filters)
                if pipelines is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve pipelines.",
                    )

                # Log the listing in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "READ",
                    "entity_type": "pipeline",
                    "entity_id": None,
                    "details": f"Listed pipelines with filters: {filters}.",
                }
                self.audit_service.create_audit_log(audit_log)

                # Log the listing event
                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Listed {len(pipelines)} pipelines successfully.",
                    extra={"filters": filters},
                )
                return pipelines

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "PipelineController",
                "error",
                f"HTTPException during pipeline listing: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline listing: {str(e)}",
                extra={"traceback": traceback.format_exc(), "filters": filters},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline listing.",
            )

    # -------------------
    # Advanced Pipeline Operations
    # -------------------

    async def create_pipeline_with_dependencies(
        self,
        pipeline_data: PipelineCreateSchema,
        blocks: List[PipelineBlockCreateSchema],
        edges: List[PipelineEdgeCreateSchema],
    ) -> PrismaPipeline:
        """
        Creates a pipeline along with its associated blocks and edges.

        Args:
            pipeline_data (PipelineCreateSchema): Data to create the pipeline.
            blocks (List[PipelineBlockCreateSchema]): List of blocks to assign to the pipeline.
            edges (List[PipelineEdgeCreateSchema]): List of edges to assign to the pipeline.

        Returns:
            PipelineResponseSchema: The created pipeline data if successful.

        Raises:
            HTTPException: If any part of the creation process fails.
        """
        try:
            async with self.prisma.tx() as tx:
                # Create the pipeline
                pipeline = await self.pipeline_service.create_pipeline(tx, pipeline_data)
                if not pipeline:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to create pipeline.",
                    )
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline created successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )

                # Assign blocks to the pipeline
                for block_data in blocks:
                    assigned_block = await self.block_service.create_block(tx, block_data.block_data)
                    if not assigned_block:
                        self.logger.log(
                            "PipelineController",
                            "error",
                            f"Failed to create block: {block_data.block_data.name}",
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to create block: {block_data.block_data.name}",
                        )

                    # Assign the block to the pipeline
                    assigned_pipeline_block = (
                        await self.pipeline_service.assign_block_to_pipeline(tx, block_data)
                    )
                    if not assigned_pipeline_block:
                        self.logger.log(
                            "PipelineController",
                            "error",
                            f"Failed to assign block {assigned_block.block_id} to pipeline.",
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to assign block {assigned_block.block_id} to pipeline.",
                        )

                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Block {assigned_block.block_id} assigned to pipeline {pipeline.pipeline_id}.",
                    )

                # Assign edges to the pipeline
                for edge_data in edges:
                    assigned_edge = await self.edge_service.create_edge(tx, edge_data.edge_data)
                    if not assigned_edge:
                        self.logger.log(
                            "PipelineController",
                            "error",
                            f"Failed to create edge: {edge_data.edge_data.name}",
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to create edge: {edge_data.edge_data.name}",
                        )

                    # Assign the edge to the pipeline
                    assigned_pipeline_edge = await self.pipeline_service.assign_edge_to_pipeline(
                        tx, edge_data
                    )
                    if not assigned_pipeline_edge:
                        self.logger.log(
                            "PipelineController",
                            "error",
                            f"Failed to assign edge {assigned_edge.edge_id} to pipeline.",
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to assign edge {assigned_edge.edge_id} to pipeline.",
                        )

                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Edge {assigned_edge.edge_id} assigned to pipeline {pipeline.pipeline_id}.",
                    )

                # Log the creation in Audit Logs
                audit_log = {
                    "user_id": pipeline_data.created_by,
                    "action_type": "CREATE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": f"Pipeline '{pipeline.name}' created with {len(blocks)} blocks and {len(edges)} edges.",
                }
                self.audit_service.create_audit_log(audit_log)

                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline and dependencies created successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "PipelineController",
                "error",
                f"HTTPException during creating pipeline with dependencies: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during creating pipeline with dependencies: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline creation with dependencies.",
            )

    async def delete_pipeline_with_dependencies(self, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline along with all its associated blocks and edges.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.

        Raises:
            HTTPException: If any part of the deletion process fails.
        """
        try:
            async with self.prisma.tx() as tx:
                # Retrieve all blocks associated with the pipeline
                pipeline_blocks = await self.pipeline_service.get_pipeline_blocks(tx, pipeline_id)
                if pipeline_blocks is None:
                    self.logger.log(
                        "PipelineController", "error", "Failed to retrieve pipeline blocks."
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve pipeline blocks.",
                    )

                # Retrieve all edges associated with the pipeline
                pipeline_edges = await self.pipeline_service.get_pipeline_edges(tx, pipeline_id)
                if pipeline_edges is None:
                    self.logger.log(
                        "PipelineController", "error", "Failed to retrieve pipeline edges."
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve pipeline edges.",
                    )

                # Delete all edges first to maintain referential integrity
                for edge in pipeline_edges:
                    success = await self.pipeline_service.remove_edge_from_pipeline(
                        tx, edge.pipeline_edge_id
                    )
                    if not success:
                        self.logger.log(
                            "PipelineController",
                            "error",
                            f"Failed to delete edge {edge.pipeline_edge_id} from pipeline.",
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to delete edge {edge.pipeline_edge_id} from pipeline.",
                        )

                    # Optionally, delete the edge entity itself
                    await self.edge_service.delete_edge(tx, edge.edge_id)
                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Edge {edge.edge_id} deleted successfully.",
                    )

                # Delete all blocks
                for block in pipeline_blocks:
                    success = await self.pipeline_service.remove_block_from_pipeline(
                        tx, block.pipeline_block_id
                    )
                    if not success:
                        self.logger.log(
                            "PipelineController",
                            "error",
                            f"Failed to delete block {block.pipeline_block_id} from pipeline.",
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Failed to delete block {block.pipeline_block_id} from pipeline.",
                        )

                    # Optionally, delete the block entity itself
                    await self.block_service.delete_block(tx, block.block_id)
                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Block {block.block_id} deleted successfully.",
                    )

                # Finally, delete the pipeline
                success = await self.pipeline_service.delete_pipeline(tx, pipeline_id)
                if not success:
                    self.logger.log(
                        "PipelineController",
                        "error",
                        f"Failed to delete pipeline {pipeline_id}.",
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Pipeline deletion failed.",
                    )

                # Log the deletion in Audit Logs
                audit_log = {
                    "user_id": None,  # Replace with actual user ID if available
                    "action_type": "DELETE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline_id),
                    "details": f"Pipeline '{pipeline_id}' and all associated blocks and edges were deleted.",
                }
                await self.audit_service.create_audit_log(audit_log)

                # Log the deletion event
                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Pipeline {pipeline_id} and all associated blocks and edges deleted successfully.",
                    extra={"pipeline_id": str(pipeline_id)},
                )
                return True

        except HTTPException as he:
            # Log HTTPExceptions with error level
            self.logger.log(
                "PipelineController",
                "error",
                f"HTTPException during deleting pipeline with dependencies: {he.detail}",
                extra={"status_code": he.status_code, "detail": he.detail},
            )
            raise he
        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during deleting pipeline with dependencies: {str(e)}",
                extra={
                    "traceback": traceback.format_exc(),
                    "pipeline_id": str(pipeline_id),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline deletion with dependencies.",
            )

    ## TODO: to be fixed
    def verify_pipeline(
        self, verification_request: PipelineVerificationRequestSchema
    ) -> PipelineVerificationResponseSchema:
        """
        Verifies if a group of blocks can form a valid pipeline.

        Args:
            verification_request (PipelineVerificationRequestSchema): The block IDs to include in the pipeline.

        Returns:
            PipelineVerificationResponseSchema: The result of the pipeline validation.
        """
        try:
            # Use PipelineService to perform the validation
            validation_result = self.pipeline_service.validate_pipeline(
                block_ids=verification_request.block_ids
            )

            # Log the verification in Audit Logs
            audit_log = {
                "user_id": None,  # Replace with actual user ID if available
                "action_type": "READ",
                "entity_type": "pipeline",
                "entity_id": "validation",
                "details": f"Pipeline validation for blocks: {verification_request.block_ids}.",
            }
            self.audit_service.create_audit_log(audit_log)

            # Log the verification event
            self.logger.log(
                "PipelineController",
                "info",
                "Pipeline validation performed.",
                extra={
                    "block_ids": [str(bid) for bid in verification_request.block_ids],
                    "can_build_pipeline": validation_result.can_build_pipeline,
                },
            )
            return validation_result

        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline validation: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error during pipeline validation.",
            )
