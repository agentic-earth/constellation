# app/controllers/block_controller.py

"""
Block Controller Module

This module defines the BlockController class responsible for managing block-related operations.
It orchestrates interactions between BlockService, TaxonomyService, and VectorEmbeddingService to
perform operations that involve blocks, taxonomy, and vector embeddings. Additionally, it handles
search functionalities based on taxonomy filters and vector similarity.

Responsibilities:
- Coordinating between BlockService, TaxonomyService, and VectorEmbeddingService to perform complex workflows.
- Handling CRUD operations for blocks, including optional taxonomy and vector embeddings.
- Managing similarity searches with optional taxonomy filters.
- Ensuring transactional integrity and robust error handling.
- Managing audit logs through AuditService.

Design Philosophy:
- Maintain high cohesion by focusing solely on block-related orchestration.
- Promote loose coupling by interacting with services through well-defined interfaces.
- Ensure robustness through comprehensive error handling and logging.
"""

import traceback
from typing import List, Optional, Dict, Any
from uuid import UUID
from prisma import Prisma
from backend.app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema,
    AuditLogCreateSchema,
    VectorRepresentationCreateSchema,
    VectorRepresentationResponseSchema,
    BlockTypeEnum
)

from backend.app.taxonomy import (
    PaperType, ApplicationArea, SpatialScale, TemporalScale, ApplicationReadiness,
    ModelType, Architecture, ModelCharacteristics, InputDataType, OutputDataType,
    SpatialResolution, TemporalResolution, SatelliteSource, ProcessingLevel,
    EarthObservationModelTaxonomy, WeatherClimateModelTaxonomy,
    DatasetTaxonomy, Taxonomy, GeneralTaxonomy
)


from backend.app.database import database
from backend.app.features.core.services.block_service import BlockService
from backend.app.features.core.services.taxonomy_service import TaxonomyService
from backend.app.features.core.services.vector_embedding_service import VectorEmbeddingService
from backend.app.features.core.services.audit_service import AuditService
import asyncio


