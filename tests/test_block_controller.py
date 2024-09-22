# tests/test_block_controller.py

"""
Test Suite for BlockController

This test suite extensively tests the BlockController's CRUD operations for blocks,
handling of taxonomies, management of vector embeddings, and execution of vector similarity searches.
Each test case includes detailed print statements to trace the computation and internal states.
"""

import pytest
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4
from typing import List, Dict, Any
from pydantic import ValidationError
from datetime import datetime
from fastapi import HTTPException, status

# Import the BlockController and relevant schemas
from app.controllers.block_controller import BlockController
from app.schemas import (
    BlockCreateSchema,
    BlockUpdateSchema,
    BlockResponseSchema,
    VectorRepresentationSchema,
    VectorRepresentationCreateSchema,
    VectorRepresentationResponseSchema,
    AuditLogCreateSchema,
)

from app.taxonomy import SearchQuery, SearchResult

# -------------------
# Fixtures for Mocking Services
# -------------------

@pytest.fixture
def mock_block_service():
    with patch('app.controllers.block_controller.BlockService') as MockBlockService:
        instance = MockBlockService.return_value
        # Mock methods
        instance.create_block = MagicMock()
        instance.get_block_by_id = MagicMock()
        instance.update_block = MagicMock()
        instance.delete_block = MagicMock()
        yield instance

@pytest.fixture
def mock_taxonomy_service():
    with patch('app.controllers.block_controller.TaxonomyService') as MockTaxonomyService:
        instance = MockTaxonomyService.return_value
        # Mock methods
        instance.create_taxonomy_for_block = MagicMock()
        instance.get_taxonomy_for_block = MagicMock()
        instance.delete_taxonomy_for_block = MagicMock()
        yield instance

@pytest.fixture
def mock_vector_embedding_service():
    with patch('app.controllers.block_controller.VectorEmbeddingService') as MockVectorEmbeddingService:
        instance = MockVectorEmbeddingService.return_value
        # Mock methods
        instance.create_vector_embedding = MagicMock()
        instance.get_vector_embedding = MagicMock()
        instance.update_vector_embedding = MagicMock()
        instance.delete_vector_embedding = MagicMock()
        instance.search_similar_blocks = MagicMock()
        yield instance

@pytest.fixture
def mock_audit_service():
    with patch('app.controllers.block_controller.AuditService') as MockAuditService:
        instance = MockAuditService.return_value
        # Mock methods
        instance.create_audit_log = MagicMock()
        yield instance

@pytest.fixture
def mock_logger():
    with patch('app.controllers.block_controller.ConstellationLogger') as MockLogger:
        instance = MockLogger.return_value
        # Mock the log method
        instance.log = MagicMock()
        yield instance

@pytest.fixture
def block_controller(mock_block_service, mock_taxonomy_service, mock_vector_embedding_service, mock_audit_service, mock_logger):
    """
    Fixture to instantiate the BlockController with mocked services.
    """
    controller = BlockController()
    controller.block_service = mock_block_service
    controller.taxonomy_service = mock_taxonomy_service
    controller.vector_embedding_service = mock_vector_embedding_service
    controller.audit_service = mock_audit_service
    controller.logger = mock_logger
    return controller

# -------------------
# Helper Functions
# -------------------

def generate_uuid() -> UUID:
    return uuid4()

def create_sample_block_create_schema() -> BlockCreateSchema:
    """
    Creates a sample BlockCreateSchema with mock data.
    """
    print("Creating sample BlockCreateSchema...")
    return BlockCreateSchema(
        name="Sample Block",
        block_type="dataset",  # Assuming 'dataset' is a valid BlockTypeEnum
        description="This is a sample block for testing.",
        created_by=generate_uuid()
    )

def create_sample_block_update_schema() -> BlockUpdateSchema:
    """
    Creates a sample BlockUpdateSchema with mock data.
    """
    print("Creating sample BlockUpdateSchema...")
    return BlockUpdateSchema(
        name="Updated Sample Block",
        block_type="model",  # Assuming 'model' is another valid BlockTypeEnum
        description="This is an updated sample block for testing."
    )

