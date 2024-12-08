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
from backend.app.features.core.services.user_service import UserService
from backend.app.logger import ConstellationLogger
from prisma import Prisma
import asyncio
from collections import defaultdict
import requests

from dagster.orchestrator.app.main import run_dagster_job_with_config


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
        # self.user_service = UserService(self.prisma)
        self.logger = ConstellationLogger()

    # -------------------
    # Pipeline CRUD Operations
    # -------------------

    async def create_pipeline(
        self, pipeline_data: Dict[str, Any], user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a new pipeline.

        Args:
            pipeline_data (Dict[str, Any]): The data required to create a new pipeline.
                Expected keys:
                    -'name': str
                    -'description': str
                    -'user_id': UUID
            user_id (UUID): The UUID of the user creating the pipeline.

        Returns:
            Dict[str, Any]: The created pipeline data if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # TODO: Ensure user exists
                # user = await self.user_service.get_profile_by_user_id(user_id)
                # if not user:
                #     raise ValueError("User not found.")

                # Create the pipeline using the PipelineService
                pipeline = await self.pipeline_service.create_pipeline(
                    tx, pipeline_data
                )
                if not pipeline:
                    raise ValueError("Failed to create pipeline.")

                # Log the creation in Audit Logs
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "CREATE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": {
                        "pipeline_name": pipeline.name,
                    },
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for pipeline creation")

                # Log the creation event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline created successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline.dict()

        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline creation: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            return None

    async def get_pipeline_by_id(
        self, pipeline_id: UUID, user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves a pipeline by its unique identifier.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to retrieve.
            user_id (UUID): The UUID of the user retrieving the pipeline.
        Returns:
            Dict[str, Any]: The pipeline data if found, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Retrieve the pipeline using the PipelineService
                pipeline = await self.pipeline_service.get_pipeline_by_id(
                    tx, pipeline_id
                )
                if not pipeline:
                    raise ValueError("Pipeline not found.")

                # Log the successful retrieval in Audit Logs
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "READ",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": {
                        "pipeline_name": pipeline.name,
                    },
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for pipeline retrieval")

                # Log the retrieval event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline retrieved successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline.dict()

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
            return None

    async def update_pipeline(
        self, pipeline_id: UUID, update_data: Dict[str, Any], user_id: UUID
    ) -> Dict[str, Any]:
        """
        Updates an existing pipeline's information.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to update.
            update_data (Dict[str, Any]): The data to update for the pipeline.
                Expected keys:
                    - 'name': str
                    - 'description': str
            user_id (UUID): The UUID of the user updating the pipeline.

        Returns:
            Dict[str, Any]: The updated pipeline data if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Update the pipeline using the PipelineService
                pipeline = await self.pipeline_service.update_pipeline(
                    tx, pipeline_id, update_data
                )
                if not pipeline:
                    raise ValueError("Failed to update pipeline.")

                # Log the update in Audit Logs
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "UPDATE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": {
                        "pipeline_name": pipeline.name,
                        "updated_fields": list(update_data.keys()),
                    },
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for pipeline update")

                # Log the update event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline updated successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline.dict()

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
            return None

    async def delete_pipeline(self, pipeline_id: UUID, user_id: UUID) -> bool:
        """
        Deletes a pipeline.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.
            user_id (UUID): The UUID of the user deleting the pipeline.
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Delete the pipeline using the PipelineService
                deletion_success = await self.pipeline_service.delete_pipeline(
                    tx, pipeline_id
                )
                if not deletion_success:
                    raise ValueError("Failed to delete pipeline.")

                # Log the deletion in Audit Logs
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "DELETE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline_id),
                    "details": {
                        "pipeline_id": str(pipeline_id),
                    },
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception("Failed to create audit log for pipeline deletion")

                # Log the deletion event
                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline deleted successfully.",
                    extra={"pipeline_id": str(pipeline_id)},
                )
                return True

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
            return False

    async def list_pipelines(
        self,
        user_id: UUID,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Lists pipelines with optional filtering and pagination.

        Args:
            user_id (UUID): The UUID of the user listing the pipelines.
            filters (Optional[Dict[str, Any]]): Key-value pairs to filter the pipelines.
                Supported filters: 'name', 'user_id'.
            limit (int): The maximum number of pipelines to return.
            offset (int): The number of pipelines to skip before returning the results.

        Returns:
            List[Dict[str, Any]]: A list of pipelines if successful, empty list otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # List pipelines using the PipelineService
                pipelines = await self.pipeline_service.list_pipelines(
                    tx, filters, limit, offset
                )

                if pipelines:
                    # Log the listing in Audit Logs
                    audit_log = {
                        "user_id": str(user_id),
                        "action_type": "READ",
                        "entity_type": "pipeline",
                        "entity_id": str(
                            pipelines[0].pipeline_id
                        ),  # TODO: temporarily use first pipeline id
                        "details": {
                            "filters": filters,
                        },
                    }
                    audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                    if not audit_log:
                        raise Exception(
                            "Failed to create audit log for pipeline listing"
                        )

                    # Log the listing event
                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Listed {len(pipelines)} pipelines successfully.",
                        extra={"filters": filters},
                    )
                    return [pipeline.dict() for pipeline in pipelines]
                else:
                    self.logger.log(
                        "PipelineController",
                        "info",
                        "No pipelines found.",
                        filters=filters,
                        limit=limit,
                        offset=offset,
                    )
                    return []

        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline listing: {str(e)}",
                extra={"traceback": traceback.format_exc(), "filters": filters},
            )
            return []

    # -------------------
    # Advanced Pipeline Operations
    # -------------------

    async def create_pipeline_with_dependencies(
        self,
        pipeline_data: Dict[str, Any],
        blocks: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        user_id: UUID,
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a pipeline along with its associated blocks and edges.

        Args:
            pipeline_data (Dict[str, Any]): Data to create the pipeline.
            blocks (List[Dict[str, Any]]): List of blocks to assign to the pipeline.
            edges (List[Dict[str, Any]]): List of edges to assign to the pipeline.
            user_id (UUID): The UUID of the user creating the pipeline.

        Returns:
            Optional[Dict[str, Any]]: The created pipeline data if successful, None otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Create the pipeline
                pipeline = await self.pipeline_service.create_pipeline(
                    tx, pipeline_data
                )
                if not pipeline:
                    raise ValueError("Failed to create pipeline.")

                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline created successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )

                # Assign blocks to the pipeline
                for block_data in blocks:
                    assigned_block = await self.block_service.get_block_by_name(
                        tx, block_data["name"]
                    )
                    if not assigned_block:
                        assigned_block = await self.block_service.create_block(
                            tx, block_data
                        )

                    if not assigned_block:
                        raise ValueError(
                            f"Failed to retrieve or create block: {block_data['name']}"
                        )

                    # Assign the block to the pipeline
                    assigned_pipeline_block = (
                        await self.pipeline_service.assign_block_to_pipeline(
                            tx, assigned_block.block_id, pipeline.pipeline_id
                        )
                    )
                    if not assigned_pipeline_block:
                        raise ValueError(
                            f"Failed to assign block {assigned_block.block_id} to pipeline."
                        )

                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Block {assigned_block.block_id} assigned to pipeline {pipeline.pipeline_id}.",
                    )

                # Assign edges to the pipeline
                for edge_data in edges:
                    # allow multiple edges between same two blocks
                    assigned_edge = await self.edge_service.create_edge(tx, edge_data)
                    if not assigned_edge:
                        raise ValueError(f"Failed to create edge: {edge_data}")

                    # Assign the edge to the pipeline
                    assigned_pipeline_edge = (
                        await self.pipeline_service.assign_edge_to_pipeline(
                            tx, assigned_edge.edge_id, pipeline.pipeline_id
                        )
                    )
                    if not assigned_pipeline_edge:
                        raise ValueError(
                            f"Failed to assign edge {edge_data['edge_id']} to pipeline."
                        )

                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Edge {assigned_edge.edge_id} assigned to pipeline {pipeline.pipeline_id}.",
                    )

                # Log the creation in Audit Logs
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "CREATE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline.pipeline_id),
                    "details": {
                        "pipeline_name": pipeline.name,
                        "blocks": len(blocks),
                        "edges": len(edges),
                    },
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception(
                        "Failed to create audit log for pipeline creation with dependencies"
                    )

                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline and dependencies created successfully.",
                    extra={"pipeline_id": str(pipeline.pipeline_id)},
                )
                return pipeline.dict()

        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during creating pipeline with dependencies: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            return None

    async def delete_pipeline_with_dependencies(
        self, pipeline_id: UUID, user_id: UUID
    ) -> bool:
        """
        Deletes a pipeline along with all its associated blocks and edges.

        Args:
            pipeline_id (UUID): The UUID of the pipeline to delete.
            user_id (UUID): The UUID of the user deleting the pipeline.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Retrieve all blocks associated with the pipeline
                pipeline_blocks = await self.pipeline_service.get_pipeline_blocks(
                    tx, pipeline_id
                )
                if pipeline_blocks is None:
                    raise ValueError("Failed to retrieve pipeline blocks.")

                # Retrieve all edges associated with the pipeline
                pipeline_edges = await self.pipeline_service.get_pipeline_edges(
                    tx, pipeline_id
                )
                if pipeline_edges is None:
                    raise ValueError("Failed to retrieve pipeline edges.")

                # Delete all edges first to maintain referential integrity
                for edge in pipeline_edges:
                    success = await self.pipeline_service.remove_edge_from_pipeline(
                        tx, edge.pipeline_edge_id
                    )
                    if not success:
                        raise ValueError(
                            f"Failed to delete edge {edge.pipeline_edge_id} from pipeline."
                        )

                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Pipeline edge {edge.pipeline_edge_id} deleted successfully.",
                    )

                    # Optionally, delete the edge entity itself
                    success = await self.edge_service.delete_edge(tx, edge.edge_id)
                    if not success:
                        raise ValueError(f"Failed to delete edge {edge.edge_id}.")

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
                        raise ValueError(
                            f"Failed to delete block {block.pipeline_block_id} from pipeline."
                        )

                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Pipeline block {block.pipeline_block_id} deleted successfully.",
                    )

                    # Optionally, delete the block entity itself
                    success = await self.block_service.delete_block(tx, block.block_id)
                    if not success:
                        raise ValueError(f"Failed to delete block {block.block_id}.")

                    self.logger.log(
                        "PipelineController",
                        "info",
                        f"Block {block.block_id} deleted successfully.",
                    )

                # Finally, delete the pipeline
                success = await self.pipeline_service.delete_pipeline(tx, pipeline_id)
                if not success:
                    raise ValueError(f"Failed to delete pipeline {pipeline_id}.")

                # Log the deletion in Audit Logs
                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "DELETE",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline_id),
                    "details": {
                        "description": "All blocks and edges associated with pipeline deleted.",
                        "blocks": len(pipeline_blocks),
                        "edges": len(pipeline_edges),
                    },
                }
                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception(
                        "Failed to create audit log for pipeline deletion with dependencies"
                    )

                # Log the deletion event
                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Pipeline {pipeline_id} and all associated blocks and edges deleted successfully.",
                    extra={"pipeline_id": str(pipeline_id)},
                )
                return True

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
            return False

    async def verify_pipeline(self, pipeline_id, user_id: UUID) -> bool:
        """
        Verifies if a group of blocks can form a valid pipeline.
        Goal: Check if the pipeline is a connected DAG
            - Check if no cycles exist in the graph
            - Check if all blocks are connected

        Args:
            pipeline_id (UUID): The UUID of the pipeline to verify.
            user_id (UUID): The UUID of the user verifying the pipeline.

        Returns:
            bool: True if the pipeline is valid, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                pipeline_edges = await self.pipeline_service.get_pipeline_edges(
                    tx, pipeline_id
                )
                if pipeline_edges is None:
                    raise ValueError("Failed to retrieve pipeline edges.")

                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline edges retrieved successfully.",
                    pipeline_id=str(pipeline_id),
                    edges_found=len(pipeline_edges),
                )

                # 1. check if no cycles exist in the graph
                edge_ids = [edge.edge_id for edge in pipeline_edges]
                verified_edges = await self.edge_service.verify_edges(tx, edge_ids)
                if not verified_edges:
                    raise ValueError("Edges are not valid to form a pipeline.")

                # 2. check if all blocks are connected
                graph = defaultdict(list)
                for edge in pipeline_edges:
                    edge = await self.edge_service.get_edge_by_id(tx, edge.edge_id)
                    if not edge:
                        raise ValueError(f"Edge {edge.edge_id} not found.")

                    graph[edge.source_block_id].append(edge.target_block_id)

                def connected_blocks(graph: Dict[UUID, List[UUID]]) -> bool:
                    """
                    Check if all blocks are connected using DFS.
                    """
                    visited = set()
                    stack = set()

                    def dfs(node: UUID):
                        visited.add(node)
                        stack.add(node)
                        for neighbor in graph[node]:
                            if neighbor not in visited:
                                dfs(neighbor)

                    dfs(next(iter(graph)))
                    return len(visited) == len(graph)

                if not connected_blocks(graph):
                    raise ValueError("Blocks are not connected.")

                audit_log = {
                    "user_id": str(user_id),
                    "action_type": "READ",
                    "entity_type": "pipeline",
                    "entity_id": str(pipeline_id),
                    "details": {
                        "description": "Pipeline is valid.",
                    },
                }

                audit_log = await self.audit_service.create_audit_log(tx, audit_log)
                if not audit_log:
                    raise Exception(
                        "Failed to create audit log for pipeline verification"
                    )

                self.logger.log(
                    "PipelineController",
                    "info",
                    "Pipeline is valid.",
                    pipeline_id=str(pipeline_id),
                )

                return True

        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline validation: {str(e)}",
                extra={"traceback": traceback.format_exc()},
            )
            return False
    
    async def update_pipeline_status_by_run_id(self, run_id: UUID, status: str) -> bool:
        """
        Updates the status of a pipeline based on its run ID.

        Args:
            run_id (UUID): The run ID of the pipeline to update.
            status (str): The new status to set for the pipeline.

        Returns:
            bool: True if the status update is successful, False otherwise.
        """
        try:
            async with self.prisma.tx() as tx:
                # Retrieve the pipeline using the run_id
                pipeline = await self.pipeline_service.get_pipeline_by_run_id(tx, run_id)
                if not pipeline:
                    raise ValueError(f"Pipeline with run_id {run_id} not found.")

                # Update the pipeline status
                update_success = await self.pipeline_service.update_pipeline_status(
                    tx, pipeline.pipeline_id, status
                )
                if not update_success:
                    raise ValueError("Failed to update pipeline status.")

                # Log the update event
                self.logger.log(
                    "PipelineController",
                    "info",
                    f"Pipeline status updated successfully.",
                    extra={
                        "run_id": str(run_id),
                        "pipeline_id": str(pipeline.pipeline_id),
                        "status": status,
                    },
                )
                return True

        except Exception as e:
            # Log unexpected exceptions with critical level
            self.logger.log(
                "PipelineController",
                "critical",
                f"Exception during pipeline status update: {str(e)}",
                extra={
                    "traceback": traceback.format_exc(),
                    "run_id": str(run_id),
                    "status": status,
                },
            )
            return False
        
    async def run_pipeline(self, config: str, user_id: UUID) -> bool:
        """
        Runs a pipeline with the given config.
        """
        # Based on the config, store the pipeline in the database
        pipeline_data = {
            "user_id": str(user_id),
        }
        pipeline = await self.pipeline_service.create_pipeline(self.prisma, pipeline_data)

        try:
            print(f"config: {config}")
            response = requests.post(
                "http://dagster_api:8001/execute", json={"instructions": config}
            )

            response = response.json()
            print(f"response: {response}")

            if response["status"] == "success":
                run_id = response["run_id"]
                async with self.prisma.tx() as tx:
                    # assign the run_id to the pipeline
                    self.pipeline_service.update_pipeline(tx, pipeline.pipeline_id, {"run_id": run_id})
                    # change the pipeline status to running
                    self.pipeline_service.update_pipeline_status_by_run_id(tx, run_id, "running")
                
                return True

            elif response["status"] == "failure":
                # delete the pipeline
                delete_result = await self.delete_pipeline(pipeline.pipeline_id)
                if not delete_result:
                    raise Exception("Failed to delete pipeline.")
                
                return False


        except HTTPException as e:
            raise e

    async def main(self):
        from backend.app.features.core.services.block_service import BlockService
        from backend.app.features.core.services.edge_service import EdgeService

        block_service = BlockService()
        edge_service = EdgeService()
        user_id = UUID("123e4567-e89b-12d3-a456-426614174000")

        try:
            # 1. Setup: create a pipeline with 3 blocks and 2 edges
            blocks = [
                {
                    "name": "Test Block 1",
                    "block_type": "dataset",
                    "description": "Test Block 1 Description",
                },
                {
                    "name": "Test Block 2",
                    "block_type": "model",
                    "description": "Test Block 2 Description",
                },
                {
                    "name": "Test Block 3",
                    "block_type": "dataset",
                    "description": "Test Block 3 Description",
                },
            ]
            created_blocks = []
            for block in blocks:
                created_block = await block_service.create_block(self.prisma, block)
                if not created_block:
                    raise Exception("Failed to create block.")
                created_blocks.append(created_block.dict())
                print("Created block: ", created_block.block_id)

            edges = [
                {
                    "source_block_id": created_blocks[0]["block_id"],
                    "target_block_id": created_blocks[1]["block_id"],
                },
                {
                    "source_block_id": created_blocks[1]["block_id"],
                    "target_block_id": created_blocks[2]["block_id"],
                },
            ]
            print("Edges to add: ", edges)

            pipeline_data = {"user_id": user_id, "name": "Test Pipeline"}

            # 2. Create pipeline with dependencies
            print("\nCreating pipeline with dependencies...")
            pipeline = await self.create_pipeline_with_dependencies(
                pipeline_data, blocks, edges, user_id
            )
            if pipeline:
                print("Pipeline created successfully.")
            else:
                raise Exception("Failed to create pipeline.")

            # 3. test get pipeline by id
            print("\nGetting pipeline by id...")
            pipeline = await self.get_pipeline_by_id(pipeline["pipeline_id"], user_id)
            if pipeline:
                print("Pipeline retrieved successfully.")
            else:
                raise Exception("Failed to retrieve pipeline.")

            # 4. test update pipeline
            print("\nUpdating pipeline...")
            pipeline = await self.update_pipeline(
                pipeline["pipeline_id"], {"name": "Updated Test Pipeline"}, user_id
            )
            if pipeline:
                print("Pipeline updated successfully.")
            else:
                raise Exception("Failed to update pipeline.")

            # 5. verify pipeline
            print("\nVerifying pipeline...")
            expected = True
            is_valid = await self.verify_pipeline(pipeline["pipeline_id"], user_id)
            if is_valid == expected:
                print("Pipeline is valid.")
            else:
                raise Exception("Pipeline is not valid. Expected it to be valid.")

            # 6. add an edge that creates a cycle
            print("\nAdding an edge to the pipeline that creates a cycle...")
            edge = await edge_service.create_edge(
                self.prisma,
                {
                    "source_block_id": created_blocks[2]["block_id"],
                    "target_block_id": created_blocks[0]["block_id"],
                },
            )
            if edge:
                print("Edge created successfully.")
            else:
                raise Exception("Failed to create edge.")

            pipeline_edge = await self.pipeline_service.assign_edge_to_pipeline(
                self.prisma, edge.edge_id, pipeline["pipeline_id"]
            )
            if pipeline_edge:
                print("Edge assigned to pipeline successfully.")
            else:
                raise Exception("Failed to assign edge to pipeline.")

            # 7. verify pipeline
            print("\nVerifying pipeline...")
            expected = False
            is_valid = await self.verify_pipeline(pipeline["pipeline_id"], user_id)
            if is_valid == expected:
                print("Pipeline is not valid.")
            else:
                raise Exception("Pipeline is valid. Expected it to be invalid.")

            # 8. delete pipeline with dependencies
            print("\nDeleting pipeline with dependencies...")
            success = await self.delete_pipeline_with_dependencies(
                pipeline["pipeline_id"], user_id
            )
            if success:
                print("Pipeline deleted successfully.")
            else:
                raise Exception("Failed to delete pipeline.")

            print("\nPipeline tests completed successfully.")
        except Exception as e:
            print(f"Exception: {str(e)}")
        finally:
            print("Disconnecting from the database...")
            await self.prisma.disconnect()
            print("Disconnected from the database.")


if __name__ == "__main__":

    async def run_pipeline_controller_tests():
        """
        Function to run PipelineController tests.
        """
        prisma = Prisma()
        print("Connecting to the database...")
        await prisma.connect()
        print("Database connected.")

        pipeline_controller = PipelineController(prisma)
        await pipeline_controller.main()

    asyncio.run(run_pipeline_controller_tests())
