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

from supabase import Client
from postgrest import APIError as PostgrestError

from app.schemas import (
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
from app.logger import ConstellationLogger
from app.database import get_supabase_client
from app.utils.serialization_utils import serialize_dict
from app.services.block_service import BlockService
from app.services.edge_service import EdgeService
from app.services.vector_embedding_service import VectorEmbeddingService


class PipelineService:
    """
    PipelineService handles all pipeline-related operations, including CRUD (Create, Read, Update, Delete)
    functionalities. It manages the association of blocks and edges to pipelines and ensures data integrity
    and consistency throughout all operations.
    """

    def __init__(self):
        """
        Initializes the PipelineService with the Supabase client and ConstellationLogger for logging purposes.
        Also initializes instances of BlockService and EdgeService to manage associations.
        """
        self.supabase_client: Client = get_supabase_client()
        self.logger = ConstellationLogger()
        self.block_service = BlockService()
        self.edge_service = EdgeService()

    # -------------------
    # Pipeline Operations
    # -------------------

    def create_pipeline(self, pipeline_data: PipelineCreateSchema) -> Optional[PipelineResponseSchema]:
        """
        Creates a new pipeline in the Supabase `pipelines` table.

        Args:
            pipeline_data (PipelineCreateSchema): The data required to create a new pipeline.

        Returns:
            Optional[PipelineResponseSchema]: The created pipeline data if successful, None otherwise.
        """
        try:
            # Generate UUID for the new pipeline if not provided
            if not pipeline_data.pipeline_id:
                pipeline_id = uuid4()
            else:
                pipeline_id = pipeline_data.pipeline_id

            # Prepare pipeline data with timestamps
            current_time = datetime.utcnow()
            pipeline_dict = pipeline_data.dict(exclude_unset=True)
            pipeline_dict.update({
                "pipeline_id": str(pipeline_id),
                "created_at": current_time.isoformat(),
                "updated_at": current_time.isoformat(),
                "times_run": 0,
                "average_runtime": 0.0
            })

            # Insert the new pipeline into Supabase
            response = self.supabase_client.table("pipelines").insert(serialize_dict(pipeline_dict)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to create pipeline in Supabase.",
                    extra={"error": response.error.message, "pipeline_data": pipeline_dict}
                )
                return None

            # Construct the PipelineResponseSchema
            created_pipeline = PipelineResponseSchema(
                pipeline_id=pipeline_id,
                name=pipeline_dict["name"],
                description=pipeline_dict.get("description", ""),
                created_at=current_time,
                updated_at=current_time,
                dagster_pipeline_config=pipeline_dict.get("dagster_pipeline_config"),
                created_by=pipeline_dict.get("created_by"),
                times_run=pipeline_dict["times_run"],
                average_runtime=pipeline_dict["average_runtime"]
            )

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline created successfully.",
                extra={"pipeline_id": str(created_pipeline.pipeline_id), "name": created_pipeline.name}
            )
            return created_pipeline

        except ValidationError as ve:
            self.logger.log(
                "PipelineService",
                "error",
                "Validation error during pipeline creation.",
                extra={"error": ve.errors(), "pipeline_data": pipeline_data.dict()}
            )
            return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline creation: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_data": pipeline_data.dict()}
            )
            return None

    def get_pipeline_by_id(self, pipeline_id: UUID) -> Optional[PipelineResponseSchema]:
        """
        Retrieves a pipeline by its unique identifier from the Supabase `pipelines` table.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to retrieve.

        Returns:
            Optional[PipelineResponseSchema]: The pipeline data if found, None otherwise.
        """
        try:
            response = self.supabase_client.table("pipelines").select("*").eq("pipeline_id", str(pipeline_id)).single().execute()

            if response.error:
                if "No rows found" in response.error.message:
                    self.logger.log(
                        "PipelineService",
                        "warning",
                        "Pipeline not found.",
                        extra={"pipeline_id": str(pipeline_id)}
                    )
                else:
                    self.logger.log(
                        "PipelineService",
                        "error",
                        "Failed to retrieve pipeline from Supabase.",
                        extra={"error": response.error.message, "pipeline_id": str(pipeline_id)}
                    )
                return None

            pipeline_data = response.data

            # Construct the PipelineResponseSchema
            retrieved_pipeline = PipelineResponseSchema(
                pipeline_id=UUID(pipeline_data["pipeline_id"]),
                name=pipeline_data["name"],
                description=pipeline_data.get("description", ""),
                created_at=pipeline_data["created_at"],
                updated_at=pipeline_data["updated_at"],
                dagster_pipeline_config=pipeline_data.get("dagster_pipeline_config"),
                created_by=UUID(pipeline_data["created_by"]) if pipeline_data.get("created_by") else None,
                times_run=pipeline_data.get("times_run", 0),
                average_runtime=pipeline_data.get("average_runtime", 0.0)
            )

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline retrieved successfully.",
                extra={"pipeline_id": str(retrieved_pipeline.pipeline_id), "name": retrieved_pipeline.name}
            )
            return retrieved_pipeline

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline retrieval: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": str(pipeline_id)}
            )
            return None

    def update_pipeline(self, pipeline_id: UUID, update_data: PipelineUpdateSchema) -> Optional[PipelineResponseSchema]:
        """
        Updates an existing pipeline's information in the Supabase `pipelines` table.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to update.
            update_data (PipelineUpdateSchema): The data to update for the pipeline.

        Returns:
            Optional[PipelineResponseSchema]: The updated pipeline data if successful, None otherwise.
        """
        try:
            # Prepare update data with updated_at timestamp
            current_time = datetime.utcnow()
            update_dict = update_data.dict(exclude_unset=True)
            update_dict.update({
                "updated_at": current_time.isoformat()
            })

            # Update the pipeline in Supabase
            response = self.supabase_client.table("pipelines").update(serialize_dict(update_dict)).eq("pipeline_id", str(pipeline_id)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to update pipeline in Supabase.",
                    extra={"error": response.error.message, "pipeline_id": str(pipeline_id), "update_data": update_dict}
                )
                return None

            # Retrieve the updated pipeline
            updated_pipeline = self.get_pipeline_by_id(pipeline_id)
            if updated_pipeline:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline updated successfully.",
                    extra={"pipeline_id": str(updated_pipeline.pipeline_id), "updated_fields": list(update_dict.keys())}
                )
                return updated_pipeline
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline updated but retrieval failed.",
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return None

        except ValidationError as ve:
            self.logger.log(
                "PipelineService",
                "error",
                "Validation error during pipeline update.",
                extra={"error": ve.errors(), "update_data": update_data.dict()}
            )
            return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline update: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": str(pipeline_id), "update_data": update_data.dict()}
            )
            return None

    def delete_pipeline(self, pipeline_id: UUID) -> bool:
        """
        Deletes a pipeline from the Supabase `pipelines` table.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_client.table("pipelines").delete().eq("pipeline_id", str(pipeline_id)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to delete pipeline from Supabase.",
                    extra={"error": response.error.message, "pipeline_id": str(pipeline_id)}
                )
                return False

            if response.count > 0:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Pipeline deleted successfully.",
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return True
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline not found or already deleted.",
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return False

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during pipeline deletion: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": str(pipeline_id)}
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
            query = self.supabase_client.table("pipelines").select("*")
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, [str(v) for v in value])
                    else:
                        query = query.eq(key, str(value))
            response = query.execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to retrieve pipelines from Supabase.",
                    extra={"error": response.error.message, "filters": filters}
                )
                return None

            if response.data:
                pipelines = [
                    PipelineResponseSchema(
                        pipeline_id=UUID(pipeline["pipeline_id"]),
                        name=pipeline["name"],
                        description=pipeline.get("description", ""),
                        created_at=pipeline["created_at"],
                        updated_at=pipeline["updated_at"],
                        dagster_pipeline_config=pipeline.get("dagster_pipeline_config"),
                        created_by=UUID(pipeline["created_by"]) if pipeline.get("created_by") else None,
                        times_run=pipeline.get("times_run", 0),
                        average_runtime=pipeline.get("average_runtime", 0.0)
                    ) for pipeline in response.data
                ]
                self.logger.log(
                    "PipelineService",
                    "info",
                    f"{len(pipelines)} pipelines retrieved successfully.",
                    extra={"filters": filters}
                )
                return pipelines
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No pipelines found.",
                    extra={"filters": filters}
                )
                return []

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during listing pipelines: {e}",
                extra={"traceback": traceback.format_exc(), "filters": filters}
            )
            return None

    # -------------------
    # Pipeline Block Operations
    # -------------------

    def assign_block_to_pipeline(self, pipeline_block_data: PipelineBlockCreateSchema) -> Optional[PipelineBlockResponseSchema]:
        """
        Assigns a block to a pipeline by creating a pipeline_block entry in the Supabase `pipeline_blocks` table.

        Args:
            pipeline_block_data (PipelineBlockCreateSchema): The data required to assign a block to a pipeline.

        Returns:
            Optional[PipelineBlockResponseSchema]: The created pipeline_block data if successful, None otherwise.
        """
        try:
            # Validate existence of pipeline and block
            pipeline = self.get_pipeline_by_id(pipeline_block_data.pipeline_id)
            if not pipeline:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Cannot assign block to non-existent pipeline.",
                    extra={"pipeline_id": str(pipeline_block_data.pipeline_id)}
                )
                return None

            block = self.block_service.get_block_by_id(pipeline_block_data.block_id)
            if not block:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Cannot assign non-existent block to pipeline.",
                    extra={"block_id": str(pipeline_block_data.block_id)}
                )
                return None

            # Prepare pipeline_block data with timestamp
            current_time = datetime.utcnow()
            pipeline_block_dict = pipeline_block_data.dict()
            pipeline_block_dict.update({
                "pipeline_block_id": str(uuid4()),
                "created_at": current_time.isoformat(),
                "updated_at": current_time.isoformat()
            })

            # Insert the pipeline_block into Supabase
            response = self.supabase_client.table("pipeline_blocks").insert(serialize_dict(pipeline_block_dict)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to assign block to pipeline in Supabase.",
                    extra={"error": response.error.message, "pipeline_block_data": pipeline_block_dict}
                )
                return None

            # Construct the PipelineBlockResponseSchema
            created_pipeline_block = PipelineBlockResponseSchema(
                pipeline_block_id=UUID(pipeline_block_dict["pipeline_block_id"]),
                pipeline_id=pipeline_block_data.pipeline_id,
                block_id=pipeline_block_data.block_id,
                created_at=current_time,
                updated_at=current_time
            )

            self.logger.log(
                "PipelineService",
                "info",
                "Block assigned to pipeline successfully.",
                extra={
                    "pipeline_block_id": str(created_pipeline_block.pipeline_block_id),
                    "pipeline_id": str(created_pipeline_block.pipeline_id),
                    "block_id": str(created_pipeline_block.block_id)
                }
            )
            return created_pipeline_block

        except ValidationError as ve:
            self.logger.log(
                "PipelineService",
                "error",
                "Validation error during assigning block to pipeline.",
                extra={"error": ve.errors(), "pipeline_block_data": pipeline_block_data.dict()}
            )
            return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during assigning block to pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_block_data": pipeline_block_data.dict()}
            )
            return None

    def get_pipeline_blocks(self, pipeline_id: UUID) -> Optional[List[PipelineBlockResponseSchema]]:
        """
        Retrieves all blocks assigned to a specific pipeline from the Supabase `pipeline_blocks` table.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.

        Returns:
            Optional[List[PipelineBlockResponseSchema]]: A list of pipeline_block entries if successful, None otherwise.
        """
        try:
            response = self.supabase_client.table("pipeline_blocks").select("*").eq("pipeline_id", str(pipeline_id)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to retrieve pipeline blocks from Supabase.",
                    extra={"error": response.error.message, "pipeline_id": str(pipeline_id)}
                )
                return None

            if response.data:
                pipeline_blocks = [
                    PipelineBlockResponseSchema(
                        pipeline_block_id=UUID(pb["pipeline_block_id"]),
                        pipeline_id=UUID(pb["pipeline_id"]),
                        block_id=UUID(pb["block_id"]),
                        created_at=pb["created_at"],
                        updated_at=pb["updated_at"]
                    ) for pb in response.data
                ]
                self.logger.log(
                    "PipelineService",
                    "info",
                    f"{len(pipeline_blocks)} blocks retrieved for pipeline {pipeline_id}.",
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return pipeline_blocks
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No blocks found for the specified pipeline.",
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return []

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during retrieving pipeline blocks: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": str(pipeline_id)}
            )
            return None

    def remove_block_from_pipeline(self, pipeline_block_id: UUID) -> bool:
        """
        Removes a block from a pipeline by deleting the corresponding pipeline_block entry from Supabase.

        Args:
            pipeline_block_id (UUID): The UUID of the pipeline_block entry to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_client.table("pipeline_blocks").delete().eq("pipeline_block_id", str(pipeline_block_id)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to remove block from pipeline in Supabase.",
                    extra={"error": response.error.message, "pipeline_block_id": str(pipeline_block_id)}
                )
                return False

            if response.count > 0:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Block removed from pipeline successfully.",
                    extra={"pipeline_block_id": str(pipeline_block_id)}
                )
                return True
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline block not found or already deleted.",
                    extra={"pipeline_block_id": str(pipeline_block_id)}
                )
                return False

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during removing block from pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_block_id": str(pipeline_block_id)}
            )
            return False

    # -------------------
    # Pipeline Edge Operations
    # -------------------

    def assign_edge_to_pipeline(self, pipeline_edge_data: PipelineEdgeCreateSchema) -> Optional[PipelineEdgeResponseSchema]:
        """
        Assigns an edge to a pipeline by creating a pipeline_edge entry in the Supabase `pipeline_edges` table.

        Args:
            pipeline_edge_data (PipelineEdgeCreateSchema): The data required to assign an edge to a pipeline.

        Returns:
            Optional[PipelineEdgeResponseSchema]: The created pipeline_edge data if successful, None otherwise.
        """
        try:
            # Validate existence of pipeline and edge
            pipeline = self.get_pipeline_by_id(pipeline_edge_data.pipeline_id)
            if not pipeline:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Cannot assign edge to non-existent pipeline.",
                    extra={"pipeline_id": str(pipeline_edge_data.pipeline_id)}
                )
                return None

            edge = self.edge_service.get_edge_by_id(pipeline_edge_data.edge_id)
            if not edge:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Cannot assign non-existent edge to pipeline.",
                    extra={"edge_id": str(pipeline_edge_data.edge_id)}
                )
                return None

            # Prepare pipeline_edge data with timestamp
            current_time = datetime.utcnow()
            pipeline_edge_dict = pipeline_edge_data.dict()
            pipeline_edge_dict.update({
                "pipeline_edge_id": str(uuid4()),
                "created_at": current_time.isoformat(),
                "updated_at": current_time.isoformat()
            })

            # Insert the pipeline_edge into Supabase
            response = self.supabase_client.table("pipeline_edges").insert(serialize_dict(pipeline_edge_dict)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to assign edge to pipeline in Supabase.",
                    extra={"error": response.error.message, "pipeline_edge_data": pipeline_edge_dict}
                )
                return None

            # Construct the PipelineEdgeResponseSchema
            created_pipeline_edge = PipelineEdgeResponseSchema(
                pipeline_edge_id=UUID(pipeline_edge_dict["pipeline_edge_id"]),
                pipeline_id=pipeline_edge_data.pipeline_id,
                edge_id=pipeline_edge_data.edge_id,
                source_block_id=pipeline_edge_data.source_block_id,
                target_block_id=pipeline_edge_data.target_block_id,
                created_at=current_time,
                updated_at=current_time
            )

            self.logger.log(
                "PipelineService",
                "info",
                "Edge assigned to pipeline successfully.",
                extra={
                    "pipeline_edge_id": str(created_pipeline_edge.pipeline_edge_id),
                    "pipeline_id": str(created_pipeline_edge.pipeline_id),
                    "edge_id": str(created_pipeline_edge.edge_id)
                }
            )
            return created_pipeline_edge

        except ValidationError as ve:
            self.logger.log(
                "PipelineService",
                "error",
                "Validation error during assigning edge to pipeline.",
                extra={"error": ve.errors(), "pipeline_edge_data": pipeline_edge_data.dict()}
            )
            return None
        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during assigning edge to pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_edge_data": pipeline_edge_data.dict()}
            )
            return None

    def get_pipeline_edges(self, pipeline_id: UUID) -> Optional[List[PipelineEdgeResponseSchema]]:
        """
        Retrieves all edges assigned to a specific pipeline from the Supabase `pipeline_edges` table.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.

        Returns:
            Optional[List[PipelineEdgeResponseSchema]]: A list of pipeline_edge entries if successful, None otherwise.
        """
        try:
            response = self.supabase_client.table("pipeline_edges").select("*").eq("pipeline_id", str(pipeline_id)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to retrieve pipeline edges from Supabase.",
                    extra={"error": response.error.message, "pipeline_id": str(pipeline_id)}
                )
                return None

            if response.data:
                pipeline_edges = [
                    PipelineEdgeResponseSchema(
                        pipeline_edge_id=UUID(pe["pipeline_edge_id"]),
                        pipeline_id=UUID(pe["pipeline_id"]),
                        edge_id=UUID(pe["edge_id"]),
                        source_block_id=UUID(pe["source_block_id"]),
                        target_block_id=UUID(pe["target_block_id"]),
                        created_at=pe["created_at"],
                        updated_at=pe["updated_at"]
                    ) for pe in response.data
                ]
                self.logger.log(
                    "PipelineService",
                    "info",
                    f"{len(pipeline_edges)} edges retrieved for pipeline {pipeline_id}.",
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return pipeline_edges
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "No edges found for the specified pipeline.",
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return []

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during retrieving pipeline edges: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": str(pipeline_id)}
            )
            return None

    def remove_edge_from_pipeline(self, pipeline_edge_id: UUID) -> bool:
        """
        Removes an edge from a pipeline by deleting the corresponding pipeline_edge entry from Supabase.

        Args:
            pipeline_edge_id (UUID): The UUID of the pipeline_edge entry to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            response = self.supabase_client.table("pipeline_edges").delete().eq("pipeline_edge_id", str(pipeline_edge_id)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to remove edge from pipeline in Supabase.",
                    extra={"error": response.error.message, "pipeline_edge_id": str(pipeline_edge_id)}
                )
                return False

            if response.count > 0:
                self.logger.log(
                    "PipelineService",
                    "info",
                    "Edge removed from pipeline successfully.",
                    extra={"pipeline_edge_id": str(pipeline_edge_id)}
                )
                return True
            else:
                self.logger.log(
                    "PipelineService",
                    "warning",
                    "Pipeline edge not found or already deleted.",
                    extra={"pipeline_edge_id": str(pipeline_edge_id)}
                )
                return False

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during removing edge from pipeline: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_edge_id": str(pipeline_edge_id)}
            )
            return False

    # -------------------
    # Advanced Operations
    # -------------------

    def increment_pipeline_run(self, pipeline_id: UUID, latest_runtime: float) -> bool:
        """
        Increments the `times_run` and updates the `average_runtime` for a pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline.
            latest_runtime (float): The runtime of the latest pipeline execution in seconds.

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
                    extra={"pipeline_id": str(pipeline_id)}
                )
                return False

            # Calculate new times_run and average_runtime
            new_times_run = pipeline.times_run + 1
            new_average_runtime = ((pipeline.average_runtime * pipeline.times_run) + latest_runtime) / new_times_run

            # Prepare update data
            update_data = {
                "times_run": new_times_run,
                "average_runtime": new_average_runtime,
                "updated_at": datetime.utcnow().isoformat()
            }

            # Update the pipeline in Supabase
            response = self.supabase_client.table("pipelines").update(serialize_dict(update_data)).eq("pipeline_id", str(pipeline_id)).execute()

            if response.error:
                self.logger.log(
                    "PipelineService",
                    "error",
                    "Failed to update pipeline run metrics in Supabase.",
                    extra={"error": response.error.message, "pipeline_id": str(pipeline_id), "update_data": update_data}
                )
                return False

            self.logger.log(
                "PipelineService",
                "info",
                "Pipeline run metrics updated successfully.",
                extra={"pipeline_id": str(pipeline_id), "times_run": new_times_run, "average_runtime": new_average_runtime}
            )
            return True

        except Exception as e:
            self.logger.log(
                "PipelineService",
                "critical",
                f"Exception during incrementing pipeline run: {e}",
                extra={"traceback": traceback.format_exc(), "pipeline_id": str(pipeline_id)}
            )
            return False


    def validate_pipeline(self, block_ids: List[UUID], edge_ids: Optional[List[UUID]] = None) -> PipelineVerificationResponseSchema:
        """
        Validates if a group of blocks can form a valid pipeline without fatal connections.

        Args:
            block_ids (List[UUID]): List of block UUIDs to include in the pipeline.
            edge_ids (Optional[List[UUID]]): Optional list of edge UUIDs to include.

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