def create_sample_block_response(block_id: UUID, name="Sample Block", block_type="dataset", description="This is a sample block for testing.") -> BlockResponseSchema:
    print("Creating sample BlockResponseSchema...")
    return BlockResponseSchema(
        block_id=block_id,
        name=name,
        block_type=block_type,
        description=description,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-02T00:00:00Z",
        current_version_id=generate_uuid(),
        
        taxonomy={"category": "Test Category"},
        vector_embedding=VectorRepresentationSchema(
            vector_id=generate_uuid(),
            entity_type="block",
            entity_id=block_id,
            vector=[0.1, 0.2, 0.3],
            taxonomy_filter={"category": "Test Category"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z"
        )
    )

def create_sample_vector_representation(block_id: UUID, vector: List[float]) -> VectorRepresentationSchema:
    """
    Creates a sample VectorRepresentationSchema with mock data.
    """
    print("Creating sample VectorRepresentationSchema...")
    return VectorRepresentationSchema(
        vector_id=generate_uuid(),
        entity_type="block",
        entity_id=block_id,
        vector=vector,
        taxonomy_filter={"category": "Test Category"},
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-02T00:00:00Z"
    )

def create_sample_audit_log_create_schema(action_type: str, entity_type: str, entity_id: UUID, user_id: UUID = None, details: Dict[str, Any] = None) -> AuditLogCreateSchema:
    """
    Creates a sample AuditLogCreateSchema with mock data.
    """
    print("Creating sample AuditLogCreateSchema...")
    return AuditLogCreateSchema(
        user_id=user_id if user_id else generate_uuid(),
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details if details else {}
    )

def create_sample_block_create_schema_with_creator() -> BlockCreateSchema:
    creator_id = generate_uuid()
    return BlockCreateSchema(
        name="Sample Block",
        block_type="dataset",
        description="This is a sample block for testing.",
        created_by=creator_id,
        taxonomy=None,
        metadata=None
    )

def create_sample_block_response_with_creator(block_id: UUID, creator_id: UUID) -> BlockResponseSchema:
    return BlockResponseSchema(
        block_id=block_id,
        name="Sample Block",
        block_type="dataset",
        description="This is a sample block for testing.",
        created_by=creator_id,
        # Add other required fields here
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

def create_sample_taxonomy():
    return {
        "category": "Test Category",
        "subcategory": "Test Subcategory",
        "tags": ["test", "sample"]
    }

def create_sample_block_create_schema_with_creator_and_taxonomy() -> BlockCreateSchema:
    creator_id = generate_uuid()
    return BlockCreateSchema(
        name="Sample Block",
        block_type="dataset",
        description="This is a sample block for testing.",
        created_by=creator_id,
        taxonomy=create_sample_taxonomy(),
        metadata={"key": "value"}
    )

def create_sample_block_response_with_creator_and_taxonomy(block_id: UUID, creator_id: UUID) -> BlockResponseSchema:
    return BlockResponseSchema(
        block_id=block_id,
        name="Sample Block",
        block_type="dataset",
        description="This is a sample block for testing.",
        created_by=creator_id,
        taxonomy=create_sample_taxonomy(),
        metadata={"key": "value"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        current_version_id=generate_uuid(),
        vector_embedding=create_sample_vector_representation(block_id, [0.1, 0.2, 0.3])
    )

def create_sample_vector_representation(block_id: UUID, vector: List[float]) -> VectorRepresentationSchema:
    return VectorRepresentationSchema(
        vector_id=generate_uuid(),
        entity_type="block",
        entity_id=block_id,
        vector=vector,
        taxonomy_filter=create_sample_taxonomy(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )



def create_multiple_sample_blocks(controller: BlockController, num_blocks: int) -> List[BlockResponseSchema]:
    """
    Creates multiple sample blocks with varying attributes and taxonomy for testing.

    Args:
        controller (BlockController): The BlockController instance.
        num_blocks (int): Number of blocks to create.

    Returns:
        List[BlockResponseSchema]: List of created block responses.
    """
    blocks = []
    for i in range(1, num_blocks + 1):
        block_id = generate_uuid()
        creator_id = generate_uuid()
        taxonomy = {
            "category": f"Category {i % 3}",  # Categories: Category 0, 1, 2
            "subcategory": f"Subcategory {i % 2}",  # Subcategories: Subcategory 0, 1
            "tags": ["test", f"sample_{i}"]
        }
        block_create_data = BlockCreateSchema(
            name=f"Sample Block {i}",
            block_type="dataset" if i % 2 == 0 else "model",
            description=f"This is sample block number {i}.",
            created_by=creator_id,
            taxonomy=taxonomy,
            metadata={"key": f"value_{i}"}
        )
        sample_block = create_sample_block_response_with_creator_and_taxonomy(block_id, creator_id)
        sample_block.taxonomy = taxonomy
        mock_block_service = MagicMock()
        mock_taxonomy_service = MagicMock()
        mock_vector_embedding_service = MagicMock()
        mock_audit_service = MagicMock()
        mock_logger = MagicMock()

        # Mock service methods
        mock_block_service.create_block.return_value = sample_block
        mock_taxonomy_service.create_taxonomy_for_block.return_value = True
        mock_vector_embedding_service.create_vector_embedding.return_value = create_sample_vector_representation(
            block_id, [0.1 * i, 0.2 * i, 0.3 * i]
        )

        # Assign mocks to controller
        controller.block_service = mock_block_service
        controller.taxonomy_service = mock_taxonomy_service
        controller.vector_embedding_service = mock_vector_embedding_service
        controller.audit_service = mock_audit_service
        controller.logger = mock_logger

        # Create block
        block = controller.create_block(block_create_data)
        blocks.append(block)

    return blocks


# -------------------
# Test Cases
# -------------------

class TestBlockController:
    """
    Test class for BlockController covering CRUD operations, taxonomy management,
    vector embedding management, and similarity search.
    """

    def test_search_blocks_by_keywords(self, block_controller, mock_vector_embedding_service, 
                                    mock_audit_service, mock_logger):
        """
        Test searching blocks by keywords present in their name and description.
        """
        print("\n--- Starting test_search_blocks_by_keywords ---")
        # Arrange
        keyword = "Sample"
        top_k = 5

        # Create sample blocks
        num_blocks = 5
        blocks = []
        for i in range(1, num_blocks + 1):
            block_id = generate_uuid()
            creator_id = generate_uuid()
            taxonomy = {
                "category": "Category 1",
                "subcategory": "Subcategory 1",
                "tags": ["test", f"sample_{i}"]
            }
            block_create_data = BlockCreateSchema(
                name=f"Sample Block {i}",
                block_type="dataset",
                description=f"This is sample block number {i}.",
                created_by=creator_id,
                taxonomy=taxonomy,
                metadata={"key": f"value_{i}"}
            )
            sample_block = create_sample_block_response_with_creator_and_taxonomy(block_id, creator_id)
            sample_block.taxonomy = taxonomy
            blocks.append(sample_block)

            # Mock block creation
            block_controller.block_service.create_block.return_value = sample_block
            block_controller.taxonomy_service.create_taxonomy_for_block.return_value = True
            block_controller.vector_embedding_service.create_vector_embedding.return_value = create_sample_vector_representation(
                block_id, [0.1 * i, 0.2 * i, 0.3 * i]
            )

            # Create block
            block_controller.create_block(block_create_data)

        # Mock search_similar_blocks to return blocks containing the keyword
        mock_vector_embedding_service.search_similar_blocks.return_value = blocks[:top_k]

        # Act
        print(f"Performing similarity search with keyword='{keyword}'...")
        search_query = SearchQuery(
            keywords=[keyword],
            limit=top_k,
            offset=0
        )
        result = block_controller.perform_similarity_search(
            query_text="Sample search",
            taxonomy_filters=None,
            top_k=top_k
        )

        # Assert
        print("Asserting search results based on keywords...")
        assert result is not None, "Search returned None."
        assert len(result) == top_k, f"Expected {top_k} results, got {len(result)}."
        for block in result:
            assert keyword in block.name or keyword in block.description, "Keyword not found in block."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.search_similar_blocks.assert_called_once_with("Sample search", None, top_k)

        print("test_search_blocks_by_keywords passed.")


    def test_search_blocks_by_taxonomy_filters(self, block_controller, mock_vector_embedding_service, 
                                            mock_audit_service, mock_logger):
        """
        Test searching blocks using taxonomy filters.
        """
        print("\n--- Starting test_search_blocks_by_taxonomy_filters ---")
        # Arrange
        taxonomy_filters = {
            "category": "Category 1",
            "subcategory": "Subcategory 1"
        }
        top_k = 3

        # Create sample blocks
        blocks = []
        for i in range(1, top_k + 1):
            block_id = generate_uuid()
            creator_id = generate_uuid()
            taxonomy = {
                "category": "Category 1",
                "subcategory": "Subcategory 1",
                "tags": ["test", f"filter_sample_{i}"]
            }
            block_create_data = BlockCreateSchema(
                name=f"Filter Sample Block {i}",
                block_type="model",
                description=f"This is filter sample block number {i}.",
                created_by=creator_id,
                taxonomy=taxonomy,
                metadata={"key": f"value_filter_{i}"}
            )
            sample_block = create_sample_block_response_with_creator_and_taxonomy(block_id, creator_id)
            sample_block.taxonomy = taxonomy
            blocks.append(sample_block)

            # Mock block creation
            block_controller.block_service.create_block.return_value = sample_block
            block_controller.taxonomy_service.create_taxonomy_for_block.return_value = True
            block_controller.vector_embedding_service.create_vector_embedding.return_value = create_sample_vector_representation(
                block_id, [0.4 * i, 0.5 * i, 0.6 * i]
            )

            # Create block
            block_controller.create_block(block_create_data)

        # Mock search_similar_blocks to return blocks matching taxonomy filters
        mock_vector_embedding_service.search_similar_blocks.return_value = blocks[:top_k]

        # Act
        print(f"Performing similarity search with taxonomy_filters={taxonomy_filters}...")
        result = block_controller.perform_similarity_search(
            query_text="Filter search",
            taxonomy_filters=taxonomy_filters,
            top_k=top_k
        )

        # Assert
        print("Asserting search results based on taxonomy filters...")
        assert result is not None, "Search returned None."
        assert len(result) == top_k, f"Expected {top_k} results, got {len(result)}."
        for block in result:
            assert block.taxonomy["category"] == "Category 1", "Category filter mismatch."
            assert block.taxonomy["subcategory"] == "Subcategory 1", "Subcategory filter mismatch."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.search_similar_blocks.assert_called_once_with("Filter search", taxonomy_filters, top_k)

        print("test_search_blocks_by_taxonomy_filters passed.")

    def test_search_blocks_pagination(self, block_controller, mock_vector_embedding_service, 
                                    mock_audit_service, mock_logger):
        """
        Test searching blocks with pagination parameters.
        """
        print("\n--- Starting test_search_blocks_pagination ---")
        # Arrange
        total_blocks = 10
        limit = 5
        offset = 5

        # Create sample blocks
        blocks = []
        for i in range(1, total_blocks + 1):
            block_id = generate_uuid()
            creator_id = generate_uuid()
            taxonomy = {
                "category": "Category Pagination",
                "subcategory": "Subcategory Pagination",
                "tags": ["pagination", f"page_sample_{i}"]
            }
            block_create_data = BlockCreateSchema(
                name=f"Pagination Block {i}",
                block_type="dataset",
                description=f"This is pagination block number {i}.",
                created_by=creator_id,
                taxonomy=taxonomy,
                metadata={"key": f"value_pagination_{i}"}
            )
            sample_block = create_sample_block_response_with_creator_and_taxonomy(block_id, creator_id)
            sample_block.taxonomy = taxonomy
            blocks.append(sample_block)

            # Mock block creation
            block_controller.block_service.create_block.return_value = sample_block
            block_controller.taxonomy_service.create_taxonomy_for_block.return_value = True
            block_controller.vector_embedding_service.create_vector_embedding.return_value = create_sample_vector_representation(
                block_id, [0.7 * i, 0.8 * i, 0.9 * i]
            )

            # Create block
            block_controller.create_block(block_create_data)

        # Mock search_similar_blocks to return a subset based on pagination
        paginated_blocks = blocks[offset:offset + limit]
        mock_vector_embedding_service.search_similar_blocks.return_value = paginated_blocks

        # Act
        print(f"Performing similarity search with limit={limit} and offset={offset}...")
        result = block_controller.perform_similarity_search(
            query_text="Pagination search",
            taxonomy_filters=None,
            top_k=limit,
            # Assuming the controller supports offset; if not, adjust accordingly
        )

        # Assert
        print("Asserting search results based on pagination...")
        assert result is not None, "Search returned None."
        assert len(result) == limit, f"Expected {limit} results, got {len(result)}."
        expected_blocks = blocks[offset:offset + limit]
        for result_block, expected_block in zip(result, expected_blocks):
            assert result_block.block_id == expected_block.block_id, "Block ID mismatch in pagination."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.search_similar_blocks.assert_called_once_with("Pagination search", None, limit)

        print("test_search_blocks_pagination passed.")

    def test_create_block(self, block_controller, mock_block_service, mock_taxonomy_service, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test the creation of a block with CRUD operations, including taxonomy.
        """
        print("\n--- Starting test_create_block ---")
        # Arrange
        block_id = generate_uuid()
        block_create_data = create_sample_block_create_schema_with_creator_and_taxonomy()
        sample_block = create_sample_block_response_with_creator_and_taxonomy(block_id, block_create_data.created_by)

        mock_block_service.create_block.return_value = sample_block
        mock_taxonomy_service.create_taxonomy_for_block.return_value = True
        mock_vector_embedding_service.create_vector_embedding.return_value = create_sample_vector_representation(
            block_id, [0.1, 0.2, 0.3]
        )

        # Act
        print("Calling block_controller.create_block with sample data...")
        result = block_controller.create_block(block_create_data)

        # Assert
        print("Asserting block creation...")
        assert result is not None, "Block creation returned None."
        assert result.block_id == block_id, "Block ID does not match."
        assert result.name == block_create_data.name, "Block name does not match."
        assert result.block_type == block_create_data.block_type, "Block type does not match."
        assert result.description == block_create_data.description, "Block description does not match."
        assert result.created_by == block_create_data.created_by, "Block creator does not match."
        assert result.taxonomy == block_create_data.taxonomy, "Block taxonomy does not match."
        assert result.metadata == block_create_data.metadata, "Block metadata does not match."

        # Verify service calls
        print("Verifying service calls...")
        mock_block_service.create_block.assert_called_once_with(block_create_data)
        mock_taxonomy_service.create_taxonomy_for_block.assert_called_once_with(
            block_id=block_id, 
            taxonomy=block_create_data.taxonomy
        )
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called()

        print("test_create_block passed.")

    def test_get_block_by_id(self, block_controller, mock_block_service, mock_taxonomy_service, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test retrieving a block by its ID.
        """
        print("\n--- Starting test_get_block_by_id ---")
        # Arrange
        block_id = generate_uuid()
        sample_block = create_sample_block_response(block_id)

        mock_block_service.get_block_by_id.return_value = sample_block
        mock_taxonomy_service.get_taxonomy_for_block.return_value = sample_block.taxonomy
        mock_vector_embedding_service.get_vector_embedding.return_value = sample_block.vector_embedding

        # Act
        print(f"Calling block_controller.get_block_by_id with block_id={block_id}...")
        result = block_controller.get_block_by_id(block_id)

        # Assert
        print("Asserting block retrieval...")
        assert result is not None, "Block retrieval returned None."
        assert result.block_id == block_id, "Block ID does not match."
        assert result.name == sample_block.name, "Block name does not match."
        assert result.taxonomy == sample_block.taxonomy, "Block taxonomy does not match."
        assert result.vector_embedding == sample_block.vector_embedding, "Block vector embedding does not match."

        # Verify service calls
        print("Verifying service calls...")
        mock_block_service.get_block_by_id.assert_called_once_with(block_id)
        mock_taxonomy_service.get_taxonomy_for_block.assert_called_once_with(block_id=block_id)
        mock_vector_embedding_service.get_vector_embedding.assert_called_once_with(block_id=block_id)
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called()

        print("test_get_block_by_id passed.")

    def test_update_block(self, block_controller, mock_block_service, mock_taxonomy_service, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test updating an existing block.
        """
        print("\n--- Starting test_update_block ---")
        # Arrange
        block_id = generate_uuid()
        block_update_data = create_sample_block_update_schema()
        sample_block = create_sample_block_response(
            block_id,
            name=block_update_data.name,
            block_type=block_update_data.block_type,
            description=block_update_data.description
        )
        
        mock_block_service.update_block.return_value = sample_block
        mock_taxonomy_service.create_taxonomy_for_block.return_value = True
        mock_vector_embedding_service.update_vector_embedding.return_value = True

        # Act
        print(f"Calling block_controller.update_block with block_id={block_id} and update_data={block_update_data}...")
        result = block_controller.update_block(block_id, block_update_data)

        # Assert
        print("Asserting block update...")
        assert result is not None, "Block update returned None."
        assert result.block_id == block_id, "Block ID does not match."
        assert result.name == block_update_data.name, "Block name was not updated correctly."
        assert result.block_type == block_update_data.block_type, "Block type was not updated correctly."
        assert result.description == block_update_data.description, "Block description was not updated correctly."

        # Verify service calls
        print("Verifying service calls...")
        mock_block_service.update_block.assert_called_once_with(block_id, block_update_data)

        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called()

        print("test_update_block passed.")

    def test_delete_block(self, block_controller, mock_block_service, mock_taxonomy_service, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test deleting a block along with its taxonomy and vector embedding.
        """
        print("\n--- Starting test_delete_block ---")
        # Arrange
        block_id = generate_uuid()

        mock_vector_embedding_service.delete_vector_embedding.return_value = True
        mock_taxonomy_service.delete_taxonomy_for_block.return_value = True
        mock_block_service.delete_block.return_value = True

        # Act
        print(f"Calling block_controller.delete_block with block_id={block_id}...")
        result = block_controller.delete_block(block_id)

        # Assert
        print("Asserting block deletion...")
        assert result is True, "Block deletion did not return True."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.delete_vector_embedding.assert_called_once_with(block_id=block_id)
        mock_taxonomy_service.delete_taxonomy_for_block.assert_called_once_with(block_id=block_id)
        mock_block_service.delete_block.assert_called_once_with(block_id)
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called()

        print("test_delete_block passed.")

    def test_add_vector_embedding(self, block_controller, mock_vector_embedding_service, 
                                mock_audit_service, mock_logger):
        """
        Test adding a vector embedding to a block.
        """
        print("\n--- Starting test_add_vector_embedding ---")
        # Arrange
        block_id = generate_uuid()
        vector_create_data = VectorRepresentationCreateSchema(
            entity_type="block",
            entity_id=block_id,
            vector=[0.7, 0.8, 0.9],
            taxonomy_filter={"category": "Test Category"}
        )
        sample_vector = create_sample_vector_representation(block_id, vector_create_data.vector)

        mock_vector_embedding_service.create_vector_embedding.return_value = sample_vector

        # Act
        print(f"Calling block_controller.create_vector_embedding with block_id={block_id} and vector_create_data={vector_create_data}...")
        result = block_controller.create_vector_embedding(vector_create_data)

        # Assert
        print("Asserting vector embedding creation...")
        assert result is not None, "Vector embedding creation returned None."
        assert result.vector_id == sample_vector.vector_id, "Vector ID does not match."
        assert result.entity_id == block_id, "Entity ID does not match."
        assert result.vector == vector_create_data.vector, "Vector data does not match."


    def test_delete_vector_embedding(self, block_controller, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test deleting a vector embedding from a block.
        """
        print("\n--- Starting test_delete_vector_embedding ---")
        # Arrange
        block_id = generate_uuid()

        mock_vector_embedding_service.delete_vector_embedding.return_value = True

        # Act
        print(f"Calling block_controller.delete_vector_embedding with block_id={block_id}...")
        result = block_controller.delete_vector_embedding(block_id)

        # Assert
        print("Asserting vector embedding deletion...")
        assert result is True, "Vector embedding deletion did not return True."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.delete_vector_embedding.assert_called_once_with(block_id)
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called()

        print("test_delete_vector_embedding passed.")

    def test_add_multiple_vector_embeddings(self, block_controller, mock_vector_embedding_service, 
                                            mock_audit_service, mock_logger):
        print("\n--- Starting test_add_multiple_vector_embeddings ---")
        # Arrange
        blocks = [generate_uuid() for _ in range(5)]
        vector_create_datas = [
            VectorRepresentationCreateSchema(
                entity_type="block",
                entity_id=block_id,
                vector=[i * 0.1 for i in range(1, 4)],
                taxonomy_filter={"category": f"Category {i}"}
            ) for i, block_id in enumerate(blocks, start=1)
        ]

        # Create sample vectors corresponding to each block
        sample_vectors = [
            create_sample_vector_representation(block_id, create_data.vector)
            for block_id, create_data in zip(blocks, vector_create_datas)
        ]

        # Set the side_effect of the mock to return a different vector each time
        mock_vector_embedding_service.create_vector_embedding.side_effect = sample_vectors

        # Act
        for create_data in vector_create_datas:
            print(f"Adding vector embedding with data={create_data}...")
            result = block_controller.create_vector_embedding(create_data)
            print(f"Vector embedding added: {result.vector_id}")
            assert result is not None, f"Vector embedding creation for block {create_data.entity_id} returned None."
            assert result.entity_id == create_data.entity_id, f"Entity ID mismatch for block {create_data.entity_id}."
        
        # Assert
        print("Asserting multiple vector embeddings were added successfully...")
        assert mock_vector_embedding_service.create_vector_embedding.call_count == 5, "Not all vector embeddings were created."
        assert mock_audit_service.create_audit_log.call_count == 5, "Not all audit logs were created."
        assert mock_logger.log.call_count == 5, "Not all logs were created."

        print("test_add_multiple_vector_embeddings passed.")

    def test_similarity_search(self, block_controller, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test performing a vector similarity search.
        """
        print("\n--- Starting test_similarity_search ---")
        # Arrange
        query_text = "Find similar blocks related to testing."
        taxonomy_filters = {"category": "Test Category"}
        top_k = 3

        # Sample similar blocks
        similar_blocks = [
            BlockResponseSchema(
                block_id=generate_uuid(),
                name=f"Similar Block {i}",
                block_type="model",
                description=f"Description for similar block {i}.",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
                current_version_id=generate_uuid(),
                taxonomy={"category": "Test Category"},
                vector_embedding=VectorRepresentationSchema(
                    vector_id=generate_uuid(),
                    entity_type="block",
                    entity_id=generate_uuid(),
                    vector=[0.1 * i, 0.2 * i, 0.3 * i],
                    taxonomy_filter={"category": "Test Category"},
                    created_at="2024-01-01T00:00:00Z",
                    updated_at="2024-01-02T00:00:00Z"
                )
            ) for i in range(1, top_k + 1)
        ]

        mock_vector_embedding_service.search_similar_blocks.return_value = similar_blocks

        # Act
        print(f"Performing similarity search with query_text='{query_text}', taxonomy_filters={taxonomy_filters}, top_k={top_k}...")
        result = block_controller.perform_similarity_search(query_text, taxonomy_filters, top_k)

        # Assert
        print("Asserting similarity search results...")
        assert result is not None, "Similarity search returned None."
        assert len(result) == top_k, f"Expected {top_k} similar blocks, got {len(result)}."
        for i, block in enumerate(result, start=1):
            print(f"Similar Block {i}: {block.block_id} - {block.name}")
            assert block.name == f"Similar Block {i}", f"Block name mismatch for Similar Block {i}."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.search_similar_blocks.assert_called_once_with(query_text, taxonomy_filters, top_k)
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called_once()

        print("test_similarity_search passed.")

    def test_create_block_failure(self, block_controller, mock_block_service, mock_logger):
        """
        Test the creation of a block when the BlockService fails.
        """
        print("\n--- Starting test_create_block_failure ---")
        # Arrange
        block_id = generate_uuid()
        block_create_data = create_sample_block_create_schema()

        mock_block_service.create_block.return_value = None  # Simulate failure

        # Act
        print("Calling block_controller.create_block with data that will cause failure...")
        with pytest.raises(HTTPException) as exc_info:
            block_controller.create_block(block_create_data)

        # Assert
        print("Asserting that HTTPException was raised...")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST, "Expected status code 400."
        assert exc_info.value.detail == "Block creation failed.", "Unexpected error detail."

        # Verify service calls
        print("Verifying service calls...")
        mock_block_service.create_block.assert_called_once_with(block_create_data)
        mock_logger.log.assert_called()

        print("test_create_block_failure passed.")

    def test_delete_block_failure(self, block_controller, mock_block_service, 
                                mock_taxonomy_service, mock_vector_embedding_service, mock_logger):
        """
        Test deleting a block when the BlockService fails.
        """
        print("\n--- Starting test_delete_block_failure ---")
        # Arrange
        block_id = generate_uuid()

        mock_vector_embedding_service.delete_vector_embedding.return_value = True
        mock_taxonomy_service.delete_taxonomy_for_block.return_value = True
        mock_block_service.delete_block.return_value = False  # Simulate failure

        # Act
        print(f"Calling block_controller.delete_block with block_id={block_id} that will fail...")
        with pytest.raises(HTTPException) as exc_info:
            block_controller.delete_block(block_id)

        # Assert
        print("Asserting that HTTPException was raised...")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST, "Expected status code 400."
        assert exc_info.value.detail == "Block deletion failed.", "Unexpected error detail."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.delete_vector_embedding.assert_called_once_with(block_id)
        mock_taxonomy_service.delete_taxonomy_for_block.assert_called_once_with(block_id=block_id)
        mock_block_service.delete_block.assert_called_once_with(block_id)
        mock_logger.log.assert_called()

        print("test_delete_block_failure passed.")

    def test_similarity_search_failure(self, block_controller, mock_vector_embedding_service, mock_logger):
        """
        Test performing a similarity search when the VectorEmbeddingService fails.
        """
        print("\n--- Starting test_similarity_search_failure ---")
        # Arrange
        query_text = "Invalid search query."
        taxonomy_filters = {"category": "Nonexistent Category"}
        top_k = 5

        mock_vector_embedding_service.search_similar_blocks.return_value = None  # Simulate failure

        # Act
        print(f"Performing similarity search with invalid parameters...")
        with pytest.raises(HTTPException) as exc_info:
            block_controller.perform_similarity_search(query_text, taxonomy_filters, top_k)

        # Assert
        print("Asserting that HTTPException was raised...")
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, "Expected status code 500."
        assert exc_info.value.detail == "Similarity search failed.", "Unexpected error detail."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.search_similar_blocks.assert_called_once_with(query_text, taxonomy_filters, top_k)
        mock_logger.log.assert_called()

        print("test_similarity_search_failure passed.")

    def test_add_vector_embedding_failure(self, block_controller, mock_vector_embedding_service, mock_logger):
        """
        Test adding a vector embedding when the VectorEmbeddingService fails.
        """
        print("\n--- Starting test_add_vector_embedding_failure ---")
        # Arrange
        block_id = generate_uuid()
        vector_create_data = VectorRepresentationCreateSchema(
            entity_type="block",
            entity_id=block_id,
            vector=[0.7, 0.8, 0.9],
            taxonomy_filter={"category": "Test Category"}
        )

        mock_vector_embedding_service.create_vector_embedding.return_value = None  # Simulate failure

        # Act
        print(f"Adding vector embedding to block_id={block_id} that will fail...")
        with pytest.raises(HTTPException) as exc_info:
            block_controller.create_vector_embedding(vector_create_data)

        # Assert
        print("Asserting that HTTPException was raised...")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST, "Expected status code 400."
        assert exc_info.value.detail == "Vector embedding creation failed.", "Unexpected error detail."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.create_vector_embedding.assert_called_once_with(vector_create_data)
        mock_logger.log.assert_called()

        print("test_add_vector_embedding_failure passed.")

    def test_update_vector_embedding(self, block_controller, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test updating a vector embedding for a block.
        """
        print("\n--- Starting test_update_vector_embedding ---")
        # Arrange
        block_id = generate_uuid()
        update_success = True

        mock_vector_embedding_service.update_vector_embedding.return_value = update_success

        # Act
        print(f"Updating vector embedding for block_id={block_id}...")
        update_data = VectorRepresentationCreateSchema(
            entity_type="block",
            entity_id=block_id,
            vector=[0.1, 0.2, 0.3],
            taxonomy_filter={"category": "Updated Category"}
        )
        result = block_controller.update_vector_embedding(block_id, update_data)

        # Assert
        print("Asserting vector embedding update...")
        assert result is True, "Vector embedding update did not return True."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.update_vector_embedding.assert_called_once_with(block_id, update_data)
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called_once()

        print("test_update_vector_embedding passed.")

    def test_update_vector_embedding_failure(self, block_controller, mock_vector_embedding_service, mock_logger):
        """
        Test updating a vector embedding when the VectorEmbeddingService fails.
        """
        print("\n--- Starting test_update_vector_embedding_failure ---")
        # Arrange
        block_id = generate_uuid()

        mock_vector_embedding_service.update_vector_embedding.return_value = False  # Simulate failure

        # Act
        print(f"Updating vector embedding for block_id={block_id} that will fail...")
        update_data = VectorRepresentationCreateSchema(
            entity_type="block",
            entity_id=block_id,
            vector=[0.1, 0.2, 0.3],
            taxonomy_filter={"category": "Fail Category"}
        )
        with pytest.raises(HTTPException) as exc_info:
            block_controller.update_vector_embedding(block_id, update_data)

        # Assert
        print("Asserting that HTTPException was raised...")
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST, "Expected status code 400."
        assert exc_info.value.detail == "Vector embedding update failed.", "Unexpected error detail."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.update_vector_embedding.assert_called_once_with(block_id, update_data)
        mock_logger.log.assert_called_once()

        print("test_update_vector_embedding_failure passed.")

    def test_perform_similarity_search_no_results(self, block_controller, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test performing a similarity search that returns no results.
        """
        print("\n--- Starting test_perform_similarity_search_no_results ---")
        # Arrange
        query_text = "No matching blocks."
        taxonomy_filters = {"category": "Nonexistent Category"}
        top_k = 5

        mock_vector_embedding_service.search_similar_blocks.return_value = []

        # Act
        print(f"Performing similarity search with query_text='{query_text}', taxonomy_filters={taxonomy_filters}, top_k={top_k}...")
        result = block_controller.perform_similarity_search(query_text, taxonomy_filters, top_k)

        # Assert
        print("Asserting similarity search results...")
        assert result is not None, "Similarity search returned None."
        assert len(result) == 0, "Expected no similar blocks, but some were returned."

        # Verify service calls
        print("Verifying service calls...")
        mock_vector_embedding_service.search_similar_blocks.assert_called_once_with(query_text, taxonomy_filters, top_k)
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called_once()

        print("test_perform_similarity_search_no_results passed.")

    def test_create_block_with_invalid_data(self, block_controller, mock_block_service, mock_logger):
        """
        Test creating a block with invalid data that should raise a validation error.
        """
        print("\n--- Starting test_create_block_with_invalid_data ---")
        # Arrange
        with pytest.raises(ValidationError) as exc_info:
            # Creating BlockCreateSchema with an invalid block_type
            invalid_block_create_data = BlockCreateSchema(
                name="Invalid Block",
                block_type="invalid_type",  # Invalid BlockTypeEnum
                description="This block has an invalid type.",
                created_by=generate_uuid()
            )
        # Optionally, assert the details of the exception
        assert "block_type" in str(exc_info.value), "Expected validation error on block_type"
        print("test_create_block_with_invalid_data passed.")
        
    def test_create_block_with_missing_fields(self, block_controller, mock_logger):
        """
        Test creating a block with missing required fields to ensure validation errors are raised.
        """
        print("\n--- Starting test_create_block_with_missing_fields ---")
        # Arrange
        with pytest.raises(ValidationError) as exc_info:
            # Missing 'name' field
            BlockCreateSchema(
                block_type="dataset",
                description="Missing name field.",
                created_by=generate_uuid()
            )
        # Optionally, assert the details of the exception
        assert "name" in str(exc_info.value), "Expected validation error on missing 'name' field"

    def test_create_block_without_taxonomy(self, block_controller, mock_block_service, mock_taxonomy_service, mock_logger):
        """
        Test creating a block without taxonomy data.
        """
        print("\n--- Starting test_create_block_without_taxonomy ---")
        # Arrange
        block_id = generate_uuid()
        block_create_data = create_sample_block_create_schema()
        block_create_data.taxonomy = None  # Ensure no taxonomy is provided

        mock_block_service.create_block.return_value = create_sample_block_response(block_id)

        # Act
        print(f"Creating block without taxonomy data for block_id={block_id}...")
        result = block_controller.create_block(block_create_data)

        # Assert
        print("Asserting that block was created successfully without taxonomy...")
        assert result is not None, "Expected block to be created."
        assert result.block_id == block_id, "Block ID mismatch."

        # Verify service calls
        print("Verifying service calls...")
        mock_block_service.create_block.assert_called_once_with(block_create_data)
        mock_taxonomy_service.create_taxonomy_for_block.assert_not_called()
        mock_logger.log.assert_called()

        print("test_create_block_without_taxonomy passed.")

    def test_create_block_without_taxonomy(self, block_controller, mock_block_service, mock_taxonomy_service, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test creating a block without providing taxonomy data.
        """
        print("\n--- Starting test_create_block_without_taxonomy ---")
        # Arrange
        block_id = generate_uuid()
        block_create_data = BlockCreateSchema(
            name="Block Without Taxonomy",
            block_type="model",
            description="This block does not have taxonomy.",
            created_by=generate_uuid()
        )

        sample_block = create_sample_block_response(block_id)
        sample_block.taxonomy = None  # No taxonomy
        sample_block.vector_embedding = None  # No vector embedding

        mock_block_service.create_block.return_value = sample_block

        # Act
        print("Creating block without taxonomy data...")
        result = block_controller.create_block(block_create_data)

        # Assert
        print("Asserting block creation without taxonomy...")
        assert result is not None, "Block creation returned None."
        assert result.block_id == block_id, "Block ID does not match."
        assert result.taxonomy is None, "Block taxonomy should be None."
        assert result.vector_embedding is None, "Block vector embedding should be None."

        # Verify service calls
        print("Verifying service calls...")
        mock_block_service.create_block.assert_called_once_with(block_create_data)
        mock_taxonomy_service.create_taxonomy_for_block.assert_not_called()
        mock_vector_embedding_service.create_vector_embedding.assert_not_called()
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called_once()

        print("test_create_block_without_taxonomy passed.")

    def test_create_block_without_metadata(self, block_controller, mock_block_service, mock_taxonomy_service, mock_vector_embedding_service, mock_audit_service, mock_logger):
        """
        Test creating a block without providing metadata for vector embedding.
        """
        print("\n--- Starting test_create_block_without_metadata ---")
        # Arrange
        block_id = generate_uuid()
        block_create_data = BlockCreateSchema(
            name="Block Without Metadata",
            block_type="dataset",
            description=None,  # No metadata
            created_by=generate_uuid()
        )

        sample_block = create_sample_block_response(block_id)
        sample_block.metadata = None  # No metadata
        sample_block.vector_embedding = None  # No vector embedding

        mock_block_service.create_block.return_value = sample_block

        # Act
        print("Creating block without metadata...")
        result = block_controller.create_block(block_create_data)

        # Assert
        print("Asserting block creation without metadata...")
        assert result is not None, "Block creation returned None."
        assert result.block_id == block_id, "Block ID does not match."
        assert result.vector_embedding is None, "Block vector embedding should be None."

        # Verify service calls
        print("Verifying service calls...")
        mock_block_service.create_block.assert_called_once_with(block_create_data)
        mock_vector_embedding_service.create_vector_embedding.assert_not_called()
        mock_audit_service.create_audit_log.assert_called_once()
        mock_logger.log.assert_called_once()

        print("test_create_block_without_metadata passed.")