class BlockController:
    """
    BlockController manages all block-related operations, including creating, retrieving, updating,
    deleting blocks, and performing similarity searches. It coordinates between BlockService,
    TaxonomyService, VectorEmbeddingService, and AuditService to ensure data integrity and
    transactional safety. All operations are handled asynchronously and are encapsulated within
    Prisma transactions to maintain ACID properties. In the event of any operation failure,
    the transaction is rolled back to prevent partial data instantiation.

    Responsibilities:
    - Create, retrieve, update, and delete blocks.
    - Manage taxonomy associations for blocks.
    - Perform similarity searches based on vector embeddings.
    - Handle audit logging for all block operations.
    - Ensure transactional safety and data consistency.
    """

    def __init__(self, prisma: Prisma):
        self.prisma = prisma
        self.block_service = BlockService(prisma)
        self.taxonomy_service = TaxonomyService(prisma)
        self.vector_embedding_service = VectorEmbeddingService(prisma)
        self.audit_service = AuditService(prisma)

    async def create_block(self, block_data: BlockCreateSchema, user_id: UUID) -> Optional[BlockResponseSchema]:
        """
        Creates a new block along with its taxonomy and vector embedding. All operations are performed
        within a transaction to ensure atomicity. If any step fails, the entire transaction is rolled back.

        Args:
            block_data (BlockCreateSchema): Data required to create the block.
            user_id (UUID): UUID of the user performing the creation.

        Returns:
            Optional[BlockResponseSchema]: The created block data if successful, None otherwise.
        """
        async with self.prisma.tx() as transaction:
            # Step 1: Create Block
            block = await self.block_service.create_block(block_data)
            if not block:
                return None  # Transaction will be rolled back

            # Step 2: Associate Taxonomy if provided
            if block_data.taxonomy:
                taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(block.block_id, block_data.taxonomy)
                if not taxonomy_success:
                    return None  # Transaction will be rolled back

            # Step 3: Create Vector Embedding if metadata provided
            if block_data.metadata and "vector" in block_data.metadata:
                vector_create_schema = VectorRepresentationCreateSchema(
                    entity_type="BLOCK",
                    entity_id=block.block_id,
                    vector=block_data.metadata["vector"],  # Ensure vector is part of metadata
                    taxonomy_filter=block_data.taxonomy
                )
                vector_embedding = await self.vector_embedding_service.create_vector_embedding(vector_create_schema)
                if not vector_embedding:
                    return None  # Transaction will be rolled back
                block.vector_embedding = vector_embedding

            # Step 4: Audit Logging
            audit_log = AuditLogCreateSchema(
                user_id=user_id,
                action_type="CREATE",
                entity_type="BLOCK",
                entity_id=block.block_id,
                details={"name": block.name, "block_type": block.block_type}
            )
            await self.audit_service.create_audit_log(audit_log)

            return block

    async def get_block_by_id(self, block_id: UUID, user_id: UUID) -> Optional[BlockResponseSchema]:
        """
        Retrieves a block by its UUID, including its taxonomy and vector embedding. Logs the retrieval action.

        Args:
            block_id (UUID): UUID of the block to retrieve.
            user_id (UUID): UUID of the user performing the retrieval.

        Returns:
            Optional[BlockResponseSchema]: The retrieved block data if found, None otherwise.
        """
        # Step 1: Retrieve Block
        block = await self.block_service.get_block_by_id(block_id)
        if not block:
            return None

        # Step 2: Retrieve Taxonomy
        taxonomy = await self.taxonomy_service.get_taxonomy_for_block(block_id)
        block.taxonomy = taxonomy

        # Step 3: Retrieve Vector Embedding
        vector_embedding = await self.vector_embedding_service.get_vector_embedding(block_id)
        block.vector_embedding = vector_embedding

        # Step 4: Audit Logging
        audit_log = AuditLogCreateSchema(
            user_id=user_id,
            action_type="READ",
            entity_type="BLOCK",
            entity_id=block.block_id,
            details={"name": block.name}
        )
        await self.audit_service.create_audit_log(audit_log)

        return block

    async def update_block(self, block_id: UUID, update_data: BlockUpdateSchema, user_id: UUID) -> Optional[BlockResponseSchema]:
        """
        Updates an existing block's details, taxonomy, and vector embedding. All operations are performed
        within a transaction to ensure atomicity. If any step fails, the entire transaction is rolled back.

        Args:
            block_id (UUID): UUID of the block to update.
            update_data (BlockUpdateSchema): Data to update the block.
            user_id (UUID): UUID of the user performing the update.

        Returns:
            Optional[BlockResponseSchema]: The updated block data if successful, None otherwise.
        """
        async with self.prisma.transaction():
            # Step 1: Update Block
            updated_block = await self.block_service.update_block(block_id, update_data)
            if not updated_block:
                return None  # Transaction will be rolled back

            # Step 2: Update Taxonomy if provided
            if update_data.taxonomy:
                taxonomy_success = await self.taxonomy_service.create_taxonomy_for_block(block_id, update_data.taxonomy)
                if not taxonomy_success:
                    return None  # Transaction will be rolled back

            # Step 3: Update Vector Embedding if metadata provided
            if update_data.metadata and "vector" in update_data.metadata:
                new_vector = update_data.metadata["vector"]
                taxonomy_filters = update_data.taxonomy
                vector_update_success = await self.vector_embedding_service.update_vector_embedding(
                    block_id=block_id,
                    new_vector=new_vector,
                    taxonomy_filters=taxonomy_filters
                )
                if not vector_update_success:
                    return None  # Transaction will be rolled back

            # Step 4: Audit Logging
            audit_log = AuditLogCreateSchema(
                user_id=user_id,
                action_type="UPDATE",
                entity_type="BLOCK",
                entity_id=block_id,
                details={"updated_fields": list(update_data.dict(exclude_unset=True).keys())}
            )
            await self.audit_service.create_audit_log(audit_log)

            return updated_block

    async def delete_block(self, block_id: UUID, user_id: UUID) -> bool:
        """
        Deletes a block along with its taxonomy and vector embedding. All operations are performed
        within a transaction to ensure atomicity. If any step fails, the entire transaction is rolled back.

        Args:
            block_id (UUID): UUID of the block to delete.
            user_id (UUID): UUID of the user performing the deletion.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        async with self.prisma.transaction():
            # Step 1: Delete Vector Embedding
            vector_deleted = await self.vector_embedding_service.delete_vector_embedding(block_id)
            if not vector_deleted:
                return False  # Transaction will be rolled back

            # Step 2: Delete Taxonomy Associations
            taxonomy_deleted = await self.taxonomy_service.associate_block_with_categories(block_id, [])
            if not taxonomy_deleted:
                return False  # Transaction will be rolled back

            # Step 3: Delete Block
            block_deleted = await self.block_service.delete_block(block_id)
            if not block_deleted:
                return False  # Transaction will be rolled back

            # Step 4: Audit Logging
            audit_log = AuditLogCreateSchema(
                user_id=user_id,
                action_type="DELETE",
                entity_type="BLOCK",
                entity_id=block_id,
                details={"block_id": str(block_id)}
            )
            await self.audit_service.create_audit_log(audit_log)

            return True

    async def perform_similarity_search(self, query_vector: List[float], top_k: int, user_id: UUID) -> Optional[List[BlockResponseSchema]]:
        """
        Performs a similarity search to find blocks similar to the provided query vector. Logs the search action.

        Args:
            query_vector (List[float]): The vector to compare against existing block vectors.
            top_k (int): Number of top similar blocks to retrieve.
            user_id (UUID): UUID of the user performing the search.

        Returns:
            Optional[List[BlockResponseSchema]]: List of similar blocks if successful, None otherwise.
        """
        # Step 1: Perform Similarity Search
        similar_blocks = await self.vector_embedding_service.search_similar_blocks(query_vector, top_k=top_k)
        if similar_blocks is None:
            return None  # Search failed

        # Step 2: Audit Logging
        audit_log = AuditLogCreateSchema(
            user_id=user_id,
            action_type="SEARCH",
            entity_type="BLOCK",
            entity_id=uuid4(),  # Assuming a unique UUID for the search action
            details={"search_vector": query_vector, "top_k": top_k}
        )
        await self.audit_service.create_audit_log(audit_log)

        return similar_blocks


# -------------------
# Testing Utility
# -------------------

async def main():
    """
    Main function to test the BlockController functionality with correct schemas and taxonomies.
    """
    print("Starting BlockController test...")
    await database.prisma.connect()
    print("Connected to database.")
    controller = BlockController(database.prisma)

    user_id = UUID('12345678-1234-5678-1234-567812345678')  # Example user ID
    print(f"Using test user ID: {user_id}")

    # Step 1: Create a new block (Earth Observation Model)
    print("\nStep 1: Creating a new Earth Observation Model block...")
    create_schema = BlockCreateSchema(
        name="EarthObservationModelExample",
        block_type=BlockTypeEnum.MODEL,
        description="An example Earth Observation model for testing.",
        created_by=user_id,
        taxonomy=Taxonomy(
            general=GeneralTaxonomy(
                paper_id="paper123",
                paper_type=PaperType.EARTH_OBSERVATION,
                application_areas=[ApplicationArea.AGRICULTURE_FOOD_SECURITY, ApplicationArea.CLIMATE_ATMOSPHERIC_SCIENCE],
                keywords=["remote sensing", "machine learning"],
                spatial_scale=SpatialScale.REGIONAL,
                temporal_scale=TemporalScale.ANNUAL,
                application_readiness=ApplicationReadiness.PROTOTYPE
            ),
            specific=EarthObservationModelTaxonomy(
                paper_id="paper123",
                paper_type=PaperType.EARTH_OBSERVATION,
                application_areas=[ApplicationArea.AGRICULTURE_FOOD_SECURITY, ApplicationArea.CLIMATE_ATMOSPHERIC_SCIENCE],
                keywords=["remote sensing", "machine learning"],
                spatial_scale=SpatialScale.REGIONAL,
                temporal_scale=TemporalScale.ANNUAL,
                application_readiness=ApplicationReadiness.PROTOTYPE,
                model_type=ModelType.VISION,
                architecture=Architecture.CNN,
                model_characteristics=ModelCharacteristics(
                    is_stochastic=False,
                    is_deterministic=True,
                    is_multi_modal=False,
                    is_foundation_model=False,
                    is_physics_informed=False
                ),
                input_data_types=[InputDataType.OPTICAL, InputDataType.THERMAL],
                output_data_type=OutputDataType.CLASSIFICATION,
                spatial_resolution=SpatialResolution.MEDIUM_HIGH,
                temporal_resolution=TemporalResolution.ANNUAL,
                satellite_data_sources=[SatelliteSource.SENTINEL_2, SatelliteSource.LANDSAT_1],
                processing_level=ProcessingLevel.LEVEL_1
            )
        ),
        metadata={
            "vector": [0.1] * 512  # Example 512-dimensional vector
        }
    )
    created_block = await controller.create_block(create_schema, user_id)
    if created_block:
        print(f"Block Created: {created_block.block_id}")
    else:
        print("Block creation failed.")

    # Step 2: Retrieve the created block
    if created_block:
        print("\nStep 2: Retrieving the created block...")
        retrieved_block = await controller.get_block_by_id(created_block.block_id, user_id)
        if retrieved_block:
            print(f"Block Retrieved: {retrieved_block.block_id}, Name: {retrieved_block.name}")
            print(f"Taxonomy: {retrieved_block.taxonomy}")
        else:
            print("Block retrieval failed.")

    # Step 3: Update the block's name and taxonomy (to Weather/Climate Model)
    if created_block:
        print("\nStep 3: Updating the block to a Weather/Climate Model...")
        update_schema = BlockUpdateSchema(
            name="UpdatedWeatherClimateModelExample",
            taxonomy=Taxonomy(
                general=GeneralTaxonomy(
                    paper_id="paper123",
                    paper_type=PaperType.WEATHER_CLIMATE,
                    application_areas=[ApplicationArea.WEATHER_FORECASTING, ApplicationArea.CLIMATE_MODELING],
                    keywords=["climate", "forecasting"],
                    spatial_scale=SpatialScale.GLOBAL,
                    temporal_scale=TemporalScale.DECADAL,
                    application_readiness=ApplicationReadiness.OPERATIONAL
                ),
                specific=WeatherClimateModelTaxonomy(
                    paper_id="paper123",
                    model_type=ModelType.PHYSICS_BASED,
                    architecture=Architecture.GCM,
                    model_characteristics=ModelCharacteristics(
                        is_stochastic=True,
                        is_deterministic=False,
                        is_multi_modal=True,
                        is_foundation_model=False,
                        is_physics_informed=True
                    ),
                    input_data_types=[InputDataType.REANALYSIS, InputDataType.WEATHER_STATION],
                    output_data_type=OutputDataType.TIME_SERIES,
                    spatial_resolution=SpatialResolution.COARSE,
                    temporal_resolution=TemporalResolution.HOURLY,
                    climate_weather_data_sources=[ClimateWeatherDataSource.ERA5, ClimateWeatherDataSource.GHCN]
                )
            ),
            metadata={
                "vector": [0.2] * 512
            },
            updated_by=user_id
        )
        updated_block = await controller.update_block(created_block.block_id, update_schema, user_id)
        if updated_block:
            print(f"Block Updated: {updated_block.block_id}, New Name: {updated_block.name}")
            print(f"Updated Taxonomy: {updated_block.taxonomy}")
        else:
            print("Block update failed.")

    # Step 4: Perform a similarity search
    print("\nStep 4: Performing a similarity search...")
    search_vector = [0.2] * 512
    top_k = 5
    similar_blocks = await controller.perform_similarity_search(search_vector, top_k, user_id)
    if similar_blocks:
        print(f"Similarity Search Results (Top {top_k}):")
        for blk in similar_blocks:
            print(f"- Block ID: {blk.block_id}, Name: {blk.name}")
    else:
        print("Similarity search failed or no similar blocks found.")

    # Step 5: Delete the block
    if created_block:
        print("\nStep 5: Deleting the created block...")
        deletion_success = await controller.delete_block(created_block.block_id, user_id)
        if deletion_success:
            print(f"Block Deleted: {created_block.block_id}")
        else:
            print("Block deletion failed.")

    print("\nDisconnecting from database...")
    await database.prisma.disconnect()
    print("Test completed.")

if __name__ == "__main__":
    import os
    print(f"Database URL: {os.getenv('DATABASE_URL')}")
    asyncio.run(main())