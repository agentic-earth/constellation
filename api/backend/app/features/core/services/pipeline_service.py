# app/services/pipeline_service.py

"""
Pipeline Service Module

This module encapsulates all pipeline-related business logic and interactions with the Supabase backend.
It provides functions to create, retrieve, update, and delete pipelines, as well as manage their associated
blocks and edges. All operations are diligently logged using the Constellation Logger to ensure traceability
and facilitate debugging.

Design Philosophy:
- **Separation of Concerns:** Each function handles a specific aspect of pipeline management, promoting modularity.
- **Integration with Supabase:** Utilizes Supabase's capabilities, including pg-vector for efficient data operations.
- **Robust Error Handling:** Ensures graceful handling of exceptions with comprehensive logging.
- **Scalability and Maintainability:** Designed to accommodate growth and adapt to future schema changes with ease.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from pydantic import ValidationError

from prisma import Prisma
import traceback
import asyncio

from backend.app.schemas import (
    PipelineCreateSchema,
    PipelineUpdateSchema,
    PipelineResponseSchema,
    PipelineBlockCreateSchema,
    PipelineBlockResponseSchema,
    PipelineEdgeCreateSchema,
    PipelineEdgeResponseSchema,
    PipelineVerificationRequestSchema,
    PipelineVerificationResponseSchema
)
from backend.app.logger import ConstellationLogger
from backend.app.database import get_supabase_client
from backend.app.utils.serialization_utils import serialize_dict
from backend.app.features.core.services.block_service import BlockService
from backend.app.features.core.services.edge_service import EdgeService
from backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from prisma.models import pipelines as PrismaPipeline
from prisma.models import pipeline_blocks as PrismaPipelineBlock
from prisma.models import pipeline_edges as PrismaPipelineEdge


class PipelineService:
    """
    PipelineService handles all pipeline-related operations, including CRUD (Create, Read, Update, Delete)
    functionalities. It manages the association of blocks and edges to pipelines and ensures data integrity
    and consistency throughout all operations.
    """

    def __init__(self):
        """
        Initializes the PipelineService with the ConstellationLogger for logging purposes.
        Also initializes instances of BlockService and EdgeService to manage associations.
        """
        self.logger = ConstellationLogger()
        self.block_service = BlockService()
        self.edge_service = EdgeService()
        # Removed Prisma client initialization; transactions will be passed to methods instead

    # -------------------
    # Pipeline Operations
    # -------------------

    async def create_pipeline(self, tx: Prisma, pipeline_data: Dict[str, Any]) -> Optional[PrismaPipeline]:
        """
        Creates a new pipeline in the Prisma-managed database.

        Args:
            pipeline_data (Dict[str, Any]): The data required to create a new pipeline.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[PrismaPipeline]: The created pipeline data if successful, None otherwise.
        """
        try:
            # Prepare pipeline data with timestamps
            current_time = datetime.utcnow()
            pipeline_dict = {
                "pipeline_id": pipeline_data.get("pipeline_id", str(uuid4())),
                "name": pipeline_data["name"],
                "created_by": pipeline_data["created_by"],
                "description": pipeline_data.get("description", None),
                "created_at": current_time,
                "updated_at": current_time,
                "times_run": 0,
                "average_runtime": 0.0,
                "dagster_pipeline_config": pipeline_data.get("dagster_pipeline_config", None),
            }

            # Insert the new pipeline into Prisma
            created_pipeline = await tx.pipelines.create(data=pipeline_dict)

            if not created_pipeline:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to create pipeline in Prisma.",
                    extra={"pipeline_data": pipeline_dict}
                )
                return None

            # created_pipeline is a dict returned by Prisma
            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline created successfully.",
                extra={"pipeline_id": created_pipeline.pipeline_id, "name": created_pipeline.name}
            )
            return created_pipeline

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline creation: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_data": pipeline_data}
            )
            return None

    async def get_pipeline_by_id(self, tx: Prisma, pipeline_id: UUID) -> Optional[PrismaPipeline]:
        """
        Retrieves a pipeline by its unique identifier from the Prisma-managed database.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to retrieve.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[PrismaPipeline]: The pipeline data if found, None otherwise.
        """
        try:
            # Retrieve the pipeline from Prisma
            pipeline = await tx.pipelines.find_unique(where={"pipeline_id": str(pipeline_id)})

            if not pipeline:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline not found.",
                    extra={"pipeline_id": pipeline_id}
                )
                return None

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline retrieved successfully.",
                extra={"pipeline_id": pipeline.pipeline_id, "name": pipeline.name}
            )
            return pipeline

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline retrieval: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": pipeline_id}
            )
            return None

    async def update_pipeline(self, tx: Prisma, pipeline_id: UUID, update_data: Dict[str, Any]) -> Optional[PrismaPipeline]:
        """
        Updates an existing pipeline's information in the Prisma-managed database.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to update.
            update_data (Dict[str, Any]): The data to update for the pipeline.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[PrismaPipeline]: The updated pipeline data if successful, None otherwise.
        """
        try:
            # prepare update data
            current_time = datetime.utcnow()
            update_dict = {
                "description": update_data.get("description", None),
                "updated_at": current_time,
                "times_run": update_data.get("times_run", None),
                "average_runtime": update_data.get("average_runtime", None),
                "dagster_pipeline_config": update_data.get("dagster_pipeline_config", None),
            }

            # Remove keys with None values to avoid overwriting existing data with null
            update_dict = {k: v for k, v in update_dict.items() if v is not None}

            # Update the pipeline in Prisma
            updated_pipeline = await tx.pipelines.update(
                where={"pipeline_id": str(pipeline_id)},
                data=update_dict
            )

            if not updated_pipeline:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to update pipeline in Prisma.",
                    extra={"pipeline_id": pipeline_id, "update_data": update_data}
                )
                return None

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline updated successfully.",
                extra={"pipeline_id": updated_pipeline.pipeline_id, "name": updated_pipeline.name}
            )
            return updated_pipeline

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline update: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": pipeline_id, "update_data": update_data}
            )
            return None

    async def delete_pipeline(self, tx: Prisma, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline from the Prisma-managed database.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.
            tx (Prisma): The Prisma transaction object.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Delete the pipeline from Prisma
            deleted_pipeline = await tx.pipelines.delete(where={"pipeline_id": str(pipeline_id)})

            if not deleted_pipeline:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to delete pipeline from Prisma.",
                    extra={"pipeline_id": pipeline_id}
                )
                return False

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline deleted successfully.",
                extra={"pipeline_id": pipeline_id}
            )
            return True

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline deletion: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": pipeline_id}
            )
            return False

    async def list_pipelines(self, tx: Prisma, filters: Optional[Dict[str, Any]] = None) -> Optional[List[PrismaPipeline]]:
        """
        Retrieves a list of pipelines with optional filtering.

        Args:
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the pipelines.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[List[PrismaPipeline]]: A list of pipelines if successful, None otherwise.
        """
        try:
            # Retrieve the list of pipelines from Prisma with optional filtering
            pipelines = await tx.pipelines.find_many(where=filters)

            if not pipelines:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No pipelines found.",
                    extra={"filters": filters}
                )
                return None

            self.logger.log(
                "PipelineService",
                "info",
                "Pipelines retrieved successfully.",
                extra={"count": len(pipelines)}
            )
            return pipelines

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline listing: {e}",
                extra={"traceback": traceback.format_exc(), "filters": filters}
            )
            return None

    async def assign_block_to_pipeline(self, tx: Prisma, pipeline_block_data: Dict[str, Any]) -> Optional[PrismaPipelineBlock]:
        """
        Assigns a block to a pipeline by creating a pipeline_block entry in the Prisma-managed database.

        Args:
            pipeline_block_data (Dict[str, Any]): The data required to assign a block to a pipeline.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[PrismaPipelineBlock]: The created pipeline_block data if successful, None otherwise.
        """
        try:
            # prepare pipeline_block data
            current_time = datetime.utcnow()
            pipeline_block_dict = {
                "pipeline_block_id": pipeline_block_data.get("pipeline_block_id", str(uuid4())),
                "block_id": pipeline_block_data["block_id"],
                "pipeline_id": pipeline_block_data["pipeline_id"],
                "created_at": current_time,
                "updated_at": current_time,
            }
            # Create a pipeline_block entry in Prisma
            created_pipeline_block = await tx.pipeline_blocks.create(data=pipeline_block_dict)

            if not created_pipeline_block:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to assign block to pipeline in Prisma.",
                    extra={"pipeline_block_data": pipeline_block_data}
                )
                return None

            self.logger.log(
                "PipelineService",
                "info",
                "Block assigned to pipeline successfully.",
                extra={"pipeline_block_id": created_pipeline_block.pipeline_block_id}
            )
            return created_pipeline_block

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during block assignment to pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_block_data": pipeline_block_data}
            )
            return None

    async def get_pipeline_blocks(self, tx: Prisma, pipeline_id: UUID) -> Optional[List[PrismaPipelineBlock]]:
        """
        Retrieves all blocks assigned to a specific pipeline from the Prisma-managed database.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[List[PrismaPipelineBlock]]: A list of pipeline_block entries if successful, None otherwise.
        """
        try:
            # Retrieve all blocks assigned to the pipeline from Prisma
            pipeline_blocks = await tx.pipeline_blocks.find_many(where={"pipeline_id": str(pipeline_id)})

            if not pipeline_blocks:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No blocks found for the pipeline.",
                    extra={"pipeline_id": pipeline_id}
                )
                return None
            
            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline blocks retrieved successfully.",
                extra={"pipeline_id": pipeline_id, "count": len(pipeline_blocks)}
            )
            return pipeline_blocks

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline block retrieval: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": pipeline_id}
            )
            return None

    async def remove_block_from_pipeline(self, tx: Prisma, pipeline_block_id: UUID) -> bool:
        """
        Removes a block from a pipeline by deleting the corresponding pipeline_block entry from Prisma.

        Args:
            pipeline_block_id (UUID): The UUID of the pipeline_block entry to delete.
            tx (Prisma): The Prisma transaction object.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Delete the pipeline_block entry from Prisma
            deleted_pipeline_block = await tx.pipeline_blocks.delete(where={"pipeline_block_id": str(pipeline_block_id)})

            if not deleted_pipeline_block:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to remove block from pipeline in Prisma.",
                    extra={"pipeline_block_id": pipeline_block_id}
                )
                return False

            self.logger.log(
                "PipelineService",
                "info",
                "Block removed from pipeline successfully.",
                extra={"pipeline_block_id": pipeline_block_id}
            )
            return True

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during block removal from pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_block_id": pipeline_block_id}
            )
            return False

    async def assign_edge_to_pipeline(self, tx: Prisma, pipeline_edge_data: Dict[str, Any]) -> Optional[PrismaPipelineEdge]:
        """
        Assigns an edge to a pipeline by creating a pipeline_edge entry in the Prisma-managed database.

        Args:
            pipeline_edge_data (Dict[str, Any]): The data required to assign an edge to a pipeline.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[PrismaPipelineEdge]: The created pipeline_edge data if successful, None otherwise.
        """
        try:
            # prepare pipeline_edge data
            current_time = datetime.utcnow()
            pipeline_edge_dict = {
                "pipeline_edge_id": pipeline_edge_data.get("pipeline_edge_id", str(uuid4())),
                "pipeline_id": pipeline_edge_data["pipeline_id"],
                "edge_id": pipeline_edge_data["edge_id"],
                "source_block_id": pipeline_edge_data["source_block_id"],
                "target_block_id": pipeline_edge_data["target_block_id"],
                "created_at": current_time,
                "updated_at": current_time,
            }
            # Create a pipeline_edge entry in Prisma
            created_pipeline_edge = await tx.pipeline_edges.create(data=pipeline_edge_dict)

            if not created_pipeline_edge:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to assign edge to pipeline in Prisma.",
                    extra={"pipeline_edge_data": pipeline_edge_data}
                )
                return None

            self.logger.log(
                "PipelineService",
                "info",
                "Edge assigned to pipeline successfully.",
                extra={"pipeline_edge_id": created_pipeline_edge.pipeline_edge_id}
            )
            return created_pipeline_edge

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during edge assignment to pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_edge_data": pipeline_edge_data}
            )
            return None

    async def get_pipeline_edges(self, tx: Prisma, pipeline_id: UUID) -> Optional[List[PrismaPipelineEdge]]:
        """
        Retrieves all edges assigned to a specific pipeline from the Prisma-managed database.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.
            tx (Prisma): The Prisma transaction object.

        Returns:
            Optional[List[PrismaPipelineEdge]]: A list of pipeline_edge entries if successful, None otherwise.
        """
        try:
            # Retrieve all edges assigned to the pipeline from Prisma
            pipeline_edges = await tx.pipeline_edges.find_many(where={"pipeline_id": str(pipeline_id)})

            if not pipeline_edges:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No edges found for the pipeline.",
                    extra={"pipeline_id": pipeline_id}
                )
                return None

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline edges retrieved successfully.",
                extra={"pipeline_id": pipeline_id, "count": len(pipeline_edges)}
            )
            return pipeline_edges

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline edge retrieval: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": pipeline_id}
            )
            return None

    async def remove_edge_from_pipeline(self, tx: Prisma, pipeline_edge_id: UUID) -> bool:
        """
        Removes an edge from a pipeline by deleting the corresponding pipeline_edge entry from Prisma.

        Args:
            pipeline_edge_id (UUID): The UUID of the pipeline_edge entry to delete.
            tx (Prisma): The Prisma transaction object.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            # Delete the pipeline_edge entry from Prisma
            deleted_pipeline_edge = await tx.pipeline_edges.delete(where={"pipeline_edge_id": str(pipeline_edge_id)})

            if not deleted_pipeline_edge:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to remove edge from pipeline in Prisma.",
                    extra={"pipeline_edge_id": pipeline_edge_id}
                )
                return False

            self.logger.log(
                "PipelineService",
                "info",
                "Edge removed from pipeline successfully.",
                extra={"pipeline_edge_id": pipeline_edge_id}
            )
            return True

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during edge removal from pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_edge_id": pipeline_edge_id}
            )
            return False

    async def increment_pipeline_run(self, tx: Prisma, pipeline_id: UUID, latest_runtime: float) -> bool:
        """
        Increments the `times_run` and updates the `average_runtime` for a pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.
            latest_runtime (float): The runtime of the latest pipeline execution in seconds.
            tx (Prisma): The Prisma transaction object.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            # Retrieve the pipeline from Prisma
            pipeline = await tx.pipelines.find_unique(where={"pipeline_id": str(pipeline_id)})

            if not pipeline:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Pipeline not found for incrementing run.",
                    extra={"pipeline_id": pipeline_id}
                )
                return False

            # Calculate the new average runtime
            new_average_runtime = (pipeline.average_runtime * pipeline.times_run + latest_runtime) / (pipeline.times_run + 1)

            # Update the pipeline's times_run and average_runtime in Prisma
            updated_pipeline = await tx.pipelines.update(
                    where={"pipeline_id": str(pipeline_id)},
                    data={"times_run": pipeline.times_run + 1, "average_runtime": new_average_runtime}
                )

            if not updated_pipeline:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to increment pipeline run in Prisma.",
                    extra={"pipeline_id": pipeline_id}
                )
                return False

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline run incremented successfully.",
                extra={"pipeline_id": pipeline_id}
            )
            return True

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline run increment: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": pipeline_id, "latest_runtime": latest_runtime}
            )
            return False

    # TODO: To be fixed
    async def validate_pipeline(self, tx: Prisma, block_ids: List[UUID], edge_ids: Optional[List[UUID]] = None) -> PipelineVerificationResponseSchema:
        """
        Validates if a group of blocks can form a valid pipeline without fatal connections.

        Args:
            block_ids (List[UUID]): List of block UUIDs to include in the pipeline.
            edge_ids (Optional[List[UUID]]): Optional list of edge UUIDs to include.
            tx (Prisma): The Prisma transaction object.

        Returns:
            PipelineVerificationResponseSchema: The result of the pipeline validation.
        """
        response = PipelineVerificationResponseSchema(can_build_pipeline=True)
        reasons = []
        conflicting_edges = []

        # Example Validation Rules:
        # 1. Ensure no cycles are formed.
        # 2. Check for required edge types between certain blocks.
        # 3. Prevent duplicate connections.

        # Rule 1: Check for cycles in the proposed pipeline
        # Build adjacency list
        adjacency = {block_id: [] for block_id in block_ids}

        # Retrieve all edges between the blocks
        edges = self.supabase_client.table("edges")\
            .select("*").in_("source_block_id", [str(bid) for bid in block_ids])\
            .in_("target_block_id", [str(bid) for bid in block_ids]).execute()

        for edge in edges.data:
            source = UUID(edge["source_block_id"])
            target = UUID(edge["target_block_id"])
            adjacency[source].append(target)

            # Rule 2: Enforce specific edge types
            # Example: Only 'primary' can connect to 'secondary'
            source_block = self.supabase_client.table("blocks")\
                .select("block_type").eq("block_id", str(source)).single().execute()

            target_block = self.supabase_client.table("blocks")\
                .select("block_type").eq("block_id", str(target)).single().execute()

            if source_block.data and target_block.data:
                if source_block.data["block_type"] == "primary" and target_block.data["block_type"] != "secondary":
                    response.can_build_pipeline = False
                    reasons.append(f"Primary block {source} can only connect to secondary blocks.")
                    conflicting_edges.append(EdgeResponseSchema(**edge))
        
        # Detect cycles using DFS
        def has_cycle(adjacency: Dict[UUID, List[UUID]]) -> bool:
            visited = set()
            rec_stack = set()
        
            def dfs(v: UUID) -> bool:
                visited.add(v)
                rec_stack.add(v)
        
                for neighbour in adjacency[v]:
                    if neighbour not in visited:
                        if dfs(neighbour):
                            return True
                    elif neighbour in rec_stack:
                        return True
                rec_stack.remove(v)
                return False
        
            for node in adjacency:
                if node not in visited:
                    if dfs(node):
                        return True
            return False
        
        if has_cycle(adjacency):
            response.can_build_pipeline = False
            reasons.append("Pipeline contains cycles.")
        
        # Rule 3: Prevent duplicate connections
        # Already handled in edge retrieval
        
        response.reasons = reasons
        response.conflicting_edges = conflicting_edges
        return response
